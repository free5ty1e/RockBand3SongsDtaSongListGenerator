# RB4 Song List Investigation - Complete Context File

## Current Status (For User Review)

### What's Working
- HTML Song List: `/workspace/docs/RB4SongList.html` (3794 songs)
- TXT Song Lists: `/workspace/docs/SongListSortedByArtist.txt`, etc.
- GitHub Pages: https://free5ty1e.github.io/RB4-Song-List-Generator/
- All outputs include: artist, title, album, year, duration, source, instruments, shortName, inferred, PKG filename

### Quick Steps to Try Before Next Party
1. **CRITICAL**: In RB4, go to Options → Modifiers → **Rebuild Song Cache** before playing!
2. This forces PS4 to re-scan all installed DLC packages
3. Test specific missing songs after doing this

### Song Counts
| Source | Count |
|--------|-------|
| PS4 game shows | 4084 |
| Our extraction (HTML) | 3794 |
| Our extraction (JSON) | 3705 |
| Gap | ~290 |

### File Locations

**SMB Share Locations:**
```
//192.168.100.135/incoming/temp/Rb4Dlc       (DLC packages - 98 files)
//192.168.100.135/incoming/temp/rb4gamepkgs   (Game/Update packages)
```

**PS4 FTP Access (READ-ONLY):**
```
ftp://192.168.100.117:2121
Login: anonymous
```
- Port: 2121
- Use only for READ operations - do NOT write to PS4

**Game/Expansion PKGs in rb4gamepkgs:**
- `Rock.Band.4_CUSA02084_v1.00_[2.50]_OPOISSO893.pkg` (base game ~3.7GB)
- `Rock.Band.4_CUSA02084_v2.21_[5.05]_OPOISSO893.pkg` (update ~11GB)
- `Rock.Band.4_CUSA02084_Rock.Band.Rivals.Expansion.Pack.pkg` (Rivals ~1MB)

**GitHub Pages Deployment:**
- Source: `/workspace/docs/` folder
- Files auto-copied from `/workspace/RB4/output/` during pipeline run:
  - RB4SongList.html
  - SongListSortedByArtist.txt
  - SongListSortedBySongName.txt
  - SongListSortedByArtistClean.txt
  - SongListSortedBySongNameClean.txt
- Process: Pipeline runs `rb4_songlist_generator.py` which calls:
  - `generate_html_list.py` → creates RB4SongList.html
  - `generate_rb4_song_list.js` → creates TXT files
  - Each script copies output to docs folder with `shutil.copy()`
- Deployed via GitHub Pages at: https://free5ty1e.github.io/RB4-Song-List-Generator/

---

## Additional Investigation Notes

### songs.dta Found in SMB Share
- Location: `//192.168.100.135/income/temp/songs.dta`
- Downloaded to: `/workspace/rb4_temp/songs_backup.dta`
- Contains: 55 songs in Rock Band's LISP-like dta format
- Appears to be a custom songs list, not the full game list

### RB4 Deluxe Project Potential
The RB4DX project at https://rb4dx.milohax.org/ has:
- Full decompilation of Rock Band 4
- Could provide exact song counts
- Would require extracting from the game PKG files

### Possible Causes of Gap (4084 vs 3794)

1. **Our extraction issues:**
   - Some PKGs may not have been fully processed
   - The "fake" PKGs (RB4BONUSGUITARGS_fake, RB4BONUSSHIRTBGR_fake) may have songs we haven't extracted

2. **PS4 vs our counting:**
   - PS4 may count duplicates differently
   - Some songs may exist in multiple PKGs
   - The 82 duplicates in our list might not be counted the same way

3. **Missing content:**
   - Not all PKGs may have been transferred from PS4
   - Some DLC may have been purchased but not downloaded
   - RBN2 content may not be in our set

### What Would Help Close the Gap

1. **Verify all 98 PKGs are processed** - Check processed list vs SMB list
2. **Extract the 2 fake PKGs** - RB4BONUSGUITARGS_fake, RB4BONUSSHIRTBGR_fake
3. **Compare specific missing songs** - Get list of songs from PS4 that aren't in our extraction
4. **Check RB4 Deluxe song lists** - Their repo may have complete lists

### GitHub Pages Deployment Details

The docs folder is deployed automatically via GitHub Pages:
1. Pipeline runs: `python3 scripts/rb4_songlist_generator.py --reprocess-cached-metadata`
2. This calls:
   - `generate_html_list.py` → creates RB4SongList.html in output folder
   - `generate_rb4_song_list.js` → creates TXT files in output folder
3. Each script uses `shutil.copy()` to copy to `/workspace/docs/`
4. GitHub Pages serves from docs/ folder automatically
5. URL: https://free5ty1e.github.io/RB4-Song-List-Generator/

