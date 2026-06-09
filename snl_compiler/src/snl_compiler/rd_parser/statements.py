"""递归下降语法分析器 — 语句部分（StmList、各类语句、实参列表）。"""

from __future__ import annotations
from typing import Optional

from snl_compiler.tokens import Token, TokenType
from snl_compiler.syntax_tree import TreeNode
class StatementsMixin:
    """语句部分 Mixin。"""

    def _stm_list(self) -> TreeNode:
        n = TreeNode("StmList")
        n.add_child(self._stm())
        n.add_child(self._stm_more())
        return n

    def _stm_more(self) -> Optional[TreeNode]:
        if not self._check(TokenType.SEMI):
            return None
        n = TreeNode("StmMore")
        n.add_child(self._match(TokenType.SEMI))
        n.add_child(self._stm_list())
        return n

    def _stm(self) -> TreeNode:
        n = TreeNode("Stm")
        if self._check(TokenType.IF):
            n.add_child(self._conditional_stm())
        elif self._check(TokenType.WHILE):
            n.add_child(self._loop_stm())
        elif self._check(TokenType.READ):
            n.add_child(self._input_stm())
        elif self._check(TokenType.WRITE):
            n.add_child(self._output_stm())
        elif self._check(TokenType.RETURN):
            n.add_child(self._return_stm())
        elif self._check(TokenType.ID):
            n.add_child(self._match(TokenType.ID))
            n.add_child(self._ass_call())
        else:
            t = self._current()
            self._errors.append(f"Line {t.line}, col {t.col}: 非法语句起始 '{t.sem_value}'")
        return n

    def _ass_call(self) -> TreeNode:
        if self._check(TokenType.LPAREN):
            n = TreeNode("CallStmRest")
            n.add_child(self._match(TokenType.LPAREN))
            n.add_child(self._act_param_list())
            n.add_child(self._match(TokenType.RPAREN))
            return n
        n = TreeNode("AssignmentRest")
        n.add_child(self._vari_more())
        n.add_child(self._match(TokenType.ASSIGN))
        n.add_child(self._exp())
        return n

    def _conditional_stm(self) -> TreeNode:
        n = TreeNode("ConditionalStm")
        n.add_child(self._match(TokenType.IF))
        n.add_child(self._rel_exp())
        n.add_child(self._match(TokenType.THEN))
        n.add_child(self._stm_list())
        n.add_child(self._match(TokenType.ELSE))
        n.add_child(self._stm_list())
        n.add_child(self._match(TokenType.FI))
        return n

    def _loop_stm(self) -> TreeNode:
        n = TreeNode("LoopStm")
        n.add_child(self._match(TokenType.WHILE))
        n.add_child(self._rel_exp())
        n.add_child(self._match(TokenType.DO))
        n.add_child(self._stm_list())
        n.add_child(self._match(TokenType.ENDWH))
        return n

    def _input_stm(self) -> TreeNode:
        n = TreeNode("InputStm")
        n.add_child(self._match(TokenType.READ))
        n.add_child(self._match(TokenType.LPAREN))
        n.add_child(self._match(TokenType.ID))
        n.add_child(self._match(TokenType.RPAREN))
        return n

    def _output_stm(self) -> TreeNode:
        n = TreeNode("OutputStm")
        n.add_child(self._match(TokenType.WRITE))
        n.add_child(self._match(TokenType.LPAREN))
        n.add_child(self._exp())
        n.add_child(self._match(TokenType.RPAREN))
        return n

    def _return_stm(self) -> TreeNode:
        n = TreeNode("ReturnStm")
        n.add_child(self._match(TokenType.RETURN))
        n.add_child(self._match(TokenType.LPAREN))
        n.add_child(self._exp())
        n.add_child(self._match(TokenType.RPAREN))
        return n

    def _act_param_list(self) -> Optional[TreeNode]:
        return None if self._check(TokenType.RPAREN) else TreeNode("ActParamList", children=[self._exp(), self._act_param_more()])

    def _act_param_more(self) -> Optional[TreeNode]:
        if not self._check(TokenType.COMMA):
            return None
        n = TreeNode("ActParamMore")
        n.add_child(self._match(TokenType.COMMA))
        n.add_child(self._act_param_list())
        return n
