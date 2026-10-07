## 7.2 Décomposer un écart : prix, volume, mix

### 7.2.1 Trois questions dans un écart

Quand le chiffre d'affaires dépasse le budget, trois choses ont pu se passer, qui n'appellent pas les mêmes décisions.

- On a **vendu plus d'unités** que prévu : c'est l'effet **volume**.
- On les a vendues à un **autre prix** que prévu (hausse de tarif, promotions) : c'est l'effet **prix**.
- On a vendu **une autre combinaison** de produits ou de canaux : davantage de ce qui est cher, moins de ce qui est bon marché : c'est l'effet **mix**.

La décomposition prix-volume-mix répartit l'écart **exactement** entre ces trois effets, de sorte que leur somme redonne l'écart total à l'euro près. C'est l'outil le plus utile de l'analyse d'écarts, et aussi le plus mal compris, parce que ses formules paraissent arbitraires. Elles ne le sont pas : chacune répond à une question précise.

### 7.2.2 Un exemple à la main

Trois produits, un budget, un réalisé.

| Produit | Quantité budget | Prix budget | CA budget | Quantité réalisée | Prix réalisé | CA réalisé |
|---|---|---|---|---|---|---|
| A | 100 | 10 € | 1 000 € | 90 | 10,50 € | 945 € |
| B | 50 | 20 € | 1 000 € | 80 | 20 € | 1 600 € |
| C | 50 | 30 € | 1 500 € | 40 | 33 € | 1 320 € |
| **Total** | **200** | **17,50 € en moyenne** | **3 500 €** | **210** | **18,40 € en moyenne** | **3 865 €** |

L'écart est de $3\,865-3\,500=+365$ €. Décomposons-le en trois étapes.

**Le volume.** On a vendu $210-200=10$ unités de plus. À quel prix les valoriser ? Au **prix moyen du budget**, 17,50 € : $10\times17{,}5=+175$ €. C'est l'effet qu'aurait eu la hausse du nombre d'unités si la combinaison de produits et les prix étaient restés ceux du budget.

**Le mix.** Avec 210 unités et la combinaison du budget (50 % de A, 25 % de B, 25 % de C), on aurait vendu 105 A, 52,5 B et 52,5 C. On a vendu 90, 80 et 40 : −15 A, +27,5 B, −12,5 C. Chacun est valorisé **au prix du budget** : $-15\times10+27{,}5\times20-12{,}5\times30=-150+550-375=+25$ €. Le mix est légèrement favorable : on a vendu relativement plus de B que de A.

**Le prix.** Reste l'écart de prix, valorisé sur les **quantités réalisées** : $90\times(10{,}5-10)+80\times0+40\times(33-30)=45+0+120=+165$ €.

Total : $175+25+165=365$ €. La vérification par la fonction du chapitre (écrite pour que le livre et le cahier utilisent les mêmes formules) :

```python
ex = pd.DataFrame({"produit": list("ABC"), "quantite_budget": [100, 50, 50], "quantite_reel": [90, 80, 40],
                   "ca_budget": [1000, 1000, 1500], "ca_reel": [945, 1600, 1320]})
r = O.pvm_ca(ex, ["produit"])
print({k: round(v, 2) for k, v in r.items()})
print("somme des effets = écart total :", round(r["volume"] + r["mix"] + r["prix"], 6) == round(r["ecart"], 6))
```
<!--sortie-->
```text
{'volume': 175.0, 'mix': 25.0, 'prix': 165.0, 'total': 365.0, 'ecart': 365.0}
somme des effets = écart total : True
```

> 📐 **Les formules.** Notons $Q$ les quantités, $P$ les prix, $b$ le budget, $r$ le réalisé, $i$ le produit (ou la ligne de budget), et $P_b^{\text{moy}}=\sum_i Q_{b,i}P_{b,i}/\sum_i Q_{b,i}$ le prix moyen du budget. Alors
>
> $$\underbrace{(Q_r-Q_b)\,P_b^{\text{moy}}}_{\text{volume}}\;+\;\underbrace{\sum_i\bigl(Q_{r,i}-Q_r\,s_{b,i}\bigr)P_{b,i}}_{\text{mix}}\;+\;\underbrace{\sum_i Q_{r,i}\,(P_{r,i}-P_{b,i})}_{\text{prix}}\;=\;\sum_i Q_{r,i}P_{r,i}-\sum_i Q_{b,i}P_{b,i},$$
>
> où $s_{b,i}=Q_{b,i}/Q_b$ est la part du produit $i$ dans les quantités budgétées. La somme des deux premiers termes vaut $\sum_i Q_{r,i}P_{b,i}-\sum_i Q_{b,i}P_{b,i}$ (parce que $\sum_i s_{b,i}P_{b,i}=P_b^{\text{moy}}$) ; en ajoutant le troisième, on obtient bien l'écart de chiffre d'affaires. L'identité est **exacte** : c'est ce qui la rend utile.

