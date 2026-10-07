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

```python hide
assert [round(v * 100, 1) for v in (actuel, seul, c_vers_a)] == [73.5, 80.7, 85.1]
assert (tab["a_l_heure"] * 100).round(1).tolist() == [84.7, 73.6, 47.8] and round(tab.loc["Transporteur A", "décembre"] * 100, 1) == 61.7
```

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

```python hide
O.fig_benchmark(d)
assert pos["position"].tolist() == ["dans la norme", "dans la norme", "dans la norme", "meilleur", "dans la norme", "dans la norme", "moins bon", "moins bon", "moins bon", "meilleur", "à interpréter"]
assert pos.set_index("indicateur").loc["Livraisons à l'heure (%)", "boutique"] == 73.47
```
<!--sortie-->
```text
figure : ch06-benchmark.png
```

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

```python hide
O.fig_bruit()
assert round((abs(ecart) >= 0.5).mean() * 100) == 65 and round((abs(ecart) >= 1).mean() * 100) == 31 and round((abs(ecart) >= 1.5).mean() * 100) == 14
```
<!--sortie-->
```text
figure : ch06-bruit.png
```

**Près de deux semaines sur trois** s'éloignent d'au moins un demi-point de la vraie valeur, **près d'une sur trois** d'au moins un point, et une sur sept de plus d'un point et demi, **sans qu'aucune cause n'existe**. Si la gérante réagit à chaque variation de un point, elle réagira à du bruit une semaine sur trois.

Les données de la boutique le confirment : sur 52 semaines de 2025, l'écart-type du taux de retour hebdomadaire est de 0,97 point, pour 1,04 point attendu du seul hasard d'échantillonnage (rapport 0,93). **Toute la variabilité du taux de retour hebdomadaire est compatible avec du bruit pur** : il n'y a pas de « bonne » ou de « mauvaise » semaine à commenter.

```python hide
x25 = d["x"][d["x"]["annee"] == 2025]
w = O.semaines(x25, "date_commande", "retourne"); w = w[w["size"] >= 300]
pb = w["sum"].sum() / w["size"].sum(); theo = float(np.sqrt(pb * (1 - pb) / w["size"]).mean() * 100)
assert len(w) == 52 and round(w["mean"].std() * 100, 2) == 0.97 and round(theo, 2) == 1.04 and round(w["mean"].std() * 100 / theo, 2) == 0.93
assert round(float(np.sqrt(530 * 0.059 * 0.941)), 1) == 5.4 and round(5.4 / 530 * 100, 1) == 1.0
```

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

```python hide
O.fig_pcharts(d)
assert len(wl) == 48 and round(pbar * 100, 1) == 78.2 and pd.Series(statut).value_counts().to_dict() == {"vert": 44, "rouge": 4}
assert [round(v, 1) for v in z.tail(4)] == [-12.7, -10.7, -13.6, -13.2] and round(wl["mean"].iloc[-4] * 100, 1) == 46.1
```
<!--sortie-->
```text
figure : ch06-cartes-controle.png
```

**Les indicateurs saisonniers.** Une carte de contrôle sur le chiffre d'affaires brut serait inutile : décembre n'est pas « anormal », il est saisonnier. On compare alors **à la même période de l'an dernier** et l'on contrôle la **croissance**. Les douze croissances mensuelles de 2025 ont une moyenne de 11,4 % et un écart-type de 6,5 points ; le seul mois en baisse, **mai (−1,2 %)**, est à 1,9 écart-type de la moyenne : sous la limite d'alerte de deux écarts-types, donc **un mois à surveiller, pas à commenter**.

```python hide
a_ = d["x"].groupby("mois")["montant"].sum(); yy = pd.DataFrame({"m": a_.index.str[5:7], "an": a_.index.str[:4], "v": a_.values}).pivot(index="m", columns="an", values="v")
cr_ = (yy["2025"] / yy["2024"] - 1) * 100
assert (round(cr_.mean(), 1), round(cr_.std(), 1), round(cr_["05"], 1)) == (11.4, 6.5, -1.2) and round((cr_["05"] - cr_.mean()) / cr_.std(), 1) == -1.9
```

