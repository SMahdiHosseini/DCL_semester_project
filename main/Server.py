from Utils import Helper, Message, connectionHelper, ConnectionDistributer, evaluator
from Utils.aggregator import RobustAggregator
from Utils.attacks import ByzantineAttack
from multiprocessing.connection import Listener
import sys
from datetime import datetime
import threading

#program input: nb_clients, server_address, server_port, nb_byz, nb_rounds aggregator_name, attack_name
nb_clients = int(sys.argv[1])
server_address = sys.argv[2]
server_port = int(sys.argv[3])
nb_byz = int(sys.argv[4])
nb_rounds = int(sys.argv[5])
aggregator_name = sys.argv[6]
attack_name = sys.argv[7]
aggregator = RobustAggregator('nnm', aggregator_name, 1, nb_byz, Helper.device)
attacker = ByzantineAttack(attack_name, nb_byz)
text_file = open("/localhome/shossein/DCL_semester_project/FL_res/ncl_" + str(nb_clients) + "_agg_" + aggregator_name + "_nbyz_" + str(nb_byz) + "_attcak_" + attack_name + ".txt", "w")

def evaluation(params, r, text_file):
    evaluator.evaluateTheRound(params, r, text_file)

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

def runTheRound(r, connections):
    t = datetime.now().strftime("%H:%M:%S:%f")
    recvd_params, recvd_size = connectionHelper.getAllParams(connections, nb_clients, None, None, None, r)
    ordered_params = dict(sorted(recvd_params.items(), key=lambda x: x[0][1])[:nb_clients - 2 * nb_byz])
    byz_vectors = attacker.generate_byzantine_vectors(list(ordered_params.values()), None)
    id = -1
    for v in byz_vectors:
        ordered_params[(id, t)] = v
        id -= 1
    print(ordered_params.keys())
    new_model_parameters = aggregator.aggregate(list(ordered_params.values()))
    
    my_thread = threading.Thread(target=evaluation, args=(new_model_parameters, r, text_file))
    my_thread.start()
    
    for conn in connections:
        connectionHelper.sendNewParameters(conn, new_model_parameters, connectionHelper.PYTHON, info={Message.ROUND: r, Message.SIZE: None, Message.SRC: None})

def execute(connections):
    for r in range(1, nb_rounds + 1):
        runTheRound(r, connections)

def terminate(connections, listeners):
    for conn in connections:
        conn.close()
    for lis in listeners:
        lis.close()

def main():
    print("Server started! ... ")
    listeners, connections = connectToClients(ConnectionDistributer.generateFLPorts(server_port, nb_clients))
    execute(list(connections.values()))
    terminate(list(connections.values()), listeners)
    print("Server terminated! ...")

if __name__ == "__main__":
    main()