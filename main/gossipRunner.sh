#!/bin/bash          

if [ $# -lt 8 ]
then
    echo "usage: $0 <nb_clients> <server_address> <server_port> <nb_byz> <nb_rounds> <aggregator> <attack> <test>"
    exit
fi

for ((c=0; c<$1; c++))
do
    python3 Client_Gossip.py $c $1 $2 $3 $4 $5 $6 $7 $8 > "./Results/gossip/res_$c.txt" &
    sleep 2s
done

wait
echo "Done!" 