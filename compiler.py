#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import ply.lex as lex
import ply.yacc as yacc

import math

from symtab import Scope, Symbol, SymbolTable
from fundef import Fundef
from llvmcode import *
from operand import OType, Operand

## トークン名のリスト
tokens = (
    'BEGIN', 'DIV', 'DO', 'ELSE', 'END', 'FOR', 'FUNCTION', 'IF',
    'PROCEDURE', 'PROGRAM', 'READ', 'THEN', 'TO', 'VAR', 'WHILE', 'WRITE',
    'PLUS', 'MINUS', 'MULT', 'EQ', 'NEQ', 'LT', 'LE', 'GT', 'GE',
    'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET', 'COMMA', 'SEMICOLON',
    'PERIOD', 'INTERVAL', 'ASSIGN',
    'IDENT', 'NUMBER'
)

## 予約語の定義
reserved = {
    'begin': 'BEGIN',
    'div': 'DIV',
    'do': 'DO',
    'else': 'ELSE',
    'end': 'END',
    'for': 'FOR',
    'function': 'FUNCTION',
    'if': 'IF',
    'procedure': 'PROCEDURE',
    'program': 'PROGRAM',
    'read': 'READ',
    'then': 'THEN',
    'to': 'TO',
    'var': 'VAR',
    'while': 'WHILE',
    'write': 'WRITE'
}

## 基本シンボルトークンを切り出すルール
t_PLUS  = '\+'
t_MINUS = '-'
t_MULT  = '\*'
t_EQ = '='
t_NEQ = '<>'
t_LT = '<'
t_LE = '<='
t_GT = '>'
t_GE = '>='
t_LPAREN = '\('
t_RPAREN = '\)'
t_LBRACKET = '\['
t_RBRACKET = '\]'
t_COMMA = ','
t_SEMICOLON = ';'
t_PERIOD = '\.'
t_INTERVAL = '\.\.'
t_ASSIGN = ':='

# コメントおよび空白・タブを無視するルール
t_ignore_COMMENT = '\#.*'
t_ignore = ' \t'

## アクションを伴うトークンルール
# 変数名・手続き名などの識別子を切り出すルール
def t_IDENT(t):
    '[a-zA-Z][a-zA-Z0-9]*'
    t.type = reserved.get(t.value, 'IDENT')
    return t

# 数値を切り出すルール
def t_NUMBER(t):
    '[1-9][0-9]*|0'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Line %d: integer value %s is too large" % t.lineno, t.value)
        t.value = 0
    return t

# 改行を読んだときの処理
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# エラー処理
def t_error(t):
    print("不正な文字「", t.value[0], "」")
    t.lexer.skip(1)


#################################################################
# 解析に必要な変数を宣言しておく
#################################################################

symtable = SymbolTable()
varscope = Scope.GLOBAL_VAR

fundefs = []				# 生成した関数定義（Fundef）のリスト

useWrite = False			# write関数が使用されているかのフラグ
useRead  = False			# read関数が使用されているかのフラグ

def addCode(l:LLVMCode):
    ''' 現在の関数定義オブジェクトの codes に命令 l を追加 '''
    fundefs[-1].codes.append(l)

def getRegister():
    ''' 新たなレジスタ番号をもつ Operand オブジェクトを返す '''
    return Operand(OType.NUMBERED_REG, val=fundefs[-1].getNewRegNo())

def getLabel():
    return Labels(fundefs[-1].getNewLab())

def addParam(l):
    fundefs[-1].params.append(l)

#################################################################
# ここから先に構文規則を書く
#################################################################

def p_program(p):
    '''
    program : PROGRAM IDENT SEMICOLON outblock PERIOD
    '''
    with open("result.ll", "w") as fout:
        # 大域変数ごとに common global 命令を出力
        for t in symtable.rows:
            if t.scope == Scope.GLOBAL_VAR:
                print(LLVMCodeGlobal(t.name), file=fout)
            elif t.scope == Scope.ARRAY:
                size = t.index[1] - t.index[0] + 1
                print(LLVMCodeGlobalArray(t.name, size), file=fout)
        print('', file=fout)

        # 関数定義を出力
        for f in fundefs:
            f.print(fout)

        # printfやscanf関数の宣言と書式を表す文字列定義を出力
        if useWrite:
            LLVMCodeCallPrintf.printDeclare(fout)
            LLVMCodeCallPrintf.printFormat(fout)
        if useRead:
            LLVMCodeCallScanf.printDeclare(fout)
            LLVMCodeCallScanf.printFormat(fout)


