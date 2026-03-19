# PyJanus Grammar

This document summarizes the grammar accepted by the current Python parser in
[`src/jana_py/parser.py`](/home/a/myclaude/Jana-JanusInterp/src/jana_py/parser.py).

The notation below is EBNF-style rather than strict BNF.

## Lexical Structure

```ebnf
IDENT
  ::= /[A-Za-z][A-Za-z0-9_']*/

NUMBER
  ::= DECIMAL | BINARY

DECIMAL
  ::= /[0-9]+/

BINARY
  ::= /0b[01]+/

STRING
  ::= JSON-style double-quoted string literal

COMMENT
  ::= "//" ... end-of-line
   |  "/*" ... "*/"
```

Reserved keywords:

```text
void procedure main
int i8 i16 i32 i64 u8 u16 u32 u64
char string struct
ancilla constant bool true false
if then else fi
switch case default break
from do loop until
push pop local delocal call uncall external
error skip stack empty top size show print printf scanf nil assert
for in iterate by to end
```

## Grammar

```ebnf
program
  ::= { struct_def | procedure_def } EOF

struct_def
  ::= "struct" ident "{"
        { struct_field [ "," | ";" ] }
      "}" [ ";" ]

struct_field
  ::= type decl_dims ident decl_dims

procedure_def
  ::= main_def | proc_def

main_def
  ::= "void" "main" "(" ")" "{"
        { main_vdecl ";" }
        stmt_block_cstyle
      "}"
   |  "procedure" "main" "(" ")"
        { main_vdecl }
        stmt_block_procstyle

proc_def
  ::= "void" ident params cstyle_body
   |  "procedure" ident params procstyle_body

params
  ::= "(" [ vdecls_noinit { "," vdecls_noinit } ] ")"

cstyle_body
  ::= stmt_block_cstyle

procstyle_body
  ::= stmt_block_procstyle

main_vdecl
  ::= vdecls_init

vdecls_init
  ::= decl_type type decl_dims vdecl_tail_init
      { "," vdecl_tail_init }

vdecls_noinit
  ::= decl_type type decl_dims vdecl_tail_noinit
      { "," vdecl_tail_noinit }

vdecl_tail_init
  ::= ident decl_dims [ "=" array_or_expr ]

vdecl_tail_noinit
  ::= ident decl_dims

decl_type
  ::= "ancilla"
   |  "constant"
   |  ε

type
  ::= "int" | "i8" | "i16" | "i32" | "i64"
   |  "u8"  | "u16" | "u32" | "u64"
   |  "char" | "string"
   |  "bool"
   |  "stack"
   |  ident

decl_dims
  ::= { "[" [ expression ] "]" }

stmt_block_cstyle
  ::= { statement [ ";" ] }

stmt_block_procstyle
  ::= { statement [ ";" ] }

statement
  ::= ancilla_stmt
   |  constant_stmt
   |  if_stmt
   |  switch_stmt
   |  from_stmt
   |  iterate_stmt
   |  for_stmt
   |  push_stmt
   |  pop_stmt
   |  local_stmt
   |  bare_delocal_stmt
   |  call_stmt
   |  uncall_stmt
   |  error_stmt
   |  print_stmt
   |  printf_stmt
   |  scanf_stmt
   |  show_stmt
   |  skip_stmt
   |  assert_stmt
   |  bare_call_stmt
   |  assign_or_swap

assign_or_swap
  ::= lval "<=>" lval
   |  lval ("+=" | "-=" | "^=" | "=") array_or_expr

if_stmt
  ::= "if" "(" expression ")" "{" stmt_block_cstyle "}"
        [ "else" "{" stmt_block_cstyle "}" ]
        [ "fi" [ "(" expression ")" ] ]
        ";"
   |  "if" expression "then"
        stmt_block_procstyle
        [ "else" stmt_block_procstyle ]
        "fi" expression

switch_stmt
  ::= "switch" "(" expression ")" "{"
        { switch_case | switch_default }
      "}"
      [ "switch" [ "(" expression ")" ] ]
      [ ";" ]

switch_case
  ::= "case" expression ":" switch_case_body

switch_default
  ::= "default" ":" switch_case_body

switch_case_body
  ::= { statement [ ";" ] } "break" ";"

from_stmt
  ::= "from" "(" expression ")"
        [ "{" stmt_block_cstyle "}" ]
        "loop" "{" stmt_block_cstyle "}"
        "until" "(" expression ")" ";"
   |  "from" expression
        [ "do" stmt_block_procstyle ]
        [ "loop" stmt_block_procstyle ]
        "until" expression

iterate_stmt
  ::= "iterate" type ident "=" expression
        [ "by" expression ]
        "to" expression
        stmt_block_procstyle
        "end"

for_stmt
  ::= "for" "(" type ident "=" expression ";" expression ";" lval "+=" expression ")"
        "{" stmt_block_cstyle "}"

push_stmt
  ::= "push" "(" expression "," ident ")"

pop_stmt
  ::= "pop" "(" expression "," ident ")"

ancilla_stmt
  ::= "ancilla" "(" local_decl { "," local_decl } ")" "{"
        stmt_block_cstyle
      "}" ";"
   |  "ancilla" local_decl stmt_block_procstyle

constant_stmt
  ::= "constant" local_decl stmt_block_procstyle

local_stmt
  ::= "local" local_decl { "," local_decl }
        (
          "{" stmt_block_cstyle "}" "delocal" local_decl { "," local_decl } ";"
        | stmt_block_procstyle [ "delocal" local_decl { "," local_decl } [ ";" ] ]
        )

bare_delocal_stmt
  ::= "delocal" local_decl
        [ "{" stmt_block_cstyle "}" | stmt_block_procstyle ]

local_decl
  ::= type decl_dims ident decl_dims [ "=" array_or_expr ]

call_stmt
  ::= "call" [ "external" ] ident arg_list

bare_call_stmt
  ::= ident arg_list

uncall_stmt
  ::= "uncall" [ "external" ] ident arg_list

arg_list
  ::= "(" [ expression { "," expression } ] ")"

error_stmt
  ::= "error" "(" string_lit ")"

print_stmt
  ::= "print" "(" string_lit ")"

printf_stmt
  ::= "printf" "(" string_lit [ "," printf_arg { "," printf_arg } ] ")"

scanf_stmt
  ::= "scanf" "(" string_lit [ "," printf_arg { "," printf_arg } ] ")"

show_stmt
  ::= "show" "(" printf_arg { "," printf_arg } ")"

printf_arg
  ::= ident | lval

skip_stmt
  ::= "skip"

assert_stmt
  ::= "assert" expression

array_or_expr
  ::= array_expr
   |  string_lit
   |  expression

array_expr
  ::= "{" array_or_expr { "," array_or_expr } "}"

expression
  ::= binary_expr [ "?" expression ":" expression ]

binary_expr
  ::= prefix_expr { binop prefix_expr }

binop
  ::= "||"
   |  "&&"
   |  "&" | "|" | "^"
   |  "<=" | "<" | ">=" | ">" | "==" | "=" | "!="
   |  "<<" | ">>"
   |  "+" | "-"
   |  "*" | "/" | "%"
   |  "**"

prefix_expr
  ::= ("!" | "~" | "-") prefix_expr
   |  type_cast
   |  term

type_cast
  ::= "(" simple_type ")" prefix_expr

simple_type
  ::= "int" | "i8" | "i16" | "i32" | "i64"
   |  "u8"  | "u16" | "u32" | "u64"
   |  "char" | "string" | "bool" | "stack"

term
  ::= "(" expression ")"
   |  number
   |  "true"
   |  "false"
   |  "empty" "(" ident ")"
   |  "top" "(" ident ")"
   |  "size" "(" ident ")"
   |  "nil"
   |  array_expr
   |  lval

lval
  ::= ident { "." ident | "[" expression "]" }

ident
  ::= IDENT
   |  "main"
   |  "size"

number
  ::= NUMBER

string_lit
  ::= STRING
```

## Notes

- This grammar reflects the current Python parser implementation, not an
  abstract language specification.
- `void ... { ... }` is the C-style syntax; `procedure ...` is the classic
  procedure-style syntax.
- `main()` takes no parameters.
- `=` is accepted both as an equality operator in expressions and as an update
  operator in assignment statements.
- `for` loops are more restricted than they may look:
  the parser currently expects the update to be `ident += expr`, and the
  condition must have the shape `ident < expr`.
- `switch` cases require an explicit `break;`.
- Struct type names are parsed as identifiers.
