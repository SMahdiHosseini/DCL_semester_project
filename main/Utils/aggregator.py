import torch
from Utils import misc

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