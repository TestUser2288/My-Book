# Chapitre 1 : Analyse exploratoire des données — exercices et applications

> 🧭 Ce chapitre du cahier prolonge le chapitre 1 du livre. Les **applications** sont de petites études guidées sur les données de la boutique, à refaire pas à pas ; les **exercices** (⭐ facile, ⭐⭐ moyen, ⭐⭐⭐ difficile) sont corrigés à la fin. Chaque élément renvoie à la section du livre qui le prépare. Tout le code s'exécute à partir du dossier du volume.

```python
import os, sys, warnings
sys.path.insert(0, "build")
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from scipy import stats
import outils_ch01 as O

donnees = O.charger()
cmd, lig, prod, ret, j, cli, liv, ji, vi = (donnees[k] for k in ["cmd", "lig", "prod", "ret", "j", "cli", "liv", "ji", "vi"])
print(len(cmd), "commandes |", len(j), "jours |", len(liv), "livraisons")
```
<!--sortie-->
```text
36395 commandes | 1096 jours | 19420 livraisons
```

## Applications

### Application 1.1 — Résumer le panier, honnêtement (section 1.1.1)

**Objectif.** Produire en quelques lignes le résumé du panier que l'on remettrait à la gérante : des chiffres qui ne mentent pas.

**Étape 1 — Les résumés qui comptent.** Moyenne, médiane, moyenne tronquée à 5 %, quartiles, centiles 95 et 99.

```python
x = cmd["panier"]
res = {"moyenne": x.mean(), "médiane": x.median(), "moyenne tronquée 5 %": stats.trim_mean(x, 0.05),
       "Q1": x.quantile(0.25), "Q3": x.quantile(0.75), "centile 95": x.quantile(0.95), "centile 99": x.quantile(0.99)}
print({k: round(float(v), 1) for k, v in res.items()})
```
<!--sortie-->
```text
{'moyenne': 100.4, 'médiane': 79.8, 'moyenne tronquée 5 %': 92.4, 'Q1': 42.9, 'Q3': 135.4, 'centile 95': 254.5, 'centile 99': 383.7}
```

**Étape 2 — Combien de commandes sont « au-dessus de la moyenne » ?** Et quelle part du chiffre d'affaires font les 10 % de paniers les plus élevés ?

```python
print("part des commandes au-dessus de la moyenne :", round((x > x.mean()).mean() * 100, 1), "%")
tri = x.sort_values(ascending=False)
print("part du chiffre d'affaires des 10 % de paniers les plus élevés :", round(tri.head(int(0.1 * len(tri))).sum() / x.sum() * 100, 1), "%")
```
<!--sortie-->
```text
part des commandes au-dessus de la moyenne : 39.2 %
part du chiffre d'affaires des 10 % de paniers les plus élevés : 27.9 %
```

**Lecture.** Quatre commandes sur dix seulement dépassent la moyenne, et le dixième supérieur des paniers pèse plus du quart du chiffre d'affaires : un portrait par la seule moyenne serait trompeur.

**À vous.** Refaites l'étape 1 pour **chaque canal** et dites si la phrase « le panier typique est de 80 € » s'applique aux trois.

### Application 1.2 — Choisir ses classes et lire des délais (sections 1.1.2 et 1.1.3)

**Objectif.** Comparer des règles de choix du nombre de classes, puis résumer une variable discrète (les délais de livraison) par ses centiles.

**Étape 1 — Combien de classes selon la règle ?** Pour des tailles d'échantillon très différentes.

```python
rng = np.random.default_rng(0)
for n in (100, 1000, len(cmd)):
    e = x.sample(n, random_state=1) if n < len(cmd) else x
    print(f"n = {n:6d} | Sturges : {len(np.histogram_bin_edges(e, bins='sturges')) - 1:3d} classes | Freedman-Diaconis : {len(np.histogram_bin_edges(e, bins='fd')) - 1:3d} classes")
```
<!--sortie-->
```text
n =    100 | Sturges :   8 classes | Freedman-Diaconis :  14 classes
n =   1000 | Sturges :  11 classes | Freedman-Diaconis :  28 classes
n =  36395 | Sturges :  17 classes | Freedman-Diaconis : 177 classes
```

**Étape 2 — Les délais par transporteur.** Médiane, centile 90, part de livraisons à plus de 8 jours.

```python
t = liv.groupby("transporteur")["delai"].agg(médiane="median", centile90=lambda s: s.quantile(0.9), plus_de_8_jours=lambda s: (s > 8).mean() * 100)
print(t.round(1).to_string())
```
<!--sortie-->
```text
                médiane  centile90  plus_de_8_jours
transporteur                                       
Transporteur A      5.0        7.0              1.7
Transporteur B      6.0        8.0              3.5
Transporteur C      7.0        8.0              9.1
```

