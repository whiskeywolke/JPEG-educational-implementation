def bitstring_to_bytes(bits):
    # prepends bits in the front to even number of bytes
    prepended = 0
    if len(bits) % 8 != 0:
        prepended = 8 - (len(bits) % 8)

    return int(bits, 2).to_bytes((len(bits) + 7) // 8, byteorder='big'), prepended


# https://stackoverflow.com/questions/60579197/python-bytes-to-bit-string
def bytes_to_bitstring(bytestring, prepended_bits=0):
    return ''.join(f'{byte:08b}' for byte in bytestring)[prepended_bits:]


def dict_to_bytes(dictionary):
    dict_string = str(dictionary)
    # remove uneccessary information
    dict_string = dict_string.replace(" ", "")
    dict_string = dict_string.replace(".0:", ":")
    dict_string = dict_string.replace("'", "")
    dict_string = dict_string[1:-1]

    # substitute sequences
    dict_string = dict_string.replace("0000000000", "a")
    dict_string = dict_string.replace("1111111111", "A")
    dict_string = dict_string.replace("000000000", "b")
    dict_string = dict_string.replace("111111111", "B")
    dict_string = dict_string.replace("00000000", "c")
    dict_string = dict_string.replace("11111111", "C")
    dict_string = dict_string.replace("0000000", "d")
    dict_string = dict_string.replace("1111111", "D")
    dict_string = dict_string.replace("000000", "e")
    dict_string = dict_string.replace("111111", "E")
    dict_string = dict_string.replace("00000", "f")
    dict_string = dict_string.replace("11111", "F")
    dict_string = dict_string.replace("0000", "g")
    dict_string = dict_string.replace("1111", "G")
    dict_string = dict_string.replace("000", "h")
    dict_string = dict_string.replace("111", "H")
    dict_string = dict_string.replace("00", "i")
    dict_string = dict_string.replace("11", "I")

    dict_string = dict_string.replace("0101010101", "j")
    dict_string = dict_string.replace("1010101010", "J")
    dict_string = dict_string.replace("010101010", "k")
    dict_string = dict_string.replace("101010101", "K")
    dict_string = dict_string.replace("01010101", "l")
    dict_string = dict_string.replace("10101010", "L")
    dict_string = dict_string.replace("0101010", "m")
    dict_string = dict_string.replace("1010101", "M")
    dict_string = dict_string.replace("010101", "n")
    dict_string = dict_string.replace("101010", "N")
    dict_string = dict_string.replace("01010", "o")
    dict_string = dict_string.replace("10101", "O")
    dict_string = dict_string.replace("0101", "p")
    dict_string = dict_string.replace("1010", "P")
    dict_string = dict_string.replace("010", "q")
    dict_string = dict_string.replace("101", "Q")
    dict_string = dict_string.replace("01", "r")
    dict_string = dict_string.replace("10", "R")

    dict_string = dict_string.replace(",-", "y")
    dict_string = dict_string.replace(":0", "z")
    dict_string = dict_string.replace(":1", "Z")

    res = bytes(dict_string, 'ascii')
    return res


def bytes_to_dict(dict_bytes):
    # reconstruct removed information
    dict_bytes = bytes.decode(dict_bytes)
    dict_bytes = dict_bytes.replace(":", ":'")
    dict_bytes = dict_bytes.replace(",", "',")
    dict_bytes = dict_bytes + "'"

    # reconstruct sequences
    dict_bytes = dict_bytes.replace("a", "0000000000")
    dict_bytes = dict_bytes.replace("A", "1111111111")
    dict_bytes = dict_bytes.replace("b", "000000000")
    dict_bytes = dict_bytes.replace("B", "111111111")
    dict_bytes = dict_bytes.replace("c", "00000000")
    dict_bytes = dict_bytes.replace("C", "11111111")
    dict_bytes = dict_bytes.replace("d", "0000000")
    dict_bytes = dict_bytes.replace("D", "1111111")
    dict_bytes = dict_bytes.replace("e", "000000")
    dict_bytes = dict_bytes.replace("E", "111111")
    dict_bytes = dict_bytes.replace("f", "00000")
    dict_bytes = dict_bytes.replace("F", "11111")
    dict_bytes = dict_bytes.replace("g", "0000")
    dict_bytes = dict_bytes.replace("G", "1111")
    dict_bytes = dict_bytes.replace("h", "000")
    dict_bytes = dict_bytes.replace("H", "111")
    dict_bytes = dict_bytes.replace("i", "00")
    dict_bytes = dict_bytes.replace("I", "11")

    dict_bytes = dict_bytes.replace("j", "0101010101")
    dict_bytes = dict_bytes.replace("J", "1010101010")
    dict_bytes = dict_bytes.replace("k", "010101010")
    dict_bytes = dict_bytes.replace("K", "101010101")
    dict_bytes = dict_bytes.replace("l", "01010101")
    dict_bytes = dict_bytes.replace("L", "10101010")
    dict_bytes = dict_bytes.replace("m", "0101010")
    dict_bytes = dict_bytes.replace("M", "1010101")
    dict_bytes = dict_bytes.replace("n", "010101")
    dict_bytes = dict_bytes.replace("N", "101010")
    dict_bytes = dict_bytes.replace("o", "01010")
    dict_bytes = dict_bytes.replace("O", "10101")
    dict_bytes = dict_bytes.replace("p", "0101")
    dict_bytes = dict_bytes.replace("P", "1010")
    dict_bytes = dict_bytes.replace("q", "010")
    dict_bytes = dict_bytes.replace("Q", "101")
    dict_bytes = dict_bytes.replace("r", "01")
    dict_bytes = dict_bytes.replace("R", "10")

    dict_bytes = dict_bytes.replace("y", "',-")
    dict_bytes = dict_bytes.replace("z", ":'0")
    dict_bytes = dict_bytes.replace("Z", ":'1")

    dict_bytes = bytes(dict_bytes, "ascii")
    dict_bytes = b"".join([bytes("{", "ascii"), dict_bytes, bytes("}", "ascii")])
    return dict(eval(dict_bytes))


separator = b"\x00\x00\x00\x00"


def store_as_file(filename, table_y, table_u, table_v, enc_y, enc_u, enc_v):
    t_y_b = dict_to_bytes(table_y)
    t_u_b = dict_to_bytes(table_u)
    t_v_b = dict_to_bytes(table_v)

    d_y_b, prep_y = bitstring_to_bytes(enc_y)
    d_u_b, prep_u = bitstring_to_bytes(enc_u)
    d_v_b, prep_v = bitstring_to_bytes(enc_v)
    bytes_size = len(t_y_b) + len(t_u_b) + len(t_v_b) + len(d_y_b) + len(d_u_b) + len(d_v_b) + 3

    data = prep_y.to_bytes(1, byteorder="big") + separator + \
           prep_u.to_bytes(1, byteorder="big") + separator + \
           prep_v.to_bytes(1, byteorder="big") + separator + \
           t_y_b + separator + \
           t_u_b + separator + \
           t_v_b + separator + \
           d_y_b + separator + \
           d_u_b + separator + \
           d_v_b

    assert data.count(separator) == 8

    with open(filename, "wb") as fp:
        fp.write(data)
    return len(data)


def read_from_file(filename):
    with open(filename, "rb") as fp:
        data = fp.read()

        split_data = data.split(separator)

        assert len(split_data) == 9

        prep_y = int.from_bytes(split_data[0], byteorder="big")
        prep_u = int.from_bytes(split_data[1], byteorder="big")
        prep_v = int.from_bytes(split_data[2], byteorder="big")

        table_y = bytes_to_dict(split_data[3])
        table_u = bytes_to_dict(split_data[4])
        table_v = bytes_to_dict(split_data[5])

        enc_y = bytes_to_bitstring(split_data[6], prep_y)
        enc_u = bytes_to_bitstring(split_data[7], prep_u)
        enc_v = bytes_to_bitstring(split_data[8], prep_v)
        return table_y, table_u, table_v, enc_y, enc_u, enc_v


def test0():
    bits = "11111111"
    byte_string, prepended_bits = bitstring_to_bytes(bits)
    print(len(bits), byte_string)
    print(prepended_bits, 8 - (len(bits) % 8), (8 - (len(bits) % 8)) % 8)


def test1():
    huffman_code = {63: '111', 50: '11011111', 57: '11011110', -5.0: '1101110', 6.0: '110110', 5.0: '110101', 54: '0'}
    dict_bytes = dict_to_bytes(huffman_code)
    print(len(dict_bytes), type(dict_bytes))
    with open("huffman.code", "wb") as fp:
        fp.write(dict_bytes)

    with open("huffman.code", "rb") as fp:
        dict_bytes_file = fp.read()
        reassembled = bytes_to_dict(dict_bytes_file)

    print(reassembled == huffman_code)
    print(dict_bytes)


def test2():
    encoded = "11101010010111010110010111010110010111010100000100001001100111010100100101000100001001101101010000101110101000010111010100001011111010100000111100101010010110010111110101001000010000100111010000100110111101100010111110101001011101011000000100101101000010011011010110011001001001100111011000000010011001110110000100001001100101010000000010010110000100110110101000010111010110010111010110010111010110010111011100101110111001011101011000100001001110100001001010110010100001011111010100010001111001010100110001000000100101101000010011011011000100010000100101101000010011011011000100101110110001001011111011000101111101010000001001100101010000101110101100101110101100010000100110011101010010010100010000100110110101000010111010100001"
    # convert huffman encoded bits to bytes
    byte_string, prepended_bits = bitstring_to_bytes(encoded)

    # write bytes to file
    with open("compressed.imagedata", "wb") as fp:
        fp.write(byte_string)

    # read file
    with open("compressed.imagedata", "rb") as fp:
        read_bytes = fp.read()

    # decode bytes to bitstring
    encoded_from_file = bytes_to_bitstring(read_bytes, prepended_bits)

    # compare
    print(len(byte_string), "bytes of image data", "prepended_bits:", prepended_bits)
    print(len(encoded), len(encoded_from_file))
    print(encoded == encoded_from_file)


# test0()
# test1()
# test2()
