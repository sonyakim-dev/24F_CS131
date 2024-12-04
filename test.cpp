#include <iostream>
using namespace std;

#define SWAP(X,Y) { int temp=X; X=Y; Y=temp;}
// variable capture bug! 
int main() {
  int a = 2, temp = 17;
  cout << a << " " << temp << endl;
  SWAP(a, temp); 
  cout << a << " " << temp << endl;
}
