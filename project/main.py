from interpreterv2 import Interpreter
from type import *


def main():
    program = """
func main() {
  var foo;
  foo = foo(4);
  print(foo);
}

func foo(a) {
  var i;
  for (i = 0; i < a; i = i + 1) {
    if (i == 3) {
      return i;
    }
    print(i);
    return i;
  }
}
    """

    interpreter = Interpreter(trace_output=True)
    interpreter.run(program)


if __name__ == "__main__":
    main()
