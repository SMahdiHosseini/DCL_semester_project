import sys, math
from datetime import datetime
import Log
import matplotlib.pyplot as plt
from pylab import plot, show, savefig, xlim, figure, ylim, legend, boxplot, setp, axes
import seaborn as sns
import pandas as pd
import numpy as np

plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = (40, 20)
plt.rcParams.update({
    "lines.color": "black",
    "patch.edgecolor": "black",
    "text.color": "black",
    "axes.facecolor": "white",
    "axes.edgecolor": "black",
    "axes.labelcolor": "black",
    "xtick.color": "black",
    "ytick.color": "black",
    "grid.color": "white",
    "figure.facecolor": "white",
    "figure.edgecolor": "white",
    "savefig.facecolor": "white",
    "savefig.edgecolor": "white",
    "font.size": 30,
    "xtick.labelsize":30,
    "ytick.labelsize":30,
    "lines.linewidth":1.})

#program input: nb_clients, nb_byz, nb_rounds
nb_clients = int(sys.argv[1])
nb_byz = int(sys.argv[2])
nb_rounds = int(sys.argv[3])
nb_experiments = 3
experiment = 1
# heterogeneity = "Homogeneous"
heterogeneity = "Heterogeneous"

attacks = ["SF"]
aggregators = ["trmean"]

colors = ['blue', 'red', 'green', 'brown', 'olive', 'cyan', 'lime', 'royalblue', 'pink']

def readlines(input_file_name):
    input_file = open(input_file_name, "r")
    lines = dict()
    for line in input_file:
        line = line.strip()
        key_value = line.split(":")
        if "order" in key_value[0]:
            continue
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

def accuracy(input_file_name):
    input_file = open(input_file_name, "r")
    lines = dict()
    result = []
    i = 0
    for line in input_file:
        line = line.strip()
        key_value = line.split("=")
        if i != 0:
            result.append(round(float(key_value[-1]), 4))
        i += 1
    return result

def analyseAccuracy(aggregator, attack, nb_clients, nb_byz, res, senario):
    if senario == 'fl':
        senario = "FL_res"
    if senario == 'p2p':
        senario = 'Gossip_res'
    if senario == 'con':
        # senario = 'Consensus_res'
        senario = "FL_res"

    exps = []
    for exp in range(1, nb_experiments + 1):
        accs = []
        for i in range(nb_clients - nb_byz):
            accs.append(accuracy("../../" + senario +"/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Accuracy_" + str(exp) + "/" + heterogeneity + "/" + attack + "/" + str(i) + ".txt"))
        exps.append([round(sum(sub_list) / len(sub_list), 4) for sub_list in zip(*accs)])

    res[aggregator][attack] = [list(sub_list) for sub_list in list(zip(*exps))]

def analysePerformance(aggregator, nb_clients, nb_byz, res, senario):
    if senario == 'fl':
        senario = "FL_res"
    if senario == 'p2p':
        senario = 'Gossip_res'
    if senario == 'con':
        senario = 'Consensus_res'

    res[aggregator]['time'] = []
    res[aggregator]['end_time'] = []

    for exp in range(1, nb_experiments + 1):
        log = Log.Log("../../" + senario + "/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance_" + str(exp) + "/performance.txt")
        
        lines_clients = []
        for i in range(nb_clients):
            lines_clients.append(readlines("../../" + senario + "/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance_" + str(exp) + "/" + str(i)  + ".txt"))
        total_average = 0
        times = dict()
        end_times = dict()
        for r in range(2, nb_rounds + 1):
            #clients
            rounds_times = []
            end_rounds_times = []
            for c in range(nb_clients):
                temp = lines_clients[c]['round_{}_end'.format(r)] - lines_clients[c]['round_{}_start'.format(r)]
                # temp = lines_clients[c]['round_{}_model_shared'.format(r)] - lines_clients[c]['round_{}_model_trained'.format(r)]
                # temp = lines_clients[c]['round_{}_model_trained'.format(r)] - lines_clients[c]['round_{}_start'.format(r)]
                # temp = lines_clients[c]['round_{}_end'.format(r)] - lines_clients[c]['round_{}_model_shared'.format(r)]
                rounds_times.append(temp.total_seconds())
                end_rounds_times.append((lines_clients[c]['round_{}_end'.format(r)] - lines_clients[c]['round_2_start'.format(r)]).total_seconds())
            avg = sumOfTimes(rounds_times) / nb_clients
            if r == 2:
                total_average = avg
            else:
                total_average += avg
            log.addLog("round {}\n\tclients average time: {}\n".format(r, avg))
            
            times[r] = rounds_times
            end_times[r] = end_rounds_times
        log.addLog("total \n\tclients average total time: {}".format(total_average))
        log.writeLogs()

        res[aggregator]['time'].append(times)
        res[aggregator]['end_time'].append(end_times)

