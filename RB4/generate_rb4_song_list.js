#!/usr/bin/env node
// =============================================================================
// generate_rb4_song_list.js — RB4 Song List Generator
//
// Reads a hardcoded baseline (rb4songlistWithRivals.txt) and an optional
// Onyx-scan JSON file (rb4_custom_songs.json), de-duplicates, applies a
// profanity filter, and writes 4 output text files matching the RB3 pattern:
//
//   SongListSortedByArtist.txt
//   SongListSortedBySongName.txt
//   SongListSortedByArtistClean.txt
//   SongListSortedBySongNameClean.txt
//
// Usage:
//   node generate_rb4_song_list.js [OPTIONS]
//
// Options:
//   --baseline <file>  Path to rb4songlistWithRivals.txt  (default: ./rb4songlistWithRivals.txt)
//   --custom   <file>  Path to rb4_custom_songs.json      (optional)
//   --outdir   <dir>   Output directory                   (default: ./output)
//   --timezone <tz>    Timezone (e.g. America/New_York)   (default: system)
//   -v, --verbose      Print each song as it is processed
//   -h, --help         Show this help
// =============================================================================

'use strict';

const fs   = require('fs');
const path = require('path');

// ── Profanity filter (mirrors generate_song_lists.py) ─────────────────────────
const CURSE_WORDS = [
  'shit', 'fuck', 'bitch', 'bullshit', 'motherfucker', 'mother fucker',
  'tits', 'boobs', 'jizz',
  'asshole', 'dumbass', 'badass', 'jackass', 'smartass',
  'bastard', 'damn', 'dammit', 'goddamn', 'god damn',
];
const CURSE_REGEXES = [
  /\bdick\b/i,
  /\bcock\b/i,
  /\bcum\b/i,
  /\bpiss(ed|ing)?\b/i,
];

function matchesCurse(line) {
  const low = line.toLowerCase();
  for (const w of CURSE_WORDS) {
    if (low.includes(w)) return true;
  }
  for (const r of CURSE_REGEXES) {
    if (r.test(line)) return true;
  }
  return false;
}

