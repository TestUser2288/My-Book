# Chapitre 4 : Séries temporelles

> « Hier explique un peu aujourd'hui.
> Les séries temporelles sont l'art de mesurer *combien*. »

Jusqu'ici, nous avons presque toujours supposé que nos observations étaient **indépendantes** : 400 commandes tirées au hasard, 2 000 clients qui ne se parlent pas. Cette hypothèse a fait toute la force du volume I (la loi des grands nombres, le théorème central limite, les intervalles de confiance) et celle des régressions des chapitres 1 et 2.

Elle tombe dès qu'on observe **la même chose au fil du temps**. Le chiffre d'affaires de Dar Jasmin en mars dépend de celui de février : une bonne année tire les mois vers le haut, décembre est toujours le mois des fêtes, et un choc comme celui de 2020 se prolonge pendant des mois. Les observations sont **dépendantes**, et c'est précisément cette dépendance qui est à la fois le **piège** (les formules du volume I deviennent fausses) et la **ressource** (le passé permet de prévoir l'avenir).

Ce chapitre apprend à lire, à modéliser et à prévoir une série temporelle, avec une seule série en fil rouge : **dix ans de chiffre d'affaires mensuel de Dar Jasmin** (janvier 2016 à décembre 2025).

## Le chemin de ce chapitre

- **4.1 Stationnarité, autocorrélation, décomposition** : que veut dire « avoir une structure stable dans le temps » ? Comment mesurer la mémoire d'une série (la fonction d'autocorrélation) ? Comment séparer tendance, saisonnalité et bruit ?
- **4.2 Modèles ARIMA et saisonniers** : les briques AR et MA, la méthode de Box-Jenkins, l'ajout de variables explicatives (promotions, COVID), le diagnostic des résidus.
- **4.3 Prévision et évaluation** : prévoir, quantifier l'incertitude, comparer honnêtement des modèles (découpage temporel, mesures d'erreur, validation à origine glissante), et une première révélation sur la façon dont les données ont été fabriquées.
- ➕ **Pour aller plus loin** : modèles multivariés VAR, cointégration et GARCH (4.4) ; modèles d'espace d'états et filtre de Kalman (4.5) ; Prophet et les bibliothèques modernes de prévision (4.6).
- **4.7 Exercices corrigés**.

> 🛠️ **Comment travailler avec ce chapitre.** Le fil conducteur est un **concours de prévision** : plusieurs modèles prévoient les 24 derniers mois de la série, que nous aurons mis de côté **dès le début**, avant même d'avoir regardé les données. Vous verrez que le modèle qui paraît le meilleur sur le papier n'est pas toujours celui qui gagne, et pourquoi. Tapez le code vous-même, changez les paramètres, regardez ce qui casse.

> 📦 **Les données.** Le fichier `donnees/ventes_mensuelles.csv` contient 120 mois : `mois`, `ca` (chiffre d'affaires en DT), `nb_commandes`, `promo` (1 si une promotion a eu lieu dans le mois) et `covid` (1 de mars à juin 2020, quatre mois de fermeture partielle). Comme au chapitre précédent, ces données sont **simulées** avec des graines fixes : nous connaissons donc la vérité, et nous la révélerons à la fin de la section 4.3, pour voir si les méthodes l'ont retrouvée. Les sections 4.4 et 4.5 utilisent aussi des séries simulées à part, annoncées chaque fois.

> 🧭 **Prérequis.** Le volume I (section 2.4 sur la loi des grands nombres, section 3.3 sur les intervalles de confiance, section 3.5 sur les p-valeurs, section 1.1 sur les valeurs propres) et le chapitre 1 de ce volume (la régression linéaire et ses diagnostics, section 1.3). Les modèles ARIMA sont, au fond, des régressions où les variables explicatives sont le passé de la série elle-même.


## 4.1 Stationnarité, autocorrélation, décomposition

> 💡 **Intuition.** Un statisticien qui regarde une série temporelle se pose trois questions, dans cet ordre. **(1)** « Cette série a-t-elle des règles stables dans le temps ? » (la **stationnarité**). **(2)** « Combien de mémoire a-t-elle ? Aujourd'hui ressemble-t-il à hier, à il y a un an ? » (l'**autocorrélation**). **(3)** « Quelle part de ce que je vois est une tendance, une saison, ou du bruit ? » (la **décomposition**). Les modèles des sections suivantes ne sont que des réponses chiffrées à ces trois questions.

### 4.1.1 Pourquoi l'ordre compte : le test du mélange

Prenez 100 commandes tirées au hasard : vous pouvez les mélanger, l'histogramme reste le même, la moyenne aussi. Prenez les 96 chiffres d'affaires mensuels de 2016 à 2023 : si vous les mélangez, **vous détruisez l'information**. Un décembre n'est plus à côté d'un janvier, la tendance a disparu, la mémoire aussi. C'est la différence fondamentale entre un échantillon et une **série temporelle** : l'ordre est une partie de la donnée.

Une règle d'hygiène avant d'aller plus loin. Nous voulons, en fin de chapitre, juger honnêtement des prévisions. Il faut donc **mettre de côté dès maintenant** les 24 derniers mois (2024 et 2025) et ne plus les regarder tant que nous n'avons pas choisi nos modèles. Tout ce que nous ferons dans les sections 4.1 et 4.2 (graphiques, tests, choix d'un modèle) utilisera **uniquement les 96 premiers mois**. Un analyste qui choisit son modèle après avoir vu l'avenir ne prévoit rien : il décrit le passé.

```python
import warnings
warnings.filterwarnings("ignore")        # masque les avertissements de bibliothèques, pour des sorties lisibles
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.api as sm
from statsmodels.tsa.stattools import acf, pacf, adfuller, kpss
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.seasonal import seasonal_decompose, STL

v = pd.read_csv("donnees/ventes_mensuelles.csv", parse_dates=["mois"]).set_index("mois")
v.index.freq = "MS"                      # fréquence « début de mois » : indispensable pour les modèles
y = np.log(v["ca"])                      # on travaille sur le logarithme (voir 4.1.2)
train = y[:"2023-12"]                    # 96 mois pour construire les modèles
test = y["2024-01":]                     # 24 mois mis de côté : on n'y touche plus jusqu'en 4.3
print("apprentissage :", train.index[0].strftime("%Y-%m"), "à", train.index[-1].strftime("%Y-%m"), "-", len(train), "mois")
print("mis de côté   :", test.index[0].strftime("%Y-%m"), "à", test.index[-1].strftime("%Y-%m"), "-", len(test), "mois")
print(v.loc[:"2016-06", ["ca", "nb_commandes", "promo", "covid"]])
```
<!--sortie-->
```text
apprentissage : 2016-01 à 2023-12 - 96 mois
mis de côté   : 2024-01 à 2025-12 - 24 mois
                ca  nb_commandes  promo  covid
mois                                          
2016-01-01   620.0            14      0      0
2016-02-01   757.5            11      0      0
2016-03-01  1007.0            13      0      0
2016-04-01  1018.5            17      0      0
2016-05-01  1067.8            13      0      0
2016-06-01  1155.4            11      0      0
```

Chaque ligne est un mois. Le chiffre d'affaires (`ca`) de janvier 2016 est de 620 DT. Les colonnes `promo` et `covid` sont des variables **explicatives** que nous utiliserons en 4.2.

Pour mesurer à quel point l'ordre compte, calculons la **corrélation entre un mois et le suivant** (nous la définirons proprement en 4.1.4) sur la série, puis sur 1 000 mélanges aléatoires de la même série :

```python
def acf_manuel(x, k):
    """Autocorrélation d'ordre k : corrélation entre la série et elle-même décalée de k pas."""
    d = np.asarray(x, float) - np.mean(x)
    return (d[:len(d) - k] * d[k:]).sum() / (d ** 2).sum()

rng = np.random.default_rng(1)
r_vrai = acf_manuel(train.values, 1)
r_melanges = [acf_manuel(rng.permutation(train.values), 1) for _ in range(1000)]
print("corrélation mois/mois-suivant, série réelle :", round(r_vrai, 3))
print("après mélange aléatoire (1000 essais)       : moyenne", round(np.mean(r_melanges), 3),
      "| écart-type", round(np.std(r_melanges), 3))
print("pour comparaison, 1/racine(96) =", round(1 / np.sqrt(96), 3))
```
<!--sortie-->
```text
corrélation mois/mois-suivant, série réelle : 0.479
après mélange aléatoire (1000 essais)       : moyenne -0.011 | écart-type 0.104
pour comparaison, 1/racine(96) = 0.102
```

La série réelle a une corrélation de l'ordre de 0,48 entre un mois et le suivant ; après mélange, elle tombe en moyenne à zéro, avec une dispersion d'environ 0,10, c'est-à-dire $1/\sqrt{96}$. Cette valeur n'est pas un hasard : nous la retrouverons en 4.1.4 comme **bande de confiance** du graphique d'autocorrélation.

### 4.1.2 Première lecture : tendance, saison, bruit, et pourquoi on prend le logarithme

Dessinons la série d'apprentissage, d'abord en dinars, puis en logarithme :

```python
BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
plt.rcParams.update({"figure.dpi": 100, "savefig.dpi": 200, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": "#e1e0d9", "grid.linewidth": 0.6, "axes.titlesize": 11,
                     "axes.titleweight": "regular", "legend.frameon": False, "font.size": 10})

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.8))
ca_train = v["ca"][:"2023-12"]
ax1.plot(ca_train.index, ca_train, color=BLEU, lw=1.6)
ax1.set_title("Chiffre d'affaires mensuel (DT)")
ax2.plot(train.index, train, color=BLEU, lw=1.6)
ax2.set_title("Logarithme du chiffre d'affaires")
for ax in (ax1, ax2):
    ax.axvspan(pd.Timestamp("2020-03-01"), pd.Timestamp("2020-06-30"), color=ORANGE, alpha=0.18, lw=0)
ax1.text(pd.Timestamp("2020-03-10"), 3150, "COVID", color=ORANGE, fontsize=9)
ax2.text(pd.Timestamp("2020-03-10"), 8.05, "COVID", color=ORANGE, fontsize=9)
plt.tight_layout()
plt.savefig("figures/ch04-serie.png", bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Chiffre d'affaires mensuel de Dar Jasmin de 2016 à 2023 : en dinars (à gauche) l'amplitude des oscillations saisonnières grandit avec le niveau ; en logarithme (à droite), elle reste à peu près constante. La bande orange marque mars-juin 2020.](figures/ch04-serie.png)

On lit quatre choses :

1. Une **tendance** : la série monte globalement, d'un peu plus de 1 000 DT par mois en 2016 à près de 2 000 DT en 2023.
2. Une **saisonnalité** : chaque année se ressemble (creux en janvier, plateau haut l'été, pic en décembre).
3. Un **accident** : le trou de mars à juin 2020.
4. Du **bruit** : des écarts irréguliers autour de la tendance et de la saison.

Observez aussi le panneau de gauche : plus la série monte, plus les oscillations saisonnières s'**élargissent** (l'écart entre le mois le plus haut et le mois le plus bas de l'année est d'environ 1 160 DT en 2017 et d'environ 1 970 DT en 2023). C'est un schéma **multiplicatif** : la saison *multiplie* le niveau au lieu de s'y *ajouter*. Le panneau de droite montre le remède : en **logarithme**, un produit devient une somme ($\log(T\times S\times R)=\log T+\log S+\log R$), et les oscillations ont une amplitude à peu près constante. Vérifions-le chiffre en main :

```python
g = pd.DataFrame({"annee": ca_train.index.year, "brut": ca_train.values, "log": train.values})
amplitude = g.groupby("annee").agg(niveau_moyen=("brut", "mean"),
                                   amplitude_brute=("brut", lambda s: s.max() - s.min()),
                                   amplitude_log=("log", lambda s: s.max() - s.min())).round(2)
print(amplitude)
```
<!--sortie-->
```text
       niveau_moyen  amplitude_brute  amplitude_log
annee                                              
2016        1054.87           1415.4           1.19
2017        1153.82           1162.9           1.00
2018        1273.32           1264.3           1.03
2019        1402.31           1503.8           1.03
2020        1306.68           1571.7           1.02
2021        1737.24           1626.7           1.02
2022        1911.13           1739.5           0.91
2023        1906.96           1968.6           1.00
```

L'amplitude brute passe d'environ 1 160 DT (2017) à environ 1 970 DT (2023), en suivant la croissance du niveau moyen ; l'amplitude en logarithme, elle, reste comprise entre 0,9 et 1,2 pour toutes les années. À partir de maintenant, **nous modélisons le logarithme du chiffre d'affaires**.

> 💡 **Lire une variation en logarithme.** Si $\log y$ augmente de $0{,}05$, alors $y$ est multiplié par $e^{0{,}05}\approx1{,}051$ : une hausse d'environ 5 %. Pour de petites variations, *différence de logarithmes ≈ variation relative*. C'est pourquoi les coefficients des modèles en log se lisent comme des pourcentages.

### 4.1.3 La stationnarité

Pour estimer quelque chose à partir d'**une seule trajectoire** (nous n'avons qu'une seule histoire de Dar Jasmin, on ne peut pas rejouer 2016), il faut que le processus ait des règles qui ne changent pas dans le temps. C'est le sens de la stationnarité.

> 📐 **Définition (stationnarité faible).** Une série $(Y_t)$ est **stationnaire au second ordre** si
> 1. $\mathbb E[Y_t]=\mu$ ne dépend pas de $t$ ;
> 2. $\operatorname{Var}(Y_t)=\sigma^2<\infty$ ne dépend pas de $t$ ;
> 3. $\operatorname{Cov}(Y_t,Y_{t+k})=\gamma(k)$ ne dépend que du **décalage** $k$, pas de $t$.
>
> On appelle $\gamma(k)$ l'**autocovariance** et $\rho(k)=\gamma(k)/\gamma(0)$ l'**autocorrélation** d'ordre $k$. Une série *strictement* stationnaire a toutes ses lois jointes invariantes par translation ; avec une variance finie, elle est faiblement stationnaire. La réciproque est fausse en général (elle est vraie pour les séries gaussiennes). Nous n'utiliserons que la version faible.

Quatre exemples simulés montrent à quoi cela ressemble. Chacun a 200 points, et nous comparons la moyenne et la variance de la **première moitié** à celles de la **seconde** :

```python
rng = np.random.default_rng(4)
n = 200
bruit_blanc = rng.normal(size=n)                          # Y_t = e_t
marche = np.cumsum(rng.normal(size=n))                    # Y_t = Y_{t-1} + e_t
ar1 = np.zeros(n)
for t in range(1, n):
    ar1[t] = 0.8 * ar1[t - 1] + rng.normal()              # Y_t = 0,8 Y_{t-1} + e_t
tendance = 0.05 * np.arange(n) + rng.normal(size=n)       # Y_t = 0,05 t + e_t

exemples = {"bruit blanc": bruit_blanc, "marche aléatoire": marche, "AR(1), phi = 0,8": ar1, "tendance + bruit": tendance}
lignes = []
for nom, s in exemples.items():
    lignes.append({"série": nom, "moyenne 1re moitié": s[:100].mean(), "moyenne 2e moitié": s[100:].mean(),
                   "variance 1re moitié": s[:100].var(), "variance 2e moitié": s[100:].var()})
print(pd.DataFrame(lignes).round(2).to_string(index=False))

fig, axes = plt.subplots(2, 2, figsize=(11, 5.6), sharex=True)
couleurs = [BLEU, ROUGE, AQUA, VIOLET]
for ax, (nom, s), c in zip(axes.ravel(), exemples.items(), couleurs):
    ax.plot(s, color=c, lw=1.3)
    ax.set_title(nom)
plt.tight_layout()
plt.savefig("figures/ch04-stationnarite.png", bbox_inches="tight")
```
<!--sortie-->
```text
           série  moyenne 1re moitié  moyenne 2e moitié  variance 1re moitié  variance 2e moitié
     bruit blanc               -0.06               0.16                 1.02                0.94
marche aléatoire                7.73              16.69                52.92               26.63
AR(1), phi = 0,8               -0.58               0.20                 3.19                2.34
tendance + bruit                2.46               7.45                 3.03                3.16
```

![Quatre séries simulées : le bruit blanc et l'AR(1) fluctuent autour d'un niveau fixe (stationnaires) ; la marche aléatoire erre sans revenir ; la série « tendance + bruit » monte (la moyenne change avec le temps).](figures/ch04-stationnarite.png)

- Le **bruit blanc** (des chocs indépendants) et l'**AR(1)** (nous l'étudierons en 4.2) gardent des moyennes et des variances comparables d'une moitié à l'autre : ils sont stationnaires.
- La **série avec tendance** a une variance stable mais une moyenne qui change (environ 2,5 puis 7,5) : elle viole la condition 1.
- La **marche aléatoire** a une moyenne et une variance très différentes d'une moitié à l'autre : elle viole les conditions 1 et 2.

La marche aléatoire est l'exemple fondamental de non-stationnarité. Montrons rigoureusement que sa variance explose :

> 📐 **Démonstration : la variance d'une marche aléatoire croît linéairement.** Soit $Y_t=Y_{t-1}+\varepsilon_t$ avec $Y_0=0$ et des $\varepsilon_t$ indépendants de variance $\sigma^2$. En remplaçant récursivement, $Y_t=\varepsilon_1+\varepsilon_2+\dots+\varepsilon_t$ : une somme de $t$ chocs indépendants. Donc $\operatorname{Var}(Y_t)=t\,\sigma^2$, qui dépend de $t$ et tend vers l'infini. La série ne revient jamais « se stabiliser » : chaque choc a un effet **permanent**. $\blacksquare$

Vérifions par simulation : 5 000 marches aléatoires de 200 pas, et la variance **à travers les trajectoires** à trois instants :

```python
trajectoires = np.cumsum(np.random.default_rng(5).normal(size=(5000, 200)), axis=1)
for t in (50, 100, 200):
    print(f"t = {t:3d} : variance observée = {trajectoires[:, t - 1].var():6.1f}   (théorie : t x sigma^2 = {t})")
```
<!--sortie-->
```text
t =  50 : variance observée =   50.3   (théorie : t x sigma^2 = 50)
t = 100 : variance observée =   96.4   (théorie : t x sigma^2 = 100)
t = 200 : variance observée =  194.0   (théorie : t x sigma^2 = 200)
```

> ⚠️ **Deux façons d'être non stationnaire, deux traitements.** Une série peut avoir une **tendance déterministe** (comme $Y_t=a+bt+u_t$ avec $u_t$ stationnaire : on dit « stationnaire autour d'une tendance »), ou une **tendance stochastique** (comme la marche aléatoire : les chocs s'accumulent). Le premier cas se traite en **retirant la tendance par régression** ; le second en **différenciant** ($Z_t=Y_t-Y_{t-1}$). Appliquer le mauvais remède abîme la série : nous le montrerons en 4.1.6.

Et notre série de chiffre d'affaires ? Elle a une tendance, une saison forte et un accident : elle n'est évidemment **pas stationnaire telle quelle**. La question est de savoir *quelle sorte* de non-stationnarité elle a, ce qui détermine le traitement.

### 4.1.4 L'autocorrélation : mesurer la mémoire

Reprenons la définition : $\rho(k)=\operatorname{Corr}(Y_t,Y_{t+k})$, la corrélation entre la série et elle-même décalée de $k$ pas. On l'estime à partir d'un échantillon $y_1,\dots,y_n$ par

$$r_k=\frac{\sum_{t=k+1}^{n}(y_t-\bar y)(y_{t-k}-\bar y)}{\sum_{t=1}^{n}(y_t-\bar y)^2}.$$

> 💡 **Exemple à la main.** Six chiffres : $10,\ 12,\ 11,\ 14,\ 13,\ 15$. Leur moyenne est $\bar y=12{,}5$ ; les écarts sont $-2{,}5,\ -0{,}5,\ -1{,}5,\ 1{,}5,\ 0{,}5,\ 2{,}5$. Le dénominateur est $\sum(y_t-\bar y)^2=6{,}25+0{,}25+2{,}25+2{,}25+0{,}25+6{,}25=17{,}5$.
> **Décalage 1** : on multiplie chaque écart par le précédent : $(-0{,}5)(-2{,}5)=1{,}25$ ; $(-1{,}5)(-0{,}5)=0{,}75$ ; $(1{,}5)(-1{,}5)=-2{,}25$ ; $(0{,}5)(1{,}5)=0{,}75$ ; $(2{,}5)(0{,}5)=1{,}25$. La somme vaut $1{,}75$, donc $r_1=1{,}75/17{,}5=0{,}10$.
> **Décalage 2** : $(-1{,}5)(-2{,}5)=3{,}75$ ; $(1{,}5)(-0{,}5)=-0{,}75$ ; $(0{,}5)(-1{,}5)=-0{,}75$ ; $(2{,}5)(1{,}5)=3{,}75$. La somme vaut $6$, donc $r_2=6/17{,}5\approx0{,}343$.

```python
x = np.array([10, 12, 11, 14, 13, 15])
print("r1 =", round(acf_manuel(x, 1), 4), "  r2 =", round(acf_manuel(x, 2), 4))
```
<!--sortie-->
```text
r1 = 0.1   r2 = 0.3429
```

Le code retrouve exactement les valeurs de la main. Notez que le dénominateur est toujours la somme des **$n$ termes** (même pour $k$ grand), ce qui garantit que les autocorrélations estimées forment toujours une suite « possible » (semi-définie positive). Appliquons-le à la série d'apprentissage et comparons avec la fonction de `statsmodels` :

```python
r_perso = np.array([acf_manuel(train.values, k) for k in range(7)])
r_sm = acf(train, nlags=6, fft=False)
print("manuel   :", r_perso.round(3))
print("statsmodels:", r_sm.round(3))
print("identiques :", np.allclose(r_perso, r_sm))
```
<!--sortie-->
```text
manuel   : [1.    0.479 0.224 0.305 0.344 0.283 0.191]
statsmodels: [1.    0.479 0.224 0.305 0.344 0.283 0.191]
identiques : True
```

#### L'autocorrélation partielle

L'autocorrélation d'ordre 2 mélange deux effets : l'influence directe de $y_{t-2}$ sur $y_t$, et l'influence **indirecte** passant par $y_{t-1}$ (qui dépend lui-même de $y_{t-2}$). L'**autocorrélation partielle** d'ordre $k$, notée $\varphi_{kk}$, isole l'effet direct : c'est le **coefficient de $y_{t-k}$ dans la régression de $y_t$ sur $y_{t-1},\dots,y_{t-k}$**. On peut donc la calculer avec les moindres carrés du chapitre 1 :

```python
def pacf_manuel(x, k):
    x = np.asarray(x, float)
    n = len(x)
    cible = x[k:]
    explicatives = np.column_stack([np.ones(n - k)] + [x[k - j:n - j] for j in range(1, k + 1)])
    coef = np.linalg.lstsq(explicatives, cible, rcond=None)[0]
    return coef[-1]                                   # coefficient de y_{t-k}

p_sm = pacf(train, nlags=3, method="ols")
print("pacf manuelle   :", np.round([pacf_manuel(train.values, k) for k in (1, 2, 3)], 4))
print("pacf statsmodels:", p_sm[1:].round(4))
```
<!--sortie-->
```text
pacf manuelle   : [0.5074 0.0042 0.2814]
pacf statsmodels: [0.5074 0.0042 0.2814]
```

Les deux concordent : l'autocorrélation partielle n'est rien d'autre qu'une régression, ce qui annonce les modèles autorégressifs de la section 4.2.

#### Les bandes de confiance

Sur un graphique d'autocorrélation, on trace une bande autour de zéro. D'où vient-elle ? Pour un **bruit blanc** (aucune mémoire), les $r_k$ sont approximativement gaussiens, centrés, de variance $1/n$ (c'est le théorème central limite du volume I, section 2.4, appliqué à une somme de produits). D'où la bande $\pm1{,}96/\sqrt n$ à 95 %. Vérifions par simulation que le taux de fausses alertes est bien d'environ 5 % :

```python
rng = np.random.default_rng(2)
n = 96
alertes = np.mean([abs(acf_manuel(rng.normal(size=n), 1)) > 1.96 / np.sqrt(n) for _ in range(2000)])
print("bande :", round(1.96 / np.sqrt(n), 3), "| part de bruits blancs avec |r1| hors bande :", round(alertes, 3))
```
<!--sortie-->
```text
bande : 0.2 | part de bruits blancs avec |r1| hors bande : 0.046
```

> ⚠️ **Une barre qui dépasse n'est pas une catastrophe.** À 95 %, sur 20 décalages, **une** barre dépasse en moyenne la bande même pour du bruit pur. Ce qui compte, ce sont les barres **nettement** hors bande, ou une structure répétée (tous les 12 mois, par exemple).

Voici l'autocorrélation et l'autocorrélation partielle de notre série d'apprentissage (en logarithme), sur 24 décalages :

```python
def tracer_acf(ax, valeurs, n, titre, couleur=BLEU):
    k = np.arange(len(valeurs))
    ax.vlines(k, 0, valeurs, color=couleur, lw=2)
    ax.plot(k, valeurs, "o", color=couleur, ms=3.5)
    ax.axhline(0, color="#898781", lw=0.8)
    b = 1.96 / np.sqrt(n)
    ax.axhspan(-b, b, color=couleur, alpha=0.10, lw=0)
    ax.set_title(titre)
    ax.set_xlabel("décalage (mois)")
    ax.set_ylim(-1, 1)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.6))
tracer_acf(ax1, acf(train, nlags=24, fft=False), len(train), "Autocorrélation de log(ca)")
tracer_acf(ax2, pacf(train, nlags=24, method="ols"), len(train), "Autocorrélation partielle de log(ca)", ORANGE)
plt.tight_layout()
plt.savefig("figures/ch04-acf-serie.png", bbox_inches="tight")
```

![Autocorrélation (à gauche) et autocorrélation partielle (à droite) du logarithme du chiffre d'affaires sur les 96 mois d'apprentissage ; la zone colorée est la bande de confiance à 95 % d'un bruit blanc.](figures/ch04-acf-serie.png)

L'autocorrélation reste significative sur de nombreux décalages (la série a une longue mémoire, due à la tendance et à la saison), avec des bosses aux multiples de 12 : la signature de la saisonnalité annuelle.

### 4.1.5 Le bruit blanc et le test de Ljung-Box

Un **bruit blanc** est une suite de variables indépendantes, centrées, de même variance : la série la plus ennuyeuse possible, **sans mémoire**. Il joue un rôle central, car c'est ce qu'il doit **rester** quand un modèle a tout expliqué : si les résidus d'un modèle ne ressemblent pas à un bruit blanc, il reste de l'information à exploiter.

Pour tester cela globalement (plutôt que décalage par décalage), on utilise la statistique de **Ljung-Box** :

$$Q(h)=n(n+2)\sum_{k=1}^{h}\frac{r_k^2}{n-k}.$$

Sous l'hypothèse « bruit blanc », $Q(h)$ suit approximativement une loi du khi-deux à $h$ degrés de liberté (volume I, section 3.4.6). Une grande valeur de $Q$ signifie qu'au moins une autocorrélation est trop forte pour être due au hasard. Calculons-la à la main puis avec `statsmodels`, sur un vrai bruit blanc simulé et sur notre série :

```python
def ljung_box(x, h):
    x = np.asarray(x, float)
    n = len(x)
    r = np.array([acf_manuel(x, k) for k in range(1, h + 1)])
    Q = n * (n + 2) * np.sum(r ** 2 / (n - np.arange(1, h + 1)))
    return Q, 1 - stats.chi2.cdf(Q, h)

w = np.random.default_rng(6).normal(size=96)
for nom, s in [("bruit blanc simulé", w), ("log(ca), apprentissage", train.values)]:
    Q, p = ljung_box(s, 10)
    print(f"{nom:24s} Q(10) = {Q:7.2f}   p-valeur = {p:.2e}")
sm_lb = acorr_ljungbox(train, lags=[10])
print("statsmodels (log ca)      Q(10) =", round(float(sm_lb['lb_stat'].iloc[0]), 2))
```
<!--sortie-->
```text
bruit blanc simulé       Q(10) =    9.52   p-valeur = 4.84e-01
log(ca), apprentissage   Q(10) =   84.00   p-valeur = 8.20e-14
statsmodels (log ca)      Q(10) = 84.0
```

Pour le bruit blanc, la p-valeur est grande : on ne rejette pas l'hypothèse « pas de mémoire ». Pour notre série, elle est pratiquement nulle : la série a de la mémoire, ce que l'œil voyait déjà.

> ⚠️ **Quand on teste des résidus de modèle.** Si l'on applique Ljung-Box aux résidus d'un modèle qui a estimé $m$ paramètres de type AR ou MA, il faut réduire les degrés de liberté à $h-m$. Nous le ferons en 4.2.

### 4.1.6 Rendre une série stationnaire : différencier, et tester

Reprenons la distinction de 4.1.3. Pour une **marche aléatoire**, on **différencie** : $\nabla Y_t=Y_t-Y_{t-1}=\varepsilon_t$ est un bruit blanc. Pour une série à **saison** de période $s=12$, on peut utiliser la **différence saisonnière** $\nabla_{12}Y_t=Y_t-Y_{t-12}$ (comparer chaque mois au même mois de l'an passé). Pour notre série en logarithme, cela a une belle interprétation :

- $\nabla\log y_t=\log y_t-\log y_{t-1}\approx$ **taux de croissance mensuel** ;
- $\nabla_{12}\log y_t\approx$ **taux de croissance sur un an**, c'est-à-dire le « +x % par rapport au même mois l'an dernier » des bilans d'entreprise.

Comment décider si une série a besoin d'être différenciée ? On utilise des **tests de racine unitaire**. Le plus célèbre est le **test de Dickey-Fuller**. Son idée : dans le modèle $Y_t=\rho Y_{t-1}+\varepsilon_t$, la série est une marche aléatoire si $\rho=1$ (racine unitaire) et stationnaire si $|\rho|<1$. En retranchant $Y_{t-1}$ des deux côtés, on obtient la régression

$$\nabla Y_t=\alpha+\gamma\,Y_{t-1}+e_t,\qquad \gamma=\rho-1,$$

et on teste $H_0:\gamma=0$ (racine unitaire) contre $\gamma<0$ (stationnaire), avec la statistique de Student habituelle de $\hat\gamma$.

> ⚠️ **Le piège : cette statistique ne suit PAS la loi de Student.** Sous $H_0$, la série n'est pas stationnaire, et les théorèmes du volume I (sur lesquels reposent Student et la loi normale) ne s'appliquent plus. La loi de la statistique est **différente** et se simule. Faisons-le : 5 000 marches aléatoires de 100 pas, la statistique de Dickey-Fuller de chacune, et ses quantiles.

```python
def stat_df(s):
    """Statistique t de gamma dans : diff(Y_t) = alpha + gamma * Y_{t-1} + e_t."""
    s = np.asarray(s, float)
    d = np.diff(s)
    X = np.column_stack([np.ones(len(d)), s[:-1]])
    b = np.linalg.lstsq(X, d, rcond=None)[0]
    e = d - X @ b
    s2 = e @ e / (len(d) - 2)
    cov = s2 * np.linalg.inv(X.T @ X)
    return b[1] / np.sqrt(cov[1, 1])

