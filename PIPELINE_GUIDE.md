# Max & Mia World — Vollständiger Pipeline Guide + HANDOFF
> **ZUERST LESEN! Vor jedem Chat, vor jedem Run.** Alle Learnings von Tag 0 bis heute.

Zuletzt aktualisiert: 2026-05-17 (nach `__client` HttpOnly-Fix)

---

## ⚡ HANDOFF — Neuer Chat startet hier

Du bist ein neuer Claude-Chat. Lies das hier **bevor** du irgendetwas tust:

### Was läuft gerade
- Vollautomatischer YouTube-Kanal "Max & Mia World" auf GitHub Actions
- Repo: `shinobi1412ai/maxmia` (GitHub User: `shinobi1412ai`)
- Täglicher Cron: 02:00 UTC → Bilder + Videos + Upload

### Die 3 absoluten Pflichtregeln
```
1. NIEMALS Higgsfield API/CLI/MCP für Generierung nutzen → IMMER Credits!
   Browser + Unlimited Toggle ON = 0 Credits (Nano Banana Pro Plan)

2. IMMER Max & Mia Charaktere in JEDEN Clip einbauen (beide!)
   Ohne Max & Mia = falsches Bild

3. IMMER 16:9 Aspect Ratio (Querformat = YouTube)
```

### Status nach letztem Fix (17.05.2026)
- ✅ `__client` HttpOnly Cookie als `HIGGSFIELD_COOKIES` Secret gesetzt
- ✅ `_ensure_logged_in()` hat jetzt CHECK 0: `window.Clerk.session.getToken()` 
- ✅ `_new_browser_context()` erkennt `__client` Cookie und loggt korrekt
- ✅ Kein OTP mehr nötig — Clerk refresht JWT automatisch via `__client`

### Erster Schritt bei Problemen
```bash
# GitHub Actions letzten Run ansehen
gh run list --repo shinobi1412ai/maxmia --limit 3
gh run view <ID> --repo shinobi1412ai/maxmia --log | grep -E "(ERROR|Toggle|Login|OTP|✅|❌|Clerk)"

# Cookies erneuern (wenn Login-Probleme)
# → Abschnitt 6 lesen!
```

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

## 2. Die Charaktere (IMMER in jedem Clip — BEIDE!)

### Mia (Mädchen)
- Braune Haare in **ZWEI Zöpfen mit ROTEN Schleifen**
- Grüne Augen, Sommersprossen
- Rosa Kleid mit gelben Sternen, rosa Leggings, rosa Mary Jane Schuhe

### Max (Junge)
- **Lockige** braune Haare, braune Augen, Sommersprossen
- Blaues Strickpulli, braune Latzhose mit **Dino-Aufnäher** auf Brusttasche
- Rote Turnschuhe mit weißen Streifen

### Basis-Prompt (IMMER als Prefix verwenden — in CHAR_PROMPT in Code)
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

