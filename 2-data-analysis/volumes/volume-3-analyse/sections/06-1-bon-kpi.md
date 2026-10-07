## 6.1 Ce qui fait un bon KPI

Un indicateur est un **chiffre au service d'une décision**. Cette section pose les critères d'un bon KPI, calcule ceux de la boutique, puis passe aux pièges : ceux du calcul (un même mot, plusieurs formules) et ceux de l'usage (un indicateur que l'on cible cesse souvent d'être un bon indicateur).

### 6.1.1 Un chiffre, une décision

Reprenons les quarante chiffres de la gérante. Pour chacun, une seule question : **« si ce chiffre sort de sa zone normale, que fait-on ? »** Trois réponses possibles.

- **« On change quelque chose. »** C'est un indicateur de pilotage : le taux de livraisons à l'heure baisse, on appelle le transporteur ; le taux de rupture monte, on commande plus tôt.
- **« On le sait, c'est tout. »** C'est un chiffre de contexte (le nombre de lignes de commande de la semaine) : utile pour interpréter les autres, inutile à suivre seul.
- **« On ne sait pas. »** C'est un chiffre à supprimer du tableau, ou à relier à une décision avant de le garder.

Un KPI est donc défini par un **trio** : un chiffre, **une personne qui peut agir**, **une action possible**. Sans l'un des trois, on a une statistique, pas un indicateur.

On distingue aussi deux familles.

| Famille | Question posée | Exemple pour la boutique | Défaut |
|---|---|---|---|
| **Résultat** (retardé) | Qu'avons-nous obtenu ? | chiffre d'affaires, marge, clients actifs | arrive **trop tard** pour corriger |
| **Pilotage** (avancé) | Où va-t-on, et que peut-on encore changer ? | visites du site, ajouts au panier, délai d'expédition, ruptures | **moins parlant** pour la direction |

Les indicateurs de résultat disent si l'on a gagné ; ceux de pilotage disent **pourquoi** et **à temps**. La gérante avait besoin d'un indicateur de pilotage : le taux de livraisons à l'heure aurait signalé le problème en une semaine, pas en trois.

#### De quarante à dix : un tri en pratique

Pour trier les quarante chiffres de la gérante, on les passe un par un dans les trois questions ci-dessus. Voici le résultat sur douze d'entre eux, qui donne le **ton** du tri.

| Chiffre reçu le lundi | Décision liée ? | Verdict |
|---|---|---|
| Chiffre d'affaires de la semaine | revue mensuelle de la trajectoire | **garder** (résultat) |
| Livraisons à l'heure de la semaine | appeler le transporteur | **garder** (pilotage) |
| Taux de rupture des 20 produits principaux | passer commande plus tôt | **garder** (pilotage) |
| Taux de retour de la semaine | corriger une fiche produit ou un fournisseur | **garder** (pilotage) |
| Conversion du site | revoir le parcours d'achat | **garder** (pilotage) |
| Nombre de lignes de commande | aucune seule | **supprimer** (le contexte est dans le panier moyen) |
| CA du mardi, du mercredi, du jeudi… | aucune : le bruit quotidien est trop fort | **regrouper** en semaine |
| Stock de chaque produit (120 lignes) | commande de réapprovisionnement | **sortir du tableau de bord** vers un état de gestion, ne garder que le taux de rupture |
| Pages vues du site | aucune seule | **supprimer** |
| Nombre de clients inscrits | aucune seule | **remplacer** par les clients actifs |
| Dépense publicitaire | arbitrage budgétaire | **garder**, avec le coût par commande (chapitre 10) |
| Part du site dans le CA | stratégie de canal | **garder** (contexte stratégique, trimestriel) |

On passe de quarante à une dizaine, **sans perdre une seule décision**. Notez que le tri est aussi une question de **fréquence** : le même indicateur peut être hebdomadaire pour un responsable et trimestriel pour la direction.

> ✅ **À retenir.** Pour chaque chiffre : **quelle décision, qui la prend, quand**. Un tableau de bord utile mélange quelques indicateurs de résultat et surtout des indicateurs de pilotage qui les annoncent.

### 6.1.2 La définition écrite : la fiche d'un KPI

