# Chapitre 7 : ➕ Analyse des écarts et des causes racines — exercices et applications

> 🧭 Ce chapitre du cahier prolonge le chapitre 7 du livre (chapitre complémentaire). Les **applications** sont de petites études guidées sur le budget et le réalisé de 2025 ; les **exercices** sont numérotés, avec leur niveau (⭐ de base, ⭐⭐ intermédiaire, ⭐⭐⭐ plus délicat) ; les **corrigés** sont à la fin. Tout le code est exécuté : essayez avant de regarder.

Une première cellule charge les bibliothèques et les fichiers ; les autres reprennent les noms ainsi définis.

```python
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch07 as O

D = os.environ["DONNEES"]
lire = lambda nom, **kw: pd.read_csv(os.path.join(D, nom), **kw)
bud = lire("budget_reel_2025.csv")
cmd, lig, prod = lire("commandes.csv", parse_dates=["date_commande"]), lire("lignes_commande.csv"), lire("produits.csv")
jours = lire("jours_exploitation.csv", parse_dates=["date"])
cmd["annee"] = cmd["date_commande"].dt.year
TVA = 0.20
print(len(bud), "lignes de budget |", len(cmd), "commandes |", len(lig), "lignes de commande")
```
<!--sortie-->
```text
216 lignes de budget | 36395 commandes | 83905 lignes de commande
```

## Applications

### Application 7.1 — Lire un écart et fixer un seuil (section 7.1)

**Objectif.** Construire le tableau d'écarts par catégorie et décider lesquels expliquer.

**Étape 1 — le tableau par catégorie.**

```python
cat = bud.groupby("categorie")[["ca_budget", "ca_reel", "marge_budget", "marge_reelle"]].sum()
cat["écart CA"] = cat["ca_reel"] - cat["ca_budget"]
cat["écart CA %"] = (cat["écart CA"] / cat["ca_budget"] * 100).round(1)
cat["écart marge %"] = ((cat["marge_reelle"] / cat["marge_budget"] - 1) * 100).round(1)
print(cat[["écart CA", "écart CA %", "écart marge %"]].round(1).to_string())
```
<!--sortie-->
```text
            écart CA  écart CA %  écart marge %
categorie                                      
Bien-être     7157.5         6.5           12.1
Cuisine       8267.8         3.7            9.1
Décoration  -10410.1        -3.9           -0.3
Jardin       27469.2         8.4           15.0
Maison       10912.2         3.7            8.0
Papeterie     2667.0         4.9           10.8
```

**Étape 2 — un seuil.** Quelles catégories dépassent 5 % d'écart de chiffre d'affaires ?

```python
print("catégories à plus de 5 % d'écart :", list(cat[cat["écart CA %"].abs() > 5].index))
print("catégorie en retard :", list(cat[cat["écart CA"] < 0].index))
```
<!--sortie-->
```text
catégories à plus de 5 % d'écart : ['Bien-être', 'Jardin']
catégorie en retard : ['Décoration']
```

**À vous.** Refaites le tableau par **canal** et par **mois** (le mois le plus en avance, le plus en retard) et commentez.

### Application 7.2 — La décomposition à la main (section 7.2)

**Objectif.** Refaire le calcul prix-volume-mix sur deux produits, puis le confronter à la fonction.

**Étape 1.** Budget : produit X, 80 unités à 10 € ; produit Y, 20 unités à 40 €. Réalisé : X, 70 unités à 10 € ; Y, 40 unités à 42 €.

```python
x = pd.DataFrame({"p": ["X", "Y"], "quantite_budget": [80, 20], "quantite_reel": [70, 40], "ca_budget": [800, 800], "ca_reel": [700, 1680]})
r = O.pvm_ca(x, ["p"])
print({k: round(v, 2) for k, v in r.items()})
```
<!--sortie-->
```text
{'volume': 160.0, 'mix': 540.0, 'prix': 80.0, 'total': 780.0, 'ecart': 780.0}
```

**Étape 2 — le calcul à la main.** Prix moyen du budget : $1\,600/100=16$ € ; volume : $(110-100)\times16=160$ ; mix : $(70-110\times0{,}8)\times10+(40-110\times0{,}2)\times40=-180+720=540$ ; prix : $40\times2=80$ ; total $160+540+80=780=2\,380-1\,600$.

