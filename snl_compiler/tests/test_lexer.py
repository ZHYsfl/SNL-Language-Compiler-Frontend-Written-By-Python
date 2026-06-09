"""词法分析器单元测试 — 目标覆盖率 100%。"""

from __future__ import annotations
import pytest

from snl_compiler.tokens import TokenType
from snl_compiler.lexer import LexicalAnalyzer


# ---------------------------------------------------------------------------
# 正向测试：基本 Token 类别
# ---------------------------------------------------------------------------
class TestBasicTokens:
    def test_empty_source(self) -> None:
        lexer = LexicalAnalyzer("")
        tokens, errors = lexer.analyze()
        assert len(tokens) == 1
        assert tokens[0].token_type == TokenType.EOF
        assert not errors

    def test_only_whitespace(self) -> None:
        lexer = LexicalAnalyzer("   \n\t\r  ")
        tokens, errors = lexer.analyze()
        assert len(tokens) == 1
        assert tokens[0].token_type == TokenType.EOF

    def test_only_comment(self) -> None:
        lexer = LexicalAnalyzer("{ this is a comment }")
        tokens, errors = lexer.analyze()
        assert len(tokens) == 1
        assert tokens[0].token_type == TokenType.EOF
        assert not errors

    def test_identifier(self) -> None:
        lexer = LexicalAnalyzer("abc")
        tokens, _ = lexer.analyze()
        assert tokens[0].token_type == TokenType.ID
        assert tokens[0].sem_value == "abc"

    def test_identifier_mixed_alnum(self) -> None:
        lexer = LexicalAnalyzer("a1b2")
        tokens, _ = lexer.analyze()
        assert tokens[0].token_type == TokenType.ID
        assert tokens[0].sem_value == "a1b2"

    def test_intc(self) -> None:
        lexer = LexicalAnalyzer("123")
        tokens, _ = lexer.analyze()
        assert tokens[0].token_type == TokenType.INTC
        assert tokens[0].sem_value == "123"

    def test_intc_zero(self) -> None:
        lexer = LexicalAnalyzer("0")
        tokens, _ = lexer.analyze()
        assert tokens[0].token_type == TokenType.INTC
        assert tokens[0].sem_value == "0"


# ---------------------------------------------------------------------------
# 保留字测试（大小写敏感 — SNL 通常为小写）
# ---------------------------------------------------------------------------
class TestReservedWords:
    def test_all_reserved_words(self) -> None:
        src = (
            "program type var procedure begin end array of record "
            "if then else fi while do endwh read write return integer char"
        )
        lexer = LexicalAnalyzer(src)
        tokens, _ = lexer.analyze()
        expected = [
            TokenType.PROGRAM, TokenType.TYPE, TokenType.VAR,
            TokenType.PROCEDURE, TokenType.BEGIN, TokenType.END,
            TokenType.ARRAY, TokenType.OF, TokenType.RECORD,
            TokenType.IF, TokenType.THEN, TokenType.ELSE,
            TokenType.FI, TokenType.WHILE, TokenType.DO,
            TokenType.ENDWH, TokenType.READ, TokenType.WRITE,
            TokenType.RETURN, TokenType.INTEGER, TokenType.CHAR,
        ]
        assert len(tokens) == len(expected) + 1  # +EOF
        for i, exp in enumerate(expected):
            assert tokens[i].token_type == exp, f"index {i}"


# ---------------------------------------------------------------------------
# 分界符测试
# ---------------------------------------------------------------------------
class TestDelimiters:
    def test_single_delimiters(self) -> None:
        src = "+ - * / < = ( ) [ ] . ; ,"
        lexer = LexicalAnalyzer(src)
        tokens, _ = lexer.analyze()
        expected = [
            TokenType.PLUS, TokenType.MINUS, TokenType.TIMES, TokenType.OVER,
            TokenType.LT, TokenType.EQ, TokenType.LPAREN, TokenType.RPAREN,
            TokenType.LMIDPAREN, TokenType.RMIDPAREN, TokenType.DOT,
            TokenType.SEMI, TokenType.COMMA,
        ]
        assert len(tokens) == len(expected) + 1
        for i, exp in enumerate(expected):
            assert tokens[i].token_type == exp

    def test_assign(self) -> None:
        lexer = LexicalAnalyzer(":=")
        tokens, _ = lexer.analyze()
        assert tokens[0].token_type == TokenType.ASSIGN
        assert tokens[0].sem_value == ":="

    def test_underange(self) -> None:
        lexer = LexicalAnalyzer("..")
        tokens, _ = lexer.analyze()
        assert tokens[0].token_type == TokenType.UNDERANGE
        assert tokens[0].sem_value == ".."

    def test_dot_vs_underange(self) -> None:
        lexer = LexicalAnalyzer(". ..")
        tokens, _ = lexer.analyze()
        assert tokens[0].token_type == TokenType.DOT
        assert tokens[1].token_type == TokenType.UNDERANGE


