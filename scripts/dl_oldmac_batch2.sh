#!/bin/bash
cd /c/Users/myshi/Documents/Claude/Projects/video-animation-kids/output/oldmacdonald/clips
curl -s -o OM07.mp4 'https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260527_004844_c1beac8f-013b-4461-9326-1ba133a024e7.mp4' &
curl -s -o OM09.mp4 'https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260527_004800_1428ce5a-c724-4a5e-be0a-25e425c4c61c.mp4' &
curl -s -o OM10.mp4 'https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260527_005000_591aaf48-26c4-4771-bb63-edddba5d67e2.mp4' &
curl -s -o OM12.mp4 'https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260527_004900_70093414-b5c1-421d-a82d-7d3595f46067.mp4' &
wait
echo "Downloaded: $(ls OM*.mp4 | wc -l) clips total"
du -sh OM*.mp4 2>/dev/null
