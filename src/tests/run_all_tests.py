from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TIMEOUT = 180


def discover_tests() -> list[Path]:
  return sorted((ROOT / "src/tests").glob("test_*.py"))


def run_one(test_file: Path, pytest_args: list[str], timeout: int) -> tuple[str, int]:
  env = dict(os.environ)
  env["PYTHONPATH"] = str(ROOT / "src")
  cmd = [sys.executable, "-m", "pytest", "-q", str(test_file), *pytest_args]
  try:
    completed = subprocess.run(
      cmd,
      cwd=ROOT,
      env=env,
      text=True,
      capture_output=True,
      timeout=timeout,
      check=False,
    )
  except subprocess.TimeoutExpired as exc:
    print(f"TIMEOUT {test_file} ({timeout}s)")
    if exc.stdout:
      print(exc.stdout.rstrip())
    if exc.stderr:
      print(exc.stderr.rstrip())
    return ("timeout", 124)

  label = "PASS" if completed.returncode == 0 else "FAIL"
  print(f"{label} {test_file}")
  if completed.stdout:
    print(completed.stdout.rstrip())
  if completed.stderr:
    print(completed.stderr.rstrip())
  return (label.lower(), completed.returncode)


def main(argv: list[str] | None = None) -> int:
  parser = argparse.ArgumentParser(description="Run all test files one-by-one with per-file timeouts.")
  parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="per-file timeout in seconds")
  parser.add_argument("paths", nargs="*", help="optional test files to run instead of full discovery")
  parser.add_argument("--", dest="pytest_args", nargs=argparse.REMAINDER)
  args, unknown = parser.parse_known_args(argv)

  tests = [ROOT / path for path in args.paths] if args.paths else discover_tests()
  pytest_args = list(unknown)

  failures: list[str] = []
  timeouts: list[str] = []

  for test_file in tests:
    status, code = run_one(test_file, pytest_args, args.timeout)
    if code == 0:
      continue
    if status == "timeout":
      timeouts.append(str(test_file.relative_to(ROOT)))
    else:
      failures.append(str(test_file.relative_to(ROOT)))

  total = len(tests)
  passed = total - len(failures) - len(timeouts)
  print(f"SUMMARY total={total} passed={passed} failed={len(failures)} timed_out={len(timeouts)}")
  if failures:
    print("FAILED FILES")
    for path in failures:
      print(path)
  if timeouts:
    print("TIMED OUT FILES")
    for path in timeouts:
      print(path)
  return 0 if not failures and not timeouts else 1


if __name__ == "__main__":
  raise SystemExit(main())
