from Utils import connectionHelper
from torch import tensor
# import zlib

# # Given string
# s = 'tensor([ 0.0118,  0.0261, -0.0229, -0.0163,  0.0201, -0.0379])'

# # Extracting the list of floats from the string
# lst = [float(x) for x in s[s.find('[')+1:s.find(']')].split(',')]

# # Creating a PyTorch tensor from the list of floats
# tensor = torch.tensor(lst)

# print(tensor)

# compressed = zlib.compress(bytes(''.join(str(round(x, 4)) + "," for x in [0.01182,  0.02261, -0.02292, -0.01623,  0.02012, -0.03792]), 'utf-8'))
# print(compressed)

# decom = [float(num) for num in zlib.decompress(compressed).decode().split(',') if num]
# print(decom)

# t = torch.tensor(decom)
# print(t)

# def encodeTag(header, r, s):
#     return '#'.join([header, str(r), str(s)])
# def decodeTag(tag):
#     return [s for s in tag.split('#')]
# f = encodeTag("EWEWEW", 2, 1450)
# print(f)
# print(decodeTag(f))

s1 = open("param_fl_r1.txt", "r")
s2 = open("param_go_r1.txt", "r")
ss1 = s1.readline()
ss2 = s2.readline()
lss1 = [num for num in ss1.split(',') if num]
lss2 = [num for num in ss2.split(',') if num]
ss1 = connectionHelper.stringToTensor(ss1).tolist()
ss2 = connectionHelper.stringToTensor(ss2).tolist()

for i in range(len(ss1)):
    if ss1[i] != ss2[i]:
        print(ss1[i], lss1[i], ss2[i], lss2[i])
        # print(ss1[i], ss2[i])

# a = tensor([1.21234567989, 2.235456354, 5.322434637895])
# s = connectionHelper.tensorToString(a)
# print(s)
# b = connectionHelper.stringToTensor(s)
# print(b)