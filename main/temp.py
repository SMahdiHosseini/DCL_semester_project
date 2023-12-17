# import random
# from Utils import connectionHelper, Helper, aggregator, attacks, Model, evaluator
# import torch 
# # from torch.utils.data import Dataset, Subset, DataLoader
# import torchvision.transforms as transforms
# from torchvision.datasets import MNIST
# import multiprocessing as mp
# import time
# import threading
# threads= []
# def subProcess(q , i):
#     while True:
#         if q.empty():
#             continue
#         else:
#             a, b = q.get()
#             if a == 0:
#                 print("GOT HERE")
#                 return
#             print(f"Process {i}:  {a, b}")


# manager = mp.Manager()
# shared_dict = manager.dict()
# for i in range(4):
#     shared_dict[i] = manager.Queue()

# print("shared_dict")

# for i in range(4):
#     t = threading.Thread(target=subProcess, args=(shared_dict[i], i))
#     t.start()
#     threads.append(t)

# i = 1
# terminate = False
# while terminate == False:
#     for j in range(4):
#         shared_dict[j].put((i, i+1))
#     if i == 10:
#         for j in range(4):
#             shared_dict[j].put((0, 0))
#         terminate = True
#     else:
#         i += 1
#     time.sleep(1)

# for t in threads:
#     t.join()

# import matplotlib.pyplot as plt
# import numpy as np

# data = [[i-5, i, i + 5] for i in range(10)]
# print(data)
# # Calculate the mean and standard deviation of the data
# mean = [np.mean(d) for d in data]
# std = [np.std(d) for d in data]

# # Plot the data with error bars
# plt.errorbar(x=range(len(data)), y=mean, yerr=std, fmt='o')
# plt.show()

# from Utils import Model, Helper
# import torch
# import torchvision.transforms as transforms
# from torchvision.datasets import MNIST

# test_dataset = MNIST('../Data', train=False, download=True, transform=transforms.ToTensor())
# dataset = MNIST('../Data', train=True, download=True, transform=transforms.ToTensor())
# dataset = DataDistributer.idx_to_dataset(0, 10)
# dataset = torch.load("./Data/ClientsDatasets/0.pt")
# net = Helper.to_device(Model.FederatedNet(), Helper.device)
# for i in range(3):
#     net.fit(dataset)

# test_loss, test_acc = net.evaluate(test_dataset)
# print('After round {}, test_loss = {}, test_acc = {}\n'.format(3, round(test_loss, 4), round(test_acc, 4)))
# print(len(bytes(connectionHelper.tensorToString(net.get_parameters()), 'utf-8')))

from Utils import Model, Helper
import torch
dataset = torch.load("./Data/ClientsDatasets/0.pt")
net = Helper.to_device(Model.FederatedNet(), Helper.device)
for i in range(3):
    net.fit(dataset)
print(len(net.get_parameters()))
