from enum import Enum, auto
from typing import Optional, Any


class Type:
    INT = "int"
    BOOL = "bool"
    STRING = "string"
    NIL = "nil"
    CLOSURE = "closure"

# Represents a value, which has a type and its value
class Value:
    def __init__(self, type: str, value: Any):
        self._t = type
        self._v = value # value can be a closure object
    @property
    def value(self):
        return self._v
    @value.setter
    def value(self, v):
        self._v = v
    @property
    def type(self):
        return self._t
    @type.setter
    def type(self, t):
        self._t = t

def create_value(t: str, v: Optional[Any] = None) -> Value|None:
    """ Return a Value object with the given Type and value. If value is not provided, then return default value. """
    match t:
        case Type.INT:
            return Value(Type.INT, 0 if v is None else v)
        case Type.STRING:
            return Value(Type.STRING, "" if v is None else v)
        case Type.BOOL:
            return Value(Type.BOOL, False if v is None else v)
        case Type.NIL:
            return Value(Type.NIL, None)
        case Type.CLOSURE:
            return Value(Type.CLOSURE, v)
    raise ValueError(f"Invalid type: {t}")

def get_printable(val: Value) -> str|None:
    match val.type:
        case Type.INT:
            return str(val.value)
        case Type.STRING:
            return val.value
        case Type.BOOL:
            return "true" if val.value else "false"
    return None

class Statement:
    VAR_DEF = "vardef"
    VAR = "var"
    ASSIGNMENT = "="
    FUNC_CALL = "fcall"
    IF_STATEMENT = "if"
    FOR_STATEMENT = "for"
    RETURN = "return"
    NEW = "new"
    TRY = "try"
    RAISE = "raise"
    CATCH = "catch"

UnaryOps = {"neg", "!"}
EqualOps = {"==", "!="}
BinaryOps = {"+", "-", "*", "/", ">=", "<=", ">", "<", "||", "&&", "==", "!="}

OP_TO_LAMBDA = {
    Type.INT: {
        "==": lambda x, y: Value(Type.BOOL, x.type == y.type and x.value == y.value),
        "!=": lambda x, y: Value(Type.BOOL, x.type != y.type or x.value != y.value),
        "+": lambda x, y: Value(Type.INT, x.value + y.value),
        "-": lambda x, y: Value(Type.INT, x.value - y.value),
        "*": lambda x, y: Value(Type.INT, x.value * y.value),
        "/": lambda x, y: Value(Type.INT, x.value // y.value),
        ">=": lambda x, y: Value(Type.BOOL, x.value >= y.value),
        "<=": lambda x, y: Value(Type.BOOL, x.value <= y.value),
        ">": lambda x, y: Value(Type.BOOL, x.value > y.value),
        "<": lambda x, y: Value(Type.BOOL, x.value < y.value),
        "neg": lambda x: Value(Type.INT, -x.value),
    },
    Type.BOOL: {
        "==": lambda x, y: Value(Type.BOOL, x.type == y.type and x.value == y.value),
        "!=": lambda x, y: Value(Type.BOOL, x.type != y.type or x.value != y.value),
        "||": lambda x, y: Value(Type.BOOL, x.value or y.value),
        "&&": lambda x, y: Value(Type.BOOL, x.value and y.value),
        "!": lambda x: Value(Type.BOOL, not x.value),
    },
    Type.STRING: {
        "==": lambda x, y: Value(Type.BOOL, x.type == y.type and x.value == y.value),
        "!=": lambda x, y: Value(Type.BOOL, x.type != y.type or x.value != y.value),
        "+": lambda x, y: Value(Type.STRING, x.value + y.value),
    },
    Type.NIL: {
        "==": lambda x, y: Value(Type.BOOL, x.type == y.type and x.value == y.value),
        "!=": lambda x, y: Value(Type.BOOL, x.type != y.type or x.value != y.value),
    },
}

def get_operator_lambda(t: Type, op: str) -> callable:
    return OP_TO_LAMBDA.get(t, {}).get(op)

class ExecStatus(Enum):
    CONTINUE = auto()
    RETURN = auto()
    RAISE = auto()
