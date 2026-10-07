# Chapitre 9 : ➕ Analyse financière — exercices et applications

> 🧭 Ce chapitre du cahier prolonge le chapitre 9 du livre (complémentaire). Les **applications** sont de petites études guidées sur les comptes simulés de la boutique (compte de résultat mensuel, bilan annuel) ; vous les refaites pas à pas, puis vous prolongez dans les rubriques « À vous ». Les **exercices** (⭐ facile, ⭐⭐ moyen, ⭐⭐⭐ plus long) renvoient chacun à une section du livre ; leurs **corrigés** sont à la fin. Les comptes sont **simulés et simplifiés** (TVA fictive de 20 %, résultat net approché à 70 % du résultat d'exploitation, bilan équilibré par construction) : rien ici n'est un avis comptable ou fiscal.

Une première cellule charge les bibliothèques et les fichiers ; les autres reprennent les noms ainsi définis.

```python
import os, sys, warnings
import numpy as np, pandas as pd, statsmodels.api as sm
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch09 as O                      # chargement, comptes annuels, ratios, régression des coûts, point mort, rentabilité par canal

pd.options.display.width = 150
pd.options.display.max_columns = 20
cr, bil, cmd, lig, prod, camp, bm = O.charger()
ann = O.annuel(cr)
bi = bil.set_index("annee")
fr = lambda x, nd=0: f"{x:,.{nd}f}".replace(",", " ").replace(".", ",").replace("-", "−")
print(len(cr), "mois de comptes |", len(bil), "bilans |", len(cmd), "commandes |", len(lig), "lignes de commande")
```
<!--sortie-->
```text
36 mois de comptes | 3 bilans | 36395 commandes | 83905 lignes de commande
```

## Applications

### Application 9.1 — Recouper les comptes avec les ventes (section 9.1 du livre)

**Objectif.** S'assurer que le chiffre d'affaires du compte de résultat se retrouve dans la base, puis que le bilan s'équilibre.

**Étape 1 — Reconstituer le chiffre d'affaires hors taxes** à partir des lignes de commande (montants toutes taxes comprises, divisés par 1,2).

```python
ventes = O.ventes_mensuelles(cmd, lig)
ecart = cr.set_index("mois")["ca_ht"] - ventes
print("écart absolu maximal :", round(ecart.abs().max(), 2), "€ | écart moyen :", round(ecart.mean(), 3), "€")
```
<!--sortie-->
```text
écart absolu maximal : 0.49 € | écart moyen : 0.007 €
```

**Étape 2 — Mesurer l'effet d'une mauvaise TVA.** Si l'on divisait par 1,196 au lieu de 1,2, quel écart relatif obtiendrait-on ?

```python
ventes_mauvaise = ventes * 1.2 / 1.196
rel = (ventes_mauvaise / cr.set_index("mois")["ca_ht"] - 1) * 100
print("écart relatif moyen avec une TVA de 19,6 % :", round(rel.mean(), 2), "%")
```
<!--sortie-->
```text
écart relatif moyen avec une TVA de 19,6 % : 0.33 %
```

**Étape 3 — Vérifier l'équilibre du bilan.**

```python
actif = bi[["immobilisations_nettes", "stock", "creances_clients", "tresorerie"]].sum(axis=1)
passif = bi[["capitaux_propres", "emprunt", "dettes_fournisseurs", "autres_dettes"]].sum(axis=1)
print((actif - passif).to_dict())
```
<!--sortie-->
```text
{2023: 0, 2024: 1, 2025: 0}
```

**À vous.** (1) Quel est le mois où l'écart absolu est maximal, et pourquoi n'est-il pas nul ? (2) Faites-vous confiance à un compte de résultat dont le chiffre d'affaires s'écarte de 0,35 % de la base ? Que feriez-vous ? (3) Un écart d'actif moins passif de 1 € est-il une erreur ?

### Application 9.2 — Calculer les ratios à partir des comptes (section 9.2 du livre)

**Objectif.** Refaire les ratios de rentabilité, de cycle d'exploitation et de solidité **sans** la fonction du livre, pour en comprendre chaque dénominateur.

**Étape 1 — Marges.**

```python
marge = pd.DataFrame({"taux_marge_brute": ann["marge_brute"] / ann["ca_ht"], "taux_marge_exploitation": ann["resultat_exploitation"] / ann["ca_ht"]})
print((marge * 100).round(1).T)
```
<!--sortie-->
```text
annee                    2023  2024  2025
taux_marge_brute         36.4  36.4  37.8
taux_marge_exploitation   1.8   1.8   3.6
```

**Étape 2 — Stock, délais et BFR.**

```python
rotation = ann["achats"] / bi["stock"]
delai_clients = bi["creances_clients"] / ann["ca_ht"] * 365
delai_fournisseurs = bi["dettes_fournisseurs"] / ann["achats"] * 365
bfr = bi["stock"] + bi["creances_clients"] - bi["dettes_fournisseurs"]
print(pd.DataFrame({"rotation": rotation, "jours de stock": 365 / rotation, "délai clients": delai_clients, "délai fournisseurs": delai_fournisseurs, "BFR": bfr}).round(1).T)
```
<!--sortie-->
```text
annee                  2023      2024      2025
rotation                4.4       4.3       4.2
jours de stock         83.0      84.6      86.3
délai clients          10.6      10.6      10.6
délai fournisseurs     42.6      42.6      42.6
BFR                 94583.0  101762.0  114186.0
```

**Étape 3 — Rentabilité des capitaux propres et décomposition en trois facteurs** (marge nette × rotation de l'actif × levier financier, dite décomposition de DuPont).

```python
net = 0.7 * ann["resultat_exploitation"]                     # résultat net approché
total_actif = bi[["immobilisations_nettes", "stock", "creances_clients", "tresorerie"]].sum(axis=1)
roe = net / bi["capitaux_propres"]
facteurs = pd.DataFrame({"marge nette": net / ann["ca_ht"], "rotation de l'actif": ann["ca_ht"] / total_actif, "levier": total_actif / bi["capitaux_propres"]})
facteurs["produit"] = facteurs.prod(axis=1)
print(pd.concat([facteurs, roe.rename("ROE")], axis=1).round(3).T)
```
<!--sortie-->
```text
annee                 2023   2024   2025
marge nette          0.013  0.012  0.025
rotation de l'actif  2.502  2.592  2.704
levier               2.344  2.196  2.020
produit              0.073  0.071  0.138
ROE                  0.073  0.071  0.138
```

**À vous.** (1) Entre 2024 et 2025, lequel des trois facteurs explique la hausse de la rentabilité des capitaux propres ? (2) Calculez la liquidité générale en supposant que 30 000 € de l'emprunt sont exigibles à moins d'un an au lieu de 15 000 € : conclut-on autrement ? (3) Pourquoi le délai clients de 10,6 jours est-il identique les trois années, et que dirait-on s'il augmentait ?

### Application 9.3 — Séparer coûts fixes et coûts variables (section 9.3 du livre)

**Objectif.** Estimer, ligne de coût par ligne de coût, la part qui suit le chiffre d'affaires, puis calculer le point mort.

**Étape 1 — Une régression par ligne de coût** (36 mois).

```python
X = sm.add_constant(cr["ca_ht"])
lignes = ["achats", "frais_personnel", "loyers_charges", "marketing", "livraison", "frais_bancaires", "autres_charges"]
res = {c: (sm.OLS(cr[c], X).fit().params["ca_ht"], sm.OLS(cr[c], X).fit().rsquared) for c in lignes}
print(pd.DataFrame(res, index=["pente", "R2"]).T.round(3))
```
<!--sortie-->
```text
                 pente     R2
achats           0.610  0.989
frais_personnel  0.046  0.923
loyers_charges   0.002  0.057
marketing        0.043  0.595
livraison        0.033  0.929
frais_bancaires  0.018  1.000
autres_charges   0.003  0.118
```

**Étape 2 — Le point mort de 2025**, en traitant le marketing comme un coût fixe.

```python
x = ann.loc[2025]
b_pers = sm.OLS(cr["frais_personnel"], X).fit().params["ca_ht"]
cv = (x["achats"] - x["variation_stock"]) + x["livraison"] + x["frais_bancaires"] + b_pers * x["ca_ht"]
cf = x["charges_totales"] - x["livraison"] - x["frais_bancaires"] - b_pers * x["ca_ht"]
pm = O.point_mort(x["ca_ht"], cv, cf)
print("taux de MCV :", round(pm["taux_mcv"] * 100, 1), "% | seuil :", round(pm["seuil"]), "€ | marge de sécurité :", round(pm["marge_securite"] * 100, 1), "% | levier :", round(pm["levier"], 1))
```
<!--sortie-->
```text
taux de MCV : 28.5 % | seuil : 963968 € | marge de sécurité : 12.7 % | levier : 7.9
```

**Étape 3 — Traiter le marketing comme variable** (pente de 0,043 € par euro de chiffre d'affaires) et recalculer le seuil.

```python
b_mkt = sm.OLS(cr["marketing"], X).fit().params["ca_ht"]
cv2, cf2 = cv + b_mkt * x["ca_ht"], cf - b_mkt * x["ca_ht"]
pm2 = O.point_mort(x["ca_ht"], cv2, cf2)
print("seuil si le marketing est variable :", round(pm2["seuil"]), "€ | marge de sécurité :", round(pm2["marge_securite"] * 100, 1), "%")
```
<!--sortie-->
```text
seuil si le marketing est variable : 939403 € | marge de sécurité : 14.9 %
```

**À vous.** (1) De combien le seuil change-t-il entre les deux traitements du marketing, et lequel est le plus prudent pour un budget ? (2) Calculez le seuil en nombre de commandes avec le panier moyen hors taxes de 2025. (3) Pourquoi la pente des loyers n'est-elle pas exactement nulle ?

### Application 9.4 — Rentabilité par canal et clés de répartition (section 9.3 du livre)

**Objectif.** Voir comment le choix d'une clé de répartition change le résultat d'un canal, et pourquoi la contribution est plus fiable.

**Étape 1 — Contribution et résultat par canal** avec les deux clés du livre.

```python
g, tot = O.rentabilite_canal(cmd, lig, prod, cr, camp)
print(g[["ca_ht", "marge_brute", "contribution", "resultat_cle_ca", "resultat_cle_commandes"]].round(0).astype(int))
```
<!--sortie-->
```text
           ca_ht  marge_brute  contribution  resultat_cle_ca  resultat_cle_commandes
canal                                                                               
Boutique  467478       177622        169207            62194                   62975
Réseaux   121729        46392         15683           -12183                  -12154
Site      514763       195003        109595            -8242                   -9052
```

**Étape 2 — Une troisième clé : la marge brute.** Répartissons les coûts communs au prorata de la marge brute.

```python
communes = tot["frais_personnel"] + tot["loyers_charges"] + tot["amortissements"] + tot["autres_charges"]
g["resultat_cle_marge"] = g["contribution"] - g["marge_brute"] / g["marge_brute"].sum() * communes
print(g[["contribution", "resultat_cle_ca", "resultat_cle_commandes", "resultat_cle_marge"]].round(0).astype(int))
```
<!--sortie-->
```text
          contribution  resultat_cle_ca  resultat_cle_commandes  resultat_cle_marge
canal                                                                              
Boutique        169207            62194                   62975               62080
Réseaux          15683           -12183                  -12154              -12297
Site            109595            -8242                   -9052               -8014
```

**Étape 3 — Réconciliation avec le résultat de l'entreprise.**

```python
somme = g["resultat_cle_ca"].sum()
print("somme des résultats par canal :", round(somme), "€ | résultat d'exploitation :", round(ann.loc[2025, 'resultat_exploitation']), "€ | variation de stock :", round(ann.loc[2025, 'variation_stock']), "€ | reste :", round(somme + ann.loc[2025, 'variation_stock'] - ann.loc[2025, 'resultat_exploitation']), "€")
```
<!--sortie-->
```text
somme des résultats par canal : 41769 € | résultat d'exploitation : 39879 € | variation de stock : -1888 € | reste : 2 €
```

**À vous.** (1) La conclusion « le Site perd de l'argent » dépend-elle de la clé ? (2) Si l'on pouvait supprimer 30 % des coûts communs imputés à Réseaux en arrêtant ce canal, faut-il l'arrêter ? (3) Réaffectez le marketing de façon différente (tout au Site) et observez la contribution de Réseaux.

### Application 9.5 — Hausse de prix ou hausse de volume ? (section 9.3 du livre)

**Objectif.** Chiffrer l'effet d'une hausse de prix et d'une hausse de volume, puis chercher la baisse de volume qui annule le gain d'une hausse de prix.

**Étape 1 — Les deux leviers.**

```python
ca = x["ca_ht"]
liees_ca = x["frais_bancaires"] + b_pers * ca            # coûts proportionnels au chiffre d'affaires
prix = 0.01 * (ca - liees_ca)
volume = 0.01 * (ca - cv)
print("+1 % de prix :", round(prix), "€ | +1 % de volume :", round(volume), "€ | rapport :", round(prix / volume, 2))
```
<!--sortie-->
```text
+1 % de prix : 10328 € | +1 % de volume : 3145 € | rapport : 3.28
```

**Étape 2 — Hausse de prix de 3 % : quelle perte de volume la compense ?** Après la hausse de prix de $p$, le chiffre d'affaires est multiplié par $(1+p)$ et le coût des marchandises ne change pas ; une baisse de volume de $q$ retire $q$ de toutes les ventes et de tous les coûts variables.

```python
p = 0.03
gain = p * (ca - liees_ca)
def resultat(p, q):
    ca_ = ca * (1 + p) * (1 - q)
    cv_ = ((x["achats"] - x["variation_stock"]) + x["livraison"]) * (1 - q) + (x["frais_bancaires"] + b_pers * ca) * (1 + p) * (1 - q)
    return ca_ - cv_ - cf
q_zero = next(q for q in np.arange(0, 0.2, 0.0005) if resultat(p, q) <= resultat(0, 0))
print("gain d'une hausse de 3 % de prix à volume constant :", round(gain), "€ | baisse de volume qui l'annule :", round(q_zero * 100, 1), "%")
```
<!--sortie-->
```text
gain d'une hausse de 3 % de prix à volume constant : 30985 € | baisse de volume qui l'annule : 9.0 %
```

**À vous.** (1) Que devient ce seuil si la hausse de prix est de 1 % ? (2) Commentez : « une baisse de 5 % du volume après une hausse de prix de 3 % est-elle acceptable ? » (3) Pourquoi cette analyse est-elle en réalité un premier pas vers l'analyse de sensibilité du chapitre 13 ?

## Exercices

### Exercice 9.1 ⭐ — Une cascade à la main (section 9.1 du livre)

Un commerce a un chiffre d'affaires hors taxes de 240 000 €, des achats de marchandises de 150 000 € et une variation de stock de −5 000 € (le stock a baissé). Ses charges d'exploitation totalisent 70 000 €. Calculez la marge brute, son taux et le résultat d'exploitation.

### Exercice 9.2 ⭐ — Marge ou marque ? (section 9.1 du livre)

Un article acheté 60 € hors taxes est vendu 120 € toutes taxes comprises (TVA de 20 %). Calculez son prix de vente hors taxes, sa marge, son taux de marge (sur le coût d'achat) et son taux de marque (sur le prix de vente).

### Exercice 9.3 ⭐⭐ — Un bilan à équilibrer (section 9.1 du livre)

Un bilan compte : immobilisations nettes 80 000 €, stock 120 000 €, créances clients 30 000 €, capitaux propres 150 000 €, emprunt 50 000 €, dettes fournisseurs 60 000 €, autres dettes 40 000 €. Quelle est la trésorerie qui équilibre le bilan ? Quel est le total du bilan ?

### Exercice 9.4 ⭐ — Rotation et délais à la main (section 9.2 du livre)

Un commerce a un stock de fin d'année de 80 000 €, des achats annuels de 400 000 €, des créances clients de 20 000 € pour un chiffre d'affaires de 480 000 €, et des dettes fournisseurs de 50 000 €. Calculez la rotation du stock, les jours de stock, le délai clients et le délai fournisseurs.

### Exercice 9.5 ⭐⭐ — La croissance consomme de la trésorerie (section 9.2 du livre)

Avec les comptes de 2025, supposez que le chiffre d'affaires augmente de 10 % en 2026 et que le stock, les créances et les dettes fournisseurs augmentent dans la même proportion. De combien le BFR augmente-t-il ? Quelle part du résultat net approché de 2025 cela représente-t-il ?

### Exercice 9.6 ⭐⭐ — Décomposer la rentabilité (section 9.2 du livre)

Un commerce a un chiffre d'affaires de 800 000 €, un résultat net de 24 000 €, un total d'actif de 400 000 € et des capitaux propres de 160 000 €. Calculez sa marge nette, la rotation de son actif, son levier financier et sa rentabilité des capitaux propres ; vérifiez que le produit des trois premiers donne la dernière.

### Exercice 9.7 ⭐ — Un point mort à la main (section 9.3 du livre)

Un commerce a des coûts fixes de 60 000 € par an et un taux de marge sur coûts variables de 30 %. Calculez son seuil de rentabilité. S'il réalise 250 000 € de chiffre d'affaires, quels sont son résultat, sa marge de sécurité et son levier opérationnel ?

### Exercice 9.8 ⭐⭐⭐ — Le coût d'une livraison (section 9.3 du livre)

Les frais de livraison ne concernent que les commandes du Site et des Réseaux. Estimez par régression le coût variable **par commande livrée** à partir des 36 mois de comptes, et comparez-le à la régression sur le chiffre d'affaires. Quelle explication est la plus fidèle ?

### Exercice 9.9 ⭐⭐ — Arrêter ou garder un canal ? (section 9.3 du livre)

Pour le canal Réseaux en 2025, dites ce qui change dans le résultat de l'entreprise si on l'arrête, dans trois hypothèses : (a) aucun coût commun n'est économisé ; (b) 30 % des coûts communs qui lui sont imputés (clé « chiffre d'affaires ») sont réellement économisés ; (c) 60 % le sont. À partir de quelle part d'économie l'arrêt devient-il favorable ?

## Corrigés

### Corrigé 9.1

Marge brute $=240\,000-150\,000+(-5\,000)=85\,000$ € (un stock qui baisse veut dire que l'on a vendu des articles achetés avant : leur coût s'ajoute au coût des achats de l'année). Taux de marge brute $=85\,000/240\,000=35{,}4\ \%$. Résultat d'exploitation $=85\,000-70\,000=15\,000$ €, soit un taux de marge d'exploitation de $6{,}25\ \%$.

### Corrigé 9.2

Prix de vente hors taxes $=120/1{,}2=100$ €. Marge $=100-60=40$ €. Taux de marge (sur le coût) $=40/60=66{,}7\ \%$ ; taux de marque (sur le prix de vente) $=40/100=40\ \%$. Les deux disent la même chose avec des dénominateurs différents : on précise toujours lequel.

### Corrigé 9.3

L'actif hors trésorerie vaut $80\,000+120\,000+30\,000=230\,000$ €, le passif $150\,000+50\,000+60\,000+40\,000=300\,000$ €. La trésorerie qui équilibre est donc $300\,000-230\,000=70\,000$ €, et le total du bilan est de $300\,000$ €.

### Corrigé 9.4

Rotation $=400\,000/80\,000=5$ ; jours de stock $=365/5=73$ ; délai clients $=20\,000/480\,000\times365=15{,}2$ jours ; délai fournisseurs $=50\,000/400\,000\times365=45{,}6$ jours. Le commerce paie ses fournisseurs 45,6 jours après la livraison et vend son stock en 73 jours : il finance donc environ 27 jours de stock avec son propre argent (sans compter le délai clients).

### Corrigé 9.5

Le BFR de 2025 vaut 114 186 € ; si ses trois composantes augmentent de 10 %, il augmente de 10 %, soit 11 419 €, ce qui représente 40,9 % du résultat net approché de 27 915 €. **La croissance coûte du financement** : même une entreprise rentable doit trouver de l'argent pour financer le stock supplémentaire.

```python
bfr25 = bi.loc[2025, "stock"] + bi.loc[2025, "creances_clients"] - bi.loc[2025, "dettes_fournisseurs"]
print(round(bfr25), round(0.10 * bfr25), round(0.10 * bfr25 / (0.7 * ann.loc[2025, "resultat_exploitation"]) * 100, 1))
```
<!--sortie-->
```text
114186 11419 40.9
```

### Corrigé 9.6

Marge nette $=24\,000/800\,000=3{,}0\ \%$ ; rotation de l'actif $=800\,000/400\,000=2{,}0$ ; levier financier $=400\,000/160\,000=2{,}5$ ; rentabilité des capitaux propres $=24\,000/160\,000=15\ \%$. Produit : $0{,}03\times2{,}0\times2{,}5=0{,}15$. On lit que la rentabilité vient de trois sources distinctes : ce que l'on gagne par euro vendu, la vitesse à laquelle l'actif produit des ventes, et la part de dette dans le financement.

### Corrigé 9.7

Seuil $=60\,000/0{,}30=200\,000$ €. Pour 250 000 € de chiffre d'affaires, la marge sur coûts variables est de $0{,}30\times250\,000=75\,000$ €, donc un résultat de $75\,000-60\,000=15\,000$ €. Marge de sécurité $=(250\,000-200\,000)/250\,000=20\ \%$. Levier opérationnel $=75\,000/15\,000=5$ : +1 % de chiffre d'affaires donne +5 % de résultat.

### Corrigé 9.8

On régresse la livraison mensuelle sur le nombre de commandes livrées du mois (Site et Réseaux).

```python
liv = cmd[cmd["canal"] != "Boutique"].assign(mois=lambda d: d["date_commande"].str[:7]).groupby("mois").size().rename("cmd_livrees")
d = cr.set_index("mois").join(liv)
m_cmd = sm.OLS(d["livraison"], sm.add_constant(d["cmd_livrees"])).fit()
m_ca = sm.OLS(d["livraison"], sm.add_constant(d["ca_ht"])).fit()
print("coût par commande livrée :", round(m_cmd.params["cmd_livrees"], 2), "€ | R2 :", round(m_cmd.rsquared, 3), "| R2 sur le CA :", round(m_ca.rsquared, 3))
```
<!--sortie-->
```text
coût par commande livrée : 4.2 € | R2 : 1.0 | R2 sur le CA : 0.929
```

Le coût par commande livrée est de 4,20 € avec un $R^2$ de 1,00 (la vérité programmée est de 4,20 € par commande livrée), contre un $R^2$ de 0,93 pour la régression sur le chiffre d'affaires. La livraison suit le **nombre de commandes livrées**, pas le chiffre d'affaires : c'est un coût variable **par commande**, qui pèse plus lourd sur les petits paniers. C'est un bon exemple de ce qu'un *inducteur de coût* mal choisi (le CA) donne une explication moins fidèle que le bon (les commandes livrées).

### Corrigé 9.9

La contribution de Réseaux est de 15 683 € ; la part de coûts communs qui lui est imputée (clé « chiffre d'affaires ») est de 27 866 €. Si l'on arrête le canal : (a) aucun coût commun économisé : le résultat de l'entreprise baisse de 15 683 € ; (b) 30 % économisés (8 360 €) : il baisse de $15\,683-8\,360=7\,323$ € ; (c) 60 % économisés (16 719 €) : il augmente de $16\,719-15\,683=1\,036$ €. L'arrêt devient favorable à partir d'une économie de $15\,683/27\,866=56{,}3\ \%$ des coûts communs imputés : c'est la question à poser aux équipes (« quels coûts disparaissent réellement ? »), pas à la clé de répartition.

```python
g, tot = O.rentabilite_canal(cmd, lig, prod, cr, camp)
contrib, commun = g.loc["Réseaux", "contribution"], g.loc["Réseaux", "communes_prorata_ca"]
print(round(contrib), round(commun), {p: round(p * commun - contrib) for p in (0, 0.3, 0.6)}, round(contrib / commun * 100, 1))
```
<!--sortie-->
```text
15683 27866 {0: -15683, 0.3: -7323, 0.6: 1036} 56.3
```

## Pistes des applications

**Application 9.1.** (1) Le mois d'écart maximal est octobre 2024, avec 0,49 € : les comptes sont arrondis à l'euro, et les ventes de la base sont divisées par 1,2 sans arrondi. (2) Avec une TVA de 19,6 % au lieu de 20 %, l'écart relatif moyen est de 0,33 % : c'est un écart **systématique**, de même signe tous les mois, qui révèle un mauvais taux. Un écart de cet ordre se cherche (taux de TVA, ventes à taux réduit, canal oublié) avant d'analyser. (3) Un euro d'écart d'équilibre vient d'arrondis ; il n'y a pas d'erreur.

**Application 9.2.** (1) Entre 2024 et 2025, la marge nette double (de 1,2 % à 2,5 %), la rotation de l'actif progresse (de 2,59 à 2,70) et le levier baisse (de 2,20 à 2,02) : la hausse de la rentabilité vient de la **marge**, malgré moins d'endettement. (2) Avec 30 000 € d'emprunt exigible à moins d'un an, la liquidité générale tombe de 2,04 à 1,87 : elle reste supérieure à 1, la conclusion est la même. (3) Le délai clients est constant parce que les créances ont été fabriquées proportionnelles aux ventes ; s'il augmentait, les clients paieraient plus tard et le besoin en fonds de roulement croîtrait.

**Application 9.3.** (1) Le seuil passe de 963 968 € à 939 403 € (−2,5 %) quand le marketing est traité comme variable ; traiter le marketing comme fixe est plus **prudent** pour un budget (seuil plus haut, marge de sécurité de 12,7 % au lieu de 14,9 %). (2) 963 968 / 85,27 ≈ 11 304 commandes. (3) Les loyers ont augmenté par paliers en 2025, en même temps que les ventes : la pente (0,002 €) est un artefact, avec un $R^2$ de 0,06.

**Application 9.4.** (1) Non : le Site est en perte avec les trois clés (−8 242 €, −9 052 € et −8 014 €). (2) Il faut que l'économie dépasse 56,3 % des coûts communs imputés (exercice 9.9) : 30 % ne suffisent pas. (3) Si tout le marketing est affecté au Site, la contribution du Site tombe à 87 066 € et celle de Réseaux monte à 38 212 € : la contribution **dépend de l'affectation directe**, qu'il faut donc justifier.

**Application 9.5.** (1) Pour une hausse de prix de 1 %, la baisse de volume qui annule le gain est de 3,2 % ; pour 3 %, de 9,0 % (une perte de volume égale à trois fois la hausse de prix, environ). (2) Après +3 % de prix et −5 % de volume, le résultat est **encore supérieur de 13 712 €** à celui de départ : la hausse est favorable tant que le volume ne baisse pas de plus de 9 %. (3) Parce qu'on y fait varier **deux paramètres incertains** (prix, volume) et qu'on cherche le seuil de bascule : c'est exactement un calcul de sensibilité.
