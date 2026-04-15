# Rock Band 4 Custom Song List Generator

This folder contains a pipeline for scanning PS4 (fPKG) Rock Band 4 custom song packages, extracting metadata from compiled `.songdta_ps4` binary blobs, and generating a human-readable song list.

## Requirements

- Python 3.x
- .NET 8 (for PkgTool)
- Node.js (for song list generation)
- Optional: smbclient (for network share access)

## Running the Pipeline

**IMPORTANT:** Run scripts from the `RB4` folder for relative paths to work:

```bash
cd RB4
python3 scripts/rb4_songlist_generator.py --pkg-dir /path/to/pkgs
```

Or with default paths:

```bash
cd RB4
python3 scripts/rb4_songlist_generator.py
```

## Quick Start

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

| Option                     | Default                    | Description                                      |
| --------------------------- | -------------------------- | ------------------------------------------------ |
| `--pkg-dir`                | `pkgs`                     | Directory containing PKG files                   |
| `--temp-dir`               | `rb4_temp`                 | Temporary directory for extraction              |
| `--output-json`            | `rb4_temp/rb4_custom_songs.json` | Output JSON file with extracted metadata    |
| `--metadata-dir`           | `output/PkgMetadataExtracted` | Directory for extracted metadata JSONs       |
| `--songlist-dir`           | `output/`                  | Output directory for song lists                 |
| `--baseline`               | `rb4songlistWithRivals.txt` | Baseline song list file                         |

## How It Works

### Baseline Song Database

The standard `rb4songlistWithRivals.txt` file serves as the baseline database of all default RB4 songs + Rivals expansion tracks. This tool supplements the baseline with your custom songs, dropping duplicates (custom files take precedence).

### Empty Metadata Fallback

Some custom songs have unparseable/empty metadata in their `.songdta_ps4` files. The pipeline uses `rb4_empty_songs_full.json` as a lookup table to recover artist, title, and instruments from the short filename. Songs recovered this way are marked with a "✓" in the Inferred column of the HTML output.

### Output Files

**Text lists (in `output/`):**
- `SongListSortedByArtist.txt` - All songs sorted by artist
- `SongListSortedBySongName.txt` - All songs sorted by title  
- `SongListSortedByArtistClean.txt` - Same as above, with inferred songs flagged
- `SongListSortedBySongNameClean.txt` - Same as above, with inferred songs flagged

**HTML list (in `output/` and `docs/`):**
- `RB4SongList.html` - Interactive HTML with filtering, sorting, 7 themes

The HTML output is auto-copied to `docs/RB4SongList.html` for GitHub Pages deployment.
| `--progress-length`        | `40`                       | Progress bar length in characters               |
| `--reprocess-cached-metadata` | -                       | Skip PKG extraction, reprocess existing metadata |
| `--smb`                    | -                          | Access PKGs via SMB share using smbclient        |
| `--no-incremental`         | -                          | Disable incremental mode - re-process all PKGs   |
| `--incremental`     | enabled                          | Skip already-processed PKGs (default: enabled) |
| `--no-incremental`  | -                                | Disable incremental mode - re-process all PKGs |
| `--smb`             | -                                | Access PKGs via SMB share using smbclient      |
| `--log`             | `temp_dir/rb4_extract_<ts>.log`  | Log file path                                  |
| `-v`, `--verbose`   | -                                | Verbose output                                 |

## Error Logging

The pipeline tracks errors and warnings during execution:

**Error types:**

- `pfs_image_extract_failed` - Step 1: extracting inner PFS image from PKG
- `pfs_contents_extract_failed` - Step 2: extracting PFS contents
- `memory_map_error` - .NET memory mapped file errors (often from large PKGs)
- `pkg_processing_failed` - Generic catch-all for PKG failures
- `songdta_parse_failed` - Failed to parse .songdta_ps4 metadata files

**Warning types:**

- `no_songdta_found` - PKG extracted but no .songdta_ps4 files found
- `empty_metadata` - Song has empty/unparseable metadata
- `unknown_source` - Could not determine song source

**Output files:**

- `/workspace/RB4/pipeline_errors.json` - Full error/warning report in JSON format
- `/workspace/rb4_temp/rb4_extract_<timestamp>.log` - Detailed execution log

Example error report:

```json
{
  "errors": {
    "memory_map_error": [
      { "pkg": "CREQ2604P15MISCS.pkg", "details": "...", "timestamp": "..." }
    ]
  },
  "warnings": {}
}
```

After each run, a summary is printed:

```
📊 Error Report: Errors: 1, Warnings: 0
   Full report saved to: /workspace/RB4/pipeline_errors.json
```

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

When debugging issues (source detection, missing songs, etc.), you don't need to re-extract from PKGs each time. Use the "Reprocess Cached Data" task or run:

```bash
# Regenerate song lists from cached metadata in rb4_temp
cd /workspace/RB4 && node generate_rb4_song_list.js
```

The pipeline stores intermediate files in `/workspace/rb4_temp/`:

- `rb4_custom_songs.json` - extracted song metadata
- `processed_pkgs.json` - PKGs already scanned
- `pipeline_errors.json` - extraction errors/warnings
- `update_history.json` - update history log
- `rb4_extract_*.log` - run logs

