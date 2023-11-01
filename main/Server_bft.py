from Utils import Message, connectionHelper, Helper
from Utils.aggregator import RobustAggregator
import sys
import jpysocket

#program input: server_address, server_port, nb_byz, aggregator_name
server_address = sys.argv[1]
server_port = int(sys.argv[2])
nb_byz = int(sys.argv[3])
aggregator_name = sys.argv[4]
aggregator = RobustAggregator(aggregator_name, '', 1, nb_byz, Helper.device)

def handleNewParam(connection):
    connection.send(jpysocket.jpyencode("ACK"))
    datasetSize = int(jpysocket.jpydecode(connection.recv(1024)))
    return datasetSize, connectionHelper.getNewParameters(connection, connectionHelper.JAVA)

def finalizeTheRound(recvd_params, connection):
    new_param = aggregator.aggregate(recvd_params)
    connectionHelper.sendNewParameters(connection, new_param, connectionHelper.JAVA)

def execute(connection):
    recvd_params = []
    recvd_size = []
    r = 1
    while True:
        msg = jpysocket.jpydecode(connection.recv(1024))
        if msg == Message.NEW_PARAMETERS:
            s, params = handleNewParam(connection)
            recvd_params.append(params)
            recvd_size.append(s)
            continue
        if msg == Message.AGGREGATE:
            finalizeTheRound(recvd_params[:len(recvd_params) - nb_byz], connection)
            r += 1
            recvd_params = []
            recvd_size = []
            continue
        if msg == Message.TERMINATE:
            connection.send(jpysocket.jpyencode("ACK"))
            return

def main():
    print("server started! ... ")
    connection = connectionHelper.connect(server_address, server_port)
    execute(connection)
    connection.close()
    print("Server terminated! ...")


if __name__ == "__main__":
    main()