# Converting Custom Songs to RB4 PS4 PKG

This document outlines the process for converting custom songs from various formats to installable PS4 PKG files for Rock Band 4 Deluxe.

---

## Supported Input Formats

| Format | Source | Tool Required |
|--------|--------|----------------|
| Xbox 360 CON | RB1-3 customs, other RB games | LibForge (ForgeTool) |
| Clone Hero `.sng` | Clone Hero library | Onyx |
| Phase Shift folder | Phase Shift library | Onyx |
| Magma project (RBA) | Authoring tool output | Onyx/LibForge |
| Score Hero | Score Hero library | Onyx (untested) |

---

## Required Tools

### 1. LibForge (Primary Tool)

**Location:** `/workspace/binaries/ForgeTool.exe` (Pre-built binary)

**Installation:** Automatically copied to `/workspace/binaries/` during devcontainer setup

**Components:**
- `ForgeTool.exe` - Command-line tool (Windows only, run via Wine)
- `ForgeToolGUI.exe` - GUI tool (Windows only, run via Wine)

**Build status:** Pre-built binaries provided from RB4DX repo

### 2. Onyx (Haskell Tool)

**Location:** `/usr/local/bin/onyx` (installed)

**Capabilities:**
- Import Clone Hero songs
- Import Phase Shift songs  
- Convert to RB4 format
- Create PKG files

---

## Process Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  INPUT FORMATS                                                 │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  Xbox 360 CON   │ Clone Hero .sng │  Phase Shift / Other      │
│  (RB1-RB3)      │  (CH songs)    │                            │
└────────┬────────┴────────┬────────┴────────────┬──────────────┘
         │                │                    │
         ▼                ▼                    ▼
    ┌──────────┐    ┌──────────┐         ┌──────────┐
    │ LibForge │    │  Onyx   │         │  Onyx   │
    │con2pkg   │    │ import  │         │ import  │
    └────┬─────┘    └────┬───┘         └────┬───┘
         │               │                    │
         ▼               ▼                    ▼
    ┌──────────────────────────────────────────────┐
    │         RB4 Song Format (.songdta_ps4)       │
    │         RB4 MIDI (.rbmid_ps4)                │
    │         RB4 Audio (.mogg)                    │
    └────────────────────┬────────────────────────┘
                          │
                          ▼
    ┌──────────────────────────────────────────────┐
    │            PS4 PKG File                       │
    │         (Installable on PS4)                  │
    └──────────────────────────────────────────────┘
```

---

## Uninstalling and Modifying PKGs

If a custom song causes a crash (e.g., during preview) or has issues, you must remove it from the PS4 and rebuild the package.

### How to Uninstall or Replace a Custom PKG

If a custom song causes a crash (e.g., during preview) or has issues, you must remove it.

#### Option 1: Standard PS4 Method (May not work for all PKGs)
1. Go to **Settings** $\rightarrow$ **Storage** $\rightarrow$ **Home Space** $\rightarrow$ **Saved Data** (or **Games/DLC**).
2. Find the custom PKG you installed.
3. Select the package and choose **Delete**.

#### Option 2: The Overwrite Method (Best for "Un-deletable" PKGs)
If you cannot find a "Delete" option in the system menus, you can force an update.
1. **Remove the problematic song** from your source library (CON/SNG folder).
2. **Rebuild the PKG** using the **EXACT SAME ID** as the previous version.
3. **Install the new PKG** on the PS4. The system will overwrite the old files.
4. **CRITICAL:** In Rock Band 4, go to **Options** $\rightarrow$ **Modifiers** $\rightarrow$ **Rebuild Song Cache**. This clears the game's internal index and prevents crashes from "ghost" songs.

#### Option 3: Manual FTP Removal (Advanced/Risky)
*Use this only as a last resort.*
1. Connect via FTP (`ftp://192.168.100.117:2121`).
2. Navigate to the DLC content directory (e.g., `/mnt/sandbox/NPXS.../`).
3. Locate the specific song folder (e.g., `cu_jimmyeatworld_authority`) and delete it.
4. **Warning:** This often leaves a "ghost" entry in the library that crashes the game. You will still need to "Rebuild Song Cache".

### Identifying Which PKG Contains a Song

If you have multiple custom PKGs and aren't sure which one contains the crash-inducing song:

1. **Check the Extraction Pipeline**:
   Run the extraction pipeline in the devcontainer:
   ```bash
   python3 scripts/rb4_songlist_generator.py
   ```
2. **Search the JSON Output**:
   Open `rb4_temp/rb4_custom_songs.json` and search for the song title.
