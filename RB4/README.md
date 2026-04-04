# Rock Band 4 Custom Song List Generator

This folder contains a pipeline for scanning PS4 (fPKG) Rock Band 4 custom song packages, pulling their track metadata with Onyx, and generating a text-based, human-readable song list that mirrors the output format of the older RB3 tool in the root of this repository.

## Overview

The standard `rb4songlistWithRivals.txt` file serves as the baseline database of all default RB4 songs + Rivals expansion tracks. 
This tool supplements the baseline with your custom songs, dropping duplicates (custom files take precedence as they usually have better metadata).

## Two-Step Workflow

**1. Scan custom PKG files**
Run the shell script to recursively scan a folder full of `.pkg` files and generate a metadata JSON file:
```bash
./RB4/scripts/scan_rb4_pkgs.sh --dir /path/to/pkgs --out RB4/rb4_custom_songs.json
```
_Note: We use `xvfb-run` inside the devcontainer to handle Onyx's UI constraints frictionlessly, letting it run fully statelessly._

**2. Generate Text Lists**
Run the Node.js generator to combine the baseline files with the custom JSON data:
```bash
node RB4/generate_rb4_song_list.js --baseline RB4/rb4songlistWithRivals.txt --custom RB4/rb4_custom_songs.json
```

This generates 4 text files in `RB4/output/`:
- `RB4SongListSortedByArtist.txt`
- `RB4SongListSortedBySongName.txt`
- `RB4SongListSortedByArtistClean.txt` (profanity filtered)
- `RB4SongListSortedBySongNameClean.txt` (profanity filtered)

## Output Format
```
Artist (Album) - Song Title (Year / MM:SS) - Source
```
Example:
```
50 Cent (Get Rich Or Die Tryin') - In Da Club (2003 / 3:30) - Custom
```

## Setup (Devcontainer)
You can bring up this repo inside its VS Code Devcontainer, which properly comes equipped with Node.js 22, Python 3, `Onyx CLI`, and Xorg dependencies (`xvfb`) necessary for headless custom pkg parsing.
Make sure to mount your local PKG path securely in your `.devcontainer/devcontainer.json`.
