def subsample_u_v(u, v, j, a, b):
    """
    sub-samples the u v components based on the ratio given by j a b
    j is the sampling reference width
        each block that is sub-sampled is of size j * 2
    a is the number of samples in the first row
    b is the number of samples in the second row equal to a or 0
    """
    if j != 4 or a not in [4, 2, 1] or b not in [a, 0]:
        raise RuntimeError("Invalid value for subsampling settings")
    if j == 4 and a == 4 and b == 4:
        return u, v
    if int(j / a) != j / a:
        raise RuntimeError("Invalid value for subsampling settings")

    if b == 0:
        return u[::2, ::int(j / a)], v[::2, ::int(j / a)]
    else:
        return u[::1, ::int(j / a)], v[::1, ::int(j / a)]

def upsample_u_v(u, v, j, a, b):
    pass
