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
    total_data = ''
    while ((len(total_data)*4) < params_size):
        p = connection.recv(params_size - (len(total_data) * 4)).decode()
        total_data = total_data + p
    params = [float(num) for num in total_data.split(',') if num]
    connection.send(jpysocket.jpyencode("ACK"))
    return params

def sendNewParameters(connection, params):
    connection.send(jpysocket.jpyencode(str(len(params))))
    connection.send(params)