**Lecture.** Les deux règles diffèrent dès 100 observations (8 contre 14 classes) et l'écart s'élargit avec l'échantillon (17 contre 177 pour les 36 395 commandes), parce que Freedman-Diaconis tient compte de la dispersion et de la taille. Pour les délais, les centiles révèlent ce que la moyenne cache : le transporteur C a une médiane de deux jours de plus que le transporteur A et dépasse **environ cinq fois plus** souvent 8 jours que le transporteur A.

**À vous.** Quelle phrase écririez-vous pour promettre un délai aux clients, pour chaque transporteur ?

### Application 1.3 — Nuages, saison et corrélation « à saison égale » (section 1.2.1)

**Objectif.** Mesurer ce qui reste d'une corrélation une fois la saison retirée.

**Étape 1 — La corrélation brute.**

```python
print({c: round(float(j[c].corr(j["nb_commandes"])), 2) for c in ["depense_pub", "temperature_moy", "pluie_mm", "promo_active"]})
```
<!--sortie-->
```text
{'depense_pub': 0.53, 'temperature_moy': -0.21, 'pluie_mm': -0.03, 'promo_active': 0.07}
```

**Étape 2 — La corrélation à mois égal.** On retire de chaque variable la moyenne de son mois.

```python
jm = j.assign(mois=j["date"].dt.month)
def a_mois_egal(a, b):
    ra = jm[a] - jm.groupby("mois")[a].transform("mean")
    rb = jm[b] - jm.groupby("mois")[b].transform("mean")
    return round(float(ra.corr(rb)), 2)
print({c: a_mois_egal(c, "nb_commandes") for c in ["depense_pub", "temperature_moy", "pluie_mm", "promo_active"]})
```
<!--sortie-->
```text
{'depense_pub': 0.1, 'temperature_moy': -0.04, 'pluie_mm': -0.02, 'promo_active': 0.18}
```

**Lecture.** La corrélation de la publicité passe de 0,53 à 0,10, celle de la température de −0,21 à −0,04 : la saison portait l'essentiel du lien. La pluie, qui n'avait pas de lien brut, n'en a pas davantage. La promotion, dont le lien brut est faible (0,07), gagne en force **à mois égal** : c'est le signe d'une variable de confusion qui **cachait** l'effet.

**À vous.** Refaites l'étape 2 en retirant la moyenne par **mois et jour de la semaine**. Quelle corrélation de la publicité obtenez-vous ?

### Application 1.4 — Comparer des groupes et croiser des variables (sections 1.2.2 et 1.2.3)

**Objectif.** Décider, avec des intervalles de confiance, quels groupes diffèrent.

**Étape 1 — Intervalles de la moyenne par groupe.**

```python
def moyenne_ic(df, groupe, valeur):
    g = df.groupby(groupe)[valeur].agg(["mean", "std", "count"])
    g["bas"] = g["mean"] - 1.96 * g["std"] / np.sqrt(g["count"])
    g["haut"] = g["mean"] + 1.96 * g["std"] / np.sqrt(g["count"])
    return g[["mean", "bas", "haut"]].round(2)
print(moyenne_ic(cmd, "canal", "panier").to_string())
print(moyenne_ic(liv, "transporteur", "delai").to_string())
```
<!--sortie-->
```text
            mean    bas    haut
canal                          
Boutique  100.90  99.68  102.11
Réseaux   100.52  97.98  103.05
Site       99.77  98.50  101.03
                mean   bas  haut
transporteur                    
Transporteur A  5.21  5.18  5.24
Transporteur B  5.82  5.79  5.85
Transporteur C  6.68  6.64  6.72
```

**Étape 2 — Un tableau croisé et sa force.** Le taux de retour par canal et le V de Cramér.

```python
lc = lig.merge(cmd[["id_commande", "canal"]], on="id_commande")
lc["retourne"] = lc["id_ligne"].isin(ret["id_ligne"])
tab = pd.crosstab(lc["canal"], lc["retourne"])
chi2 = stats.chi2_contingency(tab)[0]
print((tab[True] / tab.sum(axis=1) * 100).round(1).to_dict(), "| V de Cramér :", round((chi2 / tab.values.sum()) ** 0.5, 3))
```
<!--sortie-->
```text
{'Boutique': 3.1, 'Réseaux': 6.7, 'Site': 9.0} | V de Cramér : 0.118
```

**Lecture.** Les intervalles du panier se recouvrent presque entièrement entre canaux ; ceux du délai ne se recouvrent pas du tout entre transporteurs. Le canal est lié au retour avec un V de 0,118 : modeste en valeur absolue, mais net sur plus de 80 000 lignes.

**À vous.** Croisez le **mode de livraison** et le **retard** (colonnes de `liv`) et calculez le V de Cramér. Le point relais retarde-t-il les livraisons ?

### Application 1.5 — Profils hebdomadaires et indice de prix (sections 1.3.1 et 1.3.2)

