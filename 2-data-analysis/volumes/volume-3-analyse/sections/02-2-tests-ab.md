## 2.2 Tests A/B : conception et lecture des résultats

Un test A/B est une **expérience** : on tire au sort qui voit la version A et qui voit la version B, puis on compare un résultat chiffré. Le tirage au sort est ce qui donne à un test A/B une force que n'aura jamais une corrélation : comme les deux groupes ne diffèrent, en moyenne, **que** par la version qu'ils ont vue, un écart qui n'est pas du hasard est **causé** par la version. Cette section explique comment préparer un test, comment lire les deux tests de la boutique (celui de l'e-mail, qui ne conclut pas, et celui de la page de paiement, dont la répartition est suspecte), les pièges qui font mentir les tests, et comment décider.

### 2.2.1 Concevoir avant de lancer

La plupart des tests ratés l'étaient **avant** d'être lancés. Six décisions, à écrire **avant** de regarder le moindre résultat, forment la **fiche de conception**.

| Décision | Question à trancher | Exemple (e-mail) |
|---|---|---|
| **L'hypothèse** | Qu'attend-on, et pourquoi ? | Un objet plus court augmente l'ouverture et les achats |
| **L'unité** | Qui est tiré au sort ? | Le contact (une adresse), pas l'e-mail ni la session |
| **La métrique principale** | Un seul indicateur décisif | Achat dans les 7 jours (pas l'ouverture, qui n'est qu'un moyen) |
| **Les garde-fous** | Ce qui ne doit pas se dégrader | Taux de désabonnement, retours |
| **La taille et la durée** | Combien de contacts, combien de temps, fixés **à l'avance** | Calculées en 2.5 pour un effet minimal qui compte |
| **La règle de décision** | Que fait-on selon le résultat ? | Déployer si l'intervalle de confiance exclut zéro **et** l'effet dépasse 0,3 point |

Trois principes les gouvernent.

- **Le tirage au sort est la seule vraie protection.** Si l'on met la version B « pour les clients fidèles » et la version A « pour les autres », on ne teste plus la version : on compare deux populations. Le tirage doit être fait par un procédé aléatoire (une fonction de hachage de l'identifiant fait très bien l'affaire), jamais « un jour sur deux » ni « les nouveaux contre les anciens ».
- **Une métrique principale, choisie à l'avance.** Si l'on regarde dix métriques, l'une d'elles sortira significative par hasard (2.1.3, cinquième erreur). Les autres métriques servent à **comprendre**, pas à **conclure**.
- **La taille se fixe avant, pas pendant.** Arrêter un test « dès que c'est significatif » est la façon la plus sûre de produire de faux positifs (2.2.6).

> ⚠️ **Piège.** Un test A/B ne démontre une cause que pour **la population tirée au sort** et **pendant la période du test**. Un résultat obtenu en juin sur des visiteurs de juin ne se transpose pas sans réflexion aux soldes de janvier.

### 2.2.2 Lire le test d'e-mail

L'e-mail a été envoyé à 12 000 contacts tirés au sort. Trois indicateurs sont disponibles ; celui qui compte (la métrique principale) est l'achat à 7 jours. Nous les calculons tous les trois pour voir comment le test se lit.

```python
lignes = []
for nom, col in [("ouverture", "ouvert"), ("clic", "clique"), ("achat à 7 jours", "achat_7j")]:
    t = email.groupby("groupe")[col].agg(["sum", "size"])
    r = O.deux_proportions(t.loc["A", "sum"], t.loc["A", "size"], t.loc["B", "sum"], t.loc["B", "size"])
    lignes.append([nom, f"{r['pa']:.2%}", f"{r['pb']:.2%}", f"{r['ecart']*100:+.2f}", f"[{r['ic_bas']*100:+.2f} ; {r['ic_haut']*100:+.2f}]", f"{r['p']:.4f}"])
print(pd.DataFrame(lignes, columns=["indicateur", "A", "B", "écart (pts)", "IC à 95 %", "p"]).to_string(index=False))
```
<!--sortie-->
```text
     indicateur      A      B écart (pts)       IC à 95 %      p
      ouverture 21.82% 26.08%       +4.27 [+2.74 ; +5.79] 0.0000
           clic  3.88%  4.88%       +1.00 [+0.27 ; +1.73] 0.0075
achat à 7 jours  2.92%  3.38%       +0.47 [-0.16 ; +1.09] 0.1434
```

La lecture se fait ligne par ligne, **en commençant par la métrique principale** : l'**achat** passe de 2,92 % à 3,38 % (+0,47 point), mais l'intervalle de confiance, de −0,16 à +1,09 point, **contient zéro** et la p-valeur est de 0,143 : le test **ne conclut pas**. L'**ouverture** et le **clic**, eux, augmentent nettement (+4,27 et +1,00 point) : le nouvel objet attire davantage d'ouvertures et de clics, mais cela n'a pas été démontré pour les achats.

> 💡 **Intuition.** « Non significatif » se lit : *je ne peux pas dire si l'objet change les achats*. Ce n'est ni « il ne change rien », ni « il change un peu ». La question utile devient : *l'expérience pouvait-elle voir l'effet qui m'intéresse ?* C'est la question de la **puissance**.

#### Ce test pouvait-il voir quelque chose ?

Les données sont simulées et la **vérité programmée** est connue : le nouvel objet augmente réellement le taux d'achat, de **3,0 % à 3,4 %**, soit 0,4 point. Une expérience de 6 000 contacts par groupe aurait-elle dû le voir ? On le mesure par simulation : on rejoue 4 000 fois l'expérience avec ces deux taux réels, et l'on compte la part des expériences qui concluent.

```python
rng = np.random.default_rng(1)
puiss = O.puissance_simulee(rng, 0.030, 0.034, 6000)
n_requis = O.taille_deux_proportions(0.030, 0.034)
print("part des expériences qui détectent l'effet réel :", round(puiss, 3))
print("effectif par groupe pour 80 % de puissance :", round(n_requis))
```
<!--sortie-->
```text
part des expériences qui détectent l'effet réel : 0.236
effectif par groupe pour 80 % de puissance : 30387
```

La **puissance** de ce test est d'environ **24 %** : même si le nouvel objet apporte bien 0,4 point, trois expériences sur quatre ne concluront pas. Pour avoir 80 % de chances de le voir, il aurait fallu environ **30 400 contacts par groupe**, soit plus de cinq fois ce que la liste permettait. Le test n'a donc pas échoué parce que l'effet n'existait pas, mais parce qu'il était **trop petit pour cette taille d'échantillon**.

> ✅ **À retenir.** Avant de lancer un test, calculez la **taille nécessaire** pour l'effet minimal qui compterait pour l'entreprise (2.5). Si la liste est trop petite, ne lancez pas le test : vous n'apprendriez rien. Et si un test non significatif est déjà derrière vous, calculez la puissance **a posteriori sur un effet qui compte** (pas sur l'effet observé), pour dire ce qu'il pouvait voir.

