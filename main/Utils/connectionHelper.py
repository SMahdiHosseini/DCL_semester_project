import socket
import jpysocket
from torch import tensor
from Utils import Message, Log, Helper
from Utils.Message import Msg
import select
from datetime import datetime

JAVA = "JAVA"
PYTHON = "PYTHON"
LOGFILE = "FILE"
TEST  = "TEST"

def tensorToString(t):
    return ''.join([str(round(x, 5)) + "," for x in t.tolist()])

def stringToTensor(s):
    return tensor([round(float(num), 5) for num in s.split(',') if num])

def connect(hostAddress, hostPort):
    address = (hostAddress, hostPort)
    connection = socket.socket()
    connection.connect(address)
    print("Connected!")
    return connection

def sendNewParameters(connection, params, config, info=None):
    params = tensorToString(params)
    if config == JAVA:
        sendNewParametersToJava(connection, bytes(params, 'utf-8'))
    else:
        sendNewParametersToPython(connection, params, info)

def getNewParameters(connection, config, info=None):
    if config == JAVA:
        return getNewParametersFromJava(connection)
    else:
        return getNewParametersFromPython(connection, info)
    
def getNewParametersFromPython(connections, info):
    recvd_params = dict()
    recvd_size = dict()
    ready_to_read, _, _ = select.select(connections, [], [])
    for sock in ready_to_read:
        msg = sock.recv()
        if msg.header == Message.NEW_PARAMETERS:
            if int(msg.content[Message.ROUND]) == info[Message.ROUND]:
                t = datetime.now().strftime("%H:%M:%S:%f")
                recvd_params[(msg.src_id, t)] = stringToTensor(msg.content[Message.PARAMS])
                recvd_size[(msg.src_id, t)] = msg.content[Message.SIZE]
            elif int(msg.content[Message.ROUND]) > info[Message.ROUND]:
                sock.send(Msg(header=Message.WAIT))
        if msg.header == Message.WAIT and info[Message.SRC] != None:
            sendNewParameters(sock, info[Message.PARAMS], PYTHON, info={Message.ROUND: info[Message.ROUND], Message.SIZE: info[Message.SIZE], Message.SRC: info[Message.SRC]})
    return recvd_params, recvd_size

def sendNewParametersToPython(connection, params, info):
    connection.send(Msg(header=Message.NEW_PARAMETERS, content={Message.ROUND: info[Message.ROUND], Message.SIZE: info[Message.SIZE], Message.PARAMS: params}, src_id=info[Message.SRC]))

def getNewParametersFromJava(connection):
    connection.send(jpysocket.jpyencode("ACK"))
    params_size = int(jpysocket.jpydecode(connection.recv(1024))) * 4
    connection.send(jpysocket.jpyencode("ACK"))
    total_data = ''
    while ((len(total_data)*4) < params_size):
        p = connection.recv(params_size - (len(total_data) * 4)).decode()
        total_data = total_data + p
    params = stringToTensor(total_data)
    connection.send(jpysocket.jpyencode("ACK"))
    return params

def sendNewParametersToJava(connection, params):
    connection.send(jpysocket.jpyencode(str(len(params))))
    connection.send(params)

def getAllParams(connections, num_of_connections, client_parameters, dataset_size, client_id, r, num_of_params, log, test):
    recvd_params = dict()
    recvd_size = dict()
    while len(list(recvd_size.values())) < num_of_connections:
        new_params, new_sizes = getNewParameters(connections, PYTHON, info={Message.ROUND: r, Message.SIZE: dataset_size, Message.PARAMS: client_parameters, Message.SRC: client_id})
        recvd_params.update(new_params)
        recvd_size.update(new_sizes)
        if test == Helper.performance_test and len(list(recvd_size.values())) >= num_of_params:
            log.addLog("received_params: {}\n".format(datetime.now().strftime("%H:%M:%S:%f")))

    return recvd_params, recvd_size