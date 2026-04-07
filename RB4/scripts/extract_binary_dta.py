#!/usr/bin/env python3
"""
extract_binary_dta.py — Extract song metadata from Rock Band 4 binary .songdta_ps4 files.
Uses exact field offsets from LibForge's 010 Editor template.
"""

import sys
import json
import os
import argparse
import struct

_FRIENDLY_SOURCES = {
    'rb1': 'Rock Band 1', 'rb2': 'Rock Band 2', 'rb3': 'Rock Band 3',
    'rb1_dlc': 'Rock Band 1 DLC', 'rb2_dlc': 'Rock Band 2 DLC', 'rb3_dlc': 'Rock Band 3 DLC',
    'rb4_dlc': 'Rock Band 4 DLC', 'rbn1': 'Rock Band Network 1', 'rbn2': 'Rock Band Network 2',
    'greenday': 'Rock Band Green Day', 'beatles': 'The Beatles: Rock Band',
    'gdrb': 'Rock Band Green Day', 'tbrb': 'The Beatles: Rock Band',
    'ugc_plus': 'Custom', 'ugc': 'Custom', 'custom': 'Custom',
    'legacy_rbn': 'Rock Band Network 1', 'rbn': 'Rock Band Network 1',
    'lego': 'LEGO Rock Band', 'legorockband': 'LEGO Rock Band',
}

_INSTRUMENT_EMOJI = {
    'guitar': '🎸',
    'bass': '🎸',
    'drums': '🥁',
    'vocals': '🎤',
    'keys': '🎹',
    'real_guitar': '🎸',
    'real_keys': '🎹',
}

# Field offsets from LibForge 010/songdta.bt template
OFFSETS = {
    'songdta_type': 0,
    'song_id': 4,
    'version': 8,
    'game_origin': 10,
    'preview_start': 28,
    'preview_end': 32,
    'name': 36,
    'artist': 292,
    'album_name': 548,
    'album_track_number': 804,
    'album_year': 808,
    'original_year': 812,
    'genre': 816,
    'song_length': 880,
    'guitar': 884,
    'bass': 888,
    'vocals': 892,
    'drum': 896,
    'band': 900,
    'keys': 904,
    'real_keys': 908,
    'tutorial': 912,
    'album_art': 913,
    'cover': 914,
    'vocal_gender': 915,
    'anim_tempo': 916,
    'has_markup': 932,
    'vocal_parts': 936,
    'solos': 940,
    'fake': 944,
    'shortname': 945,
}

SIZES = {
    'game_origin': 18,
    'name': 256,
    'artist': 256,
    'album_name': 256,
    'genre': 64,
    'anim_tempo': 16,
    'shortname': 256,
}


def _read_string(data: bytes, offset: int, max_size: int) -> str:
    """Read a null-terminated UTF-8 string from binary data."""
    try:
        if offset + max_size > len(data):
            return ""
        chunk = data[offset:offset + max_size]
        return chunk.split(b'\x00')[0].decode('utf-8', errors='replace').strip()
    except Exception:
        return ""


def _read_int(data: bytes, offset: int) -> int:
    """Read a 4-byte little-endian integer."""
    try:
        if offset + 4 > len(data):
            return 0
        return struct.unpack('<I', data[offset:offset + 4])[0]
    except Exception:
        return 0


def _read_short(data: bytes, offset: int) -> int:
    """Read a 2-byte little-endian short."""
    try:
        if offset + 2 > len(data):
            return 0
        return struct.unpack('<h', data[offset:offset + 2])[0]
    except Exception:
        return 0


def _read_float(data: bytes, offset: int) -> float:
    """Read a 4-byte float."""
    try:
        if offset + 4 > len(data):
            return 0.0
        return struct.unpack('<f', data[offset:offset + 4])[0]
    except Exception:
        return 0.0


def _read_byte(data: bytes, offset: int) -> int:
    """Read a single byte."""
    if offset >= len(data):
        return 0
    return data[offset]


