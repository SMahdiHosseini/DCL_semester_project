from ConnectionDistributer import readConfig
import sys
import fileinput

replicas_port = 10000
nb_clients = int(sys.argv[1])
nb_byz = int(sys.argv[2])

config = readConfig('../ips.config')
hostsConfig = fileinput.input('../../library/config/hosts.config', inplace=True)
for line in hostsConfig:
    if "#server id, address and port (the ids from 0 to n-1 are the service replicas)" in line:
        print(line, end='')
        for i in range(nb_clients):
            print(str(i) + " " + config['client_' + str(i)] + " " + str(replicas_port) + " " + str(replicas_port + 1))
            replicas_port += 10
        break
    else:
        print(line, end='')
hostsConfig.close()

systemConfig = fileinput.input('../../library/config/system.config', inplace=True)
for line in systemConfig:
    if "system.servers.num =" in line:
        print("system.servers.num = " + str(nb_clients))
        continue
    if "system.servers.f" in line:
        print("system.servers.f = " + str(nb_byz))
        continue
    if "system.initial.view = " in line:
        s = ",".join([str(i) for i in range(nb_clients)])
        print("system.initial.view = " + s)
        continue
    else:
        print(line, end='')