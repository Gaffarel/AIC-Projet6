#!/usr/bin/python3

#####################################################################
##                                                                 ##
##    Script de création d'un serveur wordpress et MariaDB  V0.6   ##
##                                                                 ##
#####################################################################


#####################################################################
##                                                                 ##
##  Importation des modules et installation des modules spéciaux   ##
##                                                                 ##
#####################################################################

import os # Diverses interfaces pour le système d'exploitation
import os.path # manipulation courante des chemins

############# Installation des modules supplémentaires ##############

os.system("apt install python3-pip -y") # installation de PIP pour python 3
os.system("pip3 install docker") # installation du module DOCKER
os.system("pip3 install azure-storage-file") # installation du module AZURE

############################# Fonction ##############################

# Vérifier si le fichier .env existe ou non #

if os.path.isfile('/home/AIC-Projet6/.env'):
  print("Fichier .env présent")
else:
  print("Fichier .env absent")
  exit(1)

# Vérifier si le fichier P6_config.ini existe ou non #

if os.path.isfile('/home/AIC-Projet6/P6_config.ini'):
  print("Fichier P6_config.ini présent")
else:
  print("Fichier P6_config.ini absent")
  exit(1)

import datetime # Types de base pour la date et l'heure
import configparser # Configuration file parser
import shutil # aide à automatiser la copie des fichiers et des répertoires
import docker # Docker
from datetime import date #
import tarfile #
from azure.storage.file import FileService #
#import subprocess

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

#bash : ou subprocess : pip3 install -r requirements.txt

#####################################################################
##                                                                 ##
##                  Programme de Préparation                       ##
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

# Copy des fichiers utiles dans le repertoire de sauvegarde #

repertoire = shutil.copy('/home/AIC-Projet6/docker-compose.yml', repertoire_de_sauvegarde+'/')
repertoire = shutil.copy('/home/AIC-Projet6/.env', repertoire_de_sauvegarde+'/')
repertoire = shutil.copy('/home/AIC-Projet6/P6_config.ini', repertoire_de_sauvegarde+'/')
repertoire = shutil.copy('/home/AIC-Projet6/save.py', repertoire_de_sauvegarde+'/')
repertoire = shutil.copy('/home/AIC-Projet6/restore.py', repertoire_de_sauvegarde+'/')

# Modification des fichiers save.py et create.py pour les rendres exécutables #

os.chmod(repertoire_de_sauvegarde+"/save.py", 751)
os.chmod(repertoire_de_sauvegarde+"/restore.py", 751)

#####################################################################
##                                                                 ##
##              Programme d'installation de docker                 ##
##                                                                 ##
#####################################################################


########################### Docker Engine ###########################

os.system("apt-get update") # apt-get update

# apt-get install -y \
#     apt-transport-https \
#     ca-certificates \
#     curl \
#     gnupg2 \
#     software-properties-common

os.system("apt-get install -y apt-transport-https ca-certificates curl gnupg2 software-properties-common") 

os.system("curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -") # curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
#subprocess.call(["curl"," -fsSL https://download.docker.com/linux/debian/gpg"," | ","apt-key add -"])

os.system("apt-key fingerprint 0EBFCD88") # apt-key fingerprint 0EBFCD88

# add-apt-repository \
#    "deb [arch=amd64] https://download.docker.com/linux/debian \
#    $(lsb_release -cs) \
#    stable"

os.system('add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"')

os.system("apt-get update") # apt-get update

os.system("apt-get install -y docker-ce docker-ce-cli containerd.io") # apt-get install -y docker-ce docker-ce-cli containerd.io

########################## DOCKER-COMPOSE ###########################

#curl -L "https://github.com/docker/compose/releases/download/1.25.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

#os.chmod("/usr/local/bin/docker-compose", 751) #chmod +x /usr/local/bin/docker-compose

#docker-compose --version

