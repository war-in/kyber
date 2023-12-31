import hashlib
from typing import List

import numpy as np
import sympy
from Cryptodome.Random import get_random_bytes

from helper_functions import decode, encode
from ring.polynomial_ring import PolynomialRing

DEFAULT_PARAMETERS = {
    "kyber_512": {
        "k": 2,
        "eta_1": 3,
        "eta_2": 2,
        "du": 10,
        "dv": 4,
    },
    "kyber_768": {
        "k": 3,
        "eta_1": 2,
        "eta_2": 2,
        "du": 10,
        "dv": 4,
    },
    "kyber_1024": {
        "k": 4,
        "eta_1": 2,
        "eta_2": 2,
        "du": 11,
        "dv": 5,
    },
}


class Kyber:
    def __init__(self, version):
        self.n = 256
        self.k = version["k"]
        self.q = 3329
        self.eta_1 = version["eta_1"]
        self.eta_2 = version["eta_2"]
        self.du = version["du"]
        self.dv = version["dv"]

        self.A = np.empty((self.k, self.k), dtype=object)
        self.s = np.empty(self.k, dtype=object)
        self.e = np.empty(self.k, dtype=object)

    def CBD(self, B, eta):
        """
        Centered binomial distribution

        Parameters:
        - B (bytes): Input bytes, size: self.eta_1 * 64 .
        - eta (int): Security parameter.

        Returns:
        - np.ndarray: Array of integers, size: 256.
        """

        binary_representation = "".join(format(byte, "08b") for byte in B)
        beta = [int(bit) for bit in binary_representation]
        f = np.zeros(self.n)

        for i in range(0, 255):
            a = sum(beta[2 * i * eta + j] for j in range(eta))
            b = sum(beta[2 * i * eta + eta + j] for j in range(eta))
            f[i] = a - b

        return list(f.astype(int))

    def parse(self, B):
        """
        Parameters:
        - B (bytes): Input bytes, size: 3 * self.n.

        Returns:
        - np.ndarray: Array of integers, size: self.n.
        """

        i = 0
        j = 0
        a = np.zeros(self.n)

        while j < self.n:
            d1 = B[i] + 256 * (B[i + 1] % 16)
            d2 = (B[i + 1] // 16) + 16 * B[i + 2]

            if d1 < self.q:
                a[j] = d1
                j += 1

            if d2 < self.q and j < self.n:
                a[j] = d2
                j += 1

            i += 3

        return list(a.astype(int))

    def apply_ntt(self, polynomials):
        return np.array(
            [
                PolynomialRing(sympy.ntt(polynomial.get_coefs(), self.q), is_ntt=True)
                for polynomial in polynomials
            ]
        )

    def apply_intt(self, polynomials):
        return np.array(
            [
                PolynomialRing(sympy.intt(polynomial.get_coefs(), self.q))
                for polynomial in polynomials
            ]
        )

    def key_gen(self):
        """
        Parameters: None

        Should return:
        - pk (np.ndarray): Public key.
        - sk (np.ndarray): Secret Key.
        """

        d = get_random_bytes(32)  # get random 32 bytes
        d_hash = hashlib.sha3_512(d).digest()  # G(d)
        rho, sigma = d_hash[:32], d_hash[32:]
        N = 0

        for i in range(0, self.k):
            for j in range(0, self.k):
                self.A[i, j] = PolynomialRing(
                    self.parse(
                        hashlib.shake_128(rho + bytes([j]) + bytes([i])).digest(
                            3 * self.n
                        )
                    ),
                    is_ntt=True,
                )

        for i in range(0, self.k):
            self.s[i] = PolynomialRing(
                self.CBD(
                    hashlib.shake_256(sigma + bytes([N])).digest(self.eta_1 * 64),
                    self.eta_1,
                )
            )
            N += 1

        for i in range(0, self.k):
            self.e[i] = PolynomialRing(
                self.CBD(
                    hashlib.shake_256(sigma + bytes([N])).digest(self.eta_1 * 64),
                    self.eta_1,
                )
            )
            N += 1

        self.s = self.apply_ntt(self.s)
        self.e = self.apply_ntt(self.e)

        t = self.A @ self.s + self.e

        pk = bytes()
        for poly in t:
            pk += encode(poly, 12)
        sk = bytes()
        for poly in self.s:
            sk += encode(poly, 12)

        return pk + rho, sk

    def enc(self, pk, m):
        N = 0
        l = []
        for i in range(self.k):
            l.append(decode(pk[i * 12 * 32 : (i + 1) * 12 * 32], 12))
            l[i].is_ntt = True
        t = np.array(l)
        rho = pk[-32:]
        A_t = np.empty((self.k, self.k), dtype=object)

        r = np.empty(self.k, dtype=object)
        e1 = np.empty(self.k, dtype=object)

        for i in range(self.k):
            for j in range(self.k):
                A_t[i][j] = PolynomialRing(
                    self.parse(
                        hashlib.shake_128(rho + bytes([i]) + bytes([j])).digest(
                            3 * self.n
                        )
                    ),
                    is_ntt=True,
                )

        for i in range(0, self.k):
            r[i] = PolynomialRing(
                self.CBD(
                    hashlib.shake_256(rho + bytes([N])).digest(self.eta_1 * 64),
                    self.eta_1,
                )
            )
            N += 1

        for i in range(0, self.k):
            e1[i] = PolynomialRing(
                self.CBD(
                    hashlib.shake_256(rho + bytes([N])).digest(self.eta_2 * 64),
                    self.eta_2,
                )
            )
            N += 1

        e2 = PolynomialRing(
            self.CBD(
                hashlib.shake_256(rho + bytes([N])).digest(self.eta_2 * 64),
                self.eta_2,
            )
        )

        r = self.apply_ntt(r)
        u = self.apply_intt(A_t @ r) + e1
        v = self.apply_intt(np.array([t.T @ r]))[0] + e2 + decode(m, 1).decompress(1)
        c1 = bytes()
        for polynomialRing in u:
            c1 += encode(polynomialRing.compress(self.du), self.du)
        c2 = encode(v.compress(self.dv), self.dv)
        return c1 + c2

    def dec(self, sk, c):
        u = []
        for i in range(self.k):
            u.append(
                decode(
                    c[i * self.du * 32 : (i + 1) * self.du * 32], self.du
                ).decompress(self.du)
            )
        u = np.array(u)
        v = c[-self.dv * 32 :]
        v = np.array(decode(v, self.dv).decompress(self.dv))
        s = []
        for i in range(self.k):
            s.append(decode(sk[i * 12 * 32 : (i + 1) * 12 * 32], 12))
            s[i].is_ntt = True
        s = np.array(s)
        m = self.apply_intt(np.array([s.T @ self.apply_ntt(u)]))
        m = (v - m)[0]
        m = encode(m.compress(1), 1)
        return m


if __name__ == "__main__":
    kyber512 = Kyber(DEFAULT_PARAMETERS["kyber_512"])
    pk, sk = kyber512.key_gen()
    m = bytes([128] * 32)
    encoded = kyber512.enc(pk, m)
    decoded = kyber512.dec(sk, encoded)
    print(m == decoded)
    print(m)
    print(decoded)