3. **Find the `_pkg_file` field**:
   The JSON entry for the song will contain a field called `_pkg_file`. This is the exact PKG name you need to uninstall or overwrite.
   *Example:* `"title": "The Authority Song", "_pkg_file": "UP8802-CUSA02084_00-CUSTOM_SNG_01.pkg"`

---

## Detailed Conversion Steps

### Method 1: Xbox RB CON to PS4 PKG (LibForge)

**Prerequisites:**
- Wine installed (available in devcontainer)
- Xbox RB CON file ready

**Steps:**

1. **Locate your CON file**
   ```
   Path: /path/to/your/song_rb3con
   ```

2. **Convert using ForgeTool (CLI)**
   ```bash
   wine /workspace/binaries/ForgeTool.exe \
     con2pkg \
     --id YOURSONG001 \
     --desc "Custom Song - Artist Name" \
     /path/to/song_rb3con \
     /output/directory
   ```

3. **Options:**
   - `--scee` - Use for European (SCEE) PS4 version
   - `--id` - 16 character unique ID (e.g., `CUSTOM00001`)
   - `--desc` - Display name on PS4

4. **Using ForgeToolGUI (Easier)**
   ```bash
   wine /workspace/LibForge/LibForge/ForgeToolGUI/ForgeToolGUI.exe
   ```
   Then: Tools → Convert CON to PKG

**Output:** A `.pkg` file in the specified output directory

### Method 2: Clone Hero to RB4 (Onyx)

**Prerequisites:**
- Clone Hero `.sng` files OR
- Phase Shift/Clone Hero folder with `song.ini` + `notes.chart`

**Steps:**

1. **Import Clone Hero song folder**
   ```bash
   onyx import /path/to/clone_hero_song.sng
   ```
   Or for folder:
   ```bash
   onyx import /path/to/song_folder/
   ```

2. **Export to RB4 format**
   ```bash
   onyx build --format rb4 --output /output/path
   ```

3. **Create PKG**
   ```bash
   onyx build --format rb4_ps4 --output /output/pkg
   ```

**Note:** Onyx can create PKG directly for PS4 or PS3 formats.

### Method 3: Batch Conversion

For multiple songs, you can batch convert by pointing to a folder:

```bash
wine ForgeTool.exe con2pkg \
  --id BATCH00001 \
  --desc "Custom Pack" \
  /path/to/con_folder/ \
  /output/directory
```

---

## Required Song Files

A complete RB4 custom song requires these files in the PKG:

| File | Purpose | Generated By |
|------|---------|--------------|
| `.songdta_ps4` | Metadata (title, artist, etc.) | LibForge/Onyx |
| `.rbmid_ps4` | Note charts (MIDI) | LibForge/Onyx |
| `.mogg` | Audio | Must be original |
| `.mogg.dta` | Audio config | LibForge/Onyx |
| `.moggsong` | Song config | LibForge/Onyx |
| `.png_ps4` | Album art | User provides |
| `.lipsync_ps4` | Face animation | LibForge/Onyx |
| `.rbsong` | Arrangement config | LibForge/Onyx |

---

## Audio File Requirements

### MOGG Files

- **Source:** Original RB audio or re-ripped from source
- **Encryption:** LibForge can decrypt/encrypt MOGG files
- **Format:** Must be in Rock Band MOGG format

### Handling Encrypted MOGG

If MOGG files are encrypted (from older customs):

```bash
# Decrypt MOGG using LibForge
wine ForgeTool.exe decryptmogg /path/to/encrypted.mogg /path/to/output/
```

---

## PS4 Installation

Once you have the PKG file:

1. **Copy to USB drive** or transfer via FTP
2. **On PS4:**
   - Settings → Debug Settings → Game → Package Installer
3. **Select the PKG file** and install
4. **Launch RB4** - Song appears in library

**Note:** PS4 must be jailbroken with HEN to install custom PKGs

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| PKG won't install | Wrong version (SCEE vs SCEE) | Use `--scee` flag for EU |
| Song doesn't appear | Missing files in PKG | Verify all 8 required files |
| Audio not playing | Encrypted MOGG | Decrypt MOGG first |
| Wrong notes | Chart conversion issue | Use Onyx for better results |

### Validation

Check your PKG contains all required files:
```bash
# Extract and verify
PkgTool.Core dump your_song.pkg --out extracted/
ls extracted/uroot/songs/*/
```

---

## Automation Opportunities (Future)