def setBoxColors_i(bp, num):
    for i in range(num):        
        setp(bp['boxes'][i], color=colors[i])
        setp(bp['caps'][2 * i], color=colors[i])
        setp(bp['caps'][2 * i + 1], color=colors[i])
        setp(bp['whiskers'][2 * i], color=colors[i])
        setp(bp['whiskers'][2 * i + 1], color=colors[i])
        setp(bp['medians'][i], color=colors[i])

def boxplots_i(boxes, num, labels, boxes_tags, x_label, y_label, 
                          y_lim, filename, option=False, value_1=0, value_2=0, title=""):
    plt.rcParams['figure.figsize'] = (60, 20)
    ax = axes()
    positions = 1
    xticklabels = []
    for i in range(len(labels)):
        bp = boxplot([boxes[k][i] for k in range(num)], positions = [positions + k for k in range(num)], widths = 0.6, patch_artist=True, showmeans=True, meanline=True, meanprops={'color':'white', 'linewidth':2})
        setBoxColors_i(bp, num)
        positions += (num + 1)
        for j in range(num):
            if j == math.floor(num / 2):
                xticklabels.append(str(labels[i]))
            else:
                xticklabels.append(" ")

    xlim(0, positions + 1)
    ylim(- y_lim * 0.008, y_lim)
    # ylim(0.4, y_lim)
    ax.set_xticklabels(xticklabels, fontsize=60)

    
    h = [None for i in range(num)]
    for i in range(num):
        h[i], = plot([1,1], colors[i])
    
    legend((h[i] for i in range(num)),(boxes_tags[i] for i in range(num)), fontsize=40)
    
    for i in range(num):
        h[i].set_visible(False)
        
    ax.set_title(title, fontsize=40)
    ax.set_xlabel(x_label, fontsize=60)
    ax.set_ylabel(y_label, fontsize=60)
    
    ax.yaxis.set_tick_params(labelsize=40)
    
    if option :
        plt.axhline(y = value_1, color = 'gray', linestyle = 'dotted')
        plt.axhline(y = value_2, color = 'gray', linestyle = 'dotted')
        
    # plt.text(7, y_lim * 0.8, formula, fontsize=60)
    plt.savefig(filename)
    plt.close()
    
def accuracy_attack_plot(res, label, nb_clients, nb_byz):
    for agg in aggregators:
        fig, ax = plt.subplots()
        for att in attacks:
            ax.errorbar(x=range(1, nb_rounds + 1), y=[np.mean(t) for t in res[agg][att]], yerr=[np.std(t) for t in res[agg][att]], fmt='o')
        ax.set_xlabel('rounds')
        ax.set_ylabel('accuracy')
        ax.legend()
        ax.set_title("n = " + str(nb_clients) + ", n byz = " + str(nb_byz) + "\naggregator: " + agg)
        # plt.xticks(range(nb_rounds + 1))
        plt.savefig("../../Plots/" + agg + "/" + label + "_" + str(nb_clients) + "_"  + str(nb_byz) + "_" + heterogeneity + ".png", bbox_inches='tight')
        plt.close()

