import Parser
import copy


class CFG(object):

    def __init__(self, production_rule_list: list):
        self.production_rules = production_rule_list
        self.starting_production_rule = production_rule_list[0]
        self.left_hands = self.left_hand_listing()

        self.iteration_count = 0

    def process_word(self, word_to_match, current_string):

        # print("process word start: " + current_string)
        self.iteration_count += 1

        if self.iteration_count > 100000000:
            return False

        if word_to_match == current_string:
            return True

        if len(current_string) > len(word_to_match) + 12:
            return False

        # Find the first non terminal in the working string
        found_non_terminal = self.find_non_terminal(current_string)
        # If one was found then continue
        if found_non_terminal:

            result = False

            # Iterate through rules
            for rule in self.production_rules:

                # if found_non_terminal == rule.left_hand
                if found_non_terminal in rule.left_hand:
                    # Make a new string
                    new_string = self.replace_non_term(rule, current_string)
                    # recurse
                    result = self.process_word(word_to_match, new_string)
                    #print("process word result: " + str(result))

                    # if the result is true, exit from production_rules iteration.
                    if result:
                        break

            return result

    def find_non_terminal(self, current_string):

        if isinstance(current_string, Parser.ProductionRule):
            current_string = current_string.right_hand
        lb = current_string.find("<")
        rb = current_string.find(">") + 1

        if lb > 0 and rb > 0:
            non_term = current_string[lb:rb]
            return non_term
        return False

    def left_hand_listing(self):
        temp = []
        for rule in self.production_rules:
            temp.append(rule.left_hand[1])
        return temp

    def replace_non_term(self, production_rule, current_string):
        return current_string.replace(production_rule.left_hand, production_rule.right_hand, 1)


if __name__ == '__main__':

    parser = Parser.Parser("parser_passoff.txt")
    parser.parse()

    for grammer in parser.grammers:
        production_rules = grammer[0]
        words = grammer[1]

        the_sorted_list = copy.deepcopy(production_rules)
        a = the_sorted_list[:1]
        b = the_sorted_list[1:]
        b.sort(key=len, reverse=True)
        c = a + b
        cfg = CFG(c)

        print(" ")
        print("Production Rules: ")
        for rule in production_rules:
            print(rule)

        for word in words:
            cfg.iteration_count = 0
            print("Is {} in the language?".format(word))
            if cfg.process_word(word, str(cfg.starting_production_rule.right_hand)):
                print("Yes")
            else:
                print("No")