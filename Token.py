

class Token(object):

    def __init__(self, string):
        self.token_string = string

    def is_integer(self):
        try:
            if int(self.token_string):
                return True
        except ValueError:
            return False

    def is_alpha(self):
        pass