def p_outblock(p):
    '''
    outblock :  var_decl_part subprog_decl_part outblock_act statement
    '''
    # 規則の右辺に outblock_act が追加されていることに注意!!

    # 還元時に「ret i32 0」命令を追加
    addCode(LLVMCodeRet('i32', Operand(OType.CONSTANT, val=0)))


def p_outblock_act(p):
    '''
    outblock_act :
    '''
    # メイン処理に対する関数定義オブジェクトを生成(名前は main とする）
    fundefs.append(Fundef('main', 'i32'))


def p_var_decl_part(p):
    '''
    var_decl_part : var_decl_list SEMICOLON
                  |
    '''


def p_var_decl_list(p):
    '''
    var_decl_list : var_decl_list SEMICOLON var_decl 
                  | var_decl
    '''

def p_var_decl(p):
    '''
    var_decl : VAR id_list
    '''


def p_subprog_decl_part(p):
    '''
    subprog_decl_part : subprog_decl_list SEMICOLON
                      |
    '''

def p_subprog_decl_list(p): 
    '''
    subprog_decl_list : subprog_decl_list SEMICOLON subprog_decl
                  | subprog_decl
    '''

def p_subprog_decl(p):
    '''
    subprog_decl : proc_decl
                 | func_decl
    '''


def p_proc_decl(p):
    '''
    proc_decl : PROCEDURE proc_name LPAREN RPAREN SEMICOLON inblock
              | PROCEDURE proc_name LPAREN proc_decl_act1 id_list RPAREN SEMICOLON inblock
    '''
    addCode(LLVMCodeRet('void'))
    symtable.delete()

def p_proc_decl_act1(p):
    '''
    proc_decl_act1 : 
    '''
    global varscope
    varscope = Scope.PARAM

def p_proc_name(p):
    '''
    proc_name : IDENT
    '''
    x = p[1]
    symtable.insert(x, Scope.PROC)

    fundefs.append(Fundef(x, 'void'))

def p_inblock(p):
    '''
    inblock : inblock_act1 var_decl_part inblock_act2 statement
    '''

    
def p_inblock_act1(p):
    '''
    inblock_act1 : 
    '''
    global varscope 
    varscope = Scope.LOCAL_VAR

def p_inblock_act2(p):
    '''
    inblock_act2 : 
    '''
    for t in symtable.rows:
        if t.scope == Scope.LOCAL_VAR:
            addCode(LLVMCodeAlloca(t.name))

def p_func_decl(p):
    '''
    func_decl : FUNCTION func_name LPAREN RPAREN SEMICOLON func_inblock
              | FUNCTION func_name LPAREN func_decl_act1 id_list RPAREN SEMICOLON func_inblock
    '''
    if len(p) == 7:
        arg = p[6]
    else:
        arg = p[8]

    addCode(LLVMCodeRet('i32', val = arg))
    symtable.delete()

def p_func_decl_act1(p):
    '''
    func_decl_act1 : 
    '''
    global varscope
    varscope = Scope.PARAM

def p_func_name(p):
    '''
    func_name : IDENT
    '''
    x = p[1]
    symtable.insert(x, Scope.FUNC)

    fundefs.append(Fundef(x, 'i32'))

def p_func_inblock(p):
    '''
    func_inblock : func_inblock_act1 var_decl_part func_inblock_act2 statement
    '''
    retval = getRegister()
    ptr = Operand(OType.NAMED_REG, name = fundefs[-1].name) 
    addCode(LLVMCodeLoad(retval, ptr))
    p[0] = retval

def p_func_inblock_act1(p):
    '''
    func_inblock_act1 : 
    '''
    global varscope 
    varscope = Scope.LOCAL_VAR

def p_func_inblock_act2(p):
    '''
    func_inblock_act2 : 
    '''
    for t in symtable.rows:
        if t.scope == Scope.LOCAL_VAR:
            addCode(LLVMCodeAlloca(t.name))

    x = fundefs[-1].name
    addCode(LLVMCodeAlloca(x))

def p_statement_list(p):
    '''
    statement_list : statement_list SEMICOLON statement
                   | statement
    '''


def p_statement(p):
    '''
    statement : assignment_statement
                  | if_statement
                  | while_statement
                  | for_statement
                  | proc_call_statement
                  | null_statement
                  | block_statement
                  | read_statement
                  | write_statement
                  | func_call_statement
    '''


