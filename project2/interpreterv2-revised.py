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
        self.__call_func(main_func)

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
                    self.__assign(statement)
                case Statement.FUNC_CALL:
                    self.__call_func(statement)
                case Statement.IF_STATEMENT:
                    result, ret = self.__call_if(statement)
                    if ret == ExecStatus.RETURN:  # return early if return statement is encountered
                        return result, ret
                case Statement.FOR_STATEMENT:
                    result, ret = self.__call_for(statement)
                    if ret == ExecStatus.RETURN:  # return early if return statement is encountered
                        return result, ret
                case Statement.RETURN:  # return immediately
                    return self.__call_return(statement)
                case _:
                    super().error(ErrorType.TYPE_ERROR, f"Unknown statement type: {category}")

        return create_value(Type.NIL), ExecStatus.CONTINUE

    def __var_def(self, vardef_node: Element) -> None:
        var_name = vardef_node.get("name")
        if not self.env.create(var_name):
            super().error(ErrorType.NAME_ERROR, f"Variable {var_name} has already been defined")

    def __assign(self, assign_node: Element) -> None:
        var_name = assign_node.get("name")
        var_value = self.__eval_expr(assign_node.get("expression"))
        if not self.env.assign(var_name, var_value):
            super().error(ErrorType.NAME_ERROR, f"Variable {var_name} has not been defined")

    def __call_func(self, fcall_node: Element) -> Value|None:
        func_name = fcall_node.get("name")
        match func_name:
            case "print":
                return self.__call_print(fcall_node)
            case "inputi" | "inputs":
                return self.__call_input(fcall_node)
            case _:  # user-defined function
                func_hash = (func_name, len(fcall_node.get("args")))
                if func_hash not in self.func_table:
                    super().error(ErrorType.NAME_ERROR, f"Function {func_name} not found")

                func_node = self.func_table[func_hash]
                param_names = [arg_node.get("name") for arg_node in func_node.get("args")]
                arg_values = [self.__eval_expr(arg) for arg in fcall_node.get("args")]

                self.env.push_env()  # new environment for function call

                # map arguments to parameters and add to environment
                for param_name, arg_value in zip(param_names, arg_values):
                    self.env.create(param_name, arg_value)

                if self.trace_output: self.env.print(func_name)  # debug

                self.env.push_block()
                result, _ = self.__run_statements(func_node.get("statements"))
                self.env.pop_block()

                self.env.pop_env()
                return result

    def __call_if(self, if_node: Element) -> tuple[Value, ExecStatus]:
        condition = self.__eval_expr(if_node.get("condition"))
        if condition.type != Type.BOOL:
            super().error(ErrorType.TYPE_ERROR, "If condition must be a boolean")

        self.env.push_block()  # new child scope for if statement body

        result, ret = create_value(Type.NIL), ExecStatus.CONTINUE
        if condition.value:
            result, ret = self.__run_statements(if_node.get("statements"))
        elif if_node.get("else_statements"):
            result, ret = self.__run_statements(if_node.get("else_statements"))

        self.env.pop_block()

        return result, ret

    def __call_for(self, for_node: Element) -> tuple[Value, ExecStatus]:
        init: Element = for_node.get("init")
        condition: Element = for_node.get("condition")
        update: Element = for_node.get("update")

        if init.elem_type != Statement.ASSIGNMENT:
            super().error(ErrorType.TYPE_ERROR, "For loop initialization must be a variable declaration")
        if update.elem_type != Statement.ASSIGNMENT:
            super().error(ErrorType.TYPE_ERROR, "For loop update must be an assignment")

        self.__assign(init)
        result, ret = create_value(Type.NIL), ExecStatus.CONTINUE

        while True:
            condition_result = self.__eval_expr(condition)
            if condition_result.type != Type.BOOL:
                super().error(ErrorType.TYPE_ERROR, "For loop condition must be a boolean")
            if condition_result.value is False: break

            self.env.push_block()  # new child scope for for loop body
            result, ret = self.__run_statements(for_node.get("statements"))
            self.env.pop_block()
            if ret == ExecStatus.RETURN: break

            self.__assign(update)

        return result, ret

    def __call_return(self, return_node: Element) -> tuple[Value, ExecStatus]:
        result = create_value(Type.NIL)  # void return
        if return_node.get("expression"):
            result = self.__eval_expr(return_node.get("expression"))

        return result, ExecStatus.RETURN

    def __eval_expr(self, expr_node: Element) -> Value:
        expr = expr_node.elem_type
        if expr == Type.NIL:
            return create_value(Type.NIL)
        if expr in [Type.INT, Type.STRING, Type.BOOL]:
            return create_value(expr, expr_node.get("val"))
        if expr == "var":
            var_name: str = expr_node.get("name")
            val = self.env.get(var_name)
            if val is None:
                super().error(ErrorType.NAME_ERROR, f"Variable {var_name} not found")
            return val
        if expr == Statement.FUNC_CALL:
            return self.__call_func(expr_node)
        if expr in UnaryOps:
            return self.__eval_unary_op(expr_node)
        if expr in BinaryOps:
            return self.__eval_op(expr_node)

        super().error(ErrorType.TYPE_ERROR, f"Unknown operand type: {expr}")

    def __eval_unary_op(self, expr_node: Element) -> Value:  # neg, !
        val = self.__eval_expr(expr_node.get("op1"))
        op_func = get_operator_lambda(val.type, expr_node.elem_type)
        if op_func is None:
            super().error(ErrorType.TYPE_ERROR, f"Incompatible types for '{expr_node.elem_type}' operation")
        return op_func(val)

    def __eval_op(self, expr_node: Element) -> Value:
        oper = expr_node.elem_type
        lhs, rhs = self.__eval_expr(expr_node.get("op1")), self.__eval_expr(expr_node.get("op2"))

        # only equality check is allowed for different types
        if oper not in EqualOps and lhs.type != rhs.type:
            super().error(ErrorType.TYPE_ERROR, f"Incompatible types for {oper} operation")

        op_func = get_operator_lambda(lhs.type, oper)
        if op_func is None:
            super().error(ErrorType.TYPE_ERROR,
                          f"Incompatible types '{lhs.type}' and '{rhs.type}' for '{oper}' operation")
        return op_func(lhs, rhs)

    def __call_print(self, fcall_node: Element) -> Value:
        args = fcall_node.get("args")
        s = ""
        for arg in args:
            printable = get_printable(self.__eval_expr(arg))
            if printable is None:
                super().error(ErrorType.TYPE_ERROR, "Non-printable type for print()")
            s += printable
        super().output(s)
        return create_value(Type.NIL)

    def __call_input(self, fcall_node: Element) -> Value:
        args = fcall_node.get("args")
        if len(args) > 1:
            super().error(ErrorType.NAME_ERROR, "inputi() function got more than one parameter")

        if args:
            prompt = get_printable(self.__eval_expr(args[0]))
            super().output(prompt)

        usr_input = super().get_input()
        func_name = fcall_node.get("name")

        match func_name:
            case "inputi":
                return create_value(Type.INT, int(usr_input))
            case "inputs":
                return create_value(Type.STRING, usr_input)
