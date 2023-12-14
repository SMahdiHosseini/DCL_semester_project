import sys, random
import torchvision.transforms as transforms
from torchvision.datasets import MNIST
from torch.utils.data import random_split, Subset
from torch.utils.data import DataLoader
import numpy as np
import torch

random_seed = 10
torch.manual_seed(random_seed)
torch.cuda.manual_seed(random_seed)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
np.random.seed(random_seed)
random.seed(random_seed)

# nb_clients = int(sys.argv[1])
# train_dataset = MNIST('../Data', train=True, download=True, transform=transforms.ToTensor())
# test_dataset = MNIST('../Data', train=False, download=True, transform=transforms.ToTensor())

def extreme_niid_idx(targets, idx, nb_honest):
    sorted_idx = np.array(sorted(zip(targets[idx],idx)))[:,1]
    split_idx = np.array_split(sorted_idx, nb_honest)
    for i in range(len(split_idx)):
        split_idx[i] = split_idx[i].tolist()
    return split_idx

def idx_to_dataloaders(dataset, split_idx, batch_size):
    data_loaders = []
    for i in range(len(split_idx)):
        subset = torch.utils.data.Subset(dataset, split_idx[i])
        data_loader = DataLoader(subset, batch_size=batch_size, shuffle=True)
        data_loaders.append(data_loader)
    return data_loaders

def idx_to_dataset(id, nb_clients):
    dataset = MNIST('./Data', train=True, download=False, transform=transforms.ToTensor())
    split_idx = extreme_niid_idx(dataset.targets, range(len(dataset.targets)), nb_clients)
    return Subset(dataset, split_idx[id])

def idx_to_dataset_bft(id, nb_clients):
    dataset = MNIST('../../../../main/Data', train=True, download=False, transform=transforms.ToTensor())
    split_idx = extreme_niid_idx(dataset.targets, range(len(dataset.targets)), nb_clients)
    return Subset(dataset, split_idx[id])

# dss = idx_to_dataloaders(train_dataset, extreme_niid_idx(train_dataset.targets, range(len(train_dataset.targets)), nb_clients), 64)
# for i in range(nb_clients):
#     torch.save(dss[i], "../Data/ClientsDatasets/" + str(i) + ".pt")
# print(extreme_niid_idx(train_dataset.targets, range(len(train_dataset.targets)), nb_clients)[0])

# train_dataset, dev_dataset = random_split(train_dataset, [int(len(train_dataset) * 0.83), int(len(train_dataset) * 0.17)])

# # for test
# # train_dataset = Subset(train_dataset, range(100))
# # test_dataset = Subset(test_dataset, range(100))
# # dev_dataset = Subset(dev_dataset, range(100))

# total_train_size = len(train_dataset)
# total_test_size = len(test_dataset)
# total_dev_size = len(dev_dataset)

# examples_per_client = total_train_size // nb_clients
# client_datasets = random_split(train_dataset, [min(i + examples_per_client, total_train_size) - i for i in range(0, total_train_size, examples_per_client)])

# torch.save(train_dataset, "../Data/trainDataset.pt")
# torch.save(test_dataset, "../Data/testDataset.pt")
# torch.save(dev_dataset, "../Data/devDataset.pt")

# for i in range(nb_clients):
#     torch.save(client_datasets[i], "../Data/ClientsDatasets/" + str(i) + ".pt")