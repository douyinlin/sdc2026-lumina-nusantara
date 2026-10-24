# Submission package — what is in here

Everything the judges need, in one place. The ZIP is a convenience copy: the individual files
below are the source of truth.

## Download everything at once

**Current bundle:** use the Replit download card / Library item **SkillRadar 提交材料包**.
It is generated at `generated-artifacts/submission/SDC2026_LuminaNusantara_Submission.zip`
in the workspace (ignored, not a GitHub-hosted download). To recreate it, follow
[README.md](README.md). The
[legacy ZIP on GitHub](https://github.com/douyinlin/sdc2026-lumina-nusantara/blob/73b4f344efeaaed281d7f1d0eac384f329897d04/submission/SDC2026_LuminaNusantara_Submission.zip)
is historical, not this new deliverable.

The legacy committed ZIP contains the proposal, declaration, deck, historical
proof and an older README. It does **not** establish the latest runtime status.
Use the current individual documents as the source of truth, or regenerate a
bundle with the updated index and validation report before submitting.

## Files

| File | What it is | Pages / slides |
| --- | --- | --- |
| [`SDC2026_LuminaNusantara_Preliminary.pdf`](https://github.com/douyinlin/sdc2026-lumina-nusantara/blob/73b4f344efeaaed281d7f1d0eac384f329897d04/submission/SDC2026_LuminaNusantara_Preliminary.pdf) | Phase 1 project proposal, filled into the official SDC template and signed 24 October 2026 | 9 pages |
| [`SDC2026_LuminaNusantara_TechDeclaration.pdf`](https://github.com/douyinlin/sdc2026-lumina-nusantara/blob/73b4f344efeaaed281d7f1d0eac384f329897d04/submission/SDC2026_LuminaNusantara_TechDeclaration.pdf) | Technical and tools declaration, official template, signed 24 October 2026 | 11 pages |
| [`SDC2026_LuminaNusantara_SlideDeck.pptx`](https://github.com/douyinlin/sdc2026-lumina-nusantara/blob/73b4f344efeaaed281d7f1d0eac384f329897d04/submission/SDC2026_LuminaNusantara_SlideDeck.pptx) | Preliminary-round deck | 12 slides |
| [`REPLIT PROOF OF USE.pdf`](https://github.com/douyinlin/sdc2026-lumina-nusantara/blob/73b4f344efeaaed281d7f1d0eac384f329897d04/submission/REPLIT%20PROOF%20OF%20USE.pdf) | Historical screenshots of the Replit workspace (not proof of current access) | — |
| [`README.md`](README.md) | This index | — |

Plain-text version of every slide: [`team/DECK_TALKING_POINTS.md`](https://github.com/douyinlin/sdc2026-lumina-nusantara/blob/73b4f344efeaaed281d7f1d0eac384f329897d04/team/DECK_TALKING_POINTS.md).

## Application and Replit links (verified 24 October 2026)

| Portal field | Value / status |
| --- | --- |
| Source repository | <https://github.com/douyinlin/sdc2026-lumina-nusantara> |
| Replit project / Run → Preview | <https://replit.com/@duyulin18/SkillRadar-MY-Streamlit-app> |
| Public app demo | <https://sdc2026-lumina-nusantara-65cnugvuxdle5dgp9ky3fs.streamlit.app> — anonymous app access verified, deployed SHA unknown |
| Replit public deployment URL | **Not available: deployment service reports no active deployment. Owner approval required before publishing.** |
| Current Replit evidence and runtime SHA | [Validation report](../docs/REPLIT_VALIDATION.md); screenshots captured from the actual Preview, separate from the historical PDF |

The development Preview was browser-tested, including its WebSocket connection.
It is not a permanent production address or a substitute for a public judging
URL. Do not invent a `replit.app` URL or claim that the old proof PDF verifies
this version. Portal submission and sponsor declarations require owner review;
no portal form has been submitted by this repair.

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
- 57 automated unit/page tests passed in the Replit workspace; see the report
- Three languages: English, Bahasa Malaysia, 中文
- Live demo: <https://sdc2026-lumina-nusantara-65cnugvuxdle5dgp9ky3fs.streamlit.app>

Regenerate the ZIP with `python team/tools/build_bundle.py --fetch-originals`;
see [README.md](README.md) for prerequisites and input/output paths.
