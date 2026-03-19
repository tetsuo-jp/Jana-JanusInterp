# Jana-JanusInterp

An interpreter for **Janus**, a reversible programming language. Reversible computing allows programs to be run both forward and backward, with every operation being logically invertible.

## Project Overview

This repository contains two primary implementations of the Janus interpreter:
1.  **Haskell (Core):** The original and feature-rich implementation, supporting reversible debugging (Lanese/Vidal semantics), C++ code generation, and finite field arithmetic.
2.  **Python:** A modern implementation that adds features like preprocessor macros, ternary expressions, and struct array fields. It also includes a comprehensive regression test suite.

### Key Features
- **Forward & Backward Execution:** Procedures can be `call`ed (forward) or `uncall`ed (backward).
- **Inversion:** Automatically generate the inverse of a Janus program.
- **Reversible Debugger:** Step forward and backward through program execution with true reversibility.
- **C++ Codegen:** Transpile Janus code to C++ for performance or integration.
- **Modular Arithmetic:** Support for $n$-bit modular arithmetic and $GF(p)$ finite field arithmetic.

## Building and Running

### Haskell Interpreter
The Haskell implementation is located in `src/`.

**Building:**
- Using Cabal: `cabal configure && cabal build`
- Using Stack: `stack build`
- Using GHC/Make: `cd src && make opt` (produces binary at `bin/janus`)

**Running:**
```bash
# Using the compiled binary
./bin/janus [options] <file.ja>

# Using runhaskell
cd src && runhaskell Main.hs [options] <file.ja>
```

**Common Options:**
- `-m[n]`: $n$-bit modular arithmetic (default 32).
- `-p[n]`: $GF(n)$ finite field arithmetic.
- `-i`: Print the inverted program.
- `-c`: Generate C++ code.
- `-d`: Interactive debug mode.
- `-r`: Reversible debugger mode.

### Python Interpreter
The Python implementation is located in `src-python/`.

**Running:**
```bash
PYTHONPATH=src-python python3 -m jana_py.cli [options] <file.ja>
```

**Common Options:**
- `-a`: Show AST.
- `-i`: Invert program.
- `-c`: Generate C code.
- `-d`: Debug mode.
- `--circuit`: Generate circuit representation.

## Testing

The primary regression tests are Python-based and use `pytest`.

**Run Python Tests:**
```bash
# Run all regression tests
python3 src-python/tests/run_release_candidate.py

# Run specific tests with pytest
PYTHONPATH=src-python pytest src-python/tests/test_local_parity.py
```

## Project Structure

- `src/`: Haskell source code.
  - `Jana/Ast.hs`: Abstract Syntax Tree definition.
  - `Jana/Parser.hs`: Janus parser.
  - `Jana/Eval.hs`: Interpreter engine.
  - `Jana/RevDebugger.hs`: Reversible debugger.
- `src-python/`: Python source code.
  - `jana_py/`: Core logic (parser, ast, runtime, codegen).
  - `tests/`: Regression test suite.
- `basicExamples/` & `examples/`: Janus program examples (e.g., `fib.ja`, `sort.ja`).
- `docs/`: Feature backlogs and documentation for recent updates.
- `web/`: Web-based interface for the interpreter.

## Development Conventions

- **Reversibility:** Always ensure new language constructs or library functions are logically reversible.
- **Parity:** The Python and Haskell implementations should ideally maintain parity in behavior, especially for core Janus semantics.
- **Testing:** New features should be accompanied by regression tests in `src-python/tests/`.
- **AST:** When modifying the language, update both the Haskell (`src/Jana/Ast.hs`) and Python (`src-python/jana_py/ast.py`) AST definitions.
