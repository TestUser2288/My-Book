# Projet du volume et auto-évaluation — exercices et applications

> 🧭 Ce chapitre du cahier clôt le volume III. Il contient **le projet du volume** : répondre **de bout en bout** à une vraie question métier, de la question de la gérante à la recommandation chiffrée, en passant par l'exploration, une régression, un contrefactuel, de l'incertitude et une analyse de sensibilité ; puis l'**auto-évaluation** (quarante questions). Il ne demande aucune notion nouvelle : chaque étape s'appuie sur un chapitre du livre.

## Projet du volume

### P.1 La question et le cahier des charges

La gérante vous écrit : « *Nous faisons des promotions trois fois par an (soldes d'hiver, soldes d'été, semaine du « Vendredi noir »). Les ventes montent, et l'on me dit que c'est un succès. Je voudrais savoir si ces promotions nous font vraiment **gagner de l'argent**, et si je dois les reconduire telles quelles l'an prochain.* »

Avant tout calcul, vous **reformulez la question** (livre, introduction et 6.1) : « gagner de l'argent » n'est pas « vendre davantage ». La question testable est :

> **Sur les jours de promotion, la marge brute dégagée est-elle supérieure à celle que l'on aurait dégagée sans promotion ?**

Elle suppose un **contrefactuel** (ce qui se serait passé sans promotion) que l'on ne verra jamais : il faudra l'**estimer**, et dire avec quelle incertitude. La méthode suit huit étapes, chacune appuyée sur un chapitre du livre :

| Étape | Question | Chapitre du livre |
|---|---|---|
| P.2 Explorer | À quoi ressemblent les jours de promotion ? La comparaison brute est-elle équitable ? | 1 |
| P.3 Effet sur les commandes | Combien de commandes la promotion ajoute-t-elle, à saison égale ? | 3, 5 |
| P.4 Effet sur la marge | Le contrefactuel de marge : gagne-t-on ou perd-on ? | 3, 9 |
| P.5 Incertitude | Le résultat tient-il si l'effet est un peu plus fort ou plus faible ? | 2, 13 |
| P.6 Seuil de bascule | À partir de quel effet la promotion devient-elle rentable ? | 13 |
| P.7 Mesurer mieux la prochaine fois | Comment concevoir un test pour trancher ? | 2.5 |
| P.8 La recommandation | Qu'écrit-on à la gérante ? | 6 |

