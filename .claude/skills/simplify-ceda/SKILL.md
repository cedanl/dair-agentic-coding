---
name: simplify-ceda
description: Review changed code for reuse, quality, and efficiency against CEDA standards. Fix any issues found. Use after writing or editing code in cedanl repositories.
---

# Simplify: Code Review and Cleanup

Review all changed files for reuse, quality, and efficiency against CEDA standards. Fix any issues found.

## Vereiste installatie

Deze skill is een uitbreiding van de simplify plugin. Controleer bij het opstarten of de plugin geïnstalleerd is en installeer hem indien nodig:

```bash
claude plugin install code-simplifier@claude-plugins-official
```

Als de plugin al geïnstalleerd is, geeft dit commando een melding en gaat het verder. Dit is een eenmalige stap per machine.

## Phase 1: Identify Changes

Run `git diff` (or `git diff HEAD` if there are staged changes) to see what changed. If there are no git changes, review the most recently modified files mentioned or edited earlier in this conversation.

Detect the language from the changed files:
- R files (`.R`) → apply R-specific CEDA checks
- Python files (`.py`) → apply Python-specific CEDA checks
- Mixed → apply both

**Skip data files**: never include or inspect files in `data/`, `Output/`, or any directory listed in `.claudeignore`. These directories contain large datasets that will cause agents to hang. Only review source code files (`.R`, `.py`, `.md`, config files).

## Phase 2: Launch Three Review Agents in Parallel

Use the Agent tool to launch all three agents concurrently in a single message. Pass each agent the full diff and the detected language so it has complete context.

**Important**: include the full diff content directly in each agent prompt. Do NOT instruct agents to explore the filesystem — they must work only from the diff you provide. This prevents agents from accidentally reading large data files in `data/` or `Output/`.

### Agent 1: Code Reuse Review

For each change:

1. **Search for existing utilities and helpers** that could replace newly written code. Common locations: `R/`, `src/`, utility directories, files adjacent to changed ones.
2. **Flag any new function that duplicates existing functionality.** Suggest the existing function instead.
3. **Flag any inline logic that could use an existing utility** — hand-rolled string manipulation, manual path handling, custom environment checks, and similar patterns.

**R-specific**: check for re-implementation of tidyverse functions (`dplyr`, `stringr`, `purrr`, `lubridate`, `fs`). Flag use of base R equivalents where tidyverse improves readability (e.g., `grepl()` instead of `str_detect()`, `read.csv()` instead of `read_csv()`).

**Python-specific**: check for re-implementation of Polars operations, manual path handling where `Path` from `pathlib` exists, and custom iteration where `polars` method chaining would work.

### Agent 2: Code Quality Review

Review the same changes against CEDA standards:

**General (both languages):**
1. **Redundant state**: state that duplicates existing state, cached values that could be derived
2. **Parameter sprawl**: adding parameters instead of generalizing or restructuring
3. **Copy-paste with slight variation**: near-duplicate blocks that should share an abstraction
4. **Leaky abstractions**: exposing internal details that should be encapsulated
5. **Unnecessary comments**: comments that explain WHAT the code does rather than WHY — delete them. Keep only comments explaining hidden constraints, subtle invariants, or non-obvious decisions. Comments should explain *why*, not narrate the code.
6. **Deeply nested logic**: flag if/else nesting deeper than 2 levels — suggest guard clauses and early returns (happy path principle)
7. **Functions not starting with a verb**: `snake_case` verb + object naming is required (`transform_data`, not `data_transform` or `getData`)

**R-specific:**
- `=` used for assignment instead of `<-`
- `%>%` used instead of `|>` (base pipe)
- Missing explicit `return()` statements
- `stop()` used instead of `rlang::abort()`
- `message()` / `print()` used instead of `cli::cli_alert_*()`
- `#` single-hash comments in R code — should be `##` (double hash)
- Missing `::` namespace qualification in package functions (e.g., `mutate()` instead of `dplyr::mutate()`)
- `library()` calls inside package functions — these must not exist in `R/`
- Implicit returns at end of functions

**Python-specific:**
- Missing type hints on function signatures
- Missing or incomplete Google-style docstrings on functions
- `os.path` used instead of `pathlib.Path`
- Pandas used where Polars would work
- `Optional[X]` instead of `X | None`
- `List[X]` instead of `list[X]`
- Bare `except Exception` without re-raising

### Agent 3: Efficiency Review

Review the same changes for efficiency:

1. **Unnecessary work**: redundant computations, repeated file reads, duplicate API calls, N+1 patterns
2. **Missed concurrency**: independent operations run sequentially that could run in parallel
3. **Hot-path bloat**: new blocking work added to startup or per-request paths
4. **Unconditional updates in loops/intervals**: add change-detection guards so downstream consumers aren't notified when nothing changed
5. **Unnecessary existence checks before operating** (TOCTOU anti-pattern) — operate directly and handle the error
6. **Memory**: unbounded data structures, missing cleanup, event listener leaks
7. **Overly broad operations**: reading entire files when only a portion is needed

**R-specific**: flag explicit `for` loops over data frames that could use `purrr::map()` or `dplyr` operations.

**Python-specific**: flag row-by-row Polars iteration where vectorized expressions exist.

## Phase 3: Fix Issues

Wait for all three agents to complete. Aggregate findings and fix each issue directly in the code. If a finding is a false positive or not worth addressing, note it and move on.

After fixing, run the appropriate formatter:
- R: `air format .`
- Python: `uv run ruff format .` and `uv run ruff check --fix .`

When done, briefly summarize what was fixed (or confirm the code was already clean).

## Installation

Install via the Claude plugin page: https://claude.com/plugins/code-simplifier
