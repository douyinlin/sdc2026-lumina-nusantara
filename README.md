# SkillRadar MY — AI Skills & Career Radar for Malaysia

> **Lumina Nusantara · SDC 2026 Hackathon · Domain 1 — The Aiversecity Future-Ready Workforce Domain · SDG 4**

A working web app that takes a Malaysian worker from "who I am today" to "where I
can be in the AI era", with every forecast traceable to a dated public source and
every role mapped to the UN SDGs.

**Live demo (Replit):** https://skill-radar-my-streamlit-app.replit.app

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
| Streamlit Cloud (backup, currently behind a sign-in wall) | https://sdc2026-lumina-nusantara-65cnugvuxdle5dgp9ky3fs.streamlit.app |
| Replit workspace (private) | https://replit.com/@duyulin18/SkillRadar-MY-Streamlit-app |
| **Live Demo** | https://skill-radar-my-streamlit-app.replit.app |
| RunPod Endpoint | Not used — the app runs no GPU endpoint (see Technical Declaration §5) |
| Submission bundle | [SDC2026_LuminaNusantara_Submission.zip](submission/SDC2026_LuminaNusantara_Submission.zip) (all files, 4.4 MB) |
| Slide Deck | [SDC2026_LuminaNusantara_SlideDeck.pptx](submission/SDC2026_LuminaNusantara_SlideDeck.pptx) |
| Demo Video (6:34) | https://youtu.be/wCsUDKMBIfs |

---

## Presentation material

