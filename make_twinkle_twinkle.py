"""
Twinkle Twinkle Little Star — vollautomatische Generierung
Max & Mia World | YouTube Kids Channel

Ablauf:
1. Playwright-Login via Email OTP (Gmail IMAP)
2. 36 Bilder generieren (Nano Banana Pro, Toggle ON = kostenlos)
3. 36 Videos animieren (Kling 2.5 Turbo, Toggle ON = kostenlos)
4. ffmpeg: 3-Min Video + Shorts
5. YouTube Upload
"""
import asyncio
import json
import logging
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

# Stell sicher dass src/ im Pfad ist
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

# Windows UTF-8
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("twinkle")

# Env vars setzen (lokal)
os.environ.setdefault("HIGGSFIELD_EMAIL", "makevision1412@gmail.com")
os.environ.setdefault("GMAIL_APP_PASSWORD", "xzrjyztrnmffkteq")

SONG_ID = "twinkle-twinkle-little-star"
SONG_TITLE = "Twinkle Twinkle Little Star"
OUTPUT_DIR = ROOT / "output" / SONG_ID
CLIPS_DIR = OUTPUT_DIR / "clips"
JOBS_FILE = OUTPUT_DIR / "jobs.json"

CHAR_PROMPT = (
    "Mia girl with brown pigtail hair and red ribbons, green eyes, freckles, "
    "pink dress with yellow stars, pink leggings, pink mary jane shoes. "
    "Max boy with curly brown hair, brown eyes, freckles, blue knit sweater, "
    "brown dungarees with dinosaur patch, red sneakers with white stripes. "
    "3D Pixar animation style, bright and cheerful."
)

