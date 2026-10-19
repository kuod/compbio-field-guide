#!/usr/bin/env node
// Dependency-free sanity checks for the DATA array in index.html.
// Usage: node tests/validate-data.js
const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const script = html.match(/<script>([\s\S]*)<\/script>/)[1];

const start = script.indexOf('const DATA = ');
const end = script.indexOf('\n];', start) + 3;
const DATA = new Function('return ' + script.slice(start + 'const DATA = '.length, end).replace(/;\s*$/, ''))();
const catBlock = script.match(/const catLabels = \{([\s\S]*?)\n\};/)[1];
const CATS = new Set([...catBlock.matchAll(/(\w+)\s*:/g)].map(m => m[1]));

const errors = [];
const err = (id, msg) => errors.push(`id ${id}: ${msg}`);

const seen = new Set();
const pmids = new Map();
const required = ['id', 'year', 'cats', 'impact', 'title', 'authors', 'journal', 'summary', 'pros', 'cons', 'details'];

for (const d of DATA) {
  if (!Number.isInteger(d.id)) err(d.id, 'id is not an integer');
  if (seen.has(d.id)) err(d.id, 'duplicate id');
  seen.add(d.id);
  for (const k of required) if (d[k] == null || d[k] === '') err(d.id, `missing ${k}`);
  if (!Number.isInteger(d.year) || d.year < 1990 || d.year > new Date().getFullYear() + 1) err(d.id, `bad year ${d.year}`);
  if (!Number.isInteger(d.impact) || d.impact < 1 || d.impact > 5) err(d.id, `impact must be 1-5, got ${d.impact}`);
  if (!Array.isArray(d.cats) || d.cats.length === 0) err(d.id, 'cats must be a non-empty array');
  for (const c of d.cats || []) if (!CATS.has(c)) err(d.id, `unknown category "${c}"`);
  for (const k of ['pros', 'cons']) if (!Array.isArray(d[k]) || d[k].some(s => typeof s !== 'string')) err(d.id, `${k} must be a string array`);
  if (!d.papers && !/^https?:\/\//.test(d.url || '')) err(d.id, `url must be http(s): ${d.url}`);
  if (d.pmid != null) {
    if (!/^\d+$/.test(d.pmid)) err(d.id, `bad pmid ${d.pmid}`);
    if (pmids.has(d.pmid)) err(d.id, `pmid ${d.pmid} also used by id ${pmids.get(d.pmid)}`);
    pmids.set(d.pmid, d.id);
  }
  for (const p of d.papers || []) {
    if (!p.label || !/^https?:\/\//.test(p.url || '')) err(d.id, 'papers[] items need label and http(s) url');
    if (p.pmid != null && !/^\d+$/.test(p.pmid)) err(d.id, `bad papers[] pmid ${p.pmid}`);
  }
  if ('job_impact' in d) err(d.id, 'job_impact is unused and must not be shipped');
}

// scripts/pmids.json must mirror the pmids in index.html (index.html is the source of truth).
const json = JSON.parse(fs.readFileSync(path.join(root, 'scripts', 'pmids.json'), 'utf8'));
const expected = Object.fromEntries(DATA.filter(d => d.pmid).map(d => [String(d.id), d.pmid]));
for (const k of new Set([...Object.keys(json), ...Object.keys(expected)])) {
  if (json[k] !== expected[k]) err(k, `scripts/pmids.json has ${json[k]} but index.html has ${expected[k]}`);
}

if (errors.length) {
  console.error(errors.join('\n'));
  console.error(`\n${errors.length} problem(s) in ${DATA.length} entries`);
  process.exit(1);
}
console.log(`OK: ${DATA.length} entries, ${CATS.size} categories`);
