#!/usr/bin/python3

#####################################################################
##                                                                 ##
##  Script de sauvegarde d'un serveur wordpress et MariaDB  V0.3a  ##
##                                                                 ##
#####################################################################


#####################################################################
##                                                                 ##
##                    Importation des modules                      ##
##                                                                 ##
#####################################################################

import os # Diverses interfaces pour le système d'exploitation
import os.path # manipulation courante des chemins
import datetime # Types de base pour la date et l'heure
import configparser # Configuration file parser
import docker # Docker
from datetime import date # 
import tarfile # 
from azure.storage.file import FileService # 

#####################################################################
##                                                                 ##
##                         Les Variables                           ##
##                                                                 ##
#####################################################################

################ Import du fichier de configuration #################

config = configparser.ConfigParser()
config.read('/home/backup/P6_config.ini')
AZURE_CPT = config.get('config','azure_login')
AZURE_KEY = config.get('config','azure_key')
AZURE_REP_BKP = config.get('config','azure_bkp')
UserBDD = config.get('config','user_bdd')
MdpBDD = config.get('config','mdp_bdd')
Nom_de_la_BDD = config.get('config','name_bdd')
NBjourDEretention = config.get('retention','nbjour')
repertoire_de_sauvegarde = config.get('repertoire','backup_repertoire')

############################## Temps ################################

BACKUP_DATE = date.today().strftime("%d-%m-%Y") # date d'aujourd'hui au format Jour/Mois/Année
BACKUP_DATE_OLD = (date.today()-datetime.timedelta(days=int(NBjourDEretention))).strftime("%d-%m-%Y") # date d'aujourd'hui - le nb de jour de rétention au format Jour/Mois/Année

############################# Fonction ##############################



#####################################################################
##                                                                 ##
##                    Programme de Backup                          ##
##                                                                 ##
#####################################################################

# Vérifier si le répertoire de sauvegarde existe ou non #

if os.path.exists(repertoire_de_sauvegarde) :
     print("Chemin " , repertoire_de_sauvegarde, " existe")
else:
     os.makedirs(repertoire_de_sauvegarde, exist_ok=True)
     print("Chemin " , repertoire_de_sauvegarde, " n'existe pas")

print(BACKUP_DATE)
print(BACKUP_DATE_OLD)

# Récupération du short ID et des images du conteneurs dans un dictionnaire #

client = docker.from_env()
dict_conteneur = {} # dictionnaire vide des conteneurs
for container in client.containers.list(): # equivaut a docker ps
  dict_conteneur[str(container.image)[8:-1]] = str(container.short_id) # récuperation du short_id et de l'image avec mise en forme dans le dictionnaire
#print(conteneur)
print({dict_conteneur["'mariadb:10.3.18'"]})

# Dump de la base de donnée MariaDB #

client = docker.from_env()
#container = client.containers.get('33a595d494')
container = client.containers.get(dict_conteneur["'mariadb:10.3.18'"])
res = str((container.exec_run("mysqldump -u "+UserBDD+" -p"+MdpBDD+" "+Nom_de_la_BDD)).output, 'utf-8')
#print(res)
fichier = open(repertoire_de_sauvegarde+"/save_"+str(BACKUP_DATE)+"db.sql","w")
fichier.write(res)
fichier.close()

# Compréssion et sauvegarde des fichiers du serveur #

backup_bz2 = tarfile.open(repertoire_de_sauvegarde+'/save_'+str(BACKUP_DATE)+'.tar.bz2','w:bz2') # Emplacement de sauvegarde du fichier compressé (tar.bz2)
backup_bz2.add('/var/lib/docker/volumes/backup_wp/') # sauvegarde du volumes wordpress
backup_bz2.add('/etc/network/interfaces') #
backup_bz2.add('/etc/resolv.conf') #
backup_bz2.add('/etc/hosts') #
backup_bz2.add('/etc/hostname') #
backup_bz2.add('/var/log/') #
backup_bz2.add('/var/spool/cron/crontabs/') #
backup_bz2.add(repertoire_de_sauvegarde+'/log/') #
backup_bz2.add(repertoire_de_sauvegarde+'/save_'+str(BACKUP_DATE)+'db.sql') #
backup_bz2.add(repertoire_de_sauvegarde+'/.env') #
backup_bz2.add(repertoire_de_sauvegarde+'/docker-compose.yml') #
backup_bz2.close() # 

# Sauvegarde sur AZURE #

# Autorisation d'accès au compte Microsoft AZURE
file_service = FileService(account_name=AZURE_CPT, account_key=AZURE_KEY)

# Création du répertoire: backup6
file_service.create_share(AZURE_REP_BKP)

# Création d'un sous-repertoire: save_date du jour
file_service.create_directory(AZURE_REP_BKP,'save_'+str(BACKUP_DATE))

# copy des fichiers de sauvegarde sur un repertoire Microsoft AZURE

file_service.create_file_from_path(AZURE_REP_BKP,'save_'+str(BACKUP_DATE),'save_'+str(BACKUP_DATE)+'db.sql',repertoire_de_sauvegarde+'/save_'+str(BACKUP_DATE)+'db.sql')
file_service.create_file_from_path(AZURE_REP_BKP,'save_'+str(BACKUP_DATE),'save_'+str(BACKUP_DATE)+'.tar.bz2',repertoire_de_sauvegarde+'/save_'+str(BACKUP_DATE)+'.tar.bz2')

# suppression des fichiers de sauvegarde

os.remove(repertoire_de_sauvegarde+"/save_"+str(BACKUP_DATE)+"db.sql")
os.remove(repertoire_de_sauvegarde+"/save_"+str(BACKUP_DATE)+".tar.bz2")

# Liste des fichiers ou repertoires de Microsoft AZURE

list_file = file_service.list_directories_and_files(AZURE_REP_BKP)
for file_or_dir in list_file:
  if ('save_'+str(BACKUP_DATE_OLD)) in file_or_dir.name:
    file_service.delete_file(AZURE_REP_BKP,'save_'+str(BACKUP_DATE_OLD),'save_'+str(BACKUP_DATE_OLD)+'db.sql')
    file_service.delete_file(AZURE_REP_BKP,'save_'+str(BACKUP_DATE_OLD),'save_'+str(BACKUP_DATE_OLD)+'.tar.bz2')
    file_service.delete_directory(AZURE_REP_BKP,'save_'+str(BACKUP_DATE_OLD))
  else:
    print(file_or_dir.name)
