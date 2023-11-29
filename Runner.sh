. global.config

i=0
d=1
ssh ubuntu@"$server" 'bash DCL_semester_project/main/DistRunner.sh fl test server' &
for client in "${clients[@]}"
do
    ssh ubuntu@"$client" 'bash DCL_semester_project/main/DistRunner.sh fl test client '$i' '&
    i=$(( $i + $d ))
done