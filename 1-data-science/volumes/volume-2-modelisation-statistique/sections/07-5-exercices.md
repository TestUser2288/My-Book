## 7.5 Exercices corrigés

> 🧭 **Comment s'y prendre.** Faites d'abord l'exercice **à la main**, puis vérifiez avec le code. Les exercices sont notés ⭐ (application directe), ⭐⭐ (il faut combiner deux idées) et ⭐⭐⭐ (démonstration ou analyse critique). Les corrigés suivent tous les énoncés.

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats

clients = pd.read_csv("donnees/clients.csv")
panel = pd.read_csv("donnees/ch07-panel-villes.csv")
panel["vid"] = pd.factorize(panel["ville"])[0]
print(clients.shape, panel.shape)
```
<!--sortie-->
```text
(2000, 12) (480, 7)
```

### Énoncés

**Exercice 1 ⭐ (résultats potentiels).** Six clients ont les dépenses potentielles suivantes (en €) : Aya ($Y(0)=60$, $Y(1)=75$), Bilel (40, 50), Cyrine (100, 105), Dali (80, 100), Emna (30, 40), Firas (90, 95). Les trois premiers ont reçu l'offre, les trois derniers non. (a) Calculez à la main l'ATE, l'ATT et l'ATU. (b) Quelle est la différence naïve des moyennes observées ? (c) Décomposez-la en ATT plus biais de sélection.

**Exercice 2 ⭐ (sous-groupes).** Dans l'expérience de `clients.csv`, calculez l'effet de l'offre sur le rachat (`rachat_12m`) **dans chaque canal d'acquisition**, avec intervalle de confiance à 95 %. La gérante remarque : « l'offre marche presque cinq fois mieux sur Réseaux que sur le site ». (a) Testez cette différence. (b) Que devez-vous répondre à la gérante ?

**Exercice 3 ⭐ (Simpson).** Une campagne d'e-mails a été envoyée à des clients en ville (1 000 clients dont 600 destinataires) et à la campagne (1 000 clients dont 200 destinataires). En ville, le rachat vaut 50 % chez les destinataires et 40 % chez les autres ; à la campagne, 30 % chez les destinataires et 20 % chez les autres. (a) Calculez le rachat global chez les destinataires et chez les non-destinataires. (b) Que dit la différence globale ? Que dit la différence par zone ? (c) Laquelle croire si la zone est une cause commune de la décision d'envoi et du rachat ? Et si la zone était une conséquence de l'e-mail ?

**Exercice 4 ⭐⭐ (choisir l'ensemble d'ajustement).** On simule : un facteur de confusion $C$ ; un traitement $T$ qui en dépend ; un médiateur $M$ affecté par $T$ ; un résultat $Y=5T+3M+4C+\varepsilon$ ; et un effet commun $K=T+Y+\varepsilon'$. (a) Quel est l'effet **total** de $T$ sur $Y$ ? (b) Estimez l'effet par régression avec quatre ensembles d'ajustement : $\varnothing$, $\{C\}$, $\{C,M\}$, $\{C,K\}$. (c) Lequel est correct, et que mesurent les autres ?

**Exercice 5 ⭐⭐ (stratification sur le score).** Les clients ont été classés en trois strates de score de propension. Strate A : 400 clients, probabilité d'offre 0,2, dépense moyenne 130 (avec offre) et 100 (sans). Strate B : 400 clients, probabilité 0,5, moyennes 150 et 115. Strate C : 200 clients, probabilité 0,8, moyennes 190 et 150. (a) Calculez la différence naïve. (b) Calculez l'ATE en pondérant les effets par strate. (c) Retrouvez-le par IPW.

**Exercice 6 ⭐⭐ (chevauchement).** Reprenez l'étude observationnelle de 7.2 (`ch07-observationnel.csv`). (a) Restreignez l'analyse aux clients dont le score de propension est compris entre 0,1 et 0,9 : combien en reste-t-il ? (b) Réestimez l'ATE par IPW sur cet échantillon, et comparez avec l'estimation sur tous les clients. (c) Quelle quantité estime-t-on désormais ?

**Exercice 7 ⭐⭐ (DiD à la main).** Chiffre d'affaires moyen par ville (en milliers de €) : villes traitées 120 avant, 150 après ; villes témoins 80 avant, 92 après. (a) Calculez la DiD en niveau. (b) Calculez-la en logarithme et interprétez en pourcentage. (c) Laquelle des deux hypothèses de tendances parallèles est la plus plausible si le chiffre d'affaires évolue en pourcentage ?

**Exercice 8 ⭐⭐ (inférence avec peu de groupes).** Dans le panel, ne gardez que les 12 villes témoins, et attribuez **au hasard** à 4 d'entre elles une « fausse campagne » à partir de `t = 18` : il n'y a **aucun effet** à trouver. Répétez 300 fois (graine 81) et comptez à quelle fréquence la DiD avec erreurs-types groupées paraît « significative » à 5 %. (a) Avec le seuil normal $|t|>1{,}96$. (b) Avec le seuil de Student à 11 degrés de liberté. (c) Que concluez-vous ?

**Exercice 9 ⭐⭐ (instrument à la main).** Dans une étude, on observe : avec l'instrument ($Z=1$), 60 % des clients suivent le compte et la dépense moyenne est de 52 € ; sans ($Z=0$), 30 % le suivent et la dépense moyenne est de 46 €. (a) Calculez l'estimateur de Wald. (b) Quelle proportion de complaisants peut-on au mieux estimer ? (c) Si l'instrument avait en réalité un effet direct de 1,5 € sur la dépense, de combien l'estimation serait-elle faussée ?

**Exercice 10 ⭐⭐⭐ (démonstration).** Soit $Z$ binaire de probabilité $q=\mathbb P(Z=1)$. (a) Montrez que $\operatorname{Cov}(Z,Y)=q(1-q)\big(\mathbb E[Y\mid Z=1]-\mathbb E[Y\mid Z=0]\big)$. (b) Déduisez que $\operatorname{Cov}(Z,Y)/\operatorname{Cov}(Z,T)$ est égal au rapport de Wald. (c) Vérifiez-le numériquement sur `ch07-iv.csv`.

**Exercice 11 ⭐⭐⭐ (médiation).** Reprenez la simulation de 7.1.7 (offre randomisée ; médiateur « code utilisé » ; motivation qui influence à la fois l'utilisation du code et la dépense). Cette fois, **supposez la motivation observée**. (a) Estimez l'effet direct de l'offre en ajustant sur le code **et** la motivation. (b) Déduisez l'effet indirect (par le code), et comparez avec la valeur vraie $30\times\mathbb P(\text{code}\mid\text{offre})$. (c) Pourquoi l'ajustement sur le médiateur marche-t-il ici et pas en 7.1.7 ?

**Exercice 12 ⭐⭐⭐ (critique d'une étude).** Une collègue veut estimer l'effet de « venir en boutique » (traitement) sur la dépense annuelle (résultat). Elle propose comme instrument la **distance** entre le domicile du client et la boutique. Discutez chacune des trois conditions d'un instrument, proposez une vérification ou un ajustement pour chacune, et dites ce que l'on estimerait si l'instrument était valide.

---

### Corrigés

**Corrigé 1.** (a) Effets individuels : Aya $+15$, Bilel $+10$, Cyrine $+5$, Dali $+20$, Emna $+10$, Firas $+5$. ATT $=(15+10+5)/3=10$ ; ATU $=(20+10+5)/3=11{,}67$ ; ATE $=65/6=10{,}83$. (b) Observé : traités (les $Y(1)$ des trois premiers) $75,50,105$, moyenne $76{,}67$ ; non traités (les $Y(0)$ des trois derniers) $80,30,90$, moyenne $66{,}67$ ; différence naïve $=10$. (c) $\mathbb E[Y(0)\mid T=1]=(60+40+100)/3=66{,}67$ et $\mathbb E[Y(0)\mid T=0]=66{,}67$ : le biais de sélection est **nul** (par hasard dans ce petit exemple), donc la différence naïve égale l'ATT (10). Vérifions :

```python
ex1 = pd.DataFrame({"client": ["Aya", "Bilel", "Cyrine", "Dali", "Emna", "Firas"],
                    "y0": [60, 40, 100, 80, 30, 90], "y1": [75, 50, 105, 100, 40, 95], "offre": [1, 1, 1, 0, 0, 0]})