API/CLI/MCP = IMMER Credits (10/Video, 2/Bild) → NIEMALS nutzen!
Toggle AUS = Credits! → Sofort abbrechen!
```

### Was "Unlimited Toggle" bedeutet
- Der Toggle existiert NUR im Browser (higgsfield.ai UI)
- API/CLI/MCP umgehen ihn immer → kosten immer Credits
- MCP-Tools wie `generate_image`, `generate_video` = VERBOTEN!
- Higgsfield CLI (`higgsfield generate`) = VERBOTEN!
- `_ensure_unlimited()` macht den Browser-Toggle-Check automatisch

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
| `HIGGSFIELD_COOKIES` | base64 JSON (MIT `__client` HttpOnly!) | Abschnitt 6 |
| `YOUTUBE_TOKEN_JSON` | base64 JSON | `py scripts/setup_youtube_oauth.py` |
| `YOUTUBE_CLIENT_SECRETS` | base64 JSON | Google Cloud Console |
| `SUNO_EMAIL` | makevision1412@gmail.com | Direkt |
| `SUNO_PASSWORD` | Suno Passwort | Direkt |
| `ANTHROPIC_API_KEY` | sk-ant-... | anthropic.com |

**NICHT mehr genutzt:** `HIGGSFIELD_PASSWORD` (Higgsfield hat kein Passwort-Login!)

### Secret via CLI setzen (PFLICHT — kein BOM-Problem!)
```bash
gh secret set GMAIL_APP_PASSWORD --repo shinobi1412ai/maxmia --body "xzrjyztrnmffkteq"
gh secret set HIGGSFIELD_EMAIL --repo shinobi1412ai/maxmia --body "makevision1412@gmail.com"
```

**NIEMALS** via PowerShell Copy-Paste ins GitHub Web UI! (BOM-Bug → JSONDecodeError)

---

## 5. Higgsfield Auth — Wie es wirklich funktioniert

### Hintergrund — Clerk Auth
Higgsfield nutzt **Clerk Auth** mit Email OTP — KEIN Passwort-Login!

**Die 3 wichtigen Cookies:**
| Cookie | Typ | Ablauf | Funktion |
|--------|-----|--------|---------|
| `__session` | HttpOnly JWT | ~60 Minuten | Aktive Session-Token |
| `__client` | HttpOnly JWT | ~2031 (5 Jahre!) | Refresh-Token — erneuert `__session` automatisch! |
| `__client_uat` | Normal | ~2031 | Zeitstempel des letzten Logins |

**Warum `__client` der Schlüssel ist:**
- Clerk JS (`window.Clerk`) nutzt `__client` um `__session` automatisch zu erneuern
- Mit `__client` im Cookie Store: kein OTP nötig, kein manueller Login!
- Ohne `__client`: `__session` läuft nach 60 Min ab → Login-Button → OTP → Rate-Limit

**Warum `document.cookie` NICHT funktioniert:**
```
document.cookie  →  nur nicht-HttpOnly Cookies (KEIN __client, KEIN __session!)
Playwright storage_state()  →  ALLE Cookies inkl. HttpOnly ✅
Chrome DevTools → Application → Cookies  →  ALLE Cookies inkl. HttpOnly ✅
```

### Login-Check (CHECK 0 — neu seit 17.05.2026)
```python
# In _ensure_logged_in() — ZUERST ausgeführt:
clerk_status = await page.evaluate("""
    async () => {
        if (!window.Clerk) return 'no_clerk';
        if (!window.Clerk.session) return 'no_session';
        const token = await window.Clerk.session.getToken();
        return token ? 'ok:' + token.substring(0,20) : 'no_token';
    }
""")
# Wenn 'ok:...' → eingeloggt — KEIN OTP nötig!
```

### Normaler Login-Flow (wenn `__client` fehlt oder abgelaufen)
```
1. Cookies laden → Higgsfield.ai öffnen
2. Cookie-Banner wegklicken (_dismiss_cookie_banner)
3. CHECK 0: window.Clerk.session.getToken() → eingeloggt? ✅ Fertig!
4. Falls nicht: Login-Button in Navbar klicken
5.   "Continue with Email" klicken
6.   Email eingeben → ENTER drücken (nicht button[type='submit']!)
7.   Gmail IMAP liest 6-stelligen OTP Code (max 90s warten)
8.   OTP in Feld eingeben → Clerk auto-submits
9. Eingeloggt → Toggle ON prüfen → Generate!
```

### Gmail App Password (einmalig einrichten — für OTP-Fallback)
1. → https://myaccount.google.com/apppasswords
2. App name: `Higgsfield Pipeline` → Create
3. 16-stelligen Code kopieren (ohne Leerzeichen)
4. `gh secret set GMAIL_APP_PASSWORD --repo shinobi1412ai/maxmia --body "<code>"`

---

## 6. Higgsfield Cookies exportieren (mit `__client` HttpOnly!)

> ⚠️ **WICHTIG:** `document.cookie` in der Browser-Konsole gibt `__client` NICHT zurück!
> Es muss Chrome DevTools Application Tab oder Playwright `storage_state()` benutzt werden!

### Methode 1: Chrome DevTools Application Tab (empfohlen — einfachste)

1. Chrome öffnen → `https://higgsfield.ai/ai/image` → einloggen
2. `F12` → Tab **Application** (oder Anwendung)
3. Linke Seite: **Cookies** → `https://higgsfield.ai`
4. Alle Cookies sind sichtbar inkl. HttpOnly (🔒 Schloss-Symbol)
5. Folgende Cookies notieren (Name + Value):
   - `__client` ← **DER WICHTIGSTE** (sehr langer JWT)
   - `__client_uat`
   - `__session` (kann fehlen wenn abgelaufen)
