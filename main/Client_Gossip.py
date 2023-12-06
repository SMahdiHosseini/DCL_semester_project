from Utils import Model, Helper, Message, connectionHelper, evaluator, Log
from Utils.aggregator import RobustAggregator
from Utils.attacks import ByzantineAttack
from Utils.Message import Msg
from Utils.ConnectionDistributer import generateGossipPorts, readConfig
from multiprocessing.connection import Client, Listener
import sys
import torch
from datetime import datetime
import select
import threading

#program input: client_id, nb_clients, listening_address, server_port, nb_byz, nb_rounds, aggregator_name, attack_name, test
client_id = int(sys.argv[1])
nb_clients = int(sys.argv[2])
listening_address = sys.argv[3]
server_port = int(sys.argv[4])
nb_byz = int(sys.argv[5])
nb_rounds = int(sys.argv[6])
aggregator_name = sys.argv[7]
attack_name = sys.argv[8]
test = sys.argv[9]

log = Log.Log("../Gossip_res/" + aggregator_name + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance/" + str(client_id) + ".txt")

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
            self.text_file = open("../Gossip_res/" + aggregator_name + "/ncl_" + str(nb_clients + nb_byz)  + "/nbyz_" + str(nb_byz) + "/Accuracy/"  + attack_name + "/" + str(client_id) + ".txt", "w")

    def get_dataset_size(self):
        return len(self.dataset)

    def connectToNeighbors(self, ports):
        config = readConfig('ips.config')
        for neighborId in self.neighbors:
            if neighborId < self.client_id:
                address = (config['client_' + str(neighborId)], ports[neighborId])
                self.connections[neighborId] = Client(address)
            else:
                address = (listening_address, ports[neighborId])
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
            
        self.net.fit(self.dataset)
        addNewLog("round_{}_model_trained: {}\n".format(r, datetime.now().strftime("%H:%M:%S:%f")))
        self.shareToNeighbors(r)
        addNewLog("round_{}_model_shared: {}\n".format(r, datetime.now().strftime("%H:%M:%S:%f")))

    def aggregate(self, r, recvd_params, t):
        addNewLog("round_{}_aggregation: {}\n".format(r, datetime.now().strftime("%H:%M:%S:%f")))
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
        print("round {} param {}".format(r, new_model_parameters)) 
        if test == Helper.accuracy_test:
            evaluation(new_model_parameters, r, self.text_file)
        return new_model_parameters
    def checkForTermination(self, r):
            if r > nb_rounds:
                for conn in self.connections.values():
                    conn.send(Msg(header=Message.TERMINATE))

    def execute(self):
        addNewLog("Starting: {}\n".format(datetime.now().strftime("%H:%M:%S:%f")))
        
        r = 1
        round_params = dict()
        recvd_params = dict()
        addNewLog("round_{}_start: {}\n".format(r, datetime.now().strftime("%H:%M:%S:%f")))
        t = datetime.now().strftime("%H:%M:%S:%f")
        self.runTheRound(r)
        recvd_params[(self.client_id, t)] = self.net.get_parameters().cpu()
        termination = 0
        while(r <= nb_rounds or termination < nb_clients - 1):
            self.checkForTermination(r)
            ready_to_read, _, _ = select.select(list(self.connections.values()), [], [])
            for sock in ready_to_read:
                msg = sock.recv()
                if msg.header == Message.TERMINATE:
                    termination += 1
                if msg.header == Message.NEW_PARAMETERS:
                    if int(msg.content[Message.ROUND]) == r:
                        t = datetime.now().strftime("%H:%M:%S:%f")
                        recvd_params[(msg.src_id, t)] = connectionHelper.stringToTensor(msg.content[Message.PARAMS])
                    elif int(msg.content[Message.ROUND]) > r:
                        sock.send(Msg(header=Message.WAIT))
                    elif int(msg.content[Message.ROUND]) < r:
                        print(round_params)
                        connectionHelper.sendNewParameters(sock, round_params[int(msg.content[Message.ROUND])], connectionHelper.PYTHON, info={Message.ROUND: msg.content[Message.ROUND], Message.SIZE: None, Message.SRC: None})
                    if msg.header == Message.WAIT:
                        connectionHelper.sendNewParameters(sock, round_params[r], connectionHelper.PYTHON, info={Message.ROUND: r, Message.SIZE: None, Message.SRC: self.client_id})
                if len(list(recvd_params.values())) >= nb_clients - nb_byz:
                    addNewLog("round_{}_received_params_{}: {}\n".format(r, str(nb_clients - nb_byz), datetime.now().strftime("%H:%M:%S:%f")))
                    round_params[r] = self.aggregate(r, recvd_params, t)
                    print("round {} finished".format(r))
                    addNewLog("round_{}_end: {}\n".format(r, datetime.now().strftime("%H:%M:%S:%f")))
                    r += 1
                    if r <= nb_rounds:
                        recvd_params = dict()
                        addNewLog("round_{}_start: {}\n".format(r, datetime.now().strftime("%H:%M:%S:%f")))
                        t = datetime.now().strftime("%H:%M:%S:%f")
                        self.runTheRound(r)
                        recvd_params[(self.client_id, t)] = self.net.get_parameters().cpu()

        addNewLog("end: {}\n".format(datetime.now().strftime("%H:%M:%S:%f")))
        print("Client ++++++++")

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
    # if test == Helper.performance_test:
    #     log.writeLogs()
if __name__ == "__main__":
    main()