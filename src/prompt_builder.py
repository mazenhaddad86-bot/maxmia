"""Baut Higgsfield-Bild/Video-Prompts für jede Szene auf Basis der Lyrics."""
from __future__ import annotations
from .lyrics import Scene, SongStructure

# ── Charaktere — IMMER gleich, CI-konsistent ─────────────────────────────
# FINAL APPROVED DESIGN (user confirmed from Higgsfield reference image):
# Max = Junge: braune lockige Haare, braune Augen, Sommersprossen,
#              blauer Strickpullover unter brauner Cord-Latzhose mit Dino-Patch,
#              rote Converse Sneakers
# Mia = Mädchen: dunkles Haar in hohen Zöpfen mit ROTEN Schleifen,
#                grüne Augen, Sommersprossen,
#                rosa Kleid mit gelben Sternen, rosa Strumpfhose, rosa Mary-Jane-Schuhe
CHARACTERS = (
    "Max (boy age 3, blue dungaree overalls with dino patch, red sneakers, curly hair) "
    "and Mia (girl age 3, pink star dress, dark pigtails with red bows, Mary Jane shoes), "
    "both fully clothed, family-safe, children's TV animation"
)

# ── Qualitäts-Vorgabe — gelernt aus den besten Szenen (1, 2, 3) ──────────
# Regel: Weniger Elemente = schärfere Qualität. Fokus auf Charaktere im Vordergrund.
QUALITY = (
    "3D Pixar animation, production quality render, professional studio lighting, "
    "sharp focus on characters, characters large in foreground, "
    "simple clean background, vivid saturated colors, soft shadows, "
    "ultra-detailed characters, 16:9 cinematic frame, no blur on characters"
)

# ── Lerninhalt pro Szenentyp ──────────────────────────────────────────────
EDUCATIONAL = {
    "intro":  "showing colorful number 1 and letter A, introducing the topic visually",
    "verse":  "with a visible educational element (colorful letters, numbers, or shapes) in the scene",
    "chorus": "with large colorful letters or numbers visible and prominent in the background",
    "bridge": "showing a question card with '?' symbol, Max pointing curiously, Mia looking thoughtful",
    "outro":  "Max and Mia waving goodbye, colorful stars with the number of things learned today",
}

# ── Bewegungs-Prompts — energetisch aber stabil ──────────────────────────
MOTIONS = {
    "intro":  "slow push-in zoom, Max and Mia wave hello at camera, warm welcoming energy",
    "verse":  "gentle side-to-side camera, Max and Mia act out the lyrics naturally, curious expressions",
    "chorus": "upbeat bounce, both characters clap and jump together, bright light pulses, joyful",
    "bridge": "smooth slow dolly, Max tilts head curiously, Mia points at something, wonder expression",
    "outro":  "slow zoom out, Max and Mia wave goodbye together, sparkles and confetti rain down",
}


def build_image_prompt(scene: Scene, song_title: str, theme_style: str = "") -> str:
    """Baut einen fokussierten Bild-Prompt mit Lerninhalt und Qualitätsvorgaben."""
    # Lyric-Snippet für Kontext (max 80 Zeichen — mehr = unschärfere Ergebnisse)
    snippet = scene.lyrics[:80].replace("\n", " ").strip()
    edu = EDUCATIONAL.get(scene.section_type, EDUCATIONAL["verse"])

    # Theme-spezifische Ergänzung (aus themes.yaml)
    theme_extra = f", {theme_style}" if theme_style else ""

    return (
        f"{CHARACTERS}, {edu}. "
        f"Scene: '{snippet}' from kids nursery rhyme '{song_title}'. "
        f"{QUALITY}{theme_extra}."
    )


def build_motion_prompt(scene: Scene) -> str:
    return MOTIONS.get(scene.section_type, MOTIONS["verse"])


def assign_prompts(struct: SongStructure, style: str = "") -> None:
    for key, scene in struct.unique_scenes.items():
        scene.image_prompt = build_image_prompt(scene, struct.title, style)
        scene.motion_prompt = build_motion_prompt(scene)
