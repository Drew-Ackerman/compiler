import enum
import Scanner
import Array

class Symbol(object):
    def __init__(self, name, value, token_type, symbol_type, size=1):
        self.name = name
        self.value = value
        self.data_type = self.determine_type(token_type)
        self.symbol_type = symbol_type
        self.size = size

    def determine_type(self, token_type):
        if token_type is Scanner.TokenTypes.NUM:
            return DataTypes.NUM
        elif token_type is Scanner.TokenTypes.ARRAY:
            return DataTypes.ARRAY
        elif token_type is Scanner.TokenTypes.VARIABLE:
            return DataTypes.VARIABLE
        elif token_type is Scanner.TokenTypes.PROCEDURE:
            return DataTypes.PROCEDURE
        elif token_type is Scanner.TokenTypes.STRING:
            return DataTypes.STRING
        else:
            return token_type

class SymbolTable(object):

    def __init__(self):
        self.symbol_table = {}
        self.reserved_symbols = ['begin', 'program', 'end.', 'num', 'write', 'array', 'read', 'for', 'to', 'step', 'do']
        self.scope = ""
        self.setup_default_symbols()

    def insert(self, symbol):
        if self.scope:
            symbol.name = self.scope + symbol.name

        if (symbol.name) in self.reserved_symbols:
            raise ValueError("Symbol: {}, is a reserved keyword.".format(symbol))

        if (symbol.name) in self.symbol_table:
            raise ValueError("Symbol: {}, is already defined.".format(symbol))

        if (symbol.name) not in self.symbol_table:
            self.symbol_table[symbol.name] = symbol
            return True

    def lookup(self, symbol_name) -> Symbol:
        if self.scope:
            symbol_name = self.scope + symbol_name

        symbol = self.symbol_table.get(symbol_name)
        if symbol:
            return symbol
        else:
            raise ValueError("Symbol: {}, has not been defined yet.".format(symbol_name))

    def update(self, symbol_name, symbol):
        self.symbol_table.update({symbol_name:symbol})


    def delete(self, symbol_name):
        if self.scope:
            symbol_name = self.scope + symbol_name
        del self.symbol_table[symbol_name]

    def setup_default_symbols(self):
        temp_0 = Symbol("temp_0", 0, Scanner.TokenTypes.VARIABLE, SymbolTypes.KNOWN)
        temp_1 = Symbol("temp_1", 0, Scanner.TokenTypes.VARIABLE, SymbolTypes.KNOWN)
        temp_2 = Symbol("temp_2", 0, Scanner.TokenTypes.VARIABLE, SymbolTypes.KNOWN)
        empty_string = Symbol("empty_string", "\"\"", Scanner.TokenTypes.STRING, SymbolTypes.KNOWN, 128)

        self.insert(temp_0)
        self.insert(temp_1)
        self.insert(temp_2)
        self.insert(empty_string)

    def enter_scope(self, scope_name, scope_type):
        if scope_type == ScopeTypes.CLASS:
            scope_name = scope_type.value.format(scope_name)
        elif scope_type == ScopeTypes.PROCEDURE:
            scope_name = scope_type.value.format(scope_name)

        self.scope = scope_name + self.scope

    def exit_scope(self, scope_name, scope_type):
        if scope_type == ScopeTypes.CLASS:
            scope_name = scope_type.value.format(scope_name)
        elif scope_type == ScopeTypes.PROCEDURE:
            scope_name = scope_type.value.format(scope_name)

        self.scope = self.scope.strip(scope_name)

class SymbolTypes(enum.Enum):
    UNKNOWN = "unknown"
    KNOWN = "known"

class ScopeTypes(enum.Enum):
    CLASS = "class_{}"
    PROCEDURE = "procedure_{}"

class DataTypes(enum.Enum):
    ARRAY = "array"
    NUM = "num"
    VARIABLE = "variable"
    STRING = "string"
    PROCEDURE = "procedure"