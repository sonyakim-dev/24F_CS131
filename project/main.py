from interpreterv3 import Interpreter


def main():
    program = """
struct list {
    val: int;
    next: list;
}

func cons(val: int, l: list) : list {
    var h: list;
    h = new list;
    h.val = val;
    h.next = l;
    return h;
}

func rev_app(l: list, a: list) : list {
    if (l == nil) {
        return a;
    }

    return rev_app(l.next, cons(l.val, a));
}

func reverse(l: list) : list {
    var a: list;

    return rev_app(l, a);
}

func print_list(l: list): void {
    var x: list;
    var n: int;
    for (x = l; x != nil; x = x.next) {
        print(x.val);
        n = n + 1;
    }
    print("N=", n);
}

func main() : void {
    var n: int;
    var i: int;
    var l: list;
    var r: list;

    n = inputi();
    for (i = n; i; i = i - 1) {
        var n: int;
        n = inputi();
        l = cons(n, l);
    }
    r = reverse(l);
    print_list(r);
}

/*
*IN*
8
1
2
3
4
5
6
7
8
*IN*
*OUT*
1
2
3
4
5
6
7
8
N=8
*OUT*
*/
"""
    interpreter = Interpreter(trace_output=True)
    interpreter.run(program)


if __name__ == "__main__":
    main()