rng = np.random.default_rng(7)
stats_sim = np.array([stat_df(np.cumsum(rng.normal(size=100))) for _ in range(5000)])
q = [1, 5, 10]
print("quantiles à 1 %, 5 %, 10 % de la loi de Dickey-Fuller simulée :", np.percentile(stats_sim, q).round(2))
print("quantiles de la loi normale                                     :", stats.norm.ppf([0.01, 0.05, 0.10]).round(2))
print("part des marches aléatoires « rejetées » avec le seuil normal -1,645 :", round(np.mean(stats_sim < -1.645), 3))

fig, ax = plt.subplots(figsize=(7, 3.4))
ax.hist(stats_sim, bins=60, density=True, color=BLEU, alpha=0.75, label="statistique de Dickey-Fuller (simulée)")
xs = np.linspace(-5, 3, 300)
ax.plot(xs, stats.norm.pdf(xs), color=ORANGE, lw=2, label="loi normale")
ax.axvline(np.percentile(stats_sim, 5), color=ROUGE, ls="--", lw=1.2)
ax.text(np.percentile(stats_sim, 5) - 0.1, 0.40, "seuil à 5 %", color=ROUGE, ha="right", fontsize=9)
ax.set_xlabel("valeur de la statistique")
ax.legend(loc="upper right")
plt.tight_layout()
plt.savefig("figures/ch04-dickey-fuller.png", bbox_inches="tight")
```
<!--sortie-->
```text
quantiles à 1 %, 5 %, 10 % de la loi de Dickey-Fuller simulée : [-3.52 -2.92 -2.56]
quantiles de la loi normale                                     : [-2.33 -1.64 -1.28]
part des marches aléatoires « rejetées » avec le seuil normal -1,645 : 0.468
```

![Loi simulée de la statistique de Dickey-Fuller sous l'hypothèse de racine unitaire (histogramme bleu), décalée vers la gauche par rapport à la loi normale (orange). Le seuil à 5 % se situe vers −2,9 et non −1,64.](figures/ch04-dickey-fuller.png)

Le seuil à 5 % est d'environ $-2{,}9$ (et non $-1{,}645$). Utiliser par erreur le seuil normal ferait « rejeter » la racine unitaire pour près d'une marche aléatoire sur deux : un test nul. Les logiciels utilisent les vraies tables, obtenues par simulation comme ici (Dickey et Fuller, 1979).

Le test de Dickey-Fuller **augmenté** (ADF) ajoute à la régression des différences retardées $\nabla Y_{t-1},\nabla Y_{t-2},\dots$ pour absorber l'autocorrélation. Le test **KPSS** renverse les rôles : son hypothèse nulle est que la série est **stationnaire** (autour d'un niveau ou d'une tendance). Les deux tests se complètent :

| ADF | KPSS | Lecture |
|---|---|---|
| rejette la racine unitaire | ne rejette pas la stationnarité | **stationnaire** (autour de la tendance éventuelle) |
| ne rejette pas | rejette | **racine unitaire** : différencier |
| les deux rejettent / aucun ne rejette | | **verdict ambigu** : les données ne tranchent pas |

Appliquons les deux à notre série d'apprentissage, selon qu'on autorise ou non une tendance déterministe :

```python
def tester(s, regression, nom):
    a = adfuller(s, regression=regression, autolag="AIC")
    k = kpss(s, regression=regression, nlags="auto")
    return {"série": nom, "ADF stat": a[0], "ADF p": a[1], "retards": a[2], "seuil 5 %": a[4]["5%"],
            "KPSS stat": k[0], "KPSS p": k[1]}

lignes = [tester(train, "ct", "log(ca), avec tendance"),
          tester(train, "c", "log(ca), niveau seul"),
          tester(train.diff().dropna(), "c", "différence première"),
          tester(train.diff(12).dropna(), "c", "différence saisonnière (12)"),
          tester(train.diff().diff(12).dropna(), "c", "différences 1 et 12")]
tab = pd.DataFrame(lignes).set_index("série")
print(tab.round(3).to_string())
```
<!--sortie-->
```text
                             ADF stat  ADF p  retards  seuil 5 %  KPSS stat  KPSS p
série                                                                              
log(ca), avec tendance         -3.228  0.079       12     -3.465      0.042    0.10
log(ca), niveau seul           -1.064  0.729       12     -2.897      1.561    0.01
différence première            -3.617  0.005       12     -2.897      0.185    0.10
différence saisonnière (12)    -2.418  0.137       12     -2.903      0.057    0.10
différences 1 et 12            -4.436  0.000       11     -2.903      0.023    0.10
```

> ⚠️ **La lecture honnête de ce tableau.** La p-valeur de KPSS est tronquée à 0,10 (borne de la table) ou à 0,01, d'où les valeurs « rondes ».
> - **Avec tendance** : ADF obtient une p-valeur de l'ordre de 0,08, **au-dessus de 5 %**, donc il ne rejette pas la racine unitaire ; mais KPSS, de son côté, **ne rejette pas non plus** la stationnarité autour d'une tendance. C'est le cas ambigu de la troisième ligne du tableau. Avec seulement 96 observations, un COVID au milieu et une saison forte (l'ADF a dû utiliser 12 retards pour l'absorber), le test a **peu de puissance** : il ne peut pas trancher.
> - **Sans tendance** : les deux tests s'accordent pour dire que la série n'est pas stationnaire autour d'un niveau constant (ce qui est évident : elle monte).
> - **Après différenciation** : avec la différence première ou avec les deux différences (1 et 12), les deux tests s'accordent pour la stationnarité. La seule différence saisonnière laisse en revanche un verdict ambigu (l'ADF a une p-valeur de l'ordre de 0,14 : il ne rejette pas la racine unitaire).
>
> **Conclusion** : les données sont compatibles avec **deux** descriptions, « tendance stochastique » (il faut différencier) et « tendance déterministe » (il faut modéliser la tendance et la saison). Plutôt que de forcer un verdict, nous garderons **les deux** candidats en 4.2 et les départagerons en 4.3 par ce qui compte vraiment : la qualité des prévisions.

#### Le danger de la sur-différenciation

Que se passe-t-il si l'on différencie une série qui n'en avait pas besoin ? Prenons un bruit blanc pur, déjà stationnaire, et différencions-le : $\nabla\varepsilon_t=\varepsilon_t-\varepsilon_{t-1}$.

> 📐 **Calcul.** $\operatorname{Var}(\nabla\varepsilon_t)=2\sigma^2$ et $\operatorname{Cov}(\nabla\varepsilon_t,\nabla\varepsilon_{t-1})=\operatorname{Cov}(\varepsilon_t-\varepsilon_{t-1},\varepsilon_{t-1}-\varepsilon_{t-2})=-\sigma^2$. Donc l'autocorrélation d'ordre 1 de la série différenciée vaut $-\sigma^2/(2\sigma^2)=-0{,}5$ : on a **fabriqué** une mémoire artificielle (un « MA(1) avec $\theta=-1$ », que nous étudierons en 4.2).

```python
w = np.random.default_rng(9).normal(size=2000)
print("autocorrélation d'ordre 1 de diff(bruit blanc) :", round(acf_manuel(np.diff(w), 1), 3), "   théorie : -0,5")
print("autocorrélations de la différence première de log(ca) (décalages 1 à 13) :")
print(acf(train.diff().dropna(), nlags=13)[1:].round(2))
```
<!--sortie-->
```text
autocorrélation d'ordre 1 de diff(bruit blanc) : -0.522    théorie : -0,5
autocorrélations de la différence première de log(ca) (décalages 1 à 13) :
[-0.24 -0.31  0.02  0.1   0.04 -0.18  0.04  0.11  0.07 -0.29 -0.25  0.75
 -0.19]