```python
print("volume", (110 - 100) * 16, "| mix", (70 - 110 * 0.8) * 10 + (40 - 110 * 0.2) * 40, "| prix", 40 * (42 - 40), "| total", (110 - 100) * 16 + (70 - 110 * 0.8) * 10 + (40 - 110 * 0.2) * 40 + 40 * 2)
```
<!--sortie-->
```text
volume 160 | mix 540.0 | prix 80 | total 780.0
```

**À vous.** Que se passe-t-il si l'on inverse l'ordre de calcul (valoriser le volume au prix **réalisé**) ? Le total change-t-il ?

### Application 7.3 — Décomposer la marge par canal (section 7.2)

**Objectif.** Appliquer la décomposition de la marge à chaque canal et comparer.

```python
rows = {canal: O.pvm_marge(d, ["categorie"]) for canal, d in bud.groupby("canal")}
print(pd.DataFrame(rows).T.round(0).to_string())
```
<!--sortie-->
```text
           volume    mix  marge_unitaire    total    ecart
Boutique -12514.0  494.0          7936.0  -4084.0  -4084.0
Réseaux    1547.0  232.0          3127.0   4906.0   4906.0
Site      23025.0 -780.0          9995.0  32239.0  32239.0
```

**Étape 2.** La somme des trois effets de chaque canal est-elle égale à son écart de marge ?

```python
t = pd.DataFrame(rows).T
print("somme des effets = écart, pour chaque canal :", bool(np.allclose(t["volume"] + t["mix"] + t["marge_unitaire"], t["ecart"])))
```
<!--sortie-->
```text
somme des effets = écart, pour chaque canal : True
```

**À vous.** Quel canal doit le plus de sa marge au volume ? À la marge unitaire ?

### Application 7.4 — Le prix et le coût derrière la marge unitaire (section 7.2)

**Objectif.** Séparer, pour chaque canal, l'effet prix et l'effet coût dans l'effet « marge unitaire ».

```python
res = {}
for canal, d in bud.groupby("canal"):
    ca, mg = O.pvm_ca(d, ["categorie"]), O.pvm_marge(d, ["categorie"])
    prix = ca["prix"] / (1 + TVA)
    res[canal] = {"marge unitaire": mg["marge_unitaire"], "dont prix (HT)": prix, "dont coût": mg["marge_unitaire"] - prix}
print(pd.DataFrame(res).T.round(0).to_string())
```
<!--sortie-->
```text
          marge unitaire  dont prix (HT)  dont coût
Boutique          7936.0           541.0     7396.0
Réseaux           3127.0          1238.0     1888.0
Site              9995.0          2004.0     7991.0
```

**À vous.** Dans quel canal l'effet « coût » est-il le plus élevé en proportion des unités vendues ?

### Application 7.5 — Tester une hypothèse (section 7.3)

**Objectif.** Tester « le Site a pris des clients à la Boutique » par une autre méthode que la part des commandes : comparer le **nombre moyen de commandes en Boutique par client** en 2024 et en 2025, pour les clients actifs les deux années.

```python
x = cmd[cmd["annee"].isin([2024, 2025])]
deux = x.groupby("id_client")["annee"].nunique()
ids = deux[deux == 2].index
nb = x[x["id_client"].isin(ids) & (x["canal"] == "Boutique")].groupby(["id_client", "annee"]).size().unstack(fill_value=0).reindex(ids, fill_value=0)
print("commandes en Boutique par client : 2024", round(nb[2024].mean(), 2), "| 2025", round(nb[2025].mean(), 2), "| clients :", len(ids))
```
<!--sortie-->
```text
commandes en Boutique par client : 2024 1.81 | 2025 1.62 | clients : 2828
```

**Étape 2 — un test.** Les moyennes diffèrent-elles de façon convaincante ? On calcule un intervalle par rééchantillonnage.

```python
diff = nb[2025] - nb[2024]
graines = np.random.default_rng(1).integers(0, 10**6, 400)
boot = np.array([diff.sample(len(diff), replace=True, random_state=int(s)).mean() for s in graines])
print("variation moyenne :", round(diff.mean(), 3), "| IC à 95 % :", np.round(np.percentile(boot, [2.5, 97.5]), 3))
```
<!--sortie-->
```text
variation moyenne : -0.191 | IC à 95 % : [-0.256 -0.127]
```

**À vous.** Quelle conclusion honnête en tirez-vous (rejetée, probable, établie, non démontrée) ? Que faudrait-il de plus pour établir une cause ?

### Application 7.6 — Rédiger le tableau d'hypothèses (section 7.3)

