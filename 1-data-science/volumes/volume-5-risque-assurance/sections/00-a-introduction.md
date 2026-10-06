# Introduction : pourquoi la modélisation du risque est une discipline à part

> « On ne mesure pas un risque pour le connaître, mais pour décider de ce que l'on peut se permettre de perdre. »

## Là où les volumes précédents nous ont laissés

Les quatre premiers volumes vous ont donné une boîte à outils complète : des **probabilités** et de la **statistique** (volume I), des **modèles de régression** et de **durée** (volume II), une **démarche de modélisation prédictive rigoureuse** (volume III), puis les moyens de **mettre un modèle en service et de le surveiller** (volume IV). Avec cela, vous savez construire un modèle qui prédit bien, vous savez prouver qu'il prédit bien sur des données qu'il n'a jamais vues, et vous savez le faire tourner.

Ce volume change de **question**. Jusqu'ici, nous demandions : *quelle est la meilleure prédiction ?* Nous demandons maintenant : **combien pouvons-nous perdre, avec quelle probabilité, et que faisons-nous de ce chiffre ?** Une banque qui prête de l'argent ne veut pas seulement savoir quels emprunteurs risquent de ne pas rembourser ; elle doit décider **à quel taux prêter**, **combien mettre de côté** et **combien de fonds propres conserver** pour survivre à une mauvaise année. Une mutuelle d'assurance ne veut pas seulement prédire le nombre de sinistres ; elle doit fixer une **prime**, constituer une **provision** pour des sinistres qui ne sont pas encore payés (voire pas encore déclarés), et prouver à une autorité de contrôle qu'elle pourra tenir ses engagements.

Dans ce volume, le fil conducteur n'est donc plus une boutique mais deux organisations fictives, **une banque** (un établissement de crédit) et **une mutuelle d'assurance**, sans nom et sans pays. Les montants sont en €. Les données sont, comme toujours, **simulées** avec des graines fixes, à une exception près (un jeu réel de défauts de cartes de crédit, déjà rencontré au volume III) : vous obtiendrez exactement les mêmes chiffres que dans le livre.

## Un risque, c'est une perte possible, chiffrée

### Trois ingrédients

Dans la vie courante, « risque » désigne vaguement ce qui pourrait mal tourner. En modélisation, le mot a un sens précis : un risque est une **perte possible, dont on sait chiffrer la probabilité et l'ampleur**. Il faut donc toujours trois ingrédients : un **événement** (un emprunteur ne rembourse pas, un conducteur déclare un accident, un marché s'effondre), la **probabilité** que cet événement se produise sur un horizon donné, et la **conséquence financière** s'il se produit.

Le cas du crédit est le plus simple à écrire. Pour un prêt, on note PD la **probabilité de défaut** à un an, EAD l'**exposition au défaut** (ce que la banque a prêté et n'a pas encore récupéré au moment où l'emprunteur cesse de payer) et LGD la **perte en cas de défaut** (la part de cette exposition que la banque ne récupère jamais, après garanties et recouvrement). La **perte attendue** du prêt est le produit des trois :

$$\text{EL} = \text{PD} \times \text{LGD} \times \text{EAD}.$$

Voici trois prêts, à calculer à la main :

| Prêt | EAD (€) | PD | LGD | Perte attendue (€) |
|---|---|---|---|---|
| A | 10 000 | 1 % | 45 % | 10 000 × 0,01 × 0,45 = 45 |
| B | 20 000 | 4 % | 40 % | 20 000 × 0,04 × 0,40 = 320 |
| C | 5 000 | 10 % | 60 % | 5 000 × 0,10 × 0,60 = 300 |
| **Total** | 35 000 | | | **665** |

Le prêt B est quatre fois plus risqué que A en probabilité, mais sa perte attendue est plus de sept fois supérieure : l'exposition compte autant que la probabilité. Et le prêt C, le plus petit, est presque aussi coûteux que B parce que sa probabilité de défaut et sa perte en cas de défaut sont fortes toutes les deux. Ces trois lettres, PD, LGD et EAD, structurent le chapitre 1 et reviennent au chapitre 4 dans les règles de capital.

### La perte attendue, et tout ce qu'elle ne dit pas

La perte attendue est une **moyenne**. Elle est utile : c'est elle que l'on facture dans le taux d'intérêt ou dans la prime, en considérant que, sur beaucoup de contrats, les pertes moyennes seront couvertes par les revenus. Mais une moyenne ne dit rien de ce qui arrive **une mauvaise année**, et c'est pourtant cette mauvaise année qui fait faire faillite.

