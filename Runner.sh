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
for j in {1..1}
do
    for agg in ${aggregator[@]}; do
        recvd=$(ssh ubuntu@"$server" 'cat /sys/class/net/ens5/statistics/rx_bytes')
        send=$(ssh ubuntu@"$server" 'cat /sys/class/net/ens5/statistics/tx_bytes')
        echo "server=$recvd, $send" > main/net_$1.txt
        i=0
        d=1
        for client in "${clients[@]}"
        do
            recvd=$(ssh ubuntu@"$client" 'cat /sys/class/net/ens5/statistics/rx_bytes')
            send=$(ssh ubuntu@"$client" 'cat /sys/class/net/ens5/statistics/tx_bytes')
            echo "client_$i=$recvd, $send" >> main/net_$1.txt
            i=$(( $i + $d ))
        done

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

        sleep 140s

        recvd=$(ssh ubuntu@"$server" 'cat /sys/class/net/ens5/statistics/rx_bytes')
        send=$(ssh ubuntu@"$server" 'cat /sys/class/net/ens5/statistics/tx_bytes')
        echo "server=$recvd, $send" >> main/net_$1.txt
        i=0
        d=1
        for client in "${clients[@]}"
        do
            recvd=$(ssh ubuntu@"$client" 'cat /sys/class/net/ens5/statistics/rx_bytes')
            send=$(ssh ubuntu@"$client" 'cat /sys/class/net/ens5/statistics/tx_bytes')
            echo "client_$i=$recvd, $send" >> main/net_$1.txt
            i=$(( $i + $d ))
        done

        bash Terminate.sh
        # wait

        echo "*********************"
        echo "*********************" 
        echo "     $agg Done!      "
        echo "*********************"
        echo "*********************"
        if [[ "$1" == "fl" || "$1" == "all" ]]
        then
            mkdir -p "./FL_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance_$j
            rm -rf "./FL_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance_$j/*
            # mkdir -p "./FL_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy

            scp ubuntu@$server:/home/ubuntu/DCL_semester_project/FL_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance/server.txt  ./FL_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance_$j &
            i=0
            d=1
            for client in "${clients[@]}"
            do
                scp ubuntu@$client:/home/ubuntu/DCL_semester_project/FL_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance/$i.txt  ./FL_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance_$j &
                i=$(( $i + $d ))
            done  
        fi

        if [[ "$1" == "p2p" || "$1" == "all" ]]
        then
            mkdir -p "./Gossip_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance
            rm -rf "./Gossip_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance/*
            # mkdir -p "./Gossip_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy
            i=0
            d=1
            for client in "${clients[@]}"
            do
                scp ubuntu@$client:/home/ubuntu/DCL_semester_project/Gossip_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance/$i.txt  ./Gossip_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance_$j &
                i=$(( $i + $d ))
            done  
        fi

        if [[ "$1" == "con" || "$1" == "all" ]]
        then
            mkdir -p "./Consensus_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance
            rm -rf "./Consensus_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance/*
            # mkdir -p "./Consensus_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy
            i=0
            d=1
            for client in "${clients[@]}"
            do
                scp ubuntu@$client:/home/ubuntu/DCL_semester_project/Consensus_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance/$i.txt  ./Consensus_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance_$j &
                scp ubuntu@$client:/home/ubuntu/DCL_semester_project/Consensus_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance/server_$i.txt  ./Consensus_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance_$j &
                i=$(( $i + $d ))
            done  
        fi
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