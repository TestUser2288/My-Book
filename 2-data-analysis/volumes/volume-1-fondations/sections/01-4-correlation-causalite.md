## 1.4 Corrélation et causalité

Voici la question qui revient dans toutes les entreprises : « Les jours où nous dépensons plus en publicité, nous vendons plus. La publicité marche, non ? » La première moitié de la phrase est un constat sur les données (une **corrélation**) ; la seconde est une **affirmation sur le monde** (une **causalité**). On passe de l'une à l'autre bien plus vite qu'on ne le devrait. Cette section apprend à mesurer une liaison, à la lire correctement, puis à se demander ce qui la produit.

### 1.4.1 Mesurer une liaison : covariance et corrélation

Pour deux grandeurs mesurées sur les mêmes jours (la dépense publicitaire $x$ et le nombre de commandes $y$), la **covariance** moyenne les produits des écarts à la moyenne :

$$\text{cov}(x,y)=\frac{1}{n-1}\sum_{i=1}^{n}(x_i-\bar x)(y_i-\bar y).$$

Elle est positive quand $x$ et $y$ sont **ensemble** au-dessus ou au-dessous de leur moyenne, négative quand l'un est haut quand l'autre est bas. Mais son échelle dépend des unités (euros × commandes). On la divise donc par les deux écarts-types pour obtenir le **coefficient de corrélation de Pearson**, sans unité, compris entre $-1$ et $+1$ :

$$r=\frac{\text{cov}(x,y)}{s_x\,s_y}=\frac{\sum(x_i-\bar x)(y_i-\bar y)}{\sqrt{\sum(x_i-\bar x)^2\;\sum(y_i-\bar y)^2}}.$$

$r=+1$ : les points sont exactement alignés sur une droite croissante ; $r=-1$ : sur une droite décroissante ; $r=0$ : aucune **liaison linéaire**. Le carré $r^2$ s'interprète comme la part de la variation de $y$ « partagée » avec celle de $x$ le long de la droite.

**À la main sur six jours.** Prenons les six premiers jours de novembre 2025 à partir du lundi 3 : dépense publicitaire (en euros arrondis) et nombre de commandes.

| Jour | $x$ (pub, €) | $y$ (commandes) | $x-\bar x$ | $y-\bar y$ | produit |
|---|---:|---:|---:|---:|---:|
| 1 | 242 | 32 | −153,2 | −14,3 | 2 195,4 |
| 2 | 358 | 45 | −37,2 | −1,3 | 49,6 |
| 3 | 374 | 32 | −21,2 | −14,3 | 303,4 |
| 4 | 583 | 41 | 187,8 | −5,3 | −1 001,8 |
| 5 | 325 | 58 | −70,2 | 11,7 | −818,6 |
| 6 | 489 | 70 | 93,8 | 23,7 | 2 220,7 |
| **Somme** | | | 0 | 0 | **2 948,7** |

Avec $\bar x=395{,}2$ €, $\bar y=46{,}3$, $\sum(x-\bar x)^2=74\,298{,}8$ et $\sum(y-\bar y)^2=1\,137{,}3$ :

$$r=\frac{2\,948{,}7}{\sqrt{74\,298{,}8\times1\,137{,}3}}=\frac{2\,948{,}7}{9\,192{,}4}\approx0{,}32.$$

Une corrélation modérée et positive. Mais **six jours, c'est très peu**. En prenant d'autres semaines de six jours, on obtient des coefficients de -0,81, -0,24, 0,32 et 0,45 : de fortement négatif à modérément positif, pour la **même** relation sous-jacente. Un coefficient de corrélation calculé sur peu d'observations est **très instable** ; l'intervalle de confiance de la section 1.3 s'applique aussi à $r$.

