"""递归下降语法分析器 — 声明部分（类型、变量、过程、参数、记录域）。"""

from __future__ import annotations
from typing import Optional

from snl_compiler.tokens import Token, TokenType
from snl_compiler.syntax_tree import TreeNode
class DeclarationsMixin:
    """声明部分 Mixin。"""

    # ------------------------------------------------------------------
    # 类型声明
    # ------------------------------------------------------------------
    def _type_dec_part(self) -> Optional[TreeNode]:
        if not self._check(TokenType.TYPE):
            return None
        n = TreeNode("TypeDecPart")
        n.add_child(self._type_dec())
        return n

    def _type_dec(self) -> TreeNode:
        n = TreeNode("TypeDec")
        n.add_child(self._match(TokenType.TYPE))
        n.add_child(self._type_dec_list())
        return n

    def _type_dec_list(self) -> TreeNode:
        n = TreeNode("TypeDecList")
        n.add_child(self._match(TokenType.ID))
        n.add_child(self._match(TokenType.EQ))
        n.add_child(self._type_def())
        n.add_child(self._match(TokenType.SEMI))
        n.add_child(self._type_dec_more())
        return n

    def _type_dec_more(self) -> Optional[TreeNode]:
        return self._type_dec_list() if self._check(TokenType.ID) else None

    def _type_def(self) -> TreeNode:
        n = TreeNode("TypeDef")
        if self._check(TokenType.INTEGER, TokenType.CHAR):
            n.add_child(self._base_type())
        elif self._check(TokenType.ARRAY, TokenType.RECORD):
            n.add_child(self._structure_type())
        elif self._check(TokenType.ID):
            n.add_child(self._match(TokenType.ID))
        else:
            t: Token = self._current()
            self._errors.append(f"Line {t.line}, col {t.col}: 非法类型定义")
        return n

    def _base_type(self) -> TreeNode:
        n = TreeNode("BaseType")
        if self._check(TokenType.INTEGER):
            n.add_child(self._match(TokenType.INTEGER))
        elif self._check(TokenType.CHAR):
            n.add_child(self._match(TokenType.CHAR))
        return n

    def _structure_type(self) -> TreeNode:
        n = TreeNode("StructureType")
        if self._check(TokenType.ARRAY):
            n.add_child(self._array_type())
        elif self._check(TokenType.RECORD):
            n.add_child(self._rec_type())
        return n

    def _array_type(self) -> TreeNode:
        n = TreeNode("ArrayType")
        n.add_child(self._match(TokenType.ARRAY))
        n.add_child(self._match(TokenType.LMIDPAREN))
        n.add_child(self._match(TokenType.INTC))
        n.add_child(self._match(TokenType.UNDERANGE))
        n.add_child(self._match(TokenType.INTC))
        n.add_child(self._match(TokenType.RMIDPAREN))
        n.add_child(self._match(TokenType.OF))
        n.add_child(self._base_type())
        return n

    def _rec_type(self) -> TreeNode:
        n = TreeNode("RecType")
        n.add_child(self._match(TokenType.RECORD))
        n.add_child(self._field_dec_list())
        n.add_child(self._match(TokenType.END))
        return n

    def _field_dec_list(self) -> TreeNode:
        n = TreeNode("FieldDecList")
        if self._check(TokenType.INTEGER, TokenType.CHAR):
            n.add_child(self._base_type())
        elif self._check(TokenType.ARRAY):
            n.add_child(self._array_type())
        else:
            t: Token = self._current()
            self._errors.append(f"Line {t.line}, col {t.col}: 记录域声明类型错误")
        n.add_child(self._id_list())
        n.add_child(self._match(TokenType.SEMI))
        n.add_child(self._field_dec_more())
        return n

    def _field_dec_more(self) -> Optional[TreeNode]:
        return self._field_dec_list() if self._check(TokenType.INTEGER, TokenType.CHAR, TokenType.ARRAY) else None

    def _id_list(self) -> TreeNode:
        n = TreeNode("IDList")
        n.add_child(self._match(TokenType.ID))
        n.add_child(self._id_more())
        return n

    def _id_more(self) -> Optional[TreeNode]:
        if not self._check(TokenType.COMMA):
            return None
        n = TreeNode("IDMore")
        n.add_child(self._match(TokenType.COMMA))
        n.add_child(self._id_list())
        return n

    # ------------------------------------------------------------------
    # 变量声明
    # ------------------------------------------------------------------
    def _var_dec_part(self) -> Optional[TreeNode]:
        if not self._check(TokenType.VAR):
            return None
        n = TreeNode("VarDecPart")
        n.add_child(self._var_dec())
        return n

    def _var_dec(self) -> TreeNode:
        n = TreeNode("VarDec")
        n.add_child(self._match(TokenType.VAR))
        n.add_child(self._var_dec_list())
        return n

    def _var_dec_list(self) -> TreeNode:
        n = TreeNode("VarDecList")
        n.add_child(self._type_def())
        n.add_child(self._var_id_list())
        n.add_child(self._match(TokenType.SEMI))
        n.add_child(self._var_dec_more())
        return n

    def _var_dec_more(self) -> Optional[TreeNode]:
        if not self._check(TokenType.INTEGER, TokenType.CHAR, TokenType.ARRAY, TokenType.RECORD, TokenType.ID):
            return None
        if self._check(TokenType.ID):
            p: Optional[Token] = self._peek(1)
            if p is None or p.token_type != TokenType.ID:
                return None
        return self._var_dec_list()

    def _var_id_list(self) -> TreeNode:
        n = TreeNode("VarIDList")
        n.add_child(self._match(TokenType.ID))
        n.add_child(self._var_id_more())
        return n

    def _var_id_more(self) -> Optional[TreeNode]:
        if not self._check(TokenType.COMMA):
            return None
        n = TreeNode("VarIDMore")
        n.add_child(self._match(TokenType.COMMA))
        n.add_child(self._var_id_list())
        return n

    # ------------------------------------------------------------------
    # 过程声明
    # ------------------------------------------------------------------
    def _proc_dec_part(self) -> Optional[TreeNode]:
        if not self._check(TokenType.PROCEDURE):
            return None
        n = TreeNode("ProcDecpart")
        n.add_child(self._proc_dec())
        return n

    def _proc_dec(self) -> TreeNode:
        n = TreeNode("ProcDec")
        n.add_child(self._match(TokenType.PROCEDURE))
        n.add_child(self._match(TokenType.ID))
        n.add_child(self._match(TokenType.LPAREN))
        n.add_child(self._param_list())
        n.add_child(self._match(TokenType.RPAREN))
        n.add_child(self._match(TokenType.SEMI))
        n.add_child(self._declare_part())
        n.add_child(self._proc_body())
        n.add_child(self._proc_dec_more())
        return n

    def _proc_body(self) -> TreeNode:
        n = TreeNode("ProcBody")
        n.add_child(self._program_body())
        return n

    def _proc_dec_more(self) -> Optional[TreeNode]:
        if not self._check(TokenType.SEMI):
            return None
        self._pos += 1
        if self._check(TokenType.PROCEDURE):
            return self._proc_dec()
        return None

    def _param_list(self) -> Optional[TreeNode]:
        return None if self._check(TokenType.RPAREN) else TreeNode("ParamList", children=[self._param_dec_list()])

    def _param_dec_list(self) -> TreeNode:
        n = TreeNode("ParamDecList")
        n.add_child(self._param())
        n.add_child(self._param_more())
        return n

    def _param_more(self) -> Optional[TreeNode]:
        if not self._check(TokenType.SEMI):
            return None
        n = TreeNode("ParamMore")
        n.add_child(self._match(TokenType.SEMI))
        n.add_child(self._param_dec_list())
        return n

    def _param(self) -> TreeNode:
        n = TreeNode("Param")
        if self._check(TokenType.VAR):
            n.add_child(self._match(TokenType.VAR))
        n.add_child(self._type_def())
        n.add_child(self._form_list())
        return n

    def _form_list(self) -> TreeNode:
        n = TreeNode("FormList")
        n.add_child(self._match(TokenType.ID))
        n.add_child(self._fid_more())
        return n

    def _fid_more(self) -> Optional[TreeNode]:
        if not self._check(TokenType.COMMA):
            return None
        n = TreeNode("FidMore")
        n.add_child(self._match(TokenType.COMMA))
        n.add_child(self._form_list())
        return n
