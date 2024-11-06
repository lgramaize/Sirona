from leginorma import LegifranceText, LegifranceClient
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime
import re
import json
import requests
import requests_cache
import os
import PySimpleGUI as sg
import pandas as pd
import html.parser
import traceback
import os


######################################################################
#               Définition des fonctions générales                   #
######################################################################

percents = []

def quit():
 """
    Quitte le programme en cours d'exécution.

    Cette fonction utilise `sys.exit()` pour mettre fin au programme.
    Elle est particulièrement utile pour arrêter un programme en cas
    d'erreur ou lorsque certaines conditions sont remplies, nécessitant
    l'interruption de l'exécution du code.

    Notes :
        - `sys.exit()` lève une exception `SystemExit`, ce qui permet
          aux applications embarquées d'attraper cette exception si
          nécessaire pour effectuer des tâches de nettoyage avant de
          terminer.
        - Cette fonction doit être importée avec le module `sys` :
          `import sys`.
    """

def progression(lst_len, display=10):
    """
    Suivi de la progression d'une tâche basée sur une liste.

    Cette fonction calcule et affiche périodiquement la progression d'un traitement
    basé sur la longueur d'une liste `lst_len`. Elle imprime le pourcentage de
    progression chaque fois que celui-ci atteint un multiple de `display` (par défaut 10 %).

    Paramètres :
    -----------
    lst_len : int
        La longueur totale de la liste, indiquant la progression maximale à atteindre.

    display : int, optionnel
        Le pas d'affichage en pourcentage (par défaut à 10 %). Par exemple, avec `display=10`,
        la fonction affichera 10 %, 20 %, 30 %, etc., de progression.

    Variables globales :
    --------------------
    - `check` : variable globale représentant le pourcentage précédent affiché.
      Cette variable est utilisée pour éviter les affichages redondants.
    - `check_ac` : variable globale comptant les éléments déjà traités dans `lst_len`.
    - `percents` : liste globale de pourcentages déjà affichés pour éviter les doublons.

    Retourne :
    ---------
    tuple
        Un tuple contenant la valeur actuelle de `check` et `check_ac` (le compteur total d'avancement).

    Notes :
    ------
    - Cette fonction modifie les variables globales `check`, `check_ac` et `percents`,
      ce qui permet de suivre l'état entre différents appels de la fonction.
    - `check_ac` est incrémenté à chaque appel pour représenter le nombre d'éléments traités.

    """


######################################################################
#          Définition des fonctions de l'interface graphique         #
######################################################################


def message_erreur(type_erreur):
 """
    Affiche un message d'erreur dans une fenêtre graphique.

    Cette fonction crée une fenêtre graphique pour afficher un message d'erreur
    spécifique fourni par l'utilisateur. Elle utilise le module `PySimpleGUI` pour
    afficher la fenêtre avec le message d'erreur et un bouton "Ok" pour fermer la fenêtre.

    Paramètres :
    -----------
    type_erreur : str
        Le message d'erreur à afficher dans la fenêtre. Ce message donne des détails
        sur l'erreur rencontrée.

    Variables globales :
    --------------------
    - `version` : variable globale représentant le titre de la fenêtre d'erreur.
      Cette variable doit être définie avant d'appeler la fonction.

    Détails :
    --------
    - `layout` : Liste de liste définissant l'agencement des éléments de la fenêtre.
        - `sg.Text("Erreur : ")` : Texte d'introduction indiquant qu'il s'agit d'un message d'erreur.
        - `sg.Text(type_erreur)` : Texte affichant le message d'erreur détaillé.
        - `sg.Button('Ok')` : Bouton pour fermer la fenêtre.

    - `error` : Instance de la fenêtre d'erreur, créée avec `sg.Window`, utilisant la version globale
      comme titre et les éléments définis dans `layout`.

    Fonctionnement :
    ---------------
    - La fenêtre attend que l'utilisateur clique sur le bouton "Ok" ou ferme la fenêtre pour se fermer.
    - Lorsque l'événement `sg.WIN_CLOSED` ou 'Ok' est déclenché, la fenêtre se ferme automatiquement.

    Notes :
    ------
    - `sg` doit être importé depuis `PySimpleGUI` avant d'utiliser cette fonction.
    - La variable globale `version` doit être définie pour que la fonction fonctionne correctement.

    """

######################################################################
#         Définition des fonctions d'extraction des id               #
######################################################################

# Objectif : Export des ids de textes obtenus par une recherche avancée sur legifrance.


def operateur(input_dic):
    """
    Détermine l'opérateur logique ('ET' ou 'OU') basé sur l'entrée de l'utilisateur.

    Cette fonction vérifie le dictionnaire d'entrée `input_dic` pour déterminer
    si l'opérateur choisi est 'ET' ou 'OU' en fonction de l'état d'une clé spécifique, `'-RADIO-'`.
    Si `input_dic['-RADIO-']` est `True`, l'opérateur sera 'ET', sinon, il sera 'OU'.

    Paramètres :
    -----------
    input_dic : dict
        Dictionnaire contenant les valeurs d'entrée pour déterminer l'opérateur.
        Il doit inclure la clé `'-RADIO-'`, qui doit être de type booléen.

    Retourne :
    ---------
    str
        L'opérateur logique sélectionné sous forme de chaîne de caractères : 'ET' ou 'OU'.

    Notes :
    ------
    - Cette fonction est utile pour appliquer des critères multiples avec un
      opérateur logique choisi dynamiquement par l'utilisateur.
    - La clé `'-RADIO-'` doit être présente dans `input_dic`, sinon une erreur sera levée.

    """


def fonds():
    """
    Sélectionne un fonds juridique pour effectuer une recherche, en utilisant une interface graphique.

    Cette fonction affiche une fenêtre graphique permettant à l'utilisateur de choisir parmi différents types
    de fonds juridiques. Une fois le fonds sélectionné, il est affiché dans une nouvelle fenêtre de confirmation.
    La fonction retourne le code du fonds sélectionné.

    Variables globales :
    --------------------
    - `version` : variable globale représentant le titre de la fenêtre, nécessaire pour identifier la version
      de l'application. Doit être initialisée avant d'appeler cette fonction.

    Détails du fonds :
    ------------------
    - `types_fonds` : dictionnaire de correspondance entre le nom complet de chaque fonds et son code abrégé.

    - Fonds pris en charge :
    Journal officiel, CNIL, Jurisprudence administrative, Jurisprudence judiciaire,
    Jurisprudence constitutionnelle, Accords de branche et conventions collectives, Codes (par date de version),
    Codes (par état juridique), Textes consolidés (par date de version), Textes consolidés (par état juridique),
    Tous les contenus, Circulaires et instructions, Accords d'entreprise


    Interface graphique :
    ---------------------
    1. La première fenêtre présente une liste des fonds disponibles à sélectionner.
    2. L'utilisateur sélectionne un fonds, puis clique sur "Ok".
    3. Une fenêtre de confirmation s'ouvre, affichant le fonds sélectionné.
    4. L'utilisateur peut fermer la fenêtre de confirmation en cliquant sur "Ok".

    Paramètres de la fenêtre :
    --------------------------
    - `sg.Text('Sélectionner un fonds dans lequel effectuer la recherche')` : Indique à l'utilisateur l'action à réaliser.
    - `sg.Listbox(...)` : Liste déroulante de tous les fonds disponibles, triés par ordre alphabétique.
    - `sg.Button('Ok')` : Bouton de confirmation pour valider la sélection.

    Gestion des erreurs :
    ---------------------
    - Si aucune sélection valide n'est faite ou si une erreur se produit, la fonction appelle `message_erreur`
      pour afficher un message d'erreur.

    Retourne :
    ---------
    str
        Code abrégé du fonds sélectionné.

    Notes :
    ------
    - `sg` doit être importé depuis `PySimpleGUI` avant d'utiliser cette fonction.
    - Cette fonction utilise la fonction `message_erreur` pour gérer les erreurs de sélection.
    - La variable globale `version` doit être définie pour que la fonction fonctionne correctement.

    """


def champs():
    """
    Permet de définir les champs de recherche ainsi que les critères associés, en utilisant une interface graphique.

    Cette fonction affiche une interface permettant à l'utilisateur de choisir un champ de recherche parmi une
    liste de types, d'y associer un opérateur logique ('ET' ou 'OU'), puis de définir les critères de recherche
    pour ce champ. L'utilisateur peut ensuite ajouter d'autres champs de recherche. La fonction retourne une liste
    de dictionnaires contenant les champs sélectionnés, leurs opérateurs et leurs critères.

    Variables globales :
    --------------------
    - `version` : titre de la fenêtre (doit être défini avant l'appel à cette fonction).

    Paramètres de la fenêtre :
    --------------------------
    - `types_champs` : dictionnaire mappant chaque champ de recherche à son code interne.

    Champs pris en charge :
    Dans tous les champs, Dans les titres, Dans les tables des matières, NOR, Numéro de texte, Numéro de délibération,
    Numéro de décision, Numéro d'article, Dans les contenus d’articles, Ministère, Dans les visas, Dans les notices,
    Dans les visas ou les notices, Dans les travaux préparatoires, Dans les signatures, Dans les notas, Numéro d'affaire,
    Dans les abstrats, Dans les résumés, Dans les contenus des textes, ECLI, Numéro de la loi déférée, Type de décision,
    Numéro interne, Référence de publication au JO ou au BO, RESUME_CIRC, TEXTE_REF, Titre de la loi déférée,
    Raison sociale, Mots clés, IDCC


    Interface utilisateur :
    -----------------------
    1. La première fenêtre demande de sélectionner un opérateur ('ET' ou 'OU') et un champ de recherche.
    2. Après la sélection, l'utilisateur peut définir des critères pour le champ.
    3. Une fenêtre de confirmation s'affiche, demandant si l'utilisateur souhaite ajouter un nouveau champ.
    4. Si "OUI" est sélectionné, le processus recommence; sinon, la fonction retourne la liste des champs définis.

    Paramètres de la fonction `operateur` et `criteres` :
    -----------------------------------------------------
    - `operateur(values)` : détermine si l'opérateur pour le champ est 'ET' ou 'OU' en fonction de la sélection utilisateur.
    - `criteres(type_champ)` : définit les critères spécifiques à chaque champ de recherche.

    Retourne :
    ---------
    list
        Une liste de dictionnaires, chaque dictionnaire contient :
        - 'typeChamp' : code interne du champ sélectionné.
        - 'operateur' : opérateur logique pour les critères du champ.
        - 'criteres' : critères définis pour le champ.

    Gestion des erreurs :
    ---------------------
    - Si une erreur survient lors de la définition du champ ou des critères, la fonction appelle `message_erreur`
      pour afficher un message d'erreur.

    Notes :
    ------
    - `sg` doit être importé depuis `PySimpleGUI` avant d'utiliser cette fonction.
    - La fonction utilise `message_erreur` pour gérer les erreurs et `criteres` pour définir des critères spécifiques.
    - `version` doit être défini pour afficher le titre de la fenêtre.
    """


def criteres(typeChamp):
"""
    Définit les critères de recherche pour un champ donné en utilisant une interface graphique.

    Cette fonction affiche une interface permettant à l'utilisateur de spécifier des critères de recherche
    pour un champ particulier. Elle permet de sélectionner un type de recherche, d'entrer un texte à rechercher,
    et de choisir un opérateur logique ('ET' ou 'OU'). L'utilisateur peut définir plusieurs critères pour un même champ.

    Variables globales :
    --------------------
    - `version` : titre de la fenêtre (doit être défini avant l'appel à cette fonction).

    Paramètres :
    -----------
    typeChamp : str
        Le nom du champ pour lequel les critères de recherche sont définis. Il est utilisé pour indiquer
        le champ en cours de configuration dans l'interface graphique.

    Types de recherche :
    --------------------
    - `types_recherche` : dictionnaire contenant les options de recherche disponibles et leur code interne
    Types de recherche pris en charge :
    Un de ces mots, Expression exacte, Tous les mots, Exclure ces mots, Exclure cette expression exacte

    Interface utilisateur :
    -----------------------
    1. Affiche une fenêtre demandant l'opérateur, le texte à rechercher, et le type de recherche.
    2. L'utilisateur sélectionne un type de recherche et entre un texte de recherche.
    3. Une fenêtre de confirmation montre les informations saisies et demande si l'utilisateur souhaite ajouter un autre critère.
    4. Si "OUI" est sélectionné, le processus recommence; sinon, la fonction retourne la liste des critères définis.

    Paramètres de la fonction `operateur` :
    ---------------------------------------
    - `operateur(values)` : détermine l'opérateur logique 'ET' ou 'OU' pour le critère de recherche.

    Retourne :
    ---------
    list
        Une liste de dictionnaires, chaque dictionnaire contenant :
        - 'typeRecherche' : le type de recherche sélectionné.
        - 'valeur' : le texte de recherche saisi.
        - 'operateur' : l'opérateur logique pour le critère.

    Gestion des erreurs :
    ---------------------
    - Si une erreur survient (par exemple, aucun texte saisi), la fonction appelle `message_erreur` pour afficher
      un message d'erreur.

    Notes :
    ------
    - `sg` doit être importé depuis `PySimpleGUI` avant d'utiliser cette fonction.
    - La fonction utilise `message_erreur` pour gérer les erreurs, et `operateur` pour définir l'opérateur.
    - `version` doit être défini pour afficher le titre de la fenêtre.

    """


