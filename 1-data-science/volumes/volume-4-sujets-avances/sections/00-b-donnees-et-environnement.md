# Les données, les modèles et l'environnement du volume

## Les jeux du volume

Dans ce volume, la boutique change d'échelle. Le volume III observait douze mille clients ; ici il faut des **images** à reconnaître, des **avis** à lire, des **millions de lignes** à traiter, des **exports sales** à nettoyer, et un modèle à **mettre en service**. Les jeux sont donc de natures très différentes : un seul est **réel** (des chiffres manuscrits), les autres sont **simulés** avec des graines fixes (script `build/donnees4.py`) : vous obtiendrez exactement les mêmes chiffres que dans le livre.

| Fichier ou source | Contenu | Utilisé surtout dans |
|---|---|---|
| `mnist_sous_ensemble.npz` | **jeu réel** : 12 000 images de chiffres manuscrits (28 × 28 pixels) | chapitre 1 (réseaux, convolutions) |
| `ventes_quotidiennes.csv` | les ventes journalières de la boutique sur trois ans | chapitre 1 (réseaux récurrents) |
| `avis_clients.csv` | des avis de clients en français, avec une note de 1 à 5 | chapitre 2 (langage) |
| `clients_ml.csv` | les 12 000 clients du volume III, avec leur départ à 90 jours | chapitre 4 et projet (mise en production) |
| `sources/*.csv` | des exports « bruts » volontairement sales (commandes, clients, produits) | chapitre 5 (ingénierie des données) |
| générateur `gros_volume` | des millions de transactions, écrites à la demande en format Parquet | chapitre 3 (calcul distribué) |

Chargeons-les et regardons, comme toujours, leur forme et leurs valeurs manquantes :

```python hide-code
import os, sys, tempfile, shutil, importlib
import numpy as np
import pandas as pd

sys.path.insert(0, "build")
import donnees4

mn = np.load("donnees/mnist_sous_ensemble.npz")
ventes = pd.read_csv("donnees/ventes_quotidiennes.csv")
avis = pd.read_csv("donnees/avis_clients.csv")
clients = pd.read_csv("donnees/clients_ml.csv")
sources = {nom: pd.read_csv(f"donnees/sources/{nom}.csv") for nom in
           ["commandes_export", "clients_crm", "produits_catalogue", "produits_fournisseur", "verite_clients", "verite_produits"]}
print(f"mnist (apprentissage)  {mn['x_train'].shape[0]:6d} images {mn['x_train'].shape[1]}x{mn['x_train'].shape[2]}")
print(f"mnist (test)           {mn['x_test'].shape[0]:6d} images")
for nom, tab in [("ventes_quotidiennes", ventes), ("avis_clients", avis), ("clients_ml", clients)]:
    print(f"{nom:22s} {tab.shape[0]:6d} lignes, {tab.shape[1]:2d} colonnes, {int(tab.isna().sum().sum()):5d} valeur(s) manquante(s)")
for nom, tab in sources.items():
    print(f"sources/{nom:22s} {tab.shape[0]:6d} lignes, {tab.shape[1]:2d} colonnes")
```
<!--sortie-->
```text
mnist (apprentissage)   10000 images 28x28
mnist (test)             2000 images
ventes_quotidiennes      1096 lignes,  5 colonnes,     0 valeur(s) manquante(s)
avis_clients             8000 lignes,  6 colonnes,     0 valeur(s) manquante(s)
clients_ml              12000 lignes, 24 colonnes,  6426 valeur(s) manquante(s)
sources/commandes_export        19700 lignes,  6 colonnes
sources/clients_crm              5000 lignes,  6 colonnes
sources/produits_catalogue         48 lignes,  4 colonnes
sources/produits_fournisseur       40 lignes,  3 colonnes
sources/verite_clients           5000 lignes,  2 colonnes
sources/verite_produits            40 lignes,  2 colonnes
```

Les 6 426 valeurs manquantes de `clients_ml.csv` sont **voulues** (nous y revenons plus bas) ; tous les autres jeux sont complets.

## Des chiffres manuscrits : `mnist_sous_ensemble.npz`