> 📦 **Les données.** `donnees/jours_exploitation.csv` (1 096 jours : commandes, chiffre d'affaires, météo, promotion, dépense publicitaire) et `donnees/commandes.csv`, `lignes_commande.csv`, `produits.csv`. Elles sont **simulées** et leur vérité est programmée (volume I) : la promotion augmente les commandes de **18 %** ; nous comparerons à la fin. Les marges sont **hors taxe** (TVA fictive de 20 %).

### P.2 Étape 1 : explorer

On commence par regarder, sans modèle : combien de jours de promotion, quand, et ce que dit la comparaison brute (livre, 1.1 et 1.2).

```python
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
import warnings; warnings.filterwarnings("ignore")

j = pd.read_csv("donnees/jours_exploitation.csv", parse_dates=["date"])
j["mois"], j["annee"], j["t"] = j["date"].dt.month, j["date"].dt.year, np.arange(len(j)) / 365.25
print("jours de promotion :", int(j["promo_active"].sum()), "sur", len(j), "| mois concernés :", [int(m) for m in sorted(j.loc[j["promo_active"] == 1, "mois"].unique())])
brut = j.groupby("promo_active")[["nb_commandes", "chiffre_affaires"]].mean().round(1)
print(brut)
print("écart brut des commandes :", round((brut.loc[1, "nb_commandes"] / brut.loc[0, "nb_commandes"] - 1) * 100, 1), "% | écart brut du CA :", round((brut.loc[1, "chiffre_affaires"] / brut.loc[0, "chiffre_affaires"] - 1) * 100, 1), "%")
```
<!--sortie-->
```text
jours de promotion : 153 sur 1096 | mois concernés : [1, 6, 7, 11]
              nb_commandes  chiffre_affaires
promo_active                                
0                     32.8            3338.5
1                     35.4            3300.1
écart brut des commandes : 7.9 % | écart brut du CA : -1.2 %
```

**Lecture.** 153 jours de promotion sur 1 096, en janvier, juin-juillet et novembre. La comparaison brute donne 7,9 % de commandes en plus et même **1,2 % de chiffre d'affaires en moins** : un jour de promotion rapporte en moyenne un peu moins qu'un jour ordinaire, ce qui annonce déjà la question de la marge.

La comparaison brute est **trompeuse** : les promotions tombent en janvier et en été, deux **saisons creuses** ; comparer des jours de soldes à des jours « normaux » compare aussi des saisons différentes. Il faut contrôler le mois, le jour de la semaine, la tendance, la pluie et la publicité.

### P.3 Étape 2 : l'effet sur les commandes

Une régression sur le logarithme du nombre de commandes donne l'effet en **pourcentage**, « toutes choses égales par ailleurs » (livre, 3.1 et 3.2). Les jours se suivent : on utilise des **erreurs robustes** à l'autocorrélation (livre, 3.1).

```python
j["pub7"] = j["depense_pub"].rolling(7, min_periods=1).sum() / 1000
j["pluie"] = (j["pluie_mm"] > 1).astype(int)
formule = "np.log(nb_commandes) ~ promo_active + C(mois) + C(jour_semaine) + t + pluie + pub7"
mod = smf.ols(formule, data=j).fit(cov_type="HAC", cov_kwds={"maxlags": 7})
pct = lambda b: (np.exp(b) - 1) * 100
b, ic = mod.params["promo_active"], mod.conf_int().loc["promo_active"]
print("effet de la promotion sur les commandes : %+.1f %% (IC à 95 %% : %+.1f à %+.1f)" % (pct(b), pct(ic[0]), pct(ic[1])))
icp = mod.conf_int().loc["pub7"]
print("effet de 1 000 € de publicité hebdomadaire : %+.2f %% (IC à 95 %% : %+.2f à %+.2f) | R² : %.2f" % (pct(mod.params["pub7"]), pct(icp[0]), pct(icp[1]), mod.rsquared))
naif = smf.ols("np.log(nb_commandes) ~ promo_active", data=j).fit()
print("régression sans contrôle : %+.1f %%" % pct(naif.params["promo_active"]))
```
<!--sortie-->
```text
effet de la promotion sur les commandes : +19.2 % (IC à 95 % : +13.5 à +25.1)
effet de 1 000 € de publicité hebdomadaire : +0.73 % (IC à 95 % : -4.55 à +6.31) | R² : 0.78
régression sans contrôle : +8.7 %
```

**Lecture.** Avec les contrôles, l'effet de la promotion sur les commandes est de **+19,2 %**, avec un intervalle de 13,5 à 25,1 % : plus du double de l'écart brut (7,9 %), parce que les promotions tombent en saison creuse. Sans contrôle, la régression ne trouve que 8,7 %. Pour la publicité, l'estimation (+0,73 % par 1 000 € hebdomadaires) a un intervalle de −4,6 à +6,3 % qui contient à la fois zéro et l'effet programmé (+1,5 %) : les données ne permettent pas de trancher.

### P.4 Étape 3 : le contrefactuel de marge

La **marge brute** d'un jour est la somme, sur ses lignes de commande, du montant hors taxe moins le coût d'achat (livre, 9.1). Pendant la promotion, deux choses se passent : on vend **plus** de commandes (effet positif), mais chaque commande **rapporte moins** (remises).

```python
cmd = pd.read_csv("donnees/commandes.csv"); lig = pd.read_csv("donnees/lignes_commande.csv"); prod = pd.read_csv("donnees/produits.csv")
x = lig.merge(cmd[["id_commande", "date_commande"]], on="id_commande").merge(prod[["id_produit", "cout_achat"]], on="id_produit")
x["marge"] = x["montant"] / 1.2 - x["quantite"] * x["cout_achat"]
marge_j = x.groupby("date_commande")["marge"].sum().rename("marge").reset_index().rename(columns={"date_commande": "date"})
marge_j["date"] = pd.to_datetime(marge_j["date"])
j = j.merge(marge_j, on="date")
pr, npr = j[j["promo_active"] == 1], j[j["promo_active"] == 0]
mo_np, mo_p = npr["marge"].sum() / npr["nb_commandes"].sum(), pr["marge"].sum() / pr["nb_commandes"].sum()
print("marge par commande : hors promotion", round(mo_np, 2), "€ | en promotion", round(mo_p, 2), "€")
```
<!--sortie-->
```text
marge par commande : hors promotion 32.08 € | en promotion 23.62 €
```

**Lecture.** Une commande rapporte en moyenne 32,08 € de marge hors promotion et 23,62 € en promotion : les remises (55,5 % des commandes en promotion portent le code « SOLDES », à −20 %) font perdre un quart de la marge par commande.

Le **contrefactuel** : sans promotion, il y aurait eu $N/(1+e)$ commandes (où $N$ est le nombre réel et $e$ l'effet estimé), chacune rapportant la marge d'une commande ordinaire. L'**incrément de marge** est la marge réelle moins cette marge contrefactuelle.

```python
def increment(e, marge_ordre=mo_np):
    commandes_sans = pr["nb_commandes"].sum() / (1 + e)
    return pr["marge"].sum() - commandes_sans * marge_ordre

e_hat, e_bas, e_haut = np.exp(b) - 1, np.exp(ic[0]) - 1, np.exp(ic[1]) - 1
print("marge réelle des jours de promotion :", round(pr["marge"].sum()), "€")
for nom, e in [("effet estimé", e_hat), ("effet bas de l'IC", e_bas), ("effet haut de l'IC", e_haut)]:
    print(f"{nom:20s} e = {e * 100:5.1f} % | marge sans promotion {pr['nb_commandes'].sum() / (1 + e) * mo_np:8.0f} € | incrément de marge {increment(e):8.0f} €")
```
<!--sortie-->
```text
marge réelle des jours de promotion : 127977 €
effet estimé         e =  19.2 % | marge sans promotion   145861 € | incrément de marge   -17884 €
effet bas de l'IC    e =  13.5 % | marge sans promotion   153101 € | incrément de marge   -25125 €
effet haut de l'IC   e =  25.1 % | marge sans promotion   138963 € | incrément de marge   -10986 €
```

La promotion **vend plus mais gagne moins** : même avec l'extrémité haute de l'intervalle de confiance de l'effet, l'incrément de marge est négatif. On n'a pas encore compté le surcoût publicitaire des jours de promotion.

```python
pub_supp = pr["depense_pub"].sum() - len(pr) * npr["depense_pub"].mean()
print("surcoût publicitaire des jours de promotion :", round(pub_supp), "€ | incrément de marge après publicité :", round(increment(e_hat) - pub_supp), "€")
```
<!--sortie-->
```text
surcoût publicitaire des jours de promotion : 7132 € | incrément de marge après publicité : -25016 €
```

**Lecture.** Le gain de commandes ne compense pas la perte de marge par commande : l'incrément de marge est de **−17 884 €** à l'effet estimé, de −10 986 € à la borne haute de l'intervalle, et de **−25 016 €** une fois la publicité supplémentaire (7 132 €) comptée.

### P.5 Étape 4 : l'incertitude et la sensibilité

L'effet estimé est incertain, et le contrefactuel suppose que la marge par commande « normale » aurait été la même. On simule : l'effet est tiré selon l'incertitude de la régression (loi normale sur le coefficient), et la marge par commande varie de plus ou moins 10 % (livre, 13.1 et 13.2).

```python
rng = np.random.default_rng(42)
se = (ic[1] - ic[0]) / (2 * 1.96)
sims = np.array([increment(np.exp(rng.normal(b, se)) - 1, mo_np * rng.uniform(0.9, 1.1)) for _ in range(5000)])
print("incrément de marge simulé : médiane", round(np.median(sims)), "€ | intervalle à 90 % :", round(np.percentile(sims, 5)), "à", round(np.percentile(sims, 95)), "€")
print("part des simulations où la promotion gagne de l'argent :", round((sims > 0).mean() * 100, 1), "%")
```
<!--sortie-->
```text
incrément de marge simulé : médiane -17864 € | intervalle à 90 % : -32456 à -3416 €
part des simulations où la promotion gagne de l'argent : 1.0 %
```

**Lecture.** L'incrément de marge simulé a pour médiane −17 864 € (90 % des simulations entre −32 456 € et −3 416 €) ; la promotion ne gagne de l'argent que dans 1 % des simulations.

La conclusion est **robuste** aux deux sources d'incertitude que l'on a modélisées : dans presque toutes les simulations, la promotion fait perdre de la marge. Il reste des incertitudes **non modélisées** (voir P.8).

### P.6 Étape 5 : le seuil de bascule

À partir de quel effet sur les commandes la promotion serait-elle neutre en marge ? C'est un **seuil de bascule** (livre, 13.3) : on cherche $e^*$ tel que l'incrément soit nul, c'est-à-dire $1+e^*=N\,m_0/M$, avec $m_0$ la marge d'une commande ordinaire et $M$ la marge réelle des jours de promotion.

```python
e_seuil = pr["nb_commandes"].sum() * mo_np / pr["marge"].sum() - 1
print("effet nécessaire pour ne pas perdre de marge : %+.1f %% de commandes (effet estimé : %+.1f %%)" % (e_seuil * 100, e_hat * 100))
```
<!--sortie-->
```text
effet nécessaire pour ne pas perdre de marge : +35.8 % de commandes (effet estimé : +19.2 %)
```

**Lecture.** Il faudrait **+35,8 %** de commandes pour ne pas perdre de marge, contre +19,2 % observés : même la borne haute de l'intervalle (+25,1 %) est loin du seuil.

```python
cp = cmd.merge(j[["date", "promo_active"]].assign(date=lambda d: d["date"].dt.strftime("%Y-%m-%d")), left_on="date_commande", right_on="date")
codes = cp.loc[cp["promo_active"] == 1, "code_promo"].fillna("aucun").replace("", "aucun").value_counts(normalize=True)
print("codes promotionnels des commandes en promotion (%) :", (codes * 100).round(1).to_dict())
```
<!--sortie-->
```text
codes promotionnels des commandes en promotion (%) : {'SOLDES': 55.5, 'aucun': 44.5}
```

### P.7 Étape 6 : mesurer mieux la prochaine fois

On n'a **pas** randomisé la promotion : on a estimé son effet par régression, ce qui suppose que les variables de contrôle suffisent. Pour trancher une prochaine fois, on peut tester une promotion sur **une partie** des jours ou des clients, et la question devient : **combien de jours** faut-il (livre, 2.5) ? On utilise l'écart-type des résidus de la régression comme mesure du bruit.

```python
from statsmodels.stats.power import TTestIndPower
sigma = np.sqrt(mod.scale)
for effet in (0.05, 0.10, 0.20):
    n_jours = TTestIndPower().solve_power(effect_size=np.log(1 + effet) / sigma, alpha=0.05, power=0.8)
    print(f"détecter +{effet * 100:.0f} % de commandes : environ {np.ceil(n_jours):.0f} jours par groupe (écart-type résiduel du log : {sigma:.3f})")
```
<!--sortie-->
```text
détecter +5 % de commandes : environ 212 jours par groupe (écart-type résiduel du log : 0.179)
détecter +10 % de commandes : environ 57 jours par groupe (écart-type résiduel du log : 0.179)
détecter +20 % de commandes : environ 17 jours par groupe (écart-type résiduel du log : 0.179)
```

**Lecture.** Pour détecter +10 % de commandes avec un test sur des jours, il faut environ 57 jours par groupe ; +5 % en exigerait 212. Une expérience sur quelques semaines ne tranche que les effets d'au moins 10 à 20 %.

> ✅ **À retenir.** Quand on ne peut pas expérimenter, on **estime** un contrefactuel ; quand on peut, on **expérimente**. Dans les deux cas, on annonce l'incertitude et le seuil de bascule, pas seulement une moyenne.

### P.8 Étape 7 : la recommandation à la gérante

Le message tient en cinq lignes, chacune avec un chiffre ; on le **produit par le calcul**, pas à la main.

```python
fr = lambda v, nd=0: f"{v:,.{nd}f}".replace(",", " ").replace(".", ",")
print(f"1) Les {len(pr)} jours de promotion ont vu {fr(pct(b), 1)} % de commandes en plus que des jours comparables (intervalle : {fr(pct(ic[0]), 1)} à {fr(pct(ic[1]), 1)} %).")
print(f"2) La marge par commande tombe de {fr(mo_np, 1)} € à {fr(mo_p, 1)} € à cause des remises.")
print(f"3) La marge brute des jours de promotion est inférieure de {fr(-increment(e_hat))} € à ce qu'elle aurait été sans promotion (de {fr(-increment(e_haut))} à {fr(-increment(e_bas))} €).")
print(f"4) Il aurait fallu {fr(e_seuil * 100, 0)} % de commandes en plus pour ne pas perdre de marge.")
print(f"5) Sur {fr(len(sims))} simulations, la promotion gagne de l'argent dans {fr((sims > 0).mean() * 100, 1)} % des cas.")
```
<!--sortie-->
```text
1) Les 153 jours de promotion ont vu 19,2 % de commandes en plus que des jours comparables (intervalle : 13,5 à 25,1 %).
2) La marge par commande tombe de 32,1 € à 23,6 € à cause des remises.
3) La marge brute des jours de promotion est inférieure de 17 884 € à ce qu'elle aurait été sans promotion (de 10 986 à 25 125 €).
4) Il aurait fallu 36 % de commandes en plus pour ne pas perdre de marge.
5) Sur 5 000 simulations, la promotion gagne de l'argent dans 1,0 % des cas.
```

> **Recommandation proposée.** Ne pas reconduire la promotion « telle quelle » : réduire la **profondeur** des remises (la remise de 20 % est le principal levier), la **concentrer** sur les produits à forte marge ou sur les clients à acquérir, et **tester** la prochaine édition sur une partie des jours ou des clients.
>
> **Ce que cette analyse ne dit pas :** la **valeur à long terme** des clients acquis pendant les soldes (ils reviennent peut-être) ; l'effet sur l'**image** ou sur le **déstockage** ; l'effet de la promotion sur les **autres jours** (reports d'achats) ; la marge sur les ventes **perdues** si l'on avait été en rupture.

### P.9 Les limites de l'étude

- **Contrefactuel estimé, non observé.** Le modèle suppose que mois, jour, tendance, pluie et publicité contrôlent bien la saison ; une cause oubliée biaiserait l'effet (livre, 3.1).
- **Marge par commande « ordinaire » supposée constante** : en réalité, le mélange de produits varie selon la saison. La simulation de P.5 en tient compte par ±10 %.
- **Reports d'achats et effets de long terme non mesurés** : une promotion peut décaler des achats (donc surestimer l'effet) ou acquérir des clients durables (donc le sous-estimer).
- **Données simulées.** La vérité (+18 % de commandes) est connue ; en réalité, aucune vérité n'est disponible.

