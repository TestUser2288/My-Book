## 3.2 Modèles prédictifs simples

Cette section construit **deux modèles complets** sur les données de la boutique, avec la même discipline : poser la question avec précision, séparer **dans le temps** ce qui sert à construire et ce qui sert à juger, comparer à une référence naïve, et chiffrer l'incertitude. Le **cas A** (cette partie) répond à « combien de commandes en janvier ? » ; le **cas B** (sections 3.2.6 à 3.2.13) répond à « quels clients rachèteront dans les 90 jours ? ».

```python hide
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch03 as O
import fig_ch03 as F
import statsmodels.api as sm
import statsmodels.formula.api as smf
```

### 3.2.1 Cas A : combien de commandes en janvier ?

La série à prévoir est la **série mensuelle des commandes** de la boutique : trente-six valeurs, de janvier 2023 à décembre 2025. Les trois janviers sont les suivants.

```python
m = d["M"]
print({str(k): int(v) for k, v in m[m.index.month == 1].items()})
print("croissance :", round((m["2024-01"] / m["2023-01"] - 1) * 100, 1), "%, puis", round((m["2025-01"] / m["2024-01"] - 1) * 100, 1), "%")
```
<!--sortie-->
```text
{'2023-01': 785, '2024-01': 882, '2025-01': 963}
croissance : 12.4 %, puis 9.2 %
```

```python hide
assert [int(v) for v in m[m.index.month == 1].values] == [785, 882, 963]
```

Janvier est un mois creux (la figure de la section 3.2.5 montre le pic de décembre, puis la chute), qui progresse d'une année à l'autre. Le modèle à construire doit donc connaître **au moins trois choses** : la saison, la tendance, et les soldes d'hiver (qui occupent une bonne partie de janvier, du 8 au 28, chaque année).

Il reste à décider **comment on jugera** le modèle. On ne peut pas, comme dans une analyse ordinaire, l'ajuster sur les trente-six mois puis mesurer son erreur sur ces trente-six mois : il aurait « vu » les réponses. On procède par **origine glissante**. À la fin de chaque mois d'une période de test (ici, décembre 2024 à novembre 2025), on se place **comme si** l'on était ce jour-là : on n'utilise que les données déjà connues, on prévoit le mois suivant (et, séparément, le troisième mois suivant), puis on compare à ce qui s'est réellement passé. On obtient douze prévisions à un mois et dix à trois mois, chacune faite **sans connaître la réponse**.

> 💡 **Intuition.** L'origine glissante rejoue le passé comme un film : à chaque image, le modèle ne voit que ce qui précède. C'est la seule façon honnête de juger une prévision, car c'est exactement la situation dans laquelle il sera utilisé.

### 3.2.2 Quatre références, de la plus bête à la plus fine

On ne démarre jamais par le modèle compliqué. On aligne d'abord des méthodes simples, chacune plus fine que la précédente, et l'on voit ce que chaque raffinement apporte.

1. **Naïf** : le mois prochain sera comme ce mois-ci. (Aucune saison.)
2. **Saisonnier** : le mois prochain sera comme le même mois de l'an dernier. (La saison, pas la croissance.)
3. **Saisonnier × croissance** : le même mois de l'an dernier, multiplié par la croissance des douze derniers mois sur les douze d'avant. (La saison et la tendance.)
4. **Holt-Winters** (lissage exponentiel) : trois quantités mises à jour mois après mois, un **niveau**, une **tendance** et un **indice saisonnier**, chacune lissée en donnant plus de poids aux observations récentes. C'est la méthode « tout en un » de la prévision de séries ; elle s'obtient en une ligne de statsmodels.

Faisons la troisième à la main pour **janvier 2025**, au 31 décembre 2024 : la croissance de 2024 sur 2023, puis le janvier de 2024 multiplié par cette croissance.

```python
total23, total24 = m["2023"].sum(), m["2024"].sum()
g = total24 / total23
print("croissance 2024 sur 2023 :", round((g - 1) * 100, 1), "%")
print("janvier 2025 prévu :", round(m["2024-01"] * g), "| réel :", int(m["2025-01"]))
```
<!--sortie-->
```text
croissance 2024 sur 2023 : 5.4 %
janvier 2025 prévu : 929 | réel : 963
```

