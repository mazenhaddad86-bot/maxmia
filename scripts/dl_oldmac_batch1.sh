#!/bin/bash
mkdir -p /c/Users/myshi/Documents/Claude/Projects/video-animation-kids/output/oldmacdonald/clips
cd /c/Users/myshi/Documents/Claude/Projects/video-animation-kids/output/oldmacdonald/clips
curl -s -o OM01.mp4 'https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260527_004158_bec079bf-86f3-49e2-8aa7-cf5bd6696130.mp4' &
curl -s -o OM02.mp4 'https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260527_004201_788c7119-f655-4cae-8345-d9140c263b1d.mp4' &
curl -s -o OM03.mp4 'https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260527_004203_140ef07b-335c-4c23-b53e-b741d55e2016.mp4' &
curl -s -o OM04.mp4 'https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260527_004205_401a170c-5fc1-4bab-8050-fd1e419aba6d.mp4' &
wait
echo "Downloaded: $(ls *.mp4 | wc -l) clips"
du -sh *.mp4 2>/dev/null
