from functools import reduce
from typing import Any

from brewparse import parse_program
from element import Element
from intbase import ErrorType, InterpreterBase
from type import NODE_TYPE


class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)  # call InterpreterBase's constructor
        self.trac_output: bool = trace_output  # debug purpose
        self.__variables: dict[str, Any] = {}  # map variable names to values
        self.__functions: dict[str, Element] = {}

    def __set_variable(self, key: str, val=None) -> None:
        self.__variables[key] = val

    def __get_variable(self, key: str):
        try:
            return self.__variables[key]
        except:
            super().error(ErrorType.NAME_ERROR, f"Variable {key} has not been defined")

    def run(self, program) -> None:
        ast = parse_program(program)  # generate Abstract Syntax Tree of the program
        main_func_node = self.get_main_func_node(ast)
        self.run_func_node(main_func_node)
        self._print_attributes()  # debug purpose


    def get_main_func_node(self, ast: Element) -> Element:
        for func in ast.get("functions"):
            func_name = func.get("name")
            if func_name in self.__functions:
                super().error(ErrorType.NAME_ERROR, f"Function {func_name} defined more than once")

            self.__functions[func_name] = func

        try: # must have ONE main function
            return self.__functions["main"]
        except:
            super().error(ErrorType.NAME_ERROR, "No main function was found")

    def run_func_node(self, func_node: Element):  # TODO: return what func returns
        # run each statement in the function top to bottom
        for statement_node in func_node.get("statements"):
            self.run_statement_node(statement_node)


    def run_statement_node(self, statement_node: Element) -> None:
        category: str = statement_node.elem_type
        match category:
            case NODE_TYPE.VAR_DEF:  # var x;
                self.do_var_definition(statement_node)
            case NODE_TYPE.ASSIGNMENT:  # x = y + 1;
                self.do_assignment(statement_node)
            case NODE_TYPE.FUNC_CALL:  # print("Hello, World!");
                self.do_func_call(statement_node)
            case _:
                super().error(ErrorType.TYPE_ERROR, f"Unknown statement type: {category}")

    # -- Statement node handlers-- #
    def do_var_definition(self, vardef_node: Element) -> None:
        var_name: str = vardef_node.get("name")
        if var_name in self.__variables: # check if variable is already defined
            super().error(ErrorType.NAME_ERROR, f"Variable {var_name} defined more than once")

        self.__set_variable(var_name)

    def do_assignment(self, assignment_node: Element) -> None:
        var_name: str = assignment_node.get("name")  # lfs
        expression_node: Element = assignment_node.get("expression")  # rhs
        if var_name not in self.__variables: # check if variable is defined
            super().error(ErrorType.NAME_ERROR, f"Variable {var_name} has not been defined")

        self.__set_variable(var_name, self.evaluate_expression(expression_node))

    def do_func_call(self, fcall_node: Element):
        func_name: str = fcall_node.get("name")
        args: list[Element] = fcall_node.get("args")

        match func_name:
            case "print":
                return self.print(args)
            case "inputi":
                return self.inputi(args)
            case _:
                try:
                    return self.run_func_node(self.__functions[func_name], args)
                except:
                    super().error(ErrorType.NAME_ERROR, f"Function {func_name} has not been defined")


    def run_expression_node(self, expression_node: Element) -> Any:
        # op can be either const, var, func call, or nested expression
        op1, op2 = expression_node.get("op1"), expression_node.get("op2")
        op1_val, op2_val = self.evaluate_expression(op1), self.evaluate_expression(op2)

        if type(op1_val) != type(op2_val):
            super().error(ErrorType.TYPE_ERROR, "Incompatible types for arithmetic operation")

        category: str = expression_node.elem_type
        match category:
            case NODE_TYPE.ADDITION:
                return op1_val + op2_val
            case NODE_TYPE.SUBTRACTION:
                return op1_val - op2_val
            case _:
                super().error(ErrorType.TYPE_ERROR, f"Unknown expression type: {category}")
                
    def evaluate_expression(self, node: Element) -> Any:
        match node.elem_type:
            case NODE_TYPE.INT_VALUE | NODE_TYPE.STRING_VALUE:
                return node.get("val")
            case NODE_TYPE.VARIABLE:
                return self.__get_variable(node.get("name"))
            case NODE_TYPE.FUNC_CALL:
                return self.do_func_call(node)
            case NODE_TYPE.ADDITION | NODE_TYPE.SUBTRACTION:
                return self.run_expression_node(node)
            case _:
                super().error(ErrorType.TYPE_ERROR, f"Unknown operand type: {node.elem_type}")


    # -- Pre-defined functions -- #
    # NOTE: print() function in an expression is an UNDEFINED BEHAVIOR and will NOT be tested
    def print(self, args: list[Element]) -> None:
        # concatenate all arguments
        s = reduce(lambda acc, arg: acc + str(self.evaluate_expression(arg)), args, "")
        super().output(s)

    def inputi(self, args: list[Element]) -> int:  # get int input from user
        if len(args) > 1:
            super().error(ErrorType.NAME_ERROR, "inputi() function found that takes > 1 parameter")

        if args:
            prompt = self.evaluate_expression(args[0]) # NOTE: assume the prompt is a string
            super().output(prompt)

        usr_input: str = super().get_input() # NOTE: assume only valid integers will be entered
        return int(usr_input)


    # -- debug purpose -- #
    def _print_attributes(self):
        if self.trac_output:
            print("\n---Variables---")
            for key, val in self.__variables.items():
                print(f"{key}: {val}")
            print("---------------")
