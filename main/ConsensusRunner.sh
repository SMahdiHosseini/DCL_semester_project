#!/bin/bash          

if [ $# -lt 5 ]
then
    echo "usage: $0 <number of replicas> <number of clients> <number of rounds> <address> <byz_num> <aggregator>"
    exit
fi

cd /localhome/shossein/DCL_semester_project/library/build/install/library

for ((r=0; r<$1; r++))
do
    ./smartrun.sh bftsmart.FL.FLServer $r $2 $3 $4 $5 $6 > "./Results/res_$r.txt" &
done

sleep 3s

for ((c=0; c<$2; c++))
do
    ./smartrun.sh bftsmart.FL.FLClientInterface $c $4 $2 $5 $6&
done

wait
echo "Done!"