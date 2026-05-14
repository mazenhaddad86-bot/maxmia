"""Persistent state — welches Theme war zuletzt dran (round-robin)."""
from __future__ import annotations
import json
from pathlib import Path
from .config_loader import ROOT

STATE_FILE = ROOT / "state.json"

def load() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"last_theme_index": -1, "history": []}

def save(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
