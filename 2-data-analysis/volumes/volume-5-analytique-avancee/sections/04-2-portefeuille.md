## 4.2 Suivi de portefeuille

Un **portefeuille** est l'ensemble des contrats (ou des prêts) qu'une société détient à un moment donné. Le **suivi** consiste à le lire régulièrement, par segment et dans le temps, pour repérer ce qui se dégrade avant que les comptes ne le montrent. Nous commençons par l'assurance (où la question est « quels segments perdent de l'argent ? »), puis nous passons au crédit, qui demande des outils propres : les **tranches de retard**, les **cohortes** lues à âge égal, la **matrice de transition**, la **concentration**.

### 4.2.1 À l'assurance : mix et rentabilité par segment

On appelle **mix** la répartition du portefeuille entre ses segments (âge, zone, usage, canal de vente…). Un portefeuille est rentable si **chaque segment** paie, ou si les segments qui perdent sont assez petits pour être compensés. Pour le savoir, on met côte à côte, pour chaque segment, sa **part de l'exposition**, sa **part des primes**, sa **fréquence**, son **S/P** et son **ratio combiné**.

```python
t = O.table_sp(d, "classe_age").loc[["< 25 ans", "25-39 ans", "40-59 ans", "60 ans et +"]]
t["part_expo"] = t["exposition"] / t["exposition"].sum()
t["part_primes"] = t["primes"] / t["primes"].sum()
t["resultat_k"] = t["primes"] * (1 - t["combine"]) / 1e3
print((t[["part_expo", "part_primes", "frequence", "sp", "combine"]] * 100).round(1).join(t["resultat_k"].round(0)).to_string())
```
<!--sortie-->
```text
             part_expo  part_primes  frequence     sp  combine  resultat_k
classe_age                                                                
< 25 ans           7.4         18.2       22.5  102.1    130.1     -1301.0
25-39 ans         25.6         28.3        7.1   62.7     90.7       626.0
40-59 ans         48.4         36.8        5.1   57.5     85.5      1267.0
60 ans et +       18.5         16.7        6.0   60.2     88.2       468.0
```

Les moins de 25 ans représentent **7,4 %** de l'exposition et **18 %** des primes : ils paient cher, mais pas assez. Leur fréquence est de **22,5 %** par année-police, contre 5,1 % pour les 40-59 ans, soit **4,4 fois plus** ; leur S/P atteint **102 %** et leur ratio combiné **130 %**. Ce segment perd à lui seul environ **1,3 million d'euros** sur quatre ans, que gagnent les autres segments. Le tarif corrige le risque dans le bon sens, mais **pas assez** : nous le mesurerons avec un modèle en section 4.4.

> ⚠️ **Piège : lire un ratio par segment sans regarder le volume.** Un segment qui a un très mauvais ratio mais 3 % de l'exposition ne se traite pas comme un segment qui pèse 30 %. Et, on l'a vu en 4.1.6, un ratio de petit segment peut n'être que du hasard : un tableau de portefeuille sérieux donne, pour chaque ligne, **l'effectif et un intervalle**.

### 4.2.2 Au crédit : encours, tranches de retard et créances douteuses

