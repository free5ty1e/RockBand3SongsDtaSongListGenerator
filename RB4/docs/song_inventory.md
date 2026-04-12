# RB4 Song Inventory - Complete Tracking

## Current Status (2026-04-11)

### Song Count Summary

| Category | Count | Source |
|----------|-------|--------|
| Rock Band 1 DLC | 893 | PS3-era DLC |
| Rock Band 1 (core) | 51 | Base game |
| Rock Band 2 (core) | 75 | Base game |
| Rock Band 3 (core) | 73 | Base game |
| Rock Band 3 DLC | 463 | PS3-era DLC |
| Rock Band 4 DLC | 623 | PS4-era DLC |
| Rock Band Network 1 | 155 | Xbox 360 community songs |
| Rock Band Green Day | 41 | Green Day export |
| LEGO Rock Band | 40 | LEGO bundle |
| Custom (UGC+) | 1,279 | Custom songs (various sources) |
| **TOTAL FROM PKGs** | **3,793** | |
| Baseline (rb4songlistWithRivals) | 98 | Official RB4 Rivals |
| **COMBINED TOTAL** | **3,183** | Unique from PKGs |
| **PS4 Target** | **4,084** | Expected total |
| **GAP** | **901** | Missing songs |

---

## Executive Summary

We have extracted **3,183 unique songs** from PKGs. The PS4 shows **4,084 songs** - a gap of **901 songs**.

### What's Accounted For (3,183 songs)
- Official DLC from all passes: ~2,800 songs
- Custom/UGC songs: ~1,279 (some overlap with DLC counts)
- Export content: ~240 songs

### The Gap (901 songs) Likely Includes:
1. **Base game songs** - Not yet extracted from Rock.Band.4 PKGs (3.7GB + 11GB)
2. **Additional custom songs** - Not in our current extraction
3. **Rivals expansion** - 26 songs
4. **Unreleased/delisted content** - Content that was removed

---

## Detailed PKG Breakdown

### Top 30 PKGs by Song Count

| Songs | Custom | RB1 | RB4 | PKG Name |
|-------|--------|-----|-----|----------|
| 540 | 82 | 0 | 0 | RBLEGACYDLCPASS3 |
| 524 | 72 | 452 | 0 | RBLEGACYDLCPASS2 |
| 500 | 60 | 440 | 0 | RBLEGACYDLCPASS1 |
| 230 | 29 | 0 | 201 | RB4PRESEASONPASS |
| 188 | 34 | 0 | 154 | RB4SEASON21TOS30 |
| 186 | 186 | 0 | 0 | CREQ2604P18FIXED |
| 168 | 13 | 0 | 0 | RB4RBNRERELEASES |
| 125 | 11 | 0 | 114 | RB4SEASON01TOS10 |
| 120 | 119 | 0 | 0 | CREQ2604P15MISCS |
| 102 | 15 | 0 | 87 | RB4SEASON11TOS20 |
| 83 | 10 | 0 | 0 | RB3ROCKBAND3PASS |
| 81 | 11 | 0 | 0 | RB2ROCKBAND2PASS |
| 79 | 79 | 0 | 0 | CREQ2604P17WRDAL |
| 74 | 13 | 0 | 61 | RB4SEASON31TOS35 |
| 62 | 62 | 0 | 0 | CREQ2604P03AVRIL |

## Custom Song Analysis (1,279 songs)

### By gameOrigin

| gameOrigin | Count | Notes |
|------------|-------|-------|
| ugc_plus | 804 | Rock Band 4 custom songs |
| (empty) | 465 | Songs with no gameOrigin (fallback/inferred) |
| DOWNLOADED | 9 | Pre-installed content (The Strokes) |
| ugc | 1 | Legacy UGC |

### Notable Albums in Custom Songs

| Count | Album |
|-------|-------|
| 40 | Hamilton (Original Broadway Cast Recording) |
| 20 | One Night Only (Live) |
| 15 | Goodbye Lullaby (Avril Lavigne) |
| 14 | The Best Damn Thing (Avril Lavigne) |
| 12 | Let Go (Avril Lavigne) |
| 11 | Love Sux (Avril Lavigne) |

