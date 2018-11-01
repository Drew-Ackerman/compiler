

class RegisterAllocation(object):

    def __init__(self):
        self.register_dict = {"eax":0,  "ebx": 0, "ecx":0, "edx":0}


    def get_available_register(self):
        for register, availability in self.register_dict.items():
            if availability == 0:
                return_value = register
                self.register_dict[register] = 1
                return return_value
        raise ValueError("No registers available")

    def release_register(self, register_name):
        self.register_dict.update({register_name:0})

    def release_all_registers(self):
        self.register_dict = {"eax":0,  "ebx": 0, "ecx":0, "edx":0}

