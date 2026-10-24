# Deck talking points

Generated from `submission/SDC2026_LuminaNusantara_SlideDeck.pptx` (12 slides).
Each slide lists its own text, top to bottom.

## Slide 1

- SKILLRADAR MY
- LUMINA NUSANTARA
- SDC 2026 · DOMAIN 1 — THE AIVERSECITY FUTURE-READY WORKFORCE DOMAIN
- From who I am today to where I can be in the AI era.
- Explainable role matching · versioned labour-market signals · personalised reskilling pathways
- TEAM LUMINA NUSANTARA
- XIAMEN UNIVERSITY MALAYSIA
- SDG 4 · TARGETS 4.4 / 8.5
- Preliminary-round deck · Live demo on Streamlit Community Cloud

## Slide 2

- · SDC 2026 · SKILLRADAR MY
- Contents WHAT'S INSIDE
- An AI-assisted reskilling navigator built on the UN Sustainable Development Goals — led by SDG 4, Quality Education.
- 01
- Problem
- The training gap is widening
- 02
- Who we build for
- Four personas, one question
- 03
- Our solution
- Four steps to a new role
- 04
- Key features
- The six must-haves, delivered
- 05
- Explainable scoring
- Five inputs, fully auditable
- 06
- Technical design
- Signals in, pathways out
- 07
- SDG impact & demo
- Intended contribution, live proof
- SkillRadar MY · Lumina Nusantara · SDC 2026
- 02 / 12

## Slide 3

- 01 · PROBLEM · BACKGROUND
- AI is changing roles faster than training systems can update
- 56%
- of Malaysian professionals already use AI tools at work
- yet only
- 26%
- have received any formal AI training
- A 30-point gap between tool adoption and capability — most people are improvising with AI, unguided.
- 600k+
- Malaysian workers are expected to need reskilling within the next 3–5 years
- — Ministry of Science, Technology & Innovation (MOSTI)
- The reskilling window is closing: skill frameworks haven't caught up, and job requirements have already moved.
- Sources: Hays Asia Salary Guide 2025; MOSTI public statement (2025).
- SkillRadar MY · Lumina Nusantara · SDC 2026
- 03 / 12

## Slide 4

- 01 · PROBLEM · BACKGROUND
- Three gaps keep people stuck in place
- 1
- Workers can't see the way forward
- They don't know which AI skills are worth learning, or whether their own role is rising or declining.
- 2
- Employers can't see the gap
- HR can't translate AI headlines into a training plan — team reskilling lacks a data basis.
- 3
- Training providers ship stale maps
- Learning pathways are static lists; by the time a course launches, demand has moved.
- A one-off skills assessment is not enough — people need a system that keeps evolving as the market does.
- SkillRadar MY · Lumina Nusantara · SDC 2026
- 04 / 12

## Slide 5

- 02 · WHO WE BUILD FOR
- Built for everyone the AI shift touches
- Four personas, one shared question — “what should I learn next?” The live demo opens with this exact choice.
- Jobseeker / worker at risk
- “Will my role disappear? Where do I go next — and what do I learn to get there?”
- WORKER FLOW: QUESTIONNAIRE + CV UPLOAD
- Graduate & career switcher
- “Show me the direction before I bet my career start on a shrinking track.”
- GRADUATE STUDY-FIELD FILTERING
- HR & talent development
- “Give me a team-level skills-gap view I can actually plan training around.”
- HR FLOW: ROSTER → GAP HEATMAP & PLAN
- TVET & career centres
- “Back career advice with live data, not an outdated handbook.”
- CAREER-CENTRE FLOW: CURRICULUM COVERAGE
- SkillRadar MY · Lumina Nusantara · SDC 2026
- 05 / 12

## Slide 6

- 03 · OUR SOLUTION
- One web app, four steps from here to your next role
- 01
- Tell us who you are
- Upload a CV or answer a 3-minute questionnaire — get a structured skills profile.
- →
- 02
- See the market evidence
- A versioned trend layer of dated, linked sources: job offerings, named-skill signals, global forecasts.
- →
- 03
- Get matched roles
- Future roles ranked by an explainable score, with your skill gaps spelled out.
- →
- 04
- Follow your pathway
- An ordered learning plan with weekly steps, free or low-cost resources and SDG tags.
- Design principles — every recommendation is explainable and source-traceable; forecasts come as scenarios and are labelled as estimates. The judgement stays with the person, not the algorithm.
- SkillRadar MY · Lumina Nusantara · SDC 2026
- 06 / 12

## Slide 7

