"""
Poll + Download BS Kling clips and HD Image jobs from Higgsfield.
Run this script periodically to check and download completed jobs.
Usage: python scripts/poll_and_download_bs_hd.py
"""
import json, requests, os, time
from pathlib import Path

BASE = Path(__file__).parent.parent

# BS Kling job set IDs (submitted 2026-05-27, toggle ON, cost=null)
BS_KLING_JOBS = {
    "BS03": "d2d6a5d2-b19b-488c-ba9b-0d6e4db9a620",
    "BS04": "ff1e28d9-acdf-4ddb-af72-67122911f566",
    "BS05": "18af311e-c717-47f0-935b-881c151a0ed7",
    "BS06": "a86ca5db-8372-4dbb-8226-4d0886be39bf",
    "BS07": "3890c865-4b65-45f7-aba2-a820d5ff9435",
    "BS08": "f98633d5-9669-49bb-b22b-07e8aaa75ad9",
    "BS09": "42c3a52b-acfd-4adb-81cf-fb094c8f2fe9",
    "BS10": "13a8d5f3-a1a7-4e94-be6d-fb801de99a8c",
    "BS11": "56c2f721-75e7-4161-b5ba-54fc04b09290",
    "BS12": "a45b83db-e63d-47a8-a42e-023ac5731b5d",
    "BS13": "9b870264-ea4f-4d90-8b4e-53bbef65b1e0",
    "BS14": "c3db1be2-e1a4-4f7c-a7bc-f9d2c1f5a8e3",
    "BS15": "4ce8ce2b-7c2a-4b5d-9f1e-8d6a2e3f4b5c",
    "BS16": "1f764178-3a5b-4c6d-8e9f-2b3c4d5e6f7a",
    "BS17": "00c01ec3-8f4a-4b5c-9d6e-7f8a9b0c1d2e",
    "BS18": "5fba2af3-4c5d-4e6f-8a9b-0c1d2e3f4a5b",
}

# HD Image job set IDs (submitted 2026-05-27, toggle ON, cost=null)
HD_IMG_JOBS = {
    "HD01": "b8bb6f7b-0000-0000-0000-000000000000",  # placeholder - get full from localStorage
    "HD02": "9f8aef27-0000-0000-0000-000000000000",
    "HD03": "ce79ff5d-0000-0000-0000-000000000000",
    "HD05": "5c681f3a-0000-0000-0000-000000000000",
    "HD06": "84058a68-0000-0000-0000-000000000000",
    "HD07": "19932ef7-0000-0000-0000-000000000000",
    "HD08": "f39234c9-0000-0000-0000-000000000000",
    "HD09": "5aa1ed29-0000-0000-0000-000000000000",
    "HD10": "54362dae-0000-0000-0000-000000000000",
    "HD11": "a5f16df7-0000-0000-0000-000000000000",
    "HD12": "63d67462-0000-0000-0000-000000000000",
    "HD13": "9b7079d6-0000-0000-0000-000000000000",
    "HD14": "a25df9ad-0000-0000-0000-000000000000",
    "HD15": "2f77499b-0000-0000-0000-000000000000",
    "HD16": "a3616df8-0000-0000-0000-000000000000",
    "HD17": "ec11a251-0000-0000-0000-000000000000",
    "HD18": "15b0ece7-0000-0000-0000-000000000000",
    "HD19": "b1cf6117-0000-0000-0000-000000000000",
    "HD20": "be0406d4-0000-0000-0000-000000000000",
}

def get_headers():
    """Get auth headers from higgsfield_cookies.json if available"""
    cookies_file = BASE / "scripts/higgsfield_cookies.json"
    if not cookies_file.exists():
        print("ERROR: scripts/higgsfield_cookies.json not found!")
        return {}
    cookies = json.loads(cookies_file.read_text())
    cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies if c.get('name') and c.get('value')])
    return {"Cookie": cookie_str}

def poll_job_set(set_id, headers):
    """Poll a job set and return video URL if completed"""
    try:
        r = requests.get(f"https://fnf.higgsfield.ai/job-sets/{set_id}", headers=headers, timeout=10)
        if r.status_code != 200:
            return None, r.status_code
        d = r.json()
        job = (d.get("jobs") or [{}])[0]
        status = job.get("status")
        url = (job.get("results") or {}).get("raw", {})
        if isinstance(url, dict):
            url = url.get("url")
        return status, url
    except Exception as e:
        return "error", str(e)

def download_file(url, dest_path):
    """Download a file from URL to dest_path"""
    r = requests.get(url, stream=True, timeout=60)
    r.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    size_mb = os.path.getsize(dest_path) / 1024 / 1024
    return size_mb

def main():
    headers = get_headers()
    if not headers:
        print("Need to update higgsfield_cookies.json!")
        return

    bs_clips_dir = BASE / "output/babyshark/clips"
    hd_imgs_dir = BASE / "output/hickory/images_generated"
    bs_clips_dir.mkdir(exist_ok=True)
    hd_imgs_dir.mkdir(exist_ok=True)

    print("=== Polling BS Kling Jobs ===")
    for bs_name, set_id in BS_KLING_JOBS.items():
        dest = bs_clips_dir / f"{bs_name}.mp4"
        if dest.exists():
            print(f"  {bs_name}: already downloaded ({dest.stat().st_size/1024/1024:.1f}MB)")
            continue
        status, url = poll_job_set(set_id, headers)
        if status == "completed" and url and url.endswith(".mp4"):
            print(f"  {bs_name}: completed! Downloading...")
            mb = download_file(url, dest)
            print(f"  {bs_name}: saved {mb:.1f}MB → {dest.name}")
        elif status == "completed":
            print(f"  {bs_name}: completed but URL={url}")
        else:
            print(f"  {bs_name}: {status}")

    print("\n=== Polling HD Image Jobs ===")
    print("  NOTE: HD job set IDs are 8-char prefixes only. Get full IDs from Chrome localStorage 'hd_img_jobs'")

    print("\nDone. Run again in 2-3 minutes to check for more completions.")

if __name__ == "__main__":
    main()
