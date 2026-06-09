"""SNL 递归下降语法分析器 — 按职责拆分为 Mixin 组合。"""

from __future__ import annotations

from snl_compiler.rd_parser.base import ParserBase
from snl_compiler.rd_parser.program import ProgramMixin
from snl_compiler.rd_parser.declarations import DeclarationsMixin
from snl_compiler.rd_parser.statements import StatementsMixin
from snl_compiler.rd_parser.expressions import ExpressionsMixin


class RecursiveDescentParser(
    ParserBase,
    ProgramMixin,
    DeclarationsMixin,
    StatementsMixin,
    ExpressionsMixin,
):
    """递归下降语法分析器入口。

    通过 Mixin 组合将 104 条文法产生式拆分为：
    - 程序结构 (ProgramMixin)
    - 声明部分 (DeclarationsMixin)
    - 语句部分 (StatementsMixin)
    - 表达式部分 (ExpressionsMixin)
    """

    pass


__all__ = ["RecursiveDescentParser"]
