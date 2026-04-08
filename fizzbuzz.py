#!/usr/bin/env python3
"""
FizzBuzz Solution

A classic programming interview question that demonstrates:
- Basic control flow (loops, conditionals)
- Modulo arithmetic
- String concatenation

The task: Print numbers 1 to N, but:
- Print "Fizz" if divisible by 3
- Print "Buzz" if divisible by 5
- Print "FizzBuzz" if divisible by both 3 and 5
- Print the number otherwise
"""

def fizzbuzz(n: int) -> None:
    """
    Generate FizzBuzz output from 1 to n (inclusive).

    Args:
        n: The upper bound of the range (must be a positive integer)
    """
    for i in range(1, n + 1):
        # Check divisibility in order of most specific to least specific
        # FizzBuzz (both) must come first, otherwise "Fizz" or "Buzz"
        # would match first and we'd never hit the combined case.

        if i % 3 == 0 and i % 5 == 0:
            # Divisible by both 3 and 5 (i.e., divisible by 15)
            output = "FizzBuzz"
        elif i % 3 == 0:
            # Divisible by 3 only
            output = "Fizz"
        elif i % 5 == 0:
            # Divisible by 5 only
            output = "Buzz"
        else:
            # Not divisible by 3 or 5 — print the number
            output = str(i)

        print(output)


def fizzbuzz_list(n: int) -> list[str]:
    """
    Generate FizzBuzz output as a list instead of printing.

    Useful when you want to capture the results for testing
    or further processing.

    Args:
        n: The upper bound of the range

    Returns:
        A list containing the FizzBuzz strings
    """
    results = []

    for i in range(1, n + 1):
        if i % 3 == 0 and i % 5 == 0:
            results.append("FizzBuzz")
        elif i % 3 == 0:
            results.append("Fizz")
        elif i % 5 == 0:
            results.append("Buzz")
        else:
            results.append(str(i))

    return results


if __name__ == "__main__":
    # Run the classic FizzBuzz for numbers 1 to 100
    # This block only executes when the file is run directly
    # (not when imported as a module)

    print("=== Classic FizzBuzz (1-100) ===")
    fizzbuzz(100)

    print("\n=== FizzBuzz as a list (1-20) ===")
    # Demonstrating the list version
    results = fizzbuzz_list(20)
    for item in results:
        print(item)
