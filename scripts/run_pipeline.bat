@echo off
REM =====================================================================
REM  Leo & Mia Video Pipeline — läuft automatisch beim PC-Start
REM  Max. 1x pro Tag (prüft ob heute schon gelaufen)
REM =====================================================================
setlocal

set PROJECT=C:\Users\myshi\Documents\Claude\Projects\video-animation-kids
set STAMP=%PROJECT%\output\.last_run

REM Heutiges Datum holen
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set DT=%%I
set TODAY=%DT:~0,8%

REM Schon heute gelaufen? Dann überspringen.
if exist "%STAMP%" (
    set /p LAST=<"%STAMP%"
    if "%LAST%"=="%TODAY%" (
        echo [%DATE% %TIME%] Heute schon gelaufen — überspringe. >> "%PROJECT%\pipeline.log"
        exit /b 0
    )
)

REM Warte 60 Sekunden damit Windows + WLAN vollständig gestartet sind
timeout /t 60 /nobreak > nul

REM Ins Projekt-Verzeichnis
cd /d "%PROJECT%"

REM Venv aktivieren
call .venv\Scripts\activate.bat

REM Pipeline starten
echo [%DATE% %TIME%] Pipeline startet... >> pipeline.log
python -m src.main

REM Datum als "heute gelaufen" speichern
echo %TODAY% > "%STAMP%"

echo [%DATE% %TIME%] Pipeline fertig. >> pipeline.log
endlocal
