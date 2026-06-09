"""递归下降语法分析器单元测试 — 目标覆盖率 >95%。"""

from __future__ import annotations
import pytest

from snl_compiler.tokens import TokenType
from snl_compiler.lexer import LexicalAnalyzer
from snl_compiler.rd_parser import RecursiveDescentParser


def _parse(src: str) -> tuple:
    tokens, lex_err = LexicalAnalyzer(src).analyze()
    assert not lex_err, f"词法错误: {lex_err}"
    return RecursiveDescentParser(tokens).parse()


# ---------------------------------------------------------------------------
# 正向测试：完整程序
# ---------------------------------------------------------------------------
class TestValidPrograms:
    def test_minimal_program(self) -> None:
        src = "program p begin read(x) end."
        tree, errors = _parse(src)
        assert tree is not None
        assert tree.name == "Program"
        assert not errors

    def test_program_with_type_var(self) -> None:
        src = (
            "program p\n"
            "type t = integer;\n"
            "var integer x;\n"
            "begin\n"
            "    x := 1\n"
            "end."
        )
        tree, errors = _parse(src)
        assert tree is not None
        assert not errors

    def test_program_with_procedure(self) -> None:
        src = (
            "program p\n"
            "var integer x;\n"
            "procedure f();\n"
            "begin\n"
            "    x := 1\n"
            "end;\n"
            "begin\n"
            "    f()\n"
            "end."
        )
        tree, errors = _parse(src)
        assert tree is not None
        assert not errors

    def test_array_type(self) -> None:
        src = (
            "program p\n"
            "type a = array [1 .. 10] of integer;\n"
            "begin\n"
            "    read(x)\n"
            "end."
        )
        tree, errors = _parse(src)
        assert tree is not None
        assert not errors

    def test_record_type(self) -> None:
        src = (
            "program p\n"
            "type r = record integer x; char c; end;\n"
            "begin\n"
            "    read(x)\n"
            "end."
        )
        tree, errors = _parse(src)
        assert tree is not None
        assert not errors

    def test_if_statement(self) -> None:
        src = (
            "program p\n"
            "var integer x;\n"
            "begin\n"
            "    if x < 1 then x := 1 else x := 2 fi\n"
            "end."
        )
        tree, errors = _parse(src)
        assert tree is not None
        assert not errors

    def test_while_statement(self) -> None:
        src = (
            "program p\n"
            "var integer x;\n"
            "begin\n"
            "    while x < 10 do x := x + 1 endwh\n"
            "end."
        )
        tree, errors = _parse(src)
        assert tree is not None
        assert not errors

    def test_read_write(self) -> None:
        src = (
            "program p\n"
            "var integer x;\n"
            "begin\n"
            "    read(x);\n"
            "    write(x)\n"
            "end."
        )
        tree, errors = _parse(src)
        assert tree is not None
        assert not errors

    def test_return_statement(self) -> None:
        src = (
            "program p\n"
            "var integer x;\n"
            "begin\n"
            "    return(x)\n"
            "end."
        )
        tree, errors = _parse(src)
        assert tree is not None
        assert not errors

    def test_array_access_and_record_field(self) -> None:
        src = (
            "program p\n"
            "var integer x;\n"
            "begin\n"
            "    a[1] := x;\n"
            "    r.f := x\n"
            "end."
        )
        tree, errors = _parse(src)
        assert tree is not None
        assert not errors

    def test_procedure_with_params(self) -> None:
        src = (
            "program p\n"
            "var integer x;\n"
            "procedure f(integer a, b; var integer c);\n"
            "begin\n"
            "    c := a + b\n"
            "end;\n"
            "begin\n"
            "    f(1, 2, x)\n"
            "end."
        )
        tree, errors = _parse(src)
        assert tree is not None
        assert not errors

    def test_multiple_statements_semicolon(self) -> None:
        src = (
            "program p\n"
            "var integer x;\n"
            "begin\n"
            "    x := 1;\n"
            "    x := 2;\n"
            "    x := 3\n"
            "end."
        )
        tree, errors = _parse(src)
        assert tree is not None
        assert not errors

    def test_var_dec_with_type_name(self) -> None:
        src = (
            "program p\n"
            "type t = integer;\n"
            "var t x;\n"
            "begin\n"
            "    x := 1\n"
            "end."
        )
        tree, errors = _parse(src)
        assert tree is not None
        assert not errors


