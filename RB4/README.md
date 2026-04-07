# Rock Band 4 Custom Song List Generator

This folder contains a pipeline for scanning PS4 (fPKG) Rock Band 4 custom song packages, extracting metadata from compiled `.songdta_ps4` binary blobs, and generating a text-based, human-readable song list that mirrors the output format of the older RB3 tool.

## Overview

The standard `rb4songlistWithRivals.txt` file serves as the baseline database of all default RB4 songs + Rivals expansion tracks.
This tool supplements the baseline with your custom songs, dropping duplicates (custom files take precedence).

## Quick Start

Run the full extraction pipeline:

```bash
python3 RB4/scripts/rb4_songlist_generator.py --pkg-dir /path/to/your/pkgs --temp-dir /tmp/rb4_extract
```

Or use default paths (local `/workspace/pkgs` directory):

```bash
python3 RB4/scripts/rb4_songlist_generator.py
```

## Full Pipeline (End-to-End)

### One-Command Extraction

The `rb4_songlist_generator.py` script handles everything:

```bash
python3 RB4/scripts/rb4_songlist_generator.py \
  --pkg-dir /path/to/pkgs \
  --temp-dir /tmp/rb4_extract \
  --output-json RB4/rb4_custom_songs.json \
  --songlist-dir RB4/output
```

### Options

| Option             | Default                         | Description                                                 |
| ------------------ | ------------------------------- | ----------------------------------------------------------- |
| `--pkg-dir`        | `/workspace/pkg`                | Directory containing PKG files (local or network mount)     |
| `--temp-dir`       | `/workspace/rb4_temp`           | Temporary directory for extraction (cleaned after each PKG) |
| `--output-json`    | `RB4/rb4_custom_songs.json`     | Output JSON file with extracted metadata                    |
| `--songlist-dir`   | `RB4/output`                    | Output directory for generated song lists                   |
| `--baseline`       | `RB4/rb4songlistWithRivals.txt` | Baseline song list file                                     |
| `--incremental`    | enabled                         | Skip already-processed PKGs (saves time on re-runs)         |
| `--no-incremental` | -                               | Disable incremental mode - re-process all PKGs              |

## Network Share / SMB Access

The container cannot directly mount SMB shares (no kernel CAP_SYS_ADMIN), but can access them via `smbclient`.

### Recommended: SMB Mode (smbclient)

Use the `--smb` flag to access PKGs directly via smbclient:

```bash
python3 RB4/scripts/rb4_songlist_generator.py --smb
```

Or use the VS Code task: `RB4: Scan PKGs (SMB share via smbclient)`

This:

- Lists PKGs from SMB share
- Downloads one at a time to temp directory
- Processes and extracts songs
- Deletes PKG immediately after processing (to free space)
- Repeats for next file

### Alternative: Local PKG Folder

Copy your PKGs to `/workspace/pkgs/` or use `pkgs_test/` for testing:

```bash
python3 RB4/scripts/rb4_songlist_generator.py --pkg-dir /workspace/pkgs
```

### Docker Desktop File Sharing

If you configure Docker Desktop to share your PKG folder:

1. Open Docker Desktop → Settings → Resources → File Sharing
2. Add your PKG folder (e.g., `/Volumes/incoming/temp`)
3. Rebuild the container
4. Then use normal `--pkg-dir /mnt/rb4dlc` mode

## VS Code Tasks

The project includes pre-configured VS Code tasks for common operations. Press `Ctrl+Shift+P` → "Tasks: Run Task" to access them.

### Opencode Tasks

| Task                            | Description                                             |
| ------------------------------- | ------------------------------------------------------- |
| `Opencode: Resume Last Session` | Resume your previous session (auto-runs on folder open) |
| `Opencode: Launch Fresh`        | Start a new opencode session                            |

### RB4 Scanning Tasks

| Task                                               | Description                                     |
| -------------------------------------------------- | ----------------------------------------------- |
| `RB4: Scan PKGs (test set, fresh)`                 | Scan `pkgs_test/` folder, fresh run             |
| `RB4: Scan PKGs (test set, incremental)`           | Scan `pkgs_test/` folder, skip processed PKGs   |
| `RB4: Scan PKGs (local /pkgs folder, fresh)`       | Scan `/workspace/pkgs`, fresh run               |
| `RB4: Scan PKGs (local /pkgs folder, incremental)` | Scan `/workspace/pkgs`, skip processed PKGs     |
| `RB4: Scan PKGs (network share, fresh)`            | Scan `/mnt/rb4dlc`, fresh run                   |
| `RB4: Scan PKGs (network share, incremental)`      | Scan `/mnt/rb4dlc`, skip processed PKGs         |
| `RB4: Scan PKGs (SMB share via smbclient)`         | Scan SMB share directly, fetch 1 file at a time |
| `RB4: Scan PKGs (SMB share, fresh)`                | Scan SMB share directly, fresh run              |
| `RB4: Scan PKGs (custom path)`                     | Prompt for directory, incremental mode          |
| `RB4: Scan PKGs (custom path, fresh)`              | Prompt for directory, fresh run                 |
| `RB4: Show Mount Status`                           | Display current mount configuration             |
| `RB4: Configure Network Share (help)`              | Show instructions for Docker Desktop setup      |
| `RB4: List available PKG locations`                | Show PKG counts in all locations                |

