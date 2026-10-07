# Chapitre 2 : Tests d'hypothèses, tests A/B et corrélation

> « Un écart observé est une question, pas une réponse. »

Le lundi matin, la gérante arrive avec une impression de victoire.

— L'e-mail de la semaine dernière, celui avec le nouvel objet : **3,4 % d'achats contre 2,9 %** pour l'ancien. On le garde pour toutes nos campagnes, non ?

Vous regardez les chiffres. 3,4 est plus grand que 2,9. Mais 12 000 personnes ont reçu l'e-mail, et chaque groupe compte 6 000 contacts : sur 6 000 contacts, 2,9 % font 175 acheteurs, 3,4 % en font 203. Il y a **28 acheteurs de différence**. Est-ce que le nouvel objet les a fait acheter, ou est-ce que le hasard du tirage au sort, d'un groupe à l'autre, a placé 28 acheteurs de plus par chance ?

C'est la question de ce chapitre, et c'est la plus fréquente de toute la vie d'un analyste : **un écart observé est-il réel, ou est-il du bruit ?** Nous répondons avec trois familles d'outils.

- Les **tests d'hypothèses** (section 2.1) donnent une façon disciplinée de dire « cet écart est peu compatible avec le hasard » ou « cet écart pourrait très bien être du hasard », et de **ne pas confondre** les deux.
- Les **tests A/B** (section 2.2) sont des tests d'hypothèses appliqués à une **expérience** : on compare deux versions (un objet d'e-mail, une page de paiement) en les montrant à des groupes tirés au sort. C'est le seul cadre où l'on peut parler de **cause**.
- La **corrélation** (section 2.3) mesure la liaison entre deux variables observées. Elle sert à explorer ; elle ne dit rien de la cause, et nous verrons comment un chiffre élevé peut être trompeur.

Deux sections facultatives complètent : un **catalogue des tests** classiques (2.4) et la **puissance** d'un test, c'est-à-dire la taille d'échantillon dont on a besoin pour avoir une chance de voir ce que l'on cherche (2.5).

## Le chemin de ce chapitre

- **2.1 Tests essentiels et quand les utiliser** : hypothèse nulle, p-valeur (et les cinq façons de la mal comprendre), erreurs de type I et II, intervalle de confiance, et un arbre de décision pour choisir son test.
- **2.2 Tests A/B : conception et lecture des résultats** : préparer un test avant de le lancer, lire le test d'e-mail (non significatif… et pourquoi), vérifier la répartition des groupes sur le test de la page de paiement, éviter les pièges (regarder en continu, comparer dix sous-groupes), décider et rapporter.
- **2.3 Analyse de corrélation** : Pearson, Spearman, Kendall, nuages de points, corrélation fallacieuse, séries temporelles, et le passage (prudent) de la corrélation à la cause.
- **➕ 2.4 Catalogue des tests statistiques** : un tableau de choix et un exemple exécuté pour chaque test classique.
- **➕ 2.5 Analyse de puissance et taille d'échantillon** : combien de personnes interroger ou observer, combien de temps attendre.

> 💡 **Fil conducteur du chapitre.** Un test ne dit pas « cet effet est vrai » ou « faux ». Il répond à une question plus étroite : *si rien ne se passait, verrait-on souvent un écart aussi grand ?* La réponse n'a de sens que si l'expérience était bien conçue, assez grande, et lue une seule fois.

## Les données du chapitre

> 📦 **Les données.** Tout est **simulé** (docstring de `build/donnees_a3.py`), déjà propre, et la **vérité programmée** est connue ; nous la révélerons après chaque analyse, pour que vous puissiez juger ce que la méthode retrouve et ce qu'elle rate.

- `ab_email.csv` : 12 000 contacts d'une liste de diffusion (moitié clients, moitié contacts qui n'ont jamais acheté), tirés au sort entre l'objet **A** (ancien) et **B** (nouveau) ; pour chacun, l'ouverture, le clic, l'achat dans les 7 jours et son montant.
- `ab_site.csv` : environ 38 600 sessions du site pendant trois semaines de juin, avec l'ancienne page de paiement (**A**) ou la nouvelle (**B**), l'appareil utilisé, et si la session a débouché sur une commande.
- `jours_exploitation.csv` : les 1 096 jours de la boutique, avec les commandes, le chiffre d'affaires, la température, la pluie, la promotion du jour et la dépense publicitaire.
- Les tables de la boutique (`commandes.csv`, `lignes_commande.csv`, `retours.csv`, `produits.csv`) pour les exemples du catalogue de tests.


