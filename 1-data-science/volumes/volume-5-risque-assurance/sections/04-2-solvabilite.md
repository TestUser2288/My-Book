## 4.2 Cadre Solvabilité

Un assureur n'est pas une banque. Il encaisse des primes **avant** de connaître le coût de ce qu'il a promis, et il paie des sinistres parfois **dix ans** plus tard. Ses dettes ne sont pas des dépôts mais des **engagements envers les assurés**, dont la valeur dépend de lois de probabilité (chapitre 2). Les régimes de contrôle des assureurs tiennent compte de cette différence. Nous prenons comme référence les régimes dits « de type Solvabilité II », conçus à l'origine pour un grand ensemble régional de pays et pris pour modèle ailleurs : ils sont fondés sur le **risque**, et leur logique est celle que nous voulons comprendre. À la fin de cette section, vous saurez construire un **bilan économique**, calculer une **marge de risque** et un **capital de solvabilité requis** (SCR) par agrégation de modules, et vous saurez discuter ce que vaut cette agrégation.

### 4.2.1 Trois piliers, comme pour les banques

La structure rappelle celle du cadre de Bâle (section 4.1), mais le contenu est celui de l'assurance.

- **Pilier 1 : exigences quantitatives.** Comment évaluer les **provisions techniques**, quels **fonds propres** sont admis, et combien il en faut : un **capital de solvabilité requis** (SCR) et un seuil plus bas, le **minimum de capital requis** (MCR).
- **Pilier 2 : gouvernance et surveillance.** Un système de gestion des risques, quatre **fonctions clés** (gestion des risques, conformité, audit interne, fonction actuarielle) et une évaluation interne des risques et de la solvabilité, l'**ORSA** (*own risk and solvency assessment*), tournée vers l'avenir, qui comprend des scénarios de crise (section 3.2).
- **Pilier 3 : transparence.** Des **rapports** à l'autorité (états quantitatifs périodiques) et un rapport public sur la solvabilité et la situation financière.

Le principe fondamental est celui de l'**évaluation économique** : on valorise tout **à sa valeur de marché ou à une valeur cohérente avec le marché**, y compris les engagements, et on mesure le risque par la perte de **fonds propres** possible sur un an.

### 4.2.2 Le bilan économique

Dans le bilan comptable traditionnel, les actifs et les provisions sont enregistrés à des valeurs prudentes, souvent historiques. Dans le **bilan économique**, les actifs sont à la valeur de marché et les engagements à la **valeur actuelle des flux futurs attendus**, plus une marge pour le risque. Les fonds propres sont ce qui reste :

$$\text{fonds propres} = \text{actifs} - \text{provisions techniques} - \text{autres dettes},\qquad \text{provisions techniques} = \text{meilleure estimation} + \text{marge de risque}.$$

Pour notre mutuelle fictive, supposons 1 270 M€ d'actifs, une meilleure estimation de 900 M€ et une marge de risque que nous calculons plus bas (36,5 M€) ; sans autre dette, les fonds propres s'élèvent à $1\,270 - 900 - 36{,}5 = 333{,}5$ M€. La question du pilier 1 est de savoir si 333,5 M€ **suffit**.

Tous les fonds propres ne se valent pas. Le régime les classe en trois **niveaux** (*tiers*) selon leur capacité à absorber une perte, y compris en cas de liquidation : le niveau 1 (capital social, réserves : la meilleure qualité), le niveau 2 (dettes subordonnées de longue durée), le niveau 3 (par exemple des impôts différés actifs). Des **limites quantitatives** empêchent de couvrir le SCR avec des éléments de moindre qualité ; nous les ignorons, et nous parlons de « fonds propres éligibles » sans distinguer les niveaux.

### 4.2.3 Meilleure estimation et marge de risque

La **meilleure estimation** (*best estimate*) est la **moyenne pondérée par les probabilités** des flux de trésorerie futurs, actualisée à une courbe de taux sans risque. Ni le scénario central, ni un scénario prudent : l'**espérance**. Un exemple à la main, sur une branche en extinction. Trois scénarios de paiements de sinistres sur trois ans (en M€) :

| Scénario | Probabilité | Année 1 | Année 2 | Année 3 |
|---|---|---|---|---|
| Favorable | 50 % | 60 | 30 | 10 |
| Central | 30 % | 70 | 40 | 15 |
| Défavorable | 20 % | 90 | 60 | 30 |
| **Flux attendu** | | $0{,}5\cdot60+0{,}3\cdot70+0{,}2\cdot90=69$ | $39$ | $15{,}5$ |

