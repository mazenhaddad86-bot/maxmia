"""
Lokale API Server fuer n8n
n8n ruft diese Endpoints auf statt executeCommand
"""
from flask import Flask, request, jsonify
import subprocess, os, json, glob

app = Flask(__name__)
PYTHON = r"C:\Users\myshi\AppData\Local\Python\bin\python.exe"
BASE = r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids"

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/build-video", methods=["POST"])
def build_video():
    data = request.json
    theme = data.get("theme", "humpty-dumpty").replace(" ", "_").lower()
    music = data.get("music_path", "")

    # Suche nach Ausgabe-Ordner fuer dieses Theme
    theme_dir = os.path.join(BASE, "output", theme)
    os.makedirs(theme_dir, exist_ok=True)

    # Suche nach concat.txt (versuche verschiedene Namen)
    concat = None
    for name in ["concat_v3.txt", "concat_story.txt", "concat.txt"]:
        candidate = os.path.join(theme_dir, name)
        if os.path.exists(candidate):
            concat = candidate
            break

    # Falls kein concat.txt vorhanden, erstelle es aus allen normalisierten Clips
    if concat is None:
        clips_dirs = [
            os.path.join(theme_dir, "new_clips_norm"),
            os.path.join(theme_dir, "clips_norm"),
            theme_dir
        ]
        clips = []
        for d in clips_dirs:
            if os.path.isdir(d):
                found = sorted(glob.glob(os.path.join(d, "*.mp4")))
                clips.extend(found)

        if not clips:
            return jsonify({"error": f"Keine Clips gefunden in {theme_dir}"}), 400

        concat = os.path.join(theme_dir, "concat_auto.txt")
        lines = [f"file '{c}'" for c in clips]
        with open(concat, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    noaudio = os.path.join(theme_dir, f"{theme}_noaudio.mp4")
    final = os.path.join(theme_dir, f"{theme}_FINAL.mp4")

    # Step 1: concat clips
    r1 = subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat, "-c", "copy", noaudio],
        capture_output=True, text=True
    )
    if r1.returncode != 0:
        return jsonify({"error": "ffmpeg concat: " + r1.stderr[-800:]}), 500

    # Step 2: add music (falls music angegeben)
    if music and os.path.exists(music):
        r2 = subprocess.run(
            ["ffmpeg", "-y", "-i", noaudio, "-i", music,
             "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
             "-b:a", "192k", "-shortest", final],
            capture_output=True, text=True
        )
        if r2.returncode != 0:
            return jsonify({"error": "ffmpeg audio: " + r2.stderr[-800:]}), 500
    else:
        # Kein Audio vorhanden - Video ohne Ton
        final = noaudio

    return jsonify({"success": True, "video_path": final})


@app.route("/youtube-upload", methods=["POST"])
def youtube_upload():
    data = request.json
    video = data.get("video_path", "")
    title = data.get("title", "Max und Mia World")
    description = data.get("description",
        "Nursery Rhymes fuer Kinder | Max & Mia World\n\n"
        "#NurseryRhymes #KidsMusic #MaxMiaWorld #Kinderlieder"
    )
    tags = data.get("tags", "nursery rhyme,kids,children,Max und Mia,Kinderlieder")

    if not os.path.exists(video):
        return jsonify({"error": f"Video nicht gefunden: {video}"}), 400

    script = os.path.join(BASE, "youtube", "upload.py")
    r = subprocess.run(
        [PYTHON, script, "--video", video, "--title", title,
         "--description", description, "--tags", tags],
        capture_output=True, text=True, cwd=os.path.join(BASE, "youtube")
    )
    if r.returncode != 0:
        return jsonify({"error": r.stderr[-800:], "stdout": r.stdout[-400:]}), 500

    # Extract video ID from output
    output = r.stdout
    video_id = ""
    for line in output.split("\n"):
        if "youtube.com/watch?v=" in line or "Video ID:" in line:
            if "v=" in line:
                video_id = line.split("v=")[-1].strip()
            else:
                video_id = line.split(":")[-1].strip()

    return jsonify({"success": True, "video_id": video_id, "output": output})


@app.route("/save-mp3", methods=["POST"])
def save_mp3():
    data = request.json
    audio_url = data.get("audio_url", "")
    theme = data.get("theme", "song").replace(" ", "_")

    import urllib.request
    out_path = os.path.join(BASE, "music", f"{theme}_auto.mp3")
    urllib.request.urlretrieve(audio_url, out_path)
    return jsonify({"success": True, "path": out_path})


@app.route("/normalize-clips", methods=["POST"])
def normalize_clips():
    """Normalisiert alle Clips in einem Ordner auf 1280x720 H.264"""
    data = request.json
    theme = data.get("theme", "").replace(" ", "_").lower()
    input_dir = data.get("input_dir", "")

    if not input_dir:
        input_dir = os.path.join(BASE, "output", theme, "clips_raw")

    if not os.path.isdir(input_dir):
        return jsonify({"error": f"Ordner nicht gefunden: {input_dir}"}), 400

    out_dir = os.path.join(BASE, "output", theme, "clips_norm")
    os.makedirs(out_dir, exist_ok=True)

    clips = glob.glob(os.path.join(input_dir, "*.mp4"))
    results = []
    for clip in clips:
        basename = os.path.basename(clip)
        outfile = os.path.join(out_dir, basename)
        r = subprocess.run([
            "ffmpeg", "-y", "-i", clip, "-an",
            "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=24",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23", outfile
        ], capture_output=True, text=True)
        results.append({"file": basename, "ok": r.returncode == 0})

    return jsonify({"success": True, "processed": len(results), "results": results})


if __name__ == "__main__":
    print("API Server laeuft auf http://localhost:8765")
    app.run(host="0.0.0.0", port=8765, debug=False)