def find_fastest_slowest(senario, aggregator):
    if senario == 'fl':
        senario = "FL_res"
    if senario == 'p2p':
        senario = 'Gossip_res'
    if senario == 'con':
        senario = 'Consensus_res'
    
    clients_times = dict()
    lines_clients = dict()
    for i in range(nb_clients):
        clients_times[i] = []
        lines_clients[i] = readlines("../../" + senario + "/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance_" + str(experiment) + "/" + str(i)  + ".txt")
        
    for r in range(2, nb_rounds + 1):
        for i in range(nb_clients):
            clients_times[i].append((lines_clients[i]['round_{}_end'.format(r)] - lines_clients[i]['round_{}_start'.format(r)]).total_seconds())
            
    total_times = {key: sum(value) for key, value in clients_times.items()}
    slowest_key = max(total_times, key=total_times.get)
    fastest_key = min(total_times, key=total_times.get)

    return clients_times[slowest_key], clients_times[fastest_key]

def violin_plot(fl, p2p, con):
    all_times = dict()
    all_times['fl'] = dict()
    all_times['p2p'] = dict()
    all_times['con'] = dict()
    for agg in aggregators:
        # all_times['fl'][agg] = [value for values in fl[agg]['time'].values() for value in values]
        # all_times['p2p'][agg] = [value for values in p2p[agg]['time'].values() for value in values]
        # all_times['con'][agg] = [value for values in con[agg]['time'].values() for value in values]
        all_times['fl'][agg] = [value for item in fl[agg]['time'] for values in item.values() for value in values]
        all_times['p2p'][agg] = [value for item in p2p[agg]['time'] for values in item.values() for value in values]
        all_times['con'][agg] = [value for item in con[agg]['time'] for values in item.values() for value in values]

    df = pd.DataFrame(columns = ['senario', 'trmean'])
    for key, value in all_times.items():
        times_df = pd.DataFrame({'senario': key, 'trmean': value['trmean']})
        df = pd.concat([df, times_df], ignore_index=True)
    
    df = pd.melt(frame = df, id_vars = 'senario', value_vars = ['trmean'],var_name = 'aggregator', value_name = 'time')
    df['time'] = df['time'].astype(float)
    # print(df)

    ax = sns.violinplot(data = df,x = 'aggregator', y = 'time', hue='senario', fill=False, linewidth=5)
    # ax.axhline(np.median(all_times['fl']['trmean']), color='blue', linewidth=1)
    # ax.axhline(np.median(all_times['p2p']['trmean']), color='red', linewidth=1)
    # ax.axhline(np.median(all_times['con']['trmean']), color='green', linewidth=1)
    ax.set_ylabel('time(s)')
    plt.savefig("../../Plots/Violin_" + str(nb_clients) + "_"  + str(nb_byz) + ".png", bbox_inches='tight')
    plt.close()

def violin_plot_slowest_fastest(fl, p2p, con):
    all_times = {'fl': {'slowest': [value for value in fl['slowest']], 'fastest': [value for value in fl['fastest']]},
                 'p2p': {'slowest': [value for value in p2p['slowest']], 'fastest': [value for value in p2p['fastest']]},
                 'con': {'slowest': [value for value in con['slowest']], 'fastest': [value for value in con['fastest']]}}
    
    df = pd.DataFrame(columns = ['senario', 'slowest', 'fastest'])
    for key, value in all_times.items():
        times_df = pd.DataFrame({'senario': key, 'slowest': value['slowest'], 'fastest': value['fastest']})
        df = pd.concat([df, times_df], ignore_index=True)


    df = pd.melt(frame = df, id_vars = 'senario', value_vars = ['slowest', 'fastest'], var_name = 'type', value_name = 'time')
    df['time'] = df['time'].astype(float)
    # print(df)
    ax = sns.violinplot(data = df,x = 'senario', y = 'time', fill=False, split=True, hue='type')
    ax.set_ylabel('time(s)')
    plt.savefig("../../Plots/Violin_Slowest_Fastest_" + str(nb_clients) + "_"  + str(nb_byz) + ".png", bbox_inches='tight')
    plt.close()

