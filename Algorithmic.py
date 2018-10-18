from Scanner import  TokenTypes
import collections
from Scanner import Token
import SymbolTable

def label_number_generator():
    n = 0
    while True:
        yield n
        n += 2

class Algorithmic(object):

    def __init__(self, asm_string:list, symbol_table, generator, expression:list):
        self.asm_string = asm_string
        self.symbol_table = symbol_table
        self.generator = generator

        self.expression = collections.deque(expression)
        self.unoptomized = True

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
                return self.expression[index]

    def process_postfix(self, variable):
        if len(self.expression) > 1:
            while len(self.expression) > 1:
                self._process_postfix(self.expression)
            if len(self.expression) == 1:
                last_token = self.expression.pop()
                if last_token.token_type == TokenTypes.VARIABLE:
                    self.asm_string.append("mov esi, DWORD[{}]".format(last_token.token_str))
                elif last_token.token_type == TokenTypes.NUM:
                    self.asm_string.append("mov esi, {}".format(last_token.token_str))
            self.asm_string.append("mov DWORD[{}], esi".format(variable.name))
        else:
            self.assign_value(variable)

    def assign_value(self, variable):
        token = self.expression.pop()

        updated_symbol = self.symbol_table.lookup(variable.name)
        updated_symbol.value = token.token_str
        updated_symbol.symbol_type = SymbolTable.SymbolTypes.KNOWN
        self.symbol_table.update(updated_symbol.name, updated_symbol)

        if token.token_type is TokenTypes.NUM:
            self.asm_string.append("mov DWORD[{}], {}".format(updated_symbol.name, updated_symbol.value))

        elif token.token_type is TokenTypes.VARIABLE:
            if updated_symbol.data_type in [SymbolTable.DataTypes.NUM]:
                self.asm_string.append("mov DWORD[{}], {}".format(updated_symbol.name, updated_symbol.value))

    def _process_postfix(self, expression):
        operator = self.get_from_expression(TokenTypes.ALGORITHMIC)
        operator_index = expression.index(operator)
        self.expression.pop(operator_index)

        operand_right = expression.pop(operator_index-1)
        operand_left = expression.pop(operator_index-2)

        if operand_right is None or operand_left is None:
            raise ValueError("operand_left is {}, operand_right is {}".format(operand_right, operand_left))
        new_token = self.process_expression(operand_left, operand_right, operator)
        if new_token:
            self.expression.insert(operator_index-2, new_token)

    def process_expression(self, opl, opr, operator):
        if operator.token_str == "+":
            return self.add(opl, opr)
        elif operator.token_str == "-":
            return self.sub(opl, opr)
        elif operator.token_str == "*":
            return self.mult(opl, opr)
        elif operator.token_str == "^":
            return self.pow(opl, opr)

    def add(self, opl, opr):
        temporary_asm = []

        try:
            opl_symbol = self.symbol_table.lookup(opl.token_str)
        except ValueError:
            opl_symbol = SymbolTable.Symbol(None, opl.token_str, None, SymbolTable.SymbolTypes.KNOWN)
        try:
            opr_symbol = self.symbol_table.lookup(opr.token_str)
        except ValueError:
            opr_symbol = SymbolTable.Symbol(None, opr.token_str, None, SymbolTable.SymbolTypes.KNOWN)

        if opl_symbol.data_type == SymbolTable.DataTypes.VARIABLE:
            temporary_asm.append("mov esi, DWORD[{}];".format(opl_symbol.name))
        else:
            temporary_asm.append("mov esi, {};".format(opl_symbol.value))

        if opr_symbol.data_type == SymbolTable.DataTypes.VARIABLE:
            temporary_asm.append("add esi, DWORD[{}];".format(opr_symbol.name))
        else:
            temporary_asm.append("add esi, {};".format(opr_symbol.value))

        if self.unoptomized:
            new_token = Token(TokenTypes.VARIABLE)
            new_token.token_str = "temp_0"
            self.asm_string.extend(temporary_asm)
            self.asm_string.append("mov DWORD[temp_0], esi")
            self.unoptomize = True
            return new_token

        else:

            if opl_symbol.symbol_type is SymbolTable.SymbolTypes.KNOWN and opr_symbol.symbol_type is SymbolTable.SymbolTypes.KNOWN:
                new_num_value = str(int(opl_symbol.value) + int(opr_symbol.value))
                new_token = Token(TokenTypes.NUM)
                new_token.token_str = new_num_value
                return new_token
            else:
                new_token = Token(TokenTypes.VARIABLE)
                new_token.token_str = "temp_0"
                self.asm_string.extend(temporary_asm)
                self.asm_string.append("mov DWORD[temp_0], esi")
                self.unoptomized = True
                return new_token

    def sub(self, opl, opr):
        temporary_asm = []
        try:
            opl_symbol = self.symbol_table.lookup(opl.token_str)
        except ValueError:
            opl_symbol = SymbolTable.Symbol(None, opl.token_str, None, SymbolTable.SymbolTypes.KNOWN)
        try:
            opr_symbol = self.symbol_table.lookup(opr.token_str)
        except ValueError:
            opr_symbol = SymbolTable.Symbol(None, opr.token_str, None, SymbolTable.SymbolTypes.KNOWN)

        if opl_symbol.data_type == SymbolTable.DataTypes.VARIABLE:
            temporary_asm.append("mov esi, DWORD[{}];".format(opl_symbol.name))
        else:
            temporary_asm.append("mov esi, {};".format(opl_symbol.value))


        if opr_symbol.data_type == SymbolTable.DataTypes.VARIABLE:
            temporary_asm.append("sub esi, DWORD[{}];".format(opr_symbol.name))
        else:
            temporary_asm.append("sub esi, {};".format(opr_symbol.value))

        if self.unoptomized:
            new_token = Token(TokenTypes.VARIABLE)
            new_token.token_str = "temp_2"
            self.asm_string.extend(temporary_asm)
            self.asm_string.append("mov DWORD[temp_2], esi")
            self.unoptomize = True
            return new_token

        else:

            if opl_symbol.symbol_type is SymbolTable.SymbolTypes.KNOWN and opr_symbol.symbol_type is SymbolTable.SymbolTypes.KNOWN:
                new_num_value = str(int(opl_symbol.value) - int(opr_symbol.value))
                new_token = Token(TokenTypes.NUM)
                new_token.token_str = new_num_value
                return new_token
            else:
                new_token = Token(TokenTypes.VARIABLE)
                new_token.token_str = "temp_2"
                self.asm_string.extend(temporary_asm)
                self.asm_string.append("mov DWORD[temp_2], esi")
                self.unoptomized = True
                return new_token

    def mult(self, opl, opr):
        temporary_asm = []
        try:
            opl_symbol = self.symbol_table.lookup(opl.token_str)
        except ValueError:
            opl_symbol = SymbolTable.Symbol(None, opl.token_str, None, SymbolTable.SymbolTypes.KNOWN)
        try:
            opr_symbol = self.symbol_table.lookup(opr.token_str)
        except ValueError:
            opr_symbol = SymbolTable.Symbol(None, opr.token_str, None, SymbolTable.SymbolTypes.KNOWN)

        if opl_symbol.data_type == SymbolTable.DataTypes.VARIABLE:
            temporary_asm.append("mov esi, DWORD[{}];".format(opl_symbol.name))
        else:
            temporary_asm.append("mov esi, {};".format(opl_symbol.value))


        if opr_symbol.data_type == SymbolTable.DataTypes.VARIABLE:
            temporary_asm.append("imul esi, DWORD[{}];".format(opr_symbol.name))
        else:
            temporary_asm.append("imul esi, {};".format(opr_symbol.value))

        if self.unoptomized:
            new_token = Token(TokenTypes.VARIABLE)
            new_token.token_str = "temp_1"
            self.asm_string.extend(temporary_asm)
            self.asm_string.append("mov DWORD[temp_1], esi")
            self.unoptomize = True
            return new_token

        else:

            if opl_symbol.symbol_type is SymbolTable.SymbolTypes.KNOWN and opr_symbol.symbol_type is SymbolTable.SymbolTypes.KNOWN:
                new_num_value = str(int(opl_symbol.value) * int(opr_symbol.value))
                new_token = Token(TokenTypes.NUM)
                new_token.token_str = new_num_value
                return new_token
            else:
                new_token = Token(TokenTypes.NUM)
                new_token.token_str = "temp_1"
                self.asm_string.extend(temporary_asm)
                self.asm_string.append("mov DWORD[temp_1], esi")
                self.unoptomized = True
                return new_token

    def pow(self, opl, opr):
        temporary_asm = []
        new_temp = self.generator.get_temp_variable()


        try:
            opl_symbol = self.symbol_table.lookup(opl.token_str)
        except ValueError:
            opl_symbol = SymbolTable.Symbol(None, opl.token_str, None, SymbolTable.SymbolTypes.KNOWN)
        try:
            opr_symbol = self.symbol_table.lookup(opr.token_str)
        except ValueError:
            opr_symbol = SymbolTable.Symbol(None, opr.token_str, None, SymbolTable.SymbolTypes.KNOWN)

        label_string_num = next(self.label_num_gen)
        temporary_asm.append("xor edi, edi")	#; clear out the counter
        temporary_asm.append("inc edi")

        if opl_symbol.data_type == SymbolTable.DataTypes.VARIABLE:
            temporary_asm.append("mov esi, DWORD[{}]".format(opl_symbol.name))
        else:
            temporary_asm.append("mov esi, {}".format(opl_symbol.value))

        temporary_asm.append("_exp_top_{}:".format(label_string_num))

        if opl_symbol.data_type == SymbolTable.DataTypes.VARIABLE:
            temporary_asm.append("cmp edi, DWORD[{}];".format(opl_symbol.name))
        else:
            temporary_asm.append("cmp edi, {};".format(opr_symbol.value))

        temporary_asm.append("jz _exp_out_{}".format(label_string_num))       #; jump out if done

        if opl_symbol.data_type == SymbolTable.DataTypes.VARIABLE:
            temporary_asm.append("imul esi, DWORD[{}];".format(opl_symbol.name))
        else:
            temporary_asm.append("imul esi, {};".format(opl_symbol.value))

        temporary_asm.append("inc	edi")
        temporary_asm.append("jmp	_exp_top_{}".format(label_string_num))      #; result of exponentiation is in eax
        temporary_asm.append("_exp_out_{}:".format(label_string_num))

        if self.unoptomized:
            new_token = Token(TokenTypes.VARIABLE)
            new_token.token_str = "temp_0"
            self.asm_string.extend(temporary_asm)
            self.asm_string.append("mov DWORD[temp_0], esi")
            self.unoptomize = True
            return new_token

        else:

            if opl_symbol.symbol_type is SymbolTable.SymbolTypes.KNOWN and opr_symbol.symbol_type is SymbolTable.SymbolTypes.KNOWN:
                new_num_value = str(int(opl_symbol.value) ** int(opr_symbol.value))
                new_token = Token(TokenTypes.NUM)
                new_token.token_str = new_num_value
                return new_token

            else:
                new_token = Token(TokenTypes.NUM)
                new_token.token_str = "temp_0"
                self.asm_string.extend(temporary_asm)
                self.asm_string.append("mov DWORD[temp_0], esi")
                self.unoptomized = True
                return new_token

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
