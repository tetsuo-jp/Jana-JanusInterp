These samples are the canonical C-style YANUS syntax fixtures.

- `core_control_flow.ja`: `void`, braces, semicolons, `if/else/fi`, `from/loop/until`, `for`, `local/delocal`, `call/uncall`, `printf`.
- `struct_switch_foreach.ja`: `struct`, field access, struct arrays, `for`, `switch/case/default/break`, parenthesized ternary expressions.
- `char_arrays.ja`: `char` arrays, string literal initialization, indexed updates, `printf`.
- `stack_ops.ja`: `stack`, `push`, `pop`, `empty`, `top`, `size`, `assert`.
- `scanf_printf.ja`: `scanf`, `printf`, and the consume-on-output rule using disposable locals.

These files live under `examples/syntax/` so they do not alter the existing top-level example parity set.
