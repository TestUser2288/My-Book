# Chapitre 4 : Analytique du risque et de l'assurance — exercices et applications

> 🧭 Ce cahier prolonge le chapitre 4 : on y **mesure** un portefeuille, on **refait à la main** un triangle de développement et une matrice de transition, on **compare des cohortes à âge égal**, on **rapproche** des chiffres de deux sources, on **ajuste** un modèle de fréquence, et l'on **choisit** un seuil d'alerte selon la charge d'un comité. Le cahier est autonome : il recharge ses données. Les données sont **simulées** ; l'assureur et la banque sont **fictifs**, et rien ici n'est un calcul réglementaire.

```python
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch04 as O
D = os.environ["DONNEES"]
d = O.charger(D)
bil = O.bilan_annuel(d)
print("polices :", len(d["pol"]), "| sinistres :", len(d["sin"]), "| prêts :", len(d["prets"]), "| lignes de suivi :", len(d["suivi"]))
print("S/P déclaré 2025 :", O.pct(bil.loc[2025, "sp_declare"], 1), "| frais supposés :", O.pct(O.FRAIS, 0))
```
<!--sortie-->
```text
polices : 30000 | sinistres : 5113 | prêts : 12000 | lignes de suivi : 229747
S/P déclaré 2025 : 82,4 % | frais supposés : 28 %
```

## Applications

### Application 4.1 — Fréquence, coût et ratio combiné par canal de vente (section 4.1)

**Objectif.** Reprendre l'analyse par segment du livre sur deux variables que le livre n'a pas utilisées : l'**usage** du véhicule et le **canal** de vente (Agence, Courtier, Web).

**Étape 1 — ajouter les colonnes.** Les tables d'exposition et de sinistres ne portent pas encore le canal ni l'usage ; on les ajoute depuis la table des polices.

```python
pol = d["pol"][["id_police", "usage", "canal"]]
dd = dict(d)                                   # une copie : on ne modifie pas d
dd["ex"] = d["ex"].merge(pol, on="id_police")
dd["sin"] = d["sin"].drop(columns=["usage"]).merge(pol, on="id_police")
print(len(dd["ex"]), len(dd["sin"]))
```
<!--sortie-->
```text
84875 5113
```

**Étape 2 — le tableau par segment.** On regarde, pour chaque modalité, l'exposition, la fréquence, le coût moyen, le S/P (coût ultime vrai sur primes acquises, 2021-2024) et le ratio combiné.

```python
for col in ["usage", "canal"]:
    t = O.table_sp(dd, col)
    print((t[["exposition", "nb", "frequence", "cout_moyen", "sp", "combine"]]).round(3).to_string(), "\n")
```
<!--sortie-->
```text
               exposition    nb  frequence  cout_moyen     sp  combine
usage                                                                 
Privé           44048.004  3049      0.069    4566.883  0.685    0.965
Professionnel    6085.823   493      0.081    4251.604  0.620    0.900 

          exposition    nb  frequence  cout_moyen     sp  combine
canal                                                            
Agence     22442.038  1582      0.070    4292.984  0.635    0.915
Courtier   15201.394  1075      0.071    4770.971  0.712    0.992
Web        12490.395   885      0.071    4632.964  0.703    0.983 
```

**Étape 3 — lire.** La fréquence est quasiment identique selon le canal (7,0 à 7,1 %), mais le coût moyen et le S/P diffèrent : les contrats de l'**Agence** ont un S/P de **63,5 %** (ratio combiné de 91,5 %), ceux du **Courtier** de **71,2 %** (99,2 %) et ceux du **Web** de **70,3 %** (98,3 %). Les contrats à usage **professionnel** ont un S/P plus bas (62,0 %) que ceux à usage privé (68,5 %).

**À vous.** Écrivez, en trois phrases, ce que vous diriez à la directrice **et** ce que vous refuseriez d'affirmer. Pensez à l'effectif de chaque ligne, aux gros sinistres (section 4.1.6) et au fait que les frais de 28 % sont **uniformes** par hypothèse (un contrat vendu par un courtier coûte en réalité une commission).

### Application 4.2 — Un triangle de développement à la main, puis en retrait (section 4.1)

**Objectif.** Refaire à la main la méthode chain ladder sur un petit triangle, puis la **tester en situation réelle** : refaire l'estimation avec les données telles qu'elles étaient fin 2023.

**Étape 1 — un petit triangle.** Quatre années de survenance, quatre délais, paiements cumulés en milliers d'euros.

```python
tri = pd.DataFrame([[100, 150, 175, 180], [110, 170, 200, np.nan], [130, 190, np.nan, np.nan], [150, np.nan, np.nan, np.nan]],
                   index=["A", "B", "C", "D"], columns=[0, 1, 2, 3], dtype=float)
f_, res = O.chain_ladder(tri)
print("facteurs :", np.round(f_, 4))
print(res.round(1).to_string())
print("provision totale :", round(res["a_payer"].sum(), 1))
```
<!--sortie-->
```text
facteurs : [1.5    1.1719 1.0286]
    paye  delai  facteur  ultime  a_payer
A  180.0      3      1.0   180.0      0.0
B  200.0      2      1.0   205.7      5.7
C  190.0      1      1.2   229.0     39.0
D  150.0      0      1.8   271.2    121.2
provision totale : 165.9
```

