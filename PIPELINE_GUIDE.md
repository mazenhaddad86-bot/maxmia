# Max & Mia World — Vollständiger Pipeline Guide
> **ZUERST LESEN! Vor jedem Chat, vor jedem Run.** Alle Learnings von Tag 0 bis heute.

Zuletzt aktualisiert: 2026-05-16 (nach 5 Tagen Debugging)

---

## 1. Was wir bauen

Ein **vollautomatischer YouTube-Kanal für Kinder** — läuft täglich auf GitHub Actions, kein PC nötig.

```
GitHub Actions (täglich 02:00 UTC)
  → Higgsfield Browser (36 Bilder + 36 Videos) — KOSTENLOS mit Toggle ON
  → Suno (Kinderlieder-Musik)
  → ffmpeg (alles zusammenbauen → 3 Min MP4)
  → YouTube Upload (public, Made for Kids, English)
```

- **Kanal:** Max & Mia World
- **Repo:** https://github.com/shinobi1412ai/maxmia
- **GitHub User:** shinobi1412ai
- **Cron:** täglich 02:00 UTC (03:00 Berlin)

---

## 2. Die Charaktere (IMMER in jedem Clip)

### Mia (Mädchen)
- Braune Haare in **ZWEI Zöpfen mit ROTEN Schleifen**
- Grüne Augen, Sommersprossen
- Rosa Kleid mit gelben Sternen, rosa Leggings, rosa Mary Jane Schuhe

### Max (Junge)
- **Lockige** braune Haare, braune Augen, Sommersprossen
- Blaues Strickpulli, braune Latzhose mit **Dino-Aufnäher** auf Brusttasche
- Rote Turnschuhe mit weißen Streifen

### Basis-Prompt (IMMER als Prefix verwenden)
```
Mia girl with brown pigtail hair and red ribbons, green eyes, freckles,
pink dress with yellow stars, pink leggings, pink mary jane shoes.
Max boy with curly brown hair, brown eyes, freckles, blue knit sweater,
brown dungarees with dinosaur patch, red sneakers with white stripes.
3D Pixar animation style, bright and cheerful.
```

---

## 3. DIE WICHTIGSTE REGEL: Higgsfield Kosten

```
⚠️⚠️⚠️ NIEMALS AUCH NUR 1 CREDIT BENUTZEN ⚠️⚠️⚠️

Browser + Unlimited Toggle ON = 0 Credits
  Bilder: Nano Banana Pro  →  GRATIS (0 Credits)
  Videos: Kling 2.5 Turbo  →  GRATIS (0 Credits)

API = IMMER Credits (10/Video, 2/Bild) → NIEMALS API nutzen!
Toggle AUS = Credits! → Sofort abbrechen!
```

### Toggle-Check (vor JEDER Generierung!)
- Toggle-Selector: `div:has-text("Unlimited") > [role="switch"]`
- `aria-checked` muss `"true"` sein
- `_ensure_unlimited()` macht das automatisch — niemals überspringen!

---

## 4. GitHub Secrets — Vollständige Liste

Alle in `shinobi1412ai/maxmia` → Settings → Secrets → Actions:

| Secret | Inhalt | Wie erstellen |
|--------|--------|---------------|
| `HIGGSFIELD_EMAIL` | makevision1412@gmail.com | Direkt |
| `GMAIL_APP_PASSWORD` | 16-stellig (kein Leerzeichen) | myaccount.google.com → Sicherheit → App-Passwörter |
| `HIGGSFIELD_COOKIES` | base64 JSON (Session-Cookies) | Siehe Abschnitt 6 |
| `YOUTUBE_TOKEN_JSON` | base64 JSON | `python scripts/setup_youtube_oauth.py` |
| `YOUTUBE_CLIENT_SECRETS` | base64 JSON | Google Cloud Console |
| `SUNO_EMAIL` | makevision1412@gmail.com | Direkt |
| `SUNO_PASSWORD` | Suno Passwort | Direkt |
| `ANTHROPIC_API_KEY` | sk-ant-... | anthropic.com |

