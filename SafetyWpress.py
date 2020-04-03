#!/usr/bin/python3

#####################################################################
##                                                                 ##
##      Script de sauvegarde, de création, et de restauration      ##
##            d'un serveur wordpress avec MariaDB  V0.6a           ##
##                                                                 ##
#####################################################################

#####################################################################
##                                                                 ##
##                    Importation des modules                      ##
##                                                                 ##
#####################################################################

import time #
import os # Diverses interfaces pour le système d'exploitation
import os.path # manipulation courante des chemins
from pathlib import Path #
import datetime # Types de base pour la date et l'heure
import configparser # Configuration file parser
import docker # Docker
from datetime import date # 
import tarfile # 
from azure.storage.file import FileService # 
import sys #
import yaml # 
import logging #
import syslog #

#####################################################################
##                                                                 ##
##                         Les Variables                           ##
##                                                                 ##
#####################################################################

####################### Nom du fichier de LOG #######################

logging.basicConfig(filename='/var/log/SafetyWpress/SafetyWpress.log',level=logging.DEBUG, format='%(asctime)s : %(levelname)s - %(name)s - %(module)s : %(message)s')

############## On récupére le chemin absolu du script ###############

script_path = os.path.abspath(os.path.dirname( __file__))

############## Présence des Fichiers de configuration ###############

# Vérifier si le fichier P6_config.ini existe ou non #

try:
    (Path(script_path+'/P6_config.ini')).resolve(strict=True)
    print("Fichier P6_config.ini présent")
    logging.info("Fichier P6_config.ini présent")
    syslog.syslog(syslog.LOG_INFO,"Fichier P6_config.ini présent")
except FileNotFoundError:
    print("Fichier P6_config.ini manquant")
    logging.error("Fichier P6_config.ini manquant")
    syslog.syslog(syslog.LOG_ERR,"Fichier P6_config.ini manquant")
    exit(1)

################ Import du fichier de configuration #################

config = configparser.ConfigParser()
config.read(script_path+'/P6_config.ini')
AZURE_CPT = config.get('config','azure_login')
AZURE_KEY = config.get('config','azure_key')
AZURE_REP_BKP = config.get('config','azure_bkp')
UserBDD = config.get('config','user_bdd')
MdpBDD = config.get('config','mdp_bdd')
Nom_de_la_BDD = config.get('config','name_bdd')
NBjourDEretention = config.get('retention','nbjour')
repertoire_de_sauvegarde = config.get('repertoire','backup_repertoire')

#####################################################################
##                                                                 ##
##                        Microsoft AZURE                          ##
##                                                                 ##
#####################################################################

# Autorisation d'accès au compte Microsoft AZURE

#file_service = FileService(account_name=AZURE_CPT, account_key=AZURE_KEY)

# Test de l'accès à Microsoft AZURE #

try:
    FileService(account_name=AZURE_CPT, account_key=AZURE_KEY)
    file_service = FileService(account_name=AZURE_CPT, account_key=AZURE_KEY)
    print("Autorisation d'accès au compte Microsoft AZURE OK")
    logging.info("Autorisation d'accès au compte Microsoft AZURE OK")
    syslog.syslog(syslog.LOG_INFO,"Autorisation d'accès au compte Microsoft AZURE OK")
except:
    print("Problème d'autorisation d'accès au compte Microsoft AZURE")
    logging.error("Problème d'autorisation d'accès au compte Microsoft AZURE")
    syslog.syslog(syslog.LOG_ERR,"Problème d'autorisation d'accès au compte Microsoft AZURE")
    exit(2) # sortie avec erreur !

# Création du répertoire: backup6 sur Microsoft AZURE de notre exemple

# Vérifier si le répertoire de sauvegarde backup6 sur Microsoft AZURE existe ou non #

try:
    file_service.exists(AZURE_REP_BKP)
    print("Le répertoire de sauvegarde AZURE existe !")
    logging.info("Le répertoire de sauvegarde AZURE existe !")
    syslog.syslog(syslog.LOG_INFO,"Le répertoire de sauvegarde AZURE existe !")
except FileNotFoundError:
    file_service.create_share(AZURE_REP_BKP)
    print("Création du répertoire de sauvegarde AZURE ")
    logging.warning("Création du répertoire de sauvegarde AZURE ")
    syslog.syslog(syslog.LOG_WARNING,"Création du répertoire de sauvegarde AZURE ")

#file_service.create_share(AZURE_REP_BKP)

############################## Temps ################################

BACKUP_DATE = date.today().strftime("%d-%m-%Y") # date d'aujourd'hui au format Jour/Mois/Année
BACKUP_DATE_OLD = (date.today()-datetime.timedelta(days=int(NBjourDEretention))).strftime("%d-%m-%Y") # date d'aujourd'hui - le nb de jour de rétention au format Jour/Mois/Année

############################# Fonction ##############################

# Récupération du Nom de l'image de la Base De Donnée du fichier docker-compose.yml #

