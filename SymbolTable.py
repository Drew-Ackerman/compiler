

class SymbolTable(object):

    def __init__(self):
        self.symbol_table = {}
        self.reserved_symbols = ['begin', 'program', 'end', 'num', 'write', 'array']

    def insert(self, var_name, symbol):
        if (var_name) in self.reserved_symbols:
            raise ValueError("Symbol: {}, is a reserved keyword.".format(symbol))

        if (var_name) in self.symbol_table:
            raise ValueError("Symbol: {}, is already defined.".format(symbol))

        if (var_name) not in self.symbol_table:
            self.symbol_table[var_name] = symbol
            return True

    def lookup(self, var_name):
        symbol = self.symbol_table.get(var_name)
        if symbol:
            return symbol
        else:
            raise ValueError("Symbol: {}, has not been defined yet.".format(var_name))

    def delete(self, var_name):
        del self.symbol_table[var_name]


class Symbol(object):

    def __init__(self, name, value, type):
        self.name = name
        self.value = value
        self.type = type