**Étape 2 — vérifier à la main.** Le facteur du délai 0 au délai 1 est (150 + 170 + 190) ÷ (100 + 110 + 130) = 510 ÷ 340 = **1,5**. Celui du délai 1 au délai 2 est (175 + 200) ÷ (150 + 170) = **1,172**, celui du délai 2 au délai 3 est 180 ÷ 175 = **1,029**. L'ultime de D vaut 150 × 1,5 × 1,172 × 1,029 = **271,2** : il reste donc 121,2 à payer pour D, et **165,9** au total.

**Étape 3 — le retrait.** On se met dans la situation de l'analyste de **fin 2023** : on ne garde du triangle réel que les paiements effectués jusqu'en 2023, sur les trois premières années de survenance et les trois premiers délais, et l'on compare l'ultime estimé à la vérité.

```python
inc, cum = O.triangle(d)
annee_pay = np.array(cum.index)[:, None] + np.array(cum.columns)[None, :]
cum23 = cum.where(annee_pay <= 2023).loc[[2021, 2022, 2023], [0, 1, 2]]
f23, r23 = O.chain_ladder(cum23)
vrai = O.vrai_ultime(d)
print("facteurs fin 2023 :", np.round(f23, 3))
print(pd.DataFrame({"ultime_estime": r23["ultime"].round(0), "ultime_vrai": vrai.loc[[2021, 2022, 2023]].round(0), "ecart_%": ((r23["ultime"] / vrai.loc[[2021, 2022, 2023]] - 1) * 100).round(1)}).to_string())
```
<!--sortie-->
```text
facteurs fin 2023 : [2.263 1.231]
      ultime_estime  ultime_vrai  ecart_%
an                                       
2021      1254779.0    1489094.0    -15.7
2022      3090926.0    3333803.0     -7.3
2023      4432960.0    4674311.0     -5.2
```

**À vous.** Avec trois délais seulement, la « queue » (les paiements après le délai 2) est ignorée : **l'estimation est trop basse** : de 16 % pour 2021 (la plus ancienne année, dont les derniers paiements sont ignorés), de 7 % pour 2022 et de 5 % pour 2023. Quel facteur de queue (supérieur à 1 appliqué à tous les ultimes) faudrait-il pour ramener l'ultime de 2022 à la vérité ? Pourquoi ne peut-on pas le calculer sur ce triangle en vie réelle ?

### Application 4.3 — Cohortes à âge égal, par segment (section 4.2)

**Objectif.** Appliquer la méthode des cohortes à âge égal non plus aux millésimes mais aux **segments** : les prêts aux particuliers et aux professionnels.

```python
cs = O.courbes_cohortes(d, par="segment")
print((cs.loc[[6, 12, 18, 24]] * 100).round(1).to_string())
```
<!--sortie-->
```text
segment   Particulier  Professionnel
age_mois                            
6                 1.7            2.2
12                5.2            6.0
18                8.4            9.7
24                9.7           11.8
```

```python
s = O.suivi_enrichi(d)
eff = s[s["age_mois"] == 12].groupby("segment").size()
print(eff.to_dict(), "prêts observés à 12 mois")
```
<!--sortie-->
```text
{'Particulier': 6368, 'Professionnel': 2058} prêts observés à 12 mois
```

**Lire.** À 12 mois, le défaut cumulé est de **5,2 %** pour les particuliers et de **6,0 %** pour les professionnels ; à 24 mois, de **9,7 %** et de **11,8 %**. La différence est visible, mais **modérée** : avec les effectifs observés (6 368 particuliers et 2 058 professionnels observés à 12 mois), l'intervalle de chaque courbe est large. **À vous** : avant de recommander un durcissement des conditions pour les professionnels, que calculeriez-vous pour dire si l'écart est significatif ?

### Application 4.4 — Matrice de transition et probabilités à horizon, par segment (section 4.2)

**Objectif.** Calculer la matrice de transition séparément pour les particuliers et pour les professionnels, puis la probabilité de défaut à 3 et à 6 mois selon la tranche de départ.

```python
for seg in ["Particulier", "Professionnel"]:
    n_, p_ = O.matrice_transition(d, "segment", seg)
    print(seg, "- effectifs de la ligne 30-59 :", int(n_.loc["30-59"].sum()))
    print((O.proba_defaut_horizon(n_, (3, 6)) * 100).round(1).to_string())
```
<!--sortie-->
```text
Particulier - effectifs de la ligne 30-59 : 1153
           3      6
0        0.4    1.5
1-29     3.4    4.6
30-59   42.9   43.5
60-89  100.0  100.0
Professionnel - effectifs de la ligne 30-59 : 377
           3      6
0        0.8    2.2
1-29     2.7    4.1
30-59   35.1   36.0
60-89  100.0  100.0
```

