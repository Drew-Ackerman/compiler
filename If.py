from Scanner import TokenTypes
import Parser

def get_generated_num():
    n = 0
    while True:
        yield n
        n += 2


even_number_generator = get_generated_num()


class If(object):

    def __init__(self, asm_string, tokens, symbol_table):
        self.asm_string = asm_string
        self.tokens = tokens
        self.symbol_table = symbol_table

        self.even_number_for_labels = next(even_number_generator)

    def get_next_token(self):
        next_token = self.tokens.popleft()
        try:
            self.lookahead_token = self.tokens[0]
        except IndexError:
            self.end_of_tokens = True
        return next_token

    def create_start(self):
        left_hand = self.get_next_token()
        operation = self.get_next_token()
        right_hand = self.get_next_token()

        if left_hand.token_type == TokenTypes.VARIABLE:
            left_hand_symbol = self.symbol_table.lookup(left_hand.token_str)
            self.asm_string.append("mov edi, DWORD[{}]".format(left_hand_symbol.name))
        else:
            self.asm_string.append("mov edi, {}".format(left_hand.token_str))

        if right_hand.token_type == TokenTypes.VARIABLE:
            right_hand_symbol = self.symbol_table.lookup(right_hand.token_str)
            self.asm_string.append("cmp edi, DWORD[{}]".format(right_hand_symbol.name))
        else:
            self.asm_string.append("cmp edi, {}".format(right_hand.token_str))

        if operation.token_str == "==":
            self.asm_string.append("jne _endif_{}".format(self.even_number_for_labels))

        elif operation.token_str == "!=":
            self.asm_string.append("je _endif_{}".format(self.even_number_for_labels))

        elif operation.token_str == ">":
            self.asm_string.append("jle _endif_{}".format(self.even_number_for_labels))

        elif operation.token_str == "<":
            self.asm_string.append("jge _endif_{}".format(self.even_number_for_labels))

        elif operation.token_str == "<=":
            self.asm_string.append("jg _endif_{}".format(self.even_number_for_labels))

        elif operation.token_str == ">=":
            self.asm_string.append("jl _endif_{}".format(self.even_number_for_labels))
        return

    def create_end(self):
        if self.lookahead_token.token_str == "else":
            pass

        self.asm_string.append("_endif_{}:".format(self.even_number_for_labels))
        return

class Else(object):

    def __init__(self, asm_string, tokens, symbol_table):
        self.asm_string = asm_string
        self.tokens = tokens
        self.symbol_table = symbol_table

        self.even_number_for_labels = next(even_number_generator)

    def get_next_token(self):
        next_token = self.tokens.popleft()
        try:
            self.lookahead_token = self.tokens[0]
        except IndexError:
            self.end_of_tokens = True
        return next_token