### HTML Output Fields (all 10 columns)
1. Artist
2. Title  
3. Album
4. Year
5. Duration
6. Source (e.g., "Custom", "Rock Band 4 DLC")
7. Instruments (emoji display)
8. ShortName (in-game song identifier)
9. Inferred (✓ if metadata was empty, recovered from shortName)
10. PKG (which PKG file contains this song)

This context file was last updated: April 19, 2026

RESEARCH PROGRESS:
- Created /workspace/RB4/docs/research/ folder
- Created pkg_source_comparison.html - detailed gaps by source with 150+ songs to check
- Created songs_to_verify_on_ps4.md - test procedures  
- Created online_resources.md - external references
- KEY FINDINGS:
  - RB2 DLC: WE HAVE 0 of ~84 (completely missing!)
  - RBN1: Only 155 of ~1030 (875 missing!)
  - RB3 DLC: Only 463 of ~588 (125 missing)
  - RB4 DLC: Only 625 of ~800+ (175 missing)

---

## Investigation Log

### April 19 2026 - Fake PKG Investigation
- Downloaded RB4BONUSGUITARGS_fake.pkg (1.9MB)
- Contains mostly garbage/random data - not real songs
- Conclusion: "fake" PKGs are not yielding additional songs

### April 19 2026 - Duplicate Analysis
- Total songs: 3705
- Unique: 3623  
- Duplicates: 82
- All duplicates are Custom vs Custom (same song in multiple PKGs)
- Examples: Badfinger, Caballo Dorado, Avril Lavigne, Michael Jackson

### April 19 2026 - SMB songs.dta Investigation
- Found songs.dta in SMB temp folder
- Contains 55 songs in LISP format
- Appears to be custom songs, not full game list

### Gap Analysis Summary
- PS4 shows: 4084
- Our unique: 3623  
- Our total with dups: 3705
- Gap to PS4: 379 (4084 - 3705)
- This could include:
  - Songs in base game xpak not extracted
  - Songs from Rivals expansion not in our PKGs
  - Some PKGs not transferred to SMB
  - Songs that need "Rebuild Song Cache" to appear

---

## External Resources Found

### RB4.app - Rock Band 4 Library
- Website: https://rb4.app/
- Appears to have a complete song list

### Harmonix Official Song List
- http://www.harmonixmusic.com/games/rock-band/rb4songs
- Official announced songs for launch

### Outcyders Complete List (2015)
- https://www.outcyders.net/news/the-100-complete-definitive-full-rock-band-4-song-list
- Day-one song list from 2015

### RB4 Deluxe Project
- https://rb4dx.milohax.org/
- Full decompilation project

### Google Sheets Resources Found (April 2026)
1. **Rock Band Song List** - https://docs.google.com/spreadsheets/d/1R1scPKLJo70WiCNXNU8_DoyZgK_R8xjwU5uY_WUHaAs/edit
   - Complete Rock Band series songs

2. **Rock Band 4 DLC** - https://docs.google.com/spreadsheets/d/1FQF5jJ0es3pReJXUVBmJZaxJb9xkXJ9GPI5RvbNgoCw/edit
   - Weekly DLC tracking (updated June 2025)
   - Shows PS4 vs Xbox differences

3. **Rock Band & Guitar Hero Songs** - https://docs.google.com/spreadsheets/d/1-3lo2ASxM-3yVr_JH14F7-Lc1v2_FcS5Rv_yDCANEmk/edit
   - Massive cross-game database
   - Has RB1-RB4, GH1-6, DJs, more

4. **Wikipedia List**
   - https://en.wikipedia.org/wiki/List_of_songs_in_Rock_Band_4
   - Official 65 songs on disc + DLC info

---

## Tests/Experiments for PS4 Validation

### What To Test on PS4 (For Manual Validation)

The PS4 shows 4084 songs. Our extraction has 3705 (with 82 duplicates = 3623 unique).

**Categories of potential missing songs:**

1. **Songs in our list that show on PS4 but filter differently** - need to test filters
2. **Songs NOT in our list that ARE on PS4** - need to identify these
3. **Rebuild cache test** - verify this fixes visibility

### Test 1: Search for specific known songs on PS4
These songs SHOULD be in our list but verify they show:
- Search "Franz Ferdinand" - we have 0 in our extraction
- Search "Seether" - we have 2 (from fake PKGs)
- Search "Joan Jett" - we have 1

### Test 2: Check custom songs section
Our "Custom" source has 1289 songs. Check if all show.

### Test 3: Check Rivals section  
Our baseline has songs from Rivals xpak. Verify these show.

### Test 4: After running "Rebuild Song Cache"
Compare new total after cache rebuild.

### Test 5: Compare totals by category
Match our counts:
- Custom: 1289
- RB1 DLC: 893  
- RB4 DLC: 625
- RB3 DLC: 463
- RB Network 1: 155
- RB2: 75
- RB3: 73
- RB1: 51
- RB Green Day: 41
- LEGO Rock Band: 40
- Baseline (v1.00 + Rivals): 99