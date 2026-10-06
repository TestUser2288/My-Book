# Chapitre 4 : Cadre réglementaire

> « Un capital n'est pas une réserve de précaution : c'est le prix de la survie les jours où tout va mal. »

Les trois premiers chapitres vous ont appris à **chiffrer un risque** : une probabilité de défaut (chapitre 1), un prix et une provision d'assurance (chapitre 2), une perte extrême à un seuil donné (chapitre 3). Ce chapitre répond à une question que se posent tôt ou tard tous les modélisateurs de ce métier : **qui impose ces chiffres, qui les contrôle, et pourquoi ?** Une banque et une mutuelle d'assurance ne sont pas des entreprises comme les autres. Elles gardent l'argent d'autrui, elles promettent de le rendre ou de payer un sinistre **des années plus tard**, et leur faillite coûte cher à des personnes qui n'ont aucun moyen de la prévoir. Les autorités fixent donc des règles : combien de **fonds propres** détenir face aux risques pris, **comment mesurer** ces risques, et **quoi publier**.

La banque et la mutuelle de ce livre sont fictives : aucune entité, aucun régulateur, aucun pays particulier n'apparaît. Nous étudions des **cadres internationaux**, par leur logique et leurs formules : le cadre de Bâle pour les banques, un régime de type Solvabilité II pour les assureurs, les normes comptables IFRS 9 et IFRS 17, les principes du Takaful (l'assurance fondée sur la mutualisation, conforme à la finance islamique), et la lutte contre le blanchiment. Pour chacun, l'objectif est le même : que vous sachiez **ce que mesure le texte, quelles hypothèses il cache, comment le calculer sur un exemple et ce qu'il laisse volontairement de côté**.

> ⚠️ **Ce chapitre n'est pas un conseil.** Rien de ce chapitre ne constitue un conseil juridique, comptable ou financier. Les textes réglementaires changent, leur transposition varie d'un pays à l'autre, et les valeurs numériques que nous utilisons (coefficients, seuils, matrices de corrélation) sont des **valeurs d'illustration** ou des ordres de grandeur, établies d'après l'état des textes tel que nous le connaissons à la rédaction (2026). Pour toute décision réelle, **lisez le texte en vigueur dans votre juridiction** et faites valider vos calculs par les personnes responsables. Les mêmes précautions valent pour les chapitres facultatifs.

## Le chemin de ce chapitre

- **4.1 Cadre de Bâle** : pourquoi un capital réglementaire, les trois piliers, les actifs pondérés par le risque, et la **formule des notations internes**, démontrée à partir d'un modèle à un facteur puis vérifiée par simulation, puis appliquée au portefeuille de prêts du chapitre 1.
- **4.2 Cadre Solvabilité** : le bilan « économique » d'un assureur, la meilleure estimation et la marge de risque, le **capital de solvabilité requis** agrégé par une matrice de corrélation, et ce que vaut cette agrégation.
- **4.3 Principes du Takaful** : l'assurance par partage mutuel du risque, ses deux fonds, sa gouvernance, et ce qui change (et ne change pas) pour le modélisateur.
- ➕ **4.4 IFRS 17, Bâle III finalisé et paysage national** : comment un contrat d'assurance entre dans les comptes, un plancher de capital qui limite les modèles internes, et comment aborder un cadre national **sans le nommer**.
- ➕ **4.5 Takaful et finance islamique** : l'excédent technique, les modèles wakala et moudaraba comparés sur des données, le déficit et le prêt sans intérêt, et les contrats de finance islamique usuels.
- ➕ **4.6 Lutte contre le blanchiment et analytique de la fraude** : règles, graphes, détection d'anomalies et apprentissage supervisé sur des transactions simulées, avec leurs charges d'alertes.

Chaque section peut se lire seule pour son idée principale ; les calculs réutilisent les modèles des chapitres précédents sans en dépendre : **tout est recalculé ici**.

