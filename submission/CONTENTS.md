# Submission package — what is in here

Everything the judges need, in one place. The ZIP is a convenience copy: the individual files
below are the source of truth.

## Download everything at once

[`SDC2026_LuminaNusantara_Submission.zip`](SDC2026_LuminaNusantara_Submission.zip) (about 4.4 MB)

Contains the proposal, the technical declaration, the slide deck, the Replit proof and this
folder's README.

## Files

| File | What it is | Pages / slides |
| --- | --- | --- |
| [`SDC2026_LuminaNusantara_Preliminary.pdf`](SDC2026_LuminaNusantara_Preliminary.pdf) | Phase 1 project proposal, filled into the official SDC template and signed 24 October 2026 | 9 pages |
| [`SDC2026_LuminaNusantara_TechDeclaration.pdf`](SDC2026_LuminaNusantara_TechDeclaration.pdf) | Technical and tools declaration, official template, signed 24 October 2026 | 11 pages |
| [`SDC2026_LuminaNusantara_SlideDeck.pptx`](SDC2026_LuminaNusantara_SlideDeck.pptx) | Preliminary-round deck | 12 slides |
| [`REPLIT PROOF OF USE.pdf`](REPLIT%20PROOF%20OF%20USE.pdf) | Historical screenshots of the Replit workspace (not proof of current access) | — |
| [`README.md`](README.md) | This index | — |

## Where it runs

| Host | URL |
| --- | --- |
| Replit (published, required) | <https://skill-radar-my-streamlit-app.replit.app> |
| Streamlit Community Cloud (backup) | <https://sdc2026-lumina-nusantara-65cnugvuxdle5dgp9ky3fs.streamlit.app> |


Plain-text version of every slide: [`team/DECK_TALKING_POINTS.md`](../team/DECK_TALKING_POINTS.md).

## The six required features, and where each one lives

| Feature | Code | Shown in the deck |
| --- | --- | --- |
| Skills profile intake | `app.py` (`screen_js_intake`), `src/cv.py` | slide 7 |
| AI-trend signal layer | `data/trends/`, `src/trends.py` | slides 6, 7, 9 |
| Future-role matching | `src/utils.py` (`rank`) | slides 7, 8 |
| Personalised pathway | `src/utils.py` (`pathway`), `data/courses.json` | slides 7, 11 |
| SDG mapping | `data/skills_sdg.json`, `src/utils.py` (`sdg_summary`) | slide 10 |
| Uncertainty handled | `src/utils.py` (scenario weights) | slides 7, 8 |

## Current numbers

- 54 skills, 45 roles, **60 verified course links covering all 54 skills**
- 54 automated tests
- Three languages: English, Bahasa Malaysia, 中文
- Live demo: <https://sdc2026-lumina-nusantara-65cnugvuxdle5dgp9ky3fs.streamlit.app>

Regenerate the ZIP with `python team/tools/build_bundle.py`.
