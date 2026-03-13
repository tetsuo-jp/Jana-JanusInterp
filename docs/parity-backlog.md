# Jana Python Parity Backlog

Use this file as the default execution queue for autonomous parity work. Process rows from top to bottom unless the user explicitly reprioritizes.

## Status Keys

- `todo`: not started
- `doing`: actively being worked on
- `blocked`: requires execution model change, broader design choice, or user input
- `done`: completion condition satisfied and scoped tests green

## Rows

| Order | Theme | Status | Haskell Reference | Python Scope | Scoped Tests | Completion Condition | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Debug backward stepping deeper than one visible boundary (`END -> 5 -> 9 -> 10` class) | done | `src/Jana/Eval.hs`, `src/Jana/Types.hs` | `src-python/jana_py/runtime.py` | `src-python/tests/test_debugger_cli.py` | Haskell-observed stepping sequence matches for the targeted debugger flows and existing debugger CLI tests remain green | Covered by `fib.ja` debugger regression for `END -> 5 -> 9 -> 10` |
| 2 | `From` reverse stepping stop positions in debugger | done | `src/Jana/Eval.hs`, `src/Jana/Types.hs` | `src-python/jana_py/runtime.py`, `src-python/jana_py/invert.py` | `src-python/tests/test_debugger_cli.py`, targeted new debugger cases | `from`-based reverse stepping matches Haskell stop positions for minimal examples | Covered by `from_debug_simple.ja` debugger parity tests and scoped regressions |
| 3 | `Iterate` reverse stepping and debugger parity | done | `src/Jana/Eval.hs`, `src/Jana/Types.hs` | `src-python/jana_py/runtime.py`, `src-python/jana_py/invert.py` | targeted new iterate parity tests, success regressions | `iterate` stepping and reverse stepping match Haskell for minimal examples | Covered by `iterate_debug_simple.ja` debugger parity tests and scoped regressions |
| 4 | `Local` backward semantics parity | done | `src/Jana/Eval.hs`, `src/Jana/Types.hs` | `src-python/jana_py/runtime.py`, `src-python/jana_py/errors.py` | targeted local semantic tests, success regressions | forward/backward local checks and failure locations match Haskell for targeted cases | Covered by delocal error parity tests and `local_backward_simple.ja` debugger parity |
| 5 | `Call/Uncall` deeper reverse stepping across procedure boundaries | done | `src/Jana/Eval.hs`, `src/Jana/Types.hs` | `src-python/jana_py/runtime.py`, `src-python/jana_py/invert.py` | debugger CLI parity tests, targeted call/uncall cases | multi-step reverse stepping across procedure boundaries matches Haskell on targeted examples | Covered by `fib.ja` debugger regression across procedure boundary reverse stepping |
| 6 | Contextual error parity beyond current covered cases | done | `src/Jana/Eval.hs`, `src/Jana/Types.hs` | `src-python/jana_py/errors.py`, `src-python/jana_py/runtime.py` | selected `tests/errors/*.ja`, `src-python/tests/test_control_flow_parity.py` | targeted error cases match Haskell in code, stdout, and stderr | `test_step1_golden.py -k 'errors and not infinite_recursion'` passed (`49 passed`) |
| 7 | Residual backward type semantics parity | done | `src/Jana/Types.hs` | `src-python/jana_py/runtime.py`, `src-python/jana_py/ast.py` | targeted type/error cases, success regressions | targeted backward-only type constraints match Haskell | Targeted type-related golden cases passed (`12 passed`) |
| 8 | Record post-completion verification commands and release-candidate checks | done | project policy | docs only | doc review | Main parity verification commands are documented in one short place | Covered by `docs/parity-verification.md` and `Release-Candidate Checks` section |
| 9 | Add a lightweight final verification suite wrapper | done | project policy | `src-python/tests/`, optional helper script | wrapper command plus existing tests | One command runs the main final parity checks with concise output | Covered by `python3 src-python/tests/run_release_candidate.py` |
| 10 | Refactor debugger internals for readability without changing behavior | done | existing passing behavior | `src-python/jana_py/runtime.py` | debugger CLI tests, success regressions | Internal structure is clearer and tests remain green | Extracted debugger help text and break-print helpers; regressions stayed green |

## Default Test Sets

- Debugger/theme-local: `pytest -q src-python/tests/test_debugger_cli.py`
- Control-flow parity: `pytest -q src-python/tests/test_control_flow_parity.py`
- Success regression: `pytest -q src-python/tests/test_step2_success.py src-python/tests/test_step3_success.py src-python/tests/test_step4_success.py src-python/tests/test_step5_success.py src-python/tests/test_step6_success.py`

## Release-Candidate Checks

- Main success regression: `pytest -q src-python/tests/test_step2_success.py src-python/tests/test_step3_success.py src-python/tests/test_step4_success.py src-python/tests/test_step5_success.py src-python/tests/test_step6_success.py`
- Main debugger regression: `pytest -q src-python/tests/test_debugger_cli.py`
- Local parity regression: `pytest -q src-python/tests/test_local_parity.py`
- Control-flow parity regression: `pytest -q src-python/tests/test_control_flow_parity.py`
- Error golden subset: `python3 -m pytest -q src-python/tests/test_step1_golden.py -k 'errors and not infinite_recursion'`
- Type-related golden subset: `python3 -m pytest -q src-python/tests/test_step1_golden.py -k 'type_error or type-error or modular_integer or prints_printf_type_mismatch or prints_printf_unrecognized_type or delocal_wrong_type'`

## Execution Policy

- Before editing, identify the single row being handled and keep the code-reading scope to the listed files.
- Before broad implementation, reproduce the Haskell behavior with the smallest possible example or command sequence.
- After a patch, run the row's scoped tests first.
- Run success regression only if the scoped tests pass.
- If 2 focused implementation attempts fail on the same row, mark the row `blocked` or note the required redesign in `Notes` before proceeding further.