// ── Normalization (mirrors clean_for_comparison in Python) ────────────────────
function normalize(s) {
  if (!s) return '';
  return s
    .toLowerCase()
    .trim()
    .replace(/\s+/g, ' ')
    .replace(/[\"'.,]/g, '');
}

// ── Duration conversion ───────────────────────────────────────────────────────
function msToMmSs(ms) {
  if (ms == null || ms < 0) return '?:??';
  const totalSec = Math.floor(ms / 1000);
  const m = Math.floor(totalSec / 60);
  const s = totalSec % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
}

// ── Parse MM:SS back to ms (for baseline .txt) ────────────────────────────────
function mmSsToMs(str) {
  if (!str || str === '?:??') return null;
  const [m, s] = str.split(':').map(Number);
  if (isNaN(m) || isNaN(s)) return null;
  return (m * 60 + s) * 1000;
}

// ── Parse the baseline .txt file ─────────────────────────────────────────────
// Expected line format:
//   Artist (Album) - Song Title (Year / MM:SS) - Source
// e.g.:
//   .38 Special (Special Forces) - Caught Up in You (1982 / 4:37) - RB4
function parseBaselineLine(line) {
  line = line.trim();
  if (!line) return null;

  // Find the LAST " - " separating song block from source label
  // Source label has no parentheses, so the last " - " is the source separator
  const srcMatch = line.match(/^(.*)\s-\s(\S+)\s*$/);
  if (!srcMatch) return null;
  const source = srcMatch[2].trim();
  const rest = srcMatch[1].trim(); // "Artist (Album) - Song Title (Year / MM:SS)"

  // Locate the year/duration block: " (YYYY / MM:SS)" at the end of rest
  const yearDurMatch = rest.match(/^(.*)\s\((\d{4}|\?)\s*\/\s*([\d:?]+)\)\s*$/);
  if (!yearDurMatch) return null;
  const artistAlbumDash = yearDurMatch[1].trim(); // "Artist (Album) - Song Title"
  const year  = yearDurMatch[2] === '?' ? null : parseInt(yearDurMatch[2], 10);
  const mmss  = yearDurMatch[3].trim();
  const durationMs = mmSsToMs(mmss);

  // Split on LAST " - " to get artist(Album) and song title
  const lastDashIdx = artistAlbumDash.lastIndexOf(' - ');
  if (lastDashIdx === -1) return null;
  const artistAlbumPart = artistAlbumDash.slice(0, lastDashIdx).trim();
  const title            = artistAlbumDash.slice(lastDashIdx + 3).trim();

  // Extract album from the artistAlbumPart: last balanced set of parens = album
  let artist = artistAlbumPart;
  let album  = null;
  const albumMatch = artistAlbumPart.match(/^(.*?)\s\(([^)]+)\)\s*$/);
  if (albumMatch) {
    artist = albumMatch[1].trim();
    album  = albumMatch[2].trim();
  }

  if (!artist || !title) return null;
  return { artist, album, title, year, durationMs, source };
}

// ── Parse Onyx JSON metadata (flexible field mapping) ────────────────────────
// Onyx may use different field names depending on version. We try multiple.
function parseOnyxSong(obj, sourceOverride) {
  const get = (...keys) => {
    for (const k of keys) {
      if (obj[k] != null && obj[k] !== '') return String(obj[k]);
    }
    return null;
  };
  const getNum = (...keys) => {
    for (const k of keys) {
      const v = parseFloat(obj[k]);
      if (!isNaN(v)) return v;
    }
    return null;
  };

  const artist = get('artist', 'Artist', 'song_artist', 'artist_name');
  const title  = get('title', 'Title', 'name', 'song_name', 'songname');
  const album  = get('album', 'Album', 'album_name');

  const yearRaw = get('year', 'Year', 'year_released', 'release_year');
  const year    = yearRaw ? parseInt(yearRaw, 10) : null;

  const durationMs = getNum('duration_ms', 'durationMs', 'length_ms', 'song_length', 'length', 'duration');

  const source = sourceOverride || get('source', 'source_pkg') || 'Custom';

  const shortName = get('shortName', 'shortname') || '';
  const instruments = get('instruments', 'instrumentEmoji') || '';

  if (!artist || !title) return null; // skip non-song PKGs
  return { artist, album: album || null, title, year: isNaN(year) ? null : year, durationMs, source, shortName, instruments };
}

// ── Format a song as an output line (artist-sorted style) ────────────────────
function formatArtistLine(song) {
  const album   = song.album  || '(unknown album)';
  const year    = song.year   != null ? song.year : '?';
  const dur     = msToMmSs(song.durationMs);
  const shortName = song.shortName || '';
  let instruments = song.instruments || '';
  
  // For baseline (official) songs, default to full band + vocals
  // Emoji order: 🎸=guitar, 🎸=bass, 🥁=drums, 🎤=vocals
  // Check for harmony (vocalParts > 1 means multiple vocal tracks)
  const isBaseline = ['RB4', 'Rivals'].includes(song.source);
  if (song.vocalParts && song.vocalParts > 1) {
    instruments = '🎸🎸🥁🎤🎤';  // Multiple vocal mics for harmony
  } else if (!instruments && isBaseline) {
    instruments = '🎸🎸🥁🎤';  // guitar, bass, drums, vocals
  }
  
  return `${song.artist} (${album}) - ${song.title} (${year} / ${dur}) - ${song.source} [${shortName}]${instruments}`;
}

// ── Format a song as a name-sorted line ──────────────────────────────────────
function formatNameLine(song) {
  const album   = song.album  || '(unknown album)';
  const year    = song.year   != null ? song.year : '?';
  const dur     = msToMmSs(song.durationMs);
  const shortName = song.shortName || '';
  let instruments = song.instruments || '';
  
  // For baseline (official) songs, default to full band + vocals
  // RB4, Rivals, and other official content have all instruments
  const isBaseline = ['RB4', 'Rivals'].includes(song.source);
  if (song.vocalParts && song.vocalParts > 1) {
    instruments = '🎸🎸🥁🎤🎤';
  } else if (!instruments && isBaseline) {
    instruments = '🎸🎸🥁🎤';
  }
  
  return `${song.title} by ${song.artist} on ${album} (${year} / ${dur}) - ${song.source} [${shortName}]${instruments}`;
}

// ── Build stats header ────────────────────────────────────────────────────────
function buildHeader(songs, timestamp) {
  const counts = {};
  for (const s of songs) {
    counts[s.source] = (counts[s.source] || 0) + 1;
  }
  const artists = new Set(songs.map(s => normalize(s.artist)));
  const albums  = new Set(songs.filter(s => s.album).map(s => normalize(s.album)));

  let header = `Generated on: ${timestamp}\n\n`;
  header += `Total songs: ${songs.length}\n`;
  header += `Total artists: ${artists.size}\n`;
  header += `Total albums: ${albums.size}\n`;

  const sourceBreakdown = Object.entries(counts)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([src, n]) => `  ${src}: ${n}`)
    .join('\n');
  header += `\nBreakdown by source:\n${sourceBreakdown}\n\n`;

  // Check for current update (from JSON file) and show in header
  const updateHistoryFile = path.join(__dirname, 'update_history.json');
  if (fs.existsSync(updateHistoryFile)) {
    const history = JSON.parse(fs.readFileSync(updateHistoryFile, 'utf8'));
    if (history && history.length > 0) {
      const latest = history[history.length - 1];
      if (latest.newSongs && latest.newSongs.length > 0) {
        const totalNew = latest.newSongs.length;
        header += `---\nNew in this update (${latest.timestamp}): ${totalNew} song${totalNew > 1 ? 's' : ''}\n`;
        const artistCounts = {};
        for (const s of latest.newSongs) {
          const artist = s.artist || 'Unknown';
          artistCounts[artist] = (artistCounts[artist] || 0) + 1;
        }
        const sorted = Object.entries(artistCounts)
          .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
          .slice(0, 20);
        for (const [artist, count] of sorted) {
          header += `  ${artist}: ${count} song${count > 1 ? 's' : ''}\n`;
        }
        if (Object.keys(artistCounts).length > 20) {
          header += `  ... and ${Object.keys(artistCounts).length - 20} more artists\n`;
        }
        header += `\n`;
      }
    }
  }

  return header;
}