Trois précautions pour utiliser ces cartes.

- **Calculer les limites sur un historique « normal »**, pas sur la période que l'on juge : si l'on avait inclus décembre dans la valeur centrale, les limites se seraient élargies et l'alerte aurait disparu.
- **Tenir compte de la saison** pour un indicateur saisonnier : un chiffre d'affaires de décembre ne se juge pas sur la moyenne de l'année, mais sur le décembre précédent (chapitre 5).
- **Ne pas confondre signal et cause** : la carte dit *quand* quelque chose a changé, pas *quoi*. Ici la cause est à chercher dans la logistique de fin d'année (transporteurs, volumes), ce que le chapitre 11 reprend.

### 6.3.6 Le tableau de bord d'une page et le dictionnaire des KPI

Il reste à tout assembler. Un tableau de bord réussi tient en **une page**, ne contient que des indicateurs liés à une décision, affiche pour chacun la **valeur**, la **comparaison** (année précédente ou secteur) et la **tendance**, et colore l'état **selon une règle écrite**. Voici celui de la boutique pour 2025 : les huit indicateurs de pilotage retenus, avec leur tendance mensuelle ; la couleur du cadre est la **position par rapport au secteur** (6.3.2).

![Tableau de bord de la boutique en 2025 : huit indicateurs, chacun avec sa valeur annuelle, sa comparaison (2024 ou secteur) et sa tendance mensuelle. Le cadre est vert quand l'indicateur est meilleur que le secteur, bleu dans la norme, rouge moins bon, gris sans référence.](figures/ch06-tableau-bord.png)

```python hide
O.fig_tableau_bord(d)
```
<!--sortie-->
```text
figure : ch06-tableau-bord.png
```

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

```python hide
assert [round(sh[k]["orange"], 1) for k in sh] == [8.3, 71.1, 3.9, 11.6] and [round(sh[k]["rouge"], 1) for k in sh] == [9.3, 67.5, 3.5, 13.8]
assert [round(sh[k]["p"], 1) for k in sh] == [6.3, 78.2, 4.8, 7.2]
```

Ce dictionnaire est la **mémoire** du tableau de bord : le jour où le chiffre bouge, il évite de se demander ce qu'il mesure, qui s'en occupe, et à partir de quand on s'alarme.

### 6.3.7 La cadence de revue : qui lit quoi, quand

Un tableau de bord n'a de valeur que par le **rituel** qui l'accompagne. Trois rythmes se complètent.

- **Chaque semaine**, 15 minutes : les indicateurs de **pilotage** (livraisons, retours, ruptures, conversion), lus avec leurs couleurs. Une seule question : **quelque chose est-il sorti de sa zone ?** Si oui, une personne est désignée et une date fixée.
- **Chaque mois**, une heure : les indicateurs de **résultat** (chiffre d'affaires, marge, panier moyen) contre l'an dernier et le budget ; on décompose l'écart dans l'arbre (6.2) et l'on décide d'instruire ou non une cause (chapitre 7).
- **Chaque trimestre ou chaque année** : les **cibles** et les **seuils** eux-mêmes. On supprime les indicateurs qui n'ont déclenché aucune décision, on corrige les seuils devenus trop larges ou trop étroits, on réécrit les fiches si une définition a évolué.

Un conseil de méthode : **notez chaque décision prise** à la lecture du tableau de bord. Un indicateur qui n'a jamais déclenché de décision en un an ne mérite pas sa place ; un indicateur qui en a déclenché dix doit être surveillé plus finement.

> ✅ **À retenir.** Une cible a une **base, une ambition, un horizon** ; une référence répond à une question précise (hier, l'an dernier, le budget, le secteur) et a ses limites. Un seuil d'alerte doit être **plus large que le bruit** : on le fixe avec une **carte de contrôle** sur un historique normal. Le tableau de bord d'une page affiche valeur, comparaison, tendance et statut, et il s'appuie sur un **dictionnaire**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.5 et 6.6, exercices 6.9 à 6.12.
