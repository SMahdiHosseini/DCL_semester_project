git clone https://github.com/SMahdiHosseini/DCL_semester_project.git
cd DCL_semester_project
. main/$1.config
mkdir main/Data/
mkdir main/Data/ClientsDatasets
cd main/Utils
# python3 DataDistributer.py $nb_clients
python3 Setup.py $nb_clients