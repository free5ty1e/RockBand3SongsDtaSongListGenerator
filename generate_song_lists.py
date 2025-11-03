#!/usr/bin/env python3

import argparse
import os
import sys
import logging
import re
from typing import List, Tuple, Optional, Dict, Iterable, Set
import datetime


# Lines containing any of these (case-insensitive) will be excluded from the
# "Clean" output files. Extend this list as needed.
CURSE_WORDS: List[str] = [
    # strong profanity
    'shit', 'fuck', 'bitch', 'bullshit', 'motherfucker', 'mother fucker',
    # sexual/body terms (note: see regex boundary list below for risky ones)
    'tits', 'boobs', 'jizz',
    # ass compounds (avoid plain 'ass')
    'asshole', 'dumbass', 'badass', 'jackass', 'smartass',
    # other
    'bastard', 'damn', 'dammit', 'goddamn', 'god damn',
]

# Regex patterns with word boundaries to reduce false positives
# Use lowercase in patterns; matching is case-insensitive
CURSE_REGEX_PATTERNS: List[str] = [
    r"\bdick\b",
    r"\bcock\b",
    r"\bcum\b",
    r"\bpiss(ed|ing)?\b",
]

_CURSE_REGEX: List[re.Pattern] = [re.compile(p, re.IGNORECASE) for p in CURSE_REGEX_PATTERNS]


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


