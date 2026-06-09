"""符号表单元测试。"""

from snl_compiler.symbol_table import SymbolTable, SymbolEntry, IdentifierKind, AccessKind
from snl_compiler.types import TypeIR, TypeKind


def test_empty_find() -> None:
    st = SymbolTable()
    assert st.find("x") is None
    assert st.find_in_current("x") is None
    assert st.find_last_var() is None
    assert st.find_proc_scope("f") == -1


def test_scope_lifecycle() -> None:
    st = SymbolTable()
    st.create_scope()
    assert st.current_level == 1
    st.destroy_scope()
    assert st.current_level == 0


def test_enter_and_find() -> None:
    st = SymbolTable()
    st.create_scope()
    e = SymbolEntry("x", id_type=TypeIR(TypeKind.INT_TY, size=2), kind=IdentifierKind.VAR_KIND)
    assert st.enter("x", e) is not None
    assert st.find("x") is not None
    assert st.find_in_current("x") is not None


def test_enter_duplicate() -> None:
    st = SymbolTable()
    st.create_scope()
    e1 = SymbolEntry("x", kind=IdentifierKind.VAR_KIND)
    e2 = SymbolEntry("x", kind=IdentifierKind.VAR_KIND)
    assert st.enter("x", e1) is not None
    assert st.enter("x", e2) is None


def test_find_last_var() -> None:
    st = SymbolTable()
    st.create_scope()
    e1 = SymbolEntry("x", id_type=TypeIR(TypeKind.INT_TY, size=2), kind=IdentifierKind.VAR_KIND, offset=0)
    e2 = SymbolEntry("y", id_type=TypeIR(TypeKind.CHAR_TY, size=1), kind=IdentifierKind.VAR_KIND, offset=2)
    st.enter("x", e1)
    st.enter("y", e2)
    last = st.find_last_var()
    assert last is not None
    assert last.idname == "y"


def test_proc_scope() -> None:
    st = SymbolTable()
    st.create_scope()
    e = SymbolEntry("f", kind=IdentifierKind.PROC_KIND)
    st.enter("f", e)
    assert st.find_proc_scope("f") == 0
    assert st.find_proc_scope("g") == -1


def test_entries() -> None:
    st = SymbolTable()
    st.create_scope()
    st.enter("x", SymbolEntry("x", kind=IdentifierKind.VAR_KIND))
    assert len(st.entries()) == 1


def test_nested_scope_find() -> None:
    st = SymbolTable()
    st.create_scope()
    st.enter("x", SymbolEntry("x", kind=IdentifierKind.VAR_KIND))
    st.create_scope()
    assert st.find("x") is not None  # 内层作用域应能查找到外层
    st.destroy_scope()
    assert st.find("x") is not None
