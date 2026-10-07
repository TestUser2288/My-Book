# Carte du volume, données et environnement

Cette section ouvre le volume par trois choses : la **carte des chapitres**, le **catalogue des jeux de données** (avec, pour chacun, ce qu'il contient et ce qu'on y a « programmé »), et l'**environnement** nécessaire pour refaire tous les calculs.

## Carte du volume

Chaque chapitre répond à l'une des questions de la gérante, ou à une question que l'on se pose en chemin. Les chapitres sont lisibles dans l'ordre, mais on peut les prendre séparément ; les sections marquées ➕ sont facultatives.

| Chapitre | Question posée | Contenu |
|---|---|---|
| **1. Les essentiels de la statistique** | Comment résumer 36 000 commandes ? Peut-on croire un échantillon ? Ce lien est-il une cause ? | statistique descriptive, distributions et courbe normale, échantillonnage, corrélation et causalité ; ➕ pourcentages, taux de croissance, moyennes pondérées |
| **2. Excel** | Comment construire un suivi des ventes que d'autres comprennent ? | formules et fonctions, tableaux croisés dynamiques, Power Query, bonnes pratiques ; ➕ Power Pivot et DAX, macros, Google Sheets et Looker Studio |
| **3. SQL** | Comment interroger la base de la boutique ? | `SELECT`, jointures, fonctions fenêtres, requêtes structurées (CTE) ; ➕ optimisation, différences entre moteurs |
| **4. Python et R pour l'analyse** | Comment automatiser et reproduire un calcul ? | pandas, tidyverse, lecture et restructuration, notebooks ; ➕ ggplot2 et Shiny, NumPy, polars |
| **5. Types de données, collecte et enquêtes** | D'où viennent les données, et comment en produire de fiables ? | types et niveaux de mesure, sources, conception d'enquêtes ; ➕ questionnaires, plans de sondage, API et web scraping |
| **Projet du volume (cahier)** | Une première analyse de bout en bout | du fichier brut au tableau de synthèse, par trois outils |

## Les jeux de données du volume

Tout est **simulé**, avec des graines fixes, par le script `build/donnees_a1.py`. Chaque jeu suit un mécanisme que le script décrit en tête de fichier : c'est la **vérité programmée**. Nous la révélerons dans les chapitres où elle est instructive, et le cahier permet de la retrouver. Aucune donnée ne vient d'une entreprise réelle.

Chargeons les sept tables principales et regardons leur forme.

```python hide-code
import os, sqlite3
import numpy as np
import pandas as pd

def lire(nom, **kw):
    return pd.read_csv(f"donnees/{nom}.csv", **kw)

noms = ["clients", "produits", "commandes", "lignes_commande", "retours", "jours_exploitation", "enquete_satisfaction"]
D = {n: lire(n) for n in noms}
for n in noms:
    t = D[n]
    print(f"{n:22s} {t.shape[0]:6d} lignes {t.shape[1]:3d} colonnes {int(t.isna().sum().sum()):6d} manquants")
cli, prod, cmd, lig, ret, jour, enq = (D[n] for n in noms)
```
<!--sortie-->
```text
clients                  6000 lignes   8 colonnes      0 manquants
produits                  120 lignes   7 colonnes      0 manquants
commandes               36395 lignes   7 colonnes  30652 manquants
lignes_commande         83905 lignes   7 colonnes      0 manquants
retours                  5002 lignes   5 colonnes      0 manquants
jours_exploitation       1096 lignes   8 colonnes      0 manquants
enquete_satisfaction      958 lignes  12 colonnes   1295 manquants
```

Les valeurs manquantes sont **voulues** : un code promo absent signifie « pas de promotion » (30 652 commandes sur 36 395), et l'enquête a des questions sans réponse (le conseil ne concerne que la boutique, certains clients restent anonymes, beaucoup ne laissent pas de commentaire).

