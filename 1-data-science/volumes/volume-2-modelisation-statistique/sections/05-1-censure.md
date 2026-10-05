## 5.1 Censure et fonctions de survie

> 💡 **Intuition.** Une durée est un nombre comme un autre, sauf sur un point : **on n'a pas toujours le temps d'attendre la fin**. Quand l'étude s'arrête, certains clients sont encore là. Pour eux, on ne connaît pas la durée complète, mais on sait quelque chose de précieux : *elle dépasse celle observée*. Toute l'analyse de survie consiste à **utiliser cette information partielle sans la déformer**.

### 5.1.1 Un problème que la moyenne ne sait pas résoudre

Commençons petit, avec huit clients que la gérante a suivis dans son cahier. Pour chacun, elle a noté le nombre de mois pendant lesquels elle l'a observé, et si elle l'a vu **partir** (il n'a plus jamais commandé) ou s'il était **encore là** quand elle a fermé son cahier.

| Client | Mois observés | Situation |
|---|---|---|
| A | 3 | parti |
| B | 5 | parti |
| C | 6 | encore là (**censuré**) |
| D | 8 | parti |
| E | 10 | encore là (**censuré**) |
| F | 12 | parti |
| G | 14 | encore là (**censuré**) |
| H | 14 | encore là (**censuré**) |

Quelle est la durée de fidélité d'un client « typique » ? Trois réponses viennent naturellement, et **les trois sont fausses**.

```python hide
import numpy as np
import pandas as pd

clients8 = pd.DataFrame({
    "client": list("ABCDEFGH"),
    "mois":   [3, 5, 6, 8, 10, 12, 14, 14],
    "parti":  [1, 1, 0, 1, 0, 1, 0, 0],      # 1 = départ observé, 0 = censuré
})
print("(1) moyenne de toutes les durées observées :", clients8["mois"].mean())
print("(2) moyenne des seuls clients partis        :", clients8.loc[clients8["parti"] == 1, "mois"].mean())
print("(3) clients partis / clients observés       :", clients8["parti"].mean())
```
<!--sortie-->
```text
(1) moyenne de toutes les durées observées : 9.0
(2) moyenne des seuls clients partis        : 7.0
(3) clients partis / clients observés       : 0.5
```

- **(1) Tout moyenner.** C'est traiter C, E, G et H comme s'ils étaient partis à l'instant où l'on a cessé de les regarder. Or ils sont toujours là : leur vraie durée est **plus longue** que celle notée. La moyenne de 9 mois est donc **trop faible**.
- **(2) Ne garder que les clients partis.** On jette les censurés, comme s'ils n'avaient pas existé. Mais on jette précisément ceux qui **restent le plus longtemps**. On ne garde que les départs précoces : la moyenne de 7 mois est **encore plus faible**.
- **(3) Compter la proportion de départs.** La moitié des clients sont partis, mais cette proportion dépend uniquement de **la durée pendant laquelle on a regardé**. Avec un cahier fermé plus tard, la proportion serait plus grande ; elle ne mesure aucune propriété du client.

Le dessin rend la situation limpide. Chaque ligne est un client ; le trait s'arrête quand on cesse de l'observer ; le point plein marque un départ, le cercle vide un client **encore présent**, dont l'histoire continue hors du cadre.

```python hide
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
fig, ax = plt.subplots(figsize=(7.2, 3.4))
for i, (nom, m, p) in enumerate(zip(clients8["client"], clients8["mois"], clients8["parti"])):
    y = len(clients8) - i
    ax.plot([0, m], [y, y], color="#898781", lw=1.6, zorder=1)
    if p == 1:
        ax.scatter(m, y, s=70, color=ORANGE, zorder=3)
    else:
        ax.scatter(m, y, s=70, facecolor="white", edgecolor=BLEU, linewidth=2, zorder=3)
        ax.annotate("", xy=(m + 1.6, y), xytext=(m + 0.3, y), arrowprops=dict(arrowstyle="->", color=BLEU, lw=1.4))
ax.set_yticks(range(1, 9))
ax.set_yticklabels(list("HGFEDCBA"))
ax.set_xlabel("mois depuis l'inscription")
ax.set_xlim(0, 17)
ax.text(1.0, 8.9, "● départ observé", color=ORANGE, fontsize=9, va="bottom")
ax.text(6.0, 8.9, "○ encore client à la fermeture du cahier : durée censurée", color=BLEU, fontsize=9, va="bottom")
ax.set_ylim(0.3, 9.6)
ax.grid(axis="y", visible=False)
plt.tight_layout()
plt.savefig("figures/ch05-clients-censures.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Huit clients suivis : un trait par client, un point plein pour un départ observé, un cercle vide et une flèche pour un client encore présent (durée censurée).](figures/ch05-clients-censures.png)

> ⚠️ **Une durée censurée n'est pas une donnée manquante.** On ne la supprime pas, et on ne la remplace pas par la durée observée. Elle dit : « *cette personne a survécu au moins jusque-là* ». C'est exactement l'information que les méthodes de ce chapitre exploitent.

**Mesurer l'erreur.** Avec huit clients, on ne peut pas savoir ce qui est « juste ». Faisons donc une **expérience contrôlée**, possible parce que nous simulons : nous créons 5 000 clients dont nous **connaissons les vraies durées** (une loi de Weibull, que nous définirons au 5.1.3), puis nous les « observons » en coupant l'étude à une date quelconque entre 6 et 60 mois après leur inscription (l'expérience est détaillée dans le cahier, application 5.1).

```python hide
from math import gamma, log

rng = np.random.default_rng(51)
n, k, echelle = 5000, 1.35, 36.0
T_vraie = echelle * rng.weibull(k, n)               # durées complètes (inconnues en pratique)
C = rng.uniform(6, 60, n)                            # durée d'observation possible de chaque client
y = np.minimum(T_vraie, C)                           # ce que l'on voit
parti = (T_vraie <= C).astype(int)

moy_vraie = echelle * gamma(1 + 1 / k)
print(f"part de clients censurés                   : {100 * (1 - parti.mean()):.1f} %")
print(f"VRAIE durée moyenne (formule exacte)       : {moy_vraie:.1f} mois")
print(f"(1) moyenne de toutes les durées observées : {y.mean():.1f} mois")
print(f"(2) moyenne des seuls partis               : {y[parti == 1].mean():.1f} mois")
```
<!--sortie-->
```text
part de clients censurés                   : 44.8 %
VRAIE durée moyenne (formule exacte)       : 33.0 mois
(1) moyenne de toutes les durées observées : 21.5 mois
(2) moyenne des seuls partis               : 18.5 mois
```

La vérité est de **33 mois** ; les deux moyennes naïves donnent environ 21,5 et 18,5, soit **un tiers à presque la moitié de moins**. Aucune ne converge vers la bonne valeur quand on ajoute des données : ce sont des **estimateurs biaisés**, au sens du volume I (section 3.2). Les méthodes du chapitre corrigent ce biais.

### 5.1.2 Le vocabulaire

Posons les notations, qui serviront jusqu'à la fin du chapitre. Pour chaque client $i$ :

- $T_i$ est la **durée vraie** (le temps entre l'**origine** et l'**événement**), généralement inconnue ;
- $C_i$ est la **durée de censure** : le temps entre l'origine et l'instant où l'on cesse d'observer ;
- ce que l'on **voit** est le couple $(Y_i, \delta_i)$ avec
$$Y_i=\min(T_i, C_i),\qquad \delta_i=\begin{cases}1&\text{si } T_i\le C_i\ \text{(événement observé)}\\0&\text{si } T_i> C_i\ \text{(censuré)}\end{cases}$$

Dans notre fichier, `duree_mois` est $Y$ et `churn` est $\delta$. Trois choix, souvent oubliés, définissent proprement une étude de survie :

1. **L'événement** : ici, « le client cesse d'acheter ». À définir précisément (dans le fichier simulé, la colonne est donnée ; dans la réalité, on décide, par exemple, « aucun achat depuis 6 mois »).
2. **L'origine du temps** : ici, la date d'inscription. Chaque client a *sa propre* horloge, qui démarre à *son* inscription ; c'est ce qui permet de comparer des clients arrivés à des dates différentes.
3. **L'unité** : le mois.

### 5.1.3 Trois fonctions pour décrire une durée

Soit $T$ une durée (positive) de fonction de répartition $F(t)=P(T\le t)$ et de densité $f(t)$. On définit trois objets, équivalents mais qui éclairent chacun un aspect différent.

**La fonction de survie.**
$$S(t)=P(T>t)=1-F(t)$$
C'est la proportion de clients encore là à l'instant $t$. Elle vaut 1 en $t=0$, décroît, et tend vers 0 (si tout le monde finit par partir).

**Le risque instantané** (en anglais *hazard*) :
$$h(t)=\lim_{\Delta t\to 0}\frac{P(t\le T<t+\Delta t\mid T\ge t)}{\Delta t}=\frac{f(t)}{S(t)}$$
C'est le **taux de départ, à l'instant $t$, parmi ceux qui sont encore là**. Ce n'est pas une probabilité (il peut dépasser 1, il se mesure « par mois ») : c'est une vitesse. Si $h(10)=0{,}03$ par mois, un client encore présent au dixième mois a environ 3 % de chances de partir dans le mois qui suit.

**Le risque cumulé** :
$$H(t)=\int_0^t h(u)\,du$$
C'est le « total de risque » accumulé depuis l'origine.

> 📐 **Les trois fonctions sont reliées : $S(t)=e^{-H(t)}$.** Partons de $f=-S'$, car $S=1-F$ et $F'=f$. Alors
> $$h(t)=\frac{f(t)}{S(t)}=-\frac{S'(t)}{S(t)}=-\frac{d}{dt}\ln S(t).$$
> Intégrons de 0 à $t$ en utilisant $S(0)=1$, donc $\ln S(0)=0$ :
> $$H(t)=\int_0^t h(u)\,du=-\ln S(t)+\ln S(0)=-\ln S(t),\qquad\text{d'où}\qquad S(t)=e^{-H(t)}.$$
> Connaître l'une des trois fonctions suffit donc à retrouver les deux autres : $f(t)=h(t)\,e^{-H(t)}$.

**Exemple à la main : le risque constant.** Supposons que, chaque mois, un client encore présent ait la même chance de partir : $h(t)=\lambda=0{,}03$ par mois. Alors $H(t)=0{,}03\,t$ et $S(t)=e^{-0{,}03t}$ : la loi **exponentielle** du volume I. Au bout de 12 mois, $S(12)=e^{-0{,}36}\approx0{,}698$ : 70 % des clients sont encore là. La médiane vérifie $S(t)=0{,}5$, soit $t=\ln 2/0{,}03\approx23{,}1$ mois. La moyenne vaut $1/\lambda\approx33{,}3$ mois.

```python hide
lam = 0.03
print("S(12)     =", round(np.exp(-lam * 12), 4))
print("médiane   =", round(np.log(2) / lam, 2), "mois")
print("moyenne   =", round(1 / lam, 2), "mois")
```
<!--sortie-->
```text
S(12)     = 0.6977
médiane   = 23.1 mois
moyenne   = 33.33 mois
```

Un risque constant a une propriété remarquable (et très restrictive) : la loi exponentielle est **sans mémoire**. Un client qui est là depuis 30 mois a *exactement* la même chance de partir le mois prochain qu'un client arrivé hier. Est-ce réaliste ? En pratique, rarement : les premiers mois d'une relation commerciale sont souvent les plus risqués (on essaie, on est déçu, on part), ou au contraire le risque augmente avec le temps (lassitude, usure). Il faut une famille plus souple.

**La loi de Weibull** généralise l'exponentielle avec un paramètre de **forme** $k>0$ et un paramètre d'**échelle** $\sigma>0$ :
$$h(t)=\frac{k}{\sigma}\Big(\frac t\sigma\Big)^{k-1},\qquad H(t)=\Big(\frac t\sigma\Big)^{k},\qquad S(t)=\exp\!\Big[-\Big(\frac t\sigma\Big)^{k}\Big].$$
Le risque est **décroissant** si $k<1$, **constant** si $k=1$ (c'est l'exponentielle, avec $\lambda=1/\sigma$), **croissant** si $k>1$. La médiane est $\sigma(\ln 2)^{1/k}$ et la moyenne $\sigma\,\Gamma(1+1/k)$.

```python hide
import matplotlib.pyplot as plt

t = np.linspace(0.01, 60, 400)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.8))
formes = [(0.7, AQUA, "k = 0,7 : risque décroissant"), (1.0, BLEU, "k = 1 : risque constant"),
          (1.35, ORANGE, "k = 1,35 : risque croissant"), (2.0, VIOLET, "k = 2 : croissant plus vite")]
