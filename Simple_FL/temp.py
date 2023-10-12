import torch
import zlib

# # Given string
# s = 'tensor([ 0.0118,  0.0261, -0.0229, -0.0163,  0.0201, -0.0379])'

# # Extracting the list of floats from the string
# lst = [float(x) for x in s[s.find('[')+1:s.find(']')].split(',')]

# # Creating a PyTorch tensor from the list of floats
# tensor = torch.tensor(lst)

# print(tensor)

compressed = zlib.compress(bytes(''.join(str(round(x, 4)) + "," for x in [0.01182,  0.02261, -0.02292, -0.01623,  0.02012, -0.03792]), 'utf-8'))
print(compressed)

decom = [float(num) for num in zlib.decompress(compressed).decode().split(',') if num]
print(decom)

t = torch.tensor(decom)
print(t)