**Lire.** Pour un prêt en retard de 30 à 59 jours, la probabilité d'être en défaut dans les 6 mois est de **43,5 %** pour un particulier et de **36,0 %** pour un professionnel : les professionnels en retard **se redressent un peu plus souvent**, alors que leurs prêts à jour font défaut plus souvent (2,2 % contre 1,5 % à 6 mois). **À vous** : une banque qui fixe son provisionnement à partir d'une matrice unique pour les deux segments se trompe-t-elle d'un côté ou des deux ? Calculez l'écart de provisions pour 1 M€ de prêts en retard de 30 à 59 jours dans chaque segment avec un taux de perte de 45 % (hypothèse fictive).

### Application 4.5 — Rapprochement et jointure silencieuse (section 4.3)

**Objectif.** Reproduire une erreur de jointure, la **détecter** par un contrôle d'effectifs et de totaux, la **corriger**, puis faire un second rapprochement entre deux sources.

```python
ex = d["ex"][["id_police", "annee", "prime_acquise"]]
x = ex.merge(d["sin"][["id_police", "an"]], left_on=["id_police", "annee"], right_on=["id_police", "an"], how="left")
print("avant :", len(ex), round(ex["prime_acquise"].sum()), "| après :", len(x), round(x["prime_acquise"].sum()))
```
<!--sortie-->
```text
avant : 84875 34239469 | après : 85216 34555810
```

```python
nb = d["sin"].groupby(["id_police", "an"]).size().rename("nb").reset_index().rename(columns={"an": "annee"})
y = ex.merge(nb, on=["id_police", "annee"], how="left").fillna({"nb": 0})
print("corrigé :", len(y), round(y["prime_acquise"].sum()), "| égal à l'original :", round(y["prime_acquise"].sum()) == round(ex["prime_acquise"].sum()))
```
<!--sortie-->
```text
corrigé : 84875 34239469 | égal à l'original : True
```

**Un second rapprochement : les paiements.** Le montant payé par sinistre (`sinistres.csv`) et la liste des règlements (`paiements.csv`) décrivent la même chose.

```python
a, b = d["sin"]["montant_paye"].sum(), d["pay"]["montant"].sum()
print(round(a, 2), round(b, 2), "| écart :", round(a - b, 2))
reste = d["sin"][d["sin"]["statut"] == "Ouvert"]
print("sinistres ouverts :", len(reste), "| réserves restantes (M€) :", round(reste["reserve_dossier"].sum() / 1e6, 2))
```
<!--sortie-->
```text
15925640.24 15925640.24 | écart : 0.0
sinistres ouverts : 848 | réserves restantes (M€) : 8.98
```

**Lire.** La jointure naïve passe de 84 875 à 85 216 lignes et ajoute près de 0,3 M€ de primes (+0,9 %). Corrigée, elle retrouve exactement le total d'origine. Les deux sources de paiements concordent **à zéro près** ; les 848 dossiers ouverts portent encore **8,98 M€** de réserves, c'est-à-dire la partie « à payer » connue dossier par dossier (hors IBNR). **À vous** : pourquoi un contrôle « nombre de lignes avant = nombre de lignes après » aurait-il suffi ici, alors qu'il serait **faux** si l'on joignait volontairement une table de détail ?

### Application 4.6 — Un GLM de fréquence et la lecture d'un tarif (section 4.4)

**Objectif.** Ajuster un modèle de fréquence **sans** le bonus-malus, observer ce qui change pour l'âge, puis le comparer à la grille de tarif.

```python
import statsmodels.api as sm, statsmodels.formula.api as smf
base = O.police_annees(d)
f_sans = "nb ~ C(classe_age, Treatment('40-59 ans')) + C(zone, Treatment('A'))"
f_avec = f_sans + " + C(puissance) + C(usage, Treatment('Privé')) + np.log(bonus)"
fam = sm.families.Poisson()
m_sans = smf.glm(f_sans, data=base, family=fam, offset=np.log(base["exposition"])).fit()
m_avec = smf.glm(f_avec, data=base, family=fam, offset=np.log(base["exposition"])).fit()
r1 = O.relativites(m_sans, "classe_age", "40-59 ans")["rapport"]
r2 = O.relativites(m_avec, "classe_age", "40-59 ans")["rapport"]
print(pd.DataFrame({"sans bonus ni puissance": r1, "modèle complet": r2, "grille de tarif": [1.25, 1.19, 2.0, 1.0]}, index=r1.index).round(2).to_string())
```
<!--sortie-->
```text
             sans bonus ni puissance  modèle complet  grille de tarif
25-39 ans                       1.38            1.20             1.25
60 ans et +                     1.16            1.16             1.19
< 25 ans                        4.34            2.84             2.00
40-59 ans                       1.00            1.00             1.00
```

**Lire.** Sans les autres variables, l'effet des moins de 25 ans apparaît **de 4,3 fois** celui des 40-59 ans ; avec toutes les variables, il tombe à **2,8 fois**. L'écart s'explique : **les jeunes conducteurs ont un coefficient de bonus-malus plus élevé** (moins d'expérience), et le modèle sans bonus attribue à l'âge ce qui revient au bonus. La grille de tarif applique un coefficient d'âge de **2,0** : trop bas par rapport à 2,8, **à bonus égal** (le bonus-malus est tarifé à part : la comparaison porte sur l'effet propre de l'âge). **À vous** : le sens de la causalité peut-il être lu dans ces coefficients ? (Non : ce sont des associations, à caractéristiques observées égales.)

