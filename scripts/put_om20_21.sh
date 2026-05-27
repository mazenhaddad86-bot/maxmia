#!/bin/bash
cd /c/Users/myshi/Documents/Claude/Projects/video-animation-kids/output/oldmacdonald/images
curl -s -X PUT -H "Content-Type: image/png" --data-binary @OM20.png 'https://d276s3zg8h21b2.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/5264ccdd-553d-4e91-baf7-c54fd797591d.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAYPNTVMCGYPZMTKFK%2F20260527%2Feu-north-1%2Fs3%2Faws4_request&X-Amz-Date=20260527T005750Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=content-type%3Bhost&X-Amz-Signature=83f8f40646f6c7964830a8eafebe02542c0cfd51d0c0a91326f41514b19868a7' -w "OM20:%{http_code}\n" &
curl -s -X PUT -H "Content-Type: image/png" --data-binary @OM21.png 'https://d276s3zg8h21b2.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/c32396ec-e8c4-4fe6-8557-8cd4a57ea43c.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAYPNTVMCGYPZMTKFK%2F20260527%2Feu-north-1%2Fs3%2Faws4_request&X-Amz-Date=20260527T005750Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=content-type%3Bhost&X-Amz-Signature=200664f973970703545a907925de223f1ca7346e6b9b05efb7b3b45540fe0c0f' -w "OM21:%{http_code}\n" &
wait
echo "done"
