from Utils import Model, Helper, bft_Helper
from torch.multiprocessing import set_start_method
from torch import load, tensor, sum, stack
from Utils import Model, Helper
import sys
import jpysocket

try:
     set_start_method('spawn')
except RuntimeError:
    pass

train_dataset = load("F:/DCL/Semester Project 1/Codes/DCL_semester_project/Simple_FL/Data/trainDataset.pt")
test_dataset = load("F:/DCL/Semester Project 1/Codes/DCL_semester_project/Simple_FL/Data/testDataset.pt")
dev_dataset = load("F:/DCL/Semester Project 1/Codes/DCL_semester_project/Simple_FL/Data/devDataset.pt")
total_train_size = len(train_dataset)


def aggregateParams(params):
    return sum(stack(params), dim=0).tolist()

def handleNewParam(connection):
    connection.send(jpysocket.jpyencode("ACK"))
    datasetSize = int(jpysocket.jpydecode(connection.recv(1024)))
    return (datasetSize / total_train_size * tensor(bft_Helper.getNewParameters(connection)))

def execute(connection, global_net):
    params = []
    while True:
        msg = jpysocket.jpydecode(connection.recv(1024))
        if msg == "NEWPARAMS":
            params.append(handleNewParam(connection))
        if msg == "AGGREGATE":
            bft_Helper.sendNewParameters(connection, bytes(''.join([str(round(x, 4)) + "," for x in aggregateParams(params)]), 'utf-8'))
            params = []
        if msg == "TERMINATE":
            connection.send(jpysocket.jpyencode("ACK"))
            return

def main():
    print("server started! ... ")
    global_net = Helper.to_device(Model.FederatedNet(), Helper.device)
    connection = bft_Helper.connect(sys.argv[1], int(sys.argv[2]))
    execute(connection, global_net)
    connection.close()
    print("Server terminated! ...")


if __name__ == "__main__":
    main()