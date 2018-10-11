from Scanner import TokenTypes
import SymbolTable
import Array


def get_generated_num():
    n = 0
    while True:
        yield n
        n += 2

class IO(object):

    def __init__(self, asm_string, symbol_table, tokens):
        self.asm_string = asm_string
        self.symbol_table = symbol_table
        self.tokens = tokens

    even_number_generator = get_generated_num()


    def read(self):
        symbol = None

        token = self.get_next_token()

        if token.token_type is TokenTypes.VARIABLE:

            try:
                symbol = self.symbol_table.lookup(token.token_str)
            except ValueError:
                pass

            # If theres already a symbol defined
            if symbol:
                symbol.symbol_type = SymbolTable.SymbolTypes.UNKNOWN
                self.symbol_table.update(symbol.name, symbol)

            # No symbol defined
            else:
                new_symbol = SymbolTable.Symbol(token.token_str, None, token.token_type, SymbolTable.SymbolTypes.UNKNOWN)
                self.symbol_table.insert(new_symbol)

        self.asm_string.append("pusha")
        self.asm_string.append("push {}".format(token.token_str))
        self.asm_string.append("push dword int_format")
        self.asm_string.append("call _scanf")
        self.asm_string.append("add	esp, 0x04")
        self.asm_string.append("popa")

    def write(self):

        token_to_write = self.get_next_token()

        if token_to_write.token_type == TokenTypes.STRING:
            next_var = next(self.even_number_generator)

            new_symbol = SymbolTable.Symbol("s{}".format(next_var), token_to_write.token_str, SymbolTable.DataTypes.STRING, SymbolTable.SymbolTypes.KNOWN)
            self.symbol_table.insert(new_symbol)
            self.asm_string.append("push s{}".format(next_var))
            self.asm_string.append("push stringPrinter")
            self.asm_string.append("call _printf")
            self.asm_string.append("add esp, 0x08")

        else:
            symbol = self.symbol_table.lookup(token_to_write.token_str)

            if isinstance(symbol.value, Array.Array):
                self._write_array(token_to_write.token_str)
                return

            if token_to_write.token_type == TokenTypes.VARIABLE:
                self.asm_string.append("push DWORD[{}]".format(token_to_write.token_str))
            elif token_to_write.token_type == TokenTypes.NUM:
                self.asm_string.append("push {}".format(token_to_write.token_str))
            self.asm_string.append("push numberPrinter")
            self.asm_string.append("call _printf")
            self.asm_string.append("add esp, 0x08")
            return

    def _write_array(self, variable_name):

        symbol = self.symbol_table.lookup(variable_name)

        in_array_statement = True
        list_of_indicies = []

        if self.get_next_token().token_str == '[':
            while in_array_statement:
                array_statement_token = self.get_next_token()

                if array_statement_token.token_type is TokenTypes.NUM:
                    list_of_indicies.append(array_statement_token.token_str)
                if array_statement_token.token_str == ']':
                    in_array_statement = False

        self.asm_string.append('xor edi, edi')

        for delta, index in zip(symbol.value.mapping_values, list_of_indicies):
            self.asm_string.append('mov esi, {}'.format(delta))
            self.asm_string.append('imul esi, {}'.format(index))
            self.asm_string.append('add edi, esi')

        self.asm_string.append('sub edi, {}'.format(symbol.value.relocation_factor))
        self.asm_string.append('imul edi, 4')
        self.asm_string.append('add edi, {}'.format(variable_name))
        self.asm_string.append('push DWORD[edi]')
        self.asm_string.append('push numberPrinter')
        self.asm_string.append('call _printf')
        self.asm_string.append('add esp, 0x08')
        self.asm_string.append('\n')

    def get_next_token(self):
        next_token = self.tokens.popleft()
        try:
            self.lookahead_token = self.tokens[0]
        except IndexError:
            self.end_of_tokens = True
        return next_token