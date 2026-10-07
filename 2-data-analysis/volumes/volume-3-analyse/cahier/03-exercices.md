# Chapitre 3 : Régression pour les questions métier — exercices et applications

> 🧭 **Ce chapitre du cahier** accompagne le chapitre 3 du livre. Il contient **sept applications guidées** (de petites études que vous refaites sur les données de la boutique) et **quatorze exercices** (de ⭐ à ⭐⭐⭐) avec leurs corrigés. Les calculs à la main servent à comprendre ; le code sert à vérifier et à passer à l'échelle. Essayez toujours **avant** de lire le corrigé.

Une seule cellule charge les bibliothèques et les données. Elle est reprise telle quelle au début de chaque application : si vous travaillez dans un notebook, exécutez-la une fois.

```python
import sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
import outils_ch03 as O

jr = O.charger_jours()                  # un jour par ligne, dépense des 7 derniers jours en k€ (pub_hebdo), pluie 0/1, mois, temps t
lg = O.charger_lignes()                 # une ligne de commande par ligne, avec canal, catégorie et indicateur de retour
f = O.FORMULE
print(len(jr), "jours ;", len(lg), "lignes de commande")
```
<!--sortie-->
```text
1090 jours ; 83905 lignes de commande
```

```python hide
def NUM(cle, valeur):
    print("NUM", cle, valeur)
```

## Applications

### Application 3.1 — La droite à la main, puis à la machine (sections 3.1.1 et 3.1.2)

**Objectif.** Refaire le calcul des moindres carrés sur six jours, le comparer à `statsmodels`, puis lire un tableau de résultats.

**Étape 1 — Six jours, calcul direct.** On prend les six jours du 2 au 7 juin 2025 : dépense publicitaire du jour et nombre de commandes.

```python
six = jr[(jr["date"] >= "2025-06-02") & (jr["date"] <= "2025-06-07")]
x, y = six["depense_pub"].values, six["nb_commandes"].values.astype(float)
b = ((x - x.mean()) * (y - y.mean())).sum() / ((x - x.mean()) ** 2).sum()
a = y.mean() - b * x.mean()
e = y - (a + b * x)
print("pente :", round(b, 4), "| ordonnée :", round(a, 2), "| somme des résidus :", round(e.sum(), 6))
print("R2 :", round(1 - (e ** 2).sum() / ((y - y.mean()) ** 2).sum(), 3))
```
<!--sortie-->
```text
pente : 0.1318 | ordonnée : 21.63 | somme des résidus : 0.0
R2 : 0.198
```

**Étape 2 — La même chose avec `statsmodels`.** Vérifiez que l'on retrouve la pente, l'ordonnée et le $R^2$.

```python
m6 = smf.ols("nb_commandes ~ depense_pub", data=six).fit()
print(m6.params.round(4).to_dict(), "| R2 =", round(m6.rsquared, 3), "| intervalle de la pente :", m6.conf_int().loc["depense_pub"].round(4).tolist())
```
<!--sortie-->
```text
{'Intercept': 21.6251, 'depense_pub': 0.1318} | R2 = 0.198 | intervalle de la pente : [-0.2363, 0.4999]
```

**Étape 3 — Sur tous les jours.** Régressez le nombre de commandes sur la température moyenne et lisez chaque colonne du tableau.

```python
mt = smf.ols("nb_commandes ~ temperature_moy", data=jr).fit()
print(mt.summary2().tables[1].round(3))
print("R2 =", round(mt.rsquared, 3))
```
<!--sortie-->
```text
                  Coef.  Std.Err.       t  P>|t|  [0.025  0.975]
Intercept        38.722     0.838  46.223    0.0  37.078  40.365
temperature_moy  -0.415     0.057  -7.328    0.0  -0.526  -0.304
R2 = 0.047
```

**À vous.** (1) Sur six jours, l'intervalle de confiance de la pente est-il étroit ? Qu'en concluez-vous ? (2) La pente de la température est négative : la chaleur fait-elle baisser les commandes ? Quelle variable cachée (le mois) pourrait l'expliquer ? (3) Le $R^2$ est-il élevé ? Un $R^2$ faible veut-il dire que le coefficient est mal estimé ?