| Item | File | What it is |
| --- | --- | --- |
| Preliminary deck | [SDC2026_LuminaNusantara_SlideDeck.pptx](submission/SDC2026_LuminaNusantara_SlideDeck.pptx) | 20 slides, the deck shown to judges |
| Product demo video | [YouTube, 6:34](https://youtu.be/wCsUDKMBIfs) | the recorded walkthrough |

Data, method and validation pages: [docs/DATA.md](docs/DATA.md) · [docs/TECH.md](docs/TECH.md) · [docs/VALIDATION.md](docs/VALIDATION.md).

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
pathway built from free or low-cost resources, SDG tags at both role and skill level,
and two disruption scenarios so the user sees how robust each choice is.

### Key Features

| # | Must-have feature | How we deliver it |
| --- | --- | --- |
| 1 | Skills profile intake | Questionnaire + synthetic CV parsing into a shared skill taxonomy |
| 2 | AI-trend signal layer | Separate Malaysia job-offering observations, reported named-skill signals and global WEF forecasts; each source shows its date and link |
| 3 | Future-role matching | Explainable score decomposed into skill coverage, role focus, transferability, demand trend and gap cost |
| 4 | Personalised reskilling pathway | Sequential learning plan with linked course records (60 links, 54 of 54 catalogue skills); skills without a verified course get a search route instead of an invented one |
| 5 | SDG mapping | Role-level SDG tags, plus a skill-to-target crosswalk (`data/skills_sdg.json`) shown on the results page; clearly labelled as the team's own reading of the 2030 Agenda |
| 6 | Handling uncertainty | Moderate vs fast AI-disruption scenarios, explicitly labelled as estimates |

### Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend | Streamlit (Python) |
| Backend | Python service modules (`src/`) |
| Database | No database in the current UI; local JSON files and session state |
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
|-- docs/
|   `-- architecture.png    # System block diagram
|-- src/                    # Engine: demo UI, matching, pathway, SDG
|-- data/                   # Synthetic profiles, sample CV, dated trend source snapshots
|-- tests/                  # unit tests
|-- runpod/                 # Optional RunPod handler (not used by the demo)
|-- team/                   # Team working material; tracked files are public if the repository is public
|-- LICENSE                 # Apache License 2.0
|-- requirements.txt
`-- README.md
```

---

## How to Run

### Option 1 — Use the live demo (recommended)

Open https://skill-radar-my-streamlit-app.replit.app

No installation required. The deployment runs on Replit Autoscale, so the first
visit after a quiet period can take 20–30 seconds to wake.

<sub>Backup host: https://sdc2026-lumina-nusantara-65cnugvuxdle5dgp9ky3fs.streamlit.app
(Streamlit Community Cloud — currently behind a sign-in wall, so use the Replit link above.)</sub>

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

The project is **built and published on Replit**.

- **Published app:** <https://skill-radar-my-streamlit-app.replit.app> — public, no login needed.
  The deployment runs on Replit Autoscale, so the first visit after a quiet period can take
  20–30 seconds to wake.
- **Workspace:** <https://replit.com/@duyulin18/SkillRadar-MY-Streamlit-app> (private to the team).
- **Run configuration:** `.replit` starts `python -m streamlit run app.py` on port 5000, bound to
  `0.0.0.0` in headless mode, so Replit's proxy reaches it.
- **Secrets:** none are required — the app calls no external API and needs no key or GPU.
- **Second host:** the Streamlit Community Cloud instance in the links table stays online as a
  backup and is the one used in the demo video.

Replit usage evidence is also kept as screenshots:
[`submission/REPLIT PROOF OF USE.pdf`](submission/REPLIT%20PROOF%20OF%20USE.pdf).

## On RunPod

This application does **not** call a RunPod endpoint. CV parsing is a local regex/alias extractor and every score is a deterministic rule set in `src/utils.py`, so the demo needs no GPU and no API key. `runpod/handler.py` is kept only as an optional deployment path for a future version and is not on the request path. This is declared in the Technical Tools Declaration, Section 5.

---

## Trend sources and scoring

The app keeps three kinds of evidence distinct:

- **Malaysia observations:** DOSM online job offerings for 2026 Q1 and Q2, stored in
  `data/trends/dosm_q2_2026.json` ([Q2 release](https://www.dosm.gov.my/portal-main/release-content/big-data-analytics-job-market-insights-q22026),
  [Q1 release](https://www.dosm.gov.my/portal-main/release-content/big-data-analytics-job-market-insights-q12026)).
  These are advertised offerings by occupation group, not all vacancies and not
  skill-level counts.
- **Reported skill signals:** the [2025 JobStreet / Randstad report](https://theedgemalaysia.com/node/791561)
  names skill areas but does not publish comparable percentages for each skill.
- **Global forecast:** WEF's [*Future of Jobs Report 2025*](https://www.weforum.org/publications/the-future-of-jobs-report-2025/3-skills-outlook)
  describes employer expectations through 2030. It is not a Malaysia-specific
  measurement. Only aligned or explicitly mapped skills in the app's catalogue
  affect ranking; unmapped forecast items are shown as context.

Qualitative rising and declining directions use a fixed ±0.7 score signal (stable is
0.0). This is a prototype ranking heuristic, not a statistic published by DOSM, WEF
or JobStreet. Source snapshots are maintained manually; there is no automated scraping job.
The validated manual-import workflow below preserves the previous valid snapshot
when validation fails. Source claims have not been reverified during this repair.

## Challenges & Learnings

- **Trustworthy, updatable trend data** is the hardest part: official occupation counts,
  reported skill names and global forecasts measure different things, so we keep them
  separate and label every proxy.
- **Avoiding invented jobs and courses**: roles, skills and courses come from
  curated tables with URLs; the live app does not call a language model.
- **Explaining a score** is harder than computing one — the five weighted components
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
### Repository access

The code lives at <https://github.com/douyinlin/sdc2026-lumina-nusantara>. Accounts with
access, checked through the GitHub API on 23 October 2026:

| GitHub account | Repository role |
| --- | --- |
| `douyinlin` | Admin (team leader) |
| `Lover-Leo` | Write |
| `bojunzw` | Write |
| `Lynnyue826` | Write |
| `ZHENGQUANYING` | Write |

The team keeps the mapping between these accounts and the five registered members; this
table records access, not identity.

---

## Submission Checklist

- [x] Team name, domain (Domain 1) and SDG track filled in
- [x] Slide deck added (`submission/SDC2026_LuminaNusantara_SlideDeck.pptx`, 20 slides), also inside the bundle ZIP
- [x] Demo video link added (YouTube, 6:34)
- [x] Replit used, with proof of use in `submission/`
- **RunPod:** not used — CV parsing and scoring run locally; the project has no GPU endpoint (declared in the Technical Declaration §5). This is a statement of fact, not a checklist item.
- [x] Revised submission PDFs reviewed and signed by the leader on 24 October 2026 (signature block on the last page of each)
- [x] "How to Run" steps verified
- [x] No API keys or secrets committed to the repository

## License

This project is licensed under the [Apache License 2.0](LICENSE).
