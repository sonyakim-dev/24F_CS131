#include <iostream>

int main() {
  int *arr = new int[100];
  delete [ ] arr;
  arr = nullptr;
}
