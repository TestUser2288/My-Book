# Chapitre 12 : ➕ Analytique RH et des ressources humaines

> « Derrière chaque ligne de ce tableau, il y a quelqu'un qui peut le lire. »

> 🧭 **Chapitre complémentaire.** Il est entièrement facultatif : le reste du volume ne le suppose pas. Il applique les outils des chapitres 1 à 3 (intervalles de confiance, comparaisons, régression) à des questions sur les **personnes**, avec une particularité : le droit de calculer quelque chose ne dit rien du **droit de le conclure**, ni de le diffuser.

La gérante de la boutique vous écrit après le départ d'une vendeuse qui comptait sept ans d'ancienneté : « *Je perds des collaborateurs depuis quelques années. Est-ce un problème de salaire, d'heures supplémentaires, ou autre chose ? Et au passage : est-ce que mes équipes sont payées de façon équitable ?* »

Ces questions sont de celles où l'analyste a le plus de pouvoir et le plus de responsabilité. Le pouvoir, parce que des chiffres sur les départs ou sur les salaires influencent des décisions qui touchent des personnes. La responsabilité, parce que ces chiffres sont **fragiles** (les effectifs sont petits), **sensibles** (la rémunération, le genre, la santé) et **faciles à mal utiliser** (un « score de risque de départ » peut devenir un instrument de surveillance). Ce chapitre fait donc deux choses à la fois : il vous donne les outils de l'analyse RH (taux de rotation, absentéisme, courbes de survie, écarts de salaire, modèles de départ) et il vous apprend à **dire ce que ces outils ne permettent pas de conclure**.

Trois idées l'organisent. La première est que **l'incertitude est la règle** : avec une cinquantaine de personnes et une vingtaine de départs en cinq ans, un taux de rotation est entouré d'un intervalle large, et comparer deux équipes revient presque toujours à comparer du bruit. La deuxième est que **un écart ajusté n'est pas une explication** : à poste et ancienneté égaux, un écart de salaire entre femmes et hommes peut subsister ; il signale une question, il ne prouve ni ne réfute une discrimination. La troisième est que **prédire n'est pas décider** : un modèle de départ avec vingt événements ne prédit rien d'utile, et même avec davantage de données, l'utiliser sur des personnes pose des questions d'éthique avant d'en poser de technique.

> ⚠️ **Ce que ce chapitre n'est pas.** Ce n'est pas un conseil juridique ni un cours de gestion des ressources humaines. Les règles sur les données des salariés (ce que l'on peut collecter, conserver, publier, ce que les personnes peuvent demander) dépendent du pays et du secteur : nous parlons de **principes communs** et vous renvoyons, pour votre cas, aux personnes compétentes (la direction juridique, le délégué à la protection des données, les représentants du personnel).

## Le chemin de ce chapitre

| Section | Question | Idée centrale |
|---|---|---|
| 12.1 | Combien de personnes partent, absentes, et depuis quand restent-elles ? | Taux de rotation avec intervalle exact, absentéisme, courbe de survie ; la prudence sur les petits effectifs |
| 12.2 | Les salaires sont-ils équitables ? | Écart brut et écart ajusté, compa-ratio ; ce que l'on peut et ne peut pas conclure ; ne pas publier de petits groupes |
| 12.3 | Peut-on prédire les départs ? Doit-on ? | Un modèle logistique, sa performance honnête, la puissance qui manque ; les limites éthiques |

## Les données du chapitre

> 📦 **Données simulées.** Tous les fichiers sont **simulés** (graines fixes, générateur `build/donnees_a3.py`) : la boutique, ses collaborateurs et leurs départs sont fictifs. Aucun identifiant ne renvoie à une vraie personne, et nous connaissons la **vérité programmée**, que nous révélerons en fin de chapitre.

- `employes_annees.csv` : **245 lignes collaborateur-année** (2021 à 2025) avec le poste, le site, le genre, l'ancienneté, le salaire brut mensuel, les heures supplémentaires par mois, les jours d'absence, l'évaluation annuelle, une indication de promotion et l'indicateur de départ dans l'année.
- `departs.csv` : les **20 départs** (date et motif).
- `employes.csv` : les **64 collaborateurs** (poste, site, genre).

Une précision d'honnêteté : ces collaborateurs sont ceux d'un **groupe** auquel appartient la boutique (entrepôt et siège compris), pas seulement les personnes payées par le compte de résultat de la boutique du chapitre 9. Surtout, les effectifs sont **petits** (de 47 à 52 personnes par an) : c'est le trait dominant de tout ce chapitre, et le comprendre est plus important que n'importe quelle formule.


Le fichier compte 245 lignes pour 64 collaborateurs et **20 départs** sur cinq ans ; l'effectif présent dans l'année va de 47 à 52 personnes.


## 12.1 Effectifs, turnover et absentéisme

Cette section pose les indicateurs de base d'un tableau de bord RH : l'**effectif**, le **taux de rotation** (turnover), l'**absentéisme** et la **durée de présence**. Pour chacun, elle donne la formule, le calcul sur les données de la boutique et, surtout, l'**intervalle d'incertitude**, que les petits effectifs rendent large.

### 12.1.1 Compter les personnes

Avant tout taux, il faut savoir de quoi l'on parle : qui est « dans l'effectif » ? Une personne partie en mars compte-t-elle pour l'année ? Un recrutement en novembre ? Les conventions diffèrent ; ce qui compte est d'en choisir **une**, de l'écrire (volume II, section 4.2) et de la tenir. Ici, l'effectif d'une année est le nombre de collaborateurs présents **à un moment** de l'année : une ligne du fichier par personne et par année.

```python
eff = ea.groupby("annee").agg(effectif=("id_employe", "size"), departs=("depart_dans_l_annee", "sum"))
eff["taux_rotation_%"] = (eff["departs"] / eff["effectif"] * 100).round(1)
print(eff.T)
```
<!--sortie-->
```text
annee            2021  2022  2023  2024  2025
effectif         47.0  48.0  50.0  52.0  48.0
departs           5.0   5.0   2.0   4.0   4.0
taux_rotation_%  10.6  10.4   4.0   7.7   8.3
```


Le **taux de rotation** annuel est le rapport entre le nombre de départs de l'année et l'effectif de l'année (on divise parfois par l'effectif **moyen** ; ici l'effectif présent dans l'année en fait office) :

