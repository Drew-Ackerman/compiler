class Array(object):

    def __init__(self, lower_bounds, upper_bounds):

        self.lower_bounds = lower_bounds
        self.upper_bounds = upper_bounds

        self.k_values = []
        self.array_size = 1
        self.mapping_values = []
        self.relocation_factor = 0

    def create_array(self):
        self.calc_k_values()
        self.calc_array_size()
        self.calc_mapping_values()
        self.calc_relocation_factor()

    def calc_k_values(self):
        for lower_bound, upper_bound in zip(self.lower_bounds, self.upper_bounds):
            self.k_values.append(upper_bound-lower_bound+1)

    def calc_array_size(self):
        for k in self.k_values:
            self.array_size *= k

    def calc_mapping_values(self):
        total_k_len = len(self.k_values)

        self.mapping_values.append(1)

        for x in range(total_k_len, 1, -1):
            self.mapping_values.append(self.mapping_values[-1] * self.k_values[x - 1])
        self.mapping_values.reverse()

    def calc_relocation_factor(self):
        # Calculate the relocation factor
        for lower_bound, mapping_value in zip(self.lower_bounds, self.mapping_values):
            self.relocation_factor += (lower_bound*mapping_value)

    def calculate_offset(self, list_of_numbers):
        offset = 0
        for value, delta_value in zip(list_of_numbers, self.mapping_values):
            offset += value*delta_value
        return offset
