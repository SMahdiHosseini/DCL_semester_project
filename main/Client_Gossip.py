from Utils import Model, Helper, Message, connectionHelper, evaluator, Log
from Utils.aggregator import RobustAggregator
from Utils.attacks import ByzantineAttack
from Utils.Message import Msg
from Utils.ConnectionDistributer import generateGossipPorts
from multiprocessing.connection import Client, Listener
import sys
import torch
from datetime import datetime
import threading

#program input: client_id, nb_clients, server_address, server_port, nb_byz, nb_rounds, aggregator_name, attack_name, test
client_id = int(sys.argv[1])
nb_clients = int(sys.argv[2])
server_address = sys.argv[3]
server_port = int(sys.argv[4])
nb_byz = int(sys.argv[5])
nb_rounds = int(sys.argv[6])
aggregator_name = sys.argv[7]
attack_name = sys.argv[8]
test = sys.argv[9]

log = Log.Log("/localhome/shossein/DCL_semester_project/Gossip_res/" + aggregator_name + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance/" + str(client_id) + ".txt")

def addNewLog(new_log):
    if test == Helper.performance_test:
        log.addLog(new_log)

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
        self.aggregator = RobustAggregator('nnm', aggregator_name, 1, nb_byz, Helper.device)
        self.attacker = ByzantineAttack(attack_name, nb_byz)
        if test == Helper.accuracy_test:
            self.text_file = open("/localhome/shossein/DCL_semester_project/Gossip_res/" + aggregator_name + "/ncl_" + str(nb_clients + nb_byz)  + "/nbyz_" + str(nb_byz) + "/Accuracy/"  + attack_name + "/" + str(client_id) + ".txt", "w")

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
        if test == Helper.accuracy_test and r == 1:
            evaluation(self.net.get_parameters(), 0, self.text_file)
            
        addNewLog("round_{}_start: {}\n".format(r, datetime.now().strftime("%H:%M:%S:%f")))
        self.net.fit(self.dataset)
        self.shareToNeighbors(r)
        addNewLog("round_{}_".format(r))
        t = datetime.now().strftime("%H:%M:%S:%f")
        recvd_params, recvd_size = connectionHelper.getAllParams(list(self.connections.values()), len(self.neighbors), self.net.get_parameters(), self.get_dataset_size(), self.client_id, r, nb_clients - nb_byz - 1, log, test)
        addNewLog("round_{}_aggregation: {}\n".format(r, datetime.now().strftime("%H:%M:%S:%f")))
        recvd_params[(self.client_id, t)] = self.net.get_parameters().cpu()
        recvd_size[(self.client_id, t)] = self.get_dataset_size()
        if test == Helper.accuracy_test:
            recvd_params = dict(sorted(recvd_params.items(), key=lambda x: x[0][1])[:nb_clients - nb_byz])
            byz_vectors = self.attacker.generate_byzantine_vectors(list(recvd_params.values()), None)
            id = -1
            for v in byz_vectors:
                recvd_params[(id, t)] = v
                id -= 1
            ordered_params = dict(sorted(recvd_params.items(), key=lambda x: x[0][1])[:nb_clients])
        else:
            ordered_params = dict(sorted(recvd_params.items(), key=lambda x: x[0][1])[:nb_clients - nb_byz])
        print(ordered_params.keys())
        new_model_parameters = self.aggregator.aggregate(list(ordered_params.values()))
        self.net.apply_parameters(new_model_parameters)
        addNewLog("round_{}_end: {}\n".format(r, datetime.now().strftime("%H:%M:%S:%f")))
        if test == Helper.accuracy_test:
            evaluation(new_model_parameters, r, self.text_file)

    def execute(self):
        addNewLog("Starting: {}\n".format(datetime.now().strftime("%H:%M:%S:%f")))
        for r in range(1, nb_rounds + 1):
            self.runTheRound(r)
        addNewLog("end: {}\n".format(datetime.now().strftime("%H:%M:%S:%f")))

def evaluation(params, r, text_file):
    evaluator.evaluateTheRound(params, r, text_file)

def main():
    print("Client {} started! ... ".format(client_id))
    ports, adjMat = generateGossipPorts(server_port, nb_clients)
    traning_client = TraningClient(client_id, torch.load("./Data/ClientsDatasets/" + str(client_id) + ".pt"), adjMat[client_id])
    traning_client.connectToNeighbors(ports[client_id])
    print("client connected to neighbors!")
    traning_client.execute()
    traning_client.terminate()
    print("Client {} terminated! ...".format(client_id))
    if test == Helper.performance_test:
        log.writeLogs()
if __name__ == "__main__":
    main()