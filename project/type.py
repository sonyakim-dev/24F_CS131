from enum import Enum, auto
from typing import Union

from intbase import InterpreterBase

class BasicType:
    INT = "int"
    BOOL = "bool"
    STRING = "string"
    NIL = "nil"
    VOID = "void"

class StructType:
    name: str
    def __eq__(self, other): # struct comparison
        if isinstance(other, StructType):
            return self.name == other.name
        return False

Type = Union[BasicType, StructType]

COERCION = {
    Type.INT: {
        Type.BOOL: lambda x: Value(BasicType.BOOL, x.value() != 0),
    },
}

# Represents a value, which has a type and its value
class Value:
    def __init__(self, type, value):
        self.t = type
        self.v = value

    def value(self):
        return self.v

    def type(self):
        return self.t
    
def create_value(val) -> Value:
    if val == InterpreterBase.TRUE_DEF:
        return Value(BasicType.BOOL, True)
    elif val == InterpreterBase.FALSE_DEF:
        return Value(BasicType.BOOL, False)
    elif isinstance(val, str):
        return Value(BasicType.STRING, val)
    elif isinstance(val, int):
        return Value(BasicType.INT, val)
    else:
        raise ValueError("Unknown value type")

def get_printable(val) -> str:
    t = val.type()
    if t == BasicType.INT:
        return str(val.value())
    if t == BasicType.STRING:
        return val.value()
    if t == BasicType.BOOL:
        return "true" if val.value() else "false"
    if isinstance(t, StructType) and val.value() is None:
        return "nil"
    raise ValueError("Not printable type")

def get_default_value(t: str) -> Value|None:
    match t:
        case BasicType.INT:
            return Value(BasicType.INT, 0)
        case BasicType.STRING:
            return Value(BasicType.STRING, "")
        case BasicType.BOOL:
            return Value(BasicType.BOOL, False)
        case BasicType.NIL | BasicType.VOID:
            return Value(BasicType.NIL, None)
        case "struct":
            return Value(t, None)
        case _:
            return None

class Statement:
    VAR_DEF = "vardef"
    ASSIGNMENT = "="
    FUNC_CALL = "fcall"
    IF_STATEMENT = "if"
    FOR_STATEMENT = "for"
    RETURN = "return"
    NEW = "new"

class Operator:
    UNA_OPS = {"neg", "!"}
    BIN_OPS = {"+", "-", "*", "/", ">=", "<=", ">", "<", "||", "&&", "==", "!="}
    
    OP_TO_LAMBDA = {
        Type.INT: {
            "+": lambda x, y: Value(BasicType.INT, x.value() + y.value()),
            "-": lambda x, y: Value(BasicType.INT, x.value() - y.value()),
            "*": lambda x, y: Value(BasicType.INT, x.value() * y.value()),
            "/": lambda x, y: Value(BasicType.INT, x.value() // y.value()),
            "==": lambda x, y: Value(BasicType.BOOL, x.type() == y.type() and x.value() == y.value()),
            "!=": lambda x, y: Value(BasicType.BOOL, x.type() != y.type() or x.value() != y.value()),
            ">=": lambda x, y: Value(BasicType.BOOL, x.value() >= y.value()),
            "<=": lambda x, y: Value(BasicType.BOOL, x.value() <= y.value()),
            ">": lambda x, y: Value(BasicType.BOOL, x.value() > y.value()),
            "<": lambda x, y: Value(BasicType.BOOL, x.value() < y.value()),
            "neg": lambda x: Value(BasicType.INT, -x.value()),
        },
        Type.BOOL: {
            "==": lambda x, y: Value(BasicType.BOOL, x.type() == y.type() and x.value() == y.value()),
            "!=": lambda x, y: Value(BasicType.BOOL, x.type() != y.type() or x.value() != y.value()),
            "||": lambda x, y: Value(BasicType.BOOL, x.value() or y.value()),
            "&&": lambda x, y: Value(BasicType.BOOL, x.value() and y.value()),
            "!": lambda x: Value(BasicType.BOOL, not x.value()),
        },
        Type.STRING: {
            "+": lambda x, y: Value(BasicType.STRING, x.value() + y.value()),
            "==": lambda x, y: Value(BasicType.BOOL, x.value() == y.value()),
            "!=": lambda x, y: Value(BasicType.BOOL, x.value() != y.value()),
        },
        Type.NIL: {
            "==": lambda x, y: Value(BasicType.BOOL, x.type() == y.type() and x.value() == y.value()),
            "!=": lambda x, y: Value(BasicType.BOOL, x.type() != y.type() or x.value() != y.value()),
        },
        Type.STRUCT: {
            "==": lambda x, y: Value(BasicType.BOOL, x.value() == y.value()),
            "!=": lambda x, y: Value(BasicType.BOOL, x.value() != y.value()),
        }
    }

class ExecStatus(Enum):
    CONTINUE = auto()
    RETURN = auto()
