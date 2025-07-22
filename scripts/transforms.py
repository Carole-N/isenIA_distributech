import pandas as pd
from datetime import datetime


#########  TRANSFORM ELEMENT VIDE  #############################################
# Transformation des éléments vides d'une dataframe
# ajout de '*' en cas d'élément manquant
# Paramètre d'entrée : dataframe
# Sortie : dataframe corrigée
def transform_data_vide_df(name, data_df):

    champs_obligatoires = data_df.columns.tolist()
    print(f"[{name.upper()}]Champs attendus : {champs_obligatoires}", end=">")
    erreurs = []
    lignes_valides = []

    # data_df.iterrows() permet de parcourir chaque ligne du CSV une par une.
    # index = numéro de la ligne (commence à 0)
    # ligne = données de cette ligne, sous forme de dictionnaire

    for index, ligne in data_df.iterrows():
        ligne_dict = ligne.to_dict()
        valeurs = list(ligne_dict.values())

        # Vérification 1 : ligne avec un mauvais nombre de colonnes

        if len(valeurs) < len(champs_obligatoires) or pd.isnull(valeurs[-1]):
            # TO DO : Moyen de reconstituer une valeur manquante avec décalage des colonnes ?
            erreurs.append(
                {
                    "ligne": index + 2,  # +2 pour tenir compte de l'en-tête (ligne 1)
                    "erreur": "Longueur de ligne incorrecte",
                    "données": ligne_dict,
                }
            )
            continue

        # Remplacement des champs manquants ou nuls par '*'
        ligne_complete = {}
        for champ, val in ligne_dict.items():
            if pd.isnull(val):
                ligne_complete[champ] = "*"
            else:
                ligne_complete[champ] = val

        # Vérification : détection des champs marqués comme manquants
        champs_manquants = [
            champ for champ, val in ligne_complete.items() if val == "*"
        ]

        if champs_manquants:
            erreurs.append(
                {
                    "ligne": index + 2,
                    "erreur": "Champs manquants",
                    "champs_manquants": champs_manquants,
                    "données": ligne_complete,
                }
            )

        lignes_valides.append(ligne_complete)

    # Afficher les erreurs à l'écran : à vérifier plus tard comment le rendre plus précis
    if erreurs:
        print(f"\n\033[91m⚠️ Lignes avec problèmes détectées :\033[0m")
        for err in erreurs:
            if err["erreur"] == "Longueur de ligne incorrecte":
                print(
                    f"\033[35mLigne {err['ligne']} → ligne ignorée (longueur incorrecte)\033[0m"
                )
            else:
                print(
                    f"\033[34mLigne {err['ligne']} → champs manquants : {err['champs_manquants']}\033[0m"
                )
    else:
        print(f"\033[32m✅ Toutes les lignes sont valides.\033[0m")

    # On crée un nouveau fichier avec uniquement les lignes valides.
    df_valide = pd.DataFrame(lignes_valides)

    return df_valide


# Transformation des dates d'une dataframe
# # Paramètre d'entrée : dataframe
# Sortie : date corrigée


def corriger_date(date_str):

    if pd.isnull(date_str) or not isinstance(date_str, str):
        print(f"❌ Entrée invalide ou nulle : {date_str}")
        return "*"

    # Essai de plusieurs formats possibles
    formats_possibles = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%Y%m%d",
        "%d%m%Y",
        "%m-%d-%Y",
        "%d %b %Y",
        "%d %B %Y",
    ]

    for fmt in formats_possibles:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            print(
                f"✅ Correction réussie : '{date_str}' avec format '{fmt}' → {dt.strftime('%Y-%m-%d')}"
            )
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            print(f"⛔ Format invalide pour '{date_str}' avec '{fmt}'")
            continue

    print(f"❌ Aucun format valide trouvé pour : {date_str}")
    return "*"


