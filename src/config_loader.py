from __future__ import annotations
import os
from pathlib import Path
from typing import Any
import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent

def load_env() -> None:
    load_dotenv(ROOT / ".env")

def load_yaml(name: str) -> dict[str, Any]:
    with open(ROOT / "config" / name, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def env(key: str, default: str | None = None) -> str | None:
    val = os.getenv(key, default)
    return val if val not in ("", None) else default

def env_bool(key: str, default: bool = False) -> bool:
    val = os.getenv(key)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")

def output_dir() -> Path:
    p = ROOT / env("OUTPUT_DIR", "output")
    p.mkdir(parents=True, exist_ok=True)
    return p
