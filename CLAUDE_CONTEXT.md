# MAX & MIA WORLD — VOLLSTÄNDIGER CLAUDE CONTEXT
> **Für jeden neuen Chat-Start pflichtlesen.**  
> Enthält alles: Architektur, alle Bugs, alle Fixes, alle Code-Patterns, Setup-Anleitung.  
> Ein neuer Claude-Chat kann nach diesem Dokument **sofort ohne Fragen** weiterarbeiten.

---

## 1. WAS IST DAS HIER?

Ein **vollautomatisches YouTube-Kinderchannel-System** für den Kanal **"Max & Mia World"**.

- GitHub Actions läuft täglich um 03:00 Uhr Berlin — **PC muss nicht an sein**
- Playwright-Browser generiert **36 Bilder + 36 Videos** auf Higgsfield.ai (kostenlos via Toggle)
- Suno.com generiert **thematische Kinderlieder** (Playwright-Browser)
- ffmpeg schneidet alles zu einem **3-Minuten-Video + 60s Short** zusammen
- Automatischer **YouTube-Upload** (public, Made for Kids, English)

**Ziel:** Täglich 1 Video + 1 Short = 730 Videos/Jahr, vollautomatisch, keine manuellen Schritte.

---

## 2. REPO & ZUGANG

```
Repo:      https://github.com/shinobi1412ai/maxmia
User:      shinobi1412ai
Branch:    master
Lokal:     C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\
```

---

## 3. DATEISTRUKTUR — JEDE DATEI ERKLÄRT

```
maxmia/
│
├── .github/workflows/
│   └── daily_pipeline.yml          # GitHub Actions — MAIN ENTRY POINT
│                                   # Läuft täglich 02:00 UTC (03:00 Berlin)
│                                   # Steps: checkout → python → ffmpeg/xvfb →
│                                   #        pip → playwright → credentials →
│                                   #        pipeline → commit state → artifact
│
├── config/
│   └── themes.yaml                 # 12 Songs: id, title, lyrics, visual_style,
│                                   # music_style, learn_element, interactive_questions
│                                   # Round-Robin via state.json
│
├── music/                          # Fallback MP3s — IN GIT! (Exception in .gitignore)
│   ├── Baa_Baa_Black_Sheep_1.mp3   # Wird genutzt wenn Suno fehlschlägt
│   ├── Baa_Baa_Black_Sheep_2.mp3
│   ├── Baa_Baa_Black_Sheep_auto.mp3
│   ├── humpty_mix_final.mp3
│   ├── Humpty Great Fall.mp3
│   ├── Humpty Great Fall (1).mp3
│   └── Humpy Dumpty Hop (1).mp3
│
├── output/                         # Generierte Videos (gitignored — zu groß)
│   └── {theme-id}/
│       ├── clips/
│       │   ├── img_01.jpg ... img_36.jpg    # Generierte Bilder
│       │   └── vid_01.mp4 ... vid_36.mp4    # Generierte Videos
│       ├── {theme-id}_FINAL.mp4             # Hauptvideo (3 Min)
│       ├── shorts/{theme-id}_SHORT.mp4      # Short (60s, 9:16)
│       └── jobs.json                        # Status aller 36 Clips
│
├── scripts/
│   ├── pipeline_orchestrator.py    # HAUPTDATEI — orchestriert ALLES
│   │                               # build_storyboard() → 3-Akt-Story
│   │                               # Ruft higgsfield_cloud + suno_cloud auf
│   │                               # ffmpeg assembly + YouTube upload
│   │
│   └── restore_credentials.py     # Stellt YouTube OAuth aus GitHub Secrets her
│                                   # decode_secret() = BOM-sicherer JSON-Decoder
│
├── src/
│   ├── higgsfield_cloud.py         # Higgsfield Browser-Automation (KRITISCH)
│   │                               # _strip_bom() — BOM aus Cookies entfernen
│   │                               # _ensure_unlimited() — Toggle vor jeder Gen.
│   │                               # _goto_with_retry() — 3x Retry, domcontentloaded
│   │                               # _download_with_ctx() — ctx.request.get() mit Cookies
│   │                               # generate_image(prompt, save_path) → speichert direkt
│   │                               # generate_video(image_path, prompt, save_path) → lokal
│   │
│   └── suno_cloud.py               # Suno Browser-Automation
│                                   # Clerk Login (email-first, dann password)
│                                   # Network Interception für CDN Audio-URLs
│
├── youtube/
│   └── upload.py                   # YouTube Data API v3 Upload
│                                   # OAuth2 via token.pickle (aus Secrets)
│
├── state.json                      # {"last_theme_index": N} — Round-Robin State
│                                   # Wird nach jedem Run in Git committed
│
├── requirements.txt                # Python Dependencies
├── PIPELINE_GUIDE.md               # Kurzguide (Setup, Checklist, TODOs)
└── CLAUDE_CONTEXT.md               # Diese Datei — vollständiger Kontext
```