// ── Extract update history from existing song list file (for incremental runs) ──
function loadUpdateHistoryFromSongList(songListPath) {
  if (!fs.existsSync(songListPath)) return [];
  
  const content = fs.readFileSync(songListPath, 'utf8');
  
  // Find "Update History:" section
  const historyMatch = content.match(/---\nUpdate History:\n([\s\S]*?)(?:---|\nProcessed PKGs:)/);
  if (!historyMatch) return [];
  
  const historySection = historyMatch[1];
  const updates = [];
  
  // Parse each update block: "=== timestamp: +X songs ==="
  const updateRegex = /=== (\d{4}-\d{2}-\d{2} \d{2}:\d{2}): \+(\d+) songs ===/g;
  let match;
  while ((match = updateRegex.exec(historySection)) !== null) {
    const timestamp = match[1];
    const songCount = parseInt(match[2]);
    
    // Extract artist list for this update
    const blockStart = match.index;
    const nextBlock = historySection.indexOf('===', blockStart + 1);
    const blockEnd = nextBlock === -1 ? historySection.length : nextBlock;
    const block = historySection.substring(blockStart, blockEnd);
    
    // Parse artists from this block
    const artists = [];
    const artistRegex = /^\s{2}([^:]+): (\d+) song/g;
    let artistMatch;
    while ((artistMatch = artistRegex.exec(block)) !== null) {
      artists.push({ artist: artistMatch[1], title: `song ${artistMatch[2]}` }); // Simplified
    }
    
    updates.push({
      timestamp: timestamp,
      newSongs: artists,
      totalSongs: songCount
    });
  }
  
  return updates;
}

// ── Append update history and processed PKGs to bottom of output files ─────
function appendProcessedPKGs(outputPath, processedPkgs) {
  // Try to load history from existing song list, fallback to JSON file
  let history = [];
  const songListPath = path.join(__dirname, 'output', 'SongListSortedBySongName.txt');
  if (fs.existsSync(songListPath)) {
    history = loadUpdateHistoryFromSongList(songListPath);
  }
  
  // Also check JSON file for any new updates since last generation
  const updateHistoryFile = path.join(__dirname, 'update_history.json');
  if (fs.existsSync(updateHistoryFile)) {
    const jsonHistory = JSON.parse(fs.readFileSync(updateHistoryFile, 'utf8'));
    // Merge: add any JSON entries that are not in the song list yet
    if (jsonHistory && jsonHistory.length > 0) {
      const existingTimestamps = new Set(history.map(h => h.timestamp));
      for (const entry of jsonHistory) {
        if (!existingTimestamps.has(entry.timestamp)) {
          history.push(entry); // Add to end (will be sorted newest-first below)
        }
      }
    }
  }
  
  // Sort by timestamp descending (newest first)
  history.sort((a, b) => b.timestamp.localeCompare(a.timestamp));
  
  // Use CLI processed PKGs if provided, otherwise check song list
  if (!processedPkgs || processedPkgs.length === 0) {
    if (fs.existsSync(songListPath)) {
      const content = fs.readFileSync(songListPath, 'utf8');
      const pkgMatch = content.match(/---\nProcessed PKGs:\n([\s\S]*)$/);
      if (pkgMatch) {
        processedPkgs = pkgMatch[1].split('\n').filter(l => l.trim().startsWith('UP8802'));
      }
    }
  }
  
  let append = '';
  
  // Append all update history entries (newest first, oldest bottom)
  if (history.length > 0) {
    append += `---\nUpdate History:\n`;
    for (const h of history) {
      const totalNew = h.newSongs ? h.newSongs.length : 0;
      append += `\n=== ${h.timestamp}: +${totalNew} songs ===\n`;
      
      if (h.newSongs && h.newSongs.length > 0) {
        const artistCounts = {};
        for (const s of h.newSongs) {
          const artist = s.artist || 'Unknown';
          artistCounts[artist] = (artistCounts[artist] || 0) + 1;
        }
        const sorted = Object.entries(artistCounts)
          .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
        for (const [artist, count] of sorted) {
          append += `  ${artist}: ${count} song${count > 1 ? 's' : ''}\n`;
        }
      }
    }
    append += `\n`;
  }
  
  // Append processed PKGs
  if (processedPkgs.length > 0) {
    append += `---\nProcessed PKGs:\n`;
    for (const pkg of processedPkgs) {
      if (pkg.trim()) append += `  ${pkg.trim()}\n`;
    }
  }
  
  if (append) {
    const existing = fs.readFileSync(outputPath, 'utf8');
    fs.writeFileSync(outputPath, existing + append + '\n', 'utf8');
  }
}

