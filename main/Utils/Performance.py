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
    "lines.linewidth":5.})

#program input: nb_clients, nb_byz, nb_rounds
nb_clients = int(sys.argv[1])
nb_byz = int(sys.argv[2])
nb_rounds = int(sys.argv[3])
attacks = ["SF", "FOE"]
aggregators = ["trmean"]
# aggregators = ["average", "median", "geometric_median", "trmean"]
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
        # if i != 0:
        result.append(round(float(key_value[-1]), 4))
        i += 1
    return result

def analyseFLPerformance(aggregator, attack, nb_clients, nb_byz, fl_res):
    # fl_res[aggregator][attack] = accuracy("../../FL_res/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Accuracy/" + attack + "/0.txt")
    log = Log.Log("../../FL_res/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance/performance.txt")
    lines_server = readlines("../../FL_res/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance/server.txt")
    lines_clients = []
    for i in range(nb_clients):
        lines_clients.append(readlines("../../FL_res/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance/" + str(i)  + ".txt"))
    total_average = 0
    total = 0
    times = dict()
    for r in range(2, nb_rounds + 1):
        #clients
        rounds_times = []
        for c in range(nb_clients):
            temp = lines_clients[c]['round_{}_end'.format(r)] - lines_clients[c]['round_{}_start'.format(r)]
            # temp = lines_clients[c]['round_{}_model_shared'.format(r)] - lines_clients[c]['round_{}_model_trained'.format(r)]
            # temp = lines_clients[c]['round_{}_model_trained'.format(r)] - lines_clients[c]['round_{}_start'.format(r)]
            rounds_times.append(temp.total_seconds())
        avg = sumOfTimes(rounds_times) / nb_clients
        #server
        # t = (lines_server['round_{}_end'.format(r)] - lines_server['round_{}_start'.format(r)]).total_seconds()
        # t = (lines_server['round_{}_received_params'.format(r)] - lines_server['round_{}_start'.format(r)] + lines_server['round_{}_end'.format(r)] - lines_server['round_{}_aggregation'.format(r)]).total_seconds()
        if r == 2:
            # total = t
            total_average = avg
        else:
            # total += t
            total_average += avg
        # log.addLog("round {}\n\tserver time: {}\n\tclients average time: {}\n".format(r, t, avg))
        # times[r] = [t] + rounds_times
        times[r] = rounds_times
    log.addLog("total \n\tserver_time: {}\n\tclients average total time: {}".format(total, total_average))
    log.writeLogs()
    fl_res[aggregator]['time'] = times

def analyseP2PPerformance(aggregator, attack, nb_clients, nb_byz, p2p_res):
    # p2p_res[aggregator][attack] = accuracy("../../Gossip_res/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Accuracy/" + attack + "/0.txt")
    log = Log.Log("../../Gossip_res/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance/performance.txt")
    lines_clients = []
    for i in range(nb_clients):
        lines_clients.append(readlines("../../Gossip_res/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance/" + str(i)  + ".txt"))
    total_average = 0
    times = dict()
    for r in range(2, nb_rounds + 1):
        #clients
        rounds_times = []
        for c in range(nb_clients):
            temp = lines_clients[c]['round_{}_end'.format(r)] - lines_clients[c]['round_{}_start'.format(r)]
            # temp = lines_clients[c]['round_{}_model_shared'.format(r)] - lines_clients[c]['round_{}_model_trained'.format(r)]
            # temp = lines_clients[c]['round_{}_model_trained'.format(r)] - lines_clients[c]['round_{}_start'.format(r)]
            # temp = lines_clients[c]['round_{}_received_params'.format(r)] - lines_clients[c]['round_{}_start'.format(r)] + lines_clients[c]['round_{}_end'.format(r)] - lines_clients[c]['round_{}_aggregation'.format(r)]
            rounds_times.append(temp.total_seconds())
        avg = sumOfTimes(rounds_times) / nb_clients
        if r == 2:
            total_average = avg
        else:
            total_average += avg
        log.addLog("round {}\n\tclients average time: {}\n".format(r, avg))
        times[r] = rounds_times
    log.addLog("total \n\tclients average total time: {}".format(total_average))
    log.writeLogs()
    p2p_res[aggregator]['time'] = times

