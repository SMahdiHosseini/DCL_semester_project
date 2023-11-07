from Utils import Helper, Model, Message, connectionHelper, ConnectionDistributer
from multiprocessing.connection import Client
import sys
import torch

#program input: nb_clients, client_id, server_address, server_port, nb_rounds, aggregator
nb_clients = int(sys.argv[1])
client_id = int(sys.argv[2])
server_address = sys.argv[3]
server_port = int(sys.argv[4])
nb_rounds = int(sys.argv[5])
nb_byz = int(sys.argv[6])
aggregator = sys.argv[7]

## Define Client Class
class TraningClient:
    def __init__(self, client_id, dataset):
        self.client_id = client_id
        self.dataset = dataset
        self.net = Helper.to_device(Model.FederatedNet(), Helper.device)
        self.connection = None

    def get_dataset_size(self):
        return len(self.dataset)

    def connectToServer(self, port):
        address = (server_address, port)
        self.connection = Client(address)
        print("Client {} connected to the server!".format(self.client_id))

    def runTheRound(self, r):
        self.net.fit(self.dataset)
        client_parameters = self.net.get_parameters()
            
        connectionHelper.sendNewParameters(self.connection, client_parameters, connectionHelper.PYTHON, info={Message.ROUND: r, Message.SIZE: self.get_dataset_size(), Message.SRC: self.client_id})
        recvd_params, recvd_size = connectionHelper.getAllParams([self.connection], 1, client_parameters, self.get_dataset_size(), self.client_id, r)
        self.net.apply_parameters(list(recvd_params.values())[0])

    def execute(self):
        for r in range(1, nb_rounds + 1):
            self.runTheRound(r)

    def terminate(self):
        self.connection.close()

def main():
    print("Client {} started! ... ".format(client_id))
    traning_client = TraningClient(client_id, torch.load("./Data/ClientsDatasets/" + str(client_id) + ".pt"))
    traning_client.connectToServer(ConnectionDistributer.generateFLPorts(server_port, nb_clients)[client_id])
    traning_client.execute()
    traning_client.terminate()
    print("Client {} terminated! ...".format(client_id))

if __name__ == "__main__":
    main()