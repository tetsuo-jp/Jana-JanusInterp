"""Tests for the Janus self-interpreter encoder and execution."""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from jana_py.encode import encode_program, generate_janus, Encoder
from jana_py.parser_janus2026 import parse_program
from jana_py.preprocess import preprocess_text
from jana_py.encode import (
    S_ADDEQ, S_SUBEQ, S_XOREQ, S_SWAP, S_SKIP,
    E_CONST, E_VAR, E_BINOP,
    L_VAR,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
INTERP_PATH = PROJECT_ROOT / "examples" / "self-interp" / "modern_interpreter_cstyle.ja"


def run_encoded(src: str, timeout: int = 60) -> str:
    """Encode source and run through self-interpreter, return stdout."""
    import tempfile
    result = encode_program(src)
    janus_src = generate_janus(result, str(INTERP_PATH))
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ja", delete=False) as f:
        f.write(janus_src)
        tmp_path = f.name
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "jana_py.cli", tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            env={"PYTHONPATH": str(PROJECT_ROOT / "src-python")},
        )
    finally:
        os.unlink(tmp_path)
    if proc.returncode != 0:
        raise RuntimeError(f"PyJanus failed:\n{proc.stderr}")
    return proc.stdout.strip()


def extract_vals(output: str) -> dict[str, str]:
    """Extract variable assignments from output."""
    vals = {}
    for line in output.split("\n"):
        line = line.strip()
        if "=" in line and not line.startswith(("code", "procs", "store", "pc", "num")):
            parts = line.split("=", 1)
            if len(parts) == 2:
                vals[parts[0].strip()] = parts[1].strip()
    return vals


# ── Encoder unit tests ────────────────────────────────────────────────

class TestEncoderBasic:

    def test_encode_addeq_const(self):
        src = "procedure main()\n    int x\n    x += 5\n"
        result = encode_program(src)
        assert result.code[0] == S_ADDEQ

    def test_encode_subeq(self):
        src = "procedure main()\n    int x\n    x -= 3\n"
        result = encode_program(src)
        assert result.code[0] == S_SUBEQ

    def test_encode_xoreq(self):
        src = "procedure main()\n    int x\n    x ^= 7\n"
        result = encode_program(src)
        assert result.code[0] == S_XOREQ

    def test_encode_swap(self):
        src = "procedure main()\n    int x\n    int y\n    x <=> y\n"
        result = encode_program(src)
        assert result.code[0] == S_SWAP

    def test_encode_skip(self):
        src = "procedure main()\n    int x\n    skip\n"
        result = encode_program(src)
        assert result.code[0] == S_SKIP

    def test_encode_binexpr(self):
        src = "procedure main()\n    int x\n    int a\n    int b\n    x += a + b\n"
        result = encode_program(src)
        assert E_BINOP in result.code

    def test_var_slots(self):
        src = "procedure main()\n    int x\n    int y\n    int z\n    x += 1\n"
        result = encode_program(src)
        assert result.var_map["x"].slot == 0
        assert result.var_map["y"].slot == 1
        assert result.var_map["z"].slot == 2

    def test_array_slots(self):
        src = "procedure main()\n    int a[5]\n    int x\n    x += 1\n"
        result = encode_program(src)
        assert result.var_map["a"].slot == 0
        assert result.var_map["a"].size == 5
        assert result.var_map["x"].slot == 5

    def test_procedure_encoding(self):
        src = "procedure inc(int x)\n    x += 1\nprocedure main()\n    int x\n    call inc(x)\n"
        result = encode_program(src)
        assert len(result.procs) == 1
        assert result.procs[0].name == "inc"


# ── Integration tests (encoder + interpreter) ────────────────────────

