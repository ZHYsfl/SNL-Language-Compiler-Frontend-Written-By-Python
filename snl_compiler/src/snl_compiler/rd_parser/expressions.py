"""递归下降语法分析器 — 表达式部分（RelExp、Exp、Term、Factor、Variable）。"""

from __future__ import annotations
from typing import Optional

from snl_compiler.tokens import Token, TokenType
from snl_compiler.syntax_tree import TreeNode
class ExpressionsMixin:
    """表达式部分 Mixin。"""

    def _rel_exp(self) -> TreeNode:
        n = TreeNode("RelExp")
        n.add_child(self._exp())
        n.add_child(self._other_rel_e())
        return n

    def _other_rel_e(self) -> TreeNode:
        n = TreeNode("OtherRelE")
        n.add_child(self._cmp_op())
        n.add_child(self._exp())
        return n

    def _exp(self) -> TreeNode:
        n = TreeNode("Exp")
        n.add_child(self._term())
        n.add_child(self._other_term())
        return n

    def _other_term(self) -> Optional[TreeNode]:
        if not self._check(TokenType.PLUS, TokenType.MINUS):
            return None
        n = TreeNode("OtherTerm")
        n.add_child(self._add_op())
        n.add_child(self._exp())
        return n

    def _term(self) -> TreeNode:
        n = TreeNode("Term")
        n.add_child(self._factor())
        n.add_child(self._other_factor())
        return n

    def _other_factor(self) -> Optional[TreeNode]:
        if not self._check(TokenType.TIMES, TokenType.OVER):
            return None
        n = TreeNode("OtherFactor")
        n.add_child(self._mult_op())
        n.add_child(self._term())
        return n

    def _factor(self) -> TreeNode:
        n = TreeNode("Factor")
        if self._check(TokenType.INTC):
            n.add_child(self._match(TokenType.INTC))
        elif self._check(TokenType.LPAREN):
            n.add_child(self._match(TokenType.LPAREN))
            n.add_child(self._exp())
            n.add_child(self._match(TokenType.RPAREN))
        elif self._check(TokenType.ID):
            n.add_child(self._variable())
        else:
            t = self._current()
            self._errors.append(f"Line {t.line}, col {t.col}: 非法因子 '{t.sem_value}'")
        return n

    def _variable(self) -> TreeNode:
        n = TreeNode("Variable")
        n.add_child(self._match(TokenType.ID))
        n.add_child(self._vari_more())
        return n

    def _vari_more(self) -> Optional[TreeNode]:
        if self._check(TokenType.LMIDPAREN):
            n = TreeNode("VariMore")
            n.add_child(self._match(TokenType.LMIDPAREN))
            n.add_child(self._exp())
            n.add_child(self._match(TokenType.RMIDPAREN))
            return n
        if self._check(TokenType.DOT):
            n = TreeNode("VariMore")
            n.add_child(self._match(TokenType.DOT))
            n.add_child(self._field_var())
            return n
        return None

    def _field_var(self) -> TreeNode:
        n = TreeNode("FieldVar")
        n.add_child(self._match(TokenType.ID))
        n.add_child(self._field_var_more())
        return n

    def _field_var_more(self) -> Optional[TreeNode]:
        if not self._check(TokenType.LMIDPAREN):
            return None
        n = TreeNode("FieldVarMore")
        n.add_child(self._match(TokenType.LMIDPAREN))
        n.add_child(self._exp())
        n.add_child(self._match(TokenType.RMIDPAREN))
        return n

    def _cmp_op(self) -> TreeNode:
        n = TreeNode("CmpOp")
        if self._check(TokenType.LT):
            n.add_child(self._match(TokenType.LT))
        elif self._check(TokenType.EQ):
            n.add_child(self._match(TokenType.EQ))
        else:
            t = self._current()
            self._errors.append(f"Line {t.line}, col {t.col}: 期望比较运算符 '<' 或 '='")
        return n

    def _add_op(self) -> TreeNode:
        n = TreeNode("AddOp")
        if self._check(TokenType.PLUS):
            n.add_child(self._match(TokenType.PLUS))
        elif self._check(TokenType.MINUS):
            n.add_child(self._match(TokenType.MINUS))
        return n

    def _mult_op(self) -> TreeNode:
        n = TreeNode("MultOp")
        if self._check(TokenType.TIMES):
            n.add_child(self._match(TokenType.TIMES))
        elif self._check(TokenType.OVER):
            n.add_child(self._match(TokenType.OVER))
        return n
