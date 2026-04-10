# SNG Decrypter

The SNG Decrypter is a Python tool used to extract and decrypt song data from `.sng` files, which are used by Rock Band 4 and similar games.

## Overview

`.sng` files are custom archives that use a specific XOR-based masking algorithm to protect their contents. This tool implements the decryption logic found in the Nautilus open-source project, allowing users to recover the original files (such as audio stems, MIDI data, and metadata) from an SNG archive.

## Features

- **Full SNG Parsing**: Reads the `SNGPKG` header, versioning, and XOR mask.
- **Metadata Extraction**: Extracts embedded key-value pairs and saves them as a `song.ini` file.
- **XOR Decryption**: Implements the seed-based lookup table masking algorithm to decrypt file contents.
- **Directory Reconstruction**: Automatically recreates the internal folder structure of the SNG archive on the local filesystem.

## How it Works

The decryption process follows these steps:

1. **Seed Extraction**: The tool reads the 16-byte XOR mask (seed) from the SNG header.
2. **Lookup Table Generation**: A 256-byte lookup table is generated where `loop_lookup[i] = i ^ seed[i & 0xF]`.
3. **Stream Decryption**: Each file within the archive is decrypted by XORing its bytes with the lookup table: `decrypted[i] = encrypted[i] ^ loop_lookup[i & 0xFF]`.

## Usage

### Command Line

Run the script from the terminal:

```bash
python3 sng_decrypt.py <input_sng_file> <output_directory>
```

**Example:**

```bash
python3 sng_decrypt.py song_data.sng ./extracted_song
```

### Parameters

- `<input_sng_file>`: The path to the `.sng` file you wish to decrypt.
- `<output_directory>`: The directory where the decrypted files and `song.ini` will be saved.

## Technical Details

- **File Identifier**: `SNGPKG`
- **Encryption**: XOR masking with a rolling 256-byte lookup table.
- **Language**: Python 3.x
