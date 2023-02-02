import numpy as np

# https://www.math.cuhk.edu.hk/~lmlui/dct.pdf

def basis_vector(N,k) :
    n = np.arange(0, N)
    if k == 0:
        ck = np.sqrt(1/N)
    else:
        ck = np.sqrt(2/N)

    ak_n = ck*np.cos((np.pi/(2*N))*k*(2*n+1))
    return ak_n

def dct_mat(N):
    res = []
    for k in range(N):
        res.append(basis_vector(N,k))
    return np.array(res)

def block_dct2(blocks, block_size):
    transformed = []
    transformation_mat = dct_mat(block_size)

    for block in blocks:
        transformed.append(np.matmul(np.matmul(transformation_mat, block), transformation_mat.transpose()))

    transformed = np.array(transformed)

    return transformed



def test():
    # https://www.math.cuhk.edu.hk/~lmlui/dct.pdf
    blocksize = 8
    data_list = [26, -5, -5, -5, -5, -5, -5, 8,
                64, 52, 8, 26, 26, 26, 8, -18,
                126, 70, 26, 26, 52, 26, -5, -5,
                111, 52, 8, 52, 52, 38, -5, -5,
                52, 26, 8, 39, 38, 21, 8, 8,
                0, 8, -5, 8, 26, 52, 70, 26,
                -5, -23, -18, 21, 8, 8, 52, 38,
                -18, 8, -5, -5, -5, 8, 26, 8]
    matrix = np.array(data_list).reshape(8, 8)


    print(np.matrix(np.round(dct_mat(8), 4))) #dct matrix is correct

    b = block_dct2([matrix], block_size) #block transform is also correct
    print(b)