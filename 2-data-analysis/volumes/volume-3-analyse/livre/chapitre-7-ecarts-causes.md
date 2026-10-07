# Chapitre 7 : ➕ Analyse des écarts et des causes racines

> « Un écart n'est pas une réponse : c'est une question que le budget pose à la réalité. »

> 🧭 **Chapitre complémentaire.** Il est facultatif : le reste du volume ne le suppose pas. Il montre comment passer d'un chiffre qui « ne colle pas au budget » à une explication **chiffrée** (décomposer l'écart) puis à une **cause** que l'on peut défendre (tester des hypothèses), ou à l'aveu honnête qu'on ne peut pas conclure.

À la réunion de janvier, la gérante pose le problème : « *Le chiffre d'affaires de 2025 dépasse le budget de 3,6 %, la marge de 8,6 %, et pourtant la Boutique est en dessous du budget sur les deux. Que s'est-il passé ? Et qu'est-ce que je change pour 2026 ?* »

Deux questions en une. La première est **descriptive** : *où* sont les écarts et *de quoi* sont-ils faits ? La seconde est **causale** : *pourquoi* ? Elles n'appellent pas les mêmes méthodes, et la confusion des deux est l'erreur classique : on explique un écart par la première histoire plausible, sans l'avoir vérifiée.

## Le chemin de ce chapitre

- **7.1 Budget contre réalisé** : lire un écart (absolu, relatif, favorable ou défavorable), construire le tableau d'écarts, décider quels écarts méritent une explication, et reconnaître les pièges (compensations, budget irréaliste, périodes décalées).
- **7.2 Décomposer un écart (prix, volume, mix)** : séparer l'écart de chiffre d'affaires, puis de marge, en effets qui **somment exactement** à l'écart total.
- **7.3 Remonter aux causes** : les cinq pourquoi, le diagramme d'Ishikawa, des hypothèses **testables** que l'on teste avec les données, et la façon d'écrire une conclusion honnête.

## Les données du chapitre

