"""Concat 36 Kling Twinkle clips + Suno audio = ECHTES Video."""
import subprocess, shutil
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
FFMPEG = shutil.which("ffmpeg") or r"C:\Program Files\WinGet\Links\ffmpeg.exe"
CLIPS = PROJECT / "output/twinkle/clips"
AUDIO = PROJECT / "output/twinkle/twinkle_lullaby_ac051e17.mp3"
OUT   = PROJECT / "output/twinkle/twinkle_kling_final.mp4"

# Sorted order: C01.mp4 ... C36.mp4
order = sorted(CLIPS.glob("C*.mp4"), key=lambda p: int(p.stem.replace("C","")))
print(f"Clips found: {len(order)}")
for c in order:
    print(f"  {c.name} ({c.stat().st_size//1024}KB)")

concat_txt = CLIPS / "concat.txt"
concat_txt.write_text("\n".join(f"file '{p.as_posix()}'" for p in order), encoding="utf-8")

# Concat + add audio + trim to audio duration
cmd = [FFMPEG, "-y",
       "-f", "concat", "-safe", "0", "-i", str(concat_txt),
       "-i", str(AUDIO),
       "-map", "0:v:0", "-map", "1:a:0",
       "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20",
       "-c:a", "aac", "-b:a", "192k",
       "-shortest",
       str(OUT)]
print("Running ffmpeg...")
subprocess.run(cmd, check=True)
print(f"DONE: {OUT}")
print(f"Size: {OUT.stat().st_size // 1024 // 1024}MB")
