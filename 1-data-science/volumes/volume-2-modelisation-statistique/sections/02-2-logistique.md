## 2.2 Régression logistique

> 💡 **Intuition.** la gérante envoie un bon de bienvenue à la moitié de ses nouveaux clients, tirés au sort. Douze mois plus tard, elle observe pour chaque client un seul bit d'information : a-t-il **racheté** (1) ou non (0) ? Elle veut savoir de combien l'offre augmente les chances de rachat, et comment les autres caractéristiques (âge, canal d'acquisition, satisfaction) y contribuent. La régression logistique modélise la **probabilité** de racheter, mais pas directement : elle modélise une transformation de cette probabilité, la **cote**, qui vit sur toute la droite réelle et qui se prête à un modèle linéaire.

### 2.2.1 De la probabilité à la cote

Si un événement a la probabilité $p$, sa **cote** (*odds*) est $\dfrac{p}{1-p}$ : le rapport entre les chances que l'événement arrive et les chances qu'il n'arrive pas. Une probabilité de $0{,}75$ donne une cote de $3$ (« trois contre un »). Le **logit** est le logarithme de la cote : $\operatorname{logit}(p)=\log\dfrac{p}{1-p}$.

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from scipy.special import expit

clients = pd.read_csv("donnees/clients.csv")
clients["canal"] = pd.Categorical(clients["canal_acquisition"], categories=["Boutique", "Réseaux", "Site"])  # référence : Boutique

p = np.array([0.05, 0.10, 0.25, 0.50, 0.60, 0.75, 0.90, 0.95])
tab = pd.DataFrame({"probabilité p": p, "cote p/(1-p)": p / (1 - p), "logit = log(cote)": np.log(p / (1 - p))})
print(tab.round(3).to_string(index=False))
```
<!--sortie-->
```text
 probabilité p  cote p/(1-p)  logit = log(cote)
          0.05         0.053             -2.944
          0.10         0.111             -2.197
          0.25         0.333             -1.099
          0.50         1.000              0.000
          0.60         1.500              0.405
          0.75         3.000              1.099
          0.90         9.000              2.197
          0.95        19.000              2.944
```

Lisez le tableau en trois temps. Une probabilité de 0,5 correspond à une cote de 1 (« une chance contre une ») et à un logit de 0. Les probabilités symétriques ont des logits **opposés** : $0{,}25$ donne $-1{,}099$ et $0{,}75$ donne $+1{,}099$ ; $0{,}05$ donne $-2{,}944$ et $0{,}95$ donne $+2{,}944$. Enfin, le logit **étire les extrémités** : passer de 90 % à 95 % ne change presque rien en probabilité (5 points), mais la cote passe de 9 à 19 et le logit de 2,2 à 2,9. C'est précisément ce qui permet d'écrire un modèle linéaire sans jamais sortir de $]0,1[$.

Le logit est la fonction qui transforme une probabilité ($]0,1[$) en un nombre réel quelconque ($]-\infty,+\infty[$) ; sa réciproque, la fonction **logistique** $\operatorname{expit}(\eta)=\dfrac1{1+e^{-\eta}}$, fait le chemin inverse. C'est elle qui donne à la courbe sa forme de **S**.

### 2.2.2 Le modèle

Le client $i$ a pour caractéristiques $x_i$ et un résultat $Y_i\in\{0,1\}$. Le modèle de **régression logistique** (cas $\text{Bernoulli}$ + lien logit, le lien canonique du tableau de 2.1.3) pose
$$Y_i\sim\text{Bernoulli}(p_i),\qquad \operatorname{logit}(p_i)=\log\frac{p_i}{1-p_i}=\beta_0+\beta_1x_{i1}+\dots+\beta_px_{ip},$$
soit, de façon équivalente, $p_i=\dfrac{1}{1+e^{-x_i^\top\beta}}$.

> 📐 **Une deuxième lecture : la variable latente.** Imaginons que chaque client ait une « envie de racheter » continue $Y_i^*=x_i^\top\beta+\varepsilon_i$, que nous n'observons pas ; il rachète si cette envie dépasse zéro. Si $\varepsilon_i$ suit la **loi logistique** (de fonction de répartition $F(t)=1/(1+e^{-t})$), alors $P(Y_i=1)=P(\varepsilon_i>-x_i^\top\beta)=F(x_i^\top\beta)$ par symétrie : on retrouve exactement le modèle logistique. (Si $\varepsilon_i$ était normale, on obtiendrait le modèle **probit**, très voisin.) Cette image aide à comprendre pourquoi la courbe est un S : près de $p=0{,}5$, un petit changement de l'envie fait basculer beaucoup de clients ; près de 0 ou de 1, il en faut beaucoup plus.

**Comment lire un coefficient ?** Si la variable $x_j$ augmente d'une unité, toutes choses égales par ailleurs, le logit augmente de $\beta_j$, c'est-à-dire que la **cote est multipliée par $e^{\beta_j}$** : $e^{\beta_j}$ est un **rapport de cotes** (*odds ratio*, OR). Un OR de 1 signifie « pas d'effet » ; supérieur à 1, l'effet favorise l'événement ; inférieur à 1, il le défavorise. Mais sur l'échelle de la **probabilité**, l'effet n'est pas constant :

```python
beta = 0.5                     # un effet de +0,5 sur le logit : OR = exp(0,5) ≈ 1,65
p0 = np.array([0.02, 0.10, 0.30, 0.50, 0.70, 0.90, 0.98])
p1 = expit(np.log(p0 / (1 - p0)) + beta)
print("OR =", round(float(np.exp(beta)), 3))
print(pd.DataFrame({"p avant": p0, "p après": p1, "gain (points)": 100 * (p1 - p0)}).round(3).to_string(index=False))
```
<!--sortie-->
```text
OR = 1.649
 p avant  p après  gain (points)
    0.02    0.033          1.255
    0.10    0.155          5.483
    0.30    0.414         11.404
    0.50    0.622         12.246
    0.70    0.794          9.369
    0.90    0.937          3.686
    0.98    0.988          0.777
```

Un même effet de $+0{,}5$ sur le logit (un OR de 1,649) produit un gain de **12,2 points** quand la probabilité de départ est de 50 %, mais seulement 5,5 points à 10 %, 3,7 points à 90 % et 1,3 point à 2 %. L'effet en points de pourcentage est donc **maximal au milieu** et s'écrase vers 0 et 1 (pour un petit effet, il vaut environ $\beta\,p(1-p)$ : ici $0{,}5\times0{,}25=12{,}5$ à $p=0{,}5$, très proche de 12,2). Conclusion pratique : **un coefficient logistique est constant sur l'échelle du logit, pas sur celle de la probabilité** ; pour parler en points de pourcentage, il faut préciser *pour quel client*.

### 2.2.3 Un premier modèle : l'offre de bienvenue seule

Commençons par le modèle le plus simple, une seule variable binaire : `offre_bienvenue`. Avant de l'ajuster, calculons tout à la main à partir du tableau croisé.

```python
croise = pd.crosstab(clients["offre_bienvenue"], clients["rachat_12m"])
print(croise)
sans, avec = croise.loc[0], croise.loc[1]
p_sans, p_avec = sans[1] / sans.sum(), avec[1] / avec.sum()
cote_sans, cote_avec = sans[1] / sans[0], avec[1] / avec[0]
print()
print(f"sans offre : {p_sans:.4f} ont racheté | cote = {cote_sans:.4f} | logit = {np.log(cote_sans):.4f}")
print(f"avec offre : {p_avec:.4f} ont racheté | cote = {cote_avec:.4f} | logit = {np.log(cote_avec):.4f}")
print(f"rapport de cotes (a*d)/(b*c) = {cote_avec / cote_sans:.4f} | log = {np.log(cote_avec / cote_sans):.4f}")
print(f"différence de risque = {p_avec - p_sans:.4f} | risque relatif = {p_avec / p_sans:.4f}")

m_offre = smf.glm("rachat_12m ~ offre_bienvenue", clients, family=sm.families.Binomial()).fit()
print()
print(m_offre.params.round(4).to_string())
print("exp(coefficient de l'offre) =", round(float(np.exp(m_offre.params["offre_bienvenue"])), 4))
```
<!--sortie-->
```text
rachat_12m         0    1
offre_bienvenue          
0                544  441
1                437  578

sans offre : 0.4477 ont racheté | cote = 0.8107 | logit = -0.2099
avec offre : 0.5695 ont racheté | cote = 1.3227 | logit = 0.2796
rapport de cotes (a*d)/(b*c) = 1.6316 | log = 0.4895
différence de risque = 0.1217 | risque relatif = 1.2719

Intercept         -0.2099
offre_bienvenue    0.4895
exp(coefficient de l'offre) = 1.6316
```

Sans offre, 441 clients sur 985 ont racheté (44,77 %) ; avec l'offre, 578 sur 1 015 (56,95 %). Les cotes correspondantes sont 0,8107 et 1,3227, d'où un rapport de cotes de $1{,}3227/0{,}8107=1{,}6316$, ou encore $(578\times544)/(437\times441)$ : le « produit en croix » du tableau. Le modèle logistique donne `Intercept` $=-0{,}2099$, qui est le logit du groupe sans offre, et `offre_bienvenue` $=0{,}4895$, qui est le logarithme du rapport de cotes ; son exponentielle est $1{,}6316$. L'égalité est **exacte**, pas approchée.

> 📐 **Pourquoi retrouve-t-on exactement le tableau ?** Avec une seule variable binaire, le modèle a **deux** paramètres ($\beta_0,\beta_1$) pour **deux** groupes : il est dit **saturé**. Les équations du score, qui pour le lien canonique s'écrivent simplement $\sum_i(y_i-\hat p_i)\,x_{ij}=0$ (voir 2.2.5), imposent alors que la proportion prédite de chaque groupe égale la proportion observée. Donc $\hat\beta_0=\operatorname{logit}(\hat p_{\text{sans}})$ et $\hat\beta_0+\hat\beta_1=\operatorname{logit}(\hat p_{\text{avec}})$, d'où $\hat\beta_1$ = logarithme du rapport de cotes du tableau.

> ⚠️ **Rapport de cotes $\neq$ risque relatif.** Les clients à qui l'on a envoyé l'offre ont des cotes de rachat multipliées par environ 1,6 ; pourtant la probabilité de rachat n'est « multipliée » que par environ 1,27. Le rapport de cotes **exagère** le risque relatif quand l'événement est fréquent (ici, environ la moitié des clients rachètent). Dire « l'offre rend le rachat 63 % plus probable » serait faux : elle le rend plus probable de **12 points de pourcentage**, ou de 27 % en valeur relative. Quand l'événement est rare (moins de 10 %), l'OR et le RR sont presque identiques ; sinon, il faut les distinguer.

### 2.2.4 Le modèle complet

Ajoutons l'âge et le canal d'acquisition. Avec `statsmodels`, une formule à la R suffit ; la catégorie de référence du canal est la boutique (nous l'avons fixée en tête de liste).

```python
modele = smf.glm("rachat_12m ~ offre_bienvenue + age + canal", clients, family=sm.families.Binomial()).fit()
print(modele.summary().tables[1])
print()
print("log-vraisemblance :", round(modele.llf, 2), "| déviance :", round(modele.deviance, 2), "| AIC :", round(modele.aic, 2), "| n =", int(modele.nobs))
```
<!--sortie-->
```text
======================================================================================
                         coef    std err          z      P>|z|      [0.025      0.975]
--------------------------------------------------------------------------------------
Intercept              0.5885      0.185      3.175      0.001       0.225       0.952
canal[T.Réseaux]    -0.4630      0.116     -4.008      0.000      -0.689      -0.237
canal[T.Site]         -0.1677      0.120     -1.402      0.161      -0.402       0.067
offre_bienvenue        0.4933      0.091      5.423      0.000       0.315       0.672
age                   -0.0155      0.004     -3.562      0.000      -0.024      -0.007
======================================================================================

log-vraisemblance : -1355.42 | déviance : 2710.83 | AIC : 2720.83 | n = 2000
```

Lecture ligne à ligne (les coefficients sont des log-cotes) :

- `offre_bienvenue` : $+0{,}493$ (erreur-type 0,091, $z=5{,}42$) : l'offre augmente nettement la cote de rachat.
- `canal[T.Réseaux]` : $-0{,}463$ ($z=-4{,}01$) : à âge et offre fixés, les clients acquis par Réseaux rachètent moins que ceux de la boutique.
- `canal[T.Site]` : $-0{,}168$ ($p=0{,}161$) : on ne peut pas distinguer le site de la boutique.
- `age` : $-0{,}0155$ par année ($z=-3{,}56$) : les clients plus âgés rachètent un peu moins.
- `Intercept` : $0{,}5885$ est le logit d'un client de la boutique, sans offre, **d'âge 0** : une extrapolation sans signification (on gagnerait à *centrer* l'âge, par exemple en soustrayant 36).

Sous le tableau, trois nombres : la log-vraisemblance $-1\,355{,}42$, la déviance $2\,710{,}83$ et l'AIC $2\,720{,}83$. Remarquez que, pour des données binaires, la déviance est exactement $-2\ell=2\times1\,355{,}42$ (la vraisemblance du modèle saturé vaut 0), et que l'AIC est $-2\ell+2k=2\,710{,}83+2\times5=2\,720{,}83$ avec $k=5$ paramètres. Nous reviendrons sur la déviance à la section 2.4.

Les coefficients sont des **log-cotes**, peu parlants. On les convertit en rapports de cotes, avec leur intervalle de confiance à 95 % (on prend l'exponentielle des bornes de l'intervalle du coefficient).

```python
ic = modele.conf_int()
rapports = pd.DataFrame({"OR": np.exp(modele.params), "IC95 bas": np.exp(ic[0]), "IC95 haut": np.exp(ic[1]), "p-valeur": modele.pvalues})
print(rapports.round(3).to_string())
print()
print("OR pour +10 ans d'âge :", round(float(np.exp(10 * modele.params["age"])), 3))
```
<!--sortie-->
```text
                       OR  IC95 bas  IC95 haut  p-valeur
Intercept           1.801     1.253      2.590     0.001
canal[T.Réseaux]  0.629     0.502      0.789     0.000
canal[T.Site]       0.846     0.669      1.069     0.161
offre_bienvenue     1.638     1.370      1.957     0.000
age                 0.985     0.976      0.993     0.000

OR pour +10 ans d'âge : 0.856
```

Les rapports de cotes se lisent directement :

- **Offre** : OR $=1{,}64$, intervalle à 95 % de 1,37 à 1,96. L'offre multiplie la cote de rachat par un facteur compris, avec 95 % de confiance, entre 1,4 et 2,0.
- **Réseaux** par rapport à la boutique : OR $=0{,}63$ (de 0,50 à 0,79) : la cote de rachat est environ **37 % plus basse**.
- **Site** par rapport à la boutique : OR $=0{,}85$, intervalle de 0,67 à 1,07 : l'intervalle contient 1, aucun effet net n'est démontré.
- **Âge** : OR $=0{,}985$ par année ; pour **dix ans** de plus, $e^{10\hat\beta}=0{,}856$ : la cote est réduite d'environ 14 %.

L'intervalle d'un OR n'est pas symétrique autour de l'OR : c'est l'exponentielle d'un intervalle symétrique pour le log-OR (intervalle de Wald, 2.1.6).

### 2.2.5 L'estimation à la main : IRLS contre `statsmodels`

Reprenons la fonction `irls` écrite à la section 2.1.5, et appliquons-la à ce modèle. Il suffit de construire la matrice $X$ (une colonne de 1, puis les variables ; `patsy` fait ce travail comme `statsmodels`).

```python
from patsy import dmatrices

Y, X = dmatrices("rachat_12m ~ offre_bienvenue + age + canal", clients, return_type="dataframe")
r = irls(X.to_numpy(), Y.to_numpy().ravel(), "binomial")
comparaison = pd.DataFrame({
    "coef (IRLS main)": r["beta"], "coef (statsmodels)": modele.params.to_numpy(),
    "se (IRLS main)": np.sqrt(np.diag(r["cov"])), "se (statsmodels)": modele.bse.to_numpy(),
}, index=X.columns)
print(comparaison.round(6).to_string())
print()
print("itérations de notre IRLS :", r["iterations"], "| écart maximal sur les coefficients :", f"{np.max(np.abs(r['beta'] - modele.params.to_numpy())):.2e}")
print("écart maximal sur les erreurs-types :", f"{np.max(np.abs(np.sqrt(np.diag(r['cov'])) - modele.bse.to_numpy())):.2e}")
```
<!--sortie-->
```text
                    coef (IRLS main)  coef (statsmodels)  se (IRLS main)  se (statsmodels)
Intercept                   0.588499            0.588499        0.185372          0.185372
canal[T.Réseaux]         -0.462955           -0.462955        0.115509          0.115509
canal[T.Site]              -0.167719           -0.167719        0.119619          0.119619
offre_bienvenue             0.493258            0.493258        0.090953          0.090953
age                        -0.015498           -0.015498        0.004351          0.004351

itérations de notre IRLS : 5 | écart maximal sur les coefficients : 3.13e-14
écart maximal sur les erreurs-types : 4.44e-09
```

Les deux méthodes donnent les **mêmes coefficients** (écart maximal de l'ordre de $10^{-14}$) et les **mêmes erreurs-types** (écart maximal de l'ordre de $10^{-9}$), après 5 itérations seulement. Notre petite fonction, écrite à partir de la théorie de la section 2.1, reproduit donc fidèlement ce que fait le logiciel : il n'y a pas de magie derrière `.fit()`. Les erreurs-types viennent de la matrice $(X^\top WX)^{-1}$ calculée au point final.

> 📐 **Une propriété du lien canonique.** Pour la régression logistique, l'équation du score (2.1.5) se simplifie : comme $\frac{\partial\mu_i}{\partial\eta_i}=p_i(1-p_i)=V(p_i)$, on obtient $\sum_i(y_i-\hat p_i)\,x_{ij}=0$ pour chaque colonne $x_j$, y compris la colonne de 1. Deux conséquences : (1) la somme des probabilités prédites est égale au nombre de « oui » observés ; (2) les résidus $y_i-\hat p_i$ sont **orthogonaux** à chaque variable explicative. Vérifions-le.

```python
residus = clients["rachat_12m"] - modele.fittedvalues
print("somme des résidus (y - p̂)                :", round(float(residus.sum()), 8))
print("somme des p̂ =", round(float(modele.fittedvalues.sum()), 3), "| nombre de 1 observés =", int(clients["rachat_12m"].sum()))
for col in ["offre_bienvenue", "age"]:
    print(f"somme des résidus × {col:16s}:", round(float((residus * clients[col]).sum()), 6))
```
<!--sortie-->
```text
somme des résidus (y - p̂)                : 0.0
somme des p̂ = 1019.0 | nombre de 1 observés = 1019
somme des résidus × offre_bienvenue : 0.0
somme des résidus × age             : 0.0
```

Les sommes de résidus sont nulles (à la précision de l'arrondi) et la somme des probabilités prédites, $1\,019$, est **exactement** le nombre de clients qui ont racheté. C'est un excellent réflexe de vérification : si, après un ajustement logistique **avec constante**, ces deux nombres diffèrent, c'est que l'algorithme n'a pas convergé.

### 2.2.6 Probabilités et effets marginaux

Un rapport de cotes dit « de combien la cote est multipliée » ; mais la gérante veut savoir *de combien de points de pourcentage* l'offre augmente la probabilité de rachat. Deux façons de répondre.

**Pour un profil donné.** Prenons un client de 36 ans acquis par Réseaux, avec ou sans l'offre.

```python
profil = pd.DataFrame({"offre_bienvenue": [0, 1], "age": [36, 36],
                       "canal": pd.Categorical(["Réseaux", "Réseaux"], categories=["Boutique", "Réseaux", "Site"])})
p_profil = modele.predict(profil)
b = modele.params
a_la_main = expit(b["Intercept"] + b["canal[T.Réseaux]"] + 36 * b["age"] + b["offre_bienvenue"] * np.array([0, 1]))
print("probabilités prédites (sans offre, avec offre) :", p_profil.round(4).to_numpy(), "| à la main :", a_la_main.round(4))
print("gain en points de pourcentage pour ce profil   :", round(100 * float(p_profil.iloc[1] - p_profil.iloc[0]), 2))
```
<!--sortie-->
```text
probabilités prédites (sans offre, avec offre) : [0.3936 0.5152] | à la main : [0.3936 0.5152]
gain en points de pourcentage pour ce profil   : 12.17
```

**En moyenne sur tous les clients** (effet marginal moyen). On calcule, pour *chaque* client, sa probabilité prédite en lui attribuant l'offre, puis sans l'offre, et l'on moyenne la différence. Comme l'offre a été **attribuée au hasard**, cette quantité estime directement l'effet causal moyen de l'offre sur la probabilité de rachat.

```python
avec_offre = clients.assign(offre_bienvenue=1)
sans_offre = clients.assign(offre_bienvenue=0)
effet_moyen = (modele.predict(avec_offre) - modele.predict(sans_offre)).mean()
print(f"effet marginal moyen de l'offre (modèle) : {100 * effet_moyen:.2f} points")
print(f"différence brute des taux de rachat      : {100 * (p_avec - p_sans):.2f} points")

# effet marginal moyen de l'âge : +1 an
effet_age = (modele.predict(clients.assign(age=clients["age"] + 1)) - modele.predict(clients)).mean()
print(f"effet marginal moyen d'un an de plus     : {100 * effet_age:.3f} point  (soit {100 * 10 * effet_age:.2f} points pour 10 ans)")

# contrôle avec la fonction de statsmodels (modèle Logit)
logit = smf.logit("rachat_12m ~ offre_bienvenue + age + canal", clients).fit(disp=0)
print()
print(logit.get_margeff(at="overall", dummy=True).summary_frame().round(4).to_string())
```
<!--sortie-->
```text
effet marginal moyen de l'offre (modèle) : 12.07 points
différence brute des taux de rachat      : 12.17 points
effet marginal moyen d'un an de plus     : -0.376 point  (soit -3.76 points pour 10 ans)

                     dy/dx  Std. Err.       z  Pr(>|z|)  Conf. Int. Low  Cont. Int. Hi.
canal[T.Réseaux] -0.1126     0.0277 -4.0625    0.0000         -0.1669         -0.0583
canal[T.Site]      -0.0405     0.0287 -1.4108    0.1583         -0.0967          0.0158
offre_bienvenue     0.1207     0.0220  5.4768    0.0000          0.0775          0.1640
age                -0.0038     0.0010 -3.6063    0.0003         -0.0058         -0.0017
```

Pour ce profil (Réseaux, 36 ans), l'offre fait passer la probabilité de rachat de 39,4 % à 51,5 %, soit un gain de **12,2 points** (le calcul à la main coïncide avec `predict`). En moyenne sur les 2 000 clients, l'effet marginal de l'offre est de **12,07 points**, très proche de la différence brute des taux (12,17 points) : c'est normal puisque l'offre a été tirée au sort. La fonction `get_margeff` de `statsmodels` donne le même chiffre (0,1207) avec un intervalle de confiance de **7,8 à 16,4 points**. Pour l'âge, un an de plus réduit la probabilité de rachat d'environ **0,38 point** en moyenne (0,0038 dans le tableau de `statsmodels`), soit environ 3,8 points pour dix ans. Notez que ces effets, exprimés en points, sont **moyens** : ils varient d'un client à l'autre (2.2.2).

> 💡 **Pourquoi la différence brute et l'effet du modèle sont proches.** Quand le traitement est attribué au hasard, il est (en moyenne) indépendant de l'âge et du canal : ajuster pour ces variables précise l'estimation, mais ne la déplace pas beaucoup. Dans une étude **observationnelle** (où les clients choisissent), les deux chiffres pourraient être très différents ; c'est le sujet du chapitre 7 (inférence causale).

### 2.2.7 Utiliser plus d'information : les notes de l'enquête

Nous avons, pour environ 60 % des clients, deux notes issues du questionnaire de satisfaction : `note_produits` (moyenne des questions 1 à 4) et `note_service` (questions 5 à 8). Ajoutons-les au modèle, **sur les répondants seulement** (les clients qui n'ont pas répondu n'ont pas de notes).

```python
enquete = pd.read_csv("donnees/enquete_satisfaction.csv")
enquete["note_produits"] = enquete[["q1", "q2", "q3", "q4"]].mean(axis=1)
enquete["note_service"] = enquete[["q5", "q6", "q7", "q8"]].mean(axis=1)
repondants = clients.merge(enquete[["id_client", "note_produits", "note_service"]], on="id_client")

m_base = smf.glm("rachat_12m ~ offre_bienvenue + age + canal", repondants, family=sm.families.Binomial()).fit()
m_riche = smf.glm("rachat_12m ~ offre_bienvenue + age + canal + note_produits + note_service", repondants,
                  family=sm.families.Binomial()).fit()
ic = m_riche.conf_int()
print(pd.DataFrame({"coef": m_riche.params, "OR": np.exp(m_riche.params), "IC95 bas": np.exp(ic[0]), "IC95 haut": np.exp(ic[1]),
                    "p": m_riche.pvalues}).round(3).to_string())
print()
print("répondants :", int(m_riche.nobs), "| AIC modèle de base :", round(m_base.aic, 1), "| AIC modèle avec notes :", round(m_riche.aic, 1))
print("écart-types des notes :", repondants[["note_produits", "note_service"]].std().round(2).to_dict())
print("OR de l'offre, sur ces mêmes répondants : sans les notes =", round(float(np.exp(m_base.params["offre_bienvenue"])), 3), "| avec les notes =", round(float(np.exp(m_riche.params["offre_bienvenue"])), 3))
```
<!--sortie-->
```text
                     coef     OR  IC95 bas  IC95 haut      p
Intercept          -3.626  0.027     0.010      0.069  0.000
canal[T.Réseaux] -0.474  0.622     0.458      0.845  0.002
canal[T.Site]      -0.244  0.783     0.570      1.075  0.131
offre_bienvenue     0.607  1.834     1.442      2.334  0.000
age                -0.018  0.983     0.971      0.994  0.003
note_produits       0.764  2.148     1.781      2.589  0.000
note_service        0.420  1.522     1.285      1.803  0.000

répondants : 1212 | AIC modèle de base : 1652.3 | AIC modèle avec notes : 1545.2
écart-types des notes : {'note_produits': 0.69, 'note_service': 0.73}
OR de l'offre, sur ces mêmes répondants : sans les notes = 1.749 | avec les notes = 1.834
```

Sur les 1 212 répondants, les deux notes sont fortement associées au rachat : un point de plus sur la **note « produits »** multiplie la cote par **2,15** (de 1,78 à 2,59), un point de plus sur la **note « service »** par **1,52** (de 1,29 à 1,80). Comme les notes n'ont pas la même dispersion (écarts-types 0,69 et 0,73), comparons à écart-type égal : $e^{0{,}764\times0{,}69}\approx1{,}69$ pour les produits, $e^{0{,}420\times0{,}73}\approx1{,}36$ pour le service. Les deux comptent, avec un avantage à la qualité des produits. L'AIC chute de 1 652,3 à 1 545,2 : le gain est considérable (plus de 100 points).

Un détail instructif : l'OR de l'offre passe de **1,749** (sans les notes) à **1,834** (avec les notes), alors que l'offre est tirée au hasard et n'est donc pas corrélée aux notes : aucun biais de confusion ne peut expliquer ce changement. C'est un phénomène classique, la **non-collapsibilité** du rapport de cotes : quand on ajoute au modèle une variable qui prédit bien le résultat, l'OR de la variable de traitement change, même sans confusion, parce que l'on passe d'un OR *moyenné sur la population* à un OR *conditionnel aux notes*. Ce n'est pas le cas des différences de probabilités ou des coefficients d'une régression linéaire. Une raison de plus de préférer les effets marginaux en points de pourcentage pour communiquer.

### 2.2.8 Évaluer un modèle de classement : matrice de confusion, ROC, AUC, calibration

Un modèle logistique rend une **probabilité**. On peut s'en servir de deux façons : (a) comme **score** pour classer les clients (qui relancer en priorité ?), (b) comme **règle de décision** : on prédit « rachète » si $\hat p$ dépasse un seuil. Les deux se jugent différemment.

**Matrice de confusion.** À un seuil donné, on compare la prédiction (0/1) au résultat réel.

```python
y = repondants["rachat_12m"].to_numpy()
score = m_riche.fittedvalues.to_numpy()

def matrice(y, score, seuil):
    pred = (score >= seuil).astype(int)
    vp, fp = int(((pred == 1) & (y == 1)).sum()), int(((pred == 1) & (y == 0)).sum())
    fn, vn = int(((pred == 0) & (y == 1)).sum()), int(((pred == 0) & (y == 0)).sum())
    return vp, fp, fn, vn

for seuil in (0.5, 0.4, 0.6):
    vp, fp, fn, vn = matrice(y, score, seuil)
    print(f"seuil {seuil} : VP={vp} FP={fp} FN={fn} VN={vn} | exactitude={(vp + vn) / len(y):.3f} | "
          f"sensibilité={vp / (vp + fn):.3f} | spécificité={vn / (vn + fp):.3f} | précision={vp / (vp + fp):.3f}")
```
<!--sortie-->
```text
seuil 0.5 : VP=406 FP=228 FN=206 VN=372 | exactitude=0.642 | sensibilité=0.663 | spécificité=0.620 | précision=0.640
seuil 0.4 : VP=512 FP=353 FN=100 VN=247 | exactitude=0.626 | sensibilité=0.837 | spécificité=0.412 | précision=0.592
seuil 0.6 : VP=270 FP=112 FN=342 VN=488 | exactitude=0.625 | sensibilité=0.441 | spécificité=0.813 | précision=0.707
```

Parmi les 1 212 répondants, 612 ont racheté (50,5 %) : un modèle qui répondrait toujours « oui » aurait une exactitude de 50,5 %. Au seuil de 0,5, la matrice donne 406 vrais positifs, 228 faux positifs, 206 faux négatifs et 372 vrais négatifs : exactitude 64,2 %, sensibilité 66,3 % (parmi ceux qui rachètent, 66 % sont repérés), spécificité 62,0 %. En **baissant le seuil à 0,4**, on repère davantage de rachats (sensibilité 83,7 %) au prix de davantage de fausses alertes (spécificité 41,2 %) ; en **montant à 0,6**, l'inverse (sensibilité 44,1 %, spécificité 81,3 %, mais précision de 70,7 %). L'exactitude, elle, reste presque la même (entre 62,5 % et 64,2 %) : c'est un résumé qui **cache** le compromis. Le bon seuil dépend du coût de chaque type d'erreur.

**Courbe ROC et AUC.** Plutôt que de choisir un seuil, on regarde **tous** les seuils à la fois : la courbe ROC trace la sensibilité (taux de vrais positifs) en fonction de $1-{}$spécificité (taux de faux positifs). L'**AUC** (*area under the curve*) est l'aire sous cette courbe. Elle a une interprétation très parlante : c'est la **probabilité qu'un client pris au hasard parmi ceux qui ont racheté ait un score plus élevé qu'un client pris au hasard parmi ceux qui n'ont pas racheté** (avec une demi-part pour les ex æquo). Vérifions-le en calculant l'AUC de trois façons.

```python
from sklearn.metrics import roc_auc_score

def auc_paires(y, s):
    pos, neg = s[y == 1], s[y == 0]
    return (pos[:, None] > neg[None, :]).mean() + 0.5 * (pos[:, None] == neg[None, :]).mean()

# courbe ROC « à la main » : on trie les clients par score décroissant et on cumule
ordre = np.argsort(-score)
y_trie = y[ordre]
tpr = np.concatenate([[0], np.cumsum(y_trie) / y.sum()])
fpr = np.concatenate([[0], np.cumsum(1 - y_trie) / (1 - y).sum()])
auc_trapezes = np.trapezoid(tpr, fpr)

print("AUC par comparaison de paires :", round(float(auc_paires(y, score)), 4))
print("AUC par aire sous la courbe   :", round(float(auc_trapezes), 4))
print("AUC de scikit-learn           :", round(float(roc_auc_score(y, score)), 4))
print("AUC du modèle de base (sans les notes) :", round(float(roc_auc_score(y, m_base.fittedvalues)), 4))
```
<!--sortie-->
```text
AUC par comparaison de paires : 0.6975
AUC par aire sous la courbe   : 0.6975
AUC de scikit-learn           : 0.6975
AUC du modèle de base (sans les notes) : 0.599
```

Les trois calculs donnent la **même valeur**, 0,6975 : l'aire sous la courbe ROC est bien la probabilité qu'un client qui a racheté ait un score supérieur à celui d'un client qui n'a pas racheté. Un modèle sans pouvoir de classement aurait une AUC de 0,5 ; un modèle parfait, 1. Le modèle sans les notes de l'enquête n'atteint que **0,599** : les notes font passer l'AUC de 0,60 à 0,70, un gain sensible. Les deux valeurs restent modestes : prédire un comportement individuel est difficile (et notre jeu simulé contient réellement beaucoup de hasard).

**Calibration.** Un bon classement ne suffit pas toujours : si l'on veut utiliser $\hat p$ comme une **vraie probabilité** (par exemple pour calculer un gain espéré), il faut qu'elle soit *calibrée* : parmi les clients à qui le modèle donne 70 %, environ 70 % doivent avoir racheté. On le vérifie en regroupant les clients par dixièmes de score.

```python
dec = pd.qcut(score, 10, labels=False)
calib = pd.DataFrame({"p prédite": score, "observé": y, "dixième": dec}).groupby("dixième").agg(
    p_predite=("p prédite", "mean"), observe=("observé", "mean"), n=("observé", "size"))
print(calib.round(3).to_string())

fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))
BLEU, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
ax = axes[0]
ordre_b = np.argsort(-m_base.fittedvalues.to_numpy())
yb = y[ordre_b]
tpr_b = np.concatenate([[0], np.cumsum(yb) / y.sum()]); fpr_b = np.concatenate([[0], np.cumsum(1 - yb) / (1 - y).sum()])
ax.plot(fpr, tpr, color=BLEU, lw=2); ax.plot(fpr_b, tpr_b, color=ORANGE, lw=2); ax.plot([0, 1], [0, 1], color="#898781", ls=":")
ax.text(0.45, 0.30, f"avec les notes : AUC = {roc_auc_score(y, score):.2f}", color=BLEU, fontsize=9)
ax.text(0.45, 0.22, f"sans les notes : AUC = {roc_auc_score(y, m_base.fittedvalues):.2f}", color=ORANGE, fontsize=9)
ax.text(0.45, 0.14, "hasard : AUC = 0,50", color="#898781", fontsize=9)
ax.set_xlabel("taux de faux positifs (1 - spécificité)"); ax.set_ylabel("taux de vrais positifs (sensibilité)"); ax.set_title("Courbe ROC")
ax = axes[1]
ax.plot([0, 1], [0, 1], color="#898781", ls=":")
ax.plot(calib["p_predite"], calib["observe"], "o-", color=AQUA, lw=1.8)
ax.set_xlabel("probabilité prédite (moyenne par dixième)"); ax.set_ylabel("fréquence observée de rachat"); ax.set_title("Calibration")
plt.tight_layout()
plt.savefig("figures/ch02-roc-calibration.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
         p_predite  observe    n
dixième                         
0            0.212    0.287  122
1            0.308    0.207  121
2            0.377    0.397  121
3            0.433    0.421  121
4            0.485    0.537  121
5            0.537    0.479  121
6            0.582    0.595  121
7            0.635    0.628  121
8            0.698    0.661  121
9            0.783    0.836  122
figure enregistrée
```

![À gauche : courbes ROC du modèle de rachat avec et sans les notes de l'enquête. À droite : courbe de calibration, la diagonale pointillée représente un modèle parfaitement calibré.](figures/ch02-roc-calibration.png)

À gauche, la courbe bleue (avec les notes) est partout au-dessus de la courbe orange (sans les notes) : à taux de fausses alertes égal, elle repère davantage de rachats. À droite, les points suivent globalement la diagonale : le modèle est **assez bien calibré**. Quelques écarts sont visibles (deuxième dixième : 30,8 % prédits, 20,7 % observés), mais avec environ 121 clients par dixième, l'erreur-type d'une proportion observée est d'au plus $\sqrt{0{,}25/121}\approx4{,}5$ points : un écart de 10 points (environ deux erreurs-types) sur dix classes n'a rien d'alarmant. Nous verrons au 2.4.4 un test formel (Hosmer-Lemeshow).

> ⚠️ **Évaluer sur les données qui ont servi à ajuster est optimiste.** Le modèle a vu les réponses qu'on lui demande de « prédire ». Pour une estimation honnête, on sépare les données : on ajuste sur une partie (apprentissage) et l'on évalue sur l'autre (test). C'est le sujet central du volume III ; voici un avant-goût.

```python
rng = np.random.default_rng(5)
idx = rng.permutation(len(repondants))
n_app = int(0.7 * len(repondants))
app, test = repondants.iloc[idx[:n_app]], repondants.iloc[idx[n_app:]]
m_app = smf.glm("rachat_12m ~ offre_bienvenue + age + canal + note_produits + note_service", app, family=sm.families.Binomial()).fit()
print("AUC en apprentissage :", round(float(roc_auc_score(app["rachat_12m"], m_app.fittedvalues)), 4), "(", len(app), "clients )")
print("AUC en test          :", round(float(roc_auc_score(test["rachat_12m"], m_app.predict(test))), 4), "(", len(test), "clients )")
```
<!--sortie-->
```text
AUC en apprentissage : 0.6841 ( 848 clients )
AUC en test          : 0.7193 ( 364 clients )
```

L'AUC en test (0,719) est *supérieure* à celle d'apprentissage (0,684) : ce n'est pas une anomalie. Avec 364 clients en test (environ 180 par classe), l'incertitude sur une AUC est de l'ordre de $\sqrt{0{,}7\times0{,}3/180}\approx0{,}03$ : un seul découpage aléatoire ne permet de conclure ni à du sur-apprentissage ni à son absence. En moyenne, l'AUC en test est plutôt un peu inférieure à celle en apprentissage, et pour une estimation fiable on **répète** le découpage (validation croisée, volume III). Retenez le principe : **on n'évalue pas un modèle sur les données qui l'ont ajusté**.

### 2.2.9 Pièges de la régression logistique

**La séparation parfaite.** Si une combinaison des variables sépare **parfaitement** les 0 des 1, la vraisemblance n'a pas de maximum : elle augmente sans fin quand les coefficients grossissent. Un exemple minuscule : six clients, trois qui n'ont pas racheté avec 1, 2 et 3 achats préalables, trois qui ont racheté avec 4, 5 et 6.

```python
import warnings
x_sep = np.array([1.0, 2, 3, 4, 5, 6])
y_sep = np.array([0, 0, 0, 1, 1, 1])
with warnings.catch_warnings(record=True) as avertissements:
    warnings.simplefilter("always")
    try:
        res = sm.GLM(y_sep, sm.add_constant(x_sep), family=sm.families.Binomial()).fit()
        print("pente estimée :", round(float(res.params[1]), 1), "| erreur-type de la pente :", round(float(res.bse[1]), 1))
        print("probabilités prédites (arrondies) :", res.fittedvalues.round(3).tolist())
    except Exception as e:
        print(type(e).__name__, ":", e)
    for message in sorted({str(a.message) for a in avertissements}):
        print("AVERTISSEMENT :", message)
```
<!--sortie-->
```text
pente estimée : 41.2 | erreur-type de la pente : 25719.8
probabilités prédites (arrondies) : [0.0, 0.0, 0.0, 1.0, 1.0, 1.0]
AVERTISSEMENT : Perfect separation or prediction detected, parameter may not be identified
```

`statsmodels` n'a pas planté, mais il a **averti** : les probabilités prédites sont arrondies à 0,0 et 1,0 (le modèle classe parfaitement), et la pente estimée (41,2) n'a pas de sens : son erreur-type est de plusieurs dizaines de milliers. L'algorithme ne s'est pas arrêté parce qu'il a trouvé un maximum, mais parce que la vraisemblance est devenue quasi plate : la « vraie » solution est infinie, et les valeurs affichées dépendent des détails de l'algorithme. **Ne faites jamais confiance à un coefficient accompagné de cet avertissement.** Les remèdes classiques sont de regrouper ou retirer la variable en cause, d'ajouter une pénalité (régularisation, section 1.5) ou d'utiliser la régression logistique de Firth (par exemple le paquet R `logistf`).

**Autres pièges.** (1) **Choisir le seuil à 0,5 par réflexe** : le bon seuil dépend des coûts relatifs d'un faux positif et d'un faux négatif (envoyer une relance inutile coûte peu, rater un client précieux coûte beaucoup). (2) **Les événements rares** : avec 1 % de « oui », une exactitude de 99 % est obtenue en répondant toujours « non » ; il faut regarder la sensibilité, la précision, l'AUC. (3) **Interpréter un OR comme un risque relatif** (2.2.3). (4) **Oublier la forme fonctionnelle** : le modèle suppose que l'effet de chaque variable est **linéaire sur le logit** ; si l'effet est en cloche (section 2.5), la logistique « simple » passe à côté.

> ✅ **À retenir**
> - Le modèle logistique pose $\operatorname{logit}(p)=x^\top\beta$ : les coefficients sont des **log-cotes**, $e^{\beta_j}$ est un **rapport de cotes**.
> - Le rapport de cotes n'est pas un risque relatif : il le surestime quand l'événement est fréquent. Pour parler en points de pourcentage, calculez des **probabilités prédites** et des **effets marginaux moyens**.
> - Avec un traitement tiré au hasard, l'effet marginal moyen de la variable de traitement estime son effet causal moyen.
> - L'estimation se fait par IRLS ; avec le lien canonique, $\sum_i(y_i-\hat p_i)x_{ij}=0$ : les probabilités prédites ont la bonne moyenne.
> - Un modèle se juge sur le **classement** (AUC, sensibilité/spécificité à un seuil) **et** sur la **calibration**, de préférence sur des données **non utilisées** pour l'ajustement.
> - Attention à la séparation parfaite, au choix du seuil, aux événements rares.
