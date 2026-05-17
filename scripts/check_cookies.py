import sqlite3, json, base64, shutil
from pathlib import Path

db = Path(r"C:\Users\myshi\AppData\Local\Google\Chrome SxS\User Data\Default\Network\Cookies")
tmp = Path(r"C:\Users\myshi\AppData\Local\Temp\hf_cookies_tmp.db")
shutil.copy2(db, tmp)

conn = sqlite3.connect(str(tmp))
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cur.fetchall()]
print("Tables:", tables)

# Cookies für higgsfield lesen
cur.execute("SELECT host_key, name, value, path FROM cookies WHERE host_key LIKE '%higgsfield%'")
rows = cur.fetchall()
print(f"Higgsfield cookies found: {len(rows)}")

cookies = []
for row in rows:
    host_key, name, value, path = row
    if value:  # Nur unverschlüsselte
        cookies.append({"name": name, "value": value, "domain": host_key.lstrip("."), "path": path or "/"})
        print(f"  {name}: {value[:20]}...")

if cookies:
    b64 = base64.b64encode(json.dumps(cookies).encode()).decode()
    print("\nHIGGSFIELD_COOKIES secret value:")
    print(b64)
else:
    print("\nKeine unverschluesselten Cookies - Browser DevTools Methode noetig!")
    print("""
Oeffne Chrome Canary -> higgsfield.ai -> F12 -> Console -> einfuegen:

const c=[]; document.cookie.split(';').forEach(x=>{const[n,...v]=x.trim().split('='); c.push({name:n,value:v.join('='),domain:'higgsfield.ai',path:'/'});}); console.log(btoa(JSON.stringify(c)));

Den Base64-String als HIGGSFIELD_COOKIES in GitHub Secrets eintragen.
""")

conn.close()
tmp.unlink(missing_ok=True)
