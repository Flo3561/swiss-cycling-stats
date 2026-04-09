#!/usr/bin/env node
/**
 * Swiss Cycling Stats – build.js
 * ─────────────────────────────
 * Liest alle CSV-Dateien aus /data/ und schreibt die Daten
 * direkt als JavaScript-Objekte in die index.html.
 *
 * Ausführen: node build.js
 * Voraussetzung: Node.js (kein npm install nötig)
 */

const fs   = require('fs');
const path = require('path');

// ── CSV Parser (ohne externe Abhängigkeiten) ─────────────────
function parseCSV(content) {
  const lines = content.trim().split('\n').map(l => l.trim()).filter(Boolean);
  const headers = lines[0].split(',').map(h => h.trim());
  return lines.slice(1).map(line => {
    const values = line.split(',');
    const obj = {};
    headers.forEach((h, i) => {
      const v = (values[i] || '').trim();
      obj[h] = isNaN(v) || v === '' ? v : Number(v);
    });
    return obj;
  });
}

// ── Dateien einlesen ─────────────────────────────────────────
const dataDir = path.join(__dirname, 'data');
const datasets = {};

const files = {
  lizenzen:        'lizenzen.csv',
  personal:        'personal.csv',
  erfolgsrechnung: 'erfolgsrechnung.csv',
  veranstaltungen: 'veranstaltungen.csv',
};

for (const [key, filename] of Object.entries(files)) {
  const filePath = path.join(dataDir, filename);
  if (!fs.existsSync(filePath)) {
    console.warn(`⚠️  Nicht gefunden: ${filePath}`);
    continue;
  }
  const content = fs.readFileSync(filePath, 'utf-8');
  datasets[key] = parseCSV(content);
  console.log(`✓  ${filename}: ${datasets[key].length} Zeilen eingelesen`);
}

// ── JavaScript-Block generieren ──────────────────────────────
function toJS(key, data) {
  const rows = data.map(row => {
    const entries = Object.entries(row).map(([k, v]) => {
      return typeof v === 'string' ? `${k}:"${v}"` : `${k}:${v}`;
    });
    return `    {${entries.join(',')}}`;
  }).join(',\n');
  return `  ${key}: [\n${rows},\n  ]`;
}

const newBlock = `/* ══════════════════════════════════════════════════════════════
   EINGEBETTETE DATEN
   → Zum Aktualisieren: neue Zeile am Ende jedes Arrays hinzufügen
   → Format: Objekt mit denselben Schlüsseln wie die CSV-Spalten
   → Alternativ: build.js ausführen um aus CSV-Dateien zu bauen
══════════════════════════════════════════════════════════════ */
const EMBEDDED_DATA = {
${Object.entries(datasets).map(([k, v]) => toJS(k, v)).join(',\n')},
};

function loadCSV(key) {
  // key is e.g. 'data/lizenzen.csv' → extract dataset name
  const name = key.replace('data/','').replace('.csv','');
  const map = {
    lizenzen: 'lizenzen',
    personal: 'personal',
    erfolgsrechnung: 'erfolgsrechnung',
    veranstaltungen: 'veranstaltungen',
  };
  return Promise.resolve(EMBEDDED_DATA[map[name]] || []);
}`;

// ── In index.html einsetzen ──────────────────────────────────
const htmlPath = path.join(__dirname, 'index.html');
let html = fs.readFileSync(htmlPath, 'utf-8');

// Marker: alles zwischen den beiden Kommentarblöcken ersetzen
const startMarker = '/* ══════════════════════════════════════════════════════════════\n   EINGEBETTETE DATEN';
const endMarker   = "  return Promise.resolve(EMBEDDED_DATA[map[name]] || []);\n}";

const startIdx = html.indexOf(startMarker);
const endIdx   = html.indexOf(endMarker) + endMarker.length;

if (startIdx === -1 || endIdx < endMarker.length) {
  console.error('❌  Marker in index.html nicht gefunden. Bitte nicht manuell verändern.');
  process.exit(1);
}

html = html.slice(0, startIdx) + newBlock + html.slice(endIdx);
fs.writeFileSync(htmlPath, html, 'utf-8');

console.log('\n✅  index.html erfolgreich aktualisiert!');
console.log('   Öffne index.html im Browser um das Ergebnis zu sehen.\n');
