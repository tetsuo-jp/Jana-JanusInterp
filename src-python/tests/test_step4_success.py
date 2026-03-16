from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[2]
_DIST_JANA = ROOT / "dist-newstyle" / "build" / "x86_64-linux" / "ghc-9.6.7" / "jana-1.1" / "x" / "jana" / "build" / "jana" / "jana"
import shutil as _shutil
HASKELL_JANA = Path(_shutil.which("jana")) if _shutil.which("jana") and not _DIST_JANA.exists() else _DIST_JANA


def run_haskell(path: str) -> subprocess.CompletedProcess[str]:
  return subprocess.run(
    [str(HASKELL_JANA), path],
    cwd=ROOT,
    text=True,
    capture_output=True,
    check=False,
  )


def run_python(path: str) -> subprocess.CompletedProcess[str]:
  env = dict(os.environ)
  env["PYTHONPATH"] = str(ROOT / "src-python")
  return subprocess.run(
    [sys.executable, "-m", "jana_py.cli", path],
    cwd=ROOT,
    text=True,
    capture_output=True,
    env=env,
    check=False,
  )


class Step4SuccessTests(unittest.TestCase):
  def check_case(self, path: str) -> None:
    haskell = run_haskell(path)
    python = run_python(path)
    self.assertEqual((python.returncode, python.stdout, python.stderr), (haskell.returncode, haskell.stdout, haskell.stderr), path)

  def test_stack_operations(self) -> None:
    self.check_case("examples/stack-operations.ja")

  def test_two_dimensional_array(self) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".ja", dir=ROOT, delete=False) as handle:
      handle.write(textwrap.dedent(
        """\
        procedure inc(int x)
            x += 1

        procedure main()
            int a[2][2]
            a[0][0] += 1
            a[0][1] += 2
            a[1][0] += 3
            a[1][1] += 4
            call inc(a[1][0])
            show(a)
        """
      ))
      tmp_path = Path(handle.name)
    try:
      self.check_case(str(tmp_path))
    finally:
      tmp_path.unlink(missing_ok=True)


if __name__ == "__main__":
  unittest.main()
