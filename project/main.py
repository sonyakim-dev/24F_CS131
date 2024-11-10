from interpreterv3 import Interpreter
from type import *


def main():
    program = """
struct person {
  name: string;
  age: int;
}

func foo(a:int, b: person) : void {
  a = 10;
  b.age = b.age + 1;  /* changes p.age from 18 to 19 */

  b = new person;  /* this changes local b variable, not p var below */
  b.age = 100;     /* this does NOT change the p.age field below */
}

func main() : void {
  var x: int;
  x = 5;
  var p:person;
  p = new person;
  p.age = 18;
  foo(x, p);
  print(x);      /* prints 5, since x is passed by value */
  print(p.age);  /* prints 19, since p is passed by object reference */
}
"""
    interpreter = Interpreter(trace_output=True)
    interpreter.run(program)


if __name__ == "__main__":
    main()