ex1["effet"] = ex1["y1"] - ex1["y0"]
obs = np.where(ex1.offre == 1, ex1.y1, ex1.y0)
print(f"ATE = {ex1.effet.mean():.2f}  ATT = {ex1.effet[ex1.offre == 1].mean():.2f}  ATU = {ex1.effet[ex1.offre == 0].mean():.2f}")
print(f"différence naïve = {obs[ex1.offre == 1].mean() - obs[ex1.offre == 0].mean():.2f}")
print(f"biais de sélection = {ex1.y0[ex1.offre == 1].mean() - ex1.y0[ex1.offre == 0].mean():.2f}")
```
<!--sortie-->
```text
ATE = 10.83  ATT = 10.00  ATU = 11.67
différence naïve = 10.00
biais de sélection = 0.00
```

Moralité : un biais de sélection **nul** n'est pas impossible, mais on ne peut jamais le savoir sans connaître les $Y(0)$ des traités ; la différence naïve n'est donc fiable que si l'on a une raison de croire que la sélection est ignorable.

**Corrigé 2.** (a) Dans chaque canal, la différence de proportions et son intervalle de Wald :

```python
lignes = []
for canal, g in clients.groupby("canal_acquisition"):
    t, u = g[g.offre_bienvenue == 1]["rachat_12m"], g[g.offre_bienvenue == 0]["rachat_12m"]
    diff = t.mean() - u.mean()
    se = np.sqrt(t.var() / len(t) + u.var() / len(u))
    lignes.append({"canal": canal, "clients": len(g), "effet": diff, "IC95 bas": diff - 1.96 * se, "IC95 haut": diff + 1.96 * se})
