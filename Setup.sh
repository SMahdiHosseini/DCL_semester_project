. global.config
# set the addresses
if [[ ! -z "$server" ]]
then
    server_local=$(ssh ubuntu@"$server" 'hostname -i' ) 
    echo "server=$server_local" > main/ips.config
else
    echo "server=0.0.0.0" > main/ips.config
fi
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

if [[ ! -z "$server" ]]
then
    scp -r installRequirements.sh ubuntu@"$server":/home/ubuntu/ &
fi

for client in "${clients[@]}"
do
    scp -r installRequirements.sh ubuntu@"$client":/home/ubuntu/ &
done

wait

if [[ ! -z "$server" ]]
then
    ssh ubuntu@"$server" 'bash --login installRequirements.sh' &
fi

for client in "${clients[@]}"
do
    ssh ubuntu@"$client" 'bash --login installRequirements.sh' &
done

wait

echo "*********************"
echo "*********************" 
echo Requirements Installed!
echo "*********************"
echo "*********************"

## send code to machines
cd ../
if [[ ! -z "$server" ]]
then
    scp -r DCL_semester_project/main/ips.config ubuntu@"$server":/home/ubuntu/DCL_semester_project/main &
fi

for client in "${clients[@]}"
do
    scp -r DCL_semester_project/main/ips.config ubuntu@"$client":/home/ubuntu/DCL_semester_project/main &
done

wait

echo "*********************"
echo "*********************" 
echo   codes transferred!
echo "*********************"
echo "*********************"

echo "*********************"
echo "*********************" 
echo          Done! 
echo "*********************"
echo "*********************"