# Janus BNF (default parser)

この文書は、デフォルトのパーサ `src/jana_py/parser_janus2026.py` (`--std janus2026`) が受理する構文をコードベースから整理したものです。実装上は一部 EBNF 的な繰り返し・省略を持つため、ここでは補助非終端を導入した BNF で表します。

## 字句

```bnf
<identifier> ::= <letter> <identifier-rest>
<identifier-rest> ::= "" | <identifier-char> <identifier-rest>
<identifier-char> ::= <letter> | <digit> | "_" | "'"

<number> ::= <decimal-number> | <binary-number>
<decimal-number> ::= <digit> | <digit> <decimal-number>
<binary-number> ::= "0b" <binary-digit> | "0b" <binary-digit> <binary-tail>
<binary-tail> ::= "" | <binary-digit> <binary-tail>

<string-literal> ::= JSON string literal

<letter> ::= "A" | ... | "Z" | "a" | ... | "z"
<digit> ::= "0" | ... | "9"
<binary-digit> ::= "0" | "1"
```

`// ...` と `/* ... */` はコメントとして無視されます。空白も自由に入れられます。

予約語:

```text
void main int i8 i16 i32 i64 u8 u16 u32 u64
char string struct ancilla constant bool true false if then else fi
for from do loop until push pop local delocal call uncall
external error stack empty top size printf nil
assert iterate by to end read write switch case default break scanf
```

## プログラム全体

```bnf
<program> ::= <top-list> <eof>

<top-list> ::= ""
             | <top-item> <top-list>

<top-item> ::= <struct-def>
             | <proc-def>
             | <main-def>
```

## 構造体定義

```bnf
<struct-def> ::= "struct" <field-identifier> "{" <struct-fields-opt> "}" <opt-semicolon>

<struct-fields-opt> ::= ""
                      | <struct-field> <struct-fields-tail>

<struct-fields-tail> ::= ""
                       | <field-sep> <struct-fields-opt>

<field-sep> ::= ","
              | ";"

<struct-field> ::= <type> <decl-dims> <field-identifier> <decl-dims>
```

`<field-identifier>` は通常の `<identifier>` に加えて `size` も許されます。

## 手続きと main

```bnf
<proc-def> ::= "void" <identifier> <params> <brace-stmt-block>

<main-def> ::= "void" "main" "{" <main-vdecls> <stmt-list> "}"
             | "void" "main" "(" ")" "{" <main-vdecls> <stmt-list> "}"

<params> ::= "(" ")"
           | "(" <param-list> ")"

<param-list> ::= <vdecl-no-init>
               | <vdecl-no-init> "," <param-list>

<main-vdecls> ::= ""
                | <main-vdecl> ";" <main-vdecls>

<main-vdecl> ::= <decl-type> <type> <main-vdecl-item> <main-vdecl-tail>

<main-vdecl-tail> ::= ""
                    | "," <main-vdecl-item> <main-vdecl-tail>

<main-vdecl-item> ::= <decl-dims> <identifier> <decl-dims> <init-opt>
```

## 型と宣言

```bnf
<decl-type> ::= ""
              | "ancilla"
              | "constant"

<type> ::= "int" | "i8" | "i16" | "i32" | "i64"
         | "u8" | "u16" | "u32" | "u64"
         | "char" | "string"
         | "stack"
         | "bool"
         | <struct-type-name>

<struct-type-name> ::= <identifier>

<vdecl-no-init> ::= <decl-type> <type> <decl-dims> <identifier> <decl-dims>

<local-decl> ::= <type> <decl-dims> <identifier> <decl-dims> <init-opt>

<decl-dims> ::= ""
              | <decl-dim> <decl-dims>

<decl-dim> ::= "[" "]"
             | "[" <expression> "]"

<init-opt> ::= ""
             | "=" <array-or-expr>
```

`<struct-type-name>` は、それ以前に `struct` 定義として現れた識別子だけが使えます。

## 文ブロック

```bnf
<brace-stmt-block> ::= "{" <stmt-list> "}"

<stmt-block-no-braces> ::= <stmt-list>

<stmt-list> ::= <statement> <stmt-tail>

<stmt-tail> ::= ""
              | <opt-semicolon> <stmt-list>

<opt-semicolon> ::= ""
                  | ";"
```

実装上、多くの場所で文末セミコロンは任意です。`switch` の各 `case` は `break;` が必須です。

## 文