**NICHT mehr genutzt:** `HIGGSFIELD_PASSWORD` (Higgsfield hat kein Passwort-Login!)

### Secret via CLI setzen (empfohlen — kein BOM-Problem!)
```bash
gh secret set GMAIL_APP_PASSWORD --repo shinobi1412ai/maxmia --body "xzrjyztrnmffkteq"
gh secret set HIGGSFIELD_EMAIL --repo shinobi1412ai/maxmia --body "makevision1412@gmail.com"
```

---

## 5. Higgsfield Login — Wie es wirklich funktioniert

### Hintergrund (warum das so komplex ist)
Higgsfield nutzt **Clerk Auth** mit Email OTP — KEIN Passwort-Login!
- Clerk JWT (`__session` Cookie) läuft nach **~60 Minuten** ab
- Nach Ablauf zeigt Higgsfield "Log in" Button aber URL bleibt `/ai/image` (kein Redirect!)
- Google OAuth wird von Google für automatisierte Logins geblockt
- Lösung: Email OTP + **Gmail IMAP** liest den Code automatisch

### Login-Flow (vollautomatisch nach Fix)
```
1. Cookies laden → Higgsfield.ai öffnen
2. Cookie-Banner wegklicken (_dismiss_cookie_banner)
3. "Log in" Button sichtbar? → OTP Flow
4.   Login-Button in Navbar klicken (a:has-text('Login'))
5.   "Continue with Email" klicken
6.   Email eingeben → ENTER drücken (nicht button[type='submit']!)
7.   Gmail IMAP liest 6-stelligen OTP Code (max 90s warten)
8.   OTP in Feld eingeben → ENTER drücken
9. Eingeloggt → Toggle ON prüfen → Generate!
```

### KRITISCH: button[type='submit'] ist der FALSCHE Button!
```
PROBLEM: button[type='submit'] findet den Higgsfield Generate-Button
         im Seitenhintergrund — NICHT den Continue-Button im Auth-Modal!
         → Timeout nach 5s

FIX: await email_input.press("Enter")
     Trifft immer die richtige Form, egal was im Hintergrund ist.
```

### Gmail App Password (einmalig einrichten)
1. → https://myaccount.google.com/apppasswords
2. App name: `Higgsfield Pipeline` → Create
3. 16-stelligen Code kopieren (ohne Leerzeichen)
4. `gh secret set GMAIL_APP_PASSWORD --repo shinobi1412ai/maxmia --body "<code>"`

---

## 6. Higgsfield Cookies exportieren

Cookies halten mehrere Wochen. Wenn Login-Probleme → neue Cookies:

### Methode: Chrome Console (einfachste)
1. Chrome öffnen, auf `higgsfield.ai` eingeloggt sein
2. F12 → Console → ausführen:
```javascript
copy(btoa(JSON.stringify(document.cookie.split(';').map(c => {
  const [name, ...rest] = c.trim().split('=');
  return { name: name.trim(), value: rest.join('=').trim(),
           domain: 'higgsfield.ai', path: '/' };
}).filter(c => c.name && c.value))));
// Inhalt der Zwischenablage als Secret speichern:
```
3. `gh secret set HIGGSFIELD_COOKIES --repo shinobi1412ai/maxmia`

### Methode: Script
```bash
# Chrome erst schließen (DB-Lock), dann:
python scripts/update_cookies_secret.py
```

---

## 7. Alle Bugs — Von Tag 0 bis heute

### BUG 1: UTF-8 BOM in GitHub Secrets ⚠️ HÄUFIGSTER BUG
**Fehler:** `UnicodeEncodeError` / `JSONDecodeError: Unexpected UTF-8 BOM`
**Ursache:** PowerShell schreibt `\xef\xbb\xbf` BOM in alle Secrets
**Betrifft:** YOUTUBE_TOKEN_JSON, YOUTUBE_CLIENT_SECRETS, HIGGSFIELD_COOKIES
**Fix:** `_strip_bom()` in `src/higgsfield_cloud.py`:
```python
def _strip_bom(raw: str) -> str:
    raw = raw.strip().lstrip('﻿').lstrip('\xef\xbb\xbf').strip()
    return raw.encode('ascii', errors='ignore').decode('ascii').strip()
```
**Regel:** Immer `gh secret set` via CLI nutzen — nie via PowerShell-Copy-Paste ins GitHub Web UI!

