# What the program does, and what the AI does

## The short version

The running application contains **no model**. It parses text with keywords, scores roles with five
weighted rules, and looks courses up in a curated catalogue. The same profile always produces the
same answer, and every point of the score can be traced to a line of code or a row of data.

AI tools (DeepSeek, GitHub Copilot, Codex, ChatGPT) were used **during development** — to draft code,
tests and copy. They are declared in the Technical Declaration, section 4.3.

## The scoring rule

```
score = 0.30 · skill coverage
      + 0.25 · role focus
      + 0.15 · transferability
      + 0.15 · demand trend
      + 0.15 · (1 − gap cost)
```

- **Skill coverage** — share of the role's required skills the profile already has.
- **Role focus** — how central those skills are to the role, not just how many.
- **Transferability** — whether a held skill counts partially for a missing one (a table of
  coefficients, not a guess at the moment of scoring).
- **Demand trend** — a 50/50 blend of the curated role signal and the chosen dated snapshot.
- **Gap cost** — how expensive the missing skills are to close.

The fast-disruption scenario re-weights the trend input to **0.35** and penalises flat or declining
roles. That is a stated assumption, shown in the interface, not a hidden setting.

## Where each piece lives

| Piece | File |
| --- | --- |
| UI, flow, three personas | `app.py` |
| Scoring, ranking, pathway, SDG summary | `src/utils.py` |
| CV parsing (keywords + aliases, PDF text layer) | `src/cv.py` |
| Snapshot validation, import, signal strength | `src/trends.py` |
| Trilingual strings | `src/i18n.py`, `data/i18n/` |
| Roles, skills, courses, SDG crosswalk | `data/*.json` |

## What is deliberately not here

- No LLM call, no vector search, no embedding index at request time.
- No database: state lives in the Streamlit session.
- No GPU and no RunPod endpoint anywhere in the project.

Semantic CV parsing and a vector index are on the roadmap, labelled as planned in the deck.
