"""类型系统单元测试。"""

from snl_compiler.types import TypeKind, TypeIR, FieldChain


def test_int_ty_str() -> None:
    t = TypeIR(TypeKind.INT_TY, size=2)
    assert repr(t) == "intTy"
    assert t == TypeIR(TypeKind.INT_TY)


def test_array_ty_str() -> None:
    elem = TypeIR(TypeKind.INT_TY, size=2)
    arr = TypeIR(TypeKind.ARRAY_TY, size=20, elem_type=elem, array_low=1)
    assert "array[1..] of intTy" in repr(arr)


def test_record_ty_str() -> None:
    f1 = FieldChain("x", TypeIR(TypeKind.INT_TY, size=2))
    rec = TypeIR(TypeKind.RECORD_TY, size=2, body=f1)
    assert "record(x)" in repr(rec)


def test_eq_with_non_typeir() -> None:
    t = TypeIR(TypeKind.INT_TY)
    assert t != "intTy"


def test_field_chain_next() -> None:
    f1 = FieldChain("x", TypeIR(TypeKind.INT_TY, size=2))
    f2 = FieldChain("y", TypeIR(TypeKind.CHAR_TY, size=1))
    f1.next_field = f2
    assert f1.next_field == f2
