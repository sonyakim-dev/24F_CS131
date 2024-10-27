class Node:
    def __init__(self, value: int, children=[]):
        self.value = value
        self.children = children
      
def largest_val (root):
  if not root.children: return root.value
  max_subtree = max(largest_val(child) for child in root.children)
  return max(root.value, max_subtree)

def height(root):
  if not root.children: return 1
  return 1 + max(height(child) for child in root.children)


root = Node(1, [
    Node(2, [
        Node(4),
        Node(5),
        Node(9)
    ]),
    Node(3, [
        Node(6),
        Node(7, [
            Node(8)
        ])
    ])
])

print(height(root))


divis = lambda n, m: [i for i in range(n, m+1) if i % 5 == 0 or i % 7 == 0 or i % 9 == 0]
