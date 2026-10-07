# Chapitre 5 : Séries temporelles et analyse de tendance

> « Une courbe qui monte n'est une bonne nouvelle que si l'on sait de combien elle aurait monté sans la saison. »

La gérante arrive avec deux questions qui se ressemblent et qui n'ont rien à voir. La première : « **Mes ventes progressent-elles vraiment, au-delà de la saison ?** » Chaque année, décembre est le meilleur mois et février le pire ; comparer le mois courant au mois précédent n'apprend donc presque rien. La seconde : « **Combien allons-nous vendre en décembre prochain ?** » Elle doit commander des produits, prévoir du personnel, négocier un emplacement pour le stock : elle a besoin d'un chiffre, et surtout de savoir **de combien ce chiffre peut se tromper**.

Les deux questions relèvent de l'analyse des **séries temporelles**, c'est-à-dire de mesures répétées à intervalle régulier : le chiffre d'affaires de chaque jour, de chaque semaine, de chaque mois. Leur particularité est que **l'ordre compte** : on ne peut pas mélanger les lignes comme on le ferait pour des clients, parce que les valeurs voisines se ressemblent (un lundi ressemble au lundi précédent, un décembre au décembre d'avant) et que l'avenir ne ressemble au passé que de certaines manières.

## Le chemin de ce chapitre

- **5.1 Tendances et saisonnalité** : on apprend à **décomposer** une série en une tendance (où va-t-on ?), une saison (ce qui se répète) et un résidu (ce qui reste), à comparer honnêtement à la même période de l'an dernier, à calculer des indices saisonniers à la main, à tenir compte du calendrier, et à repérer les ruptures et les incidents avant qu'ils ne faussent l'analyse.
- **5.2 Moyennes mobiles et prévisions simples** : on lisse une série, on construit des prévisions de référence (naïve, saisonnière, lissage exponentiel) et surtout on apprend à les **évaluer honnêtement**, sur des données que le modèle n'a pas vues, avec des mesures d'erreur dont on connaît les défauts.
- **5.3 ➕ Saisonnalité et prévision pour la planification** : régression avec indicatrices, modèle ARIMA saisonnier (en une page), prévision par canal et pour le total, effet de l'horizon, scénarios « avec ou sans promotion », et traduction d'une prévision en décisions de stock et de personnel.
- **Bilan du chapitre** : ce qu'on répond à la gérante, avec les chiffres.

> 🧭 **Parcours essentiel.** Les sections 5.1 et 5.2 suffisent pour répondre à la première question et pour produire une prévision défendable. La section 5.3 (facultative) traite de la planification.

## Les données du chapitre

> 📦 **Les données.** La série du chapitre est `jours_exploitation.csv` : **1 096 jours** (du 1er janvier 2023 au 31 décembre 2025) avec le nombre de commandes et le **chiffre d'affaires TTC** de la boutique (canaux Boutique, Site et Réseaux confondus), la température, la pluie, un indicateur de promotion et la dépense publicitaire du jour. Une variante, `jours_incidents.csv`, contient les mêmes jours avec des **incidents injectés** (une panne du site, une erreur de saisie, une journée en double…) : nous nous en servons en 5.1.7. Les données sont **simulées** et la **vérité programmée** est connue : la demande progresse de 6 % par an, la saison suit un profil mensuel fixe, le samedi vend plus que le dimanche, une promotion augmente les commandes de 18 %, et les prix ont augmenté de 3 % le 1er janvier 2025. Nous la révélerons au fil du chapitre, pour mesurer ce que l'analyse retrouve et ce qu'elle manque.


Avant tout calcul, **regardons la série**. Les trois années du chiffre d'affaires mensuel, superposées, racontent déjà l'essentiel.

![Chiffre d'affaires mensuel des trois années, superposées : la saison se répète d'une année à l'autre, et chaque courbe est plus haute que la précédente.](figures/ch05-annees.png)

Le chiffre d'affaires annuel passe de 1 138 932 € en 2023 à 1 189 461 € en 2024 (**+4,4 %**) puis à 1 324 764 € en 2025 (**+11,4 %**). Mais l'année est faite de douze mois très inégaux, et la progression visible à l'œil sur la figure mélange trois choses : une **tendance** de fond, une **saison** qui revient chaque année, et du **bruit**. Démêler ces trois composantes, c'est tout l'objet de la section suivante.

> ⚠️ **Piège de départ.** Deux chiffres qui ressemblent à une réponse : « +11,4 % en 2025 » et « décembre : +19,4 % par rapport à novembre » (en 2024). Le premier compare des périodes **de même nature** (deux années entières) ; le second compare deux mois que la saison sépare à elle seule. Savoir lequel est une information, et lequel est un artefact du calendrier, est la compétence centrale du chapitre.


## 5.1 Tendances et saisonnalité

La première question de la gérante demande de **séparer** ce qui monte de ce qui revient. Cette section donne les outils pour le faire : une décomposition en composantes, une comparaison honnête à l'année précédente, des indices saisonniers que l'on sait calculer à la main, une prise en compte du calendrier, et des réflexes pour traiter les ruptures et les incidents. Tout se fait sur le chiffre d'affaires TTC de la boutique.

### 5.1.1 Trois composantes

Une série temporelle $y_t$ (le chiffre d'affaires du mois $t$) se lit comme la combinaison de trois ingrédients.

- La **tendance** $T_t$ : le niveau de fond, qui évolue lentement (la clientèle grandit, les prix montent). C'est ce que la gérante appelle « progresser vraiment ».
- La **saison** $S_t$ : un motif qui **se répète à intervalle fixe**, ici chaque année (décembre fort, février faible) et chaque semaine (samedi fort, dimanche faible).
- Le **résidu** $R_t$ : tout le reste, c'est-à-dire le hasard (le nombre de clients qui poussent la porte un mardi donné) et les événements ponctuels.

Deux manières de les assembler. Dans le **modèle additif**, $y_t=T_t+S_t+R_t$ : la saison ajoute ou retire un nombre **d'euros** constant (« décembre ajoute 60 000 € »). Dans le **modèle multiplicatif**, $y_t=T_t\times S_t\times R_t$ : la saison multiplie le niveau par un **coefficient** (« décembre vaut 1,58 fois un mois moyen »). Le choix dépend de la forme de la série : si l'amplitude des oscillations **grandit avec le niveau**, le multiplicatif est le bon modèle (nous le vérifierons en 5.1.5).

> 💡 **Intuition.** Pensez à un thermomètre de cuisine placé dans un four dont on monte la température : la tendance est la température de consigne, la saison est la montée et la descente de chaque cycle de chauffe, le résidu est le tremblement de l'aiguille. On ne juge pas la consigne en regardant l'aiguille à un instant.

Pour **voir** la tendance, on remplace chaque mois par la moyenne des douze mois qui l'entourent : sur une année complète, la saison s'annule (chaque mois du calendrier apparaît une fois), et ce qui reste est le niveau de fond. C'est la **moyenne mobile centrée** que l'on étudiera en détail en 5.2.1.

![Chiffre d'affaires mensuel (bleu) et sa tendance (orange), calculée par une moyenne mobile centrée sur douze mois. L'écart entre les deux courbes est la saison et le résidu.](figures/ch05-composantes.png)


La tendance est lisse et monte : de juillet 2023 à juin 2025, elle passe de 95 281 € à 109 291 € par mois. La moyenne mobile centrée ne peut pas être calculée aux deux extrémités (il faut six mois avant et après), ce qui est un premier piège que nous retrouverons (5.1.9).

### 5.1.2 Choisir le pas : jour, semaine ou mois

La même série existe à plusieurs **pas** : 1 096 points au jour, environ 157 à la semaine, 36 au mois. Le pas n'est pas neutre.

- **Au jour**, la série est dominée par le **calendrier** (le samedi vend plus que le lundi) et par le hasard : on voit surtout du bruit et un créneau hebdomadaire.
- **À la semaine**, le créneau disparaît (chaque semaine contient chaque jour de semaine une fois) ; il reste la saison annuelle et le bruit.
- **Au mois**, la série est lisible, mais elle ne compte plus que 36 points et ses mois ont des **longueurs inégales** (28 à 31 jours) et des compositions inégales (quatre ou cinq samedis).


![Le même chiffre d'affaires de septembre à décembre 2025 au jour, à la semaine et au mois.](figures/ch05-pas.png)

Un exemple suffit pour se méfier des mois bruts. Février 2025 a vendu 72 642 € et janvier 89 179 € : février est **-18,5 %** plus bas. Mais janvier a 31 jours et février 28 : ramené **au jour**, février vend 2 594 € par jour contre 2 877 € en janvier, soit seulement **-9,8 %**. Plus de la moitié de l'écart apparent vient simplement de la longueur du mois.

> 🧭 **En pratique.** Choisissez le pas selon **la décision**. Un réapprovisionnement hebdomadaire se pilote à la semaine ; un budget annuel au mois. Gardez toujours la série au pas le plus fin : on peut toujours agréger, on ne peut jamais désagréger. Et n'agrégez pas des pourcentages (5.1.9) : on **somme** les montants, puis on calcule le pourcentage.

### 5.1.3 Comparer à la même période de l'an dernier

La saison rend inutile la comparaison d'un mois au précédent : décembre bat toujours novembre. La comparaison honnête met en face **le même mois de l'année précédente**, où la saison est la même : c'est la **variation annuelle** (ou « à un an d'écart »).

$$\text{variation annuelle}_t=\frac{y_t}{y_{t-12}}-1.$$

Elle supprime la saison, mais elle reste **bruyante** quand on la calcule mois par mois. On le voit sur 2025 : les variations mensuelles vont de -1,2 % à 18,5 %, avec un écart-type de 6,2 points, alors que l'année entière progresse de 11,4 %. Un mois isolé qui « baisse de 1 % » n'invalide pas une tendance de +11 %.


Pour lisser le bruit sans perdre la comparaison à l'an dernier, on utilise le **glissement annuel** : on somme les **douze derniers mois** et l'on compare à la somme des douze mois d'un an plus tôt. Cette mesure couvre toujours une année complète, donc toute la saison. Ses valeurs racontent l'accélération : 4,4 % à fin 2024, 5,1 % à fin mars 2025, 5,0 % à fin juin, 7,4 % à fin septembre, et 11,4 % à fin 2025. La progression ne se répartit donc pas uniformément : elle s'est nettement accélérée à partir de l'été 2025.

> ⚠️ **Piège : la comparaison de mois consécutifs.** De décembre 2024 à janvier 2025, le chiffre d'affaires « chute » de **-43,3 %**. Personne n'en conclura à une catastrophe : janvier est toujours le lendemain de décembre. Comparer deux mois voisins sur une série saisonnière mesure la saison, pas la tendance. Quand on doit absolument comparer un mois au précédent, on le fait sur la série **désaisonnalisée** (5.1.4 et 5.1.5).

### 5.1.4 Les indices saisonniers, calculés à la main

Un **indice saisonnier** dit de combien un mois s'écarte d'un mois moyen **à cause de la saison seule**. La méthode classique tient en trois étapes, que l'on déroule d'abord sur les **trimestres** (douze nombres, calculables à la main), puis que l'on applique aux mois.

1. **Isoler la tendance** : moyenne mobile centrée sur un cycle complet. Avec des trimestres, un cycle compte quatre périodes ; pour que la moyenne soit centrée sur un trimestre précis, on prend 0,5 fois le trimestre le plus ancien, les trois du milieu entiers, et 0,5 fois le plus récent, le tout divisé par 4.
2. **Rapport à la tendance** : on divise la valeur observée par cette moyenne ; un rapport de 1,3 signifie « 30 % au-dessus du niveau de fond ».
3. **Moyenner par position** : on moyenne les rapports d'un même trimestre sur les années, puis on **normalise** pour que la moyenne des indices soit 1.


Voici, sur les huit trimestres où la moyenne centrée existe (les deux premiers et les deux derniers trimestres de la série n'en ont pas), le calcul de l'étape 1 et de l'étape 2.

```text
trimestre CA (k€) tendance (k€) rapport
  T3 2023   267,0         286,9   0,930
  T4 2023   381,7         290,9   1,312
  T1 2024   226,0         293,9   0,769
  T2 2024   296,4         296,2   1,001
  T3 2024   276,4         300,6   0,920
  T4 2024   390,7         305,6   1,279
  T1 2025   251,6         312,1   0,806
  T2 2025   310,8         324,1   0,959
```

Les rapports d'un même trimestre se ressemblent d'une année à l'autre : le quatrième trimestre tourne autour de 1,3 (1,295 en moyenne), le premier autour de 0,8 (0,787). On moyenne par trimestre, puis on **normalise** : la somme des quatre moyennes vaut 3,988, alors qu'elle devrait valoir 4 ; on divise donc chaque moyenne par 3,988 / 4. Les indices trimestriels sont :

| Trimestre | T1 | T2 | T3 | T4 |
|---|---|---|---|---|
| Indice saisonnier | 0,790 | 0,983 | 0,928 | 1,299 |

Le quatrième trimestre vend donc environ **30 % de plus** qu'un trimestre moyen, le premier environ **21 % de moins**. Pour les **mois**, la méthode est identique, avec une moyenne centrée sur douze mois (en fait deux moyennes de douze mois décalées d'un mois, pour que le centre tombe sur un mois précis) : on obtient douze indices dont la moyenne vaut 1.

```python
idx = O.indices_saisonniers(m)              # rapport à la moyenne mobile centrée, moyenné par mois, normalisé
print(idx.round(3).to_dict())
```
<!--sortie-->
```text
{1: 0.821, 2: 0.677, 3: 0.87, 4: 0.906, 5: 1.032, 6: 1.014, 7: 0.945, 8: 0.819, 9: 1.015, 10: 1.036, 11: 1.281, 12: 1.583}
```


![Indices saisonniers mensuels du chiffre d'affaires : mois moyen = 1.](figures/ch05-indices.png)

Décembre vaut 1,583 fois un mois moyen, novembre 1,281, février seulement 0,677 ; les douze indices somment à 12,000. **Désaisonnaliser** une série, c'est diviser chaque mois par son indice : on obtient ce que le mois « aurait vendu » dans un mois moyen, et les mois deviennent enfin comparables entre eux.

> 📐 **Pourquoi normaliser ?** Un indice saisonnier n'a de sens que **relativement** : si tous les indices étaient multipliés par 2, la saison ne changerait pas, mais la série désaisonnalisée serait divisée par 2 et sa tendance serait faussée d'un facteur arbitraire. La normalisation (moyenne 1) fixe l'échelle : la série désaisonnalisée a le **même niveau moyen** que la série d'origine.

### 5.1.5 Décomposer : additif ou multiplicatif, `seasonal_decompose` et STL

Deux outils de `statsmodels` font ce calcul, et bien davantage, en une ligne : `seasonal_decompose` (la méthode à la main de la section précédente) et **STL** (*Seasonal-Trend decomposition using Loess*), plus souple.

```python
from statsmodels.tsa.seasonal import seasonal_decompose, STL
dm = seasonal_decompose(m, model="multiplicative", period=12)     # observé = tendance × saison × résidu
st = STL(np.log(m), period=12, robust=True).fit()                  # même idée sur le logarithme (somme = produit)
print("janvier, indice classique :", round(dm.seasonal.iloc[0], 3), "| indices STL des trois janviers :", np.exp(st.seasonal[st.seasonal.index.month == 1]).round(3).values)
```
<!--sortie-->
```text
janvier, indice classique : 0.821 | indices STL des trois janviers : [0.735 0.8   0.871]
```


Les deux outils racontent la même saison, avec une nuance instructive. `seasonal_decompose` impose un **profil unique** pour toute la période : janvier vaut 0,821, exactement la valeur calculée à la main plus haut. STL, plus souple, laisse le profil **évoluer lentement** : son indice de janvier est de 0,735 en 2023, 0,800 en 2024 et 0,871 en 2025. Un janvier qui s'étoffe d'une année sur l'autre est un fait que le profil unique ignore ; avec trois années seulement, on ne sait pas encore s'il s'agit d'une vraie évolution de la saison ou du bruit. Avec `robust=True`, STL n'est en outre pas dérangé par un mois exceptionnel.

![Décomposition multiplicative du chiffre d'affaires mensuel : observé, tendance, saison et résidu.](figures/ch05-decomposition.png)

**Additif ou multiplicatif ?** Regardons l'écart entre décembre et février, chaque année. Le **rapport** décembre/février est quasi constant : 2,50 en 2023, 2,46 en 2024, 2,53 en 2025. La **différence** en euros, elle, augmente : 94 306 € en 2023, 93 366 € en 2024, 111 202 € en 2025. La saison se comporte comme un **coefficient** qui s'applique à un niveau qui monte : c'est le signe d'un modèle **multiplicatif**. En pratique, si l'on hésite, on prend le logarithme de la série : un modèle multiplicatif devient additif, et tous les outils additifs redeviennent utilisables.

Le **résidu** de la décomposition est un indice autour de 1 : il va de 0,941 à 1,052, avec un écart-type de 3,0 % (la valeur la plus basse est celle de 01/2024, le mois où la série s'écarte le plus de « tendance × saison »). Un résidu qui garderait une structure (une série de mois consécutifs tous du même côté de 1, par exemple) dirait que la décomposition a oublié quelque chose, par exemple une **rupture**.

### 5.1.6 La tendance progresse-t-elle vraiment ?

La tendance extraite par la décomposition est une série ; on peut lui poser une question chiffrée : **de combien progresse-t-elle par an, et peut-on distinguer cette progression du hasard ?** On désaisonnalise la série, puis on ajuste une droite sur le **logarithme** : la pente d'une droite sur un logarithme est un **taux de croissance** (une pente de 0,06 signifie environ +6 % par an).

```python
des = m / idx.reindex(m.index.month).values                  # série désaisonnalisée
t = np.arange(len(m)) / 12                                    # le temps en années
reg = sm.OLS(np.log(des.values), sm.add_constant(t)).fit(cov_type="HAC", cov_kwds={"maxlags": 3})
print("croissance annuelle :", round((np.exp(reg.params[1]) - 1) * 100, 1), "% ; intervalle à 95 % :", np.round((np.exp(reg.conf_int()[1]) - 1) * 100, 1))
```
<!--sortie-->
```text
croissance annuelle : 8.2 % ; intervalle à 95 % : [ 6.4 10. ]
```


La progression estimée est de **8,2 % par an**, avec un intervalle à 95 % de 6,4 % à 10,0 %. Zéro est loin de l'intervalle (la probabilité qu'une telle pente apparaisse par hasard est inférieure à un pour mille) : **oui, les ventes progressent vraiment, au-delà de la saison**.

Deux précautions de méthode. D'abord, les erreurs d'une série temporelle sont **corrélées** d'un mois au suivant ; une régression ordinaire, qui suppose des erreurs indépendantes, annoncerait un intervalle **trop étroit**. L'option `cov_type="HAC"` (erreurs robustes à l'autocorrélation) corrige cela. Ensuite, la droite suppose une croissance **régulière**. Or nous savons que 2025 est différente (prix, voir 5.1.8). Ajoutons à la régression un **saut** de niveau en janvier 2025 : la tendance est alors de **6,5 % par an** (intervalle 3,6 % à 9,6 %) et le saut de **3,5 %** (intervalle -0,8 % à 8,0 %). Les intervalles sont larges, parce que trois années ne fournissent que 36 points ; mais les deux estimations sont proches de ce que la **vérité programmée** annonce : une demande qui croît de **6 % par an** et un prix catalogue relevé de **3 %** au 1er janvier 2025.

> 🧪 **Remarque.** La tendance à +8,2 % de la première régression est un **mélange** : de la croissance de fond (6 %) et d'un relèvement de prix ponctuel (3 %) étalé sur toute la série. Elle décrit bien le passé, et prédit mal le futur : si les prix ne montent plus, la progression sera plus proche de 6 % que de 8,2 %. Une tendance estimée n'est jamais une loi ; c'est un **résumé du passé** dont on doit connaître les ingrédients.

### 5.1.7 Le calendrier : jours de la semaine, mois inégaux

Au jour, le calendrier domine tout. On le mesure par un **indice du jour de semaine**, obtenu comme les indices mensuels : la moyenne du chiffre d'affaires de chaque jour de semaine, divisée par la moyenne générale.

```python
dow = j["chiffre_affaires"].groupby(j.index.dayofweek).mean()
print((dow / dow.mean()).round(3).to_dict())          # 0 = lundi ... 6 = dimanche
```
<!--sortie-->
```text
{0: 0.972, 1: 0.882, 2: 0.93, 3: 0.994, 4: 1.174, 5: 1.39, 6: 0.657}
```


![Indice du jour de semaine du chiffre d'affaires quotidien : le samedi est le jour fort, le dimanche le jour faible.](figures/ch05-jours-semaine.png)

Le samedi vend 1,390 fois un jour moyen, le dimanche 0,657 : le samedi vend **2,1 fois plus** que le dimanche. Ce motif hebdomadaire est de loin le plus fort de la série ; il est aussi la raison pour laquelle on ne compare jamais « hier » à « avant-hier ».

Au mois, le calendrier agit de façon plus discrète : un mois qui compte cinq samedis au lieu de quatre est mécaniquement un peu plus fort. En pondérant chaque jour par son indice, on obtient un **facteur de calendrier mensuel**. Sur nos 36 mois, il varie de 0,984 à 1,019, soit un écart de **3,5 %** entre le mois le mieux et le moins bien doté. L'effet est modeste, mais il suffit à produire des variations de quelques points d'un mois sur l'autre. Pour une analyse fine, on **corrige** le mois en le divisant par ce facteur ; pour une analyse grossière, on se contente de savoir qu'il existe et de comparer des **mois entiers** à des mois entiers.

> 🧭 **En pratique.** Pour les boutiques ouvertes tous les jours, les « jours ouvrés » ne comptent pas ; pour une entreprise fermée le week-end, on comparerait des **mois à nombre égal de jours ouvrés**. Les jours fériés mobiles (Pâques) et les vacances scolaires sont d'autres effets de calendrier du même type : on les traite avec des variables indicatrices (5.3.1).

### 5.1.8 Ruptures et incidents

Une série réelle n'est pas une jolie courbe : elle contient des **ruptures** (un changement durable de niveau) et des **incidents** (un jour exceptionnel). Les deux faussent une décomposition ; on les traite **avant**.

#### Une rupture : le prix catalogue de 2025

Si les ventes passent d'un niveau à un autre le 1er janvier, on cherche **ce qui a changé ce jour-là**. Ici, c'est le prix : comparons le prix catalogue de chaque produit en 2025 et en 2024.


Pour les 120 produits vendus les deux années, le rapport du prix de 2025 à celui de 2024 est de **1,030** pour la médiane (minimum 1,030, maximum 1,031) : une **hausse uniforme de 3 %**. Le prix moyen par ligne montre +3,7 % (de 36,51 € à 37,85 €) parce que le mélange des produits vendus change aussi ; comparer produit à produit isole l'effet prix. Conséquence pour l'analyse : une partie de la progression de 2025 n'est **pas** de la demande. On la sépare en **modélisant la rupture** (comme en 5.1.6) ou en exprimant la série en volumes (quantités) plutôt qu'en euros.

#### Des incidents : trouver ce qui sort du bruit

La variante `jours_incidents.csv` contient, sans que le fichier le dise, des jours anormaux. On les cherche en deux temps. D'abord, les **contrôles exacts** : une journée présente deux fois se trouve avec un simple test de doublon sur la date.

```python
ji = O.jours(incidents=True)
print("dates en double :", ji.index[ji.index.duplicated()].strftime("%d/%m/%Y").tolist())
```
<!--sortie-->
```text
dates en double : ['20/10/2025']
```

Ensuite, les incidents **statistiques** : on ajuste un modèle simple du chiffre d'affaires du jour (jour de semaine, mois, promotion, tendance), robuste aux valeurs extrêmes, et l'on signale les jours dont le **résidu** est très grand. Pour comparer des écarts, on les ramène à un **score z robuste** : l'écart divisé par sa dispersion habituelle, mesurée par la **MAD** (écart absolu médian), qui ne se laisse pas gonfler par les incidents eux-mêmes.

```python
z = O.residus_robustes(ji)                       # score z robuste de chaque jour (modèle : semaine, mois, promotion, tendance)
signales = z[z.abs() > 3.5]
print(len(signales), "jours signalés :", {d.strftime("%d/%m/%y"): round(v, 1) for d, v in signales.items()})
```
<!--sortie-->
```text
8 jours signalés : {'12/02/23': 3.8, '26/06/23': -3.6, '19/08/24': -4.2, '02/02/25': -3.5, '13/03/25': -6.2, '14/03/25': -3.7, '28/04/25': -4.0, '09/09/25': 10.4}
```


![Score z robuste de chaque jour. Les points orange sont signalés au seuil de 3,5 ; les cercles rouges sont les incidents réellement injectés.](figures/ch05-incidents.png)

Au seuil 3,5, 8 jours sont signalés, dont 4 sont de vrais incidents statistiques et 4 de fausses alertes ; en abaissant le seuil à 3, 18 jours sont signalés, dont 7 vrais incidents et 11 fausses alertes. **Ouvrons la vérité programmée** : elle contient 8 incidents (une panne du site de trois jours, une grosse commande professionnelle de 4 200 €, une erreur de saisie qui multiplie par dix le chiffre d'affaires d'un jour, deux jours de fermeture exceptionnelle de la boutique, et la journée en double). Le doublon est trouvé par le contrôle exact ; parmi les 7 incidents statistiques, la règle en retrouve **4** au seuil 3,5 et **7** au seuil 3, au prix de fausses alertes.

La leçon est celle de tout détecteur : **on ne peut détecter que ce qui sort du bruit**. Le chiffre d'affaires d'un jour fluctue d'environ ±24 % sans incident (c'est la dispersion de référence du modèle, la MAD) ; une panne qui retire 55 % des ventes d'un jour ne dépasse pas toujours ce niveau. Les incidents très marqués (l'erreur ×10) sont trouvés par tous les seuils ; les incidents modestes ne se distinguent du hasard qu'au prix de fausses alertes. Le seuil se choisit selon le **coût** d'une erreur : laisser passer un incident, ou vérifier à tort une journée normale.

Que faire d'un incident, une fois trouvé ? Trois traitements, du plus au moins prudent.

- **Le signaler** et garder la valeur (un incident réel fait partie de l'histoire : une vraie panne a bien coûté des ventes).
- **La corriger** quand c'est une **erreur de saisie** : remplacer la valeur par sa valeur attendue ou par la bonne valeur retrouvée à la source. L'erreur de septembre fait passer le mois de 113 453 € à 141 337 €, soit **1,25 fois** la bonne valeur : laissée telle quelle, elle fausserait la tendance et la prévision de la fin d'année.
- **L'exclure** de l'ajustement d'un modèle tout en la gardant dans les données, quand elle n'est pas représentative de l'avenir (une commande exceptionnelle).

> ⚠️ **Piège.** Supprimer silencieusement les jours qui « dérangent » est le meilleur moyen d'obtenir des prévisions trop belles. Chaque traitement se **documente** (chapitre 4 du volume II) : quelle date, quelle règle, quel effet sur le total.

### 5.1.9 Cinq pièges classiques

1. **Comparer des mois consécutifs sur une série saisonnière** (5.1.3) : on mesure la saison, pas la tendance.
2. **Faire la moyenne de pourcentages.** La croissance du chiffre d'affaires de 2025 sur 2024 est de **11,4 %** pour l'ensemble ; par canal, elle est de 0,5 % pour la Boutique, 13,4 % pour les Réseaux et 22,9 % pour le Site. La moyenne simple de ces trois pourcentages donne 12,3 %, ce qui **n'est pas** le taux de l'ensemble : les canaux ont des poids différents. On somme les montants, puis on calcule le pourcentage.
3. **Oublier les bords de la série.** Une moyenne mobile centrée sur douze mois perd six mois au début et six à la fin : sur 36 mois, la tendance n'en couvre que 24. Une décomposition qui « invente » la tendance aux extrémités se trompe justement là où l'on veut prévoir.
4. **Conclure avec trop peu de cycles.** Trois années ne donnent que trois observations par mois pour estimer chaque indice saisonnier : un mois exceptionnel pèse beaucoup. Il faut le dire dans les intervalles (5.1.6) et ne pas sur-interpréter.
5. **Lisser avant de tester ou de prévoir.** Une moyenne mobile crée une **fausse régularité** : ses valeurs voisines partagent des données, donc elles sont très corrélées. Calculer un écart-type ou une corrélation sur une série lissée donne une précision illusoire. On lisse pour **regarder**, pas pour estimer.


> ✅ **À retenir.**
> - Une série temporelle se décompose en **tendance, saison et résidu** ; le modèle est **multiplicatif** quand l'amplitude de la saison grandit avec le niveau.
> - On compare à la **même période de l'an dernier** (variation annuelle) ou, pour lisser le bruit, au **glissement annuel** sur douze mois ; jamais deux mois consécutifs sur une série saisonnière.
> - Un **indice saisonnier** est le rapport moyen à la tendance, normalisé pour valoir 1 en moyenne ; **désaisonnaliser**, c'est diviser par lui.
> - La tendance se mesure par la pente d'une droite sur le **logarithme** de la série désaisonnalisée, avec des erreurs **robustes à l'autocorrélation**, et se lit avec son intervalle.
> - Le **calendrier** (jours de la semaine, longueur des mois) est un effet fort à court terme ; **ruptures** et **incidents** se traitent avant de décomposer, et le traitement se documente.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.4 et exercices 5.1 à 5.6.


## 5.2 Moyennes mobiles et prévisions simples

La seconde question de la gérante, « combien allons-nous vendre en décembre prochain ? », demande de **prévoir**. On commence par l'outil de base de tout lissage, la moyenne mobile, puis on construit des prévisions volontairement **simples**, et l'on consacre l'essentiel de la section à ce qui distingue un analyste d'un devin : **évaluer** une prévision honnêtement, sur des données que la méthode n'a pas vues, et dire de combien elle peut se tromper.

### 5.2.1 Les moyennes mobiles : lisser pour regarder

Une **moyenne mobile** remplace chaque valeur par la moyenne des valeurs voisines. Trois versions suffisent.

- La **moyenne mobile simple** (« à fenêtre arrière ») moyenne les $w$ derniers jours, aujourd'hui compris. Elle utilise uniquement le passé : c'est la version du **suivi en temps réel**.
- La **moyenne mobile centrée** moyenne les valeurs autour du jour (par exemple trois jours avant et trois après). Elle suit mieux la courbe, mais elle utilise le futur : c'est la version de l'**analyse rétrospective** (c'est celle qui sert à extraire la tendance en 5.1).
- La **moyenne mobile exponentielle** donne un poids qui **décroît** avec l'ancienneté : la valeur d'hier compte plus que celle d'il y a un mois. Elle s'écrit de façon récursive, $s_t=\alpha\,y_t+(1-\alpha)\,s_{t-1}$, avec un paramètre $\alpha$ entre 0 et 1 : plus $\alpha$ est grand, plus la courbe réagit vite.

Un exemple à la main avec $\alpha=0{,}5$ et trois valeurs 100, 110 et 90 : on pose $s_1=100$ ; puis $s_2=0{,}5\times110+0{,}5\times100=105$ ; puis $s_3=0{,}5\times90+0{,}5\times105=97{,}5$. La dernière valeur lissée (97,5) tient compte des trois points, avec des poids 0,5, 0,25 et 0,25 en remontant le temps.


En pandas, chacune tient en une ligne.

```python
d = j.loc["2025-09-01":"2025-12-31", "chiffre_affaires"]       # chiffre d'affaires quotidien, de septembre à décembre 2025
ma7 = d.rolling(7).mean()                                       # moyenne mobile simple sur 7 jours (arrière)
ma7c = d.rolling(7, center=True).mean()                         # la même, centrée
ewm = d.ewm(alpha=0.15).mean()                                  # moyenne exponentielle
```

![Chiffre d'affaires quotidien (gris) et trois lissages. La fenêtre de 7 jours efface le créneau hebdomadaire ; celle de 28 jours est plus lisse mais retarde ; l'exponentielle réagit vite sans oublier le passé.](figures/ch05-moyennes-mobiles.png)

Le choix de la fenêtre est un **compromis** entre lissage et retard. Une fenêtre de $w$ jours accuse un retard moyen de $(w-1)/2$ jours : 3 jours pour 7 jours, environ 14 jours pour 28 jours (la figure le montre : la courbe violette n'a pas encore monté quand le chiffre d'affaires de décembre est déjà fort). Une fenêtre de **sept jours** est le choix naturel pour un chiffre d'affaires quotidien : elle contient chaque jour de semaine exactement une fois, donc le créneau hebdomadaire disparaît. Pour la moyenne exponentielle, l'« âge moyen » des données utilisées vaut $(1-\alpha)/\alpha$ : environ 5,7 jours pour $\alpha=0{,}15$.

> ⚠️ **Piège : une série lissée n'est plus une série d'observations.** Chaque valeur d'une moyenne mobile de 7 jours partage six jours avec sa voisine : l'écart-type tombe de 1 570 € (jour) à 978 € (moyenne sur 7 jours), et la corrélation entre deux valeurs consécutives passe de 0,32 à 0,98. Cette régularité est **fabriquée par le lissage** : calculer un écart-type, une corrélation ou un test sur une série lissée donne une précision illusoire. On lisse pour **regarder**, on estime sur les données brutes.

### 5.2.2 Des prévisions de référence

Prévoir, c'est choisir un **modèle du passé** et le prolonger. Avant d'utiliser quoi que ce soit de sophistiqué, on construit des méthodes si simples qu'on peut les expliquer en une phrase, et l'on fait de leur erreur la **barre à franchir**. Une méthode plus complexe n'est justifiée que si elle bat nettement la plus simple de ces références.

Le protocole est celui d'une vraie prévision : on **ne regarde que 2023 et 2024** (24 mois), on prévoit les douze mois de 2025, puis on compare à ce qui s'est réellement passé. Six méthodes :

1. **Naïve** : tous les mois à venir valent le dernier mois connu (décembre 2024). Elle ignore la saison.
2. **Naïve saisonnière** : chaque mois à venir vaut le même mois de l'an dernier.
3. **Naïve saisonnière × croissance** : le même mois de l'an dernier, multiplié par la croissance de la dernière année (le rapport des douze derniers mois aux douze précédents).
4. **Moyenne des douze derniers mois** : une valeur plate, la moyenne de 2024.
5. **Tendance linéaire × indices saisonniers** : on désaisonnalise la série d'entraînement avec les indices de 5.1.4, on ajuste une droite, on la prolonge et on remultiplie par les indices.
6. **Lissage exponentiel de Holt-Winters** : un modèle qui met à jour, chaque mois, un niveau, une pente et des coefficients saisonniers, avec des poids qui décroissent avec l'ancienneté (version multiplicative, avec `statsmodels`).

```python
F, train, test = O.previsions_mensuelles(m)                    # entraînement : 2023-2024 ; test : 2025 ; six méthodes
tab = O.tableau_erreurs(F, train, test)                        # MAE, RMSE, MAPE, MASE et biais de chaque méthode
print(tab.round(1).to_string())
```
<!--sortie-->
```text
                                    MAE     RMSE  MAPE %  MASE  biais %
méthode                                                                
naïve (dernier mois)            51330.5  54712.6    52.8  11.2     42.5
naïve saisonnière               11487.8  13381.1    10.2   2.5    -10.2
naïve saisonnière × croissance   8148.3   9662.2     7.2   1.8     -6.2
moyenne des 12 derniers mois    20528.8  30337.0    16.7   4.5    -10.2
tendance linéaire × indices      7792.3   8990.7     7.0   1.7     -6.2
Holt-Winters                     8019.8   9184.9     7.1   1.7     -6.3
```


![Les prévisions de 2025 (pointillés) face au réalisé (trait épais gris foncé), pour trois méthodes.](figures/ch05-previsions-2025.png)

Les enseignements se lisent dans le tableau et sur la figure.

- La **naïve** est inutilisable (MAPE de 52,8 %) : elle prend décembre, le meilleur mois, pour le niveau de toute l'année suivante. Elle est pourtant la prévision de quiconque regarde « le dernier chiffre ».
- La **moyenne des douze derniers mois** (16,7 %) ne connaît pas la saison. Dès qu'une série est saisonnière, une méthode plate est toujours battue.
- La **naïve saisonnière** (10,2 %) est déjà un bon point de départ : elle connaît la saison et ne coûte rien. **Elle se trompe** parce qu'elle suppose que 2025 sera égale à 2024.
- Les trois méthodes qui ajoutent une **croissance** font mieux : 7,2 % pour la naïve saisonnière multipliée par la croissance passée (+4,4 %), 7,0 % pour la tendance linéaire avec indices, 7,1 % pour Holt-Winters. Ces trois chiffres sont **proches** : sur 24 mois d'historique, la sophistication n'achète presque rien.

Observons aussi le **biais** : toutes les méthodes sérieuses sous-estiment 2025 de -6,2 % environ (la tendance linéaire prévoit 1 242 249 € pour l'année contre 1 324 764 € réalisés). Le biais est **systématique**, pas aléatoire : 2025 a progressé de 11,4 %, soit bien plus que les +4,4 % observés sur la dernière année d'entraînement, parce que le prix a augmenté de 3 % et que le canal Site a accéléré. **Aucun modèle ne pouvait le savoir** en n'ayant vu que 2023 et 2024 ; c'est ce qui sépare une erreur de méthode d'un changement de régime.

> 💡 **Intuition.** Une prévision simple est une **hypothèse de continuité** : « l'avenir ressemblera au passé, à la saison et à la tendance près ». Quand la continuité casse (un prix, un concurrent, une panne), toutes les méthodes simples se trompent **ensemble**, du même côté. Le rôle de l'analyste est alors de le dire, pas de changer de modèle jusqu'à ce que l'erreur diminue.

### 5.2.3 Évaluer honnêtement une prévision

Un tableau d'erreurs n'a de valeur que si le protocole qui l'a produit est honnête. Trois règles.

**Règle 1 : on découpe dans le temps, jamais au hasard.** Pour des clients indépendants, on peut tirer un jeu de test au sort (volume I, section 1.3). Pour une série temporelle, mélanger les mois revient à prédire février 2025 en connaissant janvier et mars 2025 : c'est de la **fuite d'information temporelle**. L'entraînement doit précéder le test, et **rien** de ce qui sert à construire la prévision (indices, tendance, paramètres) ne doit avoir vu le test.

Pour mesurer la fuite, recalculons la prévision « tendance × indices » en utilisant, pour les indices saisonniers, les 36 mois (donc en y mêlant 2025) au lieu des seuls 24 mois d'entraînement.

```python
idx_tout = O.indices_saisonniers(m)                              # indices calculés avec 2025 dedans : TRICHERIE
b = np.polyfit(np.arange(24), (train / O.indices_saisonniers(train).reindex(train.index.month).values).values, 1)
f_triche = np.polyval(b, np.arange(24, 36)) * idx_tout.reindex(test.index.month).values
print("MAPE honnête :", round(tab.loc["tendance linéaire × indices", "MAPE %"], 1), "% | avec fuite :", round(O.mape(test, f_triche), 1), "%")
```
<!--sortie-->
```text
MAPE honnête : 7.0 % | avec fuite : 6.0 %
```


L'erreur tombe de 7,0 % à 6,0 % : la fuite améliore **artificiellement** le résultat en laissant la méthode voir les saisons de 2025. En production, ce gain disparaîtrait.

**Règle 2 : on mesure l'erreur avec la bonne règle.** Quatre mesures courantes, que l'on illustre sur trois mois de réalisé $y=(100,\,120,\,80)$ et de prévision $f=(110,\,100,\,90)$ : les erreurs sont $(+10,\,-20,\,+10)$ en valeur absolue (10, 20, 10).

| Mesure | Formule | Exemple | Ce qu'elle dit |
|---|---|---|---|
| **MAE** (erreur absolue moyenne) | moyenne de $\lvert y-f\rvert$ | 13,3 | l'erreur typique, **dans l'unité** de la série (ici des euros) |
| **RMSE** (racine de l'erreur quadratique moyenne) | $\sqrt{\text{moyenne de }(y-f)^2}$ | 14,1 | comme la MAE, mais **punit les grosses erreurs** ; toujours ≥ MAE |
| **MAPE** (erreur absolue moyenne en %) | moyenne de $\lvert y-f\rvert/\lvert y\rvert$ | 13,1 % | un **pourcentage**, comparable entre séries |
| **MASE** (erreur absolue relative à la naïve) | MAE divisée par l'erreur d'une naïve saisonnière sur l'entraînement | — | inférieure à 1 : meilleure que la référence |


Le MAPE est la mesure la plus répandue **et la plus trompeuse**. Elle explose quand la valeur réelle est petite (diviser par un jour de faible chiffre d'affaires), et elle est **asymétrique** : prévoir 150 quand on a réalisé 100 coûte 50 %, mais prévoir 100 quand on a réalisé 150 ne coûte que 33 % (la division se fait par le réalisé). Une méthode qui sous-estime est donc avantagée. Pour une série quotidienne, préférez la **MAE** ; pour comparer des séries d'ordres de grandeur différents, la **MASE** est plus sûre. Et quelle que soit la mesure, **annoncez-la** : « MAPE de 7 % » ne veut rien dire sans le pas (jour ? mois ?) et l'horizon.

**Règle 3 : on compare à la référence naïve saisonnière.** Une erreur de 7 % paraît bonne ou mauvaise selon ce qu'on aurait obtenu sans effort. Ici, la naïve saisonnière fait 10,2 % : tout modèle qui ne fait pas nettement mieux n'a pas de raison d'être.

### 5.2.4 Plusieurs origines : ne pas juger sur un seul test

Un seul découpage (2025 entière) est un **seul tirage** : une méthode peut le gagner par chance. On juge plus solidement en répétant l'exercice à **plusieurs dates d'origine** : on « se place » à une date, on prévoit les 28 jours suivants avec ce que l'on savait ce jour-là, on compare, puis on avance d'une semaine. Sur 2025, cela fait 48 origines.

Cette fois, on prévoit la série **quotidienne** à un horizon de 28 jours avec cinq méthodes : la naïve saisonnière de 7 jours (la semaine dernière se répète), la moyenne des quatre mêmes jours de semaine, le même jour de l'an dernier, ce dernier multiplié par le rapport du niveau récent (28 derniers jours) à celui de l'année précédente, et Holt-Winters avec saison hebdomadaire.

```python
y = j["chiffre_affaires"]
mae_o, tot_o = O.origines(y)                                    # 48 origines hebdomadaires en 2025, horizon 28 jours
print(mae_o.mean().round(0).to_dict())                          # MAE quotidienne moyenne, en euros
```
<!--sortie-->
```text
{'naïve saisonnière 7 j': 891.0, 'moyenne des 4 mêmes jours': 802.0, "même jour l'an dernier": 872.0, 'an dernier × niveau récent': 897.0, 'Holt-Winters (7 j)': 718.0}
```


```text
                            MAE par jour (€)  erreur absolue sur 28 jours (%)  biais sur 28 jours (%)  écart-type du biais (points)
naïve saisonnière 7 j                  891.0                             10.4                    -3.4                          12.8
moyenne des 4 mêmes jours              802.0                             11.7                    -2.7                          16.0
même jour l'an dernier                 872.0                              9.8                    -9.6                           5.4
an dernier × niveau récent             897.0                              7.2                     0.2                           9.0
Holt-Winters (7 j)                     718.0                             10.9                    -4.4                          12.7
```

![Erreur sur le total des 28 jours suivants, pour chacune des 48 origines (la boîte contient la moitié des origines ; le trait rouge est la médiane).](figures/ch05-origines.png)

Le verdict dépend de **ce que l'on prévoit**. À l'échelle de la journée, la meilleure méthode est Holt-Winters avec une MAE de 718 € par jour (contre 891 € pour la naïve de 7 jours), sur un chiffre d'affaires moyen de 3 629 € : l'erreur quotidienne reste d'environ 20 %, ce qui est **énorme** et qu'aucune méthode ne réduira (5.2.6 le montre). À l'échelle du **total des 28 jours**, la meilleure méthode est « l'an dernier × niveau récent », qui se trompe en moyenne de 7,2 % (contre 10,9 % pour Holt-Winters), parce que **la saison annuelle compte plus que la structure hebdomadaire** quand on additionne un mois.

On lit aussi sur la figure un deuxième enseignement : deux méthodes de **même erreur moyenne** n'ont pas la même **dispersion**. Une prévision dont l'erreur varie de −20 % à +15 % selon l'origine est plus risquée qu'une prévision qui se trompe toujours de 8 %, même si les deux ont le même écart moyen.

> ⚠️ **Précaution.** Les 48 origines ne sont pas indépendantes : deux origines voisines (à sept jours d'écart) partagent 21 jours sur 28 de la période prévue. L'échantillon efficace est plus proche de douze origines que de 48 ; une différence de quelques dixièmes de point entre deux méthodes n'est donc pas démontrée.

### 5.2.5 Un intervalle de prévision, pas seulement un chiffre

Une prévision sans intervalle est une promesse que personne ne peut tenir. L'idée la plus simple, et souvent la meilleure, est d'utiliser les **erreurs passées** de la méthode : on regarde la distribution du rapport « réalisé sur prévu » aux origines précédentes, et l'on en tire un intervalle.

On l'applique à la méthode « an dernier × niveau récent » sur le total des 28 jours. On **calibre** l'intervalle sur la première moitié des origines (les 24 premières semaines de 2025), puis on **vérifie** sur la seconde moitié combien de fois le réalisé tombe dedans.

```python
r = 1 / (1 + tot_o["an dernier × niveau récent"] / 100)         # réalisé / prévu à chaque origine
calib, test_o = r.iloc[:24], r.iloc[24:]
bas, haut = calib.quantile([0.10, 0.90])                         # intervalle « à 80 % »
print("intervalle :", round(bas, 2), "à", round(haut, 2), "× la prévision | couverture sur la seconde moitié :", round(test_o.between(bas, haut).mean() * 100), "%")
```
<!--sortie-->
```text
intervalle : 0.89 à 1.1 × la prévision | couverture sur la seconde moitié : 79 %
```


L'intervalle « à 80 % » est de 0,89 à 1,10 fois la prévision. La **couverture réelle** sur les 24 origines suivantes est de 79 %, **proche des 80 % visés** : ici, l'intervalle tient. Mais ne concluons pas trop vite : le biais moyen de la méthode passe de -0,8 % sur la première moitié à 1,9 % sur la seconde (la croissance s'est accélérée), et 24 origines qui se chevauchent ne permettent d'estimer une couverture qu'à une dizaine de points près. La règle est donc double : on **vérifie** la couverture de cette façon, et l'on **élargit** l'intervalle si elle est insuffisante, car l'avenir contient des régimes que le passé n'a pas connus.

Les méthodes de lissage exponentiel et les modèles ARIMA fournissent aussi des intervalles « théoriques » par simulation, fondés sur l'hypothèse d'erreurs indépendantes et symétriques. Ils sont utiles, et la même vérification s'impose.

### 5.2.6 Ce qu'aucune méthode ne peut faire : le plancher du hasard

Avant de chercher une meilleure méthode, demandons-nous : **quelle est la meilleure erreur possible ?** Même si l'on connaissait parfaitement l'espérance du chiffre d'affaires de chaque jour, le **hasard** (qui entre ce jour-là, ce qu'il achète) laisserait un écart irréductible. Comme nous avons programmé les données, nous pouvons mesurer ce plancher : on simule des journées dont on **connaît** le niveau moyen exact (35 commandes, tirées avec un tirage de Poisson), et l'on tire, pour chaque commande, un panier au hasard parmi les paniers réels de 2025.

```python
c25 = cmd.loc[cmd["date_commande"] >= "2025-01-01", "id_commande"]
paniers = lig[lig["id_commande"].isin(c25)].groupby("id_commande")["montant"].sum().values     # un montant par commande de 2025
rng = np.random.default_rng(0)
sim = np.array([rng.choice(paniers, rng.poisson(35.5)).sum() for _ in range(5000)])
print("dispersion du chiffre d'affaires d'un jour de niveau connu :", round(sim.std() / sim.mean() * 100), "% ; MAE plancher :", round(np.mean(np.abs(sim - sim.mean()))), "€")
```
<!--sortie-->
```text
dispersion du chiffre d'affaires d'un jour de niveau connu : 22 % ; MAE plancher : 630 €
```


Un jour de niveau connu fluctue de **22 %** autour de son espérance, soit une erreur absolue moyenne **incompressible** d'environ **630 €** par jour pour un chiffre d'affaires moyen de 3 627 €. Notre meilleure méthode quotidienne (Holt-Winters, 718 € en moyenne sur les origines) est **tout près de ce plancher** (à moins de cent euros) : il n'y a presque rien à gagner à la raffiner. À l'échelle du mois (1000 commandes en juin 2025), la dispersion tombe à 4,1 %, et l'erreur absolue moyenne plancher à environ **3,2 %**. Nos prévisions mensuelles font entre 7,0 % et 7,2 % : l'écart au plancher (de l'ordre de 4 points) n'est pas du hasard mais le **changement de régime** de 2025 (prix et accélération du Site), que les 24 mois d'historique ne pouvaient pas anticiper.

> ✅ **À retenir.**
> - Une **moyenne mobile** lisse pour regarder ; elle retarde de $(w-1)/2$ périodes et ne se prête pas à l'estimation statistique.
> - Une bonne prévision commence par des **références simples** (naïve saisonnière, naïve saisonnière × croissance) ; une méthode sophistiquée doit les **battre nettement**.
> - On évalue sur des données **postérieures** à l'entraînement, sans fuite, avec une mesure adaptée (MAE d'abord ; MAPE avec précaution), et à **plusieurs origines** quand c'est possible.
> - Une prévision se donne avec un **intervalle**, vérifié sur des origines que l'on n'a pas utilisées pour le calibrer.
> - Le hasard fixe un **plancher d'erreur** : au jour, environ 22 % ; au mois, quelques points. Une méthode qui s'en approche est suffisante.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.5 à 5.7 et exercices 5.7 à 5.10.


## 5.3 ➕ Pour aller plus loin : saisonnalité et prévision pour la planification

> 🧭 **Section complémentaire.** Elle prolonge 5.1 et 5.2 vers l'usage que fait la gérante d'une prévision : planifier. On y présente la régression avec variables indicatrices (qui sait tenir compte des promotions et des calendriers), le modèle ARIMA saisonnier (en une page), la prévision par canal, l'effet de l'horizon, les scénarios et la traduction d'une prévision en stocks et en personnel. Rien de ce qui suit n'est nécessaire au reste du volume.

Les méthodes de 5.2 prolongent le passé sans comprendre **pourquoi** les ventes varient. Or la gérante sait des choses sur l'avenir : le calendrier des promotions, les semaines de publicité prévues, les jours fériés. Une prévision pour la **planification** doit les utiliser, et leur donner un ordre de grandeur.

### 5.3.1 Régression avec variables indicatrices

L'idée est celle du chapitre 3 (régression linéaire), appliquée au temps : on explique le niveau de ventes de chaque jour par un **calendrier** (le mois, le jour de la semaine), des **décisions** (promotion, dépense publicitaire) et une **tendance**. Les variables qualitatives (le mois, le jour de semaine) deviennent des **indicatrices** : pour chaque modalité, une colonne qui vaut 1 si le jour est de cette modalité, 0 sinon. On prend le **logarithme** de la variable expliquée, pour que les coefficients se lisent comme des **pourcentages** d'effet (un coefficient de 0,17 correspond à une hausse d'environ 19 % : $e^{0{,}17}-1$).

On explique le **nombre de commandes** plutôt que le chiffre d'affaires : le nombre de commandes ne subit pas les remises et les hausses de prix, qui brouilleraient les effets que l'on veut isoler. Pour la publicité, on retient la dépense des **sept derniers jours** (en milliers d'euros), car l'effet d'un jour de publicité s'étale sur les jours suivants.

```python
dj = j.reset_index().assign(mois=lambda x: x["date"].dt.month, jds=lambda x: x["date"].dt.dayofweek, t=lambda x: (x["date"] - x["date"].min()).dt.days / 365.25)
dj["pub7"] = dj["depense_pub"].rolling(7, min_periods=1).sum() / 1000        # dépense des 7 derniers jours, en k€
tr5, te5 = dj[dj["date"] < "2025-01-01"], dj[dj["date"] >= "2025-01-01"]
mod = smf.ols("np.log(nb_commandes) ~ C(mois) + C(jds) + promo_active + pub7 + t", tr5).fit(cov_type="HAC", cov_kwds={"maxlags": 7})
pct = lambda c: (np.exp(mod.params[c]) - 1) * 100
print({c: round(float(pct(c)), 1) for c in ("promo_active", "pub7", "t")})
```
<!--sortie-->
```text
{'promo_active': 21.7, 'pub7': -0.8, 't': 4.7}
```


![Effets estimés par la régression (points bleus, avec leur intervalle à 95 %) et valeurs programmées (losanges rouges).](figures/ch05-effets-regression.png)

Un **jour de promotion** augmente les commandes de **21,7 %** (intervalle de 14,8 % à 29,0 %). La **vérité programmée** est de +18 % : elle tombe dans l'intervalle, et l'analyse a retrouvé l'ordre de grandeur. La **tendance** est estimée à 4,7 % par an (intervalle de 2,2 % à 7,3 %) pour 6 % programmés : même constat. Pour la **publicité**, l'estimation est de -0,8 % par millier d'euros dépensé sur sept jours, avec un intervalle de -6,4 % à 5,2 % : **le zéro est au milieu de l'intervalle**. La vérité programmée est un effet de +1,5 %, qui existe bel et bien ; l'analyse ne peut pas le distinguer du hasard avec trois ans de données quotidiennes, parce qu'un effet de 1,5 % est noyé dans les variations de ±24 % d'un jour. Ce n'est pas une preuve d'inefficacité : c'est un défaut de **puissance** (section 2.5), et seule une expérience délibérée (tester la publicité sur certaines semaines seulement) permettrait de trancher.

La régression sert aussi à **prévoir**, à condition de connaître à l'avance les variables : le calendrier est connu, le programme de promotion se décide, la publicité se planifie. Prévoyons les commandes de 2025 avec le modèle ajusté sur 2023-2024, puis convertissons en chiffre d'affaires avec le **panier moyen** de la période d'entraînement.

```python
pred = np.exp(mod.predict(te5)) * np.exp(mod.mse_resid / 2)                  # correction de la retransformation du logarithme
mens = pd.DataFrame({"réel": te5.set_index("date")["nb_commandes"], "prévu": pred.values}).resample("MS").sum()
print("MAPE mensuelle sur les commandes :", round(O.mape(mens["réel"], mens["prévu"]), 1), "% | biais :", round((mens["prévu"].sum() / mens["réel"].sum() - 1) * 100, 1), "%")
```
<!--sortie-->
```text
MAPE mensuelle sur les commandes : 4.4 % | biais : -2.9 %
```


Sur les **commandes**, l'erreur mensuelle est de 4,4 % (biais de -2,9 %), meilleure que celle de toutes les méthodes simples de 5.2 sur le chiffre d'affaires. Ce n'est pas tout à fait comparable : la régression bénéficie ici de la **connaissance du calendrier de promotion de 2025** et ne subit pas l'effet prix. Si l'on convertit en euros avec le panier moyen de 2023-2024 (99,3 €, alors qu'il vaut 102,3 € en 2025), l'erreur sur le chiffre d'affaires est de 6,6 % (biais de -5,8 %) : la hausse de prix de 2025, que le modèle n'a pas vue, ramène l'erreur au niveau des méthodes simples de 5.2 (7,0 % pour la meilleure).

> 💡 **Intuition.** La régression ne prédit pas mieux **parce qu'elle est plus savante**, mais parce qu'elle sait quelque chose de plus : le calendrier. Son avantage disparaît quand ce que l'on connaît à l'avance est faux ou incomplet, comme ici pour les prix.

### 5.3.2 Le modèle ARIMA saisonnier, en une page

Les modèles **ARIMA** sont la famille classique de la prévision statistique. Leur nom décrit leurs ingrédients : une partie **autorégressive** (AR : la valeur d'aujourd'hui dépend des valeurs d'hier et d'avant-hier), une partie **d'intégration** (I : on travaille sur les **variations** plutôt que sur les niveaux, pour enlever la tendance), une partie **moyenne mobile** (MA : on corrige à l'aide des erreurs récentes). La version **saisonnière** applique les mêmes idées au motif qui se répète (ici, tous les 7 jours). On note $(p,d,q)\times(P,D,Q)_s$ les ordres de chaque partie et la période $s$ ; le modèle $(1,1,1)\times(0,1,1)_7$ est un classique de la série quotidienne.

En pratique, `statsmodels` s'en occupe : on donne la série (en logarithme, pour que la saison soit multiplicative) et les ordres, et l'on obtient des prévisions avec leurs intervalles.

```python
import statsmodels.api as sm
ajust = sm.tsa.SARIMAX(np.log(y[:"2025-09-30"].iloc[-180:]), order=(1, 1, 1), seasonal_order=(0, 1, 1, 7)).fit(disp=False, maxiter=50)
prevu = np.exp(ajust.forecast(28))                                       # 28 jours après le 30 septembre 2025
print("octobre 2025 : prévu", round(prevu[:28].sum()), "€ pour 28 jours ; réalisé", round(y["2025-10-01":"2025-10-28"].sum()), "€")
```
<!--sortie-->
```text
octobre 2025 : prévu 107991 € pour 28 jours ; réalisé 108802 €
```


Pour octobre 2025 (28 jours), ce modèle prévoit 107 991 € pour 108 802 € réalisés. Un ajustement isolé ne prouve rien. Comparons donc, comme en 5.2.4, ce modèle à Holt-Winters sur 24 origines (une toutes les deux semaines en 2025), avec un horizon de 28 jours : la MAE quotidienne est de 718 € pour le modèle ARIMA saisonnier et de 690 € pour Holt-Winters ; l'erreur sur le total des 28 jours est de 12,4 % contre 10,0 %. **Le modèle plus savant ne fait pas mieux** : à ce pas et sur cette série, il retrouve la structure hebdomadaire que Holt-Winters capte déjà.

> ⚠️ **Prudence avec ARIMA.** Ces modèles demandent de **choisir des ordres**, de vérifier que la série est stationnaire après différenciation, et leurs paramètres peuvent devenir instables sur peu de données : en leur ajoutant des variables explicatives sur une série de 24 mois, nous avons obtenu des coefficients autorégressifs collés à 1 et des prévisions très biaisées. ARIMA vaut son prix quand on a **beaucoup de séries à prévoir** et le temps de les surveiller. Pour une boutique, le lissage exponentiel et la régression avec calendrier suffisent presque toujours.

### 5.3.3 Prévoir le total ou prévoir par canal ?

La gérante veut un chiffre pour l'ensemble, mais ses canaux n'évoluent pas pareil : de 2024 à 2025, la Boutique progresse de 0,5 %, les Réseaux de 13,4 % et le Site de 22,9 %. Deux stratégies : prévoir **directement le total**, ou prévoir **chaque canal** puis additionner (approche « du bas vers le haut »). Une troisième répartit la prévision du total selon les **parts** observées de chaque canal (« du haut vers le bas »).

```python
cc = O.ca_par_canal()                                             # chiffre d'affaires mensuel par canal
bu = sum(O.prevision_tendance_indices(cc[c], "2024-12-01") for c in cc)       # bas vers haut : somme des prévisions par canal
direct = O.prevision_tendance_indices(cc.sum(axis=1), "2024-12-01")            # prévision directe du total
reel = cc.sum(axis=1)["2025-01-01":]
print("MAPE du total : direct", round(O.mape(reel, direct), 1), "% | bas vers haut", round(O.mape(reel, bu), 1), "%")
```
<!--sortie-->
```text
MAPE du total : direct 7.0 % | bas vers haut 6.9 %
```


Pour le **total**, les deux approches sont équivalentes (6,99 % pour la prévision directe, 6,92 % pour la somme des canaux). L'intérêt de l'approche par canal est ailleurs : elle donne une prévision **pour chaque canal**, utile pour planifier le stock du site et le personnel de la boutique. Et pour cela, partir du total est **mauvais** : répartir le total selon les parts de 2023-2024 donne, pour le Site, une erreur de 19,5 % contre 10,5 % en prévoyant le canal directement, parce que la part du Site croît (la répartition fixe ne le sait pas). Pour la Boutique, les deux approches sont comparables (10,2 % et 9,3 %).

> 🧭 **En pratique.** Prévoyez au niveau où l'on **décide** : le total pour le budget, le canal pour la logistique, la catégorie pour les achats. Plus on descend, plus le hasard pèse (5.2.6) : au-dessous d'un certain niveau de détail, la prévision individuelle est moins fiable qu'une répartition du total.

### 5.3.4 L'effet de l'horizon

Un horizon plus long donne-t-il une prévision moins bonne ? Pour des **niveaux**, oui ; pour des **sommes**, pas forcément. Comparons deux méthodes sur le total de $h$ jours, pour $h$ de 7 à 84, à toutes les origines hebdomadaires de 2025 : la première prolonge le **niveau récent** (moyenne des 28 derniers jours), la seconde reprend le **même jour de l'an dernier**, ajusté du niveau récent.

```python
tab_h = O.erreur_par_horizon(y)                                   # erreur relative (%) sur le total de h jours
print(tab_h.round(1).to_string())
```
<!--sortie-->
```text
    niveau récent (plat)  an dernier × niveau récent
7                   12.9                        12.5
14                  11.2                         8.8
28                  10.5                         6.5
56                  11.9                         4.6
84                  12.9                         4.5
```


![Erreur relative sur le total des h jours suivants, selon l'horizon, pour une prévision plate et pour une prévision saisonnière.](figures/ch05-horizon.png)

La méthode **saisonnière** s'améliore avec l'horizon : l'erreur passe de 12,5 % pour une semaine à 6,5 % pour 28 jours et à 4,5 % pour 84 jours, parce que le hasard d'un jour à l'autre **se compense** quand on additionne, alors que la saison est connue. La prévision **plate** ne bénéficie pas de cet effet : elle ne s'améliore pas (12,9 % à une semaine, 12,9 % à 84 jours) parce qu'elle ignore que la saison **change** le niveau. Deux conséquences pratiques : prévoyez **des sommes** plutôt que des jours isolés, et donnez la saison à une prévision à long terme.

> ⚠️ **Piège.** L'erreur **relative** qui baisse avec l'horizon ne veut pas dire que le long terme est facile. Elle baisse parce que l'on additionne ; mais le **biais de niveau** (le changement de régime de 2025) ne s'efface pas, et il pèse davantage sur les horizons que l'on ne peut pas corriger en route.

### 5.3.5 Des scénarios plutôt qu'un chiffre

La gérante demande « combien en décembre prochain ? ». Une réponse honnête est un **chiffre central** accompagné de **scénarios** qui disent ce qui le ferait varier. Décembre 2025 a rapporté 183 845 €. Pour décembre 2026, la question est la **croissance**, et nous savons depuis 5.2 qu'elle est l'inconnue principale. Trois scénarios :

- **prudent** : la croissance de 2024 (+4,4 %), c'est-à-dire sans effet de prix ;
- **central** : la **tendance de fond** estimée en 5.1.6 (+6,5 % par an), sans nouvelle hausse de prix ;
- **avec hausse de prix** : la tendance de fond, plus un relèvement de prix de 3 % comme en 2025.

```python
dec25 = m["2025-12-01"]
scen = {"prudent": dec25 * (1 + 0.044), "central": dec25 * (1 + 0.065), "hausse de prix": dec25 * 1.065 * 1.03}
print({k: round(v) for k, v in scen.items()})
```
<!--sortie-->
```text
{'prudent': 191934, 'central': 195795, 'hausse de prix': 201669}
```


![Chiffre d'affaires mensuel des trois dernières années et trois scénarios pour décembre 2026.](figures/ch05-scenarios.png)

Les trois scénarios donnent 191 934 €, 195 795 € et 201 669 € pour décembre 2026. En comparaison, la méthode « tendance × indices » ajustée sur les 36 mois prévoit 190 904 €, **juste sous le scénario prudent** : la droite ajustée sur trois ans est un peu plus prudente que le scénario central, mais elle raconte la même histoire. L'écart entre le scénario prudent et le scénario avec hausse de prix est d'environ **5 %** : voilà l'ordre de grandeur de l'incertitude à déclarer, et il vient d'**une hypothèse** (le prix), pas du modèle.

Les scénarios servent aussi à **peser une décision**. Sur novembre, la régression de 5.3.1 donne l'effet d'une promotion : +21,7 % de commandes les jours de promotion. Le « Vendredi noir » couvre neuf jours de novembre ; sans lui, les commandes du mois baisseraient d'environ **6,1 %**, une fois l'effet des neuf jours retiré.


> 🧭 **En pratique.** Présentez trois chiffres et une phrase : « Entre X et Z, avec Y comme chiffre central ; l'écart vient surtout de la politique de prix ». Cela vaut mieux qu'un faux chiffre précis, et cela dit à la gérante **sur quoi elle a prise**.

### 5.3.6 De la prévision aux décisions : stock et personnel

Une prévision ne vaut que par les décisions qu'elle éclaire. Deux exemples chiffrés pour décembre 2026.

**Le personnel.** Le scénario central prévoit 195 795 € de chiffre d'affaires en décembre. Avec un panier moyen d'environ 100 €, cela fait environ 1 958 commandes, soit 63 par jour en moyenne. Les jours ne se valent pas : le samedi pèse 1,390 fois un jour moyen (5.1.7), soit environ 88 commandes un samedi de décembre. Si un collaborateur prépare environ **20 commandes par jour** (hypothèse illustrative : contrôle, emballage, expédition), il faut 5 personnes les samedis de pointe, contre 4 un jour moyen : dimensionner sur la moyenne laisserait chaque samedi en dessous de la charge. Pour couvrir l'incertitude, on vérifie le résultat sur le scénario **haut** (environ 3 % de commandes de plus), qui ne change pas ici le nombre de personnes.

**Le stock.** Pour un produit populaire, le stock de sécurité protège contre l'écart entre la demande prévue et la demande réelle pendant le délai de réapprovisionnement. Une formule classique : $\text{stock de sécurité}=z\times\sigma_j\times\sqrt{L}$, où $\sigma_j$ est l'écart-type de la demande **quotidienne**, $L$ le délai en jours et $z$ un coefficient lié au niveau de service visé ($z=1{,}65$ pour 95 %).


Pour le produit le plus vendu de novembre et décembre 2025, la demande est de 3,69 unités par jour en moyenne, avec un écart-type de 2,61. Pour un délai de réapprovisionnement de 14 jours et un niveau de service de 95 %, le stock de sécurité est d'environ **16 unités** ; le stock nécessaire au moment de commander est de 52 unités pour couvrir la demande attendue pendant le délai, plus ce stock de sécurité, soit **68 unités**. Un niveau de service plus exigeant (99 % ; $z=2{,}33$) augmente le stock de sécurité d'environ 40 % : **chaque point de service a un coût**, et c'est à la gérante de choisir.

### 5.3.7 Quand un modèle simple suffit

Résumons ce chapitre sur la question qui compte : **quel outil pour quelle situation ?**

| Situation | Outil recommandé | Pourquoi |
|---|---|---|
| Peu d'historique (moins de trois ans), décision à ± 10 % | Naïve saisonnière × croissance | Ne se trompe pas plus que les autres, s'explique en une phrase |
| Calendrier de promotions ou de publicité connu à l'avance | Régression avec indicatrices | Utilise ce que l'on sait de l'avenir, donne des effets chiffrés |
| Prévision quotidienne à court terme | Holt-Winters (saison de 7 jours) | Atteint presque le plancher du hasard |
| Prévision par canal ou catégorie | Méthode simple appliquée à chaque série, puis comparaison avec le total | Les parts changent ; la répartition fixe est mauvaise |
| Beaucoup de séries à suivre, des données longues | ARIMA saisonnier ou méthodes automatiques | Seulement si l'on a le temps de les surveiller |
| Changement de régime probable (prix, nouveau canal) | Scénarios | Aucun modèle ne le connaît : on dit ce que l'on suppose |

> ✅ **À retenir.**
> - La **régression avec indicatrices** (mois, jour, promotion, publicité, tendance) prévoit bien quand l'avenir **connu** est utilisé ; elle donne des effets en %, avec leur intervalle : la promotion se détecte, une publicité à +1,5 % reste dans le bruit.
> - Un modèle **ARIMA** n'est pas meilleur par nature : sur cette série, il fait jeu égal avec le lissage exponentiel, en demandant plus de soin.
> - Prévoyez **au niveau où l'on décide** ; les sommes sont plus faciles à prévoir que les jours isolés ; la saison aide d'autant plus que l'horizon est long.
> - Une prévision pour la planification se présente en **scénarios**, et se traduit en décisions (personnel de pointe, stock de sécurité) avec un niveau de service **choisi**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.8 et 5.9 et exercices 5.11 et 5.12.


## Bilan du chapitre 5

Vous savez maintenant :

- **décomposer** une série en **tendance, saison et résidu**, additif ou multiplicatif, et reconnaître que la saison est multiplicative quand son amplitude grandit avec le niveau (le rapport décembre/février reste proche de 2,5 alors que la différence en euros augmente) ;
- **comparer honnêtement** : à la même période de l'an dernier, ou en glissement sur douze mois, jamais de mois consécutifs sur une série saisonnière ; **somme** les montants avant de calculer un pourcentage ;
- **calculer des indices saisonniers** à la main (rapport à la moyenne mobile centrée, moyenné par position, normalisé), **désaisonnaliser**, et utiliser `seasonal_decompose` et STL ;
- **mesurer une tendance** par la pente du logarithme de la série désaisonnalisée, avec des erreurs robustes à l'autocorrélation, et la lire avec son intervalle ; séparer croissance de fond et **rupture** (le relèvement de prix de 2025) ;
- **tenir compte du calendrier** (jour de semaine, longueur et composition des mois) et **traiter les incidents** : les trouver (contrôles exacts, score z robuste), choisir un seuil selon le coût des erreurs, corriger ou signaler, et le documenter ;
- **lisser** (moyenne mobile simple, centrée, exponentielle) en connaissant le retard et la fausse régularité ;
- **prévoir** avec des références simples, **évaluer** sans fuite temporelle, avec une mesure adaptée et à plusieurs origines, **donner un intervalle** que l'on vérifie, et connaître le **plancher** du hasard ;
- (en option) **régresser** avec des indicatrices de calendrier et de décision, **comparer** à un ARIMA saisonnier, **prévoir par canal**, mesurer l'effet de l'**horizon**, bâtir des **scénarios** et en tirer des décisions de personnel et de stock.

Les chiffres du chapitre, qui répondent à la gérante :

| Question | Ce que nous avons mesuré |
|---|---|
| Les ventes progressent-elles vraiment ? | oui : 8,2 % par an en moyenne (intervalle 6,4 % à 10,0 %) ; en séparant le relèvement de prix de 2025, 6,5 % de croissance de fond (3,6 % à 9,6 %) et 3,5 % de saut de niveau |
| Comparaison à l'an dernier | +4,4 % en 2024, +11,4 % en 2025 ; glissement annuel de 4,4 % à fin 2024 à 11,4 % à fin 2025 |
| Saison | décembre 1,583 fois un mois moyen, février 0,677 ; samedi 1,390 fois un jour moyen, dimanche 0,657 |
| Incidents | au seuil 3,5, 4 incidents statistiques sur 7 trouvés (et 4 fausses alertes) ; au seuil 3, 7 sur 7 (et 11 fausses alertes) |
| Prévoir 2025 avec 2023-2024 | naïve saisonnière : MAPE 10,2 % ; avec croissance : 7,2 % ; tendance × indices : 7,0 % ; Holt-Winters : 7,1 % ; biais commun de -6,2 % (changement de régime) |
| Prévoir à 28 jours, jour par jour | MAE de 718 € par jour pour Holt-Winters, plancher du hasard d'environ 630 € ; sur le total des 28 jours, l'erreur est de 7,2 % pour la meilleure méthode |
| Décembre prochain | 191 934 € (prudent), 195 795 € (central), 201 669 € (avec hausse de prix de 3 %) ; modèle : 190 904 € |

**Le fil conducteur du chapitre tient en une phrase : une série temporelle se lit en séparant ce qui revient de ce qui change, et une prévision se juge à sa capacité à battre un chiffre simple, avec l'incertitude écrite à côté.** Les erreurs les plus coûteuses ne sont pas des erreurs de modèle ; ce sont des **changements de régime** (un prix, un canal) que personne ne pouvait voir dans l'historique, et que l'on doit nommer plutôt que de laisser un modèle les absorber.

> 🧭 **En pratique : liste de contrôle d'une analyse de série temporelle.**
> 1. Le pas est-il celui de la décision (jour, semaine, mois) ? Les mois sont-ils comparables (longueur, calendrier) ?
> 2. A-t-on cherché les incidents et les ruptures avant de décomposer, et consigné ce qu'on en a fait ?
> 3. La comparaison est-elle à la même période de l'an dernier (ou en glissement annuel) ?
> 4. Une référence naïve saisonnière a-t-elle été calculée, et la méthode retenue la bat-elle nettement ?
> 5. L'évaluation est-elle faite dans le temps (sans fuite), avec la mesure annoncée et, si possible, plusieurs origines ?
> 6. Chaque prévision est-elle accompagnée d'un intervalle ou de scénarios, et de ce qui les ferait changer ?

Le chapitre 6 traite d'un sujet qui touche tout ce qui précède : comment **choisir** les chiffres que l'on suit, c'est-à-dire concevoir des **indicateurs de performance** (KPI), les relier dans un **arbre**, et fixer des **cibles** et des **seuils** qui évitent de réagir au bruit.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.9 (composantes et comparaisons, indices saisonniers et décomposition, calendrier, incidents, moyennes mobiles, prévoir 2025, plusieurs origines, régression avec indicatrices, décembre prochain et planification) et exercices 5.1 à 5.12.
