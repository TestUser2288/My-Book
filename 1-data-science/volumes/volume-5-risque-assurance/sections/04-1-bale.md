## 4.1 Cadre de Bâle

Cette section présente le cadre international de supervision des **banques**, dit « de Bâle » d'après la ville où siège le comité qui l'élabore. Nous gardons l'essentiel : le but du capital réglementaire, la structure en trois piliers, la façon dont on pondère les expositions, et surtout **la formule des notations internes**, que nous démontrons au lieu de l'admettre. À la fin, vous saurez calculer le capital exigé pour un portefeuille de prêts à partir des **probabilités de défaut** (PD) du chapitre 1 et des **pertes en cas de défaut** (LGD), et vous saurez dire ce que ce nombre garantit… et ce qu'il ne garantit pas.

### 4.1.1 Pourquoi un capital réglementaire

Une banque prête de l'argent qu'elle a empruntée, en grande partie à ses déposants. Quand un prêt n'est pas remboursé, la perte est d'abord absorbée par les **fonds propres** (l'argent des actionnaires) ; si les fonds propres sont épuisés, ce sont les déposants et les créanciers qui perdent. Les actionnaires, eux, ne risquent que leur mise : ils ont donc intérêt à prêter plus et à moins de fonds propres que ce qui est prudent pour les autres. **Le capital réglementaire corrige cette incitation** : il impose un matelas minimal, proportionnel aux risques pris.

Pour fixer ce matelas, il faut distinguer **deux sortes de pertes**.

> 💡 **Perte attendue, perte inattendue.** Sur un portefeuille de prêts, une partie de la perte est **prévisible** : si 2 % des prêts font défaut chaque année en moyenne, ce coût est un **coût normal du métier**, que la banque facture dans le taux d'intérêt et met en **provision**. C'est la **perte attendue** (*expected loss*, EL). Une année exceptionnelle fait bien pire que la moyenne : l'écart entre la perte de cette année-là et la perte attendue est la **perte inattendue** (*unexpected loss*, UL). Les provisions couvrent l'EL ; **le capital couvre l'UL**, jusqu'à un niveau de confiance fixé.

Un exemple à la main. Une banque détient 1 000 prêts de 1 000 € chacun. Chaque prêt a une probabilité de défaut de 2 % sur l'année, et en cas de défaut on perd en moyenne 50 % de l'exposition. La perte attendue est $1\,000 \times 1\,000 \times 0{,}02 \times 0{,}5 = 10\,000$ €. Mais si l'économie se retourne et que 4 % des prêts font défaut, la perte est de $1\,000 \times 1\,000 \times 0{,}04 \times 0{,}5 = 20\,000$ €. L'excédent de 10 000 € ne peut pas être facturé a posteriori : il faut **l'avoir déjà en réserve**. Le régulateur demande combien : « le capital qui suffit dans 999 années sur 1 000 », ce qui est un quantile de la distribution des pertes, exactement l'objet de la section 3.1. Le capital réglementaire des banques est ainsi une **valeur en risque à 99,9 % sur un an, moins la perte attendue**.

### 4.1.2 Les trois piliers et les ratios

Le cadre repose sur trois piliers.

- **Pilier 1 : exigences minimales de fonds propres** pour trois risques : **crédit** (les emprunteurs ne remboursent pas), **marché** (les prix des actifs bougent) et **opérationnel** (erreurs, fraudes, pannes ; section 3.3). Il fixe des formules.
- **Pilier 2 : surveillance prudentielle.** La banque évalue elle-même son besoin total de capital, **y compris les risques que le pilier 1 ne voit pas** (concentration, taux d'intérêt du portefeuille bancaire, risque de modèle) ; l'autorité de contrôle examine cette évaluation et peut demander un supplément.
- **Pilier 3 : discipline de marché.** La banque **publie** ses expositions, ses ratios et ses méthodes, pour que les créanciers et les analystes puissent juger.

L'exigence se mesure par un **ratio** : fonds propres divisés par **actifs pondérés par le risque** (*risk-weighted assets*, RWA). Le tableau donne les ordres de grandeur du cadre international ; chaque pays peut les transposer en les durcissant.

| Élément | Valeur de principe | Lecture |
|---|---|---|
| Fonds propres de base (CET1) / RWA | au moins 4,5 % | actions et réserves : la meilleure qualité |
| Fonds propres de catégorie 1 / RWA | au moins 6 % | CET1 plus certains instruments hybrides |
| Fonds propres totaux / RWA | au moins 8 % | plus des instruments de moindre rang |
| Coussin de conservation | 2,5 % de RWA en CET1 | au-dessus du minimum ; sinon, restrictions de distribution |
| Coussin contracyclique | 0 à 2,5 % de RWA, décidé par pays | on le constitue quand le crédit s'emballe |
| Ratio de levier | au moins 3 % (catégorie 1 / expositions totales **non pondérées**) | garde-fou contre les modèles trop optimistes |
| Ratio de liquidité à 30 jours (LCR) | au moins 100 % (actifs liquides / sorties nettes de trésorerie sur 30 jours de stress) | survivre un mois de panique |
| Ratio de financement stable (NSFR) | au moins 100 % (financement stable disponible / requis) | ne pas financer du long avec du court |

Avec le coussin de conservation, la banque doit donc viser un CET1 d'au moins $4{,}5 + 2{,}5 = 7$ % de ses RWA, et un total d'au moins $8 + 2{,}5 = 10{,}5$ %. Pour 100 M€ de RWA, cela fait 10,5 M€ de fonds propres. Tout le travail du modélisateur est donc de **calculer le dénominateur**, les RWA, et de montrer que ce calcul est juste.

### 4.1.3 Les actifs pondérés par le risque

Une créance de 100 € n'a pas le même risque selon l'emprunteur. Le cadre multiplie l'exposition par un **poids de risque** pour obtenir les RWA. Deux familles de méthodes coexistent.

**L'approche standard.** Les poids sont fixés par le texte, par catégorie d'exposition : par exemple un poids de **75 %** pour la clientèle de détail (valeur d'ordre de grandeur dans l'approche standard historique), 100 % pour une entreprise non notée, un poids plus faible pour l'immobilier résidentiel bien garanti. C'est simple, comparable d'une banque à l'autre, mais **insensible au profil réel du portefeuille** : un prêt à très faible risque et un prêt à haut risque de la même catégorie pèsent autant.

**L'approche des notations internes** (*internal ratings-based*, IRB). La banque estime elle-même les paramètres de risque avec ses modèles, après validation par l'autorité, et **le texte fournit la formule** qui les transforme en capital. Il y a deux niveaux : dans l'approche **fondation**, la banque estime seulement la PD ; dans l'approche **avancée**, elle estime aussi la LGD et l'exposition au défaut (EAD ; section 1.5). On retrouve ici les trois paramètres du chapitre 1, qui deviennent les entrées d'une formule réglementaire :

$$\text{RWA}=12{,}5\times K\times \text{EAD}, \qquad \text{capital minimal} = 8\,\%\times \text{RWA} = K\times\text{EAD}.$$

Le facteur 12,5 est simplement l'inverse de 8 %. Un poids de risque de 100 % correspond donc à $K=8$ %. Il reste à connaître $K$.

### 4.1.4 La formule IRB, démontrée

La formule de $K$ n'est pas arbitraire : elle découle d'un **modèle à un facteur** dû à Vasicek, que nous établissons maintenant. Prenons un grand portefeuille de prêts semblables, de même PD, de même LGD, de même exposition.

> 📐 **Démonstration : de Vasicek à la formule IRB.**
> 1. Chaque emprunteur $i$ a une « valeur d'actifs » normalisée $X_i = \sqrt{\rho}\,Z + \sqrt{1-\rho}\,\varepsilon_i$, où $Z\sim\mathcal N(0,1)$ est un **facteur systématique** commun à tous (l'état de l'économie) et les $\varepsilon_i\sim\mathcal N(0,1)$ sont des aléas **propres** à chaque emprunteur, tous indépendants. Le paramètre $\rho$ est la **corrélation d'actifs** : plus il est grand, plus les défauts se produisent ensemble.
> 2. L'emprunteur $i$ fait défaut si $X_i \le c$, avec $c=\Phi^{-1}(\mathrm{PD})$ : cela donne bien $P(X_i\le c)=\mathrm{PD}$.
> 3. **Conditionnellement** à $Z=z$, les défauts sont indépendants, de probabilité
> $$p(z)=P(X_i\le c\mid Z=z)=\Phi\!\left(\frac{\Phi^{-1}(\mathrm{PD})-\sqrt{\rho}\,z}{\sqrt{1-\rho}}\right).$$
> 4. Pour un portefeuille **très granulaire** (beaucoup de petits prêts), la loi des grands nombres, conditionnelle à $Z$, dit que la **proportion de défauts est égale à $p(Z)$** : il ne reste plus que le risque systématique. Le taux de perte est $\text{LGD}\times p(Z)$.
> 5. La fonction $p$ est **décroissante** en $z$ : la perte est grande quand $Z$ est petit. Le quantile de niveau $q$ de la perte correspond donc à $z=\Phi^{-1}(1-q)=-\Phi^{-1}(q)$ :
> $$\text{perte}_q=\text{LGD}\;\Phi\!\left(\frac{\Phi^{-1}(\mathrm{PD})+\sqrt{\rho}\,\Phi^{-1}(q)}{\sqrt{1-\rho}}\right).$$
> 6. On retire la perte attendue $\text{LGD}\times\text{PD}$ (car $E[p(Z)]=\mathrm{PD}$), et avec $q=99{,}9\,\%$ on obtient
> $$\boxed{K=\text{LGD}\left[\Phi\!\left(\frac{\Phi^{-1}(\mathrm{PD})+\sqrt{\rho}\,\Phi^{-1}(0{,}999)}{\sqrt{1-\rho}}\right)-\mathrm{PD}\right]}$$

Le texte réglementaire impose la valeur de $\rho$, qui dépend de la catégorie. Pour les **autres expositions de détail**, la corrélation passe de 16 % (PD très faible) à 3 % (PD élevée) selon la formule $\rho=0{,}03\,w+0{,}16\,(1-w)$, avec $w=(1-e^{-35\,\mathrm{PD}})/(1-e^{-35})$ : les très bons emprunteurs sont supposés plus sensibles à l'économie que les emprunteurs déjà fragiles, dont le défaut tient surtout à des causes individuelles. Les prêts immobiliers résidentiels ont une corrélation fixe de 15 %, le renouvelable de détail de 4 %. Pour les **entreprises**, $\rho$ varie de 12 % à 24 % (avec des constantes 50 au lieu de 35) et la formule ajoute un **ajustement d'échéance** : $K$ est multiplié par $\frac{1+(M-2{,}5)\,b}{1-1{,}5\,b}$ avec $b=(0{,}11852-0{,}05478\ln \mathrm{PD})^2$, car une créance longue est plus exposée à une dégradation de la note. Il n'y a pas d'ajustement d'échéance pour le détail, et c'est la formule **« autres expositions de détail »** que nous utiliserons pour nos prêts à la consommation.

Vérifions la démonstration, au lieu de la croire. Pour une PD de 6 %, la corrélation de détail vaut $\rho\approx 4{,}6$ %. On simule 500 000 « années » : à chacune, un facteur $Z$ est tiré, puis le nombre de défauts parmi 50 000 prêts. Le taux de perte (avec une LGD de 100 %, pour isoler le mécanisme) est alors une variable aléatoire dont on lit le quantile à 99,9 %.

```python hide-code
p_exemple = 0.06
rho_exemple = float(rho_detail_autre(p_exemple))
pertes_sim = perte_portefeuille_vasicek(p_exemple, rho_exemple, 50000, 500000, seed=1)
q_sim = float(np.quantile(pertes_sim, 0.999))
q_formule = float(k_vasicek(p_exemple, 1.0, rho_exemple)) + p_exemple
print("corrélation d'actifs rho   :", round(rho_exemple, 4))
print("perte moyenne simulée      :", round(float(pertes_sim.mean()), 4), "(PD =", p_exemple, ")")
print("quantile 99,9 % simulé     :", round(q_sim, 4))
print("quantile 99,9 % par formule:", round(q_formule, 4))
print("capital K simulé / formule :", round(q_sim - float(pertes_sim.mean()), 4), "/", round(q_formule - p_exemple, 4))
gran = {n_: round(float(np.quantile(perte_portefeuille_vasicek(p_exemple, rho_exemple, n_, 500000, seed=2), 0.999)), 3) for n_ in (100, 1000, 10000)}
print("quantile 99,9 % selon le nombre de prêts :", gran)
```
<!--sortie-->
```text
corrélation d'actifs rho   : 0.0459
perte moyenne simulée      : 0.06 (PD = 0.06 )
quantile 99,9 % simulé     : 0.1823
quantile 99,9 % par formule: 0.1804
capital K simulé / formule : 0.1223 / 0.1204
quantile 99,9 % selon le nombre de prêts : {100: 0.22, 1000: 0.184, 10000: 0.181}
```

La simulation donne un quantile de 0,182 contre 0,180 par la formule : l'écart de 1 % tient à la **finitude** du portefeuille (50 000 prêts, pas une infinité) et à l'aléa de simulation. La formule IRB est donc exactement le quantile d'un portefeuille infiniment granulaire. Cette hypothèse a un coût : sur un portefeuille de 100 prêts, le même quantile vaut environ 0,220, il est de 0,184 pour 1 000 prêts et de 0,181 pour 10 000. **La formule ignore la concentration** : elle suppose que le risque propre à chaque emprunteur est parfaitement dilué. C'est une des raisons d'être du pilier 2.

![Distribution simulée du taux de perte d'un portefeuille homogène (PD 6 %, corrélation d'actifs 4,6 %). La perte attendue est la moyenne de la distribution ; le capital K couvre l'écart jusqu'au quantile à 99,9 %.](figures/ch04-perte-vasicek.png)

```python hide
fig, ax = plt.subplots(figsize=(7.4, 3.6))
ax.hist(pertes_sim, bins=np.linspace(0, 0.30, 90), color=style.BLEU, alpha=0.85, density=True)
moy = float(pertes_sim.mean())
ax.axvline(moy, color=style.ORANGE, lw=1.4)
ax.axvline(q_sim, color=style.ROUGE, lw=1.4)
ymax = ax.get_ylim()[1]
ax.annotate("perte attendue\n%.1f %%" % (100 * moy), xy=(moy, ymax * 0.85), xytext=(moy + 0.012, ymax * 0.88), color=style.ORANGE, fontsize=9, va="center")
ax.annotate("quantile 99,9 %%\n%.1f %%" % (100 * q_sim), xy=(q_sim, ymax * 0.55), xytext=(q_sim - 0.075, ymax * 0.55), color=style.ROUGE, fontsize=9, va="center", ha="left")
ax.annotate("", xy=(moy, ymax * 0.30), xytext=(q_sim, ymax * 0.30), arrowprops=dict(arrowstyle="<->", color=style.VIOLET, lw=1.2))
ax.text(0.145, ymax * 0.40, "capital K : perte inattendue", color=style.VIOLET, ha="center", fontsize=9)
ax.set_xlabel("taux de perte du portefeuille sur un an (LGD = 100 %)")
ax.set_ylabel("densité")
ax.set_xlim(0, 0.30)
fig.savefig("figures/ch04-perte-vasicek.png", dpi=200, bbox_inches="tight")
plt.close(fig)
```

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.2 (simuler le quantile à 99,9 % et jouer sur la granularité) et exercices 4.1 à 4.3 (la formule à la main).

### 4.1.5 Appliquer la formule à un portefeuille de prêts

Reprenons les 20 000 prêts à la consommation du chapitre 1 (une moitié de l'échantillon, sur laquelle une régression logistique estimée sur l'autre moitié a prédit une PD par prêt). L'exposition au défaut est prise à 70 % du montant initial (un encours moyen), et la LGD est la moyenne des pertes réalisées de `recouvrements.csv`, soit 46 %. Un seul appel calcule le capital de chaque prêt :

```python
pf["k"] = k_detail(pf["pd"], LGD)             # capital par euro d'exposition, formule « autres expositions de détail »
pf["rwa"] = 12.5 * pf["k"] * pf["ead"]        # actifs pondérés par le risque
```

Le portefeuille compte 135,5 M€ d'exposition, pour une PD moyenne de 5,8 %. Voici ce que disent les trois mesures.

```python hide-code
EL = (pf["pd"] * LGD * pf["ead"]).sum()
cap = (pf["k"] * pf["ead"]).sum()
rwa_irb = pf["rwa"].sum()
rwa_std = 0.75 * EAD
perte_obs = (pf["defaut"] * LGD * pf["ead"]).sum()
print("exposition au défaut (M€)            :", round(EAD / 1e6, 1))
print("perte attendue EL (M€ | % EAD)       :", round(EL / 1e6, 2), "|", round(100 * EL / EAD, 2))
print("perte réellement subie (M€)          :", round(perte_obs / 1e6, 2))
print("capital IRB K x EAD (M€ | % EAD)     :", round(cap / 1e6, 2), "|", round(100 * cap / EAD, 2))
print("RWA IRB (M€ | poids moyen)           :", round(rwa_irb / 1e6, 1), "|", round(100 * rwa_irb / EAD, 1), "%")
print("RWA standard à 75 % (M€)             :", round(rwa_std / 1e6, 1))
print("capital à 8 % : IRB / standard (M€)  :", round(0.08 * rwa_irb / 1e6, 2), "/", round(0.08 * rwa_std / 1e6, 2))
```
<!--sortie-->
```text
exposition au défaut (M€)            : 135.5
perte attendue EL (M€ | % EAD)       : 4.47 | 3.3
perte réellement subie (M€)          : 4.3
capital IRB K x EAD (M€ | % EAD)     : 7.44 | 5.49
RWA IRB (M€ | poids moyen)           : 93.0 | 68.6 %
RWA standard à 75 % (M€)             : 101.6
capital à 8 % : IRB / standard (M€)  : 7.44 / 8.13
```

La perte attendue est de 4,47 M€ (3,3 % de l'exposition) ; sur ce portefeuille, la perte réellement subie vaut 4,30 M€, tout près de la prévision (la PD du modèle est bien calibrée, point du chapitre 1). **Le capital IRB** est de 7,44 M€, soit 5,5 % de l'exposition : c'est la perte inattendue que la banque doit pouvoir absorber en plus. Le poids de risque moyen est de 68,6 %, **inférieur** aux 75 % de l'approche standard : les RWA sont de 93,0 M€ au lieu de 101,6 M€, et le capital à 8 % de 7,44 M€ au lieu de 8,13 M€. Cet avantage de 8,5 % est le **bénéfice du modèle interne** : la banque a investi dans la mesure du risque, et le régulateur l'en récompense, sous réserve qu'elle prouve que ses PD tiennent (sections 1.3 et 3.4).

Trois lectures se dégagent des chiffres.

1. **Perte attendue et capital ne se confondent pas.** La perte attendue (3,3 %) est plus petite que le capital (5,5 %) mais du même ordre. Toutes deux se paient : la première dans le prix du crédit et les provisions, la seconde dans le coût du capital.
2. **Le capital est une fonction concave de la PD, pas proportionnelle.** Multiplier toutes les PD par 1,5 fait passer la perte attendue de 3,3 % à 4,95 % (+50 %) mais le capital de 5,5 % à 6,0 % (+9 %) ; avec un facteur 2, la perte attendue double (6,5 %) alors que le capital ne gagne que 15 % (6,3 %). C'est la conséquence de la corrélation, qui **décroît** avec la PD : un emprunteur plus risqué est moins corrélé aux autres. En revanche, la somme « perte attendue + capital » monte presque comme la PD : une dégradation du portefeuille se paie surtout en provisions.
3. **La LGD est proportionnelle.** Le capital vaut 3,6 % de l'exposition avec une LGD de 30 %, 5,5 % avec 46 % et 7,2 % avec 60 % : une erreur de LGD se répercute telle quelle. D'où l'importance des modèles de recouvrement et de l'**exigence d'une LGD de ralentissement économique** (*downturn LGD*) : les pertes de récupération sont plus fortes **quand** les défauts sont nombreux, ce que la formule ne dit pas.

```python hide
sens = {}
for f in (1.0, 1.5, 2.0):
    p2 = np.clip(pf["pd"] * f, 0.0003, 0.9)
    sens[f] = (float(100 * (p2 * LGD * pf["ead"]).sum() / EAD), float(100 * (k_detail(p2, LGD) * pf["ead"]).sum() / EAD))
lgd_sens = {l: float(100 * (k_detail(pf["pd"], l) * pf["ead"]).sum() / EAD) for l in (0.30, 0.46, 0.60)}
homog = float(k_detail(pf["pd"].mean(), LGD))
print("sensibilité PD (EL%, K%) :", {f: (round(a, 2), round(b, 2)) for f, (a, b) in sens.items()})
print("sensibilité LGD (K%)     :", {l: round(v, 2) for l, v in lgd_sens.items()})
print("K homogène (PD moyenne)  :", round(100 * homog, 2), "| rho :", round(float(rho_detail_autre(pf['pd'].mean())), 4))
```
<!--sortie-->
```text
sensibilité PD (EL%, K%) : {1.0: (3.3, 5.49), 1.5: (4.95, 5.97), 2.0: (6.48, 6.31)}
sensibilité LGD (K%)     : {0.3: 3.58, 0.46: 5.49, 0.6: 7.16}
K homogène (PD moyenne)  : 5.52 | rho : 0.047
```

Notre portefeuille hétérogène (5,49 % de capital) est très proche de celui d'un portefeuille « homogène » où tous les prêts auraient la PD moyenne (5,52 %). La concavité de $K$ en PD aurait pu faire croire à un écart plus grand ; ici, les deux effets (prêts très sûrs de forte corrélation, prêts risqués de faible corrélation) se compensent presque.

![Poids de risque (capital × 12,5) selon la PD, pour une LGD de 45 %. La courbe des entreprises est supérieure à celle du détail : corrélation plus forte, plus l'ajustement d'échéance (M = 2,5 ans).](figures/ch04-poids-risque.png)

```python hide
ps = np.logspace(-3.3, np.log10(0.30), 120)
fig, ax = plt.subplots(figsize=(7.4, 3.8))
ax.plot(ps * 100, 12.5 * k_detail(ps, 0.45) * 100, color=style.BLEU, lw=1.8)
ax.plot(ps * 100, 12.5 * k_entreprise(ps, 0.45) * 100, color=style.ORANGE, lw=1.8)
ax.plot(ps * 100, 12.5 * k_vasicek(ps, 0.45, 0.15) * 100, color=style.AQUA, lw=1.8)
ax.axhline(75, color=style.MUET, lw=1.0, ls="--")
ax.text(0.052, 79, "approche standard : 75 % (détail)", color=style.MUET, fontsize=8.5)
ax.text(2.4, 36, "détail, autres expositions", color=style.BLEU, fontsize=9)
ax.text(0.06, 108, "entreprises (M = 2,5 ans)", color=style.ORANGE, fontsize=9)
ax.text(3.2, 255, "immobilier résidentiel\n(corrélation 15 %)", color=style.AQUA, fontsize=9)
ax.set_xscale("log")
ax.set_xlabel("probabilité de défaut PD (%, échelle logarithmique)")
ax.set_ylabel("poids de risque (%)")
ax.set_ylim(0, 300)
fig.savefig("figures/ch04-poids-risque.png", dpi=200, bbox_inches="tight")
plt.close(fig)
```

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.1 (le capital IRB d'un portefeuille, de la PD au poids de risque) et exercices 4.4 à 4.5.

### 4.1.6 Ce que la formule suppose, et où elle se trompe

Le capital IRB est un **chiffre très précis posé sur des hypothèses très fortes**. Les voici, avec le chapitre qui les met à l'épreuve.

- **Un seul facteur.** Toutes les corrélations passent par un unique facteur $Z$. Une économie réelle a des secteurs, des régions, des cycles différents ; un portefeuille concentré sur un secteur est plus risqué que ne le dit la formule (pilier 2).
- **Une corrélation imposée.** Le texte fixe $\rho$ ; la vraie corrélation de votre portefeuille est inconnue, et elle augmente typiquement en crise (c'est ce que fait le régime de stress des rendements simulés du volume, `rendements_marche.csv`). Une corrélation de 4,6 % au lieu de 8 % ne fait pas la même perte au quantile 99,9 %.
- **Une PD « à travers le cycle ».** La formule suppose une PD moyenne sur le cycle économique ; si votre modèle prédit une PD **instantanée** (*point in time*) qui grimpe en récession, le capital exigé **monte justement quand les fonds propres sont rares** : c'est la **procyclicité**. Le coussin contracyclique et les PD lissées sont des réponses. L'application 4.3 du cahier la mesure sur les 80 trimestres de `taux_defaut_macro.csv`.
- **Un portefeuille infiniment granulaire.** On a vu que 100 prêts changent beaucoup le quantile.
- **Un seul horizon et un seul seuil.** 99,9 % sur un an est une convention. Un quantile ne dit rien de la perte **au-delà** : c'est la limite de la valeur en risque que corrige la perte attendue conditionnelle de la section 3.1.
- **Des paramètres estimés.** PD, LGD et EAD sont des estimations avec leurs incertitudes ; le capital en hérite (une erreur de 20 % sur la LGD est une erreur de 20 % sur le capital). Leur **validation** (calibration des PD, test rétrospectif) est une exigence du cadre : section 1.3 et section 3.4.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.3 (la procyclicité du capital, mesurée sur 80 trimestres).

> ⚠️ **Piège.** Dire « notre capital est de 7,4 M€, donc nous sommes sûrs à 99,9 % » est faux : cela signifie que **si le modèle à un facteur est exact, avec ces PD, ces LGD et ces corrélations**, la perte dépassera le capital moins d'une année sur mille. Chaque « si » est une source de risque de modèle. Le régulateur le sait ; c'est pourquoi le cadre ajoute des **planchers** (section 4.4), un **ratio de levier** qui ne dépend d'aucun modèle, et le pilier 2.

> ✅ **À retenir.**
> - Le capital couvre la **perte inattendue** (quantile à 99,9 % moins perte attendue) ; les provisions couvrent la perte attendue.
> - $\text{RWA}=12{,}5\,K\,\text{EAD}$ et le capital minimal vaut 8 % des RWA (plus les coussins).
> - La formule IRB est le quantile d'un portefeuille infiniment granulaire dans un **modèle à un facteur** : $K=\text{LGD}\,[\Phi((\Phi^{-1}(\mathrm{PD})+\sqrt\rho\,\Phi^{-1}(0{,}999))/\sqrt{1-\rho}) - \mathrm{PD}]$ ; elle se démontre et se vérifie par simulation.
> - Sur notre portefeuille de prêts : perte attendue 3,3 %, capital 5,5 %, poids de risque 68,6 % contre 75 % en approche standard.
> - Le capital est concave en PD, proportionnel en LGD, et dépend de la corrélation imposée : un chiffre précis, des hypothèses fortes.
