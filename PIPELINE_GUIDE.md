# Max & Mia World — Kompletter Pipeline Guide
> **Lies das VOR JEDEM Chat!** Alle Fehler, Fixes und Learnings dokumentiert.

---

## 🏗️ Architektur-Übersicht

```
GitHub Actions (Ubuntu Cloud — PC kann AUS sein)
│
├── 1. themes.yaml → Lied auswählen (Round-Robin)
├── 2. build_storyboard() → 36 Clips mit 3-Akt-Story
├── 3. Higgsfield Browser → 36 Bilder (Playwright + Xvfb)
│      └── Toggle ON = 0 Credits! (Nano Banana Pro)
├── 4. Higgsfield Browser → 36 Videos animieren
├── 5. Suno Browser → Musik generieren (Fallback: /music/)
├── 6. ffmpeg → 3-Min Video + Shorts zusammenbauen
└── 7. YouTube API → Public Upload (Made for Kids)
```

---

## 📁 Dateistruktur

```
maxmia/
├── .github/workflows/
│   └── daily_pipeline.yml          # GitHub Actions Workflow
├── config/
│   └── themes.yaml                 # 12 Songs mit Lyrics + Storyboard-Info
├── music/                          # Fallback MP3s (in git!)
│   ├── Baa_Baa_Black_Sheep_1.mp3
│   ├── humpty_mix_final.mp3
│   └── ...
├── output/                         # Generierte Videos (gitignored)
├── scripts/
│   ├── pipeline_orchestrator.py    # HAUPTDATEI — orchestriert alles
│   └── restore_credentials.py     # YouTube OAuth aus GitHub Secrets
├── src/
│   ├── higgsfield_cloud.py         # Higgsfield Browser-Automation
│   └── suno_cloud.py               # Suno Browser-Automation
├── youtube/
│   └── upload.py                   # YouTube API Upload
├── state.json                      # Welches Lied als nächstes (Round-Robin)
├── requirements.txt
└── PIPELINE_GUIDE.md               # Diese Datei
```

---

## 🔑 GitHub Secrets (alle erforderlich)

| Secret | Inhalt | Wie setzen |
|--------|--------|-----------|
| `HIGGSFIELD_COOKIES` | base64(JSON Cookie-Array) | Chrome DevTools Console |
| `YOUTUBE_TOKEN_JSON` | base64(OAuth token dict) | `scripts/export_token.py` lokal |
| `YOUTUBE_CLIENT_SECRETS` | base64(client_secrets.json) | Google Cloud Console |
| `SUNO_EMAIL` | makevision1412@gmail.com | direkt |
| `SUNO_PASSWORD` | Mh261296200 | direkt |

### ⚠️ Secrets über PowerShell setzen — BOM-Problem!
PowerShell schreibt UTF-8 BOM in alle Secrets. **IMMER** diese Methode nutzen:
```powershell
# Richtig — kein BOM:
$value = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((Get-Content file.json -Raw)))
gh secret set SECRET_NAME --body $value --repo shinobi1412ai/maxmia

# FALSCH — BOM wird eingefügt:
Get-Content file.json | gh secret set SECRET_NAME  # NIEMALS SO!
```

---

## 🍪 Higgsfield Cookies erneuern (wenn abgelaufen)

Cookies laufen alle paar Wochen ab. Zeichen: `Nicht eingeloggt! HIGGSFIELD_COOKIES erneuern.`

**Schritt 1:** Chrome Canary öffnen → https://higgsfield.ai einloggen  
**Schritt 2:** F12 → Console → einfügen:
```javascript
const c=[]; document.cookie.split(';').forEach(x=>{const[n,...v]=x.trim().split('='); c.push({name:n,value:v.join('='),domain:'higgsfield.ai',path:'/'});}); console.log(btoa(JSON.stringify(c)));
```
**Schritt 3:** Base64-String kopieren  
**Schritt 4:** GitHub Secret aktualisieren:
```powershell
gh secret set HIGGSFIELD_COOKIES --body "BASE64_STRING_HIER" --repo shinobi1412ai/maxmia
```

---

## 🎬 Higgsfield — KRITISCHE REGELN

### Toggle ON = 0 Credits (Nano Banana Pro)
```
Nano Banana Pro Plan:
- Toggle ON (Unlimited) → Bilder: KOSTENLOS, Videos: KOSTENLOS
- Toggle OFF            → Bilder: 2 Credits, Videos: ~10 Credits
```

**`_ensure_unlimited()` prüft den Toggle VOR JEDER Generierung.**  
Wenn Toggle nicht gefunden: Warnung aber weiter (nicht blocken).  
Wenn Toggle OFF: RuntimeError → Abbruch (würde Credits kosten).

### Download mit Session-Cookies (kein 403!)
Higgsfield CDN-URLs (`images.higgs.ai`, CloudFront) brauchen Cookies.  
`urllib.request.urlretrieve` → 403 Forbidden  
`ctx.request.get(url)` → ✅ (Playwright-Kontext hat Session-Cookies)

---

## 🎭 Roter Faden — 3-Akt-Struktur

Jedes Video = echte Geschichte mit Anfang → Spannungsbogen → Ende.

| Akt | Clips | Inhalt |
|-----|-------|--------|
| **1 — Setup** | 1-8 | Max & Mia wachen auf, starten Abenteuer, entdecken das Thema |
| **2 — Adventure** | 9-27 | Liedtext Zeile für Zeile, verschiedene Umgebungen |
| **3 — Triumph** | 28-36 | Sieg, Feier, Regenbogen, Daumen hoch ans Publikum |

**Characters sind IMMER beide sichtbar** (Max + Mia).

