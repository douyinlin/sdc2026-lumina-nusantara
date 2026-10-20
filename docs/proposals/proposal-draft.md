# Proposal draft — Lumina Nusantara (Domain 1)

Copy-paste source for `SDC2026_LuminaNusantara_Preliminary.pdf` and
`SDC2026_LuminaNusantara_TechDeclaration.pdf`. Word counts are measured for the
English text between the markers (target limits in brackets).

---

## Section 1 — Team and Project Overview

| Field | Value |
| --- | --- |
| Team Name | Lumina Nusantara |
| Selected Domain | Domain 1 — The Aiversecity Future-Ready Workforce Domain |
| Selected SDG Track (1–17) | SDG 4 — Quality Education (sub-target 4.4, with 8.5) |
| Project / Solution Name | SkillRadar MY |
| Name (Leader) | DU YULIN |
| Email & Phone (Leader) | CYS2609009@xmu.edu.my / +60 11-1798 1756 |
| University Affiliation(s) | Xiamen University Malaysia |
| Number of Team Members | 5 |

---

## Section 2.1 — The Problem Context  `[≤250 words]`

<!-- BEGIN 2.1 -->
Malaysia's labour market is being reshaped faster than its training system can respond. 56% of Malaysian professionals already use AI tools at work, yet only 26% have received formal training in them (Hays Asia Salary Guide 2025), and the Ministry of Science, Technology and Innovation expects more than 600,000 workers to need reskilling within three to five years.

The people most exposed are rarely the loudest in this debate: a 34-year-old customer-service supervisor in Klang whose tasks are being automated one by one; a TVET graduate applying for entry roles that no longer exist; an L&D manager in a 200-person SME who must set next year's training budget without evidence of which roles will still be viable.

Three failures repeat. Workers cannot see which skills are rising, so they buy credentials that are already commoditised. Employers cannot translate AI trends into a training plan, so budgets default to generic soft-skills courses. And career guidance is a snapshot: a one-off skills assessment in a market that keeps moving, so the advice expires before the learner finishes the course.

The cost is economic and social — wasted tuition, slower wage growth, and widening gaps for older workers, women returning from care work, and rural learners who cannot reach premium bootcamps. Without a system that updates as AI advances and shows how each role connects to the SDGs, reskilling stays an expensive guess rather than a pathway out.
<!-- END 2.1 -->

---

## Section 2.2 — The Proposed AI Solution  `[≤300 words]`

<!-- BEGIN 2.2 -->
SkillRadar MY turns public AI and labour-market signals into a personal, auditable career plan in four steps.

Intake. A user answers a short questionnaire on role, years of experience, tools and interests, or uploads a CV that we parse into a normalised skill profile. Every skill maps to a shared taxonomy (O*NET / ESCO identifiers), so "customer support" and "client service" are comparable.

Trend layer. A scheduled job ingests public signals — WEF Future of Jobs indicators, O*NET skill updates, sampled public job postings and the HRD Corp course catalogue — into a versioned trend table. Each record stores its source URL, retrieval date and metric, and the interface exposes that provenance on every forecast, so anyone can see when the data changed and what moved.

Matching. For each candidate future role we compute an explainable score from four visible components: skill coverage, transferability of adjacent skills, demand trend and gap cost. The user sees the arithmetic and the exact missing skills, not a black box.

Pathway and scenarios. Missing skills are ordered into a week-by-week plan built from free or low-cost resources, each with a link and estimated hours. The ranking runs twice — moderate and fast AI disruption — so the user sees how robust a choice is. Every role and skill carries SDG tags (primary 4.4 and 8.5, with 5, 9 and 10 where relevant), making the sustainability contribution of the choice visible.

From the Phase 1 workshops we apply GenAI APIs for CV parsing and plain-language explanations, a relational schema for profiles, trends and courses, and cloud deployment: Replit for hosting and RunPod serverless GPUs for embeddings, so the prototype is genuinely online rather than a slide.
<!-- END 2.2 -->

---

## Section 3.1 — Conceptual Tech Stack  `[no word limit]`

