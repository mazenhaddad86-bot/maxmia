import sys
sys.path.insert(0, '.')
from youtube.upload import upload_video

BASE = r'output\baa-baa-black-sheep'
THUMB = r'output\baa-baa-black-sheep\thumbnail.jpg'
TAGS = ['Baa Baa Black Sheep','Shorts','nursery rhyme','kids music','Max and Mia','toddler','preschool','kids songs','animated','sheep']

videos = [
    {
        'file': BASE + r'\baa_baa_SHORT_part1.mp4',
        'title': 'Baa Baa Black Sheep Part 1 #Shorts | Max & Mia',
        'desc': 'Baa Baa Black Sheep with Max & Mia! Part 1\n\n#BaaBaaBlackSheep #Shorts #NurseryRhyme #KidsMusic #MaxAndMia #Toddler #Preschool',
    },
    {
        'file': BASE + r'\baa_baa_SHORT_part2.mp4',
        'title': 'Baa Baa Black Sheep Part 2 #Shorts | Max & Mia',
        'desc': 'Baa Baa Black Sheep with Max & Mia! Part 2\n\n#BaaBaaBlackSheep #Shorts #NurseryRhyme #KidsMusic #MaxAndMia #Toddler #Preschool',
    },
    {
        'file': BASE + r'\baa_baa_SHORT_part3.mp4',
        'title': 'Baa Baa Black Sheep Part 3 #Shorts | Max & Mia',
        'desc': 'Baa Baa Black Sheep with Max & Mia! Part 3\n\n#BaaBaaBlackSheep #Shorts #NurseryRhyme #KidsMusic #MaxAndMia #Toddler #Preschool',
    },
]

for v in videos:
    print('--- Uploading:', v['title'])
    upload_video(
        video_path=v['file'],
        title=v['title'],
        description=v['desc'],
        tags=TAGS,
        category_id='27',
        privacy='public',
        thumbnail_path=THUMB,
    )
