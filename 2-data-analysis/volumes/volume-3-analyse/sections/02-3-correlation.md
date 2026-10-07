## 2.3 Analyse de corrélation

Un test A/B n'est pas toujours possible : on ne peut pas tirer au sort la météo, la saison ou les clients qui s'inscrivent un mois donné. Il reste alors à **observer** et à mesurer des **liaisons** entre variables : c'est la corrélation. Elle est précieuse pour explorer, pour prévoir, pour formuler des hypothèses ; elle est dangereuse dès qu'on la lit comme une cause. Cette section donne les trois coefficients, leurs limites, et trois exemples de la boutique où une corrélation élevée trompe.

### 2.3.1 Mesurer une liaison : Pearson, Spearman, Kendall

La gérante demande : « Plus je dépense en publicité, plus je reçois de commandes, non ? » Prenons les 1 096 jours de la boutique, avec la dépense publicitaire quotidienne et le nombre de commandes du jour. Trois coefficients mesurent la liaison, chacun à sa façon.

- Le coefficient de **Pearson** $r$ mesure la liaison **linéaire** : il vaut +1 si les points sont exactement alignés sur une droite croissante, −1 sur une droite décroissante, 0 s'il n'y a aucune tendance linéaire. Il est sensible aux valeurs extrêmes.
- Le coefficient de **Spearman** est le Pearson calculé sur les **rangs** (on remplace chaque valeur par son numéro d'ordre) : il mesure une liaison **monotone**, pas forcément linéaire, et résiste aux valeurs extrêmes.
- Le coefficient de **Kendall** ($\tau$) compare des **paires** d'observations : c'est la différence entre la part de paires qui vont dans le même sens (quand la dépense monte, les commandes montent) et la part des paires qui vont en sens contraire. Il est plus petit en valeur que les deux autres, mais plus robuste pour de petits échantillons.

```python
x, y = jours["depense_pub"], jours["nb_commandes"]
print("Pearson :", round(stats.pearsonr(x, y)[0], 3), "| Spearman :", round(stats.spearmanr(x, y)[0], 3), "| Kendall :", round(stats.kendalltau(x, y)[0], 3))
```
<!--sortie-->
```text
Pearson : 0.529 | Spearman : 0.384 | Kendall : 0.265
```

Pearson vaut 0,53, Spearman 0,38 et Kendall 0,27. Les trois sont positifs : les jours de forte dépense sont, en moyenne, des jours de plus de commandes. L'écart entre Pearson et Spearman signale que la liaison n'est pas une belle droite : quelques jours extrêmes pèsent dans Pearson (les jours de fin d'année, où la dépense et les commandes sont toutes deux très élevées). La valeur de Kendall, plus faible, n'indique pas une liaison plus faible : elle suit simplement une échelle différente (ne comparez pas le $\tau$ à un $r$).

> 💡 **Intuition.** Un coefficient de corrélation résume un nuage de points en un seul nombre. Ce nombre cache la forme du nuage : **regardez toujours le nuage** (volume I, section 1.4.2).

### 2.3.2 Toujours regarder le nuage, et se méfier d'un point

Un seul point peut fabriquer une corrélation. Prenons les trente premiers jours, où la liaison entre dépense et commandes est faible, et ajoutons-y **un jour aberrant** (une dépense de 900 € et 150 commandes, par exemple une erreur de saisie).

```python
x30, y30 = jours["depense_pub"].values[:30], jours["nb_commandes"].values[:30]
x31, y31 = np.r_[x30, 900], np.r_[y30, 150]
print("30 jours : Pearson", round(np.corrcoef(x30, y30)[0, 1], 2), "| avec le jour aberrant :", round(np.corrcoef(x31, y31)[0, 1], 2), "| Spearman :", round(stats.spearmanr(x31, y31)[0], 2))
```
<!--sortie-->
```text
30 jours : Pearson 0.23 | avec le jour aberrant : 0.89 | Spearman : 0.25
```

Un seul point fait passer le Pearson de **0,23 à 0,89** ; le Spearman, lui, reste à **0,25**. C'est la raison pour laquelle on calcule les deux : un grand écart entre eux est un signal d'alarme.

```python hide
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.3))
j = jours.copy()
mois_nom = j["date"].dt.month
ax = axes[0]
sc = ax.scatter(j["depense_pub"], j["nb_commandes"], c=mois_nom, cmap="viridis", s=7, alpha=0.7)
ax.set_xlabel("Dépense publicitaire du jour (€)"); ax.set_ylabel("Commandes du jour"); ax.set_title("Jours bruts : r = %.2f" % np.corrcoef(j["depense_pub"], j["nb_commandes"])[0, 1], loc="left", fontsize=10)
cb = fig.colorbar(sc, ax=ax, ticks=[1, 6, 12]); cb.set_label("mois", fontsize=8)
dmx = j["depense_pub"] - j.groupby("mois")["depense_pub"].transform("mean"); dmy = j["nb_commandes"] - j.groupby("mois")["nb_commandes"].transform("mean")
ax = axes[1]
ax.scatter(dmx, dmy, s=7, alpha=0.5, color=BLEU)
ax.set_xlabel("Dépense, écart à la moyenne du mois (€)"); ax.set_ylabel("Commandes, écart à la moyenne du mois"); ax.set_title("À mois égal : r = %.2f" % np.corrcoef(dmx, dmy)[0, 1], loc="left", fontsize=10)
fig.tight_layout(); fig.savefig("figures/ch02-pub-mois.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

![À gauche : dépense publicitaire et commandes de chaque jour, colorées selon le mois (corrélation 0,53) ; à droite : les mêmes jours après retrait de la moyenne de leur mois (corrélation 0,11).](figures/ch02-pub-mois.png)

### 2.3.3 Significativité d'une corrélation, intervalle de confiance

Un coefficient calculé sur un échantillon est une **estimation** : il porte une incertitude, comme une moyenne. Deux outils la mesurent.

- Le **test de nullité** demande si une corrélation de cette taille pourrait venir d'une population où la vraie corrélation est nulle. Sa p-valeur dépend surtout de $n$ : avec 1 096 jours, une corrélation de **0,06 seulement** suffirait pour passer sous 0,05.
- L'**intervalle de confiance** se calcule par la **transformation de Fisher** : $z=\operatorname{arctanh}(r)$, qui suit à peu près une loi normale d'écart-type $1/\sqrt{n-3}$ ; on calcule l'intervalle de $z$, puis on revient à l'échelle de $r$ par $\tanh$.

```python
r, p = stats.pearsonr(x, y)
n = len(x)
z = np.arctanh(r); se = 1 / np.sqrt(n - 3)
ic = np.tanh([z - 1.96 * se, z + 1.96 * se])
r_min = np.tanh(1.96 * se)                                   # plus petite corrélation significative à 5 % avec ce n
print("r =", round(r, 3), "| IC à 95 % :", ic.round(3), "| p =", f"{p:.0e}", "| plus petit r significatif :", round(r_min, 3))
```
<!--sortie-->
```text
r = 0.529 | IC à 95 % : [0.485 0.57 ] | p = 6e-80 | plus petit r significatif : 0.059
```

La corrélation de 0,53 a un intervalle de confiance de **0,49 à 0,57** : elle est donc **bien mesurée** (c'est une vraie liaison dans les données). Mais *significative* ne veut pas dire *causale* ni même *importante* : dès que $n$ est grand, une corrélation minuscule est significative (ici, à partir de 0,06). La question utile est : « *qu'est-ce qui produit cette liaison ?* »

### 2.3.4 Corrélation et confusion : la publicité, la saison, la température

Le chiffre de 0,53 laisse penser que la publicité fait vendre. Mais la dépense publicitaire est **plus forte en novembre-décembre et au printemps**, et c'est aussi en novembre-décembre que les clients commandent le plus. La **saison** pousse les deux variables dans le même sens : c'est une **variable de confusion** (volume I, section 1.4.3). Pour la neutraliser, on compare des jours **du même mois** : on retire à chaque jour la moyenne de son mois, pour la dépense comme pour les commandes.

```python
mois = jours["mois"]
dx = jours["depense_pub"] - jours.groupby("mois")["depense_pub"].transform("mean")
dy = jours["nb_commandes"] - jours.groupby("mois")["nb_commandes"].transform("mean")
print("corrélation brute :", round(np.corrcoef(jours["depense_pub"], jours["nb_commandes"])[0, 1], 2), "| à mois égal :", round(np.corrcoef(dx, dy)[0, 1], 2))
```
<!--sortie-->
```text
corrélation brute : 0.53 | à mois égal : 0.11
```

À mois égal, la corrélation tombe de **0,53 à 0,11**. Une grande partie de la liaison venait de la saison. Il reste un peu de liaison : est-elle réelle ? Une **régression** permet de contrôler plusieurs facteurs à la fois (le mois, le jour de la semaine, la promotion) et de lire l'effet de la dépense « toutes choses égales par ailleurs » (le chapitre 3 y revient en détail).

```python
import statsmodels.formula.api as smf
m = smf.ols("nb_commandes ~ depense_pub + promo_active + C(mois) + C(jour_semaine)", data=jours).fit()
b, s, pv = m.params["depense_pub"], m.bse["depense_pub"], m.pvalues["depense_pub"]
print("commandes par euro de dépense quotidienne :", round(b, 4), "| IC à 95 % :", (b - 1.96 * s).round(4), "à", (b + 1.96 * s).round(4), "| p =", round(pv, 3))
```
<!--sortie-->
```text
commandes par euro de dépense quotidienne : 0.006 | IC à 95 % : -0.0004 à 0.0124 | p = 0.067
```

Avec le mois, le jour de la semaine et la promotion contrôlés, chaque euro de dépense quotidienne supplémentaire est associé à **0,006 commande** de plus par jour, mais l'intervalle (de −0,0004 à +0,0124) contient zéro (p = 0,067) : on ne peut pas conclure.

**La vérité programmée** : l'effet réel de la publicité est de **+1,5 % de commandes pour 1 000 € de dépense hebdomadaire supplémentaire**, soit environ 0,0035 commande par jour et par euro de dépense quotidienne : une valeur **dans l'intervalle**, que l'analyse ne peut ni confirmer ni exclure. L'effet est petit, et le bruit des journées est grand : la corrélation brute de **0,53** était donc hors de proportion avec l'effet réel : elle mesurait surtout la saison.

```python hide
cmd_j = jours["nb_commandes"].mean()
vrai_par_euro = 0.015 * cmd_j / (1000 / 7)
print("commandes moyennes par jour :", round(cmd_j, 1), "| effet programmé (commandes par € de dépense quotidienne) :", round(vrai_par_euro, 4))
```
<!--sortie-->
```text
commandes moyennes par jour : 33.2 | effet programmé (commandes par € de dépense quotidienne) : 0.0035
```

Un deuxième exemple, plus net : **la température et les ventes de jardin**. Le jour où il fait chaud, la boutique vend beaucoup d'articles de jardin ; la corrélation est forte.

```python
jar = lig.merge(cmd[["id_commande", "date_commande"]], on="id_commande").merge(prod[["id_produit", "categorie"]], on="id_produit")
par_jour = jar.groupby("date_commande").apply(lambda g: pd.Series({"jardin": g.loc[g["categorie"] == "Jardin", "quantite"].sum(), "total": g["quantite"].sum()}))
j2 = jours.assign(cle=jours["date"].dt.strftime("%Y-%m-%d")).set_index("cle").join(par_jour).fillna(0)
j2["part_jardin"] = j2["jardin"] / j2["total"].replace(0, np.nan)
dt_ = j2["temperature_moy"] - j2.groupby("mois")["temperature_moy"].transform("mean")
dp_ = j2["part_jardin"] - j2.groupby("mois")["part_jardin"].transform("mean")
print("température × articles de jardin vendus :", round(j2[["temperature_moy", "jardin"]].corr().iloc[0, 1], 2), "| × part du jardin :", round(j2[["temperature_moy", "part_jardin"]].corr().iloc[0, 1], 2), "| à mois égal :", round(np.corrcoef(dt_[dp_.notna()], dp_.dropna())[0, 1], 2))
```
<!--sortie-->
```text
température × articles de jardin vendus : 0.68 | × part du jardin : 0.83 | à mois égal : 0.03
```

La température est corrélée à **0,68** avec le nombre d'articles de jardin vendus et à **0,83** avec leur part dans les ventes ; mais **à mois égal**, la corrélation avec la part tombe à **0,03**. La **vérité programmée** : la part du jardin dépend de la **saison** (de la température moyenne du mois), pas de la température du jour. La corrélation de 0,83 était entièrement due au calendrier.

> ⚠️ **Piège.** Quand deux variables ont une **cause commune** (ici, la saison), elles sont corrélées sans que l'une agisse sur l'autre. Les quatre questions à poser devant une corrélation : *y a-t-il une troisième variable qui les pousse toutes les deux ? Une tendance dans le temps ? Un effet de sélection ? Le sens de la cause pourrait-il être inverse ?*

### 2.3.5 Les séries temporelles : la tendance commune

Les corrélations entre **séries temporelles** sont les plus trompeuses, parce que deux séries qui **dérivent** dans le même sens (ou dans des sens opposés) sont corrélées même si elles n'ont rien à voir. Une simulation convainc mieux qu'un argument : on tire deux **marches aléatoires** indépendantes de 36 points (36 mois, par exemple), c'est-à-dire des séries obtenues en cumulant des bruits sans lien entre eux.

```python
def deux_marches(graine):
    r = np.random.default_rng(graine).normal(size=(2, 36)).cumsum(axis=1)
    return np.corrcoef(r)[0, 1], np.corrcoef(np.diff(r))[0, 1]
paires = np.array([deux_marches(g) for g in range(2000)])
print("deux séries indépendantes, 1re paire : r =", round(paires[0, 0], 2), "| sur les variations :", round(paires[0, 1], 2))
print("paires avec |r| > 0,5 : séries brutes", round((np.abs(paires[:, 0]) > 0.5).mean(), 2), "| variations", round((np.abs(paires[:, 1]) > 0.5).mean(), 3))
```
<!--sortie-->
```text
deux séries indépendantes, 1re paire : r = -0.83 | sur les variations : -0.08
paires avec |r| > 0,5 : séries brutes 0.41 | variations 0.001
```

Sur 2 000 paires de séries **sans aucun lien**, **41 %** ont une corrélation de plus de 0,5 en valeur absolue (en positif ou en négatif) : un chiffre que l'on aurait pris pour un résultat. Si l'on corrèle plutôt les **variations d'un mois à l'autre** (les différences), ce pourcentage tombe à presque rien. C'est le remède : **différencier** les séries, ou travailler à tendance et saisonnalité retirées (chapitre 5).

```python hide
r = np.random.default_rng(3).normal(size=(2, 36)).cumsum(axis=1)
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.1))
axes[0].plot(r[0], color=BLEU, label="série 1"); axes[0].plot(r[1], color=ORANGE, label="série 2")
axes[0].set_xlabel("Mois"); axes[0].set_title("Deux séries sans aucun lien", loc="left", fontsize=10); axes[0].legend(frameon=False, fontsize=8)
axes[1].scatter(r[0], r[1], color=BLEU, s=14); axes[1].set_xlabel("série 1"); axes[1].set_ylabel("série 2")
axes[1].set_title("… et pourtant r = %.2f" % np.corrcoef(r)[0, 1], loc="left", fontsize=10)
fig.tight_layout(); fig.savefig("figures/ch02-marches.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

![À gauche : deux marches aléatoires indépendantes de 36 mois ; à droite : leur nuage de points, avec une corrélation de −0,72.](figures/ch02-marches.png)

Un exemple réel, plus modeste : le **nombre de clients inscrits cumulé** et les **commandes mensuelles** (2023 à 2025) progressent tous deux avec le temps.

```python
cm = cmd.assign(m=pd.to_datetime(cmd["date_commande"]).dt.to_period("M")).groupby("m").size()
cl = pd.read_csv("donnees/clients.csv", parse_dates=["date_inscription"])
cumul = cl.assign(m=cl["date_inscription"].dt.to_period("M")).groupby("m").size().cumsum().reindex(cm.index, method="ffill")
print("corrélation des niveaux :", round(np.corrcoef(cumul.values, cm.values)[0, 1], 2), "| des variations mensuelles :", round(np.corrcoef(np.diff(cumul.values), np.diff(cm.values))[0, 1], 2))
```
<!--sortie-->
```text
corrélation des niveaux : 0.41 | des variations mensuelles : -0.11
```

La corrélation des niveaux (0,41) disparaît (−0,11) quand on regarde les variations : les deux séries montent, sans que les inscriptions expliquent les commandes mois par mois.

### 2.3.6 De la corrélation à la causalité

Une corrélation observée entre A et B peut avoir quatre explications : **A cause B**, **B cause A**, une **troisième variable** cause les deux (la saison), ou le **hasard**. Distinguer ces possibilités demande plus que de calculer un coefficient. Par ordre de force croissante, on peut :

1. **Contrôler** les facteurs connus (comparer à mois égal, à jour de semaine égal, par régression) : c'est ce que nous venons de faire, et cela réduit la confusion sans l'éliminer, parce que l'on ne contrôle que ce que l'on a mesuré.
2. **Exploiter une expérience naturelle** : un événement qui modifie A sans toucher B directement (une panne de site, une promotion décidée pour d'autres raisons).
3. **Faire une expérience** (un test A/B, section 2.2) : le tirage au sort est le seul moyen de rompre toutes les causes communes à la fois.

La promotion en donne un dernier exemple. **La vérité programmée** : les jours de promotion, la boutique reçoit **18 % de commandes de plus**. Pourtant, la corrélation brute entre promotion et chiffre d'affaires est de **−0,01** : presque nulle. Les promotions ont lieu en janvier et en été, saisons creuses ; et elles baissent les prix de 20 % : le chiffre d'affaires par commande diminue. La saison cache l'effet. En contrôlant le mois et le jour de la semaine :

```python
mp = smf.ols("np.log(nb_commandes) ~ promo_active + depense_pub + C(mois) + C(jour_semaine)", data=jours).fit()
print("corrélation brute promotion × CA :", round(jours[["promo_active", "chiffre_affaires"]].corr().iloc[0, 1], 2), "| effet estimé sur les commandes :", f"{np.exp(mp.params['promo_active']) - 1:+.1%}")
```
<!--sortie-->
```text
corrélation brute promotion × CA : -0.01 | effet estimé sur les commandes : +18.7%
```

Une fois le calendrier contrôlé, l'effet estimé est de **+19 % de commandes** (voisin des +18 % programmés), alors que la corrélation brute était trompeuse. La régression a retrouvé un effet que la corrélation cachait ; mais cela n'a marché que parce que **nous savions quoi contrôler**.

> ✅ **À retenir.** Une corrélation dit que deux variables varient ensemble ; elle ne dit pas pourquoi. Avant de lui donner un sens : regardez le nuage, comparez à tendance et saison égales, calculez un intervalle de confiance, et, pour décider d'agir, **testez** (section 2.2). Une corrélation forte est un point de départ pour une expérience, pas un point d'arrivée.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.5 et 2.6, exercices 2.9 à 2.11.
