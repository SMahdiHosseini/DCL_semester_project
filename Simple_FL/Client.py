from Utils import Helper, Model, Message, evaluator, connectionHelper
from Utils.Message import Msg
from multiprocessing.connection import Client
import sys
import torch

## Define Client Class
class TraningClient:
    def __init__(self, client_id, dataset):
        self.client_id = client_id
        self.dataset = dataset
        self.net = Helper.to_device(Model.FederatedNet(), Helper.device)
        self.connection = None
        if client_id == 0:
            self.text_file = open("/localhome/shossein/DCL_semester_project/FL_res/Output.txt", "w")

    def get_dataset_size(self):
        return len(self.dataset)

    def connectToServer(self, port):
        address = (Helper.localHost, port)
        self.connection = Client(address)
        print("Client {} connected to the server!".format(self.client_id))

    def runTheRound(self, r):
        self.net.fit(self.dataset)
        client_parameters = self.net.get_parameters()
            
        connectionHelper.sendNewParameters(self.connection, client_parameters, connectionHelper.PYTHON, info={Message.ROUND: r, Message.SIZE: self.get_dataset_size(), Message.SRC: self.client_id})
        recvd_params, recvd_size = connectionHelper.getAllParams([self.connection], 1, client_parameters, self.get_dataset_size(), self.client_id, r)
        self.net.apply_parameters(list(recvd_params.values())[0])

    def execute(self):
        for r in range(1, Helper.rounds + 1):
            self.runTheRound(r)
            if self.client_id == 0:
                evaluator.evaluateTheRound(self.net.get_parameters(), r, self.text_file)

    def terminate(self):
        self.connection.close()

def main():
    client_id = int(sys.argv[1])
    print("Client {} started! ... ".format(client_id))
    traning_client = TraningClient(client_id, torch.load("./Data/ClientsDatasets/" + str(client_id) + ".pt"))
    traning_client.connectToServer(Helper.ports[client_id])
    traning_client.execute()
    traning_client.terminate()
    print("Client {} terminated! ...".format(client_id))

if __name__ == "__main__":
    main()