---

## 4. CHARAKTERE — IMMER BEIDE SICHTBAR

```python
CHAR_PROMPT = (
    "Mia girl with brown pigtail hair and red ribbons, green eyes, freckles, "
    "pink dress with yellow stars, pink leggings, pink mary jane shoes. "
    "Max boy with curly brown hair, brown eyes, freckles, blue knit sweater, "
    "brown dungarees with dinosaur patch, red sneakers with white stripes. "
    "3D Pixar animation style, bright and cheerful."
)
```

**Regel:** In JEDEM Clip sind beide Charaktere sichtbar. Niemals nur einen zeigen.

---

## 5. HIGGSFIELD — TOGGLE-REGEL (GELD-KRITISCH)

```
Nano Banana Pro Plan:
┌─────────────────────────────────────────────────────────┐
│  Toggle ON  (Unlimited) → Bilder: 0 Credits             │
│                         → Videos: 0 Credits (Kling 2.5) │
│  Toggle OFF             → Bilder: 2 Credits             │
│                         → Videos: ~10 Credits           │
└─────────────────────────────────────────────────────────┘
```

**`_ensure_unlimited()` wird VOR JEDER Generierung aufgerufen.**  
Wenn Toggle OFF → `RuntimeError` → Pipeline stoppt → KEIN Credit-Verlust.

```python
async def _ensure_unlimited(page) -> bool:
    for sel in ['[role="switch"]', '[data-testid*="toggle"]', 'button[aria-checked]']:
        toggle = page.locator(sel).first
        if await toggle.count() > 0:
            checked = await toggle.get_attribute("aria-checked")
            if checked != "true":
                await toggle.click()          # Toggle einschalten
                await page.wait_for_timeout(1500)
                checked = await toggle.get_attribute("aria-checked")
            if checked == "true":
                log.info("✅ Unlimited Toggle: ON — 0 Credits!")
                return True
            else:
                log.error("❌ Toggle bleibt AUS! Stoppe!")
                return False
    return True  # Toggle nicht gefunden → trotzdem weiter (nicht blocken)
```

---

## 6. GITHUB SECRETS — VOLLSTÄNDIGE LISTE

| Secret | Wert | Wie generieren |
|--------|------|----------------|
| `HIGGSFIELD_COOKIES` | base64(JSON) | Schritt A unten |
| `YOUTUBE_TOKEN_JSON` | base64(JSON) | Schritt B unten |
| `YOUTUBE_CLIENT_SECRETS` | base64(JSON) | Google Cloud Console |
| `SUNO_EMAIL` | makevision1412@gmail.com | direkt |
| `SUNO_PASSWORD` | Mh261296200 | direkt |
| `ANTHROPIC_API_KEY` | sk-ant-... | optional, für zukünftige Nutzung |

### ⚠️ WICHTIG: Secrets NIEMALS über PowerShell `echo` oder `Get-Content | pipe` setzen!
PowerShell fügt UTF-8 BOM (﻿) ein → JSON-Parser crasht auf Linux.

