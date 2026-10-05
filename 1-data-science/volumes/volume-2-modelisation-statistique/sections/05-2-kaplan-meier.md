## 5.2 L'estimateur de Kaplan-Meier

> 💡 **Intuition.** Pour savoir quelle part des clients est encore là au bout de 24 mois, on ne peut pas simplement compter ceux qui ont duré 24 mois : beaucoup de clients récents n'ont pas encore atteint cet âge. L'idée de Kaplan et Meier (1958) est de **découper le temps** : à chaque moment où quelqu'un part, on regarde *parmi ceux qui étaient encore sous observation à cet instant* quelle fraction est partie, et on **multiplie** les fractions de survie successives. Chaque client, censuré ou non, participe tant qu'il est observé, puis sort proprement du calcul.

### 5.2.1 Le principe, à la main

Reprenons nos huit clients (section 5.1.1). Les départs ont lieu aux mois 3, 5, 8 et 12. À chacun de ces instants, on se demande : *parmi les clients encore présents et observés juste avant, quelle fraction part ?*

- Mois 3 : les 8 clients sont là. Un part (A). La survie sur cet instant est $1-\tfrac18=\tfrac78=0{,}875$.
- Mois 5 : 7 clients sont là (A est parti). B part : $1-\tfrac17=\tfrac67$. La survie cumulée est $\tfrac78\times\tfrac67=0{,}75$.
- Mois 6 : C est **censuré**. Personne ne part. La courbe ne bouge pas, mais C **quitte l'ensemble à risque** : à partir de maintenant, il n'est plus compté.
- Mois 8 : il reste 5 clients (D, E, F, G, H). D part : $1-\tfrac15=\tfrac45$, survie cumulée $0{,}75\times0{,}8=0{,}6$.
- Mois 10 : E est censuré, sort de l'ensemble à risque.
- Mois 12 : il reste 3 clients (F, G, H). F part : $1-\tfrac13=\tfrac23$, survie cumulée $0{,}6\times\tfrac23=0{,}4$.
- Mois 14 : G et H sont censurés. Il n'y a plus d'autre départ : la courbe reste à 0,4.

Le nombre de clients sous observation juste avant l'instant $t_j$ s'appelle l'**ensemble à risque** (*risk set*), noté $n_j$. Le nombre de départs à $t_j$ est $d_j$. Voilà l'estimateur de Kaplan-Meier :

$$\boxed{\ \hat S(t)=\prod_{j:\,t_j\le t}\Big(1-\frac{d_j}{n_j}\Big)\ }$$

où le produit porte sur tous les instants $t_j\le t$ où au moins un départ a été observé. Les censures **n'apparaissent pas** dans la formule, mais elles agissent *indirectement* en réduisant $n_j$ : un client censuré à 6 mois compte dans les $n_j$ des instants antérieurs à 6 mois, mais plus ensuite.

Mettons ce calcul en code, sous la forme d'un tableau que nous réutiliserons :

```python
import numpy as np
import pandas as pd

def tableau_km(y, d):
    """Version pédagogique : une ligne par instant de départ, calcul direct."""
    y, d = np.asarray(y, float), np.asarray(d, int)
    lignes, S, somme_gw = [], 1.0, 0.0
    for t in np.unique(y[d == 1]):
        n = int(np.sum(y >= t))                      # ensemble à risque : encore là juste avant t
        dj = int(np.sum((y == t) & (d == 1)))        # départs à l'instant t
        cj = int(np.sum((y == t) & (d == 0)))        # censures à l'instant t (comptées après les départs)
        S *= 1 - dj / n
        somme_gw += dj / (n * (n - dj)) if n > dj else np.inf
        lignes.append((t, n, dj, cj, round(dj / n, 4), round(S, 4), round(somme_gw, 4)))
    return pd.DataFrame(lignes, columns=["t_j", "n_j (à risque)", "d_j (départs)", "censurés en t_j",
                                         "d_j/n_j", "S(t_j)", "somme Greenwood"])

y8 = np.array([3, 5, 6, 8, 10, 12, 14, 14])
d8 = np.array([1, 1, 0, 1, 0, 1, 0, 0])
print(tableau_km(y8, d8).to_string(index=False))
```
<!--sortie-->
```text
 t_j  n_j (à risque)  d_j (départs)  censurés en t_j  d_j/n_j  S(t_j)  somme Greenwood
 3.0               8              1                0   0.1250   0.875           0.0179
 5.0               7              1                0   0.1429   0.750           0.0417
 8.0               5              1                0   0.2000   0.600           0.0917
12.0               3              1                0   0.3333   0.400           0.2583
```

On retrouve les valeurs de la main : $0{,}875\to0{,}75\to0{,}6\to0{,}4$. La dernière colonne servira au 5.2.3.

> 📐 **Pourquoi cette formule, et pourquoi est-elle « la bonne » ?** Deux justifications.
>
> *Par les probabilités conditionnelles.* Découpons l'axe du temps en intervalles autour des instants de départ. Survivre au-delà de $t$ revient à survivre à chacun des instants de départ précédents *en ayant survécu aux précédents* :
> $$S(t)=\prod_{j:\,t_j\le t}P(T>t_j\mid T\ge t_j)=\prod_{j}(1-h_j),\qquad h_j=P(T=t_j\mid T\ge t_j).$$
> Le « risque discret » $h_j$ se lit directement dans les données : parmi les $n_j$ clients à risque, $d_j$ partent, d'où l'estimation naturelle $\hat h_j=d_j/n_j$.
>
> *Par le maximum de vraisemblance.* Supposons que la loi de $T$ ne charge que les instants observés, avec des risques $h_1,\dots,h_J$ libres. À l'instant $t_j$, parmi les $n_j$ clients à risque, $d_j$ partent (probabilité $h_j$ chacun) et $n_j-d_j$ restent (probabilité $1-h_j$). Les censures n'ajoutent aucun facteur en $h_j$ au-delà de leur participation aux $n_j$. La vraisemblance (section 5.1.5) est donc
> $$L(h_1,\dots,h_J)=\prod_{j=1}^J h_j^{d_j}(1-h_j)^{n_j-d_j}.$$
> Chaque facteur est une vraisemblance binomiale ; on le maximise séparément en $\hat h_j=d_j/n_j$. Kaplan-Meier est donc l'**estimateur du maximum de vraisemblance non paramétrique** de la fonction de survie : on ne suppose *aucune forme* pour $S$.

