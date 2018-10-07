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
        else:
            return token_type

class SymbolTable(object):

    def __init__(self):
        self.symbol_table = {}
        self.reserved_symbols = ['begin', 'program', 'end.', 'num', 'write', 'array', 'read', 'for', 'to', 'step', 'do']

        self.setup_default_symbols()

    def insert(self, symbol):
        if (symbol.name) in self.reserved_symbols:
            raise ValueError("Symbol: {}, is a reserved keyword.".format(symbol))

        if (symbol.name) in self.symbol_table:
            raise ValueError("Symbol: {}, is already defined.".format(symbol))

        if (symbol.name) not in self.symbol_table:
            self.symbol_table[symbol.name] = symbol
            return True

    def lookup(self, symbol_name) -> Symbol:
        symbol = self.symbol_table.get(symbol_name)
        if symbol:
            return symbol
        else:
            raise ValueError("Symbol: {}, has not been defined yet.".format(symbol_name))

    def update(self, symbol_name, symbol):
        self.symbol_table.update({symbol_name:symbol})


    def delete(self, symbol_name):
        del self.symbol_table[symbol_name]

    def setup_default_symbols(self):
        temp_0 = Symbol("temp_0", 0, Scanner.TokenTypes.VARIABLE, SymbolTypes.KNOWN)
        self.insert(temp_0)

class SymbolTypes(enum.Enum):
    UNKNOWN = "unknown"
    KNOWN = "known"

class DataTypes(enum.Enum):
    ARRAY = "array"
    NUM = "num"
    VARIABLE = "variable"
    STRING = "string"