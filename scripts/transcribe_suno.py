"""
transcribe_suno.py — Extract real lyrics from Suno MP3s using faster-whisper.

Usage:
    python scripts/transcribe_suno.py <path-to-mp3>
    python scripts/transcribe_suno.py --all   # all 6 ready songs
"""
import sys
from pathlib import Path
from faster_whisper import WhisperModel

PROJECT = Path(__file__).resolve().parent.parent

READY_SONGS = [
    PROJECT / "output/wheels/suno/wheels_pep_16b83b57.mp3",
    PROJECT / "output/twinkle/twinkle_lullaby_ac051e17.mp3",
    PROJECT / "output/oldmacdonald/oldmac_2c1ea1ba.mp3",
    PROJECT / "output/babyshark/bs_93eec1c5.mp3",
    PROJECT / "output/hickory/hickory_a721f2e7.mp3",
    PROJECT / "output/row/row_v55_136d4cff.mp3",
]


def transcribe(mp3: Path, model: WhisperModel):
    print(f"\n=== {mp3.name} ===")
    segments, info = model.transcribe(
        str(mp3), beam_size=5, language="en",
        vad_filter=False, condition_on_previous_text=False,
    )
    lines = []
    for seg in segments:
        line = f"[{seg.start:6.2f} -> {seg.end:6.2f}] {seg.text.strip()}"
        print(line)
        lines.append(line)
    out_txt = mp3.with_suffix(".lyrics.txt")
    out_txt.write_text("\n".join(lines), encoding="utf-8")
    print(f"  -> {out_txt}")


def main():
    if len(sys.argv) < 2:
        print("Usage: transcribe_suno.py <mp3|--all>")
        return
    print("Loading whisper model (small, CPU)...")
    model = WhisperModel("small", device="cpu", compute_type="int8")
    targets = READY_SONGS if sys.argv[1] == "--all" else [Path(sys.argv[1])]
    for mp3 in targets:
        if not mp3.exists():
            print(f"SKIP (missing): {mp3}")
            continue
        try:
            transcribe(mp3, model)
        except Exception as e:
            print(f"FAILED {mp3.name}: {e}")


if __name__ == "__main__":
    main()
