"""
Shorts Creator — schneidet ein Hauptvideo in 3-4 YouTube Shorts
Jeder Short: max 60 Sekunden, 9:16 (center crop), dann direkt hochladen
"""
import os
import sys
import subprocess
import math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from upload import upload_video

def create_shorts(video_path: str, theme: str, num_shorts: int = 3):
    """
    Schneidet das Hauptvideo in num_shorts Teile und lädt sie hoch.
    Jeder Short wird auf 9:16 gecroppt (für YouTube Shorts).
    """
    video_path = Path(video_path)
    out_dir = video_path.parent / "shorts"
    out_dir.mkdir(exist_ok=True)

    # Videolänge ermitteln
    result = subprocess.run([
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_streams", str(video_path)
    ], capture_output=True, text=True)

    import json
    info = json.loads(result.stdout)
    duration = float(next(s["duration"] for s in info["streams"] if s["codec_type"] == "video"))

    # Segment-Länge berechnen (max 59 Sekunden pro Short)
    segment_duration = min(59, math.floor(duration / num_shorts))

    print(f"Video: {duration:.1f}s → {num_shorts} Shorts à {segment_duration}s")

    short_paths = []
    for i in range(num_shorts):
        start = i * segment_duration
        if start >= duration:
            break

        out_path = out_dir / f"{theme.replace(' ', '_')}_short_{i+1}.mp4"

        # Crop zu 9:16 (center crop von 16:9) + segment schneiden
        subprocess.run([
            "ffmpeg", "-y",
            "-ss", str(start),
            "-t", str(segment_duration),
            "-i", str(video_path),
            "-vf", "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "192k",
            str(out_path)
        ], capture_output=True)

        if out_path.exists():
            size_mb = out_path.stat().st_size / 1024 / 1024
            print(f"Short {i+1}: {out_path.name} ({size_mb:.1f} MB)")
            short_paths.append(str(out_path))

    # Hochladen
    video_ids = []
    for i, short_path in enumerate(short_paths):
        title = f"{theme} Part {i+1} | Max und Mia World #Shorts"
        description = (
            f"{theme} - Max und Mia World 🎵\n\n"
            f"Nursery Rhymes für Kinder!\n\n"
            f"#Shorts #NurseryRhymes #KidsMusic #MaxMiaWorld #Kinderlieder #{theme.replace(' ', '')}"
        )
        tags = ["Shorts", "NurseryRhymes", "Kids", "MaxMiaWorld", "Kinderlieder",
                "KidsMusic", "Animation", theme, "Kinder", "Kinderlied"]

        print(f"\nLade Short {i+1} hoch: {title}")
        try:
            vid_id = upload_video(
                video_path=short_path,
                title=title,
                description=description,
                tags=tags,
                category_id="27",
                privacy="public",
            )
            video_ids.append(vid_id)
            print(f"✅ Short {i+1} hochgeladen: https://youtube.com/shorts/{vid_id}")
        except Exception as e:
            print(f"❌ Short {i+1} Fehler: {e}")

    return video_ids


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--theme", required=True)
    parser.add_argument("--num", type=int, default=3)
    args = parser.parse_args()

    ids = create_shorts(args.video, args.theme, args.num)
    print(f"\n✅ {len(ids)} Shorts hochgeladen!")
