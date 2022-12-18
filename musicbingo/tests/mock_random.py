"""
mock version of the random library that always produces repeatable
values.
"""

from random import Random

from musicbingo.primes import PRIME_NUMBERS


class MockRandom(Random):
    """
    Provides a mock version of random.randbelow.
    The values returned are always repeatable.
    """

    def __init__(self):
        seed = ''.join(map(str, PRIME_NUMBERS[:10]))
        super().__init__()
        self.seed(seed, version=2)

    def randbelow(self, max_value: int) -> int:
        """implements secrets.randbelow()"""
        return self.randint(0, max_value - 1)

    def shuffle(self, x, _=None):
        """Shuffle list x in place, and return None."""

        for i in reversed(range(1, len(x))):
            # pick an element in x[:i+1] with which to exchange x[i]
            j = self.randbelow(i+1)
            x[i], x[j] = x[j], x[i]

def main():
    """print output from using MockRandom class"""
    mock_rand = MockRandom()
    numbers = [mock_rand.randbelow(1000) for _ in range(200)]
    print(numbers)


if __name__ == "__main__":
    main()
