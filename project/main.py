from interpreterv3 import Interpreter


def main():
    program = """
struct dog {
 bark: int;
 bite: int;
}

func foo(d: dog) : dog {  /* d holds the same object reference that the koda variable holds */
  d.bark = 10;
  return d;  		/* this returns the same object reference that the koda variable holds */
}

 func main() : void {
  var koda: dog;
  var kippy: dog;
  koda = new dog;
  kippy = foo(koda);	/* kippy holds the same object reference as koda */
  kippy.bite = 20;
  print(koda.bark, " ", koda.bite); /* prints 10 20 */
}
"""
    interpreter = Interpreter(trace_output=True)
    interpreter.run(program)


if __name__ == "__main__":
    main()
