#!/bin/bash          

if [ $# -lt 3 ]
then
    echo "usage: $0 <senario> <config> <side> <optinal: id>"
    exit
fi

cd DCL_semester_project/main

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

if [[ "$1" != "con" && "$1" != "p2p" && "$1" != "fl" && "$1" != "all" ]]
then
    echo "Wrong senario!"
    exit
fi

if [[ "$3" != "server" && "$3" != "client" ]]
then
    echo "Wrong side!"
    exit
fi

function f {
    echo Done!
}

trap f SIGINT

. ips.config

for agg in ${aggregator[@]}; do
    if [[ "$1" == "fl" || "$1" == "all" ]]
    then
        mkdir -p "../FL_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance
        mkdir -p "../FL_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy
        mkdir -p "./Results/FL"
        if [[ "$3" == "server" ]]
        then
            echo running FL server with "$nb_byz" byzantine client. Performanace test phase! Aggregator: "$agg"
            python3 Server.py "$nb_clients" "$localHost" "$server_port" "$nb_byz" "$rounds" "$agg" "att" "Performance" > "./Results/FL/server_res.txt"
        fi
        if [[ "$3" == "client" ]]
        then
            echo running FL client "$4" with "$nb_byz" byzantine client. Performanace test phase! Aggregator: "$agg"
            # variablename=client_$4
            # echo ${!variablename}
            python3 Client.py "$nb_clients" "$4" "$server" "$server_port" "$rounds" "$nb_byz" "$agg" "att" "Performance" > "./Results/FL/res_$c.txt"
        fi
    fi

    # if [[ "$1" == "p2p" || "$1" == "all" ]]
    # then
    #     mkdir -p "../Gossip_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance
    #     mkdir -p "../Gossip_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy
    #     echo running p2p with "$nb_byz" byzantine client. Performanace test phase! Aggregator: "$agg"
    #     bash gossipRunner.sh "$nb_clients" "$localHost" "$server_port" "$nb_byz" "$rounds" "$agg" "att" "Performance"
    # fi

    # if [[ "$1" == "con" || "$1" == "all" ]]
    # then
    #     mkdir -p "../Consensus_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance
    #     mkdir -p "../Consensus_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy
    #     echo running con with "$nb_byz" byzantine client. Performanace test phase! Aggregator: "$agg"
    #     bash ConsensusRunner.sh "$nb_replicas" "$nb_clients" "$rounds" "$localHost" "$nb_byz" "$agg" "att" "Performance"
    # fi
done