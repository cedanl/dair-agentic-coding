---
name: ship
description: Land a code change safely — review, fix, commit, push — with guardrails that verify the change actually works first. Use when finishing a piece of work that needs to land on a branch.
---

# ship

Land a change safely: verify the work actually runs before calling it done, keep
git state clean, and commit with a conventional message.

## Workflow

When the user invokes `/ship`:

### 1. Make the change

### 2. Test and lint
Run the relevant tests + linter (`uv run pytest ...`, `uvx ruff check ...`).
Note: heavy Polars tests may segfault locally under x86/Rosetta emulation —
that's environmental, not a code failure; CI runners are native and fine.

### 3. Verify behavior
For anything user-facing, verify it actually works; be explicit about coverage
gaps. For UI/browser changes that can't be tested headless, SAY SO and ask for
confirmation — never claim a UI change works without evidence. Distinguish
"static checks pass" from "feature verified".

### 4. Review and stage
Review the diff. Stage only intended files by name (never `git add -A`).

### 5. Commit and push
Commit with a conventional message (`fix:`/`feat:`/`test:`/`ci:` ...); body in
Dutch is fine. If the team convention is to attribute AI-assisted commits, add a
trailing `Co-Authored-By: Claude <noreply@anthropic.com>` line. Then push. If a
PR is involved, consider /pr-reply or /branch-pr next.

## Important

- **Verify before "done"** — distinguish "static checks pass" from "feature
  verified"; be honest about what wasn't tested.
- **Check git state after checkouts/rebases** — run `git status` and confirm no
  unintended staged changes (a checkout can silently stage reverting changes);
  reconcile local vs remote before committing.
- **Never commit stray files** — stage by name to avoid sweeping in local build
  artifacts, reports, or editor junk (`coverage.xml`, generated HTML, etc.).
- **gh auth**: an invalid `$GITHUB_TOKEN` can shadow the `gh` login — prefix `gh`
  commands with `unset GITHUB_TOKEN &&`.
- Applies to cedanl repos.