Deux personnes qui parlent du « taux de retour » ne parlent pas forcément de la même chose : retours sur lignes vendues ? sur commandes ? sur chiffre d'affaires ? comptés à la date de vente ou à la date de retour ? Pour que le chiffre de mars soit comparable à celui d'avril, et celui de la boutique à celui du secteur, la définition doit être **écrite** une fois pour toutes. Voici la fiche minimale.

| Rubrique | Exemple : « taux de retour » |
|---|---|
| **Nom** | Taux de retour (lignes) |
| **Décision liée** | Corriger la qualité ou la description d'un produit, négocier avec un fournisseur |
| **Formule** | lignes de commande retournées ÷ lignes de commande vendues |
| **Périmètre** | tous canaux ; ventes de la période (même si le retour arrive plus tard) |
| **Période et date de référence** | semaine ou mois **de la vente** |
| **Source** | tables `lignes_commande` et `retours` |
| **Propriétaire** | la responsable des achats |
| **Fréquence** | hebdomadaire |
| **Sens favorable** | à la baisse |
| **Limites connues** | les retours de la fin de période arrivent en retard : la valeur est **sous-estimée** pendant trois semaines |

Cette fiche a l'air administrative ; c'est la première défense contre les disputes de chiffres. Nous reconstruirons une fiche complète pour chaque indicateur du tableau de bord en section 6.3.6.

### 6.1.3 Les critères d'un bon indicateur

Une liste courte suffit à tester un indicateur. Il doit être :

