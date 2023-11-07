import torch, math
from Utils import misc

def labelflipping(attack, flipped_vectors, **kwargs):
    #TODO
    avg_flipped_vector = torch.stack(flipped_vectors).mean(dim=0)
    return [avg_flipped_vector] * attack.nb_real_byz

def signflipping(attack, honest_vectors, **kwargs):
    avg_honest_vector = torch.stack(honest_vectors).mean(dim=0)
    byzantine_vector = torch.mul(avg_honest_vector, -1)
    return [byzantine_vector] * attack.nb_real_byz

byzantine_attacks = {"LF": labelflipping, "SF": signflipping}

class ByzantineAttack(object):

    def __init__(self, attack_name, nb_real_byz):

        self.attack_name = attack_name
        self.nb_real_byz = nb_real_byz


    def generate_byzantine_vectors(self, honest_vectors, flipped_vectors):
        if self.nb_real_byz == 0:
            return list()
        
        return byzantine_attacks[self.attack_name](self, honest_vectors=honest_vectors, flipped_vectors=flipped_vectors)