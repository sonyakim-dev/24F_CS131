from ctypes.wintypes import BOOL
from pickle import FALSE, TRUE


class NODE_TYPE:
    PROGRAM = "program"
    FUNCTION = "func"
    
    VAR_DEF = "vardef"
    ASSIGNMENT = "="
    FUNC_CALL = "fcall"
    IF_STATEMENT = "if"
    FOR_STATEMENT = "for"

    ADDITION = "+"
    SUBTRACTION = "-"
    MULTIPLICATION = "*"
    DIVISION = "/"
    
    EQ = "=="
    NE = "!="
    GE = ">="
    LE = "<="
    GT = ">"
    LT = "<"
    
    NOT = "!"
    NEG = "neg"

    VARIABLE = "var"
    INT_VALUE = "int"
    STRING_VALUE = "string"
    BOOL_VALUE = "bool"
    TRUE_VALUE = "True"
    FALSE_VALUE = "False"
    NIL_VALUE = "nil"
    
    RETURN = "return"
    
