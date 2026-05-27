@echo off
REM Canary mit CDP + separatem Profil (Default-Profile blockt CDP!)
start "" "C:\Users\myshi\AppData\Local\Google\Chrome SxS\Application\chrome.exe" --remote-debugging-port=9222 --remote-allow-origins=* --user-data-dir="C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\.canary-cdp-profile"
