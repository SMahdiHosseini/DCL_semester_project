import torch
from Utils import misc

def readlines(input_file_name):
    input_file = open(input_file_name, "r")
    lines = dict()
    for line in input_file:
        line = line.strip()
        key_value = line.split(":")
        if "order" in key_value[0]:
            lines[key_value[0]] = key_value[1]
    return lines

def average(aggreagator, vectors):
    return torch.stack(vectors).mean(dim=0)

def trmean(aggregator, vectors):
    if aggregator.nb_byz == 0:
        return torch.stack(vectors).mean(dim=0)
    return torch.stack(vectors).sort(dim=0).values[aggregator.nb_byz:-aggregator.nb_byz].mean(dim=0)

def median(aggregator, vectors):
    return torch.stack(vectors).quantile(q=0.5, dim=0)
    #return torch.stack(vectors).median(dim=0)[0]

def geometric_median(aggregator, vectors):
    return misc.smoothed_weiszfeld(vectors)

def krum(aggregator, vectors):
    #JS: Compute all pairwise distances
    distances = misc.compute_distances(vectors)
    #JS: return the vector with smallest score
    return misc.get_vector_best_score(vectors, aggregator.nb_byz, distances)

def nearest_neighbor_mixing(aggregator, vectors, numb_iter=1):
    for _ in range(numb_iter):
        mixed_vectors = list()
        for vector in vectors:
            #JS: Replace every vector by the average of its nearest neighbors
            mixed_vectors.append(misc.average_nearest_neighbors(vectors, aggregator.nb_byz, vector))
        vectors = mixed_vectors
    return robust_aggregators[aggregator.second_aggregator](aggregator, vectors)

#JS: Dictionary mapping every aggregator to its corresponding function
robust_aggregators = {"average": average, "trmean": trmean, "median": median, "geometric_median": geometric_median, "krum": krum, "nnm": nearest_neighbor_mixing}

class RobustAggregator(object):

    def __init__(self, aggregator_name, second_aggregator, bucket_size, nb_byz, device):

        self.aggregator_name = aggregator_name
        self.second_aggregator = second_aggregator
        self.bucket_size = bucket_size
        self.nb_byz = nb_byz

    def aggregate(self, vectors):
        aggregate_vector = robust_aggregators[self.aggregator_name](self, vectors)
        #JS: Update the value of the previous momentum (e.g., for Centered Clipping aggregator)
        self.prev_momentum = aggregate_vector
        return aggregate_vector
    
    def readOrders(self, client_id, nb_clients, nb_byz, nb_rounds, attack, senario):
        if senario == 'fl':
            logFile = "../FL_res/" + self.second_aggregator + "/ncl_" + str(nb_clients + nb_byz) + "/nbyz_" + str(nb_byz) + "/Performance/server.txt"
        if senario == 'p2p':
            logFile = "../Gossip_res/" + self.second_aggregator + "/ncl_" + str(nb_clients + nb_byz) + "/nbyz_" + str(nb_byz) + "/Performance/" + str(client_id) + ".txt"
        if senario == 'con':
            logFile = "../../../../Consensus_res/" + self.second_aggregator + "/ncl_" + str(nb_clients + nb_byz) + "/nbyz_" + str(nb_byz) + "/Performance/orders.txt"

        byz_ids = [i for i in range(nb_clients + nb_byz) if i >= nb_clients]
        lines = readlines(logFile)
        orders = dict()
        for r in range(1, nb_rounds + 1):
            temp = [int(i) for i in lines["round_{}_aggregation order".format(r)][2:-1].split(',')]
            orders[r] = [i for i in temp if i not in byz_ids][:nb_clients - nb_byz]
            print("round_{}_aggregation order: {}".format(r, orders[r]))
        return orders