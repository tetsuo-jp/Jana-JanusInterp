from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[2]
HASKELL_CMD = ["runhaskell", "-isrc", "src/Main.hs"]


def run_haskell(path: str) -> subprocess.CompletedProcess[str]:
  return subprocess.run(
    [*HASKELL_CMD, path],
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

  def test_run_length_encoding(self) -> None:
    self.check_case("examples/run-length-enc.ja")

  def test_run_length_encoding_stack(self) -> None:
    self.check_case("examples/run-length-enc-stack.ja")

  def test_matrixmult(self) -> None:
    self.check_case("examples/matrixmult.ja")

  def test_matrixmult_v1(self) -> None:
    self.check_case("examples/matrixmult_v1.0.ja")

  def test_two_dimensional_array(self) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".ja", dir=ROOT, delete=False) as handle:
      handle.write(textwrap.dedent(
        """\
        void inc(int x) {
            x += 1;
        }

        void main() {
            int a[2][2];
            a[0][0] += 1;
            a[0][1] += 2;
            a[1][0] += 3;
            a[1][1] += 4;
            call inc(a[1][0]);
            show(a);
        }
        """
      ))
      tmp_path = Path(handle.name)
    try:
      self.check_case(str(tmp_path))
    finally:
      tmp_path.unlink(missing_ok=True)


if __name__ == "__main__":
  unittest.main()