# ---------------------------------------------------------------------------
# 注释测试
# ---------------------------------------------------------------------------
class TestComments:
    def test_comment_skipped(self) -> None:
        lexer = LexicalAnalyzer("{ comment } abc")
        tokens, _ = lexer.analyze()
        assert tokens[0].token_type == TokenType.ID
        assert tokens[0].sem_value == "abc"

    def test_comment_multiline(self) -> None:
        lexer = LexicalAnalyzer("{ line1\nline2 } 42")
        tokens, _ = lexer.analyze()
        assert tokens[0].token_type == TokenType.INTC
        assert tokens[0].line == 2

    def test_unclosed_comment(self) -> None:
        lexer = LexicalAnalyzer("{ never ends")
        tokens, errors = lexer.analyze()
        assert errors
        assert "注释" in errors[0] or "非法字符" in errors[0]


# ---------------------------------------------------------------------------
# 括号匹配测试
# ---------------------------------------------------------------------------
class TestBracketMatching:
    def test_matched_parens(self) -> None:
        lexer = LexicalAnalyzer("( )")
        tokens, errors = lexer.analyze()
        assert not errors
        assert tokens[0].token_type == TokenType.LPAREN
        assert tokens[1].token_type == TokenType.RPAREN

    def test_matched_brackets(self) -> None:
        lexer = LexicalAnalyzer("[ ]")
        tokens, errors = lexer.analyze()
        assert not errors
        assert tokens[0].token_type == TokenType.LMIDPAREN
        assert tokens[1].token_type == TokenType.RMIDPAREN

    def test_unmatched_right_paren(self) -> None:
        lexer = LexicalAnalyzer(")")
        tokens, errors = lexer.analyze()
        assert errors
        assert "括号不匹配" in errors[0]

    def test_unmatched_left_paren_eof(self) -> None:
        lexer = LexicalAnalyzer("(")
        tokens, errors = lexer.analyze()
        assert errors
        assert "未闭合" in errors[0]

    def test_mismatched_bracket_types(self) -> None:
        lexer = LexicalAnalyzer("( ]")
        tokens, errors = lexer.analyze()
        assert errors
        assert "不匹配" in errors[0]


# ---------------------------------------------------------------------------
# 错误测试
# ---------------------------------------------------------------------------
class TestLexicalErrors:
    def test_illegal_character(self) -> None:
        lexer = LexicalAnalyzer("@")
        tokens, errors = lexer.analyze()
        assert errors
        assert "非法字符" in errors[0]

    def test_single_colon(self) -> None:
        lexer = LexicalAnalyzer(":")
        tokens, errors = lexer.analyze()
        assert errors
        assert "非法字符" in errors[0]

    def test_illegal_after_valid(self) -> None:
        lexer = LexicalAnalyzer("abc @")
        tokens, errors = lexer.analyze()
        assert tokens[0].token_type == TokenType.ID
        assert errors
        assert "非法字符" in errors[0]


# ---------------------------------------------------------------------------
# 综合正向程序
# ---------------------------------------------------------------------------
class TestMiniPrograms:
    def test_simple_assignment(self) -> None:
        src = "x := 1"
        lexer = LexicalAnalyzer(src)
        tokens, errors = lexer.analyze()
        assert not errors
        types = [t.token_type for t in tokens[:-1]]
        assert types == [TokenType.ID, TokenType.ASSIGN, TokenType.INTC]

    def test_array_declaration(self) -> None:
        src = "array [1 .. 10] of integer"
        lexer = LexicalAnalyzer(src)
        tokens, errors = lexer.analyze()
        assert not errors
        types = [t.token_type for t in tokens[:-1]]
        assert types == [
            TokenType.ARRAY, TokenType.LMIDPAREN, TokenType.INTC,
            TokenType.UNDERANGE, TokenType.INTC, TokenType.RMIDPAREN,
            TokenType.OF, TokenType.INTEGER,
        ]

    def test_line_col_tracking(self) -> None:
        src = "abc\ndef"
        lexer = LexicalAnalyzer(src)
        tokens, _ = lexer.analyze()
        assert tokens[0].line == 1 and tokens[0].col == 1
        assert tokens[1].line == 2 and tokens[1].col == 1

    def test_column_after_two_char_token(self) -> None:
        src = ":= x"
        lexer = LexicalAnalyzer(src)
        tokens, _ = lexer.analyze()
        assert tokens[0].col == 1
        assert tokens[1].col == 4

    def test_complex_program(self) -> None:
        src = (
            "program test\n"
            "type\n"
            "    t1 = integer;\n"
            "var\n"
            "    integer i;\n"
            "begin\n"
            "    read(i);\n"
            "    i := i + 1\n"
            "end."
        )
        lexer = LexicalAnalyzer(src)
        tokens, errors = lexer.analyze()
        assert not errors
        assert tokens[0].token_type == TokenType.PROGRAM
        assert tokens[-1].token_type == TokenType.EOF