### Application 3.2 — Promotion et publicité : du modèle naïf au modèle contrôlé (section 3.1.3)

**Objectif.** Reproduire la construction « marche par marche » et voir le coefficient de la publicité s'effondrer quand on contrôle la saison.

```python
etapes = {"A. promo + pub": "np.log(nb_commandes) ~ promo_active + pub_hebdo",
          "B. + jour de la semaine": "np.log(nb_commandes) ~ promo_active + pub_hebdo + C(jour_semaine)",
          "C. + mois": "np.log(nb_commandes) ~ promo_active + pub_hebdo + C(jour_semaine) + C(mois)",
          "D. modèle complet": f}
lignes = []
for nom, fm in etapes.items():
    m = smf.ols(fm, data=jr).fit(cov_type="HAC", cov_kwds={"maxlags": 7})
    ic = m.conf_int().loc["pub_hebdo"]
    lignes.append((nom, O.pct(m.params["promo_active"]), O.pct(m.params["pub_hebdo"]), O.pct(ic[0]), O.pct(ic[1])))
print(pd.DataFrame(lignes, columns=["modèle", "promo %", "pub %", "pub bas", "pub haut"]).round(1).to_string(index=False))
```
<!--sortie-->
```text
                 modèle  promo %  pub %  pub bas  pub haut
         A. promo + pub      2.4   31.4     25.7      37.4
B. + jour de la semaine      2.0   31.5     25.9      37.4
              C. + mois     18.8   -0.2     -6.5       6.6
      D. modèle complet     19.2    0.1     -5.1       5.7
```

**À vous.** (1) À quelle étape l'effet de la publicité disparaît-il ? Quel est le point commun entre la publicité et le mois ? (2) Remplacez `pub_hebdo` par la dépense **du jour** (`depense_pub`) : le résultat change-t-il ? (3) Ajoutez la température au modèle complet : que devient le coefficient de la pluie, et pourquoi la température seule est-elle un mauvais contrôle du mois ?

### Application 3.3 — Indicatrices, logarithmes et interactions (sections 3.1.4 à 3.1.6)

**Objectif.** Changer de catégorie de référence, vérifier que le modèle ne change pas, estimer une élasticité, tester une interaction.

```python
mod = smf.ols(f, data=jr).fit()
f2 = f.replace("C(jour_semaine)", "C(jour_semaine, Treatment(7))")           # le dimanche devient la référence
mod2 = smf.ols(f2, data=jr).fit()
print("mêmes valeurs prévues :", np.allclose(mod.fittedvalues, mod2.fittedvalues))
print("samedi contre dimanche :", round(O.pct(mod2.params["C(jour_semaine, Treatment(7))[T.6]"]), 1), "%")
```
<!--sortie-->
```text
mêmes valeurs prévues : True
samedi contre dimanche : 109.9 %
```

```python
from statsmodels.stats.anova import anova_lm
jr["weekend"] = jr["jour_semaine"].isin([6, 7]).astype(int)
f_int = f.replace("promo_active", "promo_active * weekend").replace("C(jour_semaine) + ", "")
m_int = smf.ols(f_int, data=jr).fit()
print("effet de la promotion en semaine :", round(O.pct(m_int.params["promo_active"]), 1), "%")
print("écart pour le week-end (coefficient d'interaction) :", round(m_int.params["promo_active:weekend"], 3), "| p-valeur :", round(m_int.pvalues["promo_active:weekend"], 3))
```
<!--sortie-->
```text
effet de la promotion en semaine : 17.4 %
écart pour le week-end (coefficient d'interaction) : 0.094 | p-valeur : 0.078
```

**À vous.** (1) Pourquoi les valeurs prévues sont-elles identiques malgré le changement de référence ? (2) L'interaction promotion × week-end est-elle significative ? Ajouteriez-vous cette interaction au modèle ? (3) Testez l'interaction promotion × mois d'hiver (janvier et février) : que remarquez-vous sur le nombre de jours concernés ?

### Application 3.4 — Diagnostic : résidus, erreurs robustes, colinéarité, points influents (section 3.1.7)