```python hide
xs6 = np.array([242, 358, 374, 583, 325, 489.]); ys6 = np.array([32, 45, 32, 41, 58, 70.])
dx6, dy6 = xs6 - xs6.mean(), ys6 - ys6.mean()
chk = jours[jours["date"] >= "2025-11-03"].head(6)
assert np.allclose(chk["depense_pub"].round(0).values, xs6) and (chk["nb_commandes"].values == ys6).all()
assert round((dx6 * dy6).sum(), 1) == 2948.7 and round((dx6 ** 2).sum(), 1) == 74298.8 and round((dy6 ** 2).sum(), 1) == 1137.3
assert round(np.corrcoef(xs6, ys6)[0, 1], 2) == 0.32
rs = []
for deb in ("2025-03-10", "2025-06-02", "2025-09-15", "2025-11-03"):
    w = jours[jours["date"] >= deb].head(6)
    rs.append(np.corrcoef(w["depense_pub"], w["nb_commandes"])[0, 1])
NUM("r6_min", min(rs)); NUM("r6_max", max(rs))
NUM("r6_a", sorted(rs)[1]); NUM("r6_b", sorted(rs)[2])
```
<!--sortie-->
```text
NUM r6_min -0.8082914314683223
NUM r6_max 0.44517493122368657
NUM r6_a -0.23998599781895685
NUM r6_b 0.3219213746915459
```

Le coefficient de Pearson mesure une relation **linéaire**. Quand la relation est monotone sans être linéaire, ou en présence de valeurs extrêmes, on préfère le coefficient de **Spearman**, qui n'est autre que le coefficient de Pearson calculé sur les **rangs** (on remplace chaque valeur par sa position dans l'ordre croissant) : il ne dépend que de l'ordre, pas de l'échelle, et résiste aux valeurs aberrantes.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : exercice 1.11.

### 1.4.2 Toujours regarder le nuage de points

Un seul nombre ne peut pas résumer une relation. L'exemple classique est celui du statisticien Francis Anscombe (1973) : **quatre jeux de onze points** qui ont exactement les mêmes moyennes, les mêmes variances et **le même coefficient de corrélation** ($r=0{,}816$), mais des formes très différentes.

```python hide
ax1 = np.array([10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5.])
ay = [np.array([8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68]),
      np.array([9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74]),
      np.array([7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73]),
      np.array([6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89])]
ax4 = np.array([8, 8, 8, 8, 8, 8, 8, 19, 8, 8, 8.])
xx = [ax1, ax1, ax1, ax4]
rr = [np.corrcoef(a, b)[0, 1] for a, b in zip(xx, ay)]
assert all(abs(v - 0.816) < 0.001 for v in rr)
NUM("r_anscombe", rr[0])
fig, axs = plt.subplots(1, 4, figsize=(11.5, 2.9), sharex=True, sharey=True)
for k, (ax, a, b) in enumerate(zip(axs, xx, ay)):
    ax.plot(a, b, "o", color=BLEU, ms=5)
    pente, ordo = np.polyfit(a, b, 1)
    gx = np.array([3, 20]); ax.plot(gx, pente * gx + ordo, color=ORANGE, lw=1.6)
    ax.set_title(["A : relation linéaire", "B : courbe", "C : un point isolé", "D : un seul point décide"][k], fontsize=9.5)
    ax.set_xlim(2, 20); ax.set_ylim(2, 14)
style.save(fig, "ch01-anscombe.png")
```
<!--sortie-->
```text
NUM r_anscombe 0.81642051634484
figure : ch01-anscombe.png
```

