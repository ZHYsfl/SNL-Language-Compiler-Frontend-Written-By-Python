"""SNL 语义分析器主入口。

整合声明遍历（SemanticCore）与表达式/语句检查（SemanticExpr），
输出符号表、类型表与语义错误报告。
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

from snl_compiler.syntax_tree import TreeNode
from snl_compiler.symbol_table import SymbolTable, SymbolEntry, IdentifierKind, AccessKind
from snl_compiler.types import TypeKind, TypeIR
from snl_compiler.semantic_core import SemanticCore
from snl_compiler.semantic_proc import SemanticProc
from snl_compiler.semantic_stmt import SemanticStmt


@dataclass
class SemanticResult:
    """语义分析结果。"""

    type_table: str
    symbol_table: str
    errors: List[str]


class SemanticAnalyzer:
    """语义分析器。"""

    def __init__(self) -> None:
        self._symtab: SymbolTable = SymbolTable()
        self._errors: List[str] = []
        self._core: SemanticCore = SemanticCore(self._symtab, self._errors)

    def analyze(self, tree: Optional[TreeNode]) -> SemanticResult:
        """对语法树进行完整语义分析。"""
        if tree is None:
            return SemanticResult("", "", ["语法树为空"])
        self._core.analyze_declarations(tree)
        proc = SemanticProc(self._symtab, self._errors, self._core)
        proc.analyze_procedures(tree)
        stmt = SemanticStmt(self._symtab, self._errors, self._core.int_type, self._core.char_type)
        stmt.analyze_statements(tree)
        self._symtab.destroy_scope()
        return SemanticResult(
            type_table=self._format_type_table(),
            symbol_table=self._format_symbol_table(),
            errors=list(self._errors),
        )

    # ------------------------------------------------------------------
    # 格式化输出
    # ------------------------------------------------------------------
    def _format_type_table(self) -> str:
        lines: List[str] = [
            "=" * 70,
            "                        类 型 表",
            "=" * 70,
            f"{'序号':<6}{'类型种类':<14}{'大小':<8}{'详细信息'}",
            "-" * 70,
        ]
        for i, t in enumerate(self._core.type_list):
            detail = ""
            if t.type_kind == TypeKind.ARRAY_TY:
                elem = t.elem_type.type_kind if t.elem_type else "?"
                detail = f"low={t.array_low}, elemType={elem}"
            elif t.type_kind == TypeKind.RECORD_TY:
                fields: List[str] = []
                cur = t.body
                while cur:
                    fields.append(f"{cur.idname}:{cur.unit_type.type_kind}")
                    cur = cur.next_field
                detail = ", ".join(fields)
            lines.append(f"{i:<6}{t.type_kind:<14}{t.size:<8}{detail}")
        lines.append("-" * 70)
        return "\n".join(lines)

    def _format_symbol_table(self) -> str:
        lines: List[str] = [
            "=" * 90,
            "                           符 号 表",
            "=" * 90,
            f"{'层级':<6}{'标识符':<12}{'种类':<12}{'类型':<18}{'访问':<8}{'偏移':<8}{'大小':<8}",
            "-" * 90,
        ]
        kind_map = {
            IdentifierKind.TYPE_KIND: "类型",
            IdentifierKind.VAR_KIND: "变量",
            IdentifierKind.PROC_KIND: "过程",
        }
        for level, entry in self._symtab.entries():
            if entry.idname == "*Unknown":
                continue
            kind_str = kind_map.get(entry.kind, entry.kind)
            type_str = self._type_str(entry.id_type)
            access_str = ""
            offset_str = ""
            size_str = ""
            if entry.kind == IdentifierKind.PROC_KIND:
                type_str = "-"
            if entry.kind == IdentifierKind.VAR_KIND:
                access_str = "变参" if entry.access == AccessKind.INDIRECT else "直接"
                offset_str = str(entry.offset)
                size_str = str(entry.id_type.size) if entry.id_type else "0"
            elif entry.kind == IdentifierKind.PROC_KIND:
                param_count = 0
                p = entry.param_table
                while p:
                    param_count += 1
                    p = p.next_param
                access_str = f"参数数:{param_count}"
                size_str = str(entry.proc_size)
            lines.append(
                f"{level:<6}{entry.idname:<12}{kind_str:<12}{type_str:<18}"
                f"{access_str:<8}{offset_str:<8}{size_str:<8}"
            )
        lines.append("-" * 90)
        return "\n".join(lines)

    def _type_str(self, t: Optional[TypeIR]) -> str:
        if t is None:
            return "未知"
        if t.type_kind == TypeKind.INT_TY:
            return "integer"
        if t.type_kind == TypeKind.CHAR_TY:
            return "char"
        if t.type_kind == TypeKind.ARRAY_TY:
            return f"array of {self._type_str(t.elem_type)}"
        if t.type_kind == TypeKind.RECORD_TY:
            return "record"
        return t.type_kind
