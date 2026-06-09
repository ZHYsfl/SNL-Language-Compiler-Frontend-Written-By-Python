"""语义分析公共基类 — 提供树遍历辅助与错误收集。"""

from __future__ import annotations
from typing import List, Optional

from snl_compiler.tokens import Token
from snl_compiler.syntax_tree import TreeNode
from snl_compiler.symbol_table import SymbolTable


class SemanticBase:
    """语义分析公共基类。"""

    def __init__(self, symtab: SymbolTable, errors: List[str]) -> None:
        self._symtab: SymbolTable = symtab
        self._errors: List[str] = errors

    def _error(self, line: int, msg: str) -> None:
        self._errors.append(f"Line {line}: {msg}")

    def _token(self, node: Optional[TreeNode], idx: int) -> Optional[Token]:
        if node is None or idx >= len(node.children):
            return None
        c = node.children[idx]
        return c.token if c.token is not None else None

    def _child(self, node: Optional[TreeNode], idx: int) -> Optional[TreeNode]:
        if node is None or idx >= len(node.children):
            return None
        return node.children[idx]

    def _child_by_name(self, node: Optional[TreeNode], name: str) -> Optional[TreeNode]:
        if node is None:
            return None
        for c in node.children:
            if c.name == name:
                return c
        return None
