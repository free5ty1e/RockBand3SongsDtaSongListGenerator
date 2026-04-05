# Rock Band 4 Custom Song List Generator

This folder contains a pipeline for scanning PS4 (fPKG) Rock Band 4 custom song packages, extracting metadata from compiled `.songdta_ps4` binary blobs, and generating a text-based, human-readable song list that mirrors the output format of the older RB3 tool.

## Overview

The standard `rb4songlistWithRivals.txt` file serves as the baseline database of all default RB4 songs + Rivals expansion tracks. 
This tool supplements the baseline with your custom songs, dropping duplicates (custom files take precedence).

## Two-Step Workflow

**1. Scan custom PKG files**
Run the shell script to recursively scan a folder full of `.pkg` files. This script uses `PkgTool.Core` (.NET 8) to unpack the fPKGs and a custom Python scraper to extract metadata from the binary blobs:
```bash
bash RB4/scripts/scan_rb4_pkgs.sh --dir /path/to/pkgs --out RB4/rb4_custom_songs.json
```
_Note: Decrypted files are temporarily stored in `RB4/working_dir/` for observation and debugging as requested._

**2. Generate Text Lists**
Run the Node.js generator to combine the baseline files with the custom JSON data:
```bash
node RB4/generate_rb4_song_list.js --baseline RB4/rb4songlistWithRivals.txt --custom RB4/rb4_custom_songs.json
```

This generates 4 text files in `RB4/output/`:
- `SongListSortedByArtist.txt`
- `SongListSortedBySongName.txt`
- `SongListSortedByArtistClean.txt` (profanity filtered)
- `SongListSortedBySongNameClean.txt` (profanity filtered)

## Setup & Dependencies
The project is designed to run in the provided **Devcontainer** (Ubuntu 24.04), which comes pre-configured with:
- **.NET 8 Runtime**: Required for `PkgTool.Core`.
- **Python 3**: For the `extract_binary_dta.py` heuristic scraper.
- **Node.js 22**: For the final song list generator.
- **PkgTool.Core**: Installed at `/usr/local/bin/PkgTool.Core` for fPKG decryption.
- **Onyx CLI**: Available for supplementary DTA utilities.

## Output Format
```
Artist (Album) - Song Title (Year / MM:SS) - Source
```
Example:
```
The Cramps (Psychedelic Jungle) - Goo Goo Muck (? / ?:??) - Custom
```

## Troubleshooting
If you see junk characters (e.g. "G", "H") in the output or flipped Artist/Title:
1. Check `RB4/rb4_custom_songs.json` to identify the problematic file.
2. Inspect the raw extraction in `RB4/working_dir/`.
3. Refine the heuristics in `RB4/scripts/extract_binary_dta.py`.
