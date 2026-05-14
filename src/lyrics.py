"""Lyrics in strukturierte Szenen aufteilen.

Ein 3-5 Min Kinderlied hat typisch:
  Intro → Verse 1 → Chorus → Verse 2 → Chorus → Bridge → Verse 3 → Chorus → Outro

Jede einzigartige Sektion bekommt ein eigenes Bild + Video-Clip.
Gleiche Sektionen (z.B. alle Choruses) nutzen denselben Clip → spart API-Calls.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field

@dataclass
class Scene:
    section_type: str       # "verse", "chorus", "bridge", "intro", "outro"
    section_num: int        # 1, 2, 3 ...
    key: str                # eindeutiger Key z.B. "chorus" oder "verse_1"
    lyrics: str             # Text dieser Sektion
    image_prompt: str = ""  # wird später befüllt
    motion_prompt: str = "" # wird später befüllt
    duration_sec: int = 8   # Clip-Länge

@dataclass
class SongStructure:
    title: str
    scenes: list[Scene] = field(default_factory=list)
    unique_scenes: dict[str, Scene] = field(default_factory=dict)  # key → Scene

def parse_lyrics(lyrics: str, title: str = "Song") -> SongStructure:
    """Teilt Lyrics-Text in Szenen auf.

    Erwartet Format:
        [Intro]
        Bla bla bla

        [Verse 1]
        Lyrics hier

        [Chorus]
        Refrain hier
    """
    struct = SongStructure(title=title)
    section_pattern = re.compile(r"\[([^\]]+)\]", re.IGNORECASE)
    parts = section_pattern.split(lyrics.strip())

    # parts[0] = vor erstem Label (oft leer), dann abwechselnd Label + Text
    current_label = "intro"
    label_counts: dict[str, int] = {}
    i = 0
    chunks = []

    # Wenn kein Label am Anfang, Text gehört zu Intro
    if parts and parts[0].strip():
        chunks.append(("intro", parts[0].strip()))
    if len(parts) > 1:
        for j in range(1, len(parts), 2):
            label = parts[j].strip().lower()
            text = parts[j + 1].strip() if j + 1 < len(parts) else ""
            if text:
                chunks.append((label, text))

    verse_re = re.compile(r"verse\s*(\d*)", re.I)
    chorus_re = re.compile(r"chorus|refrain|hook", re.I)
    bridge_re = re.compile(r"bridge|pre.?chorus|interlude", re.I)
    outro_re = re.compile(r"outro|ending|end", re.I)
    intro_re = re.compile(r"intro", re.I)

    for raw_label, text in chunks:
        if intro_re.search(raw_label):
            stype = "intro"
        elif outro_re.search(raw_label):
            stype = "outro"
        elif chorus_re.search(raw_label):
            stype = "chorus"
        elif bridge_re.search(raw_label):
            stype = "bridge"
        elif verse_re.search(raw_label):
            stype = "verse"
        else:
            stype = raw_label.split()[0]  # erstes Wort

        label_counts[stype] = label_counts.get(stype, 0) + 1
        num = label_counts[stype]

        # Chorus immer gleicher Key (ein Clip für alle Choruses)
        if stype == "chorus":
            key = "chorus"
        elif stype in ("intro", "outro", "bridge"):
            key = stype
        else:
            key = f"{stype}_{num}"

        scene = Scene(section_type=stype, section_num=num, key=key, lyrics=text)
        struct.scenes.append(scene)
        if key not in struct.unique_scenes:
            struct.unique_scenes[key] = scene

    return struct

def total_duration(struct: SongStructure) -> int:
    return sum(s.duration_sec for s in struct.scenes)

def set_scene_durations(struct: SongStructure, target_total_sec: int) -> None:
    """Passt Clip-Längen an damit Gesamt ≈ target_total_sec."""
    n = len(struct.scenes)
    if n == 0:
        return
    per_scene = max(5, target_total_sec // n)
    per_scene = min(per_scene, 10)  # Higgsfield max 10s
    for scene in struct.scenes:
        scene.duration_sec = per_scene
    # Unique scenes bekommen dieselbe Länge
    for key, scene in struct.unique_scenes.items():
        scene.duration_sec = per_scene
