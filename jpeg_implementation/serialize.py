
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




def store_as_image():
    pass




def test():
    bits = "11111111"
    byte_string, prepended_bits = bitstring_to_bytes(bits)
    print(len(bits), byte_string)
    print(prepended_bits, 8 - (len(bits) % 8), (8 - (len(bits) % 8))%8)

test()