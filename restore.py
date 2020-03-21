#!/usr/bin/python3

#####################################################################
##                                                                 ##
## Script de restauration d'un serveur wordpress et MariaDB  V0.3  ##
##                                                                 ##
#####################################################################


#####################################################################
##                                                                 ##
##                    Importation des modules                      ##
##                                                                 ##
#####################################################################

import os # Diverses interfaces pour le système d'exploitation
import os.path # manipulation courante des chemins
import platform # modules pour vérifier la platform (Linux/Windows/Mac)
import datetime # Types de base pour la date et l'heure
import configparser # Configuration file parser
import docker # Docker
from datetime import date # 
import tarfile # 
from azure.storage.file import FileService # 
import sys #
import yaml # 

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

# # Récupération du short_id de la BDD via le dictionnaire #

# def get_short_id_container(name_container):
#  client = docker.from_env()
#  dict_conteneur = {} # dictionnaire vide des conteneurs
#  for container in client.containers.list(): # equivaut a docker ps
#    dict_conteneur[str(container.image)[9:-2]] = str(container.short_id) # récuperation du short_id et de l'image avec mise en forme dans le dictionnaire
#  return (dict_conteneur[name_container])

# # Récupération du Nom de l'image de la BDD du fichier docker-compose.yml #

# def get_database_name():
#   with open(repertoire_de_sauvegarde+"/docker-compose.yml",'r') as file:
#     doc = yaml.load(file, Loader=yaml.FullLoader)
#     txt = doc["services"]["db"]["image"]
#   return(txt)

# récupération d'un fichier de sauvegarde dans un répertoire de Microsoft AZURE

def get_choix_de_la_sauvegarde():
  list_file_save = file_service.list_directories_and_files(AZURE_REP_BKP)
  nb_save=1
  dict_save = {}
  for file_save in list_file_save:
    dict_save[nb_save] = str(file_save.name)
    print("N°"+str(nb_save)+":", file_save.name)
    nb_save += 1
  choix = input("Entrez le numéro de sauvegarde: N°:") # input choice
  return(dict_save[int(choix)])

# Sauvegarde sur AZURE #

# Autorisation d'accès au compte Microsoft AZURE

file_service = FileService(account_name=AZURE_CPT, account_key=AZURE_KEY)

print ("Choix du Numéro de sauvegarde: ?")
print ("")
BACKUP_DATE_SAVE=get_choix_de_la_sauvegarde()
print (BACKUP_DATE_SAVE)
file_service.get_file_to_path(AZURE_REP_BKP, BACKUP_DATE_SAVE, BACKUP_DATE_SAVE+'.tar.bz2', BACKUP_DATE_SAVE+'.tar.bz2')
file_service.get_file_to_path(AZURE_REP_BKP, BACKUP_DATE_SAVE, BACKUP_DATE_SAVE+'db.sql', BACKUP_DATE_SAVE+'db.sql')
print ('sauvegarde récupéré')

# Décompression de la sauvegarde des fichiers du serveur #

backup_bz2 = tarfile.open(repertoire_de_sauvegarde+'/'+BACKUP_DATE_SAVE+'.tar.bz2') # Emplacement de sauvegarde du fichier compressé (tar.bz2)
backup_bz2.extractall('/')
backup_bz2.close() #
print ('décompression faite')

# suppression du fichiers tar.bz2 sauvegarde récupéré

os.remove(repertoire_de_sauvegarde+"/save_"+str(BACKUP_DATE_SAVE)+".tar.bz2")

# Restauration de la base de donnée .sql



# suppression du fichiers tar.bz2 sauvegarde récupéré

#os.remove(repertoire_de_sauvegarde+"/save_"+str(BACKUP_DATE_SAVE)+"db.sql")