for kk, couleur, nom in formes:
    h = (kk / 36) * (t / 36) ** (kk - 1)
    S = np.exp(-(t / 36) ** kk)
    ax1.plot(t, h, color=couleur, label=nom)
    ax2.plot(t, S, color=couleur)
ax1.set_ylim(0, 0.12)
ax1.set_xlabel("mois depuis l'inscription")
ax1.set_ylabel("risque instantané h(t), par mois")
ax1.set_title("Le risque : quatre formes")
ax1.legend(fontsize=8, loc="upper center")
ax2.set_xlabel("mois depuis l'inscription")
ax2.set_ylabel("survie S(t)")
ax2.set_title("La survie correspondante (σ = 36 mois)")
ax2.axhline(0.5, color="#c3c2b7", lw=0.8, ls="--")
plt.tight_layout()
plt.savefig("figures/ch05-formes-risque.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Quatre lois de Weibull de même échelle (36 mois) : à gauche le risque instantané, à droite la courbe de survie correspondante. Le pointillé marque la médiane (S = 0,5).](figures/ch05-formes-risque.png)

Remarquez que les quatre courbes de survie se croisent au même point, à $t=\sigma=36$ mois, où elles valent toutes $e^{-1}\approx0{,}37$ : c'est la conséquence de $S(\sigma)=\exp[-(\sigma/\sigma)^k]=e^{-1}$, quel que soit $k$. On lit ensuite l'effet de la forme : à échelle égale, un risque qui **monte** (k > 1) laisse presque tous les clients survivre au début puis les fait partir massivement plus tard, tandis qu'un risque qui **baisse** (k < 1) en élimine beaucoup tôt et laisse un noyau de fidèles.

> 📐 **La durée moyenne est l'aire sous la courbe de survie : $E[T]=\int_0^\infty S(t)\,dt$.** Pour le voir, écrivons $T=\int_0^\infty \mathbf 1_{\{T>t\}}\,dt$ (l'intégrale de la fonction qui vaut 1 tant que $t<T$ vaut $T$). L'espérance de l'intégrale est l'intégrale de l'espérance (théorème de Fubini, valable ici car tout est positif) :
> $$E[T]=\int_0^\infty E\big[\mathbf 1_{\{T>t\}}\big]\,dt=\int_0^\infty P(T>t)\,dt=\int_0^\infty S(t)\,dt.$$
> Cette formule sera notre boussole : estimer la durée moyenne, c'est estimer **l'aire sous la courbe de survie**.

