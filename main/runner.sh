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

if [[ "$1" != "con" && "$1" != "p2p" && "$1" != "fl" && "$1" != "all" ]]
then
    echo "Wrong senario!"
    exit
fi


function f {
    echo Done!
}

trap f SIGINT

for agg in ${aggregator[@]}; do
    if [[ "$1" == "fl" || "$1" == "all" ]]
    then
        mkdir -p "../FL_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance
        mkdir -p "../FL_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy
        echo running FL with "$nb_byz" byzantine client. Performanace test phase! Aggregator: "$agg"
        bash FLRunner.sh "$nb_clients" "$localHost" "$server_port" "$nb_byz" "$rounds" "$agg" "att" "Performance"

        for att in ${attack[@]}; do
            mkdir -p "../FL_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy/"$att"
            echo running FL with "$nb_byz" byzantine client. Accuracy test phase! Aggregator: "$agg" Attack: "$att"
            ((new_nb_clients = nb_clients - nb_byz))
            bash FLRunner.sh "$new_nb_clients" "$localHost" "$server_port" "$nb_byz" "$rounds" "$agg" "$att" "accuracy"
        done
    fi

    if [[ "$1" == "p2p" || "$1" == "all" ]]
    then
        mkdir -p "../Gossip_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance
        mkdir -p "../Gossip_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy
        echo running p2p with "$nb_byz" byzantine client. Performanace test phase! Aggregator: "$agg"
        bash gossipRunner.sh "$nb_clients" "$localHost" "$server_port" "$nb_byz" "$rounds" "$agg" "att" "Performance"

        for att in ${attack[@]}; do
            mkdir -p "../Gossip_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy/"$att"
            echo running p2p with "$nb_byz" byzantine client. Accuracy test phase! Aggregator: "$agg" Attack: "$att"
            ((new_nb_clients = nb_clients - nb_byz))
            bash gossipRunner.sh "$new_nb_clients" "$localHost" "$server_port" "$nb_byz" "$rounds" "$agg" "$att" "accuracy"
        done
    fi

    if [[ "$1" == "con" || "$1" == "all" ]]
    then
        mkdir -p "../Consensus_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance
        mkdir -p "../Consensus_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy
        echo running con with "$nb_byz" byzantine client. Performanace test phase! Aggregator: "$agg"
        bash ConsensusRunner.sh "$nb_replicas" "$nb_clients" "$rounds" "$localHost" "$nb_byz" "$agg" "att" "Performance"

        for att in ${attack[@]}; do
            mkdir -p "../Consensus_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy/"$att"
            echo running con with "$nb_byz" byzantine client. Accuracy test phase! Aggregator: "$agg" Attack: "$att"
            ((new_nb_clients = nb_clients - nb_byz))
            # bash ConsensusRunner.sh "$nb_replicas" "$new_nb_clients" "$rounds" "$localHost" "$nb_byz" "$agg" "$att" "accuracy"
        done
    fi
done