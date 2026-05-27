#!/bin/bash
cd /c/Users/myshi/Downloads
curl -s -X PUT -H "Content-Type: image/png" --data-binary @maxmia.png 'https://d276s3zg8h21b2.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/9c581440-50ed-4fc7-9fdd-3ad50cba244b.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAYPNTVMCGYPZMTKFK%2F20260526%2Feu-north-1%2Fs3%2Faws4_request&X-Amz-Date=20260526T232946Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=content-type%3Bhost&X-Amz-Signature=27008e58462925aa36dd9566c5fafb0e64f7e7d4652d148c63fe4582b9ba36d7' -w "%{http_code}\n"
