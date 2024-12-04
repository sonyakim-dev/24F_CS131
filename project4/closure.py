from element import Element

class Closure:
    def __init__(self, expr: Element):
        self._expr = expr
        self._scope = [{}]

    @property
    def expr(self):
        return self._expr

    @property
    def scope(self):
        return self._scope

    def add_scope(self, var_name: str, expr):
        self._scope[-1][var_name] = expr
