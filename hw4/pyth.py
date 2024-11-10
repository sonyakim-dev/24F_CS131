import copy
from functools import reduce


# PTYH9
def strip_characters(sentence, chars_to_remove):
    return "".join([s for s in sentence if s not in chars_to_remove])

# PYTH10
def foo(a):
    def bar(b):
        return a + b # captures a from outer scope
    return bar
print(foo("1")("2"))

# PYTH11
def convert_to_decimal(bits):
    exponents = range(len(bits)-1, -1, -1)
    nums = [b * 2**e for b, e in zip(bits, exponents)]
    return reduce(lambda acc, num: acc + num, nums)

# PYTH12
def parse_csv(lines):
    return [(word, int(num)) for word, num in (line.split(",") for line in lines)]

def unique_characters(sentence):
    return {c for c in sentence}

def squares_dict(lower_bound, upper_bound):
    return {i: i**2 for i in range(lower_bound, upper_bound+1)}


# print(strip_characters("Hello, world!", {"o", "h", "l"}))
# print(convert_to_decimal([1, 0, 1]))
# print(parse_csv(["apple,8", "pear,24", "gooseberry,-2"]))
# print(unique_characters("happy"))
# print(squares_dict(1, 5))


class A:
    def __init__(self, a):
        self.a = a
    
class B(A):
    def __init__(self, b):
        self.b = b

# print(isinstance(B(1), A))
# print(issubclass(A, A))
# print(type(A(1)) is type(B(2)))

ls1 = [1, 2, 3]
# ls2 = ls1
ls1[len(ls1):] = [4]
print(ls1)
# print(ls2)
