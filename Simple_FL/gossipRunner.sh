#!/bin/bash          

if [ $# -lt 1 ]
then
    echo "usage: $0 <number of clients>"
    exit
fi

for ((c=0; c<$1; c++))
do
    python3 Client_Gossip.py $c > "./Results/gossip/res_$c.txt" &
    sleep 1s
done

wait
echo "Done!" 