def filtres():
"""
    Définit un filtre de date pour une recherche, en utilisant une interface graphique.

    Cette fonction affiche une interface permettant à l'utilisateur de spécifier une période de recherche en sélectionnant
    une date de début et une date de fin. Les dates sont ensuite converties au format AAAA-MM-JJ et stockées dans un
    dictionnaire `filtre_date` sous le champ `dates`.

    Variables globales :
    --------------------
    - `version` : titre de la fenêtre (doit être défini avant l'appel à cette fonction).

    Paramètres de l'interface graphique :
    -------------------------------------
    - `sg.Text('Indiquer la période de la recherche au format JJ/MM/AAAA')` : instruction pour l'utilisateur.
    - `sg.CalendarButton` : bouton pour sélectionner une date via un calendrier.
    - `sg.In(key='-CAL1-')` : champ pour afficher la date de début sélectionnée.
    - `sg.In(key='-CAL2-')` : champ pour afficher la date de fin sélectionnée.

    Structure des filtres de date :
    -------------------------------
    - `filtre_date` : dictionnaire contenant le filtre de date, avec les clés :
        - 'facette' : identifiant du type de filtre (ici, 'DATE_SIGNATURE').
        - 'dates' : sous-dictionnaire contenant :
            - 'start' : date de début au format AAAA-MM-JJ.
            - 'end' : date de fin au format AAAA-MM-JJ.

    Gestion des erreurs :
    ---------------------
    - Si l'utilisateur ne saisit pas les dates correctement, un message d'erreur est affiché
      pour demander une correction. La validation du format est faite avec une expression régulière.

    Retourne :
    ---------
    list
        Une liste contenant un dictionnaire `filtre_date` avec les informations de la période de recherche.

    Notes :
    ------
    - `sg` doit être importé depuis `PySimpleGUI` avant d'utiliser cette fonction.
    - `re` doit être importé pour la validation du format de date.
    - La variable globale `version` doit être définie pour que la fonction fonctionne correctement.
    - Utilisation du module leginorma, modifiée

    """


def requete():
"""
    Définit et exécute une requête de recherche avec possibilité d'importer une requête JSON préexistante.

    Cette fonction utilise une interface graphique pour permettre à l'utilisateur de créer une requête de recherche
    ou d'importer une requête à partir d'un fichier JSON. Elle utilise des paramètres spécifiques d'API pour interroger
    une base de données juridique et retourne les identifiants des textes trouvés.

    Variables globales :
    --------------------
    - `version` : titre de la fenêtre (doit être défini avant l'appel à cette fonction).

    Processus de la fonction :
    --------------------------
    1. **Sélection de la méthode de recherche** :
       - L'utilisateur choisit entre une recherche manuelle ou l'importation d'une requête JSON.
    2. **Importation de la requête JSON** :
       - Si un fichier JSON est importé, la fonction vérifie sa validité. Un message d'erreur est affiché si le fichier est incorrect.
    3. **Définition de la requête manuelle** :
       - La fonction appelle d'autres fonctions (`fonds`, `champs`, `filtres`) pour recueillir les informations nécessaires.
       - La requête est structurée avec des paramètres spécifiques pour l'API, tels que le type de pagination, le nombre de résultats par page, et les filtres.
    4. **Exécution de la requête** :
       - La fonction utilise `client.search()` pour récupérer les résultats par page (100 résultats maximum par page).
       - Elle assure la complétion de la récupération en relançant les requêtes si certains résultats manquent.
    5. **Export de la requête** :
       - Une fois la recherche terminée, l'utilisateur peut choisir d'exporter la requête dans un fichier JSON.

    Structure de `search_dic` :
    ---------------------------
    1) fond
    2) recherche
        2.1) filtres
            2.1.1) facette du filtre
            2.1.2) dates
                2.1.2.1) date de début
                2.1.2.2) date de fin
    3) opérateur (ET/OU)
    4) page à afficher
    5) nombre de textes par page
    6) critère de recherche 1
    7) critère de recherche 2
    8) type de pagination
    9) champ de la recherche (plusieurs champs possibles)
        9.1) champ n° X de la recherche
            9.1.1) opérateur (ET/OU)
            9.1.2) type de champ de recherche
            9.1.3) critères de recherche (plusieurs critères possibles)
                9.1.3.1) critère n° X correspondant au champ n° X
                    9.1.3.1.1) type de recherche
                    9.1.3.1.2) valeur (mots clefs de la recherche pour ce critère)
                    9.1.3.1.3) opérateur (ET/OU)

    Gestion des erreurs :
    ---------------------
    - Affiche des messages d'erreur si la requête JSON est invalide ou si un champ requis est manquant.
    - Si la récupération des résultats est incomplète, un message informe l'utilisateur et relance la requête.

    Retourne :
    ---------
    list
        Une liste contenant les identifiants des textes trouvés.

    Notes :
    ------
    - `sg` doit être importé depuis `PySimpleGUI` avant d'utiliser cette fonction.
    - `json` doit être importé pour lire et écrire des fichiers JSON.
    - `client.search()` est une méthode modifiée de leginorma pour exécuter la requête.

    """

######################################################################
#       Définition des fonctions d'extraction des textes             #
######################################################################

# Objectif : à partir d'une liste d'ids, récupérer le contenu des textes.


def retrieve(id, dics):
    """
    Récupère les informations d'un texte via une API si ce texte n'est pas déjà dans la liste des textes récupérés.

    Cette fonction vérifie si un texte spécifique, identifié par `id`, est déjà présent dans la liste `dics`.
    Si le texte est absent, la fonction interroge l'API pour obtenir les informations du texte et l'ajoute à la liste.
    La fonction utilise également une fonction de progression pour indiquer l'avancement de la récupération.

    Paramètres :
    -----------
    id : str
        Identifiant unique du texte à récupérer.

    dics : list
        Liste des dictionnaires de textes déjà récupérés. Chaque dictionnaire dans cette liste contient un texte
        identifié par la clé `'cid'`.

    Utilisation :
    -------------
    - La fonction commence par générer une liste `dics_ids` contenant les identifiants (`cid`) des textes déjà dans `dics`.
    - Si `id` n'est pas dans `dics_ids`, la fonction utilise `client.consult_jorf(id)` pour obtenir le texte et l'ajoute à `dics`.

    Retourne :
    ---------
    list
        La liste `dics` mise à jour avec le texte récupéré, le cas échéant.

    Notes :
    ------
    - `progression(len(ids))` est appelée pour indiquer l'avancement de la récupération.
    - `client.consult_jorf(id)` est une méthode modifiée de leginorma pour récupérer les informations du texte.

    """


######################################################################
#     Définition des fonctions de création de la base de données     #
######################################################################

def date_format(date):
    """
    Convertit une chaîne de caractères représentant une date en un objet `datetime`, prenant en charge deux formats de date.

    Cette fonction tente de convertir une date fournie sous forme de chaîne de caractères en un objet `datetime`.
    Elle gère les formats de date suivants :
    1) "Jour Mois Année" (exemple : "12 janvier 2024").
    2) "AAAA-MM-JJ" (exemple : "2024-01-12").

    La fonction utilise un dictionnaire `months` pour remplacer les noms de mois en français par leur équivalent pour
    un traitement homogène.

    Paramètres :
    -----------
    date : str
        Chaîne de caractères représentant une date, soit sous le format "Jour Mois Année", soit sous le format "AAAA-MM-JJ".

    Variables requises :
    --------------------
    - `months` : dictionnaire mappant les noms de mois en français vers leurs équivalents en anglais
      pour que `strptime` puisse interpréter les dates correctement.

    Retourne :
    ---------
    datetime
        L'objet `datetime` correspondant à la date fournie.

    Gestion des erreurs :
    ---------------------
    - Si le format "Jour Mois Année" ne peut pas être interprété, la fonction tente le format "AAAA-MM-JJ".
    - Si aucun format n'est compatible, une exception sera levée.

    Notes :
    ------
    - `datetime` doit être importé depuis le module `datetime`.
    - Le dictionnaire `months` doit être défini avant d'utiliser la fonction.

    """


def date_to_string(date):
    """
    Convertit une date au format `datetime` en une chaîne de caractères au format "JJ/MM/AAAA".

    Cette fonction prend un objet `datetime` et le convertit en chaîne de caractères.
    Si `date` est déjà une chaîne (par exemple, si la date est vide ou déjà formatée),
    la fonction la retourne inchangée.

    Paramètres :
    -----------
    date : `datetime` ou str
        La date à convertir. Elle est au format `datetime` pour la conversion,
        mais peut aussi être une chaîne déjà formatée.

    Retourne :
    ---------
    str
        La date sous forme de chaîne au format "JJ/MM/AAAA", ou la date inchangée si elle est déjà une chaîne.

    Gestion des erreurs :
    ---------------------
    - Si `date` est déjà une chaîne ou un objet incompatible avec `strftime`, la fonction la retourne sans modification.

    Notes :
    ------
    - `datetime` doit être importé depuis le module `datetime` si vous travaillez avec des objets `datetime`.
    - Cette fonction est utile pour formater des dates dans des affichages ou exports en texte.

    """


def balises(text, action = 'clean'):
    """
    Nettoie les balises HTML dans une chaîne de caractères en fonction de l'action spécifiée.

    Cette fonction cherche toutes les balises HTML dans le texte donné et les traite selon deux options :
    1) `clean` : supprime complètement les balises HTML du texte.
    2) `replace` : remplace chaque balise HTML par le caractère `|`.

    La fonction effectue également quelques remplacements pour supprimer les espaces insécables et les espaces
    multiples, en rendant le texte plus lisible.

    Paramètres :
    -----------
    text : str
        Le texte contenant des balises HTML à nettoyer.

    action : str, optionnel
        Action à effectuer sur les balises HTML, soit :
        - `'clean'` : supprime les balises (par défaut).
        - `'replace'` : remplace chaque balise par `|`.

    Retourne :
    ---------
    str
        Le texte nettoyé, avec les balises supprimées ou remplacées selon l'option choisie.


    Notes :
    ------
    - La fonction utilise `re.findall` pour identifier les balises HTML sous le format `<...>`.
    - `chr(160)` est remplacé par un espace standard pour supprimer les espaces insécables.
    - Plusieurs remplacements sont effectués pour éviter les espaces multiples consécutifs.

    """


def signers(excerpt):
    """
    Nettoie et extrait les noms des signataires d'un extrait de texte.

    Cette fonction prend un extrait de texte contenant les signataires et utilise une série de traitements pour :
    1) Nettoyer les balises HTML et autres caractères indésirables.
    2) Extraire les noms des signataires.
    3) Appliquer des corrections et des normalisations pour uniformiser le format des noms.

    Paramètres :
    -----------
    excerpt : str
        Le texte contenant les signataires, potentiellement avec des balises HTML et des mots-clés.

    Processus de la fonction :
    --------------------------
    - Utilise `balises(excerpt, 'replace')` pour remplacer les balises HTML par `|`.
    - Identifie la section contenant les signataires via une expression régulière ciblant les formats typiques de signatures.
    - Effectue un traitement pour extraire les noms individuels des signataires.
    - Normalise les noms en remplaçant certains termes communs par des variantes standardisées (par exemple, 'Le ministre' devient 'Ministre').

    Retourne :
    ---------
    str
        Une chaîne de caractères avec les noms des signataires, séparés par des `|` pour une présentation uniforme.

    Gestion des erreurs :
    ---------------------
    - Si une erreur se produit (par exemple, si l'extrait n'a pas le format attendu), la fonction retourne une chaîne vide.

    Notes :
    ------
    - La fonction `balises` est utilisée pour nettoyer les balises HTML.
    - Plusieurs remplacements de chaînes sont effectués pour homogénéiser le format des noms des signataires.

    """


def nominations_multiples(dic):
    """
    Vérifie si un texte contient plusieurs nominations.

    Cette fonction détecte la présence de plusieurs nominations dans les sections d'un dictionnaire
    en recherchant des occurrences de mots indiquant une nomination (par exemple, "nommé" ou "nommés").
    Elle retourne `True` si plus d'une nomination est détectée, indiquant des nominations multiples.

    Paramètres :
    -----------
    dic : dict
        Un dictionnaire contenant les sections de texte à analyser pour les nominations.
        Il doit inclure les clés suivantes :
        - `'Texte_article_1'`
        - `'Texte_article_2'`
        - `'Autre_article_nomination'`

    Détails de fonctionnement :
    ---------------------------
    - La fonction concatène les valeurs des trois clés en une seule chaîne de texte.
    - Elle recherche ensuite les occurrences de "nommé" (incluant "nommée") et "nommés".
    - Si plus d'une occurrence de "nommé(e)" ou une occurrence de "nommés" est détectée,
      la fonction retourne `True`, indiquant des nominations multiples. Sinon, elle retourne `False`.

    Retourne :
    ---------
    bool
        `True` si plusieurs nominations sont détectées, sinon `False`.

    Notes :
    ------
    - La fonction utilise `re.findall` pour compter les occurrences de "nommé(e)".
    - La recherche de "nommés" est effectuée séparément, car elle indique directement des nominations multiples.

    """


