from Utils import Message, connectionHelper, Helper
from Utils.aggregator import RobustAggregator
from Utils.attacks import ByzantineAttack
from Utils.Log import Log
import sys
import jpysocket
from datetime import datetime


#program input: server_address, server_port, server_id, nb_clients, nb_byz, aggregator_name, attack_name, test
server_address = sys.argv[1]
server_port = int(sys.argv[2])
server_id = int(sys.argv[3])
nb_clients = int(sys.argv[4])
nb_byz = int(sys.argv[5])
aggregator_name = sys.argv[6]
attack_name = sys.argv[7]
test = sys.argv[8]
aggregator = RobustAggregator('nnm', aggregator_name, 1, nb_byz, Helper.device)
attacker = ByzantineAttack(attack_name, nb_byz)
log = Log("../../../../Consensus_res/" + aggregator_name + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance/server_" + str(server_id) + ".txt")

def addNewLog(new_log):
    if test == Helper.performance_test:
        log.addLog(new_log)

def handleNewParam(connection):
    connection.send(jpysocket.jpyencode("ACK"))
    datasetSize = int(jpysocket.jpydecode(connection.recv(1024)))
    return datasetSize, connectionHelper.getNewParameters(connection, connectionHelper.JAVA)

def finalizeTheRound(recvd_params, connection):
    if test == Helper.accuracy_test:
        byz_vectors = attacker.generate_byzantine_vectors(recvd_params, None)
        for v in byz_vectors:
            recvd_params.insert(0, v)
        new_param = aggregator.aggregate(recvd_params[:nb_clients])
    else:
        new_param = aggregator.aggregate(recvd_params)
    connectionHelper.sendNewParameters(connection, new_param, connectionHelper.JAVA)

def execute(connection):
    recvd_params = []
    recvd_size = []
    r = 1
    addNewLog("Starting: {}\n".format(datetime.now().strftime("%H:%M:%S:%f")))
    while True:
        if test == Helper.performance_test and r == 1 and len(recvd_params) == 0:
            addNewLog("round_{}_start: {}\n".format(r, datetime.now().strftime("%H:%M:%S:%f")))
        msg = jpysocket.jpydecode(connection.recv(1024))
        if msg == Message.NEW_PARAMETERS:
            s, params = handleNewParam(connection)
            recvd_params.append(params)
            recvd_size.append(s)
            if test == Helper.performance_test and len(recvd_params) == nb_clients - nb_byz:
                addNewLog("round_{}_received_params: {}\n".format(r, datetime.now().strftime("%H:%M:%S:%f")))
            continue
        if msg == Message.AGGREGATE:
            addNewLog("round_{}_aggregation: {}\n".format(r, datetime.now().strftime("%H:%M:%S:%f")))
            finalizeTheRound(recvd_params[:nb_clients - nb_byz], connection)
            addNewLog("round_{}_end: {}\n".format(r, datetime.now().strftime("%H:%M:%S:%f")))
            r += 1
            recvd_params = []
            recvd_size = []
            addNewLog("round_{}_start: {}\n".format(r, datetime.now().strftime("%H:%M:%S:%f")))
            continue
        if msg == Message.TERMINATE:
            addNewLog("end: {}\n".format(datetime.now().strftime("%H:%M:%S:%f")))
            if test == Helper.performance_test:
                log.writeLogs()
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