print(pd.DataFrame(lignes).round(3).to_string(index=False))

complet = smf.logit("rachat_12m ~ offre_bienvenue * C(canal_acquisition)", clients).fit(disp=0)
reduit = smf.logit("rachat_12m ~ offre_bienvenue + C(canal_acquisition)", clients).fit(disp=0)
lr = 2 * (complet.llf - reduit.llf)
print(f"\ntest de l'interaction offre x canal (rapport de vraisemblance, 2 ddl) : p = {stats.chi2.sf(lr, 2):.4f}")
```
<!--sortie-->
```text
    canal  clients  effet  IC95 bas  IC95 haut
 Boutique      504  0.116     0.029      0.202
Réseaux      816  0.196     0.129      0.263
     Site      680  0.042    -0.033      0.117

test de l'interaction offre x canal (rapport de vraisemblance, 2 ddl) : p = 0.0105
```

L'effet est de $+19{,}6$ points sur Réseaux contre $+4{,}2$ sur le site, avec des intervalles larges ; le test d'interaction (rapport de vraisemblance, chapitre 2) donne $p\approx0{,}01$. (b) Que répondre ? **Prudence.** Cette analyse par sous-groupe est *exploratoire* : si la gérante avait regardé cinq découpages différents (canal, ville, âge, année d'inscription…), le seuil de Bonferroni serait $0{,}05/5=0{,}01$, que $p=0{,}0105$ ne franchit pas (volume I, section 3.5.5). Et l'expérience n'était **pas dimensionnée** pour détecter des différences entre sous-groupes (chaque canal n'a que quelques centaines de clients par bras). **Vérité révélée** : dans le simulateur, l'effet de l'offre est **le même** dans les trois canaux (12,3 à 12,4 points, comme on peut le vérifier par la même intégration qu'en 7.1.4) ; l'écart observé n'est qu'une fluctuation d'échantillonnage, de celles qui arrivent environ une fois sur cent. La bonne réponse : « c'est une piste, pas une conclusion ; on peut la **confirmer** par une nouvelle expérience prévue pour cela ».

**Corrigé 3.** (a) Destinataires : $600\times0{,}5+200\times0{,}3=300+60=360$ rachats sur $800$, soit $45\,\%$. Non-destinataires : $400\times0{,}4+800\times0{,}2=160+160=320$ rachats sur $1200$, soit $26{,}7\,\%$. (b) Globalement l'e-mail est associé à **+18,3 points** ; par zone, à **+10 points** dans chaque zone. L'écart global **surestime** l'effet, car les destinataires sont surtout des citadins, qui rachètent davantage de toute façon (ici le sens est l'inverse du paradoxe de 7.1.6, mais le mécanisme est le même). (c) Si la zone est une cause commune de l'envoi et du rachat, il faut **ajuster** : l'effet standardisé est $0{,}5\times10+0{,}5\times10=10$ points. Si la zone était une **conséquence** de l'e-mail (l'e-mail pousserait les clients à déménager en ville !), ajuster sur elle serait une erreur : la différence globale deviendrait l'effet total.

```python
ex3 = pd.DataFrame({"zone": ["ville", "ville", "campagne", "campagne"], "mail": [1, 0, 1, 0],
                    "n": [600, 400, 200, 800], "taux": [0.5, 0.4, 0.3, 0.2]})