### 2.2.3 Le montant : une queue lourde

La gérante demande aussi : « Et en euros ? Les clients du nouvel objet dépensent-ils plus ? » Le **montant d'achat par contact** est une mesure difficile : 97 % des contacts n'achètent pas, et ceux qui achètent dépensent des montants très inégaux.

```python
ach = email[email["achat_7j"] == 1]
print(email.groupby("groupe")["montant_7j"].agg(moyenne="mean", mediane="median").round(3).T.to_string())
print(ach.groupby("groupe")["montant_7j"].agg(acheteurs="size", moyenne="mean", mediane="median").round(1).T.to_string())
```
<!--sortie-->
```text
groupe       A      B
moyenne  2.722  3.093
mediane  0.000  0.000
groupe         A      B
acheteurs  175.0  203.0
moyenne     93.3   91.4
mediane     69.3   71.6
```

Par contact, la **moyenne** est de 2,72 € pour A et 3,09 € pour B ; la **médiane** vaut zéro dans les deux groupes (la plupart des contacts ne dépensent rien). Chez les seuls acheteurs (175 et 203), la moyenne est de 93,3 € et 91,4 € : le panier **n'augmente pas**. Si le montant par contact semble plus élevé avec B, c'est uniquement parce qu'il y a plus d'acheteurs, et cette différence n'est pas démontrée.