| Jeu | Contenu | Nature | Chapitres |
|---|---|---|---|
| `clients.csv` | 6 000 clients : ville, canal d'acquisition, carte de fidélité | simulé | tous |
| `produits.csv` | 120 produits : catégorie, prix de vente, coût d'achat, fournisseur | simulé | 1 à 4 |
| `commandes.csv` | 36 395 commandes (2023-2025) : date, heure, client, canal, livraison, code promo | simulé | 1 à 4 |
| `lignes_commande.csv` | 83 905 lignes : produit, quantité, prix unitaire, remise, montant | simulé | 1 à 4 |
| `retours.csv` | 5 002 retours : ligne, date, motif, montant remboursé | simulé | 3, 4, projet |
| `jours_exploitation.csv` | 1 096 jours : commandes, chiffre d'affaires, météo, promotion, publicité | simulé | 1, 2, 4 |
| `enquete_satisfaction.csv` | 958 réponses d'une enquête de satisfaction | simulé | 1, 5, projet |
| `ventes_2025.xlsx` | classeur Excel de 2025 : feuilles `Lignes`, `Produits`, `Clients` | simulé | 2 |
| `export_caisse_brut.csv` | export de caisse désordonné (une semaine, boutique) | simulé | 2, 4, projet |
| `boutique.db` | base SQLite contenant les six premières tables | simulé | 3, 4 |

### Les clients et les produits

La table `clients` décrit les 6 000 clients de la boutique ; la table `produits` décrit le catalogue.

| Colonne | Signification |
|---|---|
| `id_client` | identifiant unique du client |
| `date_inscription` | date d'inscription (de 2018 à 2025) |
| `annee_naissance` | année de naissance |
| `ville` | une des 20 villes (« Ville A » à « Ville T ») |
| `canal_acquisition` | canal par lequel le client est arrivé : `Boutique`, `Site`, `Réseaux` |
| `fidelite` | 1 si le client a la carte de fidélité |
| `email_valide`, `consentement_marketing` | 1 si l'adresse est valide ; 1 si le client accepte les messages commerciaux |

| Colonne | Signification |
|---|---|
| `id_produit`, `nom_produit` | identifiant et nom (« Bougie classique », « Plaid nordique »…) |
| `categorie` | `Cuisine`, `Maison`, `Décoration`, `Papeterie`, `Jardin`, `Bien-être` (20 produits chacune) |
| `prix_vente`, `cout_achat` | prix de vente TTC et coût d'achat, en € |
| `fournisseur` | un des huit fournisseurs (« Fournisseur A » à « Fournisseur H ») |
| `date_lancement` | date de mise au catalogue |

```python hide-code
cli["date_inscription"] = pd.to_datetime(cli["date_inscription"])
print("clients : inscrits avant 2023 :", int((cli["date_inscription"] < "2023-01-01").sum()), "| depuis :", int((cli["date_inscription"] >= "2023-01-01").sum()))
print("  âge moyen en 2025 :", round(float((2025 - cli["annee_naissance"]).mean()), 1), "| ville la plus fréquente :", cli["ville"].value_counts().index[0], round(float(cli["ville"].value_counts(normalize=True).iloc[0]), 3))
print("  canal d'acquisition :", cli["canal_acquisition"].value_counts(normalize=True).round(3).to_dict())
print("  carte de fidélité :", round(float(cli["fidelite"].mean()), 3), "| email valide :", round(float(cli["email_valide"].mean()), 3), "| consentement :", round(float(cli["consentement_marketing"].mean()), 3))
marge = 1 - prod["cout_achat"] / prod["prix_vente"]
print("produits : prix de", prod["prix_vente"].min(), "à", prod["prix_vente"].max(), "€ | marge moyenne", round(float(marge.mean()), 3), "| de", round(float(marge.min()), 3), "à", round(float(marge.max()), 3))
print("  prix moyen par catégorie :", prod.groupby("categorie")["prix_vente"].mean().round(1).to_dict())
```
<!--sortie-->
```text
clients : inscrits avant 2023 : 4000 | depuis : 2000
  âge moyen en 2025 : 43.3 | ville la plus fréquente : Ville A 0.144
  canal d'acquisition : {'Boutique': 0.493, 'Site': 0.388, 'Réseaux': 0.119}
  carte de fidélité : 0.351 | email valide : 0.921 | consentement : 0.605
produits : prix de 2.9 à 152.9 € | marge moyenne 0.478 | de 0.352 à 0.6
  prix moyen par catégorie : {'Bien-être': 27.5, 'Cuisine': 34.8, 'Décoration': 38.0, 'Jardin': 51.8, 'Maison': 51.8, 'Papeterie': 11.4}
```