Vérification numérique pour la Weibull ($k=1{,}35$, $\sigma=36$) : l'aire sous $S$ vaut 33,01 mois, exactement la valeur de la formule $\sigma\,\Gamma(1+1/k)$ ; la médiane est de $\sigma(\ln2)^{1/k}\approx27{,}4$ mois.

```python hide
from scipy.integrate import quad

aire, _ = quad(lambda s: np.exp(-(s / 36) ** 1.35), 0, np.inf)
print("aire sous S(t)         :", round(aire, 3))
print("formule σ Γ(1 + 1/k)   :", round(36 * gamma(1 + 1 / 1.35), 3))
print("médiane σ (ln 2)^(1/k) :", round(36 * log(2) ** (1 / 1.35), 2), "mois")
```
<!--sortie-->
```text
aire sous S(t)         : 33.012
formule σ Γ(1 + 1/k)   : 33.012
médiane σ (ln 2)^(1/k) : 27.44 mois
```

### 5.1.4 Les différentes sortes de censure

Nous avons parlé de censure « à droite » sans la définir précisément. Il en existe plusieurs sortes, qu'il faut savoir reconnaître car elles ne se traitent pas de la même façon.

| Type | Ce que l'on sait | Exemple pour la boutique |
|---|---|---|
| **À droite** | $T > c$ : l'événement n'a pas eu lieu à la fin de l'observation | un client inscrit en mars 2025, toujours actif en décembre |
| **À gauche** | $T < c$ : l'événement a *déjà* eu lieu avant la première observation | on découvre en 2025 qu'un client de la base n'a rien acheté depuis une date inconnue, avant l'étude |
| **Par intervalle** | $a < T \le b$ | une enquête annuelle : « le client est encore là en 2023, parti en 2024 » |

