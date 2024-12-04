from brewparse import parse_program
from element import Element
from env import EnvironmentManager
from intbase import ErrorType, InterpreterBase
from type import *


class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.trace_output = trace_output  # debug purpose
        self.env = EnvironmentManager()  # store variables
        self.func_table: dict[tuple[str, int], Element] = {}  # key: (func name, arg count)

    def run(self, program) -> None:
        ast = parse_program(program)  # generate Abstract Syntax Tree of the program
        self.__set_function_table(ast)
        main_func = self.__get_func_by_name(("main", 0))
        result, state = self.__call_func(main_func, [{}])
        if state == ExecStatus.RAISE:
            super().error(ErrorType.FAULT_ERROR, f"Unhandled exception {result.value}")

    def __set_function_table(self, ast: Element) -> None:
        for func_node in ast.get("functions"):
            func_name = func_node.get("name")
            if func_name in self.func_table:
                super().error(ErrorType.NAME_ERROR, f"Function {func_name} defined more than once")

            self.func_table[(func_name, len(func_node.get("args")))] = func_node

    def __get_func_by_name(self, func_key: tuple[str, int]) -> Element:
        if func_key not in self.func_table:
            super().error(ErrorType.NAME_ERROR, f"Function {func_key[0]} not found")

        return self.func_table[func_key]

    def __run_statements(self, statement_nodes: list[Element]) -> tuple[Value, ExecStatus]:
        for statement in statement_nodes:
            if self.trace_output: print(" 👩‍💻 ", statement)  # debug

            category = statement.elem_type
            match category:
                case Statement.VAR_DEF:
                    self.__var_def(statement)
                case Statement.ASSIGNMENT:
                    self.__assign(statement, self.env.get_current_env())
                case Statement.FUNC_CALL:  # standalone function call (e.g. print();)
                    result, ret = self.__call_func(statement, self.env.get_current_env())
                    if ret == ExecStatus.RAISE:
                        return result, ret
                case Statement.IF_STATEMENT:
                    result, ret = self.__call_if(statement, self.env.get_current_env())
                    if ret != ExecStatus.CONTINUE:
                        return result, ret
                case Statement.FOR_STATEMENT:
                    result, ret = self.__call_for(statement, self.env.get_current_env())
                    if ret != ExecStatus.CONTINUE:
                        return result, ret
                case Statement.TRY:
                    result, ret = self.__call_try(statement)
                    if ret != ExecStatus.CONTINUE:
                        return result, ret
                case Statement.RAISE:
                    result, _ = self.__force_eval(statement.get("exception_type"), self.env.get_current_env())
                    if result.type != Type.STRING:
                        super().error(ErrorType.TYPE_ERROR, "Exception type must be a string")
                    return result, ExecStatus.RAISE
                case Statement.RETURN:  # return immediately
                    return self.__call_return(statement, self.env.get_current_env())
                case _:
                    pass  # lazy evaluation

        return create_value(Type.NIL), ExecStatus.CONTINUE

    def __var_def(self, vardef_node: Element) -> None:
        var_name = vardef_node.get("name")
        if not self.env.create(var_name):
            super().error(ErrorType.NAME_ERROR, f"Variable {var_name} has already been defined")

    def __assign(self, assign_node: Element, env: list[dict]) -> None:
        var_name = assign_node.get("name")
        closure = self.__create_closure(assign_node.get("expression"), env)
        if not self.env.assign(var_name, closure):
            super().error(ErrorType.NAME_ERROR, f"Variable {var_name} has not been defined")

    def __create_closure(self, expr_node: Element, env: list[dict]) -> Closure:
        closure = Closure(expr_node)
        self.__capture_scope(closure, expr_node, env)
        return closure

    def __capture_scope(self, closure: Closure, expr_node: Element, env: list[dict]) -> None:
        """Capture variable scope for closure within environment"""
        expr = expr_node.elem_type
        if expr == "var":
            var_name = expr_node.get("name")
            var_val = find_var(var_name, env)
            closure.add_scope(var_name, var_val)
        elif expr == Statement.FUNC_CALL:
            for arg in expr_node.get("args"):
                self.__capture_scope(closure, arg, env)
        elif expr in UnaryOps:
            self.__capture_scope(closure, expr_node.get("op1"), env)
        elif expr in BinaryOps:
            self.__capture_scope(closure, expr_node.get("op1"), env)
            self.__capture_scope(closure, expr_node.get("op2"), env)

    def __call_func(self, fcall_node: Element, env: list[dict]) -> tuple[Value, ExecStatus]:
        func_name = fcall_node.get("name")
        match func_name:
            case "print":
                return self.__call_print(fcall_node, env)
            case "inputi" | "inputs":
                return self.__call_input(fcall_node, env)
            case _:  # user-defined function
                func_hash = (func_name, len(fcall_node.get("args")))
                if func_hash not in self.func_table:
                    super().error(ErrorType.NAME_ERROR, f"Function {func_name} not found")

                func_node = self.func_table[func_hash]
                param_names = [arg_node.get("name") for arg_node in func_node.get("args")]
                arg_values = [self.__create_closure(arg, env) for arg in fcall_node.get("args")]

                self.env.push_env()  # new environment for function call

                # map arguments to parameters and add to environment
                for param_name, arg_value in zip(param_names, arg_values):
                    self.env.create(param_name, arg_value)

                self.env.push_block()
                result, state = self.__run_statements(func_node.get("statements"))
                self.env.pop_block()

                self.env.pop_env()

                return result, state

    def __call_if(self, if_node: Element, env: list[dict]) -> tuple[Value, ExecStatus]:
        condition, state = self.__force_eval(if_node.get("condition"), env)
        if state != ExecStatus.CONTINUE:
            return condition, state
        if condition.type != Type.BOOL:
            super().error(ErrorType.TYPE_ERROR, "If condition must be a boolean")

        self.env.push_block()  # new child scope for if statement body
        result, state = create_value(Type.NIL), ExecStatus.CONTINUE

        if condition.value:
            result, state = self.__run_statements(if_node.get("statements"))
        elif if_node.get("else_statements"):
            result, state = self.__run_statements(if_node.get("else_statements"))

        self.env.pop_block()

        return result, state

    def __call_for(self, for_node: Element, env: list[dict]) -> tuple[Value, ExecStatus]:
        init: Element = for_node.get("init")
        condition: Element = for_node.get("condition")
        update: Element = for_node.get("update")

        if init.elem_type != Statement.ASSIGNMENT:
            super().error(ErrorType.TYPE_ERROR, "For loop initialization must be a variable declaration")
        if update.elem_type != Statement.ASSIGNMENT:
            super().error(ErrorType.TYPE_ERROR, "For loop update must be an assignment")

        self.__assign(init, env)
        result, state = create_value(Type.NIL), ExecStatus.CONTINUE

        while True:
            condition_result, state = self.__force_eval(condition, env)
            if state != ExecStatus.CONTINUE:
                return condition_result, state
            if condition_result.type != Type.BOOL:
                super().error(ErrorType.TYPE_ERROR, "For loop condition must be a boolean")
            if condition_result.value is False:
                break

            self.env.push_block()  # new child scope for for loop body
            result, state = self.__run_statements(for_node.get("statements"))
            self.env.pop_block()
            if state == ExecStatus.RETURN: break

            self.__assign(update, env)

        return result, state

    def __call_return(self, return_node: Element, env: list[dict]) -> tuple[Value, ExecStatus]:
        result = create_value(Type.NIL)  # default return value
        expr = return_node.get("expression")
        if expr:
            result = self.__create_closure(expr, env)

        return result, ExecStatus.RETURN

    def __call_try(self, try_node: Element) -> tuple[Value, ExecStatus]:
        self.env.push_block()
        result, state = self.__run_statements(try_node.get("statements"))
        self.env.pop_block()

        if state == ExecStatus.RAISE:
            for catch_node in try_node.get("catchers"):
                if catch_node.get("exception_type") == result.value:  # exception caught
                    self.env.push_block()
                    result, state = self.__run_statements(catch_node.get("statements"))
                    self.env.pop_block()
                    return result, state

        return result, state

    def __eval_expr(self, expr_node: Element, env: list[dict]) -> tuple[Value, ExecStatus]:
        expr = expr_node.elem_type
        if expr == Type.NIL:
            return create_value(Type.NIL), ExecStatus.CONTINUE
        if expr in [Type.INT, Type.STRING, Type.BOOL]:
            return create_value(expr, expr_node.get("val")), ExecStatus.CONTINUE
        if expr == "var":
            return self.__eval_var(expr_node, env)
        if expr == Statement.FUNC_CALL:  # function call within expression
            result, ret = self.__call_func(expr_node, env)
            return result, ExecStatus.CONTINUE if ret != ExecStatus.RAISE else ret
        if expr in UnaryOps:
            return self.__eval_unary_op(expr_node, env)
        if expr in BinaryOps:
            return self.__eval_op(expr_node, env)

        super().error(ErrorType.TYPE_ERROR, f"Unknown operand type: {expr}")

    def __force_eval(self, expr_node: Element, env: list[dict]) -> tuple[Value, ExecStatus]:
        value, state = self.__eval_expr(expr_node, env)
        if isinstance(value, Closure):
            return self.__eval_expr(value.expr, value.scope)
        return value, state

    def __eval_var(self, var_node: Element, env: list[dict]) -> tuple[Value, ExecStatus]:
        var_name: str = var_node.get("name")
        var_value, state = find_var(var_name, env), ExecStatus.CONTINUE

        if var_value is None:
            super().error(ErrorType.NAME_ERROR, f"Variable {var_name} not found")

        if isinstance(var_value, Closure):  # not evaluated yet
            var_value, state = self.__eval_expr(var_value.expr, var_value.scope)
            if state != ExecStatus.CONTINUE:
                return var_value, state

        assign_var(var_name, var_value, env)  # cache evaluated value
        return var_value, state

    def __eval_unary_op(self, expr_node: Element, env: list[dict]) -> tuple[Value, ExecStatus]:  # neg, !
        value, state = self.__force_eval(expr_node.get("op1"), env)
        if state != ExecStatus.CONTINUE: return value, state

        op_func = get_operator_lambda(value.type, expr_node.elem_type)
        if op_func is None:
            super().error(ErrorType.TYPE_ERROR, f"Incompatible types for '{expr_node.elem_type}' operation")

        return op_func(value), ExecStatus.CONTINUE

    def __eval_op(self, expr_node: Element, env: list[dict]) -> tuple[Value, ExecStatus]:
        oper = expr_node.elem_type
        lhs, state = self.__force_eval(expr_node.get("op1"), env)
        if state != ExecStatus.CONTINUE: return lhs, state

        # short-circuiting
        if oper == "&&" and lhs.value is False:
            return create_value(Type.BOOL, False), ExecStatus.CONTINUE
        if oper == "||" and lhs.value is True:
            return create_value(Type.BOOL, True), ExecStatus.CONTINUE

        rhs, state = self.__force_eval(expr_node.get("op2"), env)
        if state != ExecStatus.CONTINUE: return rhs, state

        # only equality check is allowed for different types
        if oper not in EqualOps and lhs.type != rhs.type:
            super().error(ErrorType.TYPE_ERROR, f"Incompatible types for {oper} operation")

        if oper == "/" and rhs.value == 0:
            return create_value(Type.STRING, "div0"), ExecStatus.RAISE

        op_func = get_operator_lambda(lhs.type, oper)
        if op_func is None:
            super().error(ErrorType.TYPE_ERROR,
                          f"Incompatible types '{lhs.type}' and '{rhs.type}' for '{oper}' operation")
        return op_func(lhs, rhs), ExecStatus.CONTINUE

    def __call_print(self, fcall_node: Element, env: list[dict]) -> tuple[Value, ExecStatus]:
        args = fcall_node.get("args")
        s = ""
        for arg in args:
            value, state = self.__force_eval(arg, env)
            if state != ExecStatus.CONTINUE:
                return value, state
            printable = get_printable(value)
            if printable is None:
                super().error(ErrorType.TYPE_ERROR, "Non-printable type for print()")
            s += printable
        super().output(s)
        return create_value(Type.NIL), ExecStatus.CONTINUE

    def __call_input(self, fcall_node: Element, env: list[dict]) -> tuple[Value, ExecStatus]:
        args = fcall_node.get("args")
        if len(args) > 1:
            super().error(ErrorType.NAME_ERROR, "inputi() function got more than one parameter")

        if args:
            arg, state = self.__force_eval(args[0], env)
            if state != ExecStatus.CONTINUE:
                return arg, state
            prompt = get_printable(arg)
            super().output(prompt)

        usr_input = super().get_input()
        func_name = fcall_node.get("name")

        match func_name:
            case "inputi":
                return create_value(Type.INT, int(usr_input)), ExecStatus.CONTINUE
            case "inputs":
                return create_value(Type.STRING, usr_input), ExecStatus.CONTINUE


def find_var(var_name: str, env: list[dict]) -> Closure | Value | None:
    for scope in reversed(env):
        if var_name in scope:
            return scope[var_name]
    return None


def assign_var(var_name: str, val: Closure | Value, env: list[dict]) -> bool:
    for scope in reversed(env):
        if var_name in scope:
            scope[var_name] = val
            return True
    return False
