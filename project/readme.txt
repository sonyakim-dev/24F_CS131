I combined the provided Carey's code with my interpreterv1 code.

I used Enum libray to check if a operation is a member of the Enum class.
However, the 'in' operation for enum class is not supported for Python v13.11 and I was using v3.12.

I struggled how to set local scopes diffrently.
This blog post(https://craftinginterpreters.com/statements-and-state.html#statements) helped me,
and I found the link in someone's Campuswire post.
ChatGPT suggested using contextmanager for stability, but I didn't use it eventually.

I also struggled handling return statement.
I eventually decided to return a flag to check if the statement has return or not along with Value.
