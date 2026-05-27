"""Concat 17 Kling Wheels clips + Suno audio = ECHTES Video."""
import subprocess, shutil
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
FFMPEG = shutil.which("ffmpeg") or r"C:\Program Files\WinGet\Links\ffmpeg.exe"
CLIPS = PROJECT / "output/wheels/clips"
AUDIO = PROJECT / "output/wheels/wheels_pep_16b83b57.mp3"
OUT   = PROJECT / "output/wheels/wheels_kling_final.mp4"

# Sorted order
order = sorted(CLIPS.glob("W*.mp4"), key=lambda p: int(p.stem.replace("W","")))
print(f"Clips: {len(order)}")
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
subprocess.run(cmd, check=True)
print(f"DONE: {OUT}")
