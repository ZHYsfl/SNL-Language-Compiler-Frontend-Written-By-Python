"""语法树节点单元测试。"""

from snl_compiler.tokens import Token, TokenType
from snl_compiler.syntax_tree import TreeNode


def test_treenode_add_child_none() -> None:
    n = TreeNode("Test")
    n.add_child(None)
    assert len(n.children) == 0  # None 被忽略


def test_treenode_repr_leaf() -> None:
    tok = Token(TokenType.ID, "x", 1, 1)
    n = TreeNode("ID", token=tok)
    assert "Leaf" in repr(n)


def test_treenode_repr_node() -> None:
    n = TreeNode("Program", children=[TreeNode("ProgramHead")])
    assert "Node" in repr(n)
