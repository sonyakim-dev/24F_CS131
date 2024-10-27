from interpreterv2 import Interpreter
from type import *


def main():
    program = """
func main() {
  if (true) {
    if (true) {
      print(1);
      return;
    }
    print(2);
  }
  return;
}
    """

    interpreter = Interpreter(trace_output=False)
    interpreter.run(program)


if __name__ == "__main__":
    main()
