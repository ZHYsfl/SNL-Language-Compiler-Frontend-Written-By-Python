"""SNL 词法分析器 — 基于 DFA 状态转换表实现。

实验要求步骤：
1. 确定单词分类;
2. 单词的正则表达式定义（词法定义）;
3. 构造 DFA;
4. 根据 DFA 生成单词识别函数。

特殊情形处理：注释 {...}、括号匹配检查、向前扫描 (:= / ..)。
"""

from __future__ import annotations
from enum import Enum, auto
from typing import List, Tuple

from snl_compiler.tokens import Token, TokenType, RESERVED_WORDS, SINGLE_DELIM_MAP


class _State(Enum):
    """DFA 状态。"""
    START = auto() # 遇到空格，换行，或刚启动
    INID = auto() # 在读标识符
    INNUM = auto() # 在读数字
    INASSIGN = auto()      # 在读赋值符，已读 ':'，需前瞻 '='
    INUNDERANGE = auto()   # 在读下标界限，已读 '.'，需前瞻 '.'
    INCOMMENT = auto() # 在读注释
    DONE = auto() # 完成，当前Token已经识别完毕
    ERROR = auto() # 错误

# "action"
def _char_class(ch: str) -> str:
    """将输入字符分类，用于查询 DFA 状态转换表。"""
    if ch == "\0": # 文件结束标记
        return "EOF"
    if ch in " \t\n\r": # 空格，制表符，换行，回车
        return "BLANK"
    if ch == "{": # 注释开始
        return "LBRACE"
    if ch == "}": # 注释结束
        return "RBRACE"
    if ch.isalpha(): # 标识符/保留字的开头，a-z,A-Z,下划线
        return "LETTER"
    if ch.isdigit(): # 整数常量的开头，0-9
        return "DIGIT"
    if ch == ":": # :=的第一个字符，需要前瞻
        return "COLON"
    if ch == "=": # :=的第二个字符，或者单独的=
        return "EQUAL"
    if ch == ".": # ..的第一个字符，需要前瞻
        return "DOT"
    if ch in "+-*/<()[];," or ch == "'": # 单字符分界符，读到一个就是一个token，无需前瞻
        return "SINGLE_DELIM"
    return "OTHER" # 其他字符，报错


# DFA 状态转换表: {(当前状态, 字符类): 下一状态}
_TRANSITION_TABLE: dict[Tuple[_State, str], _State] = {
    (_State.START, "BLANK"): _State.START, # 空白 -> 继续空闲
    (_State.START, "LBRACE"): _State.INCOMMENT, # { -> 进入注释
    (_State.START, "LETTER"): _State.INID, # 字母 -> 开始读标识符
    (_State.START, "DIGIT"): _State.INNUM, # 数字 -> 开始读整数
    (_State.START, "COLON"): _State.INASSIGN, # : -> 可能是 := ，等等看 
    (_State.START, "DOT"): _State.INUNDERANGE, # . -> 可能是 ..,等等看
    (_State.START, "SINGLE_DELIM"): _State.DONE, # + - * / 等 -> 直接完成
    (_State.START, "EQUAL"): _State.DONE, # = -> 直接完成
    (_State.START, "EOF"): _State.DONE, # 文件结束 -> 完成
    (_State.INID, "LETTER"): _State.INID, # 正在读标识符，又读到字母 -> 继续读
    (_State.INID, "DIGIT"): _State.INID, # 正在读标识符，读到数字 -> 继续读
    (_State.INNUM, "DIGIT"): _State.INNUM, # 正在读数字，又读到数字 -> 继续读
    (_State.INASSIGN, "EQUAL"): _State.DONE, # 读到了 := -> 完成
    (_State.INUNDERANGE, "DOT"): _State.DONE, # 读到了 .. -> 完成
    (_State.INCOMMENT, "RBRACE"): _State.START, # } -> 注释结束，回到空闲
    (_State.INCOMMENT, "EOF"): _State.ERROR, # 文件结束了还没遇到} -> 报错
    # 没写到的组合默认进入ERROR状态
}