$$\text{rotation}=\frac{\text{départs de l'année}}{\text{effectif de l'année}}.$$

Il vaut 10,6 % en 2021, 10,4 % en 2022, **4,0 % en 2023**, 7,7 % en 2024 et 8,3 % en 2025, soit 8,2 % sur l'ensemble. Une lecture hâtive dirait : « la rotation a été divisée par deux en 2023, la situation s'est améliorée, puis dégradée ». Nous allons voir que ce récit est un récit **que les données ne soutiennent pas**.

### 12.1.2 Un taux avec son intervalle : la loi de Poisson

Un nombre de départs est un **comptage** d'événements rares : on le modélise naturellement par une **loi de Poisson** (chapitre 1, section 1.2.2) dont le paramètre est le taux de départ par personne-année. Si $k$ départs sont observés pour une exposition de $E$ personnes-années, le taux estimé est $k/E$ et son **intervalle exact** (dit de Garwood) vient de la loi du khi-deux : la fonction `poisson_ic` de `build/outils_ch12.py` le calcule.

```python
for annee in (2021, 2023, 2025):
    k, E = int(eff.loc[annee, "departs"]), int(eff.loc[annee, "effectif"])
    t, bas, haut = O.poisson_ic(k, E)
    print(annee, k, "départs pour", E, "personnes :", round(t * 100, 1), "% [", round(bas * 100, 1), ";", round(haut * 100, 1), "]")
```
<!--sortie-->
```text
2021 5 départs pour 47 personnes : 10.6 % [ 3.5 ; 24.8 ]
2023 2 départs pour 50 personnes : 4.0 % [ 0.5 ; 14.4 ]
2025 4 départs pour 48 personnes : 8.3 % [ 2.3 ; 21.3 ]
```


En 2021, 10,6 % avec un intervalle de 3,5 à 24,8 % ; en 2023, 4,0 % avec un intervalle de **0,5 à 14,4 %** ; en 2025, 8,3 % de 2,3 à 21,3 %. Ces intervalles **se chevauchent tous** : la baisse de 2023 n'est pas distinguable du hasard. Sur cinq ans, le taux global de 8,2 % est estimé de 5,0 à 12,6 %.


![Taux de rotation annuel avec son intervalle de confiance exact à 95 % : tous les intervalles se recouvrent et contiennent le taux moyen des cinq ans (ligne pointillée).](figures/ch12-rotation.png)

> 💡 **Intuition.** Avec une cinquantaine de personnes, un départ de plus ou de moins change le taux de deux points. Le « bruit » vient de la **petite taille** de l'équipe, pas de la gestion. Avant d'expliquer une variation, demandez : *de combien de départs parle-t-on ?*

> ⚠️ **Piège.** Comparer un taux de rotation mensuel ou trimestriel est encore pire : avec vingt départs en soixante mois, la plupart des mois n'ont **aucun** départ. Pour ces effectifs, **l'année est la plus petite période lisible**.

### 12.1.3 Rotation volontaire, selon le motif

Tous les départs ne se valent pas. Un départ à la retraite ou une fin de contrat à durée déterminée est prévisible et rarement un signal ; une **démission** est le départ que l'entreprise cherche à comprendre. Le fichier des départs donne le motif.

```python
motifs = dep["motif"].value_counts()
print(motifs.to_frame("départs").assign(part_pct=(motifs / motifs.sum() * 100).round(0)))
```
<!--sortie-->
```text
                départs  part_pct
motif                            
démission            14      70.0
fin de contrat        3      15.0
retraite              2      10.0
licenciement          1       5.0
```


**14 des 20 départs (70 %) sont des démissions.** Le taux de **rotation volontaire** (démissions seules) vaut 5,7 % (3,1 à 9,6 %). C'est lui qui compte pour la gérante, plus que le taux global : les autres motifs relèvent du calendrier des contrats et de l'âge.

> 📒 **Pour s'entraîner.** Cahier, chapitre 12 : application 12.1, exercices 12.1 et 12.2.

### 12.1.4 Comparer des équipes : prudence

La gérante demande naturellement : *où est le problème, dans quel poste, dans quel site ?* La tentation est de calculer le taux de rotation par poste et de désigner le plus élevé. Faisons-le, mais **avec les intervalles**.

```python
par_poste = ea.groupby("poste").agg(personnes_annees=("id_employe", "size"), departs=("depart_dans_l_annee", "sum"))
rows = []
for poste, r in par_poste.iterrows():
    t, bas, haut = O.poisson_ic(int(r["departs"]), int(r["personnes_annees"]))
    rows.append((poste, int(r["personnes_annees"]), int(r["departs"]), round(t * 100, 1), round(bas * 100, 1), round(haut * 100, 1)))
print(pd.DataFrame(rows, columns=["poste", "pers.-années", "départs", "taux %", "bas", "haut"]).to_string(index=False))
```
<!--sortie-->
```text
         poste  pers.-années  départs  taux %  bas  haut
 Administratif             2        1    50.0  1.3 278.6
      Caissier            45        5    11.1  3.6  25.9
    Logistique            60        4     6.7  1.8  17.1
   Responsable            14        0     0.0  0.0  26.3
Service client            28        3    10.7  2.2  31.3
       Vendeur            96        7     7.3  2.9  15.0
```