Les deux tiers des clients (4 000 sur 6 000) étaient déjà inscrits au 1er janvier 2023 ; les 2 000 autres se sont inscrits pendant la période. L'âge moyen est d'environ 43 ans, et la ville la plus fréquente, la Ville A, regroupe 14 % des clients. Près de la moitié (49 %) sont arrivés par la boutique, 39 % par le Site, 12 % par les réseaux. Un client sur trois (35 %) a la carte de fidélité. La marge moyenne des produits est de 48 % du prix de vente (de 35 % à 60 %), et le prix va de 2,90 € à 152,90 € : les catégories `Jardin` et `Maison` contiennent les articles les plus chers (prix moyen de 51,80 € chacune, contre 11,40 € en papeterie).

### Les commandes, les lignes et les retours

Une **commande** est un achat d'un client, à une date et par un canal ; elle contient une ou plusieurs **lignes** (une ligne = un produit en une certaine quantité) ; une ligne peut donner lieu à un **retour**.

| Table | Colonnes principales |
|---|---|
| `commandes` | `id_commande`, `date_commande` (jj, texte `aaaa-mm-jj`), `heure`, `id_client`, `canal`, `mode_livraison` (`Domicile`, `Point relais`, `Retrait magasin`), `code_promo` (`SOLDES`, `BIENVENUE`, `FIDELITE`, ou vide) |
| `lignes_commande` | `id_ligne`, `id_commande`, `id_produit`, `quantite`, `prix_unitaire` (€), `remise_pct` (0, 5, 10 ou 20), `montant` = quantité × prix unitaire × (1 − remise) |
| `retours` | `id_retour`, `id_ligne`, `date_retour`, `motif`, `montant_rembourse` |

```python hide-code
cmd["annee"] = pd.to_datetime(cmd["date_commande"]).dt.year
n_l = lig.groupby("id_commande").size()
print("commandes du", cmd["date_commande"].min(), "au", cmd["date_commande"].max())
print("  par canal :", cmd["canal"].value_counts().to_dict())
print("  par livraison :", cmd["mode_livraison"].value_counts().to_dict())
print("  codes promo :", cmd["code_promo"].fillna("(aucun)").value_counts().to_dict())
print("lignes par commande : moyenne", round(float(n_l.mean()), 2), "| maximum", int(n_l.max()), "| quantités :", lig["quantite"].value_counts().sort_index().to_dict())
print("  remises :", lig["remise_pct"].value_counts().sort_index().to_dict(), "| part des lignes remisées :", round(float((lig["remise_pct"] > 0).mean()), 3))
lc = lig.merge(cmd[["id_commande", "canal"]], on="id_commande")
rc = ret.merge(lc[["id_ligne", "canal"]], on="id_ligne")
print("retours par canal (part des lignes) :", (rc.groupby("canal").size() / lc.groupby("canal").size()).round(3).to_dict())
print("  motifs :", ret["motif"].value_counts(normalize=True).round(3).to_dict())
print("  remboursé :", round(float(ret["montant_rembourse"].sum()), 2), "| chiffre d'affaires :", round(float(lig["montant"].sum()), 2))
```
<!--sortie-->
```text
commandes du 2023-01-01 au 2025-12-31
  par canal : {'Boutique': 16975, 'Site': 15463, 'Réseaux': 3957}
  par livraison : {'Retrait magasin': 18348, 'Domicile': 10737, 'Point relais': 7310}
  codes promo : {'(aucun)': 30652, 'SOLDES': 3006, 'FIDELITE': 2423, 'BIENVENUE': 314}
lignes par commande : moyenne 2.31 | maximum 8 | quantités : {1: 71218, 2: 9288, 3: 2552, 4: 847}
  remises : {0: 70611, 5: 5603, 10: 751, 20: 6940} | part des lignes remisées : 0.158
retours par canal (part des lignes) : {'Boutique': 0.031, 'Réseaux': 0.067, 'Site': 0.09}
  motifs : {'Mauvais choix': 0.314, "Changement d'avis": 0.303, 'Défaut': 0.182, 'Livraison tardive': 0.121, 'Autre': 0.08}
  remboursé : 221010.01 | chiffre d'affaires : 3653157.28
```

