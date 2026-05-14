"""Findet die erfolgreichsten Kids-Videos auf YouTube und analysiert sie.

Aufruf:
    python scripts/analyze_competitors.py
    python scripts/analyze_competitors.py --query "nursery rhyme" --max 20
    python scripts/analyze_competitors.py --channel "Dave and Ava"
"""
from __future__ import annotations
import argparse, json, os, sys
from pathlib import Path

# .env laden
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from src import config_loader
config_loader.load_env()

from googleapiclient.discovery import build


QUERIES = [
    "kids nursery rhyme 2024",
    "children's songs ABC",
    "toddler learning song",
    "baby cartoon song",
    "Leo Mia kids",
    "Dave and Ava",
    "Choo Choo TV",
    "CoComelon nursery rhyme",
]


def youtube_client():
    key = os.environ.get("YOUTUBE_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        # Fallback: aus client_secrets.json
        secrets_file = ROOT / "scripts" / "client_secrets.json"
        if secrets_file.exists():
            data = json.loads(secrets_file.read_text())
            key = (data.get("installed") or data.get("web") or {}).get("api_key")
    if not key:
        raise SystemExit(
            "Kein YouTube API Key gefunden.\n"
            "Füge YOUTUBE_API_KEY=... in .env ein (Data API v3 Key aus Google Cloud Console)."
        )
    return build("youtube", "v3", developerKey=key)


def search_videos(yt, query: str, max_results: int = 10) -> list[dict]:
    resp = yt.search().list(
        q=query,
        part="id,snippet",
        type="video",
        order="viewCount",
        videoCategoryId="10",   # Music
        maxResults=max_results,
        relevanceLanguage="en",
    ).execute()

    ids = [item["id"]["videoId"] for item in resp.get("items", [])]
    if not ids:
        return []

    stats_resp = yt.videos().list(
        id=",".join(ids),
        part="statistics,contentDetails,snippet",
    ).execute()

    results = []
    for item in stats_resp.get("items", []):
        snip = item["snippet"]
        stats = item.get("statistics", {})
        details = item.get("contentDetails", {})
        results.append({
            "title": snip["title"],
            "channel": snip["channelTitle"],
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)),
            "duration": details.get("duration", ""),
            "published": snip["publishedAt"][:10],
            "url": f"https://youtube.com/watch?v={item['id']}",
            "thumbnail": snip["thumbnails"].get("high", {}).get("url", ""),
            "description": snip.get("description", "")[:200],
        })

    results.sort(key=lambda x: x["views"], reverse=True)
    return results


def format_views(n: int) -> str:
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.0f}K"
    return str(n)


def analyze_with_claude(videos: list[dict]) -> str:
    """Analysiert die Videos mit Claude und gibt Empfehlungen."""
    try:
        import anthropic
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            return ""
        client = anthropic.Anthropic(api_key=key)

        top = videos[:15]
        video_list = "\n".join(
            f"- '{v['title']}' ({format_views(v['views'])} Views) — {v['channel']}"
            for v in top
        )

        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=800,
            messages=[{
                "role": "user",
                "content": f"""Analysiere diese erfolgreichen Kids YouTube Videos und gib mir:
1. Die 5 häufigsten Themen/Patterns die funktionieren
2. Was bei den Titeln auffällt (Keywords, Struktur)
3. Welche 3 konkreten Video-Ideen ich für meine Charaktere Leo (Junge) und Mia (Mädchen) ableiten kann

Videos:
{video_list}

Antworte auf Deutsch, kurz und actionable."""
            }]
        )
        return "\n\n--- Claude-Analyse ---\n" + msg.content[0].text
    except Exception as e:
        return f"\n(Claude-Analyse übersprungen: {e})"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default=None, help="Eigene Suchanfrage")
    parser.add_argument("--max", type=int, default=10)
    parser.add_argument("--channel", default=None, help="Bestimmten Kanal analysieren")
    args = parser.parse_args()

    yt = youtube_client()
    all_videos: list[dict] = []

    queries = [args.query] if args.query else (
        [f"channel:{args.channel}"] if args.channel else QUERIES[:4]
    )

    for q in queries:
        print(f"Suche: {q!r} ...")
        videos = search_videos(yt, q, max_results=args.max)
        all_videos.extend(videos)
        for v in videos[:3]:
            print(f"  {format_views(v['views']):>6}  {v['title'][:60]}")

    # Deduplizieren und sortieren
    seen = set()
    unique = []
    for v in sorted(all_videos, key=lambda x: x["views"], reverse=True):
        if v["url"] not in seen:
            seen.add(v["url"])
            unique.append(v)

    top20 = unique[:20]

    print(f"\n{'='*60}")
    print(f"TOP {len(top20)} KIDS VIDEOS")
    print(f"{'='*60}\n")

    for i, v in enumerate(top20, 1):
        print(f"{i:2}. {format_views(v['views']):>6} Views — {v['title'][:55]}")
        print(f"    Kanal: {v['channel']}  |  {v['published']}  |  {v['url']}")
        print()

    # Claude-Analyse (falls API Key vorhanden)
    analysis = analyze_with_claude(top20)
    if analysis:
        print(analysis)

    # Als JSON speichern
    out_file = ROOT / "output" / "competitor_analysis.json"
    out_file.parent.mkdir(exist_ok=True)
    out_file.write_text(json.dumps(top20, indent=2, ensure_ascii=False))
    print(f"\nGespeichert: {out_file}")


if __name__ == "__main__":
    main()
