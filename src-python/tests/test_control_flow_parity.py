from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
HASKELL_JANA = ROOT / "dist-newstyle" / "build" / "x86_64-linux" / "ghc-9.6.7" / "jana-1.1" / "x" / "jana" / "build" / "jana" / "jana"


def run_haskell(path: Path) -> subprocess.CompletedProcess[str]:
  return subprocess.run(
    [str(HASKELL_JANA), str(path)],
    cwd=ROOT,
    text=True,
    capture_output=True,
    check=False,
    timeout=5,
  )


def run_python(path: Path) -> subprocess.CompletedProcess[str]:
  env = dict(os.environ)
  env["PYTHONPATH"] = str(ROOT / "src-python")
  return subprocess.run(
    [sys.executable, "-m", "jana_py.cli", str(path)],
    cwd=ROOT,
    text=True,
    capture_output=True,
    env=env,
    check=False,
    timeout=5,
  )


class ControlFlowParityTests(unittest.TestCase):
  maxDiff = None

  def assert_matches_haskell(self, relative_path: str) -> None:
    path = ROOT / relative_path
    haskell = run_haskell(path)
    python = run_python(path)
    self.assertEqual(
      (python.returncode, python.stdout, python.stderr),
      (haskell.returncode, haskell.stdout, haskell.stderr),
      f"Mismatch for {relative_path}",
    )

  def test_if_forward_assertion_failure_matches(self) -> None:
    self.assert_matches_haskell("tests/errors/assertion-fail-if-fwd.ja")

  def test_if_backward_assertion_failure_matches(self) -> None:
    self.assert_matches_haskell("tests/errors/assertion-fail-if-bwd.ja")

  def test_from_forward_assertion_failure_matches(self) -> None:
    self.assert_matches_haskell("tests/errors/assertion-fail-from-fwd.ja")

  def test_from_backward_assertion_failure_matches(self) -> None:
    self.assert_matches_haskell("tests/errors/assertion-fail-from-bwd.ja")


if __name__ == "__main__":
  unittest.main()
