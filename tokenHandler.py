import re

class TokenHandler:    
    tokens = []
    index = 0
    
    #Generates token list from the given file path
    def __init__(self, filePath):
        with open(filePath) as inputFile:
            lines = inputFile.readlines()
        row = 0
        commentRemoval = False

        regExKeywords = r'(program'\
                      + r'|begin|procedure|end\.'\
                      + r'|switch|case|default'\
                      + r'|write|read'\
                      + r'|for|to|step|do'\
                      + r'|if|then|else'\
                      + r'|return'\
                      + r'|num)\s'

        regExNumber = r'(\d+)'

        regExVariable = r'([a-zA-Z_][a-zA-Z_$0-9]*)'

        regExOperator = r'(!=|==|='\
                      + r'|\+|-|/|\*|\^'\
                      + r'|]|\[|\(|\)'\
                      + r'|;|,)'

        for line in lines:
            row += 1
            column = 0
            while column < len(line):
                if commentRemoval == True:
                    endColumn = 0
                    while line[endColumn - 1] != '*' or line[endColumn] != '/':
                        if line[endColumn] == '\n':
                            break
                        endColumn += 1
                    if line[endColumn] == '\n':
                        break
                    column = endColumn + 2
                    commentRemoval = False

                #strings have precedence
                elif line[column] == '"':
                    endColumn = column + 1
                    while line[endColumn - 1] == '\\' or line[endColumn] != '"' :
                        endColumn += 1
                        if line[endColumn] == '\n':
                            print("ERROR: string not terminated line: {} row: {}", row, column)
                            break
                    self.tokens.append(["STRING", line[column:endColumn], row, column])
                    column = endColumn + 1

                #if the next characters are newline or // then continue to next line
                elif line[column] == '\n':
                    break
                elif line[column] == '/' and line[column + 1] == '/':
                    break

                #handle multiline comments
                elif line[column] == '/' and line[column + 1] == '*':
                    endColumn = column + 2
                    commentRemoval = True
                    while line[endColumn - 1] != '*' or line[endColumn] != '/':
                        if line[endColumn] == '\n':
                            break
                        endColumn += 1
                    if line[endColumn] == '\n':
                        break
                    column = endColumn + 1
                    commentRemoval = False

                #bypass whitespace
                elif re.match(r'[\t ]', line[column:]):
                    column += 1
                elif re.match(regExKeywords, line[column:]):
                    tmp = re.match(regExKeywords, line[column:])
                    self.tokens.append(['KEYWORD', tmp.group(1), row, column])
                    column += len(tmp.group(1))
                elif re.match(regExVariable, line[column:]):
                    tmp = re.match(regExVariable, line[column:])
                    self.tokens.append(['VARIABLE', tmp.group(1), row, column])
                    column += len(tmp.group(1))
                elif re.match(regExOperator, line[column:]):
                    tmp = re.match(regExOperator, line[column:])
                    self.tokens.append(['OPERATOR', tmp.group(1), row, column])
                    column += len(tmp.group(1))
                elif re.match(regExNumber, line[column:]):
                    tmp = re.match(regExNumber, line[column:])
                    self.tokens.append(['NUMBER', tmp.group(1), row, column])
                    column += len(tmp.group(1))
                else:
                    column += 1

    #offset shall be the distance from the current index to allow for look ahead
    #entry shall be 0 for type, 1 for value, 2 for row, and 3 for column
    def peekType(self, offset=0):
        return self.tokens[self.index+offset][0]
    
    
    def peekValue(self, offset=0):
        return self.tokens[self.index+offset][1]
    
    
    def getRow(self):
        return self.tokens[self.index][2]


    def getColumn(self):
        return self.tokens[self.index][3]
    
    
    def consume(self):
        self.index += 1