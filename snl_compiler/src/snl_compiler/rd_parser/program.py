"""递归下降语法分析器 — 程序结构（ProgramHead, DeclarePart, ProgramBody）。"""

from __future__ import annotations

from snl_compiler.tokens import TokenType
from snl_compiler.syntax_tree import TreeNode
class ProgramMixin:
    """程序结构 Mixin。"""

    def _program(self) -> TreeNode:
        n = TreeNode("Program")
        n.add_child(self._program_head())
        n.add_child(self._declare_part())
        n.add_child(self._program_body())
        n.add_child(self._match(TokenType.DOT))
        return n

    def _program_head(self) -> TreeNode:
        n = TreeNode("ProgramHead")
        n.add_child(self._match(TokenType.PROGRAM))
        n.add_child(self._match(TokenType.ID))
        return n

    def _declare_part(self) -> TreeNode:
        n = TreeNode("DeclarePart")
        n.add_child(self._type_dec_part())
        n.add_child(self._var_dec_part())
        n.add_child(self._proc_dec_part())
        return n

    def _program_body(self) -> TreeNode:
        n = TreeNode("ProgramBody")
        n.add_child(self._match(TokenType.BEGIN))
        n.add_child(self._stm_list())
        n.add_child(self._match(TokenType.END))
        return n
