from interpreterv2 import Interpreter
from type import *


def main():
    program = """
func main() {
    var a;
    a = foo(5);
    print(0);
}
func foo(n) {
    print(1);
    boo(2);
    print(3);
}
func boo(n) {
    print(4);
    return;
}
    """

    interpreter = Interpreter(trace_output=True)
    interpreter.run(program)


if __name__ == "__main__":
    main()
