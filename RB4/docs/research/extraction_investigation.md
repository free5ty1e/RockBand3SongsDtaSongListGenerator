# RB4 Extraction Investigation - Finding Missing Songs

## CRITICAL FINDING: What is the 4084 count?

The PS4 displays 4084 songs because it counts song CONTENT, not just DLC packages. The total INCLUDES:

1. **DLC Package Songs** (what we extracted) - ~3705 songs from 98 PKGs
2. **Export Packs** (separate purchases) - require owning original games:
   - Rock Band 1 Export - 47 songs (if exported from RB3)
   - Rock Band 2 Export - ~60 songs
   - Rock Band 3 Export - ~84 songs  
   - Lego Rock Band Export - ~45 songs
   - Green Day: Rock Band Export - ~20 songs
   - Rock Band Blitz - ~25 songs
   - Track Packs: AC/DC, Vol 2, Vol 3, Metal, Country 1/2 - ~150+ songs
3. **Base Game v2.21 Songs** - possibly added in update

The export packs were NOT included in our 98 PKG extraction - they're separate content that must be downloaded from PSN if user owns original disc exports.

## Current Status (Updated April 23, 2026)

### What We Extracted vs What PS4 Counts

| Source | Our Extraction | PS4 Total Count |
|--------|---------------|----------------|
| DLC Packages | 3705 (3627 unique) | ~3705 |
| Export Packs | 0 | ~400+ |
| Base Game | 0 | ~50-100 |
| **Total** | **3627** | **4084** |

### Game PKG Extraction Attempts

| Package | Result |
|---------|--------|
| Rivals Expansion Pack (1 MB) | Invalid PFS format - cannot extract |
| v1.00 (3.7 GB) | Extracted to ARK archives - no .songdta files found |
| v2.21 (11.2 GB) | NOT YET ATTEMPTED |

### RB4 Deluxe Mod Research

- RB4DX mod website: https://rb4dx.milohax.org/
- LibForge: https://github.com/mtolly/LibForge - documents file formats
- The game PKGs use ARK archives, not .songdta files

### Conclusion

The 372+ (actually 457) song gap is likely the export packs + base game songs, NOT a "different counting method".
The PS4 shows EVERYTHING available to the user account including export packs.

## CRITICAL DISCOVERY: 89 Baseline Songs Missing!

**89 out of 99 baseline songs are MISSING from our extraction!**

These are the RB4 base game + Rivals songs that were NOT released as separate DLC. They must come from the game PKG (v1.00 or v2.21).

### Baseline Analysis

- Total baseline songs: 99 (from rb4songlistWithRivals.txt)
- Found in extraction: 10 (released as DLC)
- Missing: 89 (base game / Rivals only, NOT in DLC)

### Missing Songs List

See `/workspace/RB4/missing_baseline_songs.txt` for the complete list of 89 missing songs.

These songs are from:
- RB4 v1.00 disc: ~65 songs
- Rivals expansion: ~34 songs

They are NOT in the 98 DLC PKGs - they can only be extracted from the game PKG (v2.21).

| gameOrigin | Label | Count | Notes |
|------------|-------|-------|-------|-------|
| rb1_dlc | RB1 DLC | 896 | Includes base game songs mis-mapped |
| ugc_plus | Custom | 779 | |
| rb4_dlc | RB4 DLC | 638 | |
| (empty→inferred) | Unknown | 377 | |
| rb3_dlc | RB3 DLC | 467 | |
| legacy_rbn | RBN1 | 166 | |
| rb2 | RB2 | 72 | |
| rb3 | RB3 | 72 | |
| rb1 | RB1 | 49 | |
| greenday | Green Day | 44 | |
| lego | LEGO | 43 | |
| rb2_dlc | RB2 DLC | 11 | From UNEXPORTABLEPORT |
| DOWNLOADED | Downloaded | 7 | |
| ugc | UGC | 1 | |

### Definitive Math

| Metric | Count |
|--------|-------|
| Metadata raw entries | 3705 |
| Internal duplicates removed | 82 |
| First occurrence unique artist+title | 3622 |
| + Baseline unique | 90 |
| = **Total unique songs** | **3712** |
| PS4 shows | 4084 |
| **Gap** | **372 songs** |

### Critical Findings

