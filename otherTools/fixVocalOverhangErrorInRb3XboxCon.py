#!/usr/bin/env python3
"""
RB3 Xbox CON → Auto-fix HARM1/HARM2/HARM3 vocal overhang error → New CON

Fixes the infamous Magma/Onyx error:
"Vocal note at [XX:X.XXX] extends beyond phrase"

Usage examples:
    python fixVocalOverhangErrorInRb3XboxCon.py --con_file "MySong.con" --location "49:4.300"
    python fixVocalOverhangErrorInRb3XboxCon.py --con_file "Pack.con" --location "72:1.850" --track_name "PART HARM2" --onyx_path "C:\\Tools\\onyx.exe"
    python fixVocalOverhangErrorInRb3XboxCon.py --midi_file "path/to/song.mid" --location "49:4.300" --track_name "PART HARM1"

Requirements:
    pip install mido tqdm
    Extract the Onyx command-line ZIP to a folder (e.g., C:\\Program Files\\OnyxToolkit)
    (Download: https://github.com/mtolly/onyxite-customs/releases → onyx-command-line-*.zip)

Options:
    --onyx_path: Full path to onyx.exe (default: C:\\Program Files\\OnyxToolkit\\onyx.exe)
    --midi_file: Path to MIDI file (skips extraction/repacking, applies fix directly)
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path
import argparse
from tqdm import tqdm
import mido

# How much to shorten the offending note (5–15 ms is completely inaudible)
SHORTEN_MS = 10

def extract_con(con_path: Path, extract_dir: Path, onyx_path: str):
    cmd = [onyx_path, "extract", str(con_path), str(extract_dir), "--format", "rb3-ps3"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        raise RuntimeError(f"Onyx extraction failed. Return code: {result.returncode}")


def repack_con(work_dir: Path, output_con: Path, onyx_path: str):
    cmd = [onyx_path, "pack", str(work_dir), str(output_con), "--format", "rb3-ps3"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        raise RuntimeError(f"Onyx repacking failed. Return code: {result.returncode}")

def fix_vocal_overhang(con_path=None, midi_path=None, location="", track_name="PART HARM1", onyx_path=r"C:\Program Files\OnyxToolkit\onyx.exe"):
    if not con_path and not midi_path:
        print("ERROR: Must provide either con_file or midi_file")
        return
    
    if con_path and midi_path:
        print("ERROR: Cannot provide both con_file and midi_file")
        return

    meas_str, beat_frac_str = location.split(':')
    target_measure = int(meas_str)
    target_beat = float(beat_frac_str)

    use_midi_mode = midi_path is not None

    if use_midi_mode:
        # MIDI mode: use provided MIDI file directly
        midi_path = Path(midi_path).resolve()
        if not midi_path.exists():
            print(f"ERROR: MIDI file not found: {midi_path}")
            return
        
        print(f"Processing MIDI file: {midi_path.name}")
        mid_path = midi_path
        fixed = False
        
        # MIDI processing logic for MIDI mode
        mid = mido.MidiFile(mid_path)
        ppq = mid.ticks_per_beat

        print("Detailed MIDI track analysis:")
        print("=" * 50)
        
        for idx, track in enumerate(mid.tracks):
            print(f"\nTrack {idx}:")
            
            # Collect all text events
            text_events = [msg.text for msg in track if msg.type == 'text']
            if text_events:
                print(f"  Text events: {text_events}")
            else:
                print("  Text events: None")
            
            # Count note events
            note_on_events = sum(1 for msg in track if msg.type == 'note_on' and msg.velocity > 0)
            note_off_events = sum(1 for msg in track if msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0))
            print(f"  Notes: {note_on_events} note_on, {note_off_events} note_off")
            
            # Check for program changes (instrument assignments)
            program_changes = [msg.program for msg in track if msg.type == 'program_change']
            if program_changes:
                print(f"  Program changes: {program_changes}")
            
            # Check for lyrics events
            lyrics_events = [msg.text for msg in track if msg.type == 'lyrics']
            if lyrics_events:
                print(f"  Lyrics events: {len(lyrics_events)} found")
                # Show first few lyrics
                for i, lyric in enumerate(lyrics_events[:3]):
                    print(f"    Lyric {i+1}: '{lyric}'")
                if len(lyrics_events) > 3:
                    print(f"    ... and {len(lyrics_events) - 3} more")
            
            # Check for other relevant events
            other_events = {}
            for msg in track:
                if msg.type not in ['text', 'note_on', 'note_off', 'program_change', 'lyrics', 'set_tempo', 'time_signature', 'key_signature', 'control_change', 'end_of_track']:
                    if msg.type not in other_events:
                        other_events[msg.type] = 0
                    other_events[msg.type] += 1
            
            if other_events:
                print(f"  Other events: {other_events}")
            
            # Summary
            has_notes = note_on_events > 0
            has_lyrics = len(lyrics_events) > 0
            likely_vocal = has_notes and (has_lyrics or any('vocal' in text.lower() or 'harm' in text.lower() for text in text_events))
            print(f"  Likely vocal track: {likely_vocal}")
        
        print("=" * 50)

        # Find correct track by text event or lyrics (for vocal tracks)
        harm_track_idx = None
        for idx, track in enumerate(mid.tracks):
            # First try to find by text event
            for msg in track:
                if msg.type == 'text' and track_name.upper() in msg.text.upper():
                    harm_track_idx = idx
                    break
            
            # If not found by text, check if this is a vocal track with lyrics
            if harm_track_idx is None:
                lyrics_count = sum(1 for msg in track if msg.type == 'lyrics')
                if lyrics_count > 0:
                    # This is a vocal track - assign based on track_name
                    if track_name.upper() in ['HARM1', 'PART HARM1'] and idx == 4:
                        harm_track_idx = idx
                    elif track_name.upper() in ['HARM2', 'PART HARM2'] and idx == 5:
                        harm_track_idx = idx
                    elif track_name.upper() in ['HARM3', 'PART HARM3'] and idx == 6:
                        harm_track_idx = idx
                    elif track_name.upper() in ['VOCALS', 'PART VOCALS'] and idx == 7:
                        harm_track_idx = idx
            
            if harm_track_idx is not None:
                break
        
        if harm_track_idx is None:
            print(f"No {track_name} track found in MIDI file")
            print("Available vocal tracks (by lyrics):")
            for idx, track in enumerate(mid.tracks):
                lyrics_count = sum(1 for msg in track if msg.type == 'lyrics')
                if lyrics_count > 0:
                    print(f"  Track {idx}: {lyrics_count} lyrics events")
            return

        print(f"Processing → {track_name} found (track {harm_track_idx})")
        
        # MIDI processing logic continues...
        # Accurate time calculation using actual tempo changes
        current_time_sec = 0.0
        current_tempo = 500000  # 120 BPM default
        tick_to_sec = lambda ticks: mido.tick2second(ticks, ppq, current_tempo)

        note_start_sec = None
        note_pitch = None
        note_on_msg_idx = None

        # First pass: find the note that contains or is near the target time
        abs_sec = 0.0
        for i, msg in enumerate(mid.tracks[harm_track_idx]):
            abs_sec += tick_to_sec(msg.time)
            if msg.type == 'set_tempo':
                current_tempo = msg.tempo

            if msg.type == 'note_on' and msg.velocity > 0:
                start_sec = abs_sec
                pitch = msg.note
                # look ahead for note_off
                lookahead_sec = abs_sec
                for later_msg in mid.tracks[harm_track_idx][i+1:]:
                    lookahead_sec += tick_to_sec(later_msg.time)
                    if (later_msg.type == 'note_off' or 
                        (later_msg.type == 'note_on' and later_msg.velocity == 0)) and \
                        later_msg.note == pitch:
                        end_sec = lookahead_sec
                        break
                else:
                    end_sec = abs_sec + 1.0

                # Does this note cover or is very close to target time?
                if (abs(start_sec - (abs_sec)) < 0.2 or 
                    start_sec <= abs_sec <= end_sec + 0.1):
                    if (abs(start_sec - abs_sec) < 0.3 or 
                        (start_sec <= abs_sec <= end_sec)):
                        print(f"Found offending note: pitch {pitch}, "
                              f"{start_sec:.3f}s → {end_sec:.3f}s "
                              f"(length {(end_sec-start_sec)*1000:.1f}ms)")
                        note_start_sec = start_sec
                        note_pitch = pitch
                        note_on_msg_idx = i
                        break

        if note_pitch is None:
            print("No matching note found. Already fixed or wrong time/track name?")
            return

        # Second pass: rebuild track and shorten this note
        new_track = []
        time_acc = 0.0
        shorten_sec = SHORTEN_MS / 1000.0
        new_duration_sec = (end_sec - start_sec) - shorten_sec
        if new_duration_sec < 0.001:
            new_duration_sec = 0.001

        for msg in mid.tracks[harm_track_idx]:
            time_acc += tick_to_sec(msg.time)
            if msg.type in ['note_on', 'note_off'] and msg.note == note_pitch:
                if msg.type == 'note_on' and msg.velocity > 0:
                    # this is the note_on we want to shorten
                    new_track.append(msg)
                elif (msg.type == 'note_off' or 
                      (msg.type == 'note_on' and msg.velocity == 0)):
                    # replace note_off with one at correct earlier time
                    new_ticks = int(new_duration_sec / tick_to_sec(1) * ppq)
                    new_msg = msg.copy(time=max(1, new_ticks) if new_track else msg.time)
                    new_track.append(new_msg)
                    fixed = True
            else:
                new_track.append(msg)

        if fixed:
            mid.tracks[harm_track_idx] = new_track
            mid.save(mid_path)
            print(f"Fixed! Shortened by {SHORTEN_MS} ms")

        print(f"\nSUCCESS! Fixed MIDI file saved:\n   {mid_path}\n")
        print("You can now manually repack this into a CON file.")
    else:
        # CON mode: extract and process
        con_path = Path(con_path).resolve()
        if not con_path.exists():
            print(f"ERROR: File not found: {con_path}")
            return

        # Use a fixed working directory instead of temp
        work_dir = Path("onyx_work_temp")
        extract_dir = work_dir / "extracted"
        
        try:
            # Clean up any existing work directory
            if work_dir.exists():
                shutil.rmtree(work_dir)
            
            work_dir.mkdir(parents=True, exist_ok=True)  # Create work dir but not extracted subdir

            print(f"Extracting {con_path.name} ...")
            extract_con(con_path, work_dir, onyx_path)  # Extract directly to work_dir

            # Find song subfolders (e.g. aaaa0001, songs inside packs)
            song_folders = [p for p in work_dir.iterdir() if p.is_dir()]
            if not song_folders:
                print("No song folders found inside CON")
                return

            fixed = False
            for folder in song_folders:
                mid_candidates = list(folder.glob("*.mid")) + [folder / "song.mid"]
                mid_path = next((p for p in mid_candidates if p.exists()), None)
                if not mid_path:
                    continue

                # MIDI processing logic for CON mode
                mid = mido.MidiFile(mid_path)
                ppq = mid.ticks_per_beat

                # Find correct track by text event
                harm_track_idx = None
                for idx, track in enumerate(mid.tracks):
                    for msg in track:
                        if msg.type == 'text' and track_name.upper() in msg.text.upper():
                            harm_track_idx = idx
                            break
                    if harm_track_idx is not None:
                        break
                if harm_track_idx is None:
                    continue

                print(f"Scanning {folder.name} → {track_name} found")

                # Accurate time calculation using actual tempo changes
                current_time_sec = 0.0
                current_tempo = 500000  # 120 BPM default
                tick_to_sec = lambda ticks: mido.tick2second(ticks, ppq, current_tempo)

                note_start_sec = None
                note_pitch = None
                note_on_msg_idx = None

                # First pass: find the note that contains or is near the target time
                abs_sec = 0.0
                for i, msg in enumerate(mid.tracks[harm_track_idx]):
                    abs_sec += tick_to_sec(msg.time)
                    if msg.type == 'set_tempo':
                        current_tempo = msg.tempo

                    if msg.type == 'note_on' and msg.velocity > 0:
                        start_sec = abs_sec
                        pitch = msg.note
                        # look ahead for note_off
                        lookahead_sec = abs_sec
                        for later_msg in mid.tracks[harm_track_idx][i+1:]:
                            lookahead_sec += tick_to_sec(later_msg.time)
                            if (later_msg.type == 'note_off' or 
                                (later_msg.type == 'note_on' and later_msg.velocity == 0)) and \
                                later_msg.note == pitch:
                                end_sec = lookahead_sec
                                break
                        else:
                            end_sec = abs_sec + 1.0

                        # Does this note cover or is very close to target time?
                        if (abs(start_sec - (abs_sec)) < 0.2 or 
                            start_sec <= abs_sec <= end_sec + 0.1):
                            if (abs(start_sec - abs_sec) < 0.3 or 
                                (start_sec <= abs_sec <= end_sec)):
                                print(f"Found offending note: pitch {pitch}, "
                                      f"{start_sec:.3f}s → {end_sec:.3f}s "
                                      f"(length {(end_sec-start_sec)*1000:.1f}ms)")
                                note_start_sec = start_sec
                                note_pitch = pitch
                                note_on_msg_idx = i
                                break

                if note_pitch is None:
                    continue

                # Second pass: rebuild track and shorten this note
                new_track = []
                time_acc = 0.0
                shorten_sec = SHORTEN_MS / 1000.0
                new_duration_sec = (end_sec - start_sec) - shorten_sec
                if new_duration_sec < 0.001:
                    new_duration_sec = 0.001

                for msg in mid.tracks[harm_track_idx]:
                    time_acc += tick_to_sec(msg.time)
                    if msg.type in ['note_on', 'note_off'] and msg.note == note_pitch:
                        if msg.type == 'note_on' and msg.velocity > 0:
                            # this is the note_on we want to shorten
                            new_track.append(msg)
                        elif (msg.type == 'note_off' or 
                              (msg.type == 'note_on' and msg.velocity == 0)):
                            # replace note_off with one at correct earlier time
                            new_ticks = int(new_duration_sec / tick_to_sec(1) * ppq)
                            new_msg = msg.copy(time=max(1, new_ticks) if new_track else msg.time)
                            new_track.append(new_msg)
                            fixed = True
                    else:
                        new_track.append(msg)

                if fixed:
                    mid.tracks[harm_track_idx] = new_track
                    mid.save(mid_path)
                    print(f"Fixed! Shortened by {SHORTEN_MS} ms")
                    break  # Process only the first valid MIDI file found

            if not fixed:
                print("No matching note found. Already fixed or wrong time/track name?")
                return

            # Repack
            output_con = con_path.with_name(con_path.stem + "_FIXED.con")
            print("Repacking into new CON...")
            repack_con(extract_dir, output_con, onyx_path)
            print(f"\nSUCCESS! Fixed file saved as:\n   {output_con}\n")
            print("You can now convert this new CON with Nautilus PS3 Converter.")

        finally:
            if work_dir.exists():
                shutil.rmtree(work_dir)

# ------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    parser = argparse.ArgumentParser(description="Fix RB3 vocal overhang errors")
    parser.add_argument("--con_file", help="Path to the .con file")
    parser.add_argument("--midi_file", help="Path to MIDI file (skips extraction/repacking)")
    parser.add_argument("--location", required=True, help="Error location, e.g., '49:4.300'")
    parser.add_argument("--track_name", default="PART HARM1", help="Track name (default: PART HARM1)")
    parser.add_argument("--onyx_path", default=r"C:\Program Files\OnyxToolkit\onyx.exe", help="Full path to onyx.exe")

    args = parser.parse_args()

    # Validate arguments
    if not args.con_file and not args.midi_file:
        parser.error("Must provide either --con_file or --midi_file")
    if args.con_file and args.midi_file:
        parser.error("Cannot provide both --con_file and --midi_file")
        

    fix_vocal_overhang(con_path=args.con_file, midi_path=args.midi_file, location=args.location, track_name=args.track_name, onyx_path=args.onyx_path)


    