def analyseConPerformance(aggregator, attack, nb_clients, nb_byz, con_res):
    temp = []
    # for i in range(nb_clients - nb_byz):
    #     temp.append(accuracy("../../Consensus_res/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Accuracy/" + attack + "/" + str(i) + ".txt"))
    # con_res[aggregator][attack] = [sum(sub_list) / len(sub_list) for sub_list in zip(*temp)]
    # nb_replicas = 4
    log = Log.Log("../../Consensus_res/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance/performance.txt")
    lines_replicas = []
    lines_clients = []
    for i in range(nb_clients):
        lines_clients.append(readlines("../../Consensus_res/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance/" + str(i)  + ".txt"))
    for i in range(nb_clients):
        lines_replicas.append(readlines("../../Consensus_res/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance/server_" + str(i)  + ".txt"))

    total_average_clients = 0
    total_average_replicas = 0
    times = dict()
    for r in range(2, nb_rounds + 1):
        #clients
        rounds_times_clients = []
        for c in range(nb_clients):
            temp = lines_clients[c]['round_{}_end'.format(r)] - lines_clients[c]['round_{}_start'.format(r)]
            # temp = lines_clients[c]['round_{}_model_shared'.format(r)] - lines_clients[c]['round_{}_model_trained'.format(r)]
            # temp = lines_clients[c]['round_{}_model_trained'.format(r)] - lines_clients[c]['round_{}_start'.format(r)]
            rounds_times_clients.append(temp.total_seconds())
        avg_c = sumOfTimes(rounds_times_clients) / nb_clients
        #replicas
        rounds_times_replicas = []
        for s in range(nb_clients):
            temp = lines_replicas[s]['round_{}_end'.format(r)] - lines_replicas[s]['round_{}_start'.format(r)]
            # temp = lines_replicas[s]['round_{}_received_params'.format(r)] - lines_replicas[s]['round_{}_start'.format(r)] + lines_replicas[s]['round_{}_end'.format(r)] - lines_replicas[s]['round_{}_aggregation'.format(r)]
            rounds_times_replicas.append(temp.total_seconds())
        avg_s = sumOfTimes(rounds_times_replicas) / nb_clients

        if r == 2:
            total_average_replicas = avg_s
            total_average_clients = avg_c
        else:
            total_average_replicas += avg_s
            total_average_clients += avg_c
        log.addLog("round {}\n\treplicas average time: {}\n\tclients average time: {}\n".format(r, avg_s, avg_c))
        # times[r] = rounds_times_replicas + rounds_times_clients
        times[r] = rounds_times_clients
    log.addLog("total \n\treplicas average total time: {}\n\tclients average total time: {}".format(total_average_replicas, total_average_clients))
    log.writeLogs()
    con_res[aggregator]['time'] = times

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
    # ylim(- y_lim * 0.008, y_lim)
    ylim(0.4, y_lim)
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
            ax.plot(range(nb_rounds + 1), res[agg][att], label=att)
        ax.set_xlabel('rounds')
        ax.set_ylabel('accuracy')
        ax.legend()
        ax.set_title("n = " + str(nb_clients) + ", n byz = " + str(nb_byz) + "\naggregator: " + agg)
        plt.xticks(range(nb_rounds + 1))
        plt.savefig("../../Plots/" + agg + "/" + label + "_" + str(nb_clients) + "_"  + str(nb_byz) + ".png", bbox_inches='tight')
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
        lines_clients[i] = readlines("../../" + senario + "/" + aggregator + "/ncl_" + str(nb_clients) + "/nbyz_" + str(nb_byz) + "/Performance/" + str(i)  + ".txt")
        
    for r in range(2, nb_rounds + 1):
        for i in range(nb_clients):
            clients_times[i].append((lines_clients[i]['round_{}_end'.format(r)] - lines_clients[i]['round_{}_start'.format(r)]).total_seconds())
            
    total_times = {key: sum(value) for key, value in clients_times.items()}
    slowest_key = max(total_times, key=total_times.get)
    fastest_key = min(total_times, key=total_times.get)

    return clients_times[slowest_key], clients_times[fastest_key]

