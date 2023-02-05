import math


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


def up_sample_u_v(u, v, j, a, b, resolution=(32, 32)):
    if j != 4 or a not in [4, 2, 1] or b not in [a, 0]:
        raise RuntimeError("Invalid value for subsampling settings")
    if int(j / a) != j / a:
        raise RuntimeError("Invalid value for subsampling settings")
    if j == 4 and a == 4 and b == 4:
        return u, v

    if b != 0:
        u_up = u.repeat(1, axis=0).repeat(j // a, axis=1)
        v_up = v.repeat(1, axis=0).repeat(j // a, axis=1)
    else:
        u_up = u.repeat(2, axis=0).repeat(j // a, axis=1)
        v_up = v.repeat(2, axis=0).repeat(j // a, axis=1)

    return u_up[:resolution[1], :resolution[0]], v_up[:resolution[1], :resolution[0]]


def calculate_down_sampled_resolution(j, a, b, resolution):
    if j != 4 or a not in [4, 2, 1] or b not in [a, 0]:
        raise RuntimeError("Invalid value for subsampling settings")
    if int(j / a) != j / a:
        raise RuntimeError("Invalid value for subsampling settings")
    if j == 4 and a == 4 and b == 4:
        return resolution

    if b != 0:
        x_res = math.ceil(resolution[0] / (j // a))
        y_res = math.ceil(resolution[1])
    else:
        x_res = math.ceil(resolution[0] / (j // a))
        y_res = math.ceil(resolution[1] / 2)
    return x_res, y_res
