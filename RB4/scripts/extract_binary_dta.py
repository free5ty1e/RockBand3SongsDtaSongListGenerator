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
    # Handle G prefix (single uppercase followed by title, e.g., GHoliday -> Holiday)
    if len(s) >= 3 and s[0].isupper() and s[1].isupper() and s[2].isupper():
        return s[1:]
    for i in range(len(s)):
        if i + 1 < len(s) and s[i].isupper() and s[i+1].islower():
            return s[i:] if i > 0 else s
    return s


def _is_garbage_string(s: str) -> bool:
    """Check if string is binary garbage that should be skipped."""
    if not s or len(s) < 2:
        return True
    # Starts with special characters (binary garbage indicator)
    if s[0] in '@*`#%$&^~[]{}|<>?/\\~' or (len(s) > 0 and ord(s[0]) < 32):
        return True
    # Contains null bytes or control chars
    if any(ord(c) < 32 and c not in '\t\n' for c in s):
        return True
    # All uppercase short strings are usually garbage
    if s.isupper() and len(s) <= 4:
        return True
    # Strings with hex-like patterns at start
    if len(s) >= 2 and all(c in 'ABCDEF0123456789' for c in s[:2]) and s[0] in 'ABCDEF':
        return True
    # Short uppercase prefix + lowercase rest (like "GBasket", not standalone words)
    # Must be short (3-10 chars) and have clear prefix boundary
    if len(s) >= 3 and len(s) <= 12 and s[0].isupper() and s[1].isupper() and s[2].islower():
        return True
    return False


def is_valid_title(s: str) -> bool:
    """Check if string is likely a valid title (not binary garbage)."""
    if not s or len(s) < 2:
        return False
    if _is_garbage_string(s):
        return False
    # Starts with lowercase is OK for actual song names (like "alive")
    if s[0].islower() and len(s) >= 3:
        return True
    # All uppercase prefix like GTitle is garbage
    if len(s) >= 3 and s[0].isupper() and s[1:].isupper():
        return False
    # Multi-word is almost always valid
    if ' ' in s:
        return True
    # Single-word starting with uppercase, must be long enough
    if s[0].isupper() and s[0].isalpha() and len(s) >= 4:
        return True
    return False


def is_valid_artist_or_album(s: str) -> bool:
    """Check if string is likely a valid artist or album (not split garbage)."""
    if not s or len(s) < 4:
        return False
    if s[0].islower():
        return False
    if s.isupper() and len(s) <= 5:
        return False
    if ' ' in s or len(s) >= 6:
        return True
    if s[0].isupper():
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
    """Extract song duration from fixed offset 884 (float32 in seconds)."""
    try:
        if len(data) > 888:
            duration = struct.unpack('<f', data[884:888])[0]
            if 60.0 <= duration <= 900.0:
                return int(duration * 1000)
    except:
        pass
    return 0


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

    def merge_split_strings(items: list, start: int) -> list:
        merged = []
        i = start
        while i < len(items):
            s = items[i]
            # Skip garbage strings
            if _is_garbage_string(s):
                i += 1
                continue
            if i + 1 < len(items):
                next_s = items[i + 1]
                # Skip garbage in next_s too
                if _is_garbage_string(next_s):
                    merged.append(s)
                    i += 1
                    continue
                # Merge short split parts (like Mot + rhead = Motörhead)
                # Both must be short AND second must start with lowercase
                if len(s) <= 5 and len(next_s) <= 5 and next_s[0].islower():
                    merged.append(s + next_s)
                    i += 2
                    continue
                # Merge when first ends with lowercase and next starts with lowercase
                if s[-1].islower() and next_s[0].islower():
                    merged.append(s + next_s)
                    i += 2
                    continue
                # Merge short uppercase prefix with rest (like 'Mot' + 'rhead' = 'Motrhead')
                if len(s) <= 4 and s[0].isupper() and next_s and next_s[0].islower():
                    merged.append(s + next_s)
                    i += 2
                    continue
            merged.append(s)
            i += 1
        return merged

    if source_idx >= 0 and genre_idx > source_idx:
        between = strings[source_idx + 1:genre_idx]
    elif source_idx >= 0:
        between = strings[source_idx + 1:]
    else:
        between = strings[:5] if genre_idx > 0 else strings[:5]

    # First, filter out garbage and merge split strings in the entire between list
    filtered_between = [s for s in between if not _is_garbage_string(s)]
    merged_between = merge_split_strings(filtered_between, 0)

    title, artist, album = None, None, None

    # Find all valid title candidates
    title_candidates = []
    for i in range(min(6, len(merged_between))):
        candidate = merged_between[i]
        if is_valid_title(candidate):
            title_candidates.append((i, candidate))

    if title_candidates:
        # Check if artist is in position BEFORE title (typical RB2 format: artist, title)
        # Or AFTER title (typical RB4 format: title, artist)
        first_title_idx = title_candidates[0][0]
        last_title_idx = title_candidates[-1][0]
        
        # If first title is at index 1 or higher, likely has artist before it
        if first_title_idx > 0:
            best_idx, best_title = title_candidates[0]
        else:
            # Use last title
            best_idx, best_title = title_candidates[-1]
        
        title = _strip_binary_prefix(best_title)
        
        # Artist can be before OR after the title
        artist = None
        artist_idx = -1
        # First check positions after title
        for j in range(best_idx + 1, min(best_idx + 3, len(merged_between))):
            if is_valid_title(merged_between[j]):
                artist = merged_between[j]
                artist_idx = j
                break
        # If no artist after, check before title (some songs have artist before title)
        if not artist and best_idx > 0:
            for j in range(best_idx - 1, max(-1, best_idx - 3), -1):
                if is_valid_title(merged_between[j]):
                    artist = merged_between[j]
                    artist_idx = j
                    break
        
        # Album is after artist (or after title if no artist found)
        album = None
        search_start = (artist_idx + 1) if artist_idx >= 0 else best_idx + 1
        for k in range(search_start, min(search_start + 3, len(merged_between))):
            if is_valid_title(merged_between[k]):
                album = merged_between[k]
                break

    if not title and len(between) >= 1:
        title = _strip_binary_prefix(between[0])
    if not artist and len(between) >= 2:
        artist = between[1]
    if not album and len(between) >= 3:
        album = between[2]

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