### SMB Mode (No Kernel Mount Required)

When the container can't mount SMB shares directly (no CAP_SYS_ADMIN), use `--smb` flag:

```bash
python3 RB4/scripts/rb4_songlist_generator.py --smb
```

This uses `smbclient` to:

1. List PKG files from the network share
2. Download one at a time to temp directory
3. Process and extract songs
4. **Immediately delete the PKG to free space**
5. Repeat for next file

This is slower but works without kernel-level SMB mount.

### Quick Start with Tasks

1. **Resume session**: Opens automatically when folder loads
2. **Test scan**: Run `RB4: Scan PKGs (test set, fresh)`
3. **Full scan**: After configuring Docker Desktop file sharing, run `RB4: Scan PKGs (network share, fresh)`

## Debugging / Iterating on Existing Data

When debugging issues (source detection, missing songs, etc.), you don't need to re-extract from PKGs each time. The extraction creates JSON metadata files in `/workspace/rb4_temp/metadata_*.json` that can be reprocessed directly:

```bash
# Re-process all metadata JSON files with fixed logic
cd /workspace && python3 -c "
import json, glob, os

# Your re-processing logic here
# Read from rb4_temp/metadata_*.json
# Write to RB4/rb4_custom_songs.json
"

# Then regenerate song lists
cd /workspace/RB4 && node generate_rb4_song_list.js \
  --baseline /workspace/RB4/rb4songlistWithRivals.txt \
  --custom /workspace/RB4/rb4_custom_songs.json \
  --processed /workspace/RB4/processed_pkgs.json
```

This is much faster than re-extracting from PKGs (which involves SMB download + binary parsing for each file).

## Output Format

Each line in the generated song lists contains:

```
Artist (Album) - Title (Year / Duration) - Source [ShortName]🎸🎸🎤🥁
```

Where:

- `Artist` - Band name
- `Album` - Album name
- `Title` - Song title
- `Year` - Release year
- `Duration` - Length in MM:SS format
- `Source` - Song source (RB4, Rivals, custom, greenday, rb2, etc.)
- `ShortName` - Internal song folder name (for identification)
- `🎸🎸🎤🥁` - Instrument icons (guitar, bass, drums, vocals)

## Generated Files

The pipeline generates 4 text files in `RB4/output/`:

- `SongListSortedByArtist.txt` - Sorted by artist name
- `SongListSortedBySongName.txt` - Sorted by song title
- `SongListSortedByArtistClean.txt` - Profanity filtered (artist sort)
- `SongListSortedBySongNameClean.txt` - Profanity filtered (song sort)

## Binary Structure (.songdta_ps4)

The `.songdta_ps4` files contain compiled song metadata using a fixed binary structure documented in LibForge's 010 Editor template.

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

The `song_length` field at offset 880 contains garbage in some files. Duration is calculated by finding the minimum float value in range 60-500 seconds across the entire file, with fallbacks for truncated WIP files.

## Incremental Mode

The pipeline tracks which PKGs have been processed in `processed_pkgs.json`. On subsequent runs:

- Already-processed PKGs are automatically skipped
- Only new PKGs are extracted
- Existing song data is preserved and merged

To force a full re-extraction:

```bash
python3 RB4/scripts/rb4_extract_songs.py --no-incremental
```

## Architecture

- `rb4_extract_songs.py` - Main orchestration script (end-to-end pipeline)
- `extract_binary_dta.py` - Binary parser for .songdta_ps4 files
- `generate_rb4_song_list.js` - JSON to text list converter
- `rb4songlistWithRivals.txt` - Baseline RB4 + Rivals songs

## Dependencies

Runs in the Devcontainer (Ubuntu 24.04) with:

- Python 3 - for extraction scripts
- Node.js 22 - for generator
- .NET 8 Runtime - for PkgTool
- smbclient - for network share access (optional)
- PkgTool.Core - for PKG/PFS extraction

## References

- LibForge (mtolly/LibForge) - https://github.com/mtolly/LibForge
- Rock Band Wiki - https://rockband.fandom.com
- Onyx (mtolly/onyx) - https://github.com/mtolly/onyx
