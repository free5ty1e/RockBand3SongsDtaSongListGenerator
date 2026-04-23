# RB4 Extraction Debug Investigation

## Theory

Our extraction pipeline from the 98 DLC PKG files is NOT working correctly. Evidence:
1. Songs are being extracted with empty metadata (artist/title = "")
2. We rely on a fallback baseline file (`rb4_empty_songs_full.json`) to recover metadata
3. PS4 shows 4084 songs but we only have ~3705 (~3627 unique)
4. The `rb4songlistWithRivals.txt` baseline has 99 songs that should be in the game, but many show up in our extraction anyway

**Hypothesis**: Any PKG that produces a song with empty metadata represents a FAILURE to extract correctly. The song metadata parsing is stopping early and not getting all songs from that PKG.

**Goal**: Fix the extraction until NO empty metadata songs are produced.

## Open Questions

1. Why does the extraction produce empty metadata? Is it a parsing bug or a data issue?
2. Are there more songs in each PKG that we're not extracting?
3. Can we verify the exact number of songs per PKG from other sources?

## Plan

1. Systematically extract ONE PKG at a time
2. Check each extraction for empty metadata songs
3. Count total songs extracted per PKG
4. Match empty metadata songs against `rb4_empty_songs_full.json`
5. Identify which PKGs fail and document the failure pattern
6. Fix the extraction logic
7. Re-extract failing PKGs with fixes
8. Track all experiments in the table below

## Extraction Experiment Log

| # | PKG Name | Songs Extracted | Empty Metadata | Matched in Fallback | Status |
|---|----------|-----------------|----------------|---------------------|--------|
|   |          |                 |                |                     |        |

## PKG Extraction Details

Will populate as experiments progress...

## Baseline Comparison

The baseline `rb4songlistWithRivals.txt` contains 99 songs from RB4 v1.00 + Rivals.
Need to compare against online sources to verify completeness.

## Progress

[WORKING] - Systematically testing each PKG...