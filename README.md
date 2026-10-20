# SkillRadar MY — AI Skills & Career Radar for Malaysia

> **Lumina Nusantara · SDC 2026 Hackathon · Domain 1 — The Aiversecity Future-Ready Workforce Domain · SDG 4**

A working web app that takes a Malaysian worker from "who I am today" to "where I
can be in the AI era", with every forecast traceable to a dated public source and
every role mapped to the UN SDGs.

---

## 1. Team Information

| Field | Details |
| --- | --- |
| **Team Name** | Lumina Nusantara |
| **Team Domain** | Domain 1 — The Aiversecity Future-Ready Workforce Domain |
| **SDG Track (1–17)** | SDG 4 — Quality Education (sub-target 4.4, with 8.5) |
| **Team Leader** | DU YULIN |
| **University** | Xiamen University Malaysia (XMUM) |
| **Number of Members** | 5 |

## 2. Links

| Resource | Link |
| --- | --- |
| GitHub Repository | https://github.com/douyinlin/sdc2026-lumina-nusantara |
| Replit Project | `<TODO — after Replit import>` |
| Live Demo | `<TODO — after Replit Deploy>` |
| RunPod Endpoint | `<TODO — after RunPod endpoint is deployed>` |
| Slide Deck | `<TODO>` |
| Demo Video | `<TODO>` |

## 3. Overview

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
| 1 | Skills profile intake | Questionnaire + CV parsing into a shared skill taxonomy (O*NET/ESCO identifiers) |
| 2 | AI-trend signal layer | Scheduled ingestion of public sources; every forecast exposes source URL and retrieval date |
| 3 | Future-role matching | Explainable score decomposed into coverage, transferability, demand trend and gap cost |
| 4 | Personalised reskilling pathway | Week-by-week plan with estimated hours and free / HRD Corp-claimable resources |
| 5 | SDG mapping | Each role and skill tagged to at least one SDG, plus a personal contribution view |
| 6 | Handling uncertainty | Moderate vs fast AI-disruption scenarios, labelled as estimates |

### Tech Stack

See [`docs/tech-stack.md`](docs/tech-stack.md) for the full table and block diagram.

| Layer | Technology |
| --- | --- |
| Frontend | Streamlit (Python) |
| Backend | Python service modules (`src/`) |
| Database | SQLite locally, Postgres (Supabase) when hosted |
| AI / Compute | RunPod Serverless — embeddings and LLM inference |
| Hosting / Dev | Replit (Deployments) |

## 4. Project Structure

```
.
├── docs/                          # Documentation
│   ├── proposals/                 # Proposal drafting material
│   │   └── proposal-draft.md      # All answers for the two submission PDFs
│   ├── screenshots/               # UI screenshots for the README and video
│   ├── tech-stack.md              # Stack table + system block diagram
│   ├── GitHub上传步骤.md            # How we push to GitHub
│   └── README.md                  # Documentation index
├── data/                          # Trend snapshots (source_url + retrieved_at)
├── runpod/
│   └── handler.py                 # RunPod serverless handler (GPU workload)
├── src/
│   ├── main.py                    # Application entry point
│   └── utils.py                   # Matching, pathway and SDG engine
├── submission/                    # Required submission documents
│   ├── SDC2026_LuminaNusantara_Preliminary.pdf
│   ├── SDC2026_LuminaNusantara_TechDeclaration.pdf
│   ├── REPLIT PROOF OF USE.pdf
│   └── RUNPOD PROOF OF USE.pdf
├── tests/
│   └── test_utils.py              # Unit tests
├── .env.example
├── .gitignore
├── .replit
├── LICENSE
├── requirements.txt
├── 任务清单.md                     # Team checklist (Chinese)
└── README.md
```

> The three PDFs currently in `submission/` are the **blank official templates**.
> Replace them with the filled versions before submitting.

## 5. How to Run

### Option 1 — Run on Replit (Recommended)

1. Create a Repl → **Import from GitHub** → select this repository.
2. Open **Secrets** (🔒) and add the variables from `.env.example`.
3. Click **Run**. `.replit` starts `python src/main.py`.

### Option 2 — Run Locally

```bash
git clone https://github.com/douyinlin/sdc2026-lumina-nusantara.git
cd sdc2026-lumina-nusantara
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env           # then fill in your values
python src/main.py
```

### Run Tests

```bash
python -m unittest discover tests
```

## 6. How We Use Replit *(Required)*

- **Development:** the app runs directly from this repository inside Replit; no local setup needed by teammates.
- **Hosting:** deployed with Replit Deployments at the Live Demo link above.
- **Secrets:** `RUNPOD_API_KEY` and `RUNPOD_ENDPOINT_ID` live in Replit Secrets and are never committed.

📄 Proof of use: [`submission/REPLIT PROOF OF USE.pdf`](submission/REPLIT%20PROOF%20OF%20USE.pdf)

## 7. How We Use RunPod *(Required)*

- **Workload:** CV text parsing and sentence embeddings for skill matching run on a RunPod GPU serverless endpoint.
- **Setup:** `runpod/handler.py` is deployed as a **RunPod Serverless Endpoint**.
- **Integration:** the app calls the endpoint with `RUNPOD_API_KEY` and `RUNPOD_ENDPOINT_ID`; if the endpoint is unavailable it falls back to a local rule-based parser so the demo never breaks.

```bash
curl -X POST https://api.runpod.ai/v2/$RUNPOD_ENDPOINT_ID/runsync \
  -H "Authorization: Bearer $RUNPOD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"input": {"text": "5 years customer service team lead, Excel, Zendesk"}}'
```

📄 Proof of use: [`submission/RUNPOD PROOF OF USE.pdf`](submission/RUNPOD%20PROOF%20OF%20USE.pdf)

## 8. Challenges & Learnings

- **Trustworthy, updatable trend data** is the hardest part: sources change format, and hard-coded lists are explicitly disqualified. We version every ingestion run, store source and retrieval date, and fall back to the most recent snapshot.
- **Avoiding invented jobs and courses**: the LLM only phrases explanations; roles, skills and courses come from curated seed tables with URLs.
- **Explaining a score** is harder than computing one — we expose the four weighted components in the UI.

## 9. Future Improvements

- [ ] Employer / HR view: team-level skills-gap heatmap and reskilling plan.
- [ ] Automatic re-planning when a new trend snapshot lands.
- [ ] Multi-language UI (English, Bahasa Malaysia, 中文) and low-bandwidth mode.
- [ ] Fairness checks across age, gender and background.

## 10. Team

| Name | Role | GitHub |
| --- | --- | --- |
| DU YULIN | Team Lead / Product & AI | [@douyinlin](https://github.com/douyinlin) |
| `<member 2>` | Frontend / UX | `<TODO>` |
| `<member 3>` | Data & trend pipeline | `<TODO>` |
| `<member 4>` | Matching & evaluation | `<TODO>` |
| `<member 5>` | Docs, demo video, submission | `<TODO>` |

## 11. Submission Checklist

- [x] Team name, domain (Domain 1) and SDG track filled in
- [ ] Slide deck link added
- [ ] Demo video link added
- [ ] Replit used, with proof of use in `submission/`
- [ ] RunPod used, with proof of use in `submission/`
- [ ] Submission template completed in `submission/`
- [ ] "How to Run" steps verified
- [ ] No API keys or secrets committed to the repository

## License

This project is licensed under the [Apache License 2.0](LICENSE).
