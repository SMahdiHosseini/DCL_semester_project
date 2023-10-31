from Utils import Helper, Message, connectionHelper, ConnectionDistributer
from Utils.aggregator import RobustAggregator
from multiprocessing.connection import Listener
import sys

#program input: nb_clients, server_address, server_port, nb_byz, nb_rounds
nb_clients = int(sys.argv[1])
server_address = sys.argv[2]
server_port = int(sys.argv[3])
nb_byz = int(sys.argv[4])
nb_rounds = int(sys.argv[5])
aggregator = RobustAggregator("average", '', 1, nb_byz, Helper.device)

def connectToClients(ports):
    Listeners = []
    connections = dict()
    for client in range(nb_clients):
        address = (server_address, ports[client])
        listener = Listener(address)
        connections[client] = listener.accept()
        Listeners.append(listener)
        
    print("Server connected to clients!")
    return Listeners, connections

def runTheRound(r, connections):
    recvd_params, recvd_size = connectionHelper.getAllParams(connections, nb_clients - nb_byz, None, None, None, r)
    new_model_parameters = aggregator.aggregate(list(recvd_params.values()))
    
    for conn in connections:
        connectionHelper.sendNewParameters(conn, new_model_parameters, connectionHelper.PYTHON, info={Message.ROUND: r, Message.SIZE: None, Message.SRC: None})

def execute(connections):
    for r in range(1, nb_rounds + 1):
        runTheRound(r, connections)

def terminate(connections, listeners):
    for conn in connections:
        conn.close()
    for lis in listeners:
        lis.close()

def main():
    print("Server started! ... ")
    listeners, connections = connectToClients(ConnectionDistributer.generateFLPorts(server_port, nb_clients))
    execute(list(connections.values()))
    terminate(list(connections.values()), listeners)
    print("Server terminated! ...")

if __name__ == "__main__":
    main()