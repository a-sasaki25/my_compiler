# -*- coding: utf-8 -*-

from enum import Enum
from operand import Operand

##
## 比較演算子の種類
##
class CmpType(Enum):
    EQ  = 0    # eq  (=)
    NE  = 1    # ne  (<>)
    SGT = 2    # sgt (>， 符号付き)
    SGE = 3    # sge (>=，符号付き)
    SLT = 4    # slt (<， 符号付き)
    SLE = 5    # sle (<=，符号付き)

    @classmethod
    def getCmpType(cls, op):
        if   op == '=':		return CmpType.EQ
        elif op == '<>':	return CmpType.NE
        elif op == '>':		return CmpType.SGT
        elif op == '>=':	return CmpType.SGE
        elif op == '<':		return CmpType.SLT
        elif op == '<=':	return CmpType.SLE

    def __str__(self):
        if   self == CmpType.EQ:	return "eq"
        elif self == CmpType.NE:	return "ne"
        elif self == CmpType.SGT:	return "sgt"
        elif self == CmpType.SGE:	return "sge"
        elif self == CmpType.SLT:	return "slt"
        elif self == CmpType.SLE:	return "sle"

##
## ラベル
##
class Labels(object):
    def __init__(self, lab:int):
        super().__init__()
        self.lab = lab
    
    def __str__(self):
        return f"L{self.lab}"


##
## LLVMコード
##
class LLVMCode(object):
    def __init__(self):
        pass


class LLVMCodeGlobal(LLVMCode):
    ''' global 命令
            @{name} = common global i32 0, align 4
    '''

    def __init__(self, name:str):
        super().__init__()
        self.name  = name

    def __str__(self):
        return f"@{self.name} = common global i32 0, align 4"

class LLVMCodeGlobalArray(LLVMCode):
    '''
    global命令(配列)
        @{name} = common global [{size} x i32] zeroinitializer, align 16
    '''
    def __init__(self, name:str, size:int):
        super().__init__()
        self.name  = name
        self.size = size

    def __str__(self):
        return f"@{self.name} = common global [{self.size} x i32] zeroinitializer, align 16"

class LLVMCodeAlloca(LLVMCode):
    ''' alloca命令
            %{name} = alloca i32, align 4    
    '''

    def __init__(self, name:str):
        super().__init__()
        self.name  = name

    def __str__(self):
        return f"%{self.name} = alloca i32, align 4"



class LLVMCodeStore(LLVMCode):
    ''' store 命令
            store i32 {argval}, i32* {ptr}, align 4
    '''
    def __init__(self, val:Operand, ptr:Operand):
        super().__init__()
        self.argval = val
        self.ptr = ptr

    def __str__(self):
        return f"store i32 {self.argval}, i32* {self.ptr}, align 4"


class LLVMCodeLoad(LLVMCode):
    ''' load 命令
            {retval} = load i32, i32* {ptr}, align 4
    '''

    def __init__(self, retval:Operand, ptr:Operand):
        super().__init__()
        self.retval = retval
        self.ptr = ptr

    def __str__(self):
        return f"{self.retval} = load i32, i32* {self.ptr}, align 4"


class LLVMCodeAdd(LLVMCode):
    ''' add 命令
            {retval} = add nsw i32 {arg1}, {arg2}
    '''

    def __init__(self, retval:Operand, arg1:Operand, arg2:Operand):
        super().__init__()
        self.retval = retval
        self.arg1 = arg1
        self.arg2 = arg2

    def __str__(self):
        return f"{self.retval} = add nsw i32 {self.arg1}, {self.arg2}"


class LLVMCodeSub(LLVMCode):
    ''' sub 命令
            {retval} = sub nsw i32 {self.arg1}, {self.arg2}
    '''

    def __init__(self, retval:Operand, arg1:Operand, arg2:Operand):
        super().__init__()
        self.retval = retval
        self.arg1 = arg1
        self.arg2 = arg2

    def __str__(self):
        return f"{self.retval} = sub nsw i32 {self.arg1}, {self.arg2}"


class LLVMCodeMul(LLVMCode):
    ''' mul 命令
            {retval} = mul nsw i32 {arg1}, {arg2}"
    '''

    def __init__(self, retval:Operand, arg1:Operand, arg2:Operand):
        super().__init__()
        self.retval = retval
        self.arg1 = arg1
        self.arg2 = arg2

    def __str__(self):
        return f"{self.retval} = mul nsw i32 {self.arg1}, {self.arg2}"


class LLVMCodeDiv(LLVMCode):
    ''' sdiv 命令
            {retval} = sdiv i32 {arg1}, {arg2}
    '''

    def __init__(self, retval:Operand, arg1:Operand, arg2:Operand):
        super().__init__()
        self.retval = retval
        self.arg1 = arg1
        self.arg2 = arg2

    def __str__(self):
        return f"{self.retval} = sdiv i32 {self.arg1}, {self.arg2}"


class LLVMCodeRet(LLVMCode):
    ''' ret 命令
            ret void
            ret i32 {val}
    '''

    def __init__(self, type:str, val:Operand=None):
        super().__init__()
        self.type = type
        self.val = val

    def __str__(self):
        if self.type == 'i32':
            return f"ret i32 {self.val}"
        else:
            return "ret void"