def get_database_name(): #
  with open(repertoire_de_sauvegarde+"/docker-compose.yml",'r') as file: #
    doc = yaml.load(file, Loader=yaml.FullLoader) #
    txt = doc["services"]["db"]["image"] #
  return(txt) # la fontion retourne le nom du conteneur demandé

# Récupération du short_id de la Base De Donnée via le dictionnaire #

def get_short_id_container(name_container): #
  client = docker.from_env() #
  dict_conteneur = {} # dictionnaire vide des conteneurs
  for container in client.containers.list(): # equivaut à docker ps
    dict_conteneur[str(container.image)[9:-2]] = str(container.short_id) # récuperation du short_id et de l'image avec mise en forme dans le dictionnaire
  return (dict_conteneur[name_container]) # la fontion retourne le short_id nom conteneur demandé

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

# Fonction de Compte à rebours

def get_countdown(temps):
    while temps:
        mins, secs = divmod(temps, 60)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
        print(timeformat, end='\r')
        time.sleep(1)
        temps -= 1

#####################################################################
##                                                                 ##
##         Test et choix des fonctions avec les arguments          ##
##                                                                 ##
#####################################################################

# Testing the presence of an argument

if len(sys.argv) < 2:
        print("Il faut un argument pour appeller le script :\n")
        print("\n        save ou -s   pour sauvegarder ")
        print("\n        restoreDB ou -rDB   pour restaurer uniquement la base de donnée")
        print("\n        restoreT ou -rT   pour restaurer le serveur complet")
        exit(1)

# Récupération de l'argument

argument = sys.argv[1]

##################################################
#            Traitement de l'argument            #
# et lancement de la fonction attachée save / -s #
##################################################

if argument == 'save' or argument == '-s':
  print("Sauvegarde en cours ...")
  print("")
  NAME = get_database_name()
  print("le nom de l'image de la Base de donnée est: ",NAME)
  print("")
  ID = get_short_id_container(NAME)
  print("le short ID de l'image de la Base de donnée est: ",ID)
  print("")

# Dump de la base de donnée MariaDB #

  client = docker.from_env()
  container = client.containers.get(ID)
  MySQLdump = str((container.exec_run("mysqldump -u "+UserBDD+" -p"+MdpBDD+" "+Nom_de_la_BDD)).output, 'utf-8') # dump de la BDD,
                                                                                                                # puis récupération de la sortie de command
                                                                                                                # et formattage du binaire
  fichier = open(repertoire_de_sauvegarde+"/save_"+str(BACKUP_DATE)+"db.sql","w")
  fichier.write(MySQLdump)
  fichier.close()

# Compréssion et sauvegarde des fichiers du serveur #

  backup_bz2 = tarfile.open(repertoire_de_sauvegarde+'/save_'+str(BACKUP_DATE)+'.tar.bz2','w:bz2') # Emplacement de sauvegarde du fichier compressé (tar.bz2)
  backup_bz2.add('/var/lib/docker/volumes/backup_wp/') # sauvegarde du volumes docker wordpress
  backup_bz2.add('/etc/network/interfaces')
  backup_bz2.add('/etc/resolv.conf')
  backup_bz2.add('/etc/hosts')
  backup_bz2.add('/etc/hostname')
  backup_bz2.add('/var/log/')
  backup_bz2.add('/var/spool/cron/crontabs/')
  backup_bz2.add(repertoire_de_sauvegarde+'/log/')
  backup_bz2.add(repertoire_de_sauvegarde+'/.env')
  backup_bz2.add(repertoire_de_sauvegarde+'/docker-compose.yml')
  backup_bz2.close() # fermeture du fichier

# Sauvegarde sur Microsoft AZURE #

# Création d'un sous-repertoire: save_date du jour
  file_service.create_directory(AZURE_REP_BKP,'save_'+str(BACKUP_DATE))

# copy des fichiers de sauvegarde sur le repertoire Microsoft AZURE

  file_service.create_file_from_path(AZURE_REP_BKP,'save_'+str(BACKUP_DATE),'save_'+str(BACKUP_DATE)+'db.sql',repertoire_de_sauvegarde+'/save_'+str(BACKUP_DATE)+'db.sql')
  file_service.create_file_from_path(AZURE_REP_BKP,'save_'+str(BACKUP_DATE),'save_'+str(BACKUP_DATE)+'.tar.bz2',repertoire_de_sauvegarde+'/save_'+str(BACKUP_DATE)+'.tar.bz2')

# suppression des fichiers de sauvegarde

  os.remove(repertoire_de_sauvegarde+"/save_"+str(BACKUP_DATE)+"db.sql")
  os.remove(repertoire_de_sauvegarde+"/save_"+str(BACKUP_DATE)+".tar.bz2")

