#-------------------------------------------------------------------------------
# Name:        telecharger_icpe_georiques.py
# Purpose:     télécharger les ICPE à partir de l'API Géorisques
#
# Authors:     Vincent Rouillard, Pierre-Maxime Micalef
#
# Created:     09/11/2023
# Copyright:
# Licence:     MIT
#-------------------------------------------------------------------------------


# -*- coding: utf-8 -*-

"""imports"""

#fonctions basiques (os et sys)
'''besoin pour concaténer dossier+fichier'''
import os
'''besoin pour récupérer les variables passées lors de l'appel du script'''
import sys

#pour requêtes http
'''pour interroger l'url'''
import urllib.request
'''pour télécharger les données'''
import requests

#librairies json geojson
'''besoin pour lire la réponse à la requête'''
import json
'''besoin pour créer le geojson'''
import geojson

#librairies csv et time
'''besoin pour ouvrir le csv des communes'''
import csv
'''besoin pour dater le csv produit'''
import datetime

#pour connaitre la version des modules
from importlib_metadata import version
import pkg_resources


"""fonction date"""
def date_AAAA_MM_JJ():
    maintenant = datetime.datetime.now()
    annee = str(maintenant.year)
    mois = str(maintenant.month)
    jour = str(maintenant.day)

    if int(mois)<10: mois='0'+mois
    if int(jour)<10: jour='0'+jour

    return annee+'_'+mois+'_'+jour

"""fonction telecharger"""
def telecharger_100_lignes(url, liste_pour_geojson):

    try:
        reponse = urllib.request.urlopen(url)
    except urllib.error.URLError as erreur:
        #si erreur : signaler erreur et on s'arrête
        print (str(erreur),"pour l'url ",url)
        print("il faut se déconnecter du réseau Ministère")
        sys.exit()
    else:
        reponse = requests.get(url, allow_redirects=True)
        objet_natif_python = reponse.json()
        rubrique_data = objet_natif_python['data']

        for item in rubrique_data:
            if 'regimeVigueur' not in item:     item['regimeVigueur']=None
            if 'siret' not in item:             item['siret']=None
            if 'statutSeveso' not in item:      item['statutSeveso']=None
            if 'etatActivite' not in item:      item['etatActivite']=None
            if 'adresse1' not in item:          item['adresse1']=None

            properties = {
                'raisonSociale': item['raisonSociale'],
                'siret' : item['siret'],
                'adresse1': item['adresse1'],
                'codePostal': item['codePostal'],
                'codeInsee': item['codeInsee'],
                'commune': item['commune'],
                'longitude': item['longitude'],
                'latitude': item['latitude'],
                'bovins': item['bovins'],
                'porcs': item['porcs'],
                'volailles': item['volailles'],
                'carriere': item['carriere'],
                'eolienne': item['eolienne'],
                'industrie': item['industrie'],
                'prioriteNationale': item['prioriteNationale'],
                'statutSeveso': item['statutSeveso'],
                'ied': item['ied'],
                'etatActivite': item['etatActivite'],
                'regime': item['regime'],
                'codeAIOT': item['codeAIOT'],
                'coordonneeXAIOT': item['coordonneeXAIOT'],
                'coordonneeYAIOT': item['coordonneeYAIOT'],
                'systemeCoordonneesAIOT': item['systemeCoordonneesAIOT'],
                'serviceAIOT': item['serviceAIOT']
            }

            liste_rubriques = item['rubriques']

            for rubrique in liste_rubriques:
                if not 'alinea' in rubrique:                rubrique['alinea']=None
                if not 'regimeAutoriseAlinea' in rubrique:  rubrique['regimeAutoriseAlinea']=None
                if not 'quantiteTotale' in rubrique:        rubrique['quantiteTotale']=None
                if not 'unite' in rubrique:                 rubrique['unite']=None

            #on classe les régimes dans cet ordre
            regime_autorise = {"Autorisation": 4, "Enregistrement": 3, "Déclaration avec contrôle": 2, "Autres régimes": 1}
            for i, rubrique in enumerate(
                    sorted(liste_rubriques, key=lambda x: regime_autorise.get(x.get('regimeAutoriseAlinea',-1),-1), reverse=True),start=1):
                properties[f"numeroRubrique_{i}"] = rubrique['numeroRubrique']
                properties[f"nature_{i}"] = rubrique['nature']
                properties[f"alinea_{i}"] = rubrique['alinea']
                properties[f"regimeAutoriseAlinea_{i}"] = rubrique['regimeAutoriseAlinea']
                properties[f"quantiteTotale_{i}"] = rubrique['quantiteTotale']
                properties[f"unite_{i}"] = rubrique['unite']
            # Traiter les inspections
            liste_inspections = item.get('inspections', [])
            for i, inspection in enumerate(liste_inspections, start=1):
                properties[f"dateInspection_{i}"] = inspection.get('dateInspection', None)
                fichier_inspection = inspection.get('fichierInspection', {})
                url_fichier_inspection = fichier_inspection.get('urlFichier', None)
                properties[f"urlFichierInspection_{i}"] = url_fichier_inspection

            # Traiter les documents hors inspection
            liste_documents_hors_inspection = item.get('documentsHorsInspection', [])
            for i, document in enumerate(liste_documents_hors_inspection, start=1):
                properties[f"nomFichier_{i}"] = document.get('nomFichier', None)
                properties[f"typeFichier_{i}"] = document.get('typeFichier', None)
                properties[f"dateFichier_{i}"] = document.get('dateFichier', None)
                properties[f"urlFichier_{i}"] = document.get('urlFichier', None)


            liste_pour_geojson.append(geojson.Feature(geometry=geojson.Point(( item['longitude'], item['latitude'])),
                                                   properties=properties))

        url_next = objet_natif_python["next"]
        return(url_next, liste_pour_geojson)


"""fonction MAIN"""


def main(fichier_communes, champ_code_insee):

    #ouvrir la liste des codes insee
    file_in = open(fichier_communes,"r")
    reader = csv.DictReader(file_in)
    liste_pour_geojson = []

    #télécharger les ICPE pour chaque commune de la liste
    i_commune=1
    for commune in reader:
        code_insee = commune[champ_code_insee]
        print()
        print("téléchargement de la commune",i_commune)
        page=1

        #Tant qu'url_next n'est pas vide, télécharger les 100 lignes suivantes
        while url_next!=None:
            url_next = 'https://www.georisques.gouv.fr/api/v1/installations_classees?code_insee='+code_insee+'&page='+page+'&page_size=100'
            url_next, liste_pour_geojson = telecharger_100_lignes(url_next,liste_pour_geojson)
            page = page + 1

        #url_next est vide, on passe à la commune suivante
        i_commune = i_commune + 1

    #on convertit la liste pour geojson en collection geojson
    feature_collection = geojson.FeatureCollection(liste_pour_geojson)

    #on enregistre le geojson dans le dossier de la liste des codes insee
    dossier = os.path.dirname(fichier_communes)
    fichier_geojson = 'icpe_'+date_AAAA_MM_JJ()+'.geojson'
    chemin_geojson = os.path.join(dossier,fichier_geojson)

    with open(chemin_geojson, 'w', encoding='utf-8') as f:
        geojson.dump(feature_collection, f, ensure_ascii=False)


"""programme principal"""
#récupération des paramètres

if __name__ == '__main__':
    if len(sys.argv)==1:
        print( "\tusage: python3 script.py chemin_du_csv colonne_code_insee " )
        exit()

    fichier_communes = sys.argv[1]
    champ_code_insee = sys.argv[2]

    main(fichier_communes, champ_code_insee)