def analyse_patronyme(patronyme_string, capsname = False):
"""
    Extrait le nom et le prénom d'un patronyme donné.

    Cette fonction prend une chaîne de caractères représentant un nom complet (patronyme)
    et utilise des expressions régulières pour extraire séparément le prénom et le nom de famille.
    Elle prend en compte deux formats différents :
    - Format normal (par défaut).
    - Format majuscules (si `capsname=True`), pour les noms entièrement en majuscules.

    Paramètres :
    -----------
    patronyme_string : str
        La chaîne de caractères contenant le nom complet de la personne (prénom et nom).

    capsname : bool, optionnel
        Indique si le patronyme est entièrement en majuscules. Si `True`, la fonction
        applique un traitement différent pour les noms en majuscules. Par défaut, `False`.

    Retourne :
    ---------
    tuple
        Un tuple contenant le prénom et le nom extraits sous forme de chaînes de caractères.

    Détails de fonctionnement :
    ---------------------------
    - **Format normal** (`capsname=False`) :
        - La fonction utilise une expression régulière pour détecter les patronymes avec des noms et prénoms
          commençant par une majuscule suivie de minuscules, et des noms de famille possibles avec des particules
          comme "de", "du", etc.
    - **Format majuscules** (`capsname=True`) :
        - La fonction remplace les particules en minuscules par leurs équivalents en majuscules avant de procéder
          à l'extraction des noms et prénoms.

    Notes :
    ------
    - La fonction retourne le prénom et le nom extraits selon le format du patronyme.
    - Elle utilise `re.findall` pour correspondre aux noms et prénoms et suppose que le patronyme est bien formé.

    """


def capitalize_name(nom_string):
"""
    Met une majuscule au début de chaque composant du nom de famille.

    Cette fonction prend une chaîne de caractères représentant un nom de famille et s'assure que chaque composant
    du nom commence par une majuscule. Elle gère les noms composés, incluant ceux avec des traits d'union.

    Paramètres :
    -----------
    nom_string : str
        Chaîne de caractères représentant un nom de famille, qui peut être composé d'un ou plusieurs mots
        (séparés par des espaces ou des traits d'union).

    Retourne :
    ---------
    str
        Le nom formaté avec une majuscule au début de chaque composant.

    Détails de fonctionnement :
    ---------------------------
    - La fonction sépare le nom en composants individuels par des espaces.
    - Pour chaque composant :
        - Si le composant est en majuscules, il est mis en majuscule initiale.
        - Si le composant contient un trait d'union, chaque sous-composant est également mis en majuscule initiale.
    - Les composants sont ensuite recombinés avec des espaces.

    Notes :
    ------
    - Cette fonction gère uniquement les noms en majuscules ou en minuscules complètes; elle ne modifie pas les noms déjà correctement formatés.

    """


def coherence_patro_nom_prenom(patronyme, nom, prenom):
    """
    Vérifie la cohérence entre le patronyme et les valeurs séparées du prénom et du nom.

    Cette fonction compare un patronyme complet avec un prénom et un nom fournis séparément pour vérifier leur correspondance.
    Si le patronyme est une combinaison exacte du prénom et du nom, la fonction retourne `'oui'`.
    Si une différence d'un seul caractère est détectée (erreur typographique), la fonction retourne également `'oui'`.
    Dans les autres cas, elle retourne `'non'`.

    Paramètres :
    -----------
    patronyme : str
        Le nom complet (prénom + nom) sous forme de chaîne de caractères.

    nom : str
        Le nom de famille.

    prenom : str
        Le prénom.

    Retourne :
    ---------
    str
        - `'oui'` si le patronyme est cohérent avec le prénom et le nom.
        - `'non'` si une incohérence majeure est détectée.
        - `''` si l'un des champs est vide.

    Détails de fonctionnement :
    ---------------------------
    - La fonction concatène le prénom et le nom (en minuscules) et les compare avec le patronyme (en minuscules).
    - Si les chaînes ne correspondent pas, la fonction effectue une vérification de "typos" en comptant les différences de caractères.
    - Si une seule différence de caractère est détectée, la fonction considère que le patronyme est cohérent.

    Notes :
    ------
    - La fonction retourne une chaîne vide si le patronyme, le prénom ou le nom est vide.

    """


def vigueur(input_dic):
    """
    Détermine et attribue la date d'entrée en vigueur d'un texte en fonction des dates disponibles.

    Cette fonction établit la date d'entrée en vigueur en fonction des informations présentes dans le dictionnaire
    `input_dic`. Si une "Date_d'effet" est fournie, elle est formatée et utilisée comme date d'entrée en vigueur.
    Si la "Date_d'effet" est absente, mais que la date de publication (date_JORF) est disponible, la date d'entrée en
    vigueur est fixée au lendemain de la date de publication.

    Paramètres :
    -----------
    input_dic : dict
        Dictionnaire contenant les informations nécessaires pour déterminer la date d'entrée en vigueur.
        Il doit inclure les clés suivantes :
        - `"Date_d'effet"` : chaîne de caractères représentant la date d'effet (peut être vide).
        - `'date_JORF'` : date de publication au Journal Officiel, au format `datetime` ou chaîne vide.

    Retourne :
    ---------
    dict
        Le dictionnaire `input_dic` mis à jour avec la clé `'Entrée_en_vigueur'`, qui contient la date d'entrée en vigueur.

    Gestion des cas :
    -----------------
    - Si `"Date_d'effet"` est renseignée, elle est utilisée comme date d'entrée en vigueur après formatage.
    - Si `"Date_d'effet"` est vide et `date_JORF` est une date valide (non-chaîne), la date d'entrée en vigueur est fixée au lendemain de `date_JORF`.
    - Si aucune date n'est disponible, la clé `'Entrée_en_vigueur'` est définie comme une chaîne vide.

    Notes :
    ------
    - La fonction utilise `date_format` pour convertir `"Date_d'effet"` si elle est au format chaîne.
    - `datetime.timedelta(days=1)` est utilisé pour calculer le lendemain de `date_JORF`.

    """


def flag(dic, url_to_check=''):
    """
    Déclenche des alertes pour les situations nécessitant une vérification manuelle.

    Cette fonction vérifie plusieurs conditions dans les informations d'un dictionnaire (`dic`) représentant une ligne
    du fichier CSV final. Elle génère des alertes si certaines conditions ne sont pas remplies, indiquant qu'une
    vérification manuelle est recommandée. Une URL optionnelle peut être utilisée pour vérifier les risques d'homonymie.

    Paramètres :
    -----------
    dic : dict
        Dictionnaire contenant les informations de la ligne du CSV. Il doit inclure les clés suivantes :
        - `'Correspondance_Patronyme_avec_Prénom_et_Nom'`
        - `'Civilité'`
        - `'Poste'`

    url_to_check : str, optionnel
        Si l'URL est fournie, la fonction utilise une requête pour détecter la présence d'homonymes.

    Vérifications effectuées :
    --------------------------
    1. **Nominations multiples** : Utilise `nominations_multiples(dic)` pour vérifier si plusieurs nominations sont présentes dans le texte.
    2. **Cohérence patronyme-prénom-nom** : Vérifie si `'Correspondance_Patronyme_avec_Prénom_et_Nom'` est `'non'` ou vide.
    3. **Civilité manquante** : Vérifie si la clé `'Civilité'` est vide.
    4. **Risque d'homonymie** : Si une URL est fournie, la fonction fait une requête GET pour vérifier la présence du mot "homonymes".
    5. **Poste manquant** : Vérifie si la clé `'Poste'` est vide.

    Retourne :
    ---------
    dict
        Le dictionnaire `dic` mis à jour avec une clé `'Alerte'` qui contient les alertes sous forme de chaîne de caractères,
        avec chaque alerte séparée par un `|`.

    Notes :
    ------
    - `requests` doit être importé pour les vérifications d'URL.
    - Cette fonction est utile pour alerter les utilisateurs des incohérences ou données manquantes
      avant l'enregistrement final des informations.

    """


def gender_control(text_to_check):
    """
    Détermine la civilité (Monsieur/Madame) en analysant les marqueurs de genre présents dans un texte.

    Cette fonction vise à identifier la civilité d'une personne mentionnée dans un décret en se basant sur la présence
    de marqueurs de genre (`M.` pour Monsieur et `Mme` pour Madame). Elle traite les cas où plusieurs marqueurs
    sont présents et tente de déduire la civilité correcte en tenant compte des contextes de nomination (`nommé` pour
    masculin et `nommée` pour féminin).

    Paramètres :
    -----------
    text_to_check : str
        Le texte dans lequel la civilité est recherchée. Ce texte peut inclure des marqueurs de genre et
        des contextes de nomination.

    Retourne :
    ---------
    str
        La civilité déterminée :
        - `'Monsieur'` ou `'Madame'` si un genre unique ou une logique contextuelle permet de la déduire.
        - `None` si la civilité ne peut pas être déterminée avec certitude.

    Détails de fonctionnement :
    ---------------------------
    1. **Remplacement de termes** : Remplace les occurrences de "Monsieur" et "Madame" par leurs abréviations ("M." et "Mme").
    2. **Cas de civilité unique** : Si un seul marqueur est trouvé, il est utilisé pour déterminer la civilité.
    3. **Cas de multiples marqueurs** :
       - Si tous les marqueurs sont identiques, utilise ce marqueur pour la civilité.
       - Si les marqueurs sont mixtes, vérifie le premier marqueur et le contexte de nomination :
           - Si le premier marqueur est "Mme" et "nommée" est présent, la civilité est "Madame".
           - Si le premier marqueur est "M." et "nommé" est présent, la civilité est "Monsieur".
       - Si aucune de ces règles ne s'applique, la fonction retourne `None`.

    Notes :
    ------
    - La fonction utilise `re.findall` pour détecter et compter les occurrences des marqueurs.
    - La civilité est basée sur la première occurrence lorsque les marqueurs sont mixtes et les contextes de nomination.

    """


def patronyme(text_to_check):
"""
    Extrait et formate le patronyme d'une personne à partir d'un texte.

    Cette fonction analyse un texte pour extraire le patronyme (nom complet) d'une personne,
    en utilisant des marqueurs tels que "M." pour Monsieur et "Mme" pour Madame. Elle applique
    des règles de nettoyage et de formatage pour obtenir un nom correctement capitalisé.

    Paramètres :
    -----------
    text_to_check : str
        Le texte contenant potentiellement le patronyme. Le texte peut inclure des informations supplémentaires
        comme des grades et des titres qui seront supprimés.

    Retourne :
    ---------
    str
        Le patronyme formaté avec les noms et prénoms capitalisés. Si le patronyme ne peut être déterminé,
        retourne une chaîne vide.

    Détails de fonctionnement :
    ---------------------------
    1. **Remplacement de termes** : Remplace "Monsieur" et "Madame" par leurs abréviations.
    2. **Extraction du patronyme** : Utilise `re.findall` pour extraire le patronyme en se basant sur les marqueurs
       de genre et des séparateurs (`est` ou `,`).
    3. **Suppression des grades** : Retire les titres de grade spécifiés dans la liste `grades`.
    4. **Gestion des prénoms entre parenthèses** : Si un prénom est entre parenthèses, il est placé avant le nom.
    5. **Formatage** : Capitalise chaque partie du nom, en gérant les noms composés avec des traits d'union.

    Notes :
    ------
    - `grades` doit être défini comme une liste de chaînes représentant les titres de grade à retirer du texte.
    - La fonction retourne une chaîne vide si aucun patronyme ne peut être extrait du texte.

    """


######################################################################
#  Définition des fonctions d'analyse de la source complémentaire    #
######################################################################


def date_carriere(carriere, maj):
"""
    Formate les dates de début et de fin de chaque étape de carrière d'une personne.

    Cette fonction prend une chaîne décrivant la carrière d'une personne, qui inclut des dates sous divers formats,
    et la reformate en une structure cohérente. Les formats de date sont standardisés pour faciliter la lecture et
    interpréter les dates incomplètes (par exemple, uniquement l'année ou le mois et l'année).

    Paramètres :
    -----------
    carriere : str
        Chaîne de caractères décrivant la carrière, incluant les dates de début et de fin au format brut.

    maj : datetime
        Date de dernière mise à jour de la fiche, utilisée lorsque le poste est en cours (marqué comme "depuis").

    Retourne :
    ---------
    str
        La chaîne de carrière formatée, où chaque étape est séparée par des `|` et les dates sont au format
        "JJ/MM/AAAA" ou "le JJ/MM/AAAA".

    Détails de fonctionnement :
    ---------------------------
    1. **Conversion initiale** : Transforme les séparateurs `/` et `|` en segments de dates (par exemple, 'du ... au ...').
    2. **Gestion des postes en cours** : Remplace les dates en cours par la date de mise à jour (`maj`).
    3. **Formats de date** :
       - Convertit les formats "AAAA, JJ mois", "AAAA, mois", et "AAAA" en formats complets "JJ/MM/AAAA".
       - Prend le premier jour du mois pour les dates ne précisant que le mois, et le 1er janvier pour les dates
         ne précisant que l'année.
    4. **Cas particuliers** :
       - Une seule date : Formatée comme "le JJ/MM/AAAA".
       - Date de fin incomplète (par exemple, "jusqu'en AAAA") : Ajoute la date finale de l'année ou du mois en question.

    Exceptions gérées :
    -------------------
    - La fonction vérifie et ignore les étapes sans format de date valide, en les laissant inchangées.
    - Si une étape contient des informations incomplètes sur les dates (par exemple, juste un mois), elle remplace par une date par défaut (voir ci-dessus).

    Notes :
    ------
    - `date_format` et `date_to_string` doivent être définies pour formater et convertir les dates.
    - Cette fonction est utile pour harmoniser les étapes de carrière, en particulier dans le contexte des CV et des documents officiels.

    """