Trois tests donnent la même conclusion, avec des hypothèses différentes.

```python
a, b = (email.loc[email["groupe"] == g, "montant_7j"].values for g in ("A", "B"))
rng = np.random.default_rng(1)
boot = np.array([rng.choice(b, 6000).mean() - rng.choice(a, 6000).mean() for _ in range(3000)])
print("écart de moyennes :", round(b.mean() - a.mean(), 2), "€")
print("Welch p =", round(stats.ttest_ind(b, a, equal_var=False).pvalue, 3), "| Mann-Whitney p =", round(stats.mannwhitneyu(b, a).pvalue, 3))
print("bootstrap, IC à 95 % :", np.percentile(boot, [2.5, 97.5]).round(2))
```
<!--sortie-->
```text
écart de moyennes : 0.37 €
Welch p = 0.324 | Mann-Whitney p = 0.141
bootstrap, IC à 95 % : [-0.39  1.09]
```

```python hide-code
tous = np.sort(np.r_[a, b])[::-1]
print("part des 120 plus gros montants (1 % des contacts) dans le total :", round(tous[:120].sum() / tous.sum(), 3))
```
<!--sortie-->
```text
part des 120 plus gros montants (1 % des contacts) dans le total : 0.595
```

L'écart de moyennes (+0,37 € par contact) a un intervalle de confiance de −0,39 à +1,10 € et des p-valeurs de 0,32 (Welch) et 0,14 (Mann-Whitney) : on ne peut rien conclure sur le montant. Le montant par contact est une variable à **queue lourde** : en cumulant les deux groupes, **les 120 contacts qui dépensent le plus (1 % de l'échantillon) font 60 % des euros**. Quelques très gros paniers peuvent faire basculer une moyenne ; c'est pourquoi on teste d'abord la **proportion d'acheteurs**, plus stable, et l'on traite le montant avec prudence (bootstrap, médiane des acheteurs, ou plafonnement des valeurs extrêmes).

### 2.2.4 Le test de la page de paiement : vérifier la répartition d'abord

La deuxième expérience porte sur la nouvelle page de paiement du site, testée en juin sur environ 38 600 sessions. L'intention était une répartition **50/50**. Avant de comparer les conversions, un contrôle de bon sens : **la répartition observée est-elle bien 50/50 ?**

```python
effectifs = site["groupe"].value_counts().sort_index()
khi = stats.chisquare(effectifs.values)
print(effectifs.to_dict(), "| part de B :", round(effectifs["B"] / effectifs.sum(), 4))
print("khi-deux d'une répartition 50/50 :", round(khi.statistic, 1), "| p =", f"{khi.pvalue:.1e}")
```
<!--sortie-->
```text
{'A': 20048, 'B': 18574} | part de B : 0.4809
khi-deux d'une répartition 50/50 : 56.3 | p = 6.4e-14
```

On a 20 048 sessions pour A et 18 574 pour B : **48,1 % de B** au lieu de 50 %. L'écart de 1 474 sessions n'a rien de fortuit : le test du khi-deux donne $\chi^2=56$ et une p-valeur de $6\times10^{-14}$. C'est un **défaut de répartition** (en anglais *sample ratio mismatch*, SRM) : le tirage au sort **n'a pas été respecté** quelque part dans la chaîne.

> ⚠️ **Piège.** Un défaut de répartition invalide le test, quelle que soit la conversion observée : le mécanisme qui a fait « disparaître » des sessions de B (ici, nous le saurons à la fin, un filtre) peut aussi bien avoir retiré des sessions qui convertissent mal ou bien. **Ne lisez pas le résultat avant d'avoir élucidé le défaut.** En pratique, on vérifie la répartition globale **et** par appareil, par jour, par source de trafic, pour localiser où les sessions manquent.

On localise donc le défaut. La répartition par appareil des sessions diffère entre les groupes :

