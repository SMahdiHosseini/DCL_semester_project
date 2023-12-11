# import random
# from Utils import connectionHelper, Helper, aggregator, attacks, Model, evaluator
# import torch 
# # from torch.utils.data import Dataset, Subset, DataLoader
# import torchvision.transforms as transforms
# from torchvision.datasets import MNIST
import multiprocessing as mp
import time
import threading
threads= []
def subProcess(q , i):
    while True:
        if q.empty():
            continue
        else:
            a, b = q.get()
            if a == 0:
                print("GOT HERE")
                return
            print(f"Process {i}:  {a, b}")


manager = mp.Manager()
shared_dict = manager.dict()
for i in range(4):
    shared_dict[i] = manager.Queue()

print("shared_dict")

for i in range(4):
    t = threading.Thread(target=subProcess, args=(shared_dict[i], i))
    t.start()
    threads.append(t)

i = 1
terminate = False
while terminate == False:
    for j in range(4):
        shared_dict[j].put((i, i+1))
    if i == 10:
        for j in range(4):
            shared_dict[j].put((0, 0))
        terminate = True
    else:
        i += 1
    time.sleep(1)

for t in threads:
    t.join()