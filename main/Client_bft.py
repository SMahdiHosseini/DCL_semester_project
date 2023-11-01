from Utils import Model, Helper, Message, connectionHelper, evaluator
import sys
import jpysocket
from torch import load
import threading

#program input: nb_clients, client_id, server_address, server_port, nb_byz, aggregator_name
nb_clients = int(sys.argv[1])
client_id = int(sys.argv[2])
server_address = sys.argv[3]
server_port = int(sys.argv[4])
nb_byz = int(sys.argv[5])
aggregator_name = sys.argv[6]

## Define Client Class
class TraningClient:
    def __init__(self, client_id, dataset):
        self.client_id = client_id
        self.dataset = dataset
        self.net = Helper.to_device(Model.FederatedNet(), Helper.device)
        if client_id == 0:
            self.text_file = open("/localhome/shossein/DCL_semester_project/Consensus_res/ncl_" + str(nb_clients) + "_agg_" + aggregator_name + "_nbyz_" + str(nb_byz) + ".txt", "w")

    def get_dataset_size(self):
        return len(self.dataset)
    
    def handleTrainCmd(self, connection):
        self.net.fit(self.dataset)
        connection.send(jpysocket.jpyencode(str(self.get_dataset_size())))
        connectionHelper.sendNewParameters(connection, self.net.get_parameters(), connectionHelper.JAVA)

    def execute(self, connection):
        r = 1
        my_thread = []
        while True:
            msg = jpysocket.jpydecode(connection.recv(1024))
            if msg == Message.NEW_PARAMETERS:
                new_param = connectionHelper.getNewParameters(connection, connectionHelper.JAVA)
                self.net.apply_parameters(new_param)
                if self.client_id == 0:
                    new_thread = threading.Thread(target=evaluation, args=(self.net.get_parameters(), r, self.text_file))
                    new_thread.start()
                    my_thread.append(new_thread)
                r += 1
                print("Round Ended!")
                continue
            if msg == Message.TRAIN:
                self.handleTrainCmd(connection)
                continue
            if msg == Message.TERMINATE:
                for t in my_thread:
                    t.join()
                connection.send(jpysocket.jpyencode("ACK"))
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