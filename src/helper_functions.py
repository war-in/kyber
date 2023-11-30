from ring.polynomial_ring import PolynomialRing


def encode(polynomial: PolynomialRing, l: int) -> bytes:
    """
    Encodes polynomial into bytes (coefficients are serialized into byte array).

    :param l: ???
    :param polynomial: Polynomial we want to serialize
    :return: Byte array
    """
    bit_string = "".join(format(c, f"0{l}b")[::-1] for c in polynomial.get_coefs())
    return bytes(
        [int(bit_string[i : i + 8][::-1], 2) for i in range(0, len(bit_string), 8)]
    )


def bytes_to_bits(input_bytes):
    bit_string = "".join(format(byte, "08b")[::-1] for byte in input_bytes)
    return list(map(int, list(bit_string)))


def decode(encoded_bytes: bytes, l: int) -> PolynomialRing:
    """
    Decodes bytes into polynomial (byte array is deserialized to Polynomial).

    :param l: ???
    :param encoded_bytes: Byte array
    :return: Polynomial from encoded_bytes
    """
    coefficients = [0] * 255
    list_of_bits = bytes_to_bits(encoded_bytes)
    for i in range(256):
        coefficients[i] = sum(list_of_bits[i * l + j] << j for j in range(l))

    return PolynomialRing(list(coefficients))


if __name__ == "__main__":
    original = PolynomialRing([255] * 256)
    serialized = encode(original, 12)
    deserialized = decode(serialized, 12)

    assert deserialized.coefficients == original.coefficients
