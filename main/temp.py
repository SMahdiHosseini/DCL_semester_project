# import random
# from Utils import connectionHelper, Helper, aggregator, attacks, Model, evaluator
# import torch 
# # from torch.utils.data import Dataset, Subset, DataLoader
# import torchvision.transforms as transforms
# from torchvision.datasets import MNIST

s = dict()
s[1] = 2321
s[2] = 2322
s[3] = 2323
s[4] = 2324

d = dict()
d[(1, "s")] = 1
d[(2, "s")] = 2

r = [i for i in s.keys() if i in [k[0] for k in d.keys()]]
rr = list(s.keys() - r)
print(r)
print(rr)
