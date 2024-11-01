// HASK 17
#include <iostream>

int longestRun(std::vector<bool> arr) {
  int max = 0;
  int count = 0;

  for (bool a : arr) {
    if (a) {
      count++;
    }
    max = std::max(max, count);
    if (!a) {
      count = 0;
    }
  }
  return max;
}

#include <queue>
using namespace std;

class Tree {
public:
  unsigned value;
  vector<Tree *> children;
  Tree(unsigned value, vector<Tree *> children) {
    this->value = value;
    this->children = children;
  }
};

unsigned maxTreeValue(Tree *root) {
  if (root == nullptr) return 0;

  unsigned max = root->value;
  queue<Tree *> queue;
  queue.push(root);

  while (!queue.empty()) {
    Tree* curr = queue.front();
    queue.pop();
    max = std::max(max, curr->value);

    for (Tree *child : curr->children) {
      queue.push(child);
    }
  }
  return max;
}


int main() {
  // std::vector<bool> arr = {true, false, true, true};
  // std::cout << longestRun(arr) << std::endl;
  cout << maxTreeValue(new Tree(1, {new Tree(2, {new Tree(3, {new Tree(9, {})}), new Tree(4, {})}), new Tree(10, {})})) << endl;
  return 0;
}