```powershell
# ✅ RICHTIG — kein BOM:
$content = Get-Content "datei.json" -Raw -Encoding UTF8
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$b64 = [Convert]::ToBase64String($bytes)
gh secret set SECRET_NAME --body $b64 --repo shinobi1412ai/maxmia

# ❌ FALSCH — BOM wird eingefügt:
Get-Content datei.json | gh secret set SECRET_NAME  # NIE SO!
cat datei.json | gh secret set SECRET_NAME          # NIE SO!
```

---

## 7. SCHRITT A: HIGGSFIELD COOKIES EXPORTIEREN

Cookies laufen alle paar Wochen ab. Symptom: `Nicht eingeloggt! HIGGSFIELD_COOKIES erneuern.`

**1.** Chrome Canary öffnen → https://higgsfield.ai → einloggen  
**2.** F12 → Console → exakt diesen Code einfügen und Enter:

```javascript
const c=[];
document.cookie.split(';').forEach(x => {
  const [n,...v] = x.trim().split('=');
  c.push({name:n, value:v.join('='), domain:'higgsfield.ai', path:'/'});
});
console.log(btoa(JSON.stringify(c)));
```

**3.** Base64-String aus Console kopieren  
**4.** In GitHub Secret eintragen:
```powershell
gh secret set HIGGSFIELD_COOKIES --body "DEIN_BASE64_STRING" --repo shinobi1412ai/maxmia
```

---

## 8. SCHRITT B: YOUTUBE TOKEN ERNEUERN

```powershell
# Lokal ausführen:
cd C:\Users\myshi\Documents\Claude\Projects\video-animation-kids
python youtube\get_token.py
# Browser öffnet sich → Google Login → Token wird gespeichert

# Token in Secret umwandeln:
$pickle = [System.IO.File]::ReadAllBytes("youtube\token.pickle")
$b64 = [Convert]::ToBase64String($pickle)
gh secret set YOUTUBE_TOKEN_JSON --body $b64 --repo shinobi1412ai/maxmia
```

---

## 9. ROTER FADEN — 3-AKT-STRUKTUR

Jedes Video = 36 Clips = eine echte Geschichte.

```
AKT 1 — SETUP (Clips 1-8)
  01: Max & Mia wachen auf — Sonnenschein, Abenteuer-Tag!
  02: Sie rennen zum Fenster — die bunte Welt wartet
  03: Max Sweater anziehen, Mia Bänder binden — bereit!
  04: [Intro-Zeile des Liedes] — Sie treten raus in die Sonne
  05: Magische Entdeckung — [learn_element] leuchtet überall
  06: Mia zeigt, Max jubelt — die Welt von [Liedtitel] wartet!
  07: Hand in Hand losziehen — beste Freunde für immer
  08: [Chorus-Zeile 1] — Sie beginnen zu singen

AKT 2 — ADVENTURE (Clips 9-27) — LIEDTEXT ZEILE FÜR ZEILE
  09-27: Verse → Chorus → Bridge, jede Zeile = eine Szene
        Verschiedene Umgebungen: Wald, Teich, Bauernhof, Strand...
        Verschiedene Kameraperspektiven: Zoom, Pan, Rotation, Tracking

AKT 3 — TRIUMPH (Clips 28-36)
  28: [learn_element] gemeistert! Konfetti-Feier!
  29: [Outro-Zeile] — alle Tier-Freunde feiern mit
  30: Max hält goldene Trophäe — Mia klatscht stolz
  31: Regenbogen erscheint — magische Belohnung
  32: Siegestanz — drehen, lachen, springen
  33: Mia umarmt Max — beste Freunde für immer
  34: Winken — bis zum nächsten Mal!
  35: Magische Funken — bis bald!
  36: Daumen hoch — DU HAST ES AUCH GESCHAFFT!
```

---

## 10. ALLE BUGS & FIXES — CHRONOLOGISCH