```python hide
assert round((g - 1) * 100, 1) == 5.4 and round(m["2024-01"] * g) == 929
```

La prévision « saisonnier × croissance » est de 929 commandes, la réalité de 963 : un écart de 34, soit 3,5 %. La saison fait déjà presque tout le travail ; la croissance l'a rapprochée de la vérité (le simple « même mois de l'an dernier » donnait 882, soit 81 de trop peu).

### 3.2.3 Un modèle de comptage qui connaît le calendrier

Les quatre méthodes précédentes ne connaissent qu'un **chiffre par mois**. Or nous savons bien plus : combien de samedis (jour fort) et de dimanches (jour faible) compte le mois, combien de jours de soldes il contient, et ce que ces jours valent. Un **modèle de comptage** au niveau du **jour** exploite tout cela, puis on additionne les jours du mois.

Le nombre de commandes d'un jour est un **comptage** : un entier, positif, dont les effets sont **multiplicatifs** (les soldes ajoutent un pourcentage, pas un nombre fixe ; volume III, section 3.1.5). La régression de **Poisson** avec lien logarithmique est faite pour cela :

$$\log E[\text{commandes du jour}] = \text{effet du mois} + \text{effet du jour de la semaine} + b \times \text{promotion} + c \times \text{tendance}.$$

Le coefficient $b$ se lit comme un pourcentage (section 3.1.2) ; la prévision d'un mois est la **somme** des espérances des jours qui le composent. Ne figurent que des variables **connues à l'avance** : le mois, le jour de la semaine, le calendrier des soldes (décidé chaque année pour les mêmes dates) et la tendance. Ni la pluie ni la publicité n'y figurent : la première n'est pas connue à l'avance, la seconde dépend d'un budget qui n'est pas fixé pour janvier.

Voici la prévision de janvier 2025 faite le 31 décembre 2024 : on ajuste sur les jours **antérieurs**, on prédit les 31 jours à venir et l'on additionne.

```python
j = d["j"]
passe, futur = j[j["per"] < pd.Period("2025-01")], j[j["per"] == pd.Period("2025-01")]       # connu au 31/12/2024, puis à prévoir
mod = smf.glm("nb_commandes ~ C(mois) + C(dow) + promo_active + t", passe, family=sm.families.Poisson()).fit()
print("janvier 2025 prévu :", round(mod.predict(futur).sum()), "| réel :", int(m["2025-01"]))
```
<!--sortie-->
```text
janvier 2025 prévu : 911 | réel : 963
```

```python hide
assert round(mod.predict(futur).sum()) == 911
```

911 prévus, 963 réels : 52 de trop peu, soit 5,4 %. **Cette fois, la méthode plus fine se trompe plus que la précédente** (929). Un mois ne prouve rien : c'est précisément pourquoi on juge sur douze origines, pas sur une.

> ⚠️ **Piège.** Choisir un modèle parce qu'il a bien prévu **un** mois, c'est choisir au hasard. Même un très bon modèle se trompe de 5 % certains mois ; même un mauvais en a un où il tombe juste. Le jugement se fait sur l'ensemble des origines, avec une mesure d'erreur moyenne.

### 3.2.4 Juger par origine glissante

Trois mesures résument les erreurs d'une série de prévisions $\hat y_i$ contre les réalités $y_i$ :

> 📐 **Les trois mesures.**
> - **MAE** (erreur absolue moyenne) : $\frac1n\sum|\hat y_i-y_i|$, dans l'unité de la série (ici des commandes).
> - **MAPE** (erreur absolue moyenne en pourcentage) : $\frac1n\sum\frac{|\hat y_i-y_i|}{y_i}\times100$ : comparable entre séries de tailles différentes, mais instable si la série s'approche de zéro.
> - **Biais** : $\frac1n\sum(\hat y_i-y_i)$ : l'erreur **moyenne avec son signe**. Un biais négatif signifie que l'on sous-estime systématiquement.
>
> Deux modèles de même MAE peuvent avoir des biais opposés, et le biais est le plus facile à corriger : il faut donc toujours le regarder.

