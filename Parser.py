import SymbolTable
from collections import deque
from Scanner import TokenTypes
from Array import Array
import Algorithmic

class Parser(object):

    def __init__(self, tokens):
        self.tokens: deque = tokens
        self.symbol_table = SymbolTable.SymbolTable()
        self.asm_file = None
        self.error_file = None
        self.asm_string = []
        self.number_variable_counter = 0
        self.initialized_variables = []
        self.uninitialized_variables = Uninitialized_Variables()
        self.end_of_tokens = False
        self.algorithmic_stack = []

    def get_string_var_num(self):
        n = 0
        while True:
            yield n
            n += 2

    def parse(self):
        self.parse_header()
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

        while not self.end_of_tokens:
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

            elif next_token.token_type == TokenTypes.DELIMETER:
                if next_token.token_str == ";":
                    continue

            elif next_token.token_type == TokenTypes.VARIABLE:
                if next_token.token_str == "end.":
                    self.end()
                    return
                self.variable(next_token)

    def write(self):
        token_to_write = self.get_next_token()

        if token_to_write.token_type == TokenTypes.ALPHANUM:
            self.symbol_table.insert(token_to_write.token_str, token_to_write)
            string_var_number = self.get_string_var_num()
            string_var_number = next(string_var_number)
            self.initialized_variables.append((token_to_write.token_str, "s{}".format(string_var_number)))
            self.asm_string.append("push s{}".format(string_var_number))
            self.asm_string.append("push stringPrinter")
            self.asm_string.append("call _printf")
            self.asm_string.append("add esp, 0x08")

        else:
            variable = self.symbol_table.lookup(token_to_write.token_str)

            if isinstance(variable, Array):
                self.write_array(token_to_write.token_str)
                return

            if token_to_write.token_type == TokenTypes.VARIABLE:
                self.asm_string.append("push DWORD[{}]".format(token_to_write.token_str))
            elif token_to_write.token_type == TokenTypes.NUM:
                self.asm_string.append("push {}".format(token_to_write.token_str))
            self.asm_string.append("push numberPrinter")
            self.asm_string.append("call _printf")
            self.asm_string.append("add esp, 0x08")
            return

    def write_array(self, variable_name):

        variable = self.symbol_table.lookup(variable_name)

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

        for delta, index in zip(variable.mapping_values, list_of_indicies):
            self.asm_string.append('mov esi, {}'.format(delta))
            self.asm_string.append('imul esi, {}'.format(index))
            self.asm_string.append('add edi, esi')

        self.asm_string.append('sub edi, {}'.format(variable.relocation_factor))
        self.asm_string.append('imul edi, 4')
        self.asm_string.append('add edi, {}'.format(variable_name))
        self.asm_string.append('push DWORD[edi]')
        self.asm_string.append('push numberPrinter')
        self.asm_string.append('call _printf')
        self.asm_string.append('add esp, 0x08')
        self.asm_string.append('\n')

    def variable(self, variable_name):
        try:
            variable = self.symbol_table.lookup(variable_name.token_str)
        except ValueError:
            raise ValueError("Variable: {}, has not been defined yet".format(variable_name))

        if isinstance(variable, Array):
            self.array_assignment(variable, variable_name)
            return

        token = self.get_next_token()

        if token.token_str == "=":
            self.variable_assignment(variable)

    def array_assignment(self, variable, variable_name):

        in_array_statement = True
        list_of_indicies = []
        value_to_assign = None

        if self.get_next_token().token_str == '[':
            while in_array_statement:
                array_statement_token = self.get_next_token()

                if array_statement_token.token_type is TokenTypes.NUM:
                    list_of_indicies.append(array_statement_token.token_str)
                if array_statement_token.token_str == ']':
                    in_array_statement = False

        if self.get_next_token().token_str == '=':
            value_to_assign = self.get_next_token()

        self.asm_string.append('xor edi, edi')

        for delta, index in zip(variable.mapping_values, list_of_indicies):
            self.asm_string.append('mov esi, {}'.format(delta))
            self.asm_string.append('imul esi, {}'.format(index))
            self.asm_string.append('add edi, esi')

        self.asm_string.append('sub edi, {}'.format(variable.relocation_factor))
        self.asm_string.append('imul edi, 4')
        self.asm_string.append('add edi, {}'.format(variable_name.token_str))

        self.asm_string.append('mov DWORD[edi], {}'.format(value_to_assign.token_str))
        self.asm_string.append('\n')

    def num(self):
        token = self.get_next_token()

        if token.token_type == TokenTypes.VARIABLE:
            self.symbol_table.insert(token.token_str, token)
        else:
            raise TypeError("Varible token expected, got {} instead".format(token))

        next_token = self.get_next_token()
        if next_token.token_str == ";":
            self.uninitialized_variables.append(token)
            return

        elif next_token.token_str == "=":
            self.variable_assignment(token)

    def variable_assignment(self, variable):
        self.uninitialized_variables.append(variable.token_str)
        expression = []
        token = self.get_next_token()
        while token.token_str != ";":
            expression.append(token)
            token = self.get_next_token()

        algorithmic_class = Algorithmic.Algorithmic(self.asm_string, self.symbol_table, expression)
        algorithmic_class.infix_to_postfix()
        algorithmic_class.process_postfix()

        self.asm_string.append("mov esi, DWORD[temp_0]")
        self.asm_string.append("mov DWORD[{}], esi".format(variable.token_str))

    def array(self):
        # This is for creating an array
        array_variable_name = self.get_next_token()

        array_size_deque = deque()
        in_array_statement = True
        if array_variable_name.token_type is TokenTypes.VARIABLE:

            if self.get_next_token().token_str == '[':
                while in_array_statement:
                    array_statement_token = self.get_next_token()

                    if array_statement_token.token_type is TokenTypes.NUM:
                        array_size_deque.append(array_statement_token.token_str)


                    if array_statement_token.token_str == ']':
                        in_array_statement = False

        array = self._create_array(array_variable_name, array_size_deque)

    def _create_array(self, array_variable_name, array_size_deque):
        lower_bounds = []
        upper_bounds = []

        array_size_deque = iter(list(array_size_deque))
        for value in array_size_deque:
            lower_bounds.append(int(value))
            upper_bounds.append(int(next(array_size_deque)))

        new_array = Array(lower_bounds, upper_bounds)
        new_array.create_array()

        self.uninitialized_variables.append(array_variable_name.token_str, new_array.array_size)
        self.symbol_table.insert(array_variable_name.token_str, new_array)

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
        self.asm_file.write("extern _ExitProcess@4")
        self.asm_file.write("\n")

    def create_initialized(self):
        self.asm_file.write("\n")
        self.asm_file.write("section .data USE32")
        self.asm_file.write("\n")
        self.asm_file.write("\n")

        for init_var, init_value in self.initialized_variables:
            if init_value.isnumeric():
                s = "{} dd {}".format(init_var, init_value)
                self.asm_file.write(s)
                self.asm_file.write("\n")
            elif init_value[0].isalpha():
                s = "{} db {},0x0d,0x0a,0".format(init_value, init_var)
                self.asm_file.write(s)
                self.asm_file.write("\n")
        self.asm_file.write("stringPrinter db \"%s\",0")
        self.asm_file.write("\n")
        self.asm_file.write("numberPrinter db \"%d\",0x0d,0x0a,0")
        self.asm_file.write("\n")

    def create_uninitialized(self):
        self.asm_file.write("\n")
        self.asm_file.write("section .bss USE32")
        self.asm_file.write("\n")
        for variable, size in set(self.uninitialized_variables.vars_list):
            s = "{} resd {}".format(variable, size)
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

class Uninitialized_Variables(object):

    def __init__(self):
        self.vars_list = [("temp_0",1)]

    def append(self, var_name, size=1):
        self.vars_list.append((var_name, size))

    def remove(self, var_name):
        self.vars_list.remove(var_name)