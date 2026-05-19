PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
PYTEST ?= $(PYTHON) -m pytest
TEST_RUNNER ?= $(PYTHON) src/tests/run_all_tests.py
PYTHONPATH := src
export PYTHONPATH

EXAMPLE ?= examples/fib.ja
PYTEST_ARGS ?=

.PHONY: help install prepare-test-env test test-all smoke rc run debug ast invert cgen clean

help:
	@printf '%s\n' \
	  'Available targets:' \
	  '  make install        Install the Python package in editable mode' \
	  '  make prepare-test-env  Create compatibility paths used by older tests' \
	  '  make test           Run the full Python test suite' \
	  '  make test-all       Alias for test' \
	  '  make smoke          Run a small smoke subset' \
	  '  make rc             Run the release-candidate regression wrapper' \
	  '  make run EXAMPLE=examples/fib.ja' \
	  '  make debug EXAMPLE=examples/fib.ja' \
	  '  make ast EXAMPLE=examples/fib.ja' \
	  '  make invert EXAMPLE=examples/fib.ja' \
	  '  make cgen EXAMPLE=examples/fib.ja' \
	  '  make clean          Remove Python cache files'

install:
	$(PIP) install -e src

prepare-test-env:
	@test -e src-python || ln -s src src-python

test: prepare-test-env test-all

test-all: prepare-test-env
	$(TEST_RUNNER) $(PYTEST_ARGS)

smoke: prepare-test-env
	$(PYTEST) -q \
	  src/tests/test_cstyle_syntax.py \
	  src/tests/test_basic_examples.py \
	  $(PYTEST_ARGS)

rc: prepare-test-env
	$(PYTEST) -q src/tests/test_cstyle_syntax.py src/tests/test_syntax_examples.py
	$(PYTEST) -q src/tests/test_self_interp.py -k 'not if_else and not from_until and not fib and not uncall and not mutual_recursion and not tower_1level_backward'
	$(PYTEST) -q src/tests/test_struct_parse.py src/tests/test_struct_runtime.py
	$(PYTEST) -q src/tests/test_char_array_support.py
	$(PYTEST) -q src/tests/test_basic_examples.py

run:
	$(PYTHON) -m jana_py.cli $(EXAMPLE)

debug:
	$(PYTHON) -m jana_py.cli -d $(EXAMPLE)

ast:
	$(PYTHON) -m jana_py.cli -a $(EXAMPLE)

invert:
	$(PYTHON) -m jana_py.cli -i $(EXAMPLE)

cgen:
	$(PYTHON) -m jana_py.cli -c $(EXAMPLE)

clean:
	find . -type d \( -name '__pycache__' -o -name '.pytest_cache' -o -name '.ruff_cache' \) -prune -exec rm -rf {} +
