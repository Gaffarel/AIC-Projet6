#!/usr/bin/python3

#####################################################################
##                                                                 ##
##    Script de création d'un serveur wordpress et MariaDB  V0.1   ##
##                                                                 ##
#####################################################################


#####################################################################
##                                                                 ##
##                    Importation des modules                      ##
##                                                                 ##
#####################################################################

import os # Diverses interfaces pour le système d'exploitation
import os.path # manipulation courante des chemins
#import platform # modules pour vérifier la platform (Linux/Windows/Mac)
import datetime # Types de base pour la date et l'heure
import configparser # Configuration file parser
import shutil # aide à automatiser la copie des fichiers et des répertoires
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
config.read('P6_config.ini')
AZURE_CPT = config.get('config','azure_login')
AZURE_KEY = config.get('config','azure_key')
AZURE_REP_BKP = config.get('config','azure_bkp')
UserBDD = config.get('config','user_bdd')
MdpBDD = config.get('config','mdp_bdd')
NBjourDEretention = config.get('retention','nbjour')
repertoire_de_sauvegarde = config.get('repertoire','backup_repertoire')

############################## Temps ################################

BACKUP_DATE = date.today().strftime("%d-%m-%Y") # date d'aujourd'hui au format Jour/Mois/Année
BACKUP_DATE_OLD = (date.today()-datetime.timedelta(days=int(NBjourDEretention))).strftime("%d-%m-%Y") # date d'aujourd'hui - le nb de jour de rétention au format Jour/Mois/Année

############################# Fonction ##############################



#####################################################################
##                                                                 ##
##                    Programme de Création                        ##
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

# Copy des fichiers utiles au bon endroit #

repertoire = shutil.copy('/home/Projet6/AIC-Projet6/docker-compose.yml', repertoire_de_sauvegarde+'/')
print(repertoire)