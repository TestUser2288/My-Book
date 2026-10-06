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


# Carte du volume, données et environnement

Cette section ouvre le volume par trois choses : la **carte des chapitres**, le **catalogue des jeux de données** (avec, pour chacun, ce qu'il contient et ce qu'on y a « programmé »), et l'**environnement** nécessaire pour refaire tous les calculs.

## Carte du volume

Les chapitres suivent la boucle de l'introduction : **chiffrer**, **décider**, **valider**. Les chapitres marqués ➕ sont facultatifs : le reste du volume ne les suppose pas, et chaque chapitre est lisible seul à condition d'avoir lu l'introduction.

| Chapitre | Question posée | Contenu |
|---|---|---|
| **1. Risque de crédit et scoring** | Quel emprunteur risque de défaillir, et combien la banque perdra-t-elle ? | grille de score, modèles de défaut, mesures de performance (Gini, KS, ROC) ; ➕ WOE et IV, PD-LGD-EAD et pertes attendues (IFRS 9), matrices de transition |
| **2. Modélisation actuarielle** | Quelle prime faut-il demander, et combien mettre de côté pour des sinistres futurs ? | fréquence et sévérité, tarification, provisionnement ; ➕ GLM tarifaires et crédibilité, *chain ladder*, Mack et bootstrap, assurance santé |
| **3. Mesures de risque et stress tests** | Que peut-on perdre dans le pire millième des cas ? Et si la crise est plus dure que prévu ? | VaR et *expected shortfall*, stress tests ; ➕ risques opérationnel, de marché et de liquidité, rétro-test et validation |
| **4. Cadre réglementaire** | Quel capital exige-t-on, et selon quelles règles ? | Bâle, Solvabilité, principes du Takaful ; ➕ IFRS 17, Takaful et finance islamique, lutte contre le blanchiment et fraude |
| **➕ 5. Assurance vie** | Combien vaut un engagement qui dure quarante ans ? | tables de mortalité, mathématiques actuarielles de la vie, modèle de Lee-Carter |
| **➕ 6. Réassurance** | Quelle part du risque faut-il céder, et à quel prix ? | formes de réassurance, tarification d'un traité, choix d'une couverture |
| **➕ 7. Actif-passif et portefeuille** | Comment adosser ce que l'on possède à ce que l'on doit ? | gestion actif-passif, théorie du portefeuille, de la frontière efficiente à l'actif-passif |
| **Projet du volume (cahier)** | Un tarif défendable, de bout en bout | un modèle de tarification avec validation hors période et notes réglementaires |

## Les jeux de données du volume

Tout est **simulé** avec des graines fixes (script `build/donnees5.py`), sauf un jeu **réel**. Chaque jeu simulé suit un mécanisme que le script documente en tête de fichier : c'est la **vérité programmée**. Nous la révélerons à la fin des études où elle est instructive, et le cahier permet de la retrouver.

Chargeons tous les fichiers et regardons leur forme et leurs valeurs manquantes.

```text
credit_defaut              30000 lignes  24 colonnes      0 manquants
credits_conso              40000 lignes  12 colonnes   4787 manquants
recouvrements               6000 lignes   7 colonnes      0 manquants
revolving_defauts           8000 lignes   5 colonnes      0 manquants
portefeuille_ifrs9         20000 lignes   9 colonnes      0 manquants
notations_panel            39102 lignes   4 colonnes      0 manquants
taux_defaut_macro             80 lignes   7 colonnes      0 manquants
polices_auto              100000 lignes  12 colonnes      0 manquants
sinistres_auto              5722 lignes   5 colonnes      0 manquants
triangle_rc                   55 lignes   5 colonnes      0 manquants
triangle_dommages             45 lignes   5 colonnes      0 manquants
triangle_choc                 55 lignes   5 colonnes      0 manquants
sante_assures              39112 lignes  15 colonnes      0 manquants
sinistres_gros              2898 lignes   2 colonnes      0 manquants
cat_annuel                    40 lignes   2 colonnes      0 manquants
rendements_marche           4000 lignes   6 colonnes      0 manquants
courbe_taux                  120 lignes  10 colonnes      0 manquants
pertes_operationnelles      1802 lignes   6 colonnes      0 manquants
mortalite_population        8000 lignes   5 colonnes      0 manquants
portefeuille_vie           20000 lignes   8 colonnes      0 manquants
transactions_lab          110223 lignes   8 colonnes      0 manquants
comptes_lab                 3000 lignes   4 colonnes      0 manquants
takaful_fonds                 45 lignes   7 colonnes      0 manquants
```

