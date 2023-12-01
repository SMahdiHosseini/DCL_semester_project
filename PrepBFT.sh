. main/$1.config
cd main/Utils
python3 BFTConfig.py $nb_clients $nb_byz
cd ../../library
rm build/install/library/config/currentView
./gradlew installDist
mkdir -p build/install/library/Results
cd build/install/library
chmod +x ./smartrun.sh