from brewparse import parse_program
from element import Element
from env import EnvironmentManager
from intbase import InterpreterBase, ErrorType
from type import *


class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.trace_output = trace_output # debug purpose
        self.env = EnvironmentManager() # store variables
        self.func_table: dict[tuple[str, int], Element] = {} # {(func_name, arg_count): func_node}
        self.struct_table: dict[str, dict[str, Value]] = {} # {struct_name: {field_name: Value}}

    def run(self, program) -> None:
        ast = parse_program(program) # generate Abstract Syntax Tree of the program
        self.__set_struct_table(ast.get("structs"))
        self.__set_function_table(ast.get("functions"))
        main_func = self.__get_func_by_name(("main", 0))
        self.__call_func(main_func)

    def __set_function_table(self, func_nodes: list[Element]) -> None:
        for func_node in func_nodes:
            func_name = func_node.get("name")
            params = func_node.get("args")
            return_type = func_node.get("return_type")

            if func_name in self.func_table: # check duplicated function
                super().error(ErrorType.NAME_ERROR, f"Function '{func_name}' defined more than once")
            if return_type not in FuncType and return_type not in self.struct_table: # check return type
                super().error(ErrorType.TYPE_ERROR, f"Function '{func_name}' has invalid return type '{return_type}'")

            for param in params: # check param types
                param_type = param.get("var_type")
                if param_type not in VarType and param_type not in self.struct_table:
                    super().error(ErrorType.TYPE_ERROR,
                                  f"Function '{func_name}' has invalid parameter type '{param_type}' for '{param.get('name')}'")

            self.func_table[(func_name, len(func_node.get("args")))] = func_node

    def __set_struct_table(self, struct_nodes: list[Element]) -> None:
        for struct_node in struct_nodes:
            struct_name = struct_node.get("name")

            if BasicType.contains(struct_name):
                super().error(ErrorType.NAME_ERROR, f"Struct '{struct_name}' is invalid name")
            if struct_name in self.struct_table:
                super().error(ErrorType.NAME_ERROR, f"Struct '{struct_name}' defined more than once")

            self.struct_table[struct_name] = {} # hold namespace in case a field type references itself (ex. List{next:List})

            fields = {}
            for field_node in struct_node.get("fields"):
                field_name = field_node.get("name")
                var_type = self.__get_type(field_node.get("var_type"))

                if isinstance(var_type, ErrorType): # or var_type in [BasicType.NIL, BasicType.VOID] ?
                    super().error(var_type,
                                  f"Struct '{struct_name}' has invalid type '{field_node.get('var_type')}' for '{field_name}'")

                fields[field_name] = create_value(var_type)

            self.struct_table[struct_name] = fields

    def __get_type(self, var_type: str) -> Type|ErrorType:
        if BasicType.contains(var_type):
            return BasicType(var_type)
        elif var_type in self.struct_table:
            return StructType(var_type)
        else:
            return ErrorType.TYPE_ERROR

    def __get_func_by_name(self, func_key: tuple[str, int]) -> Element:
        func_name, arg_count = func_key
        if func_key not in self.func_table:
            super().error(ErrorType.NAME_ERROR, f"Function '{func_name}' with {arg_count} params not found")

        return self.func_table[func_key]

    def __run_statements(self, statement_nodes: list[Element]) -> tuple[Value, ExecStatus]:
        for statement in statement_nodes:
            if self.trace_output: print(" 👩‍💻 ", statement)

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
                    if ret == ExecStatus.RETURN: # return early if return statement is encountered
                        return result, ret
                case Statement.FOR_STATEMENT:
                    result, ret = self.__call_for(statement)
                    if ret == ExecStatus.RETURN: # return early if return statement is encountered
                        return result, ret
                case Statement.RETURN: # return immediately
                    return self.__call_return(statement)
                case _:
                    super().error(ErrorType.TYPE_ERROR, f"Statement '{category}' is unknown")

            if self.trace_output: self.env.print(category)

        return create_value(BasicType.VOID), ExecStatus.CONTINUE

    def __var_def(self, vardef_node: Element) -> None:
        var_name = vardef_node.get("name")
        var_type = self.__get_type(vardef_node.get("var_type"))

        if isinstance(var_type, ErrorType):
            super().error(var_type, f"Variable '{var_name}' has invalid type '{vardef_node.get('var_type')}'")

        var_value = create_value(var_type)

        if not self.env.create(var_name, var_value):
            super().error(ErrorType.NAME_ERROR, f"Variable '{var_name}' defined more than once")

    def __assign(self, assign_node: Element) -> None:
        var_name = assign_node.get("name")
        var_def = self.env.get(var_name)
        value = self.__eval_expr(assign_node.get("expression"))

        if isinstance(var_def, ErrorType):
            super().error(var_def, f"Variable '{var_name}' not found")

        value, var_def = try_conversion(value, var_def)
        if var_def.type != value.type:
            super().error(ErrorType.TYPE_ERROR, f"Cannot assign '{value.type}' to variable '{var_name}'")

        res = self.env.assign(var_name, value)

        if isinstance(res, ErrorType):
            super().error(res, f"Cannot assign '{value.type}' to variable '{var_name}'")

    def __call_func(self, fcall_node: Element) -> Value:
        func_name = fcall_node.get("name")
        match func_name:
            case "print":
                return self.__call_print(fcall_node)
            case "inputi" | "inputs":
                return self.__call_input(fcall_node)
            case _: # user-defined function
                func_hash = (func_name, len(fcall_node.get("args")))
                func_node = self.__get_func_by_name(func_hash)

                # no need to check invalid parameter type since it's already checked in __set_function_table
                params = {arg_node.get("name"): self.__get_type(arg_node.get("var_type")) for arg_node in func_node.get("args")}
                arg_values = [self.__eval_expr(arg) for arg in fcall_node.get("args")]

                self.env.push_env() # new environment for function call

                # map arguments to parameters and add to environment
                for (param_name,param_type), arg_value in zip(params.items(), arg_values):
                    param_value = create_value(param_type)
                    if param_value != arg_value.type:
                        arg_value, param_value = try_conversion(arg_value, param_value)
                        if param_value.type != arg_value.type:
                            super().error(ErrorType.TYPE_ERROR,
                                          f"Function '{func_name}' expects '{param_value.type}' type for '{param_name}'")
                    self.env.create(param_name, arg_value)

                if self.trace_output: self.env.print(func_name) # debug

                self.env.push_block()
                result, _ = self.__run_statements(func_node.get("statements"))
                self.env.pop_block()
                self.env.pop_env()

                # no need to check invalid return type since it's already checked in __set_function_table
                return_type = self.__get_type(func_node.get("return_type"))
                return_value = create_value(return_type)

                # if function has no return statement or simply return without value, return default value
                if result.type == BasicType.VOID and result.type != return_type:
                    return return_value

                result, _ = try_conversion(result, return_value)
                if result.type != return_type:
                    super().error(ErrorType.TYPE_ERROR, f"Function '{func_name}' must return '{return_type}' type")

                return result

    def __call_if(self, if_node: Element) -> tuple[Value, ExecStatus]:
        condition = self.__eval_expr(if_node.get("condition"))
        if condition.type != BasicType.BOOL:
            condition, _ = try_conversion(condition, create_value(BasicType.BOOL))
            if condition.type != BasicType.BOOL:
                super().error(ErrorType.TYPE_ERROR, "'if' condition must be a boolean")

        self.env.push_block() # new child scope for if statement body

        result, ret = create_value(BasicType.VOID), ExecStatus.CONTINUE
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
            super().error(ErrorType.TYPE_ERROR, "'for' loop initialization must be a variable declaration")
        if update.elem_type != Statement.ASSIGNMENT:
            super().error(ErrorType.TYPE_ERROR, "'for' loop update must be an assignment")

        self.__assign(init)
        result, ret = create_value(BasicType.VOID), ExecStatus.CONTINUE

        while True:
            condition_result = self.__eval_expr(condition)
            if condition_result.type != BasicType.BOOL:
                condition_result, _ = try_conversion(condition_result, create_value(BasicType.BOOL))
                if condition_result.type != BasicType.BOOL:
                    super().error(ErrorType.TYPE_ERROR, "'for' loop condition must be a boolean")
            if condition_result.value is False: break

            self.env.push_block() # new child scope for for loop body
            result, ret = self.__run_statements(for_node.get("statements"))
            self.env.pop_block()
            if ret == ExecStatus.RETURN: break

            self.__assign(update)

        return result, ret

    def __call_return(self, return_node: Element) -> tuple[Value, ExecStatus]:
        result = create_value(BasicType.VOID) # default is void return
        if return_node.get("expression"):
            result = self.__eval_expr(return_node.get("expression"))

        return result, ExecStatus.RETURN

    def __eval_expr(self, expr_node: Element) -> Value:
        expr = expr_node.elem_type
        if expr in VarType:
            return create_value(BasicType(expr), expr_node.get("val"))
        if expr == BasicType.NIL.value: # nil does not have expr_node.get("val")
            return create_value(BasicType.NIL)
        if expr == "var": # can be struct type
            var_name = expr_node.get("name")
            val = self.env.get(var_name)
            if isinstance(val, ErrorType):
                super().error(val, f"Variable '{var_name}' not found")
            return val
        if expr in UnaryOps:
            return self.__eval_unary_op(expr_node)
        if expr in BinaryOps:
            return self.__eval_op(expr_node)
        if expr == Statement.FUNC_CALL:
            return self.__call_func(expr_node)
        if expr == Statement.NEW:
            return self.__new_struct(expr_node)

        super().error(ErrorType.TYPE_ERROR, f"Operand '{expr}' is unknown")

    def __new_struct(self, expr_node: Element) -> Value:
        struct_name = expr_node.get("var_type")

        if struct_name not in self.struct_table:
            super().error(ErrorType.TYPE_ERROR, f"Struct '{struct_name}' not found")

        struct_fields = self.struct_table[struct_name]
        value = { field: value for field, value in struct_fields.items() }

        return create_value(StructType(struct_name), value)

    def __eval_op(self, expr_node: Element) -> Value:
        oper = expr_node.elem_type
        lhs, rhs = self.__eval_expr(expr_node.get("op1")), self.__eval_expr(expr_node.get("op2"))

        # handle equality operators for struct types
        if oper in EqualOps:
            if isinstance(lhs.type, StructType) or isinstance(rhs.type, StructType):
                # check first if both struct types are different but uninitialized before normalization
                if isinstance(lhs.type, StructType) and isinstance(rhs.type, StructType) and lhs.type != rhs.type:
                    super().error(ErrorType.TYPE_ERROR,
                                  f"Incompatible types '{lhs.type}' and '{rhs.type}' for '{oper}' operation")

                lhs, rhs = normalize_struct(lhs), normalize_struct(rhs) # normalize None value structs to NIL value
                # return now in case comparing uninitialized struct with NIL
                if isinstance(lhs.type, StructType) or isinstance(rhs.type, StructType):
                    return get_operator_lambda(StructType.STRUCT, oper)(lhs,rhs)

            else: # basic types coercion
                lhs, rhs = coercion_by_priority(lhs, rhs)

        elif oper in LogicOps:
            lhs, _ = try_conversion(lhs, create_value(BasicType.BOOL)) # convert to boolean
            rhs, _ = try_conversion(rhs, create_value(BasicType.BOOL))

        else:
            lhs, rhs = coercion_by_priority(lhs, rhs)

        # types must match except for equality operators
        if lhs.type != rhs.type:
            super().error(ErrorType.TYPE_ERROR,
                          f"Incompatible types '{lhs.type}' and '{rhs.type}' for '{oper}' operation")

        op_func = get_operator_lambda(lhs.type, oper)
        if op_func is None:
            super().error(ErrorType.TYPE_ERROR,
                          f"Incompatible types '{lhs.type}' and '{rhs.type}' for '{oper}' operation")
        return op_func(lhs, rhs)

    def __eval_unary_op(self, expr_node: Element) -> Value: # neg for INT, ! for BOOL
        val = self.__eval_expr(expr_node.get("op1"))
        val, _ = try_conversion(val, create_value(BasicType.BOOL) if expr_node.elem_type == "!" else create_value(BasicType.INT))

        op_func = get_operator_lambda(val.type, expr_node.elem_type)
        if op_func is None:
            super().error(ErrorType.TYPE_ERROR, f"Incompatible types for '{expr_node.elem_type}' operation")
        return op_func(val)

    def __call_print(self, fcall_node: Element) -> Value:
        args = fcall_node.get("args")
        s = ""
        for arg in args:
            printable = get_printable(self.__eval_expr(arg))
            if printable is None:
                super().error(ErrorType.TYPE_ERROR, "Non-printable type for print()")
            s += printable
        super().output(s)

        return create_value(BasicType.VOID)

    def __call_input(self, fcall_node: Element) -> Value:
        args = fcall_node.get("args")
        if len(args) > 1:
            super().error(ErrorType.NAME_ERROR, "inputi() can take only one parameter")

        if args:
            prompt = get_printable(self.__eval_expr(args[0])) # arg is always a string
            super().output(prompt)

        usr_input = super().get_input()
        func_name = fcall_node.get("name")

        match func_name:
            case "inputi":
                return create_value(BasicType.INT, int(usr_input))
            case "inputs":
                return create_value(BasicType.STRING, usr_input)