```python
tab = pd.crosstab(site["appareil"], site["groupe"])
print(tab.to_string())
print((tab / tab.sum()).round(3).to_string())
print("khi-deux d'indépendance appareil × groupe :", round(stats.chi2_contingency(tab)[0], 1), "| p =", f"{stats.chi2_contingency(tab)[1]:.1e}")
```
<!--sortie-->
```text
groupe          A      B
appareil                
mobile      11688  11625
ordinateur   7195   5768
tablette     1165   1181
groupe          A      B
appareil                
mobile      0.583  0.626
ordinateur  0.359  0.311
tablette    0.058  0.064
khi-deux d'indépendance appareil × groupe : 101.3 | p = 1.0e-22
```

Il manque des sessions **sur ordinateur** dans le groupe B (5 768 contre 7 195 dans A, alors que sur mobile les groupes sont presque égaux). Les ordinateurs pèsent 31,1 % des sessions de B contre 35,9 % de celles de A ; la composition des groupes n'est donc plus la même. **La vérité programmée** : un filtre de robots n'a été appliqué qu'au groupe B et a retiré environ 20 % de ses sessions sur ordinateur. Un tel filtre ne devrait pas changer le taux de conversion des sessions restantes, mais le groupe B contient désormais **plus de mobiles**, qui convertissent un peu mieux : la comparaison globale est faussée par la **composition**.

### 2.2.5 Effet global, effet par appareil, comparaisons multiples

On lit malgré tout les conversions, en connaissant la limite du test.

```python
t = site.groupby("groupe")["commande"].agg(["sum", "size"])
g = O.deux_proportions(t.loc["A", "sum"], t.loc["A", "size"], t.loc["B", "sum"], t.loc["B", "size"])
print(f"global : A {g['pa']:.2%} | B {g['pb']:.2%} | écart {g['ecart']*100:+.2f} pt, IC [{g['ic_bas']*100:+.2f} ; {g['ic_haut']*100:+.2f}], p = {g['p']:.3f}")
```
<!--sortie-->
```text
global : A 3.53% | B 3.70% | écart +0.17 pt, IC [-0.21 ; +0.54], p = 0.379
```

Globalement, B convertit à 3,70 % contre 3,53 % pour A : +0,17 point, avec un intervalle de −0,21 à +0,54 point et une p-valeur de 0,38 : **rien de démontré**. L'analyste curieux regarde alors **par appareil** (et voit apparaître quelque chose).

```python
lignes, pvals = [], []
for dev in ["mobile", "ordinateur", "tablette"]:
    x = site[site["appareil"] == dev].groupby("groupe")["commande"].agg(["sum", "size"])
    r = O.deux_proportions(x.loc["A", "sum"], x.loc["A", "size"], x.loc["B", "sum"], x.loc["B", "size"])
    lignes.append([dev, int(x["size"].sum()), r["ecart"] * 100, r["ic_bas"] * 100, r["ic_haut"] * 100, r["p"]]); pvals.append(r["p"])
res = pd.DataFrame(lignes, columns=["appareil", "sessions", "écart (pts)", "IC bas", "IC haut", "p brute"])
res["p ajustée (Holm)"] = O.holm(pvals)
print(res.round(3).to_string(index=False))
```
<!--sortie-->
```text
  appareil  sessions  écart (pts)  IC bas  IC haut  p brute  p ajustée (Holm)
    mobile     23313        0.570   0.072    1.069    0.025             0.075
ordinateur     12963       -0.509  -1.092    0.073    0.090             0.179
  tablette      2346       -0.908  -2.512    0.696    0.267             0.267
```

Sur **mobile**, l'écart est de +0,57 point, avec un intervalle de 0,07 à 1,07 point et une p-valeur brute de **0,025** : « significatif ». Mais on a fait **trois tests** (trois appareils), et sur trois tests, la probabilité d'en trouver au moins un à moins de 5 % par pur hasard est d'environ 14 %. La **correction de Holm** (qui garantit un risque global de 5 % sur l'ensemble des tests) ajuste les p-valeurs : celle du mobile devient **0,075**, au-dessus du seuil. Le résultat par appareil n'est donc plus significatif.

