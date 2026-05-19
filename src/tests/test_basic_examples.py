from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src-python"))

from jana_py.parser_janus2026 import parse_program
from jana_py.preprocess import preprocess_text
from jana_py.runtime import Runtime
from jana_py.validate import validate_program


ROOT = Path(__file__).resolve().parents[2]


def run_python(relative_path: str) -> subprocess.CompletedProcess[str]:
  path = ROOT / relative_path
  text = path.read_text(encoding="utf-8")
  preprocessed = preprocess_text(str(path), text)
  program = parse_program(str(path), preprocessed.text, preprocessed.line_origins)
  validate_program(program)
  try:
    stdout = Runtime(program).run(show_store=True)
    return subprocess.CompletedProcess(["runtime"], 0, stdout, "")
  except Exception as exc:
    return subprocess.CompletedProcess(["runtime"], 1, str(exc) + "\n", "")


class BasicExamplesTests(unittest.TestCase):
  def test_basic_fib_runs(self) -> None:
    result = run_python("examples/basic/fib.janus")
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    self.assertIn("0 5 8", result.stdout)

  def test_basic_perm_to_code_runs(self) -> None:
    result = run_python("examples/basic/perm_to_code.janus")
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    self.assertIn("x[6] = {0, 0, 2, 1, 4, 4}", result.stdout)

  def test_basic_swap_equals_runs(self) -> None:
    result = run_python("examples/basic/swap_equals.janus")
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    self.assertIn("b[20] = {0, 1, 2, 3, 4, 15, 16, 17, 8, 9, 10, 11, 12, 13, 14, 5, 6, 7, 18, 19}", result.stdout)

  def test_basic_root_runs(self) -> None:
    result = run_python("examples/basic/root.janus")
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    self.assertIn("0 10", result.stdout)

  def test_basic_factor_runs(self) -> None:
    result = run_python("examples/basic/factor.janus")
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    self.assertIn("fact[20] = {0, 2, 2, 2, 3, 5, 7", result.stdout)

  def test_basic_runlength_runs(self) -> None:
    result = run_python("examples/basic/runlength_encoding.janus")
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    self.assertIn("arc[14] = {1, 2, 2, 3, 1, 1", result.stdout)

  def test_basic_sort_runs(self) -> None:
    result = run_python("examples/basic/sort.janus")
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    self.assertIn("list[12] = {0, 1, 2, 3", result.stdout)
    self.assertIn("perm[12] = {3, 2, 0, 1", result.stdout)

  def test_basic_smf_runs(self) -> None:
    result = run_python("examples/basic/smf.janus")
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    self.assertIn("0", result.stdout)


if __name__ == "__main__":
  unittest.main()
