# Transaction-Ancestry-Sets
Use a programming language of your choice to build a basic transaction ancestry set calculator.

Every bitcoin transaction has inputs and outputs. When a transaction A uses an output of transaction B, B is a direct parent of A.
The transaction ancestry of A are all direct and indirect parents of A.

Write a program that:
Fetches all transactions for a block 680000
Determines the ancestor set for every transaction in the block (all ancestors need to be in the block as well)
Prints the 10 transaction with the largest ancestry sets.
