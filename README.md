Phi-sigma squares

This is the code and data for my paper, "When the product of the totient and divisor sum is a square". I look for positive integers where multiplying the totient, phi(n), by the sum of the divisors, sigma(n), gives a perfect square.

I also check the exponents in each solution's prime factorization. My original guess was that every exponent greater than 1 would be a prime power. The earlier search found counterexamples, so that guess is false.

Files

- 'original_small_range.py' is my original trial-division program.
- 'original_large_range.py' is my original program using a smallest-prime-factor sieve. I have kept both original programs unchanged.
- 'verify_phi_sigma.py' is the simplified verification program I ran on 8 November 2026.
- 'requirements.txt' lists the package versions I used for the November run.
- 'results' contains the complete results and run record for the new search through 500,000,000.
- 'checks' contains the run records for my checks through 10,000 and 100,000.
- 'previous_results' contains my earlier results, including the solution lists, exception list, graphs and run record.

Running the program

I use 64-bit Python. From this folder, the commands are:

python -m pip install -r requirements.txt
python verify_phi_sigma.py


The program asks for an upper limit. '10000' is a small check; '500000000' covers the full range in my paper. I keep the 'previous_results' folder beside the program because it compares its answers with those earlier lists.

The first search factors numbers in blocks. The second calculates phi and sigma separately by going through multiples and adding divisors. I compare the complete answers from both searches and use SymPy for additional checks.

The second search is slower. Its two main arrays need about 8 GB at the full limit, with extra memory needed for Python and the other packages. Each run starts from the beginning and creates a new results folder and ZIP. A successful full run ends with 'PASS_FULL_RANGE'.

Results

My full run on 8 November 2026 finished with 'PASS_FULL_RANGE'. Both searches found the same 26,627 solutions through 500,000,000, including 70 exceptions to my original guess. The results also matched the earlier lists. The only exponents causing exceptions in that range were 6 and 10. I do not claim that this holds beyond the searched range.

The complete run took 137.81 seconds before the ZIP was created. The first search took 20.38 seconds and the second took 112.55 seconds. I did not measure peak memory use. The old dates, timings and program hash in 'previous_results' belong to the earlier program.

The smaller checks also passed: 71 solutions through 10,000 and 254 through 100,000, with no exceptions in either range. All three runs used the same source file. Its SHA-256 fingerprint is:

274c856441b5eb5f9dfc1686c4c6430f0dd24699ebe1dcae9594d6259b6d9c9e


I treat the probability calculations and intervals as illustrations based on assumptions, not as proofs about the integers.