---

### BUG 2: `triple_click()` existiert nicht in Playwright
**Fehler:** `'Locator' object has no attribute 'triple_click'`
**Fix:** `await box.click(click_count=3)`

---

### BUG 3: `networkidle` Timeout bei Higgsfield
**Fehler:** `Page.goto: Timeout 60000ms exceeded`
**Ursache:** Higgsfield SPA macht immer aktive Requests → `networkidle` wird nie erreicht
**Fix:** `wait_until="domcontentloaded"` + `timeout=90_000` + `_goto_with_retry()` (3 Versuche)

---

### BUG 4: HTTP 403 beim Download ⚠️ KRITISCH
**Fehler:** `HTTP Error 403: Forbidden` beim Herunterladen von Bildern/Videos
**Ursache:** Higgsfield CDN braucht Session-Cookies. `urllib` hat keine.
**Fix:** Playwright `ctx.request.get(url)` — trägt automatisch Session-Cookies:
```python
async def _download_with_ctx(ctx, url, dest):
    response = await ctx.request.get(url)
    dest.write_bytes(await response.body())
```

---

### BUG 5: Zweiter BOM-Bug (YOUTUBE_CLIENT_SECRETS)
Erster Fix nur für `YOUTUBE_TOKEN_JSON`. Beide Secrets brauchen `decode_secret()`!

---

### BUG 6: MP3-Fallback nicht in Git
**Problem:** `music/*.mp3` war in `.gitignore` → GitHub Actions hat keine Musik
**Fix:** `.gitignore` Exception: `!music/*.mp3` + MP3s committen

---

### BUG 7: Video-Upload mit CDN-URL statt lokalem Bild
**Problem:** CDN-URL kann nicht als File-Input verwendet werden
**Fix:** `set_input_files(str(local_image_path))` — lokales Bild direkt uploaden

---

### BUG 8: Kein echter Roter Faden
**Problem:** Clips wurden zyklisch aus Lyrik-Zeilen gewählt — keine Story
**Fix:** 3-Akt-Struktur implementiert: Setup (8) → Liedtext (19) → Triumph (9)

---

### BUG 9: Workflow-Name mit Em-Dash
**Problem:** `"Max & Mia World — Daily Video Pipeline"` (—) ließ sich nicht via CLI triggern
**Fix:** Normaler Bindestrich: `"Max & Mia World - Daily Video Pipeline"`

---

### BUG 10: Toggle 5 Tage lang nie gefunden ⚠️ GRÖSSTER BUG
**Symptom:** Alle Runs fehlgeschlagen, 0 Bilder generiert
**Root Causes (in dieser Reihenfolge):**

1. **Cookie-Banner** überdeckte Toggle physisch
   → Fix: `_dismiss_cookie_banner()` VOR Toggle-Check aufrufen

2. **Cookies abgelaufen** → Seite zeigt "Log in" Button, aber URL bleibt `/ai/image`
   → Fehler: Pipeline hat nur URL geprüft, nicht Button-Existenz
   → Fix: `not_logged_in = page.locator("button:has-text('Log in'), ...")`

3. **`/login` URL gibt 404**
   → Fix: Login-Button im Navbar klicken, nicht URL direkt navigieren

4. **Higgsfield hat KEIN Passwort-Login** (nur Email OTP oder Google OAuth)
   → Pipeline versuchte Google OAuth → geblockt von Google

5. **Google OAuth geblockt** → Fallback auf Email OTP → kein Code-Reader → Loop
   → Fix: Gmail IMAP OTP Reader implementiert

---