Les seules valeurs manquantes sont celles de `credits_conso` : elles sont **voulues**, nous y revenons plus bas. Voici maintenant le catalogue, avec les chapitres qui utilisent chaque jeu.

| Jeu | Contenu | Nature | Chapitres |
|---|---|---|---|
| `credit_defaut.csv` | 30 000 clients de cartes de crédit, défaut au mois suivant | **réel** (UCI, CC0) | 1, 3, projet (variante) |
| `credits_conso.csv` | 40 000 prêts à la souscription, défaut à 12 mois | simulé | 1, 3, 4 |
| `recouvrements.csv`, `revolving_defauts.csv` | pertes réalisées après défaut ; crédit renouvelable en défaut | simulé | 1 |
| `portefeuille_ifrs9.csv` | 20 000 prêts en vie, avec retards et probabilités de défaut | simulé | 1, 4 |
| `notations_panel.csv` | 5 000 emprunteurs notés pendant dix ans | simulé | 1 |
| `taux_defaut_macro.csv` | 80 trimestres de conjoncture et de taux de défaut | simulé | 1, 3 |
| `polices_auto.csv`, `sinistres_auto.csv` | 100 000 contrats-années d'assurance automobile ; leurs sinistres | simulé | 2, projet |
| `triangle_*.csv` et `triangle_*_verite.csv` | triangles de paiements (3 branches) ; paiements futurs réels | simulé | 2 |
| `sante_assures.csv` | assurés d'une complémentaire santé, trois années | simulé | 2 |
| `sinistres_gros.csv`, `cat_annuel.csv` | grands sinistres incendie ; pertes catastrophes annuelles | simulé | 6 |
| `rendements_marche.csv`, `marche_verite.csv` | rendements journaliers de cinq actifs ; régime vrai | simulé | 3, 7 |
| `courbe_taux.csv` | courbe des taux, mois par mois | simulé | 3, 7 |
| `pertes_operationnelles.csv` | événements de risque opérationnel | simulé | 3 |
| `mortalite_population.csv` (+ vérité), `portefeuille_vie.csv` | décès et expositions par âge ; contrats d'assurance vie | simulé | 5, 7 |
| `transactions_lab.csv`, `comptes_lab.csv`, `verite_lab.csv` | transactions bancaires et étiquettes de comptes suspects | simulé | 4 |
| `takaful_fonds.csv` | trois fonds de Takaful sur quinze ans | simulé | 4 |

### Le crédit à la consommation

Le jeu principal du chapitre 1 est `credits_conso.csv`, un portefeuille de prêts à la consommation observé **à la souscription**, avec la cible `defaut_12m` : 1 si l'emprunteur est en défaut dans les douze mois.

| Colonne | Signification |
|---|---|
| `age`, `revenu_annuel`, `anciennete_emploi` | caractéristiques de l'emprunteur (ancienneté en années) |
| `logement` | `locataire`, `proprietaire`, `heberge` |
| `objet` | `auto`, `travaux`, `conso` |
| `montant`, `duree_mois` | caractéristiques du prêt (en €, en mois) |
| `taux_endettement` | charges mensuelles rapportées au revenu mensuel, après le nouveau prêt |
| `nb_incidents_12m`, `anciennete_relation` | incidents de paiement récents ; ancienneté de la relation avec la banque |
| `defaut_12m` | **cible** : défaut dans les douze mois |


Le taux de défaut est de **6,0 %** (2 387 défauts sur 40 000 prêts) : un événement rare, comme il se doit. Deux colonnes ont des valeurs manquantes, **volontairement** : 5,0 % des revenus et 6,9 % des anciennetés d'emploi. Mais ces manquants ne sont pas aléatoires : l'ancienneté d'emploi manque pour 14,0 % des emprunteurs en défaut contre 6,5 % des autres, comme dans un dossier réel où ce qu'on ne sait pas dire sur soi est souvent significatif. Un modèle qui ignore ce fait perd de l'information (section 1.1). Le défaut est d'ailleurs très lié à l'historique : il passe de 4,4 % pour les emprunteurs sans incident à 37,1 % pour ceux qui en ont eu trois ou plus, et il est de 4,4 % chez les propriétaires contre 6,6 % chez les locataires et 7,5 % chez les hébergés. Enfin, le mécanisme de défaut comporte des **effets non linéaires** (un effet de l'âge en forme de U, un « coude » du taux d'endettement) qu'une grille de score par classes retrouvera mieux qu'une régression logistique linéaire : c'est le sujet des sections 1.1 et 1.4.