Prenons un portefeuille de 10 000 prêts identiques : EAD de 10 000 €, PD de 2 %, LGD de 45 %. La perte attendue est de 10 000 × 10 000 × 0,02 × 0,45, soit 900 000 €. Imaginons deux mondes.

- **Défauts indépendants.** Chaque emprunteur défait ou non sans rien devoir aux autres. Le nombre de défauts suit alors une loi binomiale : en moyenne 200, avec un écart-type d'environ 14. Il est très improbable d'en observer beaucoup plus : même dans le pire millième des cas, on dépasse à peine 245 défauts.
- **Défauts corrélés.** Les emprunteurs partagent un **facteur commun** (la conjoncture) : quand l'économie va mal, beaucoup d'entre eux défaillent ensemble. Chacun garde sa probabilité moyenne de 2 %, mais les défauts ne sont plus indépendants.

```python hide
import numpy as np
from scipy.stats import norm, binom
import sys
sys.path.insert(0, "build")
import style
style.setup()
import matplotlib.pyplot as plt

N, EAD, PD, LGD, RHO = 10000, 10000, 0.02, 0.45, 0.15
EL = N * EAD * PD * LGD
rng = np.random.default_rng(7)
S = 100000
d_ind = rng.binomial(N, PD, S)
z = rng.standard_normal(S)
p_cond = norm.cdf((norm.ppf(PD) - np.sqrt(RHO) * z) / np.sqrt(1 - RHO))
d_cor = rng.binomial(N, p_cond)
res = {}
for nom, d in (("indépendants", d_ind), ("corrélés", d_cor)):
    perte = d * EAD * LGD
    q = np.quantile(perte, 0.999)
    res[nom] = dict(moy=perte.mean(), sd=perte.std(), q=q, es=perte[perte >= q].mean())
    print(f"{nom:13s} moyenne {perte.mean()/1e6:6.3f} M€ | écart-type {perte.std()/1e6:6.3f} | quantile 99,9 % {q/1e6:6.3f} | ES 99,9 % {res[nom]['es']/1e6:6.3f} | rapport à la perte attendue {q/EL:5.2f}")
print("perte attendue (M€) :", EL / 1e6)
print("quantile 99,9 % du nombre de défauts (loi binomiale) :", int(binom.ppf(0.999, N, PD)))
print("défauts max (indépendants) :", int(d_ind.max()), "| (corrélés) :", int(d_cor.max()))
print("part de défauts dans la limite d'un grand portefeuille, quantile 99,9 % :", round(norm.cdf((norm.ppf(PD) + np.sqrt(RHO) * norm.ppf(0.999)) / np.sqrt(1 - RHO)), 4))

fig, axes = plt.subplots(1, 2, figsize=(10, 3.4), sharey=False)
for ax, (nom, d), col in zip(axes, (("Défauts indépendants", d_ind), ("Défauts corrélés", d_cor)), (style.BLEU, style.ORANGE)):
    perte = d * EAD * LGD / 1e6
    ax.hist(perte, bins=np.linspace(0, 12, 121), color=col, alpha=0.9)
    q = np.quantile(perte, 0.999)
    ax.axvline(EL / 1e6, color=style.ENCRE, lw=1.2)
    ax.axvline(q, color=style.ROUGE, lw=1.2, ls="--")
    ax.set_title(nom)
    ax.set_xlabel("perte annuelle du portefeuille (M€)")
    ax.set_xlim(0, 12)
    ax.text(EL / 1e6 + 0.2, ax.get_ylim()[1] * 0.92, "perte attendue", fontsize=8, color=style.ENCRE, ha="left")
    ax.text(q + 0.2, ax.get_ylim()[1] * 0.70, "quantile 99,9 %", fontsize=8, color=style.ROUGE, ha="left")
axes[0].set_ylabel("nombre de scénarios")
style.save(fig, "ch00-perte-queue.png")
```
<!--sortie-->
```text
indépendants  moyenne  0.900 M€ | écart-type  0.063 | quantile 99,9 %  1.098 | ES 99,9 %  1.114 | rapport à la perte attendue  1.22
corrélés      moyenne  0.899 M€ | écart-type  0.979 | quantile 99,9 %  7.848 | ES 99,9 %  9.304 | rapport à la perte attendue  8.72
perte attendue (M€) : 0.9
quantile 99,9 % du nombre de défauts (loi binomiale) : 245
défauts max (indépendants) : 260 | (corrélés) : 3022
part de défauts dans la limite d'un grand portefeuille, quantile 99,9 % : 0.1763
figure : ch00-perte-queue.png
```