**Objectif.** Appliquer les quatre contrôles du livre au modèle complet.

```python
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.outliers_influence import variance_inflation_factor as vif
mco = smf.ols(f, data=jr).fit()
mha = smf.ols(f, data=jr).fit(cov_type="HAC", cov_kwds={"maxlags": 7})
print("Breusch-Pagan p =", round(het_breuschpagan(mco.resid, mco.model.exog)[1], 4), "| Durbin-Watson =", round(durbin_watson(mco.resid), 2))
print(pd.DataFrame({"classique": mco.bse, "HAC": mha.bse}).loc[["promo_active", "pub_hebdo", "pluie_jour", "t"]].round(4))
```
<!--sortie-->
```text
Breusch-Pagan p = 0.0001 | Durbin-Watson = 1.99
              classique     HAC
promo_active     0.0215  0.0248
pub_hebdo        0.0234  0.0274
pluie_jour       0.0123  0.0112
t                0.0066  0.0061
```

```python
noms = mco.model.exog_names
print({n: round(float(vif(mco.model.exog, noms.index(n))), 1) for n in ["promo_active", "pub_hebdo", "pluie_jour", "t"]})
cook = mco.get_influence().cooks_distance[0]
print(jr.assign(cook=cook).nlargest(5, "cook")[["date", "nb_commandes", "promo_active", "cook"]].round(3).to_string(index=False))
```
<!--sortie-->
```text
{'promo_active': 1.9, 'pub_hebdo': 8.7, 'pluie_jour': 1.0, 't': 1.1}
      date  nb_commandes  promo_active  cook
2024-01-01            14             0 0.034
2024-01-02            15             0 0.015
2025-02-09             9             0 0.012
2024-01-07            10             0 0.010
2024-04-10            16             0 0.009
```

**À vous.** (1) Les erreurs types robustes sont-elles plus grandes ou plus petites que les classiques ? Les coefficients changent-ils ? (2) Quelle variable a le VIF le plus élevé, et pourquoi ? (3) Retirez les cinq jours les plus influents et réajustez : la conclusion sur la promotion change-t-elle ?

### Application 3.5 — Expliquer ou prédire : 2025 mis de côté (section 3.1.8)

**Objectif.** Juger une prévision sur des jours que le modèle n'a pas vus, et la comparer à des références.

```python
app, test = jr[jr["annee"] <= 2024], jr[jr["annee"] == 2025]
m_app = smf.ols(f, data=app).fit()
prevu = np.exp(m_app.predict(test))
mae = (test["nb_commandes"] - prevu).abs().mean()
mape = ((test["nb_commandes"] - prevu).abs() / test["nb_commandes"]).mean() * 100
print("modèle complet : MAE =", round(mae, 2), "| MAPE =", round(mape, 1), "% | R2 d'ajustement =", round(m_app.rsquared, 3))
```
<!--sortie-->
```text
modèle complet : MAE = 4.44 | MAPE = 12.9 % | R2 d'ajustement = 0.757
```

```python
ref = jr.set_index("date")["nb_commandes"].shift(364).reindex(test["date"]).values        # même jour de semaine, un an plus tôt
print("même jour 364 jours avant : MAE =", round(np.nanmean(np.abs(test["nb_commandes"].values - ref)), 2))
for nom, fm in {"sans les mois": f.replace(" + C(mois)", ""), "sans le jour de la semaine": f.replace(" + C(jour_semaine)", "")}.items():
    m = smf.ols(fm, data=app).fit()
    print(nom, ": MAE =", round((test["nb_commandes"] - np.exp(m.predict(test))).abs().mean(), 2))
```
<!--sortie-->
```text
même jour 364 jours avant : MAE = 6.66
sans les mois : MAE = 6.24
sans le jour de la semaine : MAE = 7.35
```

**À vous.** (1) Quelle variable fait le plus perdre en prévision quand on la retire ? (2) Le modèle fait-il mieux que la référence « même jour, un an plus tôt » ? (3) Estimez l'erreur sur les seuls jours de promotion : le modèle y est-il meilleur ou moins bon ?

