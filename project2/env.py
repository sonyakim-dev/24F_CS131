from type import Type, Value


# The EnvironmentManager class keeps a mapping between each variable (aka symbol)
# in a brewin program and the value of that variable - the value that's passed in can be
# anything you like. In our implementation we pass in a Value object which holds a type
# and a value (e.g., Int, 10).
class EnvironmentManager:
    def __init__(self, enclosing=None):
        self.environment = {}
        self.enclosing = enclosing # parent environment

    # Gets the data associated a variable name
    def get(self, symbol: str) -> Value | None:
        if symbol in self.environment:
            return self.environment[symbol]
        if self.enclosing:
            return self.enclosing.get(symbol)
        return None

    # assign a value to a variable name
    def assign(self, symbol: str, value: Value) -> bool:
        if symbol in self.environment:
            self.environment[symbol] = value
            return True
        if self.enclosing:
            self.enclosing.assign(symbol, value)
            return True
        return False

    # variable declaration
    def create(self, symbol: str, val: None) -> bool:
        if val is None: val = Value(Type.NIL, None)
        if symbol not in self.environment:
            self.environment[symbol] = val
            return True
        return False
    
    def begin_scope(self):
        return EnvironmentManager(self)
    
    def end_scope(self):
        return self.enclosing if self.enclosing else self

    def _print(self, env_name='ENV'):
        print(f"{'=' * 4} {env_name:^10} {'=' * 4}")
        if self.enclosing:
            print(f"| 👉 {'Enclosing':<10}|")
            self.enclosing._print()
        print(f"| 👉 {'Local':<14} |")
        for key, item in self.environment.items():
            print(f"|  {key:<5}: {item.value():<10}|")
        print(f"{'=' * 20}")
