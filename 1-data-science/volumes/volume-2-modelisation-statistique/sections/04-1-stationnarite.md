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
