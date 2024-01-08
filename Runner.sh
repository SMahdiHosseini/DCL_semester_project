function add_latency {
    echo "Adding latency to the network..."
    i=0
    d=1
    for client in "${clients[@]}"
    do
        r=$(cat latency.txt | grep "client_$i" | cut -d'=' -f2)
        ssh ubuntu@"$client" 'sudo tc qdisc add dev ens5 root netem delay '"$r"'ms'
        i=$(( $i + $d ))
    done
}

function remove_latency {
    echo "Removing latency from the network..."
    i=0
    d=1
    for client in "${clients[@]}"
    do
        ssh ubuntu@"$client" 'sudo tc qdisc del dev ens5 root 2>/dev/null'
        i=$(( $i + $d ))
    done
}

function transfer_files {
    if [[ "$1" == "fl" || "$1" == "all" ]]
    then
        mkdir -p "./FL_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance_$j
        rm -rf "./FL_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance_$j/*
        # mkdir -p "./FL_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy

        scp ubuntu@$server:/home/ubuntu/DCL_semester_project/FL_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance/server.txt  ./FL_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance_$j &
        scp ubuntu@$server:/home/ubuntu/DCL_semester_project/main/Results/FL/server_res.txt  ./main/Results/FL &
        i=0
        d=1
        for client in "${clients[@]}"
        do
            scp ubuntu@$client:/home/ubuntu/DCL_semester_project/FL_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance/$i.txt  ./FL_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance_$j &
            scp ubuntu@$client:/home/ubuntu/DCL_semester_project/main/Results/FL/res_$i.txt  ./main/Results/FL &
            i=$(( $i + $d ))
        done  
    fi

    if [[ "$1" == "p2p" || "$1" == "all" ]]
    then
        mkdir -p "./Gossip_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance_$j
        rm -rf "./Gossip_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance_$j/*
        # mkdir -p "./Gossip_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy
        i=0
        d=1
        for client in "${clients[@]}"
        do
            scp ubuntu@$client:/home/ubuntu/DCL_semester_project/Gossip_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance/$i.txt  ./Gossip_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance_$j &
            scp ubuntu@$client:/home/ubuntu/DCL_semester_project/main/Results/gossip/res_$i.txt  ./main/Results/gossip &
            i=$(( $i + $d ))
        done  
    fi

    if [[ "$1" == "con" || "$1" == "all" ]]
    then
        mkdir -p "./Consensus_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance_$j
        rm -rf "./Consensus_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance_$j/*
        # mkdir -p "./Consensus_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy
        i=0
        d=1
        for client in "${clients[@]}"
        do
            scp ubuntu@$client:/home/ubuntu/DCL_semester_project/Consensus_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance/$i.txt  ./Consensus_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance_$j &
            scp ubuntu@$client:/home/ubuntu/DCL_semester_project/Consensus_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance/server_$i.txt  ./Consensus_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance_$j &
            scp ubuntu@$client:/home/ubuntu/DCL_semester_project/Consensus_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance/recevdParamIds.txt  ./Consensus_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance_$j &
            scp ubuntu@$client:/home/ubuntu/DCL_semester_project/library/build/install/library/Results/res_$i.txt  ./library/build/install/library/Results & 
            i=$(( $i + $d ))
        done  
    fi
}

function read_bytes {
    recvd=$(ssh ubuntu@"$server" 'cat /sys/class/net/ens5/statistics/rx_bytes')
    send=$(ssh ubuntu@"$server" 'cat /sys/class/net/ens5/statistics/tx_bytes')
    echo "server=$recvd, $send"
    i=0
    d=1
    for client in "${clients[@]}"
    do
        recvd=$(ssh ubuntu@"$client" 'cat /sys/class/net/ens5/statistics/rx_bytes')
        send=$(ssh ubuntu@"$client" 'cat /sys/class/net/ens5/statistics/tx_bytes')
        echo "client_$i=$recvd, $send"
        i=$(( $i + $d ))
    done
}

