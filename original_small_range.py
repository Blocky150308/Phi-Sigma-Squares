import math

lower_limit = int(input("Enter lower limit: "))
upper_limit = int(input("Enter upper limit: "))


def calculate_sigma(number):
    total = 0
    divisor = 1
    while divisor * divisor <= number:
        if number % divisor == 0:
            total = total + divisor
            if divisor != number // divisor:
                total = total + number // divisor
        divisor = divisor + 1
    return total


def calculate_phi(number):
    result = number
    temp = number
    prime = 2
    while prime * prime <= temp:
        if temp % prime == 0:
            while temp % prime == 0:
                temp = temp // prime
            result = result - result // prime
        prime = prime + 1
    if temp > 1:
        result = result - result // temp
    return result


def is_perfect_square(number):
    root = math.isqrt(number)
    return root * root == number


def get_prime_factors(number):
    factors = {}
    divisor = 2
    while divisor * divisor <= number:
        while number % divisor == 0:
            if divisor in factors:
                factors[divisor] = factors[divisor] + 1
            else:
                factors[divisor] = 1
            number = number // divisor
        divisor = divisor + 1
    if number > 1:
        if number in factors:
            factors[number] = factors[number] + 1
        else:
            factors[number] = 1
    return factors


def is_prime_power(number):
    if number == 1:
        return True
    prime = 2
    while prime <= number:
        if number % prime == 0:
            while number % prime == 0:
                number = number // prime
            if number == 1:
                return True
            else:
                return False
        prime = prime + 1
    return False


solutions = []
violations = []
print("starting search now")
for current in range(lower_limit, upper_limit + 1):
    phi_val = calculate_phi(current)
    sigma_val = calculate_sigma(current)
    product = phi_val * sigma_val
    if is_perfect_square(product):
        solutions.append(current)
        prime_factors = get_prime_factors(current)
        for prime in prime_factors:
            exponent = prime_factors[prime]
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
