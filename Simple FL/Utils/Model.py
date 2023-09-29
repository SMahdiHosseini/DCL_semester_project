import torch
from torch.utils.data import DataLoader
from Utils import Helper

## Define FederatedNet class
class FederatedNet(torch.nn.Module):
    def __init__(self):
        super().__init__()
        # self.conv1 = torch.nn.Conv2d(1, 20, 7)
        # self.conv2 = torch.nn.Conv2d(20, 40, 7)
        # self.maxpool = torch.nn.MaxPool2d(2, 2)
        self.flatten = torch.nn.Flatten()
        self.linear = torch.nn.Linear(784, 128)
        # self.non_linearity = torch.nn.functional.relu
        # self.track_layers = {'conv1': self.conv1, 'conv2': self.conv2, 'linear': self.linear}
        self.track_layers = {'linear': self.linear}

    def forward(self, x_batch):
        # out = self.conv1(x_batch)
        # out = self.non_linearity(out)
        # out = self.conv2(out)
        # out = self.non_linearity(out)
        # out = self.maxpool(out)
        # out = self.flatten(out)
        # out = self.linear(out)
        out = self.flatten(x_batch)
        out = self.linear(out)
        return out

    def get_track_layers(self):
        return self.track_layers

    def apply_parameters(self, parameters_dict):
        with torch.no_grad():
            for layer_name in parameters_dict:
                self.track_layers[layer_name].weight.data *= 0
                self.track_layers[layer_name].bias.data *= 0
                self.track_layers[layer_name].weight.data = parameters_dict[layer_name]['weight']
                self.track_layers[layer_name].bias.data = parameters_dict[layer_name]['bias']

    def get_parameters(self):
        parameters_dict = dict()
        for layer_name in self.track_layers:
            parameters_dict[layer_name] = {
                'weight': self.track_layers[layer_name].weight.data.clone(),
                'bias': self.track_layers[layer_name].bias.data.clone()
            }
        return parameters_dict

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

    def fit(self, dataset, epochs, lr, batch_size=128, opt=torch.optim.SGD):
        dataloader = Helper.DeviceDataLoader(DataLoader(dataset, batch_size, shuffle=True), Helper.device)
        optimizer = opt(self.parameters(), lr)
        history = []
        for epoch in range(epochs):
            losses = []
            accs = []
            for batch in dataloader:
                loss, acc = self._process_batch(batch)
                loss.backward()
                optimizer.step()
                optimizer.zero_grad()
                loss.detach()
                losses.append(loss)
                accs.append(acc)
            avg_loss = torch.stack(losses).mean().item()
            avg_acc = torch.stack(accs).mean().item()
            history.append((avg_loss, avg_acc))
        return history

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