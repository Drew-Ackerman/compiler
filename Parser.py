import SymbolTable
from collections import deque
from Scanner import TokenTypes
from Array import Array
import Algorithmic
import IO
import For


def get_generated_num():
    n = 0
    while True:
        yield n
        n += 2

class Parser(object):

    def __init__(self, tokens):
        self.tokens: deque = tokens
        self.symbol_table = SymbolTable.SymbolTable()
        self.asm_file = None
        self.error_file = None
        self.asm_string = []
        self.number_variable_counter = 0
        self.initialized_variables = []
        self.end_of_tokens = False
        self.algorithmic_stack = []

        self.for_loop_counter = 0

    even_number_generator = get_generated_num()


    def parse(self):
        self.parse_header()

        while not self.end_of_tokens:
            self.statement()

    def parse_header(self):
        if self.get_next_token().token_str != 'program':
            raise ValueError("program was not the first token.")

        program_name = self.get_next_token()

        if program_name.token_type == TokenTypes.VARIABLE:
            self.asm_file = open("{}.asm".format(program_name.token_str), "w", encoding="utf-8")
            self.error_file = open("{}.err".format(program_name.token_str), "w", encoding="utf-8")
        else:
            raise ValueError("{} is not a valid alphanumeric program name".format(program_name.token_str))

        if self.get_next_token().token_str != ';':
            raise ValueError("';' was expected, did not get ';'")

        if self.get_next_token().token_str != 'begin':
            raise ValueError("Did not get 'begin'")
        return

    def statement(self):

            next_token = self.get_next_token()

            if next_token.token_type == TokenTypes.KEYWORD:
                if next_token.token_str == "num":
                    self.num()
                elif next_token.token_str == "write":
                    self.write()
                elif next_token.token_str == "end.":
                    self.end()
                elif next_token.token_str == "array":
                    self.array()
                elif next_token.token_str == "read":
                    self.read()
                elif next_token.token_str == "for":
                    self.for_loop()

            elif next_token.token_type == TokenTypes.DELIMETER:
                if next_token.token_str == ";":
                    return

            elif next_token.token_type == TokenTypes.VARIABLE:
                if next_token.token_str == "end.":
                    self.end()
                else:
                    self.variable(next_token)
            return

    def for_loop(self):
        loop_counter = self.for_loop_counter
        self.for_loop_counter += 1
        for_class = For.For(self.asm_string, self.tokens, self.symbol_table)
        for_class.create_start(loop_counter)


        assert self.get_next_token().token_str == "{"

        while self.lookahead_token.token_str != "}":
            self.statement()

        assert self.get_next_token().token_str == "}"

        loop_counter = self.for_loop_counter
        self.for_loop_counter += 1
        for_class.create_end(loop_counter)

        return

    def read(self):
        io = IO.IO(self.asm_string, self.symbol_table, self.tokens)
        io.read()

    def write(self):
        io = IO.IO(self.asm_string, self.symbol_table, self.tokens)
        io.write()

    def variable(self, variable_name):
        try:
            symbol = self.symbol_table.lookup(variable_name.token_str)
        except ValueError:
            raise ValueError("Variable: {}, has not been defined yet".format(variable_name))

        if isinstance(symbol.value, Array):
            self.array_assignment(symbol, variable_name)
            return

        token = self.get_next_token()

        if token.token_str == "=":
            self.variable_assignment(symbol)

    def array_assignment(self, symbol, variable_name):

        in_array_statement = True
        list_of_indicies = []
        value_to_assign = None

        array = symbol.value

        if self.get_next_token().token_str == '[':
            while in_array_statement:
                array_statement_token = self.get_next_token()

                if array_statement_token.token_type is TokenTypes.NUM:
                    list_of_indicies.append(array_statement_token.token_str)
                if array_statement_token.token_str == ']':
                    in_array_statement = False

        if self.get_next_token().token_str == '=':
            value_to_assign = self.get_next_token()
        else:
            raise ValueError("There needs to be an equal sign for assignment.")

        self.asm_string.append('xor edi, edi')

        for delta, index in zip(array.mapping_values, list_of_indicies):
            self.asm_string.append('mov esi, {}'.format(delta))
            self.asm_string.append('imul esi, {}'.format(index))
            self.asm_string.append('add edi, esi')

        self.asm_string.append('sub edi, {}'.format(array.relocation_factor))
        self.asm_string.append('imul edi, 4')
        self.asm_string.append('add edi, {}'.format(variable_name.token_str))

        self.asm_string.append('mov DWORD[edi], {}'.format(value_to_assign.token_str))
        self.asm_string.append('\n')

    def num(self):
        token = self.get_next_token()

        if token.token_type == TokenTypes.VARIABLE:
            new_symbol = SymbolTable.Symbol(token.token_str, None, token.token_type, SymbolTable.SymbolTypes.UNKNOWN)
            self.symbol_table.insert(new_symbol)
        else:
            raise TypeError("Varible token expected, got {} instead".format(token))

        if self.lookahead_token.token_str == "=":
            self.get_next_token() # Clear out the "=" token
            self.variable_assignment(self.symbol_table.lookup(token.token_str))

    def variable_assignment(self, symbol):
        expression = []
        token = self.get_next_token()
        while token.token_str != ";":
            expression.append(token)
            token = self.get_next_token()

        algorithmic_class = Algorithmic.Algorithmic(self.asm_string, self.symbol_table, expression)
        algorithmic_class.infix_to_postfix()
        algorithmic_class.process_postfix(symbol)

        # self.asm_string.append("mov esi, DWORD[temp_0]")
        # self.asm_string.append("mov DWORD[{}], esi".format(symbol.name))

    def array(self):
        # This is for creating an array
        array_variable = self.get_next_token()

        array_size_deque = deque()
        in_array_statement = True
        if array_variable.token_type is TokenTypes.VARIABLE:

            if self.get_next_token().token_str == '[':
                while in_array_statement:
                    array_statement_token = self.get_next_token()

                    if array_statement_token.token_type is TokenTypes.NUM:
                        array_size_deque.append(array_statement_token.token_str)


                    if array_statement_token.token_str == ']':
                        in_array_statement = False

        array = self._create_array(array_variable.token_str, array_size_deque)

    def _create_array(self, array_variable_name, array_size_deque):
        lower_bounds = []
        upper_bounds = []

        array_size_deque = iter(list(array_size_deque))
        for value in array_size_deque:
            lower_bounds.append(int(value))
            upper_bounds.append(int(next(array_size_deque)))

        new_array = Array(lower_bounds, upper_bounds)
        new_array.create_array()
        new_array_symbol = SymbolTable.Symbol(array_variable_name, new_array, TokenTypes.ARRAY, SymbolTable.SymbolTypes.KNOWN)
        self.symbol_table.insert(new_array_symbol)

        return new_array

    def end(self):
        # if self.get_next_token().token_str == '.':
            self.create_file()
        # else:
        #     raise ValueError("The 'end.' Token was not the final token called")

    def create_file(self):
        self.create_exports()
        self.create_imports()

        self.create_initialized()
        self.create_uninitialized()
        self.print_asm_string()

    def create_exports(self):
        self.asm_file.write("global _main")
        self.asm_file.write("\n")
        self.asm_file.write("EXPORT _main")
        self.asm_file.write("\n")

    def create_imports(self):

        self.asm_file.write("\n")
        self.asm_file.write("extern _printf")
        self.asm_file.write("\n")
        self.asm_file.write("extern _scanf")
        self.asm_file.write("\n")
        self.asm_file.write("extern _ExitProcess@4")
        self.asm_file.write("\n")

    def create_initialized(self):
        self.asm_file.write("\n")
        self.asm_file.write("section .data USE32")
        self.asm_file.write("\n")
        self.asm_file.write("\n")

        for symbol_name, symbol in self.symbol_table.symbol_table.items():
            if symbol.data_type is SymbolTable.DataTypes.STRING:
                s = "{} db {},0x0d,0x0a,0".format(symbol_name, symbol.value)
                self.asm_file.write(s)
                self.asm_file.write("\n")

        self.asm_file.write("stringPrinter db \"%s\",0")
        self.asm_file.write("\n")
        self.asm_file.write("numberPrinter db \"%d\",0x0d,0x0a,0")
        self.asm_file.write("\n")
        self.asm_file.write("int_format db \"%i\", 0")
        self.asm_file.write("\n")

    def create_uninitialized(self):
        self.asm_file.write("\n")
        self.asm_file.write("section .bss USE32")
        self.asm_file.write("\n")
        for symbol_name, symbol in self.symbol_table.symbol_table.items():
            if symbol.data_type is not SymbolTable.DataTypes.STRING:
                s = "{} resd {}".format(symbol_name, symbol.size)
                self.asm_file.write(s)
                self.asm_file.write("\n")

    def print_asm_string(self):
        self.asm_file.write("\n")
        self.asm_file.write("section .code USE32")
        self.asm_file.write("\n")
        self.asm_file.write("_main:")

        for asm_instruction in self.asm_string:
            self.asm_file.write("\n")
            self.asm_file.write(asm_instruction)

        self.asm_file.write("\n")
        self.asm_file.write("exit:")
        self.asm_file.write("\n")

        self.asm_file.write("\n")
        self.asm_file.write("mov eax, 0x0")
        self.asm_file.write("\n")
        self.asm_file.write("call _ExitProcess@4")
        self.asm_file.write("\n")

    def get_next_token(self):
        next_token = self.tokens.popleft()
        try:
            self.lookahead_token = self.tokens[0]
        except IndexError:
            self.end_of_tokens = True
        return next_token