### Application 3.6 — Présenter à la gérante (sections 3.2.1 à 3.2.6)

**Objectif.** Fabriquer automatiquement des phrases d'interprétation justes, avec effet, incertitude et conditions.

```python
mod = smf.ols(f, data=jr).fit(cov_type="HAC", cov_kwds={"maxlags": 7})
ic = mod.conf_int()

def phrase(nom, libelle, unite):
    e, lo, hi = (O.pct(v) for v in (mod.params[nom], ic.loc[nom, 0], ic.loc[nom, 1]))
    if lo < 0 < hi:
        return f"{libelle} : pas d'effet détecté ({e:+.1f} %, intervalle de {lo:+.1f} % à {hi:+.1f} %)."
    return f"{libelle} : {e:+.1f} % de commandes {unite}, intervalle de {lo:+.1f} % à {hi:+.1f} %."

print(phrase("promo_active", "Jour de promotion", "par rapport à un jour comparable sans promotion"))
print(phrase("pub_hebdo", "1 000 € de publicité hebdomadaire de plus", "toutes choses égales par ailleurs"))
print(phrase("pluie_jour", "Jour de pluie", "toutes choses égales par ailleurs"))
```
<!--sortie-->
```text
Jour de promotion : +19.2 % de commandes par rapport à un jour comparable sans promotion, intervalle de +13.5 % à +25.1 %.
1 000 € de publicité hebdomadaire de plus : pas d'effet détecté (+0.1 %, intervalle de -5.1 % à +5.7 %).
Jour de pluie : pas d'effet détecté (-1.7 %, intervalle de -3.8 % à +0.5 %).
```

**À vous.** (1) Ajoutez la phrase du samedi contre lundi. (2) Convertissez l'effet de la promotion en commandes par jour pour un jour moyen de promotion (voir le livre, 3.2.1). (3) Rédigez les cinq lignes pour la gérante.

### Application 3.7 — Les retours : régression logistique et seuil (section 3.3)

**Objectif.** Estimer des rapports de cotes, juger le modèle et choisir un seuil par un calcul de coûts.

```python
fl = "retour ~ C(canal, Treatment('Boutique')) + C(categorie) + np.log(prix_unitaire) + promo + quantite"
mlog = smf.logit(fl, data=lg).fit(disp=0)
rc = np.exp(pd.concat([mlog.params, mlog.conf_int()], axis=1)); rc.columns = ["rapport de cotes", "bas", "haut"]
print(rc.drop("Intercept").round(2).head(6))
```
<!--sortie-->
```text
                                            rapport de cotes   bas  haut
C(canal, Treatment('Boutique'))[T.Réseaux]              2.25  2.04  2.49
C(canal, Treatment('Boutique'))[T.Site]                 3.11  2.91  3.33
C(categorie)[T.Cuisine]                                 1.01  0.90  1.12
C(categorie)[T.Décoration]                              0.99  0.89  1.10
C(categorie)[T.Jardin]                                  1.01  0.91  1.13
C(categorie)[T.Maison]                                  0.95  0.85  1.06
```

```python
from sklearn.metrics import roc_auc_score
lg["p"] = mlog.predict(lg)
print("AUC :", round(roc_auc_score(lg["retour"], lg["p"]), 3), "| taux de retour :", round(lg["retour"].mean() * 100, 1), "%")
cout_retour, cout_action, succes = 18.0, 0.5, 0.4
b = lg.groupby("canal").agg(lignes=("retour", "size"), retours=("retour", "sum"))
b["gain net (€)"] = (b["retours"] * succes * cout_retour - b["lignes"] * cout_action).round(0)
print(b)
```
<!--sortie-->
```text
AUC : 0.636 | taux de retour : 6.0 %
          lignes  retours  gain net (€)
canal                                  
Boutique   39362     1211      -10962.0
Réseaux     9071      605        -180.0
Site       35472     3186        5203.0
```

**À vous.** (1) Quel est le seuil de probabilité rentable ? Quels canaux dépassent ce seuil ? (2) Si l'action n'évite le retour que dans 25 % des cas, que devient la décision ? (3) Ajoutez le mois de la commande au modèle : la saison joue-t-elle sur les retours ?

