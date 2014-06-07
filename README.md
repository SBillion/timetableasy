Timetableasy
============

Project school at SUPINFO (2009)
=============================

Le projet que nous devons réaliser est une plateforme de saisie de plannings
pour université. Elle doit permettre, une fois terminée, de gérer les différents cursus,
cours et interventions de milliers d’étudiants et de professeurs. C’est une
« application lourde », en réseau qui permet à tous de consulter ses planning et selon
les droits acquis de procéder à leur gestion.



Lancement
==================
Pour lancer l'application sans l'installer, ouvrez un terminal et tapez ./run.sh
à la racine du dossier.
Options:
-o : go into offline mode
-r : rebuild database (drop all -> create all)
-v : active verbose mode (display activities)
-d : active debug mode
-f X: fill the db for testing with X items
--help, -h, -? : print this message

La base de données de test a été remplie en utilisant l'option -f 20
Pour vous connecter, vous pouvez choisir un utilisateur entre "db_user_1" et "db_user_20"
Mot de passe entre "user0" et "user20"


Package Debian
===============
Le dossier build, comprit dans les sources, contient les fichiers necessaires
pour empaqueter le projet en .deb.
Ouvrez un terminal et dans build/debian/timetableasy-1.0/
faites sh compiler.sh.




### Création du package d'installation sous windows ###

Les fichiers nécessaire à la création du package d'installation sont dans build/windows