Le chapitre 1 a besoin d'**images** : c'est pour elles qu'ont été inventés les réseaux convolutifs. Nous utilisons **MNIST**, un classique réel : des chiffres de 0 à 9 écrits à la main, numérisés en 28 × 28 pixels en niveaux de gris (chaque pixel est un entier de 0, le fond, à 255, l'encre). Il a été constitué par Yann LeCun, Corinna Cortes et Christopher Burges ; nous le récupérons via OpenML, qui l'indique sous la licence « Public » (à vérifier avant tout usage commercial). Pour que les entraînements tiennent dans le temps d'un exemple de livre, nous n'en gardons qu'un **sous-ensemble** tiré au hasard, de façon stratifiée et à graine fixe : 10 000 images pour l'apprentissage et 2 000 pour le test. Le fichier, d'environ 2 Mo, est fourni ; le script `build/telecharger_mnist.py` montre comment il a été fabriqué.

```python hide
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import style
style.setup()
x, y = mn["x_train"], mn["y_train"]
fig, axes = plt.subplots(2, 10, figsize=(10, 2.5))
for c in range(10):
    for r in range(2):
        axes[r, c].imshow(x[np.where(y == c)[0][r]], cmap="gray_r")
        axes[r, c].axis("off")
        axes[r, c].grid(False)
    axes[0, c].set_title(str(c), fontsize=10)
style.save(fig, "ch00-mnist.png")
print("effectifs par chiffre (apprentissage) :", np.bincount(y, minlength=10).tolist())
print("valeurs des pixels :", int(x.min()), "à", int(x.max()), "; part de pixels non nuls :", round(float((x > 0).mean()), 3), "; pixel moyen :", round(float(x.mean()), 1))
print("test : effectifs", np.bincount(mn["y_test"], minlength=10).tolist())
```
<!--sortie-->
```text
figure : ch00-mnist.png
effectifs par chiffre (apprentissage) : [986, 1125, 999, 1020, 975, 902, 982, 1042, 975, 994]
valeurs des pixels : 0 à 255 ; part de pixels non nuls : 0.192 ; pixel moyen : 33.4
test : effectifs [197, 225, 200, 204, 195, 180, 197, 208, 195, 199]
```

