from __future__ import annotations

import os
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest
from contextlib import redirect_stderr
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src-python"))

from jana_py.format import format_program
from jana_py.parser_janus2026 import parse_program
from jana_py.preprocess import preprocess_text
from jana_py.runtime import Runtime
from jana_py.validate import validate_program


def run_python(path: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
  env = dict(os.environ)
  env["PYTHONPATH"] = str(ROOT / "src-python")
  return subprocess.run(
    [sys.executable, "-m", "jana_py.cli", path],
    cwd=ROOT,
    text=True,
    capture_output=True,
    input=stdin,
    env=env,
    check=False,
  )


class CharArraySupportTests(unittest.TestCase):
  def run_case(self, source: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    path = "char_support_case.ja"
    try:
      preprocessed = preprocess_text(path, textwrap.dedent(source))
      program = parse_program(path, preprocessed.text, preprocessed.line_origins)
      validate_program(program)
      stderr = io.StringIO()
      with patch("sys.stdin", io.StringIO(stdin or "")), redirect_stderr(stderr):
        stdout = Runtime(program).run(show_store=True)
      return subprocess.CompletedProcess(["runtime"], 0, stdout, stderr.getvalue())
    except Exception as exc:
      return subprocess.CompletedProcess(["runtime"], 1, str(exc) + "\n", "")

  def test_parser_and_formatter_preserve_char_string_init(self) -> None:
    program = parse_program(
      "char_format.ja",
      textwrap.dedent(
        """\
        void main() {
            char s[] = "abc";
            printf("%s", s);
        }
        """
      ),
    )
    self.assertEqual(
      format_program(program),
      textwrap.dedent(
        """\
        void main() {
            char s[] = "abc";
            printf("%s", s);
        }
        """
      ),
    )

  def test_parser_and_formatter_preserve_escaped_char_string_init(self) -> None:
    program = parse_program(
      "char_escape_format.ja",
      textwrap.dedent(
        """\
        void main() {
            char s[] = "a\\n\\\\\\\"b\\u0000";
            printf("%s", s);
        }
        """
      ),
    )
    self.assertEqual(
      format_program(program),
      textwrap.dedent(
        """\
        void main() {
            char s[] = "a\\n\\\\\\\"b\\u0000";
            printf("%s", s);
        }
        """
      ),
    )

  def test_parser_and_formatter_preserve_scanf(self) -> None:
    program = parse_program(
      "scanf_format.ja",
      textwrap.dedent(
        """\
        void main() {
            int x = 0;
            char s[6] = { 0, 0, 0, 0, 0, 0 };
            scanf("%d %s", x, s);
        }
        """
      ),
    )
    self.assertEqual(
      format_program(program),
      textwrap.dedent(
        """\
        void main() {
            int x = 0;
            char s[6] = { 0, 0, 0, 0, 0, 0 };
            scanf("%d %s", x, s);
        }
        """
      ),
    )

  def test_char_array_infers_size_and_supports_printf_s(self) -> None:
    result = self.run_case(
      """\
      void main() {
          char s[] = "abc";
          printf("%s", s);
      }
      """
    )
    self.assertEqual(result.returncode, 0)
    self.assertEqual(result.stdout, "abc\ns[4] = {0, 0, 0, 0}\n")
    self.assertEqual(result.stderr, "")

  def test_char_array_fixed_size_zero_pads(self) -> None:
    result = self.run_case(
      """\
      void main() {
          char s[5] = "abc";
          assert true;
      }
      """
    )
    self.assertEqual(result.returncode, 0)
    self.assertEqual(result.stdout, "s[5] = {97, 98, 99, 0, 0}\n")
    self.assertEqual(result.stderr, "Warning: non-zero values remain at end of execution: s\n")

  def test_string_alias_fixed_size_accepts_string_initializer(self) -> None:
    result = self.run_case(
      """\
      void main() {
            string text[9] = "bananana";
            printf("%s", text);
        }
      """
    )
    self.assertEqual(result.returncode, 0)
    self.assertEqual(result.stdout, "bananana\ntext[9] = {0, 0, 0, 0, 0, 0, 0, 0, 0}\n")
    self.assertEqual(result.stderr, "")

  def test_string_alias_infers_size_from_string_initializer(self) -> None:
    result = self.run_case(
      """\
      void main() {
            string text[] = "bananana";
            printf("%s", text);
        }
      """
    )
    self.assertEqual(result.returncode, 0)
    self.assertEqual(result.stdout, "bananana\ntext[9] = {0, 0, 0, 0, 0, 0, 0, 0, 0}\n")
    self.assertEqual(result.stderr, "")

  def test_local_char_array_round_trips(self) -> None:
    result = self.run_case(
      """\
      void main() {
          local char s[] = "abc" {
              printf("%s", s);
          } delocal char s[4] = {0, 0, 0, 0};
      }
      """
    )
    self.assertEqual(result.returncode, 0)
    self.assertEqual(result.stdout, "abc\n")
    self.assertEqual(result.stderr, "")

  def test_printf_s_stops_at_embedded_nul(self) -> None:
    result = self.run_case(
      """\
      void main() {
          char s[] = "ab\\u0000c";
          printf("%s", s);
      }
      """
    )
    self.assertEqual(result.returncode, 0)
    self.assertEqual(result.stdout, "ab\ns[5] = {0, 0, 0, 0, 0}\n")
    self.assertEqual(result.stderr, "")

  def test_char_array_handles_escape_sequences(self) -> None:
    result = self.run_case(
      """\
      void main() {
          char s[] = "a\\n\\\\\\\"b";
          printf("%s", s);
      }
      """
    )
    self.assertEqual(result.returncode, 0)
    self.assertEqual(result.stdout, 'a\n\\"b\ns[6] = {0, 0, 0, 0, 0, 0}\n')
    self.assertEqual(result.stderr, "")

  def test_printf_percent_and_backslash_escapes(self) -> None:
    result = self.run_case(
      """\
      void main() {
          char s[] = "xy";
          printf("path=\\\\tmp %% %s", s);
      }
      """
    )
    self.assertEqual(result.returncode, 0)
    self.assertEqual(result.stdout, "path=\\tmp % xy\ns[3] = {0, 0, 0}\n")
    self.assertEqual(result.stderr, "")

  def test_caesar_example_file_runs(self) -> None:
    result = run_python("examples/caesar.ja")
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    self.assertIn("plain:  hello world", result.stdout)
    self.assertIn("cipher: khoor zruog", result.stdout)
    self.assertIn("back:   hello world", result.stdout)

  def test_printf_reports_unrecognized_percent_with_escapes(self) -> None:
    result = self.run_case(
      """\
      void main() {
          char s[] = "xy";
          printf("path=\\\\tmp %q %s", s);
      }
      """
    )
    self.assertEqual(result.returncode, 1)
    self.assertIn("Unrecognized format specifier: `%q'", result.stdout)

  def test_char_array_size_too_small_fails(self) -> None:
    result = self.run_case(
      """\
      void main() {
          char s[3] = "abc";
          assert true;
      }
      """
    )
    self.assertEqual(result.returncode, 1)
    self.assertIn("Initializer is too large for variable `s'", result.stdout)

  def test_printf_s_requires_char_array(self) -> None:
    result = self.run_case(
      """\
      void main() {
          int s[4] = {97, 98, 99, 0};
          printf("%s", s);
      }
      """
    )
    self.assertEqual(result.returncode, 1)
    self.assertIn("Type mismatch for `%s' format specifier", result.stdout)

  def test_scanf_reads_zero_cleared_int(self) -> None:
    result = self.run_case(
      """\
      void main() {
          int x = 0;
          scanf("%d", x);
          printf("%d", x);
      }
      """,
      stdin="42\n",
    )
    self.assertEqual(result.returncode, 0)
    self.assertEqual(result.stdout, "42\nx = 0\n")
    self.assertEqual(result.stderr, "")

  def test_scanf_accepts_existing_matching_value(self) -> None:
    result = self.run_case(
      """\
      void main() {
          int x = 7;
          scanf("%d", x);
          printf("%d", x);
      }
      """,
      stdin="7\n",
    )
    self.assertEqual(result.returncode, 0)
    self.assertEqual(result.stdout, "7\nx = 0\n")
    self.assertEqual(result.stderr, "")

  def test_scanf_rejects_nonzero_mismatched_destination(self) -> None:
    result = self.run_case(
      """\
      void main() {
          int x = 7;
          scanf("%d", x);
      }
      """,
      stdin="9\n",
    )
    self.assertEqual(result.returncode, 1)
    self.assertIn("scanf destination must be zero-cleared or already equal to the incoming value", result.stdout)

  def test_scanf_reads_zero_cleared_char_array(self) -> None:
    result = self.run_case(
      """\
      void main() {
          char s[6] = {0, 0, 0, 0, 0, 0};
          scanf("%s", s);
          printf("%s", s);
      }
      """,
      stdin="hello\n",
    )
    self.assertEqual(result.returncode, 0)
    self.assertEqual(result.stdout, "hello\ns[6] = {0, 0, 0, 0, 0, 0}\n")
    self.assertEqual(result.stderr, "")

  def test_scanf_rejects_string_that_does_not_fit(self) -> None:
    result = self.run_case(
      """\
      void main() {
          char s[4] = {0, 0, 0, 0};
          scanf("%s", s);
      }
      """,
      stdin="hello\n",
    )
    self.assertEqual(result.returncode, 1)
    self.assertIn("scanf string is too large for destination array", result.stdout)


if __name__ == "__main__":
  unittest.main()
