# <div align="center"> Script de Création , Sauvegarde et de Restauration d'un serveur Wordpress avec MariaDB sous Docker </div>

# <div align="center"> Projet N°6 [AIC] </div>

# <p align="center"><img width=20% src="https://github.com/Gaffarel/AIC-Projet6/blob/master/images/logo.png"></p>

# <div align="center">SafetyWpress.py</div>

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python 3.7.3](https://badgen.net/badge/python/3.7.3)](https://www.python.org/downloads/release/python-373/)
[![Debian 10](https://badgen.net/badge/Debian/10)](https://www.debian.org/)
![Contibutions welcom](https://img.shields.io/badge/contributions-welcom-orange.svg)
![Last commit](https://img.shields.io/github/last-commit/Gaffarel/AIC-Projet6)

## Table des matières
- [Présentation du projet](#pr%C3%A9sentation)
- [Préparation du serveur](#pr%C3%A9paration)
  - [Configuration du programme create.py](#configuration-du-programme-createpy)
  - [Fichier P6_config.ini](#le-fichier-p6_configini)
  - [Fichier .env](#le-fichier-env)
  - [Fichier requirements.txt](#le-fichier-requirementstxt)
- [Utilisation du logiciel SafetyWpress.py](#utilisation-du-logiciel-safetywpresspy)
- [Log](#les-fichiers-logs)
- [Crontab](#crontab)
- [Licence](#licence)

## Présentation

Ce projet à pour but de créer automatiquement un serveur WordPress prêt à l'emploi,  
avec le programme Python [create.py](https://github.com/Gaffarel/AIC-Projet6/blob/master/create.py) .  
Pour cela on se servira de docker-compose et d'un fichier de référence [docker-compose.yml](https://github.com/Gaffarel/AIC-Projet6/blob/master/docker-compose.yml)  
qu'il faudra configurer avec le fichier d'environnement [.env](https://github.com/Gaffarel/AIC-Projet6/blob/master/ex_.env)  
et configurer ensuite le fichier [P6_config.ini](https://github.com/Gaffarel/AIC-Projet6/blob/master/ex_P6_config.ini) .

Nous pourrons également grâce au programme Python [SafetyWpress.py](https://github.com/Gaffarel/AIC-Projet6/blob/master/SafetyWpress.py)  
sauvegarder et restaurer les fichiers de configuration du serveur linux hôte,  
ainsi que les fichiers du volume WordPress et le Dump de sa base de donnée.  

Et enfin, envoyer et récupérer les sauvegardes depuis le cloud de Microsoft AZURE  


## Préparation

Afin d'utiliser au mieux les programmes [create.py](https://github.com/Gaffarel/AIC-Projet6/blob/master/create.py) et [SafetyWpress.py](https://github.com/Gaffarel/AIC-Projet6/blob/master/SafetyWpress.py),  
il faudra installer un serveur Linux avec Debian 10.

Puis on lancera le programme `./create.py` pour préparer le serveur à recevoir  
Docker, Docker-compose et les images de Wordpress ainsi que la base de donnée MariaDB avec le fichier `docker-compose.yml`.

### Configuration du programme `create.py`

Avant de lancer le programme `./create.py`,  
il faudra préparer les fichiers de configuration `P6_config.ini`, `.env` et `requirements.txt` qui se situe dans le projet.

### Le Fichier `P6_config.ini`

; Fichier de configuration

[config]

azure_login=******** ; Compte de stockage AZURE  
azure_key=******** ; 'key azure'  
azure_bkp=******** ; Répertoire de sauvegarde AZURE  
user_bdd=******** ; le nom de l'utilisateur de la base de donnée autorisé à se connecter  
mdp_bdd=******** ; le mot de passe de l'utilisateur de la base de donnée autorisé à se connecter  
name_bdd=******** ; le nom de la base de donnée pour Wordpress  

[retention]

nbjour=10 ; nombre de jour de rétention

[repertoire]

backup_repertoire=/srv/backup ; répertoire de sauvegarde par défaut.  

### Le Fichier `.env`

DB_ROOT_PASSWORD=********  # Le mot de passe administrateur de notre moteur MariaDB  
DB_DATABASE=********  # le nom de la base de donnée à créer  
DB_USER=********  # le nom de l'utilisateur de la base de donnée  
DB_PASSWORD=********  # le mot de passe de l'utilisateur de la base de donnée  
WP_DB_USER=********  # le nom de l'utilisateur de la base de donnée  
WP_DB_PASSWORD=********  # le mot de passe de l'utilisateur de la base de donnée  
WP_DB_NAME=********  # le nom de la base de donnée pour Wordpress  

### Le Fichier `requirements.txt`
Il contient les modules spécifiques au bon fonctionnement du programme `SafetyWpress.py`  

| Modules                  | version | explication                          |
|--------------------------|---------|--------------------------------------|
|azure-storage-file==2.1.0 | 2.1.0   | permet d'utiliser la librairie AZURE |
|docker==4.2.0             | 4.2.0   | permet d'utiliser la librairie DOCKER|
|PyYAML==5.3               | 5.3     | permet de parser les fichiers YAML   |

## Utilisation du logiciel `./SafetyWpress.py`

| Commandes                      | Arguments     | Raccourcis     |
|--------------------------------|---------------|----------------|
| sauvegarde                     | -save         | -s             |
| restauration totale du serveur | -restoreT     | -rT            |
| restauration d'une BDD         | -restoreDB    | -rDB           |

## Crontab

en root lancé crontab -e puis :

20 3 * * *  /srv/backup/SafetyWpress.py save >/dev/null 2>&1

où

20 3 * * *  /srv/backup/SafetyWpress.py -s >/dev/null 2>&1

afin d'éffectuer une sauvegarde tous les jours à 3H20 par exemple.

## Les fichiers logs

`SafetyWpress.log` et `create.log` sont créés dans /var/log/SafetyWpress/  

```
logging.basicConfig(filename='/var/log/SafetyWpress/SafetyWpress.log',level=logging.WARNING, format='%(asctime)s : %(levelname)s - %(name)s - %(module)s : %(message)s')  
# pour le mode WARNING  
```
pour le monde DEBUG il suffit de changer ceci:  

```
level=logging.DEBUG 
```


## Licence

 <p><a href="https://github.com/Gaffarel/AIC-Projet6/blob/master/LICENSE">
 <img width=6% src="https://www.gnu.org/graphics/gplv3-or-later.svg">SafetyWpress.py et create.py sont sous licence GNU General Public License v3.0 
 </a></p>