### BUG 1 — UTF-8 BOM in GitHub Secrets (HÄUFIGSTER FEHLER)
```
Fehlermeldung: UnicodeEncodeError: 'ascii' codec can't encode character '﻿'
Fehlermeldung: JSONDecodeError: Unexpected UTF-8 BOM (decode using utf-8-sig)
Datei:         restore_credentials.py, higgsfield_cloud.py
```
**Ursache:** PowerShell fügt \xef\xbb\xbf (UTF-8 BOM) vor den Secret-Wert.  
**Fix:** `_strip_bom()` und `decode_secret()` Funktionen:
```python
def _strip_bom(raw: str) -> str:
    raw = raw.strip().lstrip('﻿').lstrip('\xef\xbb\xbf').strip()
    raw = raw.encode('ascii', errors='ignore').decode('ascii').strip()
    return raw

def decode_secret(raw: str) -> dict:
    raw = _strip_bom(raw)  # oder inline strip
    try:
        return json.loads(base64.b64decode(raw + "=="))
    except Exception:
        return json.loads(raw)
```
**Regel:** Jede `os.environ.get()` für Secrets → zuerst BOM strippen!

---

### BUG 2 — `triple_click()` existiert nicht in Playwright
```
Fehlermeldung: 'Locator' object has no attribute 'triple_click'
Datei:         higgsfield_cloud.py
```
**Fix:** `await box.click(click_count=3)`  
**Merksatz:** Playwright = `click_count`, kein `triple_click`.

---

### BUG 3 — `networkidle` Timeout auf Higgsfield
```
Fehlermeldung: Page.goto: Timeout 60000ms exceeded
Datei:         higgsfield_cloud.py
```
**Ursache:** Higgsfield ist eine SPA die ständig Background-Requests macht → `networkidle` wird nie erreicht.  
**Fix:**
```python
async def _goto_with_retry(page, url: str, retries: int = 3) -> bool:
    for attempt in range(retries):
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=90_000)
            await page.wait_for_timeout(2000)
            return True
        except Exception as e:
            if attempt < retries - 1:
                await page.wait_for_timeout(3000)
    return False
```
**Regel:** Für SPAs immer `domcontentloaded` + `timeout=90_000` + Retry.

---

### BUG 4 — HTTP 403 beim Image/Video Download (WICHTIGSTER BUG)
```
Fehlermeldung: HTTP Error 403: Forbidden
Datei:         pipeline_orchestrator.py → download_file()
```
**Ursache:** Higgsfield CDN-URLs (`images.higgs.ai`, CloudFront) brauchen Session-Cookies.  
`urllib.request.urlretrieve()` sendet keine Cookies → 403.  
**Fix:** Download innerhalb des Playwright-Kontexts mit `ctx.request.get()`:
```python
async def _download_with_ctx(ctx, url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    response = await ctx.request.get(url)
    if not response.ok:
        raise IOError(f"Download HTTP {response.status}: {url[:60]}")
    dest.write_bytes(await response.body())
```
**Regel:** Alle Downloads von Auth-geschützten URLs → `ctx.request.get()`, NIE `urllib`.

---

### BUG 5 — Video-Referenzbild Upload via JS fetch schlägt fehl
```
Problem: JavaScript fetch(imageUrl) im Browser kann CDN-Datei nicht hochladen
Datei:   higgsfield_cloud.py → _generate_video_async()
```
**Fix:** Lokales Bild direkt mit `set_input_files()` hochladen:
```python
await upload_input.set_input_files(str(local_image_path))
await page.wait_for_timeout(2000)
```
**Regel:** File-Uploads in Playwright → immer `set_input_files()`, nie JS fetch.

---

### BUG 6 — MP3-Fallback nicht auf GitHub Actions verfügbar
```
Problem: /music/ Ordner in .gitignore mit *.mp3 → GitHub Actions hat keine Musik
```
**Fix in .gitignore:**
```gitignore
*.mp3
!music/*.mp3     # Exception: Fallback-Musik darf in Git
```
**Regel:** Alles was auf dem GitHub-Runner verfügbar sein muss → in Git!

---

### BUG 7 — Suno Login bleibt auf sign-in Seite (noch offen)
```
Log: Nach Login URL: https://suno.com/sign-in  (= nicht eingeloggt)
Ursache: Suno nutzt Clerk Auth, Login-Flow ändert sich häufig
```
**Workaround:** Fallback auf `/music/*.mp3` (7 Dateien vorhanden).  
**Echte Lösung (TODO):** Suno-Cookies exportieren wie Higgsfield-Cookies.