Rappel des bases dont ce chapitre a besoin : l'erreur type, l'intervalle de confiance d'une moyenne et d'une proportion, la différence entre corrélation et causalité (volume I, sections 1.3.3, 1.3.4 et 1.4).


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

```text
khi-deux : 2.14 | p = 0.143 | Fisher p = 0.158
```

#### Comparer deux moyennes

C'est le cas du panier moyen par canal. Le **test $t$ de Welch** compare deux moyennes **sans supposer** que les deux groupes ont la même variance : c'est le choix par défaut. Pour le panier moyen 2025 des commandes du Site (101,63 €) et de la Boutique (103,08 €), l'écart est de 1,45 € ; la statistique $t$ vaut −0,94 et la p-valeur 0,345 : aucune raison de penser que les paniers diffèrent d'un canal à l'autre. Le test $t$ de Student (qui suppose les variances égales) donne ici 0,344 : presque la même chose, mais Welch ne coûte rien et évite l'erreur quand les variances diffèrent.

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

```text
conversion de B repondérée sur la répartition d'appareils de A : 3.63 % | écart avec A : 0.1 point
six sous-groupes : p brutes de 0.069 à 0.977 | p ajustées (Holm) de 0.41 à 0.98
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


![Trente tests A/A (sans aucun effet) suivis pendant 21 jours : p-valeur de chaque jour en échelle logarithmique ; plusieurs courbes passent sous le seuil de 5 % avant de remonter.](figures/ch02-regarder-en-continu.png)

Trois remèdes, du plus simple au plus sophistiqué : **fixer la durée et la taille à l'avance et ne conclure qu'à la fin** (la règle d'or) ; si l'on veut pouvoir s'arrêter plus tôt, utiliser une méthode **séquentielle** conçue pour cela (les tests à « seuils dépensés » ajustent le seuil à chaque regard) ; ou simplement **regarder** le tableau de bord sans décider, en réservant la décision à la date prévue.

```text
plus petite p-valeur cumulée sur les 21 jours du test de la page de paiement : 0.122
```

Sur le vrai test de la page de paiement, la p-valeur cumulée n'est jamais passée sous 0,12 (la plus petite vaut 0,122) : le piège n'aurait pas mordu cette fois, mais le hasard aurait pu en décider autrement.

### 2.2.7 Nouveauté, interférences et durée

Trois autres sources d'erreur se corrigent par la conception : la nouveauté, les interférences et la durée.

#### L'effet de nouveauté

Un objet inhabituel attire d'abord la curiosité, puis l'effet retombe. Regardons l'écart d'ouverture entre B et A selon l'heure d'envoi.

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


## 2.4 ➕ Pour aller plus loin : catalogue des tests statistiques

Cette section est un **catalogue de poche**. Pour chaque test classique : la question à laquelle il répond, ses conditions d'emploi, un exemple exécuté sur les données de la boutique, et la façon de lire le résultat. La section 2.1 en a présenté quatre ; nous ajoutons ici le khi-deux, l'ANOVA avec son test post hoc, et les tests de normalité, et nous rassemblons le tout dans un tableau de choix.

### 2.4.1 Le tableau de choix

| Test | Question | Variable(s) | Conditions principales | Alternative robuste |
|---|---|---|---|---|
| $t$ de Student / Welch | Deux moyennes diffèrent-elles ? | numérique, 2 groupes indépendants | pas de valeurs extrêmes, ou $n$ assez grand | Mann-Whitney, bootstrap |
| $t$ apparié | La moyenne des différences est-elle nulle ? | numérique, mesures appariées | différences à peu près symétriques | Wilcoxon |
| $z$ de deux proportions | Deux taux diffèrent-ils ? | binaire, 2 groupes | effectifs attendus ≥ 5 par case | Fisher |
| Khi-deux d'indépendance | Deux variables catégorielles sont-elles liées ? | 2 catégorielles | effectifs attendus ≥ 5 par case | Fisher, regrouper |
| Khi-deux d'ajustement | La répartition observée suit-elle une répartition donnée ? | 1 catégorielle | effectifs attendus ≥ 5 | test exact |
| ANOVA à un facteur | Plusieurs moyennes diffèrent-elles ? | numérique, 3 groupes ou plus | variances voisines, résidus à peu près normaux | Kruskal-Wallis |
| Mann-Whitney | Un groupe tend-il à avoir des valeurs plus grandes ? | numérique ou ordinale, 2 groupes | aucune condition de forme | — |
| Shapiro-Wilk | Les données sont-elles compatibles avec une loi normale ? | numérique | échantillon modéré | diagramme quantile-quantile |

> ⚠️ **Piège.** Tous ces tests supposent des observations **indépendantes** (une personne ne compte qu'une fois, un jour ne dépend pas du précédent). Cette condition est plus importante que la forme de la distribution, et c'est la plus souvent violée : séries temporelles, clients revenus plusieurs fois, sessions d'un même visiteur.

### 2.4.2 Student, Welch, et le test de normalité

Nous avons comparé en 2.1.6 le panier moyen des commandes du Site et de la Boutique avec le $t$ de Welch. Le test de **Shapiro-Wilk** vérifie la condition de normalité : son hypothèse nulle est que les données **sont** normales. On l'applique ici à 500 paniers pris au hasard.

```python
paniers = cmd.loc[cmd["date_commande"] >= "2025-01-01", ["canal", "panier"]]
echantillon = paniers.loc[paniers["canal"] == "Site", "panier"].sample(500, random_state=1)
w1, q1 = stats.shapiro(echantillon); w2, q2 = stats.shapiro(np.log(echantillon))
print(f"Shapiro, paniers : W = {w1:.3f}, p = {q1:.0e} | paniers en logarithme : W = {w2:.3f}, p = {q2:.0e}")
```
<!--sortie-->
```text
Shapiro, paniers : W = 0.833, p = 2e-22 | paniers en logarithme : W = 0.972, p = 3e-08
```

Dans les deux cas la p-valeur est minuscule (de l'ordre de $10^{-22}$ pour les montants, $10^{-8}$ pour leur logarithme) : les paniers ne sont **pas** normaux, ni même log-normaux. Faut-il abandonner le test $t$ ? Non : avec des milliers d'observations par groupe, le **théorème central limite** rend la **moyenne** approximativement normale même quand les données ne le sont pas. Ce n'est pas le test de normalité qui décide, mais la **taille de l'échantillon** et la présence de valeurs extrêmes. Pour des petits échantillons, regardez plutôt un histogramme et un diagramme quantile-quantile, et préférez un test non paramétrique ou un bootstrap.

> 💡 **Intuition.** Un test de normalité sur un grand échantillon rejette presque toujours, parce qu'il détecte des écarts minuscules à la normale. Sur un petit échantillon, il ne détecte presque rien. Il répond mal à la question que l'on se pose vraiment : « *mon test $t$ est-il fiable ?* ».

### 2.4.3 Le khi-deux d'indépendance et d'ajustement

Le **khi-deux d'indépendance** teste le lien entre deux variables **catégorielles** : il compare le tableau croisé observé à celui que l'on obtiendrait si les deux variables étaient indépendantes. Exemple : le **taux de retour** dépend-il du canal de vente ?

```python
l25 = lig.merge(cmd[["id_commande", "canal", "date_commande"]], on="id_commande")
l25 = l25[l25["date_commande"] >= "2025-01-01"].assign(retour=lambda t: t["id_ligne"].isin(ret["id_ligne"]).astype(int))
tableau = pd.crosstab(l25["canal"], l25["retour"])
khi, p, ddl, _ = stats.chi2_contingency(tableau)
print(tableau.assign(taux=(tableau[1] / tableau.sum(axis=1)).round(4)).to_string())
print("khi-deux :", round(khi, 1), "| ddl :", ddl, "| p =", f"{p:.0e}", "| V de Cramér :", round(np.sqrt(khi / tableau.values.sum()), 3))
```
<!--sortie-->
```text
retour        0     1    taux
canal                        
Boutique  12192   419  0.0332
Réseaux    3060   228  0.0693
Site      12699  1229  0.0882
khi-deux : 342.5 | ddl : 2 | p = 4e-75 | V de Cramér : 0.107
```

Les taux de retour sont de **3,3 %** en Boutique, **6,9 %** sur Réseaux et **8,8 %** sur le Site. Le khi-deux (342,5, deux degrés de liberté) rejette l'indépendance avec une p-valeur de l'ordre de $10^{-75}$. Le **V de Cramér** (0,11 ici) mesure l'**intensité** du lien, entre 0 et 1 : le lien est net, mais d'intensité modeste (le canal n'explique pas tout : la catégorie de produit, le prix, la saison jouent aussi).

Le **khi-deux d'ajustement** compare une répartition **observée** à une répartition **attendue**. Les commandes de 2025 sont-elles réparties de façon uniforme sur les sept jours de la semaine ?

```python
par_jour = pd.to_datetime(cmd.loc[cmd["date_commande"] >= "2025-01-01", "date_commande"]).dt.dayofweek.value_counts().sort_index()
ajust = stats.chisquare(par_jour.values)
print("commandes par jour (lundi → dimanche) :", par_jour.values.tolist(), "| khi-deux :", round(ajust.statistic, 1), "| p =", f"{ajust.pvalue:.0e}")
```
<!--sortie-->
```text
commandes par jour (lundi → dimanche) : [1765, 1692, 1788, 1805, 2077, 2607, 1212] | khi-deux : 578.4 | p = 1e-121
```

La répartition n'est évidemment pas uniforme : le samedi (2 607 commandes) pèse plus du double du dimanche (1 212). La **vérité programmée** (samedi +40 %, dimanche −35 %) se lit dans les comptes. Le test, ici, n'apprend rien que l'œil ne voie : il devient utile quand la répartition est plus subtile, ou quand il faut **chiffrer** l'écart à une répartition de référence.

### 2.4.4 L'ANOVA et le test post hoc de Tukey

L'**ANOVA** (analyse de la variance) étend le test $t$ à **trois groupes ou plus** : elle demande si **au moins une** moyenne diffère des autres. Elle compare la variation **entre** les groupes à la variation **à l'intérieur** des groupes : si la première est grande par rapport à la seconde, les groupes diffèrent. Exemple : le **montant d'une ligne de commande** dépend-il de la catégorie de produit ?

```python
cat = l25.merge(prod[["id_produit", "categorie"]], on="id_produit")
groupes = [g["montant"] for _, g in cat.groupby("categorie")]
f = stats.f_oneway(*groupes)
print(cat.groupby("categorie")["montant"].agg(lignes="size", moyenne="mean", mediane="median").round(1).to_string())
print("ANOVA : F =", round(f.statistic, 1), "| p =", f.pvalue, "| Kruskal-Wallis p =", stats.kruskal(*groupes).pvalue)
gm = cat["montant"].mean()
print("part de variance expliquée (eta²) :", round(sum(len(g) * (g.mean() - gm) ** 2 for g in groupes) / ((cat["montant"] - gm) ** 2).sum(), 3))
```
<!--sortie-->
```text
            lignes  moyenne  mediane