ex3["rachats"] = ex3["n"] * ex3["taux"]
glob = ex3.groupby("mail")[["n", "rachats"]].sum()
print("taux global :", (glob.rachats / glob.n).round(3).to_dict())
par_zone = ex3.pivot(index="zone", columns="mail", values="taux")
poids = ex3.groupby("zone")["n"].sum() / ex3["n"].sum()
print("effet par zone :", (par_zone[1] - par_zone[0]).round(2).to_dict(), "| poids :", poids.round(2).to_dict())
print("effet standardisé :", round(((par_zone[1] - par_zone[0]) * poids).sum(), 3))
```
<!--sortie-->
```text
taux global : {0: 0.267, 1: 0.45}
effet par zone : {'campagne': 0.1, 'ville': 0.1} | poids : {'campagne': 0.5, 'ville': 0.5}
effet standardisé : 0.1
```

**Corrigé 4.** (a) $T$ agit directement (5) et par $M$ (qui vaut $2T$ en moyenne, et pèse 3 dans $Y$) : effet total $=5+3\times2=11$. (b) et (c) :

```python
rng = np.random.default_rng(401)
n = 50_000
conf = rng.normal(size=n)                                      # facteur de confusion (nommé « conf » pour ne pas masquer C() de patsy)
T = (conf + rng.normal(size=n) > 0).astype(int)
M = 2 * T + rng.normal(size=n)
Y = 5 * T + 3 * M + 4 * conf + rng.normal(size=n)
K = T + Y + rng.normal(size=n)
df4 = pd.DataFrame({"Y": Y, "T": T, "M": M, "conf": conf, "K": K})
for nom, f in [("∅", "Y ~ T"), ("{C}", "Y ~ T + conf"), ("{C, M}", "Y ~ T + conf + M"), ("{C, K}", "Y ~ T + conf + K")]:
    print(f"ensemble {nom:7s} : effet estimé de T = {smf.ols(f, df4).fit().params['T']:.2f}")
```
<!--sortie-->
```text
ensemble ∅       : effet estimé de T = 15.50
ensemble {C}     : effet estimé de T = 11.00
ensemble {C, M}  : effet estimé de T = 5.01
ensemble {C, K}  : effet estimé de T = 0.08
```

Seul $\{C\}$ donne l'effet **total** (11). Sans ajustement, on garde la **confusion** (15,5 : $C$ pousse à la fois $T$ et $Y$) ; avec $\{C,M\}$, on retire la voie par le médiateur et on mesure l'effet **direct** (5), ce qui peut être voulu mais ne répond pas à la question « que fait $T$ ? » ; avec $\{C,K\}$, on conditionne sur un effet commun : l'estimation s'effondre vers 0, **en créant un biais**, alors que $K$ semble une covariable « utile ».

**Corrigé 5.** (a) Nombres de traités par strate : $0{,}2\times400=80$, $0{,}5\times400=200$, $0{,}8\times200=160$ (total 440) ; de témoins : $320$, $200$, $40$ (total 560). Moyenne des traités $=(80\times130+200\times150+160\times190)/440=160{,}9$ ; moyenne des témoins $=(320\times100+200\times115+40\times150)/560=108{,}9$ ; différence naïve $=52{,}0$. (b) Effets par strate : $30,35,40$ ; ATE $=(400\times30+400\times35+200\times40)/1000=34{,}0$. (c) IPW : poids $1/e$ pour les traités, $1/(1-e)$ pour les témoins. Dans chaque strate, le poids total des traités est $n$ et celui des témoins aussi ; la pseudo-population a donc la même composition dans les deux groupes. L'ATE par IPW coïncide avec 34.

```python
ex5 = pd.DataFrame({"strate": ["A", "B", "C"], "n": [400, 400, 200], "e": [0.2, 0.5, 0.8],
                    "m1": [130, 150, 190], "m0": [100, 115, 150]})