Calculons-les pour les cinq méthodes, d'abord à un mois d'horizon, puis à trois mois. La fonction `origines` rejoue les douze (puis dix) origines ; le code est caché car il ne fait que répéter, pour chaque origine, ce que nous venons de faire à la main une fois.

```python hide
R = O.origines(d)
t1, t3 = O.metriques(R[R["h"] == 1]), O.metriques(R[R["h"] == 3])
assert len(R[R["h"] == 1]) == 12 and len(R[R["h"] == 3]) == 10
assert [round(v, 1) for v in t1["MAE"]] == [210.7, 80.8, 46.9, 40.3, 34.7]
assert [round(v, 1) for v in t3["MAPE (%)"]] == [27.3, 7.5, 5.3, 5.3, 3.4]
```

```python
print("Horizon d'un mois (12 prévisions)")
print(O.metriques(R[R["h"] == 1]).drop(columns="n").round(1))
```
<!--sortie-->
```text
Horizon d'un mois (12 prévisions)
                                      MAE  MAPE (%)  biais
naïf (mois précédent)               210.7      19.9  -13.5
saisonnier (même mois, an dernier)   80.8       7.3  -76.2
saisonnier × croissance              46.9       4.5  -25.5
Holt-Winters                         40.3       4.1  -32.0
régression de Poisson                34.7       3.4  -14.0
```

```python
print("Horizon de trois mois (10 prévisions)")
print(O.metriques(R[R["h"] == 3]).drop(columns="n").round(1))
```
<!--sortie-->
```text
Horizon de trois mois (10 prévisions)
                                      MAE  MAPE (%)  biais
naïf (mois précédent)               320.1      27.3 -111.7
saisonnier (même mois, an dernier)   86.0       7.5  -80.6
saisonnier × croissance              57.7       5.3  -32.7
Holt-Winters                         58.2       5.3  -50.9
régression de Poisson                35.3       3.4  -12.7
```

![Les douze prévisions à un mois de l'année 2025. La prévision naïve recopie le mois précédent et rate chaque tournant ; la régression qui connaît le calendrier suit la courbe réelle de près.](figures/ch03-references.png)

```python hide
F.fig_references(R, d["M"])
```
<!--sortie-->
```text
figure : ch03-references.png
```

Plusieurs choses se lisent dans ces tableaux.

- **Chaque raffinement apporte quelque chose, de moins en moins.** Passer du naïf (MAE 211) au saisonnier (81) divise l'erreur par plus de deux ; ajouter la croissance (47) la réduit encore d'environ 40 % ; la régression de Poisson (35) gagne encore un quart. La régression a une erreur moyenne de 3,4 %, contre 19,9 % pour le naïf et 7,3 % pour le saisonnier.
- **L'horizon pénalise les méthodes qui prolongent la dernière valeur et épargne celles qui connaissent le calendrier.** À trois mois, le naïf passe à 27 % d'erreur et Holt-Winters de 4,1 % à 5,3 % ; la régression reste à 3,4 %, car son information (le calendrier) ne vieillit pas.
- **Le biais est négatif partout** (de −14 à −76 commandes par mois) : toutes les méthodes sous-estiment, parce que la boutique **croît** et qu'une méthode qui regarde en arrière le fait un peu trop peu. Celui de la régression est faible (−14 commandes par mois, un peu plus de 1 %).

Mais prudence : douze origines, c'est peu. Comptons les mois où la régression l'emporte sur Holt-Winters :

```python
a = (R[R["h"] == 1]["régression de Poisson"] - R[R["h"] == 1]["reel"]).abs()
b = (R[R["h"] == 1]["Holt-Winters"] - R[R["h"] == 1]["reel"]).abs()
print("la régression bat Holt-Winters", int((a < b).sum()), "mois sur", len(a))
```
<!--sortie-->
```text
la régression bat Holt-Winters 7 mois sur 12
```

```python hide
assert int((a < b).sum()) == 7
```

Sept mois sur douze : à peine mieux qu'à pile ou face, et loin de **démontrer** que les deux méthodes diffèrent (sept sur douze, ou mieux, arrive plus d'une fois sur trois si elles étaient équivalentes). Pour trancher entre deux modèles voisins, il faudrait plus d'origines, ou une autre raison : la simplicité, l'explicabilité, la possibilité de poser un scénario (« sans soldes »). Ici, la régression en a une, décisive : elle sait ce qu'est une promotion, ce que Holt-Winters ignore.

