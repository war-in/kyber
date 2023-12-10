from typing import List

import numpy as np
from numpy.polynomial import polynomial as P


def round_up(x):
    """
    Round x.5 up always
    """
    return round(x + 0.000001)


# pylint: disable=inconsistent-return-statements
class PolynomialRing:
    """
    Coefficients are read in this order:

    1 + 2x + 3x^2 + 4x^3 -> [1, 2, 3, 4]
    """

    def __init__(self, coefficients: List, is_ntt: bool = False):
        self.q = 3329
        self.coefficients: P.Polynomial = P.Polynomial(
            [c % self.q for c in coefficients]
        )
        self.denominator = P.Polynomial([1] + [0] * 255 + [1])
        self.is_ntt = is_ntt

    def get_coefs(self):
        return np.array(self.coefficients.coef).astype(int)

    def __str__(self):
        return str(self.coefficients)

    def __add__(self, other):
        if isinstance(other, PolynomialRing):
            remainder = (self.coefficients + other.coefficients) % self.denominator
            return PolynomialRing(self._elem_wise_modulo(remainder), self.is_ntt)

        if isinstance(other, int):
            return self + PolynomialRing([other])

        self._raise_type_error("+", type(other).__name__)

    def __radd__(self, other):
        if isinstance(other, int):
            return self + PolynomialRing([other])

        self._raise_type_error("+", type(other).__name__)

    def __mul__(self, other):
        if isinstance(other, PolynomialRing):
            if self.is_ntt and other.is_ntt:
                remainder = (
                    P.Polynomial(
                        np.multiply(self.coefficients.coef, other.coefficients.coef)
                    )
                ) % self.denominator
            elif (self.is_ntt and other.is_ntt is False) or (
                self.is_ntt is False and other.is_ntt
            ):
                raise ValueError("Both should be ntt or both should not be ntt")
            else:
                remainder = (self.coefficients * other.coefficients) % self.denominator
            return PolynomialRing(self._elem_wise_modulo(remainder), self.is_ntt)

        if isinstance(other, int):
            return self * PolynomialRing([other])

        self._raise_type_error("*", type(other).__name__)

    def __rmul__(self, other):
        if isinstance(other, int):
            return self * PolynomialRing([other])

        self._raise_type_error("*", type(other).__name__)

    def compress(self, d):
        """
        Compress the polynomial by compressing each coefficent
        NOTE: This is lossy compression
        """
        compress_mod = 2**d
        compress_float = compress_mod / self.q

        return PolynomialRing(
            [round_up(compress_float * c) % compress_mod for c in self.get_coefs()]
        )

    def decompress(self, d):
        """
        Compress the polynomial by compressing each coefficent
        NOTE: This is lossy compression
        """
        compress_mod = 2**d
        compress_float = self.q / compress_mod

        return PolynomialRing([round_up(compress_float * c) for c in self.get_coefs()])

    def __sub__(self, other):
        if isinstance(other, PolynomialRing):
            remainder = (self.coefficients - other.coefficients) % self.denominator
            return PolynomialRing(self._elem_wise_modulo(remainder), self.is_ntt)

        if isinstance(other, int):
            return self - PolynomialRing([other])

        self._raise_type_error("-", type(other).__name__)

    def __rsub__(self, other):
        if isinstance(other, int):
            return PolynomialRing([other]) - self

        self._raise_type_error("-", type(other).__name__)

    def __pow__(self, other):
        if isinstance(other, int):
            remainder = (self.coefficients**other) % self.denominator
            return PolynomialRing(self._elem_wise_modulo(remainder), self.is_ntt)

        self._raise_type_error("**", type(other).__name__)

    def _elem_wise_modulo(self, remainder: P.Polynomial) -> List[int]:
        return [coef % self.q for coef in remainder.coef]

    def _raise_type_error(self, operand: str, type_name: str):
        raise TypeError(
            f"unsupported operand type '{operand}' for: 'PolynomialRing' and '{type_name}'"
        )


if __name__ == "__main__":
    a = PolynomialRing([1, 1, 1, 1])
    b = PolynomialRing([1, 0, 0, 0])

    print(a + b)
