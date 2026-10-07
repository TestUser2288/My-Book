# Chapitre 4 : Documentation et dictionnaires de données — exercices et applications

> 🧭 Ce chapitre du cahier prolonge le chapitre 4 du livre. Les **applications** sont de petites études guidées, à refaire pas à pas : fiche d'un jeu, journal d'un nettoyage, dictionnaires, test d'un dictionnaire, glossaire, lignage, empreintes, et le rejeu d'un chiffre depuis le brut. Les **exercices** (⭐ facile, ⭐⭐ moyen, ⭐⭐⭐ plus long) vous demandent d'appliquer une idée du livre ; chacun renvoie à la section concernée, et un **corrigé** suit. Les fichiers `verite_*.csv` ne servent qu'à **juger** vos choix une fois le travail fait.

```python
import os, sys, json, shutil, tempfile
import numpy as np
import pandas as pd

sys.path.insert(0, "build")
import outils_ch04 as O

TMP4C = tempfile.mkdtemp(prefix="doc4c_", dir=os.environ.get("TMPDIR"))
```

## Applications

### Application 4.1 — La fiche de l'export du site (section 4.1.2)

**Objectif.** Remplir la fiche d'un jeu de données que l'on vient de recevoir : l'export des commandes du site (`site_commandes.csv`). On **mesure** ce que le fichier livre, on **constate** ses défauts, puis on les consigne dans la rubrique « limites connues ».

**Étape 1 — Lire sans rien deviner, et regarder le grain.** On lit tout en texte et l'on vérifie que la clé annoncée (`order_ref`) identifie bien une ligne.

```python
so = O.charger("site_commandes", dtype=str)
print("lignes :", len(so), "| colonnes :", len(so.columns))
print("order_ref en double :", int(so["order_ref"].duplicated().sum()))
print("commandes de test (e-mail test@example.com) :", int(so["customer_email"].str.strip().str.lower().eq("test@example.com").sum()))
print("statuts :", so["status"].value_counts().to_dict())
```
<!--sortie-->
```text
lignes : 6259 | colonnes : 9
order_ref en double : 121
commandes de test (e-mail test@example.com) : 60
statuts : {'paid': 3629, 'PAID': 1537, 'Paid': 907, 'cancelled': 186}
```

**Lecture.** Le fichier compte 6 259 lignes pour 9 colonnes. La clé annoncée n'est **pas unique** : 121 `order_ref` apparaissent en double. 60 lignes sont des commandes de test, et le statut s'écrit de trois façons (`paid`, `PAID`, `Paid`), plus 186 lignes `cancelled`. Ce sont quatre limites à consigner dans la fiche.

**Étape 2 — Le changement d'unité.** La fiche mentionne que `total` change d'unité à une date. On le **vérifie** : on convertit le texte en nombre et l'on compare les totaux médians avant et après le 15 septembre.

```python
nombre = pd.to_numeric(so["total"].str.replace(r"[^\d,.]", "", regex=True).str.replace(",", "."), errors="coerce")
apres = so["created_at"] >= "2025-09-15"
print("médiane du total avant le 15/09 :", nombre[~apres].median(), "| après :", nombre[apres].median())
print("rapport :", round(nombre[apres].median() / nombre[~apres].median(), 1))
```
<!--sortie-->
```text
médiane du total avant le 15/09 : 82.93 | après : 7808.0
rapport : 94.2
```

**Lecture.** Le total médian passe de 82,93 € avant le 15 septembre à 7 808 après : un rapport de l'ordre de **100** (94 ici, la différence tenant à la variation normale du panier d'une période à l'autre). Le changement d'unité est **confirmé par les données** : la rubrique de la fiche n'est plus une rumeur.

**Étape 3 — La fiche.** On consigne ce que l'on sait, y compris les défauts découverts.

```python
O.fiche_jeu(so, **{
    "nom": "site_commandes (v1)", "source": "export de la plateforme du site", "date d'extraction": "2025-12-31",
    "périmètre": "commandes du canal Site, année 2025", "une ligne =": "une commande, SAUF doublons d'export",
    "clé": "order_ref (pas unique : doublons)", "limites connues": "doublons, commandes de test, statut en 3 casses",
    "limite n° 2": "total en texte ; en centimes à partir du 15/09", "droits": "adresses e-mail : données personnelles"})
```
<!--sortie-->
```text
nom                   : site_commandes (v1)
source                : export de la plateforme du site
date d'extraction     : 2025-12-31
périmètre             : commandes du canal Site, année 2025
une ligne =           : une commande, SAUF doublons d'export
clé                   : order_ref (pas unique : doublons)
limites connues       : doublons, commandes de test, statut en 3 casses
limite n° 2           : total en texte ; en centimes à partir du 15/09
droits                : adresses e-mail : données personnelles
lignes                : 6 259
colonnes              : 9
empreinte du contenu  : 37254f3f50e0
```

**À vous.** Ajoutez la rubrique « version » et le propriétaire du jeu. Que diriez-vous à la personne qui vous a livré l'export, pour obtenir la date d'extraction exacte ?

### Application 4.2 — Le journal du nettoyage de l'export du site (sections 4.1.3 et 4.1.4)

**Objectif.** Nettoyer l'export du site en consignant **chaque** décision dans un journal, vérifier l'équation de conservation, puis juger le nettoyage avec la vérité.

**Étape 1 — La fonction de nettoyage.** Cinq étapes : commandes de test, doublons d'export, annulées (selon la définition du glossaire), puis conversion du total en euros.

