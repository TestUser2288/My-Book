## 9.2 Rentabilité et ratios

Un chiffre isolé ne dit presque rien : 39 879 € de résultat, est-ce beaucoup ? Les **ratios** rapportent un chiffre à un autre (un résultat au chiffre d'affaires, un stock aux achats) pour obtenir des mesures **comparables** d'une année à l'autre, d'une entreprise à l'autre, d'un canal à l'autre. Cette section en présente quatre familles : les marges, la rentabilité, la gestion du cycle d'exploitation (stock, clients, fournisseurs) et la solidité financière.

### 9.2.1 Les marges : ce que l'on garde sur chaque euro vendu

Le **taux de marge brute** est la marge brute divisée par le chiffre d'affaires hors taxes ; le **taux de marge d'exploitation** est le résultat d'exploitation divisé par ce même chiffre d'affaires. Le premier mesure ce que l'on gagne **sur les marchandises**, le second ce qui reste **après toutes les charges**.

```python hide-code
t = pd.DataFrame({"Taux de marge brute (%)": rat["taux_marge_brute"] * 100, "Taux de marge d'exploitation (%)": rat["taux_marge_exploitation"] * 100,
                  "Part du personnel dans le CA (%)": rat["part_personnel"] * 100}).T
print(tab(t, 1))
```
<!--sortie-->
```text
annee                             2023  2024  2025
Taux de marge brute (%)           36,4  36,4  37,8
Taux de marge d'exploitation (%)   1,8   1,8   3,6
Part du personnel dans le CA (%)  13,6  13,1  12,8
```

Le taux de marge brute est stable de 2023 à 2024 (36,4 %) puis gagne 1,4 point en 2025 (37,8 %). **C'est la bonne nouvelle du compte** : la même cascade, sur 1 104 k€, rapporte environ 15 800 € de plus qu'avec le taux de 2024. D'où vient-il ? Probablement d'une hausse des prix de 3 % au début de 2025 et d'un mélange de ventes légèrement différent ; l'analyse des écarts (chapitre 7) apprend à le démontrer. Le taux de marge d'exploitation double, de 1,8 % à 3,6 % : la marge brute gagne 1,4 point, les charges n'en reprennent qu'une partie.

> 📐 **Pour qui veut la formule.** Le résultat d'exploitation s'écrit $R = \tau\,\text{CA} - C$, où $\tau$ est le taux de marge brute et $C$ l'ensemble des charges. Si le chiffre d'affaires est multiplié par $(1+g)$ et les charges par $(1+h)$ avec $h<g$, le résultat augmente de $\tau g\,\text{CA}-hC$ : on gagne si la **marge brute supplémentaire** dépasse les **charges supplémentaires**. Entre 2024 et 2025 : $0{,}503\times112\,751 = 56\,760$ de marge brute (en prenant la marge sur le seul chiffre d'affaires **supplémentaire**) contre $34\,480$ de charges.

### 9.2.2 La rentabilité : que rapporte l'argent investi ?

La marge dit ce que l'on garde sur les ventes ; la **rentabilité** dit ce que l'on gagne par rapport à **l'argent investi** par les propriétaires. Le ratio le plus courant est la **rentabilité des capitaux propres** (en anglais *return on equity*) : le résultat net divisé par les capitaux propres.

Nos comptes ne donnent pas le résultat net ; nous l'**approchons** par 70 % du résultat d'exploitation (hypothèse simplificatrice). La rentabilité obtenue est de 7,3 % en 2023, 7,1 % en 2024 et 13,8 % en 2025.

```python
print("résultat net approché (€) :", {int(a): fr(v) for a, v in rat["resultat_net_approche"].items()})
print("rentabilité des capitaux propres (%) :", {int(a): fr(v * 100, 1) for a, v in rat["rentabilite_capitaux_propres"].items()})
```
<!--sortie-->
```text
résultat net approché (€) : {2023: '11 867', 2024: '12 319', 2025: '27 915'}
rentabilité des capitaux propres (%) : {2023: '7,3', 2024: '7,1', 2025: '13,8'}
```

La rentabilité des capitaux propres a presque doublé en 2025 : le résultat a plus que doublé, les capitaux propres n'ont augmenté que de 16 %. **Mais** elle dépend aussi du dénominateur : une entreprise peut afficher une belle rentabilité parce que ses capitaux propres sont faibles (elle est très endettée) ; il faut donc la lire avec les ratios d'endettement de la section 9.2.4.

> ⚠️ **Piège : une rentabilité n'est pas une performance.** Un taux de 13,8 % est sans signification tant qu'on ne sait pas **à quoi** on le compare : au taux d'un placement sans risque, à celui du secteur, à celui des années précédentes. Et il repose ici sur un résultat net **approché** : ne citez jamais un taux de ce chapitre comme celui d'une entreprise réelle.

### 9.2.3 Stock, clients, fournisseurs : le cycle d'exploitation

Entre le moment où l'on paie une marchandise et celui où l'on encaisse sa vente, de l'argent est **immobilisé**. Trois mesures l'expriment en jours.

- La **rotation du stock** compare les achats de l'année au stock de fin d'année : 4,4 en 2023, 4,3 en 2024 et 4,2 en 2025, c'est-à-dire que le stock se renouvelle un peu plus de quatre fois par an. En jours, $365/4{,}23\approx86$ jours de stock en 2025, contre 83 en 2023 : **le stock grossit un peu plus vite que les achats**.
- Le **délai de règlement des clients** divise les créances clients par le chiffre d'affaires et multiplie par 365 : 10,6 jours.
- Le **délai de règlement des fournisseurs** divise les dettes fournisseurs par les achats : 42,6 jours.

Ces deux délais sont **identiques** les trois années : ce n'est pas une constante de la nature, c'est une conséquence de la façon dont les comptes ont été fabriqués (créances et dettes proportionnelles aux ventes et aux achats). Dans des comptes réels, une dérive de ces délais serait un signal précieux.

Le **besoin en fonds de roulement** (BFR) résume le cycle : ce que l'on doit **financer** pour que l'activité tourne. Nous le définissons ici comme $\text{stock}+\text{créances clients}-\text{dettes fournisseurs}$.

```python
t = rat[["rotation_stock", "jours_stock", "delai_clients_j", "delai_fournisseurs_j", "bfr", "bfr_jours_ca"]].T
t.index = ["Rotation du stock (par an)", "Jours de stock", "Délai clients (jours)", "Délai fournisseurs (jours)", "BFR (€)", "BFR en jours de CA"]
txt = t.astype(object).apply(lambda r: r.map(lambda v: fr(v, 0 if r.name == "BFR (€)" else 1)), axis=1)
print(txt.to_string())
```
<!--sortie-->
```text
annee                         2023     2024     2025
Rotation du stock (par an)     4,4      4,3      4,2
Jours de stock                83,0     84,6     86,3
Délai clients (jours)         10,6     10,6     10,6
Délai fournisseurs (jours)    42,6     42,6     42,6
BFR (€)                     94 583  101 762  114 186
BFR en jours de CA            36,4     37,5     37,8
```

Le BFR passe de 94 583 € à 114 186 € : l'activité exige **19 603 € de financement de plus** en deux ans, soit plus du tiers du résultat d'exploitation cumulé de 2024 et 2025 (57 478 €). Autrement dit, **une partie du résultat n'est pas de la trésorerie** : elle dort dans le stock. Un résultat positif et une trésorerie qui baisse sont compatibles, et c'est un classique de la croissance.

> 💡 **Intuition.** Le résultat dit si l'on est **rentable** ; la trésorerie dit si l'on est **solvable** ; le BFR fait le lien entre les deux. Une entreprise qui grandit vite a besoin de plus de stock, donc de plus de financement : elle peut manquer d'argent alors qu'elle gagne de l'argent.

### 9.2.4 Liquidité et endettement : l'entreprise est-elle solide ?

La **liquidité** mesure la capacité de payer ses dettes à court terme. On rapporte l'actif qui se transforme en argent dans l'année (stock, créances, trésorerie) aux dettes exigibles dans l'année (fournisseurs, autres dettes, et la part de l'emprunt à rembourser, que nous supposons égale à 15 000 € par an). La **liquidité générale** utilise tout cet actif ; la **liquidité immédiate** seulement la trésorerie.

L'**endettement** compare l'emprunt aux capitaux propres, et l'**autonomie financière** la part des capitaux propres dans l'ensemble des financements.

```python hide-code
t = rat[["liquidite_generale", "liquidite_immediate", "endettement", "autonomie_financiere"]].T
t.index = ["Liquidité générale", "Liquidité immédiate", "Emprunt / capitaux propres", "Autonomie financière"]
print(tab(t, 2))
```
<!--sortie-->
```text
annee                       2023  2024  2025
Liquidité générale          2,00  1,99  2,04
Liquidité immédiate         0,84  0,81  0,84
Emprunt / capitaux propres  0,56  0,43  0,30
Autonomie financière        0,43  0,46  0,50
```

La liquidité générale est stable, autour de 2,0 : l'entreprise dispose de deux euros d'actif à court terme pour chaque euro de dette à court terme. La liquidité immédiate est de 0,84 : la trésorerie seule ne couvre pas **toutes** les dettes exigibles, mais le stock est vendable. Surtout, l'**endettement baisse** (de 0,56 à 0,30) et l'autonomie financière monte (de 0,43 à 0,50) : l'entreprise rembourse son emprunt et conserve ses bénéfices. Elle est de plus en plus solide, et c'est une autre réponse à la gérante : la rentabilité est faible, mais la **structure financière s'améliore**.

> 🧭 **En pratique.** Il n'existe pas de seuil universel : un ratio de liquidité « acceptable » dépend du secteur, de la saison et des habitudes de paiement. On compare une entreprise à **elle-même dans le temps** et à des entreprises **semblables**, jamais à une valeur magique.

### 9.2.5 Analyse horizontale et analyse verticale

Deux façons très simples de lire des comptes méritent des noms.

- L'**analyse horizontale** compare une même ligne **dans le temps** : le chiffre d'affaires croît de 11,4 %, le résultat de 126,6 %, le stock de 10,4 % (de 146 660 € à 161 898 €), le marketing de 22,0 % (de 59 975 € à 73 145 €).
- L'**analyse verticale** exprime chaque ligne **en pourcentage d'une base** (le chiffre d'affaires pour le compte de résultat, le total du bilan pour le bilan) : le personnel pèse 12,8 % du chiffre d'affaires, le stock 39,7 % du total du bilan.

```python
base = ann.loc[[2024, 2025], ["ca_ht", "achats", "frais_personnel", "marketing", "livraison", "resultat_exploitation"]]
print("évolution 2025 / 2024 (%) :", {k: fr(v, 1) for k, v in ((base.loc[2025] / base.loc[2024] - 1) * 100).items()})
print("stock / total du bilan 2025 (%) :", fr(bi.loc[2025, "stock"] / actif[2025] * 100, 1))
```
<!--sortie-->
```text
évolution 2025 / 2024 (%) : {'ca_ht': '11,4', 'achats': '8,3', 'frais_personnel': '8,7', 'marketing': '22,0', 'livraison': '17,0', 'resultat_exploitation': '126,6'}
stock / total du bilan 2025 (%) : 39,7
```

Le tableau d'évolution montre ce que le cahier des charges demande : le **marketing croît deux fois plus vite que le chiffre d'affaires** (+22,0 % contre +11,4 %), la livraison de 17,0 %, le personnel de 8,7 % (moins vite que les ventes), les achats de 8,3 %. Les écarts entre ces taux, rapportés à la taille de chaque poste, expliquent la formation du résultat.

### 9.2.6 Comparer à un secteur, sans surinterpréter

Un secteur fournit des repères : la médiane et les quartiles de chaque indicateur sur un échantillon d'entreprises. Les valeurs du jeu `benchmark_secteur.csv` sont **fictives**, mais le raisonnement est réel.

```python
ref = bm.set_index("indicateur")
ligne = lambda nom, valeur: (nom, fr(valeur, 1), fr(ref.loc[nom, "quartile_1"], 1) + " – " + fr(ref.loc[nom, "quartile_3"], 1))
print(*[ligne("Taux de marge brute (HT)", rat.loc[2025, "taux_marge_brute"] * 100),
        ligne("Rotation du stock (par an)", rat.loc[2025, "rotation_stock"]),
        ligne("Part des frais de personnel dans le CA", rat.loc[2025, "part_personnel"] * 100)], sep="\n")
```
<!--sortie-->
```text
('Taux de marge brute (HT)', '37,8', '33,0 – 42,0')
('Rotation du stock (par an)', '4,2', '3,0 – 5,8')
('Part des frais de personnel dans le CA', '12,8', '19,0 – 29,0')
```

La boutique est **dans la fourchette** du secteur pour la marge brute (37,8 % pour une médiane de 38,0 %) et pour la rotation du stock (4,2 pour une médiane de 4,2) ; sa part de personnel (12,8 %) est **bien en dessous du premier quartile** (19 %). Faut-il s'en réjouir ? Non, pas sans enquête : la boutique emploie peu de monde par rapport à son chiffre d'affaires (c'est une petite structure, et d'autres tâches sont peut-être assurées par la gérante ou par un groupe), ou ses charges de personnel sont mal rapportées. **Un écart au secteur est une question, pas une réponse.**

> ⚠️ **Pièges de la comparaison.** (1) Les définitions varient d'une source à l'autre (rotation calculée sur les achats ou sur le coût des ventes ; marge avant ou après remises). (2) Les entreprises d'un « secteur » sont très hétérogènes (taille, mix de canaux). (3) Un ratio dans la médiane n'est pas bon par nature, et un ratio hors fourchette n'est pas mauvais par nature. (4) Les valeurs du secteur sont ici fictives ; les valeurs réelles datent et se vérifient.

> ✅ **À retenir.** Les ratios rendent les comptes comparables : **marges** (ce qu'on garde sur les ventes), **rentabilité** (ce qu'on gagne sur l'argent investi), **cycle d'exploitation** (stock, délais, BFR) et **solidité** (liquidité, endettement). On les lit **dans le temps** et **avec des repères**, en gardant en tête que chaque ratio a une définition qu'il faut écrire.

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : application 9.2 et exercices 9.4 à 9.6.