**Objectif.** Mesurer un rythme, puis isoler un changement de niveau à composition constante.

**Étape 1 — L'indice par jour de la semaine, par année.** La forme est-elle stable ?

```python
jj = j.assign(an=j["date"].dt.year, js=j["date"].dt.dayofweek)
idx = jj.groupby(["an", "js"])["nb_commandes"].mean().unstack(0)
print((idx / idx.mean()).round(2).T.to_string())
```
<!--sortie-->
```text
js       0     1     2     3     4     5     6
an                                            
2023  0.93  0.89  0.95  1.02  1.17  1.35  0.69
2024  0.97  0.90  0.91  0.97  1.17  1.42  0.67
2025  0.96  0.92  0.95  0.98  1.13  1.41  0.66
```

**Étape 2 — L'indice de prix par catégorie.** Le prix payé rapporté au prix catalogue, par année et catégorie.

```python
l2 = lig.merge(cmd[["id_commande", "date_commande"]], on="id_commande").merge(prod[["id_produit", "prix_vente", "categorie"]], on="id_produit")
l2["indice"] = l2["prix_unitaire"] / l2["prix_vente"]
print(l2.groupby([l2["date_commande"].dt.year, "categorie"])["indice"].mean().unstack(0).round(3).to_string())
```
<!--sortie-->
```text
date_commande  2023  2024  2025
categorie                      
Bien-être       1.0   1.0  1.03
Cuisine         1.0   1.0  1.03
Décoration      1.0   1.0  1.03
Jardin          1.0   1.0  1.03
Maison          1.0   1.0  1.03
Papeterie       1.0   1.0  1.03
```

**Lecture.** Le profil de la semaine est stable d'une année à l'autre (samedi fort, dimanche faible). La hausse de prix de 3 % se retrouve dans **toutes** les catégories : elle est générale, pas propre à un produit.

**À vous.** Calculez le panier moyen 2025 contre 2024 **à catégorie et canal constants** et comparez à la hausse brute de 3,5 %.

### Application 1.6 — Détecter des incidents pas à pas (section 1.3.4)

**Objectif.** Refaire la détection du livre en détaillant chaque étape.

**Étape 1 — Référence locale et score.**

```python
jz, doublons = O.incidents_jours(ji)
print(jz[["date", "nb_commandes", "chiffre_affaires", "z_commandes", "z_panier"]].round(2).loc[jz["date"].isin(vi["date"])].to_string(index=False))
```
<!--sortie-->
```text
      date  nb_commandes  chiffre_affaires  z_commandes  z_panier
2025-03-12            11           1293.02        -4.35      1.29
2025-03-13             8            742.37        -5.64     -0.14
2025-03-14            16           1512.58        -2.72     -0.35
2025-04-28            14           1298.36        -4.12     -0.65
2025-04-29            15           1359.77        -2.93     -1.30
2025-06-18            31           6752.36        -0.29      4.75
2025-09-09            29          30982.80        -0.15     15.26
2025-10-20            38           3684.52         0.58     -0.09
```

**Étape 2 — Choisir un seuil.** Précision et rappel pour plusieurs seuils.

```python
vrais = set(vi["date"])
for seuil in (3, 4, 5):
    s = O.signaler(jz, doublons, seuil)
    p, r = O.precision_rappel(s, vrais)
    print(f"seuil {seuil} : {len(s):2d} jours signalés, précision {p * 100:.0f} %, rappel {r * 100:.0f} %")
```
<!--sortie-->
```text
seuil 3 : 25 jours signalés, précision 24 %, rappel 75 %
seuil 4 : 11 jours signalés, précision 55 %, rappel 75 %
seuil 5 :  4 jours signalés, précision 75 %, rappel 38 %
```

**Lecture.** Les scores de commandes sont négatifs pour les pannes et fermetures mais modestes (de −2,7 à −5,6), tandis que le score de panier du jour est très élevé pour la commande B2B et l'erreur de saisie. Plus le seuil monte, plus la précision monte et plus le rappel baisse.

**À vous.** Ajoutez un troisième signal : le score du **chiffre d'affaires** (`z_ca`). Améliore-t-il le rappel au seuil 4 ?

### Application 1.7 — Le rapport d'exploration automatique (section 1.4)

**Objectif.** Appliquer le rapport à trois fichiers et décider des suites.

**Étape 1 — Trois fichiers, trois jeux d'alertes.**

