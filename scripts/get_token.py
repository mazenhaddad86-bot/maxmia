"""Extract Clerk JWT from Chrome Canary - shared read of locked cookie DB."""
import sqlite3
import json
import base64
import os
import sys
import tempfile
import ctypes
import ctypes.wintypes as wintypes

CANARY_COOKIES = r"C:\Users\myshi\AppData\Local\Google\Chrome SxS\User Data\Default\Network\Cookies"
CANARY_LOCAL_STATE = r"C:\Users\myshi\AppData\Local\Google\Chrome SxS\User Data\Local State"

def copy_locked_file(src, dst):
    """Copy a file locked by another process using Win32 shared read."""
    import win32file, win32con, pywintypes
    GENERIC_READ = 0x80000000
    FILE_SHARE_READ = 0x1
    FILE_SHARE_WRITE = 0x2
    FILE_SHARE_DELETE = 0x4
    OPEN_EXISTING = 3

    handle = win32file.CreateFile(
        src,
        GENERIC_READ,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        None,
        OPEN_EXISTING,
        0,
        None
    )
    try:
        size = win32file.GetFileSize(handle)
        _, data = win32file.ReadFile(handle, size)
    finally:
        handle.Close()

    with open(dst, "wb") as f:
        f.write(data)

def get_encryption_key():
    with open(CANARY_LOCAL_STATE, "r", encoding="utf-8") as f:
        local_state = json.load(f)
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    encrypted_key = encrypted_key[5:]  # Strip "DPAPI" prefix
    import win32crypt
    key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    return key

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
    try:
        import win32crypt
        return win32crypt.CryptUnprotectData(bytes(encrypted_value), None, None, None, 0)[1].decode("utf-8", errors="replace")
    except:
        return None

def get_higgsfield_cookies():
    tmp = tempfile.mktemp(suffix=".db")
    try:
        copy_locked_file(CANARY_COOKIES, tmp)
    except Exception as e:
        print(f"Win32 copy failed: {e}, trying shutil...")
        import shutil
        shutil.copy2(CANARY_COOKIES, tmp)

    key = get_encryption_key()

    conn = sqlite3.connect(tmp)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, encrypted_value, host_key
        FROM cookies
        WHERE host_key LIKE '%higgsfield%' OR host_key LIKE '%clerk%'
        ORDER BY host_key, name
    """)
    rows = cursor.fetchall()
    conn.close()
    os.unlink(tmp)

    result = {}
    for row in rows:
        value = decrypt_value(bytes(row["encrypted_value"]), key)
        if value:
            result[row["name"]] = value
            print(f"  {row['host_key']} | {row['name']} = {value[:80]}")
    return result

if __name__ == "__main__":
    print("=== Higgsfield/Clerk cookies from Chrome Canary ===\n")
    try:
        cookies = get_higgsfield_cookies()
        print(f"\nTotal: {len(cookies)} cookies")
        with open("scripts/higgsfield_cookies.json", "w") as f:
            json.dump(cookies, f, indent=2)
        print("Saved → scripts/higgsfield_cookies.json")
    except Exception as e:
        import traceback; traceback.print_exc()
