#!/bin/bash          

if [ $# -lt 1 ]
then
    echo "usage: $0 <number of clients>"
    exit
fi

python3 Server.py > "../FL_res/Output.txt" &

for ((c=0; c<$1; c++))
do
    python3 Client.py $c > "./Results/FL/res_$c.txt" &
done

wait
echo "Done!" 