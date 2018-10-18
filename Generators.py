

class Generators(object):

    def __init__(self, symbol_table):
        self.symbol_table = symbol_table
        self.integer_generator = self._integer_generator()

    def _integer_generator(self):
        n = 0
        while True:
            yield n
            n += 2

    def get_label(self, text):
        new_label = text + "{}:".format(next(self.integer_generator))
        return new_label

    def get_temp_variable(self):
        new_temp = "temp_{}".format(next(self.integer_generator))
        return new_temp