```python
for nom, t, cle in [("produits", prod, "id_produit"), ("livraisons", liv[["id_commande", "transporteur", "delai", "colis_abime", "delai_promis_j"]], "id_commande"), ("retours", ret, "id_retour")]:
    r = O.rapport_eda(t, cle=cle)
    print(f"== {nom} ({r['lignes']} lignes)")
    print(*(r["alertes"] or ["aucune alerte"]), sep="\n")
```
<!--sortie-->
```text
== produits (120 lignes)
id_produit : une valeur différente par ligne (identifiant ?)
date_lancement : des dates stockées en texte (convertir)
prix_vente et cout_achat : corrélation forte (0.97)
== livraisons (19420 lignes)
id_commande : une valeur différente par ligne (identifiant ?)
delai_promis_j : une seule valeur (colonne inutile)
== retours (5002 lignes)
id_retour : une valeur différente par ligne (identifiant ?)
id_ligne : une valeur différente par ligne (identifiant ?)
date_retour : des dates stockées en texte (convertir)
montant_rembourse : très asymétrique (2.54) : regarder la médiane et l'échelle logarithmique
id_retour et id_ligne : corrélation forte (1.0)
```

**Étape 2 — Les noms de produits.** Le rapport ne dit pas tout : comptons les noms distincts.

```python
print("produits :", len(prod), "| noms distincts :", prod["nom_produit"].nunique(), "| identifiants distincts :", prod["id_produit"].nunique())
```
<!--sortie-->
```text
produits : 120 | noms distincts : 60 | identifiants distincts : 120
```

**Lecture.** Le rapport signale ce qui se mesure sur une colonne ; il n'a pas vu que **120 produits se partagent 60 noms** : une jointure sur le nom doublerait les lignes (volume II, chapitre 2). L'alerte manquante est un rappel : une exploration automatique ne remplace pas le regard.

**À vous.** Ajoutez à la fonction une alerte « le nom n'est pas unique » pour les colonnes de texte censées identifier une ligne, et relancez-la sur `produits`.

## Exercices

### Exercice 1.1 ⭐ — Moyenne et médiane à la main (section 1.1.1)

Sept paniers (en €) : 20, 25, 30, 35, 40, 45, 1 500. Calculez la moyenne et la médiane à la main, puis vérifiez avec Python. Laquelle annonceriez-vous ? Que deviennent-elles si l'on remplace 1 500 par 150 ?

### Exercice 1.2 ⭐ — Moyenne géométrique (section 1.1.1)

La moyenne **géométrique** d'une variable positive est l'exponentielle de la moyenne de ses logarithmes. Calculez-la pour le panier et comparez avec la moyenne et la médiane. Laquelle des trois est la plus proche du « montant typique » ?

### Exercice 1.3 ⭐⭐ — Les classes selon Sturges (section 1.1.2)

La règle de Sturges propose $1+\log_2 n$ classes. Calculez à la main le nombre de classes pour $n=100$, $n=1\,000$ et $n=36\,395$, et comparez à `np.histogram_bin_edges`. Pourquoi cette règle sous-estime-t-elle le nombre de classes utile quand $n$ est très grand ?

### Exercice 1.4 ⭐⭐ — Une hausse « à l'œil » (section 1.1.6)

Pour les paniers moyens 2024 (98,9 €) et 2025 (102,3 €), calculez le rapport des **hauteurs de barre** pour un axe qui commence à zéro, puis à 97 €, puis à 90 €. À partir de quelle origine l'écart visuel dépasse-t-il le double ? Que concluez-vous ?

### Exercice 1.5 ⭐ — Pearson et Spearman (section 1.2.1)

Pour les couples $(1,\,1)$, $(2,\,4)$, $(3,\,9)$, $(4,\,16)$, $(5,\,25)$, calculez les coefficients de Pearson et de Spearman. Pourquoi diffèrent-ils ? Ajoutez le point $(6,\,300)$ : que deviennent-ils ?

### Exercice 1.6 ⭐⭐ — La pluie, à mois égal (section 1.2.1)

Calculez la corrélation entre la pluie (`pluie_mm`) et le nombre de commandes du canal Boutique par jour (à reconstruire à partir de `cmd`), brute, puis à mois égal. La pluie a-t-elle un effet détectable sur la boutique ? (Indice : la vérité programmée parle de −8 % les jours de pluie pour la boutique.)

### Exercice 1.7 ⭐⭐ — Le V de Cramér à la main (section 1.2.3)

Dans un tableau 2 × 2 dont les lignes sont les canaux Boutique et Site, les colonnes « retour » et « pas de retour », les effectifs sont 120 et 3 880 pour la Boutique, 360 et 3 640 pour le Site. Calculez à la main le khi-deux, le V de Cramér, puis vérifiez avec `scipy`.

### Exercice 1.8 ⭐⭐⭐ — Fabriquer un paradoxe de Simpson (section 1.2.5)

Construisez une table de deux traitements A et B appliqués à deux groupes de patients (légers et graves) où **B réussit mieux que A dans chaque groupe**, mais **A réussit mieux que B globalement**. Donnez des effectifs et des taux ; vérifiez par le calcul. Quelle variable de confusion avez-vous créée ?

### Exercice 1.9 ⭐ — Un indice hebdomadaire à la main (section 1.3.1)

