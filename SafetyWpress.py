#!/usr/bin/python3

#####################################################################
##                                                                 ##
##     Script de sauvegarde et de restauration sur le cloud de     ##
##    Microsoft AZURE d'un serveur wordpress avec MariaDB  V0.7f   ##
##                                                                 ##
#####################################################################

#####################################################################
##                                                                 ##
##               Script crée par : Allouis Sébastien               ##
##   Ce script est sous licence GNU General Public License v3.0    ##
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
import subprocess #

#####################################################################
##                                                                 ##
##                         Les Variables                           ##
##                                                                 ##
#####################################################################

####################### Nom du fichier de LOG #######################

logging.basicConfig(filename='/var/log/SafetyWpress/SafetyWpress.log',level=logging.WARNING, format='%(asctime)s : %(levelname)s - %(name)s - %(module)s : %(message)s') # pour le mode WARNING
#logging.basicConfig(filename='/var/log/SafetyWpress/SafetyWpress.log',level=logging.INFO, format='%(asctime)s : %(levelname)s - %(name)s - %(module)s : %(message)s') # pour le mode INFO
#logging.basicConfig(filename='/var/log/SafetyWpress/SafetyWpress.log',level=logging.DEBUG, format='%(asctime)s : %(levelname)s - %(name)s - %(module)s : %(message)s') # pour le mode DEBUG

############## On récupére le chemin absolu du script ###############

script_path = os.path.abspath(os.path.dirname( __file__))

############## Présence des Fichiers de configuration ###############

# Vérifier si le fichier P6_config.ini existe ou non #

try:
    (Path(script_path+'/P6_config.ini')).resolve(strict=True)
    print("Fichier P6_config.ini présent")
    logging.debug("Fichier P6_config.ini présent")
    syslog.syslog(syslog.LOG_DEBUG,"Fichier P6_config.ini présent")
except FileNotFoundError:
    print("Fichier P6_config.ini manquant")
    logging.warning("Fichier P6_config.ini manquant")
    syslog.syslog(syslog.LOG_WARNING,"Fichier P6_config.ini manquant")
    exit(1)  # sortie avec Warning !

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
# Test de l'accès à Microsoft AZURE #

try:
    FileService(account_name=AZURE_CPT, account_key=AZURE_KEY)
    file_service = FileService(account_name=AZURE_CPT, account_key=AZURE_KEY)
    print("Autorisation d'accès au compte Microsoft AZURE OK")
    logging.debug("Autorisation d'accès au compte Microsoft AZURE OK")
    syslog.syslog(syslog.LOG_DEBUG,"Autorisation d'accès au compte Microsoft AZURE OK")
except:
    print("Problème d'autorisation d'accès au compte Microsoft AZURE")
    logging.error("Problème d'autorisation d'accès au compte Microsoft AZURE")
    syslog.syslog(syslog.LOG_ERR,"Problème d'autorisation d'accès au compte Microsoft AZURE")
    exit(2) # sortie avec erreur !

# Création du répertoire: backup6 sur Microsoft AZURE de notre exemple #
# Vérifier si le répertoire de sauvegarde backup6 sur Microsoft AZURE existe ou non #

try:
    file_service.exists(AZURE_REP_BKP)
    print("Le répertoire de sauvegarde AZURE existe !")
    logging.debug("Le répertoire de sauvegarde AZURE existe !")
    syslog.syslog(syslog.LOG_DEBUG,"Le répertoire de sauvegarde AZURE existe !")
except FileNotFoundError:
    file_service.create_share(AZURE_REP_BKP)
    print("Création du répertoire de sauvegarde AZURE ")
    logging.warning("Création du répertoire de sauvegarde AZURE ")
    syslog.syslog(syslog.LOG_WARNING,"Création du répertoire de sauvegarde AZURE ")

############################## Temps ################################

BACKUP_DATE = date.today().strftime("%d-%m-%Y") # date d'aujourd'hui au format Jour/Mois/Année
BACKUP_DATE_OLD = (date.today()-datetime.timedelta(days=int(NBjourDEretention))).strftime("%d-%m-%Y") # date d'aujourd'hui - le nb de jour de rétention au format Jour/Mois/Année

############################# Fonction ##############################

# Fonction de récupération du Nom de l'image de la Base De Donnée du fichier docker-compose.yml #

def get_database_name():
  with open(repertoire_de_sauvegarde+"/docker-compose.yml",'r') as file: # Ouverture du fichier YML en lecture
    fichier_yml = yaml.load(file, Loader=yaml.FullLoader) #
    BDD = fichier_yml["services"]["db"]["image"] # Emplacement de l'image de le base de donnée dans le fchier YML
  return(BDD) # la fontion retourne le nom du conteneur demandé

