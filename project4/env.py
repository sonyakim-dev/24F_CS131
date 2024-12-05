from type import *
from closure import Closure


class EnvironmentManager:
    """ The EnvironmentManager class keeps a mapping between each variable (aka symbol) in a Brewin program and the value of that variable """
    def __init__(self):
        self.environment = []  # [[{}], [{},{}], ...]

    def assign(self, symbol: str, val: Value) -> bool:
        """ Assign a value to a variable name. """
        curr_env = self.environment[-1]
        for env in reversed(curr_env):
            if symbol in env:
                env[symbol] = val
                return True
        return False  # variable not exist

    def create(self, symbol: str, val: Value = None) -> bool:
        """ Declare a variable at the top environment with a given value. Return False if the variable already exists. """
        if val is None: val = create_value(Type.NIL)  # default value
        curr_env = self.environment[-1][-1]
        if symbol not in curr_env:
            curr_env[symbol] = val
            return True
        return False  # variable already declared

    def get_current_env(self):
        return self.environment[-1]

    def push_env(self):
        self.environment.append([{}])

    def pop_env(self):
        self.environment.pop()

    def push_block(self):
        self.environment[-1].append({})

    def pop_block(self):
        self.environment[-1].pop()