![Les quatre jeux d'Anscombe : mêmes moyennes, mêmes écarts-types, même droite de régression et même corrélation (0,816). A : une vraie relation linéaire. B : une relation courbe, que la droite décrit mal. C : une relation parfaitement linéaire, déformée par un point isolé. D : aucune relation, sauf un point extrême qui, à lui seul, crée la corrélation.](figures/ch01-anscombe.png)

Dans le jeu B, la relation est **parfaite mais courbe** ; dans C, un seul point isolé fait baisser un alignement parfait ; dans D, il n'y a **aucune** relation, hormis un point extrême qui fabrique la corrélation à lui seul. Le coefficient $r$ est **aveugle** à ces différences. Les règles qui en découlent :

- **Dessinez toujours** le nuage de points avant de calculer $r$.
- Un $r$ proche de 0 n'implique pas l'**absence** de relation, seulement l'absence de relation *linéaire* (une relation en U donne $r\approx0$).
- Un $r$ élevé peut être l'œuvre d'un **seul point** : retirez-le pour voir.
- Le $r$ calculé sur des **moyennes** (par mois, par ville) est généralement plus fort que celui calculé sur les individus, car la moyenne gomme le bruit : c'est l'**erreur écologique** quand on en tire des conclusions sur des individus.

### 1.4.3 La publicité et les ventes : une corrélation trompeuse

Revenons à la gérante. Sur les 1 096 jours de la boutique, la corrélation de Pearson entre la **dépense publicitaire du jour** et le **chiffre d'affaires du jour** vaut **0,42** (Spearman : 0,29). C'est une liaison positive franche. Regardons le nuage.

```python hide
import statsmodels.formula.api as smf
jj = jours.copy()
jj["pub7k"] = jj["depense_pub"].rolling(7, min_periods=1).sum() / 1000
jj["pluvieux"] = (jj["pluie_mm"] > 1).astype(int)
jj["t"] = np.arange(len(jj)) / 365.25
jj["lc"] = np.log(jj["nb_commandes"])
n_jours = len(jj)
NUM("n_jours", n_jours)
NUM("r_pub_ca", jj["depense_pub"].corr(jj["chiffre_affaires"])); NUM("rho_pub_ca", jj["depense_pub"].corr(jj["chiffre_affaires"], method="spearman"))
NUM("r2_pub_ca", jj["depense_pub"].corr(jj["chiffre_affaires"]) ** 2 * 100)
jj["groupe"] = np.select([jj["mois"].isin([11, 12]), jj["mois"].isin([3, 4, 5])], ["novembre-décembre", "mars à mai"], "autres mois")
for g, c_ in jj.groupby("groupe"):
    NUM("pub_" + g[:3], c_["depense_pub"].mean()); NUM("ca_" + g[:3], c_["chiffre_affaires"].mean())
jj["pub_res"] = jj["depense_pub"] - jj.groupby("mois")["depense_pub"].transform("mean")
jj["ca_res"] = jj["chiffre_affaires"] - jj.groupby("mois")["chiffre_affaires"].transform("mean")
NUM("r_intra", jj["pub_res"].corr(jj["ca_res"]))
fig, axs = plt.subplots(1, 2, figsize=(10.4, 3.9), constrained_layout=True)
couleurs = {"novembre-décembre": ORANGE, "mars à mai": AQUA, "autres mois": BLEU}
ax = axs[0]
for g, c_ in jj.groupby("groupe"):
    ax.plot(c_["depense_pub"], c_["chiffre_affaires"], ".", color=couleurs[g], ms=3.5, alpha=0.6, label=g)
ax.set_xlabel("dépense publicitaire du jour (€)"); ax.set_ylabel("chiffre d'affaires du jour (€)"); ax.set_title("Tous les jours : r = " + f"{jj['depense_pub'].corr(jj['chiffre_affaires']):.2f}".replace(".", ","))
ax.legend(fontsize=8, markerscale=3, loc="upper left")
ax = axs[1]
for g, c_ in jj.groupby("groupe"):
    ax.plot(c_["pub_res"], c_["ca_res"], ".", color=couleurs[g], ms=3.5, alpha=0.6)
ax.axhline(0, color=MUET, lw=0.8); ax.axvline(0, color=MUET, lw=0.8)
ax.set_xlabel("écart de dépense à la moyenne du mois (€)"); ax.set_ylabel("écart de CA à la moyenne du mois (€)")
ax.set_title("À mois égal : r = " + f"{jj['pub_res'].corr(jj['ca_res']):.2f}".replace(".", ","))
style.save(fig, "ch01-pub.png")
```
<!--sortie-->
```text
NUM n_jours 1096
NUM r_pub_ca 0.41517601017459865
NUM rho_pub_ca 0.2860107180039987
NUM r2_pub_ca 17.237111942449847
NUM pub_aut 140.51475667189953
NUM ca_aut 3006.2855886970174
NUM pub_mar 236.37644927536232
NUM ca_mar 3051.8109057971014
NUM pub_nov 400.46393442622957
NUM ca_nov 4895.374590163935
NUM r_intra 0.04898908594976713
figure : ch01-pub.png
```

![À gauche, chaque point est un jour : la dépense publicitaire (horizontal) et le chiffre d'affaires (vertical), colorés selon la période de l'année. Les points de novembre-décembre (orange) sont en haut à droite : forte dépense et fortes ventes. À droite, les mêmes données après avoir retiré, pour chaque mois, la moyenne du mois : à mois égal, la relation disparaît presque.](figures/ch01-pub.png)

Le nuage de gauche a une structure : les jours de **novembre-décembre** (orange) ont à la fois les plus fortes dépenses (en moyenne 400 € par jour, contre 141 € les autres mois) et les plus fortes ventes (4 895 € par jour contre 3 006 €). La **saison** pousse **en même temps** la dépense (la boutique fait plus de publicité avant Noël) et les ventes (les clients achètent plus avant Noël). La publicité et les ventes sont corrélées parce qu'elles **ont une cause commune**, la saison.

Pour tester cette explication, on compare des jours **du même mois** : on retire à chaque jour la moyenne de son mois, pour la dépense et pour le chiffre d'affaires, et l'on regarde la corrélation entre les **écarts**. Elle tombe de 0,42 à **0,05** (graphique de droite) : à mois égal, un jour de forte dépense n'est pas sensiblement meilleur qu'un jour de faible dépense. Le coefficient initial mesurait surtout l'**effet du calendrier**.

> 💡 **Le facteur de confusion.** Quand une troisième grandeur $Z$ (ici la saison) influence à la fois $X$ (la dépense) et $Y$ (les ventes), $X$ et $Y$ sont corrélées **même si $X$ n'a aucun effet sur $Y$**. On dit que $Z$ est un **facteur de confusion**. C'est la raison de principe pour laquelle une corrélation observée ne prouve pas une causalité.

Peut-on aller plus loin, et chiffrer le **vrai** effet de la publicité ? On compare des journées qui ne diffèrent que par la dépense, en neutralisant simultanément le mois, le jour de la semaine, la promotion, la pluie et la tendance (une **régression multiple**, que le volume III de cette série détaille). Voici le résultat pour la dépense cumulée sur les sept derniers jours, en milliers d'euros, et la variation relative du nombre de commandes :

| Effet de 1 000 € de dépense hebdomadaire sur le nombre de commandes | Estimation | Intervalle à 95 % |
|---|---:|---:|
| **Naïf** : sans rien neutraliser | +32 % | |
| **Ajusté** : à mois, jour, promotion, pluie et tendance égaux | +0,7 % | de -3,7 % à +5,3 % |
| **Vérité programmée** | +1,5 % | |

L'estimation naïve annonce que 1 000 € de plus par semaine augmentent les commandes de **32 %** : un résultat énorme, qui est un artefact de la saison. L'estimation ajustée est de l'ordre de **0,7 %**, avec un intervalle qui contient à la fois **zéro** et la vérité (+1,5 %). Honnêtement : avec trois ans de données et un effet aussi petit, on **ne sait pas distinguer** une publicité utile d'une publicité inutile. C'est une conclusion modeste, et c'est la bonne : pour la trancher, il faudrait **faire varier la dépense exprès** (une expérience), pas attendre que le calendrier la fasse varier à notre place.

```python hide
m_naif = smf.ols("lc ~ pub7k", data=jj).fit()
m_adj = smf.ols("lc ~ pub7k + C(mois) + C(jour_sem) + promo_active + t + pluvieux", data=jj).fit()
b_adj = m_adj.params["pub7k"]; se_adj = m_adj.bse["pub7k"]
NUM("pub_naif", (np.exp(m_naif.params["pub7k"]) - 1) * 100)
NUM("pub_adj", (np.exp(b_adj) - 1) * 100)
NUM("pub_adj_bas", (np.exp(b_adj - 1.96 * se_adj) - 1) * 100); NUM("pub_adj_haut", (np.exp(b_adj + 1.96 * se_adj) - 1) * 100)
NUM("promo_adj", (np.exp(m_adj.params["promo_active"]) - 1) * 100)
NUM("promo_bas", (np.exp(m_adj.conf_int().loc["promo_active", 0]) - 1) * 100); NUM("promo_haut", (np.exp(m_adj.conf_int().loc["promo_active", 1]) - 1) * 100)
NUM("tend_adj", (np.exp(m_adj.params["t"]) - 1) * 100)
assert m_adj.conf_int().loc["pub7k", 0] < 0.015 < m_adj.conf_int().loc["pub7k", 1]
```
<!--sortie-->
```text
NUM pub_naif 31.908406760730635
NUM pub_adj 0.7315144144337093
NUM pub_adj_bas -3.682223368086346
NUM pub_adj_haut 5.347510615846618
NUM promo_adj 19.175378725848002
NUM promo_bas 14.270542134151022
NUM promo_haut 24.290745709209773
NUM tend_adj 6.526876583838548
```

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.7.

### 1.4.4 La température et les ventes de jardin

Un second exemple, plus subtil. La boutique vend, dans sa catégorie « Jardin », des arrosoirs, des parasols, des transats. Sur les 1 096 jours, le nombre de lignes « Jardin » vendues dans la journée est corrélé à la température moyenne du jour (coefficient de corrélation de 0,69). Le froid ou la chaleur du jour pilotent-ils les achats de jardin ?

On refait le test précédent : comparer des jours **du même mois**. À mois égal, la corrélation entre l'écart de température et l'écart de lignes « Jardin » vaut **-0,00** : rien. C'est **la saison**, une fois de plus, qui produit la liaison : en été il fait chaud *et* l'on achète des transats ; mais un jour de juillet plus frais que la moyenne ne fait pas vendre moins. (Dans cette simulation, la température intervient dans le *choix des catégories* selon le mois, jamais selon le temps du jour. Dans la réalité, la météo du jour peut avoir un effet réel : on ne le saurait qu'en le mesurant à saison égale, comme on vient de le faire.)

```python hide
lj = lig.assign(jardin=(lig["categorie"] == "Jardin").astype(int)).groupby("date_commande")["jardin"].sum()
jj["jardin"] = lj.reindex(jj["date"]).fillna(0).values
jj["temp_res"] = jj["temperature_moy"] - jj.groupby("mois")["temperature_moy"].transform("mean")
jj["jar_res"] = jj["jardin"] - jj.groupby("mois")["jardin"].transform("mean")
NUM("r_temp_jardin", jj["temperature_moy"].corr(jj["jardin"])); NUM("r_temp_intra", jj["temp_res"].corr(jj["jar_res"]))
```
<!--sortie-->
```text
NUM r_temp_jardin 0.6912599496681746
NUM r_temp_intra -0.00018640305890668435
```

### 1.4.5 Les corrélations fortuites

Troisième piège : à force de chercher, on **trouve**. Avec 100 variables, il y a $100\times99/2=4\,950$ paires. Si chacune est testée au risque habituel de 5 %, on s'attend à voir environ 5 % de paires « significativement » corrélées **par pur hasard**, soit quelque 250. Vérifions avec 100 séries de 30 nombres tirés au hasard, **indépendantes** par construction.

```python
import numpy as np
rng = np.random.default_rng(7)
series = rng.normal(size=(30, 100))                   # 100 variables sans aucun lien, 30 observations
r = np.corrcoef(series.T)[np.triu_indices(100, 1)]    # les 4 950 corrélations
print("paires :", len(r), "| |r| > 0,36 :", int((abs(r) > 0.36).sum()), "| plus grand |r| :", round(abs(r).max(), 2))
```
<!--sortie-->
```text
paires : 4950 | |r| > 0,36 : 271 | plus grand |r| : 0.63
```

```python hide
rng_f = np.random.default_rng(7)
ser = rng_f.normal(size=(30, 100)); rf = np.corrcoef(ser.T)[np.triu_indices(100, 1)]
NUM("n_paires", len(rf)); NUM("n_fortuit", (abs(rf) > 0.36).sum()); NUM("max_fortuit", abs(rf).max()); NUM("part_fortuit", (abs(rf) > 0.36).mean() * 100)
```
<!--sortie-->
```text
NUM n_paires 4950
NUM n_fortuit 271
NUM max_fortuit 0.6337187308858852
NUM part_fortuit 5.474747474747475
```

Avec 30 observations, un coefficient dépasse 0,36 en valeur absolue dans environ 5 % des cas **sous l'hypothèse d'indépendance** ; on en trouve ici **271 sur 4 950** (5,5 %), et le plus grand atteint **0,63**, un chiffre qui ferait un joli graphique dans une présentation. Aucune de ces liaisons n'est réelle. La leçon est celle du **dragage de données** (*p-hacking*) : plus on teste de relations, plus on est sûr d'en trouver une « remarquable ». Le remède est de **formuler l'hypothèse avant** de regarder les données, de **corriger** pour le nombre de comparaisons (le volume III y revient), et surtout de **vérifier sur des données nouvelles** : une vraie relation survit, une relation fortuite disparaît.

### 1.4.6 De la corrélation à la causalité

Quand on observe que $X$ et $Y$ sont corrélées, il y a **quatre** explications possibles :

1. **$X$ cause $Y$** (la publicité fait vendre).
2. **$Y$ cause $X$** : la **causalité inverse**. La gérante règle son budget de décembre sur les ventes qu'elle attend : les ventes « causent » la dépense.
3. **Un tiers $Z$ cause les deux** : le **facteur de confusion** (la saison).
4. **Le hasard** : une corrélation fortuite, surtout quand on a cherché ou que $n$ est petit.

Les explications se combinent, et les données seules ne disent pas laquelle est la bonne. Dessiner la situation aide : une flèche par influence supposée.

```python hide
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
fig, ax = plt.subplots(figsize=(7.6, 2.9)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 4)
def boite(x_, y_, txt, col):
    ax.add_patch(FancyBboxPatch((x_ - 1.35, y_ - 0.34), 2.7, 0.68, boxstyle="round,pad=0.05", fc="white", ec=col, lw=1.8))
    ax.text(x_, y_, txt, ha="center", va="center", fontsize=9.5, color=ENCRE)
def fleche(a, b, col, txt=None, ls="-", lw=1.8, dy=0.0, dx=0.0):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=14, color=col, lw=lw, ls=ls, shrinkA=2, shrinkB=2))
    if txt:
        ax.text((a[0] + b[0]) / 2 + dx, (a[1] + b[1]) / 2 + dy, txt, ha="center", fontsize=8.5, color=col)
boite(5, 3.3, "Saison", MUET); boite(1.7, 1.0, "Dépense publicitaire", BLEU); boite(8.3, 1.0, "Ventes", ORANGE)
fleche((4.3, 2.95), (2.3, 1.4), MUET, "forte influence", dx=-0.9, dy=0.1); fleche((5.7, 2.95), (7.7, 1.4), MUET, "forte influence", dx=0.9, dy=0.1)
fleche((3.1, 1.0), (6.9, 1.0), ROUGE, "effet réel (petit)", ls="--", dy=0.22)
style.save(fig, "ch01-confusion.png")
```
<!--sortie-->
```text
figure : ch01-confusion.png
```

![Le schéma du facteur de confusion dans la boutique. La saison influence fortement la dépense publicitaire et les ventes (flèches grises) ; l'effet direct de la dépense sur les ventes (flèche rouge pointillée) est petit. La corrélation observée entre dépense et ventes mélange les deux chemins.](figures/ch01-confusion.png)

Comment établir qu'une relation est **causale** ? La méthode la plus solide est l'**expérience aléatoire** : on **décide au hasard** quels clients (ou quels jours) reçoivent le « traitement » (la publicité, la promotion, l'e-mail) et l'on compare les groupes. Le tirage au sort garantit que tous les facteurs de confusion, connus ou inconnus, se répartissent également entre les groupes ; la différence qui reste ne peut venir que du traitement. C'est le **test A/B**, que le volume III détaille. Quand l'expérience est impossible (on ne peut pas tirer au sort la saison), on **ajuste** par des facteurs mesurés, comme nous l'avons fait ; mais l'ajustement ne neutralise que ce que l'on a **pensé** à mesurer.

Les données de la boutique, parce qu'elles sont simulées, permettent un contrôle rare : comparer ce que l'on estime à ce qui a **réellement** été programmé.

| Effet | Estimation naïve | Estimation ajustée | Vérité programmée |
|---|---:|---:|---|
| Promotion sur le nombre de commandes du jour | +8 % | +19 % (de +14 à +24 %) | +18 % |
| Dépense hebdomadaire (+1 000 €) sur les commandes | +32 % | +0,7 % (de -3,7 à +5,3 %) | +1,5 % |
| Tendance annuelle des commandes | | +6,5 % | +6 % |

Pour la **promotion**, la comparaison naïve (nombre moyen de commandes les jours de promotion et les autres) donne +8 % : la plupart des jours de promotion tombent **en creux saisonnier** (soldes de janvier et d'été), ce qui réduit l'écart apparent. En comparant à mois, jour de semaine et tendance égaux, on retrouve +19 %, tout près des +18 % programmés. Même méthode que pour la publicité, même facteur de confusion (le calendrier), mais **ici** l'effet est assez grand pour émerger du bruit, **là** il ne l'est pas. Le contrôle par les facteurs mesurés a donc **fonctionné pour la promotion** et **révélé un effet minuscule pour la publicité** : deux conclusions honnêtes à partir des mêmes outils.

```python hide
jj["promo_active"] = jj["promo_active"].astype(int)
NUM("promo_naif", (jj[jj["promo_active"] == 1]["nb_commandes"].mean() / jj[jj["promo_active"] == 0]["nb_commandes"].mean() - 1) * 100)
```
<!--sortie-->
```text
NUM promo_naif 7.800284461526474
```

> ⚠️ **Le vocabulaire compte.** « La publicité **augmente** les ventes » est une affirmation causale ; « les ventes sont **plus élevées** les jours de forte publicité » est un constat. Dans un rapport, écrivez le constat sauf si votre méthode (expérience, ajustement soigneux, argument de mécanisme) justifie l'affirmation, et **dites laquelle**.

> ✅ **À retenir.** (1) $r$ mesure une liaison **linéaire**, entre −1 et +1 ; il est instable sur peu de données et aveugle à la forme (Anscombe) : **dessinez**. (2) Une corrélation a quatre explications : cause, cause inverse, facteur de confusion, hasard. (3) Comparer **à saison égale** fait souvent disparaître une corrélation : la saison, le calendrier, la taille des clients sont les facteurs de confusion habituels. (4) À force de chercher, on trouve : formulez l'hypothèse avant, vérifiez sur des données nouvelles. (5) La preuve causale la plus solide est l'expérience aléatoire ; à défaut, ajuster honnêtement et dire ce que l'on n'a pas pu mesurer.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.7, exercices 1.11 et 1.12.
