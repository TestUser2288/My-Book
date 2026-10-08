## 1.4 ➕ Erreurs courantes et graphiques trompeurs

Un graphique peut tromper sans qu'aucun chiffre soit faux. Il suffit d'un axe qui ne part pas de zéro, d'une période bien choisie ou de deux échelles ajustées pour que la lectrice tire une conclusion que les données ne soutiennent pas. Cette section présente **dix pièges**. Chacun est montré par un graphique qui trompe, puis par sa version corrigée ; et pour chacun, nous répondons à trois questions, parce que c'est ainsi que l'on mesure la gravité d'une erreur : **qui est trompé, par quoi, avec quelle conséquence**.

Une précision avant de commencer : la plupart de ces pièges sont **involontaires**. On les commet parce que l'outil le propose par défaut, parce que le graphique « avait l'air mieux » ainsi, ou parce que l'on n'a pas vu ce que la lectrice verrait. Mais l'effet est le même, et la responsabilité de la personne qui publie aussi.

> ⚠️ **Règle d'honnêteté.** Si un graphique vous plaît **parce qu'il appuie votre message**, relisez-le comme si vous cherchiez à le contredire. Les trois questions de cette section (qui, quoi, quelle conséquence) servent à cela.

### 1.4.1 L'axe tronqué

**Le piège.** Une barre représente une valeur par sa **longueur**. Si l'axe ne part pas de zéro, la longueur ne représente plus la valeur : elle représente l'**écart** à la valeur où l'on a coupé. Les chiffres d'affaires de 2023, 2024 et 2025 (1 139, 1 189 et 1 325 k€) en donnent un exemple.

![À gauche, les trois chiffres d'affaires annuels sur des barres dont l'axe est coupé à 1 100 k€ : 2025 paraît presque six fois plus haut que 2023. À droite, les mêmes barres avec un axe à zéro : +16 % en deux ans. Figure construite avec matplotlib (données simulées).](figures/ch01-axe-tronque.png)

```python hide
O.fig_axe_tronque()
```
<!--sortie-->
```text
figure : ch01-axe-tronque.png
```

```python
t = F["t"]
visuel = (t[2025] - 1100) / (t[2023] - 1100)        # hauteurs des barres si l'axe part de 1 100 k€
reel = t[2025] / t[2023]
print(f"hauteur apparente : x{visuel:.1f} ; rapport réel : x{reel:.2f} (+{(reel - 1) * 100:.0f} %)")
```
<!--sortie-->
```text
hauteur apparente : x5.8 ; rapport réel : x1.16 (+16 %)
```

Avec un axe coupé à 1 100 k€, la barre de 2025 paraît **5,8 fois** plus haute que celle de 2023 ; en réalité, elle ne l'est que de 16 %. Le graphique de droite, à zéro, dit la vérité.

**Qui est trompé, par quoi, avec quelle conséquence ?** *La gérante, ou le financeur*, par la **longueur des barres**, qui laisse croire à un quasi-sextuplement de l'activité. *Conséquence :* un investissement ou un recrutement décidé sur une croissance imaginaire ; et, quand la réalité rattrape l'enthousiasme, une confiance durablement entamée dans tous les graphiques de l'analyste.

**Le correctif.** Pour des **barres**, l'axe part de zéro, sans exception. Pour une **courbe**, on peut ne pas partir de zéro, à condition que l'axe soit visible et que l'on ne cherche pas à dramatiser (si l'écart est petit, on le **dit** dans le titre : « +16 % en deux ans »).

### 1.4.2 Les aires proportionnelles au mauvais carré, et la 3D

**Le piège.** Quand on représente une valeur par un cercle, un carré ou une icône, il faut décider ce qui est proportionnel à la valeur : la **dimension** (rayon, côté) ou l'**aire**. Si l'on prend le rayon, une valeur trois fois plus grande donne un cercle d'une aire **neuf** fois plus grande, et c'est l'aire que l'œil perçoit.

