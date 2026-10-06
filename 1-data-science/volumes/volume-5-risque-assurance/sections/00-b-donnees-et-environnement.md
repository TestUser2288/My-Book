# Carte du volume, données et environnement

Cette section ouvre le volume par trois choses : la **carte des chapitres**, le **catalogue des jeux de données** (avec, pour chacun, ce qu'il contient et ce qu'on y a « programmé »), et l'**environnement** nécessaire pour refaire tous les calculs.

## Carte du volume

Les chapitres suivent la boucle de l'introduction : **chiffrer**, **décider**, **valider**. Les chapitres marqués ➕ sont facultatifs : le reste du volume ne les suppose pas, et chaque chapitre est lisible seul à condition d'avoir lu l'introduction.

| Chapitre | Question posée | Contenu |
|---|---|---|
| **1. Risque de crédit et scoring** | Quel emprunteur risque de défaillir, et combien la banque perdra-t-elle ? | grille de score, modèles de défaut, mesures de performance (Gini, KS, ROC) ; ➕ WOE et IV, PD-LGD-EAD et pertes attendues (IFRS 9), matrices de transition |
| **2. Modélisation actuarielle** | Quelle prime faut-il demander, et combien mettre de côté pour des sinistres futurs ? | fréquence et sévérité, tarification, provisionnement ; ➕ GLM tarifaires et crédibilité, *chain ladder*, Mack et bootstrap, assurance santé |
| **3. Mesures de risque et stress tests** | Que peut-on perdre dans le pire millième des cas ? Et si la crise est plus dure que prévu ? | VaR et *expected shortfall*, stress tests ; ➕ risques opérationnel, de marché et de liquidité, rétro-test et validation |
| **4. Cadre réglementaire** | Quel capital exige-t-on, et selon quelles règles ? | Bâle, Solvabilité, principes du Takaful ; ➕ IFRS 17, Takaful et finance islamique, lutte contre le blanchiment et fraude |
| **➕ 5. Assurance vie** | Combien vaut un engagement qui dure quarante ans ? | tables de mortalité, mathématiques actuarielles de la vie, modèle de Lee-Carter |
| **➕ 6. Réassurance** | Quelle part du risque faut-il céder, et à quel prix ? | formes de réassurance, tarification d'un traité, choix d'une couverture |
| **➕ 7. Actif-passif et portefeuille** | Comment adosser ce que l'on possède à ce que l'on doit ? | gestion actif-passif, théorie du portefeuille, de la frontière efficiente à l'actif-passif |
| **Projet du volume (cahier)** | Un tarif défendable, de bout en bout | un modèle de tarification avec validation hors période et notes réglementaires |

## Les jeux de données du volume

Tout est **simulé** avec des graines fixes (script `build/donnees5.py`), sauf un jeu **réel**. Chaque jeu simulé suit un mécanisme que le script documente en tête de fichier : c'est la **vérité programmée**. Nous la révélerons à la fin des études où elle est instructive, et le cahier permet de la retrouver.

Chargeons tous les fichiers et regardons leur forme et leurs valeurs manquantes.

```python hide-code
import os, sys
import numpy as np
import pandas as pd

sys.path.insert(0, "build")
import donnees5

def lire(nom):
    return pd.read_csv(f"donnees/{nom}.csv")

fichiers = ["credit_defaut", "credits_conso", "recouvrements", "revolving_defauts", "portefeuille_ifrs9", "notations_panel",
            "taux_defaut_macro", "polices_auto", "sinistres_auto", "triangle_rc", "triangle_dommages", "triangle_choc",
            "sante_assures", "sinistres_gros", "cat_annuel", "rendements_marche", "courbe_taux", "pertes_operationnelles",
            "mortalite_population", "portefeuille_vie", "transactions_lab", "comptes_lab", "takaful_fonds"]
D = {nom: lire(nom) for nom in fichiers}
for nom in fichiers:
    t = D[nom]
    print(f"{nom:24s} {t.shape[0]:7d} lignes {t.shape[1]:3d} colonnes {int(t.isna().sum().sum()):6d} manquants")
```
<!--sortie-->
```text
credit_defaut              30000 lignes  24 colonnes      0 manquants
credits_conso              40000 lignes  12 colonnes   4787 manquants
recouvrements               6000 lignes   7 colonnes      0 manquants
revolving_defauts           8000 lignes   5 colonnes      0 manquants
portefeuille_ifrs9         20000 lignes   9 colonnes      0 manquants
notations_panel            39102 lignes   4 colonnes      0 manquants
taux_defaut_macro             80 lignes   7 colonnes      0 manquants
polices_auto              100000 lignes  12 colonnes      0 manquants
sinistres_auto              5722 lignes   5 colonnes      0 manquants
triangle_rc                   55 lignes   5 colonnes      0 manquants
triangle_dommages             45 lignes   5 colonnes      0 manquants
triangle_choc                 55 lignes   5 colonnes      0 manquants
sante_assures              39112 lignes  15 colonnes      0 manquants
sinistres_gros              2898 lignes   2 colonnes      0 manquants
cat_annuel                    40 lignes   2 colonnes      0 manquants
rendements_marche           4000 lignes   6 colonnes      0 manquants
courbe_taux                  120 lignes  10 colonnes      0 manquants
pertes_operationnelles      1802 lignes   6 colonnes      0 manquants
mortalite_population        8000 lignes   5 colonnes      0 manquants
portefeuille_vie           20000 lignes   8 colonnes      0 manquants
transactions_lab          110223 lignes   8 colonnes      0 manquants
comptes_lab                 3000 lignes   4 colonnes      0 manquants
takaful_fonds                 45 lignes   7 colonnes      0 manquants
```

