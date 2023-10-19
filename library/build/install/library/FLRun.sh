#!/bin/bash          

if [ $# -lt 3 ]
then
    echo "usage: $0 <number of replicas> <number of clients> <number of rounds>"
    exit
fi

for ((r=0; r<$1; r++))
do
    ./smartrun.sh bftsmart.FL.FLServer $r $2 $3 localhost > "./Results/res_$r.txt" &
done

sleep 3s

for ((c=0; c<$2; c++))
do
    ./smartrun.sh bftsmart.FL.FLClientInterface $c localhost &
done

wait
echo "Done!"