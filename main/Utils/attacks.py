import torch, math
from Utils import misc

random_seed = 10
torch.manual_seed(random_seed)
torch.cuda.manual_seed(random_seed)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False

def labelflipping(attack, flipped_vectors, **kwargs):
    #TODO
    avg_flipped_vector = torch.stack(flipped_vectors).mean(dim=0)
    return [avg_flipped_vector] * attack.nb_real_byz

def signflipping(attack, honest_vectors, **kwargs):
    avg_honest_vector = torch.stack(honest_vectors).mean(dim=0)
    byzantine_vector = torch.mul(avg_honest_vector, -1)
    return [byzantine_vector] * attack.nb_real_byz

def fall_of_empires(attack, honest_vectors, attack_factor=3, negative=False, **kwargs):
    avg_honest_vector = torch.stack(honest_vectors).mean(dim=0)
    attack_vector = avg_honest_vector.neg()
    if negative:
        attack_factor = - attack_factor
    byzantine_vector = avg_honest_vector.add(attack_vector, alpha=attack_factor)
    return [byzantine_vector] * attack.nb_real_byz

byzantine_attacks = {"LF": labelflipping, "SF": signflipping, "FOE": fall_of_empires}

class ByzantineAttack(object):

    def __init__(self, attack_name, nb_real_byz):

        self.attack_name = attack_name
        self.nb_real_byz = nb_real_byz


    def generate_byzantine_vectors(self, honest_vectors, flipped_vectors):
        if self.nb_real_byz == 0:
            return list()
        
        return byzantine_attacks[self.attack_name](self, honest_vectors=honest_vectors, flipped_vectors=flipped_vectors)