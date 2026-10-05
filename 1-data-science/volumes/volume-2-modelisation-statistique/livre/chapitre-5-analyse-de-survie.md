# Chapitre 5 : Analyse de survie

> « La question n'est pas seulement *si* l'événement arrivera, mais *quand*, et ce que l'on peut dire des personnes qu'on n'a pas encore vues partir. »

Yasmine a une inquiétude que tous les commerçants connaissent : **combien de temps un client reste-t-il fidèle ?** Elle sait que 49 % de ses 2 000 clients ont cessé d'acheter à la fin de 2025. Mais les autres ? Certains sont arrivés en 2019 et sont toujours là ; d'autres se sont inscrits il y a trois mois et n'ont tout simplement pas eu le temps de partir. Peut-on dire qu'ils « ne partiront jamais » ? Bien sûr que non : on ne sait pas encore. C'est un problème très particulier : **une partie de l'information est incomplète, et pourtant elle n'est pas sans valeur**, puisque savoir qu'un client est resté au moins 40 mois est un renseignement précieux.

L'**analyse de survie** (on dit aussi *analyse des durées*) est la branche de la statistique qui traite ce problème. Son nom vient de la médecine (durée de survie d'un patient), mais ses applications dépassent largement l'hôpital : durée de vie d'un client, d'un abonnement, d'une machine, délai avant un remboursement anticipé de crédit, durée d'un chômage, temps avant le premier sinistre d'une assurance…

> 🧭 **Ce que ce chapitre suppose.** Les chapitres 1 à 3 du volume I (surtout : lois de probabilité et loi exponentielle, estimation par maximum de vraisemblance, intervalles de confiance, tests, bootstrap) et le chapitre 2 de ce volume (modèles linéaires généralisés) pour l'idée de « modèle de régression avec une fonction de lien ». Aucune connaissance préalable en analyse de survie n'est nécessaire.

## Le chemin de ce chapitre

- **5.1 Censure et fonctions de survie** : pourquoi la moyenne ne marche pas, ce qu'est la censure, et les trois fonctions (survie, risque instantané, risque cumulé) qui décrivent une durée.
- **5.2 L'estimateur de Kaplan-Meier** : estimer la courbe de survie **sans hypothèse de forme**, avec son intervalle de confiance, et comparer des groupes (test du log-rank).
- **5.3 Le modèle de Cox à risques proportionnels** : une régression pour les durées, le modèle le plus utilisé de la discipline. Comment l'ajuster, l'interpréter, le vérifier.
- **5.4 Modèles de durée paramétriques** : exponentiel, Weibull, log-normal ; extrapoler au-delà des données et calculer la **valeur vie client**.
- ➕ **5.5 Pour aller plus loin : les risques concurrents** : quand plusieurs événements peuvent interrompre la durée et s'excluent mutuellement.
- **5.6 Exercices corrigés** et bilan.

## Les données de ce chapitre

Nous utilisons le fichier `donnees/clients.csv`, déjà présenté en début de volume : 2 000 clients de Dar Jasmin inscrits entre janvier 2019 et juin 2025, observés jusqu'au **31 décembre 2025**. Quatre colonnes comptent ici :

| Colonne | Signification |
|---|---|
| `duree_mois` | durée pendant laquelle le client a été **observé** (en mois) |
| `churn` | **1** si le départ a été observé, **0** si le client était encore là à la fin de l'observation (durée *censurée*) |
| `offre_bienvenue` | 1 si le client a reçu une offre de bienvenue, 0 sinon, **attribuée au hasard** |
| `canal_acquisition`, `age` | canal par lequel le client est arrivé, âge à l'inscription |

> 📦 **Des données simulées.** Comme dans tout le volume, ces données sont **simulées** avec une graine fixe : nous connaissons donc la loi qui les a engendrées. Nous ne la révélerons qu'à la fin du chapitre (section 5.4.7), pour pouvoir vérifier ce que les méthodes retrouvent, et ce qu'elles retrouvent mal. Faites comme si Yasmine ne la connaissait pas.

> 🛠️ **Les outils.** Nous écrivons à la main les estimateurs importants (Kaplan-Meier, log-rank, vraisemblance de Cox, maximum de vraisemblance paramétrique) pour comprendre ce qu'ils calculent, puis nous les comparons aux bibliothèques : `statsmodels` (`SurvfuncRight`, `survdiff`, `PHReg`), `lifelines`, et le paquet R `survival`, qui est la référence de la discipline. Chaque fois qu'une comparaison est faite, elle est **exécutée**.


## 5.1 Censure et fonctions de survie

> 💡 **Intuition.** Une durée est un nombre comme un autre, sauf sur un point : **on n'a pas toujours le temps d'attendre la fin**. Quand l'étude s'arrête, certains clients sont encore là. Pour eux, on ne connaît pas la durée complète, mais on sait quelque chose de précieux : *elle dépasse celle observée*. Toute l'analyse de survie consiste à **utiliser cette information partielle sans la déformer**.

### 5.1.1 Un problème que la moyenne ne sait pas résoudre

