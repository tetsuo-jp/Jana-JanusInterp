from __future__ import annotations

from dataclasses import dataclass, field

from .ast import SourcePos


@dataclass
class JanaError(Exception):
  pos: SourcePos
  message: str
  details: list[str] = field(default_factory=list)
  contextual: bool = False

  def add_detail(self, detail: str, contextual: bool = True) -> "JanaError":
    return JanaError(self.pos, self.message, self.details + [detail], self.contextual or contextual)

  def __str__(self) -> str:
    if self.contextual:
      parts = [self.message]
      for detail in self.details:
        if detail.startswith("  where "):
          parts.append("\n" + detail)
        else:
          parts.append("," + detail)
      return f"[ERROR (line {self.pos.line})]\n[{''.join(parts)}]"
    if self.pos.filename and not self.pos.line and not self.pos.column:
      return f'File "{self.pos.filename}":\n    {self.message}'
    if self.pos.filename and self.pos.line and self.pos.column:
      return f'File "{self.pos.filename}" in line {self.pos.line}, column {self.pos.column}:\n    {self.message}'
    return f"Error:\n    {self.message}"
