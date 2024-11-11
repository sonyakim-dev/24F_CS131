from type import Type, Value


# The EnvironmentManager class keeps a mapping between each variable (aka symbol)
# in a brewin program and the value of that variable - the value that's passed in can be
# anything you like. In our implementation we pass in a Value object which holds a type
# and a value (e.g., Int, 10).
class EnvironmentManager:
    def __init__(self):
        self.environment = [[{}]] # [[{}], [{},{}], ...]

    # Gets the data associated a variable name
    def get(self, symbol: str) -> Value | None:
        curr_env = self.environment[-1]
        for env in reversed(curr_env):
            if symbol in env:
                return env[symbol]
        return None

    # assign a value to a variable name
    def assign(self, symbol: str, value: Value) -> bool:
        curr_env = self.environment[-1]
        for env in reversed(curr_env):
            if symbol in env:
                env[symbol] = value
                return True
        return False # variable not exist

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
        print(f"{'=' * 4} {env_name:^10} {'=' * 4}")
        for key, item in reversed(self.environment[-1]):
            print(f"|  {key:<5}: {item.value():<10}|")
        print(f"{'=' * 20}")
        # if self.enclosing:
        #     print(f"| 👉 {'Enclosing':<10}|")
        #     self.enclosing._print()
        # print(f"| 👉 {'Local':<14} |")
        # for key, item in self.environment.items():
        #     print(f"|  {key:<5}: {item.value():<10}|")
        # print(f"{'=' * 20}")