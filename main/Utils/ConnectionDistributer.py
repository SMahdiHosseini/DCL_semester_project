from Utils import Helper
import random

random.seed(10)

# adjMat = [[(i - 1) % Helper.nb_clients, (i + 1) % Helper.nb_clients] for i in range(Helper.nb_clients)]
# adjMat = [[(i + 1) % Helper.nb_clients] for i in range(Helper.nb_clients)]
adjMat = [[] for i in range(Helper.nb_clients)]
for i in range(Helper.nb_clients):
    s = []
    for j in range(Helper.nb_clients):
        if i != j:
            s.append(j)
    adjMat[i] = s

# portsPool = [Helper.server_port + i for i in random.sample(range(0, 100), Helper.nb_clients)]

numOfports = 0
for i in range(Helper.nb_clients):
    numOfports += len(adjMat[i])
numOfports = int(numOfports / 2 )

portsPool = [Helper.server_port + i for i in random.sample(range(0, 100), numOfports)]

ports = dict()
for i in range(Helper.nb_clients):
    ports[i] = dict()
    for j in adjMat[i]:
        ports[i][j] = 0

k = 0
for i in range(Helper.nb_clients):
    for j in adjMat[i]:
        if ports[j][i] == 0:
            ports[i][j] = portsPool[k]
            ports[j][i] = portsPool[k]
            k +=1

# print(adjMat)
# print(ports)
# print(numOfports)
# print(portsPool)