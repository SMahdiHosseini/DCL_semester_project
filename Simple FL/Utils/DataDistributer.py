import torchvision.transforms as transforms
from torchvision.datasets import MNIST
from torch.utils.data import random_split, Subset
from Utils import Helper

train_dataset = MNIST('/kaggle/working', train=True, download=True, transform=transforms.ToTensor())
test_dataset = MNIST('/kaggle/working', train=False, download=True, transform=transforms.ToTensor())

train_dataset, dev_dataset = random_split(train_dataset, [int(len(train_dataset) * 0.83), int(len(train_dataset) * 0.17)])

# for test
train_dataset = Subset(train_dataset, range(5))
test_dataset = Subset(test_dataset, range(5))
dev_dataset = Subset(dev_dataset, range(5))

total_train_size = len(train_dataset)
total_test_size = len(test_dataset)
total_dev_size = len(dev_dataset)

examples_per_client = total_train_size // Helper.num_clients
client_datasets = random_split(train_dataset, [min(i + examples_per_client, total_train_size) - i for i in range(0, total_train_size, examples_per_client)])