from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


@dataclass(frozen=True)
class SourcePos:
  filename: str
  line: int
  column: int


class IntType(Enum):
  FRESH_VAR = "FreshVar"
  UNBOUND = "Unbound"
  I8 = "I8"
  I16 = "I16"
  I32 = "I32"
  I64 = "I64"
  U8 = "U8"
  U16 = "U16"
  U32 = "U32"
  U64 = "U64"
  INFER_INT = "InferInt"


class DeclType(Enum):
  VARIABLE = "Variable"
  ANCILLA = "Ancilla"
  CONSTANT = "Constant"


class ModOp(Enum):
  ADD_EQ = "+="
  SUB_EQ = "-="
  XOR_EQ = "^="


class UnaryOpKind(Enum):
  NOT = "!"
  BW_NEG = "~"


class BinOpKind(Enum):
  ADD = "+"
  SUB = "-"
  MUL = "*"
  DIV = "/"
  MOD = "%"
  EXP = "**"
  AND = "&"
  OR = "|"
  XOR = "^"
  SL = "<<"
  SR = ">>"
  LAND = "&&"
  LOR = "||"
  GT = ">"
  LT = "<"
  EQ = "="
  NEQ = "!="
  GE = ">="
  LE = "<="


@dataclass(frozen=True)
class Type:
  kind: str
  pos: SourcePos
  int_type: IntType | None = None


@dataclass(frozen=True)
class Ident:
  name: str
  pos: SourcePos


@dataclass(frozen=True)
class Lval:
  ident: Ident
  indices: list["Expr"] = field(default_factory=list)


class Expr:
  pos: SourcePos


@dataclass(frozen=True)
class Number(Expr):
  value: int
  pos: SourcePos


@dataclass(frozen=True)
class Boolean(Expr):
  value: bool
  pos: SourcePos


@dataclass(frozen=True)
class LvalExpr(Expr):
  lval: Lval
  pos: SourcePos


@dataclass(frozen=True)
class UnaryExpr(Expr):
  op: UnaryOpKind
  expr: Expr
  pos: SourcePos


@dataclass(frozen=True)
class TypeCastExpr(Expr):
  typ: Type
  expr: Expr
  pos: SourcePos


@dataclass(frozen=True)
class BinExpr(Expr):
  op: BinOpKind
  left: Expr
  right: Expr
  pos: SourcePos


@dataclass(frozen=True)
class EmptyExpr(Expr):
  ident: Ident
  pos: SourcePos


@dataclass(frozen=True)
class TopExpr(Expr):
  ident: Ident
  pos: SourcePos


@dataclass(frozen=True)
class SizeExpr(Expr):
  ident: Ident
  pos: SourcePos


@dataclass(frozen=True)
class NilExpr(Expr):
  pos: SourcePos


@dataclass(frozen=True)
class ArrayExpr(Expr):
  items: list[Expr]
  pos: SourcePos


@dataclass(frozen=True)
class Vdecl:
  decl_type: DeclType
  typ: Type
  ident: Ident
  dimensions: list[Expr | None]
  init_expr: Expr | None
  pos: SourcePos


@dataclass(frozen=True)
class LocalDecl:
  decl_type: DeclType
  typ: Type
  ident: Ident
  dimensions: list[Expr | None]
  init_expr: Expr | None
  pos: SourcePos


@dataclass(frozen=True)
class Prints:
  kind: str
  text: str | None = None
  idents: list[Ident] = field(default_factory=list)


class Stmt:
  pos: SourcePos


@dataclass(frozen=True)
class AssignStmt(Stmt):
  mod_op: ModOp
  lval: Lval
  expr: Expr
  pos: SourcePos


@dataclass(frozen=True)
class IfStmt(Stmt):
  entry_cond: Expr
  if_part: list[Stmt]
  else_part: list[Stmt]
  exit_cond: Expr
  pos: SourcePos


@dataclass(frozen=True)
class FromStmt(Stmt):
  entry_cond: Expr
  do_part: list[Stmt]
  loop_part: list[Stmt]
  exit_cond: Expr
  pos: SourcePos


@dataclass(frozen=True)
class IterateStmt(Stmt):
  typ: Type
  ident: Ident
  start_expr: Expr
  step_expr: Expr
  end_expr: Expr
  body: list[Stmt]
  pos: SourcePos


@dataclass(frozen=True)
class PushStmt(Stmt):
  expr: Expr
  ident: Ident
  pos: SourcePos


@dataclass(frozen=True)
class PopStmt(Stmt):
  expr: Expr
  ident: Ident
  pos: SourcePos


@dataclass(frozen=True)
class LocalStmt(Stmt):
  enter_decl: LocalDecl
  body: list[Stmt]
  exit_decl: LocalDecl
  pos: SourcePos


@dataclass(frozen=True)
class CallStmt(Stmt):
  ident: Ident
  args: list[Expr]
  external: bool
  pos: SourcePos


@dataclass(frozen=True)
class UncallStmt(Stmt):
  ident: Ident
  args: list[Expr]
  external: bool
  pos: SourcePos


@dataclass(frozen=True)
class UserErrorStmt(Stmt):
  message: str
  pos: SourcePos


@dataclass(frozen=True)
class SwapStmt(Stmt):
  left: Lval
  right: Lval
  pos: SourcePos


@dataclass(frozen=True)
class PrintsStmt(Stmt):
  prints: Prints
  pos: SourcePos


@dataclass(frozen=True)
class SkipStmt(Stmt):
  pos: SourcePos


@dataclass(frozen=True)
class AssertStmt(Stmt):
  expr: Expr
  pos: SourcePos


@dataclass(frozen=True)
class ProcMain:
  vdecls: list[Vdecl]
  stmts: list[Stmt]
  pos: SourcePos


@dataclass(frozen=True)
class Proc:
  procname: Ident
  params: list[Vdecl]
  body: list[Stmt]


@dataclass(frozen=True)
class Program:
  main: ProcMain | None
  procs: list[Proc]