Le jeu **réel** est `credit_defaut.csv` : 30 000 clients de cartes de crédit d'une banque, observés en 2005, avec le défaut de paiement le mois suivant (22,1 %). Il vient du dépôt de l'UCI sous la licence CC0, et a été constitué par Yeh et Lien (2009). Il nous sert aux « détours sur données réelles » : il est plus délicat que nos jeux simulés (dépendances cachées, variables liées), et c'est ce qui le rend instructif.

### Les pertes en cas de défaut, les expositions, les provisions

Cinq jeux complètent le crédit pour le chapitre 1 (➕ sections 1.4 à 1.6) :

| Jeu | Colonnes principales |
|---|---|
| `recouvrements.csv` (6 000 prêts en défaut) | `garantie` (`aucune`, `caution`, `nantissement`), `objet`, `ead`, `delai_recouvrement_mois`, **`lgd_realisee`** (part de l'exposition définitivement perdue, de 0 à 1) |
| `revolving_defauts.csv` (8 000 lignes de crédit renouvelable en défaut) | `limite`, `tirage_12m_avant` (la part utilisée un an avant), `ead` (l'exposition au moment du défaut), `ccf_observe` (la part du non-utilisé finalement tirée) |
| `portefeuille_ifrs9.csv` (20 000 prêts en vie) | `ead`, `pd_origine`, `pd_actuelle`, `jours_retard`, `maturite_residuelle`, `lgd_estimee`, `taux_effectif`, `restructure` |
| `notations_panel.csv` (5 000 emprunteurs, dix ans) | `annee` (0 à 9), `note_debut` (de 1, la meilleure, à 7), `note_fin` (de 1 à 7, **8 = défaut**, 0 = sorti du portefeuille) |
| `taux_defaut_macro.csv` (80 trimestres) | `croissance_pib`, `chomage`, `variation_immo`, `taux_defaut` |


Les pertes réalisées après défaut ont une allure caractéristique : la **LGD moyenne est de 45,9 %**, mais 12 % des défauts se soldent par une perte **nulle** (tout est récupéré), et la garantie compte énormément (61 % de perte moyenne sans garantie, 27 % avec caution, 37 % avec nantissement). Pour le crédit renouvelable, le **CCF** moyen est de 40,2 % : en moyenne, un emprunteur qui fait défaut a tiré 40 % de ce qui lui restait disponible avant la rupture. Le portefeuille `portefeuille_ifrs9.csv` totalise 302,4 M€ d'encours, dont 5,9 % de prêts en retard d'au moins 30 jours et 2,4 % d'au moins 90 jours ; c'est à vous de calculer les « étapes » de la norme (section 1.5). Le panel de notations compte 39 102 observations annuelles de 5 000 emprunteurs, avec 767 défauts et 1 537 sorties du portefeuille (retraits que l'on ne doit pas confondre avec des défauts, section 1.6). Les taux de défaut trimestriels vont de 1,0 % à 12,8 %, avec un pic au trimestre 52 : une **récession** programmée que le chapitre 3 utilisera pour les tests de crise.

### L'assurance automobile, les triangles, la santé

Le chapitre 2 repose sur l'assurance automobile de la mutuelle.

| Colonne de `polices_auto.csv` | Signification |
|---|---|
| `annee` | année d'exercice (2022, 2023 ou 2024) ; une ligne = un contrat sur une année |
| `exposition` | fraction de l'année pendant laquelle le contrat était en vigueur (de 0,05 à 1) |
| `age_conducteur`, `anciennete_permis`, `age_vehicule`, `puissance` | caractéristiques du conducteur et du véhicule |
| `zone` | `Zone A` à `Zone F` (zones tarifaires fictives) |
| `bonus_malus`, `usage`, `carburant` | coefficient de bonus-malus (50 à 150), usage, motorisation |
| `nb_sinistres` | **cible de fréquence** : nombre de sinistres déclarés pendant l'exposition |

`sinistres_auto.csv` détaille chaque sinistre : `id_police`, `annee`, `type` (`materiel` ou `corporel`) et `montant` (en €). Les **triangles** (`triangle_rc.csv`, `triangle_dommages.csv`, `triangle_choc.csv`) donnent, pour dix années de survenance (2015 à 2024) et pour chaque **délai** de règlement, le paiement incrémental, le cumul, et la prime acquise de l'année ; les fichiers `*_verite.csv` contiennent le carré **complet**, c'est-à-dire aussi les paiements qui n'ont pas encore été faits à fin 2024, ce qui permet de juger une provision **a posteriori**. Enfin `sante_assures.csv` suit des assurés d'une complémentaire santé (`age`, `sexe`, `niveau` de garantie, `ald` pour une affection de longue durée, `exposition`, les coûts par poste et `cout_total`).


Le portefeuille automobile compte 100 000 contrats-années (86 602 années-véhicule d'exposition) et **5 722 sinistres**, soit une fréquence annuelle de 6,6 %. La plupart sont matériels (5 146, coût moyen de 2 638 €) ; 576 sont corporels, avec un coût moyen de 53 099 € et un maximum de plus de 2,4 M€ : **un faible nombre de sinistres porte l'essentiel du coût**, d'où l'intérêt d'une loi à queue lourde (section 2.1). Les triangles révèlent l'écart des branches : à fin 2024, il reste à payer **242,1 M€** sur la branche de responsabilité civile (queue longue, treize délais) contre **32,3 M€** sur les dommages (queue courte, six délais), pour des paiements déjà effectués du même ordre (environ 424 M€ et 410 M€). Dans le troisième triangle (`choc`), un choc d'inflation a frappé la diagonale de 2022 : le reste à payer réel (243,5 M€) est du même ordre, mais la méthode du *chain ladder* s'y trompera (section 2.5).

### Les marchés, la conjoncture et les pertes opérationnelles

Pour les mesures de risque (chapitre 3), `rendements_marche.csv` donne les rendements journaliers de cinq actifs (`actions_A`, `actions_B`, `obligations`, `immobilier`, `matieres`) sur 4 000 jours ouvrés à partir du 4 janvier 2010. Le générateur y a programmé des **régimes** (calme, stress) ; `marche_verite.csv` donne le régime vrai de chaque jour. `courbe_taux.csv` donne, mois par mois (120 mois), les taux de neuf maturités de 3 mois à 30 ans. `pertes_operationnelles.csv` liste les événements de risque opérationnel de dix ans (`categorie`, `ligne_metier`, `perte_brute`, `recuperation`, `perte_nette`).


Les rendements portent les défauts classiques des marchés : volatilité qui se regroupe, queues épaisses, corrélations qui montent en crise. Les jours de stress représentent 7 % de l'échantillon, et le pire jour atteint −10,9 % pour la seconde action et −13,9 % pour les matières premières. Le taux à dix ans de la courbe passe de 2,3 % au premier mois à 2,7 % au mois 60, monte à 4,35 % au mois 90 (le cycle de hausse programmé) puis revient à 2,5 %. Les pertes opérationnelles comptent 1 802 événements, de 2015 à 2024, pour 25,7 M€ au total : la perte nette moyenne est de 14 238 €, mais le maximum atteint près de 1,8 M€, ce qui est typique d'une distribution à queue lourde.

### La vie, la réassurance, la lutte contre le blanchiment, le Takaful

Les chapitres suivants utilisent des jeux plus spécialisés :

| Jeu | Contenu et colonnes principales |
|---|---|
| `mortalite_population.csv` | pour chaque `annee` (1980 à 2019), `age` (0 à 99) et `sexe` : `exposition` (personnes-années) et `deces` |
| `mortalite_verite.csv`, `mortalite_kt_vrai.csv` | les paramètres vrais du modèle de Lee-Carter qui a produit les décès |
| `portefeuille_vie.csv` | `sexe`, `age_emission`, `annee_emission`, `contrat` (`temporaire_10`, `temporaire_20`, `vie_entiere`), `capital`, `exposition_2015_2019`, `deces` |
| `sinistres_gros.csv`, `cat_annuel.csv` | grands sinistres incendie (`annee_survenance`, `montant`) ; perte annuelle due aux catastrophes (`annee`, `perte_cat`, souvent nulle) |
| `transactions_lab.csv` | transactions bancaires : `date`, `id_compte`, `sens`, `type` (`virement`, `especes`, `carte`), `montant`, `contrepartie`, `pays_contrepartie` |
| `comptes_lab.csv`, `verite_lab.csv` | profil des comptes ; **étiquette de vérité** : le schéma suspect planté (ou `aucun`) |
| `takaful_fonds.csv` | pour trois fonds (`famille`, `auto`, `sante`) et quinze années : `cotisations`, `sinistres`, `frais_gestion`, `rendement`, `reserve_ouverture` |


Le portefeuille d'assurance vie compte 20 000 contrats pour 84 909 années d'exposition et 832 décès ; la mortalité de la population porte sur plus de 6,5 millions de décès. Les grands sinistres incendie sont au nombre de 2 898 sur quinze ans et vont jusqu'à plus de 4,3 M€ ; parmi les 40 années de catastrophes, 17 ont connu un événement (le maximum atteint 35,6 M€). Côté lutte contre le blanchiment, 57 comptes sur 3 000 (1,9 %) portent un schéma suspect planté (fractionnement, relais, aller-retour, flux vers des pays à risque), noyés dans 110 223 transactions, avec en plus des commerces légitimes qui déposent beaucoup d'espèces et qui seront des **faux positifs** difficiles.

> 📦 **Régénérer les données.** Les fichiers sont versionnés avec le volume, mais la commande `python build/donnees5.py` les régénère à l'identique (une dizaine de secondes). La docstring de ce script contient toute la vérité programmée ; `donnees5.matrice_vraie()` donne la matrice de transition de notations qui a produit `notations_panel.csv`.

## L'environnement de travail

Ce volume n'utilise que des outils déjà rencontrés (Python et sa pile scientifique, statsmodels pour les GLM, `arch` pour les modèles GARCH), sans modèle pré-entraîné ni service externe. Les versions sont **figées** (fichier `requirements.txt`) : la pile numérique doit rester celle des volumes précédents, sinon certains résultats peuvent changer d'une décimale.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt           # versions figées (pandas 3.0.6, numpy 2.5.3, scikit-learn 1.9.1, statsmodels 0.15...)
python build/donnees5.py                  # régénère les jeux simulés ; credit_defaut.csv (jeu réel, UCI CC0) est fourni
```

```text
Python        : 3.13.3
numpy         : 2.5.3
pandas        : 3.0.6
scipy         : 1.18.1
scikit-learn  : 1.9.1
statsmodels   : 0.15.0
arch          : 8.0.0
lifelines     : 0.30.3
lightgbm      : 4.7.0
xgboost       : 3.4.1
shap          : 0.52.0
matplotlib    : 3.11.2
pyarrow       : 25.0.1
```

| Bibliothèque | Pour quoi faire | Chapitres |
|---|---|---|
| `numpy`, `pandas`, `scipy` | calcul, tableaux, lois de probabilité, optimisation | tous |
| `statsmodels` | régressions logistiques, GLM (Poisson, binomiale négative, Gamma, Tweedie) | 1, 2 |
| `scikit-learn`, `lightgbm`, `xgboost`, `shap` | modèles d'apprentissage, explications | 1, 2, projet |
| `arch` | modèles GARCH pour les rendements | 3 |
| `lifelines` | durées et survie | 5 |
| `matplotlib` | figures | tous |

> ⚠️ **Ce qui n'est pas installé, et que l'on écrit à la main.** Il existe des bibliothèques spécialisées pour la construction de grilles de score, le provisionnement par triangles, l'optimisation de portefeuille ou les calculs actuariels. Elles ne sont **pas** utilisées ici : les méthodes principales (discrétisation, *chain ladder*, frontière efficiente, commutations) sont écrites en quelques lignes de NumPy, parce que c'est le meilleur moyen de savoir ce que l'outil calcule, y compris ses hypothèses. Aucun outil n'est présenté comme « le standard ».

## Conventions du volume

- **Validation hors période.** Quand les données sont datées, on **entraîne sur le passé et on valide sur la période suivante** : par exemple 2022 et 2023 pour apprendre, 2024 pour juger. Un découpage aléatoire mélange le futur et le passé et donne des résultats trop optimistes ; la réalité ne nous offre jamais de futur en entraînement (volume III, section 1.1).
- **Nommer pareil.** La cible de défaut s'appelle `defaut_12m` ; les ensembles sont « jeu d'entraînement », « jeu de validation », « jeu de test » ; le « modèle de référence » est le modèle simple à battre.
- **Monnaie et unités.** Les montants sont en €, les durées en mois ou en années (précisé dans chaque colonne), les taux sont des fractions (0,02 pour 2 %) dans les tableaux et des pourcentages dans la prose.
- **Anonymat.** La banque et la mutuelle n'ont pas de nom ; les zones sont « Zone A… Zone F », les pays « Pays P1… Pays P12 ». Aucune autorité nationale n'est citée : on parle de « l'autorité de contrôle » ou de « la banque centrale ». Les textes **internationaux** sont nommés.
- **Graines fixes.** Chaque simulation fixe sa graine : `np.random.default_rng(graine)`. Aucun résultat du livre ne dépend du temps de calcul.
- **Une vérité programmée à comparer.** Quand une étude se termine par la comparaison à la vérité, c'est une particularité des données simulées, qu'on signale à chaque fois ; en pratique, on ne dispose que de la réalité qui se réalise, et trop tard.
