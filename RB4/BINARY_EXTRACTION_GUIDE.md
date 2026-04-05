# Rock Band 4 Binary Metadata Extraction Guide

## Overview

This document describes how to extract song metadata (title, artist, album, year, duration, source) from Rock Band 4 `.songdta_ps4` binary files found in PS4 PKG packages.

## Binary File Structure

The `.songdta_ps4` file is a binary file containing UTF-8 encoded strings with `0xCD 0xAB` (padding) bytes between strings.

### Typical String Order

1. **Source code** - identifies game origin (e.g., `rb2`, `greenday`, `rb4_dlc`)
2. **Title** - song title (may have garbage prefix like `GTitle` or `GHoliday`)
3. **Artist** - band/artist name
4. **Album** - album name
5. **Genre** - genre tag (e.g., `rock`, `punk`, `metal`, `grunge`)
6. **Difficulty** - tempo/difficulty (e.g., `medium`, `fast`, `slow`)
7. **Short name** - song folder name

### Garbage Patterns

The binary contains garbage strings that must be filtered:
- **Prefix patterns**: `GTitle`, `GHoliday`, `GBasket` - single uppercase letter prefix + title
- **Split names**: `Mot` + `rhead` = `Motörhead` (special chars split across bytes)
- **Special chars**: `@*`#%$&^~[]{}|<>?/\` - indicate garbage
- **Hex patterns**: Strings starting with hex chars like `0A`, `FF`

## Extraction Rules

### 1. String Extraction
```python
import re
raw = re.findall(b'[ -~]{2,}', data)  # Extract printable ASCII strings
strings = [s.decode('utf-8', errors='replace').strip() for s in raw]
```

### 2. Source Detection
Use regex to find source code in first few strings:
```python
_SOURCE_REGEX = re.compile(r'^rb\d(_dlc)?$|^rbn\d?$|^gdrb$|^tbrb$|^greenday$|^beatles$|^rb4_dlc$')
```

### 3. Genre Detection
Find genre tag to determine metadata boundaries:
```python
_GENRE_TAGS = {"rock", "metal", "punk", "grunge", "pop", "alternative", ...}
```

### 4. Garbage Filtering
```python
def _is_garbage_string(s: str) -> bool:
    if not s or len(s) < 2:
        return True
    # Special char prefix
    if s[0] in '@*`#%$&^~[]{}|<>?/\\~':
        return True
    # All uppercase short
    if s.isupper() and len(s) <= 4:
        return True
    # Single uppercase prefix + lowercase rest (like "GBasket")
    if len(s) >= 3 and len(s) <= 12 and s[0].isupper() and s[1].isupper() and s[2].islower():
        return True
    return False
```

### 5. Title Validation
```python
def is_valid_title(s: str) -> bool:
    if not s or len(s) < 2:
        return False
    if _is_garbage_string(s):
        return False
    # Lowercase start OK (like "alive")
    if s[0].islower() and len(s) >= 3:
        return True
    # Multi-word valid
    if ' ' in s:
        return True
    # Single-word must start uppercase
    if s[0].isupper() and len(s) >= 4:
        return True
    return False
```

### 6. Split String Merging
Merge split artist names (Motörhead stored as `Mot` + `rhead`):
```python
def merge_split_strings(items: list, start: int) -> list:
    merged = []
    i = start
    while i < len(items):
        s = items[i]
        if i + 1 < len(items):
            next_s = items[i + 1]
            # Both short + second starts lowercase
            if len(s) <= 5 and len(next_s) <= 5 and next_s[0].islower():
                merged.append(s + next_s)
                i += 2
                continue
            # First ends lowercase + second starts lowercase
            if s[-1].islower() and next_s[0].islower():
                merged.append(s + next_s)
                i += 2
                continue
        merged.append(s)
        i += 1
    return merged
```

### 7. Title/Artist Position Logic

**RB2 format**: artist → title → album (artist BEFORE title)
**RB4/Green Day format**: title → artist → album

Strategy: Find all valid titles, then:
- If first title is at index > 0, assume artist is BEFORE title
- Otherwise use artist AFTER title

### 8. Year Extraction
Year is stored as 4-byte little-endian integer immediately before genre:
```python
def extract_year(data: bytes, genre: str) -> int:
    genre_bytes = genre.encode('utf-8')
    idx = data.find(genre_bytes)
    if idx >= 4:
        year = struct.unpack('<I', data[idx-4:idx])[0]
        if 1950 <= year <= 2026:
            return year
    return 0
```

### 9. Duration Extraction
Duration is stored as float32 at fixed offset 884 (seconds):
```python
def extract_duration(data: bytes) -> int:
    if len(data) > 888:
        duration = struct.unpack('<f', data[884:888])[0]
        if 60.0 <= duration <= 900.0:
            return int(duration * 1000)  # Convert to ms
    return 0
```

## Known Limitations

1. **Special characters**: UTF-8 chars like `ö` in `Motörhead` are lost (shows as `Motrhead`)
2. **Duration offset**: Fixed at 884 works for most songs but may vary
3. **Split detection**: Not perfect - some garbage strings may be merged incorrectly
4. **Album detection**: Sometimes picks wrong position (title repeated as album)

## Source Mapping

| Binary Code | Friendly Name |
|-------------|---------------|
| `rb1` | Rock Band 1 |
| `rb2` | Rock Band 2 |
| `rb3` | Rock Band 3 |
| `rb4_dlc` | Rock Band 4 DLC |
| `greenday` | Rock Band Green Day |
| `rbn1` | Rock Band Network 1 |
| `rbn2` | Rock Band Network 2 |
| `beatles` | The Beatles: Rock Band |

## File Locations

- `extract_binary_dta.py` - Main extraction script
- `rb4_custom_songs.json` - Extracted songs from all PKGs

## References

- LibForge (mtolly/LibForge) - Rock Band file format research
- Rock Band Wiki (rockband.fandom.com) - Song metadata verification
- DtxCS (maxton/DtxCS) - DTA parsing library
