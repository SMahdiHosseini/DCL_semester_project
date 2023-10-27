import torch

def averageAgg(recvd_params, recvd_size):
    cluster_size = sum(recvd_size)
    for i in range(len(recvd_params)):
        recvd_params[i] = recvd_size[i] / cluster_size * recvd_params[i]
    new_model_parameters = torch.sum(torch.stack(recvd_params), dim=0)
    return new_model_parameters