# SDG mapping

**Track:** SDG 4, sub-target **4.4** — relevant skills for employment — with **8.5** (decent work and
equal pay) as the second target. Some skills also carry 9.5 (research and innovation) or 10.2
(inequality).

## How it is built

The mapping goes down to **skill level**, not role level. All 54 skills in the catalogue have one or
more targets in [`data/skills_sdg.json`](../data/skills_sdg.json), grouped by skill family:

| Skill family | Targets |
| --- | --- |
| Digital and data | 4.4, 9.c |
| Engineering and built environment | 4.4, 9.5 |
| Care and health | 4.4, 10.2 |
| Teaching and training | 4.4, 4.c |
| People, finance, management | 4.4, 8.5 |
| Operations and marketing | 4.4, 8.2 |

A role inherits the targets of the skills it requires. On the results page, each step of the learning
pathway shows the target its skill serves, so the SDG claim is attached to what the learner actually
studies — not to a logo on the slide.

## What it is not

**This is the team's own reading of the targets.** It is not an official UN, DOSM or WEF mapping, and
the interface labels it as such next to the chart. Contributing to a target is not the same as
measuring impact, and no impact figure is claimed anywhere in the product.

## Why 4.4

The brief's problem is a workforce that adopts AI faster than it trains for it (56% adoption against
26% formal training). 4.4 is the target about the skills people need to get and keep decent work, so
it is the honest fit; 8.5 covers what happens after reskilling — better work, equal pay.
