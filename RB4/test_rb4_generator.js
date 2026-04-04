#!/usr/bin/env node
// =============================================================================
// test_rb4_generator.js — Unit tests for RB4 generator logic
//
// Run: node RB4/test_rb4_generator.js
// =============================================================================

'use strict';

let passed = 0;
let failed = 0;

function assert(desc, condition) {
  if (condition) {
    console.log(`  ✓ ${desc}`);
    passed++;
  } else {
    console.error(`  ✗ FAIL: ${desc}`);
    failed++;
  }
}

function assertEqual(desc, actual, expected) {
  const ok = actual === expected;
  if (ok) {
    console.log(`  ✓ ${desc}`);
    passed++;
  } else {
    console.error(`  ✗ FAIL: ${desc}`);
    console.error(`      Expected: ${JSON.stringify(expected)}`);
    console.error(`      Actual:   ${JSON.stringify(actual)}`);
    failed++;
  }
}

// ── Import helpers from generator (inline them for test isolation) ────────────

function msToMmSs(ms) {
  if (ms == null || ms < 0) return '?:??';
  const totalSec = Math.floor(ms / 1000);
  const m = Math.floor(totalSec / 60);
  const s = totalSec % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
}

function normalize(s) {
  if (!s) return '';
  return s.toLowerCase().trim().replace(/\s+/g, ' ').replace(/[\"'.,]/g, '');
}

function mmSsToMs(str) {
  if (!str || str === '?:??') return null;
  const [m, s] = str.split(':').map(Number);
  if (isNaN(m) || isNaN(s)) return null;
  return (m * 60 + s) * 1000;
}

function parseBaselineLine(line) {
  line = line.trim();
  if (!line) return null;
  const srcMatch = line.match(/^(.*)\s-\s(\S+)\s*$/);
  if (!srcMatch) return null;
  const source = srcMatch[2].trim();
  const rest = srcMatch[1].trim();
  const yearDurMatch = rest.match(/^(.*)\s\((\d{4}|\?)\s*\/\s*([\d:?]+)\)\s*$/);
  if (!yearDurMatch) return null;
  const artistAlbumDash = yearDurMatch[1].trim();
  const year  = yearDurMatch[2] === '?' ? null : parseInt(yearDurMatch[2], 10);
  const mmss  = yearDurMatch[3].trim();
  const durationMs = mmSsToMs(mmss);
  const lastDashIdx = artistAlbumDash.lastIndexOf(' - ');
  if (lastDashIdx === -1) return null;
  const artistAlbumPart = artistAlbumDash.slice(0, lastDashIdx).trim();
  const title = artistAlbumDash.slice(lastDashIdx + 3).trim();
  let artist = artistAlbumPart;
  let album = null;
  const albumMatch = artistAlbumPart.match(/^(.*?)\s\(([^)]+)\)\s*$/);
  if (albumMatch) { artist = albumMatch[1].trim(); album = albumMatch[2].trim(); }
  if (!artist || !title) return null;
  return { artist, album, title, year, durationMs, source };
}

const CURSE_WORDS = ['shit','fuck','bitch','bullshit','damn','dammit','goddamn'];
const CURSE_REGEXES = [/\bdick\b/i, /\bcock\b/i, /\bcum\b/i, /\bpiss(ed|ing)?\b/i];
function matchesCurse(line) {
  const low = line.toLowerCase();
  for (const w of CURSE_WORDS) { if (low.includes(w)) return true; }
  for (const r of CURSE_REGEXES) { if (r.test(line)) return true; }
  return false;
}

// ═════════════════════════════════════════════════════════════════════════════
// Test Suite: Duration conversion
// ═════════════════════════════════════════════════════════════════════════════
console.log('\n── msToMmSs ─────────────────────────────────────────────────────────');
assertEqual('0 ms → 0:00',             msToMmSs(0),         '0:00');
assertEqual('59999 ms → 0:59',         msToMmSs(59999),     '0:59');
assertEqual('60000 ms → 1:00',         msToMmSs(60000),     '1:00');
assertEqual('210000 ms → 3:30',        msToMmSs(210000),    '3:30');
assertEqual('3599000 ms → 59:59',      msToMmSs(3599000),   '59:59');
assertEqual('3600000 ms → 60:00',      msToMmSs(3600000),   '60:00');
assertEqual('null → ?:??',             msToMmSs(null),      '?:??');
assertEqual('-1 → ?:??',               msToMmSs(-1),        '?:??');

// ═════════════════════════════════════════════════════════════════════════════
// Test Suite: mmSsToMs
// ═════════════════════════════════════════════════════════════════════════════
console.log('\n── mmSsToMs ─────────────────────────────────────────────────────────');
assertEqual('4:37 → 277000',           mmSsToMs('4:37'),    277000);
assertEqual('0:00 → 0',               mmSsToMs('0:00'),    0);
assertEqual('?:?? → null',            mmSsToMs('?:??'),    null);

// ═════════════════════════════════════════════════════════════════════════════
// Test Suite: Normalize
// ═════════════════════════════════════════════════════════════════════════════
console.log('\n── normalize ────────────────────────────────────────────────────────');
assertEqual('strips quotes',           normalize('"Hello"'),    'hello');
assertEqual("strips apostrophes",      normalize("Don't"),      'dont');
assertEqual('strips periods',          normalize('St. Vincent'), 'st vincent');
assertEqual('lowercases',              normalize('ABBA'),        'abba');
assertEqual('trims whitespace',        normalize('  Foo  '),     'foo');
assertEqual('collapses spaces',        normalize('Foo   Bar'),   'foo bar');

// ═════════════════════════════════════════════════════════════════════════════
// Test Suite: Baseline parser
// ═════════════════════════════════════════════════════════════════════════════
console.log('\n── parseBaselineLine ────────────────────────────────────────────────');

const r1 = parseBaselineLine('.38 Special (Special Forces) - Caught Up in You (1982 / 4:37) - RB4');
assert('Parses artist correctly',      r1 && r1.artist === '.38 Special');
assert('Parses album correctly',       r1 && r1.album  === 'Special Forces');
assert('Parses title correctly',       r1 && r1.title  === 'Caught Up in You');
assert('Parses year correctly',        r1 && r1.year   === 1982);
assert('Parses durationMs correctly',  r1 && r1.durationMs === 277000);
assert('Parses source correctly',      r1 && r1.source === 'RB4');

const r2 = parseBaselineLine('Mark Ronson ft. Bruno Mars (Uptown Special) - Uptown Funk (2015 / 4:30) - RB4');
assert('Artist with ft. parses',       r2 && r2.artist === 'Mark Ronson ft. Bruno Mars');
assert('Title with no extras',         r2 && r2.title  === 'Uptown Funk');

const r3 = parseBaselineLine('Dream Theater (Images and Words) - Metropolis - Part 1 "The Miracle And The Sleeper" (1992 / 9:32) - RB4');
assert('Title with dashes parses',     r3 && r3.title  === 'Metropolis - Part 1 "The Miracle And The Sleeper"');

const r4 = parseBaselineLine('');
assert('Empty line returns null',      r4 === null);

// ═════════════════════════════════════════════════════════════════════════════
// Test Suite: De-duplication
// ═════════════════════════════════════════════════════════════════════════════
console.log('\n── de-duplication ───────────────────────────────────────────────────');

const baseline = [
  { artist: '50 Cent', title: 'In Da Club', album: 'GCORDT', year: 2003, durationMs: 210000, source: 'RB4' },
  { artist: 'Aerosmith', title: 'Toys in the Attic', album: 'Toys', year: 1975, durationMs: 185000, source: 'RB4' },
];
const custom = [
  { artist: '50 cent', title: 'in da club', album: "Get Rich Or Die Tryin'", year: 2003, durationMs: 212000, source: 'Custom' },
];

// Simulate de-dup logic from generate_rb4_song_list.js
const customKeys = new Set(custom.map(s => normalize(s.artist) + '|' + normalize(s.title)));
const baselineUniq = baseline.filter(s => !customKeys.has(normalize(s.artist) + '|' + normalize(s.title)));
const seen = new Set();
const allSongs = [];
for (const song of [...custom, ...baselineUniq]) {
  const key = normalize(song.artist) + '|' + normalize(song.title);
  if (!seen.has(key)) { seen.add(key); allSongs.push(song); }
}

assertEqual('Total songs = 2 (not 3)', allSongs.length, 2);
assert('Custom version kept (album)',  allSongs.find(s => normalize(s.artist) === '50 cent')?.album === "Get Rich Or Die Tryin'");
assert('Aerosmith preserved',          allSongs.some(s => normalize(s.title) === 'toys in the attic'));

// ═════════════════════════════════════════════════════════════════════════════
// Test Suite: Profanity filter
// ═════════════════════════════════════════════════════════════════════════════
console.log('\n── profanity filter ─────────────────────────────────────────────────');
assert('Catches "shit"',               matchesCurse('Song With Shit In It'));
assert('Catches "fuck"',               matchesCurse('F Song Fuck'));
assert('Catches \\bdick\\b',           matchesCurse('Dick Van Dyke')); // intentional: 'dick' triggers filter
assert('Catches "damn"',               matchesCurse('God Damn You'));
assert('Clean line passes',            !matchesCurse('In Da Club - 50 Cent (Custom)'));
assert('Cocks vs cock: cock triggers', matchesCurse('Cock Robin'));
assert('Peacock does not trigger',     !matchesCurse('Peacock')); // \bcock\b — "Peacock" has no word boundary

// ═════════════════════════════════════════════════════════════════════════════
// Summary
// ═════════════════════════════════════════════════════════════════════════════
console.log(`\n${'─'.repeat(60)}`);
console.log(`Results: ${passed} passed, ${failed} failed`);
if (failed > 0) {
  console.error('❌ Some tests failed.');
  process.exit(1);
} else {
  console.log('✅ All tests passed.');
}
