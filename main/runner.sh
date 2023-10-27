#!/bin/bash          

if [ $# -lt 1 ]
then
    echo "usage: $0 <number of clients>"
    exit
fi

python3 Server.py > "./Results/FL/server_res.txt" &

for ((c=0; c<$1; c++))
do
    python3 Client.py $c > "./Results/FL/res_$c.txt" &
    sleep 2s
done

wait
echo "Done!" 