# RB4 Research Scripts Catalog

This folder contains 91 Python scripts used for extracting song metadata from Rock Band 4 PKG files.

## Main Categories

### 1. PKG Extraction & Structure Analysis

| Script | Purpose |
|--------|---------|
| `explore_pkg_structure.py` | List PKG contents without full extraction. Scans for `.ark` and `.sng` signatures inside PKG files. |
| `scan_single_dlc_pkg.py` | Scans a single DLC PKG file for song IDs by searching for `RBSongMetadata` markers. Uses heuristic filtering to avoid false positives from asset names. |
| `scan_dlc_pkgs.py` | Batch version - scans multiple DLC PKG files and extracts unique song IDs. Filters out known asset prefixes (crowd_, light_, etc.). |
| `fix_pkg_names.py` | Attempts to fix PKG names for proper identification. |

### 2. ARK File Analysis

| Script | Purpose |
|--------|---------|
| `count_metadata.py` | Counts `RBSongMetadata` entries in ARK files to estimate song counts. |
| `check_ark_versions.py` | Checks ARK file versions to understand format differences. |
| `extract_short_names.py` | Extracts short song names from ARK files using regex pattern `short_name\x00([a-zA-Z0-9_]+)\x00`. |
| `extract_short_names_v2.py` | Improved version of short name extraction. |
| `scan_ark_song_ids.py` | General purpose ARK file song ID scanner. |
| `scan_ark_metadata_v3.py` | Advanced ARK metadata extraction (v3). |
| `scan_single_ark.py` | Scans a single ARK file for metadata. |
| `scan_single_ark_v2.py` | Version 2 of single ARK scanner. |
| `parse_ark_simple.py` | Simple ARK file parser. |

### 3. Song ID Extraction

| Script | Purpose |
|--------|---------|
| `find_song_ids.py` | General purpose song ID finder using regex patterns. |
| `find_new_ids.py` | Finds new/unknown song IDs not in known database. |
| `find_candidates_v2.py` | Version 2 - finds candidate song IDs with higher confidence. |
| `find_high_conf_ids.py` | Finds high-confidence song ID matches. |
| `find_truly_new_ids.py` | Identifies truly new songs not in any database. |
| `find_truly_new_ids_v2.py` | Version 2 of new ID finder. |
| `find_potential_ids.py` | Finds potential song IDs using various heuristics. |
| `find_potential_ids_batch.py` | Batch version of potential ID finder. |
| `locate_ids_pattern.py` | Uses pattern matching to locate song IDs. |
| `locate_ids_mmap.py` | Memory-mapped file version for faster searching. |
| `locate_ids_fixed_pattern.py` | Fixed pattern location finder. |
| `locate_known_ids.py` | Locates known song IDs in files. |
| `extract_loaded_ids.py` | Extracts IDs that were previously loaded. |
| `extract_loaded_ids_v2.py` | Version 2. |
| `extract_loaded_ids_v3.py` | Version 3. |
| `get_ids.py` | General ID extraction utility. |
| `get_offsets.py` | Gets file offsets for IDs. |

### 4. Metadata Recovery

| Script | Purpose |
|--------|---------|
| `recover_metadata.py` | Recovers metadata from binary files. |
| `recover_metadata_batch.py` | Batch metadata recovery. |
| `recover_metadata_mmap_batch.py` | Memory-mapped batch recovery. |
| `recover_metadata_v2.py` | Version 2 of metadata recovery. |
| `recover_ids_final.py` | Final recovery of song IDs. |
| `recover_ids_from_markers.py` | Uses markers to recover IDs. |
| `recover_ids_v2.py` | Version 2 of ID recovery. |
| `resolve_song_metadata.py` | Resolves and completes song metadata. |

### 5. Filtering & Processing

| Script | Purpose |
|--------|---------|
| `filter_song_ids.py` | Filters extracted song IDs to remove false positives. |
| `filter_all_strings.py` | Filters all strings from binary files. |
| `filter_game_params.py` | Filters game parameters. |
| `filter_new_ids.py` | Filters to find only new IDs. |
| `final_filter.py` | Final filtering pass. |
| `expand_known_ids.py` | Expands known ID database. |
| `mark_genre_ids.py` | Marks genre information for IDs. |
| `validate_and_extract_ids.py` | Validates and extracts IDs. |
| `validate_and_extract_paths.py` | Validates file paths. |

