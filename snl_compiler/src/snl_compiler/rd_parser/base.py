"""递归下降语法分析器 — 基础工具类。"""

from __future__ import annotations
from typing import List, Optional

from snl_compiler.tokens import Token, TokenType
from snl_compiler.syntax_tree import TreeNode


class ParserBase:
    """提供 Token 索引、匹配、前瞻与错误收集的基础能力。"""

    def __init__(self, tokens: List[Token]) -> None:
        self._tokens: List[Token] = tokens # 词法分析器输出的 Token 序列
        self._pos: int = 0 # 当前读到第几个 Token （指针）
        self._errors: List[str] = [] # 收集语法错误

    def _current(self) -> Token: 
        '''
        如果 _pos 越界（正常情况下不应该，但保险起见），返回最后一个 Token（通常是 EOF）
        '''
        return self._tokens[self._pos] if self._pos < len(self._tokens) else self._tokens[-1]

    def _check(self, *types: TokenType) -> bool:
        '''
        检查当前 Token 的类型是否匹配给定的一种或多种类型
        '''
        return self._current().token_type in types

    def _match(self, expected: TokenType) -> TreeNode:
        tok: Token = self._current()
        if tok.token_type == expected:
            self._pos += 1 #  匹配成功，指针前进
            return TreeNode(name=expected.value, token=tok) # 返回叶子节点
        # 匹配失败
        # 关键设计：匹配失败时不抛出异常，而是：
        # 1. 记录错误
        # 2. 返回一个占位节点（让 parser 能继续分析后面的内容，而不是一崩到底）
        # 这就是错误恢复（error recovery）。
        # 如果源码写错了：procedure p
        # self._match(TokenType.PROGRAM)
        # 期望 PROGRAM，实际 PROCEDURE 报错，但 _pos 不前进，返回占位节点
        self._errors.append(
            f"Line {tok.line}, col {tok.col}: 期望 {expected.value}, 实际为 {tok.token_type.value}"
        )
        return TreeNode(name=expected.value, token=tok) # 返回占位节点，继续分析

    def _peek(self, offset: int) -> Optional[Token]:
        '''
        不移动指针，预览未来第 offset 个 Token
        '''
        idx: int = self._pos + offset
        return self._tokens[idx] if idx < len(self._tokens) else None

    def parse(self) -> tuple[Optional[TreeNode], List[str]]:
        '''
        总入口
        '''
        tree: TreeNode = self._program()
        if not self._check(TokenType.EOF):
            t: Token = self._current()
            self._errors.append(f"Line {t.line}, col {t.col}: 程序结束后仍有多余内容")
        return tree, self._errors

    # 非终结符方法由各个 Mixin 提供，组合后在 RecursiveDescentParser 的 MRO 中生效。