def get_excerpt(input_url):
"""
    Isole un extrait de texte spécifique de la page de la source complémentaire à partir de l'URL donnée.

    Cette fonction envoie une requête GET vers la page spécifiée, récupère le contenu HTML, puis extrait
    deux sections spécifiques :
    1) `meta` : le titre de la page pour obtenir des informations de contexte.
    2) `excerpt` : l'extrait de texte principal, qui sera utilisé pour l'analyse.

    Paramètres :
    -----------
    input_url : str
        URL de la page à analyser.

    Retourne :
    ---------
    tuple
        Un tuple contenant :
        - `meta` : Chaîne de caractères avec le titre de la page.
        - `excerpt` : Extrait principal pour analyse.

    Détails de fonctionnement :
    ---------------------------
    - **Requête HTTP** : Utilise une session HTTP pour envoyer une requête GET à l'URL fournie.
    - **Décodage HTML** : Utilise `html.unescape` pour convertir les entités HTML en texte lisible.
    - **Extraction** :
        - `meta` : Extrait le contenu entre deux balises.
        - `excerpt` : Extrait le texte principal aligné à gauche, entre deux balises.

    Notes :
    ------
    - `s` doit être défini en tant que session HTTP (`requests.Session()`).
    - `html` doit être importé pour `html.unescape`.

    """


def get_corps_sortie_ena(poste_sortie):
"""
    Détermine le corps de sortie de l'ENA d'un individu en fonction de son poste de sortie.

    Cette fonction analyse une chaîne de caractères décrivant le poste ou le corps de sortie d'un
    diplômé de l'ENA et renvoie le corps de sortie correspondant. Elle utilise des mots-clés pour
    identifier le corps de sortie en fonction du type d'affectation (par exemple, Inspection générale
    des finances, Conseil d'État).

    Paramètres :
    -----------
    poste_sortie : str
        Description du poste ou corps de sortie (par exemple, "secrétaire des affaires étrangères").

    Retourne :
    ---------
    str
        Le corps de sortie de l'ENA correspondant, si identifiable. Retourne une chaîne vide si aucun
        corps de sortie n'est détecté.

    Détails de fonctionnement :
    ---------------------------
    - La fonction utilise une série de conditions `elif` pour associer des mots-clés dans `poste_sortie`
      à des corps de sortie précis.
    - Elle analyse des termes comme "inspecteur", "conseil d'état", "affaires étrangères", etc., et
      retourne la correspondance la plus spécifique.

    Cas spécifiques traités :
    -------------------------
    - **Affaires étrangères** : différenciation entre secrétaires et conseillers.
    - **Inspections générales** : inspection de l'administration, des finances, des affaires sociales, etc.
    - **Autres postes** : Conseil d'État, Cour des comptes, chambres régionales des comptes, etc.

    Notes :
    ------
    - Cette fonction est spécifique aux corps de sortie de l'ENA et peut être adaptée si de nouvelles catégories
      sont nécessaires.

    """


def biographies(dic):
    """
    Recherche et analyse des informations de biographie pour un nom spécifique sur la source complémentaire.

    La fonction effectue une recherche en ligne pour vérifier si le patronyme (nom de famille) est présent sur
    la source complémentaire et compare les informations trouvées avec celles du dictionnaire de données `dic`.
    Elle détecte et signale les possibles faux positifs et alerte si le patronyme ou les éléments associés ne correspondent pas entièrement.

    Paramètres :
    -----------
    dic : dict
        Dictionnaire de données contenant des informations telles que le patronyme, la civilité et le poste,
        ainsi que des champs vides pré-formatés pour la sortie, afin de conserver une structure cohérente
        même si des informations sont absentes.

    Retourne :
    ---------
    dict
        Le dictionnaire enrichi avec des données trouvées sur la source complémentaire, y compris les détails de la carrière,
        la date de naissance, le lieu de naissance, et un indicateur de correspondance pour détecter les homonymes potentiels.

    Détails de fonctionnement :
    ---------------------------
    1. **Initialisation et structure des données** :
       - La fonction initialise les champs de sortie dans `dic` pour structurer les données indépendamment de leur présence.
       - Si `Patronyme` est vide dans `dic`, la fonction ne procède pas à la recherche et retourne `dic` sans effectuer d’autres opérations.

    2. **Recherche initiale avec le patronyme** :
       - Le `Patronyme` est nettoyé des apostrophes (remplacées par des espaces).
       - Le lien de recherche est créé.
       - Une requête GET est envoyée pour récupérer les résultats sous forme de texte HTML.
       - Si "Aucun résultat" est trouvé dans le texte, la fonction arrête la recherche pour ce dictionnaire et retourne `dic` sans modification.

    3. **Vérification de correspondance avec marge d'erreur** :
       - Le nombre de résultats est extrait, ainsi qu’une liste d'extraits.
       - Pour chaque extrait trouvé :
           - Le nom complet est extrait et comparé au `Patronyme`.
           - La comparaison utilise un "typo check" avec une tolérance de 3 caractères de différence (calculée par comparaison caractère par caractère entre le nom et le `Patronyme`).
       - Si le nom extrait correspond au `Patronyme` (typo check ≤ 3), l’URL du profil est extraite et enregistrée.
       - Si plusieurs correspondances sont trouvées, la plus précise est choisie en comparant la correspondance avec les informations de poste. Pour cela,
       on calcule un indice de certitude d'homonymie (ICHB) pour évaluer la similarité des biographies.

    4. **Recherche alternative avec sous-parties du patronyme ou le nom complet** :
       - Si le patronyme n'a pas permis d'identifier une correspondance unique et valide :
           - Si le `Nom` dans `dic` est vide et que `Patronyme` comporte plusieurs éléments (ex. nom composé ou titre de noblesse), la recherche utilise seulement la partie du patronyme la plus probable (en général, le nom de famille).
           - Si le `Nom` est présent dans `dic`, une recherche est effectuée uniquement avec le `Nom`.
       - Ce processus est répétitif : la recherche est réinitialisée à chaque étape si aucun résultat pertinent n’est trouvé et que la page contient plus de 50 résultats.

    5. **Analyse détaillée du contenu de la biographie** :
       - Lorsque l’URL du profil est trouvée, la fonction `get_excerpt` est appelée pour extraire le titre de la page (métadonnées) et un extrait de la page.
       - Les informations suivantes sont extraites et nettoyées :
           - **Civilité** : Extraite du titre de la page (`Monsieur` ou `Madame`). Si non trouvée, on recherche dans l'extrait (`Né` pour homme, `Née` pour femme).
           - **Nom et Prénom** : Le `Patronyme` est analysé et segmenté en `Nom` et `Prénom` par `analyse_patronyme`.
           - **Date et lieu de naissance** : Extraits à partir de motifs textuels (`Né le JJ/MM/AAAA`) avec gestion des formats incomplets (ex. uniquement mois et année).
           - **Ville et Département de naissance** : Extraits de l’information de naissance ; le département est séparé de la ville pour les départements français.

    6. **Extraction des étapes de carrière et autres informations** :
       - Les informations sont segmentées en sections spécifiques par `#` et `|`.
       - Chaque section est traitée individuellement pour identifier le type d’information, en fonction des termes dans `types_datas` :
           - **Étapes de carrière** : Extraites et formatées par la fonction `date_carriere`.
           - **Autres types** (`Informations diverses`, `Parentés`, `Adresses`) :
               - `Informations diverses` : S'il s'agit d'une formation à l'ENA, l'année de sortie est vérifiée et ajoutée.
               - `Parentés` : Gère les liens familiaux (`Père`, `Mère`, `Frère`, etc.), en comptant chaque occurrence.
               - `Adresses` : Extrait les informations de contact (`Tél`, `Courriel`) et les adresse dans des colonnes distinctes.

    7. **Vérification des étapes de carrière pour l’ENA** :
       - Si une mention de l'ENA comme école figure dans `Formation` ou `Etapes de carrière`, la fonction :
           - Récupère l'année de sortie et le corps d’affectation.

    8. **Contrôles de cohérence et alertes** :
       - La cohérence est vérifiée entre les informations `Civilité`, `Patronyme`, et `ICHB` :
           - Si des incohérences ou des correspondances partielles sont détectées, des alertes sont ajoutées dans `b_alerte`.
       - Si le `Poste` dans `dic` ne correspond pas aux étapes de carrière trouvées, une alerte est également signalée.

    9. **Gestion des erreurs et exceptions** :
       - Si une exception se produit lors de l’analyse ou de la recherche, un message d'erreur est affiché avec l'URL pour permettre le débogage.
       - Les clés temporaires sont supprimées avant de retourner `dic`.


    Étapes de Calcul de l'ICHB
    --------------------------
    L'ICHB est un indicateur exprimé en pourcentage qui mesure la probabilité qu'une biographie trouvée sur la source complémentaire
    corresponde à la personne recherchée. Il est calculé en fonction de la similitude des informations entre deux biographies
    (précédemment trouvée et nouvelle candidate). L’ICHB aide à déterminer si deux entrées biographiques pourraient se référer
    au même individu malgré d’éventuelles différences dans les détails.

    1. **Définition des Éléments de Correspondance** :
       - L'ICHB prend en compte deux types de correspondances pour déterminer la similitude :
         a) Correspondance de l'année et du poste : Priorise une correspondance exacte des postes et de l'année.
         b) Correspondance uniquement sur le poste : Considère la correspondance des postes, indépendamment de l'année.

    2. **Évaluation des Correspondances** :
       - Les scores sont attribués pour chaque biographie (0 pour la biographie précédemment trouvée, 1 pour la nouvelle candidate).
       - Pour chaque biographie, on recherche dans le texte de la carrière si :
         - a) L'année et le poste correspondent exactement à ceux indiqués dans `dic['Entrée_en_vigueur']` et `dic['Poste']`.
            - Si une correspondance exacte est trouvée, le score est fixé à 9999.
            - Si seulement une partie des mots du poste correspond, un score pondéré est calculé en fonction du nombre de mots trouvés,
              doublant ce score pour les correspondances avec année.
         - b) La correspondance des mots du poste uniquement est recherchée sans tenir compte de l’année :
            - Un score inférieur (999 maximum) est attribué en fonction du nombre de mots du poste correspondants.

    3. **Calcul du Pourcentage d'ICHB** :
       - Une fois les scores attribués pour les deux biographies (précédente et candidate), on calcule l'ICHB.
       - Si les scores des deux biographies sont identiques, l'ICHB est fixé à 0 %, indiquant l'impossibilité de départager les deux biographies.
       - Sinon, l'ICHB est calculé en utilisant le ratio entre les deux valeurs :
       - Cette formule donne un pourcentage représentant la certitude de correspondance, en privilégiant les entrées avec un score élevé.
       - L'ICHB est ainsi retourné en pourcentage, avec un maximum de 100 % indiquant une correspondance très probable.
       - Un ICHB de 90 % ou plus suggère une forte correspondance, tandis qu'un score inférieur peut indiquer des différences significatives,
         nécessitant une vérification manuelle.

    Notes :
    ------
    - `s` doit être une session HTTP (`requests.Session()`), et `html` doit être importé pour `html.unescape`.
    - La fonction repose sur plusieurs sous-fonctions et variables globales : `get_excerpt`, `analyse_patronyme`, `date_format`,
      `date_to_string`, `get_corps_sortie_ena`, et `types_datas`.
    - Elle est optimisée pour vérifier des homonymes, analyser les postes de carrière et extraire les informations biographiques, en particulier pour les personnalités publiques.
    """


######################################################################
#                    Début du code principal                         #
######################################################################


# Vérification de l'existence d'un logo image

# Traduction des mois en anglais pour faire fonctionner la fonction 'date_format'
months = {
    'janvier': 'january', 'février': 'february', 'mars': 'march', 'avril': 'april', 'mai': 'may', 'juin': 'june', 'juillet': 'july',
    'août': 'august', 'septembre': 'september', 'octobre': 'october', 'novembre': 'november', 'décembre': 'december'
}


# Dictionnaire des étapes d'exécution du programme
# - Associe chaque étape clé d'exécution à un identifiant unique pour organiser et exécuter des opérations spécifiques.
etapes = {
    "Réinitialiser les identifiants de l'API legifrance" : 'ids', "Obtenir une liste de textes à partir d'une recherche sur legifrance":'etape1',
    "Récupérer le contenu de textes à partir d'une liste d'identifiants" : 'etape2', "Générer une base de données 'textes'" : "etape3",
    'Réinitialiser les identifiants de la source complémentaire' : 'ids_bio', 'Analyse biographique': 'etape4',
    "Quitter l'application" : 'quitter'
}