categorie                           
Bien-être     3675     32.0     26.7
Cuisine       5141     45.4     40.1
Décoration    5897     43.9     30.8
Jardin        5393     65.6     55.1
Maison        5300     57.5     50.4
Papeterie     4421     12.8     10.2
ANOVA : F = 1096.0 | p = 0.0 | Kruskal-Wallis p = 0.0
part de variance expliquée (eta²) : 0.155
```

La moyenne d'une ligne va de **12,8 €** (papeterie) à **65,6 €** (jardin) ; l'ANOVA donne $F=1\,096$ et une p-valeur nulle (en pratique inférieure à $10^{-300}$), le test de Kruskal-Wallis, version sans condition de forme, aussi. Environ **16 %** de la variance des montants s'explique par la catégorie (le $\eta^2$ de l'ANOVA).

L'ANOVA dit **qu'il y a** une différence, pas **entre quels groupes**. Pour le savoir, on compare les groupes **deux à deux**, mais avec une **correction** : avec six catégories, on fait 15 comparaisons, et sans correction on aurait presque une chance sur deux d'en trouver une « significative » par hasard. Le **test de Tukey** compare toutes les paires en gardant un risque global de 5 %.

```python
from statsmodels.stats.multicomp import pairwise_tukeyhsd
tk = pairwise_tukeyhsd(cat["montant"], cat["categorie"])
tab = pd.DataFrame(tk._results_table.data[1:], columns=tk._results_table.data[0])
print("paires comparées :", len(tab), "| paires différentes à 5 % :", int(tab["reject"].sum()))
print(tab.loc[~tab["reject"], ["group1", "group2", "meandiff", "p-adj"]].to_string(index=False))
```
<!--sortie-->
```text
paires comparées : 15 | paires différentes à 5 % : 14
 group1     group2  meandiff  p-adj