### P.10 La vérité programmée

Après coup seulement, on compare à ce qui a été programmé. L'effet de la promotion sur les commandes est **+18 %** dans le simulateur ; la régression avec contrôles en trouve environ **+19 %**, avec un intervalle qui contient 18 %, alors que la comparaison brute en trouve moins de la moitié. C'est le résultat que l'on attend d'une bonne analyse : on retrouve l'ordre de grandeur, avec son incertitude, **et** on sait pourquoi la comparaison naïve se trompait.

### P.11 Variante : l'objet d'e-mail

La même démarche s'applique au test A/B d'un objet d'e-mail (`donnees/ab_email.csv`) : **mesurer l'écart**, **tester**, **calculer la puissance** (livre, 2.2 et 2.5), puis **décider**.

```python
from statsmodels.stats.proportion import proportions_ztest, proportion_confint
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

ab = pd.read_csv("donnees/ab_email.csv")
t = ab.groupby("groupe")["achat_7j"].agg(["sum", "size"])
p = t["sum"] / t["size"]
stat, pval = proportions_ztest(t["sum"].values, t["size"].values)
print("taux d'achat : A", round(p["A"] * 100, 2), "% | B", round(p["B"] * 100, 2), "% | écart", round((p["B"] - p["A"]) * 100, 2), "points | p-valeur :", round(pval, 3))
pui = NormalIndPower().solve_power(effect_size=proportion_effectsize(0.034, 0.030), nobs1=6000, alpha=0.05)
print("puissance pour détecter un vrai écart de 3,0 % à 3,4 % avec 6 000 par groupe :", round(pui * 100, 1), "%")
n_req = NormalIndPower().solve_power(effect_size=proportion_effectsize(0.034, 0.030), alpha=0.05, power=0.8)
print("destinataires par groupe pour 80 % de puissance :", int(np.ceil(n_req)))
```
<!--sortie-->
```text
taux d'achat : A 2.92 % | B 3.38 % | écart 0.47 points | p-valeur : 0.143
puissance pour détecter un vrai écart de 3,0 % à 3,4 % avec 6 000 par groupe : 23.8 %
destinataires par groupe pour 80 % de puissance : 30362
```