1. **466 empty entries recovered from baseline** - These are songs with empty artist/title in PKGs that were recovered using the shortName-to-baseline lookup.
2. **73 duplicate groups (82 extra occurrences)** - Same artist+title appears in multiple PKGs. First occurrence kept.
3. **Empty shortName entries (465 in JSON)** - 466 empty shortNames in metadata, 465 recovered via baseline. 1 truly empty entry (sextypething) NOT recovered.
4. **gameOrigin mapping issue** - RB1ROCKBAND1PASS has mixed origins (rb1, rb3_dlc, empty) from binary data. Source field uses PKG filename fallback correctly.

## Full Re-Extraction Results (April 22, 2026)

Completed full re-extraction from all 98 SMB PKGs:
- RB4PRESEASONPASS: 230 songs
- RB4RBNRERELEASES: 168 songs
- RB4SEASON01TOS10: 125 songs
- RB4SEASON11TOS20: 102 songs
- RB4SEASON21TOS30: 188 songs
- RB4SEASON31TOS35: 74 songs
- RBLEGACYDLCPASS1: 500 songs
- RBLEGACYDLCPASS2: 524 songs
- RBLEGACYDLCPASS3: 540 songs
- RB1ROCKBAND1PASS: 55 songs
- RB2ROCKBAND2PASS: 81 songs
- RB3ROCKBAND3PASS: 83 songs
- CREQ packages: 638 songs total
- Other individual PKGs: ~200 songs

New extraction removed 1 garbage entry → 3626 final songs.

## CRITICAL FINDING: 17 baseline songs NOT in extraction

The baseline (rb4songlistWithRivals.txt) has 99 songs from RB4 v1.00 + Rivals. Only 82 of these overlap with our extraction - **17 baseline songs are NOT in our 3705 extraction**.

This means:
- Baseline: 99 songs (from BASE GAME, NOT in DLC PKGs)
- Our extraction: 3705 songs (from DLC PKGs)
- Duplicates: 82 songs appear in both
- Unique total: 3705 + 99 - 82 = **3722 unique songs**

But PS4 shows **4084** - so there are still **362 songs** truly missing from our DLC extraction.

The DLC PKGs should contain ~3712 songs but we only extracted 3705. The 7-song gap in DLC + 355 more songs (from other sources) = 362 missing.

## Key Question: Why are we missing songs from the DLC PKGs?

Possible reasons:
1. PKG extraction is skipping some .songdta_ps4 files
2. Some .songdta_ps4 files have corrupted metadata
3. The extraction offsets are wrong for certain PKG types
4. Some songs are in a different file format inside PKGs

## Investigation Steps

### Step 1: Download a complete DLC PKG for analysis
- [ ] Download RBLEGACYDLCPASS3 (RB3 DLC) from SMB
- [ ] Extract all files from the PKG
- [ ] Find ALL song metadata files (.songdta_ps4, .ark, etc.)

### Step 2: Analyze PKG contents
- [ ] List all files in the extracted PKG
- [ ] Identify all file types containing song data
- [ ] Check if there are multiple songdta formats

### Step 3: Test extraction on single PKG
- [ ] Modify pipeline to extract from one PKG
- [ ] Compare extracted count vs expected
- [ ] Find what's being skipped

### Step 4: Fix and iterate
- [ ] Implement fixes in extract_binary_dta.py
- [ ] Test on single PKG
- [ ] Apply to all PKGs

## Key PKGs to Analyze

| PKG | Expected Songs | Our Extraction |
|-----|---------------|-----------------|
| RBLEGACYDLCPASS3 | ~540 | 540 |
| RBLEGACYDLCPASS2 | ~524 | 524 |
| RBLEGACYDLCPASS1 | ~500 | 500 |
| RB4SEASON01-35 | ~719 | 719 |

## Analysis Findings

### RB4 DLC Breakdown
- **RB4 Season Pass songs**: 719 extracted
- **Source field**: 625 marked as "Rock Band 4 DLC", 156 marked as "Custom"
- **Custom from RB4 packages**: 156 songs

### CREQ Packages (Custom Requests)
- 18 PKGs with "CREQ" in name
- Contains 638 songs total
- These are custom/requested songs, NOT official DLC

### Gap Analysis
## CRITICAL: Legacy DLC Pack Mis-categorization

The RBLEGACYDLCPASS1/2/3 packages are COMBINED packs, not separate RB1/RB2/RB3 DLC:
- PASS1: 500 songs (mix of RB1-3 era DLC)
- PASS2: 524 songs 
- PASS3: 540 songs
- Total: 1564 songs

Expected Wikipedia: RB1 DLC (893) + RB2 DLC (84) + RB3 DLC (588) = 1565

Current mapping assigns them as separate RB1/RB2/RB3 DLC, which is WRONG. These are legacy DLC re-released for RB4.