### BUG 11: Clerk JWT läuft nach 60 Min ab
**Symptom:** Erste ~10 Bilder OK, dann OTP-Spam (viele Emails 04:08-04:10)
**Ursache:** Clerk JWT hat 60-Minuten-Expiry. Pipeline läuft 3-6 Stunden.
**Fix:** Gmail IMAP OTP Auto-Reader → Pipeline kann sich automatisch neu einloggen

---

### BUG 12: button[type='submit'] ist der FALSCHE Button (heute!)
**Symptom:** `Locator.click: Timeout 5000ms exceeded` auf `button[type='submit']`
**Ursache:** Selector findet den Higgsfield Generate-Button im Seitenhintergrund,
           nicht den Continue-Button im Clerk Auth-Modal
**Fix:** `await email_input.press("Enter")` — trifft immer die richtige Form

---

## 8. Pipeline-Architektur

```
GitHub Actions (ubuntu-latest, timeout: 360min)
│
├── Setup (~2 Min)
│   ├── Python 3.11 + pip install
│   ├── playwright install chromium
│   └── Xvfb :99 (virtuelles Display — headless=False braucht Display!)
│
└── scripts/pipeline_orchestrator.py
    ├── Thema aus state.json (rotiert täglich)
    ├── Storyboard: 36 Clips, 3-Akt-Struktur
    │
    ├── 36× _generate_image_async()
    │   ├── Browser + Cookies laden
    │   ├── Cookie-Banner wegklicken
    │   ├── Login prüfen → ggf. OTP Flow (Gmail IMAP)
    │   ├── Toggle ON prüfen (PFLICHT!)
    │   ├── Prompt eingeben → Enter
    │   ├── Auf neues Bild warten (max 5 Min)
    │   └── ctx.request.get() downloaden (kein 403!)
    │
    ├── Suno Musik oder Fallback MP3
    │
    ├── 36× _generate_video_async()
    │   └── (gleicher Flow, Kling 2.5 Turbo, 5s, 16:9)
    │
    └── ffmpeg → 3 Min MP4 → YouTube Upload
```

---

## 9. Wichtige Dateien

```
video-animation-kids/
├── src/higgsfield_cloud.py       ← KERNSTÜCK der Pipeline
│   ├── _strip_bom()              BOM entfernen (PowerShell-Fix)
│   ├── _load_cookies()           Cookies aus HIGGSFIELD_COOKIES Env
│   ├── _ensure_unlimited()       Toggle ON prüfen — NIEMALS überspringen!
│   ├── _dismiss_cookie_banner()  Cookie-Banner wegklicken
│   ├── _ensure_logged_in()       Login-Status prüfen (Button-Check, nicht URL!)
│   ├── _get_otp_from_gmail_sync() Gmail IMAP OTP lesen
│   ├── _login_with_email()        Email OTP Login (Enter statt submit-Button!)
│   ├── _goto_with_retry()         Navigation mit Retry + 5s SPA-Wait
│   ├── _new_browser_context()     Browser + Anti-Bot + Cookies
│   ├── _generate_image_async()   Bild generieren + ctx.request.get() download
│   └── _generate_video_async()   Video generieren + download
│
├── scripts/pipeline_orchestrator.py   Hauptorchestrator
├── scripts/restore_credentials.py     YouTube OAuth aus Secrets
├── scripts/update_cookies_secret.py   Higgsfield Cookies exportieren
├── .github/workflows/daily_pipeline.yml
├── music/                              Fallback MP3s (MÜSSEN in Git sein!)
├── state.json                          Themen-Index (auto-committed nach Run)
└── PIPELINE_GUIDE.md                  DIESE DATEI
```

---

## 10. Run starten und überwachen

```bash
# Run starten
gh workflow run daily_pipeline.yml --repo shinobi1412ai/maxmia

# Status
gh run list --repo shinobi1412ai/maxmia --limit 5

# Job-Steps ansehen (während Run)
gh api repos/shinobi1412ai/maxmia/actions/runs/<ID>/jobs \
  --jq '.jobs[0].steps[] | select(.status != "pending") | {name, status, conclusion}'

# Logs (erst nach Run-Ende verfügbar!)
gh run view <ID> --repo shinobi1412ai/maxmia --log | grep -E "(ERROR|Toggle|Login|OTP|✅|❌)"

# Run abbrechen
gh run cancel <ID> --repo shinobi1412ai/maxmia
```

