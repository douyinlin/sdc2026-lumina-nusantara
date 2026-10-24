# SDG mapping, and what we actually validated

## SDG mapping

**Track:** SDG 4, sub-target **4.4** (relevant skills for employment), with **8.5** (decent work and
equal pay) as the second target and 9.5 / 10.2 tags on some skills.

The mapping goes down to **skill level**: all 54 skills in the catalogue carry one or more targets in
`data/skills_sdg.json`. Roles inherit the targets of their required skills.

**This crosswalk is the team's own reading of the targets.** It is not an official UN or DOSM mapping,
and the interface says so next to the chart. Impact numbers are targets, never measured results.

## What was tested

| Check | Result |
| --- | --- |
| Automated tests | **54**, run with `python -m unittest discover -s tests -p "test_*.py"` |
| Page flows | all three personas, walked in English / Bahasa Malaysia / 中文 |
| Profiles used | synthetic only (`data/sample_cv.txt`) |
| Course links | **60** links covering all 54 skills, each checked as reachable on 24 October 2026 |
| Trend snapshots | validated on import: source URL host, publication date, mapping keys |
| Live demo | Streamlit Community Cloud, free tier (may take 30–60 s to wake) |

## What was **not** tested

- **No user study.** No interviews, no usability sessions, no baseline task time.
- Course durations and fees are **not re-verified**; the catalogue records that per row.
- One quarter of DOSM data cannot establish a trend.

## Phase 2 targets

Ten consenting adult testers on synthetic profiles; median plan completion under five minutes; at
least 70% rating a top-three role 4/5 or better; 100% of displayed recommendations carrying a source
or an explicit assumption label.

These are targets. None of them has been achieved yet, and none is presented as a result.

## Known limits

**Résumé parsing is the least finished part of the product.** It is keyword and alias matching over
a fixed catalogue of 54 skills — no semantic model, no layout awareness. In practice that means it
misses synonyms and abbreviations, silently drops skills outside the catalogue, and returns nothing
for scanned PDFs that have no text layer. A user can correct the result by hand, and the app says so
when nothing is recognised, but automatic detection is partial by design at this stage.

The occupation-to-skill mapping is a heuristic; some course prices are stale; the scenario weights
are assumptions. Each of these is stated in the interface or the README rather than hidden.
