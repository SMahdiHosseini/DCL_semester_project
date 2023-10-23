
from Utils import Model, Helper, Message
from Utils.Message import Msg
from multiprocessing.connection import Listener
from torch.multiprocessing import Manager
from threading import Thread
from torch.multiprocessing import set_start_method
from torch import load
import torch
try:
     set_start_method('spawn')
except RuntimeError:
    pass

train_dataset = load("./Data/trainDataset.pt")
test_dataset = load("./Data/testDataset.pt")
dev_dataset = load("./Data/devDataset.pt")
total_train_size = len(train_dataset)

def receiveNewParams(connection, new_params):
    msg = connection.recv()
    if msg.header == Message.NEW_PARAMETERS:
        new_params.append(msg.content[Message.FRACTION] / total_train_size * msg.content[Message.PARAMS].cpu())

def getAllNewParams(connections, current_parameters):
    threads = []
    new_params = Manager().list()
    for client in connections.keys():
        connections[client].send(Msg(header=Message.TRAIN, content=current_parameters))
        new_thread = Thread(target=receiveNewParams, args=(connections[client], new_params))
        threads.append(new_thread)
        new_thread.start()    
    for t in threads:
        t.join()
    return new_params
    
def runTheRound(r, connections, global_net):
    print('Start Round {} ...'.format(r))
    new_params = getAllNewParams(connections, global_net.get_parameters())
    new_model_parameters = torch.sum(torch.stack(list(new_params)), dim=0)
    global_net.apply_parameters(new_model_parameters)

def evaluateTheRound(global_net, history, r):
    train_loss, train_acc = global_net.evaluate(train_dataset)
    dev_loss, dev_acc = global_net.evaluate(dev_dataset)
    test_loss, test_acc = global_net.evaluate(test_dataset)
    print('After round {}, train_loss = {}, train_acc = {}, dev_loss = {}, dev_acc = {}, test_loss = {}, test_acc = {}\n'.format(r, round(train_loss, 4), round(train_acc, 4), round(dev_loss, 4), round(dev_acc, 4), round(test_loss, 4), round(test_acc, 4)))
    history.append((train_loss, dev_loss))

def federatedLearningPhase(connections):
    global_net = Helper.to_device(Model.FederatedNet(), Helper.device)
    history = []
    for i in range(Helper.rounds):
        runTheRound(i + 1, connections, global_net)
        evaluateTheRound(global_net, history, i + 1)

def connectToClient(listener):
    new_connection = listener.accept()
    msg = new_connection.recv()
    if msg.header == Message.NEW_CONNECTION:
        print("Server established new connection with client {}".format(msg.src_id))
        return msg.src_id, new_connection

def connectionEstablishmentPahse():
    address = (Helper.localHost, Helper.server_port)
    listener = Listener(address)
    connections = dict()
    print("Server is running on port: {}".format(Helper.server_port))
    for client in range(Helper.num_clients):
        src_id, new_connecion = connectToClient(listener)
        connections[src_id] = new_connecion
    print("Server connected to clients: {}".format(str(connections.keys())))
    return listener, connections

def closeConnections(connections):
    print("Server in closing sonnections!")
    for connection in connections:
        connection.send(Msg(header=Message.TERMINATE))
        connection.close()

def main():
    listener, connections = connectionEstablishmentPahse()
    federatedLearningPhase(connections)
    closeConnections(connections.values())
    listener.close()
    print("Done!")

if __name__ == '__main__':
    main()