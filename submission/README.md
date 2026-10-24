# Submission package

Everything a reviewer needs, in one folder. The ZIP below is a convenience copy; the individual
files are the source of truth.

- [`SDC2026_LuminaNusantara_Preliminary.pdf`](SDC2026_LuminaNusantara_Preliminary.pdf) — proposal in
  the **official SDC 2026 template**, 9 pages, signed by the team leader on 24 October 2026.
- [`SDC2026_LuminaNusantara_TechDeclaration.pdf`](SDC2026_LuminaNusantara_TechDeclaration.pdf) —
  technical and tools declaration in the official template, 11 pages, signed 24 October 2026.
- [`SDC2026_LuminaNusantara_SlideDeck.pptx`](SDC2026_LuminaNusantara_SlideDeck.pptx) — preliminary
  round deck, **20 slides**: main deck plus three synthetic demo profiles.
- [`REPLIT PROOF OF USE.pdf`](REPLIT%20PROOF%20OF%20USE.pdf) — screenshots of the Replit workspace
  during development.
- [`SDC2026_LuminaNusantara_Submission.zip`](SDC2026_LuminaNusantara_Submission.zip) — the files
  above plus this README, packed for a single download.

## Where it runs

| Host | URL |
| --- | --- |
| **Replit (published — primary)** | <https://skill-radar-my-streamlit-app.replit.app> |
| Replit workspace (private to the team) | <https://replit.com/@duyulin18/SkillRadar-MY-Streamlit-app> |
| Streamlit Community Cloud (backup, currently behind a sign-in wall) | <https://sdc2026-lumina-nusantara-65cnugvuxdle5dgp9ky3fs.streamlit.app> |
| Product demo video (YouTube) | <https://youtu.be/wCsUDKMBIfs> |
| Code repository | <https://github.com/douyinlin/sdc2026-lumina-nusantara> |

The Replit deployment is the one to use. It answers on `/_stcore/health` with `ok` and needs no
login; the first visit after a quiet period can take 20–30 seconds to wake.

## Declarations at a glance

- **RunPod:** not used. There is no GPU endpoint anywhere in the project; parsing and scoring are
  local Python. This is stated in the Technical Declaration, section 5.
- **Sponsor technology:** the organisers clarified on 23 October that the required
  "API Premium sponsor technology" refers to **Replit and RunPod, if used**. This project is built
  and published on Replit (declared in Technical Declaration §3.2), so the sponsor confirmation on
  the submission form is accurate. RunPod is not used and no GPU endpoint is involved (§5).
- **Data:** public Malaysian labour-market sources, transcribed by hand with the source URL and
  release date stored next to each figure.
- **Profiles:** synthetic only. No real CV, name or contact detail appears in the demo material.
