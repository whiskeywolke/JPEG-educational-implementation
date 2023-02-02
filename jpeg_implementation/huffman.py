class Node:
    def __init__(self, value, occurence, left = None, right = None):  
        self.value = value
        self.occurence = occurence
        self.left = left
        self.right = right

# https://www.javatpoint.com/huffman-coding-using-python




def traverse_tree(node, codes, current_code = ""):
    if(node.left):  
        traverse_tree(node.left, codes, current_code + "1")  
    if(node.right):  
        traverse_tree(node.right, codes, current_code + "0")  
  
    if(not node.left and not node.right):
        codes[node.value] = current_code
             

def generate_huffman_code(values):
    occurences = {}
    for val in values:
        if val in occurences:
            occurences[val] += 1
        else:
            occurences[val] = 1
    
#    print(len(occurences), occurences)

    nodes = [Node(val, occ) for val, occ in occurences.items()]

    while len(nodes) > 1:
        nodes = sorted(nodes, key = lambda x: x.occurence)  
        
        left = nodes[0]
        right = nodes[1]
        nodes.remove(left)
        nodes.remove(right)

        root_node = Node("", left.occurence + right.occurence, left, right)
        nodes.append(root_node)
    

    codes = {}
    traverse_tree(root_node, codes)

    return codes

def encode_huffman(huffman_code, message):
    encoded = ""
    for val in message:
        encoded += huffman_code[val]
    return encoded