```bnf
<statement> ::= <ancilla-stmt>
              | <constant-stmt>
              | <if-stmt>
              | <switch-stmt>
              | <from-stmt>
              | <for-stmt>
              | <iterate-stmt>
              | <push-stmt>
              | <pop-stmt>
              | <local-stmt>
              | <call-stmt>
              | <uncall-stmt>
              | <bare-call-stmt>
              | <error-stmt>
              | <printf-stmt>
              | <scanf-stmt>
              | <read-stmt>
              | <write-stmt>
              | <assert-stmt>
              | <assign-stmt>
              | <swap-stmt>
```

### 局所宣言系

```bnf
<ancilla-stmt> ::= "ancilla" <local-decl> <stmt-list-opt-until-delocal-boundary>
<constant-stmt> ::= "constant" <local-decl> <stmt-list-opt-until-delocal-boundary>

<local-stmt> ::= "local" <local-decl-list> <brace-local-tail>
               | "local" <local-decl-list> <plain-local-tail>

<local-decl-list> ::= <local-decl>
                    | <local-decl> "," <local-decl-list>

<brace-local-tail> ::= "{" <stmt-list-opt> "}" "delocal" <local-decl-list-same-arity> <opt-semicolon>

<plain-local-tail> ::= <stmt-list-opt-until-delocal> "delocal" <local-decl-list-same-arity>

<local-decl-list-same-arity> ::= <local-decl>
                               | <local-decl> "," <local-decl-list-same-arity>

<stmt-list-opt> ::= ""
                  | <stmt-list>

<stmt-list-opt-until-delocal> ::= ""
                                | <stmt-list>

<stmt-list-opt-until-delocal-boundary> ::= ""
                                         | <stmt-list>
```

`ancilla` / `constant` 文は、実装上 `delocal` を持たず、対応する `LocalStmt` として構築されます。

### 制御構文

```bnf
<if-stmt> ::= "if" <expression> <then-opt> <if-body> <else-opt> <fi-opt>

<then-opt> ::= ""
             | "then"

<if-body> ::= <brace-stmt-block>
            | <stmt-list-opt-until-else-or-fi>

<else-opt> ::= ""
             | "else" <else-body>

<else-body> ::= <brace-stmt-block>
              | <stmt-list-opt-until-fi>

<fi-opt> ::= ""
           | "fi" <exit-expr-opt>

<exit-expr-opt> ::= ""
                  | <expression>

<switch-stmt> ::= "switch" "(" <expression> ")" "{"
                    <switch-case-list> <default-opt>
                  "}" <switch-exit-opt> <opt-semicolon>

<switch-case-list> ::= ""
                     | <switch-case> <switch-case-list>

<switch-case> ::= "case" <expression> ":" <case-body>

<case-body> ::= <case-stmt-list> "break" ";"

<case-stmt-list> ::= ""
                   | <statement> <opt-semicolon> <case-stmt-list>

<default-opt> ::= ""
                | "default" ":" <case-body>

<switch-exit-opt> ::= ""
                    | "switch"
                    | "switch" "(" <expression> ")"

<from-stmt> ::= "from" <expression> <from-do-opt> <from-loop-opt> "until" <expression> <opt-semicolon>

<from-do-opt> ::= ""
                | "do" <stmt-list-opt-until-loop-or-until>
                | <brace-stmt-block>

<from-loop-opt> ::= ""
                  | "loop" <stmt-list-opt-until-until>
                  | "loop" <brace-stmt-block>

<for-stmt> ::= "for" "(" <type> <identifier> "=" <expression> ";"
                         <expression> ";"
                         <lval> "+=" <expression> ")"
               <brace-stmt-block>

<iterate-stmt> ::= "iterate" <type> <identifier> "=" <expression> <by-opt> "to" <expression>
                   <stmt-list-opt-until-end> "end"

<by-opt> ::= ""
           | "by" <expression>
```

`for` 文は構文上もっと一般的に見えても、実装では条件が `<identifier> < <expression>` でなければ拒否されます。

### 呼び出し・入出力・基本文

```bnf
<push-stmt> ::= "push" "(" <expression> "," <identifier> ")"
<pop-stmt> ::= "pop" "(" <expression> "," <identifier> ")"

<call-stmt> ::= "call" <external-opt> <callable-ident> <arg-list>
<uncall-stmt> ::= "uncall" <external-opt> <callable-ident> <arg-list>
<bare-call-stmt> ::= <callable-ident> <arg-list>

<external-opt> ::= ""
                 | "external"

<callable-ident> ::= <identifier>
                   | "main"

<arg-list> ::= "(" ")"
             | "(" <expr-list> ")"

<error-stmt> ::= "error" "(" <string-literal> ")"
<printf-stmt> ::= "printf" "(" <string-literal> <printf-args-opt> ")"
<scanf-stmt> ::= "scanf" "(" <string-literal> <printf-args-opt> ")"
<read-stmt> ::= "read" <lval>
<write-stmt> ::= "write" <lval>
<assert-stmt> ::= "assert" <expression>

<printf-args-opt> ::= ""
                    | "," <printf-arg-list>

<printf-arg-list> ::= <printf-arg>
                    | <printf-arg> "," <printf-arg-list>

<printf-arg> ::= <identifier>
               | <lval-with-selector>

```