1. **Python wrapper** around ForgeTool with Wine
2. **Batch script** for multiple CON files
3. **Onyx integration** for Clone Hero imports
4. **Automated MOGG decryption** for old custom libraries

---

## References

- [LibForge GitHub](https://github.com/maxton/LibForge)
- [Onyx GitHub](https://github.com/mtolly/onyx)
- [PSXHAX RB4 Custom Guide](https://www.psxhax.com/threads/rock-band-4-rb4-custom-ps4-dlc-building-tools-guide-by-maxton.6180/)
- [RB4 Deluxe](https://rb4dx.milohax.org/)

---

## Quick Reference Commands

```bash
# Convert single CON to PKG (LibForge)
wine ForgeTool.exe con2pkg --id CUSTOM00001 --desc "My Song" input.con output/

# Import Clone Hero song (Onyx)
onyx import song.sng --to output_folder

# Build RB4 PKG (Onyx)
onyx build --format rb4_ps4 --input song_folder/ --output song.pkg
```

---

*Document created: April 25, 2026*
*Last updated: April 25, 2026*

## Devcontainer Tools Status

The following tools are currently available in the devcontainer:

| Tool | Status | Location |
|------|--------|-----------|
| Onyx | ✅ Installed | `/usr/local/bin/onyx` |
| LibForge source | ✅ Cloned | `/workspace/LibForge/` |
| PkgTool.Core | ✅ Installed | Via .NET |
| Wine | ✅ Installed | System |
| ps4_pkg_tool | ✅ Cloned | `/workspace/ps4_pkg_tool/` |
| ForgeTool | ⚠️ Windows only | Needs Wine |

### What's Missing

1. **ForgeTool.exe** - Requires Windows, available via Wine but may have issues
2. **Nautilus** - Windows-only tool for batch conversion
3. **Magma** - RB authoring tool (external)

### Next Steps for Automation

1. Test ForgeTool conversion with Wine
2. Build Onyx CLI for direct PKG creation
3. Create Python wrapper scripts for batch operations

---

## Adding Custom Songs to the Song List

Once you've created and installed custom song PKGs on your PS4, you'll want them to appear in your searchable song list on GitHub Pages. Here's the complete workflow:

### Step 1: Copy PKGs to the SMB Share

1. **Location:** Copy your new custom `.pkg` files to:
   ```
   //192.168.100.135/incoming/temp/Rb4Dlc/
   ```

### Step 2: Run the Extraction Pipeline

From the devcontainer, run the full extraction pipeline:

```bash
cd /workspace/RB4

# Run the full pipeline (reprocesses all PKGs including new ones)
python3 scripts/rb4_songlist_generator.py \
  --reprocess-cached-metadata
```

**What this does:**
- Scans all PKGs in the SMB share
- Extracts metadata from `.songdta_ps4` files
- Applies baseline fallback for empty metadata songs
- Generates updated JSON and HTML outputs

### Step 3: Verify Output

Check the generated files:

```bash
# Check song count
python3 -c "import json; print(len(json.load(open('rb4_temp/rb4_custom_songs.json'))))"

# View the HTML list
ls -la docs/RB4SongList.html
```

### Step 4: Deploy to GitHub Pages

The updated files are auto-copied to `/workspace/docs/` during pipeline run:

| File | Purpose |
|------|---------|
| `docs/RB4SongList.html` | Interactive song list |
| `docs/SongListSortedByArtist.txt` | By artist (text) |
| `docs/SongListSortedBySongName.txt` | By title (text) |

**Deploy to GitHub:**
```bash
cd /workspace
git add docs/
git commit -m "Add new custom songs"
git push origin main
```

GitHub Pages will automatically deploy the updated song list.

### Quick Summary - Add Custom Songs Workflow

```
1. Convert:  CON/.sng → PKG (LibForge/Onyx)
2. Copy:     PKG → SMB share (//192.168.100.135/incoming/temp/Rb4Dlc/)
3. Extract:  python3 scripts/rb4_songlist_generator.py --reprocess-cached-metadata
4. Deploy:   git add docs/ && git push
5. Play:     Install PKG on PS4 → Song appears in RB4 library
```

### Troubleshooting

**Problem:** New songs don't appear in the list
- Verify PKG is on SMB share
- Check pipeline output for errors
- Ensure `.songdta_ps4` has valid metadata

**Problem:** Songs show empty metadata
- This is expected for some customs
- Baseline fallback should recover artist/title from shortname

**Problem:** Duplicate songs
- The pipeline handles duplicates (custom takes precedence)

---

*Document created: April 25, 2026*
*Last updated: April 25, 2026*