---

## 🐛 Bekannte Bugs & Fixes (WICHTIG!)

### BUG 1: UTF-8 BOM in Secrets ⚠️ HÄUFIGSTER FEHLER
```
Fehler: UnicodeEncodeError: 'ascii' codec can't encode character '﻿'
Fehler: JSONDecodeError: Unexpected UTF-8 BOM
```
**Fix:** `_strip_bom()` Funktion ist in `higgsfield_cloud.py` und `restore_credentials.py` eingebaut.  
**Learning:** JEDES Secret das über PowerShell kommt → hat BOM → muss gestripper werden.

### BUG 2: `triple_click()` existiert nicht
```
Fehler: 'Locator' object has no attribute 'triple_click'
```
**Fix:** `await box.click(click_count=3)` — immer so für Dreifachklick in Playwright.

### BUG 3: `networkidle` Timeout
```
Fehler: Page.goto: Timeout 60000ms exceeded
```
**Fix:** `wait_until="domcontentloaded"` + `timeout=90_000` + `_goto_with_retry()` (3x)  
**Warum:** Moderne SPAs feuern immer Background-Requests → `networkidle` wird nie erreicht.

### BUG 4: HTTP 403 beim CDN-Download
```
Fehler: HTTP Error 403: Forbidden
```
**Fix:** `ctx.request.get(url)` statt `urllib.request.urlretrieve()`  
**Warum:** CDN-URLs brauchen Session-Cookies die nur im Playwright-Kontext vorhanden sind.

### BUG 5: Suno Login schlägt fehl (noch offen)
```
Status: Nach Login URL: https://suno.com/sign-in (= nicht eingeloggt)
```
**Workaround:** Fallback auf `/music/*.mp3` Dateien (7 MP3s in git).  
**Echte Lösung:** Suno-Cookies genauso wie Higgsfield-Cookies exportieren.

### BUG 6: Video-Referenzbild Upload
```
Problem: fetch(url) im Browser funktioniert nicht für CDN-Upload
```
**Fix:** `set_input_files(str(local_path))` — lokale Datei direkt in `<input type="file">`  
**Learning:** Für Datei-Uploads in Playwright immer `set_input_files()` nutzen.

---

## 🔄 Workflow — Manuell triggern

```bash
# Status checken
gh run list --repo shinobi1412ai/maxmia --limit 5

# Manuell starten
gh workflow run "Max & Mia World - Daily Video Pipeline" --repo shinobi1412ai/maxmia

# Logs live verfolgen
gh run watch RUN_ID --repo shinobi1412ai/maxmia

# Fehler analysieren
gh run view RUN_ID --repo shinobi1412ai/maxmia --log 2>&1 | grep -v "xkbcomp\|keysym\|Could not" | grep -E "(ERROR|WARNING|✅|❌|Phase)" | head -40
```

---

## 🎵 Musik — Fallback-System

```
1. Suno generiert Song passend zum Thema (Browser-Automation)
   └── Schlägt fehl? → Weiter zu 2.
2. /music/ Ordner — MP3s nach Song-ID suchen
   └── Leer? → Video ohne Musik (selten)
```

**MP3s in /music/ sind in Git** (`.gitignore` hat `!music/*.mp3` Exception).  
Neue MP3s hinzufügen: `git add music/neues_lied.mp3 && git commit && git push`

---

## 📺 YouTube Upload

- **Kategorie:** 27 (Education)
- **Privacy:** public
- **Made for Kids:** ja
- **OAuth Token:** wird aus `youtube/token.pickle` geladen (aus GitHub Secrets wiederhergestellt)
- **Token erneuern:** Lokal `python youtube/get_token.py` → neues pickle → base64 → Secret updaten

---

## 🗺️ themes.yaml — Struktur

```yaml
themes:
  - id: counting-1-10           # URL-safe ID
    title: "Count to 10 with Max and Mia!"
    caption: "YouTube Beschreibung"
    visual_style: "..."          # Higgsfield Image Style
    music_style: "..."           # Suno Musik-Style  
    learn_element: "numbers 1-10" # Was gelernt wird
    lyrics: |
      [Intro]
      [Verse 1]
      [Chorus]
      [Bridge]
      [Outro]
```

`state.json` trackt `last_theme_index` für Round-Robin über alle 12 Songs.

---

## ✅ Deployment Checklist (neu aufsetzen)

- [ ] Repo: `gh repo create shinobi1412ai/maxmia --private`
- [ ] Higgsfield einloggen + Cookies exportieren → `HIGGSFIELD_COOKIES` Secret
- [ ] YouTube OAuth lokal holen → `YOUTUBE_TOKEN_JSON` + `YOUTUBE_CLIENT_SECRETS` Secrets
- [ ] Suno Login testen → `SUNO_EMAIL` + `SUNO_PASSWORD` Secrets
- [ ] `gh workflow run` → ersten Run testen
- [ ] Logs checken: Toggle ON? Bilder gespeichert? Video erstellt?

---

## 🚀 Nächste Verbesserungen (TODO)

- [ ] **Suno Cookies** statt Email/Password (wie Higgsfield)
- [ ] **Claude API** für Storyboard-Generierung (bessere Prompts)
- [ ] **Zweiter Suno Account** als Backup
- [ ] **Thumbnail** auto-generieren (erstes Bild des Videos)
- [ ] **Beschreibung** mit Claude API optimieren (SEO)
- [ ] **Playlist** automatisch befüllen
- [ ] **Telegram/Discord** Notification wenn Video live

---

*Letzte Aktualisierung: Mai 2026 — nach 10+ Debugging-Sessions*
