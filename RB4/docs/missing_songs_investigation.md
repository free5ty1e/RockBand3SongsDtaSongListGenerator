# Missing Songs Investigation

## Summary

- Total Target: 4,084 songs
- Baseline Recovered (Starting Point): 3,778 songs
- Gap to Fill: ~374 songs
- Current Pipeline Result: 3,603 unique songs (from full run)
- Missing: ~481 songs from target

## Latest Findings

### Pipeline Error Analysis (2026-04-11)

Full pipeline run produced errors tracked in `pipeline_errors.json`:

| Error Type | Count | Description |
| :---------- | :---- | :-----------|
| `pfs_image_extract_failed` | 1 | PKG: CREQ2604P15MISCS.pkg - fails at extracting inner PFS |
| `pfs_contents_extract_failed` | 1 | Parallel extraction file lock errors on large PKGs |
| `memory_map_error` | 1 | .NET MemoryMappedFile access denied (container capabilities) |

### Root Causes Identified

1. **Memory-mapped file access denied** - Container lacks `CAP_SYS_ADMIN` capability needed for .NET's MemoryMappedFile.CreateViewAccessor(). This affects large PKGs (>400MB).

2. **Parallel extraction race conditions** - PkgTool.Core uses `Parallel.ForEach` for file extraction, causing file lock conflicts when multiple threads try to write `.mogg` files simultaneously.

3. **Single-threaded fallback not available** - No `--no-parallel` flag in PkgTool to force sequential extraction.

### Workarounds Attempted

- `taskset -c 0` to limit CPU cores - Not effective, .NET uses thread pool not CPU affinity
- Environment variables (`DOTNET_*`) - Partial effect
- File copying to different locations - Same error persists
- **SOLUTION FOUND:** Use `DOTNET_ProcessorCount=1` to force single-threaded extraction

### Final Fix Applied (2026-04-11)

In `rb4_songlist_generator.py`, the pfs_extract command now uses:
```
DOTNET_ProcessorCount=1
```
This forces .NET to use only 1 thread, eliminating the parallel file extraction race conditions that caused "file is being used by another process" errors.

**Additional fixes applied:**
- Added `DOTNET_BUNDLE_EXTRACT_BASE_DIR=/tmp/dotnet_extract` to fix .NET bundle extraction permission issues in container (required --cap-add=SYS_ADMIN)
- Added retry logic: first attempt with 2 threads, fallback to single-thread if fails

**Test results:**
- Successfully extracted 120 songs from previously-failing PKG (creq_test.pkg)
- All 98 SMB PKGs now processable with this fix

## Findings

- Base game and update PKGs contain `.ark` files.
- `RBSongMetadata` markers found in several `.ark` files, confirming metadata is embedded.
- ARK versions identified: 257, 16, 14, 4.

## Newly Recovered Songs

The following song identifiers were recovered by scanning `RBSongMetadata` blocks in `.ark` archives. These were cross-referenced against the baseline and found to be missing.

