# 🥚 Humpty Dumpty — Max & Mia World | Projekt-Dokumentation

## Übersicht
Vollautomatisch erstelltes 3-Minuten-Kindervideo für den YouTube-Kanal **"Max & Mia World"**.
- **Video**: 36 einzigartige Clips, 3 Akte, klarer roter Faden, keine Wiederholungen
- **Musik**: 3 Suno-Songs als Medley-Mix (automatisch geloopt + Fade-Out)
- **Tool-Stack**: Higgsfield MCP (Bilder + Videos) · ffmpeg · Python · PowerShell
- **Finales Video**: `humpty_dumpty_v3_FINAL.mp4` (48.6 MB, 3:01 Min)

---

## 📁 Dateistruktur

```
video-animation-kids/
├── music/
│   ├── Humpty Great Fall.mp3          # Suno v4.5 — 1:16 Min
│   ├── Humpty Great Fall (1).mp3      # Suno v4.5 — 1:15 Min
│   ├── Humpy Dumpty Hop (1).mp3       # Suno v4.5 — 1:37 Min
│   └── humpty_mix_final.mp3           # Fertig-Mix: alle 3 Songs, 3:01 Min, Fade-Out
│
└── output/humpty-dumpty/
    ├── clips_norm/                    # 8 Original-Clips (normalisiert)
    ├── new_clips_norm/                # 28 neue Clips (normalisiert)
    ├── concat_story.txt               # ffmpeg Concat-Liste (Story-Reihenfolge)
    ├── story_noaudio.mp4              # Video ohne Audio (3:01 Min)
    ├── concat_v3.txt                  # ffmpeg Concat-Liste v3 (verbesserter roter Faden)
    ├── story_v3_noaudio.mp4           # Video v3 ohne Audio
    └── humpty_dumpty_v3_FINAL.mp4     # 🎬 FINALES VIDEO v3 (3:01 Min, 48.6 MB)
```

---

## 🎬 Video-Struktur v3 (36 Clips × ~5s = 3:01 Min)

> **Roter Faden**: Glücklicher Anfang → Dramatischer Fall → Rettung schlägt fehl → Emotionales Ende → Leben geht weiter

### Akt 1 — HAPPY INTRO: Alle glücklich, Humpty zeigt sich (Clips 1–10, ~50s)
| # | Datei | Inhalt | Warum hier |
|---|-------|--------|------------|
| 1 | v01_wide_meadow | Weite Wiese, sonniger Tag | Welt-Aufbau, schöner Einstieg |
| 2 | v02_maxmia_arrive | Max & Mia kommen begeistert an | Haupt-Charaktere einführen |
| 3 | k26_a_humpty_wall | Humpty sitzt stolz auf der Mauer | Humpty einführen, alles ist normal |
| 4 | v03_humpty_waving | Humpty winkt freundlich | Sympathie aufbauen |
| 5 | v04_humpty_closeup | Close-Up: glückliches Gesicht | Emotionale Verbindung |
| 6 | k26_b_kids_singing | Alle singen zusammen | Nursery Rhyme Moment, Höhepunkt Akt 1 |
| 7 | v05_humpty_showoff | Humpty zeigt Balance-Künste | Foreshadowing: er ist zu mutig! |
| 8 | v06_humpty_dancing | Humpty tanzt stolz | Noch mehr Foreshadowing |
| 9 | v07_maxmia_laughing | Max & Mia lachen | Alles ist perfekt — vor dem Sturm |
| 10 | v08_maxmia_clapping | Alle klatschen mit | Ende Akt 1: alles glücklich |

### Akt 2 — DER FALL + HILFE RUFEN: Drama! (Clips 11–24, ~70s)
| # | Datei | Inhalt | Warum hier |
|---|-------|--------|------------|
| 11 | k26_c_fall_a | Humpty verliert Balance! GEFAHR! | Wendepunkt — direkt nach Glück |
| 12 | v09_humpty_wobbling | Wackeln wird schlimmer | Spannung aufbauen |
| 13 | v10_humpty_tipping | Kippt gefährlich zur Seite | Noch mehr Spannung |
| 14 | v11_humpty_falling | **DER GROSSE FALL!** | Haupt-Ereignis des Videos |
| 15 | 07_fall | CRASH! Aufprall | Impact zeigen |
| 16 | k26_d_fall_b | Humpty liegt gebrochen am Boden | Konsequenz zeigen |
| 17 | v12_eggshell_crash | Eierschalen überall | Ausmaß der Katastrophe |
| 18 | v13_max_reaching | Max eilt hin, versucht zu helfen | Kinder reagieren sofort |
| 19 | v14_mia_eggshells | Mia schaut traurig auf Scherben | Emotionale Reaktion |
| 20 | v15_max_calling | Max ruft nach des Königs Männern! | Lösung wird gesucht |
| 21 | v16_king_throne | König erfährt die Neuigkeit | Hilfe wird aktiviert |
| 22 | v17_trumpeters | Trompeter blasen Alarm | Dringlichkeit, Bewegung |
| 23 | v18_soldiers_galloping | Alle Pferde und Männer galoppieren los | Rettung ist unterwegs! |
| 24 | v19_horses_horizon | Pferde am Horizont — sie kommen! | Hoffnung aufbauen |