**Lecture.** L'écart observé (0,47 point, p = 0,14) n'est **pas significatif** ; ce n'est pas la preuve qu'il n'y a pas d'effet : avec 6 000 destinataires par groupe, la puissance n'est que de 24 % pour un vrai écart de 0,4 point, et il en faudrait environ 30 000 par groupe pour atteindre 80 %. Décision raisonnable : ne pas conclure, ou refaire le test avec plus de monde.

## Auto-évaluation

**Mode d'emploi.** Répondez à voix haute ou par écrit **avant** de lire le corrigé, en une ou deux phrases. Les sections à relire sont indiquées dans le corrigé. Trente-cinq bonnes réponses sur quarante signalent un volume bien assimilé ; les questions des sections et chapitres facultatifs (➕ 1.4, 2.4, 2.5, 3.3, 4.3, 4.4, 5.3 et chapitres 7 à 13) comptent si vous les avez lus.

### Exploration (chapitre 1)

1. Le panier moyen vaut 100,4 € et la médiane 79,8 € ; 61 % des commandes sont inférieures à la moyenne. Que dit ce couple de chiffres, et lequel annoncez-vous ?
2. En moyenne, un jour de promotion rapporte **moins** de chiffre d'affaires qu'un jour ordinaire, et pourtant, mois par mois, il rapporte **plus**. Comment est-ce possible ?
3. Pourquoi la règle des 1,5 écart interquartile appliquée au chiffre d'affaires quotidien signale-t-elle surtout des jours de novembre et de décembre ? Que faire à la place ?
4. Distinguez une anomalie, une erreur et un événement, avec un exemple pour chacun.