### 7.2.3 Appliquer à l'écart de chiffre d'affaires

Que sont les « produits » de la décomposition ? Les **lignes** du budget : ici, une ligne est un couple *catégorie × canal*. On applique la fonction au budget de 2025.

```python
ca = O.pvm_ca(bud, ["categorie", "canal"])
print({k: round(v) for k, v in ca.items()})
print("quantités : budget", int(bud["quantite_budget"].sum()), "| réalisé", int(bud["quantite_reel"].sum()), "| écart", round((bud["quantite_reel"].sum() / bud["quantite_budget"].sum() - 1) * 100, 1), "%")
```
<!--sortie-->
```text
{'volume': 40344, 'mix': 1180, 'prix': 4540, 'total': 46064, 'ecart': 46064}
quantités : budget 34706 | réalisé 35801 | écart 3.2 %
```

**Lecture.** Sur 46 064 € d'écart de chiffre d'affaires, le **volume** pèse 40 344 € (environ 88 %), le **prix** 4 540 € (10 %) et le **mix** 1 180 € (3 % : les arrondis font dépasser 100 %). La boutique a vendu 3,2 % d'unités de plus que prévu ; le reste est modeste.

La quasi-totalité de l'écart de chiffre d'affaires est un **effet volume** : on a vendu plus d'unités que prévu, et à peu près au prix attendu. L'effet prix est modeste, l'effet mix presque négligeable.

On peut aussi décomposer **canal par canal** : on remplace « catégorie × canal » par « catégorie » à l'intérieur de chaque canal. La décomposition globale cache alors des histoires très différentes.

```python
par_canal_pvm = {canal: O.pvm_ca(d, ["categorie"]) for canal, d in bud.groupby("canal")}
print(pd.DataFrame(par_canal_pvm).T.round(0).to_string())
```
<!--sortie-->
```text
           volume     mix    prix    total    ecart
Boutique -41306.0  1845.0   649.0 -38813.0 -38813.0
Réseaux    5162.0   966.0  1486.0   7614.0   7614.0
Site      76454.0 -1596.0  2405.0  77263.0  77263.0
```

**Lecture.** La Boutique perd 38 813 €, dont **41 306 €** d'effet volume (le prix et le mix la compensent de 2 494 €) ; le Site gagne 77 263 €, dont **76 454 €** d'effet volume. Dans les deux canaux, l'écart est presque entièrement une affaire de **nombre d'unités**, pas de prix : les canaux ne diffèrent pas par le tarif mais par la quantité vendue.

### 7.2.4 Appliquer à l'écart de marge

