## 2.1 Tests essentiels et quand les utiliser

Un test d'hypothèses est une **procédure** pour décider si un écart observé dans un échantillon est assez grand pour qu'on cesse de croire qu'il vient du simple hasard. Cette section donne la logique (une seule, valable pour tous les tests), les cinq erreurs que l'on commet le plus souvent en lisant une p-valeur, puis les quatre tests qu'un analyste utilise 90 % du temps et l'arbre qui permet de choisir.

### 2.1.1 Une question, deux hypothèses

Reprenons l'e-mail de la gérante. On compare la part d'acheteurs du groupe A (ancien objet) et du groupe B (nouvel objet). Un test commence par écrire **deux hypothèses**, qui s'excluent.

- L'**hypothèse nulle**, notée $H_0$, dit « il ne se passe rien » : le nouvel objet ne change pas la probabilité d'acheter. Les deux groupes ont le même taux d'achat réel, et l'écart observé n'est que le hasard du tirage au sort.
- L'**hypothèse alternative**, notée $H_1$, dit « il se passe quelque chose » : les taux réels sont différents (test **bilatéral**, que l'on utilise par défaut), ou le taux de B est supérieur à celui de A (test **unilatéral**, que l'on n'utilise que si l'on avait décidé à l'avance qu'une baisse n'aurait aucune importance).

La logique est celle d'un **procès**. L'accusé est présumé innocent ($H_0$) ; on ne le déclare coupable ($H_1$) que si les preuves sont **très difficiles à expliquer** s'il était innocent. Et un acquittement ne prouve pas l'innocence : il dit seulement que les preuves ne suffisent pas. C'est la clé de ce chapitre : *« non significatif » ne veut pas dire « pas d'effet »*.

> 💡 **Intuition.** Un test répond à : « *Si rien ne se passait, verrait-on souvent un écart aussi grand que celui que j'ai observé ?* » Si l'on en voyait souvent, l'écart ne prouve rien. Si l'on en voyait rarement, on a une raison de douter de $H_0$.

### 2.1.2 La p-valeur, sans jargon

La **p-valeur** est la probabilité de cette question : *si $H_0$ était vraie, quelle serait la probabilité d'observer un écart au moins aussi grand que le nôtre ?* Plus elle est petite, plus l'écart est surprenant sous $H_0$.

On peut **la fabriquer sans formule** par une expérience de pensée, que l'ordinateur fait en une seconde. Si le nouvel objet ne change rien, alors l'étiquette « A » ou « B » collée à chaque contact est arbitraire : on peut la **mélanger** au hasard sans changer le monde. On mélange donc les 12 000 étiquettes, on recalcule l'écart de taux d'achat, et l'on recommence 10 000 fois. La part des mélanges qui donnent un écart **au moins aussi grand que l'écart réel** est la p-valeur.

```python
rng = np.random.default_rng(1)
achat = email["achat_7j"].values
est_b = (email["groupe"] == "B").values
ecart_obs = achat[est_b].mean() - achat[~est_b].mean()
melanges = np.empty(10000)
for k in range(10000):
    m = rng.permutation(achat)                    # on mélange les résultats : les étiquettes A/B n'ont plus de sens
    melanges[k] = m[:6000].mean() - m[6000:].mean()
p_perm = np.mean(np.abs(melanges) >= abs(ecart_obs))
print("écart observé :", round(ecart_obs * 100, 2), "points | p-valeur par mélange :", round(p_perm, 3))
```
<!--sortie-->
```text
écart observé : 0.47 points | p-valeur par mélange : 0.161
```

