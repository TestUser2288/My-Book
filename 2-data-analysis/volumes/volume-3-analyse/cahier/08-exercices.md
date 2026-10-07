# Chapitre 8 : ➕ Pareto, analyse ABC et benchmarking — exercices et applications

> 🧭 Ce chapitre du cahier prolonge le chapitre 8 du livre (chapitre complémentaire). Les **applications** sont de petites études guidées sur les produits, les clients et les indicateurs de la boutique ; les **exercices** sont numérotés, avec leur niveau (⭐ de base, ⭐⭐ intermédiaire, ⭐⭐⭐ plus délicat) ; les **corrigés** sont à la fin. Tout le code est exécuté : essayez avant de regarder.

Une première cellule charge les bibliothèques et les fichiers ; les autres reprennent les noms ainsi définis.

```python
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch08 as O

D = os.environ["DONNEES"]
cmd, lg, prod, ret, cli = O.charger(D)
sect = pd.read_csv(os.path.join(D, "benchmark_secteur.csv"))
l25 = lg[lg["annee"] == 2025]
ca_produit = l25.groupby("id_produit")["montant"].sum()
print(len(lg), "lignes de commande |", len(prod), "produits |", len(cli), "clients |", len(sect), "indicateurs de secteur (fictifs)")
```
<!--sortie-->
```text
83905 lignes de commande | 120 produits | 6000 clients | 12 indicateurs de secteur (fictifs)
```

## Applications

### Application 8.1 — Pareto d'une année à l'autre (section 8.1)

**Objectif.** Comparer la concentration du chiffre d'affaires par produit en 2023, 2024 et 2025.

```python
for an in (2023, 2024, 2025):
    d = O.pareto(lg[lg["annee"] == an].groupby("id_produit")["montant"].sum())
    print(an, "| les 20 % premiers font", round(d.loc[d["part_elements"] <= 20, "part_cumulee"].max(), 1), "% | Gini", round(O.gini(d["valeur"]), 3))
```
<!--sortie-->
```text
2023 | les 20 % premiers font 50.5 % | Gini 0.479
2024 | les 20 % premiers font 50.3 % | Gini 0.476
2025 | les 20 % premiers font 51.0 % | Gini 0.479
```

**Lecture.** La part des 20 % premiers produits est stable (50,5 %, 50,3 %, 51,0 %) et le Gini aussi (0,479, 0,476, 0,479) : sur trois ans, la concentration ne bouge pas. Avec 120 produits, une différence d'un demi-point n'est de toute façon pas un signal.

**À vous.** La concentration augmente-t-elle ou baisse-t-elle ? Est-ce significatif, vu le nombre de produits ?

### Application 8.2 — ABC par catégorie (section 8.1)

**Objectif.** Faire une analyse ABC **à l'intérieur** de chaque catégorie plutôt que sur tout le catalogue, et comparer.

```python
global_abc = O.classes_abc(ca_produit)
cat_de = prod.set_index("id_produit")["categorie"]
local = pd.concat([O.classes_abc(s) for _, s in ca_produit.groupby(cat_de.reindex(ca_produit.index))]).reindex(ca_produit.index)
print(pd.crosstab(global_abc.rename("classe globale"), local.rename("classe dans la catégorie")).to_string())
```
<!--sortie-->
```text
classe dans la catégorie   A   B   C
classe globale                      
A                         48   8   0
B                         13  15   4
C                          5   8  19
```

**Étape 2.** Quelle catégorie n'a **aucun** produit en classe A globale ?

```python
print(pd.crosstab(cat_de.reindex(global_abc.index), global_abc).to_string())
```
<!--sortie-->
```text
col_0        A  B   C
categorie            
Bien-être    4  9   7
Cuisine     12  4   4
Décoration  14  4   2
Jardin      12  4   4
Maison      14  5   1
Papeterie    0  6  14
```

**Lecture.** La Papeterie n'a **aucun** produit en classe A (14 produits C sur 20) : ses produits sont peu chers (entre 3 et 25 €). Classés à l'intérieur de la catégorie, 48 des 56 produits A globaux restent A, mais 13 produits B globaux deviennent A dans leur catégorie : c'est utile pour juger la place de chaque produit **parmi ses semblables**, par exemple pour la Papeterie.

