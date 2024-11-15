from enum import Enum, auto
from typing import Any, Union, Optional


class BasicType(Enum):
    INT = "int"
    BOOL = "bool"
    STRING = "string"
    NIL = "nil"
    VOID = "void"

    @classmethod
    def contains(cls, other): # Python v3.11 Enum does not support 'in' operation
        """ Check if the type is BasicType """
        return any(other == item.value for item in cls)
    def __str__(self):  # debug print
        return self.value

class StructType:
    STRUCT = "struct"
    def __init__(self, name):
        self.name = name
    def __eq__(self, other):  # struct comparison (can be used to for both equality and inequality)
        if isinstance(other, StructType):
            return self.name == other.name
        return False
    def __hash__(self):
        return hash("struct")
    def __str__(self):  # debug print
        return self.name

Type = Union[BasicType, StructType]
VarType = {BasicType.INT.value, BasicType.BOOL.value, BasicType.STRING.value}
FuncType = {BasicType.INT.value, BasicType.BOOL.value, BasicType.STRING.value, BasicType.VOID.value}

# Represents a value, which has a type and its value
class Value:
    def __init__(self, type, value):
        self.t = type
        self.v = value

    def value(self):
        return self.v

    def type(self):
        return self.t

COERCION = {
    BasicType.INT: {
        BasicType.BOOL: lambda x: Value(BasicType.BOOL, x.value() != 0),
    },
}
COERCION_PRIORITY = { # e.g. 1 == true; 1 is converted to bool, not vice versa
    BasicType.INT: 1,
    BasicType.BOOL: 2
}

def try_conversion(old: Value, new: Value) -> tuple[Value, Value]:
    # NIL to STRUCT; in case assigning nil to struct type var (e.g. var s: struct; s = nil;)
    if old.type() == BasicType.NIL and isinstance(new.type(), StructType):
        return Value(new.type(), None), new
    if isinstance(old.type(), StructType) and new.type() == BasicType.NIL:
        return old, Value(old.type(), None)

    # basic type coercion
    if isinstance(old.type(), BasicType) and isinstance(new.type(), BasicType)\
            and old.type() in COERCION and new.type() in COERCION[old.type()]:
        return COERCION[old.type()][new.type()](old), new

    return old, new

def coercion_by_priority(lhs: Value, rhs: Value) -> tuple[Value, Value]:
    lhs_priority = COERCION_PRIORITY.get(lhs.type(), 10)
    rhs_priority = COERCION_PRIORITY.get(rhs.type(), 10)

    if lhs_priority > rhs_priority:
        return try_conversion(rhs, lhs)
    elif lhs_priority < rhs_priority:
        return try_conversion(lhs, rhs)
    else:
        return lhs, rhs

def normalize_struct(val: Value) -> Value:
    """ If a struct is not initialized (value is None), then return NIL Value. """
    return Value(BasicType.NIL, None) \
        if isinstance(val.type(), StructType) and val.value() is None else val

def create_value(t: Type, v: Optional[Any] = None) -> Value|None:
    """ Return a Value object with the given Type and value. If value is not provided, then return default value. """
    if t == BasicType.INT:
        return Value(BasicType.INT, 0 if v is None else v)
    if t == BasicType.STRING:
        return Value(BasicType.STRING, "" if v is None else v)
    if t == BasicType.BOOL:
        return Value(BasicType.BOOL, False if v is None else v)
    if t == BasicType.NIL:
        return Value(BasicType.NIL, None)
    if t == BasicType.VOID:
        return Value(BasicType.VOID, None)
    if isinstance(t, StructType):
        return Value(t, None if v is None else v)
    raise ValueError(f"Invalid type: {t}")

def get_printable(val: Value) -> str|None:
    t = val.type()
    if t == BasicType.INT:
        return str(val.value())
    if t == BasicType.STRING:
        return val.value()
    if t == BasicType.BOOL:
        return "true" if val.value() else "false"
    if isinstance(t, StructType) and val.value() is None:
        return "nil"
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
    EQ_OPS = {"==", "!="}
    LOG_OPS = {"||", "&&"}
    COMP_OPS = {">=", "<=", ">", "<"}
    BIN_OPS = {"+", "-", "*", "/", ">=", "<=", ">", "<", "||", "&&", "==", "!="}

    OP_TO_LAMBDA = {
        BasicType.INT: {
            "==": lambda x, y: Value(BasicType.BOOL, x.type() == y.type() and x.value() == y.value()),
            "!=": lambda x, y: Value(BasicType.BOOL, x.type() != y.type() or x.value() != y.value()),
            "+": lambda x, y: Value(BasicType.INT, x.value() + y.value()),
            "-": lambda x, y: Value(BasicType.INT, x.value() - y.value()),
            "*": lambda x, y: Value(BasicType.INT, x.value() * y.value()),
            "/": lambda x, y: Value(BasicType.INT, x.value() // y.value()),
            ">=": lambda x, y: Value(BasicType.BOOL, x.value() >= y.value()),
            "<=": lambda x, y: Value(BasicType.BOOL, x.value() <= y.value()),
            ">": lambda x, y: Value(BasicType.BOOL, x.value() > y.value()),
            "<": lambda x, y: Value(BasicType.BOOL, x.value() < y.value()),
            "neg": lambda x: Value(BasicType.INT, -x.value()),
        },
        BasicType.BOOL: {
            "==": lambda x, y: Value(BasicType.BOOL, x.type() == y.type() and x.value() == y.value()),
            "!=": lambda x, y: Value(BasicType.BOOL, x.type() != y.type() or x.value() != y.value()),
            "||": lambda x, y: Value(BasicType.BOOL, x.value() or y.value()),
            "&&": lambda x, y: Value(BasicType.BOOL, x.value() and y.value()),
            "!": lambda x: Value(BasicType.BOOL, not x.value()),
        },
        BasicType.STRING: {
            "==": lambda x, y: Value(BasicType.BOOL, x.value() == y.value()),
            "!=": lambda x, y: Value(BasicType.BOOL, x.value() != y.value()),
            "+": lambda x, y: Value(BasicType.STRING, x.value() + y.value()),
        },
        BasicType.NIL: {
            "==": lambda x, y: Value(BasicType.BOOL, x.type() == y.type() and x.value() == y.value()),
            "!=": lambda x, y: Value(BasicType.BOOL, x.type() != y.type() or x.value() != y.value()),
        },
        StructType.STRUCT: {
            "==": lambda x, y: Value(BasicType.BOOL,
                x.type() == y.type() and id(x.value()) == id(y.value())
                if isinstance(y.type(), StructType) else x.value() == y.value()),
            "!=": lambda x, y: Value(BasicType.BOOL,
                x.type() != y.type() or id(x.value()) != id(y.value())
                if isinstance(y.type(), StructType) else x.value() != y.value()),
        }
    }

class ExecStatus(Enum):
    CONTINUE = auto()
    RETURN = auto()
