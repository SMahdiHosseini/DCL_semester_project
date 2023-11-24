server=16.16.65.152
client_0=16.171.235.51

cd ../silk/bin

./silk run --cwd=../../DCL_semester_project/main "$server":3200 bash DistRunnser.sh fl test server 0 &

./silk run --cwd=../../DCL_semester_project/main "$client_0":3200 bash DistRunnser.sh fl test client 0 &