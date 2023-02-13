import time

import numpy as np

resort_indices_inverse = {}
resort_indices = {}


def get_zig_zag_indices(block_size):
    range_block = np.reshape(range(block_size ** 2), newshape=(block_size, block_size))
    new_block = []
    for diag in range(2 * block_size - 1):
        direction = diag % 2 == 0
#        direction = True
        if diag < block_size:
            if direction:
                x = 0
                y = diag
            else:
                x = diag
                y = 0
        else:
            if direction:
                x = diag - block_size + 1
                y = block_size - 1
            else:
                x = block_size - 1
                y = diag - block_size + 1

        while block_size > x >= 0 and block_size > y >= 0:
            new_block.append(range_block[y][x])
            if direction:
                x += 1
                y -= 1
            else:
                x -= 1
                y += 1
    return new_block


def resort_values_zig_zag(block, block_size):
    global resort_indices
    if block_size not in resort_indices:
        resort_indices[block_size] = get_zig_zag_indices(block_size)

    indices = resort_indices[block_size]
    new_block = []

    block = np.reshape(block, (1, block_size ** 2))[0]
    # for index in indices:
    #     new_block.append(block[index])
    # return new_block
    return [block[index] for index in indices ]


def resort_values_zig_zag_reverse(block, block_size):
    global resort_indices_inverse
    # to reverse the process of zigzag iteration, give incremental list to zigzag iteration
    # then find indices of incremental values
    # then use indices to reverse reordering

    # store in variable so that it is not calculated again for every block
    if block_size not in resort_indices:
        resort_indices[block_size] = get_zig_zag_indices(block_size)
    if block_size not in resort_indices_inverse:
        resort_indices_inverse[block_size] = [resort_indices[block_size].index(i) for i in range(block_size ** 2)]

    indices = resort_indices_inverse[block_size]

    # new_block = []
    #
    # for index in indices:
    #     new_block.append(block[index])
    new_block = [block[index] for index in indices]
    return np.reshape(new_block, (block_size, block_size))


def run_length_encode(input_vals):
    encoded_list = []
    current = input_vals[0]
    current_counter = 1
    for val in input_vals[1:]:
        if val == current:
            current_counter += 1
        else:
            encoded_list.append((current, current_counter))
            current = val
            current_counter = 1

    encoded_list.append((current, current_counter))

    return encoded_list


def run_length_decode(encoded):
    decoded = []
    for val, count in encoded:
        decoded += [val] * int(count)
    return decoded


def flatten(encoded):
    res = []
    for val in encoded:
        res.append(val[0])
        res.append(val[1])
    return res