### Application 4.7 — Quel seuil d'alerte pour quel comité ? (section 4.5)

**Objectif.** Choisir le nombre de dossiers examinés chaque mois en comparant le **coût de l'examen** au **bénéfice des défauts évités**, à partir de la précision mesurée.

**Hypothèses (fictives).** Un examen coûte 120 € de temps de comité ; une action préventive évite le défaut dans 30 % des cas où le dossier **va** défaut, et un défaut évité fait économiser 4 000 € (perte moyenne). Ces nombres sont **inventés pour l'exercice** : une vraie banque les mesure.

```python
m, tr, te, coef = O.modele_alerte(d)
ks = [25, 50, 75, 100, 150, 200, 300, 400]
ev = O.evaluer_topk(te, ks)
ev["valeur_nette"] = ev.index * (ev["precision"] * 0.30 * 4000 - 120)
print(ev.round(2).to_string())
print("k optimal :", int(ev["valeur_nette"].idxmax()), "| valeur nette mensuelle :", round(ev["valeur_nette"].max()))
```
<!--sortie-->
```text
     precision  rappel  valeur_nette
k                                   
25        1.00    0.16      27000.00
50        1.00    0.31      53933.33
75        0.97    0.46      78733.33
100       0.88    0.54      94066.67
150       0.67    0.61     102066.67
200       0.52    0.64     101600.00
300       0.36    0.67      95133.33
400       0.28    0.69      87466.67
k optimal : 150 | valeur nette mensuelle : 102067
```

**Lire.** La valeur nette augmente tant que **le dossier supplémentaire examiné rapporte plus qu'il ne coûte**, c'est-à-dire tant que sa probabilité de défaut dépasse 120 ÷ (0,30 × 4 000) = **10 %**. Entre 150 et 200 dossiers, la précision marginale (environ 9 %) passe sous ce seuil et la valeur nette cesse de croître : le maximum est atteint autour de **150 dossiers par mois**. **À vous** : refaites le calcul avec un coût d'examen de 300 € puis de 60 € ; commentez la sensibilité du résultat à des hypothèses que la banque ne connaît qu'approximativement.

## Exercices

### Exercice 4.1 ⭐ — Exposition et fréquence (section 4.1.1)

Un assureur a 400 contrats couverts toute l'année, 100 couverts trois mois, et 50 couverts neuf mois. Il enregistre 42 sinistres pour un coût total de 168 000 €. Calculez l'exposition, la fréquence, le coût moyen et la prime pure ; donnez le S/P si la prime moyenne par année-police est de 400 €. Puis comparez la fréquence à celle que l'on obtiendrait en divisant par le nombre de contrats.

### Exercice 4.2 ⭐⭐ — Répondre à la directrice (section 4.1.5)

La directrice vous demande en une minute si 2025 est une bonne année. Vous disposez de trois estimations du S/P ultime de 2025 : 77,3 % (chain ladder), 82,4 % (dossiers) et 83,0 % (vérité, que vous ne connaissez pas). Rédigez la réponse en cinq lignes (réponse, chiffres, incertitude, limite, suite), sans utiliser la vérité.

### Exercice 4.3 ⭐⭐ — Choisir un seuil d'écrêtement (section 4.1.6)

Calculez le S/P des quatre zones avec un plafond de 20 000 €, 50 000 € et 100 000 € par sinistre. Pour chaque plafond, indiquez quelle zone paraît la plus mauvaise et de combien elle dépasse la moyenne des trois autres. Que dites-vous de la stabilité du classement ?

### Exercice 4.4 ⭐ — Taux brut contre âge égal (section 4.2.3)

Le millésime X compte 2 000 prêts suivis depuis 24 mois ; 160 sont en défaut, dont 40 dans les 6 premiers mois. Le millésime Y compte 2 000 prêts suivis depuis 6 mois ; 36 sont en défaut. (a) Calculez le taux brut de chaque millésime. (b) Calculez le taux à 6 mois du millésime X. (c) Lequel est le plus risqué ?

### Exercice 4.5 ⭐⭐ — Matrice de transition à la main (section 4.2.4)

Sur un mois, on a observé : parmi 1 000 prêts à jour, 950 le restent, 40 passent à « 1-29 jours » et 10 sortent (remboursés) ; parmi 100 prêts à « 1-29 jours », 70 reviennent à jour, 20 y restent et 10 passent à « 30-59 jours ». On suppose qu'un prêt à « 30-59 jours » passe en défaut avec une probabilité de 0,5 le mois suivant et revient à jour sinon. Écrivez la matrice (états : à jour, 1-29, 30-59, défaut, sortie ; les deux derniers sont absorbants) et calculez la probabilité qu'un prêt à jour soit en défaut dans deux, trois puis quatre mois.

### Exercice 4.6 ⭐⭐ — Concentration (section 4.2.5)

Trois portefeuilles ont des parts de 50 %, 30 %, 20 % ; 25 %, 25 %, 25 %, 25 % ; 70 %, 10 %, 10 %, 10 %. Calculez leur HHI et classez-les. À partir de quelle part le secteur Commerce de notre portefeuille de crédit (en gardant les proportions des autres secteurs) ferait-il dépasser un HHI de 0,35 ?

