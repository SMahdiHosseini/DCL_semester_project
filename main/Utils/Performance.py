import sys
from datetime import datetime
import Log
#program input: nb_clients, nb_byz, nb_rounds, aggregator, senario
nb_clients = int(sys.argv[1])
nb_byz = int(sys.argv[2])
nb_rounds = int(sys.argv[3])
aggregator = sys.argv[4]
senario = sys.argv[5]

def readlines(input_file_name):
    input_file = open(input_file_name, "r")
    lines = dict()
    for line in input_file:
        line = line.strip()
        key_value = line.split(":")
        key = key_value[0]
        t = datetime(year=2023, month=2, day=1, hour=int(key_value[1]), minute=int(key_value[2]), second=int(key_value[3]), microsecond=int(key_value[4]))
        lines[key] = t
    return lines

def sumOfTimes(times):
    result = None
    for i in range(len(times)):
        if i == 0:
            result = times[i]
        else:
            result += times[i]
    return result

def analyseFLPerformance():
    log = Log.Log("/localhome/shossein/DCL_semester_project/FL_res/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance/performance.txt")
    lines_server = readlines("/localhome/shossein/DCL_semester_project/FL_res/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance/server.txt")
    lines_clients = []
    for i in range(nb_clients):
        lines_clients.append(readlines("/localhome/shossein/DCL_semester_project/FL_res/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance/" + str(i)  + ".txt"))
    total_average = 0
    total = 0
    for r in range(1, nb_rounds + 1):
        #clients
        rounds_times = []
        for c in range(nb_clients):
            temp = lines_clients[c]['round_{}_end'.format(r)] - lines_clients[c]['round_{}_start'.format(r)]
            rounds_times.append(temp)
        avg = sumOfTimes(rounds_times) / nb_clients
        #server
        t = lines_server['round_{}_received_params'.format(r)] - lines_server['round_{}_start'.format(r)] + lines_server['round_{}_end'.format(r)] - lines_server['round_{}_aggregation'.format(r)]
        if r == 1:
            total = t
            total_average = avg
        else:
            total += t
            total_average += avg
        log.addLog("round {}\n\tserver time: {}\n\tclients average time: {}\n".format(r, t, avg))
    log.addLog("total \n\tserver_time: {}\n\tclients average total time: {}".format(total, total_average))
    log.writeLogs()

def analyseP2PPerformance():
    log = Log.Log("/localhome/shossein/DCL_semester_project/Gossip_res/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance/performance.txt")
    lines_clients = []
    for i in range(nb_clients):
        lines_clients.append(readlines("/localhome/shossein/DCL_semester_project/Gossip_res/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance/" + str(i)  + ".txt"))
    total_average = 0
    for r in range(1, nb_rounds + 1):
        #clients
        rounds_times = []
        for c in range(nb_clients):
            temp = lines_clients[c]['round_{}_received_params'.format(r)] - lines_clients[c]['round_{}_start'.format(r)] + lines_clients[c]['round_{}_end'.format(r)] - lines_clients[c]['round_{}_aggregation'.format(r)]
            rounds_times.append(temp)
        avg = sumOfTimes(rounds_times) / nb_clients
        if r == 1:
            total_average = avg
        else:
            total_average += avg
        log.addLog("round {}\n\tclients average time: {}\n".format(r, avg))
    log.addLog("total \n\tclients average total time: {}".format(total_average))
    log.writeLogs()

def analyseConPerformance():
    nb_replicas = 4
    log = Log.Log("/localhome/shossein/DCL_semester_project/Consensus_res/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance/performance.txt")
    lines_replicas = []
    lines_clients = []
    for i in range(nb_clients):
        lines_clients.append(readlines("/localhome/shossein/DCL_semester_project/Consensus_res/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance/" + str(i)  + ".txt"))
    for i in range(nb_replicas):
        lines_replicas.append(readlines("/localhome/shossein/DCL_semester_project/Consensus_res/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance/server_" + str(i)  + ".txt"))

    total_average_clients = 0
    total_average_replicas = 0
    for r in range(1, nb_rounds + 1):
        #clients
        rounds_times = []
        for c in range(nb_clients):
            temp = lines_clients[c]['round_{}_end'.format(r)] - lines_clients[c]['round_{}_start'.format(r)]
            rounds_times.append(temp)
        avg_c = sumOfTimes(rounds_times) / nb_clients
        #replicas
        rounds_times = []
        for s in range(nb_replicas):
            temp = lines_replicas[s]['round_{}_received_params'.format(r)] - lines_replicas[s]['round_{}_start'.format(r)] + lines_replicas[s]['round_{}_end'.format(r)] - lines_replicas[s]['round_{}_aggregation'.format(r)]
            rounds_times.append(temp)
        avg_s = sumOfTimes(rounds_times) / nb_clients

        if r == 1:
            total_average_replicas = avg_s
            total_average_clients = avg_c
        else:
            total_average_replicas += avg_s
            total_average_clients += avg_c
        log.addLog("round {}\n\treplicas average time: {}\n\tclients average time: {}\n".format(r, avg_s, avg_c))
    log.addLog("total \n\treplicas average total time: {}\n\tclients average total time: {}".format(total_average_replicas, total_average_clients))
    log.writeLogs()

if senario == "fl":
    analyseFLPerformance()
if senario == "p2p":
    analyseP2PPerformance()
if senario == "con":
    analyseConPerformance()