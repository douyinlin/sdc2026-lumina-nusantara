@echo off
REM Clean 1280x720 (logical) Edge window for the demo recording.
REM On a 150% display this is 1920x1080 physical pixels - exactly the OBS canvas.
set URL=https://sdc2026-lumina-nusantara-65cnugvuxdle5dgp9ky3fs.streamlit.app
set PROFILE=%LOCALAPPDATA%\SkillRadar-record

start "" msedge ^
  --app="%URL%" ^
  --window-size=1280,720 ^
  --window-position=40,40 ^
  --user-data-dir="%PROFILE%" ^
  --no-first-run ^
  --no-default-browser-check ^
  --disable-features=msEdgeSidebarV2,msEdgeCollections ^
  --hide-crash-restore-bubble
