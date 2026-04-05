# Rock Band 4 Custom Song List Generator

This folder contains a pipeline for scanning PS4 (fPKG) Rock Band 4 custom song packages, extracting metadata from compiled `.songdta_ps4` binary blobs, and generating a text-based, human-readable song list that mirrors the output format of the older RB3 tool.

## Overview

The standard `rb4songlistWithRivals.txt` file serves as the baseline database of all default RB4 songs + Rivals expansion tracks.
This tool supplements the baseline with your custom songs, dropping duplicates (custom files take precedence).

## Binary Structure (.songdta_ps4)

The `.songdta_ps4` files contain compiled song metadata using a fixed binary structure documented in LibForge's 010 Editor template (`LibForge/010/songdta.bt`).

### Field Offsets

| Field           | Offset | Description                       |
| --------------- | ------ | --------------------------------- |
| `songdta_type`  | 0      | File type identifier              |
| `song_id`       | 4      | Unique song ID                    |
| `version`       | 8      | Version number                    |
| `game_origin`   | 10     | Source code (rb2, greenday, etc.) |
| `preview_start` | 28     | Preview start position (seconds)  |
| `preview_end`   | 32     | Preview end position (seconds)    |
| `name`          | 36     | Song title                        |
| `artist`        | 292    | Artist name                       |
| `album_name`    | 548    | Album name                        |
| `album_year`    | 808    | Year added to RB                  |
| `original_year` | 812    | Original release year             |
| `genre`         | 816    | Genre tag                         |
| `guitar`        | 884    | Guitar difficulty                 |
| `bass`          | 888    | Bass difficulty                   |
| `vocals`        | 892    | Vocals difficulty                 |
| `drums`         | 896    | Drums difficulty                  |
| `shortname`     | 945    | Song folder name                  |

### Duration Extraction

The `song_length` field at offset 880 contains garbage data. Duration is calculated by finding the minimum float value in range 60-500 seconds across the entire file.

## Two-Step Workflow

**1. Extract binary metadata**
Run the Python script to extract from all `.songdta_ps4` files:

```bash
python3 RB4/scripts/extract_binary_dta.py <songs_dir> --source <source> RB4/rb4_custom_songs.json
```

**2. Generate Text Lists**
Run the Node.js generator to combine baseline with custom JSON:

```bash
node RB4/generate_rb4_song_list.js --baseline RB4/rb4songlistWithRivals.txt --custom RB4/rb4_custom_songs.json
```

Generates 4 text files in `RB4/output/`:

- `SongListSortedByArtist.txt`
- `SongListSortedBySongName.txt`
- `SongListSortedByArtistClean.txt` (profanity filtered)
- `SongListSortedBySongNameClean.txt` (profanity filtered)

## Output Format

Each line contains:

```
Artist (Album) - Title (Year / Duration) - Source [ShortName]🎸🎤🥁
```

Where:

- `Artist` - Band name
- `Album` - Album name
- `Title` - Song title
- `Year` - Release year
- `Duration` - Length in MM:SS format
- `Source` - Song source (Rock Band 2, custom, etc.)
- `ShortName` - Internal song folder name (for reference)
- `🎸🎤🥁` - Instrument icons (guitar, vocals, drums, keys)

## Extraction Details

The `extract_binary_dta.py` parser uses exact field offsets:

1. Read fixed offsets for known fields (title at 36, artist at 292, etc.)
2. Calculate duration from minimum float in reasonable range
3. Map `game_origin` to friendly source names
4. Generate instrument emoji from difficulty values > 0
5. Return complete JSON with all metadata fields

## Setup & Dependencies

Runs in **Devcontainer** (Ubuntu 24.04) with:

- Python 3 - for extract_binary_dta.py
- Node.js 22 - for generator
- PkgTool.Core - for extracting PKG files (if needed)

## Output Fields

The parser extracts all available fields:

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
  "genre": "metal",
  "previewStart": 16720.92,
  "previewEnd": 46720.83,
  "difficulty": {
    "guitar": 388.0,
    "bass": 471.0,
    "vocals": 255.0,
    "drums": 429.0,
    "band": 453.0,
    "keys": 0.0
  },
  "instruments": "🎸🎸🎤🥁",
  "instrumentList": ["guitar", "bass", "vocals", "drums"]
}
```

## References

- LibForge: https://github.com/mtolly/LibForge
- 010 Editor Template: `LibForge/010/songdta.bt`
- Rock Band Wiki: https://rockband.fandom.com
