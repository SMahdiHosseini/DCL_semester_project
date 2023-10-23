from Utils import Model, Helper, Message
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

    def get_dataset_size(self):
        return len(self.dataset)

    def connectToServer(self):
        address = (Helper.localHost, Helper.server_port)
        self.connection = Client(address)
        self.connection.send(Msg(self.client_id, header=Message.NEW_CONNECTION))

    def terminate(self):
        self.connection.close()

    def execute(self):
        first = True
        while True:
            msg = self.connection.recv()
            if msg.header == Message.TRAIN:
                if first is not True:
                    self.net.apply_parameters(msg.content)
                    p = self.net.get_parameters()
                    s = ''.join([str(round(x, 4)) + "," for x in p.tolist()])
                    file = open("temp_fl_before.txt", "w")
                    file.write(s)
                    file.close()

                # client_parameters = self.train()
                self.net.fit(self.dataset)
                client_parameters = self.net.get_parameters()

                if first is not True:
                    p = self.net.get_parameters()
                    s = ''.join([str(round(x, 4)) + "," for x in p.tolist()])
                    file = open("temp_fl_after.txt", "w")
                    file.write(s)
                    file.close()

                first = False
                self.connection.send(Msg(header=Message.NEW_PARAMETERS, content={Message.FRACTION: self.get_dataset_size(), Message.PARAMS: client_parameters}))
            if msg.header == Message.TERMINATE:
                break
def main():
    client_id = int(sys.argv[1])
    print("Client {} started! ... ".format(client_id))
    traning_client = TraningClient(client_id, torch.load("./Data/ClientsDatasets/" + str(client_id) + ".pt"))
    traning_client.connectToServer()
    print("Client connected to the server!")
    traning_client.execute()
    traning_client.terminate()
    print("Client {} terminated! ...".format(client_id))

if __name__ == "__main__":
    main()