![Deux exemples de chaque chiffre de MNIST, pris dans le jeu d'apprentissage. Chaque image fait 28 × 28 pixels ; les écritures varient beaucoup d'une personne à l'autre.](figures/ch00-mnist.png)

Les dix classes sont à peu près équilibrées : de 902 images pour le 5 à 1 125 pour le 1 dans le jeu d'apprentissage (de 180 à 225 dans le jeu de test). Seulement **19,2 % des pixels sont non nuls** : une image est surtout du fond, avec un pixel moyen de 33,4 sur 255. Cette régularité sera utile au chapitre 1.

## Les ventes quotidiennes : `ventes_quotidiennes.csv`

Pour parler de **séquences**, le chapitre 1 reprend les ventes de la boutique, cette fois **jour par jour**, du 1er janvier 2023 au 31 décembre 2025 (1 096 jours : 2024 est bissextile). La série mélange les effets qu'on s'attend à trouver : une croissance régulière, un rythme **hebdomadaire**, un renforcement en fin d'année, des **promotions** ponctuelles et du bruit.

| Colonne | Signification |
|---|---|
| `date` | jour, au format `AAAA-MM-JJ` |
| `ventes` | chiffre d'affaires du jour, en € |
| `promo` | 1 s'il y avait une promotion ce jour-là |
| `jour_semaine` | 0 pour lundi, 6 pour dimanche |
| `mois` | numéro du mois |

```python hide
print("période :", ventes["date"].iloc[0], "à", ventes["date"].iloc[-1], "(", len(ventes), "jours )")
print("ventes : moyenne", round(ventes["ventes"].mean(), 1), "médiane", round(ventes["ventes"].median(), 1), "maximum", round(ventes["ventes"].max(), 1), "minimum", round(ventes["ventes"].min(), 1))
print("part de jours en promotion :", round(ventes["promo"].mean(), 3))
print("moyenne par jour de la semaine (0 = lundi) :", ventes.groupby("jour_semaine")["ventes"].mean().round(1).tolist())
print("décembre :", round(ventes.loc[ventes["mois"] == 12, "ventes"].mean(), 1), "; autres mois :", round(ventes.loc[ventes["mois"] != 12, "ventes"].mean(), 1))
print("moyenne par année :", ventes.groupby(ventes["date"].str[:4])["ventes"].mean().round(1).to_dict())
print("effet promo (moyenne avec / sans) :", round(ventes.loc[ventes["promo"] == 1, "ventes"].mean(), 1), "/", round(ventes.loc[ventes["promo"] == 0, "ventes"].mean(), 1))
```
<!--sortie-->
```text
période : 2023-01-01 à 2025-12-31 ( 1096 jours )
ventes : moyenne 154.1 médiane 145.3 maximum 356.2 minimum 67.2
part de jours en promotion : 0.07
moyenne par jour de la semaine (0 = lundi) : [115.8, 124.1, 132.9, 146.0, 175.1, 224.0, 161.0]
décembre : 182.6 ; autres mois : 151.4
moyenne par année : {'2023': 135.3, '2024': 153.4, '2025': 173.5}
effet promo (moyenne avec / sans) : 187.4 / 151.5
```

Les ventes valent en moyenne 154,1 € par jour (de 67,2 € à 356,2 €). Le samedi (jour 5) est le jour fort, avec 224,0 € en moyenne, contre 115,8 € le lundi. La moyenne annuelle passe de 135,3 € en 2023 à 153,4 € en 2024 puis 173,5 € en 2025. Décembre est environ un cinquième plus fort que les autres mois (182,6 € contre 151,4 €), et les 7 % de jours en promotion vendent en moyenne 187,4 € contre 151,5 €. Ce sont ces structures qu'un réseau récurrent devra apprendre.

## Les avis des clients : `avis_clients.csv`

Le chapitre 2 travaille sur du **texte** : huit mille avis de clients, en français, chacun avec une note de 1 à 5, le sujet principal (livraison, qualité, prix, service, emballage), la catégorie du produit (A à D) et le canal d'achat. Ces avis sont **simulés** : le texte a été fabriqué en assemblant des phrases-types, avec des fautes de frappe, quelques emojis, des avis très courts (« RAS », « Top !! »), des avis en anglais, des phrases à **négation** (« Rapide, la livraison ? Pas vraiment. ») et environ 8 % de désaccords entre le ton du texte et la note.

```python hide
a = avis.copy()
vocab_en = set(sum(donnees4.ANGLAIS.values(), []))
nie = set(sum([v for d in donnees4.NIE.values() for v in d.values()], []))
print("notes :", a["note"].value_counts().sort_index().to_dict())
print("anglais :", int(a["texte"].isin(vocab_en).sum()), round(100 * a["texte"].isin(vocab_en).mean(), 1))
print("très courts (< 3 mots) :", int((a["texte"].str.split().str.len() < 3).sum()))
print("avec phrase niée :", int(a["texte"].apply(lambda t: any(p in t for p in nie)).sum()))
print("longueur médiane (mots) :", int(a["texte"].str.split().str.len().median()), "; maximum :", int(a["texte"].str.split().str.len().max()))
print("sujets :", a["sujet"].value_counts().to_dict())
print("canaux :", a["canal"].value_counts().to_dict(), "; catégories :", a["categorie"].value_counts().sort_index().to_dict())
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
b = a[a["note"] != 3].copy()
b["positif"] = (b["note"] >= 4).astype(int)
Xa, Xb, ya, yb = train_test_split(b["texte"], b["positif"], test_size=0.25, random_state=0, stratify=b["positif"])
vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2)
lr = LogisticRegression(max_iter=3000, C=3).fit(vec.fit_transform(Xa), ya)
print("avis non neutres :", len(b), "; part positive :", round(b["positif"].mean(), 3))
print("référence TF-IDF + régression logistique, exactitude test :", round(lr.score(vec.transform(Xb), yb), 3))
niee = Xb.apply(lambda t: any(p in t for p in nie))
print("sur les avis contenant une négation :", int(niee.sum()), "avis ; exactitude", round(lr.score(vec.transform(Xb[niee]), yb[niee]), 3), "; sans négation :", round(lr.score(vec.transform(Xb[~niee]), yb[~niee]), 3))
en = Xb.isin(vocab_en)
print("sur les avis en anglais :", int(en.sum()), "; exactitude", round(lr.score(vec.transform(Xb[en]), yb[en]), 3))
```
<!--sortie-->
```text
notes : {1: 564, 2: 704, 3: 1234, 4: 2426, 5: 3072}
anglais : 433 5.4
très courts (< 3 mots) : 319
avec phrase niée : 2353
longueur médiane (mots) : 11 ; maximum : 32
sujets : {'livraison': 2234, 'qualite': 2181, 'service': 1411, 'prix': 1321, 'emballage': 853}
canaux : {'Site': 3699, 'Réseaux': 2310, 'Boutique': 1991} ; catégories : {'A': 2387, 'B': 2365, 'C': 1614, 'D': 1634}
avis non neutres : 6766 ; part positive : 0.813
référence TF-IDF + régression logistique, exactitude test : 0.942
sur les avis contenant une négation : 582 avis ; exactitude 0.955 ; sans négation : 0.935
sur les avis en anglais : 94 ; exactitude 0.957
```

Les notes sont majoritairement bonnes (5 498 notes de 4 ou 5 sur 8 000) ; 433 avis (5,4 %) sont en anglais, 319 comptent moins de trois mots, et 2 353 contiennent une phrase à négation. Un avis fait 11 mots en médiane (32 au maximum).

> ⚠️ **Ce corpus est plus facile qu'un vrai corpus, et il faut le dire.** Parce que le texte est assemblé à partir d'un petit nombre de phrases-types, des méthodes très simples le lisent presque parfaitement. Une régression logistique sur des fréquences de mots et de paires de mots (TF-IDF, section 2.1) distingue les avis positifs (note 4 ou 5) des négatifs (note 1 ou 2) avec une exactitude de **0,942** sur des avis mis de côté. Ce chiffre sera la **référence** du chapitre 2 : un modèle plus sophistiqué doit la battre pour justifier son coût. Contre-intuitivement, la référence ne fait pas moins bien sur les phrases niées (0,955 sur 582 avis) ou sur les avis en anglais (0,957 sur 94 avis) : ces phrases sont elles aussi répétées d'un avis à l'autre, donc mémorisables. Sur de vrais avis, l'écart serait bien plus grand ; le chapitre 2 le rappellera.

## Les clients : `clients_ml.csv`

Pour la mise en production (chapitre 4 et projet du cahier), nous reprenons **tels quels** les 12 000 clients du volume III : le fichier est une copie de celui de ce volume (même graine, mêmes colonnes), pour que ce livre se lise sans lui. Il contient 24 colonnes : un identifiant, **19 variables d'entrée** (comportement d'achat, satisfaction, support, âge, ville, canal…), trois colonnes de résultat et une colonne piégée. La cible à prédire est `churn_90j` (1 si le client ne commande plus dans les 90 jours suivants), qui vaut 1 pour 14 % des clients.