### Tests, A/B et corrélation (chapitre 2)

5. Que mesure une p-valeur, et que ne mesure-t-elle pas ? Donnez deux interprétations fausses courantes.
6. Un test d'e-mail compare 2,92 % d'achats (A) à 3,38 % (B), avec 6 000 destinataires par groupe et une p-valeur de 0,14. Que concluez-vous ? Que faire ensuite ?
7. Une refonte de page est répartie 50/50 mais l'on observe 20 048 sessions en A et 18 574 en B. Est-ce un hasard ? Que faire avant de lire les conversions ?
8. Pourquoi regarder les résultats d'un test A/B tous les jours et s'arrêter dès que p < 0,05 est-il dangereux ?
9. Combien de personnes par groupe faut-il pour détecter, avec 80 % de puissance et un seuil de 5 %, le passage d'un taux de 4,0 % à 4,6 % ?
10. La corrélation entre dépense publicitaire et commandes est de 0,53 sur l'année, et de 0,11 à mois égal. Que s'est-il passé ?

### Régression (chapitre 3)

11. Dans une régression de $\ln(\text{commandes})$ sur une indicatrice de promotion et des contrôles, le coefficient de la promotion vaut 0,176. Que signifie-t-il en pourcentage ?
12. Que veut dire « toutes choses égales par ailleurs » dans l'interprétation d'un coefficient ? Pourquoi la régression simple et la régression multiple donnent-elles des effets différents ?
13. Pourquoi emploie-t-on des erreurs standard robustes sur des données journalières ?
14. Le rapport de cotes d'un retour pour le Site contre la Boutique est de 3,11 ; la probabilité de retour en Boutique est de 3 %. Quelle est la probabilité pour le Site ?
15. Un modèle expliquant les commandes a un R² de 0,78. Peut-on dire qu'il « explique la cause » de 78 % des ventes ? Quelle est la différence entre expliquer et prédire ?

### Segmentation et cohortes (chapitre 4)

16. Pourquoi standardise-t-on les variables avant une segmentation par k-moyennes ?
17. Une segmentation en quatre groupes a une silhouette de 0,28. Que faut-il en penser ?
18. Pourquoi les cohortes les plus récentes semblent-elles « moins fidèles » dans une matrice de rétention ?
19. Un client a commandé il y a 20 jours, 12 fois dans l'année, pour 1 200 € : que dit son score RFM ?
20. Marge annuelle par client actif de 69 €, rétention annuelle de 80 %, taux d'actualisation de 10 % : quelle est la valeur vie client par la formule simple $m\,r/(1+d-r)$ ?

### Séries temporelles (chapitre 5)

21. Un indice saisonnier de janvier vaut 0,82 : que signifie-t-il ?
22. Pourquoi compare-t-on souvent un mois au même mois de l'année précédente plutôt qu'au mois précédent ?
23. Quelle est la prévision de référence à battre pour une série saisonnière, et pourquoi le MAPE est-il un indicateur imparfait ?
24. Les ventes de quatre mois valent 100, 110, 90 et 120. Calculez la moyenne mobile sur trois mois pour le troisième et le quatrième mois.

### KPI (chapitre 6)

25. Quels éléments doit contenir la fiche d'un KPI ?
26. Donnez un exemple de la loi de Goodhart avec un indicateur de la boutique.
27. Le chiffre d'affaires du site se décompose en sessions × conversion × panier : vérifiez-le avec 127 022 sessions, 4,785 % de conversion et 101,63 € de panier.
28. Un taux de livraisons à l'heure oscille autour de 92 % avec un écart-type hebdomadaire de 2 points. Quelles limites de contrôle à ±3 écarts-types ? Une semaine à 87 % est-elle un signal ?

### Chapitres complémentaires (7 à 13)

29. Budget : 100 unités à 10 € ; réalisé : 110 unités à 9,50 €. Décomposez l'écart de chiffre d'affaires en effet volume et effet prix.
30. Que sont les « 5 pourquoi », et pourquoi faut-il tester une cause supposée plutôt que de l'affirmer ?
31. Les 20 % de produits les plus vendus font 51 % du chiffre d'affaires, et non 80 % : que dit-on de la « règle des 80/20 » ? Que mesure une analyse ABC ?
32. Votre coût d'acquisition d'un client est de 98,6 € contre une médiane de secteur de 18 €. Peut-on conclure que vous dépensez cinq fois trop ?
33. Coûts fixes annuels de 400 000 € et taux de marge sur coûts variables de 38 % : quel est le seuil de rentabilité ?
34. Résultat d'exploitation de 39 879 € pour un chiffre d'affaires hors taxe de 1 103 969 € : quelle est la marge d'exploitation, et en quoi diffère-t-elle de la marge brute ?
35. Quel est le seuil de rentabilité d'une dépense publicitaire, exprimé en ROAS (chiffre d'affaires sur dépense), si la marge est de 38 % du chiffre d'affaires hors taxe ?
36. 127 022 sessions, 6 078 commandes : quel est le taux de conversion ? Pourquoi dépend-il de la source de trafic ?
37. Demande moyenne de 12 unités par jour, écart-type journalier de 4, délai de 10 jours, niveau de service visé de 95 % ($z=1{,}65$) : stock de sécurité et point de commande ?
38. Sept départs sur un effectif moyen de 64 : quel est le taux de turnover ? Pourquoi faut-il être prudent avec ce taux ?
39. Qu'apporte un diagramme en tornade ? Quelle est sa limite ?
40. Une simulation de Monte-Carlo donne un résultat médian de 17 834 € et une probabilité de perte de 22,6 %. Comment le présentez-vous, et que ne dit-elle pas ?

