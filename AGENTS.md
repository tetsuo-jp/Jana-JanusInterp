# Repo Notes

- Keep context narrow: prefer reading only `src/`, `src-python/`, `tests/`, `examples/`, `basicExamples/`, `README.md`, and `Tutorial.md`.
- Respect `.codexignore`; do not load `dist-newstyle/`, `.git/`, `bin/`, `web/`, `src-gen_ulrik/`, `src-gen.zip`, or `misc/` unless strictly needed.
- Use `rg` first to locate symbols, then open only the smallest relevant file region with `sed`.
- When comparing behavior, treat `src/Jana/Eval.hs` and `src/Jana/Types.hs` as the primary semantic references.
- Prefer failure-focused test runs; avoid full verbose output when only a few failing cases matter.
- Keep normal-success checks separate from abnormal/error golden checks.
- When reporting test results, summarize counts and failing case names instead of pasting full logs unless asked.
- For Python parity work, default to `src-python/jana_py/runtime.py`, `parser.py`, `validate.py`, `errors.py`, and `c_codegen.py`.
- Reuse saved repo memories before re-explaining parity status or `.codexignore` policy.
- If a task is scoped to one subsystem, avoid scanning unrelated directories or generated assets.

## Jana Python Parity: Low-Token Workflow

- Treat `src/` as the source of truth when behavior differs from papers, notes, or inferred intent.
- Judge observable-behavior parity by `exit code + stdout + stderr + final store`.
- Prioritize normal execution parity as `must` and debugger parity as `should`.
- Scope each turn to exactly one theme; do not mix debugger, control-flow, type, and error-alignment work.
- Use this execution order: `debug step` -> `debug output` -> `If` -> `From` -> `Iterate` -> `Local` -> `Call/Uncall` -> `errors` -> `types`.
- Read only the relevant function(s) in `src/Jana/Eval.hs` for the current theme.
- Open `src/Jana/Types.hs` only when the current theme involves type rules or contextual error construction.
- Default Python-side scope to `src-python/jana_py/runtime.py`; add `invert.py`, `errors.py`, or `ast.py` only if required by the theme.
- Run only the tests that directly exercise the current theme; avoid full-suite runs unless the scoped checks pass and regression coverage is needed.
- For `tests/errors/`, execute only the specific case(s) likely to move with the current change.
- If a normal-success test regresses, fix it first; if it cannot be fixed promptly, stop and report.
- Check output parity separately for stop position, wording, newline behavior, and whitespace.
- End each task with a short note stating what now matches and what remains unmatched.

## Jana Python Parity: Autonomous Execution Rules

- Unless the user redirects, continue working top-down through `docs/parity-backlog.md`.
- Treat each backlog row as one self-contained theme and finish it before moving to the next row.
- For each row, run only the listed scoped tests first; run broader success regressions only after scoped tests pass.
- A row is complete only when its listed completion condition is satisfied and the scoped regression tests stay green.
- If a normal-success test fails, attempt to fix it immediately; if it is not fixed within 2 focused attempts, stop and report.
- If the current implementation approach fails twice on the same row, a design change may be implemented automatically, but first mark the row `blocked` in `docs/parity-backlog.md` and report the situation.
- If resolving a row requires changing the execution model rather than a local behavior patch, that redesign is allowed without additional confirmation unless it changes the public CLI or test specification.
- Public CLI changes and test-specification changes always require user confirmation before implementation.
- If Haskell-observed behavior and Python behavior diverge more after a patch, revert the local approach conceptually and choose a narrower or different strategy before continuing.
- Prefer adding a minimal regression test that captures the observed Haskell behavior before broadening the implementation.
- If a row remains unresolved after 2 focused attempts, it is acceptable to mark it `blocked` and continue with the next backlog row.
- Prioritize user-visible observable behavior parity; internal implementation differences are acceptable if observable behavior matches.
- Final progress updates should state: backlog row handled, tests run, what now matches, and the next unmatched item.
