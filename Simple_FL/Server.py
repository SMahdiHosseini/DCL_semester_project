from Utils import Helper, Message
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
    recvd_params = []
    recvd_size = []
    while len(recvd_params) < Helper.num_clients:
        ready_to_read, _, _ = select.select(connections, [], [])
        for sock in ready_to_read:
            msg = sock.recv()
            if msg.header == Message.NEW_PARAMETERS:
                if int(msg.content[Message.ROUND]) == r:
                    recvd_params.append(torch.tensor([float(num) for num in msg.content[Message.PARAMS].split(',') if num]))
                    recvd_size.append(msg.content[Message.FRACTION])
                else:
                    sock.send(Msg(header=Message.WAIT))
    cluster_size = sum(recvd_size)
    for i in range(len(recvd_params)):
        recvd_params[i] = recvd_size[i] / cluster_size * recvd_params[i]
    new_model_parameters = torch.sum(torch.stack(recvd_params), dim=0)
    new_model_parameters = ''.join([str(round(x, 4)) + "," for x in new_model_parameters.tolist()])
    
    for conn in connections:
        conn.send(Msg(header=Message.NEW_PARAMETERS, content=new_model_parameters))

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
    execute(connections.values())
    terminate(connections.values(), listeners)
    print("Server terminated! ...")

if __name__ == "__main__":
    main()