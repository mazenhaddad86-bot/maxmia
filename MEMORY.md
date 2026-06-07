# MEMORY — Lebendes Projekt-Gedächtnis

## ⚠️ MEMORY-PROTOKOLL (PFLICHT)
- ZUERST lesen: Diese Datei ist dein Gedächtnis. Lies sie bei JEDEM Start.
- ZULETZT schreiben: Trage neue Erkenntnisse, Fehler & Lösungen hier ein bevor du fertig meldest.
- So vergisst du NIE etwas zwischen Sessions.

---

# Max & Mia World — Pipeline Memory

## Projekt-Grundlagen
- **Repo:** https://github.com/mazenhaddad86-bot/maxmia (user: mazenhaddad86-bot, Token: ghp_REDACTED_SEE_VPS_MEMORY)
- **ALT (nicht mehr):** https://github.com/shinobi1412ai/maxmia
- **Zweck:** Vollautomatischer YouTube-Kanal für Kids (Nursery Rhymes, 3D Pixar-Style)
- **Läuft auf:** GitHub Actions (Ubuntu) — PC kann AUS sein
- **Zeitplan:** Täglich 03:00 Berlin (02:00 UTC) — `cron: '0 2 * * *'`
- **YouTube-Kanal:** Max & Mia World — public, Made for Kids, English

## Charaktere (IMMER beide sichtbar)
- **Mia:** brown pigtail hair, red ribbons, green eyes, freckles, pink dress with yellow stars, pink leggings, pink mary jane shoes
- **Max:** curly brown hair, brown eyes, freckles, blue knit sweater, brown dungarees with dinosaur patch, red sneakers with white stripes
- **Style:** 3D Pixar animation style, bright and cheerful

## Higgsfield — KRITISCHE REGELN
- **Nano Banana Pro + Toggle ON = 0 Credits** (Bilder UND Videos kostenlos)
- **Toggle OFF = Credits werden verbraucht** — DAS NIEMALS ZULASSEN
- **Browser = GRATIS**, API = IMMER Credits
- `_ensure_unlimited()` prüft Toggle VOR JEDER Generierung
- Cookies laufen ab (alle paar Wochen) → neu exportieren

## Suno — Account
- Email: makevision1412@gmail.com
- 2490 Credits Stand Mai 2026
- Login via Clerk (Email-first Flow, dann Password)
- Fallback: lokale MP3s in `/music/` Ordner

## GitHub Secrets (alle gesetzt in mazenhaddad86-bot/maxmia — 27.05.2026)
- `HIGGSFIELD_COOKIES` — base64 JSON, aus Chrome DevTools
- `YOUTUBE_TOKEN_JSON` — base64 JSON, OAuth token
- `YOUTUBE_CLIENT_SECRETS` — base64 JSON, client secrets
- `SUNO_EMAIL` — makevision1412@gmail.com
- `SUNO_PASSWORD` — Mh261296200
- `ANTHROPIC_API_KEY` — (optional, für zukünftige Claude-Storyboard-Generierung)

## Roter Faden — 3-Akt-Struktur (36 Clips)
- **Akt 1 (Clips 1-8):** Setup — Max & Mia wachen auf, starten Abenteuer
- **Akt 2 (Clips 9-27):** Hauptabenteuer — Liedtext Zeile für Zeile, verschiedene Umgebungen
- **Akt 3 (Clips 28-36):** Triumph — Feier, Lernerfolg, Daumen hoch, Happy End