```python hide-code
rep_a = site.loc[site["groupe"] == "A", "appareil"].value_counts(normalize=True)
taux_b = site[site["groupe"] == "B"].groupby("appareil")["commande"].mean()
repondere = float((rep_a * taux_b).sum())
print("conversion de B repondérée sur la répartition d'appareils de A :", round(repondere * 100, 2), "% | écart avec A :", round((repondere - site.loc[site["groupe"] == "A", "commande"].mean()) * 100, 2), "point")
pv6 = []
for (dv, nv), x in site.groupby(["appareil", "nouveau_visiteur"]):
    t6 = x.groupby("groupe")["commande"].agg(["sum", "size"])
    pv6.append(O.deux_proportions(t6.loc["A", "sum"], t6.loc["A", "size"], t6.loc["B", "sum"], t6.loc["B", "size"])["p"])
print("six sous-groupes : p brutes de", round(min(pv6), 3), "à", round(max(pv6), 3), "| p ajustées (Holm) de", round(O.holm(pv6).min(), 2), "à", round(O.holm(pv6).max(), 2))
```
<!--sortie-->
```text
conversion de B repondérée sur la répartition d'appareils de A : 3.63 % | écart avec A : 0.1 point
six sous-groupes : p brutes de 0.069 à 0.977 | p ajustées (Holm) de 0.41 à 0.98
```

```python hide
fig, ax = plt.subplots(figsize=(6.4, 2.9))
etiq = [f"{r['appareil']}\n({r['sessions']:,} sessions)".replace(",", " ") for _, r in res.iterrows()]
y = np.arange(3)[::-1]
ax.errorbar(res["écart (pts)"], y, xerr=[res["écart (pts)"] - res["IC bas"], res["IC haut"] - res["écart (pts)"]], fmt="o", color=BLEU, capsize=4)
ax.axvline(0, color=MUET, lw=1); ax.set_yticks(y); ax.set_yticklabels(etiq, fontsize=8)
for yi, (_, r) in zip(y, res.iterrows()):
    ax.text(r["IC haut"] + 0.1, yi, f"p = {r['p brute']:.3f}  (Holm : {r['p ajustée (Holm)']:.3f})".replace(".", ","), va="center", fontsize=8)
ax.set_xlim(-3, 4.2); ax.set_xlabel("Écart de conversion B − A (points), avec intervalle de confiance à 95 %")
ax.set_title("Effet de la nouvelle page de paiement, par appareil", loc="left")
fig.savefig("figures/ch02-appareils.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

![Écart de conversion entre la nouvelle et l'ancienne page de paiement pour chaque appareil, avec intervalle de confiance à 95 % et p-valeurs brute et ajustée par la méthode de Holm.](figures/ch02-appareils.png)

La **vérité programmée** : la nouvelle page apporte réellement **+0,75 point sur mobile** et **rien sur ordinateur ni sur tablette**. L'analyse par appareil a donc **bien deviné** la nature de l'effet (un effet sur mobile : +0,57 point, dans l'intervalle de la vérité), mais le test **ne peut pas le démontrer**, ni après correction, ni a fortiori sans elle : environ 23 000 sessions mobiles ne suffisent pas pour un effet de 0,75 point sur une conversion de 3,6 %. Remarquez aussi que les **intervalles** sont plus instructifs que les p-valeurs : celui du mobile exclut à peine zéro, celui de l'ordinateur et de la tablette sont larges.

Deux enseignements, qui valent bien au-delà de ce test.

- **Les sous-groupes sont une pente glissante.** Chaque découpage supplémentaire (appareil, nouveau visiteur, jour de la semaine…) est un test de plus, donc une chance de plus de trouver un faux positif. Six sous-groupes (appareil × nouveau visiteur) donnent, après Holm, des p-valeurs ajustées de 0,41 à 0,98 : aucun effet ne ressort. On annonce **à l'avance** les sous-groupes que l'on analysera, ou on les présente comme des **pistes** à confirmer par un nouveau test.
- **La composition des groupes compte.** Avec le défaut de répartition, B compte plus de mobiles. En **repondérant** B pour qu'il ait la même répartition d'appareils que A, la conversion de B passe à 3,63 % (au lieu de 3,70 %) : l'écart global n'est plus que de +0,10 point. Une partie de l'écart apparent venait donc de la composition, pas de la page.

> ✅ **À retenir.** Ordre de lecture d'un test A/B : (1) la répartition est-elle conforme ? (2) l'écart global et son intervalle ; (3) les garde-fous ; (4) seulement alors, les sous-groupes annoncés, **corrigés** pour les comparaisons multiples.

### 2.2.6 Regarder en continu : le piège de l'arrêt prématuré

Le tableau de bord du test est ouvert chaque matin, et chaque matin la p-valeur est un peu différente. La tentation : s'arrêter dès qu'elle passe sous 0,05. C'est une grave erreur, que l'on peut chiffrer par simulation. Imaginons un test **A/A** : les deux groupes reçoivent **exactement la même version** ; il n'y a donc aucun effet, et chaque conclusion « significative » est un faux positif. On le suit pendant 21 jours, 900 sessions par jour, et l'on calcule la p-valeur **chaque jour** sur les données cumulées.

```python
rng = np.random.default_rng(7)
P = np.array([O.p_aa(rng) for _ in range(4000)])
print("conclusion à 5 % au 21e jour seulement :", round((P[:, -1] < 0.05).mean(), 3))
print("conclusion à l'un des trois contrôles hebdomadaires (j7, j14, j21) :", round((P[:, [6, 13, 20]] < 0.05).any(axis=1).mean(), 3))
print("« significatif » à au moins un des 21 jours :", round((P < 0.05).any(axis=1).mean(), 3))
```
<!--sortie-->
```text
conclusion à 5 % au 21e jour seulement : 0.052
conclusion à l'un des trois contrôles hebdomadaires (j7, j14, j21) : 0.117
« significatif » à au moins un des 21 jours : 0.268
```

Si l'on ne regarde qu'**une fois**, au 21ᵉ jour, on a bien environ 5 % de faux positifs. Mais en regardant **chaque jour** et en s'arrêtant à la première p-valeur sous 0,05, on se trompe dans plus d'**un test sur quatre** (27 % dans cette simulation) : plus de cinq fois ce qu'annonce le seuil. Même un contrôle hebdomadaire (trois regards) double le risque. La figure montre trente tests A/A : beaucoup d'entre eux franchissent le seuil un jour donné, puis le quittent.

```python hide
fig, ax = plt.subplots(figsize=(6.4, 3.3))
for k in range(30):
    ax.plot(np.arange(1, 22), P[k], color=BLEU, alpha=0.35, lw=1)