### 5.2.2 L'estimateur sur les 2 000 clients, comparé aux bibliothèques

La version précédente boucle sur chaque instant et chaque client : c'est lisible, mais lent sur 2 000 clients. Voici une version vectorisée, qui prend en charge aussi les **entrées tardives** (nous en aurons besoin au 5.2.6), et que nous réutiliserons pour tout le chapitre.

```python
def kaplan_meier(y, d, entree=None):
    """Kaplan-Meier vectorisé. Retourne (t_j, n_j, d_j, S, somme_greenwood).
    entree : date d'entrée dans l'observation (troncature à gauche), 0 par défaut."""
    y, d = np.asarray(y, float), np.asarray(d, int)
    tj = np.unique(y[d == 1])
    y_tries = np.sort(y)
    departs = np.sort(y[d == 1])
    sorties_avant = np.searchsorted(y_tries, tj, side="left")                # clients sortis strictement avant t_j
    entres_avant = len(y) if entree is None else np.searchsorted(np.sort(np.asarray(entree, float)), tj, side="left")
    n = entres_avant - sorties_avant                                          # à risque : entrés avant t_j et pas encore sortis
    dj = np.searchsorted(departs, tj, side="right") - np.searchsorted(departs, tj, side="left")
    S = np.cumprod(1 - dj / n)
    with np.errstate(divide="ignore"):
        gw = np.cumsum(dj / (n * (n - dj)))
    return tj, n, dj, S, gw

def surv_at(t, tj, S, avant=1.0):
    """Valeur de la fonction en escalier S à l'instant t (avant = valeur avant le premier départ)."""
    i = np.searchsorted(tj, t, side="right") - 1
    return avant if i < 0 else S[i]

# 1) la version rapide redonne exactement le tableau des 8 clients
tj8, n8, dj8, S8, gw8 = kaplan_meier(y8, d8)
print("8 clients, S aux instants de départ :", S8.round(4), "| à risque :", n8)

# 2) sur les 2000 clients
c = pd.read_csv("donnees/clients.csv")
y, d = c["duree_mois"].to_numpy(), c["churn"].to_numpy()
tj, n, dj, S, gw = kaplan_meier(y, d)
print("instants de départ distincts :", len(tj), "pour", int(d.sum()), "départs")
print("instants avec plusieurs départs simultanés (ex aequo) :", int((dj > 1).sum()))
```
<!--sortie-->
```text
8 clients, S aux instants de départ : [0.875 0.75  0.6   0.4  ] | à risque : [8 7 5 3]
instants de départ distincts : 882 pour 977 départs
instants avec plusieurs départs simultanés (ex aequo) : 91
```

Comme les durées sont mesurées au centième de mois, quelques départs coïncident (les *ex aequo*) ; la formule les traite d'un seul bloc : $d_j>1$. Comparons maintenant à `statsmodels` et au paquet R de référence, `survival`, à plusieurs instants :

```python
from statsmodels.duration.survfunc import SurvfuncRight

sf = SurvfuncRight(y, d)
print(f"{'mois':>5} {'à la main':>10} {'statsmodels':>12} {'ET (Greenwood)':>15} {'ET statsmodels':>15}")
for t in (12, 24, 36, 48, 60):
    i = np.searchsorted(sf.surv_times, t, side="right") - 1
    s_main = surv_at(t, tj, S)
    et_main = s_main * np.sqrt(surv_at(t, tj, gw, avant=0.0))
    print(f"{t:>5} {s_main:>10.5f} {sf.surv_prob[i]:>12.5f} {et_main:>15.5f} {sf.surv_prob_se[i]:>15.5f}")
```
<!--sortie-->
```text
 mois  à la main  statsmodels  ET (Greenwood)  ET statsmodels
   12    0.82519      0.82519         0.00888         0.00888
   24    0.63376      0.63376         0.01211         0.01211
   36    0.45275      0.45275         0.01396         0.01396
   48    0.30758      0.30758         0.01498         0.01498
   60    0.24754      0.24754         0.01558         0.01558
```

```r
library(survival)
clients <- read.csv("donnees/clients.csv")
km_all <- survfit(Surv(duree_mois, churn) ~ 1, data = clients)
print(summary(km_all, times = c(12, 24, 36, 48, 60)))
```
<!--sortie-->
```text
Call: survfit(formula = Surv(duree_mois, churn) ~ 1, data = clients)

 time n.risk n.event survival std.err lower 95% CI upper 95% CI
   12   1378     323    0.825 0.00888        0.808        0.843
   24    814     286    0.634 0.01211        0.610        0.658
   36    416     200    0.453 0.01396        0.426        0.481
   48    186     111    0.308 0.01498        0.280        0.338
   60     96      31    0.248 0.01558        0.219        0.280
```

Les trois sources donnent la même courbe et les mêmes erreurs standard. Lecture : **82,5 %** des clients sont encore là à 12 mois, **63,4 %** à 24 mois, **45,3 %** à 36 mois, et **24,8 %** à 60 mois. La colonne `n.risk` de R est instructive : à 60 mois, il ne reste que 96 clients sous observation, contre 1 378 à 12 mois. Ce sont les *clients récents*, sortis de l'ensemble à risque par censure, qui font fondre l'effectif.