def p_assignment_statement(p):
    '''
    assignment_statement : IDENT ASSIGN expression
                         | IDENT LBRACKET expression RBRACKET ASSIGN expression
    '''
    t = symtable.lookup(p[1])
    sval = p[3]
    if t.scope == Scope.GLOBAL_VAR:
        ptr = Operand(OType.GLOBAL_VAR, name=t.name)
    elif t.scope == Scope.LOCAL_VAR:
        ptr = Operand(OType.NAMED_REG, name = t.name)
    elif t.scope == Scope.PARAM:
        ptr = Operand(OType.NAMED_REG, name = t.name)
    elif t.scope == Scope.FUNC:
        ptr = Operand(OType.NAMED_REG, name = t.name)
    elif t.scope == Scope.ARRAY:
        arg1 = p[3]
        retval = getRegister()
        arg2 = t.index[0]
        addCode(LLVMCodeSub(retval, arg1, arg2))
        v = retval

        retval = getRegister()
        addCode(LLVMCodeSext(retval, v))
        ptr = retval

        retval = getRegister()
        size = t.index[1] - t.index[0] + 1
        name = t.name
        addCode(LLVMCodeGetelementptr(retval, size, name, ptr))
        ptr = retval
        sval = p[6]
    addCode(LLVMCodeStore(sval, ptr))


def p_if_statement(p):
    '''
    if_statement : IF condition if_act1 THEN statement else_statement
    '''

def p_if_act1(p):
    '''
    if_act1 : 
    '''
    cond = p[-1]
    arg1 = getLabel()
    arg2 = getLabel()
    addCode(LLVMCodeBr(cond, arg1, arg2))
    p[0] = arg2
    addCode(LLVMCodeLabel(arg1))  

def p_else_statement(p):
    '''
    else_statement : ELSE else_act1 statement
                  |
    '''
    if (len(p) == 4):
        arg1 = p[2]
        addCode(LLVMCodeJ(arg1))
        addCode(LLVMCodeLabel(arg1))
    else:
        arg1 = p[-3]
        addCode(LLVMCodeJ(arg1))
        addCode(LLVMCodeLabel(arg1))

def p_else_act1(p):
    '''
    else_act1 : 
    '''
    arg1 = getLabel()
    addCode(LLVMCodeJ(arg1))
    p[0] = arg1

    arg2 = p[-4]
    addCode(LLVMCodeLabel(arg2))

def p_while_statement(p):
    '''
    while_statement : WHILE while_act1 condition while_act2 DO statement 
    '''
    arg1 = p[2]
    addCode(LLVMCodeJ(arg1))
    arg2 = p[4]
    addCode(LLVMCodeLabel(arg2))

def p_while_act1(p):
    '''
    while_act1 : 
    '''
    arg1 = getLabel()
    addCode(LLVMCodeJ(arg1))
    addCode(LLVMCodeLabel(arg1))
    p[0] = arg1

def p_while_act2(p):
    '''
    while_act2 : 
    '''
    arg1 = getLabel()
    arg2 = getLabel()
    cond = p[-1]
    addCode(LLVMCodeBr(cond, arg1, arg2))
    addCode(LLVMCodeLabel(arg1))
    p[0] = arg2


def p_for_statement(p):
    '''
    for_statement : FOR IDENT ASSIGN expression TO expression for_act1 DO statement
    '''
    
    arg1 = p[7][2]
    retval1 = getRegister()
    addCode(LLVMCodeLoad(retval1, arg1))
    
    arg2 = retval1
    arg3 = Operand(OType.CONSTANT, val = 1)
    retval2 = getRegister()
    addCode(LLVMCodeAdd(retval2, arg2, arg3))

    ptr = p[7][2]
    addCode(LLVMCodeStore(retval2, ptr))

    arg4 = p[7][0]
    arg5 = p[7][1]
    addCode(LLVMCodeJ(arg4))
    addCode(LLVMCodeLabel(arg5))

def p_for_act1(p):
    '''
    for_act1 : 
    '''
    t = symtable.lookup(p[-5])
    if t.scope == Scope.GLOBAL_VAR:
        ptr = Operand(OType.GLOBAL_VAR, name=t.name)
    elif t.scope == Scope.LOCAL_VAR:
        ptr = Operand(OType.NAMED_REG, name = t.name)

    arg1 = p[-3]
    addCode(LLVMCodeStore(arg1, ptr))

    arg2 = getLabel()
    addCode(LLVMCodeJ(arg2))
    addCode(LLVMCodeLabel(arg2))

    retval1 = getRegister()
    addCode(LLVMCodeLoad(retval1, ptr))
    arg3 = retval1
    arg4 = p[-1]
    cond = CmpType.SLE
    retval2 = getRegister()
    addCode(LLVMCodeIcmp(retval2, cond, arg3, arg4))
    
    arg5 = getLabel()
    arg6 = getLabel()
    addCode(LLVMCodeBr(retval2, arg5, arg6))
    
    addCode(LLVMCodeLabel(arg5))
    
    p[0] = [arg2, arg6, ptr]

