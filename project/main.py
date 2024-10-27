from interpreterv2 import Interpreter
from type import *


def main():
    program = """
func main() {
 var a;
 a = factorial(5);
 print(a);
 foo();
}
func factorial(n) {
    if (n == 0) {
        return 1;
    }
    return n * factorial(n - 1);
}
func foo() {
    return;
}
    """

    interpreter = Interpreter(trace_output=True)
    interpreter.run(program)


if __name__ == "__main__":
    main()
