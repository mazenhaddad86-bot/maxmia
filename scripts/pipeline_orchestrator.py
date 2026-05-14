"""
Max & Mia World — Vollautomatische Pipeline
Läuft täglich via GitHub Actions

Ablauf:
1. Nächstes Lied aus themes.yaml auswählen (Round-Robin)
2. 36 Clip-Prompts generieren (Storyboard mit Rotem Faden)
3. Bilder generieren via Higgsfield Browser (Toggle ON = kostenlos)
4. Videos animieren via Higgsfield Browser (Kling 2.5 Turbo, kostenlos)
5. Musik aus Music-Ordner laden (oder Suno.com falls verfügbar)
6. ffmpeg: 3-Minuten-Video + Shorts zusammenbauen
7. YouTube Upload (public, Made for Kids, English)
"""
from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import yaml

# Pfade
ROOT = Path(__file__).parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SRC))

OUTPUT_BASE = ROOT / "output"
MUSIC_DIR = ROOT / "music"
THEMES_FILE = ROOT / "config" / "themes.yaml"
STATE_FILE = ROOT / "state.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("pipeline")

# Umgebungen für Roter Faden — werden rotiert damit nie dasselbe
ENVIRONMENTS = [
    "wide green meadow with wildflowers and blue sky, bright and cheerful",
    "colorful garden with rainbow flowers and white picket fence, soft natural daylight",
    "red barn farmyard with hay bales and sunflowers, warm afternoon light",
    "sunny forest path with tall trees and dappled light, clear blue sky",
    "pond with weeping willows and lily pads, bright and cheerful",
    "rolling hills with orchards and fruit trees, soft natural daylight",
    "cozy village square with cobblestones and colorful houses, warm afternoon light",
    "sandy beach with gentle waves and colorful beach balls, bright and cheerful",
    "mountain meadow with alpine flowers and butterflies, clear blue sky",
    "rainy day park with puddles and colorful umbrellas, soft natural daylight",
    "winter wonderland with snowflakes and warm glowing windows, bright and cheerful",
    "autumn forest with orange and red leaves, warm afternoon light",
]


# ── State management ─────────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"last_theme_index": -1}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))


# ── Theme selection ──────────────────────────────────────────────────────────

def pick_next_theme() -> dict:
    cfg = yaml.safe_load(THEMES_FILE.read_text(encoding="utf-8"))
    themes = cfg["themes"]
    state = load_state()
    idx = (state.get("last_theme_index", -1) + 1) % len(themes)
    state["last_theme_index"] = idx
    save_state(state)
    theme = dict(themes[idx])
    log.info(f"🎵 Gewähltes Lied: {theme['title']} (index {idx})")
    return theme, cfg.get("hashtags", [])


# ── Storyboard generieren ────────────────────────────────────────────────────

def build_storyboard(theme: dict) -> list[dict]:
    """
    Erstellt 36 Clips mit Rotem Faden aus Liedtext.
    Jeder Clip = eine Szene aus der Geschichte des Liedes.
    Verschiedene Umgebungen, keine Wiederholungen.
    """
    lyrics = theme.get("lyrics", "")
    title = theme["title"]
    visual_style = theme.get("visual_style", "3D Pixar animation style")

    # Lyrics in Abschnitte aufteilen
    sections = re.split(r"\[(?:Verse|Chorus|Bridge|Outro|Intro)\s*\d*\]", lyrics)
    sections = [s.strip() for s in sections if s.strip()]

    clips = []
    env_idx = 0

    for i in range(36):
        section_idx = i % max(len(sections), 1)
        section = sections[section_idx] if sections else ""
        lines = [l.strip() for l in section.split("\n") if l.strip()]
        line = lines[i % max(len(lines), 1)] if lines else f"Max and Mia in {title}"

        env = ENVIRONMENTS[env_idx % len(ENVIRONMENTS)]
        env_idx += 1

        prompt = (
            f"{line.rstrip('!')} — "
            f"{env}, {visual_style}, "
            f"soft natural daylight, bright and cheerful, "
            f"no dramatic light rays"
        )

        motion = (
            f"Gentle camera pan, Max and Mia {line[:40].lower()}, "
            f"happy expressions, smooth motion, 3D Pixar style"
        )

        clips.append({
            "idx": i + 1,
            "scene_desc": line,
            "environment": env,
            "image_prompt": prompt,
            "motion_prompt": motion,
            "img_url": None,
            "vid_url": None,
            "local_img": None,
            "local_vid": None,
            "status": "pending",
        })

    log.info(f"📋 Storyboard erstellt: {len(clips)} Clips")
    return clips


