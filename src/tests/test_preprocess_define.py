from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[2]


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


class PreprocessDefineTests(unittest.TestCase):
  def run_case(self, source: str, extra_args: list[str] | None = None) -> subprocess.CompletedProcess[str]:
    with tempfile.NamedTemporaryFile("w", suffix=".ja", dir=ROOT, delete=False) as handle:
      handle.write(textwrap.dedent(source))
      path = handle.name
    try:
      return run_python([*(extra_args or []), path])
    finally:
      Path(path).unlink(missing_ok=True)

  def test_define_expands_in_execution(self) -> None:
    result = self.run_case(
      """\
      #define X 333
      void main() {
          int x = X;
          printf("%d", x);
      }
      """
    )
    self.assertEqual(result.returncode, 0)
    self.assertEqual(result.stdout, "333\n")
    self.assertEqual(result.stderr, "")

  def test_define_expands_in_ast_output(self) -> None:
    result = self.run_case(
      """\
      #define N 4
      void main() {
          int a[N];
          assert true;
      }
      """,
      ["-a"],
    )
    self.assertEqual(result.returncode, 0)
    self.assertIn('"value": 4', result.stdout)
    self.assertNotIn("#define", result.stdout)

  def test_define_chain_expands_recursively(self) -> None:
    result = self.run_case(
      """\
      #define VALUE 9
      #define X VALUE
      void main() {
          int x = X;
          printf("%d", x);
      }
      """
    )
    self.assertEqual(result.returncode, 0)
    self.assertEqual(result.stdout, "9\n")

  def test_undef_removes_macro(self) -> None:
    result = self.run_case(
      """\
      #define X 9
      #undef X
      void main() {
          int x = 4;
          printf("%d", x);
      }
      """
    )
    self.assertEqual(result.returncode, 0)
    self.assertEqual(result.stdout, "4\n")

  def test_define_supports_line_continuation(self) -> None:
    result = self.run_case(
      """\
      #define SUM 300 + \\
      33
      void main() {
          int x = SUM;
          printf("%d", x);
      }
      """
    )
    self.assertEqual(result.returncode, 0)
    self.assertEqual(result.stdout, "333\n")

  def test_function_macro_expands_arguments(self) -> None:
    result = self.run_case(
      """\
      #define ADD(x, y) ((x) + (y))
      void main() {
          int x = ADD(300, 33);
          printf("%d", x);
      }
      """
    )
    self.assertEqual(result.returncode, 0)
    self.assertEqual(result.stdout, "333\n")

  def test_function_macro_handles_nested_arguments(self) -> None:
    result = self.run_case(
      """\
      #define WRAP(x) x
      void main() {
          int x = WRAP((300 + 33));
          printf("%d", x);
      }
      """
    )
    self.assertEqual(result.returncode, 0)
    self.assertEqual(result.stdout, "333\n")

  def test_define_supports_array_type_alias_in_parameter_position(self) -> None:
    result = self.run_case(
      """\
      #define code int
      #define codes code[]
      void fill(codes out) {
          out[0] += 4;
          out[1] += 5;
      }

      void main() {
          int out[2];
          call fill(out);
          printf("%d %d", out[0], out[1]);
      }
      """
    )
    self.assertEqual(result.returncode, 0)
    self.assertEqual(result.stdout, "4 5\n")
    self.assertEqual(
      result.stderr,
      "Warning: non-zero values remain at end of execution: out\n",
    )

  def test_define_supports_array_type_alias_in_main_declaration(self) -> None:
    result = self.run_case(
      """\
      #define code int
      #define codes code[]
      void main() {
          codes out[2];
          out[0] += 1;
          printf("%d %d", out[0], out[1]);
      }
      """
    )
    self.assertEqual(result.returncode, 0)
    self.assertEqual(result.stdout, "1 0\n")
    self.assertEqual(
      result.stderr,
      "Warning: non-zero values remain at end of execution: out\n",
    )


if __name__ == "__main__":
  unittest.main()