## Exercices

### Exercice 3.1 ⭐ — Une pente à la main (section 3.1.1)

Quatre jours : dépense publicitaire $x$ (en centaines d'euros) 1, 2, 3, 4 et commandes $y$ : 20, 26, 29, 37. Calculez la pente et l'ordonnée de la droite des moindres carrés, puis la prévision pour une dépense de 5.

### Exercice 3.2 ⭐ — Un $R^2$ à la main (section 3.1.1)

Avec les données de l'exercice 3.1, calculez les résidus, leur somme et la somme de leurs carrés, puis le $R^2$. Que veut dire cette valeur ?

### Exercice 3.3 ⭐⭐ — Lire un tableau de résultats (section 3.1.2)

Un tableau indique, pour la pente de la publicité du jour : coefficient 0,061, erreur type 0,003. (1) Calculez le $t$ et un intervalle de confiance approximatif à 95 %. (2) Un collègue dit « la p-valeur est nulle, donc la publicité est très efficace ». Que lui répondez-vous ?

### Exercice 3.4 ⭐ — Toutes choses égales par ailleurs (section 3.1.3)

Un modèle de régression sur les commandes quotidiennes donne : promotion $+0{,}175$ (en logarithme), samedi $+0{,}375$ par rapport au lundi. Un jour de promotion tombe un samedi. Que prévoit le modèle pour ce jour par rapport à un lundi sans promotion, en pourcentage ?

### Exercice 3.5 ⭐⭐ — De la valeur du coefficient à l'effet en pourcentage (section 3.1.5)

(1) Convertissez en pourcentage les coefficients du logarithme suivants : $0{,}05$, $0{,}175$, $-0{,}017$, $0{,}754$. (2) À partir de quelle taille l'approximation « le coefficient est le pourcentage » devient-elle trompeuse ? (3) Quelle élasticité faut-il pour qu'une hausse de 10 % de la dépense publicitaire fasse monter les commandes de 1 % ?

### Exercice 3.6 ⭐⭐ — Les indicatrices (section 3.1.4)

On régresse les commandes sur le canal d'acquisition d'un client (Boutique, Site, Réseaux) avec la Boutique en référence. (1) Combien d'indicatrices crée-t-on ? (2) Que vaut le coefficient du Site si les moyennes des trois groupes sont 4,0, 5,5 et 3,5 (dans l'ordre Boutique, Site, Réseaux) ? (3) Que devient-il si le Site est la référence ?

### Exercice 3.7 ⭐⭐ — La colinéarité à la main (section 3.1.7)

Deux variables explicatives ont une corrélation de 0,9. Avec seulement ces deux variables, le VIF de chacune vaut $1/(1-r^2)$. (1) Calculez-le. (2) De combien l'erreur type d'un coefficient est-elle multipliée par rapport au cas indépendant ? (3) La publicité a un VIF de 8,7 dans le modèle du livre : que cela signifie-t-il ?

### Exercice 3.8 ⭐⭐ — Détecter un défaut (section 3.1.7)

Sur une série de 8 résidus consécutifs $+2, +1, +2, -1, -2, -1, +1, +2$, calculez la statistique de Durbin-Watson $\sum_{t\ge2}(e_t-e_{t-1})^2/\sum e_t^2$. Qu'indique-t-elle ? Et qu'indiquerait un résultat proche de 2 ?

### Exercice 3.9 ⭐⭐ — Mesurer une prévision (section 3.1.8)

Quatre jours : commandes observées 30, 40, 50, 60 ; prévues 33, 36, 55, 57. Calculez l'erreur absolue moyenne et l'erreur relative moyenne (MAPE). Un modèle qui prévoit toujours 45 fait-il mieux ?

### Exercice 3.10 ⭐⭐⭐ — Une expérience pour trancher sur la publicité (section 3.1.9)

L'intervalle de confiance de l'effet de la publicité va de −5 % à +6 % par millier d'euros. On veut distinguer un effet de +1,5 % de zéro. (1) Si l'on pouvait répartir **au hasard** la dépense hebdomadaire entre deux niveaux, combien de semaines faudrait-il, en supposant que l'écart-type du logarithme des commandes hebdomadaires autour de leur moyenne est de 0,06 ? (2) Pourquoi une expérience aléatoire résout-elle le problème de la saison ?

