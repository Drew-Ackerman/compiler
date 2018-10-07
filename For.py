from Scanner import TokenTypes
import Parser

def get_generated_num():
    n = 0
    while True:
        yield n
        n += 2


class For(object):

    def __init__(self, asm_string, tokens, symbol_table):
        self.asm_string = asm_string
        self.tokens = tokens
        self.symbol_table = symbol_table

        self.step_symbol = None
        self.step_token = None
        self.init_symbol = None
        self.even_number_for_labels = None

    even_number_generator = get_generated_num()

    def get_next_token(self):
        next_token = self.tokens.popleft()
        try:
            self.lookahead_token = self.tokens[0]
        except IndexError:
            self.end_of_tokens = True
        return next_token

    def create_start(self,counter):
        self.which_registers_to_use = self.select_registers(counter)

        variable = self.get_next_token()

        self.init_symbol = self.symbol_table.lookup(variable.token_str)

        assert self.get_next_token().token_str == "="

        init_assignment_value_token = self.get_next_token()
        if init_assignment_value_token.token_type is TokenTypes.VARIABLE:
            init_assignment_value_symbol = self.symbol_table.lookup(init_assignment_value_token.token_str)
            self.asm_string.append("mov {}, DWORD[{}]".format(self.which_registers_to_use, init_assignment_value_symbol.name))
        else:
            self.asm_string.append("mov {}, {}".format(self.which_registers_to_use, init_assignment_value_token.token_str))

        # Assign value to init variable from the assignment value.
        self.asm_string.append("mov DWORD[{}], {}".format(self.init_symbol.name, self.which_registers_to_use))


        assert self.get_next_token().token_str == "to"

        end_range_token = self.get_next_token()
        if end_range_token.token_type is TokenTypes.VARIABLE:
            end_range_symbol = self.symbol_table.lookup(end_range_token.token_str)
            self.asm_string.append("mov {}, DWORD[{}] ;end range assignment".format(self.which_registers_to_use, end_range_symbol.name))
        else:
            self.asm_string.append("mov {}, {} ;end range assignment".format(self.which_registers_to_use, end_range_token.token_str))


        assert self.get_next_token().token_str == "step"

        self.step_token = self.get_next_token()
        if self.step_token.token_type is TokenTypes.VARIABLE:
            self.step_symbol = self.symbol_table.lookup(self.step_token.token_str)

        assert self.get_next_token().token_str == "do"

        self.even_number_for_labels = next(self.even_number_generator)


        self.asm_string.append("loop_start_{}:".format(self.even_number_for_labels))
        self.asm_string.append("cmp DWORD[{}], {}".format(self.init_symbol.name, self.which_registers_to_use))
        self.asm_string.append("jg loop_end_{}".format(self.even_number_for_labels))

    def create_end(self,counter):
        self.which_registers_to_use = self.select_registers(counter)

        #End Block
        if self.step_symbol:
            self.asm_string.append("mov {}, DWORD[{}] ; step assignment".format(self.which_registers_to_use, self.step_symbol.name)) # <- Move step into esi
        else:
            self.asm_string.append("mov {}, {}; step assignment".format(self.which_registers_to_use, self.step_token.token_str))


        self.asm_string.append("add DWORD[{}], {}".format(self.init_symbol.name, self.which_registers_to_use))
        self.asm_string.append("jmp loop_start_{}".format(self.even_number_for_labels))
        self.asm_string.append("loop_end_{}:".format(self.even_number_for_labels))

        return


    def select_registers(self, counter):
        mod_var = 4

        if  counter % mod_var == 0:
            return "eax"
        elif counter % mod_var == 1:
            return "ebx"
        elif counter % mod_var == 2:
            return "ecx"
        elif counter % mod_var == 3:
            return "edx"
        # elif counter % mod_var == 4:
        #     return "esp"
        # elif counter % mod_var == 5:
        #     return "ebp"