**À vous.** Quand est-il préférable de classer à l'intérieur d'une catégorie ?

### Application 8.3 — Les remboursements par classe (section 8.1)

**Objectif.** Croiser les classes ABC (chiffre d'affaires) avec la part des remboursements.

```python
rb = l25[l25["retournee"]].merge(ret[["id_ligne", "montant_rembourse"]], on="id_ligne").groupby("id_produit")["montant_rembourse"].sum()
t = pd.DataFrame({"remboursements": rb.groupby(global_abc.reindex(rb.index)).sum(), "ca": ca_produit.groupby(global_abc).sum()})
t["remboursé / CA %"] = (t["remboursements"] / t["ca"] * 100).round(2)
t["part des remboursements %"] = (t["remboursements"] / t["remboursements"].sum() * 100).round(1)
print(t.round(1).to_string())
```
<!--sortie-->
```text
   remboursements         ca  remboursé / CA %  part des remboursements %
A         67931.8  1068313.7               6.4                       80.4
B         12250.1   192883.9               6.4                       14.5
C          4287.0    63566.2               6.7                        5.1
```

**Lecture.** Le taux de remboursement rapporté au chiffre d'affaires est presque le même dans les trois classes (6,4 %, 6,4 % et 6,7 %) : les produits A concentrent les remboursements (80,4 %) **en proportion** de leur chiffre d'affaires, pas davantage. Le Pareto des retours reproduit donc celui des ventes : un retour est un risque de **volume**, pas d'un produit en particulier.

**À vous.** Les produits A concentrent-ils les remboursements en proportion de leur chiffre d'affaires ?

### Application 8.4 — Produits irréguliers (section 8.1)

**Objectif.** Repérer les produits de classe A dont la demande est irrégulière et estimer leur besoin de stock de sécurité.

```python
mens = l25.groupby(["id_produit", "mois"])["quantite"].sum().unstack(fill_value=0)
cv = mens.std(axis=1) / mens.mean(axis=1)
irreguliers = cv[(global_abc == "A") & (cv >= 0.60)].sort_values(ascending=False)
print(len(irreguliers), "produits A à demande irrégulière (coefficient de variation d'au moins 0,60)")
print(pd.DataFrame({"produit": prod.set_index("id_produit").loc[irreguliers.index[:5], "nom_produit"].values, "cv": irreguliers.iloc[:5].round(2).values}).to_string(index=False))
```
<!--sortie-->
```text
12 produits A à demande irrégulière (coefficient de variation d'au moins 0,60)
           produit   cv
 Guirlande compact 0.88
          Vase mat 0.76
      Gants design 0.74
Statuette rustique 0.70
  Transat nordique 0.69
```

**Étape 2.** Un stock de sécurité simple vaut $z\,\sigma\sqrt{L}$ avec $z=1{,}65$ (95 %), $\sigma$ l'écart-type de la demande **mensuelle** et $L$ le délai de réapprovisionnement exprimé en **mois** (ici un demi-mois).

```python
sig = mens.std(axis=1)
ss = (1.65 * sig * np.sqrt(0.5)).round(0)
print("stock de sécurité (unités) pour les cinq premiers :", ss.loc[irreguliers.index[:5]].astype(int).to_dict())
```
<!--sortie-->
```text
stock de sécurité (unités) pour les cinq premiers : {54: 17, 52: 19, 98: 9, 55: 15, 86: 29}
```

**Lecture.** Douze produits A ont une demande irrégulière ; le plus irrégulier, la « Guirlande compact », a un coefficient de variation de 0,88. Pour les cinq premiers, le stock de sécurité va de 9 à 29 unités, alors que leur demande mensuelle moyenne va de 10 à 36 unités.

**À vous.** Pourquoi le stock de sécurité est-il plus élevé pour un produit irrégulier que pour un produit régulier de même volume ?

### Application 8.5 — Positionner la boutique (section 8.2)

**Objectif.** Positionner la boutique par rapport au secteur (données fictives), puis tester la sensibilité du verdict.

```python
pos = O.positionner(O.indicateurs_boutique(D, 2025), sect)
print(pos[["indicateur", "valeur", "mediane_secteur", "ecart_std", "verdict"]].round(2).to_string(index=False))
```
<!--sortie-->
```text
                            indicateur  valeur  mediane_secteur  ecart_std              verdict
              Taux de marge brute (HT)   37.96             38.0      -0.01 proche de la médiane
               Taux de retour (lignes)    6.29              5.5       0.21 proche de la médiane
                          Panier moyen  102.33             92.0       0.29            favorable
            Taux de conversion du site    4.78              2.6       1.47            favorable
               Part du site dans le CA   46.63             35.0       0.52               neutre
            Rotation du stock (par an)    4.23              4.2       0.01 proche de la médiane
              Taux de rupture de stock    7.36              4.0       0.91          défavorable
                  Livraisons à l'heure   73.47             92.0      -2.50          défavorable
        Coût d'acquisition d'un client  115.37             18.0       8.21          défavorable
              Clients actifs à 12 mois   64.58             42.0       1.22            favorable
Part des frais de personnel dans le CA   12.78             24.0      -1.51            favorable
```

**Étape 2.** Que deviennent les verdicts si l'on considère qu'un écart de moins de **0,5** écart-type est « proche de la médiane » (au lieu de 0,25) ?

```python
pos["verdict_05"] = np.where(pos["sens"] == 0, "neutre", np.where(pos["ecart_std"].abs() < 0.5, "proche de la médiane", pos["verdict"]))
print(pos.loc[pos["verdict"] != pos["verdict_05"], ["indicateur", "ecart_std", "verdict", "verdict_05"]].round(2).to_string(index=False))
```
<!--sortie-->
```text
  indicateur  ecart_std   verdict           verdict_05
Panier moyen       0.29 favorable proche de la médiane
```

**Lecture.** Un seul verdict change avec le seuil de 0,5 écart-type : le **panier moyen** (écart de 0,29), qui passe de « favorable » à « proche de la médiane ». Les autres verdicts — ruptures, livraisons, coût d'acquisition, conversion, clients actifs, frais de personnel — sont **robustes** : leurs écarts dépassent 0,9 écart-type.

**À vous.** Quel est l'indicateur dont le verdict est le plus **robuste** au choix du seuil ?

## Exercices

**Exercice 8.1 ⭐ (section 8.1).** Cinq produits ont pour ventes 50, 30, 10, 6 et 4 €. Calculez les parts, les parts cumulées et les classes ABC (80 % et 95 %).

**Exercice 8.2 ⭐⭐ (section 8.1).** Calculez à la main le coefficient de Gini de quatre produits de ventes 1, 1, 2 et 6, avec la formule $G=\dfrac{2\sum_i i\,x_{(i)}}{n\sum_i x_i}-\dfrac{n+1}{n}$ où $x_{(i)}$ sont les valeurs triées par ordre **croissant**. Vérifiez avec `O.gini`.

**Exercice 8.3 ⭐⭐ (section 8.1).** Combien de produits faut-il pour atteindre 50 %, 70 % et 90 % du chiffre d'affaires de 2025 ? Qu'en concluez-vous sur la concentration ?

**Exercice 8.4 ⭐⭐ (section 8.1).** Calculez la part des produits A de 2023 qui sont encore A en 2025. Comparez avec le chiffre 2024–2025 du livre.

**Exercice 8.5 ⭐⭐ (section 8.1).** Refaites l'analyse ABC sur la **marge** de 2025 et comparez les produits A en chiffre d'affaires et A en marge : combien sont communs ? La Papeterie a-t-elle des produits A en marge ?

**Exercice 8.6 ⭐⭐⭐ (section 8.1).** Refaites la classification XYZ avec la variabilité **hebdomadaire** au lieu de la variabilité mensuelle (coefficient de variation des ventes par semaine). Les classes changent-elles ? Pourquoi un pas de temps plus fin donne-t-il des coefficients plus élevés ?

**Exercice 8.7 ⭐ (section 8.2).** Le taux de retour de la boutique est de 6,3 %, la médiane du secteur de 5,5 %, les quartiles de 3,5 % et 8,5 %. Calculez à la main l'écart standardisé robuste et dites si l'écart est favorable.

**Exercice 8.8 ⭐⭐ (section 8.2).** Recalculez le coût d'acquisition avec une définition plus étroite : seules les dépenses **payantes et réseaux sociaux** (fichier `campagnes.csv`) divisées par les nouveaux clients dont le canal d'acquisition est le **Site** ou les **Réseaux**. Cet indicateur se rapproche-t-il de la médiane du secteur ?

**Exercice 8.9 ⭐⭐ (section 8.2).** Les livraisons à l'heure dépendent du délai **promis**. Calculez la part des livraisons de 2025 effectuées en 6, 8 et 10 jours au plus (depuis la commande). Que concluez-vous sur la comparabilité avec un secteur dont on ignore le délai promis ?

## Corrigés

**Corrigé 8.1.** Parts : 50 %, 30 %, 10 %, 6 %, 4 % ; cumul : 50, 80, 90, 96, 100 %. Avec la règle « A tant que le cumul **avant** l'élément est inférieur à 80 % » : le produit 1 (cumul avant 0) est A, le produit 2 (50) est A, le produit 3 (80) est B, le produit 4 (90) est B, le produit 5 (96) est C.

```python
v = pd.Series([50, 30, 10, 6, 4], index=list("12345"), dtype=float)
print(O.pareto(v)[["valeur", "part_cumulee"]].round(1).assign(classe=O.classes_abc(v)).to_string())
```
<!--sortie-->
```text
   valeur  part_cumulee classe
1    50.0          50.0      A
2    30.0          80.0      A
3    10.0          90.0      B
4     6.0          96.0      B
5     4.0         100.0      C
```

**Corrigé 8.2.** Valeurs triées 1, 1, 2, 6 ($n=4$, somme 10). $\sum_i i\,x_{(i)}=1\cdot1+2\cdot1+3\cdot2+4\cdot6=33$. $G=\dfrac{2\times33}{4\times10}-\dfrac{5}{4}=1{,}65-1{,}25=0{,}40$.

```python
print("Gini :", round(O.gini([1, 1, 2, 6]), 2))
```
<!--sortie-->
```text
Gini : 0.4
```

**Corrigé 8.3.**

```python
d = O.pareto(ca_produit)
for part in (50, 70, 90):
    n = int((d["part_cumulee"] < part).sum() + 1)
    print(f"{part} % du chiffre d'affaires : {n} produits sur {len(d)} ({n / len(d) * 100:.0f} %)")
```
<!--sortie-->
```text
50 % du chiffre d'affaires : 24 produits sur 120 (20 %)
70 % du chiffre d'affaires : 43 produits sur 120 (36 %)
90 % du chiffre d'affaires : 74 produits sur 120 (62 %)
```

Il faut 24 produits (20 % du catalogue) pour la moitié du chiffre d'affaires, 43 (36 %) pour 70 % et 74 (62 %) pour 90 % : la concentration est **modérée** et la courbe monte régulièrement ; il n'y a pas de poignée de produits qui porte l'entreprise.

**Corrigé 8.4.**

```python
abc23 = O.classes_abc(lg[lg["annee"] == 2023].groupby("id_produit")["montant"].sum())
a23 = abc23[abc23 == "A"].index
print("produits A en 2023 :", len(a23), "| encore A en 2025 :", int(global_abc.reindex(a23).eq("A").sum()), "(", round(global_abc.reindex(a23).eq("A").mean() * 100, 1), "%)")
```
<!--sortie-->
```text
produits A en 2023 : 55 | encore A en 2025 : 54 ( 98.2 %)
```

**Corrigé 8.5.**

```python
abc_marge = O.classes_abc(l25.groupby("id_produit")["marge"].sum())
a_ca, a_m = set(global_abc[global_abc == "A"].index), set(abc_marge[abc_marge == "A"].index)
print("A en CA :", len(a_ca), "| A en marge :", len(a_m), "| communs :", len(a_ca & a_m))
print("produits A en marge dans la Papeterie :", int(sum(cat_de[p] == "Papeterie" for p in a_m)))
```
<!--sortie-->
```text
A en CA : 56 | A en marge : 54 | communs : 50
produits A en marge dans la Papeterie : 0
```

**Corrigé 8.6.**

```python
l25b = l25.merge(cmd[["id_commande", "date_commande"]], on="id_commande")
sem = l25b.assign(semaine=l25b["date_commande"].dt.isocalendar().week).groupby(["id_produit", "semaine"])["quantite"].sum().unstack(fill_value=0)
cv_h = sem.std(axis=1) / sem.mean(axis=1)
print("coefficient de variation médian : mensuel", round(cv.median(), 2), "| hebdomadaire", round(cv_h.median(), 2))
print(pd.crosstab(global_abc.rename("ABC"), pd.cut(cv_h, [0, 0.45, 0.6, 10], labels=["X", "Y", "Z"], right=False).rename("XYZ hebdo")).to_string())
```
<!--sortie-->
```text
coefficient de variation médian : mensuel 0.48 | hebdomadaire 0.66
XYZ hebdo  X   Y   Z
ABC                 
A          1  19  36
B          0  10  22
C          0   3  29
```

À pas de temps plus fin, une même demande moyenne se répartit en peu d'unités par période : le **hasard de Poisson** (une semaine ordinaire compte tantôt 3, tantôt 7 ventes) fait alors varier fortement le coefficient. La classe XYZ dépend donc du pas de temps ; on la choisit en cohérence avec la fréquence de réapprovisionnement.

**Corrigé 8.7.** Écart-type robuste $=(8{,}5-3{,}5)/1{,}349\approx3{,}71$ ; écart standardisé $=(6{,}3-5{,}5)/3{,}71\approx0{,}22$. Un taux de retour **plus bas** est favorable : ici il est **plus haut** que la médiane (légèrement défavorable), mais l'écart est inférieur à un quart d'écart-type : on le dit « proche de la médiane ».

```python
print("écart-type robuste :", round((8.5 - 3.5) / 1.349, 2), "| écart standardisé :", round((6.3 - 5.5) / ((8.5 - 3.5) / 1.349), 2))
```
<!--sortie-->
```text
écart-type robuste : 3.71 | écart standardisé : 0.22
```

**Corrigé 8.8.**

```python
camp = pd.read_csv(os.path.join(D, "campagnes.csv"))
dep = camp.loc[camp["source"].isin(["payant", "reseaux"]), "depense"].sum()
nouveaux = cli[(pd.to_datetime(cli["date_inscription"]).dt.year == 2025) & cli["canal_acquisition"].isin(["Site", "Réseaux"])]
print("dépenses payant + réseaux :", round(dep), "€ | nouveaux clients Site ou Réseaux :", len(nouveaux), "| coût :", round(dep / len(nouveaux), 1), "€ | médiane du secteur : 18 €")
```
<!--sortie-->
```text
dépenses payant + réseaux : 64903 € | nouveaux clients Site ou Réseaux : 337 | coût : 192.6 € | médiane du secteur : 18 €
```

Avec cette définition, le coût est de **193 €**, donc **plus élevé** que les 115 € de l'indicateur large : on retire les courriels (peu coûteux), mais aussi la plupart des nouveaux clients (ceux qui s'inscrivent en Boutique). Aucune de ces deux définitions ne rapproche l'indicateur de 18 € : **l'écart avec le secteur n'est pas qu'une affaire de définition**, et le fichier ne dit pas quels nouveaux clients viennent réellement de la publicité. La bonne conduite : ajuster la définition, mesurer ce qui reste, et en conclure que la donnée manque pour trancher.

**Corrigé 8.9.**

```python
liv = pd.read_csv(os.path.join(D, "livraisons.csv"))
liv = liv[liv["date_commande"].str[:4] == "2025"]
duree = (pd.to_datetime(liv["date_livraison"]) - pd.to_datetime(liv["date_commande"])).dt.days
for j in (6, 8, 10):
    print(f"livrées en {j} jours au plus : {(duree <= j).mean() * 100:.1f} %")
```
<!--sortie-->
```text
livrées en 6 jours au plus : 73.5 %
livrées en 8 jours au plus : 96.3 %
livrées en 10 jours au plus : 99.7 %
```

La part de livraisons « à l'heure » passe de **73,5 %** (six jours) à **96,3 %** (huit jours) et **99,7 %** (dix jours), **sans livrer plus vite** : sans connaître le délai promis par le secteur, la comparaison avec une médiane de 92 % n'a pas de sens.
