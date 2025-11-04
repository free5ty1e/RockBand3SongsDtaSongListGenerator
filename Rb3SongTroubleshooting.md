PS3 Rock Band 3 Deluxe troubleshooting problematic songs


====Endless looping at end of song / hang / crash instead of score
---->>>Fix with Nautilus PS3 Converter's File -> Batch Fix Looping Songs (input CON, output fixed CON) :
* Dire Straits - Money for Nothing


====Crash immediately upon scrolling to / past song in song list
---->>>Fix with Nautilus CON/RBA Converter: drag CON here, it converts to LIVE.  Drag LIVE here, converts back to fixed CON.  
* R.E.M. - The One I Love


==========================================ENDLESS HANG ON SPECIFIC SONG ON MOTD LOADING======================================




1. If song loading hangs endlessly on the text screen where it shows a quote or tip of the day or fun fact about the band when attempting to play certain songs, this might be the problem / solution:

Troubleshooting guide: https://rb3pc.milohax.org/customs_troubleshooting

The fix is decrypting the .mogg file for:
* Counting Crows - A Long December






-----------
AI thread:

🛑 Problem Diagnosis: The Keys Track Mismatch
The issue is a classic track configuration mismatch, specifically related to the Pro Keys instrument.

Here is a breakdown of the conflicting lines in your "A Long December" entry:

1. The tracks_count Array (The Song's Blueprint)
This line tells the game which tracks are supposed to be in the song's MIDI file (in order: Drums, Bass, Guitar, Vocals, Keys, Pro Keys):

('tracks_count' (2 2 2 2 2 2))
Interpretation: The game expects 2 audio streams for all 6 primary instruments, which means it expects the song to have both Standard Keys (5th spot: 2) and Pro Keys (6th spot: 2).

2. The rank Data (The Song's Difficulty/Content)
The rank data suggests that the Pro Keys track is actually empty or missing:

(
   'rank'
   ('drum' 151)
   ('guitar' 176)
   ('bass' 181)
   ('vocals' 175)
   ('keys' 211)
   ('real_keys' 0)  <-- Rank 0 means the chart is empty/missing
   ('band' 215)
)
Interpretation: The rank of 0 for 'real_keys' (Pro Keys) strongly indicates that the chart data is not present in the .mid file.

3. The Missing tracks Entry (The Crash)
This is the critical error: If the tracks_count is (2 2 2 2 2 2), the game expects to see a track mapping for all six instruments in the tracks block.

Your tracks block for "A Long December" only lists five instruments:

(
   'tracks'
   (
      ('drum' (0 1))
      ('bass' (2 3))
      ('guitar' (4 5))
      ('vocals' (6 7))
      ('keys' (8 9))
      ; !!! The 'real_keys' track is MISSING from this block !!!
   )
)
The Conflict: The tracks_count says "I have Pro Keys" (the final 2), but the tracks list is missing the entry for 'real_keys'. When the game attempts to parse this, it encounters an unexpected end of data, which results in the infamous loading screen hang.

💡 Solution: Harmonize the Track Configuration
You have two options to fix this, depending on whether the song actually includes a Pro Keys track or not. The most reliable fix is to make the tracks_count match the actual, listed tracks.

Option 1 (The Easiest Fix): Remove Pro Keys from tracks_count
Since the real_keys rank is 0 and the real_keys track is missing from the tracks list, the chart almost certainly doesn't exist. Change the tracks_count line to remove Pro Keys.

Change this line:

('tracks_count' (2 2 2 2 2 2))
TO THIS: (Changing the final 2 to a 0)

('tracks_count' (2 2 2 2 2 0))
This tells the game: "We have Drum, Bass, Guitar, Vocals, and Keys, but no Pro Keys," which aligns with the actual five tracks listed in the tracks block and the rank of 0.

Option 2: Add the Missing real_keys Entry
If you are certain the song has a Pro Keys chart (which seems unlikely given the rank of 0), you would need to add the missing entry to the tracks block. Since the last entry ('keys') uses audio streams (8 9), the next one would typically use streams (10 11).

Add this line after the ('keys' (8 9)) entry in the tracks block:

('real_keys' (10 11))
Recommendation: Go with Option 1. The mismatch between tracks_count (...2 2) and the length of the tracks list (5 entries) is the smoking gun. Correcting tracks_count to ...2 0 will resolve the hang for "A Long December."








-- Option 1 didn't work, and the preview audio doesn't play for this song in the menu


That is an excellent additional clue. The fact that the song preview fails to play strongly suggests the issue is related to the song's audio file (.mogg) or the way the game is trying to locate/decode it.Since reverting the tracks_count change didn't fix the problem, let's step away from the track configuration for a moment and look at the actual audio setup.Here is the next step-by-step troubleshooting plan, focusing on the audio component of "A Long December":🔍 Next Steps: Audio/File Checks1. Verify Audio File Name and LocationThe game is looking for the audio file based on the file path defined in the songs.dta entry.In your "A Long December" entry:Code snippet      (
         'song'
         (
            'name'
            "songs/longdecember_v1/longdecember_v1"
         )
         ...
This tells the game to look in the main songs directory (usually a folder named songs/) for a subfolder named longdecember_v1, and inside that, a file named longdecember_v1.mogg.Check 1: Folder and File Naming:On your PS3/PC/USB drive, find the song folder (e.g., .../PS3/EXDATA/00000000/BLES01234-RB3DX/songs/).Do you have a folder named exactly longdecember_v1?Inside that folder, is there a file named exactly longdecember_v1.mogg?Crucially: Are the capitalization and spelling identical to the DTA entry? (Linux/PS3 is case-sensitive.)Check 2: File Presence: Is the .mogg file present? If it's missing, you will definitely get a hang and no preview.2. Check the .mogg File Integrity (Likely Cause)The .mogg file is the proprietary audio container used by the Rock Band engine. If this file is corrupt, incorrectly encoded, or has zero bytes, the game will hang while trying to initialize the audio stream.Check 3: File Size:Open the song folder (longdecember_v1).Check the size of longdecember_v1.mogg. A typical song .mogg is usually 10MB or more, depending on the song length and number of tracks.If the file size is 0 KB or just a few kilobytes, it is corrupted/missing, and this is your problem.Check 4: Encoding/Corrupted Magma Output:The song file was authored using Magma. It's possible the Magma conversion process failed for this song's audio. If you have the Magma source files, you should try re-exporting or re-creating the song package.As a quick check, you can try opening the .mogg file using a specialized program like rbhxmoggtool on your computer. If the tool can't open/decode it, the file is corrupt.3. Revisit The Track Count (The Hidden Clue from pans/vols)Let's quickly re-examine the track count in light of the working example "Friday I'm In Love".Songtracks_counttracks List Countpans/vols/cores CountResult"Friday I'm In Love" (Working)(2 2 2 2 **0 2**)4 (Drum, Bass, Guitar, Vocals)10 pairs (-1.00 1.00 repeated 10 times)Works. It omits Keys (0) but includes Pro Keys (2), and the number of audio streams is correct (4+2+2+2+0+2 = 10 pairs)."A Long December" (Broken)(2 2 2 2 **2 2**)5 (Drum, Bass, Guitar, Vocals, Keys)12 pairs (-1.00 1.00 repeated 12 times)CRASH. It expects 6 tracks (12 streams) but only lists 5 in tracks.You said Option 1 didn't work, which was changing tracks_count to (2 2 2 2 2 0).Let's try Option 3 (The Final DTA Fix): Since the tracks block is only 5 instruments long, and A Long December does not have a rank for Pro Keys (rank 0 for real_keys), we must align the DTA so the audio stream count matches the tracks list:Keep tracks_count: (2 2 2 2 2 2) (Tells the game 12 audio streams are in the .mogg.)Add the missing real_keys line to the tracks block:Code snippet(
   'tracks'
   (
      ('drum' (0 1))
      ('bass' (2 3))
      ('guitar' (4 5))
      ('vocals' (6 7))
      ('keys' (8 9))
      ('real_keys' (10 11)) <--- ADD THIS LINE
   )
)
This is necessary because your tracks_count of (2 2 2 2 2 2) means the game expects 12 audio streams (0 through 11) to be mapped, but your original tracks block only mapped up to stream 9 (keys at (8 9)).If all of these DTA changes fail, the problem is 99% a corrupted or empty longdecember_v1.mogg file.









---Adding real_keys didn't work either, suspect .mogg or .mid file issues:

2. The .mid.edat FileYou mentioned a file named longdecember_v1.mid.edat.The Problem: The game expects the MIDI file to be named longdecember_v1.mid. The presence of the .edat extension suggests the file may be encrypted or wrapped in a PS3-specific format used by an older custom song process (often associated with original DLC).Rock Band 3 Deluxe generally works best with a standard, decrypted .mid file.Actionable Step: Try renaming the file from longdecember_v1.mid.edat to longdecember_v1.mid and see if the song loads. If it was encrypted, the game won't know how to read the note charts and will hang.3. Revisit the DTA (A Specific MOGG Setting)There is one setting in the songs.dta that is crucial for audio and might be set incorrectly for a multitrack file:The Mute/Volume Settings: Your pans and vols arrays have 12 entries (6 instruments $\times$ 2 streams). This is consistent with your tracks_count of (2 2 2 2 2 2).The mute_volume_vocals: This is set to a normal value:Code snippet(mute_volume_vocals -12)
In some rare cases, people accidentally set the main mute_volume or the vols array too low, but yours look okay ((0.00 0.00 ...)).🚀 Final RecommendationSince you are missing the audio preview, the most likely issues are:Corrupt/Incomplete MOGG: The longdecember_v1.mogg at 5.9MB is suspicious for a 5-minute song. This is the primary suspect.Encrypted MIDI: The .mid.edat file name is unconventional and could be preventing the game from loading the chart data necessary to sync to the audio.I strongly recommend you first rename longdecember_v1.mid.edat to longdecember_v1.mid and test the song again. If that fails, you will unfortunately need to source a different, uncorrupted version of the longdecember_v1.mogg file.Would you like me to try a Google Search for information related to the longdecember_v1 custom song package to see if a known, working version or a fix is documented online?This is valuable diagnostic work! The fact that the DTA adjustments didn't fix it, combined with the lack of an audio preview, strongly reinforces that the problem lies with a fundamental asset file.The file sizes you reported are the most critical clue right now:longdecember_v1.mogg at 5.9 MB: This is extremely small for a 5-minute, presumably multitrack song. It is highly likely the .mogg is corrupted, incomplete, or incorrectly encoded.longdecember_v1.mid.edat at 122 KB: The .edat extension suggests the file is encrypted or wrapped, which is a significant red flag for Rock Band 3 Deluxe, which prefers decrypted files.Here is an updated action plan based on the new information and search results:🛠️ Action Plan: Fixing the Audio and MIDI FilesStep 1: Fix the MIDI File NameThe most immediate and easiest fix is to address the unusual file extension. The game is looking for longdecember_v1.mid.Navigate to your song folder: longdecember_v1/.Rename the file: longdecember_v1.mid.edat to longdecember_v1.mid.Test the song again.If the file was merely misnamed or wrapped in a way the game can now process, this may fix the crash.Step 2: Decrypt/Re-Generate the MOGG File (Using Nautilus)Since the small size and lack of preview point to a faulty .mogg or general file encryption, you need a tool to repair or replace the audio file. The search results point to Nautilus (formerly C3 CON Tools) as the modern utility for this kind of repair and conversion.Goal: Decrypt the MOGG/MIDI, and/or re-export a working package.Required Tool: Nautilus (You can find the GitHub link in the search results here).What you're likely dealing with is a song file that was originally packaged as a "CON" (a common format for Xbox 360 customs) or an older, encrypted PS3 format, which Rock Band 3 Deluxe is having trouble parsing. The error message "Required mogg audio file not present or used invalid encryption" is common in these situations, as seen in the search results here.Actionable Step:Download and open Nautilus.Use the Batch Extractor or the Clone Hero Converter tool within Nautilus.Load the entire longdecember_v1 folder (or just the suspect files) into the tool.The goal is to have Nautilus re-generate a clean, decrypted, and correct set of files (especially the .mogg) into a new output folder.Replace your old longdecember_v1 folder contents with the newly generated files.If the original .mogg was simply incomplete, Nautilus may prompt you to find or input the original source audio to generate a proper MOGG.I highly recommend trying Step 1 (renaming the file) first, as it's the simplest. If that fails, proceed to Step 2 using the Nautilus tool to handle the encryption/audio integrity issue.