class TestSelfInterpExecution:

    def test_addeq_const(self):
        output = run_encoded("procedure main()\n    int x\n    x += 5\n")
        assert extract_vals(output)["x"] == "5"

    def test_two_assignments(self):
        output = run_encoded("procedure main()\n    int x\n    x += 3\n    x += 2\n")
        assert extract_vals(output)["x"] == "5"

    def test_subeq(self):
        output = run_encoded("procedure main()\n    int x\n    x += 10\n    x -= 3\n")
        assert extract_vals(output)["x"] == "7"

    def test_xoreq(self):
        output = run_encoded("procedure main()\n    int x\n    x += 5\n    x ^= 3\n")
        assert extract_vals(output)["x"] == "6"

    def test_swap(self):
        src = "procedure main()\n    int x\n    int y\n    x += 3\n    y += 7\n    x <=> y\n"
        vals = extract_vals(run_encoded(src))
        assert vals["x"] == "7"
        assert vals["y"] == "3"

    def test_skip(self):
        output = run_encoded("procedure main()\n    int x\n    x += 1\n    skip\n    x += 2\n")
        assert extract_vals(output)["x"] == "3"

    def test_if_then(self):
        src = textwrap.dedent("""\
            procedure main()
                int x
                int y
                x += 1
                if x = 1 then
                    y += 10
                fi y = 10
        """)
        vals = extract_vals(run_encoded(src))
        assert vals["y"] == "10"

    def test_if_else(self):
        src = textwrap.dedent("""\
            procedure main()
                int x
                int y
                x += 2
                if x = 1 then
                    y += 10
                else
                    y += 20
                fi y = 10
        """)
        vals = extract_vals(run_encoded(src))
        assert vals["y"] == "20"

    def test_procedure_call(self):
        src = textwrap.dedent("""\
            procedure inc(int x)
                x += 1
            procedure main()
                int x
                call inc(x)
                call inc(x)
        """)
        assert extract_vals(run_encoded(src))["x"] == "2"

    def test_uncall(self):
        src = textwrap.dedent("""\
            procedure inc(int x)
                x += 1
            procedure main()
                int x
                call inc(x)
                call inc(x)
                call inc(x)
                uncall inc(x)
        """)
        assert extract_vals(run_encoded(src))["x"] == "2"

    def test_from_until(self):
        src = textwrap.dedent("""\
            procedure main()
                int n
                int x
                n += 3
                from n != 0 do
                    n -= 1
                    x += 1
                loop
                    skip
                until n = 0
        """)
        vals = extract_vals(run_encoded(src))
        assert vals["n"] == "0"
        assert vals["x"] == "3"

    def test_fib(self):
        src = textwrap.dedent("""\
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
        """)
        vals = extract_vals(run_encoded(src))
        assert vals["x1"] == "8"
        assert vals["x2"] == "13"
        assert vals["n"] == "0"


def run_uncall_roundtrip(src: str, timeout: int = 60) -> dict[str, str]:
    """Encode src, run call+uncall through SINT, return post-uncall store values.

    The generated Janus code calls exec_stmts then uncall exec_stmts.
    Post-uncall printf statements are injected to read store values,
    which should all be zero if the interpreter is correct.
    """
    import tempfile
    result = encode_program(src)
    janus_src = generate_janus(result, str(INTERP_PATH))

    # Inject post-uncall printf after the uncall line
    uncall_line = "    uncall exec_stmts(vm);"
    post_printfs = "\n".join(
        f'    printf("post_{name} = %d\\n", vm.store[{vs.slot}]);'
        for name, vs in result.var_map.items()
        if vs.size == 1
    )
    janus_src = janus_src.replace(
        uncall_line,
        uncall_line + "\n" + post_printfs,
    )

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ja", delete=False) as f:
        f.write(janus_src)
        tmp_path = f.name
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "jana_py.cli", tmp_path],
            capture_output=True, text=True, timeout=timeout,
            env={"PYTHONPATH": str(PROJECT_ROOT / "src-python")},
        )
    finally:
        os.unlink(tmp_path)
    if proc.returncode != 0:
        raise RuntimeError(f"PyJanus failed:\n{proc.stderr}")

    output = proc.stdout.strip()
    vals = {}
    for line in output.split("\n"):
        line = line.strip()
        if line.startswith("post_") and "=" in line:
            parts = line.split("=", 1)
            if len(parts) == 2:
                vals[parts[0].strip()[5:]] = parts[1].strip()
    return vals


# ── Phase 2a: Array element operations ──────────────────────────────

class TestArrayOperations:

    def test_array_addeq(self):
        src = textwrap.dedent("""\
            procedure main()
                int a[3]
                int x
                a[0] += 5
                x += a[0]
        """)
        assert extract_vals(run_encoded(src))["x"] == "5"

    def test_array_subeq(self):
        src = textwrap.dedent("""\
            procedure main()
                int a[3]
                int x
                a[0] += 10
                a[0] -= 3
                x += a[0]
        """)
        assert extract_vals(run_encoded(src))["x"] == "7"

    def test_array_xoreq(self):
        src = textwrap.dedent("""\
            procedure main()
                int a[3]
                int x
                a[0] += 5
                a[0] ^= 3
                x += a[0]
        """)
        assert extract_vals(run_encoded(src))["x"] == "6"

    def test_array_swap(self):
        src = textwrap.dedent("""\
            procedure main()
                int a[3]
                int x
                int y
                a[0] += 3
                a[1] += 7
                a[0] <=> a[1]
                x += a[0]
                y += a[1]
        """)
        vals = extract_vals(run_encoded(src))
        assert vals["x"] == "7"
        assert vals["y"] == "3"

    def test_array_indexed_by_var(self):
        src = textwrap.dedent("""\
            procedure main()
                int a[5]
                int i
                int x
                i += 2
                a[i] += 42
                x += a[2]
                i -= 2
        """)
        assert extract_vals(run_encoded(src))["x"] == "42"


