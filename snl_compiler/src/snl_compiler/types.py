"""SNL 类型内部表示系统（Type Internal Representation）。"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


class TypeKind:
    """类型种类常量。"""

    INT_TY: str = "intTy"
    CHAR_TY: str = "charTy"
    ARRAY_TY: str = "arrayTy"
    RECORD_TY: str = "recordTy"


@dataclass
class FieldChain:
    """记录类型的域链。"""

    idname: str
    unit_type: TypeIR
    offset: int = 0
    next_field: Optional[FieldChain] = None


@dataclass
class TypeIR:
    """类型内部表示。"""

    type_kind: str
    size: int = 0
    # 数组类型专用
    index_type: Optional[TypeIR] = None
    elem_type: Optional[TypeIR] = None
    array_low: int = 0
    # 记录类型专用
    body: Optional[FieldChain] = None

    def __eq__(self, other: object) -> bool:
        """基于 type_kind 的浅比较；语义分析中通常比较 type_kind。"""
        if not isinstance(other, TypeIR):
            return NotImplemented
        return self.type_kind == other.type_kind

    def __repr__(self) -> str:
        if self.type_kind == TypeKind.ARRAY_TY:
            elem: str = self.elem_type.type_kind if self.elem_type else "?"
            return f"array[{self.array_low}..] of {elem}"
        if self.type_kind == TypeKind.RECORD_TY:
            fields: list[str] = []
            cur: Optional[FieldChain] = self.body
            while cur:
                fields.append(cur.idname)
                cur = cur.next_field
            return f"record({', '.join(fields)})"
        return self.type_kind