# Fonction de récupération du short_id de la Base De Donnée via le dictionnaire #

def get_short_id_container(name_container):
  client = docker.from_env() #
  dict_conteneur = {} # dictionnaire vide des conteneurs
  for container in client.containers.list(): # equivaut à docker ps
    dict_conteneur[str(container.image)[9:-2]] = str(container.short_id) # récuperation du short_id et de l'image avec mise en forme dans le dictionnaire
  return (dict_conteneur[name_container]) # la fontion retourne le short_id nom conteneur demandé

# Fonction de récupération d'un fichier de sauvegarde dans un répertoire de Microsoft AZURE #

def get_choix_de_la_sauvegarde():
  list_file_save = file_service.list_directories_and_files(AZURE_REP_BKP)
  nb_save=1
  dict_save = {} # dictionnaire vide de la liste des sauvegarde
  for file_save in list_file_save: # parcours de tous les dossiers de sauvegarde
    dict_save[nb_save] = str(file_save.name)
    print("N°"+str(nb_save)+":", file_save.name) # affichage des sauvegardes
    nb_save += 1
# Vérification du bonne saisie de N° de Sauvegarde avec un caractère valide #
  while True:
      try:
          choix = int(input("Entrez le numéro de sauvegarde: N°:"))
      except ValueError:
          print("Caractère non accepté, veuillez choisir entre 1 et",nb_save-1)
          continue
      if choix < 1 or choix > nb_save-1:
          print("Sauvegarde de 1 à ",nb_save-1)
          continue
      else:
          break
  return(dict_save[int(choix)])

# Fonction de Compte à rebours #

def get_countdown(temps):
    while temps:
        mins, secs = divmod(temps, 60)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
        print(timeformat, end='\r')
        time.sleep(1)
        temps -= 1

# Test de la disponibilité de la base de donnée #

def connect_db():
  NAME = get_database_name()
  ID = get_short_id_container(NAME)
  try:
    subprocess.check_call('docker exec -it '+ID+' /usr/bin/mysql -u '+UserBDD+' -p'+MdpBDD+' --execute \"SHOW DATABASES;"', shell = True)
  except subprocess.CalledProcessError as err:
    print(err.output)
    print("La base de donnée n'est pas prête, veuillez réssayer !")
    logging.error("La base de donnée n'est pas prête, veuillez réssayer !")
    syslog.syslog(syslog.LOG_ERR,"La base de donnée n'est pas prête, veuillez réssayer !")
    exit(2) # sortie avec erreur !

#####################################################################
##                                                                 ##
##         Test et choix des fonctions avec les arguments          ##
##                                                                 ##
#####################################################################

# Tester la présence d'un argument #

if len(sys.argv) < 2:
        print("Il faut un argument pour appeller le script :\n")
        print("\n        save ou -s   pour sauvegarder ")
        print("\n        restoreDB ou -rDB   pour restaurer uniquement la base de donnée")
        print("\n        restoreT ou -rT   pour restaurer le serveur complet")
        exit(1)

# Récupération de l'argument #

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
  logging.warning("Début de la sauvegarde !") # warning 
  syslog.syslog(syslog.LOG_WARNING,"Début de la sauvegarde !") # warning 

# Dump de la base de donnée MariaDB #

  client = docker.from_env()
  container = client.containers.get(ID)
  print("Dump de la Base de donnée "+Nom_de_la_BDD+" en cours ...")
  logging.info("Dump de la Base de donnée "+Nom_de_la_BDD+" en cours ...") # warning 
  syslog.syslog(syslog.LOG_INFO, "Dump de la Base de donnée "+Nom_de_la_BDD+" en cours ...") # warning 
  MySQLdump = str((container.exec_run("mysqldump -u "+UserBDD+" -p"+MdpBDD+" "+Nom_de_la_BDD)).output, 'utf-8') # dump de la BDD,
                                                                                                                # puis récupération de la sortie de command
                                                                                                                # et formattage du binaire
  fichier = open(repertoire_de_sauvegarde+"/save_"+str(BACKUP_DATE)+"db.sql","w")
  fichier.write(MySQLdump)
  fichier.close()
  print("Dump de la Base de donnée "+Nom_de_la_BDD+" OK !")
  logging.info("Dump de la Base de donnée "+Nom_de_la_BDD+" OK !") # warning 
  syslog.syslog(syslog.LOG_INFO, "Dump de la Base de donnée "+Nom_de_la_BDD+" OK !") # warning 