1. **lié à une décision**, comme on vient de le voir ;
2. **mesurable** de façon fiable, avec des données disponibles à la fréquence voulue ;
3. **comparable** dans le temps (même définition d'une période à l'autre) et avec une référence (un budget, l'année précédente, le secteur) ;
4. **compréhensible** par ceux qui l'utilisent, sans mode d'emploi ;
5. **actionnable** : une personne précise peut agir dessus ;
6. **difficile à truquer** : améliorer le chiffre doit vouloir dire améliorer la réalité (nous y revenons en 6.1.6).

On connaît aussi le moyen mnémotechnique **SMART** (spécifique, mesurable, atteignable, réaliste, temporel) ; il décrit surtout une **cible** (section 6.3), pas un indicateur. Retenez plutôt les six questions ci-dessus.

Deux précisions de vocabulaire servent tout le temps.

**Taux ou volume ?** Un **volume** (le nombre de commandes) augmente avec la taille de l'entreprise, la saison, la publicité ; un **taux** (la part de commandes qui se concluent, le taux de retour) la **normalise**. Pour piloter la qualité, on préfère un taux ; pour piloter la taille, un volume. Dans les deux cas, on regarde toujours **le dénominateur** : un taux qui monte parce que le dénominateur s'effondre ne signale pas une amélioration.

**Valeur absolue ou relative ?** Une hausse de 5 % du chiffre d'affaires n'a pas le même sens si le secteur croît de 10 % ou recule de 3 %. D'où la nécessité de références (section 6.3).

### 6.1.4 Calculer les indicateurs de la boutique, une seule fois

Passons aux données. La règle d'or de la mise en place d'un tableau de bord : **chaque indicateur est calculé par une seule fonction**, que tout le monde utilise. Sinon, le même nom recouvre deux formules et les chiffres divergent. Notre fonction `kpis` renvoie, pour une année, les indicateurs de la boutique (elle est écrite dans `build/outils_ch06.py` ; son code se lit en un coup d'œil, et les formules sont celles de la fiche de 6.1.2). Voici d'abord le « cœur » : les six indicateurs disponibles pour 2024 et 2025.

```python
coeur = ["CA TTC (€)", "Commandes", "Panier moyen (€)", "Taux de marge brute (HT, %)", "Taux de retour (lignes, %)", "Part du site dans le CA (%)"]
print(pd.DataFrame({"2024": pd.Series(k24), "2025": pd.Series(k25)}).loc[coeur].round(2).to_string())
```
<!--sortie-->
```text
                                   2024        2025
CA TTC (€)                   1189461.17  1324763.72
Commandes                      12031.00    12946.00
Panier moyen (€)                  98.87      102.33
Taux de marge brute (HT, %)       36.17       37.96
Taux de retour (lignes, %)         5.83        6.29
Part du site dans le CA (%)       42.25       46.63
```

Le chiffre d'affaires progresse de 11,4 % ; les commandes, de 7,6 % ; le panier moyen, de 3,5 % ; la marge gagne 1,8 point. Le **taux de retour**, lui, monte de 0,5 point : la croissance n'est pas gratuite. Six autres indicateurs ne sont calculables que pour 2025 (les sessions du site et les stocks ne remontent pas plus loin).

```python
autres = [c for c in k25 if c not in coeur]
print(pd.Series({c: k25[c] for c in autres}).round(2).to_string())
```
<!--sortie-->
```text
Taux de conversion du site (%)         4.78
Livraisons à l'heure (%)              73.47
Taux de rupture de stock (%)           7.36
Clients actifs sur 12 mois (%)        64.58
Coût d'acquisition d'un client (€)    98.58
Frais de personnel / CA HT (%)        12.78
Rotation du stock (par an)             4.23
```

Un chiffre isolé ne dit encore rien : **73 % de livraisons à l'heure**, est-ce bon ? Cela dépend de la référence (section 6.3). Notez aussi que chaque ligne cache une définition : les « clients actifs sur 12 mois » sont les clients ayant au moins une commande en 2025, rapportés aux 6 000 clients de la base ; le « coût d'acquisition » rapporte les dépenses de marketing de 2025 au nombre de clients dont la **première commande** date de 2025. Avec une autre définition (par exemple le nombre de clients inscrits dans l'année), le chiffre changerait. **Un indicateur n'existe qu'avec sa fiche.**

> 🧪 **Remarque.** Plusieurs de ces chiffres sont des **ratios de deux sommes** (la marge sur le chiffre d'affaires, les retours sur les lignes). On les calcule toujours par `somme(numérateur) ÷ somme(dénominateur)` sur la période entière, jamais en moyennant des taux déjà calculés : c'est le premier piège de la section suivante.

### 6.1.5 Les pièges de calcul

Ces pièges sont **silencieux** : le chiffre est faux, mais il a l'air raisonnable.

#### La moyenne des moyennes

Un taux global n'est pas la moyenne des taux de ses morceaux, sauf si les morceaux ont la même taille. Un exemple à la main : deux canaux. Le premier a 100 commandes et 10 % de retours ; le second, 900 commandes et 2 % de retours. La moyenne des deux taux vaut $(10+2)/2=6\ \%$ ; le taux global vaut $(100\times0{,}10+900\times0{,}02)/1\,000=2{,}8\ \%$. Plus de deux fois moins. Il faut **pondérer** par le dénominateur, c'est-à-dire repartir des sommes. Sur nos données, les trois canaux ont des taux de retour de 3,3 %, 6,9 % et 8,8 % pour des effectifs très différents ; leur moyenne simple (6,36 %) s'écarte du taux global (6,29 %).

```python hide
x25 = d["x"][d["x"]["annee"] == 2025]
rc = x25.groupby("canal")["retourne"].agg(["mean", "size"])
assert round((10 + 2) / 2, 1) == 6.0 and round((100 * 0.10 + 900 * 0.02) / 1000 * 100, 1) == 2.8
assert round(rc["mean"].mean() * 100, 2) == 6.36 and round(x25["retourne"].mean() * 100, 2) == 6.29
assert [round(v * 100, 1) for v in rc["mean"]] == [3.3, 6.9, 8.8]
```

#### Un mot, trois formules

« Le taux de retour » peut se calculer de trois façons. Comparons-les sur 2025.

```python
cmd_ret = x25.groupby("id_commande")["retourne"].max()
print("sur les lignes :", round(x25["retourne"].mean() * 100, 2), "%")
print("sur les commandes (au moins un retour) :", round(cmd_ret.mean() * 100, 2), "%")
print("en euros (ventes retournées / ventes) :", round(x25.loc[x25["retourne"], "montant"].sum() / x25["montant"].sum() * 100, 2), "%")
```
<!--sortie-->
```text
sur les lignes : 6.29 %
sur les commandes (au moins un retour) : 13.64 %
en euros (ventes retournées / ventes) : 6.38 %
```

Les deux premiers chiffres diffèrent d'un **facteur deux** parce que le dénominateur change (une commande compte plusieurs lignes). Aucune des trois définitions n'est fausse ; une seule doit être **la** définition du KPI, et celle du secteur doit être la même pour que la comparaison ait un sens.

#### Les périodes qui ne se superposent pas

Un retour arrive quelques jours **après** la vente. Si l'on rapporte les retours **enregistrés** en décembre aux ventes de décembre, on mélange deux populations. Les ventes de décembre 2025 ont 6,76 % de lignes retournées (en rapportant chaque retour à sa vente) ; les retours **enregistrés** en décembre, rapportés aux lignes vendues en décembre, donnent 6,46 %. Et 101 retours de ventes de 2025 sont **datés de 2026** : un indicateur calculé au 31 décembre est incomplet. D'où la mention « sous-estimé pendant trois semaines » dans la fiche, et la règle : on **date l'indicateur par la vente**, on laisse mûrir la période.

```python hide
dec = d["x"][d["x"]["mois"] == "2025-12"]
r = d["ret"].merge(d["x"][["id_ligne", "date_commande"]], on="id_ligne")
assert round(dec["retourne"].mean() * 100, 2) == 6.76
assert len(d["ret"][(d["ret"]["date_retour"] >= "2025-12-01") & (d["ret"]["date_retour"] <= "2025-12-31")]) == 275 and len(dec) == 4259
assert round(275 / 4259 * 100, 2) == 6.46
assert int(((r["date_retour"] >= "2026-01-01") & (r["date_commande"] >= "2025-01-01")).sum()) == 101
```

#### Les petits effectifs

Un taux calculé sur peu d'observations est **instable** : une seule ligne déplace le chiffre. À la main, pour un taux de livraisons à l'heure de 78 %, l'incertitude d'une semaine vaut $\sqrt{0{,}78\times0{,}22/n}$ : environ 5,9 points pour 50 commandes, 3,6 points pour 134 et 1,9 point pour 500. Un tableau de bord par **point de livraison** ou par **produit** (quelques dizaines de commandes par semaine) fait donc osciller des taux qui ne signifient rien. La parade est de **regrouper** (par mois, par famille de produits) ou d'afficher l'**effectif** à côté du taux ; nous en ferons une règle au moment des seuils (6.3.5).

```python hide
for n_, att in [(50, 5.9), (134, 3.6), (500, 1.9)]:
    assert round(float(np.sqrt(0.78 * 0.22 / n_)) * 100, 1) == att
```

#### Le cumul qui cache la tendance

Un indicateur **cumulé** depuis le début de l'année (le chiffre d'affaires de janvier à ce jour) ne peut que monter : il est « positif » en permanence et n'alerte jamais. Une tendance se lit sur des **périodes séparées** (la semaine, le mois) ou en **glissant** (les 12 derniers mois). Le cumul sert à comparer à un budget annuel, pas à détecter un problème.

> ⚠️ **Piège.** Avant de comparer deux valeurs d'un KPI, vérifiez trois choses : **même formule**, **même dénominateur**, **même période**. Une grande partie des « évolutions » spectaculaires viennent d'un changement de définition, comme la bascule en centimes du site au volume II.

### 6.1.6 Quand le KPI devient la cible : la loi de Goodhart

Il y a un piège plus sournois : l'**usage**. L'économiste Charles Goodhart a énoncé, sous une forme plus technique, une idée que l'on résume aujourd'hui ainsi : *quand une mesure devient un objectif, elle cesse d'être une bonne mesure.* Dès que l'on récompense un chiffre, on optimise le chiffre, parfois aux dépens de ce qu'il était censé représenter. Trois exemples avec nos données.

**Le nombre de commandes et la promotion.** La gérante veut « plus de commandes » : on lance des promotions. Comparons les jours de promotion (soldes et vendredi noir) aux autres jours.

```python
j = d["jours"].set_index("date").join(d["x"].groupby("date_commande").agg(marge=("marge_ht", "sum"), n=("id_commande", "nunique")))
g = j.groupby("promo_active")[["n", "marge"]].mean().round(1)
print(g.rename(index={0: "autres jours", 1: "jours de promotion"}, columns={"n": "commandes/jour", "marge": "marge HT/jour (€)"}))
```
<!--sortie-->
```text
                    commandes/jour  marge HT/jour (€)
promo_active                                         
autres jours                  32.8             1053.9
jours de promotion            35.4              836.4
```

Les jours de promotion, il y a **8 % de commandes en plus** mais **21 % de marge en moins** : le taux de marge tombe de 37,9 % à 30,4 %. Si l'on récompense le nombre de commandes, on choisit la promotion ; l'entreprise s'appauvrit. (Ces jours ne sont pas ordinaires : ils tombent en janvier, en juin et juillet, en novembre. La comparaison est descriptive ; mesurer l'effet *causal* d'une promotion demande les méthodes du chapitre 2.)

**Le panier moyen et un seuil minimal.** Pour « faire monter le panier moyen », on peut supprimer les petites commandes (livraison minimale à 40 €, par exemple) : l'indicateur monte, mécaniquement.

```python
op = x25.groupby("id_commande")["montant"].sum()
gros = op[op >= 40]
print("commandes sous 40 € :", round((op < 40).mean() * 100, 1), "% | panier moyen :", round(op.mean(), 2), "->", round(gros.mean(), 2), "| CA :", round((gros.sum() / op.sum() - 1) * 100, 1), "%")
```
<!--sortie-->
```text
commandes sous 40 € : 22.3 % | panier moyen : 102.33 -> 125.02 | CA : -5.1 %
```

Le panier moyen **bondit de 22 %**, le chiffre d'affaires **recule de 5 %** : on a gagné l'indicateur et perdu de l'argent.

**La conversion et un trafic de mauvaise qualité.** La conversion mesure la part de sessions qui aboutissent à une commande. Si l'on achète beaucoup de trafic « réseaux » (2,2 % de conversion), les commandes augmentent mais la conversion baisse ; si l'on évalue l'équipe sur la conversion, elle n'achètera plus ce trafic, même rentable. Simulons 20 000 sessions « réseaux » de plus, converties comme les sessions actuelles de ce canal.

```python
s = d["sess"]; C, N = s["commande"].sum(), len(s); cr = s.loc[s["source"] == "reseaux", "commande"].mean()
apres = (C + 20000 * cr) / (N + 20000)
print("conversion :", round(C / N * 100, 2), "% ->", round(apres * 100, 2), "% | commandes :", C, "->", round(C + 20000 * cr))
```
<!--sortie-->
```text
conversion : 4.78 % -> 4.43 % | commandes : 6078 -> 6510
```

La conversion **baisse de 7 %** alors que les commandes **augmentent de 7 %**. Aucun de ces deux chiffres, seul, ne dit s'il fallait acheter ce trafic : il faut le **coût par commande** et la marge (chapitre 10).

![Trois indicateurs qui deviennent des objectifs : à chaque fois, le chiffre ciblé (en bleu) s'améliore alors que ce qu'il devait représenter (en orange) se dégrade. Indices, 100 = situation de référence.](figures/ch06-goodhart.png)

```python hide
O.fig_goodhart(d)
ind = O.indices_goodhart(d)
assert [round(v) for v in ind["promo"]] == [108, 79] and [round(v) for v in ind["seuil"]] == [122, 95] and [round(v) for v in ind["trafic"]] == [107, 93]
assert round(g.loc[1, "n"] / g.loc[0, "n"] - 1, 3) == 0.079 or round(g.loc[1, "n"] / g.loc[0, "n"] - 1, 2) == 0.08
assert round(1 - g.loc[1, "marge"] / g.loc[0, "marge"], 2) == 0.21
```
<!--sortie-->
```text
figure : ch06-goodhart.png
```

Que faire contre ce phénomène ? Trois habitudes.

1. **Associer à chaque KPI un contre-indicateur.** Les commandes avec la marge, le panier moyen avec le chiffre d'affaires, la conversion avec le nombre de commandes. L'effet pervers apparaît dès que les deux divergent.
2. **Cibler un résultat, pas un moyen.** « Augmenter la marge totale » plutôt que « le nombre de commandes ».
3. **Regarder la distribution, pas seulement la moyenne.** Un panier moyen qui monte parce que les petits paniers disparaissent se voit dans l'histogramme.

> ✅ **À retenir.** Un bon KPI est **défini par écrit**, **comparable**, **actionnable** et **accompagné d'un contre-indicateur**. Les pièges de calcul (moyenne de moyennes, dénominateur, période) font mentir un chiffre ; les pièges d'usage (Goodhart) le font mentir **une fois qu'il est ciblé**. La section 6.2 apprend à décomposer un chiffre pour savoir quoi regarder quand il bouge.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.1 et 6.2, exercices 6.1 à 6.5.