### Exercice 3.11 ⭐ — Réécrire des phrases (section 3.2.5)

Corrigez : (a) « La pluie ne compte pas, son coefficient est de −1,7 % ». (b) « Chaque euro de publicité rapporte 0,06 commande ». (c) « p < 0,05 donc la promotion est très importante ».

### Exercice 3.12 ⭐⭐ — Relatif ou absolu (section 3.2.2)

La promotion augmente les commandes de 19 % et le chiffre d'affaires de 8 %. (1) Pour un jour à 20 commandes sans promotion, combien de commandes de plus ? Et pour un jour à 50 ? (2) Comment l'effet sur le chiffre d'affaires peut-il être plus faible que sur les commandes ? (3) Quel indicateur faudrait-il ajouter pour répondre à « est-ce que ça rapporte ? »

### Exercice 3.13 ⭐ — Un rapport de cotes à la main (section 3.3.1)

Sur 1 000 lignes du Site, 90 sont retournées ; sur 1 000 lignes de la Boutique, 30. Calculez les deux probabilités, les deux cotes, le rapport de cotes et le rapport de probabilités.

### Exercice 3.14 ⭐⭐ — Un seuil par les coûts (section 3.3.5)

Un retour coûte 25 €, une vérification coûte 1 € par ligne et évite le retour dans 50 % des cas. (1) Quel est le seuil de probabilité rentable ? (2) Une ligne a une probabilité de retour de 6 % : faut-il la vérifier ? (3) Que devient le seuil si la vérification coûte 2 € ?

## Corrigés

### Corrigé 3.1

$\bar x=2{,}5$, $\bar y=28$ ; $S_{xy}=(-1{,}5)(-8)+(-0{,}5)(-2)+(0{,}5)(1)+(1{,}5)(9)=12+1+0{,}5+13{,}5=27$ ; $S_{xx}=2{,}25+0{,}25+0{,}25+2{,}25=5$. Pente $b=27/5=5{,}4$ commandes par centaine d'euros ; ordonnée $a=28-5{,}4\times2{,}5=14{,}5$. Prévision pour $x=5$ : $14{,}5+5{,}4\times5=41{,}5$ commandes.

```python hide
x_ = np.array([1, 2, 3, 4.]); y_ = np.array([20, 26, 29, 37.])
b_ = ((x_ - x_.mean()) * (y_ - y_.mean())).sum() / ((x_ - x_.mean()) ** 2).sum(); a_ = y_.mean() - b_ * x_.mean()
assert abs(b_ - 5.4) < 1e-9 and abs(a_ - 14.5) < 1e-9 and abs(a_ + 5 * b_ - 41.5) < 1e-9
e_ = y_ - (a_ + b_ * x_); r2_ = 1 - (e_ ** 2).sum() / ((y_ - y_.mean()) ** 2).sum()
assert abs(e_.sum()) < 1e-9 and abs((e_ ** 2).sum() - 4.2) < 1e-9 and abs(r2_ - (1 - 4.2 / 150)) < 1e-9
```

### Corrigé 3.2

Valeurs prévues : 19,9 ; 25,3 ; 30,7 ; 36,1. Résidus : 0,1 ; 0,7 ; −1,7 ; 0,9 (somme nulle). Somme des carrés : $0{,}01+0{,}49+2{,}89+0{,}81=4{,}2$. Variabilité totale : $\sum(y-\bar y)^2=(-8)^2+(-2)^2+1^2+9^2=150$, donc $R^2=1-4{,}2/150=0{,}972$. La droite explique 97 % de la variabilité de ces quatre jours (un $R^2$ très élevé sur quatre points ne prouve pas grand-chose).

### Corrigé 3.3