# ── Datei-Download ───────────────────────────────────────────────────────────

def download_file(url: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, dest)
    log.info(f"💾 Downloaded: {dest.name}")
    return dest


# ── jobs.json aktualisieren ──────────────────────────────────────────────────

def save_jobs(song_dir: Path, clips: list[dict]):
    jobs_file = song_dir / "jobs.json"
    jobs_file.write_text(json.dumps(clips, indent=2, ensure_ascii=False))


# ── Video Assembly via ffmpeg ────────────────────────────────────────────────

def assemble_video(song_dir: Path, clips: list[dict], theme: dict, hashtags: list) -> Path:
    clips_dir = song_dir / "clips"
    clips_dir.mkdir(exist_ok=True)

    # Concat-Liste für ffmpeg
    done_clips = [c for c in clips if c.get("local_vid") and Path(c["local_vid"]).exists()]

    if len(done_clips) < 8:
        raise RuntimeError(f"Zu wenig fertige Clips: {len(done_clips)}/36")

    # Clips wiederholen bis 3 Minuten erreicht (36 × 5s = 180s)
    target_count = 36
    while len(done_clips) < target_count:
        done_clips += done_clips[: target_count - len(done_clips)]

    concat_file = song_dir / "concat.txt"
    with open(concat_file, "w") as f:
        for c in done_clips[:target_count]:
            f.write(f"file '{c['local_vid']}'\n")

    # Musik auswählen
    song_id = theme["id"].replace("-", "_")
    music_candidates = sorted(MUSIC_DIR.glob(f"*{song_id.split('_')[0]}*.mp3")) + \
                       sorted(MUSIC_DIR.glob("*.mp3"))
    music_file = music_candidates[0] if music_candidates else None

    output_main = song_dir / f"{theme['id']}_FINAL.mp4"

    # ffmpeg: Clips zusammenfügen
    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
    ]

    if music_file:
        cmd_concat += [
            "-i", str(music_file),
            "-c:v", "libx264", "-c:a", "aac",
            "-shortest",
            "-map", "0:v:0", "-map", "1:a:0",
        ]
    else:
        cmd_concat += ["-c:v", "libx264", "-an"]

    cmd_concat += [
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
        str(output_main),
    ]

    log.info("🎬 ffmpeg: Hauptvideo zusammenbauen...")
    subprocess.run(cmd_concat, check=True)
    log.info(f"✅ Hauptvideo: {output_main}")

    # Shorts (9:16 crop, max 60s)
    shorts_dir = song_dir / "shorts"
    shorts_dir.mkdir(exist_ok=True)
    output_short = shorts_dir / f"{theme['id']}_SHORT.mp4"

    cmd_short = [
        "ffmpeg", "-y",
        "-i", str(output_main),
        "-t", "60",
        "-vf", "crop=ih*9/16:ih,scale=1080:1920",
        "-c:v", "libx264", "-c:a", "aac",
        str(output_short),
    ]
    subprocess.run(cmd_short, check=True)
    log.info(f"✅ Short: {output_short}")

    return output_main


# ── YouTube Upload ───────────────────────────────────────────────────────────

def upload_to_youtube(video_path: Path, short_path: Path, theme: dict, hashtags: list):
    """YouTube Upload mit gespeichertem OAuth-Token."""
    sys.path.insert(0, str(ROOT / "youtube"))
    from upload import upload_video  # Existing upload script

    tag_str = " ".join(hashtags[:5])
    title = f"{theme['title']} | Max & Mia World | Nursery Rhyme"[:100]

    description = f"""{theme.get('caption', theme['title'])}

🎵 Subscribe to Max & Mia World for new nursery rhymes every day!
👶 Perfect for toddlers, babies and preschoolers!
📚 Educational songs for kids aged 1-5!

{tag_str}
{" ".join(hashtags)}

#MaxAndMiaWorld #NurseryRhymes #KidsSongs #ToddlerLearning #ChildrensMusic"""

    tags = [
        "Max and Mia", "nursery rhymes", "kids songs", "toddler learning",
        "educational videos for kids", "children's music", "baby songs",
        theme["title"],
    ] + [h.replace("#", "") for h in hashtags[:8]]

    # Hauptvideo
    log.info("📺 YouTube Upload: Hauptvideo...")
    vid_id = upload_video(
        video_path=str(video_path),
        title=title,
        description=description,
        tags=tags,
        category_id="27",
        privacy="public",
    )
    log.info(f"✅ Hauptvideo live: https://www.youtube.com/watch?v={vid_id}")

    # Short
    if short_path.exists():
        short_title = f"{theme['title']} #Shorts | Max & Mia World"[:100]
        log.info("📺 YouTube Upload: Short...")
        short_id = upload_video(
            video_path=str(short_path),
            title=short_title,
            description=description,
            tags=tags + ["Shorts"],
            category_id="27",
            privacy="public",
        )
        log.info(f"✅ Short live: https://www.youtube.com/shorts/{short_id}")