Cuisine Décoration   -1.5058  0.328
```

Sur 15 paires, **14** diffèrent ; la seule paire dont la différence n'est pas démontrée est **cuisine contre décoration** (1,5 € d'écart, p = 0,33). À l'inverse, la même ANOVA sur le **panier par canal** (Boutique, Site, Réseaux) donne $F=0{,}45$ et $p=0{,}64$ : aucune différence entre canaux, et le test de Tukey ne rejette aucune paire.

```text
panier selon les trois canaux : F = 0.45 , p = 0.639 | paires rejetées par Tukey : 0
```

### 2.4.5 Mann-Whitney et Wilcoxon

Le test de **Mann-Whitney** (ou Wilcoxon-Mann-Whitney) compare **deux groupes indépendants** sans supposer de forme : il utilise les rangs. Exemple : le nombre de commandes par jour diffère-t-il entre les jours de promotion (153 jours) et les autres (943 jours) ?

```python
promo, normal = jours.loc[jours["promo_active"] == 1, "nb_commandes"], jours.loc[jours["promo_active"] == 0, "nb_commandes"]
print("moyenne :", round(promo.mean(), 1), "contre", round(normal.mean(), 1), "| médiane :", promo.median(), "contre", normal.median(), "| Mann-Whitney p =", round(stats.mannwhitneyu(promo, normal).pvalue, 3))
```
<!--sortie-->
```text
moyenne : 35.4 contre 32.8 | médiane : 31.0 contre 30.0 | Mann-Whitney p = 0.029
```

Les jours de promotion ont 35,4 commandes en moyenne contre 32,8 les autres jours (médianes 31 et 30), et le test donne $p=0{,}029$ : significatif, mais l'**écart brut** (+8 %) est bien inférieur à l'effet réel de la promotion (+18 %), parce que la promotion tombe en saison creuse (section 2.3.6). Cet exemple rappelle la limite de tout test **non apparié ni ajusté** : il compare des jours qui diffèrent aussi par la saison. Le **test de Wilcoxon** pour échantillons appariés (2.1.6) en est la version pour des mesures sur les mêmes unités.

> ✅ **À retenir.** Choisissez le test à partir de **trois questions** : quelle variable (binaire, numérique, catégorielle) ? combien de groupes ? les groupes sont-ils indépendants ou appariés ? Vérifiez ensuite l'**indépendance** des observations, la **taille** des effectifs et les **valeurs extrêmes**. La plupart des tests « robustes » donnent la même conclusion que leur version classique sur de grands échantillons : la vraie difficulté est de bien poser la question.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.7, exercice 2.12.


## 2.5 ➕ Pour aller plus loin : analyse de puissance et taille d'échantillon

Un test non significatif est ambigu : l'effet est-il absent, ou le test était-il trop petit pour le voir ? La **puissance** lève l'ambiguïté. Cette section montre comment la mesurer, comment calculer la taille d'échantillon nécessaire **avant** une expérience, et combien de temps un test A/B dure réellement avec le trafic de la boutique.

### 2.5.1 La puissance, mesurée par simulation

La puissance est la probabilité qu'un test **détecte** un effet réel d'une taille donnée. On la mesure en rejouant l'expérience : on suppose les deux taux réels, on simule des milliers d'expériences, on compte celles qui concluent. Pour le test d'e-mail (3,0 % contre 3,4 %, 6 000 par groupe), c'est ce que nous avions fait en 2.2.2. Faisons varier la taille des groupes.

```python
rng = np.random.default_rng(1)
tailles = [3000, 6000, 12000, 20000, 30000, 40000]
puiss = [O.puissance_simulee(rng, 0.030, 0.034, n) for n in tailles]
print(pd.DataFrame({"contacts par groupe": tailles, "puissance": np.round(puiss, 2)}).to_string(index=False))
```
<!--sortie-->
```text
 contacts par groupe  puissance
                3000       0.14
                6000       0.23
               12000       0.43
               20000       0.64
               30000       0.79
               40000       0.89
