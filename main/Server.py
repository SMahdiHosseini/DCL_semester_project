import random
from Utils import Helper, Message, connectionHelper, ConnectionDistributer
from Utils.Log import Log
from Utils.aggregator import RobustAggregator
from Utils.attacks import ByzantineAttack
from Utils.Message import Msg
from multiprocessing.connection import Listener
import sys
from datetime import datetime
import threading
import select
import multiprocessing as mp

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
if test == Helper.accuracy_test:
    orders = aggregator.readOrders(None, nb_clients, nb_byz, nb_rounds, attack_name, 'fl')

log = Log("../FL_res/" + aggregator_name + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance/server.txt")
threads = []
manager = mp.Manager()
shared_dict = manager.dict()
events = manager.dict()

def addNewLog(new_log):
    if test == Helper.performance_test:
        log.addLog(new_log)

def sendingThread(conn, client_parameters_queue, e):
    while True:
        e.wait()
        while not client_parameters_queue.empty():
            client_parameters, r = client_parameters_queue.get()
            if client_parameters == None:
                return
            if client_parameters == Message.TRAIN:
                conn.send(Msg(header=Message.TRAIN))
            info={Message.ROUND: r, Message.SIZE: None, Message.SRC: None}
            connectionHelper.sendNewParametersToPython(conn, client_parameters, info)
        e.clear()

def connectToClients(ports):
    Listeners = []
    connections = dict()
    for client in range(nb_clients):
        address = (server_address, ports[client])
        listener = Listener(address)
        connections[client] = listener.accept()
        Listeners.append(listener)

    for client in range(nb_clients):
        events[client] = manager.Event()
        shared_dict[client] = manager.Queue()
        t = threading.Thread(target=sendingThread, args=(connections[client], shared_dict[client], events[client]))
        threads.append(t)
        t.start()
        
    print("Server connected to clients!")
    return Listeners, connections


def runTheRound(r, connections, recvd_params):
    t = datetime.now().strftime("%H:%M:%S:%f")
    # recvd_connections = [connections[s] for s in list(connections.keys()) if s in [k[0] for k in recvd_params.keys()]]
    recvd_connections_ids = [s for s in list(connections.keys()) if s in [k[0] for k in recvd_params.keys()]]
    addNewLog("round_{}_aggregation: {}\n".format(r, datetime.now().strftime("%H:%M:%S:%f")))
    if test == Helper.accuracy_test:
        ordered_params = {k: v for k, v in recvd_params.items() if k[0] in orders[r]}
        # recvd_params = dict(sorted(recvd_params.items(), key=lambda x: x[0][1])[:nb_clients - nb_byz])
        byz_vectors = attacker.generate_byzantine_vectors(list(ordered_params.values()), None)
        id = -1
        for v in byz_vectors:
            ordered_params[(id, t)] = v
            id -= 1
        print(ordered_params.keys())
        # ordered_params = dict(sorted(recvd_params.items(), key=lambda x: x[0][1])[:nb_clients])
    else:
        ordered_params = dict(sorted(recvd_params.items(), key=lambda x: x[0][1])[:nb_clients - nb_byz])
    # print(ordered_params.keys())
    addNewLog("round_{}_aggregation order: {}\n".format(r, [x[0] for x in ordered_params.keys()]))
    new_model_parameters = aggregator.aggregate(list(ordered_params.values()))

    sendNewParameters(recvd_connections_ids, connectionHelper.tensorToString(new_model_parameters), r)
    # t = threading.Thread(target=sendNewParameters, args=(recvd_connections, new_model_parameters, r))
    # threads.append(t)
    # t.start()
    addNewLog("round_{}_end: {}\n".format(r, datetime.now().strftime("%H:%M:%S:%f")))
    return new_model_parameters

def execute(connections):
    addNewLog("Starting: {}\n".format(datetime.now().strftime("%H:%M:%S:%f")))
    r = 1
    recvd_params = dict()
    recvd_size = dict()
    round_params = dict()
    addNewLog("round_{}_start: {}\n".format(r, datetime.now().strftime("%H:%M:%S:%f")))
    termination = 0
    while(r <= nb_rounds or termination < nb_clients):
        ready_to_read, _, _ = select.select(list(connections.values()), [], [])
        for sock in ready_to_read:
            msg = sock.recv()
            if msg.header == Message.TERMINATE:
                termination += 1
            if msg.header == Message.NEW_PARAMETERS:
                if int(msg.content[Message.ROUND]) == r:
                    t = datetime.now().strftime("%H:%M:%S:%f")
                    recvd_params[(msg.src_id, t)] = connectionHelper.stringToTensor(msg.content[Message.PARAMS])
                    recvd_size[(msg.src_id, t)] = msg.content[Message.SIZE]
                elif int(msg.content[Message.ROUND]) < r:
                    connectionHelper.sendNewParameters(sock, round_params[int(msg.content[Message.ROUND])], connectionHelper.PYTHON, info={Message.ROUND: msg.content[Message.ROUND], Message.SIZE: None, Message.SRC: None})
                    
            if (test == Helper.performance_test and len(list(recvd_params.values())) >= nb_clients - nb_byz) or (test == Helper.accuracy_test and len(list(recvd_params.values())) >= nb_clients):
            # if (test == Helper.performance_test and len(list(recvd_params.values())) >= nb_clients) or (test == Helper.accuracy_test and len(list(recvd_params.values())) >= nb_clients):
            # if len(list(recvd_params.values())) >= nb_clients - nb_byz:
                addNewLog("round_{}_received_params_{}: {}\n".format(r, str(nb_clients - nb_byz), datetime.now().strftime("%H:%M:%S:%f")))
                round_params[r] = runTheRound(r, connections, recvd_params)
                print("round {} finished".format(r))
                r += 1
                addNewLog("round_{}_start: {}\n".format(r, datetime.now().strftime("%H:%M:%S:%f")))
                recvd_params = dict()
                recvd_size = dict()

    addNewLog("end: {}\n".format(datetime.now().strftime("%H:%M:%S:%f")))
    sendNewParameters(list(connections.keys()), None, r)

def sendNewParameters(recvd_connections, new_model_parameters, r):
    random.shuffle(recvd_connections)
    for id in recvd_connections:
        shared_dict[id].put((new_model_parameters, r))
        events[id].set()
    # for conn in recvd_connections:
    #     connectionHelper.sendNewParameters(conn, new_model_parameters, connectionHelper.PYTHON, info={Message.ROUND: r, Message.SIZE: None, Message.SRC: None})

def sendTrainMessage(connections):
    for id in list(connections.keys()):
        shared_dict[id].put((Message.TRAIN, 0))
        events[id].set()

def terminate(connections, listeners):
    for conn in connections:
        conn.send(Msg(header=Message.ACK))
    for conn in connections:
        conn.close()
    for lis in listeners:
        lis.close()

def main():
    print("Server started! ... ")
    listeners, connections = connectToClients(ConnectionDistributer.generateFLPorts(server_port, nb_clients))
    sendTrainMessage(connections)
    execute(connections)
    for t in threads:
        t.join()
    terminate(list(connections.values()), listeners)
    print("Server terminated! ...")
    if test == Helper.performance_test:
        log.writeLogs()
if __name__ == "__main__":
    main()