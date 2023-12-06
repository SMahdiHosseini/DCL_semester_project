#!/bin/bash          

if [ $# -lt 8 ]
then
    echo "usage: $0 <nb_clients> <server_address> <server_port> <nb_byz> <nb_rounds> <aggregator> <attack> <test>"
    exit
fi

python3 Server.py $1 $2 $3 $4 $5 $6 $7 $8 > "./Results/FL/server_res.txt" &

for ((c=0; c<$1; c++))
do
    python3 Client.py $1 $c $2 $3 $5 $4 $6 $7 $8 > "./Results/FL/res_$c.txt" &
    sleep 0.5s
done

wait
echo "Done!" 