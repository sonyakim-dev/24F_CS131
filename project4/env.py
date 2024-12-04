from type import *
from closure import Closure


class EnvironmentManager:
    """ The EnvironmentManager class keeps a mapping between each variable (aka symbol) in a Brewin program and the value of that variable """
    def __init__(self):
        self.environment = []  # [[{}], [{},{}], ...]

    def get(self, symbol: str) -> Value|Closure|None:
        """ Get the data associated a variable name. """
        curr_env = self.environment[-1]
        for env in reversed(curr_env):
            if symbol in env:
                return env[symbol]
        return None

    def assign(self, symbol: str, val: Value|Closure) -> bool:
        """ Assign a value to a variable name. """
        curr_env = self.environment[-1]
        for env in reversed(curr_env):
            if symbol in env:
                env[symbol] = val
                return True
        return False  # variable not exist

    def create(self, symbol: str, val: Value|Closure = None) -> bool:
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


    # def print(self, env_name='ENV'):
    #     print(f"{'=' * 6} {env_name:^12} {'=' * 6}")
    #     for env in reversed(self.environment[-1]):
    #         for key, item in env.items():
    #             self.__print_value(key, item)
    #         print(f"{'-' * 26}")
    #     print(f"{'=' * 26}")
    #
    # def __print_value(self, key, item, indent=0):
    #     print(f"|{' ' * indent}  {key:<6}: {item.type} {str(item.value):<{max(0, 12-indent)}}|")
