# 2023级《编译原理》实验 — SNL 编译器前端

## 小组成员

| 学号 | 姓名 | 角色 | 作用占比 |
|---|---|---|---|
| 55230121 | 周浩洋 | 组长 | 40% |
| 55230128 | 齐昊 | 组员 | 30% |
| 55230111 | 李沂朋 | 组员 | 30% |

## 实验内容

完成对 SNL（Small Nested Language）教学模型语言的编译器前端三阶段分析：

1. **词法分析程序** — 输入 SNL 源程序，输出 Token 序列
2. **语法分析程序** — 输入 Token 序列，采用递归下降法输出语法树与语法错误信息
3. **语义分析程序** — 输入语法树，输出符号表、类型表及语义错误信息

## 快速开始

### 环境要求
- Python >= 3.12
- [uv](https://docs.astral.sh/uv/)（推荐）或 pip

### 安装依赖
```bash
uv sync
```

### 运行测试
```bash
uv run pytest --cov=snl_compiler
```
当前测试覆盖率：**> 95%**（195 个测试用例全部通过）。

### 执行编译器
```bash
# 完整三阶段分析
uv run python -m snl_compiler tests/fixtures/normal/correct_basic.snl --semantic

# 仅词法分析
uv run python -m snl_compiler tests/fixtures/normal/correct_basic.snl --tokens

# 词法 + 语法分析
uv run python -m snl_compiler tests/fixtures/normal/correct_basic.snl --parse
```

运行后会自动在同目录生成以下 `.txt` 产物：

| 产物文件 | 说明 | 触发条件 |
|---|---|---|
| `xxx_tokens.txt` | Token 序列 | 始终生成 |
| `xxx_词法错误.txt` | 词法错误列表 | 始终生成（无错则写"未发现词法错误"） |
| `xxx_语法错误.txt` | 语法错误列表 | **词法无错**时生成 |
| `xxx_语法树.txt` | 语法树文本 | **词法无错**时生成 |
| `xxx_符号表.txt` | 类型表 + 符号表 | **词法+语法均无错**时生成 |
| `xxx_语义错误.txt` | 语义错误列表 | **词法+语法均无错**时生成 |

## 项目结构

```
src/snl_compiler/
├── tokens.py              # Token 定义与保留字表
├── lexer.py               # 词法分析器（DFA 状态转换表）
├── rd_parser/             # 递归下降语法分析器（按职责拆分为 Mixin）
│   ├── base.py            # Token 索引、匹配、前瞻基础能力
│   ├── program.py         # 程序结构（ProgramHead / DeclarePart / ProgramBody）
│   ├── declarations.py    # 声明部分（类型、变量、过程、参数、记录域）
│   ├── statements.py      # 语句部分（If / While / Read / Write / Assign / Call）
│   └── expressions.py     # 表达式部分（Exp / Term / Factor / Variable）
├── syntax_tree.py         # 语法树节点定义
├── grammar.py             # SNL 文法产生式（104 条）
├── semantic_base.py       # 语义分析公共辅助（树遍历、错误收集）
├── semantic_core.py       # 声明语义分析（类型表、变量偏移计算）
├── semantic_proc.py       # 过程声明语义分析（参数、作用域嵌套）
├── semantic_expr.py       # 表达式语义分析（类型推导、数组/记录访问检查）
├── semantic_stmt.py       # 语句语义分析（赋值兼容、过程调用参数匹配）
├── semantic_analyzer.py   # 语义分析主入口与格式化输出
├── symbol_table.py        # 栈式作用域符号表
├── types.py               # 类型内部表示（基本类型、数组、记录）
├── pipeline.py            # 三阶段流水线串联
└── cli.py                 # 命令行接口

tests/fixtures/            # 测试示例程序（按类别分子文件夹）
├── normal/                # 正常程序（无语义错误）
├── lexical_errors/        # 词法错误示例（每个文件一种错误）
├── syntax_errors/         # 语法错误示例（每个文件一种错误）
└── semantic_errors/       # 语义错误示例
```

## 设计思想

### 词法分析
采用 **DFA 状态转换表** 实现。将输入字符分类为 LETTER、DIGIT、BLANK、LBRACE 等，通过 `_State` 枚举定义 START、INID、INNUM、INASSIGN、INUNDERANGE、INCOMMENT、DONE、ERROR 八个状态。对于 `:=` 和 `..` 进行向前扫描，注释 `{...}` 及括号匹配均在词法阶段处理。

### 语法分析
采用 **递归下降法**，严格依据图片中的 104 条文法产生式实现。每个非终结符对应一个分析子程序，通过 `RecursiveDescentParser` 组合 `ParserBase` 与四个职责单一的 Mixin（Program / Declarations / Statements / Expressions），确保每个文件不超过 250 行，职责高度内聚。

### 语义分析
- **符号表**：栈式作用域结构，支持过程嵌套定义与递归调用。`SymbolEntry` 包含标识符名、类型、种类、访问方式、层级、偏移量。
- **类型表**：`TypeIR` 支持基本类型（integer / char）、数组类型（含下标范围与元素类型）、记录类型（域链结构）。
- **类型检查**：赋值兼容性、算术运算分量类型相容、数组下标整数检查、记录域存在性检查、过程调用形实参个数与类型匹配。

## 工程约束

本项目在开发过程中严格遵守以下工程观：
- **文件体积**：每个源文件 ≤ 250 行，通过职责拆分倒逼设计解耦。
- **测试驱动**：pytest + pytest-cov，覆盖率 > 95%。
- **开闭原则**：Parser 与 Semantic 模块均通过组合/继承方式扩展，不对已有验证代码做侵入式修改。