Les commandes s'étalent du 1er janvier 2023 au 31 décembre 2025. Elles sont réparties entre la boutique (16 975), le Site (15 463) et les réseaux (3 957). Un panier compte en moyenne 2,3 lignes (jusqu'à 8), et la quantité vaut presque toujours 1 (85 % des lignes). Les remises existent sur 16 % des lignes. Les **retours** concernent 3,1 % des lignes de la boutique, 6,7 % de celles des réseaux et 9,0 % de celles du Site ; les motifs les plus fréquents sont le « mauvais choix » (31 %) et le « changement d'avis » (30 %), loin devant le défaut du produit (18 %). Le total remboursé (221 010 €) représente un peu plus de 6 % du chiffre d'affaires de trois ans (3 653 157,28 €).

### Les jours d'exploitation

La table `jours_exploitation` résume chaque jour : le nombre de commandes et le chiffre d'affaires **calculés à partir des commandes**, auxquels s'ajoutent des variables extérieures (température et pluie du lieu de la boutique, jour de promotion, dépense publicitaire).

| Colonne | Signification |
|---|---|
| `date`, `jour_semaine` | date et jour (1 = lundi … 7 = dimanche) |
| `nb_commandes`, `chiffre_affaires` | commandes et chiffre d'affaires du jour (€) |
| `temperature_moy`, `pluie_mm` | température moyenne (°C) et pluie (mm) |
| `promo_active` | 1 les jours de soldes ou de « Vendredi noir » (153 jours en tout) |
| `depense_pub` | dépense publicitaire quotidienne moyenne (€) |

```python hide-code
jour["mois"] = jour["date"].str[5:7].astype(int)
print("jours :", len(jour), "| jours de promotion :", int(jour["promo_active"].sum()), "| jours de pluie (> 1 mm) :", int((jour["pluie_mm"] > 1).sum()))
print("  température moyenne :", round(float(jour["temperature_moy"].mean()), 1), "| dépense publicitaire moyenne :", round(float(jour["depense_pub"].mean()), 1))
print("  CA moyen par mois :", jour.groupby("mois")["chiffre_affaires"].mean().round(0).astype(int).to_dict())
print("  CA moyen par jour de semaine :", jour.groupby("jour_semaine")["chiffre_affaires"].mean().round(0).astype(int).to_dict())
print("  corrélation CA / dépense publicitaire :", round(float(jour["chiffre_affaires"].corr(jour["depense_pub"])), 2), "| CA / jour de promotion :", round(float(jour["chiffre_affaires"].corr(jour["promo_active"])), 2))
print("  somme des commandes :", int(jour["nb_commandes"].sum()), "| somme du CA :", round(float(jour["chiffre_affaires"].sum()), 2))
```
<!--sortie-->
```text
jours : 1096 | jours de promotion : 153 | jours de pluie (> 1 mm) : 290
  température moyenne : 13.1 | dépense publicitaire moyenne : 208.1
  CA moyen par mois : {1: 2488, 2: 2345, 3: 2747, 4: 3031, 5: 3378, 6: 3355, 7: 3171, 8: 2689, 9: 3477, 10: 3488, 11: 4418, 12: 5357}
  CA moyen par jour de semaine : {1: 3241, 2: 2941, 3: 3102, 4: 3317, 5: 3917, 6: 4634, 7: 2192}
  corrélation CA / dépense publicitaire : 0.42 | CA / jour de promotion : -0.01
  somme des commandes : 36395 | somme du CA : 3653157.28
```

Le chiffre d'affaires moyen d'un jour passe de 2 488 € en janvier à 5 357 € en décembre : la **saisonnalité** est forte. Le samedi est le meilleur jour (4 634 € en moyenne) et le dimanche le plus faible (2 192 €). Les sommes de cette table redonnent exactement celles des commandes (36 395 commandes, 3 653 157,28 €), ce qui est un bon contrôle. La corrélation de 0,42 entre le chiffre d'affaires et la dépense publicitaire est un piège que le chapitre 1 (section 1.4) démontera.

### L'enquête de satisfaction

L'enquête a été envoyée en fin d'année 2025 aux clients qui avaient commandé dans l'année : 3 875 invitations et 958 réponses (soit 24,7 %). Chaque ligne est une réponse.