def p_proc_call_statement(p):
    '''
    proc_call_statement : proc_call_name LPAREN RPAREN
                        | proc_call_name LPAREN proc_call_statement_act1 arg_list RPAREN
    '''
    if len(p) == 4:
        addCode(LLVMCodeCallVoid(p[1]))
    else:
        addCode(p[3])


def p_proc_call_statement_act1(p):
    '''
    proc_call_statement_act1 : 
    '''
    p[0] = LLVMCodeCallVoid(p[-2])


def p_func_call_statement(p):
    '''
    func_call_statement : func_call_name LPAREN RPAREN
                        | func_call_name LPAREN func_call_statement_act1 arg_list RPAREN
    '''
    retval = getRegister()
    if len(p) == 4:
        x = LLVMCodeCall(p[1])
    else:
        x = p[3]
    x.retval = retval
    addCode(x)
    p[0] = x.retval

def p_func_call_statement_act1(p):
    '''
    func_call_statement_act1 : 
    '''
    p[0] = LLVMCodeCall(p[-2])


def p_arg_list(p):
    '''
    arg_list : expression
             | arg_list COMMA expression
    '''
    if len(p) == 2:
        arg = p[1]
    else:
        arg = p[3]
    p[-1].arg.append(arg)
    


def p_proc_call_name(p):
    '''
    proc_call_name : IDENT
    '''
    x = p[1]
    symtable.lookup(x)

    p[0] = p[1]

def p_func_call_name(p):
    '''
    func_call_name : IDENT
    '''
    x = p[1]
    symtable.lookup(x)

    p[0] = p[1]

def p_block_statement(p):
    '''
    block_statement : BEGIN statement_list END
    '''


def p_read_statement(p):
    '''
    read_statement : READ LPAREN IDENT RPAREN
                   | READ LPAREN IDENT LBRACKET expression RBRACKET RPAREN
    '''
    global useRead
    useRead = True

    t = symtable.lookup(p[3])
    if t.scope == Scope.GLOBAL_VAR:
        ptr = Operand(OType.GLOBAL_VAR, name=t.name)
    elif t.scope == Scope.LOCAL_VAR:
        ptr = Operand(OType.NAMED_REG, name = t.name)
    elif t.scope == Scope.PARAM:
        ptr = Operand(OType.NAMED_REG, name = t.name)
    elif t.scope == Scope.ARRAY:
        
        arg1 = p[5]

        retval = getRegister()
        arg2 = t.index[0]
        addCode(LLVMCodeSub(retval, arg1, arg2))
        v = retval

        retval = getRegister()
        addCode(LLVMCodeSext(retval, v))
        ptr = retval

        retval = getRegister()
        size = t.index[1] - t.index[0] + 1
        name = t.name
        addCode(LLVMCodeGetelementptr(retval, size, name, ptr))
        ptr = retval

    addCode(LLVMCodeCallScanf(getRegister(), ptr))


def p_write_statement(p):
    '''
    write_statement : WRITE LPAREN expression RPAREN
    '''
    global useWrite
    useWrite = True
    arg = p[3]
    addCode(LLVMCodeCallPrintf(getRegister(), arg))


def p_null_statement(p):
    '''
    null_statement : 
    '''

def p_condition(p):
    '''
    condition : expression EQ expression
              | expression NEQ expression
              | expression LT expression
              | expression LE expression
              | expression GT expression
              | expression GE expression
    '''
    arg1 = p[1]
    arg2 = p[3]
    cond = CmpType.getCmpType(p[2])
    retval = getRegister()
    addCode(LLVMCodeIcmp(retval, cond, arg1, arg2))
    p[0] = retval


