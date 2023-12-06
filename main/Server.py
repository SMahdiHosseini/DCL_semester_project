from Utils import Helper, Message, connectionHelper, ConnectionDistributer
from Utils.Log import Log
from Utils.aggregator import RobustAggregator
from Utils.attacks import ByzantineAttack
from multiprocessing.connection import Listener
import sys
from datetime import datetime
import threading

#program input: nb_clients, server_address, server_port, nb_byz, nb_rounds, aggregator_name, attack_name, test
nb_clients = int(sys.argv[1])
server_address = sys.argv[2]
server_port = int(sys.argv[3])
nb_byz = int(sys.argv[4])
nb_rounds = int(sys.argv[5])
aggregator_name = sys.argv[6]
attack_name = sys.argv[7]
test = sys.argv[8]
aggregator = RobustAggregator('nnm', aggregator_name, 1, nb_byz, Helper.device)
attacker = ByzantineAttack(attack_name, nb_byz)
log = Log("../FL_res/" + aggregator_name + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance/server.txt")

def addNewLog(new_log):
    if test == Helper.performance_test:
        log.addLog(new_log)

def connectToClients(ports):
    Listeners = []
    connections = dict()
    for client in range(nb_clients):
        address = (server_address, ports[client])
        listener = Listener(address)
        connections[client] = listener.accept()
        Listeners.append(listener)
        
    print("Server connected to clients!")
    return Listeners, connections

def handleRemainedClients(connections, params, r):
    connectionHelper.getAllParams(connections, len(connections), None, None, None, r, len(connections), log, test)
    for conn in connections:
        connectionHelper.sendNewParameters(conn, params, connectionHelper.PYTHON, info={Message.ROUND: r, Message.SIZE: None, Message.SRC: None})
    

def runTheRound(r, connections):
    addNewLog("round_{}_start: {}\n".format(r, datetime.now().strftime("%H:%M:%S:%f")))
    addNewLog("round_{}_".format(r))
    t = datetime.now().strftime("%H:%M:%S:%f")
    recvd_params, recvd_size = connectionHelper.getAllParams(list(connections.values()), nb_clients - nb_byz, None, None, None, r, nb_clients - nb_byz, log, test)
    # recvd_params, recvd_size = connectionHelper.getAllParams(connections, nb_clients, None, None, None, r, nb_clients - nb_byz, log, test)
    addNewLog("round_{}_aggregation: {}\n".format(r, datetime.now().strftime("%H:%M:%S:%f")))
    if test == Helper.accuracy_test:
        recvd_params = dict(sorted(recvd_params.items(), key=lambda x: x[0][1])[:nb_clients - nb_byz])
        print(recvd_params.keys())
        byz_vectors = attacker.generate_byzantine_vectors(list(recvd_params.values()), None)
        id = -1
        for v in byz_vectors:
            recvd_params[(id, t)] = v
            id -= 1
        ordered_params = dict(sorted(recvd_params.items(), key=lambda x: x[0][1])[:nb_clients])
    else:
        ordered_params = dict(sorted(recvd_params.items(), key=lambda x: x[0][1])[:nb_clients - nb_byz])
    print(ordered_params.keys())
    addNewLog("round_{}_aggregation order: {}\n".format(r, [x[0] for x in ordered_params.keys()]))
    new_model_parameters = aggregator.aggregate(list(ordered_params.values()))
    recvd_connections = [connections[s] for s in list(connections.keys()) if s in [k[0] for k in ordered_params.keys()]]
    unrecvd_connections = [connections[s] for s in list(connections.keys()) if s not in [k[0] for k in ordered_params.keys()]]

    t1 = threading.Thread(target=handleRemainedClients, args=(unrecvd_connections, new_model_parameters, r))
    t1.start()
    for conn in recvd_connections:
        connectionHelper.sendNewParameters(conn, new_model_parameters, connectionHelper.PYTHON, info={Message.ROUND: r, Message.SIZE: None, Message.SRC: None})
    t1.join()
    
    addNewLog("round_{}_end: {}\n".format(r, datetime.now().strftime("%H:%M:%S:%f")))

def execute(connections):
    addNewLog("Starting: {}\n".format(datetime.now().strftime("%H:%M:%S:%f")))
    for r in range(1, nb_rounds + 1):
        runTheRound(r, connections)
    addNewLog("end: {}\n".format(datetime.now().strftime("%H:%M:%S:%f")))

def terminate(connections, listeners):
    for conn in connections:
        conn.close()
    for lis in listeners:
        lis.close()

def main():
    print("Server started! ... ")
    listeners, connections = connectToClients(ConnectionDistributer.generateFLPorts(server_port, nb_clients))
    execute(connections)
    terminate(list(connections.values()), listeners)
    print("Server terminated! ...")
    if test == Helper.performance_test:
        log.writeLogs()
if __name__ == "__main__":
    main()