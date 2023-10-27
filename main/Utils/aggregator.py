import torch

def average(aggreagator, vectors):
    return torch.stack(vectors).mean(dim=0)

#JS: Dictionary mapping every aggregator to its corresponding function
# {"average": average, "trmean": trmean, "median": median, "geometric_median": geometric_median, "krum": krum, "nnm": nearest_neighbor_mixing}
robust_aggregators = {"average": average}

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