"""SNL 语法树 AST 节点定义。

语法分析模块输出语法树，语义分析模块消费语法树。
树节点设计需与语义分析遍历逻辑兼容。
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

from snl_compiler.tokens import Token


@dataclass
class TreeNode:
    """语法树节点。

    - name: 非终结符名称（如 "Program"）或终结符类型名（如 "ID"）
    - token: 终结符节点携带的原始 Token；非终结符节点为 None
    - children: 子节点列表，按文法产生式顺序排列
    """

    name: str
    token: Optional[Token] = None
    children: List[TreeNode] = field(default_factory=list)

    def add_child(self, child: Optional[TreeNode]) -> None:
        """安全地添加子节点，忽略 None。"""
        if child is not None:
            self.children.append(child)

    def __repr__(self) -> str:
        if self.token is not None:
            return f"Leaf({self.token.token_type.value}, '{self.token.sem_value}')"
        child_names: List[str] = [
            c.name if c.token is None else c.token.sem_value for c in self.children
        ]
        return f"Node({self.name}, children={child_names})"
