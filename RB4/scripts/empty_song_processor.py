#!/usr/bin/env python3
"""Empty song processor - shared logic for applying baseline fallback to metadata."""

import json
import os

BASELINE_PATH = '/workspace/RB4/rb4_empty_songs_full.json'

def load_empty_songs_baseline(baseline_path=None):
    """Load the pre-identified empty songs baseline.
    
    Returns dict: {short_filename: {'title': ..., 'artist': ...}}
    """
    path = baseline_path or BASELINE_PATH
    if os.path.exists(path):
        try:
            with open(path) as f:
                data = json.load(f)
                return {
                    s['short_filename']: {
                        'title': s.get('probable_title'), 
                        'artist': s.get('probable_artist'),
                        'instrumentList': s.get('instrumentList', []),
                        'vocalParts': s.get('vocalParts', 0)
                    } 
                    for s in data if 'short_filename' in s
                }
        except Exception as e:
            print(f"Warning: Failed to load empty songs baseline: {e}")
    return {}

def apply_empty_song_fallback(songs, baseline=None):
    """Apply baseline fallback to songs with empty metadata.
    
    For each song without artist/title, tries to find matching info
    in the baseline using _debug_file (filename) as the key.
    
    Args:
        songs: List of song dicts
        baseline: Optional pre-loaded baseline dict
        
    Returns:
        List of songs with fallback applied
    """
    if baseline is None:
        baseline = load_empty_songs_baseline()
    
    if not baseline:
        return songs
    
    for song in songs:
        filename = song.get('_debug_file', '')
        short_name = filename.replace('.songdta_ps4', '')
        
        if short_name in baseline:
                baseline_info = baseline[short_name]
                current_title = song.get('title')
                current_artist = song.get('artist')
                current_inst = song.get('instrumentList', [])
                current_vp = song.get('vocalParts', 0)
                
                # Apply fallback for any missing data
                if not current_title or current_title == short_name:
                    song['title'] = baseline_info.get('title') or current_title
                if not current_artist or current_artist == 'Unknown':
                    song['artist'] = baseline_info.get('artist') or current_artist
                # Copy instruments if not present or empty
                if (not current_inst or len(current_inst) == 0) and baseline_info.get('instrumentList'):
                    song['instrumentList'] = baseline_info['instrumentList']
                if not current_vp and baseline_info.get('vocalParts'):
                    song['vocalParts'] = baseline_info['vocalParts']
                song['inferred'] = True
    
    return songs

def get_songs_with_fallback(metadata_dir, baseline=None):
    """Load all metadata JSONs from a directory and apply fallback.
    
    Args:
        metadata_dir: Directory containing metadata_*.json files
        baseline: Optional pre-loaded baseline
        
    Returns:
        List of all songs with fallback applied
    """
    import glob
    
    if baseline is None:
        baseline = load_empty_songs_baseline()
    
    songs = []
    for f in sorted(glob.glob(os.path.join(metadata_dir, 'metadata_*.json'))):
        # Add pkg filename from metadata filename
        pkg_name = os.path.basename(f).replace('metadata_', '').replace('.json', '')
        with open(f) as fp:
            loaded_songs = json.load(fp)
        # Add pkg to ALL songs in this file
        for song in loaded_songs:
            song['_pkg_file'] = pkg_name
        songs.extend(loaded_songs)
    
    return apply_empty_song_fallback(songs, baseline)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: empty_song_processor.py <metadata_dir> [output.json]")
        sys.exit(1)
    
    metadata_dir = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    songs = get_songs_with_fallback(metadata_dir)
    print(f"Total songs with fallback: {len(songs)}")
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(songs, f, indent=2)
        print(f"Wrote: {output_file}")
