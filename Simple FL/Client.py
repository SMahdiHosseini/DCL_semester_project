from Utils import Model, Helper
import sys

## Define Client Class
class Client:
    def __init__(self, client_id, dataset):
        self.client_id = client_id
        self.dataset = dataset

    def get_dataset_size(self):
        return len(self.dataset)

    def get_client_id(self):
        return self.client_id

    def train(self, parameters_dict):
        net = Helper.to_device(Model.FederatedNet(), Helper.device)
        net.apply_parameters(parameters_dict)
        train_history = net.fit(self.dataset, Helper.epochs_per_client, Helper.learning_rate, Helper.batch_size)
        print('{}: Loss = {}, Accuracy = {}'.format(self.client_id, round(train_history[-1][0], 4), round(train_history[-1][1], 4)))
        return net.get_parameters()

def main():
    client = Client(int(sys.argv[1]), Helper.client_datasets[int(sys.argv[1])])


if __name__ == "__main__":
    main()