import time

from Cryptodome.Random import get_random_bytes

from src.kyber import DEFAULT_PARAMETERS, Kyber


def test_performance(kyber_type: str, tests_number=1000):
    print(kyber_type)
    kyber512 = Kyber(DEFAULT_PARAMETERS[kyber_type])
    successes = 0
    start = time.time()
    for _ in range(tests_number):
        pk, sk = kyber512.key_gen()
        m = get_random_bytes(32)
        encoded = kyber512.enc(pk, m)
        decoded = kyber512.dec(sk, encoded)
        if m == decoded:
            successes += 1
    time_measured = time.time() - start
    print(f"Success rate: {100.0 * successes / tests_number} %")
    print(f"Time: { time_measured / tests_number} s")
    print()


if __name__ == "__main__":
    test_performance("kyber_1024", 1000)
    test_performance("kyber_768", 1000)
    test_performance("kyber_512", 1000)
