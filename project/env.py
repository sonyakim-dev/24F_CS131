from intbase import ErrorType
from type import BasicType, StructType, Type, Value


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
            if isinstance(scope.type(), BasicType.NIL): # nil check
                return None, '', ErrorType.FAULT_ERROR

            scope = scope.value() # step into the next scope
            if not isinstance(scope, dict): # struct type check
                return None, '', ErrorType.TYPE_ERROR
            """
            If the variable to the left of a dot is not a struct type, then you must generate an error of ErrorType.TYPE_ERROR.
            If the variable to the left of a dot is nil, then you must generate an error of ErrorType.FAULT_ERROR.
            If a field name is invalid (e.g., it's not a valid field in a struct definition), then you must generate an error of ErrorType.NAME_ERROR.
            """
        return scope, fields[-1], None

    # Gets the data associated a variable name
    def get(self, symbol: str) -> Value | ErrorType:
        fields = symbol.split('.')
        scope = self._find_scope(fields[0])

        if scope is None: # base variable not in scope
            return ErrorType.NAME_ERROR

        curr_val = scope[fields[0]]
        # traverse nested fields
        for field in fields[1:]:
            val_value: dict|Value = curr_val.value()

            if val_value is None: # check for nil
                return ErrorType.FAULT_ERROR
            if not isinstance(val_value, dict): # check for struct
                return ErrorType.TYPE_ERROR
            if field not in val_value: # check for field
                return ErrorType.NAME_ERROR
            """ NOTE:
            If the variable to the left of a dot is not a struct type, then you must generate an error of ErrorType.TYPE_ERROR.
            If the variable to the left of a dot is nil, then you must generate an error of ErrorType.FAULT_ERROR.
            If a field name is invalid (e.g., it's not a valid field in a struct definition), then you must generate an error of ErrorType.NAME_ERROR.
            """
            curr_val = val_value[field]

        return curr_val

    # Assign a value to a variable name
    def assign(self, symbol: str, value: Value) -> ErrorType|None:
        fields = symbol.split('.')
        scope = self._find_scope(fields[0])

        if scope is None: # base variable not in scope
            return ErrorType.NAME_ERROR

        # traverse nested fields up to the second-to-last field
        for i in range(len(fields) - 1):
            field = fields[i]
            if field not in scope:  # field existence check
                return ErrorType.NAME_ERROR

            scope = scope.get(field)
            if scope is None:  # nil check
                return ErrorType.FAULT_ERROR

            scope = scope.value() # step into the next scope
            if not isinstance(scope, dict): # struct type check
                return ErrorType.TYPE_ERROR

        # assign the value to the final field
        final_field = fields[-1]
        scope[final_field] = value

        return None

    # Variable declaration
    def create(self, symbol: str, val: Value=None) -> bool:
        if val is None: val = Value(Type.NIL, None) # default value
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
            print(f"|{' ' * indent}  {key:<6}: {item.type()} {str(item.value()):<{10 - indent}}|")