ax.axhline(0.05, color=ROUGE, lw=1.5, ls="--"); ax.set_yscale("log"); ax.set_ylim(0.002, 1.1)
ax.text(1.2, 0.058, "seuil de 5 %", color=ROUGE, fontsize=8)
ax.set_xlabel("Jour du test"); ax.set_ylabel("p-valeur calculée ce jour-là (échelle log)")
ax.set_title("30 tests A/A suivis jour après jour : aucun effet, et pourtant des « victoires »", loc="left")
fig.savefig("figures/ch02-regarder-en-continu.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

![Trente tests A/A (sans aucun effet) suivis pendant 21 jours : p-valeur de chaque jour en échelle logarithmique ; plusieurs courbes passent sous le seuil de 5 % avant de remonter.](figures/ch02-regarder-en-continu.png)

Trois remèdes, du plus simple au plus sophistiqué : **fixer la durée et la taille à l'avance et ne conclure qu'à la fin** (la règle d'or) ; si l'on veut pouvoir s'arrêter plus tôt, utiliser une méthode **séquentielle** conçue pour cela (les tests à « seuils dépensés » ajustent le seuil à chaque regard) ; ou simplement **regarder** le tableau de bord sans décider, en réservant la décision à la date prévue.

```python hide-code
jour = pd.to_datetime(site["date"])
min_p = 1.0
for dj in sorted(jour.unique()):
    x = site[jour <= dj].groupby("groupe")["commande"].agg(["sum", "size"])
    min_p = min(min_p, O.deux_proportions(x.loc["A", "sum"], x.loc["A", "size"], x.loc["B", "sum"], x.loc["B", "size"])["p"])
print("plus petite p-valeur cumulée sur les 21 jours du test de la page de paiement :", round(min_p, 3))
```
<!--sortie-->
```text
plus petite p-valeur cumulée sur les 21 jours du test de la page de paiement : 0.122
```

Sur le vrai test de la page de paiement, la p-valeur cumulée n'est jamais passée sous 0,12 (la plus petite vaut 0,122) : le piège n'aurait pas mordu cette fois, mais le hasard aurait pu en décider autrement.

### 2.2.7 Nouveauté, interférences et durée

Trois autres sources d'erreur se corrigent par la conception : la nouveauté, les interférences et la durée.

#### L'effet de nouveauté

Un objet inhabituel attire d'abord la curiosité, puis l'effet retombe. Regardons l'écart d'ouverture entre B et A selon l'heure d'envoi.

```python hide-code
tr = pd.cut(email["heure_envoi"], [-1, 5, 11, 17, 23], labels=["0-5 h", "6-11 h", "12-17 h", "18-23 h"])
op = email.groupby([tr, "groupe"], observed=True)["ouvert"].mean().unstack()
print("écart d'ouverture B − A par tranche d'heure d'envoi (points) :", ((op["B"] - op["A"]) * 100).round(1).to_dict())
```
<!--sortie-->
```text
écart d'ouverture B − A par tranche d'heure d'envoi (points) : {'0-5 h': 4.2, '6-11 h': 5.9, '12-17 h': 3.7, '18-23 h': 3.3}
```

Dans nos données, l'écart d'ouverture entre B et A est positif dans chaque tranche horaire d'envoi (entre 3,3 et 5,9 points), et la vérité programmée contient un effet de nouveauté qui s'estompe au fil des envois ; mais le bruit est tel que l'on ne peut pas lire cette décroissance dans quatre tranches. Pour détecter une nouveauté, on suit l'effet **par semaine** sur un test assez long, et l'on se méfie des tests très courts.

#### Les interférences

On suppose que la version vue par une personne n'influence pas ce que fait une autre. C'est faux si les utilisateurs s'influencent (un code de réduction qui circule, deux membres d'un même foyer dans des groupes différents) ou partagent une ressource (un stock limité). On tire alors au sort des **groupes** (foyers, villes), pas des individus.

#### La durée

Même si la taille est atteinte en deux jours, on laisse tourner **au moins un cycle complet** de l'activité (ici, une ou deux semaines entières, car le samedi n'est pas le mardi), pour ne pas mesurer seulement un jour particulier.