![À gauche, des cercles dont le rayon est proportionnel à la valeur (1, 2, 3) : celui de la valeur 3 paraît neuf fois plus grand que celui de la valeur 1. À droite, des cercles dont l'aire est proportionnelle à la valeur : l'impression de 1 à 3 est respectée. Schéma dessiné avec matplotlib.](figures/ch01-aire-rayon.png)

```python hide
O.fig_aire_rayon()
assert 3 ** 2 == 9
```
<!--sortie-->
```text
figure : ch01-aire-rayon.png
```

Le même effet vaut pour les **graphiques en 3D** : une barre en perspective ne se lit plus contre une grille, sa hauteur dépend de l'angle de vue, et celles du fond sont partiellement cachées. Il n'y a **aucun cas** où l'effet 3D aide à lire un chiffre.

**Qui est trompé, par quoi, avec quelle conséquence ?** *Tout lecteur*, par l'**aire** et la **perspective**, qui amplifient les grandes valeurs. *Conséquence :* des écarts surestimés ou mal classés (la barre de devant paraît plus grande que celle de derrière, même quand elle est plus petite).

**Le correctif.** Représenter les valeurs par la **longueur** (barres planes) ; si l'on doit absolument utiliser des cercles (une carte), faire l'**aire** proportionnelle à la valeur, et ajouter des **étiquettes chiffrées**. Pas de 3D.

### 1.4.3 Des échelles différentes qui rendent comparable ce qui ne l'est pas

**Le piège.** Quand on place deux graphiques côte à côte avec des **axes propres** à chacun, ils ont l'air aussi grands l'un que l'autre, même si l'un représente sept fois plus que l'autre. Les chiffres d'affaires mensuels de la boutique et des réseaux sociaux en 2025 le montrent.