### Akt 3 — RETTUNG SCHLÄGT FEHL + EMOTIONALES ENDE (Clips 25–36, ~60s)
| # | Datei | Inhalt | Warum hier |
|---|-------|--------|------------|
| 25 | 05_horses | Königspferde treffen ein | Logisch: Pferde kommen zur Rettung |
| 26 | v20_soldiers_arriving | Soldaten stürmen zur Stelle | Voller Einsatz |
| 27 | v21_soldiers_confused | Ratlose Blicke — wie reparieren? | Wendepunkt: können nicht helfen |
| 28 | v22_soldiers_givingup | Geben traurig auf | Kern der Nursery Rhyme Moral |
| 29 | v28_sad_soldier | Soldat geht Kopf hängend weg | Persönliche Traurigkeit |
| 30 | v23_sad_horses | Pferde senken traurig den Kopf | Alle sind betroffen |
| 31 | v24_maxmia_sad | Max & Mia am Boden zerstört | Kinder-Perspektive |
| 32 | v25_mia_crying | Mia weint für Humpty | Emotionaler Tiefpunkt |
| 33 | v26_sunset_wall | Leere Mauer bei Sonnenuntergang | Humpty ist weg — visuelles Symbol |
| 34 | k26_e_finale | Hoffnungsvolles Finale | Stimmung dreht sich |
| 35 | v27_maxmia_skip | Max & Mia hüpfen davon | Das Leben geht weiter |
| 36 | k26_f_goodbye | Winken zum Abschied | THE END — Kinder winken mit |

---

## 🖼️ Clip-Generierung

### Technischer Ablauf
1. **Referenz-Bild generieren** → Higgsfield MCP `generate_image` (Modell: `nano_banana_2`)
2. **Video aus Bild generieren** → Higgsfield MCP `generate_video` (Modell: `kling2_6`, 5s, 16:9, `start_image`)
3. **Normalisieren** → ffmpeg auf einheitliche Specs

### Normalisierungs-Befehl (alle Clips)
```bash
ffmpeg -y -i input.mp4 -an \
  -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=24" \
  -c:v libx264 -preset fast -crf 23 output.mp4
```
- **Auflösung**: 1280×720 (16:9)
- **FPS**: 24
- **Codec**: H.264
- **Kein Audio** (wird später hinzugefügt)

### concat.txt — Format (ohne BOM!)
```
file 'C:\...\clip1.mp4'
file 'C:\...\clip2.mp4'
```
```powershell
# BOM-freies Schreiben (wichtig für ffmpeg!)
[System.IO.File]::WriteAllLines($path, $lines, [System.Text.UTF8Encoding]::new($false))
```

---

## 🎵 Musik

### Songs
| Datei | Modell | Dauer | Stil |
|-------|--------|-------|------|
| Humpty Great Fall.mp3 | Suno v4.5-all | 1:16 | Children's Music, fast bouncy |
| Humpty Great Fall (1).mp3 | Suno v4.5-all | 1:15 | Children's Music, fast bouncy |
| Humpy Dumpty Hop (1).mp3 | Suno v4.5-all | 1:37 | Upbeat nursery rhyme |

### Suno Prompt (der funktioniert!)
```
Children's nursery rhyme waltz in 3/4 with bouncy folk swing and playful toybox percussion;
verse stays simple and repetitive, glockenspiel melody, xylophone, recorder flute, toy piano
```

### Musik-Mix Befehl
```bash
# 1. Alle 3 Songs aneinander hängen, auf 181.5s kürzen, Fade-Out
ffmpeg -y -f concat -safe 0 -i music_concat.txt \
  -af "atrim=0:181.5,afade=t=out:st=176.5:d=5" \
  -c:a libmp3lame -b:a 192k humpty_mix_final.mp3
```

### Musik auf Video legen
```bash
ffmpeg -y -i story_noaudio.mp4 -i humpty_mix_final.mp3 \
  -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest \
  humpty_dumpty_MUSIC_FINAL.mp4
```

---