---

## 11. Troubleshooting

| Symptom | Ursache | Fix |
|---------|---------|-----|
| OTP-Emails kommen, Login schlägt fehl | GMAIL_APP_PASSWORD fehlt oder falsch | Secret prüfen, neu setzen |
| Toggle nicht gefunden | Cookie-Banner / nicht eingeloggt | Screenshots in Artifacts ansehen |
| HTTP 403 beim Download | urllib statt ctx.request | `_download_with_ctx()` nutzen |
| JSONDecodeError BOM | Secret via PowerShell gesetzt | `_strip_bom()` + gh CLI nutzen |
| Timeout auf button[type='submit'] | Falscher Button (Generate, nicht Auth) | `inp.press("Enter")` |
| networkidle Timeout | Higgsfield SPA always active | `domcontentloaded` nutzen |
| Login Button nicht gefunden nach Login | URL prüfen statt Button | Button-Existenz prüfen |

---

## 12. Prompts & Beleuchtung

### Verbotene Beleuchtung
```
❌ "golden sunlight beams", "rays of sunlight through trees"
❌ "dramatic lighting", "god rays", "volumetric light"
✅ "bright and cheerful", "soft natural daylight", "clear blue sky"
```

### Environments — IMMER verschieden pro Clip!
Grüne Wiese → Bunter Garten → Bauernhof → Wald → Teich → Strand → Obstgarten...
Niemals denselben Hintergrund zweimal!

---

## 13. YouTube Upload — Pflicht

```python
privacy = "public"                 # NIEMALS "private"!
selfDeclaredMadeForKids = True     # IMMER!
# Titel + Beschreibung + Tags: IMMER Englisch, nie Deutsch!
```

---

## 14. Aktuelle Runs-Chronologie

| Run ID | Datum | Problem | Ergebnis |
|--------|-------|---------|----------|
| frühe Runs | vor Mai 2026 | BOM, networkidle, triple_click | ❌ |
| mehrere | Mai 2026 | 403, MP3, Story | ❌ → ✅ fixed |
| 25950996901 | 16.05 02:57 | Cookies abgelaufen → OTP Loop | ❌ cancelled |
| 25951372718 | 16.05 03:15 | button[type='submit'] Timeout | ❌ |
| 25960280515 | 16.05 11:02 | Enter-Fix + Gmail App PW | 🔄 läuft |

---

## 15. Checkliste — Von 0 alles neu einrichten

```bash
# 1. Secrets setzen
gh secret set HIGGSFIELD_EMAIL --repo shinobi1412ai/maxmia --body "makevision1412@gmail.com"
gh secret set GMAIL_APP_PASSWORD --repo shinobi1412ai/maxmia   # App PW eingeben
gh secret set SUNO_EMAIL --repo shinobi1412ai/maxmia --body "makevision1412@gmail.com"
gh secret set SUNO_PASSWORD --repo shinobi1412ai/maxmia
gh secret set ANTHROPIC_API_KEY --repo shinobi1412ai/maxmia

# 2. Higgsfield Cookies (Chrome auf higgsfield.ai offen!)
# Console: copy(btoa(JSON.stringify([...alle cookies...])))
gh secret set HIGGSFIELD_COOKIES --repo shinobi1412ai/maxmia

# 3. YouTube OAuth
python scripts/setup_youtube_oauth.py
gh secret set YOUTUBE_TOKEN_JSON --repo shinobi1412ai/maxmia
gh secret set YOUTUBE_CLIENT_SECRETS --repo shinobi1412ai/maxmia

# 4. state.json
echo '{"last_theme_index": -1}' > state.json
git add state.json && git commit -m "init: state" && git push

# 5. Ersten Run starten
gh workflow run daily_pipeline.yml --repo shinobi1412ai/maxmia
```

---

*Erstellt von Claude Sonnet 4.6 — 5 Tage Debugging, 12 Bugs gefunden und gefixt*
