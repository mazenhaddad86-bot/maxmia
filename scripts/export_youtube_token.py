"""
EINMALIG LOKAL AUSFÜHREN — exportiert YouTube OAuth Token für GitHub Actions.
Das Token wird als Base64 JSON kodiert → als GitHub Secret YOUTUBE_TOKEN_JSON eintragen.

Ausführen:
    python scripts/export_youtube_token.py
"""
import base64
import json
import pickle
from pathlib import Path

TOKEN_PICKLE = Path(__file__).parent.parent / "youtube" / "token.pickle"
CLIENT_SECRETS = Path(__file__).parent.parent / "youtube" / "client_secrets.json"


def main():
    print("=" * 60)
    print("YouTube Token Export für GitHub Actions")
    print("=" * 60)

    if not TOKEN_PICKLE.exists():
        print(f"\n❌ {TOKEN_PICKLE} nicht gefunden!")
        print("Führe zuerst einmal manuell aus:")
        print("  python youtube/upload.py")
        print("Damit wird der OAuth-Flow gestartet und token.pickle erstellt.")
        return

    with open(TOKEN_PICKLE, "rb") as f:
        creds = pickle.load(f)

    # Token als JSON serialisieren
    token_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes) if creds.scopes else [],
    }

    token_json = json.dumps(token_data, indent=2)
    token_b64 = base64.b64encode(token_json.encode()).decode()

    print(f"\n✅ Token exportiert!")
    print("\n" + "=" * 60)
    print("GITHUB SECRET: YOUTUBE_TOKEN_JSON")
    print("Wert:")
    print("=" * 60)
    print(token_b64)
    print("=" * 60)

    # Client Secrets auch exportieren
    if CLIENT_SECRETS.exists():
        cs_data = CLIENT_SECRETS.read_text()
        cs_b64 = base64.b64encode(cs_data.encode()).decode()
        print("\n" + "=" * 60)
        print("GITHUB SECRET: YOUTUBE_CLIENT_SECRETS")
        print("Wert:")
        print("=" * 60)
        print(cs_b64)
        print("=" * 60)

    print("\nSo eintragen:")
    print("1. GitHub Repo → Settings → Secrets and variables → Actions")
    print("2. Für jeden Secret: 'New repository secret'")
    print("   - YOUTUBE_TOKEN_JSON → ersten Base64-String")
    print("   - YOUTUBE_CLIENT_SECRETS → zweiten Base64-String")


if __name__ == "__main__":
    main()