Les seules valeurs manquantes sont celles de `credits_conso` : elles sont **voulues**, nous y revenons plus bas. Voici maintenant le catalogue, avec les chapitres qui utilisent chaque jeu.

| Jeu | Contenu | Nature | Chapitres |
|---|---|---|---|
| `credit_defaut.csv` | 30 000 clients de cartes de crédit, défaut au mois suivant | **réel** (UCI, CC0) | 1, 3, projet (variante) |
| `credits_conso.csv` | 40 000 prêts à la souscription, défaut à 12 mois | simulé | 1, 3, 4 |
| `recouvrements.csv`, `revolving_defauts.csv` | pertes réalisées après défaut ; crédit renouvelable en défaut | simulé | 1 |
| `portefeuille_ifrs9.csv` | 20 000 prêts en vie, avec retards et probabilités de défaut | simulé | 1, 4 |
| `notations_panel.csv` | 5 000 emprunteurs notés pendant dix ans | simulé | 1 |
| `taux_defaut_macro.csv` | 80 trimestres de conjoncture et de taux de défaut | simulé | 1, 3 |
| `polices_auto.csv`, `sinistres_auto.csv` | 100 000 contrats-années d'assurance automobile ; leurs sinistres | simulé | 2, projet |
| `triangle_*.csv` et `triangle_*_verite.csv` | triangles de paiements (3 branches) ; paiements futurs réels | simulé | 2 |
| `sante_assures.csv` | assurés d'une complémentaire santé, trois années | simulé | 2 |
| `sinistres_gros.csv`, `cat_annuel.csv` | grands sinistres incendie ; pertes catastrophes annuelles | simulé | 6 |
| `rendements_marche.csv`, `marche_verite.csv` | rendements journaliers de cinq actifs ; régime vrai | simulé | 3, 7 |
| `courbe_taux.csv` | courbe des taux, mois par mois | simulé | 3, 7 |
| `pertes_operationnelles.csv` | événements de risque opérationnel | simulé | 3 |
| `mortalite_population.csv` (+ vérité), `portefeuille_vie.csv` | décès et expositions par âge ; contrats d'assurance vie | simulé | 5, 7 |
| `transactions_lab.csv`, `comptes_lab.csv`, `verite_lab.csv` | transactions bancaires et étiquettes de comptes suspects | simulé | 4 |
| `takaful_fonds.csv` | trois fonds de Takaful sur quinze ans | simulé | 4 |

### Le crédit à la consommation

Le jeu principal du chapitre 1 est `credits_conso.csv`, un portefeuille de prêts à la consommation observé **à la souscription**, avec la cible `defaut_12m` : 1 si l'emprunteur est en défaut dans les douze mois.

| Colonne | Signification |
|---|---|
| `age`, `revenu_annuel`, `anciennete_emploi` | caractéristiques de l'emprunteur (ancienneté en années) |
| `logement` | `locataire`, `proprietaire`, `heberge` |
| `objet` | `auto`, `travaux`, `conso` |
| `montant`, `duree_mois` | caractéristiques du prêt (en €, en mois) |
| `taux_endettement` | charges mensuelles rapportées au revenu mensuel, après le nouveau prêt |
| `nb_incidents_12m`, `anciennete_relation` | incidents de paiement récents ; ancienneté de la relation avec la banque |
| `defaut_12m` | **cible** : défaut dans les douze mois |

