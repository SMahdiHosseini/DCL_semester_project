import socket
import jpysocket
from torch import tensor
from Utils import Message

JAVA = "JAVA"
PYTHON = "PYTHON"

def tensorToString(t):
    return ''.join([str(round(x, 4)) + "," for x in t.tolist()])

def stringToTensor(s):
    return tensor([float(num) for num in s.split(',') if num])

def connect(hostAddress, hostPort):
    address = (hostAddress, hostPort)
    connection = socket.socket()
    connection.connect(address)
    print("Connected!")
    return connection

def sendNewParameters(connection, params, config):
    params = bytes(tensorToString(params), 'utf-8')
    if config == JAVA:
        sendNewParametersToJava(connection, params)
    else:
        sendNewParametersToPython(connection)

def getNewParameters(connection, config):
    if config == JAVA:
        return getNewParametersFromJava(connection)
    else:
        return getNewParametersFromPython(connection)
    
def getNewParametersFromPython(connection):
    #TODO
    return None

def sendNewParametersToPython(connection, params):
    #TODO
    return

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