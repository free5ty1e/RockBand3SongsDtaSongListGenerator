# RockBand3SongsDtaSongListGenerator

Rock Band 3 `songs.dta` song list generator for parties.

I run [Rock Band 3 Deluxe](https://rb3dx.milohax.org/) on a PS3 at parties and maintain a large custom `songs.dta`. Guests like browsing songs on their phones to plan what to play next. This Python 3 tool parses the `songs.dta` and produces sharable, human-friendly lists.

## Features

- Robust parsing of large `songs.dta` files (handles quoted strings, single-quoted atoms, and comments)
- Extracts artist, song name, album name (if present), year released, and song length
- Generates four text files:
  - `SongListSortedByArtist.txt` — sorted by artist, then album, then song name
  - `SongListSortedBySongName.txt` — sorted by song name, then artist
  - `SongListSortedByArtistClean.txt` — same as artist list, with profanity-filtered lines removed
  - `SongListSortedBySongNameClean.txt` — same as song-name list, with profanity-filtered lines removed
- Summary at the end: entries parsed, extracted pairs, missing counts, lines written, clean-file stats, and per-term profanity counts
- Logs partial/malformed entries (with song identifier) to help diagnose parsing issues

## Requirements

- Python 3.8+

## Usage

```bash
python3 generate_song_lists.py /path/to/songs.dta
```

Notes:
- Input may be a standard `songs.dta` or a text export (e.g., `songs.dta.txt`).
- The script writes outputs into the current working directory.

## Output format

- `SongListSortedByArtist.txt`
  - Line format: `artist (album) - name (year_released / mm:ss)`
  - Sorted by artist → album → name

- `SongListSortedBySongName.txt`
  - Line format: `name by artist on album (year_released / mm:ss)`
  - Sorted by name → artist

Placeholders when data is missing:
- Album: `(unknown album)`
- Year: `?`
- Length: `?:??` (length is interpreted as milliseconds in the DTA and converted to mm:ss)

## Clean outputs and profanity filtering

Two additional files exclude lines containing configured profanity (case-insensitive):
- `SongListSortedByArtistClean.txt`
- `SongListSortedBySongNameClean.txt`

The filter uses a combined approach:
- Simple substrings (e.g., `shit`, `bitch`, `asshole`, `bastard`, `damn`, etc.)
- Regexes with word boundaries for risky matches (e.g., `\bdick\b`, `\bcock\b`)

Every filtered line is logged with the specific matching terms. The summary includes per-term counts so you can refine the list.

### Customizing the word list

Edit the lists near the top of `generate_song_lists.py`:
- `CURSE_WORDS`: simple case-insensitive substrings
- `CURSE_REGEX_PATTERNS`: regex patterns (compiled with `re.IGNORECASE`)


## Console logging and summary

The script prints:
- Warnings if no (artist, name) pairs were found
- Partial entries with missing fields in the form: `id=<identifier> | artist=<...> | name=<...> | album=<...> | year=<...> | length=<...>`
- Final summary with counts for total parsed, extracted pairs, skipped entries, lines written for each file, and clean-file filtering stats (including per-term counts)

## Troubleshooting

- Unexpectedly low entry count:
  - The parser skips quoted strings, single-quoted atoms, and `;` comments while tracking parentheses depth. If your DTA has unusual formatting, share an example entry to refine the parser.
- Missing data for some entries:
  - The tool includes entries even when only one of artist/name is available, using placeholders so lists remain comprehensive.
- Garbled characters:
  - Input is read as UTF-8 with replacement for invalid sequences (`errors='replace'`). Provide a properly encoded export if possible.

## Example outputs

`SongListSortedByArtist.txt`:
```
Foreigner (Agent Provocateur) - I Want to Know What Love Is (1984 / 5:16)
Foreigner (Double Vision) - Blue Morning, Blue Day (1978 / ?:??)
Foreigner (Double Vision) - Double Vision (1978 / 4:00)
Foreigner (Double Vision) - Hot Blooded (1978 / 4:45)
Foreigner (Foreigner) - Feels Like the First Time (1977 / ?:??)
Foreigner (Foreigner) - Headknocker (1977 / ?:??)
Foster the People (Torches) - Don't Stop (Color on the Walls) (2011 / 2:58)
Foster the People (Torches) - Helena Beat (2011 / 4:33)
Foster the People (Torches) - Pumped Up Kicks (2011 / 3:57)
Fountains of Wayne (Welcome Interstate Managers) - Stacy's Mom (2003 / 3:21)
Frank Sinatra (It Might as Well Be Swing) - Fly Me to the Moon (In Other Words) (1964 / 2:37)
Frank Sinatra (My Way) - My Way (1969 / 4:49)
```

`SongListSortedBySongName.txt`
```
29 Fingers by The Konks on (unknown album) (? / ?:??)
3's & 7's by Queens of the Stone Age on (unknown album) (? / ?:??)
3rd Stone from the Sun by The Jimi Hendrix Experience on Are You Experienced (1967 / 6:50)
5 Minutes Alone by Pantera on Far Beyond Driven (1994 / 5:58)
7 Things by Miley Cyrus on Breakout (2008 / 3:33)
867-5309/Jenny by Tommy Tutone on Tutone-Ality (1981 / 3:48)
```




# Other Tools
See the other tools folder for README files for each specific related tool / toolset