| Colonne | Signification |
|---|---|
| `id_reponse`, `date_reponse` | identifiant et date de la réponse |
| `id_client` | client (vide pour une réponse **anonyme**) |
| `canal`, `tranche_age` | canal de la dernière commande ; tranche d'âge du répondant |
| `satisfaction_globale`, `satisfaction_livraison`, `satisfaction_prix` | notes de 1 à 5 |
| `satisfaction_conseil` | note de 1 à 5 (vide hors boutique : on ne conseille pas en ligne) |
| `recommandation_0_10` | « recommanderiez-vous la boutique ? » de 0 à 10 |
| `commentaire`, `duree_reponse_s` | commentaire libre (souvent vide) ; durée de réponse en secondes |

```python hide-code
print("réponses :", len(enq), "| invitations (clients ayant commandé en 2025) :", int(cmd.loc[cmd["annee"] == 2025, "id_client"].nunique()))
print("  anonymes :", round(float(enq["id_client"].isna().mean()), 3), "| doublons exacts :", int(enq.duplicated(subset=[c for c in enq.columns if c != "id_reponse"]).sum()), "| commentaires vides :", int(enq["commentaire"].isna().sum()))
print("  satisfaction globale :", enq["satisfaction_globale"].value_counts().sort_index().to_dict(), "| moyenne :", round(float(enq["satisfaction_globale"].mean()), 2), "| notes 4 ou 5 :", round(float((enq["satisfaction_globale"] >= 4).mean()), 3))
sl = (enq["satisfaction_globale"] == 5) & (enq["satisfaction_livraison"] == 5) & (enq["satisfaction_prix"] == 5) & (enq["duree_reponse_s"] < 20)
print("  réponses 5-5-5 en moins de 20 s :", int(sl.sum()), "| durée médiane :", float(enq["duree_reponse_s"].median()), "s")
inv = cmd[cmd["annee"] == 2025].drop_duplicates("id_client", keep="last").merge(cli[["id_client", "fidelite"]], on="id_client")
inv["repondu"] = inv["id_client"].isin(enq["id_client"].dropna().astype(int))
print("  taux de réponse selon la carte de fidélité :", inv.groupby("fidelite")["repondu"].mean().round(3).to_dict())
inv["recent"] = pd.to_datetime(inv["date_commande"]) >= "2025-10-01"
print("  taux de réponse selon que la dernière commande date d'octobre-décembre :", inv.groupby("recent")["repondu"].mean().round(3).to_dict())
```
<!--sortie-->
```text
réponses : 958 | invitations (clients ayant commandé en 2025) : 3875
  anonymes : 0.204 | doublons exacts : 27 | commentaires vides : 538
  satisfaction globale : {1: 27, 2: 136, 3: 266, 4: 256, 5: 273} | moyenne : 3.64 | notes 4 ou 5 : 0.552
  réponses 5-5-5 en moins de 20 s : 35 | durée médiane : 70.0 s
  taux de réponse selon la carte de fidélité : {0: 0.179, 1: 0.214}
  taux de réponse selon que la dernière commande date d'octobre-décembre : {False: 0.167, True: 0.205}
```

Les trois quarts des clients ne répondent pas, et ceux qui répondent **ne ressemblent pas** à ceux qui ne répondent pas : les clients avec carte répondent davantage (21 % contre 18 %), de même que ceux dont la dernière commande est récente (21 % contre 17 %). Le fichier contient aussi des **doublons** (27 réponses identiques en tout), des réponses « 5-5-5 » remplies en quelques secondes, et un cinquième de réponses anonymes. Ces défauts sont **programmés** : ils servent à apprendre à se méfier d'une enquête (sections 1.3 et 5.3).

### Les fichiers « de bureau » : un classeur et un export de caisse

Deux fichiers imitent ce que l'on reçoit dans la vraie vie.

- **`ventes_2025.xlsx`** est un classeur Excel de l'année 2025 avec trois feuilles : `Lignes` (une ligne de commande par ligne du tableau, avec la date, le client, le canal, le produit, la catégorie, la quantité, le prix, la remise et le montant), `Produits` (le catalogue) et `Clients`. Il sert de base au chapitre 2.
- **`export_caisse_brut.csv`** est un export de la caisse de la boutique pour la semaine du 3 au 9 novembre 2025, **volontairement désordonné** : deux lignes de titre, séparateur point-virgule, virgule décimale, dates `jj/mm/aaaa`, encodage Windows (`cp1252`), un en-tête répété à chaque « page », quelques montants absents, des majuscules incohérentes et une ligne de total en bas. Il servira à apprendre à lire un fichier tel qu'il arrive (chapitres 2 et 4, puis le projet).

