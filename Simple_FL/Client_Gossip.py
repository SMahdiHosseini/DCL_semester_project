from Utils import Model, Helper, Message, aggregator, connectionHelper, evaluator
from Utils.Message import Msg
from Utils.ConnectionDistributer import adjMat, ports
from multiprocessing.connection import Client, Listener
import sys
import torch

## Define Client Class
class TraningClient:
    def __init__(self, client_id, dataset, neighbors):
        self.client_id = client_id
        self.dataset = dataset
        self.net = Helper.to_device(Model.FederatedNet(), Helper.device)
        self.neighbors = neighbors
        self.neighbors.sort()
        self.connections = dict()
        self.listeners = []
        if client_id == 0:
            self.text_file = open("/localhome/shossein/DCL_semester_project/Gossip_res/Output.txt", "w")

    def get_dataset_size(self):
        return len(self.dataset)

    def connectToNeighbors(self, ports):
        for neighborId in self.neighbors:
            address = (Helper.localHost, ports[neighborId])
            if neighborId < self.client_id:
                self.connections[neighborId] = Client(address)
            else:
                listener = Listener(address)
                self.connections[neighborId] = listener.accept()
                self.listeners.append(listener)

            print("Client {} connected to client {} !".format(self.client_id, neighborId))

    def terminate(self):
        for neighborId in self.neighbors:
            if self.client_id < neighborId :
                self.connections[neighborId].send(Msg(header=Message.TERMINATE))
            
            msg = self.connections[neighborId].recv()
            if msg.header == Message.ACK:
                self.connections[neighborId].close()
            if msg.header == Message.TERMINATE:
                self.connections[neighborId].send(Msg(header=Message.ACK))

        for listener in self.listeners:
            listener.close()
    
    def shareToNeighbors(self, r):
        client_parameters = self.net.get_parameters()
        for conn in self.connections.values():
            connectionHelper.sendNewParameters(conn, client_parameters, connectionHelper.PYTHON, info={Message.ROUND: r, Message.SIZE: self.get_dataset_size(), Message.SRC: self.client_id})

    def getAllParams(self, r):
        client_parameters = self.net.get_parameters()
        recvd_params = dict()
        recvd_size = dict()
        recvd_params[self.client_id] = client_parameters.cpu()
        recvd_size[self.client_id] = self.get_dataset_size()
        while len(list(recvd_size.values())) < len(self.neighbors) + 1:
            new_params, new_sizes = connectionHelper.getNewParameters(self.connections.values(), connectionHelper.PYTHON, info={Message.ROUND: r, Message.SIZE: self.get_dataset_size(), Message.PARAMS: client_parameters, Message.SRC: self.client_id})
            recvd_params.update(new_params)
            recvd_size.update(new_sizes)
        return recvd_params, recvd_size

    def runTheRound(self, r):
        self.net.fit(self.dataset)
        self.shareToNeighbors(r)            
        recvd_params, recvd_size = self.getAllParams(r)
        new_model_parameters = aggregator.averageAgg(list(recvd_params.values()), list(recvd_size.values()))
        self.net.apply_parameters(new_model_parameters)

    def execute(self):
        for r in range(1, Helper.rounds + 1):
            self.runTheRound(r)
            if self.client_id == 0:
                evaluator.evaluateTheRound(self.net.get_parameters(), r, self.text_file)

def main():
    client_id = int(sys.argv[1])
    print("Client {} started! ... ".format(client_id))
    traning_client = TraningClient(client_id, torch.load("./Data/ClientsDatasets/" + str(client_id) + ".pt"), adjMat[client_id])
    traning_client.connectToNeighbors(ports[client_id])
    print("client connected to neighbors!")
    traning_client.execute()
    traning_client.terminate()
    print("Client {} terminated! ...".format(client_id))

if __name__ == "__main__":
    main()