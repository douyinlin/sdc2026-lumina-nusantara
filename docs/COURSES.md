# The course catalogue

Every skill in the taxonomy has at least one course you can actually open. That is the rule the
catalogue is built on: a learner should never be told "you have a gap" and then handed nothing.

## What is in it

| | |
| --- | --- |
| Courses | **60** |
| Skills covered | **54 of 54** |
| Skills with more than one option | 5 (machine learning, excel, python, cybersecurity, digital marketing) |
| Providers | Coursera, edX, Alison, OpenLearn (Open University), freeCodeCamp, official documentation |
| Cost | Free, or free to audit with an optional paid certificate |

## How a row is written

Each record in [`data/courses.json`](../data/courses.json) stores the skill it teaches, the course
title, the provider, an estimated number of hours, the cost model, and a link that was opened and
checked on a stated date.

Two things are deliberately recorded as **not** verified:

- `duration_verified: false` — hours are the provider's headline estimate, not our measurement.
- Prices change; the cost column says "free to audit" rather than promising a price.

## When no course exists

If a skill has no verified course, the app does not invent one. It shows a labelled search route
instead ("no verified course yet") and links to the provider's search page, so the limitation is
visible rather than hidden. At the time of writing there are no such skills left.

## How the pathway uses it

The learning pathway orders the missing skills cheapest-first, then attaches the matching course to
each step. If a profile has no gaps at all, the app switches to an **advance** track and recommends
the next level for the skills the role leans on most — a full-coverage user still gets a plan.