Le plus fort taux apparent est celui du poste « Administratif » (**50,0 %**), mais il repose sur **2 personnes-années** et 1 départ : son intervalle couvre presque toute l'échelle (un taux annuel supérieur à 100 % n'a pas de sens : quand l'exposition est minuscule, l'intervalle exact d'un taux par personne-année déborde de l'échelle, ce qui dit simplement que l'on ne sait rien). Parmi les postes d'au moins vingt personnes-années, les taux vont de 6,7 % à 11,1 %, avec des intervalles qui se chevauchent largement. Au niveau des sites, la Boutique est à 7,7 % (4,0 à 13,5 %), l'Entrepôt à 6,7 % (1,8 à 17,1 %), le Siège à 13,3 % (3,6 à 34,1 %) : **aucune différence démontrable**.

> 🧭 **En pratique.** Pour de petits effectifs, ne publiez pas de taux par équipe sans intervalle, **et** écartez les équipes de moins d'une dizaine de personnes (le taux n'a aucun sens, et la personne qui part est identifiable : section 12.2.6). Regroupez (postes proches, deux années) pour gagner en précision.

### 12.1.5 Absentéisme

L'**absentéisme** mesure le temps de travail perdu. Deux indicateurs courants : le nombre moyen de **jours d'absence** par personne et par an, et le **taux d'absentéisme**, rapport entre les jours d'absence et les jours théoriquement travaillés. Le fichier donne les jours d'absence par collaborateur et par année ; nous supposons, pour l'illustration, **218 jours** théoriques par an (une valeur de référence pour un temps plein, à ajuster aux contrats réels).

```python
JOURS_THEORIQUES = 218
ab = ea.groupby("poste")["jours_absence"].agg(["mean", "median", "std", "count"])
ab["taux_%"] = (ab["mean"] / JOURS_THEORIQUES * 100).round(1)
print(ab.round(1))
```
<!--sortie-->
```text
                mean  median  std  count  taux_%
poste                                           
Administratif    8.5     8.5  0.7      2     3.9
Caissier         7.5     7.0  2.5     45     3.4
Logistique       8.8     9.0  3.8     60     4.0
Responsable      9.0     9.0  4.2     14     4.1
Service client   7.8     9.0  3.1     28     3.6
Vendeur          8.1     8.0  3.1     96     3.7
```


Un collaborateur est absent en moyenne **8,2 jours par an** (médiane de 8 ; intervalle de 7,8 à 8,6 jours), soit un **taux d'absentéisme de 3,7 %**. Les moyennes par poste sont proches ; un seul lien se détache dans ces données : les collaborateurs qui font plus d'**heures supplémentaires** sont plus souvent absents. La corrélation vaut 0,43 et la droite de régression indique environ **0,47 jour d'absence supplémentaire par heure supplémentaire mensuelle** : dix heures de plus par mois vont avec cinq jours d'absence de plus par an.

> ⚠️ **Piège.** Corrélation n'est pas causalité (chapitre 1, section 1.4). Les heures supplémentaires **fatiguent** peut-être (et provoquent des absences), mais les collaborateurs fréquemment absents peuvent aussi faire **moins** d'heures, ou les équipes en sous-effectif cumuler les deux. Ici la relation est programmée dans le sens heures vers absences ; en réalité, on ne le sait pas.

### 12.1.6 La durée de présence : la courbe de survie

Combien de temps un collaborateur reste-t-il ? Calculer « l'ancienneté moyenne des personnes parties » est un piège classique : cela ne prend en compte que les gens qui sont **partis**, ignorant ceux qui sont encore là. La bonne méthode est celle de l'**analyse de survie** : la courbe de **Kaplan-Meier** estime, pour chaque durée $t$, la probabilité de **rester au moins $t$ ans**, en utilisant à la fois les personnes parties et celles qui sont encore présentes (« censurées »).

> 📐 **Le principe, sur cinq personnes.** Observons des durées de présence (en années) : 1 (départ), 2 (départ), 2,5 (toujours là), 3 (départ), 4 (toujours là). À $t=1$, 5 personnes sont à risque et 1 part : la probabilité de rester passe à $4/5=0{,}8$. À $t=2$, 4 sont à risque, 1 part : on multiplie par $3/4$, soit $0{,}6$. La personne de 2,5 ans, encore présente, **sort du calcul** sans compter comme un départ. À $t=3$, 2 sont à risque (celles de 3 et 4 ans), 1 part : on multiplie par $1/2$, soit $0{,}3$. La courbe est le produit des « probabilités de rester à chaque départ » :
> $$\hat S(t)=\prod_{t_i\le t}\Bigl(1-\frac{d_i}{n_i}\Bigr).$$

Notre fichier n'observe les collaborateurs qu'à partir de 2021 : ceux entrés avant sont déjà dans l'entreprise à cette date (c'est la **troncature à gauche**), et la méthode en tient compte en ne les comptant dans le risque qu'**à partir de leur ancienneté d'entrée dans l'observation**. La bibliothèque `lifelines` le fait avec l'argument `entry`.

```python
from lifelines import KaplanMeierFitter
du = O.durees(ea, dep)
km = KaplanMeierFitter().fit(du["fin"], du["depart"], entry=du["entree"])
for t in (1, 3, 5, 8):
    s = km.survival_function_at_times([t]).iloc[0]
    print("reste au moins", t, "an(s) :", round(s * 100), "%")
```
<!--sortie-->
```text
reste au moins 1 an(s) : 90 %
reste au moins 3 an(s) : 73 %
reste au moins 5 an(s) : 53 %
reste au moins 8 an(s) : 44 %
```


