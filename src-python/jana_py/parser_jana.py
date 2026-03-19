"""Jana (JanusInterp) syntax parser — parser_jana.py

Faithfully implements the grammar from:
  Jana.ParserBasic  (https://github.com/kirkedal/Jana-JanusInterp)

Key differences from parser1982.py / the C-style parser
========================================================
  - Global variable declarations are typeless (before any `procedure`)
  - All procedures receive global variables as implicit params (mirroring
    ParserBasic.hs: `return Proc { params = globs, ... }`)
  - call/uncall automatically pass all global variables as arguments
  - Assignment operators: only `+=`, `-=`, `^=`  (no bare `=`, no `!=`)
  - Swap: `<=>` only  (no `:`)
  - Not-equal: `!=` only as comparison  (no `#`)
  - Modulo: `%` only  (no `\\`)
  - No `**`, `<<`, `>>` binary operators
  - Operator precedence follows ParserBasic.hs exactly
  - `then` is required in `if` statements
  - Procedures have no explicit parameter list  (`procedure foo`)
  - Comments: `//` and `/* */`  (no `;`)
  - `main_fwd` is treated as the main entry point when no `main` exists
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Sequence

from .ast import (
    AssignStmt,
    AssertStmt,
    BareDelocalStmt,
    BareLocalStmt,
    BinExpr,
    BinOpKind,
    Boolean,
    CallStmt,
    DeclType,
    EmptyExpr,
    Expr,
    FromStmt,
    Ident,
    IfStmt,
    IntType,
    LocalDecl,
    LocalStmt,
    Lval,
    LvalExpr,
    LvalIndex,
    ModOp,
    NilExpr,
    Number,
    PopStmt,
    Prints,
    PrintsStmt,
    Proc,
    ProcMain,
    Program,
    PushStmt,
    SizeExpr,
    SkipStmt,
    SourcePos,
    StringLiteral,
    SwapStmt,
    TopExpr,
    Type,
    UnaryExpr,
    UnaryOpKind,
    UncallStmt,
    UserErrorStmt,
    Vdecl,
)
from .errors import JanaError
from .preprocess import LineOrigin


# ---------------------------------------------------------------------------
# Keywords  (ParserBasic.hs reservedNames; int/true/false are NOT reserved)
# ---------------------------------------------------------------------------
KEYWORDS = {
    "procedure",
    "if", "then", "else", "fi",
    "from", "do", "loop", "until",
    "call", "uncall",
    "skip",
    # I/O kept for compatibility
    "read", "write",
    # extras from full Jana.Parser
    "local", "delocal",
    "push", "pop",
    "print", "printf", "show",
    "assert", "error",
    "ancilla", "constant",
    "empty", "top", "size", "nil",
    "true", "false",
    "external",
}

# ---------------------------------------------------------------------------
# Tokeniser
# ---------------------------------------------------------------------------
TOKEN_RE = re.compile(
    r"""
    (?P<SPACE>\s+)
    |(?P<COMMENT>//[^\n]*|/\*.*?\*/)
    |(?P<STRING>"(?:\\.|[^"\\])*")
    |(?P<NUMBER>0b[01]+|\d+)
    |(?P<OP>
        <=>
        |\+=|-=|\^=
        |!=|<=|>=|&&|\|\|
        |=|<|>
        |\+|-|\*\*|\*|/|%|\^|&|\|
        |!|~
        |,|\(|\)|\[|\]|\{|\}
     )
    |(?P<IDENT>[A-Za-z][A-Za-z0-9_']*)
    |(?P<MISMATCH>.)
    """,
    re.DOTALL | re.VERBOSE,
)

# ---------------------------------------------------------------------------
# Binary operator precedence  (mirrors ParserBasic.hs binOperators)
# Outermost list = lowest precedence (parsed first)
# ---------------------------------------------------------------------------
BIN_PRECEDENCE = [
    {"ops": {"||": BinOpKind.LOR},                                        "assoc": "left"},
    {"ops": {"&&": BinOpKind.LAND},                                       "assoc": "left"},
    {"ops": {"&": BinOpKind.AND, "|": BinOpKind.OR, "^": BinOpKind.XOR}, "assoc": "left"},
    {"ops": {
        "<=": BinOpKind.LE, "<": BinOpKind.LT,
        ">=": BinOpKind.GE, ">": BinOpKind.GT,
        "=":  BinOpKind.EQ, "!=": BinOpKind.NEQ,
    }, "assoc": "left"},
    {"ops": {"+": BinOpKind.ADD, "-": BinOpKind.SUB},                    "assoc": "left"},
    {"ops": {"*": BinOpKind.MUL, "/": BinOpKind.DIV, "%": BinOpKind.MOD}, "assoc": "left"},
]


# ---------------------------------------------------------------------------
# Token / TokenStream
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    pos: SourcePos


class TokenStream:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.index = 0

    def peek(self, n: int = 0) -> Token:
        idx = self.index + n
        return self.tokens[min(idx, len(self.tokens) - 1)]

    def consume(self) -> Token:
        token = self.peek()
        self.index += 1
        return token

    def match(self, kind: str, value: str | None = None) -> Token | None:
        token = self.peek()
        if token.kind != kind:
            return None
        if value is not None and token.value != value:
            return None
        self.index += 1
        return token

    def expect(self, kind: str, value: str | None = None) -> Token:
        token = self.peek()
        if token.kind != kind or (value is not None and token.value != value):
            shown = token.value if token.kind != "EOF" else "end of input"
            if value is not None:
                raise JanaError(token.pos, f'Unexpected "{shown}"\n    Expecting "{value}"')
            raise JanaError(token.pos, f'Unexpected "{shown}"\n    Expecting {kind}')
        self.index += 1
        return token


# ---------------------------------------------------------------------------
# Tokenise
# ---------------------------------------------------------------------------
def tokenize(
    filename: str,
    text: str,
    line_origins: Sequence[LineOrigin] | None = None,
) -> list[Token]:
    line = 1
    col = 1
    tokens: list[Token] = []
    for match in TOKEN_RE.finditer(text):
        kind = match.lastgroup
        value = match.group()
        origin = None
        if line_origins is not None and 1 <= line <= len(line_origins):
            origin = line_origins[line - 1]
        pos = SourcePos(
            origin.filename if origin else filename,
            origin.line    if origin else line,
            col,
        )
        line_breaks = value.count("\n")
        if line_breaks:
            col = len(value.rsplit("\n", 1)[-1]) + 1
            line += line_breaks
        else:
            col += len(value)
        if kind in {"SPACE", "COMMENT"}:
            continue
        if kind == "IDENT" and value in KEYWORDS:
            tokens.append(Token("KW", value, pos))
            continue
        tokens.append(Token(kind, value, pos))

    origin = None
    if line_origins:
        eof_line = line
        overshoot = eof_line - len(line_origins)
        if overshoot > 0:
            last = line_origins[-1]
            origin = LineOrigin(filename=last.filename, line=last.line + overshoot)
        else:
            origin = line_origins[min(max(eof_line - 1, 0), len(line_origins) - 1)]
    eof_pos = SourcePos(
        origin.filename if origin else filename,
        origin.line    if origin else line,
        1,
    )
    tokens.append(Token("EOF", "", eof_pos))
    return tokens


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------
_PROC_END = {"procedure", "EOF"}

# Type-keyword map (for optional typed locals / ancilla)
_INT_TYPES = {
    "int": IntType.UNBOUND,
    "i8": IntType.I8, "i16": IntType.I16, "i32": IntType.I32, "i64": IntType.I64,
    "u8": IntType.U8, "u16": IntType.U16, "u32": IntType.U32, "u64": IntType.U64,
}


class Parser:
    def __init__(
        self,
        filename: str,
        text: str,
        line_origins: Sequence[LineOrigin] | None = None,
    ):
        self.tokens = TokenStream(tokenize(filename, text, line_origins))
        # Global variables — set in parse_program, used in call/uncall and Proc params
        self._global_vdecls: list[Vdecl] = []

    # ------------------------------------------------------------------
    # Top-level
    # ------------------------------------------------------------------
    def parse_program(self) -> Program:
        """Parse: global var decls followed by procedures."""
        global_vdecls: list[Vdecl] = []
        while self._is_global_vdecl():
            global_vdecls.append(self._parse_global_vdecl())

        # Store so call/uncall can reference them
        self._global_vdecls = global_vdecls

        mains: list[ProcMain] = []
        procs: list[Proc] = []
        while self.tokens.peek().kind != "EOF":
            result = self._parse_procedure()
            if isinstance(result, ProcMain):
                mains.append(result)
            else:
                procs.append(result)

        # Attach globals to main
        if global_vdecls and mains:
            m = mains[0]
            mains[0] = ProcMain(global_vdecls + m.vdecls, m.stmts, m.pos)
        elif global_vdecls and not mains:
            p = self.tokens.peek().pos
            mains.append(ProcMain(global_vdecls, [], p))

        if len(mains) > 1:
            raise JanaError(
                self.tokens.peek().pos,
                "Multiple main procedures defined",
            )
        return Program(mains[0] if mains else None, procs, [])

    def _is_global_vdecl(self) -> bool:
        """True when the next token starts a typeless global variable."""
        t0 = self.tokens.peek()
        if t0.kind != "IDENT":
            return False
        t1 = self.tokens.peek(1)
        # Stop at anything that looks like a procedure or statement
        return t1.value not in {"(", "{", "}", "<=>", "+=", "-=", "^="}

    def _parse_global_vdecl(self) -> Vdecl:
        """Parse one typeless global: `name` or `name[size]`."""
        pos = self.tokens.peek().pos
        ident = self._parse_ident()
        dimensions: list[Expr | None] = []
        while self.tokens.match("OP", "["):
            if self.tokens.match("OP", "]"):
                dimensions.append(None)
            else:
                dimensions.append(self._parse_expression())
                self.tokens.expect("OP", "]")
        typ = Type("int", pos, IntType.UNBOUND)
        return Vdecl(DeclType.VARIABLE, typ, ident, dimensions, None, pos)

    # ------------------------------------------------------------------
    # Procedures
    # ------------------------------------------------------------------
    def _parse_procedure(self) -> ProcMain | Proc:
        start = self.tokens.peek()
        if start.kind != "KW" or start.value != "procedure":
            raise JanaError(start.pos, f'Unexpected "{start.value}"\n    Expecting "procedure"')
        self.tokens.consume()
        ident = self._parse_ident(allow_main=True)

        # Optional empty parens
        self.tokens.match("OP", "(")
        self.tokens.match("OP", ")")

        body = self._parse_stmt_block(_PROC_END)
        if not body:
            raise JanaError(ident.pos, "Expecting statement")

        if ident.name in {"main", "main_fwd"}:
            return ProcMain([], body, ident.pos)

        # Non-main procedures receive all globals as implicit params
        # (mirrors: `return Proc { params = globs, body = stats }` in ParserBasic.hs)
        return Proc(ident, list(self._global_vdecls), body)

    # ------------------------------------------------------------------
    # Statement block
    # ------------------------------------------------------------------
    def _parse_stmt_block(self, end_keywords: set[str]) -> list:
        stmts = []
        while True:
            token = self.tokens.peek()
            if token.kind == "EOF":
                break
            if token.kind == "KW" and token.value in end_keywords:
                break
            if token.kind == "OP" and token.value == "}":
                break
            stmts.append(self._parse_statement())
        return stmts

    # ------------------------------------------------------------------
    # Statements
    # ------------------------------------------------------------------
    def _parse_statement(self):
        token = self.tokens.peek()
        if token.kind == "KW":
            dispatch = {
                "if":      self._parse_if_stmt,
                "from":    self._parse_from_stmt,
                "call":    self._parse_call_stmt,
                "uncall":  self._parse_uncall_stmt,
                "skip":    self._parse_skip_stmt,
                "read":    self._parse_read_stmt,
                "write":   self._parse_write_stmt,
                "local":   self._parse_local_stmt,
                "delocal": self._parse_bare_delocal_stmt,
                "push":    self._parse_push_stmt,
                "pop":     self._parse_pop_stmt,
                "print":   self._parse_print_stmt,
                "printf":  self._parse_printf_stmt,
                "show":    self._parse_show_stmt,
                "assert":  self._parse_assert_stmt,
                "error":   self._parse_error_stmt,
                "ancilla": self._parse_ancilla_stmt,
                "constant": self._parse_constant_stmt,
            }
            if token.value in dispatch:
                return dispatch[token.value]()
        return self._parse_assign_or_swap()

    def _parse_assign_or_swap(self):
        try:
            left = self._parse_lval()
        except JanaError as err:
            token = self.tokens.peek()
            if err.message.endswith("Expecting expression"):
                raise JanaError(token.pos, f'Unexpected "{token.value}"\n    Expecting statement')
            raise
        pos = self.tokens.peek().pos
        if op := self.tokens.match("OP", "<=>"):
            right = self._parse_lval()
            return SwapStmt(left, right, op.pos)
        for value, modop in [("+=", ModOp.ADD_EQ), ("-=", ModOp.SUB_EQ), ("^=", ModOp.XOR_EQ)]:
            if self.tokens.match("OP", value):
                return AssignStmt(modop, left, self._parse_expression(), pos)
        raise JanaError(self.tokens.peek().pos, "Expecting statement")

    def _parse_if_stmt(self) -> IfStmt:
        pos = self._expect_kw("if").pos
        entry = self._parse_expression()
        self._expect_kw("then")          # required in Jana (not optional)
        if_part = self._parse_stmt_block({"else", "fi"})
        else_part: list = []
        if self.tokens.match("KW", "else"):
            else_part = self._parse_stmt_block({"fi"})
        self._expect_kw("fi")
        exit_cond = self._parse_expression()
        return IfStmt(entry, if_part, else_part, exit_cond, pos)

    def _parse_from_stmt(self) -> FromStmt:
        pos = self._expect_kw("from").pos
        entry = self._parse_expression()
        do_part: list = []
        loop_part: list = []
        if self.tokens.match("KW", "do"):
            do_part = self._parse_stmt_block({"loop", "until"})
        if self.tokens.match("KW", "loop"):
            loop_part = self._parse_stmt_block({"until"})
        self._expect_kw("until")
        exit_cond = self._parse_expression()
        return FromStmt(entry, do_part, loop_part, exit_cond, pos)

    def _global_args(self, pos: SourcePos) -> list[Expr]:
        """Build LvalExpr list for all global variables (passed to call/uncall)."""
        return [LvalExpr(Lval(v.ident, []), pos) for v in self._global_vdecls]

    def _parse_call_stmt(self) -> CallStmt:
        pos = self._expect_kw("call").pos
        external = self.tokens.match("KW", "external") is not None
        ident = self._parse_ident(allow_main=True)
        # Optional empty parens (basic Jana has none; be lenient)
        if self.tokens.match("OP", "("):
            self.tokens.expect("OP", ")")
        # Pass all global variables as args (ParserBasic.hs: `Call procname idents pos`)
        return CallStmt(ident, self._global_args(pos), external, pos)

    def _parse_uncall_stmt(self) -> UncallStmt:
        pos = self._expect_kw("uncall").pos
        external = self.tokens.match("KW", "external") is not None
        ident = self._parse_ident(allow_main=True)
        if self.tokens.match("OP", "("):
            self.tokens.expect("OP", ")")
        return UncallStmt(ident, self._global_args(pos), external, pos)

    def _parse_skip_stmt(self) -> SkipStmt:
        return SkipStmt(self._expect_kw("skip").pos)

    def _parse_read_stmt(self) -> PrintsStmt:
        pos = self._expect_kw("read").pos
        return PrintsStmt(Prints("read", args=[self._parse_lval()]), pos)

    def _parse_write_stmt(self) -> PrintsStmt:
        pos = self._expect_kw("write").pos
        return PrintsStmt(Prints("write", args=[self._parse_lval()]), pos)

    def _parse_push_stmt(self) -> PushStmt:
        pos = self._expect_kw("push").pos
        self.tokens.expect("OP", "(")
        expr = self._parse_expression()
        self.tokens.expect("OP", ",")
        ident = self._parse_ident()
        self.tokens.expect("OP", ")")
        return PushStmt(expr, ident, pos)

    def _parse_pop_stmt(self) -> PopStmt:
        pos = self._expect_kw("pop").pos
        self.tokens.expect("OP", "(")
        expr = self._parse_expression()
        self.tokens.expect("OP", ",")
        ident = self._parse_ident()
        self.tokens.expect("OP", ")")
        return PopStmt(expr, ident, pos)

    def _parse_local_stmt(self):
        pos = self._expect_kw("local").pos
        decl = self._parse_local_decl()
        end = {"delocal"} | _PROC_END | {"else", "fi", "loop", "until"}
        body = self._parse_stmt_block(end)
        tok = self.tokens.peek()
        if tok.kind == "KW" and tok.value == "delocal":
            self._expect_kw("delocal")
            exit_decl = self._parse_local_decl()
            self.tokens.match("OP", ";")
            return LocalStmt(decl, body, exit_decl, pos)
        return BareLocalStmt(decl, body, pos)

    def _parse_bare_delocal_stmt(self):
        pos = self._expect_kw("delocal").pos
        decl = self._parse_local_decl()
        body = self._parse_stmt_block(set())
        return BareDelocalStmt(decl, body, pos)

    def _parse_ancilla_stmt(self):
        pos = self._expect_kw("ancilla").pos
        decl = self._parse_local_decl_with_dtype(DeclType.ANCILLA, pos)
        body = self._parse_stmt_block(_PROC_END | {"else", "fi", "loop", "until"})
        return LocalStmt(decl, body, decl, pos)

    def _parse_constant_stmt(self):
        pos = self._expect_kw("constant").pos
        decl = self._parse_local_decl_with_dtype(DeclType.CONSTANT, pos)
        body = self._parse_stmt_block(_PROC_END | {"else", "fi", "loop", "until"})
        return LocalStmt(decl, body, decl, pos)

    def _parse_local_decl(self) -> LocalDecl:
        return self._parse_local_decl_with_dtype(DeclType.VARIABLE, self.tokens.peek().pos)

    def _parse_local_decl_with_dtype(self, dtype: DeclType, pos: SourcePos) -> LocalDecl:
        typ = self._try_parse_type(pos)
        ident = self._parse_ident()
        dimensions: list[Expr | None] = []
        while self.tokens.match("OP", "["):
            if self.tokens.match("OP", "]"):
                dimensions.append(None)
            else:
                dimensions.append(self._parse_expression())
                self.tokens.expect("OP", "]")
        init_expr = None
        if self.tokens.match("OP", "="):
            init_expr = self._parse_expression()
        return LocalDecl(dtype, typ, ident, dimensions, init_expr, pos)

    def _try_parse_type(self, pos: SourcePos) -> Type:
        t = self.tokens.peek()
        if t.kind == "KW" and t.value in _INT_TYPES:
            self.tokens.consume()
            return Type("int", t.pos, _INT_TYPES[t.value])
        if t.kind == "KW" and t.value == "stack":
            self.tokens.consume()
            return Type("stack", t.pos)
        return Type("int", pos, IntType.UNBOUND)

    def _parse_print_stmt(self) -> PrintsStmt:
        pos = self._expect_kw("print").pos
        self.tokens.expect("OP", "(")
        text = self._parse_string()
        self.tokens.expect("OP", ")")
        return PrintsStmt(Prints("print", text=text), pos)

    def _parse_printf_stmt(self) -> PrintsStmt:
        pos = self._expect_kw("printf").pos
        self.tokens.expect("OP", "(")
        text = self._parse_string()
        args: list = []
        while self.tokens.match("OP", ","):
            lv = self._parse_lval()
            args.append(lv.ident if not lv.selectors else lv)
        self.tokens.expect("OP", ")")
        return PrintsStmt(Prints("printf", text=text, args=args), pos)

    def _parse_show_stmt(self) -> PrintsStmt:
        pos = self._expect_kw("show").pos
        self.tokens.expect("OP", "(")
        args = [self._parse_ident()]
        while self.tokens.match("OP", ","):
            args.append(self._parse_ident())
        self.tokens.expect("OP", ")")
        return PrintsStmt(Prints("show", args=args), pos)

    def _parse_assert_stmt(self) -> AssertStmt:
        pos = self._expect_kw("assert").pos
        return AssertStmt(self._parse_expression(), pos)

    def _parse_error_stmt(self) -> UserErrorStmt:
        pos = self._expect_kw("error").pos
        self.tokens.expect("OP", "(")
        msg = self._parse_string()
        self.tokens.expect("OP", ")")
        return UserErrorStmt(msg, pos)

    # ------------------------------------------------------------------
    # Expressions
    # ------------------------------------------------------------------
    def _parse_expression(self) -> Expr:
        return self._parse_binary_level(0)

    def _parse_binary_level(self, level: int) -> Expr:
        if level == len(BIN_PRECEDENCE):
            return self._parse_prefix()
        left = self._parse_binary_level(level + 1)
        while True:
            token = self.tokens.peek()
            ops = BIN_PRECEDENCE[level]["ops"]
            if token.kind == "OP" and token.value in ops:
                self.tokens.consume()
                right = self._parse_binary_level(level + 1)
                left = BinExpr(ops[token.value], left, right, token.pos)
            else:
                return left

    def _parse_prefix(self) -> Expr:
        token = self.tokens.peek()
        if token.kind == "OP" and token.value == "!":
            self.tokens.consume()
            return UnaryExpr(UnaryOpKind.NOT, self._parse_prefix(), token.pos)
        if token.kind == "OP" and token.value == "~":
            self.tokens.consume()
            return UnaryExpr(UnaryOpKind.BW_NEG, self._parse_prefix(), token.pos)
        if token.kind == "OP" and token.value == "-":
            self.tokens.consume()
            return BinExpr(BinOpKind.SUB, Number(0, token.pos), self._parse_prefix(), token.pos)
        return self._parse_term()

    def _parse_term(self) -> Expr:
        token = self.tokens.peek()
        if token.kind == "OP" and token.value == "(":
            self.tokens.consume()
            expr = self._parse_expression()
            self.tokens.expect("OP", ")")
            return expr
        if token.kind == "NUMBER":
            self.tokens.consume()
            if token.value.startswith("0b"):
                return Number(int(token.value[2:], 2), token.pos)
            return Number(int(token.value), token.pos)
        if token.kind == "KW" and token.value in {"true", "false"}:
            self.tokens.consume()
            return Boolean(token.value == "true", token.pos)
        if token.kind == "KW" and token.value == "empty":
            self.tokens.consume()
            self.tokens.expect("OP", "(")
            ident = self._parse_ident()
            self.tokens.expect("OP", ")")
            return EmptyExpr(ident, token.pos)
        if token.kind == "KW" and token.value == "top":
            self.tokens.consume()
            self.tokens.expect("OP", "(")
            ident = self._parse_ident()
            self.tokens.expect("OP", ")")
            return TopExpr(ident, token.pos)  # type: ignore[return-value]
        if token.kind == "KW" and token.value == "size":
            self.tokens.consume()
            self.tokens.expect("OP", "(")
            ident = self._parse_ident()
            self.tokens.expect("OP", ")")
            return SizeExpr(ident, token.pos)
        if token.kind == "KW" and token.value == "nil":
            self.tokens.consume()
            return NilExpr(token.pos)
        if token.kind in {"IDENT", "KW"}:
            lval = self._parse_lval()
            return LvalExpr(lval, lval.ident.pos)
        raise JanaError(token.pos, f'Unexpected "{token.value}"\n    Expecting expression')

    # ------------------------------------------------------------------
    # Lvalue
    # ------------------------------------------------------------------
    def _parse_lval(self) -> Lval:
        ident = self._parse_ident()
        selectors = []
        while self.tokens.match("OP", "["):
            selectors.append(LvalIndex(self._parse_expression()))
            self.tokens.expect("OP", "]")
        return Lval(ident, selectors)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _parse_ident(self, allow_main: bool = False) -> Ident:
        token = self.tokens.peek()
        if token.kind == "IDENT":
            self.tokens.consume()
            return Ident(token.value, token.pos)
        if allow_main and token.kind == "KW" and token.value == "main":
            self.tokens.consume()
            return Ident("main", token.pos)
        raise JanaError(token.pos, "Expecting identifier")

    def _parse_string(self) -> str:
        return json.loads(self.tokens.expect("STRING").value)

    def _expect_kw(self, value: str) -> Token:
        return self.tokens.expect("KW", value)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def parse_program(
    filename: str,
    text: str,
    line_origins: Sequence[LineOrigin] | None = None,
) -> Program:
    return Parser(filename, text, line_origins).parse_program()
