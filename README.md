# 🚴 Swiss Cycling – Verbandsstatistiken

Eine statische GitHub Pages Website zur jährlichen Statistikübersicht des Schweizer Radfahrerverbands.

**Live-Demo:** `https://Flo3651.github.io/swiss-cycling-stats/`

---

## ✨ Features

- **4 Themenbereiche:** Lizenzen, Personal, Finanzen, Veranstaltungen
- **Interaktive Charts** mit Zoom, Hover-Tooltips und Vergleichsansichten
- **Light & Dark Mode** – automatisch gespeichert
- **KPI-Karten** mit Jahres-Vergleich (% Veränderung)
- **Responsive Design** – funktioniert auf Handy, Tablet und Desktop
- **Einfache Datenpflege** – nur CSV-Dateien einmal pro Jahr aktualisieren
- **Keine Datenbank, kein Backend** – läuft komplett im Browser

---

## 📁 Projektstruktur

```
swiss-cycling-stats/
├── index.html          ← Hauptseite (alles in einer Datei)
├── data/
│   ├── lizenzen.csv          ← Lizenzen nach Kategorie und Jahr
│   ├── personal.csv          ← Personal und Stellenprozente
│   ├── erfolgsrechnung.csv   ← Ertrag, Aufwand, Ergebnis
│   └── veranstaltungen.csv   ← Rennen, Teilnehmende, Medaillen
└── README.md
```

---

## 🚀 Einrichtung (einmalig)

### 1. Repository erstellen

```bash
# Option A: Auf GitHub.com
# → Neues Repository "swiss-cycling-stats" erstellen (Public)
# → Diese Dateien hochladen

# Option B: Via Git
git clone https://github.com/[username]/swiss-cycling-stats.git
cd swiss-cycling-stats
# Dateien reinkopieren
git add .
git commit -m "Initial setup"
git push
```

### 2. GitHub Pages aktivieren

1. Repository → **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: **main** / Ordner: **/ (root)**
4. Speichern → nach 1–2 Minuten online

Die Seite ist dann erreichbar unter:
`https://Flo3561.github.io/swiss-cycling-stats/`

---

## 📊 Daten aktualisieren (jährlich)

### Lizenzen – `data/lizenzen.csv`

```csv
Jahr,Elite_Männer,Elite_Frauen,U23_Männer,U23_Frauen,Junioren,Juniorinnen,Nachwuchs_Männer,Nachwuchs_Frauen,Masters,Total
2024,412,178,243,97,548,184,1056,338,1723,4779
2025,430,192,...
```

### Personal – `data/personal.csv`

```csv
Jahr,Vollzeitstellen,Teilzeitstellen,Stellenprozente_Total,Davon_Frauen_Prozent,Davon_Männer_Prozent,Lernende,Volunteers
2024,13,17,1920,52,48,3,201
```

### Erfolgsrechnung – `data/erfolgsrechnung.csv`

```csv
Jahr,Ertrag_Lizenzen,Ertrag_Veranstaltungen,Ertrag_Sponsoring,Ertrag_Subventionen,Ertrag_Sonstiges,Ertrag_Total,Aufwand_Personal,Aufwand_Veranstaltungen,Aufwand_Betrieb,Aufwand_Sonstiges,Aufwand_Total,Ergebnis
2024,671200,356400,458000,780000,143800,2409400,1213000,356400,267000,201200,2037600,371800
```

### Veranstaltungen – `data/veranstaltungen.csv`

```csv
Jahr,Rennen_Total,Davon_Strasse,Davon_MTB,Davon_Track,Davon_BMX,Teilnehmende_Total,Internationale_Starts,Medaillen_WM,Medaillen_EM
2024,312,128,118,44,22,26789,438,8,18
```

### So lade ich die Daten hoch

**Option A: Via GitHub.com (einfachste Methode)**
1. `data/lizenzen.csv` auf GitHub.com öffnen
2. Stift-Icon (✏️ Edit) klicken
3. Neue Zeile mit den aktuellen Zahlen hinzufügen
4. Unten "Commit changes" klicken

**Option B: Via Git**
```bash
git pull
# CSV-Datei lokal bearbeiten (z.B. mit Excel → "Speichern als CSV")
git add data/
git commit -m "Daten 2025 aktualisiert"
git push
```

> ⚡ Nach dem Push ist die Website innerhalb von 1–2 Minuten aktualisiert.

---

## 🛠️ Anpassungen

### Neue Kategorie hinzufügen (z.B. Para-Cycling)

1. In `data/lizenzen.csv` neue Spalte `Para_Cycling` hinzufügen
2. In `index.html` suchen nach `const cats = [` und neue Spalte ergänzen
3. In der `catLabels` Liste das Anzeigelabel ergänzen

### Farben anpassen

In `index.html` unter `:root { ... }` die CSS-Variablen ändern:
```css
--c-accent:    #c8102e;   /* Swiss Cycling Rot */
--c-accent2:   #0057a8;   /* Blau */
```

### Neue Sektion hinzufügen

1. Neue CSV-Datei unter `data/` erstellen
2. In `index.html` eine neue `<section>` mit Canvas-Elementen hinzufügen
3. Eine neue `initMeineSektion()` Funktion nach dem Muster der bestehenden erstellen

---

## 🧰 Technologie

| Komponente | Technologie |
|---|---|
| Charts | [Chart.js 4.4](https://www.chartjs.org/) |
| CSV-Parsing | [PapaParse 5.4](https://www.papaparse.com/) |
| Schriften | Google Fonts (Syne + DM Sans) |
| Hosting | GitHub Pages (kostenlos) |
| Backend | Keins – komplett statisch |

---

## 📋 Lizenz

Internes Werkzeug des Schweizer Radfahrerverbands Swiss Cycling.
Nicht zur Weitergabe bestimmt.
