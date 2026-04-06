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

## Network Share / SMB Mount

The devcontainer automatically attempts to mount your RB4 DLC share on startup. The mount script (`mount_rb4_dlc.sh`) runs in `postCreateCommand` and:

1. **First** checks if a bind mount already exists (from devcontainer.json)
2. Then checks for custom config (`.devcontainer/rb4_dlc_config.sh` - gitignored)
3. Then tries SMB mount (cifs, smbfs, various SMB versions)
4. Falls back to local `$HOME/RB4Dlc`
5. **Fails gracefully** with helpful message if nothing works

### Option 1: Docker Desktop File Sharing (Recommended)

This enables automatic bind mounting when the container starts:

1. Open Docker Desktop → Settings → Resources → File Sharing
2. Add the folder containing your PKGs (e.g., `/Volumes/incoming/temp`)
3. Rebuild the devcontainer
4. The bind mount at `/mnt/rb4dlc` will work automatically

This is the easiest option - once configured, no further action needed.

### Option 2: Custom SMB Server

Create a gitignored config file at `.devcontainer/rb4_dlc_config.sh`:

```bash
# .devcontainer/rb4_dlc_config.sh
SMB_SHARE="//192.168.1.100/YourShareName"
MOUNT_POINT="/mnt/your-custom-path"
```

This allows each user to specify their own mount location without modifying the repo.

### Option 3: Manual Mount

If auto-mount fails, you can manually mount:

```bash
sudo mount -t cifs //192.168.100.135/incoming/temp/Rb4Dlc /mnt/rb4dlc -o guest
python3 RB4/scripts/rb4_songlist_generator.py --pkg-dir /mnt/rb4dlc
```

### Checking Mount Status

Run `RB4: Show Mount Status` task or:

```bash
bash .devcontainer/mount_rb4_dlc.sh
```

This will tell you what's mounted and what configuration options are available.

## VS Code Tasks

The project includes pre-configured VS Code tasks for common operations. Press `Ctrl+Shift+P` → "Tasks: Run Task" to access them.

### Opencode Tasks

| Task                            | Description                                             |
| ------------------------------- | ------------------------------------------------------- |
| `Opencode: Resume Last Session` | Resume your previous session (auto-runs on folder open) |
| `Opencode: Launch Fresh`        | Start a new opencode session                            |

### RB4 Scanning Tasks

| Task                                               | Description                                   |
| -------------------------------------------------- | --------------------------------------------- |
| `RB4: Scan PKGs (test set, fresh)`                 | Scan `pkgs_test/` folder, fresh run           |
| `RB4: Scan PKGs (test set, incremental)`           | Scan `pkgs_test/` folder, skip processed PKGs |
| `RB4: Scan PKGs (local /pkgs folder, fresh)`       | Scan `/workspace/pkgs`, fresh run             |
| `RB4: Scan PKGs (local /pkgs folder, incremental)` | Scan `/workspace/pkgs`, skip processed PKGs   |
| `RB4: Scan PKGs (network share, fresh)`            | Scan `/mnt/rb4dlc`, fresh run                 |
| `RB4: Scan PKGs (network share, incremental)`      | Scan `/mnt/rb4dlc`, skip processed PKGs       |
| `RB4: Scan PKGs (custom path)`                     | Prompt for directory, incremental mode        |
| `RB4: Scan PKGs (custom path, fresh)`              | Prompt for directory, fresh run               |
| `RB4: Show Mount Status`                           | Display current mount configuration           |
| `RB4: Configure Network Share (help)`              | Show instructions for Docker Desktop setup    |
| `RB4: List available PKG locations`                | Show PKG counts in all locations              |

### Quick Start with Tasks

1. **Resume session**: Opens automatically when folder loads
2. **Test scan**: Run `RB4: Scan PKGs (test set, fresh)`
3. **Full scan**: After configuring Docker Desktop file sharing, run `RB4: Scan PKGs (network share, fresh)`

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