```python
def nettoyer_site(brut):
    j = O.Journal("site", brut)
    df = brut.copy()
    test = df["customer_email"].str.strip().str.lower().eq("test@example.com")
    df = j.etape(df, df[~test].copy(), "retirer les commandes de test", "ce ne sont pas des clients")
    df = j.etape(df, df.drop_duplicates("order_ref").copy(), "une ligne par order_ref", "une nouvelle tentative d'export ne crée pas de commande")
    df["status"] = df["status"].str.lower()
    df = j.etape(df, df[df["status"] != "cancelled"].copy(), "retirer les commandes annulées", "exclues du chiffre d'affaires (glossaire)")
    nb = pd.to_numeric(df["total"].str.replace(r"[^\d,.]", "", regex=True).str.replace(",", "."), errors="coerce")
    cent = df["created_at"] >= "2025-09-15"
    df["total_eur"] = np.where(cent, nb / 100, nb)
    df = j.etape(df, df, "total : texte vers nombre ; centimes vers euros dès le 15/09", "l'unité dépend de la date", modifiees=int(cent.sum()))
    return df, j

site_propre, jn = nettoyer_site(so)
print(jn.table()[["etape", "avant", "apres", "retirees", "modifiees"]].to_string(index=False))
print("lues, retirées, finales :", jn.conservation())
```
<!--sortie-->
```text
  etape  avant  apres  retirees  modifiees
lecture   6259   6259         0          0
      1   6259   6199        60          0
      2   6199   6078       121          0
      3   6078   5897       181          0
      4   5897   5897         0       2367
lues, retirées, finales : (6259, 362, 5897)
```