### 代入・交換

```bnf
<assign-stmt> ::= <lval> "+=" <binary-expression>
                | <lval> "-=" <binary-expression>
                | <lval> "^=" <binary-expression>

<swap-stmt> ::= <lval> "<=>" <lval>
```

ここで右辺は `parse_binary_level(0)` で読まれるため、裸の三項演算子は不可です。必要なら括弧で囲みます。

## 式

```bnf
<expression> ::= <binary-expression>
               | <binary-expression> "?" <expression> ":" <expression>

<binary-expression> ::= <logical-or-expr>

<logical-or-expr> ::= <logical-and-expr>
                    | <logical-or-expr> "||" <logical-and-expr>

<logical-and-expr> ::= <bitwise-expr>
                     | <logical-and-expr> "&&" <bitwise-expr>

<bitwise-expr> ::= <compare-expr>
                 | <bitwise-expr> "&" <compare-expr>
                 | <bitwise-expr> "|" <compare-expr>
                 | <bitwise-expr> "^" <compare-expr>

<compare-expr> ::= <shift-expr>
                 | <compare-expr> "<=" <shift-expr>
                 | <compare-expr> "<" <shift-expr>
                 | <compare-expr> ">=" <shift-expr>
                 | <compare-expr> ">" <shift-expr>
                 | <compare-expr> "=" <shift-expr>
                 | <compare-expr> "==" <shift-expr>
                 | <compare-expr> "!=" <shift-expr>

<shift-expr> ::= <add-expr>
               | <shift-expr> "<<" <add-expr>
               | <shift-expr> ">>" <add-expr>

<add-expr> ::= <mul-expr>
             | <add-expr> "+" <mul-expr>
             | <add-expr> "-" <mul-expr>

<mul-expr> ::= <pow-expr>
             | <mul-expr> "*" <pow-expr>
             | <mul-expr> "/" <pow-expr>
             | <mul-expr> "%" <pow-expr>

<pow-expr> ::= <prefix-expr>
             | <pow-expr> "**" <prefix-expr>

<prefix-expr> ::= <term>
                | "!" <prefix-expr>
                | "-" <prefix-expr>
                | "(" <type> ")" <prefix-expr>
```

`**` は実装上、右結合ではなく左結合として解析されます。なお、実装内部には `~` の分岐がありますが、字句規則で `~` がトークン化されないため、デフォルトパーサでは実際には受理されません。

## 項、配列、左辺値

```bnf
<term> ::= "(" <expression> ")"
         | <number>
         | "true"
         | "false"
         | "empty" "(" <identifier> ")"
         | "top" "(" <identifier> ")"
         | "size" "(" <identifier> ")"
         | "nil"
         | <array-expr>
         | <lval>

<array-expr> ::= "{" <array-item-list> "}"

<array-item-list> ::= <array-or-expr>
                    | <array-or-expr> "," <array-item-list>

<array-or-expr> ::= <array-expr>
                  | <string-literal>
                  | <expression>

<lval> ::= <identifier> <selector-list>

<lval-with-selector> ::= <identifier> <nonempty-selector-list>

<selector-list> ::= ""
                  | <selector> <selector-list>

<nonempty-selector-list> ::= <selector>
                           | <selector> <nonempty-selector-list>

<selector> ::= "." <field-identifier>
             | "[" <expression> "]"

<expr-list> ::= <expression>
              | <expression> "," <expr-list>
```

## 実装依存の注意

```bnf
<stmt-list-opt-until-else-or-fi> ::= ""
                                   | <stmt-list>
<stmt-list-opt-until-fi> ::= ""
                           | <stmt-list>
<stmt-list-opt-until-loop-or-until> ::= ""
                                      | <stmt-list>
<stmt-list-opt-until-until> ::= ""
                              | <stmt-list>
<stmt-list-opt-until-end> ::= ""
                            | <stmt-list>
```

これらは「どこで止まるか」が周囲のキーワード (`else`, `fi`, `loop`, `until`, `end`, `delocal` など) に依存する実装都合の補助規則です。

`void main() { ... }` の本体は空でも受理されます。通常の手続き本体は、実装上は少なくとも 1 文必要です。
