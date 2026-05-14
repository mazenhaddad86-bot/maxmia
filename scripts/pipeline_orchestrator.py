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

def _parse_lyrics_sections(lyrics: str) -> dict:
    """Teilt Lyrics in benannte Sektionen: intro, verse, chorus, bridge, outro."""
    result = {"intro": [], "verse": [], "chorus": [], "bridge": [], "outro": []}
    current = "verse"
    for line in lyrics.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"\[(\w+)\s*\d*\]", line, re.IGNORECASE)
        if m:
            key = m.group(1).lower()
            if key in result:
                current = key
        else:
            result[current].append(line)
    # Fallback: alle Zeilen in verse wenn leer
    all_lines = [l for ll in result.values() for l in ll]
    if not result["verse"] and all_lines:
        result["verse"] = all_lines
    return result


def build_storyboard(theme: dict) -> list[dict]:
    """
    36 Clips mit echtem ROTEM FADEN — 3-Akt-Struktur:

    AKT 1 (Clips 01-08): Einführung — Max & Mia starten ihr Abenteuer
    AKT 2 (Clips 09-27): Hauptabenteuer — Story folgt Liedtext Zeile für Zeile
    AKT 3 (Clips 28-36): Triumph & Happy End — Feier, Lernerfolg, Abschluss
    """
    lyrics = theme.get("lyrics", "")
    title = theme["title"]
    vstyle = theme.get("visual_style", "3D Pixar animation style")
    learn = theme.get("learn_element", "letters and numbers")

    secs = _parse_lyrics_sections(lyrics)
    verse_lines  = secs["verse"]  or [f"Max and Mia learn {learn}"]
    chorus_lines = secs["chorus"] or verse_lines
    bridge_lines = secs["bridge"] or verse_lines
    intro_lines  = secs["intro"]  or [f"Let's start {title}!"]
    outro_lines  = secs["outro"]  or ["Hooray, we did it!"]

    # ── ACT 1: SETUP (Clips 1-8) ────────────────────────────────────────────
    act1 = [
        (
            "Max and Mia wake up excited — sunshine through the window, today is adventure day!",
            10, "Camera slowly zooms in on Max and Mia stretching and smiling, warm morning light"
        ),
        (
            "Max and Mia rush to the window pointing at the bright colorful world outside",
            0, "Quick pan following Max and Mia running to the window, excited and bouncy"
        ),
        (
            f"Max puts on his blue sweater, Mia ties her pink ribbons — ready for {title}!",
            1, "Close-up of Max and Mia getting dressed, big smiles, gentle camera pull-back"
        ),
        (
            f"{intro_lines[0].rstrip('!')} — Max and Mia step outside into a bright sunny world",
            0, "Wide shot, Max and Mia burst through the front door into sunlight, arms spread wide"
        ),
        (
            f"Max and Mia discover something magical — {learn} glowing and shining everywhere!",
            3, "Camera swirls around Max and Mia as colorful magic fills the air around them"
        ),
        (
            f"Mia points with delight and Max cheers — the wonderful world of {title} awaits!",
            1, "Max and Mia pointing and laughing, camera follows their gaze to the colorful scene"
        ),
        (
            "Max and Mia hold hands and skip forward together into the adventure — best friends!",
            0, "Tracking shot, Max and Mia skipping hand-in-hand on a bright sunlit path"
        ),
        (
            f"{chorus_lines[0].rstrip('!')} — Max and Mia begin their song with big happy smiles",
            2, "Slow zoom-out revealing Max and Mia in beautiful landscape, singing together"
        ),
    ]

    # ── ACT 2: ADVENTURE (Clips 9-27) — Liedtext Zeile für Zeile ────────────
    story_lines = []
    for l in verse_lines:
        story_lines.append(l)
    for l in chorus_lines:
        story_lines.append(l)
    for l in bridge_lines:
        story_lines.append(l)
    while len(story_lines) < 19:
        story_lines += story_lines
    story_lines = story_lines[:19]

    act2_envs = [3, 4, 5, 6, 7, 8, 9, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4]
    act2_motions = [
        "Gentle camera pan left, Max and Mia dancing and singing, happy expressions",
        "Camera slowly zooms in, Max pointing at something magical, Mia clapping",
        "Wide shot with slow push forward, Max and Mia exploring together",
        "Camera follows Max and Mia running and laughing, smooth tracking shot",
        "Close-up on faces, Max and Mia both smiling and singing along",
        "Camera rotates 360 around Max and Mia discovering something wonderful",
        "Camera tilts down from sky to reveal Max and Mia cheering below",
        "Side-scrolling pan, Max and Mia walking and pointing at things",
        "Zoom-out revealing a magical scene, Max and Mia in the center",
        "Gentle sway motion, Max and Mia swaying to the music together",
        "Camera cranes upward, Max and Mia looking up with wide-eyed wonder",
        "Max counts on his fingers while Mia watches and claps along",
        "Soft focus pull revealing Max and Mia learning something new together",
        "Camera spins slowly, colorful world surrounds Max and Mia",
        "Low angle shot looking up at Max and Mia jumping with joy",
        "Slow-motion, Max and Mia give each other a big high-five",
        "Tracking shot backward, Max and Mia confidently moving forward",
        "Close-up zoom-in on Mia's big eyes sparkling with wonder",
        "Wide celebration shot, Max and Mia with animal friends joining in",
    ]

    # ── ACT 3: TRIUMPH (Clips 28-36) ────────────────────────────────────────
    act3 = [
        (
            f"Max and Mia mastered {learn}! A huge glitter celebration explodes around them!",
            7, "Camera pulls back wide, Max and Mia jump for joy, confetti rains down"
        ),
        (
            f"{outro_lines[0].rstrip('!')} — Max and Mia cheer with all their animal friends!",
            8, "Wide angle, colorful animal friends join Max and Mia in a big group celebration"
        ),
        (
            f"Max holds a shining golden trophy for {title} — Mia claps with pride!",
            1, "Close-up on Max holding trophy, Mia beside him, both beaming with pride"
        ),
        (
            "A beautiful rainbow appears over Max and Mia — magical reward for finishing together!",
            0, "Camera tilts up to rainbow appearing, slow zoom-out with Max and Mia glowing below"
        ),
        (
            "Max and Mia do their victory dance — spinning, laughing, jumping with pure joy!",
            9, "Energetic spinning camera following Max and Mia dancing in a joyful circle"
        ),
        (
            "Mia hugs Max warmly — best friends forever, always learning together every day!",
            1, "Gentle warm close-up, Mia hugging Max, soft golden sunset light, heartwarming"
        ),
        (
            "Max and Mia wave goodbye to you — see you next time for more adventures!",
            0, "Slow zoom-out, Max and Mia waving directly at the camera, huge warm smiles"
        ),
        (
            "Magical sparkles fill the screen as the adventure ends — until next time!",
            0, "Camera slowly pulls back as golden sparkles fill the frame, magical ending"
        ),
        (
            "Max and Mia give a big thumbs up — YOU DID IT TOO! Great job learning today!",
            1, "Direct camera, Max and Mia thumbs up together, huge smiles, warm happy freeze"
        ),
    ]

    # ── Alle Clips zusammenbauen ────────────────────────────────────────────
    clips = []

    for scene, env_idx, motion in act1:
        env = ENVIRONMENTS[env_idx % len(ENVIRONMENTS)]
        clips.append({
            "idx": len(clips) + 1, "act": 1,
            "scene_desc": scene, "environment": env,
            "image_prompt": f"{scene} — {env}, {vstyle}, soft natural daylight, bright and cheerful",
            "motion_prompt": motion,
            "img_url": None, "vid_url": None, "local_img": None, "local_vid": None, "status": "pending",
        })

    for i, line in enumerate(story_lines):
        env = ENVIRONMENTS[act2_envs[i] % len(ENVIRONMENTS)]
        scene = f"Max and Mia: '{line.rstrip('!')}'"
        clips.append({
            "idx": len(clips) + 1, "act": 2,
            "scene_desc": scene, "lyric_line": line, "environment": env,
            "image_prompt": f"{scene} — {env}, {vstyle}, soft natural daylight, bright and cheerful",
            "motion_prompt": act2_motions[i],
            "img_url": None, "vid_url": None, "local_img": None, "local_vid": None, "status": "pending",
        })

    for scene, env_idx, motion in act3:
        env = ENVIRONMENTS[env_idx % len(ENVIRONMENTS)]
        clips.append({
            "idx": len(clips) + 1, "act": 3,
            "scene_desc": scene, "environment": env,
            "image_prompt": f"{scene} — {env}, {vstyle}, soft natural daylight, bright and cheerful",
            "motion_prompt": motion,
            "img_url": None, "vid_url": None, "local_img": None, "local_vid": None, "status": "pending",
        })

    log.info(f"📋 Storyboard: {len(clips)} Clips — Akt1=8 Akt2=19 Akt3=9 | Thema: {title}")
    log.info(f"   📚 Lernziel: {learn}")
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

    total = len(clips)

    # 3. Bilder generieren — direkt mit Session-Cookies (kein 403 mehr)
    log.info(f"\n🎨 Phase 1: Bilder generieren ({total} Stück)...")
    for i, clip in enumerate(clips):
        local_img = clips_dir / f"img_{i+1:02d}.jpg"
        try:
            log.info(f"  [{i+1:02d}/{total}] Akt{clip.get('act','-')}: {clip['scene_desc'][:55]}")
            img_url = generate_image(
                clip["image_prompt"],
                save_path=local_img,
            )
            clip["img_url"] = img_url
            clip["local_img"] = str(local_img)
            clip["status"] = "img_done"
            save_jobs(song_dir, clips)
            time.sleep(1)
        except Exception as e:
            log.error(f"  ❌ Bild {i+1} fehlgeschlagen: {e}")
            clip["status"] = f"img_error: {e}"
            save_jobs(song_dir, clips)

    img_ok = sum(1 for c in clips if c.get("status") == "img_done")
    log.info(f"✅ Bilder fertig: {img_ok}/{total}")

    # 4. Videos generieren — lokales Bild hochladen, Video mit Cookies laden
    log.info(f"\n🎬 Phase 2: Videos animieren ({total} Stück)...")
    for i, clip in enumerate(clips):
        if not clip.get("local_img") or not Path(clip["local_img"]).exists():
            log.warning(f"  [{i+1:02d}] Kein Bild → überspringe")
            continue
        local_vid = clips_dir / f"vid_{i+1:02d}.mp4"
        try:
            log.info(f"  [{i+1:02d}/{total}] Akt{clip.get('act','-')}: {clip['scene_desc'][:55]}")
            vid_url = generate_video(
                image_path=clip["local_img"],
                prompt=clip["motion_prompt"],
                save_path=local_vid,
            )
            clip["vid_url"] = vid_url
            clip["local_vid"] = str(local_vid)
            clip["status"] = "vid_done"
            save_jobs(song_dir, clips)
            time.sleep(2)
        except Exception as e:
            log.error(f"  ❌ Video {i+1} fehlgeschlagen: {e}")
            clip["status"] = f"vid_error: {e}"
            save_jobs(song_dir, clips)

    vid_ok = sum(1 for c in clips if c.get("status") == "vid_done")
    log.info(f"✅ Videos fertig: {vid_ok}/{total}")

    # 5. Musik generieren via Suno
    log.info("\n🎵 Phase 3: Musik generieren via Suno...")
    music_file = song_dir / f"{theme['id']}_music.mp3"
    try:
        from suno_cloud import generate_music
        generate_music(
            title=theme["title"],
            lyrics=theme.get("lyrics", ""),
            style=theme.get("music_style", "children's nursery rhyme, upbeat, fun"),
            output_path=music_file,
        )
        log.info(f"✅ Musik fertig: {music_file}")
    except Exception as e:
        log.warning(f"⚠️ Suno fehlgeschlagen ({e}) — nutze vorhandene Musik aus /music")
        # Fallback: vorhandene MP3 aus music/ Ordner
        candidates = sorted(MUSIC_DIR.glob("*.mp3"))
        if candidates:
            music_file = candidates[0]
            log.info(f"   Fallback: {music_file.name}")
        else:
            music_file = None

    # Musik-Pfad in clips übergeben für Assembly
    if music_file and music_file.exists():
        for clip in clips:
            clip["music_file"] = str(music_file)

    # 6. Video zusammenbauen
    log.info("\n🔧 Phase 4: Video zusammenbauen...")
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