Voyons maintenant la courbe. Nous y superposons le modèle **exponentiel** de la section 5.1.5 (risque constant, $\hat\lambda=0{,}0209$ par mois) pour juger de sa pertinence :

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
z = 1.959964
bas = S ** np.exp(z * np.sqrt(gw) / np.abs(np.log(S)))        # IC log-log, voir 5.2.3
haut = S ** np.exp(-z * np.sqrt(gw) / np.abs(np.log(S)))
temps = np.concatenate([[0], tj])

fig, ax = plt.subplots(figsize=(7.4, 4.2))
ax.step(temps, np.concatenate([[1], S]), where="post", color=BLEU, lw=2)
ax.fill_between(temps, np.concatenate([[1], bas]), np.concatenate([[1], haut]), step="post", color=BLEU, alpha=0.18, lw=0)
grille = np.linspace(0, 84, 200)
ax.plot(grille, np.exp(-(d.sum() / y.sum()) * grille), color=ORANGE, lw=1.8, ls="--")
ax.axhline(0.5, color="#c3c2b7", lw=0.8)
ax.legend(handles=[Line2D([0], [0], color=BLEU, lw=2, label="Kaplan-Meier (bande : IC 95 %)"),
                   Line2D([0], [0], color=ORANGE, lw=1.8, ls="--", label="modèle exponentiel (risque constant)")],
          loc="lower left", frameon=False, fontsize=10)
ax.set_xlabel("mois depuis l'inscription")
ax.set_ylabel("proportion de clients encore là")
ax.set_xlim(0, 84)
ax.set_ylim(0, 1.02)
plt.tight_layout()
plt.savefig("figures/ch05-km-global.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Courbe de Kaplan-Meier des 2 000 clients de Dar Jasmin, avec son intervalle de confiance à 95 %, et courbe du modèle exponentiel ajusté par maximum de vraisemblance.](figures/ch05-km-global.png)

La courbe exponentielle passe **sous** Kaplan-Meier pendant les 28 premiers mois environ (elle prévoit trop de départs précoces), croise la courbe vers 30 mois, puis reste **au-dessus** ensuite (elle prévoit trop peu de départs tardifs). Ce schéma est la signature d'un risque qui **augmente** avec l'ancienneté : un risque constant ne peut pas le reproduire. La section 5.4 le confirmera. C'est un avantage décisif de Kaplan-Meier : il ne parie sur aucune forme.

### 5.2.3 Précision : la variance de Greenwood et les intervalles de confiance

Une courbe sans mesure d'incertitude est un dessin, pas un résultat. Que vaut $\hat S(t)$ ? Reprenons le raisonnement binomial.

> 📐 **La formule de Greenwood.** À l'instant $t_j$, parmi $n_j$ clients à risque, la fraction qui survit est $\hat p_j=1-d_j/n_j$. Conditionnellement à $n_j$, $d_j$ est binomial : $\mathrm{Var}(\hat p_j)\approx p_j(1-p_j)/n_j$. Comme $\ln\hat S(t)=\sum_j\ln\hat p_j$, la **méthode delta** (qui approche la variance d'une fonction régulière $g$ d'une quantité aléatoire : $\mathrm{Var}\,g(X)\approx g'(E[X])^2\,\mathrm{Var}\,X$) donne
> $$\mathrm{Var}(\ln\hat p_j)\approx\frac{\mathrm{Var}(\hat p_j)}{p_j^2}=\frac{1-p_j}{n_jp_j}\approx\frac{d_j}{n_j(n_j-d_j)}.$$
> Les facteurs des différents instants sont (conditionnellement) non corrélés, donc les variances s'additionnent :
> $$\mathrm{Var}\big(\ln\hat S(t)\big)\approx\sum_{j:\,t_j\le t}\frac{d_j}{n_j(n_j-d_j)},\qquad\mathrm{Var}\big(\hat S(t)\big)\approx\hat S(t)^2\sum_{j:\,t_j\le t}\frac{d_j}{n_j(n_j-d_j)}.$$
> C'est la **formule de Greenwood** : la dernière colonne de notre tableau (la « somme Greenwood ») en est la somme partielle.

Sur nos huit clients à $t=12$ : $\hat S=0{,}4$ et la somme vaut $0{,}2583$, donc l'écart-type est $0{,}4\sqrt{0{,}2583}\approx0{,}20$ : énorme, ce qui n'a rien d'étonnant avec huit clients.

Pour un intervalle de confiance, on peut prendre $\hat S\pm1{,}96\,\widehat{se}$ (intervalle **plan**), mais il peut sortir de $[0,1]$ et se comporte mal quand $\hat S$ est proche de 0 ou de 1. On préfère transformer d'abord :

- **intervalle « log »** (le défaut de R) : $\hat S\,\exp\!\big(\pm1{,}96\sqrt{G(t)}\big)$, avec $G(t)=\sum d_j/[n_j(n_j-d_j)]$ ;
- **intervalle « log-log »**, souvent recommandé : on travaille sur $\ln(-\ln\hat S)$, dont la variance est $G(t)/(\ln\hat S)^2$, ce qui donne $\hat S^{\,\exp(\pm1{,}96\sqrt{G(t)}/|\ln\hat S|)}$ (les bornes restent toujours dans $[0,1]$).

