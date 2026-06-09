"""SNL 语义分析 — 声明部分遍历（类型声明、变量声明）。负责类型声明、变量声明的语义检查，并构建符号表与类型表。"""

from __future__ import annotations
from typing import List, Optional

from snl_compiler.tokens import Token, TokenType
from snl_compiler.syntax_tree import TreeNode
from snl_compiler.types import TypeKind, TypeIR, FieldChain
from snl_compiler.symbol_table import SymbolTable, SymbolEntry, IdentifierKind, AccessKind
from snl_compiler.semantic_base import SemanticBase


class SemanticCore(SemanticBase):
    """声明部分语义分析核心（类型 + 变量）。"""

    def __init__(self, symtab: SymbolTable, errors: List[str]) -> None:
        super().__init__(symtab, errors)
        self._types: List[TypeIR] = []
        self._init_base_types()

    def _init_base_types(self) -> None:
        self._types.extend([TypeIR(TypeKind.INT_TY, size=2), TypeIR(TypeKind.CHAR_TY, size=1)])

    @property
    def int_type(self) -> TypeIR:
        return self._types[0]

    @property
    def char_type(self) -> TypeIR:
        return self._types[1]

    @property
    def type_list(self) -> List[TypeIR]:
        return self._types

    def analyze_declarations(self, tree: TreeNode) -> None:
        self._symtab.create_scope()
        dp = self._child_by_name(tree, "DeclarePart")
        if dp is not None:
            self._type_dec_part(self._child_by_name(dp, "TypeDecPart"))
            self._var_dec_part(self._child_by_name(dp, "VarDecPart"))

    # ------------------------------------------------------------------
    # 类型声明
    # 
    # 这 10 个方法加起来，只做了一件事：遍历语法树的类型声明部分，
    # 把每个 type X = Y 翻译成 SymbolEntry(X, TypeIR(Y)) 存进符号表。
    # ------------------------------------------------------------------
    def _type_dec_part(self, node: Optional[TreeNode]) -> None:
        if node is None:
            return
        self._type_dec(self._child_by_name(node, "TypeDec"))

    def _type_dec(self, node: Optional[TreeNode]) -> None:
        if node is None:
            return
        self._type_dec_list(self._child_by_name(node, "TypeDecList"))

    def _type_dec_list(self, node: Optional[TreeNode]) -> None:
        if node is None:
            return
        tok = self._token(node, 0)
        tdef = self._child(node, 2)
        attr = self._type_def(tdef)
        if tok is not None and attr is not None:
            entry = SymbolEntry(idname=tok.sem_value, id_type=attr, kind=IdentifierKind.TYPE_KIND)
            if self._symtab.enter(tok.sem_value, entry, IdentifierKind.TYPE_KIND) is None:
                # 同一个作用域里，不能定义两个同名的类型。
                self._error(tok.line, f'标识符 "{tok.sem_value}" 重复定义')
        more = self._child(node, 4)
        if more is not None and more.name == "TypeDecList":
            self._type_dec_list(more)

    def _type_def(self, node: Optional[TreeNode]) -> Optional[TypeIR]:
        if node is None or not node.children:
            return None
        c = node.children[0]
        if c.name == "BaseType":
            return self._base_type(c)
        if c.name == "StructureType":
            return self._structure_type(c)
        if c.token is not None and c.token.token_type == TokenType.ID:
            sym = self._symtab.find(c.token.sem_value, IdentifierKind.TYPE_KIND)
            if sym is None:
                # 检查： 用 type1 x; 声明变量时，type1 必须先定义。
                self._error(c.token.line, f'未声明类型标识符 "{c.token.sem_value}"')
            return sym.id_type if sym else None
        return None

    def _base_type(self, node: Optional[TreeNode]) -> Optional[TypeIR]:
        if node is None or not node.children:
            return None
        t = node.children[0].token
        if t is None:
            return None
        if t.token_type == TokenType.INTEGER:
            return self.int_type
        if t.token_type == TokenType.CHAR:
            return self.char_type
        return None

    def _structure_type(self, node: Optional[TreeNode]) -> Optional[TypeIR]:
        if node is None or not node.children:
            return None
        c = node.children[0]
        if c.name == "ArrayType":
            return self._array_type(c)
        if c.name == "RecType":
            return self._rec_type(c)
        return None

    def _array_type(self, node: Optional[TreeNode]) -> Optional[TypeIR]:
        low_t = self._token(node, 2)
        high_t = self._token(node, 4)
        base_node = self._child(node, 7)
        if low_t is None or high_t is None:
            return None
        try:
            low_v = int(low_t.sem_value)
            high_v = int(high_t.sem_value)
        except ValueError:
            # 检查： 数组上下界必须是合法整数
            self._error(low_t.line, f'数组下标 "{low_t.sem_value}" 非法')
            return None
        if low_v < 0:
            # 检查： SNL 不允许负数下界。
            self._error(low_t.line, f'数组下标 "{low_t.sem_value}" 非法')
            return None
        if high_v < low_v:
            # 检查： 上界必须大于等于下界。
            self._error(low_t.line, f'数组下标越界')
            return None
        elem = self._base_type(base_node)
        if elem is None:
            return None
        ty = TypeIR(type_kind=TypeKind.ARRAY_TY, size=(high_v - low_v + 1) * elem.size,
                    index_type=self.int_type, elem_type=elem, array_low=low_v)
        self._types.append(ty)
        return ty

    def _rec_type(self, node: Optional[TreeNode]) -> Optional[TypeIR]:
        field_node = self._child_by_name(node, "FieldDecList")
        body = self._field_dec_list(field_node)
        if body is None:
            return None
        seen: set[str] = set()
        cur: Optional[FieldChain] = body
        while cur:
            if cur.idname in seen:
                # 检查：同一个记录里不能有两个同名的域。
                self._error(0, f'记录类型中标识符 "{cur.idname}" 重复定义')
            seen.add(cur.idname)
            cur = cur.next_field
        total = 0
        cur = body
        while cur:
            cur.offset = total
            total += cur.unit_type.size
            cur = cur.next_field
        ty = TypeIR(type_kind=TypeKind.RECORD_TY, size=total, body=body)
        self._types.append(ty)
        return ty

    def _field_dec_list(self, node: Optional[TreeNode]) -> Optional[FieldChain]:
        if node is None:
            return None
        type_node = self._child(node, 0)
        if type_node is None:
            return None
        unit = self._base_type(type_node) if type_node.name == "BaseType" else self._array_type(type_node)
        if unit is None:
            return None
        id_list = self._child(node, 1)
        names = self._collect_id_names(id_list)
        head: Optional[FieldChain] = None
        tail: Optional[FieldChain] = None
        for name in names:
            fc = FieldChain(idname=name, unit_type=unit)
            if head is None:
                head = fc
            else:
                tail.next_field = fc  # type: ignore[union-attr]
            tail = fc
        more = self._child(node, 3)
        if more is not None and more.name == "FieldDecList":
            more_head = self._field_dec_list(more)
            if tail is not None:
                tail.next_field = more_head
            else:
                head = more_head
        return head

    def _collect_id_names(self, node: Optional[TreeNode]) -> List[str]:
        names: List[str] = []
        if node is None:
            return names
        t = self._token(node, 0)
        if t is not None:
            names.append(t.sem_value)
        more = self._child_by_name(node, "IDMore")
        if more is not None:
            nxt = self._child_by_name(more, "IDList")
            names.extend(self._collect_id_names(nxt))
        return names

    # ------------------------------------------------------------------
    # 变量声明
    # ------------------------------------------------------------------
    def _var_dec_part(self, node: Optional[TreeNode]) -> None:
        if node is None:
            return
        self._var_dec(self._child_by_name(node, "VarDec"))

    def _var_dec(self, node: Optional[TreeNode]) -> None:
        if node is None:
            return
        self._var_dec_list(self._child_by_name(node, "VarDecList"))

    def _var_dec_list(self, node: Optional[TreeNode]) -> None:
        if node is None:
            return
        tdef = self._child(node, 0)
        var_type = self._type_def(tdef)
        id_list = self._child(node, 1)
        toks = self._collect_var_tokens(id_list)
        if var_type is not None:
            for tok in toks:
                off = self._next_var_offset()
                entry = SymbolEntry(
                    idname=tok.sem_value, id_type=var_type,
                    kind=IdentifierKind.VAR_KIND,
                    access=AccessKind.DIRECT,
                    level=self._symtab.current_level,
                    offset=off,
                )
                if self._symtab.enter(tok.sem_value, entry, IdentifierKind.VAR_KIND) is None:
                    # 检查：变量标识符不能重复定义。
                    self._error(tok.line, f'标识符 "{tok.sem_value}" 重复定义')
        more = self._child(node, 3)
        if more is not None and more.name == "VarDecList":
            self._var_dec_list(more)

    def _collect_var_tokens(self, node: Optional[TreeNode]) -> List[Token]:
        toks: List[Token] = []
        if node is None:
            return toks
        t = self._token(node, 0)
        if t is not None:
            toks.append(t)
        more = self._child_by_name(node, "VarIDMore")
        if more is not None:
            nxt = self._child_by_name(more, "VarIDList")
            toks.extend(self._collect_var_tokens(nxt))
        return toks

    def _next_var_offset(self) -> int:
        last = self._symtab.find_last_var()
        if last is None or last.id_type is None:
            return 0
        return last.offset + last.id_type.size
