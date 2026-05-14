"""Wählt ein Theme aus themes.yaml aus (round-robin / random / ai)."""
from __future__ import annotations
import random
from typing import Any
from . import state, config_loader

def pick_theme(themes_cfg: dict[str, Any]) -> dict[str, Any]:
    strategy = themes_cfg.get("strategy", "round_robin")
    themes = themes_cfg["themes"]
    s = state.load()

    if strategy == "random":
        idx = random.randrange(len(themes))
    elif strategy == "ai":
        # Optional: OpenAI generiert neues Theme on-the-fly
        return _ai_theme(themes_cfg)
    else:  # round_robin
        idx = (s["last_theme_index"] + 1) % len(themes)

    s["last_theme_index"] = idx
    state.save(s)
    return dict(themes[idx])

def _ai_theme(themes_cfg: dict[str, Any]) -> dict[str, Any]:
    import json
    from openai import OpenAI
    api_key = config_loader.env("OPENAI_API_KEY")
    if not api_key:
        # Fallback: round-robin
        return pick_theme({**themes_cfg, "strategy": "round_robin"})
    client = OpenAI(api_key=api_key)
    niche = themes_cfg.get("niche", "general")
    style = themes_cfg.get("brand_style", "")
    sys = (
        "Du erstellst Short-Form-Video Konzepte. "
        "Antworte AUSSCHLIESSLICH als kompaktes JSON mit Feldern: "
        "id, hook, image_prompt, motion_prompt, music_prompt."
    )
    user = f"Niche: {niche}\nBrand-Stil: {style}\nErstelle ein neues Konzept."
    resp = client.chat.completions.create(
        model=config_loader.env("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[{"role": "system", "content": sys}, {"role": "user", "content": user}],
        response_format={"type": "json_object"},
    )
    return json.loads(resp.choices[0].message.content)
