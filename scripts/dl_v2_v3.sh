#!/bin/bash
cd /c/Users/myshi/Documents/Claude/Projects/video-animation-kids/output/v2_alternates
declare -A urls=(
  [FM11v2]="https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260526_233024_c1d5f969-541b-4a5c-8518-1f9f3d6c08a4.png"
  [FM12v2]="https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260526_233031_4d87ff89-efe8-4036-8d19-a5ec9696371e.png"
  [FM13v2]="https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260526_233038_79f086c3-f3b6-425b-a9fb-e9bb1b76bfd4.png"
  [FM15v2]="https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260526_233115_694215e7-84f5-4039-88aa-bfa3ea5838a1.png"
  [ML11v2]="https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260526_233355_2f0a9557-0d37-4958-8dcc-bf1d43928355.png"
  [HE01v2]="https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260526_233640_fdad6230-dd78-4f33-859a-208d36a75e42.png"
  [HE03v2]="https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260526_233803_07e6397b-8b5d-4af6-ba4b-b54750d98a27.png"
  [HE04v2]="https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260526_233810_3f32e150-41c6-4498-99b5-27ff9d1a0554.png"
  [HE05v2]="https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260526_233840_f3d81fb2-a816-4383-b42b-b98669cbd9fb.png"
  [HE07v2]="https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260526_234003_c45b6465-be14-45e9-bac1-cea285f21fbb.png"
  [HE08v2]="https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260526_234010_ad328200-d372-4c79-b2e8-7e3191347938.png"
  [HE10v2]="https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260526_234133_2e80a6af-af45-48cc-b1a7-dd0f328e2342.png"
  [HE11v2]="https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260526_234140_039e1ab1-5228-400c-81ee-759ad9a1452f.png"
  [HE12v2]="https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260526_234147_cb202fb1-c36b-4ef1-8984-4908c12f686e.png"
  [HE13v2]="https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260526_234154_7f01abbb-6524-46b6-bcc1-f3b23dc2f650.png"
  [HE14v2]="https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260526_234224_f15e278c-523d-4ea3-8b61-edb13d26704c.png"
  [IB05v2]="https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260526_232938_e3841775-0fc4-4d7a-9b87-35a205a41675.png"
  [IB06v2]="https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260526_233008_e5d05e8e-b668-49bc-8aad-fedb596322f9.png"
  [IB09v2]="https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260526_233310_480dc942-de6f-4fde-9fe3-3a1d31c0a461.png"
  [IB10v2]="https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260526_233340_c546eacc-944c-4990-9f0a-38db43f93f7c.png"
  [IB11v2]="https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260526_233410_5643588b-51d8-4fdb-a292-95b439082b69.png"
  [IB12v2]="https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260526_233440_c5194398-db3a-40af-9f05-c9e9dadf5d41.png"
  [IB13v2]="https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260526_233510_25c1d61a-0661-4217-ae93-afe53141cc22.png"
  [IB15v2]="https://d8j0ntlcm91z4.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/hf_20260526_233633_972b9f05-ddd0-43d2-82e3-9ed8b172b4a3.png"
)
for label in "${!urls[@]}"; do
  curl -s -o "$label.png" "${urls[$label]}" &
done
wait
echo "downloaded: $(ls *.png | wc -l)"
