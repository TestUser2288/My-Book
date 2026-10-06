# Chapitre 1 : Risque de crédit et scoring

> « Prêter, c'est parier sur l'avenir d'une personne avec l'argent de quelqu'un d'autre. Le score est la façon d'écrire ce pari. »

Les volumes précédents vous ont appris à **construire et à valider** des modèles prédictifs. Ce volume les met au service d'un métier particulier : **mesurer des risques qui se paient en euros**, par une banque qui prête et par une mutuelle qui assure. Le premier de ces risques est le plus ancien et le mieux formalisé : celui qu'un emprunteur **ne rembourse pas**. C'est le **risque de crédit**.

Un établissement de crédit décide chaque jour des centaines ou des milliers de dossiers : accorder ou refuser, à quel taux, avec quelle limite. Il ne peut pas les examiner un par un ; il a besoin d'une **règle** qui transforme les informations d'un dossier en un nombre, le **score**, et d'une règle qui transforme ce nombre en décision. Cette règle doit être **efficace** (elle sépare bien les bons des mauvais payeurs), **stable** (elle ne s'effondre pas quand la clientèle change), **explicable** (on sait dire à un client pourquoi il est refusé, et au régulateur pourquoi le modèle est juste) et **calibrée** (quand elle annonce 3 % de défaut, il y a environ 3 % de défauts). Les trois premières sections du chapitre suivent ce fil : on **construit une grille de score** (1.1), on la **compare à des modèles plus souples** (1.2), puis on **mesure ce qu'elle vaut** avec les indicateurs du métier (1.3), le Gini, le KS et la courbe ROC. Trois sections facultatives prolongent le travail vers ce que la comptabilité et la réglementation réclament : le **WOE et l'IV** pour discrétiser proprement (1.4), les **pertes de crédit attendues** de la norme IFRS 9 avec leurs trois composantes PD, LGD et EAD (1.5), et les **matrices de migration** des notes (1.6).

> 🧭 **Ce que le chapitre suppose.** La régression logistique (volume II, section 2.2), la validation et les métriques (volume III, chapitres 1 et 5, en particulier 5.1 et 5.2 pour l'AUC et la calibration) et la notion de dérive (volume IV, section 4.7). Nous rappelons l'essentiel au moment utile.

## Le chemin de ce chapitre

| Section | Question | Idée centrale |
|---|---|---|
| 1.1 | Comment fabrique-t-on une grille de score ? | Cadrer, découper en classes, estimer sur les WOE, convertir en points |
| 1.2 | Une grille vaut-elle un modèle plus souple ? | Sur ces données, presque : la forme des effets compte plus que l'algorithme |
| 1.3 | Comment mesure-t-on un score ? | Gini, KS, calibration, stabilité, incertitude |
| ➕ 1.4 | Comment discrétiser sans se tromper ? | WOE, IV, regroupements monotones, pièges |
| ➕ 1.5 | Combien le portefeuille va-t-il perdre ? | PD × LGD × EAD, étapes IFRS 9, scénarios |
| ➕ 1.6 | Comment les notes évoluent-elles ? | Matrices de transition, cycle, PD sur plusieurs années |

## Les données du chapitre

> 📦 **Données simulées.** Tous les fichiers de ce chapitre sont **simulés** (graines fixes, générateur `build/donnees5.py`), sauf un détour sur un jeu **réel** en section 1.3 (clients d'une carte de crédit, source UCI, licence CC0, Yeh et Lien, 2009). La banque est fictive. Comme les données sont simulées, nous connaissons la **vérité programmée** et la révélons quand elle éclaire une étude : en vraie vie, personne ne vous la donne.

- `credits_conso.csv` : **40 000 prêts à la consommation**, décrits **à la souscription**, avec l'issue observée douze mois plus tard (`defaut_12m`, environ 6 %).
- `recouvrements.csv` : 6 000 prêts **entrés en défaut**, avec la perte réellement subie (section 1.5).
- `revolving_defauts.csv` : 8 000 lignes de crédit renouvelable en défaut (section 1.5).
- `portefeuille_ifrs9.csv` : 20 000 prêts en cours, avec leur probabilité de défaut à l'origine et aujourd'hui (section 1.5).
- `taux_defaut_macro.csv` : 80 trimestres de conjoncture et de taux de défaut du portefeuille (sections 1.3 et 1.5).
- `notations_panel.csv` : 5 000 emprunteurs notés chaque année pendant dix ans (section 1.6).


Voici l'allure d'un dossier : onze informations connues **au moment de la demande**, et l'issue.

```python
print(tr.drop(columns="id_credit").head(3).T.to_string())
```
<!--sortie-->
```text
                       37690      20231    31011
age                       30         21       66
revenu_annuel        15010.0    25950.0  41940.0
anciennete_emploi        7.8        0.8      8.4
logement             heberge  locataire  heberge
objet                travaux    travaux     auto
montant              18900.0     4000.0   6000.0
duree_mois                36         60       60
taux_endettement       0.519       0.06    0.331
nb_incidents_12m           0          0        0
anciennete_relation     12.7        7.1      4.4
defaut_12m                 0          0        0
```

Les variables sont celles d'un dossier de crédit à la consommation : l'âge, le revenu annuel, l'ancienneté dans l'emploi, le logement, l'objet du prêt, le montant et la durée, le **taux d'endettement** (charges mensuelles, mensualité comprise, rapportées au revenu), le nombre d'incidents de paiement des douze derniers mois, l'ancienneté de la relation avec la banque. Deux variables ont des **valeurs manquantes** : le revenu (5 %) et l'ancienneté dans l'emploi (7 %). Nous verrons que le second manque **plus souvent chez les emprunteurs risqués** : un manquant n'est pas neutre.

Le jeu est découpé **une fois pour toutes** en un échantillon de **développement** (70 %, 28 000 prêts) et un échantillon de **test** (30 %, 12 000 prêts), tous deux avec la même proportion de défauts. On n'y touche pas pendant la construction (classes, coefficients) ; il sert ensuite à mesurer des candidats **fixés d'avance**, sans réglage fait en le regardant.


> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : toutes les applications partent de ces fichiers ; commencez par l'application 1.1.


## 1.1 Construction d'une grille de score

Cette section déroule, dans l'ordre où le fait un analyste de crédit, la fabrication d'une **grille de score** : cadrer le problème, découper chaque variable en classes, estimer les poids, puis traduire le résultat en points que l'on sait lire et auditer. C'est un très vieux métier de la statistique appliquée, et il en reste une pratique solide : une grille est **simple à expliquer**, **facile à contrôler** et **difficile à faire dérailler**.

### 1.1.1 Un score, une décision

Un **score** est un nombre attaché à un dossier, construit pour que l'ordre des nombres reproduise l'ordre des risques. Par convention de ce chapitre, **un score élevé signale un dossier sûr**. Le score ne décide rien par lui-même ; il alimente trois décisions :

- **accorder ou refuser** : on fixe un **seuil** (*cut-off*) en dessous duquel le dossier est refusé ou renvoyé à un examen humain ;
- **fixer le prix et la limite** : un dossier plus risqué paie un taux plus élevé ou reçoit un montant plus faible, parce que la banque doit couvrir ses pertes attendues (section 1.5) ;
- **suivre le portefeuille** : regroupés en classes de risque (une **échelle maîtresse**, *master scale*), les scores donnent des **probabilités de défaut** par classe, que la comptabilité et la réglementation réutilisent (chapitre 4).

Le vocabulaire est celui du métier : un client qui fait défaut dans la fenêtre d'observation est un **mauvais** (*bad*), les autres sont des **bons** (*good*). Les **cotes** (*odds*) d'un groupe sont le rapport bons sur mauvais ; une cote de 50 contre 1 correspond à 2 % de mauvais. Un score est en fait une **cote écrite en points**, et c'est ce qui rend la grille lisible : nous y revenons en 1.1.5.

> 💡 **Pourquoi une grille plutôt qu'un modèle plus puissant ?** Parce que le gain de précision d'un algorithme souple est souvent faible devant ce que coûte son opacité : il faut pouvoir justifier un refus à un client, montrer à l'autorité de contrôle que le modèle est sensé, et le surveiller avec des outils éprouvés. La section 1.2 mesure ce gain **sur nos données** au lieu de le supposer.

### 1.1.2 Cadrer le problème

Avant la moindre régression, quatre décisions de cadrage déterminent ce que le score *veut dire*.

**La population.** On modélise **ceux sur qui la décision s'applique** : ici, des particuliers qui demandent un prêt à la consommation. On exclut ce qui relève d'un autre traitement (prêts aux entreprises, dossiers frauduleux avérés, produits très différents). Mélanger des populations qui n'obéissent pas aux mêmes lois est la première cause de score décevant.

**La définition du défaut.** Elle est **conventionnelle** et doit être écrite noir sur blanc : par exemple, *un retard de paiement de 90 jours ou plus sur un montant significatif*, ou bien un événement qui montre que le client ne paiera sans doute pas (restructuration, procédure collective). Le choix a des effets sur tout : un seuil de 30 jours produit bien plus de « mauvais » (et plus de bruit), un seuil de 180 jours en produit moins et plus tard. Ici, `defaut_12m` vaut 1 si le prêt est tombé en défaut dans les douze mois qui suivent sa souscription.

**Les deux fenêtres.** Le score doit prédire l'avenir à partir de ce que l'on **sait à la date de la demande**. On distingue donc la **fenêtre d'observation** (le passé, d'où viennent les variables explicatives) et la **fenêtre de performance** (l'avenir, où l'on regarde si le défaut survient) :


![Les deux fenêtres d'un score de crédit : on décrit le client avec ce que l'on sait à la date de la demande, on mesure le défaut ensuite.](figures/ch01-fenetres.png)

La conséquence est une règle d'or contre la **fuite d'information** (volume III, section 1.1) : une variable calculée *après* la date de la demande, même un peu, n'a pas le droit d'entrer dans le score. Dans nos données, `nb_incidents_12m` compte les incidents des douze mois **précédant** la demande ; le nombre de retards du prêt lui-même, lui, serait une fuite évidente.

⚠️ **Le piège de la maturité.** Un prêt souscrit il y a six mois n'a pas encore eu douze mois pour faire défaut : sa « non-défaillance » est une observation **tronquée**. Dans une vraie base, on ne garde que des prêts dont la fenêtre de performance est complète, ou on corrige. Nos données sont déjà arrêtées à douze mois pour tous.

**Les échantillons.** On découpe en développement, validation (réglages) et test. Quand les dossiers sont **datés**, on valide aussi **hors période** (*out-of-time*) : développement sur des souscriptions anciennes, test sur les plus récentes, parce que le but est de prédire l'avenir et non des dossiers mélangés avec ceux du passé. Notre fichier ne porte pas de date : nous avons donc procédé par un découpage aléatoire stratifié, et la section 1.3 montre autrement ce que l'écoulement du temps fait à un score (la conjoncture).

### 1.1.3 Découper en classes

Une grille de score **ne prend pas l'âge brut** : elle regroupe les âges en **classes**. Le découpage en classes (*binning*) a quatre raisons d'être.

1. **Les effets sont rarement linéaires.** Le risque ne croît pas régulièrement avec l'âge : il est élevé chez les très jeunes, bas au milieu de la vie, un peu plus haut chez les plus âgés. Une classe laisse à chaque tranche son propre niveau de risque, sans imposer de forme.
2. **Les valeurs extrêmes perdent leur pouvoir de nuisance.** Un revenu de 4 millions d'euros tombe simplement dans la dernière classe.
3. **Les manquants ont une place.** On les range dans une classe à part, avec son propre risque (nous le verrons), au lieu de les imputer de façon arbitraire.
4. **Le résultat se lit.** « Entre 25 et 30 ans : 52 points » se discute avec un client et se contrôle par un auditeur.

Regardons le défaut observé, classe d'âge par classe d'âge, sur l'échantillon de développement :

```python
t_age = O.table_woe(tr["age"], tr["defaut_12m"], "age")
print(t_age[["effectif", "mauvais", "taux_defaut", "woe"]].round(3).to_string())
```
<!--sortie-->
```text
          effectif  mauvais  taux_defaut    woe
classe                                         
1: <25        2121      299        0.141 -0.950
2: 25-30      2127      149        0.070 -0.173
3: 30-40      7498      410        0.055  0.093
4: 40-55     12135      558        0.046  0.276
5: 55-65      3289      183        0.056  0.073
6: 65+         830       72        0.087 -0.408
```

Le taux de défaut passe de 14,1 % chez les moins de 25 ans à 4,6 % entre 40 et 55 ans, puis remonte à 8,7 % après 65 ans : une **courbe en U**. Il en va de même, d'une autre façon, pour le taux d'endettement, dont le risque reste modeste jusqu'à 40 % puis **s'envole** (37 % de défaut au-delà de 70 %) :


![Taux de défaut observé par classe (barres : intervalle à 95 %) : l'âge dessine un U, le taux d'endettement un coude.](figures/ch01-taux-par-classe.png)

Comment choisit-on les bornes ? Il n'y a pas de recette unique, mais des **règles de prudence** que le métier a stabilisées :

- chaque classe doit contenir **assez de monde** (au moins quelques pourcents de la population) **et assez de mauvais** (quelques dizaines au minimum), sinon son taux n'est que du bruit ;
- deux classes voisines doivent avoir des taux **nettement différents** (sinon on les fusionne) ;
- quand le sens économique l'impose (plus d'endettement, plus de risque), l'ordre des classes doit être **monotone** ; une forme en U comme celle de l'âge est admise quand on peut l'expliquer ;
- on regarde les **intervalles de confiance** (les barres de la figure) avant de croire à une différence ;
- on garde les classes **lisibles** : des bornes rondes, un nombre réduit de classes (de quatre à huit par variable).