### Songs with Empty Metadata (Fallback)

- 465 songs have no artist/title in raw metadata
- 464 matched to baseline (empty_songs.json fallback)
- These are inferred from shortName pattern matching

## What's Missing? Hypotheses

### 1. Base Game Content (RB1/RB2/RB3 Ports)
- RB4 includes songs ported from RB1/RB2/RB3 base games
- These may be in base game PKGs, not DLC PKGs
- Need to check base game update PKGs

### 2. Rivals Expansion (26 songs)
- Rock Band 4 Rivals expansion had 26 additional songs
- Some may not be in separate PKG

### 3. Game Update Content
- Songs added via game patches, not DLC
- Check update PKGs: `Rock.Band.4_CUSA02084_v2.21`

### 4. Unreleased DLC
- Some songs prepared but never released
- Check RB4DLCUNRELEASED PKG

### 5. Delisted Content
- Songs that were delisted and removed

## Known PKGs to Verify

| Expected Songs | PKG | Extracted | Status |
|----------------|-----|-----------|--------|
| ~500 | RBLEGACYDLCPASS1 | 500 | ✅ Complete |
| ~500 | RBLEGACYDLCPASS2 | 524 | ✅ Complete |
| ~500 | RBLEGACYDLCPASS3 | 540 | ✅ Complete |
| 230 | RB4PRESEASONPASS | 230 | ✅ Complete |
| 10 | RB4SEASON01TOS10 | 125 | ✅ Complete |
| 10 | RB4SEASON11TOS20 | 102 | ✅ Complete |
| 10 | RB4SEASON21TOS30 | 188 | ✅ Complete |
| 5 | RB4SEASON31TOS35 | 74 | ✅ Complete |
| 168 | RB4RBNRERELEASES | 168 | ✅ Complete |
| 45 | GDRBGREENDAYPASS | 44 | ⚠️ -1 |
| 40 | LEGOROCKBANDPASS | 45 | ⚠️ +5 |

## Next Investigation Steps

1. Check base game PKG for additional songs
2. Compare against official RB4 DLC tracklists online
3. Verify Rivals expansion content
4. Identify update PKG content

## Research Findings (from web search)

### Official Rock Band 4 Song Counts (as of Jan 2024)

| Category | Count | Source |
|----------|-------|--------|
| Disc songs (base game) | 65 | On-disc soundtrack |
| At launch DLC | 1,500 | Available at RB4 launch |
| RB4-exclusive DLC | 748 | Released 2015-2024 |
| Legacy imports | ~1,700 | RB1/RB2/RB3 exports |
| **Total official** | **~3,000** | Wikipedia "nearly 3,000" |

### Why 4,084 Target?

The PS4 shows 4,084 songs which is MORE than the ~3,000 official DLC. This gap of ~1,000 songs likely includes:

1. **Custom songs (UGC+)** - Player-created songs uploaded to RB4
   - We extracted 1,279 custom songs from PKGs
   - This accounts for much of the gap!

2. **RBN songs** - Rock Band Network songs
   - Some RBN1 songs (155) are in our extraction

3. **Unreleased content** - Songs prepared but never officially released

4. **Delisted content** - Songs removed from store but still playable

5. **Export packs** - RB1, RB2, RB3, Green Day exports
   - We have: RB1 (51), RB2 (75), RB3 (73), Green Day (41) = 240 songs
   - Expected: RB1 (45), RB2 (84), RB3 (83), Green Day (47) = 259 songs
   - Gap: 19 songs

### Gap Calculation

| Source | Count |
|--------|-------|
| Official DLC | ~3,000 |
| Our custom songs (non-import) | ~1,279 |
| Gap remaining | ~800 |

The ~800 gap is likely:
- More custom songs not extracted
- Base game/update content
- Rivals expansion

## Unextracted Base Game PKGs

The following PKGs exist but were not extracted (too large, caused memory issues):

| Size | PKG Name | Status |
|------|----------|---------|
| 3.7 GB | Rock.Band.4_CUSA02084_v1.00 | Not extracted |
| 11 GB | Rock.Band.4_CUSA02084_v2.21 | Not extracted |

**These likely contain additional songs** - need to extract with the fixed pipeline.
