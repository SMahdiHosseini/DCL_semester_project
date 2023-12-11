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
import multiprocessing as mp

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
threads = []
manager = mp.Manager()
shared_dict = manager.dict()
events = manager.dict()

def addNewLog(new_log):
    if test == Helper.performance_test:
        log.addLog(new_log)

## Define Client Class
class TraningClient:
    def __init__(self, client_id, dataset, neighbors):
        self.client_id = client_id
        self.dataset = dataset
        # self.net = Helper.to_device(Model.FederatedNet(), Helper.device)
        self.net = None
        self.neighbors = neighbors
        self.neighbors.sort()
        self.connections = dict()
        self.listeners = []
        self.aggregator = RobustAggregator('nnm', aggregator_name, 1, nb_byz, Helper.device)
        self.attacker = ByzantineAttack(attack_name, nb_byz)
        self.current_round = 0
        self.clients_parameters_queus = dict()
        for i in self.neighbors:
            events[i] = manager.Event()
            shared_dict[i] = manager.Queue()
        if test == Helper.accuracy_test:
            self.text_file = open("../Gossip_res/" + aggregator_name + "/ncl_" + str(nb_clients + nb_byz)  + "/nbyz_" + str(nb_byz) + "/Accuracy/"  + attack_name + "/" + str(client_id) + ".txt", "w")

    def get_dataset_size(self):
        return len(self.dataset)

    def initialize(self):
        print("Client {} initialized! ...".format(self.client_id))
        self.net = Helper.to_device(Model.FederatedNet(), Helper.device)

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
            t = threading.Thread(target=self.sendingThread, args=(self.connections[neighborId], shared_dict[neighborId], events[neighborId]))
            threads.append(t)
            t.start()
            print("Client {} connected to client {} !".format(self.client_id, neighborId))

    def terminate(self):
        for neighborId in self.neighbors:
            if self.client_id < neighborId :
                self.connections[neighborId].send(Msg(header=Message.TERMINATE))

            terminated = False
            while terminated == False:
                msg = self.connections[neighborId].recv()
                if msg.header == Message.ACK:
                    self.connections[neighborId].close()
                    terminated = True
                elif msg.header == Message.TERMINATE:
                    self.connections[neighborId].send(Msg(header=Message.ACK))
                    terminated = True
                else:
                    self.connections[neighborId].send(Msg(header=Message.ACK))

        for listener in self.listeners:
            listener.close()
    
    def shareToNeighbors(self):
        client_parameters = connectionHelper.tensorToString(self.net.get_parameters())
        # client_parameters = self.net.get_parameters()
        for neighborId in self.neighbors:
            shared_dict[neighborId].put((client_parameters, self.current_round))
            events[neighborId].set()
        # info={Message.ROUND: self.current_round, Message.SIZE: self.get_dataset_size(), Message.SRC: self.client_id}
        # for conn in self.connections.values():
        #     t = threading.Thread(target=connectionHelper.sendNewParameters, args=(conn, client_parameters, connectionHelper.PYTHON, info))
        #     threads.append(t)
        #     t.start()

    def sendingThread(self, conn, client_parameters_queue, e):
        while True:
            e.wait()
            if client_parameters_queue.empty():
                continue
            else:
                client_parameters, r = client_parameters_queue.get()
                if client_parameters == None:
                    return
                info={Message.ROUND: r, Message.SIZE: self.get_dataset_size(), Message.SRC: self.client_id}
                # connectionHelper.sendNewParameters(conn, client_parameters, connectionHelper.PYTHON, info)
                connectionHelper.sendNewParametersToPython(conn, client_parameters, info)
            e.clear()
                
            
    def runTheRound(self):
        if test == Helper.accuracy_test and self.current_round == 1:
            evaluation(self.net.get_parameters(), 0, self.text_file)
            
        self.net.fit(self.dataset)
        addNewLog("round_{}_model_trained: {}\n".format(self.current_round, datetime.now().strftime("%H:%M:%S:%f")))
        self.shareToNeighbors()
        addNewLog("round_{}_model_shared: {}\n".format(self.current_round, datetime.now().strftime("%H:%M:%S:%f")))

    def aggregate(self, recvd_params, t):
        addNewLog("round_{}_aggregation: {}\n".format(self.current_round, datetime.now().strftime("%H:%M:%S:%f")))
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
        # print(ordered_params.keys())
        addNewLog("round_{}_aggregation order: {}\n".format(self.current_round, [x[0] for x in ordered_params.keys()]))
        new_model_parameters = self.aggregator.aggregate(list(ordered_params.values()))
        self.net.apply_parameters(new_model_parameters)
        if test == Helper.accuracy_test:
            evaluation(new_model_parameters, self.current_round, self.text_file)
        return new_model_parameters
    
    def checkForTermination(self, termination):
        if self.current_round > nb_rounds and termination == False:
            termination = True
            for neighborId in self.neighbors:
                shared_dict[neighborId].put((None, 0))
                events[neighborId].set()
            for t in threads:
                t.join()
            for conn in self.connections.values():
                conn.send(Msg(header=Message.FINISHED))
        return termination

    def execute(self):
        addNewLog("Starting: {}\n".format(datetime.now().strftime("%H:%M:%S:%f")))
        
        termination = False
        self.current_round = 1
        round_params = dict()
        recvd_params = dict()
        for i in range(1, nb_rounds + 1):
            recvd_params[i] = dict()
        addNewLog("round_{}_start: {}\n".format(self.current_round, datetime.now().strftime("%H:%M:%S:%f")))
        t = datetime.now().strftime("%H:%M:%S:%f")
        self.runTheRound()
        recvd_params[self.current_round][(self.client_id, t)] = self.net.get_parameters().cpu()
        finished = 0
        while(self.current_round <= nb_rounds or finished < nb_clients - 1):
            # termination = self.checkForTermination(termination)
            ready_to_read, _, _ = select.select(list(self.connections.values()), [], [])
            for sock in ready_to_read:
                msg = sock.recv()
                if msg.header == Message.FINISHED:
                    finished += 1
                if msg.header == Message.NEW_PARAMETERS:
                    if int(msg.content[Message.ROUND]) == self.current_round:
                        t = datetime.now().strftime("%H:%M:%S:%f")
                        recvd_params[self.current_round][(msg.src_id, t)] = connectionHelper.stringToTensor(msg.content[Message.PARAMS])
                    elif int(msg.content[Message.ROUND]) > self.current_round:
                        recvd_params[int(msg.content[Message.ROUND])][(msg.src_id, t)] = connectionHelper.stringToTensor(msg.content[Message.PARAMS])
                        # sock.send(Msg(header=Message.WAIT))
                    # elif int(msg.content[Message.ROUND]) < self.current_round:
                    #     connectionHelper.sendNewParameters(sock, round_params[int(msg.content[Message.ROUND])], connectionHelper.PYTHON, info={Message.ROUND: msg.content[Message.ROUND], Message.SIZE: None, Message.SRC: None})
                    # if msg.header == Message.WAIT:
                    #     connectionHelper.sendNewParameters(sock, round_params[self.current_round], connectionHelper.PYTHON, info={Message.ROUND: self.current_round, Message.SIZE: None, Message.SRC: self.client_id})
                if termination == False and len(list(recvd_params[self.current_round].values())) >= nb_clients - nb_byz:
                    addNewLog("round_{}_received_params_{}: {}\n".format(self.current_round, str(nb_clients - nb_byz), datetime.now().strftime("%H:%M:%S:%f")))
                    round_params[self.current_round] = self.aggregate(recvd_params[self.current_round], t)
                    print("round {} finished {}".format(self.current_round, datetime.now().strftime("%H:%M:%S:%f")))
                    addNewLog("round_{}_end: {}\n".format(self.current_round, datetime.now().strftime("%H:%M:%S:%f")))
                    self.current_round += 1
                    if self.current_round <= nb_rounds:
                        addNewLog("round_{}_start: {}\n".format(self.current_round, datetime.now().strftime("%H:%M:%S:%f")))
                        t = datetime.now().strftime("%H:%M:%S:%f")
                        self.runTheRound()
                        recvd_params[self.current_round][(self.client_id, t)] = self.net.get_parameters().cpu()
                termination = self.checkForTermination(termination)

        addNewLog("end: {}\n".format(datetime.now().strftime("%H:%M:%S:%f")))
        print("Client Iteration Finished!")

def evaluation(params, r, text_file):
    evaluator.evaluateTheRound(params, r, text_file)

def main():
    print("Client {} started! ... ".format(client_id))
    ports, adjMat = generateGossipPorts(server_port, nb_clients)
    traning_client = TraningClient(client_id, torch.load("./Data/ClientsDatasets/" + str(client_id) + ".pt"), adjMat[client_id])
    traning_client.connectToNeighbors(ports[client_id])
    print("client connected to neighbors!")
    traning_client.initialize()
    traning_client.execute()
    if test == Helper.performance_test:
        log.writeLogs()
    traning_client.terminate()
    print("Client {} terminated! ...".format(client_id))
if __name__ == "__main__":
    main()