```python hide-code
xl = pd.read_excel("donnees/ventes_2025.xlsx", sheet_name=None)
print("ventes_2025.xlsx :", {k: v.shape for k, v in xl.items()}, "| somme des montants :", round(float(xl["Lignes"]["montant"].sum()), 2))
lignes_export = open("donnees/export_caisse_brut.csv", "rb").read().decode("cp1252").splitlines()
print("export brut :", len(lignes_export), "lignes |", sum(1 for x in lignes_export if x.startswith("N° ticket")), "en-têtes | montants vides :", sum(1 for x in lignes_export[4:] if x.endswith(";")))
```
<!--sortie-->
```text
ventes_2025.xlsx : {'Lignes': (29827, 13), 'Produits': (120, 6), 'Clients': (6000, 5)} | somme des montants : 1324763.72
export brut : 289 lignes | 5 en-têtes | montants vides : 8
```

Le classeur compte 29 827 lignes de commande pour l'année 2025 et un montant total de 1 324 763,72 €, qui est celui que nous avons obtenu en introduction par deux autres chemins. L'export contient 289 lignes dont 5 en-têtes (le premier et quatre répétés) et 8 montants absents.

### La base de données `boutique.db`

Les six premières tables existent aussi dans une **base de données** SQLite, un fichier unique que l'on interroge en SQL (chapitre 3). Les tables sont reliées par des identifiants : c'est le **schéma** de la base.

```python hide
import sys
sys.path.insert(0, "build")
import style
style.setup()
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

tables = {
    "clients": (0.2, 2.9, ["id_client", "ville", "canal_acquisition", "fidelite", "…"]),
    "commandes": (3.6, 2.9, ["id_commande", "date_commande", "id_client", "canal", "code_promo", "…"]),
    "lignes_commande": (7.1, 2.9, ["id_ligne", "id_commande", "id_produit", "quantite", "montant", "…"]),
    "produits": (7.1, 0.2, ["id_produit", "categorie", "prix_vente", "cout_achat", "…"]),
    "retours": (3.6, 0.2, ["id_retour", "id_ligne", "motif", "montant_rembourse", "…"]),
    "jours_exploitation": (0.2, 0.2, ["date", "nb_commandes", "chiffre_affaires", "…"]),
}
couleurs = {"clients": style.BLEU, "commandes": style.ORANGE, "lignes_commande": style.ORANGE, "produits": style.AQUA, "retours": style.ROUGE, "jours_exploitation": style.MUET}
fig, ax = plt.subplots(figsize=(9.4, 4.6))
ax.set_xlim(0, 10.0); ax.set_ylim(0, 4.6); ax.axis("off")
W, H = 2.7, 1.55
for nom, (x, y, cols) in tables.items():
    ax.add_patch(FancyBboxPatch((x, y), W, H, boxstyle="round,pad=0.02,rounding_size=0.08", fc="white", ec=couleurs[nom], lw=1.8))
    ax.add_patch(FancyBboxPatch((x, y + H - 0.38), W, 0.38, boxstyle="round,pad=0.02,rounding_size=0.08", fc=couleurs[nom], ec=couleurs[nom]))
    ax.text(x + W / 2, y + H - 0.19, nom, ha="center", va="center", color="white", fontsize=9.5, weight="bold")
    for k, c in enumerate(cols):
        ax.text(x + 0.12, y + H - 0.62 - 0.18 * k, c, fontsize=7.6, color=style.ENCRE2, family="DejaVu Sans Mono")
def lien(a, b, rad=0.0):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-", color=style.ENCRE2, lw=1.2, connectionstyle=f"arc3,rad={rad}"))

def etiquette(x, y, t, ha="center"):
    ax.text(x, y, t, ha=ha, fontsize=8, color=style.ENCRE2, weight="bold")

lien((2.9, 3.7), (3.6, 3.7)); etiquette(3.25, 3.85, "1—n")
lien((6.3, 3.7), (7.1, 3.7)); etiquette(6.7, 3.85, "1—n")
lien((8.45, 2.9), (8.45, 1.75)); etiquette(8.7, 2.3, "n—1", ha="left")
lien((7.6, 2.9), (5.0, 1.75)); etiquette(6.0, 2.55, "1—0..1")
ax.text(1.55, 2.3, "(résume l'activité de\nchaque date)", ha="center", fontsize=7.6, color=style.MUET, style="italic")
style.save(fig, "ch00-schema-base.png")
```
<!--sortie-->
```text
figure : ch00-schema-base.png
```

