from interpreterv3 import Interpreter
from type import *


def main():
    program = """
struct flea {
  age: int;
  infected : bool;
}

struct dog {
  name: string;
  vaccinated: bool;  
  companion: flea;
}

func main() : void {
  var d: dog;     
  d = new dog;   /* sets d object reference to point to a dog structure */

  print(d.vaccinated); /* prints false - default bool value */
  print(d.companion); /* prints nil - default struct object reference */

  /* we may now set d's fields */
  d.name = "Koda";
  d.vaccinated = true;
  d.companion = new flea;
  d.companion.age = 3; 
  
  var a: int;
  a = 0;
}
"""
    interpreter = Interpreter(trace_output=True)
    interpreter.run(program)


if __name__ == "__main__":
    main()
