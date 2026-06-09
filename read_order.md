按数据流顺序看最顺，也就是跟着编译器前端的真实执行路径走：

---

第一层：数据结构（所有模块的基石）

1. tokens.py — 单词分类定义。先搞清楚 SNL 有哪些 Token（保留字、ID、INTC、分界符等），后面词法/语法/语义都围着它转。
2. syntax_tree.py — 语法树节点。就两行代码，但它是 parser 和 semantic 之间的桥梁。
3. types.py — 类型内部表示（integer / char / array / record）。语义分析的核心就是操作这些类型对象。

---

第二层：词法分析（源码 → Token 序列）

1. lexer.py — 词法分析器。重点看 _State 枚举（8 个 DFA 状态）和主循环如何根据当前状态+字符类查转换表，以及 :=、..、注释 {} 的向前扫描逻辑。

---

第三层：语法分析（Token → 语法树）

1. grammar.py — 104 条文法产生式。不用精读，但要对 SNL 的语法结构有整体印象（程序头 → 声明 → 程序体）。
2. rd_parser/base.py — 解析器基础设施。_match、_check、_current、_peek 这四个方法是核心。
3. rd_parser/program.py — 程序骨架（Program / ProgramHead / DeclarePart / ProgramBody）。
4. rd_parser/declarations.py — 声明部分。类型声明、变量声明、过程声明、参数列表都在这，是文法最复杂的区域。
5. rd_parser/statements.py — 语句部分。If / While / Read / Write / Assign / Call。
6. rd_parser/expressions.py — 表达式部分。Exp → Term → Factor 的优先级递归。

---

第四层：语义分析（语法树 → 符号表 + 类型检查）

1. symbol_table.py — 栈式作用域符号表。理解 create_scope / destroy_scope / enter / find 四个操作，这是过程嵌套和作用域查找的基础。
2. semantic_base.py — 公共辅助。_token、_child、_child_by_name、_error 四个树遍历工具。
3. semantic_core.py — 类型/变量声明的语义检查。重点看 _type_def 如何递归解析类型，以及 _array_type 的下标合法性检查。
4. semantic_proc.py — 过程声明与参数检查。重点看 _param 如何处理值参/变参，以及如何把参数挂到过程条目上。
5. semantic_expr.py — 表达式类型推导。_exp / _term / _factor 的递归推导，以及 _variable 处理数组下标和记录域访问。
6. semantic_stmt.py — 语句类型检查。赋值兼容性、过程调用参数个数/类型匹配、If/While 的条件表达式检查。
7. semantic_analyzer.py — 主入口。看 analyze() 如何按顺序调用 core → proc → stmt，以及符号表/类型表的格式化输出。

---

第五层：串联与接口

1. pipeline.py — 三阶段流水线。一句话：lexer.analyze() → parser.parse() → semantic.analyze()。
2. cli.py — 命令行接口。看 --tokens / --parse / --semantic 三个输出分支。
3. **main**.py — 可执行入口。就两行，但让 python -m snl_compiler 能跑起来。

---

推荐的精读路线（如果时间紧）

最小闭环（30 分钟就能跑通整条链）：
tokens.py → lexer.py → rd_parser/base.py → rd_parser/program.py
→ pipeline.py → cli.py

完整闭环（建议按这个顺序逐层深入）：
tokens.py → syntax_tree.py → types.py
→ lexer.py
→ grammar.py → rd_parser/*.py
→ symbol_table.py → semantic_base.py → semantic_core.py → semantic_proc.py
→ semantic_expr.py → semantic_stmt.py → semantic_analyzer.py
→ pipeline.py → cli.py

每看完一层就跑到 tests/ 里看对应测试（test_lexer.py → test_parser.py → test_semantic.py），代码和测试对照着看，理解会深很多。