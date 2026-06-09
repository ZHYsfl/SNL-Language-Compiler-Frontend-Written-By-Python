"""语义分析单元测试 — 目标覆盖率 >95%。"""

from __future__ import annotations
import pytest

from snl_compiler.lexer import LexicalAnalyzer
from snl_compiler.rd_parser import RecursiveDescentParser
from snl_compiler.semantic_analyzer import SemanticAnalyzer


def _analyze(src: str) -> tuple:
    tokens, lex_err = LexicalAnalyzer(src).analyze()
    assert not lex_err, f"词法错误: {lex_err}"
    tree, syn_err = RecursiveDescentParser(tokens).parse()
    assert not syn_err, f"语法错误: {syn_err}"
    return SemanticAnalyzer().analyze(tree)


# ---------------------------------------------------------------------------
# 正向测试
# ---------------------------------------------------------------------------
class TestCorrectPrograms:
    def test_minimal_correct(self) -> None:
        src = (
            "program p\n"
            "var integer x;\n"
            "begin\n"
            "    x := 1\n"
            "end."
        )
        result = _analyze(src)
        assert not result.errors

    def test_type_alias(self) -> None:
        src = (
            "program p\n"
            "type t = integer;\n"
            "var t x;\n"
            "begin\n"
            "    x := 1\n"
            "end."
        )
        result = _analyze(src)
        assert not result.errors

    def test_array_and_record(self) -> None:
        src = (
            "program p\n"
            "type a = array [1 .. 5] of integer;\n"
            "    r = record integer x; char c; end;\n"
            "var a arr;\n"
            "    r rec;\n"
            "begin\n"
            "    arr[1] := 10;\n"
            "    rec.x := 5\n"
            "end."
        )
        result = _analyze(src)
        assert not result.errors

    def test_procedure_call(self) -> None:
        src = (
            "program p\n"
            "var integer x;\n"
            "procedure f(integer a);\n"
            "begin\n"
            "    x := a\n"
            "end;\n"
            "begin\n"
            "    f(1)\n"
            "end."
        )
        result = _analyze(src)
        assert not result.errors

    def test_if_while(self) -> None:
        src = (
            "program p\n"
            "var integer x;\n"
            "begin\n"
            "    if x < 10 then x := 1 else x := 2 fi;\n"
            "    while x < 5 do x := x + 1 endwh\n"
            "end."
        )
        result = _analyze(src)
        assert not result.errors


# ---------------------------------------------------------------------------
# 错误测试
# ---------------------------------------------------------------------------
class TestSemanticErrors:
    def test_type_redefinition(self) -> None:
        src = (
            "program p\n"
            "type t = integer;\n"
            "    t = char;\n"
            "begin\n"
            "    read(x)\n"
            "end."
        )
        result = _analyze(src)
        assert any("重复定义" in e for e in result.errors)

    def test_var_redefinition(self) -> None:
        src = (
            "program p\n"
            "var integer x, x;\n"
            "begin\n"
            "    x := 1\n"
            "end."
        )
        result = _analyze(src)
        assert any("重复定义" in e for e in result.errors)

    def test_undeclared_identifier(self) -> None:
        src = (
            "program p\n"
            "var integer x;\n"
            "begin\n"
            "    y := 1\n"
            "end."
        )
        result = _analyze(src)
        assert any("未声明" in e for e in result.errors)

    def test_assign_type_mismatch(self) -> None:
        src = (
            "program p\n"
            "var integer x;\n"
            "    char c;\n"
            "begin\n"
            "    x := c\n"
            "end."
        )
        result = _analyze(src)
        assert any("类型不相容" in e for e in result.errors)

    def test_arith_type_mismatch(self) -> None:
        src = (
            "program p\n"
            "var integer x;\n"
            "    char c;\n"
            "begin\n"
            "    x := x + c\n"
            "end."
        )
        result = _analyze(src)
        assert any("类型不相容" in e for e in result.errors)

    def test_assign_to_type_name(self) -> None:
        src = (
            "program p\n"
            "type t = integer;\n"
            "begin\n"
            "    t := 1\n"
            "end."
        )
        result = _analyze(src)
        assert any("不是变量标识符" in e for e in result.errors)

    def test_array_index_not_int(self) -> None:
        src = (
            "program p\n"
            "type a = array [1 .. 5] of integer;\n"
            "var a arr;\n"
            "begin\n"
            "    arr[arr] := 1\n"
            "end."
        )
        result = _analyze(src)
        assert any("引用不合法" in e for e in result.errors)

    def test_subscript_on_non_array(self) -> None:
        src = (
            "program p\n"
            "var integer x;\n"
            "begin\n"
            "    x[1] := 5\n"
            "end."
        )
        result = _analyze(src)
        assert any("不是数组类型" in e for e in result.errors)

    def test_record_field_not_exist(self) -> None:
        src = (
            "program p\n"
            "type r = record integer x; end;\n"
            "var r rec;\n"
            "begin\n"
            "    rec.y := 1\n"
            "end."
        )
        result = _analyze(src)
        assert any("不存在域变量" in e for e in result.errors)

    def test_call_non_procedure(self) -> None:
        src = (
            "program p\n"
            "var integer x;\n"
            "begin\n"
            "    x(1)\n"
            "end."
        )
        result = _analyze(src)
        assert any("不是过程标识符" in e for e in result.errors)

    def test_proc_arg_count_mismatch(self) -> None:
        src = (
            "program p\n"
            "var integer x;\n"
            "procedure f(integer a);\n"
            "begin\n"
            "    x := a\n"
            "end;\n"
            "begin\n"
            "    f(1, 2)\n"
            "end."
        )
        result = _analyze(src)
        assert any("个数不相同" in e for e in result.errors)

    def test_proc_arg_type_mismatch(self) -> None:
        src = (
            "program p\n"
            "var integer x;\n"
            "    char c;\n"
            "procedure f(integer a);\n"
            "begin\n"
            "    x := a\n"
            "end;\n"
            "begin\n"
            "    f(c)\n"
            "end."
        )
        result = _analyze(src)
        assert any("参数类型不匹配" in e for e in result.errors)

    def test_cmp_type_mismatch(self) -> None:
        src = (
            "program p\n"
            "var integer x;\n"
            "    char c;\n"
            "begin\n"
            "    if x < c then x := 1 else x := 2 fi\n"
            "end."
        )
        result = _analyze(src)
        assert any("比较运算符" in e for e in result.errors)

    def test_read_undeclared(self) -> None:
        src = (
            "program p\n"
            "begin\n"
            "    read(y)\n"
            "end."
        )
        result = _analyze(src)
        assert any("未声明变量" in e for e in result.errors)