```python hide
c = D["credits_conso"]
print("credits_conso : lignes", len(c), "| défaut", round(c["defaut_12m"].mean(), 4), "| défauts", int(c["defaut_12m"].sum()))
print("  manquants : revenu", round(c["revenu_annuel"].isna().mean(), 3), "| ancienneté d'emploi", round(c["anciennete_emploi"].isna().mean(), 3))
print("  ancienneté d'emploi manquante selon le défaut :", c.groupby("defaut_12m")["anciennete_emploi"].apply(lambda s: round(s.isna().mean(), 3)).to_dict())
print("  âge", int(c["age"].min()), "à", int(c["age"].max()), "| montant médian", float(c["montant"].median()), "| revenu médian", float(c["revenu_annuel"].median()), "| durée médiane", float(c["duree_mois"].median()))
print("  défaut par logement :", c.groupby("logement")["defaut_12m"].mean().round(3).to_dict())
print("  défaut par nombre d'incidents (0,1,2,3+) :", c.groupby(c["nb_incidents_12m"].clip(upper=3))["defaut_12m"].mean().round(3).to_dict())
cd = D["credit_defaut"]
print("credit_defaut : lignes", len(cd), "| défaut", round(cd["default"].mean(), 4))
```
<!--sortie-->
```text
credits_conso : lignes 40000 | défaut 0.0597 | défauts 2387
  manquants : revenu 0.05 | ancienneté d'emploi 0.069
  ancienneté d'emploi manquante selon le défaut : {0: 0.065, 1: 0.14}
  âge 21 à 75 | montant médian 8100.0 | revenu médian 31920.0 | durée médiane 36.0
  défaut par logement : {'heberge': 0.075, 'locataire': 0.066, 'proprietaire': 0.044}
  défaut par nombre d'incidents (0,1,2,3+) : {0: 0.044, 1: 0.093, 2: 0.175, 3: 0.371}
credit_defaut : lignes 30000 | défaut 0.2212
```

Le taux de défaut est de **6,0 %** (2 387 défauts sur 40 000 prêts) : un événement rare, comme il se doit. Deux colonnes ont des valeurs manquantes, **volontairement** : 5,0 % des revenus et 6,9 % des anciennetés d'emploi. Mais ces manquants ne sont pas aléatoires : l'ancienneté d'emploi manque pour 14,0 % des emprunteurs en défaut contre 6,5 % des autres, comme dans un dossier réel où ce qu'on ne sait pas dire sur soi est souvent significatif. Un modèle qui ignore ce fait perd de l'information (section 1.1). Le défaut est d'ailleurs très lié à l'historique : il passe de 4,4 % pour les emprunteurs sans incident à 37,1 % pour ceux qui en ont eu trois ou plus, et il est de 4,4 % chez les propriétaires contre 6,6 % chez les locataires et 7,5 % chez les hébergés. Enfin, le mécanisme de défaut comporte des **effets non linéaires** (un effet de l'âge en forme de U, un « coude » du taux d'endettement) qu'une grille de score par classes retrouvera mieux qu'une régression logistique linéaire : c'est le sujet des sections 1.1 et 1.4.

Le jeu **réel** est `credit_defaut.csv` : 30 000 clients de cartes de crédit d'une banque, observés en 2005, avec le défaut de paiement le mois suivant (22,1 %). Il vient du dépôt de l'UCI sous la licence CC0, et a été constitué par Yeh et Lien (2009). Il nous sert aux « détours sur données réelles » : il est plus délicat que nos jeux simulés (dépendances cachées, variables liées), et c'est ce qui le rend instructif.

### Les pertes en cas de défaut, les expositions, les provisions

Cinq jeux complètent le crédit pour le chapitre 1 (➕ sections 1.4 à 1.6) :

