. global.config

i=0
d=1
ssh ubuntu@"$server" 'bash --login DCL_semester_project/main/DistRunner.sh fl test server' &
sleep 2s
for client in "${clients[@]}"
do
    ssh ubuntu@"$client" 'bash --login DCL_semester_project/main/DistRunner.sh fl test client '$i' '&
    i=$(( $i + $d ))
    sleep 2s
done