**Stack**

| Layer | Technology | Why |
| --- | --- | --- |
| UI | Streamlit | Fast iteration, runs unchanged on Replit |
| Service layer | Python modules (`src/utils.py`) | Testable matching / pathway logic |
| Data | SQLite locally, Postgres (Supabase) on Replit | Versioned trend snapshots, profiles, courses |
| AI | RunPod Serverless + `sentence-transformers`; optional hosted LLM for explanation text | GPU embeddings, no key in the repo |
| Ingestion | Python scheduled job, JSON snapshots committed with `source_url` + `retrieved_at` | Auditability, offline fallback |
| Hosting | Replit Deployments | Live demo URL for judges |
| CI / tests | `python -m unittest` | Regression on score and pathway logic |

**System block diagram**

```
          ┌────────────────────────────┐
          │  Streamlit UI (Replit)     │
          │  profile · radar · plan    │
          └───────────┬────────────────┘
                      │
      ┌───────────────┼───────────────────┐
      │               │                   │
┌─────▼──────┐  ┌─────▼───────┐   ┌───────▼────────┐
│ Ingestion  │  │ Matching &  │   │ RunPod         │
│ job (cron) │  │ pathway     │   │ Serverless GPU │
│ WEF/O*NET/ │  │ engine      │   │ CV parse +     │
│ postings/  │  │ score, gap, │   │ embeddings     │
│ HRD Corp   │  │ SDG tags    │   └───────┬────────┘
└─────┬──────┘  └─────┬───────┘           │
      │               │                   │
┌─────▼───────────────▼───────────────────▼─────┐
│  SQLite / Postgres: trend_snapshots(source_url,│
│  retrieved_at) · skills · roles · courses ·    │
│  sdg_map · user_profiles                       │
└────────────────────────────────────────────────┘
```

**Sponsor-provided GenAI API or Cloud Platform:** Not used at this stage. The prototype runs on Replit and RunPod with our own accounts and open models; if SDC sponsor credits become available in Phase 2 we will move LLM explanation text onto the sponsor API and record it in the Technical Tools Declaration, Section 5.

---

## Section 3.2 — Design-Thinking & Deployment Strategy  `[≤200 words]`

<!-- BEGIN 3.2 -->
We ran the work as three short design cycles.

Empathise and define: five semi-structured interviews — one HR executive, one TVET lecturer, two working adults considering a switch, one final-year student — plus a review of Malaysian reskilling reports. The recurring sentence was "I don't know what to learn next, and I don't trust course adverts". We defined the job to be done as: in under ten minutes, understand which two or three roles are realistic for me and what the first step is.

Ideate and prototype: paper flows, then a clickable Streamlit prototype tested with the same five people; we cut features that needed data we could not source honestly.

Test and de-risk: the score is transparent by construction, every claim links to a dated source, and the RunPod dependency has a local fallback so a live demo cannot fail on stage.

Deployment: Replit runs the app and holds secrets; RunPod serves embeddings; a weekly snapshot job keeps trends current. Phase 2 adds the HR view and automatic re-planning.
<!-- END 3.2 -->

---

## Section 4 — Preliminary Environmental & SDG Impact Framework

| Metric Category | Your Response |
| --- | --- |
| **Target SDG Sub-Target(s)** | **4.4** — by 2030 substantially increase the number of youth and adults with relevant skills, including technical and vocational skills, for employment and entrepreneurship; **8.5** — achieve full and productive employment and decent work for all. Secondary: **4.3** (equal access to affordable technical and vocational training). |
| **Current Problem Baseline** | 56% of Malaysian professionals use AI tools at work but only **26%** have received formal training (Hays Asia Salary Guide 2025); **600,000+** workers need reskilling within 3–5 years (MOSTI); a learner currently needs on average **several weeks** of self-directed search across job boards and course catalogues before committing to a reskilling route (our five interviews: 3–8 weeks, median 4). |
| **Core Measurable KPI** | (1) **Minutes from profile to a ranked, sourced reskilling plan** (target ≤5 min, measured in-app); (2) **Top-3 relevance rate** — share of pilot users who rate at least one of the three recommended roles as "realistic for me" (5-point scale ≥4); (3) **Source coverage** — share of displayed recommendations carrying a source URL and retrieval date (must be 100%). |
| **Phase 2 Impact Target** | **70%** top-3 relevance across ≥30 pilot users; **≥40%** reduction in time-to-plan versus the 4-week baseline (to under 2 weeks of equivalent effort); **100%** of role and skill cards traceable to a dated public source; **≥60%** of pilot users complete step 1 of their pathway within 30 days. |

