# import random
from Utils import connectionHelper, Helper, aggregator, attacks, Model, evaluator
import torch 
# from torch.utils.data import Dataset, Subset, DataLoader
import torchvision.transforms as transforms
from torchvision.datasets import MNIST

# s1 = open("param_fl_r1.txt", "r")
# s2 = open("param_go_r1.txt", "r")
# ss1 = s1.readline()
# ss2 = s2.readline()
# lss1 = [num for num in ss1.split(',') if num]
# lss2 = [num for num in ss2.split(',') if num]
# ss1 = connectionHelper.stringToTensor(ss1).tolist()
# ss2 = connectionHelper.stringToTensor(ss2).tolist()

# for i in range(len(ss1)):
#     if ss1[i] != ss2[i]:
#         print(ss1[i], lss1[i], ss2[i], lss2[i])
        # print(ss1[i], ss2[i])

# a = tensor([1.21234567989, 2.235456354, 5.322434637895])
# s = connectionHelper.tensorToString(a)
# print(s)
# b = connectionHelper.stringToTensor(s)
# print(b)

# my_dict = {('a', 2): 3, ('b', 1): 2, ('c', 3): 1, ('d', 2): 4}
# m = 2
# sorted_dict = dict(sorted(my_dict.items(), key=lambda x: x[0][1])[:m])
# print(sorted_dict)
# def replace_0_with_6(targets):
#     """
#     :param targets: Target class IDs
#     :type targets: list
#     :param target_set: Set of class IDs possible
#     :type target_set: list
#     :return: new class IDs
#     """
#     new_data = []
#     for data, label in targets:
#         if label == 0:
#             new_data.append((data, 6))
#         else:
#             new_data.append((data, label))
#     return new_data

# print(t)
# counter = 0
# for idx in range(len(t)):
#     if t[idx][1] == 0:
#         counter += 1
# print(counter)
# d = replace_0_with_6(t)
# counter = 0
# for idx in range(len(d)):
#     if d[idx][1] == 0:
#         counter += 1
# print(counter)
# print(d)

# a1 = torch.tensor([random.random() for _ in range(10)])
# # print(a1)
# a2 = torch.tensor([random.random() for _ in range(10)])
# # print(a2)
# a3 = torch.tensor([random.random() for _ in range(10)])
# # print(a3)
# a4 = torch.tensor([random.random() for _ in range(10)])
# # print(a4)

# byz_vec = attacks.ByzantineAttack("SF", 3).generate_byzantine_vectors([a1, a2, a3, a4], None)
# # print(byz_vec)
# final_vec = aggregator.RobustAggregator("average", "", 1, 1, Helper.device).aggregate([a1, a2, a3, a4, byz_vec[0], byz_vec[1], byz_vec[2]])
# print(connectionHelper.tensorToString(final_vec))


# t = [torch.mul(torch.stack([a1, a2, a3, a4]).mean(dim=0), -1) * 4/3] * 3
# f = torch.stack([a1, a2, a3, a4] + t).mean(dim=0)
# print(connectionHelper.tensorToString(f))

def readlines(input_file_name):
    input_file = open(input_file_name, "r")
    lines = dict()
    for line in input_file:
        line = line.strip()
        key_value = line.split("=")
        key = key_value[0]
        lines[key] = key_value[1]
    return lines

for i in range(2):
        print(readlines('ips.config')['client_' + str(i)])