Voici les commandes de deux semaines consécutives : lundi 30, 28 ; mardi 29, 27 ; mercredi 31, 29 ; jeudi 32, 33 ; vendredi 38, 40 ; samedi 46, 44 ; dimanche 22, 24. Calculez l'indice de chaque jour de la semaine (moyenne du jour sur la moyenne générale) et dites ce que signifie l'indice du samedi.

### Exercice 1.10 ⭐⭐ — Une référence locale à la main (section 1.3.4)

Les commandes de six samedis consécutifs sont 44, 47, 45, 12, 46, 48. Avec une référence locale de deux samedis avant et deux après (le samedi lui-même exclu), calculez la référence du quatrième samedi, l'écart relatif en logarithme, et dites s'il est « anormal » si l'écart-type robuste typique des écarts vaut 0,15.

### Exercice 1.11 ⭐⭐ — Choisir un seuil par le coût (section 1.3.4)

Une fausse alerte coûte 1 unité (dix minutes d'enquête), un incident raté 20 unités. En utilisant les résultats des seuils 3, 3,5, 4, 5 et 6 (à recalculer), quel seuil minimise le coût total pour les données de 2025 ? Que changerait un incident raté à 5 unités ?

### Exercice 1.12 ⭐⭐⭐ — Un calendrier d'événements (section 1.3.5)

Retirez des jours signalés ceux qui tombent entre le 1ᵉʳ et le 7 janvier, que l'on déclare « événement connu » (soldes et jours de l'an). Recalculez la précision et le rappel au seuil 4 contre `verite_incidents`. Que gagne-t-on, et que risque-t-on avec cette règle ?

### Exercice 1.13 ⭐ — La liste de contrôle sur les produits (section 1.4)

Appliquez `rapport_eda` à `produits.csv` avec `cle="id_produit"`, puis complétez à la main les contrôles de la liste (les six temps) en deux lignes par temps.

### Exercice 1.14 ⭐⭐ — Écrire le compte rendu (section 1.4)

À partir de `livraisons.csv`, écrivez le compte rendu d'une page de l'exploration (trame de la section 1.4.4) : une phrase par temps, avec au moins quatre chiffres calculés par du code.

## Corrigés

### Corrigé 1.1

```python
v = np.array([20, 25, 30, 35, 40, 45, 1500])
print("moyenne :", round(v.mean(), 1), "| médiane :", np.median(v))
w = v.copy(); w[-1] = 150
print("avec 150 au lieu de 1 500 : moyenne", round(w.mean(), 1), "| médiane", np.median(w))
```
<!--sortie-->
```text
moyenne : 242.1 | médiane : 35.0
avec 150 au lieu de 1 500 : moyenne 49.3 | médiane 35.0
```

La somme vaut 1 695, soit une moyenne de 242,1 € ; la médiane (quatrième valeur) est 35 €. La valeur extrême **change tout** pour la moyenne et **rien** pour la médiane. On annonce la médiane (35 €), en signalant la commande de 1 500 € à part. En remplaçant par 150, la moyenne tombe à 49,3 €.

### Corrigé 1.2

```python
g = np.exp(np.log(x).mean())
print("moyenne :", round(x.mean(), 1), "| médiane :", round(x.median(), 1), "| moyenne géométrique :", round(g, 1))
```
<!--sortie-->
```text
moyenne : 100.4 | médiane : 79.8 | moyenne géométrique : 71.9
```

La moyenne géométrique (71,9 €) est le **centre multiplicatif** : elle est moins sensible aux gros paniers que la moyenne arithmétique (100,4 €), qui s'interprète comme « total divisé par le nombre de commandes ». Elle tombe même **sous la médiane** (79,8 €), parce que le logarithme du panier est lui-même asymétrique, vers la gauche (−0,71). Pour **prévoir un chiffre d'affaires total**, c'est la moyenne arithmétique qui compte, car elle conserve la somme ; pour décrire un panier typique, la médiane est la plus simple à expliquer.

### Corrigé 1.3

```python
for n in (100, 1000, 36395):
    print(n, "classes de Sturges à la main :", round(1 + np.log2(n), 1), "| numpy :", len(np.histogram_bin_edges(np.arange(n), bins="sturges")) - 1)
```
<!--sortie-->
```text
100 classes de Sturges à la main : 7.6 | numpy : 8
1000 classes de Sturges à la main : 11.0 | numpy : 11
36395 classes de Sturges à la main : 16.2 | numpy : 17
```

$1+\log_2 100\approx7{,}6$, $1+\log_2 1\,000\approx11{,}0$ et $1+\log_2 36\,395\approx16{,}2$ : numpy arrondit à l'entier supérieur (8, 11, 17). La règle ne dépend que de $n$ et croît très lentement : avec 36 395 observations, elle propose 17 classes alors que les données en supporteraient bien davantage ; elle suppose en outre une distribution **à peu près symétrique**.

### Corrigé 1.4

