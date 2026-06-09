"""SNL 语义分析 — 表达式检查与公共辅助。

提供类型推导、赋值兼容性检查、公共树遍历辅助。
被 SemanticStmt 继承以复用表达式能力。
"""

from __future__ import annotations
from typing import List, Optional

from snl_compiler.tokens import Token, TokenType
from snl_compiler.syntax_tree import TreeNode
from snl_compiler.types import TypeKind, TypeIR, FieldChain
from snl_compiler.symbol_table import SymbolTable, SymbolEntry, IdentifierKind
from snl_compiler.semantic_base import SemanticBase


class SemanticExpr(SemanticBase):
    """表达式语义分析基类。"""

    def __init__(self, symtab: SymbolTable, errors: List[str], int_type: TypeIR, char_type: TypeIR) -> None:
        super().__init__(symtab, errors)
        self._int_type: TypeIR = int_type
        self._char_type: TypeIR = char_type

    def _check_arith(self, t1: Optional[TypeIR], t2: Optional[TypeIR]) -> Optional[TypeIR]:
        if t1 is None or t2 is None:
            return None
        if t1.type_kind != t2.type_kind:
            return None
        if t1.type_kind in (TypeKind.ARRAY_TY, TypeKind.RECORD_TY):
            return None
        return t1

    def _check_cmp(self, t1: Optional[TypeIR], t2: Optional[TypeIR], op: str, line: int) -> None:
        if t1 is None or t2 is None or t1.type_kind != t2.type_kind or t1.type_kind in (TypeKind.ARRAY_TY, TypeKind.RECORD_TY):
            self._error(line, f'比较运算符 "{op}" 的分量类型不相容')

    # ------------------------------------------------------------------
    # 表达式
    # ------------------------------------------------------------------
    def _exp(self, node: Optional[TreeNode]) -> Optional[TypeIR]:
        if node is None:
            return None
        t1 = self._term(self._child(node, 0))
        other = self._child_by_name(node, "OtherTerm")
        if other is None:
            return t1
        op, line = self._op_info(self._child(other, 0))
        t2 = self._exp(self._child(other, 1))
        if self._check_arith(t1, t2) is None:
            self._error(line, f'运算符 "{op}" 的分量类型不相容')
            return None
        return t1

    def _term(self, node: Optional[TreeNode]) -> Optional[TypeIR]:
        if node is None:
            return None
        t1 = self._factor(self._child(node, 0))
        other = self._child_by_name(node, "OtherFactor")
        if other is None:
            return t1
        op, line = self._op_info(self._child(other, 0))
        t2 = self._term(self._child(other, 1))
        if self._check_arith(t1, t2) is None:
            self._error(line, f'运算符 "{op}" 的分量类型不相容')
            return None
        return t1

    def _factor(self, node: Optional[TreeNode]) -> Optional[TypeIR]:
        if node is None or not node.children:
            return None
        c = node.children[0]
        if c.token is not None and c.token.token_type == TokenType.INTC:
            return self._int_type
        if c.token is not None and c.token.token_type == TokenType.LPAREN:
            return self._exp(self._child(node, 1))
        if c.name == "Variable":
            return self._variable(c)
        return None

    def _variable(self, node: Optional[TreeNode]) -> Optional[TypeIR]:
        if node is None:
            return None
        t = self._token(node, 0)
        if t is None:
            return None
        sym = self._symtab.find(t.sem_value, IdentifierKind.VAR_KIND)
        if sym is None:
            self._error(t.line, f'未声明变量标识符 "{t.sem_value}"')
            return None
        vm = self._child_by_name(node, "VariMore")
        if vm is None:
            return sym.id_type
        return self._vari_more(vm, sym, t)

    def _vari_more(self, node: TreeNode, sym: SymbolEntry, id_token: Token) -> Optional[TypeIR]:
        first = self._child(node, 0)
        if first is None:
            return None
        if first.token is not None and first.token.token_type == TokenType.LMIDPAREN:
            if sym.id_type is None or sym.id_type.type_kind != TypeKind.ARRAY_TY:
                self._error(id_token.line, f'变量 "{id_token.sem_value}" 不是数组类型')
                return None
            idx_type = self._exp(self._child(node, 1))
            if idx_type is not self._int_type:
                self._error(id_token.line, f'数组 "{id_token.sem_value}" 的引用不合法')
                return None
            return sym.id_type.elem_type
        if first.token is not None and first.token.token_type == TokenType.DOT:
            if sym.id_type is None or sym.id_type.type_kind != TypeKind.RECORD_TY:
                self._error(id_token.line, f'变量 "{id_token.sem_value}" 不是记录类型')
                return None
            fv = self._child_by_name(node, "FieldVar")
            return self._field_var(fv, sym, id_token)
        return None

    def _field_var(self, node: Optional[TreeNode], sym: SymbolEntry, rec_token: Token) -> Optional[TypeIR]:
        if node is None:
            return None
        t = self._token(node, 0)
        if t is None:
            return None
        body = sym.id_type.body if sym.id_type is not None else None
        found: Optional[FieldChain] = None
        cur = body
        while cur:
            if cur.idname == t.sem_value:
                found = cur
                break
            cur = cur.next_field
        if found is None:
            self._error(t.line, f'记录 "{rec_token.sem_value}" 中不存在域变量 "{t.sem_value}"')
            return None
        fm = self._child_by_name(node, "FieldVarMore")
        if fm is None:
            return found.unit_type
        if found.unit_type.type_kind == TypeKind.ARRAY_TY:
            idx_type = self._exp(self._child(fm, 1))
            if idx_type is not self._int_type:
                self._error(t.line, f'记录 "{rec_token.sem_value}" 中数组域 "{t.sem_value}" 引用不合法')
                return None
            return found.unit_type.elem_type
        self._error(t.line, f'记录 "{rec_token.sem_value}" 中域 "{t.sem_value}" 不是数组类型')
        return None

    # ------------------------------------------------------------------
    # 运算符信息提取
    # ------------------------------------------------------------------
    def _op_info(self, node: Optional[TreeNode]) -> tuple[str, int]:
        if node is not None and node.children and node.children[0].token is not None:
            return node.children[0].token.sem_value, node.children[0].token.line
        return "?", 0

    def _cmp_op_info(self, node: Optional[TreeNode]) -> tuple[str, int]:
        if node is not None and node.children and node.children[0].token is not None:
            return node.children[0].token.sem_value, node.children[0].token.line
        return "?", 0
