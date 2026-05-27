"""Upload 6 new Max & Mia videos to YouTube (sequential, 1 per run if invoked with --one)."""
import sys
sys.path.insert(0, '.')
from youtube.upload import upload_video

VIDEOS = [
    {
        "key": "wheels",
        "file": r"output\wheels\wheels_final.mp4",
        "title": "Wheels on the Bus  Max and Mia Sunny Bus Adventure!",
        "desc": "Hop on the bright yellow school bus with Max and Mia for a sunny adventure!\nRound and round the big wheels spin through town. White birds say swish swish swish, doors open and shut, the horn beeps beep beep beep!\n\nA bouncy nursery rhyme song perfect for toddlers and preschoolers.\n\n#WheelsOnTheBus #NurseryRhymes #KidsSongs #MaxAndMia #ToddlerSongs #PreschoolMusic",
        "tags": ["wheels on the bus", "nursery rhymes", "kids songs", "Max and Mia", "toddler", "preschool", "bus song", "kids music", "animation", "Pixar style"],
    },
    {
        "key": "twinkle",
        "file": r"output\twinkle\twinkle_final.mp4",
        "title": "Shiny Shiny Tiny Gem  Max and Mia Lullaby (Sleep Song for Babies)",
        "desc": "A gentle lullaby with Max and Mia. Watch them float through a starry night sky, meet the smiling moon, and say goodnight to the stars.\n\nPerfect for bedtime, nap time, and quiet play. Soft orchestral lullaby for babies and toddlers.\n\n#Lullaby #BedtimeSong #SleepMusic #KidsSongs #MaxAndMia #NurseryRhymes",
        "tags": ["lullaby", "bedtime song", "sleep music for babies", "kids songs", "Max and Mia", "twinkle little star", "nursery rhymes", "baby sleep"],
    },
    {
        "key": "oldmac",
        "file": r"output\oldmacdonald\oldmac_final.mp4",
        "title": "Old MacDonald Had a Farm  Max and Mia Farm Animal Song",
        "desc": "EE-I-EE-I-O! Join Max and Mia on Old MacDonald's farm to meet all the friendly animals  cow, pig, duck, sheep, and horse!\n\nLearn animal sounds with this classic country folk nursery rhyme.\n\n#OldMacDonald #FarmAnimals #NurseryRhymes #KidsSongs #MaxAndMia #AnimalSounds",
        "tags": ["old macdonald", "farm animals", "nursery rhymes", "animal sounds", "kids songs", "Max and Mia", "toddler music"],
    },
    {
        "key": "babyshark",
        "file": r"output\babyshark\babyshark_final.mp4",
        "title": "Shark Family Dance  Max and Mia Beach Adventure!",
        "desc": "Doo doo doo doo! Max and Mia meet the friendly shark family at the sunny beach!\n\nMama Shark, Papa Shark, Granny Shark with tiny specs reading books, and Granny Shark with a tiny hat telling tales  all swim in a line through the sea!\n\n#SharkSong #BabyShark #BeachSongs #KidsSongs #MaxAndMia #NurseryRhymes",
        "tags": ["baby shark", "shark family", "kids songs", "Max and Mia", "beach song", "ocean songs", "nursery rhymes", "doo doo"],
    },
    {
        "key": "hickory",
        "file": r"output\hickory\hickory_final.mp4",
        "title": "Tickety Tockety Toe  Max and Mia Mouse and Clock Song",
        "desc": "Tick-tock tick-tock! Hear the grandfather clock! Max and Mia in the attic watch as the friendly mouse climbs high and slow.\n\nThe clock chimes one, the mouse has fun. The clock chimes two, the mouse says boo!\n\n#HickoryDickoryDock #KidsSongs #NurseryRhymes #MaxAndMia #MouseSong #ClockSong",
        "tags": ["hickory dickory dock", "mouse song", "clock song", "nursery rhymes", "kids songs", "Max and Mia", "preschool"],
    },
    {
        "key": "row",
        "file": r"output\row\row_final.mp4",
        "title": "Paddle Paddle Little Boat  Max and Mia Stream Adventure",
        "desc": "Paddle paddle, little boat, gently down the stream. Mary Mary Mary Mary, life is but a dream!\n\nRow with Max and Mia past trees, flowers, ducks, and fish on a sunny lake at golden hour.\n\n#RowRowRowYourBoat #KidsSongs #NurseryRhymes #MaxAndMia #BoatSong #PreschoolMusic",
        "tags": ["row row row your boat", "boat song", "kids songs", "Max and Mia", "nursery rhymes", "lake", "calm music"],
    },
]


def upload_one(v):
    print(f"\n=== Uploading: {v['title']} ===")
    return upload_video(
        video_path=v["file"],
        title=v["title"],
        description=v["desc"],
        tags=v["tags"],
        category_id="27",  # Education
        privacy="public",
    )


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    if arg and arg.startswith("--key="):
        key = arg.split("=")[1]
        for v in VIDEOS:
            if v["key"] == key:
                upload_one(v)
                break
    else:
        print("Usage: upload_6_videos.py --key=<wheels|twinkle|oldmac|babyshark|hickory|row>")
        print("Available keys:", [v["key"] for v in VIDEOS])
