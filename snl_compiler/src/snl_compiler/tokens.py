"""SNL 编译器统一 Token 定义。

严格依据实验中的单词分类：
- 标识符 (ID)、保留字、无符号整数 (INTC)
- 单字符分界符、双字符分界符 (:=)、数组下标界限符 (..)
- 特殊 Token: EOF
"""

from __future__ import annotations
from enum import Enum, unique
from dataclasses import dataclass


@unique
class TokenType(Enum):
    """SNL 单词类别枚举（终结符的类别枚举）。"""

    # 保留字 (保留字是标识符的子集)
    PROGRAM = "PROGRAM"
    TYPE = "TYPE"
    VAR = "VAR"
    PROCEDURE = "PROCEDURE"
    BEGIN = "BEGIN"
    END = "END"
    ARRAY = "ARRAY"
    OF = "OF"
    RECORD = "RECORD"
    IF = "IF"
    THEN = "THEN"
    ELSE = "ELSE"
    FI = "FI"
    WHILE = "WHILE"
    DO = "DO"
    ENDWH = "ENDWH"
    READ = "READ"
    WRITE = "WRITE"
    RETURN = "RETURN"
    INTEGER = "INTEGER"
    CHAR = "CHAR"

    # 标识符与常量
    ID = "ID"
    INTC = "INTC"

    # 单字符分界符
    PLUS = "+"
    MINUS = "-"
    TIMES = "*"
    OVER = "/"
    LT = "<"
    EQ = "="
    LPAREN = "("
    RPAREN = ")"
    LMIDPAREN = "["
    RMIDPAREN = "]"
    DOT = "."
    SEMI = ";"
    COMMA = ","

    # 双字符分界符
    ASSIGN = ":="

    # 数组下标界限符
    UNDERANGE = ".."

    # 输入结束
    EOF = "EOF"


# 保留字表：保留字是标识符的子集
RESERVED_WORDS: dict[str, TokenType] = {
    "program": TokenType.PROGRAM,
    "type": TokenType.TYPE,
    "var": TokenType.VAR,
    "procedure": TokenType.PROCEDURE,
    "begin": TokenType.BEGIN,
    "end": TokenType.END,
    "array": TokenType.ARRAY,
    "of": TokenType.OF,
    "record": TokenType.RECORD,
    "if": TokenType.IF,
    "then": TokenType.THEN,
    "else": TokenType.ELSE,
    "fi": TokenType.FI,
    "while": TokenType.WHILE,
    "do": TokenType.DO,
    "endwh": TokenType.ENDWH,
    "read": TokenType.READ,
    "write": TokenType.WRITE,
    "return": TokenType.RETURN,
    "integer": TokenType.INTEGER,
    "char": TokenType.CHAR,
}

# 单字符分界符到 Token 类型的映射
SINGLE_DELIM_MAP: dict[str, TokenType] = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.TIMES,
    "/": TokenType.OVER,
    "<": TokenType.LT,
    "=": TokenType.EQ,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "[": TokenType.LMIDPAREN,
    "]": TokenType.RMIDPAREN,
    ".": TokenType.DOT,
    ";": TokenType.SEMI,
    ",": TokenType.COMMA,
}


@dataclass(frozen=True, slots=True)
class Token:
    """单词的内部表示序列 — Token。"""

    token_type: TokenType
    sem_value: str
    line: int
    col: int

    def __repr__(self) -> str:
        return (
            f"Token({self.token_type.value}, "
            f"'{self.sem_value}', line={self.line}, col={self.col})"
        )