```

Un signe de sur-différenciation est donc une autocorrélation d'ordre 1 **fortement négative** (autour de $-0{,}5$) et un modèle dont le coefficient MA est proche de $-1$. Gardons cela en tête.

### 4.1.7 Décomposer : tendance, saison, reste

La **décomposition** sépare la série en trois composantes. Sur le logarithme (donc **multiplicative** sur la série d'origine) :

$$\log y_t=T_t+S_t+R_t \quad\Longleftrightarrow\quad y_t=e^{T_t}\times e^{S_t}\times e^{R_t}.$$

La méthode **classique** procède en trois temps :
1. **Tendance** $T_t$ : une moyenne mobile **centrée** sur 12 mois, qui « efface » la saison puisqu'elle contient un exemplaire de chaque mois. Pour une période paire, on utilise la moyenne mobile $2\times12$ (poids $1/24$ aux extrémités, $1/12$ pour les 11 mois du milieu) afin de rester centré sur un mois.
2. **Saison** $S_t$ : on retire la tendance, puis on **moyenne par mois calendaire** (tous les janviers, tous les février…), et on recentre pour que la somme sur l'année soit nulle.
3. **Reste** $R_t=\log y_t-T_t-S_t$.

```python
def decomposition_manuelle(s, m=12):
    poids = np.r_[0.5, np.ones(m - 1), 0.5] / m                      # moyenne mobile 2 x 12
    tendance = pd.Series(np.convolve(s.values, poids, mode="valid"), index=s.index[m // 2: -(m // 2)])
    sans_tendance = s - tendance
    saison = sans_tendance.groupby(sans_tendance.index.month).mean()
    saison = saison - saison.mean()
    return tendance, saison

tendance_m, saison_m = decomposition_manuelle(train)
dec = seasonal_decompose(train, model="additive", period=12)
print("tendance identique à statsmodels :", np.allclose(dec.trend.dropna(), tendance_m.reindex(dec.trend.dropna().index)))
saison_sm = dec.seasonal.groupby(dec.seasonal.index.month).first()
print("saison identique à statsmodels   :", np.allclose(saison_sm.values, saison_m.values))
```
<!--sortie-->
```text
tendance identique à statsmodels : True
saison identique à statsmodels   : True
```

La méthode classique a deux défauts : elle perd 6 mois à chaque extrémité (la moyenne mobile centrée n'est pas définie), et elle est **sensible aux accidents** : le COVID de 2020 contamine à la fois la tendance et, via les moyennes par mois, la saison. La méthode **STL** (*Seasonal-Trend decomposition using LOESS*) remédie aux deux : elle estime tendance et saison par régressions locales, et son option `robust=True` **réduit le poids des observations aberrantes** pour que l'accident n'abîme pas les composantes.

```python
stl = STL(train, period=12, robust=True).fit()
fig, axes = plt.subplots(4, 1, figsize=(10, 7.6), sharex=True)
for ax, (nom, comp, c) in zip(axes, [("log(ca)", train, BLEU), ("tendance", stl.trend, VIOLET),
                                       ("saison", stl.seasonal, AQUA), ("reste", stl.resid, ORANGE)]):
    ax.plot(comp.index, comp, color=c, lw=1.5)
    ax.set_ylabel(nom)
axes[3].axhline(0, color="#898781", lw=0.8)
axes[3].axvspan(pd.Timestamp("2020-03-01"), pd.Timestamp("2020-06-30"), color=ORANGE, alpha=0.18, lw=0)
plt.tight_layout()
plt.savefig("figures/ch04-decomposition.png", bbox_inches="tight")

indices = (np.exp(stl.seasonal[:12]) * 100).round(0)
indices.index = ["jan", "fév", "mar", "avr", "mai", "juin", "juil", "août", "sept", "oct", "nov", "déc"]
print("indices saisonniers (100 = mois moyen) :")
print(indices.astype(int).to_string())
print()
print("les 5 plus gros résidus négatifs :")
print(stl.resid.nsmallest(5).round(2).to_string())
print("écart-type du reste : tous les mois =", round(stl.resid.std(), 3),
      "| hors mars-juin 2020 =", round(stl.resid.drop(stl.resid["2020-03":"2020-06"].index).std(), 3))
```
<!--sortie-->
```text
indices saisonniers (100 = mois moyen) :
jan      65
fév      80
mar     104
avr     106
mai     109
juin    119
juil    119
août    113
sept     84
oct      77
nov     100
déc     160

les 5 plus gros résidus négatifs :
mois
2020-06-01   -0.71
2020-05-01   -0.68
2020-04-01   -0.59
2020-03-01   -0.48
2023-05-01   -0.29
écart-type du reste : tous les mois = 0.146 | hors mars-juin 2020 = 0.077
```

![Décomposition STL robuste du logarithme du chiffre d'affaires (96 mois) : série, tendance, saison, reste. Le reste est petit partout, sauf pendant le COVID (bande orange).](figures/ch04-decomposition.png)

La décomposition raconte l'histoire de la boutique : la **tendance** monte régulièrement, puis semble ralentir à partir de 2021 (STL est un lissage : sa fin de tendance est moins fiable, et nous reverrons en 4.3 si ce ralentissement est réel) ; la **saison** a un profil stable d'une année sur l'autre ; les **résidus** sont petits, sauf les quatre mois de mars à juin 2020 qui ressortent comme les quatre plus gros résidus négatifs. Les **indices saisonniers** se lisent directement : décembre est environ 60 % au-dessus du mois moyen, janvier et février environ 20 à 35 % en dessous.

> 💡 **À quoi sert la décomposition ?** (1) À **comprendre** : « quelle part de la hausse est de la vraie croissance, quelle part est la saison ? ». (2) À **corriger des variations saisonnières** (CVS) : diviser par l'indice saisonnier pour comparer février à décembre. (3) À **repérer les accidents**, ici le COVID, que nous devrons traiter explicitement dans les modèles.

> ✅ **À retenir.**
> - Une série temporelle a des observations **dépendantes** ; l'ordre fait partie de la donnée. Mettez de côté la fin de la série **avant** de choisir un modèle.
> - La **stationnarité faible** : moyenne et variance constantes, autocovariance qui ne dépend que du décalage. La marche aléatoire n'est pas stationnaire ($\operatorname{Var}=t\sigma^2$).
> - L'**autocorrélation** mesure la mémoire ; l'**autocorrélation partielle** est un coefficient de régression qui isole l'effet direct. Bande de confiance : $\pm1{,}96/\sqrt n$.
> - **Ljung-Box** teste globalement l'absence d'autocorrélation ; un bon modèle laisse des résidus « bruit blanc ».
> - **Différencier** retire une tendance stochastique ; **sur-différencier** crée une autocorrélation artificielle de $-0{,}5$. La statistique de Dickey-Fuller n'est **pas** de loi normale : son seuil à 5 % est d'environ $-2{,}9$.
> - Les tests de racine unitaire (ADF, KPSS) ont **peu de puissance** sur de courtes séries : quand ils ne tranchent pas, gardez les deux hypothèses de travail et départagez-les par la prévision.
> - On **décompose** (STL robuste) en tendance, saison et reste ; le logarithme transforme un schéma multiplicatif en schéma additif.


## 4.2 Modèles ARIMA et saisonniers

> 💡 **Intuition.** Une série temporelle, c'est un enchaînement : ce qui se passe aujourd'hui dépend un peu de ce qui s'est passé hier, et un peu des **surprises** récentes. Les modèles ARIMA formalisent ces deux idées avec deux briques. La brique **AR** (*autorégressive*) dit : « la valeur d'aujourd'hui est un écho de celle d'hier ». La brique **MA** (*moyenne mobile*, *moving average*) dit : « la valeur d'aujourd'hui garde la trace des chocs d'hier ». On les assemble, on ajoute une différenciation (le **I** de *integrated*) et une version saisonnière, et on obtient la famille la plus utilisée de la prévision statistique.

Nous partons des briques sur des séries **simulées**, où l'on connaît la vérité, pour comprendre ce que chaque modèle fabrique et comment le reconnaître. Puis nous les appliquerons aux ventes de Dar Jasmin.

### 4.2.1 Les deux briques : AR et MA

Dans toute la suite, $\varepsilon_t$ désigne un **bruit blanc** (4.1.5), les « surprises » du mois : des chocs indépendants, centrés, de variance $\sigma^2$.

- **AR(1)** : $\;Y_t=\varphi\,Y_{t-1}+\varepsilon_t$. La valeur du jour est une fraction $\varphi$ de celle de la veille, plus une surprise. Si $\varphi=0{,}7$, 70 % du niveau d'hier « survit » aujourd'hui.
- **AR($p$)** : $\;Y_t=\varphi_1Y_{t-1}+\dots+\varphi_pY_{t-p}+\varepsilon_t$ (une régression sur ses $p$ propres valeurs passées).
- **MA(1)** : $\;Y_t=\varepsilon_t+\theta\,\varepsilon_{t-1}$. La valeur du jour est la surprise du jour plus une fraction $\theta$ de la surprise d'hier. Un choc a donc un effet qui dure **exactement un pas**, puis disparaît.
- **MA($q$)** : $\;Y_t=\varepsilon_t+\theta_1\varepsilon_{t-1}+\dots+\theta_q\varepsilon_{t-q}$.

> 💡 **Deux mémoires différentes.** Dans un AR, un choc se **propage indéfiniment** en s'estompant (hier m'influence, qui a influencé avant-hier, etc.). Dans un MA($q$), un choc a un effet **limité** à $q$ pas. Pensez à un AR comme à une cloche qui résonne, et à un MA comme à un coup de tampon qui laisse une trace de durée fixe.

Comment reconnaître l'un ou l'autre sur des données ? Grâce à leurs **signatures** dans l'autocorrélation (ACF) et l'autocorrélation partielle (PACF) de 4.1.4 :

| Modèle | ACF | PACF |
|---|---|---|
| AR($p$) | décroît progressivement (géométriquement) | **s'annule après le décalage $p$** |
| MA($q$) | **s'annule après le décalage $q$** | décroît progressivement |
| ARMA($p,q$) | décroît progressivement | décroît progressivement |

Vérifions-le. La fonction `ArmaProcess` de `statsmodels` calcule les autocorrélations **théoriques** d'un modèle ; nous les comparons à celles d'une trajectoire simulée de 500 points (les points), pour trois modèles : AR(1) avec $\varphi=0{,}7$, AR(2) avec $\varphi_1=0{,}5$ et $\varphi_2=0{,}3$, MA(1) avec $\theta=0{,}7$.

```python
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.api as sm
from statsmodels.tsa.arima_process import ArmaProcess, arma_acf, arma_pacf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.stats.diagnostic import acorr_ljungbox

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
modeles_sim = {"AR(1), phi = 0,7": ([1, -0.7], [1]),
               "AR(2), phi = (0,5 ; 0,3)": ([1, -0.5, -0.3], [1]),
               "MA(1), theta = 0,7": ([1], [1, 0.7])}      # convention de statsmodels : polynômes en B, AR avec signe moins

fig, axes = plt.subplots(2, 3, figsize=(11, 5.2), sharey=True)
for j, (nom, (ar, ma)) in enumerate(modeles_sim.items()):
    x = ArmaProcess(ar, ma).generate_sample(500, distrvs=np.random.default_rng(10 + j).standard_normal)
    for i, (theo, emp, titre, c) in enumerate([(arma_acf(ar, ma, 13), acf(x, nlags=12, fft=False), "ACF", BLEU),
                                                (arma_pacf(ar, ma, 13), pacf(x, nlags=12, method="ols"), "PACF", ORANGE)]):
        ax = axes[i, j]
        ax.vlines(np.arange(13), 0, theo, color=c, lw=2, alpha=0.55)
        ax.plot(np.arange(13), emp, "o", color=ROUGE, ms=3.5)
        ax.axhline(0, color="#898781", lw=0.8)
        ax.axhspan(-1.96 / np.sqrt(500), 1.96 / np.sqrt(500), color=c, alpha=0.10, lw=0)
        ax.set_title(f"{titre} - {nom}", fontsize=9.5)
        if i == 1:
            ax.set_xlabel("décalage")
plt.tight_layout()
plt.savefig("figures/ch04-signatures.png", bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Signatures théoriques (barres) et empiriques (points rouges, 500 observations simulées) : l'AR(1) a une ACF qui décroît et une PACF qui s'arrête au décalage 1 ; l'AR(2) a une PACF qui s'arrête au décalage 2 ; le MA(1) a une ACF qui s'arrête au décalage 1 et une PACF qui décroît.](figures/ch04-signatures.png)

Les signatures du tableau apparaissent nettement : la PACF de l'AR(1) n'a qu'une barre, celle de l'AR(2) en a deux, et l'ACF du MA(1) n'en a qu'une. Retenez cette figure : **c'est l'outil d'identification des modèles** que nous utiliserons en 4.2.4.

### 4.2.2 L'AR(1) et le MA(1) en profondeur

#### L'AR(1) : stationnarité, variance, autocorrélations

> 📐 **Proposition.** Soit $Y_t=\varphi Y_{t-1}+\varepsilon_t$ avec $|\varphi|<1$. Alors la série admet la représentation $Y_t=\sum_{j=0}^{\infty}\varphi^j\varepsilon_{t-j}$, elle est stationnaire, de moyenne $0$ et de variance $\gamma(0)=\dfrac{\sigma^2}{1-\varphi^2}$, et son autocorrélation est $\rho(k)=\varphi^{k}$.
>
> **Démonstration.** En remplaçant $Y_{t-1}$ par $\varphi Y_{t-2}+\varepsilon_{t-1}$, puis $Y_{t-2}$, etc., on obtient $Y_t=\varepsilon_t+\varphi\varepsilon_{t-1}+\varphi^2\varepsilon_{t-2}+\dots$. La série $\sum\varphi^{2j}$ converge si et seulement si $|\varphi|<1$, vers $1/(1-\varphi^2)$. Les $\varepsilon$ étant non corrélés, $\operatorname{Var}(Y_t)=\sigma^2\sum_j\varphi^{2j}=\sigma^2/(1-\varphi^2)$, indépendant de $t$ ; la moyenne est nulle. Pour l'autocovariance, on multiplie l'équation par $Y_{t-k}$ ($k\ge1$) et on prend l'espérance : $\gamma(k)=\varphi\,\gamma(k-1)$ (car $\varepsilon_t$ est non corrélé avec $Y_{t-k}$). Donc $\gamma(k)=\varphi^k\gamma(0)$ et $\rho(k)=\varphi^k$. $\blacksquare$
>
> Si $|\varphi|\ge1$, la somme diverge : la série **n'est pas stationnaire** (pour $\varphi=1$, c'est la marche aléatoire de 4.1.3 ; pour $|\varphi|>1$, elle explose).

> 💡 **Exemple à la main.** Avec $\varphi=0{,}5$ et $\sigma=1$ : $\gamma(0)=1/(1-0{,}25)=1{,}333$ ; $\rho(1)=0{,}5$, $\rho(2)=0{,}25$, $\rho(3)=0{,}125$. La mémoire est divisée par deux à chaque pas, et un choc d'il y a trois mois n'a plus que 12,5 % d'influence.

```python
ar, ma = [1, -0.5], [1]
print("autocorrélations théoriques de l'AR(1), phi = 0,5 :", arma_acf(ar, ma, 4).round(4))
x = ArmaProcess(ar, ma).generate_sample(200000, distrvs=np.random.default_rng(3).standard_normal)
print("variance : théorie", round(1 / (1 - 0.25), 3), "| simulation", round(x.var(), 3))
print("autocorrélations simulées (décalages 1 à 3) :", np.round([np.corrcoef(x[:-k], x[k:])[0, 1] for k in (1, 2, 3)], 3))
```
<!--sortie-->
```text
autocorrélations théoriques de l'AR(1), phi = 0,5 : [1.    0.5   0.25  0.125]
variance : théorie 1.333 | simulation 1.328
autocorrélations simulées (décalages 1 à 3) : [0.498 0.248 0.125]
```

Qu'est-ce que la condition $|\varphi|<1$ devient pour un AR($p$) ? On écrit l'équation avec l'**opérateur retard** $B$ (défini par $BY_t=Y_{t-1}$) : $\varphi(B)Y_t=\varepsilon_t$ avec $\varphi(z)=1-\varphi_1z-\dots-\varphi_pz^p$. La série est stationnaire si et seulement si **toutes les racines du polynôme $\varphi(z)$ sont en dehors du cercle unité** ($|z|>1$). Pour l'AR(1), l'unique racine est $z=1/\varphi$, et $|1/\varphi|>1\iff|\varphi|<1$. On retrouve la condition. Vérifions pour deux AR(2) :

```python
for nom, (phi1, phi2) in {"phi = (0,5 ; 0,3)": (0.5, 0.3), "phi = (0,5 ; 0,6)": (0.5, 0.6)}.items():
    racines = np.roots([-phi2, -phi1, 1])                   # polynôme 1 - phi1 z - phi2 z^2
    verdict = "stationnaire" if np.all(np.abs(racines) > 1) else "NON stationnaire"
    print(f"AR(2) {nom} : modules des racines = {np.abs(racines).round(3)}  ->  {verdict}")
```
<!--sortie-->
```text
AR(2) phi = (0,5 ; 0,3) : modules des racines = [2.84  1.174]  ->  stationnaire
AR(2) phi = (0,5 ; 0,6) : modules des racines = [1.773 0.94 ]  ->  NON stationnaire
```

Le second modèle a une racine de module $0{,}94<1$ : sa trajectoire diverge, même si chaque coefficient « a l'air raisonnable ».

#### Le MA(1) : autocorrélation et inversibilité

> 📐 **Proposition.** Pour $Y_t=\varepsilon_t+\theta\varepsilon_{t-1}$ : $\gamma(0)=\sigma^2(1+\theta^2)$, $\gamma(1)=\theta\sigma^2$, $\gamma(k)=0$ pour $k\ge2$. Donc $\rho(1)=\dfrac{\theta}{1+\theta^2}$ et $\rho(k)=0$ au-delà. Un MA est toujours stationnaire.
>
> **Démonstration.** $\operatorname{Var}(Y_t)=\sigma^2+\theta^2\sigma^2$. Et $\operatorname{Cov}(Y_t,Y_{t-1})=\operatorname{Cov}(\varepsilon_t+\theta\varepsilon_{t-1},\varepsilon_{t-1}+\theta\varepsilon_{t-2})=\theta\sigma^2$ (seul le terme $\theta\varepsilon_{t-1}\cdot\varepsilon_{t-1}$ survit). $\blacksquare$

Une subtilité qui surprend : **deux valeurs de $\theta$ donnent exactement la même autocorrélation**, car $\theta/(1+\theta^2)$ est inchangé si l'on remplace $\theta$ par $1/\theta$. Pour $\theta=0{,}5$ comme pour $\theta=2$, on a $\rho(1)=0{,}4$ :

```python
for th in (0.5, 2.0):
    print(f"theta = {th} : rho(1) = {arma_acf([1], [1, th], 3)[1]:.3f}  (formule : {th / (1 + th ** 2):.3f})")
```
<!--sortie-->
```text
theta = 0.5 : rho(1) = 0.400  (formule : 0.400)
theta = 2.0 : rho(1) = 0.400  (formule : 0.400)
```

Les données ne permettent donc pas de distinguer les deux. Par convention, on retient celui qui est **inversible** : $|\theta|<1$. Pourquoi ? Un MA(1) inversible peut se réécrire $\varepsilon_t=\sum_{j\ge0}(-\theta)^jY_{t-j}$ : on peut **reconstituer les chocs passés à partir des observations**, ce qui est indispensable pour estimer et prévoir. Si $|\theta|>1$, cette somme diverge. La condition est la même que pour l'AR, côté MA : les racines de $\theta(z)=1+\theta_1z+\dots$ doivent être hors du cercle unité.

### 4.2.3 ARMA, ARIMA et SARIMA

On assemble les briques. Avec l'opérateur retard $B$ :

- **ARMA($p,q$)** : $\varphi(B)\,Y_t=\theta(B)\,\varepsilon_t$.
- **ARIMA($p,d,q$)** : on applique d'abord $d$ différenciations : $\varphi(B)(1-B)^d\,Y_t=\theta(B)\,\varepsilon_t$. Le « I » signifie que $Y$ doit être *intégrée* $d$ fois pour revenir de la série différenciée à $Y$.
- **SARIMA($p,d,q)(P,D,Q)_s$** : on ajoute des briques et des différences **saisonnières**, de période $s$ ($s=12$ pour des données mensuelles) :
$$\varphi(B)\,\Phi(B^s)\,(1-B)^d(1-B^s)^D\,Y_t=\theta(B)\,\Theta(B^s)\,\varepsilon_t.$$

> 📐 **Le « modèle de la compagnie aérienne ».** Le SARIMA$(0,1,1)(0,1,1)_{12}$, popularisé par Box et Jenkins sur les passagers aériens, s'écrit $(1-B)(1-B^{12})Y_t=(1+\theta B)(1+\Theta B^{12})\varepsilon_t$. En développant, $Y_t-Y_{t-1}-Y_{t-12}+Y_{t-13}=\varepsilon_t+\theta\varepsilon_{t-1}+\Theta\varepsilon_{t-12}+\theta\Theta\varepsilon_{t-13}$. Le membre de gauche compare le mois courant au mois précédent, **et** compare ce changement au changement observé un an plus tôt. Avec deux paramètres seulement, ce modèle décrit une tendance, une saison qui évolue lentement, et du bruit : il est le point de départ naturel des séries mensuelles.

#### Comment estime-t-on ces modèles ?

Pour un AR(1), c'est une régression. Estimer $\varphi$ revient à régresser $y_t$ sur $y_{t-1}$ par moindres carrés (c'est la méthode des *moindres carrés conditionnels*), ce qui donne $\hat\varphi=\sum y_ty_{t-1}/\sum y_{t-1}^2$ pour une série centrée. Pour les modèles avec une partie MA, les chocs $\varepsilon_t$ ne sont pas observés, et l'on maximise la **vraisemblance gaussienne** : à chaque date, on calcule la prévision à un pas, et on suppose que l'erreur de prévision suit une loi normale ; la vraisemblance est le produit de ces densités. Le calcul récursif utilise le **filtre de Kalman**, que nous verrons en 4.5. Comparons les deux méthodes sur un AR(1) simulé :

```python
x = ArmaProcess([1, -0.7], [1]).generate_sample(300, distrvs=np.random.default_rng(21).standard_normal)
phi_mco = (x[1:] * x[:-1]).sum() / (x[:-1] ** 2).sum()          # moindres carrés (série centrée en théorie)
phi_mv = ARIMA(x, order=(1, 0, 0), trend="n").fit().params[0]    # maximum de vraisemblance
print("vraie valeur : 0.7 | moindres carrés :", round(phi_mco, 4), "| maximum de vraisemblance :", round(phi_mv, 4))
```
<!--sortie-->
```text
vraie valeur : 0.7 | moindres carrés : 0.7119 | maximum de vraisemblance : 0.7097
```

Les deux estimations sont très proches l'une de l'autre (écart d'environ 0,002) et de la vraie valeur. Qu'en est-il de leur **précision** ? Un résultat classique (Kendall, 1954) dit que l'estimateur des moindres carrés d'un AR(1) est **biaisé vers zéro** : $\mathbb E[\hat\varphi]\approx\varphi-\dfrac{1+3\varphi}{n}$. Vérifions avec 4 000 séries de 100 points et $\varphi=0{,}6$ :

```python
rng = np.random.default_rng(11)
estimations = []
for _ in range(4000):
    e = rng.normal(size=150)
    s = np.zeros(150)
    for t in range(1, 150):
        s[t] = 0.6 * s[t - 1] + e[t]
    s = s[50:]                                     # on jette 50 points de « mise en route »
    d = s - s.mean()
    estimations.append((d[1:] * d[:-1]).sum() / (d[:-1] ** 2).sum())
print("phi = 0,6, n = 100 : moyenne des estimations =", round(np.mean(estimations), 4),
      "| formule 0,6 - (1 + 3 x 0,6)/100 =", round(0.6 - (1 + 3 * 0.6) / 100, 4),
      "| écart-type =", round(np.std(estimations), 3))
```
<!--sortie-->
```text
phi = 0,6, n = 100 : moyenne des estimations = 0.571 | formule 0,6 - (1 + 3 x 0,6)/100 = 0.572 | écart-type = 0.084
```

Le biais est petit (environ $-0{,}03$ pour $n=100$), mais réel : avec peu de données, un AR estimé paraît **moins persistant** qu'il ne l'est. Étudions maintenant un ARMA(1,1) ($\varphi=0{,}6$, $\theta=0{,}4$) : une estimation sur 500 points, puis la distribution des estimations sur 200 séries de 200 points.

```python
x = ArmaProcess([1, -0.6], [1, 0.4]).generate_sample(500, distrvs=np.random.default_rng(12).standard_normal)
ajust = ARIMA(x, order=(1, 0, 1), trend="n").fit()
print(pd.DataFrame({"estimation": ajust.params, "erreur type": ajust.bse}, index=["phi", "theta", "sigma2"]).round(3))
print()
essais = []
for k in range(200):
    s = ArmaProcess([1, -0.6], [1, 0.4]).generate_sample(200, distrvs=np.random.default_rng(1000 + k).standard_normal)
    essais.append(ARIMA(s, order=(1, 0, 1), trend="n").fit().params[:2])
essais = np.array(essais)
print("200 séries de 200 points : moyenne des estimations (phi, theta) =", essais.mean(0).round(3),
      "| écart-type =", essais.std(0).round(3))
```
<!--sortie-->
```text
        estimation  erreur type
phi          0.582        0.044
theta        0.447        0.053
sigma2       0.951        0.062

200 séries de 200 points : moyenne des estimations (phi, theta) = [0.591 0.408] | écart-type = [0.076 0.08 ]
```

Sur une seule série de 500 points, les estimations sont proches des vraies valeurs (0,6 et 0,4), à l'intérieur de leurs marges d'erreur. Sur 200 séries de 200 points, la moyenne est proche de la vérité, mais la **dispersion** est importante (de l'ordre de 0,08 pour chaque paramètre) : estimer les deux paramètres d'un ARMA est nettement plus incertain qu'estimer un AR seul, parce que $\varphi$ et $\theta$ jouent des rôles voisins.

> ⚠️ **Un piège classique : la redondance.** Un ARMA(1,1) avec $\varphi=\theta'$ (où le MA est « l'opposé » de l'AR) se simplifie : $(1-\varphi B)Y_t=(1-\varphi B)\varepsilon_t$ donne $Y_t=\varepsilon_t$. Quand les deux racines sont presque égales, les paramètres ne sont plus identifiables. Si votre modèle estime $\varphi\approx0{,}9$ et $\theta\approx-0{,}9$, il est probablement trop gros : **simplifiez**.

### 4.2.4 La méthode de Box-Jenkins appliquée aux ventes de Dar Jasmin

Box et Jenkins ont proposé un cycle en quatre temps : **(1) identifier** la structure à partir de l'ACF et de la PACF, **(2) estimer** les paramètres, **(3) diagnostiquer** les résidus, et, si tout est correct, **(4) prévoir**. Appliquons-le à notre série d'apprentissage (96 mois, en logarithme).

**Étape 1 : stationnariser.** D'après 4.1.6, la série a une tendance et une saison. Les deux différences ($d=1$ et $D=1$, $s=12$) font disparaître la tendance et la saison **stochastiques**. Regardons ce qui reste :

```python
v = pd.read_csv("donnees/ventes_mensuelles.csv", parse_dates=["mois"]).set_index("mois")
v.index.freq = "MS"
y = np.log(v["ca"])
train, test = y[:"2023-12"], y["2024-01":]
X = v[["promo", "covid"]].astype(float)
Xtr = X[:"2023-12"]

def tracer_acf(ax, valeurs, n, titre, couleur=BLEU):
    k = np.arange(len(valeurs))
    ax.vlines(k, 0, valeurs, color=couleur, lw=2)
    ax.plot(k, valeurs, "o", color=couleur, ms=3.5)
    ax.axhline(0, color="#898781", lw=0.8)
    b = 1.96 / np.sqrt(n)
    ax.axhspan(-b, b, color=couleur, alpha=0.10, lw=0)
    ax.set_title(titre)
    ax.set_xlabel("décalage (mois)")
    ax.set_ylim(-1, 1)

w = train.diff().diff(12).dropna()
print("série différenciée (1 et 12) :", len(w), "observations ; bande de confiance +/-", round(1.96 / np.sqrt(len(w)), 3))
print("ACF  décalages 1 à 14 :", acf(w, nlags=14, fft=False)[1:].round(2))
print("PACF décalages 1 à 14 :", pacf(w, nlags=14, method="ols")[1:].round(2))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.4))
tracer_acf(ax1, acf(w, nlags=24, fft=False), len(w), "ACF de la série différenciée (1 et 12)")
tracer_acf(ax2, pacf(w, nlags=24, method="ols"), len(w), "PACF de la série différenciée (1 et 12)", ORANGE)
plt.tight_layout()
plt.savefig("figures/ch04-acf-diff.png", bbox_inches="tight")
```
<!--sortie-->
```text
série différenciée (1 et 12) : 83 observations ; bande de confiance +/- 0.215
ACF  décalages 1 à 14 : [-0.01 -0.12  0.   -0.23 -0.17 -0.08  0.15  0.02  0.04  0.14 -0.03 -0.43
 -0.02 -0.01]
PACF décalages 1 à 14 : [-0.01 -0.12  0.   -0.25 -0.19 -0.18  0.09 -0.08 -0.02  0.06  0.01 -0.5
 -0.02 -0.14]
```

![ACF et PACF de la série différenciée (différence première et différence saisonnière) : une barre négative nette au décalage 12 dans les deux graphiques ; les autres barres restent dans la bande ou l'effleurent.](figures/ch04-acf-diff.png)

**Lecture.** La série différenciée n'a plus de mémoire à long terme. Il reste une **seule structure nette** : une forte barre négative au décalage 12 dans l'ACF (environ $-0{,}43$) et dans la PACF (environ $-0{,}50$). Selon le tableau de 4.2.1, une ACF qui s'arrête au décalage 12 (un seul pic saisonnier) évoque un **MA saisonnier d'ordre 1** ($Q=1$). Aux décalages courts (1 à 3), rien ne dépasse la bande ; le décalage 4 l'effleure à peine (une barre sur quatorze : à ne pas sur-interpréter). La partie non saisonnière est donc modeste, peut-être nulle. On part donc du modèle de la compagnie aérienne, SARIMA$(0,1,1)(0,1,1)_{12}$, et de ses voisins.

**Étape 2 : estimer, avec des variables explicatives.** Nous savons qu'il y a eu un accident (COVID) et des promotions. Nous les ajoutons comme **variables explicatives** (*exogènes*) : le modèle devient une régression dont les erreurs suivent un SARIMA. (Nous détaillons cette idée en 4.2.5.) Ajustons une petite grille de modèles avec $d=1$, $D=1$, $p,q\in\{0,1,2\}$ et $Q\in\{0,1\}$, et comparons-les par **AIC** et **BIC** (chapitre 1, section 1.4 : ces critères mesurent l'ajustement en pénalisant la complexité ; plus petit = meilleur).

```python
import itertools

lignes = []
for p, q, Q in itertools.product((0, 1, 2), (0, 1, 2), (0, 1)):
    m = SARIMAX(train, exog=Xtr, order=(p, 1, q), seasonal_order=(0, 1, Q, 12)).fit(disp=False, maxiter=200)
    lignes.append({"p": p, "q": q, "Q": Q, "AIC": m.aic, "BIC": m.bic, "convergé": m.mle_retvals["converged"]})
grille = pd.DataFrame(lignes).sort_values("AIC").reset_index(drop=True)
print("les 8 meilleurs modèles par AIC (d = 1, D = 1, s = 12) :")
print(grille.head(8).round(1).to_string())
print()
print("tous convergés :", bool(grille["convergé"].all()), "| meilleur par BIC : (p, q, Q) =", tuple(grille.sort_values("BIC").iloc[0][["p", "q", "Q"]].astype(int)))
```
<!--sortie-->
```text
les 8 meilleurs modèles par AIC (d = 1, D = 1, s = 12) :
   p  q  Q    AIC    BIC  convergé
0  1  1  1 -176.7 -162.2      True
1  2  1  1 -175.5 -158.6      True
2  1  2  1 -175.5 -158.6      True
3  0  2  1 -173.3 -158.8      True
4  2  2  1 -172.9 -153.5      True
5  2  0  1 -166.4 -151.9      True
6  0  1  1 -165.9 -153.8      True
7  0  0  1 -164.7 -155.1      True

tous convergés : True | meilleur par BIC : (p, q, Q) = (1, 1, 1)
```

Le modèle SARIMAX$(1,1,1)(0,1,1)_{12}$ arrive en tête à la fois par l'AIC et par le BIC. Voici ses coefficients :

```python
mod_A = SARIMAX(train, exog=Xtr, order=(1, 1, 1), seasonal_order=(0, 1, 1, 12)).fit(disp=False)
print(mod_A.summary().tables[1])
```
<!--sortie-->
```text
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
promo          0.1061      0.022      4.887      0.000       0.064       0.149
covid         -0.5371      0.037    -14.464      0.000      -0.610      -0.464
ar.L1          0.5583      0.115      4.870      0.000       0.334       0.783
ma.L1         -0.9919      0.331     -3.001      0.003      -1.640      -0.344
ma.S.L12      -0.8889      0.262     -3.389      0.001      -1.403      -0.375
sigma2         0.0047      0.002      2.383      0.017       0.001       0.009
==============================================================================
```

> ⚠️ **Les deux coefficients MA sont proches de $-1$ : un signal d'alerte.** `ma.L1` vaut environ $-0{,}99$ et `ma.S.L12` environ $-0{,}89$, avec de très grandes incertitudes (erreurs types de l'ordre de $0{,}3$). Rappelez-vous la sur-différenciation de 4.1.6 : différencier une série qui n'en avait pas besoin crée un MA dont le coefficient est $-1$. Un MA non saisonnier proche de $-1$ suggère que la **différence première** est de trop (la tendance serait **déterministe**, une droite, et non un cumul de chocs) ; un MA **saisonnier** proche de $-1$ suggère que la **différence saisonnière** l'est aussi (la saison serait **déterministe** : le même profil chaque année, fixé une fois pour toutes, et non un profil qui évolue). Le modèle a trouvé le meilleur ajustement *parmi les modèles différenciés*, mais ses propres coefficients nous disent qu'il compense une différenciation excessive. Nous allons mettre cette hypothèse à l'épreuve en 4.2.7.

### 4.2.5 Variables explicatives : la régression à erreurs ARMA

Le modèle que vient d'ajuster `SARIMAX` est une **régression à erreurs ARIMA** :

$$\log y_t=\beta_1\,\text{promo}_t+\beta_2\,\text{covid}_t+\eta_t,\qquad \eta_t\sim\text{SARIMA}(1,1,1)(0,1,1)_{12}.$$

Les variables explicatives interviennent **en niveau** (pas différenciées) et l'ARIMA décrit ce qui reste. C'est la bonne façon de combiner une régression (chapitre 1) et de la mémoire temporelle : si l'on ignorait la mémoire des erreurs, les erreurs types de la régression seraient fausses (le volume I, section 2.4, suppose l'indépendance).

Les coefficients se lisent comme des pourcentages, puisque la variable dépendante est un logarithme : un coefficient $\beta$ correspond à un facteur $e^\beta$, soit une variation de $100\,(e^\beta-1)\,\%$ :

```python
for nom in ("promo", "covid"):
    b = mod_A.params[nom]
    lo, hi = mod_A.conf_int().loc[nom]
    print(f"{nom:6s} : coefficient = {b:+.3f}  ->  effet = {100 * (np.exp(b) - 1):+.1f} %   (IC 95 % : {100 * (np.exp(lo) - 1):+.1f} % à {100 * (np.exp(hi) - 1):+.1f} %)")
```
<!--sortie-->
```text
promo  : coefficient = +0.106  ->  effet = +11.2 %   (IC 95 % : +6.6 % à +16.0 %)
covid  : coefficient = -0.537  ->  effet = -41.6 %   (IC 95 % : -45.7 % à -37.1 %)
```

Une promotion est associée à des ventes environ 11 % plus élevées le mois où elle a lieu, et les quatre mois de COVID à des ventes environ 42 % plus basses, toutes choses égales par ailleurs. Sans ces deux variables, le modèle aurait dû « expliquer » le COVID par du bruit, ce qui aurait dégradé tous les paramètres. Mesurons-le :

```python
sans = SARIMAX(train, order=(1, 1, 1), seasonal_order=(0, 1, 1, 12)).fit(disp=False)
print("AIC sans variables explicatives :", round(sans.aic, 1), "| avec promo et COVID :", round(mod_A.aic, 1))
print("écart-type estimé des chocs (sigma) : sans =", round(np.sqrt(sans.params['sigma2']), 3), "| avec =", round(np.sqrt(mod_A.params['sigma2']), 3))
```
<!--sortie-->
```text
AIC sans variables explicatives : -98.1 | avec promo et COVID : -176.7
écart-type estimé des chocs (sigma) : sans = 0.107 | avec = 0.068
```

> 💡 **Les variables explicatives doivent être connues pour prévoir.** Pour prévoir 2026, il faudra fournir la valeur future de `promo` (les promotions sont décidées par Yasmine : on peut les supposer connues ou raisonner en scénarios) et de `covid` (nulle). Une variable explicative inconnue dans le futur est inutilisable telle quelle : il faudrait la prévoir elle-même.

### 4.2.6 Le diagnostic des résidus

Un modèle n'est pas fini quand il est ajusté : il faut vérifier qu'il a **tout expliqué**, c'est-à-dire que ses résidus ressemblent à un bruit blanc gaussien. On regarde quatre choses : les résidus dans le temps (pas de structure, variance stable), l'ACF des résidus (pas de barre hors bande), la normalité (histogramme et QQ-plot) et le test de Ljung-Box. Les premiers résidus d'un SARIMA avec différences (ici 13) n'ont pas de sens (ils servent à initialiser le calcul) : on les ignore.

```python
res = mod_A.resid.iloc[13:]                       # on ignore les 13 premiers (initialisation des différences)
sig = res.std()
fig, axes = plt.subplots(2, 2, figsize=(11, 6))
axes[0, 0].plot(res.index, res / sig, color=BLEU, lw=1.2)
axes[0, 0].axhline(0, color="#898781", lw=0.8)
axes[0, 0].set_title("Résidus standardisés")
axes[0, 1].hist(res / sig, bins=18, density=True, color=BLEU, alpha=0.7)
xs = np.linspace(-4, 4, 200)
axes[0, 1].plot(xs, stats.norm.pdf(xs), color=ORANGE, lw=2)
axes[0, 1].set_title("Histogramme et loi normale")
sm.qqplot(res / sig, line="45", ax=axes[1, 0], markerfacecolor=BLEU, markeredgecolor=BLEU, ms=4)
axes[1, 0].set_title("QQ-plot")
axes[1, 0].set_xlabel("quantiles théoriques")
axes[1, 0].set_ylabel("quantiles observés")
tracer_acf(axes[1, 1], acf(res, nlags=24, fft=False), len(res), "ACF des résidus", ORANGE)
plt.tight_layout()
plt.savefig("figures/ch04-diagnostics.png", bbox_inches="tight")

nb_param = 3                                     # phi, theta, Theta : les paramètres AR/MA estimés
lb = acorr_ljungbox(res, lags=[12, 24], model_df=nb_param)
print("Ljung-Box sur les résidus (degrés de liberté réduits de", nb_param, ") :")
print(lb.round(3).to_string())
print("Shapiro-Wilk (normalité) : p =", round(stats.shapiro(res).pvalue, 3))
print("plus grand résidu standardisé en valeur absolue :", round((res / sig).abs().max(), 2), "le", (res / sig).abs().idxmax().strftime("%Y-%m"))
```
<!--sortie-->
```text
Ljung-Box sur les résidus (degrés de liberté réduits de 3 ) :
    lb_stat  lb_pvalue
12    8.923      0.444
24   22.329      0.381
Shapiro-Wilk (normalité) : p = 0.334
plus grand résidu standardisé en valeur absolue : 2.37 le 2017-12
```

![Diagnostic des résidus du SARIMAX(1,1,1)(0,1,1)12 : résidus standardisés sans structure, histogramme proche de la loi normale, QQ-plot proche de la droite, ACF sans barre hors bande.](figures/ch04-diagnostics.png)

Les résidus ne montrent pas de structure : l'ACF reste dans la bande, les p-valeurs de Ljung-Box sont grandes (on ne rejette pas « bruit blanc »), la normalité n'est pas rejetée. Le modèle a donc **capté l'essentiel de la dynamique linéaire** de la série d'apprentissage.

> ⚠️ **Un bon diagnostic ne prouve pas un bon modèle.** Des résidus blancs montrent qu'il ne reste pas d'**autocorrélation exploitable**, pas que le modèle **prévoira bien** : un modèle trop flexible peut avoir des résidus parfaits sur l'apprentissage et prévoir mal (surajustement). Seule la prévision hors échantillon (4.3) le dira.

### 4.2.7 Deux visions du monde : saison stochastique ou déterministe ?

Nous avons soupçonné plusieurs fois que la tendance et la saison sont **déterministes** (4.1.6 : tests ambigus ; 4.2.4 : deux coefficients MA proches de $-1$). Construisons deux modèles alternatifs, qui **différencient moins** :

- **Modèle B** : SARIMAX$(1,0,0)(0,1,1)_{12}$ avec tendance linéaire (`trend="ct"`) : on garde la différence saisonnière mais on modélise la tendance par une droite.
- **Modèle C** : régression sur **tendance linéaire + 11 indicatrices de mois + promo + COVID**, avec des **erreurs AR(1)**. Ici, la saison est un profil fixe (11 coefficients) et aucune différenciation n'est appliquée.

```python
mois = pd.get_dummies(pd.Series(v.index.month, index=v.index).astype(str).str.zfill(2), prefix="m", drop_first=True, dtype=float)
XX = pd.concat([pd.Series(1.0, index=v.index, name="const"),
                pd.Series(np.arange(len(v), dtype=float), index=v.index, name="t"), mois, X], axis=1)

mod_B = SARIMAX(train, exog=Xtr, order=(1, 0, 0), seasonal_order=(0, 1, 1, 12), trend="ct").fit(disp=False, maxiter=300)
mod_C = ARIMA(train, exog=XX[:"2023-12"], order=(1, 0, 0), trend="n").fit()

tableau = pd.DataFrame({
    "modèle A : SARIMAX(1,1,1)(0,1,1)": [mod_A.params["promo"], mod_A.params["covid"]],
    "modèle B : (1,0,0)(0,1,1) + tendance": [mod_B.params["promo"], mod_B.params["covid"]],
    "modèle C : régression + AR(1)": [mod_C.params["promo"], mod_C.params["covid"]]}, index=["promo", "covid"])
print(tableau.round(3).T.to_string())
print()
print("modèle C : pente de la tendance =", round(mod_C.params["t"], 4), "par mois, soit", round(100 * (np.exp(12 * mod_C.params["t"]) - 1), 1), "% par an ;",
      "AR(1) : phi =", round(mod_C.params["ar.L1"], 3), "| sigma =", round(np.sqrt(mod_C.params["sigma2"]), 3))
print("AIC : A =", round(mod_A.aic, 1), "| B =", round(mod_B.aic, 1), "| C =", round(mod_C.aic, 1))
```
<!--sortie-->
```text
                                      promo  covid
modèle A : SARIMAX(1,1,1)(0,1,1)      0.106 -0.537
modèle B : (1,0,0)(0,1,1) + tendance  0.100 -0.506
modèle C : régression + AR(1)         0.106 -0.541

modèle C : pente de la tendance = 0.0077 par mois, soit 9.7 % par an ; AR(1) : phi = 0.539 | sigma = 0.06
AIC : A = -176.7 | B = -174.3 | C = -232.5
```

Les trois modèles s'accordent sur les effets de la promotion (coefficient d'environ 0,10 à 0,11, soit +10 à +11 %) et du COVID (coefficient d'environ −0,51 à −0,54, soit −40 à −42 %). Ils diffèrent sur la **dynamique**. Le modèle C décrit une croissance régulière de l'ordre de 10 % par an, un AR(1) modéré, et il obtient l'AIC le plus bas de loin. Attention : **cette comparaison d'AIC n'a pas de sens**.

> ⚠️ **On ne compare pas des AIC entre modèles de différenciations différentes.** L'AIC est calculé à partir de la vraisemblance des **données modélisées**. Le modèle A modélise une série différenciée deux fois, le modèle B une série différenciée une fois, le modèle C la série non différenciée : les vraisemblances portent sur des objets différents, et leurs valeurs ne sont pas comparables (même si le logiciel les affiche sans protester). L'AIC ne peut départager que des modèles de **même $d$ et même $D$** (comme dans la grille de 4.2.4). Pour comparer A, B et C, il n'y a **qu'un seul juge** légitime : leurs **prévisions** sur des données qu'ils n'ont pas vues. C'est l'objet de 4.3.

### 4.2.8 Le même travail en R : `auto.arima`

Les statisticiens utilisent aussi R, où le paquet `forecast` propose `auto.arima`, qui automatise la grille de 4.2.4 (et choisit même les différences par des tests de racine unitaire). Voici ce que donne la fonction sur la même série d'apprentissage, avec les mêmes variables explicatives :

```r
suppressPackageStartupMessages(library(forecast))
d <- read.csv("donnees/ventes_mensuelles.csv")
d <- d[1:96, ]                                       # les 96 mois d'apprentissage
y <- ts(log(d$ca), start = c(2016, 1), frequency = 12)
xreg <- as.matrix(d[, c("promo", "covid")])
modele <- auto.arima(y, xreg = xreg, seasonal = TRUE, ic = "aicc")
print(modele)
```
<!--sortie-->
```text
Series: y 
Regression with ARIMA(0,0,1)(0,1,1)[12] errors 

Coefficients:
         ma1     sma1   drift   promo    covid
      0.4942  -0.8836  0.0078  0.0976  -0.5425
s.e.  0.0798   0.2637  0.0004  0.0210   0.0459

sigma^2 = 0.005107:  log likelihood = 96.73
AIC=-181.47   AICc=-180.38   BIC=-166.88
```

R a retenu un **ARIMA$(0,0,1)(0,1,1)_{12}$ avec une dérive** (une tendance linéaire, `drift`) : pas de différence première, une différence saisonnière, un MA(1) de coefficient d'environ 0,49 et un MA saisonnier d'environ $-0{,}88$. Les effets estimés sont voisins des nôtres (promo : $0{,}098$ ; COVID : $-0{,}54$). Ce choix automatique, fondé sur des tests de racine unitaire pour $d$ et $D$, **va dans le même sens que nos soupçons** : la tendance se modélise bien par une dérive déterministe, sans différence première. Il diffère de la grille de 4.2.4, où nous avions *imposé* $d=1$ ; `auto.arima` utilise de plus l'AICc (une version de l'AIC corrigée pour les petits échantillons). Ce n'est pas une contradiction, mais un rappel : **la sélection automatique n'est pas une vérité**, seulement un point de départ à confronter au diagnostic et à la prévision.

> ✅ **À retenir.**
> - **AR** : la valeur d'aujourd'hui est un écho de ses propres valeurs passées ; **MA** : elle garde la trace des chocs récents. Signatures : un AR($p$) a une PACF qui s'arrête à $p$, un MA($q$) une ACF qui s'arrête à $q$.
> - **AR(1) stationnaire $\iff|\varphi|<1$**, avec $\gamma(0)=\sigma^2/(1-\varphi^2)$ et $\rho(k)=\varphi^k$. **MA inversible $\iff|\theta|<1$** ; deux valeurs $\theta$ et $1/\theta$ ont la même ACF. Pour un AR($p$) ou MA($q$), les racines du polynôme doivent être hors du cercle unité.
> - **SARIMA$(p,d,q)(P,D,Q)_s$** : $\varphi(B)\Phi(B^s)(1-B)^d(1-B^s)^DY_t=\theta(B)\Theta(B^s)\varepsilon_t$. L'estimation se fait par maximum de vraisemblance ; l'estimateur d'un AR(1) est biaisé vers zéro d'environ $(1+3\varphi)/n$.
> - **Box-Jenkins** : stationnariser, identifier avec ACF/PACF, estimer plusieurs candidats, comparer par AIC/BIC (**à même $d$ et $D$ seulement**), diagnostiquer les résidus (Ljung-Box avec degrés de liberté réduits du nombre de paramètres AR et MA).
> - Une **régression à erreurs ARIMA** (`SARIMAX` avec variables explicatives) combine les effets de variables connues et la mémoire des erreurs ; les coefficients en log se lisent en pourcentages.
> - Un coefficient MA proche de $-1$ signale souvent une **sur-différenciation** : ici, une saison qui pourrait être déterministe.
> - Des résidus blancs ne garantissent pas de bonnes prévisions. **Le juge de paix est la prévision hors échantillon** (4.3).


## 4.3 Prévision et évaluation des prévisions

> 💡 **Intuition.** Prévoir, ce n'est pas deviner un nombre : c'est annoncer **un nombre et son incertitude**. « Les ventes de décembre seront de 3 300 DT, avec 95 % de chances de tomber entre 2 800 et 3 900 » est une prévision utile ; « 3 300 » tout court n'en est pas une. Et un modèle ne se juge pas à la beauté de son ajustement passé, mais à la qualité des prévisions qu'il fait sur des données qu'il **n'a pas vues**.

Dans cette section, nous faisons trois choses : comprendre comment un modèle ARIMA prévoit et d'où viennent ses intervalles (4.3.1 et 4.3.2) ; mettre en place une **évaluation honnête** (4.3.3 à 4.3.6) ; puis prévoir 2026 pour Yasmine (4.3.7) et **lever le voile** sur la fabrication des données (4.3.8).

### 4.3.1 Comment un modèle prévoit : l'exemple de l'AR(1)

La meilleure prévision ponctuelle de $Y_{T+h}$ à partir de ce qu'on sait à la date $T$ est l'**espérance conditionnelle** $\hat y_{T+h}=\mathbb E[Y_{T+h}\mid Y_T,Y_{T-1},\dots]$ : c'est elle qui minimise l'erreur quadratique moyenne (chapitre 1, section 1.1, avec le passé comme variables explicatives). Pour un AR(1) de moyenne $\mu$, on peut tout calculer.

> 📐 **Prévision d'un AR(1).** Soit $Y_t-\mu=\varphi(Y_{t-1}-\mu)+\varepsilon_t$ avec $|\varphi|<1$. En remplaçant récursivement, $Y_{T+h}-\mu=\varphi^{h}(Y_T-\mu)+\sum_{j=0}^{h-1}\varphi^{j}\varepsilon_{T+h-j}$. Les chocs futurs $\varepsilon_{T+1},\dots,\varepsilon_{T+h}$ sont d'espérance nulle et indépendants du passé, donc
> $$\hat y_{T+h}=\mu+\varphi^{h}(Y_T-\mu),\qquad \operatorname{Var}(Y_{T+h}-\hat y_{T+h})=\sigma^2\sum_{j=0}^{h-1}\varphi^{2j}=\sigma^2\,\frac{1-\varphi^{2h}}{1-\varphi^2}.$$
> La prévision **revient vers la moyenne** à vitesse géométrique, et l'incertitude **croît** de $\sigma^2$ (à un pas) vers la variance de la série elle-même, $\sigma^2/(1-\varphi^2)$. $\blacksquare$

> 💡 **Exemple à la main.** Avec $\varphi=0{,}6$, $\mu=0$, $\sigma=1$ et $Y_T=2$ : $\hat y_{T+1}=0{,}6\times2=1{,}2$ ; $\hat y_{T+2}=0{,}6\times1{,}2=0{,}72$ ; $\hat y_{T+3}=0{,}432$. Les demi-largeurs des intervalles à 95 % sont $1{,}96\sqrt{1}=1{,}96$ ; $1{,}96\sqrt{1+0{,}36}\approx2{,}286$ ; $1{,}96\sqrt{1+0{,}36+0{,}1296}\approx2{,}392$, et tendent vers $1{,}96/\sqrt{1-0{,}36}=2{,}45$. L'avenir lointain n'est pas plus prévisible que « la valeur moyenne, avec la dispersion habituelle ».

```python
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
phi, yT = 0.6, 2.0
# un AR(1) dont on FIXE les paramètres (phi = 0,6 ; sigma^2 = 1), pour que statsmodels applique exactement la formule
fixe = ARIMA(np.r_[np.zeros(50), yT], order=(1, 0, 0), trend="n").filter([phi, 1.0])
prev = fixe.get_forecast(3)
print("prévisions statsmodels :", prev.predicted_mean.round(3))
print("demi-largeurs (statsmodels) :", ((prev.conf_int()[:, 1] - prev.conf_int()[:, 0]) / 2).round(3))
print("prévisions (formule)        :", np.round([phi ** h * yT for h in (1, 2, 3)], 3))
print("demi-largeurs (formule)     :", np.round([1.96 * np.sqrt(sum(phi ** (2 * j) for j in range(h))) for h in (1, 2, 3)], 3))
print("limite 1,96 / racine(1 - phi^2) :", round(1.96 / np.sqrt(1 - phi ** 2), 3))
```
<!--sortie-->
```text
prévisions statsmodels : [1.2   0.72  0.432]
demi-largeurs (statsmodels) : [1.96  2.286 2.392]
prévisions (formule)        : [1.2   0.72  0.432]
demi-largeurs (formule)     : [1.96  2.286 2.392]
limite 1,96 / racine(1 - phi^2) : 2.45
```

Pour un MA(1), la prévision à un pas utilise le dernier choc, et **au-delà d'un pas la prévision est la moyenne** (le choc n'a plus d'effet). Et pour une série **différenciée** ($d=1$), la prévision n'est pas stationnaire : c'est la dernière valeur (plus une éventuelle dérive), et l'incertitude ne se stabilise **jamais**. Comparons la demi-largeur d'un intervalle à 95 % pour une marche aléatoire ($\sigma=1$) et pour l'AR(1) précédent :

