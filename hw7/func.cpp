#include <iostream>
#include <vector>
#include <algorithm>

template <typename T>

class Kotainer {
  private:
    std::vector<T> elements;
    static const int MAX_SIZE = 100;

  public:
    Kotainer() {}

    void add(const T& element) {
      if (elements.size() < MAX_SIZE) {
        elements.push_back(element);
      }
    }

    T getMin() const {
      return *std::min_element(elements.begin(), elements.end());
    }
};

template <typename T>
class Holder {
private:
    static const int MAX = 10;
    T* arr_[MAX]; // array of pointers of type T
    int count_;
public:
    Holder() : { count_ = 0; }

    void add(T* ptr) {
        if (count_ >= MAX) return;
        arr_[count_++] = ptr;
    }

    T* get(int pos) const {
        if (pos >= count_) return nullptr;
        return arr_[pos];
    }
};

int main() {
    Holder<std::string> stringHolder;
    Holder<int> intHolder;

    std::string s = "hi";
    int i = 5;

    stringHolder.add(&s);
    intHolder.add(&i);

    std::cout << *stringHolder.get(0) << std::endl; // prints: hi
    std::cout << *intHolder.get(0) << std::endl;    // prints: 5
}
