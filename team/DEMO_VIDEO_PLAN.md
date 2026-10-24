# Demo video — 3-minute recording plan (Phase 1, SDC 2026)

Follows the five-beat structure the team agreed on, ~36 s per beat. English voiceover, 1080p,
YouTube unlisted.

## Hard rules

- **Never say "GPU" or "RunPod"** — organisers warned this costs marks while RunPod is unused.
- Say the score is **a ranking rule, not a hiring probability** — the brief asks for this.
- Every data screen: name the **source, the date and the scope**.
- Synthetic profile only; no real names, emails or phone numbers on screen.
- One clear flow: jobseeker. Mention HR / career centre in one sentence, do not demo them.

## Beat 1 — user input · 0:00–0:36

1. Entry scene → **CLICK TO ENTER** → landing page.
2. **Start as jobseeker** (leave the three cards visible for a second).
3. In the intake touch three real inputs: **target field** (interest), **years**, **hours/week**
   (study time).
4. Upload the synthetic CV → detected skills → continue.

Say: "This is a synthetic profile. She picks her target field, her experience, and how many hours
a week she can study. Then she uploads a CV — the parser finds seven skills, and she can edit them
by hand."

## Beat 2 — evidence · 0:36–1:12

Scroll to **2 · Future skills radar**.

1. DOSM panel: total **555,509**, QoQ **−11.4%**, release date, "view source".
2. Point at the line saying this counts **job advertisements by occupation group, not skills**.
3. Named-skill layer and the WEF panel: point at "forecast, global, not Malaysia".

Say: "DOSM published 555,509 advertised vacancies for Q2 2026, down 11.4% on the quarter — that
counts job ads by occupation, not skills. Beside it, named skill demand from a 2025 industry
report, and WEF's global outlook. Every panel states its source, its date, and what it can and
cannot tell you."

## Beat 3 — recommendation · 1:12–1:48

Scroll to **3 · Best-fit future roles**.

1. Point at the top role and its score.
2. Expand it → five bars (coverage / focus / transferability / trend / gap cost).
3. Point at "why this role": transfer, gap, evidence.

Say: "The score is a weighted rule over five inputs, all visible here. Coverage is 84%, but the
demand trend is lower, so this role sits second rather than first. It orders options for a
decision — it is not a hiring probability, and it never scores a person for an employer."

## Beat 4 — comparison / change · 1:48–2:24

Pick **one** of the two change mechanisms - not both, the beat is 36 seconds.

**Option A (preferred: shows a data update).** In the evidence section open *Update the trend data
with a reviewed snapshot*, upload `data/trends/sample_upload_example.json`, and read the before/after
table: the score column moves and one position changes. Say that a permanent update is a reviewed
commit, and that this upload lives only in the session.

**Option B (shows model sensitivity).** Open **AI disruption scenario · moderate / fast**.
2. Read one row: moderate score, fast score, rank arrow.
3. Point at the **SCENARIO ESTIMATE** badge and the caveat.

Say: "Same profile, two disruption speeds. Under fast disruption the trend carries more weight, so
scores move and some positions swap — this table shows what changed and by how much. We label the
whole block as a scenario estimate: one quarter or one weighting is not a long-term prediction."

## Beat 5 — action plan · 2:24–3:00

1. Scroll to **4 · Skills to close and your pathway**.
2. Read the three metrics: skills to close, estimated weeks, **best match after the plan** + delta.
3. Show the ordered steps and the course table (free, real links).
4. End on **5 · SDG** or the repo page.

Say: "The plan lists the missing skills, ordered cheapest-first, with real free resources and an
estimated number of weeks. Finishing it lifts the best match by twenty points. Each skill is also
tagged to an SDG target, and we label that mapping as our own reading. The links are real; prices
still need confirming."

## Setup (once, ~15 minutes)

1. Browser 1920×1080, zoom 110%, bookmarks bar hidden, one window only.
2. **Warm the app first**: run the whole flow once and keep the tab open — the free instance
   sleeps and needs 30–60 s to wake.
3. Close WeChat / Discord; turn on Focus Assist.
4. OBS: 1080p, 30 fps, screen + microphone, MP4, one file per beat.
5. Mic check: 10-second test, listen back.
6. Synthetic CV only (`data/sample_cv.txt`).

## Edit and upload

1. CapCut / Clipchamp: cut dead air, normalise audio, small labels
   (Input / Evidence / Ranking / Scenario / Plan).
2. Export 1080p MP4, target 3:00–3:20.
3. YouTube → **Unlisted** → title
   `SkillRadar MY — SDC 2026 Domain 1 demo (Lumina Nusantara)`.
4. English captions; skim for product-name typos.
5. Put the link in `README.md` (row **Demo Video**) and in the Team Portal field.

## Pre-upload check

- [ ] No GPU / RunPod wording
- [ ] "Not a hiring probability" said out loud in beat 3
- [ ] Source + date visible on every data screen
- [ ] Only synthetic profile on screen
- [ ] Length 3:00–3:30
- [ ] Link opens in a private window
