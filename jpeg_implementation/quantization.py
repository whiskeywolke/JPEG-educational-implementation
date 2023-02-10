import numpy as np

# https://www.math.cuhk.edu.hk/~lmlui/dct.pdf

quantization_10_values = [
    80, 55, 50, 80, 120, 200, 255, 255,
    60, 60, 70, 95, 130, 255, 255, 255,
    70, 65, 80, 120, 200, 255, 255, 255,
    70, 85, 110, 145, 255, 255, 255, 255,
    90, 110, 185, 255, 255, 255, 255, 255,
    120, 175, 255, 255, 255, 255, 255, 255,
    245, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255,
]

# default quantization matrix as defined in JPEG standard
quantization_50_values = [
    16, 11, 10, 16, 24, 40, 51, 61,
    12, 12, 14, 19, 26, 58, 60, 55,
    14, 13, 16, 24, 40, 57, 69, 56,
    14, 17, 22, 29, 51, 87, 80, 62,
    18, 22, 37, 56, 68, 109, 103, 77,
    24, 35, 55, 64, 81, 104, 113, 92,
    49, 64, 78, 87, 103, 121, 120, 101,
    72, 92, 95, 98, 112, 100, 103, 99,
]

quantization_90_values = [
    3, 2, 2, 3, 5, 8, 10, 12,
    2, 2, 3, 4, 5, 12, 12, 11,
    3, 3, 3, 5, 8, 11, 14, 11,
    3, 3, 4, 6, 10, 17, 16, 12,
    4, 4, 7, 11, 14, 22, 21, 15,
    5, 7, 11, 13, 16, 21, 23, 18,
    10, 13, 16, 17, 21, 24, 24, 20,
    14, 18, 19, 20, 22, 20, 21, 20,
]

quantization_10 = np.array(quantization_10_values).reshape(8, 8)
quantization_50 = np.array(quantization_50_values).reshape(8, 8)
quantization_90 = np.array(quantization_90_values).reshape(8, 8)

quantization_100 = np.zeros((8, 8)) + 1

quantization_tables = {
    100: quantization_100,
    90: quantization_90,
    50: quantization_50,
    10: quantization_10,
}


def get_quantization_matrix_for_quality_percent(quality_percentage):
    assert 0 <= quality_percentage <= 100
    if quality_percentage == 0:
        # for 0 quality all 255
        return np.zeros((8, 8)) + 255
    elif quality_percentage > 50:
        # clip values between 0 - 255
        return np.clip(np.rint(quantization_50 * ((100 - quality_percentage) / 50)), a_min=1, a_max=255)
    elif quality_percentage < 50:
        return np.clip(np.rint(quantization_50 * (50 / quality_percentage)), a_min=1, a_max=255)
    elif quality_percentage == 50:
        return quantization_50
    else:
        raise RuntimeError("Should not be here - impossible")


def quantize(blocks, quantization_table):
    quantized = []

    for block in blocks:
        quantized.append(np.round(np.divide(block, quantization_table), 0))

    quantized = np.array(quantized)

    return quantized


def quantize_inverse(blocks, quantization_table):
    i_quantized = []

    for block in blocks:
        i_quantized.append(np.round(np.multiply(quantization_table, block), 0))

    i_quantized = np.array(i_quantized)

    return i_quantized


def test():
    res = get_quantization_matrix_for_quality_percent(100)
    print(res)

# test()
