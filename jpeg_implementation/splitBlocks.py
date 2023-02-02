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