> 📦 **Données de ce chapitre.** Trois jeux **simulés**, avec une vérité connue (voir l'introduction du volume) : `credits_conso.csv` (40 000 prêts, défaut à 12 mois) et `recouvrements.csv` (pertes réalisées sur 6 000 défauts) pour le capital des banques ; `takaful_fonds.csv` (trois fonds suivis sur quinze ans : cotisations, sinistres, frais de gestion, rendement) pour la section Takaful ; `transactions_lab.csv` (110 000 transactions de 3 000 comptes), `comptes_lab.csv` et `verite_lab.csv` pour le blanchiment. Les schémas suspects de ce dernier jeu sont **programmés**, donc plus nets que dans la réalité : les performances mesurées sont **optimistes**, et le texte le rappelle chaque fois.


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


> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.2 (simuler le quantile à 99,9 % et jouer sur la granularité) et exercices 4.1 à 4.3 (la formule à la main).

### 4.1.5 Appliquer la formule à un portefeuille de prêts

Reprenons les 20 000 prêts à la consommation du chapitre 1 (une moitié de l'échantillon, sur laquelle une régression logistique estimée sur l'autre moitié a prédit une PD par prêt). L'exposition au défaut est prise à 70 % du montant initial (un encours moyen), et la LGD est la moyenne des pertes réalisées de `recouvrements.csv`, soit 46 %. Un seul appel calcule le capital de chaque prêt :

```python
pf["k"] = k_detail(pf["pd"], LGD)             # capital par euro d'exposition, formule « autres expositions de détail »
pf["rwa"] = 12.5 * pf["k"] * pf["ead"]        # actifs pondérés par le risque
```

Le portefeuille compte 135,5 M€ d'exposition, pour une PD moyenne de 5,8 %. Voici ce que disent les trois mesures.

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


Notre portefeuille hétérogène (5,49 % de capital) est très proche de celui d'un portefeuille « homogène » où tous les prêts auraient la PD moyenne (5,52 %). La concavité de $K$ en PD aurait pu faire croire à un écart plus grand ; ici, les deux effets (prêts très sûrs de forte corrélation, prêts risqués de faible corrélation) se compensent presque.

![Poids de risque (capital × 12,5) selon la PD, pour une LGD de 45 %. La courbe des entreprises est supérieure à celle du détail : corrélation plus forte, plus l'ajustement d'échéance (M = 2,5 ans).](figures/ch04-poids-risque.png)


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


```python
charges = np.array([110, 20, 30, 45, 140.])         # M€ : marché, défaut, vie, santé, non-vie
bscr = agreger(charges, corr)                        # racine de c' R c
```

Le résultat est un SCR de base de 241,8 M€ pour une somme de 345 M€ : la diversification retire **103,2 M€**, soit près de 30 %. On ajoute le capital pour le **risque opérationnel** (12 M€ ici) et on obtiendrait, dans le texte complet, un ajustement pour la capacité d'absorption des pertes par les provisions et les impôts différés, que nous omettons : le **SCR vaut 253,8 M€**. Le **ratio de solvabilité** est le rapport des fonds propres éligibles au SCR : $333{,}5/253{,}8 \approx 131{,}4$ %. Au-dessus de 100 %, l'exigence est respectée ; en dessous, l'autorité demande un plan de rétablissement.

![Du total des modules au capital de solvabilité requis : la diversification entre modules retire environ 30 % de la somme des charges ; le risque opérationnel s'y ajoute. La ligne marque les fonds propres éligibles de la mutuelle fictive.](figures/ch04-scr-cascade.png)


> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.4 (agréger les modules et mesurer la diversification) et exercice 4.6 (un SCR à trois modules, à la main).

### 4.2.5 Que vaut l'agrégation par corrélations ?

La racine d'une forme quadratique n'est pas arbitraire : elle est **exacte** dans un cas précis.

> 📐 **Quand la formule d'agrégation est exacte.** Si les pertes des modules suivent une loi **normale multivariée**, de corrélations $R$ et d'écarts-types $\sigma_i$, la perte totale est normale, d'écart-type $\sqrt{\sigma^\top R\,\sigma}$. Son quantile à 99,5 % est $z\sqrt{\sigma^\top R\,\sigma}$ avec $z=\Phi^{-1}(0{,}995)\approx2{,}576$. Or la charge de chaque module est son propre quantile à 99,5 % : $\text{SCR}_i=z\,\sigma_i$. Donc le quantile de la perte totale vaut $\sqrt{c^\top R\,c}$ avec $c_i=z\sigma_i$, qui est exactement la formule de la formule standard.

Mais les risques d'assurance ne sont pas normaux. Pour mesurer l'écart, on simule les cinq modules sous trois hypothèses, en **imposant à chacun la même charge isolée** (le même quantile à 99,5 %, donc les mêmes 110, 20, 30, 45, 140) :

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


## 4.3 Principes du Takaful

Le **Takaful** est une forme d'assurance conçue pour respecter les principes de la finance islamique. Le mot arabe désigne la **garantie mutuelle** : des personnes s'engagent à s'entraider en cas de sinistre, au moyen d'un fonds commun. Cette section présente les principes, la structure à deux fonds, la gouvernance et ce qui change pour le modélisateur. Elle ne demande aucune connaissance religieuse : nous décrivons une **organisation** et ses conséquences financières, telles que les textes professionnels et les opérateurs les décrivent, en signalant que **les pratiques varient d'un pays, d'une école juridique et d'un comité de supervision à l'autre**.

### 4.3.1 Pourquoi une assurance « différente »

Trois interdits structurent la finance islamique, et les deux premiers touchent directement l'assurance classique telle qu'elle est comprise par les spécialistes de ce droit.

- **Le *riba*** : l'intérêt, c'est-à-dire un gain tiré du simple prêt d'argent. Une grande partie des placements d'un assureur classique (obligations, dépôts rémunérés) en est donc écartée.
- **Le *gharar*** : l'incertitude excessive sur l'objet ou le prix d'un échange. Dans une assurance classique, l'assuré paie une prime certaine contre une indemnité incertaine, ce qui est analysé comme un échange entaché d'incertitude.
- **Le *maysir*** : le jeu de hasard, c'est-à-dire un gain qui ne dépend que de la chance.

Le Takaful répond en **changeant la nature du contrat**. Les participants ne **vendent** pas un risque à une compagnie ; ils **versent une contribution**, comprise comme une **donation** (*tabarru'*) à un fonds commun, destinée à indemniser ceux d'entre eux qui subiront un sinistre. L'incertitude n'est plus celle d'un échange commercial mais d'un **geste d'entraide** ; la société qui gère n'est pas l'assureur mais un **opérateur** rémunéré pour sa gestion. Le placement des sommes se fait dans des actifs conformes (pas d'intérêt, pas d'activités interdites).

### 4.3.2 Deux fonds, deux logiques

Toute la mécanique repose sur la séparation de deux patrimoines.

![Les deux fonds du Takaful. Les cotisations des participants alimentent le fonds des participants, qui paie les sinistres ; l'opérateur est rémunéré pour sa gestion et avance, en cas de déficit, un prêt sans intérêt.](figures/ch04-takaful-fonds.png)


- Le **fonds des participants** reçoit les cotisations, paie les sinistres, détient la réserve technique et reçoit les revenus de ses placements. **Il appartient collectivement aux participants** : l'opérateur n'en est ni propriétaire ni débiteur.
- Le **fonds de l'opérateur** (ou des actionnaires) regroupe le capital de la société de gestion. L'opérateur reçoit une **rémunération** : des frais d'agence (**wakala**, du mot « mandat »), une part du profit des placements (**moudaraba**, partenariat où l'un apporte le capital et l'autre le travail), ou une combinaison (modèle hybride). La section 4.5 détaille ces modèles et les calcule sur des données.

Que se passe-t-il quand le fonds des participants ne suffit plus, c'est-à-dire quand les sinistres excèdent les cotisations et la réserve ? Dans le modèle le plus courant, **les participants ne sont pas rappelés pour payer davantage** (d'autres conventions existent, selon les opérateurs) : l'opérateur avance au fonds un **prêt sans intérêt** (*qard hassan*), remboursé sur les excédents futurs. Et quand le fonds dégage un excédent ? Il revient **aux participants**, sous forme d'une réduction de la cotisation ou d'une distribution, ou il est conservé en réserve, selon les règles de l'opérateur validées par son comité de supervision ; **jamais directement à l'opérateur** comme ferait un assureur commercial qui garde le résultat technique.

Un chiffrage minimal fixe les idées. Un fonds reçoit 1 000 de cotisations et paie 700 de sinistres. Avec un modèle wakala à 20 %, l'opérateur prélève 200 ; l'**excédent technique** est $1\,000-700-200=100$ (hors placements), partagé entre participants et réserve. Si les sinistres avaient été de 850, le déficit serait de 50 : l'opérateur prête 50 au fonds, qui le lui rendra sur ses excédents futurs.

### 4.3.3 Gouvernance charia et placements

Pour qu'un produit soit reconnu conforme, une **instance de supervision charia** (un comité de juristes-théologiens) approuve les **contrats**, les **documents commerciaux**, la **politique de placement** et les **règles de répartition de l'excédent**, puis un **audit** vérifie leur application. Les placements sont **filtrés** : ni dette portant intérêt, ni secteurs exclus (alcool, jeux, armement, selon les normes retenues), avec des **seuils** sur le niveau d'endettement et la part de revenus non conformes. Ces seuils **varient selon les normes** suivies par chaque opérateur : nous n'en citons aucun.

La **réassurance** a son équivalent, le **retakaful** : un opérateur de Takaful se protège auprès d'un opérateur de retakaful, avec la même logique de partage.

### 4.3.4 Comparer assurance commerciale, mutuelle et Takaful

| | Assurance commerciale | Mutuelle d'assurance | Takaful |
|---|---|---|---|
| Qui porte le risque ? | la compagnie (actionnaires) | l'ensemble des adhérents | l'ensemble des participants (fonds commun) |
| Nature du paiement | prime (prix du transfert de risque) | cotisation (parfois révisable) | contribution (tabarru'), donation à un fonds |
| Résultat technique | revient aux actionnaires | aux adhérents (ristourne, réserves) | aux participants (réduction, distribution, réserves) |
| Rôle de la société de gestion | assureur | assureur mutualiste | opérateur rémunéré pour sa gestion |
| Placements | tous types autorisés | tous types autorisés | seuls des actifs conformes |
| Gouvernance spécifique | conseil, fonctions clés | assemblée des adhérents | + comité de supervision charia et audit |
| Déficit | capital de l'assureur | appel de cotisation ou réserves | prêt sans intérêt de l'opérateur, remboursé ensuite |

> 💡 **Ce qui change pour le modélisateur, et ce qui ne change pas.** Les **mathématiques actuarielles du chapitre 2 s'appliquent sans changement** : on modélise la fréquence et la sévérité, on construit une **prime pure**, on provisionne par chain ladder, on mesure le risque par une valeur en risque. Ce qui change, ce sont **trois choses** : *qui possède l'excédent* (donc qui bénéficie d'une meilleure tarification), *qui supporte le déficit* (donc comment sont calculés le capital de l'opérateur et le besoin de prêt), et *quels actifs sont admis* (donc quelle courbe de rendement alimente l'actualisation). La section 4.5 chiffre le premier point et le deuxième.

Côté contrôle prudentiel, les opérateurs de Takaful sont généralement soumis à un régime de solvabilité, mais **la manière d'appliquer les exigences de capital aux deux fonds** (le fonds des participants a-t-il son propre capital ? l'opérateur doit-il couvrir son déficit ?) **dépend de chaque juridiction** : nous n'en dirons pas plus, et vous inviterons à lire le texte local.

> ⚠️ **Piège : confondre les rôles.** L'opérateur n'est pas le propriétaire des cotisations. Dans un modèle de simulation, mélanger les deux fonds (par exemple calculer le résultat « de la compagnie » comme cotisations moins sinistres) revient à décrire une assurance commerciale. Gardez **deux comptes séparés**, et ne faites jamais disparaître le prêt sans intérêt : il est une dette du fonds envers l'opérateur.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : exercice 4.10 (le niveau de frais qui équilibre l'opérateur) et application 4.7 (comparer les modèles sur un fonds).

> ✅ **À retenir.**
> - Le Takaful remplace l'échange prime/indemnité par une **contribution à un fonds commun** (tabarru') géré par un **opérateur rémunéré** ; il écarte l'intérêt, l'incertitude excessive et le jeu.
> - Deux patrimoines séparés : **fonds des participants** (cotisations, sinistres, excédent) et **fonds de l'opérateur** ; le déficit est comblé par un **prêt sans intérêt**, l'excédent revient aux participants ou aux réserves.
> - Une **instance charia** approuve contrats et placements ; les placements sont filtrés.
> - Pour le modélisateur, la **technique actuarielle est identique** ; la différence est dans la propriété de l'excédent, la prise en charge du déficit et les actifs admis.
> - Les pratiques réelles varient : lisez le texte et l'avis de la gouvernance locale.


## 4.4 ➕ Pour aller plus loin : IFRS 17, Bâle III finalisé et paysage national

> 🧭 **Section optionnelle.** Elle prolonge les deux sections précédentes par trois pièces du paysage : comment un contrat d'assurance **entre dans les comptes** (IFRS 17, avec son pendant IFRS 9 pour les banques), le **plancher de capital** qui borne les modèles internes (la finalisation de Bâle III, qu'on appelle parfois « Bâle IV »), et la manière de **se repérer dans un cadre national** quand on ne vous en donne pas le texte. Comme partout dans ce chapitre : ordres de grandeur et logique, **à vérifier dans les textes en vigueur**.

### 4.4.1 IFRS 17 en une page

Pendant des années, la norme comptable internationale sur les contrats d'assurance (IFRS 4) laissait chaque pays garder ses pratiques : deux assureurs aux contrats identiques pouvaient publier des résultats incomparables. **IFRS 17**, appliquée depuis 2023 dans les pays qui suivent ces normes, fixe un modèle unique. Son idée est simple à énoncer :

> 💡 **L'idée d'IFRS 17.** Un assureur ne gagne pas sa marge **le jour où il vend** le contrat, mais **au fil du temps où il fournit la couverture**. Au départ, on mesure ce que le groupe de contrats devrait coûter (flux de trésorerie futurs actualisés, plus un ajustement pour le risque non financier) ; si les primes dépassent ce coût, la différence n'est pas un profit immédiat : elle est stockée dans une **marge sur services contractuels** (*contractual service margin*, CSM), qui est **libérée en résultat à mesure que le service est rendu**. Si le coût dépasse les primes, le contrat est **déficitaire** et **la perte est comptabilisée immédiatement**.

Les ingrédients, dans l'ordre :

- Les **flux de trésorerie d'exécution** : valeur actuelle des flux futurs attendus (primes, sinistres, frais ; c'est la meilleure estimation de la section 4.2) plus un **ajustement pour risque** (*risk adjustment*), qui rémunère l'incertitude non financière (il n'est pas calculé comme la marge de risque de la section 4.2 ; chaque assureur choisit sa méthode et doit publier le niveau de confiance qu'elle implique).
- La **CSM** : prime reçue moins flux d'exécution à l'origine. Elle ne peut pas être négative.
- La **libération** de la CSM par **unités de couverture** : une part égale à la couverture fournie sur la période divisée par la couverture totale restante.
- Un **modèle général** (blocs de construction), une **approche simplifiée de répartition des primes** (permise notamment pour les couvertures d'un an ou moins) et une **approche à honoraires variables** pour les contrats à participation directe.
- Une **présentation** du compte de résultat en deux étages : un **résultat des services d'assurance** (produits d'assurance moins charges de services) et un **résultat financier**.

