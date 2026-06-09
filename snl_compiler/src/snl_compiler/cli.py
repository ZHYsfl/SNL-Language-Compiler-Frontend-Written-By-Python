"""SNL 编译器命令行接口。"""

from __future__ import annotations
import sys
from pathlib import Path

from snl_compiler.pipeline import compile_snl


def _print_tokens(tokens: list) -> None:
    print("=" * 70)
    print("                         Token 序列")
    print("=" * 70)
    print(f"{'Type':<15} {'Value':<20} {'Line':<6} {'Col':<6}")
    print("-" * 70)
    for tok in tokens:
        if tok.token_type.value == "EOF":
            continue
        print(f"{tok.token_type.value:<15} {tok.sem_value:<20} {tok.line:<6} {tok.col:<6}")
    print("-" * 70)


def _print_tree(node, indent: int = 0) -> None:
    if node is None:
        return
    prefix = "  " * indent
    if node.token is not None:
        print(f"{prefix}{node.name}: {node.token.sem_value}")
    else:
        print(f"{prefix}{node.name}")
    for child in node.children:
        _print_tree(child, indent + 1)


def _tree_lines(node, indent: int = 0) -> list[str]:
    """返回语法树的文本行列表，用于写入文件。"""
    lines: list[str] = []
    if node is None:
        return lines
    prefix = "  " * indent
    if node.token is not None:
        lines.append(f"{prefix}{node.name}: {node.token.sem_value}")
    else:
        lines.append(f"{prefix}{node.name}")
    for child in node.children:
        lines.extend(_tree_lines(child, indent + 1))
    return lines


def main(args: list[str] | None = None) -> int:
    if args is None:
        args = sys.argv[1:]

    # Windows 终端默认 GBK，强制 UTF-8 避免中文乱码
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
            sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except (AttributeError, OSError):
            pass

    if not args or args[0] in ("-h", "--help"):
        print("Usage: python -m snl_compiler <file.snl> [options]")
        print("Options:")
        print("  --tokens    仅输出词法分析结果")
        print("  --parse     输出语法分析结果（含语法树）")
        print("  --semantic  输出完整语义分析结果")
        return 0

    filepath = args[0]
    show_tokens = "--tokens" in args
    show_parse = "--parse" in args
    show_semantic = "--semantic" in args

    if not Path(filepath).exists():
        print(f"错误: 文件 '{filepath}' 不存在")
        return 1

    source = Path(filepath).read_text(encoding="utf-8")
    result = compile_snl(source)

    # 词法错误
    if result.lexical_errors:
        print("\n[词法错误]")
        for err in result.lexical_errors:
            print(f"  {err}")

    # 语法错误
    if result.syntax_errors:
        print("\n[语法错误]")
        for err in result.syntax_errors:
            print(f"  {err}")

    # 输出控制
    if show_tokens or not (show_parse or show_semantic):
        _print_tokens(result.tokens)

    if show_parse or show_semantic:
        if result.syntax_tree is not None:
            print("\n" + "=" * 70)
            print("                         语法树")
            print("=" * 70)
            _print_tree(result.syntax_tree)
        else:
            print("\n语法树生成失败")

    if show_semantic and result.semantic_result is not None:
        print("\n" + result.semantic_result.type_table)
        print("\n" + result.semantic_result.symbol_table)
        if result.semantic_result.errors:
            print("\n[语义错误]")
            for err in result.semantic_result.errors:
                print(f"  {err}")
        else:
            print("\n语义分析完成，未发现语义错误。")

    # 保存结果到文件
    out_dir = Path(filepath).parent or Path(".")
    base = Path(filepath).stem

    # 保存 Token 序列（始终保存）
    token_lines = [f"{'Type':<15} {'Value':<20} {'Line':<6} {'Col':<6}", "-" * 60]
    for tok in result.tokens:
        if tok.token_type.value == "EOF":
            continue
        token_lines.append(f"{tok.token_type.value:<15} {tok.sem_value:<20} {tok.line:<6} {tok.col:<6}")
    (out_dir / f"{base}_tokens.txt").write_text("\n".join(token_lines), encoding="utf-8")

    # 保存词法错误（始终保存）
    lex_err_text = "\n".join(result.lexical_errors) if result.lexical_errors else "未发现词法错误。"
    (out_dir / f"{base}_词法错误.txt").write_text(lex_err_text, encoding="utf-8")

    saved: list[str] = [f"{base}_tokens.txt", f"{base}_词法错误.txt"]

    # 词法无错才继续保存语法阶段产物
    if not result.lexical_errors:
        # 保存语法错误
        syn_err_text = "\n".join(result.syntax_errors) if result.syntax_errors else "未发现语法错误。"
        (out_dir / f"{base}_语法错误.txt").write_text(syn_err_text, encoding="utf-8")
        saved.append(f"{base}_语法错误.txt")

        # 保存语法树
        if result.syntax_tree is not None:
            tree_text = "\n".join(_tree_lines(result.syntax_tree))
            (out_dir / f"{base}_语法树.txt").write_text(tree_text, encoding="utf-8")
            saved.append(f"{base}_语法树.txt")

        # 语法也无错才保存语义阶段产物
        if not result.syntax_errors and result.semantic_result is not None:
            (out_dir / f"{base}_符号表.txt").write_text(
                result.semantic_result.type_table + "\n\n" + result.semantic_result.symbol_table,
                encoding="utf-8",
            )
            saved.append(f"{base}_符号表.txt")
            err_text = "\n".join(result.semantic_result.errors) if result.semantic_result.errors else "语义分析完成，未发现语义错误。"
            (out_dir / f"{base}_语义错误.txt").write_text(err_text, encoding="utf-8")
            saved.append(f"{base}_语义错误.txt")

    print(f"\n结果已保存到: {', '.join(saved)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
