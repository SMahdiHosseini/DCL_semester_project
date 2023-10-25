from torch import load
from Utils import Helper, Model


def evaluateTheRound(params, r, text_file):
    # train_dataset = load("F:/DCL/Semester Project 1/Codes/DCL_semester_project/Simple_FL/Data/trainDataset.pt")
    # test_dataset = load("F:/DCL/Semester Project 1/Codes/DCL_semester_project/Simple_FL/Data/testDataset.pt")
    # dev_dataset = load("F:/DCL/Semester Project 1/Codes/DCL_semester_project/Simple_FL/Data/devDataset.pt")
    train_dataset = load("/localhome/shossein/DCL_semester_project/Simple_FL/Data/trainDataset.pt")
    test_dataset = load("/localhome/shossein/DCL_semester_project/Simple_FL/Data/testDataset.pt")
    dev_dataset = load("/localhome/shossein/DCL_semester_project/Simple_FL/Data/devDataset.pt")

    global_net = Helper.to_device(Model.FederatedNet(), Helper.device)
    global_net.apply_parameters(params)
    train_loss, train_acc = global_net.evaluate(train_dataset)
    dev_loss, dev_acc = global_net.evaluate(dev_dataset)
    test_loss, test_acc = global_net.evaluate(test_dataset)
    text_file.write('After round {}, train_loss = {}, train_acc = {}, dev_loss = {}, dev_acc = {}, test_loss = {}, test_acc = {}\n'.format(r, round(train_loss, 4), round(train_acc, 4), round(dev_loss, 4), round(dev_acc, 4), round(test_loss, 4), round(test_acc, 4)))

    