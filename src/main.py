"""Orchestrator — 3-5 Min Kinderlied Video Pipeline.

Aufruf:
    python -m src.main
    python -m src.main --theme choo-choo-train
    python -m src.main --dry-run
"""
from __future__ import annotations
import argparse, logging, sys, time
from datetime import datetime
from pathlib import Path
from . import config_loader, higgsfield_client, suno_client
from .compose import full_pipeline
from .lyrics import parse_lyrics, set_scene_durations
from .prompt_builder import assign_prompts
from .upload import youtube as yt_upload, tiktok as tt_upload
from .upload import instagram as ig_upload, facebook as fb_upload

log = logging.getLogger("pipeline")

def setup_logging():
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    try:
        handlers.append(logging.FileHandler(config_loader.ROOT / "pipeline.log", encoding="utf-8"))
    except PermissionError:
        pass  # log-Datei durch bat-Redirect gesperrt — nur stdout
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=handlers,
    )

def run_once(theme_id: str | None, dry_run: bool):
    config_loader.load_env()
    themes_cfg = config_loader.load_yaml("themes.yaml")
    settings = config_loader.load_yaml("settings.yaml")

    from . import topics, state as state_mod
    from .theme_generator import get_or_generate_theme

    s = state_mod.load()
    used_ids = set(s.get("used_ids", []))

    if theme_id:
        theme = next((t for t in themes_cfg["themes"] if t["id"] == theme_id), None)
        if not theme:
            raise SystemExit(f"Theme '{theme_id}' nicht gefunden.")
    else:
        # Automatisch: nächstes Theme aus YAML, dann KI-generiert wenn alle durch
        theme = get_or_generate_theme(themes_cfg, used_ids)

    log.info("Theme: %s — %s", theme["id"], theme.get("title", ""))
    used_ids.add(theme["id"])
    s["used_ids"] = list(used_ids)
    state_mod.save(s)

    target_sec = settings.get("video_length_sec", 180)
    lyrics_text = theme.get("lyrics", "")
    if not lyrics_text:
        raise SystemExit("Theme hat keine 'lyrics'.")

    struct = parse_lyrics(lyrics_text, title=theme.get("title", theme["id"]))
    set_scene_durations(struct, target_total_sec=target_sec)
    assign_prompts(struct, style=theme.get("visual_style", ""))
    log.info("Szenen: %d total, %d unique Clips", len(struct.scenes), len(struct.unique_scenes))

    out = config_loader.output_dir() / f"{datetime.now():%Y%m%d_%H%M%S}_{theme['id']}"
    out.mkdir(parents=True, exist_ok=True)
    clips_dir = out / "clips"
    clips_dir.mkdir(exist_ok=True)

    # 1. Audio
    log.info("Suno: Song mit Vocals (%ds) …", target_sec)
    audio_url = suno_client.generate_audio(
        prompt=theme.get("music_style", ""),
        lyrics=lyrics_text,
        style=theme.get("suno_style", "children's nursery rhyme, playful, fun, upbeat, sing along"),
        title=theme.get("title", theme["id"]),
        instrumental=False,
        duration_target=target_sec,
    )
    audio_file = suno_client.download(audio_url, out / "audio.mp3")
    log.info("  Audio: %s", audio_file)

    # 2. Bilder (Nano Banana Pro — FREE UNLIMITED) + Videos (VEO 3 — Credits)
    clip_cache: dict[str, Path] = {}
    for key, scene in struct.unique_scenes.items():
        log.info("Szene '%s': Bild (Nano Banana Pro, gratis) …", key)
        img_url = higgsfield_client.generate_image(prompt=scene.image_prompt, aspect_ratio="16:9")
        higgsfield_client.download(img_url, clips_dir / f"{key}.jpg")

        log.info("Szene '%s': Video (VEO 3.1, %ds) …", key, scene.duration_sec)
        vid_url = higgsfield_client.generate_video(
            image_url=img_url,
            motion_prompt=scene.motion_prompt,
            duration_sec=scene.duration_sec,
        )
        vid_file = higgsfield_client.download(vid_url, clips_dir / f"{key}.mp4")
        clip_cache[key] = vid_file

    # 3. Clip-Sequenz + Timing für Captions
    clip_sequence = [clip_cache[s.key] for s in struct.scenes]
    t = 0.0
    scenes_timing = []
    for scene in struct.scenes:
        scenes_timing.append({"lyrics": scene.lyrics, "start_sec": t, "duration_sec": scene.duration_sec})
        t += scene.duration_sec

    # 4. Compose — produziert 16:9 UND 9:16 gleichzeitig
    log.info("ffmpeg: Concat + Audio + Captions + Vertical Crop …")
    landscape, vertical = full_pipeline(clip_sequence, audio_file, out, scenes_with_timing=scenes_timing)
    log.info("  16:9 (YouTube):  %s", landscape)
    log.info("  9:16 (Shorts):   %s", vertical)

    if dry_run:
        log.info("Dry-Run aktiv — kein Upload.")
        return

    # 5. Uploads
    title = theme.get("title", "Kids Nursery Rhyme")
    caption = theme.get("caption", title)
    tags = themes_cfg.get("hashtags", []) + theme.get("extra_tags", [])
    cooldown = settings["limits"].get("cooldown_seconds_between_uploads", 90)
    pub = settings["publish_to"]

    def _upload(name: str, fn):
        try:
            url = fn()
            log.info("%s: %s", name, url)
        except Exception as e:
            log.exception("%s fehlgeschlagen: %s", name, e)
        time.sleep(cooldown)

    # YouTube 16:9 (normales Video, 3-5 Min)
    if pub.get("youtube_landscape") and config_loader.env_bool("YOUTUBE_ENABLED"):
        _upload("YouTube 16:9", lambda: yt_upload.upload(landscape, title, caption, tags))

    # YouTube Shorts 9:16
    if pub.get("youtube_shorts") and config_loader.env_bool("YOUTUBE_ENABLED"):
        shorts_title = f"{title} #Shorts"
        _upload("YouTube Shorts", lambda: yt_upload.upload(vertical, shorts_title, caption, tags))

    # TikTok 9:16
    if pub.get("tiktok") and config_loader.env_bool("TIKTOK_ENABLED"):
        _upload("TikTok", lambda: tt_upload.upload(vertical, title, caption, tags))

    # Instagram Reels 9:16
    if pub.get("instagram_reels") and config_loader.env_bool("INSTAGRAM_ENABLED"):
        public_url = config_loader.env("PUBLIC_VIDEO_URL")
        if public_url:
            _upload("Instagram Reels", lambda: ig_upload.upload(vertical, public_url, caption))
        else:
            log.warning("Instagram: PUBLIC_VIDEO_URL fehlt — Skip. Siehe README.")

def main():
    setup_logging()
    p = argparse.ArgumentParser()
    p.add_argument("--theme")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    run_once(args.theme, args.dry_run)

if __name__ == "__main__":
    main()
