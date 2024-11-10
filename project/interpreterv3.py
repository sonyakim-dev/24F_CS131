from dataclasses import fields
from functools import reduce

from brewparse import parse_program
from element import Element
from env import EnvironmentManager
from intbase import ErrorType
from type import *

class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.trace_output = trace_output # debug purpose
        self.env = EnvironmentManager() # store variables
        self.func_table: dict[tuple[str, int], Element] = {} # key: (func name, arg count)
        self.struct_table: dict[str, dict[str, str]] = {} # {struct_name: {field_name: field_type}}

    def run(self, program) -> None:
        ast = parse_program(program) # generate Abstract Syntax Tree of the program
        self.__set_struct_table(ast)
        self.__set_function_table(ast)
        main_func = self.__get_func_by_name(("main", 0))
        self.__run_statements(main_func.get("statements"))

    def __set_function_table(self, ast: Element) -> None:
        for func_node in ast.get("functions"):
            func_name = func_node.get("name")
            params = func_node.get("args")
            return_type = func_node.get("return_type")
            return_value = get_default_value(return_type)

            if func_name in self.func_table:
                super().error(ErrorType.NAME_ERROR, f"Function {func_name} defined more than once")
            if return_value is None and return_type not in self.struct_table:
                super().error(ErrorType.TYPE_ERROR, f"Function {func_name} has invalid return type")
            for param in params:
                param_type = param.get("var_type")
                param_value = get_default_value(param_type)
                if param_value is None and param_type not in self.struct_table:
                    super().error(ErrorType.TYPE_ERROR, f"Function {func_name} has invalid parameter type")

            self.func_table[(func_name, len(func_node.get("args")))] = func_node
        """NOTE:
        Use of an invalid/undefined/missing type for a parameter or return type must result in an error of ErrorType.TYPE_ERROR.
        This check should happen before the execution of the main function, 
        """

    def __set_struct_table(self, ast: Element) -> None:
        for struct_node in ast.get("structs"):
            struct_name = struct_node.get("name")
            if struct_name in self.struct_table:
                super().error(ErrorType.NAME_ERROR, f"Struct {struct_name} defined more than once")
            self.struct_table[struct_name] = {}

            fields = {}
            for field_node in struct_node.get("fields"):
                var_type = field_node.get("var_type")
                if var_type not in PRIMITIVE_TYPES and var_type not in self.struct_table:
                    super().error(ErrorType.TYPE_ERROR, f"Struct {struct_name} has invalid field type")
                fields[field_node.get("name")] = var_type
            self.struct_table[struct_name] = fields

    def __get_func_by_name(self, func_key: tuple[str, int]) -> Element:
        if func_key not in self.func_table:
            super().error(ErrorType.NAME_ERROR, f"Function {func_key[0]} not found")
            
        return self.func_table[func_key]
    
    def __run_statements(self, statement_nodes: list[Element]) -> tuple[Value, ExecStatus]:      
        for statement in statement_nodes:
            if self.trace_output: # debug
                print(" 👩‍💻 ", statement)
                self.env._print()
            
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
                    return self.__call_return(statement), ExecStatus.RETURN
                case _:
                    super().error(ErrorType.TYPE_ERROR, f"Unknown statement type: {category}")
                    
        return Value(Type.NIL, None), ExecStatus.CONTINUE

    def __var_def(self, vardef_node: Element) -> None:
        var_name = vardef_node.get("name")
        var_type = vardef_node.get("var_type")
        var_value = get_default_value(var_type)

        if var_value not in PRIMITIVE_TYPES:
            if var_type not in self.struct_table:
                super().error(ErrorType.TYPE_ERROR, f"Invalid type {vardef_node.get('var_type')} for variable {var_name}")
            var_value = Value(var_type, None)

        if not self.env.create(var_name, var_value):
            super().error(ErrorType.NAME_ERROR, f"Variable {var_name} has already been defined")

    def __assign(self, assign_node: Element) -> None:
        var_name = assign_node.get("name")
        var_value = self.__eval_expr(assign_node.get("expression"))
        var_def = self.env.get(var_name)
        if var_def is None:
            super().error(ErrorType.NAME_ERROR, f"Variable {var_name} not defined")
        if var_def.type() != var_value.type():
            super().error(ErrorType.TYPE_ERROR, f"Cannot assign {var_value.type()} to variable {var_name}")

        self.env.assign(var_name, var_value)

    def __call_func(self, fcall_node: Element) -> Value:
        func_name = fcall_node.get("name")
        match func_name:
            case "print":
                return self.__call_print(fcall_node)
            case "inputi" | "inputs":
                return self.__call_input(fcall_node)
            case _: # user-defined function
                func_hash = (func_name, len(fcall_node.get("args")))
                if func_hash not in self.func_table:
                    super().error(ErrorType.NAME_ERROR, f"Function {func_name} not found")
                
                func_node = self.func_table[func_hash]
                param_names = [arg_node.get("name") for arg_node in func_node.get("args")]
                arg_values = [self.__eval_expr(arg) for arg in fcall_node.get("args")]

                self.env.push_env() # new environment for function call
                
                # map arguments to parameters and add to environment
                for param_name, arg_value in zip(param_names, arg_values):
                    self.env.create(param_name, arg_value)

                if self.trace_output: self.env._print(func_name) # debug

                self.env.push_block()
                # default_result = get_default_value(func_node.get("return_type"))
                result, _ = self.__run_statements(func_node.get("statements"))
                self.env.pop_block()

                self.env.pop_env()
                return result

    def __call_if(self, if_node: Element) -> tuple[Value, ExecStatus]:
        condition = self.__eval_expr(if_node.get("condition"))
        if condition.type() != Type.BOOL:
            super().error(ErrorType.TYPE_ERROR, "If condition must be a boolean")

        self.env.push_block() # new child scope for if statement body
        
        result, ret = Value(Type.NIL, None), ExecStatus.CONTINUE
        if condition.value():
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
        result, ret = Value(Type.NIL, None), ExecStatus.CONTINUE
        
        while True:
            condition_result = self.__eval_expr(condition)
            if condition_result.type() != Type.BOOL:
                super().error(ErrorType.TYPE_ERROR, "For loop condition must be a boolean")
            if condition_result.value() is False: break

            self.env.push_block() # new child scope for for loop body
            result, ret = self.__run_statements(for_node.get("statements"))
            self.env.pop_block()
            if ret == ExecStatus.RETURN: break
            
            self.__assign(update)

        return result, ret
    
    def __call_return(self, return_node: Element) -> Value:
        result = Value(Type.NIL, None) # void return
        if return_node.get("expression"):
            result = self.__eval_expr(return_node.get("expression"))
        return result

    def __eval_expr(self, expr_node: Element) -> Value:
        expr = expr_node.elem_type
        if expr in {Type.INT, Type.STRING, Type.BOOL}:
            return Value(expr, expr_node.get("val"))
        if expr == Type.NIL:
            return Value(expr, None)
        if expr == Type.VARIABLE: # can be struct type
            var_name = expr_node.get("name")
            val = self.env.get(var_name)
            if val is None:
                super().error(ErrorType.NAME_ERROR, f"Variable '{var_name}' not found")
            return val
        if expr in Operator.UNA_OPS:
            return self.__eval_unary_op(expr_node)
        if expr in Operator.BIN_OPS:
            return self.__eval_op(expr_node)
        if expr == Statement.FUNC_CALL:
            return self.__call_func(expr_node)
        if expr == Statement.NEW:
            var_type = expr_node.get("var_type")
            return Value(var_type, self.__new_struct(var_type))
        
        super().error(ErrorType.TYPE_ERROR, f"Unknown operand type: {expr}")

    def __new_struct(self, struct_name: str) -> dict[str, Value]:
        if struct_name not in self.struct_table:
            super().error(ErrorType.NAME_ERROR, f"Struct {struct_name} not found")

        struct_fields = self.struct_table[struct_name]
        # for field, val in struct_fields.items():
        #     print(field, val.type(), val.value())
        return { field: get_default_value(type) if type in PRIMITIVE_TYPES else Value(type, None)
                 for field, type in struct_fields.items() }

    def __eval_unary_op(self, expr_node: Element) -> Value: # neg, !
        op = self.__eval_expr(expr_node.get("op1"))
        try:
            return Operator.OP_TO_LAMBDA[op.type()][expr_node.elem_type](op)
        except KeyError:
            super().error(ErrorType.TYPE_ERROR, f"Incompatible operator {expr_node.elem_type} for type {op.type()}")
        
    def __eval_op(self, expr_node: Element) -> Value:
        oper = expr_node.elem_type
        lhs, rhs = self.__eval_expr(expr_node.get("op1")), self.__eval_expr(expr_node.get("op2")) 

        # only equality check is allowed for different types
        if lhs.type() != rhs.type() and oper not in ["==", "!="]:
            super().error(ErrorType.TYPE_ERROR, f"Incompatible types for {oper} operation")
        
        try:
            return Operator.OP_TO_LAMBDA[lhs.type()][oper](lhs, rhs)
        except KeyError:
            super().error(ErrorType.TYPE_ERROR, f"Incompatible operator {oper} for type {lhs.type()}")

    def __call_print(self, fcall_node) -> Value:
        args = fcall_node.get("args")
        # s = reduce(lambda acc, arg: acc + get_printable(self.__eval_expr(arg)), args, "")
        s = ""
        for arg in args:
            val = self.__eval_expr(arg)
            if val.type() in self.struct_table and val.value() is None:
                s += "nil"
            else:
                s += get_printable(val)
        super().output(s)
        return Value(Type.NIL, None)

    def __call_input(self, fcall_node) -> Value:
        args = fcall_node.get("args")
        if len(args) > 1:
            super().error(ErrorType.NAME_ERROR, "inputi() function that takes > 1 parameter")
            
        if args:
            prompt = get_printable(self.__eval_expr(args[0]))
            super().output(prompt)
            
        usr_input = super().get_input()
        func_name = fcall_node.get("name")
        match func_name:
            case "inputi":
                return Value(Type.INT, int(usr_input))
            case "inputs":
                return Value(Type.STRING, usr_input)