### 2.2.8 Décider et rapporter

À la fin du test, trois décisions sont possibles, et **non significatif** n'en est pas une.

| Résultat | Décision | Exemple |
|---|---|---|
| L'intervalle exclut zéro **et** l'effet minimal qui compte | **Déployer** | Ouverture de l'e-mail : +4,3 points (IC 2,7 à 5,8) |
| L'intervalle contient zéro **et** de valeurs qui comptent | **Attendre ou refaire plus grand** | Achat par e-mail : IC −0,16 à +1,09 point, puissance de 24 % |
| L'intervalle contient zéro **et** seulement des valeurs sans intérêt | **Abandonner** (l'effet, s'il existe, est trop petit pour compter) | — |

Un rapport de test tient en une page.

> **Rapport de test A/B : objet d'e-mail (6 000 contacts par groupe, 7 jours).**
> 1. **Objectif et hypothèse** : un objet plus court augmente les achats à 7 jours.
> 2. **Conception** : tirage au sort par contact, métrique principale = achat à 7 jours ; 6 000 contacts par groupe, alors qu'il en aurait fallu environ 30 400 pour un effet de 0,4 point.
> 3. **Contrôles** : répartition 50/50 respectée (6 000 contre 6 000).
> 4. **Résultats** : achat +0,47 point (IC −0,16 à +1,09), p = 0,14 ; ouverture +4,27 points ; clic +1,00 point.
> 5. **Interprétation** : le test **ne permet pas de conclure** sur les achats ; sa puissance pour un effet de 0,4 point est d'environ 24 %.
> 6. **Décision proposée** : adopter l'objet pour l'ouverture et poursuivre le test sur une liste plus grande avant de conclure sur les achats.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.2 à 2.4, exercices 2.5 à 2.8.
