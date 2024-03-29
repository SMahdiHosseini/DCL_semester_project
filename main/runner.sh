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

for i in {3..3}
do
    for agg in ${aggregator[@]}; do
        if [[ "$1" == "fl" || "$1" == "all" ]]
        then
            mkdir -p "../FL_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance
            mkdir -p "../FL_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy
            mkdir -p "../FL_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy_$i
            mkdir -p "../FL_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy_$i/Heterogeneous
            mkdir -p "../FL_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy_$i/Homogeneous

            # echo running FL with "$nb_byz" byzantine client. Performance test phase! Aggregator: "$agg"
            # bash FLRunner.sh "$nb_clients" "$localHost" "$server_port" "$nb_byz" "$rounds" "$agg" "att" "Performance"

            for att in ${attack[@]}; do
                mkdir -p "../FL_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy/"$att"
                echo running FL with "$nb_byz" byzantine client. Accuracy test phase! Aggregator: "$agg" Attack: "$att"
                ((new_nb_clients = nb_clients - nb_byz))
                bash FLRunner.sh "$new_nb_clients" "$localHost" "$server_port" "$nb_byz" "$rounds" "$agg" "$att" "Accuracy"
                if [[ "$Heterogeneity" == "1" ]]
                then
                    rm -rf "../FL_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy_$i/Heterogeneous/"$att"
                    mv -f "../FL_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy/"$att" "../FL_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy_$i/Heterogeneous/
                else
                    rm -rf "../FL_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy_$i/Homogeneous/"$att"
                    mv -f "../FL_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy/"$att" "../FL_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy_$i/Homogeneous/
                fi
            done
        fi

        if [[ "$1" == "p2p" || "$1" == "all" ]]
        then
            mkdir -p "../Gossip_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance
            mkdir -p "../Gossip_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy
            mkdir -p "../Gossip_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy_$i
            mkdir -p "../Gossip_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy_$i/Heterogeneous
            mkdir -p "../Gossip_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy_$i/Homogeneous

            # echo running p2p with "$nb_byz" byzantine client. Performance test phase! Aggregator: "$agg"
            # bash gossipRunner.sh "$nb_clients" "$localHost" "$server_port" "$nb_byz" "$rounds" "$agg" "att" "Performance"

            for att in ${attack[@]}; do
                mkdir -p "../Gossip_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy/"$att"
                echo running p2p with "$nb_byz" byzantine client. Accuracy test phase! Aggregator: "$agg" Attack: "$att"
                ((new_nb_clients = nb_clients - nb_byz))
                bash gossipRunner.sh "$new_nb_clients" "$localHost" "$server_port" "$nb_byz" "$rounds" "$agg" "$att" "Accuracy"
                if [[ "$Heterogeneity" == "1" ]]
                then
                    rm -rf "../Gossip_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy_$i/Heterogeneous/"$att"
                    mv -f "../Gossip_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy/"$att" "../Gossip_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy_$i/Heterogeneous/
                else
                    rm -rf "../Gossip_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy_$i/Homogeneous/"$att"
                    mv -f "../Gossip_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy/"$att" "../Gossip_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy_$i/Homogeneous/
                fi
            done
        fi

        if [[ "$1" == "con" || "$1" == "all" ]]
        then
            mkdir -p "../Consensus_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance
            mkdir -p "../Consensus_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy
            mkdir -p "../Consensus_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy_$i
            mkdir -p "../Consensus_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy_$i/Heterogeneous
            mkdir -p "../Consensus_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy_$i/Homogeneous

            echo running con with "$nb_byz" byzantine client. Performance test phase! Aggregator: "$agg"
            cd Utils
            python3 BFTConfig.py "$nb_clients" "$nb_byz"
            cd ../
            bash ConsensusRunner.sh "$nb_clients" "$nb_clients" "$rounds" "$localHost" "$nb_byz" "$agg" "att" "Performance"

            # for att in ${attack[@]}; do
            #     mkdir -p "../Consensus_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy/"$att"
            #     echo running con with "$nb_byz" byzantine client. Accuracy test phase! Aggregator: "$agg" Attack: "$att"
            #     ((new_nb_clients = nb_clients - nb_byz))
            #     cd Utils
            #     python3 BFTConfig.py "$new_nb_clients" "0"
            #     cd ../
            #     bash ConsensusRunner.sh "$new_nb_clients" "$new_nb_clients" "$rounds" "$localHost" "$nb_byz" "$agg" "$att" "Accuracy"
            #     if [[ "$Heterogeneity" == "1" ]]
            #     then
            #         rm -rf "../Consensus_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy_$i/Heterogeneous/"$att"
            #         mv -f "../Consensus_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy/"$att" "../Consensus_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy_$i/Heterogeneous/
            #     else
            #         rm -rf "../Consensus_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy_$i/Homogeneous/"$att"
            #         mv -f "../Consensus_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy/"$att" "../Consensus_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy_$i/Homogeneous/
            #     fi
            # done
        fi
    done
done