def p_expression(p):
    '''
    expression : term
               | MINUS term
               | expression PLUS term
               | expression MINUS term
               | func_call_statement
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        arg1 = Operand(OType.CONSTANT, val=0)
        arg2 = p[2]
        retval = getRegister()
        addCode(LLVMCodeSub(retval, arg1, arg2))
        p[0] = retval
    else:
        arg1 = p[1]
        arg2 = p[3]
        retval = getRegister()
        if (p[2] == "+"):
            addCode(LLVMCodeAdd(retval, arg1, arg2))
        else:
            addCode(LLVMCodeSub(retval, arg1, arg2))
        p[0] = retval


def p_term(p):
    '''
    term : factor
         | term MULT factor
         | term DIV factor
         | func_call_statement
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        arg1 = p[1]
        arg2 = p[3]
        retval = getRegister()
        if p[2] == "*":
            if (arg1.type == OType.CONSTANT):
                x = arg1.val
                if (x & (x-1)) == 0:
                    arg1 = Operand(OType.CONSTANT, val=int(math.log2(x)))
                    addCode(LLVMCodeShl(retval, arg2, arg1))
                else:
                    addCode(LLVMCodeMul(retval, arg1, arg2))
            elif (arg2.type == OType.CONSTANT):
                x = arg2.val
                if (x & (x-1)) == 0:
                    arg2 = Operand(OType.CONSTANT, val=int(math.log2(x)))
                    addCode(LLVMCodeShl(retval, arg1, arg2))
                else:
                    addCode(LLVMCodeMul(retval, arg1, arg2))
            else:
                addCode(LLVMCodeMul(retval, arg1, arg2))
        else:
            if (arg2.type == OType.CONSTANT):
                x = arg2.val
                if (x & (x-1)) == 0:
                    arg2 = Operand(OType.CONSTANT, val=int(math.log2(x)))
                    addCode(LLVMCodeAshr(retval, arg1, arg2))
                else:
                    addCode(LLVMCodeDiv(retval, arg1, arg2))    
            else:
                addCode(LLVMCodeDiv(retval, arg1, arg2))
        p[0] = retval

def p_factor(p):
    '''
    factor : var_name
           | number
           | LPAREN expression RPAREN
           | func_call_statement
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]

def p_var_name(p):
    '''
    var_name : IDENT
             | IDENT LBRACKET expression RBRACKET
    '''

    t = symtable.lookup(p[1])
    if t.scope == Scope.GLOBAL_VAR:
        ptr = Operand(OType.GLOBAL_VAR, name=t.name)
        retval = getRegister()
        addCode(LLVMCodeLoad(retval, ptr))

    elif t.scope == Scope.LOCAL_VAR:
        ptr = Operand(OType.NAMED_REG, name = t.name)
        retval = getRegister()
        addCode(LLVMCodeLoad(retval, ptr))

    elif t.scope == Scope.PARAM:
        retval = Operand(OType.NAMED_REG, name = t.name)

    elif t.scope == Scope.ARRAY:
        arg1 = p[3]
        retval = getRegister()
        arg2 = t.index[0]
        addCode(LLVMCodeSub(retval, arg1, arg2))
        v = retval

        retval = getRegister()
        addCode(LLVMCodeSext(retval, v))
        ptr = retval

        retval = getRegister()
        size = t.index[1] - t.index[0] + 1
        name = t.name
        addCode(LLVMCodeGetelementptr(retval, size, name, ptr))
        ptr = retval

        retval = getRegister()
        addCode(LLVMCodeLoad(retval, ptr))
    p[0] = retval    
    

def p_number(p):
    '''
    number : NUMBER
    '''

    p[0] = Operand(OType.CONSTANT, val=int(p[1]))


def p_id_list(p):
    '''
    id_list : IDENT 
            | id_list COMMA IDENT  
            | id_list COMMA IDENT LBRACKET NUMBER INTERVAL NUMBER RBRACKET
            | IDENT LBRACKET NUMBER INTERVAL NUMBER RBRACKET COMMA id_list id_list_act1
    '''
    if len(p) == 2: #左辺を含めて長さが2のとき
        x = p[1]    #右辺において1番目であるIDENTトークンを取得
        symtable.insert(x, varscope)
    elif len(p) == 4:
        x = p[3]
        symtable.insert(x, varscope)
    elif len(p) == 9:
        x = p[3]
        symtable.insert(x, Scope.ARRAY)
        symtable.rows[-1].index = (p[5], p[7])
    elif len(p) == 10:
        x = p[1]
        symtable.insert(x, Scope.ARRAY)
        symtable.rows[-1].index = (p[3], p[5])
        
    if (varscope == Scope.PARAM):
        l = Operand(OType.NAMED_REG, name = x)
        addParam(l)
    
def p_id_list_act1(p):
    '''
    id_list_act1 : 
    '''

#################################################################
# 構文解析エラー時の処理
#################################################################

def p_error(p):
    if p:
        # p.type, p.value, p.linenoを使ってエラーの処理を書く
        print("ERROR")
        print("Token Type: " + p.type)
        print("Token Value: " + p.value)
        print("Line: " + str(p.lineno))
    else:
        print("Syntax error at EOF")

#################################################################
# メインの処理
#################################################################

if __name__ == "__main__":
    lexer = lex.lex(debug=0)  # 字句解析器
    yacc.yacc()  # 構文解析器

    # ファイルを開いて
    data = open(sys.argv[1]).read()
    # 解析を実行
    yacc.parse(data, lexer=lexer)
