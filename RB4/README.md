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

1. **First** checks for custom config (`.devcontainer/rb4_dlc_config.sh` - gitignored)
2. Then tries SMB mount (cifs, smbfs, various SMB versions)
3. Falls back to macOS bind mount (`/Volumes/incoming/temp/Rb4Dlc`)
4. Falls back to local `$HOME/RB4Dlc`
5. **Fails gracefully** with helpful message if nothing works

### Custom Mount Location

Create a gitignored config file at `.devcontainer/rb4_dlc_config.sh`:

```bash
# .devcontainer/rb4_dlc_config.sh
SMB_SHARE="//192.168.1.100/YourShareName"
MOUNT_POINT="/mnt/your-custom-path"
```

This allows each user to specify their own mount location without modifying the repo.

### Manual Mount

If auto-mount fails, you can manually mount:

```bash
sudo mount -t cifs //192.168.100.135/incoming/temp/Rb4Dlc /mnt/rb4dlc -o guest
python3 RB4/scripts/rb4_songlist_generator.py --pkg-dir /mnt/rb4dlc
```

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
