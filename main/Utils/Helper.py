import torch
from torch.utils.data import DataLoader
import random

random.seed(10)

## Constraints
localHost = 'localhost'
server_port = 6000
num_clients = 10
rounds = 5
batch_size = 128
epochs_per_client = 1
learning_rate = 2e-2
nb_byz = 0

ports = [server_port + i for i in random.sample(range(0, 100), num_clients)]
## Define utilities for GPU support
def get_device():
    # return torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    return torch.device('cpu')

def to_device(data, device):
    if isinstance(data, (list, tuple)):
        return [to_device(x, device) for x in data]
    return data.to(device, non_blocking=True)

class DeviceDataLoader(DataLoader):
        def __init__(self, dl, device):
            self.dl = dl
            self.device = device

        def __iter__(self):
            for batch in self.dl:
                yield to_device(batch, self.device)

        def __len__(self):
            return len(self.dl)

device = get_device()