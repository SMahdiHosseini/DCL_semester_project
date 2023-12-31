from torch import load
import torch
from Utils import Helper, Model
import os

random_seed = 10
torch.manual_seed(random_seed)
torch.cuda.manual_seed(random_seed)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False

def evaluateTheRound(params, r, text_file):
    # train_dataset = load("F:/DCL/Semester Project 1/Codes/DCL_semester_project/main/Data/trainDataset.pt")
    # test_dataset = load("F:/DCL/Semester Project 1/Codes/DCL_semester_project/main/Data/testDataset.pt")
    # dev_dataset = load("F:/DCL/Semester Project 1/Codes/DCL_semester_project/main/Data/devDataset.pt")
    s = os.getcwd()
    sub_str = "DCL_semester_project"
    dTest = s[:s.index(sub_str) + len(sub_str)] + "/main/Data/testDataset.pt"
    # train_dataset = load("Data/trainDataset.pt")
    test_dataset = load(dTest)
    # dev_dataset = load("Data/devDataset.pt")

    global_net = Helper.to_device(Model.FederatedNet(test_dataset), Helper.device)
    global_net.apply_parameters(params)
    # train_loss, train_acc = global_net.evaluate(train_dataset)
    # dev_loss, dev_acc = global_net.evaluate(dev_dataset)
    test_loss, test_acc = global_net.evaluate(test_dataset)
    # text_file.write('After round {}, train_loss = {}, train_acc = {}, dev_loss = {}, dev_acc = {}, test_loss = {}, test_acc = {}\n'.format(r, round(train_loss, 4), round(train_acc, 4), round(dev_loss, 4), round(dev_acc, 4), round(test_loss, 4), round(test_acc, 4)))
    text_file.write('After round {}, test_loss = {}, test_acc = {}\n'.format(r, round(test_loss, 4), round(test_acc, 4)))

    