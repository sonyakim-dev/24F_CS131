from intbase import ErrorType
from type import *

class EnvironmentManager:
    """ The EnvironmentManager class keeps a mapping between each variable (aka symbol) in a Brewin program and the value of that variable """
    def __init__(self):
        self.environment = [[{}]] # [[{}], [{},{}], ...]

    def _find_scope(self, base_field: str) -> dict|None:
        for env in reversed(self.environment[-1]):
            if base_field in env:
                return env
        return None

    def _traverse_scope(self, symbol: str) -> tuple[dict|None, str, ErrorType|None]:
        fields = symbol.split('.')
        scope = self._find_scope(fields[0])

        if scope is None:
            return None, '', ErrorType.NAME_ERROR

        # traverse nested fields up to the second-to-last field
        for field in fields[:-1]:
            if field not in scope: # field existence check
                return None, '', ErrorType.NAME_ERROR

            scope = scope.get(field)
            if scope.type == BasicType.NIL: # nil check
                return None, '', ErrorType.FAULT_ERROR

            scope = scope.value # step into the next scope
            if scope is None: # nil check
                return None, '', ErrorType.FAULT_ERROR
            if not isinstance(scope, dict): # struct type check
                return None, '', ErrorType.TYPE_ERROR

        return scope, fields[-1], None

    def get(self, symbol: str) -> Value|ErrorType:
        """ Gets the data associated a variable name. Return ErrorType if the variable does not exist. """
        scope, field, error = self._traverse_scope(symbol)
        if error is not None: return error

        val = scope.get(field)
        return val if val is not None else ErrorType.NAME_ERROR

    def assign(self, symbol: str, value: Value) -> ErrorType|None:
        """ Assign a value to a variable name. Return ErrorType if the variable does not exist. """
        scope, field, error = self._traverse_scope(symbol)
        if error is not None: return error

        scope[field] = value

    def create(self, symbol: str, val: Value) -> bool:
        """ Declare a variable at the top environment with a given value. Return False if the variable already exists. """
        # if val is None: val = Value(BasicType.NIL, None) # v3 must declare type in a variable declaration
        curr_env = self.environment[-1][-1]
        if symbol not in curr_env:
            curr_env[symbol] = val
            return True
        return False # variable already declared

    def push_env(self):
        self.environment.append([{}])

    def pop_env(self):
        self.environment.pop()

    def push_block(self):
        self.environment[-1].append({})

    def pop_block(self):
        self.environment[-1].pop()


    def print(self, env_name='ENV'):
        print(f"{'=' * 6} {env_name:^12} {'=' * 6}")
        for env in reversed(self.environment[-1]):
            for key, item in env.items():
                self.__print_value(key, item)
            print(f"{'-' * 26}")
        print(f"{'=' * 26}")

    def __print_value(self, key, item, indent=0):
        if item and isinstance(item.value, dict):
            print(f"|{' ' * indent}  {key:<6}:")
            for sub_key, sub_item in item.value.items():
                self.__print_value(sub_key, sub_item, indent + 2)
        elif isinstance(item, Value):
            print(f"|{' ' * indent}  {key:<6}: {item.type} {str(item.value):<{max(0, 12-indent)}}|")