```python hide
print("clients_ml :", clients.shape, "; départs à 90 jours :", round(clients["churn_90j"].mean(), 3))
print("colonnes :", clients.columns.tolist())
cibles = ["id_client", "churn_90j", "depense_6m", "segment_vrai", "commandes_apres_cible"]
print("variables d'entrée :", len([c for c in clients.columns if c not in cibles]))
print("manquants par colonne :", {k: int(v) for k, v in clients.isna().sum().items() if v > 0})
```
<!--sortie-->
```text
clients_ml : (12000, 24) ; départs à 90 jours : 0.14
colonnes : ['id_client', 'age', 'ville', 'canal_acquisition', 'appareil', 'anciennete_mois', 'nb_commandes_12m', 'panier_moyen', 'montant_12m', 'recence_jours', 'nb_retours_12m', 'satisfaction_moy', 'nb_tickets_support_12m', 'programme_fidelite', 'nb_promos_recues_12m', 'part_achats_promo', 'taux_ouverture_email', 'delai_livraison_moy', 'categorie_preferee', 'revenu_zone', 'churn_90j', 'depense_6m', 'segment_vrai', 'commandes_apres_cible']
variables d'entrée : 19
manquants par colonne : {'appareil': 1829, 'panier_moyen': 1630, 'satisfaction_moy': 1533, 'delai_livraison_moy': 1434}
```

> ⚠️ **Colonnes à exclure des variables d'entrée.** Quatre colonnes ne sont **pas** des variables d'entrée : `id_client` (un identifiant), `depense_6m` (une autre cible), `segment_vrai` (la classe latente qui a servi à fabriquer les données : elle n'existe pas dans la vie réelle) et `commandes_apres_cible` (le nombre de commandes **après** la date de prédiction : c'est la fuite d'information étudiée au volume III, section 1.1, qui rendrait un modèle impossible à utiliser en production, puisque cette information n'existe pas encore au moment de prédire). Les quatre colonnes manquantes (`appareil`, `panier_moyen`, `satisfaction_moy`, `delai_livraison_moy`) comptent de 1 434 à 1 829 valeurs absentes : un service de production doit savoir les traiter.

