git clone https://github.com/SMahdiHosseini/DCL_semester_project.git
cd DCL_semester_project
. main/test.config
mkdir main/Data/
mkdir main/Data/ClientsDatasets
cd main/Utils
python3 DataDistributer.py $nb_clients
# cd ../../../
# git clone https://github.com/Blockchain-Benchmarking/silk.git
# cd silk
# sudo wget -c https://dl.google.com/go/go1.14.2.linux-amd64.tar.gz -O - | sudo tar -xz -C /usr/local
# export PATH=$PATH:/usr/local/go/bin
# source ~/.profile
# make all
# cd bin
# ./silk server