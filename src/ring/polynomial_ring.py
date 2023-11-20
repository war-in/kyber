from typing import List

from numpy.polynomial import polynomial as P


# pylint: disable=inconsistent-return-statements
class PolynomialRing:
    """
    Coefficients are read in this order:

    1 + 2x + 3x^2 + 4x^3 -> [1, 2, 3, 4]
    """

    def __init__(self, coefficients: List):
        self.q = 17
        self.coefficients: P.Polynomial = P.Polynomial(coefficients)
        self.denominator = P.Polynomial([1, 0, 0, 0, 1])

    def __str__(self):
        return str(self.coefficients)

    def __add__(self, other):
        if isinstance(other, PolynomialRing):
            remainder = (self.coefficients + other.coefficients) % self.denominator
            return PolynomialRing(self._elem_wise_modulo(remainder))

        if isinstance(other, int):
            return self + PolynomialRing([other])

        self._raise_type_error("+", type(other).__name__)

    def __radd__(self, other):
        if isinstance(other, int):
            return self + PolynomialRing([other])

        self._raise_type_error("+", type(other).__name__)

    def __mul__(self, other):
        if isinstance(other, PolynomialRing):
            remainder = (self.coefficients * other.coefficients) % self.denominator
            return PolynomialRing(self._elem_wise_modulo(remainder))

        if isinstance(other, int):
            return self * PolynomialRing([other])

        self._raise_type_error("*", type(other).__name__)

    def __rmul__(self, other):
        if isinstance(other, int):
            return self * PolynomialRing([other])

        self._raise_type_error("*", type(other).__name__)

    def __sub__(self, other):
        if isinstance(other, PolynomialRing):
            remainder = (self.coefficients - other.coefficients) % self.denominator
            return PolynomialRing(self._elem_wise_modulo(remainder))

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
            return PolynomialRing(self._elem_wise_modulo(remainder))

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
