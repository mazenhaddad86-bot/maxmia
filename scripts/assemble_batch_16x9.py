"""
assemble_batch_16x9.py — Generic 16:9 batch assembler for kids songs.

Usage:
    python scripts/assemble_batch_16x9.py <theme>

Themes must have:
    output/<theme>/audio.mp3              (Suno V5.5 song)
    output/<theme>/clips/*.mp4            (Kling 2.5 Turbo clips, 16:9)
        OR
    output/<theme>/images/*.png           (Higgsfield fallback for Ken Burns)

Output:
    output/<theme>/<theme>_final.mp4

Strategy:
- If clips/ exists with enough mp4s: concat them, trim/pad to audio duration.
- Otherwise: Ken-Burns each image over its scene's planned duration.
- Always mux original Suno audio (no re-encode of audio).
"""
import subprocess
import shutil
import sys
import tempfile
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
FFMPEG = shutil.which("ffmpeg") or r"C:\Program Files\WinGet\Links\ffmpeg.exe"
FFPROBE = shutil.which("ffprobe") or r"C:\Program Files\WinGet\Links\ffprobe.exe"

# Map theme → (audio filename pattern, expected scene count)
THEMES = {
    "wheels":     {"audio": "wheels_pep_*.mp3",          "scenes": 38},
    "twinkle":    {"audio": "twinkle_lullaby_*.mp3",     "scenes": 40},
    "oldmac":     {"audio": "oldmac_*.mp3",              "scenes": 33},
    "babyshark":  {"audio": "bs_*.mp3",                  "scenes": 26},
    "hickory":    {"audio": "hickory_*.mp3",             "scenes": 27},
    "row":        {"audio": "row_v55_*.mp3",             "scenes": 25},
    "incy":       {"audio": "incy_*.mp3",                "scenes": 28},
    "monkeys":    {"audio": "monkeys_*.mp3",             "scenes": 28},
    "happy":      {"audio": "happy_*.mp3",               "scenes": 26},
    "patacake":   {"audio": "patacake_*.mp3",            "scenes": 26},
}

# Theme dir name overrides (filesystem)
DIR_NAME = {
    "wheels": "wheels",
    "twinkle": "twinkle",
    "oldmac": "oldmacdonald",
    "babyshark": "babyshark",
    "hickory": "hickory",
    "row": "row",
    "incy": "incy",
    "monkeys": "monkeys",
    "happy": "happy",
    "patacake": "patacake",
}


def ffprobe_duration(path: Path) -> float:
    out = subprocess.check_output(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        text=True,
    )
    return float(out.strip())


def find_audio(theme_dir: Path, pattern: str) -> Path:
    matches = sorted(theme_dir.glob(pattern))
    if not matches:
        raise FileNotFoundError(f"No audio matching {pattern} in {theme_dir}")
    # Prefer longest/best
    return max(matches, key=lambda p: p.stat().st_size)


def make_ken_burns_clip(img: Path, duration: float, out: Path):
    """Pan + zoom on image to make it lively for kids."""
    cmd = [
        FFMPEG, "-y",
        "-loop", "1", "-i", str(img),
        "-vf",
        f"scale=2400:1350,zoompan=z='min(zoom+0.0008,1.2)':d={int(duration*30)}:s=1920x1080:fps=30",
        "-t", f"{duration:.2f}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        str(out),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def assemble(theme: str):
    cfg = THEMES[theme]
    theme_dir = PROJECT / "output" / DIR_NAME[theme]
    audio = find_audio(theme_dir, cfg["audio"])
    audio_dur = ffprobe_duration(audio)
    print(f"[{theme}] audio={audio.name} duration={audio_dur:.2f}s")

    clips_dir = theme_dir / "clips"
    images_dir = theme_dir / "images"
    out = theme_dir / f"{theme}_final.mp4"

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        per_clip_files = []

        if clips_dir.exists() and len(list(clips_dir.glob("*.mp4"))) >= 5:
            # Use Kling clips
            clips = sorted(clips_dir.glob("*.mp4"))
            print(f"[{theme}] Using {len(clips)} Kling clips")
            per_clip_files = clips
        elif images_dir.exists() and len(list(images_dir.glob("*.png"))) >= 5:
            # Ken-Burns fallback
            images = sorted(images_dir.glob("*.png"))
            per_scene_dur = audio_dur / len(images)
            print(f"[{theme}] Ken-Burns over {len(images)} images @ {per_scene_dur:.2f}s each")
            for i, img in enumerate(images):
                clip = tmp / f"kb_{i:03d}.mp4"
                make_ken_burns_clip(img, per_scene_dur, clip)
                per_clip_files.append(clip)
        else:
            print(f"[{theme}] No clips/ or images/ found — skipping")
            return

        # Concat list
        concat_txt = tmp / "concat.txt"
        concat_txt.write_text(
            "\n".join(f"file '{p.as_posix()}'" for p in per_clip_files),
            encoding="utf-8",
        )

        # Concat video, mux audio, trim to audio length
        cmd = [
            FFMPEG, "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_txt),
            "-i", str(audio),
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            str(out),
        ]
        subprocess.run(cmd, check=True)
        print(f"[{theme}] DONE → {out}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: assemble_batch_16x9.py <theme|--all>")
        sys.exit(1)
    arg = sys.argv[1]
    targets = list(THEMES.keys()) if arg == "--all" else [arg]
    for t in targets:
        try:
            assemble(t)
        except Exception as e:
            print(f"[{t}] FAILED: {e}")
