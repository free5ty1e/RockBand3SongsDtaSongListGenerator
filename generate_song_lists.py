#!/usr/bin/env python3

import argparse
import os
import sys
import logging
from typing import List, Tuple, Optional, Dict


def read_file_text(path: str) -> str:
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()


def split_top_level_entries(dta_text: str) -> List[str]:
    entries: List[str] = []
    depth = 0
    start_idx: Optional[int] = None
    i = 0

    while i < len(dta_text):
        ch = dta_text[i]
        if ch == '"':
            # Skip over quoted strings, honoring escapes
            i += 1
            while i < len(dta_text):
                c = dta_text[i]
                if c == '\\':
                    i += 2  # skip escaped char
                    continue
                if c == '"':
                    i += 1
                    break
                i += 1
            continue

        # Skip over single-quoted atoms/strings: '...'
        if ch == "'":
            i += 1
            while i < len(dta_text) and dta_text[i] != "'":
                i += 1
            if i < len(dta_text) and dta_text[i] == "'":
                i += 1
            continue

        # Skip comments starting with ';' until end of line
        if ch == ';':
            while i < len(dta_text) and dta_text[i] not in ('\n', '\r'):
                i += 1
            continue

        if ch == '(':
            if depth == 0:
                start_idx = i
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth < 0:
                # Malformed input; reset
                depth = 0
                start_idx = None
            elif depth == 0 and start_idx is not None:
                entries.append(dta_text[start_idx:i + 1])
                start_idx = None
        i += 1

    return entries


def _find_unescaped_quote(s: str, start: int) -> int:
    i = start
    while i < len(s):
        if s[i] == '"':
            # count preceding backslashes
            bs = 0
            j = i - 1
            while j >= 0 and s[j] == '\\':
                bs += 1
                j -= 1
            if bs % 2 == 0:
                return i
        i += 1
    return -1


def _unescape_dta_string(s: str) -> str:
    # Basic unescape for common sequences in DTA strings
    return s.encode('utf-8', 'backslashreplace').decode('unicode_escape')


def extract_string_field(entry_text: str, key: str) -> Optional[str]:
    # Extract only from DIRECT CHILDREN of the entry root: (key ...)
    # Since entry_text itself is a single top-level list, its direct children
    # appear when depth == 2 while scanning characters.
    depth = 0
    i = 0
    n = len(entry_text)
    while i < n:
        ch = entry_text[i]
        if ch == '"':
            # skip strings
            i += 1
            while i < n:
                c = entry_text[i]
                if c == '\\':
                    i += 2
                    continue
                if c == '"':
                    i += 1
                    break
                i += 1
            continue
        if ch == '(':
            depth += 1
            # Direct children inside the entry are at depth 2
            if depth == 2:
                j = i + 1
                # skip whitespace
                while j < n and entry_text[j].isspace():
                    j += 1
                # key may be optionally wrapped in single quotes
                quoted_key = False
                if j < n and entry_text[j] == "'":
                    quoted_key = True
                    j += 1
                if entry_text.startswith(key, j):
                    k_end = j + len(key)
                    # if quoted, the next char must be a closing single quote
                    if quoted_key:
                        if k_end < n and entry_text[k_end] == "'":
                            k_end += 1
                        else:
                            # not an exact quoted key match
                            pass
                    # next must be whitespace or ')' or '"' or '\'' for a valid atom key
                    if k_end < n and (entry_text[k_end].isspace() or entry_text[k_end] in (')', '"', "'")):
                        # move to value
                        j = k_end
                        while j < n and entry_text[j].isspace():
                            j += 1
                        if j >= n:
                            return None
                        if entry_text[j] == '"':
                            j += 1
                            end_q = _find_unescaped_quote(entry_text, j)
                            if end_q == -1:
                                return None
                            raw = entry_text[j:end_q]
                            try:
                                return _unescape_dta_string(raw)
                            except Exception:
                                return raw
                        elif entry_text[j] == "'":
                            # single-quoted string value
                            j += 1
                            start_val = j
                            while j < n and entry_text[j] != "'":
                                j += 1
                            raw = entry_text[start_val:j]
                            return raw if raw else None
                        else:
                            start_val = j
                            while j < n and not entry_text[j].isspace() and entry_text[j] != ')':
                                j += 1
                            val = entry_text[start_val:j].strip()
                            if val:
                                return val
        elif ch == ')':
            depth = max(0, depth - 1)
        i += 1
    return None
    

def extract_first_of(entry_text: str, keys: List[str]) -> Optional[str]:
    for k in keys:
        val = extract_string_field(entry_text, k)
        if val:
            return val
    return None


def _extract_song_identifier(entry_text: str) -> Optional[str]:
    # The identifier is the FIRST atom after the entry's opening '('
    i = entry_text.find('(')
    if i == -1:
        return None
    j = i + 1
    n = len(entry_text)
    while j < n and entry_text[j].isspace():
        j += 1
    if j >= n:
        return None
    if entry_text[j] == '"':
        j += 1
        end_q = _find_unescaped_quote(entry_text, j)
        if end_q == -1:
            return None
        raw = entry_text[j:end_q]
        try:
            return _unescape_dta_string(raw)
        except Exception:
            return raw
    if entry_text[j] == "'":
        j += 1
        start_val = j
        while j < n and entry_text[j] != "'":
            j += 1
        ident = entry_text[start_val:j]
        return ident if ident else None
    start_val = j
    while j < n and not entry_text[j].isspace() and entry_text[j] != ')':
        j += 1
    ident = entry_text[start_val:j].strip()
    return ident if ident else None


