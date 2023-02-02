def resort_values(block, block_size):
    new_block = []
    for diag in range(2 * block_size - 1):
        direction = diag % 2 == 0
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

        while x < block_size and y < block_size and x >= 0 and y >= 0:
            new_block.append(block[y][x])
            
            if(direction):
                x += 1
                y -=1
            else:
                x -=1
                y += 1

    return new_block


def run_length_encode(input_vals):
    encoded_list = []
    current = input_vals[0]
    current_counter = 1
    for i, val in enumerate(input_vals[1:]):
        if val == current:
            current_counter += 1
        else:
            encoded_list.append((current, current_counter))
            current = val
            current_counter = 1

    encoded_list.append((current, current_counter))

    return encoded_list
        

def flatten(encoded):
    res = []
    for val in encoded:
        res.append(val[0])
        res.append(val[1])
    return res


def resort_and_run_length_encode(color_component, block_size):
    encoded_blocks = []
    for block in color_component:
        resorted = resort_values(block, block_size)
        run_length_encoded = run_length_encode(resorted)
        flattened = flatten(run_length_encoded)
        encoded_blocks += flattened
    return encoded_blocks
