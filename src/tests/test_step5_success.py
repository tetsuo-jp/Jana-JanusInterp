from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
HASKELL_CMD = ["runhaskell", "-isrc", "src/Main.hs"]


def run_haskell(args: list[str]) -> subprocess.CompletedProcess[str]:
  return subprocess.run(
    [*HASKELL_CMD, *args],
    cwd=ROOT,
    text=True,
    capture_output=True,
    check=False,
  )


def run_python(args: list[str]) -> subprocess.CompletedProcess[str]:
  env = dict(os.environ)
  env["PYTHONPATH"] = str(ROOT / "src-python")
  return subprocess.run(
    [sys.executable, "-m", "jana_py.cli", *args],
    cwd=ROOT,
    text=True,
    capture_output=True,
    env=env,
    check=False,
  )


class Step5SuccessTests(unittest.TestCase):
  def check_case(self, args: list[str]) -> None:
    haskell = run_haskell(args)
    python = run_python(args)
    self.assertEqual((python.returncode, python.stdout, python.stderr), (haskell.returncode, haskell.stdout, haskell.stderr), " ".join(args))

  def test_mod_bits(self) -> None:
    self.check_case(["-m32", "examples/fib.ja"])

  def test_mod_prime(self) -> None:
    self.check_case(["-p2147483647", "examples/fib.ja"])

  def test_timeout_flag(self) -> None:
    self.check_case(["-t1", "examples/fib.ja"])


if __name__ == "__main__":
  unittest.main()
