. global.config


ssh ubuntu@"$server" 'rm -rf DCL_semester_project' &
for client in "${clients[@]}"
do
    ssh ubuntu@"$client" 'rm -rf DCL_semester_project' &
done

wait

echo "*********************"
echo "*********************" 
echo "       Done!         "
echo "*********************"
echo "*********************"

# . global.config


# ssh ubuntu@"$server" 'killall python3' &
# for client in "${clients[@]}"
# do
#     ssh ubuntu@"$client" 'killall python3' &
# done

# wait

# echo "*********************"
# echo "*********************" 
# echo "       Done!         "
# echo "*********************"
# echo "*********************"