def _scan_for_strings(data: bytes, min_len: int = 3) -> dict:
    """Scan binary data for embedded strings at known positions."""
    result = {
        'shortname': '',
        'name': '',
        'artist': '',
        'album': '',
        'genre': '',
    }
    
    # Try to find strings using common patterns
    # Look for null-terminated strings in typical ranges
    
    # Shortname is usually at offset 945, length 256
    result['shortname'] = _read_string(data, 945, 256)
    
    # Name/title at offset 36, length 256
    result['name'] = _read_string(data, 36, 256)
    
    # Artist at offset 292, length 256
    result['artist'] = _read_string(data, 292, 256)
    
    # Album at offset 548, length 256
    result['album'] = _read_string(data, 548, 256)
    
    # Genre at offset 816, length 64
    result['genre'] = _read_string(data, 816, 64)
    
    return result


def _try_alternative_parsing(filepath: str, data: bytes, default_source: str) -> dict:
    """Try alternative parsing methods for corrupted/truncated binary data."""
    result = {
        'artist': '',
        'title': '',
        'album': '',
        'year': 0,
        'durationMs': 0,
        'source': default_source,
        'songId': 0,
        'shortName': '',
        'gameOrigin': '',
        'albumYear': 0,
        'originalYear': 0,
        'albumTrackNumber': 0,
        'genre': '',
        'previewStart': 0.0,
        'previewEnd': 0.0,
        'difficulty': {'guitar': 0.0, 'bass': 0.0, 'vocals': 0.0, 'drums': 0.0, 'band': 0.0, 'keys': 0.0, 'realKeys': 0.0},
        'instruments': '',
        'instrumentList': [],
        'tutorial': 0,
        'albumArt': 0,
        'cover': 0,
        'vocalGender': 'Unknown',
        'animTempo': '',
        'hasMarkup': 0,
        'vocalParts': 0,
        'fake': 0,
        'songdtaType': 0,
        'version': 0,
        '_debug_file': os.path.basename(filepath),
        'parse_mode': 'alternative_scan'
    }
    
    # Scan for strings using alternative method
    scanned = _scan_for_strings(data)
    
    # Only use scanned strings if they look valid
    if scanned['shortname'] and len(scanned['shortname']) >= 3:
        result['shortName'] = scanned['shortname']
        result['title'] = scanned['name'] or scanned['shortname']
        result['artist'] = scanned['artist']
        result['album'] = scanned['album']
        result['genre'] = scanned['genre']
    
    # Try to find year in the data
    for offset in [808, 812, 816]:
        if offset + 4 <= len(data):
            try:
                year = struct.unpack('<I', data[offset:offset+4])[0]
                if 1900 <= year <= 2030:
                    result['year'] = year
                    result['albumYear'] = year
                    result['originalYear'] = year
                    break
            except:
                pass
    
    # Try to find duration
    result['durationMs'] = _calculate_duration_ms(data)
    
    return result


def _calculate_duration_ms(data: bytes) -> int:
    """Calculate duration from floats in the file. Find min float in range 60-500 as duration."""
    floats_in_range = []
    for i in range(0, len(data) - 4, 4):
        try:
            val = struct.unpack('<f', data[i:i+4])[0]
            if 60.0 <= val <= 500.0:
                floats_in_range.append(val)
        except Exception:
            pass
    
    if floats_in_range:
        duration_seconds = min(floats_in_range)
        return int(duration_seconds * 1000)
    return 0


