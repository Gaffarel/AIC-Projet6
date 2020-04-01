#!/usr/bin/python3

#####################################################################
##                                                                 ##
##   Script de création d'un serveur wordpress avec MariaDB V0.9a  ##
##               avec docker-compose sur DEBIAN 10.2               ##
##                                                                 ##
#####################################################################


#####################################################################
##                                                                 ##
##  Importation des modules et installation des modules spéciaux   ##
##                                                                 ##
#####################################################################

import os # Diverses interfaces pour le système d'exploitation
import logging #
from pathlib import Path #
import configparser # Configuration file parser
import shutil # aide à automatiser la copie des fichiers et des répertoires

####################### Nom du fichier de LOG #######################

logging.basicConfig(filename='/var/log/create.log',level=logging.DEBUG)

############# Installation des modules supplémentaires ##############

os.system("apt install python3-pip -y") # installation de PIP pour python 3
os.system("pip3 install -r requirements.txt") # installation de la liste des modules suplèmentaires via le fichier requirements.txt
                                              # afin de préparer le système à l'utilisation du programme SafetyWpress.py

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

# Vérifier si le fichier docker-compose.yml existe ou non #

try:
    (Path('docker-compose.yml')).resolve(strict=True)
    print("Fichier docker-compose.yml présent")
    logging.info("Fichier docker-compose.yml présent")
except FileNotFoundError:
    print("Fichier docker-compose.yml manquant")
    logging.error("Fichier docker-compose.yml manquant")
    exit(1)

#####################################################################
##                                                                 ##
##                         Les Variables                           ##
##                                                                 ##
#####################################################################

################ Import du fichier de configuration #################

config = configparser.ConfigParser()
config.read('P6_config.ini')
repertoire_de_sauvegarde = config.get('repertoire','backup_repertoire')

#####################################################################
##                                                                 ##
##                  Programme de Préparation                       ##
##                                                                 ##
#####################################################################

# Vérifier si le répertoire de sauvegarde existe ou non #

try:
    (Path(repertoire_de_sauvegarde)).resolve(strict=True)
    print("Le répertoire n'existe pas !")
    logging.info("Le répertoire n'existe pas !")
except FileNotFoundError:
    os.makedirs(repertoire_de_sauvegarde, exist_ok=True)
    print("Création du répertoire de sauvegarde")
    logging.warning("Création du répertoire de sauvegarde")

# Déplacement fichiers utiles dans le repertoire de sauvegarde #

repertoire = shutil.copy('docker-compose.yml', repertoire_de_sauvegarde+'/')
repertoire = shutil.copy('.env', repertoire_de_sauvegarde+'/')
repertoire = shutil.copy('P6_config.ini', repertoire_de_sauvegarde+'/')
repertoire = shutil.copy('SafetyWpress.py', repertoire_de_sauvegarde+'/')

# Modification des fichiers SafetyWpress.py pour le rendre exécutable #

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

os.system("docker-compose -f "+repertoire_de_sauvegarde+"/docker-compose.yml up -d") 
