class Node:
    def __init__(self, val):
        self.value = val
        self.next = None
        

# CNTL2 - Part A
class HashTable:
    def __init__(self, buckets):
        self.array = [None] * buckets
    def insert(self, val):
        bucket = hash(val) % len(self.array)
        tmp_head = Node(val)
        tmp_head.next = self.array[bucket]
        self.array[bucket] = tmp_head
    def __iter__(self):
       return self.__generator(self)
    def __generator(self):
        for bucket in self.array:
            while bucket:
                yield bucket.value
                bucket = bucket.next


# CNTL2 - Part B
class HashTable:
    def __init__(self, buckets):
        self.array = [None] * buckets
    def insert(self, val):
        bucket = hash(val) % len(self.array)
        tmp_head = Node(val)
        tmp_head.next = self.array[bucket]
        self.array[bucket] = tmp_head
    def __iter__(self):
       return HashTableIterator(self.array)
   
class HashTableIterator:
    def __init__(self, array):
        self.array = array
        self.index = -1
        self.node = None
    def __next__(self):
        while self.node is None:
            self.index += 1
            if self.index == len(self.array):
                raise StopIteration
            self.node = self.array[self.index]
        value = self.node.value
        self.node = self.node.next
        return value


# CNTL2 - Part C         
ht = HashTable(5)
ht.insert("a")
ht.insert("b")
ht.insert("c")
ht.insert("c")

for value in ht:
    print(value)


# CNTL2 - Part D
iter = ht.__iter__()
try:
    while True:
        print(iter.__next__())
except StopIteration:
    pass


# CNTL2 - Part E
class HashTable:
    def __init__(self, buckets):
        self.array = [None] * buckets
    def insert(self, val):
        bucket = hash(val) % len(self.array)
        tmp_head = Node(val)
        tmp_head.next = self.array[bucket]
        self.array[bucket] = tmp_head
    def forEach(self, func):
        for bucket in self.array:
            while bucket:
                func(bucket.value)
                bucket = bucket.next
                
ht.forEach(lambda x: print(x))
