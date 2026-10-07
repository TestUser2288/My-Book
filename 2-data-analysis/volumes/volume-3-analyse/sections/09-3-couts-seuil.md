## 9.3 Analyse des coûts et seuil de rentabilité

Pourquoi les 112 751 € de chiffre d'affaires supplémentaire n'ont-ils laissé que 22 280 € de résultat ? Parce que **tous les coûts ne réagissent pas de la même façon à l'activité** : certains suivent les ventes, d'autres tombent chaque mois quoi qu'il arrive. Séparer les deux est le geste central de l'analyse des coûts, et il conduit à trois questions pratiques : à partir de quel chiffre d'affaires gagne-t-on de l'argent ? Quelle est la marge de sécurité ? Quel canal rapporte vraiment ?

### 9.3.1 Coûts fixes et coûts variables

Un **coût variable** augmente quand l'activité augmente (les marchandises, les commissions de paiement, la livraison) ; un **coût fixe** ne dépend pas, à court terme, de l'activité (le loyer, les amortissements, la plupart des salaires). La frontière est souvent floue : un salaire peut être fixe pour le contrat et variable par les heures supplémentaires ; une dépense de publicité est fixe **une fois décidée** mais elle est choisie en fonction de la saison.

Plutôt que de classer à l'intuition, on peut **mesurer** : pour chaque ligne de coût, on cherche comment la dépense mensuelle varie avec le chiffre d'affaires du mois, par une régression linéaire sur les 36 mois :

$$\text{coût}_{\text{mois}} = a + b\times \text{CA}_{\text{mois}}.$$