STORYBOARD = [
    # ACT 1: Einführung (8 Clips)
    ("Max and Mia look up at the night sky full of bright glowing stars, eyes wide with wonder", "Camera slowly tilts up revealing the starry night sky, Max and Mia looking up with wonder"),
    ("Mia points at the brightest star twinkling in the sky, Max nods with excitement", "Gentle zoom toward the twinkling star, following Mia's pointed finger with soft camera motion"),
    ("Max and Mia sit together on a cozy blanket in a garden, looking up at the stars", "Wide shot pulling back to reveal Max and Mia on a blanket surrounded by soft garden flowers"),
    ("The biggest star begins to twinkle and glow extra bright just for Max and Mia", "Close-up on the glowing star, then reveal Max and Mia below smiling up at it"),
    ("Max sings 'Twinkle twinkle little star' while Mia claps along happily", "Camera follows Max as he sings, Mia dancing beside him, warm starlight falling on them"),
    ("Mia points up asking 'How I wonder what you are?' with curious big eyes", "Camera zooms in on Mia's curious face, then tilts up to the mysterious glowing star"),
    ("Max and Mia hold hands looking at the star that twinkles like a diamond in the sky", "Slow zoom out revealing Max and Mia holding hands under a beautiful starry sky"),
    ("A magical shooting star streaks across the sky above Max and Mia who cheer with joy", "Camera pans left following the shooting star across the sky, Max and Mia cheering below"),

    # ACT 2: Adventure (19 Clips — Liedtext)
    ("Max and Mia: 'Up above the world so high' — reaching up with arms toward the stars", "Camera cranes upward following Max and Mia's outstretched arms toward the glowing stars"),
    ("Max and Mia: 'Like a diamond in the sky' — a giant sparkling diamond appears next to the star", "Slow magical reveal of a glowing diamond shape in the sky, Max and Mia watching in awe"),
    ("Max and Mia: 'Twinkle twinkle little star' — the star blinks playfully at them", "The star twinkles in time with the song, Max and Mia giggling and clapping"),
    ("Max and Mia: 'How I wonder what you are?' — they look through a big telescope together", "Max and Mia both peering through a magical telescope, camera shows the star through the lens"),
    ("Max and Mia: 'When the blazing sun is gone' — a big friendly sun waves goodbye", "The sun sets with a friendly wave as Max and Mia watch, warm orange sky fading to purple"),
    ("Max and Mia: 'When he nothing shines upon' — the world gets quiet and moonlit together", "Night falls gently, Max and Mia in soft moonlight, peaceful and wonder-filled"),
    ("Max and Mia: 'Then you show your little light' — the star lights up just for them", "The star shines its beam down onto Max and Mia, magical golden glow surrounding them"),
    ("Max and Mia: 'Twinkle twinkle all the night!' — dancing under a sky full of stars", "Max and Mia spinning and dancing under countless twinkling stars, pure joy on their faces"),
    ("Max and Mia: 'In the dark blue sky you keep' — they point at the star leading them home", "Camera follows Max and Mia pointing at the star guiding their way, warm determination"),
    ("Max and Mia: 'And often through my curtains peep' — the star peeks through a bedroom window", "The star peeks through a cozy bedroom curtain, Max and Mia inside waving hello"),
    ("Max and Mia: 'For you never shut your eye' — star stays awake while world sleeps below", "Time-lapse style motion, world sleeping below while the star watches over Max and Mia"),
    ("Max and Mia: 'Till the sun is in the sky' — sun rises golden as the star waves goodbye", "Beautiful sunrise with Max and Mia watching, the star fading as golden sunlight appears"),
    ("Max and Mia: 'As your bright and tiny spark' — they catch tiny sparks of starlight in jars", "Max and Mia laughing and trying to catch tiny sparks of starlight in magical little jars"),
    ("Max and Mia: 'Lights the traveler in the dark' — the star guides a little lost bunny home", "The star's light guides a small bunny to safety, Max and Mia helping and cheering"),
    ("Max and Mia: 'Though I know not what you are' — they draw pictures of the star together", "Max and Mia sitting with paper and crayons drawing the star, warm cozy scene"),
    ("Max and Mia: 'Twinkle twinkle little star' — final chorus with all friends joining in", "All their animal friends appear joining Max and Mia in singing, big joyful celebration"),
    ("Max and Mia: 'How I wonder what you are?' — the star winks and smiles at them warmly", "The star gains a friendly smiling face and winks at Max and Mia who wave back happily"),
    ("Max and Mia name their star 'Lucky' and promise to visit every night together", "Close-up of Max and Mia making a pinky promise with the glowing star above them"),
    ("Max and Mia watch as their star writes their names across the night sky in light", "The star draws 'MAX & MIA' in glowing light across the dark sky, magical and beautiful"),

    # ACT 3: Triumph (9 Clips)
    ("Max and Mia discover the star is actually their guardian angel watching over them always", "The star glows warmly and sends a beam of light hugging Max and Mia from above"),
    ("All the stars in the sky twinkle together in a beautiful light show for Max and Mia", "Spectacular starlight display with all stars twinkling, Max and Mia watching in amazement"),
    ("Max holds a golden star trophy and Mia cheers — they learned about the magical night sky!", "Max proudly holds a golden star trophy, Mia beside him clapping, warm celebration"),
    ("A beautiful aurora rainbow of colors fills the sky above Max and Mia as a reward", "Stunning colorful aurora fills the sky, Max and Mia bathed in magical rainbow light below"),
    ("Max and Mia do their star dance — spinning with arms wide, starlight swirling around them", "Energetic spinning dance with starlight swirling around Max and Mia, pure magical joy"),
    ("Mia hugs Max warmly under their favorite twinkling star — best friends forever", "Gentle warm close-up, Mia hugging Max, their star twinkling above them, golden warmth"),
    ("Max and Mia wave goodbye holding little lanterns that look like their favorite star", "Max and Mia walking home holding glowing star-shaped lanterns, waving back at camera"),
    ("Magical stardust fills the screen as their star sends them off to sweet dreams", "Golden stardust sparkles fill the frame, Max and Mia drifting off to sleep peacefully"),
    ("Max and Mia give thumbs up to you — YOU can find YOUR star too! Goodnight!", "Max and Mia both giving big thumbs up to the camera, huge warm smiles, magical ending"),
]


def build_clips():
    clips = []
    for i, (scene_desc, motion_prompt) in enumerate(STORYBOARD):
        img_prompt = f"{scene_desc}. {CHAR_PROMPT}"
        clips.append({
            "idx": i + 1,
            "scene_desc": scene_desc,
            "image_prompt": img_prompt,
            "motion_prompt": motion_prompt,
            "img_url": None,
            "vid_url": None,
            "local_img": None,
            "local_vid": None,
            "status": "pending",
        })
    return clips