def parse_songdta(filepath: str, default_source: str = "Custom") -> dict:
    """Parse .songdta_ps4 file using exact field offsets."""
    with open(filepath, 'rb') as f:
        data = f.read()

    if len(data) < 100:
        return _create_empty_result(filepath, default_source)

    # === EXTRACT ALL FIELDS ===
    
    # Basic identification
    songdta_type = _read_int(data, OFFSETS['songdta_type'])
    song_id = _read_int(data, OFFSETS['song_id'])
    version = _read_short(data, OFFSETS['version'])
    game_origin = _read_string(data, OFFSETS['game_origin'], SIZES['game_origin'])
    shortname = _read_string(data, OFFSETS['shortname'], SIZES['shortname'])
    
    # Core metadata
    name = _read_string(data, OFFSETS['name'], SIZES['name'])
    artist = _read_string(data, OFFSETS['artist'], SIZES['artist'])
    
    # If basic fields are empty, try alternative parsing
    if not name and not artist and not shortname:
        # This might be a truncated file or different format - try alternative
        alt_result = _try_alternative_parsing(filepath, data, default_source)
        # Only use it if we got something useful
        if alt_result.get('title') or alt_result.get('shortName'):
            return alt_result
    
    # Preview times
    preview_start = _read_float(data, OFFSETS['preview_start'])
    preview_end = _read_float(data, OFFSETS['preview_end'])
    
    # Core metadata
    name = _read_string(data, OFFSETS['name'], SIZES['name'])
    artist = _read_string(data, OFFSETS['artist'], SIZES['artist'])
    album_name = _read_string(data, OFFSETS['album_name'], SIZES['album_name'])
    album_track_number = _read_short(data, OFFSETS['album_track_number'])
    album_year = _read_int(data, OFFSETS['album_year'])
    original_year = _read_int(data, OFFSETS['original_year'])
    genre = _read_string(data, OFFSETS['genre'], SIZES['genre'])
    
    # Song length - try multiple methods
    duration_ms = _calculate_duration_ms(data)
    
    # Fallback 1: try uint32 at offset 880 as milliseconds
    if duration_ms == 0:
        try:
            val = struct.unpack('<I', data[880:884])[0]
            if 60000 <= val <= 600000:  # 1-10 minutes in ms
                duration_ms = val
        except:
            pass
    
    # Fallback 2: try float at guitar offset (could be duration in seconds)
    if duration_ms == 0:
        duration_float = _read_float(data, OFFSETS['guitar'])
        if 60.0 <= duration_float <= 500.0:
            duration_ms = int(duration_float * 1000)
    
    # Fallback 3: scan entire file for float in reasonable range (for truncated WIP files)
    if duration_ms == 0:
        for i in range(len(data) - 4):
            try:
                val = struct.unpack('<f', data[i:i+4])[0]
                if 30.0 <= val <= 600.0:  # 30 seconds to 10 minutes
                    duration_ms = int(val * 1000)
                    break
            except:
                pass
    
    # Difficulty ratings (as floats)
    guitar = _read_float(data, OFFSETS['guitar'])
    bass = _read_float(data, OFFSETS['bass'])
    vocals = _read_float(data, OFFSETS['vocals'])
    drum = _read_float(data, OFFSETS['drum'])
    band = _read_float(data, OFFSETS['band'])
    keys = _read_float(data, OFFSETS['keys'])
    real_keys = _read_float(data, OFFSETS['real_keys'])
    
    # Additional metadata
    tutorial = _read_byte(data, OFFSETS['tutorial'])
    album_art = _read_byte(data, OFFSETS['album_art'])
    cover = _read_byte(data, OFFSETS['cover'])
    vocal_gender = _read_byte(data, OFFSETS['vocal_gender'])
    anim_tempo = _read_string(data, OFFSETS['anim_tempo'], 16)
    has_markup = _read_byte(data, OFFSETS['has_markup'])
    vocal_parts = _read_byte(data, OFFSETS['vocal_parts'])
    fake = _read_byte(data, OFFSETS['fake'])
    
    # === DERIVE ADDITIONAL FIELDS ===
    
    # Year: prefer original year, fallback to album year
    year = original_year if original_year > 0 else album_year
    
    # Source: map game_origin to friendly name
    source = _FRIENDLY_SOURCES.get(game_origin.lower(), default_source)
    
    # Instruments: based on difficulty values > 0
    instruments = []
    if guitar > 0:
        instruments.append("guitar")
    if bass > 0:
        instruments.append("bass")
    if vocals > 0:
        instruments.append("vocals")
    if drum > 0:
        instruments.append("drums")
    if keys > 0:
        instruments.append("keys")
    if real_keys > 0:
        instruments.append("real_keys")
    
    # Instruments emoji string
    instruments_str = ''.join(_INSTRUMENT_EMOJI.get(i, '') for i in instruments)
    
    # Vocal gender text
    vocal_gender_str = "Male" if vocal_gender == 1 else "Female" if vocal_gender == 2 else "Unknown"
    
    return {
        # Core metadata
        "artist": artist,
        "title": name,
        "album": album_name,
        "year": year,
        "durationMs": duration_ms,
        "source": source,
        
        # Identification
        "songId": song_id,
        "shortName": shortname,
        "gameOrigin": game_origin,
        
        # Album details
        "albumYear": album_year,
        "originalYear": original_year,
        "albumTrackNumber": album_track_number,
        
        # Genre and classification
        "genre": genre,
        
        # Preview info
        "previewStart": preview_start,
        "previewEnd": preview_end,
        
        # Difficulty ratings
        "difficulty": {
            "guitar": guitar,
            "bass": bass,
            "vocals": vocals,
            "drums": drum,
            "band": band,
            "keys": keys,
            "realKeys": real_keys,
        },
        
        # Instrument icons
        "instruments": instruments_str,
        "instrumentList": instruments,
        
        # Additional metadata
        "tutorial": tutorial,
        "albumArt": album_art,
        "cover": cover,
        "vocalGender": vocal_gender_str,
        "animTempo": anim_tempo,
        "hasMarkup": has_markup,
        "vocalParts": vocal_parts,
        "fake": fake,
        
        # Technical
        "songdtaType": songdta_type,
        "version": version,
        
        # Debug
        "_debug_file": os.path.basename(filepath),
        "parse_mode": "exact_offsets"
    }


