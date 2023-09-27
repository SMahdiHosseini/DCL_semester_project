#!/bin/bash          

if [ $# -lt 3 ]
then
    echo "usage: $0 <number of clients>"
    exit
fi

start python Server.py

for i in `seq $2`
do
    start python Client.py $i
done