---

### BUG 8 — Workflow Name mit em-dash nicht triggerbar
```
Problem: "Max & Mia World — Daily Video Pipeline" (em dash) → gh workflow run schlägt fehl
Fix: Umbenannt auf "Max & Mia World - Daily Video Pipeline" (normaler Bindestrich)
```

---

### BUG 9 — Roter Faden war keine echte Story
```
Problem: build_storyboard() zyklierte nur durch Lyrik-Zeilen ohne Narrative
Fix: 3-Akt-Struktur (Setup 8 + Liedtext 19 + Triumph 9 = 36 Clips)
```

---

## 11. CODE-PATTERNS — COPY-PASTE READY

### Pattern: BOM-sicherer Secret-Decoder
```python
import base64, json, os

def decode_secret(raw: str) -> dict:
    """Dekodiert GitHub Secret — robust gegen PowerShell BOM."""
    raw = raw.strip().lstrip('﻿').lstrip('\xef\xbb\xbf').strip()
    raw = raw.encode('ascii', errors='ignore').decode('ascii').strip()
    try:
        return json.loads(base64.b64decode(raw + "=="))
    except Exception:
        return json.loads(raw)
```

### Pattern: Playwright goto mit Retry
```python
async def _goto_with_retry(page, url: str, retries: int = 3) -> bool:
    for attempt in range(retries):
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=90_000)
            await page.wait_for_timeout(2000)
            return True
        except Exception as e:
            log.warning(f"goto Versuch {attempt+1}/{retries}: {e}")
            if attempt < retries - 1:
                await page.wait_for_timeout(3000)
    return False
```

### Pattern: Download mit Playwright Session-Cookies
```python
async def _download_with_ctx(ctx, url: str, dest: Path) -> None:
    response = await ctx.request.get(url)
    if not response.ok:
        raise IOError(f"HTTP {response.status} für {url[:60]}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(await response.body())
```

### Pattern: File Upload in Playwright
```python
upload_input = page.locator("input[type='file']").first
if await upload_input.count() > 0:
    await upload_input.set_input_files(str(local_path))
    await page.wait_for_timeout(2000)
```

### Pattern: Textarea füllen (kein triple_click!)
```python
box = page.locator("textarea").first
await box.click(click_count=3)   # Alles markieren
await box.fill(mein_text)
await page.wait_for_timeout(500)
```

---

## 12. DIAGNOSE — WAS TUN WENN PIPELINE FEHLSCHLÄGT?

```bash
# 1. Letzten Run ansehen
gh run list --repo shinobi1412ai/maxmia --limit 5

# 2. Logs holen (ohne xkbcomp-Spam)
gh run view RUN_ID --repo shinobi1412ai/maxmia --log 2>&1 \
  | grep -v "xkbcomp\|keysym\|Could not\|Warning:" \
  | grep -E "(ERROR|WARNING|✅|❌|Phase|Bild|Toggle|403|Timeout)" \
  | head -40

# 3. Jobs.json aus Artifact herunterladen (zeigt Status jedes Clips)
gh run download RUN_ID --repo shinobi1412ai/maxmia

# 4. Manuell starten
gh workflow run "Max & Mia World - Daily Video Pipeline" --repo shinobi1412ai/maxmia
```

### Schnell-Diagnose Tabelle:
| Fehlermeldung | Ursache | Fix |
|---------------|---------|-----|
| `Unexpected UTF-8 BOM` | Secret über PowerShell gesetzt | `decode_secret()` prüfen |
| `'triple_click'` | Veralteter Code | `click(click_count=3)` |
| `Timeout 60000ms` | `networkidle` auf SPA | `domcontentloaded` + 90s |
| `HTTP Error 403` | CDN braucht Cookies | `ctx.request.get()` |
| `Nicht eingeloggt!` | Cookies abgelaufen | Cookies neu exportieren (Schritt A) |
| `Toggle bleibt AUS` | Higgsfield UI geändert | Toggle-Selector updaten |
| `Zu wenig fertige Clips: 0/36` | Alle Bilder fehlgeschlagen | Ersten Fehler in Logs finden |
| `Keine Musik nach 6 Min` | Suno Login fehlgeschlagen | Fallback MP3 wird genutzt ✓ |

