# Submission package

- `SDC2026_LuminaNusantara_Preliminary.pdf`: proposal filled into the **official SDC 2026 template** (9 pages), signed by the leader 24 October 2026.
- `SDC2026_LuminaNusantara_TechDeclaration.pdf`: declaration filled into the **official SDC 2026 template** (11 pages), source inventory included, signed 24 October 2026.
- `SDC2026_LuminaNusantara_SlideDeck.pptx`: existing 12-slide deck.
- `REPLIT PROOF OF USE.pdf`: historical evidence; not proof of current access or current deployed commit.
- `OWNER_ACTIONS.md`: remaining factual, account, signature and submission checks.

No GPU endpoint is used, so no RunPod runtime evidence is claimed. Video remains pending. Both documents were re-signed on 24 October 2026 after the rewrite. Complete the owner checklist before final submission.

## Current runtime addendum — 24 October 2026

The existing Replit project now runs the reviewed latest app in its real Linux
Preview. See [CONTENTS.md](CONTENTS.md) for exact repository/project/demo fields
and [the validation report](../docs/REPLIT_VALIDATION.md) for tested revisions and
scope. There is **no active public Replit deployment**; owner approval is required.
This addendum does not amend the signed PDFs or assert that historical screenshots
prove this run. Original binaries remain in the
[upstream submission folder](https://github.com/douyinlin/sdc2026-lumina-nusantara/tree/main/submission);
the Replit workspace intentionally imports runtime sources and text handoff only.

## Current ZIP download and reproducible build

The new 4.4 MB ZIP is delivered through the Replit download card / Library item
**SkillRadar 提交材料包**, not a nonexistent `submission/*.zip` in this workspace.
Its actual local path is
`generated-artifacts/submission/SDC2026_LuminaNusantara_Submission.zip`.
The old GitHub ZIP is a historical convenience copy, not the latest hosting declaration.

From the repository root, with the build-only `python-pptx` package installed:

```sh
python team/tools/build_bundle.py --fetch-originals
```

This explicitly downloads four public, commit-pinned binary originals, verifies
their SHA-256 digests, and stores them only in ignored
`generated-artifacts/submission-input/`. It uses the **current** three Markdown
indices from this workspace, not an old embedded README, and writes the new ZIP
to the actual output path above. It does not change or re-sign the PDFs.
Without network access, provide a directory containing the four original binaries
and current README/CONTENTS/OWNER_ACTIONS:

```sh
python team/tools/build_bundle.py --submission-dir generated-artifacts/submission-input
```

Running without either option requires all originals already present under
`submission/`, as in the full upstream checkout; the runtime-only workspace does
not include them. Do not upload the generated bundle to Git merely to make a link.