def all_accuracy_per_round(fl, p2p, con):
    for agg in aggregators:
        for att in attacks:
            fig, ax = plt.subplots()
            # print(len([np.mean(t) for t in fl[agg][att]]))
            ax.plot(range(1, nb_rounds + 1), [t[0] for t in fl[agg][att][:nb_rounds]], label="fl")
            ax.plot(range(1, nb_rounds + 1), [t[0] for t in p2p[agg][att][:nb_rounds]], label="p2p")
            ax.plot(range(1, nb_rounds + 1), [t[0] for t in con[agg][att][:nb_rounds]], label="con")
            # ax.errorbar(x=range(1, nb_rounds + 1), y=[np.mean(t) for t in fl[agg][att]], yerr=[np.std(t) for t in fl[agg][att]], fmt='o')
            # ax.errorbar(x=range(1, nb_rounds + 1), y=[np.mean(t) for t in p2p[agg][att]], yerr=[np.std(t) for t in p2p[agg][att]], fmt='o')
            # ax.errorbar(x=range(1, nb_rounds + 1), y=[np.mean(t) for t in con[agg][att]], yerr=[np.std(t) for t in con[agg][att]], fmt='o')
            ax.set_xlabel('rounds')
            ax.set_ylabel('accuracy')
            ax.legend(['fl', 'p2p', 'con'])
            ax.set_title("n = " + str(nb_clients) + ", n byz = " + str(nb_byz) + "\naggregator: " + agg + "\nattack:" + att)
            # plt.xticks(range(nb_rounds))
            plt.savefig("../../Plots/" + agg + "/" +  att + "/" + str(nb_clients) + "_"  + str(nb_byz) + "_" + heterogeneity + "_rounds.png", bbox_inches='tight')
            plt.close()

def all_accuracy_per_time(fl, p2p, con):
    for agg in aggregators:
        for att in attacks:
            fig, ax = plt.subplots()
            ax.errorbar(x=[np.mean(t) for t in fl[agg]['end_time'].values()], y=[np.mean(t) for t in fl[agg][att][1:]], yerr=[np.std(t) for t in fl[agg][att][1:]], xerr=[np.std(t) for t in fl[agg]['end_time'].values()], fmt='o')
            ax.errorbar(x=[np.mean(t) for t in p2p[agg]['end_time'].values()], y=[np.mean(t) for t in p2p[agg][att][1:]], yerr=[np.std(t) for t in p2p[agg][att][1:]], xerr=[np.std(t) for t in p2p[agg]['end_time'].values()], fmt='o')
            ax.errorbar(x=[np.mean(t) for t in con[agg]['end_time'].values()], y=[np.mean(t) for t in con[agg][att][1:]], yerr=[np.std(t) for t in con[agg][att][1:]], xerr=[np.std(t) for t in con[agg]['end_time'].values()], fmt='o')

            ax.set_xlabel('time(s)')
            ax.set_ylabel('accuracy')
            ax.legend(['fl', 'p2p', 'con'])
            ax.set_title("average accuracy per average time for n = " + str(nb_clients) + ", n byz = " + str(nb_byz) + "\naggregator: " + agg + "\nattack:" + att)
            plt.savefig("../../Plots/" + agg + "/" +  att + "/" + str(nb_clients) + "_"  + str(nb_byz) + "_average_time_" + heterogeneity + ".png", bbox_inches='tight')
            plt.close()

            # fig, ax = plt.subplots()
            # ax.errorbar(x=[np.min(t) for t in fl[agg]['end_time'].values()], y=[np.mean(t) for t in fl[agg][att][1:]], yerr=[np.std(t) for t in fl[agg][att][1:]], fmt='o')
            # ax.errorbar(x=[np.min(t) for t in p2p[agg]['end_time'].values()], y=[np.mean(t) for t in p2p[agg][att][1:]], yerr=[np.std(t) for t in p2p[agg][att][1:]], fmt='o')
            # ax.errorbar(x=[np.min(t) for t in con[agg]['end_time'].values()], y=[np.mean(t) for t in con[agg][att][1:]], yerr=[np.std(t) for t in con[agg][att][1:]], fmt='o')

            # ax.set_xlabel('time(s)')
            # ax.set_ylabel('accuracy')
            # ax.legend(['fl', 'p2p', 'con'])
            # ax.set_title("average accuracy per fastest node for n = " + str(nb_clients) + ", n byz = " + str(nb_byz) + "\naggregator: " + agg + "\nattack:" + att)
            # plt.savefig("../../Plots/" + agg + "/" +  att + "/" + str(nb_clients) + "_"  + str(nb_byz) + "_fastest_time.png", bbox_inches='tight')
            # plt.close()

            # fig, ax = plt.subplots()
            # ax.errorbar(x=[np.max(t) for t in fl[agg]['end_time'].values()], y=[np.mean(t) for t in fl[agg][att][1:]], yerr=[np.std(t) for t in fl[agg][att][1:]], fmt='o')
            # ax.errorbar(x=[np.max(t) for t in p2p[agg]['end_time'].values()], y=[np.mean(t) for t in p2p[agg][att][1:]], yerr=[np.std(t) for t in p2p[agg][att][1:]], fmt='o')
            # ax.errorbar(x=[np.max(t) for t in con[agg]['end_time'].values()], y=[np.mean(t) for t in con[agg][att][1:]], yerr=[np.std(t) for t in con[agg][att][1:]], fmt='o')

            # ax.set_xlabel('time(s)')
            # ax.set_ylabel('accuracy')
            # ax.legend(['fl', 'p2p', 'con'])
            # ax.set_title("average accuracy per slowest node for n = " + str(nb_clients) + ", n byz = " + str(nb_byz) + "\naggregator: " + agg + "\nattack:" + att)
            # plt.savefig("../../Plots/" + agg + "/" +  att + "/" + str(nb_clients) + "_"  + str(nb_byz) + "_slowest_time.png", bbox_inches='tight')
            # plt.close()