# ---------------------------------------------------------------------------
# 错误测试
# ---------------------------------------------------------------------------
class TestSyntaxErrors:
    def test_missing_begin(self) -> None:
        src = "program p x := 1 end."
        tokens, _ = LexicalAnalyzer(src).analyze()
        tree, errors = RecursiveDescentParser(tokens).parse()
        assert errors

    def test_missing_end(self) -> None:
        src = "program p begin x := 1 ."
        tokens, _ = LexicalAnalyzer(src).analyze()
        tree, errors = RecursiveDescentParser(tokens).parse()
        assert errors

    def test_missing_dot(self) -> None:
        src = "program p begin end"
        tokens, _ = LexicalAnalyzer(src).analyze()
        tree, errors = RecursiveDescentParser(tokens).parse()
        assert errors

    def test_missing_fi(self) -> None:
        src = (
            "program p\n"
            "var integer x;\n"
            "begin\n"
            "    if x < 1 then x := 1 else x := 2\n"
            "end."
        )
        tree, errors = _parse(src)
        assert errors

    def test_missing_then(self) -> None:
        src = (
            "program p\n"
            "var integer x;\n"
            "begin\n"
            "    if x < 1 x := 1 else x := 2 fi\n"
            "end."
        )
        tree, errors = _parse(src)
        assert errors

    def test_illegal_statement_start(self) -> None:
        src = (
            "program p\n"
            "var integer x;\n"
            "begin\n"
            "    + := 1\n"
            "end."
        )
        tree, errors = _parse(src)
        assert errors

    def test_extra_content_after_program(self) -> None:
        src = "program p begin end. abc"
        tokens, _ = LexicalAnalyzer(src).analyze()
        tree, errors = RecursiveDescentParser(tokens).parse()
        assert errors
        assert "多余内容" in errors[-1]


# ---------------------------------------------------------------------------
# 语法树结构验证
# ---------------------------------------------------------------------------
class TestTreeStructure:
    def test_program_head_children(self) -> None:
        src = "program p begin end."
        tree, _ = _parse(src)
        assert tree is not None
        ph = tree.children[0]
        assert ph.name == "ProgramHead"
        assert ph.children[0].token.token_type == TokenType.PROGRAM
        assert ph.children[1].token.token_type == TokenType.ID
        assert ph.children[1].token.sem_value == "p"

    def test_declare_part_has_three_children(self) -> None:
        src = (
            "program p\n"
            "type t = integer;\n"
            "var integer x;\n"
            "procedure f();\n"
            "begin end;\n"
            "begin end."
        )
        tree, _ = _parse(src)
        dp = tree.children[1]
        assert dp.name == "DeclarePart"
        assert len(dp.children) == 3

    def test_array_type_node_structure(self) -> None:
        src = (
            "program p\n"
            "type a = array [1 .. 10] of integer;\n"
            "begin end."
        )
        tree, _ = _parse(src)
        type_dec = tree.children[1].children[0].children[0]
        tdl = type_dec.children[1]
        tdef = tdl.children[2]
        struct_type = tdef.children[0]
        assert struct_type.name == "StructureType"
        arr = struct_type.children[0]
        assert arr.name == "ArrayType"
        assert arr.children[2].token.token_type == TokenType.INTC
        assert arr.children[2].token.sem_value == "1"
        assert arr.children[4].token.token_type == TokenType.INTC
        assert arr.children[4].token.sem_value == "10"