// ── Write a pair of files (full + clean) ─────────────────────────────────────
function writePair(lines, songs, headerFull, outFull, outClean, sortLabel, verbose, processedPkgs) {
  // Full file
  fs.writeFileSync(outFull, headerFull + lines.join('\n') + '\n', 'utf8');
  if (verbose) console.log(`  Wrote ${lines.length} lines → ${outFull}`);

  // Append processed PKGs to bottom of full file
  appendProcessedPKGs(outFull, processedPkgs);

  // Clean file: filter out curse-word lines
  const cleanLines   = lines.filter(l => !matchesCurse(l));
  const cleanSongs   = songs.filter((_, i) => !matchesCurse(lines[i]));
  const cleanArtists = new Set(cleanSongs.map(s => normalize(s.artist)));
  const cleanAlbums  = new Set(cleanSongs.filter(s => s.album).map(s => normalize(s.album)));

  const cleanHeaderExtra =
    `Total songs: ${cleanLines.length}\n` +
    `Total artists: ${cleanArtists.size}\n` +
    `Total albums: ${cleanAlbums.size}\n\n`;

  const now = headerFull.split('\n')[0]; // "Generated on: ..."
  const cleanHeader = `${now}\n\n${cleanHeaderExtra}`;

  fs.writeFileSync(outClean, cleanHeader + cleanLines.join('\n') + '\n', 'utf8');
  if (verbose) console.log(`  Wrote ${cleanLines.length} clean lines → ${outClean}`);
}

