const fs = require('fs');
const path = require('path');

const ourSongs = JSON.parse(fs.readFileSync('./rb4_temp/rb4_custom_songs.json'), 'utf8');

function normalize(t) {
  if (!t) return '';
  // Remove wiki markdown links [text](url) -> text
  t = t.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
  // Handle any remaining [text] without ()
  t = t.replace(/\[([^\]]+)\]/g, '$1');  
  // Remove /wiki/ paths
  t = t.replace(/\/wiki\/[^\s)]+/g, '');
  // Remove underscores
  t = t.replace(/_/g, ' ');
  // Normalize: lowercase, keep only letters/numbers/space/hyphen/slash/apostrophe
  t = t.toLowerCase().replace(/[^a-z0-9 \'\-\/]/g, '');
  // Collapse multiple spaces/slashes
  t = t.replace(/\s+/g, ' ').replace(/\/+/g, '/');
  return t.trim();
}

// Build lookup from our official songs with normalized keys
const ourOfficialSet = new Set();
ourSongs.filter(s => s.source !== 'Custom').forEach(s => {
  ourOfficialSet.add(normalize((s.title||'').trim()));
});

const listDir = './docs/research/song_lists';
const ghDir = './docs/research/song_lists/gh';

const files = [
  ...fs.readdirSync(listDir).filter(f => f.endsWith('.json')).map(f => ({file: f, dir: listDir})),
  ...fs.readdirSync(ghDir).filter(f => f.endsWith('.json')).map(f => ({file: f, dir: ghDir}))
];

const sourceLabels = {
  // Rock Band
  'beatles_rock_band_disc': 'The Beatles Rock Band',
  'green_day_rock_band': 'Green Day Rock Band',
  'lego_rock_band': 'LEGO Rock Band',
  'rock_band_network': 'Rock Band Network',
  'dlc_rb4_only': 'Rock Band 4 DLC',
  'dlc_rb_all_games': 'Rock Band DLC (all games)',
  'dlc_rb3_onwards': 'Rock Band 3 DLC',
  'rock_band_4_disc': 'Rock Band 4 disc',
  'rock_band_3_disc': 'Rock Band 3 disc',
  'rock_band_2_disc': 'Rock Band 2 disc',
  'rock_band_1_disc': 'Rock Band 1 disc',
  
  // Guitar Hero (in release order)
  'guitar_hero': 'Guitar Hero 1',
  'guitar_hero_2': 'Guitar Hero II',
  'gh3_songs': 'Guitar Hero III: Legends of Rock',
  'ghwt_dlc': 'Guitar Hero World Tour',  // GH4
  'guitar_hero_5': 'Guitar Hero 5',
  'guitar_hero_encore': 'Guitar Hero Encore: Rocks the 80s',
  'ghwor': 'Guitar Hero: Warriors of Rock',
  'guitar_hero_live': 'Guitar Hero Live',
  'ghm': 'Guitar Hero: Metallica',
  'gha': 'Guitar Hero: Aerosmith',
  'gh_smash_hits': 'Guitar Hero Smash Hits',
  'gh_van_halen': 'Guitar Hero: Van Halen',
  'dj_hero': 'DJ Hero',
  'dj_hero_2': 'DJ Hero 2',
  'gh_on_tour': 'Guitar Hero: On Tour'
};

const allMissing = [];

files.forEach(item => {
  const data = JSON.parse(fs.readFileSync(path.join(item.dir, item.file), 'utf8'));
  const songs = data.songs || [];
  const srcName = sourceLabels[item.file.replace('.json', '')] || item.file;
  
  songs.forEach(s => {
    if (!s.title || s.title.length < 3) return;
    const t = normalize(s.title);
    if (t.length < 3) return;
    if (!ourOfficialSet.has(t)) {
      const displayTitle = normalize(s.title);
      allMissing.push({title: displayTitle, artist: (s.artist || '').trim(), source: srcName});
    }
  });
});

const bySource = {};
allMissing.forEach(s => { bySource[s.source] = bySource[s.source] || []; bySource[s.source].push(s); });

const sorted = Object.entries(bySource).sort((a,b) => b[1].length - a[1].length);

console.log('Missing by source:');
sorted.forEach(([src, songs]) => console.log('  ' + src + ': ' + songs.length));

let html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>RB4 Missing Songs</title>
<style>
body{font-family:Arial,sans-serif;margin:20px;background:#1a1a2e;color:#eee}
h1{color:#00d4ff}
h2{color:#48dbfb;cursor:pointer;padding:10px;margin:0;background:#0f3460;border-radius:5px}
h2:hover{background:#1a4a7a}
.section{background:#16213e;padding:15px;margin:15px 0;border-radius:8px}
table,ol{display:none;width:100%;border-collapse:collapse;margin-top:10px}
ol{background:#16213e;padding:15px 15px 15px 35px;margin-top:10px;border-radius:8px}
a{color:#48dbfb}
th,td{padding:6px;text-align:left;border-bottom:1px solid #333}
th{color:#e94560;font-size:0.85em}
.song-title{color:#e94560}
.artist{color:#00d4ff;font-size:0.9em}
.show{display:table}
ol.show{display:block}
.count{color:#888;font-size:0.8em;margin-left:10px}
</style>
<script>
function toggle(id){var t=document.getElementById(id);if(t.classList.contains('show')){t.classList.remove('show');}else{t.classList.add('show');}}
</script>
</head>
<body>
<h1>RB4 Songs - MISSING from Extraction</h1>
<p><strong>PS4 shows:</strong> 4084 songs | <strong>Our official:</strong> 2416 | <strong>Missing:</strong> ${allMissing.length}</p>
<p>Click each category below to expand/collapse. Search for these songs in RB4 on PS4.</p>
`;

sorted.forEach(([src, songs], idx) => {
  songs.sort((a,b) => a.title.localeCompare(b.title));
  const id = 'table_' + idx;
  html += '<div class="section"><h2 onclick="toggle(\''+id+'\')">' + src + '<span class="count">(' + songs.length + ' songs - click to expand)</span></h2><table id="'+id+'"><tr><th>Song</th><th>Artist</th></tr>';
  songs.forEach(s => {
    html += '<tr><td class="song-title">' + s.title + '</td><td class="artist">' + s.artist + '</td></tr>';
  });
  html += '</table></div>';
});

html += `
<div class="section">
<h2 onclick="toggle('sources')">Sources & References<span class="count">(click to expand)</span></h2>
<table id="sources">
<tr><th>Source</th><th>URL</th></tr>
<tr><td>Rock Band disc</td><td><a href="https://en.wikipedia.org/wiki/List_of_songs_in_Rock_Band" target="_blank">https://en.wikipedia.org/wiki/List_of_songs_in_Rock_Band</a></td></tr>
<tr><td>Rock Band 2 disc</td><td><a href="https://en.wikipedia.org/wiki/List_of_songs_in_Rock_Band_2" target="_blank">https://en.wikipedia.org/wiki/List_of_songs_in_Rock_Band_2</a></td></tr>
<tr><td>Rock Band 3 disc</td><td><a href="https://en.wikipedia.org/wiki/List_of_songs_in_Rock_Band_3" target="_blank">https://en.wikipedia.org/wiki/List_of_songs_in_Rock_Band_3</a></td></tr>
<tr><td>Rock Band 4 disc</td><td><a href="https://en.wikipedia.org/wiki/List_of_songs_in_Rock_Band_4" target="_blank">https://en.wikipedia.org/wiki/List_of_songs_in_Rock_Band_4</a></td></tr>
<tr><td>LEGO Rock Band</td><td><a href="https://en.wikipedia.org/wiki/List_of_songs_in_Lego_Rock_Band" target="_blank">https://en.wikipedia.org/wiki/List_of_songs_in_Lego_Rock_Band</a></td></tr>
<tr><td>Green Day: Rock Band</td><td><a href="https://en.wikipedia.org/wiki/List_of_songs_in_Green_Day:_Rock_Band" target="_blank">https://en.wikipedia.org/wiki/List_of_songs_in_Green_Day:_Rock_Band</a></td></tr>
<tr><td>The Beatles: Rock Band</td><td><a href="https://en.wikipedia.org/wiki/List_of_songs_in_The_Beatles:_Rock_Band" target="_blank">https://en.wikipedia.org/wiki/List_of_songs_in_The_Beatles:_Rock_Band</a></td></tr>
<tr><td>Rock Band DLC</td><td><a href="https://en.wikipedia.org/wiki/List_of_downloadable_songs_for_the_Rock_Band_series" target="_blank">https://en.wikipedia.org/wiki/List_of_downloadable_songs_for_the_Rock_Band_series</a></td></tr>
<tr><td>Rock Band Network</td><td><a href="https://en.wikipedia.org/wiki/List_of_Rock_Band_Network_songs" target="_blank">https://en.wikipedia.org/wiki/List_of_Rock_Band_Network_songs</a></td></tr>
</table>
</div>

<div class="section">
<h2 onclick="toggle('howto')">How to Verify<span class="count">(click to expand)</span></h2>
<ol id="howto">
<li>Open Rock Band 4 on PS4</li>
<li>Go to the song library or browser</li>
<li>Search for songs listed as missing</li>
<li>If a song exists on PS4, note it - our extraction is missing that song</li>
<li>Report findings to help improve the extraction pipeline</li>
</ol>
</div>
</body>
</html>`;

fs.writeFileSync('/workspace/docs/songs_to_verify_on_ps4.html', html);
console.log('\nWrote /workspace/docs/songs_to_verify_on_ps4.html');
console.log('Total missing: ' + allMissing.length);