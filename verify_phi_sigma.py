import math
import csv
import json
import time
import sys
import platform
import random
import hashlib
import shutil
from pathlib import Path
from datetime import datetime, timezone
from importlib.metadata import version
from bisect import bisect_right
import numpy as np
from numba import njit
import psutil
import sympy as sp
from scipy.stats import beta
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def get_primes(limit):
    sieve = [True] * (limit + 1)
    sieve[0] = False
    if limit >= 1:
        sieve[1] = False
    primes = []
    for p in range(2, limit + 1):
        if sieve[p]:
            primes.append(p)
            for multiple in range(p * p, limit + 1, p):
                sieve[multiple] = False
    return np.array(primes, dtype=np.int64)


def is_prime_power(number):
    if number < 2:
        return False
    divisor = 2
    while divisor * divisor <= number:
        if number % divisor == 0:
            while number % divisor == 0:
                number = number // divisor
            return number == 1
        divisor = divisor + 1
    return True


@njit
def first_search(lower, upper, primes):
    remaining = np.arange(lower, upper + 1, dtype=np.int64)
    products = np.ones(upper - lower + 1, dtype=np.int64)
    for p in primes:
        if p * p > upper:
            break
        start = ((lower + p - 1) // p) * p
        for number in range(start, upper + 1, p):
            i = number - lower
            power = np.int64(1)
            while remaining[i] % p == 0:
                remaining[i] = remaining[i] // p
                power = power * p
            if power > 1:
                products[i] = products[i] * (power // p) * (power * p - 1)
    solutions = []
    for i in range(upper - lower + 1):
        if remaining[i] > 1:
            products[i] = products[i] * (remaining[i] * remaining[i] - 1)
        value = products[i]
        if value % 4 == 2 or value % 4 == 3:
            continue
        root = np.int64(math.sqrt(value))
        while root * root > value:
            root = root - 1
        while (root + 1) * (root + 1) <= value:
            root = root + 1
        if root * root == value:
            solutions.append((np.int64(lower + i), root))
    return solutions


@njit
def integer_root(number):
    lower = np.int64(0)
    upper = min(number, np.int64(500000000)) + 1
    while upper - lower > 1:
        middle = (lower + upper) // 2
        if middle * middle <= number:
            lower = middle
        else:
            upper = middle
    return lower


@njit
def second_search(limit):
    phi = np.arange(limit + 1, dtype=np.int64)
    sigma = np.zeros(limit + 1, dtype=np.int64)
    for p in range(2, limit + 1):
        if phi[p] == p:
            for number in range(p, limit + 1, p):
                phi[number] = phi[number] - phi[number] // p
        if p % 10000000 == 0:
            print("Totient sieve:", p)
    for divisor in range(1, limit + 1):
        for number in range(divisor, limit + 1, divisor):
            sigma[number] = sigma[number] + divisor
        if divisor % 10000000 == 0:
            print("Divisor sum sieve:", divisor)
    solutions = []
    for number in range(1, limit + 1):
        value = phi[number] * sigma[number]
        if value % 5 == 0 or value % 5 == 1 or value % 5 == 4:
            root = integer_root(value)
            if root * root == value:
                solutions.append((np.int64(number), root))
        if number % 10000000 == 0:
            print("Square checks:", number)
    return solutions


def check_number(number):
    phi = int(sp.totient(number))
    sigma = int(sp.divisor_sigma(number))
    root = math.isqrt(phi * sigma)
    return phi, sigma, root, root * root == phi * sigma


def factor_text(number):
    parts = []
    for p, a in sorted(sp.factorint(number).items()):
        if a == 1:
            parts.append(str(p))
        else:
            parts.append(str(p) + "^" + str(a))
    return " * ".join(parts) if parts else "1"


def save_csv(name, headings, rows):
    with open(output / name, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headings)
        writer.writerows(rows)


def save_json(name, data):
    with open(output / name, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


limit = int(input("Enter upper limit (1 to 500000000): "))
if limit < 1 or limit > 500000000:
    raise ValueError("The upper limit must be between 1 and 500000000.")
if sys.maxsize <= 2**32:
    raise RuntimeError("This needs 64-bit Python.")
if psutil.virtual_memory().available < 16 * (limit + 1) + 2 * 1024**3:
    raise RuntimeError("Close other programs first. There is not enough free memory.")

base = Path(__file__).resolve().parent
output = base / ("results_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
output.mkdir()
shutil.copyfile(__file__, output / "verify_phi_sigma.py")
started = time.perf_counter()
summary = {"status": "RUNNING", "limit": limit, "program_version": "simple-1",
           "started_utc": datetime.now(timezone.utc).isoformat(),
           "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "python": sys.version, "system": platform.platform(),
           "processor": platform.processor(), "physical_cores": psutil.cpu_count(logical=False),
           "logical_cores": psutil.cpu_count(), "ram_bytes": psutil.virtual_memory().total,
           "available_ram_bytes": psutil.virtual_memory().available,
           "second_search_array_bytes": 16 * (limit + 1),
           "methods": ["segmented local product", "totient sieve and divisor addition sieve"]}
summary["packages"] = {}
for package in ["numpy", "numba", "llvmlite", "sympy", "scipy", "matplotlib", "psutil"]:
    summary["packages"][package] = version(package)
save_json("summary.json", summary)
primes = get_primes(math.isqrt(limit))

print("Checking the first", min(limit, 10000), "integers first...")
small = min(limit, 10000)
small_first = first_search(1, small, primes)
small_second = second_search(small)
small_reference = []
for number in range(1, small + 1):
    phi, sigma, root, square = check_number(number)
    if square:
        small_reference.append((number, root))
if small_first != small_second or small_first != small_reference:
    raise RuntimeError("The methods disagree in the small check.")
for root in [1, 2, 3, 63, 64, 65, 10000, 100000000, 500000000]:
    for number in [root * root - 1, root * root, root * root + 1]:
        if integer_root(number) != math.isqrt(number):
            raise RuntimeError("The integer square root check failed.")
for exponent in range(1, 40):
    if is_prime_power(exponent) != (exponent > 1 and len(sp.factorint(exponent)) == 1):
        raise RuntimeError("The prime power check failed.")
summary["initial_checks_seconds"] = time.perf_counter() - started

print("Starting the first full search...")
start = time.perf_counter()
solutions = []
for lower in range(1, limit + 1, 5000000):
    upper = min(lower + 4999999, limit)
    for number, root in first_search(lower, upper, primes):
        solutions.append((int(number), int(root)))
    print("Checked", upper, "out of", limit, "- solutions:", len(solutions), flush=True)
summary["first_search_seconds"] = time.perf_counter() - start
summary["block_size"] = 5000000
save_csv("solutions.csv", ["n", "sqrt_phi_sigma"], solutions)

print("Starting the second search. This one takes longer...", flush=True)
start = time.perf_counter()
second = [(int(number), int(root)) for number, root in second_search(limit)]
summary["second_search_seconds"] = time.perf_counter() - start
save_csv("independent_solutions.csv", ["n", "sqrt_phi_sigma"], second)
if solutions != second:
    raise RuntimeError("The two full searches disagree.")

print("Checking the solutions with SymPy...")
start = time.perf_counter()
full_rows = []
violations = []
frequencies = {}
for number, root in solutions:
    phi, sigma, checked_root, square = check_number(number)
    if not square or root != checked_root:
        raise RuntimeError("SymPy disagrees at " + str(number))
    factors = sp.factorint(number)
    local_product = 1
    for p, a in factors.items():
        p, a = int(p), int(a)
        local_product = local_product * p**(a - 1) * (p**(a + 1) - 1)
        if a > 1 and not is_prime_power(a):
            violations.append([number, factor_text(number), p, a, root])
            frequencies[p, a] = frequencies.get((p, a), 0) + 1
    if local_product != phi * sigma:
        raise RuntimeError("The product formula disagrees at " + str(number))
    full_rows.append([number, factor_text(number), phi, sigma, root])
save_csv("solutions_with_factors.csv", ["n", "factorization", "phi", "sigma", "sqrt_phi_sigma"], full_rows)
save_csv("violations.csv", ["n", "factorization", "offending_prime", "offending_exponent", "sqrt_phi_sigma"], violations)
answers = dict(solutions)
sample = random.Random(20261022).sample(range(1, limit + 1), min(limit, 10000))
for number in sample:
    phi, sigma, root, square = check_number(number)
    if square != (number in answers) or (square and answers[number] != root):
        raise RuntimeError("The sample check failed at " + str(number))
summary["sympy_check_seconds"] = time.perf_counter() - start

with open(base / "previous_results" / "solutions.csv", newline="", encoding="utf-8") as file:
    previous = [(int(row["n"]), int(row["sqrt_phi_sigma"])) for row in csv.DictReader(file) if int(row["n"]) <= limit]
if solutions != previous:
    raise RuntimeError("The solutions do not match the earlier results.")
with open(base / "previous_results" / "violations.csv", newline="", encoding="utf-8") as file:
    previous = [(int(row["n"]), int(row["offending_prime"]), int(row["offending_exponent"]))
                for row in csv.DictReader(file) if int(row["n"]) <= limit]
if sorted((row[0], row[2], row[3]) for row in violations) != sorted(previous):
    raise RuntimeError("The exceptions do not match the earlier results.")

examples = []
for number in [3187917, 3488704, 94764032, 1510129664, 4294934528, 17512206336]:
    phi, sigma, root, square = check_number(number)
    if not square:
        raise RuntimeError("An example failed: " + str(number))
    examples.append({"n": number, "factorization": factor_text(number), "phi": phi,
                     "sigma": sigma, "sqrt_phi_sigma": root})
save_json("explicit_examples.json", examples)
mersenne_examples = []
for exponent in [5, 17, 89, 107]:
    q = 2**exponent - 1
    state = 4
    for i in range(exponent - 2):
        state = (state * state - 2) % q
    if state != 0 or not sp.isprime(exponent):
        raise RuntimeError("A Mersenne prime check failed.")
    a = exponent - 2
    root = 2**(a + 1) * (2**(a + 1) - 1)
    if 2**(a - 1) * (2**(a + 1) - 1) * (q * q - 1) != root * root:
        raise RuntimeError("The Mersenne construction check failed.")
    mersenne_examples.append({"a": a, "mersenne_exponent": exponent,
                              "n": str(2**a * q), "sqrt_phi_sigma": str(root)})
save_json("mersenne_examples.json", mersenne_examples)

exposure = []
for prime in primes:
    p = int(prime)
    a = 2
    while p**a <= limit:
        if not is_prime_power(a):
            total = limit // p**a - limit // p**(a + 1)
            count = frequencies.get((p, a), 0)
            low = 0.0 if count == 0 else float(beta.ppf(0.025, count, total - count + 1))
            high = 1.0 if count == total else float(beta.ppf(0.975, count + 1, total - count))
            exposure.append([p, a, total, count, count / total, low, high])
        a = a + 1
exposure.sort(key=lambda row: (row[1], row[0]))
save_csv("exposure.csv", ["prime", "exponent", "exposure", "solutions", "rate", "model_ci95_low", "model_ci95_high"], exposure)
poisson = []
groups = {(row[0], row[1]): row for row in exposure}
for source in [(2, 6), (2, 10)]:
    for target in [(2, 12), (2, 14)]:
        if source in groups and target in groups:
            expected = groups[source][4] * groups[target][2]
            poisson.append({"rate_source": source, "target": target, "expected_count": expected,
                            "poisson_probability_zero": math.exp(-expected)})
save_json("illustrative_poisson.json", {"note": "I use this only as an illustration. Equal rates and independence are not proved.", "calculations": poisson})

numbers = [number for number, root in solutions]
blocks = []
for lower in range(1, min(limit, 1000000) + 1, 100000):
    upper = min(lower + 99999, limit)
    count = bisect_right(numbers, upper) - bisect_right(numbers, lower - 1)
    blocks.append([lower, upper, count, 100 * count / (upper - lower + 1)])
save_csv("first_million_blocks.csv", ["lower", "upper", "solutions", "percentage"], blocks)
checkpoints = sorted(set(int(round(x)) for x in np.geomspace(1, limit, 300)))
counts = [bisect_right(numbers, x) for x in checkpoints]
proportions = [count / x for x, count in zip(checkpoints, counts)]
save_csv("cumulative_checkpoints.csv", ["x", "count", "proportion"], zip(checkpoints, counts, proportions))
figure, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
axes[0].step(numbers, range(1, len(numbers) + 1), where="post")
axes[0].set(xlabel="Upper bound", ylabel="Number of solutions", title="Total solutions")
axes[1].plot(checkpoints, proportions)
axes[1].set(xlabel="Upper bound", ylabel="Proportion", title="Proportion of solutions")
for axis in axes:
    if limit > 1:
        axis.set_xscale("log")
        axis.set_yscale("log")
    axis.grid(alpha=0.3)
figure.savefig(output / "cumulative_count.png", dpi=220)
figure.savefig(output / "cumulative_count.pdf")
plt.close(figure)
if exposure:
    rates = np.array([row[4] for row in exposure])
    lower = np.array([row[5] for row in exposure])
    upper = np.array([row[6] for row in exposure])
    figure, axis = plt.subplots(figsize=(9, max(4, len(exposure) * 0.3 + 1.5)), constrained_layout=True)
    axis.errorbar(rates, range(len(exposure)), xerr=[rates - lower, upper - rates], fmt="o", capsize=2)
    axis.set_yticks(range(len(exposure)), [str((row[0], row[1])) + "  " + str(row[3]) + "/" + str(row[2]) for row in exposure])
    axis.invert_yaxis()
    axis.set_xscale("symlog", linthresh=0.000001)
    axis.set_xlim(-0.0000001, 1.05)
    axis.set(xlabel="Observed rate and conditional 95% interval", ylabel="(prime, exponent)  solutions / eligible integers",
             title="Intervals under an independent-trial model\nIndependence is not proved here")
    axis.grid(axis="x", alpha=0.3)
    figure.savefig(output / "exposure_rates.png", dpi=220)
    figure.savefig(output / "exposure_rates.pdf")
    plt.close(figure)

summary["status"] = "PASS_FULL_RANGE" if limit == 500000000 else "PASS_PARTIAL_RANGE"
summary["solution_count"] = len(solutions)
summary["exception_count"] = len(set(row[0] for row in violations))
summary["offending_pairs"] = len(violations)
summary["exception_breakdown"] = [[p, a, count] for (p, a), count in sorted(frequencies.items())]
summary["counts"] = {str(x): bisect_right(numbers, x) for x in [1000000, 10000000, 500000000] if x <= limit}
summary["full_list_agreement"] = True
summary["previous_results_agree"] = True
summary["sympy_positives_checked"] = len(solutions)
summary["complete_small_range_checked"] = small
summary["sample_size"] = len(sample)
summary["sample_seed"] = 20261022
summary["explicit_and_mersenne_checks_passed"] = True
summary["exposure_groups"] = len(exposure)
summary["finished_utc"] = datetime.now(timezone.utc).isoformat()
summary["total_seconds_before_archiving"] = time.perf_counter() - started
save_json("summary.json", summary)
archive = shutil.make_archive(str(output), "zip", root_dir=output)
print("Total solutions:", len(solutions))
print("Exceptions:", summary["exception_count"])
print("Status:", summary["status"])
print("Results saved in:", archive)
