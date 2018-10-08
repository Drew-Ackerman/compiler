from collections import deque
import enum
import re
import SymbolTable

class Scanner(object):

    def __init__(self, filename):
        self.file_to_parse = filename
        self.tokens = deque()
        self.current_token = Token(None)

    def tokenize(self):
        with open(self.file_to_parse) as f:

            in_string = False
            in_inline_comment = False
            in_block_comment = False
            end_of_file = False

            # read the entire file
            file = list(f.read())

            # grab an index value for the range of the length of the file
            for index in range(len(file)):

                # if  end of file was reached then stop
                if end_of_file:
                    break

                # go through file char by char
                char:str = file[index]
                try:
                    char_lookahead:str = file[index+1]
                except IndexError as E:
                    end_of_file = True

                # if inline comment flag is set, then look through file until '\n' is found
                if in_inline_comment:
                    if char == '\n':
                        in_inline_comment = False
                        self.current_token = Token(None)

                # If its a block comment then do the same
                elif in_block_comment:
                    if char == "*":
                        if char_lookahead == "/":
                            self.current_token = Token(None)
                    elif char == "/":
                        in_block_comment = False

                # If the char is a new line or a tab, then append the current token
                elif char in ['\n', '\t']:
                    if len(self.current_token.token_str) > 0:
                        self.tokens.append(self.current_token)
                        self.current_token = Token(None)

                # Now lets check to see if / are comment starts or just division.
                else:
                    if char == '/':
                        if char_lookahead == '/':
                            if self.current_token.token_str != '':
                                self.tokens.append(self.current_token)
                            in_inline_comment = True

                        elif char_lookahead == '*':
                            if self.current_token.token_str != '':
                                self.tokens.append(self.current_token)
                            in_block_comment = True

                        else:
                            div_token = Token(TokenTypes.ALGORITHMIC)
                            div_token.token_str = '\\'
                            self.tokens.append(div_token)

                    # Check if char is numbers
                    elif char.isnumeric():
                        if self.current_token.token_type is None:
                            self.current_token.token_type = TokenTypes.NUM
                        self.current_token.token_str += char

                    # Check if char is letters
                    elif char.isalpha():
                        if self.current_token.token_type is None:
                            self.current_token.token_type = TokenTypes.ALPHANUM
                        self.current_token.token_str += char

                    elif char == "\"":
                        self.current_token.token_str += char
                        in_string = not in_string

                    # If space is found
                    elif char in [' ']:
                        if in_string:
                            self.current_token.token_str += char
                        else:
                            if self.current_token.token_str != '':
                                self.tokens.append(self.current_token)
                                self.current_token = Token(None)

                    elif char in ['.']:
                        if self.current_token.token_type is TokenTypes.ALPHANUM:
                            self.current_token.token_str += char
                        else:
                            self.tokens.append(self.current_token)
                            self.current_token = Token(None)

                    elif char in [',',';','[', ']', '(', ')' , '{', '}']:
                        self.tokens.append(self.current_token)
                        self.current_token = Token(None)

                        delimeter_token = Token(TokenTypes.DELIMETER)
                        delimeter_token.token_str += char
                        self.tokens.append(delimeter_token)

                    elif char in ['=', '+', '^', '-', '*']:
                        self.current_token.token_str += char
                        self.current_token.token_type = TokenTypes.ALGORITHMIC

                    elif char in ['!', '>', '<']:
                        self.current_token.token_str += char
                        self.current_token.token_type = TokenTypes.RELATIONAL

        self.tokens.append(self.current_token)
        self.assign_types()

        self.clear_cruft()
        return self.tokens


    def clear_cruft(self):
        temp_list = [token for token in self.tokens if token.token_type is not None]
        self.tokens = deque(temp_list)

    def assign_types(self):

        regexKW = r'(program|begin|end|write|read|num|array|for|to|step|do|if|then)$'
        regexVariable = r'([a-zA-Z_][a-zA-Z_$0-9]*)'
        regexString = r'(^").*("$)'
        regexRelationalOperators = r'(!=|==|>|<|>=|<=)'
        regexAlgorithmic = r'[\=\+\^\-\*]'


        for token in self.tokens:

            if re.match(regexKW, token.token_str):
                token.token_type = TokenTypes.KEYWORD

            elif re.match(regexVariable, token.token_str):
                token.token_type = TokenTypes.VARIABLE

            elif re.match(regexString, token.token_str):
                token.token_type = TokenTypes.STRING

            elif re.match(regexAlgorithmic, token.token_str):
                token.token_type = TokenTypes.ALGORITHMIC

            elif re.match(regexRelationalOperators, token.token_str):
                token.token_type = TokenTypes.RELATIONAL

            else:
                pass

class TokenTypes(enum.Enum):
    ALPHANUM = "alphanumeric"
    KEYWORD = "keyword"
    NUM = "num"
    DELIMETER = "delimeter"
    ALGORITHMIC = "algo"
    VARIABLE = "variable"
    ARRAY = "array"
    STRING = "string"
    RELATIONAL = "relational"


class Token(object):

    def __init__(self, token_type):
        self.token_str = ''
        self.token_type = token_type

    def __repr__(self):
        return "Token Str -> {} :: Token Type-> {}".format(self.token_str, self.token_type)