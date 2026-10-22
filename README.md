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
pathway built from free or low-cost resources, role-level SDG tags (skill-level reasons remain incomplete),
and two disruption scenarios so the user sees how robust each choice is.

### Key Features

| # | Must-have feature | How we deliver it |
| --- | --- | --- |
| 1 | Skills profile intake | Questionnaire + synthetic CV parsing into a shared skill taxonomy |
| 2 | AI-trend signal layer | Separate Malaysia job-offering observations, reported named-skill signals and global WEF forecasts; each source shows its date and link |
| 3 | Future-role matching | Explainable score decomposed into skill coverage, role focus, transferability, demand trend and gap cost |
| 4 | Personalised reskilling pathway | Sequential learning plan with linked course records; duration provenance and missing resources are explicit |
| 5 | SDG mapping | Role-level SDG tags and explanatory context; per-skill mapping remains incomplete |
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

Existing Replit usage evidence is preserved in `submission/`. This repaired local
version has **not** been run or deployed on Replit during this change. The link above
is an account profile, not verified proof of the current project deployment.

- **Development:** the app runs from this repository inside Replit; `.replit` starts
  `python -m streamlit run app.py` on port 5000.
- **Secrets:** any API keys live in Replit Secrets and are never committed.
- **Hosting:** the public live demo is served by Streamlit Community Cloud, which
  deployment settings and the deployed commit must be checked by the team.

Proof of use: [`submission/REPLIT PROOF OF USE.pdf`](submission/REPLIT%20PROOF%20OF%20USE.pdf)

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


## Repair and validation — 2026-10-22

Worker targets default to all fields and use separate state from graduate study
fields. Skills are deduplicated on both sides of weighted and count-based coverage.
Coverage is not a hiring probability. Scoring weights, transfer coefficients and
scenario assumptions are team heuristics, not observed hiring outcomes.

Skills, selected field and evidence/scenario affect matching. Weekly study hours
change duration. Work experience, urgency, budget, degree level, internship months
and graduation year are recorded only; they do not affect scoring or course filters.

Study steps are sequential. For a positive recorded course duration, weeks are
`ceil(course hours / weekly study hours)`. Existing catalogue hours are explicitly
labelled unverified estimates. A future verified record must include
`duration_verified: true` and `duration_source_url`. Missing/invalid hours use the
original team assumption (`round(skill cost * 6)` weeks at 8 hours/week), labelled
as a team estimate. Total weeks sum rounded step durations. Source verification
and course access/fees remain team tasks. Completing a step is a hypothetical
skill acquisition; the highest-scoring role after the plan may change.

### Validated manual trend update

1. Read the original source linked in the existing WEF/Jobstreet JSON. Review its
   scope, date, skill direction and any taxonomy mapping. This is a human review,
   not an automatic claim that a page was fetched or checked.
2. Prepare a JSON file outside the repository, preserving the existing schema.
   Include `source`, HTTPS `source_url`, `published`, `retrieved_at`,
   `extraction_note`, and non-empty `skill_signals` with `skill`, `direction`,
   `evidence`. Proxy mappings must have `mapping_note`. Do not invent percentages.
3. Validate, then import (replace the example input path with your reviewed file):

```powershell
python -m src.trends wef "C:\path\reviewed-wef.json" --check
python -m src.trends wef "C:\path\reviewed-wef.json"
# For the other source, replace wef with jobstreet.
```

Successful imports atomically replace only the selected source, keeping an ignored
`.json.bak` of the previous valid snapshot. Validation failure leaves it unchanged.
Ignored per-source `.*-import-status.json` records the attempt; the UI warns after
failed imports. A missing/corrupt active snapshot produces an explicit error,
not a simulated replacement. Re-run the page after importing. Review `git diff`
and the original evidence before manually committing. DOSM occupation panels
remain separate from skill scoring; update those manually and review their diff.

### Reproduce checks and run

```powershell
python -m pip install -r team/dev-env/requirements-dev.txt
python -m unittest discover tests -v
python tests/check_cv_intake.py
python -m pip check
python -m mypy --config-file team/dev-env/pyproject.toml
python -m streamlit run app.py --server.headless true
# In a second terminal, using an installed Chrome:
python tests/check_post_selection_ui.py --url http://localhost:8501 --browser "C:\Program Files\Google\Chrome\Application\chrome.exe" --output test-results/browser
```

There is no separate frontend build: Streamlit runs the Python application.
For hosted startup use `python -m streamlit run app.py --server.address 0.0.0.0
--server.port 5000 --server.headless true` on one line. `.replit` already includes
build/install and startup settings; importing and running this commit on the
team's Replit account is still required. No API key is needed. `.env` is not loaded
by the app; `PORT` is used only by the `.replit` deployment shell command. RunPod
variables are reserved for the disconnected optional experiment.

Validation performed locally: unit/integration tests, dependency consistency,
mypy and a Chrome worker flow with field selection, edited synthetic skills,
study hours, evidence/scenario switching and SDG display. See
`team/DEVELOPMENT_LOG.md` for actual results and remaining limitations.