Ne confondez pas la censure avec la **troncature** (ou **entrée tardive**) : un client qui a rejoint le programme de fidélité en 2022 alors qu'il était client depuis 2018 n'est observé qu'à partir de 2022. Ceux qui sont partis *avant* 2022 n'apparaissent jamais dans la base. La censure, elle, conserve l'individu dans l'échantillon ; la troncature le fait **disparaître** s'il n'a pas « survécu jusqu'à l'entrée ». Il faut alors corriger les ensembles à risque (nous le ferons à la section 5.2 avec des entrées tardives). Dans notre fichier, tous les clients sont observés **dès leur inscription** : il n'y a pas de troncature, et la seule censure est à droite.

On distingue encore, pour la censure à droite :

- la censure **administrative** (type I) : l'étude s'arrête à une date fixée à l'avance, ici le 31 décembre 2025 ;
- la censure **aléatoire** : des individus sortent de l'étude pour une raison propre (déménagement, perte de contact, décès par une autre cause) ;
- la censure de **type II** : on arrête quand un nombre fixé d'événements est atteint (fréquent en essais industriels).

> 📐 **L'hypothèse de censure non informative.** Toute la théorie qui suit suppose que **la censure est indépendante de la durée** : savoir qu'un client est censuré à $c$ ne doit rien dire sur son risque de partir juste après $c$. Autrement dit, les clients encore sous observation au temps $c$ sont **représentatifs** de tous ceux qui seraient encore là à $c$. Pour la censure administrative, c'est plausible (la date du 31 décembre ne dépend pas des clients). Pour une perte de vue, c'est souvent **faux** : un client qui cesse de répondre est peut-être précisément en train de partir. Cette hypothèse n'est **pas testable** avec les seules données ; il faut la défendre par la connaissance du terrain.