def all_accuracy_per_time_per_pace(fl, p2p, con, rank):
    for agg in aggregators:
        for att in attacks:
            fig, ax = plt.subplots()
            # connect data points

            ax.errorbar(x=fl[agg][att][rank]['end_time'], y=[np.mean(t) for t in fl[agg][att][rank]['acc']], yerr=[np.std(t) for t in fl[agg][att][rank]['acc']], fmt='o-', markersize=1)
            ax.errorbar(x=p2p[agg][att][rank]['end_time'], y=[np.mean(t) for t in p2p[agg][att][rank]['acc']], yerr=[np.std(t) for t in p2p[agg][att][rank]['acc']], fmt='o-', markersize=1)
            ax.errorbar(x=con[agg][att][rank]['end_time'], y=[np.mean(t) for t in con[agg][att][rank]['acc']], yerr=[np.std(t) for t in con[agg][att][rank]['acc']], fmt='o-', markersize=1)

            ax.set_xlabel('time(s)')
            ax.set_ylabel('accuracy')
            ax.legend(['fl', 'p2p', 'con'])
            ax.set_title("average accuracy per " + rank + " time for n = " + str(nb_clients) + ", n byz = " + str(nb_byz) + "\naggregator: " + agg + "\nattack:" + att)
            plt.savefig("../../Plots/" + agg + "/" +  att + "/" + str(nb_clients) + "_"  + str(nb_byz) + "_trsh_" + rank + "_" + heterogeneity + "_time.png", bbox_inches='tight')
            plt.close()

