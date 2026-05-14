# YouTube Upload Setup — Einmalige Einrichtung

## Schritt 1: Google Cloud Console (5 Minuten)

1. Gehe zu: https://console.cloud.google.com/
2. Klick **"Neues Projekt"** → Name: `MaxMiaWorld`
3. Linkes Menü → **"APIs & Dienste"** → **"Bibliothek"**
4. Suche: `YouTube Data API v3` → **Aktivieren**
5. Linkes Menü → **"APIs & Dienste"** → **"Anmeldedaten"**
6. Klick **"Anmeldedaten erstellen"** → **"OAuth-Client-ID"**
7. Typ: **"Desktop-Anwendung"** → Name: `YouTube Upload`
8. Klick **"Erstellen"**
9. Klick **"JSON herunterladen"**
10. Datei umbenennen zu: `client_secrets.json`
11. Datei hierher kopieren: `C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\youtube\`

## Schritt 2: OAuth Consent Screen

1. Linkes Menü → **"OAuth-Zustimmungsbildschirm"**
2. User Type: **"Extern"** → Erstellen
3. App-Name: `MaxMiaWorld Upload`
4. Deine E-Mail eintragen
5. Speichern

## Schritt 3: Test-Nutzer hinzufügen

1. Im OAuth Consent Screen → **"Testnutzer"**
2. Deine Google-Account-E-Mail hinzufügen
3. Speichern

## Schritt 4: Upload ausführen

```powershell
C:\Users\myshi\AppData\Local\Python\bin\python.exe upload.py
```

- Browser öffnet sich automatisch
- Mit Google Account einloggen
- Zugriff erlauben
- **Fertig!** Token wird gespeichert — nächstes Mal vollautomatisch

## Nach dem ersten Login

Jedes weitere Mal läuft der Upload **ohne Browser** — vollautomatisch!

```powershell
# Video hochladen
C:\Users\myshi\AppData\Local\Python\bin\python.exe upload.py
```

## Video von privat auf öffentlich schalten

Nach dem Upload ist das Video **privat** (zum Prüfen).
Wenn alles gut ist → YouTube Studio → Video → Sichtbarkeit → Öffentlich
