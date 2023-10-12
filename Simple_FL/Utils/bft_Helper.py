import socket
import jpysocket

def connect(hostAddress, hostPort):
    address = (hostAddress, hostPort)
    connection = socket.socket()
    connection.connect(address)
    print("Connected!")
    return connection

def getNewParameters(connection):
    connection.send(jpysocket.jpyencode("ACK"))
    params_size = int(jpysocket.jpydecode(connection.recv(1024))) * 4
    connection.send(jpysocket.jpyencode("ACK"))
    p = connection.recv(params_size).decode()
    params = [float(num) for num in p.split(',') if num]
    connection.send(jpysocket.jpyencode("ACK"))
    return params

def sendNewParameters(connection, params):
    connection.send(jpysocket.jpyencode(str(len(params))))
    connection.send(params)