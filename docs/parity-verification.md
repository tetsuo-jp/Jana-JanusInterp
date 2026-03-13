# Parity Verification

Use these commands for the main release-candidate checks after parity work.

## Current State

- Python parity work is currently in a release-candidate state.
- `docs/parity-backlog.md` is fully marked `done`.
- Use `python3 src-python/tests/run_release_candidate.py` as the default verification entry point for future changes.

## One-Command Wrapper

- `python3 src-python/tests/run_release_candidate.py`

## Core Checks

- Success regression
  - `pytest -q src-python/tests/test_step2_success.py src-python/tests/test_step3_success.py src-python/tests/test_step4_success.py src-python/tests/test_step5_success.py src-python/tests/test_step6_success.py`
- Debugger regression
  - `pytest -q src-python/tests/test_debugger_cli.py`
- Local parity regression
  - `pytest -q src-python/tests/test_local_parity.py`
- Control-flow parity regression
  - `pytest -q src-python/tests/test_control_flow_parity.py`

## Golden Subsets

- Error golden subset
  - `python3 -m pytest -q src-python/tests/test_step1_golden.py -k 'errors and not infinite_recursion'`
- Type-related golden subset
  - `python3 -m pytest -q src-python/tests/test_step1_golden.py -k 'type_error or type-error or modular_integer or prints_printf_type_mismatch or prints_printf_unrecognized_type or delocal_wrong_type'`

## Interpretation

- Treat `src/` as the source of truth.
- Judge observable behavior by `exit code + stdout + stderr + final store`.
- Treat normal execution parity as `must`.
- Treat debugger parity as `should`.
