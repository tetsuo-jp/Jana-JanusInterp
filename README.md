
# Jana

An interpreter for Janus, the reversible programming language.

## Build and Installation

To build Jana run

    cabal configure
    cabal build

and to install

    cabal install

The program can also be run (assuming all dependencies are installed) by cd'ing
to `src` and then running

    runhaskell Main.hs

For more info about `cabal` see http://www.haskell.org/cabal/.

For building and installation using stack, run

    stack init
    stack install

and the interpreter can then be invoked like this:

    stack exec jana

However, that installation is only local to that folder; to make Jana available
globally, edit your global config in `~/.stack/global-project/stack.yaml`
and add the directory in the `packages` array like so:

    packages:
    - /home/user/path/Jana-JanusInterp

and install it globally, outside the project directory, using

    cd
    stack install path/Jana-JanusInterp

Or, to run it directly using stack, use

    cd src/
    stack exec -- runhaskell Main.hs

## Python Interpreter

The repository also contains a Python implementation under `src/`.
From the repository root, the simplest entry points are the provided `make`
targets:

    make run EXAMPLE=examples/fib.ja
    make debug EXAMPLE=examples/fib.ja
    make invert EXAMPLE=examples/fib.ja

You can also invoke the CLI module directly by setting `PYTHONPATH` to `src`:

    PYTHONPATH=src python3 -m jana_py.cli examples/fib.ja
    PYTHONPATH=src python3 -m jana_py.cli -i examples/fib.ja
    PYTHONPATH=src python3 -m jana_py.cli -d examples/fib.ja

Useful Python-side checks:

    make smoke
    make test
    make rc

Python-side extended examples live under `examples/`; `examples/build-dict.ja` exercises preprocessor macros, ternary expressions, and struct array fields added in the Python implementation.