```

La puissance est d'environ **14 % à 3 000 contacts**, **23 % à 6 000**, **43 % à 12 000**, **64 % à 20 000**, **79 % à 30 000** et **89 % à 40 000** par groupe (le calcul exact donne 23,8 % à 6 000). La courbe, calculée cette fois par la formule, a la forme classique : elle monte vite, puis s'aplatit ; **doubler** l'échantillon ne **double** pas la puissance.


![Courbes de puissance d'un test de comparaison de deux proportions selon la taille des groupes, pour trois tailles d'effet ; la ligne pointillée horizontale marque 80 % ; le trait vertical marque la taille du test d'e-mail.](figures/ch02-puissance.png)

### 2.5.2 Les formules de taille d'échantillon

Plutôt que de simuler, on peut **calculer** la taille nécessaire. Quatre quantités sont liées : le **seuil** $\alpha$ (5 %), la **puissance** visée (80 %), la **taille de l'effet** et l'**effectif**. Fixez-en trois, la quatrième se déduit.

Pour comparer **deux proportions** $p_1$ et $p_2$, avec $z_{\alpha/2}=1{,}96$ et $z_\beta=0{,}84$ (puissance de 80 %), l'effectif par groupe est

$$n=\frac{(z_{\alpha/2}+z_\beta)^2\,\big[p_1(1-p_1)+p_2(1-p_2)\big]}{(p_2-p_1)^2}.$$

À la main, pour 3,0 % contre 3,4 % : $(1{,}96+0{,}84)^2\approx7{,}85$ ; $p_1(1-p_1)+p_2(1-p_2)=0{,}0291+0{,}0328=0{,}0619$ ; $(p_2-p_1)^2=0{,}004^2=1{,}6\times10^{-5}$ ; donc $n\approx7{,}85\times0{,}0619/1{,}6\times10^{-5}\approx$ **30 400**. Pour comparer deux **moyennes** d'écart-type commun $\sigma$ et d'écart attendu $\delta$ :

$$n=\frac{2\,\sigma^2\,(z_{\alpha/2}+z_\beta)^2}{\delta^2}.$$

Le panier moyen a un écart-type d'environ 82 € ; pour détecter une hausse de **5 €**, il faut $2\times82^2\times7{,}85/25\approx$ **4 250 commandes par groupe** ; pour détecter **10 €**, quatre fois moins (la taille varie comme **l'inverse du carré** de l'effet).

```python
sigma = cmd.loc[cmd["date_commande"] >= "2025-01-01", "panier"].std()
print("écart-type du panier :", round(sigma, 1), "€")
print("par groupe : 3,0 % → 3,4 % :", round(O.taille_deux_proportions(0.030, 0.034)), "| 3,0 % → 3,8 % :", round(O.taille_deux_proportions(0.030, 0.038)))
print("panier +5 € :", round(O.taille_deux_moyennes(5, sigma)), "| +10 € :", round(O.taille_deux_moyennes(10, sigma)))
```
<!--sortie-->
```text
écart-type du panier : 82.3 €
par groupe : 3,0 % → 3,4 % : 30387 | 3,0 % → 3,8 % : 8052
panier +5 € : 4256 | +10 € : 1064
```

Les formules de `statsmodels` (`NormalIndPower`, `TTestIndPower`) donnent des valeurs voisines (30 362 pour les proportions avec la transformation « arc-sinus », 4 257 pour les moyennes avec la loi $t$). Cette exigence a une conséquence : **un petit effet sur une petite proportion coûte très cher**. Détecter un point de conversion sur 3 % en demande des dizaines de milliers.

> 📐 **D'où vient la formule ?** La différence observée $\hat p_2-\hat p_1$ suit à peu près une loi normale centrée sur l'effet réel $\delta=p_2-p_1$, d'écart-type $\sqrt{[p_1(1-p_1)+p_2(1-p_2)]/n}$. Le test rejette $H_0$ quand cette différence dépasse $z_{\alpha/2}$ écarts-types (sous $H_0$) ; pour qu'elle le dépasse avec la probabilité $1-\beta$ quand l'effet est réel, le décalage $\delta$ doit valoir $z_{\alpha/2}+z_\beta$ écarts-types. En résolvant en $n$ on obtient la formule. On y lit que $n$ **augmente avec la variance** et **diminue avec le carré de l'effet**.

### 2.5.3 L'effet minimal détectable

On peut retourner la question : étant donné l'effectif **dont on dispose**, quel est le plus **petit effet** que l'on a 80 % de chances de détecter ? C'est l'**effet minimal détectable** (EMD). C'est le bon réflexe avant de lancer un test : si l'EMD est plus grand que ce que l'on peut raisonnablement espérer, le test est inutile.

```python
from scipy.optimize import brentq
def emd(base, n, puissance=0.8):
    return brentq(lambda p2: O.taille_deux_proportions(base, p2, puissance=puissance) - n, base + 1e-6, 0.5) - base
