from interpreterv3 import Interpreter
from type import *


def main():
    program = """
struct dog {
  bark: int;
  bite: int;
}

func bar() : int {
  return;  /* no return value specified - returns 0 */
}

func bletch() : bool {
  print("hi");
  /* no explicit return; bletch must return default bool of false */
}

func boing() : dog {
  return;  /* returns nil */
}

func main() : void {
   var val: int;
   val = bar();
   print(val);  /* prints 0 */
   print(bletch()); /* prints false */
   print(boing()); /* prints nil */
}
"""
    interpreter = Interpreter(trace_output=True)
    interpreter.run(program)


if __name__ == "__main__":
    main()
