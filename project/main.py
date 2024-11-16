from interpreterv3 import Interpreter


def main():
    program = """
    func main() : void {
        var i: int;
        for (i = 3; i; i = i - 1) {
            print(i);
        }
    }
    """
    interpreter = Interpreter(trace_output=True)
    interpreter.run(program)


if __name__ == "__main__":
    main()
