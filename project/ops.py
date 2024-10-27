from type import Type, Value

OP_TO_LAMBDA = {
    Type.INT: {
        "+": lambda x, y: Value(Type.INT, x.value() + y.value()),
        "-": lambda x, y: Value(Type.INT, x.value() - y.value()),
        "*": lambda x, y: Value(Type.INT, x.value() * y.value()),
        "/": lambda x, y: Value(Type.INT, x.value() // y.value()),
        "==": lambda x, y: Value(Type.BOOL, x.value() == y.value()),
        "!=": lambda x, y: Value(Type.BOOL, x.value() != y.value()),
        ">=": lambda x, y: Value(Type.BOOL, x.value() >= y.value()),
        "<=": lambda x, y: Value(Type.BOOL, x.value() <= y.value()),
        ">": lambda x, y: Value(Type.BOOL, x.value() > y.value()),
        "<": lambda x, y: Value(Type.BOOL, x.value() < y.value()),
        "neg": lambda x: Value(Type.INT, -x.value()),
    },
    Type.BOOL: {
        "==": lambda x, y: Value(Type.BOOL, x.value() == y.value()),
        "!=": lambda x, y: Value(Type.BOOL, x.value() != y.value()),
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
        "==": lambda x, y: Value(Type.BOOL, True),
        "!=": lambda x, y: Value(Type.BOOL, False),
    }
}
