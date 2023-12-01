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

for agg in ${aggregator[@]}; do
    if [[ "$1" == "fl" ]]
    then
        ssh ubuntu@"$server" 'bash --login DCL_semester_project/main/DistRunner.sh '$1' '$2' '$agg' server' &
    fi

    if [[ "$1" == "con" ]]
    then
        i=0
        d=1
        for client in "${clients[@]}"
        do
            ssh ubuntu@"$client" 'bash --login DCL_semester_project/main/DistRunner.sh '$1' '$2' '$agg' server '$i' '&
            i=$(( $i + $d ))
        done
        sleep 15s
    fi

    sleep 3s
    i=0
    d=1
    for client in "${clients[@]}"
    do
        ssh ubuntu@"$client" 'bash --login DCL_semester_project/main/DistRunner.sh '$1' '$2' '$agg' client '$i' '&
        i=$(( $i + $d ))
        if [[ "$1" == "con" ]]
        then
            sleep 1s
        else
            sleep 3s
        fi
    done

    sleep 30s
    bash Terminate.sh
    # wait

    echo "*********************"
    echo "*********************" 
    echo "     $agg Done!      "
    echo "*********************"
    echo "*********************"

done

echo "*********************"
echo "*********************" 
echo "       Done!         "
echo "*********************"
echo "*********************"

for agg in ${aggregator[@]}; do
    if [[ "$1" == "fl" || "$1" == "all" ]]
    then
        mkdir -p "./FL_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance
        mkdir -p "./FL_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy

        scp ubuntu@$server:/home/ubuntu/DCL_semester_project/FL_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance/server.txt  ./FL_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance &
        i=0
        d=1
        for client in "${clients[@]}"
        do
            scp ubuntu@$client:/home/ubuntu/DCL_semester_project/FL_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance/$i.txt  ./FL_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance &
            i=$(( $i + $d ))
        done  
    fi

    if [[ "$1" == "p2p" || "$1" == "all" ]]
    then
        mkdir -p "./Gossip_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance
        mkdir -p "./Gossip_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy
        i=0
        d=1
        for client in "${clients[@]}"
        do
            scp ubuntu@$client:/home/ubuntu/DCL_semester_project/Gossip_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance/$i.txt  ./Gossip_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance &
            i=$(( $i + $d ))
        done  
    fi

    if [[ "$1" == "con" || "$1" == "all" ]]
    then
        mkdir -p "./Consensus_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Performance
        mkdir -p "./Consensus_res/""$agg"/ncl_"$nb_clients"/nbyz_"$nb_byz"/Accuracy
        i=0
        d=1
        for client in "${clients[@]}"
        do
            scp ubuntu@$client:/home/ubuntu/DCL_semester_project/Consensus_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance/$i.txt  ./Consensus_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance &
            scp ubuntu@$client:/home/ubuntu/DCL_semester_project/Consensus_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance/server_$i.txt  ./Consensus_res/$agg/ncl_$nb_clients/nbyz_$nb_byz/Performance &
            i=$(( $i + $d ))
        done  
    fi
done
echo "*********************"
echo "*********************" 
echo "   Files Tranfered!  "
echo "*********************"
echo "*********************"