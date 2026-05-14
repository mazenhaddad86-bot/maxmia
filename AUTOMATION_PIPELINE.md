# Vollautomatischer Video-Pipeline

## Übersicht
```
Google Sheet (Thema) → n8n → Claude (Lyrics) → Suno API (Musik) 
    → Higgsfield (Clips) → ffmpeg (Video) → YouTube Upload
```

## Tools
| Tool | Zweck |
|------|-------|
| n8n | Workflow-Orchestrierung |
| Claude API | Lyrics + Style Prompts generieren |
| Suno API | Musik generieren + downloaden |
| Higgsfield MCP | Video-Clips generieren |
| ffmpeg | Video zusammenbauen |
| YouTube Data API | Video hochladen |

## Nursery Rhyme Video-Ideen
1. ✅ Humpty Dumpty (fertig)
2. 🐑 Baa Baa Black Sheep
3. ⭐ Twinkle Twinkle Little Star
4. 🕰️ Hickory Dickory Dock
5. 🎵 Jack and Jill
6. 🐑 Mary Had a Little Lamb
7. 🎠 Ring Around the Rosie
8. 🥣 Little Miss Muffet

## Suno Prompt Template (Claude generiert das automatisch)
```
[Intro]
[Verse 1]
{lyrics_verse_1}
[Chorus]
{lyrics_chorus}
[Verse 2]
{lyrics_verse_2}
[Chorus]
{lyrics_chorus}
[Outro]

Style: Children's nursery rhyme, {style_tags}, glockenspiel, xylophone, 
       bouncy 3/4 waltz, toy piano, recorder flute, upbeat, 80-100 BPM
```

## n8n Workflow Schritte
1. Trigger: Manuell oder Schedule (täglich)
2. Input: Thema aus Google Sheet / Variable
3. Claude: Generiert Lyrics + Style Prompt
4. Suno API: Generiert Song (POST /api/generate)
5. Warten: Poll bis Song fertig
6. Download: MP3 von Suno CDN
7. Higgsfield: 36 Clips generieren
8. ffmpeg: Video zusammenbauen
9. YouTube: Upload + Metadata