if [ $# -lt 2 ]
then
    echo "usage: $0 <senario> <config>"
    exit
fi


if [[ "$2" == "main" ]];
then 
    . main/main.config
elif [[ "$2" == "test" ]];
then 
    . main/test.config
else
    echo "Worng config file!"
    exit
fi

if [[ "$1" != "con" && "$1" != "p2p" && "$1" != "fl" ]]
then
    echo "Wrong senario!"
    exit
fi

. global.config

## Performance Test
for j in {3..3}
do
    for agg in ${aggregator[@]}; do
        read_bytes > main/net_$1.txt

        add_latency

        if [[ "$1" == "fl" ]]
        then
            ssh ubuntu@"$server" 'bash --login DCL_semester_project/main/DistRunner.sh '$1' '$2' '$agg' 'att' 'Performance' server' &
        fi

        if [[ "$1" == "con" ]]
        then
            i=0
            d=1
            for client in "${clients[@]}"
            do
                ssh ubuntu@"$client" 'bash --login DCL_semester_project/main/DistRunner.sh '$1' '$2' '$agg' 'att' 'Performance' server '$i' '&
                i=$(( $i + $d ))
            done
            sleep 15s
        fi

        sleep 5s
        i=0
        d=1
        for client in "${clients[@]}"
        do
            ssh ubuntu@"$client" 'bash --login DCL_semester_project/main/DistRunner.sh '$1' '$2' '$agg' 'att' 'Performance' client '$i' '&
            i=$(( $i + $d ))
            if [[ "$1" == "con" ]]
            then
                sleep 1s
            else
                sleep 3s
            fi
        done

        sleep 45s
        # wait

        remove_latency

        read_bytes >> main/net_$1.txt

        bash Terminate.sh

        echo "*********************"
        echo "*********************" 
        echo "     $agg Done!      "
        echo "*********************"
        echo "*********************"

        transfer_files $1 $agg $j

        wait
        echo "*********************"
        echo "*********************" 
        echo "   Files Tranfered!  "
        echo "*********************"
        echo "*********************"
    done
done
## Accuracy Test
# for agg in ${aggregator[@]}; do
#     for att in ${attack[@]};do
#         if [[ "$1" == "fl" ]]
#         then
#             ssh ubuntu@"$server" 'bash --login DCL_semester_project/main/DistRunner.sh '$1' '$2' '$agg' '$att' 'Accuracy' server' &
#         fi

#         if [[ "$1" == "con" ]]
#         then
#             i=0
#             d=1
#             for client in "${clients[@]}"
#             do
#                 ssh ubuntu@"$client" 'bash --login DCL_semester_project/main/DistRunner.sh '$1' '$2' '$agg' '$att' 'Accuracy' server '$i' '&
#                 i=$(( $i + $d ))
#             done
#             sleep 15s
#         fi

#         sleep 5s
#         i=0
#         d=1
#         for client in "${clients[@]}"
#         do
#             ssh ubuntu@"$client" 'bash --login DCL_semester_project/main/DistRunner.sh '$1' '$2' '$agg' '$att' 'Accuracy' client '$i' '&
#             i=$(( $i + $d ))
#             if [[ "$1" == "con" ]]
#             then
#                 sleep 1s
#             else
#                 sleep 3s
#             fi
#         done

#         # sleep 90s
#         # bash Terminate.sh
#         wait

#         echo "*********************"
#         echo "*********************" 
#         echo "     $agg Done!      "
#         echo "*********************"
#         echo "*********************"
#         if [[ "$1" == "fl" || "$1" == "all" ]]
#         then
#             mkdir -p "./FL_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance
#             mkdir -p "./FL_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy/"$att"

#             i=0
#             d=1
#             for client in "${clients[@]}"
#             do
#                 scp ubuntu@$client:/home/ubuntu/DCL_semester_project/FL_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Accuracy/$att/$i.txt  ./FL_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Accuracy/$att &
#                 i=$(( $i + $d ))
#             done  
#         fi

#         if [[ "$1" == "p2p" || "$1" == "all" ]]
#         then
#             mkdir -p "./Gossip_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance
#             mkdir -p "./Gossip_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy/$att
#             i=0
#             d=1
#             for client in "${clients[@]}"
#             do
#                 scp ubuntu@$client:/home/ubuntu/DCL_semester_project/Gossip_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Accuracy/$att/$i.txt  ./Gossip_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Accuracy/$att &
#                 i=$(( $i + $d ))
#             done  
#         fi

#         if [[ "$1" == "con" || "$1" == "all" ]]
#         then
#             mkdir -p "./Consensus_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance
#             mkdir -p "./Consensus_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy/$att
#             i=0
#             d=1
#             for client in "${clients[@]}"
#             do
#                 scp ubuntu@$client:/home/ubuntu/DCL_semester_project/Consensus_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Accuracy/$att/$i.txt  ./Consensus_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Accuracy/$att &
#                 i=$(( $i + $d ))
#             done  
#         fi
#         wait
#         echo "*********************"
#         echo "*********************" 
#         echo "   Files Tranfered!  "
#         echo "*********************"
#         echo "*********************"
#     done
# done

echo "*********************"
echo "*********************" 
echo "       Done!         "
echo "*********************"
echo "*********************"