#!/usr/bin/python3

#####################################################################
##                                                                 ##
##     Script de sauvegarde et restauration wordpresss  V0.0b      ##
##                                                                 ##
#####################################################################


#####################################################################
##                                                                 ##
##                    Importation des modules                      ##
##                                                                 ##
#####################################################################

#import os
import os.path #
import docker #
import datetime #
from datetime import date #

#####################################################################
##                                                                 ##
##                         Les Variables                           ##
##                                                                 ##
#####################################################################

############################ rétention ##############################

nbjour=10

############################## Temps ################################

date_aujourdhui = date.today() # date d'aujourd'hui
date_aujourdhui_retention = date_aujourdhui-datetime.timedelta(days=nbjour) # date d'aujourd'hui - la date de retention désiré
BACKUPDATE = date_aujourdhui.strftime("%d-%m-%Y") # formatage de la date Jour/Mois/Année
BACKUPDATE_OLD = date_aujourdhui_retention.strftime("%d-%m-%Y") # formatage de la date Jour/Mois/Année

############################ répertoire #############################

repertoire_de_sauvegarde = '/home/save' # répertoire de sauvegarde linux

#####################################################################
##                                                                 ##
##                    Programme de Backup                          ##
##                                                                 ##
#####################################################################

# Vérifier si le répertoire "/home/save" existe ou non

if os.path.exists(repertoire_de_sauvegarde) :
     print("Chemin " , repertoire_de_sauvegarde, " existe")
else:
     os.makedirs(repertoire_de_sauvegarde, exist_ok=True)
     print("Chemin " , repertoire_de_sauvegarde, " n'existe pas")

# Récupération du nom et de l'ID du conteneur

# client = docker.from_env()
# for container in client.containers.list():
#  print (container.image,container.id)





print(BACKUPDATE)
print(BACKUPDATE_OLD)