```python
for origine in (0, 97, 90):
    h24, h25 = 98.9 - origine, 102.3 - origine
    print(f"origine {origine:3d} € : hauteur 2024 = {h24:5.1f}, hauteur 2025 = {h25:5.1f}, rapport = {h25 / h24:.2f}")
```
<!--sortie-->
```text
origine   0 € : hauteur 2024 =  98.9, hauteur 2025 = 102.3, rapport = 1.03
origine  97 € : hauteur 2024 =   1.9, hauteur 2025 =   5.3, rapport = 2.79
origine  90 € : hauteur 2024 =   8.9, hauteur 2025 =  12.3, rapport = 1.38
```

À zéro, le rapport est de 1,03 : l'œil voit la hausse réelle. À 97 €, il vaut 2,8 ; à 90 €, 1,4. Le rapport dépasse 2 dès que l'origine dépasse environ 95 €. Une barre dont l'origine n'est pas zéro **ment sur les proportions** : on la réserve aux courbes, ou on le dit explicitement.

### Corrigé 1.5

```python
a = np.array([1, 2, 3, 4, 5]); b = a ** 2
print("sans extrême : Pearson", round(stats.pearsonr(a, b)[0], 3), "| Spearman", round(stats.spearmanr(a, b)[0], 3))
a2 = np.r_[a, 6]; b2 = np.r_[b, 300]
print("avec (6 ; 300) : Pearson", round(stats.pearsonr(a2, b2)[0], 3), "| Spearman", round(stats.spearmanr(a2, b2)[0], 3))
```
<!--sortie-->
```text
sans extrême : Pearson 0.981 | Spearman 1.0
avec (6 ; 300) : Pearson 0.707 | Spearman 1.0
```

La relation $y=x^2$ est **monotone mais pas droite** : Spearman vaut exactement 1, Pearson un peu moins (0,98). Avec le point extrême (6 ; 300), Pearson tombe à 0,71 : un seul point domine la droite ; Spearman, qui ne regarde que les rangs, reste à 1. Spearman est plus robuste aux extrêmes, mais il ne dit pas si la relation est droite.

### Corrigé 1.6

```python
cb = cmd[cmd["canal"] == "Boutique"].groupby("date_commande").size().rename("boutique")
jb = j.set_index("date").join(cb).fillna({"boutique": 0}).reset_index()
jb["mois"] = jb["date"].dt.month
brut = jb["pluie_mm"].corr(jb["boutique"])
ra = jb["pluie_mm"] - jb.groupby("mois")["pluie_mm"].transform("mean"); rb = jb["boutique"] - jb.groupby("mois")["boutique"].transform("mean")
print("corrélation brute :", round(brut, 3), "| à mois égal :", round(ra.corr(rb), 3))
jb["pluvieux"] = jb["pluie_mm"] > 1
print("commandes Boutique par jour : sans pluie", round(jb.loc[~jb["pluvieux"], "boutique"].mean(), 1), "| avec pluie", round(jb.loc[jb["pluvieux"], "boutique"].mean(), 1))
```
<!--sortie-->
```text
corrélation brute : -0.062 | à mois égal : -0.057
commandes Boutique par jour : sans pluie 15.9 | avec pluie 14.4
```

La corrélation est faible dans les deux cas (−0,06), parce que **le hasard quotidien (Poisson) et la saison noient** un effet de −8 %. La comparaison des moyennes (15,9 commandes sans pluie contre 14,4 avec pluie, soit −9 %) est, elle, compatible avec la vérité programmée, mais elle ne tient pas compte de la saison : un jour de pluie n'est pas réparti au hasard dans l'année. Un effet réel de cette taille ne se voit pas à l'œil sur un nuage ; il faut un modèle qui contrôle la saison et le jour de la semaine (chapitre 3) ou un test sur un grand nombre de jours (chapitre 2).

### Corrigé 1.7

```python
t = np.array([[120, 3880], [360, 3640]])
att = np.outer(t.sum(1), t.sum(0)) / t.sum()
chi2 = ((t - att) ** 2 / att).sum()
print("effectifs attendus :", att.round(0).tolist(), "| khi-deux :", round(chi2, 1), "| V :", round((chi2 / t.sum()) ** 0.5, 3))
print("scipy (sans correction) :", round(stats.chi2_contingency(t, correction=False)[0], 1))
```
<!--sortie-->
```text
effectifs attendus : [[240.0, 3760.0], [240.0, 3760.0]] | khi-deux : 127.7 | V : 0.126
scipy (sans correction) : 127.7
```

Les effectifs attendus sont 240 retours et 3 760 non-retours dans chaque ligne ; le khi-deux est la somme des $(\text{observé}-\text{attendu})^2/\text{attendu}$ ; le V de Cramér vaut $\sqrt{\chi^2/(n\,(k-1))}$ avec $k=2$. Le résultat (V proche de 0,13) est du même ordre que celui des données réelles (0,118) : la liaison est modeste mais indiscutable sur 8 000 lignes.

