from Utils import Model, Helper, Message
from Utils.Message import Msg
from Utils.DataDistributer import client_datasets, total_train_size
from multiprocessing.connection import Client
import sys

## Define Client Class
class TraningClient:
    def __init__(self, client_id, dataset):
        self.client_id = client_id
        self.dataset = dataset
        self.net = Helper.to_device(Model.FederatedNet(), Helper.device)

    def get_dataset_size(self):
        return len(self.dataset)

    def get_client_id(self):
        return self.client_id

    def train(self, current_parameters):
        self.net.apply_parameters(current_parameters)
        train_history = self.net.fit(self.dataset, Helper.epochs_per_client, Helper.learning_rate, Helper.batch_size)
        print('{}: Loss = {}, Accuracy = {}'.format(self.client_id, round(train_history[-1][0], 4), round(train_history[-1][1], 4)))
        return self.net.get_parameters()

def connectToServer(client_id):
    address = (Helper.localHost, Helper.server_port)
    connection = Client(address)
    connection.send(Msg(client_id, header=Message.NEW_CONNECTION))
    print("Client {} sent new connection request".format(client_id))
    return connection

def main():
    client_id = int(sys.argv[1])
    print("Client {} started! ... ".format(client_id))
    traning_client = TraningClient(client_id, client_datasets[client_id])
    connection = connectToServer(client_id)
    while True:
        msg = connection.recv()
        if msg.header == Message.TRAIN:
            client_parameters = traning_client.train(msg.content)
            connection.send(Msg(header=Message.NEW_PARAMETERS, content={Message.FRACTION: traning_client.get_dataset_size() / total_train_size, Message.PARAMS: client_parameters}))
        if msg.header == Message.TERMINATE:
            break

    connection.close()
    print("Client {} terminated! ...".format(client_id))


if __name__ == "__main__":
    main()