print("e-mail, 6 000 par groupe, base 3,0 % :", f"+{emd(0.030, 6000)*100:.2f} point", f"(soit +{emd(0.030, 6000)/0.030:.0%} en relatif)")
print("page de paiement, 19 000 par groupe, base 3,5 % :", f"+{emd(0.035, 19000)*100:.2f} point", f"(soit +{emd(0.035, 19000)/0.035:.0%} en relatif)")
```
<!--sortie-->
```text
e-mail, 6 000 par groupe, base 3,0 % : +0.94 point (soit +31% en relatif)
page de paiement, 19 000 par groupe, base 3,5 % : +0.55 point (soit +16% en relatif)
```

Le test d'e-mail ne pouvait détecter, avec 80 % de chances, qu'un effet d'**au moins 0,94 point** sur le taux d'achat (+31 % en relatif) : plus du double des 0,4 point réels. Le test de la page de paiement pouvait détecter **+0,55 point** (+16 % en relatif) : la vérité de **+0,75 point sur mobile seulement** se dilue dans l'ensemble (0,75 point sur environ 59 % de sessions mobiles fait un effet moyen d'environ **+0,45 point**, inférieur à l'EMD).

### 2.5.4 Combien de temps dure un test ? Le trafic réel

L'effectif, c'est surtout une question de **durée** : combien de jours faut-il attendre pour avoir assez de monde ? Les sessions du site en 2025 fournissent le trafic réel : environ **348 sessions par jour**, avec un taux de conversion global de **4,8 %**. Supposons un test A/B de la page de panier, partageant ce trafic en deux, avec une conversion de référence de 5 %.

```python
sess = pd.read_csv("donnees/sessions_web.csv")
par_jour = len(sess) / 365
lignes = []
for rel in (0.05, 0.10, 0.20, 0.30):
    n = O.taille_deux_proportions(0.05, 0.05 * (1 + rel))
    lignes.append([f"+{rel:.0%}", round(n), round(2 * n), round(2 * n / par_jour), round(2 * n / par_jour / 7, 1)])
