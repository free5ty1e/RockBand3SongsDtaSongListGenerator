# PS3 Rock Band 3 Deluxe troubleshooting problematic songs


## Official RB3 Deluxe troubleshooting guide: https://rb3pc.milohax.org/customs_troubleshooting
Start here first.  

## Toolsets
* Onyx - https://github.com/mtolly/onyxite-customs/releases
* Nautilus - https://github.com/trojannemo/Nautilus 


## Converting Score Hero customs to RB3 XBOX CON format
1. Extract archive to song folder
2. Open song.ini in Onyx
3. Choose `RB` tab up top
4. Click `Create Xbox 360 CON file` button
5. ?
6. Profit!


## Warning: Using the Nautilus PS3 Converter tool to Merge Songs with an existing `songs.dta` song list might result in unintended modifications to your song list.  Specifically:
* If you have commented out songs by using semicolons, they may be uncommented by the merge process.

## Issue: Endless looping at end of song / hang / crash instead of score
### Fix with Nautilus PS3 Converter's File -> Batch Fix Looping Songs (input CON, output fixed CON) :
* Dire Straits - Money for Nothing


## Issue: Crash immediately upon scrolling to / past song in song list
### Fix with Nautilus CON/RBA Converter: drag CON here, it converts to LIVE.  Drag LIVE here, converts back to fixed CON.  
* R.E.M. - The One I Love

#### May also have to balance your two required sections, `tracks_count` and `tracks`
`tracks_count` contains track counts for each of the `track` sections, each in order
Also, the `rank` section will contain difficulties for each part?  `0` rank means part is not included, so this can clue you in on how to fill these sections all out
For example:

```
  ( 'song'
      (
         'tracks_count'
         (6 2 2 2 2 2)
      )
      (
         'tracks'
         (
            (
               'drum'
               (0 1 2 3 4 5)
            )
            (
               'bass'
               (6 7)
            )
            (
               'guitar'
               (8 9)
            )
            (
               'vocals'
               (10 11)
            )
            (
               'keys'
               (12 13)
            )
            (
               'real_keys'
               (14 15)
            )
         )
      )
   )
   (
      'rank'
      ('drum' 178)
      ('guitar' 139)
      ('bass' 1)
      ('vocals' 132)
      ('keys' 211)
      ('real_keys' 211)
      ('band' 165)
   )
```

Additionally, if `tracks_count` section is missing, add it!


## Issue: Crash upon highlighting / stopping on a song in the song list for a second or two, when preview attempts to play
### Fix with Nautilus CON/RBA Converter: drag CON here, it converts to LIVE.  Drag LIVE here, converts back to fixed CON.
* GOTYE - Somebody That I Used To Know
*   After this fix, this song no longer crashes when it attempts to play a preview in the song list, but it also does not play a preview and hangs endlessly on loading.
*   I attempted decrypting with the Batch Cryptor tool to fix this, but after this step the song crashes when scrolling to it
*   I had worked through the songs.dta entry with AI and had to add `tracks` for `real_keys` to match the `tracks_count`, and this change got lost along the way, which leads to the next issue:






## Issue: Endless hang on song loading (shows tip of the day / fun fact text endlessly) - accompanied by no preview audio in the song list
### Fix by directly decrypting the .mogg file in Nautilus Batch Cryptor: drag PS3 song folder MOGG here, decrypts into `decrypted` folder.  Replace MOGG with decrypted version.
If song loading hangs endlessly on the text screen where it shows a quote or tip of the day or fun fact about the band when attempting to play certain songs, this might be the problem / solution.
####For batches of songs that need this treatment, see the [moggFlattenReadme](otherTools/moggFlattenReadme.md) file.

* Counting Crows - A Long December



## Issue: Score Hero song conversion to RB3 XBOX CON format fails with "Vocal note at [xx:y:zzz] is outside any phrases"
1. In the case of Sia - The Greatest, the problem was a missing phrase start marker to match an orphaned phrase end marker.  I uploaded the `notes.chart` file to Grok and asked it to analyze the vocal phrases:
   a. Edit `notes.chart` manually (Notepad):
   b. Find line `49412 = E "phrase_end"`
   c. Insert immediately after: `49428 = E "phrase_start"`
   d. Save and try conversion again.


## Issue: RB3 XBOX CON file won't convert in Nautilus PS3 Converter tool
1. Try opening with Onyx and then exporting back out again: PS3 tab, Create XBOX 360 CON File button.
2. If that fails with something like "ERROR: MIDI Compiler: (HARM1): Vocal note at [49:4.300] extends beyond phrase"
   a. Fix with [fixVocalOverhangErrorInRb3XboxCon.py](otherTools/fixVocalOverhangErrorInRb3XboxCon.py) tool in [otherTools](otherTools/) folder, then try step 1 again.
3. If that CON conversion to PS3 format fails with `There was an error processing the songs.dta file` then you might also need to fix up the `songs.dta` in that CON package and re-package it back up with CON Creator.
   a. For the example of Sia - Cheap Thrills (RB4 DLC), I had to replace the songs.dta contents with a stripped-down version with only the minimally required tags.  This fixed it, something that was there was causing the issue.  Below is the minimal `songs.dta` entry I used to fix this:

```
(cheapthrills
   (name "Cheap Thrills")
   (artist "Sia") 
   (master 1)
   (song
      (name 'songs/cheapthrills/cheapthrills')
      (tracks
         ((drum (0 1))
          (bass (2 3))
          (guitar (4 5))
          (vocals (6 7))))
      (pans (-1.0 1.0 -1.0 1.0 -1.0 1.0 -1.0 1.0 -1.0 1.0))
      (vols (0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0))
      (cores (-1 -1 -1 -1 1 1 -1 -1 -1 -1))
      (vocal_parts 3)
      (midi_file 'songs/cheapthrills/cheapthrills.mid'))
   (song_length 219998)
   (preview 37000 67000)
   (rank
      (drum 189)
      (bass 139) 
      (guitar 115)
      (vocals 318))
   (genre pop)
   (vocal_gender female)
   (version 0)
   (format 4))
```

NOTE: I also then had to extract the original `songs.dta` entry and replace the above in the main `songs.dta` file in order to actually get the song to show up in the PS3 RB3 song list!  