![Schéma de la base de la boutique : un client passe plusieurs commandes, chaque commande contient plusieurs lignes, chaque ligne désigne un produit et peut donner lieu à un retour ; la table des jours d'exploitation résume l'activité par date. Maquette dessinée avec matplotlib.](figures/ch00-schema-base.png)

Les liens se lisent « un client passe **plusieurs** commandes, une commande contient **plusieurs** lignes, une ligne désigne **un** produit et donne lieu à **zéro ou un** retour ». Ce sont ces identifiants communs (`id_client`, `id_commande`, `id_produit`, `id_ligne`) qui permettent de **joindre** les tables, thème du chapitre 3.

```python hide-code
con = sqlite3.connect("donnees/boutique.db")
print("tables :", [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")])
print("index  :", [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='index' ORDER BY name")])
print("lignes :", {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ["clients", "produits", "commandes", "lignes_commande", "retours", "jours_exploitation"]})
con.close()
```
<!--sortie-->
```text
tables : ['clients', 'commandes', 'jours_exploitation', 'lignes_commande', 'produits', 'retours']
index  : ['idx_cmd_client', 'idx_cmd_date', 'idx_lig_cmd', 'idx_lig_prod']
lignes : {'clients': 6000, 'produits': 120, 'commandes': 36395, 'lignes_commande': 83905, 'retours': 5002, 'jours_exploitation': 1096}
```

Les quatre **index** accélèrent les recherches par client, par date et par commande (section 3.5).

### La vérité programmée

Le script qui fabrique les données y a inscrit des mécanismes connus. Les voici en résumé : nous les retrouverons un par un, et vous verrez que l'analyse les retrouve (ou non, et pourquoi).

