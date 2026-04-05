# Rock Band 4 Custom Song List Generator

This folder contains a pipeline for scanning PS4 (fPKG) Rock Band 4 custom song packages, extracting metadata from compiled `.songdta_ps4` binary blobs, and generating a text-based, human-readable song list that mirrors the output format of the older RB3 tool.

## Overview

The standard `rb4songlistWithRivals.txt` file serves as the baseline database of all default RB4 songs + Rivals expansion tracks. 
This tool supplements the baseline with your custom songs, dropping duplicates (custom files take precedence).

## Binary Structure (.songdta_ps4)

The `.songdta_ps4` files contain compiled song metadata in a binary format. Through analysis, we've discovered the following structure:

```
[source_code][garbage_prefix][Title][Artist][Album][Genre][Difficulty][song_id]
```

### Key Patterns

1. **Source Code**: Located first, contains identifiers like:
   - `greenday` - Rock Band Green Day export
   - `rb4_dlc` - Rock Band 4 DLC
   - `rb1`, `rb2`, `rb3` - Rock Band 1/2/3
   - `rbn1`, `rbn2` - Rock Band Network

2. **Garbage Prefixes**: Binary length bytes that appear before the title, typically:
   - Single uppercase letter: `G`, `H`, `J` (e.g., `GHoliday`)
   - Multiple: `JH`, `JHB` (e.g., `JHBrain Stew`)
   - Lowercase + uppercase: `sGD"` (garbage, not real title)

3. **Genre Tags**: Known genre strings used as anchors:
   - `rock`, `metal`, `punk`, `pop`, `country`, `rb`, `soul`, etc.

4. **Metadata Position**: Strings between source code and genre are always:
   - Position 0: Title (may have garbage prefix)
   - Position 1: Artist
   - Position 2: Album

## Two-Step Workflow

**1. Scan custom PKG files**
Run the shell script to recursively scan a folder full of `.pkg` files:
```bash
bash RB4/scripts/scan_rb4_pkgs.sh --dir /path/to/pkgs --out RB4/rb4_custom_songs.json
```

This uses `PkgTool.Core` (.NET 8) to unpack fPKGs and extracts metadata from binary blobs.

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

## Extraction Algorithm

The `extract_binary_dta.py` parser works as follows:

1. Extract all printable ASCII strings from binary
2. Find source code position using regex (`^rb\d(_dlc)?$|^rbn\d?$|^greenday$...`)
3. Find genre position using known genre list
4. Take strings between source and genre
5. Filter garbage (short strings, uppercase-only, lowercase+uppercase pattern)
6. Assign by position: title, artist, album
7. Strip leading garbage prefix from title

## Setup & Dependencies

Runs in **Devcontainer** (Ubuntu 24.04) with:
- .NET 8 Runtime - for PkgTool.Core
- Python 3 - for extract_binary_dta.py
- Node.js 22 - for generator
- PkgTool.Core - at `/usr/local/bin/PkgTool.Core`

## Known Limitations

- Some edge cases with garbage prefixes not fully filtered
- Album extraction not always accurate
- Duration extraction not working for all songs

## Troubleshooting

If you see junk in output:
1. Check `RB4/rb4_custom_songs.json`
2. Inspect raw extraction in `RB4/working_dir/`
3. Examine binary directly: `strings song.songdta_ps4`
4. Refine heuristics in `extract_binary_dta.py`