# Dictionnaire des extensions de fichiers pris en charge pour l'exportation
# - Associe chaque format de fichier descriptif (Excel, JSON, CSV) à son extension pour la sauvegarde.
extensions = {'.xlsx (Excel)': 'xlsx', '.json (JSON)': 'json', '.csv (CSV)': 'csv'}

# Variable initialisée pour garder une trace de l'étape en cours
etape = ''

# Version de l'application
version = 'SIRONA 3.5'

# Contrôles pour les connexions API


# Création des répertoires nécessaires au programme
# - `dirs` : Liste de répertoires requis. Chaque répertoire est créé si inexistant pour organiser les fichiers du programme.
# Ignorer les erreurs si le répertoire existe déjà.


# Configuration de l'interface utilisateur avec un thème spécifique
# - `sg.theme('BrownBlue')` : Définit le thème pour PySimpleGUI.

# dictionnaire contenant les paramètres qui permettent la connexion à l'API

# dictionnaire contenant les paramètres qui permettent la connexion à la source complémentaire

# Chargement des informations d'authentification pour l'API

# Chargement des informations d'authentification pour la source complémentaire


######################################
# Boucle principale de l'application #
######################################

# - La boucle continue tant que `etape` n'est pas défini sur 'quitter', permettant à l'application de fonctionner en continu.

# Choix de l'interface en fonction de la présence du logo :
# - Si `logo` est défini comme `True`, une interface avec un logo est affichée.
# - Si `logo` est `False`, une version sans logo est présentée.

# Affichage de l'interface avec ou sans logo :
# - Dans les deux cas, les éléments d'interface incluent :
#   - Le numéro de version de l'application.
#   - Le titre "Interface de recherche sur Legifrance".
#   - Une liste déroulante des actions disponibles (options dans le dictionnaire `etapes`).
#   - Deux boutons : `Ok` pour valider la sélection et `Quitter` pour sortir de l’application.

