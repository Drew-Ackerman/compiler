import re

class Parser(object):

    def __init__(self, filename):
        self.file_to_parse = filename
        self.grammers = []
        self.production_rules = []
        self.words = []

    def parse(self):
        space_count = 0

        with open(self.file_to_parse) as file:

            for line in file:

                # Its a production rule
                if re.search('::=', line):
                    self.production_rules.append(self.parse_production_rule(line))

                # No, its white space
                elif line.isspace():
                    space_count += 1
                    if space_count % 2 == 0:
                        self.grammers.append([self.production_rules[:], self.words[:]])
                        self.production_rules.clear()
                        self.words.clear()

                # No, its a word to match
                else:
                    self.words.append(line.strip())

        return self.grammers

    def parse_production_rule(self, rule:str):

        left_hand_rule_end_index = rule.find(" ")
        right_hand_rule_start_index = rule.rfind(" ")

        left_side = rule[0:left_hand_rule_end_index].strip()
        right_side = rule[right_hand_rule_start_index:-1].strip()

        return ProductionRule(left_side, right_side)

class ProductionRule(object):

    def __init__(self, left_hand, right_hand):
        self.left_hand = left_hand
        self.right_hand = right_hand
        self.complete_rule = self.__str__()

    def __str__(self):
        return "{} ::= {}".format(self.left_hand, self.right_hand)

    def __len__(self):
        return len(self.complete_rule)