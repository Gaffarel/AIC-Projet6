#!/usr/bin/python3

#####################################################################
##                                                                 ##
##     Script de sauvegarde et restauration wordpresss  V0.0a      ##
##                                                                 ##
#####################################################################


#####################################################################
##                                                                 ##
##                    Importation des modules                      ##
##                                                                 ##
#####################################################################

#import os
import os.path

#help(os.path ) #aide sur la commande

#####################################################################
##                                                                 ##
##                    Importation des modules                      ##
##                                                                 ##
#####################################################################

#os.makedirs('/home/backup', exist_ok=True) 

# Vérifier si le chemin existe ou non
path = '/home/save'
path2 = 'c:\\save'

if os.path.exists(path2) :
    print("Chemin " , path2, " existe")
else:
    os.makedirs('c:\\save', exist_ok=True) 
    print("Chemin " , path2, " n'existe pas")

