# Technical Stack — SkillRadar MY

Used by proposal Section 3.1 and Technical Declaration Section 2.1.

| Layer | Technology | Why |
| --- | --- | --- |
| UI | Streamlit | Fast iteration; runs unchanged on Replit |
| Service layer | Python modules (`src/utils.py`) | Testable matching / pathway / SDG logic |
| Data | SQLite locally, Postgres (Supabase) on Replit | Versioned trend snapshots, profiles, courses |
| AI | RunPod Serverless + `sentence-transformers`; optional hosted LLM for explanation text | GPU embeddings, no key in the repo |
| Ingestion | Python scheduled job, JSON snapshots with `source_url` + `retrieved_at` | Auditability and offline fallback |
| Hosting | Replit Deployments | Live demo URL for judges |
| Tests | `python -m unittest discover tests` | Regression on score and pathway logic |

## System block diagram

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

Sponsor-provided GenAI API or cloud platform: **not used** at this stage. The
prototype runs on Replit and RunPod with team accounts and open models.