## Corrigés des questions

Pour les questions numériques, **calculons** plutôt que de nous fier à la mémoire.

```python
import numpy as np
from scipy.stats import chi2, norm
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

print("Q7  chi2 de la répartition :", round(((20048 - 19311) ** 2 / 19311) * 2, 1), "| p =", f"{chi2.sf(((20048 - 19311) ** 2 / 19311) * 2, 1):.1e}", "| part de B :", round(18574 / 38622 * 100, 1), "%")
print("Q9  n par groupe :", int(np.ceil(NormalIndPower().solve_power(effect_size=proportion_effectsize(0.046, 0.040), alpha=0.05, power=0.8))))
print("Q11 effet en % :", round((np.exp(0.176) - 1) * 100, 1))
cote = 0.03 / 0.97 * 3.11
print("Q14 probabilité pour le Site :", round(cote / (1 + cote) * 100, 1), "%")
print("Q20 valeur vie client :", round(69 * 0.8 / (1 + 0.10 - 0.8), 1), "€")
v = [100, 110, 90, 120]
print("Q24 moyennes mobiles à 3 mois :", [round(float(np.mean(v[i - 2:i + 1])), 1) for i in (2, 3)])
print("Q27 CA du site :", round(127022 * 0.04785 * 101.63))
print("Q28 limites :", 92 - 3 * 2, "à", 92 + 3 * 2, "| z de 87 % :", (87 - 92) / 2)
print("Q29 volume :", (110 - 100) * 10, "| prix :", round((9.5 - 10) * 110, 2), "| total :", 110 * 9.5 - 100 * 10)
print("Q33 seuil :", round(400000 / 0.38))
print("Q34 marge d'exploitation :", round(39879 / 1103969 * 100, 1), "%")
print("Q35 ROAS de bascule :", round(1 / 0.38, 2))
print("Q36 conversion :", round(6078 / 127022 * 100, 2), "%")
ss = 1.65 * 4 * np.sqrt(10)
print("Q37 stock de sécurité :", round(ss, 1), "| point de commande :", round(12 * 10 + ss, 1))
print("Q38 turnover :", round(7 / 64 * 100, 1), "%")
```
<!--sortie-->
```text
Q7  chi2 de la répartition : 56.3 | p = 6.4e-14 | part de B : 48.1 %
Q9  n par groupe : 17923
Q11 effet en % : 19.2
Q14 probabilité pour le Site : 8.8 %
Q20 valeur vie client : 184.0 €
Q24 moyennes mobiles à 3 mois : [100.0, 106.7]
Q27 CA du site : 617707
Q28 limites : 86 à 98 | z de 87 % : -2.5
Q29 volume : 100 | prix : -55.0 | total : 45.0
Q33 seuil : 1052632
Q34 marge d'exploitation : 3.6 %
Q35 ROAS de bascule : 2.63
Q36 conversion : 4.78 %
Q37 stock de sécurité : 20.9 | point de commande : 140.9
Q38 turnover : 10.9 %
```

**1.** La moyenne dépasse la médiane de 26 % et 61 % des commandes sont sous la moyenne : la distribution est **asymétrique à droite** (quelques gros paniers). On annonce la **médiane** (79,8 €) avec les quartiles, et l'on peut citer la moyenne pour le chiffre d'affaires total (1.1.1, 1.1.6).

**2.** C'est le **paradoxe de Simpson** : les promotions tombent en saison creuse (janvier, été), donc la moyenne globale compare des mois différents ; **dans chaque mois comparable**, la promotion rapporte plus. Il faut comparer à **période égale**, jamais sur la moyenne globale (1.2.5).

**3.** Parce que le chiffre d'affaires est **saisonnier** : novembre et décembre sont naturellement hauts, la règle globale les prend pour des extrêmes. On compare chaque jour à une **référence locale** (même saison, même jour de semaine) et l'on utilise un écart robuste (1.3.3, 1.3.4).

**4.** Une **anomalie** est un écart par rapport à l'attendu (une journée à −55 % de ventes) ; une **erreur** a une cause technique (un chiffre d'affaires multiplié par 10 par une faute de saisie) ; un **événement** a une cause réelle (une panne du site, une fermeture, une grosse commande professionnelle). On ne les traite pas de la même façon : corriger, annoter ou garder (1.3.5).

**5.** La p-valeur est la probabilité, si l'hypothèse nulle est vraie, d'observer un écart au moins aussi grand que celui mesuré. Ce n'est **pas** la probabilité que l'hypothèse nulle soit vraie, ni la probabilité que le résultat soit dû au hasard, ni une mesure de la **taille** ou de l'**importance** de l'effet (2.1.2, 2.1.3).

**6.** L'écart (0,46 point) n'est **pas significatif** (p = 0,14) ; cela ne prouve pas l'absence d'effet : avec 6 000 par groupe, la puissance pour un vrai écart de 0,4 point n'est que d'environ 24 %. On ne conclut pas, et l'on refait le test avec plus de monde (environ 30 000 par groupe pour 80 % de puissance) (2.2.2, 2.5).