(1) $t=0{,}061/0{,}003\approx20{,}3$ ; intervalle approximatif $0{,}061\pm1{,}96\times0{,}003$, soit de 0,055 à 0,067. (2) Une p-valeur nulle dit seulement que la pente est **distinguable de zéro** dans ce modèle ; elle ne dit ni que l'effet est grand (0,061 commande par euro), ni qu'il est **causal** : sans contrôle de la saison, la publicité capte l'effet des mois chargés (livre, 3.1.3).

### Corrigé 3.4

Dans un modèle sur le logarithme, les effets se **multiplient** : $e^{0{,}175+0{,}375}=e^{0{,}55}\approx1{,}73$, soit environ **+73 %** par rapport à un lundi sans promotion. Attention : additionner les pourcentages ($+19{,}1\ \%+45{,}5\ \%=64{,}6\ \%$) est faux, car $1{,}191\times1{,}455\approx1{,}733$.

```python hide
assert abs(np.exp(0.55) - 1.7333) < 1e-3 and abs(np.exp(0.175) * np.exp(0.375) - np.exp(0.55)) < 1e-12
```

### Corrigé 3.5

(1) $e^{0{,}05}-1=5{,}1\ \%$ ; $e^{0{,}175}-1=19{,}1\ \%$ ; $e^{-0{,}017}-1=-1{,}7\ \%$ ; $e^{0{,}754}-1=112{,}5\ \%$. (2) Pour un coefficient inférieur à 0,05 en valeur absolue, l'approximation est bonne (écart inférieur à 0,2 point) ; au-delà de 0,2, elle sous-estime nettement (0,754 donne 75 % au lieu de 112 %). (3) Une élasticité de 0,1 : $10\ \%\times0{,}1=1\ \%$ (approximation valable pour de petites variations).

```python hide
assert [round((np.exp(b) - 1) * 100, 1) for b in (0.05, 0.175, -0.017, 0.754)] == [5.1, 19.1, -1.7, 112.5]
```

### Corrigé 3.6

(1) **Deux** indicatrices (Site et Réseaux) ; la Boutique est la référence. (2) Coefficient du Site : $5{,}5-4{,}0=+1{,}5$ commande en moyenne ; Réseaux : $3{,}5-4{,}0=-0{,}5$. (3) Avec le Site en référence : Boutique $4{,}0-5{,}5=-1{,}5$ et Réseaux $3{,}5-5{,}5=-2{,}0$ ; le modèle (les moyennes prévues) est inchangé.

### Corrigé 3.7

(1) $\text{VIF}=1/(1-0{,}81)=1/0{,}19\approx5{,}26$. (2) L'erreur type est multipliée par $\sqrt{\text{VIF}}\approx2{,}3$. (3) Un VIF de 8,7 multiplie l'erreur type par $\sqrt{8{,}7}\approx2{,}9$ : le coefficient de la publicité est près de **trois fois plus incertain** qu'il le serait si la publicité ne dépendait pas du mois ; c'est l'une des raisons de la largeur de son intervalle.

### Corrigé 3.8

Différences successives : $-1, +1, -3, -1, +1, +2, +1$ ; carrés : $1+1+9+1+1+4+1=18$. Somme des carrés des résidus : $4+1+4+1+4+1+1+4=20$. $DW=18/20=0{,}9$. Une valeur nettement **inférieure à 2** indique une **autocorrélation positive** (les résidus d'un jour ressemblent à ceux de la veille) : les erreurs types classiques sont trop petites, d'où les erreurs robustes. Un résultat proche de 2 indique l'absence d'autocorrélation.

```python hide
r_ = np.array([2, 1, 2, -1, -2, -1, 1, 2.]); assert abs((np.diff(r_) ** 2).sum() / (r_ ** 2).sum() - 0.9) < 1e-12
```

### Corrigé 3.9

Erreurs absolues : $3, 4, 5, 3$ ; MAE $=15/4=3{,}75$. Erreurs relatives : $3/30=0{,}10$ ; $4/40=0{,}10$ ; $5/50=0{,}10$ ; $3/60=0{,}05$ ; MAPE $=8{,}75\ \%$. Le modèle « toujours 45 » a des erreurs absolues $15, 5, 5, 15$ : MAE $=10$ : bien pire.

```python hide
o_ = np.array([30, 40, 50, 60.]); p_ = np.array([33, 36, 55, 57.])
assert abs(np.abs(o_ - p_).mean() - 3.75) < 1e-12 and abs((np.abs(o_ - p_) / o_).mean() - 0.0875) < 1e-12 and np.abs(o_ - 45).mean() == 10
```

### Corrigé 3.10

(1) On compare deux niveaux de dépense qui diffèrent de 1 000 € par semaine, avec $n$ semaines par niveau ; l'erreur type de la différence de moyennes de logarithmes est $0{,}06\sqrt{2/n}$ ; on veut que l'effet de 0,015 (environ 1,5 % en logarithme) soit à 2,8 erreurs types (puissance de 80 % au seuil de 5 %) : $0{,}015\ge2{,}8\times0{,}06\sqrt{2/n}$, soit $n\ge2\times(2{,}8\times0{,}06/0{,}015)^2=2\times125=250$ semaines par groupe. C'est irréaliste : il faudrait **des années** ; on augmente la puissance en expérimentant par **zone géographique** ou **par jour** plutôt que par semaine, ou en visant un effet plus grand. (2) Le tirage au hasard rend la dépense **indépendante** de la saison (en moyenne, chaque niveau tombe autant en décembre qu'en janvier) : la comparaison n'a plus besoin de « contrôler » la saison.