| Ce qui est programmé | Ce que l'on observe | Où on le retrouve |
|---|---|---|
| tendance de +6 % par an | 11 418 commandes en 2023, 12 946 en 2025 (+13,4 %) | 1.1, 1.5 |
| saison (creux de janvier-février et d'été, pic de novembre-décembre) | CA moyen par jour de 2 488 € en janvier, 5 357 € en décembre | 1.1, 2.2 |
| jour de la semaine (samedi +40 %, dimanche −35 %) | 4 634 € le samedi, 2 192 € le dimanche | 1.1 |
| part du Site : de 35 % à 48 % en trois ans | 37,4 % en 2023, 46,9 % en 2025 | introduction, 1.5 |
| retours : Site 9 %, réseaux 7 %, boutique 3 % | 9,0 %, 6,7 %, 3,1 % | 3.1, 4.3 |
| dépense publicitaire liée à la saison, avec un vrai effet faible | corrélation de 0,42 avec le chiffre d'affaires | 1.4 |
| promotions : +18 % de commandes les jours de promotion | masqué par la saison et la remise (corrélation brute de −0,01 avec le CA) | 1.4, volume III |
| enquête : biais de réponse, doublons, réponses anonymes, « 5-5-5 » | 24,7 % de réponses, 27 doublons, 20 % d'anonymes | 1.3, 5.3 |

Un exemple de piège : la corrélation brute entre jour de promotion et chiffre d'affaires est **quasi nulle** (−0,01), alors que la promotion augmente bien les commandes de 18 %. Les promotions tombent en hiver et en été, saisons où les ventes sont plus faibles, et la remise réduit le montant de chaque commande : les effets se masquent. C'est exactement le genre de situation dont l'analyste doit se méfier, et nous la retrouverons au chapitre 1 et au volume III.

## L'environnement de travail

### Python, R et SQL

Les calculs du livre sont faits en **Python** (bibliothèques pandas, NumPy, SciPy, matplotlib…), en **R** (tidyverse) et en **SQL** (SQLite et DuckDB). Voici les versions utilisées pour écrire ce volume ; les vôtres peuvent différer, tant que tout s'exécute.

```python hide-code
import platform, subprocess
import importlib.metadata as M
print("python", platform.python_version(), "|", ", ".join(f"{p} {M.version(p)}" for p in ["pandas", "numpy", "scipy", "statsmodels", "matplotlib", "openpyxl", "XlsxWriter", "polars", "duckdb"]))
print("SQLite", sqlite3.sqlite_version)
r = subprocess.run(["Rscript", "-e", "cat(R.version.string)"], capture_output=True, text=True)
print(r.stdout.strip())
```
<!--sortie-->
```text
python 3.13.3 | pandas 3.0.6, numpy 2.5.3, scipy 1.18.1, statsmodels 0.15.0, matplotlib 3.11.2, openpyxl 3.1.5, XlsxWriter 3.2.9, polars 2.0.0, duckdb 1.5.6
SQLite 3.46.1
R version 4.4.3 (2025-02-28)
```

**SQL** : les requêtes du chapitre 3 sont exécutées avec **SQLite** (un moteur léger, sans serveur), qui accepte les jointures, les fonctions fenêtres et les CTE. Les différences avec PostgreSQL, MySQL, SQL Server et Oracle sont décrites à la section 3.6, mais **ces moteurs ne sont pas exécutés** : nous le signalons chaque fois.

### Le tableur : Excel, LibreOffice et nos maquettes

Une précision d'honnêteté. **Excel n'est pas installé** sur la machine qui a produit ce livre, mais **LibreOffice Calc**, un tableur libre qui lit les fichiers Excel, l'est. Les formules du chapitre 2 ont donc été **écrites dans des classeurs, recalculées par LibreOffice et comparées aux résultats de pandas** : chaque résultat cité est calculé, pas recopié. Trois limites à garder en tête :

- les **copies d'écran** sont des **maquettes dessinées** avec matplotlib, pas des captures d'Excel ;
- les noms de menus et de fonctions varient avec la **version** et la **langue** d'Excel : nous écrivons les formules avec les noms français (`SOMME.SI.ENS`), les noms anglais figurant dans un tableau de correspondance ; à vérifier dans votre version ;
- ce qui n'est pas exécutable ici (tableaux croisés dynamiques réels, Power Query, Power Pivot, macros, Google Sheets, Looker Studio) est signalé **« non exécuté »**, avec un équivalent calculé quand c'est possible.

### Régénérer les données et refaire les calculs

Tout le dossier `donnees/` se régénère à l'identique par un script, et les calculs du livre se rejouent par `make check` (qui vérifie que chaque sortie est inchangée).

```bash noexec
python build/donnees_a1.py        # régénère donnees/ (quelques secondes, graines fixes)
make check                        # rejoue tous les blocs de code et signale toute différence
make pdf                          # reconstruit le livre et le cahier en PDF
```

## Conventions du volume

- **Monnaie et villes** : montants en **€** ; villes « Ville A » à « Ville T » ; canaux `Boutique`, `Site`, `Réseaux` (écrits ainsi, entre accents graves, quand ce sont des valeurs de données).
- **Nombres** : nous écrivons à la française (espace pour les milliers, virgule décimale) dans le texte, et à l'anglaise (point décimal) dans les sorties de programme.
- **Dates** : `aaaa-mm-jj` dans les données et les requêtes (sans ambiguïté) ; `jj/mm/aaaa` dans les exports « à la française ».
- **Aléatoire** : toute simulation fixe sa **graine** (`np.random.default_rng(42)`, par exemple), donc vos résultats sont identiques aux nôtres.
- **Anonymat** : aucun nom réel, ni de boutique, ni de personne, ni de lieu. Les noms d'outils et de bibliothèques, eux, sont réels.
- **Encadrés** : 💡 intuition · 📐 pour qui veut la formule · 🧪 expérience · ⚠️ piège · ✅ à retenir · 🧭 repère ou section facultative · 📒 pour s'entraîner · 📦 données.

> ✅ **À retenir.** Les données de la boutique sont **simulées** : 36 395 commandes, 83 905 lignes, 6 000 clients, 120 produits, trois années, plus une enquête, un classeur Excel, un export de caisse désordonné et une base SQLite. La **vérité programmée** permet de juger ce que l'analyse retrouve. Les formules Excel sont vérifiées avec LibreOffice, les copies d'écran sont des maquettes, et tout se régénère par un script.
