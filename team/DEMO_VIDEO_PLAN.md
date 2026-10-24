# Demo video — 6-minute recording plan (Phase 1, SDC 2026)

Follows the organiser's six-block timing. English voiceover, 1080p, YouTube unlisted, linked from
the README.

## Hard rules

- **Never say "GPU" or "RunPod" is used.** RunPod is not part of this build; say plainly that the
  app calls no GPU endpoint and leave it there.
- The score is **a ranking rule, not a hiring probability** — say it out loud once.
- Every data screen: name the **source, the date and the scope**.
- Synthetic profile only; no real names, emails or phone numbers on screen.
- Say "planned / not built yet" for anything that is not in the demo. The brief allows unfinished
  features if they are labelled.

## Block 1 — problem and user · 0:00–0:40

Screen: landing page, then the three entry cards.

Say: "In Malaysia, 56% of professionals already use AI at work, but only 26% have had formal
training. A worker who is told to 'learn AI' still has to answer three questions: which role fits
me, which skills am I actually missing, and what do I study first. SkillRadar MY answers those three
questions with numbers the user can check."

## Block 2 — what the product does · 0:40–1:10

Screen: results page, scroll slowly past the evidence, ranking and pathway sections.

Say: "It turns a profile into a ranked shortlist of future-fit roles, each with a visible score,
the evidence behind its demand trend, and an ordered learning path with real resources. The
difference from a course list: every number is traceable, and nothing is generated at request time."

## Block 3 — real product walkthrough · 1:10–4:10

1. **Input (1:10–1:45)** — synthetic CV upload, parsed skills, edit one by hand, set hours/week.
2. **Trend evidence (1:45–2:30)** — DOSM panel: 555,509 vacancies, Q2 2026, −11.4% QoQ; point at the
   line that says this counts job ads by occupation, not skills. Then the named-skill layer and the
   WEF panel: global forecast, not a Malaysian measurement.
3. **Recommendation (2:30–3:20)** — top role, five score inputs, "why this role" block. Say: "This
   orders options for a decision; it is not a hiring probability."
4. **A real change (3:20–4:00)** — open *Update the trend data*, upload
   `data/trends/sample_upload_example.json`, read the before/after table: scores move, one position
   changes. Say the upload lives only in the session and a permanent update is a reviewed commit.
5. **Learning route (4:00–4:10)** — hold on the pathway: first skill, weeks, free resource link.

## Block 4 — technical implementation · 4:10–5:00

**4:10–4:30 — where the data comes from.**
Screen: the README *Data sources* table, then `data/trends/` in the repository.

Say: "Three kinds of input, kept separate. DOSM publishes advertised vacancies by occupation — we
transcribe the counts by hand and keep the release link and the date in the JSON. Industry reporting
gives named skills, and the WEF report gives a global forecast. Every file carries its source URL,
its publication date and a note on what it can and cannot support."

**4:30–4:45 — what the program does, what the AI does.**
Screen: the results page score, then a terminal running the test suite.

Say: "The running application contains no model. Parsing is a keyword and alias matcher; scoring is
five weighted rules; the pathway is a lookup over a curated catalogue. That is deliberate: a user can
be shown exactly why a role ranked where it did, and the same profile always produces the same
answer. AI tools were used to write the code — DeepSeek, Copilot, Codex — and every change was read,
run and tested before it was kept."

**4:45–5:00 — Replit and RunPod.**
Screen: the repository's Replit screenshots folder, or the Technical Declaration section 3.2.

Say: "Replit was our development workspace, and screenshots of that use are in the repository.
RunPod is not used: there is no GPU endpoint anywhere in this project, the public demo runs on
Streamlit Community Cloud, and the Technical Declaration says so."

## Block 5 — SDG and what was actually tested · 5:00–5:40

**5:00–5:20 — SDG.**
Screen: the SDG section, skill-level tags.

Say: "The track is SDG 4, sub-target 4.4 — relevant skills for employment — with 8.5 as the second
target. The mapping goes down to individual skills: this pathway's skills are tagged to 4.4 and 9.5,
and we label that crosswalk as our own reading, not an official UN mapping."

**5:20–5:40 — validation, honestly.**
Screen: test output, then the robustness table.

Say: "What we did test: 52 automated tests, a walkthrough of every flow in three languages on
synthetic profiles, and 36 course links checked as reachable. What we have not done: a user study.
The Phase 2 target is ten testers, a median plan in under five minutes, and 70% rating a top-three
role at least 4 out of 5. Those are targets, not results."

## Block 6 — limits and next steps · 5:40–6:00

Screen: README *Known limitations*, or the last slide of the deck.

Say: "Known limits: the occupation-to-skill mapping is our heuristic, one quarter is not a trend,
course fees are unverified, and the parser misses synonyms. Next: verified course metadata, semantic
CV parsing, and the user pilot. Everything that is planned is labelled as planned."

## Setup

1. Browser 1920×1080, zoom 110%, bookmarks bar hidden, one window only.
2. Warm the app first — the free instance sleeps and needs 30–60 s to wake.
3. Close WeChat / Discord; Focus Assist on.
4. OBS: 1080p, 30 fps, screen + microphone, MP4, one file per block.
5. Mic check: 10-second test, listen back.

## Edit and upload

1. CapCut or Clipchamp: cut dead air, normalise audio, six small labels matching the blocks.
2. Export 1080p, target 5:50–6:10.
3. YouTube → **Unlisted** → `SkillRadar MY — SDC 2026 Domain 1 demo (Lumina Nusantara)`.
4. English captions; check product names.
5. Link in `README.md` (row **Demo Video**) and in the Team Portal field.

## Pre-upload check

- [ ] No claim that RunPod or a GPU is used
- [ ] "Not a hiring probability" said once
- [ ] Source + date visible on every data screen
- [ ] Only synthetic profile on screen
- [ ] "Not built yet" said for anything planned
- [ ] Length 5:50–6:20
- [ ] Link opens in a private window