def _create_empty_result(filepath: str, default_source: str) -> dict:
    """Create an empty result for invalid files."""
    return {
        "artist": "Unknown",
        "title": os.path.basename(filepath).replace('.songdta_ps4', ''),
        "album": "",
        "year": 0,
        "durationMs": 0,
        "source": default_source,
        "songId": 0,
        "shortName": "",
        "gameOrigin": "",
        "albumYear": 0,
        "originalYear": 0,
        "albumTrackNumber": 0,
        "genre": "",
        "previewStart": 0.0,
        "previewEnd": 0.0,
        "difficulty": {},
        "instruments": "",
        "instrumentList": [],
        "tutorial": 0,
        "albumArt": 0,
        "cover": 0,
        "vocalGender": "Unknown",
        "animTempo": "",
        "hasMarkup": 0,
        "vocalParts": 0,
        "fake": 0,
        "songdtaType": 0,
        "version": 0,
        "_debug_file": os.path.basename(filepath),
        "parse_mode": "exact_offsets"
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', nargs='+', help='Input directories or files')
    parser.add_argument('--source', default='Custom', help='Default source name')
    parser.add_argument('output', help='Output JSON file')
    args = parser.parse_args()

    results = []
    files = []
    for path in args.input:
        if os.path.isdir(path):
            for root, dirs, fnames in os.walk(path):
                for f in fnames:
                    if f.endswith('.songdta_ps4'):
                        files.append(os.path.join(root, f))
        else:
            files.append(path)

    print(f"\tFound {len(files)} .songdta_ps4 files to process...")
    
    for i, filepath in enumerate(files):
        print(f"\t[{i+1}/{len(files)}] Processing {os.path.basename(filepath)}...")
        try:
            result = parse_songdta(filepath, args.source)
            results.append(result)
        except Exception as e:
            print(f"\tERROR parsing {filepath}: {e}", file=sys.stderr)

    print(f"\tDone. Extracted {len(results)} songs.")
    print(f"\tWriting to {args.output}...")
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    print("\tDone!")


if __name__ == '__main__':
    main()