def write_outputs(pairs: List[Tuple[str, str, Optional[str], Optional[int], Optional[int]]], cwd: str) -> Dict[str, int]:
    # Get current time in Eastern Time
    now = datetime.datetime.now()
    timestamp = now.strftime("%A, %B %d, %Y at %I:%M:%S %p ET")
    
    header_timestamp = f"Generated on: {timestamp}\n\n"

    # Calculate totals for full lists
    total_songs = len(pairs)
    unique_artists = set(artist for artist, _, _, _, _ in pairs if artist and artist != '(unknown artist)')
    total_artists = len(unique_artists)
    unique_albums = set(album for _, _, album, _, _ in pairs if album and album != '(unknown album)')
    total_albums = len(unique_albums)
    
    header_full = header_timestamp + f"Total songs: {total_songs}\nTotal albums: {total_albums}\nTotal artists: {total_artists}\n\n"

    # Sort explicitly by artist, then album (if present), then name for artist list
    artist_sorted = sorted(pairs, key=lambda x: (x[0].lower(), (x[2] or '').lower(), x[1].lower()))
    # Sort by name, then artist for name list
    name_sorted = sorted(pairs, key=lambda x: (x[1].lower(), x[0].lower()))

    artist_path = os.path.join(cwd, 'SongListSortedByArtist.txt')
    name_path = os.path.join(cwd, 'SongListSortedBySongName.txt')
    artist_clean_path = os.path.join(cwd, 'SongListSortedByArtistClean.txt')
    name_clean_path = os.path.join(cwd, 'SongListSortedBySongNameClean.txt')

    def _format_mm_ss(length_ms: Optional[int]) -> str:
        if length_ms is None or length_ms < 0:
            return '?:??'
        total_seconds = length_ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02d}"

    def _matched_curses(line: str) -> Set[str]:
        low = line.lower()
        matched: Set[str] = set()
        for w in CURSE_WORDS:
            if w in low:
                matched.add(w)
        for pat in _CURSE_REGEX:
            if pat.search(line):
                matched.add(pat.pattern)
        return matched

    artist_lines: List[str] = []
    for artist, name, album, year_val, length_ms_val in artist_sorted:
        album_disp = album if album else '(unknown album)'
        year_disp = str(year_val) if year_val is not None else '?'
        length_disp = _format_mm_ss(length_ms_val)
        artist_lines.append(f"{artist} ({album_disp}) - {name} ({year_disp} / {length_disp})")

    with open(artist_path, 'w', encoding='utf-8') as fa:
        fa.write(header_full)  # Use full totals with timestamp
        for line in artist_lines:
            fa.write(line + "\n")

    # Collect clean artist lines and compute clean totals
    artist_clean_lines: List[str] = []
    artist_clean_filtered = 0
    artist_clean_written = 0
    artist_term_counts: Dict[str, int] = {}
    for line in artist_lines:
        terms = _matched_curses(line)
        if terms:
            artist_clean_filtered += 1
            for t in terms:
                artist_term_counts[t] = artist_term_counts.get(t, 0) + 1
            logging.info(f"Filtered (artist-clean): {line}")
            logging.info(f"  -> matched: {', '.join(sorted(terms))}")
            continue
        artist_clean_written += 1
        artist_clean_lines.append(line)

    # Calculate clean totals from artist_clean_lines
    artist_clean_pairs = [artist_sorted[i] for i, line in enumerate(artist_lines) if _matched_curses(line) == set()]  # Unfiltered tuples
    clean_unique_artists_artist = set(artist for artist, _, _, _, _ in artist_clean_pairs if artist and artist != '(unknown artist)')
    clean_total_artists_artist = len(clean_unique_artists_artist)
    clean_unique_albums_artist = set(album for _, _, album, _, _ in artist_clean_pairs if album and album != '(unknown album)')
    clean_total_albums_artist = len(clean_unique_albums_artist)
    clean_total_songs_artist = len(artist_clean_pairs)
    header_clean_artist = header_timestamp + f"Total songs: {clean_total_songs_artist}\nTotal albums: {clean_total_albums_artist}\nTotal artists: {clean_total_artists_artist}\n\n"

    with open(artist_clean_path, 'w', encoding='utf-8') as fa_clean:
        fa_clean.write(header_clean_artist)  # Use clean totals with timestamp
        for line in artist_clean_lines:
            fa_clean.write(line + "\n")

    name_lines: List[str] = []
    for artist, name, album, year_val, length_ms_val in name_sorted:
        album_disp = album if album else '(unknown album)'
        year_disp = str(year_val) if year_val is not None else '?'
        length_disp = _format_mm_ss(length_ms_val)
        name_lines.append(f"{name} by {artist} on {album_disp} ({year_disp} / {length_disp})")

    with open(name_path, 'w', encoding='utf-8') as fn:
        fn.write(header_full)  # Use full totals with timestamp
        for line in name_lines:
            fn.write(line + "\n")

    # Collect clean name lines and compute clean totals
    name_clean_lines: List[str] = []
    name_clean_filtered = 0
    name_clean_written = 0
    name_term_counts: Dict[str, int] = {}
    for line in name_lines:
        terms = _matched_curses(line)
        if terms:
            name_clean_filtered += 1
            for t in terms:
                name_term_counts[t] = name_term_counts.get(t, 0) + 1
            logging.info(f"Filtered (name-clean):   {line}")
            logging.info(f"  -> matched: {', '.join(sorted(terms))}")
            continue
        name_clean_written += 1
        name_clean_lines.append(line)

    # Calculate clean totals from name_clean_lines
    name_clean_pairs = [name_sorted[i] for i, line in enumerate(name_lines) if _matched_curses(line) == set()]  # Unfiltered tuples
    clean_unique_artists_name = set(artist for artist, _, _, _, _ in name_clean_pairs if artist and artist != '(unknown artist)')
    clean_total_artists_name = len(clean_unique_artists_name)
    clean_unique_albums_name = set(album for _, _, album, _, _ in name_clean_pairs if album and album != '(unknown album)')
    clean_total_albums_name = len(clean_unique_albums_name)
    clean_total_songs_name = len(name_clean_pairs)
    header_clean_name = header_timestamp + f"Total songs: {clean_total_songs_name}\nTotal albums: {clean_total_albums_name}\nTotal artists: {clean_total_artists_name}\n\n"

    with open(name_clean_path, 'w', encoding='utf-8') as fn_clean:
        fn_clean.write(header_clean_name)  # Use clean totals with timestamp
        for line in name_clean_lines:
            fn_clean.write(line + "\n")

    return {
        'artist_total': len(artist_lines),
        'artist_clean_written': artist_clean_written,
        'artist_clean_filtered': artist_clean_filtered,
        'name_total': len(name_lines),
        'name_clean_written': name_clean_written,
        'name_clean_filtered': name_clean_filtered,
        # include per-term counts for analysis
        'artist_term_counts': artist_term_counts,
        'name_term_counts': name_term_counts,
    }

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

    out_stats = write_outputs(all_pairs, os.getcwd())

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
    if out_stats:
        print('- Clean outputs:')
        print(f"  - Artist clean: total={out_stats.get('artist_total', 0)}, "
              f"written={out_stats.get('artist_clean_written', 0)}, "
              f"filtered={out_stats.get('artist_clean_filtered', 0)}")
        print(f"  - Name clean:   total={out_stats.get('name_total', 0)}, "
              f"written={out_stats.get('name_clean_written', 0)}, "
              f"filtered={out_stats.get('name_clean_filtered', 0)}")
        # Per-term breakdown (only show non-zero terms), merged across both outputs
        term_counts: Dict[str, int] = {}
        for k, v in (out_stats.get('artist_term_counts', {}) or {}).items():
            term_counts[k] = term_counts.get(k, 0) + v
        for k, v in (out_stats.get('name_term_counts', {}) or {}).items():
            term_counts[k] = term_counts.get(k, 0) + v
        if term_counts:
            print('  - Filter term counts:')
            for term, count in sorted(term_counts.items(), key=lambda kv: (-kv[1], kv[0])):
                print(f'    • {term}: {count}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
