#!/bin/bash          

if [ $# -lt 4 ]
then
    echo "usage: $0 <senario> <config> <aggregator> <side> <optinal: id>"
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

if [[ "$4" != "server" && "$4" != "client" ]]
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
    if [[ "$4" == "server" ]]
    then
        echo running FL server with "$nb_byz" byzantine client. Performanace test phase! Aggregator: "$3"
        python3 Server.py "$nb_clients" "0.0.0.0" "$server_port" "$nb_byz" "$rounds" "$3" "att" "Performance" > "./Results/FL/server_res.txt"
    fi
    if [[ "$4" == "client" ]]
    then
        echo running FL client "$5" with "$nb_byz" byzantine client. Performanace test phase! Aggregator: "$3"
        # variablename=client_$4
        # echo ${!variablename}
        python3 Client.py "$nb_clients" "$5" "$server" "$server_port" "$rounds" "$nb_byz" "$3" "att" "Performance" > "./Results/FL/res_$5.txt"
    fi
fi

if [[ "$1" == "p2p" || "$1" == "all" ]]
then
    mkdir -p "../Gossip_res/""$3"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance
    mkdir -p "../Gossip_res/""$3"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy
    echo running p2p client "$5" with "$nb_byz" byzantine client. Performanace test phase! Aggregator: "$3"
    python3 Client_Gossip.py "$5" "$nb_clients" "0.0.0.0" "$server_port" "$nb_byz" "$rounds" "$3" "att" "Performance" > "./Results/gossip/res_$5.txt"
fi

if [[ "$1" == "con" || "$1" == "all" ]]
then
    mkdir -p "../Consensus_res/""$3"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance
    mkdir -p "../Consensus_res/""$3"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy
    cd ../library/build/install/library
    echo running con client "$5" with "$nb_byz" byzantine client. Performanace test phase! Aggregator: "$3"
    ./smartrun.sh bftsmart.FL.FLServer "$5" "$nb_clients" "$rounds" "$localHost" "$nb_byz" "$3" "att" "Performance" > "./Results/res_$5.txt" &
    sleep 5s
    ./smartrun.sh bftsmart.FL.FLClientInterface "$5" "$localHost" "$nb_clients" "$nb_byz" "$3" "att" "Performance" &
    wait
fi