def find_fastest_slowest_trsh(senario, aggregator, attack, trsh):
    if senario == 'fl':
        senario = "FL_res"
        fake_senario = "FL_res"
    if senario == 'p2p':
        senario = 'Gossip_res'
        fake_senario = 'Gossip_res'
    if senario == 'con':
        senario = 'Consensus_res'
        fake_senario = 'FL_res'

    clients_reached_trsh_round = dict()
    clients_reached_trsh_time = dict()    
    lines_clients = dict()
    clients_times = dict()
    clients_accs = dict()
    for i in range(nb_clients - nb_byz):
        clients_times[i] = []
        clients_accs[i] = []
        exps = []
        for exp in range(1, nb_experiments + 1):
            exps.append(accuracy("../../" + fake_senario +"/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Accuracy_" + str(exp) + "/" + heterogeneity + "/" + attack + "/" + str(i) + ".txt"))
        
        clients_accs[i] = [list(sub_list) for sub_list in zip(*exps)]
        exps = [round(sum(sub_list) / len(sub_list), 4) for sub_list in zip(*exps)]
        index = next((i for i, x in enumerate(exps) if x > trsh), None)
        if index == None or index == nb_rounds - 1:
            clients_reached_trsh_round[i] = nb_rounds
        else:
            clients_reached_trsh_round[i] = index + 1
            
        
        lines_clients[i] = readlines("../../" + senario + "/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance_" + str(experiment) + "/" + str(i)  + ".txt")
        for r in range(2, nb_rounds + 1):
            clients_times[i].append((lines_clients[i]['round_{}_end'.format(r)] - lines_clients[i]['round_2_start'.format(r)]).total_seconds())

        clients_reached_trsh_time[i] = (lines_clients[i]['round_{}_end'.format(clients_reached_trsh_round[i])] - lines_clients[i]['round_2_start']).total_seconds()

    # find the key of reached trsh time that has teh minimum value
    min_key = min(clients_reached_trsh_time, key=clients_reached_trsh_time.get)
    max_key = max(clients_reached_trsh_time, key=clients_reached_trsh_time.get)
    # print(len(clients_accs[max_key]), len(clients_times[max_key]))
    print(senario, clients_reached_trsh_round[min_key], min_key)
    res = {'slowest': {'end_time': clients_times[max_key][:clients_reached_trsh_round[max_key] - 1], 'acc': clients_accs[max_key][1:clients_reached_trsh_round[max_key]]},
           'fastest': {'end_time': clients_times[min_key][:clients_reached_trsh_round[min_key] - 1], 'acc': clients_accs[min_key][1:clients_reached_trsh_round[min_key]]}}
    # print(max_key, min_key)
    # print(clients_reached_trsh_time, clients_reached_trsh_time[max_key], clients_reached_trsh_time[min_key])
    return res

def readOrders(client_id, nb_clients, nb_byz, nb_rounds, aggreagator, attack, senario):
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
        if "order" in key_value[0]:
            lines[key_value[0]] = key_value[1]

    orders = dict()
    for i in range(nb_clients):
        orders[i] = 0

    for r in range(1, nb_rounds + 1):
        temp = [int(i) for i in lines["round_{}_aggregation order".format(r)][2:-1].split(',')]
        for t in temp:
            orders[t] += 1
    return orders

def all_clients_acccs(senario, aggregator, attack):
    if senario == 'fl':
        senario = "FL_res"
        fake_senario = "FL_res"
    if senario == 'p2p':
        senario = 'Gossip_res'
        fake_senario = 'Gossip_res'
    if senario == 'con':
        senario = 'Consensus_res'
        fake_senario = 'FL_res'
    
    lines_clients = dict()
    clients_times = dict()
    clients_accs = dict()
    for i in range(nb_clients - nb_byz):
        clients_times[i] = []
        clients_accs[i] = []
        exps = []
        for exp in range(1, nb_experiments + 1):
            exps.append(accuracy("../../" + fake_senario +"/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Accuracy_" + str(exp) + "/" + heterogeneity + "/" + attack + "/" + str(i) + ".txt"))
        
        clients_accs[i] = [np.mean(list(sub_list)) for sub_list in zip(*exps)]
        # print(clients_accs[i])
        
        lines_clients[i] = readlines("../../" + senario + "/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance_" + str(experiment) + "/" + str(i)  + ".txt")
        for r in range(2, nb_rounds + 1):
            clients_times[i].append((lines_clients[i]['round_{}_end'.format(r)] - lines_clients[i]['round_2_start'.format(r)]).total_seconds())

    # plot the accuracy of each client per time
    for i in range(nb_clients - nb_byz):
        plt.plot(clients_times[i], clients_accs[i][1:])

    plt.savefig("../../Plots/" + aggregator + "/" + attack + "/" + str(nb_clients) + "_"  + str(nb_byz) + "_clients_time_" + senario + "_" + heterogeneity + ".png", bbox_inches='tight')
    plt.close()