### Exercice 4.7 ⭐⭐ — Écrire un contrôle de rapprochement (section 4.3.3)

Voici les primes mensuelles (en k€) du système de gestion et de la comptabilité de janvier à juin :

| | Janv. | Févr. | Mars | Avr. | Mai | Juin |
|---|---|---|---|---|---|---|
| Gestion | 612 | 640 | 655 | 701 | 690 | 722 |
| Comptabilité | 612 | 640 | 648 | 701 | 689,5 | 722 |

Écrivez une fonction qui renvoie, pour chaque mois, l'écart, l'écart relatif et un verdict (« conforme » ou « à expliquer » avec une tolérance de 0,2 %), puis une phrase qui résume le trimestre.

### Exercice 4.8 ⭐⭐⭐ — Critiquer un paragraphe de rapport (sections 4.1.3, 4.1.6, 4.3)

Voici un paragraphe écrit par un analyste débutant :

> « *Les sinistres de 2025 sont en baisse de 28 % au quatrième trimestre, ce qui montre que nos mesures de prévention fonctionnent. La zone A est la plus mauvaise (S/P de 85 %) : il faut augmenter ses tarifs de 30 %. Le taux de couverture est de 67,35 %, très bon. Le chiffre de primes est de 8 846 669 €.* »

Relevez **au moins six défauts** (période incomplète, cause affirmée, S/P sans intervalle ni gros sinistre, taux de couverture sans définition, précision excessive, chiffre sans source ni rapprochement…) et réécrivez le paragraphe.

### Exercice 4.9 ⭐⭐ — Décomposer l'écart de S/P (section 4.4.1)

Comparez les zones D et A (2021-2024) : calculez les rapports de fréquence, de coût moyen, de prime moyenne et de S/P. Expliquez pourquoi la zone D, avec une fréquence presque deux fois plus forte, a un S/P **plus bas** que la zone A.

### Exercice 4.10 ⭐⭐⭐ — Sensibilité de la hausse de tarif aux frais (section 4.4.4)

La hausse moyenne de tarif nécessaire pour ramener le ratio combiné de 2025 à 100 % est S/P ÷ (1 − frais) − 1. Calculez-la pour des frais de 25 %, 28 % et 31 %, avec le S/P chain ladder de 2025 (77,3 %) puis avec celui de 2024 (72,4 %). Que concluez-vous sur la fiabilité d'une recommandation « +7 % » ?

### Exercice 4.11 ⭐⭐⭐ — Changer l'horizon de l'alerte (section 4.5.4)

Ajustez le modèle d'alerte avec un horizon de **3 mois** au lieu de 6. Comparez, pour 100 dossiers par mois, la précision, le rappel et le délai médian d'anticipation. Pourquoi le rappel monte-t-il alors que la précision baisse ?

### Exercice 4.12 ⭐⭐⭐ — Contrôles et justification (section 4.6.3)

Écrivez une fonction `controler_etat(ea, eb, ea_prec)` qui renvoie un tableau de contrôles : arithmétique (A04), complétude (aucune case vide), variation de A05 de plus de 5 points par rapport à l'état précédent. Testez-la par **injection d'erreur** (case vide, S/P gonflé) et rédigez la justification de la variation 2023 → 2024 en quatre éléments (fait, cause établie, cause probable, suite).

## Corrigés

### Corrigé 4.1

L'exposition est 400 + 100 × 0,25 + 50 × 0,75 = 400 + 25 + 37,5 = **462,5 années-police**. La fréquence est 42 ÷ 462,5 = **9,08 %** par année-police (et non 42 ÷ 550 = 7,6 %). Le coût moyen est 168 000 ÷ 42 = **4 000 €**, la prime pure 168 000 ÷ 462,5 = **363 €** (ou 0,0908 × 4 000), et le S/P 363 ÷ 400 = **90,8 %**.

```python
expo = 400 + 100 * 0.25 + 50 * 0.75
print(expo, round(42 / expo * 100, 2), 168000 / 42, round(168000 / expo, 1), round(168000 / expo / 400 * 100, 1), round(42 / 550 * 100, 1))
```
<!--sortie-->
```text
462.5 9.08 4000.0 363.2 90.8 7.6
```

### Corrigé 4.2

> **Réponse** : non, 2025 n'est pas une bonne année. **Chiffres** : même en complétant ce qui n'est pas connu, le S/P est de 77 à 82 % selon la méthode, au-dessus du seuil d'équilibre de 72 % ; avec 28 % de frais, le ratio combiné dépasse 100 % (105 à 110 %). **Incertitude** : les deux estimations diffèrent de 5 points, car le chain ladder ne voit que 2,6 M€ de paiements sur les 8 M€ attendus. **Limite** : notre chain ladder est simple et il manque encore des déclarations tardives, que l'on ne peut qu'estimer. **Suite** : suivre le S/P chaque trimestre et décomposer l'écart par nature de sinistre et par segment.

### Corrigé 4.3