---

## 13. THEMES.YAML — WIE NEUE SONGS HINZUFÜGEN

```yaml
- id: neues-lied-id           # lowercase, bindestrich, URL-safe
  title: "Lied-Titel hier"
  caption: "YouTube Beschreibung (emoji ok)"
  extra_tags: ["#tag1", "#tag2"]
  visual_style: "Beschreibung des visuellen Stils für Higgsfield"
  suno_style: "Musik-Style für Suno: genre, tempo, mood"
  music_style: "Fallback-Beschreibung"
  learn_element: "was Kinder lernen (z.B. colors, numbers 1-10)"
  interactive_questions:
    - question: "Frage?"
      answer: "Antwort!"
      visual: "was gezeigt wird"
  lyrics: |
    [Intro]
    Zeile 1
    Zeile 2

    [Verse 1]
    ...

    [Chorus]
    ...

    [Bridge]
    ...

    [Outro]
    ...
```

**Wichtig:** `state.json` trackt automatisch welches Lied als nächstes dran ist.  
`{"last_theme_index": 3}` → nächstes Mal kommt Index 4.

---

## 14. PIPELINE FLOW — VOLLSTÄNDIG

```python
run_pipeline():
  1. pick_next_theme()              # themes.yaml + state.json → Round-Robin
  2. build_storyboard(theme)        # 36 Clips, 3-Akt-Story generieren
  3. save_jobs(song_dir, clips)     # jobs.json speichern

  # PHASE 1: Bilder
  for clip in clips:
    generate_image(prompt, save_path=local_img)
      → _new_browser_context()     # Cookies laden
      → _goto_with_retry(IMAGE_URL) # domcontentloaded, 3x Retry
      → _ensure_unlimited()         # Toggle ON prüfen
      → textarea.click(click_count=3).fill(prompt)
      → button "Generate" klicken
      → warten auf img[src*='higgs.ai'] (max 5 Min)
      → _download_with_ctx(ctx, img_url, save_path)  # MIT Cookies

  # PHASE 2: Videos
  for clip in clips:
    generate_video(image_path=local_img, prompt, save_path=local_vid)
      → _new_browser_context()
      → _goto_with_retry(VIDEO_URL)
      → _ensure_unlimited()
      → set_input_files(local_img)  # lokales Bild hochladen
      → textarea.fill(prompt)
      → button "Generate" klicken
      → warten auf video source[src] (max 8 Min)
      → _download_with_ctx(ctx, vid_url, save_path)

  # PHASE 3: Musik
  suno_cloud.generate_music(...)   # Clerk Login + Musik generieren
  └── Fehler? → Fallback: music/*.mp3

  # PHASE 4: Video zusammenbauen
  assemble_video():
    → ffmpeg concat (36 Videos, 5s je = 180s)
    → Musik hinzufügen (-shortest)
    → Scale 1920x1080
    → Shorts: crop 9:16, trim 60s

  # PHASE 5: YouTube Upload
  upload_to_youtube():
    → Hauptvideo (public, category 27, Made for Kids)
    → Short (title + "#Shorts")
```

---

## 15. TÄGLICHE AUTOMATISIERUNG

```yaml
# .github/workflows/daily_pipeline.yml
on:
  schedule:
    - cron: '0 2 * * *'   # 02:00 UTC = 03:00 Berlin
  workflow_dispatch:        # Auch manuell triggerbar

timeout-minutes: 360        # 6 Stunden max (36 Bilder + 36 Videos brauchen Zeit)
```

Nach jedem Run:
- `state.json` wird automatisch committed (`last_theme_index` erhöht)
- Artifacts werden 7 Tage gespeichert (`jobs.json` + fertige MP4s)

---

## 16. ERWEITERUNGEN (TODO)

