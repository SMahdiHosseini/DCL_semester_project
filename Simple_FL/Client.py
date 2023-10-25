from Utils import Helper, Model, Message
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
            self.train_dataset = torch.load("/localhome/shossein/DCL_semester_project/Simple_FL/Data/trainDataset.pt")
            self.test_dataset = torch.load("/localhome/shossein/DCL_semester_project/Simple_FL/Data/testDataset.pt")
            self.dev_dataset = torch.load("/localhome/shossein/DCL_semester_project/Simple_FL/Data/devDataset.pt")
            self.text_file = open("/localhome/shossein/DCL_semester_project/FL_res/Output.txt", "w")

    def get_dataset_size(self):
        return len(self.dataset)
    
    def evaluateTheRound(self, r):
        train_loss, train_acc = self.net.evaluate(self.train_dataset)
        dev_loss, dev_acc = self.net.evaluate(self.dev_dataset)
        test_loss, test_acc = self.net.evaluate(self.test_dataset)
        self.text_file.write('After round {}, train_loss = {}, train_acc = {}, dev_loss = {}, dev_acc = {}, test_loss = {}, test_acc = {}\n'.format(r, round(train_loss, 4), round(train_acc, 4), round(dev_loss, 4), round(dev_acc, 4), round(test_loss, 4), round(test_acc, 4)))

    def connectToServer(self, port):
        address = (Helper.localHost, port)
        self.connection = Client(address)
        print("Client {} connected to the server!".format(self.client_id))

    def runTheRound(self, r):
        self.net.fit(self.dataset)
        client_parameters = ''.join([str(round(x, 4)) + "," for x in self.net.get_parameters().cpu().tolist()])
            
        self.connection.send(Msg(header=Message.NEW_PARAMETERS, content={Message.ROUND: str(r), Message.FRACTION: self.get_dataset_size(), Message.PARAMS: client_parameters}))

        recvd_params = False
        while recvd_params is False:
            msg = self.connection.recv()
            if msg.header == Message.NEW_PARAMETERS:
                recvd_params = True
                self.net.apply_parameters(torch.tensor([float(num) for num in msg.content.split(',') if num]))
            if msg.header == Message.WAIT:
                self.connection.send(Msg(header=Message.NEW_PARAMETERS, content={Message.ROUND: str(r), Message.FRACTION: self.get_dataset_size(), Message.PARAMS: client_parameters}))

    def execute(self):
        for r in range(1, Helper.rounds + 1):
            self.runTheRound(r)
            if self.client_id == 0:
                self.evaluateTheRound(r)

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