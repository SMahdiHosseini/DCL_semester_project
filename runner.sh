server=54.224.69.3
clients=(35.171.165.230 54.174.73.157)

## set the addresses
server_local=$(ssh ubuntu@"$server" 'hostname -i' )
echo "server=$server_local" > main/ips.txt
i=0
d=1
for client in "${clients[@]}"
do
    ip=$(ssh ubuntu@"$client" 'hostname -i' )
    echo "client_$i=$ip" >> main/ips.txt
    i=$(( $i + $d ))
done

## install reqs
ssh ubuntu@"$server" 'bash -s' < installRequirements.sh &
for client in "${clients[@]}"
do
    ssh ubuntu@"$client" 'bash -s' < installRequirements.sh &
done

## send code to machines
cd ../
scp -r DCL_semester_project/main ubuntu@"$server":/home/ubuntu/

# cd ../silk/bin
# ./silk send --target-directory='../../' '('$server':3200)' ../../DCL_semester_project/main
# ./silk send --target-directory='../../' '('$server':3200)' ../../DCL_semester_project/library
for client in "${clients[@]}"
do
    scp -r DCL_semester_project/main ubuntu@"$client":/home/ubuntu/
#     ./silk send --target-directory='../../' '('$client':3200)' ../../DCL_semester_project/main
#     ./silk send --target-directory='../../' '('$client':3200)' ../../DCL_semester_project/library
done

echo "*********************"
echo "*********************" 
echo          Done! 
echo "*********************"
echo "*********************"
# for client in "${clients[@]}"
# do
#     ./silk run --cwd=../../DCL_semester_project/main '('$client':3200)' mkdir Data/ClientsDatasets
#     ./silk run --cwd=../../DCL_semester_project/main/Utils '('$client':3200)' python3 DataDistributer.py 10
# done

# ./silk run --cwd=../../DCL_semester_project/main "$server":3200 bash DistRunnser.sh fl test server 0 &

# i=0
# d=1
# for client in "${clients[@]}"
# do
#     ./silk run --cwd=../../DCL_semester_project/main "$client":3200 bash DistRunnser.sh fl test client $i &
#     i=$(( $i + $d ))
#     # echo $i
# done