**Lecture.** 6 259 lignes lues, 60 + 121 + 181 retirées, 5 897 lignes finales : l'équation de conservation tombe juste. L'étape 4 ne retire rien mais **modifie 2 367 lignes** (les 2 367 commandes d'après le 15 septembre, dont le total passe des centimes aux euros).

**Étape 2 — Juger avec la vérité.** Le fichier de vérité dit quelles lignes étaient de test, des doublons d'export ou des annulées, et quel était le vrai total.

```python
ver = O.charger("verite_site")
base = ver[~ver["defaut"].isin(["test", "doublon_export"])].drop_duplicates("order_ref")
print("vérité : tests", int((ver["defaut"] == "test").sum()), "| doublons", int((ver["defaut"] == "doublon_export").sum()),
      "| annulées", int((base["defaut"] == "annulee").sum()))
chk = site_propre.merge(ver.drop_duplicates("order_ref")[["order_ref", "total_vrai"]], on="order_ref")
print("écart maximal entre total_eur et le vrai total :", round((chk["total_eur"] - chk["total_vrai"]).abs().max(), 2), "€")
print("commandes restantes :", len(site_propre), "| chiffre d'affaires :", O.eur(site_propre["total_eur"].sum()))
```
<!--sortie-->
```text
vérité : tests 60 | doublons 121 | annulées 181
écart maximal entre total_eur et le vrai total : 0.0 €
commandes restantes : 5897 | chiffre d'affaires : 600 164,13 €
```

**Lecture.** Le nettoyage retire **exactement** ce que la vérité dit : 60 tests, 121 doublons, 181 annulées, et le total converti coïncide avec le vrai total à zéro euro près. Le chiffre d'affaires nettoyé est de 600 164,13 €. Ce résultat parfait n'a rien de normal : les règles sont **exactes** parce que les défauts ont été fabriqués pour l'être ; sur une vraie donnée, le journal montrerait aussi ses fausses fusions, comme au livre (section 4.1.5).

**À vous.** Que se passerait-il si l'on oubliait la conversion des centimes ? Calculez le chiffre d'affaires **sans** la conversion et comparez.

### Application 4.3 — Le dictionnaire de `clients` et de `produits` (sections 4.2.2 et 4.2.3)

**Objectif.** Fabriquer un squelette pour deux référentiels, l'enrichir avec les informations de métier, le ranger en CSV, et le relire.

**Étape 1 — Les squelettes.**

```python
clients = O.charger("clients")
produits = O.charger("produits")
print(O.squelette(clients)[["colonne", "type", "manquants_pct", "distincts", "min", "max"]].to_string(index=False))
print()
print(O.squelette(produits)[["colonne", "type", "distincts", "min", "max"]].to_string(index=False))
```
<!--sortie-->
```text
               colonne  type  manquants_pct  distincts        min        max
             id_client int64            0.0       6000          1       6000
      date_inscription   str            0.0       2541 2018-01-01 2025-12-30
       annee_naissance int64            0.0         68       1940       2007
                 ville   str            0.0         20    Ville A    Ville T
     canal_acquisition   str            0.0          3   Boutique       Site
              fidelite int64            0.0          2          0          1
          email_valide int64            0.0          2          0          1
consentement_marketing int64            0.0          2          0          1

       colonne    type  distincts            min             max
    id_produit   int64        120              1             120
   nom_produit     str         60 Affiche design Étagère compact
     categorie     str          6      Bien-être       Papeterie
    prix_vente float64         64            2.9           152.9
    cout_achat float64        117           1.53            71.1
   fournisseur     str          8  Fournisseur A   Fournisseur H
date_lancement     str        118     2018-01-30      2023-11-25
```

**Étape 2 — L'enrichissement et le rangement.** `dico_complet` fusionne le squelette et les informations saisies à la main (`META`). On range le résultat en CSV puis on le relit.

```python
dc, dp = O.dico_complet(clients, "clients"), O.dico_complet(produits, "produits")
chemin = os.path.join(TMP4C, "dictionnaire_produits_v1.csv")
dp.to_csv(chemin, index=False)
relu = pd.read_csv(chemin)
print("relu :", relu.shape, "| colonnes du dictionnaire :", list(relu.columns))
print(relu[["colonne", "libelle", "unite", "valeurs_permises", "sensibilite"]].fillna("").to_string(index=False))
```
<!--sortie-->
```text
relu : (7, 11) | colonnes du dictionnaire : ['colonne', 'type', 'manquants_pct', 'exemple', 'libelle', 'unite', 'valeurs_permises', 'obligatoire', 'codage_manquant', 'regle_ou_source', 'sensibilite']
       colonne                     libelle             unite                                     valeurs_permises    sensibilite
    id_produit      Identifiant du produit                                                                                      
   nom_produit     Désignation commerciale                                                                                      
     categorie                   Catégorie                   Cuisine|Maison|Décoration|Papeterie|Jardin|Bien-être               
    prix_vente Prix de vente catalogue TTC                 €                                                                    
    cout_achat    Coût d'achat unitaire HT                 €                                                      confidentielle
   fournisseur                 Fournisseur                                                                                      
date_lancement   Date de mise au catalogue date (aaaa-mm-jj)                                                                    
```

**Étape 3 — Un piège que le squelette signale.** `nom_produit` a-t-il autant de valeurs distinctes que de lignes ? Et que dit alors le dictionnaire ?

```python
print("produits :", len(produits), "| noms distincts :", produits["nom_produit"].nunique())
print("règle inscrite dans le dictionnaire :", dp.loc[dp["colonne"] == "nom_produit", "regle_ou_source"].iloc[0])
```
<!--sortie-->
```text
produits : 120 | noms distincts : 60
règle inscrite dans le dictionnaire : catalogue ; NON unique (voir limites)
```

**Lecture.** Le catalogue compte 120 produits mais seulement **60 noms distincts** : chaque nom est porté par deux produits (à des prix différents). Une jointure sur le nom doublerait les lignes. Le dictionnaire le dit en toutes lettres (« NON unique ») : c'est cette phrase qui évite à un collègue de joindre sur `nom_produit`.

**À vous.** Quelles colonnes de `clients` marqueriez-vous « sensibles » et pourquoi ? Comparez à la colonne `sensibilite` du dictionnaire.

### Application 4.4 — Le test du dictionnaire (section 4.2.5)

**Objectif.** Transformer le dictionnaire en **contrôle** : le laisser arrêter la chaîne, puis s'en servir comme cahier des charges d'un nettoyage.

**Étape 1 — Un contrôle qui bloque.** On enveloppe la vérification dans une fonction qui lève une erreur.

```python
def controle(df, dico, nom):
    anomalies = O.verifier_dictionnaire(df, dico)
    if anomalies:
        raise AssertionError(f"{nom} ne respecte pas son dictionnaire :\n- " + "\n- ".join(anomalies))
    return "ok"

print("clients :", controle(clients, dc, "clients"))
degrade = clients.drop(columns="email_valide").assign(pays="Pays P1")
degrade.loc[3, "fidelite"] = 5
try:
    controle(degrade, dc, "clients dégradé")
except AssertionError as e:
    print(e)
```
<!--sortie-->
```text
clients : ok
clients dégradé ne respecte pas son dictionnaire :
- colonne absente du dictionnaire : pays
- fidelite : 1 valeurs hors domaine (0|1)
- colonne du dictionnaire absente du fichier : email_valide
```

**Lecture.** Le contrôle lève une erreur qui **nomme les trois anomalies** : la colonne `pays` ajoutée, la valeur `5` hors du domaine `0|1` de `fidelite`, et la colonne `email_valide` disparue. La chaîne s'arrêterait là, avant qu'un calcul faux ne parte.

**Étape 2 — Le dictionnaire du CRM comme cahier des charges.** Sur le CRM brut, le test liste ce qu'il faut nettoyer. On corrige le **consentement** (sept écritures), puis on relance.

```python
crm = O.charger("crm_clients", dtype=str)
dcrm = O.dico_complet(crm, "crm_clients")
print("avant :", [a for a in O.verifier_dictionnaire(crm, dcrm) if a.startswith("consentement")])
oui = {"oui", "o", "1", "true"}
crm["consentement_marketing"] = crm["consentement_marketing"].str.strip().str.lower().map(lambda v: np.nan if pd.isna(v) else ("oui" if v in oui else v))
print("après :", [a for a in O.verifier_dictionnaire(crm, dcrm) if a.startswith("consentement")])
```
<!--sortie-->
```text
avant : ['consentement_marketing : 2428 valeurs hors domaine (oui|non)', 'consentement_marketing : 2161 valeurs vides alors que la colonne est obligatoire']
après : ['consentement_marketing : 2161 valeurs vides alors que la colonne est obligatoire']
```

**Lecture.** La normalisation fait disparaître les 2 428 consentements hors domaine (`O`, `1`, `TRUE`, `OUI`… deviennent `oui`). Il reste les **2 161 vides** : ce sont des consentements **non renseignés**, que le nettoyage ne peut pas inventer.

**À vous.** Il reste des consentements vides alors que la colonne est obligatoire. Est-ce un défaut des données ou du dictionnaire ? Argumentez, puis proposez une modification du dictionnaire (et notez-la dans un journal des changements).

### Application 4.5 — Un glossaire pour la boutique (section 4.2.6)

**Objectif.** Mesurer ce qu'une définition change, puis la figer dans un glossaire exploitable par un programme.

**Étape 1 — « Client actif » selon trois définitions, par canal d'acquisition.**

```python
cmd = O.charger("commandes"); cmd["jour"] = pd.to_datetime(cmd["date_commande"])
cli = O.charger("clients").set_index("id_client")
ref = pd.Timestamp("2025-12-31")
def actifs(jours, mini=1):
    r = cmd[cmd["jour"] > ref - pd.Timedelta(days=jours)].groupby("id_client").size()
    return r[r >= mini].index
res = pd.DataFrame({"1 commande, 12 mois": cli.loc[actifs(365), "canal_acquisition"].value_counts(),
                    "1 commande, 6 mois": cli.loc[actifs(183), "canal_acquisition"].value_counts(),
                    "2 commandes, 12 mois": cli.loc[actifs(365, 2), "canal_acquisition"].value_counts()})
print(res.assign(**{"inscrits": cli["canal_acquisition"].value_counts()}).to_string())
```
<!--sortie-->
```text
                   1 commande, 12 mois  1 commande, 6 mois  2 commandes, 12 mois  inscrits
canal_acquisition                                                                         
Boutique                          1916                1561                  1323      2957
Site                              1496                1216                  1019      2329
Réseaux                            463                 371                   312       714
```

**Lecture.** Au 31 décembre 2025, la Boutique compte 1 916 clients actifs selon la première définition, sur 2 957 inscrits ; le Site 1 496 sur 2 329 ; les Réseaux 463 sur 714. Les trois définitions ne changent pas le classement des canaux (Boutique, Site, Réseaux), et la proportion de clients ayant au moins deux commandes parmi ceux qui en ont une est voisine d'un canal à l'autre (de l'ordre de 67 à 69 %) : le choix de la définition déplace le **total**, pas la comparaison entre canaux. Il faut le savoir pour ne pas s'inquiéter à tort quand deux collègues citent des totaux différents.

**Étape 2 — « Panier moyen » selon trois définitions.**

```python
lig = O.charger("lignes_commande")
x = lig.merge(cmd, on="id_commande")
x25 = x[x["date_commande"] >= "2025-01-01"]
ttc = x25["montant"].sum() / x25["id_commande"].nunique()
ht = ttc / 1.2
par_canal = (x25.groupby("canal")["montant"].sum() / x25.groupby("canal")["id_commande"].nunique())
print("TTC remises déduites :", O.eur(ttc), "| HT :", O.eur(ht), "| moyenne des paniers moyens des canaux :", O.eur(par_canal.mean()))
```
<!--sortie-->
```text
TTC remises déduites : 102,33 € | HT : 85,27 € | moyenne des paniers moyens des canaux : 102,38 €
```

**Lecture.** Le panier moyen 2025 est de 102,33 € TTC, remises déduites, et de 85,27 € hors taxe. La moyenne des paniers moyens des canaux (102,38 €) en est proche **ici**, mais rien ne l'y oblige : si les canaux avaient des tailles très différentes, l'écart serait plus grand. La règle du glossaire (calculer sur le total) protège de ce risque, même quand il est faible.

**Étape 3 — Le glossaire, en YAML.** On écrit les définitions retenues sous une forme qu'un programme peut lire, puis on la relit.

```python
import yaml
glossaire = {"client_actif": {"definition": "au moins une commande payée sur les 12 derniers mois", "calcul": "COUNT(DISTINCT id_client), commandes du 01/01 au 31/12", "proprietaire": "gérante"},
             "panier_moyen": {"definition": "CA TTC remises déduites / commandes distinctes, sur le total", "calcul": "SUM(montant) / COUNT(DISTINCT id_commande)", "proprietaire": "analyse"}}
chemin = os.path.join(TMP4C, "glossaire_v1.yaml")
open(chemin, "w", encoding="utf-8").write(yaml.safe_dump(glossaire, allow_unicode=True, sort_keys=False))
print(list(yaml.safe_load(open(chemin, encoding="utf-8"))), "|", yaml.safe_load(open(chemin, encoding="utf-8"))["panier_moyen"]["calcul"])
```
<!--sortie-->
```text
['client_actif', 'panier_moyen'] | SUM(montant) / COUNT(DISTINCT id_commande)
```

**À vous.** Ajoutez l'entrée « commande annulée » du livre et une entrée « trimestre ». Quel serait le contre-exemple de chacune ?

### Application 4.6 — Le lignage d'un rapport et l'analyse d'impact (sections 4.3.2 et 4.3.3)

**Objectif.** Décrire les dépendances d'un livrable, remonter en amont, mesurer l'impact en aval, et dessiner le graphe.

**Étape 1 — Construire le lignage.** On ajoute à la synthèse du livre un fichier de paramètres (le taux de taxe) dont dépend le calcul de marge.

```python
L = O.Lignage()
for nom in ["commandes", "lignes_commande", "produits", "parametres.yaml"]:
    L.ajouter(nom, "source")
L.ajouter("ca_par_canal.sql", "requete", ["commandes", "lignes_commande"])
L.ajouter("marge.py", "script", ["lignes_commande", "produits", "parametres.yaml"])
L.ajouter("synthese_t4.csv", "table", ["ca_par_canal.sql", "marge.py"])
L.ajouter("message_gerante.md", "sortie", ["synthese_t4.csv"])
print("sources du message :", L.sources("message_gerante.md"))
print("si le taux de taxe change :", L.aval("parametres.yaml"))
print("si `commandes` change :", L.aval("commandes"))
```
<!--sortie-->
```text
sources du message : ['commandes', 'lignes_commande', 'parametres.yaml', 'produits']
si le taux de taxe change : ['marge.py', 'message_gerante.md', 'synthese_t4.csv']
si `commandes` change : ['ca_par_canal.sql', 'message_gerante.md', 'synthese_t4.csv']
```

**Étape 2 — Les éléments sans effet.** Quels éléments ne dépendent **ni** des paramètres **ni** des commandes ? Et existe-t-il une source dont rien ne dépend (donc inutile) ?

```python
touches = set(L.aval("parametres.yaml")) | set(L.aval("commandes"))
print("éléments non touchés :", sorted(set(L.noeuds) - touches - {"parametres.yaml", "commandes"}))
print("sources inutilisées :", [n for n in L.noeuds if not L.noeuds[n]["depend"] and not L.aval(n)])
```
<!--sortie-->
```text
éléments non touchés : ['lignes_commande', 'produits']
sources inutilisées : []
```

**Lecture.** Aucune source n'est inutilisée. Les éléments que ni le taux de taxe ni les commandes n'atteignent sont `lignes_commande` et `produits` : ce sont d'autres sources. Si le taux de taxe change, il faut relancer `marge.py`, la synthèse et le message ; si les commandes changent, `ca_par_canal.sql`, la synthèse et le message : `marge.py` n'est **pas** touché, puisqu'il ne lit pas les commandes.

**Étape 3 — Le dessin.**

```python hide
import fig_ch04 as F4
L.dessiner("ch04-c-lignage.png", titre="Lignage de la synthèse, avec le fichier de paramètres", surligne=["parametres.yaml"] + L.aval("parametres.yaml"), largeur=10.0, hauteur=3.8)
```
<!--sortie-->
```text
figure : ch04-c-lignage.png
```

![Lignage de la synthèse avec son fichier de paramètres : en couleur pleine, tout ce qui dépend du taux de taxe.](figures/ch04-c-lignage.png)

**À vous.** Ajoutez un nœud `graphique_t4.png` qui dépend de `synthese_t4.csv`. Que devient la liste « si `commandes` change » ?

### Application 4.7 — Empreintes et manifeste (sections 4.3.4 et 4.3.6)

**Objectif.** Construire un manifeste, détecter une modification, et comprendre ce qu'une empreinte de **tableau** dit de l'ordre des lignes.

**Étape 1 — Le manifeste d'une livraison et sa vérification.**

```python
fichiers = ["clients.csv", "produits.csv", "commandes.csv", "lignes_commande.csv"]
manif = {f: O.empreinte_fichier(os.path.join(O.donnees(), f))[:12] for f in fichiers}
def verifier(manif, dossier):
    return {f: O.empreinte_fichier(os.path.join(dossier, f))[:12] == h for f, h in manif.items()}
print(verifier(manif, O.donnees()))
```
<!--sortie-->
```text
{'clients.csv': True, 'produits.csv': True, 'commandes.csv': True, 'lignes_commande.csv': True}
```

**Étape 2 — Une modification discrète.** On copie la livraison, on change **une** valeur d'un fichier, et l'on vérifie à nouveau.

```python
copie = os.path.join(TMP4C, "livraison"); os.makedirs(copie)
for f in fichiers:
    shutil.copy(os.path.join(O.donnees(), f), copie)
p = os.path.join(copie, "produits.csv")
open(p, "w", encoding="utf-8").write(open(p, encoding="utf-8").read().replace("Cuisine", "Cuisinier", 1))
print(verifier(manif, copie))
```
<!--sortie-->
```text
{'clients.csv': True, 'produits.csv': False, 'commandes.csv': True, 'lignes_commande.csv': True}
```

**Lecture.** La modification d'**un seul mot** dans `produits.csv` est détectée (`False`), les trois autres fichiers restent conformes.

**Étape 3 — L'empreinte d'un tableau dépend de l'ordre des lignes.** Mélanger les lignes ne change pas le **contenu**, mais change l'empreinte, sauf si l'on trie avant de calculer.

```python
m = produits.sample(frac=1, random_state=1)
print("même empreinte après mélange :", O.empreinte_df(m) == O.empreinte_df(produits))
print("même empreinte après tri sur la clé :", O.empreinte_df(m.sort_values("id_produit")) == O.empreinte_df(produits.sort_values("id_produit")))
```
<!--sortie-->
```text
même empreinte après mélange : False
même empreinte après tri sur la clé : True
```

**Lecture.** Le même contenu, dans un autre ordre, donne une **autre** empreinte ; trié sur la clé avant le calcul, la même. Pour comparer des **contenus**, on trie avant de calculer l'empreinte (ou l'on calcule l'empreinte du fichier brut, qui dépend de l'ordre des octets).

**À vous.** Dans un manifeste, faut-il calculer l'empreinte du fichier ou du tableau lu ? Donnez un argument pour chaque choix.

### Application 4.8 — Rejouer un chiffre depuis le brut (section 4.3.8)

**Objectif.** Documenter un second chiffre, le rejouer, le recouper par un calcul indépendant, et vérifier que la documentation **détecte** un fichier remplacé.

**Étape 1 — La documentation et le rejeu.** Chiffre visé : le CA TTC du canal Réseaux au troisième trimestre 2024.

```python
doc = {"question": "CA TTC du canal Réseaux, T3 2024",
       "sources": {"commandes": {"fichier": "commandes.csv", "empreinte": manif["commandes.csv"]},
                   "lignes_commande": {"fichier": "lignes_commande.csv", "empreinte": manif["lignes_commande.csv"]}},
       "filtres": [("canal", "==", "Réseaux"), ("date_commande", ">=", "2024-07-01"), ("date_commande", "<=", "2024-09-30")],
       "mesure": "montant"}
res = O.rejouer(doc)
print(res)
```
<!--sortie-->
```text
{'empreintes_ok': True, 'valeur': 30903.86, 'lignes': 657}
```

**Étape 2 — Un recoupement indépendant.** On refait le calcul **sans** la fonction `rejouer`, avec une jointure écrite à la main.

```python
x = lig.merge(cmd[["id_commande", "canal", "date_commande"]], on="id_commande")
y = x[(x["canal"] == "Réseaux") & (x["date_commande"].between("2024-07-01", "2024-09-30"))]
print("recoupement :", round(y["montant"].sum(), 2), "| lignes :", len(y), "| identique :", round(y["montant"].sum(), 2) == res["valeur"])
```
<!--sortie-->
```text
recoupement : 30903.86 | lignes : 657 | identique : True
```

**Lecture.** Le rejeu donne 30 903,86 € sur 657 lignes, et le calcul indépendant (une jointure écrite à la main) le confirme.

**Étape 3 — Le fichier remplacé.** On rejoue la documentation sur la copie modifiée de l'application 4.7 : les chiffres sortent, mais l'empreinte ne correspond plus.

```python
res_copie = O.rejouer(doc, dossier=copie)
print("sur la copie dont produits.csv a changé :", res_copie)
```
<!--sortie-->
```text
sur la copie dont produits.csv a changé : {'empreintes_ok': True, 'valeur': 30903.86, 'lignes': 657}
```

**Lecture.** Sur la copie, l'empreinte est « ok » : la documentation ne décrit que **deux sources** (`commandes` et `lignes_commande`), pas `produits`. Une documentation ne protège que ce qu'elle déclare.

**À vous.** Dans la copie, seul `produits.csv` a été modifié : pourquoi le rejeu ne le voit-il pas ? Que faudrait-il ajouter à la documentation pour qu'elle le voie ?

## Exercices

### Exercice 4.1 ⭐ — Qu'est-ce qui manque ? (section 4.1.1)

Une collègue vous transmet un fichier avec ce seul mot d'accompagnement : « `ventes_final2.xlsx` : ventes nettoyées, chiffres en euros, voir mon notebook. » Listez **six** informations qui manquent pour que vous puissiez refaire son travail et défendre ses chiffres.

### Exercice 4.2 ⭐ — La fiche du catalogue fournisseur (section 4.1.2)

Remplissez la fiche de `catalogue_fournisseur.csv` avec `O.fiche_jeu` : source, date d'extraction (inventée mais précisée), périmètre, grain, clé, limites. Vérifiez par le code que la clé annoncée est bien unique, et signalez-le dans les limites si ce n'est pas le cas.

### Exercice 4.3 ⭐⭐ — L'équation de conservation (section 4.1.3)

Un journal de nettoyage indique : 5 000 lignes lues ; étape 1 : 120 lignes retirées ; étape 2 : 300 lignes modifiées, aucune retirée ; étape 3 : 480 lignes retirées ; étape 4 : 35 lignes retirées. Le rapport final annonce **4 380** lignes. L'équation de conservation est-elle vérifiée ? Si non, de combien est l'écart et que cela signifie-t-il ?

### Exercice 4.4 ⭐⭐ — Nommer ses fichiers (section 4.1.6)

Renommez, selon la convention `nom_AAAA-MM-JJ_vN.ext`, ces cinq fichiers : `clients_final.csv` (extrait le 5 mars 2025, première version), `clients_final2.csv` (même extraction, corrigé), `Copie de ventes (3).xlsx` (ventes du T1 2025, troisième version), `export 12-02.csv` (export de caisse du 2 décembre 2025), `rapport_VRAI.docx` (rapport du T2 2025, deuxième version). Que gagne-t-on à écrire la date en ISO ?

### Exercice 4.5 ⭐ — Des commentaires qui disent pourquoi (section 4.1.6)

Réécrivez ces trois commentaires pour qu'ils expliquent **la raison** et non le geste, en inventant une raison plausible tirée des données de la boutique : (a) `df = df[df["montant"] > 0]  # garde les montants positifs` ; (b) `df["total"] = df["total"] / 100  # divise par 100` ; (c) `df = df.drop_duplicates("email")  # supprime les doublons`.

### Exercice 4.6 ⭐⭐ — Ce que le squelette ne sait pas dire (section 4.2.2)

Fabriquez le squelette de `site_commandes` (lu en texte). Notez **trois** choses qu'il vous apprend, puis **trois** choses qu'il ne peut pas vous apprendre et que seul un humain peut écrire.

### Exercice 4.7 ⭐⭐ — Le dictionnaire de cinq colonnes (section 4.2.3)

Écrivez le dictionnaire (libellé, type technique, type logique, unité, valeurs permises, obligatoire, codage des manquants, règle ou source) de `order_ref`, `created_at`, `status`, `total` et `currency` dans `site_commandes`. Faites apparaître le changement d'unité de `total` et les trois écritures de `status`.

### Exercice 4.8 ⭐⭐ — Un test sur le statut (section 4.2.5)

Écrivez l'entrée de dictionnaire de `status` avec ses valeurs permises (`paid`, `cancelled`), lancez `verifier_dictionnaire` sur le fichier brut, puis normalisez la casse et relancez. Combien de lignes sont hors domaine avant, après ?

### Exercice 4.9 ⭐ — Une définition unique de « commande annulée » (section 4.2.6)

Écrivez l'entrée de glossaire de « commande annulée » (définition, calcul, contre-exemple, propriétaire). Combien de commandes `cancelled` compte le fichier brut du site, et combien après avoir retiré les doublons d'export ?

### Exercice 4.10 ⭐⭐ — Le lignage d'une campagne (section 4.3.2)

Une campagne d'e-mails suit cette chaîne : `rapprochement.py` lit `crm.csv` et `site.csv` ; il produit `clients_uniques.csv` ; `campagne.csv` est fabriqué à partir de `clients_uniques.csv` et de `consentements.csv` ; `courriel_envoye.log` découle de `campagne.csv`. Écrivez le lignage et répondez : si `consentements.csv` change, quoi relancer ? Et d'où vient exactement `courriel_envoye.log` ?

### Exercice 4.11 ⭐⭐⭐ — Un journal d'audit qui ne s'efface pas (section 4.3.5)

Écrivez cinq événements dans un journal d'audit, puis une fonction `ajout_seulement(ancien, nouveau)` qui vérifie que l'ancien état du fichier est un **préfixe** du nouveau. Montrez qu'elle accepte un ajout et refuse la modification d'une ligne ancienne.

### Exercice 4.12 ⭐⭐⭐ — Une documentation qui se trompe (section 4.3.8)

Une collègue vous a laissé cette documentation : « CA TTC du canal Site, T4 2025 = 211 433,79 € ; filtres : `canal == 'Site'`, `date_commande >= '2025-10-01'`, `date_commande <= '2025-12-30'`. » Rejouez-la. Le chiffre annoncé est-il retrouvé ? Trouvez la cause de l'écart, corrigez la documentation et chiffrez l'effet de l'erreur.

## Corrigés

### Corrigé 4.1

Il manque, au minimum : (1) la **source** (d'où viennent les données brutes, quel système) ; (2) la **date d'extraction** ; (3) le **périmètre** (quelles années, quels canaux, quelles lignes exclues) ; (4) le **grain** (une ligne = une commande, une ligne de commande, un client ?) ; (5) les **règles de nettoyage** avec leurs effectifs (« nettoyées » ne dit pas ce qui a été retiré) ; (6) la **définition** des chiffres : TTC ou HT, remises déduites ou non, périodes. Et aussi : la **version** du fichier, l'**unité** réelle (« euros » sans date de validité est suspect), le **lieu du notebook** et la façon de le relancer. La phrase de la collègue est une affirmation, pas une documentation.

### Corrigé 4.2

```python
cat = O.charger("catalogue_fournisseur", dtype=str)
O.fiche_jeu(cat, **{"nom": "catalogue_fournisseur (v1)", "source": "catalogue envoyé par le fournisseur", "date d'extraction": "2025-11-20 (supposée)",
                    "périmètre": "produits proposés par le fournisseur, pas tous ceux de la boutique", "une ligne =": "un article du catalogue fournisseur",
                    "clé": "code_fournisseur", "limites connues": "désignations réécrites (casse, accents, abréviations), codes différents de ceux de la boutique"})
print("code_fournisseur unique :", cat["code_fournisseur"].is_unique)
```
<!--sortie-->
```text
nom                   : catalogue_fournisseur (v1)
source                : catalogue envoyé par le fournisseur
date d'extraction     : 2025-11-20 (supposée)
périmètre             : produits proposés par le fournisseur, pas tous ceux de la boutique
une ligne =           : un article du catalogue fournisseur
clé                   : code_fournisseur
limites connues       : désignations réécrites (casse, accents, abréviations), codes différents de ceux de la boutique
lignes                : 118
colonnes              : 5
empreinte du contenu  : 29a5a9a41a19
code_fournisseur unique : True
```

La clé est bien unique (`True`), mais elle **n'est pas** celle de la boutique : la mention « codes différents de ceux de la boutique » est la limite la plus utile, parce qu'elle annonce qu'il faudra un **rapprochement** (section 2.5) avant toute jointure.

### Corrigé 4.3

Lignes finales attendues : $5\,000-120-480-35=4\,365$ (l'étape 2 ne retire rien). Le rapport annonce 4 380 : **15 lignes de trop**. L'équation de conservation n'est donc **pas** vérifiée : une étape a **créé** des lignes que le journal ne mentionne pas (par exemple une jointure qui a dupliqué des lignes, ou une concaténation faite deux fois). On ne cherche pas l'erreur dans le résultat, on la cherche dans le journal, à l'étape où l'effectif « après » ne vaut pas « avant » moins « retirées ».

### Corrigé 4.4

`clients_2025-03-05_v1.csv` ; `clients_2025-03-05_v2.csv` ; `ventes_t1_2025_v3.xlsx` (ou `ventes_2025-Q1_v3.xlsx`) ; `export_caisse_2025-12-02.csv` ; `rapport_t2_2025_v2.docx`. L'écriture **année-mois-jour** a un grand avantage : l'**ordre alphabétique** des noms est l'**ordre chronologique**, et il n'y a aucune ambiguïté entre `12-02` (le 12 février, ou le 2 décembre ?).

### Corrigé 4.5

(a) `# les montants négatifs sont des avoirs (retours), traités à part dans l'analyse des retours` ; (b) `# le site exporte les totaux en centimes depuis le 15/09/2025` ; (c) `# une même personne peut avoir été saisie plusieurs fois : on garde la saisie la plus ancienne (id_crm le plus petit)`. Chaque commentaire répond à la question qu'une relectrice se poserait : **pourquoi** ?

### Corrigé 4.6

```python
O.squelette(O.charger("site_commandes", dtype=str))
```

Le squelette **apprend** : (1) toutes les colonnes sont du texte, y compris `total` et `created_at` (donc rien n'est typé) ; (2) `promo_code` est vide pour environ 84 % des lignes (l'absence de code est un cas normal, pas une erreur) ; (3) `order_ref` a **moins de valeurs distinctes que de lignes** (des doublons d'export). Il **ne peut pas** dire : (1) que `total` est en euros avant le 15 septembre et en **centimes** après ; (2) que `paid`, `PAID` et `Paid` sont le **même** statut ; (3) que `test@example.com` désigne des commandes de test à écarter. Aucune de ces trois informations n'est dans les valeurs : elles viennent de la source ou de l'enquête.

### Corrigé 4.7

| Colonne | Libellé | Type technique → logique | Unité | Valeurs permises | Oblig. | Manquants | Règle ou source |
|---|---|---|---|---|---|---|---|
| `order_ref` | Référence de la commande | `str` → identifiant | | `WEB-` + 6 chiffres (ou `WEB-T` pour un test) | oui | jamais vide | plateforme du site ; **non unique** (doublons d'export) |
| `created_at` | Date et heure de création | `str` → date-heure | | ISO ; **sans fuseau** avant le 15/09, en **UTC** (`Z`) après | oui | jamais vide | plateforme |
| `status` | Statut de la commande | `str` → catégorie | | `paid`, `cancelled` après mise en minuscules ; écrit `paid`, `PAID` ou `Paid` | oui | jamais vide | plateforme |
| `total` | Total de la commande TTC, remises déduites | `str` → montant | € jusqu'au 14/09/2025, **centimes** à partir du 15/09 | positif | oui | jamais vide | somme des lignes ; **texte** avec `€`, virgule ou point |
| `currency` | Devise | `str` → catégorie | | `EUR` ; écrit `EUR`, `eur` ou `€` | oui | jamais vide | plateforme |

Le dictionnaire écrit **les pièges** que le squelette ne voit pas : l'unité qui change à une date, la casse du statut, le format du total.

### Corrigé 4.8

```python
dsite = pd.DataFrame([{"colonne": "status", "type": "str", "valeurs_permises": "paid|cancelled", "obligatoire": "oui"}])
so_c = O.charger("site_commandes", dtype=str)[["status"]]
print("avant :", O.verifier_dictionnaire(so_c, dsite))
so_c["status"] = so_c["status"].str.lower()
print("après :", O.verifier_dictionnaire(so_c, dsite) or "aucune anomalie")
```
<!--sortie-->
```text
avant : ['status : 2444 valeurs hors domaine (paid|cancelled)']
après : aucune anomalie
```

Avant la normalisation, le test signale **2 444** lignes (celles écrites `PAID` ou `Paid`) comme **hors domaine** ; après `str.lower()`, il ne reste plus d'anomalie. C'est la preuve que la **normalisation** de la casse est une étape de nettoyage **exigée par le dictionnaire**.

### Corrigé 4.9

Entrée de glossaire : **commande annulée** — *définition* : commande dont le statut vaut `cancelled` après mise en minuscules ; *calcul* : `lower(status) = 'cancelled'` ; *traitement* : exclue du chiffre d'affaires et du nombre de commandes ; *contre-exemple* : une commande **retournée** après livraison n'est pas annulée ; *propriétaire* : la gérante.

```python
so9 = O.charger("site_commandes", dtype=str)
print("lignes cancelled dans le brut :", int((so9["status"].str.lower() == "cancelled").sum()))
print("commandes annulées distinctes :", int(so9.loc[so9["status"].str.lower() == "cancelled", "order_ref"].nunique()))
```
<!--sortie-->
```text
lignes cancelled dans le brut : 186
commandes annulées distinctes : 181
```

Le fichier brut compte **186 lignes** `cancelled` mais seulement **181 commandes annulées distinctes** : cinq lignes sont des **doublons d'export** de commandes annulées. Compter des lignes plutôt que des commandes distinctes est exactement l'erreur de grain que la définition doit empêcher.

### Corrigé 4.10

```python
L10 = O.Lignage()
for nom in ["crm.csv", "site.csv", "consentements.csv"]:
    L10.ajouter(nom, "source")
L10.ajouter("rapprochement.py", "script", ["crm.csv", "site.csv"])
L10.ajouter("clients_uniques.csv", "table", ["rapprochement.py"])
L10.ajouter("campagne.csv", "table", ["clients_uniques.csv", "consentements.csv"])
L10.ajouter("courriel_envoye.log", "sortie", ["campagne.csv"])
print("si consentements.csv change :", L10.aval("consentements.csv"))
print("sources de courriel_envoye.log :", L10.sources("courriel_envoye.log"))
```
<!--sortie-->
```text
si consentements.csv change : ['campagne.csv', 'courriel_envoye.log']
sources de courriel_envoye.log : ['consentements.csv', 'crm.csv', 'site.csv']
```

Si `consentements.csv` change, il faut relancer **`campagne.csv`** puis **`courriel_envoye.log`** ; `rapprochement.py` et `clients_uniques.csv` ne sont pas touchés. Le journal d'envoi a **trois sources** : `crm.csv`, `site.csv` et `consentements.csv`. Un lignage de ce type rend visible un risque juridique : le fichier des consentements est une **entrée directe** de l'envoi.

### Corrigé 4.11

```python
a1 = os.path.join(TMP4C, "audit_hier.jsonl"); a2 = os.path.join(TMP4C, "audit_aujourdhui.jsonl")
evts = [("2026-01-05 09:00", "analyste", "réception", "crm_v1.csv", "aaa"), ("2026-01-05 09:30", "analyste", "nettoyage", "crm_propre.csv", "bbb"),
        ("2026-01-05 10:00", "gérante", "validation", "crm_propre.csv", "bbb"), ("2026-01-06 08:00", "analyste", "réception", "site_v1.csv", "ccc"),
        ("2026-01-06 08:20", "analyste", "nettoyage", "site_propre.csv", "ddd")]
for e in evts[:3]:
    O.consigner(a1, *e)
shutil.copy(a1, a2)
for e in evts[3:]:
    O.consigner(a2, *e)

def ajout_seulement(ancien, nouveau):
    a, n = open(ancien, encoding="utf-8").read(), open(nouveau, encoding="utf-8").read()
    return n.startswith(a)

print("ajout accepté :", ajout_seulement(a1, a2))
open(a2, "w", encoding="utf-8").write(open(a2, encoding="utf-8").read().replace("validation", "relecture", 1))
print("après retouche d'une ligne ancienne :", ajout_seulement(a1, a2))
```
<!--sortie-->
```text
ajout accepté : True
après retouche d'une ligne ancienne : False
```

Un journal d'audit **n'est valable que s'il n'est jamais retouché** : la vérification « l'ancien contenu est un préfixe du nouveau » accepte un ajout et refuse la moindre modification d'une ligne passée (ici, « validation » changé en « relecture »). Pour une garantie plus forte, on peut aussi **enchaîner** les empreintes (chaque ligne contient l'empreinte de la précédente), de sorte qu'on ne puisse pas retoucher le passé sans casser la chaîne.

### Corrigé 4.12

```python
doc12 = {"sources": {"commandes": {"fichier": "commandes.csv", "empreinte": O.empreinte_fichier(os.path.join(O.donnees(), "commandes.csv"))[:12]},
                     "lignes_commande": {"fichier": "lignes_commande.csv", "empreinte": O.empreinte_fichier(os.path.join(O.donnees(), "lignes_commande.csv"))[:12]}},
         "filtres": [("canal", "==", "Site"), ("date_commande", ">=", "2025-10-01"), ("date_commande", "<=", "2025-12-30")], "mesure": "montant"}
faux = O.rejouer(doc12)
doc12["filtres"][2] = ("date_commande", "<=", "2025-12-31")
juste = O.rejouer(doc12)
print("avec <= 2025-12-30 :", faux["valeur"], "| avec <= 2025-12-31 :", juste["valeur"], "| écart :", round(juste["valeur"] - faux["valeur"], 2))
```
<!--sortie-->
```text
avec <= 2025-12-30 : 210063.78 | avec <= 2025-12-31 : 211433.79 | écart : 1370.01
```

Le chiffre annoncé (211 433,79 €) n'est **pas** retrouvé : la borne haute du filtre est le **30 décembre** au lieu du **31**, de sorte que le dernier jour du trimestre est oublié. La documentation corrigée (`<= '2025-12-31'`) redonne 211 433,79 €. L'effet de l'erreur est l'écart affiché : le chiffre d'affaires **d'une seule journée** (le 31 décembre), que personne n'aurait vu sans rejouer. C'est l'intérêt d'une documentation **exécutable** : une erreur de rédaction devient une erreur détectable.

## Pistes pour les « À vous » des applications

- **4.1.** La fiche gagne `version : v1` et `propriétaire : équipe du site (à confirmer)`. À la personne qui a fait l'export, on demande par écrit : « à quelle date et à quelle heure l'export a-t-il été lancé, et avec quel filtre de période ? ».
- **4.2.** Sans la conversion, le chiffre d'affaires nettoyé serait de **23 891 020,95 €** au lieu de 600 164,13 €, soit près de **quarante fois** trop : les 2 367 commandes d'après le 15 septembre pèseraient cent fois leur valeur.
- **4.3.** Dans `clients`, cinq colonnes sont marquées sensibles : l'identifiant (indirecte), l'année de naissance, la ville et le consentement (personnelles), et la validité de l'e-mail (indirecte). Le canal d'acquisition, la carte de fidélité et la date d'inscription ne le sont pas, mais **croisés** avec la ville et l'année de naissance ils peuvent aider à retrouver une personne : c'est l'objet du chapitre 5.
- **4.4.** Un consentement vide est d'abord un défaut **de saisie** (ou d'absence de recueil) : le dictionnaire a raison de dire « obligatoire ». On peut décider de le traiter comme « non » par prudence, **à écrire** dans le dictionnaire (`vide = non renseigné, traité comme refus`) et dans le journal des changements, avec la date et la raison.
- **4.5.** « Commande annulée » : statut `cancelled` après mise en minuscules, exclue du chiffre d'affaires ; contre-exemple : une commande retournée. « Trimestre » : trimestre civil, du 1er janvier, avril, juillet ou octobre au dernier jour du troisième mois, bornes **incluses** ; contre-exemple : une extraction arrêtée au 15 du dernier mois.
- **4.6.** Avec `graphique_t4.png` qui dépend de `synthese_t4.csv`, la liste « si `commandes` change » devient `['ca_par_canal.sql', 'graphique_t4.png', 'message_gerante.md', 'synthese_t4.csv']` (le graphique y entre).
- **4.7.** L'empreinte du **fichier** prouve que les octets sont les mêmes (rapide, indépendante de la lecture, mais sensible à un simple changement de fin de ligne). L'empreinte du **tableau lu** ignore ces détails de format, à condition de trier et de fixer les types, mais suppose que la lecture soit elle-même reproductible.
- **4.8.** `rejouer` ne vérifie que les sources déclarées dans `sources`. Pour que la modification de `produits.csv` soit vue, il faudrait déclarer `produits.csv` (et son empreinte) dans la documentation, même si le calcul ne s'en sert pas directement, parce qu'une valeur recalculée par un autre chemin peut en dépendre demain.

```python hide
shutil.rmtree(TMP4C, ignore_errors=True)
```