# Liste des fichiers ou repertoires de Microsoft AZURE et suppression des anciennes sauvegardes en fonction du nombre de jour 

  list_file = file_service.list_directories_and_files(AZURE_REP_BKP)
  for file_or_dir in list_file:
    if ('save_'+str(BACKUP_DATE_OLD)) in file_or_dir.name:
      file_service.delete_file(AZURE_REP_BKP,'save_'+str(BACKUP_DATE_OLD),'save_'+str(BACKUP_DATE_OLD)+'db.sql')
      file_service.delete_file(AZURE_REP_BKP,'save_'+str(BACKUP_DATE_OLD),'save_'+str(BACKUP_DATE_OLD)+'.tar.bz2')
      file_service.delete_directory(AZURE_REP_BKP,'save_'+str(BACKUP_DATE_OLD))
    else:
      print("")
      print(file_or_dir.name)

######################################################
# Lancement de la fonction attachée restoreDB / -rDB #
######################################################

elif argument == 'restoreDB' or argument == '-rDB':
  print("Restauration de la Base de donnée en cours ...")
  print("")
  print("Choix du Numéro de sauvegarde: ?")
  print("")
  BACKUP_DATE_SAVE=get_choix_de_la_sauvegarde()
  print (BACKUP_DATE_SAVE)
  file_service.get_file_to_path(AZURE_REP_BKP, BACKUP_DATE_SAVE, BACKUP_DATE_SAVE+'db.sql', BACKUP_DATE_SAVE+'db.sql')
  print('sauvegarde récupéré')

# Restauration de la base de donnée .sql #
  NAME = get_database_name()
  print("le nom de l'image de la Base de donnée est: ",NAME)
  print("")
  ID = get_short_id_container(NAME)
  print("le short ID de l'image de la Base de donnée est: ",ID)
  print("")

  #os.system("cat save_21-03-2020db.sql | docker exec -i 4698 /usr/bin/mysql -u allouis -pbob MyCompany")
  os.system("cat "+BACKUP_DATE_SAVE+"db.sql | docker exec -i "+ID+" /usr/bin/mysql -u "+UserBDD+" -p"+MdpBDD+" "+Nom_de_la_BDD)
  #MySQLdump = str((container.exec_run("mysqldump -u "+UserBDD+" -p"+MdpBDD+" "+Nom_de_la_BDD)).output, 'utf-8')

# suppression du fichiers tar.bz2 sauvegarde récupéré #
  os.remove(repertoire_de_sauvegarde+"/"+BACKUP_DATE_SAVE+"db.sql")

####################################################
# Lancement de la fonction attachée restoreT / -rT #
####################################################

elif argument == 'restoreT' or argument == '-rT':
  print("Restauration du serveur en cours ...")
  print("")
  print("Choix du Numéro de sauvegarde: ?")
  print("")
  BACKUP_DATE_SAVE=get_choix_de_la_sauvegarde()
  print(BACKUP_DATE_SAVE)
  file_service.get_file_to_path(AZURE_REP_BKP, BACKUP_DATE_SAVE, BACKUP_DATE_SAVE+'.tar.bz2', BACKUP_DATE_SAVE+'.tar.bz2')
  file_service.get_file_to_path(AZURE_REP_BKP, BACKUP_DATE_SAVE, BACKUP_DATE_SAVE+'db.sql', BACKUP_DATE_SAVE+'db.sql')
  print('sauvegarde récupéré')

# Décompression de la sauvegarde des fichiers du serveur #

  backup_bz2 = tarfile.open(repertoire_de_sauvegarde+'/'+BACKUP_DATE_SAVE+'.tar.bz2') # Emplacement de sauvegarde du fichier compressé (tar.bz2)
  backup_bz2.extractall('/')
  backup_bz2.close() #
  print ('décompression faite')

# suppression du fichiers tar.bz2 sauvegarde récupéré #

  os.remove(repertoire_de_sauvegarde+"/"+BACKUP_DATE_SAVE+".tar.bz2")

# Restauration de la base de donnée *.sql #
  NAME = get_database_name()
  print("le nom de l'image de la Base de donnée est: ",NAME)
  print("")
  ID = get_short_id_container(NAME)
  print("le short ID de l'image de la Base de donnée est: ",ID)
  print("")

  #os.system("cat save_21-03-2020db.sql | docker exec -i 4698 /usr/bin/mysql -u allouis -pbob MyCompany")
  os.system("cat "+BACKUP_DATE_SAVE+"db.sql | docker exec -i "+ID+" /usr/bin/mysql -u "+UserBDD+" -p"+MdpBDD+" "+Nom_de_la_BDD)
  #MySQLdump = str((container.exec_run("mysqldump -u "+UserBDD+" -p"+MdpBDD+" "+Nom_de_la_BDD)).output, 'utf-8')

# suppression du fichiers *db.sql sauvegarde récupéré #
  os.remove(repertoire_de_sauvegarde+"/"+BACKUP_DATE_SAVE+"db.sql")

# redémarrage du serveur Linux dans 5 secondes #
  print("Reboot du système dans 5 secondes...")
  get_countdown(5)
  print('Redémarrage !\n\n\n\n\n')
  os.system("reboot")

else:
        print("Il faut un argument pour appeller le script :\n")
        print("\n        save ou -s   pour sauvegarder ")
        print("\n        restoreDB ou -rDB   pour restaurer uniquement la base de donnée")
        print("\n        restoreT ou -rT   pour restaurer le serveur complet")
        exit(1)