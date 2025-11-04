#PS3 Rock Band 3 Deluxe troubleshooting problematic songs


##Official RB3 Deluxe troubleshooting guide: https://rb3pc.milohax.org/customs_troubleshooting
Start here first.  


##Issue: Endless looping at end of song / hang / crash instead of score
###Fix with Nautilus PS3 Converter's File -> Batch Fix Looping Songs (input CON, output fixed CON) :
* Dire Straits - Money for Nothing


##Issue: Crash immediately upon scrolling to / past song in song list
###Fix with Nautilus CON/RBA Converter: drag CON here, it converts to LIVE.  Drag LIVE here, converts back to fixed CON.  
* R.E.M. - The One I Love


##Issue: Crash upon highlighting / stopping on a song in the song list for a second or two, when preview attempts to play
###Fix with Nautilus CON/RBA Converter: drag CON here, it converts to LIVE.  Drag LIVE here, converts back to fixed CON.
After this fix, the song no longer crashes when it attempts to play a preview in the song list, but it also does not play a preview and hangs endlessly on loading
* GOTYE - Somebody That I Used To Know


##Issue: Endless hang on song loading (shows tip of the day / fun fact text endlessly) - accompanied by no preview audio in the song list
###Fix by directly decrypting the .mogg file in Nautilus Batch Cryptor: drag PS3 song folder MOGG here, decrypts into `decrypted` folder.  Replace MOGG with decrypted version.
If song loading hangs endlessly on the text screen where it shows a quote or tip of the day or fun fact about the band when attempting to play certain songs, this might be the problem / solution.
####For batches of songs that need this treatment, see the [moggFlattenReadme](otherTools/moggFlattenReadme.md) file.

* Counting Crows - A Long December

