# PKG and PFS Structure

Rock Band 4 content is distributed via PlayStation 4 PKG files.

## PKG Extraction

PKGs are extracted using tools like `PkgTool.Core`, which reveals the underlying Package File System (PFS).

## PFS Layout

The PFS contains the actual game files. In the case of Rock Band 4:

- **DLC PKGs**: Contain `.songdta_ps4` files directly in the PFS.
- **Base Game/Update PKGs**: Instead of individual `.songdta_ps4` files, these PKGs contain `.ark` archives (e.g., `main_ps4_0.ark`), which act as a second layer of compression/archiving.

## SMB Access

For large-scale processing, PKGs are often accessed via SMB shares (e.g., `//192.168.100.135/incoming/temp/Rb4Dlc`) to avoid local disk exhaustion.
