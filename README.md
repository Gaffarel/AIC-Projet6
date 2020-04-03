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
- [Préparation du serveur](#pr%C3%A9paration)
  - [Configuration du programme create.py](#configuration-du-programme-createpy)
  - [Fichier P6_config.ini](#le-fichier-p6_configini)
  - [Fichier .env](#le-fichier-env)
  - [Fichier requirements.txt](#le-fichier-requirementstxt)
- [Utilisation du logiciel SafetyWpress.py](#utilisation-du-logiciel-safetywpresspy)
- [Log](#les-fichiers-logs)
- [Crontab](#crontab)
- [Licence](#licence)

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

20 3 * * * /bin/python3.7 /srv/backup/SafetyWpress.py save >/dev/null 2>&1

où

20 3 * * * /bin/python3.7 /srv/backup/SafetyWpress.py -s >/dev/null 2>&1

afin d'éffectuer une sauvegarde tous les jours à 3H20 .

## Les fichiers logs

`SafetyWpress.log` et `create.log` sont créés dans /var/log/SafetyWpress/

## Licence

 <p><a href="https://github.com/Gaffarel/AIC-Projet6/blob/master/LICENSE">
 <img width=6% src="https://www.gnu.org/graphics/gplv3-or-later.svg">AIC-Projet6 is licensed under the GNU General Public License v3.0
 </a></p>
