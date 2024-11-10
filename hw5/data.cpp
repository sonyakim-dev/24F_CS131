class my_shared_ptr {
  private:
    int* ptr = nullptr;
    int* refCount = nullptr; // a)

  public:
    // b) constructor
    my_shared_ptr(int * ptr) {
      this->ptr = ptr;
      refCount = new int(1);
    }
    // c) copy constructor
    my_shared_ptr(const my_shared_ptr & other) {
      ptr = other.ptr;
      refCount = other.refCount;
      (*refCount)++;
    }
    // d) destructor
    ~my_shared_ptr()
    {
      (*refCount)--;
      if (*refCount == 0) {
        delete ptr;
        delete refCount;
      }
    }
    // e) copy assignment
    my_shared_ptr& operator=(const my_shared_ptr & obj) {
      if (this != &obj) {
        (*refCount)--;
        if (*refCount == 0) {
          delete ptr;
          delete refCount;
        }
        ptr = obj.ptr;
        refCount = obj.refCount;
        (*refCount)++;
      }
      return *this;
    }
};