```python
print(" horizon   marche aléatoire   AR(1), phi = 0,6")
for h in (1, 3, 12, 60):
    print(f"{h:8d}   {1.96 * np.sqrt(h):16.2f}   {1.96 * np.sqrt((1 - phi ** (2 * h)) / (1 - phi ** 2)):16.2f}")
```
<!--sortie-->
```text
 horizon   marche aléatoire   AR(1), phi = 0,6
       1               1.96               1.96
       3               3.39               2.39
      12               6.79               2.45
      60              15.18               2.45
```

> ⚠️ **Conséquence pratique.** Un modèle avec une différence (première ou saisonnière) a des intervalles de prévision qui **s'élargissent sans limite** quand l'horizon grandit ; un modèle stationnaire autour d'une tendance et d'une saison **déterministes** a des intervalles qui se stabilisent. Parmi nos trois modèles de 4.2, A (deux différences) et B (une différence saisonnière) sont du premier type, et C (aucune différence) du second. Choisir entre les deux, c'est choisir ce que l'on croit de l'avenir lointain : des chocs qui laissent une trace **permanente** ou qui s'effacent.

### 4.3.2 Prévoir en logarithme, annoncer en dinars

Nos modèles prévoient $\log(\text{ca})$. Pour annoncer des dinars, on revient par l'exponentielle. Deux précautions :

- **Les intervalles** se transforment sans difficulté : si $[L,U]$ est un intervalle à 95 % pour $\log y$, alors $[e^L,e^U]$ en est un pour $y$ (l'exponentielle est croissante).
- **La prévision ponctuelle** $e^{\hat y}$ est la **médiane** de la loi de $Y$, pas sa moyenne : si $\log Y\sim\mathcal N(m,s^2)$, alors $\mathbb E[Y]=e^{m+s^2/2}$. Pour des erreurs de l'ordre de 0,07 en log, le facteur $e^{s^2/2}$ vaut environ 1,0025 : négligeable ici. Il ne le serait pas pour une série plus volatile.

Voyons ce que donnent nos trois modèles (A, B, C de 4.2) sur les 24 mois mis de côté. Rappelons les objets : `train` (96 mois), `test` (24 mois), `mod_A`, `mod_B`, `mod_C` ajustés **sur `train` seulement**.

```python
v = pd.read_csv("donnees/ventes_mensuelles.csv", parse_dates=["mois"]).set_index("mois")
v.index.freq = "MS"
y = np.log(v["ca"])
train, test = y[:"2023-12"], y["2024-01":]
X = v[["promo", "covid"]].astype(float)
Xte = X["2024-01":]                                   # les promotions de 2024-2025 sont supposées connues à l'avance
mois_ind = pd.get_dummies(pd.Series(v.index.month, index=v.index).astype(str).str.zfill(2), prefix="m", drop_first=True, dtype=float)
XX = pd.concat([pd.Series(1.0, index=v.index, name="const"),
                pd.Series(np.arange(len(v), dtype=float), index=v.index, name="t"), mois_ind, X], axis=1)

prev_A = mod_A.get_forecast(24, exog=Xte)
prev_B = mod_B.get_forecast(24, exog=Xte)
prev_C = mod_C.get_forecast(24, exog=XX["2024-01":])
previsions = {"A : SARIMAX(1,1,1)(0,1,1)": prev_A, "B : (1,0,0)(0,1,1) + tendance": prev_B, "C : régression + AR(1)": prev_C}

print("facteur de correction moyenne/médiane exp(s^2/2) pour C, 1er et 24e mois :",
      np.round(np.exp(0.5 * prev_C.se_mean.values[[0, 23]] ** 2), 4))
couverture = {}
for nom, p in previsions.items():
    ic = np.asarray(p.conf_int(alpha=0.05))
    dedans = (test.values >= ic[:, 0]) & (test.values <= ic[:, 1])
    couverture[nom] = dedans.sum()
    print(f"{nom:34s} : {dedans.sum():2d} mois sur 24 dans l'intervalle à 95 %   (rapport moyen borne haute / borne basse : x{np.exp(ic[:, 1] - ic[:, 0]).mean():.2f})")
```
<!--sortie-->
```text
facteur de correction moyenne/médiane exp(s^2/2) pour C, 1er et 24e mois : [1.0018 1.0026]
A : SARIMAX(1,1,1)(0,1,1)          : 22 mois sur 24 dans l'intervalle à 95 %   (rapport moyen borne haute / borne basse : x1.41)
B : (1,0,0)(0,1,1) + tendance      : 24 mois sur 24 dans l'intervalle à 95 %   (rapport moyen borne haute / borne basse : x1.43)
C : régression + AR(1)             : 21 mois sur 24 dans l'intervalle à 95 %   (rapport moyen borne haute / borne basse : x1.32)
```

> 📐 **La couverture.** Un intervalle à 95 % **bien calibré** devrait contenir la vraie valeur 95 % du temps. Sur 24 mois, on attend 22 à 23 mois dedans. Observer 21, 22 ou 24 n'est pas une preuve de mauvaise calibration : avec 24 points **corrélés** entre eux, l'incertitude sur la couverture est très grande. Remarquez aussi que les intervalles des modèles qui différencient (A et B, rapports moyens de 1,41 et 1,43) sont plus larges que celui de C (1,32) : conséquence de la remarque de 4.3.1. À retenir : la couverture se vérifie sur de **longues** périodes ou sur **beaucoup** de séries.

### 4.3.3 Le découpage temporel : ne jamais mélanger le passé et l'avenir

En régression ordinaire (chapitre 1), on peut tirer au hasard 20 % des observations pour les tenir à l'écart et évaluer le modèle dessus : les observations sont indépendantes. En série temporelle, **c'est une faute** : un mois « tenu à l'écart » a ses voisins dans l'échantillon d'apprentissage, et le modèle peut les interpoler. On estime alors la capacité du modèle à **combler un trou**, pas à **prévoir**.

Voyons cela sur un cas où le piège est spectaculaire. Ajustons des régressions où la tendance est un **polynôme** de degré $1$, $3$, $6$ ou $10$ (plus saison et COVID) sur nos 96 mois d'apprentissage, et évaluons-les de deux façons : **(a)** en tenant à l'écart 24 mois tirés au hasard ; **(b)** en apprenant sur les 72 premiers mois et en prévoyant les 24 suivants (donc toujours *dans* la période d'apprentissage : nous ne touchons pas aux données de test).

```python
tt = np.arange(96) / 95                                        # le temps ramené à [0, 1]
M = mois_ind.values[:96]
covid96 = X["covid"].values[:96]

def dessin(idx, deg):
    return np.column_stack([tt[idx] ** d for d in range(deg + 1)] + [M[idx], covid96[idx]])

def eqm(a, b):
    return np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2))

rng = np.random.default_rng(0)
lignes = []
for deg in (1, 3, 6, 10):
    hasard = []
    for _ in range(50):
        test_i = rng.choice(96, 24, replace=False)
        app_i = np.setdiff1d(np.arange(96), test_i)
        b = np.linalg.lstsq(dessin(app_i, deg), train.values[app_i], rcond=None)[0]
        hasard.append(eqm(train.values[test_i], dessin(test_i, deg) @ b))
    app_i, test_i = np.arange(72), np.arange(72, 96)
    b = np.linalg.lstsq(dessin(app_i, deg), train.values[app_i], rcond=None)[0]
    lignes.append({"degré du polynôme": deg, "RMSE (log), 24 mois au hasard": np.mean(hasard),
                   "RMSE (log), 24 derniers mois": eqm(train.values[test_i], dessin(test_i, deg) @ b)})
print(pd.DataFrame(lignes).round(3).to_string(index=False))
```
<!--sortie-->
```text
 degré du polynôme  RMSE (log), 24 mois au hasard  RMSE (log), 24 derniers mois
                 1                          0.093                         0.102
                 3                          0.098                         0.123
                 6                          0.097                         4.442
                10                          0.103                       157.857
```

Avec l'évaluation au hasard, tous les polynômes se valent (erreur de l'ordre de 0,1, sans lien avec le degré) : l'évaluation ne détecte rien. Avec l'évaluation chronologique, la vérité éclate : le polynôme de degré 6 **explose** hors de la zone d'apprentissage (une erreur de 4,4 en logarithme, soit des prévisions fausses d'un facteur de l'ordre de $e^{4{,}4}\approx80$), et celui de degré 10 est absurde (erreur de près de 158). Un modèle flexible ajuste parfaitement le passé et **extrapole n'importe comment**.

> ⚠️ **La règle d'or.** En série temporelle, les données d'évaluation doivent toujours être **postérieures** aux données d'apprentissage. Même règle pour la validation croisée (4.3.6 : on la fait à origine glissante, jamais au hasard) et pour tout prétraitement (une moyenne ou une normalisation doivent être calculées sur l'apprentissage seul).

### 4.3.4 Des références simples, puis des mesures d'erreur

Avant de juger un modèle sophistiqué, on le compare à une **référence simple**. Un modèle qui ne bat pas la référence ne mérite pas sa complexité. Pour une série saisonnière, deux références naturelles :

- le **naïf saisonnier** : prévoir pour un mois la valeur du **même mois l'an dernier** ;
- le **naïf saisonnier avec dérive** : idem, plus la croissance annuelle moyenne observée sur tout l'apprentissage (en logarithme : la moyenne de $y_t-y_{t-12}$).

Pour mesurer l'erreur, quatre indicateurs usuels, avec $e_t=y_t-\hat y_t$ l'erreur de prévision sur $n$ points :