**Objectif.** Rédiger la conclusion d'une analyse d'écart : un tableau d'hypothèses avec leur statut, à partir de résultats calculés.

```python
cout_budget = bud["ca_budget"].sum() / bud["quantite_budget"].sum() / (1 + TVA) - bud["marge_budget"].sum() / bud["quantite_budget"].sum()
lg = lig.merge(cmd[["id_commande", "annee"]], on="id_commande").merge(prod[["id_produit", "cout_achat"]], on="id_produit")
cu = lg.assign(c=lg["quantite"] * lg["cout_achat"]).groupby("annee").agg(c=("c", "sum"), q=("quantite", "sum"))
cu["u"] = cu["c"] / cu["q"]
jours["annee"] = jours["date"].dt.year
pluie = jours[jours["pluie_mm"] > 1].groupby("annee").size()
tab = pd.DataFrame([
    ["La pluie a freiné la Boutique", f"jours de pluie {pluie[2024]} (2024) puis {pluie[2025]} (2025)", "rejetée" if pluie[2025] < pluie[2024] else "à examiner"],
    ["Le budget anticipait un coût d'achat trop élevé", f"supposé {cout_budget:.2f} €, réalisé {cu.loc[2025, 'u']:.2f} €", "établie" if cout_budget > cu.loc[2025, "u"] * 1.02 else "à examiner"],
], columns=["hypothèse", "résultat", "statut"])
print(tab.to_string(index=False))
```
<!--sortie-->
```text
                                      hypothèse                                 résultat  statut
                  La pluie a freiné la Boutique jours de pluie 111 (2024) puis 92 (2025) rejetée
Le budget anticipait un coût d'achat trop élevé         supposé 19.58 €, réalisé 19.13 € établie
```

**À vous.** Ajoutez une ligne pour « la hausse de tarif de janvier » à partir du rapport des prix catalogue d'une année à l'autre.

## Exercices

**Exercice 7.1 ⭐ (section 7.1).** Le budget d'un canal est de 80 000 € et le réalisé de 72 000 €. Calculez l'écart absolu, l'écart relatif, et dites s'il est favorable. Même question pour des **coûts** budgétés à 30 000 € et réalisés à 33 000 €.

**Exercice 7.2 ⭐⭐ (section 7.1).** Trois lignes de budget ont pour écarts +9 000 €, −8 500 € et −400 €. Le total est de +100 €. Qu'en concluez-vous sur la lecture d'un écart total ? Quel indicateur complémentaire proposez-vous (par exemple la somme des écarts absolus) ?

**Exercice 7.3 ⭐⭐ (section 7.1).** Sur nos données, comptez les lignes mensuelles (216) dont l'écart relatif dépasse 15 % et l'écart absolu 1 500 €. Comparez à un seuil de 10 % et 800 € : quelle conclusion tirez-vous du choix du seuil ?

**Exercice 7.4 ⭐ (section 7.2).** Budget : A, 50 unités à 20 € ; B, 50 unités à 40 €. Réalisé : A, 60 unités à 20 € ; B, 40 unités à 40 €. Calculez les trois effets à la main, puis vérifiez avec `O.pvm_ca`. Que révèle le fait que le prix ne bouge pas ?

**Exercice 7.5 ⭐⭐ (section 7.2).** Même budget qu'à l'exercice 7.4, réalisé : A, 50 unités à 22 € ; B, 50 unités à 40 €. Quel est l'effet prix ? Y a-t-il un effet volume ou mix ?

**Exercice 7.6 ⭐⭐ (section 7.2).** Démontrez que la somme volume + mix + prix égale l'écart total pour deux produits (utilisez la formule du livre et la relation $\sum_i s_{b,i}P_{b,i}=P_b^{\text{moy}}$).

**Exercice 7.7 ⭐⭐⭐ (section 7.2).** Décomposez l'écart de chiffre d'affaires de la **catégorie Jardin** seule, avec les canaux comme lignes. Quel effet domine ? Qu'apprend-on en comparant à la décomposition de la catégorie Décoration ?

**Exercice 7.8 ⭐⭐ (section 7.3).** Écrivez une hypothèse réfutable pour chacune des causes suivantes de l'écart de la Boutique : (a) la météo ; (b) les ruptures de stock ; (c) un transfert vers le Site. Pour chacune, indiquez le test et le résultat qui la réfuterait.