| Jeu | Colonnes principales |
|---|---|
| `recouvrements.csv` (6 000 prêts en défaut) | `garantie` (`aucune`, `caution`, `nantissement`), `objet`, `ead`, `delai_recouvrement_mois`, **`lgd_realisee`** (part de l'exposition définitivement perdue, de 0 à 1) |
| `revolving_defauts.csv` (8 000 lignes de crédit renouvelable en défaut) | `limite`, `tirage_12m_avant` (la part utilisée un an avant), `ead` (l'exposition au moment du défaut), `ccf_observe` (la part du non-utilisé finalement tirée) |
| `portefeuille_ifrs9.csv` (20 000 prêts en vie) | `ead`, `pd_origine`, `pd_actuelle`, `jours_retard`, `maturite_residuelle`, `lgd_estimee`, `taux_effectif`, `restructure` |
| `notations_panel.csv` (5 000 emprunteurs, dix ans) | `annee` (0 à 9), `note_debut` (de 1, la meilleure, à 7), `note_fin` (de 1 à 7, **8 = défaut**, 0 = sorti du portefeuille) |
| `taux_defaut_macro.csv` (80 trimestres) | `croissance_pib`, `chomage`, `variation_immo`, `taux_defaut` |

```python hide
r = D["recouvrements"]; rv = D["revolving_defauts"]; p = D["portefeuille_ifrs9"]; n = D["notations_panel"]; m = D["taux_defaut_macro"]
print("recouvrements : LGD moyenne", round(r["lgd_realisee"].mean(), 3), "| part de LGD nulle", round((r["lgd_realisee"] == 0).mean(), 3), "| par garantie", r.groupby("garantie")["lgd_realisee"].mean().round(2).to_dict())
print("revolving : CCF moyen", round(rv["ccf_observe"].mean(), 3))
print("ifrs9 : retard >= 30 j", round((p["jours_retard"] >= 30).mean(), 3), "| retard >= 90 j", round((p["jours_retard"] >= 90).mean(), 3), "| encours M€", round(p["ead"].sum() / 1e6, 1), "| restructurés", round(p["restructure"].mean(), 3), "| PD d'origine médiane", round(p["pd_origine"].median(), 4))
print("notations : lignes", len(n), "| emprunteurs", n["id_emprunteur"].nunique(), "| défauts", int((n["note_fin"] == 8).sum()), "| sorties", int((n["note_fin"] == 0).sum()), "| années", int(n["annee"].min()), "à", int(n["annee"].max()))
print("macro : trimestres", len(m), "| taux de défaut : min", m["taux_defaut"].min(), "max", m["taux_defaut"].max(), "moyen", round(m["taux_defaut"].mean(), 4), "| pic au trimestre", int(m.loc[m["taux_defaut"].idxmax(), "trimestre"]))
print("matrice vraie : somme des lignes", donnees5.matrice_vraie().sum(axis=1).round(6).tolist(), "| PD à un an de la note 7 :", round(float(donnees5.matrice_vraie()[6, 7]), 3))
```
<!--sortie-->
```text
recouvrements : LGD moyenne 0.459 | part de LGD nulle 0.12 | par garantie {'aucune': 0.61, 'caution': 0.27, 'nantissement': 0.37}
revolving : CCF moyen 0.402
ifrs9 : retard >= 30 j 0.059 | retard >= 90 j 0.024 | encours M€ 302.4 | restructurés 0.026 | PD d'origine médiane 0.0199
notations : lignes 39102 | emprunteurs 5000 | défauts 767 | sorties 1537 | années 0 à 9
macro : trimestres 80 | taux de défaut : min 0.00992 max 0.1283 moyen 0.0306 | pic au trimestre 52
matrice vraie : somme des lignes [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0] | PD à un an de la note 7 : 0.283
```

Les pertes réalisées après défaut ont une allure caractéristique : la **LGD moyenne est de 45,9 %**, mais 12 % des défauts se soldent par une perte **nulle** (tout est récupéré), et la garantie compte énormément (61 % de perte moyenne sans garantie, 27 % avec caution, 37 % avec nantissement). Pour le crédit renouvelable, le **CCF** moyen est de 40,2 % : en moyenne, un emprunteur qui fait défaut a tiré 40 % de ce qui lui restait disponible avant la rupture. Le portefeuille `portefeuille_ifrs9.csv` totalise 302,4 M€ d'encours, dont 5,9 % de prêts en retard d'au moins 30 jours et 2,4 % d'au moins 90 jours ; c'est à vous de calculer les « étapes » de la norme (section 1.5). Le panel de notations compte 39 102 observations annuelles de 5 000 emprunteurs, avec 767 défauts et 1 537 sorties du portefeuille (retraits que l'on ne doit pas confondre avec des défauts, section 1.6). Les taux de défaut trimestriels vont de 1,0 % à 12,8 %, avec un pic au trimestre 52 : une **récession** programmée que le chapitre 3 utilisera pour les tests de crise.

### L'assurance automobile, les triangles, la santé

Le chapitre 2 repose sur l'assurance automobile de la mutuelle.

| Colonne de `polices_auto.csv` | Signification |
|---|---|
| `annee` | année d'exercice (2022, 2023 ou 2024) ; une ligne = un contrat sur une année |
| `exposition` | fraction de l'année pendant laquelle le contrat était en vigueur (de 0,05 à 1) |
| `age_conducteur`, `anciennete_permis`, `age_vehicule`, `puissance` | caractéristiques du conducteur et du véhicule |
| `zone` | `Zone A` à `Zone F` (zones tarifaires fictives) |
| `bonus_malus`, `usage`, `carburant` | coefficient de bonus-malus (50 à 150), usage, motorisation |
| `nb_sinistres` | **cible de fréquence** : nombre de sinistres déclarés pendant l'exposition |

`sinistres_auto.csv` détaille chaque sinistre : `id_police`, `annee`, `type` (`materiel` ou `corporel`) et `montant` (en €). Les **triangles** (`triangle_rc.csv`, `triangle_dommages.csv`, `triangle_choc.csv`) donnent, pour dix années de survenance (2015 à 2024) et pour chaque **délai** de règlement, le paiement incrémental, le cumul, et la prime acquise de l'année ; les fichiers `*_verite.csv` contiennent le carré **complet**, c'est-à-dire aussi les paiements qui n'ont pas encore été faits à fin 2024, ce qui permet de juger une provision **a posteriori**. Enfin `sante_assures.csv` suit des assurés d'une complémentaire santé (`age`, `sexe`, `niveau` de garantie, `ald` pour une affection de longue durée, `exposition`, les coûts par poste et `cout_total`).

```python hide
po = D["polices_auto"]; s = lire("sinistres_auto"); sa = D["sante_assures"]
print("polices : lignes", len(po), "| exposition totale", round(po["exposition"].sum()), "| sinistres", int(po["nb_sinistres"].sum()), "| fréquence annuelle", round(po["nb_sinistres"].sum() / po["exposition"].sum(), 4), "| lignes par année", po.groupby("annee").size().to_dict())
print("sinistres : n", len(s), "| répartition", s["type"].value_counts().to_dict(), "| coût moyen", s.groupby("type")["montant"].mean().round(0).to_dict(), "| maximum", int(s["montant"].max()), "| médiane", float(s["montant"].median()))
for k in ["rc", "dommages", "choc"]:
    o = lire("triangle_" + k); v = lire("triangle_" + k + "_verite")
    reste = v.groupby("annee_survenance")["paiement_incremental"].sum() - o.groupby("annee_survenance")["paiement_incremental"].sum()
    print(f"triangle {k:9s}: cellules observées {len(o):3d} | carré complet {len(v):3d} | délais {int(v['delai'].max()) + 1:2d} | payé à fin 2024 {o['paiement_incremental'].sum() / 1e6:6.1f} M€ | reste à payer réel {reste.sum() / 1e6:6.1f} M€")
print("sante : lignes", len(sa), "| assurés", sa["id_assure"].nunique(), "| coût moyen", round(sa["cout_total"].mean()), "| part d'ALD", round(sa["ald"].mean(), 3), "| coût moyen par niveau", sa.groupby("niveau")["cout_total"].mean().round(0).to_dict())
```
<!--sortie-->
```text
polices : lignes 100000 | exposition totale 86602 | sinistres 5722 | fréquence annuelle 0.0661 | lignes par année {2022: 30244, 2023: 32741, 2024: 37015}
sinistres : n 5722 | répartition {'materiel': 5146, 'corporel': 576} | coût moyen {'corporel': 53099.0, 'materiel': 2638.0} | maximum 2477620 | médiane 2399.5
triangle rc       : cellules observées  55 | carré complet 130 | délais 13 | payé à fin 2024  423.7 M€ | reste à payer réel  242.1 M€
triangle dommages : cellules observées  45 | carré complet  60 | délais  6 | payé à fin 2024  410.4 M€ | reste à payer réel   32.3 M€
triangle choc     : cellules observées  55 | carré complet 130 | délais 13 | payé à fin 2024  427.9 M€ | reste à payer réel  243.5 M€
sante : lignes 39112 | assurés 15884 | coût moyen 1292 | part d'ALD 0.173 | coût moyen par niveau {'basique': 962.0, 'confort': 1304.0, 'premium': 2051.0}
```

Le portefeuille automobile compte 100 000 contrats-années (86 602 années-véhicule d'exposition) et **5 722 sinistres**, soit une fréquence annuelle de 6,6 %. La plupart sont matériels (5 146, coût moyen de 2 638 €) ; 576 sont corporels, avec un coût moyen de 53 099 € et un maximum de plus de 2,4 M€ : **un faible nombre de sinistres porte l'essentiel du coût**, d'où l'intérêt d'une loi à queue lourde (section 2.1). Les triangles révèlent l'écart des branches : à fin 2024, il reste à payer **242,1 M€** sur la branche de responsabilité civile (queue longue, treize délais) contre **32,3 M€** sur les dommages (queue courte, six délais), pour des paiements déjà effectués du même ordre (environ 424 M€ et 410 M€). Dans le troisième triangle (`choc`), un choc d'inflation a frappé la diagonale de 2022 : le reste à payer réel (243,5 M€) est du même ordre, mais la méthode du *chain ladder* s'y trompera (section 2.5).

### Les marchés, la conjoncture et les pertes opérationnelles

Pour les mesures de risque (chapitre 3), `rendements_marche.csv` donne les rendements journaliers de cinq actifs (`actions_A`, `actions_B`, `obligations`, `immobilier`, `matieres`) sur 4 000 jours ouvrés à partir du 4 janvier 2010. Le générateur y a programmé des **régimes** (calme, stress) ; `marche_verite.csv` donne le régime vrai de chaque jour. `courbe_taux.csv` donne, mois par mois (120 mois), les taux de neuf maturités de 3 mois à 30 ans. `pertes_operationnelles.csv` liste les événements de risque opérationnel de dix ans (`categorie`, `ligne_metier`, `perte_brute`, `recuperation`, `perte_nette`).

```python hide
rm = D["rendements_marche"]; mv = lire("marche_verite"); ct = D["courbe_taux"]; po2 = D["pertes_operationnelles"]
print("marché : jours", len(rm), "|", rm["date"].iloc[0], "à", rm["date"].iloc[-1], "| part de jours de stress", round((mv["regime"] == "stress").mean(), 3))
print("  écart-type journalier :", rm.iloc[:, 1:].std().round(4).to_dict())
print("  pire jour :", rm.iloc[:, 1:].min().round(3).to_dict())
print("courbe : lignes", len(ct), "| maturités", ct.shape[1] - 1, "| taux 10 ans au mois 1, 60, 90, 120 :", ct["taux_10_0a"].iloc[[0, 59, 89, 119]].round(4).tolist())
print("opérationnel : événements", len(po2), "| de", po2["date_evenement"].min(), "à", po2["date_evenement"].max(), "| perte nette moyenne", round(po2["perte_nette"].mean()), "| maximum", int(po2["perte_nette"].max()), "| total M€", round(po2["perte_nette"].sum() / 1e6, 1))
```
<!--sortie-->
```text
marché : jours 4000 | 2010-01-04 à 2025-05-02 | part de jours de stress 0.07
  écart-type journalier : {'actions_A': 0.0118, 'actions_B': 0.0143, 'obligations': 0.0028, 'immobilier': 0.0083, 'matieres': 0.0139}
  pire jour : {'actions_A': -0.089, 'actions_B': -0.109, 'obligations': -0.025, 'immobilier': -0.057, 'matieres': -0.139}
courbe : lignes 120 | maturités 9 | taux 10 ans au mois 1, 60, 90, 120 : [0.0234, 0.027, 0.0435, 0.0246]
opérationnel : événements 1802 | de 2015-01-02 à 2024-12-29 | perte nette moyenne 14238 | maximum 1798860 | total M€ 25.7
```

Les rendements portent les défauts classiques des marchés : volatilité qui se regroupe, queues épaisses, corrélations qui montent en crise. Les jours de stress représentent 7 % de l'échantillon, et le pire jour atteint −10,9 % pour la seconde action et −13,9 % pour les matières premières. Le taux à dix ans de la courbe passe de 2,3 % au premier mois à 2,7 % au mois 60, monte à 4,35 % au mois 90 (le cycle de hausse programmé) puis revient à 2,5 %. Les pertes opérationnelles comptent 1 802 événements, de 2015 à 2024, pour 25,7 M€ au total : la perte nette moyenne est de 14 238 €, mais le maximum atteint près de 1,8 M€, ce qui est typique d'une distribution à queue lourde.

### La vie, la réassurance, la lutte contre le blanchiment, le Takaful

Les chapitres suivants utilisent des jeux plus spécialisés :

| Jeu | Contenu et colonnes principales |
|---|---|
| `mortalite_population.csv` | pour chaque `annee` (1980 à 2019), `age` (0 à 99) et `sexe` : `exposition` (personnes-années) et `deces` |
| `mortalite_verite.csv`, `mortalite_kt_vrai.csv` | les paramètres vrais du modèle de Lee-Carter qui a produit les décès |
| `portefeuille_vie.csv` | `sexe`, `age_emission`, `annee_emission`, `contrat` (`temporaire_10`, `temporaire_20`, `vie_entiere`), `capital`, `exposition_2015_2019`, `deces` |
| `sinistres_gros.csv`, `cat_annuel.csv` | grands sinistres incendie (`annee_survenance`, `montant`) ; perte annuelle due aux catastrophes (`annee`, `perte_cat`, souvent nulle) |
| `transactions_lab.csv` | transactions bancaires : `date`, `id_compte`, `sens`, `type` (`virement`, `especes`, `carte`), `montant`, `contrepartie`, `pays_contrepartie` |
| `comptes_lab.csv`, `verite_lab.csv` | profil des comptes ; **étiquette de vérité** : le schéma suspect planté (ou `aucun`) |
| `takaful_fonds.csv` | pour trois fonds (`famille`, `auto`, `sante`) et quinze années : `cotisations`, `sinistres`, `frais_gestion`, `rendement`, `reserve_ouverture` |

```python hide
mo = D["mortalite_population"]; pv = D["portefeuille_vie"]; sg = D["sinistres_gros"]; ca = D["cat_annuel"]
tx = D["transactions_lab"]; cl = D["comptes_lab"]; ve = lire("verite_lab"); tk = D["takaful_fonds"]
print("mortalité : lignes", len(mo), "| décès", int(mo["deces"].sum()), "| années", int(mo["annee"].min()), "à", int(mo["annee"].max()))
print("vie : contrats", len(pv), "| décès", int(pv["deces"].sum()), "| exposition", round(pv["exposition_2015_2019"].sum()), "| contrats", pv["contrat"].value_counts().to_dict())
print("gros sinistres : n", len(sg), "|", int(sg["annee_survenance"].min()), "à", int(sg["annee_survenance"].max()), "| maximum", int(sg["montant"].max()), "| catastrophes : années", len(ca), "dont avec événement", int((ca["perte_cat"] > 0).sum()), "| maximum", int(ca["perte_cat"].max()))
print("LAB : transactions", len(tx), "| comptes", len(cl), "| suspects", int(ve["suspect"].sum()), round(ve["suspect"].mean(), 3), "| schémas", ve["schema"].value_counts().to_dict(), "| part d'espèces", round((tx["type"] == "especes").mean(), 3))
print("takaful : lignes", len(tk), "| fonds", tk["fonds"].unique().tolist(), "| années", int(tk["annee"].min()), "à", int(tk["annee"].max()))
```
<!--sortie-->
```text
mortalité : lignes 8000 | décès 6596675 | années 1980 à 2019
vie : contrats 20000 | décès 832 | exposition 84909 | contrats {'vie_entiere': 7009, 'temporaire_20': 6954, 'temporaire_10': 6037}
gros sinistres : n 2898 | 2010 à 2024 | maximum 4310320 | catastrophes : années 40 dont avec événement 17 | maximum 35614167
LAB : transactions 110223 | comptes 3000 | suspects 57 0.019 | schémas {'aucun': 2943, 'relais': 15, 'fractionnement': 15, 'pays_a_risque': 15, 'aller_retour': 12} | part d'espèces 0.206
takaful : lignes 45 | fonds ['famille', 'auto', 'sante'] | années 2010 à 2024
```

Le portefeuille d'assurance vie compte 20 000 contrats pour 84 909 années d'exposition et 832 décès ; la mortalité de la population porte sur plus de 6,5 millions de décès. Les grands sinistres incendie sont au nombre de 2 898 sur quinze ans et vont jusqu'à plus de 4,3 M€ ; parmi les 40 années de catastrophes, 17 ont connu un événement (le maximum atteint 35,6 M€). Côté lutte contre le blanchiment, 57 comptes sur 3 000 (1,9 %) portent un schéma suspect planté (fractionnement, relais, aller-retour, flux vers des pays à risque), noyés dans 110 223 transactions, avec en plus des commerces légitimes qui déposent beaucoup d'espèces et qui seront des **faux positifs** difficiles.

> 📦 **Régénérer les données.** Les fichiers sont versionnés avec le volume, mais la commande `python build/donnees5.py` les régénère à l'identique (une dizaine de secondes). La docstring de ce script contient toute la vérité programmée ; `donnees5.matrice_vraie()` donne la matrice de transition de notations qui a produit `notations_panel.csv`.

## L'environnement de travail

Ce volume n'utilise que des outils déjà rencontrés (Python et sa pile scientifique, statsmodels pour les GLM, `arch` pour les modèles GARCH), sans modèle pré-entraîné ni service externe. Les versions sont **figées** (fichier `requirements.txt`) : la pile numérique doit rester celle des volumes précédents, sinon certains résultats peuvent changer d'une décimale.

```bash noexec
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt           # versions figées (pandas 3.0.6, numpy 2.5.3, scikit-learn 1.9.1, statsmodels 0.15...)
python build/donnees5.py                  # régénère les jeux simulés ; credit_defaut.csv (jeu réel, UCI CC0) est fourni
```

```python hide-code
import platform
from importlib.metadata import version
print("Python        :", platform.python_version())
for nom in ["numpy", "pandas", "scipy", "scikit-learn", "statsmodels", "arch", "lifelines", "lightgbm", "xgboost", "shap", "matplotlib", "pyarrow"]:
    print(f"{nom:13s} :", version(nom))
```
<!--sortie-->
```text
Python        : 3.13.3
numpy         : 2.5.3
pandas        : 3.0.6
scipy         : 1.18.1
scikit-learn  : 1.9.1
statsmodels   : 0.15.0
arch          : 8.0.0
lifelines     : 0.30.3
lightgbm      : 4.7.0
xgboost       : 3.4.1
shap          : 0.52.0
matplotlib    : 3.11.2
pyarrow       : 25.0.1
```

| Bibliothèque | Pour quoi faire | Chapitres |
|---|---|---|
| `numpy`, `pandas`, `scipy` | calcul, tableaux, lois de probabilité, optimisation | tous |
| `statsmodels` | régressions logistiques, GLM (Poisson, binomiale négative, Gamma, Tweedie) | 1, 2 |
| `scikit-learn`, `lightgbm`, `xgboost`, `shap` | modèles d'apprentissage, explications | 1, 2, projet |
| `arch` | modèles GARCH pour les rendements | 3 |
| `lifelines` | durées et survie | 5 |
| `matplotlib` | figures | tous |

> ⚠️ **Ce qui n'est pas installé, et que l'on écrit à la main.** Il existe des bibliothèques spécialisées pour la construction de grilles de score, le provisionnement par triangles, l'optimisation de portefeuille ou les calculs actuariels. Elles ne sont **pas** utilisées ici : les méthodes principales (discrétisation, *chain ladder*, frontière efficiente, commutations) sont écrites en quelques lignes de NumPy, parce que c'est le meilleur moyen de savoir ce que l'outil calcule, y compris ses hypothèses. Aucun outil n'est présenté comme « le standard ».

## Conventions du volume

- **Validation hors période.** Quand les données sont datées, on **entraîne sur le passé et on valide sur la période suivante** : par exemple 2022 et 2023 pour apprendre, 2024 pour juger. Un découpage aléatoire mélange le futur et le passé et donne des résultats trop optimistes ; la réalité ne nous offre jamais de futur en entraînement (volume III, section 1.1).
- **Nommer pareil.** La cible de défaut s'appelle `defaut_12m` ; les ensembles sont « jeu d'entraînement », « jeu de validation », « jeu de test » ; le « modèle de référence » est le modèle simple à battre.
- **Monnaie et unités.** Les montants sont en €, les durées en mois ou en années (précisé dans chaque colonne), les taux sont des fractions (0,02 pour 2 %) dans les tableaux et des pourcentages dans la prose.
- **Anonymat.** La banque et la mutuelle n'ont pas de nom ; les zones sont « Zone A… Zone F », les pays « Pays P1… Pays P12 ». Aucune autorité nationale n'est citée : on parle de « l'autorité de contrôle » ou de « la banque centrale ». Les textes **internationaux** sont nommés.
- **Graines fixes.** Chaque simulation fixe sa graine : `np.random.default_rng(graine)`. Aucun résultat du livre ne dépend du temps de calcul.
- **Une vérité programmée à comparer.** Quand une étude se termine par la comparaison à la vérité, c'est une particularité des données simulées, qu'on signale à chaque fois ; en pratique, on ne dispose que de la réalité qui se réalise, et trop tard.
