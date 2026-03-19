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
    "c-style syntax",
    [
      PYTHON,
      "-m",
      "pytest",
      "-q",
      "src-python/tests/test_cstyle_syntax.py",
      "src-python/tests/test_syntax_examples.py",
    ],
  ),
  (
    "self interpreter",
    [
      PYTHON,
      "-m",
      "pytest",
      "-q",
      "src-python/tests/test_self_interp.py",
      "-k",
      "not if_else and not from_until and not fib and not uncall and not mutual_recursion and not tower_1level_backward",
    ],
  ),
  (
    "struct runtime",
    [PYTHON, "-m", "pytest", "-q", "src-python/tests/test_struct_parse.py", "src-python/tests/test_struct_runtime.py"],
  ),
  (
    "char arrays",
    [PYTHON, "-m", "pytest", "-q", "src-python/tests/test_char_array_support.py"],
  ),
  (
    "basic examples",
    [PYTHON, "-m", "pytest", "-q", "src-python/tests/test_basic_examples.py"],
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