```python
for cap in [20000, 50000, 100000]:
    sp = O.sp_par_segment(d, "zone", ecreter=cap) * 100
    autres = sp.drop(sp.idxmax()).mean()
    print(cap, sp.round(1).to_dict(), "| pire :", sp.idxmax(), "| écart à la moyenne des autres :", round(sp.max() - autres, 1), "points")
```
<!--sortie-->
```text
20000 {'A': 52.0, 'B': 43.8, 'C': 46.7, 'D': 46.0} | pire : A | écart à la moyenne des autres : 6.5 points
50000 {'A': 65.2, 'B': 50.4, 'C': 54.0, 'D': 56.0} | pire : A | écart à la moyenne des autres : 11.8 points
100000 {'A': 75.6, 'B': 55.4, 'C': 58.7, 'D': 63.4} | pire : A | écart à la moyenne des autres : 16.4 points
```

La zone A reste « la pire » quel que soit le plafond, mais **l'écart diminue** quand le plafond baisse (de 16,4 points avec 100 000 € à 6,5 points avec 20 000 € ; le S/P de A passe de 85 % brut à 52 %) : une partie de la différence vient de **quelques gros sinistres**. Le classement des trois autres zones est **instable** : C et D échangent leurs places quand le plafond tombe à 20 000 €, et les écarts entre B, C et D sont de quelques points seulement. On conclut qu'il y a peut-être un effet de la zone A, mais qu'il faut un intervalle (section 4.1.6) avant de recommander une hausse de tarif.

### Corrigé 4.4

(a) Taux brut : X, 160 ÷ 2 000 = **8,0 %** ; Y, 36 ÷ 2 000 = **1,8 %**. (b) À 6 mois, X : 40 ÷ 2 000 = **2,0 %**. (c) À âge égal (6 mois), X est à 2,0 % et Y à 1,8 % : **presque identiques** ; l'écart brut (8,0 % contre 1,8 %) vient uniquement de la durée d'observation. Il serait imprudent de dire que Y est quatre fois meilleur.

### Corrigé 4.5

La matrice (lignes : à jour, 1-29, 30-59, défaut, sortie) est :

| de \ vers | à jour | 1-29 | 30-59 | défaut | sortie |
|---|---|---|---|---|---|
| à jour | 0,95 | 0,04 | 0 | 0 | 0,01 |
| 1-29 | 0,70 | 0,20 | 0,10 | 0 | 0 |
| 30-59 | 0,50 | 0 | 0 | 0,50 | 0 |
| défaut | 0 | 0 | 0 | 1 | 0 |
| sortie | 0 | 0 | 0 | 0 | 1 |

Pour être en défaut, un prêt à jour doit passer par « 1-29 » puis « 30-59 » puis « défaut » : il faut **au moins trois mois**. À deux mois, la probabilité est donc **nulle** ; à trois mois, elle vaut 0,04 × 0,10 × 0,5 = **0,2 %** ; à quatre mois, la probabilité monte à **0,43 %**, car des chemins plus longs s'ajoutent (un mois de plus à jour, ou un mois de plus en retard léger).

```python
P = np.array([[0.95, 0.04, 0.00, 0.00, 0.01],
              [0.70, 0.20, 0.10, 0.00, 0.00],
              [0.50, 0.00, 0.00, 0.50, 0.00],
              [0.00, 0.00, 0.00, 1.00, 0.00],
              [0.00, 0.00, 0.00, 0.00, 1.00]])
print([round(float(np.linalg.matrix_power(P, h)[0, 3]) * 100, 3) for h in (1, 2, 3, 4)])
```
<!--sortie-->
```text
[0.0, 0.0, 0.2, 0.43]
```

### Corrigé 4.6

Le HHI du premier portefeuille est 0,25 + 0,09 + 0,04 = **0,38** ; celui du deuxième, 4 × 0,0625 = **0,25** ; celui du troisième, 0,49 + 3 × 0,01 = **0,52**. Par concentration croissante : deuxième, premier, troisième. Pour notre portefeuille de crédit, on fait varier la part *x* du Commerce en gardant les proportions relatives des autres secteurs.

```python
conc = O.concentration(d, "2025-06-01")
autres = conc.drop("Commerce") / conc.drop("Commerce").sum()
grille = np.linspace(0.16, 0.90, 741)
hh = np.array([O.hhi(np.append(autres.to_numpy() * (1 - x), x)) for x in grille])
for x in [0.163, 0.30, 0.50, 0.60]:
    print(x, round(O.hhi(np.append(autres.to_numpy() * (1 - x), x)), 3))
print("HHI >= 0,35 à partir d'une part de Commerce de", round(float(grille[np.argmax(hh >= 0.35)]), 2))
```
<!--sortie-->
```text
0.163 0.298
0.3 0.28
0.5 0.347
0.6 0.422
HHI >= 0,35 à partir d'une part de Commerce de 0.51
```

Avec 16,3 % de Commerce, le HHI est de 0,30. Il **descend** d'abord (minimum de 0,28 autour de 30 %), parce que Commerce se rapproche de la taille des autres secteurs, puis **remonte** : il dépasse 0,35 à partir d'une part d'environ **51 %** de l'encours dans un seul secteur. La concentration n'est donc pas préoccupante tant que ce secteur reste loin de la moitié du portefeuille, mais le HHI ne dit **rien** de la solidité du secteur lui-même (section 4.2.6).

### Corrigé 4.7

