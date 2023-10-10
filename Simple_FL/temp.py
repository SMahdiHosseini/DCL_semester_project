import torch

# Given string
s = 'tensor([ 0.0118,  0.0261, -0.0229, -0.0163,  0.0201, -0.0379])'

# Extracting the list of floats from the string
lst = [float(x) for x in s[s.find('[')+1:s.find(']')].split(',')]

# Creating a PyTorch tensor from the list of floats
tensor = torch.tensor(lst)

print(tensor)