Les bornes de ce chapitre ont été choisies à la main selon ces règles ; la section ➕ 1.4 montre comment les chercher de façon systématique.

### 1.1.4 Le poids de l'évidence et la régression

Une fois les classes tracées, on remplace chaque classe par un nombre qui résume son risque : le **poids de l'évidence** (*weight of evidence*, **WOE**). Pour une classe $j$,

$$\text{WOE}_j=\ln\frac{\text{part des bons dans la classe } j}{\text{part des mauvais dans la classe } j}=\ln\frac{B_j/B}{M_j/M},$$

où $B_j$ et $M_j$ sont les nombres de bons et de mauvais de la classe, $B$ et $M$ ceux de l'échantillon entier. Un WOE **positif** signale une classe plus sûre que la moyenne ; un WOE **négatif**, une classe plus risquée ; zéro, une classe moyenne. Calculons-le à la main pour les moins de 25 ans de notre échantillon : 299 mauvais et 1 822 bons, alors que l'échantillon compte 1 671 mauvais et 26 329 bons au total.

$$\text{WOE}_{<25}=\ln\frac{1\,822/26\,329}{299/1\,671}=\ln\frac{0{,}0692}{0{,}1789}=\ln 0{,}387\approx-0{,}95.$$

Ces jeunes emprunteurs pèsent 7 % des bons mais 18 % des mauvais. Le WOE est aussi la **différence de log-cotes** entre la classe et l'ensemble : $\text{WOE}_j=\ln(\text{cote}_j)-\ln(\text{cote globale})$, avec $\text{cote}_j=B_j/M_j$. C'est ce qui le rend si pratique : il est exprimé dans **la même unité que la régression logistique**, le logarithme d'une cote.

La grille s'obtient alors par une **régression logistique sur les WOE**. On prédit l'événement « bon » et chaque variable $k$ entre par le WOE de la classe où tombe le dossier :

$$\ln\frac{P(\text{bon})}{P(\text{mauvais})}=\alpha+\sum_{k=1}^{p}\beta_k\,\text{WOE}_k(x).$$

> 📐 **Pourquoi des coefficients proches de 1 ?** Si les $p$ variables étaient **indépendantes** conditionnellement au résultat bon/mauvais, la formule de Bayes donnerait exactement $\ln\frac{P(\text{bon}\mid x)}{P(\text{mauvais}\mid x)}=\ln\frac{P(\text{bon})}{P(\text{mauvais})}+\sum_k \text{WOE}_k(x)$ : tous les $\beta_k$ vaudraient 1 (c'est le **Bayes naïf**). En pratique, les variables sont corrélées (le revenu et le taux d'endettement partagent de l'information), la régression **corrige** cette redondance en abaissant certains coefficients. Un coefficient **négatif** serait un signal d'alarme : il traduirait une variable trop corrélée à une autre, ou des classes mal construites.

L'appel suivant fait tout cela : tables WOE, remplacement des variables par leurs WOE, régression logistique.

```python
from sklearn.linear_model import LogisticRegression
tables = O.tables_woe(tr)                      # une table WOE par variable (classes de O.BORNES)
W_tr = O.vers_woe(tr, tables)                  # chaque variable remplacée par le WOE de sa classe
lr = LogisticRegression(max_iter=2000).fit(W_tr, 1 - y_tr)     # on prédit « bon »
print(pd.Series(lr.coef_[0], index=W_tr.columns).round(2).to_string())
```
<!--sortie-->
```text
age                    0.85
taux_endettement       0.72
anciennete_emploi      0.80
revenu_annuel          0.65
montant                0.25
duree_mois             0.35
nb_incidents_12m       0.85
anciennete_relation    1.04
logement               1.01
objet                  0.98
```

Les coefficients vont de 0,25 pour le montant à 1,04 pour l'ancienneté de la relation : ils sont **tous positifs**, proches de 1 pour le logement (1,01), l'objet (0,98) et l'ancienneté de la relation, plus bas pour les variables qui se recoupent (le montant, la durée, le revenu, qui dépendent les uns des autres).

### 1.1.5 Des log-cotes aux points

La régression produit une **log-cote** $\ln(\text{bons}/\text{mauvais})$ par dossier. Il reste à l'écrire en **points**, pour qu'un score de 600 ait un sens. La convention du métier fixe deux nombres :

- un **score de base** associé à une **cote de base** (par exemple 600 points pour une cote de 50 bons contre 1 mauvais, soit 2 % de défaut) ;
- le **PDO** (*points to double the odds*) : le nombre de points qu'il faut ajouter pour **doubler la cote** (par exemple 20 points).

Le score est une fonction affine de la log-cote : $\text{Score}=\text{décalage}+\text{facteur}\times\ln(\text{cote})$. Les deux conditions donnent les deux constantes :

$$\text{facteur}=\frac{\text{PDO}}{\ln 2}=\frac{20}{0{,}6931}\approx28{,}85,\qquad \text{décalage}=600-28{,}85\times\ln 50\approx487{,}12.$$

Vérifions à la main : une cote de 50 donne $487{,}12+28{,}85\times3{,}912=600$ ; une cote de 100 donne $487{,}12+28{,}85\times4{,}605=620$, soit 20 points de plus : la cote a doublé, le score a gagné un PDO.

Comme la log-cote est une somme ($\alpha+\sum\beta_k\text{WOE}_k$), le score est une **somme de points par variable**. En répartissant l'intercept et le décalage également entre les $p$ variables, la classe $j$ de la variable $k$ reçoit

$$\text{points}_{jk}=\Bigl(\beta_k\,\text{WOE}_{jk}+\frac{\alpha}{p}\Bigr)\times\text{facteur}+\frac{\text{décalage}}{p}.$$

Pour retrouver une probabilité, on inverse : $\text{cote}=\exp\bigl((\text{Score}-\text{décalage})/\text{facteur}\bigr)$ et $\text{PD}=1/(1+\text{cote})$. Un score de 580 correspond à une cote de $\exp(92{,}88/28{,}85)\approx25$, soit une probabilité de défaut de $1/26\approx3{,}8\ \%$.


### 1.1.6 Lire la carte de score

Le résultat est la **carte de score** : un tableau classe par classe. Voici deux de ses variables, avec le défaut observé (pour mémoire), le WOE et les points :

```python
carte = G.points_classes()
print(carte[carte.variable.isin(["age", "nb_incidents_12m"])].drop(columns="variable").to_string(index=False))
```
<!--sortie-->
```text
  classe  effectif  taux_defaut    woe  points
  1: <25      2121       0.1410 -0.950    33.3
2: 25-30      2127       0.0701 -0.173    52.4
3: 30-40      7498       0.0547  0.093    58.9
4: 40-55     12135       0.0460  0.276    63.4
5: 55-65      3289       0.0556  0.073    58.4
  6: 65+       830       0.0867 -0.408    46.6
    1: 0     21066       0.0439  0.325    64.6
    2: 1      5964       0.0942 -0.494    44.5
   3: 2+       970       0.1907 -1.313    24.3
```

On y lit d'un coup d'œil ce que la grille pense : les moins de 25 ans reçoivent 33 points, contre 63 pour les 40–55 ans. Trente points d'écart valent un PDO et demi, donc une cote **environ 2,8 fois** meilleure ($2^{30/20}\approx2{,}8$). Un seul incident dans l'année coûte 20 points par rapport à aucun ; deux incidents ou plus, 40 points. La carte complète compte une cinquantaine de lignes ; le cahier (application 1.1) la construit en entier.

L'**amplitude** des points d'une variable (le plus haut moins le plus bas) mesure son **influence** dans la grille :

```text
variable
taux_endettement       55.7
nb_incidents_12m       40.3
anciennete_emploi      35.4
revenu_annuel          30.4
age                    30.1
anciennete_relation    27.0
logement               16.5
objet                   8.0
duree_mois              6.6
montant                 6.2
```

Le taux d'endettement domine (56 points d'écart), suivi des incidents (40 points), de l'ancienneté dans l'emploi (35), du revenu (30) et de l'âge (30) ; le montant, la durée et l'objet pèsent peu. Voici maintenant **trois dossiers du jeu de test**, un très sûr, un médian, un très risqué : on additionne simplement les points de la classe où tombe chaque variable.

```text
           variable             sûr            médian           risqué
                age      30-40 : 59        30-40 : 59         <25 : 33
   taux_endettement       <0.2 : 66      0.3-0.4 : 59     0.4-0.5 : 51
  anciennete_emploi        10+ : 75          1-3 : 46         3-6 : 52
      revenu_annuel     50000+ : 73     manquant : 54 40000-50000 : 67
            montant 7000-12000 : 57   7000-12000 : 57 12000-20000 : 55
         duree_mois      24-36 : 59        24-36 : 59       36-48 : 57
   nb_incidents_12m          0 : 65            0 : 65           1 : 44
anciennete_relation       6-12 : 66          3-6 : 59         1-3 : 53
           logement  locataire : 53 proprietaire : 66   locataire : 53
              objet      conso : 52         auto : 59       conso : 52
     TOTAL (points)             625               583              519
```


