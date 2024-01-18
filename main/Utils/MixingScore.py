import numpy as np
from scipy import linalg as la
import zlib
from scipy.stats import chisquare

def entropyMixingScore(participationMatrix):
    R = participationMatrix*(la.logm(participationMatrix)/la.logm(np.matrix([[2]])))
    S = -np.matrix.trace(R)
    return(S)

def CompressionMixingScore(participationMatrix):
    bytes = participationMatrix.tobytes()
    compressedBytes = zlib.compress(bytes)
    # compressionRatio = len(bytes)/len(compressedBytes)
    return len(compressedBytes)

def chisquareMixingScore(participationFrequency, expectedFrequency):
    return chisquare(participationFrequency, expectedFrequency).pvalue

def transitionMixingScore(participationMatrix):
    score = 0
    for i in range(1, len(participationMatrix)):
        for j in range(len(participationMatrix[i])):
            if participationMatrix[i][j] == 1 and participationMatrix[i-1][j] == 1:
                score += 1
            if participationMatrix[i][j] == 1 and participationMatrix[i-1][j] == 0:
                score += 2
    return score

def readOrders(client_id, nb_clients, nb_byz, nb_rounds, aggreagator, attack, senario, experiment):
    if senario == 'fl':
        logFile = "../../FL_res/" + aggreagator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance_" + str(experiment) + "/server.txt"
    if senario == 'p2p':
        logFile = "../../Gossip_res/" + aggreagator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance_" + str(experiment) + "/" + str(client_id) + ".txt"
    if senario == 'con':
        logFile = "../../Consensus_res/" + aggreagator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance_" + str(experiment) + "/recevdParamIds.txt"

    input_file = open(logFile, "r")
    lines = dict()
    for line in input_file:
        line = line.strip()
        key_value = line.split(":")
        if (senario == 'fl' or senario == 'p2p') and  "order" in key_value[0]:
            lines[key_value[0]] = key_value[1]
        if senario == 'con':
            lines[key_value[0]] = key_value[1]

    participationDict = dict()
    participationMatrix = np.zeros((nb_rounds, nb_clients))

    for i in range(nb_clients):
        participationDict[i] = 0

    for r in range(1, nb_rounds + 1):
        if senario == 'fl' or senario == 'p2p':
            temp = [int(i) for i in lines["round_{}_aggregation order".format(r)][2:-1].split(',')]
        else:
            temp = [int(i) for i in lines["Round {}".format(r)][:-1].split(',')]
        for t in temp:
            participationDict[t] += 1
            participationMatrix[r-1][t] += 1

    return participationDict, participationMatrix

flParticipationDict, flParticipationMatrix = readOrders(0, 10, 3, 250, 'trmean', 'SF', 'fl', 1)
ConParticipationDict, conParticipationMatrix = readOrders(0, 10, 3, 250, 'trmean', 'SF', 'con', 1)
f_exp = [175 for i in range(10)]

# print(entropyMixingScore(participationMatrix))

print("FL CompressionMixingScore: ", CompressionMixingScore(flParticipationMatrix))
print("Consensus CompressionMixingScore: ", CompressionMixingScore(conParticipationMatrix))

print("FL ChisquareMixingScore: ", chisquareMixingScore(list(flParticipationDict.values()), f_exp))
print("Consensus ChisquareMixingScore: ", chisquareMixingScore(list(ConParticipationDict.values()), f_exp))

print("FL TransitionMixingScore: ", transitionMixingScore(flParticipationMatrix))
print("Consensus TransitionMixingScore: ", transitionMixingScore(conParticipationMatrix))