Regardons ce que contient notre fichier : quelle part des durées censurées est purement administrative ?

```python hide
c = pd.read_csv("donnees/clients.csv")
c["date_inscription"] = pd.to_datetime(c["date_inscription"])
c["suivi_possible"] = (pd.Timestamp("2025-12-31") - c["date_inscription"]).dt.days / 30.4375

censures = c[c["churn"] == 0]
admin = (censures["duree_mois"] - censures["suivi_possible"]).abs() < 0.01
print("clients :", len(c), "| départs observés :", int(c["churn"].sum()), "| censurés :", len(censures))
print("censurés administratifs (observés jusqu'au 31/12/2025) :", int(admin.sum()))
print("censurés avant la fin (pertes de vue)                  :", int((~admin).sum()))
print("durée de suivi possible : de", round(c["suivi_possible"].min(), 1), "à", round(c["suivi_possible"].max(), 1), "mois")
```
<!--sortie-->
```text
clients : 2000 | départs observés : 977 | censurés : 1023
censurés administratifs (observés jusqu'au 31/12/2025) : 660
censurés avant la fin (pertes de vue)                  : 363
durée de suivi possible : de 6.0 à 84.0 mois
```

Environ **deux tiers** des durées censurées (660 sur 1 023) sont purement administratives : ces clients sont encore là le 31 décembre 2025. Le tiers restant (363) est constitué de **pertes de vue** : des clients qui sortent de l'observation avant la fin sans que l'on ait vu de départ (changement d'adresse, compte clos par erreur, perte de contact...). Ce n'est donc pas un détail. La durée de suivi possible va de 6 mois (inscrits en juin 2025) à 84 mois (inscrits en janvier 2019).

Que faire de ces pertes de vue ? Nous les traiterons, comme le fait toute analyse standard, comme une censure **non informative**. Ici, c'est justifié par une raison que nous connaissons parce que nous simulons : elles sont indépendantes de la durée par construction. Dans une vraie étude, ce serait **une hypothèse à discuter** : si les clients « perdus de vue » étaient en réalité des clients qui partent sans prévenir, les traiter comme censurés *surestimerait* la survie. Une analyse de sensibilité classique consiste à les recompter comme des départs (le pire cas) pour encadrer la vérité.

### 5.1.5 La vraisemblance avec censure

Comment estimer des paramètres quand une partie des durées est censurée ? Par le **maximum de vraisemblance** (volume I, section 3.2), à condition d'écrire correctement la contribution de chaque client.

- Un client dont le départ est **observé** à $y_i$ apporte la densité $f(y_i)$ : « la durée est exactement $y_i$ ».
- Un client **censuré** à $y_i$ apporte $S(y_i)=P(T>y_i)$ : « la durée dépasse $y_i$ ».

La vraisemblance du paramètre $\theta$ de la loi de $T$ est donc, pour des durées indépendantes :
$$L(\theta)=\prod_{i=1}^{n} f(y_i;\theta)^{\delta_i}\;S(y_i;\theta)^{1-\delta_i}=\prod_{i=1}^n h(y_i;\theta)^{\delta_i}\,S(y_i;\theta),$$
puisque $f=h\,S$. En passant au logarithme et en utilisant $\ln S=-H$ :
$$\boxed{\ \ell(\theta)=\sum_{i=1}^n\Big[\delta_i\ln h(y_i;\theta)-H(y_i;\theta)\Big]\ }$$
La loi de la censure $C$ n'apparaît pas : sous l'hypothèse d'indépendance, elle ne dépend pas de $\theta$ et se factorise hors de la vraisemblance. C'est cette forme que nous utiliserons aux sections 5.3 (vraisemblance partielle de Cox) et 5.4 (modèles paramétriques).

**Premier calcul : le taux de départ constant.** Pour la loi exponentielle, $h=\lambda$ et $H(y)=\lambda y$ :
$$\ell(\lambda)=D\ln\lambda-\lambda\sum_i y_i,\qquad D=\sum_i\delta_i\ \text{(nombre de départs)}.$$
En dérivant, $\ell'(\lambda)=D/\lambda-\sum y_i=0$, donc
$$\hat\lambda=\frac{D}{\sum_i y_i}=\frac{\text{nombre de départs observés}}{\text{total des mois d'exposition}}.$$
Le dénominateur est l'**exposition**, en « mois-clients » : chaque client, parti ou censuré, contribue par **tout** le temps qu'il a passé sous observation. La dérivée seconde $-D/\lambda^2$ donne l'écart-type $\hat\lambda/\sqrt D$.

Sur nos huit clients : $D=4$ départs et $\sum y_i=3+5+6+8+10+12+14+14=72$ mois-clients, donc $\hat\lambda=4/72\approx0{,}056$ par mois. La durée moyenne estimée est $1/\hat\lambda=18$ mois et la médiane $18\ln2\approx12{,}5$ mois. Un optimiseur numérique retrouve le même $\hat\lambda$ pour les huit clients ; appliquons maintenant la formule aux 2 000 clients.

```python hide
from scipy.optimize import minimize_scalar

def log_vraisemblance_exp(lam, y, d):
    return d.sum() * np.log(lam) - lam * y.sum()

y8, d8 = clients8["mois"].to_numpy(float), clients8["parti"].to_numpy()
opt = minimize_scalar(lambda l: -log_vraisemblance_exp(l, y8, d8), bounds=(1e-4, 1), method="bounded")
print(f"8 clients : λ̂ optimiseur = {opt.x:.4f} | formule D/Σy = {d8.sum() / y8.sum():.4f}")

y, d = c["duree_mois"].to_numpy(), c["churn"].to_numpy()
lam_hat = d.sum() / y.sum()
se = lam_hat / np.sqrt(d.sum())
print(f"2000 clients : D = {d.sum()}, exposition = {y.sum():,.0f} mois-clients")
print(f"λ̂ = {lam_hat:.5f} par mois  (IC95 : {lam_hat - 1.96 * se:.5f} à {lam_hat + 1.96 * se:.5f})")
print(f"durée moyenne estimée 1/λ̂ = {1 / lam_hat:.1f} mois | médiane ln2/λ̂ = {np.log(2) / lam_hat:.1f} mois")
print("pour comparer : moyenne naïve de toutes les durées =", round(y.mean(), 1), "mois")
```
<!--sortie-->
```text
8 clients : λ̂ optimiseur = 0.0556 | formule D/Σy = 0.0556
2000 clients : D = 977, exposition = 46,761 mois-clients
λ̂ = 0.02089 par mois  (IC95 : 0.01958 à 0.02220)
durée moyenne estimée 1/λ̂ = 47.9 mois | médiane ln2/λ̂ = 33.2 mois
pour comparer : moyenne naïve de toutes les durées = 23.4 mois
```

Sur les 2 000 clients : $D=977$ départs pour $46\,761$ mois-clients d'exposition, donc $\hat\lambda=0{,}0209$ par mois (IC95 : de 0,0196 à 0,0222), une durée moyenne estimée de $1/\hat\lambda=47{,}9$ mois et une médiane de $\ln2/\hat\lambda=33{,}2$ mois. Pour comparer, la moyenne naïve de toutes les durées vaut 23,4 mois.

L'estimation exponentielle donne environ 48 mois de durée moyenne, plus du double de la moyenne naïve (23 mois). Est-elle pour autant fiable ? Elle repose sur une hypothèse très forte : un risque **constant**. Si le vrai risque est croissant ou décroissant, l'estimation est biaisée. Il nous faut donc une méthode qui **ne suppose pas la forme du risque** : c'est l'objet de la section suivante.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.1, exercices 5.1 à 5.3.

> ✅ **À retenir**
> - Une durée est **censurée à droite** quand l'événement n'a pas eu lieu à la fin de l'observation : on sait seulement $T>y$. Ce n'est pas une donnée manquante.
> - Ni la moyenne de toutes les durées, ni celle des seuls événements, ni la proportion d'événements ne convergent vers la vraie durée moyenne : ces trois résumés sont **biaisés** par la censure.
> - Trois fonctions décrivent une durée : $S(t)=P(T>t)$, le risque instantané $h(t)=f/S$ et le risque cumulé $H(t)$, reliés par $S(t)=e^{-H(t)}$ ; et $E[T]=\int_0^\infty S(t)\,dt$.
> - La loi de Weibull offre un risque décroissant, constant ou croissant selon sa forme $k$ ; l'exponentielle est le cas $k=1$ (sans mémoire).
> - La vraisemblance avec censure est $\ell=\sum[\delta_i\ln h(y_i)-H(y_i)]$ ; pour un risque constant, $\hat\lambda=D/\sum y_i$ (événements par mois d'exposition).
> - Toute la théorie suppose une censure **non informative** (indépendante de la durée) : une hypothèse qui se défend, mais ne se teste pas.
