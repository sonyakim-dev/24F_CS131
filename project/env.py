from intbase import ErrorType
from type import *


# The EnvironmentManager class keeps a mapping between each variable (aka symbol)
# in a brewin program and the value of that variable - the value that's passed in can be
# anything you like. In our implementation we pass in a Value object which holds a type
# and a value (e.g., Int, 10).
class EnvironmentManager:
    def __init__(self):
        self.environment = [[{}]] # [[{}], [{},{}], ...]

    def _find_scope(self, base_field: str) -> dict | None:
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
            if scope.type() == BasicType.NIL: # nil check
                return None, '', ErrorType.FAULT_ERROR

            scope = scope.value() # step into the next scope
            if scope is None: # nil check
                return None, '', ErrorType.FAULT_ERROR
            if not isinstance(scope, dict): # struct type check
                return None, '', ErrorType.TYPE_ERROR

        return scope, fields[-1], None

    # Gets the data associated a variable name
    def get(self, symbol: str) -> Value | ErrorType:
        scope, field, error = self._traverse_scope(symbol)
        if error is not None: return error

        val = scope.get(field)
        return val if val is not None else ErrorType.NAME_ERROR

    # Assign a value to a variable name
    def assign(self, symbol: str, value: Value) -> ErrorType|None:
        scope, field, error = self._traverse_scope(symbol)
        if error is not None: return error

        scope[field] = value

    # Variable declaration
    def create(self, symbol: str, val: Value=None) -> bool:
        if val is None: val = Value(BasicType.NIL, None) # default value
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


    def _print(self, env_name='ENV'):
        print(f"{'=' * 5} {env_name:^12} {'=' * 5}")
        for env in reversed(self.environment[-1]):
            for key, item in env.items():
                self._print_value(key, item)
            print(f"{'-' * 24}")
        print(f"{'=' * 24}")

    def _print_value(self, key, item, indent=0):
        if item and isinstance(item.value(), dict):
            print(f"|{' ' * indent}  {key:<6}:")
            for sub_key, sub_item in item.value().items():
                self._print_value(sub_key, sub_item, indent + 2)
        elif isinstance(item, Value):
            print(f"|{' ' * indent}  {key:<6}: {item.type()} {str(item.value()):<{max(0, 10-indent)}}|")
