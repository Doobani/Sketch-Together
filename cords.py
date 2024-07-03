def string_to_tuple(input_string):
    # Strip the parentheses from the string
    stripped_string = input_string.strip('()')

    # Split the stripped string by comma
    components = stripped_string.split(',')

    # Convert each component to an integer
    tuple_values = tuple(int(component.strip()) for component in components)

    return tuple_values


class Cords:

    def __init__(self, tup_str):
        self.tup = tuple(string_to_tuple(tup_str)) #Has the values as a tuple
        self.x = int(self.tup[0])
        self.y = int(self.tup[1])
