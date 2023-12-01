. DCL_semester_project/main/$1.config
cd DCL_semester_project/main/Utils
python3 BFTConfig.py $nb_clients $nb_byz
cd ../../library
rm build/install/library/config/currentView
./gradlew installDist
mkdir -p build/install/library/Results
cd build/install/library
chmod +x ./smartrun.sh