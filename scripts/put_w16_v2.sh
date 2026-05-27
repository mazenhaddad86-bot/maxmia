#!/bin/bash
cd /c/Users/myshi/Documents/Claude/Projects/video-animation-kids/output/wheels/images
curl -s -X PUT -H "Content-Type: image/png" --data-binary @W16.png 'https://d276s3zg8h21b2.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/333f9ca2-dbf7-4269-a95d-1f8c8e736b57.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAYPNTVMCGYPZMTKFK%2F20260526%2Feu-north-1%2Fs3%2Faws4_request&X-Amz-Date=20260526T222125Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=content-type%3Bhost&X-Amz-Signature=95f8abcdd523210ae02c95cf056c0f43387d33585a5f430aaa196e9b30195a84' -w "W16:%{http_code}\n"
