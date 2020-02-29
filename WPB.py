#!/usr/bin/python3

#####################################################################
##                                                                 ##
##     Script de sauvegarde et restauration wordpresss  V0.2       ##
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

# Récupération du nom et de l'ID du conteneur #

def CONTAINER_bis(motcle):
 client = docker.from_env()
 for container in client.containers.list():
  container_image = str(container.image)
# print(container_image)
  if motcle in container_image[8:]:
   container_mariadb_id = container.short_id
   container_mariadb_image = container.image
#  elif "wordpress" in container_image[8:]:
#   container_wordpress_id = container.short_id

  print ("le conteneur MariaDB est :", container_mariadb_id)
 # print ("le comteneur WordPress est :", container_wordpress_id)
  print ("l'image de conteneur MariaDB est :",container_mariadb_image)

 return container_mariadb_id, container_mariadb_image


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

# Récupération de l'ID du conteneur #

client = docker.from_env()
container_mariadb_id = ""
container_wordpress_id = ""

for container in client.containers.list():
 container_image = str(container.image)
 if "mariadb" in container_image[8:]:
  container_mariadb_id = container.short_id
 elif "wordpress" in container_image[8:]:
  container_wordpress_id = container.short_id

print ("le conteneur MariaDB est :", container_mariadb_id)
print ("le comteneur WordPress est :", container_wordpress_id)

print(BACKUPDATE)
print(BACKUPDATE_OLD)

#CONTAINER()

toto = CONTAINER_bis('mariadb')
print(toto)

# Récupération du short ID et du nom des conteneurs dans un dictionnaire#

conteneur = {}
client = docker.from_env()
for container in client.containers.list():
  conteneur[str(container.short_id)] = str(container.image)[8:-1]

print(conteneur)


# Dump de la base de donnée MariaDB #

client = docker.from_env()
container = client.containers.get('33a595d494')
res = container.exec_run("mysqldump -u allouis -pbob MyCompany")
fichier = open("save.sql","w")
resultat = str(res.output, 'utf-8')
print(resultat)
fichier.write(resultat)
fichier.close()

# Compréssion et sauvegarde des fichiers du serveur #

backup_bz2 = tarfile.open('/home/backup/save_'+str(BACKUPDATE)+'.tar.bz2','w:bz2') # Emplacement de sauvegarde du fichier compressé (tar.bz2)
backup_bz2.add('/var/lib/docker/volumes/backup_wp/') # sauvegarde du volumes wordpress
backup_bz2.add('/etc/network/interfaces') #
backup_bz2.add('/etc/resolv.conf') #
backup_bz2.add('/etc/hosts') #
backup_bz2.add('/etc/hostname') #
backup_bz2.add('/var/log/') #
backup_bz2.add('/var/spool/cron/crontabs/') #
backup_bz2.add('/home/backup/log/') #
backup_bz2.close() # 