**7.** Non : $\chi^2\approx56$, $p\approx6\times10^{-14}$ (code ci-dessus) ; 48,1 % des sessions en B au lieu de 50 %. C'est un **ratio d'échantillon défectueux** (ici le filtre de robots n'a été appliqué qu'au groupe B). Il faut d'abord comprendre et corriger la répartition : tant qu'elle est faussée, la comparaison ne l'est pas moins (2.2.4).

**8.** Chaque coup d'œil est un **test de plus** : le risque de faux positif s'accumule. Dans une simulation sans aucun effet, regarder tous les jours conduit à conclure à tort dans 27 % des cas, au lieu de 5 %. Il faut fixer la taille et la durée à l'avance, ou utiliser des méthodes séquentielles (2.2.6).

**9.** Environ **17 900** personnes par groupe (code ci-dessus) : passer de 4,0 % à 4,6 % est un petit effet (0,6 point) qui exige beaucoup de monde (2.5.2).

**10.** La publicité et les commandes montent **ensemble en novembre-décembre** : la saison est une **variable de confusion**. À mois égal, la corrélation tombe à 0,11, et un modèle avec contrôles ne permet pas de conclure sur l'effet de la publicité (2.3.4).

**11.** $e^{0{,}176}-1\approx19{,}2\ \%$ : à contrôles égaux, un jour de promotion s'accompagne d'environ **19 % de commandes en plus** (3.1.5, 3.2.2).

**12.** C'est l'effet d'une variable lorsque **les autres variables du modèle sont gardées constantes**. Une régression simple attribue à la promotion ce qui vient de la saison, du jour de la semaine, etc. : la régression multiple **sépare** ces effets, d'où des coefficients différents (3.1.3).

**13.** Les erreurs de jours consécutifs sont **corrélées** (autocorrélation) et leur variance n'est pas constante : les erreurs standard classiques sont trop petites et les intervalles trop étroits. Les erreurs robustes (HAC) corrigent cet effet (3.1.7).

**14.** Cote en Boutique $=0{,}03/0{,}97\approx0{,}031$ ; cote pour le Site $\approx0{,}031\times3{,}11\approx0{,}096$, soit une probabilité d'environ **8,8 %** (code ci-dessus). Un rapport de cotes de 3 ne triple pas la probabilité, sauf quand elle est petite (3.3.1).

**15.** Non. Un R² élevé dit que le modèle **reproduit** bien les variations observées, pas qu'il en détermine la **cause**. **Expliquer** demande un modèle interprétable et des hypothèses causales ; **prédire** demande de bonnes prévisions sur des données nouvelles (jeu de test), quelle que soit l'interprétation des coefficients (3.1.8).

**16.** Parce que les k-moyennes reposent sur des **distances** : une variable en euros (milliers) écraserait une variable en nombre de commandes (dizaines). On ramène les variables à des échelles comparables, par exemple en les centrant et réduisant (4.1.4).

**17.** Une silhouette de 0,28 indique une **structure faible** : les groupes se recouvrent. La segmentation peut quand même être **utile** si elle est stable et si les groupes se comportent différemment (réachat), mais on ne doit pas la présenter comme des « familles naturelles » de clients (4.1.5, 4.1.7).

**18.** À cause de l'**observation tronquée à droite** : une cohorte récente n'a pas encore vécu autant de mois que les anciennes ; ses cellules lointaines sont vides, ou reposent sur peu de données. Comparer des cohortes à **âge égal**, jamais à date égale (4.2.6).

**19.** Un score **élevé** sur les trois axes : récence (très récent), fréquence (12 commandes) et montant (1 200 €) la placent dans les meilleurs quintiles. Le score classe des clients **relativement** aux autres, il ne dit pas pourquoi (4.3.1).

**20.** $69\times0{,}8/(1+0{,}10-0{,}8)=184$ € (code ci-dessus). La formule suppose une rétention constante et un horizon infini : elle donne un ordre de grandeur, pas une valeur à garantir (4.3.2).

**21.** En janvier, les ventes valent en moyenne **82 % d'un mois moyen** (18 % de moins) : l'indice est le rapport entre le niveau de janvier et le niveau de référence de la tendance (5.1.4).

**22.** Parce que la **saison** est la même : comparer janvier à décembre compare un creux à un pic. La comparaison au même mois de l'an dernier neutralise la saisonnalité, et mesure la croissance annuelle (5.1.3).

