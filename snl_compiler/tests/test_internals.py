"""内部方法直接测试 — 提升覆盖率。"""

from snl_compiler.semantic_core import SemanticCore
from snl_compiler.semantic_proc import SemanticProc
from snl_compiler.semantic_expr import SemanticExpr
from snl_compiler.semantic_stmt import SemanticStmt
from snl_compiler.symbol_table import SymbolTable, SymbolEntry
from snl_compiler.syntax_tree import TreeNode
from snl_compiler.tokens import Token, TokenType
from snl_compiler.types import TypeIR, TypeKind


def test_semantic_core_token_with_none() -> None:
    symtab = SymbolTable()
    core = SemanticCore(symtab, [])
    assert core._token(None, 0) is None
    assert core._token(TreeNode("Test"), 5) is None


def test_semantic_core_child_with_none() -> None:
    symtab = SymbolTable()
    core = SemanticCore(symtab, [])
    assert core._child(None, 0) is None


def test_semantic_core_type_dec_none() -> None:
    symtab = SymbolTable()
    core = SemanticCore(symtab, [])
    core._type_dec_part(None)
    core._type_dec(None)
    core._type_dec_list(None)
    # 空 TypeDecList 不应崩溃
    core._type_dec_list(TreeNode("TypeDecList"))


def test_semantic_core_type_def_edge() -> None:
    symtab = SymbolTable()
    core = SemanticCore(symtab, [])
    assert core._type_def(None) is None
    assert core._type_def(TreeNode("TypeDef")) is None
    assert core._base_type(None) is None
    assert core._base_type(TreeNode("BaseType")) is None
    assert core._structure_type(None) is None
    assert core._structure_type(TreeNode("StructureType")) is None


def test_semantic_core_array_type_none() -> None:
    symtab = SymbolTable()
    core = SemanticCore(symtab, [])
    assert core._array_type(None) is None
    # 缺少子节点的 ArrayType
    assert core._array_type(TreeNode("ArrayType")) is None


def test_semantic_core_rec_type_none() -> None:
    symtab = SymbolTable()
    core = SemanticCore(symtab, [])
    assert core._rec_type(None) is None
    assert core._field_dec_list(None) is None
    assert core._field_dec_list(TreeNode("FieldDecList")) is None


def test_semantic_core_var_dec_none() -> None:
    symtab = SymbolTable()
    core = SemanticCore(symtab, [])
    core._var_dec_part(None)
    core._var_dec(None)
    core._var_dec_list(None)
    core._var_dec_list(TreeNode("VarDecList"))


def test_semantic_core_proc_dec_none() -> None:
    symtab = SymbolTable()
    core = SemanticCore(symtab, [])
    proc = SemanticProc(symtab, [], core)
    proc._proc_dec_part(None)
    proc._proc_dec(None)
    # 缺少 ID 的 ProcDec
    proc._proc_dec(TreeNode("ProcDec"))


def test_semantic_core_param_none() -> None:
    symtab = SymbolTable()
    core = SemanticCore(symtab, [])
    proc = SemanticProc(symtab, [], core)
    assert proc._param_list(None) is None
    assert proc._param_dec_list(None) is None
    assert proc._param(None) is None
    assert proc._collect_form_tokens(None) == []


def test_semantic_expr_helpers_none() -> None:
    symtab = SymbolTable()
    int_t = TypeIR(TypeKind.INT_TY, size=2)
    char_t = TypeIR(TypeKind.CHAR_TY, size=1)
    expr = SemanticExpr(symtab, [], int_t, char_t)
    assert expr._token(None, 0) is None
    assert expr._child(None, 0) is None
    assert expr._child_by_name(None, "Foo") is None
    assert expr._child_by_name(TreeNode("Test"), "Foo") is None


def test_semantic_expr_stm_none() -> None:
    symtab = SymbolTable()
    int_t = TypeIR(TypeKind.INT_TY, size=2)
    char_t = TypeIR(TypeKind.CHAR_TY, size=1)
    stmt = SemanticStmt(symtab, [], int_t, char_t)
    stmt._stm(None)
    stmt._stm(TreeNode("Stm"))
    stmt._stm_list(None)
    stmt._input_stm(TreeNode("InputStm"))
    stmt._output_stm(TreeNode("OutputStm"))


def test_semantic_expr_exp_none() -> None:
    symtab = SymbolTable()
    int_t = TypeIR(TypeKind.INT_TY, size=2)
    char_t = TypeIR(TypeKind.CHAR_TY, size=1)
    expr = SemanticExpr(symtab, [], int_t, char_t)
    assert expr._exp(None) is None
    assert expr._term(None) is None
    assert expr._factor(None) is None
    assert expr._factor(TreeNode("Factor")) is None
    assert expr._variable(None) is None
    assert expr._variable(TreeNode("Variable")) is None


