from Utils import Helper, Model, Message, connectionHelper, ConnectionDistributer, Log
from Utils import evaluator
from multiprocessing.connection import Client
import sys
import torch
import threading
from datetime import datetime

#program input: nb_clients, client_id, server_address, server_port, nb_rounds, nb_byz, aggregator, attack, test
nb_clients = int(sys.argv[1])
client_id = int(sys.argv[2])
server_address = sys.argv[3]
server_port = int(sys.argv[4])
nb_rounds = int(sys.argv[5])
nb_byz = int(sys.argv[6])
aggregator = sys.argv[7]
attack = sys.argv[8]
test = sys.argv[9]

log = Log.Log("../FL_res/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance/" + str(client_id) + ".txt")

def addNewLog(new_log):
    if test == Helper.performance_test:
        log.addLog(new_log)

## Define Client Class
class TraningClient:
    def __init__(self, client_id, dataset):
        self.client_id = client_id
        self.dataset = dataset
        self.net = Helper.to_device(Model.FederatedNet(), Helper.device)
        self.connection = None
        if test == Helper.accuracy_test:
            self.text_file = open("../FL_res/" + aggregator + "/ncl_" + str(nb_clients)  + "/nbyz_" + str(nb_byz) + "/Accuracy/"  + attack + "/" + str(client_id) + ".txt", "w")

    def get_dataset_size(self):
        return len(self.dataset)

    def connectToServer(self, port):
        address = (server_address, port)
        self.connection = Client(address)
        print("Client {} connected to the server!".format(self.client_id))

    def runTheRound(self, r):
        addNewLog("round_{}_start: {}\n".format(r, datetime.now().strftime("%H:%M:%S:%f")))
        if test == Helper.accuracy_test and r == 1:
            evaluation(self.net.get_parameters(), 0, self.text_file)
        
        self.net.fit(self.dataset)
        client_parameters = self.net.get_parameters()
            
        connectionHelper.sendNewParameters(self.connection, client_parameters, connectionHelper.PYTHON, info={Message.ROUND: r, Message.SIZE: self.get_dataset_size(), Message.SRC: self.client_id})
        recvd_params, recvd_size = connectionHelper.getAllParams([self.connection], 1, client_parameters, self.get_dataset_size(), self.client_id, r, 1, None, Helper.accuracy_test)
        self.net.apply_parameters(list(recvd_params.values())[0])
        addNewLog("round_{}_end: {}\n".format(r, datetime.now().strftime("%H:%M:%S:%f")))
        if test == Helper.accuracy_test:
            evaluation(list(recvd_params.values())[0], r, self.text_file)

    def execute(self):
        addNewLog("Starting: {}\n".format(datetime.now().strftime("%H:%M:%S:%f")))
        for r in range(1, nb_rounds + 1):
            self.runTheRound(r)
        addNewLog("end: {}\n".format(datetime.now().strftime("%H:%M:%S:%f")))

    def terminate(self):
        self.connection.close()

def evaluation(params, r, text_file):
    evaluator.evaluateTheRound(params, r, text_file)
    return

def main():
    print("Client {} started! ... ".format(client_id))
    traning_client = TraningClient(client_id, torch.load("./Data/ClientsDatasets/" + str(client_id) + ".pt"))
    traning_client.connectToServer(ConnectionDistributer.generateFLPorts(server_port, nb_clients)[client_id])
    traning_client.execute()
    traning_client.terminate()
    print("Client {} terminated! ...".format(client_id))
    if test == Helper.performance_test:
        log.writeLogs()
if __name__ == "__main__":
    main()