"""Smart Image Router — Priorität: Browser Unlimited (gratis) → CLI (Credits).

Reihenfolge:
1. Higgsfield Browser (Chrome Canary, Unlimited-Toggle = GRATIS)
2. Higgsfield CLI (Nano Banana 2, 2 Credits/Bild — Fallback)
"""
from __future__ import annotations
import logging

log = logging.getLogger("image_router")


def generate_image(prompt: str, aspect_ratio: str = "16:9") -> str:
    """Generiert Bild: erst Browser (gratis), dann CLI (Credits)."""
    from . import browser_higgsfield, higgsfield_client

    if browser_higgsfield.is_available():
        try:
            log.info("Image via Browser (Unlimited, gratis)...")
            return browser_higgsfield.generate_image(prompt, aspect_ratio)
        except Exception as e:
            log.warning("Browser-Generation fehlgeschlagen (%s) — fallback auf CLI", e)

    log.info("Image via CLI (Nano Banana 2, 2 Credits)...")
    return higgsfield_client.generate_image(prompt=prompt, aspect_ratio=aspect_ratio)

