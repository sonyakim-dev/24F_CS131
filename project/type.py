from intbase import InterpreterBase


# Enumerated type for our different language data types
class Type:
    INT = "int"
    BOOL = "bool"
    STRING = "string"
    NIL = "nil"
    VARIABLE = "var"

# Represents a value, which has a type and its value
class Value:
    def __init__(self, type, value=None):
        self.t = type
        self.v = value

    def value(self):
        return self.v

    def type(self):
        return self.t
    
def create_value(val):
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

def get_printable(val):
    match val.type():
        case Type.INT:
            return str(val.value())
        case Type.STRING:
            return val.value()
        case Type.BOOL:
            return "true" if val.value() else "false"
        case _: #FIXME:
            raise ValueError("Not printable type")

class Statement:
    VAR_DEF = "vardef"
    ASSIGNMENT = "="
    FUNC_CALL = "fcall"
    IF_STATEMENT = "if"
    FOR_STATEMENT = "for"
    RETURN = "return"
