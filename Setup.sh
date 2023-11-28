. global.config
## set the addresses
server_local=$(ssh ubuntu@"$server" 'hostname -i' )
echo "server=$server_local" > main/ips.config
i=0
d=1
for client in "${clients[@]}"
do
    ip=$(ssh ubuntu@"$client" 'hostname -i' )
    echo "client_$i=$ip" >> main/ips.config
    i=$(( $i + $d ))
done


echo "*********************"
echo "*********************" 
echo Local IP addresses are set! 
echo "*********************"
echo "*********************"

## send code to machines
cd ../
scp -r DCL_semester_project/main ubuntu@"$server":/home/ubuntu/ &
scp -r DCL_semester_project/library ubuntu@"$server":/home/ubuntu/ &

for client in "${clients[@]}"
do
    scp -r DCL_semester_project/main ubuntu@"$client":/home/ubuntu/ &
    scp -r DCL_semester_project/library ubuntu@"$client":/home/ubuntu/ &
done

wait

echo "*********************"
echo "*********************" 
echo   codes transferred!
echo "*********************"
echo "*********************"

## install reqs
cd DCL_semester_project/
ssh ubuntu@"$server" 'bash -s' < installRequirements.sh &
for client in "${clients[@]}"
do
    ssh ubuntu@"$client" 'bash -s' < installRequirements.sh &
done

wait

echo "*********************"
echo "*********************" 
echo          Done! 
echo "*********************"
echo "*********************"

# ./silk run --cwd=../../DCL_semester_project/main "$server":3200 bash DistRunnser.sh fl test server 0 &

# i=0
# d=1
# for client in "${clients[@]}"
# do
#     ./silk run --cwd=../../DCL_semester_project/main "$client":3200 bash DistRunnser.sh fl test client $i &
#     i=$(( $i + $d ))
#     # echo $i
# done