Avec un taux d'actualisation de 2 %, la meilleure estimation vaut $69/1{,}02+39/1{,}02^2+15{,}5/1{,}02^3\approx 119{,}7$ M€, alors que le seul scénario favorable donnerait 97,1 M€. Cette provision est exactement celle que cherchent les méthodes du chapitre 2 (chain ladder, Mack, bootstrap : section 2.5) : le chain ladder fournit une **espérance** des paiements futurs, le bootstrap leur **dispersion**.

La **marge de risque** (*risk margin*) rémunère un repreneur hypothétique qui devrait **porter le portefeuille jusqu'à son extinction** : il doit immobiliser du capital, au fur et à mesure de l'écoulement des engagements, et ce capital a un coût. On la calcule par la méthode du **coût du capital** :

$$\text{RM}=c\sum_{t\ge0}\frac{\text{SCR}_t}{(1+r_{t+1})^{t+1}},$$

où $\text{SCR}_t$ est le capital requis pour le portefeuille restant à la date $t$ et $c$ le taux du coût du capital, fixé par le texte (6 % dans la calibration d'origine du régime, une valeur que les révisions ultérieures ont abaissée ; à vérifier dans le texte en vigueur). Si le capital requis du portefeuille de la mutuelle décroît en cinq ans de 100 %, 70 %, 45 %, 25 % et 10 % de son niveau initial (253,8 M€, calculé juste après) et que l'actualisation est à 2 %, la somme actualisée vaut $253{,}8\times2{,}399\approx 608{,}9$, et la marge de risque est $0{,}06\times608{,}9\approx 36{,}5$ M€. Plus le portefeuille s'écoule lentement, plus la marge est grande : **les branches à queue longue coûtent plus cher en marge de risque**.

### 4.2.4 Le capital de solvabilité requis

Le SCR est calibré pour que l'assureur **survive, avec une probabilité de 99,5 %, à un choc d'une année** : c'est la valeur en risque à 99,5 % sur un an des fonds propres (section 3.1). Calculer un quantile du résultat global exigerait un modèle interne complet ; la **formule standard** procède **par modules** puis les agrège.

Chaque module mesure la perte de fonds propres que provoquerait un choc calibré : **marché** (actions, taux d'intérêt, immobilier, spread de crédit, change), **défaut des contreparties** (réassureurs, banques), **souscription vie**, **souscription santé**, **souscription non-vie** (primes et réserves, catastrophes). Dans notre exemple, les charges sont en M€ : marché 110, défaut 20, vie 30, santé 45, non-vie 140. Leur somme vaut 345 M€, mais les modules ne sont pas **parfaits corrélés** : une tempête n'a rien à voir avec une mauvaise année boursière. On les agrège donc par une **matrice de corrélation** $R$ :

$$\text{BSCR}=\sqrt{\sum_{i,j} R_{ij}\,\text{SCR}_i\,\text{SCR}_j}=\sqrt{c^\top R\,c}.$$

Voici la matrice d'exemple (des valeurs de l'ordre de celles de la formule standard, **données à titre d'illustration**) :

| | marché | défaut | vie | santé | non-vie |
|---|---|---|---|---|---|
| marché | 1 | 0,25 | 0,25 | 0,25 | 0,25 |
| défaut | 0,25 | 1 | 0,25 | 0,25 | 0,5 |
| vie | 0,25 | 0,25 | 1 | 0,25 | 0 |
| santé | 0,25 | 0,25 | 0,25 | 1 | 0,5 |
| non-vie | 0,25 | 0,5 | 0 | 0,5 | 1 |

Un calcul à la main sur **deux** modules rend la formule concrète : marché (110) et non-vie (140), corrélation 0,25. On obtient $\sqrt{110^2+140^2+2\times0{,}25\times110\times140}=\sqrt{12\,100+19\,600+7\,700}=\sqrt{39\,400}\approx198{,}5$ M€, contre une somme de 250 M€ : la **diversification** retire 51,5 M€. Avec les cinq modules, le calcul se fait en une ligne.

```python hide
corr = np.array([[1, .25, .25, .25, .25], [.25, 1, .25, .25, .5], [.25, .25, 1, .25, 0],
                 [.25, .25, .25, 1, .5], [.25, .5, 0, .5, 1]])      # matrice d'exemple du tableau ci-dessus
```

```python
charges = np.array([110, 20, 30, 45, 140.])         # M€ : marché, défaut, vie, santé, non-vie
bscr = agreger(charges, corr)                        # racine de c' R c
```

Le résultat est un SCR de base de 241,8 M€ pour une somme de 345 M€ : la diversification retire **103,2 M€**, soit près de 30 %. On ajoute le capital pour le **risque opérationnel** (12 M€ ici) et on obtiendrait, dans le texte complet, un ajustement pour la capacité d'absorption des pertes par les provisions et les impôts différés, que nous omettons : le **SCR vaut 253,8 M€**. Le **ratio de solvabilité** est le rapport des fonds propres éligibles au SCR : $333{,}5/253{,}8 \approx 131{,}4$ %. Au-dessus de 100 %, l'exigence est respectée ; en dessous, l'autorité demande un plan de rétablissement.

![Du total des modules au capital de solvabilité requis : la diversification entre modules retire environ 30 % de la somme des charges ; le risque opérationnel s'y ajoute. La ligne marque les fonds propres éligibles de la mutuelle fictive.](figures/ch04-scr-cascade.png)

```python hide
modules = ["marché", "défaut", "vie", "santé", "non-vie"]
corr = np.array([[1, .25, .25, .25, .25], [.25, 1, .25, .25, .5], [.25, .25, 1, .25, 0],
                 [.25, .25, .25, 1, .5], [.25, .5, 0, .5, 1]])
charges = np.array([110, 20, 30, 45, 140.])
bscr = agreger(charges, corr)
op = 12.0
scr = bscr + op
diversif = charges.sum() - bscr
proba_sc = np.array([.5, .3, .2])
flux = np.array([[60, 30, 10], [70, 40, 15], [90, 60, 30.]])
flux_att = proba_sc @ flux
taux = 0.02
BE = sum(flux_att[t] / (1 + taux) ** (t + 1) for t in range(3))
BE_fav = sum(flux[0][t] / (1 + taux) ** (t + 1) for t in range(3))
motif = np.array([1, .7, .45, .25, .1])
scr_t = scr * motif
somme_act = sum(scr_t[t] / (1 + taux) ** (t + 1) for t in range(5))
RM = 0.06 * somme_act
actifs, be_bilan = 1270.0, 900.0
FP = actifs - be_bilan - RM
print("flux attendus (M€) :", flux_att, "| meilleure estimation :", round(BE, 2), "| scénario favorable seul :", round(BE_fav, 2))
print("somme des charges :", charges.sum(), "| SCR de base :", round(bscr, 1), "| diversification :", round(diversif, 1), "(", round(100 * diversif / charges.sum(), 1), "%)")
print("deux modules (marché, non-vie) :", round(agreger([110, 140], [[1, .25], [.25, 1]]), 1), "au lieu de 250")
print("SCR (avec opérationnel 12) :", round(scr, 1), "| SCR_t :", scr_t.round(1))
print("somme actualisée des SCR_t :", round(somme_act, 1), "| marge de risque :", round(RM, 2))
print("fonds propres :", round(FP, 1), "| ratio de solvabilité :", round(100 * FP / scr, 1), "% | couloir du MCR :", round(.25 * scr, 1), "à", round(.45 * scr, 1))
print("ratio après un choc de 100 / 150 M€ :", round(100 * (FP - 100) / scr, 1), "/", round(100 * (FP - 150) / scr, 1), "%")
```
<!--sortie-->
```text
flux attendus (M€) : [69.  39.  15.5] | meilleure estimation : 119.74 | scénario favorable seul : 97.08
somme des charges : 345.0 | SCR de base : 241.8 | diversification : 103.2 ( 29.9 %)
deux modules (marché, non-vie) : 198.5 au lieu de 250
SCR (avec opérationnel 12) : 253.8 | SCR_t : [253.8 177.7 114.2  63.5  25.4]
somme actualisée des SCR_t : 608.9 | marge de risque : 36.53
fonds propres : 333.5 | ratio de solvabilité : 131.4 % | couloir du MCR : 63.5 à 114.2
ratio après un choc de 100 / 150 M€ : 92.0 / 72.3 %
```

```python hide
fig, ax = plt.subplots(figsize=(7.6, 3.9))
noms = modules + ["somme", "diversification", "SCR de base", "opérationnel", "SCR"]
vals = list(charges) + [charges.sum(), -diversif, bscr, op, scr]
bas, h, coul = [], [], []
cum = 0.0
for i, (n_, v) in enumerate(zip(noms, vals)):
    if i < 5:
        bas.append(cum); h.append(v); coul.append(style.BLEU); cum += v
    elif n_ == "somme":
        bas.append(0); h.append(v); coul.append(style.MUET)
    elif n_ == "diversification":
        bas.append(charges.sum() - diversif); h.append(diversif); coul.append(style.ORANGE)
    elif n_ == "SCR de base":
        bas.append(0); h.append(v); coul.append(style.VIOLET)
    elif n_ == "opérationnel":
        bas.append(bscr); h.append(v); coul.append(style.BLEU)
    else:
        bas.append(0); h.append(v); coul.append(style.VIOLET)
ax.bar(range(len(noms)), h, bottom=bas, color=coul, width=0.7)
for i, (b_, h_) in enumerate(zip(bas, h)):
    ax.text(i, b_ + h_ + 5, ("−" if noms[i] == "diversification" else "") + "%.0f" % h_, ha="center", fontsize=8.5, color=style.ENCRE2)
ax.axhline(FP, color=style.ROUGE, lw=1.3, ls="--")
ax.text(-0.4, FP + 8, "fonds propres éligibles : %.0f M€" % FP, ha="left", color=style.ROUGE, fontsize=9)
ax.set_xticks(range(len(noms)))
ax.set_xticklabels(noms, rotation=30, ha="right", fontsize=8.5)
ax.set_ylabel("M€")
ax.set_ylim(0, 420)
fig.savefig("figures/ch04-scr-cascade.png", dpi=200, bbox_inches="tight")
plt.close(fig)
```

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.4 (agréger les modules et mesurer la diversification) et exercice 4.6 (un SCR à trois modules, à la main).

### 4.2.5 Que vaut l'agrégation par corrélations ?

La racine d'une forme quadratique n'est pas arbitraire : elle est **exacte** dans un cas précis.

> 📐 **Quand la formule d'agrégation est exacte.** Si les pertes des modules suivent une loi **normale multivariée**, de corrélations $R$ et d'écarts-types $\sigma_i$, la perte totale est normale, d'écart-type $\sqrt{\sigma^\top R\,\sigma}$. Son quantile à 99,5 % est $z\sqrt{\sigma^\top R\,\sigma}$ avec $z=\Phi^{-1}(0{,}995)\approx2{,}576$. Or la charge de chaque module est son propre quantile à 99,5 % : $\text{SCR}_i=z\,\sigma_i$. Donc le quantile de la perte totale vaut $\sqrt{c^\top R\,c}$ avec $c_i=z\sigma_i$, qui est exactement la formule de la formule standard.

Mais les risques d'assurance ne sont pas normaux. Pour mesurer l'écart, on simule les cinq modules sous trois hypothèses, en **imposant à chacun la même charge isolée** (le même quantile à 99,5 %, donc les mêmes 110, 20, 30, 45, 140) :

```python hide-code
from scipy.stats import t as loi_t

def var_totale(variante, seed=0, n=400000):
    rng = np.random.default_rng(seed)
    Z = rng.standard_normal((n, 5)) @ np.linalg.cholesky(corr).T
    z = norm.ppf(0.995)
    if variante == "normale":
        tot = (Z * charges / z).sum(axis=1)
    elif variante == "asymetrique":
        s = np.array([.15, .15, .15, .5, .8])                     # santé et non-vie très asymétriques (loi lognormale)
        base = np.exp(s * Z) - np.exp(s * s / 2)
        q = np.exp(s * z) - np.exp(s * s / 2)
        tot = (base * charges / q).sum(axis=1)
    else:                                                          # copule de Student (4 ddl), marginales normales
        W = rng.chisquare(4, n) / 4
        T = Z / np.sqrt(W)[:, None]
        tot = (norm.ppf(loi_t.cdf(T, 4)) * charges / z).sum(axis=1)
    return float(np.quantile(tot, 0.995))

print("formule standard (racine de c' R c)           :", round(bscr, 1))
for v, nom in (("normale", "marginales normales, copule gaussienne"), ("asymetrique", "marginales asymétriques, copule gaussienne"),
               ("copule_t", "marginales normales, copule de Student")):
    print("%-46s: %.1f" % (nom, var_totale(v)))
```
<!--sortie-->
```text
formule standard (racine de c' R c)           : 241.8
marginales normales, copule gaussienne        : 242.1
marginales asymétriques, copule gaussienne    : 220.1
marginales normales, copule de Student        : 260.9
```

Sous l'hypothèse normale, la simulation (242,1 M€) retrouve la formule (241,8 M€), à l'erreur de simulation près. Avec des marginales **asymétriques** (comme le sont les sinistres), la perte totale au quantile 99,5 % est **plus petite** : 220,1 M€. Les grandes pertes de chaque module sont rares et ne se produisent pas en même temps, et la formule serait **prudente**. Mais avec une **dépendance de queue** (une copule de Student à 4 degrés de liberté, qui fait que les modules **s'effondrent ensemble** dans les situations extrêmes), la perte monte à 260,9 M€ : la formule serait **imprudente** de 8 %. La formule d'agrégation n'est **ni prudente ni imprudente par nature** ; elle ne l'est qu'à l'aune des queues et de la dépendance de queue, ce que la corrélation linéaire ne mesure pas (copules : volume II, section 6.6 ; sous-additivité de la valeur en risque : section 3.1).

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : exercice 4.8 (la perte totale selon le nombre de degrés de liberté de la copule).

C'est précisément la raison d'être des **modèles internes** : un assureur qui estime qu'un portefeuille a un profil très différent de celui qu'a calibré la formule standard peut proposer son propre modèle, après approbation de l'autorité et sous exigences de validation (section 3.4). Un modèle interne est plus riche, mais il porte un **risque de modèle** de plus.

### 4.2.6 MCR, niveaux d'intervention et ORSA

Le **MCR** est un seuil plus bas : sous lui, l'agrément de l'assureur est en jeu. Il se calcule par une formule linéaire plus simple, bornée à un couloir de **25 % à 45 % du SCR** (et à un plancher absolu), ce qui donne ici une plage de 63,5 à 114,2 M€. Les niveaux d'intervention sont graduels :

| Situation | Conséquence typique |
|---|---|
| Fonds propres ≥ SCR | situation normale, supervision courante |
| MCR ≤ fonds propres < SCR | plan de rétablissement à remettre à l'autorité sous un délai court |
| Fonds propres < MCR | mesures les plus sévères : restriction d'activité, retrait d'agrément si la situation ne se redresse pas |

Reprenons notre mutuelle. Un choc de marché de 100 M€ sur ses actifs ramène les fonds propres à 233,5 M€ et le ratio à **92 %** : le SCR est franchi, le MCR non. Un choc de 150 M€ ramène le ratio à **72 %** (les fonds propres, 183,5 M€, restent au-dessus du couloir du MCR). Le rôle de l'**ORSA** est justement de **ne pas attendre la crise** : la mutuelle calcule ces chocs avant, avec des scénarios propres à son portefeuille (section 3.2), dit à l'autorité ce qu'elle ferait (réduire le risque, lever du capital, se réassurer : chapitre 6), et vérifie que son profil de risque réel est cohérent avec les hypothèses de la formule standard.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.5 (marge de risque selon le rythme d'écoulement, ratio après chocs) et exercice 4.7 (une marge de risque à la main).

> ⚠️ **Piège : un ratio, c'est un quotient.** Un ratio de 131 % peut baisser parce que les fonds propres baissent **ou** parce que le SCR monte (le même choc de marché alourdit les deux). Suivez toujours les deux termes, et rappelez-vous que les fonds propres dépendent d'une **meilleure estimation** que le chapitre 2 a montrée incertaine : une provision sous-estimée de 5 % fait gagner au ratio des points qu'il n'a pas.

> ✅ **À retenir.**
> - Le régime de type Solvabilité II est fondé sur un **bilan économique** : actifs à la valeur de marché, provisions = **meilleure estimation** (espérance actualisée) + **marge de risque** (coût du capital sur le capital futur requis).
> - Le **SCR** est la perte de fonds propres à **99,5 % sur un an** ; la formule standard calcule des modules et les agrège par $\sqrt{c^\top R\,c}$ (ici : 345 M€ de somme, 241,8 M€ agrégés, 253,8 M€ avec l'opérationnel).
> - L'agrégation est exacte pour des pertes **normales** ; pour des pertes asymétriques elle peut être prudente, pour des queues dépendantes elle peut ne pas l'être. Un **modèle interne** ou une marge de jugement répond à cette limite, au prix d'un risque de modèle.
> - Les ratios ont des **niveaux d'intervention** (SCR, puis MCR) ; l'ORSA oblige à examiner **avant** la crise ce que l'on ferait.
> - Les chapitres 2 et 3 sont les **entrées** de ce cadre : provisions (2.3, 2.5), mesures de risque (3.1), scénarios (3.2), validation (3.4).