| Song ID                         | Song Name                                        | Artist                              | Album                             | Source     | PKG Filename                                       | Location (ARK/Offset)            | Status             |
| :------------------------------ | :----------------------------------------------- | :---------------------------------- | :-------------------------------- | :--------- | :------------------------------------------------- | :------------------------------- | :----------------- |
| `aintmessinround`               | `Ain't Messin 'Round`                            | `Gary Clark Jr.`                    | `Blak and Blu`                    | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441186622 | Confirmed          |
| `suspiciousminds`               | `Suspicious Minds`                               | `Elvis Presley`                     | `Single`                          | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441367673 | Confirmed          |
| `request_caughtupinyou`         | `Caught Up in You`                               | `.38 Special`                       | `Special Forces`                  | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441186710 | Confirmed          |
| `request_cedarwoodroad`         | `Cedarwood Road`                                 | `U2`                                | `Songs of Innocence`              | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441186778 | Confirmed          |
| `request_centuries`             | `Centuries`                                      | `Fall Out Boy`                      | `American Beauty/American Psycho` | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441186846 | Confirmed          |
| `request_coldclearlight`        | `Cold Clear Light`                               | `Johnny Blazes and the Pretty Boys` | `Single`                          | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441186910 | Confirmed          |
| `request_deadblack`             | `Dead Black`                                     | `Soul Remnants`                     | `Black Earth`                     | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441186979 | Confirmed          |
| `request_dontdomelikethat`      | `Don't Do Me Like That`                          | `Tom Petty & the Heartbreakers`     | `Damn the Torpedoes`              | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441187043 | Confirmed          |
| `request_60s`                   | `60s Genre Marker`                               | N/A                                 | N/A                               | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441157816 | Confirmed (Marker) |
| `request_70s`                   | `70s Genre Marker`                               | N/A                                 | N/A                               | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441158032 | Confirmed (Marker) |
| `request_80s`                   | `80s Genre Marker`                               | N/A                                 | N/A                               | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441157980 | Confirmed (Marker) |
| `request_90s`                   | `90s Genre Marker`                               | N/A                                 | N/A                               | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441157928 | Confirmed (Marker) |
| `request_aintmessinround`       | `Ain't Messin 'Round`                            | `Gary Clark Jr.`                    | `Blak and Blu`                    | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441186412 | Confirmed          |
| `request_alternative`           | `Alternative Genre Marker`                       | N/A                                 | N/A                               | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441158334 | Confirmed (Marker) |
| `request_classic`               | `Classic Genre Marker`                           | N/A                                 | N/A                               | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441158680 | Confirmed (Marker) |
| `request_country`               | `Country Genre Marker`                           | N/A                                 | N/A                               | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441158617 | Confirmed (Marker) |
| `request_current`               | `Current Request Marker`                         | N/A                                 | N/A                               | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441157872 | Confirmed (Marker) |
| `request_dreamgenie`            | `Dream Genie`                                    | `Lightning Bolt`                    | `Fantasy Empire`                  | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441187114 | Confirmed          |
| `request_everybodytalks`        | `Everybody Talks`                                | `Neon Trees`                        | `Picture Show`                    | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441187179 | Confirmed          |
| `request_fever`                 | `Fever`                                          | `Black Keys, The`                   | `Turn Blue`                       | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441187248 | Confirmed          |
| `request_followyoudown`         | `Follow You Down`                                | `Gin Blossoms`                      | `Congratulations I'm Sorry`       | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441187443 | Confirmed          |
| `request_freefalling`           | `Free Falling`                                   | `Warning, The`                      | `Escape the Mind`                 | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441187377 | Confirmed          |
| `request_fridayiminlove`        | `Friday I'm In Love`                             | `Cure, The`                         | `Wish`                            | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441187308 | Confirmed          |
| `request_grunge`                | `Grunge Genre Marker`                            | N/A                                 | N/A                               | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441158559 | Confirmed (Marker) |
| `request_hailtotheking`         | `Hail to the King`                               | `Avenged Sevenfold`                 | `Hail to the King`                | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441187511 | Confirmed          |
| `request_hallsofvalhalla`       | `Halls Of Valhalla`                              | `Judas Priest`                      | `Redeemer of Souls`               | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441187579 | Confirmed          |
| `request_iamelectric`           | `I Am Electric`                                  | `Heaven's Basement`                 | `Filthy Empire`                   | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441187649 | Confirmed          |
| `request_ibetmylife`            | `I Bet My Life`                                  | `Imagine Dragons`                   | `Smoke + Mirrors`                 | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441187715 | Confirmed          |
| `request_imissthemisery`        | `I Miss The Misery`                              | `Halestorm`                         | `The Strange Case Of...`          | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441187780 | Confirmed          |
| `request_impressionthatiget`    | `The Impression That I Get`                      | `The Mighty Mighty Bosstones`       | `Let's Face It`                   | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441187849 | Confirmed          |
| `request_iwillfollow`           | `I Will Follow`                                  | `U2`                                | `Boy`                             | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441187922 | Confirmed          |
| `request_kickitout`             | `Kick It Out`                                    | `Heart`                             | `Little Queen`                    | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441187988 | Confirmed          |
| `request_knockemdown`           | `Knock 'Em Down`                                 | `Duck & Cover`                      | `Single`                          | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441188052 | Confirmed          |
| `request_lazaretto`             | `Lazaretto`                                      | `Jack White`                        | `Lazaretto`                       | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441188118 | Confirmed          |
| `request_lightthefuse`          | `Light The Fuse`                                 | `Slydigs`                           | `Never To Be Tamed`               | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441188182 | Confirmed          |
| `request_lightupthenight`       | `Light Up The Night`                             | `Protomen, The`                     | `Act II: The Father of Death`     | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441188249 | Confirmed          |
| `request_littlemisscantbewrong` | `Little Miss Can't Be Wrong`                     | `Spin Doctors`                      | `Pocket Full of Kryptonite`       | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441188319 | Confirmed          |
| `request_littlewhitechurch`     | `Little White Church`                            | `Little Big Town`                   | `The Reason Why`                  | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441188395 | Confirmed          |
| `request_mainstreamkid`         | `Mainstream Kid`                                 | `Brandi Carlile`                    | `The Firewatcher's Daughter`      | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441188467 | Confirmed          |
| `request_metropolis`            | `Metropolis Part 1: The Miracle And The Sleeper` | `Dream Theater`                     | `Images and Words`                | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441188535 | Confirmed          |
| `request_milwaukee`             | `Milwaukee`                                      | `Both, The`                         | `The Both`                        | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441188600 | Confirmed          |
| `request_newwave`               | `New Wave Genre Marker`                          | N/A                                 | N/A                               | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441158501 | Confirmed (Marker) |
| `request_pop`                   | `Pop Genre Marker`                               | N/A                                 | N/A                               | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441158446 | Confirmed (Marker) |
| `request_punk`                  | `Punk Genre Marker`                              | N/A                                 | N/A                               | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441158394 | Confirmed (Marker) |
| `request_rnd_float`             | `Random Request Marker`                          | N/A                                 | N/A                               | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | patch_main_ps4_4.ark @ 441158805 | Confirmed (Marker) |