La banque finance des particuliers (crédits à la consommation) et des professionnels (commerces, entreprises de services, du bâtiment, de la restauration, de l'industrie). Au total, **12 000 prêts** ont été octroyés de janvier 2022 à juin 2025, pour **180,7 M€** (9 062 prêts à des particuliers, 2 938 à des professionnels ; le prêt médian est de 9 900 €). Chaque mois, pour chaque prêt encore actif, on connaît l'**encours** (le capital restant dû) et le **nombre de jours de retard** sur la dernière échéance.

On range les prêts dans cinq **tranches de retard** : **0** (à jour), **1 à 29 jours**, **30 à 59 jours**, **60 à 89 jours**, et **90 jours ou plus**. La dernière est conventionnelle : on parle de **défaut** à partir de 90 jours de retard, et de **créances douteuses** pour les encours des prêts en défaut. Cette convention est un choix de gestion ; les cadres réglementaires internationaux en proposent des définitions plus détaillées, qui ne sont pas reproduites ici.

Trois indicateurs se déduisent de cette classification.

- Le **taux de créances douteuses** = créances douteuses ÷ (encours sain + créances douteuses).
- Les **provisions** : une somme mise de côté pour absorber les pertes attendues. Chaque tranche reçoit un **taux de provisionnement** : plus le retard est ancien, plus la probabilité de perte est grande. Pour l'exemple, nous prenons des taux **fictifs** (0,5 % pour les prêts à jour, 2 %, 10 %, 30 % puis 55 % pour la tranche 90+).
- Le **taux de couverture** = provisions totales ÷ créances douteuses : il dit quelle part des créances douteuses est « déjà couverte » par les provisions.

```python hide
pr = d["prets"]
print(len(pr), round(pr["montant"].sum() / 1e6, 1), pr["segment"].value_counts().to_dict(), pr["montant"].median(), pr["date_octroi"].min().date(), pr["date_octroi"].max().date())
assert round(pr["montant"].sum() / 1e6, 1) == 180.7 and pr["montant"].median() == 9900 and pr["date_octroi"].max() <= pd.Timestamp("2025-06-30")
```
<!--sortie-->
```text
12000 180.7 {'Particulier': 9062, 'Professionnel': 2938} 9900.0 2022-01-01 2025-06-28
```

Une limite du jeu de données doit être dite avant de calculer. Le suivi mensuel d'un prêt s'arrête **au mois du défaut** : on ne sait pas ce qui se passe ensuite (recouvrement, abandon de créance). Pour mesurer le stock de créances douteuses, nous faisons donc une **hypothèse de simplification** : un prêt entré en défaut reste douteux **douze mois** avant d'être passé en perte. C'est un choix d'école ; une banque réelle suit ses créances douteuses jusqu'à leur extinction.

```python
st = O.stock_mensuel(d)
cols = ["encours", "douteux", "taux_douteux", "couverture"]
sel = st.loc[pd.to_datetime(["2024-12-01", "2025-06-01", "2025-12-01"]), cols]
sel[["encours", "douteux"]] = (sel[["encours", "douteux"]] / 1e6).round(1)
print(sel.round(3).to_string())
```
<!--sortie-->
```text
            encours  douteux  taux_douteux  couverture
2024-12-01     70.7      2.9         0.039       0.745
2025-06-01     76.2      4.3         0.054       0.674
2025-12-01     56.7      4.5         0.073       0.625
```

Le taux de créances douteuses passe de **3,9 %** (décembre 2024) à **5,4 %** (juin 2025), puis à **7,3 %** (décembre 2025), et le taux de couverture baisse de 75 % à 62 %. Faut-il s'alarmer ? Il faut d'abord regarder le **dénominateur** : l'encours sain **baisse** de 76,2 à 56,7 M€ entre juin et décembre 2025. La raison est un fait propre à notre jeu de données : **aucun prêt n'a été octroyé après juin 2025**, le portefeuille s'éteint donc par amortissement, alors que les créances douteuses (entrées en défaut sur les douze derniers mois) ne diminuent presque pas. Une partie de la hausse du taux est donc **mécanique**.

> 💡 **Intuition.** Un ratio peut monter parce que son numérateur augmente **ou** parce que son dénominateur diminue. Sur un portefeuille qui s'éteint, ou sur un portefeuille jeune qui grossit vite, le taux de créances douteuses est un mauvais thermomètre. C'est une raison de plus pour suivre les **cohortes d'octroi** à âge égal, qui ne dépendent pas de la taille du portefeuille à la date de mesure.

### 4.2.3 Cohortes d'octroi : comparer à âge égal

Une **cohorte d'octroi** (ou **millésime**) regroupe les prêts accordés pendant une même période : ici, un semestre. Pour savoir si un millésime est plus risqué qu'un autre, la comparaison la plus simple consiste à calculer, pour chaque millésime, **la part des prêts passés en défaut**. Elle est trompeuse, comme le montre un exemple à la main.

> Le millésime « 2023 S1 » compte 1 000 prêts suivis depuis 24 mois : 90 sont en défaut, soit **9,0 %**. Le millésime « 2025 S1 » compte 1 000 prêts suivis depuis 6 mois : 18 sont en défaut, soit **1,8 %**. Le second est-il cinq fois meilleur ? Non : il a eu **quatre fois moins de temps** pour se dégrader. À six mois, le premier millésime en avait 20 sur 1 000, soit 2,0 % : presque identique.

Il faut donc comparer **à âge égal** : pour chaque millésime et chaque âge (en mois depuis l'octroi), on calcule le **risque de défaut du mois** (défauts du mois ÷ prêts encore suivis à cet âge), puis on **cumule** : la probabilité d'avoir fait défaut à l'âge *a* est 1 − Π(1 − risque du mois). La courbe s'arrête quand moins de 300 prêts restent suivis : c'est la **troncature à droite** (volume III, chapitre 4).

```python
cc = O.courbes_cohortes(d)
brut = O.defauts_par_millesime_brut(d)
print(pd.DataFrame({"brut": brut * 100}).join(cc.loc[[12, 18]].T * 100, how="left").round(1).to_string())
```
<!--sortie-->
```text
           brut   12    18
millesime                 
2022 S1     8.3  4.1   7.6
2022 S2     8.9  5.2   7.9
2023 S1     9.2  5.0   8.1
2023 S2     9.1  5.3   8.3
2024 S1    11.3  6.7  11.4
2024 S2     6.2  5.7   NaN
2025 S1     2.9  NaN   NaN
```

```python hide
O.fig_cohortes(d)
```
<!--sortie-->
```text
figure : ch04-cohortes.png
```

![À gauche, la part brute de prêts en défaut par millésime (trompeuse : les récents ont eu moins de temps). À droite, le défaut cumulé à âge égal : le millésime 2024 S1 se détache.](figures/ch04-cohortes.png)

Le taux brut classe les millésimes de façon absurde : 2025 S1 paraît le meilleur (2,9 %), 2024 S2 aussi (6,2 %). À âge égal, l'image est différente : à 12 mois, le millésime **2024 S1** est à **6,7 %** de défaut contre 4,1 à 5,3 % pour les quatre premiers millésimes ; à 18 mois, il est à **11,4 %** contre 7,6 à 8,3 %. C'est un millésime **plus risqué**, ce qui correspond à une explication plausible (des critères d'octroi relâchés au premier semestre 2024 : nous le savons parce que le simulateur l'a programmé, mais un analyste le *découvrirait* par cette analyse et irait vérifier auprès de la direction du crédit). Le millésime suivant (2024 S2) retrouve une courbe proche des autres.

> ⚠️ **Piège : une cohorte récente ne se juge pas sur son taux brut.** Un millésime qui n'a que trois mois ne dit rien de ses défauts à dix-huit mois. Les courbes à âge égal sont le seul outil honnête, **avec leurs effectifs** (on ne garde que les âges où il reste assez de prêts observés).

### 4.2.4 La matrice de transition des retards

Un prêt en retard de 15 jours ce mois-ci sera-t-il à jour, toujours en retard, ou plus en retard le mois prochain ? La **matrice de transition** répond : chaque ligne est la tranche de départ, chaque colonne la tranche d'arrivée un mois plus tard, chaque case la **part des prêts** qui font ce passage. On parle aussi de **roll rates** (taux de glissement).

Un exemple à la main. Sur 100 prêts à jour, 95 le restent, 4 passent à « 1-29 jours » et 1 sort (remboursé). Sur 50 prêts de la tranche « 1-29 jours », 40 reviennent à jour, 5 y restent et 5 glissent en « 30-59 jours ». La ligne « 0 » est donc (95 %, 4 %, 0 %, …, 1 %) et la ligne « 1-29 » est (80 %, 10 %, 10 %, …).

```python
n, p = O.matrice_transition(d)
print((p * 100).round(1).to_string())
```
<!--sortie-->
```text
suiv        0  1-29  30-59  60-89    90+  Sortie
tranche                                         
0        94.2   3.7    0.4    0.0    0.1     1.7
1-29     81.1   9.8    7.4    0.0    0.0     1.8
30-59    55.9   2.3    0.1   40.8    0.0     0.8
60-89     0.0   0.0    0.0    0.0  100.0     0.0
```

```python hide
O.fig_transitions(d)
```
<!--sortie-->
```text
figure : ch04-transitions.png
```

![Matrice de transition mensuelle entre tranches de retard (en pourcentage de la ligne). La colonne « Sortie » regroupe les prêts remboursés ou arrivés à échéance.](figures/ch04-transitions.png)

La lecture se fait ligne par ligne. Un prêt à jour le reste dans **94,2 %** des cas ; il passe en retard de 1 à 29 jours dans 3,7 % des cas ; 0,1 % des prêts à jour passent **directement** en défaut (ce sont des défauts « brutaux », sans retard préalable). Un prêt en retard de **30 à 59 jours** revient à jour dans 55,9 % des cas, mais glisse vers 60-89 jours dans **40,8 %** des cas. Un prêt de la tranche 60-89 jours passe en défaut **dans 100 % des cas**.

> ⚠️ **Cette dernière valeur est une simplification du simulateur.** Dans nos données simulées, aucun prêt en retard de 60 à 89 jours ne se redresse : c'est une propriété de la façon dont le simulateur fabrique les retards avant un défaut. Dans la réalité, certains prêts se régularisent, et le taux de 100 % serait nettement plus bas. Retenez la **méthode**, pas ce chiffre.

Cette matrice permet de passer du mois à un **horizon**. En la multipliant par elle-même (en rendant « 90+ » et « Sortie » absorbants, c'est-à-dire sans retour), on obtient la probabilité d'être en défaut dans 1, 3, 6 ou 12 mois selon la tranche de départ.

> 📐 **Pour qui veut la formule.** Si *P* est la matrice mensuelle (avec les états absorbants), la probabilité d'être dans l'état *j* dans *h* mois en partant de *i* est l'élément (*i*, *j*) de *P*ʰ. C'est le principe des chaînes de Markov ; l'hypothèse est que les transitions d'un mois ne dépendent que de l'état présent et sont stables dans le temps.

```python
print(O.proba_defaut_horizon(n).mul(100).round(1).to_string())
```
<!--sortie-->
```text
          1      3      6      12
0        0.1    0.5    1.6    3.7
1-29     0.0    3.2    4.5    6.5
30-59    0.0   41.0   41.6   42.9
60-89  100.0  100.0  100.0  100.0
```

Un prêt à jour fait défaut dans les 6 mois avec une probabilité de **1,6 %** ; un prêt en retard de moins de 30 jours, de **4,5 %** ; un prêt en retard de 30 à 59 jours, de **41,6 %**. On tient là un **outil de provisionnement** (les taux de provision par tranche doivent croître comme ces probabilités) et un **outil d'alerte** (la tranche 30-59 jours est un signal fort). La section 4.5 va plus loin en cherchant des signaux **avant** les premiers retards.

### 4.2.5 La concentration du portefeuille

Même si chaque prêt est sain, un portefeuille peut être **fragile** parce qu'il dépend trop d'un secteur, d'une région, d'un client. La **concentration** mesure cette dépendance. La mesure la plus simple est la **part** de chaque catégorie dans l'encours ; un indicateur de synthèse est l'**indice de Herfindahl-Hirschman** (HHI), la **somme des carrés des parts**.

> 📐 **HHI.** Pour *n* catégories de parts *s*₁, …, *s*ₙ (somme égale à 1) : HHI = Σ *s*ᵢ². Il vaut 1/*n* quand toutes les parts sont égales (diversification maximale) et 1 quand tout est dans une seule catégorie.

Par exemple, avec quatre catégories à 40 %, 30 %, 20 % et 10 % : 0,16 + 0,09 + 0,04 + 0,01 = **0,30**, à comparer à 1/4 = 0,25 pour une répartition égale.

```python
conc = O.concentration(d, "2025-06-01")
reg = O.concentration(d, "2025-06-01", "region")
pro = conc.drop("Particuliers") / conc.drop("Particuliers").sum()
print((conc * 100).round(1).to_dict())
print("HHI secteurs :", round(O.hhi(conc), 3), "| professionnels seuls :", round(O.hhi(pro), 3), "| régions :", round(O.hhi(reg), 3))
```
<!--sortie-->
```text
{'Particuliers': 48.7, 'Commerce': 16.3, 'Services': 13.1, 'Bâtiment': 9.9, 'Restauration': 7.0, 'Industrie': 5.0}
HHI secteurs : 0.298 | professionnels seuls : 0.232 | régions : 0.26
```

Au 30 juin 2025, les particuliers représentent **48,7 %** de l'encours sain ; le secteur le plus exposé parmi les professionnels est le **Commerce** (16,3 % de l'encours, soit **32 %** de l'encours professionnel). Le HHI des secteurs vaut **0,30** (minimum possible avec six catégories : 0,17), celui des professionnels seuls **0,23** (minimum 0,20) et celui des régions **0,26** (minimum 0,25 pour quatre régions) : les régions sont **très bien réparties**, les secteurs un peu moins.

La concentration n'est un risque que si elle rencontre un **choc** : un secteur qui se dégrade. C'est ce que montre la sous-section suivante.

### 4.2.6 Une dérive à repérer : Commerce et Restauration en 2025

Pour détecter une dérive, on compare le **taux de défaut** de chaque secteur sur deux périodes. Comme les prêts sont à des âges différents, on calcule un taux par **prêt-mois** (défauts ÷ nombre de prêts suivis dans le mois) que l'on annualise (multiplié par 12), et l'on y ajoute un **intervalle** fondé sur le nombre de défauts (loi de Poisson).

```python
g = O.risque_secteur(d)
a = g.pivot(index="secteur", columns="periode", values=["dfl", "taux"])
a["taux"] = (a["taux"] * 100).round(1)
print(a.loc[["Commerce", "Restauration", "Bâtiment", "Services", "Industrie", "Particuliers"]].to_string())
```
<!--sortie-->
```text
                dfl         taux      
periode       apres  avant apres avant
secteur                               
Commerce       53.0   27.0   8.8   6.0
Restauration   22.0   10.0   7.7   4.3
Bâtiment       20.0   17.0   5.4   6.0
Services       17.0   13.0   3.4   3.3
Industrie      10.0    4.0   5.1   2.7
Particuliers  285.0  214.0   4.7   4.5
```

```python hide
O.fig_secteurs(d)
```
<!--sortie-->
```text
figure : ch04-secteurs.png
```

![À gauche, taux de défaut annuel pour 100 prêts par secteur en 2024 et en 2025, avec intervalle à 95 %. À droite, la part de chaque secteur dans l'encours sain et l'indice de concentration.](figures/ch04-secteurs.png)

Le taux de défaut du **Commerce** passe de **6,0** à **8,8** défauts par an pour 100 prêts, celui de la **Restauration** de **4,3** à **7,7**. Pris séparément, chaque secteur a un intervalle large (dix défauts seulement pour la Restauration en 2024). En les regroupant, la comparaison devient plus nette : 37 défauts en 2024 et 75 défauts en 2025 pour les deux secteurs ensemble, soit **5,5 puis 8,5** défauts par an pour 100 prêts (un facteur 1,5). Un test sur la répartition des défauts entre les deux périodes (test binomial, en tenant compte des prêts-mois de chaque période) donne une **p-valeur de 0,03** : la hausse n'est probablement pas due au hasard. D'autres secteurs montrent aussi des variations (l'industrie passe de 4 à 10 défauts) mais avec **trop peu de défauts** pour conclure.

```python hide
from scipy.stats import binomtest
cr = g[g["secteur"].isin(["Commerce", "Restauration"])].groupby("periode")[["pm", "dfl"]].sum()
pv = binomtest(int(cr.loc["apres", "dfl"]), int(cr["dfl"].sum()), cr.loc["apres", "pm"] / cr["pm"].sum()).pvalue
print(cr.to_dict(), round(pv, 3), (12 * cr["dfl"] / cr["pm"] * 100).round(2).to_dict())
```
<!--sortie-->
```text
{'pm': {'apres': 10651, 'avant': 8149}, 'dfl': {'apres': 75, 'avant': 37}} 0.028 {'apres': 8.45, 'avant': 5.45}
```

La dérive de ces deux secteurs rencontre une **concentration** : ils représentent 23 % de l'encours sain. C'est exactement le genre de situation qu'un tableau de suivi doit signaler à la directrice : « *deux secteurs qui pèsent près du quart du portefeuille voient leur taux de défaut augmenter de moitié ; nous recommandons d'examiner les nouveaux octrois dans ces secteurs et de revoir les provisions.* » Cette phrase **n'affirme pas la cause** : le simulateur nous la dit (un choc programmé sur 2025), mais dans la réalité l'analyste signalerait le fait, proposerait des hypothèses (conjoncture, saisonnalité, un lot de dossiers particulier) et demanderait à la direction du crédit de les vérifier.

> ✅ **À retenir.** (1) À l'assurance, le **mix** et le **ratio par segment** (avec effectifs et intervalles) montrent où le portefeuille perd de l'argent ; (2) au crédit, on range les prêts en **tranches de retard** et l'on suit les **créances douteuses**, le **taux de couverture** et leurs **dénominateurs** ; (3) les **cohortes d'octroi** se comparent **à âge égal**, jamais sur le taux brut ; (4) la **matrice de transition** donne des probabilités de défaut par tranche et à différents horizons ; (5) la **concentration** (parts, HHI) mesure une fragilité qui devient un risque quand un choc la touche.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.3 (cohortes à âge égal), application 4.4 (matrice de transition et probabilités à horizon), exercices 4.4 à 4.6.