6. JSON erstellen:
```json
[
  {"name":"__client","value":"eyJhbGciOi...","domain":".higgsfield.ai","path":"/","secure":true,"httpOnly":true,"sameSite":"Lax","expires":1813524580},
  {"name":"__client_uat","value":"1234567890","domain":".higgsfield.ai","path":"/","secure":true,"httpOnly":false,"sameSite":"Strict","expires":1813524580}
]
```
7. Als base64 kodieren und als Secret setzen:
```bash
# In Python:
import json, base64
cookies = [{"name":"__client","value":"eyJ...","domain":".higgsfield.ai","path":"/","secure":True,"httpOnly":True,"sameSite":"Lax"}]
b64 = base64.b64encode(json.dumps(cookies).encode()).decode()
print(b64)

# Dann:
gh secret set HIGGSFIELD_COOKIES --repo shinobi1412ai/maxmia --body "<base64>"
```

### Methode 2: Playwright Script (export_session.py)
```bash
# Exports ALLE Cookies inkl. HttpOnly via Playwright storage_state()
py scripts/export_session.py
# → Öffnet Browser → einloggen → ENTER drücken
# → Exportiert alle Cookies inkl. __client als GitHub Secret
```

### Methode 3: Nur wenn __client schon bekannt (direkt setzen)
```python
import json, base64

cookies = [
    {
        "name": "__client",
        "value": "<WERT AUS DEVTOOLS>",
        "domain": ".higgsfield.ai",
        "path": "/",
        "secure": True,
        "httpOnly": True,
        "sameSite": "Lax",
        "expires": 1813524580  # ~2031
    }
]
b64 = base64.b64encode(json.dumps(cookies).encode()).decode()
print(b64)
```
```bash
gh secret set HIGGSFIELD_COOKIES --repo shinobi1412ai/maxmia --body "<b64>"
```