La pente $b$ est la **part variable** (les centimes de coût par euro de chiffre d'affaires), la constante $a$ la **part fixe mensuelle**.

```python
r = reg[["pente", "constante", "r2", "ic_bas", "ic_haut"]].copy()
r.index = ["Achats", "Personnel", "Loyers", "Marketing", "Livraison", "Frais bancaires", "Amortissements", "Autres charges"]
print(r.drop(index="Amortissements").round(3).to_string())
```
<!--sortie-->
```text
                 pente  constante     r2  ic_bas  ic_haut
Achats           0.610   1832.130  0.989   0.587    0.633
Personnel        0.046   7178.626  0.923   0.042    0.051
Loyers           0.002   5070.676  0.057  -0.001    0.004
Marketing        0.043   1524.341  0.595   0.030    0.055
Livraison        0.033   -486.180  0.929   0.029    0.036
Frais bancaires  0.018     -0.246  1.000   0.018    0.018
Autres charges   0.003   1771.860  0.118   0.000    0.006
```

Chaque ligne se lit ainsi : les **achats** suivent le chiffre d'affaires à 0,610 € par euro (intervalle de confiance de 0,587 à 0,633) avec un $R^2$ de 0,99 : ce sont des coûts **purement variables**. Les **frais bancaires** valent 0,018 € par euro, sans aucun bruit ($R^2=1{,}00$) : une commission proportionnelle. La **livraison** est variable (0,033 €, $R^2=0{,}93$). Le **personnel** a une part fixe de 7 179 € par mois et une part variable de 0,046 € par euro (de 0,042 à 0,051), ce qui s'interprète comme des primes ou des heures supplémentaires. Les **loyers**, les **autres charges** et les **amortissements** ont une pente nulle ou négligeable : ils sont **fixes**.

Le **marketing** demande de la prudence : sa pente est de 0,043 € par euro, mais le $R^2$ n'est que de 0,60. Ce n'est pas un lien mécanique entre les ventes et la publicité : la dépense est **décidée selon le calendrier** (plus forte en novembre, décembre et au printemps), précisément quand les ventes sont fortes. Le traiter comme variable reviendrait à croire que les ventes **provoquent** la dépense ; nous le traiterons donc comme un coût **fixe** à l'échelle de l'année (une décision budgétaire), tout en gardant en tête que c'est un choix de modèle.

> ⚠️ **Piège : une pente n'est pas une loi.** La régression décrit **ce qui s'est passé** sur 36 mois, avec les arrondis et les saisons. Elle suppose que la relation est linéaire et stable ; un nouveau loyer, une renégociation de commissions la rendraient fausse. Et, comme toute estimation, elle a un intervalle de confiance : celui du personnel va de 0,042 à 0,051, soit un facteur 1,2 entre les bornes.

### 9.3.2 La marge sur coûts variables et le point mort

Avec cette séparation, on obtient deux quantités :

- les **coûts variables** de 2025 : achats nets de la variation de stock, livraison, frais bancaires et la part variable du personnel (0,046 € par euro de chiffre d'affaires), soit 789 506 €, c'est-à-dire **71,5 %** du chiffre d'affaires ;
- les **coûts fixes** de 2025 : tout le reste (loyers, marketing, amortissements, autres charges et la part fixe du personnel), soit 274 584 €.

La **marge sur coûts variables** (MCV) est le chiffre d'affaires moins les coûts variables : c'est ce qui reste **pour payer les coûts fixes**, puis pour faire le résultat. Son **taux** est de $1-0{,}715=28{,}5\ \%$ : sur chaque euro vendu, 28,5 centimes contribuent aux coûts fixes.

Le **seuil de rentabilité** (ou **point mort**) est le chiffre d'affaires pour lequel la MCV couvre exactement les coûts fixes, c'est-à-dire pour lequel le résultat est nul :

$$\text{CA}^{*}=\frac{\text{coûts fixes}}{\text{taux de MCV}}.$$

Pourquoi cette formule ? Le résultat vaut $R=\tau_{\text{MCV}}\times\text{CA}-\text{CF}$. Il s'annule quand $\text{CA}=\text{CF}/\tau_{\text{MCV}}$.

```python
x = ann.loc[2025]
cv = (x["achats"] - x["variation_stock"]) + x["livraison"] + x["frais_bancaires"] + reg.loc["frais_personnel", "pente"] * x["ca_ht"]
cf = x["charges_totales"] - x["livraison"] - x["frais_bancaires"] - reg.loc["frais_personnel", "pente"] * x["ca_ht"]
pm = O.point_mort(x["ca_ht"], cv, cf)
print("coûts variables :", fr(cv), "€ (", fr(cv / x["ca_ht"] * 100, 1), "% du CA ) | coûts fixes :", fr(cf), "€")
print("taux de MCV :", fr(pm["taux_mcv"] * 100, 1), "% | seuil de rentabilité :", fr(pm["seuil"]), "€ | contrôle du résultat :", fr(x["ca_ht"] - cv - cf), "€")
```
<!--sortie-->
```text
coûts variables : 789 506 € ( 71,5 % du CA ) | coûts fixes : 274 584 €
taux de MCV : 28,5 % | seuil de rentabilité : 963 968 € | contrôle du résultat : 39 879 €
```

Le seuil de rentabilité de 2025 est de **963 968 €** de chiffre d'affaires, contre 1 103 969 € réalisés. Le résultat de contrôle retombe bien sur le résultat d'exploitation (39 879 €). En commandes : avec un panier moyen de 85,27 € hors taxes (1 103 969 € pour 12 946 commandes), le seuil correspond à **11 304 commandes**, contre 12 946 réalisées.

```python hide
O.fig_point_mort(x["ca_ht"], cv, cf, pm, "figures/ch09-point-mort-2025.png")
```

![Droites des produits (bleu) et des coûts totaux (rouge) selon le chiffre d'affaires annuel de 2025 : elles se croisent au point mort, à 964 k€ ; la boutique a réalisé 1 104 k€, au-dessus du seuil. Les coûts fixes (pointillés) sont de 275 k€ à chiffre d'affaires nul.](figures/ch09-point-mort-2025.png)

> 💡 **Intuition.** Sous le point mort, chaque euro de chiffre d'affaires **réduit la perte** de 28,5 centimes ; au-dessus, chaque euro **augmente le bénéfice** de 28,5 centimes. La droite des coûts totaux est moins pentue que celle des produits, parce que les coûts variables ne prennent que 71,5 % de chaque euro : la différence est la marge qui construit le résultat.

### 9.3.3 Marge de sécurité et levier opérationnel

Deux indicateurs complètent le point mort.

La **marge de sécurité** est la part du chiffre d'affaires qui pourrait disparaître avant d'atteindre le seuil : $(\text{CA}-\text{CA}^{*})/\text{CA}$. En 2025, elle est de **12,7 %** : si le chiffre d'affaires baisse de plus de 12,7 %, l'entreprise perd de l'argent.

Le **levier opérationnel** (ou degré de levier) est le rapport de la MCV au résultat : il dit **de combien de pour cent bouge le résultat quand le chiffre d'affaires bouge de 1 %**. En 2025, il vaut 7,9 : +1 % de chiffre d'affaires donne environ +7,9 % de résultat (et −1 % donne −7,9 %). Plus les coûts fixes sont lourds, plus l'effet est grand, dans les deux sens.

```python
comp = {}
for an in (2023, 2024, 2025):
    y = ann.loc[an]
    pv_ = reg.loc["frais_personnel", "pente"] * y["ca_ht"]
    cv_ = (y["achats"] - y["variation_stock"]) + y["livraison"] + y["frais_bancaires"] + pv_
    cf_ = y["charges_totales"] - y["livraison"] - y["frais_bancaires"] - pv_
    comp[an] = O.point_mort(y["ca_ht"], cv_, cf_) | {"cf": cf_, "ca": y["ca_ht"]}
print(pd.DataFrame(comp).T[["ca", "cf", "seuil", "marge_securite", "levier"]].round(3).to_string())
```
<!--sortie-->
```text
             ca          cf       seuil  marge_securite  levier
2023   949111.0  244648.722  887600.830           0.065  15.430
2024   991218.0  251947.937  926493.471           0.065  15.314
2025  1103969.0  274583.882  963967.803           0.127   7.885
```

Les trois années se comparent : le seuil passe de 887 601 € à 963 968 € (+8,6 %), les coûts fixes de 244 649 € à 274 584 € (+12,2 %), mais le chiffre d'affaires a progressé plus vite, de sorte que la marge de sécurité **double** (de 6,5 % à 12,7 %) et que le levier opérationnel **est divisé par deux** (de 15,4 à 7,9). C'est la seconde réponse à la gérante, qui dit plus que le simple taux de marge : **l'entreprise s'est éloignée du précipice**. En 2023 et 2024, une baisse de 6,5 % des ventes aurait suffi à effacer le résultat ; en 2025, il en faudrait près du double. Ce qui ressemble à un faible profit est en réalité un profit **moins fragile**.

> 🧭 **En pratique.** Le levier opérationnel est un **grossissement** : il amplifie les bonnes années et les mauvaises. Une activité saisonnière avec des coûts fixes lourds (loyers, salaires) est très sensible : un mois de décembre raté pèse sur toute l'année, car décembre rapporte à lui seul près de la moitié du résultat.

### 9.3.4 La rentabilité par canal : le piège des clés de répartition

La gérante veut savoir quel canal (Boutique, Site, Réseaux) rapporte de l'argent. On calcule pour chacun la marge brute (ventes hors taxes moins coût d'achat des marchandises vendues), puis on lui retire ses coûts.

- Certains coûts sont **directs** : la livraison (seulement Site et Réseaux), les frais bancaires (au prorata des ventes), le marketing (nous affectons les dépenses de publicité payante et d'e-mails au Site, et les dépenses sur les réseaux sociaux au canal Réseaux : c'est une **hypothèse** du chapitre).
- D'autres sont **communs** : le personnel, les loyers, les amortissements, les autres charges. Pour les imputer aux canaux, il faut une **clé de répartition**, c'est-à-dire un choix.

La **contribution** d'un canal est sa marge brute moins ses coûts directs : c'est ce qu'il apporte au paiement des coûts communs. Le **résultat** d'un canal est sa contribution moins sa part des coûts communs, qui dépend de la clé.

```python
g, tot = O.rentabilite_canal(cmd, lig, prod, cr, camp)
t = g[["ca_ht", "marge_brute", "contribution", "resultat_cle_ca", "resultat_cle_commandes"]].round(0).astype(int)
t.columns = ["CA HT", "Marge brute", "Contribution", "Résultat (clé CA)", "Résultat (clé commandes)"]
print(t.to_string())
```
<!--sortie-->
```text
           CA HT  Marge brute  Contribution  Résultat (clé CA)  Résultat (clé commandes)
canal                                                                                   
Boutique  467478       177622        169207              62194                     62975
Réseaux   121729        46392         15683             -12183                    -12154
Site      514763       195003        109595              -8242                     -9052
```

```python hide
O.fig_canaux(g, "figures/ch09-canaux.png")
```

![Contribution et résultat par canal en 2025, avec deux clés de répartition des charges communes. La Boutique gagne dans tous les cas ; les canaux Réseaux et Site sont en perte avec chaque clé, tout en apportant une contribution positive.](figures/ch09-canaux.png)

La **Boutique** rapporte 169 207 € de contribution et 62 194 € de résultat avec la clé « chiffre d'affaires » (62 975 € avec la clé « commandes »). Les canaux **Réseaux** et **Site** ont chacun une contribution positive (15 683 € et 109 595 €) mais un **résultat négatif** une fois leur part des coûts communs imputée (−12 183 € et −8 242 € avec la clé « chiffre d'affaires »). Le choix de la clé change les chiffres de quelques centaines d'euros (ici, 9 052 € de perte pour le Site avec la clé « commandes »), mais **pas la conclusion**, parce que les deux clés répartissent les coûts communs presque de la même façon : le panier moyen est voisin d'un canal à l'autre (environ 85 € hors taxes).