**Exercice 7.9 ⭐⭐ (section 7.3).** Menez les « cinq pourquoi » sur l'écart de marge **favorable** de l'entreprise (+8,6 %), en vous appuyant sur les chiffres de la section 7.2.

**Exercice 7.10 ⭐⭐⭐ (section 7.3).** Un collègue affirme : « le Site a fait perdre des ventes à la Boutique parce que la publicité en ligne a augmenté ». Quels sont les risques de raisonnement dans cette phrase ? Quelles données demanderiez-vous pour la tester ?

## Corrigés

**Corrigé 7.1.** Écart absolu $72\,000-80\,000=-8\,000$ €, relatif $-10\ \%$ ; **défavorable** pour un chiffre d'affaires. Coûts : $+3\,000$ € soit $+10\ \%$ ; **défavorable** aussi (des coûts supérieurs au budget) : même signe, mais le sens n'est pas le même que pour un chiffre d'affaires.

```python
print("CA :", 72000 - 80000, round((72000 / 80000 - 1) * 100, 1), "% | coûts :", 33000 - 30000, round((33000 / 30000 - 1) * 100, 1), "%")
```
<!--sortie-->
```text
CA : -8000 -10.0 % | coûts : 3000 10.0 %
```

**Corrigé 7.2.** Le total de +100 € cache deux écarts importants qui se compensent presque. L'indicateur complémentaire : la somme des **écarts absolus** ($9\,000+8\,500+400=17\,900$ €), qui dit l'ampleur des écarts indépendamment du signe. Un écart total proche de zéro n'est pas un bon budget : c'est peut-être deux gros écarts de signes opposés.

```python
e = np.array([9000, -8500, -400])
print("total :", e.sum(), "| somme des écarts absolus :", np.abs(e).sum())
```
<!--sortie-->
```text
total : 100 | somme des écarts absolus : 17900
```

**Corrigé 7.3.**

```python
bud["e"] = bud["ca_reel"] - bud["ca_budget"]
bud["p"] = bud["e"] / bud["ca_budget"] * 100
for pc, eu in ((15, 1500), (10, 800)):
    print(f"plus de {pc} % et {eu} € :", int(((bud['p'].abs() > pc) & (bud['e'].abs() > eu)).sum()), "lignes sur", len(bud))
```
<!--sortie-->
```text
plus de 15 % et 1500 € : 34 lignes sur 216
plus de 10 % et 800 € : 79 lignes sur 216
```

Le nombre de lignes à expliquer **plus que double** quand on baisse les seuils : le seuil est un choix qui détermine la charge de travail, et il doit être écrit et justifié (et plutôt appliqué à un grain agrégé, où le bruit est moindre).

**Corrigé 7.4.** Prix moyen du budget : 30 €. Volume : $(100-100)\times30=0$. Mix : $(60-50)\times20+(40-50)\times40=200-400=-200$. Prix : 0. Total $-200$ ; vérification : réalisé $1\,200+1\,600=2\,800$ contre budget $1\,000+2\,000=3\,000$, soit $-200$. Le prix ne bouge pas, donc **tout** l'écart est un effet de mix : on a vendu plus du produit bon marché.

```python
ex = pd.DataFrame({"p": ["A", "B"], "quantite_budget": [50, 50], "quantite_reel": [60, 40], "ca_budget": [1000, 2000], "ca_reel": [1200, 1600]})
print({k: round(v, 1) for k, v in O.pvm_ca(ex, ["p"]).items()})
```
<!--sortie-->
```text
{'volume': 0.0, 'mix': -200.0, 'prix': 0.0, 'total': -200.0, 'ecart': -200.0}
```

**Corrigé 7.5.** Seul le prix de A change ($+2$ € sur 50 unités) : effet prix $=50\times2=+100$ €. Les quantités sont inchangées : pas d'effet volume ni mix.

```python
ex2 = pd.DataFrame({"p": ["A", "B"], "quantite_budget": [50, 50], "quantite_reel": [50, 50], "ca_budget": [1000, 2000], "ca_reel": [1100, 2000]})
print({k: round(v, 1) for k, v in O.pvm_ca(ex2, ["p"]).items()})
```
<!--sortie-->
```text
{'volume': 0.0, 'mix': 0.0, 'prix': 100.0, 'total': 100.0, 'ecart': 100.0}
```

