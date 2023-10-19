from Utils import Model, Helper, Message
from Utils.Message import Msg
from Utils.ConnectionDistributer import adjMat, ports
from multiprocessing.connection import Client, Listener
import sys
import torch
import select

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

    def get_dataset_size(self):
        return len(self.dataset)

    def get_client_id(self):
        return self.client_id

    def train(self):
        # self.net.apply_parameters(current_parameters)
        train_history = self.net.fit(self.dataset, Helper.epochs_per_client, Helper.learning_rate, Helper.batch_size)
        print('{}: Loss = {}, Accuracy = {}'.format(self.client_id, round(train_history[-1][0], 4), round(train_history[-1][1], 4)))
        return self.net.get_parameters()

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
        for listener in self.listeners:
            listener.close()
    
    def shareToNeighbors(self, client_parameters, r):
        for conn in self.connections.values():
            conn.send(Msg(header=Message.NEW_PARAMETERS, content={Message.ROUND: str(r), Message.FRACTION: self.get_dataset_size(), Message.PARAMS: client_parameters}))

    def aggregateParams(self, recvd_params, recvd_size):
        cluster_size = sum(recvd_size)
        for i in range(len(recvd_params)):
            recvd_params[i] = recvd_size[i] / cluster_size * recvd_params[i]
        new_model_parameters = torch.sum(torch.stack(recvd_params), dim=0)
        self.net.apply_parameters(new_model_parameters)

    def runTheRound(self, r):
        client_parameters = self.train()
        if r < Helper.rounds:
            # print("****", r)
            self.shareToNeighbors(client_parameters, r)

            recvd_params = []
            recvd_size = []
            recvd_params.append(client_parameters.cpu())
            recvd_size.append(self.get_dataset_size())
            while len(recvd_params) < len(self.neighbors):
                ready_to_read, _, _ = select.select(self.connections.values(), [], [])
                for sock in ready_to_read:
                    msg = sock.recv()
                    if msg.header == Message.NEW_PARAMETERS:
                        if int(msg.content[Message.ROUND]) == r:
                            recvd_params.append(msg.content[Message.PARAMS].cpu())
                            recvd_size.append(msg.content[Message.FRACTION])
                        else:
                            sock.send(Msg(header=Message.WAIT))
                    if msg.header == Message.WAIT:
                        sock.send(Msg(header=Message.NEW_PARAMETERS, content={Message.ROUND: str(r), Message.FRACTION: self.get_dataset_size(), Message.PARAMS: client_parameters}))
            self.aggregateParams(recvd_params, recvd_size)

    def execute(self):
        for r in range(1, Helper.rounds + 1):
            self.runTheRound(r)

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