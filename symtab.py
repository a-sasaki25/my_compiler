# -*- coding: utf-8 -*-

from enum import Enum

class Scope(Enum):
    ''' Scopeクラス
            記号のタイプを表現
    '''
    GLOBAL_VAR = 0    # 大域変数
    LOCAL_VAR  = 1    # 局所変数
    PROC       = 2    # 手続き
    PARAM      = 3    # 仮引数変数
    FUNC       = 4    # 関数
    ARRAY      = 5    # 配列


class Symbol(object):
    ''' Symbolクラス
            記号（変数，手続き）の情報を表現
    '''

    def __init__(self, name:str, scope:Scope):
        self.name = name     # 名前 : str
        self.scope = scope   # スコープ : Scope
        self.index = None

    def __str__(self):
        return f"({self.name},{self.scope})"

    def __repr__(self):
        return str(self)


class SymbolTable(object):
    ''' SymbolTableクラス
            記号表とその操作関数を定義
    '''

    def __init__(self):
        self.rows = []


    def insert(self, name:str, scope:Scope):
        ''' 記号表への変数・手続きの登録 '''
        print("-- insert --")
        s = Symbol(name, scope)
        self.rows.append(s)
        print(self.rows)


    def lookup(self, name:str) -> Symbol:
        ''' 変数・手続きの検索 '''
        print("-- lookup --")
        for s in reversed(self.rows):
            if (s.name == name):
                print(s)
                return s
        print("nameerror")


    def delete(self):
        ''' 記号表から局所変数の削除 '''
        print("-- delete --")
        new = []
        for s in self.rows:
            if (s.scope != Scope.LOCAL_VAR) and (s.scope != Scope.PARAM):
                new.append(s)
        self.rows = new
        print(self.rows)