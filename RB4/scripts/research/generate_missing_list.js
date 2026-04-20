const fs = require('fs');
const path = require('path');

const ourSongs = JSON.parse(fs.readFileSync('./rb4_temp/rb4_custom_songs.json'), 'utf8');
const ourOfficialSet = new Set(ourSongs.filter(s => s.source !== 'Custom').map(s => (s.title||'').toLowerCase().trim()));

function cleanTitle(t) {
  if (!t) return '';
  // Remove wiki markdown links [text](url) -> text
  t = t.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
  // Handle any remaining [text] without ()
  t = t.replace(/\[([^\]]+)\]/g, '$1');  
  // Remove /wiki/ paths
  t = t.replace(/\/wiki\/[^\s)]+/g, '');
  // Remove underscores
  t = t.replace(/_/g, ' ');
  // Clean up special chars but keep apostrophes and hyphens
  t = t.replace(/[^a-z0-9 \'\-]/gi, '');
  // Remove duplicate words
  const words = t.split(' ').filter(w => w.length > 0);
  const unique = [];
  for (let i = 0; i < words.length; i++) {
    if (i === 0 || words[i] !== words[i-1]) unique.push(words[i]);
  }
  return unique.join(' ').toLowerCase().trim();
}

const listDir = './docs/research/song_lists';
const files = fs.readdirSync(listDir).filter(f => f.endsWith('.json'));

const sourceMap = {
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
  'rock_band_1_disc': 'Rock Band 1 disc'
};

const allMissing = [];

files.forEach(file => {
  const data = JSON.parse(fs.readFileSync(path.join(listDir, file), 'utf8'));
  const songs = data.songs || [];
  const srcName = sourceMap[file] || file;
  
  songs.forEach(s => {
    if (!s.title || s.title.length < 3) return;
    const t = cleanTitle(s.title);
    if (t.length < 3) return;
    if (!ourOfficialSet.has(t)) {
      allMissing.push({title: t, artist: (s.artist || '').trim(), source: srcName});
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
table{display:none;width:100%;border-collapse:collapse;margin-top:10px}
th,td{padding:6px;text-align:left;border-bottom:1px solid #333}
th{color:#e94560;font-size:0.85em}
.song-title{color:#e94560}
.artist{color:#00d4ff;font-size:0.9em}
.show{display:table}
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
<h2>Sources & References</h2>
<table>
<tr><th>Source</th><th>URL</th></tr>
<tr><td>Rock Band disc</td><td>https://en.wikipedia.org/wiki/List_of_songs_in_Rock_Band</td></tr>
<tr><td>Rock Band 2 disc</td><td>https://en.wikipedia.org/wiki/List_of_songs_in_Rock_Band_2</td></tr>
<tr><td>Rock Band 3 disc</td><td>https://en.wikipedia.org/wiki/List_of_songs_in_Rock_Band_3</td></tr>
<tr><td>Rock Band 4 disc</td><td>https://en.wikipedia.org/wiki/List_of_songs_in_Rock_Band_4</td></tr>
<tr><td>LEGO Rock Band</td><td>https://en.wikipedia.org/wiki/List_of_songs_in_Lego_Rock_Band</td></tr>
<tr><td>Green Day: Rock Band</td><td>https://en.wikipedia.org/wiki/List_of_songs_in_Green_Day:_Rock_Band</td></tr>
<tr><td>The Beatles: Rock Band</td><td>https://en.wikipedia.org/wiki/List_of_songs_in_The_Beatles:_Rock_Band</td></tr>
<tr><td>Rock Band DLC</td><td>https://en.wikipedia.org/wiki/List_of_downloadable_songs_for_the_Rock_Band_series</td></tr>
<tr><td>Rock Band Network</td><td>https://en.wikipedia.org/wiki/List_of_Rock_Band_Network_songs</td></tr>
</table>
</div>

<div class="section">
<h2>How to Verify</h2>
<ol>
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