def un_flatten(flattened):
    assert len(flattened) % 2 == 0
    res = []
    for i in range(len(flattened) // 2):
        res.append((flattened[i * 2], flattened[i * 2 + 1]))
    return res


def resort_and_run_length_encode(color_component, block_size):
    resorted_blocks_flattened = []
    for block in color_component:
        resorted = resort_values_zig_zag(block, block_size)
        resorted_blocks_flattened += resorted
    encoded_blocks = run_length_encode(resorted_blocks_flattened)
    encoded_blocks_flattened = flatten(encoded_blocks)
    return encoded_blocks_flattened


def unsort_and_run_length_decode(color_component, block_size):
    un_flattened = un_flatten(color_component)
    rld = run_length_decode(un_flattened)
    block_element_count = block_size ** 2
    assert len(rld) % block_element_count == 0

    blocks = []
    for i in range(len(rld[::block_element_count])):
        block_zig_zag = rld[i * block_element_count: (i + 1) * block_element_count]
        block = resort_values_zig_zag_reverse(block_zig_zag, block_size)
        blocks.append(block)

    return np.array(blocks)


def test():
    quantized1 = [
        [
            [6., 1., -1., 0., -0., 0., -0., -0.],
            [0., -0., 0., 0., -0., -0., -0., 0.],
            [0., -0., 0., -0., 0., -0., 0., -0.],
            [0., -0., 0., -0., -0., 0., 0., -0.],
            [-0., 0., -0., -0., 0., -0., -0., 0.],
            [-0., 0., 0., 0., -0., 0., 0., -0.],
            [-0., 0., -0., 0., 0., -0., -0., 0.],
            [-0., 0., -0., 0., -0., 0., 0., -0.],
        ],
        [
            [5., -0., -0., -0., 0., -0., -0., -0.],
            [1., 0., -0., -0., -0., 0., 0., 0.],
            [0., 0., 0., 0., -0., -0., -0., 0.],
            [-0., -0., 0., 0., 0., 0., -0., 0.],
            [-0., -0., 0., -0., 0., 0., 0., -0.],
            [0., -0., -0., -0., 0., -0., 0., 0.],
            [0., -0., 0., 0., -0., -0., 0., 0.],
            [-0., -0., 0., -0., -0., 0., -0., -0.],
        ],
        [
            [4., 0., 1., -1., -0., -0., 0., -0.],
            [0., 1., -0., 0., 0., 0., 0., 0.],
            [0., 0., -0., 0., 0., 0., -0., 0.],
            [-0., 0., -0., 0., 0., 0., -0., -0.],
            [-0., 0., -0., 0., -0., 0., -0., -0.],
            [0., 0., -0., 0., 0., 0., 0., 0.],
            [0., 0., -0., 0., 0., 0., -0., -0.],
            [-0., 0., -0., 0., 0., 0., -0., -0.],
        ],
        [
            [5., 1., 1., 0., -0., -0., -0., -0.],
            [-0., 0., -0., -0., -0., 0., -0., -0.],
            [0., -0., 0., -0., -0., -0., 0., 0.],
            [-0., -0., 0., -0., 0., -0., 0., -0.],
            [-0., 0., -0., 0., 0., 0., -0., -0.],
            [0., 0., 0., 0., -0., 0., -0., -0.],
            [0., 0., -0., -0., 0., -0., 0., 0.],
            [0., -0., -0., 0., -0., 0., -0., 0.]
        ]
    ]

    quantized2 = [
        [[-1., -0., 0., -0., -0., 0., 0., 0.],
         [-0., 0., -0., -0., 0., -0., -0., 0.],
         [0., -0., 0., -0., -0., 0., -0., -0.],
         [-0., 0., 0., -0., 0., -0., 0., -0.],
         [0., 0., -0., 0., 0., -0., -0., 0.],
         [0., -0., 0., -0., 0., 0., 0., -0.],
         [-0., 0., -0., 0., -0., 0., 0., -0.],
         [0., -0., -0., -0., -0., -0., -0., 0.], ],

        [[-1., -0., 0., 0., -0., 0., 0., 0.],
         [-0., -0., 0., -0., -0., 0., -0., 0.],
         [-0., 0., -0., -0., 0., -0., 0., 0.],
         [-0., 0., -0., 0., -0., -0., 0., -0.],
         [-0., -0., -0., 0., -0., 0., -0., 0.],
         [0., 0., 0., 0., -0., 0., 0., -0.],
         [-0., -0., -0., -0., -0., 0., -0., -0.],
         [0., 0., 0., 0., -0., 0., -0., 0.], ],

        [[-0., -0., -1., 0., 0., 0., 0., 0.],
         [-0., -0., 0., 0., -0., -0., -0., -0.],
         [-0., 0., -0., 0., -0., -0., 0., -0.],
         [0., -0., 0., 0., -0., -0., 0., 0.],
         [-0., -0., 0., -0., -0., -0., 0., 0.],
         [-0., -0., 0., 0., -0., 0., -0., 0.],
         [-0., -0., -0., 0., -0., 0., -0., 0.],
         [0., -0., 0., 0., -0., -0., 0., -0.], ],

        [[-1., 0., -1., -0., 0., 0., 0., -0.],
         [0., 0., -0., 0., -0., 0., -0., 0.],
         [0., -0., 0., 0., 0., 0., -0., 0.],
         [0., 0., -0., 0., 0., -0., 0., -0.],
         [0., 0., 0., -0., -0., 0., 0., 0.],
         [-0., 0., 0., -0., 0., -0., 0., 0.],
         [0., -0., 0., 0., 0., 0., 0., -0.],
         [0., 0., 0., -0., 0., -0., 0., 0.], ],
    ]

    quantized3 = [
        [
            [0, 1],
            [2, 3]
        ],
        [
            [4, 5],
            [6, 7]
        ]
    ]

    # rle = resort_and_run_length_encode(quantized3, 2)
    # res = unsort_and_run_length_decode(rle, 2)
    # print(len(res), len(quantized3))
    # print(res)
    # print(quantized3)
    # print(np.array_equal(res, quantized3))

    rle = resort_and_run_length_encode(quantized2, 8)
    res = unsort_and_run_length_decode(rle, 8)
    print(np.array_equal(res, quantized2))

    # random_list = np.random.random_sample(size=64).reshape((8, 8))
    # a = resort_values_zig_zag(random_list, 8)
    # b = resort_values_zig_zag_reverse(a, 8)
    # print(b)
    # # print(list(random_list.reshape(1,64)[0]))
    # # print(list(random_list.reshape(1,64)[0]) == b)

# test()

def test2():
    block_size = 3
    zigzag = get_zig_zag_indices(block_size)
    zigzag_i = [zigzag.index(i) for i in range(block_size ** 2)]

    print(zigzag)
    print(zigzag_i)

# test2()
