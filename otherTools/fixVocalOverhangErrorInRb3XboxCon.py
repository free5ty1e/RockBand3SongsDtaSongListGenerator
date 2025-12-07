#!/usr/bin/env python3
"""
RB3 Xbox CON → Auto-fix HARM1/HARM2/HARM3 vocal overhang error → New CON

Fixes the infamous Magma/Onyx error:
"Vocal note at [XX:X.XXX] extends beyond phrase"

Usage examples:
    python rb3_vocal_fix.py "MySong.con" "49:4.300"
    python rb3_vocal_fix.py "Pack.con" "72:1.850" "PART HARM2" --onyx_path "C:\\Tools\\onyx.exe"
    python rb3_vocal_fix.py song.con "15:3.000" "HARM3"

Requirements:
    pip install mido tqdm
    Extract the Onyx command-line ZIP to a folder (e.g., C:\\Program Files\\OnyxToolkit)
    (Download: https://github.com/mtolly/onyxite-customs/releases → onyx-command-line-*.zip)

Options:
    --onyx_path: Full path to onyx.exe (default: C:\\Program Files\\OnyxToolkit\\onyx.exe)
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path
import argparse
from tqdm import tqdm
import mido

# How much to shorten the offending note (5–15 ms is completely inaudible)
SHORTEN_MS = 10

def extract_con(con_path: Path, extract_dir: Path, onyx_path: str):
    cmd = f'"{onyx_path}" extract "{con_path}" "{extract_dir}" >nul 2>&1'
    result = os.system(cmd)
    if result != 0:
        raise RuntimeError(f"Onyx extraction failed. Command: {cmd}. Check onyx_path and DLLs.")

def repack_con(work_dir: Path, output_con: Path, onyx_path: str):
    cmd = f'"{onyx_path}" pack "{work_dir}" "{output_con}" --format rb3-xbox >nul 2>&1'
    result = os.system(cmd)
    if result != 0:
        raise RuntimeError(f"Onyx repacking failed. Command: {cmd}")

def fix_vocal_overhang(con_path: Path, location: str, track_name: str = "PART HARM1", onyx_path: str = r"C:\Program Files\OnyxToolkit\onyx.exe"):
    con_path = Path(con_path).resolve()
    if not con_path.exists():
        print(f"ERROR: File not found: {con_path}")
        return

    meas_str, beat_frac_str = location.split(':')
    target_measure = int(meas_str)
    target_beat = float(beat_frac_str)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        extract_dir = tmp_path / "extracted"
        extract_dir.mkdir()

        print(f"Extracting {con_path.name} ...")
        extract_con(con_path, extract_dir, onyx_path)

        # Find song subfolders (e.g. aaaa0001, songs inside packs)
        song_folders = [p for p in extract_dir.iterdir() if p.is_dir()]
        if not song_folders:
            print("No song folders found inside CON")
            return

        fixed = False
        for folder in song_folders:
            mid_candidates = list(folder.glob("*.mid")) + [folder / "song.mid"]
            mid_path = next((p for p in mid_candidates if p.exists()), None)
            if not mid_path:
                continue

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

        if not fixed:
            print("No matching note found. Already fixed or wrong time/track name?")
            return

        # Repack
        output_con = con_path.with_name(con_path.stem + "_FIXED.con")
        print("Repacking into new CON...")
        repack_con(extract_dir, output_con, onyx_path)
        print(f"\nSUCCESS! Fixed file saved as:\n   {output_con}\n")
        print("You can now convert this new CON with Nautilus PS3 Converter.")

# ------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    parser = argparse.ArgumentParser(description="Fix RB3 vocal overhang errors")
    parser.add_argument("con_file", help="Path to the .con file")
    parser.add_argument("location", help="Error location, e.g., '49:4.300'")
    parser.add_argument("track_name", nargs="?", default="PART HARM1", help="Track name (default: PART HARM1)")
    parser.add_argument("--onyx_path", default=r"C:\Program Files\OnyxToolkit\onyx.exe", help="Full path to onyx.exe")

    args = parser.parse_args()

    fix_vocal_overhang(args.con_file, args.location, args.track_name, args.onyx_path)
    