class LLVMCodeCallPrintf(LLVMCode):
    ''' printf関数呼び出し専用の call命令
            {res} = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.w, i64 0, i64 0), i32 {arg})
    '''

    @classmethod
    def printFormat(cls, fp):
        # printf関数に与える書式文字列
        print(r'@.str.w = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1', file=fp)

    @classmethod
    def printDeclare(cls, fp):
        # printf関数の宣言
        print('declare i32 @printf(i8*, ...)', file=fp)

    def __init__(self, res:Operand, arg:Operand):
        super().__init__()
        self.res = res
        self.arg = arg

    def __str__(self):
        return f"{self.res} = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([4 x i8], [4 x i8]* @.str.w, i64 0, i64 0), i32 {self.arg})"


class LLVMCodeCallScanf(LLVMCode):
    ''' scanf関数呼び出し専用の call命令
             {res} = call i32 (i8*, ...) @scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.str.r, i64 0, i64 0), i32* {arg})
    '''

    @classmethod
    def printFormat(cls, fp):
        # scanf関数に与える書式文字列
        print(r'@.str.r = private unnamed_addr constant [3 x i8] c"%d\00", align 1', file=fp)

    @classmethod
    def printDeclare(cls, fp):
        # scanf関数の宣言
        print('declare i32 @scanf(i8*, ...)', file=fp)

    def __init__(self, res:Operand, arg:Operand):
        super().__init__()
        self.res = res
        self.arg = arg

    def __str__(self):
        return f"{self.res} = call i32 (i8*, ...) @scanf(i8* getelementptr inbounds ([3 x i8], [3 x i8]* @.str.r, i64 0, i64 0), i32* {self.arg})"



class LLVMCodeJ(LLVMCode):
    ''' br命令 （無条件ジャンプ）
            br label {arg1}
    '''
    def __init__(self, arg1:Labels):
        super().__init__()
        self.arg1 = arg1

    def __str__(self):
        return f"br label %{self.arg1}"


class LLVMCodeBr(LLVMCode):
    ''' br命令（分岐命令） 
            br i1 {cond}, label {arg1}, label {arg2}
    '''
    def __init__(self, cond:Operand, arg1:Labels, arg2:Labels):
        super().__init__()
        self.cond = cond
        self.arg1 = arg1
        self.arg2 = arg2

    def __str__(self):
        return f"br i1 {self.cond}, label %{self.arg1}, label %{self.arg2}"


class LLVMCodeLabel(LLVMCode):
    ''' ラベル付け
            {arg1}:
    '''
    def __init__(self, arg1:Labels):
        super().__init__()
        self.arg1 = arg1

    def __str__(self):
        return f"{self.arg1}:"



class LLVMCodeIcmp(LLVMCode):
    ''' icmp
            {retval} = icmp {cond} i32 {arg1}, {arg2}
    '''

    def __init__(self, retval:Operand, cond:CmpType, arg1:Operand, arg2:Operand):
        super().__init__()
        self.retval = retval
        self.cond = cond
        self.arg1 = arg1
        self.arg2 = arg2

    def __str__(self):
        return f"{self.retval} = icmp {self.cond} i32 {self.arg1}, {self.arg2}"


class LLVMCodeCallVoid(LLVMCode):
    ''' call命令(void)
            call void f([i32 v]*)
    '''

    def __init__(self, name:Operand):
        super().__init__()
        self.name = name
        self.arg = []

    def __str__(self):
        r = f"call void @{self.name}("
        new = ""
        for l in self.arg:
            new = new + f"i32 {l}, "
        r = r + new[:-2] +")"
        return r

class LLVMCodeCall(LLVMCode):
    ''' call命令
        {retval} = call i32 f([i32 v]*)
    '''

    def __init__(self, name:Operand):
        super().__init__()
        self.retval = None
        self.name = name
        self.arg = []

    def __str__(self):
        r = f"{self.retval} = call i32 @{self.name}("
        new = ""
        for l in self.arg:
            new = new + f"i32 {l}, "
        r = r + new[:-2] + ")"
        return r


class LLVMCodeSext(LLVMCode):
    '''
    sext命令
    {retval} = sext to i32 {v} to i64
    '''
    def __init__(self, retval:Operand, v:Operand):
        super().__init__()
        self.retval  = retval
        self.v = v

    def __str__(self):
        return f"{self.retval} = sext i32 {self.v} to i64"


class LLVMCodeGetelementptr(LLVMCode):
    '''
    getelementptr命令
    {retval} = getelementptr inbounds [{size} x i32], [{size} x i32]* @{name}, i32 0, i64 {ptr}
    '''
    def __init__(self, retval:Operand, size:str, name:str, ptr:Operand):
        super().__init__()
        self.retval  = retval
        self.size = size
        self.name = name
        self.ptr = ptr

    def __str__(self):
        return f"{self.retval} = getelementptr inbounds [{self.size} x i32], [{self.size} x i32]* @{self.name}, i64 0, i64 {self.ptr}"


class LLVMCodeShl(LLVMCode):
    '''
    shl命令
    {retval} = shl i32 {arg1}, {arg2}
    '''
    def __init__(self, retval:Operand, arg1:Operand, arg2:Operand):
        super().__init__()
        self.retval  = retval
        self.arg1 = arg1
        self.arg2 = arg2

    def __str__(self):
        return f"{self.retval} = shl i32 {self.arg1}, {self.arg2}"


class LLVMCodeAshr(LLVMCode):
    '''
    ashr命令
    {retval} = ashr i32 {arg1}, {arg2}
    '''
    def __init__(self, retval:Operand, arg1:Operand, arg2:Operand):
        super().__init__()
        self.retval  = retval
        self.arg1 = arg1
        self.arg2 = arg2

    def __str__(self):
        return f"{self.retval} = ashr i32 {self.arg1}, {self.arg2}"