# Compression et sauvegarde des fichiers du serveur #

  print("Sauvegarde des fichiers de configuration du serveur Linux ...")
  print("")

  print("Compression et sauvegarde des fichiers du serveur ...")
  logging.info("Compression et sauvegarde des fichiers du serveur ...") # warning 
  syslog.syslog(syslog.LOG_INFO,"Compression et sauvegarde des fichiers du serveur ...") # warning 

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

  print("Compression et sauvegarde des fichiers OK !")
  logging.info("Compression et sauvegarde des fichiers OK !") # warning 
  syslog.syslog(syslog.LOG_INFO,"Compression et sauvegarde des fichiers OK !") # warning 

# Sauvegarde sur Microsoft AZURE #

# Création d'un sous-répertoire: save_date du jour
  print("Création d'un sous-répertoire save_"+str(BACKUP_DATE)+" sur Microsoft AZURE en cours ...")
  logging.info("Création d'un sous-répertoire save_"+str(BACKUP_DATE)+" sur Microsoft AZURE en cours ...") # warning 
  syslog.syslog(syslog.LOG_INFO, "Création d'un sous-répertoire save_"+str(BACKUP_DATE)+" sur Microsoft AZURE en cours ...") # warning 

  file_service.create_directory(AZURE_REP_BKP,'save_'+str(BACKUP_DATE))

  print("Création d'un sous-répertoire save_"+str(BACKUP_DATE)+" sur Microsoft AZURE OK !")
  logging.info("Création d'un sous-répertoire save_"+str(BACKUP_DATE)+" sur Microsoft AZURE OK !") # warning 
  syslog.syslog(syslog.LOG_INFO, "Création d'un sous-répertoire save_"+str(BACKUP_DATE)+" sur Microsoft AZURE OK !") # warning 

# copy des fichiers de sauvegarde sur le répertoire Microsoft AZURE

  print("Copy des fichiers de sauvegarde sur le répertoire Microsoft AZURE en cours ...")
  logging.info("Copy des fichiers de sauvegarde sur le répertoire Microsoft AZURE en cours ...") # warning 
  syslog.syslog(syslog.LOG_INFO,"Copy des fichiers de sauvegarde sur le répertoire Microsoft AZURE en cours ...") # warning 

  file_service.create_file_from_path(AZURE_REP_BKP,'save_'+str(BACKUP_DATE),'save_'+str(BACKUP_DATE)+'db.sql',repertoire_de_sauvegarde+'/save_'+str(BACKUP_DATE)+'db.sql')
  file_service.create_file_from_path(AZURE_REP_BKP,'save_'+str(BACKUP_DATE),'save_'+str(BACKUP_DATE)+'.tar.bz2',repertoire_de_sauvegarde+'/save_'+str(BACKUP_DATE)+'.tar.bz2')

  print("Copy des fichiers de sauvegarde sur le répertoire Microsoft AZURE OK !")
  logging.info("Copy des fichiers de sauvegarde sur le répertoire Microsoft AZURE OK !") # warning 
  syslog.syslog(syslog.LOG_INFO,"Copy des fichiers de sauvegarde sur le répertoire Microsoft AZURE OK !") # warning 

# suppression des fichiers de sauvegarde

  os.remove(repertoire_de_sauvegarde+"/save_"+str(BACKUP_DATE)+"db.sql")
  print("Suppression du fichier "+BACKUP_DATE+"db.sql")
  os.remove(repertoire_de_sauvegarde+"/save_"+str(BACKUP_DATE)+".tar.bz2")
  print("Suppression du fichier "+BACKUP_DATE+".tar.bz2")

# Liste des fichiers ou répertoires de Microsoft AZURE et suppression des anciennes sauvegardes en fonction du nombre de jour 

  print("Liste des sauvegardes: ")
  list_file = file_service.list_directories_and_files(AZURE_REP_BKP)
  for file_or_dir in list_file:
    if ('save_'+str(BACKUP_DATE_OLD)) in file_or_dir.name:
      file_service.delete_file(AZURE_REP_BKP,'save_'+str(BACKUP_DATE_OLD),'save_'+str(BACKUP_DATE_OLD)+'db.sql')
      file_service.delete_file(AZURE_REP_BKP,'save_'+str(BACKUP_DATE_OLD),'save_'+str(BACKUP_DATE_OLD)+'.tar.bz2')
      file_service.delete_directory(AZURE_REP_BKP,'save_'+str(BACKUP_DATE_OLD))
    else:
      print("")
      print(file_or_dir.name)
      logging.warning(file_or_dir.name) # warning 
      syslog.syslog(syslog.LOG_WARNING, file_or_dir.name) # warning 

  print("")
  print("La sauvegarde c'est terminé correctement !")
  logging.warning("La sauvegarde c'est terminé correctement !") # warning
  syslog.syslog(syslog.LOG_WARNING,"La sauvegarde c'est terminé correctement !") # warning

