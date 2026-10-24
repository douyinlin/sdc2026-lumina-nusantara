# Where the data comes from

Three sources, kept separate on purpose. Each file in `data/trends/` stores its own source URL, its
publication date and a note on what it can and cannot support. Nothing is scraped at request time.

## 1. DOSM — advertised vacancies by occupation

**Source:** Department of Statistics Malaysia (DOSM), *Big Data Analytics: Job Market Insights*.
**Release used:** 2026 Q2, published 18 August 2026.
**Link:** <https://www.dosm.gov.my/portal-main/release-content/big-data-analytics-job-market-insights-q22026>

| Occupation group | 2026 Q2 offers | vs 2026 Q1 |
| --- | ---: | ---: |
| Professionals | 285,907 | −9.5% |
| Managers | 87,950 | −11.6% |
| Technicians and associate professionals | 86,512 | −8.0% |
| Advertising and marketing professionals | 40,640 | −15.7% |
| Managing directors and chief executives | 26,649 | −0.8% |
| Administrative associate professionals | 23,984 | −8.7% |
| Accountants and auditors | 22,067 | −11.0% |
| Software developers | 19,899 | −0.9% |
| **Total** | **555,509** | **−11.4%** |

**Scope:** this counts *job advertisements* by occupation group. It says nothing about skills, about
hiring quality, or about people. We transcribe the counts by hand and keep the link and the date in
`data/trends/dosm_q2_2026.json`. One quarter is not a trend.

## 2. Jobstreet by SEEK and Randstad — named skills

**Source:** both companies, as reported by The Edge Malaysia, published 4 February 2026.
**Link:** <https://theedgemalaysia.com/node/791561>
**File:** `data/trends/jobstreet_skills_2025.json` (8 named-skill signals).

**Scope:** named skills that the reporting calls out. It is a news article, not a dataset, so it
feeds direction only — no percentage is invented from it.

## 3. World Economic Forum — global outlook

**Source:** *The Future of Jobs Report 2025 — Skills Outlook*, published 7 January 2025.
**Link:** <https://www.weforum.org/publications/the-future-of-jobs-report-2025/3-skills-outlook>
**File:** `data/trends/wef_future_jobs_2025.json` (8 signals).

**Scope:** a **global employer survey**, not a Malaysian measurement. The interface labels it that way.
Some WEF skill labels do not exist in our catalogue; those rows are kept as `mapping_kind: proxy` or
`unmapped` rather than silently dropped.

## How the three become a score

The evidence source is a visible switch in the app: the same profile can be ranked on the Malaysian
article or on the WEF forecast, and the robustness table shows where a role holds under both. The
trend input is a 50/50 blend of the curated role signal and the chosen snapshot, so one source can
never dominate a recommendation.

## What we do not claim

- No Malaysian skill-level measurement — DOSM reports occupations, not skills.
- No real-time data: these are dated snapshots, updated by a reviewed import command.
- No scraping and no LLM reading the news: every row is transcribed or mapped by a person.
