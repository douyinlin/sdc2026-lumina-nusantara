# SkillRadar MY — AI Skills & Career Radar for Malaysia

> **Lumina Nusantara · SDC 2026 Hackathon · Domain 1 — The Aiversecity Future-Ready Workforce Domain · SDG 4**

A working web app that takes a Malaysian worker from "who I am today" to "where I
can be in the AI era", with every forecast traceable to a dated public source and
every role mapped to the UN SDGs.

**Live demo:** https://sdc2026-lumina-nusantara-65cnugvuxdle5dgp9ky3fs.streamlit.app

> [!IMPORTANT]
> ### 📁 Submission Documents 提交文件
>
> The two signed submission PDFs, the Replit proof of use and the online demo guide are in the
> [submission/](submission) folder. Start with [submission/README.md](submission/README.md).
>
> 两份已签署的提交 PDF、Replit 使用证明与在线演示说明都在 [submission/](submission) 目录内。
> 请先读 [submission/README.md](submission/README.md)。

---

## Team Information

| Field | Details |
| --- | --- |
| **Team Name** | Lumina Nusantara |
| **Team Domain** | Domain 1 — The Aiversecity Future-Ready Workforce Domain |
| **SDG Track (1–17)** | SDG 4 — Quality Education (sub-target 4.4, with 8.5) |
| **Team Leader** | DU YULIN |
| **University** | Xiamen University Malaysia (XMUM) |
| **Number of Members** | 5 |

## Links

| Resource | Link |
| --- | --- |
| GitHub Repository | https://github.com/douyinlin/sdc2026-lumina-nusantara |
| Replit Project | https://replit.com/@duyulin18 |
| **Live Demo** | https://sdc2026-lumina-nusantara-65cnugvuxdle5dgp9ky3fs.streamlit.app |
| RunPod Endpoint | Not used — the app runs no GPU endpoint (see Technical Declaration §5) |
| Slide Deck | `<TODO>` |
| Demo Video | `<TODO>` |

---

## Overview

### Problem

Malaysian workers cannot see which skills are rising, so they invest in credentials
that are already commoditised; employers cannot translate AI trends into a training
plan; and career guidance is a static snapshot in a market that keeps moving. 56% of
Malaysian professionals already use AI tools at work, yet only 26% have received
formal training (Hays Asia Salary Guide 2025), and more than 600,000 workers are
expected to need reskilling within three to five years (MOSTI).

### Solution

SkillRadar MY turns public AI and labour-market signals into a personal, auditable
career plan: a normalised skills profile, a versioned trend layer that always shows
its source and retrieval date, an explainable role-match score, an ordered reskilling
pathway built from free or low-cost resources, an SDG tag on every role and skill,
and two disruption scenarios so the user sees how robust each choice is.

### Key Features

| # | Must-have feature | How we deliver it |
| --- | --- | --- |
| 1 | Skills profile intake | Questionnaire + synthetic CV parsing into a shared skill taxonomy |
| 2 | AI-trend signal layer | Versioned trend snapshot; every forecast exposes source URL and retrieval date |
| 3 | Future-role matching | Explainable score decomposed into coverage, transferability, demand trend and gap cost |
| 4 | Personalised reskilling pathway | Ordered learning plan with estimated hours, free / HRD Corp-claimable resources |
| 5 | SDG mapping | Each role and skill tagged to at least one SDG, plus a personal contribution view |
| 6 | Handling uncertainty | Moderate vs fast AI-disruption scenarios, explicitly labelled as estimates |

### Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend | Streamlit (Python) |
| Backend | Python service modules (`src/`) |
| Database | SQLite locally, Postgres when hosted |
| AI / Compute | No external AI service — deterministic rule engine runs in-app |
| Hosting / Dev | Streamlit Community Cloud; Replit workspace |

---

## Project Structure

