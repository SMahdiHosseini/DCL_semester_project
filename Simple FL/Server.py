
from Utils import Model, Helper, Message
from Utils.Message import Msg
from Utils.DataDistributer import test_dataset, dev_dataset, train_dataset
from multiprocessing.connection import Listener
from multiprocessing import Manager
from threading import Thread

def receiveNewParams(connection, new_params):
    msg = connection.recv()
    if msg.header == Message.NEW_PARAMETERS:
        new_params.append(msg.content)

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
    return list(new_params)
    
def runTheRound(round, connections, global_net):
    print('Start Round {} ...'.format(round))
    new_params = getAllNewParams(connections, global_net.get_parameters())
    curr_parameters = global_net.get_parameters()
    new_model_parameters = dict([(layer_name, {'weight': 0, 'bias': 0}) for layer_name in curr_parameters])
    for params in new_params:
        for layer_name in params[Message.PARAMS]:
            new_model_parameters[layer_name]['weight'] += params[Message.FRACTION] * params[Message.PARAMS][layer_name]['weight']
            new_model_parameters[layer_name]['bias'] += params[Message.FRACTION] * params[Message.PARAMS][layer_name]['bias']    
    
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
        evaluateTheRound(global_net, history, round)

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
    for connection in connections:
        connection.send(Msg(header=Message.TERMINATE))
        connection.close()

def main():
    listener, connections = connectionEstablishmentPahse()
    federatedLearningPhase(connections)
    closeConnections(connections.values())
    listener.close()

if __name__ == '__main__':
    main()