```python
gest = np.array([612, 640, 655, 701, 690, 722.0])
compt = np.array([612, 640, 648, 701, 689.5, 722.0])

def rapprocher(g, c, tol=0.002):
    t = pd.DataFrame({"gestion": g, "compta": c}, index=["janv", "févr", "mars", "avr", "mai", "juin"])
    t["ecart"] = t["gestion"] - t["compta"]
    t["ecart_rel"] = t["ecart"] / t["compta"]
    t["verdict"] = np.where(t["ecart_rel"].abs() <= tol, "conforme", "à expliquer")
    return t

r = rapprocher(gest, compt)
print(r.assign(ecart_rel=(r["ecart_rel"] * 100).round(2)).to_string())
print(f"{(r['verdict'] == 'conforme').sum()} mois sur 6 conformes ; à expliquer : {', '.join(r.index[r['verdict'] != 'conforme'])}")
```
<!--sortie-->
```text
      gestion  compta  ecart  ecart_rel      verdict
janv    612.0   612.0    0.0       0.00     conforme
févr    640.0   640.0    0.0       0.00     conforme
mars    655.0   648.0    7.0       1.08  à expliquer
avr     701.0   701.0    0.0       0.00     conforme
mai     690.0   689.5    0.5       0.07     conforme
juin    722.0   722.0    0.0       0.00     conforme
5 mois sur 6 conformes ; à expliquer : mars
```

Quatre mois sont conformes à l'euro près, **mai** l'est avec un écart de 0,07 % (sous la tolérance de 0,2 %) et **mars** est à expliquer : 7 k€ d'écart (1,08 %). La phrase du trimestre : « *Cinq mois sur six concordent avec la comptabilité ; mars présente un écart de 7 k€ (1,1 %) à justifier avant publication.* »

### Corrigé 4.8

**Défauts.** (1) Le recul de 28 % du quatrième trimestre compare un trimestre **incomplet** (déclarations tardives) à un trimestre complet. (2) « Nos mesures de prévention fonctionnent » est une **cause affirmée sans preuve**. (3) Le S/P de 85 % de la zone A est donné **sans effectif, sans intervalle** et sans dire qu'il est dominé par un très gros sinistre. (4) La recommandation « +30 % » découle de ce chiffre fragile et ne dit rien de la **réaction du marché**. (5) Le taux de couverture n'a ni **définition**, ni **date**, ni mention des **hypothèses de provisionnement**, et son jugement « très bon » n'a pas de référence ; (6) la précision à deux décimales (67,35 %) est **excessive** pour une estimation. (7) Le chiffre de primes n'a ni **définition** (acquises ? émises ?), ni **période**, ni **rapprochement**.

> *Le nombre de sinistres déclarés du quatrième trimestre 2025 (339) est inférieur à celui du troisième (468), mais ce recul reflète surtout le retard de déclaration (21 % des sinistres sont déclarés plus de 30 jours après) ; il ne dit rien de la prévention. Le S/P 2021-2024 de la zone A est le plus élevé (85 %), mais il repose sur un petit nombre de gros dossiers : plafonné à 50 000 € par sinistre, il est de 65 % (intervalle à 90 % de 58 à 73 %). Nous ne recommandons pas de hausse avant d'avoir étudié les gros sinistres. Au 30 juin 2025, le taux de couverture (provisions ÷ créances douteuses, avec des taux de provisionnement d'exemple) est d'environ 67 %. Les primes acquises 2024 du système de gestion sont de 8,85 M€ et concordent avec la comptabilité à 0,9 % près, écart expliqué par six régularisations de janvier 2025.*

### Corrigé 4.9

```python
t = O.table_sp(d, "zone")
t["prime_moy"] = t["primes"] / t["exposition"]
a, z = t.loc["A"], t.loc["D"]
print({k: round(float(z[c] / a[c]), 2) for k, c in [("fréquence", "frequence"), ("coût moyen", "cout_moyen"), ("prime", "prime_moy"), ("S/P", "sp")]})
```
<!--sortie-->
```text
{'fréquence': 1.83, 'coût moyen': 0.85, 'prime': 1.96, 'S/P': 0.8}
```

La zone D a **1,83 fois** la fréquence de la zone A, mais un coût moyen **plus faible** (×0,85) et une prime moyenne **1,96 fois** plus élevée : le S/P est donc **0,80 fois** celui de A. Deux raisons : le tarif suit bien la fréquence (le coefficient de zone D est proche du risque réel), et le coût moyen de la zone A est **tiré vers le haut** par quelques gros dossiers (section 4.1.6). La comparaison de S/P bruts désigne la mauvaise zone, la décomposition le montre.

### Corrigé 4.10

```python
for sp_ in (0.773, 0.724):
    print("S/P", sp_, {int(fr * 100): round((sp_ / (1 - fr) - 1) * 100, 1) for fr in (0.25, 0.28, 0.31)})
print("avec le S/P vrai 2025 (83,0 %) et 28 % de frais :", round((0.830 / 0.72 - 1) * 100, 1))
```
<!--sortie-->
```text
S/P 0.773 {25: 3.1, 28: 7.4, 31: 12.0}
S/P 0.724 {25: -3.5, 28: 0.6, 31: 4.9}
avec le S/P vrai 2025 (83,0 %) et 28 % de frais : 15.3
```

