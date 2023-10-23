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
        if client_id == 0:
            self.train_dataset = torch.load("/localhome/shossein/DCL_semester_project/Simple_FL/Data/trainDataset.pt")
            self.test_dataset = torch.load("/localhome/shossein/DCL_semester_project/Simple_FL/Data/testDataset.pt")
            self.dev_dataset = torch.load("/localhome/shossein/DCL_semester_project/Simple_FL/Data/devDataset.pt")
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
    
    def shareToNeighbors(self, client_parameters, r):
        for conn in self.connections.values():
            conn.send(Msg(header=Message.NEW_PARAMETERS, content={Message.ROUND: str(r), Message.FRACTION: self.get_dataset_size(), Message.PARAMS: client_parameters}))

    def aggregateParams(self, recvd_params, recvd_size, r):
        cluster_size = sum(recvd_size)
        for i in range(len(recvd_params)):
            recvd_params[i] = recvd_size[i] / cluster_size * recvd_params[i]
        new_model_parameters = torch.sum(torch.stack(recvd_params), dim=0)
        self.net.apply_parameters(new_model_parameters)

    def evaluateTheRound(self, r):
        train_loss, train_acc = self.net.evaluate(self.train_dataset)
        dev_loss, dev_acc = self.net.evaluate(self.dev_dataset)
        test_loss, test_acc = self.net.evaluate(self.test_dataset)
        self.text_file.write('After round {}, train_loss = {}, train_acc = {}, dev_loss = {}, dev_acc = {}, test_loss = {}, test_acc = {}\n'.format(r, round(train_loss, 4), round(train_acc, 4), round(dev_loss, 4), round(dev_acc, 4), round(test_loss, 4), round(test_acc, 4)))

    def runTheRound(self, r):
        if r == Helper.rounds:
            p = self.net.get_parameters()
            s = ''.join([str(round(x, 4)) + "," for x in p.tolist()])
            file = open("temp_go_before.txt", "w")
            file.write(s)
            file.close()

        # client_parameters = self.train()
        self.net.fit(self.dataset)
        client_parameters = self.net.get_parameters()

        if r == Helper.rounds:
            p = self.net.get_parameters()
            s = ''.join([str(round(x, 4)) + "," for x in p.tolist()])
            file = open("temp_go_after.txt", "w")
            file.write(s)
            file.close()
            
        self.shareToNeighbors(client_parameters, r)

        recvd_params = []
        recvd_size = []
        recvd_params.append(client_parameters.cpu())
        recvd_size.append(self.get_dataset_size())
        while len(recvd_params) < len(self.neighbors) + 1:
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
        self.aggregateParams(recvd_params, recvd_size, r)
        
        if self.client_id == 0:
            self.evaluateTheRound(r)

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