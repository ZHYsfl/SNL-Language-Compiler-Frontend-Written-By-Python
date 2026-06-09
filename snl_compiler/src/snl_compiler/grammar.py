"""SNL 上下文无关文法产生式声明。

依据实验逐条整理，作为实现与文档的双重基准。
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class Production:
    """一条产生式：左部非终结符 + 右部符号序列。"""

    lhs: str
    rhs: Tuple[str, ...]


# ---------------------------------------------------------------------
# 文法产生式列表（编号与PPT要求一致，ε 用空元组表示）
# ---------------------------------------------------------------------
SNL_PRODUCTIONS: List[Production] = [
    # 1-11: 程序头、声明部分骨架
    Production("Program", ("ProgramHead", "DeclarePart", "ProgramBody", ".")),
    Production("ProgramHead", ("PROGRAM", "ProgramName")),
    Production("ProgramName", ("ID",)),
    Production("DeclarePart", ("TypeDec", "VarDec", "ProcDec")),
    Production("TypeDec", ()),
    Production("TypeDec", ("TypeDeclaration",)),
    Production("TypeDeclaration", ("TYPE", "TypeDecList")),
    Production("TypeDecList", ("TypeId", "=", "TypeName", ";", "TypeDecMore")),
    Production("TypeDecMore", ()),
    Production("TypeDecMore", ("TypeDecList",)),
    Production("TypeId", ("ID",)),
    # 12-22: 类型系统
    Production("TypeName", ("BaseType",)),
    Production("TypeName", ("StructureType",)),
    Production("TypeName", ("ID",)),
    Production("BaseType", ("INTEGER",)),
    Production("BaseType", ("CHAR",)),
    Production("StructureType", ("ArrayType",)),
    Production("StructureType", ("RecType",)),
    Production("ArrayType", ("ARRAY", "[", "Low", "..", "Top", "]", "OF", "BaseType")),
    Production("Low", ("INTC",)),
    Production("Top", ("INTC",)),
    Production("RecType", ("RECORD", "FieldDecList", "END")),
    Production("FieldDecList", ("BaseType", "IdList", ";", "FieldDecMore")),
    Production("FieldDecList", ("ArrayType", "IdList", ";", "FieldDecMore")),
    Production("FieldDecMore", ()),
    Production("FieldDecMore", ("FieldDecList",)),
    # 27-38: 标识符列表与变量声明
    Production("IdList", ("ID", "IdMore")),
    Production("IdMore", ()),
    Production("IdMore", (",", "IdList")),
    Production("VarDec", ()),
    Production("VarDec", ("VarDeclaration",)),
    Production("VarDeclaration", ("VAR", "VarDecList")),
    Production("VarDecList", ("TypeName", "VarIdList", ";", "VarDecMore")),
    Production("VarDecMore", ()),
    Production("VarDecMore", ("VarDecList",)),
    Production("VarIdList", ("ID", "VarIdMore")),
    Production("VarIdMore", ()),
    Production("VarIdMore", (",", "VarIdList")),
    # 39-54: 过程声明与参数
    Production("ProcDec", ()),
    Production("ProcDec", ("ProcDeclaration",)),
    Production("ProcDeclaration", ("PROCEDURE", "ProcName", "(", "ParamList", ")", ";", "ProcDecPart", "ProcBody", "ProcDecMore")),
    Production("ProcDecMore", ()),
    Production("ProcDecMore", ("ProcDeclaration",)),
    Production("ProcName", ("ID",)),
    Production("ParamList", ()),
    Production("ParamList", ("ParamDecList",)),
    Production("ParamDecList", ("Param", "ParamMore")),
    Production("ParamMore", ()),
    Production("ParamMore", (";", "ParamDecList")),
    Production("Param", ("TypeName", "FormList")),
    Production("Param", ("VAR", "TypeName", "FormList")),
    Production("FormList", ("ID", "FidMore")),
    Production("FidMore", ()),
    Production("FidMore", (",", "FormList")),
    # 55-60: 程序体与语句列表
    Production("ProcDecPart", ("DeclarePart",)),
    Production("ProcBody", ("ProgramBody",)),
    Production("ProgramBody", ("BEGIN", "StmList", "END")),
    Production("StmList", ("Stm", "StmMore")),
    Production("StmMore", ()),
    Production("StmMore", (";", "StmList")),
    # 61-75: 各类语句
    Production("Stm", ("ConditionalStm",)),
    Production("Stm", ("LoopStm",)),
    Production("Stm", ("InputStm",)),
    Production("Stm", ("OutputStm",)),
    Production("Stm", ("ReturnStm",)),
    Production("Stm", ("ID", "AssCall")),
    Production("AssCall", ("AssignmentRest",)),
    Production("AssCall", ("CallStmRest",)),
    Production("AssignmentRest", ("VariMore", ":=", "Exp")),
    Production("ConditionalStm", ("IF", "RelExp", "THEN", "StmList", "ELSE", "StmList", "FI")),
    Production("LoopStm", ("WHILE", "RelExp", "DO", "StmList", "ENDWH")),
    Production("InputStm", ("READ", "(", "Invar", ")")),
    Production("Invar", ("ID",)),
    Production("OutputStm", ("WRITE", "(", "Exp", ")")),
    Production("ReturnStm", ("RETURN", "(", "Exp", ")")),
    # 76-80: 过程调用实参
    Production("CallStmRest", ("(", "ActParamList", ")")),
    Production("ActParamList", ()),
    Production("ActParamList", ("Exp", "ActParamMore")),
    Production("ActParamMore", ()),
    Production("ActParamMore", (",", "ActParamList")),
    # 81-104: 表达式、变量、运算符
    Production("RelExp", ("Exp", "OtherRelE")),
    Production("OtherRelE", ("CmpOp", "Exp")),
    Production("Exp", ("Term", "OtherTerm")),
    Production("OtherTerm", ()),
    Production("OtherTerm", ("AddOp", "Exp")),
    Production("Term", ("Factor", "OtherFactor")),
    Production("OtherFactor", ()),
    Production("OtherFactor", ("MultOp", "Term")),
    Production("Factor", ("(", "Exp", ")")),
    Production("Factor", ("INTC",)),
    Production("Factor", ("Variable",)),
    Production("Variable", ("ID", "VariMore")),
    Production("VariMore", ()),
    Production("VariMore", ("[", "Exp", "]")),
    Production("VariMore", (".", "FieldVar")),
    Production("FieldVar", ("ID", "FieldVarMore")),
    Production("FieldVarMore", ()),
    Production("FieldVarMore", ("[", "Exp", "]")),
    Production("CmpOp", ("<",)),
    Production("CmpOp", ("=",)),
    Production("AddOp", ("+",)),
    Production("AddOp", ("-",)),
    Production("MultOp", ("*",)),
    Production("MultOp", ("/",)),
]


# 非终结符集合（用于调试与校验）
NON_TERMINALS: set[str] = {p.lhs for p in SNL_PRODUCTIONS}