### FALSCHE Methode (funktioniert NICHT — kein __client!)
```javascript
// ❌ FUNKTIONIERT NICHT — document.cookie kann HttpOnly NICHT lesen!
copy(btoa(JSON.stringify(document.cookie.split(';').map(...))));
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

### BUG 13: `__client` HttpOnly Cookie fehlte in HIGGSFIELD_COOKIES ⚠️ ROOT CAUSE DER 5-TAGE-AUSFALLS!
**Symptom:** Pipeline läuft, Clerk-Session läuft nach 60 Min ab, OTP-Flood
**Ursache:**
- `document.cookie` in Browser-Console kann HttpOnly-Cookies NICHT lesen
- `__client` (Clerk Refresh-Token) ist HttpOnly → war NIE in HIGGSFIELD_COOKIES Secret!
- Ohne `__client` kann Clerk JS den `__session` JWT NICHT refreshen
- Nach 60 Min: `__session` abgelaufen → Higgsfield zeigt Login-Button → OTP nötig
- OTP Rate-Limiting nach 20+ Versuchen in einem Tag → Higgsfield sendet keine mehr

**Fix:**
1. `__client` Wert aus Chrome DevTools kopieren (Application → Cookies, nicht Console!)
2. Als JSON mit allen Cookie-Feldern (httpOnly: true, expires: ...) bauen
3. Als base64 codieren → `gh secret set HIGGSFIELD_COOKIES`
4. In `_new_browser_context()`: `has_client = any(c.get("name") == "__client" for c in cookies)`
5. In `_ensure_logged_in()`: CHECK 0 — `window.Clerk.session.getToken()` — direkte Clerk JS Prüfung

**Erkennung:**
```
Logmeldung: "⚠️ Kein __client Cookie in HIGGSFIELD_COOKIES — JWT kann ablaufen!"
→ Sofort Cookies erneuern via Abschnitt 6!
```

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
    │   ├── Browser + HIGGSFIELD_COOKIES laden (mit __client!)
    │   ├── Cookie-Banner wegklicken
    │   ├── CHECK 0: window.Clerk.session.getToken() → eingeloggt? ✅
    │   ├── Falls nicht: Login-Button → OTP Flow (Gmail IMAP)
    │   ├── _save_session() → storage_state() speichert alle Cookies
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
│   ├── _ensure_logged_in()       Login CHECK 0: Clerk JS, dann UI-Elemente
│   ├── _get_otp_from_gmail_sync() Gmail IMAP OTP lesen
│   ├── _login_with_email()        Email OTP Login (Enter statt submit-Button!)
│   ├── _goto_with_retry()         Navigation mit Retry + 5s SPA-Wait
│   ├── _save_session()           storage_state() speichern (inkl. HttpOnly!)
│   ├── _new_browser_context()     Browser + Anti-Bot + __client Cookie Detect
│   ├── _generate_image_async()   Bild generieren + ctx.request.get() download
│   └── _generate_video_async()   Video generieren + download
│
├── scripts/pipeline_orchestrator.py   Hauptorchestrator
├── scripts/restore_credentials.py     YouTube OAuth aus Secrets
├── scripts/export_session.py          Playwright storage_state Export (inkl. __client!)
├── scripts/update_cookies_secret.py   Chrome SQLite Cookie-Export (ohne HttpOnly!)
├── .github/workflows/daily_pipeline.yml
├── music/                              Fallback MP3s (MÜSSEN in Git sein!)
├── state.json                          Themen-Index (auto-committed nach Run)
└── PIPELINE_GUIDE.md                  DIESE DATEI
```

> ⚠️ `update_cookies_secret.py` kann `__client` NICHT exportieren (SQLite hat HttpOnly nicht)
> → Nutze `export_session.py` (Playwright) oder Chrome DevTools Application Tab!

---

## 10. Run starten und überwachen

```bash
# Workflow starten
gh workflow run daily_pipeline.yml --repo shinobi1412ai/maxmia

# Status ansehen
gh run list --repo shinobi1412ai/maxmia --limit 5

# Job-Steps ansehen (während Run läuft)
gh api repos/shinobi1412ai/maxmia/actions/runs/<RUN_ID>/jobs \
  --jq '.jobs[0].steps[] | select(.status != "pending") | {name, status, conclusion}'

# Logs (WÄHREND Run)
gh run view <RUN_ID> --repo shinobi1412ai/maxmia --log | grep -E "(ERROR|Toggle|Login|OTP|Clerk|✅|❌)"

# Run abbrechen
gh run cancel <RUN_ID> --repo shinobi1412ai/maxmia

# Aktuellen Run-Status prüfen
gh run list --repo shinobi1412ai/maxmia --limit 1 --json status,conclusion,databaseId
```

**Wichtig auf Windows:** Python-Befehle mit `py` starten, nicht `python`!
```bash
py scripts/export_session.py     # ✅ (py = Windows Python Launcher)
python scripts/...               # ❌ Nicht gefunden auf Windows
```

---

## 11. Troubleshooting