> 🧪 **Ce que disait la vérité programmée.** La fabrique des données a bien pour recette : saison mensuelle × jour de la semaine × tendance de 6 % par an × promotion de +18 % × météo. La régression de Poisson a donc **la bonne forme**, et c'est un avantage que l'on n'a pas toujours dans la vie réelle : sur des données réelles, l'écart avec une référence saisonnière est souvent plus petit. Le bon réflexe ne change pas : **comparer à la référence et ne garder que ce qui gagne**.

### 3.2.5 Une prévision, une fourchette, deux scénarios

On peut maintenant répondre à la gérante. Le modèle est ajusté sur les trente-six mois, le calendrier de janvier 2026 est connu (les soldes sont prévus du 8 au 28 janvier, comme les trois années précédentes), et l'on additionne les trente et un jours. On calcule aussi le **scénario sans soldes**, puisque la décision de les maintenir appartient à la gérante.

```python
f_avec, mod_final = O.prevision_mois(d, "2026-01")
f_sans, _ = O.prevision_mois(d, "2026-01", scenario_promo=False)
err = R["reel"] / R["régression de Poisson"] - 1                     # erreurs relatives passées (22 prévisions)
bas, haut = f_avec * (1 + err.quantile(0.10)), f_avec * (1 + err.quantile(0.90))
print(f"avec soldes : {f_avec:.0f} (fourchette {bas:.0f} à {haut:.0f}) | sans soldes : {f_sans:.0f}")
```
<!--sortie-->
```text
avec soldes : 1014 (fourchette 979 à 1059) | sans soldes : 901
```

```python hide
assert (round(f_avec), round(bas), round(haut), round(f_sans)) == (1014, 979, 1059, 901)
F.fig_janvier(d, f_avec, f_sans, bas, haut)
```
<!--sortie-->
```text
figure : ch03-janvier-2026.png
```

La **fourchette** vient des erreurs passées du même modèle : on applique à la prévision les 10e et 90e centiles des erreurs relatives observées sur les 22 prévisions de l'origine glissante (12 à un mois, 10 à trois mois). Elle contient donc, si le futur se comporte comme le passé, environ huit réalisations sur dix. C'est une fourchette **honnête mais modeste** : elle s'appuie sur 22 erreurs seulement et ignore tout événement qui ne s'est pas produit pendant la période (une panne du site de plusieurs jours, par exemple ; volume III, chapitre 1).

![Prévision de janvier 2026 : environ mille commandes avec les soldes d'hiver, une centaine de moins sans. La barre verticale est la fourchette estimée à partir des erreurs passées.](figures/ch03-janvier-2026.png)

La note qui part chez la gérante tient en quatre lignes, chiffres et conditions comprises :

> *Janvier 2026 : environ 1 010 commandes, probablement entre 980 et 1 060, **si** les soldes d'hiver ont lieu du 8 au 28 janvier comme chaque année. Sans soldes : environ 900. Pour les équipes, prévoir une capacité d'environ 1 045 commandes (la prévision plus 3 %, parce qu'un manque coûte plus cher qu'un surplus). Nous saurons début février si la prévision était juste ; je vous écris l'écart.*

Cette note contient **tout ce qu'une prévision doit contenir** : un chiffre, une fourchette, les hypothèses dont elle dépend, une règle de décision, et la date où l'on mesurera l'erreur. La dernière ligne compte : elle transforme une affirmation en **engagement vérifiable**, et c'est ce qui construit la confiance dans la durée.

> ✅ **À retenir du cas A.** On juge une prévision par **origine glissante** (MAE, MAPE et biais, à plusieurs horizons), contre des **références** de plus en plus fines. Un modèle qui connaît le **calendrier** (jours, mois, promotions planifiées) gagne nettement ici ; on le dit avec **une fourchette tirée de ses erreurs passées** et les **hypothèses** dont il dépend. Un seul mois ne juge pas un modèle, douze origines non plus quand l'écart est petit.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.2 et 3.3, exercices 3.4 et 3.5.