La question « faut-il arrêter le canal Réseaux ? » montre le danger de lire le résultat par canal : arrêter Réseaux **supprimerait sa contribution de 15 683 €** ; les coûts communs qu'on lui impute (27 866 €) ne disparaîtraient pas pour autant (le loyer reste le même). Le résultat de l'entreprise **baisserait** de 15 683 €, et non pas augmenterait de 12 183 €. À l'inverse, si une réorganisation permet de supprimer une partie réelle des coûts communs, le calcul change. La règle pratique : **pour décider de garder ou d'arrêter un canal, on regarde la contribution (et ce qu'on peut réellement économiser), pas le résultat après répartition.**

La somme des résultats par canal (41 769 €) diffère du résultat d'exploitation de l'entreprise (39 879 €) de 1 890 € : c'est la **variation de stock** de −1 888 €, qui n'est affectée à aucun canal, plus 2 € d'arrondis.

> ⚠️ **Piège : les clés de répartition fabriquent des résultats.** Répartir au prorata du chiffre d'affaires revient à dire que chaque euro vendu coûte autant en personnel et en loyer ; répartir au prorata des commandes dit que chaque commande coûte autant. Aucune clé n'est « vraie ». Si deux clés raisonnables donnent des conclusions opposées, la bonne question n'est pas « laquelle choisir ? » mais « **que me dit la contribution, qui ne dépend d'aucune clé ?** ».

### 9.3.5 Hausse de prix ou hausse de volume ?

Le modèle coûts fixes / coûts variables permet de chiffrer deux leviers très différents. Une **hausse de prix de 1 %** à volume égal ajoute 1 % au chiffre d'affaires **sans ajouter** d'achats ni de livraison ; seuls les coûts proportionnels aux ventes (frais bancaires, part variable du personnel) augmentent. Une **hausse de volume de 1 %** ajoute 1 % au chiffre d'affaires **et** 1 % à tous les coûts variables.

```python
ca25 = x["ca_ht"]
liees_ca = x["frais_bancaires"] + reg.loc["frais_personnel", "pente"] * ca25          # coûts proportionnels au chiffre d'affaires
prix = 0.01 * ca25 - 0.01 * liees_ca
volume = 0.01 * (ca25 - cv)
print("effet sur le résultat : +1 % de prix :", fr(prix), "€ ( +", fr(prix / x["resultat_exploitation"] * 100, 1), "% ) | +1 % de volume :", fr(volume), "€ ( +", fr(volume / x["resultat_exploitation"] * 100, 1), "% )")
```
<!--sortie-->
```text
effet sur le résultat : +1 % de prix : 10 328 € ( + 25,9 % ) | +1 % de volume : 3 145 € ( + 7,9 % )
```

**Un point de prix vaut trois points de volume** : +1 % de prix rapporte 10 328 € (+25,9 % de résultat), +1 % de volume 3 145 € (+7,9 %), soit un rapport de 3,3. C'est le résultat le plus utile du chapitre pour une discussion avec la gérante : une hausse de prix de 3 % faite en 2025 a probablement contribué plus au résultat que la hausse du nombre de commandes. Attention toutefois : la hausse de prix **n'est pas gratuite**, car elle peut faire baisser le volume ; on cherche alors la baisse de volume qui annule le gain, et c'est le sujet de l'analyse de sensibilité (chapitre 13).

> ✅ **À retenir.** Séparer coûts **fixes** et **variables** (par régression, avec un intervalle) donne le **point mort**, la **marge de sécurité** et le **levier opérationnel**. Pour juger un canal ou un produit, on regarde sa **contribution** plutôt que son résultat après clé de répartition, et l'on garde à l'esprit qu'**un point de prix vaut bien plus qu'un point de volume** quand les coûts variables sont élevés.

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : applications 9.3 à 9.5 et exercices 9.7 à 9.9.