**Sources:** Hays Asia Salary Guide 2025; Ministry of Science, Technology and Innovation (MOSTI) reskilling estimate, as cited in the SDC Domain 1 brief; WEF *Future of Jobs Report*; O*NET database (U.S. Department of Labor); HRD Corp course directory.

> Note: baselines marked as estimates are from published reports or our own five-person interviews; the interview count is stated so judges can weigh it.

---

## Section 6 — IP & Originality Declaration

- **6.1 Pre-existing / prior-owned work:** No. All code, design and research was created during the SDC 2026 hackathon period.
- **6.2 Third-party code, datasets, or models:** Yes — declared below.

| Name | Type (code/dataset/model) | License |
| --- | --- | --- |
| Streamlit | code | Apache 2.0 |
| O*NET database | dataset | CC BY 4.0 (attribution given in-app) |
| WEF Future of Jobs indicators | dataset | Public report, cited |
| `sentence-transformers` (all-MiniLM-L6-v2) | model | Apache 2.0 |
| RunPod Python SDK | code | Apache 2.0 |
| HRD Corp course catalogue | dataset | Public directory, cited |

- **6.3 Employment-related IP conflicts:** No. No team member is bound by an agreement that could claim ownership of this work.

---

## Section 7 — Declaration

Team leader: DU YULIN. Signature: ____________________  Date: 2026-10-__

---

## Technical Declaration — content mapping

| Tech-declaration field | What to enter |
| --- | --- |
| 1. Team / project / leader / email+phone / university | As Section 1 above |
| 1. Live Prototype URL · Code Repository URL | Your Replit deployment URL · your public GitHub URL |
| 2.1 System architecture (≤200 words) | Condensed version of Section 3.1 above + same block diagram |
| 2.2 Languages / frameworks / libraries | Python 3.11, Streamlit, pandas, sentence-transformers, runpod SDK, SQLite/Postgres driver |
| 3.1 External APIs | RunPod API — GPU inference — paid; (optional) LLM provider — explanation text — paid |
| 3.2 Cloud platforms | Replit — hosting + secrets — Deployments, Singapore; RunPod — serverless GPU — community cloud |
| 4.1 AI models | all-MiniLM-L6-v2 (pre-trained, Apache 2.0); optional LLM (pre-trained, provider terms) |
| 4.2 Datasets | O*NET (public, CC BY 4.0, no personal data); WEF indicators (public); synthetic demo profiles (synthetic, no personal data) |
| 4.3 AI-assisted dev tools | Yes — coding assistant + this planning assistant; extent "moderate"; ≤100-word review statement below |
| 5. Sponsor resources | No (unless you receive SDC credits — then declare them) |
| 6.1 Data handling (≤150 words) | Demo uses synthetic profiles only; no real CVs; CV text sent to RunPod endpoint is not persisted; no account, no cookies beyond session |
| 6.2 Limitations (≤150 words) | Trend data lag and source bias; embeddings mis-map niche skills; small pilot; mitigation: dated sources, human review, fallback parser |
| 7. Compliance | Tick all seven |

**4.3 review statement (≤100 words):** "AI assistants were used for scaffolding, boilerplate and wording, never for data or claims. Every generated block was read, tested or rewritten by a team member; matching logic, SDG tags and all statistics are hand-verified against the cited sources. Unit tests cover the scoring and pathway functions, and a reviewer other than the author checks each pull request before merge."