![Distribution de la perte annuelle d'un même portefeuille de 10 000 prêts (perte attendue : 0,9 M€), dans deux mondes. À gauche, défauts indépendants : tout se concentre autour de la moyenne. À droite, défauts corrélés par un facteur commun : la moyenne est la même, mais la distribution a une longue queue.](figures/ch00-perte-queue.png)

Les deux portefeuilles ont **la même perte attendue**, 900 000 €. Pourtant, dans le monde indépendant, la perte du pire millième des années est d'environ 1,1 M€, soit 22 % de plus que la moyenne ; dans le monde corrélé, elle est d'environ 7,8 M€, soit près de **neuf fois** la perte attendue. Une banque qui aurait gardé en réserve « un peu plus que la perte attendue » ferait faillite dans le second monde.

> 💡 **L'idée centrale du volume.** Ce qui menace une institution financière n'est pas la **moyenne** des pertes, mais leur **queue** : les années rares où tout va mal en même temps. On distingue donc la perte **attendue** (que l'on prévoit et que l'on facture), de la perte **inattendue** (l'écart entre une mauvaise année et la moyenne), pour laquelle on **immobilise du capital**. Mesurer cette queue (VaR, *expected shortfall*, capital réglementaire) est l'objet des chapitres 3 et 4.

Cette expérience illustre aussi une leçon de modélisation : **la corrélation n'apparaît dans aucune des données d'un seul prêt**. Un modèle qui prédit parfaitement la probabilité de défaut de chaque emprunteur pris isolément donnerait pourtant, ici, une vision complètement fausse du risque du portefeuille. Nous retrouverons ce facteur commun dans la formule de Bâle (section 4.1).

## Trois métiers, une même logique

Ce volume parcourt trois grands domaines. Ils ont des vocabulaires différents, mais la même structure : une **variable aléatoire de perte**, que l'on modélise en deux temps (combien de fois, puis combien à chaque fois, ou bien une probabilité puis un montant), et une **décision** que le chiffre éclaire.

| Domaine | Ce qui est aléatoire | Décision que le chiffre éclaire | Chapitres |
|---|---|---|---|
| **Crédit** (la banque) | le défaut d'un emprunteur, la perte qu'il laisse | accorder ou refuser un prêt, fixer son taux, provisionner, immobiliser du capital | 1, 3, 4 |
| **Assurance** (la mutuelle) | le nombre et le coût des sinistres, leur date de règlement, la durée de vie | fixer une prime, constituer des provisions, choisir une réassurance, vérifier sa solvabilité | 2, 4, 5, 6 |
| **Marchés et capital** | la valeur d'un portefeuille d'actifs, la courbe des taux, les pertes opérationnelles | mesurer un risque, simuler un choc, adosser l'actif au passif | 3, 7 |

Un même mécanisme apparaît partout : un **modèle de fréquence** (combien) et un **modèle de sévérité** (combien à chaque fois) se combinent en une **perte agrégée**, dont on étudie la queue. Pour un portefeuille de prêts, la « fréquence » est le nombre de défauts et la « sévérité » est EAD × LGD ; pour une assurance automobile, c'est le nombre de sinistres et leur coût ; pour le risque opérationnel, le nombre d'incidents et leur montant. Apprendre ce schéma une fois, c'est le retrouver dans tout le volume.

## La boucle : chiffrer, décider, valider

La modélisation du risque suit une boucle à trois temps, que chaque chapitre déroule à sa manière.

1. **Chiffrer.** Estimer une probabilité, une distribution, un coût, à partir de données. Les outils sont ceux des volumes précédents (régression logistique, GLM, séries chronologiques, méthodes d'apprentissage), mais le chiffre produit n'est pas une « prédiction » à juger au coup par coup : c'est une **estimation** d'une quantité (une probabilité, une espérance, un quantile) dont on doit connaître l'incertitude.
2. **Décider.** Transformer ce chiffre en acte : un **prix** (la prime, le taux), une **provision** (l'argent mis de côté pour une dette dont on ne connaît pas encore le montant), un **capital** (les fonds propres qui servent de coussin). Ce sont trois décisions de nature différente, et on verra que l'on ne peut pas toujours utiliser le même modèle pour les trois.
3. **Valider.** Vérifier que le chiffre **tient** : sur des données hors période, par comparaison à la réalité qui se réalise (rétro-test), par des chocs volontaires (tests de crise), par un regard indépendant (validation de modèle). Et pour des raisons de régulation, la validation n'est pas facultative.

Le volume est organisé selon cette boucle. Le chapitre 1 (crédit) et le chapitre 2 (assurance dommages) montrent comment **chiffrer** et **tarifer** ; le chapitre 3 montre comment **mesurer** une queue et la **mettre sous contrainte** ; le chapitre 4 explique le **cadre réglementaire** qui encadre les trois étapes ; les chapitres 5 à 7 prolongent l'assurance vie, la réassurance et la gestion actif-passif.

## Ce qui rend la discipline à part

Les méthodes sont celles que vous connaissez. Pourtant, quatre caractéristiques font de la modélisation du risque un métier distinct.

### Des événements rares et des queues lourdes

Les défauts, les grands sinistres, les krachs sont **rares**, et ce sont eux qui comptent. Un modèle excellent sur la grande masse des cas peut être mauvais là où cela coûte cher. L'exactitude moyenne, le critère favori du volume III, devient insuffisante : un modèle qui annonce « aucun défaut » se trompe pour 6 % des prêts de nos données, mais a 94 % d'exactitude. Les lois à queue épaisse (Pareto, lognormale, loi des valeurs extrêmes) remplacent souvent la loi normale, et les quantiles extrêmes (le pire millième) se lisent dans des données qui n'en contiennent presque pas.

### Des résultats qui arrivent tard

Un prêt consenti aujourd'hui révèle son défaut dans un an, parfois trois ; un sinistre de responsabilité civile survenu cette année peut être réglé dans douze ans ; un contrat d'assurance vie met des décennies à se dénouer. Il n'existe pas de « jeu de test » que l'on peut consulter immédiatement. On travaille donc avec des **triangles** de sinistres incomplets, des défauts observés sur une fenêtre fixe, des projections de mortalité. La réalité répond tard, et il faut décider avant.

### Des chiffres qui engagent, et qui sont encadrés

Une prime est un contrat ; une provision apparaît dans les comptes ; un capital est exigé par le régulateur. Un chiffre faux a donc des conséquences immédiates (un prix mal fixé attire les mauvais risques et fuit les bons), et le cadre réglementaire impose des méthodes, des documentations, des validations. Un modèle n'est pas seulement un outil d'analyse : c'est un objet **audité**.

### Le risque de modèle

Tout modèle est une simplification, et ce qu'il simplifie peut précisément être ce qui compte. On appelle **risque de modèle** la perte possible due à un modèle faux, mal utilisé ou mal compris. Il prend de nombreuses formes que ce volume illustre : une corrélation ignorée (l'expérience ci-dessus), une hypothèse de la méthode des triangles qui ne tient plus quand l'inflation change, un modèle de défaut excellent en période calme et médiocre en crise, une queue estimée sur trop peu de points.

> ⚠️ **Un modèle bien calibré en moyenne peut être faux là où cela compte.** La probabilité de défaut moyenne prédite peut être exacte (6 % prédit pour 6 % observé) alors que le modèle se trompe d'un facteur deux pour les plus mauvais emprunteurs, ou que sa queue sous-estime systématiquement les années de crise. Le volume insiste donc sur des vérifications **par tranches**, **hors période** et **dans les queues**.

Une particularité heureuse de ce livre : puisque nos données sont **simulées**, nous connaissons la vérité (la vraie probabilité de défaut, le vrai montant futur des sinistres, la vraie mortalité). Nous pouvons donc, ce qui est impossible dans la réalité, **comparer chaque estimation à la vérité programmée**. C'est un privilège pédagogique : en pratique, on ne saura jamais avec certitude si une provision était juste, seulement si elle s'est révélée suffisante.

## Ce que les volumes précédents vous donnent

Ce volume suppose acquis les outils suivants ; nous y renvoyons plutôt que de les refaire.

| Besoin dans ce volume | Où le retrouver |
|---|---|
| Probabilités, espérance, variance, lois usuelles, loi des grands nombres | volume I, sections 2.2 à 2.4 |
| Estimation, intervalles de confiance, tests | volume I, sections 3.2 à 3.5 |
| Régression logistique (le cœur du scoring) | volume II, section 2.2 |
| Régressions de Poisson et Gamma (fréquence, sévérité) | volume II, section 2.3 |
| Déviance, qualité d'ajustement, zéros en excès, loi de Tweedie | volume II, sections 2.4 et 2.6 |
| Séries temporelles, GARCH | volume II, chapitre 4, section 4.4 |
| Survie, censure | volume II, chapitre 5 |
| Méthodes de Monte-Carlo, théorie des valeurs extrêmes, copules | volume II, sections 6.2, 6.5 et 6.6 |
| Validation, fuite d'information, références | volume III, sections 1.1 à 1.4 |
| Métriques de classification, calibration, interprétabilité | volume III, sections 5.1 à 5.3 |
| Supervision d'un modèle en service, dérive, indice de stabilité de population (PSI) | volume IV, chapitre 4 (4.3 et 4.7) |

## Six idées qui reviennent dans tout le volume

> 💡 **Les six idées.**
> 1. **Un risque se chiffre en trois temps** : une fréquence ou une probabilité, une sévérité, une dépendance. Oublier la dépendance, c'est sous-estimer la queue.
> 2. **La moyenne se facture, la queue se capitalise.** Perte attendue et perte inattendue sont deux quantités, avec deux outils.
> 3. **Un chiffre de risque est une convention.** Une VaR à 99 % sur un jour, un capital à un an, une provision « au meilleur estimé » : chaque nombre est lisible seulement avec ses hypothèses.
> 4. **La réalité répond tard** : on valide hors période, on compare à ce qui s'est réalisé, on planifie le rétro-test.
> 5. **Prix, provision et capital sont trois décisions** : trois modèles possibles, trois horizons, trois exigences de précision.
> 6. **Le modèle lui-même est un risque.** On documente ses hypothèses, on le teste dans les queues, on le fait relire par quelqu'un d'autre.

## Comment travailler avec ce volume

### Un livre, et son cahier

Comme les volumes précédents, ce volume est publié en **deux ouvrages**. Le **livre** que vous lisez explique : intuitions, exemples calculés à la main, démonstrations, pièges. Il ne contient ni exercices ni corrigés. Le **cahier d'exercices et d'applications** contient les applications guidées, les exercices corrigés, le **projet du volume** (construire un modèle de tarification, avec validation et notes réglementaires) et l'auto-évaluation. Une ligne de ce genre termine chaque section :

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.1, exercices 1.1 à 1.4.

### Le rythme d'une section

Chaque section suit le même rythme : une **intuition**, un petit exemple **calculé à la main**, la **formalisation** (avec la démonstration quand elle éclaire), l'**application** aux données du volume, les **pièges** et un encadré **À retenir**. Les chapitres marqués ➕ sont **facultatifs** : le reste du volume ne les suppose pas.

### Le code dans ce livre

Le livre montre **très peu de code**, seulement pour obtenir un résultat avec une bibliothèque, ou quand le code est le sujet. Les formules, les algorithmes et les vérifications numériques de la prose sont exécutés **en coulisses** : chaque nombre cité a été produit par un programme. Le cahier, lui, contient le code par petites étapes.

### Des données simulées, avec la vérité programmée

Presque toutes les données sont **simulées** (script `build/donnees5.py`, graines fixes), à partir d'un mécanisme que nous connaissons. À la fin d'une étude, nous **révélons la vérité programmée** et la comparons à ce que l'estimation a trouvé. Cela ne remplace pas des données réelles : les données simulées sont plus **propres** que les vraies (peu de dépendances cachées, aucun changement de régime imprévu, aucune faute de saisie) ; les conclusions de méthode s'appliquent, les conclusions chiffrées non. Un seul jeu est **réel** : `credit_defaut.csv` (défaut de paiement de cartes de crédit, source UCI, licence CC0), utilisé dans les « détours sur données réelles ».

### Des textes réglementaires datés, et aucun conseil

Le chapitre 4 présente des cadres réglementaires (Bâle, Solvabilité, IFRS 9 et 17, principes du Takaful). Les **mécanismes** (la logique des formules, l'agrégation des risques, les trois piliers) sont stables ; les **paramètres** (seuils, coefficients, calendriers) changent. Ce livre décrit l'état des textes **tel qu'il était connu lors de la rédaction (2026)** : tout paramètre chiffré est donné à titre d'**exemple illustratif** et doit être vérifié dans les textes en vigueur dans votre juridiction. **Rien de ce volume n'est un conseil juridique, comptable, actuariel ou financier.** Les textes d'un pays ne sont jamais présentés comme universels, et aucune autorité nationale n'est nommée : les exemples parlent de « l'autorité de contrôle » ou de « la banque centrale ».

### Ce qui n'a pas pu être vérifié

Tout le code de ce volume s'exécute (sur un ordinateur ordinaire, sans carte graphique ni réseau). Deux limites sont à connaître. D'abord, aucun relecteur humain n'a relu ce volume d'un bout à l'autre : chaque nombre de la prose a été comparé aux sorties des programmes, mais des maladresses de rédaction subsistent sans doute. Ensuite, les bibliothèques spécialisées de l'actuariat et de la finance (provisionnement, optimisation de portefeuille, bibliothèques de scoring) **ne sont pas utilisées** : nous écrivons les méthodes à la main, parce que c'est le meilleur moyen de les comprendre ; en pratique, vous utiliserez souvent des outils spécialisés, après avoir compris ce qu'ils calculent.