Commençons petit, avec huit clients que Yasmine a suivis dans son cahier. Pour chacun, elle a noté le nombre de mois pendant lesquels elle l'a observé, et si elle l'a vu **partir** (il n'a plus jamais commandé) ou s'il était **encore là** quand elle a fermé son cahier.

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

```python
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

```python
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

**Mesurer l'erreur.** Avec huit clients, on ne peut pas savoir ce qui est « juste ». Faisons donc une **expérience contrôlée**, possible parce que nous simulons : nous créons 5 000 clients dont nous **connaissons les vraies durées** (une loi de Weibull, que nous définirons au 5.1.3), puis nous les « observons » en coupant l'étude à une date quelconque entre 6 et 60 mois après leur inscription.

```python
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

```python
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

```python
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

Vérifions-la numériquement pour la Weibull ($k=1{,}35$, $\sigma=36$) :

```python
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

| Type | Ce que l'on sait | Exemple chez Dar Jasmin |
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

```python
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

Sur nos huit clients : $D=4$ départs et $\sum y_i=3+5+6+8+10+12+14+14=72$ mois-clients, donc $\hat\lambda=4/72\approx0{,}056$ par mois. La durée moyenne estimée est $1/\hat\lambda=18$ mois et la médiane $18\ln2\approx12{,}5$ mois. Vérifions avec un optimiseur, puis appliquons aux 2 000 clients :

```python
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

L'estimation exponentielle donne environ 48 mois de durée moyenne, plus du double de la moyenne naïve (23 mois). Est-elle pour autant fiable ? Elle repose sur une hypothèse très forte : un risque **constant**. Si le vrai risque est croissant ou décroissant, l'estimation est biaisée. Il nous faut donc une méthode qui **ne suppose pas la forme du risque** : c'est l'objet de la section suivante.

> ✅ **À retenir**
> - Une durée est **censurée à droite** quand l'événement n'a pas eu lieu à la fin de l'observation : on sait seulement $T>y$. Ce n'est pas une donnée manquante.
> - Ni la moyenne de toutes les durées, ni celle des seuls événements, ni la proportion d'événements ne convergent vers la vraie durée moyenne : ces trois résumés sont **biaisés** par la censure.
> - Trois fonctions décrivent une durée : $S(t)=P(T>t)$, le risque instantané $h(t)=f/S$ et le risque cumulé $H(t)$, reliés par $S(t)=e^{-H(t)}$ ; et $E[T]=\int_0^\infty S(t)\,dt$.
> - La loi de Weibull offre un risque décroissant, constant ou croissant selon sa forme $k$ ; l'exponentielle est le cas $k=1$ (sans mémoire).
> - La vraisemblance avec censure est $\ell=\sum[\delta_i\ln h(y_i)-H(y_i)]$ ; pour un risque constant, $\hat\lambda=D/\sum y_i$ (événements par mois d'exposition).
> - Toute la théorie suppose une censure **non informative** (indépendante de la durée) : une hypothèse qui se défend, mais ne se teste pas.


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


## 5.3 Le modèle de Cox à risques proportionnels

> 💡 **Intuition.** Kaplan-Meier sait comparer deux ou trois groupes, mais pas dire *« à canal et à offre égaux, que change un an de plus d'âge ? »*. Il faut un modèle de **régression**. David Cox (1972) a eu l'idée géniale de modéliser le **risque instantané** plutôt que la durée, en ne supposant que ceci : le risque d'un client est le risque d'un client « de référence », multiplié par un facteur qui dépend de ses caractéristiques, **le même à tout âge de la relation**. La forme du risque de référence reste libre, ce qui rend le modèle très robuste. Et miracle : on peut estimer les facteurs *sans jamais estimer ce risque de référence*.

### 5.3.1 Le modèle

Pour un client de caractéristiques $x=(x_1,\dots,x_p)$, le **modèle de Cox** s'écrit
$$\boxed{\ h(t\mid x)=h_0(t)\,\exp(\beta_1x_1+\dots+\beta_px_p)=h_0(t)\,e^{x^\top\beta}\ }$$
- $h_0(t)$ est le **risque de base** : le risque d'un client dont toutes les caractéristiques valent 0. **On ne lui impose aucune forme** : c'est la partie « non paramétrique » du modèle. Le modèle est donc dit **semi-paramétrique**.
- $e^{x^\top\beta}$ est le **facteur multiplicatif** : il ne dépend pas de $t$.

**Comment lire un coefficient.** Prenons deux clients identiques sauf pour la variable $x_j$, qui vaut $a+1$ pour l'un et $a$ pour l'autre. Le rapport de leurs risques est
$$\frac{h(t\mid x_j=a+1)}{h(t\mid x_j=a)}=\frac{h_0(t)\,e^{\beta_j(a+1)+\dots}}{h_0(t)\,e^{\beta_ja+\dots}}=e^{\beta_j}.$$
Le terme $h_0(t)$ s'est **simplifié** : ce rapport ne dépend pas de $t$. C'est le **rapport de risques** (en anglais *hazard ratio*, HR) :

- $\mathrm{HR}=e^{\beta_j}<1$ : la variable **réduit** le risque de partir à tout instant (protectrice) ;
- $\mathrm{HR}>1$ : elle l'**augmente** ;
- $\mathrm{HR}=1$ ($\beta_j=0$) : aucun effet.

**Exemple chiffré.** Si $\mathrm{HR}=0{,}67$ pour l'offre de bienvenue, cela signifie : *à n'importe quel âge de la relation, parmi deux clients identiques encore là, celui qui a eu l'offre a un risque instantané de partir égal à 67 % de celui qui ne l'a pas eu*, soit un risque réduit d'un tiers.

> ⚠️ **Un rapport de risques n'est pas un rapport de probabilités.** « Le risque est réduit d'un tiers » ne veut pas dire « un tiers de départs en moins sur 3 ans » : le risque instantané et la proportion cumulée de départs sont deux choses différentes. C'est la **courbe de survie** (section 5.3.7) qui traduit le HR en pourcentages de clients conservés.

### 5.3.2 La vraisemblance partielle : estimer $\beta$ sans connaître $h_0$

Comment estimer $\beta$ si $h_0(t)$ est inconnue ? L'idée de Cox est d'utiliser un **argument conditionnel**, que l'on comprend sur un exemple.

Reprenons nos huit clients (section 5.1.1) et supposons que C, E, F et G aient reçu l'offre ($x=1$) et A, B, D, H non ($x=0$). À l'instant $t=3$, **un** départ a lieu, et les huit clients sont à risque. *Sachant qu'un départ a lieu à cet instant*, quelle est la probabilité que ce soit A ? Chaque client $k$ à risque a un risque $h_0(3)e^{\beta x_k}$ : la probabilité que ce soit A est sa part du risque total,
$$\frac{h_0(3)\,e^{\beta x_A}}{\sum_{k\in\text{à risque}}h_0(3)\,e^{\beta x_k}}=\frac{e^{\beta x_A}}{\sum_{k\in\text{à risque}}e^{\beta x_k}}.$$
**Le risque de base $h_0(3)$ s'est simplifié**, en haut comme en bas ! Il en est de même à chaque instant de départ. En multipliant ces probabilités conditionnelles sur tous les départs, on obtient la **vraisemblance partielle** de Cox :
$$\boxed{\ L_p(\beta)=\prod_{i:\ \delta_i=1}\frac{e^{x_i^\top\beta}}{\sum_{k\in R_i}e^{x_k^\top\beta}}\ }\qquad\ell_p(\beta)=\sum_{i:\ \delta_i=1}\Big[x_i^\top\beta-\ln\sum_{k\in R_i}e^{x_k^\top\beta}\Big]$$
où $R_i$ est l'**ensemble à risque** à l'instant du départ du client $i$ (ceux encore sous observation juste avant). Les clients censurés n'ont pas de facteur propre, mais ils figurent dans les ensembles à risque tant qu'ils sont observés.

À la main, pour nos huit clients (en notant $u=e^\beta$) :

| Départ | $t$ | Ensemble à risque | Facteur de $L_p$ |
|---|---|---|---|
| A ($x=0$) | 3 | A à H : 4 avec offre, 4 sans | $\dfrac{1}{4+4u}$ |
| B ($x=0$) | 5 | B, C, D, E, F, G, H : 4 avec, 3 sans | $\dfrac{1}{3+4u}$ |
| D ($x=0$) | 8 | D, E, F, G, H : 3 avec, 2 sans | $\dfrac{1}{2+3u}$ |
| F ($x=1$) | 12 | F, G, H : 2 avec, 1 sans | $\dfrac{u}{1+2u}$ |

D'où $\ell_p(\beta)=-\ln(4+4u)-\ln(3+4u)-\ln(2+3u)+\beta-\ln(1+2u)$. Où est son maximum ? Pour le trouver, on dérive. Le **score** et l'**information** ont une interprétation simple (cas d'une seule variable) :
$$U(\beta)=\ell_p'(\beta)=\sum_{i:\,\delta_i=1}\big[x_i-\bar x_{R_i}(\beta)\big],\qquad I(\beta)=-\ell_p''(\beta)=\sum_{i:\,\delta_i=1}\mathrm{Var}_{R_i}(x;\beta),$$
où $\bar x_{R_i}(\beta)=\sum_{k\in R_i}x_ke^{\beta x_k}/\sum_{k\in R_i}e^{\beta x_k}$ est la **moyenne pondérée** de $x$ dans l'ensemble à risque (les poids sont les risques relatifs $e^{\beta x_k}$), et $\mathrm{Var}_{R_i}$ la variance pondérée correspondante. Le score compare, à chaque départ, la valeur de $x$ du client parti à la valeur « attendue » : si ceux qui partent ont systématiquement un $x$ plus grand que la moyenne de ceux qui restent, $\beta$ doit être positif. C'est ce qu'on appelle les **résidus de Schoenfeld** $x_i-\bar x_{R_i}$, que nous retrouverons au 5.3.5.

```python
import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize_scalar

y8 = np.array([3, 5, 6, 8, 10, 12, 14, 14], float)
d8 = np.array([1, 1, 0, 1, 0, 1, 0, 0])
x8 = np.array([0, 0, 1, 0, 1, 1, 1, 0], float)           # 1 = a reçu l'offre (C, E, F, G)

def log_vrais_partielle_8(beta):
    u = np.exp(beta)
    return -np.log(4 + 4 * u) - np.log(3 + 4 * u) - np.log(2 + 3 * u) + beta - np.log(1 + 2 * u)

def score_info(beta, y, d, x):
    """Score U(beta) et information I(beta) d'une covariable : boucle sur les départs."""
    U = I = 0.0
    for i in np.where(d == 1)[0]:
        R = y >= y[i]                                     # ensemble à risque
        w = np.exp(beta * x[R])
        m = (w * x[R]).sum() / w.sum()                    # moyenne pondérée de x dans R
        v = (w * x[R] ** 2).sum() / w.sum() - m**2        # variance pondérée
        U += x[i] - m
        I += v
    return U, I

U0, I0 = score_info(0.0, y8, d8, x8)
print(f"en beta = 0 : score U = {U0:.4f}, information I = {I0:.4f}")
print(f"statistique de score U²/I = {U0**2 / I0:.3f}   (comparer au chi2 du log-rank des huit clients : 1.87)")

beta = 0.0                                                # algorithme de Newton-Raphson : beta <- beta + U/I
for it in range(6):
    U, I = score_info(beta, y8, d8, x8)
    print(f"itération {it} : beta = {beta:8.5f}   log-vraisemblance partielle = {log_vrais_partielle_8(beta):.5f}")
    beta += U / I
opt = minimize_scalar(lambda b: -log_vrais_partielle_8(b), bounds=(-6, 3), method="bounded")
print(f"optimiseur : beta = {opt.x:.5f}  ->  HR = {np.exp(opt.x):.3f}")
```
<!--sortie-->
```text
en beta = 0 : score U = -1.3381, information I = 0.9571
statistique de score U²/I = 1.871   (comparer au chi2 du log-rank des huit clients : 1.87)
itération 0 : beta =  0.00000   log-vraisemblance partielle = -6.73340
itération 1 : beta = -1.39804   log-vraisemblance partielle = -5.79849
itération 2 : beta = -1.45965   log-vraisemblance partielle = -5.79702
itération 3 : beta = -1.46056   log-vraisemblance partielle = -5.79702
itération 4 : beta = -1.46057   log-vraisemblance partielle = -5.79702
itération 5 : beta = -1.46057   log-vraisemblance partielle = -5.79702
optimiseur : beta = -1.46056  ->  HR = 0.232
```

Trois enseignements.

1. **La méthode de Newton** converge en quatre itérations (le cinquième chiffre décimal ne bouge plus ensuite) vers $\hat\beta\approx-1{,}46$, donc $\widehat{\mathrm{HR}}=e^{-1{,}46}\approx0{,}23$ : l'offre semblerait diviser le risque par quatre. Mais ce n'est qu'un exemple jouet à huit clients ; l'erreur standard est de $1/\sqrt{I}\approx1{,}16$, de sorte qu'un intervalle de confiance irait de $e^{-1{,}46-1{,}96\times1{,}16}\approx0{,}02$ à $e^{-1{,}46+1{,}96\times1{,}16}\approx2{,}3$.
2. La statistique de score en $\beta=0$ vaut exactement $1{,}87$ : c'est **le chi-deux du test du log-rank** de la section 5.2.5.
3. Ce n'est pas un hasard.

> 📐 **Le test du log-rank est le test de score du modèle de Cox.** En $\beta=0$, $e^{\beta x_k}=1$ pour tous : la moyenne pondérée $\bar x_{R_i}(0)$ est la **proportion de clients du groupe 1** dans l'ensemble à risque ($n_{1j}/n_j$), et le score vaut $\sum_j(d_{1j}-d_jn_{1j}/n_j)=O_1-E_1$. L'information est la variance de la loi hypergéométrique. Autrement dit, tester $H_0:\beta=0$ par le score revient à calculer le log-rank. Le test du log-rank est donc exactement ce que « donne » le modèle de Cox lorsqu'on n'a que la variable de groupe.

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
bs = np.linspace(-4.5, 2.0, 300)
ll = np.array([log_vrais_partielle_8(b) for b in bs])
fig, ax = plt.subplots(figsize=(6.4, 3.8))
ax.plot(bs, ll, color=BLEU, lw=2)
ax.axvline(opt.x, color=ORANGE, lw=1.4, ls="--")
ax.axvline(0, color="#898781", lw=1)
ax.scatter([opt.x, 0], [log_vrais_partielle_8(opt.x), log_vrais_partielle_8(0)], color=[ORANGE, "#898781"], zorder=3)
ax.set_ylim(top=log_vrais_partielle_8(opt.x) + 0.45)
ax.text(opt.x - 0.12, log_vrais_partielle_8(opt.x) + 0.12, "maximum : β̂ = %.2f" % opt.x, color=ORANGE, fontsize=10, ha="right")
ax.text(0.3, log_vrais_partielle_8(0) + 0.5, "β = 0 (aucun effet)", color="#52514e", fontsize=10)
ax.set_xlabel("β : effet de l'offre sur le log du risque")
ax.set_ylabel("log-vraisemblance partielle")
plt.tight_layout()
plt.savefig("figures/ch05-cox-vraisemblance.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Log-vraisemblance partielle de Cox pour les huit clients, en fonction du coefficient β de l'offre : le maximum se trouve à β ≈ −1,46 et la courbe est très plate autour, signe d'une grande incertitude.](figures/ch05-cox-vraisemblance.png)

La courbe est **plate** autour de son maximum : beaucoup de valeurs de $\beta$ sont presque aussi vraisemblables. C'est la traduction graphique de l'erreur standard élevée.

### 5.3.3 Ajuster le modèle sur les 2 000 clients

Pour plusieurs variables, les mêmes formules s'écrivent avec des vecteurs : le score est $U(\beta)=\sum_i[x_i-\bar x_{R_i}]$ (un vecteur) et l'information $I(\beta)$ est la matrice (variances et covariances pondérées dans les ensembles à risque). L'estimateur $\hat\beta$ est asymptotiquement normal de matrice de covariance $I(\hat\beta)^{-1}$, comme tout estimateur du maximum de vraisemblance (volume I, section 3.2).

Voici une implémentation complète, **vectorisée** (on trie les clients par durée décroissante pour obtenir toutes les sommes sur les ensembles à risque par des sommes cumulées). Elle traite les départs simultanés (*ex aequo*) par la correction de **Breslow** : voir 5.3.4.

```python
from scipy.optimize import minimize

def cox_ph(y, d, X):
    """Modèle de Cox par maximum de vraisemblance partielle (ex aequo : Breslow).
    y : durées, d : 1 = départ, X : matrice n x p.  Retourne un dictionnaire."""
    y, d, X = np.asarray(y, float), np.asarray(d, int), np.asarray(X, float)
    ordre = np.argsort(-y, kind="stable")
    ys, Xs = y[ordre], X[ordre]                                   # clients triés par durée DÉCROISSANTE
    tj = np.unique(y[d == 1])                                     # instants de départ distincts
    rang = np.searchsorted(-ys, -tj, side="right")                # nb de clients avec y >= t_j : leur ensemble à risque
    dj = np.array([np.sum((y == t) & (d == 1)) for t in tj])      # départs à chaque instant
    sx = np.array([X[(y == t) & (d == 1)].sum(axis=0) for t in tj])

    def sommes(beta):
        w = np.exp(Xs @ beta)
        s0 = np.cumsum(w)[rang - 1]                                                # somme des risques relatifs dans R_j
        s1 = np.cumsum(w[:, None] * Xs, axis=0)[rang - 1]                          # somme de w x
        s2 = np.cumsum(w[:, None, None] * Xs[:, :, None] * Xs[:, None, :], axis=0)[rang - 1]
        return s0, s1, s2

    def moins_ll(beta):
        s0, _, _ = sommes(beta)
        return -((sx @ beta).sum() - (dj * np.log(s0)).sum())

    def moins_score(beta):
        s0, s1, _ = sommes(beta)
        return -(sx.sum(axis=0) - (dj[:, None] * s1 / s0[:, None]).sum(axis=0))

    res = minimize(moins_ll, np.zeros(X.shape[1]), jac=moins_score, method="BFGS")
    beta = res.x
    s0, s1, s2 = sommes(beta)
    info = (dj[:, None, None] * (s2 / s0[:, None, None] - s1[:, :, None] * s1[:, None, :] / s0[:, None, None] ** 2)).sum(axis=0)
    return {"beta": beta, "cov": np.linalg.inv(info), "info": info, "ll": -res.fun,
            "ll0": -moins_ll(np.zeros(X.shape[1])), "tj": tj, "dj": dj, "s0": s0}

c = pd.read_csv("donnees/clients.csv")
y, d = c["duree_mois"].to_numpy(), c["churn"].to_numpy()
X = pd.get_dummies(c[["offre_bienvenue", "age", "canal_acquisition"]], drop_first=True, dtype=float)
print("colonnes :", list(X.columns), "(référence : Boutique)")
fit = cox_ph(y, d, X.to_numpy())

se = np.sqrt(np.diag(fit["cov"]))
z = fit["beta"] / se
tableau = pd.DataFrame({"coef": fit["beta"], "ET": se, "z": z, "p": 2 * stats.norm.sf(np.abs(z)),
                        "HR": np.exp(fit["beta"]), "HR bas": np.exp(fit["beta"] - 1.96 * se), "HR haut": np.exp(fit["beta"] + 1.96 * se)}, index=X.columns)
print(tableau.round(4).to_string())
```
<!--sortie-->
```text
colonnes : ['offre_bienvenue', 'age', 'canal_acquisition_Instagram', 'canal_acquisition_Site'] (référence : Boutique)
                               coef      ET       z       p      HR  HR bas  HR haut
offre_bienvenue             -0.4061  0.0645 -6.2926  0.0000  0.6662  0.5871   0.7561
age                         -0.0136  0.0030 -4.4792  0.0000  0.9865  0.9806   0.9924
canal_acquisition_Instagram  0.6351  0.0842  7.5467  0.0000  1.8872  1.6002   2.2256
canal_acquisition_Site       0.3258  0.0887  3.6735  0.0002  1.3851  1.1641   1.6481
```

Vérifions avec `statsmodels` (`PHReg`, option `ties="breslow"`) et avec **R** (`coxph`), la référence :

```python
from statsmodels.duration.hazard_regression import PHReg

ph = PHReg(y, X, status=d, ties="breslow").fit()
print("statsmodels : coef", np.round(ph.params, 5), "| ET", np.round(ph.bse, 5))
print("à la main   : coef", np.round(fit["beta"], 5), "| ET", np.round(se, 5))
print(f"log-vraisemblance partielle : à la main {fit['ll']:.3f} | statsmodels {ph.llf:.3f}")
```
<!--sortie-->
```text
statsmodels : coef [-0.40612 -0.01363  0.63508  0.3258 ] | ET [0.06454 0.00304 0.08415 0.08869]
à la main   : coef [-0.40612 -0.01363  0.63508  0.3258 ] | ET [0.06454 0.00304 0.08415 0.08869]
log-vraisemblance partielle : à la main -6512.361 | statsmodels -6512.361
```

```r
clients$canal_acquisition <- factor(clients$canal_acquisition, levels = c("Boutique", "Instagram", "Site"))
cox_r <- coxph(Surv(duree_mois, churn) ~ offre_bienvenue + age + canal_acquisition, data = clients, ties = "breslow")
print(summary(cox_r))
```
<!--sortie-->
```text
Call:
coxph(formula = Surv(duree_mois, churn) ~ offre_bienvenue + age + 
    canal_acquisition, data = clients, ties = "breslow")

  n= 2000, number of events= 977 

                                coef exp(coef)  se(coef)      z Pr(>|z|)    
offre_bienvenue            -0.406119  0.666231  0.064540 -6.293 3.12e-10 ***
age                        -0.013635  0.986458  0.003044 -4.479 7.49e-06 ***
canal_acquisitionInstagram  0.635078  1.887170  0.084153  7.547 4.47e-14 ***
canal_acquisitionSite       0.325800  1.385138  0.088688  3.674 0.000239 ***
---
Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1

                           exp(coef) exp(-coef) lower .95 upper .95
offre_bienvenue               0.6662     1.5010    0.5871    0.7561
age                           0.9865     1.0137    0.9806    0.9924
canal_acquisitionInstagram    1.8872     0.5299    1.6002    2.2256
canal_acquisitionSite         1.3851     0.7219    1.1641    1.6481

Concordance= 0.605  (se = 0.01 )
Likelihood ratio test= 112  on 4 df,   p=<2e-16
Wald test            = 110.3  on 4 df,   p=<2e-16
Score (logrank) test = 111.8  on 4 df,   p=<2e-16
```

Les trois calculs coïncident à la cinquième décimale. Lisons le tableau.

- **Offre de bienvenue** : $\widehat{\mathrm{HR}}\approx0{,}67$ (IC95 : de 0,59 à 0,76). À âge et canal égaux, l'offre réduit le risque de départ d'environ **un tiers**, à n'importe quel âge de la relation. Comme l'offre est **attribuée au hasard**, l'interprétation causale est licite ; l'intervalle exclut nettement 1.
- **Âge** : $\widehat{\mathrm{HR}}\approx0{,}986$ **par année** : chaque année d'âge de plus réduit le risque d'environ 1,4 %. Pour parler à Yasmine, on exprime l'effet par tranche : *dix ans de plus* correspondent à $\mathrm{HR}=e^{10\hat\beta}$, soit environ $0{,}87$ (calculé ci-dessous).
- **Canal** : par rapport à la boutique (référence), un client arrivé par **Instagram** a un risque environ **1,9 fois plus élevé** et un client arrivé par le **site**, environ **1,4 fois**. C'est cohérent avec les courbes de la section 5.2.

```python
i_age = list(X.columns).index("age")
b, s_ = fit["beta"][i_age], se[i_age]
print(f"âge, +10 ans : HR = {np.exp(10 * b):.3f}  (IC95 : {np.exp(10 * (b - 1.96 * s_)):.3f} à {np.exp(10 * (b + 1.96 * s_)):.3f})")

# Tests globaux : rapport de vraisemblance, Wald, score (comparer avec R)
lr = 2 * (fit["ll"] - fit["ll0"])
wald = fit["beta"] @ fit["info"] @ fit["beta"]
print(f"test global (4 ddl) : rapport de vraisemblance = {lr:.2f}, p = {stats.chi2.sf(lr, 4):.1e} ; Wald = {wald:.2f}")
```
<!--sortie-->
```text
âge, +10 ans : HR = 0.873  (IC95 : 0.822 à 0.926)
test global (4 ddl) : rapport de vraisemblance = 112.01, p = 2.7e-23 ; Wald = 110.28
```

> 💡 **Les trois tests classiques.** Pour un modèle de maximum de vraisemblance, on peut tester $H_0:\beta=0$ de trois façons : par le **rapport de vraisemblance** (comparer $\ell_p(\hat\beta)$ à $\ell_p(0)$), par le test de **Wald** ($\hat\beta^\top I\hat\beta$, valeur de $z^2$ pour un seul coefficient), ou par le test de **score** (évaluer le score en $\beta=0$ : c'est le log-rank). Ils sont équivalents asymptotiquement et donnent ici des conclusions identiques ; R affiche les trois.

### 5.3.4 Les ex aequo : Breslow, Efron et les autres

Si deux clients partent exactement au même instant, la vraisemblance partielle ne dit pas dans quel ordre : les facteurs de la formule ne sont plus bien définis. Trois approches :

- **Breslow** : on traite tous les ex aequo comme si l'ensemble à risque était *le même* pour chacun (celui d'avant l'instant). Simple, mais approximative quand les ex aequo sont nombreux. C'est ce que nous avons codé.
- **Efron** : on retire progressivement les clients partis simultanément de l'ensemble à risque, en moyenne. Plus précise ; c'est le **défaut de R** (`coxph`) et de `lifelines`.
- **Exacte** : on somme sur tous les ordres possibles. Précise mais coûteuse quand les ex aequo sont nombreux.

Dans nos données, mesurées au centième de mois, il y a peu d'ex aequo (91 instants sur 882 comportent plusieurs départs) ; la différence est **négligeable** :

```python
efron = PHReg(y, X, status=d, ties="efron").fit()
print("Breslow :", np.round(ph.params, 5))
print("Efron   :", np.round(efron.params, 5))
```
<!--sortie-->
```text
Breslow : [-0.40612 -0.01363  0.63508  0.3258 ]
Efron   : [-0.40616 -0.01364  0.63513  0.32584]
```

Mais voyons ce qui se passe quand on **arrondit** les durées au mois supérieur, comme le ferait une base de données qui ne stocke que des mois entiers : les ex aequo deviennent massifs.

```python
y_mois = np.ceil(y)
print("départs :", int(d.sum()), "| instants distincts après arrondi :", len(np.unique(y_mois[d == 1])))
b_b = PHReg(y_mois, X, status=d, ties="breslow").fit().params
b_e = PHReg(y_mois, X, status=d, ties="efron").fit().params
print(pd.DataFrame({"Breslow": b_b, "Efron": b_e, "écart relatif (%)": 100 * (b_b - b_e) / np.abs(b_e)}, index=X.columns).round(4).to_string())
```
<!--sortie-->
```text
départs : 977 | instants distincts après arrondi : 75
                             Breslow   Efron  écart relatif (%)
offre_bienvenue              -0.4030 -0.4075             1.1077
age                          -0.0135 -0.0136             1.1785
canal_acquisition_Instagram   0.6260  0.6327            -1.0456
canal_acquisition_Site        0.3211  0.3240            -0.8909
```

Après arrondi, les 977 départs se répartissent sur seulement 75 instants (une douzaine d'ex aequo par instant en moyenne). Breslow tire alors chaque coefficient **vers zéro** (son coefficient est plus petit en valeur absolue que celui d'Efron, de l'ordre de 1 % ici), alors que sans arrondi, les deux méthodes étaient confondues à la quatrième décimale. L'écart reste modeste parce que les ex aequo sont, ici, une petite fraction de chaque ensemble à risque (quelques dizaines sur plusieurs centaines) ; il deviendrait important si la fraction de clients partant à chaque instant était grande. La règle pratique : **utilisez Efron par défaut**.

### 5.3.5 Vérifier l'hypothèse : les risques sont-ils vraiment proportionnels ?

Tout le modèle repose sur *un seul* pari : l'effet d'une variable est **le même à tout âge de la relation**. L'offre de bienvenue divise-t-elle le risque par 0,67 aussi bien le premier mois que la troisième année ? Si ce n'est pas le cas, le coefficient estimé n'est qu'une **moyenne**, potentiellement trompeuse. Il faut **vérifier**.

**(a) Le graphique log-log.** Si les risques sont proportionnels, $H(t\mid x)=H_0(t)e^{x^\top\beta}$, donc $\ln\big(-\ln S(t\mid x)\big)=\ln H_0(t)+x^\top\beta$ : en traçant $\ln(-\ln\hat S)$ contre $\ln t$ pour plusieurs groupes, on doit obtenir des courbes **parallèles** (décalées de $x^\top\beta$).

**(b) Les résidus de Schoenfeld.** Le résidu du client $i$ parti à $t_i$ est $r_i=x_i-\bar x_{R_i}(\hat\beta)$ (5.3.2). Si l'effet de $x_j$ était constant, ces résidus n'auraient aucune tendance en fonction du temps. S'ils croissent avec $t$, l'effet réel de $x_j$ augmente avec le temps ; s'ils décroissent, il diminue. Grambsch et Therneau transforment cette idée en **test de score** : on ajoute au modèle un terme $\theta_j\,x_j\,g(t)$ où $g$ est une fonction du temps (ici, le **rang** de la durée), et l'on teste $\theta_j=0$ au point $(\hat\beta,\ \theta=0)$. Les trois ingrédients se calculent avec les mêmes sommes que précédemment : le score $U_{\theta_j}=\sum_ig(t_i)\,r_{ij}$, et la matrice d'information du modèle étendu.

```python
def test_ph(y, d, X, fit):
    """Test de score de proportionnalité des risques (Grambsch-Therneau), g(t) = rang de la durée."""
    y, d, X, beta, V = np.asarray(y, float), np.asarray(d, int), np.asarray(X, float), fit["beta"], fit["cov"]
    ev = np.where(d == 1)[0]
    g = stats.rankdata(y)[ev]
    g = g - g.mean()
    w = np.exp(X @ beta)
    ordre = np.argsort(-y, kind="stable")
    ys, Xs, ws = y[ordre], X[ordre], w[ordre]
    pos = np.searchsorted(-ys, -y[ev], side="right") - 1                  # fin de l'ensemble à risque de chaque départ
    s0 = np.cumsum(ws)[pos]
    m1 = np.cumsum(ws[:, None] * Xs, axis=0)[pos] / s0[:, None]
    cov = np.cumsum(ws[:, None, None] * Xs[:, :, None] * Xs[:, None, :], axis=0)[pos] / s0[:, None, None] - m1[:, :, None] * m1[:, None, :]
    R = X[ev] - m1                                                          # résidus de Schoenfeld (non normalisés)
    U = (g[:, None] * R).sum(axis=0)                                        # score des coefficients dépendant du temps
    Ibt = (g[:, None, None] * cov).sum(axis=0)
    Itt = (g[:, None, None] ** 2 * cov).sum(axis=0)
    Schur = Itt - Ibt.T @ V @ Ibt                                           # information « nette » (le beta est re-estimé)
    chi2_j = np.array([U[j] ** 2 / Schur[j, j] for j in range(X.shape[1])])
    chi2_glob = float(U @ np.linalg.solve(Schur, U))
    return chi2_j, chi2_glob

chi2_j, chi2_glob = test_ph(y, d, X, fit)
res_ph = pd.DataFrame({"chi2": chi2_j, "p": stats.chi2.sf(chi2_j, 1)}, index=X.columns)
res_ph.loc["GLOBAL (4 ddl)"] = [chi2_glob, stats.chi2.sf(chi2_glob, 4)]
print(res_ph.round(4).to_string())
```
<!--sortie-->
```text
                               chi2       p
offre_bienvenue              0.5588  0.4548
age                          0.7292  0.3931
canal_acquisition_Instagram  2.2063  0.1375
canal_acquisition_Site       0.0146  0.9037
GLOBAL (4 ddl)               4.9502  0.2924
```

```r
print(cox.zph(cox_r, transform = "rank", terms = FALSE))
```
<!--sortie-->
```text
                            chisq df    p
offre_bienvenue            0.5588  1 0.45
age                        0.7292  1 0.39
canal_acquisitionInstagram 2.2063  1 0.14
canal_acquisitionSite      0.0146  1 0.90
GLOBAL                     4.9502  4 0.29
```

Notre test à la main et `cox.zph` de R donnent les **mêmes** statistiques. Aucune p-valeur n'est petite : la proportionnalité des risques est **plausible**. Ce n'est pas une surprise : les données ont été simulées avec un modèle de Weibull, qui est à risques proportionnels (nous le démontrerons au 5.4).

Que se passe-t-il quand l'hypothèse est **fausse** ? Simulons deux groupes de 750 clients : dans le groupe A, le risque de partir **diminue** avec le temps (Weibull de forme 0,8) ; dans le groupe B, il **augmente** (forme 1,8). Leurs risques se croisent.

```python
rng = np.random.default_rng(54)
n = 1500
g = np.repeat([0, 1], n // 2)
T = np.where(g == 0, 30 * rng.weibull(0.8, n), 40 * rng.weibull(1.8, n))
C = rng.uniform(10, 80, n)
yc, dc = np.minimum(T, C), (T <= C).astype(int)
Xc = g[:, None].astype(float)

fit_c = cox_ph(yc, dc, Xc)
chi2_c, _ = test_ph(yc, dc, Xc, fit_c)
print(f"Cox : HR (B contre A) = {np.exp(fit_c['beta'][0]):.2f}   ->   « B a 27 % de risque en moins »")
print(f"test de proportionnalité : chi2 = {chi2_c[0]:.1f}, p = {stats.chi2.sf(chi2_c[0], 1):.1e}")

# La vérité : on compare le risque dans les 25 premiers mois puis après
def hr_periode(debut, fin):
    garde = yc > debut
    yy = np.minimum(yc[garde], fin)
    dd = dc[garde] * (yc[garde] <= fin)
    ph_ = PHReg(yy, Xc[garde], status=dd, entry=np.full(garde.sum(), float(debut)), ties="efron").fit()
    return float(np.exp(ph_.params[0]))
print(f"HR sur 0-25 mois : {hr_periode(0, 25):.2f}   |   HR après 25 mois : {hr_periode(25, 1000):.2f}")
```
<!--sortie-->
```text
Cox : HR (B contre A) = 0.73   ->   « B a 27 % de risque en moins »
test de proportionnalité : chi2 = 216.3, p = 5.7e-49
HR sur 0-25 mois : 0.43   |   HR après 25 mois : 2.20
```

Le HR global (0,73) est une moyenne qui ne décrit **aucune période réelle** : le groupe B est bien plus protégé au début (HR $\approx0{,}43$ sur les 25 premiers mois), puis devient moins bon que A (HR $\approx2{,}2$ ensuite). Le test de proportionnalité le détecte immédiatement ($\chi^2$ très grand). Visualisons-le, avec les deux graphiques (courbes de survie qui se croisent ; graphique log-log) :

```python
def courbe_loglog(ax, y_, d_, masque, couleur, nom):
    t_, n_, dj_, S_, g_ = kaplan_meier(y_[masque], d_[masque])
    garde = (S_ > 0) & (S_ < 1) & (t_ > 3)        # on écarte les tout premiers mois (très peu de départs)
    ax.plot(np.log(t_[garde]), np.log(-np.log(S_[garde])), color=couleur, lw=2, label=nom)

fig, axes = plt.subplots(1, 3, figsize=(13, 3.9))
# (1) Clients : les trois canaux, courbes log-log presque parallèles
for nom, couleur in [("Boutique", AQUA), ("Site", BLEU), ("Instagram", ORANGE)]:
    courbe_loglog(axes[0], y, d, (c["canal_acquisition"] == nom).to_numpy(), couleur, nom)
axes[0].set_title("Clients : les risques sont proportionnels")
# (2) et (3) Groupes simulés qui se croisent
for k_, couleur, nom in [(0, VIOLET, "groupe A (risque décroissant)"), (1, AQUA, "groupe B (risque croissant)")]:
    t_, n_, dj_, S_, g_ = kaplan_meier(yc[g == k_], dc[g == k_])
    axes[1].step(np.concatenate([[0], t_]), np.concatenate([[1], S_]), where="post", color=couleur, lw=2, label=nom)
    courbe_loglog(axes[2], yc, dc, g == k_, couleur, nom)
axes[1].set_title("Simulé : les courbes se croisent")
axes[2].set_title("Simulé : log-log non parallèles")
axes[0].set_xlabel("log(mois)"); axes[2].set_xlabel("log(mois)"); axes[1].set_xlabel("mois")
axes[0].set_ylabel("log(-log S(t))"); axes[1].set_ylabel("survie S(t)")
for ax in axes:
    ax.legend(frameon=False, fontsize=8, loc="best")
plt.tight_layout()
plt.savefig("figures/ch05-cox-loglog.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![À gauche : graphique log-log des trois canaux de Dar Jasmin (courbes presque parallèles). Au centre et à droite : deux groupes simulés dont les risques se croisent (courbes de survie qui se coupent, courbes log-log non parallèles).](figures/ch05-cox-loglog.png)

**Que faire quand les risques ne sont pas proportionnels ?** Plusieurs remèdes, du plus simple au plus fin :

1. **Stratifier** sur la variable fautive : chaque strate (par exemple chaque canal) a son propre risque de base $h_{0s}(t)$, mais les autres coefficients sont communs. On n'obtient plus de coefficient pour la variable de stratification, mais on se libère de l'hypothèse pour elle.
2. **Estimer un effet qui change avec le temps** : $\beta_j(t)=\beta_j+\theta_jg(t)$, ou un coefficient différent par période (comme ci-dessus).
3. **Changer de résumé** : comparer des durées moyennes restreintes (5.2.4), qui n'exigent pas la proportionnalité.

```python
strat = PHReg(y, X[["offre_bienvenue", "age"]], status=d, strata=c["canal_acquisition"].to_numpy(), ties="efron").fit()
sans_strat = PHReg(y, X[["offre_bienvenue", "age"]], status=d, ties="efron").fit()
print(pd.DataFrame({"stratifié par canal": strat.params, "non stratifié": sans_strat.params}, index=["offre_bienvenue", "age"]).round(4).to_string())
```
<!--sortie-->
```text
                 stratifié par canal  non stratifié
offre_bienvenue              -0.4074        -0.3954
age                          -0.0136        -0.0120
```

Les coefficients de l'offre et de l'âge changent peu (offre : $-0{,}407$ avec stratification, $-0{,}395$ sans) ; la différence vient surtout de ce que le canal, facteur important du risque, est omis dans le second modèle.

> ⚠️ **Un test non significatif ne prouve pas la proportionnalité.** Avec peu de données, le test manque de puissance ; avec beaucoup, il détecte des écarts sans importance pratique. Combinez le test avec le **graphique**, et posez-vous la question du **mécanisme** : est-il plausible qu'une offre de bienvenue ait le même effet relatif au premier mois et à la cinquième année ?

### 5.3.6 Variables qui changent avec le temps, et le piège de l'« immortalité »

Jusqu'ici, chaque variable était fixée à l'inscription. Mais certaines évoluent : un client reçoit une carte de fidélité au mois 12, passe à un abonnement premium au mois 20, etc. Le modèle de Cox accepte des **covariables dépendant du temps** $x(t)$ ; on les représente en découpant la vie du client en **épisodes** $(\text{début},\text{fin}]$ sur chacun desquels la covariable est constante : c'est le format **« processus de comptage »**.

| Client | Épisode | début | fin | carte de fidélité | départ à la fin de l'épisode ? |
|---|---|---|---|---|---|
| Z (a eu la carte au mois 12, parti au mois 30) | 1 | 0 | 12 | 0 | non |
| | 2 | 12 | 30 | 1 | oui |
| W (jamais de carte, parti au mois 8) | 1 | 0 | 8 | 0 | oui |

Dans la vraisemblance partielle, à chaque instant de départ, un client est à risque **avec la valeur de sa covariable à cet instant-là**. La date de début de l'épisode joue le rôle d'une **entrée tardive** (comme en 5.2.6).

> ⚠️ **Le biais d'immortalité.** Voici l'erreur la plus fréquente, et la plus trompeuse. Yasmine veut savoir si la **carte de fidélité** (remise aux clients encore là au mois 12) réduit les départs. Elle crée une colonne « a la carte » = 1 pour tous ceux qui l'ont **un jour** reçue, et ajuste un modèle de Cox. Problème : pour avoir la carte, il fallait **être encore client au mois 12**. Les porteurs de carte ont donc, par construction, **survécu 12 mois** : ils sont « immortels » pendant cette période. La variable prédit le futur depuis le passé.

Simulons une situation où la carte n'a **strictement aucun effet** (le risque de tout le monde est constant, 3 % par mois) :

```python
rng = np.random.default_rng(53)
N = 3000
T = rng.exponential(1 / 0.03, N)                  # durées vraies : risque constant 3 % par mois, indépendantes de la carte
C = rng.uniform(24, 60, N)
Y, D = np.minimum(T, C), (T <= C).astype(int)
carte = (Y > 12) & (rng.random(N) < 0.5)           # carte remise au mois 12 à la moitié des clients encore là
print("porteurs de carte :", int(carte.sum()), "sur", N)

# Analyse FAUSSE : la carte est traitée comme une variable fixe de départ
naif = PHReg(Y, carte.astype(float)[:, None], status=D, ties="efron").fit()
print(f"analyse naïve   : HR = {np.exp(naif.params[0]):.2f}  (IC95 {np.exp(naif.params[0] - 1.96 * naif.bse[0]):.2f} à {np.exp(naif.params[0] + 1.96 * naif.bse[0]):.2f})")

# Analyse JUSTE : variable dépendant du temps, deux épisodes pour les porteurs
porteurs = np.where(carte)[0]
debut = np.concatenate([np.zeros(N), np.full(len(porteurs), 12.0)])
fin = np.concatenate([np.where(carte, 12.0, Y), Y[porteurs]])
statut = np.concatenate([np.where(carte, 0, D), D[porteurs]])
x_carte = np.concatenate([np.zeros(N), np.ones(len(porteurs))])
juste = PHReg(fin, x_carte[:, None], status=statut, entry=debut, ties="efron").fit()
print(f"analyse correcte : HR = {np.exp(juste.params[0]):.2f}  (IC95 {np.exp(juste.params[0] - 1.96 * juste.bse[0]):.2f} à {np.exp(juste.params[0] + 1.96 * juste.bse[0]):.2f})")
```
<!--sortie-->
```text
porteurs de carte : 995 sur 3000
analyse naïve   : HR = 0.46  (IC95 0.41 à 0.50)
analyse correcte : HR = 1.03  (IC95 0.92 à 1.16)
```

L'analyse naïve « découvre » que la carte divise le risque par plus de deux (HR ≈ 0,46) alors qu'elle n'a **aucun effet** ; l'analyse correcte trouve un HR proche de 1, avec un intervalle de confiance qui contient 1. Cette erreur est célèbre (elle a faussé des études médicales entières, par exemple sur les bénéfices d'un traitement reçu « un jour »). **Règle** : toute variable dont la valeur n'est connue qu'*après* un certain temps de survie doit être traitée comme dépendant du temps.

### 5.3.7 Prédire : la courbe de survie d'un client donné

Le risque de base $h_0$ a disparu de la vraisemblance, mais on peut l'estimer *après coup*. Pour un client de profil $x$, $S(t\mid x)=\exp\big(-H_0(t)\,e^{x^\top\beta}\big)$, où le **risque cumulé de base** $H_0(t)$ est estimé par l'**estimateur de Breslow** :
$$\hat H_0(t)=\sum_{j:\,t_j\le t}\frac{d_j}{\sum_{k\in R_j}e^{x_k^\top\hat\beta}}.$$
C'est une version « pondérée » de l'estimateur de Nelson-Aalen $\sum d_j/n_j$ (si $\beta=0$, les deux coïncident). Chaque saut est le nombre de départs divisé par la **somme des risques relatifs** des clients à risque.

```python
H0 = np.cumsum(fit["dj"] / fit["s0"])                       # risque cumulé de base (Breslow)
def survie_pred(t, x):
    i = np.searchsorted(fit["tj"], t, side="right") - 1
    return float(np.exp(-(H0[i] if i >= 0 else 0.0) * np.exp(np.asarray(x, float) @ fit["beta"])))

profils = {"A : Instagram, 25 ans, sans offre": [0, 25, 1, 0],
           "B : Instagram, 25 ans, avec offre": [1, 25, 1, 0],
           "C : Boutique, 45 ans, avec offre": [1, 45, 0, 0]}          # ordre des colonnes : offre, age, Instagram, Site
horizons = (12, 24, 36, 60)
print(pd.DataFrame({k: [survie_pred(t, v) for t in horizons] for k, v in profils.items()}, index=[f"{t} mois" for t in horizons]).round(4).T.to_string())
```
<!--sortie-->
```text
                                   12 mois  24 mois  36 mois  60 mois
A : Instagram, 25 ans, sans offre   0.7108   0.4379   0.2298   0.0686
B : Instagram, 25 ans, avec offre   0.7966   0.5769   0.3754   0.1678
C : Boutique, 45 ans, avec offre    0.9123   0.8010   0.6735   0.4867
```

```r
nd <- data.frame(offre_bienvenue = c(0, 1, 1), age = c(25, 25, 45),
                 canal_acquisition = factor(c("Instagram", "Instagram", "Boutique"), levels = levels(clients$canal_acquisition)))
print(round(t(summary(survfit(cox_r, newdata = nd), times = c(12, 24, 36, 60))$surv), 4))
```
<!--sortie-->
```text
    [,1]   [,2]   [,3]   [,4]
1 0.7108 0.4379 0.2298 0.0686
2 0.7966 0.5769 0.3754 0.1678
3 0.9123 0.8010 0.6735 0.4867
```

Les prédictions à la main et celles de R sont identiques. Elles se traduisent en pourcentages de clients : un client arrivé par Instagram à 25 ans **sans offre** a environ 44 % de chances d'être encore là à 24 mois, contre 58 % **avec** l'offre ; un client de 45 ans arrivé par la boutique avec l'offre : 80 %. Dessinons ces courbes :

```python
temps = np.linspace(0, 70, 300)
fig, ax = plt.subplots(figsize=(7.2, 4.2))
for (nom, x), couleur in zip(profils.items(), [ORANGE, VIOLET, AQUA]):
    ax.plot(temps, [survie_pred(t, x) for t in temps], color=couleur, lw=2, label=nom)
ax.axhline(0.5, color="#c3c2b7", lw=0.8)
ax.set_xlabel("mois depuis l'inscription")
ax.set_ylabel("probabilité d'être encore client")
ax.set_ylim(0, 1.02)
ax.legend(frameon=False, loc="lower left", fontsize=9)
plt.tight_layout()
plt.savefig("figures/ch05-cox-profils.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Courbes de survie prédites par le modèle de Cox pour trois profils de clients de Dar Jasmin.](figures/ch05-cox-profils.png)

### 5.3.8 Le modèle sépare-t-il bien les clients ? L'indice de concordance

Un modèle de survie est-il bon ? Une mesure très utilisée est l'**indice de concordance** de Harrell (C-index) : parmi tous les **couples comparables** de clients (c'est-à-dire ceux dont on sait lequel est parti le premier), quelle proportion le modèle ordonne-t-il correctement, c'est-à-dire en attribuant le **risque le plus élevé** à celui qui est parti le plus tôt ? Un couple $(i,j)$ est comparable si $y_i<y_j$ et que $i$ est un départ observé (le client $j$, lui, peut être censuré : on sait qu'il est resté plus longtemps). C'est l'extension du « AUC » du volume I à des durées censurées : 0,5 = hasard, 1 = tri parfait.

```python
def indice_concordance(y, d, eta):
    """C de Harrell : pourcentage de couples comparables bien ordonnés (les ex aequo de score comptent pour 1/2)."""
    y, d, eta = np.asarray(y), np.asarray(d), np.asarray(eta)
    concordants = egalites = total = 0
    for i in np.where(d == 1)[0]:
        plus_longs = y > y[i]                                  # clients observés plus longtemps que i
        total += plus_longs.sum()
        concordants += (eta[plus_longs] < eta[i]).sum()         # i a un score de risque plus élevé : bien ordonné
        egalites += (eta[plus_longs] == eta[i]).sum()
    return (concordants + 0.5 * egalites) / total

eta = X.to_numpy() @ fit["beta"]
print(f"indice de concordance : {indice_concordance(y, d, eta):.4f}")
```
<!--sortie-->
```text
indice de concordance : 0.6052
```

```r
print(round(summary(coxph(Surv(duree_mois, churn) ~ offre_bienvenue + age + canal_acquisition, data = clients))$concordance, 4))
```
<!--sortie-->
```text
     C  se(C) 
0.6052 0.0101 
```

Le C-index est d'environ **0,605**, identique à celui de R. C'est **modeste**, et c'est normal : nous n'avons que trois variables, et surtout, la durée d'un client individuel comporte une très grande part d'aléa. Le modèle explique bien les **différences entre groupes** (le HR de 0,67 est très significatif) mais prédit mal le sort d'un client *particulier*. C'est une distinction capitale en pratique : *un résultat significatif n'est pas un modèle prédictif performant* (volume I, section 3.5.3).

### 5.3.9 Un second jeu de données : la récidive (Rossi)

Pour nous assurer que le modèle ne marche pas que sur des données que nous avons simulées, essayons un jeu de données **réel** classique, livré avec la bibliothèque `lifelines` (donc utilisable hors ligne). Il provient de l'étude de **Rossi, Berk et Lenihan (1980)** : 432 hommes libérés de prison dans le Maryland, suivis pendant 52 semaines ; l'événement est une **nouvelle arrestation**. La moitié, tirée au hasard, a reçu une **aide financière** (variable `fin`) pendant sa période de libération. Les autres variables : âge, origine (`race`), expérience professionnelle (`wexp`), marié (`mar`), libération conditionnelle (`paro`), nombre de condamnations antérieures (`prio`).

```python
from lifelines.datasets import load_rossi
from lifelines import CoxPHFitter

rossi = load_rossi()
Xr = rossi.drop(columns=["week", "arrest"])
print(f"{len(rossi)} personnes, {int(rossi['arrest'].sum())} arrestations observées, {int((rossi['arrest'] == 0).sum())} censurées à 52 semaines")
sm_r = PHReg(rossi["week"], Xr, status=rossi["arrest"], ties="efron").fit()
ll_r = CoxPHFitter().fit(rossi, "week", "arrest")
comp = pd.DataFrame({"HR statsmodels": np.exp(sm_r.params), "HR lifelines": ll_r.hazard_ratios_.to_numpy(),
                     "ET(log HR)": sm_r.bse, "p": sm_r.pvalues}, index=Xr.columns)
print(comp.round(3).to_string())
print(f"log-vraisemblance : statsmodels {sm_r.llf:.3f} | lifelines {ll_r.log_likelihood_:.3f}")
```
<!--sortie-->
```text
432 personnes, 114 arrestations observées, 318 censurées à 52 semaines
      HR statsmodels  HR lifelines  ET(log HR)      p
fin            0.684         0.684       0.191  0.047
age            0.944         0.944       0.022  0.009
race           1.369         1.369       0.308  0.308
wexp           0.861         0.861       0.212  0.480
mar            0.648         0.648       0.382  0.256
paro           0.919         0.919       0.196  0.665
prio           1.096         1.096       0.029  0.001
log-vraisemblance : statsmodels -658.748 | lifelines -658.748
```

Les deux bibliothèques donnent les mêmes résultats. L'**aide financière** (`fin`, attribuée au hasard) réduit le risque de nouvelle arrestation d'environ **32 %** ($\mathrm{HR}\approx0{,}68$), un effet à la limite de la significativité ($p\approx0{,}047$ : avec 114 arrestations seulement, la précision est limitée) ; chaque condamnation antérieure l'augmente d'environ 10 % ; chaque année d'âge de plus le réduit de près de 6 %. Notez que, comme pour notre offre de bienvenue, la variable d'intérêt a été **randomisée** : c'est ce qui autorise la lecture causale (volume II, chapitre 7, pour aller plus loin).

> ✅ **À retenir**
> - Le modèle de Cox : $h(t\mid x)=h_0(t)e^{x^\top\beta}$. Le risque de base $h_0$ est **libre** ; chaque coefficient est un **rapport de risques** $\mathrm{HR}=e^{\beta}$, constant dans le temps.
> - La **vraisemblance partielle** $\prod_i e^{x_i^\top\beta}/\sum_{k\in R_i}e^{x_k^\top\beta}$ ne contient pas $h_0$. Son score est $\sum_i(x_i-\bar x_{R_i})$ (les résidus de Schoenfeld) ; **le test du log-rank est le test de score** du modèle à une variable de groupe.
> - Pour les **ex aequo**, préférez **Efron** à Breslow, surtout quand les durées sont arrondies.
> - L'hypothèse de **proportionnalité** se vérifie par le graphique log-log et par le test de score de Grambsch-Therneau (par défaut avec le rang du temps) ; en cas de violation : stratifier, introduire un effet variable dans le temps, ou changer de résumé.
> - Une variable connue seulement **après** un certain temps de survie doit être traitée comme **dépendant du temps** (format à épisodes), sinon on tombe dans le **biais d'immortalité**.
> - Le **risque de base** s'estime a posteriori par Breslow ; on en déduit $S(t\mid x)=\exp[-H_0(t)e^{x^\top\beta}]$ pour tout profil.
> - L'**indice de concordance** mesure la capacité à ordonner les clients ; un effet très significatif peut aller avec un C-index modeste.


## 5.4 Modèles de durée paramétriques

> 💡 **Intuition.** Le modèle de Cox est élégant parce qu'il ne dit rien sur la forme du risque de base. Mais ce silence a un prix : on ne peut rien dire **au-delà** de ce qu'on a observé. Yasmine voudrait savoir combien un client rapporte *au total*, y compris pendant les années à venir que personne n'a encore vécues. Pour extrapoler, il faut **parier sur une forme** de loi. Les modèles paramétriques font ce pari : ils décrivent la durée par une loi connue (exponentielle, Weibull, log-normale…) dont les paramètres dépendent des caractéristiques du client. En échange du pari, on obtient des courbes lisses, des durées moyennes, des extrapolations, et des estimations plus précises *si la forme est bonne*.

### 5.4.1 Le modèle à temps de vie accéléré

Les modèles paramétriques s'écrivent le plus naturellement sur le **logarithme de la durée** (le logarithme transforme une quantité positive et asymétrique en une quantité symétrique, comme pour la régression linéaire du début du volume) :
$$\boxed{\ \ln T=\mu(x)+\sigma\,W,\qquad \mu(x)=x^\top\gamma\ }$$
où $W$ est une variable aléatoire de loi **fixée** (le « bruit ») et $\sigma>0$ un paramètre d'**échelle**. C'est le **modèle à temps de vie accéléré** (en anglais *accelerated failure time*, AFT). Le choix de la loi de $W$ détermine la famille :

| Loi de $W$ | Loi de $T$ | $S(t\mid x)$, avec $z=(\ln t-\mu)/\sigma$ | Forme du risque $h(t)$ |
|---|---|---|---|
| $\sigma=1$, valeur extrême | **exponentielle** | $\exp(-e^{z})$ | constant |
| valeur extrême (Gumbel du minimum) | **Weibull** | $\exp(-e^{z})$ | monotone : croissant si $\sigma<1$, décroissant si $\sigma>1$ |
| normale | **log-normale** | $1-\Phi(z)$ | croît puis décroît |
| logistique | **log-logistique** | $1/(1+e^{z})$ | croît puis décroît (ou décroît seulement si $\sigma\ge1$) |

(On reconnaît la forme de Weibull du 5.1.3 avec la **forme** $k=1/\sigma$ et l'**échelle** $e^{\mu}$.)

**Interprétation : l'« accélération ».** Écrivons $T=e^{x^\top\gamma}\,T_0$, où $T_0=e^{\sigma W}$ est la durée d'un client « de référence » ($x=0$). Un client de caractéristiques $x$ vit **$e^{x^\top\gamma}$ fois plus longtemps** : les covariables **accélèrent ou ralentissent l'horloge** :
$$S(t\mid x)=S_0\big(t\,e^{-x^\top\gamma}\big).$$
Le facteur $e^{\gamma_j}$ est le **facteur d'accélération** : s'il vaut 1,37 pour l'offre de bienvenue, tout se passe comme si le temps s'écoulait 1,37 fois plus lentement pour un client qui l'a reçue ; sa durée **médiane** (et sa durée moyenne) est 37 % plus longue. C'est un langage plus parlant que le rapport de risques : *« l'offre rallonge la relation de 37 % »*.

> ⚠️ **Attention au sens des coefficients.** Dans un modèle AFT, un coefficient **positif** signifie une durée **plus longue** (protecteur). Dans le modèle de Cox, un coefficient **positif** signifie un risque **plus élevé** (néfaste). Les signes sont opposés ! Si l'on compare ce que fait Cox et ce que fait un AFT, il faut convertir (ce que nous ferons au 5.4.2).

### 5.4.2 La Weibull : à la fois « risques proportionnels » et « temps accéléré »

Parmi toutes les lois, la Weibull a une propriété unique : elle appartient aux **deux** familles. Montrons-le. Avec $k=1/\sigma$ et $\lambda(x)=e^{x^\top\gamma}$,
$$S(t\mid x)=\exp\!\Big[-\Big(\frac{t}{\lambda(x)}\Big)^{k}\Big],\qquad H(t\mid x)=\Big(\frac{t}{\lambda(x)}\Big)^{k}=t^{k}\,e^{-k\,x^\top\gamma}.$$
Dérivons pour obtenir le risque :
$$h(t\mid x)=k\,t^{k-1}\,e^{-k\,x^\top\gamma}=\underbrace{k\,t^{k-1}}_{h_0(t)}\ \cdot\ e^{x^\top\beta}\qquad\text{avec}\quad\boxed{\ \beta=-k\,\gamma=-\gamma/\sigma\ }.$$
C'est exactement la forme du modèle de Cox, avec un risque de base **imposé** $h_0(t)=kt^{k-1}$. Les coefficients des deux modèles se déduisent l'un de l'autre. C'est un excellent test de cohérence : *si les données sont vraiment Weibull, un modèle de Cox et un AFT Weibull doivent donner les mêmes effets*.

### 5.4.3 Le maximum de vraisemblance, écrit à la main

La vraisemblance avec censure (5.1.5) s'écrit pour un AFT, avec $z_i=(\ln y_i-x_i^\top\gamma)/\sigma$, $f_W$ la densité et $S_W$ la survie de $W$ :
$$\ell(\gamma,\sigma)=\sum_i\Big[\delta_i\big(\ln f_W(z_i)-\ln\sigma-\ln y_i\big)+(1-\delta_i)\ln S_W(z_i)\Big].$$
(La densité de $T=e^{\mu+\sigma W}$ est $f_W(z)/(\sigma t)$ : c'est le changement de variable habituel.) Pour la Weibull, $\ln f_W(z)=z-e^z$ et $\ln S_W(z)=-e^z$ ; pour la log-normale, $f_W=\varphi$ et $S_W=1-\Phi$ ; pour la log-logistique, $\ln f_W(z)=z-2\ln(1+e^z)$ et $\ln S_W(z)=-\ln(1+e^z)$. Le code suivant écrit ces trois vraisemblances, les maximise numériquement et calcule les erreurs standard par la **hessienne** numérique de $-\ell$ (l'inverse de l'information, comme au volume I, section 3.2).

```python
import numpy as np
import pandas as pd
from math import gamma as Gamma
from scipy import stats
from scipy.optimize import minimize
from statsmodels.tools.numdiff import approx_hess3

c = pd.read_csv("donnees/clients.csv")
y, d = c["duree_mois"].to_numpy(), c["churn"].to_numpy()
X = pd.get_dummies(c[["offre_bienvenue", "age", "canal_acquisition"]], drop_first=True, dtype=float)
Xc = np.column_stack([np.ones(len(c)), X.to_numpy()])            # première colonne : constante
noms = ["(constante)"] + list(X.columns)

def log_vrais_aft(theta, y, d, X, loi):
    """theta = (gamma_0..gamma_p, ln sigma). Retourne la log-vraisemblance (avec censure à droite)."""
    gam, sigma = theta[:-1], np.exp(theta[-1])
    z = (np.log(y) - X @ gam) / sigma
    if loi == "weibull":
        lf, ls = z - np.exp(z), -np.exp(z)
    elif loi == "lognormale":
        lf, ls = stats.norm.logpdf(z), stats.norm.logsf(z)
    elif loi == "loglogistique":
        lf, ls = z - 2 * np.log1p(np.exp(z)), -np.log1p(np.exp(z))
    return np.sum(d * (lf - np.log(sigma) - np.log(y)) + (1 - d) * ls)

def ajuster(loi, y, d, X, sigma_fixe=None):
    """Maximum de vraisemblance. sigma_fixe=1 donne l'exponentielle (Weibull avec sigma = 1)."""
    p = X.shape[1]
    if sigma_fixe is None:
        f = lambda t: -log_vrais_aft(t, y, d, X, loi)
        t0 = np.concatenate([[np.log(y.mean())], np.zeros(p - 1), [0.0]])
    else:
        f = lambda t: -log_vrais_aft(np.concatenate([t, [np.log(sigma_fixe)]]), y, d, X, loi)
        t0 = np.concatenate([[np.log(y.mean())], np.zeros(p - 1)])
    r = minimize(f, t0, method="Nelder-Mead", options={"xatol": 1e-9, "fatol": 1e-11, "maxiter": 20000, "maxfev": 20000})
    r = minimize(f, r.x, method="BFGS")                                   # affinage
    H = approx_hess3(r.x, f)
    return {"theta": r.x, "cov": np.linalg.inv(H), "ll": -r.fun, "k": len(r.x)}

ajustements = {loi: ajuster(loi, y, d, Xc) for loi in ("weibull", "lognormale", "loglogistique")}
ajustements["exponentielle"] = ajuster("weibull", y, d, Xc, sigma_fixe=1.0)

wb = ajustements["weibull"]
se = np.sqrt(np.diag(wb["cov"]))
tab = pd.DataFrame({"gamma": wb["theta"][:-1], "ET": se[:-1], "facteur d'accélération e^gamma": np.exp(wb["theta"][:-1])}, index=noms)
print(tab.round(4).to_string())
sigma = np.exp(wb["theta"][-1])
print(f"\nsigma = {sigma:.4f}  ->  forme k = 1/sigma = {1 / sigma:.4f}   (ET de ln sigma : {se[-1]:.4f})")
print(f"log-vraisemblance = {wb['ll']:.3f}")
```
<!--sortie-->
```text
                              gamma      ET  facteur d'accélération e^gamma
(constante)                  3.5257  0.0970                         33.9765
offre_bienvenue              0.3132  0.0489                          1.3678
age                          0.0102  0.0023                          1.0102
canal_acquisition_Instagram -0.4799  0.0636                          0.6188
canal_acquisition_Site      -0.2452  0.0671                          0.7825

sigma = 0.7563  ->  forme k = 1/sigma = 1.3223   (ET de ln sigma : 0.0253)
log-vraisemblance = -4657.378
```

Comparons avec **R** (`survreg`, la référence) et avec `lifelines` :

```r
w_r <- survreg(Surv(duree_mois, churn) ~ offre_bienvenue + age + canal_acquisition, data = clients, dist = "weibull")
print(summary(w_r))
```
<!--sortie-->
```text

Call:
survreg(formula = Surv(duree_mois, churn) ~ offre_bienvenue + 
    age + canal_acquisition, data = clients, dist = "weibull")
                             Value Std. Error      z       p
(Intercept)                 3.5257     0.0970  36.34 < 2e-16
offre_bienvenue             0.3132     0.0489   6.40 1.5e-10
age                         0.0102     0.0023   4.43 9.3e-06
canal_acquisitionInstagram -0.4799     0.0636  -7.55 4.4e-14
canal_acquisitionSite      -0.2452     0.0671  -3.66 0.00026
Log(scale)                 -0.2794     0.0253 -11.04 < 2e-16

Scale= 0.756 

Weibull distribution
Loglik(model)= -4657.4   Loglik(intercept only)= -4714.4
	Chisq= 114.02 on 4 degrees of freedom, p= 1e-23 
Number of Newton-Raphson Iterations: 6 
n= 2000 
```

```python
from lifelines import WeibullAFTFitter

df_ll = pd.concat([c[["duree_mois", "churn"]], X], axis=1)
ll_w = WeibullAFTFitter().fit(df_ll, "duree_mois", "churn")
print("lifelines : coefficients de lambda_ :", ll_w.params_["lambda_"].round(4).to_dict())
print(f"lifelines : rho = ln k = {ll_w.params_[('rho_', 'Intercept')]:.4f} (à la main : -ln sigma = {-wb['theta'][-1]:.4f}) ; log-vraisemblance {ll_w.log_likelihood_:.3f}")
```
<!--sortie-->
```text
lifelines : coefficients de lambda_ : {'age': 0.0102, 'canal_acquisition_Instagram': -0.4799, 'canal_acquisition_Site': -0.2452, 'offre_bienvenue': 0.3132, 'Intercept': 3.5257}
lifelines : rho = ln k = 0.2794 (à la main : -ln sigma = 0.2794) ; log-vraisemblance -4657.378
```

Les trois sources donnent les mêmes coefficients, la même échelle et la même log-vraisemblance. Lecture :

- **Offre de bienvenue** : facteur d'accélération $e^{0{,}313}\approx1{,}37$ : la durée de vie d'un client qui l'a reçue est **37 % plus longue** (à âge et canal égaux).
- **Canal** : par rapport à la boutique, un client arrivé par Instagram a une durée de vie **38 % plus courte** ($e^{-0{,}48}\approx0{,}62$) et un client arrivé par le site, **22 % plus courte** ($e^{-0{,}245}\approx0{,}78$).
- **Âge** : chaque année en plus allonge la durée d'environ 1 %.
- **Forme** : $k\approx1{,}32>1$ : le risque **augmente** avec l'ancienneté, ce qui confirme ce que montrait la comparaison de Kaplan-Meier et de l'exponentielle (5.2.2).

**La vérification croisée avec Cox.** Convertissons ces coefficients AFT en coefficients de risques par $\beta=-\gamma/\sigma$ et comparons au modèle de Cox de la section 5.3 :

```python
beta_ph = -wb["theta"][1:-1] / sigma
cox_coef = np.array([-0.40612, -0.01363, 0.63508, 0.32580])          # section 5.3.3 (Breslow)
print(pd.DataFrame({"Weibull converti (-gamma/sigma)": beta_ph, "Cox (5.3.3)": cox_coef}, index=noms[1:]).round(4).to_string())
```
<!--sortie-->
```text
                             Weibull converti (-gamma/sigma)  Cox (5.3.3)
offre_bienvenue                                      -0.4141      -0.4061
age                                                  -0.0135      -0.0136
canal_acquisition_Instagram                           0.6346       0.6351
canal_acquisition_Site                                0.3242       0.3258
```

Les deux séries sont presque identiques : les données sont bien compatibles avec une Weibull. Les erreurs standard sont, elles aussi, voisines (environ 0,065 pour l'offre dans les deux cas, en convertissant celle de l'AFT par $0{,}0489/0{,}756$). Quand la forme paramétrique est bonne, on pourrait espérer un gain de précision par rapport à Cox ; ici il est négligeable : avec 977 départs, le risque de base est déjà estimé très précisément, et Cox ne perd presque rien.

### 5.4.4 Choisir entre plusieurs lois

Tous ces modèles ont le même nombre de paramètres sauf l'exponentielle (un de moins) ; on peut donc les comparer par la **vraisemblance** et le **critère d'Akaike** (AIC $=2k-2\ell$, voir la section 1.4 de ce volume ; plus petit = meilleur).

```python
lignes = []
for loi, r in ajustements.items():
    lignes.append({"loi": loi, "paramètres": r["k"], "log-vraisemblance": round(r["ll"], 2), "AIC": round(2 * r["k"] - 2 * r["ll"], 2)})
print(pd.DataFrame(lignes).sort_values("AIC").to_string(index=False))

# Test du rapport de vraisemblance : exponentielle (sigma = 1) contre Weibull
lr = 2 * (ajustements["weibull"]["ll"] - ajustements["exponentielle"]["ll"])
print(f"\nexponentielle contre Weibull : chi2 = {lr:.1f} (1 ddl), p = {stats.chi2.sf(lr, 1):.1e}")
```
<!--sortie-->
```text
          loi  paramètres  log-vraisemblance     AIC
      weibull           6           -4657.38 9326.76
loglogistique           6           -4663.73 9339.45
   lognormale           6           -4697.20 9406.40
exponentielle           5           -4710.58 9431.17

exponentielle contre Weibull : chi2 = 106.4 (1 ddl), p = 6.0e-25
```

```r
for (loi in c("weibull", "lognormal", "loglogistic", "exponential")) {
  f <- survreg(Surv(duree_mois, churn) ~ offre_bienvenue + age + canal_acquisition, data = clients, dist = loi)
  cat(sprintf("%-12s log-vraisemblance = %.3f   AIC = %.2f\n", loi, f$loglik[2], AIC(f)))
}
```
<!--sortie-->
```text
weibull      log-vraisemblance = -4657.378   AIC = 9326.76
lognormal    log-vraisemblance = -4697.200   AIC = 9406.40
loglogistic  log-vraisemblance = -4663.725   AIC = 9339.45
exponential  log-vraisemblance = -4710.583   AIC = 9431.17
```

La **Weibull** est nettement la meilleure ; la log-logistique arrive deuxième (13 points d'AIC derrière), la log-normale troisième, l'exponentielle dernière. Le test du rapport de vraisemblance rejette l'exponentielle de façon écrasante : le risque n'est pas constant. Les valeurs coïncident avec celles de R.

Un AIC compare des modèles **entre eux** ; il ne dit pas si le meilleur est *bon*. Pour juger l'adéquation, on utilise les **résidus de Cox-Snell**.

> 📐 **Résidus de Cox-Snell.** Si $T$ a pour fonction de survie $S$, alors $S(T)$ suit une loi uniforme (transformée intégrale de probabilité) et donc $H(T)=-\ln S(T)$ suit une loi **exponentielle de paramètre 1**. Pour un modèle correct, les résidus $r_i=\hat H(y_i\mid x_i)$ se comportent comme un échantillon **censuré** de loi exponentielle(1). On estime donc le risque cumulé de ces résidus par Kaplan-Meier (on garde la censure, $\delta_i$) : le graphique de ce risque cumulé contre $r$ doit suivre la **diagonale**.

Superposons la comparaison globale (survie marginale prédite par chaque modèle, contre Kaplan-Meier) et les résidus de Cox-Snell, pour la Weibull et pour l'exponentielle :

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"

def survie_aft(t, mu, sigma, loi):
    z = (np.log(t) - mu) / sigma
    return {"weibull": lambda: np.exp(-np.exp(z)), "lognormale": lambda: stats.norm.sf(z), "loglogistique": lambda: 1 / (1 + np.exp(z))}[loi]()

def survie_marginale(t_grille, theta, loi, Xmat):
    mu, sg = Xmat @ theta[:-1], np.exp(theta[-1])
    return np.array([survie_aft(t, mu, sg, loi).mean() for t in t_grille])

def km_simple(t, dd):
    tj = np.unique(t[dd == 1])
    ys, ev = np.sort(t), np.sort(t[dd == 1])
    n_ = len(t) - np.searchsorted(ys, tj, side="left")
    dj_ = np.searchsorted(ev, tj, side="right") - np.searchsorted(ev, tj, side="left")
    return tj, np.cumprod(1 - dj_ / n_)

grille = np.linspace(0.5, 84, 150)
tj_km, S_km = km_simple(y, d)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
ax1.step(np.concatenate([[0], tj_km]), np.concatenate([[1], S_km]), where="post", color="#52514e", lw=2.2, label="Kaplan-Meier")
for loi, couleur, nom in [("weibull", ORANGE, "Weibull"), ("loglogistique", AQUA, "log-logistique"),
                          ("lognormale", VIOLET, "log-normale")]:
    ax1.plot(grille, survie_marginale(grille, ajustements[loi]["theta"], loi, Xc), color=couleur, lw=1.6, label=nom)
th_e = np.concatenate([ajustements["exponentielle"]["theta"], [0.0]])
ax1.plot(grille, survie_marginale(grille, th_e, "weibull", Xc), color=BLEU, lw=1.6, ls="--", label="exponentielle")
ax1.set_xlabel("mois depuis l'inscription")
ax1.set_ylabel("proportion de clients encore là")
ax1.set_title("Survie prédite (moyenne sur les 2 000 clients)")
ax1.legend(frameon=False, fontsize=9)
ax1.set_ylim(0, 1.02)

# Résidus de Cox-Snell
for loi, th, couleur, nom in [("weibull", ajustements["weibull"]["theta"], ORANGE, "Weibull"), ("weibull", th_e, BLEU, "exponentielle")]:
    mu, sg = Xc @ th[:-1], np.exp(th[-1])
    r = -np.log(survie_aft(y, mu, sg, loi))                  # résidus de Cox-Snell : H(y_i | x_i)
    tj_r, S_r = km_simple(r, d)
    ax2.step(tj_r, -np.log(S_r), where="post", color=couleur, lw=1.8, label=nom)
ax2.plot([0, 3], [0, 3], color="#898781", lw=1, ls=":")
ax2.set_xlim(0, 2.6)
ax2.set_ylim(0, 2.6)
ax2.set_xlabel("résidu de Cox-Snell r")
ax2.set_ylabel("risque cumulé estimé des résidus")
ax2.set_title("Adéquation : suivre la diagonale")
ax2.legend(frameon=False, fontsize=9, loc="upper left")
plt.tight_layout()
plt.savefig("figures/ch05-param-ajustement.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![À gauche : survie de Kaplan-Meier des 2 000 clients et survie moyenne prédite par quatre modèles paramétriques. À droite : résidus de Cox-Snell du modèle de Weibull et du modèle exponentiel avec covariables ; le bon modèle suit la diagonale.](figures/ch05-param-ajustement.png)

À gauche, les quatre modèles sont presque indiscernables de Kaplan-Meier jusqu'à 35 mois environ, sauf l'exponentielle, qui prévoit trop de départs au tout début (le schéma de la section 5.2.2). Au-delà de 40 mois, les courbes se séparent : la Weibull suit Kaplan-Meier jusqu'à 55 mois environ, puis passe **un peu en dessous** ; les trois autres lois restent **au-dessus**. À droite, les résidus de Cox-Snell du modèle de Weibull suivent la diagonale jusqu'à $r\approx1{,}5$ (au-delà, quelques résidus seulement : le tracé est instable), tandis que ceux du modèle exponentiel s'en écartent dès que $r$ dépasse environ 0,7.

### 5.4.5 Extrapoler et chiffrer : la valeur vie client

Yasmine veut savoir **ce que rapporte un client en moyenne sur toute sa vie**. Pour cela, il lui faut la survie *au-delà* de la fenêtre observée (84 mois au plus). Seul un modèle paramétrique peut fournir cette extrapolation.

La **durée de vie moyenne** d'un client de profil $x$ dans un modèle de Weibull est $E[T\mid x]=\lambda(x)\,\Gamma(1+1/k)$ (section 5.1.3). La **valeur vie client** actualisée (en anglais *customer lifetime value*, CLV) combine cette survie avec un revenu :
$$\mathrm{CLV}(x)=m\sum_{t=0}^{T_{\max}}\frac{S(t\mid x)}{(1+r)^{t}}$$
où $m$ est la **marge mensuelle** par client encore actif, $r$ le taux d'actualisation mensuel (un euro dans un an vaut moins qu'un euro aujourd'hui), et $S(t\mid x)$ la probabilité d'être encore client au mois $t$.

> 🧭 **Des hypothèses, pas des données.** Nous n'avons dans nos fichiers **ni marge ni coût**. Les trois chiffres ci-dessous sont des hypothèses que Yasmine devrait remplacer par les siens : une marge de **6 DT par mois** et par client actif, un taux d'actualisation de **1 % par mois** (environ 13 % par an) et un horizon de 20 ans (240 mois). Le but est de montrer la **mécanique** du calcul, pas de chiffrer vraiment la boutique.

```python
m_mensuelle, taux, horizon = 6.0, 0.01, 240
mois = np.arange(0, horizon)
k_hat, th = 1 / sigma, wb["theta"]
lam = np.exp(Xc @ th[:-1])                                         # échelle e^{x gamma} de chaque client

def S_groupe(masque):
    """Survie moyenne du groupe, d'après le modèle de Weibull ajusté, mois par mois."""
    return np.array([np.mean(np.exp(-(t / lam[masque]) ** k_hat)) for t in mois])

groupes = {"tous les clients": np.ones(len(c), bool),
           "sans offre": (c["offre_bienvenue"] == 0).to_numpy(), "avec offre": (c["offre_bienvenue"] == 1).to_numpy(),
           "Boutique": (c["canal_acquisition"] == "Boutique").to_numpy(), "Site": (c["canal_acquisition"] == "Site").to_numpy(),
           "Instagram": (c["canal_acquisition"] == "Instagram").to_numpy()}
lignes = []
for nom, masque in groupes.items():
    S = S_groupe(masque)
    clv = m_mensuelle * np.sum(S / (1 + taux) ** mois)
    apres_84 = m_mensuelle * np.sum(S[84:] / (1 + taux) ** mois[84:])
    lignes.append({"groupe": nom, "clients": int(masque.sum()), "durée moyenne (mois)": np.mean(lam[masque]) * Gamma(1 + 1 / k_hat),
                   "survie à 36 mois": S[36], "CLV (DT)": clv, "part de la CLV après 84 mois (%)": 100 * apres_84 / clv})
print(pd.DataFrame(lignes).round(3).to_string(index=False))
```
<!--sortie-->
```text
          groupe  clients  durée moyenne (mois)  survie à 36 mois  CLV (DT)  part de la CLV après 84 mois (%)
tous les clients     2000                41.339             0.453   186.096                             3.741
      sans offre      985                35.167             0.384   165.806                             2.156
      avec offre     1015                47.329             0.521   205.785                             4.981
        Boutique      504                53.159             0.574   223.468                             6.364
            Site      680                42.068             0.471   189.751                             3.545
       Instagram      816                33.431             0.364   159.967                             1.672
```

Quelques vérifications de bon sens. La survie moyenne à 36 mois du modèle (0,453) retrouve **exactement** la valeur de Kaplan-Meier de la section 5.2 (0,453), ce qui confirme que le modèle colle aux données observées. La durée moyenne d'un client est de **41 mois**, tandis que la durée moyenne *restreinte* à 60 mois de Kaplan-Meier valait 34 mois : l'écart (7 mois) est la part de la vie *au-delà de 60 mois*, que Kaplan-Meier ne peut pas chiffrer et que le modèle extrapole. Et la durée moyenne **exponentielle** de la section 5.1.5 (48 mois) était trop optimiste.

**L'offre de bienvenue en valait-elle la peine ?** Elle augmente la CLV de 166 à 206 DT par client, soit un gain de **40 DT** d'actualisé. Si l'offre coûte, par hypothèse, 10 DT par client, le gain net est de 30 DT par client. Comme l'offre est randomisée, cette différence est une estimation de **l'effet causal** de l'offre sur la valeur. Voyons si le résultat dépend des hypothèses :

```python
S0, S1 = S_groupe(groupes["sans offre"]), S_groupe(groupes["avec offre"])
cout_offre = 10.0
print(f"CLV sans offre : {m_mensuelle * np.sum(S0 / (1 + taux) ** mois):.1f} DT | avec offre : {m_mensuelle * np.sum(S1 / (1 + taux) ** mois):.1f} DT\n")
print("gain net par client (CLV avec offre - CLV sans offre - coût de 10 DT), selon les hypothèses :")
resultats = pd.DataFrame(index=[f"taux {100 * r:.1f} %/mois" for r in (0.005, 0.01, 0.02)],
                         columns=[f"marge {m} DT/mois" for m in (3, 6, 9)], dtype=float)
for r in (0.005, 0.01, 0.02):
    for m in (3, 6, 9):
        v = (1 + r) ** (-mois)
        resultats.loc[f"taux {100 * r:.1f} %/mois", f"marge {m} DT/mois"] = m * np.sum((S1 - S0) * v) - cout_offre
print(resultats.round(1).to_string())
```
<!--sortie-->
```text
CLV sans offre : 165.8 DT | avec offre : 205.8 DT

gain net par client (CLV avec offre - CLV sans offre - coût de 10 DT), selon les hypothèses :
                 marge 3 DT/mois  marge 6 DT/mois  marge 9 DT/mois
taux 0.5 %/mois             16.5             42.9             69.4
taux 1.0 %/mois             10.0             30.0             50.0
taux 2.0 %/mois              2.4             14.7             27.1
```

Le gain net reste **positif dans les neuf cas testés**, mais son ordre de grandeur varie d'un facteur 30 : de 69 DT par client (marge de 9 DT, actualisation faible) à seulement 2,4 DT (marge de 3 DT, actualisation de 2 % par mois), c'est-à-dire presque rien. La conclusion « l'offre est rentable » est donc **robuste** ; la conclusion « elle rapporte 30 DT par client » ne l'est pas. Voilà exactement le genre d'information utile : on peut dire à Yasmine que l'offre ne perd pas d'argent dans ce domaine d'hypothèses, et lui demander sa vraie marge pour chiffrer le gain.

> ⚠️ **Les limites de l'extrapolation.** La CLV dépend de la survie *au-delà* des données, donc de la forme de loi supposée. La dernière colonne du premier tableau chiffre cette dépendance : la part de la valeur située **après 84 mois** n'est que d'environ 4 % pour l'ensemble des clients (6 % pour la boutique), parce que l'**actualisation** écrase les mois lointains et que beaucoup de clients sont déjà partis. La CLV est donc peu sensible à l'extrapolation. Ce n'est pas le cas de la **durée moyenne**, qui n'est pas actualisée : c'est elle qui réclame de l'extrapolation (7 mois de plus que la RMST à 60 mois). Deux lois qui s'ajustent presque aussi bien sur 84 mois peuvent extrapoler très différemment : la figure du 5.4.4 le montre, avec une Weibull qui passe sous Kaplan-Meier à partir de 55 mois et des lois log-logistique et log-normale qui restent au-dessus. Le bon réflexe : refaire le calcul avec une autre loi (log-logistique) et comparer ; et ne jamais interpréter une CLV comme une certitude.

### 5.4.6 Une variable manquante : le service

Nos modèles ne connaissent ni la qualité du service reçu, ni la satisfaction du client. Or l'enquête de satisfaction (`donnees/enquete_satisfaction.csv`) en mesure une partie : les notes `q5` à `q8` portent sur le service et la livraison. Environ 60 % des clients ont répondu. Que se passe-t-il si l'on ajoute leur **note moyenne de service** au modèle de survie, sur les répondants ?

```python
q = pd.read_csv("donnees/enquete_satisfaction.csv")
q["service"] = q[["q5", "q6", "q7", "q8"]].mean(axis=1)
rep = c.merge(q[["id_client", "service"]], on="id_client")
rep["service_std"] = (rep["service"] - rep["service"].mean()) / rep["service"].std()
Xr_base = np.column_stack([np.ones(len(rep)), pd.get_dummies(rep[["offre_bienvenue", "age", "canal_acquisition"]], drop_first=True, dtype=float).to_numpy()])
Xr_serv = np.column_stack([Xr_base, rep["service_std"]])
yr, dr = rep["duree_mois"].to_numpy(), rep["churn"].to_numpy()
sans = ajuster("weibull", yr, dr, Xr_base)
avec = ajuster("weibull", yr, dr, Xr_serv)
se_a = np.sqrt(np.diag(avec["cov"]))
print(f"répondants : {len(rep)}")
print(f"sans le service : log-vraisemblance {sans['ll']:.1f} ; forme k = {1 / np.exp(sans['theta'][-1]):.3f}")
print(f"avec le service : log-vraisemblance {avec['ll']:.1f} ; forme k = {1 / np.exp(avec['theta'][-1]):.3f}")
print(f"coefficient du service (par écart-type de la note) : {avec['theta'][-2]:.3f} (ET {se_a[-2]:.3f}) -> durée x {np.exp(avec['theta'][-2]):.2f}")
lr_s = 2 * (avec["ll"] - sans["ll"])
print(f"rapport de vraisemblance : chi2 = {lr_s:.1f} (1 ddl), p = {stats.chi2.sf(lr_s, 1):.1e}")
```
<!--sortie-->
```text
répondants : 1212
sans le service : log-vraisemblance -2785.8 ; forme k = 1.312
avec le service : log-vraisemblance -2750.2 ; forme k = 1.368
coefficient du service (par écart-type de la note) : 0.262 (ET 0.031) -> durée x 1.30
rapport de vraisemblance : chi2 = 71.2 (1 ddl), p = 3.2e-17
```

Un client dont la note de service est **un écart-type au-dessus de la moyenne** reste en moyenne environ **30 % plus longtemps** (facteur 1,30) : le service compte, et le test du rapport de vraisemblance le confirme. C'est un exemple concret de ce qu'apportent les **variables explicatives pertinentes** (et du travail de construction d'indicateurs de la section 3.2 de ce volume, l'analyse factorielle, pour condenser huit notes en un score de service).

### 5.4.7 Révéler la vérité

Comme les données sont simulées, nous pouvons maintenant comparer nos estimations à la loi qui les a engendrées (documentée en tête de `build/donnees2.py`). Les durées sont de loi de **Weibull de forme 1,35**, avec
$$\ln T=3{,}6+0{,}30\,F_2+0{,}35\,\mathrm{offre}+\big\{\text{Boutique }{+}0{,}30,\ \text{Site }0,\ \text{Instagram }{-}0{,}15\big\}+0{,}008\,(\mathrm{âge}-36)+\sigma W,$$
où $F_2$ est un **facteur de sensibilité au service** (loi normale centrée réduite) **que le fichier ne contient pas**, et où $\sigma=1/1{,}35\approx0{,}74$. On peut même reconstruire ce facteur manquant avec le générateur de données, et ajuster le modèle « oracle » qui le connaît :

```python
import sys
sys.path.insert(0, "build")
import donnees2
_, F1, F2 = donnees2.clients()
oracle = ajuster("weibull", y, d, np.column_stack([Xc, F2]))
se_o = np.sqrt(np.diag(oracle["cov"]))

# Valeurs vraies, exprimées dans la même paramétrisation que notre modèle (âge centré en 36 dans le générateur,
# référence = Boutique, donc Instagram = -0.15 - 0.30 et Site = 0 - 0.30)
vrai = {"(constante)": 3.6 + 0.30 - 0.008 * 36, "offre_bienvenue": 0.35, "age": 0.008,
        "canal_acquisition_Instagram": -0.15 - 0.30, "canal_acquisition_Site": 0.0 - 0.30}
lignes = []
for j, nom in enumerate(noms):
    lignes.append({"paramètre": nom, "vérité": vrai[nom], "estimé (sans F2)": wb["theta"][j], "ET": se[j],
                   "écart / ET": (wb["theta"][j] - vrai[nom]) / se[j], "oracle (avec F2)": oracle["theta"][j]})
lignes.append({"paramètre": "forme k = 1/sigma", "vérité": 1.35, "estimé (sans F2)": 1 / sigma, "ET": np.nan,
               "écart / ET": np.nan, "oracle (avec F2)": 1 / np.exp(oracle["theta"][-1])})
lignes.append({"paramètre": "F2 (facteur manquant)", "vérité": 0.30, "estimé (sans F2)": np.nan, "ET": np.nan,
               "écart / ET": np.nan, "oracle (avec F2)": oracle["theta"][len(noms)]})
print(pd.DataFrame(lignes).round(3).to_string(index=False))
```
<!--sortie-->
```text
                  paramètre  vérité  estimé (sans F2)    ET  écart / ET  oracle (avec F2)
                (constante)   3.612             3.526 0.097      -0.890             3.562
            offre_bienvenue   0.350             0.313 0.049      -0.753             0.299
                        age   0.008             0.010 0.002       0.955             0.009
canal_acquisition_Instagram  -0.450            -0.480 0.064      -0.471            -0.486
     canal_acquisition_Site  -0.300            -0.245 0.067       0.817            -0.242
          forme k = 1/sigma   1.350             1.322   NaN         NaN             1.400
      F2 (facteur manquant)   0.300               NaN   NaN         NaN             0.310
```

Que montre cette comparaison ?

1. **Tous les coefficients du modèle réaliste sont à moins d'une erreur standard de la vérité** (colonne « écart / ET ») : la méthode retrouve ce qu'on a programmé (effet de l'offre : $+0{,}31$ estimé contre $+0{,}35$ ; les canaux et l'âge aussi).
2. Le modèle **oracle**, qui connaît le facteur manquant, retrouve **son coefficient** ($\approx0{,}31$ pour une vérité de 0,30). Il estime aussi une forme de $1{,}40$, contre $1{,}32$ pour le modèle sans $F_2$ : la vraie valeur (1,35) se situe entre les deux, et l'écart entre les deux estimations est précisément ce que prédit le point suivant. (De même, sur les répondants à l'enquête, la forme passe de 1,31 à 1,37 quand on ajoute la note de service.)
3. Le **déplacement de la forme** est un phénomène classique : quand une variable qui joue sur le risque est **omise**, le risque observé pour l'ensemble de la population est un **mélange** de risques individuels ; les clients les plus fragiles partent les premiers, de sorte que les survivants sont de plus en plus robustes. La population semble avoir un risque qui augmente **moins vite** que celui de chaque individu. En termes de modèle, on parle d'**hétérogénéité non observée** (ou de **fragilité**, *frailty*). Elle est inévitable : il y a toujours des variables que l'on ne mesure pas.

> ✅ **À retenir**
> - Un modèle **paramétrique** parie sur la loi de la durée. Il permet d'**extrapoler**, de calculer des durées moyennes et d'être plus précis que Cox *si la forme est bonne*.
> - Le modèle **AFT** s'écrit $\ln T=x^\top\gamma+\sigma W$ : les covariables **accélèrent ou ralentissent le temps** ; $e^{\gamma}$ est le facteur d'accélération (**signe opposé** à celui de Cox).
> - La **Weibull** est à la fois AFT et à risques proportionnels, avec $\beta=-\gamma/\sigma$ : un excellent test de cohérence avec Cox.
> - La vraisemblance avec censure s'écrit à la main pour chaque loi ; le résultat doit coïncider avec `survreg` de R. On choisit entre lois par l'**AIC** et on vérifie l'**adéquation** par les **résidus de Cox-Snell**.
> - La **valeur vie client** $\sum_t S(t\mid x)\,m/(1+r)^t$ repose sur des hypothèses explicites (marge, actualisation, horizon) et sur une extrapolation : on la présente avec une analyse de sensibilité, jamais comme une certitude.
> - Une variable pertinente **omise** (hétérogénéité non observée) déplace la forme apparente du risque ; on ne peut jamais exclure qu'il en existe.


## 5.5 ➕ Pour aller plus loin : les risques concurrents

> 🧭 **Section optionnelle.** Elle prolonge le chapitre quand **plusieurs événements** peuvent mettre fin à la durée et s'excluent mutuellement. Les sections 5.1 à 5.4 se lisent sans elle.

> 💡 **Intuition.** Jusqu'ici, il n'y avait qu'une façon de « sortir » : le client partait, ou on ne l'avait pas encore vu partir. Mais dans la vie d'une boutique, un compte peut aussi être **fermé de force** (impayés, soupçon de fraude, adresse invalide). Dès qu'une sortie de ce type survient, le client **ne peut plus partir volontairement** : les deux événements sont en **compétition**, et le premier qui arrive élimine l'autre. Si l'on oublie cette compétition, on surestime les probabilités de chaque cause.

### 5.5.1 Deux façons de sortir

Reprenons le fil de Dar Jasmin. Un client peut :

- **cause 1 : partir volontairement** (il ne commande plus et se désinscrit) ;
- **cause 2 : voir son compte fermé de force** (un incident de paiement, par exemple).

On observe un seul de ces événements, **le premier**. Notons $T_1$ et $T_2$ les durées « potentielles » jusqu'à chaque cause (la seconde n'est jamais observée si la première survient avant) ; la durée observée est $T=\min(T_1,T_2)$ (ou la durée de censure, comme avant) et la **cause** est celle qui l'emporte.

Les objets du 5.1 se généralisent :

- le **risque propre à la cause $k$** (*cause-specific hazard*) :
$$h_k(t)=\lim_{\Delta t\to0}\frac{P(t\le T<t+\Delta t,\ \text{cause}=k\mid T\ge t)}{\Delta t}\quad\text{: le taux de sortie par la cause }k\text{ parmi ceux encore là} ;$$
- le risque total $h(t)=h_1(t)+h_2(t)$ : les risques **s'additionnent**, et la survie (« rester client, quelle que soit la cause de départ ») est donc
$$S(t)=\exp\!\Big[-\int_0^t\big(h_1(u)+h_2(u)\big)du\Big]=\exp\big[-H_1(t)-H_2(t)\big] ;$$
- la **fonction d'incidence cumulée** (CIF) de la cause $k$ : la **probabilité** d'être sorti *par la cause $k$* avant $t$,
$$\boxed{\ F_k(t)=P(T\le t,\ \text{cause}=k)=\int_0^t h_k(u)\,S(u)\,du\ }$$

> 📐 **Pourquoi cette formule ?** Pour sortir par la cause $k$ **entre** $u$ et $u+du$, il faut deux choses : être encore là en $u$ (probabilité $S(u)$), puis sortir par la cause $k$ à cet instant (probabilité $h_k(u)\,du$). On additionne sur tous les instants. Le point crucial est que **$S(u)$ est la survie *totale*** : elle dépend des *deux* risques. La probabilité d'une cause dépend donc de l'autre. De plus, comme tout client finit dans l'un des trois états (encore là, sorti par 1, sorti par 2),
> $$S(t)+F_1(t)+F_2(t)=1\quad\text{à tout instant.}$$

### 5.5.2 Pourquoi « 1 − Kaplan-Meier » trompe

La tentation est de traiter la cause 2 comme une simple *censure* : « pour estimer le départ volontaire, on compte les fermetures forcées comme des clients perdus de vue ». Et d'estimer la probabilité de partir volontairement par $1-\hat S_{KM}(t)$. C'est **faux** : on estime ainsi la probabilité de départ volontaire *dans un monde imaginaire où aucune fermeture forcée n'existerait*, que l'on n'a jamais observé. Voyons-le sur dix clients.

| Client | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Mois | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 12 |
| Issue | départ (1) | fermé (2) | départ (1) | censuré | fermé (2) | départ (1) | censuré | départ (1) | fermé (2) | censuré |

**L'estimateur d'Aalen-Johansen** de la CIF de la cause $k$ applique la formule précédente en version « escalier » :
$$\hat F_k(t)=\sum_{j:\,t_j\le t}\hat S(t_{j}^{-})\,\frac{d_{kj}}{n_j}$$
où $n_j$ est l'ensemble à risque en $t_j$, $d_{kj}$ le nombre de sorties par la cause $k$ en $t_j$, et $\hat S(t_j^-)$ la survie **totale** de Kaplan-Meier (toutes causes confondues) juste avant $t_j$. Calculons à la main :

| $t_j$ | $n_j$ | $d_{1j}$ | $d_{2j}$ | $\hat S(t_j^-)$ | ajout à $\hat F_1$ | $\hat F_1$ | ajout à $\hat F_2$ | $\hat F_2$ | $\hat S(t_j)$ |
|---|---|---|---|---|---|---|---|---|---|
| 2 | 10 | 1 | 0 | 1,000 | $1/10=0{,}100$ | 0,100 | 0 | 0 | 0,900 |
| 3 | 9 | 0 | 1 | 0,900 | 0 | 0,100 | $0{,}9/9=0{,}100$ | 0,100 | 0,800 |
| 4 | 8 | 1 | 0 | 0,800 | $0{,}8/8=0{,}100$ | 0,200 | 0 | 0,100 | 0,700 |
| 6 | 6 | 0 | 1 | 0,700 | 0 | 0,200 | $0{,}7/6=0{,}117$ | 0,217 | 0,583 |
| 7 | 5 | 1 | 0 | 0,583 | $0{,}583/5=0{,}117$ | 0,317 | 0 | 0,217 | 0,467 |
| 9 | 3 | 1 | 0 | 0,467 | $0{,}467/3=0{,}156$ | 0,472 | 0 | 0,217 | 0,311 |
| 10 | 2 | 0 | 1 | 0,311 | 0 | 0,472 | $0{,}311/2=0{,}156$ | 0,372 | 0,156 |

(Les censures des mois 5, 8 et 12 réduisent $n_j$ sans produire de ligne.) À la fin, $0{,}156+0{,}472+0{,}372=1$ : la propriété $S+F_1+F_2=1$ est respectée. Comparons avec « 1 − KM » obtenu en traitant les fermetures comme des censures :

```python
import numpy as np
import pandas as pd

def incidence_cumulee(t, cause):
    """Aalen-Johansen. t : durées, cause : 0 = censuré, 1, 2, ... Retourne (instants, survie totale, [CIF des causes])."""
    t, cause = np.asarray(t, float), np.asarray(cause, int)
    tj = np.unique(t[cause > 0])
    ys = np.sort(t)
    n_ = len(t) - np.searchsorted(ys, tj, side="left")                          # ensemble à risque
    causes = sorted(set(cause[cause > 0]))
    dk = [np.array([np.sum((t == u) & (cause == k)) for u in tj]) for k in causes]
    S = np.cumprod(1 - sum(dk) / n_)                                            # survie totale (Kaplan-Meier toutes causes)
    S_avant = np.concatenate([[1.0], S[:-1]])                                   # S(t_j^-)
    return tj, S, [np.cumsum(S_avant * d_ / n_) for d_ in dk]

t10 = np.array([2, 3, 4, 5, 6, 7, 8, 9, 10, 12.])
c10 = np.array([1, 2, 1, 0, 2, 1, 0, 1, 2, 0])
tj10, S10, (F1_10, F2_10) = incidence_cumulee(t10, c10)
print(pd.DataFrame({"t_j": tj10, "S": S10, "F1": F1_10, "F2": F2_10, "S + F1 + F2": S10 + F1_10 + F2_10}).round(3).to_string(index=False))

# « 1 - KM » naïf : on traite la cause 2 comme une censure
tj_n, S_n, (F1_naif,) = incidence_cumulee(t10, np.where(c10 == 1, 1, 0))
print(f"\n1 - KM (cause 2 traitée comme censure) à t = 9 : {1 - S_n[-1]:.3f}   |   incidence cumulée correcte F1(9) = {F1_10[5]:.3f}")
```
<!--sortie-->
```text
 t_j     S    F1    F2  S + F1 + F2
 2.0 0.900 0.100 0.000          1.0
 3.0 0.800 0.100 0.100          1.0
 4.0 0.700 0.200 0.100          1.0
 6.0 0.583 0.200 0.217          1.0
 7.0 0.467 0.317 0.217          1.0
 9.0 0.311 0.472 0.217          1.0
10.0 0.156 0.472 0.372          1.0

1 - KM (cause 2 traitée comme censure) à t = 9 : 0.580   |   incidence cumulée correcte F1(9) = 0.472
```

Le « 1 − KM » donne 0,58 pour la probabilité de départ volontaire à 9 mois, alors que la vraie incidence cumulée est de 0,47. Il est **trop grand** : il fait comme si les trois clients dont le compte a été fermé (aux mois 3, 6, 10) étaient restés exposés au départ volontaire.

> ⚠️ **Les risques concurrents ne s'additionnent pas comme les 1 − KM.** Avec la méthode erronée, la somme des deux « probabilités » de sortie peut dépasser 1, ce qui est absurde. Avec les incidences cumulées, la somme $F_1+F_2$ est toujours $1-S\le1$.

### 5.5.3 Une simulation avec une vérité connue

Pour voir tout cela à l'échelle, simulons 6 000 clients avec deux causes. Nous choisissons les risques de sorte que :

- **cause 1 (départ volontaire)** : durée de loi de Weibull (forme 1,3), allongée par l'offre de bienvenue (offre tirée au hasard) ;
- **cause 2 (fermeture forcée)** : risque **constant** de 0,6 % par mois, multiplié par 2,2 pour les clients arrivés par Instagram, et **sans effet de l'offre** ;
- une censure uniforme entre 12 et 72 mois.

```python
rng = np.random.default_rng(55)
n = 6000
offre = rng.integers(0, 2, n)
insta = (rng.random(n) < 0.45).astype(int)
k1 = 1.3
echelle1 = 40 * np.exp(0.40 * offre)                       # l'offre allonge de 49 % le départ volontaire (exp(0.40))
T1 = echelle1 * rng.weibull(k1, n)                         # durée potentielle de départ volontaire
taux2 = 0.006 * np.exp(0.8 * insta)                        # fermeture forcée : taux constant, x 2.2 pour Instagram
T2 = rng.exponential(1 / taux2)
C = rng.uniform(12, 72, n)
t_obs = np.minimum.reduce([T1, T2, C])
cause = np.where(C <= np.minimum(T1, T2), 0, np.where(T1 <= T2, 1, 2))
rc = pd.DataFrame({"duree": t_obs, "cause": cause, "offre": offre, "instagram": insta})
rc.to_csv("donnees/ch05-risques-concurrents.csv", index=False)          # fichier relu par R plus bas
print("effectifs par issue (0 = censuré) :", rc["cause"].value_counts().sort_index().to_dict())

tj, S, (F1, F2) = incidence_cumulee(rc["duree"], rc["cause"])
def a(t, tab): return tab[np.searchsorted(tj, t, side="right") - 1]
horizons = (12, 24, 36, 48)
tj_1, S_1, (F1_naif,) = incidence_cumulee(rc["duree"], np.where(rc["cause"] == 1, 1, 0))     # cause 2 traitée comme censure
print(pd.DataFrame({"S (encore client)": [a(t, S) for t in horizons],
                    "F1 (départ volontaire)": [a(t, F1) for t in horizons],
                    "F2 (fermeture forcée)": [a(t, F2) for t in horizons],
                    "1 - KM naïf (cause 1)": [F1_naif[np.searchsorted(tj_1, t, side='right') - 1] for t in horizons]},
                   index=[f"{t} mois" for t in horizons]).round(3).to_string())
```
<!--sortie-->
```text
effectifs par issue (0 = censuré) : {0: 2079, 1: 2655, 2: 1266}
         S (encore client)  F1 (départ volontaire)  F2 (fermeture forcée)  1 - KM naïf (cause 1)
12 mois              0.762                   0.143                  0.095                  0.151
24 mois              0.538                   0.299                  0.163                  0.335
36 mois              0.367                   0.422                  0.211                  0.494
48 mois              0.251                   0.514                  0.235                  0.627
```

Comparons à **R** (`cmprsk::cuminc`) et à `lifelines`. Nous avons déposé la table dans un fichier précisément pour que R puisse la relire :

```r
library(cmprsk)
rc <- read.csv("donnees/ch05-risques-concurrents.csv")
ci <- cuminc(rc$duree, rc$cause)
print(round(timepoints(ci, c(12, 24, 36, 48))$est, 4))
```
<!--sortie-->
```text
        12     24     36     48
1 1 0.1428 0.2993 0.4217 0.5141
1 2 0.0948 0.1629 0.2109 0.2350
```

```python
from lifelines import AalenJohansenFitter

aj1 = AalenJohansenFitter(calculate_variance=False, seed=1).fit(rc["duree"], rc["cause"], event_of_interest=1)
print("lifelines, F1 aux horizons :", [round(float(aj1.cumulative_density_.loc[:t].iloc[-1, 0]), 4) for t in horizons])
print("à la main,  F1 aux horizons :", [round(float(a(t, F1)), 4) for t in horizons])
```
<!--sortie-->
```text
lifelines, F1 aux horizons : [0.1428, 0.2993, 0.4217, 0.5141]
à la main,  F1 aux horizons : [0.1428, 0.2993, 0.4217, 0.5141]
```

Les trois méthodes donnent les mêmes incidences. Remarquez la dernière colonne du premier tableau : le « 1 − KM » naïf **surestime** systématiquement la probabilité de départ volontaire (par exemple 0,49 contre 0,42 à 36 mois, et 0,63 contre 0,51 à 48 mois). La simulation nous permet même de comparer à la **vérité** : pour un groupe donné, $F_k(t)=\int_0^th_k(u)S(u)\,du$ s'évalue par une intégrale numérique, en mélangeant les clients d'Instagram (45 %) et des autres canaux.

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
u = np.linspace(0, 100, 20001)
du = u[1] - u[0]

def vraies_cif(off):
    """CIF vraies des deux causes pour le groupe 'off', en moyennant sur la part d'Instagram (45 %)."""
    echelle = 40 * np.exp(0.40 * off)
    h1 = (k1 / echelle) * (u / echelle) ** (k1 - 1)
    H1 = (u / echelle) ** k1
    F1_v = np.zeros_like(u); F2_v = np.zeros_like(u)
    for ins, poids in ((0, 0.55), (1, 0.45)):
        l2 = 0.006 * np.exp(0.8 * ins)
        S_v = np.exp(-H1 - l2 * u)
        F1_v += poids * np.cumsum(h1 * S_v) * du
        F2_v += poids * np.cumsum(l2 * S_v) * du
    return F1_v, F2_v

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
for off, couleur, nom in [(0, VIOLET, "sans offre"), (1, AQUA, "avec offre")]:
    g = rc[rc["offre"] == off]
    tj_g, S_g, (F1_g, F2_g) = incidence_cumulee(g["duree"], g["cause"])
    v1, v2 = vraies_cif(off)
    for ax, F_g, v in ((axes[0], F1_g, v1), (axes[1], F2_g, v2)):
        ax.step(np.concatenate([[0], tj_g]), np.concatenate([[0], F_g]), where="post", color=couleur, lw=2, label=nom + " (estimée)")
        ax.plot(u, v, color=couleur, lw=1.2, ls=":", label=nom + " (vraie)")
axes[0].set_title("Cause 1 : départ volontaire")
axes[1].set_title("Cause 2 : fermeture forcée")
for ax in axes:
    ax.set_xlim(0, 70); ax.set_xlabel("mois depuis l'inscription")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
axes[0].set_ylabel("probabilité cumulée (incidence)")
axes[0].set_ylim(0, 0.8)
plt.tight_layout()
plt.savefig("figures/ch05-risques-concurrents.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Incidences cumulées estimées (traits pleins) et vraies (pointillés) des deux causes de sortie, selon l'offre de bienvenue : à gauche le départ volontaire, à droite la fermeture forcée.](figures/ch05-risques-concurrents.png)

Observons la **cause 2**, à droite. L'offre n'a *aucun effet sur le risque de fermeture* (nous l'avons simulée ainsi). Pourtant, les deux courbes ne sont pas superposées : les clients avec offre ont une incidence de fermeture **plus élevée** (le test de Gray, plus bas, rejette l'égalité des deux courbes avec $p\approx3\times10^{-4}$). Pourquoi ? Parce qu'ils partent moins volontairement, donc **restent plus longtemps exposés** au risque de fermeture. La probabilité d'une cause dépend de l'autre : c'est la compétition.

### 5.5.4 Modéliser : deux questions, deux modèles

On peut régresser sur chaque cause de deux façons, qui répondent à **deux questions différentes**.

**Le modèle de Cox par cause.** On ajuste un modèle de Cox pour la cause $k$ en traitant les sorties par les *autres* causes comme des censures. Les coefficients sont des rapports de **risques propres à la cause** : *« parmi les clients encore là, comment la variable change-t-elle le taux de sortie par la cause $k$ ? »*. C'est la bonne question pour **comprendre le mécanisme** (l'offre diminue-t-elle le départ volontaire ?).

**Le modèle de Fine et Gray.** Il modélise directement le **risque de sous-distribution** : le taux de sortie par la cause $k$ parmi ceux qui *n'ont pas encore connu la cause $k$* (ceux qui ont eu l'autre cause restent dans l'ensemble à risque, avec un poids qui décroît). Le coefficient décrit alors l'effet de la variable **sur la CIF** elle-même. C'est la bonne question pour **prédire des probabilités** (quelle part de nos clients quittera volontairement d'ici trois ans ?).

```python
from statsmodels.duration.hazard_regression import PHReg

covariables = rc[["offre", "instagram"]]
for k in (1, 2):
    m = PHReg(rc["duree"], covariables, status=(rc["cause"] == k).astype(int), ties="efron").fit()
    tab = pd.DataFrame({"HR propre à la cause": np.exp(m.params), "IC95 bas": np.exp(m.params - 1.96 * m.bse),
                        "IC95 haut": np.exp(m.params + 1.96 * m.bse), "p": m.pvalues}, index=["offre", "instagram"])
    print(f"Modèle de Cox par cause : cause {k}")
    print(tab.round(3).to_string(), "\n")
```
<!--sortie-->
```text
Modèle de Cox par cause : cause 1
           HR propre à la cause  IC95 bas  IC95 haut      p
offre                     0.584     0.540      0.631  0.000
instagram                 0.974     0.901      1.053  0.504 

Modèle de Cox par cause : cause 2
           HR propre à la cause  IC95 bas  IC95 haut      p
offre                     1.033     0.925      1.154  0.565
instagram                 2.316     2.066      2.595  0.000 
```

```r
cov <- cbind(offre = rc$offre, instagram = rc$instagram)
for (k in 1:2) {
  f <- crr(rc$duree, rc$cause, cov, failcode = k, cencode = 0)
  cat("Fine-Gray, cause", k, "\n")
  print(round(summary(f)$conf.int[, c(1, 3, 4)], 3))      # exp(coef) et son IC95
  cat("\n")
}
print(cuminc(rc$duree, rc$cause, group = rc$offre)$Tests)
```
<!--sortie-->
```text
Fine-Gray, cause 1 
          exp(coef)  2.5% 97.5%
offre         0.604 0.560 0.652
instagram     0.792 0.733 0.855

Fine-Gray, cause 2 
          exp(coef)  2.5% 97.5%
offre         1.219 1.091 1.361
instagram     2.280 2.036 2.554

      stat           pv df
1 170.5141 0.0000000000  1
2  12.9234 0.0003244992  1
```

Lisons ces deux familles de résultats ensemble.

- **Cause 1 (départ volontaire).** L'offre réduit le risque propre à la cause 1 : $\widehat{\mathrm{HR}}\approx0{,}58$ (IC95 : 0,54 à 0,63), ce qui retrouve l'effet programmé ($e^{-0{,}40\times1{,}3}\approx0{,}59$ ; voir la conversion AFT ↔ risques proportionnels au 5.4.2). Le modèle de Fine et Gray donne un rapport de sous-distribution du même ordre (environ 0,60) : la réduction du risque se traduit en réduction de l'incidence.
- **Cause 2 (fermeture forcée).** Les clients d'**Instagram** ont un risque propre multiplié par **2,3** environ (IC95 : 2,07 à 2,60 ; la valeur programmée est $e^{0{,}8}\approx2{,}2$). Et l'**offre** n'a **aucun effet sur le risque** de fermeture : HR $=1{,}03$ (IC95 : 0,93 à 1,15). Mais, dans le modèle de Fine et Gray, l'offre **augmente significativement l'incidence** de la cause 2 : rapport de sous-distribution d'environ **1,22** (IC95 : 1,09 à 1,36). C'est exactement l'effet de compétition que montrait la figure : l'offre ne change pas le risque de fermeture, mais, en retenant plus longtemps les clients, elle les expose plus longtemps à ce risque.
- **Instagram et la cause 1 : le piège.** Dans le modèle par cause, Instagram n'a **aucun effet** sur le départ volontaire : HR $=0{,}97$ (IC95 : 0,90 à 1,05), et c'est la vérité. Mais dans le modèle de Fine et Gray, son rapport de sous-distribution est de **0,79** (IC95 : 0,73 à 0,86), **significativement inférieur à 1** : les clients d'Instagram ont une *incidence cumulée de départ volontaire plus faible*. Ce n'est pas qu'ils soient plus fidèles : ils sont **plus souvent éliminés avant** par la fermeture forcée, qui les empêche de partir volontairement. Le coefficient de Fine et Gray mélange l'effet direct sur la cause et l'effet de la compétition.

> 💡 **Quelle question posez-vous ?**
> - *« Pourquoi les clients partent-ils ? »* (étiologie, mécanisme) : **modèles par cause**. On y lit l'effet de chaque variable sur chaque cause, toutes choses égales.
> - *« Combien de clients seront perdus par chaque cause ? »* (pronostic, planification) : **incidences cumulées** (Aalen-Johansen) et **modèle de Fine et Gray**.
> - En cas de doute, présentez **les deux**, avec leurs interprétations.

### 5.5.5 Pièges

> ⚠️ **L'indépendance des causes ne se teste pas.** On ne peut observer que la première des deux durées $T_1,T_2$ : leur loi **jointe** n'est pas identifiable à partir des données. Le modèle par cause n'a pas besoin de cette hypothèse pour estimer les *risques propres* ; mais toute phrase du type « que se passerait-il si l'on supprimait la fermeture forcée ? » en a besoin, et elle est invérifiable. C'est la raison profonde pour laquelle « $1-\mathrm{KM}$ » n'a pas de sens ici.

> ⚠️ **Ne déclarez pas la cause 2 « censure » pour calculer une probabilité.** C'est valable pour estimer un *risque*, jamais pour estimer une *probabilité cumulée*. Si l'on veut une probabilité, on utilise l'incidence cumulée.

> ⚠️ **Événement composite.** Une autre option est de regrouper les causes (« tout départ, volontaire ou forcé ») et d'appliquer les méthodes des sections 5.1 à 5.4 : c'est licite si la question porte sur « rester client » et non sur le mécanisme. Il est alors plus sûr de **le dire**.

> ✅ **À retenir**
> - Avec plusieurs causes de sortie **concurrentes**, on observe la première seulement. Les risques propres $h_k$ s'additionnent ; $S=e^{-H_1-H_2}$ ; la **CIF** de la cause $k$ est $F_k(t)=\int_0^th_k(u)S(u)\,du$ et $S+F_1+F_2=1$.
> - **1 − Kaplan-Meier** (autres causes traitées en censure) **surestime** la probabilité d'une cause. Utilisez l'estimateur d'**Aalen-Johansen** $\hat F_k(t)=\sum_{t_j\le t}\hat S(t_j^-)\,d_{kj}/n_j$.
> - Le **modèle de Cox par cause** estime l'effet sur le **risque** (mécanisme) ; le modèle de **Fine et Gray** estime l'effet sur l'**incidence cumulée** (pronostic). Les deux peuvent diverger : une variable sans effet direct sur une cause peut modifier son incidence par la compétition.
> - La dépendance entre causes n'est pas identifiable : on évite les phrases « si l'autre cause n'existait pas ».


## 5.6 Exercices corrigés

Les exercices sont classés par difficulté : ⭐ (application directe), ⭐⭐ (demande de réfléchir), ⭐⭐⭐ (synthèse). **Cherchez d'abord seul(e)**, à la main quand c'est demandé, avant de lire le corrigé. Les fonctions écrites dans le chapitre (`kaplan_meier`, `logrank`, `cox_ph`, `test_ph`, `ajuster`, `incidence_cumulee`…) sont réutilisées dans les corrigés.

**Exercice 1 ⭐ (censure et Kaplan-Meier à la main).** Yasmine suit six clients : $(4;\text{parti})$, $(7;\text{censuré})$, $(9;\text{parti})$, $(12;\text{parti})$, $(15;\text{censuré})$, $(20;\text{censuré})$ (durées en mois). (a) Calculez la moyenne de toutes les durées, puis celle des seuls clients partis. (b) Calculez la courbe de Kaplan-Meier à la main. (c) Donnez la médiane de survie. (d) Calculez la durée moyenne restreinte jusqu'à 20 mois.

**Exercice 2 ⭐ (relations entre les fonctions).** Un client a, à l'âge $t$ de la relation (en mois), un risque instantané $h(t)=0{,}0008\,t$. (a) Déduisez $H(t)$ et $S(t)$. (b) Calculez $S(24)$ et la médiane. (c) De quelle loi de Weibull s'agit-il ? Donnez sa durée moyenne.

**Exercice 3 ⭐ (taux constant).** Sur un échantillon, on observe 40 départs pour un total de 1 600 mois-clients d'exposition. (a) Estimez le taux de départ mensuel $\lambda$ (exponentielle), son écart-type et un intervalle de confiance à 95 %. (b) Estimez $S(24)$ et la durée moyenne. (c) Testez $H_0:\lambda=0{,}03$ par le test de Wald et par le rapport de vraisemblance.

**Exercice 4 ⭐⭐ (Greenwood).** Huit clients : $(2;1)$, $(3;1)$, $(3;1)$, $(5;0)$, $(6;1)$, $(8;0)$, $(9;1)$, $(11;0)$ (durée ; 1 = parti, 0 = censuré). Construisez le tableau de Kaplan-Meier (avec les ex aequo), puis donnez $\hat S(6)$, son erreur standard de Greenwood et son intervalle de confiance log-log à 95 %.

**Exercice 5 ⭐⭐ (log-rank).** Deux groupes de cinq clients. Groupe A : $(3;1)$, $(6;1)$, $(8;0)$, $(10;1)$, $(12;0)$. Groupe B : $(5;1)$, $(7;1)$, $(9;1)$, $(11;0)$, $(13;0)$. Calculez à la main le test du log-rank (tableau aux instants de départ : ensembles à risque, départs attendus, variances), concluez, puis vérifiez avec `statsmodels`.

**Exercice 6 ⭐⭐ (durée moyenne restreinte).** Les courbes de survie de deux campagnes sont des escaliers. Campagne A : $S=1$ jusqu'à 6 mois, $0{,}8$ sur $[6,12[$, $0{,}5$ sur $[12,18[$, $0{,}3$ ensuite. Campagne B : $S=1$ jusqu'à 9 mois, $0{,}9$ sur $[9,15[$, $0{,}7$ sur $[15,21[$, $0{,}6$ ensuite. Calculez la durée moyenne restreinte à 24 mois de chaque campagne et leur différence. Que signifie ce nombre ?

**Exercice 7 ⭐⭐ (lire une sortie de Cox).** Un modèle de Cox donne : offre de bienvenue $\hat\beta=-0{,}40$ (ET $0{,}065$), âge $\hat\beta=-0{,}0136$ (ET $0{,}0030$), canal Instagram (contre Boutique) $\hat\beta=0{,}635$ (ET $0{,}084$). (a) Donnez pour chaque variable le rapport de risques, son IC95 et le $z$ de Wald. (b) Quel est l'effet de dix années d'âge de plus ? (c) Quel est le rapport de risques d'un client Instagram *avec* offre contre un client Boutique *sans* offre, à âge égal ? (d) La survie à 24 mois d'un client de référence est de 0,80 : quelle est celle du même client avec l'offre ? (e) Un AFT Weibull donne $\hat\gamma_{\text{offre}}=0{,}35$ avec $\hat\sigma=0{,}74$ : quel rapport de risques équivalent ?

**Exercice 8 ⭐⭐ (le biais d'immortalité).** Simulez 2 000 clients dont les durées sont exponentielles de taux 2 % par mois (graine 8), censurées uniformément entre 18 et 48 mois. Un cadeau est remis au mois 6 à la moitié des clients encore présents. Estimez l'effet du cadeau (qui n'en a aucun) (a) en traitant « a reçu le cadeau » comme une variable fixe, (b) correctement, avec une variable dépendant du temps. Commentez.

**Exercice 9 ⭐⭐ (estimer la forme de Weibull de deux façons).** Pour l'ensemble des 2 000 clients (sans covariables), estimez la forme $k$ de la loi de Weibull (a) par le graphique de Weibull : régression de $\ln(-\ln\hat S_{KM})$ sur $\ln t$ entre 6 et 60 mois ; (b) par maximum de vraisemblance. Comparez, et expliquez l'écart avec la valeur $k=1{,}35$ utilisée pour simuler.

**Exercice 10 ⭐⭐⭐ (log-rank et Cox).** (a) Montrez que le score du modèle de Cox à une variable binaire en $\beta=0$ vaut $O_1-E_1$. (b) Vérifiez numériquement, sur les 2 000 clients (variable `offre_bienvenue`), que la statistique de score $U^2/I$ est très proche du $\chi^2$ du log-rank. Pourquoi n'est-elle pas *exactement* égale ?

**Exercice 11 ⭐⭐⭐ (décider : le seuil de rentabilité).** Reprenez les survies moyennes avec et sans offre du 5.4.5. L'offre de bienvenue coûte maintenant 25 DT par client. À partir de quelle **marge mensuelle** par client actif est-elle rentable, pour un taux d'actualisation de 1 % par mois ? Et pour 2 % ?

**Exercice 12 ⭐⭐⭐ (risques concurrents à la main).** Huit clients, durées et causes de sortie (0 = censuré, 1 = départ volontaire, 2 = fermeture forcée) : $(1;1)$, $(2;2)$, $(3;1)$, $(4;0)$, $(5;2)$, $(6;1)$, $(7;0)$, $(9;2)$. Calculez à la main les incidences cumulées $\hat F_1$ et $\hat F_2$ (estimateur d'Aalen-Johansen) et la survie totale. Vérifiez que $\hat S+\hat F_1+\hat F_2=1$. Comparez $\hat F_1$ à « $1-\mathrm{KM}$ » où la cause 2 est traitée comme une censure.

**Exercice 13 ⭐⭐⭐ (proportionnalité des risques sur des données réelles).** Reprenez les données de récidive de Rossi (5.3.9). Appliquez le test de score de proportionnalité des risques du 5.3.5 à chacune des sept covariables. Quelles variables posent problème ? Que feriez-vous ?

---

### Corrigés

**Corrigé 1.** (a) Moyenne de toutes les durées : $(4+7+9+12+15+20)/6\approx11{,}17$ mois ; moyenne des seuls clients partis : $(4+9+12)/3\approx8{,}33$ mois. Les deux sont biaisées (5.1.1). (b) Départs aux mois 4, 9 et 12. À 4 mois, 6 clients à risque : $5/6=0{,}833$. À 9 mois (le client censuré à 7 est sorti), 4 clients à risque : $0{,}833\times3/4=0{,}625$. À 12 mois, 3 clients à risque : $0{,}625\times2/3=0{,}417$. (c) La courbe passe sous 0,5 au mois 12 : **médiane = 12 mois**. (d) $\mathrm{RMST}(20)=4\times1+5\times0{,}833+3\times0{,}625+8\times0{,}417=4+4{,}167+1{,}875+3{,}333=13{,}375$ mois.

```python
import numpy as np
import pandas as pd
from scipy import stats

y1 = np.array([4, 7, 9, 12, 15, 20.]); d1 = np.array([1, 0, 1, 1, 0, 0])
tj1, n1, dj1, S1_, gw1 = kaplan_meier(y1, d1)
print("moyenne de toutes les durées :", round(y1.mean(), 2), "| des seuls partis :", round(y1[d1 == 1].mean(), 2))
print("S aux instants de départ", tj1, ":", S1_.round(4), "| à risque :", n1)
print("médiane :", tj1[S1_ <= 0.5][0], "| RMST(20) :", round(rmst(tj1, S1_, 20), 3))
```
<!--sortie-->
```text
moyenne de toutes les durées : 11.17 | des seuls partis : 8.33
S aux instants de départ [ 4.  9. 12.] : [0.8333 0.625  0.4167] | à risque : [6 4 3]
médiane : 12.0 | RMST(20) : 13.375
```

**Corrigé 2.** (a) $H(t)=\int_0^t0{,}0008u\,du=0{,}0004\,t^2$, donc $S(t)=\exp(-0{,}0004\,t^2)$. (b) $S(24)=\exp(-0{,}0004\times576)=e^{-0{,}2304}\approx0{,}794$ ; la médiane vérifie $0{,}0004\,t^2=\ln2$, donc $t=\sqrt{\ln2/0{,}0004}\approx41{,}6$ mois. (c) Une Weibull a $H(t)=(t/\sigma)^k$ : on lit $k=2$ et $\sigma^{-2}=0{,}0004$, soit $\sigma=50$ mois. La durée moyenne vaut $\sigma\,\Gamma(1+1/k)=50\,\Gamma(1{,}5)\approx44{,}3$ mois.

```python
from math import gamma, log
from scipy.integrate import quad
print("S(24) =", round(np.exp(-0.0004 * 24 ** 2), 4), "| médiane =", round(np.sqrt(log(2) / 0.0004), 2))
print("moyenne par la formule :", round(50 * gamma(1.5), 2), "| par intégration de S :", round(quad(lambda t: np.exp(-0.0004 * t ** 2), 0, np.inf)[0], 2))
```
<!--sortie-->
```text
S(24) = 0.7942 | médiane = 41.63
moyenne par la formule : 44.31 | par intégration de S : 44.31
```

**Corrigé 3.** (a) $\hat\lambda=D/E=40/1600=0{,}025$ par mois ; $\widehat{se}=\hat\lambda/\sqrt D=0{,}025/\sqrt{40}\approx0{,}00395$ ; IC95 : $0{,}025\pm1{,}96\times0{,}00395$, soit $[0{,}0173\ ;\ 0{,}0327]$. (b) $\hat S(24)=e^{-0{,}025\times24}=e^{-0{,}6}\approx0{,}549$ ; durée moyenne $1/\hat\lambda=40$ mois. (c) Wald : $z=(0{,}025-0{,}03)/0{,}00395\approx-1{,}26$, $p\approx0{,}21$. Rapport de vraisemblance : $2[\ell(\hat\lambda)-\ell(0{,}03)]=2[D\ln(\hat\lambda/0{,}03)-(\hat\lambda-0{,}03)E]=2[40\ln(0{,}8333)+8]\approx1{,}41$, $p\approx0{,}23$. Les deux tests concluent de la même façon : **on ne rejette pas** $\lambda=0{,}03$ (les données sont compatibles aussi avec ce taux).

```python
D, E = 40, 1600
lam = D / E; se = lam / np.sqrt(D)
print(f"lambda = {lam:.4f}, ET = {se:.5f}, IC95 = [{lam - 1.96 * se:.4f} ; {lam + 1.96 * se:.4f}]")
print(f"S(24) = {np.exp(-lam * 24):.4f}, durée moyenne = {1 / lam:.1f} mois")
z = (lam - 0.03) / se
lr = 2 * (D * np.log(lam / 0.03) - (lam - 0.03) * E)
print(f"Wald : z = {z:.3f}, p = {2 * stats.norm.sf(abs(z)):.3f} | rapport de vraisemblance : chi2 = {lr:.3f}, p = {stats.chi2.sf(lr, 1):.3f}")
```
<!--sortie-->
```text
lambda = 0.0250, ET = 0.00395, IC95 = [0.0173 ; 0.0327]
S(24) = 0.5488, durée moyenne = 40.0 mois
Wald : z = -1.265, p = 0.206 | rapport de vraisemblance : chi2 = 1.414, p = 0.234
```

**Corrigé 4.** Départs : mois 2 (1 départ, 8 à risque : $7/8$), mois 3 (2 départs, 7 à risque : $5/7$), mois 6 (1 départ, 4 à risque, car le client censuré à 5 est sorti : $3/4$), mois 9 (1 départ, 2 à risque : $1/2$). D'où $\hat S(2)=0{,}875$, $\hat S(3)=0{,}875\times5/7=0{,}625$, $\hat S(6)=0{,}625\times3/4=0{,}469$, $\hat S(9)=0{,}234$. Greenwood : $\sum\frac{d_j}{n_j(n_j-d_j)}=\frac1{8\times7}+\frac2{7\times5}+\frac1{4\times3}=0{,}0179+0{,}0571+0{,}0833=0{,}1583$ ; l'erreur standard de $\hat S(6)$ vaut $0{,}469\times\sqrt{0{,}1583}\approx0{,}187$. Intervalle log-log : $\hat S^{\exp(\pm1{,}96\sqrt{G}/|\ln\hat S|)}$ avec $1{,}96\times\sqrt{0{,}1583}/|\ln0{,}469|=0{,}780/0{,}757=1{,}03$, d'où $[0{,}469^{2{,}80}\ ;\ 0{,}469^{1/2{,}80}]\approx[0{,}12\ ;\ 0{,}76]$ : un intervalle immense, faute de données.

```python
y4 = np.array([2, 3, 3, 5, 6, 8, 9, 11.]); d4 = np.array([1, 1, 1, 0, 1, 0, 1, 0])
tj4, n4, dj4, S4, gw4 = kaplan_meier(y4, d4)
print(pd.DataFrame({"t_j": tj4, "à risque": n4, "départs": dj4, "S": S4.round(4), "somme Greenwood": gw4.round(4)}).to_string(index=False))
s, plan, log_, loglog = intervalles(6, tj4, S4, gw4)
print(f"S(6) = {s:.4f} ; ET = {s * np.sqrt(surv_at(6, tj4, gw4)):.4f} ; IC log-log = [{loglog[0]:.3f} ; {loglog[1]:.3f}]")
```
<!--sortie-->
```text
 t_j  à risque  départs      S  somme Greenwood
 2.0         8        1 0.8750           0.0179
 3.0         7        2 0.6250           0.0750
 6.0         4        1 0.4688           0.1583
 9.0         2        1 0.2344           0.6583
S(6) = 0.4688 ; ET = 0.1865 ; IC log-log = [0.120 ; 0.763]
```

**Corrigé 5.** Aux instants de départ 3, 5, 6, 7, 9 et 10, on a respectivement $n_j=10,9,8,7,5,4$ clients à risque, dont $n_{Aj}=5,4,4,3,2,2$ dans le groupe A. Chaque instant compte un seul départ : $E_{Aj}=n_{Aj}/n_j$ et $V_j=\frac{n_{Aj}}{n_j}(1-\frac{n_{Aj}}{n_j})$. Le code donne le détail :

```python
y5 = np.array([3, 6, 8, 10, 12, 5, 7, 9, 11, 13.]); d5 = np.array([1, 1, 0, 1, 0, 1, 1, 1, 0, 0])
g5 = np.array(["A"] * 5 + ["B"] * 5)
lignes, O1, E1, V1 = [], 0, 0.0, 0.0
for t in np.unique(y5[d5 == 1]):
    n_ = int(np.sum(y5 >= t)); nA = int(np.sum((y5 >= t) & (g5 == "A")))
    dd = int(np.sum((y5 == t) & (d5 == 1))); dA = int(np.sum((y5 == t) & (d5 == 1) & (g5 == "A")))
    e = dd * nA / n_; v = dd * (nA / n_) * (1 - nA / n_) * (n_ - dd) / (n_ - 1)
    lignes.append((t, n_, nA, dd, dA, round(e, 4), round(v, 4))); O1 += dA; E1 += e; V1 += v
print(pd.DataFrame(lignes, columns=["t_j", "n_j", "n_Aj", "d_j", "départ en A", "E_Aj", "V_j"]).to_string(index=False))
chi5 = (O1 - E1) ** 2 / V1
print(f"O_A = {O1}, E_A = {E1:.3f}, V = {V1:.3f}, chi2 = {chi5:.3f}, p = {stats.chi2.sf(chi5, 1):.3f}")
from statsmodels.duration.survfunc import survdiff
print("statsmodels : chi2 = %.3f, p = %.3f" % survdiff(y5, d5, g5))
```
<!--sortie-->
```text
 t_j  n_j  n_Aj  d_j  départ en A   E_Aj    V_j
 3.0   10     5    1            1 0.5000 0.2500
 5.0    9     4    1            0 0.4444 0.2469
 6.0    8     4    1            1 0.5000 0.2500
 7.0    7     3    1            0 0.4286 0.2449
 9.0    5     2    1            0 0.4000 0.2400
10.0    4     2    1            1 0.5000 0.2500
O_A = 3, E_A = 2.773, V = 1.482, chi2 = 0.035, p = 0.852
statsmodels : chi2 = 0.035, p = 0.852
```

Le groupe A a 3 départs pour 2,77 attendus : $\chi^2\approx0{,}03$, $p\approx0{,}85$. Avec dix clients, on ne peut rien conclure ; c'est tout à fait normal, et c'est la raison pour laquelle on ne compare pas des groupes aussi petits.

**Corrigé 6.** $\mathrm{RMST}_A(24)=6\times1+6\times0{,}8+6\times0{,}5+6\times0{,}3=6+4{,}8+3+1{,}8=15{,}6$ mois ; $\mathrm{RMST}_B(24)=9\times1+6\times0{,}9+6\times0{,}7+3\times0{,}6=9+5{,}4+4{,}2+1{,}8=20{,}4$ mois. La différence est de **4,8 mois** : en moyenne, sur les 24 premiers mois, un client de la campagne B reste 4,8 mois de plus dans la clientèle qu'un client de la campagne A. Contrairement au rapport de risques, cette quantité s'interprète sans hypothèse de proportionnalité et se lit directement en unités de temps (ou, multipliée par la marge mensuelle, en dinars).

```python
tjA, SA = np.array([6, 12, 18.]), np.array([0.8, 0.5, 0.3])
tjB, SB = np.array([9, 15, 21.]), np.array([0.9, 0.7, 0.6])
print("RMST(24) A :", round(rmst(tjA, SA, 24), 2), "| B :", round(rmst(tjB, SB, 24), 2), "| différence :", round(rmst(tjB, SB, 24) - rmst(tjA, SA, 24), 2))
```
<!--sortie-->
```text
RMST(24) A : 15.6 | B : 20.4 | différence : 4.8
```

**Corrigé 7.** (a) $\mathrm{HR}=e^{\hat\beta}$, IC $=e^{\hat\beta\pm1{,}96\,se}$, $z=\hat\beta/se$ : offre $0{,}670$ ($[0{,}590\ ;\ 0{,}761]$, $z=-6{,}15$) ; âge $0{,}986$ ($[0{,}981\ ;\ 0{,}992]$, $z=-4{,}53$) ; Instagram $1{,}887$ ($[1{,}60\ ;\ 2{,}22]$, $z=7{,}56$). (b) $e^{10\times(-0{,}0136)}\approx0{,}873$ : dix ans de plus réduisent le risque d'environ 13 %. (c) Les effets se multiplient : $e^{-0{,}40+0{,}635}=e^{0{,}235}\approx1{,}26$ (le canal Instagram l'emporte sur l'offre). (d) $S(t\mid x)=S_0(t)^{\exp(x^\top\beta)}$ : $0{,}80^{0{,}670}\approx0{,}861$. (e) $\hat\beta=-\hat\gamma/\hat\sigma=-0{,}35/0{,}74\approx-0{,}473$, soit $\mathrm{HR}=e^{-0{,}473}\approx0{,}623$.

```python
b = np.array([-0.40, -0.0136, 0.635]); se_ = np.array([0.065, 0.0030, 0.084])
print(pd.DataFrame({"HR": np.exp(b), "IC bas": np.exp(b - 1.96 * se_), "IC haut": np.exp(b + 1.96 * se_), "z": b / se_}, index=["offre", "age", "Instagram"]).round(3).to_string())
print("+10 ans :", round(np.exp(10 * b[1]), 3), "| Instagram avec offre / Boutique sans offre :", round(np.exp(b[0] + b[2]), 3))
print("S(24) avec offre :", round(0.80 ** np.exp(b[0]), 3), "| HR depuis AFT :", round(np.exp(-0.35 / 0.74), 3))
```
<!--sortie-->
```text
              HR  IC bas  IC haut      z
offre      0.670   0.590    0.761 -6.154
age        0.986   0.981    0.992 -4.533
Instagram  1.887   1.601    2.225  7.560
+10 ans : 0.873 | Instagram avec offre / Boutique sans offre : 1.265
S(24) avec offre : 0.861 | HR depuis AFT : 0.623
```

**Corrigé 8.** Dans l'analyse (a), le cadeau n'est donné qu'à ceux qui ont **survécu** jusqu'au mois 6 : ils ont une avance garantie, et le modèle y voit un effet protecteur qui n'existe pas. Dans l'analyse (b), le cadeau est une variable qui passe de 0 à 1 au mois 6 (deux épisodes pour les clients concernés), et seuls les clients **présents au mois 6** sont comparés entre eux.

```python
from statsmodels.duration.hazard_regression import PHReg

rng = np.random.default_rng(8)
N = 2000
T = rng.exponential(1 / 0.02, N)
C = rng.uniform(18, 48, N)
Y, D = np.minimum(T, C), (T <= C).astype(int)
cadeau = (Y > 6) & (rng.random(N) < 0.5)
naif = PHReg(Y, cadeau.astype(float)[:, None], status=D, ties="efron").fit()
porteurs = np.where(cadeau)[0]
debut = np.concatenate([np.zeros(N), np.full(len(porteurs), 6.0)])
fin = np.concatenate([np.where(cadeau, 6.0, Y), Y[porteurs]])
statut = np.concatenate([np.where(cadeau, 0, D), D[porteurs]])
x_tv = np.concatenate([np.zeros(N), np.ones(len(porteurs))])
juste = PHReg(fin, x_tv[:, None], status=statut, entry=debut, ties="efron").fit()
for nom, m in (("naïve (variable fixe)", naif), ("correcte (dépend du temps)", juste)):
    print(f"{nom:<28} HR = {np.exp(m.params[0]):.2f}  IC95 [{np.exp(m.params[0] - 1.96 * m.bse[0]):.2f} ; {np.exp(m.params[0] + 1.96 * m.bse[0]):.2f}]")
```
<!--sortie-->
```text
naïve (variable fixe)        HR = 0.64  IC95 [0.56 ; 0.74]
correcte (dépend du temps)   HR = 1.00  IC95 [0.86 ; 1.16]
```

L'analyse naïve conclut à un effet protecteur net (un HR bien inférieur à 1), l'analyse correcte à un effet nul (HR proche de 1, intervalle contenant 1) : c'est le **biais d'immortalité**.

**Corrigé 9.** (a) Si $S(t)=\exp[-(t/\sigma)^k]$, alors $\ln(-\ln S)=k\ln t-k\ln\sigma$ : la pente de la droite est $k$. (b) Le maximum de vraisemblance sans covariable est l'estimation de $k=1/\hat\sigma$ dans `ajuster` avec une seule colonne de 1.

```python
c = pd.read_csv("donnees/clients.csv")
y, d = c["duree_mois"].to_numpy(), c["churn"].to_numpy()
tj_, _, _, S_, _ = kaplan_meier(y, d)
garde = (tj_ >= 6) & (tj_ <= 60)
pente, ord_, r, _, _ = stats.linregress(np.log(tj_[garde]), np.log(-np.log(S_[garde])))
mv = ajuster("weibull", y, d, np.ones((len(y), 1)))
print(f"forme par le graphique de Weibull : k = {pente:.3f} (r = {r:.3f}) | forme par maximum de vraisemblance : k = {1 / np.exp(mv['theta'][-1]):.3f}")
```
<!--sortie-->
```text
forme par le graphique de Weibull : k = 1.296 (r = 1.000) | forme par maximum de vraisemblance : k = 1.281
```

Les deux méthodes donnent une forme voisine de 1,3 (1,30 et 1,28) et légèrement inférieure à la vraie valeur 1,35. La raison est celle du 5.4.7 : en **ignorant les covariables** (offre, canal, âge, facteur de service non observé), le risque de la population est un mélange de risques individuels, dont la croissance apparente est plus lente. L'ajout des covariables mesurées dans le modèle du 5.4.3 faisait passer la forme à 1,32, et l'ajout du facteur non observé (modèle « oracle » du 5.4.7) à 1,40 : la vraie valeur (1,35) n'est approchée, à l'erreur d'échantillonnage près, que si l'on tient compte de *toutes* les covariables, y compris celles qu'on ne mesure pas. Les deux méthodes d'estimation (graphique, maximum de vraisemblance) s'accordent entre elles ; c'est le *modèle* qui est incomplet, pas la méthode.

**Corrigé 10.** (a) En $\beta=0$, $e^{\beta x_k}=1$ : la moyenne pondérée de $x$ dans l'ensemble à risque $R_j$ est la proportion $n_{1j}/n_j$ de clients du groupe 1. Le score est $\sum_j\sum_{i\text{ parti en }t_j}\big(x_i-n_{1j}/n_j\big)=\sum_j\big(d_{1j}-d_j\,n_{1j}/n_j\big)=O_1-E_1$. (b) L'information en $\beta=0$ est $\sum_{i}\mathrm{Var}_{R_i}(x)=\sum_i\frac{n_{1}}{n}(1-\frac{n_{1}}{n})$ (somme sur *chaque* départ), alors que le log-rank utilise la variance hypergéométrique, avec le facteur $\frac{n_j-d_j}{n_j-1}$ qui corrige les départs simultanés. Les deux coïncident exactement quand il n'y a **jamais** d'ex aequo.

```python
off = c["offre_bienvenue"].to_numpy().astype(float)
U0, I0 = score_info(0.0, y, d, off)                       # fonction du 5.3.2 : boucle sur chaque départ (ex aequo à la Breslow)
O, E, chi_lr, _, _ = logrank(y, d, off)
print(f"Cox : score U = {U0:.3f}, information I = {I0:.3f}, U²/I = {U0 ** 2 / I0:.3f}")
print(f"log-rank : O1 - E1 = {O[1] - E[1]:.3f}, chi2 = {chi_lr:.3f}")
```
<!--sortie-->
```text
Cox : score U = -92.383, information I = 240.231, U²/I = 35.527
log-rank : O1 - E1 = -92.383, chi2 = 35.535
```

Le score est exactement $O_1-E_1$ (même valeur, signe compris, puisque $x=1$ désigne le groupe avec offre), et les deux statistiques ne diffèrent que de 0,008 sur 35,5 : la différence vient de la correction des ex aequo dans la variance.

**Corrigé 11.** Le gain actualisé de l'offre vaut $\Delta=\sum_t(S_1(t)-S_0(t))(1+r)^{-t}$ « mois de présence actualisés » ; l'offre est rentable si $m\,\Delta>25$, c'est-à-dire $m>m^\star=25/\Delta$.

```python
cout = 25.0
for r in (0.01, 0.02):
    v = (1 + r) ** (-mois)                                # `mois`, S0 et S1 viennent du 5.4.5
    delta = np.sum((S1 - S0) * v)
    print(f"taux {100 * r:.0f} %/mois : gain en mois de présence actualisés = {delta:.3f} -> marge de rentabilité m* = {cout / delta:.2f} DT/mois")
```
<!--sortie-->
```text
taux 1 %/mois : gain en mois de présence actualisés = 6.663 -> marge de rentabilité m* = 3.75 DT/mois
taux 2 %/mois : gain en mois de présence actualisés = 4.124 -> marge de rentabilité m* = 6.06 DT/mois
```

Avec une actualisation de 1 % par mois, l'offre devient rentable dès que la marge mensuelle par client actif dépasse environ **3,75 DT** ; avec 2 %, il faut environ **6 DT**. L'offre est donc beaucoup moins coûteuse à justifier si la marge est élevée : c'est la lecture pratique du tableau de sensibilité du 5.4.5.

**Corrigé 12.** Instants de sortie : 1, 2, 3, 5, 6, 9 (les censures aux mois 4 et 7 réduisent seulement les ensembles à risque). Aux mois 1 ($n=8$) : $d_1=1$ ; 2 ($n=7$) : $d_2=1$ ; 3 ($n=6$) : $d_1=1$ ; 5 ($n=4$) : $d_2=1$ ; 6 ($n=3$) : $d_1=1$ ; 9 ($n=1$) : $d_2=1$. On applique $\hat F_k(t)=\sum\hat S(t_j^-)\,d_{kj}/n_j$.

```python
y12 = np.array([1, 2, 3, 4, 5, 6, 7, 9.]); c12 = np.array([1, 2, 1, 0, 2, 1, 0, 2])
tj12, S12, (F1_12, F2_12) = incidence_cumulee(y12, c12)
print(pd.DataFrame({"t_j": tj12, "S": S12, "F1": F1_12, "F2": F2_12, "S + F1 + F2": S12 + F1_12 + F2_12}).round(4).to_string(index=False))
tj_n12, S_n12, (F1_naif12,) = incidence_cumulee(y12, np.where(c12 == 1, 1, 0))
print("1 - KM (cause 2 traitée comme censure), aux instants de la cause 1 :", (1 - S_n12).round(4), "| F1 correcte au dernier instant de cause 1 :", round(F1_12[-2], 4))
```
<!--sortie-->
```text
 t_j      S     F1     F2  S + F1 + F2
 1.0 0.8750 0.1250 0.0000          1.0
 2.0 0.7500 0.1250 0.1250          1.0
 3.0 0.6250 0.2500 0.1250          1.0
 5.0 0.4688 0.2500 0.2812          1.0
 6.0 0.3125 0.4062 0.2812          1.0
 9.0 0.0000 0.4062 0.5938          1.0
1 - KM (cause 2 traitée comme censure), aux instants de la cause 1 : [0.125  0.2708 0.5139] | F1 correcte au dernier instant de cause 1 : 0.4062
```

La somme $\hat S+\hat F_1+\hat F_2$ vaut 1 à chaque instant. À 6 mois, la probabilité de départ volontaire est $\hat F_1(6)=0{,}406$ ; en traitant la cause 2 comme une censure, on obtiendrait « $1-\mathrm{KM}$ » $=0{,}514$, soit 11 points de trop : la compétition des fermetures forcées (aux mois 2, 5 et 9) est ignorée.

**Corrigé 13.** On applique `test_ph` à l'ajustement de Cox des données de Rossi (la fonction `cox_ph` du 5.3.3 accepte n'importe quelle matrice de covariables).

```python
from lifelines.datasets import load_rossi

rossi = load_rossi()
Xr = rossi.drop(columns=["week", "arrest"])
fit_r = cox_ph(rossi["week"].to_numpy(), rossi["arrest"].to_numpy(), Xr.to_numpy())
chi_r, chi_glob_r = test_ph(rossi["week"].to_numpy(), rossi["arrest"].to_numpy(), Xr.to_numpy(), fit_r)
out = pd.DataFrame({"HR (Breslow)": np.exp(fit_r["beta"]), "chi2 PH": chi_r, "p": stats.chi2.sf(chi_r, 1)}, index=Xr.columns)
print(out.round(3).to_string())
print(f"test global : chi2 = {chi_glob_r:.2f} (7 ddl), p = {stats.chi2.sf(chi_glob_r, 7):.3f}")
```
<!--sortie-->
```text
      HR (Breslow)  chi2 PH      p
fin          0.685    1.371  0.242
age          0.944    0.893  0.345
race         1.369    2.245  0.134
wexp         0.860    4.128  0.042
mar          0.649    0.089  0.765
paro         0.919    0.021  0.886
prio         1.095    1.618  0.203
test global : chi2 = 10.93 (7 ddl), p = 0.142
```

La proportionnalité est plausible pour six des sept covariables. Seule l'expérience professionnelle (`wexp`) a une p-valeur inférieure à 0,05 ($p=0{,}042$), et le test **global** ne rejette rien ($p=0{,}14$). Avec sept tests, obtenir une p-valeur à 0,04 arrive souvent par hasard (volume I, section 3.5.5) : ce n'est pas une preuve de violation. La démarche prudente : tracer le graphique log-log de `wexp`, et si un doute subsiste, **stratifier** sur cette variable (elle est binaire) ou ajouter un effet qui dépend du temps, puis voir si les autres coefficients, en particulier celui de l'aide financière, bougent. S'ils ne bougent pas, la conclusion principale est robuste.

---

## Bilan du chapitre 5

Vous savez maintenant :

- **reconnaître la censure** et expliquer pourquoi la moyenne des durées, la moyenne des seuls événements et la proportion d'événements sont toutes **biaisées** ; distinguer censure à droite, à gauche, par intervalle et **troncature** (entrée tardive) ; énoncer l'hypothèse de **censure non informative** ;
- manier les trois fonctions d'une durée, **survie** $S(t)$, **risque instantané** $h(t)$ et **risque cumulé** $H(t)$, reliées par $S=e^{-H}$, et la formule $E[T]=\int_0^\infty S(t)\,dt$ ;
- écrire la **vraisemblance avec censure** $\ell=\sum[\delta_i\ln h(y_i)-H(y_i)]$ et en tirer le taux constant $\hat\lambda=D/\sum y_i$ ;
- calculer l'**estimateur de Kaplan-Meier** à la main et par code, ses intervalles de confiance (**Greenwood**, log-log), la **médiane** et la **durée moyenne restreinte** ; comparer des groupes par le **log-rank** et ses variantes ;
- ajuster et interpréter un **modèle de Cox** : vraisemblance partielle, rapports de risques, **ex aequo** (Breslow, Efron), **vérification de la proportionnalité** (graphique log-log, test de score de Grambsch-Therneau), **covariables dépendant du temps** et **biais d'immortalité**, courbes de survie prédites, **indice de concordance** ;
- ajuster des **modèles paramétriques** (Weibull, log-normal, log-logistique) par maximum de vraisemblance, lire un **facteur d'accélération**, passer de l'AFT aux risques proportionnels ($\beta=-\gamma/\sigma$ pour la Weibull), choisir par l'**AIC** et les **résidus de Cox-Snell**, **extrapoler** et calculer une **valeur vie client** avec une analyse de sensibilité ;
- (en option) traiter des **risques concurrents** : incidences cumulées d'**Aalen-Johansen**, pourquoi « 1 − KM » est faux, **modèle par cause** contre **Fine et Gray**.

Deux messages à garder en mémoire. **Un chiffre de survie n'a de sens qu'avec son traitement de la censure et ses hypothèses** (non informative, proportionnalité, forme de la loi) : on les énonce, on les vérifie quand c'est possible, on mesure leur influence sinon. Et **la randomisation reste l'arme la plus solide** : l'offre de bienvenue a un effet causal mesurable parce qu'elle a été attribuée au hasard ; pour les variables non randomisées (le canal, l'âge), les résultats sont des **associations**.

Le chapitre 6 change de perspective : au lieu de chercher *une* estimation et son incertitude, la **statistique bayésienne** attribue une **loi de probabilité** aux paramètres eux-mêmes, et la **simulation** (Monte-Carlo, MCMC) permet de calculer ce que l'algèbre ne sait pas faire.
