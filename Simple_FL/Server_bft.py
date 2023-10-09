
from Utils import Model, Helper, Message
from Utils.Message import Msg
from multiprocessing.connection import Listener
from torch.multiprocessing import Manager
from threading import Thread
from torch.multiprocessing import set_start_method
from torch import load
from Utils import Model, Helper
import sys
import socket
import jpysocket
import torch
import json

try:
     set_start_method('spawn')
except RuntimeError:
    pass

train_dataset = load("./Data/trainDataset.pt")
test_dataset = load("./Data/testDataset.pt")
dev_dataset = load("./Data/devDataset.pt")
total_train_size = len(train_dataset)

def connect(hostAddress, hostPort):
    address = (hostAddress, hostPort)
    connection = socket.socket()
    connection.connect(address)
    return connection

def receiveNewParams(new_param, dataset_size):
    client_parameters = dict([(layer_name, {'weight': 0, 'bias': 0}) for layer_name in new_param])
    for layer_name in new_param:
        # convert Tensros from CUDA to CPU to aggregate them
        client_parameters[layer_name]['weight'] = dataset_size / total_train_size * new_param[layer_name]['weight'].cpu()
        client_parameters[layer_name]['bias'] = dataset_size / total_train_size * new_param[layer_name]['bias'].cpu()
    return client_parameters

def unzip_data(data):
    data = data.split("#")
    dataset_size = data[0]
    params = json.loads(data[1])
    return dataset_size, params

def pushNewParams(connection, new_params):
    connection.send(jpysocket.jpyencode("ACK"))
    msg_size = int(jpysocket.jpydecode(connection.recv(1024))) * 4
    connection.send(jpysocket.jpyencode("ACK"))
    msg = connection.recv(msg_size).decode()
    connection.send(jpysocket.jpyencode("ACK"))
    dataset_size, params = unzip_data(msg)
    new_params.append(receiveNewParams(params, dataset_size))
    return new_params

def execute(connection):
    new_params = []
    while True:
        msg = jpysocket.jpydecode(connection.recv(1024))
        if msg == "NEWPARAMS":
            new_params = pushNewParams(connection, new_params)
            print(new_params)
        # if msg == "TRAIN":
        #     client_parameters = traning_client.train()
        #     res = str(client_parameters)
        #     connection.send(jpysocket.jpyencode(str(traning_client.get_dataset_size())))
        #     connection.send(jpysocket.jpyencode(str(len(res))))
        #     # connection.send(jpysocket.jpyencode(res))
        #     connection.send(bytes(res, 'utf-8'))
        if msg == "TERMINATE":
            connection.send(jpysocket.jpyencode("ACK"))
            break

def main():
    print("Client server started! ... ")
    global_net = Helper.to_device(Model.FederatedNet(), Helper.device)
    connection = connect(sys.argv[1], int(sys.argv[2]))
    execute(connection)
    connection.close()
    print("Server terminated! ...")


if __name__ == "__main__":
    main()