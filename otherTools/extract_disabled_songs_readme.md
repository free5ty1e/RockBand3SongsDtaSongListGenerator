# 🎵 Rock Band 3 Deluxe: Extract Disabled Songs Script

This Python script extracts commented-out song definitions from your `songs.dta` file and moves them to a separate archive file, helping you manage memory usage on the PS3 while maintaining a clean, organized song library.

## 📋 Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Solution](#solution)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [File Handling](#file-handling)
- [Comment Style Support](#comment-style-support)
- [Examples](#examples)
- [Safety Features](#safety-features)
- [Troubleshooting](#troubleshooting)
- [Technical Details](#technical-details)

## 🎯 Overview

The `extract_disabled_songs.py` script intelligently scans your `songs.dta` file for commented-out song definitions and moves them to a dedicated archive file called `songs.disabled.dta`. This helps reduce memory usage on the PS3 while preserving disabled songs for future reference or restoration.

## 🚨 Problem Statement

Rock Band 3 Deluxe on PS3 has limited memory capacity. Large `songs.dta` files can cause:
- Longer loading times
- Memory allocation errors
- Game instability
- Preview audio failures

However, completely deleting disabled songs means losing access to them forever. This script provides a middle ground: disable songs to reduce memory usage while maintaining an archive of disabled content.

## ✅ Solution

The script provides:
- **Automatic detection** of commented-out song definitions
- **Clean extraction** of complete song blocks
- **Archive creation** with proper organization
- **Memory optimization** for PS3 gameplay
- **Flexible comment style support** for different editors

## 📋 Prerequisites

- **Python 3.6+** installed on your system
- **songs.dta file** in the same directory as the script
- **Write permissions** in the working directory
- **Backup** of your original songs.dta (recommended)

## 🚀 Installation & Setup

1. **Download the script** to your Rock Band 3 Deluxe tools directory
2. **Ensure Python 3** is installed and accessible via command line
3. **Place the script** in the same directory as your `songs.dta` file
4. **Optional:** Create a backup of your `songs.dta` file

# Verify Python installation
python3 --version

# Make script executable (Linux/Mac)
chmod +x extract_disabled_songs.py## 

# 📖 Usage

### Basic Usage

# Run the script
python3 extract_disabled_songs.py

# Or if python3 is not in PATH
python extract_disabled_songs.py### Advanced Usage

# Run with custom Python path
/usr/bin/python3 extract_disabled_songs.py

# Run from different directory
cd /path/to/your/rb3/files
python3 /path/to/extract_disabled_songs.py## 🔍 How It Works

### 1. **Song Detection**
The script scans `songs.dta` line by line, looking for commented-out song definitions that follow this pattern:
ta
; (
;    'song_identifier'
;    (
;       'name'
;       "Song Title"
;    )
;    ; ... entire song definition ...
; )### 2. **Metadata Extraction**
For each detected song, the script extracts:
- **Song Title** (from the 'name' field)
- **Artist** (from the 'artist' field)  
- **Album** (from the 'album_name' field, if present)

### 3. **File Processing**
- **Commented songs** → moved to `songs.disabled.dta`
- **Active songs** → remain in `songs.dta`
- **Informational comments** → remain in `songs.dta`

### 4. **Archive Management**
- **First run**: Creates `songs.disabled.dta` with header
- **Subsequent runs**: Appends new disabled songs to existing archive

## 📁 File Handling

### Input Files
- **`songs.dta`** - Your main song database file

### Output Files
- **`songs.dta`** - Cleaned file with only active songs
- **`songs.disabled.dta`** - Archive of disabled song definitions

### Backup Files
- **`songs.dta.backup`** - Automatic backup of original file

### File Structure Example

**songs.disabled.dta:**ta
; This file contains song definitions that were commented out
; from songs.dta to reduce memory usage on PS3
; Created: 2024-01-15 14:30:22 EST
; Total disabled songs: 253

; (
;    'song_id_1'
;    ; ... complete song definition ...
; )

; --- Additional disabled songs added (5 songs) - 2024-01-15 15:45:10 EST ---

; (
;    'song_id_2' 
;    ; ... complete song definition ...
; )## 💬 Comment Style Support

The script supports multiple comment styles used by different editors:

### ✅ Supported Styles

**Single Semicolon (Standard):**ta
; (
;    'song_id'
;    (
;       'name'
;       "Song Title"
;    )**Double Semicolon (Cursor Editor):**ta
;; (
;;    'song_id'
;;    (
;;       'name'
;;       "Song Title"
;    )**Direct Format (Various Editors):**ta
;; (song_id
;;    (
;;       'name'
;;       "Song Title"
;;    )### 🔍 Detection Logic

The script automatically detects and handles:
- Lines starting with `;` (single semicolon)
- Lines starting with `;;` (double semicolon)
- Mixed comment styles within the same file
- Preserves original comment style in output

## 📝 Examples

### Example 1: First Run

$ python3 extract_disabled_songs.py
Processing songs.dta...
Found commented-out song: 'Why' by Ayaka (Album: Crisis Core: Final Fantasy VII) [ayakawhy_sky]
Found commented-out song: 'Somebody That I Used to Know' by Gotye (Album: Making Mirrors) [somebodythatiusedv3]
Found commented-out song: 'Rolling in the Deep' by Adele (Album: 21) [rollinginthedeep]

Writing 3 disabled songs to songs.disabled.dta...
Writing cleaned songs.dta...
Creating backup: songs.dta.backup
Done!
- 3 song definitions moved to songs.disabled.dta
- Original file backed up as songs.dta.backup### Example 2: Subsequent Run

$ python3 extract_disabled_songs.py
Processing songs.dta...
Found commented-out song: 'Bohemian Rhapsody' by Queen (Album: A Night at the Opera) [bohemianrhapsody]

Writing 1 disabled songs to songs.disabled.dta...
Writing cleaned songs.dta...
Backup songs.dta.backup already exists, not overwriting
Done!
- 1 song definitions moved to songs.disabled.dta
- Original file backed up as songs.dta.backup### Example 3: No Disabled Songs

$ python3 extract_disabled_songs.py
Processing songs.dta...
No commented-out songs found to extract.
Writing cleaned songs.dta...
Backup songs.dta.backup already exists, not overwriting
Done!
- Original file backed up as songs.dta.backup## 🛡️ Safety Features

### Automatic Backups
- Creates `songs.dta.backup` on first run
- Preserves existing backup files
- Never overwrites backups

### Data Integrity
- Only processes complete song definition blocks
- Preserves all non-song comments
- Maintains original file encoding

### Error Handling
- Graceful handling of malformed files
- Clear error messages for missing files
- Continues processing despite encoding issues

### Non-Destructive Operation
- Never deletes data without backup
- Allows easy restoration
- Preserves file timestamps

## 🔧 Troubleshooting

### Script Won't Run

**Problem:** `python3: command not found`

**Solution:**
# Check if Python is installed
python --version

# Try different Python commands
python3 extract_disabled_songs.py
python extract_disabled_songs.py
/usr/bin/python3 extract_disabled_songs.py### No Songs Detected

**Problem:** Script reports "No commented-out songs found"

**Solutions:**
1. **Check comment style**: Ensure songs are commented with `;` or `;;`
2. **Verify format**: Songs must start with `; (` and end with `; )`
3. **Check file location**: Script must be in same directory as `songs.dta`

### Permission Errors

**Problem:** `Permission denied` when writing files

**Solutions:**
# Make script executable
chmod +x extract_disabled_songs.py

# Check directory permissions
ls -la songs.dta
chmod 644 songs.dta### Encoding Issues

**Problem:** Strange characters in output

**Solution:** The script handles UTF-8 encoding automatically. If issues persist, check your `songs.dta` file encoding.

### Restore from Backup

**Problem:** Need to restore original file

**Solution:**
# Restore from backup
cp songs.dta.backup songs.dta## 🔬 Technical Details

### Dependencies
- **Python Standard Library only** (no external dependencies)
- Uses `os`, `sys`, `re`, and `datetime` modules

### Performance
- **Memory efficient**: Processes files line-by-line
- **Fast execution**: Handles large files (287K+ lines) in seconds
- **Minimal I/O**: Single pass through input file

### Limitations
- Only processes `.dta` files with specific comment patterns
- Requires songs to be properly commented-out (not just individual lines)
- Preserves original comment style in archive

### Compatibility
- **Python 3.6+** required
- **Cross-platform**: Windows, macOS, Linux
- **Editor agnostic**: Works with any text editor's comment style

### Supported Comment Formats

1. **Single semicolon - separate lines:** `; (` followed by song ID on next line
2. **Single semicolon - Cursor format:** `; ('song_id'` on same line  
3. **Double semicolon - separate lines:** `;; (` followed by song ID on next line
4. **Double semicolon - Cursor format:** `;; ('song_id'` on same line
5. **Double semicolon - direct format:** `;; (song_id` (song ID directly after parenthesis)

---

## 📞 Support

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Verify your `songs.dta` file format
3. Ensure proper Python installation
4. Check file permissions

## 🤝 Contributing

To modify or improve the script:
- Test changes with sample data
- Maintain backward compatibility
- Update this README for any new features

---

*This script helps optimize Rock Band 3 Deluxe performance while preserving your complete song library archive.*