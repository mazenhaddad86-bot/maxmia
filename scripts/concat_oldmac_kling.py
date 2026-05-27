"""Concat OldMac Kling clips + Suno audio."""
import subprocess, shutil
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
FFMPEG = shutil.which("ffmpeg") or r"C:\Program Files\WinGet\Links\ffmpeg.exe"
CLIPS = PROJECT / "output/oldmacdonald/clips"
AUDIO = PROJECT / "output/oldmacdonald/oldmac_2c1ea1ba.mp3"
OUT   = PROJECT / "output/oldmacdonald/oldmac_kling_final.mp4"

order = sorted(CLIPS.glob("OM*.mp4"), key=lambda p: int(p.stem.replace("OM","")))
print(f"Clips found: {len(order)}")
for c in order:
    print(f"  {c.name} ({c.stat().st_size//1024}KB)")

concat_txt = CLIPS / "concat.txt"
concat_txt.write_text("\n".join(f"file '{p.as_posix()}'" for p in order), encoding="utf-8")

cmd = [FFMPEG, "-y",
       "-f", "concat", "-safe", "0", "-i", str(concat_txt),
       "-i", str(AUDIO),
       "-map", "0:v:0", "-map", "1:a:0",
       "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20",
       "-c:a", "aac", "-b:a", "192k", "-shortest",
       str(OUT)]
print("Running ffmpeg...")
subprocess.run(cmd, check=True)
print(f"DONE: {OUT}  ({OUT.stat().st_size//1024//1024}MB)")
