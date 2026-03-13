from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[2]
HASKELL_JANA = ROOT / "dist-newstyle" / "build" / "x86_64-linux" / "ghc-9.6.7" / "jana-1.1" / "x" / "jana" / "build" / "jana" / "jana"


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


class Step3SuccessTests(unittest.TestCase):
  def check_case(self, path: str) -> None:
    haskell = run_haskell(path)
    python = run_python(path)
    self.assertEqual((python.returncode, python.stdout, python.stderr), (haskell.returncode, haskell.stdout, haskell.stderr), path)

  def test_sqrt(self) -> None:
    self.check_case("examples/sqrt.ja")

  def test_round_trip_uncall(self) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".ja", dir=ROOT, delete=False) as handle:
      handle.write(textwrap.dedent(
        """\
        procedure bump(int x)
            local int z = x
                x += z
            delocal int z = x / 2

        procedure main()
            int x
            x += 7
            call bump(x)
            printf("%d\\n", x)
            uncall bump(x)
            printf("%d\\n", x)
        """
      ))
      tmp_path = Path(handle.name)
    try:
      self.check_case(str(tmp_path))
    finally:
      tmp_path.unlink(missing_ok=True)


if __name__ == "__main__":
  unittest.main()