Les trois scores valent environ 625, 583 et 519 points : le dossier sûr cumule des classes favorables presque partout (une ancienneté de dix ans et plus dans l'emploi, un revenu supérieur à 50 000 €, un endettement inférieur à 20 %), le dossier risqué cumule un âge de moins de 25 ans, un incident de paiement et un endettement entre 40 et 50 %. Comme le score est une échelle de cotes, l'écart de 106 points entre le premier et le troisième représente $106/20=5{,}3$ PDO, soit une cote **environ 40 fois** plus favorable ($2^{5{,}3}\approx40$). Le dossier médian (583 points) correspond à une probabilité de défaut de 3,5 % environ.

### 1.1.7 Les dossiers refusés : l'inférence des rejets

Toute grille est construite sur les **dossiers acceptés**, ceux dont on connaît l'issue. Les dossiers refusés n'ont jamais été financés : on ne saura jamais s'ils auraient fait défaut. Or le score doit s'appliquer à **tous les demandeurs**, y compris à ceux que l'ancienne politique aurait refusés. C'est le problème de l'**inférence des rejets** (*reject inference*) : un échantillon **sélectionné** par la politique passée donne une image déformée de la population qui se présente.

Simulons-le, puisque nos données contiennent des dossiers que l'on aurait normalement refusés. Imaginons une ancienne politique qui refuse les taux d'endettement supérieurs à 50 % et les clients ayant plus d'un incident : elle accepte environ 88,5 % des demandeurs. Construisons la grille sur ces seuls acceptés, puis mesurons-la sur **tous** les demandeurs du test :

```text
grille construite sur  AUC sur tous  PD moyenne annoncée  défaut réel
  tous les demandeurs        0.7712               0.0593       0.0597
   les acceptés seuls        0.7156               0.0439       0.0597
```


La grille construite sur les acceptés **annonce 4,4 % de défaut** alors que la réalité est de 6,0 % : elle sous-estime le risque de la population complète d'un tiers, et son pouvoir de classement tombe (AUC de 0,716 contre 0,771). La raison est visible dans ses classes : puisque presque aucun dossier à fort endettement n'a été accepté, la classe des taux entre 50 et 60 % ne contient que **20 prêts**, aucun défaut, et reçoit un WOE **positif** (+0,66), comme si ces dossiers étaient plus sûrs que la moyenne. Le modèle n'a rien vu de ce qui s'est passé hors de la zone d'acceptation : il **extrapole** à vide.

Que peut-on faire ? Aucune méthode ne remplace une observation, mais on en connaît plusieurs :

- **Utiliser une information externe** : l'issue de ces demandeurs auprès d'*autres* prêteurs, obtenue par un bureau de crédit.
- **Parcelliser** (*parcelling*) : donner aux refusés une probabilité de défaut tirée de la grille des acceptés, majorée d'un facteur prudent, et les ajouter à l'échantillon avec un poids ; on suppose que les refusés **ressemblent** aux acceptés de score voisin, ce qui est exactement ce qui est en cause.
- **Repondérer** les acceptés pour qu'ils représentent la population complète, selon leur probabilité d'acceptation ; cela corrige peu quand certaines zones n'ont **aucun** accepté.
- **Accepter volontairement** un petit échantillon aléatoire de dossiers qui auraient été refusés, à coût contrôlé : c'est la seule voie qui fournit de vraies données, et elle a un prix réel pour la banque et des conséquences pour les clients concernés.

⚠️ **L'honnêteté impose de le dire.** L'inférence des rejets réduit un biais en faisant des hypothèses invérifiables ; elle ne le supprime pas. Une grille construite sur des acceptés doit être **surveillée** après la mise en production, quand la politique d'acceptation change, car c'est alors que la population change et que le biais apparaît.

> ✅ **À retenir.**
> - Un score est une **cote écrite en points** : $\text{Score}=\text{décalage}+\text{facteur}\cdot\ln(\text{bons}/\text{mauvais})$, avec facteur = PDO/ln 2.
> - Le cadrage (population, définition du défaut, fenêtres d'observation et de performance, découpage) décide de ce que le score veut dire ; la **fuite d'information** s'évite en ne gardant que ce que l'on sait à la date de la demande.
> - On **découpe en classes** (assez de monde, assez de mauvais, bornes lisibles, ordre monotone quand le sens économique l'exige), on remplace chaque classe par son **WOE**, puis on estime une **régression logistique** ; les coefficients proches de 1 correspondent au cas indépendant (Bayes naïf).
> - La carte de score est une **somme de points** par classe ; l'amplitude des points mesure l'influence d'une variable.
> - Les refusés manquent à l'échantillon : une grille construite sur les acceptés sous-estime le risque de la population qui se présente.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 et 1.2, exercices 1.1 à 1.3.


## 1.2 Modèles de prédiction du défaut

La grille de la section 1.1 est un modèle **volontairement contraint** : des classes, des effets additifs, des points. Les données d'aujourd'hui permettent des modèles bien plus souples, comme les arbres de gradient (volume III, section 2.4). Cette section pose la question qu'un comité de risque pose toujours : **que gagne-t-on à abandonner la grille, et que perd-on ?** Nous comparons trois candidats **fixés d'avance** sur le même échantillon de test, nous regardons **pourquoi** l'un l'emporte sur l'autre en nous appuyant sur la vérité programmée, puis nous traitons deux sujets propres au crédit : la **calibration** et les **motifs de refus**.

### 1.2.1 Trois candidats

- **La régression logistique « brute »** : les variables sont prises telles quelles (âge, taux d'endettement… en nombres), avec des indicateurs pour les manquants et des modalités pour les catégories. C'est la première chose qu'un statisticien essaie (volume II, section 2.2).
- **La grille de score** de la section 1.1 : classes, WOE, régression, points.
- **Un modèle de boosting** (LightGBM) : un ensemble d'arbres qui apprend lui-même les seuils et les interactions. On en examine deux versions, libre et **monotone** (nous y revenons en 1.2.3).

Les trois sont entraînés sur les mêmes 28 000 prêts et mesurés sur les mêmes 12 000 prêts de test. Aucun réglage n'a été fait en regardant le test ; les paramètres du boosting sont ceux d'un réglage modeste (300 petits arbres de huit feuilles, pas d'apprentissage de 0,03, au moins 200 prêts par feuille), choisis pour éviter le surapprentissage, non pour gagner un dixième de point.


La version du boosting contrainte demande que le risque **ne puisse que croître** avec le taux d'endettement et le nombre d'incidents, et **que décroître** avec le revenu, l'ancienneté dans l'emploi et l'ancienneté de la relation, pour que la forme du modèle reste défendable devant un auditeur :

```python
contraintes = {"taux_endettement": 1, "nb_incidents_12m": 1, "revenu_annuel": -1,
               "anciennete_emploi": -1, "anciennete_relation": -1}       # +1 : le risque ne peut que croître
mc = [contraintes.get(c, 0) for c in Xb_tr.columns]
gbm = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.03, num_leaves=8, min_child_samples=200, subsample=0.8,
                         subsample_freq=1, colsample_bytree=0.8, monotone_constraints=mc, random_state=0, verbose=-1)
gbm.fit(Xb_tr, y_tr)
```


### 1.2.2 Le verdict mesuré

Les mesures sont celles de la section 1.3 (AUC, Gini = 2·AUC − 1, KS) ; ici, lisons-les en gros.

```text
                             AUC   Gini     KS
logistique brute           0.762  0.524  0.396
grille de score            0.771  0.542  0.406
boosting libre             0.772  0.545  0.407
boosting monotone          0.774  0.547  0.409
logistique, vraies formes  0.777  0.555  0.420
intervalle de l'AUC (rééchantillonnage, 95 %) :
  logistique brute     [0.741 ; 0.779]
  grille de score      [0.751 ; 0.789]
  boosting monotone    [0.753 ; 0.790]
AUC grille - AUC logistique brute : +0.0097  [+0.0009 ; +0.0182]
AUC grille - AUC boosting monotone : -0.0022  [-0.0089 ; +0.0040]
```


Le tableau raconte une histoire nette :

- La **grille** (AUC 0,771) fait **mieux que la logistique brute** (0,762). L'écart est petit (un point d'AUC), mais l'intervalle de la différence **apparié** (mêmes dossiers dans les deux calculs, volume III, section 1.4) est entièrement positif : il n'est pas dû au hasard de l'échantillon de test.
- Le **boosting** (0,774 pour la version monotone, 0,772 pour la version libre) **ne fait pas mieux que la grille** : la différence de 0,002 est dans le bruit (l'intervalle apparié contient zéro). Imposer la monotonie ne coûte rien ici, elle améliore même un tout petit peu.
- La logistique à laquelle on donne les **vraies formes** (nous allons voir lesquelles) atteint 0,777 : c'est le **plafond atteignable** avec ces variables et cet échantillon, la mesure de ce que valent les meilleurs modèles possibles. La grille en est à 0,6 point.

> 🧪 **Un résultat qui n'est pas un slogan.** On lit souvent que « les modèles d'arbres battent la régression logistique ». Sur ce jeu, **ce n'est pas le cas** : les variables sont peu nombreuses, la vérité est une somme d'effets (des formes simples sans interaction), et 28 000 lignes ne laissent pas de quoi apprendre des interactions fines. Sur d'autres données (le jeu réel de la section 1.3, où l'effet du statut de paiement est très non linéaire), le boosting gagne nettement. **La bonne démarche est de mesurer**, et non de supposer.

### 1.2.3 Pourquoi la grille bat la logistique brute : les formes

Pourquoi les classes aident-elles ? Parce que la vérité n'est **pas linéaire**. Les données ont été simulées avec un risque dont l'effet sur la log-cote est :

- **en U pour l'âge** : $0{,}0012\,(\text{âge}-47)^2$ (multiplié par 1,3 comme tous les effets du jeu), ce qui donne un risque plus élevé chez les jeunes que chez les plus de 65 ans, et minimal vers 47 ans ;
- **en coude pour le taux d'endettement** : 1,5 par point d'endettement, puis 3 de plus par point **au-delà de 50 %**.

Une régression logistique brute ne peut pas représenter un U avec **un seul coefficient** : elle ajuste la meilleure droite, qui **décroît** lentement avec l'âge : elle dit que les plus âgés sont les plus sûrs, alors qu'ils sont plus risqués que les 40–55 ans. La grille, qui donne à chaque classe son propre niveau, suit la courbe :


![Effet de l'âge et du taux d'endettement sur la log-cote de défaut, centré sur la population : la vérité programmée (noir), la grille qui suit sa forme (bleu), la droite de la logistique brute (orange pointillé) qui rate le U et le coude.](figures/ch01-formes.png)

La droite orange est la meilleure approximation linéaire, et elle **se trompe aux endroits qui comptent** : elle sous-estime le risque des très jeunes, des plus âgés et des très endettés, qui sont justement ceux que l'on veut repérer. La grille suit le U de l'âge et le coude de l'endettement par paliers. Le boosting, lui, les découvre seul grâce aux seuils de ses arbres.

⚠️ **Ne retenez pas « la grille bat la logistique », mais « les formes comptent ».** Une logistique à laquelle on ajoute un terme quadratique en âge et un coude en endettement (la ligne « vraies formes » du tableau) fait aussi bien que la grille, sans classes. L'avantage de la grille est ailleurs : **elle trouve les formes sans que l'on ait à les deviner**, traite proprement les manquants et reste lisible.

### 1.2.4 Le boosting monotone

Un arbre de gradient libre peut produire des effets **non monotones** là où l'économie n'en admet pas : par exemple un risque qui *baisse* quand l'endettement passe de 55 % à 60 %, simple accident d'un échantillon creux. Pour un modèle de crédit, c'est un problème de **gouvernance** : on ne sait pas l'expliquer, et un client pourrait améliorer son score en détériorant son dossier. Les contraintes de monotonie imposent à chaque arbre de ne jamais inverser le sens d'une variable : la fonction de score est alors **monotone** dans chaque variable contrainte.

Le code de 1.2.1 en montre la mise en œuvre : une liste de signes, un par colonne. Son coût en performance est ici nul. Dans d'autres situations, il peut être de quelques millièmes d'AUC ; **c'est le prix d'un modèle défendable**. Pour comprendre les contributions d'un modèle de ce type, les méthodes du volume III (section 5.3, importance par permutation, SHAP) s'appliquent sans changement ; en crédit, on leur préfère souvent des **motifs de refus** adossés à la grille (1.2.6) ou à des contributions par variable.

### 1.2.5 Calibrer : une probabilité n'est pas un rang

Un score qui classe bien peut annoncer des probabilités fausses. Or le crédit **utilise les probabilités** : pour fixer un prix, pour calculer la perte attendue, pour le capital réglementaire. La **calibration** (volume III, section 5.2) vérifie qu'un groupe de dossiers annoncés à 3 % fait bien environ 3 % de défauts. Regroupons les dossiers du test en dix groupes de taille égale, selon la probabilité annoncée par la grille :

```text
           n  annoncee  observee
groupe                          
1       1200    0.0094    0.0108
2       1200    0.0151    0.0167
3       1201    0.0200    0.0216
4       1199    0.0253    0.0192
5       1200    0.0314    0.0242
6       1200    0.0395    0.0500
7       1200    0.0501    0.0500
8       1200    0.0670    0.0633
9       1200    0.0995    0.1117
10      1200    0.2356    0.2292
```


La grille est **bien calibrée** : la probabilité moyenne annoncée (5,9 %) est celle du défaut observé (6,0 %) et, groupe par groupe, les écarts restent dans une marge de deux écarts-types (le dixième groupe annonce 23,6 % et observe 22,9 %). Ce n'est pas un hasard : une régression logistique **calibre en moyenne par construction** sur son échantillon de développement. Cette propriété se perd quand la population change (section 1.3) ; un boosting, lui, n'est pas calibré par construction et demande souvent une recalibration (régression logistique ou isotonique sur la sortie, volume III, section 5.2).

### 1.2.6 Expliquer un refus : les motifs

Dans beaucoup de juridictions, un client refusé est en droit de connaître **les principales raisons** de la décision, et le prêteur doit pouvoir les produire (nous reviendrons sur la réglementation au chapitre 4 ; le droit exact dépend du pays et de l'époque, à vérifier). La grille y répond naturellement : les **motifs de refus** (*reason codes*) sont les variables pour lesquelles le dossier **perd le plus de points** par rapport au meilleur cas possible de chaque variable.

```python
def motifs(i, k=3):
    """Les k variables où le dossier te.iloc[i] perd le plus de points, par rapport à la meilleure classe de la variable."""
    perte = {}
    for v in O.VARIABLES:
        classes = pts[pts.variable == v]
        c = O.classer(te.iloc[[i]][v], v).iloc[0]
        perte[v] = classes.points.max() - float(classes[classes.classe == c].points.iloc[0])
    return pd.Series(perte).sort_values(ascending=False).head(k).round(1)

print(motifs(trois["risqué"]))
```
<!--sortie-->
```text
age                    30.1
anciennete_relation    23.4
anciennete_emploi      22.8
dtype: float64
```


Pour ce dossier très risqué, les trois motifs sont l'âge (30 points perdus par rapport à la meilleure tranche d'âge), l'ancienneté de la relation (23 points) et l'ancienneté dans l'emploi (23 points). Remarquez qu'**un motif n'est pas un conseil** : un client de 24 ans ne peut pas « corriger » son âge. La réglementation de certains pays interdit d'ailleurs que certaines variables (le sexe, par exemple) servent à décider ; l'âge lui-même est parfois encadré. La question de savoir **quelles variables on a le droit d'utiliser**, et ce qu'on fait de celles qui servent de substitut à des variables interdites, relève du volume III (section 5.4, équité) et du cadre légal local.

### 1.2.7 Choisir

Le comité de risque ne choisit pas sur l'AUC seule. Les critères qui comptent, dans l'ordre où on les rencontre en pratique :

| Critère | Grille | Boosting monotone | Boosting libre |
|---|---|---|---|
| Pouvoir de classement (mesuré ici) | 0,771 | 0,774 | 0,772 |
| Explicabilité d'un refus | directe (points) | par contributions | par contributions |
| Monotonie garantie | oui, si les classes le sont | oui (contraintes) | non |
| Stabilité face à une population qui change | bonne (classes larges) | moyenne | plus fragile |
| Surveillance et validation | outils standard (PSI, tables) | outils standard + explicabilité | plus lourde |
| Traitement des manquants | classe à part, lisible | natif | natif |

Dans la pratique, beaucoup de banques conservent une **grille comme modèle de référence** et la mettent en concurrence avec un modèle plus souple, le **challenger** : si l'écart de performance est faible, comme ici, on garde la grille ; s'il est large et stable, on adopte le challenger **avec ses garde-fous**. C'est la logique de la **rigueur d'évaluation** du volume III : on ne s'incline pas devant la sophistication sans l'avoir mesurée, avec son incertitude.

> ✅ **À retenir.**
> - Sur nos données, trois candidats classent presque aussi bien : la **forme des effets** compte plus que l'algorithme. La grille gagne sur la logistique brute (+0,010 d'AUC, intervalle apparié positif) parce que la vérité n'est pas linéaire ; elle ne perd rien face au boosting (écart de 0,002 dans le bruit).
> - Le **plafond** (la logistique aux vraies formes) vaut 0,777 : il situe les candidats sur l'échelle de ce qui est atteignable.
> - Un modèle de crédit doit être **monotone** quand l'économie l'exige : les contraintes de monotonie ne coûtent ici rien.
> - Un score doit être **calibré** : la grille l'est par construction sur son échantillon, pas forcément ailleurs.
> - Les **motifs de refus** se lisent dans les points perdus ; ils expliquent, ils ne prescrivent pas.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.3, exercices 1.4 et 1.5.


## 1.3 Mesures de performance : Gini, KS, ROC

Un score se juge sur quatre questions distinctes, que l'on confond trop souvent : **classe-t-il bien** (discrimination : AUC, Gini, KS), **annonce-t-il de bonnes probabilités** (calibration), **reste-t-il bon quand la clientèle change** (stabilité), et **avec quelle incertitude** connaît-on ces mesures ? Cette section donne à chaque question son outil, avec les démonstrations qui permettent de les relire, puis un détour par un jeu **réel** pour ne pas croire que tout se passe toujours comme dans nos données simulées.

### 1.3.1 La courbe ROC et l'AUC

Pour un seuil de risque $c$, un dossier est « alerté » si son score de risque dépasse $c$. Deux taux décrivent la règle :

- le **taux de vrais positifs** (TPR, la *sensibilité*) : la part des **mauvais** qui sont alertés ;
- le **taux de faux positifs** (FPR) : la part des **bons** qui sont alertés à tort.

La courbe **ROC** (*receiver operating characteristic*) trace le TPR en fonction du FPR quand le seuil parcourt toutes ses valeurs. Un score aléatoire donne la diagonale ; un score parfait, un angle droit en haut à gauche. L'**AUC**, l'aire sous la courbe, a une interprétation probabiliste directe que l'on retient mieux que l'aire :

$$\text{AUC}=P(S_{\text{mauvais}}>S_{\text{bon}})+\tfrac12\,P(S_{\text{mauvais}}=S_{\text{bon}}),$$

c'est la probabilité qu'un **mauvais** tiré au hasard ait un score de risque **plus élevé** qu'un **bon** tiré au hasard. Calculons-la à la main sur six dossiers : trois mauvais (scores de risque 0,9 ; 0,6 ; 0,4) et trois bons (0,7 ; 0,3 ; 0,2). Il y a $3\times3=9$ paires (un mauvais, un bon) ; comptons celles où le mauvais a le score le plus élevé :

| mauvais | contre 0,7 | contre 0,3 | contre 0,2 | paires gagnées |
|---|---|---|---|---|
| 0,9 | oui | oui | oui | 3 |
| 0,6 | non | oui | oui | 2 |
| 0,4 | non | oui | oui | 2 |

Sept paires sur neuf : $\text{AUC}=7/9\approx0{,}778$.

### 1.3.2 Le Gini et la courbe CAP

Les risquologues préfèrent souvent le **Gini** (ou *accuracy ratio*) : $\text{Gini}=2\,\text{AUC}-1$. Il vaut 0 pour un score aléatoire et 1 pour un score parfait. Dans l'exemple, $2\times\frac79-1=\frac49\approx0{,}444$. D'où vient cette formule ? D'une autre courbe, la **CAP** (*cumulative accuracy profile*), qui classe les dossiers du plus risqué au moins risqué et trace, en fonction de la part de la population examinée, la part des mauvais **capturés**.

> 📐 **Démonstration : Gini = 2·AUC − 1.** Notons $\pi$ la proportion de mauvais dans la population. Quand on examine les dossiers dont le score dépasse un seuil, la part de la population examinée est $x=\pi\,\text{TPR}+(1-\pi)\,\text{FPR}$ et la part des mauvais capturés est $y=\text{TPR}$. L'aire sous la CAP vaut donc
> $$A_{\text{CAP}}=\int \text{TPR}\;d\bigl[\pi\,\text{TPR}+(1-\pi)\,\text{FPR}\bigr]=\pi\int \text{TPR}\,d\text{TPR}+(1-\pi)\int\text{TPR}\,d\text{FPR}=\frac\pi2+(1-\pi)\,\text{AUC}.$$
> Le score aléatoire a une aire de $\frac12$ ; le score parfait capture tous les mauvais dans les premiers $\pi$ de la population, soit une aire de $1-\frac\pi2$. Le **rapport de précision** est le rapport des aires entre le score étudié et l'aléatoire, et entre le parfait et l'aléatoire :
> $$\text{AR}=\frac{A_{\text{CAP}}-\frac12}{(1-\frac\pi2)-\frac12}=\frac{\frac\pi2+(1-\pi)\text{AUC}-\frac12}{\frac{1-\pi}{2}}=\frac{(1-\pi)(\text{AUC}-\frac12)}{\frac{1-\pi}{2}}=2\,\text{AUC}-1.$$
> Le résultat **ne dépend pas de $\pi$** : c'est ce qui permet de comparer des Gini d'un portefeuille à l'autre... sous réserve des précautions de 1.3.7.

Sur nos données, voici le Gini de la grille et les deux courbes :

```python
from sklearn.metrics import roc_auc_score, roc_curve
auc = roc_auc_score(y_te, r_grille)                  # r_grille : risque = − score
fpr, tpr, _ = roc_curve(y_te, r_grille)
print(f"AUC {auc:.3f}   Gini {2 * auc - 1:.3f}   KS {np.max(tpr - fpr):.3f}")
```
<!--sortie-->
```text
AUC 0.771   Gini 0.542   KS 0.406
```


![À gauche, courbes ROC des trois candidats du test ; à droite, courbe CAP de la grille : examiner les 10 % de dossiers les plus risqués capture une part très supérieure de 10 % des mauvais.](figures/ch01-roc-cap.png)

La courbe CAP se lit sans équation : en examinant les 10 % de dossiers que la grille juge les plus risqués, on capture **38 % des mauvais** (un score aléatoire en capturerait 10 %) ; avec 20 % des dossiers, 57 %. Les trois courbes ROC se **confondent presque** : les trois modèles de la section 1.2 sont, pour la discrimination, d'un niveau voisin.

### 1.3.3 Le KS : l'écart maximal entre bons et mauvais

La statistique de **Kolmogorov–Smirnov** mesure la plus grande distance verticale entre les fonctions de répartition des scores des bons et des mauvais :

$$\text{KS}=\max_c\,\bigl|F_{\text{mauvais}}(c)-F_{\text{bon}}(c)\bigr|=\max_c\,\bigl(\text{TPR}(c)-\text{FPR}(c)\bigr).$$

C'est la plus grande différence qu'un seuil unique puisse faire entre la part de mauvais et la part de bons captés. Le point où elle est atteinte est un **seuil naturel** de décision quand on n'a pas d'information de coûts. Le KS est très lu en banque, parce qu'il se résume en un nombre et un seuil.


![Distributions du score des bons et des mauvais (à gauche) et leurs fonctions de répartition (à droite) : le KS est l'écart vertical maximal.](figures/ch01-ks.png)

### 1.3.4 Du score à la politique d'acceptation

Un indicateur de rang ne dit pas **où couper**. La politique d'acceptation se lit dans un tableau de compromis : à chaque seuil, quelle part des demandes accepte-t-on, quel taux de défaut paie-t-on parmi les acceptés, et quel taux auraient eu les refusés ?

```text
 seuil  part acceptée  défaut des acceptés  défaut des refusés
   540         0.9116               0.0417              0.2451
   560         0.7828               0.0312              0.1623
   580         0.5392               0.0202              0.1058
   600         0.2431               0.0154              0.0739
```


Un seuil de 560 points accepte 78 % des demandes pour un taux de défaut de 3,1 % parmi les acceptés (contre 6,0 % sans score) et refuse des dossiers qui auraient fait 16 % de défauts. Monter à 600 points ramène le défaut des acceptés à 1,5 %, au prix de **refuser les trois quarts** des clients. Le bon seuil n'est pas statistique : il dépend du **coût d'un défaut** (la perte de l'exposition, section 1.5) et du **gain d'un bon client** (les intérêts), donc de la marge de la banque. L'AUC ne choisit pas le seuil, elle dit seulement si la courbe de ce compromis est bonne.

### 1.3.5 L'incertitude de la mesure


Une AUC est une **estimation** à partir de 12 000 prêts dont 716 mauvais (volume III, section 5.1 : c'est le nombre de mauvais qui compte). Quelle est sa marge d'erreur ? Un **bootstrap** (volume III, section 1.2) rééchantillonne les lignes du test avec remise et recalcule l'AUC : l'intervalle à 95 % de la grille est **[0,752 ; 0,791]**. L'incertitude est de près de **deux points d'AUC** de chaque côté, alors que les écarts entre modèles de la section 1.2 sont d'un point. C'est pourquoi l'on compare deux modèles par un **intervalle de la différence** sur des rééchantillons **appariés** (les mêmes lignes pour les deux modèles), plus étroit que chaque intervalle pris isolément.

⚠️ Il y a trois sources distinctes d'incertitude : l'**échantillon de test** (ce que mesure le bootstrap), l'**échantillon de développement** (un autre échantillon donnerait une autre grille ; on le mesure en refaisant tout le processus sur des rééchantillons de développement) et la **dérive** future de la population. Seule la première est facile à chiffrer, ce qui explique que les performances réelles soient généralement inférieures à celles du test.

### 1.3.6 Stabilité : la population change

Une grille est utilisée pendant des années. La clientèle, elle, change : la banque s'étend vers les jeunes, la conjoncture se dégrade, une campagne attire un autre profil. Le **PSI** (*population stability index*, volume IV, section 4.7) compare la distribution d'une variable, ou du score, entre la population de développement et la population actuelle :

$$\text{PSI}=\sum_{j}(p_j^{\text{actuel}}-p_j^{\text{dév.}})\,\ln\frac{p_j^{\text{actuel}}}{p_j^{\text{dév.}}}.$$

L'usage place des **repères** : moins de 0,10, la population est stable ; entre 0,10 et 0,25, un changement à examiner ; au-delà, un changement important. Ce sont des conventions, pas des lois.

Simulons un afflux de jeunes emprunteurs et de dossiers très endettés : nous tirons, dans le **jeu de test**, 6 000 prêts avec une probabilité d'autant plus forte que le client a moins de 30 ans ou un taux d'endettement supérieur à 40 %.

```text
                      PSI
score               0.129
âge                 0.246
taux d'endettement  0.149
défaut observé : 0.0893   PD annoncée : 0.0873   AUC : 0.788
```


Le PSI du score dépasse 0,10 et celui de l'âge dépasse 0,20 : l'alarme sonne. Pourtant, le **pouvoir de classement tient** (l'AUC de 0,788 est du niveau de celle du test), et la probabilité annoncée de défaut (8,7 %) reste proche du défaut observé (8,9 %) : la grille a **vu venir** le risque supplémentaire, parce que les nouveaux clients lui ressemblent par leurs variables. Ce qui casserait le score, c'est un changement de la **relation** entre les variables et le défaut (la dérive du concept du volume IV, section 4.7), que le PSI ne voit pas.

### 1.3.7 Calibration : la probabilité annoncée est-elle la bonne ?

La calibration se contrôle **classe de risque par classe de risque**. Les banques regroupent leurs clients en quelques **notes** (une *échelle maîtresse*) auxquelles est attachée une probabilité de défaut. Découpons les dossiers du test en sept notes selon la PD annoncée, et testons, pour chaque note, l'hypothèse « la probabilité de défaut vraie est celle qui est annoncée » par un **test binomial** : sous l'hypothèse, le nombre de défauts d'une note de $n$ dossiers suit une loi binomiale $\mathcal{B}(n,\text{PD})$.

```text
 note  dossiers  PD annoncée  défaut observé  p-valeur
    1       648       0.0077          0.0093    0.6484
    2      2373       0.0152          0.0169    0.5019
    3      2958       0.0269          0.0216    0.0780
    4      2628       0.0458          0.0498    0.3269
    5      1647       0.0766          0.0826    0.3542
    6      1200       0.1367          0.1300    0.5285
    7       546       0.3299          0.3352    0.7850
Hosmer-Lemeshow (10 groupes, 8 degrés de liberté) : 10.50   p-valeur 0.232
```


Les p-valeurs sont élevées (aucune note n'est rejetée au seuil de 5 %), et le test de **Hosmer–Lemeshow**, qui regroupe les dossiers en dix groupes et additionne les écarts $(O_g-E_g)^2/[E_g(1-E_g/n_g)]$ (loi du $\chi^2$ à 8 degrés de liberté), ne rejette pas non plus la calibration. La grille est calibrée **sur cet échantillon**. Le test n'a pourtant qu'une portée limitée, et nous allons voir pourquoi.

#### La conjoncture ruine le test binomial

Le fichier `taux_defaut_macro.csv` donne 80 trimestres de taux de défaut d'un portefeuille de 20 000 prêts (nombre supposé). Le taux moyen est de 3,06 %. Appliquons le test binomial trimestre par trimestre à la PD « moyenne sur le cycle » :


![Taux de défaut trimestriel d'un portefeuille et bande de confiance (95 %) du test binomial autour de la PD moyenne : presque tous les trimestres sortent de la bande.](figures/ch01-cycle-binomial.png)

Le test **rejette 65 trimestres sur 80** : la bande de confiance du test binomial est étroite (± 0,24 point) alors que le taux de défaut oscille entre 1,0 % et 12,8 %. Ces rejets ne disent pas que la PD est mal estimée : ils disent que **le test suppose des défauts indépendants**. Or les défauts d'un portefeuille sont **corrélés par la conjoncture** : une récession touche tous les emprunteurs à la fois. On modélise cette dépendance par un **facteur commun** (modèle de Vasicek, retrouvé au chapitre 4 dans la formule de capital de Bâle) : sous une corrélation d'actifs de seulement 3 %, un test binomial à 5 % rejette à tort la vraie PD **dans 85 % des cas** (simulation de 2 000 portefeuilles de 20 000 prêts, PD vraie de 3 %). La taille du test est pulvérisée.

Deux enseignements à retenir :

- une **PD « sur le cycle »** (*through the cycle*, la moyenne des années) et une **PD « à la date »** (*point in time*, qui suit la conjoncture) répondent à deux questions différentes ; la première sert au capital, la seconde aux provisions (section 1.5) ;
- le **test binomial** est **trop sévère** pour un portefeuille agrégé : les validateurs utilisent des variantes qui intègrent une corrélation (tests de Blochwitz, de Vasicek, test de Jeffreys) ou simplement des seuils de tolérance fixés d'avance. Les noms des variantes varient selon les pratiques ; le point à retenir est l'indépendance supposée.

### 1.3.8 Un détour par des données réelles

Pour ne pas conclure sur des données que nous avons nous-mêmes fabriquées, voici les mêmes mesures sur un **jeu réel** : 30 000 titulaires d'une carte de crédit (source UCI, licence CC0, Yeh et Lien, 2009 ; 22 % de défaut le mois suivant). Les variables sont la limite de crédit, l'âge, le niveau d'études, six mois de **statuts de paiement** (`pay_1` à `pay_6` : −2 = pas de consommation, −1 = payé en totalité, 0 = paiement minimal, 1 à 8 = mois de retard), les montants de facture et de paiement. Deux modèles, entraînés sur 70 % et mesurés sur 30 % :

```text
                                  AUC   Gini     KS
pay_1 seul (nombre)             0.694  0.388  0.383
logistique, tout en nombres     0.728  0.457  0.381
logistique, pay_1 en modalités  0.768  0.536  0.424
boosting                        0.791  0.582  0.448
```


Les chiffres sont d'un autre ordre que ceux de nos prêts simulés (le défaut est près de quatre fois plus fréquent, l'information sur le comportement récent est directe), et l'histoire diffère : la logistique qui prend `pay_1` comme un **nombre** (de −2 à 8) perd beaucoup, parce que l'effet n'est pas linéaire (−2, −1 et 0 sont des statuts de bons payeurs, 2 est déjà une alerte) ; **traiter `pay_1` en modalités**, comme le fait une grille par classes, récupère l'essentiel du gain, et le boosting fait encore un peu mieux (il trouve en plus des interactions). La leçon est celle de 1.2 : **ce sont les formes qui comptent**, et elles se découvrent en regardant les données ; la grille est un bon moyen de ne pas les rater.

### 1.3.9 Les pièges de la mesure

- **L'AUC ne dit rien de la calibration.** Un score qui annoncerait partout deux fois la vraie probabilité classe aussi bien (le rang ne change pas) et se trompe sur chaque prix.
- **L'AUC ignore les coûts.** Deux scores de même AUC peuvent être très différents dans la zone où l'on décide (les 20 % de dossiers les plus risqués, ou le seuil d'acceptation).
- **Le Gini dépend de la population.** Un Gini de 55 % sur la clientèle d'un prêteur n'est pas comparable à un Gini de 45 % sur un portefeuille plus homogène : avec des clients plus semblables, le classement est plus difficile. On ne compare des Gini **qu'à population comparable**.
- **Le Gini de développement est optimiste.** Il se mesure sur l'échantillon où les classes ont été choisies ; la mesure honnête est celle du **test** (et, mieux, d'une période postérieure).
- **Un Gini qui baisse n'est pas toujours un modèle qui vieillit** : il peut refléter un changement de politique d'acceptation (1.1.7).

> ✅ **À retenir.**
> - **AUC** = probabilité qu'un mauvais ait un score de risque plus élevé qu'un bon ; **Gini** = 2·AUC − 1 (démontré par la courbe CAP, indépendant de la proportion de mauvais) ; **KS** = écart maximal TPR − FPR.
> - Les trois mesurent la **discrimination**, pas la **calibration**, pas la **décision** : le seuil se choisit sur un tableau de compromis et sur des coûts.
> - Une AUC s'accompagne de son **intervalle** (bootstrap), et deux modèles se comparent sur des rééchantillons **appariés**.
> - Le **PSI** repère un changement de population ; il ne voit pas une dérive du concept.
> - Le **test binomial** de calibration suppose des défauts indépendants et rejette à tort un portefeuille soumis à la conjoncture ; il faut le compléter par des variantes qui tiennent compte de la corrélation.
> - Sur des données réelles aussi, **les formes des effets** décident de la performance : mesurez, regardez les effets, ne supposez pas.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.4, exercices 1.6 à 1.8.


## 1.4 ➕ WOE/IV et discrétisation des variables

> 🧭 **Section optionnelle.** Elle reprend, avec plus de précision, les classes et le poids de l'évidence de la section 1.1. Vous pouvez passer à 1.5 sans la lire.

La section 1.1 a découpé les variables en classes « à la main ». Cette section répond aux trois questions que pose tout relecteur de la grille : **à quoi sert l'IV, un indicateur très utilisé, et que mesure-t-il vraiment ? Comment découpe-t-on sans arbitraire ? Quels pièges guettent le WOE ?** Le fil conducteur est un avertissement : le WOE et l'IV sont d'excellents outils de **lecture**, et de mauvais juges d'un découpage sans garde-fous.

### 1.4.1 L'information qu'une variable apporte : l'IV

Pour une variable découpée en classes $j=1,\dots,J$, avec $g_j=B_j/B$ la part des bons et $b_j=M_j/M$ celle des mauvais dans la classe $j$, la **valeur d'information** (*information value*, IV) est

$$\text{IV}=\sum_{j=1}^{J}(g_j-b_j)\,\ln\frac{g_j}{b_j}=\sum_{j=1}^J(g_j-b_j)\,\text{WOE}_j.$$

Chaque terme est **positif** : si $g_j>b_j$, le WOE est positif et la différence aussi ; si $g_j<b_j$, les deux sont négatifs. L'IV est donc une somme de termes positifs, nulle seulement si les bons et les mauvais ont la **même distribution** sur les classes. Il a une lecture précise :

> 📐 **L'IV est une divergence symétrisée.** Développons : $\text{IV}=\sum_j g_j\ln\frac{g_j}{b_j}+\sum_j b_j\ln\frac{b_j}{g_j}=\text{KL}(g\,\|\,b)+\text{KL}(b\,\|\,g)$, la somme des deux **divergences de Kullback–Leibler** entre la distribution des bons et celle des mauvais. L'IV mesure donc *à quel point on distingue* les deux populations avec cette variable, dans les deux sens. Les conventions du métier lisent un IV de la façon suivante.

| IV | Lecture usuelle |
|---|---|
| moins de 0,02 | variable sans intérêt |
| de 0,02 à 0,1 | pouvoir prédictif faible |
| de 0,1 à 0,3 | pouvoir prédictif moyen |
| de 0,3 à 0,5 | pouvoir prédictif fort |
| plus de 0,5 | **suspect** : fuite d'information probable |

Ces seuils sont des **conventions de praticiens**, pas des résultats théoriques ; la dernière ligne est la plus utile : un IV trop beau est presque toujours un défaut de construction (nous le provoquons en 1.4.3). Voici les IV de nos dix variables, calculés sur l'échantillon de développement avec les classes de la section 1.1 :

```text
taux_endettement       0.403
anciennete_emploi      0.258
nb_incidents_12m       0.240
revenu_annuel          0.236
age                    0.145
montant                0.071
logement               0.054
anciennete_relation    0.051
duree_mois             0.029
objet                  0.015
```

Le taux d'endettement est de loin le plus informatif (IV 0,40, fort), devant l'ancienneté dans l'emploi, les incidents et le revenu (de 0,24 à 0,26, moyens), l'âge (0,15) ; le montant, l'ancienneté de la relation et le logement sont faibles, la durée et l'objet sont au bord de l'inutilité. Cet ordre est cohérent avec les amplitudes de points de 1.1.6. Les variables d'IV très faible ne coûtent rien à garder, mais elles alourdissent la carte : on en retire souvent sous 0,02 ou 0,03.

⚠️ L'IV est une mesure **univariée** : il ne tient pas compte de la redondance entre variables (le revenu et l'endettement se recoupent), que la régression gère ensuite.

### 1.4.2 Combien de classes ? L'IV grandit avec leur nombre

Si l'on raffine le découpage, l'IV ne peut que croître : il y a plus de façons de séparer bons et mauvais. Cette croissance n'est pas toute de l'information, c'est aussi du **bruit** que l'on apprend. Pour le voir, découpons l'âge en $k$ classes d'effectifs égaux, puis, comme contrôle, une variable de **pur bruit** (un tirage gaussien indépendant du défaut). Pour chaque découpage, nous mesurons l'IV sur l'échantillon de développement, puis la **même quantité** sur l'échantillon de test, avec les WOE appris sur le développement :

```text
 classes  âge dév.  âge test  bruit dév.  bruit test
       3    0.0603    0.0657      0.0001      0.0008
       6    0.1096    0.1268      0.0015     -0.0012
      12    0.1453    0.1594      0.0032     -0.0034
      25    0.1515    0.1617      0.0096     -0.0048
      50    0.1664    0.1712      0.0332     -0.0108
     100    0.1785    0.1725      0.0553     -0.0155
```


L'âge gagne beaucoup entre 3 et 12 classes (0,06 à 0,15) puis plafonne : au-delà, les classes supplémentaires n'ajoutent presque rien sur le test. La variable de **bruit** montre l'autre face : son IV de développement monte à 0,055 avec 100 classes alors qu'elle ne contient **aucune information** ; sur le test, il tombe à zéro ou devient négatif (aucun signal). C'est l'effet qu'on appelle **surapprentissage du découpage**. Deux règles en découlent : on ne choisit pas le nombre de classes en maximisant l'IV de développement, et on regarde toujours l'IV **sur un échantillon de contrôle**.

### 1.4.3 Fusionner pour rendre monotone

Beaucoup de variables ont un effet que l'économie dit **monotone** : plus d'ancienneté dans la relation, moins de risque. Un découpage en classes d'effectifs égaux produit pourtant de petites inversions dues au hasard : le taux de la deuxième classe dépasse celui de la troisième sans raison. L'algorithme classique est la **fusion monotone** : on part de $k=10$ classes d'effectifs égaux et, tant que le taux de défaut n'est pas monotone, on **fusionne les deux classes voisines fautives dont la fusion fait perdre le moins d'IV**. Voici le résultat sur l'ancienneté de la relation, puis sur l'âge :

```text
anciennete_relation
  avant : 10 classes, IV 0.054, taux (%) [8.2 6.8 7.2 6.7 6.3 6.  5.5 5.3 4.6 3.5]
  après : 9 classes, IV 0.054, taux (%) [8.2 7.  6.7 6.3 6.  5.5 5.3 4.6 3.5]
age
  avant : 10 classes, IV 0.138, taux (%) [13.4  6.3  5.8  5.1  4.9  4.5  4.7  4.1  5.3  6.3]
  après : 5 classes, IV 0.127, taux (%) [13.4  6.3  5.8  5.1  5. ]
```


Pour l'ancienneté de la relation, une seule fusion (dix classes deviennent neuf) suffit et l'IV ne bouge pas (0,054) : le découpage monotone est **gratuit**. Pour l'âge, au contraire, la fusion **force** la monotonie là où la vérité est en U : elle regroupe les 25–30 ans avec les suivants et fait **disparaître le sur-risque des plus de 65 ans** (la dernière classe a un taux de 5,0 %, alors que celui des plus de 65 ans est de 8,7 %). L'IV baisse peu (de 0,138 à 0,127), ce qui montre que l'IV ne suffit pas pour juger un découpage : la perte est concentrée dans une zone peu peuplée mais économiquement sensible.

> 🧪 **La monotonie est une hypothèse, pas un dogme.** On l'impose quand elle a un fondement (plus d'endettement, plus de risque ; plus de revenu, moins de risque) et on la **refuse** quand on a de bonnes raisons de voir un U (l'âge) ou un palier (le logement). Une grille dont toutes les variables sont forcément monotones est plus facile à défendre, et parfois moins juste. Dans les deux cas : décidez avant de regarder le résultat, et écrivez la raison.

Les outils qui font cette recherche automatiquement (arbres de décision de profondeur limitée, algorithmes de fusion avec test du $\chi^2$, optimisation par programmation en nombres entiers) donnent des découpages proches. Ce qui compte, c'est le garde-fou : effectifs minimaux, monotonie justifiée, contrôle sur un échantillon à part.

### 1.4.4 Trois pièges du WOE

**Les classes rares.** Si une classe ne contient aucun mauvais, $b_j=0$ et $\text{WOE}_j=\ln(g_j/0)=+\infty$. Même avec peu de mauvais, le WOE est très instable. On le **lisse** en ajoutant une demi-observation à chaque effectif (c'est le choix du code du chapitre) ou en fusionnant la classe avec sa voisine. La section 1.1.7 en a donné un exemple concret : la classe d'endettement de 50 à 60 % de l'échantillon des acceptés ne contenait que 20 prêts et recevait un WOE de +0,66.

**Les manquants informatifs.** Dans nos données, l'ancienneté dans l'emploi manque pour 7 % des prêts, et le défaut y est de 11,9 % contre 5,5 % pour les autres : le fait de ne pas fournir l'information est lui-même un signal. Le garder comme **classe à part** (« manquant », WOE −0,75) conserve ce signal ; l'**imputer** (par la médiane, 6,3 ans) le détruit :

```text
IV de l'ancienneté dans l'emploi, manquant en classe à part : 0.258
IV après imputation par la médiane (6.3 ans)        : 0.163
```


L'imputation fait perdre plus du tiers de l'information de la variable (0,26 contre 0,16). Cela vaut pour la grille ; un modèle d'arbres gère aussi les manquants nativement. Ce qu'il faut éviter, c'est de **supposer que le manquant est neutre**.

**La fuite d'information.** Le dernier piège est le plus coûteux : un IV énorme. Simulons une variable « nombre de retards de paiement du prêt » qui serait connue après la souscription : elle vaut zéro ou presque pour les bons, quelques unités pour les mauvais.

```text
IV de la variable « retards du prêt » : 4.64  (repère de suspicion : 0,5)
```


Un IV de 4,6 (plus de dix fois celui du taux d'endettement) n'est pas une aubaine, c'est **une alarme** : une variable de ce genre n'existe pas à la date de la demande. Quand un IV dépasse nettement 0,5, on ne félicite pas le modèle, on cherche **quand** la variable est connue (volume III, section 1.1).

### 1.4.5 Le WOE est une paramétrisation, pas une magie

Que perd-on à passer par les WOE plutôt que de donner à une régression les **indicateurs de classe** (une variable 0/1 par classe) ? Le WOE impose à chaque variable **un seul** coefficient $\beta_k$ multiplié à des valeurs précalculées, alors que les indicateurs laissent la régression ajuster chaque classe librement. Comparons les deux sur le test :

```text
AUC, grille par WOE            : 0.7712
AUC, indicateurs de classes    : 0.7778
différence (indicateurs - WOE) : +0.0065  [+0.0023 ; +0.0105]
```


Les deux approches sont **très proches** : les indicateurs gagnent 0,007 d'AUC, un écart petit mais réel (l'intervalle apparié, de +0,002 à +0,011, exclut zéro), parce que la régression peut ajuster chaque classe librement au lieu de se plier à un seul coefficient par variable. Le WOE n'est donc pas un gain de précision ; il rend le modèle **plus lisible** : un coefficient par variable, des points qui s'additionnent, la même échelle pour toutes les variables, et un moyen de repérer d'un coup d'œil les classes aberrantes. Il porte aussi un risque que les indicateurs n'ont pas : le WOE est un **encodage par la cible** (volume III, section 4.1), calculé avec les étiquettes ; calculé sur toutes les données avant un découpage de validation, il fuit.

> ✅ **À retenir.**
> - $\text{WOE}_j=\ln\frac{g_j}{b_j}$ ; $\text{IV}=\sum_j(g_j-b_j)\text{WOE}_j=\text{KL}(g\|b)+\text{KL}(b\|g)$ : un indicateur univarié du pouvoir de séparation, lu avec des seuils **conventionnels**, et **suspect au-dessus de 0,5**.
> - L'IV de développement **grandit avec le nombre de classes**, même pour du bruit : on le contrôle sur un échantillon à part et on garde peu de classes lisibles.
> - La **fusion monotone** est gratuite quand l'économie impose la monotonie ; elle **abîme** quand la vérité est en U.
> - Les **manquants** forment souvent une classe informative ; les **classes rares** se lissent ou se fusionnent ; un **IV énorme** est une alarme de fuite.
> - Le WOE est une **paramétrisation commode**, pas une source de performance : les indicateurs de classes font légèrement mieux (+0,007 d'AUC).

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.5, exercices 1.9 et 1.10.


## 1.5 ➕ PD, LGD, EAD et pertes de crédit attendues (IFRS 9)

> 🧭 **Section optionnelle.** Elle prolonge le score vers ce que la comptabilité réclame : un **montant en euros**, la perte que le portefeuille devrait subir. Les paramètres d'exemple (seuils d'étapes, pondérations de scénarios) sont **illustratifs** ; la norme IFRS 9 est citée dans l'état de nos connaissances à la rédaction (2026) et ses exigences exactes sont à vérifier dans le texte en vigueur. Rien ici n'est un conseil comptable.

Un score donne une probabilité. Une banque doit **provisionner** des euros. Le passage de l'un à l'autre est une multiplication de trois grandeurs, que l'on modélise **séparément** parce qu'elles ne s'expliquent pas par les mêmes causes : la **probabilité de défaut** (PD), la **perte en cas de défaut** (LGD, *loss given default*) et l'**exposition au défaut** (EAD, *exposure at default*). La **perte attendue** (*expected credit loss*, ECL) d'un prêt est

$$\text{ECL}=\text{PD}\times\text{LGD}\times\text{EAD}.$$

Pour un prêt de 10 000 € avec une PD de 3 %, une LGD de 45 % et une EAD de 10 000 €, la perte attendue est $0{,}03\times0{,}45\times10\,000=135\ €$. Cette perte n'est pas un risque, c'est un **coût prévisible** : la banque la couvre par le taux d'intérêt et par ses provisions. Le **risque** proprement dit (l'écart autour de cette moyenne) relève du capital (chapitre 4).


### 1.5.1 La PD : douze mois ou toute la vie

Deux horizons coexistent. La **PD à 12 mois** est la probabilité de défaut dans l'année qui vient, celle que donne notre grille. La **PD sur la durée de vie** est la probabilité de défaut avant l'échéance du prêt, forcément plus grande. Si le risque annuel est constant et vaut $h$, la probabilité de **survivre** $t$ années est $(1-h)^t$, d'où

$$\text{PD}_{\text{cumulée}}(T)=1-(1-h)^T,\qquad \text{PD marginale de l'année } t=(1-h)^{t-1}\,h.$$

Pour $h=3\ \%$ : $1-0{,}97^3=8{,}7\ \%$ sur trois ans, $1-0{,}97^5=14{,}1\ \%$ sur cinq ans, avec des probabilités marginales de défaut de 3,00 %, 2,91 %, 2,82 %… qui diminuent un peu parce qu'il reste moins de survivants. L'hypothèse d'un risque constant est une simplification : en réalité, le risque dépend de l'âge du prêt, de la conjoncture et de la note, qui migre (section 1.6 donne la version « matrice de transition » de la même idée).

> 💡 **Pourquoi deux PD ?** Parce que la norme IFRS 9 demande de provisionner tantôt sur un an, tantôt sur la vie entière, selon l'état du prêt (1.5.5). La PD à 12 mois de la grille ne suffit pas toujours.

### 1.5.2 La LGD : ce que l'on perd vraiment

La LGD est la **part de l'exposition que l'on ne récupère pas** après le défaut : $\text{LGD}=1-\dfrac{\text{récupérations actualisées}}{\text{EAD}}$. Elle dépend de la **garantie** (une caution, un nantissement), du **recouvrement** (frais, délais) et du moment. Le fichier `recouvrements.csv` donne, pour 6 000 prêts entrés en défaut, la perte réellement subie en part de l'exposition, supposée **déjà actualisée** (c'est la convention de ce chapitre) ; il indique aussi le délai de recouvrement, d'une durée moyenne de 19 mois et demi, car un euro récupéré dans près de vingt mois vaut moins d'un euro aujourd'hui (à 6 % par an, environ 0,91 €).

Regardons d'abord la **distribution**, qui n'a rien d'une cloche :


![Distribution de la perte en cas de défaut : en U (beaucoup de pertes quasi nulles ou quasi totales), et très différente selon la garantie.](figures/ch01-lgd.png)

La LGD moyenne est de 46 %. La forme est **en U** : 12 % des prêts sont intégralement récupérés (perte nulle), 9 % ne le sont presque pas du tout (perte supérieure à 95 %), et le reste se répartit entre les deux. La moyenne par garantie est très contrastée : **61 %** sans garantie (2 993 prêts), **37 %** avec nantissement (1 155 prêts), **27 %** avec caution (1 852 prêts).

Comment modéliser une grandeur bornée entre 0 et 1, en forme de U ? Quatre candidats, comparés sur 30 % de prêts de test (garantie, objet et montant comme variables) :

- la **moyenne globale** (la référence naïve) ;
- la **régression linéaire**, qui peut sortir de $[0,1]$ ;
- la **régression « fractionnelle »** : un GLM binomial avec lien logit, appliqué à la LGD prise comme une proportion (volume II, section 2.2 pour le lien logit), qui reste dans $[0,1]$ ;
- un **modèle en deux étapes** : la probabilité d'une perte nulle (régression logistique), puis la LGD moyenne parmi les pertes non nulles (régression fractionnelle).

```text
                           erreur absolue    RMSE      R²
moyenne globale                    0.3063  0.3443 -0.0003
régression linéaire                0.2591  0.3047  0.2165
régression fractionnelle           0.2591  0.3048  0.2163
deux étapes                        0.2591  0.3048  0.2163
vraie espérance (plafond)          0.2577  0.3049  0.2158
```


Les trois modèles font **exactement aussi bien** (erreur absolue 0,259, $R^2=0{,}216$) et dépassent nettement la moyenne globale (0,306 ; $R^2$ nul). Le plafond lui-même, la vraie espérance conditionnelle connue par construction, n'est pas plus haut : **ce que l'on prédit de la LGD d'un prêt individuel est très limité**. La garantie explique la **moyenne** d'un segment, mais, à l'intérieur d'un segment, les pertes restent dispersées entre 0 et 1. La précision d'une LGD se juge donc **par segment**, et l'erreur individuelle importe peu pour une provision de portefeuille (où seule la moyenne compte).

⚠️ Trois précautions. D'abord, le recouvrement est **tardif et censuré** : les défauts récents n'ont pas fini de se recouvrer, et leur LGD observée est trop basse (on les exclut, ou on projette). Ensuite, les LGD sont **plus fortes en période de crise** (garanties moins valorisées, recouvrements plus lents) : les approches réglementaires demandent une LGD « de ralentissement » (*downturn*), ce que notre fichier ne permet pas d'estimer. Enfin, la régression linéaire peut sortir de $[0,1]$ avec d'autres variables ; ici, avec trois variables catégorielles, elle s'en abstient et l'écart n'apparaît pas.

### 1.5.3 L'EAD : ce que l'on aura prêté au moment du défaut

Pour un prêt amortissable, l'exposition à une date est connue (un tableau d'amortissement). Pour une **ligne de crédit renouvelable** (découvert, carte), le client peut **tirer** davantage avant de faire défaut. On modélise l'exposition au défaut par

$$\text{EAD}=\text{tirage}+\text{CCF}\times(\text{limite}-\text{tirage}),$$

où le **facteur de conversion en crédit** (CCF, *credit conversion factor*) est la part du montant **non tiré** qui sera tirée avant le défaut. Dans `revolving_defauts.csv`, 8 000 lignes qui ont fait défaut, avec leur tirage un an avant :

```text
            utilisation_moy  ccf_moyen
quintile 1            0.137      0.495
quintile 2            0.272      0.443
quintile 3            0.383      0.414
quintile 4            0.506      0.357
quintile 5            0.691      0.299
EAD réelle totale 23.8 M€ ; tirages un an avant 14.5 M€ ; EAD par CCF moyen 23.4 M€
```


Le CCF moyen est de 0,40 : en moyenne, **40 % de ce qui n'était pas tiré l'est avant le défaut**. Il est plus fort pour les lignes **peu utilisées** (0,50 dans le premier quintile d'utilisation, 0,30 dans le dernier) : un client en difficulté vide sa réserve. Retenir comme EAD le tirage d'un an avant donnerait 14,5 M€ pour 23,8 M€ réellement exposés : l'exposition serait **sous-estimée de 39 %**. Appliquer le CCF moyen donne 23,4 M€, à 2 % de la réalité ; une régression du CCF sur l'utilisation (pente −0,35, $R^2$ de 0,10) est un progrès modeste. Comme pour la LGD, la moyenne est bien estimée, le détail individuel beaucoup moins.

### 1.5.4 IFRS 9 : trois étapes

La norme **IFRS 9** (en vigueur depuis 2018, dans l'état de nos connaissances ; à vérifier) remplace le provisionnement sur pertes **subies** par un provisionnement sur pertes **attendues**. Le principe est un classement des prêts en **trois étapes** (*stages*) :

| Étape | Situation du prêt | Provision |
|---|---|---|
| **1** | risque de crédit **pas sensiblement accru** depuis l'octroi | perte attendue à **12 mois** |
| **2** | risque de crédit **sensiblement accru** depuis l'octroi, sans défaut | perte attendue **sur la durée de vie** |
| **3** | **défaut avéré** | perte attendue sur la durée de vie, sur un prêt en défaut (PD = 1) |

L'idée est **prospective** : on n'attend pas le défaut pour provisionner, on le fait dès que le risque se dégrade nettement. La norme laisse à chaque établissement la définition précise de la « hausse sensible » ; elle fournit seulement des présomptions (un retard de plus de 30 jours signale en général une hausse sensible, un retard de plus de 90 jours un défaut). Nos **règles d'exemple**, sur les 20 000 prêts de `portefeuille_ifrs9.csv`, sont :

- étape **3** : retard de 90 jours ou plus ;
- étape **2** : retard de 30 jours ou plus, **ou** PD actuelle supérieure à 2,5 fois la PD d'origine, **ou** prêt restructuré ;
- étape **1** : tous les autres.

```text
         prets   ead_M  ecl_M  couverture_%
etape                                      
1      16607.0  251.65   2.92          1.16
2       2923.0   43.43   1.78          4.09
3        470.0    7.32   2.89         39.48
total  20000.0  302.41   7.59          2.51
```


Le portefeuille compte 16 607 prêts en étape 1, 2 923 en étape 2 et 470 en étape 3, pour une exposition de 302 M€ et une **perte attendue totale de 7,6 M€** (2,5 % de l'exposition). La **couverture** (perte attendue rapportée à l'exposition) croît fortement d'une étape à l'autre : 1,2 % pour l'étape 1, 4,1 % pour l'étape 2, 39 % pour l'étape 3. Le passage d'une étape à l'autre est un **effet de seuil** : si l'on provisionnait **tout le portefeuille sur 12 mois**, la perte attendue serait de 4,1 M€ ; **tout sur la durée de vie**, de 6,7 M€, soit 1,6 fois plus, pour une durée résiduelle moyenne de 3,7 ans. Un prêt qui bascule en étape 2 voit donc sa provision **augmenter d'un coup**, ce qui rend le résultat de la banque **sensible aux règles de basculement**, un point que les régulateurs et les auditeurs examinent de près.

La perte attendue d'un prêt en étape 2 est la **somme sur les années** de sa vie résiduelle : probabilité de défaut dans l'année $t$ ($(1-h)^{t-1}h$, avec $h$ la PD annuelle), perte en cas de défaut et exposition à cette date (qui diminue avec l'amortissement), **actualisés** au taux d'intérêt effectif du prêt. Le détail est dans le cahier (application 1.7).

### 1.5.5 Le regard vers l'avant : les scénarios

IFRS 9 demande que la perte attendue reflète des **informations prospectives**, donc la conjoncture attendue et non seulement celle d'hier. Les établissements calculent la perte sous **plusieurs scénarios macroéconomiques** et en font une **moyenne pondérée par leur probabilité**. Pour traduire un scénario en PD, on s'appuie sur la relation historique entre conjoncture et défauts, celle de `taux_defaut_macro.csv` : une régression du logit du taux de défaut trimestriel sur la croissance, le chômage et la variation de l'immobilier.

```text
const            -5.030
croissance_pib   -0.401
chomage           0.245
variation_immo   -0.063
R² = 0.989
             croissance  chômage  immobilier  défaut modélisé (%)  poids  ECL (M€)
central             1.4      8.2         0.6                 2.61    0.5      7.59
défavorable        -1.0      9.5        -2.5                10.51    0.3     19.89
favorable           2.4      7.4         2.5                 1.29    0.2      5.27
```


La régression explique l'essentiel des variations du logit du taux de défaut ($R^2=0{,}99$ sur l'historique) : un point de croissance en moins multiplie la cote de défaut par 1,5 (+49 %), un point de chômage en plus de 28 %. Le scénario **central** (la conjoncture moyenne de l'historique) donne 2,6 % de défaut ; le **défavorable** (récession modérée, chômage à 9,5 %, immobilier en baisse), 10,5 % ; le **favorable**, 1,3 %. Nous multiplions la PD de chaque prêt par le rapport entre le taux du scénario et celui du central (les étapes restent fixes pour simplifier : dans la réalité, un scénario défavorable fait aussi **basculer** des prêts en étape 2).

La perte attendue vaut 7,6 M€ dans le scénario central, 19,9 M€ dans le défavorable (multipliée par 2,6) et 5,3 M€ dans le favorable. Pondérées à 50 / 30 / 20 %, elles donnent une **perte attendue pondérée de 10,8 M€**, soit environ **43 % de plus que le central**. Un point mérite d'être compris : la perte au **scénario moyen** (la conjoncture pondérée : croissance 0,9 %, chômage 8,4 %) serait de 9,1 M€, **moins** que la perte pondérée des trois scénarios : la perte est une fonction **convexe** de la conjoncture (un mauvais scénario coûte plus que ce que gagne un bon), si bien que moyenner la conjoncture **sous-estime** la perte moyenne de 1,7 M€. C'est la raison pour laquelle la norme demande plusieurs scénarios et non un scénario « moyen ».

Enfin, la **sensibilité** de la provision à la PD est quasi linéaire pour les étapes 1 et 2 : une PD multipliée par 2 donne 11,9 M€ (1,6 fois la perte centrale, pas 2 fois, parce que l'étape 3, 2,9 M€, est insensible à la PD) et multipliée par 3, 16,0 M€.

⚠️ **Limites.** Les scénarios et leurs pondérations sont des **jugements**, que les auditeurs examinent ; la relation macro-défaut est estimée sur 80 trimestres d'**un seul portefeuille** ; les PD de `portefeuille_ifrs9.csv` sont supposées déjà « à la date » ; la LGD de ce fichier n'est pas ralentie.

> ✅ **À retenir.**
> - $\text{ECL}=\text{PD}\times\text{LGD}\times\text{EAD}$ : trois grandeurs modélisées séparément. La perte attendue est un **coût prévisible**, pas un risque.
> - **PD** : à 12 mois ou sur la vie ($1-(1-h)^T$ si le risque est constant). **LGD** : en U, très liée à la garantie, **peu prévisible individuellement** (les trois modèles testés ont le même $R^2$ de 0,22, plafond compris) mais bien estimée par segment. **EAD** : le CCF capte la part tirée avant le défaut (0,40 en moyenne) ; ignorer le tirage futur sous-estime l'exposition de 39 %.
> - **IFRS 9** : étape 1 (12 mois), étape 2 (durée de vie, après hausse sensible du risque), étape 3 (défaut). Le passage de 1 à 2 multiplie la provision (de 1,6 en moyenne ici).
> - Les **scénarios** pondérés remplacent un scénario moyen : la perte est **convexe** en la conjoncture, moyenner la conjoncture sous-estime la perte.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.6 et 1.7, exercices 1.11 et 1.12.


## 1.6 ➕ Migration de notations et matrices de transition

> 🧭 **Section optionnelle.** Elle étudie la **dynamique** du risque : une note n'est pas figée, elle monte et descend, et la probabilité qu'un emprunteur fasse défaut dans cinq ans dépend de ce chemin.

Les banques et les agences de notation rangent les emprunteurs dans une **échelle de notes** (ici de 1, la meilleure, à 7, la plus risquée) et suivent leur évolution chaque année. Le tableau des probabilités de passer d'une note à une autre est la **matrice de transition**. Elle sert à trois choses : estimer la probabilité de défaut **à plusieurs années** (1.6.4), anticiper la **dégradation** d'un portefeuille (c'est un moteur des étapes IFRS 9 de la section 1.5), et simuler des scénarios de crise. Cette section l'estime sur dix ans de notes, la compare à la **vérité programmée**, et montre pourquoi une matrice « moyenne » trompe en période de crise.


### 1.6.1 Qu'est-ce qu'une matrice de transition ?

Notons $X_t$ la note d'un emprunteur à la fin de l'année $t$, dans $\{1,\dots,7\}$, plus l'état **défaut** (noté 8). La matrice de transition annuelle $P$ a pour coefficient $P_{ij}=P(X_{t+1}=j\mid X_t=i)$ : chaque **ligne** est une distribution de probabilité (la somme vaut 1). Deux propriétés la structurent :

- le **défaut est absorbant** : un emprunteur en défaut y reste ($P_{88}=1$) ; la matrice complète est donc de taille $8\times8$, dont nous estimons les 7 premières lignes ;
- les notes bougent **peu** : la **diagonale** domine (on garde la même note le plus souvent), et les passages d'une note à la voisine sont bien plus fréquents que les sauts de plusieurs crans.

La dernière colonne est la **probabilité de défaut à un an** de chaque note : c'est le lien avec tout ce qui précède. Voici la matrice **vraie** utilisée pour simuler les données (une année « neutre », sans choc de conjoncture) :

```text
           1     2     3     4     5     6     7  défaut
note 1  91.5   7.0   1.0   0.3   0.1   0.0   0.0     0.1
note 2   4.0  88.0   6.0   1.2   0.4   0.2   0.1     0.1
note 3   0.5   6.0  86.0   5.5   1.2   0.4   0.2     0.2
note 4   0.2   1.0   7.0  83.0   6.2   1.5   0.6     0.5
note 5   0.1   0.3   1.2   7.5  80.0   7.0   2.2     1.7
note 6   0.0   0.2   0.4   1.5   8.0  76.0   8.0     5.9
note 7   0.0   0.0   0.2   0.5   2.0   9.0  60.0    28.3
```

Lecture : un emprunteur noté 4 a 83,0 % de chances de rester en 4, 7,0 % de passer en 3 (amélioration), 6,2 % en 5, et **0,5 % de faire défaut dans l'année**. La note 7, la plus risquée, fait défaut dans plus d'un cas sur quatre (28,3 %).

### 1.6.2 Estimer par cohortes

L'estimation la plus simple s'appelle la **méthode des cohortes** : pour chaque note de départ $i$, on compte parmi les emprunteurs notés $i$ en début d'année combien se retrouvent dans l'état $j$ en fin d'année, et l'on divise :

$$\widehat P_{ij}=\frac{N_{ij}}{N_{i\cdot}}.$$

C'est l'estimateur du maximum de vraisemblance d'un modèle multinomial, indépendamment pour chaque ligne. Il reste une question pratique : que fait-on des emprunteurs **dont la note est retirée** (sortie du portefeuille, remboursement anticipé, perte de contact) ? On les compte à part et on les **retire du dénominateur** de l'année : l'hypothèse est que leur sortie n'informe pas sur leur risque, ce qui est une hypothèse (elle est vraie dans nos données, où 4 % sortent chaque année au hasard ; elle est souvent fausse dans la réalité, où l'on sort plus volontiers quand tout va bien, ou quand tout va très mal).

Voici les effectifs de transitions du panel (5 000 emprunteurs suivis jusqu'à dix ans, 39 102 observations « emprunteur-année »), avant la division :

```text
        sortie     1     2     3     4     5     6    7  défaut
note 1      96  2150   205    29     1     2     0    0       1
note 2     280   254  5669   447    91    31    16    6       6
note 3     404    55   605  8401   625   174    46   26      23
note 4     390    26    91   653  7770   650   163   75      55
note 5     215     2     8    56   416  4179   439  141     109
note 6     115     0     5     3    44   174  1977  279     186
note 7      37     0     0     0     5    20    87  702     387
```

Les effectifs sont très inégaux : 10 359 emprunteurs-années pour la note 3, 1 238 pour la note 7. Les transitions rares (un saut de la note 1 à la note 5) reposent sur quelques cas ou aucun, d'où l'importance de l'**incertitude**. Pour la mesurer, on rééchantillonne les **emprunteurs** (et non les lignes : les années d'un même emprunteur ne sont pas indépendantes) : c'est un bootstrap par grappes.


```text
        PD vraie (%)  PD estimée (%)  IC bas  IC haut
note 1           0.1            0.04    0.00     0.13
note 2           0.1            0.09    0.03     0.19
note 3           0.2            0.23    0.15     0.33
note 4           0.5            0.58    0.44     0.73
note 5           1.7            2.04    1.65     2.45
note 6           5.9            6.97    6.14     8.00
note 7          28.3           32.22   29.59    34.71
```


La probabilité de défaut estimée est **systématiquement supérieure** à la vraie pour les notes risquées (7,0 % contre 5,9 % pour la note 6, 32,2 % contre 28,3 % pour la note 7), et la vraie valeur sort de l'intervalle de confiance pour deux notes sur sept (6 et 7) : ce n'est pas un défaut de l'estimateur, mais une **révélation**. La matrice vraie décrit une année neutre ; or le panel contient dix années dont **deux de récession**, qui augmentent les dégradations. La matrice estimée est donc une **moyenne sur le cycle**, plus sombre qu'une année neutre. Voyons-le.


![À gauche, matrice de transition estimée par cohortes ; à droite, son écart avec la matrice vraie d'une année neutre : la diagonale est plus faible et les dégradations plus fortes.](figures/ch01-migration.png)

### 1.6.3 La conjoncture déforme la matrice

Séparons les années. Le taux de défaut de l'ensemble du panel et la part d'emprunteurs **dégradés** (note de fin plus mauvaise que celle de début) varient fortement :

```text
annee               0        1        2        3        4        5        6        7        8        9
emprunteurs   5000.00  4755.00  4517.00  4268.00  4041.00  3814.00  3527.00  3260.00  3046.00  2874.00
defauts_pct      1.10     1.07     1.44     1.34     1.76     3.64     4.17     2.39     1.77     1.74
degrades_pct     7.42     7.00     8.10     9.98    12.00    19.87    19.14    11.60     7.78     6.40
```


Les années 5 et 6 se détachent : le taux de défaut passe de 1,1–1,8 % les années ordinaires à 3,6–4,2 %, et la part de dégradations passe de 6–12 % à près de 20 %. Comparons les matrices estimées sur **deux sous-périodes** : les années calmes (0 à 3, 8 et 9) et la récession (5 et 6).

```text
        PD calme (%)  PD récession (%)  défauts calme  défauts récession  rapport
note 1          0.07              0.00              1                  0     0.00
note 2          0.08              0.08              3                  1     1.04
note 3          0.13              0.49              8                  9     3.85
note 4          0.45              1.11             28                 18     2.46
note 5          1.39              4.71             46                 49     3.38
note 6          4.95             14.07             79                 76     2.84
note 7         24.49             51.55            167                133     2.11
```


Pour les notes de milieu d'échelle (de 3 à 6), la **probabilité de défaut est multipliée par 2,5 à 3,9** en récession : pour la note 5, de 1,4 % à 4,7 %. Pour les deux premières notes, les défauts sont si rares (de zéro à trois par sous-période) que le rapport n'a pas de sens : c'est la limite de toute estimation de transitions rares. Pour la note 7, le rapport est de 2,1 seulement : une PD déjà élevée (24,5 % en période calme) ne peut pas être multipliée par plus de 4. Le facteur programmé dans le simulateur, qui multiplie les probabilités brutes de dégradation par $e^{0{,}6\,\Delta z}\approx2{,}75$ avant renormalisation, retrouve cet ordre de grandeur.

> 💡 **« Sur le cycle » ou « à la date » ?** La matrice moyenne (1.6.2) convient à un horizon long et au capital, qui doit survivre à une crise. La matrice d'une année donnée (ou d'un état de la conjoncture) convient aux provisions (section 1.5), qui doivent refléter la situation et les perspectives. Utiliser la moyenne pour provisionner **sous-estime** la perte d'une récession et **surestime** celle d'une expansion. Les établissements estiment pour cela des matrices **conditionnelles** à un indicateur de conjoncture, ce que l'on fait ici de la façon la plus simple : une matrice par régime.

### 1.6.4 La probabilité de défaut à plusieurs années

La force d'une matrice est de donner la PD à **horizon $n$ années**. Si les transitions sont indépendantes d'une année à l'autre (propriété de Markov) et si la matrice est la même chaque année (homogénéité), la matrice à $n$ ans est la puissance $n$ de la matrice annuelle : $P^{(n)}=P^n$. Avec le défaut absorbant, la dernière colonne de $P^n$ est la **probabilité de défaut cumulée** à $n$ ans pour chaque note de départ.

```python
M_abs = np.vstack([M_hat, np.r_[np.zeros(7), 1.0]])       # ajoute la ligne « défaut → défaut » : l'état est absorbant
PD_5 = np.linalg.matrix_power(M_abs, 5)[:7, 7]             # défaut cumulé à 5 ans, note par note
print((100 * PD_5).round(1))
```
<!--sortie-->
```text
[ 0.4  1.2  2.7  6.5 17.  39.3 76.5]
```

À 5 ans, la note 1 a 0,4 % de risque cumulé et la note 7 en a 76,5 % : trois emprunteurs sur quatre sont en défaut avant cinq ans. Comparons cette prédiction à ce que l'on observe réellement, en suivant la **cohorte initiale** (les 5 000 emprunteurs de l'année 0, suivis sur cinq ans, les retraits étant traités comme des sorties sans défaut), et à la valeur vraie $P^5$ de la matrice neutre :

```text
        matrice estimée (%)  matrice vraie (%)  cohorte 0 observée (%)
note 1                  0.4                0.6                     0.5
note 2                  1.2                1.0                     0.8
note 3                  2.7                2.0                     1.1
note 4                  6.5                5.0                     5.2
note 5                 17.0               13.3                    10.8
note 6                 39.3               31.7                    28.1
note 7                 76.5               69.5                    63.0
```


![Probabilité de défaut cumulée selon l'horizon, pour quatre notes de départ : la matrice estimée sur dix ans (trait plein) est plus sombre que la matrice neutre (tirets), et l'écart se creuse avec l'horizon.](figures/ch01-pd-cumulee.png)

Trois lectures. **Premièrement**, la PD cumulée croît **plus vite que proportionnellement** au nombre d'années pour les notes **bonnes** (note 3 : 2,7 % à 5 ans pour 0,23 % à un an, soit douze fois plus pour cinq fois plus de temps), parce que ces emprunteurs migrent d'abord vers des notes plus risquées avant de faire défaut ; elle s'**aplatit** pour les notes très mauvaises (saturation). **Deuxièmement**, la matrice estimée donne des PD à 5 ans plus fortes que la matrice neutre (note 5 : 17,0 % contre 13,3 %), puisqu'elle intègre la récession : les erreurs **se cumulent** avec l'horizon. **Troisièmement**, la cohorte de l'année 0, qui traverse les années 0 à 4, donc **avant** la récession, observe moins de défauts que les deux matrices (note 5 : 10,8 %) : la matrice annuelle moyenne n'est ni la cohorte passée ni la cohorte à venir. L'écart n'est pas une erreur de calcul : c'est la différence entre **la moyenne du cycle** et **un morceau particulier du cycle**.

### 1.6.5 Les hypothèses : Markov, homogénéité

Le calcul $P^n$ suppose deux choses, qu'on **teste** avant de s'y fier.

**La propriété de Markov** : la note de demain ne dépend que de celle d'aujourd'hui, pas du chemin parcouru. Dans la réalité, il existe souvent un **effet d'élan** (*momentum*) : un emprunteur récemment dégradé a plus de chances de l'être encore que celui qui est resté stable. Testons-le sur les emprunteurs notés 4 : sont-ils plus risqués s'ils viennent de **plus haut** (ils ont été dégradés), de **plus bas** (ils se sont améliorés) ou s'ils étaient déjà 4 l'année précédente ?

```text
col_0                         amélioré  défaut  dégradé  inchangé  sorti
origine                                                                 
vient d'une note meilleure         7.1     0.4      9.2      80.7    2.6
vient d'une note moins bonne       8.7     0.9      9.6      77.5    3.3
était déjà 4                       7.7     0.6      9.5      78.1    4.2
test du khi-deux d'indépendance : p = 0.49
```


Les distributions d'issue sont **semblables** quelle que soit l'origine (la probabilité de dégradation reste autour de 9 à 10 %, celle de défaut, sous 1 %) et le test d'indépendance donne $p=0{,}49$ : nous **ne détectons aucun effet d'élan**, ce qui est cohérent avec la vérité, puisque nos données ont été simulées avec des transitions de Markov. Sur des données réelles, ce test conclut souvent le contraire, et l'on enrichit alors le modèle (l'état devient la note **et** la note précédente, ou la durée dans la note).

**L'homogénéité dans le temps** est, elle, manifestement **fausse** ici : on vient de voir que deux années sur dix multiplient les défauts par trois. Un test d'homogénéité formel compare les matrices de deux périodes (khi-deux de comparaison ligne par ligne) ; il rejette massivement pour les notes de milieu d'échelle. Conséquence pratique : la puissance $P^n$ d'une matrice moyenne est une **approximation**, valable en moyenne sur un cycle et trompeuse un jour de crise.

### 1.6.6 Un mot sur le temps continu

Une année est un pas arbitraire : on voudrait la probabilité de transition sur six mois, ou sur dix-huit. Le modèle à **temps continu** décrit les transitions par un **générateur** $Q$ (taux instantanés de passage d'une note à l'autre) tel que $P(t)=e^{tQ}$. On l'obtient formellement par le **logarithme matriciel** $Q=\ln P$, que l'on peut calculer sur la matrice estimée :

```text
coefficients hors diagonale négatifs : 7  (le plus bas : -0.001)
[[-0.107  0.097  0.01  -0.001]
 [ 0.044 -0.145  0.079  0.013]
 [ 0.005  0.071 -0.176  0.074]]
```


Le logarithme de la matrice estimée contient 7 **taux négatifs** (très petits : −0,001 au plus bas, dans les transitions les plus rares), ce qui n'a pas de sens pour un taux de passage. Une matrice annuelle est dite **plongeable** (*embeddable*) quand un générateur valide existe ; l'estimée ne l'est pas. On la **régularise** alors (on remplace les taux négatifs par zéro et l'on renormalise la diagonale) ou l'on estime directement le générateur à partir des durées passées dans chaque note, ce qui est une autre méthode (l'estimateur de durée, à temps continu). Retenez la précaution : **la racine carrée ou le logarithme d'une matrice de transition n'est pas toujours une matrice de transition**.

> ✅ **À retenir.**
> - Une **matrice de transition** est une matrice stochastique dont la dernière colonne est la PD à un an ; le défaut est **absorbant**. L'estimateur par **cohortes** est un simple rapport d'effectifs ; son incertitude se mesure par un bootstrap **par emprunteur**.
> - Les **transitions rares** sont mal estimées ; les notes extrêmes ont peu d'observations.
> - La conjoncture **déforme** la matrice : en récession, la PD des notes intermédiaires est multipliée par 2,5 à 3,9 dans nos données. Une matrice moyenne sert le capital, une matrice conditionnelle sert les provisions.
> - La PD à $n$ ans est la dernière colonne de $P^n$, sous les hypothèses de **Markov** et d'**homogénéité**, qu'on teste : ici, pas d'effet d'élan, mais une forte hétérogénéité temporelle.
> - Le logarithme d'une matrice estimée n'est pas toujours un générateur valide.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.8, exercices 1.13 et 1.14.


## Bilan du chapitre 1

Vous savez maintenant :

- **cadrer** un score de crédit : population, définition du défaut, fenêtres d'observation et de performance, échantillons, et le garde-fou contre la fuite d'information (ne garder que ce que l'on sait à la date de la demande) ;
- **construire une grille de score** : découper en classes, calculer les **WOE** (à la main sur un exemple), estimer une régression logistique, écrire le résultat en **points** avec un score de base et un PDO, lire une carte et en expliquer un refus par ses **motifs** ;
- **mesurer l'effet des dossiers refusés** : une grille construite sur les seuls acceptés annonce 4,4 % de défaut alors que la population qui se présente en fait 6,0 % ;
- **comparer** une grille, une logistique brute et un boosting monotone sur un échantillon de test, avec des intervalles appariés, et comprendre **pourquoi** (la forme des effets, révélée par la vérité programmée) ;
- **mesurer** un score : AUC, **Gini = 2·AUC − 1** (démontré par la courbe CAP), **KS**, tableau de seuils, intervalle de bootstrap, **PSI**, calibration par note (test binomial, Hosmer–Lemeshow) et ses limites quand la conjoncture corrèle les défauts ;
- (en option) **juger un découpage** : IV (une divergence de Kullback–Leibler symétrisée), fusion monotone, classes rares, manquants informatifs, IV suspect ;
- (en option) **chiffrer une perte attendue** : PD à 12 mois et sur la vie, LGD (en U, peu prévisible individuellement), CCF et EAD, **trois étapes IFRS 9**, scénarios macroéconomiques pondérés et effet de convexité ;
- (en option) **estimer une matrice de migration**, voir la conjoncture la déformer, calculer une PD à plusieurs années par puissance de matrice, **tester** Markov et noter les limites de l'homogénéité et du temps continu.

Le chapitre a mis des chiffres sur des idées qui restent souvent des slogans :

| Question | Ce que nous avons mesuré |
|---|---|
| Performance de la grille (test) | AUC 0,771 [0,752 ; 0,791], Gini 0,542, KS 0,406 |
| Grille contre logistique brute | +0,010 d'AUC, intervalle apparié [+0,001 ; +0,018] |
| Grille contre boosting monotone | −0,002 d'AUC, dans le bruit ; plafond (vraies formes) : 0,777 |
| Politique d'acceptation à 560 points | 78 % de demandes acceptées, 3,1 % de défaut parmi les acceptés |
| Grille construite sur les acceptés seuls | AUC 0,716 au lieu de 0,771 ; PD annoncée 4,4 % pour 6,0 % réels |
| Afflux de jeunes emprunteurs | PSI du score 0,129, de l'âge 0,246 ; la grille reste calibrée (8,7 % annoncés, 8,9 % observés) |
| Test binomial, 80 trimestres | 65 rejets ; sous une corrélation d'actifs de 3 %, il rejette à tort 85 % du temps |
| Jeu réel (carte de crédit) | AUC 0,728 (tout en nombres), 0,768 (statut en modalités), 0,791 (boosting) |
| IV d'une variable de bruit | 0,055 en développement, −0,016 en test (100 classes) |
| Ancienneté dans l'emploi | IV 0,258 avec le manquant en classe à part, 0,163 après imputation |
| LGD | moyenne 46 % (61 % sans garantie, 27 % avec caution) ; $R^2$ de 0,22, plafond compris |
| EAD d'une ligne renouvelable | CCF moyen 0,40 ; EAD sous-estimée de 39 % si l'on ignore les tirages futurs |
| Perte attendue IFRS 9 | 7,6 M€ (2,5 % de 302 M€) ; 10,8 M€ en pondérant trois scénarios, soit 43 % de plus |
| Migration en récession | PD des notes intermédiaires multipliée par 2,5 à 3,9 |
| PD à 5 ans de la note 5 | 17,0 % (matrice estimée), 13,3 % (matrice neutre), 10,8 % (cohorte observée avant la récession) |

Le fil conducteur du chapitre tient en une phrase : **un score de crédit est une cote écrite en points, et sa valeur se mesure par des indicateurs qui répondent à des questions différentes** (classe-t-il bien, est-il calibré, est-il stable, avec quelle incertitude). Chaque fois que nous avons comparé des modèles, la sophistication a apporté moins que la **forme des effets** et la **qualité des données** ; chaque fois que nous avons traduit un score en euros, l'hypothèse sur la conjoncture a pesé davantage que le modèle.

> 🧭 **En pratique : liste de contrôle d'un score de crédit.**
> 1. La population, la définition du défaut et les fenêtres sont écrites (1.1.2).
> 2. Aucune variable n'est postérieure à la date de la demande ; aucun IV n'est anormalement élevé (1.4.4).
> 3. Les classes sont assez peuplées, justifiées, monotones quand l'économie l'exige (1.1.3, 1.4.3).
> 4. Les refusés sont discutés : l'échantillon est-il représentatif des demandeurs (1.1.7) ?
> 5. Gini, KS, AUC sont donnés **avec leur intervalle**, sur un échantillon de test (1.3.5).
> 6. La calibration est contrôlée par note, avec un test qui tient compte de la corrélation (1.3.7).
> 7. La stabilité est surveillée (PSI du score et des variables, 1.3.6).
> 8. Les motifs de refus se lisent dans la carte (1.2.6).
> 9. La PD alimente une perte attendue avec LGD, EAD et scénarios documentés (1.5).

Le chapitre suivant change de métier, pas de logique : l'**assurance**. Une mutuelle ne prête pas, elle **promet** de payer des sinistres ; son risque est la **fréquence** et le **coût** de ces sinistres, que l'on modélise séparément et que l'on transforme en **prix** (un tarif) et en **provisions**, un chemin parallèle à celui de la PD, de la LGD et de l'EAD.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 à 1.8 (grille complète, inférence des rejets, comparaison de modèles, performance et stabilité, WOE et fusion monotone, LGD et CCF, perte attendue IFRS 9, matrice de migration) et exercices 1.1 à 1.14.
