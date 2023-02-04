import numpy as np


def resize_to_blocksize(color_component_in, block_size):
    remainder_y = block_size - color_component_in.shape[0] % block_size
    remainder_x = block_size - color_component_in.shape[1] % block_size

    if remainder_x == block_size:
        remainder_x = 0
    if remainder_y == block_size:
        remainder_y = 0

    color_component = []

    for line in color_component_in:
        extended_line = line.copy()
        extended_line.resize(len(line) + remainder_x)
        color_component.append(extended_line)
    color_component = np.array(color_component)

    color_component.resize(len(color_component) + remainder_y, len(color_component[0]))

    return color_component


def split(color_component_in, block_size=8):
    color_component = resize_to_blocksize(color_component_in, block_size)
    blocks = []
    for block_y in range(color_component.shape[0] // block_size):
        for block_x in range(color_component.shape[1] // block_size):
            block_start_y = block_y * block_size
            block_end_y = block_y * block_size + block_size

            block_start_x = block_x * block_size
            block_end_x = block_x * block_size + block_size

            block = np.array([row[block_start_x:block_end_x] for row in color_component[block_start_y:block_end_y]])
            blocks.append(block)
    #    blocks = np.array(blocks)
    return blocks


def merge_blocks(color_component, resolution=(32, 32), block_size=8):
    color_component = np.array(color_component)

    row_count = resolution[1] // block_size
    if resolution[1] % block_size != 0:
        row_count += 1

    row_blocks = np.split(color_component, row_count)

    rows = []
    for row in row_blocks:
        rows.append(np.hstack(row))

    rows = np.vstack(rows)

    return rows[:resolution[1], :resolution[0]]


def test():
    blocks = [
        [
            [0, 1],
            [2, 3]
        ],
        [
            [4, 5],
            [6, 7]
        ],
        [
            [8, 9],
            [10, 11]
        ],
        [
            [12, 13],
            [14, 15]
        ]
    ]
    blocks = np.array(blocks)
    merge_blocks(blocks, (4, 4), 2)

    # img_size = 4
    # d = np.array(range(img_size ** 2)).reshape((img_size, img_size))
    # sd = split(d, 2)
    # print(len(sd))
    # d2 = merge_blocks(sd, (img_size, img_size), 2)
    # print(d2)
    # print(np.array_equal(d, d2))
    #
    # img_size = 512
    # d = np.array(range(img_size ** 2)).reshape((img_size, img_size))
    # sd = split(d)
    # d2 = merge_blocks(sd, (img_size, img_size))
    # print(np.array_equal(d, d2))

    img_size = 5
    d = np.array(range(img_size ** 2)).reshape((img_size, img_size))
    sd = split(d, 2)
    d2 = merge_blocks(sd, (img_size, img_size), 2)
    print(np.array_equal(d, d2))

    img_size_x = 713
    img_size_y = 999
    d = np.array(range(img_size_x*img_size_y)).reshape((img_size_y, img_size_x))
    sd = split(d, 2)
    d2 = merge_blocks(sd, (img_size_x, img_size_y), 2)
    print(np.array_equal(d, d2))



test()
