. global.config


ssh ubuntu@"$server" 'killall python3' &
for client in "${clients[@]}"
do
    ssh ubuntu@"$client" 'killall python3' &
done

wait

for client in "${clients[@]}"
do
    ssh ubuntu@"$client" 'killall java' &
done

wait

echo "*********************"
echo "*********************" 
echo "  Termonation Done!  "
echo "*********************"
echo "*********************"