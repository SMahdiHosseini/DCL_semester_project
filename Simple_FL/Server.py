from Utils import Helper, Message, connectionHelper, aggregator
from Utils.Message import Msg
from multiprocessing.connection import Listener
import select
import torch

def connectToClients(ports):
    Listeners = []
    connections = dict()
    for client in range(Helper.num_clients):
        address = (Helper.localHost, ports[client])
        listener = Listener(address)
        connections[client] = listener.accept()
        Listeners.append(listener)
        
    print("Server connected to clients!")
    return Listeners, connections

def runTheRound(r, connections):
    recvd_params, recvd_size = connectionHelper.getAllParams(connections, Helper.num_clients, None, None, None, r)
    new_model_parameters = aggregator.averageAgg(list(recvd_params.values()), list(recvd_size.values()))
    
    for conn in connections:
        connectionHelper.sendNewParameters(conn, new_model_parameters, connectionHelper.PYTHON, info={Message.ROUND: r, Message.SIZE: None, Message.SRC: None})

def execute(connections):
    for r in range(1, Helper.rounds + 1):
        runTheRound(r, connections)

def terminate(connections, listeners):
    for conn in connections:
        conn.close()
    for lis in listeners:
        lis.close()

def main():
    print("Server started! ... ")
    listeners, connections = connectToClients(Helper.ports)
    execute(list(connections.values()))
    terminate(list(connections.values()), listeners)
    print("Server terminated! ...")

if __name__ == "__main__":
    main()