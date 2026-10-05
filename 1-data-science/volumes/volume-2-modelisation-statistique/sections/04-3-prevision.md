## 4.3 Prévision et évaluation des prévisions

> 💡 **Intuition.** Prévoir, ce n'est pas deviner un nombre : c'est annoncer **un nombre et son incertitude**. « Les ventes de décembre seront de 3 300 €, avec 95 % de chances de tomber entre 2 800 et 3 900 » est une prévision utile ; « 3 300 » tout court n'en est pas une. Et un modèle ne se juge pas à la beauté de son ajustement passé, mais à la qualité des prévisions qu'il fait sur des données qu'il **n'a pas vues**.

Dans cette section, nous faisons trois choses : comprendre comment un modèle ARIMA prévoit et d'où viennent ses intervalles (4.3.1 et 4.3.2) ; mettre en place une **évaluation honnête** (4.3.3 à 4.3.6) ; puis prévoir 2026 pour la gérante (4.3.7) et **lever le voile** sur la fabrication des données (4.3.8).

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

### 4.3.2 Prévoir en logarithme, annoncer en euros

Nos modèles prévoient $\log(\text{ca})$. Pour annoncer des euros, on revient par l'exponentielle. Deux précautions :

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

Appliquons-les à nos cinq prévisions des 24 mois de test, **en euros** (on revient de l'échelle logarithmique par l'exponentielle) :

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

Lisons ce tableau (trié par RMSE en euros ; `biais (log)` est la moyenne de $y-\hat y$ en logarithme, donc un biais **positif** signifie que le modèle **sous-estime**).

- Le **naïf saisonnier simple** est le plus mauvais, avec une MASE de 1,45 (pire que lui-même sur l'apprentissage) et un biais de $+0{,}14$ : il répète l'année passée sans tenir compte de la croissance, et donc sous-estime d'environ 14 %.
- Le **naïf saisonnier avec dérive**, trois lignes de code, est déjà très honorable : MASE de 0,74, MAPE de 6,7 %. Il **bat deux de nos trois modèles ARIMA** (A et C) sur cette fenêtre, en euros comme en MAPE. Voilà pourquoi on ne néglige jamais les références simples.
- Le modèle **B** est le seul à faire nettement mieux que la référence (MASE de 0,64, MAPE de 6,1 %). Les modèles **A** et **C** ont un biais négatif d'environ $-0{,}07$ : ils **surestiment** de 7 % en moyenne. Nous verrons en 4.3.8 pourquoi.

> ⚠️ **Prévoir en euros ou en logarithme ?** Nous avons optimisé les modèles en log (erreurs relatives), mais nous les jugeons en euros (ce qui intéresse la gérante) : une erreur de 300 € en décembre et de 300 € en février n'ont pas le même poids en log, mais le même en euros. Quand l'objectif métier est en unités de la série, évaluez dans ces unités.

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

La gérante prépare son budget. Nous prévoyons maintenant 2026 avec le modèle retenu (B), ajusté sur les **120** mois, en supposant une promotion en décembre 2026 (prévue par la gérante), pas de COVID. Outre la prévision mois par mois, on lui donne une **prévision de l'année entière** avec son incertitude, obtenue par **simulation** : on tire 2 000 trajectoires futures plausibles du modèle (en respectant la corrélation entre mois) et on additionne les 12 mois de chacune.

```python
X_2026 = pd.DataFrame({"promo": [0.0] * 11 + [1.0], "covid": [0.0] * 12},
                      index=pd.date_range("2026-01-01", periods=12, freq="MS"))
final = SARIMAX(y, exog=X, order=(1, 0, 0), seasonal_order=(0, 1, 1, 12), trend="ct").fit(disp=False, maxiter=300)
pf = final.get_forecast(12, exog=X_2026)
ic = np.asarray(pf.conf_int(alpha=0.05))
resume = pd.DataFrame({"prévision (€)": np.exp(pf.predicted_mean.values), "IC95 bas": np.exp(ic[:, 0]), "IC95 haut": np.exp(ic[:, 1])},
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
print(f"\ntotal 2025 observé : {total_2025:,.0f} €")
print(f"total 2026 prévu   : médiane {p50:,.0f} € | intervalle à 80 % [{p10:,.0f} ; {p90:,.0f}] | à 95 % [{p025:,.0f} ; {p975:,.0f}]")
print(f"croissance prévue sur 2025 : {100 * (p50 / total_2025 - 1):+.1f} %")

fig, ax = plt.subplots(figsize=(10, 3.8))
hist = v["ca"]["2023-01":]
ax.plot(hist.index, hist, color=BLEU, lw=1.6, label="observé")
ax.plot(X_2026.index, np.exp(pf.predicted_mean), color=ORANGE, lw=1.8, label="prévision 2026")
ax.fill_between(X_2026.index, np.exp(ic[:, 0]), np.exp(ic[:, 1]), color=ORANGE, alpha=0.2, label="intervalle à 95 %")
ax.set_ylabel("chiffre d'affaires mensuel (€)")
ax.legend(loc="upper left")
ax.grid(True, color="#e1e0d9", lw=0.6)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("figures/ch04-prevision-2026.png", bbox_inches="tight")
```
<!--sortie-->
```text
         prévision (€)  IC95 bas  IC95 haut
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

total 2025 observé : 27,630 €
total 2026 prévu   : médiane 29,169 € | intervalle à 80 % [27,823 ; 30,597] | à 95 % [27,073 ; 31,397]
croissance prévue sur 2025 : +5.6 %
```

![Chiffre d'affaires mensuel depuis 2023 et prévision pour 2026 (courbe orange) avec son intervalle de prévision à 95 %.](figures/ch04-prevision-2026.png)

La gérante peut retenir trois messages : (1) **le profil de l'année** : le creux de janvier, le plateau d'été, le pic de décembre ; (2) une **fourchette** de chiffre d'affaires annuel plutôt qu'un point (la fourchette à 80 % est un bon outil de budget) ; (3) une croissance attendue de l'ordre de **+5 %** sur 2025, avec une incertitude que la fourchette rend visible. Cette croissance est inférieure à la tendance de long terme de la série (environ 9 % par an, voir 4.3.4) parce que le modèle B repart du **niveau récent**, resté sous la tendance : nous verrons en 4.3.8 que ce choix est un pari sur la persistance de ces écarts.

> ⚠️ **Ce que cette prévision suppose.** Que la structure observée de 2016 à 2025 **se prolonge** (même croissance, même saisonnalité), que la promotion de décembre ait lieu, et qu'aucun choc du type COVID n'arrive (un tel choc est par nature imprévisible : les intervalles de prévision ne le contiennent pas). Une prévision n'est pas une promesse : c'est le résultat d'un modèle et d'hypothèses, qu'il faut toujours énoncer à côté du chiffre.

### 4.3.8 Révélation : comment les données ont été fabriquées

Les ventes de la boutique sont **simulées**. Il est temps de lever le voile. Voici la recette complète : une tendance exponentielle (+0,75 % par mois), une saisonnalité **déterministe** (un facteur multiplicatif par mois), un bruit **AR(1)** (coefficient 0,5, chocs de 0,07), un effet de promotion (+10 % en log), et un choc COVID (−0,55 en log, mars à juin 2020).

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