ex5["n1"], ex5["n0"] = ex5.n * ex5.e, ex5.n * (1 - ex5.e)
naif = (ex5.n1 * ex5.m1).sum() / ex5.n1.sum() - (ex5.n0 * ex5.m0).sum() / ex5.n0.sum()
ate = ((ex5.m1 - ex5.m0) * ex5.n).sum() / ex5.n.sum()
m1_ipw = (ex5.n1 * ex5.m1 / ex5.e).sum() / (ex5.n1 / ex5.e).sum()
m0_ipw = (ex5.n0 * ex5.m0 / (1 - ex5.e)).sum() / (ex5.n0 / (1 - ex5.e)).sum()
print(f"différence naïve = {naif:.1f} | ATE par strate = {ate:.1f} | ATE par IPW = {m1_ipw - m0_ipw:.1f}")
```
<!--sortie-->
```text
différence naïve = 52.0 | ATE par strate = 34.0 | ATE par IPW = 34.0
```

**Corrigé 6.** (a)-(b) On refait l'estimation du score, puis on restreint :

```python
obs = pd.read_csv("donnees/ch07-observationnel.csv")
verite = pd.read_csv("donnees/ch07-observationnel-verite.csv")
d6 = obs.merge(verite, on="id_client")
d6["ps"] = smf.logit("offre ~ age + C(canal) + engagement", d6).fit(disp=0).predict(d6)
ate_vrai = (d6.y1 - d6.y0).mean()

def ipw_ate(df):
    w = np.where(df.offre == 1, 1 / df.ps, 1 / (1 - df.ps))
    return (np.average(df.depense[df.offre == 1], weights=w[df.offre == 1])
            - np.average(df.depense[df.offre == 0], weights=w[df.offre == 0]))

