Ce script a été rédigé par Vincent Rouillard et Pierre Maxime Micalef de la DREAL Bretagne en novembre 2023 à partir d'un script fait par la DREAL ARA.

Il télécharge les données de l'API Installations Classées de Géorisques (https://www.georisques.gouv.fr/doc-api#/Installations%20Class%C3%A9es) selon une liste de codes communes. 
Il organise les attributs json en table, classe les activités par régime, géocode (point) selon les coordonnées enregistrées en attribut et exporte les données dans un fichier geojson.
Il a été développé en python 3.9

Lancement en ligne de commande :
"python   chemin_du_script.py   paramètre1   paramètre2"
avec :
- paramètre1 = chemin du fichier contenant les codes communes (format csv)
- paramètre2 = nom de la colonne qui contient les codes communes (code INSEE sur 5 caractères)

INSTALLATION

LINUX :
git clone https://github.com/sig-dreal-bretagne/telecharger_icpe_georisques

python3 -m venv .venv

source .venv/bin/activate

pip install --upgrade pip

pip install -r requirements.txt

WINDOWS :
git clone https://github.com/sig-dreal-bretagne/telecharger_icpe_georisques

python -m venv .venv

.venv\scripts\activate

pip install --upgrade pip

pip install -r telecharger_icpe_georisques\requirements.txt
