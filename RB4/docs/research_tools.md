# Research Tools Index

This document lists the utility scripts developed during the investigation of Rock Band 4 file formats, specifically targeting the recovery of missing song metadata from `.ark` archives.

## Script Catalog

| Script                           | Purpose                                                             | Status   |
| :------------------------------- | :------------------------------------------------------------------ | :------- |
| `test_ark.py`                    | Initial tests for `ark_extract.py` functionality.                   | Legacy   |
| `find_metadata.py`               | Scans `.ark` files for the `RBSongMetadata` binary marker.          | Utility  |
| `count_metadata.py`              | Counts occurrences of `RBSongMetadata` in base game archives.       | Utility  |
| `get_offsets.py`                 | Extracts specific byte offsets of `RBSongMetadata` markers.         | Utility  |
| `check_ark_versions.py`          | Identifies the version header of various `.ark` files.              | Utility  |
| `scan_metadata.py`               | Extracts binary chunks surrounding `RBSongMetadata` markers.        | Utility  |
| `extract_short_names.py`         | Attempts to extract `short_name` identifiers using regex.           | Legacy   |
| `extract_short_names_v2.py`      | Refined extraction of `short_name` with overlap handling.           | Legacy   |
| `find_new_ids.py`                | Identifies IDs in `.ark` files not present in the baseline JSON.    | Utility  |
| `scan_candidates.py`             | Heuristic search for song-like strings near metadata markers.       | Utility  |
| `scan_single_ark.py`             | Wrapper to scan a single archive for candidates.                    | Utility  |
| `filter_new_ids.py`              | Filters raw candidates against known ID lists.                      | Utility  |
| `recover_metadata.py`            | Attempts to associate Artist/Title strings with discovered IDs.     | Utility  |
| `recover_metadata_v2.py`         | Refined metadata recovery using memory mapping.                     | Utility  |
| `recover_metadata_batch.py`      | Processes metadata recovery in batches to prevent timeouts.         | Utility  |
| `recover_metadata_mmap_batch.py` | High-performance batch recovery using `mmap`.                       | Utility  |
| `find_potential_ids.py`          | Broad scan for any lowercase alphanumeric strings with underscores. | Utility  |
| `find_potential_ids_batch.py`    | Batch version of potential ID scanning.                             | Utility  |
| `filter_all_strings.py`          | Filters all extracted strings against baseline and blacklist.       | Utility  |
| `find_high_conf_ids.py`          | Extracts IDs found specifically within `RBSongMetadata` blocks.     | Utility  |
| `filter_song_ids.py`             | Final filtration of candidates based on song ID heuristics.         | Utility  |
| `final_filter.py`                | Last-pass filter to produce the `truly_new_ids.txt` list.           | Utility  |
| `final_recovery.py`              | Final attempt to recover metadata for all new IDs.                  | Utility  |
| `final_recovery_mmap.py`         | mmap-accelerated final recovery attempt.                            | Utility  |
| `locate_known_ids.py`            | Verifies the presence of known baseline IDs in `.ark` files.        | Utility  |
| `locate_ids_pattern.py`          | Tests the `[length][null][string]` pattern for IDs.                 | Research |
| `locate_ids_mmap.py`             | mmap-accelerated pattern search for known IDs.                      | Research |
| `locate_ids_fixed_pattern.py`    | Tests the `[length][string]` pattern (without null).                | Research |
| `recover_ids_from_markers.py`    | Extracts the first valid string following `RBSongMetadata`.         | Research |
| `recover_ids_v2.py`              | Refined recovery of IDs from markers with a blacklist.              | Research |
| `scan_ark_song_ids.py`           | Implements the `[length][string]` pattern scan near markers.        | Research |
| `validate_ark_songs.py`          | Cross-references discovered IDs against known song lists.           | Utility  |
| `extract_loaded_ids.py`          | Specifically targets the `loaded_song_id` key.                      | Research |
| `extract_loaded_ids_v2.py`       | Refined `loaded_song_id` extraction.                                | Research |
| `extract_loaded_ids_v3.py`       | Block-length based extraction for `loaded_song_id`.                 | Research |
| `scan_metadata_blocks.py`        | Dumps all strings found near metadata markers for analysis.         | Research |
| `extract_all_strings.py`         | Extracts every alphanumeric string from all archives.               | Utility  |
| `find_candidates_v2.py`          | Iterative candidate search with an expanded blacklist.              | Research |
| `filter_all_strings.py`          | Filter for the global string dump.                                  | Utility  |
| `extract_base_game.py`           | Utility for extracting base game files.                             | Utility  |
| `extract_binary_dta.py`          | Binary parser for `.songdta` files.                                 | Core     |