**23.** La référence à battre est la **prévision naïve saisonnière** (« comme à la même période l'an dernier »). Le MAPE est imparfait : il explose quand la valeur réelle est proche de zéro, et il pénalise différemment les surestimations et les sous-estimations (5.2.2, 5.2.3).

**24.** Troisième mois : $(100+110+90)/3=100$ ; quatrième mois : $(110+90+120)/3\approx106{,}7$ (code ci-dessus) (5.2.1).

**25.** Le **nom**, la **formule** exacte, le **périmètre** (quoi est inclus), la **période**, la **source**, le **propriétaire**, la **fréquence** de mise à jour, la **décision** qu'il éclaire, et éventuellement sa cible et ses seuils (6.1.2).

**26.** Si l'on fixe pour cible le **nombre de commandes** en promotion, on pousse les remises : les commandes montent, la marge baisse. Autre exemple : fixer un panier minimum pour la livraison gratuite augmente le panier moyen mais peut faire baisser le chiffre d'affaires. Dès qu'un indicateur devient une cible, il cesse d'être un bon indicateur (6.1.6).

**27.** $127\,022\times0{,}04785\times101{,}63\approx617\,707$ € avec les valeurs arrondies de l'énoncé (code ci-dessus) et exactement 617 715,45 € avec les valeurs non arrondies : l'égalité est exacte à l'euro près. L'arbre sert à **localiser** l'origine d'une variation (6.2.1).

**28.** Limites : $92\pm6$, soit de **86 % à 98 %**. Une semaine à 87 % reste **dans les limites** ($z=-2{,}5$) : ce n'est pas un signal à elle seule ; plusieurs semaines consécutives sous la moyenne, ou une semaine sous 86 %, en seraient un (6.3.4, 6.3.5).

**29.** Effet volume $=(110-100)\times10=+100$ € ; effet prix $=(9{,}5-10)\times110=-55$ € ; total $+45$ € $=1\,045-1\,000$ (code ci-dessus). La convention utilisée (volume au prix budgété, prix aux quantités réelles) fait que les deux effets **somment** à l'écart (7.2).

**30.** Les « 5 pourquoi » consistent à demander successivement « pourquoi ? » pour remonter d'un symptôme à une cause. Chaque cause supposée est une **hypothèse** : on la teste avec les données (corrélation, comparaison, expérience) ; sinon on ne peut écrire que « cause probable » (7.3).

**31.** La règle des 80/20 est un **ordre de grandeur** qui ne se vérifie pas toujours : ici il faut 56 produits sur 120 pour 80 % du chiffre d'affaires. L'**analyse ABC** classe les éléments en trois groupes selon leur contribution cumulée (par exemple 80 / 15 / 5 %), pour adapter la gestion à chaque classe (8.1).

**32.** Non, pas sans comprendre : les **définitions** peuvent différer (quels coûts compte-t-on, quels clients sont « nouveaux » ?), tout comme la période et la taille. Un écart avec une référence est une **question**, pas une conclusion (8.2).

**33.** $400\,000/0{,}38\approx1\,052\,632$ € de chiffre d'affaires (code ci-dessus) : en dessous, l'entreprise perd de l'argent (9.3).

**34.** $39\,879/1\,103\,969\approx3{,}6\ \%$. La **marge brute** ne retire que les achats ; la **marge d'exploitation** retire aussi le personnel, les loyers, le marketing, la livraison et les autres charges (9.2).

**35.** Il faut un ROAS d'au moins $1/0{,}38\approx2{,}6$ : en dessous, chaque euro de publicité rapporte moins d'un euro de marge (10.2).

**36.** $6\,078/127\,022\approx4{,}78\ \%$. La conversion dépend de la **source** (un trafic issu d'un e-mail, déjà client, convertit bien mieux qu'un trafic de réseaux sociaux) : la conversion globale varie avec le **mix** du trafic, pas seulement avec la qualité du site (10.1).

**37.** Stock de sécurité $=1{,}65\times4\times\sqrt{10}\approx20{,}9$ ; point de commande $=12\times10+20{,}9\approx140{,}9$, soit environ **141 unités** (code ci-dessus) (11.2).

**38.** $7/64\approx10{,}9\ \%$. Avec **peu d'événements** (7 départs), l'intervalle de confiance est très large : un taux de 11 % n'est pas distinguable de 5 % ou de 20 % ; on compare avec prudence entre postes ou sites (12.1).

**39.** Le diagramme en tornade classe les paramètres selon l'**effet sur le résultat** d'une variation de chacun, **un à la fois** : il montre où l'incertitude compte le plus. Sa limite : il ignore les **dépendances** entre paramètres et suppose des plages choisies à la main (13.1).

**40.** On présente la **médiane**, un **intervalle** (par exemple 80 %) et la **probabilité de perte** : « dans un cas sur cinq, l'année serait déficitaire ». La simulation ne prédit rien : elle ne vaut que par les **hypothèses** (lois, plages, dépendances) qui l'alimentent (13.2, 13.3).

## Votre grille d'auto-évaluation

Pour chaque ligne : **je sais l'expliquer** / **je sais le faire** / **à revoir**.

| Compétence | Où la retravailler |
|---|---|
| Explorer une variable et repérer des motifs | 1.1, 1.3 |
| Croiser des variables sans tomber dans un paradoxe de Simpson | 1.2 |
| Choisir et lire un test, interpréter une p-valeur | 2.1, 2.4 |
| Concevoir et lire un test A/B | 2.2 |
| Calculer une taille d'échantillon, une puissance | 2.5 |
| Lire une corrélation et la distinguer d'une causalité | 2.3 |
| Ajuster et diagnostiquer une régression | 3.1 |
| Interpréter les coefficients pour des non-spécialistes | 3.2 |
| Modéliser une probabilité (régression logistique) | 3.3 |
| Segmenter des clients et valider la segmentation | 4.1 |
| Lire une matrice de cohortes sans se tromper | 4.2, 4.4 |
| Calculer un RFM, une valeur vie client, un churn | 4.3 |
| Décomposer une série, comparer à l'an dernier | 5.1 |
| Lisser et prévoir honnêtement | 5.2, 5.3 |
| Définir un bon KPI et un arbre d'indicateurs | 6.1, 6.2 |
| Fixer cibles, références et seuils | 6.3 |
| Décomposer un écart et remonter aux causes | 7 |
| Faire un Pareto, une analyse ABC, un benchmarking | 8 |
| Lire des comptes, des ratios, un seuil de rentabilité | 9 |
| Analyser l'acquisition et la rentabilité marketing | 10 |
| Analyser livraisons, stocks et fournisseurs | 11 |
| Analyser effectifs et équité avec prudence | 12 |
| Mesurer sensibilité, simuler, comparer des scénarios | 13 |
| Répondre de bout en bout à une question métier | Projet du volume |
