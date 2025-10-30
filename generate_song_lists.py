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
    # Look for pattern: (key "value") or (key value) where value is a bare atom
    i = 0
    pattern = f'({key}'
    while True:
        idx = entry_text.find(pattern, i)
        if idx == -1:
            return None
        # Ensure it's actually a list start: previous char must be '(' at idx
        # We already searched for '(' + key so that's fine; now move after key
        j = idx + len(pattern)
        # Skip whitespace
        while j < len(entry_text) and entry_text[j].isspace():
            j += 1
        if j >= len(entry_text):
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
        else:
            # read until whitespace or ')'
            start_val = j
            while j < len(entry_text) and not entry_text[j].isspace() and entry_text[j] != ')':
                j += 1
            val = entry_text[start_val:j].strip()
            if val:
                return val
        i = j


def parse_entries_for_artist_name(entries: List[str]) -> Tuple[List[Tuple[str, str]], Dict[str, int]]:
    results: List[Tuple[str, str]] = []
    stats: Dict[str, int] = {
        'total_entries': len(entries),
        'missing_artist': 0,
        'missing_name': 0,
    }
    for e in entries:
        name = extract_string_field(e, 'name')
        artist = extract_string_field(e, 'artist')
        if name and artist:
            results.append((artist, name))
        else:
            if not artist:
                stats['missing_artist'] += 1
            if not name:
                stats['missing_name'] += 1
    return results, stats


def write_outputs(pairs: List[Tuple[str, str]], cwd: str) -> None:
    artist_sorted = sorted(pairs, key=lambda x: (x[0].lower(), x[1].lower()))
    name_sorted = sorted(pairs, key=lambda x: (x[1].lower(), x[0].lower()))

    artist_path = os.path.join(cwd, 'SongListSortedByArtist.txt')
    name_path = os.path.join(cwd, 'SongListSortedBySongName.txt')

    with open(artist_path, 'w', encoding='utf-8') as fa:
        for artist, name in artist_sorted:
            fa.write(f"{artist} - {name}\n")

    with open(name_path, 'w', encoding='utf-8') as fn:
        for artist, name in name_sorted:
            fn.write(f"{name} by {artist}\n")


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
    pairs, stats = parse_entries_for_artist_name(entries)

    if not pairs:
        logging.warning('No (artist, name) pairs found. Outputs may be empty.')

    write_outputs(pairs, os.getcwd())

    # Summary
    total = stats.get('total_entries', 0)
    extracted = len(pairs)
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
    print(f'- Lines written to SongListSortedByArtist.txt: {extracted}')
    print(f'- Lines written to SongListSortedBySongName.txt: {extracted}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
