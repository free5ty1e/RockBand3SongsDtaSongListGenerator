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
- Optional support for multiple input `songs.dta` files; merged outputs include source filename metadata (e.g., `(songs.usb1.dta)`)

## Requirements

- Python 3.8+

## Usage

```bash
python3 generate_song_lists.py /path/to/songs.dta
```

### Multiple Input Files

For multiple input files (merged lists with source filename metadata):

```bash
python3 generate_song_lists.py /path/to/songs.dta /path/to/songs.USB1.dta /path/to/songs.USB2.dta
```

Notes:

- Input may be a standard `songs.dta` or a text export (e.g., `songs.dta.txt`).
- The script writes outputs into the current working directory.

## Output format

- `SongListSortedByArtist.txt`
  - Line format: `artist (album) - name (year_released / mm:ss) (source.dta)`
  - Sorted by artist → album → name

- `SongListSortedBySongName.txt`
  - Line format: `name by artist on album (year_released / mm:ss) (source.dta)`
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
Foreigner (Agent Provocateur) - I Want to Know What Love Is (1984 / 5:16) (songs.dta)
Foreigner (Double Vision) - Blue Morning, Blue Day (1978 / ?:??) (songs.dta)
Foreigner (Double Vision) - Double Vision (1978 / 4:00) (songs.dta)
Foreigner (Double Vision) - Hot Blooded (1978 / 4:45) (songs.dta)
Foreigner (Foreigner) - Feels Like the First Time (1977 / ?:??) (songs.dta)
Foreigner (Foreigner) - Headknocker (1977 / ?:??) (songs.dta)
Foster the People (Torches) - Don't Stop (Color on the Walls) (2011 / 2:58) (songs.USB1.dta)
Foster the People (Torches) - Helena Beat (2011 / 4:33) (songs.USB1.dta)
Foster the People (Torches) - Pumped Up Kicks (2011 / 3:57) (songs.USB1.dta)
Fountains of Wayne (Welcome Interstate Managers) - Stacy's Mom (2003 / 3:21) (songs.dta)
Frank Sinatra (It Might as Well Be Swing) - Fly Me to the Moon (In Other Words) (1964 / 2:37) (songs.dta)
Frank Sinatra (My Way) - My Way (1969 / 4:49) (songs.dta)
```

`SongListSortedBySongName.txt`

```
29 Fingers by The Konks on (unknown album) (? / ?:??) (songs.dta)
3's & 7's by Queens of the Stone Age on (unknown album) (? / ?:??) (songs.dta)
3rd Stone from the Sun by The Jimi Hendrix Experience on Are You Experienced (1967 / 6:50) (songs.dta)
5 Minutes Alone by Pantera on Far Beyond Driven (1994 / 5:58) (songs.USB1.dta)
7 Things by Miley Cyrus on Breakout (2008 / 3:33) (songs.dta)
867-5309/Jenny by Tommy Tutone on Tutone-Ality (1981 / 3:48) (songs.dta)
```

## Rock Band 4 Support

To build song lists for Rock Band 4 and user custom PKGs, please refer to the specific toolset in the `RB4/` directory. See the [RB4 README](./RB4/README.md) for its specific setup and pipeline documentation.

## Local Ollama Models

This project includes support for running local AI models via [Ollama](https://ollama.com/). This keeps your code local and private — no data leaves your machine.

### Available Models

The following agent-capable models are configured (support tool calling):

| Model | Size | Purpose |
|-------|------|---------|
| qwen2.5-coder:7b | ~4.4GB | Fast code generation |
| deepseek-coder-v2:16b | ~9GB | GPT4-Turbo class coding |
| qwen3:8b | ~8GB | General purpose |
| mistral-nemo:12b | ~12GB | Reasoning and analysis |

**Total: ~33GB** (all models)

### Adding/Changing Models

Models are defined in one place: [`.devcontainer/ollama_models.conf`](.devcontainer/ollama_models.conf)

To add or change models:

1. Edit `.devcontainer/ollama_models.conf` (format: `["model:name"]="description|size"`)
2. Update [`.vscode/tasks.json`](.vscode/tasks.json) tasks for new models
3. Update [`opencode.json`](opencode.json) with new model entries
4. Run `bash .devcontainer/check_models.sh` to verify sync

### Checking Config Sync

Run the validation script to ensure all configs are consistent:

```bash
bash .devcontainer/check_models.sh
```

This checks that every model in `ollama_models.conf` exists in both `tasks.json` and `opencode.json`.

### Ollama Tasks

- **`Ollama: Pull Models`** — Downloads selected models (~33GB total)
  - First prompt: Install all models? (A/n)
  - If 'n': individual prompts for each model with size/description
  - Can also set via env var: `OLLAMA_MODELS='model1 model2' bash .devcontainer/setup_ollama.sh`

- **`Ollama: Start Server`** — Starts Ollama server (idempotent — safe to run multiple times)

- **`Opencode + Ollama: <model>`** — Starts server + launches opencode with that model
  - Auto-selects any installed model as your coding assistant
  - Run from VS Code: `Tasks: Run Task` → select the model you want

### Manual Ollama Usage

```bash
# Start Ollama server
bash .devcontainer/start_ollama.sh

# Pull specific model
ollama pull qwen2.5-coder:7b

# Run opencode with local model
opencode /workspace --model ollama/qwen2.5-coder:7b

# List installed models
ollama list
```

### Notes

- Ollama downloads are cached — if a model fails mid-download, re-running will resume
- Models persist in Ollama storage, not in the container — survives rebuilds
- Port 11434 is forwarded for Ollama API access

# Other Tools

See the other tools folder for README files for each specific related tool / toolset