![Courbe de survie de Kaplan-Meier des 64 collaborateurs : la probabilité de rester diminue avec l'ancienneté ; la bande grisée est l'intervalle de confiance à 95 %.](figures/ch12-survie.png)

Selon la courbe, **90 % des collaborateurs restent au moins un an, 73 % trois ans, 53 % cinq ans et 44 % huit ans**. L'incertitude est grande en bout de courbe : à la fin de l'observation (10,8 ans d'ancienneté maximale), l'intervalle de confiance va de 28 à 59 %, parce que peu de personnes ont une telle ancienneté. La courbe fournit un résultat **utile pour la gérante** (un collaborateur sur deux reste cinq ans environ, une perte sur dix la première année) que le simple taux de rotation ne dit pas.

> ✅ **À retenir.**
> - Un **taux de rotation** = départs / effectif ; avec 50 personnes, il se connaît à **plusieurs points près** (intervalle de Poisson exact).
> - **Ne pas expliquer** une variation sans avoir regardé son intervalle ; ne pas classer des équipes de quelques personnes.
> - Distinguer les **démissions** des autres départs.
> - L'**absentéisme** se lit par poste avec prudence ; un lien avec les heures supplémentaires est une corrélation, pas une preuve.
> - La **courbe de survie** (Kaplan-Meier) mesure la durée de présence en tenant compte des personnes encore là.

> 📒 **Pour s'entraîner.** Cahier, chapitre 12 : applications 12.2 et 12.3, exercices 12.3 et 12.4.


## 12.2 Rémunération et équité

Cette section traite de la question la plus délicate du chapitre : les salaires sont-ils équitables ? Elle décrit d'abord les salaires par poste et ce qui les explique (le poste, l'ancienneté), puis mesure l'**écart brut** et l'**écart ajusté** entre femmes et hommes, introduit le **compa-ratio**, et termine par les **précautions** qui s'imposent quand on manipule des données de rémunération.

### 12.2.1 Les salaires par poste, et la règle des petits groupes

La rémunération est la variable la plus sensible du fichier. Commençons par la plus simple des descriptions : le salaire brut mensuel par poste pour la dernière année, 2025. Quand un groupe est très petit, le résumé **identifie** la personne : si un seul collaborateur occupe un poste, sa médiane est son salaire. C'est la raison pour laquelle on **n'affiche pas** les groupes de moins de cinq personnes.

```python
d25 = ea[ea["annee"] == 2025]
t = d25.groupby("poste")["salaire_brut_mensuel"].agg(["count", "median", "min", "max"]).round(0)
t.loc[t["count"] < 5, ["median", "min", "max"]] = np.nan          # petits groupes : non publiés
print(t)
```
<!--sortie-->
```text
                count  median     min     max
poste                                        
Caissier            7  2096.0  2021.0  2261.0
Logistique         13  2295.0  2072.0  2571.0
Responsable         3     NaN     NaN     NaN
Service client      6  2313.0  2260.0  2609.0
Vendeur            19  2256.0  2013.0  2540.0
```


En 2025, 48 collaborateurs sont présents. Le salaire médian d'un vendeur est de 2 256 € brut par mois. Parmi les 5 postes présents, **1 compte moins de cinq personnes** (« Responsable » : 3 personnes) : ses salaires sont masqués (`NaN`). Ce n'est pas de la pudeur, c'est la protection des personnes concernées, et c'est l'application directe des principes de la section 5.4.2 du volume II.

### 12.2.2 Ce qui explique un salaire : le poste et l'ancienneté

Deux facteurs expliquent l'essentiel des écarts de salaire dans une petite entreprise : le **poste** (un responsable est mieux payé qu'un caissier) et l'**ancienneté** (les augmentations s'accumulent). Une régression du **logarithme** du salaire sur ces deux variables (chapitre 3) donne des coefficients lisibles en **pourcentages** : un coefficient de 0,01 signifie environ +1 %.

```python
m0 = smf.ols("np.log(salaire_brut_mensuel) ~ C(poste) + anciennete + C(annee)", data=ea).fit()
print(round(m0.params["anciennete"] * 100, 2), "% de salaire par année d'ancienneté | R² :", round(m0.rsquared, 2))
```
<!--sortie-->
```text
1.13 % de salaire par année d'ancienneté | R² : 0.93
```


Chaque année d'ancienneté ajoute environ **1,13 %** au salaire, à poste et année égaux ; le poste, l'ancienneté et l'année expliquent 0,93 de la variance du log-salaire (un coefficient de détermination de 0,93 : le reste est du « bruit » individuel). Le coefficient de l'année 2025 par rapport à 2021 correspond à une hausse générale d'environ 9,2 % sur quatre ans.

### 12.2.3 L'écart brut entre femmes et hommes

L'**écart brut** est la différence de salaire moyen entre deux groupes, sans tenir compte de rien d'autre. C'est le chiffre que l'on trouve dans la presse, et celui que la gérante calculerait en premier.

```python
brut = d25.groupby("genre")["salaire_brut_mensuel"].agg(["count", "mean"]).round(0)
ecart_brut = brut.loc["F", "mean"] / brut.loc["H", "mean"] - 1
print(brut, "| écart brut des femmes par rapport aux hommes :", round(ecart_brut * 100, 1), "%")
```
<!--sortie-->
```text
       count    mean
genre               
F         25  2300.0
H         23  2368.0 | écart brut des femmes par rapport aux hommes : -2.9 %
```


