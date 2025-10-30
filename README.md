# RockBand3SongsDtaSongListGenerator
Rock Band 3 songs.dta song list generator for parties

(I throw Rock Band 3 parties, where I run [Rock Band 3 Deluxe](https://rb3dx.milohax.org/) on my hacked PS3 with all the instruments and all 3 microphones, and I manage my own `songs.dta`.  My guests like to be able to look through songs on their phones when they are not active in the current band to help them decide what they'd like to play or sing next, as a lot of time is spent scrolling through songs trying to choose what to play.  This Python 3 script takes such a `songs.dta` file and generates two files, exemplified below, for sharing with rock band party guests so they can select songs when they are waiting their turn / watching others play.)

To run:
```
python3 generate_song_lists.py songs.dta
```

Output examples

`SongListSortedByArtist.txt`:
```
Foreigner (Agent Provocateur) - I Want to Know What Love Is (1984 / 5:16)
Foreigner (Double Vision) - Blue Morning, Blue Day (1978 / ?:??)
Foreigner (Double Vision) - Double Vision (1978 / 4:00)
Foreigner (Double Vision) - Hot Blooded (1978 / 4:45)
Foreigner (Foreigner) - Feels Like the First Time (1977 / ?:??)
Foreigner (Foreigner) - Headknocker (1977 / ?:??)
Foster the People (Torches) - Don't Stop (Color on the Walls) (2011 / 2:58)
Foster the People (Torches) - Helena Beat (2011 / 4:33)
Foster the People (Torches) - Pumped Up Kicks (2011 / 3:57)
Fountains of Wayne (Welcome Interstate Managers) - Stacy's Mom (2003 / 3:21)
Frank Sinatra (It Might as Well Be Swing) - Fly Me to the Moon (In Other Words) (1964 / 2:37)
Frank Sinatra (My Way) - My Way (1969 / 4:49)
Frankie Valli (Grease: The Original Soundtrack) - Grease (1978 / 3:31)
Franz Ferdinand (Franz Ferdinand) - Take Me Out (2004 / ?:??)
Franz Ferdinand (Tonight: Franz Ferdinand) - Lucid Dreams (2009 / ?:??)
Franz Ferdinand (You Could Have It So Much Better) - Do You Want To (2005 / ?:??)
Freezepop ((unknown album)) - Brainpower (? / ?:??)
Freezepop ((unknown album)) - Sprode (? / ?:??)
Freezepop (Freezepop Forever) - Get Ready 2 Rokk (2000 / ?:??)
Freezepop (Freezepop Forever) - Science Genius Girl (2000 / ?:??)
Freezepop (Future Future Future Perfect) - Less Talk More Rokk (2007 / ?:??)
Freezepop (Imaginary Friends) - Doppelgï¿½nger (2010 / 4:03)
Freezepop (Imaginary Friends) - Special Effects (2010 / 4:10)
Fun. (Some Nights) - Carry On (2012 / 4:44)
G. Love & Special Sauce (The Hustle) - Front Porch Lounger (2004 / 4:08)
Galantis (Pharmacy) - Peanut Butter Jelly (2015 / 3:38)
Galneryus ((unknown album)) - Destiny (1960 / 7:49)
Galneryus ((unknown album)) - Save You! (1960 / 7:32)
Garbage ((unknown album)) - I Think I'm Paranoid (? / ?:??)
Garbage (Garbage) - Stupid Girl (1995 / 4:22)
```


`SongListSortedBySongName.txt`
```
29 Fingers by The Konks on (unknown album) (? / ?:??)
3's & 7's by Queens of the Stone Age on (unknown album) (? / ?:??)
3rd Stone from the Sun by The Jimi Hendrix Experience on Are You Experienced (1967 / 6:50)
5 Minutes Alone by Pantera on Far Beyond Driven (1994 / 5:58)
7 Things by Miley Cyrus on Breakout (2008 / 3:33)
867-5309/Jenny by Tommy Tutone on Tutone-Ality (1981 / 3:48)
99 Luftballons by Nena on Nena (1983 / 3:53)
A Bullet in the Head by Anarchy Club on The Art of War (2009 / 3:41)
A Day In The Life by The Beatles on Sgt. Pepper's Lonely Hearts Club Band (1967 / 5:11)
A Day Like This by SpongeBob SquarePants on SpongeBob's Greatest Hits (2009 / ?:??)
A Drug Against War by KMFDM on Angst (1993 / 4:52)
A Favor House Atlantic by Coheed and Cambria on In Keeping Secrets of Silent Earth: 3 (2004 / ?:??)
A Forest by The Cure on Seventeen Seconds (1980 / 6:02)
A Hard Day's Night by The Beatles on A Hard Day's Night (1964 / 2:31)
A Hard Day's Night by The Beatles on A Hard Day's Night (1964 / 2:31)
A Jagged Gorgeous Winter by The Main Drag on Yours As Fast As Mine (2008 / 3:58)
A Little Less Sixteen Candles, a Little More \qTouch Me\q by Fall Out Boy on From Under the Cork Tree (2005 / 2:51)
A Little Respect by Erasure on The Innocents (1988 / 3:43)
A Looking in View by Alice In Chains on Black Gives Way to Blue (2009 / ?:??)
A Lot Like Me by The Offspring on Rise and Fall, Rage and Grace (2008 / 4:17)
A Milli by Lil Wayne on Tha Carter III (2008 / 3:42)
A Night Like This by The Cure on The Head on the Door (1985 / 4:17)
```

