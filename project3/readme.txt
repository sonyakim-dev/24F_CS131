I struggled with test_struct7 fail test case. It turned out that I was throwing NAME_ERROR instead of TYPE_ERROR.

It took me a long time to figure out the best way to implement struct type.
If I simply put the struct name in type, then I had to check if the struct name is in the struct map every time I check the type.
I wanted to store struct name and also indicate that it is a struct type in the type.
So I crated a new class called StructType and stored the struct name in the class, and the type can be either BasicType or StructType.
I implemented __eq__ and __hash__ method to compare the StructType object.