# ── Phase 2b: Uncall reversal tests ─────────────────────────────────

class TestUncallReverse:

    def test_uncall_reverses_simple(self):
        """x += 5 → call then uncall → x = 0."""
        vals = run_uncall_roundtrip(
            "procedure main()\n    int x\n    x += 5\n"
        )
        assert vals["x"] == "0"

    def test_uncall_reverses_fib(self):
        """fib(5) → call then uncall → all variables zero."""
        src = textwrap.dedent("""\
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
        """)
        vals = run_uncall_roundtrip(src)
        assert vals["x1"] == "0"
        assert vals["x2"] == "0"
        assert vals["n"] == "0"

    def test_uncall_reverses_loop(self):
        """from/until loop → call then uncall → all variables zero."""
        src = textwrap.dedent("""\
            procedure main()
                int n
                int x
                n += 3
                from n != 0 do
                    n -= 1
                    x += 1
                loop
                    skip
                until n = 0
        """)
        vals = run_uncall_roundtrip(src)
        assert vals["n"] == "0"
        assert vals["x"] == "0"


# ── Phase 2c: Complex structures ────────────────────────────────────

class TestComplexStructures:

    def test_nested_if(self):
        src = textwrap.dedent("""\
            procedure main()
                int x
                int y
                int z
                x += 2
                if x = 2 then
                    y += 1
                    if y = 1 then
                        z += 100
                    fi z = 100
                fi z = 100
        """)
        vals = extract_vals(run_encoded(src))
        assert vals["z"] == "100"

    @pytest.mark.skip(reason=(
        "Nested from/until loops: store[gs] go-flag accumulates across "
        "recursion levels in exec_from_body. Requires per-invocation "
        "scratch slot allocation to fix."
    ))
    def test_nested_loops(self):
        src = textwrap.dedent("""\
            procedure main()
                int i
                int j
                int sum
                i += 3
                from i != 0 do
                    j += 2
                    from j != 0 do
                        j -= 1
                        sum += 1
                    loop
                        skip
                    until j = 0
                    i -= 1
                loop
                    skip
                until i = 0
        """)
        vals = extract_vals(run_encoded(src))
        assert vals["i"] == "0"
        assert vals["j"] == "0"
        assert vals["sum"] == "6"

    def test_mutual_recursion(self):
        src = textwrap.dedent("""\
            procedure even_check(int n, int r)
                if n = 0 then
                    r += 1
                else
                    n -= 1
                    call odd_check(n, r)
                    n += 1
                fi n = 0
            procedure odd_check(int n, int r)
                if n = 0 then
                    skip
                else
                    n -= 1
                    call even_check(n, r)
                    n += 1
                fi n = 0
            procedure main()
                int n
                int r
                n += 4
                call even_check(n, r)
        """)
        vals = extract_vals(run_encoded(src))
        assert vals["n"] == "4"
        assert vals["r"] == "1"


# ── Phase 3: Tower of interpreters ──────────────────────────────────

class TestTowerOfInterpreters:

    def test_tower_1level_forward(self):
        """P on SINT → correct result (explicit tower-level-1 test)."""
        output = run_encoded("procedure main()\n    int x\n    x += 5\n")
        assert extract_vals(output)["x"] == "5"

    def test_tower_1level_backward(self):
        """call P then uncall P on SINT → store all zeros."""
        vals = run_uncall_roundtrip(
            "procedure main()\n    int x\n    x += 5\n"
        )
        assert vals["x"] == "0"

    @pytest.mark.skip(reason=(
        "Level-2 tower requires parameter binding in SINT "
        "(current encoder uses flat store without argument-parameter aliasing)"
    ))
    def test_tower_2level(self):
        """P on SINT on SINT → same result (requires parameter binding)."""
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