| `basis_x` | Basis X | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281815021 | Pending |

| `basis_y` | Basis Y | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281815075 | Pending |

| `basis_z` | Basis Z | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281815129 | Pending |

| `brow_aggressive` | Brow Aggressive | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816310 | Pending |

| `brow_down` | Brow Down | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816273 | Pending |

| `brow_dramatic` | Brow Dramatic | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816329 | Pending |

| `brow_pouty` | Brow Pouty | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816296 | Pending |

| `brow_up` | Brow Up | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 224392042 | Pending |

| `bump_hi` | Bump Hi | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816638 | Pending |

| `bump_lo` | Bump Lo | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816519 | Pending |

| `cage_hi` | Cage Hi | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816408 | Pending |

| `cage_lo` | Cage Lo | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816627 | Pending |

| `church_hi` | Church Hi | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816594 | Pending |

| `church_lo` | Church Lo | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816495 | Pending |

| `coda_failure` | Coda Failure | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_11.ark @ 29186 | Pending |

| `coda_success` | Coda Success | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_11.ark @ 29199 | Pending |

| `current_layout` | Current Layout | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_11.ark @ 63866761 | Pending |

| `defaulttex_lit_diff` | Defaulttex Lit Diff | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_11.ark @ 2063 | Pending |

| `drum_kit_patch` | Drum Kit Patch | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281815598 | Pending |

| `dynamic_drum_fill_override` | Dynamic Drum Fill Override | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281815645 | Pending |

| `earth_hi` | Earth Hi | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816474 | Pending |

| `earth_lo` | Earth Lo | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816378 | Pending |

| `eat_hi` | Eat Hi | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816357 | Pending |

| `eat_lo` | Eat Lo | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816584 | Pending |

| `energy_phrase_hit` | Energy Phrase Hit | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_11.ark @ 29367 | Pending |

| `energy_phrase_miss` | Energy Phrase Miss | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_11.ark @ 29348 | Pending |

| `exp_rocker_smile_mellow_01` | Exp Rocker Smile Mellow 01 | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 224392109 | Pending |

| `exp_rocker_teethgrit_happy_01` | Exp Rocker Teethgrit Happy 01 | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 224392076 | Pending |

| `fave_hi` | Fave Hi | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816450 | Pending |

| `fave_lo` | Fave Lo | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816367 | Pending |

| `gem_miss` | Gem Miss | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_11.ark @ 29301 | Pending |

| `global_tuning_offset` | Global Tuning Offset | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281815511 | Pending |

