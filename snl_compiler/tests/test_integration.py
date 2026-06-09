"""端到端集成测试。"""

from __future__ import annotations

from snl_compiler.pipeline import compile_snl
from snl_compiler.tokens import TokenType


class TestIntegration:
    def test_correct_program(self) -> None:
        src = (
            "program p\n"
            "type t = integer;\n"
            "var t x;\n"
            "begin\n"
            "    x := 1\n"
            "end."
        )
        result = compile_snl(src)
        assert not result.lexical_errors
        assert not result.syntax_errors
        assert result.syntax_tree is not None
        assert result.semantic_result is not None
        assert not result.semantic_result.errors

    def test_lexical_error(self) -> None:
        src = "program p begin x := @ end."
        result = compile_snl(src)
        assert result.lexical_errors
        assert result.syntax_tree is not None  # parser 会继续

    def test_syntax_error(self) -> None:
        src = "program p begin x := 1 ."
        result = compile_snl(src)
        assert result.syntax_errors
        assert result.semantic_result is not None

    def test_semantic_error(self) -> None:
        src = (
            "program p\n"
            "var integer x;\n"
            "begin\n"
            "    x := y\n"
            "end."
        )
        result = compile_snl(src)
        assert not result.lexical_errors
        assert not result.syntax_errors
        assert result.semantic_result is not None
        assert result.semantic_result.errors

    def test_token_sequence(self) -> None:
        src = "program p begin x := 1 end."
        result = compile_snl(src)
        types = [t.token_type for t in result.tokens]
        assert TokenType.PROGRAM in types
        assert TokenType.ID in types
        assert TokenType.BEGIN in types
        assert TokenType.END in types
        assert TokenType.DOT in types
        assert TokenType.EOF in types

    def test_symbol_table_output(self) -> None:
        src = (
            "program p\n"
            "var integer x;\n"
            "begin\n"
            "    x := 1\n"
            "end."
        )
        result = compile_snl(src)
        assert result.semantic_result is not None
        assert "符 号 表" in result.semantic_result.symbol_table
        assert "x" in result.semantic_result.symbol_table

    def test_full_analysis_with_procedure(self) -> None:
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
        result = compile_snl(src)
        assert not result.lexical_errors
        assert not result.syntax_errors
        assert result.semantic_result is not None
        assert not result.semantic_result.errors
