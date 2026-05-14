"""
make_nature_video.py — Baut Video #1 "Max & Mia Discover Nature!"
aus fertigen Szenenbildern + Suno-Audio.

Kein Higgsfield-Video nötig: ffmpeg Ken-Burns-Effekt (Zoom + Pan)
macht aus jedem Bild einen lebendigen 12s-Clip.

Usage:
    python scripts/make_nature_video.py
    python scripts/make_nature_video.py --audio output/nature-discovery/audio.mp3
"""
from __future__ import annotations
import argparse
import subprocess
import shutil
import sys
from pathlib import Path

# ── Konfiguration ────────────────────────────────────────────────────────────
OUTPUT_DIR   = Path("output/nature-discovery")
SCENES_DIR   = OUTPUT_DIR / "scenes"
CLIPS_DIR    = OUTPUT_DIR / "clips"
AUDIO_FILE   = OUTPUT_DIR / "audio.mp3"

# Szenen-Reihenfolge → Bild-Mapping
SCENE_ORDER = ["intro", "verse1", "chorus", "verse1", "chorus",
               "bridge", "verse3", "verse4", "chorus", "outro"]

SCENE_DURATION = 9   # Sekunden pro Clip (10 Szenen × 9s = 90s)
FPS            = 24

def find_ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if not exe:
        for p in [r"C:\Program Files\WinGet\Links\ffmpeg.exe",
                  r"C:\Program Files\ffmpeg\bin\ffmpeg.exe"]:
            if Path(p).exists():
                return p
        sys.exit("ffmpeg nicht gefunden!")
    return exe

def ken_burns_clip(ffmpeg: str, img: Path, out: Path, index: int) -> None:
    """Erstellt einen Ken-Burns-Zoom-Clip aus einem Standbild."""
    # Abwechselnd zoom-in und zoom-out, leichter Pan
    duration = SCENE_DURATION
    total_frames = duration * FPS

    # Zoom: von 1.0 → 1.08 (oder umgekehrt)
    zoom_start = 1.0 if index % 2 == 0 else 1.08
    zoom_end   = 1.08 if index % 2 == 0 else 1.0
    zoom_speed = (zoom_end - zoom_start) / total_frames

    # Pan: leichte horizontale Bewegung
    pan_x = "iw/2-(iw/zoom/2)" if index % 3 != 1 else f"iw/2-(iw/zoom/2)+{index*5}"

    vf = (
        f"scale=1920:1080:force_original_aspect_ratio=decrease,"
        f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2,"
        f"zoompan=z='zoom+{zoom_speed:.6f}':x='{pan_x}':y='ih/2-(ih/zoom/2)'"
        f":d={total_frames}:s=1280x720:fps={FPS}"
    )

    cmd = [
        ffmpeg, "-y",
        "-loop", "1", "-i", str(img),
        "-vf", vf,
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-pix_fmt", "yuv420p",
        str(out)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  WARN ffmpeg error für {img.name}: {result.stderr[-500:]}")
    else:
        print(f"  ✅ Clip {index+1}: {out.name} ({duration}s)")

def build_video(audio: Path | None = None) -> tuple[Path, Path]:
    ffmpeg = find_ffmpeg()
    CLIPS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Ken-Burns-Clips für alle Szenen
    print("🎨 Ken-Burns-Clips generieren...")
    clip_paths = []
    for i, scene_name in enumerate(SCENE_ORDER):
        img = SCENES_DIR / f"{scene_name}.png"
        if not img.exists():
            # Fallback: irgendein vorhandenes Bild
            available = list(SCENES_DIR.glob("*.png"))
            if not available:
                sys.exit(f"Keine Bilder gefunden in {SCENES_DIR}")
            img = available[0]
            print(f"  WARN: {scene_name}.png fehlt, nutze {img.name}")
        out_clip = CLIPS_DIR / f"clip_{i:02d}_{scene_name}.mp4"
        ken_burns_clip(ffmpeg, img, out_clip, i)
        clip_paths.append(out_clip)

    # 2. Clips zusammenfügen
    print("\n📎 Clips zusammenfügen...")
    concat_file = OUTPUT_DIR / "concat.txt"
    with open(concat_file, "w") as f:
        for p in clip_paths:
            f.write(f"file '{p.resolve().as_posix()}'\n")

    concat_out = OUTPUT_DIR / "concat.mp4"
    subprocess.run([
        ffmpeg, "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy", str(concat_out)
    ], check=True, capture_output=True)
    print(f"  ✅ Concat: {concat_out}")

    # 3. Audio hinzufügen (falls vorhanden)
    if audio and audio.exists():
        print("\n🎵 Audio hinzufügen...")
        landscape = OUTPUT_DIR / "final_16x9.mp4"
        subprocess.run([
            ffmpeg, "-y",
            "-stream_loop", "-1", "-i", str(concat_out),
            "-i", str(audio),
            "-map", "0:v", "-map", "1:a",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest", "-movflags", "+faststart",
            str(landscape)
        ], check=True, capture_output=True)
        print(f"  ✅ 16:9 mit Audio: {landscape}")
    else:
        landscape = concat_out
        print("  ⚠️  Kein Audio — Video ohne Ton")

    # 4. 9:16 Crop für Reels/Shorts
    print("\n📱 9:16 Crop für Reels/Shorts...")
    vertical = OUTPUT_DIR / "final_9x16.mp4"
    subprocess.run([
        ffmpeg, "-y", "-i", str(landscape),
        "-vf", "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=720:1280",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", str(vertical)
    ], check=True, capture_output=True)
    print(f"  ✅ 9:16 für Reels: {vertical}")

    return landscape, vertical


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio", type=Path, default=AUDIO_FILE,
                        help="Pfad zur Audio-Datei (.mp3)")
    args = parser.parse_args()

    print("🎬 Max & Mia Discover Nature! — Video Builder")
    print(f"   Szenen: {len(SCENE_ORDER)} × {SCENE_DURATION}s = {len(SCENE_ORDER)*SCENE_DURATION}s")
    print()

    audio = args.audio if args.audio.exists() else None
    if not audio:
        print(f"  ⚠️  Audio nicht gefunden: {args.audio} — bitte Suno abwarten")

    landscape, vertical = build_video(audio)

    print(f"\n✅ FERTIG!")
    print(f"   16:9 (YouTube):   {landscape}")
    print(f"   9:16  (Reels):    {vertical}")
    file_mb = landscape.stat().st_size / 1024 / 1024
    print(f"   Größe:            {file_mb:.1f} MB")

if __name__ == "__main__":
    main()
