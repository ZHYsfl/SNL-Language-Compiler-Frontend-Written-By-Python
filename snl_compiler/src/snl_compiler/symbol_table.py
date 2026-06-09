"""SNL 符号表与作用域管理。

采用栈式作用域结构，支持过程嵌套定义。
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from snl_compiler.types import TypeIR


class IdentifierKind:
    """标识符种类常量。"""

    TYPE_KIND: str = "typeKind"
    VAR_KIND: str = "varKind"
    PROC_KIND: str = "procKind"


class AccessKind:
    """变量访问方式常量。"""

    DIRECT: str = "dir"
    INDIRECT: str = "indir"


@dataclass
class ParamEntry:
    """过程参数表项（链式结构）。"""

    symbol_index: int = 0
    next_param: Optional[ParamEntry] = None


@dataclass
class SymbolEntry:
    """符号表条目。"""

    idname: str
    id_type: Optional[TypeIR] = None
    kind: str = ""
    # 变量属性
    access: str = AccessKind.DIRECT
    level: int = 0
    offset: int = 0
    # 过程属性
    param_table: Optional[ParamEntry] = None
    proc_size: int = 0


class SymbolTable:
    """符号表：栈式作用域管理。"""

    def __init__(self) -> None:
        self._scope_stack: List[List[SymbolEntry]] = []
        self._scope_active: List[bool] = []
        self._valid_count: int = 0

    # ------------------------------------------------------------------
    # 作用域操作
    # ------------------------------------------------------------------
    def create_scope(self) -> None:
        """创建新作用域。"""
        self._scope_stack.append([])
        self._scope_active.append(True)
        self._valid_count += 1

    def destroy_scope(self) -> None:
        """销毁最近的有效作用域。"""
        for i in range(len(self._scope_active) - 1, -1, -1):
            if self._scope_active[i]:
                self._scope_active[i] = False
                self._valid_count -= 1
                return

    @property
    def current_level(self) -> int:
        return self._valid_count

    # ------------------------------------------------------------------
    # 查找
    # ------------------------------------------------------------------
    def find(self, idname: str, kind: str = "") -> Optional[SymbolEntry]:
        """从内到外查找标识符。"""
        for i in range(len(self._scope_stack) - 1, -1, -1):
            if not self._scope_active[i]:
                continue
            for entry in self._scope_stack[i]:
                if entry.idname == idname and (not kind or entry.kind == kind):
                    return entry
        return None

    def find_in_current(self, idname: str, kind: str = "") -> Optional[SymbolEntry]:
        """仅在当前作用域查找。"""
        for i in range(len(self._scope_stack) - 1, -1, -1):
            if self._scope_active[i]:
                for entry in self._scope_stack[i]:
                    if entry.idname == idname and (not kind or entry.kind == kind):
                        return entry
                return None
        return None

    def find_proc_scope(self, idname: str) -> int:
        """查找过程标识符所在作用域索引；未找到返回 -1。"""
        for i in range(len(self._scope_stack) - 1, -1, -1):
            if self._scope_stack[i]:
                first = self._scope_stack[i][0]
                if first.idname == idname and first.kind == IdentifierKind.PROC_KIND:
                    return i
        return -1

    def find_last_var(self) -> Optional[SymbolEntry]:
        """当前作用域中最后一个变量条目。"""
        for i in range(len(self._scope_stack) - 1, -1, -1):
            if not self._scope_active[i]:
                continue
            for j in range(len(self._scope_stack[i]) - 1, -1, -1):
                if self._scope_stack[i][j].kind == IdentifierKind.VAR_KIND:
                    return self._scope_stack[i][j]
            return None
        return None

    # ------------------------------------------------------------------
    # 登记
    # ------------------------------------------------------------------
    def enter(self, idname: str, entry: SymbolEntry, kind: str = "") -> Optional[int]:
        """将标识符登记到当前作用域；返回插入后的索引，重复定义返回 None。"""
        for i in range(len(self._scope_stack) - 1, -1, -1):
            if not self._scope_active[i]:
                continue
            check_kind: str = kind if kind else entry.kind
            for existing in self._scope_stack[i]:
                if existing.idname != idname:
                    continue
                if check_kind == IdentifierKind.PROC_KIND:
                    if existing.kind == IdentifierKind.PROC_KIND:
                        return None
                else:
                    if existing.kind == entry.kind:
                        return None
            entry.idname = idname
            idx = len(self._scope_stack[i])
            self._scope_stack[i].append(entry)
            return idx
        return None

    # ------------------------------------------------------------------
    # 遍历输出
    # ------------------------------------------------------------------
    def entries(self) -> List[Tuple[int, SymbolEntry]]:
        """返回所有 (level, entry) 列表。"""
        result: List[Tuple[int, SymbolEntry]] = []
        for level, table in enumerate(self._scope_stack):
            for entry in table:
                result.append((level, entry))
        return result