## 🔧 Video zusammenbauen

```bash
# Alle 36 Clips zusammenfügen (stream copy, kein Re-encode)
ffmpeg -y -f concat -safe 0 -i concat_story.txt -c copy story_noaudio.mp4
```

---

## ⚙️ Technische Specs — Finales Video

| Parameter | Wert |
|-----------|------|
| Datei | humpty_dumpty_MUSIC_FINAL.mp4 |
| Dauer | 3:01 Min (181.5s) |
| Größe | 48.6 MB |
| Auflösung | 1280×720 (HD) |
| FPS | 24 |
| Video-Codec | H.264 (libx264) |
| Audio-Codec | AAC 192k |
| Clips | 36 einzigartige Clips |
| Musik | 3-Song Medley mit Fade-Out |

---

## ❌ Probleme & Fixes

| Problem | Ursache | Fix |
|---------|---------|-----|
| Clips wiederholten sich | Falsche Concat-Reihenfolge | Neue Story-Logik mit 3 Akten |
| 6 Fall-Clips hintereinander | Alle Fall-Clips in Folge | Auf 3 narrative Fall-Clips reduziert + Reaktionen dazwischen |
| ffmpeg stream mismatch | Verschiedene Codecs/Auflösungen | Alle Clips normalisiert (gleicher Codec, gleiche Auflösung) |
| BOM in concat.txt | PowerShell default UTF-16 | `UTF8Encoding(false)` ohne BOM |
| Suno API nicht erreichbar | `studio-api.suno.ai` suspended | Songs manuell in `music/` Ordner gelegt |
| yt-dlp Chrome Cookie-Fehler | Chrome DB gesperrt (läuft) | Edge-Cookies versucht → auch kein Erfolg → manuell |
| NSFW-Flag bei Bild | Soldat-Gesicht zu realistisch | Prompt angepasst, neues Bild generiert |
| Modell `kling_2_5_turbo` fehlt | Modell nicht mehr verfügbar | Auf `kling2_6` gewechselt |
| Musik zu langsam/langweilig | Falscher Suno-Prompt ohne Lyrics | Prompt mit Humpty Dumpty Melodie-Stil + 3/4 Waltz |

---

## 🐍 Python-Pfade

```
C:\Users\myshi\AppData\Local\Python\bin\python.exe   ← Haupt-Python
C:\Users\myshi\Documents\.venv\Scripts\python.exe    ← venv
```

---

## 📤 YouTube Upload (Vollautomatisch)

### Dateien
```
youtube/
├── upload.py              # Haupt-Upload-Script
├── SETUP_ANLEITUNG.md     # Einrichtungs-Guide
├── client_secrets.json    # ← von Google Cloud Console herunterladen (einmalig)
└── token.pickle           # ← wird automatisch erstellt nach erstem Login
```

### Wie es funktioniert (basiert auf darkzOGx/youtube-automation-agent)
1. **Einmalig**: `client_secrets.json` aus Google Cloud Console → in `youtube/` Ordner
2. **Einmalig**: `python upload.py` → Browser öffnet sich → Google Login → Token gespeichert
3. **Ab dann vollautomatisch**: `python upload.py` → lädt hoch ohne Browser

### Upload-Befehl
```powershell
C:\Users\myshi\AppData\Local\Python\bin\python.exe upload.py
```

### Video-Metadaten (vorkonfiguriert)
- **Titel**: Humpty Dumpty | Max & Mia World | Nursery Rhyme | Kinderlieder
- **Kategorie**: Education (ID: 27)
- **Made for Kids**: Ja
- **Start-Sichtbarkeit**: Privat (zum Prüfen) → dann manuell Öffentlich

### Google Cloud Setup (5 Min, einmalig)
1. console.cloud.google.com → Neues Projekt `MaxMiaWorld`
2. YouTube Data API v3 aktivieren
3. OAuth Client ID erstellen (Desktop App)
4. JSON als `client_secrets.json` speichern

## 📋 Nächste Schritte

- [ ] client_secrets.json aus Google Cloud Console holen
- [ ] `python upload.py` einmal ausführen (Browser-Login)
- [ ] Video prüfen → auf Öffentlich stellen
- [ ] Nächstes Kindervideo planen (Little Bo Peep? Baa Baa Black Sheep?)

---

## 🔑 API Keys & Zugänge

| Service | Key / Info |
|---------|-----------|
| Suno | Pro Account — Songs in `music/` Ordner |
| Higgsfield | MCP Tool (in Claude Code eingebunden) |
| YouTube | Noch einzurichten via Google Cloud Console |

---

*Erstellt: Mai 2026 | Kanal: Max & Mia World*
