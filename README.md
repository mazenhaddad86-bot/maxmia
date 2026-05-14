# Video Automation Pipeline

Komplett-Pipeline: **Higgsfield (Bild + Video) → Suno (Audio) → ffmpeg (Compose) → YouTube/TikTok/IG/FB**.

Einmal alle Keys eintragen, dann läuft es per Cron / Windows-Aufgabenplanung automatisch.

---

## TL;DR Setup-Reihenfolge

```bash
# 1. Python-Venv
python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate       # Mac/Linux
pip install -r requirements.txt

# 2. ffmpeg installieren
winget install Gyan.FFmpeg        # Windows
# brew install ffmpeg             # Mac
# sudo apt install ffmpeg         # Linux

# 3. Keys eintragen
copy .env.example .env            # Windows
# cp .env.example .env            # Mac/Linux
# → .env editieren, alle Keys eintragen

# 4. Themes anpassen
notepad config/themes.yaml        # eigene Topics rein

# 5. YouTube einmal autorisieren
python scripts/setup_youtube_oauth.py

# 6. Test-Lauf (kein Upload)
python -m src.main --dry-run

# 7. Echter Lauf
python -m src.main

# 8. Scheduler einrichten (siehe unten)
```

---

## API-Setup pro Plattform

### Higgsfield (Bilder + Videos)
- Account auf https://higgsfield.ai → **API-Key** in den Settings
- In `.env`: `HIGGSFIELD_API_KEY=hf_…`

### Suno (Audio)
**Wichtig:** Suno hat keine offizielle API. Wir nutzen Drittanbieter.
- Empfohlen: https://sunoapi.org (pay-per-use, ca. $0.014 pro Track)
- Account anlegen → Key kopieren → in `.env`: `SUNO_API_KEY=…`
- Risiko: Drittanbieter könnten ihren Zugang verlieren. Plan B = anderer Provider (APIPASS, MusicAPI.ai).

### YouTube Shorts
1. https://console.cloud.google.com → neues Projekt
2. **YouTube Data API v3** aktivieren
3. OAuth-Zustimmungsbildschirm: Typ "Extern", deine Mail als Test-User
4. **Anmeldedaten → OAuth-Client-ID → Desktop**
5. JSON-Datei runterladen, ablegen als `scripts/client_secrets.json`
6. Einmal: `python scripts/setup_youtube_oauth.py` (öffnet Browser)
7. Token wird in `scripts/youtube_token.json` gespeichert

### TikTok
1. https://developers.tiktok.com → App erstellen
2. Produkt aktivieren: **Login Kit** + **Content Posting API**
3. Scopes: `user.info.basic`, `video.publish`, `video.upload`
4. Redirect-URI: `http://localhost:8080/callback`
5. OAuth-Flow durchlaufen → Access-Token + Refresh-Token in `.env`
6. **Audit beantragen** — bis zur Freigabe sind Posts nur PRIVAT (`SELF_ONLY`)
7. Limit: ~15 Posts pro Account / Tag
8. Token läuft ab → Refresh-Logik nachrüsten (TODO im Code)

### Instagram (Reels)
**Voraussetzung:**
- Facebook **Page** (kein persönliches Profil)
- Instagram-**Business-Account** mit dieser Page verbunden

**Setup:**
1. https://developers.facebook.com → App erstellen → Typ "Business"
2. **Instagram Graph API** + **Pages API** als Produkte hinzufügen
3. Permissions: `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`
4. App-Review beantragen (Live-Mode für `instagram_content_publish`)
5. Page-Access-Token + IG-Business-User-ID holen
6. **WICHTIG**: IG erwartet eine **öffentlich erreichbare Video-URL** beim Upload.
   Optionen:
   - Eigener S3 / Cloudflare R2 Bucket (empfohlen) → setze `PUBLIC_VIDEO_URL` in .env
   - Lokal testen: ngrok-Tunnel auf localhost
7. In `.env`: `INSTAGRAM_USER_ID`, `INSTAGRAM_ACCESS_TOKEN`

### Facebook (Page Reels)
- Gleiche App wie für Instagram
- Permissions: `pages_manage_posts`, `pages_read_engagement`, `pages_manage_engagement`
- **Page-Access-Token** (nicht User-Token) holen — er läuft sonst alle 60 Tage ab
  → Long-Lived Page-Token besorgen: https://developers.facebook.com/tools/explorer
- In `.env`: `FACEBOOK_PAGE_ID`, `FACEBOOK_PAGE_ACCESS_TOKEN`

---

## Scheduler (automatischer Lauf)

### Windows (Aufgabenplanung)
1. Aufgabenplanung öffnen → "Aufgabe erstellen"
2. Trigger: täglich, 08:00 Uhr (z.B.)
3. Aktion: Programm starten → `scripts\run_pipeline.bat`
4. Zweite Aufgabe für 18:30 anlegen

### Mac/Linux (cron)
```cron
0 8 * * *   /pfad/zu/video-automation/scripts/run_pipeline.sh
30 18 * * * /pfad/zu/video-automation/scripts/run_pipeline.sh
```

---

## Was passiert in einer Iteration?

1. Theme aus `config/themes.yaml` wählen (round-robin, gespeichert in `state.json`)
2. **Higgsfield Soul** → Bild im 9:16-Format
3. **Higgsfield DOP** → Image-to-Video (5/10s)
4. **Suno** → 30s Musik passend zum Theme
5. **ffmpeg** → Video + Audio mergen, optional Hook-Text als Overlay einbrennen
6. Upload zu allen aktivierten Plattformen — Failures pro Plattform werden geloggt aber stoppen die Pipeline nicht
7. Logs landen in `pipeline.log`, Assets in `output/<timestamp>_<theme>/`

---

## Bekannte Limits / Risiken

| Plattform | Risiko |
|---|---|
| Suno | Inoffizielle API → Provider könnte Zugang verlieren |
| TikTok | App-Audit nötig sonst nur Privat-Posts. Token läuft ab (Refresh-Flow im Code als TODO) |
| Instagram | Erfordert Business-Account + öffentliche Video-URL. App-Review für Live-Posts |
| Facebook | Long-Lived Page-Token alle 60 Tage erneuern |
| YouTube | Quota: 10.000 Units / Tag (1 Upload ≈ 1.600 Units → max ~6 Uploads/Tag) |
| Higgsfield | Generierungs-Credits — bei leerem Konto schlägt der Lauf fehl |

---

## Troubleshooting

**"ffmpeg nicht gefunden"** → siehe Schritt 2 oben
**"YouTube-Token fehlt"** → `python scripts/setup_youtube_oauth.py`
**"Suno: keine task_id"** → API-Schema des Providers hat sich geändert, in `src/suno_client.py` anpassen
**"Higgsfield 401"** → Key falsch oder abgelaufen
**Logs** → `pipeline.log` im Projekt-Root
