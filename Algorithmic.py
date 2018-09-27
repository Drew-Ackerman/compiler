
from Scanner import  TokenTypes
import collections

def label_number_generator():
    n = 0
    while True:
        yield n
        n += 2

class Algorithmic(object):

    def __init__(self, asm_string:list, symbol_table, expression:list):
        self.asm_string = asm_string
        self.symbol_table = symbol_table

        self.expression = expression

    label_num_gen = label_number_generator()

    def infix_to_postfix(self):
        stack = []
        postfix_token_list = []

        self.expression.reverse()
        while self.expression:
            token = self.expression.pop()
            if token.token_str == "(":
                stack.append(token)
            elif token.token_str == ")":

                while stack:
                    popped_token = stack.pop()
                    if popped_token.token_str == "(":
                        break
                    else:
                        postfix_token_list.append(popped_token)

            elif token.token_type == TokenTypes.ALGORITHMIC:
                token_priority = self.get_priority(token.token_str)

                if stack:
                    if stack[-1].token_str == '(':
                        stack_priority = 0
                    else:
                        stack_priority = self.get_priority(stack[-1].token_str)
                else:
                    stack_priority = 0

                if not stack or (token_priority > stack_priority):
                    stack.append(token)
                else:
                    while (stack_priority >= token_priority) and stack:
                        postfix_token_list.append(stack.pop())
                    stack.append(token)
            else:
                postfix_token_list.append(token)

        while stack:
            postfix_token_list.append(stack.pop())

        self.expression = postfix_token_list

    def get_from_expression(self, *args):
        token_types = list(args)

        for index, token in enumerate(self.expression):
            if token.token_type in token_types:
                return self.expression.pop(index)

    def process_postfix(self):
        self.setup_temp()

        while self.expression:
            self._process_postfix(self.expression)

    def setup_temp(self):
        token_to_assign = self.get_from_expression(TokenTypes.VARIABLE, TokenTypes.NUM)
        if token_to_assign.token_type == TokenTypes.VARIABLE:
            self.asm_string.append("mov esi, DWORD[{}];".format(token_to_assign.token_str))
            self.asm_string.append("mov DWORD[temp_0], esi;".format(token_to_assign.token_str))
        else:
            self.asm_string.append("mov DWORD[temp_0], {};".format(token_to_assign.token_str))

    def _process_postfix(self, expression):

        operand = self.get_from_expression(TokenTypes.NUM, TokenTypes.VARIABLE)
        operator = self.get_from_expression(TokenTypes.ALGORITHMIC)


        if operand is None or operator is None:
            raise ValueError("operand is {}, operator is {}".format(operand, operator))

        self.process_expression(operand, operator)

    def process_expression(self, operand, operator):

        if operator.token_str == "+":
            self.add(operand)
        elif operator.token_str == "-":
            self.sub(operand)
        elif operator.token_str == "*":
            self.mult(operand)
        elif operator.token_str == "^":
            self.pow(operand)

        self.asm_string.append("mov DWORD[temp_0], edi;")

    def add(self, operand):
        self.asm_string.append("mov edi, DWORD[temp_0];")
        if operand.token_type == TokenTypes.VARIABLE:
            self.asm_string.append("add edi, DWORD[{}];".format(operand.token_str))
        else:
            self.asm_string.append("add edi, {};".format(operand.token_str))

    def sub(self, operand):
        self.asm_string.append("mov edi, DWORD[temp_0];")
        if operand.token_type == TokenTypes.VARIABLE:
            self.asm_string.append("sub edi, DWORD[{}];".format(operand.token_str))
        else:
            self.asm_string.append("sub edi, {};".format(operand.token_str))

    def mult(self, operand):
        self.asm_string.append("mov edi, DWORD[temp_0];")
        if operand.token_type == TokenTypes.VARIABLE:
            self.asm_string.append("imul edi, DWORD[{}];".format(operand.token_str))
        else:
            self.asm_string.append("imul edi, {};".format(operand.token_str))

    def pow(self, operand):
        label_string_num = next(self.label_num_gen)
        self.asm_string.append("xor edi, edi")	#; clear out the counter
        self.asm_string.append("inc edi")
        self.asm_string.append("mov eax, DWORD[temp_0]")
        self.asm_string.append("_exp_top_{}:".format(label_string_num))

        if operand.token_type == TokenTypes.VARIABLE:
            self.asm_string.append("cmp edi, DWORD[{}];".format(operand.token_str))
        else:
            self.asm_string.append("cmp edi, {};".format(operand.token_str))

        self.asm_string.append("jz _exp_out_{}".format(label_string_num))       #; jump out if done
        self.asm_string.append("imul eax, DWORD[temp_0]")
        self.asm_string.append("inc	edi")
        self.asm_string.append("jmp	_exp_top_{}".format(label_string_num))      #; result of exponentiation is in eax
        self.asm_string.append("_exp_out_{}:".format(label_string_num))
        self.asm_string.append("mov	DWORD[temp_0],	eax")
        self.asm_string.append("mov edi, DWORD[temp_0]")
    def get_priority(self, token_str):
            if token_str in ["+",  "-"]:
                return 1
            elif token_str in ["*", "/"]:
                return 2
            elif token_str in ['^']:
                return 3
            elif token_str in ['(']:
                return 4
            elif token_str in [')']:
                return 4