## Gap Summary

Our extraction is missing songs in these categories:
| Category | Expected | Our Count | Gap |
|----------|----------|-----------|-----|
| RB2 DLC | 84 | 0 | -84 |
| RB3 DLC | 588 | 463 | -125 |
| RB4 DLC | 800 | 625 | -175 |
| RBN | 184 | 155 | -29 |
| RB1-3 disc | 269 | 199 | -70 |
| Green Day | 44 | 41 | -3 |
| LEGO | 42 | 40 | -2 |
| **TOTAL DLC GAP** | | | **~488** |

But 1564/1565 of RB1-3 DLC is present in LEGACY packs.

## Investigation Plan

1. [x] Catalog research scripts ✅
2. [x] Download and analyze a full DLC PKG to see raw structure
3. [x] PKG files use custom format - can't extract with 7z, requires PkgTool ✅
4. [ ] Check extraction logs to see how many .songdta files were found
5. [ ] Compare .songdta count vs extracted song count

## Key Findings

1. **PKG files are encrypted/custom format** - can't be opened with standard tools (7z, etc)
2. **PkgTool required** for extraction but has issues
3. **We have 101 metadata files** from 98 PKGs (+ some extra sources)
4. **3705 songs extracted** from PKGs

## Next Steps

1. [ ] Check the original extraction logs to see how many .songdta files were found per PKG
2. [ ] Compare that to the song count in each metadata file
3. [ ] If counts don't match, the extraction may have skipped some files
4. [ ] Need to re-extract from SMB PKGs to verify

## Extraction Log Analysis

From logs, the pipeline finds .songdta_ps4 files inside each PKG:
- Example: BADFINGER0000001.pkg → Found 1 .songdta_ps4 file → Extracted 1 song
- Example: NINTENDO00000001.pkg → Expected to have 2 songs

The metadata files we have ARE being generated correctly.

## The Real Question

We have 3705 songs from 101 metadata files (from 98 PKGs). PS4 shows 4084.
The gap is **379 songs**.

Where are the missing songs coming from? Options:
1. Some PKGs have MORE .songdta files than we extracted
2. Some songs are in a different format inside PKGs
3. The game PKGs contain songs not in DLC PKGs
4. PS4 is counting something differently

## Data Quality Analysis

From metadata files:
- Total songs: 3705
- With valid artist+title: 3239 (87%)
- With missing data: 466 (inferred from baseline)
- Songs with 'inferred' field: 470

The baseline fallback IS working - 470 songs that were missing data are being filled in from the empty songs baseline.

## Action Items

1. [ ] Re-extract from SMB PKGs to verify count
2. [ ] Check extraction logs for .songdta file count per PKG
3. [ ] Compare extracted count vs expected (from Wikipedia)

## SMB Connection Method
| RB4RBNRERELEASES | ~168 | 168 |

## What We've Tried

1. ✅ Source mapping - maps PKG filenames to official sources
2. ✅ Baseline fallback - fills in missing artist/title from baseline
3. ✅ SMB listing - confirmed 98 PKGs exist
4. ✅ Created research scripts catalog (`/workspace/RB4/scripts/research/README.md`)

## Research Scripts Available

See `/workspace/RB4/scripts/research/README.md` for full catalog.

Key scripts for PKG analysis:
- `scan_single_dlc_pkg.py` - Scans PKG for RBSongMetadata markers
- `count_metadata.py` - Counts RBSongMetadata in ARK files
- `extract_short_names.py` - Extracts short names via `short_name\x00pattern`
- `scan_dlc_pkgs.py` - Batch PKG scanning

## What's Missing

The 372 gap likely includes:
- Songs in base game/update PKGs not extracted
- Songs with alternative metadata formats
- Songs counted differently by PS4

## SMB Connection Method

**CORRECT SMB CONNECTION:**
```
Share name: incoming (NOT incoming/temp/Rb4Dlc)
Connect to: //192.168.100.135/incoming
Then cd to: temp/Rb4Dlc
Example: smbclient "//192.168.100.135/incoming" -N -c "cd temp/Rb4Dlc; ls"
```

**WRONG (doesn't work):**
```
//192.168.100.135/incoming/temp/Rb4Dlc
```

## File Locations

- **DLC PKGs**: `//192.168.100.135/incoming/temp/Rb4Dlc` (98 files)
- **Game PKGs**: `//192.168.100.135/incoming/temp/rb4gamepkgs`
- **PS4 FTP**: `ftp://192.168.100.117:2121` (port 2121, read-only)

---
*Created: April 21, 2026*
