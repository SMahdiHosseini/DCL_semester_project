#!/bin/bash          

if [ $# -lt 7 ]
then
    echo "usage: $0 <nb_clients> <server_address> <server_port> <nb_byz> <nb_rounds> <aggregator> <attack>"
    exit
fi

python3 Server.py $1 $2 $3 $4 $5 $6 $7 > "./Results/FL/server_res.txt" &

for ((c=0; c<$1; c++))
do
    python3 Client.py $1 $c $2 $3 $5 $4 $6> "./Results/FL/res_$c.txt" &
    sleep 2s
done

wait
echo "Done!" 