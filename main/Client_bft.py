from Utils import Model, Helper, Message, connectionHelper, evaluator
import sys
import jpysocket
from torch import load

text_file = open("/localhome/shossein/DCL_semester_project/Consensus_res/Output.txt", "w")
## Define Client Class
class TraningClient:
    def __init__(self, client_id, dataset):
        self.client_id = client_id
        self.dataset = dataset
        self.net = Helper.to_device(Model.FederatedNet(), Helper.device)

    def get_dataset_size(self):
        return len(self.dataset)
    
    def handleTrainCmd(self, connection):
        self.net.fit(self.dataset)
        connection.send(jpysocket.jpyencode(str(self.get_dataset_size())))
        connectionHelper.sendNewParameters(connection, self.net.get_parameters(), connectionHelper.JAVA)

    def execute(self, connection):
        r = 1
        while True:
            msg = jpysocket.jpydecode(connection.recv(1024))
            if msg == Message.NEW_PARAMETERS:
                new_param = connectionHelper.getNewParameters(connection, connectionHelper.JAVA)
                self.net.apply_parameters(new_param)
                if self.client_id == 0:
                    evaluator.evaluateTheRound(new_param, r, text_file)
                r += 1
                print("Round Ended!")
                continue
            if msg == Message.TRAIN:
                self.handleTrainCmd(connection)
                continue
            if msg == Message.TERMINATE:
                connection.send(jpysocket.jpyencode("ACK"))
                return
        
def main():
    client_id = int(sys.argv[1])
    print("Client {} started! ... ".format(client_id))
    # training_client = TraningClient(client_id, load("F:/DCL/Semester Project 1/Codes/DCL_semester_project/main/Data/ClientsDatasets/" + str(client_id) + ".pt"))
    training_client = TraningClient(client_id, load("/localhome/shossein/DCL_semester_project/main/Data/ClientsDatasets/" + str(client_id) + ".pt"))
    connection = connectionHelper.connect(sys.argv[2], int(sys.argv[3]))
    training_client.execute(connection)
    connection.close()
    text_file.close()

    print("Client {} terminated! ...".format(client_id))


if __name__ == "__main__":
    main()