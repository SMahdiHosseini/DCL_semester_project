#!/bin/bash          

if [ $# -lt 6 ]
then
    echo "usage: $0 <senario> <config> <aggregator> <attack> <test> <side> <optinal: id>"
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

if [[ "$6" != "server" && "$6" != "client" ]]
then
    echo "Wrong side!"
    exit
fi

function f {
    echo Done!
}

trap f SIGINT

. ips.config

if [[ "$1" == "fl" || "$1" == "all" ]]
then
    mkdir -p "../FL_res/""$3"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance
    mkdir -p "../FL_res/""$3"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy
    mkdir -p "./Results/FL"
    if [[ "$6" == "server" ]]
    then
        echo running FL server with "$nb_byz" byzantine client. "$5" test phase! Aggregator: "$3" Attack: "$4"
        python3 Server.py "$nb_clients" "0.0.0.0" "$server_port" "$nb_byz" "$rounds" "$3" "$4" "$5" > "./Results/FL/server_res.txt"
    fi
    if [[ "$6" == "client" ]]
    then
        echo running FL client "$7" with "$nb_byz" byzantine client. "$5" test phase! Aggregator: "$3" Attack: "$4"
        python3 Client.py "$nb_clients" "$7" "$server" "$server_port" "$rounds" "$nb_byz" "$3" "$4" "$5" > "./Results/FL/res_$7.txt"
    fi
fi

if [[ "$1" == "p2p" || "$1" == "all" ]]
then
    mkdir -p "../Gossip_res/""$3"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance
    mkdir -p "../Gossip_res/""$3"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy
    echo running p2p client "$7" with "$nb_byz" byzantine client. "$5" test phase! Aggregator: "$3" Attack: "$4"
    python3 Client_Gossip.py "$7" "$nb_clients" "0.0.0.0" "$server_port" "$nb_byz" "$rounds" "$3" "$4" "$5" > "./Results/gossip/res_$7.txt"
fi

if [[ "$1" == "con" || "$1" == "all" ]]
then
    mkdir -p "../Consensus_res/""$3"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance
    mkdir -p "../Consensus_res/""$3"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy
    cd ../library/build/install/library
    if [[ "$6" == "server" ]]
    then
        echo running con replica "$7" with "$nb_byz" byzantine client. "$5" test phase! Aggregator: "$3" Attack: "$4"
        ./smartrun.sh bftsmart.FL.FLServer "$7" "$nb_clients" "$rounds" "$localHost" "$nb_byz" "$3" "$4" "$5" > "./Results/res_$7.txt"
    fi
    if [[ "$6" == "client" ]]
    then
        echo running con client "$7" with "$nb_byz" byzantine client. Performanace test phase! Aggregator: "$3" Attack: "$4"
        ./smartrun.sh bftsmart.FL.FLClientInterface "$7" "$localHost" "$nb_clients" "$nb_byz" "$3" "$4" "$5" > "./Results/res_client_$7.txt"
    fi
fi