**Output files** go to `/workspace/RB4/output/` (committed to repo).

## Output Format

Each line in the generated song lists contains:

**Artist-sorted:**

```
Artist (Album) - Title (Year / Duration) - Source [ShortName] 🎸🎤🥁
```

**Name-sorted:**

```
Title by Artist on Album (Year / Duration) - Source [ShortName] 🎸🎤🥁
```

Where:

- `Artist` - Band name
- `Album` - Album name
- `Title` - Song title
- `Year` - Release year
- `Duration` - Length in MM:SS format
- `Source` - Song source (RB4, Rivals, custom, greenday, rb2, etc.)
- `ShortName` - Internal song folder name (for identification)
- `🎸🎤🥁🎹` - Instrument icons (guitar, bass, drums, vocals, keys)

## Song List Generator Options

The `generate_rb4_song_list.js` script can also be run standalone:

```bash
cd /workspace/RB4 && node generate_rb4_song_list.js \
  --baseline <file> \
  --custom <file> \
  --outdir <dir> \
  --processed <file> \
  --allow-duplicates \
  --verbose
```

| Option               | Default                          | Description                           |
| -------------------- | -------------------------------- | ------------------------------------- |
| `--baseline`         | `rb4songlistWithRivals.txt`      | Baseline RB4/Rivals song list file    |
| `--custom`           | `rb4_temp/rb4_custom_songs.json` | Custom songs JSON file                |
| `--outdir`           | `output/`                        | Output directory for generated lists  |
| `--processed`        | `rb4_temp/processed_pkgs.json`   | Processed PKGs JSON file              |
| `--timezone`         | /etc/timezone                    | Timezone for timestamps               |
| `--allow-duplicates` | disabled                         | Allow duplicate songs (for debugging) |
| `-v`, `--verbose`    | disabled                         | Verbose output                        |
| `-h`, `--help`       | -                                | Show help                             |

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
python3 RB4/scripts/rb4_songlist_generator.py --no-incremental
```

## Architecture

- `rb4_songlist_generator.py` - Main orchestration script (end-to-end pipeline)
- `extract_binary_dta.py` - Binary parser for .songdta_ps4 files
- `generate_rb4_song_list.js` - JSON to text list converter
- `backup_rb4_run.sh` - Backup script for archiving intermediate files
- `rb4songlistWithRivals.txt` - Baseline RB4 + Rivals songs (source of truth)

## VS Code Tasks ( rb4-reprocess group)

| Task                         | Description                                  |
| ---------------------------- | -------------------------------------------- |
| `RB4: Reprocess Cached Data` | Regenerate song lists from cached metadata   |
| `RB4: Backup Previous Run`   | Archive intermediate files to timestamped 7z |
| `RB4: Restore Backup`        | Restore from most recent backup 7z file      |

### Backup Script

Run manually:

```bash
bash RB4/scripts/backup_rb4_run.sh
```

This archives to `/workspace/rb4_temp/rb4_backup_YYYYMMDD_HHMMSS.7z`:

- Output song lists (`SongListSortedBy*.txt`)
- Intermediate files from `rb4_temp/`
- Most recent run log (`rb4_extract_*.log`)

## Dependencies

Runs in the Devcontainer (Ubuntu 24.04) with:

- Python 3 - for extraction scripts
- Node.js 22 - for generator
- .NET 8 Runtime - for PkgTool
- smbclient - for network share access (optional)
- PkgTool.Core - for PKG/PFS extraction

## HTML Song List

The pipeline generates an interactive HTML song list with filtering, sorting, and theming.

### Generating HTML Directly

```bash
python3 RB4/scripts/generate_html_list.py RB4/output/PkgMetadataExtracted RB4/output/SongList.html
```

### Options

| Option              | Default                          | Description                                    |
| ------------------- | -------------------------------- | ---------------------------------------------- |
| `--title`          | `🎸 Rock Band 4 Song List`       | Custom HTML page title                        |

### Features

- **Search**: Filter by artist, title, album, or shortName
- **Year Range**: Filter by release year (defaults to min/max in data)
- **Duration Range**: Filter by song length in seconds (defaults to min/max in data)
- **Source**: Filter by song source (Custom, DLC, RB4, Rivals, etc.)
- **Instruments**: Filter by instrument availability (guitar, bass, drums, vocals, keys, pro guitar, pro drums, pro keys, harmony_1, harmony_2)
- **Themes**: 7 themes (Dark Blue, Matrix, Cyberpunk, Sunset, Forest, Rose, Monochrome)
- **Sorting**: Click any column header to sort
- **Reset**: Button to clear all filters

### Customization

Customize via `/workspace/.devcontainer/rb4_dlc_config.sh`:

```bash
# HTML page title
HTML_PAGE_TITLE="🎸 Chris's PS4's Rock Band 4 Song List"
```

## References

- LibForge (mtolly/LibForge) - https://github.com/mtolly/LibForge
- Rock Band Wiki - https://rockband.fandom.com
- Onyx (mtolly/onyx) - https://github.com/mtolly/onyx
