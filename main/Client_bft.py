from Utils import Model, Helper, Message, connectionHelper, evaluator, Log
import sys
import jpysocket
from torch import load
import threading
from datetime import datetime

#program input: nb_clients, client_id, server_address, server_port, nb_byz, aggregator_name, attack_name, test
nb_clients = int(sys.argv[1])
client_id = int(sys.argv[2])
server_address = sys.argv[3]
server_port = int(sys.argv[4])
nb_byz = int(sys.argv[5])
aggregator_name = sys.argv[6]
attack_name = sys.argv[7]
test = sys.argv[8]

log = Log.Log("/localhome/shossein/DCL_semester_project/Consensus_res/" + aggregator_name + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance/" + str(client_id) + ".txt")

def addNewLog(new_log):
    if test == Helper.performance_test:
        log.addLog(new_log)

## Define Client Class
class TraningClient:
    def __init__(self, client_id, dataset):
        self.client_id = client_id
        self.dataset = dataset
        self.net = Helper.to_device(Model.FederatedNet(), Helper.device)
        if test == Helper.accuracy_test:
            self.text_file = open("/localhome/shossein/DCL_semester_project/Consensus_res/" + aggregator_name + "/ncl_" + str(nb_clients + nb_byz)  + "/nbyz_" + str(nb_byz) + "/Accuracy/"  + attack_name + "/" + str(client_id) + ".txt", "w")

    def get_dataset_size(self):
        return len(self.dataset)
    
    def handleTrainCmd(self, connection):
        self.net.fit(self.dataset)
        connection.send(jpysocket.jpyencode(str(self.get_dataset_size())))
        connectionHelper.sendNewParameters(connection, self.net.get_parameters(), connectionHelper.JAVA)

    def execute(self, connection):
        addNewLog("Starting: {}\n".format(datetime.now().strftime("%H:%M:%S:%f")))
        r = 1
        # my_thread = []
        while True:
            msg = jpysocket.jpydecode(connection.recv(1024))
            if msg == Message.NEW_PARAMETERS:
                new_param = connectionHelper.getNewParameters(connection, connectionHelper.JAVA)
                self.net.apply_parameters(new_param)
                addNewLog("round_{}_end: {}\n".format(r, datetime.now().strftime("%H:%M:%S:%f")))
                if test == Helper.accuracy_test:
                    # new_thread = threading.Thread(target=evaluation, args=(self.net.get_parameters(), r, self.text_file))
                    # new_thread.start()
                    # my_thread.append(new_thread)
                    evaluation(self.net.get_parameters(), r, self.text_file)
                r += 1
                print("Round Ended!")
                continue
            if msg == Message.TRAIN:
                addNewLog("round_{}_start: {}\n".format(r, datetime.now().strftime("%H:%M:%S:%f")))
                self.handleTrainCmd(connection)
                continue
            if msg == Message.TERMINATE:
                # for t in my_thread:
                #     t.join()
                connection.send(jpysocket.jpyencode("ACK"))
                addNewLog("end: {}\n".format(datetime.now().strftime("%H:%M:%S:%f")))
                if test == Helper.performance_test:
                    log.writeLogs()

                return
            
def evaluation(params, r, text_file):
    evaluator.evaluateTheRound(params, r, text_file)        

def main():
    print("Client {} started! ... ".format(client_id))
    # training_client = TraningClient(client_id, load("F:/DCL/Semester Project 1/Codes/DCL_semester_project/main/Data/ClientsDatasets/" + str(client_id) + ".pt"))
    training_client = TraningClient(client_id, load("/localhome/shossein/DCL_semester_project/main/Data/ClientsDatasets/" + str(client_id) + ".pt"))
    connection = connectionHelper.connect(server_address, server_port)
    training_client.execute(connection)
    connection.close()
    training_client.text_file.close()

    print("Client {} terminated! ...".format(client_id))

if __name__ == "__main__":
    main()