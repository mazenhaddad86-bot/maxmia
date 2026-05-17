"""
Extrahiert Higgsfield-Cookies aus Chrome (entschlüsselt DPAPI/AES)
und updated direkt das GitHub Secret HIGGSFIELD_COOKIES.

Aufruf: python scripts/update_cookies_secret.py
Voraussetzung: Chrome geschlossen ODER Script kopiert DB zuerst
"""
import os, sys, json, base64, sqlite3, shutil, subprocess
from pathlib import Path

# ── Chrome Pfade (normale Installation + Canary) ─────────────────────────────
CHROME_PATHS = [
    Path(os.environ.get("LOCALAPPDATA", "")) / "Google/Chrome/User Data",
    Path(os.environ.get("LOCALAPPDATA", "")) / "Google/Chrome SxS/User Data",
    Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft/Edge/User Data",
]

GITHUB_REPO = "shinobi1412ai/maxmia"
SECRET_NAME = "HIGGSFIELD_COOKIES"


def get_chrome_key(user_data_dir: Path) -> bytes | None:
    """Liest + entschlüsselt den AES-Schlüssel aus Chrome's Local State."""
    try:
        import win32crypt
        state_file = user_data_dir / "Local State"
        if not state_file.exists():
            return None
        state = json.loads(state_file.read_text(encoding="utf-8"))
        encrypted_key = base64.b64decode(state["os_crypt"]["encrypted_key"])
        # Entferne "DPAPI" Prefix (erste 5 Bytes)
        encrypted_key = encrypted_key[5:]
        key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        return key
    except ImportError:
        print("⚠️  win32crypt nicht verfügbar — versuche unverschlüsselt...")
        return None
    except Exception as e:
        print(f"  Key-Extraktion fehlgeschlagen: {e}")
        return None


def decrypt_cookie_value(encrypted_value: bytes, key: bytes | None) -> str:
    """Entschlüsselt einen Chrome-Cookie-Wert."""
    if not encrypted_value:
        return ""

    # Neue Chrome-Verschlüsselung: v10/v20 prefix + AES-256-GCM
    if encrypted_value[:3] in (b"v10", b"v20"):
        if key is None:
            return ""  # Kann ohne Key nicht entschlüsseln
        try:
            from Crypto.Cipher import AES
            nonce = encrypted_value[3:15]
            ciphertext = encrypted_value[15:-16]
            tag = encrypted_value[-16:]
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            return cipher.decrypt_and_verify(ciphertext, tag).decode("utf-8", errors="replace")
        except ImportError:
            # pycryptodome nicht installiert
            try:
                from cryptography.hazmat.primitives.ciphers.aead import AESGCM
                aesgcm = AESGCM(key)
                nonce = encrypted_value[3:15]
                return aesgcm.decrypt(nonce, encrypted_value[15:], None).decode("utf-8", errors="replace")
            except Exception:
                return ""
        except Exception:
            return ""

    # Alte DPAPI-Verschlüsselung
    try:
        import win32crypt
        return win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode("utf-8", errors="replace")
    except Exception:
        return ""


def extract_higgsfield_cookies(user_data_dir: Path) -> list[dict]:
    """Extrahiert alle Higgsfield-Cookies aus Chrome."""
    cookies_db = user_data_dir / "Default/Network/Cookies"
    if not cookies_db.exists():
        cookies_db = user_data_dir / "Default/Cookies"
    if not cookies_db.exists():
        return []

    # Chrome sperrt die DB — temporäre Kopie
    tmp = Path(os.environ.get("TEMP", "/tmp")) / "hf_cookies_tmp.db"
    try:
        shutil.copy2(cookies_db, tmp)
    except PermissionError:
        print(f"  ⚠️  Chrome läuft noch — DB gesperrt: {cookies_db}")
        print("  Bitte Chrome kurz schließen und erneut ausführen.")
        return []

    key = get_chrome_key(user_data_dir)

    conn = sqlite3.connect(str(tmp))
    cur = conn.cursor()

    cookies = []
    try:
        cur.execute("""
            SELECT host_key, name, value, encrypted_value, path, expires_utc, is_secure
            FROM cookies
            WHERE host_key LIKE '%higgsfield%'
        """)
        for host_key, name, value, encrypted_value, path, expires, is_secure in cur.fetchall():
            # Versuche unverschlüsselten Wert zuerst
            final_value = value
            if not final_value and encrypted_value:
                final_value = decrypt_cookie_value(encrypted_value, key)

            if final_value:
                cookies.append({
                    "name": name,
                    "value": final_value,
                    "domain": host_key.lstrip("."),
                    "path": path or "/",
                    "secure": bool(is_secure),
                })
                print(f"  ✅ {name}: {final_value[:30]}...")
            else:
                print(f"  ⚠️  {name}: konnte nicht entschlüsselt werden")
    except Exception as e:
        print(f"  DB-Fehler: {e}")
    finally:
        conn.close()
        tmp.unlink(missing_ok=True)

    return cookies


def update_github_secret(cookies: list[dict]) -> bool:
    """Speichert Cookies als Base64 in GitHub Secret via gh CLI."""
    if not cookies:
        print("❌ Keine Cookies zum Speichern")
        return False

    b64 = base64.b64encode(json.dumps(cookies).encode()).decode()
    print(f"\n📦 {len(cookies)} Cookies → {len(b64)} Zeichen Base64")

    # gh secret set HIGGSFIELD_COOKIES --repo shinobi1412ai/maxmia
    result = subprocess.run(
        ["gh", "secret", "set", SECRET_NAME, "--repo", GITHUB_REPO, "--body", b64],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        print(f"✅ GitHub Secret '{SECRET_NAME}' erfolgreich aktualisiert!")
        return True
    else:
        print(f"❌ gh secret set fehlgeschlagen: {result.stderr}")
        # Fallback: Base64 anzeigen für manuelle Eingabe
        print(f"\n📋 MANUELL in GitHub eintragen ({SECRET_NAME}):")
        print(b64)
        return False


def main():
    print("🔍 Suche Higgsfield-Cookies in Chrome...\n")

    all_cookies = []
    for chrome_dir in CHROME_PATHS:
        if chrome_dir.exists():
            print(f"📂 Chrome: {chrome_dir}")
            cookies = extract_higgsfield_cookies(chrome_dir)
            if cookies:
                all_cookies = cookies
                print(f"  → {len(cookies)} Higgsfield-Cookies gefunden!\n")
                break
            else:
                print(f"  → Keine Higgsfield-Cookies\n")

    if not all_cookies:
        print("❌ Keine Higgsfield-Cookies gefunden!")
        print("\n💡 Stell sicher dass:")
        print("  1. Du auf higgsfield.ai in Chrome eingeloggt bist")
        print("  2. Chrome geschlossen ist (damit die DB nicht gesperrt ist)")
        print("  3. Dann dieses Script erneut ausführen")
        sys.exit(1)

    print(f"🍪 Gefunden: {len(all_cookies)} Higgsfield-Cookies")
    for c in all_cookies:
        print(f"  - {c['name']}: {c['value'][:20]}...")

    print(f"\n🚀 Update GitHub Secret '{SECRET_NAME}' in {GITHUB_REPO}...")
    update_github_secret(all_cookies)


if __name__ == "__main__":
    main()
