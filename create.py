#!/usr/bin/python3

#####################################################################
##                                                                 ##
##   Script de création d'un serveur wordpress avec MariaDB V0.8e  ##
##               avec docker-compose sur DEBIAN 10.2               ##
##                                                                 ##
#####################################################################


#####################################################################
##                                                                 ##
##  Importation des modules et installation des modules spéciaux   ##
##                                                                 ##
#####################################################################

import os # Diverses interfaces pour le système d'exploitation
#import os.path # manipulation courante des chemins
import logging #
from pathlib import Path #
#import datetime # Types de base pour la date et l'heure
import configparser # Configuration file parser
import shutil # aide à automatiser la copie des fichiers et des répertoires
import docker # Docker
#from datetime import date #
#import tarfile #
#from azure.storage.file import FileService #

####################### Nom du fichier de LOG #######################

logging.basicConfig(filename='/var/log/create.log',level=logging.DEBUG)

############# Installation des modules supplémentaires ##############

os.system("apt install python3-pip -y") # installation de PIP pour python 3
os.system("pip3 install -r requirements.txt") # installation de la liste des modules suplèmentaires via le fichier requirements.txt

############## Présence des Fichiers de configuration ###############

# Vérifier si le fichier .env existe ou non #

try:
    (Path('.env')).resolve(strict=True)
    print("Fichier .env présent")
    logging.info("Fichier .env présent")
except FileNotFoundError:
    print("Fichier .env manquant")
    logging.error("Fichier .env manquant")
    exit(1)

# Vérifier si le fichier P6_config.ini existe ou non #

try:
    (Path('P6_config.ini')).resolve(strict=True)
    print("Fichier P6_config.ini présent")
    logging.info("Fichier P6_config.ini présent")
except FileNotFoundError:
    print("Fichier P6_config.ini manquant")
    logging.error("Fichier P6_config.ini manquant")
    exit(1)

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

# Déplacement fichiers utiles dans le repertoire de sauvegarde #

repertoire = shutil.copy('docker-compose.yml', repertoire_de_sauvegarde+'/')
repertoire = shutil.copy('.env', repertoire_de_sauvegarde+'/')
repertoire = shutil.copy('P6_config.ini', repertoire_de_sauvegarde+'/')
repertoire = shutil.copy('SafetyWpress.py', repertoire_de_sauvegarde+'/')

# Modification des fichiers save.py et create.py pour les rendre exécutables #

os.chmod(repertoire_de_sauvegarde+"/SafetyWpress.py", 751)

#####################################################################
##                                                                 ##
##   Programme d'installation de Docker Engine et Docker-Compose   ##
##                                                                 ##
#####################################################################


########################### Docker Engine ###########################

os.system("apt-get update")

os.system("apt-get install -y apt-transport-https ca-certificates curl gnupg2 software-properties-common") 

os.system("curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -")

os.system("apt-key fingerprint 0EBFCD88")

os.system('add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"')

os.system("apt-get update")

os.system("apt-get install -y docker-ce docker-ce-cli containerd.io")

os.system("docker --version")

########################## DOCKER-COMPOSE ###########################

os.system('curl -L "https://github.com/docker/compose/releases/download/1.25.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose') 

os.chmod("/usr/local/bin/docker-compose", 751)

os.system("docker-compose --version")

#####################################################################
##                                                                 ##
##          Installation des images Wordpress et MariaDB           ##
##               via le fichier docker-compose.yml                 ##
##                                                                 ##
#####################################################################

#os.system("docker-compose -f /srv/backup/docker-compose.yml up -d")
os.system("docker-compose -f "+repertoire_de_sauvegarde+"/docker-compose.yml up -d") 