print("sessions par jour :", round(par_jour), "| conversion 2025 :", round(sess["commande"].mean() * 100, 2), "%")
print(pd.DataFrame(lignes, columns=["effet relatif", "par groupe", "total", "jours", "semaines"]).to_string(index=False))
```
<!--sortie-->
```text
sessions par jour : 348 | conversion 2025 : 4.78 %
effet relatif  par groupe  total  jours  semaines
          +5%      122121 244241    702     100.3
         +10%       31231  62461    179      25.6
         +20%        8155  16310     47       6.7
         +30%        3777   7554     22       3.1
```

Pour détecter une amélioration **relative de 10 %** (de 5,0 % à 5,5 %), il faut environ **31 000 sessions par groupe**, soit 62 000 au total : **180 jours** au trafic de 2025. Pour **+20 %**, il suffit de 8 100 par groupe, donc **47 jours** (près de sept semaines). Pour **+5 %**, il faudrait près de **deux ans** (702 jours). La durée explose quand l'effet baisse : c'est la loi de l'inverse du carré. Deux conséquences pratiques : (1) un site de ce trafic ne peut tester que des **changements importants** ; (2) on laisse **tourner un nombre entier de semaines** (ici 7 au minimum) pour ne pas biaiser par le jour de la semaine.


![Durée d'un test A/B (en jours, échelle logarithmique) en fonction de l'amélioration relative à détecter, au trafic du site en 2025 ; les petits effets demandent des mois ou des années.](figures/ch02-duree-test.png)

### 2.5.5 Quand l'échantillon est limité

Si le calcul dit « 180 jours » et que l'on n'a pas six mois, il reste cinq options, aucune n'est gratuite.

1. **Viser un effet plus grand** : tester un changement plus radical (une refonte complète plutôt qu'un détail de couleur). C'est souvent la meilleure option.
2. **Changer de métrique** : une métrique plus fréquente ou moins variable (le clic plutôt que l'achat, l'ajout au panier plutôt que la commande) demande moins de monde, mais ne mesure plus exactement ce que l'on cherche : il faut qu'elle soit **liée** au résultat final.
3. **Réduire la variance** : comparer des mesures **avant et après** sur les mêmes personnes, ou ajuster sur des variables connues (la méthode dite *CUPED* en est une version), ce qui réduit le bruit sans toucher à l'effet.
4. **Accepter une puissance plus faible** et le dire : un test de 40 % de puissance ne tranche presque jamais, mais ses intervalles de confiance restent des informations utiles à combiner avec d'autres tests.
5. **Ne pas tester** : si l'on ne peut pas détecter l'effet, décider sur d'autres bases (coût, risque, cohérence avec d'autres tests) et ne pas habiller la décision d'un test sans puissance.

> ✅ **À retenir.** Calculez **avant** l'expérience : l'effet minimal qui compterait pour l'entreprise, la taille et la durée correspondantes. Si l'on ne peut pas les atteindre, ne lancez pas le test. Un test sous-dimensionné n'est pas « un test un peu moins précis » : c'est un test qui, presque toujours, **ne répond pas**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.8, exercices 2.13 et 2.14.


## Bilan du chapitre 2

Vous savez maintenant :

- **formuler un test** : une hypothèse nulle et une alternative, une statistique, une p-valeur lue correctement (la probabilité d'un écart au moins aussi grand **si rien ne se passait**), un seuil fixé à l'avance, deux erreurs possibles (type I, type II), et un **intervalle de confiance** pour dire la taille de l'effet ;
- **éviter les cinq contresens** sur la p-valeur, et ne jamais confondre **significatif** et **important**, ni **non significatif** et **absent** ;
- **choisir un test** selon la variable, le nombre de groupes et l'indépendance des observations : deux proportions ($z$, khi-deux, Fisher), deux moyennes (Welch), distributions asymétriques (Mann-Whitney, bootstrap), mesures appariées (t apparié, Wilcoxon), plusieurs groupes (ANOVA, Tukey, Kruskal-Wallis), répartitions (khi-deux) ;
- **concevoir un test A/B** : unité tirée au sort, métrique principale, garde-fous, taille et durée fixées à l'avance, règle de décision ; **lire** un test en commençant par la **répartition** (défaut de répartition), puis l'écart global et son intervalle, puis les sous-groupes **corrigés** (Holm) ;
- **repérer les pièges** : regarder en continu (un test sans effet « gagne » dans un cas sur quatre), comparer plusieurs sous-groupes, effet de nouveauté, interférences ;
- **mesurer une corrélation** (Pearson, Spearman, Kendall), son intervalle (transformation de Fisher), et la **neutraliser** quand une saison ou une tendance la fabrique ; ne pas conclure à la cause sans expérience ;
- (en option) **calculer la puissance** d'un test, la **taille d'échantillon** nécessaire, l'**effet minimal détectable** et la **durée** d'un test avec le trafic réel.

Voici ce que le chapitre a mesuré, avec la **vérité programmée** quand elle existe.

| Question | Ce que l'analyse a donné | Vérité programmée |
|---|---|---|
| E-mail : l'objet B augmente-t-il l'achat ? | +0,47 point (IC −0,16 à +1,09), $p=0{,}14$ : non conclusif | +0,4 point réel : **puissance de 24 %**, 30 400 par groupe auraient fallu |
| E-mail : ouverture, clic | +4,27 et +1,00 point, très significatifs | effet réel sur l'ouverture, répercuté sur le clic |
| Montant par contact | +0,37 € (IC −0,39 à +1,10 €) : pas de conclusion ; 1 % des contacts font 60 % des euros | pas d'effet sur le panier des acheteurs |
| Page de paiement : répartition 50/50 ? | 48,1 % de B, $\chi^2=56$ : **défaut de répartition** | filtre de robots appliqué au seul groupe B (−20 % d'ordinateurs) |
| Page de paiement : effet par appareil | mobile +0,57 pt, $p=0{,}025$, **0,075 après Holm** | +0,75 pt sur mobile, 0 ailleurs : effet réel, non démontrable |
| Regarder chaque jour un test A/A | environ 1 test sur 4 « gagne » au moins un jour | aucun effet |
| Publicité × commandes | corrélation 0,53, **0,11 à mois égal** ; coefficient contrôlé 0,006 (IC −0,0004 à +0,0124) | +1,5 % pour 1 000 € hebdomadaires, soit 0,0035 : dans l'intervalle |
| Promotion × commandes | corrélation brute avec le CA −0,01 ; effet contrôlé +19 % | +18 % |
| Séries temporelles indépendantes | 41 % des paires avec $|r|>0{,}5$ ; presque aucune sur les variations | aucun lien |

Quatre idées dépassent ce chapitre. **Un test se prépare avant de se lire** : l'effet qui compte, la taille nécessaire et la règle de décision s'écrivent avant le lancement. **L'intervalle de confiance est plus informatif que la p-valeur** : il donne la taille et l'incertitude. **Regarder souvent, comparer beaucoup, s'arrêter tôt** multiplient les faux positifs : fixez le plan d'analyse à l'avance. **Une corrélation est une question** : la saison, la tendance et la sélection la fabriquent facilement ; seule une expérience tranche. Le chapitre 3 prolonge la dernière idée : la **régression** permet de comparer « toutes choses égales par ailleurs » quand l'expérience est impossible.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 à 2.8 (mélange des étiquettes, lecture d'un test d'e-mail, défaut de répartition et sous-groupes, arrêt prématuré, corrélation à saison égale, séries à tendance, choix d'un test, taille et durée d'un test) et exercices 2.1 à 2.14.
