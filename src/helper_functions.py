import struct

import numpy as np

from ring.polynomial_ring import PolynomialRing


def encode(polynomial: PolynomialRing) -> bytes:
    """
    Encodes polynomial into bytes (coefficients are serialized into byte array).

    :param polynomial: Polynomial we want to serialize
    :return: Byte array
    """
    format_code = f"{len(polynomial.coefficients.coef)}B"

    # Pack the integers into a byte array
    packed_data = struct.pack(
        format_code, *np.array(polynomial.coefficients.coef).astype(int)
    )

    return packed_data


def decode(encoded_bytes: bytes) -> PolynomialRing:
    """
    Decodes bytes into polynomial (byte array is deserialized to Polynomial).

    :param encoded_bytes: Byte array
    :return: Polynomial from encoded_bytes
    """
    format_code = f"{len(encoded_bytes)}B"

    # Unpack the byte array into integers
    int_array = struct.unpack(format_code, encoded_bytes)

    return PolynomialRing(list(int_array))


if __name__ == "__main__":
    original = PolynomialRing([255] * 256)
    serialized = encode(original)
    deserialized = decode(serialized)

    assert deserialized.coefficients == original.coefficients