![En haut, deux courbes (boutique, réseaux sociaux) avec chacune son propre axe : les deux variations semblent de même ampleur. En bas, les mêmes courbes sur le même axe de 0 à 85 k€ : l'échelle réelle apparaît. Figure construite avec matplotlib (données simulées).](figures/ch01-echelles.png)

```python hide
O.fig_echelles()
pc = O.ca_mensuel(2025, "canal") / 1000
assert [round(pc.loc[12, k] / pc.loc[2, k], 1) for k in ("Boutique", "Réseaux")] == [2.2, 3.7]
assert [round(v, 1) for v in (pc.loc[12, "Boutique"], pc.loc[12, "Réseaux"])] == [73.4, 20.4]
assert round(F["canal_an"]["Réseaux"] / F["canal_an"].sum() * 100, 1) == 11.0
```
<!--sortie-->
```text
figure : ch01-echelles.png
```

En haut, la courbe de la boutique et celle des réseaux ont toutes les deux une allure ascendante spectaculaire, et on peut les croire de poids comparable. En bas, avec un axe commun, la boutique atteint 73,4 k€ en décembre et les réseaux 20,4 k€ : les réseaux ne représentent que **11,0 %** du chiffre d'affaires de l'année. On voit aussi que, relativement, les réseaux progressent **plus** de février à décembre (×3,7) que la boutique (×2,2), mais à partir d'un niveau bien plus bas : les deux lectures sont vraies, et c'est l'axe commun qui permet de les tenir ensemble.

**Qui est trompé, par quoi, avec quelle conséquence ?** *Un responsable qui compare des canaux*, par l'**apparente égalité** de graphiques à axes libres. *Conséquence :* un budget publicitaire réparti comme si les deux canaux avaient le même poids.

**Le correctif.** Quand on **compare**, on met les séries sur **le même axe** (petits multiples à échelle commune, section 1.2.5). Quand on veut montrer la **forme** d'une série à petite échelle, on peut laisser un axe libre, mais on le **dit** (« axe propre à chaque graphique ») et l'on évite de les juxtaposer comme s'ils étaient comparables.

### 1.4.4 Le double axe

**Le piège.** Deux courbes sur un seul graphique, l'une lue à gauche (en k€), l'autre à droite (en nombre de commandes) : on peut choisir les deux échelles pour que les courbes **coïncident**, ou au contraire qu'elles divergent. Avec la publicité et les commandes mensuelles de 2025, voici ce que donne un bon choix d'échelles.

![À gauche, la publicité mensuelle (axe de gauche, de 0 à 14 k€) et le nombre de commandes (axe de droite, de 0 à 2 000) en 2025 : les deux courbes semblent se suivre, parce que les deux échelles ont été choisies pour cela. À droite, le nuage de points des mêmes douze mois : la relation se voit sans choix d'échelle. Figure construite avec matplotlib (données simulées).](figures/ch01-double-axe.png)

```python hide
r_double = O.fig_double_axe()
assert round(r_double, 2) == 0.80
```
<!--sortie-->
```text
figure : ch01-double-axe.png
```

La corrélation entre les deux séries, sur ces douze mois, vaut 0,80 : elle existe réellement. Mais le graphique de gauche **ne le prouve pas** : l'accord apparent des courbes est le résultat de l'échelle choisie à droite (0 à 2 000) et à gauche (0 à 14). Avec 0 à 3 000 à droite, la courbe des commandes serait bien moins pentue et ne ressemblerait plus à celle de la publicité. Le nuage de droite, lui, **ne dépend d'aucun choix** : un point par mois, la publicité en abscisse, les commandes en ordonnée.

**Qui est trompé, par quoi, avec quelle conséquence ?** *Une direction qui lit « la pub fait vendre »*, par la **coïncidence fabriquée** de deux échelles. *Conséquence :* un budget de publicité augmenté sur la foi d'une ressemblance de courbes qui aurait pu être obtenue avec n'importe quelles deux séries.

**Le correctif.** Deux graphiques **superposés** sur le même axe du temps (un par série), ou un nuage de points. Si l'on emploie malgré tout un double axe, on **colore** chaque axe comme sa courbe et on écrit les unités ; on évite d'ajuster les échelles pour que les courbes se touchent. Mais la corrélation, même réelle, n'est **pas une cause** : voir 1.4.7.

### 1.4.5 La période choisie

**Le piège.** « Les ventes ont progressé de 53 % en trois mois. » La phrase est **vraie** : le chiffre d'affaires mensuel passe de 120 k€ en octobre à 184 k€ en décembre 2025. Mais présentée seule, elle laisse croire à une accélération.

![À gauche, une courbe sur trois mois seulement (octobre à décembre 2025), titrée « les ventes ont progressé de 53 % en trois mois ». À droite, trois années entières : la même hausse se reproduit chaque fin d'année (zone orangée), c'est une saison. Figure construite avec matplotlib (données simulées).](figures/ch01-cerises.png)

```python hide
O.fig_cerises()
od = F["oct_dec"]
assert [round((od[a][1] / od[a][0] - 1) * 100, 1) for a in (2023, 2024, 2025)] == [53.0, 54.7, 53.1]
assert round((F["m"][2] / F["m"][1] - 1) * 100) == -19 and round((od[2025][1] / od[2024][1] - 1) * 100) == 17
```
<!--sortie-->
```text
figure : ch01-cerises.png
```

Sur trois années entières, la même hausse d'octobre à décembre se retrouve chaque fois : +53,0 % en 2023, +54,7 % en 2024, +53,1 % en 2025. Ce n'est pas une accélération, c'est la **saison**. Et l'on peut aussi, en choisissant d'autres bornes, raconter l'inverse : de janvier à février 2025, le chiffre d'affaires baisse de 19 %, et personne ne dira pourtant que la boutique s'effondre.

**Qui est trompé, par quoi, avec quelle conséquence ?** *Le financeur ou la gérante*, par le **choix des bornes**. *Conséquence :* une prévision extrapolée d'une pente saisonnière (on commande trop de stock en janvier, on recrute en décembre pour une demande qui ne durera pas).

**Le correctif.** Montrer **au moins un cycle complet** (un an de plus que ce que l'on veut dire), comparer **au même mois de l'an dernier**, et dire pourquoi on a choisi la période. Une phrase honnête vaut mieux qu'une période flatteuse : « Le chiffre d'affaires de décembre est supérieur de 17 % à celui de décembre 2024. »

### 1.4.6 Les pourcentages sans effectifs

**Le piège.** Un classement de **taux** (« les produits les plus retournés ») met en haut les produits qui ont **peu de ventes**, parce qu'un petit effectif fait varier un taux par à-coups. Prenons les retours de marchandises sur les lignes vendues par les réseaux sociaux : 120 produits, un taux moyen de retour de 6,7 %.

![À gauche, le classement des six produits au taux de retour le plus élevé (de 19 % à 14 %), sans leurs effectifs. À droite, le taux de chaque produit en fonction du nombre de lignes vendues, avec la moyenne (trait plein) et les bornes à 95 % (pointillés) : les petits effectifs s'étalent en entonnoir. Figure construite avec matplotlib (données simulées).](figures/ch01-effectifs.png)

```python hide
O.fig_effectifs()
g_ret = F["ret_g"]
top = g_ret[g_ret["n"] >= 5].sort_values("taux", ascending=False).head(6)
assert list(top["n"].astype(int)) == [27, 44, 31, 50, 44, 65] and [int(v) for v in top["r"]] == [5, 8, 5, 8, 7, 9]
assert [round(v, 1) for v in top["taux"]] == [18.5, 18.2, 16.1, 16.0, 15.9, 13.8]
assert round(100 / 27, 1) == 3.7 and g_ret["n"].median() == 64.5 and len(g_ret) == 120 and int(g_ret["n"].min()) == 17
```
<!--sortie-->
```text
figure : ch01-effectifs.png
```

À gauche, le classement semble alarmant : le produit 116 retourne **18,5 %** de ses ventes, trois fois la moyenne. Mais le produit 116 n'a été vendu que **27 fois** par les réseaux, et **5** de ces lignes ont été retournées. Un retour de plus ou de moins déplace son taux de **3,7 points**. Le produit « typique » a 64,5 lignes vendues ; les six du palmarès en ont entre 27 et 65.

Pour savoir si ces taux sont **trop** élevés, on compare chaque taux à ce que le seul hasard donnerait pour un effectif de cette taille : une borne autour de la moyenne, qui se resserre quand l'effectif grandit (le « diagramme en entonnoir » de droite).

```python
p0 = F["ret_moy"] / 100                                  # taux de retour moyen des réseaux
g = F["ret_g"]
ecart = np.sqrt(p0 * (1 - p0) / g["n"])
for nom, z in (("95 %", 1.96), ("99,8 %", 3.09)):
    haut = int((g["taux"] / 100 > p0 + z * ecart).sum())
    print(f"produits au-dessus de la borne à {nom} : {haut}")
print("attendu par hasard à 95 % :", round(0.025 * len(g)))
```
<!--sortie-->
```text
produits au-dessus de la borne à 95 % : 6
produits au-dessus de la borne à 99,8 % : 0
attendu par hasard à 95 % : 3
```

Six produits dépassent la borne à 95 %, pour **trois** attendus par pur hasard sur 120 produits ; aucun ne dépasse la borne à 99,8 %. Le bon message n'est donc ni « ces produits sont mauvais » ni « tout va bien » : c'est « **à surveiller**, avec des effectifs trop petits pour conclure ».

**Qui est trompé, par quoi, avec quelle conséquence ?** *La responsable des achats*, par un **classement de taux sans effectifs**. *Conséquence :* un produit retiré du catalogue, ou un fournisseur mis en cause, sur la foi de cinq retours.

**Le correctif.** Toujours **donner l'effectif** à côté du taux (« 18,5 % de 27 lignes »), ne classer que les produits ayant un effectif minimal, ou tracer un **diagramme en entonnoir** qui montre où le hasard suffit à expliquer l'écart (les intervalles et les petits effectifs sont traités au volume III, chapitres 2 et 4).

### 1.4.7 La corrélation suggérée

**Le piège.** Deux courbes qui montent ensemble ne se **causent** pas forcément. Ici, la publicité et les commandes de la boutique, mois par mois, sur trois ans.

![À gauche, le nuage de points de la publicité mensuelle et des commandes mensuelles sur 36 mois, titré « corrélation 0,81 ». À droite, le même nuage où novembre-décembre sont en orange, mars-mai en bleu et les autres mois en gris : la saison commande à la fois la publicité et les ventes. Figure construite avec matplotlib (données simulées).](figures/ch01-correlation.png)

```python hide
r_tout = O.fig_corr_suggeree()
assert round(F["r_tout"], 2) == 0.81 and round(F["r_hors"], 2) == 0.16
assert [round(F[k]) for k in ("pub_nd", "pub_hors", "cmd_nd", "cmd_hors")] == [12214, 5158, 1574, 898]
assert round(F["pub_nd"] / F["pub_hors"], 1) == 2.4 and round(F["cmd_nd"] / F["cmd_hors"], 1) == 1.8, (F["pub_nd"], F["pub_hors"], F["cmd_nd"], F["cmd_hors"])
```
<!--sortie-->
```text
figure : ch01-correlation.png
```

Sur 36 mois, la corrélation est de **0,81** : forte. La figure de droite explique pourquoi elle ne prouve rien : en novembre et décembre, la boutique dépense en moyenne **12 214 €** en publicité, contre **5 158 €** les autres mois (2,4 fois plus), et enregistre **1 574** commandes contre **898** (1,8 fois plus). La saison fait monter les deux. Si l'on retire novembre et décembre, la corrélation tombe à **0,16** : presque rien. (Ce piège et la façon de le démêler sont traités au volume III, chapitres 2 et 3 : ici, on retient que le **graphique** ne doit pas suggérer une cause que l'analyse n'a pas établie.)

**Qui est trompé, par quoi, avec quelle conséquence ?** *La gérante*, par un **nuage ou un titre qui parle de corrélation sans la mettre en perspective**. *Conséquence :* doubler le budget publicitaire en comptant sur un effet que la saison seule expliquait.

**Le correctif.** Colorer ou séparer par la variable cachée (la saison), **comparer à saison égale**, et écrire le titre avec prudence : « Publicité et commandes montent ensemble en fin d'année, mais la saison suffit à l'expliquer. »

### 1.4.8 Le camembert à neuf parts

**Le piège.** Au-delà de quatre ou cinq parts, un camembert ne se lit plus : les couleurs se confondent, la légende oblige à des allers-retours et les parts voisines sont indiscernables. Le chiffre d'affaires 2025 par ville (20 villes fictives) en fait un cas d'école.

![À gauche, un camembert à neuf parts (les huit premières villes et « autres villes ») : couleurs et angles voisins se confondent. À droite, les mêmes parts en barres triées, avec « autres villes » (30,4 %) en gris. Figure construite avec matplotlib (données simulées).](figures/ch01-camembert-neuf.png)

```python hide
O.fig_camembert_neuf()
vl = F["villes"]
assert [round(v, 1) for v in vl.values[:8]] == [13.9, 12.4, 9.2, 8.8, 7.8, 6.2, 6.0, 5.3] and round(F["autres_villes"], 1) == 30.4
assert round((vl.iloc[5] - vl.iloc[6]) * 3.6, 1) == 0.8 and len(vl) == 20
```
<!--sortie-->
```text
figure : ch01-camembert-neuf.png
```

Deux parts, la ville F (6,2 %) et la ville G (6,0 %), ne diffèrent que de 0,2 point, soit **0,8 degré** d'angle : personne ne peut les départager sur un camembert. Sur les barres, l'ordre et les valeurs sont immédiats. Et la plus grande « part » est celle des **autres villes** (30,4 %), qui est un fourre-tout : on la met en gris, en bas, pour qu'elle ne passe pas pour une ville.

**Qui est trompé, par quoi, avec quelle conséquence ?** *Un responsable de zone*, par une légende illisible et des angles voisins. *Conséquence :* un classement des villes faux, donc une priorité commerciale mal placée.

**Le correctif.** Barres triées, étiquettes chiffrées, regroupement des petites catégories en un « autres » discret, ou limitation du graphique aux huit premières.

### 1.4.9 Le paradoxe de Simpson en image

**Le piège.** Une moyenne globale peut dire l'inverse de chaque sous-groupe (c'est le paradoxe de Simpson, vu au volume III, chapitre 1). Un graphique qui ne montre que la moyenne globale trompe d'autant plus qu'il est « simple ». Le chiffre d'affaires moyen par jour, avec et sans promotion, en est un exemple.

![À gauche, le chiffre d'affaires moyen par jour des jours sans promotion (3 339 €) et des jours de promotion (3 300 €) : la promotion « rapporte moins ». À droite, la même comparaison mois par mois (janvier, juin, juillet, novembre, les seuls mois avec des promotions) : la promotion rapporte plus, chaque fois. Figure construite avec matplotlib (données simulées).](figures/ch01-simpson.png)

```python hide
glob_s, mois_s = O.fig_simpson()
assert round(glob_s[0]) == 3339 and round(glob_s[1]) == 3300
assert [round((mois_s[1][m] / mois_s[0][m] - 1) * 100, 1) for m in (1, 6, 7, 11)] == [15.5, 2.2, 6.7, 15.3]
jp = O.charger()["j"].assign(m=lambda d: d["date"].dt.month)
assert jp.groupby("m")["promo_active"].sum().to_dict() == {1: 63, 2: 0, 3: 0, 4: 0, 5: 0, 6: 21, 7: 42, 8: 0, 9: 0, 10: 0, 11: 27, 12: 0}
assert round((glob_s[1] / glob_s[0] - 1) * 100, 1) == -1.2
assert round(jp[(jp["m"] == 12)]["chiffre_affaires"].mean()) == 5357 and int(jp["promo_active"].sum()) == 153
```
<!--sortie-->
```text
figure : ch01-simpson.png
```

```python
promo = F["promo_glob"]                                   # CA moyen par jour : sans (0) et avec (1) promotion
mois = F["promo_mois"]                                    # idem, mois par mois (les mois qui ont des promotions)
print(promo.round(0).to_string())
print(((mois[1] / mois[0] - 1) * 100).round(1).to_string())
```
<!--sortie-->
```text
promo_active
0    3339.0
1    3300.0
mois
1     15.5
6      2.2
7      6.7
11    15.3
```

À gauche, un jour de promotion rapporte en moyenne 3 300 €, soit **1,2 % de moins** qu'un jour sans promotion (3 339 €). À droite, mois par mois, la promotion rapporte **plus** : +15,5 % en janvier, +2,2 % en juin, +6,7 % en juillet, +15,3 % en novembre. L'explication est une question de **composition** : les 153 jours de promotion tombent en janvier (63 jours), juin (21), juillet (42) et novembre (27), jamais en décembre, alors que les jours **sans** promotion incluent tout décembre, le meilleur mois de l'année (5 357 € par jour en moyenne). La moyenne globale compare des jours de saisons différentes.

**Qui est trompé, par quoi, avec quelle conséquence ?** *La gérante*, par une **moyenne globale** présentée sans la saison. *Conséquence :* suppression d'une promotion qui rapporte réellement, pour une raison qui tient au calendrier.

**Le correctif.** Comparer **à situation égale** (même mois, même jour de la semaine) et le montrer : le deuxième graphique est le bon.

### 1.4.10 L'échelle logarithmique non signalée

**Le piège.** Une échelle logarithmique transforme les **rapports** en **distances égales** : de 1 à 10 occupe autant de place que de 10 à 100. Elle est précieuse pour des valeurs qui s'étalent sur plusieurs ordres de grandeur (ou pour des taux de croissance), mais elle **comprime** les écarts, et, utilisée sans le dire, elle trompe. Le chiffre d'affaires 2025 des 120 produits, du plus au moins vendu, en donne l'exemple.

![À gauche, le chiffre d'affaires 2025 de chacun des 120 produits en barres sur une échelle linéaire : quelques produits dominent. À droite, le même graphique en échelle logarithmique non signalée : la décroissance paraît douce et régulière. Figure construite avec matplotlib (données simulées).](figures/ch01-log.png)

```python hide
pl = O.fig_log()
pr = F["produits"]
assert round(pr[0], 1) == 66.0 and round(pr[-1], 1) == 0.4 and round(pr[0] / pr[-1]) == 147
assert round(pr[0] / np.median(pr), 1) == 7.9 and round(pr[:10].sum() / pr.sum() * 100, 1) == 29.1 and len(pr) == 120
```
<!--sortie-->
```text
figure : ch01-log.png
```

À gauche, on voit ce qu'il y a de vrai : quelques produits dominent (le premier réalise 66,0 k€, soit **7,9 fois** le produit médian), et dix produits font à eux seuls **29,1 %** du chiffre d'affaires. À droite, la même série en échelle logarithmique, sans mention, semble une pente régulière : les écarts entre produits paraissent modestes. De plus, une **barre** sur une échelle logarithmique ne mesure plus rien : sa longueur dépend de l'endroit, arbitraire, où l'axe est coupé.

**Qui est trompé, par quoi, avec quelle conséquence ?** *Une lectrice non technique*, par une **échelle qu'elle n'a pas reconnue**. *Conséquence :* sous-estimer la concentration du chiffre d'affaires, donc le risque de dépendre de quelques produits.

**Le correctif.** On utilise l'échelle logarithmique **seulement** pour des courbes (jamais des barres), on **l'écrit** (« échelle logarithmique ») dans l'axe ou le titre, et on met en évidence les graduations (1, 10, 100) qui font comprendre qu'un pas est un facteur 10.

### 1.4.11 Une liste de contrôle avant de publier

Pour terminer, voici la liste à parcourir **avant d'envoyer** un graphique. Chaque ligne renvoie à un piège de cette section.

| Piège | La question à se poser |
|---|---|
| Axe tronqué (1.4.1) | Mes barres partent-elles de zéro ? |
| Aires et 3D (1.4.2) | La grandeur est-elle représentée par une longueur, ou par une aire proportionnelle à la valeur ? |
| Échelles différentes (1.4.3) | Si je compare, les axes sont-ils communs ? Sinon, est-ce écrit ? |
| Double axe (1.4.4) | Les deux échelles sont-elles choisies sans arrière-pensée ? Un nuage ne serait-il pas plus honnête ? |
| Période choisie (1.4.5) | Mon graphique montre-t-il au moins un cycle complet ? |
| Pourcentages sans effectifs (1.4.6) | L'effectif est-il visible à côté du taux ? |
| Corrélation suggérée (1.4.7) | Une variable cachée (saison, taille, prix) explique-t-elle les deux courbes ? |
| Camembert à neuf parts (1.4.8) | Plus de quatre parts ? Alors des barres. |
| Simpson (1.4.9) | Ma moyenne mélange-t-elle des sous-groupes qui ne sont pas comparables ? |
| Échelle logarithmique (1.4.10) | Est-elle écrite ? Mes barres sont-elles à échelle linéaire ? |

> ✅ **À retenir.** Un graphique trompeur n'est pas un graphique faux : c'est un graphique **vrai qui suggère une conclusion fausse**. Pour chaque graphique, demandez : *qui pourrait être trompé, par quoi, avec quelle conséquence ?* Et préférez toujours la version qui montre les effectifs, l'axe complet, la période entière et la comparaison à situation égale.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.8 et 1.9, exercices 1.9 à 1.14.