// ── Main ──────────────────────────────────────────────────────────────────────
function main(argv) {
  let baselineFile = path.join(__dirname, 'rb4songlistWithRivals.txt');
  let customFile   = null;
  let outDir       = path.join(__dirname, 'output');
  let timezone     = process.env.TZ || Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
  let verbose      = false;
  let processedArg = null;

  for (let i = 2; i < argv.length; i++) {
    switch (argv[i]) {
      case '--baseline': baselineFile = argv[++i]; break;
      case '--custom':   customFile   = argv[++i]; break;
      case '--outdir':   outDir       = argv[++i]; break;
      case '--timezone': timezone     = argv[++i]; break;
      case '--processed': processedArg = argv[++i]; break;
      case '-v':
      case '--verbose':  verbose = true; break;
      case '-h':
      case '--help':
        console.log('Usage: node generate_rb4_song_list.js [--baseline file] [--custom file] [--outdir dir] [--timezone tz] [--processed file] [-v]');
        process.exit(0);
        break;
      default:
        console.error(`Unknown option: ${argv[i]}`); process.exit(1);
    }
  }

  // Load processed PKGs from argument or file
  let processed = [];
  if (processedArg && fs.existsSync(processedArg)) {
    const data = JSON.parse(fs.readFileSync(processedArg, 'utf8'));
    processed = Array.isArray(data) ? data : [];
  }

  // ── Load baseline songs ──────────────────────────────────────────────────
  if (!fs.existsSync(baselineFile)) {
    console.error(`ERROR: Baseline file not found: ${baselineFile}`);
    process.exit(1);
  }
  const baselineLines = fs.readFileSync(baselineFile, 'utf8').split('\n');
  const baselineSongs = [];
  let baselineSkipped = 0;
  for (const line of baselineLines) {
    if (!line.trim()) continue;
    const song = parseBaselineLine(line);
    if (song) {
      baselineSongs.push(song);
    } else {
      if (verbose) console.warn(`  ⚠ Could not parse baseline line: ${line}`);
      baselineSkipped++;
    }
  }
  console.log(`Baseline: ${baselineSongs.length} songs loaded (${baselineSkipped} lines skipped)`);

  // ── Load custom songs from Onyx scan ────────────────────────────────────
  const customSongs = [];
  if (customFile) {
    if (!fs.existsSync(customFile)) {
      console.warn(`WARNING: Custom JSON file not found: ${customFile} — skipping custom songs`);
    } else {
      const raw  = JSON.parse(fs.readFileSync(customFile, 'utf8'));
      const list = Array.isArray(raw) ? raw : [raw];
      let skipped = 0;
      for (const obj of list) {
        const song = parseOnyxSong(obj, null);
        if (song) {
          customSongs.push(song);
        } else {
          skipped++;
          if (verbose) console.warn(`  ⚠ Non-song PKG entry skipped: ${JSON.stringify(obj).slice(0, 80)}`);
        }
      }
      console.log(`Custom: ${customSongs.length} songs loaded (${skipped} entries skipped)`);
    }
  }

  // ── De-duplicate: custom wins over baseline for same artist+title ────────
  // Build lookup of custom normalized keys
  const customKeys = new Set(customSongs.map(s => normalize(s.artist) + '|' + normalize(s.title)));

  // Exclude baseline entries that are covered by custom
  const baselineUniq = baselineSongs.filter(
    s => !customKeys.has(normalize(s.artist) + '|' + normalize(s.title))
  );
  const dedupedCount = baselineSongs.length - baselineUniq.length;
  if (dedupedCount > 0) {
    console.log(`De-duplicated: ${dedupedCount} baseline song(s) replaced by custom versions`);
  }

  // Also de-duplicate within each source group using a seen set
  const seen = new Set();
  const allSongs = [];
  for (const song of [...customSongs, ...baselineUniq]) {
    const key = normalize(song.artist) + '|' + normalize(song.title);
    if (!seen.has(key)) {
      seen.add(key);
      allSongs.push(song);
    }
  }

  console.log(`Total unique songs: ${allSongs.length}`);

  // ── Sort ─────────────────────────────────────────────────────────────────
  const artistSorted = [...allSongs].sort((a, b) => {
    const ac = normalize(a.artist), bc = normalize(b.artist);
    if (ac !== bc) return ac < bc ? -1 : 1;
    const alb = normalize(a.album || ''), blb = normalize(b.album || '');
    if (alb !== blb) return alb < blb ? -1 : 1;
    return normalize(a.title) < normalize(b.title) ? -1 : 1;
  });

  const nameSorted = [...allSongs].sort((a, b) => {
    const at = normalize(a.title), bt = normalize(b.title);
    if (at !== bt) return at < bt ? -1 : 1;
    return normalize(a.artist) < normalize(b.artist) ? -1 : 1;
  });

  // ── Output ────────────────────────────────────────────────────────────────
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  } else {
    // Delete existing SongList*.txt files to ensure clean output (per user request)
    // Delete existing SongList*.txt and RB4SongList*.txt files to ensure clean output (per user request)
    const existing = fs.readdirSync(outDir).filter(f => (f.startsWith('SongList') || f.startsWith('RB4SongList')) && f.endsWith('.txt'));
    for (const f of existing) {
      fs.unlinkSync(path.join(outDir, f));
    }
  }

  const now       = new Date();
  const timestamp = now.toLocaleString('en-US', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
    hour: 'numeric', minute: '2-digit', second: '2-digit', 
    timeZoneName: 'short',
    timeZone: timezone
  });

  const header = buildHeader(allSongs, timestamp);

  const artistLines = artistSorted.map(formatArtistLine);
  const nameLines   = nameSorted.map(formatNameLine);

  writePair(
    artistLines, artistSorted, header,
    path.join(outDir, 'SongListSortedByArtist.txt'),
    path.join(outDir, 'SongListSortedByArtistClean.txt'),
    'artist', verbose, processed
  );

  writePair(
    nameLines, nameSorted, header,
    path.join(outDir, 'SongListSortedBySongName.txt'),
    path.join(outDir, 'SongListSortedBySongNameClean.txt'),
    'name', verbose, processed
  );

  console.log('\n✅ Done. Output files:');
  for (const f of fs.readdirSync(outDir).sort()) {
    const stat = fs.statSync(path.join(outDir, f));
    console.log(`   ${f}  (${Math.round(stat.size / 1024)} KB)`);
  }
}

main(process.argv);