**Corrigé 7.6.** Volume + mix $=(Q_r-Q_b)P_b^{\text{moy}}+\sum_i(Q_{r,i}-Q_rs_{b,i})P_{b,i}$. Or $\sum_i Q_rs_{b,i}P_{b,i}=Q_rP_b^{\text{moy}}$, donc le mix vaut $\sum_iQ_{r,i}P_{b,i}-Q_rP_b^{\text{moy}}$ et la somme vaut $\sum_iQ_{r,i}P_{b,i}-Q_bP_b^{\text{moy}}=\sum_iQ_{r,i}P_{b,i}-\sum_iQ_{b,i}P_{b,i}$ (car $Q_bP_b^{\text{moy}}=\sum_iQ_{b,i}P_{b,i}$). En ajoutant le prix $\sum_iQ_{r,i}(P_{r,i}-P_{b,i})$, on obtient $\sum_iQ_{r,i}P_{r,i}-\sum_iQ_{b,i}P_{b,i}$ : l'écart total. $\square$ Vérification numérique sur 1 000 tirages aléatoires :

```python
rng = np.random.default_rng(3)
ok = True
for _ in range(1000):
    d = pd.DataFrame({"p": [0, 1, 2], "quantite_budget": rng.integers(10, 100, 3), "quantite_reel": rng.integers(10, 100, 3)})
    d["ca_budget"] = d["quantite_budget"] * rng.uniform(5, 50, 3); d["ca_reel"] = d["quantite_reel"] * rng.uniform(5, 50, 3)
    r = O.pvm_ca(d, ["p"])
    ok &= abs(r["total"] - r["ecart"]) < 1e-6
print("identité vérifiée sur 1 000 tirages :", bool(ok))
```
<!--sortie-->
```text
identité vérifiée sur 1 000 tirages : True
```

**Corrigé 7.7.**

```python
for c in ("Jardin", "Décoration"):
    r = O.pvm_ca(bud[bud["categorie"] == c], ["canal"])
    print(f"{c:11s}", {k: round(v) for k, v in r.items()})
```
<!--sortie-->
```text
Jardin      {'volume': 23042, 'mix': 217, 'prix': 4211, 'total': 27469, 'ecart': 27469}
Décoration  {'volume': -9576, 'mix': -87, 'prix': -747, 'total': -10410, 'ecart': -10410}
```

Pour le **Jardin**, l'écart est positif et presque entièrement un effet volume ; pour la **Décoration**, il est négatif et l'effet volume est également le plus important, avec un effet de prix très faible. On en tire que l'écart de la Décoration est une affaire de **quantités** (les clients en achètent moins que prévu, surtout en Boutique), pas de prix.

**Corrigé 7.8.** (a) *Météo* : « les jours de pluie ont été plus nombreux en 2025 qu'en 2024 » ; test : comparer le nombre de jours de pluie ; réfutée si 2025 en compte moins (c'est le cas). (b) *Ruptures* : « les jours-produits en rupture sont plus fréquents en 2025 qu'en 2024 » ; test : comparer les taux ; impossible ici faute de données 2024. (c) *Transfert* : « chez les clients actifs les deux années, la part de commandes en Boutique a baissé » ; test : comparer les parts avec un intervalle ; réfutée si l'intervalle contient zéro (ce n'est pas le cas).

**Corrigé 7.9.** (1) Pourquoi la marge dépasse-t-elle le budget de 8,6 % ? Parce que le volume est plus élevé et que la marge par unité est plus forte. (2) Pourquoi la marge par unité est-elle plus forte ? Pour le prix (3 783 € hors taxe) et surtout pour le coût (17 275 €). (3) Pourquoi le coût est-il plus bas ? Parce que le budget supposait +3,1 % et que le coût n'a augmenté que de 0,8 %. (4) Pourquoi cette hypothèse ? On ne sait pas : la règle de construction du budget n'est pas documentée (non démontré). (5) À documenter. Les trois premiers niveaux sont chiffrés, les deux derniers ne le sont pas.

**Corrigé 7.10.** Risques : (1) **post hoc** : la publicité a augmenté *et* la Boutique a reculé, sans lien prouvé ; (2) **cause commune** possible (saison, évolution des habitudes) ; (3) l'affirmation est **causale** alors que les données sont observationnelles ; (4) un seul mécanisme est avancé. Données demandées : les **dépenses publicitaires** par mois comparées à la **part** du Site, le **comportement des mêmes clients** avant et après une campagne, et idéalement une **expérience** (campagne testée sur une région ou une période et pas sur l'autre). Le test serait : la part des commandes passées en Boutique par les clients exposés baisse-t-elle davantage que celle des non exposés ?