- 04 · KEY FEATURES
- The six must-haves — all running in the live demo
- ✓
- Skills profile intake
- Questionnaire + synthetic CV parsing into a shared 54-skill taxonomy.
- ✓
- AI-trend signal layer
- Dated, linked snapshots: DOSM job offerings, JobStreet–Randstad 2025, WEF 2025 — uploaded snapshots re-rank the current profile.
- ✓
- Future-role matching
- Explainable score decomposed into five auditable inputs.
- ✓
- Personalised pathway
- Ordered weekly steps toward free / low-cost courses; 60 course links covering all 54 skills.
- ✓
- SDG mapping
- Role-level SDG tags plus a skill-to-target crosswalk, labelled as the team's own reading.
- ✓
- Uncertainty handled
- Moderate vs fast disruption scenarios; every forecast marked as an estimate.
- Beyond the checklist: HR team gap heatmap · evidence-source robustness check · trilingual EN / BM / 中文 · low-bandwidth friendly.
- SkillRadar MY · Lumina Nusantara · SDC 2026
- 07 / 12

## Slide 8

- 05 · EXPLAINABLE SCORING
- One score, five inputs — auditable to the source
- THE MODEL (AS SHIPPED IN THE DEMO)
- score = 0.30 · skill coverage + 0.25 · role focus + 0.15 · transferability + 0.15 · demand trend + 0.15 · (1 − gap cost)
- Fast-disruption scenario re-weights toward trend (0.35) and penalises flat or declining roles — the toggle is visible in the demo.
- Every input opens in the UI Each skill signal carries its source name, publish date and retrieval date. Scores are prototype estimates — never hiring probabilities.
- BUSINESS OPERATIONS ASSOCIATE
- Actual demo output · synthetic profile
- 64.0
- MATCH SCORE / 100
- Skill coverage
- 84%
- Role focus
- 50%
- Transferability
- 50%
- Demand trend
- 70%
- Gap cost · lower is better
- 45%
- SkillRadar MY · Lumina Nusantara · SDC 2026
- 08 / 12

## Slide 9

- 06 · TECHNICAL DESIGN
- Signals in, pathways out — four honest layers
- STREAMLIT WEB APP
- Trilingual EN / BM / 中文 UI · worker, graduate, HR and career-centre flows · low-bandwidth friendly
- DETERMINISTIC ENGINE
- Pure-Python scoring, pathway & SDG modules — no external AI service on the request path · 52 automated tests
- CURATED CATALOGUES
- Role & skill catalogue · 60 linked course records · skill-to-SDG crosswalk, all versioned in JSON
- TREND SIGNAL SNAPSHOTS
- DOSM online job offerings 2026 Q1/Q2 · JobStreet–Randstad 2025 skill signals · WEF Future of Jobs 2025 · validated manual import, source + date shown · in-app reviewed snapshot re-ranks in-session
- IN THE DEMO TODAY
- ON THE ROADMAP
- Rule-based explainable scoring · scenario toggle · evidence-source robustness check · HR heatmap · trilingual UI · tested data-import pipeline.
- LLM / vector semantic CV parsing · automated trend scraping · verified course durations & fees · fairness audits across age, gender and background.
- SkillRadar MY · Lumina Nusantara · SDC 2026
- 09 / 12

## Slide 10

- 07 · SDG IMPACT · INTENDED CONTRIBUTION
- Every pathway points at the Goals — led by SDG 4
- Primary track: SDG 4 Quality Education (Target 4.4), with SDG 8.5 on decent work. Framed as intended contribution — impact indicators are still to be validated.
- SDG 4 · Quality Education
- Reskilling pathways built from free and low-cost resources — education that reaches working adults, not just students.
- SDG 8 · Decent Work & Growth
- Helping workers transition into AI-era roles with their employability and dignity intact (intended outcome, to be measured).
- SDG 5 · Gender Equality
- Recommendations must not systematically differ by gender or age — fairness checks are on the roadmap.
- SDG 10 · Reduced Inequalities
- Trilingual, low-bandwidth design so urban and rural learners use the same tool.
- Honest mapping: the skill-to-target crosswalk is the team's own reading of the 2030 Agenda — it is shown in-app and labelled as such, not claimed as an official UN correspondence.
- SkillRadar MY · Lumina Nusantara · SDC 2026
- 10 / 12

## Slide 11

- 07 · PROTOTYPE · LIVE DEMO
- Three screens from the running app
- sdc2026-lumina-nusantara…streamlit.app
- 1
- …streamlit.app · role matches
- 2
- …streamlit.app · pathway & SDG
- 3
- Screenshots captured from the live demo · synthetic sample data · free-tier instance may take 30–60 s to wake.
- SkillRadar MY · Lumina Nusantara · SDC 2026
- 11 / 12

## Slide 12

- SKILLRADAR MY
- Make AI everyone's partner — not their replacement.
- 01
- Pilot with TVET institutions and career centres
- 02
- Verified course catalogue — real durations, links and fees
- 03
- Fairness audits across age, gender and background
- TRY IT YOURSELF
- Live demo (Streamlit) sdc2026-lumina-nusantara…streamlit.app GitHub repository github.com/douyinlin/sdc2026-lumina-nusantara
- THANK YOU · Q&A
- SkillRadar MY · Lumina Nusantara · SDC 2026
- 12 / 12
