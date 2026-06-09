"""覆盖率补强测试 — 精准覆盖各模块缺失分支。"""

from __future__ import annotations
import tempfile
from pathlib import Path

import pytest

from snl_compiler.cli import main, _print_tree
from snl_compiler.lexer import LexicalAnalyzer
from snl_compiler.rd_parser import RecursiveDescentParser
from snl_compiler.semantic_analyzer import SemanticAnalyzer
from snl_compiler.syntax_tree import TreeNode
from snl_compiler.tokens import Token, TokenType


# ---------------------------------------------------------------------------
# CLI 缺失分支
# ---------------------------------------------------------------------------
class TestCLIBranches:
    def test_print_tree_none(self) -> None:
        """覆盖 cli.py line 25: _print_tree(None)"""
        _print_tree(None)

    def test_cli_lexical_error(self, capsys) -> None:
        """覆盖 cli.py lines 61-63: 词法错误输出分支。"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".snl", delete=False, encoding="utf-8") as f:
            f.write("program p\nbegin\n    x := @\nend.\n")
            path = f.name
        try:
            assert main([path, "--tokens"]) == 0
            captured = capsys.readouterr()
            assert "词法错误" in captured.out
        finally:
            Path(path).unlink()

    def test_cli_semantic_errors(self, capsys) -> None:
        """覆盖 cli.py lines 88-90: 语义错误输出分支。"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".snl", delete=False, encoding="utf-8") as f:
            f.write("program p\nbegin\n    y := 1\nend.\n")
            path = f.name
        try:
            assert main([path, "--semantic"]) == 0
            captured = capsys.readouterr()
            assert "语义错误" in captured.out
        finally:
            Path(path).unlink()

    def test_cli_save_output(self, capsys) -> None:
        """覆盖 cli.py 98->107: 保存结果文件分支。"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".snl", delete=False, encoding="utf-8") as f:
            f.write("program p\nvar integer x;\nbegin\n    x := 1\nend.\n")
            path = f.name
        try:
            assert main([path, "--semantic"]) == 0
            out_dir = Path(path).parent
            base = Path(path).stem
            assert (out_dir / f"{base}_符号表.txt").exists()
            assert (out_dir / f"{base}_语义错误.txt").exists()
        finally:
            Path(path).unlink()
            for ext in ["_符号表.txt", "_语义错误.txt"]:
                p = Path(path).parent / (Path(path).stem + ext)
                if p.exists():
                    p.unlink()


# ---------------------------------------------------------------------------
# Parser 缺失分支
# ---------------------------------------------------------------------------
class TestParserBranches:
    def test_illegal_type_def(self) -> None:
        """覆盖 rd_parser.py _type_def else: 非法类型定义。"""
        src = "program p\ntype t = ;\nbegin\nend.\n"
        tokens, _ = LexicalAnalyzer(src).analyze()
        tree, errors = RecursiveDescentParser(tokens).parse()
        assert any("非法类型定义" in e for e in errors)

    def test_illegal_stm_start(self) -> None:
        """覆盖 rd_parser.py _stm else: 非法语句起始。"""
        src = "program p\nbegin\n+\nend.\n"
        tokens, _ = LexicalAnalyzer(src).analyze()
        tree, errors = RecursiveDescentParser(tokens).parse()
        assert any("非法语句起始" in e for e in errors)

    def test_illegal_factor(self) -> None:
        """覆盖 rd_parser.py _factor else: 非法因子。"""
        src = "program p\nbegin\n    x := +\nend.\n"
        tokens, _ = LexicalAnalyzer(src).analyze()
        tree, errors = RecursiveDescentParser(tokens).parse()
        assert any("非法因子" in e for e in errors)

    def test_cmp_op_error(self) -> None:
        """覆盖 rd_parser.py _cmp_op else: 期望比较运算符错误。"""
        src = "program p\nvar integer x;\nbegin\n    if x + 1 then x := 1 else x := 2 fi\nend.\n"
        tokens, _ = LexicalAnalyzer(src).analyze()
        tree, errors = RecursiveDescentParser(tokens).parse()
        assert any("期望比较运算符" in e for e in errors)

    def test_add_op_minus(self) -> None:
        """覆盖 rd_parser.py _add_op MINUS 分支。"""
        src = "program p\nvar integer x;\nbegin\n    x := x - 1\nend.\n"
        tokens, _ = LexicalAnalyzer(src).analyze()
        tree, errors = RecursiveDescentParser(tokens).parse()
        assert tree is not None
        assert not errors

    def test_mult_op_over(self) -> None:
        """覆盖 rd_parser.py _mult_op OVER 分支。"""
        src = "program p\nvar integer x;\nbegin\n    x := x / 1\nend.\n"
        tokens, _ = LexicalAnalyzer(src).analyze()
        tree, errors = RecursiveDescentParser(tokens).parse()
        assert tree is not None
        assert not errors


# ---------------------------------------------------------------------------
# Semantic 缺失分支
# ---------------------------------------------------------------------------
class TestSemanticBranches:
    def test_array_negative_low(self) -> None:
        """覆盖 semantic_core.py _array_type: 数组下标非法（负数）。
        直接调用内部方法，因为 lexer 会把 '-1' 拆成 MINUS 和 INTC。"""
        from snl_compiler.semantic_core import SemanticCore
        from snl_compiler.symbol_table import SymbolTable
        from snl_compiler.syntax_tree import TreeNode
        from snl_compiler.tokens import Token, TokenType

        symtab = SymbolTable()
        symtab.create_scope()
        errors: list[str] = []
        core = SemanticCore(symtab, errors)

        # 构造一个 ArrayType 节点：array [ -1 .. 5 ] of integer
        node = TreeNode("ArrayType")
        node.add_child(TreeNode("array"))
        node.add_child(TreeNode("["))
        node.add_child(TreeNode("INTC", token=Token(TokenType.INTC, "-1", 1, 1)))
        node.add_child(TreeNode(".."))
        node.add_child(TreeNode("INTC", token=Token(TokenType.INTC, "5", 1, 1)))
        node.add_child(TreeNode("]"))
        node.add_child(TreeNode("of"))
        bt = TreeNode("BaseType")
        bt.add_child(TreeNode("integer", token=Token(TokenType.INTEGER, "integer", 1, 1)))
        node.add_child(bt)

        result = core._array_type(node)
        assert result is None
        assert any("数组下标" in e for e in errors)

    def test_array_high_lt_low(self) -> None:
        """覆盖 semantic_core.py _array_type: 数组下标越界。"""
        src = (
            "program p\n"
            "type a = array [5 .. 1] of integer;\n"
            "var a arr;\n"
            "begin\n"
            "    arr[1] := 1\n"
            "end.\n"
        )
        tokens, _ = LexicalAnalyzer(src).analyze()
        tree, errors = RecursiveDescentParser(tokens).parse()
        result = SemanticAnalyzer().analyze(tree)
        assert any("数组下标越界" in e for e in result.errors)

    def test_record_field_duplicate(self) -> None:
        """覆盖 semantic_core.py _rec_type: 记录域重复定义。"""
        src = (
            "program p\n"
            "type r = record integer x; integer x; end;\n"
            "var r rec;\n"
            "begin\n"
            "    rec.x := 1\n"
            "end.\n"
        )
        tokens, _ = LexicalAnalyzer(src).analyze()
        tree, errors = RecursiveDescentParser(tokens).parse()
        result = SemanticAnalyzer().analyze(tree)
        assert any("重复定义" in e for e in result.errors)

    def test_return_stm(self) -> None:
        """覆盖 semantic_expr.py ReturnStm 路径（无报错即可）。"""
        src = (
            "program p\n"
            "var integer x;\n"
            "begin\n"
            "    return(x)\n"
            "end.\n"
        )
        tokens, _ = LexicalAnalyzer(src).analyze()
        tree, errors = RecursiveDescentParser(tokens).parse()
        result = SemanticAnalyzer().analyze(tree)
        # ReturnStm 当前不检查错误，只确认不崩溃
        assert result is not None

    def test_field_var_not_array(self) -> None:
        """覆盖 semantic_expr.py _field_var: 域不是数组类型。"""
        src = (
            "program p\n"
            "type r = record integer x; end;\n"
            "var r rec;\n"
            "begin\n"
            "    rec.x[1] := 1\n"
            "end.\n"
        )
        tokens, _ = LexicalAnalyzer(src).analyze()
        tree, errors = RecursiveDescentParser(tokens).parse()
        result = SemanticAnalyzer().analyze(tree)
        assert any("不是数组类型" in e for e in result.errors)

    def test_vari_more_dot_on_non_record(self) -> None:
        """覆盖 semantic_expr.py _vari_more: DOT 但非记录类型。"""
        src = (
            "program p\n"
            "var integer x;\n"
            "begin\n"
            "    x.y := 1\n"
            "end.\n"
        )
        tokens, _ = LexicalAnalyzer(src).analyze()
        tree, errors = RecursiveDescentParser(tokens).parse()
        result = SemanticAnalyzer().analyze(tree)
        assert any("不是记录类型" in e for e in result.errors)

    def test_arith_on_array(self) -> None:
        """覆盖 semantic_expr.py _check_arith: ARRAY/RECORD 返回 None。"""
        src = (
            "program p\n"
            "type a = array [1 .. 5] of integer;\n"
            "var a arr1, arr2;\n"
            "begin\n"
            "    arr1 := arr2 + arr1\n"
            "end.\n"
        )
        tokens, _ = LexicalAnalyzer(src).analyze()
        tree, errors = RecursiveDescentParser(tokens).parse()
        result = SemanticAnalyzer().analyze(tree)
        assert any("类型不相容" in e for e in result.errors)


# ---------------------------------------------------------------------------
# Symbol Table & Lexer 边界
# ---------------------------------------------------------------------------
class TestInternalsBranches:
    def test_symbol_table_enter_duplicate_kind(self) -> None:
        """覆盖 symbol_table.py enter 中 kind 匹配分支。"""
        from snl_compiler.symbol_table import SymbolTable, SymbolEntry, IdentifierKind

        st = SymbolTable()
        st.create_scope()
        e1 = SymbolEntry(idname="x", kind=IdentifierKind.VAR_KIND)
        assert st.enter("x", e1, IdentifierKind.VAR_KIND) is not None
        e2 = SymbolEntry(idname="x", kind=IdentifierKind.VAR_KIND)
        assert st.enter("x", e2, IdentifierKind.VAR_KIND) is None

    def test_lexer_unclosed_comment(self) -> None:
        """覆盖 lexer.py 未闭合注释后的错误 Token 路径。
        当注释未闭合遇到 EOF 时，lexer 会报告非法字符 'EOF' 并返回 EOF token。"""
        src = "program p\n{ unclosed comment\nbegin end.\n"
        tokens, errors = LexicalAnalyzer(src).analyze()
        assert any("非法字符" in e and "EOF" in e for e in errors)
        # 确保 lexer 仍然返回 EOF token 并结束
        assert tokens[-1].token_type == TokenType.EOF