def save_jobs(clips):
    JOBS_FILE.write_text(json.dumps(clips, indent=2, ensure_ascii=False), encoding="utf-8")


def load_jobs():
    if JOBS_FILE.exists():
        return json.loads(JOBS_FILE.read_text(encoding="utf-8"))
    return None


def run_pipeline():
    log.info("=" * 60)
    log.info("Twinkle Twinkle Little Star — Pipeline gestartet")
    log.info("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CLIPS_DIR.mkdir(parents=True, exist_ok=True)

    # Lade existierende Jobs oder erstelle neue
    clips = load_jobs()
    if clips is None:
        log.info("Erstelle neues Storyboard (36 Clips)")
        clips = build_clips()
        save_jobs(clips)
    else:
        pending = sum(1 for c in clips if c.get("status") == "pending")
        done_img = sum(1 for c in clips if c.get("status") in ("img_done", "vid_done"))
        done_vid = sum(1 for c in clips if c.get("status") == "vid_done")
        log.info(f"Fortsetze: {done_vid} Videos fertig, {done_img-done_vid} Bilder fertig, {pending} ausstehend")

    # Importiere Higgsfield-Cloud
    from src.higgsfield_cloud import generate_image, generate_video

    total = len(clips)

    # Phase 1: Bilder generieren
    log.info(f"\nPhase 1: {total} Bilder generieren...")
    for clip in clips:
        if clip.get("status") in ("img_done", "vid_done"):
            continue
        local_img = CLIPS_DIR / f"img_{clip['idx']:02d}.jpg"
        try:
            log.info(f"  [{clip['idx']:02d}/{total}] {clip['scene_desc'][:60]}")
            img_url = generate_image(clip["image_prompt"], save_path=str(local_img))
            clip["img_url"] = img_url
            clip["local_img"] = str(local_img)
            clip["status"] = "img_done"
            save_jobs(clips)
            time.sleep(2)
        except Exception as e:
            log.error(f"  Bild {clip['idx']} fehlgeschlagen: {e}")
            clip["status"] = f"img_error: {e}"
            save_jobs(clips)

    img_ok = sum(1 for c in clips if c.get("status") in ("img_done", "vid_done"))
    log.info(f"Bilder fertig: {img_ok}/{total}")

    # Phase 2: Videos generieren
    log.info(f"\nPhase 2: {total} Videos animieren...")
    for clip in clips:
        if clip.get("status") == "vid_done":
            continue
        if not clip.get("local_img") or not Path(clip["local_img"]).exists():
            log.warning(f"  [{clip['idx']:02d}] Kein Bild — skip")
            continue
        local_vid = CLIPS_DIR / f"vid_{clip['idx']:02d}.mp4"
        try:
            log.info(f"  [{clip['idx']:02d}/{total}] {clip['scene_desc'][:60]}")
            vid_url = generate_video(
                image_path=clip["local_img"],
                prompt=clip["motion_prompt"],
                save_path=str(local_vid),
            )
            clip["vid_url"] = vid_url
            clip["local_vid"] = str(local_vid)
            clip["status"] = "vid_done"
            save_jobs(clips)
            time.sleep(3)
        except Exception as e:
            log.error(f"  Video {clip['idx']} fehlgeschlagen: {e}")
            clip["status"] = f"vid_error: {e}"
            save_jobs(clips)

    vid_ok = sum(1 for c in clips if c.get("status") == "vid_done")
    log.info(f"Videos fertig: {vid_ok}/{total}")

    if vid_ok < 8:
        log.error(f"Zu wenige Videos ({vid_ok}) — Abbruch")
        return

    # Phase 3: ffmpeg Assembly
    log.info("\nPhase 3: Video zusammenbauen...")
    done_vids = [c for c in clips if c.get("status") == "vid_done"]
    # Auf 36 auffuellen wenn noetig
    while len(done_vids) < 36:
        done_vids += done_vids[:36 - len(done_vids)]

    concat_file = OUTPUT_DIR / "concat.txt"
    with open(concat_file, "w") as f:
        for c in done_vids[:36]:
            f.write(f"file '{c['local_vid']}'\n")

    # Musik suchen
    music_candidates = list((ROOT / "music").glob("*twinkle*.mp3")) + \
                       list((ROOT / "music").glob("*.mp3"))
    music_file = music_candidates[0] if music_candidates else None
    if music_file:
        log.info(f"Musik: {music_file.name}")
    else:
        log.warning("Keine Musik gefunden — Video ohne Audio")

    output_main = OUTPUT_DIR / "twinkle_twinkle_FINAL.mp4"
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file)]
    if music_file:
        cmd += ["-i", str(music_file), "-c:v", "libx264", "-c:a", "aac",
                "-shortest", "-map", "0:v:0", "-map", "1:a:0"]
    else:
        cmd += ["-c:v", "libx264", "-an"]
    cmd += ["-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2",
            str(output_main)]

    subprocess.run(cmd, check=True)
    log.info(f"Hauptvideo: {output_main}")

    # Shorts (3x 60s)
    shorts_dir = OUTPUT_DIR / "shorts"
    shorts_dir.mkdir(exist_ok=True)
    for i, start in enumerate([0, 60, 120]):
        short_out = shorts_dir / f"twinkle_SHORT_part{i+1}.mp4"
        subprocess.run([
            "ffmpeg", "-y", "-i", str(output_main),
            "-ss", str(start), "-t", "60",
            "-vf", "crop=ih*9/16:ih,scale=1080:1920",
            "-c:v", "libx264", "-c:a", "aac", str(short_out)
        ], check=True)
        log.info(f"Short {i+1}: {short_out}")

    # Phase 4: YouTube Upload
    log.info("\nPhase 4: YouTube Upload...")
    sys.path.insert(0, str(ROOT / "youtube"))
    from youtube.upload import upload_video

    THUMBNAIL = ROOT / "output" / "baa-baa-black-sheep" / "thumbnail_correct.jpg"
    TAGS = ["Twinkle Twinkle Little Star", "nursery rhyme", "kids music",
            "Max and Mia", "toddler", "preschool", "children's songs",
            "animated", "stars", "bedtime song", "3D animation"]

    # Hauptvideo
    title_main = "Twinkle Twinkle Little Star | Max & Mia World | Nursery Rhyme for Kids"
    desc_main = """Twinkle Twinkle Little Star with Max & Mia!

Join Max and Mia as they discover the magical world of stars!
Watch as their favorite star twinkles just for them!

Perfect for toddlers and preschoolers!
Original animation by Max & Mia World

#TwinkleTwinkle #NurseryRhyme #KidsMusic #MaxAndMia #KidsSongs #ToddlerLearning"""

    try:
        vid_id = upload_video(
            video_path=str(output_main),
            title=title_main,
            description=desc_main,
            tags=TAGS,
            category_id="27",
            privacy="public",
            thumbnail_path=str(THUMBNAIL) if THUMBNAIL.exists() else None,
        )
        log.info(f"Hauptvideo live: https://www.youtube.com/watch?v={vid_id}")
    except Exception as e:
        log.error(f"YouTube Hauptvideo fehlgeschlagen: {e}")

    # Shorts
    for i in range(1, 4):
        short_file = shorts_dir / f"twinkle_SHORT_part{i}.mp4"
        if not short_file.exists():
            continue
        try:
            short_id = upload_video(
                video_path=str(short_file),
                title=f"Twinkle Twinkle Little Star Part {i} #Shorts | Max & Mia",
                description=f"Twinkle Twinkle Little Star Part {i} with Max & Mia!\n\n#TwinkleTwinkle #Shorts #NurseryRhyme #KidsMusic #MaxAndMia",
                tags=TAGS + ["Shorts"],
                category_id="27",
                privacy="public",
                thumbnail_path=str(THUMBNAIL) if THUMBNAIL.exists() else None,
            )
            log.info(f"Short {i} live: https://www.youtube.com/shorts/{short_id}")
        except Exception as e:
            log.error(f"Short {i} Upload fehlgeschlagen: {e}")

    log.info("\n" + "=" * 60)
    log.info("Pipeline abgeschlossen!")
    log.info(f"  Videos fertig: {vid_ok}/36")
    log.info("=" * 60)


if __name__ == "__main__":
    run_pipeline()
