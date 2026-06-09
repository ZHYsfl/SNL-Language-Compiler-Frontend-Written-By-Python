"""SNL 语义分析 — 语句检查。

继承 SemanticExpr 的表达式推导能力，专注于各类语句的语义检查。
"""

from __future__ import annotations
from typing import List, Optional

from snl_compiler.tokens import Token, TokenType
from snl_compiler.syntax_tree import TreeNode
from snl_compiler.types import TypeIR
from snl_compiler.symbol_table import IdentifierKind
from snl_compiler.semantic_expr import SemanticExpr


class SemanticStmt(SemanticExpr):
    """语句语义分析。"""

    # ------------------------------------------------------------------
    # 入口
    # ------------------------------------------------------------------
    def analyze_statements(self, tree: TreeNode) -> None:
        """分析所有过程体与主程序体中的语句列表。"""
        dp = self._child_by_name(tree, "DeclarePart")
        if dp is not None:
            self._proc_dec_bodies(self._child_by_name(dp, "ProcDecpart"))
        pb = self._child_by_name(tree, "ProgramBody")
        if pb is not None:
            self._stm_list(self._child_by_name(pb, "StmList"))
            self._symtab.destroy_scope()

    def _proc_dec_bodies(self, node: Optional[TreeNode]) -> None:
        if node is None:
            return
        self._proc_body(self._child_by_name(node, "ProcDec"))

    def _proc_body(self, node: Optional[TreeNode]) -> None:
        if node is None:
            return
        proc_body = self._child_by_name(node, "ProcBody")
        if proc_body is not None:
            pb = self._child_by_name(proc_body, "ProgramBody")
            if pb is not None:
                self._stm_list(self._child_by_name(pb, "StmList"))
                self._symtab.destroy_scope()
        more = self._child(node, 8)
        if more is not None and more.name == "ProcDec":
            self._proc_body(more)

    def _stm_list(self, node: Optional[TreeNode]) -> None:
        if node is None:
            return
        self._stm(self._child(node, 0))
        more = self._child(node, 1)
        if more is not None and more.name == "StmMore":
            self._stm_list(self._child_by_name(more, "StmList"))

    def _stm(self, node: Optional[TreeNode]) -> None:
        if node is None or not node.children:
            return
        c = node.children[0]
        if c.name == "InputStm":
            self._input_stm(c)
        elif c.name == "OutputStm":
            self._output_stm(c)
        elif c.name == "ReturnStm":
            pass
        elif c.name == "ConditionalStm":
            self._conditional_stm(c)
        elif c.name == "LoopStm":
            self._loop_stm(c)
        elif c.token is not None and c.token.token_type == TokenType.ID:
            ass_call = self._child(node, 1)
            self._ass_call(ass_call, c.token)

    def _input_stm(self, node: TreeNode) -> None:
        t = self._token(node, 2)
        if t is None:
            return
        sym = self._symtab.find(t.sem_value, IdentifierKind.VAR_KIND)
        if sym is None:
            self._error(t.line, f'未声明变量标识符 "{t.sem_value}"')

    def _output_stm(self, node: TreeNode) -> None:
        exp = self._child_by_name(node, "Exp")
        self._exp(exp)

    def _conditional_stm(self, node: TreeNode) -> None:
        rel = self._child(node, 1)
        t1 = self._exp(self._child(rel, 0))
        other_rel = self._child_by_name(rel, "OtherRelE")
        t2 = self._exp(self._child(other_rel, 1))
        op, line = self._cmp_op_info(self._child(other_rel, 0))
        self._check_cmp(t1, t2, op, line)
        self._stm_list(self._child_by_name(self._child(node, 3), "StmList"))
        self._stm_list(self._child_by_name(self._child(node, 5), "StmList"))

    def _loop_stm(self, node: TreeNode) -> None:
        rel = self._child(node, 1)
        t1 = self._exp(self._child(rel, 0))
        other_rel = self._child_by_name(rel, "OtherRelE")
        t2 = self._exp(self._child(other_rel, 1))
        op, line = self._cmp_op_info(self._child(other_rel, 0))
        self._check_cmp(t1, t2, op, line)
        self._stm_list(self._child_by_name(self._child(node, 3), "StmList"))

    def _ass_call(self, node: Optional[TreeNode], id_token: Token) -> None:
        if node is None:
            return
        if node.name == "CallStmRest":
            self._call_stm_rest(node, id_token)
        elif node.name == "AssignmentRest":
            self._assignment_rest(node, id_token)

    def _assignment_rest(self, node: TreeNode, id_token: Token) -> None:
        var_sym = self._symtab.find(id_token.sem_value, IdentifierKind.VAR_KIND)
        if var_sym is None:
            any_sym = self._symtab.find(id_token.sem_value)
            if any_sym is None:
                # 检查：标识符必须先声明再使用。
                self._error(id_token.line, f'未声明标识符 "{id_token.sem_value}"')
            else:
                # 标识符必须是变量标识符
                self._error(id_token.line, f'标识符 "{id_token.sem_value}" 不是变量标识符')
            return
        t1: Optional[TypeIR] = None
        t2: Optional[TypeIR] = None
        first = self._child(node, 0)
        if first is not None and first.name == "VariMore":
            t1 = self._vari_more(first, var_sym, id_token)
            t2 = self._exp(self._child(node, 2))
        else:
            t1 = var_sym.id_type
            t2 = self._exp(self._child(node, 1))
        if self._check_arith(t1, t2) is None:
            # 
            self._error(id_token.line, f'标识符 "{id_token.sem_value}" 与赋值内容类型不相容')

    def _call_stm_rest(self, node: TreeNode, id_token: Token) -> None:
        proc_pos = self._symtab.find_proc_scope(id_token.sem_value)
        if proc_pos < 0:
            any_sym = self._symtab.find(id_token.sem_value)
            if any_sym is None:
                self._error(id_token.line, f'未声明标识符 "{id_token.sem_value}"')
            else:
                self._error(id_token.line, f'标识符 "{id_token.sem_value}" 不是过程标识符')
            return
        actuals: List[Optional[TypeIR]] = []
        act_list = self._child_by_name(node, "ActParamList")
        self._collect_actuals(act_list, actuals)
        proc_entry = self._symtab._scope_stack[proc_pos][0]
        formal_count = 0
        p = proc_entry.param_table
        while p:
            formal_count += 1
            p = p.next_param
        if formal_count != len(actuals):
            self._error(id_token.line, f'过程调用 "{id_token.sem_value}" 形实参个数不相同')
            return
        p = proc_entry.param_table
        for i, atype in enumerate(actuals):
            if p is None:
                break
            if p.symbol_index < len(self._symtab._scope_stack[proc_pos]):
                formal_type = self._symtab._scope_stack[proc_pos][p.symbol_index].id_type
                if formal_type is None or atype is None or formal_type != atype:
                    self._error(id_token.line, f'过程调用 "{id_token.sem_value}" 中第 {i + 1} 个参数类型不匹配')
            p = p.next_param

    def _collect_actuals(self, node: Optional[TreeNode], out: List[Optional[TypeIR]]) -> None:
        if node is None:
            return
        t = self._exp(self._child(node, 0))
        out.append(t)
        more = self._child(node, 1)
        if more is not None and more.name == "ActParamMore":
            nxt = self._child_by_name(more, "ActParamList")
            self._collect_actuals(nxt, out)
