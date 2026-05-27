"""Download BS03-BS18 Kling clips. Run: python scripts/download_bs_kling.py"""
import requests, os
from pathlib import Path

BASE = Path(__file__).parent.parent
OUT = BASE / "output/babyshark/clips"
OUT.mkdir(exist_ok=True)

BS_URLS = {
    "BS03": "https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260527_140442_59d4e0c0-3dd1-4aac-8cf4-f1a5b1450cdd.mp4",
    "BS04": "https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260527_140442_b63fb7ad-8351-42ea-9a3a-03c19a3e5393.mp4",
    "BS05": "https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260527_140442_ead64638-73c3-40d9-bf69-3a3ddcff4c41.mp4",
    "BS06": "https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260527_140442_7ff91cbd-b7d5-4881-adf8-91a90a52d6c0.mp4",
    "BS07": "https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260527_140442_391d6817-c8ad-432d-aeef-e8e1f9a0f87c.mp4",
    "BS08": "https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260527_140442_0ce86060-8e29-4224-96b7-f8c1081b3014.mp4",
    "BS09": "https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260527_140442_96ef7a82-3146-4299-a095-7b73810ade13.mp4",
    "BS10": "https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260527_140442_d6ad206b-50db-40cf-b0e8-38337a0e98aa.mp4",
    "BS11": "https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260527_140442_033b309f-1be4-4a8b-8a6f-d6c84f46cfec.mp4",
    "BS12": "https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260527_140442_cc4ba604-0de6-4509-a8f7-3bfc3b36ed89.mp4",
    "BS13": "https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260527_140442_02c2cb49-1aff-400e-ac00-af72328373b7.mp4",
    "BS14": "https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260527_140442_9b13a1d6-6457-41b5-9c3f-81613aac49b9.mp4",
    "BS15": "https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260527_140442_08b139b3-4179-4ae7-8d1c-dd64c2522c3f.mp4",
    "BS16": "https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260527_140442_1a485b20-05ef-4932-b0c6-61a738b50043.mp4",
    "BS17": "https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260527_140442_a88c9d98-dcdd-4612-99c3-6862fbe800f4.mp4",
    "BS18": "https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260527_140442_4ff3c2d9-356e-4be5-86c0-49c04b038458.mp4",
}

print(f"Downloading {len(BS_URLS)} BS Kling clips to {OUT}")
for name, url in BS_URLS.items():
    dest = OUT / f"{name}.mp4"
    if dest.exists():
        print(f"  {name}: skip ({dest.stat().st_size/1024/1024:.1f}MB)")
        continue
    print(f"  {name}...", end="", flush=True)
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in r.iter_content(65536):
            f.write(chunk)
    print(f" {dest.stat().st_size/1024/1024:.1f}MB OK")

print("\nAll done! Now run: python scripts/concat_babyshark_kling.py")