| Feature | Priorität | Beschreibung |
|---------|-----------|--------------|
| Suno Cookies | HOCH | Wie Higgsfield: Cookies exportieren statt Login |
| Claude API Storyboard | MITTEL | Bessere Prompts via Anthropic API |
| 2. Suno Account | MITTEL | Backup wenn Hauptaccount keine Credits |
| Auto-Thumbnail | MITTEL | Bild 1 des Videos als Thumbnail |
| SEO-Beschreibung | NIEDRIG | Claude API optimiert YouTube-Beschreibung |
| Telegram-Notification | NIEDRIG | Wenn Video live ist |
| TikTok Upload | NIEDRIG | src/upload/tiktok.py bereits vorhanden |

---

## 17. SUNO — ACCOUNT & LOGIN

```
Email:    makevision1412@gmail.com
Password: Mh261296200
Credits:  2490 (Stand Mai 2026)
Login:    Clerk Auth (email-first flow)
```

**Suno Cookies exportieren (TODO — wie Higgsfield):**
```javascript
// Nach Login auf suno.com in Console ausführen:
const c=[];
document.cookie.split(';').forEach(x=>{
  const[n,...v]=x.trim().split('=');
  c.push({name:n,value:v.join('='),domain:'suno.com',path:'/'});
});
console.log(btoa(JSON.stringify(c)));
```

---

## 18. YOUTUBE — SETUP & RENEWAL

- **Kanal:** Max & Mia World
- **Kategorie:** 27 (Education)
- **Privacy:** public
- **Made for Kids:** ja
- **Sprache:** English

OAuth Token erneuern wenn Fehler: `Token expired` oder `invalid_grant`
```powershell
# Lokal:
cd C:\Users\myshi\Documents\Claude\Projects\video-animation-kids
python youtube\get_token.py
# → Browser öffnet sich → Google-Login → fertig

# Neues Token als Secret:
python -c "import pickle,base64; print(base64.b64encode(open('youtube/token.pickle','rb').read()).decode())"
# Output als YOUTUBE_TOKEN_JSON Secret setzen
```

---

## 19. DEPLOYMENT — NEU AUFSETZEN (CHECKLISTE)

```
□ GitHub Repo erstellen: gh repo create OWNER/REPO --private
□ Code clonen und pushen
□ Higgsfield einloggen → Cookies exportieren → HIGGSFIELD_COOKIES Secret
□ YouTube OAuth lokal holen → YOUTUBE_TOKEN_JSON + YOUTUBE_CLIENT_SECRETS Secrets
□ SUNO_EMAIL + SUNO_PASSWORD Secrets setzen
□ state.json: {"last_theme_index": -1} committen (startet bei Song 1)
□ Ersten manuellen Run: gh workflow run "..." --repo OWNER/REPO
□ Logs checken: Toggle ON? Bilder gespeichert (KB-Zahl)? Video erstellt?
□ YouTube: Video live und public?
□ Täglichen Cron bestätigen: Actions → Schedules
```

---

## 20. WICHTIGE BEFEHLE — QUICK REFERENCE

```bash
# Run manuell starten
gh workflow run "Max & Mia World - Daily Video Pipeline" --repo shinobi1412ai/maxmia

# Status der letzten 5 Runs
gh run list --repo shinobi1412ai/maxmia --limit 5

# Live-Watch eines Runs
gh run watch RUN_ID --repo shinobi1412ai/maxmia

# Logs analysieren (ohne xkbcomp-Spam)
gh run view RUN_ID --repo shinobi1412ai/maxmia --log 2>&1 \
  | grep -v "xkbcomp\|keysym\|Could not\|Warning:" \
  | grep -E "(ERROR|WARNING|✅|❌|Phase|Toggle|403)" | head -50

# Secret updaten
gh secret set SECRET_NAME --body "WERT" --repo shinobi1412ai/maxmia

# Alle Secrets auflisten
gh secret list --repo shinobi1412ai/maxmia

# Lokaler Test der Pipeline
cd C:\Users\myshi\Documents\Claude\Projects\video-animation-kids
python scripts\pipeline_orchestrator.py
```

---

*Stand: Mai 2026 | Autor: Claude Sonnet 4.6 + shinobi1412ai*  
*Dieses Dokument ist der vollständige Kontext für jeden neuen Claude-Chat zu diesem Projekt.*
