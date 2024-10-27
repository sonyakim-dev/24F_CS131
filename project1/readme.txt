I was keep failing the 'test_input2' and 'test_input3'.
I did thorough test, but I always got the correct answer.
The problem was that if there is no arg passed to inputi, I set the prompt as "" and called super().output(prompt).

Expected output:
['15']
Actual output:
['', '15']

The solution is that calling super().output(prompt) only when there is one argument.