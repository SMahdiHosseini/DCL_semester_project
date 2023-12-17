import torch
from torch.utils.data import DataLoader
from Utils import Helper
import numpy as np
import random

random_seed = 10
torch.manual_seed(random_seed)
torch.cuda.manual_seed(random_seed)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
np.random.seed(random_seed)
random.seed(random_seed)

## Define FederatedNet class
class FederatedNet(torch.nn.Module):
    def __init__(self):
        super().__init__()
        # # self.conv1 = torch.nn.Conv2d(1, 20, 7)
        # # self.conv2 = torch.nn.Conv2d(20, 40, 7)
        # # self.maxpool = torch.nn.MaxPool2d(2, 2)
        # self.flatten = torch.nn.Flatten()
        # self.linear = torch.nn.Linear(784, 10)
        # # self.non_linearity = torch.nn.functional.relu
        # # self.track_layers = {'conv1': self.conv1, 'conv2': self.conv2, 'linear': self.linear}
        # self.track_layers = {'linear': self.linear}
        super().__init__()
        self.conv1 = torch.nn.Conv2d(3, 6, 5)
        self.pool = torch.nn.MaxPool2d(2, 2)
        self.conv2 = torch.nn.Conv2d(6, 16, 5)
        self.fc1 = torch.nn.Linear(16 * 5 * 5, 120)
        self.fc2 = torch.nn.Linear(120, 84)
        self.fc3 = torch.nn.Linear(84, 10)

    def forward(self, x_batch):
        # # out = self.conv1(x_batch)
        # # out = self.non_linearity(out)
        # # out = self.conv2(out)
        # # out = self.non_linearity(out)
        # # out = self.maxpool(out)
        # # out = self.flatten(out)
        # # out = self.linear(out)
        # out = self.flatten(x_batch)
        # out = self.linear(out)
        # return out
        x = self.pool(torch.nn.functional.relu(self.conv1(x_batch)))
        x = self.pool(torch.nn.functional.relu(self.conv2(x)))
        x = torch.flatten(x, 1) # flatten all dimensions except batch
        x = torch.nn.functional.relu(self.fc1(x))
        x = torch.nn.functional.relu(self.fc2(x))
        x = self.fc3(x)
        return x

    def flattenTensors(self, list_of_tensor):
        return torch.cat(tuple(tensor.detach().view(-1) for tensor in list_of_tensor))

    def unflatten(self, flat_tensor, list_of_tensor):
        c = 0
        returned_list = [torch.zeros(tensor.shape) for tensor in list_of_tensor]
        for i, tensor in enumerate(list_of_tensor):
            count = torch.numel(tensor.data)
            returned_list[i].data = flat_tensor[c:c + count].view(returned_list[i].data.shape)
            c = c + count
        return returned_list

    def get_track_layers(self):
        return self.track_layers

    def apply_parameters(self, new_parameters):
        list_of_tensor = self.unflatten(new_parameters, [tensor for tensor in self.parameters()])
        for j, param in enumerate(self.parameters()):
            param.data = list_of_tensor[j].data.to(Helper.device)


    def get_parameters(self):
        return self.flattenTensors(self.parameters())

    def batch_accuracy(self, outputs, labels):
        with torch.no_grad():
            _, predictions = torch.max(outputs, dim=1)
            return torch.tensor(torch.sum(predictions == labels).item() / len(predictions))

    def _process_batch(self, batch):
        images, labels = batch
        outputs = self(images)
        loss = torch.nn.functional.cross_entropy(outputs, labels)
        accuracy = self.batch_accuracy(outputs, labels)
        return (loss, accuracy)

    def fit(self, dataset):
        # epochs = Helper.epochs_per_client
        # lr = Helper.learning_rate
        # batch_size = Helper.batch_size
        # opt = torch.optim.SGD
        # dataloader = Helper.DeviceDataLoader(DataLoader(dataset, batch_size, shuffle=True), Helper.device)
        # optimizer = opt(self.parameters(), lr)
        # history = []
        # for epoch in range(epochs):
        #     losses = []
        #     accs = []
        #     for batch in dataloader:
        #         loss, acc = self._process_batch(batch)
        #         loss.backward()
        #         optimizer.step()
        #         optimizer.zero_grad()
        #         loss.detach()
        #         losses.append(loss)
        #         accs.append(acc)
        #     avg_loss = torch.stack(losses).mean().item()
        #     avg_acc = torch.stack(accs).mean().item()
        #     history.append((avg_loss, avg_acc))
        # print('Loss = {}, Accuracy = {}'.format(round(history[-1][0], 4), round(history[-1][1], 4)))
        # return history
        
        epochs = Helper.epochs_per_client
        batch_size = 4
        dataloader = Helper.DeviceDataLoader(DataLoader(dataset, batch_size, shuffle=True, num_workers=2), Helper.device)
        history = []
        criterion = torch.nn.CrossEntropyLoss()
        optimizer = torch.optim.SGD(self.parameters(), lr=0.001, momentum=0.9)
        for epoch in range(epochs):  
            losses = []
            accs = []
            for i, data in enumerate(dataloader, 0):
                # get the inputs; data is a list of [inputs, labels]
                inputs, labels = data

                # zero the parameter gradients
                optimizer.zero_grad()

                # forward + backward + optimize
                outputs = self(inputs)
                loss = criterion(outputs, labels)
                accuracy = self.batch_accuracy(outputs, labels)
                losses.append(loss)
                accs.append(accuracy)
                loss.backward()
                optimizer.step()
            history.append((torch.stack(losses).mean().item(), torch.stack(accs).mean().item()))
        print('Loss = {}, Accuracy = {}'.format(round(history[-1][0], 4), round(history[-1][1], 4)))

    def evaluate(self, dataset, batch_size=128):
        dataloader = Helper.DeviceDataLoader(DataLoader(dataset, batch_size), Helper.device)
        losses = []
        accs = []
        with torch.no_grad():
            for batch in dataloader:
                loss, acc = self._process_batch(batch)
                losses.append(loss)
                accs.append(acc)
        avg_loss = torch.stack(losses).mean().item()
        avg_acc = torch.stack(accs).mean().item()
        return (avg_loss, avg_acc)