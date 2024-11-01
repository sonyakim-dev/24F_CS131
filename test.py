# class Node:
#     def __init__(self, value: int, children=[]):
#         self.value = value
#         self.children = children
      
# def largest_val (root):
#   if not root.children: return root.value
#   max_subtree = max(largest_val(child) for child in root.children)
#   return max(root.value, max_subtree)

# def height(root):
#   if not root.children: return 1
#   return 1 + max(height(child) for child in root.children)


# root = Node(1, [
#     Node(2, [
#         Node(4),
#         Node(5),
#         Node(9)
#     ]),
#     Node(3, [
#         Node(6),
#         Node(7, [
#             Node(8)
#         ])
#     ])
# ])

# print(height(root))


# divis = lambda n, m: [i for i in range(n, m+1) if i % 5 == 0 or i % 7 == 0 or i % 9 == 0]

class Pet:
    def __init__(self):
        print("Pet")
        self.var = 1
    def play(self):
        self.do_playful_thing()
    def do_playful_thing(self):
        print("Pet play")
    def print_var(self):
        print(self.var)
		
class Dog(Pet):
    def __init__(self):
        self.var = 2
        super().__init__()
        print("Dog")
    def do_playful_thing(self):
        print("Dog play")
    def bark(self):
        super().do_playful_thing()
  
x = Dog()
x.play()
x.print_var()
x.bark()
