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

C'est une régression linéaire pénalisée : les moindres carrés avec un terme $\lambda\sum\delta_j^2$. Deux réglages à choisir : le nombre $K$ d'harmoniques et la pénalité $\lambda$. Plutôt que de les fixer au hasard, on les **valide** : on apprend sur les 72 premiers mois de l'apprentissage et on évalue sur les 24 suivants (toujours dans la période d'apprentissage : le test de 2024-2025 reste intact). La grille testée croise 6 valeurs de $K$ et 5 valeurs de $\lambda$ ; elle retient $K=6$ et $\lambda=0{,}1$, avec une erreur de validation (RMSE en logarithme) de $0{,}090$.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.3 (écrire ce modèle pas à pas).

```python hide
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

Refaisons l'ajustement sur les 96 mois et prévoyons les 24 mois de test : l'erreur (RMSE en logarithme) est de $0{,}0801$, avec un biais de $+0{,}017$, pour $0{,}0679$ d'erreur d'ajustement sur l'apprentissage.

```python hide
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

Un nouveau venu doit passer **le même concours** que les autres, sans faveur. Nous ajoutons donc à la validation à origine glissante de 4.3.6 deux nouveaux concurrents : le **modèle de type Prophet** que nous venons de construire (avec les réglages $K$ et $\lambda$ retenus *sur l'apprentissage*), et le **modèle structurel** de 4.5.5. Même protocole que 4.3.6 (13 origines, 12 horizons) : on ajoute simplement deux séries de prévisions à celles de 4.3. Résultats, RMSE en logarithme :

```python hide-code
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
