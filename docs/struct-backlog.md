# Struct Backlog

Agreed scope:
- Syntax: C-like `struct`
- Field access: `p.x` is a normal l-value
- This phase: simple struct variables, procedure arguments, `show`
- Deferred: arrays of structs, struct fields that are arrays, deeper nesting work unless needed for the base path

Pinned Row 1 decisions:
- Type representation: `Type(kind="struct", name="Pair")`
- Use-site syntax: `Pair p`
- Duplicate field checking: parse first, validate later

Autonomy rule:
- Continue row-by-row without asking for confirmation.
- Stop only when the current row is complete or when an error/blocker cannot be resolved promptly.

Progress format:
`handled:`
`tests:`
`now matches:`
`next unmatched:`

Recommended execution order:
1. `ast + parser`
2. `formatter`
3. `runtime storage`
4. `field l-value access`
5. `procedure arguments`
6. `show/store formatting`
7. `validation + errors`

| Row | Theme | Status | Files | Scoped tests | Done condition |
| --- | --- | --- | --- | --- | --- |
| 1 | Struct declarations in AST and parser | done | `src-python/jana_py/ast.py`, `src-python/jana_py/parser.py` | `python3 -m pytest -q src-python/tests/test_struct_parse.py` | `struct` definitions and variable declarations parse with `Type(kind="struct", name=...)` and use-site syntax `Pair p` |
| 2 | Formatting round-trip | done | `src-python/jana_py/format.py` | `python3 -m pytest -q src-python/tests/test_struct_parse.py` | parsed struct syntax formats back to stable source text |
| 3 | Runtime representation for simple struct values | done | `src-python/jana_py/runtime.py` | `python3 -m pytest -q src-python/tests/test_struct_runtime.py` | struct variables initialize and persist as named-field values |
| 4 | Field access and field update as l-values | done | `src-python/jana_py/runtime.py`, `src-python/jana_py/parser.py` | `python3 -m pytest -q src-python/tests/test_struct_runtime.py` | `p.x` reads and updates behave like ordinary l-values |
| 5 | Procedure argument passing for structs | done | `src-python/jana_py/runtime.py`, `src-python/jana_py/validate.py` | `python3 -m pytest -q src-python/tests/test_struct_runtime.py` | structs can be passed to procedures with field updates visible to caller |
| 6 | `show` and final store formatting | done | `src-python/jana_py/runtime.py`, `src-python/jana_py/format.py` | `python3 -m pytest -q src-python/tests/test_struct_show.py` | struct values render with field names in `show` and final store output |
| 7 | Validation and error surfaces | done | `src-python/jana_py/validate.py`, `src-python/jana_py/errors.py` | `python3 -m pytest -q src-python/tests/test_struct_errors.py` | duplicate fields, unknown fields, and type mismatches fail with stable messages |
| 8 | Arrays of struct variables (`Pair[3] ps`) | done | `src-python/jana_py/parser.py` | `python3 -m pytest -q src-python/tests/test_struct_parse.py src-python/tests/test_struct_runtime.py src-python/tests/test_struct_show.py` | `_starts_vdecl()` recognizes struct arrays; 1D/2D/procedure params all work |

Starter examples:

Success path:
```jana
struct Pair {
    int x,
    int y
}

procedure bump(Pair p)
    p.x += 1

procedure main()
    Pair p
    p.y += 2
    call bump(p)
    show(p)
```

Failure path:
```jana
struct Pair {
    int x
}

procedure main()
    Pair p
    p.y += 1
```
