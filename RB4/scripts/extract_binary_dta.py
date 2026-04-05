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

# Valid source codes that appear in the binary
_SOURCE_REGEX = re.compile(r'^rb\d(_dlc)?$|^rbn\d?$|^gdrb$|^tbrb$|^greenday$|^beatles$|^rb4_dlc$')

_FRIENDLY_SOURCES = {
    'rb1': 'Rock Band 1', 'rb2': 'Rock Band 2', 'rb3': 'Rock Band 3',
    'rb1_dlc': 'Rock Band 1 DLC', 'rb2_dlc': 'Rock Band 2 DLC', 'rb3_dlc': 'Rock Band 3 DLC',
    'rb4_dlc': 'Rock Band 4 DLC', 'rbn1': 'Rock Band Network 1', 'rbn2': 'Rock Band Network 2',
    'greenday': 'Rock Band Green Day', 'beatles': 'The Beatles: Rock Band',
    'gdrb': 'Rock Band Green Day', 'tbrb': 'The Beatles: Rock Band',
}
def _strip_binary_prefix(s: str) -> str:
    """Remove leading binary garbage prefix from title strings.
    
    Binary format: [length][garbage][Title]
    Garbage prefixes are uppercase single letters (G, J, H, etc.)
    Real title starts at first uppercase letter followed by lowercase.
    
    Examples:
      - "GHoliday" -> "Holiday" 
      - "JHBrain Stew/Jaded" -> "Brain Stew/Jaded" 
      - "GExtraordinary Girl" -> "Extraordinary Girl"
    """
    if not s or len(s) < 2:
        return s
    
    # Find first uppercase letter followed by lowercase (the real title start)
    for i in range(len(s)):
        if i + 1 < len(s) and s[i].isupper() and s[i+1].islower():
            if i > 0:
                return s[i:]
            return s
    
    return s

def _needs_prefix_strip(s: str) -> bool:
    """Check if string looks like it has a garbage prefix (e.g., 'sGD"', 'GBasket Case')."""
    if not s or len(s) < 3:
        return False
    if re.match(r'^[a-z]{2,}[A-Z]', s):
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
    """
    Dynamic parser for .songdta_ps4 files.
    
    Binary structure: [source_code][garbage][Title][Artist][Album][Genre][Difficulty][SongID]
    
    The KEY pattern is POSITION: strings between source and genre are always
    Title, Artist, Album in that order. This is more reliable than case detection.
    
    Garbage strings (binary length prefixes) typically appear before the real data.
    """
    with open(filepath, 'rb') as f:
        data = f.read()

    # Extract all printable ASCII strings
    raw = re.findall(b'[ -~]{2,}', data)
    strings = [s.decode('utf-8', errors='replace').strip() for s in raw]

    # Find source code position (first valid source regex match)
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

    # If no source found, default to Custom
    if source_idx == -1:
        source = "Custom"

    # Get strings between source and genre
    if source_idx >= 0 and genre_idx > source_idx:
        between = strings[source_idx + 1:genre_idx]
    elif source_idx >= 0:
        between = strings[source_idx + 1:]
    else:
        between = strings[:5] if genre_idx > 0 else strings[:5]

    # The structure is always: [title_with_garbage][artist][album]
    # First string is title (may have garbage prefix), second is artist, third is album
    # But there may be garbage at the start, so filter and take position 0, 1, 2
    
    # Filter out obvious garbage (but keep position-aware)
    def is_garbage(s):
        if not s or len(s) < 2:
            return True
        if not any(c.isalpha() for c in s):
            return True
        if len(s) <= 4 and s.isupper():
            return True
        if len(s) >= 3 and s[0].islower() and s[1].isupper():
            return True
        letters = sum(1 for c in s if c.isalpha())
        if len(s) > 3 and letters / len(s) < 0.4:
            return True
        return False
    
    # Filter but track original position - take first 3 valid strings
    candidates = []
    for s in between:
        if is_garbage(s):
            continue
        # Extra check: title should have space OR be a known pattern (contains "of", "the", etc)
        # Short strings (6 chars or less) without spaces are likely garbage
        if len(s) <= 6 and ' ' not in s:
            continue
        candidates.append(s)
        if len(candidates) >= 3:
            break
    
    # Assign by position: first candidate = title, second = artist, third = album
    title = candidates[0] if len(candidates) > 0 else None
    artist = candidates[1] if len(candidates) > 1 else None
    album = candidates[2] if len(candidates) > 2 else None

    # Clean up title (strip any leading garbage prefix)
    if title:
        title = _strip_binary_prefix(title)

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
