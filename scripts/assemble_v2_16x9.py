"""
assemble_v2_16x9.py — Assembliert das neue 16:9 Video aus allen Clips.
"""
import subprocess, shutil, sys, tempfile
from pathlib import Path

CLIPS_DIR  = Path("output/nature-discovery/clips_16x9")
AUDIO_FILE = Path("output/nature-discovery/audio.mp3")
OUT_DIR    = Path("output/nature-discovery")
FFMPEG     = shutil.which("ffmpeg") or r"C:\Program Files\WinGet\Links\ffmpeg.exe"

# Clip order — narrative flow
CLIP_SEQUENCE = [
    "01_forest_intro.mp4",
    "02_butterflies.mp4",
    "03_chorus_spin.mp4",
    "04_chorus_run.mp4",
    "05_chorus_jump.mp4",
    "06_frog_croak.mp4",
    "07_bee_hover.mp4",
    "08_frog_splash.mp4",
    "09_squirrel_reveal.mp4",
    "10_squirrel_tiptoe.mp4",
    "11_squirrel_nibble.mp4",
    "12_autumn_leaves.mp4",
    "13_mushroom_glow.mp4",
    "14_night_forest.mp4",
    "15_sparkles_forest.mp4",
    "16_outro_wave.mp4",
    "17_outro_finale.mp4",
]


def normalize_clip(clip: Path, out: Path) -> bool:
    cmd = [
        FFMPEG, "-y", "-i", str(clip),
        "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,"
               "pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=black",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-an", "-r", "24",
        str(out)
    ]
    r = subprocess.run(cmd, capture_output=True)
    return r.returncode == 0


def main():
    print("Assembliere 16:9 Video V2...\n")

    available = []
    for name in CLIP_SEQUENCE:
        p = CLIPS_DIR / name
        if p.exists():
            available.append(p)
        else:
            print(f"  MISSING: {name}")

    print(f"  Clips: {len(available)} x 8s = {len(available)*8}s\n")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        norm_clips = []
        print("Normalisiere auf 1280x720...")
        for clip in available:
            out = tmp / f"norm_{clip.name}"
            ok = normalize_clip(clip, out)
            if ok:
                norm_clips.append(out)
                print(f"  OK  {clip.name}")
            else:
                print(f"  ERR {clip.name}")

        # Concat list
        concat_file = tmp / "concat.txt"
        concat_file.write_text(
            "\n".join(f"file '{p.as_posix()}'" for p in norm_clips)
        )

        # Concatenate
        print(f"\nKonkateniere {len(norm_clips)} Clips...")
        concat_raw = tmp / "concat_raw.mp4"
        r = subprocess.run([
            FFMPEG, "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy", str(concat_raw)
        ], capture_output=True)
        if r.returncode != 0:
            print("CONCAT FEHLER:", r.stderr.decode()[-500:])
            return

        # Add audio
        final = OUT_DIR / "final_v2_16x9.mp4"
        print("\nFuege Audio hinzu...")
        if AUDIO_FILE.exists():
            r = subprocess.run([
                FFMPEG, "-y",
                "-stream_loop", "-1", "-i", str(concat_raw),
                "-i", str(AUDIO_FILE),
                "-map", "0:v", "-map", "1:a",
                "-c:v", "libx264", "-preset", "fast", "-crf", "20",
                "-c:a", "aac", "-b:a", "192k",
                "-shortest", "-movflags", "+faststart",
                str(final)
            ], capture_output=True)
            if r.returncode != 0:
                print("AUDIO FEHLER:", r.stderr.decode()[-500:])
        else:
            shutil.copy(concat_raw, final)
            print("  Kein Audio - kopiere ohne Ton")

    dur = len(norm_clips) * 8
    size = final.stat().st_size / 1024 / 1024
    print(f"\n==========================================")
    print(f"FERTIG!  {final.name}  ({size:.1f} MB)")
    print(f"Format:  1280x720, 16:9, True Native")
    print(f"Laenge:  {dur//60}:{dur%60:02d}  ({len(norm_clips)} Clips)")
    print(f"==========================================")


if __name__ == "__main__":
    main()
