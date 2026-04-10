# ARK Archive Format

The base game and update PKGs utilize `.ark` archives to store game data.

## Versions

The following ARK versions have been identified:

- `0x4B5241` ("ARK"): Old format.
- `257`: A modified version of the old format.
- `16`, `14`, `4`: Newer format versions.

## Observed Patterns

### String Storage

Strings in `.ark` files frequently follow a length-prefixed pattern:

- **Format**: `[Length (uint32, Little Endian)] [String (ASCII/UTF-8)]`
- Example: `gtrsolo_tutorial` is stored as `\x10\x00\x00\x00gtrsolo_tutorial`.

### File Table

The `.ark` files contain a file table that maps filenames to offsets and sizes. In the newer formats, this table includes offsets, flags, and sizes.

### Base Game Layout

The base game extract typically contains:

- `main_ps4.hdr`: Header file for the ARK collection.
- `main_ps4_0.ark` through `main_ps4_15.ark`: The actual archive shards.