```python
def intervalles(t, tj, S, gw, z=1.959964):
    s, g = surv_at(t, tj, S), surv_at(t, tj, gw, avant=0.0)
    se = s * np.sqrt(g)
    plan = (s - z * se, s + z * se)
    log_ = (s * np.exp(-z * np.sqrt(g)), s * np.exp(z * np.sqrt(g)))
    expo = np.exp(z * np.sqrt(g) / abs(np.log(s)))
    loglog = (s ** expo, s ** (1 / expo))
    return s, plan, log_, loglog

for t in (36, 60):
    s, plan, log_, loglog = intervalles(t, tj, S, gw)
    print(f"t = {t} mois : S = {s:.4f}")
    print(f"   plan   [{plan[0]:.4f} ; {plan[1]:.4f}]")
    print(f"   log    [{log_[0]:.4f} ; {log_[1]:.4f}]")
    print(f"   log-log[{loglog[0]:.4f} ; {loglog[1]:.4f}]")
print()
s8, plan8, log8, ll8 = intervalles(12, tj8, S8, gw8)
print(f"8 clients, t = 12 : S = {s8:.2f} ; plan [{plan8[0]:.2f} ; {plan8[1]:.2f}] ; log-log [{ll8[0]:.2f} ; {ll8[1]:.2f}]")
```
<!--sortie-->
```text
t = 36 mois : S = 0.4528
   plan   [0.4254 ; 0.4801]
   log    [0.4262 ; 0.4810]
   log-log[0.4252 ; 0.4799]
t = 60 mois : S = 0.2475
   plan   [0.2170 ; 0.2781]
   log    [0.2188 ; 0.2800]
   log-log[0.2176 ; 0.2786]

8 clients, t = 12 : S = 0.40 ; plan [0.00 ; 0.80] ; log-log [0.07 ; 0.73]
```

```r
for (ct in c("plain", "log", "log-log")) {
  f <- survfit(Surv(duree_mois, churn) ~ 1, data = clients, conf.type = ct)
  s <- summary(f, times = c(36, 60))
  cat(sprintf("%-8s t=36 [%.4f ; %.4f]   t=60 [%.4f ; %.4f]\n", ct, s$lower[1], s$upper[1], s$lower[2], s$upper[2]))
}
```
<!--sortie-->
```text
plain    t=36 [0.4254 ; 0.4801]   t=60 [0.2170 ; 0.2781]
log      t=36 [0.4262 ; 0.4810]   t=60 [0.2188 ; 0.2800]
log-log  t=36 [0.4252 ; 0.4799]   t=60 [0.2176 ; 0.2786]
```

Nos trois intervalles coïncident avec ceux de R à la quatrième décimale. Sur 2 000 clients, ils sont presque identiques ; la différence se voit sur les petits effectifs : avec les huit clients, l'intervalle plan est large (de presque 0 à 0,80), et le log-log est plus raisonnable. Ces intervalles s'interprètent comme au volume I (section 3.3.2) : la *méthode* encadre la vraie valeur dans 95 % des échantillons.

### 5.2.4 Médiane, quantiles et durée moyenne « restreinte »

**La médiane de survie** est le premier instant où la courbe passe sous 0,5. C'est le bon résumé de la « durée typique » : contrairement à la moyenne, elle est définie dès que la courbe descend sous 0,5, même si certains clients ne sont jamais partis. Son intervalle de confiance s'obtient en cherchant où la **bande de confiance** de la courbe coupe le niveau 0,5 (méthode de Brookmeyer et Crowley) :

```python
z = 1.959964
S_bas, S_haut = S * np.exp(-z * np.sqrt(gw)), S * np.exp(z * np.sqrt(gw))      # bande « log »
med = tj[S <= 0.5][0]
print(f"médiane de survie : {med:.2f} mois ; IC95 [{tj[S_bas <= 0.5][0]:.1f} ; {tj[S_haut <= 0.5][0]:.1f}]")
print("statsmodels       :", round(sf.quantile(0.5), 2))
```
<!--sortie-->
```text
médiane de survie : 32.45 mois ; IC95 [29.9 ; 34.2]
statsmodels       : 32.45
```

```r
print(km_all)
```
<!--sortie-->
```text
Call: survfit(formula = Surv(duree_mois, churn) ~ 1, data = clients)

        n events median 0.95LCL 0.95UCL
[1,] 2000    977   32.5    29.9    34.2
```

La médiane est d'environ **32,5 mois** (IC95 : 29,9 à 34,2). La moitié des clients ont quitté Dar Jasmin au bout de deux ans et huit mois et demi. Notez que ce chiffre est bien supérieur à la moyenne « naïve » de 23 mois de la section 5.1.

