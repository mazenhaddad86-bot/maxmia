import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from upload import upload_video

VIDEO = r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\output\baa-baa-black-sheep\baa_baa_final_v3.mp4"

TITLE = "Baa Baa Black Sheep \U0001F411 | Nursery Rhymes & Kids Songs | Max & Mia World"

DESCRIPTION = """Baa Baa Black Sheep, have you any wool? \U0001F411

Sing along with Max & Mia in this fun 3D animated nursery rhyme!
Join the adventure and learn this classic kids song together.

⭐ Subscribe for more nursery rhymes and kids songs every week!

#BaaBaaBlackSheep #NurseryRhymes #KidsSongs #MaxAndMia #ForKids #Toddlers #BabySongs #ChildrenSongs #Preschool #Animation

\U0001F3B5 More videos:
- Wheels on the Bus
- Old MacDonald Had a Farm
- Twinkle Twinkle Little Star

Perfect for babies, toddlers and preschoolers. Educational, fun and safe content for children.

© Max & Mia World - Original nursery rhyme animations."""

TAGS = ["baa baa black sheep","nursery rhymes","kids songs","children songs","baby songs",
        "toddler songs","nursery rhyme","kids videos","max and mia","preschool songs",
        "songs for kids","animation for kids","3d nursery rhymes","sing along","baby shark",
        "cocomelon","kids learning","educational videos for kids","lullaby","bedtime songs"]

vid = upload_video(
    video_path=VIDEO,
    title=TITLE,
    description=DESCRIPTION,
    tags=TAGS,
    category_id="1",       # Film & Animation
    privacy="public",
)
print("DONE:", vid)
