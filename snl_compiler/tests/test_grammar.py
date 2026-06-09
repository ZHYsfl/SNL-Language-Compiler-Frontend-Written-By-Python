"""grammar.py 加载测试。"""

from snl_compiler.grammar import SNL_PRODUCTIONS, NON_TERMINALS, Production


def test_productions_loaded() -> None:
    assert len(SNL_PRODUCTIONS) > 0
    assert "Program" in NON_TERMINALS
    assert isinstance(SNL_PRODUCTIONS[0], Production)
