"""语法分析器边缘分支测试 — 提升覆盖率。"""

from __future__ import annotations
from snl_compiler.lexer import LexicalAnalyzer
from snl_compiler.rd_parser import RecursiveDescentParser


def _parse(src: str) -> tuple:
    tokens, lex_err = LexicalAnalyzer(src).analyze()
    assert not lex_err, f"词法错误: {lex_err}"
    return RecursiveDescentParser(tokens).parse()


class TestParserEdgeCases:
    def test_type_def_with_id(self) -> None:
        """覆盖 _type_def 的 ID 分支。"""
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

    def test_field_dec_error(self) -> None:
        """覆盖 _field_dec_list 的错误分支。"""
        src = (
            "program p\n"
            "type r = record\n"
            "    t x;\n"
            "end;\n"
            "begin\n"
            "    read(x)\n"
            "end."
        )
        tree, errors = _parse(src)
        assert tree is not None
        # parser 应报类型错误
        assert errors

    def test_var_dec_more(self) -> None:
        """覆盖 _var_dec_more 的分支。"""
        src = (
            "program p\n"
            "var integer x;\n"
            "    integer y;\n"
            "begin\n"
            "    x := 1\n"
            "end."
        )
        tree, errors = _parse(src)
        assert tree is not None
        assert not errors

    def test_vari_more_array(self) -> None:
        """覆盖 _vari_more 的数组分支。"""
        src = (
            "program p\n"
            "type a = array [1 .. 5] of integer;\n"
            "var a arr;\n"
            "begin\n"
            "    arr[1] := 10\n"
            "end."
        )
        tree, errors = _parse(src)
        assert tree is not None
        assert not errors

    def test_vari_more_record(self) -> None:
        """覆盖 _vari_more 的记录分支。"""
        src = (
            "program p\n"
            "type r = record integer x; end;\n"
            "var r rec;\n"
            "begin\n"
            "    rec.x := 10\n"
            "end."
        )
        tree, errors = _parse(src)
        assert tree is not None
        assert not errors

    def test_field_var_more_array(self) -> None:
        """覆盖 _field_var_more 的数组分支。"""
        src = (
            "program p\n"
            "type r = record integer a; end;\n"
            "var r rec;\n"
            "begin\n"
            "    rec.a[1] := 10\n"
            "end."
        )
        tree, errors = _parse(src)
        assert tree is not None
        assert not errors

    def test_output_stm(self) -> None:
        """覆盖 _output_stm。"""
        src = (
            "program p\n"
            "var integer x;\n"
            "begin\n"
            "    write(x)\n"
            "end."
        )
        tree, errors = _parse(src)
        assert tree is not None
        assert not errors

    def test_field_dec_array(self) -> None:
        """覆盖 _field_dec_list 的 ARRAY 分支。"""
        src = (
            "program p\n"
            "type r = record\n"
            "    array [1 .. 5] of integer a;\n"
            "end;\n"
            "begin\n"
            "    read(x)\n"
            "end."
        )
        tree, errors = _parse(src)
        assert tree is not None
        assert not errors

    def test_field_dec_more(self) -> None:
        """覆盖 _field_dec_more。"""
        src = (
            "program p\n"
            "type r = record\n"
            "    integer x;\n"
            "    integer y;\n"
            "end;\n"
            "begin\n"
            "    read(z)\n"
            "end."
        )
        tree, errors = _parse(src)
        assert tree is not None
        assert not errors

    def test_vari_more_empty(self) -> None:
        """覆盖 _vari_more 的 ε 分支。"""
        src = (
            "program p\n"
            "var integer x;\n"
            "begin\n"
            "    x := 1\n"
            "end."
        )
        tree, errors = _parse(src)
        assert tree is not None
        assert not errors

    def test_field_var_empty(self) -> None:
        """覆盖 _field_var 的 ε 分支。"""
        src = (
            "program p\n"
            "type r = record integer x; end;\n"
            "var r rec;\n"
            "begin\n"
            "    rec.x := 1\n"
            "end."
        )
        tree, errors = _parse(src)
        assert tree is not None
        assert not errors

    def test_var_dec_more_empty(self) -> None:
        """覆盖 _var_dec_more 的 ε 分支。"""
        src = (
            "program p\n"
            "var integer x;\n"
            "begin\n"
            "    x := 1\n"
            "end."
        )
        tree, errors = _parse(src)
        assert tree is not None
        assert not errors

    def test_type_def_error(self) -> None:
        """覆盖 _type_def 的错误分支。"""
        src = (
            "program p\n"
            "type t = ;\n"
            "begin\n"
            "    read(x)\n"
            "end."
        )
        tree, errors = _parse(src)
        assert tree is not None
        assert errors