def main():
    fl = dict()
    p2p = dict()
    con = dict()
    for agg in aggregators:
        fl[agg] = dict()
        p2p[agg] = dict()
        con[agg] = dict()
        analysePerformance(aggregator=agg, nb_clients=nb_clients, nb_byz=nb_byz, res=fl, senario='fl')
        analysePerformance(aggregator=agg, nb_clients=nb_clients, nb_byz=nb_byz, res=p2p, senario='p2p')
        analysePerformance(aggregator=agg, nb_clients=nb_clients, nb_byz=nb_byz, res=con, senario='con')

    #     for att in attacks:
    #         analyseAccuracy(aggregator=agg, attack=att, nb_clients=nb_clients, nb_byz=nb_byz, res=fl, senario='fl')
    #         analyseAccuracy(aggregator=agg, attack=att, nb_clients=nb_clients, nb_byz=nb_byz, res=p2p, senario='p2p')
    #         analyseAccuracy(aggregator=agg, attack=att, nb_clients=nb_clients, nb_byz=nb_byz, res=con, senario='con')
    # print("fl:", len(fl['trmean']['time']))
#     # # print("p2p:", p2p)
#     # # print("con:", con)
    # all_accuracy_per_round(fl, p2p, con)
    # all_accuracy_per_time(fl, p2p, con)
    # accuracy_attack_plot(fl, "fl", nb_clients, nb_byz)
    # accuracy_attack_plot(p2p, "p2p", nb_clients, nb_byz)
    # accuracy_attack_plot(con, "con", nb_clients, nb_byz)

    # boxplots_i(boxes=[[[value for values in fl[agg]['time'].values() for value in values] for agg in aggregators], 
    #                   [[value for values in p2p[agg]['time'].values() for value in values] for agg in aggregators],
    #                   [[value for values in con[agg]['time'].values() for value in values] for agg in aggregators]],
    #            num=3, labels=aggregators, boxes_tags=['fl', 'p2p', 'con'], x_label="aggregator", y_label="time", y_lim=0.15, filename="../../Plots/roundtime_" + str(nb_clients) + "_" + str(nb_byz) + ".png", 
    #            title="n = " + str(nb_clients) + "\n n byz = " + str(nb_byz))
    

    violin_plot(fl, p2p, con)
    # slowest_fl, fastest_fl = find_fastest_slowest('fl', 'trmean')
    # slowest_p2p, fastest_p2p = find_fastest_slowest('p2p', 'trmean')
    # slowest_con, fastest_con = find_fastest_slowest('con', 'trmean')
    # violin_plot_slowest_fastest({'slowest': slowest_fl, 'fastest': fastest_fl}, {'slowest': slowest_p2p, 'fastest': fastest_p2p}, {'slowest': slowest_con, 'fastest': fastest_con})

# #### finding the fastest node that reached the trsh first
    trsh = 0.60
    fl_slowest_fastest = {'trmean': {'SF': find_fastest_slowest_trsh('fl', 'trmean', 'SF', trsh)}}
    p2p_slowest_fastest = {'trmean': {'SF': find_fastest_slowest_trsh('p2p', 'trmean', 'SF', trsh)}}
    con_slowest_fastest = {'trmean': {'SF': find_fastest_slowest_trsh('con', 'trmean', 'SF', trsh)}}
    # print(fl_slowest_fastest['trmean']['SF']['slowest']['end_time'])
    all_accuracy_per_time_per_pace(fl_slowest_fastest, p2p_slowest_fastest, con_slowest_fastest, 'fastest')
    all_accuracy_per_time_per_pace(fl_slowest_fastest, p2p_slowest_fastest, con_slowest_fastest, 'slowest')

## accuracy per time per client
    # all_clients_acccs('p2p', 'trmean', 'SF')
    # all_clients_acccs('fl', 'trmean', 'SF')
    # all_clients_acccs('con', 'trmean', 'SF')

### finding the orders of clients
    # print(readOrders(0, nb_clients, nb_byz, nb_rounds, 'trmean', 'SF', 'fl'))
    # print(readOrders(0, nb_clients, nb_byz, nb_rounds, 'trmean', 'SF', 'con'))
    # for i in range(nb_clients):
    #     print(i, readOrders(i, nb_clients, nb_byz, nb_rounds, 'trmean', 'SF', 'p2p'))
if __name__ == "__main__":
    main()