######################################################
# Lancement de la fonction attachée restoreDB / -rDB #
######################################################

elif argument == 'restoreDB' or argument == '-rDB':

  connect_db() # verification de la disponibilité de la Base de Donnée
  print("Choix du Numéro de sauvegarde: ?")
  print("")
  BACKUP_DATE_SAVE=get_choix_de_la_sauvegarde()
  print("Récupération de la sauvegarde du :",BACKUP_DATE_SAVE)
  file_service.get_file_to_path(AZURE_REP_BKP, BACKUP_DATE_SAVE, BACKUP_DATE_SAVE+'db.sql', BACKUP_DATE_SAVE+'db.sql')

# Restauration de la base de donnée .sql #

  NAME = get_database_name()
  print("le nom de l'image de la Base de donnée est: ",NAME)
  print("")
  ID = get_short_id_container(NAME)
  print("le short ID de l'image de la Base de donnée est: ",ID)
  print("")
  print("Restauration de la Base de donnée en cours ...")
  print("")
  os.system("cat "+BACKUP_DATE_SAVE+"db.sql | docker exec -i "+ID+" /usr/bin/mysql -u "+UserBDD+" -p"+MdpBDD+" "+Nom_de_la_BDD)
  print("Restauration de la base de donnée ok !")
  print("")

# suppression du fichiers *db.sql sauvegarde récupéré #

  os.remove(repertoire_de_sauvegarde+"/"+BACKUP_DATE_SAVE+"db.sql")
  print("Suppression du fichier "+BACKUP_DATE_SAVE+"db.sql")
  print("")
  print ("Opération terminé !")

####################################################
# Lancement de la fonction attachée restoreT / -rT #
####################################################

elif argument == 'restoreT' or argument == '-rT':

  connect_db() # verification de la disponibilité de la Base de Donnée 
  print("Choix du Numéro de sauvegarde: ?")
  print("")
  BACKUP_DATE_SAVE=get_choix_de_la_sauvegarde()
  print("Récupération de la sauvegarde du :",BACKUP_DATE_SAVE)
  file_service.get_file_to_path(AZURE_REP_BKP, BACKUP_DATE_SAVE, BACKUP_DATE_SAVE+'.tar.bz2', BACKUP_DATE_SAVE+'.tar.bz2')
  file_service.get_file_to_path(AZURE_REP_BKP, BACKUP_DATE_SAVE, BACKUP_DATE_SAVE+'db.sql', BACKUP_DATE_SAVE+'db.sql')

# Décompression de la sauvegarde des fichiers du serveur #

  print ("décompression en cours ...")
  print("")
  backup_bz2 = tarfile.open(repertoire_de_sauvegarde+'/'+BACKUP_DATE_SAVE+'.tar.bz2') # Emplacement de sauvegarde du fichier compressé (tar.bz2)
  backup_bz2.extractall('/')
  backup_bz2.close() #
  print ("décompression OK !")
  print("")

# suppression du fichiers tar.bz2 sauvegarde récupéré #

  os.remove(repertoire_de_sauvegarde+"/"+BACKUP_DATE_SAVE+".tar.bz2")
  print("Suppression du fichier "+BACKUP_DATE_SAVE+".tar.bz2")
  print("")

# Restauration de la base de donnée *.sql #

  NAME = get_database_name()
  print("le nom de l'image de la Base de donnée est: ",NAME)
  print("")
  ID = get_short_id_container(NAME)
  print("le short ID de l'image de la Base de donnée est: ",ID)
  print("")
  print("Restauration de la base de donnée cours ...")
  print("")
  os.system("cat "+BACKUP_DATE_SAVE+"db.sql | docker exec -i "+ID+" /usr/bin/mysql -u "+UserBDD+" -p"+MdpBDD+" "+Nom_de_la_BDD)
  print("Restauration de la base de donnée ok !")
  print("")

# suppression du fichiers *db.sql sauvegarde récupéré #

  os.remove(repertoire_de_sauvegarde+"/"+BACKUP_DATE_SAVE+"db.sql")
  print("Suppression du fichier "+BACKUP_DATE_SAVE+"db.sql")
  print("")

# redémarrage du serveur Linux dans 5 secondes #

  print ("Opération terminé !")
  print("")
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