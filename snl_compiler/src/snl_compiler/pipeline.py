"""SNL 编译器三阶段流水线串联。

封装 词法分析 → 语法分析 → 语义分析 的完整流程。
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

from snl_compiler.tokens import Token
from snl_compiler.lexer import LexicalAnalyzer
from snl_compiler.rd_parser import RecursiveDescentParser
from snl_compiler.syntax_tree import TreeNode
from snl_compiler.semantic_analyzer import SemanticAnalyzer, SemanticResult


@dataclass
class CompileResult:
    """完整编译结果。"""

    tokens: List[Token]
    syntax_tree: Optional[TreeNode]
    semantic_result: Optional[SemanticResult]
    lexical_errors: List[str]
    syntax_errors: List[str]


def compile_snl(source: str) -> CompileResult:
    """对 SNL 源程序进行完整分析。

    依次执行词法分析、语法分析、语义分析，
    返回各阶段结果与错误信息。
    """
    # 阶段1: 词法分析
    lexer = LexicalAnalyzer(source)
    tokens, lex_errs = lexer.analyze()

    # 阶段2: 语法分析
    parser = RecursiveDescentParser(tokens)
    tree, syn_errs = parser.parse()

    # 阶段3: 语义分析（仅当语法树有效时）
    sem_result: Optional[SemanticResult] = None
    if tree is not None:
        sem = SemanticAnalyzer()
        sem_result = sem.analyze(tree)

    return CompileResult(
        tokens=tokens,
        syntax_tree=tree,
        semantic_result=sem_result,
        lexical_errors=lex_errs,
        syntax_errors=syn_errs,
    )
