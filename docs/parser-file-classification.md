# Parser File Classification

This file records the intended parser family for checked-in Janus/Jana program files.

Primary parser means the parser the repository should treat as the file's main home.
Some files may also parse under a second parser, but that is compatibility, not ownership.

## Parser Families

| Parser | Intended syntax |
| --- | --- |
| `janus2026` | C-style `void`, braces, semicolons, structs, macros, `for`, `switch`, char arrays |
| `jana2014` | non-basic Jana `procedure ...(...)`, typed parameters, `procedure main()`, non-C-style blocks |
| `jana2014basic` | `ParserBasic`-style global-first Jana, implicit global params, no explicit parameter lists |
| `janus1982` | strict 1982 Janus, global variables only, no parameter lists, `:` swap, `#` not-equal, `\\` mod, `;` comments |
| `janus1982ext` | extended 1982-style syntax; compatibility bucket, not the preferred home unless stated |

## Classified Files

| Files | Primary parser | Notes |
| --- | --- | --- |
| `examples/janus1982/counter.ja` | `janus1982` | Uses global-only 1982 syntax, `;` comments, no parameter lists |
| `examples/janus1982/factor.ja` | `janus1982` | Uses `:` swap, `#`, `\\`, global-only procedures |
| `examples/janus1982/fib.ja` | `janus1982` | Classic 1982 Fibonacci |
| `examples/janus1982/sort.ja` | `janus1982` | Classic 1982 bubble sort |
| `examples/janus1982/sqrt.ja` | `janus1982` | Classic 1982 square root |
| `examples/janus1982/swap.ja` | `janus1982` | Uses 1982 swap and XOR-update notation |
| `tests/fib.janusb` | `janus1982` | Legacy/global-only Janus sample, closest to strict 1982 family |
| `examples/jana/interpreter.ja` | `jana2014` | `procedure` syntax with typed parameters and non-C-style bodies |
| `examples/jana/modern_interpreter.ja` | `jana2014` | Same non-C-style `procedure` family; also uses newer extensions |
| `examples/jana/opcodes.ja` | `jana2014` | Include-only helper for the `examples/jana/` programs |
| `tests/errors/*.ja` | `jana2014` | Primary non-C-style typed test corpus: `procedure main()`, typed locals/params, no `void` |
| `src/tests/fixtures/from_debug_simple.ja` | `jana2014` | Non-C-style typed fixture |
| `src/tests/fixtures/iterate_debug_simple.ja` | `jana2014` | Non-C-style typed fixture |
| `src/tests/fixtures/local_backward_simple.ja` | `jana2014` | Non-C-style typed fixture with explicit params |
| `examples/build-dict.ja` | `janus2026` | C-style `void`, structs, macros, char aliases |
| `examples/caesar.ja` | `janus2026` | C-style `void`, char arrays, `%s`, `for` |
| `examples/factor.ja` | `janus2026` | C-style `void`, braces, semicolons |
| `examples/fib.ja` | `janus2026` | C-style `void` Fibonacci |
| `examples/linked-list.ja` | `janus2026` | C-style `void`, structs, macros |
| `examples/matrixmult.ja` | `janus2026` | C-style `void`, `for`, braces |
| `examples/matrixmult_v1.0.ja` | `janus2026` | C-style `void` procedure shell with modern blocks |
| `examples/perm-to-code.ja` | `janus2026` | C-style `void`, braces, `show` |
| `examples/run-length-enc.ja` | `janus2026` | C-style `void` and braces |
| `examples/run-length-enc-stack.ja` | `janus2026` | C-style `void`, stack features |
| `examples/self-interp/modern_interpreter_cstyle.ja` | `janus2026` | Explicitly C-style self-interpreter |
| `examples/self-interp/modern_interpreter_full.ja` | `janus2026` | Full C-style self-interpreter |
| `examples/self-interp/opcodes.ja` | `janus2026` | Include-only helper for the self-interpreter files |
| `examples/sort-network.ja` | `janus2026` | C-style `void`, structs |
| `examples/sqrt.ja` | `janus2026` | C-style `void` square root |
| `examples/stack-operations.ja` | `janus2026` | C-style `void`, stack operations |
| `examples/syntax/char_arrays.ja` | `janus2026` | Syntax coverage for modern C-style parser |
| `examples/syntax/core_control_flow.ja` | `janus2026` | Syntax coverage for modern C-style parser |
| `examples/syntax/declarations.ja` | `janus2026` | Syntax coverage for modern C-style parser |
| `examples/syntax/from_empty_do.ja` | `janus2026` | Syntax coverage for modern C-style parser |
| `examples/syntax/scanf_printf.ja` | `janus2026` | Syntax coverage for modern C-style parser |
| `examples/syntax/stack_ops.ja` | `janus2026` | Syntax coverage for modern C-style parser |
| `examples/syntax/struct_switch_foreach.ja` | `janus2026` | Syntax coverage for modern C-style parser |
| `examples/syntax/test_cstyle.ja` | `janus2026` | Syntax coverage for modern C-style parser |
| `examples/syntax/test_for_iter.ja` | `janus2026` | Syntax coverage for modern C-style parser |
| `examples/test2.ja` | `janus2026` | C-style `void` example |

## Current Gaps

| Parser | Current checked-in primary files |
| --- | --- |
| `jana2014basic` | none |

`jana2014basic` currently exists for compatibility with upstream `ParserBasic.hs`, but there is no checked-in example or fixture that should be treated as primarily `jana2014basic`.
