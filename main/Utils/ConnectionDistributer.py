import random

random.seed(10)

def generateFLPorts(server_port, nb_clients):
    return [server_port + i for i in random.sample(range(0, 100), nb_clients)]

def generateGossipPorts(server_port, nb_clients):
    adjMat = [[] for i in range(nb_clients)]
    for i in range(nb_clients):
        s = []
        for j in range(nb_clients):
            if i != j:
                s.append(j)
        adjMat[i] = s

    numOfports = 0
    for i in range(nb_clients):
        numOfports += len(adjMat[i])
    numOfports = int(numOfports / 2 )

    portsPool = [server_port + i for i in random.sample(range(0, 100), numOfports)]

    ports = dict()
    for i in range(nb_clients):
        ports[i] = dict()
        for j in adjMat[i]:
            ports[i][j] = 0

    k = 0
    for i in range(nb_clients):
        for j in adjMat[i]:
            if ports[j][i] == 0:
                ports[i][j] = portsPool[k]
                ports[j][i] = portsPool[k]
                k +=1
    return ports, adjMat