restreint = d6[(d6.ps >= 0.1) & (d6.ps <= 0.9)]
ate_restreint_vrai = (restreint.y1 - restreint.y0).mean()
print(f"clients conservés : {len(restreint)} sur {len(d6)} ({len(restreint) / len(d6):.1%})")
print(f"IPW, tous les clients     : {ipw_ate(d6):.2f}   (ATE vrai de la population : {ate_vrai:.2f})")
print(f"IPW, scores dans [0,1 ; 0,9] : {ipw_ate(restreint):.2f}   (ATE vrai de ce sous-échantillon : {ate_restreint_vrai:.2f})")
```
<!--sortie-->
```text
clients conservés : 3778 sur 4000 (94.5%)
IPW, tous les clients     : 14.36   (ATE vrai de la population : 15.53)
IPW, scores dans [0,1 ; 0,9] : 14.73   (ATE vrai de ce sous-échantillon : 15.59)
```

(c) En restreignant, on change la **population cible** : on estime l'effet pour les clients dont la probabilité d'offre n'est ni très faible ni très forte (la population de « chevauchement »), et non plus pour tous. Ici, la différence est **minime** : 94,5 % des clients restent, et l'ATE vrai du sous-échantillon (15,59) est presque celui de la population (15,53), parce que le chevauchement était déjà bon ; l'estimation passe de 14,36 à 14,73. Elle serait beaucoup plus importante si l'on devait écarter une grande partie des clients : l'ATE vrai du sous-échantillon pourrait alors différer sensiblement de celui de la population dès que l'effet varie avec le score (ici, il varie avec le canal, et le canal influence le score). Dans tous les cas, l'estimation répond à une question légèrement différente (celle de la population de chevauchement), à **dire explicitement** dans le rapport.

**Corrigé 7.** (a) En niveau : $(150-120)-(92-80)=30-12=18$ milliers de €. (b) En logarithme : $\ln(150/120)-\ln(92/80)=\ln1{,}25-\ln1{,}15=0{,}2231-0{,}1398=0{,}0833$ (le code donne 0,0834, sans l'arrondi intermédiaire), soit un effet relatif d'environ $+8{,}7\,\%$ ($e^{0{,}0833}-1$). Les villes traitées auraient crû de $25\,\%$ ; les témoins de $15\,\%$ ; sans campagne, les traitées auraient crû de $15\,\%$ aussi, soit $138$, ce qui donne un effet de $150-138=12$ milliers, et non 18. (c) Si le chiffre d'affaires évolue en **pourcentage**, les tendances parallèles sont plausibles **en logarithme** : l'effet de 18 milliers en niveau surestime l'effet réel (il suppose que la ville traitée, plus grosse, aurait crû de $12$ milliers comme la petite, alors qu'une croissance de $15\,\%$ sur 120 fait $18$ : la hausse « naturelle » des grandes villes est plus grande en niveau).

```python
a_b, a_a, t_b, t_a = 80, 92, 120, 150
print(f"DiD en niveau : {(t_a - t_b) - (a_a - a_b)} | DiD en log : {np.log(t_a / t_b) - np.log(a_a / a_b):.4f} (soit {np.exp(np.log(t_a / t_b) - np.log(a_a / a_b)) - 1:+.1%})")
print(f"contrefactuel multiplicatif pour les villes traitées : {t_b * a_a / a_b:.0f}  -> effet {t_a - t_b * a_a / a_b:.0f}")
```
<!--sortie-->
```text
DiD en niveau : 18 | DiD en log : 0.0834 (soit +8.7%)
contrefactuel multiplicatif pour les villes traitées : 138  -> effet 12
```

**Corrigé 8.**

```python
temoins = panel[panel["groupe_traite"] == 0]
villes = temoins["ville"].unique()
rng = np.random.default_rng(81)
t_stats = []
for _ in range(300):
    faux = set(rng.choice(villes, 4, replace=False))
    d8 = temoins.assign(camp=(temoins["ville"].isin(faux) & (temoins["t"] >= 18)).astype(int))
    m = smf.ols("np.log(commandes) ~ camp + C(ville) + C(t)", d8).fit(cov_type="cluster", cov_kwds={"groups": d8["vid"]})
    t_stats.append(m.params["camp"] / m.bse["camp"])
