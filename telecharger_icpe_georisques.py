import os
import sys
import requests
import geojson
import csv
import datetime
import time

# Fonction date
def date_AAAA_MM_JJ():
    maintenant = datetime.datetime.now()
    annee = str(maintenant.year)
    mois = str(maintenant.month)
    jour = str(maintenant.day)

    if int(mois) < 10: mois = '0' + mois
    if int(jour) < 10: jour = '0' + jour

    return annee + '_' + mois + '_' + jour

# Fonction pour télécharger les données avec réessai en cas d'erreur
def telecharger_1000_lignes(url, liste_pour_geojson, retries=3):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    attempt = 0
    while attempt < retries:
        try:
            reponse = requests.get(url, headers=headers, allow_redirects=True)
            reponse.raise_for_status()  # Vérifie si la réponse HTTP est correcte (code 200)
            objet_natif_python = reponse.json()
            rubrique_data = objet_natif_python['data']
            break  # Si la requête réussit, sortir de la boucle
        except requests.exceptions.RequestException as e:
            attempt += 1
            print(f"Erreur lors de la requête, tentative {attempt}/{retries}: {e}")
            if attempt < retries:
                time.sleep(2)  # Attendre 2 secondes avant de réessayer
            else:
                print("Nombre de tentatives maximum atteint, arrêt du téléchargement.")
                sys.exit()

    for item in rubrique_data:
        if 'regimeVigueur' not in item:     item['regimeVigueur'] = None
        if 'siret' not in item:             item['siret'] = None
        if 'statutSeveso' not in item:      item['statutSeveso'] = None
        if 'etatActivite' not in item:      item['etatActivite'] = None
        if 'adresse1' not in item:          item['adresse1'] = None

        properties = {
            'raisonSociale': item['raisonSociale'],
            'siret': item['siret'],
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
            if not 'alinea' in rubrique:                rubrique['alinea'] = None
            if not 'regimeAutoriseAlinea' in rubrique:  rubrique['regimeAutoriseAlinea'] = None
            if not 'quantiteTotale' in rubrique:        rubrique['quantiteTotale'] = None
            if not 'unite' in rubrique:                 rubrique['unite'] = None

        regime_autorise = {"Autorisation": 4, "Enregistrement": 3, "Déclaration avec contrôle": 2, "Autres régimes": 1}
        for i, rubrique in enumerate(
                sorted(liste_rubriques, key=lambda x: regime_autorise.get(x.get('regimeAutoriseAlinea', -1), -1),
                       reverse=True), start=1):
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

        liste_pour_geojson.append(geojson.Feature(geometry=geojson.Point((item['longitude'], item['latitude'])),
                                                  properties=properties))

    url_next = objet_natif_python["next"]
    return (url_next, liste_pour_geojson)

# Fonction principale
def main(dossier, fichier_communes, champ_code_insee, fichier_geojson):
    chemin = os.path.join(dossier, fichier_communes)
    file_in = open(chemin, "r")
    reader = csv.DictReader(file_in)
    liste_pour_geojson = []

    i = 1
    for commune in reader:
        code = commune[champ_code_insee]
        print("Téléchargement de la commune", i)

        url_next = f'https://www.georisques.gouv.fr/api/v1/installations_classees?code_insee={code}&page_size=1000&page=1'

        while url_next is not None:
            print(f"Téléchargement à partir de l'URL : {url_next}")
            url_next, liste_pour_geojson = telecharger_1000_lignes(url_next, liste_pour_geojson)

            if url_next is not None:
                print("Il y a une page suivante à télécharger pour cette commune")
            else:
                print("Fin des pages pour cette commune.")

        i += 1

    feature_collection = geojson.FeatureCollection(liste_pour_geojson)

    chemin_fichier = os.path.join(dossier, fichier_geojson)

    with open(chemin_fichier, 'w', encoding='utf-8') as f:
        geojson.dump(feature_collection, f, ensure_ascii=False)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("\tusage: python3 script.py nom_du_csv colonne_code_insee ")
        exit()

    fichier_communes = sys.argv[1]
    champ_code_insee = sys.argv[2]
    dossier = os.path.dirname(__file__)
    fichier_geojson = 'icpe_' + date_AAAA_MM_JJ() + '.geojson'

    main(dossier, fichier_communes, champ_code_insee, fichier_geojson)
