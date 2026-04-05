#!/usr/bin/env python3
"""
extract_binary_dta.py — Extract song metadata from Rock Band 4 binary .songdta_ps4 files.
Uses dynamic structural detection based on known markers (source code, genre).
"""

import sys
import re
import json
import os
import argparse
import struct

_GENRE_TAGS = {
    "rock", "metal", "poprock", "pop", "country", "classicrock",
    "alternativerock", "hardrock", "punk", "indie", "dance",
    "electronic", "popdanceelectronic", "hiphoprap", "rb", "soul",
    "blues", "jazz", "classical", "new wave", "grunge", "alternative",
    "numetal", "prog", "latin", "world", "novelty", "emocore",
    "fusion", "jpop", "jrock", "reggae"
}

_SOURCE_REGEX = re.compile(r'^rb\d(_dlc)?$|^rbn\d?$|^gdrb$|^tbrb$|^greenday$|^beatles$|^rb4_dlc$')

_FRIENDLY_SOURCES = {
    'rb1': 'Rock Band 1', 'rb2': 'Rock Band 2', 'rb3': 'Rock Band 3',
    'rb1_dlc': 'Rock Band 1 DLC', 'rb2_dlc': 'Rock Band 2 DLC', 'rb3_dlc': 'Rock Band 3 DLC',
    'rb4_dlc': 'Rock Band 4 DLC', 'rbn1': 'Rock Band Network 1', 'rbn2': 'Rock Band Network 2',
    'greenday': 'Rock Band Green Day', 'beatles': 'The Beatles: Rock Band',
    'gdrb': 'Rock Band Green Day', 'tbrb': 'The Beatles: Rock Band',
}


def _strip_binary_prefix(s: str) -> str:
    """Strip leading garbage prefix from title (e.g., GHoliday -> Holiday)."""
    if not s or len(s) < 2:
        return s
    for i in range(len(s)):
        if i + 1 < len(s) and s[i].isupper() and s[i+1].islower():
            return s[i:] if i > 0 else s
    return s


def is_valid_title(s: str) -> bool:
    """Check if string is likely a valid title (not binary garbage)."""
    if not s or len(s) < 3:
        return False
    # Garbage: starts with lowercase, or with symbol then lowercase
    if s[0].islower() or (not s[0].isalpha() and len(s) > 0 and len(s) < 4):
        return False
    # Multi-word is almost always valid
    if ' ' in s:
        return True
    # Single-word: must start with uppercase and have mixed case OR be longer
    if s[0].isupper() and (any(c.islower() for c in s) or len(s) >= 5):
        return True
    return False


def extract_year(data: bytes, genre: str) -> int:
    """Find year as 4-byte LE integer immediately before genre string."""
    try:
        genre_bytes = genre.encode('utf-8')
        idx = data.find(genre_bytes)
        if idx >= 4:
            year_bytes = data[idx-4:idx]
            year = struct.unpack('<I', year_bytes)[0]
            if 1950 <= year <= 2026:
                return year
    except:
        pass
    return 0


def extract_duration(data: bytes) -> int:
    """Find float32 between 60.0 and 900.0 seconds, return ms."""
    matches = []
    for i in range(0, len(data) - 4, 4):
        try:
            val = struct.unpack('<f', data[i:i+4])[0]
            if 60.0 <= val <= 900.0:
                matches.append(int(val * 1000))
        except:
            pass
    return max(matches) if matches else 0


def parse_songdta(filepath: str, default_source="Custom") -> dict:
    """Dynamic parser for .songdta_ps4 files using positional extraction."""
    with open(filepath, 'rb') as f:
        data = f.read()

    raw = re.findall(b'[ -~]{2,}', data)
    strings = [s.decode('utf-8', errors='replace').strip() for s in raw]

    source = default_source
    genre = None
    source_idx = -1
    genre_idx = -1

    for i, s in enumerate(strings):
        s_lower = s.lower()
        if source_idx == -1 and _SOURCE_REGEX.match(s_lower):
            source = s_lower
            source_idx = i
        elif genre_idx == -1 and s_lower in _GENRE_TAGS:
            genre = s_lower
            genre_idx = i

    if source_idx == -1:
        source = "Custom"

    if source_idx >= 0 and genre_idx > source_idx:
        between = strings[source_idx + 1:genre_idx]
    elif source_idx >= 0:
        between = strings[source_idx + 1:]
    else:
        between = strings[:5] if genre_idx > 0 else strings[:5]

    # Check if position 0 is valid title, otherwise use position 1
    if between and is_valid_title(between[0]):
        title = _strip_binary_prefix(between[0])
        artist = between[1] if len(between) > 1 else None
        album = between[2] if len(between) > 2 else None
    else:
        # Position 0 is garbage, use 1, 2, 3
        title = _strip_binary_prefix(between[1]) if len(between) > 1 else None
        artist = between[2] if len(between) > 2 else None
        album = between[3] if len(between) > 3 else None

    if not title:
        title = "Unknown Title"
    if not artist:
        artist = "Unknown Artist"

    year = extract_year(data, genre) if genre else 0
    duration_ms = extract_duration(data)
    final_source = _FRIENDLY_SOURCES.get(source.lower(), source.title())

    return {
        "artist": artist,
        "title": title,
        "album": album,
        "year": year,
        "durationMs": duration_ms,
        "source": final_source,
        "_debug_file": os.path.basename(filepath),
        "parse_mode": "dynamic"
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', nargs='+', help='Input directories or files')
    parser.add_argument('--source', default='Custom', help='Default source name')
    parser.add_argument('output', help='Output JSON file')
    args = parser.parse_args()

    results = []
    files = []
    for path in args.input:
        if os.path.isdir(path):
            for root, dirs, fnames in os.walk(path):
                for f in fnames:
                    if f.endswith('.songdta_ps4'):
                        files.append(os.path.join(root, f))
        else:
            files.append(path)

    for filepath in files:
        try:
            results.append(parse_songdta(filepath, args.source))
        except Exception as e:
            print(f"ERROR parsing {filepath}: {e}", file=sys.stderr)

    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)


if __name__ == '__main__':
    main()
