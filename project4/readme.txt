Someone posted this file (https://www.cs.virginia.edu/~evans/cs150/book/ch13-laziness-0402.pdf) on Campuswire,
and it helped me a lot with implementing lazy evaluation.

I was keep failing test_lazy_cache2 because a variable can be either Value type or Closure type.
Once a variable is evaluated, I reassigned the variable to Value type, and it caused the problem.
So I made a variable can be only a Value type and the Value may contain Closure as a value.
Once a variable is evaluated, instead of reassigning the whole new Value class, I updated Value.value and Value.type.