def test_semantic_expr_op_info() -> None:
    symtab = SymbolTable()
    int_t = TypeIR(TypeKind.INT_TY, size=2)
    char_t = TypeIR(TypeKind.CHAR_TY, size=1)
    expr = SemanticExpr(symtab, [], int_t, char_t)
    assert expr._op_info(None) == ("?", 0)
    assert expr._cmp_op_info(None) == ("?", 0)
    assert expr._op_info(TreeNode("AddOp")) == ("?", 0)


def test_symbol_table_edge() -> None:
    st = SymbolTable()
    st.create_scope()
    st.create_scope()
    st.destroy_scope()
    st.destroy_scope()
    # 所有 scope 被销毁后再查找
    assert st.find("x") is None
    assert st.find_in_current("x") is None
    assert st.find_last_var() is None
    assert st.find_proc_scope("f") == -1
    assert not st.enter("x", SymbolEntry("x"))


def test_semantic_analyzer_type_str() -> None:
    from snl_compiler.semantic_analyzer import SemanticAnalyzer
    analyzer = SemanticAnalyzer()
    assert analyzer._type_str(TypeIR(TypeKind.ARRAY_TY, elem_type=TypeIR(TypeKind.INT_TY))) == "array of integer"
    assert analyzer._type_str(TypeIR(TypeKind.RECORD_TY)) == "record"
    assert analyzer._type_str(None) == "未知"
    assert analyzer._type_str(TypeIR("unknown")) == "unknown"


def test_semantic_expr_proc_bodies_none() -> None:
    symtab = SymbolTable()
    int_t = TypeIR(TypeKind.INT_TY, size=2)
    char_t = TypeIR(TypeKind.CHAR_TY, size=1)
    stmt = SemanticStmt(symtab, [], int_t, char_t)
    stmt._proc_dec_bodies(None)
    stmt._proc_body(None)
    stmt._proc_body(TreeNode("ProcDec"))


def test_semantic_expr_stm_branches() -> None:
    symtab = SymbolTable()
    int_t = TypeIR(TypeKind.INT_TY, size=2)
    char_t = TypeIR(TypeKind.CHAR_TY, size=1)
    stmt = SemanticStmt(symtab, [], int_t, char_t)
    stmt._stm(None)
    stmt._stm(TreeNode("Stm"))
    # 非法语句起始 — _stm 当前仅忽略不匹配的语句类型
    bad = TreeNode("Stm", children=[TreeNode("PLUS", token=Token(TokenType.PLUS, "+", 1, 1))])
    stmt._stm(bad)  # 不应崩溃


def test_semantic_expr_output_none() -> None:
    symtab = SymbolTable()
    int_t = TypeIR(TypeKind.INT_TY, size=2)
    char_t = TypeIR(TypeKind.CHAR_TY, size=1)
    stmt = SemanticStmt(symtab, [], int_t, char_t)
    stmt._output_stm(TreeNode("OutputStm"))


def test_semantic_expr_assignment_none() -> None:
    symtab = SymbolTable()
    int_t = TypeIR(TypeKind.INT_TY, size=2)
    char_t = TypeIR(TypeKind.CHAR_TY, size=1)
    stmt = SemanticStmt(symtab, [], int_t, char_t)
    stmt._assignment_rest(TreeNode("AssignmentRest"), Token(TokenType.ID, "x", 1, 1))


def test_semantic_expr_call_rest() -> None:
    symtab = SymbolTable()
    int_t = TypeIR(TypeKind.INT_TY, size=2)
    char_t = TypeIR(TypeKind.CHAR_TY, size=1)
    stmt = SemanticStmt(symtab, [], int_t, char_t)
    stmt._call_stm_rest(TreeNode("CallStmRest"), Token(TokenType.ID, "f", 1, 1))


def test_semantic_expr_collect_actuals_none() -> None:
    symtab = SymbolTable()
    int_t = TypeIR(TypeKind.INT_TY, size=2)
    char_t = TypeIR(TypeKind.CHAR_TY, size=1)
    stmt = SemanticStmt(symtab, [], int_t, char_t)
    out = []
    stmt._collect_actuals(None, out)
    assert out == []


