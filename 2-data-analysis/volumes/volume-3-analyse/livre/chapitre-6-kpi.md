# Chapitre 6 : Conception de KPI et cadres d'indicateurs

> « Ce qui se mesure se pilote, à condition de savoir ce que l'on mesure et pourquoi. »


Un lundi de janvier, la gérante pousse la porte de votre bureau avec une pile de feuilles. « Chaque lundi, je reçois **quarante chiffres** : le chiffre d'affaires par jour, par canal, par catégorie, le nombre de visites, le nombre de retours, le stock de chaque produit, les délais de livraison… J'y passe une heure, je ne sais plus ce qui compte, et la semaine dernière j'ai découvert un problème de livraison **trois semaines après** qu'il a commencé. **Lesquels dois-je suivre ?** »

C'est l'une des questions les plus fréquentes d'un analyste, et l'une des plus mal posées : on croit demander une liste, alors qu'on demande **une façon de décider**. Un chiffre n'est un indicateur que s'il fait agir. Les chapitres précédents de ce volume vous ont appris à **explorer**, à **tester**, à **expliquer** et à **prévoir** ; celui-ci vous apprend à **choisir ce que l'on regarde, chaque semaine, et à quelle condition on peut s'y fier**.

## Le chemin de ce chapitre

Le chapitre suit la question de la gérante, de la définition d'un chiffre à la lecture de ses variations.

- **6.1 Ce qui fait un bon KPI.** Un KPI (*key performance indicator*, indicateur clé de performance) est un chiffre **lié à une décision**, **défini par écrit** et **difficile à truquer**. Nous calculons une douzaine d'indicateurs de la boutique, par un seul code, et nous débusquons les pièges de calcul et les effets pervers : ce qui arrive quand le chiffre devient un objectif.
- **6.2 Arbres d'indicateurs et cadres de référence.** Un chiffre global (le chiffre d'affaires) se **décompose** en facteurs (trafic, conversion, panier) : l'arbre dit **où chercher** quand le chiffre bouge. Nous comparons aussi les grands cadres de référence (tableau de bord équilibré, AARRR, OKR, *North Star*) en gardant l'esprit critique.
- **6.3 Cibles, références et seuils.** Un chiffre sans point de comparaison ne dit rien. Nous voyons de quoi une cible est faite, quelles références utiliser (année précédente, budget, secteur), comment tracer des **seuils d'alerte** fondés sur la variabilité réelle, et comment distinguer **le bruit du signal**.

Le chapitre se termine par un **tableau de bord d'une page** et un **dictionnaire des KPI** que la gérante peut lire en cinq minutes.

> 💡 **Intuition.** Un tableau de bord n'est pas un album de photos des données : c'est un **instrument de bord**. Un pilote ne regarde pas tous les cadrans en permanence ; il en suit quelques-uns, dont il connaît les valeurs normales, et il sait ce qu'il fera si l'un d'eux sort de la zone.

## Les données du chapitre

Nous reprenons la boutique des chapitres précédents (volume I, et volume III, chapitre 1). Tout est **simulé**, et la vérité programmée est connue (docstring de `build/donnees_a3.py`) ; nous la révélons quand elle éclaire un indicateur.

> 📦 **Les données.** `commandes.csv` et `lignes_commande.csv` (2023 à 2025), `produits.csv`, `retours.csv`, `clients.csv`, `jours_exploitation.csv`, `sessions_web.csv` (127 022 sessions du site en 2025), `livraisons.csv`, `stock_quotidien.csv` (20 produits en 2025), `budget_reel_2025.csv`, `compte_resultat_mensuel.csv`, `bilan_annuel.csv` et `benchmark_secteur.csv` (médiane et quartiles **fictifs** du secteur). La TVA est fixée à 20 % **pour l'illustration**.

Toutes les données ne couvrent pas les mêmes périodes : les sessions du site et les stocks ne sont disponibles que pour **2025**, alors que les commandes remontent à 2023. Quand un indicateur n'existe que pour 2025, nous le dirons ; c'est déjà une leçon de ce chapitre : **un indicateur qui n'a pas d'historique ne peut pas être comparé**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.1 à 6.6 et exercices 6.1 à 6.12 ; chacun renvoie à la section du livre qui l'éclaire.


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


#### Les petits effectifs

Un taux calculé sur peu d'observations est **instable** : une seule ligne déplace le chiffre. À la main, pour un taux de livraisons à l'heure de 78 %, l'incertitude d'une semaine vaut $\sqrt{0{,}78\times0{,}22/n}$ : environ 5,9 points pour 50 commandes, 3,6 points pour 134 et 1,9 point pour 500. Un tableau de bord par **point de livraison** ou par **produit** (quelques dizaines de commandes par semaine) fait donc osciller des taux qui ne signifient rien. La parade est de **regrouper** (par mois, par famille de produits) ou d'afficher l'**effectif** à côté du taux ; nous en ferons une règle au moment des seuils (6.3.5).


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


Que faire contre ce phénomène ? Trois habitudes.

1. **Associer à chaque KPI un contre-indicateur.** Les commandes avec la marge, le panier moyen avec le chiffre d'affaires, la conversion avec le nombre de commandes. L'effet pervers apparaît dès que les deux divergent.
2. **Cibler un résultat, pas un moyen.** « Augmenter la marge totale » plutôt que « le nombre de commandes ».
3. **Regarder la distribution, pas seulement la moyenne.** Un panier moyen qui monte parce que les petits paniers disparaissent se voit dans l'histogramme.

> ✅ **À retenir.** Un bon KPI est **défini par écrit**, **comparable**, **actionnable** et **accompagné d'un contre-indicateur**. Les pièges de calcul (moyenne de moyennes, dénominateur, période) font mentir un chiffre ; les pièges d'usage (Goodhart) le font mentir **une fois qu'il est ciblé**. La section 6.2 apprend à décomposer un chiffre pour savoir quoi regarder quand il bouge.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.1 et 6.2, exercices 6.1 à 6.5.


## 6.2 Arbres d'indicateurs et cadres de référence

