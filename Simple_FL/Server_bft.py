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

# train_dataset = load("F:/DCL/Semester Project 1/Codes/DCL_semester_project/Simple_FL/Data/trainDataset.pt")
# test_dataset = load("F:/DCL/Semester Project 1/Codes/DCL_semester_project/Simple_FL/Data/testDataset.pt")
# dev_dataset = load("F:/DCL/Semester Project 1/Codes/DCL_semester_project/Simple_FL/Data/devDataset.pt")
# text_file = open("F:/DCL/Semester Project 1/Codes/DCL_semester_project/Consensus_res/Output.txt", "w")
train_dataset = load("/localhome/shossein/DCL_semester_project/Simple_FL/Data/trainDataset.pt")
test_dataset = load("/localhome/shossein/DCL_semester_project/Simple_FL/Data/testDataset.pt")
dev_dataset = load("/localhome/shossein/DCL_semester_project/Simple_FL/Data/devDataset.pt")
text_file = open("/localhome/shossein/DCL_semester_project/Consensus_res/Output.txt", "w")
total_train_size = len(train_dataset)

def aggregateParams(params):
    return sum(stack(params), dim=0)

def handleNewParam(connection):
    connection.send(jpysocket.jpyencode("ACK"))
    datasetSize = int(jpysocket.jpydecode(connection.recv(1024)))
    return (datasetSize / total_train_size * tensor(bft_Helper.getNewParameters(connection)))

def evaluateTheRound(global_net, history, r):
    train_loss, train_acc = global_net.evaluate(train_dataset)
    dev_loss, dev_acc = global_net.evaluate(dev_dataset)
    test_loss, test_acc = global_net.evaluate(test_dataset)
    text_file.write('After round {}, train_loss = {}, train_acc = {}, dev_loss = {}, dev_acc = {}, test_loss = {}, test_acc = {}\n'.format(r, round(train_loss, 4), round(train_acc, 4), round(dev_loss, 4), round(dev_acc, 4), round(test_loss, 4), round(test_acc, 4)))
    history.append((train_loss, dev_loss))

def finalizeTheRound(params, global_net, history, r, connection):
    newAggParam = aggregateParams(params)
    global_net.apply_parameters(newAggParam)
    evaluateTheRound(global_net, history, r)
    bft_Helper.sendNewParameters(connection, bytes(''.join([str(round(x, 4)) + "," for x in newAggParam.tolist()]), 'utf-8'))

def execute(connection):
    global_net = Helper.to_device(Model.FederatedNet(), Helper.device)
    params = []
    history = []
    r = 1
    while True:
        msg = jpysocket.jpydecode(connection.recv(1024))
        if msg == "NEWPARAMS":
            params.append(handleNewParam(connection))
            continue
        if msg == "AGGREGATE":
            finalizeTheRound(params, global_net, history, r, connection)
            r += 1
            params = []
            continue
        if msg == "TERMINATE":
            connection.send(jpysocket.jpyencode("ACK"))
            return

def main():
    print("server started! ... ")
    connection = bft_Helper.connect(sys.argv[1], int(sys.argv[2]))
    execute(connection)
    connection.close()
    text_file.close()
    print("Server terminated! ...")


if __name__ == "__main__":
    main()