def test_semantic_expr_vari_more_branches() -> None:
    symtab = SymbolTable()
    int_t = TypeIR(TypeKind.INT_TY, size=2)
    char_t = TypeIR(TypeKind.CHAR_TY, size=1)
    expr = SemanticExpr(symtab, [], int_t, char_t)
    # VariMore 为 None
    assert expr._vari_more(TreeNode("VariMore"), SymbolEntry("x", id_type=int_t, kind="varKind"), Token(TokenType.ID, "x", 1, 1)) is None


def test_semantic_expr_field_var_none() -> None:
    symtab = SymbolTable()
    int_t = TypeIR(TypeKind.INT_TY, size=2)
    char_t = TypeIR(TypeKind.CHAR_TY, size=1)
    expr = SemanticExpr(symtab, [], int_t, char_t)
    assert expr._field_var(None, SymbolEntry("r", id_type=TypeIR(TypeKind.RECORD_TY), kind="varKind"), Token(TokenType.ID, "r", 1, 1)) is None
    assert expr._field_var(TreeNode("FieldVar"), SymbolEntry("r", id_type=TypeIR(TypeKind.RECORD_TY), kind="varKind"), Token(TokenType.ID, "r", 1, 1)) is None


def test_semantic_core_structure_type_none() -> None:
    symtab = SymbolTable()
    core = SemanticCore(symtab, [])
    assert core._structure_type(None) is None
    assert core._structure_type(TreeNode("StructureType")) is None


def test_semantic_core_field_dec_list_empty() -> None:
    symtab = SymbolTable()
    core = SemanticCore(symtab, [])
    assert core._field_dec_list(TreeNode("FieldDecList")) is None


def test_semantic_core_proc_dec_no_id() -> None:
    symtab = SymbolTable()
    core = SemanticCore(symtab, [])
    proc = SemanticProc(symtab, [], core)
    proc._proc_dec(TreeNode("ProcDec"))


def test_semantic_core_param_edge() -> None:
    symtab = SymbolTable()
    core = SemanticCore(symtab, [])
    proc = SemanticProc(symtab, [], core)
    assert proc._param(None) is None
    assert proc._param(TreeNode("Param")) is None


def test_tokens_repr() -> None:
    t = Token(TokenType.ID, "x", 1, 1)
    assert "Token" in repr(t)


def test_semantic_analyzer_unknown_entry() -> None:
    from snl_compiler.semantic_analyzer import SemanticAnalyzer
    analyzer = SemanticAnalyzer()
    analyzer._symtab.create_scope()
    analyzer._symtab.enter("*Unknown", SymbolEntry("*Unknown", kind="varKind"))
    table = analyzer._format_symbol_table()
    assert "符 号 表" in table


def test_semantic_core_analyze_no_declare_part() -> None:
    symtab = SymbolTable()
    core = SemanticCore(symtab, [])
    tree = TreeNode("Program", children=[TreeNode("ProgramHead")])
    core.analyze_declarations(tree)
    assert symtab.current_level == 1


def test_semantic_expr_output_stm_none() -> None:
    symtab = SymbolTable()
    int_t = TypeIR(TypeKind.INT_TY, size=2)
    char_t = TypeIR(TypeKind.CHAR_TY, size=1)
    stmt = SemanticStmt(symtab, [], int_t, char_t)
    stmt._output_stm(TreeNode("OutputStm"))  # 缺少 Exp 子节点


def test_semantic_expr_assignment_varimore() -> None:
    symtab = SymbolTable()
    int_t = TypeIR(TypeKind.INT_TY, size=2)
    char_t = TypeIR(TypeKind.CHAR_TY, size=1)
    stmt = SemanticStmt(symtab, [], int_t, char_t)
    # 创建 AssignmentRest: VariMore := Exp
    n = TreeNode("AssignmentRest")
    n.add_child(TreeNode("VariMore"))  # 空 VariMore
    n.add_child(TreeNode("ASSIGN", token=Token(TokenType.ASSIGN, ":=", 1, 1)))
    n.add_child(TreeNode("Exp"))
    stmt._assignment_rest(n, Token(TokenType.ID, "x", 1, 1))


def test_symbol_table_enter_no_scope() -> None:
    st = SymbolTable()
    # 没有创建 scope 就 enter
    assert not st.enter("x", SymbolEntry("x"))


def test_parser_type_def_id() -> None:
    from snl_compiler.rd_parser import RecursiveDescentParser
    from snl_compiler.lexer import LexicalAnalyzer
    src = "program p type t = integer; var t x; begin x := 1 end."
    tokens, _ = LexicalAnalyzer(src).analyze()
    tree, errors = RecursiveDescentParser(tokens).parse()
    assert tree is not None
    assert not errors
