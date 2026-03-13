from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
PYTHON = sys.executable
ENV = dict(os.environ)
ENV["PYTHONPATH"] = str(ROOT / "src-python")

CHECKS: list[tuple[str, list[str]]] = [
  (
    "success regression",
    [
      PYTHON,
      "-m",
      "pytest",
      "-q",
      "src-python/tests/test_step2_success.py",
      "src-python/tests/test_step3_success.py",
      "src-python/tests/test_step4_success.py",
      "src-python/tests/test_step5_success.py",
      "src-python/tests/test_step6_success.py",
    ],
  ),
  (
    "debugger regression",
    [PYTHON, "-m", "pytest", "-q", "src-python/tests/test_debugger_cli.py"],
  ),
  (
    "local parity",
    [PYTHON, "-m", "pytest", "-q", "src-python/tests/test_local_parity.py"],
  ),
  (
    "control-flow parity",
    [PYTHON, "-m", "pytest", "-q", "src-python/tests/test_control_flow_parity.py"],
  ),
  (
    "error golden subset",
    [
      PYTHON,
      "-m",
      "pytest",
      "-q",
      "src-python/tests/test_step1_golden.py",
      "-k",
      "errors and not infinite_recursion",
    ],
  ),
  (
    "type-related golden subset",
    [
      PYTHON,
      "-m",
      "pytest",
      "-q",
      "src-python/tests/test_step1_golden.py",
      "-k",
      "type_error or type-error or modular_integer or prints_printf_type_mismatch or prints_printf_unrecognized_type or delocal_wrong_type",
    ],
  ),
]


def main() -> int:
  for name, cmd in CHECKS:
    print(f"[check] {name}")
    result = subprocess.run(cmd, cwd=ROOT, env=ENV, text=True, check=False)
    if result.returncode != 0:
      print(f"[fail] {name}")
      return result.returncode
    print(f"[ok] {name}")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
