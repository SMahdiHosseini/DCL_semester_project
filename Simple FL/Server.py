
from Utils import Model, Helper
from multiprocessing.connection import Listener
from threading import Thread



# for i in range(Helper.rounds):
#     print('Start Round {} ...'.format(i + 1))
#     curr_parameters = global_net.get_parameters()
#     new_parameters = dict([(layer_name, {'weight': 0, 'bias': 0}) for layer_name in curr_parameters])




#     for client in clients:
#         client_parameters = client.train(curr_parameters)
#         fraction = client.get_dataset_size() / total_train_size
#         for layer_name in client_parameters:
#             new_parameters[layer_name]['weight'] += fraction * client_parameters[layer_name]['weight']
#             new_parameters[layer_name]['bias'] += fraction * client_parameters[layer_name]['bias']
#     global_net.apply_parameters(new_parameters)

#     train_loss, train_acc = global_net.evaluate(train_dataset)
#     dev_loss, dev_acc = global_net.evaluate(dev_dataset)
#     test_loss, test_acc = global_net.evaluate(test_dataset)
#     print('After round {}, train_loss = {}, dev_loss = {}, dev_acc = {}, test_loss = {}, test_acc = {}\n'.format(i + 1, round(train_loss, 4),
#             round(dev_loss, 4), round(dev_acc, 4), round(test_loss, 4), round(test_acc, 4)))
#     history.append((train_loss, dev_loss))

# def clientHandler(connection):
    # start_initial_round()
    # while True:
    #     msg = conn.recv()
    #     # Do something with msg
    #     if msg == 'close':
    #         conn.close()
    #         break

def main():
    threads = []

    address = (Helper.localHost, Helper.server_port)
    listener = Listener(address)
    global_net = Helper.to_device(Model.FederatedNet(), Helper.device)
    history = []
    connections = []

    print("Server is running on port: {}".format(Helper.server_port))

    for cient in range(Helper.num_clients):
        new_connection = listener.accept()
        connections.append(new_connection)




if __name__ == '__main__':
    main()