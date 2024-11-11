from interpreterv3 import Interpreter


def main():
    program = """
struct dog {
  name: string;
  vaccinated: bool;  
}

func main() : void {
  var d: dog;    /* d is an object reference whose value is nil */
  var e: dog;
  
  d = new dog;
  print(d == e);
}
"""
    interpreter = Interpreter(trace_output=True)
    interpreter.run(program)


if __name__ == "__main__":
    main()
