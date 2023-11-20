from typing import List

from numpy.polynomial import polynomial as P


class PolynomialRing:
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
        elif isinstance(other, int):
            return self + PolynomialRing([other])
        else:
            raise TypeError(
                f"unsupported operand type(s) for +: 'Zn' and '{type(other).__name__}'"
            )

    def __radd__(self, other):
        if isinstance(other, int):
            return self + PolynomialRing([other])
        else:
            raise TypeError(
                f"unsupported operand type(s) for +: '{type(other).__name__}' and 'Zn'"
            )

    def __mul__(self, other):
        if isinstance(other, PolynomialRing):
            remainder = (self.coefficients * other.coefficients) % self.denominator

            return PolynomialRing(self._elem_wise_modulo(remainder))
        elif isinstance(other, int):
            return self * PolynomialRing([other])
        else:
            raise TypeError(
                f"unsupported operand type(s) for *: 'Zn' and '{type(other).__name__}'"
            )

    def __rmul__(self, other):
        if isinstance(other, int):
            return self * PolynomialRing([other])
        else:
            raise TypeError(
                f"unsupported operand type(s) for *: '{type(other).__name__}' and 'Zn'"
            )

    def __sub__(self, other):
        if isinstance(other, PolynomialRing):
            remainder = (self.coefficients - other.coefficients) % self.denominator

            return PolynomialRing(self._elem_wise_modulo(remainder))
        elif isinstance(other, int):
            return self - PolynomialRing([other])
        else:
            raise TypeError(
                f"unsupported operand type(s) for -: 'Zn' and '{type(other).__name__}'"
            )

    def __rsub__(self, other):
        if isinstance(other, int):
            return PolynomialRing([other]) - self
        else:
            raise TypeError(
                f"unsupported operand type(s) for -: '{type(other).__name__}' and 'Zn'"
            )

    def __pow__(self, other):
        if isinstance(other, int):
            remainder = (self.coefficients**other) % self.denominator

            return PolynomialRing(self._elem_wise_modulo(remainder))
        else:
            raise TypeError(
                f"unsupported operand type(s) for **: 'Zn' and '{type(other).__name__}'"
            )

    def _elem_wise_modulo(self, remainder: P.Polynomial) -> List[int]:
        return [coef % self.q for coef in remainder.coef]
