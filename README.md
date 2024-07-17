Ce script a été rédigé par Vincent Rouillard et Pierre Maxime Micalef de la DREAL Bretagne en novembre 2023 à partir d'un script fait par la DREAL ARA.

Il télécharge les données de l'API Installations Classées de Géorisques (https://www.georisques.gouv.fr/doc-api#/Installations%20Class%C3%A9es) selon une liste de codes communes. 
Il organise les attributs json en table, classe les activités par régime, géocode (point) selon les coordonnées enregistrées en attribut et exporte les données dans un fichier geojson.
Il a été développé en python 3.9

Lancement en ligne de commande :
"python   chemin_du_script.py   paramètre1   paramètre2"
avec :
- paramètre1 = chemin du csv contenant les communes à interroger
- paramètre2 = colonne qui contient les codes INSEE