```python hide
n_ = 2 * (2.8 * 0.06 / 0.015) ** 2; assert abs(n_ - 250.88) < 0.5 or abs(n_ - 250) < 1.5
```

### Corrigé 3.11

(a) « Pas d'effet net de la pluie détecté (−1,7 %, intervalle de −3,8 % à +0,5 %) ; s'il existe, il est petit. » (b) « Sans contrôle de la saison, la publicité semblait faire gagner 0,06 commande par euro ; après contrôle, aucun effet n'est détecté. » (c) « La promotion augmente d'environ 19 % les commandes (intervalle de 13 % à 25 %) ; la p-valeur dit seulement que l'effet n'est pas dû au hasard d'échantillonnage. »

### Corrigé 3.12

(1) Pour 20 commandes sans promotion : $0{,}19\times20=3{,}8$ commandes de plus ; pour 50 : $9{,}5$. L'effet **absolu** dépend de la base. (2) Les promotions s'accompagnent de remises de 5 à 20 % : chaque commande rapporte moins, de sorte que le chiffre d'affaires augmente moins vite que le nombre de commandes ($1{,}19\times(1-r)\approx1{,}08$ avec une remise moyenne $r$ d'environ 9 %). (3) La **marge** (chiffre d'affaires hors taxe moins coût des produits) : voir le chapitre 9.

```python hide
assert abs(0.19 * 20 - 3.8) < 1e-12 and abs(0.19 * 50 - 9.5) < 1e-12 and abs(1 - 1.08 / 1.19 - 0.0924) < 1e-3
```

### Corrigé 3.13

Probabilités : Site $90/1\,000=9\ \%$, Boutique $3\ \%$. Cotes : Site $90/910\approx0{,}0989$, Boutique $30/970\approx0{,}0309$. Rapport de cotes : $0{,}0989/0{,}0309\approx3{,}20$. Rapport de probabilités : $9/3=3{,}0$. Le rapport de cotes est un peu supérieur au risque relatif, parce que l'événement n'est pas infiniment rare.

```python hide
assert abs((90 / 910) / (30 / 970) - 3.198) < 1e-3
```

### Corrigé 3.14

(1) $p^{*}=c/(q\,s)=1/(0{,}5\times25)=0{,}08$, soit 8 %. (2) Une ligne à 6 % est **sous le seuil** : la vérification coûterait 1 € pour un gain espéré de $0{,}06\times0{,}5\times25=0{,}75$ € : non rentable. (3) Avec un coût de 2 € : $p^{*}=2/12{,}5=0{,}16$, soit 16 % : presque aucune ligne ne dépasse ce seuil.

```python hide
assert abs(1 / (0.5 * 25) - 0.08) < 1e-12 and abs(0.06 * 0.5 * 25 - 0.75) < 1e-12 and abs(2 / 12.5 - 0.16) < 1e-12
```
