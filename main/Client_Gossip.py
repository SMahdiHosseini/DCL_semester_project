from Utils import Model, Helper, Message, connectionHelper, evaluator
from Utils.aggregator import RobustAggregator
from Utils.Message import Msg
from Utils.ConnectionDistributer import generateGossipPorts
from multiprocessing.connection import Client, Listener
import sys
import torch

#program input: client_id, nb_clients, server_address, server_port, nb_byz, nb_rounds, aggregator_name
client_id = int(sys.argv[1])
nb_clients = int(sys.argv[2])
server_address = sys.argv[3]
server_port = int(sys.argv[4])
nb_byz = int(sys.argv[5])
nb_rounds = int(sys.argv[6])
aggregator_name = sys.argv[7]

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
        self.aggregator = RobustAggregator(aggregator_name, '', 1, nb_byz, Helper.device)
        if client_id == 0:
            self.text_file = open("/localhome/shossein/DCL_semester_project/Gossip_res/ncl_" + str(nb_clients) + "_agg_" + aggregator_name + "_nbyz_" + str(nb_byz) + ".txt", "w")

    def get_dataset_size(self):
        return len(self.dataset)

    def connectToNeighbors(self, ports):
        for neighborId in self.neighbors:
            address = (server_address, ports[neighborId])
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

    def runTheRound(self, r):
        self.net.fit(self.dataset)
        self.shareToNeighbors(r)            
        recvd_params, recvd_size = connectionHelper.getAllParams(list(self.connections.values()), len(self.neighbors), self.net.get_parameters(), self.get_dataset_size(), self.client_id, r)
        recvd_params[self.client_id] = self.net.get_parameters().cpu()
        recvd_size[self.client_id] = self.get_dataset_size()
        new_model_parameters = self.aggregator.aggregate(list(recvd_params.values()))
        self.net.apply_parameters(new_model_parameters)

    def execute(self):
        for r in range(1, nb_rounds + 1):
            self.runTheRound(r)
            if self.client_id == 0:
                evaluator.evaluateTheRound(self.net.get_parameters(), r, self.text_file)

def main():
    print("Client {} started! ... ".format(client_id))
    ports, adjMat = generateGossipPorts(server_port, nb_clients)
    traning_client = TraningClient(client_id, torch.load("./Data/ClientsDatasets/" + str(client_id) + ".pt"), adjMat[client_id])
    traning_client.connectToNeighbors(ports[client_id])
    print("client connected to neighbors!")
    traning_client.execute()
    traning_client.terminate()
    print("Client {} terminated! ...".format(client_id))

if __name__ == "__main__":
    main()