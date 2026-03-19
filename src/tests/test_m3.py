from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[2]


def run_python(program_path: str) -> subprocess.CompletedProcess[str]:
  env = dict(os.environ)
  env["PYTHONPATH"] = str(ROOT / "src-python")
  return subprocess.run(
    [sys.executable, "-m", "jana_py.cli", program_path],
    cwd=ROOT,
    text=True,
    capture_output=True,
    env=env,
    check=False,
  )


class M3Tests(unittest.TestCase):
  def test_call_then_uncall_restores_state(self) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".ja", dir=ROOT, delete=False) as handle:
      handle.write(textwrap.dedent(
        """\
        procedure fib(int x1, int x2, int n)
            if n = 0 then
                x1 += 1
                x2 += 1
            else
                n -= 1
                call fib(x1, x2, n)
                x1 += x2
                x1 <=> x2
            fi x1 = x2

        procedure main()
            int x1
            int x2
            int n
            n += 5
            call fib(x1, x2, n)
            local int out_n = n, int out_x1 = x1, int out_x2 = x2 {
                printf("%d %d %d\\n", out_n, out_x1, out_x2);
            } delocal int out_n = 0, int out_x1 = 0, int out_x2 = 0;
            uncall fib(x1, x2, n)
            local int back_n = n, int back_x1 = x1, int back_x2 = x2 {
                printf("%d %d %d\\n", back_n, back_x1, back_x2);
            } delocal int back_n = 0, int back_x1 = 0, int back_x2 = 0;
        """
      ))
      tmp_path = Path(handle.name)
    try:
      result = run_python(str(tmp_path))
      self.assertEqual(result.returncode, 0, result.stderr)
      self.assertEqual(result.stdout, "0 8 13\n\n5 0 0\n\n")
      self.assertEqual(result.stderr, "Warning: non-zero values remain at end of execution: n\n")
    finally:
      tmp_path.unlink(missing_ok=True)

  def test_local_scope_round_trip(self) -> None:
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
            local int out_x = x {
                printf("%d\\n", out_x);
            } delocal int out_x = 0;
            uncall bump(x)
            local int back_x = x {
                printf("%d\\n", back_x);
            } delocal int back_x = 0;
        """
      ))
      tmp_path = Path(handle.name)
    try:
      result = run_python(str(tmp_path))
      self.assertEqual(result.returncode, 0, result.stderr)
      self.assertEqual(result.stdout, "14\n\n7\n\n")
      self.assertEqual(result.stderr, "Warning: non-zero values remain at end of execution: x\n")
    finally:
      tmp_path.unlink(missing_ok=True)


if __name__ == "__main__":
  unittest.main()
