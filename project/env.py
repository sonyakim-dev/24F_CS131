from intbase import ErrorType
from type import Type, Value


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

    # Gets the data associated a variable name
    def get(self, symbol: str) -> Value | ErrorType:
        fields = symbol.split('.')
        scope = self._find_scope(fields[0])
        if scope is None: # variable not found
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
        curr_val = self.get(symbol)
        if isinstance(curr_val, ErrorType): return curr_val

        if isinstance(curr_val.value(), dict): # if it is a struct
            final_field = symbol.split('.')[-1]
            final_value = curr_val.value()
            if final_field not in final_value:
                return ErrorType.NAME_ERROR
            final_value[final_field] = value
        else: # if it is a variable
            curr_val.v = value.v

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
        # else:
        #     print(f"|{' ' * indent}  {key:<6}: {str(item):<{10 - indent}}|")