### Corrigé 1.8

```python
# groupe : (succès A, total A, succès B, total B)
t = {"légers": (234, 270, 81, 87), "graves": (55, 80, 192, 263)}
for g, (sa, na, sb, nb) in t.items():
    print(f"{g:7s} A : {sa / na * 100:.0f} % ({sa}/{na}) | B : {sb / nb * 100:.0f} % ({sb}/{nb})")
SA, NA = sum(v[0] for v in t.values()), sum(v[1] for v in t.values())
SB, NB = sum(v[2] for v in t.values()), sum(v[3] for v in t.values())
print(f"global  A : {SA / NA * 100:.0f} % ({SA}/{NA}) | B : {SB / NB * 100:.0f} % ({SB}/{NB})")
```
<!--sortie-->
```text
légers  A : 87 % (234/270) | B : 93 % (81/87)
graves  A : 69 % (55/80) | B : 73 % (192/263)
global  A : 83 % (289/350) | B : 78 % (273/350)
```

Dans **chaque** groupe, B réussit mieux que A (93 % contre 87 % chez les cas légers, 73 % contre 69 % chez les cas graves) ; **globalement**, A réussit mieux (83 % contre 78 %). L'explication tient dans la **composition** : A est appliqué surtout à des cas légers (270 sur 350), B surtout à des cas graves (263 sur 350). La variable de confusion est la **gravité**, qui détermine à la fois le traitement reçu et la réussite. D'autres effectifs conviennent, pourvu que les proportions de groupes soient très différentes d'un traitement à l'autre.

### Corrigé 1.9

```python
sem = pd.DataFrame({"jour": ["lun", "mar", "mer", "jeu", "ven", "sam", "dim"], "s1": [30, 29, 31, 32, 38, 46, 22], "s2": [28, 27, 29, 33, 40, 44, 24]})
sem["moyenne_jour"] = sem[["s1", "s2"]].mean(axis=1)
sem["indice"] = (sem["moyenne_jour"] / sem["moyenne_jour"].mean()).round(2)
print(sem[["jour", "moyenne_jour", "indice"]].to_string(index=False))
```
<!--sortie-->
```text
jour  moyenne_jour  indice
 lun          29.0    0.90
 mar          28.0    0.87
 mer          30.0    0.93
 jeu          32.5    1.00
 ven          39.0    1.21
 sam          45.0    1.39
 dim          23.0    0.71
```

La moyenne générale vaut environ 32,4 commandes par jour ; l'indice du samedi (45 sur 32,4) signifie que le samedi compte environ **39 % de commandes de plus** que le jour moyen, et celui du dimanche (23 sur 32,4) environ 29 % de moins.

### Corrigé 1.10

```python
s = np.array([44, 47, 45, 12, 46, 48], dtype=float)
ref = np.median(np.r_[s[1:3], s[4:6]])
print("référence du 4e samedi :", ref, "| écart relatif (log) :", round(np.log(12 / ref), 2), "| score z :", round(np.log(12 / ref) / 0.15, 1))
```
<!--sortie-->
```text
référence du 4e samedi : 46.5 | écart relatif (log) : -1.35 | score z : -9.0
```

La référence est la médiane de 47, 45, 46 et 48, soit 46,5. L'écart relatif est $\ln(12/46{,}5)\approx-1{,}35$, soit un score de −9,0 pour un écart-type robuste de 0,15 : ce samedi est **très** anormal (et cela se justifie : on a divisé les ventes par près de quatre).

### Corrigé 1.11

```python
vrais = set(vi["date"])
for seuil in (3, 3.5, 4, 5, 6):
    s = O.signaler(jz, doublons, seuil)
    fausses, ratees = len(s - vrais), len(vrais - s)
    print(f"seuil {seuil} : {fausses:2d} fausses alertes, {ratees} incidents ratés | coût (1 ; 20) = {fausses + 20 * ratees:3d} | (1 ; 5) = {fausses + 5 * ratees:3d} | (1 ; 1) = {fausses + ratees:3d}")
```
<!--sortie-->
```text
seuil 3 : 19 fausses alertes, 2 incidents ratés | coût (1 ; 20) =  59 | (1 ; 5) =  29 | (1 ; 1) =  21
seuil 3.5 :  7 fausses alertes, 2 incidents ratés | coût (1 ; 20) =  47 | (1 ; 5) =  17 | (1 ; 1) =   9
seuil 4 :  5 fausses alertes, 2 incidents ratés | coût (1 ; 20) =  45 | (1 ; 5) =  15 | (1 ; 1) =   7
seuil 5 :  1 fausses alertes, 5 incidents ratés | coût (1 ; 20) = 101 | (1 ; 5) =  26 | (1 ; 1) =   6
seuil 6 :  0 fausses alertes, 6 incidents ratés | coût (1 ; 20) = 120 | (1 ; 5) =  30 | (1 ; 1) =   6
```

