#!/bin/bash          

if [ $# -lt 2 ]
then
    echo "usage: $0 <senario> <config>"
    exit
fi

if [[ "$2" == "main" ]];
then 
    . main.config
elif [[ "$2" == "test" ]];
then 
    . test.config
else
    echo "Worng config file!"
    exit
fi

if [[ "$1" == "fl" || "$1" == "all" ]]
then
    bash FLRunner.sh "$nb_clients" "$localHost" "$server_port" "$nb_byz" "$rounds"
fi

if [[ "$1" == "p2p" || "$1" == "all" ]]
then
    bash gossipRunner.sh "$nb_clients" "$localHost" "$server_port" "$nb_byz" "$rounds"
fi

if [[ "$1" == "con" || "$1" == "all" ]]
then
    bash ConsensusRunner.sh "$nb_replicas" "$nb_clients" "$rounds" "$localHost" "$nb_byz"
fi

if [[ "$1" != "con" && "$1" != "p2p" && "$1" != "fl" && "$1" != "all" ]]
then
    echo "Wrong senario!"
    exit
fi