## Les exports sales : `sources/`

Le chapitre 5 apprend à **fabriquer un jeu propre à partir de sources qui ne le sont pas**. Nous fournissons donc, dans `donnees/sources/`, trois exports « bruts » (les commandes, le fichier client d'un CRM, et les produits vus par le catalogue interne et par un fournisseur) et deux fichiers de **vérité** qui permettent d'évaluer une réconciliation. Les défauts sont **programmés**, pour qu'on puisse vérifier qu'on les a tous trouvés :

| Fichier | Lignes | Défauts programmés |
|---|---|---|
| `commandes_export.csv` | 19 700 | doublons, trois formats de date, prix avec virgule décimale, quantités manquantes ou négatives, clients inconnus |
| `clients_crm.csv` | 5 000 | une même personne saisie plusieurs fois (courriel en majuscules, ville mal écrite) |
| `produits_catalogue.csv` | 48 | produits de référence, avec leur identifiant interne |
| `produits_fournisseur.csv` | 40 | les mêmes produits, avec une autre référence et un autre libellé |
| `verite_clients.csv`, `verite_produits.csv` | 5 000 ; 40 | la correspondance exacte, **à ne consulter que pour évaluer** |

```python hide
cmd, crm = sources["commandes_export"], sources["clients_crm"]
print("commandes : lignes", len(cmd), "; identifiants distincts", cmd["id_commande"].nunique(), "; doublons exacts de ligne", int(cmd.duplicated().sum()))
print("commandes : quantités manquantes", int(cmd["quantite"].isna().sum()), "; négatives", int((cmd["quantite"] < 0).sum()), "; clients inconnus (999999)", int((cmd["id_client"] == 999999).sum()))
print("commandes : prix avec virgule", int(cmd["prix_unitaire"].astype(str).str.contains(",").sum()), "; dates au format jj/mm/aaaa", int(cmd["date"].str.contains("/").sum()), "; format mm-jj-aaaa", int(cmd["date"].str.match(r"^\d\d-\d\d-\d{4}$").sum()))
print("crm : lignes", len(crm), "; courriels distincts (casse ignorée)", crm["email"].str.lower().nunique(), "; villes distinctes écrites", crm["ville"].nunique(), "; villes distinctes normalisées", crm["ville"].str.strip().str.capitalize().nunique())
print("verite_clients : personnes distinctes", sources["verite_clients"]["id_vrai"].nunique())
print("catalogue :", len(sources["produits_catalogue"]), "produits ; fournisseur :", len(sources["produits_fournisseur"]), "; fournisseur sans correspondance dans la vérité :", int((~sources["produits_fournisseur"]["ref_fournisseur"].isin(sources["verite_produits"]["ref_fournisseur"])).sum()))
print("exemples fournisseur :", sources["produits_fournisseur"]["designation"].head(4).tolist())
print("exemples catalogue :", sources["produits_catalogue"]["libelle"].head(4).tolist())
```
<!--sortie-->
```text
commandes : lignes 19700 ; identifiants distincts 18000 ; doublons exacts de ligne 1524
commandes : quantités manquantes 286 ; négatives 226 ; clients inconnus (999999) 359
commandes : prix avec virgule 5824 ; dates au format jj/mm/aaaa 5897 ; format mm-jj-aaaa 2017
crm : lignes 5000 ; courriels distincts (casse ignorée) 4200 ; villes distinctes écrites 36 ; villes distinctes normalisées 12
verite_clients : personnes distinctes 4200
catalogue : 48 produits ; fournisseur : 40 ; fournisseur sans correspondance dans la vérité : 0
exemples fournisseur : ['Plat  coton (lot)', 'Verre plat', 'Plat  céramique (lot)', 'Céramique bol']
exemples catalogue : ['Plat en coton', 'Plat en verre', 'Plat en céramique', 'Bol en céramique']
```

Concrètement : sur 19 700 lignes de commandes, il n'y a que 18 000 identifiants distincts (1 700 lignes en trop), dont 1 524 lignes strictement identiques à une autre ; 286 quantités manquent et 226 sont négatives ; 359 commandes portent sur un client inconnu ; 5 824 prix s'écrivent avec une virgule ; 5 897 dates sont au format `jj/mm/aaaa` et 2 017 au format `mm-jj-aaaa`. Dans le CRM, 5 000 lignes décrivent en réalité 4 200 personnes ; la même ville s'y écrit de 36 façons, qui se réduisent à 12 une fois la casse et les espaces normalisés. Et le fournisseur ne connaît que 40 des 48 produits du catalogue, avec des libellés qui n'ont pas la même forme (« Céramique bol » pour « Bol en céramique »).

## Un grand volume de transactions : `gros_volume`

Le chapitre 3 a besoin de données qui **ne tiennent pas confortablement** dans une session pandas. Plutôt que de stocker des centaines de mégaoctets dans le dépôt, le script fournit une fonction, `donnees4.gros_volume(n)`, qui **écrit à la demande** `n` transactions (client, produit, magasin, canal, montant, date) en plusieurs fichiers au format **Parquet**, avec une graine fixe : les mêmes chiffres à chaque exécution, et rien de volumineux dans le dépôt. Pour 5 millions de lignes :

```python hide
import pyarrow.parquet as pq
d = tempfile.mkdtemp(prefix="gv_", dir=os.environ.get("TMPDIR"))
donnees4.gros_volume(5_000_000, fichiers=8, dossier=d)
fichiers = sorted(os.listdir(d))
taille = sum(os.path.getsize(os.path.join(d, f)) for f in fichiers)
sch = pq.read_schema(os.path.join(d, fichiers[0]))
print("fichiers :", len(fichiers), "; lignes par fichier :", pq.read_metadata(os.path.join(d, fichiers[0])).num_rows, "; total :", sum(pq.read_metadata(os.path.join(d, f)).num_rows for f in fichiers))
print("taille totale sur disque (Mo) :", round(taille / 1e6))
print("schéma :", [(n, str(t)) for n, t in zip(sch.names, sch.types)])
tab = pq.read_table(os.path.join(d, fichiers[0])).to_pandas()
print("mémoire d'un fichier chargé dans pandas (Mo) :", round(tab.memory_usage(deep=True).sum() / 1e6))
shutil.rmtree(d)
```
<!--sortie-->
```text
fichiers : 8 ; lignes par fichier : 625000 ; total : 5000000
taille totale sur disque (Mo) : 71
schéma : [('id_transaction', 'int64'), ('date', 'timestamp[ms]'), ('id_client', 'int64'), ('id_produit', 'int32'), ('magasin', 'string'), ('canal', 'string'), ('montant', 'double')]
mémoire d'un fichier chargé dans pandas (Mo) : 41
```

Les 5 millions de lignes se répartissent en 8 fichiers de 625 000 lignes et occupent 71 Mo sur disque (le Parquet est un format colonnaire compressé) ; un seul de ces fichiers, chargé dans pandas, occupe déjà 41 Mo en mémoire. Les chiffres du chapitre 3 sont modestes à l'échelle d'une entreprise réelle : ils suffisent à montrer les mécanismes, pas à reproduire les difficultés d'un cluster.

## Les modèles pré-entraînés

Trois exemples de ce volume utilisent des modèles **déjà entraînés** par d'autres. Ils sont téléchargés **une seule fois**, avec une **révision figée**, par le script `build/telecharger_modeles.py`, dans un dossier `modeles/` qui n'est pas versionné ; ensuite, le livre s'exécute **hors ligne**.

| Modèle | Rôle | Paramètres | Disque | Licence | Chapitre |
|---|---|---|---|---|---|
| `paraphrase-multilingual-MiniLM-L12-v2` | plongements de phrases (vecteurs de dimension 384), langues multiples dont le français | 117,7 M | 500 Mo | Apache-2.0 | 2 |
| `SmolLM2-135M-Instruct` | petit modèle de langage conversationnel (anglais) | 134,5 M | 272 Mo | Apache-2.0 | 2 |
| ResNet-18 (poids ImageNet) | reconnaissance d'images, pour l'apprentissage par transfert | 11,7 M | 47 Mo | code BSD-3 ; poids entraînés sur ImageNet (conditions d'usage à vérifier pour un emploi commercial) | 1 (facultatif) |

```python hide
import torch
torch.manual_seed(0)
torch.set_num_threads(2)
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM
import torchvision

def taille_cache(depot):
    rep = os.path.join(os.environ["HF_HOME"], "hub", "models--" + depot.replace("/", "--"), "snapshots")
    tot = 0
    for racine, _, fs in os.walk(rep):
        for f in fs:
            tot += os.path.getsize(os.path.realpath(os.path.join(racine, f)))
    return tot

print("variables hors ligne :", {k: os.environ.get(k) is not None for k in ["HF_HOME", "TORCH_HOME", "HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE"]}, os.environ.get("HF_HUB_OFFLINE"), os.environ.get("TRANSFORMERS_OFFLINE"))
mini = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
st = SentenceTransformer(mini, device="cpu")
print("MiniLM : paramètres (M)", round(sum(p.numel() for p in st.parameters()) / 1e6, 1), "; dimension", st.get_sentence_embedding_dimension(), "; disque (Mo)", round(taille_cache(mini) / 1e6))
smol = "HuggingFaceTB/SmolLM2-135M-Instruct"
tok = AutoTokenizer.from_pretrained(smol)
lm = AutoModelForCausalLM.from_pretrained(smol, dtype=torch.float32).eval()
print("SmolLM2 : paramètres (M)", round(sum(p.numel() for p in lm.parameters()) / 1e6, 1), "; vocabulaire", len(tok), "; disque (Mo)", round(taille_cache(smol) / 1e6))
rn = torchvision.models.resnet18(weights=torchvision.models.ResNet18_Weights.IMAGENET1K_V1)
fich = os.path.join(os.environ["TORCH_HOME"], "hub", "checkpoints")
print("ResNet-18 : paramètres (M)", round(sum(p.numel() for p in rn.parameters()) / 1e6, 1), "; disque (Mo)", round(sum(os.path.getsize(os.path.join(fich, f)) for f in os.listdir(fich)) / 1e6))
print("phrase de test :", len(tok("La livraison a été très rapide.").input_ids), "jetons")
```
<!--sortie-->
```text
variables hors ligne : {'HF_HOME': True, 'TORCH_HOME': True, 'HF_HUB_OFFLINE': True, 'TRANSFORMERS_OFFLINE': True} 1 1
MiniLM : paramètres (M) 117.7 ; dimension 384 ; disque (Mo) 500
SmolLM2 : paramètres (M) 134.5 ; vocabulaire 49152 ; disque (Mo) 272
ResNet-18 : paramètres (M) 11.7 ; disque (Mo) 47
phrase de test : 13 jetons
```

> ⚠️ **Pourquoi des modèles si petits, et ce que cela change.** Les modèles de langage « de pointe » ont des centaines de milliards de paramètres et ne tournent pas sur un ordinateur ordinaire. Le seul modèle de langage génératif que nous pouvons exécuter ici, SmolLM2, en a 134,5 millions, soit des milliers de fois moins que les plus grands, et il a été entraîné pour l'**anglais** : il répond souvent en anglais à une consigne en français, et ses réponses sont approximatives. Nous l'utilisons pour montrer des **mécanismes** (découpage en jetons, génération pas à pas, effet des réglages), jamais pour juger de ce que savent faire les grands modèles. Une phrase comme « La livraison a été très rapide. » se découpe en 13 jetons avec son vocabulaire de 49 152 entrées.

L'exécution hors ligne est imposée par quatre variables d'environnement (`HF_HOME` et `TORCH_HOME` pour l'emplacement des modèles, `HF_HUB_OFFLINE=1` et `TRANSFORMERS_OFFLINE=1` pour interdire tout accès au réseau) que le `Makefile` du volume pose pour vous : si un modèle manque, le programme s'arrête avec une erreur claire au lieu de le télécharger en silence.

## L'environnement de travail

Ce volume utilise les outils des volumes précédents, plus quelques outils lourds. Voici les commandes d'installation (non exécutées ici : elles installent des paquets et des programmes sur *votre* machine). La version **CPU** de PyTorch est choisie exprès : la version par défaut de PyPI tire plusieurs gigaoctets de bibliothèques pour cartes graphiques, inutiles ici. Les paquets numériques de base sont **figés** aux versions qui ont produit les sorties du livre.

```bash noexec
python -m venv .venv && source .venv/bin/activate
pip install numpy==2.5.3 pandas==3.0.6 scipy scikit-learn==1.9.1 matplotlib
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple
pip install transformers sentence-transformers pyspark duckdb pyarrow fastapi uvicorn httpx mlflow streamlit
pip install onnx onnxruntime beautifulsoup4 requests rapidfuzz pytesseract
sudo apt-get install default-jre-headless tesseract-ocr tesseract-ocr-fra    # Java pour Spark, OCR avec le français
python build/telecharger_modeles.py     # une fois : environ 780 Mo ; ensuite, tout s'exécute hors ligne
```

```python hide
import platform
from importlib.metadata import version
print("Python        :", platform.python_version())
for nom in ["numpy", "pandas", "scikit-learn", "torch", "torchvision", "transformers", "sentence-transformers", "pyspark", "duckdb", "pyarrow",
            "fastapi", "mlflow", "streamlit", "onnxruntime", "beautifulsoup4", "rapidfuzz", "pytesseract"]:
    print(f"{nom:22s}:", version(nom))
```
<!--sortie-->
```text
Python        : 3.13.3
numpy                 : 2.5.3
pandas                : 3.0.6
scikit-learn          : 1.9.1
torch                 : 2.14.1+cpu
torchvision           : 0.29.1+cpu
transformers          : 5.18.0
sentence-transformers : 6.1.0
pyspark               : 4.2.0
duckdb                : 1.5.6
pyarrow               : 25.0.1
fastapi               : 0.142.2
mlflow                : 3.16.1
streamlit             : 1.65.0
onnxruntime           : 1.30.0
beautifulsoup4        : 4.15.0
rapidfuzz             : 3.14.6
pytesseract           : 0.3.13
```

| Bibliothèque | Version utilisée | Pour quoi faire | Chapitres |
|---|---|---|---|
| `torch`, `torchvision` | 2.14.1 (CPU), 0.29.1 | réseaux de neurones, dérivation automatique | 1, 2 |
| `transformers` | 5.18.0 | modèles de langage, découpage en jetons | 2 |
| `sentence-transformers` | 6.1.0 | plongements de phrases | 2 |
| `pyspark` (+ Java) | 4.2.0 | calcul distribué, en mode local | 3 |
| `duckdb`, `pyarrow` | 1.5.6, 25.0.1 | requêtes SQL sur fichiers, format Parquet | 3, 5 |
| `fastapi` | 0.142.2 | mise à disposition d'un modèle par une API | 4 |
| `mlflow` | 3.16.1 | suivi d'expériences | 4 (facultatif) |
| `onnxruntime` | 1.30.0 | exécuter un modèle exporté | 4 |
| `rapidfuzz`, `beautifulsoup4` (et `requests`) | 3.14.6, 4.15.0 | réconciliation, collecte de données | 5 |
| `streamlit` | 1.65.0 | applications de démonstration | 7 (facultatif) |
| `pytesseract` (+ Tesseract) | 0.3.13 | reconnaissance de caractères (OCR) | 1 (facultatif) |
| `scikit-learn`, `pandas`, `numpy` | 1.9.1, 3.0.6, 2.5.3 | les bases des volumes précédents | tous |

Python 3.13 a produit les sorties de ce livre.

> 🧭 **Ce qui ne tourne pas ici.** Certains outils du volume ne peuvent pas s'exécuter dans l'environnement qui a servi à écrire le livre : **Docker** et **Kubernetes** (pas de conteneurs), **Airflow**, **Prefect** et **dbt** (serveurs et orchestrateurs lourds), **DVC**, **Kafka** et **Hadoop** (services à installer), **TensorFlow/Keras**, et les **plateformes cloud** (AWS, Azure, GCP : pas de compte). Leur code est montré dans des blocs marqués *non exécuté* ; chaque fois que c'est possible, nous l'accompagnons d'un **équivalent minimal exécutable** (un mini-orchestrateur en Python, un mini-MapReduce, un serveur HTTP local) qui montre la même idée.

> ⚠️ **Les résultats d'un réseau de neurones varient légèrement.** L'entraînement d'un réseau repose sur des initialisations aléatoires et sur des calculs parallèles dont l'ordre peut changer d'une version de bibliothèque à l'autre. Nous fixons toujours les graines, mais votre dernière décimale peut différer de celle du livre ; une conclusion qui changerait avec une version ne serait pas une conclusion. Nous ne citons jamais de durée en secondes : elles dépendent de la machine.

> 🧭 **Prêt ?** Au chapitre 1, nous commençons par les réseaux de neurones : une idée simple (composer des fonctions et corriger leurs erreurs par la règle de la chaîne), qui devient puissante parce qu'on peut la répéter des millions de fois.
