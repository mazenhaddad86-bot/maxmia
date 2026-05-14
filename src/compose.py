"""ffmpeg: Multi-Clip Concatenation + Audio + Captions → fertiges Video."""
from __future__ import annotations
import shutil
import subprocess
import tempfile
from pathlib import Path

def _ffmpeg() -> str:
    # Zuerst in PATH suchen
    exe = shutil.which("ffmpeg")
    if not exe:
        # WinGet-Fallback (Windows)
        for candidate in [
            r"C:\Program Files\WinGet\Links\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        ]:
            if Path(candidate).exists():
                return candidate
        raise RuntimeError("ffmpeg nicht gefunden. Installiere: winget install Gyan.FFmpeg")
    return exe

def _run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg error:\n{proc.stderr[-3000:]}")

def concatenate_clips(clip_paths: list[Path], out: Path) -> Path:
    ffmpeg = _ffmpeg()
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
        for p in clip_paths:
            f.write(f"file '{str(p).replace(chr(92), '/')}'\n")
        list_file = Path(f.name)
    _run([ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(out)])
    list_file.unlink(missing_ok=True)
    return out

def add_audio(video: Path, audio: Path, out: Path) -> Path:
    ffmpeg = _ffmpeg()
    out.parent.mkdir(parents=True, exist_ok=True)
    _run([
        ffmpeg, "-y",
        "-stream_loop", "-1", "-i", str(video),
        "-i", str(audio),
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart",
        str(out),
    ])
    return out

def add_captions(video: Path, scenes: list, out: Path) -> Path:
    ffmpeg = _ffmpeg()
    out.parent.mkdir(parents=True, exist_ok=True)
    filters = []
    for s in scenes:
        if not s.get("lyrics"):
            continue
        text = s["lyrics"][:80].replace("'", r"\'").replace(":", r"\:").replace("\n", " ")
        start = s["start_sec"]
        end = start + s["duration_sec"]
        filters.append(
            f"drawtext=text='{text}':fontcolor=white:fontsize=52:"
            f"box=1:boxcolor=black@0.5:boxborderw=12:"
            f"x=(w-text_w)/2:y=h*0.82:enable='between(t,{start},{end})'"
        )
    if not filters:
        return video
    _run([
        ffmpeg, "-y", "-i", str(video),
        "-vf", ",".join(filters),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "copy", str(out),
    ])
    return out

def crop_to_vertical(video: Path, out: Path) -> Path:
    """16:9 → 9:16 center-crop für YouTube Shorts / Instagram Reels.
    Kein extra Higgsfield-Call nötig — reines ffmpeg in-place Crop.
    Ziel: 720x1280 (720p vertikal).
    """
    ffmpeg = _ffmpeg()
    out.parent.mkdir(parents=True, exist_ok=True)
    # crop=w:h:x:y — nimmt mittlere 9/16 Spalte aus dem 16:9 Frame
    _run([
        ffmpeg, "-y", "-i", str(video),
        "-vf", "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=720:1280",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(out),
    ])
    return out

def full_pipeline(
    clip_sequence: list[Path],
    audio: Path,
    out_dir: Path,
    scenes_with_timing: list | None = None,
) -> tuple[Path, Path]:
    """Gibt (landscape_16x9.mp4, vertical_9x16.mp4) zurück."""
    out_dir.mkdir(parents=True, exist_ok=True)

    concat = out_dir / "concat.mp4"
    concatenate_clips(clip_sequence, concat)

    with_audio = out_dir / "with_audio.mp4"
    add_audio(concat, audio, with_audio)

    landscape = out_dir / "final_16x9.mp4"
    if scenes_with_timing:
        add_captions(with_audio, scenes_with_timing, landscape)
    else:
        with_audio.rename(landscape)

    vertical = out_dir / "final_9x16.mp4"
    crop_to_vertical(landscape, vertical)

    return landscape, vertical