Un chiffre global (le chiffre d'affaires, la marge) bouge pour **plusieurs raisons à la fois**. Un **arbre d'indicateurs** le décompose en facteurs plus simples : quand le chiffre varie, l'arbre indique **dans quelle branche chercher**. Cette section construit les arbres de la boutique, puis passe en revue les grands cadres de référence, qui sont des façons d'organiser plusieurs arbres.

### 6.2.1 Un arbre multiplicatif : sessions × conversion × panier

La première décomposition classique du commerce en ligne : le chiffre d'affaires du site est le **produit** de trois facteurs.

$$\text{CA du site}=\underbrace{\text{sessions}}_{\text{le trafic}}\times\underbrace{\frac{\text{commandes}}{\text{sessions}}}_{\text{la conversion}}\times\underbrace{\frac{\text{CA}}{\text{commandes}}}_{\text{le panier moyen}}.$$

C'est une **identité** : en simplifiant les fractions, le produit redonne le chiffre d'affaires, à l'euro près. Vérifions-la sur les données de 2025.

```python
site = x25[x25["canal"] == "Site"]
sessions, commandes, ca = len(d["sess"]), site["id_commande"].nunique(), site["montant"].sum()
conversion, panier = commandes / sessions, ca / commandes
print("sessions :", sessions, "| conversion :", round(conversion * 100, 3), "% | panier :", round(panier, 2), "€")
print("produit :", round(sessions * conversion * panier, 2), "€ | CA du site :", round(ca, 2), "€")
```
<!--sortie-->
```text
sessions : 127022 | conversion : 4.785 % | panier : 101.63 €
produit : 617715.45 € | CA du site : 617715.45 €
```

L'égalité est exacte, comme elle doit l'être. Chaque facteur correspond à **une famille d'actions** et à **une équipe** : le trafic relève de l'acquisition (publicité, référencement, e-mail), la conversion de l'ergonomie du site et de l'offre, le panier moyen de l'assortiment, des prix et des ventes associées. Quand le chiffre d'affaires baisse, on ne demande plus « pourquoi ? » mais **« lequel des trois facteurs a baissé ? »**.

![L'arbre du chiffre d'affaires du site en 2025 : trois facteurs dont le produit redonne exactement le chiffre d'affaires. Le trafic est lui-même une somme (arbre additif) de sources.](figures/ch06-arbre-ca.png)


Le facteur « sessions » se décompose à son tour, mais **additivement** : le trafic total est la somme des sources (organique 34 %, direct 28 %, payant 14 %, réseaux 12 %, e-mail 7 %, référent 5 %). Les arbres mélangent ainsi **produits** (qui se lisent en pourcentages de variation) et **sommes** (qui se lisent en contributions en euros).

### 6.2.2 Des arbres additifs, et l'arbre de la marge

Un arbre **additif** découpe un total en parts qui s'ajoutent : le chiffre d'affaires par canal, par catégorie, par mois. Sa règle de lecture est simple : la variation du total est la **somme des variations** des branches. Voici l'évolution 2024-2025 par canal.

```python
x24 = d["x"][d["x"]["annee"] == 2024]
t = pd.concat([x24.groupby("canal")["montant"].sum().rename("2024"), x25.groupby("canal")["montant"].sum().rename("2025")], axis=1)
t["écart (€)"] = t["2025"] - t["2024"]; t["part de l'écart"] = (t["écart (€)"] / t["écart (€)"].sum() * 100).round(0)
print(t.round(0).astype(int).to_string())
print("total :", int(t["écart (€)"].sum()), "€")
```
<!--sortie-->
```text
            2024    2025  écart (€)  part de l'écart
canal                                               
Boutique  558143  560974       2831                2
Réseaux   128787  146074      17287               13
Site      502531  617715     115184               85
total : 135302 €
```

(Le tableau se lit sans calcul : le **site** explique 85 % de la hausse du chiffre d'affaires, la boutique presque rien.)


Par catégorie, la hausse vient surtout du **Jardin** (+44 245 €) et de la **Maison** (+36 014 €), puis de la Décoration (+23 669 €), de la Cuisine (+16 127 €), du Bien-être (+10 193 €) et de la Papeterie (+5 054 €).

Le même exercice vaut pour la **marge** : une marge est un produit de trois facteurs, comme le chiffre d'affaires.

$$\text{marge brute}=\text{commandes}\times\underbrace{\text{panier moyen hors taxe}}_{\text{prix}\times\text{mix}}\times\text{taux de marge}.$$

En 2025, les 12 946 commandes, un panier moyen hors taxe de 85,27 € et un taux de marge de 37,96 % redonnent la marge brute de 419 017 € (identité à vérifier dans le cahier, application 6.2). Comme pour le site, on sait maintenant que la marge peut bouger parce qu'on vend **plus** (commandes), **plus cher** (panier), ou **mieux** (taux de marge, c'est-à-dire le mix de produits et les remises).

Appliquons la même logique à l'**écart de marge** entre 2024 et 2025. Trois facteurs, trois effets : on valorise chaque effet en remplaçant les facteurs un par un de l'année 2024 à l'année 2025, dans l'ordre (commandes, puis panier hors taxe, puis taux de marge).

```python
m24, m25 = x24["marge_ht"].sum(), x25["marge_ht"].sum()
n24, n25 = x24["id_commande"].nunique(), x25["id_commande"].nunique()
h24, h25 = x24["montant"].sum() / 1.2 / n24, x25["montant"].sum() / 1.2 / n25
t24, t25 = m24 / (x24["montant"].sum() / 1.2), m25 / (x25["montant"].sum() / 1.2)
e_volume, e_panier, e_taux = (n25 - n24) * h24 * t24, n25 * (h25 - h24) * t24, n25 * h25 * (t25 - t24)
print("écart de marge :", round(m25 - m24), "€ = volume", round(e_volume), "+ panier", round(e_panier), "+ taux de marge", round(e_taux))
```
<!--sortie-->
```text
écart de marge : 60450 € = volume 27270 + panier 13517 + taux de marge 19662
```

La marge brute gagne **60 450 €**, dont 27 270 € grâce au volume, 13 517 € grâce au panier et **19 662 € grâce au taux de marge** (de 36,2 % à 38,0 %). Le dernier effet est le plus intéressant : il ne vient ni du trafic ni du prix moyen mais du **mix** (ce que l'on vend) et des **remises**. C'est un indice que quelque chose a changé dans l'assortiment ou la politique de prix, à instruire au chapitre 7.


### 6.2.3 Lire l'arbre pour localiser un écart

Quand un chiffre bouge, l'arbre permet de **répartir l'écart** entre les facteurs. Pour un produit de deux facteurs, $\text{CA}=n\times p$, l'écart entre deux années se découpe ainsi :

$$\Delta\text{CA}=\underbrace{(n_{25}-n_{24})\,p_{24}}_{\text{effet volume}}+\underbrace{n_{25}\,(p_{25}-p_{24})}_{\text{effet panier}}.$$

(On a choisi de valoriser l'effet volume au prix de l'année précédente, et l'effet panier au volume de la nouvelle année : la somme redonne exactement l'écart, sans reste.)

```python
n24, n25 = x24["id_commande"].nunique(), x25["id_commande"].nunique()
p24, p25 = x24["montant"].sum() / n24, x25["montant"].sum() / n25
volume, prix = (n25 - n24) * p24, n25 * (p25 - p24)
print("écart de CA :", round(x25["montant"].sum() - x24["montant"].sum()), "€ = volume", round(volume), "€ + panier", round(prix), "€")
```
<!--sortie-->
```text
écart de CA : 135303 € = volume 90463 € + panier 44840 €
```

Sur les 135 303 € de croissance, **les deux tiers** (90 463 €) viennent de commandes plus nombreuses, **un tiers** (44 840 €) de paniers plus gros. C'est le point de départ d'une **analyse des écarts** (c'est le sujet du chapitre complémentaire 7) : l'arbre dit **où** l'écart est, il ne dit pas encore **pourquoi**. Pour le *pourquoi*, il faut des hypothèses et des tests (chapitres 2 et 3).

> 🧪 **Remarque.** Il existe plusieurs façons de découper un écart entre deux facteurs : valoriser l'effet volume au prix de la nouvelle année donnerait un partage légèrement différent. L'important est de **choisir une convention, de l'écrire** et de s'y tenir ; l'arbre sert à **localiser**, pas à attribuer à l'euro près.

### 6.2.4 Les cadres de référence

Un tableau de bord complet couvre plusieurs arbres : un cadre de référence aide à **ne rien oublier** et à **équilibrer** les points de vue. Voici quatre cadres très utilisés, résumés puis appliqués à la boutique ; aucun n'est « le bon », ce sont des **grilles de lecture**.

| Cadre | Principe | Application à la boutique |
|---|---|---|
| **Tableau de bord équilibré** | quatre points de vue : finances, clients, processus internes, apprentissage | marge ; clients actifs ; livraisons à l'heure, ruptures ; formation de l'équipe de vente |
| **AARRR** (« métriques pirates ») | cinq étapes du parcours client : acquisition, activation, rétention, revenu, recommandation | sessions ; ajout au panier ; clients actifs ; CA ; (recommandation : pas de mesure disponible) |
| **OKR** (objectifs et résultats clés) | un objectif qualitatif, 2 à 4 résultats mesurables, sur un trimestre | « Livrer à temps » ; livraisons à l'heure de 73 % à 85 %… |
| **Étoile du Nord** (*North Star*) | un seul indicateur qui résume la valeur apportée aux clients | « commandes livrées à l'heure et sans retour » |

#### Le parcours AARRR sur nos données

Le cadre AARRR se lit bien sur un **entonnoir** : on compte à chaque étape combien de sessions poursuivent.

```python
s = d["sess"]
etapes = {"sessions": len(s), "ajout au panier": s["ajout_panier"].sum(), "début de paiement": s["debut_paiement"].sum(), "commande": s["commande"].sum()}
print(pd.Series(etapes).to_frame("n").assign(pct_des_sessions=lambda t: (t["n"] / len(s) * 100).round(1)).to_string())
```
<!--sortie-->
```text
                        n  pct_des_sessions
sessions           127022             100.0
ajout au panier     18116              14.3
début de paiement   10358               8.2
commande             6078               4.8
```

Sur 127 022 sessions, 14,3 % ajoutent un produit au panier, 8,2 % commencent le paiement et 4,8 % commandent : **12 038 paniers ajoutés ne se concluent pas**. Les actions diffèrent selon l'étape où l'on perd le plus.

Le même entonnoir, **par source de trafic**, montre où agir : la conversion d'une session « e-mail » est de 8,7 %, celle d'une session « réseaux » de 2,2 %.

```python
f = s.groupby("source")[["ajout_panier", "debut_paiement", "commande"]].mean().mul(100).round(1)
print(f.sort_values("commande", ascending=False).to_string())
```
<!--sortie-->
```text
           ajout_panier  debut_paiement  commande
source                                           
email              17.8            12.2       8.7
direct             16.5            10.3       6.9
organique          13.4             7.4       4.0
referent           12.6             7.1       3.8
payant             12.6             6.3       3.0
reseaux            11.9             5.5       2.2
```

Les écarts entre sources existent **à chaque étape** : de l'ajout au panier (17,8 % pour l'e-mail, 11,9 % pour les réseaux) jusqu'au paiement terminé. La part des paiements commencés qui aboutissent va de **71 % pour l'e-mail à 40 % pour les réseaux**. Le trafic « réseaux » est donc moins prêt à acheter **partout** dans le parcours : l'action n'est pas d'améliorer une étape précise, c'est de **mieux cibler** ce trafic (ou de le juger sur un autre indicateur que la conversion immédiate).


#### Un objectif et ses résultats clés (OKR)

La méthode OKR sépare le **qualitatif** (« quel objectif ? ») du **mesurable** (« à quoi voit-on qu'il est atteint ? »). Un exemple pour la boutique, avec les valeurs de départ tirées des données :

> **Objectif du trimestre : « Livrer à temps, sans mauvaise surprise ».**
> - Résultat clé 1 : livraisons à l'heure de **73,5 %** à **85 %**.
> - Résultat clé 2 : colis abîmés de **1,8 %** à **1,0 %**.
> - Résultat clé 3 : retours « livraison tardive » en baisse d'un tiers.

Un OKR est une **cible** avec un point de départ mesuré : nous verrons en 6.3 comment fixer le « 85 % » sans tomber dans l'arbitraire.

#### L'étoile du Nord : un chiffre qui résume la valeur

L'idée de l'étoile du Nord est de choisir **un indicateur qui ne s'améliore que si le client est vraiment servi**. Pour la boutique, un candidat : la part des commandes livrées **à l'heure et sans retour**. Elle croise la logistique (retard) et la qualité (retour), deux dimensions que les indicateurs séparés regardent isolément.

```python
l = d["liv"][d["liv"]["date_commande"] >= "2025-01-01"].copy()
l["retour"] = l["id_commande"].map(x25.groupby("id_commande")["retourne"].max()).fillna(False).astype(bool)
ok = (l["retard"] == 0) & ~l["retour"]
print("livrées à l'heure :", round((1 - l["retard"].mean()) * 100, 1), "% | sans retour :", round((~l["retour"]).mean() * 100, 1), "% | les deux :", round(ok.mean() * 100, 1), "%")
```
<!--sortie-->
```text
livrées à l'heure : 73.5 % | sans retour : 81.9 % | les deux : 59.9 %
```

Deux indicateurs à 73 % et 82 % se combinent en **60 %** : à peine plus d'une commande sur deux est livrée à temps **et** conservée. Ce chiffre, plus bas et plus parlant, est celui que l'on peut raconter à toute l'équipe.


### 6.2.5 Les limites d'un cadre

Aucun cadre ne choisit à votre place. Trois réserves.

- **Un cadre est une checklist, pas une analyse.** Il garantit que vous n'oubliez pas une dimension (par exemple la recommandation, que nous ne mesurons pas) ; il ne dit ni quoi mesurer précisément, ni quelle valeur est bonne.
- **Un cadre peut cacher le contexte.** AARRR a été pensé pour des produits numériques ; une boutique avec un canal physique (42 % du chiffre d'affaires en 2025) n'y trouve pas sa place sans adaptation.
- **Trop d'indicateurs tue l'indicateur.** Chaque cadre pousse à ajouter des cases ; la règle pratique est de **ne garder que ce qui déclenche une décision** (section 6.1.1) et de rester sous une dizaine d'indicateurs par tableau de bord.

> ✅ **À retenir.** Décomposez le chiffre global en un **arbre** : les produits (conversion, panier) donnent des variations en pourcentage, les sommes (canaux, catégories) des contributions en euros. L'arbre **localise** un écart sans l'expliquer. Les cadres de référence aident à couvrir tous les angles, jamais à décider ; gardez-en le **plus petit nombre d'indicateurs** qui déclenchent encore une action.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.3 et 6.4, exercices 6.6 à 6.8.


## 6.3 Cibles, références et seuils

Un indicateur sans point de comparaison ne dit rien : 73 % de livraisons à l'heure, est-ce bon ou mauvais ? Cette section répond à trois questions pratiques : **à quoi comparer** (les références), **ce qu'il faut viser** (les cibles), et **à partir de quand s'inquiéter** (les seuils). La dernière est la plus difficile, parce qu'elle oblige à distinguer le **bruit**, qui bouge toujours, du **signal**, qui mérite une action.

### 6.3.1 De quoi une cible est-elle faite

Une cible n'est pas un souhait ; c'est une **valeur, une échéance et un point de départ**. Trois ingrédients à toujours expliciter.

1. **La base de comparaison** : à partir de quelle valeur mesurée part-on ? (« 73,5 % aujourd'hui », pas « beaucoup mieux ».)
2. **L'ambition** : de combien veut-on progresser, et pourquoi cette valeur ?
3. **L'horizon** : en combien de temps, avec quels moyens ?

Une cible raisonnable est **ancrée dans ce qui s'est déjà produit**. Voici l'historique du chiffre d'affaires hors taxe de la boutique.

```python
ca_ht = d["cr"].assign(annee=d["cr"]["mois"].str[:4]).groupby("annee")["ca_ht"].sum()
print(pd.DataFrame({"CA HT (€)": ca_ht.round(0).astype(int), "croissance (%)": (ca_ht.pct_change() * 100).round(1)}).to_string())
```
<!--sortie-->
```text
       CA HT (€)  croissance (%)
annee                           
2023      949111             NaN
2024      991218             4.4
2025     1103969            11.4
```

La croissance a été de **4,4 %** en 2024 puis de **11,4 %** en 2025. Fixer une cible de croissance de 8 % pour 2026 se situe entre les deux années passées ; viser 15 % dépasserait la meilleure année observée et demanderait de dire **par quels leviers** (trafic, conversion, panier : l'arbre de 6.2.1). Une cible qui n'est reliée à aucun levier n'est qu'un chiffre.

> 💡 **Intuition.** Une bonne cible est **atteignable mais engageante** : on peut dire, branche par branche de l'arbre, d'où viendra le gain. Elle est aussi **révisable** : on la corrige quand l'hypothèse sur laquelle elle repose change (un nouveau transporteur, un nouveau canal).

#### Relier la cible aux leviers : un exemple

Voici comment on justifie le « 85 % de livraisons à l'heure » de l'objectif de 6.2.4. Les livraisons de 2025 se répartissent entre trois transporteurs, dont l'un est nettement moins bon ; et décembre est mauvais pour tous.

```python
liv25 = d["liv"][d["liv"]["date_commande"] >= "2025-01-01"].assign(ok=lambda t: 1 - t["retard"], dec=lambda t: t["date_commande"].str[5:7] == "12")
tab = liv25.groupby("transporteur").agg(part=("ok", "size"), a_l_heure=("ok", "mean"))
tab["part"] = tab["part"] / tab["part"].sum()
tab["hors décembre"] = liv25[~liv25["dec"]].groupby("transporteur")["ok"].mean(); tab["décembre"] = liv25[liv25["dec"]].groupby("transporteur")["ok"].mean()
print((tab * 100).round(1).to_string())
```
<!--sortie-->
```text
                part  a_l_heure  hors décembre  décembre
transporteur                                            
Transporteur A  44.8       84.7           88.7      61.7
Transporteur B  35.5       73.6           78.5      44.1
Transporteur C  19.7       47.8           54.0      15.0
```

Le transporteur C livre **la moitié** de ses colis à l'heure (47,8 %) contre 84,7 % pour A, et décembre est mauvais pour **tous** : même le meilleur transporteur tombe à 61,7 % ce mois-là. Deux leviers donc, que l'on peut chiffrer : remplacer C par A, et ramener décembre au niveau du reste de l'année.

```python
ok_hors = liv25[~liv25["dec"]].groupby("transporteur")["ok"].mean(); part = liv25["transporteur"].value_counts(normalize=True)
actuel = liv25["ok"].mean()
c_vers_a = (ok_hors["Transporteur A"] * (part["Transporteur A"] + part["Transporteur C"]) + ok_hors["Transporteur B"] * part["Transporteur B"])
tab2 = liv25.groupby("transporteur")["ok"].mean()
seul = tab2["Transporteur A"] * (part["Transporteur A"] + part["Transporteur C"]) + tab2["Transporteur B"] * part["Transporteur B"]
print("actuel :", round(actuel * 100, 1), "% | C remplacé par A :", round(seul * 100, 1), "% | et décembre comme le reste de l'année :", round(c_vers_a * 100, 1), "%")
```
<!--sortie-->
```text
actuel : 73.5 % | C remplacé par A : 80.7 % | et décembre comme le reste de l'année : 85.1 %
```

Le seul remplacement de C porte les livraisons à l'heure de 73,5 % à 80,7 % ; ajouter un décembre aussi bon que le reste de l'année les porte à 85,1 %. L'objectif de **85 %** est donc **tout juste atteignable, à condition d'agir sur les deux leviers** ; avec un seul, il ne l'est pas. Voilà ce que veut dire « ancrer une cible dans les leviers » : on peut raconter, ligne par ligne, d'où viendront les points. (Ces simulations supposent que les nouveaux colis se comportent comme les anciens du même transporteur ; une hypothèse à vérifier en cours de route.)


### 6.3.2 Choisir une référence

Un chiffre se compare à **quatre références**, qui répondent à quatre questions différentes.

| Référence | Question | Avantage | Limite |
|---|---|---|---|
| **La période précédente** (le mois dernier) | Va-t-on mieux qu'hier ? | toujours disponible | mélange saison et tendance |
| **La même période l'an dernier** | Va-t-on mieux, à saison égale ? | neutralise la saison | l'an dernier n'était pas forcément un bon modèle |
| **Le budget** ou la cible | Fait-on ce qu'on avait prévu ? | relie l'indicateur à la stratégie | vaut ce que vaut le budget (6.3.3) |
| **Le secteur** (*benchmark*) | Fait-on comme les autres ? | donne le niveau de jeu | définitions souvent différentes ; ce que d'autres ont fait n'est pas ce que vous devriez faire |

Pour la quatrième, nous disposons d'un fichier de **références sectorielles fictives** (médiane et premier et troisième quartiles). Comparons les indicateurs de la boutique en 2025 à la zone centrale du secteur : « meilleur » veut dire du bon côté du quartile favorable, « moins bon » du mauvais côté de l'autre quartile.

```python
pos = O.position_secteur(d)
print(pos[["indicateur", "boutique", "quartile_1", "mediane", "quartile_3", "position"]].to_string(index=False))
```
<!--sortie-->
```text
                        indicateur  boutique  quartile_1  mediane  quartile_3      position
       Taux de marge brute (HT, %)     37.96        33.0     38.0        42.0 dans la norme
        Taux de retour (lignes, %)      6.29         3.5      5.5         8.5 dans la norme
                  Panier moyen (€)    102.33        70.0     92.0       118.0 dans la norme
    Taux de conversion du site (%)      4.78         1.8      2.6         3.8      meilleur
       Part du site dans le CA (%)     46.63        20.0     35.0        50.0 dans la norme
        Rotation du stock (par an)      4.23         3.0      4.2         5.8 dans la norme
      Taux de rupture de stock (%)      7.36         2.0      4.0         7.0     moins bon
          Livraisons à l'heure (%)     73.47        86.0     92.0        96.0     moins bon
Coût d'acquisition d'un client (€)     98.58        11.0     18.0        27.0     moins bon
    Clients actifs sur 12 mois (%)     64.58        30.0     42.0        55.0      meilleur
    Frais de personnel / CA HT (%)     12.78        19.0     24.0        29.0 à interpréter
```

![La boutique par rapport au secteur : un point par indicateur, la bande bleue étant la zone entre le premier et le troisième quartile du secteur (valeurs fictives). Pour la rupture de stock, le coût d'acquisition et le taux de retour, plus bas est meilleur.](figures/ch06-benchmark.png)


Quatre enseignements.

- **La conversion du site (4,78 %) et la part des clients actifs (64,6 %) dépassent le troisième quartile** du secteur : des points forts, mais à vérifier avant d'être fêtés. La conversion d'un site dépend de la définition de la session et du trafic ; un trafic très qualifié (e-mail, direct) la gonfle.
- **Les livraisons à l'heure (73,5 %), la rupture de stock (7,4 %) et le coût d'acquisition d'un client (98,6 €)** sont du **mauvais côté** : les deux premiers confirment l'inquiétude de la gérante ; l'écart du dernier (98,6 € contre une médiane de 18 €) est si grand qu'il faut d'abord **vérifier la définition** (clients nouveaux ou clients inscrits, dépenses de marketing comprises ou non) avant d'y voir un problème commercial.
- **Les frais de personnel rapportés au chiffre d'affaires (12,8 %)** sont très inférieurs à la médiane : on ne sait pas si c'est une bonne nouvelle (efficacité) ou un signe de sous-effectif. L'indicateur n'a **pas de sens unique** : il est « à interpréter », et la fiche doit le dire.
- Les indicateurs « dans la norme » ne sont pas pour autant bons : **la norme du secteur peut être médiocre**.

> ⚠️ **Piège.** Un *benchmark* est presque toujours calculé avec **d'autres définitions, un autre périmètre et d'autres entreprises** que les vôtres. Avant de comparer, vérifiez que la définition de l'indicateur est la même ; sinon, comparez des **tendances** plutôt que des niveaux. Et rappelez-vous que les valeurs de ce fichier sont **inventées**.

### 6.3.3 Le budget : quelle précision en attendre ?

Le budget est la référence la plus utilisée et la plus mal comprise : on le traite comme une vérité, alors que c'est une **prévision**, avec son erreur. Mesurons-la sur 2025 : le fichier `budget_reel_2025.csv` donne le budget et le réalisé par mois, catégorie et canal.

```python
b = d["budget"]; bm = b.groupby("mois")[["ca_budget", "ca_reel"]].sum()
em = (bm["ca_reel"] / bm["ca_budget"] - 1) * 100
ec = (b["ca_reel"] / b["ca_budget"] - 1) * 100
print("année : budget", round(b["ca_budget"].sum()), "| réel", round(b["ca_reel"].sum()), "| écart", round((b["ca_reel"].sum() / b["ca_budget"].sum() - 1) * 100, 1), "%")
print("mois : de", round(em.min(), 1), "% à", round(em.max(), 1), "% | écart-type", round(em.std(), 1), "points | mois à plus de 5 % :", int((em.abs() > 5).sum()), "sur 12")
print("cellules (mois x catégorie x canal) : écart absolu médian", round(ec.abs().median(), 1), "% | cellules à plus de 5 % :", round((ec.abs() > 5).mean() * 100), "%")
```
<!--sortie-->
```text
année : budget 1278700 | réel 1324764 | écart 3.6 %
mois : de -7.9 % à 11.0 % | écart-type 6.0 points | mois à plus de 5 % : 7 sur 12
cellules (mois x catégorie x canal) : écart absolu médian 15.1 % | cellules à plus de 5 % : 82 %
```

Sur l'année, le réalisé dépasse le budget de 3,6 %. Par mois, l'écart va de −7,9 % à +11,0 %, avec un écart-type de six points : **sept mois sur douze** sortent d'une fourchette de ±5 %. Dans le détail (mois × catégorie × canal), l'écart absolu médian atteint 15 % et 82 % des cellules s'écartent de plus de 5 %. Conclusion pratique : **un seuil d'alerte plus étroit que l'erreur habituelle du budget alerte en permanence**. Si le budget se trompe de ±6 points d'un mois à l'autre, un voyant rouge à ±5 % sera rouge presque une fois sur deux, et plus personne ne le regardera.

> ✅ **À retenir.** Un budget a une **précision**, que l'on mesure sur les années passées. Un seuil sur l'écart au budget doit être **plus large que cette précision** ; sinon on produit des alertes qui n'en sont pas.

### 6.3.4 Bruit ou signal ?

Même sans budget, un indicateur **bouge toujours**. Le taux de retour de 6,3 % ne sera pas de 6,3 % chaque semaine, simplement parce que **le hasard** décide chaque semaine quelles lignes de commande seront retournées. La question centrale d'un tableau de bord est : **cette variation est-elle plus grande que ce que le hasard suffit à produire ?**

Un exemple à la main. Chaque semaine, environ 530 lignes sont vendues et chacune a 5,9 % de chances d'être retournée, **sans que rien ne change**. Le nombre de retours suit une loi binomiale, d'écart-type $\sqrt{530\times0{,}059\times0{,}941}\approx5{,}4$ retours, soit $5{,}4/530\approx1{,}0$ point de taux. Une semaine à 6,9 % au lieu de 5,9 % n'a donc **rien d'anormal**. Vérifions-le par simulation : 100 000 semaines tirées avec une vraie valeur **constante**.

```python
rng = np.random.default_rng(6)
n, p = 530, 0.059
ecart = (rng.binomial(n, p, 100000) / n - p) * 100
print("semaines à plus de 0,5 point de la vraie valeur :", round((abs(ecart) >= 0.5).mean() * 100), "%")
print("semaines à plus de 1 point :", round((abs(ecart) >= 1).mean() * 100), "% | à plus de 1,5 point :", round((abs(ecart) >= 1.5).mean() * 100), "%")
```
<!--sortie-->
```text
semaines à plus de 0,5 point de la vraie valeur : 65 %
semaines à plus de 1 point : 31 % | à plus de 1,5 point : 14 %
```

![Écart d'un taux hebdomadaire à sa vraie valeur quand rien ne change : près d'une semaine sur trois s'écarte d'au moins un point (en orange).](figures/ch06-bruit.png)


**Près de deux semaines sur trois** s'éloignent d'au moins un demi-point de la vraie valeur, **près d'une sur trois** d'au moins un point, et une sur sept de plus d'un point et demi, **sans qu'aucune cause n'existe**. Si la gérante réagit à chaque variation de un point, elle réagira à du bruit une semaine sur trois.

Les données de la boutique le confirment : sur 52 semaines de 2025, l'écart-type du taux de retour hebdomadaire est de 0,97 point, pour 1,04 point attendu du seul hasard d'échantillonnage (rapport 0,93). **Toute la variabilité du taux de retour hebdomadaire est compatible avec du bruit pur** : il n'y a pas de « bonne » ou de « mauvaise » semaine à commenter.


### 6.3.5 Des seuils fondés sur la variabilité : les cartes de contrôle

Les cartes de contrôle, inventées pour surveiller des chaînes de production, répondent à la question précédente. On trace l'indicateur dans le temps, avec sa **valeur centrale** et des **limites** à ±3 écarts-types du bruit attendu. Pour une **proportion** (taux de retour, livraisons à l'heure, conversion), l'écart-type du bruit d'une semaine est $\sqrt{\bar p(1-\bar p)/n}$, où $n$ est l'effectif de la semaine : les limites sont plus larges quand $n$ est petit.

Règle de lecture, très simple : un point **hors des limites** est un **signal** (une cause existe probablement) ; un point à l'intérieur est du **bruit** (ne rien faire). On ajoute une zone **orange** entre 2 et 3 écarts-types, et l'on obtient trois couleurs fondées sur la mesure, pas sur l'intuition. Appliquons-le aux livraisons à l'heure, en calculant la valeur centrale et les limites **avant le 24 novembre** (l'historique « normal »), puis en jugeant toutes les semaines.

```python
liv = d["liv"][d["liv"]["date_commande"] >= "2025-01-01"].assign(ok=lambda t: 1 - t["retard"])
wl = O.semaines(liv, "date_commande", "ok"); wl = wl[wl["size"] >= 100]
base = wl[wl.index < "2025-11-24"]
pbar = base["sum"].sum() / base["size"].sum()
z = (wl["mean"] - pbar) / np.sqrt(pbar * (1 - pbar) / wl["size"])
statut = np.where(z > -2, "vert", np.where(z > -3, "orange", "rouge"))
print("valeur centrale :", round(pbar * 100, 1), "% | semaines :", len(wl), "|", pd.Series(statut).value_counts().to_dict())
print(pd.DataFrame({"semaine": wl.index.strftime("%d/%m"), "à l'heure (%)": (wl["mean"] * 100).round(1), "z": z.round(1).values}).tail(5).to_string(index=False))
```
<!--sortie-->
```text
valeur centrale : 78.2 % | semaines : 48 | {'vert': 44, 'rouge': 4}
semaine  à l'heure (%)     z
  24/11           77.8  -0.1
  01/12           46.1 -12.7
  08/12           50.2 -10.7
  15/12           43.5 -13.6
  22/12           44.7 -13.2
```

Sur 48 semaines, **44 sont vertes et 4 sont rouges**, et les quatre rouges sont **les quatre semaines de décembre** : 46 % de livraisons à l'heure la semaine du 1er décembre, soit plus de douze écarts-types sous la normale. Une carte de contrôle aurait déclenché l'alerte **dès la première semaine de décembre** ; la gérante, qui regardait quarante chiffres, l'a vue trois semaines plus tard.

La même carte appliquée au taux de retour n'enregistre **aucun point hors limites** : le taux de retour est stable, et c'est précisément ce que l'on veut savoir pour **ne pas** s'en occuper.

![Cartes de contrôle de 2025. À gauche, le taux de retour reste dans les limites (pas de signal). À droite, les livraisons à l'heure sortent des limites en décembre (points rouges) : le signal apparaît dès la première semaine.](figures/ch06-cartes-controle.png)


**Les indicateurs saisonniers.** Une carte de contrôle sur le chiffre d'affaires brut serait inutile : décembre n'est pas « anormal », il est saisonnier. On compare alors **à la même période de l'an dernier** et l'on contrôle la **croissance**. Les douze croissances mensuelles de 2025 ont une moyenne de 11,4 % et un écart-type de 6,5 points ; le seul mois en baisse, **mai (−1,2 %)**, est à 1,9 écart-type de la moyenne : sous la limite d'alerte de deux écarts-types, donc **un mois à surveiller, pas à commenter**.


Trois précautions pour utiliser ces cartes.

- **Calculer les limites sur un historique « normal »**, pas sur la période que l'on juge : si l'on avait inclus décembre dans la valeur centrale, les limites se seraient élargies et l'alerte aurait disparu.
- **Tenir compte de la saison** pour un indicateur saisonnier : un chiffre d'affaires de décembre ne se juge pas sur la moyenne de l'année, mais sur le décembre précédent (chapitre 5).
- **Ne pas confondre signal et cause** : la carte dit *quand* quelque chose a changé, pas *quoi*. Ici la cause est à chercher dans la logistique de fin d'année (transporteurs, volumes), ce que le chapitre 11 reprend.

### 6.3.6 Le tableau de bord d'une page et le dictionnaire des KPI

Il reste à tout assembler. Un tableau de bord réussi tient en **une page**, ne contient que des indicateurs liés à une décision, affiche pour chacun la **valeur**, la **comparaison** (année précédente ou secteur) et la **tendance**, et colore l'état **selon une règle écrite**. Voici celui de la boutique pour 2025 : les huit indicateurs de pilotage retenus, avec leur tendance mensuelle ; la couleur du cadre est la **position par rapport au secteur** (6.3.2).

![Tableau de bord de la boutique en 2025 : huit indicateurs, chacun avec sa valeur annuelle, sa comparaison (2024 ou secteur) et sa tendance mensuelle. Le cadre est vert quand l'indicateur est meilleur que le secteur, bleu dans la norme, rouge moins bon, gris sans référence.](figures/ch06-tableau-bord.png)


Deux lectures immédiates : les **livraisons à l'heure s'effondrent en fin d'année** (et les ruptures de stock montent à la même période), alors que le chiffre d'affaires et les commandes progressent. C'est exactement le genre de message que quarante chiffres noyaient.

Reste le **dictionnaire des KPI** : une fiche par indicateur (6.1.2), regroupée en tableau. Les seuils d'alerte sont ceux des cartes de contrôle de 6.3.5, calculés sur les semaines « normales » de 2025.

```python
sh = O.seuils_hebdo(d)
print(pd.DataFrame({k: {"centre (%)": round(v["p"], 1), "orange (%)": round(v["orange"], 1), "rouge (%)": round(v["rouge"], 1), "n typique": round(v["n"])} for k, v in sh.items()}).T.to_string())
```
<!--sortie-->
```text
                         centre (%)  orange (%)  rouge (%)  n typique
Taux de retour (lignes)         6.3         8.3        9.3      568.0
Livraisons à l'heure           78.2        71.1       67.5      134.0
Conversion du site              4.8         3.9        3.5     2397.0
Rupture de stock                7.2        11.6       13.8      139.0
```

| KPI | Formule | Périmètre et période | Propriétaire | Fréquence | Alerte orange / rouge |
|---|---|---|---|---|---|
| **Livraisons à l'heure** | commandes livrées dans le délai promis ÷ commandes livrées | Site et Réseaux ; semaine de **commande** | responsable logistique | hebdomadaire | moins de 71 % / moins de 67,5 % |
| **Taux de retour** | lignes retournées ÷ lignes vendues | tous canaux ; semaine de **vente**, **mûrie** trois semaines | responsable des achats | hebdomadaire | plus de 8,3 % / plus de 9,3 % |
| **Conversion du site** | commandes ÷ sessions | site ; semaine | responsable du site | hebdomadaire | moins de 3,9 % / moins de 3,5 % |
| **Rupture de stock** | produit-jours en rupture ÷ produit-jours | 20 produits principaux ; semaine | responsable des achats | hebdomadaire | plus de 11,6 % / plus de 13,8 % |
| **Panier moyen** | CA TTC ÷ commandes distinctes | tous canaux ; mois | gérante | mensuelle | écart à l'an dernier au-delà de la précision du budget (6.3.3) |
| **Taux de marge brute** | (CA HT − coût d'achat) ÷ CA HT | tous canaux ; mois | gérante | mensuelle | baisse de plus de 2 points d'un mois à l'autre |


Ce dictionnaire est la **mémoire** du tableau de bord : le jour où le chiffre bouge, il évite de se demander ce qu'il mesure, qui s'en occupe, et à partir de quand on s'alarme.

### 6.3.7 La cadence de revue : qui lit quoi, quand

Un tableau de bord n'a de valeur que par le **rituel** qui l'accompagne. Trois rythmes se complètent.

- **Chaque semaine**, 15 minutes : les indicateurs de **pilotage** (livraisons, retours, ruptures, conversion), lus avec leurs couleurs. Une seule question : **quelque chose est-il sorti de sa zone ?** Si oui, une personne est désignée et une date fixée.
- **Chaque mois**, une heure : les indicateurs de **résultat** (chiffre d'affaires, marge, panier moyen) contre l'an dernier et le budget ; on décompose l'écart dans l'arbre (6.2) et l'on décide d'instruire ou non une cause (chapitre 7).
- **Chaque trimestre ou chaque année** : les **cibles** et les **seuils** eux-mêmes. On supprime les indicateurs qui n'ont déclenché aucune décision, on corrige les seuils devenus trop larges ou trop étroits, on réécrit les fiches si une définition a évolué.

Un conseil de méthode : **notez chaque décision prise** à la lecture du tableau de bord. Un indicateur qui n'a jamais déclenché de décision en un an ne mérite pas sa place ; un indicateur qui en a déclenché dix doit être surveillé plus finement.

> ✅ **À retenir.** Une cible a une **base, une ambition, un horizon** ; une référence répond à une question précise (hier, l'an dernier, le budget, le secteur) et a ses limites. Un seuil d'alerte doit être **plus large que le bruit** : on le fixe avec une **carte de contrôle** sur un historique normal. Le tableau de bord d'une page affiche valeur, comparaison, tendance et statut, et il s'appuie sur un **dictionnaire**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.5 et 6.6, exercices 6.9 à 6.12.


## Bilan du chapitre 6

Vous savez maintenant :

- **choisir un indicateur** par la décision qu'il éclaire (un chiffre, une personne qui peut agir, une action possible), distinguer **résultat** et **pilotage**, **taux** et **volume** ;
- **écrire la fiche d'un KPI** (formule, périmètre, période, source, propriétaire, fréquence, sens favorable, limites) et **calculer** tous les indicateurs d'une entreprise par **une seule fonction** ;
- **repérer les pièges de calcul** : la moyenne des moyennes (2,8 % de taux global contre 6 % de moyenne simple dans l'exemple à la main), un mot et trois formules (6,3 %, 13,6 % ou 6,4 % de « retours »), les périodes qui ne se superposent pas (101 retours de 2025 datés de 2026), le cumul qui masque la tendance ;
- **reconnaître la loi de Goodhart** et la contrer par un **contre-indicateur** : le nombre de commandes monte de 8 % les jours de promotion pendant que la marge baisse de 21 %, un seuil de panier à 40 € fait gagner 22 % de panier moyen et coûte 5 % de chiffre d'affaires, un trafic de mauvaise qualité fait reculer la conversion de 7 % ;
- **décomposer un chiffre en arbre** : multiplicatif (chiffre d'affaires du site = 127 022 sessions × 4,785 % × 101,63 € = 617 715 €, à l'euro près) et additif (canaux, catégories), répartir un écart entre volume et panier (90 463 € contre 44 840 €) pour **localiser** un écart sans l'expliquer ;
- **situer** les cadres de référence (tableau de bord équilibré, AARRR, OKR, étoile du Nord) et en voir les limites ;
- **fixer une cible** (base, ambition, horizon), **choisir une référence** (hier, l'an dernier, budget, secteur) et en connaître les limites, **mesurer la précision d'un budget** (écart-type mensuel de six points) ;
- **distinguer bruit et signal** par la simulation et par les **cartes de contrôle** : près d'une semaine sur trois s'écarte d'un point d'un taux qui ne change pas, et pourtant les quatre semaines de décembre sortent des limites des livraisons à l'heure, dès la première ;
- **assembler un tableau de bord d'une page** et son **dictionnaire de KPI**.

Le tableau suivant résume ce que nous avons mesuré sur la boutique en 2025.

| Question | Résultat |
|---|---|
| Croissance 2024-2025 : chiffre d'affaires, commandes, panier moyen | +11,4 % ; +7,6 % ; +3,5 % |
| D'où vient la croissance ? | canal Site : 85 % de l'écart ; volume : 90 463 € sur 135 303 € |
| Indicateurs du mauvais côté du secteur | livraisons à l'heure (73,5 %), rupture de stock (7,4 %), coût d'acquisition (98,6 €, définition à vérifier) |
| Indicateur « étoile du Nord » proposé | commandes livrées à l'heure et sans retour : 59,9 % |
| Précision du budget | écart mensuel de −7,9 % à +11,0 %, 7 mois sur 12 à plus de 5 % |
| Seuil d'alerte des livraisons à l'heure | orange sous 71 %, rouge sous 68 % ; décembre : rouge quatre semaines de suite |

Le fil conducteur du chapitre tient en une phrase : **un indicateur n'est utile que s'il est défini, comparé à quelque chose et lu avec la variabilité du hasard**. Trois habitudes à retenir :

> 🧭 **En pratique : trois habitudes.**
> 1. **Une fiche par KPI et une seule fonction de calcul.** C'est la meilleure assurance contre les disputes de chiffres et les évolutions « spectaculaires » qui viennent d'une définition qui change.
> 2. **Un contre-indicateur à côté de chaque objectif.** Quand le chiffre ciblé monte et que son contre-indicateur baisse, c'est que l'on optimise le chiffre et plus la réalité.
> 3. **Des seuils mesurés, jamais décidés à l'œil.** Un voyant rouge qui s'allume une semaine sur trois par hasard est pire que pas de voyant.

> ⚠️ **Rappel d'honnêteté.** Les données sont **simulées**, les références du secteur sont **inventées**, et la comparaison des jours de promotion est **descriptive** : elle ne mesure pas l'effet causal d'une promotion (chapitre 2). Les seuils sont calculés sur une seule année de données et seraient à réviser avec davantage d'historique.

Le chapitre 7, complémentaire, prolonge la décomposition de 6.2 : il répartit un **écart au budget** entre ses causes (prix, volume, mix) et apprend à remonter du « où » au « pourquoi ».

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.1 à 6.6 (fiche et calcul d'un KPI, pièges de définition, arbre de la marge, entonnoir, références et budget, cartes de contrôle et état hebdomadaire) et exercices 6.1 à 6.12.
