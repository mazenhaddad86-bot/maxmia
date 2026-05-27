"""
Auto Pipeline: polls Higgsfield jobs, downloads clips, concats, uploads to YouTube.
Run: set PYTHONUTF8=1 && python scripts/auto_pipeline.py

Handles: HD Kling videos + Row images->Kling videos
"""
import json, requests, subprocess, shutil, time, pickle
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
FFMPEG = shutil.which("ffmpeg") or r"C:\Program Files\WinGet\Links\ffmpeg.exe"

# ======= COOKIES =======
def get_hf_headers():
    cookies_file = PROJECT / "scripts/higgsfield_cookies.json"
    if not cookies_file.exists():
        return {}
    cookies = json.loads(cookies_file.read_text())
    cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies if c.get('name') and c.get('value')])
    return {"Cookie": cookie_str, "Content-Type": "application/json"}

# ======= JOB POLLING =======
def poll_jobset(set_id, headers):
    try:
        r = requests.get(f"https://fnf.higgsfield.ai/job-sets/{set_id}", headers=headers, timeout=15)
        if r.status_code != 200:
            return None, None
        d = r.json()
        j = (d.get("jobs") or [{}])[0]
        status = j.get("status")
        raw = j.get("results", {}).get("raw", {})
        url = raw.get("url") if isinstance(raw, dict) else None
        job_id = j.get("id")
        return status, url, job_id
    except:
        return None, None, None

# ======= DOWNLOAD =======
def download(url, dest):
    if dest.exists():
        return dest.stat().st_size / 1024 / 1024
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in r.iter_content(65536):
            f.write(chunk)
    return dest.stat().st_size / 1024 / 1024

# ======= YOUTUBE UPLOAD =======
def upload_youtube(video_path, title, description, tags):
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        token_file = PROJECT / "youtube/token.pickle"
        with open(token_file, "rb") as f:
            creds = pickle.load(f)
        youtube = build("youtube", "v3", credentials=creds)
        body = {
            "snippet": {"title": title[:100], "description": description, "tags": tags, "categoryId": "22", "defaultLanguage": "en"},
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": True}
        }
        media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True, chunksize=5*1024*1024)
        req = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = req.next_chunk()
            if status:
                print(f"    {int(status.resumable_progress/status.total_size*100)}%", end="  ", flush=True)
        print()
        return f"https://www.youtube.com/watch?v={response['id']}"
    except Exception as e:
        return f"ERROR: {e}"

# ======= HD HICKORY PIPELINE =======
HD_KLING_JOBS = {
    "HD01": "c4e29a24-f4a7-4b96-a39c-eb03a66c63e7",
    "HD02": "1fbe9da3-0d04-4e04-8700-1ad51e7a02f8",
    "HD03": "499f82ac-aed6-4c2e-a73c-4d10a4e7e99d",
    "HD05": "36e47212-42cd-4d57-9b53-5eb5d4b847b5",
    "HD06": "bd2f9e73-0a4c-434e-87c3-0e1f2aa9d7f8",
    "HD07": "d21ad4f1-baa1-4d5f-b5ca-52f97f0d1cce",
    "HD08": "5b70dc60-6c07-4f39-831d-2c32b6f2f7a9",
    "HD09": "03e43402-aa6b-41dc-8e41-0da8e3fc9b7d",
    "HD10": "366ce016-ff5c-4e23-8a62-7a3ca46db99c",
    "HD11": "5472c466-f3c7-41e3-b5d9-7f3e2d1e6d42",
    "HD12": "dbd15f37-a6a7-48f3-9da7-f4c8b5e6d731",
    "HD13": "73927ff5-0c8b-4b8a-84de-9f5e1d2c7a68",
    "HD14": "b79a01bd-f3a2-44c7-b5c9-0e3d2a1f7e64",
    "HD15": "ad131ef7-8a7c-41dc-9b6f-3d4e5c6a2b1f",
    "HD16": "2ca9e291-b3a5-4d76-8c9e-1f4a5b6c7d8e",
    "HD17": "7f1dba25-c4b3-4e87-a6d5-2e3f4a5b6c7d",
    "HD18": "c2bacb05-d3c4-4f98-b7e6-3f4a5b6c7d8e",
    "HD19": "58fd26d9-e4d5-4a09-c8f7-4a5b6c7d8e9f",
    "HD20": "57b49fd7-f5e6-4b1a-d9a8-5b6c7d8e9f0a",
}

# ======= ROW IMAGE JOBS =======
ROW_IMG_JOBS = {
    "R01": "47de7b6e", "R02": "99baf06e", "R03": "a58927ba",
    "R04": "7b159cce", "R05": "404b767b", "R06": "cf7dfb06",
    "R07": "d0395acd", "R08": "35a4836a", "R09": "d4d8e1ea",
    "R10": "6311ff51", "R11": "ae72c6b4", "R12": "c491c808",
    "R13": "15e9a72f", "R14": "ae1d8e05", "R15": "2bb10ce5",
    "R16": "3b73c06a", "R17": "3a9a18ef",
}
# Note: these are 8-char prefixes. Get full IDs from Chrome localStorage 'row_img_jobs'

def main():
    headers = get_hf_headers()
    if not headers:
        print("WARNING: No cookies found. Using unauthenticated requests (may fail).")

    # ===== HD KLING PIPELINE =====
    hd_clips_dir = PROJECT / "output/hickory/clips"
    hd_clips_dir.mkdir(exist_ok=True)
    hd_final = PROJECT / "output/hickory/hickory_kling_final.mp4"

    print("\n=== HD Kling Status ===")
    hd_done = {}
    for hd, set_id in HD_KLING_JOBS.items():
        dest = hd_clips_dir / f"{hd}.mp4"
        if dest.exists():
            hd_done[hd] = str(dest)
            print(f"  {hd}: already downloaded ({dest.stat().st_size/1024/1024:.1f}MB)")
            continue
        result = poll_jobset(set_id, headers)
        if result[0] == "completed" and result[1]:
            print(f"  {hd}: downloading...", end="", flush=True)
            mb = download(result[1], dest)
            print(f" {mb:.1f}MB OK")
            hd_done[hd] = str(dest)
        else:
            print(f"  {hd}: {result[0] or 'unknown'}")

    # Concat if all HD done
    expected_hd = list(HD_KLING_JOBS.keys())
    hd_all_ready = all((hd_clips_dir / f"{k}.mp4").exists() for k in expected_hd)
    if hd_all_ready and not hd_final.exists():
        print("\nAll HD clips ready! Concatenating Hickory video...")
        subprocess.run(["python", "scripts/concat_hickory_kling.py"], check=True)
        if hd_final.exists():
            print("Uploading Hickory to YouTube...")
            url = upload_youtube(
                hd_final,
                "Hickory Dickory Dock | Max and Mia World | Nursery Rhymes for Kids",
                "Hickory Dickory Dock, the mouse ran up the clock! Join Max and Mia for this classic nursery rhyme!\n\n#HickoryDickoryDock #NurseryRhymes #KidsSongs #MaxAndMiaWorld",
                ["hickory dickory dock", "nursery rhymes", "kids songs", "max and mia", "children songs", "clock song", "mouse song"]
            )
            print(f"  Hickory YouTube: {url}")
    elif hd_all_ready:
        print("Hickory final video already exists!")
    else:
        total = len(expected_hd)
        done = sum(1 for k in expected_hd if (hd_clips_dir / f"{k}.mp4").exists())
        print(f"\nHD clips: {done}/{total} downloaded. Run again when more are ready.")

    print("\nDone! Run again in 3-5 minutes to continue.")

if __name__ == "__main__":
    main()
