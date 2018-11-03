from Scanner import  TokenTypes
from collections import deque
from Scanner import Token
import SymbolTable


def even_number_generator():
    n = 0
    while True:
        yield n
        n += 2

class StringAlgorithmic(object):

    def __init__(self, asm_string:list, symbol_table, tokens):
        self.asm_string = asm_string
        self.symbol_table = symbol_table
        self.tokens = tokens
        self.lookahead_token = None

    even_number_generator = even_number_generator()



    def copy(self):
        copy_label = "copy_label_{}".format(next(self.even_number_generator)) # Create label for copying
        self.asm_string.append("{}:".format(copy_label))
        self.asm_string.append("mov cl, byte[esi]")
        self.asm_string.append("add cl, 1")
        self.asm_string.append("movsb")
        self.asm_string.append("loop {}".format(copy_label))

    def setup(self):
        #Setup
        self.asm_string.append("mov ecx, 0; Clear ecx")
        self.asm_string.append("cld; Clear")

    def create_string_variable(self):
        # Get name of variable to assign to, move it into edi, and make a symbol of it, insert into table.
        variable_name_token = self.get_next_token()
        self.asm_string.append("mov edi, {}; Destination Register".format(variable_name_token.token_str))
        new_variable_symbol = SymbolTable.Symbol(variable_name_token.token_str,
                                               "", TokenTypes.STRING,
                                               SymbolTable.SymbolTypes.UNKNOWN, 128)
        self.symbol_table.insert(new_variable_symbol)

        # Get string expression and figure out length
        expression = deque()
        while self.lookahead_token.token_str != ";":
            token = self.get_next_token()
            expression.append(token)


        if len(expression) == 0:
            # If there is no expression then its just a variable deceleration. We set it to "", an empty string. We set it
            # In both the symbol table and in actual assembly.
            self.asm_string.append("mov esi, {}; Source Register".format("empty_string"))
            self.copy()
            return

        elif len(expression) > 1:
            # Its being assigned an expression at this point.
            assert expression.popleft().token_str == "="

            while expression:

                # Create a symbol for the value that will be copied to the variable. Insert it.
                string_variable_name = "s{}".format(next(self.even_number_generator))
                string_value_token = expression.popleft()
                string_value_symbol = SymbolTable.Symbol(string_variable_name, string_value_token.token_str,
                                                         SymbolTable.DataTypes.STRING,
                                                         SymbolTable.SymbolTypes.KNOWN,
                                                         )
                self.symbol_table.insert(string_value_symbol)

                self.asm_string.append("mov esi, {}; Source Register".format(string_variable_name))
                self.copy()

                # Now update the Variable Register to hold the string value
                new_variable_symbol.value += string_value_symbol.value
                self.symbol_table.update(new_variable_symbol.name, new_variable_symbol)

                try:
                    if expression[0] == "+":
                        expression.popleft()
                except IndexError:
                    pass

    def assign_to_string(self, variable_to_append_to):
        # Get name of variable to assign to, move it into edi, and make a symbol of it, insert into table.
        variable_to_append_to_symbol = self.symbol_table.lookup(variable_to_append_to.token_str)
        self.asm_string.append("mov edi, {}; Destination Register".format(variable_to_append_to_symbol.name))


        assert self.get_next_token().token_str == "="


        # Get string expression and figure out length
        expression = deque()
        while self.lookahead_token.token_str != ";":
            token = self.get_next_token()
            expression.append(token)

        while expression:

            # Create a symbol for the value that will be copied to the variable. Insert it.
            string_value_token = expression.popleft()

            if string_value_token.token_type == TokenTypes.STRING:
                string_variable_name = "s{}".format(next(self.even_number_generator))
                string_value_symbol = SymbolTable.Symbol(string_variable_name, string_value_token.token_str,
                                                         SymbolTable.DataTypes.STRING,
                                                         SymbolTable.SymbolTypes.KNOWN,
                                                         128
                                                         )
                self.symbol_table.insert(string_value_symbol)

                self.asm_string.append("mov esi, {}; Source Register".format(string_variable_name))
                self.copy()

            # ITs a variable
            else:
                self.asm_string.append("mov esi, {}; Source Register".format(string_value_token.token_str))
                self.copy()

            try:
                if expression[0].token_str == "+":
                    expression.popleft()
                    self.asm_string.append("dec edi")
                    self.asm_string.append("dec edi")
                    self.asm_string.append("dec edi")

            except IndexError:
                return


    def get_next_token(self):
        next_token = self.tokens.popleft()
        try:
            self.lookahead_token = self.tokens[0]
        except IndexError:
            self.end_of_tokens = True
        return next_token