Le fichier `budget_reel_2025.csv` donne, pour chaque mois de 2025, chaque catégorie et chaque canal, le budget et le réalisé (chiffre d'affaires, quantités, prix moyen, marge). Le budget a été construit à partir de **l'année 2024 réelle** multipliée par un coefficient de croissance, avec quelques erreurs de plan selon la catégorie : c'est ce que fait la plupart des entreprises. Pour tester des hypothèses, on utilise aussi la base de la boutique (`commandes.csv`, `lignes_commande.csv`, `produits.csv`), les jours d'exploitation (`jours_exploitation.csv`) et le stock des vingt produits les plus vendus (`stock_quotidien.csv`). Toutes les données sont **simulées** ; la vérité programmée est dans la docstring de `build/donnees_a3.py`.


## 7.1 Budget contre réalisé

### 7.1.1 Un écart, trois lectures

Le budget est une **hypothèse chiffrée** sur l'année à venir ; le réalisé est ce qui s'est passé. L'**écart** est leur différence, et on la lit de trois façons.

- **Absolue** : réalisé moins budget, en euros. C'est ce qui pèse sur le résultat.
- **Relative** : l'écart rapporté au budget, en pourcentage. C'est ce qui permet de comparer une grosse ligne et une petite.
- **Favorable ou défavorable** : le **sens** compte autant que le signe. Un chiffre d'affaires supérieur au budget est favorable ; des **coûts** supérieurs au budget sont défavorables. Un tableau d'écarts mélange les deux : il faut annoter chaque ligne.

> ⚠️ **Piège.** Écrire « +3,6 % » sans préciser « du chiffre d'affaires » ni « par rapport au budget » ne dit rien : un écart n'a de sens qu'avec sa **base de comparaison** et sa **mesure**.

Voici l'écart d'ensemble de la boutique, pour le chiffre d'affaires et pour la marge brute.

```python
tot = bud[["ca_budget", "ca_reel", "marge_budget", "marge_reelle"]].sum()
ecart = pd.DataFrame({"budget": [tot["ca_budget"], tot["marge_budget"]], "réalisé": [tot["ca_reel"], tot["marge_reelle"]]}, index=["chiffre d'affaires", "marge brute"])
ecart["écart"] = ecart["réalisé"] - ecart["budget"]
ecart["écart %"] = (ecart["écart"] / ecart["budget"] * 100).round(1)
print(ecart.round({"budget": 0, "réalisé": 0, "écart": 0, "écart %": 1}).to_string())
```
<!--sortie-->
```text
                       budget    réalisé    écart  écart %
chiffre d'affaires  1278700.0  1324764.0  46064.0      3.6
marge brute          385955.0   419017.0  33062.0      8.6
```

**Lecture.** Le chiffre d'affaires dépasse le budget de 46 064 € (+3,6 %) et la marge de 33 062 € (+8,6 %) : la marge progresse **plus vite** que le chiffre d'affaires, ce qui sera à expliquer (7.2 et 7.3).

### 7.1.2 Le tableau d'écarts : où sont-ils ?

Un écart d'ensemble ne dit pas **où** chercher. On le découpe selon les dimensions du budget : ici la catégorie et le canal. Le tableau croisé des écarts relatifs de chiffre d'affaires donne une première carte.

```python
par = bud.groupby(["categorie", "canal"])[["ca_budget", "ca_reel"]].sum()
rel = ((par["ca_reel"] / par["ca_budget"] - 1) * 100).unstack().round(1)
print(rel.to_string())
```
<!--sortie-->
```text
canal       Boutique  Réseaux  Site
categorie                          
Bien-être       -7.6     14.2  20.8
Cuisine         -7.3      3.8  16.0
Décoration     -10.3     -2.5   2.7
Jardin          -3.8     12.4  21.3
Maison          -5.0      5.3  12.7
Papeterie       -6.1     -4.7  19.9
```

**Lecture.** La colonne de la Boutique est négative pour toutes les catégories (de −3,8 % à −10,3 %) ; celle du Site est positive pour toutes (de +2,7 % à +21,3 %). La Décoration est la seule catégorie en retard sur deux canaux (Boutique et Réseaux). Les écarts suivent donc le **canal** bien plus que la catégorie.

On lit la carte en deux temps : d'abord par **ligne** (une catégorie en avance partout ?), puis par **colonne** (un canal en retard partout ?). Une carte où la colonne d'un canal est de la même couleur partout suggère une cause **de canal** ; une ligne homogène, une cause **de produit**. Ici, les écarts par canal sont plus nets que les écarts par catégorie :

```python
par_canal = bud.groupby("canal")[["ca_budget", "ca_reel", "marge_budget", "marge_reelle"]].sum()
par_canal["écart CA"] = par_canal["ca_reel"] - par_canal["ca_budget"]
par_canal["écart CA %"] = (par_canal["écart CA"] / par_canal["ca_budget"] * 100).round(1)
par_canal["écart marge %"] = ((par_canal["marge_reelle"] / par_canal["marge_budget"] - 1) * 100).round(1)
print(par_canal[["écart CA", "écart CA %", "écart marge %"]].round(1).to_string())
```
<!--sortie-->
```text
          écart CA  écart CA %  écart marge %
canal                                        
Boutique  -38812.9        -6.5           -2.2
Réseaux     7613.7         5.5           11.8
Site       77262.9        14.3           19.8
```

**Lecture.** La Boutique est à −38 813 € (−6,5 %) en chiffre d'affaires et à −2,2 % en marge ; le Site à +77 263 € (+14,3 %) et +19,8 % ; les Réseaux à +7 614 € (+5,5 %) et +11,8 %. L'écart total de +46 064 € est la somme d'un **recul** de 38,8 k€ et d'une **avance** de 84,9 k€ : exactement le piège des écarts qui se compensent (7.1.4).

### 7.1.3 La matérialité : tous les écarts ne méritent pas une explication

Sur 216 lignes de budget (douze mois, six catégories, trois canaux), il y aura toujours de gros écarts relatifs dans les deux sens : les lignes sont **petites** (quelques milliers d'euros) et le hasard les bouscule. Expliquer chacun serait épuisant et trompeur : on inventerait une histoire pour du bruit. On fixe donc un **seuil de matérialité** : on n'explique que les écarts à la fois **grands en valeur relative** et **grands en euros**, au **bon niveau de détail**.

```python
bud["ecart_ca"] = bud["ca_reel"] - bud["ca_budget"]
bud["ecart_pct"] = bud["ecart_ca"] / bud["ca_budget"] * 100
fin = bud[(bud["ecart_pct"].abs() > 10) & (bud["ecart_ca"].abs() > 800)]
print("grain mensuel :", len(bud), "lignes ;", len(fin), "dépassent 10 % et 800 €")
cel = bud.groupby(["categorie", "canal"])[["ca_budget", "ca_reel"]].sum()
cel["écart"] = cel["ca_reel"] - cel["ca_budget"]
cel["écart %"] = (cel["écart"] / cel["ca_budget"] * 100).round(1)
mat = cel[(cel["écart %"].abs() > 5) & (cel["écart"].abs() > 3000)].sort_values("écart")
print("grain annuel :", len(cel), "lignes ;", len(mat), "dépassent 5 % et 3 000 € :")
print(mat[["écart", "écart %"]].round(1).to_string())
```
<!--sortie-->
```text
grain mensuel : 216 lignes ; 79 dépassent 10 % et 800 €
grain annuel : 18 lignes ; 9 dépassent 5 % et 3 000 € :
                       écart  écart %
categorie  canal                     
Décoration Boutique -12833.4    -10.3
Cuisine    Boutique  -7730.7     -7.3
Bien-être  Boutique  -4019.1     -7.6
Jardin     Réseaux    4280.3     12.4
Papeterie  Site       4501.3     19.9
Bien-être  Site       9479.2     20.8
Cuisine    Site      15079.7     16.0
Maison     Site      15912.4     12.7
Jardin     Site      29138.6     21.3
```

Le seuil est un **choix**, à écrire et à justifier. Un seuil trop bas noie l'analyste ; un seuil trop haut laisse passer un problème qui s'accumule. Et le **grain** compte : au niveau mensuel, plus du tiers des lignes dépasse 10 % et 800 € sans qu'aucune histoire ne soit à chercher, alors qu'au niveau annuel il reste neuf lignes sur dix-huit, dont le signe est **cohérent par canal** (toutes les lignes retenues de la Boutique sont en retard, toutes celles du Site en avance).

### 7.1.4 Trois pièges de lecture

**Les écarts qui se compensent.** Un écart total proche de zéro peut cacher de gros écarts de signes opposés. Ici, l'écart de chiffre d'affaires de la Boutique et celui du Site vont en sens contraire ; le total (+3,6 %) est la somme d'un recul et d'une avance. Regarder seulement le total conduirait à ne rien voir.

**Un budget irréaliste.** Un écart défavorable peut venir d'un budget **mal fait**, pas d'une mauvaise performance. Ce budget a été construit en augmentant chaque ligne de 2024 d'un coefficient de croissance uniforme, quel que soit le canal. Que faisaient les canaux avant 2025 ? Si le Site monte et la Boutique baisse depuis deux ans, un coefficient identique pour les deux est une hypothèse **fragile**.

```python
cmd_an = cmd.groupby(["annee", "canal"]).size().unstack()
evo = (cmd_an.pct_change() * 100).round(1).loc[[2024, 2025]]
bud_q = bud.groupby("canal")["quantite_budget"].sum()
print("évolution annuelle du nombre de commandes (%) :")
print(evo.to_string())
```
<!--sortie-->
```text
évolution annuelle du nombre de commandes (%) :
canal  Boutique  Réseaux  Site
annee                         
2024       -5.1      5.8  19.7
2025       -3.1      9.6  18.9
```

**Lecture.** Les commandes de la Boutique **reculent** depuis deux ans (−5,1 % en 2024, −3,1 % en 2025), celles du Site progressent de près de 20 % par an. Un budget qui applique à tous les canaux la même croissance parie contre cette tendance : nous le vérifierons en 7.3.

**Les périodes décalées.** Comparer un mois du budget à un mois réalisé suppose que les deux couvrent la même chose : même nombre de jours, de samedis, mêmes fêtes. Les écarts **mensuels** sont bien plus volatils que l'écart **cumulé** depuis janvier : un écart de +11 % en juillet n'est pas un signal, c'est un mois.

```python
mens = bud.groupby("mois")[["ca_budget", "ca_reel"]].sum()
mens["écart %"] = ((mens["ca_reel"] / mens["ca_budget"] - 1) * 100).round(1)
mens["cumul %"] = ((mens["ca_reel"].cumsum() / mens["ca_budget"].cumsum() - 1) * 100).round(1)
print(mens[["écart %", "cumul %"]].T.to_string())
```
<!--sortie-->
```text
mois      1    2    3    4    5    6     7    8    9    10   11   12
écart %  9.6  5.5 -3.5  6.0 -7.9 -3.3  11.0  3.7  4.6  9.9  1.4  7.5
cumul %  9.6  7.7  3.4  4.1  1.1  0.2   1.9  2.1  2.4  3.2  3.0  3.6
```

**Lecture.** L'écart mensuel va de −7,9 % (mai) à +11,0 % (juillet), alors que l'écart **cumulé** se stabilise : il passe de +9,6 % en janvier à +0,2 % en juin, puis remonte vers +3,6 % en décembre. Un mois isolé ne signifie presque rien ; c'est la trajectoire qui renseigne.

> ✅ **À retenir.** Un écart se lit avec sa **mesure**, sa **base** et son **sens** ; on le découpe par dimension pour savoir où chercher ; on **fixe un seuil** pour ne pas expliquer du bruit ; et l'on se méfie de trois choses : les compensations, un budget fragile, et des périodes qui ne se comparent pas.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : application 7.1 et exercices 7.1 à 7.3.


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


## 7.3 Remonter aux causes

### 7.3.1 De « où » à « pourquoi »

La décomposition a localisé l'écart : beaucoup de **volume**, venu du **Site** ; une **marge unitaire** meilleure que prévu ; une **Boutique** en retrait. Elle n'a pas dit pourquoi. Passer de l'un à l'autre est le moment où l'analyste est le plus tenté de **raconter** plutôt que de **démontrer** : une histoire plausible (« c'est la météo », « les clients préfèrent le web ») est toujours disponible, et elle est souvent fausse.

Une méthode simple évite ce travers :

1. **Poser l'écart** avec précision (quoi, où, de combien).
2. **Lister les causes possibles** sans les juger (le diagramme d'Ishikawa, ci-dessous).
3. **Transformer chaque cause en hypothèse testable** : une affirmation qui peut être **fausse**, avec le test et les données qui permettraient de la réfuter.
4. **Tester**, avec les données disponibles, et noter le résultat tel qu'il est.
5. **Conclure avec le bon niveau de certitude**, et proposer des actions proportionnées.

### 7.3.2 Les cinq pourquoi

La technique des **cinq pourquoi** consiste à demander « pourquoi ? » à répétition, jusqu'à une cause sur laquelle on peut **agir** ou que l'on peut **tester**. Pour la Boutique, qui est à −6,5 % du budget de chiffre d'affaires :

| Niveau | Question | Réponse | Preuve |
|---|---|---|---|
| 1 | Pourquoi le chiffre d'affaires de la Boutique est-il sous le budget ? | Moins d'unités vendues que prévu | décomposition : l'effet volume domine |
| 2 | Pourquoi moins d'unités ? | Moins de commandes que prévu | nombre de commandes comparé au budget |
| 3 | Pourquoi moins de commandes ? | Des hypothèses : météo, promotions, ruptures, transfert vers le Site | à tester (7.3.4) |
| 4 | Pourquoi le budget en attendait-il plus ? | Il appliquait la même croissance à tous les canaux | règle de construction du budget, tendance passée |
| 5 | Pourquoi cette règle ? | Elle est simple et ne tient pas compte de la migration vers le Site | à documenter, à corriger |

Les « pourquoi » 1 et 2 se vérifient dans les chiffres. Le troisième ouvre des **hypothèses**, qu'il faut départager. Les deux derniers touchent à la **méthode de budget** : une cause racine fréquente d'un écart est que le budget lui-même reposait sur une hypothèse qui s'est révélée fausse.

> ⚠️ **Piège.** La méthode des cinq pourquoi est un **fil conducteur**, pas une preuve : à chaque marche, c'est vous qui choisissez « la » réponse. La règle est d'accompagner chaque marche d'une **preuve** (un chiffre, un test) ou de signaler qu'elle manque.

### 7.3.3 Le diagramme d'Ishikawa

Le diagramme d'Ishikawa (ou « arête de poisson ») range les causes possibles par **famille** autour d'un effet, pour s'assurer qu'on n'en oublie pas. Il ne démontre rien : c'est un outil d'**exploration**, qui précède les tests.


![Diagramme d'Ishikawa de l'écart « Boutique sous le budget » : six familles de causes possibles.](figures/ch07-ishikawa.png)

### 7.3.4 Des hypothèses que l'on peut tester

Chaque branche du diagramme devient une **affirmation réfutable**. Prenons les plus plausibles et testons-les, avec les données de la boutique.

**H1. « La pluie a freiné la Boutique. »** Si elle l'a fait, 2025 doit compter **plus** de jours de pluie que 2024. **H2. « Il y a eu moins de promotions. »** Alors le nombre de jours de promotion doit avoir baissé.

```python
jours["annee"] = jours["date"].dt.year
jours["pluvieux"] = jours["pluie_mm"] > 1
print(jours.groupby("annee").agg(jours=("date", "size"), jours_pluvieux=("pluvieux", "sum"), jours_promo=("promo_active", "sum"), temperature=("temperature_moy", "mean")).round(1).loc[[2024, 2025]].to_string())
```
<!--sortie-->
```text
       jours  jours_pluvieux  jours_promo  temperature
annee                                                 
2024     366             111           51         12.9
2025     365              92           51         13.1
```

**Lecture.** 2025 compte **92** jours de pluie contre **111** en 2024, soit 19 de moins, et **51** jours de promotion les deux années ; la température moyenne est la même. **H1** et **H2** ne tiennent pas : la pluie aurait même dû aider la Boutique.

**H3. « Des ruptures de stock sur les produits phares ont fait perdre des ventes. »** Nous n'avons le stock quotidien que pour **2025** et pour **vingt produits** : on peut mesurer les ruptures, pas les comparer à l'année précédente.

```python
rupt = stock.groupby(stock["date"].dt.month)["rupture"].mean().mul(100).round(1)
print("jours-produits en rupture par mois (%) :", rupt.to_dict())
print("sur l'année :", round(stock["rupture"].mean() * 100, 1), "% des", len(stock), "jours-produits ; produits touchés :", stock.loc[stock["rupture"] == 1, "id_produit"].nunique(), "sur 20")
```
<!--sortie-->
```text
jours-produits en rupture par mois (%) : {1: 6.0, 2: 3.6, 3: 5.6, 4: 7.3, 5: 2.7, 6: 3.7, 7: 6.3, 8: 2.1, 9: 6.0, 10: 7.6, 11: 12.8, 12: 24.2}
sur l'année : 7.4 % des 7300 jours-produits ; produits touchés : 20 sur 20
```

**Lecture.** 7,4 % des 7 300 jours-produits sont en rupture, et les vingt produits sont touchés au moins une fois ; les ruptures se concentrent en novembre (12,8 %) et en décembre (24,2 %). C'est un vrai problème, mais le test ne peut pas relier ces ruptures à l'écart de la Boutique : il manque 2024 pour comparer et les ventes **perdues** ne sont pas observées. **H3 reste non démontrée.**

**H4. « Les clients de la Boutique sont passés au Site. »** Si c'est vrai, les clients qui achètent **les deux années** doivent avoir déplacé une part de leurs achats de la Boutique vers le Site. On compare, pour chaque client présent en 2024 et en 2025, la part de ses commandes passées en Boutique, avec un intervalle de confiance obtenu par rééchantillonnage des clients.

```python
x = cmd[cmd["annee"].isin([2024, 2025])]
deux = x.groupby("id_client")["annee"].nunique()
ids = deux[deux == 2].index
y = x[x["id_client"].isin(ids)].assign(boutique=lambda d: (d["canal"] == "Boutique").astype(int))
part = y.groupby(["id_client", "annee"])["boutique"].mean().unstack()
diff = part[2025] - part[2024]
graines = np.random.default_rng(0).integers(0, 10**6, 500)
boot = np.array([diff.sample(len(diff), replace=True, random_state=int(s)).mean() for s in graines])
print(len(ids), "clients présents les deux années | part Boutique : 2024", round(part[2024].mean() * 100, 1), "% ; 2025", round(part[2025].mean() * 100, 1), "%")
print("variation :", round(diff.mean() * 100, 1), "points | IC à 95 % :", np.round(np.percentile(boot, [2.5, 97.5]) * 100, 1))
```
<!--sortie-->
```text
2828 clients présents les deux années | part Boutique : 2024 46.8 % ; 2025 42.9 %
variation : -3.9 points | IC à 95 % : [-5.7 -2. ]
```

**Lecture.** Sur 2 828 clients présents les deux années, la part de leurs commandes passée en Boutique tombe de 46,8 % à 42,9 % : −3,9 points, avec un intervalle à 95 % de −5,7 à −2,0, qui **exclut zéro**. **H4** a résisté à un test qui pouvait la réfuter.

**H5. « Le budget supposait une croissance de la Boutique que l'historique ne justifiait pas. »** On compare la croissance **supposée** par le budget à la croissance **observée** avant 2025.

```python
lg = lig.merge(cmd[["id_commande", "annee", "canal"]], on="id_commande").merge(prod[["id_produit", "cout_achat"]], on="id_produit")
qte = lg.groupby(["annee", "canal"])["quantite"].sum().unstack()
hist = ((qte.loc[2024] / qte.loc[2023] - 1) * 100).round(1)
suppose = ((bud.groupby("canal")["quantite_budget"].sum() / qte.loc[2024] - 1) * 100).round(1)
realise = ((qte.loc[2025] / qte.loc[2024] - 1) * 100).round(1)
print(pd.DataFrame({"2024 contre 2023": hist, "supposée par le budget": suppose, "2025 réalisée": realise}).to_string())
```
<!--sortie-->
```text
          2024 contre 2023  supposée par le budget  2025 réalisée
canal                                                            
Boutique              -5.6                     4.1           -3.0
Réseaux                8.1                     4.1            8.0
Site                  19.2                     4.2           18.9
```

**Lecture.** Le budget supposait +4 % de quantités pour **chaque** canal. Or la Boutique avait **perdu** 5,6 % de quantités en 2024 (et en perdra 3,0 % en 2025), alors que le Site en gagnait 19,2 % (et 18,9 % en 2025). **H5** est établie : l'écart de la Boutique est, pour une grande part, une erreur de budget.

**H6. « Le budget anticipait une hausse des coûts d'achat qui n'a pas eu lieu. »** Elle expliquerait l'effet « coût » de la marge. Le coût d'achat unitaire est connu pour 2024 et 2025 ; celui que le budget suppose se déduit du budget lui-même (prix moyen hors taxe moins marge unitaire).

```python
cu = lg.assign(c=lg["quantite"] * lg["cout_achat"]).groupby("annee").agg(c=("c", "sum"), q=("quantite", "sum"))
cu["cout_unitaire"] = cu["c"] / cu["q"]
qb = bud["quantite_budget"].sum()
cout_budget = bud["ca_budget"].sum() / qb / (1 + TVA) - bud["marge_budget"].sum() / qb
print("coût d'achat par unité : 2024", round(cu.loc[2024, "cout_unitaire"], 2), "| supposé par le budget", round(cout_budget, 2), "| réalisé 2025", round(cu.loc[2025, "cout_unitaire"], 2))
print("hausse supposée :", round((cout_budget / cu.loc[2024, "cout_unitaire"] - 1) * 100, 1), "% | hausse réalisée :", round((cu.loc[2025, "cout_unitaire"] / cu.loc[2024, "cout_unitaire"] - 1) * 100, 1), "%")
```
<!--sortie-->
```text
coût d'achat par unité : 2024 18.99 | supposé par le budget 19.58 | réalisé 2025 19.13
hausse supposée : 3.1 % | hausse réalisée : 0.8 %
```

**Lecture.** Le coût d'achat par unité est passé de 18,99 € à 19,13 € (+0,8 %), alors que le budget en supposait 19,58 € (+3,1 %). **H6** est établie : elle explique les 0,48 € par unité de l'effet « coût ».

**H7. « L'effet prix vient d'une hausse de tarif du 1er janvier. »** Si le tarif a changé, le prix catalogue **d'un même produit** doit avoir augmenté d'une année à l'autre, dans tout le catalogue.

```python
tarif = lg.groupby(["id_produit", "annee"])["prix_unitaire"].median().unstack()
rapport = (tarif[2025] / tarif[2024]).dropna()
print("produits vendus les deux années :", len(rapport), "| rapport de prix 2025 / 2024 : médiane", round(rapport.median(), 3), "| min", round(rapport.min(), 3), "| max", round(rapport.max(), 3))
```
<!--sortie-->
```text
produits vendus les deux années : 120 | rapport de prix 2025 / 2024 : médiane 1.03 | min 1.03 | max 1.031
```

**Lecture.** Les 120 produits vendus les deux années ont un prix catalogue multiplié par 1,03 (de 1,030 à 1,031) : la hausse de tarif est **générale**. **H7** est établie ; elle est aussi ce que le budget attendait (de l'ordre de +3 % de prix moyen), d'où un effet prix modeste.

### 7.3.5 Corrélation, cause : ce que ces tests permettent de dire

Aucun de ces tests n'est une **expérience** : on n'a pas tiré au sort les clients qui passent au Site. Chaque test **réfute** ou **soutient** une hypothèse, selon trois niveaux de preuve (que le chapitre 2 a introduits avec la corrélation et la causalité) :

- une hypothèse **réfutée** par les données est écartée proprement (la prédiction ne s'est pas réalisée) ;
- une hypothèse **soutenue** a résisté à un test qui aurait pu la réfuter, mais d'autres explications restent possibles ;
- une hypothèse **non testable avec les données disponibles** reste, honnêtement, **non démontrée**.

Un test qui ne peut pas échouer ne prouve rien. Le test H4 aurait pu montrer que la part de la Boutique n'a **pas** bougé chez les mêmes clients ; il montre le contraire. Il ne prouve pas que le Site « prend » les clients de la Boutique (on n'a pas de groupe témoin), mais il rend l'hypothèse **probable** et écarte l'explication « la clientèle de la Boutique a disparu ».

### 7.3.6 Cinq pièges du raisonnement causal

Même avec de bons tests, cinq erreurs reviennent.

- **Le biais de confirmation.** On cherche des chiffres qui soutiennent l'histoire déjà choisie, et l'on s'arrête dès qu'on en trouve. Le remède est de **formuler d'abord** ce qui réfuterait l'hypothèse, comme on l'a fait pour H1 et H2.
- **Le « après donc à cause de ».** Le Site a progressé **en même temps** que la Boutique reculait : la coïncidence dans le temps ne prouve pas que l'un a causé l'autre. Les deux peuvent avoir une cause commune (un changement d'habitudes, une saison).
- **Les causes multiples.** Un écart a presque toujours **plusieurs** causes, de poids différents. Chercher « la » cause est un piège ; on cherche **les causes principales** et on chiffre leur part quand c'est possible (c'est le rôle de la décomposition).
- **La cause unique rassurante.** « C'est la météo » est confortable parce qu'elle ne demande aucune action. Une cause à laquelle on ne peut rien est suspecte : elle doit passer les mêmes tests que les autres.
- **Les données qui manquent.** L'absence de preuve n'est pas la preuve de l'absence : pour les ruptures de stock, on n'a pas conclu que « ce n'est pas la cause », on a conclu que **le test est impossible** avec les données actuelles.

Quand on **peut** agir, la meilleure preuve de causalité est une **expérience** : un test A/B (chapitre 2) tire au sort les clients ou les magasins, et supprime d'un coup les biais de sélection. Une analyse d'écart a posteriori ne le peut pas : elle **éclaire** une décision, elle ne la **prouve** pas.

### 7.3.7 Écrire la conclusion

La conclusion d'une analyse d'écart se présente en **tableau d'hypothèses**, avec un **statut** pour chacune, afin que le lecteur voie ce qui est établi et ce qui ne l'est pas.

| Hypothèse | Test | Résultat | Statut |
|---|---|---|---|
| H1 pluie | jours de pluie 2025 contre 2024 | moins de jours de pluie en 2025 | **rejetée** (elle aurait joué en sens inverse) |
| H2 promotions | jours de promotion | identiques | **rejetée** |
| H3 ruptures | taux de rupture 2025 | 7,4 % des jours-produits ; pas de comparaison possible | **non démontrée** |
| H4 transfert vers le Site | part Boutique des mêmes clients | −3,9 points, intervalle de −5,7 à −2,0 | **probable** |
| H5 budget irréaliste | croissance supposée contre historique | +4 % supposés, −5,6 % observés l'année d'avant | **établie** (c'est un fait du budget) |
| H6 coût d'achat | hausse supposée contre réalisée | +3,1 % supposés, +0,8 % réalisés | **établie** |
| H7 hausse de tarif | rapport des prix d'un même produit | rapport de 1,03 pour tout le catalogue | **établie** |

On y ajoute **ce qu'on ne sait pas** et **ce qu'il faudrait pour le savoir** : un historique de ruptures sur 2024, la décomposition du transfert (quels clients, quels produits), un groupe témoin si l'on teste une action.

### 7.3.8 Du constat à l'action

Une analyse d'écart qui n'aboutit à aucune décision a été inutile. On propose des **actions proportionnées au niveau de certitude** : une cause établie justifie un changement de méthode ; une cause probable, un test ou un suivi ; une cause non démontrée, une collecte de données.

| Action | Cause visée | Indicateur de suivi | Quand |
|---|---|---|---|
| Budgéter par canal, avec une croissance propre à chacun | H5 | écart de chaque canal au budget | prochain budget |
| Supposer le coût d'achat de l'année précédente, sauf contrat connu | H6 | coût unitaire réalisé contre budget | prochain budget |
| Suivre la part des commandes par canal et par client | H4 | part de la Boutique chez les clients fidèles | tous les mois |
| Historiser les ruptures de stock | H3 | taux de rupture par produit | dès maintenant |

> ✅ **À retenir.** Passer de « où » à « pourquoi » demande des **hypothèses réfutables** et des **tests**, pas des histoires. Une conclusion honnête classe chaque hypothèse (rejetée, probable, établie, non démontrée), dit ce qui manque, et propose des actions **proportionnées** à la certitude. Souvent, la cause racine d'un écart est dans le **budget** lui-même.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.5 et 7.6, exercices 7.8 à 7.10.


## Bilan du chapitre 7

Vous savez maintenant :

- **lire un écart** avec sa mesure, sa base et son sens (favorable ou défavorable), le **découper** par catégorie et par canal, fixer un **seuil de matérialité** et reconnaître les pièges (compensations, budget fragile, périodes décalées) ;
- **décomposer** un écart de chiffre d'affaires ou de marge en effets **volume, mix et prix** (ou coût) qui somment exactement à l'écart total, **vérifier** l'identité, la présenter en **cascade** et connaître l'influence de la convention et du niveau de détail ;
- **remonter aux causes** : poser l'écart, lister les causes (Ishikawa, cinq pourquoi), formuler des **hypothèses réfutables**, les **tester** avec les données, les classer (rejetée, probable, établie, non démontrée), conclure honnêtement et proposer des actions proportionnées.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.1 à 7.6 et exercices 7.1 à 7.10.

Le fil conducteur tient en une phrase : **un écart se localise par le calcul, mais il ne s'explique que par des hypothèses testées**, et la cause racine est parfois le budget lui-même. Le chapitre 8 change de question : plutôt que d'expliquer un écart, il demande **quels éléments comptent vraiment** (analyse de Pareto et ABC) et **comment se situer** par rapport aux autres (benchmarking).