class LexicalAnalyzer:
    """词法分析器：输入 SNL 源程序，输出 Token 序列。"""

    def __init__(self, source: str) -> None:
        self._source: str = source
        self._pos: int = 0
        self._line: int = 1
        self._col: int = 1
        self._errors: List[str] = []
        # 括号匹配栈: (左括号字符, line, col)
        self._bracket_stack: List[Tuple[str, int, int]] = []

    # ------------------------------------------------------------------
    # 底层字符操作
    # ------------------------------------------------------------------
    def _current_char(self) -> str:
        return "\0" if self._pos >= len(self._source) else self._source[self._pos]

    def _advance(self) -> str:
        ch: str = self._current_char()
        self._pos += 1
        if ch == "\n":
            self._line += 1
            self._col = 1
        else:
            self._col += 1
        return ch

    # ------------------------------------------------------------------
    # 括号匹配
    # 括号匹配本可以在语法分析阶段做，但放在词法阶段有两个好处：
    # 1. 早报错：源码刚读出来就发现括号错了，不用等到 parser
    # 2. 实验要求：文档明确说"词法分析程序涉及的一些问题：括号匹配"
    # ------------------------------------------------------------------
    def _check_bracket(self, token_type: TokenType, line: int, col: int) -> None:
        left_map: dict[TokenType, str] = {TokenType.LPAREN: "(", TokenType.LMIDPAREN: "["}
        right_map: dict[TokenType, str] = {TokenType.RPAREN: ")", TokenType.RMIDPAREN: "]"}

        if token_type in left_map:
            self._bracket_stack.append((left_map[token_type], line, col))
        elif token_type in right_map:
            if not self._bracket_stack:
                self._errors.append(
                    f"Line {line}, col {col}: 括号不匹配，多余的 '{right_map[token_type]}'")
                return
            top, top_line, top_col = self._bracket_stack.pop()
            expected_right: str = ")" if top == "(" else "]"
            if expected_right != right_map[token_type]:
                self._errors.append(
                    f"Line {line}, col {col}: 括号不匹配，'{top}' (line {top_line}, "
                    f"col {top_col}) 与 '{right_map[token_type]}' 不匹配")

    # ------------------------------------------------------------------
    # 核心：根据 DFA 状态转换表生成单词识别函数
    # ------------------------------------------------------------------
    def get_next_token(self) -> Token:
        state: _State = _State.START
        token_string: str = ""
        start_line: int = self._line
        start_col: int = self._col

        while state not in (_State.DONE, _State.ERROR):
            ch: str = self._current_char()
            char_class: str = _char_class(ch)

            # 注释状态特殊处理（不依赖主转换表的通用回退逻辑）
            if state == _State.INCOMMENT:
                if char_class == "RBRACE":
                    self._advance()
                    state = _State.START
                    start_line, start_col = self._line, self._col
                    token_string = ""
                elif char_class == "EOF":
                    state = _State.ERROR
                else:
                    self._advance()
                continue

            # 初始状态跳过空白
            if state == _State.START and char_class == "BLANK":
                self._advance()
                start_line, start_col = self._line, self._col
                continue

            key: Tuple[_State, str] = (state, char_class)

            if key not in _TRANSITION_TABLE:
                # 无对应转移，按终止状态处理
                if state == _State.INID:
                    state = _State.DONE
                elif state == _State.INNUM:
                    state = _State.DONE
                elif state == _State.INASSIGN:
                    state = _State.ERROR
                elif state == _State.INUNDERANGE:
                    state = _State.DONE
                else:
                    state = _State.ERROR
                continue

            next_state: _State = _TRANSITION_TABLE[key]

            if next_state == _State.DONE:
                if state == _State.INASSIGN and char_class == "EQUAL":
                    self._advance()
                    token_string = ":="
                elif state == _State.INUNDERANGE and char_class == "DOT":
                    self._advance()
                    token_string = ".."
                elif state == _State.START and char_class in ("SINGLE_DELIM", "EQUAL"):
                    token_string = self._advance()
                elif state == _State.START and char_class == "EOF":
                    token_string = "EOF"
                state = _State.DONE
            elif next_state == _State.ERROR:
                state = _State.ERROR
            else:
                if state == _State.START and next_state == _State.INCOMMENT:
                    self._advance()  # 跳过 '{'
                else:
                    token_string += self._advance()
                state = next_state

        # 根据结束状态生成 Token
        if state == _State.ERROR:
            bad: str = self._current_char()
            if bad == "\0":
                bad = "EOF"
            self._errors.append(
                f"Line {start_line}, col {start_col}: 非法字符 '{bad}'")
            self._advance()
            return Token(TokenType.EOF, "EOF", start_line, start_col)

        if token_string == "EOF":
            return Token(TokenType.EOF, "EOF", start_line, start_col)

        if token_string in SINGLE_DELIM_MAP:
            tok = Token(SINGLE_DELIM_MAP[token_string], token_string, start_line, start_col)
            self._check_bracket(tok.token_type, start_line, start_col)
            return tok

        if token_string == ":=":
            return Token(TokenType.ASSIGN, token_string, start_line, start_col)

        if token_string == "..":
            return Token(TokenType.UNDERANGE, token_string, start_line, start_col)

        if token_string.isdigit():
            return Token(TokenType.INTC, token_string, start_line, start_col)

        # 标识符或保留字（保留字是标识符的子集）
        token_type: TokenType = RESERVED_WORDS.get(token_string, TokenType.ID)
        return Token(token_type, token_string, start_line, start_col)

    # ------------------------------------------------------------------
    # 分析入口
    # ------------------------------------------------------------------
    def analyze(self) -> Tuple[List[Token], List[str]]:
        """词法分析主函数。

        返回 (token_list, lexical_errors)。
        """
        tokens: List[Token] = []
        while True:
            token: Token = self.get_next_token()
            tokens.append(token)
            if token.token_type == TokenType.EOF:
                break

        # 文件结束时检查未闭合括号
        while self._bracket_stack:
            top, top_line, top_col = self._bracket_stack.pop()
            self._errors.append(
                f"Line {top_line}, col {top_col}: 未闭合的括号 '{top}'")

        return tokens, self._errors