# Lecture des événements :
# - Après la configuration de l'interface, l'application attend une réponse de l'utilisateur :
#   - `event` représente l'action réalisée (ex. clic sur 'Ok' ou 'Quitter').
#   - `values` contient les valeurs sélectionnées par l'utilisateur, y compris l'action choisie dans `-LIST-`.

    # Gestion des événements pour la sélection de l'étape ou la fermeture de l'application
    # - Boucle principale qui écoute les événements de la fenêtre de sélection des étapes.
    # - Quitte l'application si la fenêtre est fermée ou si le bouton 'Quitter' est cliqué.

    # Vérification de l'événement "Ok" et d'une sélection dans la liste des étapes :
    # - Si une action est sélectionnée, le type d'étape (`type_etape`) est récupéré depuis la liste.
    # - L'étape correspondante (`etape`) est assignée à partir du dictionnaire `etapes`.
    # - La fenêtre se ferme et sort de la boucle.

    # Gestion des erreurs de sélection :
    # - Si aucune action n'est sélectionnée, un message d'erreur est affiché.

    # Sortie de la boucle :
    # - Quitte l'application si l'étape sélectionnée est 'quitter'.

    # Gestion de l'authentification API pour les étapes `etape1` et `etape2` :
    # - Tente de créer un client de l'API `Legifrance` avec les identifiants (client ID et clé).
    # - En cas d'échec, affiche un message d'erreur.

    # Saisie des identifiants OAuth si nécessaire :
    # - Si les identifiants sont manquants ou invalides, demande à l'utilisateur de saisir le client ID et la clé secrète.
    # - Affiche un message expliquant comment obtenir les identifiants sur le site `piste.gouv.fr`.

    # Lecture des identifiants saisis et tentative de connexion :
    # - Sauvegarde les identifiants `client ID` et `secret key` si l'utilisateur a activé l'option.
    # - Tente de créer un client `LegifranceClient` avec les identifiants fournis.
    # - Si la connexion API réussit, affiche un message de succès.

    # Sauvegarde des identifiants :
    # - Sauvegarde les identifiants dans un fichier JSON pour les futures connexions, si l'option est activée.
    # - Affiche un message d'erreur si les identifiants sont invalides.


    ######################################################################
    #                       Extraction des ids                           #
    ######################################################################

    # Initialisation des variables pour stocker la requête et les identifiants :
    # - `req` détermine si l'utilisateur souhaite poursuivre une nouvelle recherche.
    # - `id_list` stocke les identifiants uniques des textes récupérés.

    # Lancement de la recherche Legifrance si `etape1` est sélectionnée :
    # - Boucle continue jusqu'à ce que l'utilisateur décide d'arrêter les recherches supplémentaires.
    # - Appelle la fonction `requete` pour récupérer temporairement les identifiants de la recherche en cours.
    # - En cas d'échec de la requête, un message d'erreur est affiché.

    # Ajout des identifiants uniques dans `id_list` :
    # - Vérifie que chaque identifiant de `temp_id_list` n'est pas déjà présent dans `id_list`.

    # Confirmation et options de nouvelle recherche :
    # - Affiche le nombre total d'identifiants uniques récupérés.
    # - Propose à l'utilisateur d'effectuer une nouvelle recherche avancée, ajoutant les résultats à la liste actuelle.

    # Sauvegarde de la liste des identifiants dans un fichier JSON si l'étape est 'etape1' :
    # - Affiche une fenêtre demandant le nom de fichier et le dossier de sauvegarde.
    # - Boucle d'attente de saisie pour obtenir le nom et le dossier du fichier.

    # Vérification de la saisie et sauvegarde :
    # - Si l'utilisateur clique sur "Ok" et a renseigné le dossier et le fichier, le chemin complet du fichier JSON est généré.
    # - `id_list` est sauvegardée dans le fichier JSON spécifié.
    # - Affiche une confirmation que la liste a bien été enregistrée.
    # - En cas de nom de fichier ou dossier invalide, un message d'erreur est affiché.

    # Gestion des erreurs et messages d'information :
    # - Messages d'erreur sont affichés si aucun dossier ou nom de fichier n'est sélectionné ou si une exception se produit.


    ######################################################################
    #                     Extraction des textes                          #
    ######################################################################

    # Gestion de l'étape 'etape2' : Chargement d'un fichier contenant une liste d'identifiants
    # - Initialise `dics` pour stocker les dictionnaires de texte et `processes` pour les processus potentiels.
    # - Ferme la fenêtre précédente pour éviter toute interférence.

    # Interface de sélection du fichier contenant les identifiants :
    # - Utilise une fenêtre pour que l'utilisateur puisse sélectionner le fichier JSON contenant les identifiants.
    # - Lit les événements pour détecter la sélection et lecture du fichier.
    # - Charge le fichier JSON et vérifie qu'il contient bien une liste d'identifiants pour l'étape 'etape2'.
    # - Affiche un message d'erreur si le fichier JSON n'est pas valide.

    # Récupération des textes en fonction des identifiants :
    # - Continue d'essayer tant que le nombre de textes récupérés (`dics`) est inférieur au nombre d'identifiants.
    # - Indique le processus de récupération en cours avec une fenêtre d'attente.
    # - Utilise un `ThreadPoolExecutor` pour la fonction `retrieve`, accélérant le processus en lançant des requêtes simultanément.
    # - Réinitialise et affiche un message de progression si tous les textes ne sont pas récupérés.

    # Confirmation de la récupération et sauvegarde des textes :
    # - Affiche une confirmation lorsque tous les textes sont récupérés.
    # - Demande un nom et un dossier de sauvegarde pour le fichier JSON final.
    # - Sauvegarde le fichier si les dossiers et noms sont valides, et affiche un message de réussite.
    # - Propose un dernier message d'erreur si la sauvegarde échoue, ou si les champs requis ne sont pas remplis.


    ######################################################################
    #              Création de la base de données Textes                 #
    ######################################################################


        ######################################################################
        #                   Définition des variables                         #
        ######################################################################

        # Initialisation des variables et structures de données :
        # - `dics` : pour stocker les dictionnaires de texte.
        # - `excluded_texts` : pour lister les textes exclus lors du processus.
        # - `processes` : liste de processus (potentiellement utilisés pour les requêtes multiples).
        # - `output_dics` : pour stocker les dictionnaires de sortie.

        # Installation du cache pour les requêtes afin d'accélérer les accès répétés aux données.

        # Nettoyage des dictionnaires `input_dic` :
        # - `keys_to_remove` contient les clés à exclure des dictionnaires importés pour simplifier le code.
        # - La suppression de ces clés aide à réduire la taille des dictionnaires traités.

        # Liste des grades militaires et civils :
        # - `grades` contient des grades spécifiques qui seront utilisés pour le nettoyage et la structuration des données.
        # - Ces grades aident à identifier les titres professionnels dans les textes et à les retirer pour faciliter l'extraction de noms et de postes.

        # Dictionnaire permettant d'identifier le ministère auteur de l'acte à partir du NOR.
        nors = {
            'ACT': 'Artisanat, commerce et tourisme', 'AFS': 'Affaires sociales et santé', 'AGL': 'Agroalimentaire', 'AGR': 'Agriculture',
            'ANC': 'Anciens combattants', 'APH': 'Solidarités, autonomie et personnes handicapées', 'APP': 'Apprentissage, formation professionnelle',
            'ARC': 'Aménagement du territoire, ruralité et collectivité territoriales', 'ARM': 'Armées', 'ATE': 'Santé et sports', 'BCF': 'Budget, comptes publics et fonction publique',
            'BCR': "Budget, Comptes publics et Réforme de l'État", 'BUD': 'Budget', 'COP': 'Coopération', 'COT': 'Collectivités territoriales',
            'CPA': 'Action et comptes publics', 'DCT': 'Décentralisation', 'DEF': 'Défense', 'DEV': 'Ecologie, développement durable et énergie',
            'DFE': 'Droits des femmes', 'DVT': 'Affaires étrangères, chargé du développement', 'EAE': 'Europe et affaires étrangères', 'EAT': 'Espace rural et aménagement du territoire',
            'ECE': 'Économie, Finances et Emploi', 'ECF': 'Economie et finances', 'ECO': 'Economie', 'EFI': 'Economie et finances', 'EIN': 'Economie, industrie et numérique',
            'EQU': 'Transport, équipement, tourisme et mer', 'ERN': 'Economie, redressement productif et numérique', 'ESR': 'Enseignement supérieur et recherche',
            'ESS': "Economie et finances, chargé de l'économie sociale et solidaire et de la consommation", 'ETL': 'Logement et égalité du territoire',
            'ETS': 'Travail, emploi et dialogue social', 'EUR': 'Affaires européennes', 'EXT': 'Commerce extérieur', 'FAM': 'Famille et Enfance', 'FCP': 'Finances et comptes publics',
            'FDF': 'Familles, enfance et droits des femmes', 'FEF': "Affaires étrangères, Français de l'étranger", 'FPA': 'Travail, emploi, formation professionnelle et dialogue social, chargé de la formation professionnelle et de l’apprentissage',
            'FRA': 'Francophonie', 'FVJ': 'Droits des femmes, ville, jeunesse et sports', 'HAN': "Affaires sociales et santé, chargé des personnes handicapées et de la lutte contre l'exclusion",
            'IMI': 'Immigration, Intégration, Identité nationale et Codéveloppement', 'IND': 'Industrie', 'INT': 'Intérieur', 'IOC': 'Intérieur, Outre-mer et Collectivités territoriales',
            'IOM': 'Intérieur et outre-mer', 'JSA': 'Jeunesse, solidarités actives', 'JUD': 'Justice ministère délégué', 'JUS': 'Justice', 'LHA': 'Logement et habitat durable',
            'LOG': 'Logement', 'MAE': 'Affaires étrangères', 'MCC': 'Culture et communication', 'MEN': 'Education nationale', 'MER': 'Mer', 'MES': 'Emploi et solidarité',
            'MFP': 'Fonction publique', 'MIC': 'Culture', 'MOM': 'Outre-mer', 'MTR': 'Travail', 'MTS': 'Travail, solidarité et fonction publique', 'OME': 'Outre-mer',
            'PAD': "Affaires sociales et santé, chargé des personnes âgées et de l'autonomie", 'PME': "Redressement productif, chargé des petites et moyennes entreprises, de l'innovation et de l'économie numérique",
            'PRL': 'Relations avec le Parlement', 'PRM': 'Premier ministre', 'PRO': 'Redressement productif', 'RDF': 'Décentralisation et fonction publique',
            'RED': 'Education nationale, chargé de la réussite éducative', 'REL': 'Relance', 'SAN': 'Santé', 'SAS': 'Santé et sports', 'SCS': 'Solidarités, cohésion sociale',
            'SJS': 'Sports, jeunesse et santé', 'SOC': 'Action sociale', 'SPO': 'Sports', 'SPR': 'Sports', 'SPS': 'Santé et sports', 'SSA': 'Solidarités et santé', 'TAS': 'Santé et sports',
            'TER': 'Cohésion des territoires et relations avec les collectivités territoriales', 'TFP': 'Transformation et fonction publiques', 'TRA': 'Transports',
            'TRE': 'Transition écologique et solidaire', 'TSP': 'Transformation et la fonction publiques', 'VIL': 'Ville', 'VJS': 'Ville, jeunesse et sports',
            'ACV': 'Anciens combattants et Victimes de guerre', 'ASE': 'Affaires sociales et Emploi', 'ASS': "Relations avec l'Assemblée nationale", 'ATR': 'Aménagement du territoire et Reconversions',
            'AVI': 'Aménagement du territoire, Ville et Intégration', 'FCE': 'Finances et Commerce extérieur', 'FPP': 'Fonction publique', 'ILE': "Intégration et Lutte contre l'exclusion",
            'MLV': 'Logement et Ville', 'RES': 'Recherche et Enseignement supérieur', 'STF': 'Santé et Famille', 'TOU': 'Transport, équipement, tourisme et mer', 'REC': 'Recherche',
            'MJS': 'Jeunesse, sports et vie associative', 'DOM': 'Outre-mer', 'IOG': 'Logement', 'ENV': 'Environnement', 'PTT': 'Postes, télécommunications et espace',
            'TEF': 'Travail, emploi et formation professionnelle', 'MIP': 'Industrie, poste et télécommunications', 'COM': 'Commerce et artisanat', 'PRE': "Départements et territoires d'outre-mer",
            'RDZ': 'Fonction publique'
        }


        # Modifications manuelles pour prendre en compte des exceptions non traitées par le code
        # 'Réservé'

        ######################################################################
        #                       Début de l'analyse                           #
        ######################################################################

        # Chargement du fichier JSON contenant les textes à analyser :
        # - `input_dics` est la variable où le contenu des textes sera chargé.
        # - Ferme la fenêtre actuelle pour afficher la nouvelle interface utilisateur.

        # Interface utilisateur pour le choix du fichier et la gestion du cache :
        # - Présente une option pour sélectionner le fichier contenant les textes et une case à cocher pour vider le cache.
        # - Si l'utilisateur choisit de vider le cache, le fichier `database_cache.sqlite` sera supprimé, ce qui peut prolonger l'analyse mais permet d'utiliser des données actualisées.

        # Boucle d'événements pour la sélection du fichier de texte :
        # - Si l'utilisateur ferme la fenêtre, l'application quitte.
        # - Si "Vider le cache" est coché, tente de supprimer le cache existant (ignore les erreurs).
        # - Lorsque le fichier est sélectionné, ouvre et charge le fichier JSON dans `input_dics`.
        # - Vérifie la validité du fichier en s'assurant qu'il contient une liste et que chaque dictionnaire contient la clé `executionTime`.
        # - Si le fichier est valide, la fenêtre se ferme ; sinon, affiche un message d'erreur.

        # Interface de progression de l'analyse :
        # - Affiche une fenêtre avec un message d'attente pendant que l'analyse des textes est en cours.


        # Pour chaque page (contenue dans un dictionnaire), on procède à l'analyse.
        # Le résultat est stocké dans le dictionnaire 'dic'
        # Chaque dictionnaire 'dic' est ajouté à la liste 'dics' qui constitue la base de données

            # Exclusion des textes de type décret réglementaire en vérifiant la présence de 'n°' dans le titre du texte
            # Si un décret réglementaire est détecté, on ajoute ses informations dans `excluded_texts` et on passe au texte suivant

            #######################################
            # Nettoyage des informations inutiles #
            #######################################

            # Initialisation de certaines clés et extraction des informations de base pour le texte :

            # 1. Initialise l'identifiant de base de données pour les textes avec une valeur vide.
            # 2. Crée un lien direct vers le texte sur le site Legifrance en utilisant l'identifiant unique `cid` du texte.
            # 3. Stocke le code NOR du texte, un identifiant administratif important pour les décrets.
            # 4. Vérifie si le numéro de parution est disponible :
            #    - Si oui, l'ajoute à la base de données, sinon laisse la valeur vide.
            # 5. Extrait la date de parution dans le Journal Officiel en la formatant pour remplacer les abréviations "1er" et "ler" par "1".
            # 6. Vérifie si un numéro de texte est présent dans les données :
            #    - Si oui, l'ajoute à la base de données ; sinon, laisse la valeur vide.
            # 7. Formate le titre du décret pour supprimer les caractères indésirables et les espaces en double.

            # Initialisation des clés pour les articles pertinents à la nomination :
            # 8. Initialise des champs pour stocker les informations relatives aux articles des nominations (articles 1 et 2,
            #    autres articles de nomination, et autres articles à vérifier) avec des valeurs vides.

            # Extraction du ministère en fonction du code NOR :
            # 9. Vérifie si les trois premiers caractères du code NOR correspondent à un ministère connu,
            #    et associe le ministère correspondant si trouvé. Sinon, laisse le champ vide.

            # Récupération des informations de signature :
            # 10. Utilise la fonction `signers` pour extraire les noms des signataires et les associer au texte.
            # 11. Initialise la civilité (M./Mme) du signataire avec une valeur vide.


            ##########################################################################################################################
            # Extraction et traitement des articles d'un texte réglementaire pour identifier et organiser les articles de nomination #
            ##########################################################################################################################

            # 1. Récupère la liste des articles du texte à partir de 'input_dic'.
            # 2. Pour chaque article :
            #     - Extrait le contenu de l'article.
            #     - Utilise la fonction 'balises' pour nettoyer le contenu en supprimant les balises HTML et autres caractères non désirés.

            # Attribution directe aux colonnes en fonction du numéro de l'article :
            # 3. Si le numéro d'article est '1er', il est remplacé par '1' pour uniformiser les formats.
            # 4. Si le numéro est '1', le contenu de l'article est affecté directement à la colonne 'Texte_article_1'
            #     - Les caractères ';' sont remplacés par '|' et les espaces multiples sont réduits.

            # Identification des articles de nomination pour le numéro '2' :
            # 5. Si le numéro est '2' et que l'article contient les mots 'nommé' ou 'intérim', il est ajouté à la colonne 'Texte_article_2'.

            # Gestion des articles avec numéros supérieurs à 2 :
            # 6. Si le numéro est supérieur à 2 et que l'article contient 'nommé' ou 'intérim', il est également affecté à 'Texte_article_2'.
            # 7. Si l'article ne contient pas d'indication pour être publié et n'est pas de nomination, il est ajouté à 'Autre_article_à_vérifier'.

            # Analyse des articles sans numéro (anciens textes) :
            # 8. Si un numéro n'est pas présent :
            #     - Recherche manuellement la mention 'Art. 1e' ou 'Art. 1r' pour identifier le premier article et l'associe à 'Texte_article_1'.
            #     - Si l'article mentionne 'Art. 2' ou 'Article 2' et contient 'nommé' ou 'intérim', il est ajouté à 'Texte_article_2'.
            #     - Pour les articles sans numéro, avec 'nommé' ou 'intérim', l'article est ajouté à 'Autre_article_nomination'.
            #     - Si l'article ne correspond pas à un article de nomination et n'est pas destiné à être publié ou décomposé en sections ('A', 'B'), il est ajouté à 'Autre_article_à_vérifier'.


            ############################################################################################################################
            # Détermination de la civilité (Monsieur/Madame) pour le texte en analysant le titre et le contenu des articles pertinents #
            ############################################################################################################################

            # 1. Pour chaque article dans les colonnes 'Texte_article_1', 'Texte_article_2', et 'Autre_article_nomination' :
            #    - Effectue une recherche de civilité, d'abord dans le titre du décret pour minimiser les erreurs, puis dans le texte si nécessaire.

            # Priorité de l'analyse du titre pour la civilité :
            # 2. Si le champ 'Civilité' est vide, cherche des mentions de "M." ou "Mme" dans le titre du décret.
            #    - Si trouvé, remplace "M." par "Monsieur" et "Mme" par "Madame".

            # Analyse du contenu de l'article en cas d'absence de civilité dans le titre :
            # 3. Si 'Civilité' est encore vide et si le texte contient "nommé" ou "intérim" :
            #    - Si le texte contient également "mis fin" mais pas "chargé" ni "nommé", il est ignoré (cas de fin de fonction).
            #    - Sinon, la fonction 'gender_control' est utilisée pour déterminer la civilité basée sur le texte de l'article.

            # Cas spéciaux pour identifier la civilité via le titre :
            # 4. Si aucune civilité n'est trouvée et le titre contient "directeur" sans "directeurs", assigne "Monsieur".
            # 5. Si aucune civilité n'est trouvée et le titre contient "directrice" sans "directeurs", assigne "Madame".


            ############################################################################
            # Extraction et nettoyage du patronyme à partir des articles de nomination #
            ############################################################################

            # 1. Initialise le champ 'Patronyme' à une valeur vide pour commencer la collecte des données.
            # 2. Pour chaque texte d'article dans les colonnes 'Texte_article_1', 'Texte_article_2', et 'Autre_article_nomination' :
            #     - Si le champ 'Patronyme' est toujours vide (indiquant qu'aucune donnée n'a été trouvée et enregistrée), continue l'extraction.
            #     - Exclut les articles contenant "mis fin" ou "mis aux fonctions" pour éviter de capturer les noms de personnes sortant de fonction.

            # Extraction du patronyme :
            # 3. Utilise la fonction `patronyme(article_text)` pour extraire le nom de l'individu nommé dans l'article en le formatant proprement.
            #    - La fonction 'patronyme' prend en charge la suppression des grades militaires et autres titres honorifiques,
            #      ainsi que le nettoyage du texte pour les cas où le prénom est entre parenthèses ou en fin de phrase.

            # Gestion des majuscules et du format :
            # 4. La fonction 'patronyme' formate le nom pour correspondre au style 'Prénom Nom' en mettant en majuscule chaque composant du nom.

            # Conditions supplémentaires :
            # 5. Si le texte contient le mot 'nommé' et est un article de nomination, 'patronyme' est exécuté pour confirmer et extraire le nom complet.


            ###################################################################
            # Extraction du nom et du prénom, avec vérifications et nettoyage #
            ###################################################################

            # 1. Initialisation des champs 'Nom' et 'Prénom' à des valeurs vides pour stocker les données extraites.
            # 2. Hypothèse 1 : Extraction directe depuis le titre du décret si celui-ci contient " - " :
            #     - Recherche d'une mention de "M." ou "Mme" suivie du nom et prénom dans le titre du décret.
            #     - Supprime "M." ou "Mme" et parenthèses, et extrait le nom et prénom pour mise à jour.
            #     - Nettoie le nom pour retirer tout grade ou titre, en utilisant une liste de grades prédéfinis.
            #     - Si le champ 'Patronyme' est toujours vide, construit le patronyme en concaténant 'Prénom' et 'Nom'.

            # 3. Hypothèse 2 : Extraction depuis le patronyme si le titre n'a pas fourni de résultat :
            #     - Si le titre ne contient pas de nom et prénom, utilise la fonction 'analyse_patronyme' pour séparer le patronyme en nom et prénom.
            #     - Assure la capitalisation correcte du 'Nom' avec la fonction 'capitalize_name' pour garantir un formatage uniforme.

            # Vérification de la cohérence :
            # 4. Utilise 'coherence_patro_nom_prenom' pour vérifier la cohérence entre les valeurs extraites pour 'Patronyme', 'Nom', et 'Prénom'.
            #     - Stocke le résultat de la vérification dans 'Correspondance_Patronyme_avec_Prénom_et_Nom'.


            ################################################################################################
            # Extraction et nettoyage du poste de nomination/reconduction à partir du contenu des articles #
            ################################################################################################

            # 1. Initialise les champs de poste : 'Poste', 'Nomenclature_poste', 'Dénomination_poste', et 'Interim'.
            # 2. Pour chaque texte d'article dans 'Texte_article_1', 'Texte_article_2', et 'Autre_article_nomination' :
            #    - Si le champ 'Poste' est encore vide (indiquant qu'aucune information n'a été trouvée), poursuit l'extraction.

            # Extraction de la mention de poste :
            # 3. Utilise une expression régulière pour extraire la mention après les mots "nommé(e)" ou "reconduit(e)".
            #    - Supprime les termes redondants ou indésirables tels que "nommée", "de ce même ministère", "en outre", etc.

            # Nettoyages spécifiques :
            # 4. Supprime toute mention de date avec "à compter de JJ/MM/AAAA" ou autres mentions similaires.
            # 5. Exclut les informations supplémentaires comme "en remplacement de...", "en relève de...", "et placé(e)...", et "pour une durée de...".

            # Gestion des nominations intérimaires :
            # 6. Si aucun poste n'est trouvé, recherche des mentions "chargé(e) des fonctions en intérim" pour les postes provisoires.

            # Nettoyage final et formatage :
            # 7. Supprime les mentions inutiles (e.g., "à compter de cette même date", "sera appelée à de nouvelles fonctions").
            # 8. Capitalise le poste pour assurer la cohérence.
            # 9. Supprime les caractères de fin non nécessaires (',', '|', '.') et les espaces supplémentaires.
            # 10. Remplace les caractères espace codés (e.g., `chr(160)`) et les espaces multiples par un espace simple.


            #################################################################################################
            # Extraction de la date d'entrée en vigueur du décret et ajout des informations complémentaires #
            #################################################################################################

            # 1. Initialisation de la date d'effet ('Date_d'effet') :
            #    - Définit le champ 'Date_d'effet' comme vide en attendant une extraction réussie.

            # 2. Recherche de la date d'effet dans les champs 'Titre_du_Décret', 'Texte_article_1', 'Texte_article_2',
            #    'Autre_article_nomination', et 'Autre_article_à_vérifier'.
            #    - Pour chaque champ, vérifie si "compter du" est présent (indicatif d'une date de début).
            #    - Extrait la date à partir de cette mention, transformant le texte en format 'JJ/MM/AAAA' et normalisant "1er" en "1".

            # 3. Mise à jour de la date d'entrée en vigueur avec la fonction 'vigueur' :
            #    - La fonction 'vigueur' ajoute la date d'entrée en vigueur au dictionnaire 'dic' en fonction de la date d'effet ou, à défaut, de la date de publication.

            # 4. Prépare les champs d'information supplémentaires :
            #    - Initialise les champs 'Écoles' et 'Cabinets' comme vides en préparation pour un ajout ultérieur.

            # Ajout du dictionnaire 'dic' mis à jour dans la liste des dictionnaires 'dics', qui regroupe les informations de tous les décrets analysés.


        ######################################################################
        #             Récupération des nominations multiples                 #
        ######################################################################

        # création d'une deuxième liste de dictionnaires pour sauvegarder temporairement les lignes qui seront rajoutées à dics

        # 1. Pour chaque dictionnaire dans 'dics', vérifie si des nominations multiples sont détectées via la fonction 'nominations_multiples'.
        #    Trois cas de figure sont pris en charge pour les nominations multiples :
        #    - Cas 1 : Une liste de nominations dans l'article 1, détectée par la présence du mot "nommés".
        #      - Chaque nomination est analysée pour extraire le poste et les informations nominatives.
        #      - Si le patronyme correspond à celui du dictionnaire actuel, les informations sont mises à jour dans le dictionnaire 'dic'.
        #      - Si le patronyme diffère, un nouveau dictionnaire 'dic2' est créé pour la nomination et ajouté à la liste 'dics2'.
        #    - Cas 2 : Plusieurs phrases de nomination dans l'article 1, détectées par la répétition du mot "nommé".
        #      - Chaque phrase contenant "nommé" est traitée pour extraire le nom et poste.
        #      - Si le patronyme correspond au dictionnaire actuel, les informations sont mises à jour.
        #      - Si le patronyme diffère, un nouveau dictionnaire 'dic2' est créé et ajouté à 'dics2'.
        #    - Cas 3 : Plusieurs articles contiennent chacun une nomination, notamment dans 'Texte_article_2' et 'Autre_article_nomination'.
        #      - Pour chaque article contenant une nomination, un nouveau dictionnaire 'dic2' est créé avec les informations extraites et ajouté à 'dics2'.

        # 2. Pour chaque nouveau dictionnaire créé dans 'dics2', les étapes suivantes sont effectuées :
        #    - Civilité (titre), patronyme, prénom, et nom sont extraits et analysés.
        #    - Le poste de nomination et, si présent, la date d'effet sont extraits.
        #    - La date d'entrée en vigueur est mise à jour avec la fonction 'vigueur'.

        # 3. Après analyse de tous les dictionnaires 'dic', la base de données 'dics' est consolidée en ajoutant les nouveaux dictionnaires de 'dics2'.
        #    Cette étape garantit que toutes les nominations multiples sont correctement incluses dans la base de données consolidée.


        ######################################################################
        #                             Divers                                 #
        ######################################################################

        ##########################################################################################################
        # Attribution d'un identifiant unique et vérifications de cohérence pour chaque dictionnaire dans 'dics' #
        ##########################################################################################################

        # 1. Pour chaque dictionnaire (dic) dans la liste 'dics', les étapes suivantes sont effectuées :
        #    - Un identifiant unique est créé pour chaque entrée dans la base de données 'id_db_Textes'.
        #      Cet identifiant est structuré comme suit : 'dbtxt' suivi de six chiffres, avec des zéros en tête pour atteindre six chiffres.
        #      Par exemple : 'dbtxt000001', 'dbtxt000002', etc.
        #    - L'identifiant est généré en utilisant l'index actuel de l'élément, et un décalage de +1 pour commencer à 1 plutôt que 0.

        # 2. Vérification de la cohérence des données en fonction du champ 'NOR' (Numéro officiel de Référence) :
        #    - Pour chaque 'dic', on vérifie si la valeur de 'NOR' n'est pas déjà présente dans 'output_dics'.
        #    - Si 'NOR' est unique dans 'output_dics', il est ajouté pour garantir que chaque entrée dans 'dics' reste distincte.
        #    - Cette étape assure que le nombre de lignes de la base de données soit cohérent et qu'aucune redondance n'existe.

        # 3. Initialisation de champs additionnels pour chaque dictionnaire :
        #    - 'Alerte' : Champ vide, prêt à être rempli avec des alertes ou des messages d'erreur si des incohérences ou anomalies sont détectées dans les étapes suivantes.
        #    - 'Filtre_Poste' : Valeur par défaut définie à '1', utilisée pour indiquer un critère de filtrage spécifique sur le champ 'Poste'.


            ###################################################################################
            # Application d'un filtre pour exclure certaines catégories de postes spécifiques #
            ###################################################################################
            # Ce filtre met à jour le champ 'Filtre_Poste' à '0' pour exclure des postes spécifiques dans l'analyse.
            # Les postes exclus appartiennent généralement à des rôles de hauts fonctionnaires (conseillers, préfets de département,
            # et autres postes à responsabilité particulière), dont l'analyse n'est pas nécessaire dans ce contexte.

            # 1. Exclusion basée sur le nom exact du poste ('Conseiller du gouvernement', 'Préfet (hors classe), conseiller du gouvernement', etc.)
            #    - Si le nom de 'Poste' correspond exactement à un des intitulés ciblés (e.g., Conseiller du gouvernement ou Préfet (hors classe)),
            #      'Filtre_Poste' est défini à '0' pour cette entrée.

            # 2. Exclusion basée sur la présence de termes spécifiques dans le nom du poste :
            #    - Certains postes incluent des mots spécifiques comme 'préfet' ou 'préfète'.
            #    - Pour ces postes, un filtre supplémentaire analyse les variantes spécifiques de ces intitulés.
            #      Par exemple :
            #         - 'Préfet hors cadre'
            #         - 'Préfet d'un département'
            #         - Postes régionaux comme "administrateur supérieur des terres australes et antarctiques françaises"
            #    - Si une de ces variantes est détectée, 'Filtre_Poste' est aussi défini à '0'.

            # Cette logique est appliquée pour s'assurer que seuls les postes pertinents sont inclus dans l'analyse

            # Harcode certaines valeurs pour prendre en compte les interventions manuelles qui ne sont pas prises en charge par le code.


            ################################################################
            # Nettoyage et standardisation du poste dans les dictionnaires #
            ################################################################

            # Cette section extrait des informations de dénomination et classe les types de postes en les formalisant.

            # 1. Normalisation du champ 'Nomenclature_poste' :
            #    - 'Nomenclature_poste' est initialement défini comme une copie de 'Poste'.
            #    - Suppression de termes indiquant des statuts particuliers (e.g., 'par intérim', 'chargé des fonctions de') pour conserver une terminologie standard.
            #    - Remplacements standardisés pour harmoniser les termes similaires dans différents postes :
            #      - Conversion de termes au féminin/masculin vers un terme générique (ex: 'directrice' et 'directeur' deviennent 'direction').
            #      - Gestion de variantes pour des noms de postes (e.g., 'commissaire' à 'commissariat').

            # 2. Identification des statuts 'Interim' et 'Adjoint' :
            #    - Si le texte du poste contient "intérim" ou "adjoint", on met à jour les champs 'Interim' et 'Adjoint' à '1'.

            # 3. Extraction du préfixe de poste pour créer un nom commun de fonction :
            #    - À partir de l'intitulé normalisé de 'Nomenclature_poste', un préfixe est extrait pour catégoriser le poste en fonction de son type de rôle.
            #    - Le préfixe est ensuite appliqué à 'Nomenclature_poste' et retiré de 'Dénomination_poste'.

            # 4. Ajustement de la dénomination du poste pour correspondre au format exact du poste :
            #    - 'Dénomination_poste' est corrigé en s'assurant que son libellé final correspond au texte du champ 'Poste'.
            #    - Gestion des cas particuliers pour que la dénomination soit cohérente avec la terminologie générale.

            # 5. Élimination des parenthèses inutiles autour des termes normalisés (e.g., '(générale)' devient 'générale').


        ######################################################################
        #        Création du fichier csv à partir du dictionnaire            #
        ######################################################################

        # Formatage des dates pour la sortie en chaîne de caractères
        # - Pour chaque dictionnaire de la liste 'dics', les dates stockées sous forme de valeurs temporelles sont converties en chaînes de caractères.
        # - La conversion concerne trois champs de date :
        #   1. 'date_JORF' : date de publication du Journal Officiel de la République Française
        #   2. 'Date_d'effet' : date d'entrée en vigueur spécifiée dans les décrets
        #   3. 'Entrée_en_vigueur' : date calculée d'application du décret
        # - Le formatage en chaîne de caractères utilise la fonction 'date_to_string' pour uniformiser le format de date dans les sorties.


        # Boucle principale pour sauvegarder la base de données :
        # - Demande le nom du fichier, le format (extension), et le dossier de destination.
        # - Présente une interface à l'utilisateur pour renseigner ces informations.

        # Gestion des événements et des valeurs entrées :
        # - Si l'utilisateur ferme la fenêtre, l'application se ferme.
        # - Si l'utilisateur valide ("Ok") et que tous les champs nécessaires sont renseignés, le programme :
        #    - Récupère l'extension de fichier sélectionnée et forme le nom complet du fichier de sortie avec son extension.
        #    - Sauvegarde ensuite la base de données dans le format choisi :
        #       - JSON : Sauvegarde le contenu directement en JSON.
        #       - XLSX : Convertit la base de données en DataFrame et enregistre au format Excel.
        #       - CSV : Convertit en DataFrame, puis sauvegarde avec un séparateur de champs spécifique (#) et encodage UTF-8.

        # Confirmation de la sauvegarde :
        # - Affiche un message de confirmation indiquant le succès de la sauvegarde avec le nom et le format du fichier.
        # - Demande si l'utilisateur souhaite sauvegarder dans un autre format :
        #    - Si "OUI", rouvre la fenêtre pour permettre une nouvelle sauvegarde.
        #    - Si "NON" ou fermeture de la fenêtre, termine la boucle.

        # Vérification des erreurs :
        # - Si le nom de fichier ou le dossier est invalide, affiche un message d'erreur.
        # - Si aucun dossier ou format de fichier n'est sélectionné, une erreur s’affiche et la fenêtre est rouverte.

        # Fermeture finale :
        # - Lorsque la boucle de sauvegarde est complétée, un message indique la fin de l'analyse et invite l'utilisateur à fermer l'application.


    ######################################################################
    #           Création de la base de données Carrières                 #
    ######################################################################

        # Tentative de connexion initiale à la source complémentaire.

        # Si la connexion échoue, ou si l'étape de saisie des identifiants est requise,
        # une fenêtre de saisie des identifiants de connexion est affichée.

        # Interface d'authentification pour l'utilisateur :
        # L'utilisateur est invité à entrer son adresse email et son mot de passe pour accéder à la source complémentaire.
        # Option de sauvegarde des identifiants (coche "Sauvegarder les identifiants") pour éviter une saisie répétée lors des utilisations ultérieures.

        # Les informations sont stockées pour une nouvelle tentative de connexion.

        # Tentative de connexion avec les identifiants saisis par l'utilisateur :
        # Si les identifiants sont incorrects, un message d'erreur s'affiche.
        # En cas de succès, une confirmation de connexion est affichée à l'utilisateur.

        # Si l'utilisateur choisit de sauvegarder les identifiants, ceux-ci sont stockés dans 'tempDir' pour les sessions futures.


        ######################################################################
        #                     Définition des variables                       #
        ######################################################################

        # Mise en cache des requêtes pour la source complémentaire pour éviter de refaire des requêtes identiques.

        # Initialisation de listes et dictionnaires :
        # - 'processes' : liste vide pour gérer les threads/processus de récupération de données
        # - 'dics' : liste des dictionnaires de données récupérées

        # Types de données ('types_datas') :
        #   Liste contenant les différentes catégories de données extraites de la source complémentaire :
        #     - 'Fonctions' : liste des fonctions de la personne
        #     - 'Informations diverses' : sous-dictionnaire pour les formations, nationalité, grade, décorations, distinctions, œuvres et travaux
        #     - 'Etapes de carrière' : étapes clés dans la carrière professionnelle
        #     - 'Parentés' : sous-dictionnaire pour les informations familiales (père, mère, enfants, etc.)
        #     - 'Adresses' : sous-dictionnaire pour les informations de contact

        # Dictionnaire 'chars' pour neutraliser les accents :
        #   Utilisé pour faciliter les comparaisons entre la base 'TEXTES' et la source complémentaire
        #   en remplaçant les caractères accentués par leurs équivalents non accentués.

        # Dictionnaires pour gérer des cas particuliers :
        # - 'hardcode_names' : noms présents dans la source complémentaire avec une orthographe différente de la base 'TEXTES'
        # - 'hardcode_urls' : remplace l'URL à analyser pour certains noms spécifiques dans la source complémentaire

        promo_ena = {
            'Aimé Césaire': 2021, 'Hannah Arendt': 2020, 'Molière': 2019, 'Georges Clemenceau': 2018, 'Louise Weiss': 2017, 'George Orwell': 2016,
            'Winston Churchill': 2015, 'Jean de La Fontaine': 2014, 'Jean Zay': 2013, 'Marie Curie': 2012, 'Jean-Jacques Rousseau': 2011,
            'Robert Badinter': 2011, 'Emile Zola': 2010, 'Willy Brandt': 2009, 'Aristide Briand': 2008, 'République': 2007, 'Simone Veil': 2006,
            'Romain Gary': 2005, 'Léopold Sédar Senghor': 2004, 'René Cassin': 2003, 'Copernic': 2002, 'Nelson Mandela': 2001, 'Averroès': 2000,
            'Cyrano de Bergerac': 1999, 'Valmy': 1998, 'Marc Bloch': 1997, 'Victor Schoelcher': 1996, 'René Char': 1995,
            'Antoine de Saint-Exupéry': 1994, 'Léon Gambetta': 1993, 'Condorcet': 1992, 'Victor Hugo': 1991, 'Victor-Hugo': 1991, 'Jean Monnet': 1990, 'Liberté Egalité Fraternité': 1989,
            'Liberté, Egalité, Fraternité': 1989, 'Liberté-égalité-fraternité': 1989, 'Michel de Montaigne': 1988, 'Fernand Braudel': 1987, 'Fernand-Braudel': 1987, 'Denis Diderot': 1986,
            'Léonard de Vinci': 1985, 'Louise Michel': 1984, 'Solidarité': 1983, "Henri-François d'Aguesseau": 1982, "Henri François d'Aguesseau": 1982, "François d'Aguesseau": 1982, "Droits de l'Homme": 1981,
            "Droits de l'homme": 1981, "Droit de l'Homme": 1981, 'Voltaire': 1980, "Michel de l'Hospital": 1979, "Michel de L'Hospital": 1979, 'Pierre Mendès France': 1978, 'Mendès France': 1978, 'André Malraux': 1977, 'Guernica': 1976,
            'Léon Blum': 1975, 'Simone Weil': 1974, 'François Rabelais': 1973, 'Charles de Gaulle': 1972, 'Charles-de-Gaulle': 1972, 'Thomas More': 1971, 'Robespierre': 1970, 'Jean Jaurès': 1969,
            'Turgot': 1968, 'Marcel Proust': 1967, 'Montesquieu': 1966, 'Stendhal': 1965, 'Blaise Pascal': 1964,
            'Saint-Just': 1963, 'Albert Camus': 1962, 'Lazare Carnot': 1961, 'Alexis de Tocqueville': 1960, 'Vauban': 1959, 'Dix-huit Juin': 1958, 'France-Afrique': 1957,
            'Guy Desbos': 1956, 'Albert Thomas': 1955, 'Paul Cambon': 1953, 'Félix Eboué': 1954, 'Jean Giraudoux': 1952, 'Europe': 1951, 'Quarante-huit': 1950,
            'Jean Moulin': 1949, 'Nations unies': 1949, 'Croix de Lorraine': 1948, 'Union française': 1948, 'France combattante': 1947
        }

        departements = [
            'Ain', 'Aisne', 'Allier', 'Alpes-de-Haute-Provence', 'Hautes-alpes', 'Alpes-maritimes', 'Ardèche', 'Ardennes', 'Ariège', 'Aube', 'Aude', 'Aveyron', 'Bouches-du-Rhône',
            'Calvados', 'Cantal', 'Charente', 'Charente-maritime', 'Cher', 'Corrèze', 'Corse-du-sud', 'Haute-Corse', "Côte-d'Or", "Côtes-d'Armor", 'Creuse', 'Dordogne', 'Doubs',
            'Drôme', 'Eure', 'Eure-et-loir', 'Finistère', 'Gard', 'Haute-garonne', 'Gers', 'Gironde', 'Hérault', 'Ille-et-vilaine', 'Indre', 'Indre-et-loire', 'Isère', 'Jura',
            'Landes', 'Loir-et-cher', 'Loire', 'Haute-loire', 'Loire-atlantique', 'Loiret', 'Lot', 'Lot-et-garonne', 'Lozère', 'Maine-et-loire', 'Manche', 'Marne', 'Haute-marne',
            'Mayenne', 'Meurthe-et-moselle', 'Meuse', 'Morbihan', 'Moselle', 'Nièvre', 'Nord', 'Oise', 'Orne', 'Pas-de-calais', 'Puy-de-dôme', 'Pyrénées-atlantiques', 'Hautes-Pyrénées',
            'Pyrénées-orientales', 'Bas-rhin', 'Haut-rhin', 'Rhône', 'Haute-saône', 'Saône-et-loire', 'Sarthe', 'Savoie', 'Haute-savoie', 'Paris', 'Seine-maritime', 'Seine-et-marne',
            'Yvelines', 'Deux-sèvres', 'Somme', 'Tarn', 'Tarn-et-Garonne', 'Var', 'Vaucluse', 'Vendée', 'Vienne', 'Haute-vienne', 'Vosges', 'Yonne', 'Belfort', 'Essonne', 'Hauts-de-seine',
            'Seine-Saint-Denis', 'Val-de-marne', "Val-d'Oise", 'Guadeloupe', 'Martinique', 'Guyane', 'Réunion', 'Mayotte', 'Pyrénées'
        ]


        keys_to_remove = []


        ######################################################################
        #                         Code principal                             #
        ######################################################################


        # Chargement des configurations de noms et URLs "hardcodés" :
        # - Ces configurations permettent de traiter des cas particuliers où la source complémentaire présente des variations spécifiques.

        # Essai de chargement du fichier 'hardcode_names.json' :
        # - Ce fichier contient des correspondances de noms sous une forme JSON pour des orthographes spécifiques présentes dans la source complémentaire.
        # - Si le fichier est absent ou invalide, l'exception est ignorée.

        # Essai de chargement du fichier 'hardcode_urls.json' :
        # - Ce fichier contient des correspondances d'URLs pour les cas où une URL particulière est requise pour certains noms dans la source complémentaire.
        # - Comme pour 'hardcode_names.json', l'exception est ignorée si le fichier est introuvable ou illisible.

        # Initialisation de deux listes vides :
        # - 'output_dics' : pour stocker les dictionnaires de sortie contenant les informations collectées.
        # - 'urls' : pour conserver les URLs utilisées, facilitant le suivi et l'évitement de doublons lors de l'extraction.


        ##################################################################
        # Interface de paramétrage pour l'analyse des données textuelles #
        ##################################################################

        # Ce bloc configure l'analyse, avec des options pour ajuster la cache, gérer des substitutions de noms et liens, et lancer l'analyse.

        # Affichage de la fenêtre principale avec plusieurs options :
        # - L'utilisateur peut spécifier le fichier de base de données de textes à analyser et sélectionner des paramètres tels que :
        #     - Vider le cache (pour forcer la mise à jour).
        #     - Activer une redondance de sécurité pour une analyse approfondie.
        # - Boutons pour gérer les substitutions de noms et liens vers la source complémentaire.
        # - Bouton pour lancer l'analyse des textes.

        # Gestion du cache :
        # - Si l'option "Vider le cache" est cochée, le cache existant est supprimé pour prendre en compte les mises à jour.

        # Substitutions de noms :
        # - Une interface permet d'ajouter ou supprimer des correspondances spécifiques de noms entre la base de données 'textes' et la source complémentaire.
        # - Chaque ajout ou suppression est confirmé par l'utilisateur avant de sauvegarder.

        # Substitutions de liens :
        # - Interface similaire à celle des noms, permettant d'ajouter ou supprimer des correspondances de liens entre la base de données 'textes' et la source complémentaire.
        # - Les entrées sont sauvegardées si l'utilisateur confirme l'action.

        # Lancement de l'analyse :
        # - L'analyse démarre si un fichier JSON valide est sélectionné.
        # - Le programme vérifie que le fichier contient les bonnes clés et valeurs avant de continuer.
        # - Un message d'attente est affiché, indiquant que l'analyse est en cours.


        ###############################################################
        # Boucle principale de vérification des données biographiques #
        ###############################################################

        # Ce bloc exécute plusieurs vérifications de sécurité pour assurer la fiabilité des données provenant de la source complémentaire.

        # Initialisation de la vérification :
        # - `old_dics_checker` est initialisé pour suivre les changements dans `dics` à chaque itération.
        # - Un compteur de vérifications `check` est mis à zéro avant chaque exécution.

        # Initialisation de la session de connexion :
        # - Une session est ouverte pour se connecter à la source complémentaire.
        # - L'utilisateur est authentifié à l'aide des identifiants.

        # Analyse multi-thread pour optimiser la récupération des données biographiques :
        # - Un pool de threads est créé pour traiter les données de chaque dictionnaire `dic` en parallèle.
        # - La fonction `biographies` est appliquée à chaque dictionnaire `dic` via un processus en parallèle, ce qui améliore la vitesse d'analyse.

        # Vérification de sécurité (si `bio_redondance` est activé) :
        # - Le programme compare l'état actuel de `dics` avec le précédent (`old_dics_checker`).
        # - Si les données n'ont pas changé depuis l'itération précédente, la boucle s'arrête.
        # - Si des changements sont détectés, `old_dics_checker` est mis à jour, et une nouvelle fenêtre de progression s'ouvre pour informer l'utilisateur que l'analyse est en cours.

        # Si `bio_redondance` est désactivé, le programme arrête la boucle après une seule exécution.


        #################################################################
        # Création des dictionnaires de sortie consolidés `output_dics` #
        #################################################################

        # - Pour chaque dictionnaire `dic` dans `dics` :
        #     1. Vérifie si une URL unique de la source complémentaire est présente et n’a pas encore été ajoutée à `urls`.
        #         - Si oui, un nouveau dictionnaire `output_dic` est créé, qui contient une copie de toutes les données de `dic`.
        #         - Les champs supplémentaires (par exemple, `id_db_Carrières`, `nb_lignes_db_Textes`, `ids_db_Textes`, etc.) sont ajoutés et initialisés.
        #         - L’URL est ajoutée à la liste `urls` pour éviter les duplications dans les prochaines itérations.
        #         - Les clés contenues dans `keys_to_remove` sont supprimées de `output_dic` pour ne conserver que les informations nécessaires.
        #     2. Si l’URL existe déjà dans `urls` :
        #         - Le dictionnaire correspondant dans `output_dics` est mis à jour en concaténant les nouveaux identifiants `id_db_Textes` et le champ `Filtre_Poste`.

        # Ajout d’un identifiant unique pour chaque `output_dic` dans `output_dics` :
        # - Un identifiant unique `id_db_Carrières` est généré pour chaque `output_dic` en utilisant l'index.
        # - Le champ `nb_lignes_db_Textes` est calculé pour chaque `output_dic` en comptant le nombre de `ids_db_Textes` (séparés par `|`).

        # Mise à jour des identifiants de la base de données pour chaque `dic` dans `dics` :
        # - Associe chaque `dic` au `id_db_Carrières` de son `output_dic` correspondant en fonction de l’URL de la source complémentaire.


        #########################################################
        # Fenêtre de confirmation de récupération des carrières #
        #########################################################

        # - Affiche une fenêtre confirmant que le nombre de carrières (`output_dics`) a été récupéré avec succès.
        # - L'utilisateur clique sur 'Ok' pour fermer cette fenêtre.

        # Fenêtre de sélection pour générer la base de données :
        # - Offre un choix entre deux options de base de données : `"Carrières"` ou `"Textes" (consolidée)`.
        # - Demande le nom de fichier, le format de fichier (JSON, Excel, CSV) et le dossier de destination.

        # Logique de sauvegarde en fonction des choix :
        # - Si l'utilisateur choisit `"Carrières"`, `output_db` est assigné à `output_dics`.
        # - Si l'utilisateur choisit `"Textes"`, `output_db` est assigné à `dics`.
        # - Le nom du fichier, son extension et son dossier de destination sont validés.

        # Processus de sauvegarde :
        # - Sauvegarde en format JSON, Excel ou CSV :
        #   - En JSON : les données sont directement sauvegardées.
        #   - En Excel : crée d'abord un fichier CSV temporaire pour éviter les problèmes d'encodage, puis le convertit en Excel.
        #   - En CSV : sauvegarde directement en utilisant le séparateur `#` et l'encodage `utf-8-sig`.

        # Confirmation de sauvegarde :
        # - Affiche une confirmation indiquant que la base de données a été sauvegardée avec succès.
        # - Demande si l'utilisateur souhaite sauvegarder dans un autre format.
        # - Si l'utilisateur choisit 'Non', le processus d'analyse se termine avec un message final.
