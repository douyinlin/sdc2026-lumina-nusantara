# Recording setup for this laptop

Screen: **2560 × 1600 at 150% scaling** (logical 1707 × 1067). OBS 32.2.2 is installed.
Recording at native 1600p/60 fps looks fine in OBS but produces a heavy file and makes the
interface text small on a 1080p upload. The setup below fixes that: a 1080p/30 fps canvas, a clean
browser window that maps 1:1 to it, and the microphone as the only audio source.

## What was already created

| Item | Where |
| --- | --- |
| OBS profile `SkillRadar` — 1920×1080, 30 fps, mp4, mic only, saves to `Videos\SkillRadar` | `%APPDATA%\obs-studio\basic\profiles\SkillRadar\basic.ini` |
| OBS scene `SkillRadar` — one window-capture source, canvas 1920×1080, desktop audio muted | `%APPDATA%\obs-studio\basic\scenes\SkillRadar.json` |
| Browser launcher — Edge in app mode, 1280×720 logical = **1920×1080 physical** | `team/recording/open-app.cmd` |

The old profile and scene are untouched.

## Steps (5 minutes)

1. **Close OBS.** It is running now, and it only reads the new profile and scene at start-up.
2. Start the browser with `team/recording/open-app.cmd`. A window opens with no tabs, no bookmarks
   and no extensions, already sized to the canvas.
3. Open OBS → **Profile → SkillRadar**, then **Scene Collection → SkillRadar**.
4. In the scene, select **App window** → **Properties** → choose the window titled
   *SkillRadar MY* (Edge). Tick nothing else.
5. With the source selected press **Ctrl+F** (fit to screen). It should fill the canvas exactly, with
   no black bars.
6. Settings → Output: confirm **Recording path** `C:\Users\45\Videos\SkillRadar`, format `mp4`,
   encoder `x264`, quality `High Quality`.
7. Settings → Audio: microphone is the only active input; desktop audio is muted.

## Before every take

- Press **Record**, wait two seconds, then start talking — the first frames of x264 are the slowest.
- Keep the browser window where it is; moving it mid-take makes the capture jump.
- If the app is asleep, click once and wait for it to wake **before** recording.
- Stop the recording with the same button, then check the file plays before starting the next beat.

## If the window capture shows black

Edge sometimes hands an empty surface to the capture. Switch the source to **Window Capture → method
Windows 10 (1903 and up)** and pick the window again. Do not switch to Display Capture: that records
2560×1600 and gets downscaled, which softens every letter.

## Why 1280 × 720, not 1920 × 1080

At 150% scaling, a 1280×720 logical window is 1920×1080 physical pixels. OBS captures those pixels
and drops them into the canvas with no scaling at all, so text stays sharp. A 1920×1080 logical
window would be 2880×1620 physical — larger than the screen.
