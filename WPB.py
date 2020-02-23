#!/usr/bin/python3

#####################################################################
##                                                                 ##
##     Script de sauvegarde et restauration wordpresss  V0.1       ##
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

#####################################################################
##                                                                 ##
##                         Les Variables                           ##
##                                                                 ##
#####################################################################

################ Import du fichier de configuration #################

config = configparser.ConfigParser()
config.read('P6_config.ini')
FTP = config.get('config','serveur_ftp')
UserFTP = config.get('config','user_ftp')
MdpFTP = config.get('config','mdp_ftp')
UserBDD = config.get('config','user_bdd')
MdpBDD = config.get('config','mdp_bdd')
NBjourDEretention = config.get('retention','nbjour')
rep_linux = config.get('repertoire','backup_linux')

############################## Temps ################################

date_aujourdhui = date.today() # date d'aujourd'hui
date_aujourdhui_retention = date_aujourdhui-datetime.timedelta(days=int(NBjourDEretention)) # date d'aujourd'hui - la date de retention désiré
BACKUPDATE = date_aujourdhui.strftime("%d-%m-%Y") # formatage de la date Jour/Mois/Année
BACKUPDATE_OLD = date_aujourdhui_retention.strftime("%d-%m-%Y") # formatage de la date Jour/Mois/Année

############################ répertoire #############################

repertoire_de_sauvegarde = '/home/save' # répertoire de sauvegarde linux

############################# Fonction ##############################


def CONTAINER():
 client = docker.from_env()
 for container in client.containers.list():
  print (container.image,container.id)

#####################################################################
##                                                                 ##
##                    Programme de Backup                          ##
##                                                                 ##
#####################################################################

# Vérifier si le répertoire "/home/save" existe ou non #

if os.path.exists(repertoire_de_sauvegarde) :
     print("Chemin " , repertoire_de_sauvegarde, " existe")
else:
     os.makedirs(repertoire_de_sauvegarde, exist_ok=True)
     print("Chemin " , repertoire_de_sauvegarde, " n'existe pas")

# Récupération du nom et de l'ID du conteneur #

#client = docker.from_env()
#for container in client.containers.list():
# print (container.image,container.id)

print(BACKUPDATE)
print(BACKUPDATE_OLD)

print('')
print('le serveur FTP est:',FTP)
print('le login utilisateur du serveur FTP est:',UserFTP)
print('le mot de passe utilisateur du serveur FTP est:',MdpFTP)
print('le login utilisateur de la BDD MariaDB est:' ,UserBDD)
print('le mot de passe utilisateur de la BDD MariaDB est:' ,MdpBDD)
print('le Nombre de jour de rétention des sauvegardes est de:' ,NBjourDEretention)
print('répertoire de sauvegarde Linux:',rep_linux)
print('')

CONTAINER()