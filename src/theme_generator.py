"""Automatischer Theme-Generator via Claude API.

Erfindet täglich neue Kinderlied-Ideen inkl. vollständiger Lyrics,
Visual Style, Suno-Style und Lerninhalt — kein manuelles Schreiben nötig.
"""
from __future__ import annotations
import json
import random
import logging
from pathlib import Path
import anthropic
from . import config_loader

log = logging.getLogger("theme_generator")

# Kategorien für automatische Rotation — Leo & Mia erkunden die Welt
TOPIC_POOLS = {
    "learning":  ["numbers 1-20", "letters A-Z", "colors", "shapes", "body parts",
                  "days of the week", "months", "seasons", "opposites", "sizes"],
    "nature":    ["rain and rainbows", "the ocean", "butterflies", "the forest",
                  "flowers", "the sun and moon", "stars", "snow", "the wind"],
    "animals":   ["jungle animals", "farm animals", "ocean animals", "baby animals",
                  "birds", "insects", "dinosaurs", "zoo animals", "pets"],
    "values":    ["sharing toys", "saying sorry", "being brave", "helping mama",
                  "listening to papa", "being kind", "cleaning up", "good manners"],
    "adventure": ["going to the beach", "a trip to the zoo", "camping in the forest",
                  "riding a bicycle", "baking with mama", "gardening with papa"],
    "bedtime":   ["goodnight song", "counting sheep", "the moon and stars",
                  "sweet dreams", "pajama time", "teddy bear lullaby"],
}


def _pick_topic() -> tuple[str, str]:
    """Wählt zufällig Kategorie + spezifisches Topic."""
    category = random.choice(list(TOPIC_POOLS.keys()))
    topic = random.choice(TOPIC_POOLS[category])
    return category, topic


def generate_theme(topic: str | None = None) -> dict:
    """Generiert ein komplettes Theme-Dict via Claude API."""
    if topic is None:
        _, topic = _pick_topic()

    client = anthropic.Anthropic(api_key=config_loader.env("ANTHROPIC_API_KEY"))

    prompt = f"""You are creating a children's nursery rhyme theme for a YouTube kids channel.
Characters: Leo (boy, 3 years old) and Mia (girl, 3 years old) — Pixar-style 3D animated.
Content rules: family-friendly, educational, respectful to parents, traditional values, NO inappropriate content.

Topic: "{topic}"

Generate a complete theme as valid JSON with these exact fields:
{{
  "id": "slug-with-dashes",
  "title": "Catchy Title with Leo and Mia",
  "caption": "YouTube caption under 200 chars",
  "extra_tags": ["#tag1", "#tag2", "#tag3"],
  "visual_style": "description of visual setting for this theme (30 words max)",
  "suno_style": "music style description for Suno AI (20 words max)",
  "music_style": "brief music style (10 words max)",
  "learn_element": "what kids learn (15 words max)",
  "lyrics": "full song lyrics with [Intro] [Verse 1] [Chorus] [Verse 2] [Chorus] [Bridge] [Verse 3] [Chorus] [Outro] sections, 3-4 minutes worth, educational and fun"
}}

Rules for lyrics:
- Include the learning element naturally (count numbers, name colors, spell words, etc.)
- Leo and Mia interact with each other and the viewer
- [Bridge] section: Leo or Mia asks the viewer an interactive question
- Cheerful, rhyming, easy to sing along
- Never rude to parents or adults
- Return ONLY the JSON, no other text."""

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()
    # Entferne eventuellen Markdown-Code-Block
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    theme = json.loads(text.strip())
    log.info("Theme generiert: %s — %s", theme["id"], theme["title"])
    return theme


def get_or_generate_theme(themes_cfg: dict, used_ids: set) -> dict:
    """Gibt das nächste Theme zurück. Generiert automatisch neues wenn alle benutzt."""
    available = [t for t in themes_cfg.get("themes", []) if t["id"] not in used_ids]

    if available:
        # Noch nicht benutzte Themes aus themes.yaml
        return available[0]

    # Alle statischen Themes benutzt → KI generiert neues
    log.info("Alle statischen Themes benutzt — generiere neues via Claude AI...")
    return generate_theme()
