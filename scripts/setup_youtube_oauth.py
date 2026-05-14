"""Einmalig ausführen, um YouTube OAuth-Token zu erzeugen.

Vorbereitung:
1. https://console.cloud.google.com → Projekt anlegen
2. APIs & Services → 'YouTube Data API v3' aktivieren
3. OAuth-Zustimmungsbildschirm konfigurieren (Test-User: deine Mail)
4. Anmeldedaten → OAuth-Client-ID → 'Desktop'
5. JSON runterladen → als 'scripts/client_secrets.json' ablegen
6. Dieses Script starten:  python scripts/setup_youtube_oauth.py
   → Browser öffnet sich, Login, Token wird unter scripts/youtube_token.json gespeichert.
"""
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
HERE = Path(__file__).resolve().parent
CLIENT = HERE / "client_secrets.json"
TOKEN = HERE / "youtube_token.json"

def main() -> None:
    if not CLIENT.exists():
        raise SystemExit(
            f"Fehlt: {CLIENT}\n"
            "Lade 'OAuth Client ID' (Desktop) von der Google Cloud Console und "
            "speichere die JSON-Datei dort ab."
        )
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT), SCOPES)
    creds = flow.run_local_server(port=0)
    TOKEN.write_text(creds.to_json(), encoding="utf-8")
    print(f"Token gespeichert: {TOKEN}")

if __name__ == "__main__":
    main()