**Un exemple à la main.** Un groupe de contrats d'une couverture de trois ans encaisse 100 de primes à la souscription. Les sinistres attendus valent 70 en valeur actuelle, l'ajustement pour risque est de 8 (pour garder un calcul lisible, nous prenons un taux d'actualisation nul, ce que la norme n'autorise évidemment pas). Les flux d'exécution sont donc de $70+8=78$ et la CSM initiale est de $100-78=22$. Si la couverture est constante, la CSM est libérée par tiers : $22/3\approx7{,}33$ par an. Chaque année, le **produit d'assurance** est la somme de trois éléments : les sinistres attendus libérés ($70/3\approx23{,}33$), l'ajustement pour risque libéré ($8/3\approx2{,}67$) et la CSM libérée ($7{,}33$), soit $33{,}33$ : exactement le tiers de la prime, comme dans une comptabilité traditionnelle. Si les sinistres de l'année sont ceux attendus (23,33), le résultat des services est de $33{,}33-23{,}33=10$ chaque année.

Ce qui change, c'est le traitement d'une **mauvaise surprise**. Supposons que les sinistres de la première année soient de 28 au lieu de 23,33 (un écart d'expérience de 4,67 qui se paie **immédiatement** en résultat), et qu'à la fin de l'année on révise de 6 la valeur actuelle des sinistres **futurs**. Ce second écart concerne le service **futur** : il **ajuste la CSM** (qui passe de 14,67 à 8,67) au lieu de passer en résultat, et sera libéré sur les deux années restantes. Le tableau, calculé ci-dessous, le retrace.

```text
CSM initiale : 22.0 | libération sans surprise : 7.33 par an
produit d'assurance par an (sinistres attendus + ajustement + CSM) : 33.33
 année  CSM d'ouverture (après ajustement)  libération de la CSM
     1                               22.00                  7.33
     2                                8.67                  4.33
     3                                4.33                  4.33
CSM totale libérée : 16.0 = 22 - 6
variante déficitaire (sinistres attendus 95) : perte immédiate de 3.0 ; CSM = 0
```

L'année 1 passe en résultat la surprise de 4,67 (le produit reste de 33,33 mais les charges de sinistres sont de 28), tandis que la révision de 6 diminue la CSM et **étale** son effet sur les années 2 et 3 : la libération n'est plus que de 4,33 par an au lieu de 7,33. Les résultats sont ainsi **lissés** pour les écarts futurs, mais **jamais pour les écarts passés**. Quant au contrat déficitaire (sinistres attendus de 95, donc des flux d'exécution de 103 pour une prime de 100), il engendre une **perte de 3 dès la souscription**, sans CSM.

> ⚠️ **Piège : la CSM n'est pas une provision de prudence.** Elle n'est pas là pour absorber les mauvaises surprises passées. Elle représente un profit **futur** non gagné, et elle se réduit ou se consume avec les changements d'hypothèses sur le futur. Une CSM qui fond n'est pas un incident comptable : c'est le signal que les hypothèses de tarification (chapitre 2) étaient trop optimistes.

Pour le modélisateur, IFRS 17 déplace le travail des projections vers des **groupes de contrats** (par portefeuille, par rentabilité attendue, par année de souscription), exige des **flux actualisés** et des **ajustements pour risque** documentés, et rapproche les équipes actuarielles et comptables : les hypothèses que la section 2.2 utilise pour tarifer, la section 2.5 pour provisionner et la section 4.2 pour le bilan économique **doivent désormais être cohérentes**.

### 4.4.2 IFRS 9 et ses rapports avec le capital

La norme **IFRS 9**, qui régit les instruments financiers (donc les prêts), impose de provisionner les **pertes de crédit attendues** (section 1.5) : douze mois de pertes pour les prêts sains, **pertes à maturité** pour ceux dont le risque s'est fortement dégradé. Cette « perte attendue comptable » a un cousin, la **perte attendue réglementaire** de la formule IRB (PD × LGD × EAD). Les deux se ressemblent mais diffèrent par leurs conventions : la première est **prospective et ajustée à la conjoncture** (*point in time*), la seconde est calculée avec des paramètres **à travers le cycle**, et la LGD réglementaire est celle d'un ralentissement. Le cadre prudentiel **compare** les deux : si les provisions comptables sont **inférieures** à la perte attendue réglementaire, la différence est retranchée des fonds propres ; si elles sont supérieures, l'excédent peut, dans une certaine limite, y être ajouté. Retenez une règle de prudence : **ne mélangez pas les deux pertes attendues dans un même rapport** sans dire laquelle vous utilisez.

### 4.4.3 Bâle III finalisé et le plancher de capital

Après la crise financière de 2007-2008, le cadre a été renforcé par étapes (qualité et quantité des fonds propres, coussins, ratio de levier, ratios de liquidité : section 4.1) puis **finalisé** par un ensemble de réformes parfois surnommées « Bâle IV » dans la presse, dont les éléments principaux sont, à notre connaissance :

- une **approche standard révisée**, plus sensible au risque (pondérations selon la qualité de crédit, la nature de la garantie) ;
- des **restrictions sur les modèles internes** : certaines catégories d'expositions ne peuvent plus être traitées en IRB, des **planchers** s'appliquent à certains paramètres ;
- le **retrait du facteur d'échelle de 1,06** que Bâle II appliquait aux actifs pondérés calculés en IRB ;
- un **plancher de capital** (*output floor*) : les actifs pondérés d'une banque ne peuvent pas descendre sous **72,5 %** de ce qu'ils vaudraient en approche standard ;
- des révisions du risque de marché, du risque de crédit de contrepartie et du risque opérationnel, dont le calendrier d'application **varie selon les juridictions**.

Le plancher est le plus simple à illustrer. Il s'applique à l'ensemble des actifs pondérés de la banque ; pour montrer son mécanisme, imaginons une banque spécialisée dans les **très bons emprunteurs** de notre portefeuille (ceux dont la PD est inférieure à 2 %).

```text
prêts à PD < 2 % : 5383 | exposition (M€) : 30.98
RWA en IRB (M€)        : 14.82 (poids moyen 47.8 %)
RWA en standard (M€)   : 23.23
plancher 72,5 % (M€)   : 16.84
RWA retenus (M€)       : 16.84 | hausse due au plancher : 13.7 %
portefeuille entier : IRB 93.0 | plancher 73.7 -> plancher non contraignant
```

Pour ces 5 383 prêts de très bonne qualité, le modèle interne donne un poids moyen de 47,8 %, contre 75 % en standard ; le plancher à 72,5 % ramène à $0{,}725\times 75\,\% = 54{,}4\,\%$. Les actifs pondérés passent de 14,8 à 16,8 M€ : le plancher **augmente de 13,7 % les actifs pondérés** et annule près d'un quart de l'avantage du modèle interne (2,0 M€ sur 8,4 M€). Sur le portefeuille entier, en revanche, il ne joue pas (93,0 M€ en IRB contre 73,7 M€ de plancher) : le portefeuille mélange des emprunteurs de qualité très différente, et la corrélation décroissante en PD (section 4.1) fait que le modèle interne ne s'éloigne de l'approche standard que sur les **bons** emprunteurs. Le plancher est donc **un choix de politique** : il limite l'écart entre banques qui utilisent des modèles internes et celles qui utilisent l'approche standard, au prix d'un capital moins sensible au risque.

### 4.4.4 Se repérer dans un cadre national

Votre travail réel s'inscrira dans une juridiction particulière. Ce livre ne nomme volontairement aucun pays ; il vaut mieux vous donner **les questions à poser** que de fausses certitudes. Dans presque tous les pays, trois ou quatre institutions se partagent le terrain :

- une **autorité de supervision bancaire** (souvent la **banque centrale** ou un organisme rattaché) : elle agrée les banques, reçoit leurs ratios, examine leurs modèles internes ;
- une **autorité de contrôle des assurances** : elle agrée les assureurs, fixe les règles de provisionnement et de solvabilité, reçoit les rapports actuariels ;
- une **autorité des marchés** (information financière, produits d'épargne) ;
- une **cellule de renseignement financier**, qui reçoit les déclarations de soupçon (section 4.6).

> 🧭 **Liste de questions du modélisateur.** Avant de modéliser pour un cadre national, demandez : (1) *Quels textes s'appliquent à mon entité* (banque, assureur, opérateur de Takaful, entité d'un groupe) ? (2) *Le régime de capital est-il une transposition de Bâle, de Solvabilité II, ou un régime plus simple, fondé sur des ratios forfaitaires ?* (3) *Quelles normes comptables s'appliquent à mes comptes, et à quelle date ?* (4) *Qui valide mes modèles, et quelles pièces faut-il déposer (documentation, validation indépendante, backtesting : section 3.4) ?* (5) *Quelles remises périodiques (ratios, rapports actuariels, évaluation interne) et dans quels délais ?* (6) *Quels seuils de déclaration (espèces, soupçon) ?* (7) *Quelles règles propres s'appliquent au Takaful ?*

Un cadre national simple (ratios forfaitaires, sans modèle interne) n'enlève pas votre responsabilité : il **déplace** le risque de modèle de la banque vers le régulateur, et le travail du modélisateur vers la **documentation** et la **traçabilité**. Dans tous les cas, ce que l'autorité attend de vous se résume en quatre mots : **documenter, valider, versionner, reproduire** (volume IV, chapitre 4).

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.6 (la CSM d'un groupe de contrats, pas à pas) et exercice 4.9.

> ✅ **À retenir.**
> - **IFRS 17** : la marge d'un contrat d'assurance est **stockée** dans la CSM et **libérée** avec le service rendu ; une perte sur contrat déficitaire est **immédiate** ; un écart sur le **futur** ajuste la CSM, un écart sur le **passé** passe en résultat.
> - **IFRS 9** : perte attendue comptable (prospective) ≠ perte attendue réglementaire (à travers le cycle) ; ne les confondez pas.
> - **Bâle III finalisé** : approche standard révisée, restrictions sur les modèles internes, et **plancher à 72,5 %** des actifs pondérés standard ; dans notre exemple, il augmente de 13,7 % les actifs pondérés de très bons emprunteurs (près d'un quart de l'avantage du modèle interne) et ne joue pas sur le portefeuille entier.
> - Un cadre national se découvre **par des questions** ; la documentation, la validation et la traçabilité sont toujours exigées.


## 4.5 ➕ Takaful et finance islamique : l'excédent, les modèles wakala et moudaraba

> 🧭 **Section optionnelle.** La section 4.3 a présenté l'organisation du Takaful. Celle-ci fait les **comptes** : comment l'opérateur est rémunéré, ce que devient l'excédent, comment un déficit est comblé, et ce que cela change pour chacune des deux parties. Les paramètres (20 % de frais, 30 % du profit, 70 % de l'excédent distribué) sont des **valeurs d'illustration** : les contrats réels les fixent autrement et les font valider par leur comité de supervision. Le chapitre se termine par un panorama des contrats usuels de finance islamique.

### 4.5.1 L'excédent technique

On appelle **excédent technique** (ou résultat de souscription du fonds) la différence entre ce que le fonds des participants **reçoit** et ce qu'il **verse** sur l'année :

$$\text{excédent}=\underbrace{\text{cotisations}}_{\text{entrées}}-\underbrace{\text{sinistres}}_{\text{sorties}}-\underbrace{\text{rémunération de l'opérateur}}_{\text{frais ou part de profit}}+\underbrace{\text{revenus des placements}}_{\text{si les placements sont conformes}}.$$

Si l'excédent est positif, il ne revient pas à l'opérateur : il est **partagé entre les participants et la réserve**. S'il est négatif, c'est un **déficit** que l'opérateur comble par un prêt sans intérêt (*qard hassan*) qu'il récupérera sur les **excédents suivants**, avant toute distribution. Pour simuler un fonds sur quinze ans, nous suivons trois variables d'une année à l'autre : la **réserve** (excédents mis de côté), la **dette** envers l'opérateur et le **résultat de l'opérateur** (sa rémunération moins ses frais de gestion réels).

Les données sont celles de `takaful_fonds.csv` : trois fonds (famille, auto, santé) suivis de 2010 à 2024, avec pour chaque année les cotisations, les sinistres payés, les frais de gestion **réellement dépensés** par l'opérateur (10 % des cotisations, pour les trois fonds) et le rendement des placements. Les sinistres représentent en moyenne **73,6 %** des cotisations pour le fonds famille, **78,1 %** pour l'auto et **75,7 %** pour la santé, avec des fluctuations d'une année à l'autre de 4,5 à 7 points.

### 4.5.2 Le modèle wakala : une commission sur les cotisations

Dans le **wakala** (« mandat »), l'opérateur agit comme un **agent** des participants : il prélève, pour sa gestion, un pourcentage fixé à l'avance sur les cotisations. Les revenus des placements restent au fonds. Pour l'opérateur, c'est un revenu **stable** : il ne dépend pas des sinistres, et dépasse ses frais si le pourcentage dépasse le coût réel de la gestion (ici, 20 % contre 10 % : une marge de 10 % des cotisations). Pour les participants, c'est un prélèvement **certain** qui réduit l'excédent.

Le **taux d'équilibre** pour les participants est immédiat : l'excédent moyen est nul quand le taux de frais vaut $1-\overline{\text{sinistres}/\text{cotisations}}$, soit 26,4 % pour le fonds famille, **21,9 % pour l'auto**, 24,3 % pour la santé (sans les placements). Un taux de 20 % laisse donc au fonds auto **une marge moyenne de 1,9 point de cotisations seulement**, bien inférieure à la fluctuation annuelle des sinistres (4,5 points) : le fonds est en **déficit deux années sur cinq** (6 années sur 15 dans nos données).

Le wakala comporte aussi une **incitation** à surveiller : une commission proportionnelle aux cotisations récompense la **croissance** plus que la **qualité de souscription** ; certains contrats y ajoutent une **commission de performance** sur l'excédent pour réaligner les intérêts.

### 4.5.3 Le modèle moudaraba : une part du profit des placements

Dans la **moudaraba**, c'est un **partenariat** : les participants apportent le capital (leurs contributions investies), l'opérateur apporte son travail et reçoit, pour toute rémunération, **une part du profit des placements**. Ici, 30 % du revenu des placements du fonds. Le capital perd le contrôle, mais l'opérateur partage le **résultat réel**.

Le problème est de **dimension** : le revenu des placements d'un fonds d'assurance dommages est **petit** par rapport aux frais de gestion, car la réserve est faible devant les cotisations. Dans le fonds auto en moudaraba, ce revenu ne représente en moyenne que **1,7 % des cotisations** ; la part de 30 % de l'opérateur en fait **0,5 %**, face à des frais de gestion de 10 %. Les chiffres le montrent plus bas : **l'opérateur d'un moudaraba pur perd de l'argent sur les trois fonds**. C'est pourquoi la moudaraba seule est plutôt associée aux produits d'épargne (assurance vie familiale), où les placements sont le cœur du produit, et pourquoi on rencontre pour les branches dommages et santé le modèle hybride.

### 4.5.4 Le modèle hybride, le déficit et le prêt sans intérêt

Le modèle **hybride** combine les deux : un wakala **modéré** pour la souscription (12 % ici, un peu au-dessus du coût réel) et une moudaraba (30 %) pour les placements. L'opérateur couvre ses frais avec la commission, et participe à la performance financière de ce qu'il gère.

Quand un déficit dépasse la réserve, le **prêt sans intérêt** de l'opérateur (qard hassan) comble le trou, et il est remboursé **en priorité** sur les excédents suivants. Dans le fonds auto en wakala à 20 %, cela se produit **deux fois** : 0,1 M€ en 2010 et 1,5 M€ en 2013 (un déficit de 1,9 M€ pour une réserve de 0,4 M€), remboursé dès 2014. La dette est donc **faible, mais la réserve reste mince** : en 2024, le fonds ne dispose que de 1,3 M€ de réserve, soit moins de 3 % des cotisations annuelles. Ce n'est pas un matelas : c'est une fragilité que le chapitre 2 chiffrerait par un capital ou une réassurance (chapitre 6).

### 4.5.5 Comparer les trois modèles sur les données

Faisons tourner, pour chacun des trois fonds, les trois modèles avec les paramètres ci-dessus.

```text
  fonds              modèle  excédent moyen (M€)  années en déficit  prêts (M€)  distribué (M€)  résultat opérateur (M€)  réserve 2024 (M€)
famille         wakala 20 %                  2.0                  1         0.0            22.0                     43.2                8.1
famille      moudaraba 30 %                  8.1                  0         0.0            85.1                    -40.1               36.5
famille hybride 12 % + 30 %                  4.4                  0         0.0            46.5                     10.3               19.9
   auto         wakala 20 %                  1.0                  6         1.6            14.0                     75.5                1.3
   auto      moudaraba 30 %                 11.7                  0         0.0           122.9                    -71.3               52.7
   auto hybride 12 % + 30 %                  5.3                  0         0.0            55.7                     17.0               23.9
  sante         wakala 20 %                  1.7                  2         0.0            21.9                     60.4                3.1
  sante      moudaraba 30 %                 10.0                  0         0.0           105.2                    -57.9               45.1
  sante hybride 12 % + 30 %                  5.0                  0         0.0            52.5                     13.4               22.5
fonds auto, moudaraba : placements / cotisations = 0.0166 | part de l'opérateur / cotisations = 0.005
```

Trois constats se lisent dans ce tableau.

1. **Le wakala à 20 % rémunère l'opérateur** (43 à 76 M€ sur quinze ans) mais **laisse peu aux participants** : sur le fonds auto, 14 M€ distribués au total pour 755 M€ de cotisations (1,9 %), et six années en déficit.
2. **La moudaraba pure ruine l'opérateur** (−40 à −71 M€ sur quinze ans), car ses revenus ne couvrent pas ses frais ; les participants, eux, en profitent : jusqu'à 123 M€ distribués sur le fonds auto. Un contrat n'est viable que si **les deux parties peuvent y survivre**.
3. **Le modèle hybride** est un compromis : l'opérateur gagne de 10 à 17 M€, les participants reçoivent 47 à 56 M€, aucune année n'est déficitaire. Mais ce n'est pas « mieux » dans l'absolu : c'est un **partage différent du risque et du profit**.

![Fonds auto, quinze ans : en haut le résultat cumulé de l'opérateur, en bas les sommes distribuées cumulées aux participants, selon le modèle. Le wakala enrichit l'opérateur et laisse peu aux participants ; la moudaraba fait l'inverse ; l'hybride se place entre les deux.](figures/ch04-takaful-modeles.png)


> ⚠️ **Piège : des paramètres d'illustration ne sont pas des prix.** Les trois modèles ont été comparés **à paramètres fixés** (20 %, 30 %, 12 % + 30 %). Changez-les (taux de wakala à 15 % ou 25 %, part de moudaraba à 50 %) et les gagnants changent. Le bon exercice n'est pas de choisir le « meilleur modèle », mais de **trouver les paramètres pour lesquels aucune des deux parties n'est systématiquement perdante** : c'est l'objet de l'application 4.7 du cahier. N'oubliez pas non plus que nous avons simulé quinze ans d'**un seul tirage** : le résultat de l'opérateur est une variable aléatoire.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.7 (chercher les paramètres qui équilibrent les deux parties) et exercice 4.10.

### 4.5.6 Un panorama de la finance islamique

Le Takaful n'est qu'un volet : la banque islamique met en œuvre les mêmes principes dans le financement. Voici les contrats les plus fréquents, décrits en une phrase chacun.

| Contrat | Principe | Ce que la banque porte |
|---|---|---|
| ***Murabaha*** (vente à marge) | la banque achète un bien, le revend au client à son prix de revient **plus une marge connue**, payable à terme | le risque de crédit sur la créance, et le risque du bien entre l'achat et la vente |
| ***Ijara*** (location) | la banque achète un bien et le loue ; location-vente éventuelle | la propriété du bien : entretien structurel, valeur résiduelle |
| ***Moudaraba*** et ***moucharaka*** (partenariats) | financement d'un projet par partage des profits (moudaraba : la banque apporte le capital ; moucharaka : les deux apportent) | une partie du risque d'entreprise, **y compris les pertes** |
| ***Sukuk*** | certificats représentant la propriété d'un actif ou d'un flux, rémunérés par les revenus de l'actif | le risque de l'actif sous-jacent, selon la structure |

Une remarque de modélisateur. Un financement en murabaha fixe une **marge**, non un taux d'intérêt, et sa documentation, sa gouvernance et son traitement juridique sont distincts. Mais, du point de vue du **calcul financier**, un investisseur qui compare deux offres calcule toujours un **rendement actuariel** : pour un bien de 10 000 vendu 10 800 payables en 12 mensualités de 900, le rendement équivaut à environ 1,2 % par mois, soit **15,4 % par an** (le calcul d'un taux interne de rendement, que la marge « 8 % » masque parce qu'elle porte sur le capital initial et non sur l'encours restant). Quant au **risque de crédit**, il se mesure de la même façon : PD, LGD, EAD (chapitre 1) s'appliquent à une créance de murabaha, et la formule IRB de la section 4.1 aussi. La **différence** se situe ailleurs : dans le fait qu'on **ne peut pas pénaliser un retard par un intérêt** (des mécanismes comme des dons caritatifs sont utilisés), ce qui modifie le calcul de l'**exposition en cas de défaut**, et dans la difficulté d'utiliser les **dérivés de taux conventionnels** pour couvrir le risque de marge. Ces points débordent le cadre de ce livre : consultez les normes de votre comité de supervision.

> ✅ **À retenir.**
> - L'excédent du Takaful revient aux participants (distribution ou réserve), le déficit est comblé par un **prêt sans intérêt** remboursé sur les excédents ; un **fonds en wakala** doit être doté d'un taux compatible avec son ratio sinistres/cotisations.
> - **Wakala** : revenu stable pour l'opérateur, prélèvement certain pour les participants. **Moudaraba** : part du profit des placements, insuffisante pour couvrir les frais d'un fonds dommages. **Hybride** : compromis.
> - Sur nos 15 ans : wakala à 20 % → opérateur +43 à +76 M€, 6 années de déficit sur le fonds auto ; moudaraba pure → opérateur −40 à −71 M€ ; hybride → opérateur +10 à +17 M€, aucun déficit.
> - Un contrat est viable si **les deux parties** peuvent y survivre ; la technique actuarielle reste celle du chapitre 2.
> - Les contrats de finance islamique (murabaha, ijara, moudaraba, moucharaka, sukuk) se **modélisent** avec les outils du risque de crédit, mais leur **traitement** (retard, couverture) est propre à leur cadre.


## 4.6 ➕ Lutte contre le blanchiment d'argent et analytique de la fraude

> 🧭 **Section optionnelle.** Banques et assureurs sont tenus de **détecter les opérations suspectes** et de les signaler. C'est un des domaines où le modélisateur travaille le plus avec des règles écrites par des experts, et où les erreurs coûtent dans les deux sens : un criminel qui passe, ou des centaines d'honnêtes clients inutilement examinés. Nous construisons, sur des transactions **simulées**, une détection par règles, par graphes, par anomalies puis supervisée, et nous mesurons surtout une chose : **combien d'alertes humaines chaque méthode coûte**. Les schémas suspects de nos données sont programmés, donc nets : les performances que nous mesurons sont **bien meilleures que dans la réalité**.

### 4.6.1 Le blanchiment, et ce qu'on attend d'une banque

**Blanchir** de l'argent, c'est faire passer pour légitimes des fonds issus d'une activité illégale. On décrit classiquement trois étapes :

1. le **placement** : introduire l'argent liquide dans le système financier (dépôts d'espèces fractionnés) ;
2. l'**empilement** (*layering*) : multiplier les opérations pour brouiller l'origine (virements en chaîne, allers-retours, sociétés écrans) ;
3. l'**intégration** : réinjecter les fonds dans l'économie légale (achats, investissements).

Le cadre international, élaboré notamment par un organisme intergouvernemental de référence, repose sur une **approche par les risques** : l'établissement doit identifier ses risques (clients, pays, produits, canaux), appliquer une **vigilance** proportionnée (connaissance du client, avec une vigilance renforcée pour les personnes politiquement exposées et les pays à risque), **surveiller** les opérations, et **déclarer** à la cellule de renseignement financier celles qu'il **soupçonne** (déclaration de soupçon), sans prévenir le client. Certains pays imposent en outre la déclaration systématique des opérations d'espèces au-delà d'un seuil ; nous prendrons **10 000 €** comme seuil d'illustration. Le point d'ancrage de ce cadre est qu'**on ne juge pas une opération isolée : on juge un comportement dans le temps**.

Notre jeu de données contient 110 223 transactions de 3 000 comptes sur l'année 2024. Parmi ces comptes, **57** (1,9 %) suivent un schéma suspect programmé :

| Schéma | Comptes | Ce qu'on observe |
|---|---|---|
| **Fractionnement** (*smurfing*, placement) | 15 | 8 à 15 dépôts d'espèces de 9 000 à 9 900 €, en deux semaines, juste sous le seuil |
| **Relais** (empilement) | 15 | 10 à 19 petits virements entrants en trois jours, puis une sortie d'environ 95 % vers un pays à risque |
| **Aller-retour** (empilement) | 12 | 4 comptes qui se renvoient en boucle des montants presque identiques (4 000 à 8 000 €) |
| **Pays à risque** | 15 | 6 à 14 virements de 2 000 à 9 000 € vers deux pays désignés à risque |

S'y ajoutent **40 commerces légitimes** qui déposent beaucoup d'espèces, entre 5 000 et 9 990 € par dépôt, soixante fois dans l'année : ce sont les **faux positifs difficiles**, comme dans la vraie vie, car un commerçant ne se distingue d'un fractionneur que par le **rythme** et la **concentration** de ses dépôts, pas par leur montant.


### 4.6.2 Des variables par compte

Une règle de surveillance ne lit pas une transaction : elle lit le **profil d'un compte** sur une période. La première étape est donc de passer de 110 000 lignes de transactions à 3 000 lignes de comptes, avec les mesures qui traduisent les schémas redoutés : nombre de dépôts d'espèces juste sous le seuil (entre 90 % et 100 % de 10 000 €) et leur **concentration en 14 jours**, nombre maximal de virements entrants en 3 jours, sorties vers les pays à risque et leur part dans les entrées.

```python
F = variables_comptes(tx, comptes).merge(verite, on="id_compte")        # une ligne par compte
```

Le choix des variables est déjà un acte de modélisation : on y **encode ce qu'on sait** des typologies. Une variable sans fenêtre de temps (le nombre annuel de dépôts sous le seuil) et la même variable avec une fenêtre (le maximum dans 14 jours glissants) ne disent pas la même chose, comme on va le voir.

### 4.6.3 Les règles : rapides, lisibles… et myopes

Des règles à seuil sont écrites dans la langue du métier. Voici quatre règles, avec leur mesure d'efficacité : le nombre d'**alertes** qu'elles lèvent, la **précision** (part d'alertes qui sont de vrais cas), le **rappel** (part des 57 vrais cas qu'elles trouvent).

```python
r_naive   = F["n_depots_sous_seuil"] >= 5                                    # 5 dépôts sous le seuil dans l'année
r_fenetre = F["max_depots_sous_seuil_14j"] >= 5                              # 5 dépôts sous le seuil en 14 jours
r_relais  = (F["max_virements_entrants_3j"] >= 8) & (F["part_sortie_risque"] >= 0.5)
r_pays    = F["n_sorties_pays_risque"] >= 4                                  # au moins 4 sorties vers des pays à risque
```

```text
                      règle  alertes  vrais cas  faux positifs  précision  rappel
   dépôts sous seuil, année       54         16             38        0.3    0.28
dépôts sous seuil, 14 jours       15         15              0        1.0    0.26
   rafale + sortie à risque       12         12              0        1.0    0.21
 sorties vers pays à risque       15         15              0        1.0    0.26
  union des trois dernières       42         42              0        1.0    0.74
```

Le résultat est instructif. **La règle sans fenêtre** (cinq dépôts sous le seuil dans l'année) lève **54 alertes pour 16 vrais cas** : elle prend les 38 autres pour des fractionneurs, dont les commerçants légitimes, de précision 30 %. **La même règle avec une fenêtre de 14 jours** lève 15 alertes pour 15 vrais cas : les commerçants déposent souvent, mais **pas en rafale**. Un simple changement de fenêtre fait passer la charge de 38 faux positifs à zéro. Les trois autres règles ont, dans nos données simulées, une précision parfaite ; la règle de relais est plus stricte que les autres (elle exige aussi une sortie vers un pays à risque) et **manque 3 des 15 relais**. L'union des trois règles, qui visent chacune une typologie, trouve **42 des 57 cas** (rappel de 74 %) sans aucun faux positif.

Il manque 15 cas : les 12 allers-retours, que **aucune règle à seuil sur un compte** ne voit puisque chaque compte pris isolément fait des virements d'allure normale, et les 3 relais écartés par la règle stricte. **Une règle ne trouve que ce que son auteur a imaginé** ; son rappel, sur les schémas qu'on ne sait pas décrire, vaut zéro.

> ⚠️ **Piège : la précision parfaite est un artefact de la simulation.** Dans les vraies données, aucune règle n'atteint 100 % de précision : les schémas programmés ici sont aussi nets que possible et les commerces légitimes simulés n'ont que **peu de variété** de comportements. Retenez la **leçon relative** (fenêtre, typologie, schémas manqués), pas les valeurs absolues.

### 4.6.4 Les graphes : voir les relations

Un aller-retour est une **relation entre comptes**, pas une propriété d'un compte. On la voit en construisant un **graphe orienté** : un nœud par compte, une arête de A vers B pour chaque virement de A vers B. Les allers-retours forment des **cycles courts**. Piège classique : sur environ 17 700 virements entre 3 000 comptes, le graphe complet contient **tellement de chemins** qu'il existe presque toujours un cycle quelconque (un graphe aléatoire dense a une grande composante fortement connexe) ; chercher des cycles dans tout le graphe ne désigne personne. Il faut **restreindre** : ne garder que les virements d'au moins 2 000 € et chercher les cycles de longueur au plus 4.

```python
gros = tx[(tx["type"] == "virement") & (tx["sens"] == "debit") & (tx["contrepartie"] > 0) & (tx["montant"] >= 2000)]
G = nx.DiGraph(); G.add_edges_from(zip(gros["id_compte"], gros["contrepartie"]))
cycles = list(nx.simple_cycles(G, length_bound=4))
```

```text
virements retenus (>= 2 000 €) : 226 | cycles de longueur <= 4 : 3 | comptes concernés : 12
comptes de vrais anneaux trouvés : 12 sur 12 | faux positifs : 0
```

Les trois cycles trouvés réunissent **12 comptes, exactement les 12 des allers-retours programmés**, sans faux positif. Dans la vraie vie, des cycles apparaissent aussi par hasard (un loyer rendu, un remboursement entre amis), et les montants ne sont pas aussi proches ; on affinerait avec un critère de **similarité des montants** et de **proximité dans le temps**, et on examinerait aussi les comptes **voisins** des cycles. Le principe demeure : les **variables de réseau** (appartenance à un cycle, nombre de contreparties distinctes, centralité) enrichissent les variables par compte.

![Les trois cycles de quatre comptes détectés. Chaque flèche est un virement de 2 000 € ou plus, dont le montant est presque le même d'un maillon à l'autre : le signe d'un aller-retour programmé.](figures/ch04-lab-anneaux.png)


### 4.6.5 Détecter l'inconnu : les anomalies

Pour des schémas qu'on n'a pas décrits, on peut chercher des comptes **atypiques**. Une **forêt d'isolement** (volume III, section 6.3) isole les observations rares par des coupures aléatoires ; on lui donne les mêmes variables par compte, en échelle logarithmique, sans lui dire qui est suspect.

```text
forêt d'isolement : AUC 0.986 | précision moyenne 0.634
60 premiers comptes : précision 0.57 | rappel 0.6
composition des 60 premiers : {'aucun': 26, 'pays_a_risque': 14, 'relais': 12, 'fractionnement': 8}
dont profil commerce parmi les faux positifs : 26
```

L'AUC est élevée (0,986) : les suspects ont des scores plus élevés que les autres. Mais l'AUC ne dit pas ce que coûte l'examen. La **précision moyenne**, qui récompense d'avoir les vrais cas **en tête de liste**, est de 0,63, et parmi les 60 comptes les mieux classés, **seuls 57 % sont de vrais cas**, avec un rappel de 60 %. Les 26 faux positifs sont **tous des commerces** au gros volume de dépôts : l'algorithme a trouvé des comptes **atypiques**, pas nécessairement **suspects**. Il ne trouve pas non plus un seul aller-retour. La détection d'anomalies est un **complément** qui oriente des enquêtes ; elle ne remplace ni les règles ni les étiquettes.

### 4.6.6 Quand on a des étiquettes : l'apprentissage supervisé

Si l'on dispose d'**étiquettes** (ici, les 57 comptes confirmés), on peut apprendre à les reconnaître. Avec **57 cas positifs seulement**, il faut une **validation croisée stratifiée** et un modèle modeste : régression logistique et boosting à petites feuilles, évalués à chaque fois sur des comptes **non vus**.

```text
régression logistique                AUC 0.999 | précision moyenne 0.972 | 60 premiers : précision 0.90, rappel 0.95 | allers-retours trouvés : 9 sur 12
boosting                             AUC 0.997 | précision moyenne 0.969 | 60 premiers : précision 0.92, rappel 0.96 | allers-retours trouvés : 10 sur 12
boosting + appartenance à un cycle   AUC 1.000 | précision moyenne 0.995 | 60 premiers : précision 0.93, rappel 0.98 | allers-retours trouvés : 12 sur 12
```

Les deux modèles supervisés dépassent largement la forêt d'isolement : une précision moyenne d'environ 0,97 contre 0,63. Il leur échappe encore 2 à 3 allers-retours sur 12 parmi les 60 premiers comptes (9 trouvés par la régression logistique, 10 par le boosting) ; **ajouter la variable de réseau** « appartient à un cycle » les fait tous trouver (12 sur 12) et porte la précision moyenne à 0,995 : le graphe a **apporté une information** que les variables par compte n'avaient pas. Cette progression résume le raisonnement : *règles pour ce qu'on connaît, graphes pour les relations, anomalies pour l'inconnu, supervisé pour combiner*.

Ces performances sont **optimistes pour trois raisons**. D'abord les schémas sont **programmés** et nets. Ensuite les étiquettes sont ici **la vérité** ; en réalité, ce sont des décisions d'analystes (« dossier clos » ou « déclaré »), **biaisées** par les règles qui ont d'abord levé l'alerte : un modèle appris sur ces étiquettes apprend surtout les règles en place, et ne trouvera pas ce qu'elles manquaient. Enfin les criminels **s'adaptent** : un schéma détecté cesse d'être utilisé, et les données d'hier ne décrivent plus celles de demain (dérive du concept, volume IV, section 4.7).

![Rappel obtenu en fonction du nombre d'alertes examinées, selon la méthode (100 comptes examinés au plus). Avec 30 places, les méthodes supervisées et les règles atteignent le maximum possible ; la différence apparaît avec plus de capacité.](figures/ch04-lab-capacite.png)


```text
rappel avec 30 comptes examinés :
  forêt d'isolement    0.37
  boosting             0.53
  boosting + cycle     0.53
  règles (union)       0.53
rappel maximal possible avec 30 places : 0.53 (30 sur 57 cas)
```

### 4.6.7 La charge d'alertes décide

Un système de surveillance se juge à la **charge de travail** qu'il impose. Supposons que l'équipe puisse examiner **30 comptes par mois** (valeur d'illustration). Avec la forêt d'isolement, 30 comptes examinés trouvent **37 %** des 57 cas ; avec le boosting (avec ou sans graphe) comme avec l'union des règles, **53 %**, ce qui est le **maximum possible** avec 30 places (30 cas sur 57) : leurs trente premières alertes sont toutes de vrais cas. À cette capacité, les trois dernières méthodes ne se distinguent donc pas ; elles se séparent quand la capacité grandit. Avec 60 places, le rappel est de 60 % pour la forêt d'isolement, de 95 % et 96 % pour la logistique et le boosting, de 98 % pour le boosting enrichi du graphe. C'est pourquoi la **métrique opérationnelle** est le **rappel à capacité fixée** (ou la précision des $k$ premiers), pas l'AUC. Et c'est pourquoi le **seuil** n'est pas choisi par le modélisateur seul : il dépend du budget de l'équipe, du coût d'un cas manqué (amende, atteinte à la réputation) et du coût d'un examen inutile.

Quelques principes complètent la mise en œuvre :

- **Boucle de retour** : les décisions des analystes (déclaré, classé) alimentent les étiquettes de la période suivante ; sans elle, le modèle vieillit.
- **Explicabilité** : une alerte doit être accompagnée de **ses raisons** (« 11 dépôts sous le seuil en 9 jours ») : l'analyste doit justifier sa déclaration, et le régulateur demande de la justifier. Les méthodes du volume III (section 5.3) s'appliquent ; les règles sont naturellement explicables, les boosting moins.
- **Équité et vie privée** : on ne profile pas sur des caractéristiques protégées (origine, religion, nationalité utilisée comme proxy) ; on collecte et conserve le minimum de données nécessaire, avec des accès limités ; la **confidentialité** d'une alerte est stricte (interdiction d'avertir le client).
- **Réseau mondial** : la plupart des schémas traversent des établissements différents : la détection d'un seul établissement voit une partie de l'histoire, ce qui est l'une des limites structurelles du dispositif.

**Et la fraude à l'assurance ?** Même démarche, autres typologies : sinistres déclarés en rafale peu après la souscription, réseaux de garages ou de prestataires partageant les mêmes bénéficiaires, gonflement de factures. Les règles, les graphes et l'**anomalie** (volume III, chapitre 6) s'appliquent de la même manière, et la **charge d'enquêteurs** décide du seuil. Un score de fraude utilisé pour **refuser** une indemnité engage la responsabilité de l'assureur : il doit être **contestable** par l'assuré et expliqué.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.8 (règles, graphe, anomalies et supervisé, de bout en bout) et exercices 4.11 et 4.12.

> ✅ **À retenir.**
> - Le blanchiment se décrit en trois étapes (placement, empilement, intégration) ; on **juge un comportement dans le temps**, pas une opération.
> - Des **règles** lisibles prennent le métier en compte, mais elles ne trouvent que ce qu'on a imaginé : le simple ajout d'une **fenêtre de temps** a fait passer une règle de 38 faux positifs à zéro.
> - Les **graphes** détectent des relations (aller-retour) invisibles compte par compte, à condition de **restreindre** le graphe.
> - Les **anomalies** repèrent l'atypique (précision moyenne 0,63 ici) sans le qualifier de suspect ; le **supervisé** (précision moyenne 0,97, 0,995 avec le graphe) exige des étiquettes qui sont elles-mêmes biaisées.
> - Le critère opérationnel est le **rappel à capacité fixée** ; le seuil se décide avec le métier ; explicabilité, équité, confidentialité sont des exigences, pas des options.
> - Nos performances sont **optimistes** : schémas programmés et nets, étiquettes sans erreur.


## Bilan du chapitre 4

Vous savez maintenant :

- **expliquer pourquoi on réglemente** les banques et les assureurs, et distinguer la **perte attendue** (provisionnée, facturée) de la **perte inattendue** (couverte par le capital) ;
- **lire un cadre prudentiel** : les trois piliers (exigences quantitatives, surveillance, transparence), les **ratios** (fonds propres sur actifs pondérés, levier, liquidité), les **niveaux** de fonds propres et les coussins ;
- **démontrer la formule IRB** à partir d'un modèle à un facteur ($K=\text{LGD}\,[\Phi((\Phi^{-1}(\mathrm{PD})+\sqrt\rho\,\Phi^{-1}(0{,}999))/\sqrt{1-\rho})-\mathrm{PD}]$), la **vérifier par simulation**, l'**appliquer** à un portefeuille de prêts (capital 5,5 % de l'exposition, poids de risque moyen 68,6 % contre 75 % en approche standard) et dire ce qu'elle suppose ;
- **construire un bilan économique d'assureur** : meilleure estimation, marge de risque par le coût du capital, **SCR agrégé** par une matrice de corrélation (345 M€ de somme, 241,8 M€ agrégés, 253,8 M€ avec le risque opérationnel), ratio de solvabilité et chocs, en sachant que l'agrégation est **exacte pour des pertes normales** et peut être prudente ou imprudente sinon ;
- **décrire le Takaful** (contribution à un fonds commun, deux fonds, opérateur rémunéré, prêt sans intérêt, supervision charia) et **ce qu'il change pour le modélisateur** ;
- (en option) **lire IFRS 17** (CSM libérée avec le service, perte immédiate sur contrat déficitaire, écart futur contre écart passé) et situer IFRS 9, le **plancher de 72,5 %** de Bâle III finalisé, et **aborder un cadre national** par des questions ;
- (en option) **comparer les modèles wakala, moudaraba et hybride** sur des données (le wakala à 20 % rémunère l'opérateur, la moudaraba pure le ruine, l'hybride équilibre) et situer les contrats de finance islamique ;
- (en option) **détecter des opérations suspectes** : variables par compte, règles avec fenêtre de temps, cycles dans un graphe, anomalies, apprentissage supervisé, et juger par le **rappel à capacité fixée**.

Le tableau suivant résume les **cadres** vus dans ce chapitre, avec ce qu'ils mesurent et d'où ils tirent leurs entrées.

| Cadre | Pour qui | Ce qu'il fixe | Mesure de risque | Entrées de vos modèles | Où |
|---|---|---|---|---|---|
| **Bâle** (IRB) | banques | fonds propres ≥ 8 % des RWA, plus coussins ; levier ; liquidité | perte au quantile 99,9 % sur un an, moins la perte attendue | PD, LGD, EAD (ch. 1) | 4.1 |
| **Solvabilité** | assureurs | SCR (fonds propres éligibles ≥ SCR), MCR | valeur en risque à 99,5 % sur un an des fonds propres | provisions (ch. 2), mesures de risque (ch. 3) | 4.2 |
| **Takaful** | opérateurs et participants | structure à deux fonds, prêt sans intérêt, supervision charia | les mêmes que l'assurance (technique identique) | fréquence, sévérité, provisions (ch. 2) | 4.3, 4.5 |
| **IFRS 17 / IFRS 9** | comptes d'assureurs / de banques | quand et comment reconnaître marges et pertes | espérance actualisée plus ajustement pour risque ; perte de crédit attendue | flux, PD/LGD (ch. 1 et 2) | 4.4 |
| **Lutte contre le blanchiment** | banques, assureurs | vigilance, surveillance, déclaration de soupçon | pas de mesure unique : charge d'alertes, rappel | transactions, graphes, étiquettes | 4.6 |

Quatre idées dépassent ce chapitre.

**D'abord, un capital réglementaire est un quantile, donc une convention.** Le 99,9 % des banques et le 99,5 % des assureurs ne sont pas des vérités mais des **niveaux de confiance choisis**, que chaque formule entoure d'hypothèses (un seul facteur, des corrélations imposées, une granularité infinie, des modules agrégés linéairement). Lire un ratio de capital, c'est lire ses hypothèses.

**Ensuite, la mesure est toujours un calcul sur des estimations.** PD, LGD, CCF, meilleure estimation, ajustement pour risque : chacun est estimé avec une incertitude qui se propage au capital (une LGD trop optimiste de 20 % donne un capital trop faible de 20 %). Le cadre répond par des **planchers**, des exigences de **validation** (section 3.4), un **ratio de levier** indépendant des modèles, et la **documentation**.

**Puis, le même risque se lit à plusieurs niveaux.** Perte attendue comptable (IFRS 9), perte attendue réglementaire (IRB), meilleure estimation d'assureur, CSM d'IFRS 17 : des conventions différentes, pour des objectifs différents (information financière, protection des déposants, protection des assurés). Dire laquelle on utilise est une partie du travail.

**Enfin, la détection d'opérations suspectes se juge sur la charge humaine.** Une règle sans fenêtre de temps, ou un modèle sans graphe, coûte des centaines d'examens inutiles ou des relations ratées ; le critère est le **rappel à capacité fixée**, et nos performances simulées sont toujours **optimistes**.

> ⚠️ **Rappel d'honnêteté.** Ce chapitre ne nomme ni pays ni autorité ; il présente la **logique** de cadres internationaux, d'après l'état des textes connu à la rédaction (2026), avec des paramètres d'illustration (coefficients, matrice de corrélation, taux de frais, seuils). **Rien n'y est un conseil juridique, comptable ou financier** : pour une décision réelle, lisez le texte en vigueur dans votre juridiction. Les données sont simulées et leurs schémas programmés ; les performances de détection sont donc **bien plus élevées** que dans la réalité.

Les chapitres complémentaires suivants prolongent ce chapitre : le chapitre 5 construit les **tables de mortalité** qui nourrissent l'assurance vie et son provisionnement ; le chapitre 6 explique comment une mutuelle **se protège** par la réassurance (ce que le module de défaut des contreparties de la section 4.2 mesure) ; le chapitre 7 traite de la **gestion actif-passif**, qui relie le bilan économique de la section 4.2 aux placements.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 à 4.8 (le capital IRB d'un portefeuille, la simulation du quantile à 99,9 %, la procyclicité, l'agrégation du SCR, la marge de risque et les chocs, la CSM d'IFRS 17, les modèles de Takaful, la détection d'opérations suspectes) et exercices 4.1 à 4.12.