t_stats = np.array(t_stats)
print(f"seuil normal 1,96            : {np.mean(np.abs(t_stats) > 1.96):.1%} de « découvertes »")
print(f"seuil de Student (11 ddl)    : {np.mean(np.abs(t_stats) > stats.t.ppf(0.975, 11)):.1%} de « découvertes »")
```
<!--sortie-->
```text
seuil normal 1,96            : 8.0% de « découvertes »
seuil de Student (11 ddl)    : 4.7% de « découvertes »
```

(a)-(b) Avec le seuil normal, le test « découvre » un effet là où il n'y en a aucun dans environ 8 % des simulations au lieu des 5 % annoncés ; avec le seuil de Student à 11 degrés de liberté, le taux retombe à près de 5 % (4,7 %). (c) Quand le nombre de groupes (ici 12 villes, dont 4 « traitées ») est petit, les erreurs-types groupées sont **trop optimistes** et le seuil normal est trop laxiste : on obtient des faux positifs en excès. Remèdes : seuil de Student avec peu de degrés de liberté, bootstrap par groupes, ou tests de permutation (volume I, section 3.7) : c'est exactement ce que nous venons de faire, puisque la distribution de l'effet « fictif » est la distribution de référence d'un test de permutation.

**Corrigé 9.** (a) $\hat\beta=\dfrac{52-46}{0{,}60-0{,}30}=\dfrac{6}{0{,}3}=20$ €. (b) La part de **complaisants** est $\pi=0{,}60-0{,}30=30\,\%$ (sous la monotonie) : l'effet de 20 € est l'effet **pour ces 30 %** de clients. (c) Un effet direct $\gamma_Z=1{,}5$ ajouterait $1{,}5$ à la forme réduite ($6\to7{,}5$) sans changer la première étape : l'estimation deviendrait $7{,}5/0{,}3=25$, soit un biais de $\gamma_Z/\pi=1{,}5/0{,}3=5$ €.

```python
pi, rho = 0.60 - 0.30, 52 - 46
print(f"Wald = {rho / pi:.1f} | avec effet direct de 1,5 : {(rho + 1.5) / pi:.1f} | biais = {1.5 / pi:.1f}")
```
<!--sortie-->
```text
Wald = 20.0 | avec effet direct de 1,5 : 25.0 | biais = 5.0
```

**Corrigé 10.** (a) Comme $Z\in\{0,1\}$ : $\operatorname{Cov}(Z,Y)=\mathbb E[ZY]-\mathbb E[Z]\,\mathbb E[Y]$. On a $\mathbb E[ZY]=q\,\mathbb E[Y\mid Z=1]$ et $\mathbb E[Y]=q\,\mathbb E[Y\mid Z=1]+(1-q)\,\mathbb E[Y\mid Z=0]$. Donc $\operatorname{Cov}(Z,Y)=q\,\mu_1-q\big(q\mu_1+(1-q)\mu_0\big)=q(1-q)(\mu_1-\mu_0)$ avec $\mu_z=\mathbb E[Y\mid Z=z]$. (b) La même formule vaut pour $T$ à la place de $Y$ ; dans le rapport, le facteur $q(1-q)$ se **simplifie**, et il reste $\dfrac{\mathbb E[Y\mid Z=1]-\mathbb E[Y\mid Z=0]}{\mathbb E[T\mid Z=1]-\mathbb E[T\mid Z=0]}$, le rapport de Wald. (c) Vérification :

```python
iv_data = pd.read_csv("donnees/ch07-iv.csv")
z, tt, yy = iv_data["rappel"].to_numpy(float), iv_data["suit_instagram"].to_numpy(float), iv_data["depense"].to_numpy()
q = z.mean()
cov_zy, cov_zt = np.cov(z, yy, ddof=0)[0, 1], np.cov(z, tt, ddof=0)[0, 1]
rho = yy[z == 1].mean() - yy[z == 0].mean()
pi = tt[z == 1].mean() - tt[z == 0].mean()
print(f"Cov(Z,Y) = {cov_zy:.4f}  vs  q(1-q) x rho = {q * (1 - q) * rho:.4f}")
print(f"Cov(Z,Y)/Cov(Z,T) = {cov_zy / cov_zt:.4f}  |  rapport de Wald rho/pi = {rho / pi:.4f}")
```
<!--sortie-->
```text
Cov(Z,Y) = 2.2000  vs  q(1-q) x rho = 2.2000
Cov(Z,Y)/Cov(Z,T) = 23.6563  |  rapport de Wald rho/pi = 23.6563
```

**Corrigé 11.** (a)-(b) On réutilise la simulation de 7.1.7 (même graine), mais avec la motivation dans la régression :

```python
rng = np.random.default_rng(71)
n = 100_000
motivation = rng.normal(size=n)
offre = rng.integers(0, 2, n)
code_si_offre = rng.random(n) < 1 / (1 + np.exp(-(0.4 + 0.9 * motivation)))
code = offre * code_si_offre
depense = 100 + 8 * offre + 30 * code + 20 * motivation + rng.normal(0, 25, n)
d11 = pd.DataFrame({"depense": depense, "offre": offre, "code": code, "motivation": motivation})

