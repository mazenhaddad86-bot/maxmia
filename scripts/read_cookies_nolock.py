"""Try to read Chrome cookies via SQLite nolock mode (no admin needed)."""
import sqlite3
import json
import base64
from pathlib import Path

CANARY_COOKIES = r"C:\Users\myshi\AppData\Local\Google\Chrome SxS\User Data\Default\Network\Cookies"
CANARY_LOCAL_STATE = r"C:\Users\myshi\AppData\Local\Google\Chrome SxS\User Data\Local State"

def get_encryption_key():
    with open(CANARY_LOCAL_STATE, "r", encoding="utf-8") as f:
        local_state = json.load(f)
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    encrypted_key = encrypted_key[5:]  # Strip "DPAPI" prefix
    import win32crypt
    return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

def decrypt_value(encrypted_value, key):
    try:
        from Crypto.Cipher import AES
        ev = bytes(encrypted_value)
        if ev[:3] in (b"v10", b"v11", b"v12", b"v20"):
            nonce = ev[3:15]
            ciphertext = ev[15:]
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            return cipher.decrypt(ciphertext)[:-16].decode("utf-8", errors="replace")
    except Exception:
        pass
    return None

def main():
    print("Trying SQLite immutable+nolock mode...")
    try:
        conn = sqlite3.connect(
            f"file:{CANARY_COOKIES}?mode=ro&immutable=1&nolock=1",
            uri=True
        )
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name, encrypted_value, host_key FROM cookies "
            "WHERE host_key LIKE '%higgsfield%' OR host_key LIKE '%clerk%'"
        )
        rows = cursor.fetchall()
        conn.close()
        print(f"Found {len(rows)} cookies!")

        key = get_encryption_key()
        cookies = []
        for r in rows:
            val = decrypt_value(bytes(r["encrypted_value"]), key)
            print(f"  {r['host_key']} | {r['name']} = {str(val)[:60] if val else 'ENCRYPTED'}")
            if val:
                cookies.append({
                    "name": r["name"],
                    "value": val,
                    "domain": r["host_key"],
                    "path": "/",
                    "httpOnly": True,
                    "secure": True,
                    "sameSite": "Lax",
                })

        if cookies:
            cookies_json = json.dumps(cookies)
            cookies_b64 = base64.b64encode(cookies_json.encode()).decode()
            with open("scripts/higgsfield_cookies.json", "w") as f:
                json.dump(cookies, f, indent=2)
            with open("scripts/_cookies_b64.txt", "w") as f:
                f.write(cookies_b64)
            print(f"\nSaved {len(cookies)} cookies to scripts/higgsfield_cookies.json")
            print(f"Base64 saved to scripts/_cookies_b64.txt")
        return cookies
    except Exception as e:
        print(f"Failed: {e}")
        return []

if __name__ == "__main__":
    main()
