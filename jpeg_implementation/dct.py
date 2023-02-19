# Michael Mente 01634435, Lukas Pezzei 11834075, Julian Saria 01608505
import numpy as np


# https://www.math.cuhk.edu.hk/~lmlui/dct.pdf

def basis_vector(N, k):
    n = np.arange(0, N)
    if k == 0:
        ck = np.sqrt(1 / N)
    else:
        ck = np.sqrt(2 / N)

    ak_n = ck * np.cos((np.pi / (2 * N)) * k * (2 * n + 1))
    return ak_n


def dct_mat(N):
    res = []
    for k in range(N):
        res.append(basis_vector(N, k))
    return np.array(res)


def block_dct2(blocks, block_size):
    transformed = []
    transformation_mat = dct_mat(block_size)

    for block in blocks:
        transformed.append(np.matmul(np.matmul(transformation_mat, block), transformation_mat.transpose()))

    transformed = np.array(transformed)

    return transformed


def block_idct2(blocks, block_size):
    transformed = []
    transformation_mat = dct_mat(block_size)

    for block in blocks:
        transformed.append(np.matmul(np.matmul(transformation_mat.transpose(), block), transformation_mat))

    transformed = np.array(transformed)

    return transformed


def test_dct():
    # https://www.math.cuhk.edu.hk/~lmlui/dct.pdf
    data_list = [
        26, -5, -5, -5, -5, -5, -5, 8,
        64, 52, 8, 26, 26, 26, 8, -18,
        126, 70, 26, 26, 52, 26, -5, -5,
        111, 52, 8, 52, 52, 38, -5, -5,
        52, 26, 8, 39, 38, 21, 8, 8,
        0, 8, -5, 8, 26, 52, 70, 26,
        -5, -23, -18, 21, 8, 8, 52, 38,
        -18, 8, -5, -5, -5, 8, 26, 8
    ]
    matrix = np.array(data_list).reshape(8, 8)

    print(np.matrix(np.round(dct_mat(8), 4)))  # dct matrix is correct

    block_size = 8
    b = np.array([matrix])
    b_trans = block_dct2(b, block_size)  # block transform is also correct
    # print(b.shape)
    # print(np.matrix(np.round(b, 2)))
    ib = block_idct2(b_trans, block_size)

    print(np.array_equal(np.round(b-ib, 10), np.zeros(b.shape)))  # check idct result by 10 decimal points -> correct


# test_dct()