```python hide
fig, ax = plt.subplots(figsize=(6.4, 3.3))
ax.hist(melanges * 100, bins=50, color=BLEU, alpha=0.75, edgecolor="white", linewidth=0.4)
ax.axvline(ecart_obs * 100, color=ORANGE, lw=2); ax.axvline(-ecart_obs * 100, color=ORANGE, lw=2, ls="--")
ax.set_xlabel("Écart de taux d'achat B − A obtenu après mélange des étiquettes (points)"); ax.set_ylabel("Nombre de mélanges")
ax.text(ecart_obs * 100 + 0.03, ax.get_ylim()[1] * 0.9, "écart observé", color=ORANGE, fontsize=9)
ax.set_title("Si l'objet ne changeait rien : 10 000 écarts obtenus par le seul hasard", loc="left")
fig.savefig("figures/ch02-melange.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

![Distribution des écarts de taux d'achat obtenus en mélangeant au hasard les étiquettes A et B ; les traits orange marquent l'écart réellement observé et son opposé.](figures/ch02-melange.png)

La figure se lit ainsi : si le nouvel objet était sans effet, des écarts de la taille de l'écart observé (le trait orange) ou plus grands apparaîtraient dans environ **16 %** des mélanges. Ce n'est pas rare du tout. L'écart de 28 acheteurs est donc **compatible avec le hasard**, et la p-valeur vaut environ 0,16.

On obtient une valeur voisine par la **formule** du test de comparaison de deux proportions (le test $z$), que nous utiliserons désormais parce qu'elle ne demande aucune simulation : on divise l'écart observé par son erreur type sous $H_0$, ce qui donne une statistique $z$ ; la p-valeur se lit dans la loi normale.

$$z=\frac{\hat p_B-\hat p_A}{\sqrt{\hat p\,(1-\hat p)\left(\frac1{n_A}+\frac1{n_B}\right)}},\qquad \hat p=\frac{x_A+x_B}{n_A+n_B}.$$

```python
res = O.deux_proportions(175, 6000, 203, 6000)
print({k: round(v, 4) for k, v in res.items()})
```
<!--sortie-->
```text
{'pa': 0.0292, 'pb': 0.0338, 'ecart': 0.0047, 'ic_bas': np.float64(-0.0016), 'ic_haut': np.float64(0.0109), 'z': np.float64(1.4634), 'p': np.float64(0.1434)}
```

Le test $z$ donne $z=1{,}46$ et une p-valeur de **0,143**, voisine de celle du mélange (0,16). La petite différence est normale : le mélange est le calcul **exact** (c'est ce que fait le test de Fisher, qui donne 0,158), alors que le test $z$ en est une approximation par la loi normale. L'écart est de **0,47 point**, avec un intervalle de confiance à 95 % de **−0,16 à +1,09 point** : il contient zéro.

> 📐 **D'où vient cette formule ?** Sous $H_0$, les deux groupes ont le même taux $p$, que l'on estime par la proportion globale $\hat p$ d'acheteurs ; l'écart $\hat p_B-\hat p_A$ a alors pour variance $p(1-p)(1/n_A+1/n_B)$ (la somme des variances de deux proportions indépendantes). Divisé par son écart-type, il suit approximativement une loi normale centrée réduite (théorème central limite). La p-valeur est la probabilité que $|Z|$ dépasse la valeur observée.

### 2.1.3 Les cinq erreurs d'interprétation de la p-valeur

La p-valeur est l'objet statistique le plus mal compris. Voici les cinq contresens classiques, à relire avant chaque rapport. Ici $p=0{,}143$.

1. **« Il y a 14 % de chances que l'objet ne serve à rien. »** Faux. La p-valeur est calculée **en supposant** que l'objet ne sert à rien : elle ne peut donc pas donner la probabilité de cette hypothèse. Elle dit : *si* l'objet ne sert à rien, *alors* un écart de cette taille arrive dans 14 % des tirages.
2. **« $p>0{,}05$, donc il n'y a pas d'effet. »** Faux, et c'est l'erreur la plus coûteuse. Un test non significatif dit que les données **ne permettent pas de trancher**. Nous verrons en 2.2.2 que cette expérience était **trop petite** pour détecter l'effet réel (qui existe : c'est une donnée programmée).
3. **« $p<0{,}05$, donc l'effet est important. »** Faux. Avec assez de données, un effet minuscule devient « significatif » (voir plus bas, 2.1.5). La p-valeur mesure la **surprise**, pas la **taille**.
4. **« $p=0{,}049$ est une découverte, $p=0{,}051$ n'en est pas une. »** Faux. Le seuil de 0,05 est une convention ; 0,049 et 0,051 disent la même chose. Regardez l'écart et son intervalle de confiance.
5. **« En essayant dix tests, j'en ai trouvé un à 0,03 : c'est réel. »** Faux. Sur vingt tests où rien ne se passe, on en attend **un** « significatif » à 5 % ; c'est le problème des **comparaisons multiples**, traité en 2.2.5.

> ⚠️ **Piège.** Dans un rapport, ne dites jamais « il y a x % de chances que… » à partir d'une p-valeur. Dites : « un écart aussi grand serait observé dans x % des cas si les deux versions étaient équivalentes », ou, mieux, donnez l'écart et son intervalle.

### 2.1.4 Erreurs de type I et de type II, seuil et puissance

Un test peut se tromper de deux façons, comme un procès.

| | $H_0$ est vraie (rien ne se passe) | $H_1$ est vraie (il y a un effet) |
|---|---|---|
| **On rejette $H_0$** | **Erreur de type I** (faux positif), probabilité $\alpha$ | Bonne décision (probabilité $1-\beta$ : la **puissance**) |
| **On ne rejette pas $H_0$** | Bonne décision | **Erreur de type II** (faux négatif), probabilité $\beta$ |

Le **seuil** $\alpha$ (très souvent 5 %) est la probabilité de faux positif que l'on accepte **à l'avance** : en fixant $\alpha=5\ \%$, on s'impose de rejeter $H_0$ quand la p-valeur est inférieure à 0,05. La **puissance** $1-\beta$ est la probabilité de détecter un effet réel de taille donnée ; on vise couramment 80 %. Elle dépend de trois choses : la **taille de l'effet**, la **taille de l'échantillon** et le seuil $\alpha$. Les deux erreurs sont en tension : exiger moins de faux positifs ($\alpha$ plus petit) fait perdre de la puissance.

```python hide
x = np.linspace(-4, 6, 600)
decalage = 0.004 / np.sqrt(2 * 0.032 * 0.968 / 6000)           # effet réel (0,4 point) divisé par l'erreur type d'un groupe de 6 000
c = 1.96
puiss = 1 - stats.norm.cdf(c - decalage) + stats.norm.cdf(-c - decalage)
fig, ax = plt.subplots(figsize=(6.6, 3.4))
ax.plot(x, stats.norm.pdf(x), color=MUET, lw=1.5); ax.plot(x, stats.norm.pdf(x, decalage), color=BLEU, lw=1.8)
ax.fill_between(x[x >= c], stats.norm.pdf(x[x >= c]), color=ROUGE, alpha=0.35)
ax.fill_between(x[x <= c], stats.norm.pdf(x[x <= c], decalage), color=ORANGE, alpha=0.35)
ax.axvline(c, color="black", lw=0.8, ls=":")
ax.text(-3.9, 0.36, "$H_0$ : aucun effet", color=MUET); ax.text(2.2, 0.36, "$H_1$ : effet réel", color=BLEU)
ax.text(2.35, 0.03, "α (faux positif)", color=ROUGE, fontsize=8); ax.text(-0.3, 0.07, "β (effet manqué)", color=ORANGE, fontsize=8)
ax.set_xlabel("Statistique z du test"); ax.set_yticks([]); ax.set_title("Deux erreurs possibles, et un seuil de décision entre les deux", loc="left")
fig.savefig("figures/ch02-erreurs.png", dpi=200, bbox_inches="tight"); plt.close(fig)
print("puissance pour un effet de 0,4 point et 6 000 par groupe :", round(puiss, 3))
```
<!--sortie-->
```text
puissance pour un effet de 0,4 point et 6 000 par groupe : 0.238
```

![Deux courbes en cloche : celle de H0 (aucun effet) et celle de H1 (effet réel de 0,4 point) ; la zone rouge est l'erreur de type I, la zone orange l'erreur de type II.](figures/ch02-erreurs.png)

La figure montre notre cas : si le nouvel objet apporte réellement 0,4 point d'achats supplémentaires (la courbe bleue), la grande majorité de cette courbe reste **à gauche du seuil** : l'expérience le **manque** dans environ trois cas sur quatre, parce que 6 000 personnes par groupe, avec un taux d'achat de 3 %, ne suffisent pas à distinguer un écart aussi petit du bruit. Nous chiffrerons cette puissance en 2.2.2.

### 2.1.5 L'intervalle de confiance plutôt que la p-valeur seule, et « significatif » n'est pas « important »

Une p-valeur répond par oui ou non à « ce n'est pas du hasard ? ». Un **intervalle de confiance** répond à la question qui intéresse la gérante : « *de combien ?* ». Il donne **la taille de l'effet et son incertitude**, et il permet de lire d'un coup d'œil le test (zéro est-il dans l'intervalle ?) **et** l'importance (les valeurs de l'intervalle sont-elles grandes ou petites pour l'entreprise ?).

Le test de l'ouverture des e-mails montre un cas inverse du test d'achat : l'écart est **net**.

```python
ouv = email.groupby("groupe")["ouvert"].agg(["sum", "size"])
res_ouv = O.deux_proportions(ouv.loc["A", "sum"], ouv.loc["A", "size"], ouv.loc["B", "sum"], ouv.loc["B", "size"])
print(f"ouverture A {res_ouv['pa']:.1%} | B {res_ouv['pb']:.1%} | écart {res_ouv['ecart']*100:.2f} pts, IC [{res_ouv['ic_bas']*100:.2f} ; {res_ouv['ic_haut']*100:.2f}], p = {res_ouv['p']:.1e}")
```
<!--sortie-->
```text
ouverture A 21.8% | B 26.1% | écart 4.27 pts, IC [2.74 ; 5.79], p = 4.4e-08
```

Le nouvel objet augmente le taux d'ouverture de **4,27 points** (de 21,8 % à 26,1 %), avec un intervalle de 2,74 à 5,79 points : l'effet est réel et d'une taille qui compte. La p-valeur, elle, est minuscule, mais ce n'est pas elle qui informe.

À l'inverse, un effet **significatif** peut être **négligeable**. Si l'on envoyait l'e-mail à deux millions de personnes (un million par groupe) et que le taux d'achat passait de 3,00 % à 3,05 %, le test serait significatif… pour un gain de **cinq centièmes de point**.

```python
gros = O.deux_proportions(30000, 1_000_000, 30500, 1_000_000)
print(f"écart {gros['ecart']*100:.3f} point, IC [{gros['ic_bas']*100:.3f} ; {gros['ic_haut']*100:.3f}], p = {gros['p']:.3f}")
```
<!--sortie-->
```text
écart 0.050 point, IC [0.003 ; 0.097], p = 0.039
```

La p-valeur est de 0,04 : « significatif ». Mais l'effet vaut cinq centièmes de point, et l'intervalle va de 0,003 à 0,097 point : même la valeur haute ne justifierait pas de changer d'habitude si le nouvel objet coûtait quoi que ce soit. **Significatif** répond à « *est-ce réel ?* », **important** répond à « *est-ce que cela compte pour l'entreprise ?* ». Il faut toujours les deux.

> ✅ **À retenir.** Rapportez **l'écart, son intervalle de confiance et la p-valeur**, dans cet ordre. Si l'intervalle contient des valeurs qui ne changeraient pas votre décision, ce n'est pas la peine de s'inquiéter de la p-valeur.

### 2.1.6 Les quatre tests que l'on utilise le plus

Presque toutes les questions d'un analyste se ramènent à quatre situations.

#### Comparer deux proportions

C'est le cas du taux d'achat, du taux de conversion, du taux de retour. Le test $z$ ci-dessus est le plus simple. Deux variantes donnent presque le même résultat : le **test du khi-deux** (qui est le carré de $z$ ; ici $\chi^2=2{,}14=z^2$, même p-valeur 0,143) et le **test exact de Fisher** (p-valeur 0,158), à préférer quand les effectifs sont très petits (moins de 5 attendus dans une case).

```python hide-code
tab = np.array([[175, 6000 - 175], [203, 6000 - 203]])
khi_ = stats.chi2_contingency(tab, correction=False)
print("khi-deux :", round(khi_[0], 2), "| p =", round(khi_[1], 3), "| Fisher p =", round(stats.fisher_exact(tab)[1], 3))
```
<!--sortie-->
```text
khi-deux : 2.14 | p = 0.143 | Fisher p = 0.158
```

#### Comparer deux moyennes

C'est le cas du panier moyen par canal. Le **test $t$ de Welch** compare deux moyennes **sans supposer** que les deux groupes ont la même variance : c'est le choix par défaut. Pour le panier moyen 2025 des commandes du Site (101,63 €) et de la Boutique (103,08 €), l'écart est de 1,45 € ; la statistique $t$ vaut −0,94 et la p-valeur 0,345 : aucune raison de penser que les paniers diffèrent d'un canal à l'autre. Le test $t$ de Student (qui suppose les variances égales) donne ici 0,344 : presque la même chose, mais Welch ne coûte rien et évite l'erreur quand les variances diffèrent.

```python hide-code
c25 = cmd[cmd["date_commande"] >= "2025-01-01"]
pa_, pb_ = c25.loc[c25["canal"] == "Site", "panier"], c25.loc[c25["canal"] == "Boutique", "panier"]
w_ = stats.ttest_ind(pa_, pb_, equal_var=False)
print("panier moyen Site", round(pa_.mean(), 2), "| Boutique", round(pb_.mean(), 2), "| Welch t =", round(w_.statistic, 2), ", p =", round(w_.pvalue, 3), "| Student p =", round(stats.ttest_ind(pa_, pb_).pvalue, 3), "| Mann-Whitney p =", round(stats.mannwhitneyu(pa_, pb_).pvalue, 3))
```
<!--sortie-->
```text
panier moyen Site 101.63 | Boutique 103.08 | Welch t = -0.94 , p = 0.345 | Student p = 0.344 | Mann-Whitney p = 0.447
```

#### Comparer des distributions asymétriques

Les montants sont asymétriques (volume I, section 1.1) : quelques gros paniers tirent la moyenne. Deux options. Le **test de Mann-Whitney** compare les **rangs** plutôt que les valeurs : il demande si une valeur tirée au hasard dans un groupe tend à être plus grande qu'une valeur tirée dans l'autre. Le **bootstrap** recalcule l'écart de moyennes sur des milliers de rééchantillonnages des données observées, ce qui donne un intervalle sans hypothèse sur la forme de la distribution. Pour les paniers Site/Boutique, Mann-Whitney donne $p=0{,}447$, même conclusion que Welch.

#### Comparer des mesures appariées

Quand les deux séries portent sur **les mêmes unités** (les mêmes jours, les mêmes clients avant et après), on ne compare pas deux groupes indépendants : on calcule la **différence pour chaque unité**, puis on teste si sa moyenne est nulle (**test $t$ apparié**, ou **test de Wilcoxon** si les différences sont asymétriques). Exemple : le nombre de commandes **du Site et de la Boutique, jour par jour** en 2025. Les deux séries partagent la saison et le jour de semaine ; en comparant jour par jour, on neutralise ces effets communs.

```python
cj = cmd[cmd["date_commande"] >= "2025-01-01"].groupby(["date_commande", "canal"]).size().unstack(fill_value=0)
t_app = stats.ttest_rel(cj["Site"], cj["Boutique"])
print("moyenne par jour : Site", round(cj["Site"].mean(), 2), "| Boutique", round(cj["Boutique"].mean(), 2))
print("t apparié :", round(t_app.statistic, 2), "| p-valeur :", f"{t_app.pvalue:.1e}", "| Wilcoxon :", f"{stats.wilcoxon(cj['Site'], cj['Boutique']).pvalue:.1e}")
```
<!--sortie-->
```text
moyenne par jour : Site 16.65 | Boutique 14.91
t apparié : 6.04 | p-valeur : 3.8e-09 | Wilcoxon : 2.5e-08
```

Le Site reçoit en moyenne 1,74 commande de plus par jour que la Boutique (16,65 contre 14,91) ; l'écart est très significatif (p de l'ordre de $10^{-9}$). Un test non apparié, qui ignorerait que ce sont les mêmes jours, aurait eu beaucoup moins de pouvoir, parce que la variance liée au calendrier aurait noyé l'écart.

### 2.1.7 Un arbre de décision pour choisir son test

Deux questions suffisent pour trouver le bon test : **quelle variable** mesure-t-on, et **sur quels groupes** ?

| Ce que vous comparez | Groupes | Test par défaut | Si les conditions ne sont pas remplies |
|---|---|---|---|
| Une **proportion** (achat, retour, conversion) | 2 groupes indépendants | $z$ de deux proportions (ou khi-deux) | Fisher si les effectifs sont petits |
| Une proportion, **plusieurs catégories** | 2 variables catégorielles | khi-deux d'indépendance | Fisher, regrouper les modalités rares |
| Une **moyenne** (panier, durée) | 2 groupes indépendants | $t$ de Welch | Mann-Whitney ou bootstrap si très asymétrique et petit échantillon |
| Une moyenne | 3 groupes ou plus | ANOVA | Kruskal-Wallis |
| Une moyenne, **mêmes unités** (avant/après, jour par jour) | 2 mesures appariées | $t$ apparié | Wilcoxon |
| Le lien entre **deux variables numériques** | une seule population | corrélation (section 2.3) | Spearman si non linéaire ou valeurs extrêmes |

> 🧭 **En pratique.** Avec plus de quelques centaines d'observations par groupe, le test de Welch, le test $z$ et le khi-deux donnent des conclusions pratiquement identiques à leurs variantes « robustes ». Ne perdez pas de temps à hésiter entre eux : perdez-le plutôt à **vérifier que le test répond à la bonne question** (qui est comparé à qui, sur quelle unité, avec quelle durée ?).

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.1, exercices 2.1 à 2.4.
