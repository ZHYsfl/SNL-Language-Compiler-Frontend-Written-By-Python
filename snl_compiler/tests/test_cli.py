"""CLI 单元测试。"""

from __future__ import annotations
import tempfile
from pathlib import Path

from snl_compiler.cli import main


def test_cli_help() -> None:
    assert main(["--help"]) == 0


def test_cli_no_args() -> None:
    assert main([]) == 0


def test_cli_file_not_found() -> None:
    assert main(["nonexistent.snl"]) == 1


def test_cli_run(capsys) -> None:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".snl", delete=False, encoding="utf-8") as f:
        f.write("program p\nvar integer x;\nbegin\n    x := 1\nend.\n")
        path = f.name
    try:
        assert main([path]) == 0
        captured = capsys.readouterr()
        assert "Token" in captured.out
    finally:
        Path(path).unlink()


def test_cli_tokens(capsys) -> None:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".snl", delete=False, encoding="utf-8") as f:
        f.write("program p begin end.\n")
        path = f.name
    try:
        assert main([path, "--tokens"]) == 0
        captured = capsys.readouterr()
        assert "Token" in captured.out
    finally:
        Path(path).unlink()


def test_cli_parse(capsys) -> None:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".snl", delete=False, encoding="utf-8") as f:
        f.write("program p begin end.\n")
        path = f.name
    try:
        assert main([path, "--parse"]) == 0
        captured = capsys.readouterr()
        assert "语法树" in captured.out
    finally:
        Path(path).unlink()


def test_cli_semantic(capsys) -> None:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".snl", delete=False, encoding="utf-8") as f:
        f.write("program p\nvar integer x;\nbegin\n    x := 1\nend.\n")
        path = f.name
    try:
        assert main([path, "--semantic"]) == 0
        captured = capsys.readouterr()
        assert "符 号 表" in captured.out
    finally:
        Path(path).unlink()