**Et la durée moyenne ?** Nous savons que $E[T]=\int_0^\infty S(t)\,dt$. Mais Kaplan-Meier ne descend pas jusqu'à zéro : le dernier client est censuré, et la courbe s'arrête à 0,11 (dernier départ au mois 80,2). L'aire totale n'est pas définie ; elle dépend de ce que l'on suppose *au-delà* des données. On calcule donc la **durée moyenne restreinte** (en anglais *restricted mean survival time*, RMST) jusqu'à un horizon $\tau$ choisi :
$$\mathrm{RMST}(\tau)=\int_0^{\tau}\hat S(t)\,dt.$$
C'est le **nombre moyen de mois passés dans la clientèle pendant les $\tau$ premiers mois**. Comme $\hat S$ est une fonction en escalier, l'intégrale est une somme de rectangles. À la main, pour nos huit clients et $\tau=14$ : $3\times1+2\times0{,}875+3\times0{,}75+4\times0{,}6+2\times0{,}4=3+1{,}75+2{,}25+2{,}4+0{,}8=10{,}2$ mois. (Ni 9 mois ni 7 mois : on a bien utilisé l'information des censurés.)

```python
def rmst(tj, S, tau):
    """Aire sous la courbe en escalier de 0 à tau."""
    bornes = np.concatenate([[0.0], tj[tj < tau], [tau]])
    valeurs = np.concatenate([[1.0], S[tj < tau]])
    return float(np.sum(valeurs * np.diff(bornes)))

print("8 clients, tau = 14 :", round(rmst(tj8, S8, 14), 2), "mois")
for tau in (24, 36, 60):
    print(f"2000 clients, tau = {tau} : {rmst(tj, S, tau):.2f} mois passés en moyenne dans les {tau} premiers mois")
```
<!--sortie-->
```text
8 clients, tau = 14 : 10.2 mois
2000 clients, tau = 24 : 19.76 mois passés en moyenne dans les 24 premiers mois
2000 clients, tau = 36 : 26.19 mois passés en moyenne dans les 36 premiers mois
2000 clients, tau = 60 : 33.94 mois passés en moyenne dans les 60 premiers mois
```

Sur 36 mois, un nouveau client passe en moyenne un peu plus de 26 mois dans la clientèle de Dar Jasmin, sur un maximum possible de 36. C'est une quantité très parlante pour décider (nous la retrouverons au 5.4 pour la valeur vie client), et elle ne dépend d'aucune hypothèse de forme.

### 5.2.5 Comparer des groupes : courbes et test du log-rank

Yasmine a envoyé une **offre de bienvenue** à la moitié de ses clients, **tirée au hasard**. Cette offre prolonge-t-elle la relation ? Et le canal d'acquisition joue-t-il un rôle ? Traçons Kaplan-Meier par groupe, avec les bandes de confiance log-log.

```python
def courbe_groupe(y, d, masque):
    t_, n_, d_, S_, g_ = kaplan_meier(y[masque], d[masque])
    b = S_ ** np.exp(1.959964 * np.sqrt(g_) / np.abs(np.log(S_)))
    h = S_ ** np.exp(-1.959964 * np.sqrt(g_) / np.abs(np.log(S_)))
    return t_, S_, b, h

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
off = c["offre_bienvenue"].to_numpy()
for val, couleur, nom in [(0, VIOLET, "sans offre"), (1, AQUA, "avec offre")]:
    t_, S_, b, h = courbe_groupe(y, d, off == val)
    x = np.concatenate([[0], t_])
    ax1.step(x, np.concatenate([[1], S_]), where="post", color=couleur, lw=2)
    ax1.fill_between(x, np.concatenate([[1], b]), np.concatenate([[1], h]), step="post", color=couleur, alpha=0.15, lw=0)
ax1.legend(handles=[Line2D([0], [0], color=AQUA, lw=2, label="avec offre"), Line2D([0], [0], color=VIOLET, lw=2, label="sans offre")],
           loc="lower left", frameon=False, fontsize=10)
ax1.set_title("Selon l'offre de bienvenue (attribuée au hasard)")
canaux = [("Boutique", AQUA), ("Site", BLEU), ("Instagram", ORANGE)]
for nom, couleur in canaux:
    t_, S_, b, h = courbe_groupe(y, d, (c["canal_acquisition"] == nom).to_numpy())
    x = np.concatenate([[0], t_])
    ax2.step(x, np.concatenate([[1], S_]), where="post", color=couleur, lw=2)
    ax2.fill_between(x, np.concatenate([[1], b]), np.concatenate([[1], h]), step="post", color=couleur, alpha=0.15, lw=0)
ax2.legend(handles=[Line2D([0], [0], color=c_, lw=2, label=n_) for n_, c_ in canaux], loc="lower left", frameon=False, fontsize=10)
ax2.set_title("Selon le canal d'acquisition")
for ax in (ax1, ax2):
    ax.axhline(0.5, color="#c3c2b7", lw=0.8)
    ax.set_xlabel("mois depuis l'inscription")
    ax.set_xlim(0, 84)
    ax.set_ylim(0, 1.02)
ax1.set_ylabel("proportion de clients encore là")
plt.tight_layout()
plt.savefig("figures/ch05-km-groupes.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Courbes de Kaplan-Meier par groupe, avec bandes de confiance à 95 % : à gauche selon l'offre de bienvenue, à droite selon le canal d'acquisition.](figures/ch05-km-groupes.png)

Les courbes avec et sans offre se séparent nettement et durablement ; à droite, Boutique est au-dessus de Site, lui-même au-dessus d'Instagram (les bandes de Boutique et de Site se chevauchent par endroits). Résumons chaque groupe (médiane de survie et durée moyenne restreinte à 36 mois) :

```python
resume = []
for var in ["offre_bienvenue", "canal_acquisition"]:
    for valeur, g in c.groupby(var):
        t_, n_, d_, S_, gw_ = kaplan_meier(g["duree_mois"], g["churn"])
        m = t_[S_ <= 0.5]
        resume.append({"variable": var, "groupe": valeur, "clients": len(g), "départs": int(g["churn"].sum()),
                       "médiane (mois)": round(m[0], 1) if len(m) else np.nan, "RMST 36 mois": round(rmst(t_, S_, 36), 2)})
print(pd.DataFrame(resume).to_string(index=False))
```
<!--sortie-->
```text
         variable    groupe  clients  départs  médiane (mois)  RMST 36 mois
  offre_bienvenue         0      985      528            28.2         24.62
  offre_bienvenue         1     1015      449            36.6         27.69
canal_acquisition  Boutique      504      212            41.2         29.10
canal_acquisition Instagram      816      443            26.4         23.93
canal_acquisition      Site      680      322            34.1         26.67
```

Les chiffres sont éloquents : sans offre, la médiane est de 28 mois ; avec l'offre, de près de 37. Mais est-ce un vrai effet ou le hasard de l'échantillonnage ? Il faut un **test**.

**Le test du log-rank.** C'est le test de référence pour comparer deux courbes de survie (ou plus). Son principe est celui du volume I (section 3.4), appliqué *à chaque instant de départ* : à l'instant $t_j$, $d_j$ départs ont lieu parmi $n_j$ clients à risque, dont $n_{1j}$ dans le groupe 1. Si les deux groupes avaient **le même risque** (hypothèse nulle), les $d_j$ départs seraient répartis « au hasard » entre les clients à risque, et le nombre de départs dans le groupe 1 suivrait une loi **hypergéométrique** :
$$E_{1j}=d_j\frac{n_{1j}}{n_j},\qquad V_j=d_j\,\frac{n_{1j}}{n_j}\Big(1-\frac{n_{1j}}{n_j}\Big)\frac{n_j-d_j}{n_j-1}.$$
On additionne, sur tous les instants, les écarts entre départs observés $O_1$ et attendus $E_1=\sum_jE_{1j}$ :
$$\chi^2=\frac{(O_1-E_1)^2}{\sum_jV_j}\ \approx\ \chi^2_1\quad\text{sous }H_0.$$
Pour $K$ groupes, on utilise la forme quadratique du vecteur $(O_k-E_k)_{k<K}$ avec la matrice de covariance correspondante : $\chi^2_{K-1}$.

**À la main, sur les huit clients.** Imaginons que C, E, F et G aient reçu l'offre, et A, B, D et H non. Aux quatre instants de départ :

| $t_j$ | $n_j$ | $n_{1j}$ (avec offre) | $d_j$ | qui part | $E_{1j}=d_jn_{1j}/n_j$ | $V_j$ |
|---|---|---|---|---|---|---|
| 3 | 8 | 4 | 1 | A (sans offre) | 0,500 | 0,250 |
| 5 | 7 | 4 | 1 | B (sans offre) | 0,571 | 0,245 |
| 8 | 5 | 3 | 1 | D (sans offre) | 0,600 | 0,240 |
| 12 | 3 | 2 | 1 | F (avec offre) | 0,667 | 0,222 |

Le groupe « avec offre » a eu $O_1=1$ départ pour $E_1=2{,}338$ attendus ; $\sum V_j=0{,}957$ ; $\chi^2=(1-2{,}338)^2/0{,}957=1{,}87$, soit $p\approx0{,}17$ : avec huit clients, aucune conclusion, évidemment. Le code généralise à $K$ groupes :

```python
from scipy import stats

def logrank(y, d, groupe):
    """Test du log-rank à K groupes. Retourne (observés, attendus, chi2, ddl, p)."""
    y, d, groupe = np.asarray(y, float), np.asarray(d, int), np.asarray(groupe)
    niveaux = np.unique(groupe)
    K = len(niveaux)
    O, E, V = np.zeros(K), np.zeros(K), np.zeros((K, K))
    for t in np.unique(y[d == 1]):
        r = np.array([np.sum((y >= t) & (groupe == g)) for g in niveaux], float)
        o = np.array([np.sum((y == t) & (d == 1) & (groupe == g)) for g in niveaux], float)
        n_, dj_ = r.sum(), o.sum()
        O += o
        E += dj_ * r / n_
        if n_ > 1:
            V += dj_ * (n_ - dj_) / (n_ - 1) * (np.diag(r) / n_ - np.outer(r, r) / n_**2)
    x = (O - E)[:-1]
    chi2 = float(x @ np.linalg.solve(V[:-1, :-1], x))
    return O, E, chi2, K - 1, stats.chi2.sf(chi2, K - 1)

groupe8 = np.array(["sans", "sans", "avec", "sans", "avec", "avec", "avec", "sans"])      # A..H
O8, E8, chi8, ddl8, p8 = logrank(y8, d8, groupe8)
print(f"8 clients : observés {O8} | attendus {E8.round(3)} | chi2 = {chi8:.2f} | p = {p8:.3f}")
```
<!--sortie-->
```text
8 clients : observés [1. 3.] | attendus [2.338 1.662] | chi2 = 1.87 | p = 0.171
```

Appliquons maintenant le test aux données réelles : à la main, avec `statsmodels`, avec R.

```python
from statsmodels.duration.survfunc import survdiff

O, E, chi2, ddl, p = logrank(y, d, c["offre_bienvenue"])
print(f"À la main    : observés (sans, avec) = {O.astype(int)}, attendus = {E.round(1)}, chi2 = {chi2:.2f}, p = {p:.1e}")
print("statsmodels  : chi2 = %.2f, p = %.1e" % survdiff(y, d, c["offre_bienvenue"]))
```
<!--sortie-->
```text
À la main    : observés (sans, avec) = [528 449], attendus = [435.6 541.4], chi2 = 35.54, p = 2.5e-09
statsmodels  : chi2 = 35.54, p = 2.5e-09
```

```r
print(survdiff(Surv(duree_mois, churn) ~ offre_bienvenue, data = clients))
```
<!--sortie-->
```text
Call:
survdiff(formula = Surv(duree_mois, churn) ~ offre_bienvenue, 
    data = clients)

                     N Observed Expected (O-E)^2/E (O-E)^2/V
offre_bienvenue=0  985      528      436      19.6      35.5
offre_bienvenue=1 1015      449      541      15.8      35.5

 Chisq= 35.5  on 1 degrees of freedom, p= 3e-09 
```

Les trois calculs donnent $\chi^2\approx35{,}5$ ($p\approx3\times10^{-9}$) : dans le groupe avec offre, on observe 449 départs là où l'on en attendrait 541 si l'offre ne changeait rien ; dans le groupe sans offre, 528 au lieu de 436. L'offre étant attribuée **au hasard**, la différence peut être lue comme **l'effet causal de l'offre** sur la durée de la relation (nous reviendrons sur la mesure de cet effet au 5.3).

Pour le canal d'acquisition (trois groupes, $\chi^2_2$) puis les comparaisons deux à deux, avec la correction de **Holm** du volume I (section 3.5.5) :

```python
O3, E3, chi3, ddl3, p3 = logrank(y, d, c["canal_acquisition"])
print(f"3 canaux : chi2 = {chi3:.1f} à {ddl3} ddl, p = {p3:.1e}")
print(pd.DataFrame({"observés": O3.astype(int), "attendus": E3.round(1)}, index=np.unique(c["canal_acquisition"])).T.to_string())

paires = [("Boutique", "Instagram"), ("Boutique", "Site"), ("Site", "Instagram")]
brutes = []
for a, b in paires:
    m = c["canal_acquisition"].isin([a, b]).to_numpy()
    brutes.append(logrank(y[m], d[m], c["canal_acquisition"].to_numpy()[m])[4])
ordre = np.argsort(brutes)
holm, courant = np.empty(3), 0.0
for rang, i in enumerate(ordre):
    courant = max(courant, min(1.0, (3 - rang) * brutes[i]))
    holm[i] = courant
print(pd.DataFrame({"comparaison": [f"{a} / {b}" for a, b in paires], "p brute": brutes, "p Holm": holm}).to_string(index=False,
      float_format=lambda x: f"{x:.2e}"))
```
<!--sortie-->
```text
3 canaux : chi2 = 55.0 à 2 ddl, p = 1.1e-12
          Boutique  Instagram   Site
observés     212.0      443.0  322.0
attendus     296.5      342.4  338.1
         comparaison  p brute   p Holm
Boutique / Instagram 5.27e-13 1.58e-12
     Boutique / Site 8.61e-04 8.61e-04
    Site / Instagram 3.02e-05 6.05e-05
```

Les trois canaux diffèrent ($\chi^2_2=55{,}0$). Deux à deux, toutes les comparaisons restent significatives après correction de Holm : la plus nette oppose Boutique et Instagram (p de l'ordre de $10^{-12}$), la plus faible Boutique et Site (p $\approx9\times10^{-4}$). Les clients arrivés par la boutique restent le plus longtemps, ceux d'Instagram partent le plus vite : 212 départs observés en Boutique contre 296 attendus sous l'hypothèse « aucune différence », mais 443 contre 342 pour Instagram.

**Autres pondérations.** Le log-rank donne le **même poids** à tous les instants ; il est le plus puissant quand les risques des groupes sont **proportionnels** (section 5.3). D'autres tests pondèrent davantage le début (Gehan-Breslow, Tarone-Ware, Fleming-Harrington) ; ils sont plus sensibles aux différences précoces et moins aux différences tardives :

```python
for nom, w, kw in [("log-rank", None, {}), ("Gehan-Breslow", "gb", {}), ("Tarone-Ware", "tw", {}), ("Fleming-Harrington p=1", "fh", {"fh_p": 1})]:
    chi, pv = survdiff(y, d, c["offre_bienvenue"], weight_type=w, **kw)
    print(f"{nom:<24} chi2 = {chi:6.2f}   p = {pv:.1e}")
```
<!--sortie-->
```text
log-rank                 chi2 =  35.54   p = 2.5e-09
Gehan-Breslow            chi2 =  31.45   p = 2.0e-08
Tarone-Ware              chi2 =  35.12   p = 3.1e-09
Fleming-Harrington p=1   chi2 =  34.98   p = 3.3e-09
```

```r
print(survdiff(Surv(duree_mois, churn) ~ offre_bienvenue, data = clients, rho = 1)$chisq)
```
<!--sortie-->
```text
[1] 34.97764
```

Le dernier test (Fleming-Harrington, `rho = 1` dans R) donne le même $\chi^2$ dans les deux logiciels. Ici, toutes les pondérations concluent de la même façon. Quand elles divergent, c'est un signal qu'**il se passe quelque chose de différent selon l'âge de la relation** (par exemple des courbes qui se croisent) : on regarde alors les courbes plutôt que de choisir le test qui nous arrange.

> ⚠️ **Le choix du test ne se fait pas après avoir vu les résultats.** Décidez de la pondération *avant* (par défaut, le log-rank). Essayer plusieurs tests et ne retenir que le meilleur est un cas de tests multiples (volume I, section 3.5.5).

### 5.2.6 Quand les clients entrent tard : la troncature à gauche

Nous avons promis (5.1.4) de montrer comment traiter les **entrées tardives**. Imaginons que Yasmine n'ait enregistré les clients qu'à partir de leur **adhésion au programme de fidélité**, qui peut intervenir longtemps après le premier achat. On mesure la durée depuis le premier achat, mais un client n'apparaît dans la base que s'il était **encore client** à sa date d'adhésion. Les clients partis avant n'ont jamais été vus.

La règle est simple : **un client n'est dans l'ensemble à risque à l'instant $t$ que s'il est entré dans l'observation avant $t$ et n'en est pas encore sorti** :
$$n_j=\#\{i:\ e_i<t_j\le y_i\}.$$
Ignorer cette règle (prendre $e_i=0$ pour tout le monde) revient à compter, dans les ensembles à risque des premiers mois, des clients qui *n'étaient pas encore observables* ; on sous-estime le risque précoce et on **surestime la survie**. Vérifions par simulation, avec une vérité connue :

```python
rng = np.random.default_rng(52)
N = 6000
T = 36 * rng.weibull(1.35, N)                 # durées vraies (Weibull, comme en 5.1)
E = rng.uniform(0, 30, N)                     # date d'adhésion au programme (mois après le 1er achat)
vus = T > E                                   # seuls les clients encore là à l'adhésion sont enregistrés
Tv, Ev = T[vus], E[vus]
Cv = Ev + rng.uniform(6, 60, vus.sum())       # fin d'observation après l'adhésion
Yv, Dv = np.minimum(Tv, Cv), (Tv <= Cv).astype(int)

tj_n, _, _, S_n, _ = kaplan_meier(Yv, Dv)                       # on ignore les entrées tardives
tj_c, _, _, S_c, _ = kaplan_meier(Yv, Dv, entree=Ev)             # on les prend en compte
sf_e = SurvfuncRight(Yv, Dv, entry=Ev)
print(f"clients vus : {vus.sum()} sur {N}")
print(f"{'mois':>5} {'vraie S(t)':>11} {'ignorer entrée':>15} {'avec entrée':>12} {'statsmodels':>12}")
for t in (6, 12, 24, 36):
    i = np.searchsorted(sf_e.surv_times, t, side="right") - 1
    print(f"{t:>5} {np.exp(-(t / 36) ** 1.35):>11.3f} {surv_at(t, tj_n, S_n):>15.3f} {surv_at(t, tj_c, S_c):>12.3f} {sf_e.surv_prob[i]:>12.3f}")
```
<!--sortie-->
```text
clients vus : 4417 sur 6000
 mois  vraie S(t)  ignorer entrée  avec entrée  statsmodels
    6       0.915           0.988        0.913        0.913
   12       0.797           0.940        0.804        0.804
   24       0.561           0.759        0.577        0.577
   36       0.368           0.490        0.365        0.365
```

Les estimations qui **ignorent** l'entrée surestiment fortement la survie : 0,76 au lieu de 0,56 à 24 mois, par exemple. Celles qui **la prennent en compte** (à la main comme avec `statsmodels`, qui donnent exactement les mêmes valeurs) restent à environ deux points de la vérité à tous les horizons. Cet exemple n'est pas qu'académique : il explique pourquoi l'on dit que **la survie d'« ex-clients encore actifs » ou de patients « prévalents » est toujours plus belle que la réalité**.

### 5.2.7 Pièges et analyses de sensibilité

> ⚠️ **La queue de la courbe est fragile.** Quand l'ensemble à risque devient petit (ici : moins de 100 clients au-delà de 60 mois, 7 avant le dernier départ), un seul départ fait chuter la courbe de plusieurs points. On présente toujours sous la courbe le **nombre de clients à risque** et on arrête l'interprétation là où il devient trop faible.

```python
instants = [0, 12, 24, 36, 48, 60, 72]
tab = {}
for nom, masque in [("sans offre", off == 0), ("avec offre", off == 1)]:
    tab[nom] = [int(np.sum(y[masque] >= t)) for t in instants]
print(pd.DataFrame(tab, index=[f"{t} mois" for t in instants]).T.to_string())
```
<!--sortie-->
```text
            0 mois  12 mois  24 mois  36 mois  48 mois  60 mois  72 mois
sans offre     985      647      359      179       70       29       13
avec offre    1015      731      455      237      116       67       24
```

> ⚠️ **La censure non informative est une hypothèse, pas un fait.** À la section 5.1.4, nous avons vu que 363 clients sont des *pertes de vue*. Et si, en réalité, tous étaient partis sans prévenir ? Une **analyse de sensibilité du pire cas** consiste à les recompter comme des départs, à la date où l'on les perd de vue : la vraie courbe se trouve alors entre les deux.

```python
c["date_inscription"] = pd.to_datetime(c["date_inscription"])
suivi_possible = (pd.Timestamp("2025-12-31") - c["date_inscription"]).dt.days / 30.4375
perdu = ((c["churn"] == 0) & (suivi_possible - c["duree_mois"] > 0.01)).to_numpy()

d_pire = np.where(perdu, 1, d)
tj_p, _, _, S_p, _ = kaplan_meier(y, d_pire)
print(f"pertes de vue recomptées comme départs : {perdu.sum()}")
print(f"{'mois':>5} {'censure non informative':>24} {'pire cas':>10}")
for t in (12, 24, 36):
    print(f"{t:>5} {surv_at(t, tj, S):>24.3f} {surv_at(t, tj_p, S_p):>10.3f}")
chi_pire = logrank(y, d_pire, c["offre_bienvenue"])[2]
print(f"log-rank offre / sans offre, pire cas : chi2 = {chi_pire:.1f} (standard : 35.5)")
```
<!--sortie-->
```text
pertes de vue recomptées comme départs : 363
 mois  censure non informative   pire cas
   12                    0.825      0.753
   24                    0.634      0.526
   36                    0.453      0.341
log-rank offre / sans offre, pire cas : chi2 = 27.4 (standard : 35.5)
```

À 36 mois, la survie est de **45 %** sous l'hypothèse standard et de **34 %** dans le pire cas : l'incertitude liée à nos 363 pertes de vue pèse onze points, bien plus que l'incertitude statistique (l'intervalle à 95 % mesurait moins de trois points de demi-largeur). La vraie survie se situe entre les deux ; elle est plus proche de la première si les pertes de vue sont réellement indépendantes du risque de départ, ce qui est le cas dans notre simulation. Et la **conclusion sur l'offre** survit à l'épreuve : le test du log-rank reste très significatif même dans le pire cas (dernière ligne : $\chi^2=27{,}4$ contre 35,5), ce qui est cohérent avec le fait que, dans notre simulation, les pertes de vue ne dépendent pas de l'offre. Ce genre de vérification est précieux : il sépare les résultats **robustes** (la conclusion ne bouge pas) des chiffres **fragiles** (le niveau de survie, lui, dépend de l'hypothèse).

> ✅ **À retenir**
> - **Kaplan-Meier** : $\hat S(t)=\prod_{t_j\le t}(1-d_j/n_j)$, où $n_j$ est l'ensemble à risque (les censurés y restent jusqu'à leur censure, puis en sortent). C'est l'estimateur du maximum de vraisemblance **non paramétrique**.
> - **Greenwood** : $\mathrm{Var}\,\hat S\approx\hat S^2\sum d_j/[n_j(n_j-d_j)]$ ; on préfère les intervalles **log-log**, qui restent dans $[0,1]$.
> - La **médiane** se lit sur la courbe ; la **durée moyenne** n'est pas définie si la courbe ne descend pas à 0, d'où la **RMST** (aire jusqu'à un horizon $\tau$).
> - Le **log-rank** compare les groupes en cumulant, instant par instant, départs observés et attendus sous $H_0$ ; il est le plus puissant sous risques proportionnels.
> - Une **entrée tardive** impose de n'inclure un client dans l'ensemble à risque qu'**après** son entrée ; l'oublier surestime la survie.
> - La queue de la courbe est fragile (peu de clients à risque), et la censure non informative est une hypothèse qu'on peut éprouver par une analyse de sensibilité.