# ── Hauptpipeline ────────────────────────────────────────────────────────────

def run_pipeline():
    log.info("=" * 60)
    log.info("🚀 Max & Mia World Pipeline gestartet")
    log.info("=" * 60)

    # Higgsfield Cloud Import
    from higgsfield_cloud import generate_image, generate_video

    # 1. Lied auswählen
    theme, hashtags = pick_next_theme()
    song_dir = OUTPUT_BASE / theme["id"]
    song_dir.mkdir(parents=True, exist_ok=True)

    # 2. Storyboard
    clips = build_storyboard(theme)
    save_jobs(song_dir, clips)

    clips_dir = song_dir / "clips"
    clips_dir.mkdir(exist_ok=True)

    # 3. Bilder generieren
    log.info(f"\n🎨 Phase 1: Bilder generieren ({len(clips)} Stück)...")
    for i, clip in enumerate(clips):
        try:
            log.info(f"  [{i+1:02d}/36] {clip['scene_desc'][:50]}")
            img_url = generate_image(clip["image_prompt"])
            local_img = clips_dir / f"img_{i+1:02d}.jpg"
            download_file(img_url, local_img)
            clip["img_url"] = img_url
            clip["local_img"] = str(local_img)
            clip["status"] = "img_done"
            save_jobs(song_dir, clips)
            time.sleep(2)  # Kurze Pause zwischen Requests
        except Exception as e:
            log.error(f"  ❌ Bild {i+1} fehlgeschlagen: {e}")
            clip["status"] = f"img_error: {e}"
            save_jobs(song_dir, clips)

    # 4. Videos generieren
    log.info(f"\n🎬 Phase 2: Videos animieren ({len(clips)} Stück)...")
    for i, clip in enumerate(clips):
        if not clip.get("img_url"):
            log.warning(f"  [{i+1:02d}] Kein Bild → überspringe")
            continue
        try:
            log.info(f"  [{i+1:02d}/36] {clip['scene_desc'][:50]}")
            vid_url = generate_video(clip["img_url"], clip["motion_prompt"])
            local_vid = clips_dir / f"vid_{i+1:02d}.mp4"
            download_file(vid_url, local_vid)
            clip["vid_url"] = vid_url
            clip["local_vid"] = str(local_vid)
            clip["status"] = "vid_done"
            save_jobs(song_dir, clips)
            time.sleep(3)
        except Exception as e:
            log.error(f"  ❌ Video {i+1} fehlgeschlagen: {e}")
            clip["status"] = f"vid_error: {e}"
            save_jobs(song_dir, clips)

    # 5. Video zusammenbauen
    log.info("\n🔧 Phase 3: Video zusammenbauen...")
    try:
        final_video = assemble_video(song_dir, clips, theme, hashtags)
    except Exception as e:
        log.error(f"❌ Assembly fehlgeschlagen: {e}")
        sys.exit(1)

    # 6. YouTube Upload
    log.info("\n📺 Phase 4: YouTube Upload...")
    try:
        short_path = song_dir / "shorts" / f"{theme['id']}_SHORT.mp4"
        upload_to_youtube(final_video, short_path, theme, hashtags)
    except Exception as e:
        log.error(f"❌ YouTube Upload fehlgeschlagen: {e}")
        # Nicht fatal — Video ist trotzdem generiert

    log.info("\n" + "=" * 60)
    log.info("✅ Pipeline komplett!")
    log.info(f"   Lied: {theme['title']}")
    log.info(f"   Clips: {sum(1 for c in clips if 'vid_done' in c.get('status', ''))}/36")
    log.info("=" * 60)


if __name__ == "__main__":
    run_pipeline()
