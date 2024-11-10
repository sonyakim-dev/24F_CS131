from enum import Enum, auto
from intbase import InterpreterBase


# Enumerated type for our different language data types
class Type:
    INT = "int"
    BOOL = "bool"
    STRING = "string"
    NIL = "nil"
    VARIABLE = "var"
    VOID = "void"
    STRUCT = "struct"

PRIMITIVE_TYPES = { Type.INT, Type.STRING, Type.BOOL, Type.NIL }

# Represents a value, which has a type and its value
class Value:
    def __init__(self, type, value, struct_name=None):
        self.t = type
        self.v = value
        self.n = struct_name

    def value(self):
        return self.v

    def type(self):
        return self.t

    def name(self):
        return self.n if self.t == Type.STRUCT else None
    
def create_value(val) -> Value:
    if val == InterpreterBase.TRUE_DEF:
        return Value(Type.BOOL, True)
    elif val == InterpreterBase.FALSE_DEF:
        return Value(Type.BOOL, False)
    elif isinstance(val, str):
        return Value(Type.STRING, val)
    elif isinstance(val, int):
        return Value(Type.INT, val)
    else:
        raise ValueError("Unknown value type")

def get_printable(val) -> str:
    # type = val.type()
    # if type == Type.INT:
    #     return str(val.value())
    # if type == Type.STRING:
    #     return val.value()
    # if type == Type.BOOL:
    #     return "true" if val.value() else "false"
    # if type == Type.NIL:
    #     return "nil"
    # if type == Type.STRUCT:
    #     return val.name()
    match val.type():
        case Type.INT:
            return str(val.value())
        case Type.STRING:
            return val.value()
        case Type.BOOL:
            return "true" if val.value() else "false"
        case _:
            raise ValueError("Not printable type")

def get_default_value(t: str, struct_name: str=None) -> Value|None:
    match t:
        case Type.INT:
            return Value(Type.INT, 0)
        case Type.STRING:
            return Value(Type.STRING, "")
        case Type.BOOL:
            return Value(Type.BOOL, False)
        case Type.NIL:
            return Value(Type.NIL, None)
        case Type.VOID:
            return Value(Type.NIL, None)
        case Type.STRUCT:
            return Value(Type.STRUCT, None, struct_name)
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
            "+": lambda x, y: Value(Type.INT, x.value() + y.value()),
            "-": lambda x, y: Value(Type.INT, x.value() - y.value()),
            "*": lambda x, y: Value(Type.INT, x.value() * y.value()),
            "/": lambda x, y: Value(Type.INT, x.value() // y.value()),
            "==": lambda x, y: Value(Type.BOOL, x.type() == y.type() and x.value() == y.value()),
            "!=": lambda x, y: Value(Type.BOOL, x.type() != y.type() or x.value() != y.value()),
            ">=": lambda x, y: Value(Type.BOOL, x.value() >= y.value()),
            "<=": lambda x, y: Value(Type.BOOL, x.value() <= y.value()),
            ">": lambda x, y: Value(Type.BOOL, x.value() > y.value()),
            "<": lambda x, y: Value(Type.BOOL, x.value() < y.value()),
            "neg": lambda x: Value(Type.INT, -x.value()),
        },
        Type.BOOL: {
            "==": lambda x, y: Value(Type.BOOL, x.type() == y.type() and x.value() == y.value()),
            "!=": lambda x, y: Value(Type.BOOL, x.type() != y.type() or x.value() != y.value()),
            "||": lambda x, y: Value(Type.BOOL, x.value() or y.value()),
            "&&": lambda x, y: Value(Type.BOOL, x.value() and y.value()),
            "!": lambda x: Value(Type.BOOL, not x.value()),
        },
        Type.STRING: {
            "+": lambda x, y: Value(Type.STRING, x.value() + y.value()),
            "==": lambda x, y: Value(Type.BOOL, x.value() == y.value()),
            "!=": lambda x, y: Value(Type.BOOL, x.value() != y.value()),
        },
        Type.NIL: {
            "==": lambda x, y: Value(Type.BOOL, x.type() == y.type() and x.value() == y.value()),
            "!=": lambda x, y: Value(Type.BOOL, x.type() != y.type() or x.value() != y.value()),
        },
        Type.STRUCT: {
            "==": lambda x, y: Value(Type.BOOL, x.value() == y.value()),
            "!=": lambda x, y: Value(Type.BOOL, x.value() != y.value()),
        }
    }

class ExecStatus(Enum):
    CONTINUE = auto()
    RETURN = auto()
