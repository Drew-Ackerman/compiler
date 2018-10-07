import Parser
import Scanner

if __name__ == '__main__':

    scanner = Scanner.Scanner('myfile.txt')
    token_list = scanner.tokenize()

    parser = Parser.Parser(token_list)
    parser.parse()
