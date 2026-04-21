# Guitar Hero Song Lists

This directory contains official Guitar Hero song lists parsed from Wikipedia.

## Song Lists - COMPLETED

| # | Game | Wikipedia Link | Songs |
|---|------|---------------|------|
| 1 | Guitar Hero | https://en.wikipedia.org/wiki/List_of_songs_in_Guitar_Hero | 47 |
| 2 | Guitar Hero II | https://en.wikipedia.org/wiki/List_of_songs_in_Guitar_Hero_II | 48 |
| 3 | Guitar Hero III: Legends of Rock | https://en.wikipedia.org/wiki/List_of_songs_in_Guitar_Hero_III:_Legends_of_Rock | 73 |
| 4 | Guitar Hero World Tour (GH4) | https://en.wikipedia.org/wiki/List_of_songs_in_Guitar_Hero_World_Tour | 86 |
| 5 | Guitar Hero 5 | https://en.wikipedia.org/wiki/List_of_songs_in_Guitar_Hero_5 | 85 |
| 6 | Guitar Hero Encore: Rocks the 80s | https://en.wikipedia.org/wiki/List_of_songs_in_Guitar_Hero_Encore:_Rocks_the_80s | 30 |
| 7 | Guitar Hero: Warriors of Rock | https://en.wikipedia.org/wiki/List_of_songs_in_Guitar_Hero:_Warriors_of_Rock | 93 |
| 8 | Guitar Hero Live | https://en.wikipedia.org/wiki/List_of_songs_in_Guitar_Hero_Live | 42 |
| 9 | Guitar Hero: Metallica | https://en.wikipedia.org/wiki/List_of_songs_in_Guitar_Hero:_Metallica | 52 |
| 10 | Guitar Hero: Aerosmith | https://en.wikipedia.org/wiki/List_of_songs_in_Guitar_Hero:_Aerosmith | 31 |
| 11 | Guitar Hero Smash Hits | https://en.wikipedia.org/wiki/List_of_songs_in_Guitar_Hero_Smash_Hits | 48 |
| 12 | Guitar Hero: Van Halen | https://en.wikipedia.org/wiki/List_of_songs_in_Guitar_Hero:_Van_Halen | 47 |
| 13 | DJ Hero | https://en.wikipedia.org/wiki/List_of_songs_in_DJ_Hero | 58 |
| 14 | DJ Hero 2 | https://en.wikipedia.org/wiki/List_of_songs_in_DJ_Hero_2 | 83 |
| 15 | Guitar Hero: On Tour (DS) | https://en.wikipedia.org/wiki/List_of_songs_in_the_Guitar_Hero:_On_Tour_series | 28 |

**Total: 851 songs**

## JSON Format

Each JSON file has this structure:
```json
{
  "game": "Guitar Hero 5",
  "type": "disc",
  "songs": [
    {"title": "Song Name", "artist": "Artist Name", "year": 2007, "genre": "Rock", "master": true, "tier": "5.45", "exportable": true}
  ]
}
```

## Related

- Rock Band song lists: `../song_lists/` (3,186 songs)
- Combined total: 4,037 songs
- Verification HTML: `/workspace/docs/songs_to_verify_on_ps4.html`