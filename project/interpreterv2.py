from functools import reduce
from typing import Any

from brewparse import parse_program
from element import Element
from env import EnvironmentManager
from intbase import ErrorType, InterpreterBase
from ops import OP_TO_LAMBDA
from type import *


class Interpreter(InterpreterBase):
    UNA_OPS = {"neg", "!"}
    BIN_OPS = {"+", "-", "*", "/", ">=", "<=", ">", "<", "||", "&&", "==", "!="}

    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.trace_output = trace_output # debug purpose
        self.env = EnvironmentManager() # store variables
        self.function_table: dict[(str, int), Element] = {} # key: (func name, arg count)

    def run(self, program) -> None:
        ast = parse_program(program) # generate Abstract Syntax Tree of the program
        self.__set_function_table(ast)
        main_func = self.__get_func_by_name(("main", 0))
        self.__run_statement_nodes(main_func.get("statements"))

    def __set_function_table(self, ast: Element) -> None:
        for func_node in ast.get("functions"):
            func_name = func_node.get("name")
            if func_name in self.function_table:
                super().error(ErrorType.NAME_ERROR, f"Function {func_name} defined more than once")

            self.function_table[(func_name, len(func_node.get("args")))] = func_node

    def __get_func_by_name(self, func_key: tuple[str, int]) -> Element:
        if func_key not in self.function_table:
            super().error(ErrorType.NAME_ERROR, f"Function {func_key[0]} not found")
            
        return self.function_table[func_key]
    
    def __run_statement_nodes(self, statement_nodes: Element):      
        for statement in statement_nodes:
            if self.trace_output: print(" STAT.. ", statement)
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
                    if ret: return result, ret
                case Statement.FOR_STATEMENT:
                    result, ret = self.__call_for(statement)
                    if ret: return result, ret
                case Statement.RETURN:
                    return self.__call_return(statement), True
                case _:
                    super().error(ErrorType.TYPE_ERROR, f"Unknown statement type: {category}")
        return Value(Type.NIL, None), False

    def __var_def(self, vardef_node: Element) -> None:
        var_name = vardef_node.get("name")
        if not self.env.create(var_name, Value(Type.NIL, None)):
            super().error(ErrorType.NAME_ERROR, f"Variable {var_name} has already been defined")

    def __assign(self, assign_node: Element) -> None:
        var_name = assign_node.get("name")
        var_value = self.__eval_expr(assign_node.get("expression"))
        if not self.env.assign(var_name, var_value):
            super().error(ErrorType.NAME_ERROR, f"Variable {var_name} has not been defined")

    def __call_func(self, fcall_node: Element) -> Value:
        func_name = fcall_node.get("name")
        match func_name:
            case "print":
                return self.__call_print(fcall_node)
            case "inputi" | "inputs":
                return self.__call_input(fcall_node)
            case _: # user-defined function
                func_hash = (func_name, len(fcall_node.get("args")))
                if func_hash not in self.function_table:
                    super().error(ErrorType.NAME_ERROR, f"Function {func_name} not found")
                
                func_node = self.function_table[func_hash]
                param_names = [arg_node.get("name") for arg_node in func_node.get("args")]
                arg_values = [self.__eval_expr(arg) for arg in fcall_node.get("args")]
                
                # set new environment scope for function call
                prev_env = self.env
                self.env = EnvironmentManager()
                
                # map arguments to parameters
                for param_name, arg_value in zip(param_names, arg_values):
                    self.env.create(param_name, arg_value)

                if self.trace_output: self.env._print(func_name) # debug purpose
                
                result, _ = self.__run_statement_nodes(func_node.get("statements"))
                self.env = prev_env
                
                return result
        
    def __call_if(self, if_node: Element):
        condition = self.__eval_expr(if_node.get("condition"))
        if condition.type() != Type.BOOL:
            super().error(ErrorType.TYPE_ERROR, "If condition must be a boolean")
        
        # create child scope
        self.env = EnvironmentManager(self.env)
        
        result, ret = None, False
        if condition.value():
            result, ret = self.__run_statement_nodes(if_node.get("statements"))
        elif if_node.get("else_statements"):
            result, ret = self.__run_statement_nodes(if_node.get("else_statements"))
        
        self.env = self.env.end_scope()

        if ret: return result, True
        else: return None, False
        
    def __call_for(self, for_node: Element) -> Value:
        init = for_node.get("init")
        condition = for_node.get("condition")
        update = for_node.get("update")

        if init.elem_type != Statement.ASSIGNMENT:
            super().error(ErrorType.TYPE_ERROR, "For loop initialization must be a variable declaration")
        if update.elem_type != Statement.ASSIGNMENT:
            super().error(ErrorType.TYPE_ERROR, "For loop update must be an assignment")
        
        self.__assign(init)
        result = ret = None
        
        while True:
            condition_result = self.__eval_expr(condition)
            if condition_result.type() != Type.BOOL:
                    super().error(ErrorType.TYPE_ERROR, "For loop condition must be a boolean")
            if condition_result.value() == False:
                break
            
            # local scope for for loop
            self.env = EnvironmentManager(self.env)
            result, ret = self.__run_statement_nodes(for_node.get("statements"))
            self.env = self.env.end_scope()
            self.__assign(update)

        return result, ret
    
    def __call_return(self, return_node: Element) -> Value:
        result = Value(Type.NIL, None) # void return
        if return_node.get("expression"):
            result = self.__eval_expr(return_node.get("expression"))
        return result

    def __eval_expr(self, expr_node: Element) -> Value:
        expr = expr_node.elem_type
        if expr in [Type.INT, Type.STRING, Type.BOOL]:
            return Value(expr, expr_node.get("val"))
        if expr == Type.NIL:
            return Value(expr, None)
        if expr == Type.VARIABLE:
            var_name = expr_node.get("name")
            val = self.env.get(var_name)
            if val is None:
                super().error(ErrorType.NAME_ERROR, f"Variable {var_name} not found")
            return val
        if expr == Statement.FUNC_CALL:
            return self.__call_func(expr_node)
        if expr in Interpreter.UNA_OPS:
            return self.__eval_unary_op(expr_node)
        if expr in Interpreter.BIN_OPS:
            return self.__eval_op(expr_node)
        
        super().error(ErrorType.TYPE_ERROR, f"Unknown operand type: {expr}")

    def __eval_unary_op(self, expr_node: Element) -> Value:
        op = self.__eval_expr(expr_node.get("op1"))
        return OP_TO_LAMBDA[op.type()][expr_node.elem_type](op)
        
    def __eval_op(self, expr_node: Element) -> Value:
        oper = expr_node.elem_type
        lhs, rhs = self.__eval_expr(expr_node.get("op1")), self.__eval_expr(expr_node.get("op2"))

        if lhs.type() != rhs.type():
            if oper == "==":
                return Value(Type.BOOL, lhs.type() == rhs.type())
            if oper == "!=":
                return Value(Type.BOOL, lhs.type() != rhs.type())
            super().error(ErrorType.TYPE_ERROR, f"Incompatible types for {oper} operation")
            
        if oper not in OP_TO_LAMBDA[lhs.type()]:
            super().error(ErrorType.TYPE_ERROR, f"Incompatible operator {oper} for type {lhs.type()}")
            
        return OP_TO_LAMBDA[lhs.type()][oper](lhs, rhs)

    def __call_print(self, fcall_node) -> Value:
        args = fcall_node.get("args")
        s = reduce(lambda acc, arg: acc + get_printable(self.__eval_expr(arg)), args, "")
        super().output(s)
        return Value(Type.NIL, None)

    def __call_input(self, fcall_node) -> Value:
        args = fcall_node.get("args")
        if len(args) > 1:
            super().error(ErrorType.NAME_ERROR, "inputi() function that takes > 1 parameter")
            
        if args:
            prompt = get_printable(self.__eval_expr(args[0]))
            super().output(prompt)
            
        input = super().get_input()
        
        func_name = fcall_node.get("name")
        match func_name:
            case "inputi":
                return Value(Type.INT, int(input))
            case "inputs":
                return Value(Type.STRING, input)
