#!/bin/bash          

if [ $# -lt 8 ]
then
    echo "usage: $0 <number of replicas> <number of clients> <number of rounds> <address> <byz_num> <aggregator> <attack_name> <test>"
    exit
fi

# cd /localhome/shossein/DCL_semester_project/library/build/install/library
cd ../library/
./gradlew installDist
cd ../library/build/install/library
mkdir -p Results
chmod +x ./smartrun.sh

for ((r=0; r<$1; r++))
do
    ./smartrun.sh bftsmart.FL.FLServer $r $2 $3 $4 $5 $6 $7 $8 > "./Results/res_$r.txt" &
done

sleep 3s

for ((c=0; c<$2; c++))
do
    ./smartrun.sh bftsmart.FL.FLClientInterface $c $4 $2 $5 $6 $7 $8 &
done

wait
echo "Done!"