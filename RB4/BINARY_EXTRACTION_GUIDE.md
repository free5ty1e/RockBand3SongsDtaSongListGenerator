# Rock Band 4 Binary Metadata Extraction Guide

## Overview

This document describes how to extract song metadata from Rock Band 4 `.songdta_ps4` binary files found in PS4 PKG packages. The binary format uses fixed offsets for all fields, documented in LibForge's 010 Editor template.

## Binary File Structure (Exact Offsets)

Based on `LibForge/010/songdta.bt` template:

| Field | Offset | Size | Type | Description |
|-------|--------|------|------|-------------|
| `songdta_type` | 0 | 4 | uint | File type identifier |
| `song_id` | 4 | 4 | uint | Unique song ID |
| `version` | 8 | 2 | short | Version number |
| `game_origin` | 10 | 18 | string | Source code (rb2, greenday, etc.) |
| `preview_start` | 28 | 4 | float | Preview start position (seconds from song start) |
| `preview_end` | 32 | 4 | float | Preview end position (seconds from song start) |
| `name` | 36 | 256 | string | Song title |
| `artist` | 292 | 256 | string | Artist name |
| `album_name` | 548 | 256 | string | Album name |
| `album_track_number` | 804 | 2 | short | Track number on album |
| `album_year` | 808 | 4 | uint | Year added to RB |
| `original_year` | 812 | 4 | uint | Original release year |
| `genre` | 816 | 64 | string | Genre tag |
| `song_length` | 880 | 4 | float | Song length (variable, use min float method instead) |
| `guitar` | 884 | 4 | float | Guitar difficulty |
| `bass` | 888 | 4 | float | Bass difficulty |
| `vocals` | 892 | 4 | float | Vocals difficulty |
| `drums` | 896 | 4 | float | Drums difficulty |
| `band` | 900 | 4 | float | Band difficulty |
| `keys` | 904 | 4 | float | Keys difficulty |
| `real_keys` | 908 | 4 | float | Real Keys difficulty |
| `tutorial` | 912 | 1 | byte | Tutorial flag |
| `album_art` | 913 | 1 | byte | Album art flag |
| `cover` | 914 | 1 | byte | Cover version flag |
| `vocal_gender` | 915 | 1 | byte | Vocal gender (1=Male, 2=Female) |
| `anim_tempo` | 916 | 16 | string | Animation tempo |
| `has_markup` | 932 | 1 | byte | Has markup flag |
| `vocal_parts` | 936 | 1 | byte | Number of vocal parts |
| `solos` | 940 | 4 | struct | Solo flags |
| `fake` | 944 | 1 | byte | Fake vocal flag |
| `shortname` | 945 | 256 | string | Song folder name |

## String Fields

All string fields are null-terminated UTF-8. To read:
```python
def _read_string(data, offset, max_size):
    chunk = data[offset:offset + max_size]
    return chunk.split(b'\x00')[0].decode('utf-8', errors='replace').strip()
```

## Duration Extraction

The `song_length` field at offset 880 doesn't contain the expected value. Instead, duration is calculated by finding the minimum float value in the range 60-500 seconds across the entire file.

```python
def _calculate_duration_ms(data):
    floats_in_range = []
    for i in range(0, len(data) - 4, 4):
        val = struct.unpack('<f', data[i:i+4])[0]
        if 60.0 <= val <= 500.0:
            floats_in_range.append(val)
    if floats_in_range:
        return int(min(floats_in_range) * 1000)
    return 0
```

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

## Instrument Emoji

| Instrument | Emoji |
|------------|-------|
| Guitar | 🎸 |
| Bass | 🎸 |
| Drums | 🥁 |
| Vocals | 🎤 |
| Keys | 🎹 |

## Output Fields

The parser produces a JSON object with all fields:

```json
{
  "artist": "Motörhead",
  "title": "Ace of Spades '08",
  "album": "Ace of Spades '08",
  "year": 1980,
  "durationMs": 255000,
  "source": "Rock Band 2",
  "songId": 251,
  "shortName": "aceofspades",
  "gameOrigin": "rb2",
  "albumYear": 2008,
  "originalYear": 1980,
  "albumTrackNumber": 1,
  "genre": "metal",
  "previewStart": 16720.92,
  "previewEnd": 46720.83,
  "difficulty": {
    "guitar": 388.0,
    "bass": 471.0,
    "vocals": 255.0,
    "drums": 429.0,
    "band": 453.0,
    "keys": 0.0,
    "realKeys": 0.0
  },
  "instruments": "🎸🎸🎤🥁",
  "instrumentList": ["guitar", "bass", "vocals", "drums"],
  "vocalGender": "Male",
  "animTempo": "medium",
  "vocalParts": 1,
  "songdtaType": 11,
  "version": -1,
  "_debug_file": "aceofspades.songdta_ps4",
  "parse_mode": "exact_offsets"
}
```

## References

- LibForge (mtolly/LibForge) - https://github.com/mtolly/LibForge
- 010 Editor Templates - `010/songdta.bt`
- Rock Band Wiki (rockband.fandom.com)
- DtxCS (maxton/DtxCS) - DTA parsing library
