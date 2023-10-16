from Utils import Model, Helper, bft_Helper
import sys
import socket
import jpysocket
from torch import load, tensor

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

    def set_params(self, parameters):
        self.net.apply_parameters(parameters)

    def train(self):
        train_history = self.net.fit(self.dataset, Helper.epochs_per_client, Helper.learning_rate, Helper.batch_size)
        print('{}: Loss = {}, Accuracy = {}'.format(self.client_id, round(train_history[-1][0], 4), round(train_history[-1][1], 4)))
        return self.net.get_parameters()
    
def handleTrainCmd(connection, training_client):
    client_parameters = bytes(''.join([str(round(x, 4)) + "," for x in training_client.train().tolist()]), 'utf-8')
    connection.send(jpysocket.jpyencode(str(training_client.get_dataset_size())))
    bft_Helper.sendNewParameters(connection, client_parameters)

def execute(connection, training_client):
    while True:
        msg = jpysocket.jpydecode(connection.recv(1024))
        if msg == "NEWPARAMS":
            training_client.set_params(tensor(bft_Helper.getNewParameters(connection)))
            print("Round Ended!")
            continue
        if msg == "TRAIN":
            handleTrainCmd(connection, training_client)
        if msg == "TERMINATE":
            connection.send(jpysocket.jpyencode("ACK"))
            return
        
def main():
    client_id = int(sys.argv[1])
    print("Client {} started! ... ".format(client_id))
    training_client = TraningClient(client_id, load("F:/DCL/Semester Project 1/Codes/DCL_semester_project/Simple_FL/Data/ClientsDatasets/" + str(client_id) + ".pt"))
    # training_client = TraningClient(client_id, load("/localhome/shossein/DCL_semester_project/Simple_FL/Data/ClientsDatasets/" + str(client_id) + ".pt"))
    connection = bft_Helper.connect(sys.argv[2], int(sys.argv[3]))
    execute(connection, training_client)
    connection.close()
    print("Client {} terminated! ...".format(client_id))


if __name__ == "__main__":
    main()