Avec un incident raté qui coûte 20 fois une fausse alerte, le coût total est minimal au **seuil 4** (45 unités) ; avec 5 fois, c'est encore le seuil 4 (15), mais l'écart avec les autres se réduit. Si les deux erreurs coûtaient autant (1 contre 1), les seuils 5 et 6 (coût 6) battraient le seuil 4 (coût 7) : plus l'incident raté est bon marché, plus le seuil optimal monte. Un seuil n'est pas une propriété du jeu de données : c'est une **décision** qui encode un coût.

### Corrigé 1.12

```python
connus = {d for d in jz["date"] if d.month == 1 and d.day <= 7}
s4 = O.signaler(jz, doublons, 4)
s4b = s4 - connus
for nom, s in [("sans calendrier", s4), ("avec calendrier", s4b)]:
    p, r = O.precision_rappel(s, vrais)
    print(f"{nom} : {len(s)} jours signalés, précision {p * 100:.0f} %, rappel {r * 100:.0f} %")
```
<!--sortie-->
```text
sans calendrier : 11 jours signalés, précision 55 %, rappel 75 %
avec calendrier : 7 jours signalés, précision 86 %, rappel 75 %
```

Écarter les premiers jours de janvier retire les faux positifs qui tombent à cette période : la **précision** monte, le **rappel** ne change pas (aucun incident injecté ne tombe là). Le risque est de **masquer un vrai incident** survenant un 3 janvier : le calendrier doit être **précis** (par exemple le 1ᵉʳ janvier seulement) et revu chaque année.

### Corrigé 1.13

```python
r = O.rapport_eda(prod, cle="id_produit")
print(r["types"].to_string()); print(*(r["alertes"] or ["aucune alerte"]), sep="\n")
print("noms distincts :", prod["nom_produit"].nunique(), "sur", len(prod), "produits")
```
<!--sortie-->
```text
                   type  manquants_pct  distincts
id_produit        int64            0.0        120
nom_produit         str            0.0         60
categorie           str            0.0          6
prix_vente      float64            0.0         64
cout_achat      float64            0.0        117
fournisseur         str            0.0          8
date_lancement      str            0.0        118
id_produit : une valeur différente par ligne (identifiant ?)
date_lancement : des dates stockées en texte (convertir)
prix_vente et cout_achat : corrélation forte (0.97)
noms distincts : 60 sur 120 produits
```

Les six temps : **tableau** (120 lignes, une par produit, `id_produit` unique) ; **types** (`date_lancement` est en texte : à convertir) ; **manques** (aucun) ; **variables** (six catégories de 20 produits chacune, huit fournisseurs) ; **relations** (le prix de vente et le coût d'achat sont corrélés à 0,97 : l'un déduit presque l'autre) ; **temps et anomalies** (la date de lancement permet d'étudier l'âge du catalogue ; les noms en double, 60 pour 120 produits, sont une anomalie que le rapport ne voit pas).

### Corrigé 1.14

```python
d = liv["delai"]
print("1. grain :", len(liv), "livraisons, une par commande ; période", liv["date_commande"].min(), "à", liv["date_commande"].max())
print("2. manquants :", int(liv.isna().sum().sum()), "| types : dates en texte")
print("3. délai : médiane", d.median(), "j, centile 90 :", d.quantile(0.9), "j, plus de 8 jours :", round((d > 8).mean() * 100, 1), "%")
print("4. transporteur C : délai moyen", round(liv.loc[liv["transporteur"] == "Transporteur C", "delai"].mean(), 2), "j contre", round(liv.loc[liv["transporteur"] == "Transporteur A", "delai"].mean(), 2), "j pour A")
print("5. colis abîmés :", round(liv["colis_abime"].mean() * 100, 1), "% | retards sur délai promis :", round(liv["retard"].mean() * 100, 1), "%")
```
<!--sortie-->
```text
1. grain : 19420 livraisons, une par commande ; période 2023-01-01 à 2025-12-31
2. manquants : 0 | types : dates en texte
3. délai : médiane 6.0 j, centile 90 : 8.0 j, plus de 8 jours : 3.8 %
4. transporteur C : délai moyen 6.68 j contre 5.21 j pour A
5. colis abîmés : 1.7 % | retards sur délai promis : 26.6 %
```

Un compte rendu d'une page reprend ces cinq lignes en phrases : *grain et période* ; *qualité* (rien ne manque, dates à convertir) ; *niveau de service* (médiane de 6 jours, 9 commandes sur 10 sous 8 jours) ; *relation notable* (le transporteur C est plus lent, à confirmer par un test et par une régression) ; *anomalies* (les retards se concentrent en décembre, à explorer au chapitre 11) ; *question ouverte* (le retard coûte-t-il des retours ?).