En 2025, les 25 femmes gagnent en moyenne 2 300 € brut par mois, les 23 hommes 2 368 € : un **écart brut de 2,9 %** en défaveur des femmes (sur l'ensemble des cinq ans : 3,9 %). Mais la comparaison est-elle équitable ? Une partie de l'écart pourrait venir d'une **autre répartition entre postes** : si les femmes occupaient davantage de postes moins payés, l'écart brut mesurerait cela, pas une différence « à poste égal ».

Le tableau des effectifs par poste et par genre montre d'ailleurs la difficulté : sur 12 cases (poste × genre), **5 comptent moins de cinq personnes**. Une comparaison poste par poste est donc impossible ; il faut un modèle qui **ajuste** globalement.

### 12.2.4 L'écart ajusté : « toutes choses égales par ailleurs »

L'**écart ajusté** compare des personnes **comparables** : même poste, même ancienneté, même année. On l'estime par la régression du log-salaire avec une variable de genre en plus des variables précédentes. Les lignes d'un même collaborateur étant corrélées d'une année à l'autre, on calcule les erreurs types **en groupant par collaborateur** (erreurs robustes par grappes) : sans cela, l'intervalle serait trop étroit.

```python
m1 = smf.ols("np.log(salaire_brut_mensuel) ~ C(genre, Treatment('H')) + C(poste) + anciennete + C(annee)", data=ea).fit(
    cov_type="cluster", cov_kwds={"groups": ea["id_employe"]})
b = m1.params["C(genre, Treatment('H'))[T.F]"]
bas, haut = m1.conf_int().loc["C(genre, Treatment('H'))[T.F]"]
print(round((np.exp(b) - 1) * 100, 1), "% [", round((np.exp(bas) - 1) * 100, 1), ";", round((np.exp(haut) - 1) * 100, 1), "]")
```
<!--sortie-->
```text
-3.8 % [ -4.5 ; -3.0 ]
```


À poste, ancienneté et année égaux, les femmes gagnent en moyenne **3,8 %** de moins que les hommes, avec un intervalle à 95 % de 3,0 à 4,5 %. L'écart ajusté est **du même ordre que l'écart brut** de l'ensemble de la période (3,9 %) : la répartition entre postes n'explique donc pas la différence. En euros, il représente environ 89 € brut par mois pour un salaire masculin moyen.

> ⚠️ **Ce que ce chiffre dit, et ne dit pas.** Il dit qu'**une différence de salaire demeure** entre femmes et hommes une fois pris en compte le poste, l'ancienneté et l'année. Il ne dit pas **pourquoi** : ni qu'elle résulte d'une discrimination (cela exige un autre type d'enquête), ni qu'elle n'en résulte pas. D'autres facteurs peuvent la produire sans figurer dans nos données : le temps partiel, l'évaluation, la négociation à l'embauche, les responsabilités réelles d'un même intitulé de poste, le parcours antérieur. Le terme « inexpliqué » désigne ce que **nos variables** n'expliquent pas, pas ce que **le monde** n'explique pas.

> 💡 **Intuition.** L'écart brut répond à « combien l'ensemble des femmes gagne-t-il de moins que l'ensemble des hommes ? » ; l'écart ajusté à « combien une femme gagne-t-elle de moins qu'un homme **comparable** ? ». Les deux questions sont légitimes, mais ce ne sont pas les mêmes, et l'on ne doit pas les confondre dans une communication.

### 12.2.5 Le compa-ratio

Un indicateur très employé en rémunération est le **compa-ratio** : le salaire d'une personne divisé par le salaire **médian de son poste** (la même année). Il vaut 1 pour un salaire médian, 0,9 pour un salaire inférieur de 10 %. Il permet de comparer des postes différents sur une même échelle et de repérer les salaires nettement en dessous du marché interne.


Le compa-ratio va de 0,94 (10 % des salaires sont en dessous) à 1,07 (10 % au-dessus) ; 14 % des collaborateur-années ont un compa-ratio **inférieur à 0,95**. La moyenne est de 0,985 chez les femmes et de 1,024 chez les hommes ; la part des salaires sous 0,95 de la médiane est de 22 % pour les femmes contre 5 % pour les hommes.

![Distribution du compa-ratio selon le genre : les distributions se chevauchent largement, avec un léger décalage vers la gauche pour les femmes.](figures/ch12-compa-ratio.png)

> 🧪 **Remarque.** Le compa-ratio d'une personne dépend du groupe de référence (son poste et l'année) : pour un poste de deux personnes, le compa-ratio ne signifie rien. Comme toujours en RH, un indicateur n'est lisible que si le groupe est **assez grand**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 12 : application 12.4, exercices 12.5 et 12.6.

### 12.2.6 Les précautions à prendre

Un écart de salaire est un chiffre qui peut changer la vie de quelqu'un, dans un sens comme dans l'autre. Six précautions s'imposent à l'analyste.

**Préciser la définition.** Brut ou net ? Avec ou sans primes ? Équivalent temps plein ou réel ? Toute comparaison suppose des salaires définis de la même façon (volume II, section 4.2).

**Donner l'incertitude.** L'écart de 3,8 % se connaît de 3,0 à 4,5 % : on communique la fourchette, et la taille de l'échantillon (ici 64 personnes sur cinq ans).

**Nommer ce qui manque.** Dire explicitement que le temps partiel, l'évaluation individuelle, la négociation à l'embauche et le contenu réel des postes ne sont pas contrôlés.

**Protéger les petits groupes.** Ne jamais publier un salaire, un écart ou un taux pour un groupe de moins de cinq personnes (section 12.2.1 ; volume II, section 5.4.2). Les résultats par service ou par équipe d'une petite entreprise identifient souvent les personnes.