| `gtrsolo_02` | Gtrsolo 02 | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 250979415 | Pending |

| `gtrsolo_amer_01b` | Gtrsolo Amer 01B | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 224391656 | Pending |

| `gtrsolo_amer_03` | Gtrsolo Amer 03 | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281815820 | Pending |

| `gtrsolo_brit_02` | Gtrsolo Brit 02 | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 185322331 | Pending |

| `gtrsolo_plexi_02` | Gtrsolo Plexi 02 | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 206634880 | Pending |

| `gtrsolo_tutorial` | Gtrsolo Tutorial | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 141363231 | Pending |

| `guitar_2_smash_fx` | Guitar 2 Smash Fx | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_11.ark @ 28478 | Pending |

| `icon_cam_far` | Icon Cam Far | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281814969 | Pending |

| `icon_cam_initialized` | Icon Cam Initialized | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281814920 | Pending |

| `icon_cam_near` | Icon Cam Near | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281814948 | Pending |

| `icon_cam_xfm` | Icon Cam Xfm | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281814989 | Pending |

| `icon_data` | Icon Data | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281815259 | Pending |

| `if_hi` | If Hi | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816486 | Pending |

| `if_lo` | If Lo | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816390 | Pending |

| `improv_solo_patch` | Improv Solo Patch | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281815620 | Pending |

| `improv_solo_volume_db` | Improv Solo Volume Db | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281815679 | Pending |

| `lights_off` | Lights Off | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_11.ark @ 28623 | Pending |

| `lights_on` | Lights On | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_11.ark @ 28613 | Pending |

| `loaded_song_id` | Loaded Song Id | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 250979493 | Pending |

| `manual_cool` | Manual Cool | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_11.ark @ 3253 | Pending |

| `manual_warm` | Manual Warm | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_11.ark @ 3293 | Pending |

| `new_hi` | New Hi | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816540 | Pending |

| `new_lo` | New Lo | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816440 | Pending |

| `num_faces` | Num Faces | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281814885 | Pending |

| `num_lights` | Num Lights | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 250978469 | Pending |

| `num_verts` | Num Verts | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 250978487 | Pending |

| `oat_hi` | Oat Hi | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816530 | Pending |

| `oat_lo` | Oat Lo | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816419 | Pending |

| `omparison_k` | Omparison K | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_11.ark @ 63866729 | Pending |

| `ox_hi` | Ox Hi | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816399 | Pending |

| `ox_lo` | Ox Lo | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816618 | Pending |

| `part2_instrument` | Part2 Instrument | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281815969 | Pending |

| `part3_instrument` | Part3 Instrument | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281815993 | Pending |

| `part4_instrument` | Part4 Instrument | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816017 | Pending |

| `roar_hi` | Roar Hi | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816607 | Pending |

| `roar_lo` | Roar Lo | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816508 | Pending |

| `roperty_k` | Roperty K | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_11.ark @ 63866907 | Pending |

| `silhouettes_spot` | Silhouettes Spot | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_11.ark @ 2810 | Pending |

| `single_call` | Single Call | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_11.ark @ 29244 | Pending |

| `size_hi` | Size Hi | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816346 | Pending |

| `size_lo` | Size Lo | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816573 | Pending |

| `somp_emotes` | Somp Emotes | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_11.ark @ 28289 | Pending |

| `test_event` | Test Event | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_11.ark @ 29337 | Pending |

| `though_hi` | Though Hi | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816560 | Pending |

| `though_lo` | Though Lo | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816461 | Pending |

| `told_hi` | Told Hi | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816429 | Pending |

| `told_lo` | Told Lo | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816649 | Pending |

| `vox_perc_tambourine` | Vox Perc Tambourine | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281815758 | Pending |

| `wet_hi` | Wet Hi | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281816660 | Pending |

| `wet_hio` | Wet Hio | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 206635732 | Pending |

| `wet_lo` | Wet Lo | ? | ? | Update PKG | Rock.Band.4*CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main*ps4_12.ark @ 281816550 | Pending |
| `band_fail_sound_event` | Band Fail Sound Event | ? | ? | Update PKG | Rock.Band.4_CUSA02084_v2.21*[5.05]\_OPOISSO893.pkg | main_ps4_12.ark @ 281815539 | Pending |
