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
    def get(self, symbol: str) -> Value | None:
        curr_env = self.environment[-1]
        fields = symbol.split('.')
        curr_val = self._find_scope(fields[0])

        if curr_val is None: return None
        # find the scope where the variable is declared
        for env in reversed(curr_env):
            if fields[0] in env:
                curr_val = env[fields[0]]
                break
        if curr_val is None: return None

        for field in fields[1:]:
            val_value = curr_val.value()
            if not isinstance(val_value, dict) or field not in val_value:
                return None
            curr_val = val_value[field]
        return curr_val

    # assign a value to a variable name
    def assign(self, symbol: str, value: Value) -> bool:
        curr_env = self.environment[-1]
        fields = symbol.split('.')
        base_field = fields[0]
        curr_val = None

        # find the scope where the base variable is declared
        for env in reversed(curr_env):
            if base_field in env:
                curr_val = env[base_field]
                break
        if curr_val is None: return False

        # traverse nested fields up to the second-to-last field
        for field in fields[1:-1]:
            val_value = curr_val.value()
            if not isinstance(val_value, dict) or field not in val_value:
                return False
            curr_val = val_value[field]

        # assign value
        if isinstance(curr_val.value(), dict):
            final_field = fields[-1]
            final_value = curr_val.value()
            if final_field not in final_value:
                return False
            final_value[final_field] = value
        else:
            curr_val.v = value.v

        return True

    # variable declaration
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
        else:
            print(f"|{' ' * indent}  {key:<6}: {str(item):<{10 - indent}}|")