#########  TRANSFORM TYPE  #############################################
# Validation des types des colonnes du dataframe
# ajout de '*' en cas d'élément incohérent
# Paramètre d'entrée : dataframe
# Sortie : dataframe corrigée
def transform_type_df(name, data_df):
    champs_obligatoires = data_df.columns.tolist()
    erreurs = []
    lignes_valides = []

    for index, ligne in data_df.iterrows():
        ligne_dict = ligne.to_dict()
        ligne_valide = {}
        ligne_erreurs = []

        for champ, valeur in ligne_dict.items():
            val = str(valeur).strip()

            if champ in [
                "production_id",
                "product_id",
                "quantity",
                "region_id",
                "revendeur_id",
            ]:
                try:
                    val_float = float(val)
                    if val_float.is_integer():
                        ligne_valide[champ] = int(val_float)
                    else:
                        raise ValueError("Nombre décimal détecté")
                except:
                    ligne_valide[champ] = "*"
                    ligne_erreurs.append(champ)
                continue

            # --------- Champs de type FLOTTANT ---------
            if champ in ["cout_unitaire", "unit_price"]:
                try:
                    val_float = float(val)
                    if val_float <= 0:
                        raise ValueError("float <= 0")
                    ligne_valide[champ] = val_float
                except:
                    ligne_valide[champ] = "*"
                    ligne_erreurs.append(champ)
                continue

            # --------- Champs de type DATE ---------
            if champ in ["date_production", "commande_date"]:
                try:
                    datetime.strptime(val, "%Y-%m-%d")
                    ligne_valide[champ] = val
                except:
                    correct = corriger_date(val)
                    ligne_valide[champ] = correct
                continue

            # --------- Champs de type TEXTE ---------
            if champ in [
                "product_name",
                "region_name",
                "revendeur_name",
                # "numero_commande",
            ]:
                if not any(c.isalpha() for c in val):
                    ligne_valide[champ] = "*"
                    ligne_erreurs.append(champ)
                else:
                    val1 = nettoyer_texte(val)
                    val2 = nettoyer_typographie(val1)
                    val3 = nettoyer_typographie_aggressif(val2)
                    ligne_valide[champ] = val3
                continue

            # --------- Champs inconnus (non référencés) ---------
            ligne_valide[champ] = val

        if ligne_erreurs:
            erreurs.append(
                {
                    "ligne": index + 2,  # +2 pour prendre en compte l'en-tête
                    "erreur": "Champs invalides ou non conformes",
                    "champs": ligne_erreurs,
                    "données": ligne_dict,
                }
            )

        lignes_valides.append(ligne_valide)

    # --------- Rapport console ---------
    if erreurs:
        print(f"\033[91m⚠️ Lignes invalides détectées :\033[0m")
        for err in erreurs:
            print(
                f"\033[33mLigne {err['ligne']} → champs invalides : {err['champs']}\033[0m"
            )
    else:
        print(f"\033[32m✅ Toutes les lignes sont valides.\033[0m")

    # --------- Retour du DataFrame nettoyé ---------
    return pd.DataFrame(lignes_valides)


#########  TRANSFORM : Nettoyage des espaces, caractères et typographies  #############################################
# Transformation des espaces, caractères speciaux et typographies
# Partie. 1 Nettoyer les espaces et les sauts de lignes
def nettoyer_texte(texte):
    if pd.isnull(texte):
        return "*"
    texte = str(texte)
    texte = texte.strip()  # enlève espaces début/fin
    texte = texte.replace("\xa0", " ")  # espace insécable -> espace normal
    texte = texte.replace("\r", "").replace("\n", "")  # supprime saut de ligne
    return texte


# Partie. 2 Nettoyer la typographie classique (guillemets, tirets)
def nettoyer_typographie(texte):
    if pd.isnull(texte):
        return "*"
    texte = str(texte).strip()

    remplacements = {
        "’": "'",  # apostrophe courbe vers droite
        "“": '"',
        "”": '"',
        "«": '"',
        "»": '"',
        "–": "-",  # tiret moyen
        "—": "-",  # tiret long
    }

    for mauvais, bon in remplacements.items():
        texte = texte.replace(mauvais, bon)

    return texte


# Partie. 3 Nettoyer en supprimant accents et caractères spéciaux
# la typographie classique (guillemets, tirets)
import unicodedata


def nettoyer_typographie_agressif(texte):
    if pd.isnull(texte):
        return "*"
    texte = unicodedata.normalize("NFD", texte)  # sépare caractères + accents
    texte = texte.encode("ascii", "ignore").decode("utf-8")  # enlève accents
    return texte