**Limiter l'accès.** Les données individuelles de rémunération ne se partagent que dans le cadre prévu (direction, personne chargée de la paie) ; l'analyste travaille, quand c'est possible, sur des données **pseudonymisées** (volume II, section 5.2).

**Ne pas conclure à la place des personnes compétentes.** Un écart ajusté est un point de départ pour une **enquête** (examen des politiques d'embauche, de promotion, de négociation), pas un verdict. La conclusion juridique ou disciplinaire n'appartient pas à l'analyste.

> ✅ **À retenir.**
> - Le **poste** et l'**ancienneté** expliquent l'essentiel des salaires ; on lit les coefficients d'une régression du **log-salaire** en pourcentages.
> - L'**écart brut** compare des groupes ; l'**écart ajusté** compare des personnes comparables, avec des erreurs types **groupées par personne**.
> - Un écart ajusté **signale** une question, il ne prouve ni ne réfute une discrimination.
> - Le **compa-ratio** (salaire / médiane du poste) compare des postes différents, à condition que les groupes soient assez grands.
> - **Protéger** : définitions écrites, intervalle communiqué, petits groupes masqués, accès limité.


## 12.3 Prédire les départs, et ce que l'on a le droit d'en faire

Cette section pose la question qui revient dans toutes les directions : *peut-on prédire qui va partir ?* Elle construit un modèle logistique sur nos données, mesure honnêtement sa performance, explique pourquoi un modèle fait sur vingt départs ne peut presque rien dire, **simule** ce qui aurait été détecté avec davantage de données, puis aborde ce qu'il faut se demander avant d'utiliser un tel modèle sur des personnes.

### 12.3.1 Poser le problème

L'unité d'analyse est la **ligne collaborateur-année** (245 lignes) et la cible est l'indicateur « part dans l'année » (20 départs). Les variables explicatives sont celles dont on peut raisonnablement penser qu'elles jouent : les **heures supplémentaires** par mois, le **compa-ratio** (le salaire relatif à la médiane du poste, section 12.2.5), une **promotion** au cours des trois dernières années, l'**évaluation** de l'année et l'**ancienneté**.

Avant d'ajuster quoi que ce soit, un calcul de bon sens : on a **20 événements** pour **5 variables**, soit **4 événements par variable**. Une règle de pouce de la statistique médicale réclame au moins dix événements par variable pour qu'une régression logistique soit stable. Nous sommes très en dessous : les coefficients seront imprécis, et un modèle trop complexe apprendra du bruit.


### 12.3.2 Un modèle logistique

La régression logistique (section 3.3) modélise le **logarithme du rapport de chances** de départ comme une combinaison linéaire des variables. On lit les coefficients sous forme d'**odds ratios** : un odds ratio de 1,10 signifie que la variable multiplie les chances de départ par 1,10 quand elle augmente d'une unité.

```python
ea["compa_10"] = (ea["compa_ratio"] - 1) * 10          # une unité = 10 points de compa-ratio
X = ea[["heures_sup_mensuelles", "compa_10", "promo_3ans", "evaluation", "anciennete"]]
y = ea["depart_dans_l_annee"]
res = sm.Logit(y, sm.add_constant(X)).fit(disp=0)
tab = pd.DataFrame({"odds ratio": np.exp(res.params), "bas": np.exp(res.conf_int()[0]), "haut": np.exp(res.conf_int()[1]), "p": res.pvalues}).drop("const")
print(tab.round(3))
```
<!--sortie-->
```text
                       odds ratio    bas   haut      p
heures_sup_mensuelles       0.963  0.822  1.129  0.644
compa_10                    0.338  0.096  1.187  0.090
promo_3ans                  1.257  0.260  6.069  0.776
evaluation                  0.765  0.397  1.474  0.423
anciennete                  0.964  0.782  1.188  0.731
```


**Aucune des cinq variables n'est significative** (0 sur 5 ; la plus petite p-valeur est de 0,09). L'odds ratio des heures supplémentaires par heure mensuelle est de 0,96 avec un intervalle de 0,82 à 1,13 : il contient 1 (pas d'effet), mais aussi des valeurs qui seraient importantes. Pour le salaire relatif (par tranche de 10 points de compa-ratio), l'odds ratio de 0,34 va de 0,10 à 1,19 : le sens est plausible (un salaire plus bas va avec plus de départs), mais l'intervalle contient 1. Pour la promotion récente, l'odds ratio de 1,26 s'accompagne d'un intervalle de 0,26 à 6,07, **extrêmement large** parce que seules quelques personnes ont été promues et sont parties. Un intervalle aussi large dit : « **nous ne savons pas** ».

### 12.3.3 Une performance mesurée honnêtement

Un modèle de prédiction se juge par sa performance **sur des personnes qu'il n'a pas vues**. Comme les données sont rares, on utilise la **validation croisée répétée** (on découpe cinq fois les données en cinq morceaux, vingt fois de suite, en gardant la proportion de départs ; pour aller plus loin, voir la série 1, volume III, section 1.2). L'indicateur est l'**AUC** (série 1, volume III, section 5.1) : la probabilité que le modèle attribue un risque plus élevé à une personne qui part qu'à une personne qui reste (0,5 = hasard, 1 = parfait).

```python
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
modele = make_pipeline(StandardScaler(), LogisticRegression(C=0.5, max_iter=1000))
auc = cross_val_score(modele, X, y, cv=RepeatedStratifiedKFold(n_splits=5, n_repeats=20, random_state=0), scoring="roc_auc")
print(round(auc.mean(), 2), round(auc.std(), 2), np.percentile(auc, [2.5, 97.5]).round(2))
```
<!--sortie-->
```text
0.53 0.11 [0.3  0.73]
```


L'AUC moyenne en validation croisée est de **0,53**, très proche du hasard (0,5), avec une dispersion de 0,11 d'un découpage à l'autre : l'intervalle va de 0,30 à 0,73. Pour savoir si ce score est distinguable du hasard, on le compare à celui qu'on obtiendrait avec des départs **mélangés au hasard** (test de permutation) : la moyenne sous le hasard est de 0,49 et la part des tirages au hasard qui font aussi bien que notre modèle est de 33 % : **ce modèle ne prédit pas mieux que le hasard**.

> 🧭 **En pratique.** Ce résultat n'est pas un échec de l'analyste : c'est une **information utile pour la direction**. Elle apprend que, avec ces données, un « score de risque de départ » individuel serait un **tirage au sort habillé de statistiques**. Ne pas le construire est une décision d'analyste.

### 12.3.4 Ce que la vérité programmée dit : la puissance qui manque

Les départs ont été fabriqués selon une règle connue : le **risque augmente** avec les heures supplémentaires (coefficient de 0,07 par heure mensuelle, soit un odds ratio de 1,07), **baisse** après une promotion récente (coefficient de −0,8), baisse avec une meilleure évaluation et avec l'ancienneté, et dépend légèrement du salaire relatif. Ces effets **existent**, et notre analyse ne les voit pas. Pourquoi ? Parce qu'avec 20 événements, la **puissance** statistique est trop faible. On peut le mesurer : on simule cent autres entreprises de même taille, avec la même règle, et l'on regarde combien de fois l'analyse détecterait l'effet des heures supplémentaires.

```python
import donnees_a3 as G
detecte, coefs = 0, []
for graine in range(100):
    _, panel, _ = G.rh(seed=9000 + graine)
    panel = panel.sort_values(["id_employe", "annee"])
    panel["compa_ratio"] = panel["salaire_brut_mensuel"] / panel.groupby(["poste", "annee"])["salaire_brut_mensuel"].transform("median")
    panel["promo_3ans"] = panel.groupby("id_employe")["promotion"].transform(lambda s: s.rolling(3, min_periods=1).max())
    panel["compa_10"] = (panel["compa_ratio"] - 1) * 10
    r = sm.Logit(panel["depart_dans_l_annee"], sm.add_constant(panel[X.columns])).fit(disp=0)
    coefs.append(r.params["heures_sup_mensuelles"]); detecte += int(r.pvalues["heures_sup_mensuelles"] < 0.05 and r.params["heures_sup_mensuelles"] > 0)
print(detecte, "détections sur 100 | coefficient moyen :", round(np.mean(coefs), 3))
```
<!--sortie-->
```text
18 détections sur 100 | coefficient moyen : 0.068
```


![Distribution du coefficient estimé des heures supplémentaires dans cent entreprises simulées de même taille : la moyenne est proche de la vérité (0,07), mais l'étalement est tel que la plupart des tirages ne détectent pas l'effet.](figures/ch12-puissance.png)

L'analyse détecte l'effet des heures supplémentaires dans seulement **18 tirages sur 100**. Le coefficient estimé vaut en moyenne **0,068**, très près de la vérité (0,07) : l'estimateur n'est pas **biaisé**, mais il est **tellement dispersé** (écart-type de 0,094 d'un tirage à l'autre, soit davantage que l'effet lui-même) qu'un échantillon seul le noie. La **puissance** est faible : c'est le même phénomène que celui du test A/B de la section 2.5, appliqué à la régression.

Il suffit de regarder ce qui se passe avec beaucoup plus de données. En empilant 40 entreprises simulées (9 839 collaborateur-années, 707 départs), l'effet des heures supplémentaires est estimé à **0,066** (p-valeur inférieure à 0,001), la promotion récente à −0,69, l'évaluation à −0,37 et l'ancienneté à −0,055 : les effets programmés réapparaissent, avec les bons signes. La **vérité** est donc dans la règle ; ce qui manquait n'était pas la bonne méthode, mais **des données**.

> ⚠️ **Piège.** Une régression qui ne trouve « rien » n'a pas démontré que **rien** n'existe. Quand les effectifs sont faibles, « non significatif » veut dire « indécidable », pas « nul ». La seule manière honnête de le dire à la gérante est : *avec cinquante personnes, nous ne pouvons pas identifier ce qui fait partir ; nous pouvons seulement l'exclure pour les très gros effets.*

> 📒 **Pour s'entraîner.** Cahier, chapitre 12 : application 12.5, exercices 12.7 et 12.8.

### 12.3.5 Les limites éthiques d'un score de départ

Admettons que l'on ait **beaucoup** plus de données et un modèle qui marche. Faut-il pour autant s'en servir sur des personnes ? Cinq questions doivent précéder toute utilisation.

**À quoi servira-t-il, exactement ?** Un score de risque de départ peut orienter des actions positives (proposer un entretien, revoir une charge de travail, une rémunération) ou négatives (écarter une personne d'une promotion « parce qu'elle va partir », la surveiller davantage). La même statistique sert deux politiques opposées ; **c'est l'usage qui est bon ou mauvais, pas le calcul**.

**Que sait la personne ?** Les cadres de protection des données prévoient en général que les personnes soient **informées** des traitements qui les concernent, de leur finalité et de leurs droits (volume II, section 5.1). Un score calculé en secret est difficile à justifier.

**Le modèle est-il équitable ?** Même sans utiliser le genre ou l'âge, un modèle peut les **reconstituer** par des variables proches (poste, heures supplémentaires, temps partiel) et produire des scores systématiquement plus élevés pour un groupe. Il faut **auditer** le score par groupe, comme nous le faisons ci-dessous. Ce contrôle est nécessaire, pas suffisant.

**Que fait-on d'une erreur ?** À performance modeste, la plupart des personnes à « risque élevé » ne partiront pas, et certaines personnes à « risque faible » partiront. Traiter les premières comme des « futurs partants » est une injustice individuelle, que seule la transparence et une action **non pénalisante** peuvent éviter.

**Existe-t-il une alternative moins intrusive ?** Presque toujours : une **enquête d'engagement** anonyme, des **entretiens de départ** et de mi-carrière, des **statistiques d'équipe** (jamais d'individus) : elles répondent à la question de la gérante (« pourquoi partent-ils ? ») sans scorer personne.


Pour fixer les idées, voici un **audit** rapide du modèle ajusté. Le risque moyen prédit est de 8,2 % ; il est de 9,2 % pour les femmes et de 6,9 % pour les hommes, et va de 7,5 % à 8,4 % selon le poste. Parmi les 10 % de personnes au score le plus élevé (24 collaborateur-années), le taux de départ réel est de **16,7 %**, pour 8,2 % dans l'ensemble : soit **deux fois** le taux d'ensemble, mais sur 4 départs seulement : un résultat trop fragile pour guider une décision. Un point mérite l'attention : le modèle n'utilise pas le genre, et pourtant le risque prédit est plus élevé pour les femmes. La raison probable est leur **compa-ratio plus bas** (section 12.2.5) : sans cette variable, le risque prédit tombe à 8,1 % pour les femmes et 8,2 % pour les hommes. Un score fondé sur le salaire relatif **reproduit** donc l'écart de salaire. Retenons surtout le principe : **auditer par groupe, regarder l'écart réel entre score et résultat, et ne pas s'arrêter à l'AUC**.

> ✅ **À retenir.**
> - Avec **20 événements**, un modèle logistique ne peut identifier que des effets énormes ; on regarde l'**intervalle** des coefficients et l'**AUC en validation croisée**.
> - « Non significatif » veut dire « indécidable » quand la **puissance** est faible ; une simulation chiffre cette puissance.
> - Un **score individuel de départ** pose des questions d'**usage**, d'**information** des personnes, d'**équité** et d'**erreur** avant toute question technique.
> - Les **alternatives** (enquête d'engagement, entretiens, statistiques d'équipe) répondent mieux à la vraie question, sans scorer personne.
> - La **vérité programmée** (effets réels mais faibles) montre ce qu'un échantillon trop petit rate.


## Bilan du chapitre 12

Vous savez maintenant :

- **compter** une rotation, la rapporter à l'effectif, y joindre un **intervalle de Poisson exact**, et résister à la tentation de commenter des variations qui relèvent du bruit ;
- **distinguer** les démissions des autres départs, **calculer** un taux d'absentéisme, et **estimer** la durée de présence par une **courbe de survie** qui tient compte des personnes encore présentes ;
- **mesurer** un écart de salaire brut puis ajusté (régression du log-salaire, erreurs groupées par personne), **lire** un compa-ratio, et **dire** ce qu'un écart ajusté signifie et ne signifie pas ;
- **protéger** les personnes : définitions écrites, intervalles communiqués, groupes de moins de cinq personnes masqués ;
- **ajuster** un modèle de départ, **mesurer** sa performance par validation croisée, **chiffrer** la puissance qui manque par simulation, et **poser** les questions éthiques avant d'utiliser un score sur des personnes.

Le tableau suivant résume ce que nous avons **mesuré** sur les données de la boutique.

| Question | Mesure |
|---|---|
| Rotation annuelle | 8,2 % (5,0 à 12,6 %) ; de 4,0 % en 2023 à 10,6 % en 2021, tous intervalles recouverts |
| Démissions | 14 départs sur 20 (70 %) |
| Absentéisme | 8,2 jours par an (taux de 3,7 %) ; environ 0,47 jour de plus par heure supplémentaire mensuelle |
| Durée de présence | 90 % restent un an, 53 % cinq ans |
| Écart de salaire femmes/hommes | brut 2,9 % (2025) ; ajusté 3,8 % (3,0 à 4,5 %), toujours en défaveur des femmes |
| Modèle de départ | AUC de 0,53 en validation croisée (0,30 à 0,73) : indistinguable du hasard |
| Puissance | l'effet des heures supplémentaires est détecté dans 18 tirages sur 100 |

Le fil conducteur du chapitre tient en une phrase : **en RH, les effectifs sont petits, les enjeux grands, et la prudence est une compétence d'analyste**. Un intervalle large n'est pas une faiblesse de l'analyse, c'est son message ; un écart ajusté n'est pas un verdict ; un score individuel n'est pas une décision.

> 🧭 **En pratique : avant de publier un chiffre RH.**
> 1. Quel est le **nombre d'événements** derrière ce taux, et quel est son **intervalle** ?
> 2. Le **groupe** compte-t-il au moins cinq personnes ?
> 3. La **définition** (effectif, départ, salaire) est-elle écrite et identique d'une année à l'autre ?
> 4. Dit-on ce que l'on **n'a pas contrôlé** ?
> 5. La personne qui lit peut-elle **reconnaître quelqu'un** dans le tableau ?
> 6. Qui **décide**, et sur quelle base, à la place de l'analyste ?

Le chapitre 13 clôt le volume par un autre type de question, tournée vers l'avenir : *que se passerait-il si… ?* Analyse de sensibilité, simulations et scénarios.

> 📒 **Pour s'entraîner.** Cahier, chapitre 12 : applications 12.1 à 12.5 (rotation et intervalles, absentéisme, survie, écart ajusté, puissance d'un modèle de départ) et exercices 12.1 à 12.9.
