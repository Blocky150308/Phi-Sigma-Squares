import math

lower_limit = int(input("Enter lower limit: "))
upper_limit = int(input("Enter upper limit: "))
smallest_prime_factor = []
for i in range(upper_limit + 1):
    smallest_prime_factor.append(i)
i = 2
while i * i <= upper_limit:
    if smallest_prime_factor[i] == i:
        j = i * i
        while j <= upper_limit:
            if smallest_prime_factor[j] == j:
                smallest_prime_factor[j] = i
            j = j + i
    i = i + 1


def get_prime_factors(number):
    factors = {}
    while number > 1:
        p = smallest_prime_factor[number]
        if p in factors:
            factors[p] = factors[p] + 1
        else:
            factors[p] = 1
        number = number // p
    return factors


def is_prime_power(number):
    if number == 1:
        return True
    factors = get_prime_factors(number)
    if len(factors) == 1:
        return True
    else:
        return False


def is_perfect_square(number):
    root = math.isqrt(number)
    return root * root == number


solutions = []
violations = []
print("starting search now")
for current in range(lower_limit, upper_limit + 1):
    if current == 1:
        factors = {}
        phi_value = 1
        sigma_value = 1
    else:
        factors = get_prime_factors(current)
        phi_value = current
        sigma_value = 1
        for prime in factors:
            exponent = factors[prime]
            phi_value = phi_value // prime * (prime - 1)
            top = prime**(exponent + 1) - 1
            bottom = prime - 1
            sigma_value = sigma_value * (top // bottom)
    product = phi_value * sigma_value
    if is_perfect_square(product):
        solutions.append(current)
        for prime in factors:
            exponent = factors[prime]
            if exponent > 1:
                if is_prime_power(exponent) == False:
                    violations.append((current, prime, exponent))
print("")
print("Total solutions found between", lower_limit, "and", upper_limit, ":", len(solutions))
print("Solutions:", solutions)
print("")
print("Conjecture Check:")
if len(violations) > 0:
    print("Conjecture FAILS for:", violations)
else:
    print("Conjecture holds for all", len(solutions), "solutions in this range. No violations found.")