def parse_entries_for_artist_name(entries: List[str]) -> Tuple[List[Tuple[str, str, Optional[str], Optional[int], Optional[int]]], Dict[str, int], List[Tuple[Optional[str], Optional[str], Optional[str], Optional[str], Optional[int], Optional[int]]]]:
    results: List[Tuple[str, str, Optional[str], Optional[int], Optional[int]]] = []
    partials: List[Tuple[Optional[str], Optional[str], Optional[str]]] = []
    stats: Dict[str, int] = {
        'total_entries': len(entries),
        'missing_artist': 0,
        'missing_name': 0,
        'completed_pairs': 0,
    }
    for e in entries:
        # Prefer common display-name keys first, then fall back to 'name'
        name = extract_first_of(e, ['songname', 'song_name', 'title', 'name'])
        artist = extract_first_of(e, ['artist', 'song_artist'])
        ident = _extract_song_identifier(e)
        album = extract_first_of(e, ['album_name'])
        year_str = extract_first_of(e, ['year_released'])
        length_str = extract_first_of(e, ['song_length'])
        year_val: Optional[int] = None
        length_ms_val: Optional[int] = None
        try:
            if year_str is not None:
                year_val = int(str(year_str).strip())
        except Exception:
            year_val = None
        try:
            if length_str is not None:
                length_ms_val = int(str(length_str).strip())
        except Exception:
            length_ms_val = None
        if name and artist:
            results.append((artist, name, album, year_val, length_ms_val))
            stats['completed_pairs'] += 1
        else:
            if not artist:
                stats['missing_artist'] += 1
            if not name:
                stats['missing_name'] += 1
            partials.append((artist, name, ident, album, year_val, length_ms_val))
    return results, stats, partials


def _format_mm_ss(length_ms: Optional[int]) -> str:
    if length_ms is None or length_ms < 0:
        return '?:??'
    total_seconds = length_ms // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:02d}"


def write_outputs(pairs: List[Tuple[str, str, Optional[str], Optional[int], Optional[int]]], cwd: str) -> None:
    # Sort explicitly by artist, then album (if present), then name for artist list
    artist_sorted = sorted(pairs, key=lambda x: (x[0].lower(), (x[2] or '').lower(), x[1].lower()))
    # Sort by name, then artist for name list
    name_sorted = sorted(pairs, key=lambda x: (x[1].lower(), x[0].lower()))

    artist_path = os.path.join(cwd, 'SongListSortedByArtist.txt')
    name_path = os.path.join(cwd, 'SongListSortedBySongName.txt')

    with open(artist_path, 'w', encoding='utf-8') as fa:
        for artist, name, album, year_val, length_ms_val in artist_sorted:
            album_disp = album if album else '(unknown album)'
            year_disp = str(year_val) if year_val is not None else '?'
            length_disp = _format_mm_ss(length_ms_val)
            fa.write(f"{artist} ({album_disp}) - {name} ({year_disp} / {length_disp})\n")

    with open(name_path, 'w', encoding='utf-8') as fn:
        for artist, name, album, year_val, length_ms_val in name_sorted:
            album_disp = album if album else '(unknown album)'
            year_disp = str(year_val) if year_val is not None else '?'
            length_disp = _format_mm_ss(length_ms_val)
            fn.write(f"{name} by {artist} on {album_disp} ({year_disp} / {length_disp})\n")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description='Generate song lists from a Rock Band .DTA songs file.'
    )
    parser.add_argument('input', help='Path to songs.dta.txt (or any .DTA-format file)')
    args = parser.parse_args(argv)

    input_path = args.input
    if not os.path.isfile(input_path):
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        return 1

    try:
        text = read_file_text(input_path)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1

    # Basic logger setup
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

    entries = split_top_level_entries(text)
    pairs, stats, partials = parse_entries_for_artist_name(entries)

    if not pairs:
        logging.warning('No (artist, name) pairs found. Outputs may be empty.')

    # Log partial entries for analysis
    if partials:
        logging.info('Partial entries (missing artist or name):')
        for a, n, ident, album, year_val, length_ms_val in partials:
            logging.info(
                f"  id={ident if ident else '<unknown id>'} | artist={a if a else '<missing>'} | name={n if n else '<missing>'} | album={album if album else '<missing>'} | year={year_val if year_val is not None else '<missing>'} | length={_format_mm_ss(length_ms_val)}"
            )

    # Augment outputs with partials using placeholders so lists remain comprehensive
    placeholder_pairs: List[Tuple[str, str, Optional[str], Optional[int], Optional[int]]] = []
    for a, n, _, album, year_val, length_ms_val in partials:
        artist_val = a if a else '(unknown artist)'
        name_val = n if n else '(unknown title)'
        album_val = album if album else None
        placeholder_pairs.append((artist_val, name_val, album_val, year_val, length_ms_val))

    all_pairs = pairs + placeholder_pairs

    write_outputs(all_pairs, os.getcwd())

    # Summary
    total = stats.get('total_entries', 0)
    extracted = stats.get('completed_pairs', 0)
    skipped = total - extracted
    missing_artist = stats.get('missing_artist', 0)
    missing_name = stats.get('missing_name', 0)

    print('Wrote SongListSortedByArtist.txt and SongListSortedBySongName.txt')
    print('Summary:')
    print(f'- Total entries parsed: {total}')
    print(f'- Pairs extracted: {extracted}')
    print(f'- Skipped entries (missing artist and/or name): {skipped}')
    if skipped:
        # Provide a bit more detail about what was missing
        print(f'  - Missing artist: {missing_artist}')
        print(f'  - Missing name: {missing_name}')
    print(f'- Lines written to SongListSortedByArtist.txt: {len(all_pairs)}')
    print(f'- Lines written to SongListSortedBySongName.txt: {len(all_pairs)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