| Symptom | Ursache | Fix |
|---------|---------|-----|
| `⚠️ Kein __client Cookie` in Log | __client fehlt in HIGGSFIELD_COOKIES | Abschnitt 6 → DevTools Methode |
| OTP-Emails kommen, Login schlägt fehl | GMAIL_APP_PASSWORD fehlt oder falsch | Secret prüfen, neu setzen |
| Toggle nicht gefunden | Cookie-Banner / nicht eingeloggt | Screenshots in Artifacts ansehen |
| HTTP 403 beim Download | urllib statt ctx.request | `_download_with_ctx()` nutzen |
| JSONDecodeError BOM | Secret via PowerShell gesetzt | `_strip_bom()` + gh CLI nutzen |
| Timeout auf button[type='submit'] | Falscher Button (Generate, nicht Auth) | `inp.press("Enter")` |
| networkidle Timeout | Higgsfield SPA always active | `domcontentloaded` nutzen |
| Login Button nach Login noch da | URL prüfen statt Button | Button-Existenz prüfen |
| Credits verbraucht! | API/CLI/MCP benutzt | SOFORT stoppen. Nur Browser! |
| Clerk Check: `no_clerk` nach 25s | Seite nicht geladen / Bot-Block | Screenshot prüfen, Cookies erneuern |
| OTP Rate-Limit (keine Email mehr) | Zu viele OTP-Requests (20+ an 1 Tag) | 24h warten, dann __client Cookie setzen |

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
| 25960280515 | 16.05 11:02 | Enter-Fix + Gmail App PW | ❌ (kein __client) |
| nächster Run | 17.05+ | __client Cookie gesetzt + Clerk JS Check | 🔄 pending |

---

## 15. Checkliste — Von 0 alles neu einrichten

```bash
# 1. Basis-Secrets setzen
gh secret set HIGGSFIELD_EMAIL --repo shinobi1412ai/maxmia --body "makevision1412@gmail.com"
gh secret set GMAIL_APP_PASSWORD --repo shinobi1412ai/maxmia   # App PW eingeben
gh secret set SUNO_EMAIL --repo shinobi1412ai/maxmia --body "makevision1412@gmail.com"
gh secret set SUNO_PASSWORD --repo shinobi1412ai/maxmia
gh secret set ANTHROPIC_API_KEY --repo shinobi1412ai/maxmia

# 2. Higgsfield Cookies MIT __client (Chrome DevTools Application Tab!)
# Chrome → higgsfield.ai → F12 → Application → Cookies → __client Value kopieren
# → JSON bauen → base64 kodieren (Python):
#   import json,base64; b64=base64.b64encode(json.dumps([{"name":"__client","value":"<VALUE>","domain":".higgsfield.ai","path":"/","secure":True,"httpOnly":True,"sameSite":"Lax"}]).encode()).decode(); print(b64)
gh secret set HIGGSFIELD_COOKIES --repo shinobi1412ai/maxmia --body "<b64>"

# ODER: Playwright Script (exportiert alle Cookies automatisch)
py scripts/export_session.py

# 3. YouTube OAuth
py scripts/setup_youtube_oauth.py
gh secret set YOUTUBE_TOKEN_JSON --repo shinobi1412ai/maxmia
gh secret set YOUTUBE_CLIENT_SECRETS --repo shinobi1412ai/maxmia

# 4. state.json
echo '{"last_theme_index": -1}' > state.json
git add state.json && git commit -m "init: state" && git push

# 5. Ersten Run starten
gh workflow run daily_pipeline.yml --repo shinobi1412ai/maxmia
```

---

## 16. Was NIEMALS tun

```
❌ python statt py auf Windows (Python Launcher heißt py!)
❌ Higgsfield CLI/MCP/API für Generierung (IMMER Credits!)
❌ document.cookie für Cookie-Export (kein __client!)
❌ PowerShell Copy-Paste in GitHub Web UI (BOM-Bug!)
❌ Bilder/Videos ohne Max & Mia (beide Charaktere IMMER!)
❌ Aspect Ratio 1:1 statt 16:9 (YouTube = Querformat!)
❌ Toggle OFF Generierung (Credits!)
❌ button[type='submit'] für Auth-Form (ist der Generate-Button!)
```

---

*Erstellt von Claude Sonnet 4.6 — 5 Tage Debugging, 13 Bugs gefunden und gefixt*
*Letzter Fix: 17.05.2026 — `__client` HttpOnly Cookie + Clerk JS Check*
