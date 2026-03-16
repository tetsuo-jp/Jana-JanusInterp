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


def run_generator(command: list[str], output_path: Path) -> None:
  result = subprocess.run(
    command,
    cwd=ROOT,
    text=True,
    capture_output=True,
    check=False,
    env={**os.environ, "PYTHONPATH": str(ROOT / "src-python")},
  )
  if result.returncode != 0:
    raise AssertionError(result.stdout + result.stderr)
  output_path.write_text(result.stdout, encoding="utf-8")


def compile_cpp(source: Path, binary: Path) -> None:
  result = subprocess.run(
    ["g++", "-std=c++17", str(source), "-o", str(binary)],
    cwd=ROOT,
    text=True,
    capture_output=True,
    check=False,
  )
  if result.returncode != 0:
    raise AssertionError(result.stdout + result.stderr)


def run_binary(binary: Path) -> subprocess.CompletedProcess[str]:
  return subprocess.run(
    [str(binary)],
    cwd=ROOT,
    text=True,
    capture_output=True,
    check=False,
  )


class Step6SuccessTests(unittest.TestCase):
  def test_codegen_binary_matches_haskell_codegen(self) -> None:
    program = textwrap.dedent(
      """\
      procedure twice(int x)
          x += x

      procedure main()
          int x
          x += 5
          call twice(x)
          printf("%d\\n", x)
      """
    )
    with tempfile.TemporaryDirectory(dir=ROOT) as tmpdir:
      tmp = Path(tmpdir)
      program_path = tmp / "prog.ja"
      program_path.write_text(program, encoding="utf-8")
      hs_cpp = tmp / "hs.cpp"
      py_cpp = tmp / "py.cpp"
      hs_bin = tmp / "hs-bin"
      py_bin = tmp / "py-bin"

      run_generator([str(HASKELL_JANA), "-c", str(program_path)], hs_cpp)
      run_generator([sys.executable, "-m", "jana_py.cli", "-c", str(program_path)], py_cpp)
      compile_cpp(hs_cpp, hs_bin)
      compile_cpp(py_cpp, py_bin)

      hs_run = run_binary(hs_bin)
      py_run = run_binary(py_bin)
      self.assertEqual((py_run.returncode, py_run.stdout, py_run.stderr), (hs_run.returncode, hs_run.stdout, hs_run.stderr))


if __name__ == "__main__":
  unittest.main()