| Mesure | Définition | Remarque |
|---|---|---|
| **MAE** | $\frac1n\sum\lvert e_t\rvert$ | dans l'unité de la série ; robuste |
| **RMSE** | $\sqrt{\frac1n\sum e_t^2}$ | pénalise fortement les grosses erreurs |
| **MAPE** | $\frac{100}{n}\sum\lvert e_t\rvert/\lvert y_t\rvert$ | en %, mais **indéfini** si $y_t=0$ et asymétrique (une surestimation coûte plus qu'une sous-estimation de même taille) |
| **MASE** | MAE / (MAE *dans l'échantillon* du naïf saisonnier) | **sans unité** : $<1$ signifie « mieux que le naïf saisonnier » ; utilisable pour comparer des séries |

> 💡 **Exemple à la main.** Valeurs réelles $100,120,90,110$ ; prévisions $110,115,100,105$. Erreurs : $-10,\,5,\,-10,\,5$. MAE $=(10+5+10+5)/4=7{,}5$. RMSE $=\sqrt{(100+25+100+25)/4}=\sqrt{62{,}5}\approx7{,}91$. MAPE $=\frac{100}{4}\left(\frac{10}{100}+\frac5{120}+\frac{10}{90}+\frac5{110}\right)\approx7{,}46\,\%$. Si le naïf saisonnier avait une MAE de $5$ sur l'apprentissage, la MASE vaudrait $7{,}5/5=1{,}5$ : **pire** que la référence.

```python
def mesures(reel, prevu, ref_apprentissage=None):
    e = np.asarray(reel, float) - np.asarray(prevu, float)
    sortie = {"MAE": np.mean(np.abs(e)), "RMSE": np.sqrt(np.mean(e ** 2)), "MAPE": 100 * np.mean(np.abs(e) / np.abs(reel))}
    if ref_apprentissage is not None:
        sortie["MASE"] = sortie["MAE"] / ref_apprentissage
    return sortie

print({k: round(float(x), 3) for k, x in mesures([100, 120, 90, 110], [110, 115, 100, 105], 5).items()})
```
<!--sortie-->
```text
{'MAE': 7.5, 'RMSE': 7.906, 'MAPE': 7.456, 'MASE': 1.5}
```

Appliquons-les à nos cinq prévisions des 24 mois de test, **en dinars** (on revient de l'échelle logarithmique par l'exponentielle) :

```python
ca_train = np.exp(train)
echelle = np.mean(np.abs(ca_train.values[12:] - ca_train.values[:-12]))     # MAE du naïf saisonnier dans l'échantillon
g = (train - train.shift(12)).mean()                                        # croissance annuelle moyenne (en log)
print("croissance annuelle moyenne en apprentissage :", round(g, 3), "soit", round(100 * (np.exp(g) - 1), 1), "% par an")

naif = pd.Series(train.iloc[-12:].tolist() * 2, index=test.index)           # même mois de l'an dernier (puis de l'année précédente)
naif_derive = pd.Series([train.iloc[-12 + (h % 12)] + g * (1 + h // 12) for h in range(24)], index=test.index)
prev_log = {"naïf saisonnier": naif, "naïf saisonnier + dérive": naif_derive}
for nom, p in previsions.items():
    prev_log[nom] = pd.Series(p.predicted_mean.values, index=test.index)

lignes = []
for nom, f in prev_log.items():
    m = mesures(np.exp(test), np.exp(f), echelle)
    m["biais (log)"] = float(np.mean(test - f))
    m["RMSE (log)"] = float(np.sqrt(np.mean((test - f) ** 2)))
    lignes.append(pd.Series(m, name=nom))
tab_test = pd.DataFrame(lignes).sort_values("RMSE")
print(tab_test.round(3).to_string())
```
<!--sortie-->
```text
croissance annuelle moyenne en apprentissage : 0.086 soit 9.0 % par an
                                   MAE     RMSE    MAPE   MASE  biais (log)  RMSE (log)
B : (1,0,0)(0,1,1) + tendance  136.571  169.051   6.132  0.641       -0.004       0.074
naïf saisonnier + dérive       156.641  209.579   6.700  0.735        0.013       0.085
A : SARIMAX(1,1,1)(0,1,1)      173.243  225.707   8.229  0.813       -0.069       0.100
C : régression + AR(1)         175.374  227.290   8.366  0.823       -0.070       0.101
naïf saisonnier                309.604  386.582  13.487  1.452        0.141       0.169
```

Lisons ce tableau (trié par RMSE en dinars ; `biais (log)` est la moyenne de $y-\hat y$ en logarithme, donc un biais **positif** signifie que le modèle **sous-estime**).

- Le **naïf saisonnier simple** est le plus mauvais, avec une MASE de 1,45 (pire que lui-même sur l'apprentissage) et un biais de $+0{,}14$ : il répète l'année passée sans tenir compte de la croissance, et donc sous-estime d'environ 14 %.
- Le **naïf saisonnier avec dérive**, trois lignes de code, est déjà très honorable : MASE de 0,74, MAPE de 6,7 %. Il **bat deux de nos trois modèles ARIMA** (A et C) sur cette fenêtre, en dinars comme en MAPE. Voilà pourquoi on ne néglige jamais les références simples.
- Le modèle **B** est le seul à faire nettement mieux que la référence (MASE de 0,64, MAPE de 6,1 %). Les modèles **A** et **C** ont un biais négatif d'environ $-0{,}07$ : ils **surestiment** de 7 % en moyenne. Nous verrons en 4.3.8 pourquoi.

> ⚠️ **Prévoir en dinars ou en logarithme ?** Nous avons optimisé les modèles en log (erreurs relatives), mais nous les jugeons en dinars (ce qui intéresse Yasmine) : une erreur de 300 DT en décembre et de 300 DT en février n'ont pas le même poids en log, mais le même en dinars. Quand l'objectif métier est en unités de la série, évaluez dans ces unités.

### 4.3.5 Vingt-quatre mois suffisent-ils pour conclure ?

Le tableau précédent donne un classement. Mais il repose sur **un seul** découpage, 24 erreurs **corrélées entre elles** (une erreur en mars annonce souvent une erreur en avril), et sur un seul tirage du hasard. Deux garde-fous.

**(1) Le plancher du bruit.** Même le *meilleur modèle possible* ne peut pas prévoir mieux que le bruit qui reste. Le modèle C estime les erreurs d'un AR(1) autour de la tendance et de la saison ; leur écart-type est $\sigma/\sqrt{1-\varphi^2}$ :

```python
sigma2, phi_C = mod_C.params["sigma2"], mod_C.params["ar.L1"]
print("écart-type de l'écart à la tendance et à la saison (modèle C) :", round(np.sqrt(sigma2 / (1 - phi_C ** 2)), 4))
print("écart-type des chocs d'un mois à l'autre                       :", round(np.sqrt(sigma2), 4))
```
<!--sortie-->
```text
écart-type de l'écart à la tendance et à la saison (modèle C) : 0.0715
écart-type des chocs d'un mois à l'autre                       : 0.0603
```

Pour des prévisions à long terme (au-delà de quelques mois), aucun modèle ne peut descendre durablement sous une erreur de l'ordre de 0,07 en logarithme (environ 7 %) : c'est la limite physique. Un écart de 0,01 entre deux modèles n'est pas une différence que 24 points permettent d'établir.

**(2) Un bootstrap par blocs.** Pour quantifier l'incertitude sur l'écart de performance entre deux modèles, on rééchantillonne les **différences d'erreurs quadratiques** par **blocs** de 6 mois consécutifs (pour conserver la corrélation) : si l'intervalle à 95 % de la différence moyenne **contient 0**, l'avantage d'un modèle n'est pas établi.

```python
def bootstrap_blocs(e1, e2, L=6, B=4000, graine=0):
    """Intervalle à 95 % de la différence moyenne des erreurs quadratiques (modèle 1 - modèle 2), par blocs de L mois."""
    rng = np.random.default_rng(graine)
    d = np.asarray(e1) ** 2 - np.asarray(e2) ** 2
    n = len(d)
    moyennes = []
    for _ in range(B):
        debuts = rng.integers(0, n - L + 1, int(np.ceil(n / L)))
        idx = np.concatenate([np.arange(s, s + L) for s in debuts])[:n]
        moyennes.append(d[idx].mean())
    return np.percentile(moyennes, [2.5, 97.5]), np.mean(np.array(moyennes) < 0)

erreurs = {k: (test - f).values for k, f in prev_log.items()}
paires = [("B : (1,0,0)(0,1,1) + tendance", "A : SARIMAX(1,1,1)(0,1,1)"),
          ("B : (1,0,0)(0,1,1) + tendance", "C : régression + AR(1)"),
          ("A : SARIMAX(1,1,1)(0,1,1)", "C : régression + AR(1)"),
          ("A : SARIMAX(1,1,1)(0,1,1)", "naïf saisonnier + dérive")]
for a, b in paires:
    (lo, hi), part = bootstrap_blocs(erreurs[a], erreurs[b])
    print(f"{a[:24]:25s} contre {b[:24]:25s} : IC95 = [{lo:+.4f} ; {hi:+.4f}]  | part où le 1er est meilleur : {part:.2f}")
```
<!--sortie-->
```text
B : (1,0,0)(0,1,1) + ten  contre A : SARIMAX(1,1,1)(0,1,1  : IC95 = [-0.0092 ; -0.0011]  | part où le 1er est meilleur : 0.99
B : (1,0,0)(0,1,1) + ten  contre C : régression + AR(1)    : IC95 = [-0.0097 ; -0.0010]  | part où le 1er est meilleur : 0.99
A : SARIMAX(1,1,1)(0,1,1  contre C : régression + AR(1)    : IC95 = [-0.0007 ; +0.0004]  | part où le 1er est meilleur : 0.76
A : SARIMAX(1,1,1)(0,1,1  contre naïf saisonnier + dérive  : IC95 = [-0.0028 ; +0.0083]  | part où le 1er est meilleur : 0.17
```

Lecture : un intervalle **entièrement négatif** signifie que le premier modèle est meilleur de façon robuste *sur cette fenêtre* ; un intervalle contenant 0, qu'on ne peut pas conclure. Ici, **B bat A et C** (intervalles négatifs, mais proches de 0 : l'avantage est réel sur cette fenêtre et modeste), tandis que **A et C sont indiscernables**, et que **A ne se distingue pas de la référence simple** (intervalle qui contient 0). Ces résultats portent sur **cette** fenêtre de 24 mois, et nous allons voir en 4.3.8 qu'elle n'est pas anodine.

> ⚠️ **Le test de Diebold-Mariano.** On rencontre souvent ce test pour comparer deux prévisions. Il suppose des erreurs d'**un même horizon** (une suite temporelle de différences de pertes) ; appliqué à des prévisions de 1 à 24 mois issues d'**une seule** origine, il mélange des horizons dont la variance n'est pas la même. Le bootstrap par blocs ci-dessus est plus simple et rend le même service ; le test de Diebold-Mariano trouve sa place quand on dispose d'erreurs à horizon fixe pour de nombreuses origines (4.3.6).

### 4.3.6 La validation à origine glissante

Un seul découpage ne donne qu'un seul exemple d'erreur. Pour en avoir plusieurs, on **recommence plusieurs fois** en avançant l'origine : à chaque étape on ajuste le modèle sur les données jusqu'à la date $T$, on prévoit les $H=12$ mois suivants, on mesure l'erreur, puis on avance $T$ d'un mois (fenêtre **croissante**). On obtient, pour chaque horizon $h$ de 1 à 12, une dizaine d'erreurs. C'est la **validation croisée à origine glissante** (*rolling-origin*, ou *time-series cross-validation*).

> ⚠️ **Honnêteté.** Ces origines (décembre 2023 à décembre 2024) sont celles de notre jeu de test : nous réutilisons la **même période**, avec un autre usage. Les structures des modèles (A, B, C) ont été choisies en 4.2 sur l'apprentissage seul ; ce qui est ré-estimé à chaque origine, ce sont les paramètres. Il n'y a donc pas de fuite, mais il n'y a pas non plus de nouvelles données : le test de 24 mois est « utilisé » ici et ne servira plus à rien d'autre.

On ajoute une cinquième prévision, une **combinaison** : la moyenne des prévisions des trois modèles A, B, C (la combinaison de prévisions est connue pour être robuste : les erreurs de modèles différents ne se corrigent qu'en partie, mais elles se corrigent).

```python
H = 12
origines = list(range(96, 109))                       # 13 origines : fin décembre 2023, ..., fin décembre 2024

def prev_naif(i):
    return y.iloc[i - 12:i - 12 + H].values

def prev_derive(i):
    tr = y.iloc[:i]
    gi = (tr - tr.shift(12)).mean()
    return np.array([tr.iloc[-12 + (h % 12)] + gi * (1 + h // 12) for h in range(H)])

def prev_modele_A(i):
    m = SARIMAX(y.iloc[:i], exog=X.iloc[:i], order=(1, 1, 1), seasonal_order=(0, 1, 1, 12)).fit(disp=False)
    return m.forecast(H, exog=X.iloc[i:i + H]).values

def prev_modele_B(i):
    m = SARIMAX(y.iloc[:i], exog=X.iloc[:i], order=(1, 0, 0), seasonal_order=(0, 1, 1, 12), trend="ct").fit(disp=False, maxiter=300)
    return m.forecast(H, exog=X.iloc[i:i + H]).values

def prev_modele_C(i):
    m = ARIMA(y.iloc[:i], exog=XX.iloc[:i], order=(1, 0, 0), trend="n").fit()
    return m.forecast(H, exog=XX.iloc[i:i + H]).values

fonctions = {"naïf saisonnier": prev_naif, "naïf saisonnier + dérive": prev_derive,
             "A : SARIMAX(1,1,1)(0,1,1)": prev_modele_A, "B : (1,0,0)(0,1,1) + tendance": prev_modele_B,
             "C : régression + AR(1)": prev_modele_C}
P = {nom: np.array([f(i) for i in origines]) for nom, f in fonctions.items()}      # forme (13 origines, 12 horizons)
P["combinaison A+B+C"] = (P["A : SARIMAX(1,1,1)(0,1,1)"] + P["B : (1,0,0)(0,1,1) + tendance"] + P["C : régression + AR(1)"]) / 3
reel = np.array([y.iloc[i:i + H].values for i in origines])

lignes = []
for nom, f in P.items():
    e = reel - f
    lignes.append({"modèle": nom, "RMSE global": np.sqrt((e ** 2).mean()), "h = 1": np.sqrt((e[:, 0] ** 2).mean()),
                   "h = 6": np.sqrt((e[:, 5] ** 2).mean()), "h = 12": np.sqrt((e[:, 11] ** 2).mean()), "biais": e.mean()})
tab_glissant = pd.DataFrame(lignes).set_index("modèle").sort_values("RMSE global")
print("RMSE en logarithme, 13 origines x 12 horizons :")
print(tab_glissant.round(4).to_string())

fig, ax = plt.subplots(figsize=(8, 4))
couleurs = {"naïf saisonnier": "#898781", "naïf saisonnier + dérive": VIOLET, "A : SARIMAX(1,1,1)(0,1,1)": ORANGE,
            "B : (1,0,0)(0,1,1) + tendance": BLEU, "C : régression + AR(1)": ROUGE, "combinaison A+B+C": AQUA}
for nom, f in P.items():
    ax.plot(range(1, H + 1), np.sqrt(((reel - f) ** 2).mean(axis=0)), "o-", ms=3.5, lw=1.6, color=couleurs[nom], label=nom)
ax.set_xlabel("horizon de prévision (mois)")
ax.set_ylabel("RMSE (en logarithme)")
ax.set_xticks(range(1, H + 1))
ax.legend(fontsize=8, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.17))
ax.grid(True, color="#e1e0d9", lw=0.6)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("figures/ch04-origine-glissante.png", bbox_inches="tight")
```
<!--sortie-->
```text
RMSE en logarithme, 13 origines x 12 horizons :
                               RMSE global   h = 1   h = 6  h = 12   biais
modèle                                                                    
B : (1,0,0)(0,1,1) + tendance       0.0670  0.0712  0.0581  0.0889  0.0037
combinaison A+B+C                   0.0687  0.0708  0.0521  0.0808 -0.0295
A : SARIMAX(1,1,1)(0,1,1)           0.0763  0.0737  0.0572  0.0890 -0.0416
C : régression + AR(1)              0.0807  0.0742  0.0637  0.0903 -0.0506
naïf saisonnier + dérive            0.0839  0.0753  0.0801  0.1052 -0.0175
naïf saisonnier                     0.1081  0.1213  0.1100  0.1264  0.0707
```

![Erreur de prévision (RMSE en logarithme) selon l'horizon, pour six méthodes évaluées à 13 origines glissantes. Le naïf saisonnier est nettement derrière ; les modèles ARIMA et leur combinaison sont proches les uns des autres.](figures/ch04-origine-glissante.png)

Trois enseignements, que les chiffres du tableau confirment :

1. **Le naïf saisonnier simple est nettement le moins bon** : il ne sait pas que la série croît. Le naïf **avec dérive** (RMSE de 0,084), trois lignes de code, fait déjà beaucoup mieux, et fait presque jeu égal avec le modèle C (0,081) : **toujours essayer les références simples**.
2. **Les modèles ARIMA/régression sont proches les uns des autres**, avec un avantage au modèle B (RMSE global de 0,067), qui combine différence saisonnière (il s'adapte au niveau de l'an dernier) et tendance déterministe. La **combinaison** A+B+C (0,069) est presque aussi bonne, **sans avoir à choisir**, et elle est la meilleure aux horizons 1, 6 et 12 du tableau.
3. L'erreur **ne croît pas régulièrement avec l'horizon** (le graphique est irrégulier, avec seulement 13 origines) : elle se situe entre 0,05 et 0,10 pour tous les modèles ARIMA, c'est-à-dire autour du plancher de 0,07 évoqué en 4.3.5. Les écarts entre courbes sont petits devant cette bande de bruit.

### 4.3.7 Application : les ventes de 2026

Yasmine prépare son budget. Nous prévoyons maintenant 2026 avec le modèle retenu (B), ajusté sur les **120** mois, en supposant une promotion en décembre 2026 (prévue par Yasmine), pas de COVID. Outre la prévision mois par mois, on lui donne une **prévision de l'année entière** avec son incertitude, obtenue par **simulation** : on tire 2 000 trajectoires futures plausibles du modèle (en respectant la corrélation entre mois) et on additionne les 12 mois de chacune.

```python
X_2026 = pd.DataFrame({"promo": [0.0] * 11 + [1.0], "covid": [0.0] * 12},
                      index=pd.date_range("2026-01-01", periods=12, freq="MS"))
final = SARIMAX(y, exog=X, order=(1, 0, 0), seasonal_order=(0, 1, 1, 12), trend="ct").fit(disp=False, maxiter=300)
pf = final.get_forecast(12, exog=X_2026)
ic = np.asarray(pf.conf_int(alpha=0.05))
resume = pd.DataFrame({"prévision (DT)": np.exp(pf.predicted_mean.values), "IC95 bas": np.exp(ic[:, 0]), "IC95 haut": np.exp(ic[:, 1])},
                      index=X_2026.index.strftime("%Y-%m")).round(0).astype(int)
print(resume.to_string())

a_fin = final.predicted_state[:, -1]                       # loi de l'état caché juste après la dernière observation :
P_fin = final.predicted_state_cov[:, :, -1]                # moyenne et covariance
sigma = np.sqrt(final.params["sigma2"])

def une_trajectoire(graine):
    rng = np.random.default_rng(graine)                    # on tire nous-mêmes l'état initial et les chocs : résultat reproductible
    etat0 = rng.multivariate_normal(a_fin, P_fin, method="eigh")
    chocs = rng.normal(0, sigma, size=(12, 1))
    return final.simulate(12, measurement_shocks=np.zeros((12, 1)), state_shocks=chocs, initial_state=etat0,
                          anchor="end", exog=X_2026).values

simul = np.array([une_trajectoire(k) for k in range(2000)]).T          # forme (12 mois, 2000 trajectoires)
totaux = np.exp(simul).sum(axis=0)
total_2025 = v["ca"]["2025-01":"2025-12"].sum()
p10, p50, p90 = np.percentile(totaux, [10, 50, 90])
p025, p975 = np.percentile(totaux, [2.5, 97.5])
print(f"\ntotal 2025 observé : {total_2025:,.0f} DT")
print(f"total 2026 prévu   : médiane {p50:,.0f} DT | intervalle à 80 % [{p10:,.0f} ; {p90:,.0f}] | à 95 % [{p025:,.0f} ; {p975:,.0f}]")
print(f"croissance prévue sur 2025 : {100 * (p50 / total_2025 - 1):+.1f} %")

fig, ax = plt.subplots(figsize=(10, 3.8))
hist = v["ca"]["2023-01":]
ax.plot(hist.index, hist, color=BLEU, lw=1.6, label="observé")
ax.plot(X_2026.index, np.exp(pf.predicted_mean), color=ORANGE, lw=1.8, label="prévision 2026")
ax.fill_between(X_2026.index, np.exp(ic[:, 0]), np.exp(ic[:, 1]), color=ORANGE, alpha=0.2, label="intervalle à 95 %")
ax.set_ylabel("chiffre d'affaires mensuel (DT)")
ax.legend(loc="upper left")
ax.grid(True, color="#e1e0d9", lw=0.6)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("figures/ch04-prevision-2026.png", bbox_inches="tight")
```
<!--sortie-->
```text
         prévision (DT)  IC95 bas  IC95 haut
2026-01            1414      1214       1648
2026-02            1694      1434       2001
2026-03            2130      1799       2522
2026-04            2207      1863       2614
2026-05            2495      2106       2956
2026-06            2881      2431       3413
2026-07            2864      2418       3393
2026-08            2637      2226       3124
2026-09            2067      1745       2449
2026-10            1873      1581       2219
2026-11            2602      2197       3083
2026-12            4195      3541       4970

total 2025 observé : 27,630 DT
total 2026 prévu   : médiane 29,169 DT | intervalle à 80 % [27,823 ; 30,597] | à 95 % [27,073 ; 31,397]
croissance prévue sur 2025 : +5.6 %
```

![Chiffre d'affaires mensuel depuis 2023 et prévision pour 2026 (courbe orange) avec son intervalle de prévision à 95 %.](figures/ch04-prevision-2026.png)

Yasmine peut retenir trois messages : (1) **le profil de l'année** : le creux de janvier, le plateau d'été, le pic de décembre ; (2) une **fourchette** de chiffre d'affaires annuel plutôt qu'un point (la fourchette à 80 % est un bon outil de budget) ; (3) une croissance attendue de l'ordre de **+5 %** sur 2025, avec une incertitude que la fourchette rend visible. Cette croissance est inférieure à la tendance de long terme de la série (environ 9 % par an, voir 4.3.4) parce que le modèle B repart du **niveau récent**, resté sous la tendance : nous verrons en 4.3.8 que ce choix est un pari sur la persistance de ces écarts.

> ⚠️ **Ce que cette prévision suppose.** Que la structure observée de 2016 à 2025 **se prolonge** (même croissance, même saisonnalité), que la promotion de décembre ait lieu, et qu'aucun choc du type COVID n'arrive (un tel choc est par nature imprévisible : les intervalles de prévision ne le contiennent pas). Une prévision n'est pas une promesse : c'est le résultat d'un modèle et d'hypothèses, qu'il faut toujours énoncer à côté du chiffre.

### 4.3.8 Révélation : comment les données ont été fabriquées

Les ventes de Dar Jasmin sont **simulées**. Il est temps de lever le voile. Voici la recette complète : une tendance exponentielle (+0,75 % par mois), une saisonnalité **déterministe** (un facteur multiplicatif par mois), un bruit **AR(1)** (coefficient 0,5, chocs de 0,07), un effet de promotion (+10 % en log), et un choc COVID (−0,55 en log, mars à juin 2020).

```python
def simuler_ventes(graine):
    """La recette exacte du fichier ventes_mensuelles.csv (graine 2018)."""
    rng = np.random.default_rng(graine)
    mois = pd.date_range("2016-01-01", "2025-12-01", freq="MS")
    t = np.arange(120)
    saison = np.array([0.62, 0.72, 0.95, 1.00, 1.12, 1.18, 1.22, 1.15, 0.90, 0.78, 1.05, 1.55])   # facteur multiplicatif par mois
    bruit = np.zeros(120)
    for i in range(1, 120):
        bruit[i] = 0.5 * bruit[i - 1] + rng.normal(0, 0.07)                                      # AR(1) : phi = 0,5 ; sigma = 0,07
    promo = (rng.random(120) < 0.15).astype(int)
    covid = ((mois >= "2020-03-01") & (mois <= "2020-06-01")).astype(int)
    log_ca = np.log(1000) + 0.0075 * t + np.log(saison[mois.month - 1]) + bruit + 0.10 * promo - 0.55 * covid
    d = pd.DataFrame({"ca": np.round(np.exp(log_ca), 1), "promo": promo, "covid": covid}, index=mois)
    return d, pd.Series(bruit, index=mois)

recette, bruit = simuler_ventes(2018)
print("la recette reproduit exactement le fichier :", np.allclose(recette["ca"].values, v["ca"].values)
      and (recette["promo"].values == v["promo"].values).all() and (recette["covid"].values == v["covid"].values).all())
```
<!--sortie-->
```text
la recette reproduit exactement le fichier : True
```

Comparons ce que les modèles ont **estimé** à ce qui a été **programmé** :

```python
vrai_saison = np.log(np.array([0.62, 0.72, 0.95, 1.00, 1.12, 1.18, 1.22, 1.15, 0.90, 0.78, 1.05, 1.55]))
estim_saison = np.r_[0.0, mod_C.params[[f"m_{k:02d}" for k in range(2, 13)]].values]          # relatif à janvier
tab_vrai = pd.DataFrame({"programmé": [0.0075, 0.10, -0.55, 0.5, 0.07],
                         "modèle A": [np.nan, mod_A.params["promo"], mod_A.params["covid"], np.nan, np.nan],
                         "modèle B": [np.nan, mod_B.params["promo"], mod_B.params["covid"], np.nan, np.nan],
                         "modèle C": [mod_C.params["t"], mod_C.params["promo"], mod_C.params["covid"], mod_C.params["ar.L1"], np.sqrt(mod_C.params["sigma2"])]},
                        index=["pente de la tendance (par mois)", "effet promo (log)", "effet COVID (log)", "AR(1) : phi", "chocs : sigma"])
print(tab_vrai.round(4).to_string())
print()
saison_cmp = pd.DataFrame({"programmé": vrai_saison - vrai_saison[0], "estimé (modèle C)": estim_saison},
                          index=["jan", "fév", "mar", "avr", "mai", "juin", "juil", "août", "sept", "oct", "nov", "déc"])
print("profil saisonnier, en log et relativement à janvier :")
print(saison_cmp.round(2).T.to_string())
```
<!--sortie-->
```text
                                 programmé  modèle A  modèle B  modèle C
pente de la tendance (par mois)     0.0075       NaN       NaN    0.0077
effet promo (log)                   0.1000    0.1061    0.0995    0.1063
effet COVID (log)                  -0.5500   -0.5371   -0.5055   -0.5408
AR(1) : phi                         0.5000       NaN       NaN    0.5388
chocs : sigma                       0.0700       NaN       NaN    0.0603

profil saisonnier, en log et relativement à janvier :
                   jan   fév   mar   avr   mai  juin  juil  août  sept   oct   nov   déc
programmé          0.0  0.15  0.43  0.48  0.59  0.64  0.68  0.62  0.37  0.23  0.53  0.92
estimé (modèle C)  0.0  0.18  0.46  0.51  0.59  0.66  0.70  0.61  0.37  0.20  0.48  0.94
```

Les modèles ont **retrouvé** la recette : la pente de la tendance (0,0077 estimé pour 0,0075), l'effet de la promotion (0,106 pour 0,10), l'effet du COVID (de $-0{,}51$ à $-0{,}54$ pour $-0{,}55$), la saison mois par mois (écarts de quelques centièmes en log), le coefficient AR (0,54 pour 0,5) ; seule la taille des chocs est un peu sous-estimée (0,060 pour 0,07). Et nos soupçons étaient fondés : la tendance et la saison étaient bien **déterministes**, ce que laissaient entendre les tests ambigus de 4.1.6 et les MA proches de $-1$ de 4.2.4. Le modèle C a la **structure exacte** de la vérité.

**Pourtant, C n'a pas gagné le concours de 4.3.4.** Pourquoi un modèle correctement spécifié perd-il ? La réponse tient au bruit. Calculons ce que valait le **bruit programmé** sur les deux périodes :

```python
print("bruit AR(1) programmé, moyenne : apprentissage =", round(bruit[:"2023-12"].mean(), 4), "| test =", round(bruit["2024-01":].mean(), 4))
print("écart-type du bruit sur le test :", round(bruit["2024-01":].std(), 4), "| RMSE du « modèle parfait » (qui connaîtrait tous les paramètres) :", round(np.sqrt((bruit["2024-01":] ** 2).mean()), 4))
print("biais moyen des prévisions du modèle C sur le test :", round(float(np.mean(test - prev_log["C : régression + AR(1)"])), 4))
```
<!--sortie-->
```text
bruit AR(1) programmé, moyenne : apprentissage = -0.014 | test = -0.0695
écart-type du bruit sur le test : 0.0657 | RMSE du « modèle parfait » (qui connaîtrait tous les paramètres) : 0.0947
biais moyen des prévisions du modèle C sur le test : -0.0696
```

Le bruit programmé sur les 24 mois de test est **négativement décalé** en moyenne : $-0{,}0695$ en log, soit environ 7 % de ventes en dessous de la tendance et de la saison (contre $-0{,}014$ pendant l'apprentissage). Le modèle C, qui ne croit qu'à la tendance et à la saison, prévoit « la tendance » : son erreur moyenne ($y-\hat y$ vaut $-0{,}0696$ en moyenne, contre $-0{,}0695$ pour le bruit) est **exactement ce bruit**. Le « biais » de C n'est pas un défaut du modèle : c'est la trajectoire du hasard. Même un « modèle parfait » qui connaîtrait tous les paramètres aurait une RMSE de 0,095 sur ces 24 mois, **plus** que le modèle B (0,074, en log). C'est la malchance de cet échantillon de test : la série est restée sous sa tendance pendant deux ans, et le modèle B, qui **s'ajuste au niveau récent** grâce à sa différence saisonnière, a bénéficié de cette persistance. (Dans cette situation, il a *parié* sur la persistance des écarts, et il a gagné. Ce pari est bon quand les écarts sont persistants et mauvais quand ils sont transitoires.)

Un test sur **une** trajectoire ne distingue pas « bon modèle » et « modèle chanceux ». La seule façon de le savoir est de **rejouer le hasard** : tirons plusieurs historiques complets avec la même recette (graines différentes), ajustons B et C sur les 96 premiers mois de chacun, prévoyons les 24 suivants, et comparons les erreurs.

```python
mois_calendaire = lambda idx: pd.get_dummies(pd.Series(idx.month, index=idx).astype(str).str.zfill(2), prefix="m", drop_first=True, dtype=float)

def un_essai(graine):
    d, _ = simuler_ventes(graine)
    d.index.freq = "MS"
    yy = np.log(d["ca"])
    XXe = pd.concat([pd.Series(1.0, index=d.index, name="const"), pd.Series(np.arange(120.0), index=d.index, name="t"),
                     mois_calendaire(d.index), d[["promo", "covid"]].astype(float)], axis=1)
    Xe = d[["promo", "covid"]].astype(float)
    tr, te = yy[:96], yy[96:]
    gg = (tr - tr.shift(12)).mean()
    prevs = {"naïf saisonnier + dérive": np.array([tr.iloc[-12 + (h % 12)] + gg * (1 + h // 12) for h in range(24)]),
             "B": SARIMAX(tr, exog=Xe[:96], order=(1, 0, 0), seasonal_order=(0, 1, 1, 12), trend="ct").fit(disp=False, maxiter=300).forecast(24, exog=Xe[96:]).values,
             "C": ARIMA(tr, exog=XXe[:96], order=(1, 0, 0), trend="n").fit().forecast(24, exog=XXe[96:]).values}
    return {k: np.sqrt(np.mean((te.values - f) ** 2)) for k, f in prevs.items()}

essais = pd.DataFrame([un_essai(5000 + k) for k in range(30)])
print("RMSE (log) sur 24 mois de test, moyenne de 30 historiques simulés :")
print(essais.mean().round(4).to_string())
print("\nC bat B dans", int((essais["C"] < essais["B"]).sum()), "historiques sur 30 ;",
      "C bat le naïf avec dérive dans", int((essais["C"] < essais["naïf saisonnier + dérive"]).sum()), "sur 30")
```
<!--sortie-->
```text
RMSE (log) sur 24 mois de test, moyenne de 30 historiques simulés :
naïf saisonnier + dérive    0.1289
B                           0.1108
C                           0.0878

C bat B dans 25 historiques sur 30 ; C bat le naïf avec dérive dans 30 sur 30
```

Sur 30 historiques, c'est le **modèle de structure exacte (C)** qui a en moyenne la meilleure performance, mais il **ne gagne pas à chaque fois** : le résultat d'un seul découpage dépend beaucoup de la trajectoire du bruit. C'est exactement ce qu'on attend de la statistique : une conclusion se juge sur la **répétition**, pas sur un tirage.

> ✅ **À retenir.**
> - Une prévision est un **couple** (valeur, incertitude). Pour un AR(1) : $\hat y_{T+h}=\mu+\varphi^h(Y_T-\mu)$ et la variance de l'erreur croît de $\sigma^2$ vers $\sigma^2/(1-\varphi^2)$ ; avec une différence première, elle croît **sans limite**.
> - En logarithme, $e^{\hat y}$ est la **médiane** ; les intervalles se transforment par l'exponentielle.
> - **Découpage temporel obligatoire** : jamais de mélange au hasard. Un modèle flexible peut avoir une excellente évaluation « au hasard » et extrapoler n'importe comment.
> - Toujours comparer à des **références simples** (naïf saisonnier, avec dérive). Mesures : MAE, RMSE, MAPE (attention aux zéros), **MASE** (sans unité, $<1$ = bat le naïf).
> - Un seul découpage de 24 mois est **bruité** : l'erreur d'un modèle parfait est plafonnée par le bruit de la série ; on utilise un bootstrap par blocs, et surtout la **validation à origine glissante**. Les **combinaisons** de prévisions sont robustes.
> - Les modèles ne s'évaluent pas par l'AIC entre familles différentes, mais par la **prévision hors échantillon**, répétée.
> - Une prévision se publie avec ses **hypothèses** (promotions connues, pas de choc type COVID).


## 4.4 ➕ Pour aller plus loin : séries multivariées, cointégration et GARCH

> 🧭 **Section optionnelle.** Les sections 4.1 à 4.3 traitent **une** série à la fois et se suffisent à elles-mêmes. Ici, nous élargissons le cadre dans trois directions : **plusieurs séries qui s'influencent** (VAR), **des séries qui dérivent mais restent liées** (cointégration), et **une variabilité qui change dans le temps** (GARCH). Si vous cherchez l'essentiel, sautez à la section 4.5 ou aux exercices.

### 4.4.1 Plusieurs séries à la fois : le modèle VAR

Le chiffre d'affaires et le **nombre de commandes** sont deux séries liées. Un modèle **VAR** (*vector autoregression*) décrit chacune comme une combinaison du passé de *toutes* les séries. Pour deux séries $y_{1,t}$ et $y_{2,t}$, regroupées dans le vecteur $\mathbf y_t$, le VAR(1) s'écrit

$$\mathbf y_t=\mathbf c+A\,\mathbf y_{t-1}+\boldsymbol\varepsilon_t,\qquad A=\begin{pmatrix}a_{11}&a_{12}\\a_{21}&a_{22}\end{pmatrix}.$$

C'est un AR(1) où le coefficient $\varphi$ devient une **matrice**. Chaque ligne est une régression linéaire ordinaire (chapitre 1) de $y_{i,t}$ sur les deux retards : le coefficient $a_{12}$ dit combien le passé de la série 2 aide à prévoir la série 1, **au-delà** du passé de la série 1 elle-même.

> 📐 **Stationnarité d'un VAR(1).** Comme pour l'AR(1) ($|\varphi|<1$), la condition est que **toutes les valeurs propres de $A$ soient de module strictement inférieur à 1** (volume I, section 1.1.3 : une valeur propre mesure de combien la matrice étire une direction ; $A^k\to0$ si et seulement si ce facteur est inférieur à 1). Pour un VAR($p$), on applique la même condition à la « matrice compagne » du système.

> 💡 **Exemple à la main.** Soit $A=\begin{pmatrix}0{,}5&0{,}2\\0{,}1&0{,}4\end{pmatrix}$. Sa trace vaut $0{,}9$ et son déterminant $0{,}5\times0{,}4-0{,}2\times0{,}1=0{,}18$. Les valeurs propres sont solutions de $\lambda^2-0{,}9\lambda+0{,}18=0$, soit $\lambda=\frac{0{,}9\pm\sqrt{0{,}81-0{,}72}}2=\frac{0{,}9\pm0{,}3}2$, donc $0{,}6$ et $0{,}3$ : le système est stationnaire. Si un choc de 1 frappe la série 1 à la date 0, la réponse au pas $k$ est la première colonne de $A^k$ : $(1;0)$, puis $(0{,}5;\,0{,}1)$, puis $A^2\binom10=(0{,}27;\,0{,}09)$… C'est la **fonction de réponse impulsionnelle** : un choc sur une série se propage dans l'autre.

```python
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.api as sm
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import coint, adfuller
from statsmodels.stats.diagnostic import het_arch, acorr_ljungbox
from arch import arch_model

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
A = np.array([[0.5, 0.2], [0.1, 0.4]])
print("valeurs propres de A :", np.linalg.eigvals(A).round(3), "-> stationnaire :", bool(np.all(np.abs(np.linalg.eigvals(A)) < 1)))
for k in (1, 2, 3):
    print(f"réponse à un choc unitaire sur la série 1, pas {k} :", (np.linalg.matrix_power(A, k) @ np.array([1, 0])).round(3))
```
<!--sortie-->
```text
valeurs propres de A : [0.6+0.j 0.3+0.j] -> stationnaire : True
réponse à un choc unitaire sur la série 1, pas 1 : [0.5 0.1]
réponse à un choc unitaire sur la série 1, pas 2 : [0.27 0.09]
réponse à un choc unitaire sur la série 1, pas 3 : [0.153 0.063]
```

#### Application : ventes et commandes

Le VAR suppose des séries **stationnaires**. Pour les rendre telles, on utilise l'idée de 4.2.7 : on retire de chaque série (en logarithme) sa **tendance, sa saison, la promotion et le COVID** par régression, et on garde l'**écart** — ce qui reste quand on a enlevé tout ce qu'on sait expliquer. Ces écarts sont stationnaires (nous le vérifions) et ce sont eux qui portent la dynamique conjointe. Nous utilisons les 96 mois d'apprentissage.

```python
tr = XX[:"2023-12"]                                       # tendance, mois, promo, covid (objet défini en 4.3)
ecarts = pd.DataFrame({"e_ca": sm.OLS(np.log(v["ca"][:"2023-12"]), tr).fit().resid,
                       "e_nb": sm.OLS(np.log(v["nb_commandes"][:"2023-12"]), tr).fit().resid})
print("écarts-types :", ecarts.std().round(3).to_dict(), "| corrélation instantanée :", round(ecarts.corr().iloc[0, 1], 3))
for c in ecarts:
    print(f"test ADF de {c} : p-valeur = {adfuller(ecarts[c], regression='n', autolag='AIC')[1]:.1e}")

modele = VAR(ecarts)
print(modele.select_order(4).summary())
var1 = modele.fit(maxlags=1)
print(pd.concat({"coefficient": var1.params, "p-valeur": var1.pvalues}, axis=1).round(3).to_string())
print("modules des valeurs propres de la matrice A estimée :", np.abs(np.linalg.eigvals(var1.coefs[0])).round(3))
```
<!--sortie-->
```text
écarts-types : {'e_ca': 0.072, 'e_nb': 0.226} | corrélation instantanée : 0.235
test ADF de e_ca : p-valeur = 2.6e-07
test ADF de e_nb : p-valeur = 7.5e-08
 VAR Order Selection (* highlights the minimums) 
=================================================
      AIC         BIC         FPE         HQIC   
-------------------------------------------------
0      -8.241      -8.186   0.0002636      -8.219
1     -8.515*     -8.351*  0.0002004*     -8.449*
2      -8.479      -8.205   0.0002077      -8.369
3      -8.493      -8.109   0.0002051      -8.338
4      -8.466      -7.973   0.0002107      -8.267
-------------------------------------------------
        coefficient        p-valeur       
               e_ca   e_nb     e_ca   e_nb
const        -0.001 -0.005    0.930  0.825
L1.e_ca       0.520  0.675    0.000  0.036
L1.e_nb       0.026 -0.003    0.368  0.976
modules des valeurs propres de la matrice A estimée : [0.552 0.035]
```

Les deux écarts sont stationnaires. Les critères (AIC, BIC) choisissent **un seul retard**. Lecture des coefficients : l'écart de chiffre d'affaires d'un mois influence celui du mois suivant (coefficient d'environ $0{,}52$, comme le AR(1) du modèle C), et il **prévoit aussi** l'écart du nombre de commandes ($\approx0{,}68$, p-valeur $\approx0{,}04$). L'effet inverse (commandes $\to$ chiffre d'affaires) est proche de zéro.

> 📐 **Causalité au sens de Granger.** On dit que $x$ *cause* $y$ **au sens de Granger** si le passé de $x$ améliore la prévision de $y$ au-delà de son propre passé ; on le teste par un test de Fisher sur les coefficients du retard de $x$ dans l'équation de $y$ (hypothèse nulle : ils sont tous nuls).

```python
g1 = var1.test_causality("e_nb", ["e_ca"], kind="f")
g2 = var1.test_causality("e_ca", ["e_nb"], kind="f")
print(f"le chiffre d'affaires précède le nombre de commandes : F = {g1.test_statistic:.2f}, p = {g1.pvalue:.3f}")
print(f"le nombre de commandes précède le chiffre d'affaires : F = {g2.test_statistic:.2f}, p = {g2.pvalue:.3f}")

irf = var1.irf(8)
fig, axes = plt.subplots(1, 2, figsize=(10, 3.4), sharey=False)
for ax, (j, nom) in zip(axes, [(0, "choc sur l'écart de chiffre d'affaires"), (1, "choc sur l'écart de nombre de commandes")]):
    ax.plot(range(9), irf.irfs[:, 0, j], "o-", color=BLEU, lw=1.6, ms=4, label="réponse du chiffre d'affaires")
    ax.plot(range(9), irf.irfs[:, 1, j], "o-", color=ORANGE, lw=1.6, ms=4, label="réponse du nombre de commandes")
    ax.axhline(0, color="#898781", lw=0.8)
    ax.set_title(nom, fontsize=10)
    ax.set_xlabel("mois après le choc")
    ax.grid(True, color="#e1e0d9", lw=0.6)
    ax.spines[["top", "right"]].set_visible(False)
axes[0].legend(fontsize=8)
plt.tight_layout()
plt.savefig("figures/ch04-var-irf.png", bbox_inches="tight")
```
<!--sortie-->
```text
le chiffre d'affaires précède le nombre de commandes : F = 4.41, p = 0.037
le nombre de commandes précède le chiffre d'affaires : F = 0.81, p = 0.369
```

![Fonctions de réponse impulsionnelle du VAR(1) : un choc de 1 sur l'écart de chiffre d'affaires (à gauche) se transmet à l'écart de commandes avec un effet plus important, puis s'atténue ; un choc sur les commandes (à droite) a très peu d'effet sur le chiffre d'affaires.](figures/ch04-var-irf.png)

> ⚠️ **« Cause au sens de Granger » ne veut pas dire « cause ».** Le test dit seulement que le passé du chiffre d'affaires **aide à prévoir** le nombre de commandes. Ici, la raison est connue, puisque nous avons fabriqué les données : le nombre de commandes est tiré d'une loi de Poisson dont la moyenne est le chiffre d'affaires du mois divisé par 58 (le panier moyen). Le nombre de commandes est donc une **mesure bruitée** du chiffre d'affaires *du même mois* ; comme le chiffre d'affaires est lui-même autocorrélé, son passé aide à prévoir cette mesure, et un nombre de commandes passé n'apporte rien de plus sur le chiffre d'affaires futur que le chiffre d'affaires passé lui-même. Aucune « influence » ne passe d'un mois à l'autre : c'est de l'**information**, pas de la causalité. Pour parler de causalité, il faut un schéma d'étude, pas un test de précédence (chapitre 7).

### 4.4.2 Cointégration : des séries qui dérivent ensemble

Passons à un autre piège, plus dangereux. Deux séries qui montent toutes les deux **semblent** liées, même si elles n'ont rien à voir. Prenons deux marches aléatoires **indépendantes** (4.1.3), régressons l'une sur l'autre, et regardons ce que dit la régression du chapitre 1. Répétons 1 000 fois :

```python
rng = np.random.default_rng(31)
n_sim = 1000
t_stats, r2, dw = [], [], []
for _ in range(n_sim):
    a = np.cumsum(rng.normal(size=100))
    b = np.cumsum(rng.normal(size=100))                      # indépendante de a par construction
    f = sm.OLS(a, sm.add_constant(b)).fit()
    t_stats.append(f.tvalues[1])
    r2.append(f.rsquared)
    dw.append(sm.stats.durbin_watson(f.resid))
t_stats = np.array(t_stats)
print("régressions d'une marche aléatoire sur une AUTRE, indépendante (100 points) :")
print("part des pentes « significatives » à 5 % :", round(np.mean(np.abs(t_stats) > 1.96), 3), " (on attendrait 0,05)")
print("R2 moyen :", round(np.mean(r2), 3), "| statistique de Durbin-Watson moyenne :", round(np.mean(dw), 3), " (2 = pas d'autocorrélation)")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.4))
a = np.cumsum(np.random.default_rng(5).normal(size=100))
b = np.cumsum(np.random.default_rng(6).normal(size=100))
ax1.plot(a, color=BLEU, lw=1.5, label="série 1")
ax1.plot(b, color=ORANGE, lw=1.5, label="série 2")
ax1.set_title("deux marches aléatoires indépendantes", fontsize=10)
ax1.legend(fontsize=8)
ax2.hist(t_stats, bins=50, color=BLEU, alpha=0.75)
ax2.axvline(-1.96, color=ROUGE, ls="--", lw=1.2)
ax2.axvline(1.96, color=ROUGE, ls="--", lw=1.2)
ax2.set_title("statistique t de la pente, 1 000 régressions", fontsize=10)
ax2.set_xlabel("valeur de t (les tirets marquent ±1,96)")
for ax in (ax1, ax2):
    ax.grid(True, color="#e1e0d9", lw=0.6)
    ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("figures/ch04-regression-fallacieuse.png", bbox_inches="tight")
```
<!--sortie-->
```text
régressions d'une marche aléatoire sur une AUTRE, indépendante (100 points) :
part des pentes « significatives » à 5 % : 0.769  (on attendrait 0,05)
R2 moyen : 0.244 | statistique de Durbin-Watson moyenne : 0.172  (2 = pas d'autocorrélation)
```

![À gauche, deux marches aléatoires indépendantes qui semblent évoluer ensemble. À droite, les statistiques t de la pente de 1 000 régressions de ce type : elles sont bien plus dispersées que la loi de Student, et une majorité franchit les seuils de ±1,96.](figures/ch04-regression-fallacieuse.png)

Résultat : près de **quatre régressions sur cinq** déclarent « significatif » un lien qui n'existe pas (au lieu de 5 %), avec un $R^2$ moyen d'environ 0,25 et une statistique de Durbin-Watson très basse (les résidus sont très autocorrélés). C'est la **régression fallacieuse** (Granger et Newbold, 1974) : quand les séries ne sont pas stationnaires, les p-valeurs de la régression sont **fausses** (les hypothèses du chapitre 1 ne tiennent plus). Règle de prudence : si le $R^2$ est supérieur à la statistique de Durbin-Watson, méfiez-vous.

Comment distinguer une vraie relation d'une illusion ? Par la **cointégration**. Deux séries non stationnaires (intégrées d'ordre 1) sont **cointégrées** s'il existe une combinaison linéaire $y_t-\beta x_t$ qui, elle, est **stationnaire** : les deux séries dérivent, mais **elles dérivent ensemble**, comme deux promeneurs liés par une corde élastique. Exemple plausible pour Dar Jasmin : un indice du coût des matières premières ($x_t$, une marche aléatoire) et le prix moyen de vente ($y_t$), qui suit le coût avec un écart temporaire. Nous les **simulons** : $x_t$ est une marche aléatoire, $y_t=2+1{,}5\,x_t+u_t$ avec $u_t$ un AR(1) de coefficient $0{,}6$.

La **méthode d'Engle et Granger** a deux temps : (1) on régresse $y$ sur $x$ ; (2) on teste la **racine unitaire des résidus** (ADF de 4.1.6, avec des seuils adaptés car les résidus sont estimés). S'ils sont stationnaires, il y a cointégration.

```python
rng = np.random.default_rng(31)
n = 150
x = np.cumsum(rng.normal(size=n))
u = np.zeros(n)
for t in range(1, n):
    u[t] = 0.6 * u[t - 1] + rng.normal(0, 0.5)
y_coint = 2 + 1.5 * x + u
y_indep = np.cumsum(rng.normal(size=n))                      # une série qui n'a rien à voir avec x

for nom, serie in [("y cointégrée avec x", y_coint), ("y indépendante de x", y_indep)]:
    stat, p, _ = coint(serie, x, trend="c")
    print(f"{nom:22s} : statistique d'Engle-Granger = {stat:6.2f} | p-valeur = {p:.3f}")

reg = sm.OLS(y_coint, sm.add_constant(x)).fit()
print("régression de y sur x : constante =", round(reg.params[0], 3), "| pente =", round(reg.params[1], 3), "  (programmé : 2 et 1,5)")
```
<!--sortie-->
```text
y cointégrée avec x    : statistique d'Engle-Granger =  -4.54 | p-valeur = 0.001
y indépendante de x    : statistique d'Engle-Granger =  -2.55 | p-valeur = 0.257
régression de y sur x : constante = 2.118 | pente = 1.494   (programmé : 2 et 1,5)
```

Pour la série cointégrée, le test rejette « pas de cointégration » (p-valeur proche de 0,001) et la pente estimée est très proche de 1,5 (les estimateurs de cointégration sont *super-convergents* : ils convergent à la vitesse $n$ au lieu de $\sqrt n$). Pour la série indépendante, le test ne rejette pas.

> 📐 **Le modèle à correction d'erreur.** Si $y_t-\beta x_t-c=u_t$ avec $u_t=\varphi u_{t-1}+e_t$ stationnaire ($|\varphi|<1$), alors en différenciant $y_t=\beta x_t+c+u_t$ : $\Delta y_t=\beta\,\Delta x_t+\Delta u_t=\beta\,\Delta x_t+(\varphi-1)\,u_{t-1}+e_t$. En remplaçant $u_{t-1}$ par l'**écart à l'équilibre** $y_{t-1}-\beta x_{t-1}-c$, on obtient
> $$\Delta y_t=\gamma\,\Delta x_t+\alpha\,(y_{t-1}-\beta x_{t-1}-c)+e_t,\qquad \gamma=\beta,\quad\alpha=\varphi-1<0.$$
> Le coefficient $\alpha$ est la **vitesse de rappel** : une fraction $|\alpha|=1-\varphi$ de l'écart à l'équilibre se résorbe à chaque période. Ici, on s'attend à $\alpha=-0{,}4$ et $\gamma=1{,}5$.

```python
ecart = (y_coint - reg.params[1] * x - reg.params[0])[:-1]            # écart à l'équilibre à la date t-1
dy, dx = np.diff(y_coint), np.diff(x)
ecm = sm.OLS(dy, sm.add_constant(np.column_stack([ecart, dx]))).fit()
print(pd.DataFrame({"estimation": ecm.params[1:], "erreur type": ecm.bse[1:], "théorie": [0.6 - 1, 1.5]},
                   index=["alpha (rappel)", "gamma (effet immédiat)"]).round(3).to_string())
```
<!--sortie-->
```text
                        estimation  erreur type  théorie
alpha (rappel)              -0.417        0.068     -0.4
gamma (effet immédiat)       1.524        0.040      1.5
```

Les estimations sont proches de la théorie ($\hat\alpha\approx-0{,}42$ pour $-0{,}4$ ; $\hat\gamma\approx1{,}52$ pour $1{,}5$) : environ 40 % de l'écart entre le prix de vente et son équilibre se résorbent chaque période, et une hausse immédiate du coût se répercute presque un pour un (à 1,5) sur le prix.

### 4.4.3 Quand la variabilité change : le modèle GARCH

Les modèles précédents supposent que les chocs $\varepsilon_t$ ont une **variance constante**. Certaines séries violent cette hypothèse de façon flagrante : en finance, les rendements calmes alternent avec des périodes agitées (**clusters de volatilité**). C'est le cas, par exemple, du taux de change qui préoccupe Yasmine quand elle importe de la laine d'Italie : une variation quotidienne du taux dinar/euro est difficile à prévoir **en moyenne**, mais ses variations *absolues* se regroupent.

> 🧭 **Les données de cette sous-section sont simulées** : un jeu de 1 500 « rendements quotidiens » (en %) tiré d'un modèle GARCH(1,1) à paramètres connus (graine 41). Nous n'avons pas de série réelle de taux de change hors ligne ; ce n'est donc **pas** un historique du dinar.

Le modèle **GARCH(1,1)** (Bollerslev, 1986) écrit le rendement $r_t=\mu+\varepsilon_t$, avec $\varepsilon_t=\sigma_tz_t$ ($z_t$ de loi $\mathcal N(0,1)$) et une variance qui **évolue** :

$$\sigma_t^2=\omega+\alpha\,\varepsilon_{t-1}^2+\beta\,\sigma_{t-1}^2.$$

Un gros choc hier ($\varepsilon_{t-1}^2$ grand) augmente la variance d'aujourd'hui (terme en $\alpha$) ; et la variance est persistante (terme en $\beta$).

> 📐 **Variance inconditionnelle.** Si $\alpha+\beta<1$, la variance moyenne à long terme existe : en prenant l'espérance de l'équation (avec $\mathbb E[\varepsilon_{t-1}^2]=\mathbb E[\sigma_{t-1}^2]=\sigma^2$), on obtient $\sigma^2=\omega+(\alpha+\beta)\sigma^2$, d'où $\sigma^2=\dfrac{\omega}{1-\alpha-\beta}$. La quantité $\alpha+\beta$ mesure la **persistance** de la volatilité.

> 💡 **Exemple à la main.** Avec $\omega=0{,}05$, $\alpha=0{,}10$, $\beta=0{,}85$ : la variance de long terme est $0{,}05/(1-0{,}95)=1$. Si hier le rendement s'est écarté de sa moyenne de $\varepsilon_{t-1}=3$ (un choc de 3 écarts-types) alors que la variance valait 1, la variance d'aujourd'hui sera $0{,}05+0{,}10\times9+0{,}85\times1=1{,}8$ : presque le double, d'un seul coup.

```python
omega, alpha, beta, mu = 0.05, 0.10, 0.85, 0.02
print("variance de long terme :", round(omega / (1 - alpha - beta), 3), "| variance après un choc de 3 :", round(omega + alpha * 9 + beta * 1, 3))

rng = np.random.default_rng(41)
n = 1500
sig2 = np.zeros(n)
r = np.zeros(n)
sig2[0] = omega / (1 - alpha - beta)
for t in range(n):
    if t > 0:
        sig2[t] = omega + alpha * (r[t - 1] - mu) ** 2 + beta * sig2[t - 1]
    r[t] = mu + np.sqrt(sig2[t]) * rng.normal()

print("kurtosis (excès) des rendements :", round(pd.Series(r).kurt(), 2), "(0 pour une loi normale)")
print("Ljung-Box (10 retards) sur les rendements : p =", round(float(acorr_ljungbox(r, lags=[10])["lb_pvalue"].iloc[0]), 4))
print("Ljung-Box (10 retards) sur les carrés    : p =", f"{float(acorr_ljungbox((r - r.mean()) ** 2, lags=[10])['lb_pvalue'].iloc[0]):.1e}")
print("test ARCH-LM (5 retards)                 : p =", f"{het_arch(r - r.mean(), nlags=5)[1]:.1e}")
```
<!--sortie-->
```text
variance de long terme : 1.0 | variance après un choc de 3 : 1.8
kurtosis (excès) des rendements : 0.25 (0 pour une loi normale)
Ljung-Box (10 retards) sur les rendements : p = 0.0019
Ljung-Box (10 retards) sur les carrés    : p = 4.7e-22
test ARCH-LM (5 retards)                 : p = 1.1e-08
```

Les rendements eux-mêmes n'ont, par construction, **aucune** mémoire dans leur moyenne ; leurs **carrés** (la variance) en ont beaucoup : le test de Ljung-Box appliqué aux carrés, et le test ARCH-LM (qui régresse $\varepsilon_t^2$ sur ses retards), rejettent massivement l'hypothèse de variance constante (p-valeurs de l'ordre de $10^{-22}$ et $10^{-8}$). Remarquez que le Ljung-Box appliqué aux rendements bruts rejette *aussi* faiblement (p-valeur d'environ 0,002) alors qu'il n'y a pas de mémoire en moyenne : ce test suppose une variance constante, et il est lui-même perturbé quand elle ne l'est pas. C'est une raison de plus de tester les carrés. Ajustons le GARCH(1,1) avec la bibliothèque `arch` :

```python
fit = arch_model(r, mean="Constant", vol="GARCH", p=1, q=1).fit(disp="off")
res = pd.DataFrame({"programmé": [mu, omega, alpha, beta], "estimé": fit.params.values, "erreur type": fit.std_err.values},
                   index=["mu", "omega", "alpha", "beta"])
print(res.round(3).to_string())
a_hat, b_hat, w_hat = fit.params["alpha[1]"], fit.params["beta[1]"], fit.params["omega"]
print("\npersistance alpha + beta :", round(a_hat + b_hat, 3), "(programmé 0,95) | variance de long terme estimée :", round(w_hat / (1 - a_hat - b_hat), 3), "(programmé 1)")

fv = fit.forecast(horizon=20).variance.iloc[-1].values
print("prévision de la variance aux horizons 1, 5, 10 et 20 jours :", fv[[0, 4, 9, 19]].round(3))
z = fit.resid / fit.conditional_volatility
print("diagnostic : Ljung-Box des résidus standardisés AU CARRÉ, p =", round(float(acorr_ljungbox(z ** 2, lags=[10])["lb_pvalue"].iloc[0]), 3))
```
<!--sortie-->
```text
       programmé  estimé  erreur type
mu          0.02   0.010        0.024
omega       0.05   0.041        0.013
alpha       0.10   0.070        0.014
beta        0.85   0.891        0.020

persistance alpha + beta : 0.961 (programmé 0,95) | variance de long terme estimée : 1.054 (programmé 1)
prévision de la variance aux horizons 1, 5, 10 et 20 jours : [0.735 0.782 0.83  0.903]
diagnostic : Ljung-Box des résidus standardisés AU CARRÉ, p = 0.548
```

Les estimations se rapprochent des vraies valeurs, avec des écarts de l'ordre de une à deux erreurs types ($\alpha$ est sous-estimé de deux erreurs types environ, $\beta$ surestimé d'autant : ils jouent des rôles voisins, comme $\varphi$ et $\theta$ en 4.2.3, et leurs erreurs se compensent). C'est la **persistance** $\alpha+\beta$ (0,961 pour 0,95) qui est bien estimée. Après ajustement, les résidus standardisés au carré n'ont plus de mémoire : le modèle a absorbé le regroupement de volatilité. La prévision de la variance **remonte lentement vers sa valeur de long terme** (d'environ 0,74 à un jour à 0,90 à vingt jours, pour une cible de 1,05) : comme la prévision d'un AR(1) (4.3.1) qui revient vers sa moyenne, mais lentement, car la persistance est proche de 1.

```python
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5.4), sharex=True)
ax1.plot(r, color=BLEU, lw=0.7)
ax1.set_ylabel("rendement (%)")
ax2.plot(np.sqrt(sig2), color="#898781", lw=1.6, label="volatilité programmée")
ax2.plot(fit.conditional_volatility, color=ORANGE, lw=1.2, label="volatilité estimée par le GARCH")
ax2.set_ylabel("écart-type conditionnel")
ax2.set_xlabel("jour")
ax2.legend(loc="upper right", fontsize=8)
for ax in (ax1, ax2):
    ax.grid(True, color="#e1e0d9", lw=0.6)
    ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("figures/ch04-garch.png", bbox_inches="tight")
```

![Rendements simulés (en haut), avec des périodes calmes et agitées, et volatilité conditionnelle (en bas) : la volatilité programmée (gris) et celle estimée par le GARCH (orange) se superposent presque.](figures/ch04-garch.png)

> ⚠️ **Ce que le GARCH modélise, et ce qu'il ne modélise pas.** Il prévoit la **variance** (donc l'incertitude, les intervalles de prévision, le risque), pas le niveau. Il est fondamental en gestion du risque financier (le volume V y reviendra). Sa validité repose sur l'hypothèse de loi (ici normale) pour les $z_t$ ; sur des données réelles, les queues sont souvent plus épaisses, et on utilise une loi de Student.

> ✅ **À retenir.**
> - Un **VAR($p$)** régresse chaque série sur les retards de **toutes** les séries ; il est stationnaire si les valeurs propres de la matrice (compagne) sont de module $<1$ ; les **réponses impulsionnelles** suivent la propagation d'un choc.
> - La **causalité de Granger** est une précédence prédictive, **pas** une causalité.
> - La **régression entre séries non stationnaires est trompeuse** : environ quatre fois sur cinq, deux marches aléatoires indépendantes paraissent « significativement » liées. Méfiance quand $R^2>$ Durbin-Watson.
> - **Cointégration** : deux séries intégrées dont une combinaison est stationnaire ; test d'Engle-Granger ; le **modèle à correction d'erreur** a pour coefficient de rappel $\alpha=\varphi-1$.
> - **GARCH(1,1)** : $\sigma_t^2=\omega+\alpha\varepsilon_{t-1}^2+\beta\sigma_{t-1}^2$ ; variance de long terme $\omega/(1-\alpha-\beta)$ ; il modélise la volatilité qui se regroupe. Les rendements ont peu de mémoire, leurs **carrés** beaucoup.


## 4.5 ➕ Pour aller plus loin : modèles d'espace d'états et filtre de Kalman

> 🧭 **Section optionnelle.** Elle ne demande aucun prérequis nouveau (seulement le chapitre 1 de ce volume et la section 4.2), mais elle est plus abstraite que le reste du chapitre. Elle vaut le détour : les modèles ARIMA de 4.2 sont **un cas particulier** de ce cadre, et le **filtre de Kalman** que vous allez construire est l'algorithme qui a calculé, en coulisses, toutes les vraisemblances de `SARIMAX`.

### 4.5.1 L'idée : un état caché, des observations bruitées

Yasmine voudrait connaître le **niveau réel** de ses ventes, c'est-à-dire ce que serait son chiffre d'affaires sans les accidents du mois (une grosse commande, un jour de pluie). Elle n'observe que le chiffre d'affaires du mois, qui est **le niveau réel plus du bruit**. Le niveau réel, lui, évolue lentement. C'est un problème à **deux niveaux** :

- une **équation d'observation** : ce que l'on mesure, $y_t=\mu_t+\varepsilon_t$, avec $\varepsilon_t\sim\mathcal N(0,\sigma_\varepsilon^2)$ ;
- une **équation d'état** : comment l'état caché évolue, $\mu_{t+1}=\mu_t+\eta_t$, avec $\eta_t\sim\mathcal N(0,\sigma_\eta^2)$.

C'est le **modèle de niveau local** (*local level*). Le niveau $\mu_t$ est une marche aléatoire (il dérive sans retour), que l'on n'observe qu'à travers le bruit $\varepsilon_t$. Tout le problème est de **reconstituer** $\mu_t$ à partir des $y_t$ : c'est le rôle du **filtre de Kalman**. L'idée se généralise à un état de plusieurs composantes (niveau, pente, saison, régression), et à des observations manquantes ; nous verrons les deux.

### 4.5.2 Le filtre de Kalman, à la main

À chaque date, le filtre maintient une **croyance** sur l'état : une loi normale $\mathcal N(a,P)$ dont $a$ est la meilleure estimation et $P$ l'incertitude. Il alterne deux gestes.

1. **Prédiction.** Entre deux dates, le niveau dérive : l'estimation ne bouge pas ($a_{t+1|t}=a_{t|t}$) mais l'incertitude grandit : $P_{t+1|t}=P_{t|t}+\sigma_\eta^2$.
2. **Mise à jour.** On observe $y_t$. L'**innovation** $v_t=y_t-a_{t|t-1}$ est la surprise (ce que l'on n'avait pas prévu). On corrige l'estimation d'une fraction $K_t$ de cette surprise :
$$a_{t|t}=a_{t|t-1}+K_t\,v_t,\qquad K_t=\frac{P_{t|t-1}}{P_{t|t-1}+\sigma_\varepsilon^2},\qquad P_{t|t}=(1-K_t)\,P_{t|t-1}.$$

Le coefficient $K_t$ s'appelle le **gain de Kalman**. Il vaut entre 0 et 1 et arbitre entre deux sources d'information : l'ancienne croyance (si elle est incertaine, $P$ grand, $K$ proche de 1 : on se fie à la mesure) et la mesure (si elle est bruyante, $\sigma_\varepsilon^2$ grand, $K$ proche de 0 : on se fie à l'ancienne croyance).

> 📐 **D'où vient la formule ?** C'est le calcul bayésien le plus simple : un a priori normal $\mathcal N(a,P)$ sur $\mu$, une mesure $y=\mu+\varepsilon$ avec $\varepsilon\sim\mathcal N(0,\sigma^2)$. La loi *a posteriori* de $\mu$ est normale, de précision (inverse de la variance) **égale à la somme des précisions** : $\dfrac1{P_{\text{post}}}=\dfrac1P+\dfrac1{\sigma^2}$, d'où $P_{\text{post}}=\dfrac{P\sigma^2}{P+\sigma^2}=(1-K)P$ ; et de moyenne égale à la **moyenne des deux informations pondérée par leur précision** : $a_{\text{post}}=\dfrac{a/P+y/\sigma^2}{1/P+1/\sigma^2}=a+K(y-a)$. Le filtre de Kalman est donc une mise à jour bayésienne répétée, avec une étape de « vieillissement » entre deux (nous reverrons ce principe au chapitre 6).

> 💡 **Exemple à la main.** Prenons $\sigma_\varepsilon^2=4$, $\sigma_\eta^2=1$, et une croyance initiale $\mathcal N(100,\,5)$ sur le niveau avant la première mesure. On observe $y_1=103$, $y_2=101$, $y_3=106$.
>
> **Date 1.** $a_{1|0}=100$, $P_{1|0}=5$. Variance de l'innovation : $F_1=P+\sigma_\varepsilon^2=9$. Gain $K_1=5/9=0{,}5556$. Surprise $v_1=103-100=3$. Donc $a_{1|1}=100+0{,}5556\times3=101{,}667$ et $P_{1|1}=5\times(1-0{,}5556)=2{,}222$.
> **Date 2.** Prédiction : $a_{2|1}=101{,}667$, $P_{2|1}=2{,}222+1=3{,}222$. $F_2=7{,}222$, $K_2=3{,}222/7{,}222=0{,}4462$. Surprise $v_2=101-101{,}667=-0{,}667$. Donc $a_{2|2}=101{,}667+0{,}4462\times(-0{,}667)=101{,}369$ et $P_{2|2}=3{,}222\times(1-0{,}4462)=1{,}785$.
> **Date 3.** $P_{3|2}=2{,}785$, $F_3=6{,}785$, $K_3=0{,}4104$, $v_3=106-101{,}369=4{,}631$, $a_{3|3}=101{,}369+0{,}4104\times4{,}631=103{,}270$, $P_{3|3}=1{,}642$.
>
> Observez deux choses : le gain **diminue** (0,56 puis 0,45 puis 0,41) à mesure que l'on en sait plus, et l'incertitude $P_{t|t}$ diminue aussi.

### 4.5.3 Le filtre de Kalman en numpy, et comparaison avec statsmodels

Voici le filtre complet pour le niveau local. Il traite aussi les **observations manquantes** (une valeur `NaN`) : on ne fait alors **que la prédiction**, sans mise à jour, et l'incertitude grandit. À chaque étape, il cumule la **log-vraisemblance** gaussienne des innovations (c'est ce qu'optimisent les logiciels pour estimer les variances).

```python
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.structural import UnobservedComponents

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"

def kalman_niveau_local(y, s2_eps, s2_eta, a0, P0):
    """Filtre de Kalman du niveau local. (a0, P0) = croyance sur le niveau AVANT la première observation."""
    n = len(y)
    sortie = {k: np.zeros(n) for k in ["a_pred", "P_pred", "F", "K", "v", "a_filtre", "P_filtre"]}
    a, P, loglik = a0, P0, 0.0
    for t in range(n):
        sortie["a_pred"][t], sortie["P_pred"][t] = a, P
        if np.isnan(y[t]):                                    # observation manquante : pas de mise à jour
            sortie["F"][t] = sortie["K"][t] = sortie["v"][t] = np.nan
            a_f, P_f = a, P
        else:
            F = P + s2_eps                                    # variance de l'innovation
            v = y[t] - a                                      # innovation (surprise)
            K = P / F                                         # gain de Kalman
            a_f, P_f = a + K * v, P * (1 - K)
            loglik += -0.5 * (np.log(2 * np.pi * F) + v ** 2 / F)
            sortie["F"][t], sortie["K"][t], sortie["v"][t] = F, K, v
        sortie["a_filtre"][t], sortie["P_filtre"][t] = a_f, P_f
        a, P = a_f, P_f + s2_eta                              # prédiction pour la date suivante
    sortie["loglik"] = loglik
    return sortie

obs = np.array([103.0, 101.0, 106.0])
r = kalman_niveau_local(obs, s2_eps=4.0, s2_eta=1.0, a0=100.0, P0=5.0)
print(pd.DataFrame({k: r[k] for k in ["a_pred", "P_pred", "F", "K", "v", "a_filtre", "P_filtre"]}, index=[1, 2, 3]).round(4).to_string())

# la même chose avec statsmodels, avec la même croyance initiale connue
mod = UnobservedComponents(obs, level="llevel")
mod.ssm.initialize_known(np.array([100.0]), np.array([[5.0]]))
mod.ssm.loglikelihood_burn = 0                               # par défaut, statsmodels ignore le 1er terme de la vraisemblance
res_sm = mod.smooth([4.0, 1.0])                              # variances : irrégulière (4), niveau (1)
print("\nétat filtré statsmodels      :", res_sm.filtered_state[0].round(4), "| variances filtrées :", res_sm.filtered_state_cov[0, 0].round(4))
print("log-vraisemblance : numpy =", round(r["loglik"], 4), "| statsmodels =", round(res_sm.llf, 4))
```
<!--sortie-->
```text
     a_pred  P_pred       F       K       v  a_filtre  P_filtre
1  100.0000  5.0000  9.0000  0.5556  3.0000  101.6667    2.2222
2  101.6667  3.2222  7.2222  0.4462 -0.6667  101.3692    1.7846
3  101.3692  2.7846  6.7846  0.4104  4.6308  103.2698    1.6417

état filtré statsmodels      : [101.6667 101.3692 103.2698] | variances filtrées : [2.2222 1.7846 1.6417]
log-vraisemblance : numpy = -7.9124 | statsmodels = -7.9124
```

Le filtre écrit en numpy retrouve les valeurs calculées à la main (101,667 ; 101,369 ; 103,270) et celles de `statsmodels`, **à la quatrième décimale**, y compris la log-vraisemblance.

#### Estimer les variances

Dans la pratique, on ne connaît pas $\sigma_\varepsilon^2$ ni $\sigma_\eta^2$ : on les **estime par maximum de vraisemblance**. Testons sur un niveau local **simulé** de 200 points (variances programmées : 4 et 1) :

```python
rng = np.random.default_rng(5)
n = 200
niveau = 100 + np.cumsum(rng.normal(0, 1.0, n))               # sigma_eta = 1
y_sim = niveau + rng.normal(0, 2.0, n)                        # sigma_eps = 2

mod = UnobservedComponents(y_sim, level="llevel")
ajust = mod.fit(disp=False)
print(pd.DataFrame({"programmé": [4.0, 1.0], "estimé": ajust.params, "erreur type": ajust.bse},
                   index=["variance du bruit d'observation", "variance du niveau"]).round(3).to_string())

```
<!--sortie-->
```text
                                 programmé  estimé  erreur type
variance du bruit d'observation        4.0   3.051        0.445
variance du niveau                     1.0   1.453        0.382
```

> ⚠️ **Estimer deux variances est difficile.** Les estimations sont dans la bonne région (3,05 pour 4 et 1,45 pour 1) mais avec de **grandes erreurs types** (la variance d'observation est sous-estimée d'environ deux erreurs types) : à partir de la seule série, la part du « bruit de mesure » et celle de la « vraie dérive » du niveau sont difficiles à séparer, comme $\varphi$ et $\theta$ en 4.2.3. Seul le **rapport** $q=\sigma_\eta^2/\sigma_\varepsilon^2$ gouverne le comportement du filtre (nous le voyons ci-dessous), ce qui limite l'effet de cette incertitude sur les prévisions.

### 4.5.4 Régime permanent et lissage exponentiel

Quand le filtre a tourné assez longtemps, le gain $K_t$ **se stabilise** à une valeur $K_\infty$. Calculons-la pour $\sigma_\varepsilon^2=4$ et $\sigma_\eta^2=1$ : en régime permanent, la variance prédite $p=P_{t+1|t}$ vérifie $p=\dfrac{p\,\sigma_\varepsilon^2}{p+\sigma_\varepsilon^2}+\sigma_\eta^2$. En multipliant par $p+4$ : $p(p+4)=4p+(p+4)$, soit $p^2-p-4=0$, d'où $p=\dfrac{1+\sqrt{17}}2\approx2{,}562$ et $K_\infty=\dfrac p{p+4}\approx0{,}390$.

Or, une fois $K$ constant, la mise à jour devient $a_{t|t}=a_{t-1|t-1}+K\,(y_t-a_{t-1|t-1})=K\,y_t+(1-K)\,a_{t-1|t-1}$ : exactement le **lissage exponentiel simple** de paramètre $\alpha=K_\infty$ (la moyenne mobile exponentielle bien connue des prévisionnistes). Le lissage exponentiel est donc le filtre de Kalman d'un niveau local en régime permanent. Vérifions-le numériquement :

```python
r = kalman_niveau_local(y_sim, 4.0, 1.0, a0=100.0, P0=25.0)
p = (1 + np.sqrt(17)) / 2
print("gain final du filtre :", round(r["K"][-1], 5), "| théorie p/(p+4) :", round(p / (p + 4), 5))

alpha = p / (p + 4)
lisse = np.zeros(n)
lisse[0] = r["a_filtre"][0]
for t in range(1, n):
    lisse[t] = alpha * y_sim[t] + (1 - alpha) * lisse[t - 1]
print("écart maximal lissage exponentiel / filtre de Kalman, après 30 pas :", f"{np.abs(lisse[30:] - r['a_filtre'][30:]).max():.1e}")
```
<!--sortie-->
```text
gain final du filtre : 0.39039 | théorie p/(p+4) : 0.39039
écart maximal lissage exponentiel / filtre de Kalman, après 30 pas : 2.2e-07
```

Le gain converge vers sa valeur théorique, et le lissage exponentiel avec $\alpha=0{,}39$ **est** le filtre de Kalman une fois le régime permanent atteint (écart de l'ordre de $10^{-7}$). Plus le niveau bouge vite par rapport au bruit ($q$ grand), plus $K_\infty$ est grand : le filtre « oublie » vite le passé.

### 4.5.5 Un modèle structurel pour les ventes de Dar Jasmin

L'intérêt des modèles d'espace d'états est de **mettre bout à bout** des composantes comprises : un niveau, une pente, une saison, des variables explicatives. C'est ce qu'on appelle un **modèle structurel**. Pour nos ventes (en logarithme, 96 mois d'apprentissage), prenons un niveau, une pente, une saison de période 12 et les variables `promo` et `covid`. Pour commencer, laissons la pente évoluer aléatoirement (le « *local linear trend* » classique) :

```python
v = pd.read_csv("donnees/ventes_mensuelles.csv", parse_dates=["mois"]).set_index("mois")
v.index.freq = "MS"
y = np.log(v["ca"])
train, test = y[:"2023-12"], y["2024-01":]
X = v[["promo", "covid"]].astype(float)
Xtr, Xte = X[:"2023-12"], X["2024-01":]

mod_lt = UnobservedComponents(train, exog=Xtr, level="lltrend", seasonal=12, stochastic_seasonal=False)
fit_lt = mod_lt.fit(disp=False, maxiter=300)
print(pd.Series(fit_lt.params, index=mod_lt.param_names).round(5).to_string())
```
<!--sortie-->
```text
sigma2.irregular    0.00141
sigma2.level        0.00276
sigma2.trend        0.00000
beta.promo          0.11356
beta.covid         -0.54473
```

L'estimation donne une **variance de la pente égale à zéro** (`sigma2.trend`) : les données disent que la pente est **constante**. Le modèle se simplifie alors en un niveau qui dérive à vitesse constante plus un bruit de niveau (en langage statsmodels : `level="rwdrift"`, une marche aléatoire avec dérive). Gardons ce modèle, plus simple, avec une saison **déterministe** (profil fixe), et regardons ce qu'il estime et comment il prévoit les 24 mois de test :

```python
mod_ss = UnobservedComponents(train, exog=Xtr, level="rwdrift", seasonal=12, stochastic_seasonal=False)
fit_ss = mod_ss.fit(disp=False, maxiter=300)
print(pd.Series(fit_ss.params, index=mod_ss.param_names).round(4).to_string())

prev_ss = fit_ss.get_forecast(24, exog=Xte).predicted_mean
print("\nRMSE (log) sur les 24 mois de test :", round(np.sqrt(np.mean((test - prev_ss) ** 2)), 4),
      "| biais (y - prévision) :", round(float(np.mean(test - prev_ss)), 4))
print("pour comparaison (4.3) : modèle B 0,0738 ; naïf avec dérive 0,0849 ; modèle A 0,0997 ; modèle C 0,1008")
```
<!--sortie-->
```text
sigma2.level    0.0054
beta.promo      0.1090
beta.covid     -0.5263

RMSE (log) sur les 24 mois de test : 0.0819 | biais (y - prévision) : -0.0364
pour comparaison (4.3) : modèle B 0,0738 ; naïf avec dérive 0,0849 ; modèle A 0,0997 ; modèle C 0,1008
```

Le modèle structurel a une erreur de test d'environ 0,082, entre celle du modèle B (0,074) et celle des modèles A et C (environ 0,10). Il estime que l'effet de la promotion vaut environ $+0{,}11$ et celui du COVID environ $-0{,}53$, des valeurs voisines de celles de 4.2. Voyons les composantes que l'on peut **lire** dans ce modèle : le niveau lissé (la « vraie » tendance, débarrassée de la saison et du bruit) et le profil saisonnier.

```python
noms = mod_ss.state_names                                                         # noms des composantes de l'état caché
niveau_lisse = pd.Series(fit_ss.smoothed_state[noms.index("level")], index=train.index)         # composante de niveau
saison_lisse = pd.Series(fit_ss.smoothed_state[noms.index("seasonal")], index=train.index)       # composante saisonnière à la date t
print("composantes de l'état :", noms[:4], "...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.6), gridspec_kw={"width_ratios": [1.5, 1]})
ax1.plot(train.index, train, color="#c3c2b7", lw=1.2, label="log(ca) observé")
ax1.plot(niveau_lisse.index, niveau_lisse, color=VIOLET, lw=2.2, label="niveau lissé (filtre de Kalman)")
ax1.set_title("Le niveau réel, débarrassé de la saison et du bruit", fontsize=10)
ax1.legend(fontsize=8, loc="upper left")
profil = saison_lisse["2023-01":"2023-12"]
ax2.bar(range(1, 13), 100 * (np.exp(profil.values) - 1), color=AQUA)
ax2.set_xticks(range(1, 13))
ax2.set_xticklabels(["j", "f", "m", "a", "m", "j", "j", "a", "s", "o", "n", "d"])
ax2.set_title("Profil saisonnier (écart au niveau, en %)", fontsize=10)
ax2.axhline(0, color="#898781", lw=0.8)
for ax in (ax1, ax2):
    ax.grid(True, color="#e1e0d9", lw=0.6)
    ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("figures/ch04-structurel.png", bbox_inches="tight")
print("écart de décembre au niveau :", round(100 * (np.exp(profil.iloc[-1]) - 1)), "% ; de janvier :", round(100 * (np.exp(profil.iloc[0]) - 1)), "%")
```
<!--sortie-->
```text
composantes de l'état : ['level', 'trend', 'seasonal', 'seasonal.L1'] ...
écart de décembre au niveau : 59 % ; de janvier : -38 %
```

![À gauche : le logarithme du chiffre d'affaires (gris) et le niveau lissé par le filtre de Kalman (violet) qui en retire la saison et le bruit. À droite : le profil saisonnier estimé, avec le pic de décembre et le creux de janvier.](figures/ch04-structurel.png)

### 4.5.6 Combler un trou : les données manquantes

Un atout décisif du filtre de Kalman est de traiter les **observations manquantes** sans bricolage : à une date sans mesure, il ne fait que prédire (l'incertitude grandit), et le **lissage** (qui utilise aussi l'avenir) reconstitue la valeur manquante avec son intervalle d'incertitude. Un cas réaliste : les registres de Yasmine ont perdu les ventes de **mars à août 2022**. Nous effaçons ces six mois de la série d'apprentissage (nous connaissons les vraies valeurs, ce qui permet de vérifier), ajustons le modèle sur ce qui reste, puis **reconstituons** les mois manquants.

```python
trou = train["2022-03":"2022-08"].index
vraies = train[trou].copy()
train_trou = train.copy()
train_trou[trou] = np.nan

mod_na = UnobservedComponents(train_trou, exog=Xtr, level="rwdrift", seasonal=12, stochastic_seasonal=False)
fit_na = mod_na.fit(disp=False, maxiter=300)
lissage = fit_na.smoother_results
estim = pd.Series(lissage.smoothed_forecasts[0], index=train.index)[trou]
se = pd.Series(np.sqrt(lissage.smoothed_forecasts_error_cov[0, 0]), index=train.index)[trou]

# deux méthodes sans modèle, pour comparer : interpolation linéaire, et « même mois l'an dernier » corrigé de la croissance annuelle
lineaire = pd.Series(np.interp(np.arange(6), [-1, 6], [train["2022-02"].iloc[0], train["2022-09"].iloc[0]]), index=trou)
croissance = (train - train.shift(12))[:"2022-02"].mean()
an_dernier = pd.Series(train.shift(12)[trou].values + croissance, index=trou)

tab = pd.DataFrame({"vrai (log)": vraies, "Kalman": estim, "± 1,96 se": 1.96 * se, "interp. linéaire": lineaire, "an dernier + croiss.": an_dernier})
print(tab.round(3).to_string())
rmse = lambda a, b: np.sqrt(np.mean((a - b) ** 2))
print("\nRMSE de reconstitution (log) : Kalman =", round(rmse(vraies, estim), 3), "| interpolation linéaire =", round(rmse(vraies, lineaire), 3),
      "| an dernier corrigé =", round(rmse(vraies, an_dernier), 3))
print("mois réels dans l'intervalle à 95 % de Kalman :", int(((vraies >= estim - 1.96 * se) & (vraies <= estim + 1.96 * se)).sum()), "sur 6")
```
<!--sortie-->
```text
            vrai (log)  Kalman  ± 1,96 se  interp. linéaire  an dernier + croiss.
mois                                                                             
2022-03-01       7.400   7.371      0.142             7.127                 7.491
2022-04-01       7.553   7.442      0.183             7.182                 7.553
2022-05-01       7.711   7.550      0.201             7.238                 7.706
2022-06-01       7.667   7.661      0.201             7.293                 7.881
2022-07-01       7.803   7.722      0.183             7.349                 7.909
2022-08-01       7.717   7.674      0.142             7.404                 7.701

RMSE de reconstitution (log) : Kalman = 0.089 | interpolation linéaire = 0.383 | an dernier corrigé = 0.104
mois réels dans l'intervalle à 95 % de Kalman : 6 sur 6
```

Le filtre reconstitue les six mois avec une erreur quadratique moyenne de 0,09 en logarithme (soit 9 %) et les six vraies valeurs tombent dans son intervalle à 95 %, plus large au milieu du trou (là où l'on est le plus loin des mesures). C'est bien mieux que l'**interpolation linéaire** (0,38), qui ignore la saison et lisse une bosse qui existe réellement. La comparaison avec la méthode « l'an dernier corrigé de la croissance » (0,10) est plus serrée : elle utilise déjà la saison, mais pas l'information des mois qui entourent le trou. Les écarts du filtre ne sont pas nuls : la plus grosse erreur, en mai, est d'environ 0,16.

> ✅ **À retenir.**
> - Un **modèle d'espace d'états** distingue un **état caché** (niveau, pente, saison…) qui évolue, et des **observations bruitées**. Les ARIMA en sont un cas particulier.
> - Le **filtre de Kalman** alterne **prédiction** (l'incertitude grandit) et **mise à jour** : $a\leftarrow a+K(y-a)$, avec le **gain** $K=P/(P+\sigma_\varepsilon^2)$ qui arbitre entre ancienne croyance et mesure. C'est une mise à jour bayésienne répétée.
> - Il fournit aussi la **log-vraisemblance** des données : c'est elle qui sert à estimer les paramètres (variances), dans `SARIMAX` comme dans `UnobservedComponents`.
> - En régime permanent, le filtre d'un niveau local **est** un lissage exponentiel de paramètre $\alpha=K_\infty$.
> - Les **modèles structurels** assemblent niveau, pente, saison et variables explicatives en composantes lisibles ; ici, l'estimation de la variance de la pente à zéro a simplifié le modèle.
> - Les **observations manquantes** se traitent naturellement (prédire sans mettre à jour, puis lisser), avec une incertitude honnête.


## 4.6 ➕ Pour aller plus loin : Prophet et les bibliothèques modernes de prévision

> 🧭 **Section optionnelle.** Elle répond à une question que se posent beaucoup de lecteurs : « Et les bibliothèques à la mode, qui font tout en trois lignes ? ». Réponse en trois temps : comprendre ce qu'elles font **vraiment** (4.6.1 et 4.6.2), les **évaluer honnêtement** comme les autres (4.6.3), et savoir où chercher la suite (4.6.4).

### 4.6.1 Prophet : l'idée

**Prophet** est une bibliothèque de prévision publiée par des ingénieurs de Facebook (Taylor et Letham, 2018), conçue pour des séries d'entreprise avec des saisons marquées, des jours fériés et des ruptures de tendance. Son modèle est **additif** :

$$y(t)=g(t)+s(t)+h(t)+\varepsilon_t,$$

avec **$g(t)$** une tendance **linéaire par morceaux** (la pente peut changer en quelques dates candidates, les *points de rupture*, avec une pénalisation qui évite que toutes les ruptures soient utilisées), **$s(t)$** une saisonnalité décrite par une **série de Fourier** (une somme de sinus et de cosinus de période 1 an : $\sum_k a_k\sin(2\pi kt/P)+b_k\cos(2\pi kt/P)$), et **$h(t)$** l'effet d'événements (jours fériés, promotions) ou de variables explicatives. L'ajustement est bayésien (les coefficients ont des lois a priori ; l'estimation se fait avec le logiciel Stan), et les intervalles de prévision sont obtenus par simulation.

Rien de magique donc : c'est une **régression linéaire** sur des variables bien construites (la tendance par morceaux, les termes de Fourier, les événements), assortie d'une pénalisation, exactement dans l'esprit du chapitre 1 (section 1.5 : la régularisation). Voici le code typique, tel qu'on le trouve dans la documentation de la bibliothèque :

```python noexec
from prophet import Prophet

df = v.reset_index().rename(columns={"mois": "ds"})        # Prophet attend les colonnes « ds » (date) et « y »
df["y"] = np.log(df["ca"])
m = Prophet(yearly_seasonality=6, weekly_seasonality=False, daily_seasonality=False,
            changepoint_prior_scale=0.05)                   # nombre de termes de Fourier ; souplesse de la tendance
m.add_regressor("promo")
m.add_regressor("covid")
m.fit(df[df["ds"] < "2024-01-01"])
futur = m.make_future_dataframe(periods=24, freq="MS")
futur = futur.merge(df[["ds", "promo", "covid"]], on="ds")
prevision = m.predict(futur)                                # colonnes yhat, yhat_lower, yhat_upper, trend, yearly...
```

> ⚠️ **Ce bloc n'est pas exécuté.** La bibliothèque Prophet n'est pas installée dans l'environnement qui a produit ce livre (elle nécessite le compilateur Stan) : le code ci-dessus est donné **à titre d'illustration**, d'après la documentation ; les noms d'arguments peuvent différer selon la version, et vous devrez le vérifier chez vous. Les résultats chiffrés de cette section ne viennent **pas** de Prophet, mais du modèle équivalent écrit à la main ci-dessous.

### 4.6.2 Le même modèle, écrit à la main

Pour comprendre, le plus sûr est de **construire** le modèle. Nous ajustons, sur $\log(\text{ca})$ :

- une **tendance linéaire par morceaux** : $g(t)=k+a\,t+\sum_j\delta_j\max(0,\,t-s_j)$, où les $s_j$ sont 20 points de rupture candidats et chaque $\delta_j$ est le changement de pente en $s_j$. Les $\delta_j$ sont **pénalisés** (régression ridge, chapitre 1, section 1.5), de sorte que la pente ne change que si les données l'exigent ;
- une **saisonnalité de Fourier** à $K$ harmoniques : $s(t)=\sum_{k=1}^{K}[a_k\sin(2\pi k\,m/12)+b_k\cos(2\pi k\,m/12)]$, où $m$ est le numéro du mois ;
- les variables explicatives `promo` et `covid`.

C'est une régression linéaire pénalisée : les moindres carrés avec un terme $\lambda\sum\delta_j^2$. Deux réglages à choisir : le nombre $K$ d'harmoniques et la pénalité $\lambda$. Plutôt que de les fixer au hasard, on les **valide** : on apprend sur les 72 premiers mois de l'apprentissage et on évalue sur les 24 suivants (toujours dans la période d'apprentissage : le test de 2024-2025 reste intact).

```python
import warnings
warnings.filterwarnings("ignore")
import itertools
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.structural import UnobservedComponents

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
v = pd.read_csv("donnees/ventes_mensuelles.csv", parse_dates=["mois"]).set_index("mois")
v.index.freq = "MS"
y = np.log(v["ca"])
train, test = y[:"2023-12"], y["2024-01":]
X = v[["promo", "covid"]].astype(float)
temps = np.arange(120.0)                                       # 0 = janvier 2016
num_mois = v.index.month.values.astype(float)
Xv = X.values

def colonnes(i_t, i_mois, K, ruptures, promo, covid):
    t = i_t / 120.0
    fourier = []
    for k in range(1, K + 1):
        for f in (np.sin, np.cos):
            c = f(2 * np.pi * k * i_mois / 12)
            if np.abs(c).max() > 1e-9:                         # pour k = 6, sin(pi m) est identiquement nul : on l'écarte
                fourier.append(c)
    base = [np.ones_like(t), t] + fourier + [promo, covid]
    sauts = [np.maximum(0.0, t - s / 120.0) for s in ruptures]
    return np.column_stack(base + sauts), len(base)           # (matrice, nombre de colonnes NON pénalisées)

def ajuster_predire(y_app, i_app, i_prev, m_app, m_prev, X_app, X_prev, K, lam, n_rupt=20):
    ruptures = np.linspace(6, 0.85 * len(i_app), n_rupt)      # points de rupture candidats dans les 85 % premiers de l'apprentissage
    A, nb = colonnes(i_app, m_app, K, ruptures, X_app[:, 0], X_app[:, 1])
    B, _ = colonnes(i_prev, m_prev, K, ruptures, X_prev[:, 0], X_prev[:, 1])
    pen = np.zeros(A.shape[1])
    pen[nb:] = 1.0                                             # on ne pénalise que les changements de pente
    # moindres carrés pénalisés, résolus de façon stable : on empile sqrt(lambda) * pénalité sous la matrice de dessin
    A_aug = np.vstack([A, np.sqrt(lam) * np.diag(pen)])
    y_aug = np.r_[y_app, np.zeros(A.shape[1])]
    beta = np.linalg.lstsq(A_aug, y_aug, rcond=None)[0]
    return B @ beta, A @ beta

lignes = []
for K, lam in itertools.product((1, 2, 3, 4, 5, 6), (0.001, 0.01, 0.1, 1, 10)):
    f, _ = ajuster_predire(train.values[:72], temps[:72], temps[72:96], num_mois[:72], num_mois[72:96], Xv[:72], Xv[72:96], K, lam)
    lignes.append({"K": K, "lambda": lam, "RMSE": np.sqrt(np.mean((train.values[72:96] - f) ** 2))})
grille = pd.DataFrame(lignes)
print("RMSE (log) de validation, sur les 24 derniers mois de l'apprentissage :")
print(grille.pivot(index="K", columns="lambda", values="RMSE").round(3).to_string())
meilleur = grille.sort_values("RMSE").iloc[0]
K_opt, lam_opt = int(meilleur["K"]), float(meilleur["lambda"])
print(f"\nréglage retenu : K = {K_opt} harmoniques, lambda = {lam_opt}  (RMSE de validation : {meilleur['RMSE']:.3f})")
```
<!--sortie-->
```text
RMSE (log) de validation, sur les 24 derniers mois de l'apprentissage :
lambda  0.001   0.010   0.100   1.000   10.000
K                                             
1        0.386   0.347   0.323   0.307   0.293
2        0.294   0.284   0.277   0.271   0.260
3        0.183   0.190   0.197   0.199   0.192
4        0.133   0.125   0.133   0.145   0.141
5        0.139   0.096   0.099   0.112   0.110
6        0.153   0.094   0.090   0.104   0.103

réglage retenu : K = 6 harmoniques, lambda = 0.1  (RMSE de validation : 0.090)
```

Lecture de la grille. Avec **peu d'harmoniques** ($K=1$ à $3$), la saison est trop lisse : une seule ondulation sinusoïdale ne peut pas reproduire le **pic étroit de décembre** et le creux de janvier, et l'erreur de validation est grande (de 0,18 à 0,39). Il en faut davantage : l'erreur chute pour $K=4$ puis atteint son minimum pour $K=6$. Or $K=6$ harmoniques sur des données mensuelles équivaut à **un effet libre pour chaque mois** (12 paramètres au total), comme les 11 indicatrices de 4.2.7 : c'est la limite du système. Sur des données quotidiennes, 10 harmoniques suffisent à décrire un profil annuel détaillé ; avec seulement 12 points par an, il ne reste rien à *lisser*.

Refaisons l'ajustement sur les 96 mois et prévoyons les 24 mois de test :

```python
f_test, ajuste = ajuster_predire(train.values, temps[:96], temps[96:], num_mois[:96], num_mois[96:], Xv[:96], Xv[96:], K_opt, lam_opt)
print("RMSE (log) sur les 24 mois de test :", round(np.sqrt(np.mean((test.values - f_test) ** 2)), 4),
      "| biais (y - prévision) :", round(float(np.mean(test.values - f_test)), 4))
print("pour comparaison (4.3) : modèle B 0,0738 ; naïf avec dérive 0,0849 ; modèle A 0,0997 ; modèle C 0,1008")
print("RMSE d'ajustement sur l'apprentissage :", round(np.sqrt(np.mean((train.values - ajuste) ** 2)), 4))

fig, ax = plt.subplots(figsize=(10, 3.6))
ax.plot(train.index, train, color="#c3c2b7", lw=1.3, label="log(ca) observé (apprentissage)")
ax.plot(train.index, ajuste, color=VIOLET, lw=1.6, label="ajustement (tendance par morceaux + Fourier)")
ax.plot(test.index, test, color=BLEU, lw=1.6, label="log(ca) observé (test)")
ax.plot(test.index, f_test, color=ORANGE, lw=1.8, label="prévision")
ax.legend(fontsize=8, loc="upper left")
ax.grid(True, color="#e1e0d9", lw=0.6)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("figures/ch04-fourier.png", bbox_inches="tight")
```
<!--sortie-->
```text
RMSE (log) sur les 24 mois de test : 0.0801 | biais (y - prévision) : 0.0173
pour comparaison (4.3) : modèle B 0,0738 ; naïf avec dérive 0,0849 ; modèle A 0,0997 ; modèle C 0,1008
RMSE d'ajustement sur l'apprentissage : 0.0679
```

![Modèle de type Prophet écrit à la main : ajustement sur l'apprentissage (violet) et prévision des 24 mois de test (orange), comparés aux observations (gris puis bleu).](figures/ch04-fourier.png)

Le modèle fait presque aussi bien que le meilleur des modèles de 4.3 sur la fenêtre de test (RMSE de 0,080 contre 0,074 pour B, et mieux que A, C et le naïf avec dérive en log). Ce que fait Prophet, au fond, ce n'est pas de la magie : c'est cela, avec des a priori bayésiens, des intervalles simulés, et une interface qui évite d'écrire la matrice de dessin.

### 4.6.3 Évaluation honnête : tout le monde au même concours

Un nouveau venu doit passer **le même concours** que les autres, sans faveur. Nous ajoutons donc à la validation à origine glissante de 4.3.6 deux nouveaux concurrents : le **modèle de type Prophet** que nous venons de construire (avec les réglages $K$ et $\lambda$ retenus *sur l'apprentissage*), et le **modèle structurel** de 4.5.5. On reprend les objets de 4.3 (`P`, `reel`, `origines`, `H`, `y`, `X`) et on y ajoute deux séries de prévisions.

```python
def prev_fourier(i):
    f, _ = ajuster_predire(y.values[:i], temps[:i], temps[i:i + H], num_mois[:i], num_mois[i:i + H], Xv[:i], Xv[i:i + H], K_opt, lam_opt)
    return f

def prev_structurel(i):
    m = UnobservedComponents(y.iloc[:i], exog=X.iloc[:i], level="rwdrift", seasonal=12, stochastic_seasonal=False).fit(disp=False, maxiter=300)
    return m.forecast(H, exog=X.iloc[i:i + H]).values

P["type Prophet (Fourier + tendance par morceaux)"] = np.array([prev_fourier(i) for i in origines])
P["modèle structurel (niveau local + saison)"] = np.array([prev_structurel(i) for i in origines])

lignes = []
for nom, f in P.items():
    e = reel - f
    lignes.append({"modèle": nom, "RMSE global": np.sqrt((e ** 2).mean()), "h = 1": np.sqrt((e[:, 0] ** 2).mean()),
                   "h = 12": np.sqrt((e[:, 11] ** 2).mean()), "biais": e.mean()})
tableau_final = pd.DataFrame(lignes).set_index("modèle").sort_values("RMSE global")
print("validation à origine glissante (13 origines, 12 horizons), RMSE en logarithme :")
print(tableau_final.round(4).to_string())

fig, ax = plt.subplots(figsize=(9, 3.8))
ordre = tableau_final.index[::-1]
couleurs = [AQUA if "Prophet" in n else (ORANGE if n.startswith(("A", "B", "C", "comb")) else "#898781") for n in ordre]
ax.barh(range(len(ordre)), tableau_final.loc[ordre, "RMSE global"], color=couleurs)
ax.set_yticks(range(len(ordre)))
ax.set_yticklabels(ordre, fontsize=8)
ax.set_xlabel("RMSE global (en logarithme) : plus petit = meilleur")
ax.axvline(0.0715, color=ROUGE, ls="--", lw=1.1)
ax.text(0.0722, len(ordre) - 1, "écart-type du bruit à long terme (0,0715)", color=ROUGE, fontsize=8, va="center")
ax.spines[["top", "right"]].set_visible(False)
ax.grid(True, axis="x", color="#e1e0d9", lw=0.6)
plt.tight_layout()
plt.savefig("figures/ch04-concours.png", bbox_inches="tight")
```
<!--sortie-->
```text
validation à origine glissante (13 origines, 12 horizons), RMSE en logarithme :
                                                RMSE global   h = 1  h = 12   biais
modèle                                                                             
type Prophet (Fourier + tendance par morceaux)       0.0665  0.0777  0.0673  0.0125
B : (1,0,0)(0,1,1) + tendance                        0.0670  0.0712  0.0889  0.0037
combinaison A+B+C                                    0.0687  0.0708  0.0808 -0.0295
A : SARIMAX(1,1,1)(0,1,1)                            0.0763  0.0737  0.0890 -0.0416
C : régression + AR(1)                               0.0807  0.0742  0.0903 -0.0506
naïf saisonnier + dérive                             0.0839  0.0753  0.1052 -0.0175
modèle structurel (niveau local + saison)            0.0996  0.0786  0.1022 -0.0066
naïf saisonnier                                      0.1081  0.1213  0.1264  0.0707
```

![Concours final à origine glissante : RMSE (en logarithme) de huit méthodes, avec en pointillé l'écart-type du bruit de la série estimé en 4.3.5. Les trois meilleures, dont le modèle de type Prophet, sont voisines et au niveau de ce bruit.](figures/ch04-concours.png)

Lecture honnête du tableau :

1. Le modèle de type Prophet, tel que nous l'avons écrit, arrive **en tête** du classement (RMSE de 0,0665), de très peu devant le modèle B (0,0670) : un écart bien inférieur à ce que 13 origines permettent de distinguer (4.3.5). Il est **dans le peloton de tête**, pas au-dessus.
2. Il y est parce que, pour des données mensuelles à saison nette, il se ramène à **« tendance linéaire par morceaux + effets de mois libres + régresseurs »**, une structure très proche de la vérité (le modèle C de 4.2.7 en est le cousin direct, sans changement de pente).
3. Le **modèle structurel**, très bon pour reconstituer des trous (4.5.6), fait ici **moins bien que la référence simple avec dérive** (0,0996 contre 0,0839) : son niveau en marche aléatoire « suit le bruit » et l'ancre sur des écarts qui s'effacent. Un bon outil pour une tâche (interpoler) n'est pas forcément le meilleur pour une autre (prévoir).
4. Les meilleurs modèles ont une erreur de 0,067 : entre l'écart-type des chocs mensuels (0,060, le minimum pour une prévision à un mois) et celui de l'écart à la tendance (0,0715, valeur à long terme). Ils font **à peu près ce que le bruit permet** : **plus de sophistication n'achète pas de précision** quand on est déjà proche de ce que les données permettent.

> ⚠️ **Mise en garde sur ce classement.** Il porte sur **une** série, **une** période de test, des réglages choisis par nous. Nous avons vu en 4.3.8 que le classement d'un jeu de test de deux ans peut s'inverser avec un autre tirage du hasard. Ne généralisez pas : un benchmark honnête (nombreuses séries, nombreuses origines, mêmes données pour tous) est un travail à part entière.

### 4.6.4 Les autres bibliothèques, et comment choisir

Voici un tour d'horizon, **sans exécution** ici (aucune de ces bibliothèques n'est installée dans l'environnement du livre) ; vérifiez la documentation de la version que vous utilisez.

| Bibliothèque | Idée | Quand l'utiliser |
|---|---|---|
| `statsmodels` (utilisée ici) | ARIMA, SARIMAX, espace d'états, ETS, VAR | comprendre, diagnostiquer, un petit nombre de séries |
| `statsforecast` | versions très rapides d'AutoARIMA, ETS, modèles naïfs | **des milliers de séries** à prévoir d'un coup |
| `sktime`, `darts` | interface unifiée (même syntaxe pour des dizaines de modèles), validation à origine glissante intégrée | comparer plusieurs familles de modèles proprement |
| `Prophet`, `NeuralProphet` | décomposition additive, événements, intervalles | séries d'entreprise à plusieurs saisons et jours fériés |
| modèles de fondation (par exemple Chronos, TimesFM) | grands réseaux pré-entraînés sur de nombreuses séries, utilisables sans ré-entraînement | prévision rapide « prête à l'emploi » à évaluer sur **vos** données |
| R : `forecast`, `fable` | `auto.arima`, `ets`, écosystème très complet | si votre équipe travaille en R |

Quelques principes pour choisir, tirés de ce chapitre :

- **Commencez par les références simples** (naïf saisonnier avec dérive) : elles sont le seuil à battre.
- **Comparez à origine glissante**, jamais sur un seul découpage, avec **le même protocole pour tous**.
- Une bibliothèque qui « fait tout en trois lignes » **cache** les choix (nombre d'harmoniques, flexibilité de la tendance, a priori) : sachez ce qu'elle fait (c'est le sens de 4.6.2).
- À précision comparable, **préférez le modèle que vous pouvez expliquer** : celui dont vous savez dire pourquoi il prévoit ce qu'il prévoit.

> ✅ **À retenir.**
> - **Prophet** est un modèle additif : tendance linéaire par morceaux + saisonnalité de Fourier + événements, ajusté par une régression pénalisée avec des a priori bayésiens. On peut l'écrire à la main avec une régression ridge.
> - Sur des données **mensuelles**, avec seulement 12 points par an, une saison nette demande beaucoup d'harmoniques ($K=6$ revient à un effet libre par mois).
> - Un nouveau modèle se juge **au même concours** que les autres (origine glissante, mêmes données). Sur notre série, le modèle de type Prophet, les modèles ARIMA et leur combinaison sont **tous proches de ce que le bruit permet** : la sophistication n'améliore pas ce que les données ne contiennent pas.
> - Choisissez en cascade : références simples, modèles statistiques compréhensibles, puis bibliothèques modernes ; et exigez toujours une évaluation honnête.


## 4.7 Exercices du chapitre 4

> 🧭 Cherchez d'abord à la main (ou sur papier), vérifiez ensuite par le code, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse. Les exercices 10 et 13 s'appuient sur des objets définis dans les sections précédentes (la fonction `kalman_niveau_local` de 4.5, la série `v` de 4.3).

### Énoncés

**Exercice 1 ⭐ (autocorrélation à la main).** Six chiffres d'affaires hebdomadaires (en centaines de DT) : $8,\,6,\,9,\,5,\,7,\,4$. Calculez à la main les autocorrélations $r_1$ et $r_2$. Quel signe attendiez-vous pour $r_1$ en regardant la série, et pourquoi ?

**Exercice 2 ⭐ (stationnaire ou non ?).** Pour chaque processus ($\varepsilon_t$ est un bruit blanc), dites s'il est stationnaire, et si non, quel remède appliquer : (a) $Y_t=5+\varepsilon_t$ ; (b) $Y_t=Y_{t-1}+\varepsilon_t$ ; (c) $Y_t=0{,}9\,Y_{t-1}+\varepsilon_t$ ; (d) $Y_t=2t+\varepsilon_t$ ; (e) $Y_t=1{,}1\,Y_{t-1}+\varepsilon_t$.

**Exercice 3 ⭐ (prévoir avec un AR(1)).** Un processus suit $Y_t-10=0{,}8\,(Y_{t-1}-10)+\varepsilon_t$ avec $\sigma=2$. (a) Quelle est sa variance, et les autocorrélations $\rho(1),\rho(2),\rho(3)$ ? (b) On observe $Y_T=14$ : donnez les prévisions à 1, 2 et 3 pas, avec les demi-largeurs des intervalles à 95 %.

**Exercice 4 ⭐⭐ (MA(1) et inversibilité).** (a) Calculez $\rho(1)$ pour $\theta=0{,}8$, puis pour $\theta=1{,}25$. Que remarquez-vous ? (b) Montrez qu'un MA(1) ne peut jamais avoir $|\rho(1)|>0{,}5$. Si vous observez $r_1=0{,}6$ sur une longue série, que concluez-vous ?

**Exercice 5 ⭐⭐ (Ljung-Box à la main).** Sur $n=50$ résidus, on trouve $r_1=0{,}30$ et $r_2=0{,}20$. Calculez $Q(2)$ et sa p-valeur (indice : pour 2 degrés de liberté, $P(\chi^2_2>x)=e^{-x/2}$). Que concluez-vous ?

**Exercice 6 ⭐⭐ (du logarithme aux dinars).** Un modèle prévoit $\log(\text{ca})=7{,}60$ pour décembre, avec une erreur type de prévision de $0{,}08$. Donnez la prévision **médiane** en dinars, la prévision de la **moyenne**, et l'intervalle de prévision à 95 %.

**Exercice 7 ⭐⭐ (MASE et MAPE).** Sur l'apprentissage, le naïf saisonnier a une MAE de 150 DT. Le modèle A a une MAE de 120 DT sur le test et le modèle B de 160 DT. (a) Calculez les MASE. (b) Pourquoi le MAPE est-il dangereux quand une valeur réelle est nulle ? (c) Pourquoi favorise-t-il les prévisions trop basses ?

**Exercice 8 ⭐⭐ (identifier un modèle).** Trois séries de 300 points, $X$, $Y$ et $Z$, ont été simulées avec des modèles ARMA différents. Voici leurs autocorrélations et autocorrélations partielles. **Identifiez** pour chacune le modèle le plus probable (type et ordre), puis vérifiez avec les critères d'information.

```python
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.tsa.arima_process import ArmaProcess
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import acf, pacf

mystere = {"X": ([1, -0.75], [1]), "Y": ([1], [1, 0.7, 0.5]), "Z": ([1, -0.5, -0.3], [1])}
series = {nom: ArmaProcess(ar, ma).generate_sample(300, distrvs=np.random.default_rng(100 + j).standard_normal)
          for j, (nom, (ar, ma)) in enumerate(mystere.items())}
bande = 1.96 / np.sqrt(300)
print("bande de confiance : +/-", round(bande, 3))
for nom, s in series.items():
    print(f"série {nom} : ACF  décalages 1-6 :", acf(s, nlags=6, fft=False)[1:].round(2))
    print(f"          PACF décalages 1-6 :", pacf(s, nlags=6, method="ols")[1:].round(2))
```
<!--sortie-->
```text
bande de confiance : +/- 0.113
série X : ACF  décalages 1-6 : [0.73 0.58 0.43 0.28 0.2  0.12]
          PACF décalages 1-6 : [ 0.74  0.1  -0.05 -0.1   0.03 -0.03]
série Y : ACF  décalages 1-6 : [ 0.6   0.17 -0.19 -0.25 -0.23 -0.17]
          PACF décalages 1-6 : [ 0.6  -0.28 -0.27  0.1  -0.12 -0.12]
série Z : ACF  décalages 1-6 : [0.69 0.57 0.48 0.36 0.29 0.28]
          PACF décalages 1-6 : [ 0.69  0.19  0.08 -0.07 -0.    0.09]
```

**Exercice 9 ⭐⭐⭐ (la sur-différenciation, en théorie).** Soit $Y_t$ un AR(1) stationnaire de coefficient $\varphi$, et $W_t=Y_t-Y_{t-1}$. (a) Calculez $\operatorname{Var}(W_t)$ et $\operatorname{Cov}(W_t,W_{t-1})$ en fonction de $\gamma(0)$ et de $\varphi$, puis montrez que $\rho_W(1)=-\dfrac{1-\varphi}{2}$. (b) Que vaut ce résultat pour $\varphi=0$ ? pour $\varphi\to1$ ? Interprétez. (c) Vérifiez par simulation pour $\varphi=0{,}5$ et $\varphi=0{,}9$.

**Exercice 10 ⭐⭐⭐ (filtre de Kalman à la main).** Niveau local de variances $\sigma_\varepsilon^2=9$ (observation) et $\sigma_\eta^2=3$ (niveau), croyance initiale $\mathcal N(50,\,12)$ avant la première mesure. On observe $y_1=56$ puis $y_2=52$. (a) Calculez à la main les gains $K_1,K_2$, les niveaux filtrés $a_{1|1},a_{2|2}$ et leurs variances. (b) Quel est le gain en régime permanent ? (c) À quel paramètre de lissage exponentiel cela correspond-il ?

**Exercice 11 ⭐⭐⭐ (régression fallacieuse et remède).** Deux marches aléatoires indépendantes de 200 points sont régressées l'une sur l'autre. (a) Quelle part de régressions « significatives » à 5 % attendez-vous, en niveaux ? (b) Montrez par simulation que la régression **des différences** $\Delta a_t$ sur $\Delta b_t$ redonne le bon taux de 5 %. (c) Pourquoi ce remède fonctionne-t-il, et quelle information perd-on ?

**Exercice 12 ⭐⭐ (GARCH à la main).** Un GARCH(1,1) a pour paramètres $\omega=0{,}1$, $\alpha=0{,}2$, $\beta=0{,}7$. (a) Quelle est la variance de long terme ? (b) Hier, $\varepsilon_{t-1}=2$ et $\sigma_{t-1}^2=1{,}5$ : que vaut $\sigma_t^2$ ? (c) Quelle est la prévision de $\sigma_{t+1}^2$ ? (d) En combien de pas l'excès de variance (au-dessus de la variance de long terme) est-il divisé par deux ?

**Exercice 13 ⭐⭐⭐ (le concours complet sur une autre série).** Appliquez la démarche de 4.3 à la série `nb_commandes` (nombre de commandes par mois) : travaillez en logarithme, apprenez sur 2016-2023, prévoyez 2024-2025 avec (i) le naïf saisonnier avec dérive et (ii) un SARIMAX$(1,0,0)(0,1,1)_{12}$ avec tendance et variables `promo` et `covid`. Calculez la MASE (en nombre de commandes) de chacun. Le modèle bat-il la référence ? Que pensez-vous de la précision atteignable sur cette série, plus bruitée que le chiffre d'affaires ?

### Corrigés

**Corrigé 1.** Moyenne $=39/6=6{,}5$ ; écarts : $1{,}5;\,-0{,}5;\,2{,}5;\,-1{,}5;\,0{,}5;\,-2{,}5$ ; somme des carrés : $2{,}25+0{,}25+6{,}25+2{,}25+0{,}25+6{,}25=17{,}5$. **Décalage 1** : produits $(-0{,}5)(1{,}5)=-0{,}75$ ; $(2{,}5)(-0{,}5)=-1{,}25$ ; $(-1{,}5)(2{,}5)=-3{,}75$ ; $(0{,}5)(-1{,}5)=-0{,}75$ ; $(-2{,}5)(0{,}5)=-1{,}25$ ; somme $-7{,}75$, donc $r_1=-7{,}75/17{,}5\approx-0{,}443$. **Décalage 2** : $(2{,}5)(1{,}5)=3{,}75$ ; $(-1{,}5)(-0{,}5)=0{,}75$ ; $(0{,}5)(2{,}5)=1{,}25$ ; $(-2{,}5)(-1{,}5)=3{,}75$ ; somme $9{,}5$, donc $r_2\approx0{,}543$. On attendait un $r_1$ **négatif** : la série fait du « zigzag » (haut, bas, haut, bas) autour de sa moyenne, et un zigzag correspond à une corrélation négative entre deux mois consécutifs et positive à deux mois d'écart. Avec seulement six points, ces valeurs sont très incertaines (bande de $\pm0{,}8$).

```python
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd

def acf_manuel(x, k):
    d = np.asarray(x, float) - np.mean(x)
    return (d[:len(d) - k] * d[k:]).sum() / (d ** 2).sum()

x = [8, 6, 9, 5, 7, 4]
print("r1 =", round(acf_manuel(x, 1), 4), "| r2 =", round(acf_manuel(x, 2), 4), "| bande 1,96/racine(6) =", round(1.96 / np.sqrt(6), 2))
```
<!--sortie-->
```text
r1 = -0.4429 | r2 = 0.5429 | bande 1,96/racine(6) = 0.8
```

**Corrigé 2.** (a) **Stationnaire** : moyenne 5, variance $\sigma^2$, pas de mémoire. (b) **Marche aléatoire** : non stationnaire ($\operatorname{Var}=t\sigma^2$) ; remède : **différencier**. (c) **Stationnaire** ($|\varphi|=0{,}9<1$), mais très persistant : la mémoire décroît lentement ($\rho(k)=0{,}9^k$), et sur un échantillon court elle se confond facilement avec une racine unitaire (c'est le manque de puissance de 4.1.6). (d) **Non stationnaire** : la moyenne $2t$ varie ; remède : **retirer la tendance** (régression sur $t$), car la tendance est déterministe, pas stochastique (différencier fonctionnerait aussi, mais sur-différencierait). (e) **Explosif** ($|\varphi|>1$) : non stationnaire, aucune transformation simple ne le « répare » ; c'est rare en pratique.

```python
rng = np.random.default_rng(3)
n = 400
e = rng.normal(size=n)
def generer(phi, tendance=0.0, depart=0.0):
    y = np.zeros(n); y[0] = depart
    for t in range(1, n):
        y[t] = phi * y[t - 1] + e[t] + tendance * t
    return y
cas = {"(a) 5 + bruit": 5 + e, "(b) marche aléatoire": generer(1.0), "(c) AR(1), phi = 0,9": generer(0.9),
       "(d) 2t + bruit": 2 * np.arange(n) + e}
lignes = [{"processus": k, "moyenne 1re moitié": s[:n // 2].mean(), "moyenne 2e moitié": s[n // 2:].mean(),
           "écart-type 1re moitié": s[:n // 2].std(), "écart-type 2e moitié": s[n // 2:].std()} for k, s in cas.items()]
print(pd.DataFrame(lignes).round(1).to_string(index=False))
```
<!--sortie-->
```text
           processus  moyenne 1re moitié  moyenne 2e moitié  écart-type 1re moitié  écart-type 2e moitié
       (a) 5 + bruit                 5.0                5.0                    1.0                   1.0
(b) marche aléatoire                -2.8                7.4                    4.3                   4.1
(c) AR(1), phi = 0,9                 0.3                0.2                    2.2                   2.3
      (d) 2t + bruit               199.0              599.0                  115.6                 115.5
```

La simulation montre que les moyennes diffèrent nettement d'une moitié à l'autre pour (b) et (d), alors que (a) et (c) se ressemblent. (Pour la marche aléatoire (b), c'est la variance **à travers les trajectoires** qui croît avec $t$ (4.1.3) ; sur une seule trajectoire, comparer les écarts-types de deux moitiés n'est pas probant, et le tableau ne le montre d'ailleurs pas. C'est le déplacement de la moyenne qui trahit la non-stationnarité.)

**Corrigé 3.** (a) $\gamma(0)=\dfrac{\sigma^2}{1-\varphi^2}=\dfrac4{1-0{,}64}=11{,}11$ (écart-type $3{,}33$) ; $\rho(1)=0{,}8$, $\rho(2)=0{,}64$, $\rho(3)=0{,}512$. (b) $\hat y_{T+h}=10+0{,}8^h\times(14-10)$ : $13{,}2$ ; $12{,}56$ ; $12{,}048$. Demi-largeurs : $1{,}96\,\sigma\sqrt{\sum_{j<h}\varphi^{2j}}$ : $h=1$ : $1{,}96\times2=3{,}92$ ; $h=2$ : $3{,}92\times\sqrt{1{,}64}=5{,}02$ ; $h=3$ : $3{,}92\times\sqrt{1{,}64+0{,}4096}=5{,}61$. Limite : $1{,}96\times3{,}33=6{,}53$.

```python
from statsmodels.tsa.arima.model import ARIMA
phi, mu, sigma, yT = 0.8, 10.0, 2.0, 14.0
print("variance :", round(sigma ** 2 / (1 - phi ** 2), 2), "| rho(1..3) :", [round(phi ** k, 3) for k in (1, 2, 3)])
print("prévisions :", [round(mu + phi ** h * (yT - mu), 3) for h in (1, 2, 3)])
print("demi-largeurs :", np.round([1.96 * sigma * np.sqrt(sum(phi ** (2 * j) for j in range(h))) for h in (1, 2, 3)], 2),
      "| limite :", round(1.96 * sigma / np.sqrt(1 - phi ** 2), 2))
# vérification avec statsmodels (paramètres fixés : constante, phi, sigma2)
fixe = ARIMA(np.r_[np.full(50, mu), yT], order=(1, 0, 0), trend="c").filter([mu, phi, sigma ** 2])
p = fixe.get_forecast(3)
print("statsmodels :", p.predicted_mean.round(3), ((p.conf_int()[:, 1] - p.conf_int()[:, 0]) / 2).round(2))
```
<!--sortie-->
```text
variance : 11.11 | rho(1..3) : [0.8, 0.64, 0.512]
prévisions : [13.2, 12.56, 12.048]
demi-largeurs : [3.92 5.02 5.61] | limite : 6.53
statsmodels : [13.2   12.56  12.048] [3.92 5.02 5.61]
```

**Corrigé 4.** (a) $\rho(1)=\dfrac{0{,}8}{1+0{,}64}=0{,}488$ et $\rho(1)=\dfrac{1{,}25}{1+1{,}5625}=0{,}488$ : **les deux valeurs donnent la même autocorrélation** ($\theta$ et $1/\theta$). On retient la valeur **inversible** $\theta=0{,}8$. (b) $1+\theta^2\ge2|\theta|$ (car $(1-|\theta|)^2\ge0$), donc $|\rho(1)|=\dfrac{|\theta|}{1+\theta^2}\le\dfrac12$, avec égalité pour $\theta=\pm1$. Si l'on observe $r_1=0{,}6$ sur une longue série (assez longue pour que $0{,}6$ ne soit pas du bruit d'échantillonnage), **ce n'est pas un MA(1)** : il faut un AR (dont la mémoire peut produire une autocorrélation d'ordre 1 proche de 1), ou un ARMA.

```python
from statsmodels.tsa.arima_process import arma_acf
for th in (0.8, 1.25):
    print(f"theta = {th} : rho(1) = {arma_acf([1], [1, th], 2)[1]:.4f}")
thetas = np.linspace(-5, 5, 100001)
rho1 = thetas / (1 + thetas ** 2)
print("maximum de |rho(1)| sur theta dans [-5, 5] :", round(np.abs(rho1).max(), 4), "atteint pour theta =", round(abs(thetas[np.abs(rho1).argmax()]), 3))
```
<!--sortie-->
```text
theta = 0.8 : rho(1) = 0.4878
theta = 1.25 : rho(1) = 0.4878
maximum de |rho(1)| sur theta dans [-5, 5] : 0.5 atteint pour theta = 1.0
```

**Corrigé 5.** $Q(2)=n(n+2)\left[\dfrac{r_1^2}{n-1}+\dfrac{r_2^2}{n-2}\right]=50\times52\times\left[\dfrac{0{,}09}{49}+\dfrac{0{,}04}{48}\right]=2600\times(0{,}001837+0{,}000833)=6{,}94$. Pour 2 degrés de liberté, $p=e^{-6{,}94/2}=e^{-3{,}47}\approx0{,}031$. **p < 0,05** : on rejette l'hypothèse « bruit blanc » ; le modèle n'a pas tout expliqué. (Si les résidus provenaient d'un modèle avec deux paramètres AR/MA estimés, il faudrait comparer à un khi-deux à $2-2=0$ degré de liberté : le test serait inutilisable à 2 retards ; on utiliserait plus de retards.)

```python
from scipy import stats
n, r = 50, np.array([0.30, 0.20])
Q = n * (n + 2) * np.sum(r ** 2 / (n - np.arange(1, 3)))
print("Q(2) =", round(Q, 3), "| p-valeur =", round(np.exp(-Q / 2), 4), "| via scipy :", round(1 - stats.chi2.cdf(Q, 2), 4))
```
<!--sortie-->
```text
Q(2) = 6.942 | p-valeur = 0.0311 | via scipy : 0.0311
```

**Corrigé 6.** La **médiane** est $e^{7{,}60}\approx1\,998$ DT. La **moyenne** vaut $e^{7{,}60+0{,}08^2/2}=e^{7{,}6032}\approx2\,005$ DT (un facteur $e^{0{,}0032}\approx1{,}003$ : négligeable). L'intervalle à 95 % : $\exp(7{,}60\pm1{,}96\times0{,}08)=\exp(7{,}60\pm0{,}1568)=[1\,708\,;\,2\,337]$ DT : environ $\pm16\,\%$ autour de la médiane, de façon **asymétrique** en dinars (l'intervalle est un peu plus étendu vers le haut : $+339$ DT contre $-290$ DT).

```python
m, s = 7.60, 0.08
print("médiane :", round(np.exp(m), 1), "| moyenne :", round(np.exp(m + s ** 2 / 2), 1))
print("IC95 % :", round(np.exp(m - 1.96 * s), 1), "à", round(np.exp(m + 1.96 * s), 1),
      "| écarts à la médiane :", round(np.exp(m - 1.96 * s) - np.exp(m), 1), "et +", round(np.exp(m + 1.96 * s) - np.exp(m), 1))
```
<!--sortie-->
```text
médiane : 1998.2 | moyenne : 2004.6
IC95 % : 1708.2 à 2337.4 | écarts à la médiane : -290.0 et + 339.2
```

**Corrigé 7.** (a) $\text{MASE}_A=120/150=0{,}80$ (le modèle fait **20 % mieux** que le naïf saisonnier de l'apprentissage) ; $\text{MASE}_B=160/150\approx1{,}07$ (**moins bien** que le naïf). (b) Le MAPE divise par $|y_t|$ : si $y_t=0$ (un mois sans vente), le terme est indéfini (division par zéro), et pour des valeurs réelles très petites il explose. (c) Une sous-prévision ne peut pas dépasser **100 %** d'erreur (prévoir 0 pour une valeur de 100 donne 100 %), alors qu'une surestimation est **illimitée** (prévoir 300 pour 100 donne 200 %). En minimisant le MAPE, un modèle est donc incité à prévoir **trop bas**.

```python
actuel = 100
for prevu in (0, 50, 150, 300):
    print(f"réel = {actuel}, prévu = {prevu:3d} -> erreur en % du réel = {100 * abs(actuel - prevu) / actuel:.0f} %")
print("MASE A =", 120 / 150, "| MASE B =", round(160 / 150, 3))
```
<!--sortie-->
```text
réel = 100, prévu =   0 -> erreur en % du réel = 100 %
réel = 100, prévu =  50 -> erreur en % du réel = 50 %
réel = 100, prévu = 150 -> erreur en % du réel = 50 %
réel = 100, prévu = 300 -> erreur en % du réel = 200 %
MASE A = 0.8 | MASE B = 1.067
```

**Corrigé 8.** **Règle** (4.2.1) : AR($p$) $\Rightarrow$ PACF qui s'arrête après $p$, ACF qui décroît ; MA($q$) $\Rightarrow$ ACF qui s'arrête après $q$, PACF qui décroît. Lecture des sorties de l'énoncé (bande de $\pm0{,}113$) :

- **$X$** : ACF qui décroît lentement (0,73 ; 0,58 ; 0,43 ; 0,28…), PACF avec **un seul** pic net, au décalage 1 (0,74), puis des valeurs dans la bande : un **AR(1)**, de coefficient voisin de 0,74.
- **$Z$** : ACF qui décroît, PACF de 0,69 puis 0,19 (au-dessus de la bande), puis dans la bande : un **AR(2)** est plausible (un AR(1) est possible : le deuxième pic est faible).
- **$Y$** : PACF qui décroît avec alternance de signes ($0{,}60$ ; $-0{,}28$ ; $-0{,}27$ ; puis dans la bande) : une signature de **MA** ; mais l'ACF ($0{,}60$ ; $0{,}17$ ; puis $-0{,}19$, $-0{,}25$, $-0{,}23$ au-delà de la bande) ne s'arrête **pas** proprement après le décalage 2. Cette série est **ambiguë** à l'œil : un MA(2), mais peut-être un MA plus long ou un ARMA.

Voilà la réalité de l'identification : avec 300 points, les autocorrélations estimées fluctuent d'environ $\pm0{,}11$, et les signatures théoriques de la figure de 4.2.1 se brouillent. D'où le rôle des critères d'information, qui comparent les modèles candidats **entre eux** :

```python
candidats = {"AR(1)": (1, 0, 0), "AR(2)": (2, 0, 0), "MA(1)": (0, 0, 1), "MA(2)": (0, 0, 2), "ARMA(1,1)": (1, 0, 1)}
ajustements = {nom: {c: ARIMA(s, order=o, trend="n").fit() for c, o in candidats.items()} for nom, s in series.items()}
aic = pd.DataFrame({nom: {c: m.aic for c, m in d.items()} for nom, d in ajustements.items()})
bic = pd.DataFrame({nom: {c: m.bic for c, m in d.items()} for nom, d in ajustements.items()})
print("AIC par modèle (une colonne par série) :")
print(aic.round(1).to_string())
print("\nBIC par modèle :")
print(bic.round(1).to_string())
print("\nmeilleur modèle par AIC :", aic.idxmin().to_dict())
print("meilleur modèle par BIC :", bic.idxmin().to_dict())
print("vérité : X = AR(1), phi = 0,75 | Y = MA(2), theta = (0,7 ; 0,5) | Z = AR(2), phi = (0,5 ; 0,3)")
```
<!--sortie-->
```text
AIC par modèle (une colonne par série) :
               X      Y      Z
AR(1)      850.5  906.2  882.7
AR(2)      849.5  883.7  873.3
MA(1)      944.1  929.2  964.5
MA(2)      897.8  864.3  930.8
ARMA(1,1)  850.0  896.0  871.9

BIC par modèle :
               X      Y      Z
AR(1)      858.0  913.6  890.2
AR(2)      860.6  894.8  884.4
MA(1)      951.5  936.6  971.9
MA(2)      908.9  875.4  941.9
ARMA(1,1)  861.1  907.1  883.0

meilleur modèle par AIC : {'X': 'AR(2)', 'Y': 'MA(2)', 'Z': 'ARMA(1,1)'}
meilleur modèle par BIC : {'X': 'AR(1)', 'Y': 'MA(2)', 'Z': 'ARMA(1,1)'}
vérité : X = AR(1), phi = 0,75 | Y = MA(2), theta = (0,7 ; 0,5) | Z = AR(2), phi = (0,5 ; 0,3)
```

**Lecture des critères.** Pour **$Y$**, le MA(2) l'emporte nettement, par l'AIC comme par le BIC : le critère résout l'ambiguïté que l'œil ne résolvait pas. Pour **$X$** et **$Z$**, ce sont des modèles **voisins** qui se disputent la première place avec un ou deux points d'écart : un AR(2) dont le second coefficient est petit ressemble à un AR(1), et un ARMA(1,1) imite un AR(2). **Un écart d'AIC de l'ordre de 1 à 2 ne permet pas de trancher** (la règle empirique est qu'il faut un écart de plus de 2 à 4 points pour préférer un modèle). Le BIC, plus sévère avec la complexité, retrouve la vérité pour $X$ (AR(1)) et pour $Y$ (MA(2)), mais préfère encore l'ARMA(1,1) à l'AR(2) pour $Z$, avec 1,4 point d'écart (883,0 contre 884,4) : pour ces deux modèles voisins, les données n'ont pas de quoi décider. En pratique, on retient alors le modèle **le plus simple** parmi les ex æquo, et on valide par les résidus et par la prévision.

**Corrigé 9.** (a) Soit $\gamma(k)=\varphi^k\gamma(0)$. $\operatorname{Var}(W_t)=2\gamma(0)-2\gamma(1)=2\gamma(0)(1-\varphi)$. $\operatorname{Cov}(W_t,W_{t-1})=\operatorname{Cov}(Y_t-Y_{t-1},Y_{t-1}-Y_{t-2})=\gamma(1)-\gamma(2)-\gamma(0)+\gamma(1)=\gamma(0)(2\varphi-\varphi^2-1)=-\gamma(0)(1-\varphi)^2$. Donc $\rho_W(1)=\dfrac{-\gamma(0)(1-\varphi)^2}{2\gamma(0)(1-\varphi)}=-\dfrac{1-\varphi}2$. (b) Pour $\varphi=0$ ($Y$ est un bruit blanc), on retrouve $-0{,}5$ (4.1.6). Pour $\varphi\to1$ (quasi-marche aléatoire), $\rho_W(1)\to0$ : la différence d'une marche aléatoire est un bruit blanc : **la différenciation est alors le bon remède**. Entre les deux, plus la série est « loin » d'une racine unitaire, plus la différenciation fabrique une autocorrélation négative artificielle. (c) Simulation :

```python
from statsmodels.tsa.arima_process import ArmaProcess
for phi in (0.0, 0.5, 0.9):
    x = ArmaProcess([1, -phi], [1]).generate_sample(300000, distrvs=np.random.default_rng(7).standard_normal)
    print(f"phi = {phi} : rho_W(1) simulé = {acf_manuel(np.diff(x), 1):+.3f}   | théorie -(1-phi)/2 = {-(1 - phi) / 2:+.3f}")
```
<!--sortie-->
```text
phi = 0.0 : rho_W(1) simulé = -0.502   | théorie -(1-phi)/2 = -0.500
phi = 0.5 : rho_W(1) simulé = -0.252   | théorie -(1-phi)/2 = -0.250
phi = 0.9 : rho_W(1) simulé = -0.052   | théorie -(1-phi)/2 = -0.050
```

**Corrigé 10.** (a) **Date 1.** $P_{1|0}=12$, $F_1=12+9=21$, $K_1=12/21=0{,}5714$, $v_1=56-50=6$, $a_{1|1}=50+0{,}5714\times6=53{,}43$, $P_{1|1}=12\times\dfrac{9}{21}=5{,}143$. **Date 2.** $P_{2|1}=5{,}143+3=8{,}143$, $F_2=17{,}143$, $K_2=8{,}143/17{,}143=0{,}475$, $v_2=52-53{,}43=-1{,}43$, $a_{2|2}=53{,}43+0{,}475\times(-1{,}43)=52{,}75$, $P_{2|2}=8{,}143\times\dfrac{9}{17{,}143}=4{,}275$. (b) En régime permanent, la variance prédite $p$ vérifie $p=\dfrac{p\sigma_\varepsilon^2}{p+\sigma_\varepsilon^2}+\sigma_\eta^2$, soit $p^2=\sigma_\eta^2\,p+\sigma_\eta^2\sigma_\varepsilon^2$, donc $p=\dfrac{3+\sqrt{9+4\times27}}2=\dfrac{3+\sqrt{117}}2\approx6{,}908$ et $K_\infty=\dfrac{p}{p+9}\approx0{,}434$. (c) Le lissage exponentiel simple de paramètre $\alpha=K_\infty\approx0{,}43$.

```python
r = kalman_niveau_local(np.array([56.0, 52.0]), s2_eps=9.0, s2_eta=3.0, a0=50.0, P0=12.0)     # fonction définie en 4.5.3
print(pd.DataFrame({k: r[k] for k in ["P_pred", "F", "K", "v", "a_filtre", "P_filtre"]}, index=[1, 2]).round(4).to_string())
p_inf = (3 + np.sqrt(9 + 4 * 27)) / 2
print("régime permanent : p =", round(p_inf, 4), "| K_inf =", round(p_inf / (p_inf + 9), 4))
longue = kalman_niveau_local(np.random.default_rng(1).normal(100, 3, 300), 9.0, 3.0, 100.0, 12.0)
print("gain après 300 observations :", round(longue["K"][-1], 4))
```
<!--sortie-->
```text
    P_pred        F       K       v  a_filtre  P_filtre
1  12.0000  21.0000  0.5714  6.0000   53.4286    5.1429
2   8.1429  17.1429  0.4750 -1.4286   52.7500    4.2750
régime permanent : p = 6.9083 | K_inf = 0.4343
gain après 300 observations : 0.4343
```

**Corrigé 11.** (a) En niveaux, la pente est « significative » dans **plus des trois quarts** des cas (77 % avec 100 points en 4.4.2 ; plus encore avec 200 points, voir la sortie : plus les séries sont longues, plus l'illusion est fréquente), pas 5 %. (b) Sur les différences (qui sont des bruits blancs indépendants), le taux retombe autour de 5 % (la sortie donne une valeur proche, à l'incertitude de la simulation près). (c) La différenciation rend les séries **stationnaires** : les hypothèses du chapitre 1 s'appliquent de nouveau, donc les p-valeurs sont justes. On **perd l'information de long terme** : si les séries sont cointégrées (4.4.2), une régression sur les différences ignore la relation d'équilibre ; il faut alors le modèle à correction d'erreur.

```python
import statsmodels.api as sm
rng = np.random.default_rng(55)
niveaux, differences = [], []
for _ in range(2000):
    a = np.cumsum(rng.normal(size=200))
    b = np.cumsum(rng.normal(size=200))
    niveaux.append(abs(sm.OLS(a, sm.add_constant(b)).fit().tvalues[1]) > 1.96)
    differences.append(abs(sm.OLS(np.diff(a), sm.add_constant(np.diff(b))).fit().tvalues[1]) > 1.96)
print("part de pentes « significatives » à 5 % : en niveaux =", np.mean(niveaux).round(3), "| sur les différences =", np.mean(differences).round(3))
```
<!--sortie-->
```text
part de pentes « significatives » à 5 % : en niveaux = 0.824 | sur les différences = 0.052
```

**Corrigé 12.** (a) $\sigma^2=\dfrac{0{,}1}{1-0{,}2-0{,}7}=1$. (b) $\sigma_t^2=0{,}1+0{,}2\times2^2+0{,}7\times1{,}5=0{,}1+0{,}8+1{,}05=1{,}95$. (c) $\mathbb E[\sigma_{t+1}^2]=\omega+(\alpha+\beta)\sigma_t^2=0{,}1+0{,}9\times1{,}95=1{,}855$ (car $\mathbb E[\varepsilon_t^2\mid\text{passé}]=\sigma_t^2$). (d) L'excès $\sigma^2_{t+h}-1$ est multiplié par $\alpha+\beta=0{,}9$ à chaque pas : il est divisé par deux quand $0{,}9^h=0{,}5$, soit $h=\ln0{,}5/\ln0{,}9\approx6{,}6$ : **environ 7 jours**.

```python
omega, alpha, beta = 0.1, 0.2, 0.7
var_lt = omega / (1 - alpha - beta)
sig2_t = omega + alpha * 2 ** 2 + beta * 1.5
prev = [omega + (alpha + beta) * sig2_t]
for _ in range(19):
    prev.append(omega + (alpha + beta) * prev[-1])
print("variance de long terme :", round(var_lt, 4), "| sigma_t^2 =", round(sig2_t, 3), "| prévision de sigma_{t+1}^2 =", round(prev[0], 3))
print("excès sur la variance de long terme aux pas 1, 5, 10, 20 :", np.round(np.array(prev)[[0, 4, 9, 19]] - var_lt, 3))
print("demi-vie de l'excès :", round(np.log(0.5) / np.log(alpha + beta), 2), "pas")
```
<!--sortie-->
```text
variance de long terme : 1.0 | sigma_t^2 = 1.95 | prévision de sigma_{t+1}^2 = 1.855
excès sur la variance de long terme aux pas 1, 5, 10, 20 : [0.855 0.561 0.331 0.115]
demi-vie de l'excès : 6.58 pas
```

**Corrigé 13.** On applique la démarche de 4.3 à $\log(\text{nb\_commandes})$ : même découpage, un naïf saisonnier avec dérive, un SARIMAX, et la MASE en **nombre de commandes** (échelle : MAE du naïf saisonnier sur l'apprentissage).

```python
from statsmodels.tsa.statespace.sarimax import SARIMAX
v = pd.read_csv("donnees/ventes_mensuelles.csv", parse_dates=["mois"]).set_index("mois")
v.index.freq = "MS"
z = np.log(v["nb_commandes"])
train_z, test_z = z[:"2023-12"], z["2024-01":]
Xe = v[["promo", "covid"]].astype(float)

g = (train_z - train_z.shift(12)).mean()
naif = pd.Series([train_z.iloc[-12 + (h % 12)] + g * (1 + h // 12) for h in range(24)], index=test_z.index)
modele = SARIMAX(train_z, exog=Xe[:"2023-12"], order=(1, 0, 0), seasonal_order=(0, 1, 1, 12), trend="ct").fit(disp=False, maxiter=300)
prevu = pd.Series(modele.get_forecast(24, exog=Xe["2024-01":]).predicted_mean.values, index=test_z.index)

nb_train = np.exp(train_z)
echelle = np.mean(np.abs(nb_train.values[12:] - nb_train.values[:-12]))
lignes = {}
for nom, f in [("naïf saisonnier + dérive", naif), ("SARIMAX(1,0,0)(0,1,1)12 + tendance", prevu)]:
    mae = np.mean(np.abs(np.exp(test_z) - np.exp(f)))
    lignes[nom] = {"MAE (commandes)": mae, "MASE": mae / echelle, "RMSE (log)": np.sqrt(np.mean((test_z - f) ** 2)), "biais (log)": float(np.mean(test_z - f))}
print("MAE du naïf saisonnier sur l'apprentissage :", round(echelle, 2), "commandes")
print(pd.DataFrame(lignes).T.round(3).to_string())
print("écart-type des résidus du SARIMAX (log) :", round(float(np.sqrt(modele.params['sigma2'])), 3), "| à comparer à celui du chiffre d'affaires (4.2) : environ 0,06 à 0,07")
```
<!--sortie-->
```text
MAE du naïf saisonnier sur l'apprentissage : 7.92 commandes
                                    MAE (commandes)   MASE  RMSE (log)  biais (log)
naïf saisonnier + dérive                      7.786  0.983       0.273       -0.139
SARIMAX(1,0,0)(0,1,1)12 + tendance            6.146  0.776       0.216        0.023
écart-type des résidus du SARIMAX (log) : 0.262 | à comparer à celui du chiffre d'affaires (4.2) : environ 0,06 à 0,07
```

Le résultat se lit en trois temps. (1) Le **bruit** de cette série est nettement plus grand que celui du chiffre d'affaires : un nombre de commandes est un **comptage** (de loi de Poisson, de variance égale à la moyenne), donc son erreur relative, de l'ordre de $1/\sqrt{\text{moyenne}}$ (environ 19 % pour 28 commandes par mois), est irréductible. L'écart-type des résidus du SARIMAX est d'environ 0,26 en logarithme, près de quatre fois celui du chiffre d'affaires. (2) Le SARIMAX fait **mieux que la référence simple** (MASE de 0,78 contre 0,98, soit environ 20 % d'erreur de moins ; sa MAE est de 6,1 commandes par mois), mais la référence est déjà **à peine meilleure que le naïf saisonnier de l'apprentissage** (MASE proche de 1) : à ce niveau de bruit, le gain d'un bon modèle se mesure en dizaines de pour cent d'une erreur de toute façon élevée, pas en précision. (3) La bonne conclusion est donc moins « quel modèle ? » que « quelle précision peut-on espérer ? » : une prévision de commandes mensuelles doit s'accompagner d'une **fourchette large**.

---

## Bilan du chapitre 4

Vous savez maintenant :

- **décrire** une série temporelle (tendance, saison, bruit, accident) et la **décomposer** (classique, STL robuste), en travaillant sur le **logarithme** quand la saison est proportionnelle au niveau ;
- définir la **stationnarité**, mesurer la mémoire par l'**autocorrélation** et l'**autocorrélation partielle**, tester le bruit blanc (**Ljung-Box**) et la racine unitaire (**ADF**, **KPSS**) en connaissant leurs limites (peu de puissance, loi de Dickey-Fuller non normale) ;
- distinguer **tendance déterministe** et **tendance stochastique**, et éviter la **sur-différenciation** ;
- construire des modèles **AR, MA, ARMA, ARIMA, SARIMA** et **SARIMAX**, connaître leurs conditions de stationnarité et d'inversibilité, suivre la méthode de **Box-Jenkins** (identification, estimation, diagnostic, prévision) et lire un diagnostic de résidus ;
- **prévoir** avec ses intervalles, passer du logarithme aux dinars, et **évaluer honnêtement** : découpage temporel, références simples, MAE, RMSE, MAPE, **MASE**, bootstrap par blocs, **validation à origine glissante**, combinaison de prévisions ;
- comprendre qu'un seul jeu de test est **bruité** : le meilleur modèle en espérance ne gagne pas toujours (4.3.8) ;
- (en option) modéliser **plusieurs séries** (VAR, causalité de Granger, **cointégration**, régression fallacieuse), la **volatilité** (GARCH), les **modèles d'espace d'états** et le **filtre de Kalman** (lissage exponentiel, données manquantes), et situer **Prophet** et les bibliothèques modernes.

Le chapitre 5 change d'univers : il ne s'agit plus d'une série qui évolue **dans le temps calendaire**, mais d'un événement dont on mesure **la durée d'attente**, avec le défi particulier de la **censure** : combien de temps un client reste-t-il fidèle, quand certains sont encore clients aujourd'hui ?