def violin_plot(fl, p2p, con):
    all_times = {'fl': {'trmean': [value for values in fl['trmean']['time'].values() for value in values]}, 
             'p2p': {'trmean': [value for values in p2p['trmean']['time'].values() for value in values]}, 
             'con': {'trmean': [value for values in con['trmean']['time'].values() for value in values]}}
    df = pd.DataFrame(columns = ['senario', 'trmean'])
    for key, value in all_times.items():
        times_df = pd.DataFrame({'senario': key, 'trmean': value['trmean']})
        df = pd.concat([df, times_df], ignore_index=True)
    
    df = pd.melt(frame = df, id_vars = 'senario', value_vars = ['trmean'],var_name = 'aggregator', value_name = 'time')
    df['time'] = df['time'].astype(float)
    ax = sns.violinplot(data = df,x = 'senario', y = 'time', fill=False)
    ax.axhline(np.median(all_times['fl']['trmean']), color='blue', linewidth=1)
    ax.axhline(np.median(all_times['p2p']['trmean']), color='red', linewidth=1)
    ax.axhline(np.median(all_times['con']['trmean']), color='green', linewidth=1)
    plt.grid(True)
    plt.show()

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
    print(df)
    ax = sns.violinplot(data = df,x = 'senario', y = 'time', fill=False, split=True, hue='type')
    # # ax.axhline(mean_est, color='')

    plt.show()

def main():
    fl = dict()
    p2p = dict()
    con = dict()
    for agg in aggregators:
        fl[agg] = dict()
        p2p[agg] = dict()
        con[agg] = dict()
        for att in attacks:
            analyseFLPerformance(aggregator=agg, attack=att, nb_clients=nb_clients, nb_byz=nb_byz, fl_res=fl)
            analyseP2PPerformance(aggregator=agg, attack=att, nb_clients=nb_clients, nb_byz=nb_byz, p2p_res=p2p)
            analyseConPerformance(aggregator=agg, attack=att, nb_clients=nb_clients, nb_byz=nb_byz, con_res=con)
    # print("fl:", fl)
    # print("p2p:", p2p)
    # print("con:", con)
    # for agg in aggregators:
    #     for att in attacks:
    #         fig, ax = plt.subplots()
    #         ax.plot(range(nb_rounds + 1), fl[agg][att], label="fl")
    #         ax.plot(range(nb_rounds + 1), p2p[agg][att], label="p2p")
    #         ax.plot(range(nb_rounds + 1), con[agg][att], label="consensus")
    #         ax.set_xlabel('rounds')
    #         ax.set_ylabel('accuracy')
    #         ax.legend()
    #         ax.set_title("n = " + str(nb_clients) + ", n byz = " + str(nb_byz) + "\naggregator: " + agg + "\nattack:" + att)
    #         plt.xticks(range(nb_rounds + 1))
    #         plt.savefig("../../Plots/" + agg + "/" +  att + "/" + str(nb_clients) + "_"  + str(nb_byz) + ".png", bbox_inches='tight')
    #         plt.close()

    # accuracy_attack_plot(fl, "fl", nb_clients, nb_byz)
    # accuracy_attack_plot(p2p, "p2p", nb_clients, nb_byz)
    # accuracy_attack_plot(con, "con", nb_clients, nb_byz)

    boxplots_i(boxes=[[[value for values in fl[agg]['time'].values() for value in values] for agg in aggregators], 
                      [[value for values in p2p[agg]['time'].values() for value in values] for agg in aggregators],
                      [[value for values in con[agg]['time'].values() for value in values] for agg in aggregators]],
               num=3, labels=aggregators, boxes_tags=['fl', 'p2p', 'con'], x_label="aggregator", y_label="time", y_lim=0.7, filename="../../Plots/roundtime_" + str(nb_clients) + "_" + str(nb_byz) + ".png", 
               title="n = " + str(nb_clients) + "\n n byz = " + str(nb_byz))
    

    violin_plot(fl, p2p, con)
    slowest_fl, fastest_fl = find_fastest_slowest('fl', 'trmean')
    slowest_p2p, fastest_p2p = find_fastest_slowest('p2p', 'trmean')
    slowest_con, fastest_con = find_fastest_slowest('con', 'trmean')
    violin_plot_slowest_fastest({'slowest': slowest_fl, 'fastest': fastest_fl}, {'slowest': slowest_p2p, 'fastest': fastest_p2p}, {'slowest': slowest_con, 'fastest': fastest_con})
if __name__ == "__main__":
    main()