La marge se décompose de la même façon, en remplaçant le prix par la **marge unitaire** : volume (plus d'unités au même profit par unité), mix (une combinaison plus ou moins profitable) et marge unitaire (chaque unité rapporte plus ou moins).

```python
mg = O.pvm_marge(bud, ["categorie", "canal"])
print({k: round(v) for k, v in mg.items()})
```
<!--sortie-->
```text
{'volume': 12177, 'mix': -173, 'marge_unitaire': 21058, 'total': 33062, 'ecart': 33062}
```

L'effet « marge unitaire » est le plus gros : l'unité vendue rapporte plus que prévu. Mais il mélange deux choses distinctes : un **prix** plus élevé (qui augmente la marge hors taxe à proportion de $1/(1+\text{TVA})$) et un **coût d'achat** plus bas. Séparons-les, en rappelant qu'on compte la marge hors taxe : $\text{marge unitaire}=P/(1+\text{TVA})-c$ avec $c$ le coût d'achat par unité.

```python
prix_marge = ca["prix"] / (1 + TVA)                  # l'effet prix, ramené hors taxe : il passe en entier dans la marge
cout_marge = mg["marge_unitaire"] - prix_marge       # le reste : coût d'achat plus bas que prévu
q_reel = bud["quantite_reel"].sum()
print("effet prix sur la marge :", round(prix_marge), "| effet coût :", round(cout_marge), "| par unité vendue :", round(cout_marge / q_reel, 2), "€")
```
<!--sortie-->
```text
effet prix sur la marge : 3783 | effet coût : 17275 | par unité vendue : 0.48 €
```

**Lecture.** Sur 33 062 € d'écart de marge, le volume apporte 12 177 €, le mix retire 173 € et la marge unitaire apporte 21 058 €. Cette dernière se découpe en 3 783 € venus du **prix** (hors taxe) et 17 275 € venus d'un **coût d'achat** plus bas que prévu, soit 0,48 € par unité vendue. Les deux tiers du dépassement de marge ne viennent donc pas du chiffre d'affaires supplémentaire.

### 7.2.5 La cascade

Un tableau d'effets se lit mieux en **cascade** (*waterfall*) : on part du budget, on ajoute chaque effet, on arrive au réalisé.

```python hide
O.cascade("ch07-cascade-ca.png", [("Budget", bud["ca_budget"].sum()), ("Volume", ca["volume"]), ("Mix", ca["mix"]), ("Prix", ca["prix"]), ("Réalisé", 0)], "Chiffre d'affaires 2025 : du budget au réalisé", ylabel="k€")
O.cascade("ch07-cascade-marge.png", [("Budget", bud["marge_budget"].sum()), ("Volume", mg["volume"]), ("Mix", mg["mix"]), ("Prix", prix_marge), ("Coût d'achat", cout_marge), ("Réalisé", 0)], "Marge brute 2025 : du budget au réalisé", ylabel="k€")
```
<!--sortie-->
```text
figure : ch07-cascade-ca.png
figure : ch07-cascade-marge.png
```

![Cascade du chiffre d'affaires : le budget, les effets volume, mix et prix, puis le réalisé. Les barres vertes augmentent, les rouges diminuent.](figures/ch07-cascade-ca.png)

![Cascade de la marge brute : volume, mix, prix et coût d'achat.](figures/ch07-cascade-marge.png)

### 7.2.6 Les conventions : ce qui change, ce qui ne change pas

La décomposition n'est pas unique. Il y a plusieurs façons **valides** de répartir l'écart, selon l'**ordre** dans lequel on fait entrer les effets : valoriser le volume au prix du budget ou au prix réalisé, l'écart de prix sur les quantités du budget ou du réalisé. Chaque convention donne une somme exacte, mais des parts différentes. Deux exemples sur nos données.

```python
g = bud.groupby(["categorie", "canal"])[["quantite_budget", "quantite_reel", "ca_budget", "ca_reel"]].sum()
Pb, Pr = g["ca_budget"] / g["quantite_budget"], g["ca_reel"] / g["quantite_reel"]
prix_qr = (g["quantite_reel"] * (Pr - Pb)).sum()           # convention du chapitre : prix valorisé sur les quantités réalisées
prix_qb = (g["quantite_budget"] * (Pr - Pb)).sum()         # variante : sur les quantités du budget
print("effet prix : quantités réalisées", round(prix_qr), "| quantités budgétées", round(prix_qb), "| différence", round(prix_qr - prix_qb))
```
<!--sortie-->
```text
effet prix : quantités réalisées 4540 | quantités budgétées 4049 | différence 491
```

La différence (le terme croisé « variation de prix × variation de quantité ») représente environ 11 % de l'effet prix et 1 % de l'écart total : modeste ici, parce que les quantités ont peu varié par ligne, mais elle ne serait pas négligeable dans un budget très éloigné du réalisé. Retenez la règle pratique : **choisissez une convention, écrivez-la, et gardez-la d'une période à l'autre**. Comparer deux décompositions faites avec des conventions différentes est une source classique de disputes sans objet.

Le **niveau de détail** compte davantage. Le mix est, par construction, la partie de l'écart qui dépend de la finesse du découpage : plus les lignes sont fines, plus on met de variations sur le compte du mix et du prix.

```python
for cle in (["canal"], ["categorie"], ["categorie", "canal"], ["categorie", "canal", "mois"]):
    r = O.pvm_ca(bud, cle)
    print(f"{' x '.join(cle):28s} volume {r['volume']:9.0f} | mix {r['mix']:8.0f} | prix {r['prix']:8.0f} | total {r['total']:9.0f}")
```
<!--sortie-->
```text
canal                        volume     40344 | mix      -34 | prix     5753 | total     46064
categorie                    volume     40344 | mix     1099 | prix     4621 | total     46064
categorie x canal            volume     40344 | mix     1180 | prix     4540 | total     46064
categorie x canal x mois     volume     40344 | mix     -190 | prix     5910 | total     46064
```

**Lecture.** Le total ne change jamais (46 064 €) ni l'effet volume (40 344 €). Le mix passe de −34 € (par canal) à +1 099 € (par catégorie), +1 180 € (par catégorie et canal) puis −190 € (au grain mensuel) : sa **valeur dépend de la finesse** du découpage, et son signe peut même changer.

> ⚠️ **Piège.** Une décomposition prix-volume-mix n'est **pas une cause**. L'effet « prix » dit que le prix moyen a varié, pas **pourquoi** (hausse de tarif, moins de promotions, mix à l'intérieur de la ligne). Un effet « mix » grand à un grain et petit à un autre vous avertit qu'il faut regarder la ligne la plus fine avant de conclure.

> ✅ **À retenir.** Volume (plus ou moins d'unités, au prix moyen du budget), mix (une autre combinaison, aux prix du budget) et prix (écart de prix sur les quantités réalisées) **somment à l'écart total**. La convention et le niveau de détail changent la répartition, pas le total. La décomposition **localise** l'écart ; elle ne l'**explique** pas.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.2 à 7.4 et exercices 7.4 à 7.7.
