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
  // Remove common suffixes that cause mismatches
  t = t.replace(/\s*\(live\)/gi, '');
  t = t.replace(/\s*\(studio\)/gi, '');
  t = t.replace(/\s*\(album version\)/gi, '');
  t = t.replace(/\s*\(radio edit\)/gi, '');
  t = t.replace(/\s*\(explicit\)/gi, '');
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
  // Rock Band (release order)
  'rock_band_1_disc': { name: 'Rock Band', year: 2007 },
  'rock_band_2_disc': { name: 'Rock Band 2', year: 2008 },
  'rock_band_3_disc': { name: 'Rock Band 3', year: 2010 },
  'rock_band_4_disc': { name: 'Rock Band 4', year: 2015 },
  'dlc_rb_all_games': { name: 'Rock Band DLC (all)', year: 2007 },
  'dlc_rb3_onwards': { name: 'Rock Band 3 DLC', year: 2010 },
  'dlc_rb4_only': { name: 'Rock Band 4 DLC', year: 2015 },
  'rock_band_network': { name: 'Rock Band Network', year: 2010 },
  'beatles_rock_band_disc': { name: 'The Beatles: Rock Band', year: 2009 },
  'green_day_rock_band': { name: 'Green Day: Rock Band', year: 2010 },
  'lego_rock_band': { name: 'LEGO Rock Band', year: 2009 },
  
  // Guitar Hero (release order) - matching GH filenames
  'guitar_hero_disc': { name: 'Guitar Hero', year: 2005 },
  'guitar_hero_2_disc': { name: 'Guitar Hero II', year: 2006 },
  'guitar_hero_3_disc': { name: 'Guitar Hero III', year: 2007 },
  'guitar_hero_world_tour_disc': { name: 'Guitar Hero World Tour', year: 2008 },
  'guitar_hero_5_disc': { name: 'Guitar Hero 5', year: 2009 },
  'guitar_hero_encore_80s_disc': { name: 'GH Encore: 80s', year: 2007 },
  'guitar_hero_warriors_rock_disc': { name: 'GH: Warriors of Rock', year: 2010 },
  'guitar_hero_aerosmith_disc': { name: 'GH: Aerosmith', year: 2008 },
  'guitar_hero_metallica_disc': { name: 'GH: Metallica', year: 2009 },
  'guitar_hero_smash_hits': { name: 'GH Smash Hits', year: 2009 },
  'guitar_hero_van_halen_disc': { name: 'GH: Van Halen', year: 2010 },
  'dj_hero_disc': { name: 'DJ Hero', year: 2009 },
  'dj_hero_2_disc': { name: 'DJ Hero 2', year: 2010 },
  'guitar_hero_on_tour_disc': { name: 'GH: On Tour', year: 2008 },
  'guitar_hero_live_disc': { name: 'Guitar Hero Live', year: 2015 },
};

const allMissing = [];

files.forEach(item => {
  const data = JSON.parse(fs.readFileSync(path.join(item.dir, item.file), 'utf8'));
  const songs = data.songs || [];
  const key = item.file.replace('.json', '');
  const label = sourceLabels[key] || {name: item.file, year: '?'};
  const srcName = label.name + ' (' + label.year + ')';
  
  songs.forEach(s => {
    if (!s.title || s.title.length < 3) return;
    const t = normalize(s.title);
    if (t.length < 3) return;
    if (!ourOfficialSet.has(t)) {
      const displayTitle = normalize(s.title);
      allMissing.push({title: displayTitle, artist: (s.artist || '').trim(), source: srcName, year: label.year, orderKey: key});
    }
  });
});

const bySource = {};
allMissing.forEach(s => { bySource[s.source] = bySource[s.source] || []; bySource[s.source].push(s); });

// Sort by release order: Rock Band first (RB1-RB4, DLC, spin-offs), then Guitar Hero
const order = {
  'rock_band_1_disc': 1, 'rock_band_2_disc': 2, 'rock_band_3_disc': 3, 'rock_band_4_disc': 4,
  'dlc_rb_all_games': 5, 'dlc_rb3_onwards': 6, 'dlc_rb4_only': 7,
  'rock_band_network': 8, 'beatles_rock_band_disc': 9, 'green_day_rock_band': 10, 'lego_rock_band': 11,
  'guitar_hero_disc': 101, 'guitar_hero_2_disc': 102, 'guitar_hero_3_disc': 103, 'guitar_hero_world_tour_disc': 104,
  'guitar_hero_5_disc': 105, 'guitar_hero_encore_80s_disc': 106, 'guitar_hero_warriors_rock_disc': 107, 'guitar_hero_aerosmith_disc': 108,
  'guitar_hero_metallica_disc': 109, 'guitar_hero_smash_hits': 110, 'guitar_hero_van_halen_disc': 111, 'dj_hero_disc': 112, 'dj_hero_2_disc': 113,
  'guitar_hero_on_tour_disc': 114, 'guitar_hero_live_disc': 115
};

const sorted = Object.entries(bySource).sort((a,b) => {
  // Extract the order key (first entry's orderKey)
  const keyA = allMissing.find(s => s.source === a[0])?.orderKey || a[0];
  const keyB = allMissing.find(s => s.source === b[0])?.orderKey || b[0];
  return (order[keyA] || 999) - (order[keyB] || 999);
});

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