total = smf.ols("depense ~ offre", d11).fit().params["offre"]
direct = smf.ols("depense ~ offre + code + motivation", d11).fit().params["offre"]
print(f"effet total estimé (offre seule)            : {total:.2f}")
print(f"effet direct estimé (offre + code + motivation) : {direct:.2f}   (vrai : 8)")
print(f"effet indirect = total - direct = {total - direct:.2f}   (vrai : 30 x {code_si_offre.mean():.2f} = {30 * code_si_offre.mean():.2f})")
```
<!--sortie-->
```text
effet total estimé (offre seule)            : 25.62
effet direct estimé (offre + code + motivation) : 8.27   (vrai : 8)
effet indirect = total - direct = 17.35   (vrai : 30 x 0.58 = 17.47)
```

(c) En 7.1.7, la motivation était **cachée** : conditionner sur le médiateur ouvrait un chemin biaisé $\text{offre}\to\text{code}\leftarrow\text{motivation}\to\text{dépense}$ (le code est un effet commun de l'offre et de la motivation). Quand la motivation est **observée et incluse**, ce chemin est bloqué, et le coefficient de l'offre redevient l'effet **direct**. Moralité : l'analyse de médiation exige de contrôler **tous** les facteurs de confusion entre le médiateur et le résultat, une hypothèse supplémentaire, plus exigeante que celle de l'effet total (qui n'en demande aucune dans une expérience randomisée).

**Corrigé 12.** Il n'y a pas de code ici : c'est une analyse critique. *Pertinence* : la distance doit réellement influencer la fréquentation (plausible : plus on habite loin, moins on vient) ; on le **vérifie** avec la première étape et sa statistique $F$. *Indépendance* : les clients **choisissent** où habiter, et ce choix dépend du revenu, du mode de vie, de l'âge : la distance n'est pas tirée au sort. Les citadins aisés habitent peut-être près du centre, où se trouve la boutique, et dépensent plus pour cette raison : l'instrument est corrélé à un facteur de confusion. On peut atténuer en **ajustant** sur les variables socio-économiques observées et sur la ville, mais jamais complètement. *Exclusion* : la distance ne doit affecter la dépense **que** via la fréquentation de la boutique ; or elle peut affecter la dépense par d'autres voies (un client éloigné achète davantage en ligne, ou fait de plus gros achats par déplacement). On peut chercher des **tests de plausibilité** (l'effet de la distance sur la dépense en ligne devrait être nul chez ceux qui ne viennent jamais en boutique) sans pouvoir prouver l'exclusion. *Ce qu'on estimerait si l'instrument était valide* : l'effet moyen de venir en boutique pour les **complaisants**, c'est-à-dire les clients dont la fréquentation **dépend** de la distance (ceux qui viendraient s'ils habitaient près et ne viendraient pas s'ils habitaient loin) : pas pour les habitués, ni pour ceux qui ne viendraient jamais. Pour une variable continue comme la distance, l'interprétation est une moyenne pondérée de tels effets, plus difficile à énoncer.

---

## Bilan du chapitre 7

Vous savez maintenant :

- **formuler** une question causale avec les **résultats potentiels**, distinguer ATE, ATT et ATU, et comprendre pourquoi l'estimation d'un effet est un problème de **données manquantes** (le problème fondamental) ;
- **décomposer** une différence observée en effet causal et **biais de sélection**, et expliquer pourquoi la **randomisation** supprime le second ;
- **analyser une expérience randomisée** : tableau d'équilibre, effet moyen, intervalle de confiance, ajustement pour la précision ;
- **lire un graphe causal** (DAG) : chaîne, fourche, collision ; savoir ce qu'il faut ajuster (les causes communes) et ce qu'il ne faut **pas** ajuster (médiateurs, effets communs) ; énoncer le **critère de la porte dérobée** ;
- **estimer** un effet à partir de données observationnelles avec un **score de propension** (appariement, IPW, estimateur doublement robuste), et **vérifier** le chevauchement et l'équilibre ;
- **mener une différence de différences** : calcul à la main, régression à effets fixes avec erreurs-types groupées, **étude d'événement**, test placebo, et connaître ses pièges (tendances non parallèles, échelle, peu de groupes, lancements échelonnés) ;
- **utiliser une variable instrumentale** : Wald et 2SLS, conditions de validité, interprétation en **effet pour les complaisants**, danger des instruments faibles et de l'exclusion violée ;
- **comparer** ces méthodes et **dire honnêtement** ce qu'aucune d'elles ne peut garantir : toutes remplacent une information absente par une **hypothèse**.

> 💡 **La seule phrase à retenir.** Un résultat causal s'écrit toujours sous la forme : « *si* (hypothèse), *alors* (effet estimé, avec son incertitude) ». Ce chapitre vous a appris à écrire des hypothèses honnêtes, et à les mettre à l'épreuve.
