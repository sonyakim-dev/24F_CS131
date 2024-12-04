from element import Element
from copy import copy

class Closure:
    def __init__(self, expr: Element, scope: list[dict] = None):
        if scope is None:
            scope = [{}]
        self._expr = expr
        self._scope = copy(scope)

    @property
    def expr(self):
        return self._expr

    @property
    def scope(self):
        return self._scope

    def add_scope(self, var_name: str, expr):
        self._scope[-1][var_name] = expr
    
    def get_scope(self, var_name: str):
        return self._scope[-1][var_name]
