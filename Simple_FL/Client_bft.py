from Utils import Model, Helper, Message
# from Utils.Message import Msg
# from Utils.DataDistributer import client_datasets, total_train_size
import sys
import socket
import jpysocket
import torch

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

    def train(self):
        train_history = self.net.fit(self.dataset, Helper.epochs_per_client, Helper.learning_rate, Helper.batch_size)
        print('{}: Loss = {}, Accuracy = {}'.format(self.client_id, round(train_history[-1][0], 4), round(train_history[-1][1], 4)))
        return self.net.get_parameters()
    
def connect(client_id, hostAddress, hostPort):
    address = (hostAddress, hostPort)
    connection = socket.socket()
    connection.connect(address)
    print("Client {} sent new connection request".format(client_id))
    return connection

def main():
    client_id = int(sys.argv[1])
    print("Client {} started! ... ".format(client_id))
    traning_client = TraningClient(client_id, torch.load("F:/DCL/Semester Project 1/Codes/DCL_semester_project/Simple_FL/Data/ClientsDatasets/" + str(client_id) + ".pt"))
    connection = connect(client_id, sys.argv[2], int(sys.argv[3]))
    while True:
        msg_size = int(jpysocket.jpydecode(connection.recv(1024))) * 4
        msg = jpysocket.jpydecode(connection.recv(msg_size))
        if msg == "TRAIN":
            client_parameters = traning_client.train()
            res = str(client_parameters)
            connection.send(jpysocket.jpyencode(str(traning_client.get_dataset_size())))
            connection.send(jpysocket.jpyencode(str(len(res))))
            connection.send(jpysocket.jpyencode(res))
        if msg == "TERMINATE":
            break

    connection.close()
    print("Client {} terminated! ...".format(client_id))


if __name__ == "__main__":
    main()