# Preprocessor Backlog

Scope order:
1. `object macro`
2. `function macro`
3. `include`
4. `source map`
5. `escapes`
6. `conditionals`

Progress format:
`handled:`
`tests:`
`now matches:`
`next unmatched:`

| Row | Theme | Status | Files | Scoped tests | Done condition |
| --- | --- | --- | --- | --- | --- |
| 1 | Object-like macros: `#define`, `#undef`, line continuation | done | `src-python/jana_py/preprocess.py`, `src-python/jana_py/cli.py` | `python3 -m pytest -q src-python/tests/test_preprocess_define.py` | Object macros expand, undef removes, and multiline defines stay correct |
| 2 | Function-like macros | done | `src-python/jana_py/preprocess.py` | `python3 -m pytest -q src-python/tests/test_preprocess_define.py` | Positional arguments expand without breaking nested parens or commas in strings |
| 3 | Includes | done | `src-python/jana_py/preprocess.py`, `src-python/jana_py/cli.py` | `python3 -m pytest -q src-python/tests/test_preprocess_include.py` | Relative includes work, cycles fail, and post-code includes are rejected |
| 4 | Source mapping | done | `src-python/jana_py/preprocess.py`, `src-python/jana_py/parser.py`, `src-python/jana_py/cli.py` | `python3 -m pytest -q src-python/tests/test_preprocess_source_map.py` | Parse errors after preprocessing report original file and line |
| 5 | Escape handling | done | `src-python/jana_py/preprocess.py`, `src-python/jana_py/parser.py`, `src-python/jana_py/runtime.py` | `python3 -m pytest -q src-python/tests/test_preprocess_escape.py src-python/tests/test_char_array_support.py` | Escaped strings stay intact through preprocessing and `%s` / `print` output |
| 6 | Conditional directives | done | `src-python/jana_py/preprocess.py` | `python3 -m pytest -q src-python/tests/test_preprocess_conditionals.py` | `#ifdef/#ifndef/#else/#endif` behave consistently with current macro table |

Minimal regression commands:
- `python3 -m pytest -q src-python/tests/test_preprocess_define.py`
- `python3 -m pytest -q src-python/tests/test_preprocess_include.py`
- `python3 -m pytest -q src-python/tests/test_preprocess_source_map.py`
- `python3 -m pytest -q src-python/tests/test_preprocess_escape.py`
- `python3 -m pytest -q src-python/tests/test_preprocess_conditionals.py`
- `python3 -m pytest -q src-python/tests/test_char_array_support.py`

Broader nearby regression:
- `python3 -m pytest -q src-python/tests/test_step3_success.py src-python/tests/test_step4_success.py`
