import concurrent.futures
import itertools

import numpy as np


class Node:
    def __init__(self, value, occurrence, left=None, right=None):
        self.value = value
        self.occurrence = occurrence
        self.left = left
        self.right = right


# https://www.javatpoint.com/huffman-coding-using-python


def traverse_tree(node, codes, current_code=""):
    if node.left:
        traverse_tree(node.left, codes, current_code + "1")
    if node.right:
        traverse_tree(node.right, codes, current_code + "0")

    if not node.left and not node.right:
        codes[node.value] = current_code


def generate_huffman_code(values):
    occurrences = {}
    for val in values:
        if val in occurrences:
            occurrences[val] += 1
        else:
            occurrences[val] = 1

    nodes = [Node(val, occ) for val, occ in occurrences.items()]
    root_node = Node("", 0)

    while len(nodes) > 1:
        nodes = sorted(nodes, key=lambda x: x.occurrence)

        left = nodes[0]
        right = nodes[1]
        nodes.remove(left)
        nodes.remove(right)

        root_node = Node("", left.occurrence + right.occurrence, left, right)
        nodes.append(root_node)

    codes = {}
    traverse_tree(root_node, codes)

    return codes


def encode_huffman(huffman_code, message):
    # encoded = ""
    # for val in message:
    #     encoded += huffman_code[val]
    # print(len(encoded))
    # return encoded
    return "".join([huffman_code[val] for val in message])  # faster about factor 100


def decode_huffman(encoded, table):
    # reverse lookup table
    new_table = {key: value for value, key in table.items()}
    assert len(table) == len(new_table)
    decoded = []
    symbol = None
    for s in encoded:
        if symbol is None:
            symbol = s
        else:
            symbol += s
        if symbol in new_table:
            decoded.append(new_table[symbol])
            symbol = None

    # check that all symbols have been found
    # if symbol:
    #     print(encoded)
    #     print(table)
    #     print(symbol)
    #     print(decoded)
    assert symbol is None
    return decoded