Avec le S/P de 2025 (77,3 %), la hausse nécessaire va de **3,1 %** (frais de 25 %) à **12,0 %** (frais de 31 %), et elle est de **7,4 %** à 28 %. Avec le S/P de 2024, elle va de −3,5 % à +4,9 %. Avec le S/P vrai de 2025 (que l'on ne connaît pas), elle serait de **15,3 %**. La recommandation « +7 % » dépend donc de trois choix (le S/P retenu, l'estimation de ce S/P, l'hypothèse de frais) : on présente une **fourchette** (de 3 à 15 %) en expliquant ses déterminants, pas un chiffre unique.

### Corrigé 4.11

```python
m3, tr3, te3, c3 = O.modele_alerte(d, horizon=3)
e3, e6 = O.evaluer_topk(te3, (100,)), O.evaluer_topk(te, (100,))
print("cas positifs :", O.pct(te3["y"].mean(), 1), "contre", O.pct(te["y"].mean(), 1))
print("horizon 3 mois :", (e3 * 100).round(0).to_dict("records")[0], "| horizon 6 mois :", (e6 * 100).round(0).to_dict("records")[0])
print("délai médian d'anticipation :", O.delai_anticipation(te3).median(), "mois contre", O.delai_anticipation(te).median())
```
<!--sortie-->
```text
cas positifs : 1,2 % contre 2,4 %
horizon 3 mois : {'precision': 60.0, 'rappel': 71.0} | horizon 6 mois : {'precision': 88.0, 'rappel': 54.0}
délai médian d'anticipation : 3.0 mois contre 4.0
```

Avec un horizon de 3 mois, la précision à 100 dossiers tombe à **60 %** (contre 88 %) et le rappel monte à **71 %** (contre 54 %). La cible est plus **rare** (1,2 % des lignes contre 2,4 %) : il y a deux fois moins de cas positifs, donc 100 dossiers suffisent à en attraper une plus grande part (rappel plus élevé), mais le comité examine aussi des dossiers qui feront défaut **plus tard** (qui comptent désormais comme des erreurs), d'où une précision plus basse. Le délai d'anticipation médian est naturellement plus court (3 mois au plus). **Le choix de l'horizon est un choix de gestion** : plus il est court, plus l'alerte est précise sur ce qui est imminent et moins elle donne de temps pour agir.

### Corrigé 4.12

```python
def controler_etat(ea, eb, ea_prec):
    v = ea["valeur"]
    return pd.Series({
        "A04 = A01 - A02 - A03": bool(abs(v["A04"] - (v["A01"] - v["A02"] - v["A03"])) < 1),
        "aucune case vide": bool(ea["valeur"].notna().all() and eb["valeur"].notna().all()),
        "variation de A05 <= 5 points": bool(abs(v["A05"] - ea_prec.loc["A05", "valeur"]) * 100 <= 5)})

ea, eb, ea0 = O.etat_assureur(d, 2024), O.etat_banque(d), O.etat_assureur(d, 2023)
print("état réel contre 2023 :", controler_etat(ea, eb, ea0).to_dict())
print("état contre lui-même  :", controler_etat(ea, eb, ea).to_dict())
vide = ea.copy(); vide.loc["A02", "valeur"] = np.nan
gonfle = ea.copy(); gonfle.loc["A05", "valeur"] *= 1.2
print("case vide  :", controler_etat(vide, eb, ea).to_dict())
print("S/P gonflé :", controler_etat(gonfle, eb, ea).to_dict())
```
<!--sortie-->
```text
état réel contre 2023 : {'A04 = A01 - A02 - A03': True, 'aucune case vide': True, 'variation de A05 <= 5 points': False}
état contre lui-même  : {'A04 = A01 - A02 - A03': True, 'aucune case vide': True, 'variation de A05 <= 5 points': True}
case vide  : {'A04 = A01 - A02 - A03': False, 'aucune case vide': False, 'variation de A05 <= 5 points': True}
S/P gonflé : {'A04 = A01 - A02 - A03': True, 'aucune case vide': True, 'variation de A05 <= 5 points': False}
```

Sur l'état réel comparé à 2023, deux contrôles passent et **la variation de A05 échoue** (+7,2 points) : c'est le comportement attendu, car il faut commenter. Comparé à **lui-même**, l'état passe tous les contrôles, ce qui donne une référence propre pour l'injection d'erreurs. Avec une **case vide**, « aucune case vide » et « A04 » échouent ; avec un **S/P gonflé de 20 %**, « variation » échoue (+14,5 points). Les contrôles **fonctionnent**. La justification : *fait* : le S/P ultime passe de 65,3 % à 72,4 % (+7,2 points) ; *cause établie* : la hausse vient du coût moyen estimé (4 305 € à 4 976 €, +15,6 %), la fréquence restant stable (7,2 % puis 7,0 %) et la prime moyenne augmentant de 2,1 % ; *cause probable* : une inflation des coûts supérieure à la revalorisation du tarif (à confirmer avec la direction des sinistres) ; *suite* : décomposer l'écart par nature de sinistre et par segment avant le prochain comité.
