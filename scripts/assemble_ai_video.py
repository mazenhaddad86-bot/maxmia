"""
assemble_ai_video.py — Stitches all AI-generated 9:16 clips + Suno audio into final video.

Usage:
    python scripts/assemble_ai_video.py
"""
import subprocess
import shutil
import sys
import tempfile
from pathlib import Path

CLIPS_DIR  = Path("output/nature-discovery/ai_clips")
AUDIO_FILE = Path("output/nature-discovery/audio.mp3")
OUT_DIR    = Path("output/nature-discovery")
FFMPEG     = shutil.which("ffmpeg") or r"C:\Program Files\WinGet\Links\ffmpeg.exe"

# Clip order — best narrative flow matching the song structure
# Intro → Verse (forest discovery) → Chorus (butterflies/dancing) →
# Bridge (frog/bee) → Verse (squirrel/leaves) → Mushrooms →
# Forestwalk atmosphere → Outro
CLIP_SEQUENCE = [
    # Intro — entering the forest
    "intro_01_seedance_9x16.mp4",
    "intro_02_running_9x16.mp4",
    "intro_04_forestpath.mp4",       # flowers blooming, deer watching
    "intro_03_birds_9x16.mp4",
    # Chorus — butterflies & dancing
    "chorus_02_dance_veo.mp4",
    "chorus_03_chase.mp4",
    "chorus_01_spin_9x16.mp4",
    # Bridge — pond & insects
    "bridge_01_bumblebee.mp4",
    "bridge_02_frog.mp4",
    "bridge_03_frog_croak.mp4",
    # Squirrel & Autumn
    "squirrel_01_tracking.mp4",
    "squirrel_02_closeup.mp4",
    "squirrel_03_leaves.mp4",
    # Mushrooms — magical glow
    "mushroom_01_touch.mp4",
    "mushroom_02_atmosphere.mp4",
    "mushroom_03_glow.mp4",
    # Forestwalk — atmosphere
    "forestwalk_01_fireflies.mp4",
    "forestwalk_02_leaf.mp4",
    # Outro — celebration & farewell
    "outro_01_jump.mp4",
    "outro_02_bow.mp4",
    "outro_03_spin.mp4",
]


def run(cmd: list[str], check=True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def normalize_clip(clip: Path, out: Path) -> bool:
    """Scale any resolution to 720x1280, re-encode, strip audio."""
    cmd = [
        FFMPEG, "-y", "-i", str(clip),
        "-vf", "scale=720:1280:force_original_aspect_ratio=decrease,"
               "pad=720:1280:(ow-iw)/2:(oh-ih)/2:color=black",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-an", "-r", "24",
        str(out)
    ]
    r = subprocess.run(cmd, capture_output=True)
    return r.returncode == 0


def main():
    print("🎬 Assembling Max & Mia AI video...\n")

    # Collect available clips (skip missing ones gracefully)
    available = []
    missing = []
    for name in CLIP_SEQUENCE:
        p = CLIPS_DIR / name
        if p.exists():
            available.append(p)
        else:
            missing.append(name)

    if missing:
        print(f"  ⚠️  Missing clips (will skip): {', '.join(missing)}")
    print(f"  ✅ Using {len(available)} clips × 8s = {len(available)*8}s total\n")

    if len(available) < 10:
        sys.exit("Not enough clips! Need at least 10.")

    # Normalize all clips to 720x1280 in a temp dir
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        norm_clips = []
        print("📐 Normalizing clips to 720×1280...")
        for clip in available:
            out = tmp / f"norm_{clip.name}"
            ok = normalize_clip(clip, out)
            if ok:
                norm_clips.append(out)
                print(f"  ✅ {clip.name}")
            else:
                print(f"  ⚠️  Skip (encode error): {clip.name}")

        # Write concat list
        concat_file = tmp / "concat.txt"
        concat_file.write_text(
            "\n".join(f"file '{p.as_posix()}'" for p in norm_clips)
        )

        # Concatenate
        print("\n📎 Concatenating...")
        concat_raw = tmp / "concat_raw.mp4"
        run([
            FFMPEG, "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy", str(concat_raw)
        ])
        print(f"  ✅ Raw concat done ({len(norm_clips)} clips)")

        # Add audio
        landscape = OUT_DIR / "final_ai_16x9.mp4"
        # First make landscape (16:9 version) with audio
        print("\n🎵 Adding audio...")
        if AUDIO_FILE.exists():
            run([
                FFMPEG, "-y",
                "-stream_loop", "-1", "-i", str(concat_raw),
                "-i", str(AUDIO_FILE),
                "-map", "0:v", "-map", "1:a",
                "-c:v", "libx264", "-preset", "fast", "-crf", "20",
                "-c:a", "aac", "-b:a", "192k",
                "-shortest", "-movflags", "+faststart",
                str(landscape)
            ])
            print(f"  ✅ With audio: {landscape}")
        else:
            shutil.copy(concat_raw, landscape)
            print(f"  ⚠️  No audio — copying raw: {landscape}")

        # Final 9:16 (already 9:16 content, just copy with faststart)
        vertical = OUT_DIR / "final_ai_9x16.mp4"
        run([
            FFMPEG, "-y", "-i", str(landscape),
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", str(vertical)
        ])

    size_mb = landscape.stat().st_size / 1024 / 1024
    dur_s   = len(norm_clips) * 8
    print(f"\n✅ DONE!")
    print(f"   9:16 Reels:  {vertical}  ({vertical.stat().st_size/1024/1024:.1f} MB)")
    print(f"   Duration:    {dur_s//60}:{dur_s%60:02d}")
    print(f"   Clips used:  {len(norm_clips)}")


if __name__ == "__main__":
    main()
