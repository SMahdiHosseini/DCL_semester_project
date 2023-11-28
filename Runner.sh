. global.config

ssh ubuntu@"$server" 'bash -s' < main/DistRunner.sh fl test server &
for client in "${clients[@]}"
do
    ssh ubuntu@"$client" 'bash -s' < main/DistRunner.sh fl test client 0 &
done