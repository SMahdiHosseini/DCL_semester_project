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

# from Utils import Model, Helper, DataDistributer
# from Utils.aggregator import RobustAggregator
# from Utils.attacks import ByzantineAttack
# import torch

# random_seed = 10
# torch.manual_seed(random_seed)
# torch.cuda.manual_seed(random_seed)
# torch.backends.cudnn.deterministic = True
# torch.backends.cudnn.benchmark = False

# dataset = torch.load("./Data/testDataset.pt")
# test_dataset = torch.load("./Data/testDataset.pt")
# dataset_0 = DataDistributer.idx_to_dataset(0, 7)
# dataset_1 = DataDistributer.idx_to_dataset(1, 7)
# dataset_2 = DataDistributer.idx_to_dataset(2, 7)
# dataset_3 = DataDistributer.idx_to_dataset(3, 7)
# aggregator = RobustAggregator('nnm', 'trmean', 1, 3, Helper.device)
# attacker = ByzantineAttack('SF', 3)

# net_0 = Helper.to_device(Model.FederatedNet(dataset_0), Helper.device)
# net_1 = Helper.to_device(Model.FederatedNet(dataset_1), Helper.device)
# net_2 = Helper.to_device(Model.FederatedNet(dataset_2), Helper.device)
# net_3 = Helper.to_device(Model.FederatedNet(dataset_3), Helper.device)

# print(Helper.device)
# p = [dataset_0[i][1] for i in range(len(dataset_0))]
# print(p)
# print(dataset_1[0][1], dataset_1[1][1], dataset_1[2][1], dataset_1[3][1])
# print(dataset_2[0][1], dataset_2[1][1], dataset_2[2][1], dataset_2[3][1])
# print(dataset_3[0][1], dataset_3[1][1], dataset_3[2][1], dataset_3[3][1])
# net_0.fit()
# net_1.fit()
# net_2.fit()
# net_3.fit()
# for i in range(120):
#     params = []
#     net_0.fit()
#     net_1.fit()
#     net_2.fit()
#     net_3.fit()
#     params.append(net_0.get_parameters())
#     params.append(net_1.get_parameters())
#     params.append(net_2.get_parameters())
#     params.append(net_3.get_parameters())
#     byz_vectors = attacker.generate_byzantine_vectors(params, None)
#     for v in byz_vectors:
#         params.append(v)
#     params = aggregator.aggregate(params)
#     net_0.apply_parameters(params) 
#     net_1.apply_parameters(params)
#     net_2.apply_parameters(params)
#     net_3.apply_parameters(params)
#     test_loss, test_acc = net_0.evaluate(test_dataset)
#     print('After round {}, test_loss = {}, test_acc = {}\n'.format(i, round(test_loss, 4), round(test_acc, 4)))

# print(len(net.get_parameters()))

import matplotlib.pyplot as plt
import numpy as np

# Sample data
x = np.array([1, 2, 3, 4, 5])
y1 = np.array([3, 6, 8, 4, 7])
y2 = np.array([2, 5, 7, 3, 6])
y3 = np.array([1, 4, 6, 2, 5])

# Bar width
bar_width = 0.2

# Create a figure and axis
fig, ax = plt.subplots()

# Plotting the bars
ax.bar(x - bar_width, y1, width=bar_width, label='Bar 1')
ax.bar(x, y2, width=bar_width, label='Bar 2')
ax.bar(x + bar_width, y3, width=bar_width, label='Bar 3')

# Adding labels, title, and legend
ax.set_xlabel('X-axis')
ax.set_ylabel('Y-axis')
ax.set_title('Multiple Bars at Each X-point')
ax.legend()

# Show the plot
plt.savefig("temp.png")
plt.close()