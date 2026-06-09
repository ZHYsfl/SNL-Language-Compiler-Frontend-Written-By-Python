"""SNL 语义分析 — 过程声明与参数声明遍历。

通过组合复用 SemanticCore 的类型解析能力，保持单一职责。
"""

from __future__ import annotations
from typing import List, Optional

from snl_compiler.tokens import Token, TokenType
from snl_compiler.syntax_tree import TreeNode
from snl_compiler.symbol_table import SymbolTable, SymbolEntry, IdentifierKind, AccessKind, ParamEntry
from snl_compiler.semantic_base import SemanticBase
from snl_compiler.semantic_core import SemanticCore


class SemanticProc(SemanticBase):
    """过程声明语义分析。"""

    def __init__(self, symtab: SymbolTable, errors: List[str], core: SemanticCore) -> None:
        super().__init__(symtab, errors)
        self._core: SemanticCore = core

    def analyze_procedures(self, tree: TreeNode) -> None:
        """分析 Program 下的过程声明部分。"""
        dp = self._child_by_name(tree, "DeclarePart")
        if dp is not None:
            self._proc_dec_part(self._child_by_name(dp, "ProcDecpart"))

    # ------------------------------------------------------------------
    # 过程声明
    # ------------------------------------------------------------------
    def _proc_dec_part(self, node: Optional[TreeNode]) -> None:
        if node is None:
            return
        self._symtab.create_scope()
        self._proc_dec(self._child_by_name(node, "ProcDec"))

    def _proc_dec(self, node: Optional[TreeNode]) -> None:
        if node is None:
            return
        tok: Optional[Token] = None
        for c in node.children:
            if c.token is not None and c.token.token_type == TokenType.ID:
                tok = c.token
                break
        if tok is None:
            return
        entry = SymbolEntry(
            idname=tok.sem_value, kind=IdentifierKind.PROC_KIND,
            level=self._symtab.current_level - 1,
        )
        ok = self._symtab.enter(tok.sem_value, entry, IdentifierKind.PROC_KIND)
        if ok is None:
            # 检查： 过程标识符不能重复定义。
            self._error(tok.line, f'标识符 "{tok.sem_value}" 重复定义')
        param_node = self._child_by_name(node, "ParamList")
        phead = self._param_list(param_node)
        scope_idx = self._symtab.find_proc_scope(tok.sem_value)
        if scope_idx >= 0 and self._symtab._scope_stack[scope_idx]:
            self._symtab._scope_stack[scope_idx][0].param_table = phead
        dec_part = self._child_by_name(node, "DeclarePart")
        if dec_part is not None:
            self._core._type_dec_part(self._child_by_name(dec_part, "TypeDecPart"))
            self._core._var_dec_part(self._child_by_name(dec_part, "VarDecPart"))
            self._proc_dec_part(self._child_by_name(dec_part, "ProcDecpart"))
        if scope_idx >= 0:
            total = 0
            for e in self._symtab._scope_stack[scope_idx][1:]:
                if e.kind == IdentifierKind.VAR_KIND and e.id_type is not None:
                    total += e.id_type.size
            self._symtab._scope_stack[scope_idx][0].proc_size = total
        for c in node.children:
            if c.name == "ProcDec":
                self._proc_dec(c)
                break

    def _param_list(self, node: Optional[TreeNode]) -> Optional[ParamEntry]:
        if node is None:
            return None
        return self._param_dec_list(self._child_by_name(node, "ParamDecList"))

    def _param_dec_list(self, node: Optional[TreeNode]) -> Optional[ParamEntry]:
        if node is None:
            return None
        phead = self._param(self._child(node, 0))
        more = self._child(node, 1)
        if more is not None and more.name == "ParamMore":
            mhead = self._param_dec_list(self._child_by_name(more, "ParamDecList"))
            if phead is not None:
                tail = phead
                while tail.next_param:
                    tail = tail.next_param
                tail.next_param = mhead
            else:
                phead = mhead
        return phead

    def _param(self, node: Optional[TreeNode]) -> Optional[ParamEntry]:
        if node is None or not node.children:
            return None
        is_var = False
        type_idx = 0
        form_idx = 1
        if node.children[0].token is not None and node.children[0].token.token_type == TokenType.VAR:
            is_var = True
            type_idx = 1
            form_idx = 2
        tdef = self._child(node, type_idx)
        ptype = self._core._type_def(tdef)
        form = self._child(node, form_idx)
        toks = self._collect_form_tokens(form)
        phead: Optional[ParamEntry] = None
        ptail: Optional[ParamEntry] = None
        base_off = self._core._next_var_offset()
        for i, tok in enumerate(toks):
            vs = self._core.int_type.size if is_var else (ptype.size if ptype else 0)
            entry = SymbolEntry(
                idname=tok.sem_value, id_type=ptype,
                kind=IdentifierKind.VAR_KIND,
                access=AccessKind.INDIRECT if is_var else AccessKind.DIRECT,
                level=self._symtab.current_level,
                offset=base_off + i * vs,
            )
            param_idx = self._symtab.enter(tok.sem_value, entry, IdentifierKind.VAR_KIND)
            if param_idx is None:
                # 检查：变量标识符不能重复定义。
                self._error(tok.line, f'标识符 "{tok.sem_value}" 重复定义')
            pe = ParamEntry(symbol_index=param_idx if param_idx is not None else 0)
            if phead is None:
                phead = pe
            else:
                ptail.next_param = pe  # type: ignore[union-attr]
            ptail = pe
        return phead

    def _collect_form_tokens(self, node: Optional[TreeNode]) -> List[Token]:
        toks: List[Token] = []
        if node is None:
            return toks
        t = self._token(node, 0)
        if t is not None:
            toks.append(t)
        more = self._child_by_name(node, "FidMore")
        if more is not None:
            nxt = self._child_by_name(more, "FormList")
            toks.extend(self._collect_form_tokens(nxt))
        return toks