### 6. Batch Scanning

| Script | Purpose |
|--------|---------|
| `batch_scan_dlc.py` | Scans all DLC PKG files in batch. |
| `run_all_scans.py` | Runs all available scan methods. |
| `run_batch_scans.py` | Runs multiple scans in batch. |
| `run_scans_resumable.py` | Resumable batch scanning. |
| `scan_all_arks.py` | Scans all ARK files. |
| `scan_refined.py` | Refined scanning approach. |
| `scan_candidates.py` | Scans for candidate songs. |
| `small_dlc_scan.py` | Scans smaller DLC packages. |
| `scan_metadata.py` | General metadata scanning. |
| `scan_metadata_blocks.py` | Scans metadata in blocks. |

### 7. Debugging & Analysis

| Script | Purpose |
|--------|---------|
| `debug_parse.py` | Debug parsing issues. |
| `debug_parse2.py` | More debug parsing. |
| `debug_lines.py` | Debug line analysis. |
| `debug_lines2.py` | More debug lines. |
| `debug_smb_ls.py` | Debug SMB listing issues. |
| `gen_table_rows.py` | Generate table rows for analysis. |
| `count_metadata_updates.py` | Count metadata update patterns. |
| `update_song_details.py` | Update song detail records. |
| `update_song_details_2.py` | Version 2. |
| `update_song_details_3.py` | Version 3. |
| `update_table_columns.py` | Update table column data. |
| `update_offsets.py` | Update file offsets. |

### 8. Other Utilities

| Script | Purpose |
|--------|---------|
| `ark_decrypter.py` | Decrypts ARK files. |
| `extract_all_strings.py` | Extracts all strings from binary. |
| `extract_base_game.py` | Extracts from base game PKG. |
| `extract_context.py` | Extracts context information. |
| `extract_patch_4_ids.py` | Extracts IDs from patch 4. |
| `manual_fix.py` | Manual fix utilities. |
| `new_parser.py` | New parsing approach. |
| `parse_wiki_songs.py` | Parses Wikipedia song lists. |
| `append_requests.py` | Appends HTTP requests. |
| `test_ark.py` | Test ARK parsing. |

### 9. Shell Scripts

| Script | Purpose |
|--------|---------|
| `download_and_scan_dlc.sh` | Downloads and scans DLC from SMB. |

### 10. Current Investigation (April 2026)

| Script | Purpose | Status |
|--------|---------|--------|
| `test_pkg_extraction.py` | Systematically tests each PKG for empty metadata | CREATED |
| `analyze_songdta_structure.py` | Analyzes .songdta file structure from LibForge | CREATED |
| `investigate_extraction_failure.py` | Investigates why certain songdta files fail to parse | CREATED |

## Key Findings from Previous Research

1. **PKG files contain multiple data types:**
   - `.ark` files - main song data archives
   - `.songdta_ps4` - binary song metadata (main extraction target)
   - `RBSongMetadata` markers - found in binary data
   - `short_name` patterns - embedded in ARK files

2. **Song identification patterns:**
   - Short names: `short_name\x00([a-zA-Z0-9_]+)\x00`
   - Metadata markers: `RBSongMetadata`
   - Asset prefixes to filter: `crowd_`, `light_`, `preset_`, `emote_`, etc.

3. **Expected counts:**
   - RBLEGACYDLCPASS1: ~500 songs (RB1 DLC)
   - RBLEGACYDLCPASS2: ~524 songs (RB2 DLC)
   - RBLEGACYDLCPASS3: ~540 songs (RB3 DLC)
   - RB4 season passes: ~719 songs
   - RBN re-releases: ~168 songs

## April 2026 Investigation Findings

### Critical Discovery
- **462 songs from `rb4_empty_songs_full.json` were NOT being extracted**
- These songs exist in PKGs but `.songdta_ps4` files returned empty metadata
- The baseline file has correct metadata but wasn't being used to ADD missing songs

### Solution Implemented
- Reconstructed 462 missing songs from baseline
- Added `inferred=True` flag to mark reconstructed songs
- Updated `rb4_custom_songs.json` with all 4167 songs

### Remaining Gap
- 462 unique songs still missing from PS4 count (4084)
- These are likely: base game disc songs (~65), Rivals expansion (~34), export packs (~363)

---
*Last updated: April 23, 2026*