```text
.
|-- app.py                  # Streamlit entry point (the demo)
|-- submission/             # ALL required submission documents
|   |-- SDC2026_LuminaNusantara_Preliminary.pdf
|   |-- SDC2026_LuminaNusantara_TechDeclaration.pdf
|   |-- REPLIT PROOF OF USE.pdf
|   `-- RUNPOD PROOF OF USE.pdf
|-- docs/
|   `-- architecture.png    # System block diagram
|-- src/                    # Engine: demo UI, matching, pathway, SDG
|-- data/                   # Synthetic profiles, sample CV, trend snapshot
|-- tests/                  # 13 unit tests
|-- runpod/                 # Optional RunPod handler (not used by the demo)
|-- team/                   # Team-only material (not part of the submission)
|-- LICENSE                 # Apache License 2.0
|-- requirements.txt
`-- README.md
```

---

## How to Run

### Option 1 — Use the live demo (recommended)

Open https://sdc2026-lumina-nusantara-65cnugvuxdle5dgp9ky3fs.streamlit.app

No installation required. Free-tier instances sleep when idle; the first load can
take 30–60 seconds.

### Option 2 — Run locally

```bash
git clone https://github.com/douyinlin/sdc2026-lumina-nusantara.git
cd sdc2026-lumina-nusantara
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt
streamlit run app.py
```

Then open `http://localhost:8501`.

### Run Tests

```bash
python -m unittest discover tests
```

---

## How We Use Replit *(Required)*

Replit is our shared development workspace: all five members work on the same
running prototype without any local setup, and the repository is imported directly
from GitHub so `main` stays the single source of truth.

- **Development:** the app runs from this repository inside Replit; `.replit` starts
  `python -m streamlit run app.py` on port 5000.
- **Secrets:** any API keys live in Replit Secrets and are never committed.
- **Hosting:** the public live demo is served by Streamlit Community Cloud, which
  auto-deploys every push to `main`, so judges always see the latest build.

Proof of use: [`submission/REPLIT PROOF OF USE.pdf`](submission/REPLIT%20PROOF%20OF%20USE.pdf)

## On RunPod

This application does **not** call a RunPod endpoint. CV parsing is a local regex/alias extractor and every score is a deterministic rule set in `src/utils.py`, so the demo needs no GPU and no API key. `runpod/handler.py` is kept only as an optional deployment path for a future version and is not on the request path. This is declared in the Technical Tools Declaration, Section 5.

---

## Challenges & Learnings

- **Trustworthy, updatable trend data** is the hardest part: sources change format,
  and hard-coded lists are explicitly disqualified. Every ingestion run is versioned
  with its source URL and retrieval date.
- **Avoiding invented jobs and courses**: any language model only phrases
  explanations; roles, skills and courses come from curated tables with URLs.
- **Explaining a score** is harder than computing one — the four weighted components
  are exposed in the UI so a non-expert can audit the ranking.
- **Keeping the demo honest**: synthetic data only, no real CVs, and a visible
  reminder that predictions are estimates rather than facts.

## Future Improvements

- [ ] Employer / HR view: team-level skills-gap heatmap and reskilling plan.
- [ ] Automatic re-planning when a new trend snapshot lands.
- [ ] Verified course catalogue with real durations, links and fees.
- [ ] Fairness checks across age, gender and background.

## Team

| Name | Role |
| --- | --- |
| DU YULIN | Team Lead / Core development & submission |
| GAO TANGLINYUE | UI design & bug testing |
| ZHENG QUANYING | UI design & bug testing |
| WU ZHUOLI | Core development (matching & pathway engine) |
| ZHANG BORAN | Core development & documentation |

---

## Submission Checklist

- [x] Team name, domain (Domain 1) and SDG track filled in
- [ ] Slide deck link added
- [ ] Demo video link added
- [x] Replit used, with proof of use in `submission/`
- [ ] RunPod — **not used**; CV parsing and scoring run locally in the app
- [x] Submission template completed in `submission/`
- [x] "How to Run" steps verified
- [x] No API keys or secrets committed to the repository

## License

This project is licensed under the [Apache License 2.0](LICENSE).
