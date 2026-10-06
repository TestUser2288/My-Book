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


---

# Chapitre 1 : Risque de crédit et scoring

> « Prêter, c'est parier sur l'avenir d'une personne avec l'argent de quelqu'un d'autre. Le score est la façon d'écrire ce pari. »

Les volumes précédents vous ont appris à **construire et à valider** des modèles prédictifs. Ce volume les met au service d'un métier particulier : **mesurer des risques qui se paient en euros**, par une banque qui prête et par une mutuelle qui assure. Le premier de ces risques est le plus ancien et le mieux formalisé : celui qu'un emprunteur **ne rembourse pas**. C'est le **risque de crédit**.

Un établissement de crédit décide chaque jour des centaines ou des milliers de dossiers : accorder ou refuser, à quel taux, avec quelle limite. Il ne peut pas les examiner un par un ; il a besoin d'une **règle** qui transforme les informations d'un dossier en un nombre, le **score**, et d'une règle qui transforme ce nombre en décision. Cette règle doit être **efficace** (elle sépare bien les bons des mauvais payeurs), **stable** (elle ne s'effondre pas quand la clientèle change), **explicable** (on sait dire à un client pourquoi il est refusé, et au régulateur pourquoi le modèle est juste) et **calibrée** (quand elle annonce 3 % de défaut, il y a environ 3 % de défauts). Les trois premières sections du chapitre suivent ce fil : on **construit une grille de score** (1.1), on la **compare à des modèles plus souples** (1.2), puis on **mesure ce qu'elle vaut** avec les indicateurs du métier (1.3), le Gini, le KS et la courbe ROC. Trois sections facultatives prolongent le travail vers ce que la comptabilité et la réglementation réclament : le **WOE et l'IV** pour discrétiser proprement (1.4), les **pertes de crédit attendues** de la norme IFRS 9 avec leurs trois composantes PD, LGD et EAD (1.5), et les **matrices de migration** des notes (1.6).

> 🧭 **Ce que le chapitre suppose.** La régression logistique (volume II, section 2.2), la validation et les métriques (volume III, chapitres 1 et 5, en particulier 5.1 et 5.2 pour l'AUC et la calibration) et la notion de dérive (volume IV, section 4.7). Nous rappelons l'essentiel au moment utile.

## Le chemin de ce chapitre

| Section | Question | Idée centrale |
|---|---|---|
| 1.1 | Comment fabrique-t-on une grille de score ? | Cadrer, découper en classes, estimer sur les WOE, convertir en points |
| 1.2 | Une grille vaut-elle un modèle plus souple ? | Sur ces données, presque : la forme des effets compte plus que l'algorithme |
| 1.3 | Comment mesure-t-on un score ? | Gini, KS, calibration, stabilité, incertitude |
| ➕ 1.4 | Comment discrétiser sans se tromper ? | WOE, IV, regroupements monotones, pièges |
| ➕ 1.5 | Combien le portefeuille va-t-il perdre ? | PD × LGD × EAD, étapes IFRS 9, scénarios |
| ➕ 1.6 | Comment les notes évoluent-elles ? | Matrices de transition, cycle, PD sur plusieurs années |

## Les données du chapitre

> 📦 **Données simulées.** Tous les fichiers de ce chapitre sont **simulés** (graines fixes, générateur `build/donnees5.py`), sauf un détour sur un jeu **réel** en section 1.3 (clients d'une carte de crédit, source UCI, licence CC0, Yeh et Lien, 2009). La banque est fictive. Comme les données sont simulées, nous connaissons la **vérité programmée** et la révélons quand elle éclaire une étude : en vraie vie, personne ne vous la donne.

- `credits_conso.csv` : **40 000 prêts à la consommation**, décrits **à la souscription**, avec l'issue observée douze mois plus tard (`defaut_12m`, environ 6 %).
- `recouvrements.csv` : 6 000 prêts **entrés en défaut**, avec la perte réellement subie (section 1.5).
- `revolving_defauts.csv` : 8 000 lignes de crédit renouvelable en défaut (section 1.5).
- `portefeuille_ifrs9.csv` : 20 000 prêts en cours, avec leur probabilité de défaut à l'origine et aujourd'hui (section 1.5).
- `taux_defaut_macro.csv` : 80 trimestres de conjoncture et de taux de défaut du portefeuille (sections 1.3 et 1.5).
- `notations_panel.csv` : 5 000 emprunteurs notés chaque année pendant dix ans (section 1.6).


Voici l'allure d'un dossier : onze informations connues **au moment de la demande**, et l'issue.

```python
print(tr.drop(columns="id_credit").head(3).T.to_string())
```
<!--sortie-->
```text
                       37690      20231    31011
age                       30         21       66
revenu_annuel        15010.0    25950.0  41940.0
anciennete_emploi        7.8        0.8      8.4
logement             heberge  locataire  heberge
objet                travaux    travaux     auto
montant              18900.0     4000.0   6000.0
duree_mois                36         60       60
taux_endettement       0.519       0.06    0.331
nb_incidents_12m           0          0        0
anciennete_relation     12.7        7.1      4.4
defaut_12m                 0          0        0
```

Les variables sont celles d'un dossier de crédit à la consommation : l'âge, le revenu annuel, l'ancienneté dans l'emploi, le logement, l'objet du prêt, le montant et la durée, le **taux d'endettement** (charges mensuelles, mensualité comprise, rapportées au revenu), le nombre d'incidents de paiement des douze derniers mois, l'ancienneté de la relation avec la banque. Deux variables ont des **valeurs manquantes** : le revenu (5 %) et l'ancienneté dans l'emploi (7 %). Nous verrons que le second manque **plus souvent chez les emprunteurs risqués** : un manquant n'est pas neutre.

Le jeu est découpé **une fois pour toutes** en un échantillon de **développement** (70 %, 28 000 prêts) et un échantillon de **test** (30 %, 12 000 prêts), tous deux avec la même proportion de défauts. On n'y touche pas pendant la construction (classes, coefficients) ; il sert ensuite à mesurer des candidats **fixés d'avance**, sans réglage fait en le regardant.


> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : toutes les applications partent de ces fichiers ; commencez par l'application 1.1.


## 1.1 Construction d'une grille de score

Cette section déroule, dans l'ordre où le fait un analyste de crédit, la fabrication d'une **grille de score** : cadrer le problème, découper chaque variable en classes, estimer les poids, puis traduire le résultat en points que l'on sait lire et auditer. C'est un très vieux métier de la statistique appliquée, et il en reste une pratique solide : une grille est **simple à expliquer**, **facile à contrôler** et **difficile à faire dérailler**.

### 1.1.1 Un score, une décision

Un **score** est un nombre attaché à un dossier, construit pour que l'ordre des nombres reproduise l'ordre des risques. Par convention de ce chapitre, **un score élevé signale un dossier sûr**. Le score ne décide rien par lui-même ; il alimente trois décisions :

- **accorder ou refuser** : on fixe un **seuil** (*cut-off*) en dessous duquel le dossier est refusé ou renvoyé à un examen humain ;
- **fixer le prix et la limite** : un dossier plus risqué paie un taux plus élevé ou reçoit un montant plus faible, parce que la banque doit couvrir ses pertes attendues (section 1.5) ;
- **suivre le portefeuille** : regroupés en classes de risque (une **échelle maîtresse**, *master scale*), les scores donnent des **probabilités de défaut** par classe, que la comptabilité et la réglementation réutilisent (chapitre 4).

Le vocabulaire est celui du métier : un client qui fait défaut dans la fenêtre d'observation est un **mauvais** (*bad*), les autres sont des **bons** (*good*). Les **cotes** (*odds*) d'un groupe sont le rapport bons sur mauvais ; une cote de 50 contre 1 correspond à 2 % de mauvais. Un score est en fait une **cote écrite en points**, et c'est ce qui rend la grille lisible : nous y revenons en 1.1.5.

> 💡 **Pourquoi une grille plutôt qu'un modèle plus puissant ?** Parce que le gain de précision d'un algorithme souple est souvent faible devant ce que coûte son opacité : il faut pouvoir justifier un refus à un client, montrer à l'autorité de contrôle que le modèle est sensé, et le surveiller avec des outils éprouvés. La section 1.2 mesure ce gain **sur nos données** au lieu de le supposer.

### 1.1.2 Cadrer le problème

Avant la moindre régression, quatre décisions de cadrage déterminent ce que le score *veut dire*.

**La population.** On modélise **ceux sur qui la décision s'applique** : ici, des particuliers qui demandent un prêt à la consommation. On exclut ce qui relève d'un autre traitement (prêts aux entreprises, dossiers frauduleux avérés, produits très différents). Mélanger des populations qui n'obéissent pas aux mêmes lois est la première cause de score décevant.

**La définition du défaut.** Elle est **conventionnelle** et doit être écrite noir sur blanc : par exemple, *un retard de paiement de 90 jours ou plus sur un montant significatif*, ou bien un événement qui montre que le client ne paiera sans doute pas (restructuration, procédure collective). Le choix a des effets sur tout : un seuil de 30 jours produit bien plus de « mauvais » (et plus de bruit), un seuil de 180 jours en produit moins et plus tard. Ici, `defaut_12m` vaut 1 si le prêt est tombé en défaut dans les douze mois qui suivent sa souscription.

**Les deux fenêtres.** Le score doit prédire l'avenir à partir de ce que l'on **sait à la date de la demande**. On distingue donc la **fenêtre d'observation** (le passé, d'où viennent les variables explicatives) et la **fenêtre de performance** (l'avenir, où l'on regarde si le défaut survient) :


![Les deux fenêtres d'un score de crédit : on décrit le client avec ce que l'on sait à la date de la demande, on mesure le défaut ensuite.](figures/ch01-fenetres.png)

La conséquence est une règle d'or contre la **fuite d'information** (volume III, section 1.1) : une variable calculée *après* la date de la demande, même un peu, n'a pas le droit d'entrer dans le score. Dans nos données, `nb_incidents_12m` compte les incidents des douze mois **précédant** la demande ; le nombre de retards du prêt lui-même, lui, serait une fuite évidente.

⚠️ **Le piège de la maturité.** Un prêt souscrit il y a six mois n'a pas encore eu douze mois pour faire défaut : sa « non-défaillance » est une observation **tronquée**. Dans une vraie base, on ne garde que des prêts dont la fenêtre de performance est complète, ou on corrige. Nos données sont déjà arrêtées à douze mois pour tous.

**Les échantillons.** On découpe en développement, validation (réglages) et test. Quand les dossiers sont **datés**, on valide aussi **hors période** (*out-of-time*) : développement sur des souscriptions anciennes, test sur les plus récentes, parce que le but est de prédire l'avenir et non des dossiers mélangés avec ceux du passé. Notre fichier ne porte pas de date : nous avons donc procédé par un découpage aléatoire stratifié, et la section 1.3 montre autrement ce que l'écoulement du temps fait à un score (la conjoncture).

### 1.1.3 Découper en classes

Une grille de score **ne prend pas l'âge brut** : elle regroupe les âges en **classes**. Le découpage en classes (*binning*) a quatre raisons d'être.

1. **Les effets sont rarement linéaires.** Le risque ne croît pas régulièrement avec l'âge : il est élevé chez les très jeunes, bas au milieu de la vie, un peu plus haut chez les plus âgés. Une classe laisse à chaque tranche son propre niveau de risque, sans imposer de forme.
2. **Les valeurs extrêmes perdent leur pouvoir de nuisance.** Un revenu de 4 millions d'euros tombe simplement dans la dernière classe.
3. **Les manquants ont une place.** On les range dans une classe à part, avec son propre risque (nous le verrons), au lieu de les imputer de façon arbitraire.
4. **Le résultat se lit.** « Entre 25 et 30 ans : 52 points » se discute avec un client et se contrôle par un auditeur.

Regardons le défaut observé, classe d'âge par classe d'âge, sur l'échantillon de développement :

```python
t_age = O.table_woe(tr["age"], tr["defaut_12m"], "age")
print(t_age[["effectif", "mauvais", "taux_defaut", "woe"]].round(3).to_string())
```
<!--sortie-->
```text
          effectif  mauvais  taux_defaut    woe
classe                                         
1: <25        2121      299        0.141 -0.950
2: 25-30      2127      149        0.070 -0.173
3: 30-40      7498      410        0.055  0.093
4: 40-55     12135      558        0.046  0.276
5: 55-65      3289      183        0.056  0.073
6: 65+         830       72        0.087 -0.408
```

Le taux de défaut passe de 14,1 % chez les moins de 25 ans à 4,6 % entre 40 et 55 ans, puis remonte à 8,7 % après 65 ans : une **courbe en U**. Il en va de même, d'une autre façon, pour le taux d'endettement, dont le risque reste modeste jusqu'à 40 % puis **s'envole** (37 % de défaut au-delà de 70 %) :


![Taux de défaut observé par classe (barres : intervalle à 95 %) : l'âge dessine un U, le taux d'endettement un coude.](figures/ch01-taux-par-classe.png)

Comment choisit-on les bornes ? Il n'y a pas de recette unique, mais des **règles de prudence** que le métier a stabilisées :

- chaque classe doit contenir **assez de monde** (au moins quelques pourcents de la population) **et assez de mauvais** (quelques dizaines au minimum), sinon son taux n'est que du bruit ;
- deux classes voisines doivent avoir des taux **nettement différents** (sinon on les fusionne) ;
- quand le sens économique l'impose (plus d'endettement, plus de risque), l'ordre des classes doit être **monotone** ; une forme en U comme celle de l'âge est admise quand on peut l'expliquer ;
- on regarde les **intervalles de confiance** (les barres de la figure) avant de croire à une différence ;
- on garde les classes **lisibles** : des bornes rondes, un nombre réduit de classes (de quatre à huit par variable).

Les bornes de ce chapitre ont été choisies à la main selon ces règles ; la section ➕ 1.4 montre comment les chercher de façon systématique.

### 1.1.4 Le poids de l'évidence et la régression

Une fois les classes tracées, on remplace chaque classe par un nombre qui résume son risque : le **poids de l'évidence** (*weight of evidence*, **WOE**). Pour une classe $j$,

$$\text{WOE}_j=\ln\frac{\text{part des bons dans la classe } j}{\text{part des mauvais dans la classe } j}=\ln\frac{B_j/B}{M_j/M},$$

où $B_j$ et $M_j$ sont les nombres de bons et de mauvais de la classe, $B$ et $M$ ceux de l'échantillon entier. Un WOE **positif** signale une classe plus sûre que la moyenne ; un WOE **négatif**, une classe plus risquée ; zéro, une classe moyenne. Calculons-le à la main pour les moins de 25 ans de notre échantillon : 299 mauvais et 1 822 bons, alors que l'échantillon compte 1 671 mauvais et 26 329 bons au total.

$$\text{WOE}_{<25}=\ln\frac{1\,822/26\,329}{299/1\,671}=\ln\frac{0{,}0692}{0{,}1789}=\ln 0{,}387\approx-0{,}95.$$

Ces jeunes emprunteurs pèsent 7 % des bons mais 18 % des mauvais. Le WOE est aussi la **différence de log-cotes** entre la classe et l'ensemble : $\text{WOE}_j=\ln(\text{cote}_j)-\ln(\text{cote globale})$, avec $\text{cote}_j=B_j/M_j$. C'est ce qui le rend si pratique : il est exprimé dans **la même unité que la régression logistique**, le logarithme d'une cote.

La grille s'obtient alors par une **régression logistique sur les WOE**. On prédit l'événement « bon » et chaque variable $k$ entre par le WOE de la classe où tombe le dossier :

$$\ln\frac{P(\text{bon})}{P(\text{mauvais})}=\alpha+\sum_{k=1}^{p}\beta_k\,\text{WOE}_k(x).$$

> 📐 **Pourquoi des coefficients proches de 1 ?** Si les $p$ variables étaient **indépendantes** conditionnellement au résultat bon/mauvais, la formule de Bayes donnerait exactement $\ln\frac{P(\text{bon}\mid x)}{P(\text{mauvais}\mid x)}=\ln\frac{P(\text{bon})}{P(\text{mauvais})}+\sum_k \text{WOE}_k(x)$ : tous les $\beta_k$ vaudraient 1 (c'est le **Bayes naïf**). En pratique, les variables sont corrélées (le revenu et le taux d'endettement partagent de l'information), la régression **corrige** cette redondance en abaissant certains coefficients. Un coefficient **négatif** serait un signal d'alarme : il traduirait une variable trop corrélée à une autre, ou des classes mal construites.

L'appel suivant fait tout cela : tables WOE, remplacement des variables par leurs WOE, régression logistique.

```python
from sklearn.linear_model import LogisticRegression
tables = O.tables_woe(tr)                      # une table WOE par variable (classes de O.BORNES)
W_tr = O.vers_woe(tr, tables)                  # chaque variable remplacée par le WOE de sa classe
lr = LogisticRegression(max_iter=2000).fit(W_tr, 1 - y_tr)     # on prédit « bon »
print(pd.Series(lr.coef_[0], index=W_tr.columns).round(2).to_string())
```
<!--sortie-->
```text
age                    0.85
taux_endettement       0.72
anciennete_emploi      0.80
revenu_annuel          0.65
montant                0.25
duree_mois             0.35
nb_incidents_12m       0.85
anciennete_relation    1.04
logement               1.01
objet                  0.98
```

Les coefficients vont de 0,25 pour le montant à 1,04 pour l'ancienneté de la relation : ils sont **tous positifs**, proches de 1 pour le logement (1,01), l'objet (0,98) et l'ancienneté de la relation, plus bas pour les variables qui se recoupent (le montant, la durée, le revenu, qui dépendent les uns des autres).

### 1.1.5 Des log-cotes aux points

La régression produit une **log-cote** $\ln(\text{bons}/\text{mauvais})$ par dossier. Il reste à l'écrire en **points**, pour qu'un score de 600 ait un sens. La convention du métier fixe deux nombres :

- un **score de base** associé à une **cote de base** (par exemple 600 points pour une cote de 50 bons contre 1 mauvais, soit 2 % de défaut) ;
- le **PDO** (*points to double the odds*) : le nombre de points qu'il faut ajouter pour **doubler la cote** (par exemple 20 points).

Le score est une fonction affine de la log-cote : $\text{Score}=\text{décalage}+\text{facteur}\times\ln(\text{cote})$. Les deux conditions donnent les deux constantes :

$$\text{facteur}=\frac{\text{PDO}}{\ln 2}=\frac{20}{0{,}6931}\approx28{,}85,\qquad \text{décalage}=600-28{,}85\times\ln 50\approx487{,}12.$$

Vérifions à la main : une cote de 50 donne $487{,}12+28{,}85\times3{,}912=600$ ; une cote de 100 donne $487{,}12+28{,}85\times4{,}605=620$, soit 20 points de plus : la cote a doublé, le score a gagné un PDO.

Comme la log-cote est une somme ($\alpha+\sum\beta_k\text{WOE}_k$), le score est une **somme de points par variable**. En répartissant l'intercept et le décalage également entre les $p$ variables, la classe $j$ de la variable $k$ reçoit

$$\text{points}_{jk}=\Bigl(\beta_k\,\text{WOE}_{jk}+\frac{\alpha}{p}\Bigr)\times\text{facteur}+\frac{\text{décalage}}{p}.$$

Pour retrouver une probabilité, on inverse : $\text{cote}=\exp\bigl((\text{Score}-\text{décalage})/\text{facteur}\bigr)$ et $\text{PD}=1/(1+\text{cote})$. Un score de 580 correspond à une cote de $\exp(92{,}88/28{,}85)\approx25$, soit une probabilité de défaut de $1/26\approx3{,}8\ \%$.


### 1.1.6 Lire la carte de score

Le résultat est la **carte de score** : un tableau classe par classe. Voici deux de ses variables, avec le défaut observé (pour mémoire), le WOE et les points :

```python
carte = G.points_classes()
print(carte[carte.variable.isin(["age", "nb_incidents_12m"])].drop(columns="variable").to_string(index=False))
```
<!--sortie-->
```text
  classe  effectif  taux_defaut    woe  points
  1: <25      2121       0.1410 -0.950    33.3
2: 25-30      2127       0.0701 -0.173    52.4
3: 30-40      7498       0.0547  0.093    58.9
4: 40-55     12135       0.0460  0.276    63.4
5: 55-65      3289       0.0556  0.073    58.4
  6: 65+       830       0.0867 -0.408    46.6
    1: 0     21066       0.0439  0.325    64.6
    2: 1      5964       0.0942 -0.494    44.5
   3: 2+       970       0.1907 -1.313    24.3
```

On y lit d'un coup d'œil ce que la grille pense : les moins de 25 ans reçoivent 33 points, contre 63 pour les 40–55 ans. Trente points d'écart valent un PDO et demi, donc une cote **environ 2,8 fois** meilleure ($2^{30/20}\approx2{,}8$). Un seul incident dans l'année coûte 20 points par rapport à aucun ; deux incidents ou plus, 40 points. La carte complète compte une cinquantaine de lignes ; le cahier (application 1.1) la construit en entier.

L'**amplitude** des points d'une variable (le plus haut moins le plus bas) mesure son **influence** dans la grille :

```text
variable
taux_endettement       55.7
nb_incidents_12m       40.3
anciennete_emploi      35.4
revenu_annuel          30.4
age                    30.1
anciennete_relation    27.0
logement               16.5
objet                   8.0
duree_mois              6.6
montant                 6.2
```

Le taux d'endettement domine (56 points d'écart), suivi des incidents (40 points), de l'ancienneté dans l'emploi (35), du revenu (30) et de l'âge (30) ; le montant, la durée et l'objet pèsent peu. Voici maintenant **trois dossiers du jeu de test**, un très sûr, un médian, un très risqué : on additionne simplement les points de la classe où tombe chaque variable.

```text
           variable             sûr            médian           risqué
                age      30-40 : 59        30-40 : 59         <25 : 33
   taux_endettement       <0.2 : 66      0.3-0.4 : 59     0.4-0.5 : 51
  anciennete_emploi        10+ : 75          1-3 : 46         3-6 : 52
      revenu_annuel     50000+ : 73     manquant : 54 40000-50000 : 67
            montant 7000-12000 : 57   7000-12000 : 57 12000-20000 : 55
         duree_mois      24-36 : 59        24-36 : 59       36-48 : 57
   nb_incidents_12m          0 : 65            0 : 65           1 : 44
anciennete_relation       6-12 : 66          3-6 : 59         1-3 : 53
           logement  locataire : 53 proprietaire : 66   locataire : 53
              objet      conso : 52         auto : 59       conso : 52
     TOTAL (points)             625               583              519
```


Les trois scores valent environ 625, 583 et 519 points : le dossier sûr cumule des classes favorables presque partout (une ancienneté de dix ans et plus dans l'emploi, un revenu supérieur à 50 000 €, un endettement inférieur à 20 %), le dossier risqué cumule un âge de moins de 25 ans, un incident de paiement et un endettement entre 40 et 50 %. Comme le score est une échelle de cotes, l'écart de 106 points entre le premier et le troisième représente $106/20=5{,}3$ PDO, soit une cote **environ 40 fois** plus favorable ($2^{5{,}3}\approx40$). Le dossier médian (583 points) correspond à une probabilité de défaut de 3,5 % environ.

### 1.1.7 Les dossiers refusés : l'inférence des rejets

Toute grille est construite sur les **dossiers acceptés**, ceux dont on connaît l'issue. Les dossiers refusés n'ont jamais été financés : on ne saura jamais s'ils auraient fait défaut. Or le score doit s'appliquer à **tous les demandeurs**, y compris à ceux que l'ancienne politique aurait refusés. C'est le problème de l'**inférence des rejets** (*reject inference*) : un échantillon **sélectionné** par la politique passée donne une image déformée de la population qui se présente.

Simulons-le, puisque nos données contiennent des dossiers que l'on aurait normalement refusés. Imaginons une ancienne politique qui refuse les taux d'endettement supérieurs à 50 % et les clients ayant plus d'un incident : elle accepte environ 88,5 % des demandeurs. Construisons la grille sur ces seuls acceptés, puis mesurons-la sur **tous** les demandeurs du test :

```text
grille construite sur  AUC sur tous  PD moyenne annoncée  défaut réel
  tous les demandeurs        0.7712               0.0593       0.0597
   les acceptés seuls        0.7156               0.0439       0.0597
```


La grille construite sur les acceptés **annonce 4,4 % de défaut** alors que la réalité est de 6,0 % : elle sous-estime le risque de la population complète d'un tiers, et son pouvoir de classement tombe (AUC de 0,716 contre 0,771). La raison est visible dans ses classes : puisque presque aucun dossier à fort endettement n'a été accepté, la classe des taux entre 50 et 60 % ne contient que **20 prêts**, aucun défaut, et reçoit un WOE **positif** (+0,66), comme si ces dossiers étaient plus sûrs que la moyenne. Le modèle n'a rien vu de ce qui s'est passé hors de la zone d'acceptation : il **extrapole** à vide.

Que peut-on faire ? Aucune méthode ne remplace une observation, mais on en connaît plusieurs :

- **Utiliser une information externe** : l'issue de ces demandeurs auprès d'*autres* prêteurs, obtenue par un bureau de crédit.
- **Parcelliser** (*parcelling*) : donner aux refusés une probabilité de défaut tirée de la grille des acceptés, majorée d'un facteur prudent, et les ajouter à l'échantillon avec un poids ; on suppose que les refusés **ressemblent** aux acceptés de score voisin, ce qui est exactement ce qui est en cause.
- **Repondérer** les acceptés pour qu'ils représentent la population complète, selon leur probabilité d'acceptation ; cela corrige peu quand certaines zones n'ont **aucun** accepté.
- **Accepter volontairement** un petit échantillon aléatoire de dossiers qui auraient été refusés, à coût contrôlé : c'est la seule voie qui fournit de vraies données, et elle a un prix réel pour la banque et des conséquences pour les clients concernés.

⚠️ **L'honnêteté impose de le dire.** L'inférence des rejets réduit un biais en faisant des hypothèses invérifiables ; elle ne le supprime pas. Une grille construite sur des acceptés doit être **surveillée** après la mise en production, quand la politique d'acceptation change, car c'est alors que la population change et que le biais apparaît.

> ✅ **À retenir.**
> - Un score est une **cote écrite en points** : $\text{Score}=\text{décalage}+\text{facteur}\cdot\ln(\text{bons}/\text{mauvais})$, avec facteur = PDO/ln 2.
> - Le cadrage (population, définition du défaut, fenêtres d'observation et de performance, découpage) décide de ce que le score veut dire ; la **fuite d'information** s'évite en ne gardant que ce que l'on sait à la date de la demande.
> - On **découpe en classes** (assez de monde, assez de mauvais, bornes lisibles, ordre monotone quand le sens économique l'exige), on remplace chaque classe par son **WOE**, puis on estime une **régression logistique** ; les coefficients proches de 1 correspondent au cas indépendant (Bayes naïf).
> - La carte de score est une **somme de points** par classe ; l'amplitude des points mesure l'influence d'une variable.
> - Les refusés manquent à l'échantillon : une grille construite sur les acceptés sous-estime le risque de la population qui se présente.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 et 1.2, exercices 1.1 à 1.3.


## 1.2 Modèles de prédiction du défaut

La grille de la section 1.1 est un modèle **volontairement contraint** : des classes, des effets additifs, des points. Les données d'aujourd'hui permettent des modèles bien plus souples, comme les arbres de gradient (volume III, section 2.4). Cette section pose la question qu'un comité de risque pose toujours : **que gagne-t-on à abandonner la grille, et que perd-on ?** Nous comparons trois candidats **fixés d'avance** sur le même échantillon de test, nous regardons **pourquoi** l'un l'emporte sur l'autre en nous appuyant sur la vérité programmée, puis nous traitons deux sujets propres au crédit : la **calibration** et les **motifs de refus**.

### 1.2.1 Trois candidats

- **La régression logistique « brute »** : les variables sont prises telles quelles (âge, taux d'endettement… en nombres), avec des indicateurs pour les manquants et des modalités pour les catégories. C'est la première chose qu'un statisticien essaie (volume II, section 2.2).
- **La grille de score** de la section 1.1 : classes, WOE, régression, points.
- **Un modèle de boosting** (LightGBM) : un ensemble d'arbres qui apprend lui-même les seuils et les interactions. On en examine deux versions, libre et **monotone** (nous y revenons en 1.2.3).

Les trois sont entraînés sur les mêmes 28 000 prêts et mesurés sur les mêmes 12 000 prêts de test. Aucun réglage n'a été fait en regardant le test ; les paramètres du boosting sont ceux d'un réglage modeste (300 petits arbres de huit feuilles, pas d'apprentissage de 0,03, au moins 200 prêts par feuille), choisis pour éviter le surapprentissage, non pour gagner un dixième de point.


La version du boosting contrainte demande que le risque **ne puisse que croître** avec le taux d'endettement et le nombre d'incidents, et **que décroître** avec le revenu, l'ancienneté dans l'emploi et l'ancienneté de la relation, pour que la forme du modèle reste défendable devant un auditeur :

```python
contraintes = {"taux_endettement": 1, "nb_incidents_12m": 1, "revenu_annuel": -1,
               "anciennete_emploi": -1, "anciennete_relation": -1}       # +1 : le risque ne peut que croître
mc = [contraintes.get(c, 0) for c in Xb_tr.columns]
gbm = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.03, num_leaves=8, min_child_samples=200, subsample=0.8,
                         subsample_freq=1, colsample_bytree=0.8, monotone_constraints=mc, random_state=0, verbose=-1)
gbm.fit(Xb_tr, y_tr)
```


### 1.2.2 Le verdict mesuré

Les mesures sont celles de la section 1.3 (AUC, Gini = 2·AUC − 1, KS) ; ici, lisons-les en gros.

```text
                             AUC   Gini     KS
logistique brute           0.762  0.524  0.396
grille de score            0.771  0.542  0.406
boosting libre             0.772  0.545  0.407
boosting monotone          0.774  0.547  0.409
logistique, vraies formes  0.777  0.555  0.420
intervalle de l'AUC (rééchantillonnage, 95 %) :
  logistique brute     [0.741 ; 0.779]
  grille de score      [0.751 ; 0.789]
  boosting monotone    [0.753 ; 0.790]
AUC grille - AUC logistique brute : +0.0097  [+0.0009 ; +0.0182]
AUC grille - AUC boosting monotone : -0.0022  [-0.0089 ; +0.0040]
```


Le tableau raconte une histoire nette :

- La **grille** (AUC 0,771) fait **mieux que la logistique brute** (0,762). L'écart est petit (un point d'AUC), mais l'intervalle de la différence **apparié** (mêmes dossiers dans les deux calculs, volume III, section 1.4) est entièrement positif : il n'est pas dû au hasard de l'échantillon de test.
- Le **boosting** (0,774 pour la version monotone, 0,772 pour la version libre) **ne fait pas mieux que la grille** : la différence de 0,002 est dans le bruit (l'intervalle apparié contient zéro). Imposer la monotonie ne coûte rien ici, elle améliore même un tout petit peu.
- La logistique à laquelle on donne les **vraies formes** (nous allons voir lesquelles) atteint 0,777 : c'est le **plafond atteignable** avec ces variables et cet échantillon, la mesure de ce que valent les meilleurs modèles possibles. La grille en est à 0,6 point.

> 🧪 **Un résultat qui n'est pas un slogan.** On lit souvent que « les modèles d'arbres battent la régression logistique ». Sur ce jeu, **ce n'est pas le cas** : les variables sont peu nombreuses, la vérité est une somme d'effets (des formes simples sans interaction), et 28 000 lignes ne laissent pas de quoi apprendre des interactions fines. Sur d'autres données (le jeu réel de la section 1.3, où l'effet du statut de paiement est très non linéaire), le boosting gagne nettement. **La bonne démarche est de mesurer**, et non de supposer.

### 1.2.3 Pourquoi la grille bat la logistique brute : les formes

Pourquoi les classes aident-elles ? Parce que la vérité n'est **pas linéaire**. Les données ont été simulées avec un risque dont l'effet sur la log-cote est :

- **en U pour l'âge** : $0{,}0012\,(\text{âge}-47)^2$ (multiplié par 1,3 comme tous les effets du jeu), ce qui donne un risque plus élevé chez les jeunes que chez les plus de 65 ans, et minimal vers 47 ans ;
- **en coude pour le taux d'endettement** : 1,5 par point d'endettement, puis 3 de plus par point **au-delà de 50 %**.

Une régression logistique brute ne peut pas représenter un U avec **un seul coefficient** : elle ajuste la meilleure droite, qui **décroît** lentement avec l'âge : elle dit que les plus âgés sont les plus sûrs, alors qu'ils sont plus risqués que les 40–55 ans. La grille, qui donne à chaque classe son propre niveau, suit la courbe :


![Effet de l'âge et du taux d'endettement sur la log-cote de défaut, centré sur la population : la vérité programmée (noir), la grille qui suit sa forme (bleu), la droite de la logistique brute (orange pointillé) qui rate le U et le coude.](figures/ch01-formes.png)

La droite orange est la meilleure approximation linéaire, et elle **se trompe aux endroits qui comptent** : elle sous-estime le risque des très jeunes, des plus âgés et des très endettés, qui sont justement ceux que l'on veut repérer. La grille suit le U de l'âge et le coude de l'endettement par paliers. Le boosting, lui, les découvre seul grâce aux seuils de ses arbres.

⚠️ **Ne retenez pas « la grille bat la logistique », mais « les formes comptent ».** Une logistique à laquelle on ajoute un terme quadratique en âge et un coude en endettement (la ligne « vraies formes » du tableau) fait aussi bien que la grille, sans classes. L'avantage de la grille est ailleurs : **elle trouve les formes sans que l'on ait à les deviner**, traite proprement les manquants et reste lisible.

### 1.2.4 Le boosting monotone

Un arbre de gradient libre peut produire des effets **non monotones** là où l'économie n'en admet pas : par exemple un risque qui *baisse* quand l'endettement passe de 55 % à 60 %, simple accident d'un échantillon creux. Pour un modèle de crédit, c'est un problème de **gouvernance** : on ne sait pas l'expliquer, et un client pourrait améliorer son score en détériorant son dossier. Les contraintes de monotonie imposent à chaque arbre de ne jamais inverser le sens d'une variable : la fonction de score est alors **monotone** dans chaque variable contrainte.

Le code de 1.2.1 en montre la mise en œuvre : une liste de signes, un par colonne. Son coût en performance est ici nul. Dans d'autres situations, il peut être de quelques millièmes d'AUC ; **c'est le prix d'un modèle défendable**. Pour comprendre les contributions d'un modèle de ce type, les méthodes du volume III (section 5.3, importance par permutation, SHAP) s'appliquent sans changement ; en crédit, on leur préfère souvent des **motifs de refus** adossés à la grille (1.2.6) ou à des contributions par variable.

### 1.2.5 Calibrer : une probabilité n'est pas un rang

Un score qui classe bien peut annoncer des probabilités fausses. Or le crédit **utilise les probabilités** : pour fixer un prix, pour calculer la perte attendue, pour le capital réglementaire. La **calibration** (volume III, section 5.2) vérifie qu'un groupe de dossiers annoncés à 3 % fait bien environ 3 % de défauts. Regroupons les dossiers du test en dix groupes de taille égale, selon la probabilité annoncée par la grille :

```text
           n  annoncee  observee
groupe                          
1       1200    0.0094    0.0108
2       1200    0.0151    0.0167
3       1201    0.0200    0.0216
4       1199    0.0253    0.0192
5       1200    0.0314    0.0242
6       1200    0.0395    0.0500
7       1200    0.0501    0.0500
8       1200    0.0670    0.0633
9       1200    0.0995    0.1117
10      1200    0.2356    0.2292
```


La grille est **bien calibrée** : la probabilité moyenne annoncée (5,9 %) est celle du défaut observé (6,0 %) et, groupe par groupe, les écarts restent dans une marge de deux écarts-types (le dixième groupe annonce 23,6 % et observe 22,9 %). Ce n'est pas un hasard : une régression logistique **calibre en moyenne par construction** sur son échantillon de développement. Cette propriété se perd quand la population change (section 1.3) ; un boosting, lui, n'est pas calibré par construction et demande souvent une recalibration (régression logistique ou isotonique sur la sortie, volume III, section 5.2).

### 1.2.6 Expliquer un refus : les motifs

Dans beaucoup de juridictions, un client refusé est en droit de connaître **les principales raisons** de la décision, et le prêteur doit pouvoir les produire (nous reviendrons sur la réglementation au chapitre 4 ; le droit exact dépend du pays et de l'époque, à vérifier). La grille y répond naturellement : les **motifs de refus** (*reason codes*) sont les variables pour lesquelles le dossier **perd le plus de points** par rapport au meilleur cas possible de chaque variable.

```python
def motifs(i, k=3):
    """Les k variables où le dossier te.iloc[i] perd le plus de points, par rapport à la meilleure classe de la variable."""
    perte = {}
    for v in O.VARIABLES:
        classes = pts[pts.variable == v]
        c = O.classer(te.iloc[[i]][v], v).iloc[0]
        perte[v] = classes.points.max() - float(classes[classes.classe == c].points.iloc[0])
    return pd.Series(perte).sort_values(ascending=False).head(k).round(1)

print(motifs(trois["risqué"]))
```
<!--sortie-->
```text
age                    30.1
anciennete_relation    23.4
anciennete_emploi      22.8
dtype: float64
```


Pour ce dossier très risqué, les trois motifs sont l'âge (30 points perdus par rapport à la meilleure tranche d'âge), l'ancienneté de la relation (23 points) et l'ancienneté dans l'emploi (23 points). Remarquez qu'**un motif n'est pas un conseil** : un client de 24 ans ne peut pas « corriger » son âge. La réglementation de certains pays interdit d'ailleurs que certaines variables (le sexe, par exemple) servent à décider ; l'âge lui-même est parfois encadré. La question de savoir **quelles variables on a le droit d'utiliser**, et ce qu'on fait de celles qui servent de substitut à des variables interdites, relève du volume III (section 5.4, équité) et du cadre légal local.

### 1.2.7 Choisir

Le comité de risque ne choisit pas sur l'AUC seule. Les critères qui comptent, dans l'ordre où on les rencontre en pratique :

| Critère | Grille | Boosting monotone | Boosting libre |
|---|---|---|---|
| Pouvoir de classement (mesuré ici) | 0,771 | 0,774 | 0,772 |
| Explicabilité d'un refus | directe (points) | par contributions | par contributions |
| Monotonie garantie | oui, si les classes le sont | oui (contraintes) | non |
| Stabilité face à une population qui change | bonne (classes larges) | moyenne | plus fragile |
| Surveillance et validation | outils standard (PSI, tables) | outils standard + explicabilité | plus lourde |
| Traitement des manquants | classe à part, lisible | natif | natif |

Dans la pratique, beaucoup de banques conservent une **grille comme modèle de référence** et la mettent en concurrence avec un modèle plus souple, le **challenger** : si l'écart de performance est faible, comme ici, on garde la grille ; s'il est large et stable, on adopte le challenger **avec ses garde-fous**. C'est la logique de la **rigueur d'évaluation** du volume III : on ne s'incline pas devant la sophistication sans l'avoir mesurée, avec son incertitude.

> ✅ **À retenir.**
> - Sur nos données, trois candidats classent presque aussi bien : la **forme des effets** compte plus que l'algorithme. La grille gagne sur la logistique brute (+0,010 d'AUC, intervalle apparié positif) parce que la vérité n'est pas linéaire ; elle ne perd rien face au boosting (écart de 0,002 dans le bruit).
> - Le **plafond** (la logistique aux vraies formes) vaut 0,777 : il situe les candidats sur l'échelle de ce qui est atteignable.
> - Un modèle de crédit doit être **monotone** quand l'économie l'exige : les contraintes de monotonie ne coûtent ici rien.
> - Un score doit être **calibré** : la grille l'est par construction sur son échantillon, pas forcément ailleurs.
> - Les **motifs de refus** se lisent dans les points perdus ; ils expliquent, ils ne prescrivent pas.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.3, exercices 1.4 et 1.5.


## 1.3 Mesures de performance : Gini, KS, ROC

Un score se juge sur quatre questions distinctes, que l'on confond trop souvent : **classe-t-il bien** (discrimination : AUC, Gini, KS), **annonce-t-il de bonnes probabilités** (calibration), **reste-t-il bon quand la clientèle change** (stabilité), et **avec quelle incertitude** connaît-on ces mesures ? Cette section donne à chaque question son outil, avec les démonstrations qui permettent de les relire, puis un détour par un jeu **réel** pour ne pas croire que tout se passe toujours comme dans nos données simulées.

### 1.3.1 La courbe ROC et l'AUC

Pour un seuil de risque $c$, un dossier est « alerté » si son score de risque dépasse $c$. Deux taux décrivent la règle :

- le **taux de vrais positifs** (TPR, la *sensibilité*) : la part des **mauvais** qui sont alertés ;
- le **taux de faux positifs** (FPR) : la part des **bons** qui sont alertés à tort.

La courbe **ROC** (*receiver operating characteristic*) trace le TPR en fonction du FPR quand le seuil parcourt toutes ses valeurs. Un score aléatoire donne la diagonale ; un score parfait, un angle droit en haut à gauche. L'**AUC**, l'aire sous la courbe, a une interprétation probabiliste directe que l'on retient mieux que l'aire :

$$\text{AUC}=P(S_{\text{mauvais}}>S_{\text{bon}})+\tfrac12\,P(S_{\text{mauvais}}=S_{\text{bon}}),$$

c'est la probabilité qu'un **mauvais** tiré au hasard ait un score de risque **plus élevé** qu'un **bon** tiré au hasard. Calculons-la à la main sur six dossiers : trois mauvais (scores de risque 0,9 ; 0,6 ; 0,4) et trois bons (0,7 ; 0,3 ; 0,2). Il y a $3\times3=9$ paires (un mauvais, un bon) ; comptons celles où le mauvais a le score le plus élevé :

| mauvais | contre 0,7 | contre 0,3 | contre 0,2 | paires gagnées |
|---|---|---|---|---|
| 0,9 | oui | oui | oui | 3 |
| 0,6 | non | oui | oui | 2 |
| 0,4 | non | oui | oui | 2 |

Sept paires sur neuf : $\text{AUC}=7/9\approx0{,}778$.

### 1.3.2 Le Gini et la courbe CAP

Les risquologues préfèrent souvent le **Gini** (ou *accuracy ratio*) : $\text{Gini}=2\,\text{AUC}-1$. Il vaut 0 pour un score aléatoire et 1 pour un score parfait. Dans l'exemple, $2\times\frac79-1=\frac49\approx0{,}444$. D'où vient cette formule ? D'une autre courbe, la **CAP** (*cumulative accuracy profile*), qui classe les dossiers du plus risqué au moins risqué et trace, en fonction de la part de la population examinée, la part des mauvais **capturés**.

> 📐 **Démonstration : Gini = 2·AUC − 1.** Notons $\pi$ la proportion de mauvais dans la population. Quand on examine les dossiers dont le score dépasse un seuil, la part de la population examinée est $x=\pi\,\text{TPR}+(1-\pi)\,\text{FPR}$ et la part des mauvais capturés est $y=\text{TPR}$. L'aire sous la CAP vaut donc
> $$A_{\text{CAP}}=\int \text{TPR}\;d\bigl[\pi\,\text{TPR}+(1-\pi)\,\text{FPR}\bigr]=\pi\int \text{TPR}\,d\text{TPR}+(1-\pi)\int\text{TPR}\,d\text{FPR}=\frac\pi2+(1-\pi)\,\text{AUC}.$$
> Le score aléatoire a une aire de $\frac12$ ; le score parfait capture tous les mauvais dans les premiers $\pi$ de la population, soit une aire de $1-\frac\pi2$. Le **rapport de précision** est le rapport des aires entre le score étudié et l'aléatoire, et entre le parfait et l'aléatoire :
> $$\text{AR}=\frac{A_{\text{CAP}}-\frac12}{(1-\frac\pi2)-\frac12}=\frac{\frac\pi2+(1-\pi)\text{AUC}-\frac12}{\frac{1-\pi}{2}}=\frac{(1-\pi)(\text{AUC}-\frac12)}{\frac{1-\pi}{2}}=2\,\text{AUC}-1.$$
> Le résultat **ne dépend pas de $\pi$** : c'est ce qui permet de comparer des Gini d'un portefeuille à l'autre... sous réserve des précautions de 1.3.7.

Sur nos données, voici le Gini de la grille et les deux courbes :

```python
from sklearn.metrics import roc_auc_score, roc_curve
auc = roc_auc_score(y_te, r_grille)                  # r_grille : risque = − score
fpr, tpr, _ = roc_curve(y_te, r_grille)
print(f"AUC {auc:.3f}   Gini {2 * auc - 1:.3f}   KS {np.max(tpr - fpr):.3f}")
```
<!--sortie-->
```text
AUC 0.771   Gini 0.542   KS 0.406
```


![À gauche, courbes ROC des trois candidats du test ; à droite, courbe CAP de la grille : examiner les 10 % de dossiers les plus risqués capture une part très supérieure de 10 % des mauvais.](figures/ch01-roc-cap.png)

La courbe CAP se lit sans équation : en examinant les 10 % de dossiers que la grille juge les plus risqués, on capture **38 % des mauvais** (un score aléatoire en capturerait 10 %) ; avec 20 % des dossiers, 57 %. Les trois courbes ROC se **confondent presque** : les trois modèles de la section 1.2 sont, pour la discrimination, d'un niveau voisin.

### 1.3.3 Le KS : l'écart maximal entre bons et mauvais

La statistique de **Kolmogorov–Smirnov** mesure la plus grande distance verticale entre les fonctions de répartition des scores des bons et des mauvais :

$$\text{KS}=\max_c\,\bigl|F_{\text{mauvais}}(c)-F_{\text{bon}}(c)\bigr|=\max_c\,\bigl(\text{TPR}(c)-\text{FPR}(c)\bigr).$$

C'est la plus grande différence qu'un seuil unique puisse faire entre la part de mauvais et la part de bons captés. Le point où elle est atteinte est un **seuil naturel** de décision quand on n'a pas d'information de coûts. Le KS est très lu en banque, parce qu'il se résume en un nombre et un seuil.


![Distributions du score des bons et des mauvais (à gauche) et leurs fonctions de répartition (à droite) : le KS est l'écart vertical maximal.](figures/ch01-ks.png)

### 1.3.4 Du score à la politique d'acceptation

Un indicateur de rang ne dit pas **où couper**. La politique d'acceptation se lit dans un tableau de compromis : à chaque seuil, quelle part des demandes accepte-t-on, quel taux de défaut paie-t-on parmi les acceptés, et quel taux auraient eu les refusés ?

```text
 seuil  part acceptée  défaut des acceptés  défaut des refusés
   540         0.9116               0.0417              0.2451
   560         0.7828               0.0312              0.1623
   580         0.5392               0.0202              0.1058
   600         0.2431               0.0154              0.0739
```


Un seuil de 560 points accepte 78 % des demandes pour un taux de défaut de 3,1 % parmi les acceptés (contre 6,0 % sans score) et refuse des dossiers qui auraient fait 16 % de défauts. Monter à 600 points ramène le défaut des acceptés à 1,5 %, au prix de **refuser les trois quarts** des clients. Le bon seuil n'est pas statistique : il dépend du **coût d'un défaut** (la perte de l'exposition, section 1.5) et du **gain d'un bon client** (les intérêts), donc de la marge de la banque. L'AUC ne choisit pas le seuil, elle dit seulement si la courbe de ce compromis est bonne.

### 1.3.5 L'incertitude de la mesure


Une AUC est une **estimation** à partir de 12 000 prêts dont 716 mauvais (volume III, section 5.1 : c'est le nombre de mauvais qui compte). Quelle est sa marge d'erreur ? Un **bootstrap** (volume III, section 1.2) rééchantillonne les lignes du test avec remise et recalcule l'AUC : l'intervalle à 95 % de la grille est **[0,752 ; 0,791]**. L'incertitude est de près de **deux points d'AUC** de chaque côté, alors que les écarts entre modèles de la section 1.2 sont d'un point. C'est pourquoi l'on compare deux modèles par un **intervalle de la différence** sur des rééchantillons **appariés** (les mêmes lignes pour les deux modèles), plus étroit que chaque intervalle pris isolément.

⚠️ Il y a trois sources distinctes d'incertitude : l'**échantillon de test** (ce que mesure le bootstrap), l'**échantillon de développement** (un autre échantillon donnerait une autre grille ; on le mesure en refaisant tout le processus sur des rééchantillons de développement) et la **dérive** future de la population. Seule la première est facile à chiffrer, ce qui explique que les performances réelles soient généralement inférieures à celles du test.

### 1.3.6 Stabilité : la population change

Une grille est utilisée pendant des années. La clientèle, elle, change : la banque s'étend vers les jeunes, la conjoncture se dégrade, une campagne attire un autre profil. Le **PSI** (*population stability index*, volume IV, section 4.7) compare la distribution d'une variable, ou du score, entre la population de développement et la population actuelle :

$$\text{PSI}=\sum_{j}(p_j^{\text{actuel}}-p_j^{\text{dév.}})\,\ln\frac{p_j^{\text{actuel}}}{p_j^{\text{dév.}}}.$$

L'usage place des **repères** : moins de 0,10, la population est stable ; entre 0,10 et 0,25, un changement à examiner ; au-delà, un changement important. Ce sont des conventions, pas des lois.

Simulons un afflux de jeunes emprunteurs et de dossiers très endettés : nous tirons, dans le **jeu de test**, 6 000 prêts avec une probabilité d'autant plus forte que le client a moins de 30 ans ou un taux d'endettement supérieur à 40 %.

```text
                      PSI
score               0.129
âge                 0.246
taux d'endettement  0.149
défaut observé : 0.0893   PD annoncée : 0.0873   AUC : 0.788
```


Le PSI du score dépasse 0,10 et celui de l'âge dépasse 0,20 : l'alarme sonne. Pourtant, le **pouvoir de classement tient** (l'AUC de 0,788 est du niveau de celle du test), et la probabilité annoncée de défaut (8,7 %) reste proche du défaut observé (8,9 %) : la grille a **vu venir** le risque supplémentaire, parce que les nouveaux clients lui ressemblent par leurs variables. Ce qui casserait le score, c'est un changement de la **relation** entre les variables et le défaut (la dérive du concept du volume IV, section 4.7), que le PSI ne voit pas.

### 1.3.7 Calibration : la probabilité annoncée est-elle la bonne ?

La calibration se contrôle **classe de risque par classe de risque**. Les banques regroupent leurs clients en quelques **notes** (une *échelle maîtresse*) auxquelles est attachée une probabilité de défaut. Découpons les dossiers du test en sept notes selon la PD annoncée, et testons, pour chaque note, l'hypothèse « la probabilité de défaut vraie est celle qui est annoncée » par un **test binomial** : sous l'hypothèse, le nombre de défauts d'une note de $n$ dossiers suit une loi binomiale $\mathcal{B}(n,\text{PD})$.

```text
 note  dossiers  PD annoncée  défaut observé  p-valeur
    1       648       0.0077          0.0093    0.6484
    2      2373       0.0152          0.0169    0.5019
    3      2958       0.0269          0.0216    0.0780
    4      2628       0.0458          0.0498    0.3269
    5      1647       0.0766          0.0826    0.3542
    6      1200       0.1367          0.1300    0.5285
    7       546       0.3299          0.3352    0.7850
Hosmer-Lemeshow (10 groupes, 8 degrés de liberté) : 10.50   p-valeur 0.232
```


Les p-valeurs sont élevées (aucune note n'est rejetée au seuil de 5 %), et le test de **Hosmer–Lemeshow**, qui regroupe les dossiers en dix groupes et additionne les écarts $(O_g-E_g)^2/[E_g(1-E_g/n_g)]$ (loi du $\chi^2$ à 8 degrés de liberté), ne rejette pas non plus la calibration. La grille est calibrée **sur cet échantillon**. Le test n'a pourtant qu'une portée limitée, et nous allons voir pourquoi.

#### La conjoncture ruine le test binomial

Le fichier `taux_defaut_macro.csv` donne 80 trimestres de taux de défaut d'un portefeuille de 20 000 prêts (nombre supposé). Le taux moyen est de 3,06 %. Appliquons le test binomial trimestre par trimestre à la PD « moyenne sur le cycle » :


![Taux de défaut trimestriel d'un portefeuille et bande de confiance (95 %) du test binomial autour de la PD moyenne : presque tous les trimestres sortent de la bande.](figures/ch01-cycle-binomial.png)

Le test **rejette 65 trimestres sur 80** : la bande de confiance du test binomial est étroite (± 0,24 point) alors que le taux de défaut oscille entre 1,0 % et 12,8 %. Ces rejets ne disent pas que la PD est mal estimée : ils disent que **le test suppose des défauts indépendants**. Or les défauts d'un portefeuille sont **corrélés par la conjoncture** : une récession touche tous les emprunteurs à la fois. On modélise cette dépendance par un **facteur commun** (modèle de Vasicek, retrouvé au chapitre 4 dans la formule de capital de Bâle) : sous une corrélation d'actifs de seulement 3 %, un test binomial à 5 % rejette à tort la vraie PD **dans 85 % des cas** (simulation de 2 000 portefeuilles de 20 000 prêts, PD vraie de 3 %). La taille du test est pulvérisée.

Deux enseignements à retenir :

- une **PD « sur le cycle »** (*through the cycle*, la moyenne des années) et une **PD « à la date »** (*point in time*, qui suit la conjoncture) répondent à deux questions différentes ; la première sert au capital, la seconde aux provisions (section 1.5) ;
- le **test binomial** est **trop sévère** pour un portefeuille agrégé : les validateurs utilisent des variantes qui intègrent une corrélation (tests de Blochwitz, de Vasicek, test de Jeffreys) ou simplement des seuils de tolérance fixés d'avance. Les noms des variantes varient selon les pratiques ; le point à retenir est l'indépendance supposée.

### 1.3.8 Un détour par des données réelles

Pour ne pas conclure sur des données que nous avons nous-mêmes fabriquées, voici les mêmes mesures sur un **jeu réel** : 30 000 titulaires d'une carte de crédit (source UCI, licence CC0, Yeh et Lien, 2009 ; 22 % de défaut le mois suivant). Les variables sont la limite de crédit, l'âge, le niveau d'études, six mois de **statuts de paiement** (`pay_1` à `pay_6` : −2 = pas de consommation, −1 = payé en totalité, 0 = paiement minimal, 1 à 8 = mois de retard), les montants de facture et de paiement. Deux modèles, entraînés sur 70 % et mesurés sur 30 % :

```text
                                  AUC   Gini     KS
pay_1 seul (nombre)             0.694  0.388  0.383
logistique, tout en nombres     0.728  0.457  0.381
logistique, pay_1 en modalités  0.768  0.536  0.424
boosting                        0.791  0.582  0.448
```


Les chiffres sont d'un autre ordre que ceux de nos prêts simulés (le défaut est près de quatre fois plus fréquent, l'information sur le comportement récent est directe), et l'histoire diffère : la logistique qui prend `pay_1` comme un **nombre** (de −2 à 8) perd beaucoup, parce que l'effet n'est pas linéaire (−2, −1 et 0 sont des statuts de bons payeurs, 2 est déjà une alerte) ; **traiter `pay_1` en modalités**, comme le fait une grille par classes, récupère l'essentiel du gain, et le boosting fait encore un peu mieux (il trouve en plus des interactions). La leçon est celle de 1.2 : **ce sont les formes qui comptent**, et elles se découvrent en regardant les données ; la grille est un bon moyen de ne pas les rater.

### 1.3.9 Les pièges de la mesure

- **L'AUC ne dit rien de la calibration.** Un score qui annoncerait partout deux fois la vraie probabilité classe aussi bien (le rang ne change pas) et se trompe sur chaque prix.
- **L'AUC ignore les coûts.** Deux scores de même AUC peuvent être très différents dans la zone où l'on décide (les 20 % de dossiers les plus risqués, ou le seuil d'acceptation).
- **Le Gini dépend de la population.** Un Gini de 55 % sur la clientèle d'un prêteur n'est pas comparable à un Gini de 45 % sur un portefeuille plus homogène : avec des clients plus semblables, le classement est plus difficile. On ne compare des Gini **qu'à population comparable**.
- **Le Gini de développement est optimiste.** Il se mesure sur l'échantillon où les classes ont été choisies ; la mesure honnête est celle du **test** (et, mieux, d'une période postérieure).
- **Un Gini qui baisse n'est pas toujours un modèle qui vieillit** : il peut refléter un changement de politique d'acceptation (1.1.7).

> ✅ **À retenir.**
> - **AUC** = probabilité qu'un mauvais ait un score de risque plus élevé qu'un bon ; **Gini** = 2·AUC − 1 (démontré par la courbe CAP, indépendant de la proportion de mauvais) ; **KS** = écart maximal TPR − FPR.
> - Les trois mesurent la **discrimination**, pas la **calibration**, pas la **décision** : le seuil se choisit sur un tableau de compromis et sur des coûts.
> - Une AUC s'accompagne de son **intervalle** (bootstrap), et deux modèles se comparent sur des rééchantillons **appariés**.
> - Le **PSI** repère un changement de population ; il ne voit pas une dérive du concept.
> - Le **test binomial** de calibration suppose des défauts indépendants et rejette à tort un portefeuille soumis à la conjoncture ; il faut le compléter par des variantes qui tiennent compte de la corrélation.
> - Sur des données réelles aussi, **les formes des effets** décident de la performance : mesurez, regardez les effets, ne supposez pas.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.4, exercices 1.6 à 1.8.


## 1.4 ➕ WOE/IV et discrétisation des variables

> 🧭 **Section optionnelle.** Elle reprend, avec plus de précision, les classes et le poids de l'évidence de la section 1.1. Vous pouvez passer à 1.5 sans la lire.

La section 1.1 a découpé les variables en classes « à la main ». Cette section répond aux trois questions que pose tout relecteur de la grille : **à quoi sert l'IV, un indicateur très utilisé, et que mesure-t-il vraiment ? Comment découpe-t-on sans arbitraire ? Quels pièges guettent le WOE ?** Le fil conducteur est un avertissement : le WOE et l'IV sont d'excellents outils de **lecture**, et de mauvais juges d'un découpage sans garde-fous.

### 1.4.1 L'information qu'une variable apporte : l'IV

Pour une variable découpée en classes $j=1,\dots,J$, avec $g_j=B_j/B$ la part des bons et $b_j=M_j/M$ celle des mauvais dans la classe $j$, la **valeur d'information** (*information value*, IV) est

$$\text{IV}=\sum_{j=1}^{J}(g_j-b_j)\,\ln\frac{g_j}{b_j}=\sum_{j=1}^J(g_j-b_j)\,\text{WOE}_j.$$

Chaque terme est **positif** : si $g_j>b_j$, le WOE est positif et la différence aussi ; si $g_j<b_j$, les deux sont négatifs. L'IV est donc une somme de termes positifs, nulle seulement si les bons et les mauvais ont la **même distribution** sur les classes. Il a une lecture précise :

> 📐 **L'IV est une divergence symétrisée.** Développons : $\text{IV}=\sum_j g_j\ln\frac{g_j}{b_j}+\sum_j b_j\ln\frac{b_j}{g_j}=\text{KL}(g\,\|\,b)+\text{KL}(b\,\|\,g)$, la somme des deux **divergences de Kullback–Leibler** entre la distribution des bons et celle des mauvais. L'IV mesure donc *à quel point on distingue* les deux populations avec cette variable, dans les deux sens. Les conventions du métier lisent un IV de la façon suivante.

| IV | Lecture usuelle |
|---|---|
| moins de 0,02 | variable sans intérêt |
| de 0,02 à 0,1 | pouvoir prédictif faible |
| de 0,1 à 0,3 | pouvoir prédictif moyen |
| de 0,3 à 0,5 | pouvoir prédictif fort |
| plus de 0,5 | **suspect** : fuite d'information probable |

Ces seuils sont des **conventions de praticiens**, pas des résultats théoriques ; la dernière ligne est la plus utile : un IV trop beau est presque toujours un défaut de construction (nous le provoquons en 1.4.3). Voici les IV de nos dix variables, calculés sur l'échantillon de développement avec les classes de la section 1.1 :

```text
taux_endettement       0.403
anciennete_emploi      0.258
nb_incidents_12m       0.240
revenu_annuel          0.236
age                    0.145
montant                0.071
logement               0.054
anciennete_relation    0.051
duree_mois             0.029
objet                  0.015
```

Le taux d'endettement est de loin le plus informatif (IV 0,40, fort), devant l'ancienneté dans l'emploi, les incidents et le revenu (de 0,24 à 0,26, moyens), l'âge (0,15) ; le montant, l'ancienneté de la relation et le logement sont faibles, la durée et l'objet sont au bord de l'inutilité. Cet ordre est cohérent avec les amplitudes de points de 1.1.6. Les variables d'IV très faible ne coûtent rien à garder, mais elles alourdissent la carte : on en retire souvent sous 0,02 ou 0,03.

⚠️ L'IV est une mesure **univariée** : il ne tient pas compte de la redondance entre variables (le revenu et l'endettement se recoupent), que la régression gère ensuite.

### 1.4.2 Combien de classes ? L'IV grandit avec leur nombre

Si l'on raffine le découpage, l'IV ne peut que croître : il y a plus de façons de séparer bons et mauvais. Cette croissance n'est pas toute de l'information, c'est aussi du **bruit** que l'on apprend. Pour le voir, découpons l'âge en $k$ classes d'effectifs égaux, puis, comme contrôle, une variable de **pur bruit** (un tirage gaussien indépendant du défaut). Pour chaque découpage, nous mesurons l'IV sur l'échantillon de développement, puis la **même quantité** sur l'échantillon de test, avec les WOE appris sur le développement :

```text
 classes  âge dév.  âge test  bruit dév.  bruit test
       3    0.0603    0.0657      0.0001      0.0008
       6    0.1096    0.1268      0.0015     -0.0012
      12    0.1453    0.1594      0.0032     -0.0034
      25    0.1515    0.1617      0.0096     -0.0048
      50    0.1664    0.1712      0.0332     -0.0108
     100    0.1785    0.1725      0.0553     -0.0155
```


L'âge gagne beaucoup entre 3 et 12 classes (0,06 à 0,15) puis plafonne : au-delà, les classes supplémentaires n'ajoutent presque rien sur le test. La variable de **bruit** montre l'autre face : son IV de développement monte à 0,055 avec 100 classes alors qu'elle ne contient **aucune information** ; sur le test, il tombe à zéro ou devient négatif (aucun signal). C'est l'effet qu'on appelle **surapprentissage du découpage**. Deux règles en découlent : on ne choisit pas le nombre de classes en maximisant l'IV de développement, et on regarde toujours l'IV **sur un échantillon de contrôle**.

### 1.4.3 Fusionner pour rendre monotone

Beaucoup de variables ont un effet que l'économie dit **monotone** : plus d'ancienneté dans la relation, moins de risque. Un découpage en classes d'effectifs égaux produit pourtant de petites inversions dues au hasard : le taux de la deuxième classe dépasse celui de la troisième sans raison. L'algorithme classique est la **fusion monotone** : on part de $k=10$ classes d'effectifs égaux et, tant que le taux de défaut n'est pas monotone, on **fusionne les deux classes voisines fautives dont la fusion fait perdre le moins d'IV**. Voici le résultat sur l'ancienneté de la relation, puis sur l'âge :

```text
anciennete_relation
  avant : 10 classes, IV 0.054, taux (%) [8.2 6.8 7.2 6.7 6.3 6.  5.5 5.3 4.6 3.5]
  après : 9 classes, IV 0.054, taux (%) [8.2 7.  6.7 6.3 6.  5.5 5.3 4.6 3.5]
age
  avant : 10 classes, IV 0.138, taux (%) [13.4  6.3  5.8  5.1  4.9  4.5  4.7  4.1  5.3  6.3]
  après : 5 classes, IV 0.127, taux (%) [13.4  6.3  5.8  5.1  5. ]
```


Pour l'ancienneté de la relation, une seule fusion (dix classes deviennent neuf) suffit et l'IV ne bouge pas (0,054) : le découpage monotone est **gratuit**. Pour l'âge, au contraire, la fusion **force** la monotonie là où la vérité est en U : elle regroupe les 25–30 ans avec les suivants et fait **disparaître le sur-risque des plus de 65 ans** (la dernière classe a un taux de 5,0 %, alors que celui des plus de 65 ans est de 8,7 %). L'IV baisse peu (de 0,138 à 0,127), ce qui montre que l'IV ne suffit pas pour juger un découpage : la perte est concentrée dans une zone peu peuplée mais économiquement sensible.

> 🧪 **La monotonie est une hypothèse, pas un dogme.** On l'impose quand elle a un fondement (plus d'endettement, plus de risque ; plus de revenu, moins de risque) et on la **refuse** quand on a de bonnes raisons de voir un U (l'âge) ou un palier (le logement). Une grille dont toutes les variables sont forcément monotones est plus facile à défendre, et parfois moins juste. Dans les deux cas : décidez avant de regarder le résultat, et écrivez la raison.

Les outils qui font cette recherche automatiquement (arbres de décision de profondeur limitée, algorithmes de fusion avec test du $\chi^2$, optimisation par programmation en nombres entiers) donnent des découpages proches. Ce qui compte, c'est le garde-fou : effectifs minimaux, monotonie justifiée, contrôle sur un échantillon à part.

### 1.4.4 Trois pièges du WOE

**Les classes rares.** Si une classe ne contient aucun mauvais, $b_j=0$ et $\text{WOE}_j=\ln(g_j/0)=+\infty$. Même avec peu de mauvais, le WOE est très instable. On le **lisse** en ajoutant une demi-observation à chaque effectif (c'est le choix du code du chapitre) ou en fusionnant la classe avec sa voisine. La section 1.1.7 en a donné un exemple concret : la classe d'endettement de 50 à 60 % de l'échantillon des acceptés ne contenait que 20 prêts et recevait un WOE de +0,66.

**Les manquants informatifs.** Dans nos données, l'ancienneté dans l'emploi manque pour 7 % des prêts, et le défaut y est de 11,9 % contre 5,5 % pour les autres : le fait de ne pas fournir l'information est lui-même un signal. Le garder comme **classe à part** (« manquant », WOE −0,75) conserve ce signal ; l'**imputer** (par la médiane, 6,3 ans) le détruit :

```text
IV de l'ancienneté dans l'emploi, manquant en classe à part : 0.258
IV après imputation par la médiane (6.3 ans)        : 0.163
```


L'imputation fait perdre plus du tiers de l'information de la variable (0,26 contre 0,16). Cela vaut pour la grille ; un modèle d'arbres gère aussi les manquants nativement. Ce qu'il faut éviter, c'est de **supposer que le manquant est neutre**.

**La fuite d'information.** Le dernier piège est le plus coûteux : un IV énorme. Simulons une variable « nombre de retards de paiement du prêt » qui serait connue après la souscription : elle vaut zéro ou presque pour les bons, quelques unités pour les mauvais.

```text
IV de la variable « retards du prêt » : 4.64  (repère de suspicion : 0,5)
```


Un IV de 4,6 (plus de dix fois celui du taux d'endettement) n'est pas une aubaine, c'est **une alarme** : une variable de ce genre n'existe pas à la date de la demande. Quand un IV dépasse nettement 0,5, on ne félicite pas le modèle, on cherche **quand** la variable est connue (volume III, section 1.1).

### 1.4.5 Le WOE est une paramétrisation, pas une magie

Que perd-on à passer par les WOE plutôt que de donner à une régression les **indicateurs de classe** (une variable 0/1 par classe) ? Le WOE impose à chaque variable **un seul** coefficient $\beta_k$ multiplié à des valeurs précalculées, alors que les indicateurs laissent la régression ajuster chaque classe librement. Comparons les deux sur le test :

```text
AUC, grille par WOE            : 0.7712
AUC, indicateurs de classes    : 0.7778
différence (indicateurs - WOE) : +0.0065  [+0.0023 ; +0.0105]
```


Les deux approches sont **très proches** : les indicateurs gagnent 0,007 d'AUC, un écart petit mais réel (l'intervalle apparié, de +0,002 à +0,011, exclut zéro), parce que la régression peut ajuster chaque classe librement au lieu de se plier à un seul coefficient par variable. Le WOE n'est donc pas un gain de précision ; il rend le modèle **plus lisible** : un coefficient par variable, des points qui s'additionnent, la même échelle pour toutes les variables, et un moyen de repérer d'un coup d'œil les classes aberrantes. Il porte aussi un risque que les indicateurs n'ont pas : le WOE est un **encodage par la cible** (volume III, section 4.1), calculé avec les étiquettes ; calculé sur toutes les données avant un découpage de validation, il fuit.

> ✅ **À retenir.**
> - $\text{WOE}_j=\ln\frac{g_j}{b_j}$ ; $\text{IV}=\sum_j(g_j-b_j)\text{WOE}_j=\text{KL}(g\|b)+\text{KL}(b\|g)$ : un indicateur univarié du pouvoir de séparation, lu avec des seuils **conventionnels**, et **suspect au-dessus de 0,5**.
> - L'IV de développement **grandit avec le nombre de classes**, même pour du bruit : on le contrôle sur un échantillon à part et on garde peu de classes lisibles.
> - La **fusion monotone** est gratuite quand l'économie impose la monotonie ; elle **abîme** quand la vérité est en U.
> - Les **manquants** forment souvent une classe informative ; les **classes rares** se lissent ou se fusionnent ; un **IV énorme** est une alarme de fuite.
> - Le WOE est une **paramétrisation commode**, pas une source de performance : les indicateurs de classes font légèrement mieux (+0,007 d'AUC).

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.5, exercices 1.9 et 1.10.


## 1.5 ➕ PD, LGD, EAD et pertes de crédit attendues (IFRS 9)

> 🧭 **Section optionnelle.** Elle prolonge le score vers ce que la comptabilité réclame : un **montant en euros**, la perte que le portefeuille devrait subir. Les paramètres d'exemple (seuils d'étapes, pondérations de scénarios) sont **illustratifs** ; la norme IFRS 9 est citée dans l'état de nos connaissances à la rédaction (2026) et ses exigences exactes sont à vérifier dans le texte en vigueur. Rien ici n'est un conseil comptable.

Un score donne une probabilité. Une banque doit **provisionner** des euros. Le passage de l'un à l'autre est une multiplication de trois grandeurs, que l'on modélise **séparément** parce qu'elles ne s'expliquent pas par les mêmes causes : la **probabilité de défaut** (PD), la **perte en cas de défaut** (LGD, *loss given default*) et l'**exposition au défaut** (EAD, *exposure at default*). La **perte attendue** (*expected credit loss*, ECL) d'un prêt est

$$\text{ECL}=\text{PD}\times\text{LGD}\times\text{EAD}.$$

Pour un prêt de 10 000 € avec une PD de 3 %, une LGD de 45 % et une EAD de 10 000 €, la perte attendue est $0{,}03\times0{,}45\times10\,000=135\ €$. Cette perte n'est pas un risque, c'est un **coût prévisible** : la banque la couvre par le taux d'intérêt et par ses provisions. Le **risque** proprement dit (l'écart autour de cette moyenne) relève du capital (chapitre 4).


### 1.5.1 La PD : douze mois ou toute la vie

Deux horizons coexistent. La **PD à 12 mois** est la probabilité de défaut dans l'année qui vient, celle que donne notre grille. La **PD sur la durée de vie** est la probabilité de défaut avant l'échéance du prêt, forcément plus grande. Si le risque annuel est constant et vaut $h$, la probabilité de **survivre** $t$ années est $(1-h)^t$, d'où

$$\text{PD}_{\text{cumulée}}(T)=1-(1-h)^T,\qquad \text{PD marginale de l'année } t=(1-h)^{t-1}\,h.$$

Pour $h=3\ \%$ : $1-0{,}97^3=8{,}7\ \%$ sur trois ans, $1-0{,}97^5=14{,}1\ \%$ sur cinq ans, avec des probabilités marginales de défaut de 3,00 %, 2,91 %, 2,82 %… qui diminuent un peu parce qu'il reste moins de survivants. L'hypothèse d'un risque constant est une simplification : en réalité, le risque dépend de l'âge du prêt, de la conjoncture et de la note, qui migre (section 1.6 donne la version « matrice de transition » de la même idée).

> 💡 **Pourquoi deux PD ?** Parce que la norme IFRS 9 demande de provisionner tantôt sur un an, tantôt sur la vie entière, selon l'état du prêt (1.5.5). La PD à 12 mois de la grille ne suffit pas toujours.

### 1.5.2 La LGD : ce que l'on perd vraiment

La LGD est la **part de l'exposition que l'on ne récupère pas** après le défaut : $\text{LGD}=1-\dfrac{\text{récupérations actualisées}}{\text{EAD}}$. Elle dépend de la **garantie** (une caution, un nantissement), du **recouvrement** (frais, délais) et du moment. Le fichier `recouvrements.csv` donne, pour 6 000 prêts entrés en défaut, la perte réellement subie en part de l'exposition, supposée **déjà actualisée** (c'est la convention de ce chapitre) ; il indique aussi le délai de recouvrement, d'une durée moyenne de 19 mois et demi, car un euro récupéré dans près de vingt mois vaut moins d'un euro aujourd'hui (à 6 % par an, environ 0,91 €).

Regardons d'abord la **distribution**, qui n'a rien d'une cloche :


![Distribution de la perte en cas de défaut : en U (beaucoup de pertes quasi nulles ou quasi totales), et très différente selon la garantie.](figures/ch01-lgd.png)

La LGD moyenne est de 46 %. La forme est **en U** : 12 % des prêts sont intégralement récupérés (perte nulle), 9 % ne le sont presque pas du tout (perte supérieure à 95 %), et le reste se répartit entre les deux. La moyenne par garantie est très contrastée : **61 %** sans garantie (2 993 prêts), **37 %** avec nantissement (1 155 prêts), **27 %** avec caution (1 852 prêts).

Comment modéliser une grandeur bornée entre 0 et 1, en forme de U ? Quatre candidats, comparés sur 30 % de prêts de test (garantie, objet et montant comme variables) :

- la **moyenne globale** (la référence naïve) ;
- la **régression linéaire**, qui peut sortir de $[0,1]$ ;
- la **régression « fractionnelle »** : un GLM binomial avec lien logit, appliqué à la LGD prise comme une proportion (volume II, section 2.2 pour le lien logit), qui reste dans $[0,1]$ ;
- un **modèle en deux étapes** : la probabilité d'une perte nulle (régression logistique), puis la LGD moyenne parmi les pertes non nulles (régression fractionnelle).

```text
                           erreur absolue    RMSE      R²
moyenne globale                    0.3063  0.3443 -0.0003
régression linéaire                0.2591  0.3047  0.2165
régression fractionnelle           0.2591  0.3048  0.2163
deux étapes                        0.2591  0.3048  0.2163
vraie espérance (plafond)          0.2577  0.3049  0.2158
```


Les trois modèles font **exactement aussi bien** (erreur absolue 0,259, $R^2=0{,}216$) et dépassent nettement la moyenne globale (0,306 ; $R^2$ nul). Le plafond lui-même, la vraie espérance conditionnelle connue par construction, n'est pas plus haut : **ce que l'on prédit de la LGD d'un prêt individuel est très limité**. La garantie explique la **moyenne** d'un segment, mais, à l'intérieur d'un segment, les pertes restent dispersées entre 0 et 1. La précision d'une LGD se juge donc **par segment**, et l'erreur individuelle importe peu pour une provision de portefeuille (où seule la moyenne compte).

⚠️ Trois précautions. D'abord, le recouvrement est **tardif et censuré** : les défauts récents n'ont pas fini de se recouvrer, et leur LGD observée est trop basse (on les exclut, ou on projette). Ensuite, les LGD sont **plus fortes en période de crise** (garanties moins valorisées, recouvrements plus lents) : les approches réglementaires demandent une LGD « de ralentissement » (*downturn*), ce que notre fichier ne permet pas d'estimer. Enfin, la régression linéaire peut sortir de $[0,1]$ avec d'autres variables ; ici, avec trois variables catégorielles, elle s'en abstient et l'écart n'apparaît pas.

### 1.5.3 L'EAD : ce que l'on aura prêté au moment du défaut

Pour un prêt amortissable, l'exposition à une date est connue (un tableau d'amortissement). Pour une **ligne de crédit renouvelable** (découvert, carte), le client peut **tirer** davantage avant de faire défaut. On modélise l'exposition au défaut par

$$\text{EAD}=\text{tirage}+\text{CCF}\times(\text{limite}-\text{tirage}),$$

où le **facteur de conversion en crédit** (CCF, *credit conversion factor*) est la part du montant **non tiré** qui sera tirée avant le défaut. Dans `revolving_defauts.csv`, 8 000 lignes qui ont fait défaut, avec leur tirage un an avant :

```text
            utilisation_moy  ccf_moyen
quintile 1            0.137      0.495
quintile 2            0.272      0.443
quintile 3            0.383      0.414
quintile 4            0.506      0.357
quintile 5            0.691      0.299
EAD réelle totale 23.8 M€ ; tirages un an avant 14.5 M€ ; EAD par CCF moyen 23.4 M€
```


Le CCF moyen est de 0,40 : en moyenne, **40 % de ce qui n'était pas tiré l'est avant le défaut**. Il est plus fort pour les lignes **peu utilisées** (0,50 dans le premier quintile d'utilisation, 0,30 dans le dernier) : un client en difficulté vide sa réserve. Retenir comme EAD le tirage d'un an avant donnerait 14,5 M€ pour 23,8 M€ réellement exposés : l'exposition serait **sous-estimée de 39 %**. Appliquer le CCF moyen donne 23,4 M€, à 2 % de la réalité ; une régression du CCF sur l'utilisation (pente −0,35, $R^2$ de 0,10) est un progrès modeste. Comme pour la LGD, la moyenne est bien estimée, le détail individuel beaucoup moins.

### 1.5.4 IFRS 9 : trois étapes

La norme **IFRS 9** (en vigueur depuis 2018, dans l'état de nos connaissances ; à vérifier) remplace le provisionnement sur pertes **subies** par un provisionnement sur pertes **attendues**. Le principe est un classement des prêts en **trois étapes** (*stages*) :

| Étape | Situation du prêt | Provision |
|---|---|---|
| **1** | risque de crédit **pas sensiblement accru** depuis l'octroi | perte attendue à **12 mois** |
| **2** | risque de crédit **sensiblement accru** depuis l'octroi, sans défaut | perte attendue **sur la durée de vie** |
| **3** | **défaut avéré** | perte attendue sur la durée de vie, sur un prêt en défaut (PD = 1) |

L'idée est **prospective** : on n'attend pas le défaut pour provisionner, on le fait dès que le risque se dégrade nettement. La norme laisse à chaque établissement la définition précise de la « hausse sensible » ; elle fournit seulement des présomptions (un retard de plus de 30 jours signale en général une hausse sensible, un retard de plus de 90 jours un défaut). Nos **règles d'exemple**, sur les 20 000 prêts de `portefeuille_ifrs9.csv`, sont :

- étape **3** : retard de 90 jours ou plus ;
- étape **2** : retard de 30 jours ou plus, **ou** PD actuelle supérieure à 2,5 fois la PD d'origine, **ou** prêt restructuré ;
- étape **1** : tous les autres.

```text
         prets   ead_M  ecl_M  couverture_%
etape                                      
1      16607.0  251.65   2.92          1.16
2       2923.0   43.43   1.78          4.09
3        470.0    7.32   2.89         39.48
total  20000.0  302.41   7.59          2.51
```


Le portefeuille compte 16 607 prêts en étape 1, 2 923 en étape 2 et 470 en étape 3, pour une exposition de 302 M€ et une **perte attendue totale de 7,6 M€** (2,5 % de l'exposition). La **couverture** (perte attendue rapportée à l'exposition) croît fortement d'une étape à l'autre : 1,2 % pour l'étape 1, 4,1 % pour l'étape 2, 39 % pour l'étape 3. Le passage d'une étape à l'autre est un **effet de seuil** : si l'on provisionnait **tout le portefeuille sur 12 mois**, la perte attendue serait de 4,1 M€ ; **tout sur la durée de vie**, de 6,7 M€, soit 1,6 fois plus, pour une durée résiduelle moyenne de 3,7 ans. Un prêt qui bascule en étape 2 voit donc sa provision **augmenter d'un coup**, ce qui rend le résultat de la banque **sensible aux règles de basculement**, un point que les régulateurs et les auditeurs examinent de près.

La perte attendue d'un prêt en étape 2 est la **somme sur les années** de sa vie résiduelle : probabilité de défaut dans l'année $t$ ($(1-h)^{t-1}h$, avec $h$ la PD annuelle), perte en cas de défaut et exposition à cette date (qui diminue avec l'amortissement), **actualisés** au taux d'intérêt effectif du prêt. Le détail est dans le cahier (application 1.7).

### 1.5.5 Le regard vers l'avant : les scénarios

IFRS 9 demande que la perte attendue reflète des **informations prospectives**, donc la conjoncture attendue et non seulement celle d'hier. Les établissements calculent la perte sous **plusieurs scénarios macroéconomiques** et en font une **moyenne pondérée par leur probabilité**. Pour traduire un scénario en PD, on s'appuie sur la relation historique entre conjoncture et défauts, celle de `taux_defaut_macro.csv` : une régression du logit du taux de défaut trimestriel sur la croissance, le chômage et la variation de l'immobilier.

```text
const            -5.030
croissance_pib   -0.401
chomage           0.245
variation_immo   -0.063
R² = 0.989
             croissance  chômage  immobilier  défaut modélisé (%)  poids  ECL (M€)
central             1.4      8.2         0.6                 2.61    0.5      7.59
défavorable        -1.0      9.5        -2.5                10.51    0.3     19.89
favorable           2.4      7.4         2.5                 1.29    0.2      5.27
```


La régression explique l'essentiel des variations du logit du taux de défaut ($R^2=0{,}99$ sur l'historique) : un point de croissance en moins multiplie la cote de défaut par 1,5 (+49 %), un point de chômage en plus de 28 %. Le scénario **central** (la conjoncture moyenne de l'historique) donne 2,6 % de défaut ; le **défavorable** (récession modérée, chômage à 9,5 %, immobilier en baisse), 10,5 % ; le **favorable**, 1,3 %. Nous multiplions la PD de chaque prêt par le rapport entre le taux du scénario et celui du central (les étapes restent fixes pour simplifier : dans la réalité, un scénario défavorable fait aussi **basculer** des prêts en étape 2).

La perte attendue vaut 7,6 M€ dans le scénario central, 19,9 M€ dans le défavorable (multipliée par 2,6) et 5,3 M€ dans le favorable. Pondérées à 50 / 30 / 20 %, elles donnent une **perte attendue pondérée de 10,8 M€**, soit environ **43 % de plus que le central**. Un point mérite d'être compris : la perte au **scénario moyen** (la conjoncture pondérée : croissance 0,9 %, chômage 8,4 %) serait de 9,1 M€, **moins** que la perte pondérée des trois scénarios : la perte est une fonction **convexe** de la conjoncture (un mauvais scénario coûte plus que ce que gagne un bon), si bien que moyenner la conjoncture **sous-estime** la perte moyenne de 1,7 M€. C'est la raison pour laquelle la norme demande plusieurs scénarios et non un scénario « moyen ».

Enfin, la **sensibilité** de la provision à la PD est quasi linéaire pour les étapes 1 et 2 : une PD multipliée par 2 donne 11,9 M€ (1,6 fois la perte centrale, pas 2 fois, parce que l'étape 3, 2,9 M€, est insensible à la PD) et multipliée par 3, 16,0 M€.

⚠️ **Limites.** Les scénarios et leurs pondérations sont des **jugements**, que les auditeurs examinent ; la relation macro-défaut est estimée sur 80 trimestres d'**un seul portefeuille** ; les PD de `portefeuille_ifrs9.csv` sont supposées déjà « à la date » ; la LGD de ce fichier n'est pas ralentie.

> ✅ **À retenir.**
> - $\text{ECL}=\text{PD}\times\text{LGD}\times\text{EAD}$ : trois grandeurs modélisées séparément. La perte attendue est un **coût prévisible**, pas un risque.
> - **PD** : à 12 mois ou sur la vie ($1-(1-h)^T$ si le risque est constant). **LGD** : en U, très liée à la garantie, **peu prévisible individuellement** (les trois modèles testés ont le même $R^2$ de 0,22, plafond compris) mais bien estimée par segment. **EAD** : le CCF capte la part tirée avant le défaut (0,40 en moyenne) ; ignorer le tirage futur sous-estime l'exposition de 39 %.
> - **IFRS 9** : étape 1 (12 mois), étape 2 (durée de vie, après hausse sensible du risque), étape 3 (défaut). Le passage de 1 à 2 multiplie la provision (de 1,6 en moyenne ici).
> - Les **scénarios** pondérés remplacent un scénario moyen : la perte est **convexe** en la conjoncture, moyenner la conjoncture sous-estime la perte.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.6 et 1.7, exercices 1.11 et 1.12.


## 1.6 ➕ Migration de notations et matrices de transition

> 🧭 **Section optionnelle.** Elle étudie la **dynamique** du risque : une note n'est pas figée, elle monte et descend, et la probabilité qu'un emprunteur fasse défaut dans cinq ans dépend de ce chemin.

Les banques et les agences de notation rangent les emprunteurs dans une **échelle de notes** (ici de 1, la meilleure, à 7, la plus risquée) et suivent leur évolution chaque année. Le tableau des probabilités de passer d'une note à une autre est la **matrice de transition**. Elle sert à trois choses : estimer la probabilité de défaut **à plusieurs années** (1.6.4), anticiper la **dégradation** d'un portefeuille (c'est un moteur des étapes IFRS 9 de la section 1.5), et simuler des scénarios de crise. Cette section l'estime sur dix ans de notes, la compare à la **vérité programmée**, et montre pourquoi une matrice « moyenne » trompe en période de crise.


### 1.6.1 Qu'est-ce qu'une matrice de transition ?

Notons $X_t$ la note d'un emprunteur à la fin de l'année $t$, dans $\{1,\dots,7\}$, plus l'état **défaut** (noté 8). La matrice de transition annuelle $P$ a pour coefficient $P_{ij}=P(X_{t+1}=j\mid X_t=i)$ : chaque **ligne** est une distribution de probabilité (la somme vaut 1). Deux propriétés la structurent :

- le **défaut est absorbant** : un emprunteur en défaut y reste ($P_{88}=1$) ; la matrice complète est donc de taille $8\times8$, dont nous estimons les 7 premières lignes ;
- les notes bougent **peu** : la **diagonale** domine (on garde la même note le plus souvent), et les passages d'une note à la voisine sont bien plus fréquents que les sauts de plusieurs crans.

La dernière colonne est la **probabilité de défaut à un an** de chaque note : c'est le lien avec tout ce qui précède. Voici la matrice **vraie** utilisée pour simuler les données (une année « neutre », sans choc de conjoncture) :

```text
           1     2     3     4     5     6     7  défaut
note 1  91.5   7.0   1.0   0.3   0.1   0.0   0.0     0.1
note 2   4.0  88.0   6.0   1.2   0.4   0.2   0.1     0.1
note 3   0.5   6.0  86.0   5.5   1.2   0.4   0.2     0.2
note 4   0.2   1.0   7.0  83.0   6.2   1.5   0.6     0.5
note 5   0.1   0.3   1.2   7.5  80.0   7.0   2.2     1.7
note 6   0.0   0.2   0.4   1.5   8.0  76.0   8.0     5.9
note 7   0.0   0.0   0.2   0.5   2.0   9.0  60.0    28.3
```

Lecture : un emprunteur noté 4 a 83,0 % de chances de rester en 4, 7,0 % de passer en 3 (amélioration), 6,2 % en 5, et **0,5 % de faire défaut dans l'année**. La note 7, la plus risquée, fait défaut dans plus d'un cas sur quatre (28,3 %).

### 1.6.2 Estimer par cohortes

L'estimation la plus simple s'appelle la **méthode des cohortes** : pour chaque note de départ $i$, on compte parmi les emprunteurs notés $i$ en début d'année combien se retrouvent dans l'état $j$ en fin d'année, et l'on divise :

$$\widehat P_{ij}=\frac{N_{ij}}{N_{i\cdot}}.$$

C'est l'estimateur du maximum de vraisemblance d'un modèle multinomial, indépendamment pour chaque ligne. Il reste une question pratique : que fait-on des emprunteurs **dont la note est retirée** (sortie du portefeuille, remboursement anticipé, perte de contact) ? On les compte à part et on les **retire du dénominateur** de l'année : l'hypothèse est que leur sortie n'informe pas sur leur risque, ce qui est une hypothèse (elle est vraie dans nos données, où 4 % sortent chaque année au hasard ; elle est souvent fausse dans la réalité, où l'on sort plus volontiers quand tout va bien, ou quand tout va très mal).

Voici les effectifs de transitions du panel (5 000 emprunteurs suivis jusqu'à dix ans, 39 102 observations « emprunteur-année »), avant la division :

```text
        sortie     1     2     3     4     5     6    7  défaut
note 1      96  2150   205    29     1     2     0    0       1
note 2     280   254  5669   447    91    31    16    6       6
note 3     404    55   605  8401   625   174    46   26      23
note 4     390    26    91   653  7770   650   163   75      55
note 5     215     2     8    56   416  4179   439  141     109
note 6     115     0     5     3    44   174  1977  279     186
note 7      37     0     0     0     5    20    87  702     387
```

Les effectifs sont très inégaux : 10 359 emprunteurs-années pour la note 3, 1 238 pour la note 7. Les transitions rares (un saut de la note 1 à la note 5) reposent sur quelques cas ou aucun, d'où l'importance de l'**incertitude**. Pour la mesurer, on rééchantillonne les **emprunteurs** (et non les lignes : les années d'un même emprunteur ne sont pas indépendantes) : c'est un bootstrap par grappes.


```text
        PD vraie (%)  PD estimée (%)  IC bas  IC haut
note 1           0.1            0.04    0.00     0.13
note 2           0.1            0.09    0.03     0.19
note 3           0.2            0.23    0.15     0.33
note 4           0.5            0.58    0.44     0.73
note 5           1.7            2.04    1.65     2.45
note 6           5.9            6.97    6.14     8.00
note 7          28.3           32.22   29.59    34.71
```


La probabilité de défaut estimée est **systématiquement supérieure** à la vraie pour les notes risquées (7,0 % contre 5,9 % pour la note 6, 32,2 % contre 28,3 % pour la note 7), et la vraie valeur sort de l'intervalle de confiance pour deux notes sur sept (6 et 7) : ce n'est pas un défaut de l'estimateur, mais une **révélation**. La matrice vraie décrit une année neutre ; or le panel contient dix années dont **deux de récession**, qui augmentent les dégradations. La matrice estimée est donc une **moyenne sur le cycle**, plus sombre qu'une année neutre. Voyons-le.


![À gauche, matrice de transition estimée par cohortes ; à droite, son écart avec la matrice vraie d'une année neutre : la diagonale est plus faible et les dégradations plus fortes.](figures/ch01-migration.png)

### 1.6.3 La conjoncture déforme la matrice

Séparons les années. Le taux de défaut de l'ensemble du panel et la part d'emprunteurs **dégradés** (note de fin plus mauvaise que celle de début) varient fortement :

```text
annee               0        1        2        3        4        5        6        7        8        9
emprunteurs   5000.00  4755.00  4517.00  4268.00  4041.00  3814.00  3527.00  3260.00  3046.00  2874.00
defauts_pct      1.10     1.07     1.44     1.34     1.76     3.64     4.17     2.39     1.77     1.74
degrades_pct     7.42     7.00     8.10     9.98    12.00    19.87    19.14    11.60     7.78     6.40
```


Les années 5 et 6 se détachent : le taux de défaut passe de 1,1–1,8 % les années ordinaires à 3,6–4,2 %, et la part de dégradations passe de 6–12 % à près de 20 %. Comparons les matrices estimées sur **deux sous-périodes** : les années calmes (0 à 3, 8 et 9) et la récession (5 et 6).

```text
        PD calme (%)  PD récession (%)  défauts calme  défauts récession  rapport
note 1          0.07              0.00              1                  0     0.00
note 2          0.08              0.08              3                  1     1.04
note 3          0.13              0.49              8                  9     3.85
note 4          0.45              1.11             28                 18     2.46
note 5          1.39              4.71             46                 49     3.38
note 6          4.95             14.07             79                 76     2.84
note 7         24.49             51.55            167                133     2.11
```


Pour les notes de milieu d'échelle (de 3 à 6), la **probabilité de défaut est multipliée par 2,5 à 3,9** en récession : pour la note 5, de 1,4 % à 4,7 %. Pour les deux premières notes, les défauts sont si rares (de zéro à trois par sous-période) que le rapport n'a pas de sens : c'est la limite de toute estimation de transitions rares. Pour la note 7, le rapport est de 2,1 seulement : une PD déjà élevée (24,5 % en période calme) ne peut pas être multipliée par plus de 4. Le facteur programmé dans le simulateur, qui multiplie les probabilités brutes de dégradation par $e^{0{,}6\,\Delta z}\approx2{,}75$ avant renormalisation, retrouve cet ordre de grandeur.

> 💡 **« Sur le cycle » ou « à la date » ?** La matrice moyenne (1.6.2) convient à un horizon long et au capital, qui doit survivre à une crise. La matrice d'une année donnée (ou d'un état de la conjoncture) convient aux provisions (section 1.5), qui doivent refléter la situation et les perspectives. Utiliser la moyenne pour provisionner **sous-estime** la perte d'une récession et **surestime** celle d'une expansion. Les établissements estiment pour cela des matrices **conditionnelles** à un indicateur de conjoncture, ce que l'on fait ici de la façon la plus simple : une matrice par régime.

### 1.6.4 La probabilité de défaut à plusieurs années

La force d'une matrice est de donner la PD à **horizon $n$ années**. Si les transitions sont indépendantes d'une année à l'autre (propriété de Markov) et si la matrice est la même chaque année (homogénéité), la matrice à $n$ ans est la puissance $n$ de la matrice annuelle : $P^{(n)}=P^n$. Avec le défaut absorbant, la dernière colonne de $P^n$ est la **probabilité de défaut cumulée** à $n$ ans pour chaque note de départ.

```python
M_abs = np.vstack([M_hat, np.r_[np.zeros(7), 1.0]])       # ajoute la ligne « défaut → défaut » : l'état est absorbant
PD_5 = np.linalg.matrix_power(M_abs, 5)[:7, 7]             # défaut cumulé à 5 ans, note par note
print((100 * PD_5).round(1))
```
<!--sortie-->
```text
[ 0.4  1.2  2.7  6.5 17.  39.3 76.5]
```

À 5 ans, la note 1 a 0,4 % de risque cumulé et la note 7 en a 76,5 % : trois emprunteurs sur quatre sont en défaut avant cinq ans. Comparons cette prédiction à ce que l'on observe réellement, en suivant la **cohorte initiale** (les 5 000 emprunteurs de l'année 0, suivis sur cinq ans, les retraits étant traités comme des sorties sans défaut), et à la valeur vraie $P^5$ de la matrice neutre :

```text
        matrice estimée (%)  matrice vraie (%)  cohorte 0 observée (%)
note 1                  0.4                0.6                     0.5
note 2                  1.2                1.0                     0.8
note 3                  2.7                2.0                     1.1
note 4                  6.5                5.0                     5.2
note 5                 17.0               13.3                    10.8
note 6                 39.3               31.7                    28.1
note 7                 76.5               69.5                    63.0
```


![Probabilité de défaut cumulée selon l'horizon, pour quatre notes de départ : la matrice estimée sur dix ans (trait plein) est plus sombre que la matrice neutre (tirets), et l'écart se creuse avec l'horizon.](figures/ch01-pd-cumulee.png)

Trois lectures. **Premièrement**, la PD cumulée croît **plus vite que proportionnellement** au nombre d'années pour les notes **bonnes** (note 3 : 2,7 % à 5 ans pour 0,23 % à un an, soit douze fois plus pour cinq fois plus de temps), parce que ces emprunteurs migrent d'abord vers des notes plus risquées avant de faire défaut ; elle s'**aplatit** pour les notes très mauvaises (saturation). **Deuxièmement**, la matrice estimée donne des PD à 5 ans plus fortes que la matrice neutre (note 5 : 17,0 % contre 13,3 %), puisqu'elle intègre la récession : les erreurs **se cumulent** avec l'horizon. **Troisièmement**, la cohorte de l'année 0, qui traverse les années 0 à 4, donc **avant** la récession, observe moins de défauts que les deux matrices (note 5 : 10,8 %) : la matrice annuelle moyenne n'est ni la cohorte passée ni la cohorte à venir. L'écart n'est pas une erreur de calcul : c'est la différence entre **la moyenne du cycle** et **un morceau particulier du cycle**.

### 1.6.5 Les hypothèses : Markov, homogénéité

Le calcul $P^n$ suppose deux choses, qu'on **teste** avant de s'y fier.

**La propriété de Markov** : la note de demain ne dépend que de celle d'aujourd'hui, pas du chemin parcouru. Dans la réalité, il existe souvent un **effet d'élan** (*momentum*) : un emprunteur récemment dégradé a plus de chances de l'être encore que celui qui est resté stable. Testons-le sur les emprunteurs notés 4 : sont-ils plus risqués s'ils viennent de **plus haut** (ils ont été dégradés), de **plus bas** (ils se sont améliorés) ou s'ils étaient déjà 4 l'année précédente ?

```text
col_0                         amélioré  défaut  dégradé  inchangé  sorti
origine                                                                 
vient d'une note meilleure         7.1     0.4      9.2      80.7    2.6
vient d'une note moins bonne       8.7     0.9      9.6      77.5    3.3
était déjà 4                       7.7     0.6      9.5      78.1    4.2
test du khi-deux d'indépendance : p = 0.49
```


Les distributions d'issue sont **semblables** quelle que soit l'origine (la probabilité de dégradation reste autour de 9 à 10 %, celle de défaut, sous 1 %) et le test d'indépendance donne $p=0{,}49$ : nous **ne détectons aucun effet d'élan**, ce qui est cohérent avec la vérité, puisque nos données ont été simulées avec des transitions de Markov. Sur des données réelles, ce test conclut souvent le contraire, et l'on enrichit alors le modèle (l'état devient la note **et** la note précédente, ou la durée dans la note).

**L'homogénéité dans le temps** est, elle, manifestement **fausse** ici : on vient de voir que deux années sur dix multiplient les défauts par trois. Un test d'homogénéité formel compare les matrices de deux périodes (khi-deux de comparaison ligne par ligne) ; il rejette massivement pour les notes de milieu d'échelle. Conséquence pratique : la puissance $P^n$ d'une matrice moyenne est une **approximation**, valable en moyenne sur un cycle et trompeuse un jour de crise.

### 1.6.6 Un mot sur le temps continu

Une année est un pas arbitraire : on voudrait la probabilité de transition sur six mois, ou sur dix-huit. Le modèle à **temps continu** décrit les transitions par un **générateur** $Q$ (taux instantanés de passage d'une note à l'autre) tel que $P(t)=e^{tQ}$. On l'obtient formellement par le **logarithme matriciel** $Q=\ln P$, que l'on peut calculer sur la matrice estimée :

```text
coefficients hors diagonale négatifs : 7  (le plus bas : -0.001)
[[-0.107  0.097  0.01  -0.001]
 [ 0.044 -0.145  0.079  0.013]
 [ 0.005  0.071 -0.176  0.074]]
```


Le logarithme de la matrice estimée contient 7 **taux négatifs** (très petits : −0,001 au plus bas, dans les transitions les plus rares), ce qui n'a pas de sens pour un taux de passage. Une matrice annuelle est dite **plongeable** (*embeddable*) quand un générateur valide existe ; l'estimée ne l'est pas. On la **régularise** alors (on remplace les taux négatifs par zéro et l'on renormalise la diagonale) ou l'on estime directement le générateur à partir des durées passées dans chaque note, ce qui est une autre méthode (l'estimateur de durée, à temps continu). Retenez la précaution : **la racine carrée ou le logarithme d'une matrice de transition n'est pas toujours une matrice de transition**.

> ✅ **À retenir.**
> - Une **matrice de transition** est une matrice stochastique dont la dernière colonne est la PD à un an ; le défaut est **absorbant**. L'estimateur par **cohortes** est un simple rapport d'effectifs ; son incertitude se mesure par un bootstrap **par emprunteur**.
> - Les **transitions rares** sont mal estimées ; les notes extrêmes ont peu d'observations.
> - La conjoncture **déforme** la matrice : en récession, la PD des notes intermédiaires est multipliée par 2,5 à 3,9 dans nos données. Une matrice moyenne sert le capital, une matrice conditionnelle sert les provisions.
> - La PD à $n$ ans est la dernière colonne de $P^n$, sous les hypothèses de **Markov** et d'**homogénéité**, qu'on teste : ici, pas d'effet d'élan, mais une forte hétérogénéité temporelle.
> - Le logarithme d'une matrice estimée n'est pas toujours un générateur valide.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.8, exercices 1.13 et 1.14.


## Bilan du chapitre 1

Vous savez maintenant :

- **cadrer** un score de crédit : population, définition du défaut, fenêtres d'observation et de performance, échantillons, et le garde-fou contre la fuite d'information (ne garder que ce que l'on sait à la date de la demande) ;
- **construire une grille de score** : découper en classes, calculer les **WOE** (à la main sur un exemple), estimer une régression logistique, écrire le résultat en **points** avec un score de base et un PDO, lire une carte et en expliquer un refus par ses **motifs** ;
- **mesurer l'effet des dossiers refusés** : une grille construite sur les seuls acceptés annonce 4,4 % de défaut alors que la population qui se présente en fait 6,0 % ;
- **comparer** une grille, une logistique brute et un boosting monotone sur un échantillon de test, avec des intervalles appariés, et comprendre **pourquoi** (la forme des effets, révélée par la vérité programmée) ;
- **mesurer** un score : AUC, **Gini = 2·AUC − 1** (démontré par la courbe CAP), **KS**, tableau de seuils, intervalle de bootstrap, **PSI**, calibration par note (test binomial, Hosmer–Lemeshow) et ses limites quand la conjoncture corrèle les défauts ;
- (en option) **juger un découpage** : IV (une divergence de Kullback–Leibler symétrisée), fusion monotone, classes rares, manquants informatifs, IV suspect ;
- (en option) **chiffrer une perte attendue** : PD à 12 mois et sur la vie, LGD (en U, peu prévisible individuellement), CCF et EAD, **trois étapes IFRS 9**, scénarios macroéconomiques pondérés et effet de convexité ;
- (en option) **estimer une matrice de migration**, voir la conjoncture la déformer, calculer une PD à plusieurs années par puissance de matrice, **tester** Markov et noter les limites de l'homogénéité et du temps continu.

Le chapitre a mis des chiffres sur des idées qui restent souvent des slogans :

| Question | Ce que nous avons mesuré |
|---|---|
| Performance de la grille (test) | AUC 0,771 [0,752 ; 0,791], Gini 0,542, KS 0,406 |
| Grille contre logistique brute | +0,010 d'AUC, intervalle apparié [+0,001 ; +0,018] |
| Grille contre boosting monotone | −0,002 d'AUC, dans le bruit ; plafond (vraies formes) : 0,777 |
| Politique d'acceptation à 560 points | 78 % de demandes acceptées, 3,1 % de défaut parmi les acceptés |
| Grille construite sur les acceptés seuls | AUC 0,716 au lieu de 0,771 ; PD annoncée 4,4 % pour 6,0 % réels |
| Afflux de jeunes emprunteurs | PSI du score 0,129, de l'âge 0,246 ; la grille reste calibrée (8,7 % annoncés, 8,9 % observés) |
| Test binomial, 80 trimestres | 65 rejets ; sous une corrélation d'actifs de 3 %, il rejette à tort 85 % du temps |
| Jeu réel (carte de crédit) | AUC 0,728 (tout en nombres), 0,768 (statut en modalités), 0,791 (boosting) |
| IV d'une variable de bruit | 0,055 en développement, −0,016 en test (100 classes) |
| Ancienneté dans l'emploi | IV 0,258 avec le manquant en classe à part, 0,163 après imputation |
| LGD | moyenne 46 % (61 % sans garantie, 27 % avec caution) ; $R^2$ de 0,22, plafond compris |
| EAD d'une ligne renouvelable | CCF moyen 0,40 ; EAD sous-estimée de 39 % si l'on ignore les tirages futurs |
| Perte attendue IFRS 9 | 7,6 M€ (2,5 % de 302 M€) ; 10,8 M€ en pondérant trois scénarios, soit 43 % de plus |
| Migration en récession | PD des notes intermédiaires multipliée par 2,5 à 3,9 |
| PD à 5 ans de la note 5 | 17,0 % (matrice estimée), 13,3 % (matrice neutre), 10,8 % (cohorte observée avant la récession) |

Le fil conducteur du chapitre tient en une phrase : **un score de crédit est une cote écrite en points, et sa valeur se mesure par des indicateurs qui répondent à des questions différentes** (classe-t-il bien, est-il calibré, est-il stable, avec quelle incertitude). Chaque fois que nous avons comparé des modèles, la sophistication a apporté moins que la **forme des effets** et la **qualité des données** ; chaque fois que nous avons traduit un score en euros, l'hypothèse sur la conjoncture a pesé davantage que le modèle.

> 🧭 **En pratique : liste de contrôle d'un score de crédit.**
> 1. La population, la définition du défaut et les fenêtres sont écrites (1.1.2).
> 2. Aucune variable n'est postérieure à la date de la demande ; aucun IV n'est anormalement élevé (1.4.4).
> 3. Les classes sont assez peuplées, justifiées, monotones quand l'économie l'exige (1.1.3, 1.4.3).
> 4. Les refusés sont discutés : l'échantillon est-il représentatif des demandeurs (1.1.7) ?
> 5. Gini, KS, AUC sont donnés **avec leur intervalle**, sur un échantillon de test (1.3.5).
> 6. La calibration est contrôlée par note, avec un test qui tient compte de la corrélation (1.3.7).
> 7. La stabilité est surveillée (PSI du score et des variables, 1.3.6).
> 8. Les motifs de refus se lisent dans la carte (1.2.6).
> 9. La PD alimente une perte attendue avec LGD, EAD et scénarios documentés (1.5).

Le chapitre suivant change de métier, pas de logique : l'**assurance**. Une mutuelle ne prête pas, elle **promet** de payer des sinistres ; son risque est la **fréquence** et le **coût** de ces sinistres, que l'on modélise séparément et que l'on transforme en **prix** (un tarif) et en **provisions**, un chemin parallèle à celui de la PD, de la LGD et de l'EAD.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 à 1.8 (grille complète, inférence des rejets, comparaison de modèles, performance et stabilité, WOE et fusion monotone, LGD et CCF, perte attendue IFRS 9, matrice de migration) et exercices 1.1 à 1.14.


---

# Chapitre 2 : Modélisation actuarielle

> « Vendre une promesse avant d'en connaître le coût : voilà le métier. »

Une mutuelle d'assurance vend, aujourd'hui, une garantie dont le coût ne sera connu que dans plusieurs mois, parfois dans plusieurs années. Elle doit pourtant fixer **le prix** de cette garantie (la tarification), puis **mettre de côté l'argent** que les sinistres déjà survenus coûteront encore (le provisionnement). Ces deux décisions reposent sur des modèles statistiques, et ce sont celles dont la banque, dans le chapitre précédent, n'a pas d'équivalent exact : l'assureur *inverse le cycle de production*. Il encaisse d'abord, il paie ensuite, et l'écart entre les deux est un **risque** qu'il lui revient de mesurer.

Ce chapitre est le cœur technique du volume pour qui travaille en assurance. Il reprend des outils que vous connaissez déjà (modèles linéaires généralisés du volume II, validation hors période du volume III) et leur donne leur vocabulaire de métier : fréquence, sévérité, prime pure, chargements, triangle de développement, provision. Il repose sur une idée directrice : **un modèle d'assurance n'est jamais jugé sur sa vraisemblance, mais sur ce qui se passe l'année suivante**. Les données étant simulées, nous aurons même le luxe, rare, de comparer nos estimations à la **vérité programmée**.

## Le chemin de ce chapitre

- **2.1 Modèles de fréquence et de sévérité** : on sépare le coût d'un contrat en un *nombre* de sinistres et un *montant* par sinistre ; on apprend à compter (Poisson, binomiale négative), à décrire des montants à queue lourde (Gamma, Pareto généralisée) et à reconstituer la charge annuelle d'un portefeuille (modèle collectif).
- **2.2 Tarification et construction du tarif** : de la prime pure au tarif commercial ; deux modèles (fréquence × sévérité) ou un seul (Tweedie) ; validation sur une année qu'on n'a pas utilisée ; ce que coûte un tarif trop grossier (antisélection).
- **2.3 Provisionnement des sinistres** : le triangle de développement, la méthode *chain ladder*, la queue, et comment juger une provision *a posteriori*.
- **➕ 2.4 GLM tarifaires et théorie de la crédibilité** : sous le capot du GLM (déviance, tests, splines, régularisation), crédibilité de Bühlmann–Straub, comparaison avec un boosting.
- **➕ 2.5 Chain ladder, Bornhuetter–Ferguson, Mack, bootstrap** : quatre façons d'estimer une provision *et son incertitude*, et ce qui les met en défaut.
- **➕ 2.6 Assurance santé** : coûts, sélection adverse, aléa moral, table de morbidité.

Les sections 2.4 à 2.6 sont **facultatives** : elles approfondissent sans conditionner la suite. Le chapitre 6 (réassurance) reprend la sévérité à queue lourde de la section 2.1 ; le chapitre 3 (mesures de risque) et le chapitre 4 (Solvabilité) reprennent les quantiles de la charge annuelle.

## Les données du chapitre

> 📦 **Données (simulées).** Quatre jeux, fabriqués par `build/donnees5.py` avec des graines fixes. **Rien n'est réel** : la mutuelle, ses assurés et leurs sinistres sont fictifs, et c'est ce qui permet de révéler, en fin d'étude, les paramètres programmés.
> - `polices_auto.csv` : 100 000 lignes *police-année* (2022 à 2024), avec l'exposition (fraction d'année couverte), le conducteur (âge), le véhicule (âge, puissance), la zone (« Zone A » à « Zone F »), le bonus-malus, l'usage, le carburant et le nombre de sinistres.
> - `sinistres_auto.csv` : les 5 722 sinistres correspondants, matériels (90 %) ou corporels (10 %), avec leur montant.
> - `triangle_rc.csv`, `triangle_dommages.csv`, `triangle_choc.csv` : trois triangles de paiements (dix années de survenance), avec leurs fichiers `*_verite.csv` qui contiennent les paiements **futurs** réels.
> - `sante_assures.csv` : 39 112 lignes *assuré-année* avec les coûts par poste (section 2.6).

Nous suivrons une règle simple pour la tarification : **on estime sur 2022 et 2023, on juge sur 2024**. Les montants sont **revalorisés en euros de 2024** quand on compare des années entre elles (l'inflation des coûts est de l'ordre de 4 % par an).


## Une règle de lecture pour tout le chapitre

Dans ce volume, **un chiffre de modèle n'est jamais donné seul** : on l'accompagne de son incertitude, ou d'une comparaison avec la vérité quand on l'a. C'est le fil rouge de la série depuis le volume III (« la rigueur d'évaluation »), et il est plus important encore ici : un tarif ou une provision engage de l'argent, et l'écart entre un chiffre *précis* et un chiffre *juste* se paie.


## 2.1 Modèles de fréquence et de sévérité

Un contrat d'assurance automobile produit, sur une année, soit rien (le plus souvent), soit un sinistre, soit rarement plusieurs. Quand il y a sinistre, son montant va de quelques centaines d'euros à plusieurs millions. Cette section **sépare ces deux sources d'aléa**, parce qu'elles n'obéissent ni aux mêmes lois ni aux mêmes facteurs de risque, puis les **recompose** pour décrire ce que le portefeuille coûtera sur une année.

### 2.1.1 Le coût d'un contrat : un nombre, puis un montant

Notons $N$ le nombre de sinistres d'un contrat sur la période et $X_1,\dots,X_N$ leurs montants. Le **coût total** est
$$S=\sum_{k=1}^{N}X_k,\qquad S=0\ \text{si } N=0.$$
C'est la structure du **modèle collectif** : $N$ est la *fréquence* (une variable de comptage), les $X_k$ forment la *sévérité* (des montants positifs). On suppose d'ordinaire que les $X_k$ sont **indépendants entre eux et indépendants de $N$**, et de même loi. Ces hypothèses sont fausses de mille façons (un orage provoque beaucoup de sinistres à la fois), mais elles donnent un point de départ calculable, et nous verrons à la fin de la section ce qu'elles coûtent.

**Un exemple à la main.** Cinq contrats, une année chacun :

| Contrat | Sinistres $N$ | Montants (€) | Coût $S$ (€) |
|---|---|---|---|
| 1 | 0 | — | 0 |
| 2 | 1 | 1 800 | 1 800 |
| 3 | 0 | — | 0 |
| 4 | 2 | 900 ; 2 400 | 3 300 |
| 5 | 0 | — | 0 |

La fréquence moyenne est $3/5=0{,}6$ sinistre par contrat et par an. La sévérité moyenne est $(1\,800+900+2\,400)/3=1\,700$ €. Le coût moyen par contrat est $5\,100/5=1\,020$ €, et l'on retrouve bien $0{,}6\times1\,700=1\,020$ : **le coût moyen est le produit de la fréquence moyenne par la sévérité moyenne**. Cette égalité, démontrée plus bas, est le fondement de toute la tarification.

Voyons nos données. Chaque ligne de `pol` est un contrat sur une année, avec son **exposition** (la fraction de l'année pendant laquelle le contrat a été en vigueur : 0,5 pour un contrat résilié en juin).

```python
resume = pol.groupby("annee").agg(contrats=("id_police", "size"), exposition=("exposition", "sum"),
                                  sinistres=("nb_sinistres", "sum"))
resume["frequence"] = resume["sinistres"] / resume["exposition"]     # sinistres par année d'exposition
print(resume.round(3))
```
<!--sortie-->
```text
       contrats  exposition  sinistres  frequence
annee                                            
2022      30244   26199.870       1679      0.064
2023      32741   28320.718       1907      0.067
2024      37015   32080.943       2136      0.067
```

Les années-contrats d'exposition augmentent d'une année à l'autre (le portefeuille grandit), et la fréquence reste proche de 6,6 % : c'est ce qu'on attend d'un portefeuille stable.

### 2.1.2 Compter les sinistres : Poisson et exposition

Le modèle de référence pour un nombre de sinistres est la **loi de Poisson** :
$$P(N=k)=e^{-\mu}\frac{\mu^k}{k!},\qquad E[N]=\mathrm{Var}(N)=\mu.$$
Elle a une justification : si des sinistres surviennent indépendamment les uns des autres, à un rythme constant, le nombre de sinistres sur une durée donnée suit une loi de Poisson. Pour un contrat d'exposition $e_i$ et de **taux annuel** $\lambda$, on pose donc $N_i\sim\mathrm{Poisson}(e_i\lambda)$ : un contrat couvert six mois a deux fois moins de chances d'avoir un sinistre qu'un contrat d'un an. L'exposition entre dans le modèle comme un **décalage** (en anglais *offset*) : $\ln\mu_i=\ln e_i+\ln\lambda$, c'est-à-dire une variable explicative dont le coefficient est imposé égal à 1.

> 📐 **Estimateur du taux.** La log-vraisemblance de $n$ contrats est $\ell(\lambda)=\sum_i\bigl[N_i\ln(e_i\lambda)-e_i\lambda-\ln N_i!\bigr]$. En dérivant, $\ell'(\lambda)=\sum_i N_i/\lambda-\sum_i e_i=0$, d'où
> $$\hat\lambda=\frac{\sum_i N_i}{\sum_i e_i}.$$
> Le taux estimé est le **nombre total de sinistres divisé par l'exposition totale**, pas par le nombre de contrats. L'information de Fisher vaut $\sum_i e_i/\lambda$, donc $\mathrm{Var}(\hat\lambda)\approx\lambda/\sum_i e_i$ : l'incertitude ne dépend que de l'exposition totale.

Sur nos données, $\hat\lambda=6{,}61$ % par année d'exposition, avec une erreur-type de 0,09 point (pour une exposition totale de 86 602 années). Si l'on avait divisé par le nombre de contrats plutôt que par l'exposition, on aurait obtenu 5,72 %, un taux **sous-estimé** de 13 % parce que les contrats incomplets comptent pour une année entière : une erreur classique, silencieuse, et qui fausse le prix.

> ⚠️ **Exposition ou nombre de contrats ?** Le dénominateur d'une fréquence est la durée de couverture, pas le nombre de lignes. Un tarif construit avec des fréquences « par contrat » sous-estime systématiquement le risque quand le portefeuille contient beaucoup de contrats incomplets (nouvelles affaires en cours d'année, résiliations).

### 2.1.3 Quand la variance dépasse la moyenne : la binomiale négative

La loi de Poisson impose $\mathrm{Var}(N)=E[N]$. Or, dans un portefeuille réel, deux contrats de mêmes caractéristiques observables n'ont pas le même risque : l'un conduit prudemment, l'autre non. Ce risque **non observé** ajoute de la variabilité. Modélisons-le par un facteur aléatoire $\Theta$ de moyenne 1 : sachant $\Theta$, le nombre de sinistres est Poisson de moyenne $\mu\Theta$. Si $\Theta$ suit une loi Gamma de moyenne 1 et de variance $\alpha$, la loi de $N$ devient une **binomiale négative**, et l'on a :
$$E[N]=\mu,\qquad \mathrm{Var}(N)=E[\mathrm{Var}(N\mid\Theta)]+\mathrm{Var}(E[N\mid\Theta])=\mu+\alpha\mu^2.$$

> 📐 **Poisson–Gamma = binomiale négative.** Posons $r=1/\alpha$ ; $\Theta\sim\mathrm{Gamma}(r,\text{taux } r)$. Alors
> $$P(N=k)=\int_0^\infty e^{-\mu\theta}\frac{(\mu\theta)^k}{k!}\,\frac{r^r\theta^{r-1}e^{-r\theta}}{\Gamma(r)}\,d\theta=\frac{\Gamma(k+r)}{k!\,\Gamma(r)}\Bigl(\frac{r}{r+\mu}\Bigr)^{r}\Bigl(\frac{\mu}{r+\mu}\Bigr)^{k},$$
> la loi binomiale négative de paramètres $r$ et $p=r/(r+\mu)$. Quand $\alpha\to0$ (pas d'hétérogénéité), on retrouve la loi de Poisson.

Une vérification numérique rassure : en simulant un million de contrats avec $\mu=1$ et $\alpha=0{,}5$, la variance empirique vaut 1,50 pour une valeur théorique de $\mu+\alpha\mu^2=1{,}5$.

Quelle est l'ampleur du phénomène sur notre portefeuille ? Le taux de sinistres étant faible, la sur-dispersion y est discrète : le rapport variance sur moyenne d'un contrat vaut $1+\alpha\mu\approx1+0{,}4\times0{,}066$, soit environ $1{,}03$. Un modèle de Poisson avec les variables explicatives donne une **dispersion de Pearson** de 1,027 ; un modèle binomial négatif estime $\hat\alpha=0{,}47$ avec une erreur-type de 0,09. L'estimation est imprécise (la variance est un moment d'ordre deux) mais elle écarte nettement zéro. La **vérité programmée** est $\alpha=0{,}4$ : l'estimation en est à moins de deux erreurs-types.

Pourquoi s'en préoccuper si l'effet est si discret ? Parce qu'il se paie dans les **queues** : les contrats à plusieurs sinistres sont bien plus fréquents que ne le prévoit Poisson.

```text
           observé  Poisson  binomiale négative
0            94559  94471.3             94556.0
1             5168   5340.7              5180.0
2              265    183.1               250.9
3 et plus        8      5.0                13.1
```


Le tableau compare, parmi 100 000 contrats, le nombre de contrats ayant 0, 1, 2 ou 3 sinistres et plus avec ce que prévoit chaque modèle (en utilisant les moyennes ajustées contrat par contrat) : Poisson prévoit 183,1 contrats à deux sinistres, la binomiale négative 250,9, et l'on en observe 265. À trois sinistres ou plus : 5,0, 13,1 et 8 observés. Les écarts sont modestes en valeur absolue mais systématiques : **Poisson sous-estime les contrats à sinistres multiples**, et la binomiale négative les rattrape.

> 🧪 **Zéros en excès ?** On pense parfois à des modèles « à excès de zéros » quand il y a beaucoup de contrats sans sinistre. Ici le tableau montre que les zéros sont correctement prévus par les deux lois (la masse en zéro est portée par le faible taux de sinistres, pas par une population de contrats « immunisés »). Un modèle à inflation de zéros n'aurait rien apporté. À réserver aux cas où le diagnostic le justifie (volume II, section 2.6).

### 2.1.4 La sévérité : des montants très asymétriques

Passons aux montants. Les sinistres sont ici de deux natures : **matériels** (une carrosserie) et **corporels** (une personne blessée). Le tableau, en euros de 2024, donne l'effectif, la moyenne, la médiane et le maximum de chaque type.

```text
          effectif  moyenne  mediane  maximum
type                                         
corporel       576    55383    10315  2576725
materiel      5146     2733     2338    16694
```

Deux phrases résument le tableau. **Pour les sinistres matériels**, moyenne et médiane sont voisines (2 733 et 2 338 €) : la loi est modérément asymétrique. **Pour les sinistres corporels**, la moyenne (55 383 €) est **plus de cinq fois la médiane** (10 315 €) : quelques sinistres énormes tirent la moyenne vers le haut, jusqu'à 2 576 725 € pour le plus grand. Dans un tel cas, **la moyenne est instable** : retirer le sinistre le plus coûteux d'une année la fait varier de plusieurs points.


La loi **Gamma** convient bien aux sinistres matériels : elle est positive, asymétrique, et à moyenne $\mu$ et forme $k$ elle a pour variance $\mu^2/k$, donc un **coefficient de variation** constant $1/\sqrt k$. Un Gamma de moyenne dépendant des variables est justement le modèle linéaire généralisé de sévérité (section 2.2). Sur les sinistres matériels, la forme estimée est $\hat k=2{,}34$ (coefficient de variation 0,65) ; la forme programmée est 2,5. Le coefficient de la puissance est 0,050 (valeur programmée : 0,05) et l'inflation estimée atteint 4,4 % par an (valeur programmée : 4 %).

Pour les sinistres corporels, aucune loi usuelle ne tient d'un bout à l'autre : le corps de la distribution ressemble à une lognormale, mais les grands montants s'étirent beaucoup plus que ne le permet une lognormale. Deux outils décrivent ce comportement.

**Le graphique des montants en échelle logarithmique** montre les deux populations : les sinistres matériels se concentrent entre 1 000 et 10 000 €, les corporels s'étalent de quelques dizaines d'euros à plusieurs millions.

**La fonction d'excès moyen** $e(u)=E[X-u\mid X>u]$ mesure, pour un seuil $u$, ce que l'on perd *en moyenne au-delà du seuil*. Pour une loi **à queue légère** (exponentielle, Gamma), $e(u)$ devient constante ou décroît ; pour une loi **à queue lourde** de type Pareto, $e(u)$ **croît avec $u$**. L'empirique, calculée sur tous les sinistres, croît nettement : à $u=10\,000$ €, un sinistre qui dépasse ce seuil le dépasse en moyenne de 88 264 € ; à $u=100\,000$ €, de 170 057 €.


![À gauche : densité des montants (échelle logarithmique) des sinistres matériels et corporels, en euros de 2024. À droite : fonction d'excès moyen empirique ; sa croissance indique une queue lourde.](figures/ch02-severite.png)

### 2.1.5 La queue : seuil, loi de Pareto généralisée et gros sinistres

Quand les grands sinistres dominent, on les modélise à part. Le théorème de **Pickands, Balkema et de Haan** (volume II, section 6.5) dit que, pour presque toute loi, les excès au-delà d'un seuil $u$ assez élevé suivent approximativement une **loi de Pareto généralisée** (GPD) :
$$P(X-u>y\mid X>u)=\Bigl(1+\xi\,\frac{y}{\sigma}\Bigr)^{-1/\xi},\qquad y>0,$$
d'**indice de queue** $\xi>0$ pour une queue lourde. L'indice $\xi$ commande tout : les moments d'ordre $m$ n'existent que si $\xi<1/m$. Avec $\xi>0{,}5$, **la variance est infinie** ; avec $\xi>1$, la moyenne l'est aussi. La sévérité programmée contient une queue de Pareto d'indice $\alpha=1{,}8$, soit $\xi=1/\alpha\approx0{,}56$ : la variance de ces sinistres est donc, en théorie, infinie. On le sait ici parce que c'est nous qui l'avons programmé.

Reste à choisir **le seuil**, compromis classique : trop bas, le modèle GPD est mal ajusté (biais) ; trop haut, il reste trop peu d'excès (variance). On ajuste donc la GPD pour plusieurs seuils et l'on regarde si $\hat\xi$ se **stabilise**.


```text
 seuil  excès   xi   echelle
 30000    167 0.47  77945.91
 50000    128 0.39  98897.00
 75000    101 0.40 107026.44
100000     91 0.66  72867.30
150000     48 0.40 156753.45
200000     34 0.27 217089.33
```

![Indice de queue estimé de la loi de Pareto généralisée selon le seuil, avec son intervalle de confiance à 95 % obtenu par rééchantillonnage ; la ligne en pointillé donne la valeur de la queue de Pareto programmée.](figures/ch02-gpd.png)

On lit trois choses. D'abord, $\hat\xi$ varie de 0,27 à 0,66 selon le seuil : **il ne se stabilise pas nettement**. Ensuite, l'intervalle de confiance à 100 000 € (avec seulement 91 excès) va de 0,35 à 0,93 : il contient la valeur programmée de 0,56, mais aussi des valeurs pour lesquelles la moyenne même serait presque infinie. Enfin, la raison de cette instabilité est instructive : la sévérité corporelle programmée est un **mélange** d'une lognormale (à queue modérée) et d'une queue de Pareto, de sorte que les seuils bas mélangent deux comportements. Aucune loi simple ne s'ajuste, et les chiffres de queue sont **incertains** de façon irréductible.

> ⚠️ **Se méfier d'un indice de queue précis.** Un $\hat\xi$ à trois décimales est une illusion avec une centaine d'observations dans la queue. Une conclusion tarifaire ne doit pas dépendre de la deuxième décimale : on teste la sensibilité (seuils, intervalles), et l'on reste prudent sur les quantiles extrêmes.

**Pourquoi la queue compte autant.** Les 91 sinistres de plus de 100 000 € ne représentent que 1,6 % des sinistres, mais **53 % du coût total**. Les dix plus grands pèsent à eux seuls 20 % du coût, les cinquante plus grands 43 %. Le coût d'un portefeuille automobile dépend donc d'une poignée de sinistres, dont la sévérité n'est connue qu'avec peine.

**L'écrêtement.** La pratique courante est de **ne pas laisser ces sinistres bruiter le tarif** : on plafonne chaque sinistre à un seuil $c$ (ici 100 000 €), on estime les modèles sur les montants écrêtés $\min(X,c)$, et l'on ajoute une **charge pour gros sinistres** commune à tous les contrats :
$$E[X]=E[\min(X,c)]+E[(X-c)_+],\qquad\text{charge}=\frac{\text{somme des excès au-delà de } c}{\text{exposition totale}}.$$
On répartit uniformément la partie imprévisible (qui est surtout du hasard) et l'on réserve la segmentation à la partie ordinaire. Nous l'utiliserons en section 2.2. La réassurance (chapitre 6) est l'autre réponse : transférer cette queue à un tiers.

### 2.1.6 Le modèle collectif : la charge annuelle du portefeuille

Reconstituons maintenant le coût total $S=\sum_{k=1}^N X_k$ d'un portefeuille. Le raisonnement par conditionnement donne, sous les hypothèses d'indépendance de la section 2.1.1 :
$$E[S]=E[N]\,E[X],\qquad \mathrm{Var}(S)=E[N]\,\mathrm{Var}(X)+\mathrm{Var}(N)\,E[X]^2.$$

> 📐 **Démonstration.** Sachant $N=n$, $E[S\mid N=n]=nE[X]$ et $\mathrm{Var}(S\mid N=n)=n\mathrm{Var}(X)$. Donc $E[S]=E\bigl[E[S\mid N]\bigr]=E[N]E[X]$ et, par la formule de la variance totale, $\mathrm{Var}(S)=E[N]\mathrm{Var}(X)+\mathrm{Var}(N)E[X]^2$. Pour un nombre de Poisson, $\mathrm{Var}(N)=E[N]$ et $\mathrm{Var}(S)=E[N]\,E[X^2]$.

La première relation est **l'égalité de la prime pure** annoncée plus haut : le coût moyen est le produit de la fréquence moyenne par la sévérité moyenne (démontrée ici, utilisée en section 2.2). La seconde dit que **la variance de la charge vient de deux sources** : la variabilité des montants et celle du nombre de sinistres.

**Application à l'année 2024.** L'exposition de 2024 est de 32 081 années. Avec le taux estimé, le nombre de sinistres attendu est de 2 120. Pour la sévérité, on rééchantillonne les montants observés (revalorisés en euros de 2024). On simule 2 000 années : le nombre de sinistres tiré selon Poisson, les montants tirés avec remise.


![Distribution de la charge annuelle du portefeuille obtenue en simulant 2 000 années (nombre de sinistres de Poisson, montants tirés dans l'historique) ; la ligne rouge est le quantile à 99,5 %, la ligne orange pointillée la charge réellement observée en 2024.](figures/ch02-charge.png)

La simulation donne une charge moyenne de 17,1 M€ et un écart-type de 2,43 M€ ; les formules en forme close donnent 17,0 M€ et 2,43 M€, un accord qui valide les deux. Le **quantile à 99,5 %** de la charge annuelle vaut 23,9 M€, soit 6,8 M€ au-dessus de la moyenne (2,8 écarts-types). C'est exactement le genre de chiffre que la réglementation Solvabilité demande de calculer (chapitre 4, section 4.2).

La charge réellement observée en 2024 est de 13,7 M€ (en euros courants) : à 1,4 écarts-types **sous** la moyenne simulée. Ce n'est pas nécessairement une erreur du modèle : c'est une année où la queue ne s'est presque pas manifestée. Le tableau compare, année par année, la charge attendue avec le taux moyen et la sévérité moyenne (tout en euros de 2024) et la charge observée.

```text
 année  attendu (M€ 2024)  observé (M€ 2024)
  2022               13.9               15.3
  2023               15.0               17.0
  2024               17.0               13.7
```

Les deux premières années dépassent l'attendu, la dernière est nettement en dessous, et sur les trois années les écarts se compensent presque : 46,0 M€ observés pour 46,0 M€ attendus. C'est le signe d'un modèle **bien centré** et d'une charge annuelle **très variable**, ce que dit déjà l'écart-type de 2,4 M€.

> ⚠️ **Ce que cette simulation suppose.** Trois choses, toutes discutables : (1) les montants sont tirés dans les 5 722 sinistres observés, donc **la queue au-delà du maximum observé n'existe pas** dans la simulation (or c'est là que se trouvent les quantiles extrêmes) ; (2) le nombre de sinistres est de Poisson pur, sans la sur-dispersion de la section 2.1.3 ni la corrélation entre contrats (un orage, une épidémie) ; (3) les montants sont indépendants du nombre. Le quantile à 99,5 % estimé ici est donc un **plancher plausible**, pas un chiffre fiable à l'euro près.

### 2.1.7 Les paramètres programmés, enfin révélés

| Quantité | Vérité programmée | Estimation |
|---|---|---|
| Fréquence annuelle moyenne | environ 6,5 % | 6,61 % |
| Variance de l'hétérogénéité $\alpha$ | 0,4 | 0,47 (erreur-type 0,09) |
| Forme du Gamma (matériel) | 2,5 | 2,34 |
| Effet de la puissance sur la sévérité | 0,05 | 0,050 |
| Inflation annuelle des coûts | 4 % | 4,4 % |
| Indice de queue corporel | 0,56 | 0,66 à 100 k€ (de 0,35 à 0,93) |

Tout est retrouvé à l'erreur d'estimation près, **sauf ce qui reste fragile par nature** : l'hétérogénéité et l'indice de queue. C'est une leçon de méthode : les paramètres d'un cœur de distribution se retrouvent bien avec peu de données, ceux d'une queue ou d'une variance non observée demandent beaucoup plus.

> ✅ **À retenir.**
> - Le coût d'un contrat est $S=\sum_{k\le N}X_k$ ; sa moyenne est le produit de la **fréquence moyenne** par la **sévérité moyenne**.
> - La fréquence s'estime par **sinistres sur exposition** ; le dénominateur n'est jamais le nombre de contrats.
> - La loi de Poisson impose $\mathrm{Var}=\text{moyenne}$ ; l'hétérogénéité non observée donne une **binomiale négative** ($\mathrm{Var}=\mu+\alpha\mu^2$), visible surtout dans les queues.
> - La sévérité est asymétrique : les sinistres matériels se décrivent par un **Gamma**, les grands sinistres par une **loi de Pareto généralisée** dont l'indice de queue est **incertain** ; on **écrête** et l'on met une charge pour gros sinistres.
> - Le **modèle collectif** reconstruit la charge annuelle ; son quantile à 99,5 % est le chiffre qu'attend la réglementation, et il est fragile.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 à 2.3 et exercices 2.1 à 2.3 (comptage et exposition, binomiale négative, queue et écrêtement, modèle collectif).


## 2.2 Tarification et construction du tarif

Tarifer, c'est répondre à une question simple en apparence : **combien faut-il demander à ce contrat pour que, en moyenne, la mutuelle couvre ses sinistres, ses frais et sa marge ?** La difficulté est que « ce contrat » n'a jamais existé : on ne connaît que des contrats voisins, observés dans le passé. Cette section construit un tarif en trois temps : une **prime pure** (le coût moyen attendu), les **chargements** qui la transforment en prix, puis une **validation** sur une année que les modèles n'ont pas vue.

### 2.2.1 La prime pure

La **prime pure** d'un contrat de caractéristiques $x$ est l'espérance de son coût annuel : $\pi(x)=E[S\mid x]$. En reprenant le résultat de la section 2.1.6 *à $x$ fixé*, et sous l'hypothèse que fréquence et montants sont indépendants sachant $x$,
$$\pi(x)=\underbrace{E[N\mid x]}_{\text{fréquence}}\times\underbrace{E[X\mid x]}_{\text{sévérité moyenne}}.$$

**Un exemple à la main.** Deux segments d'exposition égale.

| Segment | Fréquence annuelle | Sévérité moyenne (€) | Prime pure (€) |
|---|---|---|---|
| Jeunes conducteurs | 10 % | 2 500 | $0{,}10\times2\,500=250$ |
| Autres conducteurs | 5 % | 2 400 | $0{,}05\times2\,400=120$ |

Le segment des jeunes coûte plus du double, **presque entièrement à cause de la fréquence** ; la sévérité y est à peine plus élevée. Cette décomposition est précieuse : elle dit *pourquoi* un segment est cher, et donc quelle variable explicative sert à quoi. Le prix d'un contrat est ainsi une **mécanique multiplicative** : on part d'un coût de base et on le multiplie par des **relativités** (jeune : ×1,9 ; zone chère : ×1,4 ; etc.). C'est exactement la structure d'un modèle linéaire généralisé à lien logarithmique.

> ⚠️ **L'indépendance fréquence–sévérité est une hypothèse.** Elle est assez bien vérifiée en automobile matériel ; elle l'est moins quand les mêmes facteurs agissent sur les deux (une puissance élevée augmente à la fois le nombre et la gravité des accidents), ce qui se traite en mettant les variables dans les deux modèles. Pour des garanties où un sinistre en entraîne d'autres (catastrophes naturelles), elle est franchement fausse.

### 2.2.2 Deux modèles linéaires généralisés, un tarif


**La fréquence.** On ajuste un modèle de Poisson à lien logarithmique avec l'exposition en décalage (volume II, section 2.3), sur les années 2022 et 2023 :

```python
formule = ("nb_sinistres ~ C(classe_age, Treatment('40-49')) + puissance + C(zone, Treatment('Zone C'))"
           " + bonus_malus + C(usage) + C(carburant) + age_vehicule")
freq = smf.glm(formule, tr, family=sm.families.Poisson(), offset=np.log(tr["exposition"])).fit()
```

Les coefficients, exponentiés, sont des **relativités** : $e^{\beta}=1{,}35$ pour la zone F signifie que, toutes choses égales par ailleurs, un contrat de la zone F produit 35 % de sinistres de plus qu'un contrat de la zone C (référence). Comme la vérité est connue, comparons-les (l'intervalle est à 95 %) :


```text
                              estimée    bas   haut  vérité
relativité                                                 
zone A (réf. : zone C)          0.891  0.787  1.008   0.819
zone D                          1.096  0.993  1.210   1.083
zone E                          1.338  1.206  1.485   1.197
zone F                          1.377  1.223  1.549   1.350
18-24 ans (réf. : 40-49 ans)    1.923  1.703  2.171   1.733
puissance, par niveau           1.058  1.039  1.078   1.041
bonus-malus, par 10 points      1.067  1.041  1.092   1.062
usage professionnel             1.153  1.054  1.261   1.105
```

Sur 8 relativités comparées, 7 ont leur valeur programmée dans l'intervalle de confiance à 95 %, ce qui est à peu près ce que l'on attend (une sur vingt peut en sortir par hasard). La plus éloignée est la zone E (1,34 estimé pour 1,20 programmé). Mais un tarif n'est pas une collection de coefficients : il est **corrélé** (les jeunes conducteurs ont un bonus-malus plus élevé), et les coefficients ne se lisent qu'ensemble.

**La sévérité.** Les sinistres matériels et corporels n'ont pas les mêmes facteurs : on les sépare. Pour les **matériels**, un GLM Gamma à lien logarithmique ; pour les **corporels**, trop peu nombreux (362 sur 2022-2023) et trop dispersés pour se laisser segmenter, on retient une moyenne unique après écrêtement à 100 000 €. La **sévérité moyenne** d'un contrat est alors le mélange
$$E[X\mid x]=(1-q)\,\mu_{\text{mat}}(x)+q\,m_{\text{cor}},$$
où $q=10{,}1$ % est la part de sinistres corporels et $m_{\text{cor}}=29 686$ € leur moyenne écrêtée. À cela s'ajoute la **charge pour gros sinistres** de la section 2.1.5 : 234 € par année d'exposition, la même pour tous.

```python
mat_tr = st[st["type"] == "materiel"]                     # sinistres matériels de 2022-2023, en euros de 2024
sev = smf.glm("rev ~ puissance + C(zone, Treatment('Zone C'))", mat_tr,
              family=sm.families.Gamma(sm.families.links.Log())).fit(scale="X2")
```


Pour la puissance, le coefficient de sévérité estimé est 0,050 par niveau (0,05 programmé), et les relativités de zone de la sévérité sont, pour les zones chères, **plus faibles** que celles de la fréquence : la zone agit surtout sur la probabilité d'avoir un sinistre, moins sur son coût.

Sur les contrats de 2024, la prime pure annuelle prédite vaut 591 € en moyenne. Elle va de 446 € (5ᵉ centile) à 855 € (95ᵉ centile), un rapport de 1,9 entre les 5 % de contrats les moins chers et les 5 % les plus chers.


### 2.2.3 Un seul modèle : la loi de Tweedie

On peut aussi modéliser **directement** le coût par unité d'exposition. La loi de **Tweedie** de paramètre $p\in(1{,}2)$ est celle d'un **Poisson composé de montants Gamma** : une masse en zéro (pas de sinistre), puis une partie continue positive. Sa variance est $\mathrm{Var}(Y)=\phi\,\mu^{p}$, et pour une fréquence de Poisson avec des montants Gamma de forme $k$, on montre que $p=(k+2)/(k+1)$ : plus les montants sont dispersés (forme petite), plus $p$ est proche de 2. C'est l'objet de la section 2.6 du volume II. Sur nos données écrêtées, le coefficient de variation des montants correspond à $p\approx1{,}87$.

```python
cout = cout_par_police(tr, st[["id_police"]].assign(montant=st["rev_cap"].values))      # coût écrêté par police
cout["pp"] = cout["cout"] / cout["exposition"]
tw = smf.glm(formule.replace("nb_sinistres", "pp"), cout, family=sm.families.Tweedie(var_power=1.5, link=sm.families.links.Log()),
             freq_weights=cout["exposition"]).fit()
```


Les deux approches sont des **modèles différents du même objet** : l'une décompose (deux GLM, deux jeux de relativités, lisibles), l'autre est directe (un seul jeu de relativités, moins de paramètres). Sur 2024, leurs primes pures sont corrélées à 0,871 et leurs pouvoirs de classement sont équivalents (indices de Gini de la section 2.2.5). On préfère en pratique la **décomposition**, parce qu'elle permet de comprendre, d'expliquer à un régulateur ou à un courtier, et de corriger séparément la tendance de fréquence et celle de sévérité (section 2.2.7).

> 🧪 **Choisir $p$.** Le choix de $p$ se fait par vraisemblance profilée ou par validation. Un test de sensibilité sur $p\in\{1{,}3\,;1{,}5\,;1{,}7\}$ montre que le classement des contrats varie très peu : c'est la **forme** de la moyenne (les relativités) qui compte, pas la forme exacte de la variance.

### 2.2.4 Du tarif pur au tarif commercial

La prime pure ne paie que les sinistres. Le prix demandé doit aussi couvrir des **frais fixes par contrat** $F$ (gestion, souscription), des **frais proportionnels au prix** (commissions de distribution, taxes, fraction $\tau$ de la prime) et une **marge** pour risque et profit ($m$, aussi proportionnelle). Le prix commercial $P$ vérifie
$$P=\pi+F+\tau P+mP\quad\Longrightarrow\quad P=\frac{\pi+F}{1-\tau-m}.$$
Avec une prime pure moyenne $\pi=591$ €, des frais fixes de 45 €, 12 % de commissions et taxes et 4 % de marge, le prix moyen est $P=(591+45)/(1-0{,}16)\approx758$ €. Le **ratio sinistres sur primes** attendu est alors $\pi/P\approx78$ % ; le reste paie les frais et la marge. Un tarif dont ce ratio dérive à la hausse, d'année en année, est un tarif en difficulté, même si le résultat reste positif.


Voici trois profils, du plus risqué au moins risqué, tarifés avec les deux modèles :

```text
                  profil  fréquence  sévérité (€)  prime pure (€)  prix (€)
jeune, zone F, puissante      0.184        5894.0          1319.0      1625
45 ans, zone C, standard      0.051        5393.0           508.0       660
 72 ans, zone A, hybride      0.046        4901.0           460.0       600
```

Le prix du jeune conducteur est de 1 624 €, celui du conducteur de 72 ans en zone A de 601 € : un rapport de 2,7. Ce rapport est **la somme de plusieurs relativités multipliées** : il est l'objet de toutes les discussions commerciales.


**La structure du tarif.** Un tarif commercial n'est pas la sortie brute du modèle : on **arrondit** (au pas de 5 €), on **lisse** les relativités pour qu'elles soient monotones et lisibles, on **plafonne** certaines (un jeune conducteur ne paiera pas officiellement 1,9 fois un conducteur de référence si le marché ne le supporte pas) et l'on **rééquilibre** pour conserver la prime moyenne. Chaque contrainte a un coût, souvent ailleurs que là où on le cherche. Par exemple, plafonner à 1,5 la relativité des 18-24 ans (estimée à 1,92) laisse le pouvoir de classement presque intact (le Gini de tarification passe de 0,178 à 0,177), mais oblige à relever tous les autres prix de 2,0 % pour garder le même chiffre d'affaires. Cette classe ne représente que 8 % de l'exposition : les autres conducteurs **subventionnent** les jeunes. C'est un choix commercial légitime, mais c'est un **choix**, dont le prix est mesurable, et qui expose à l'antisélection (section 2.2.6) : un concurrent qui ne plafonne pas attirera les conducteurs de 45 ans surfacturés.

### 2.2.5 Valider un tarif hors période

Un tarif se juge sur des contrats et une année **qu'il n'a pas vus**. On a estimé sur 2022-2023 ; on regarde 2024. Deux outils, reliés à ce que le volume III a présenté pour la discrimination et la calibration (volume III, sections 5.1 et 5.2).

**La courbe de Lorenz ordonnée et l'indice de Gini de tarification.** On classe les contrats du moins cher au plus cher selon le tarif, puis l'on trace la part cumulée du **coût réellement observé** en fonction de la part cumulée de l'exposition. Un tarif sans pouvoir de classement donne la diagonale (les 50 % les moins chers coûtent 50 % du total) ; un bon tarif donne une courbe en dessous de la diagonale (les 50 % les moins chers ne coûtent que 35 % du total). L'indice de Gini est le double de l'aire entre la diagonale et la courbe : 0 pour un tarif aveugle, de plus en plus grand quand le tarif classe mieux.


![À gauche : courbes de Lorenz ordonnées de quatre tarifs sur 2024 (plus la courbe est basse, mieux le tarif classe les contrats). À droite : coût écrêté prédit et observé par dixième d'exposition, pour le tarif complet.](figures/ch02-lorenz.png)

Les indices de Gini de 2024 sont de 0,02 pour le tarif plat, 0,10 pour le tarif sous-segmenté (sans âge ni zone), 0,18 pour le tarif complet et 0,17 pour le Tweedie. Mais **un Gini est une statistique bruitée**, et c'est le point que l'on oublie le plus souvent : un tarif **aléatoire** a un Gini de zéro *en moyenne*, avec un écart-type de 0,036 d'un tirage à l'autre sur ces 37 000 contrats. La différence entre le tarif complet et le tarif plat est de 0,19, avec un intervalle de confiance à 95 % de 0,08 à 0,28 (rééchantillonnage des contrats) : elle est **réelle**. Entre le tarif complet et le Tweedie, en revanche, la différence est inférieure au bruit : on ne peut pas les départager sur une seule année.

**La lecture par dixièmes.** Le graphique de droite compare, pour chaque dixième de l'exposition, le coût écrêté prédit et le coût observé. Le dixième le moins cher est prédit à 208 € par année d'exposition pour 247 € observés ; le plus cher à 675 € contre 653 €. Le **classement** est bon (le coût observé croît à peu près avec le coût prédit). Le **niveau** global est bien calibré sur la partie écrêtée : 343 € observés par année d'exposition contre 357 € prédits, soit 4 % d'écart, dans le bruit d'une année. L'écart se trouve ailleurs : les sinistres de plus de 100 000 € n'ont coûté que 85 € par année d'exposition en 2024, pour une charge prévue de 234 €. C'est la même année clémente que celle de la section 2.1.6.

> ⚠️ **Une année ne valide pas un tarif.** Avec une seule année de test, la fréquence a une erreur-type d'environ 2 %, et la sévérité de 10 % à 20 % à cause de la queue. Les actuaires valident donc sur plusieurs années glissantes, regardent le **classement** (Gini, dixièmes) plus que le **niveau** (que l'on recale chaque année par un facteur d'ajustement global), et conservent l'historique des écarts entre prévu et observé.

### 2.2.6 Antisélection : ce que coûte un tarif trop grossier

Pourquoi chercher un tarif plus fin, si le tarif plat « équilibre » en moyenne ? Parce que **le marché est un concurrent** : si un assureur propose un tarif plus fin, il fait payer moins cher les bons risques, qui partent chez lui, et laisse au premier assureur les mauvais risques, avec une prime moyenne devenue insuffisante. C'est l'**antisélection** (le vocabulaire est celui de Akerlof) : la sélection que l'on subit, parce qu'on ne la fait pas.

Simulons-la sur 2024. Un concurrent applique le **tarif complet** ; notre mutuelle applique soit un tarif plat, soit le tarif sous-segmenté. **Un assuré reste chez nous si notre prix est inférieur ou égal à celui du concurrent**, et part sinon (c'est une règle extrême : il n'y a ni inertie ni fidélité). Nous mettons la charge des gros sinistres à son niveau prévu pour ne mesurer que l'effet de la segmentation.


```text
                           tarif  part conservée  sinistres/primes avant  sinistres/primes après
                      tarif plat           0.375                   0.975                   1.145
sous-segmenté (sans âge ni zone)           0.398                   0.980                   1.164
```

Avec le tarif plat, la mutuelle ne conserve que 38 % de son exposition (les contrats les plus risqués, pour lesquels le concurrent est plus cher que nous) et son ratio sinistres sur primes passe de 97 % à 114 % : **elle perd de l'argent sur l'ensemble des contrats conservés**. Le tarif sous-segmenté ne fait pas mieux : 40 % de l'exposition conservée et un ratio de 116 %. Le mécanisme est un cercle vicieux : il faudrait augmenter les prix, ce qui chasse encore des bons risques, jusqu'à ne garder que les mauvais.

> ⚠️ **Les limites de la simulation.** Le concurrent applique ici un tarif estimé *sur les mêmes données* (il connaît donc les mêmes relativités : c'est le cas le plus défavorable) ; les assurés ne comparent pas tous les prix ; l'inertie et les frais de changement protègent en pratique une grande partie du portefeuille. L'ordre de grandeur est néanmoins celui que l'on rencontre sur les marchés très concurrentiels (comparateurs en ligne). La leçon reste : **un tarif plus grossier que celui du marché n'est pas neutre.**

### 2.2.7 Inflation, équité et limites

**La tendance.** On tarife pour l'année *à venir*, avec des données du passé : il faut donc **projeter** la fréquence et la sévérité. L'inflation des coûts, estimée plus haut à 4,4 % par an (programmée : 4 %), signifie qu'un tarif construit sur 2022-2023 sous-estime 2025 d'environ 2 ans de tendance, soit près de 9 % si on ne la corrige pas. D'où la revalorisation systématique des montants et l'ajustement du tarif par un **facteur de tendance** ; pour la fréquence, la tendance se lit aussi sur le temps (ici, stable autour de 6,6 %).


**L'équité.** Une variable de tarification est **justifiée** quand elle explique le risque, mais elle peut aussi *remplacer* une caractéristique que la loi interdit d'utiliser ou que la société juge inacceptable (dans plusieurs pays, des variables comme le sexe ou certaines origines ne peuvent pas servir au tarif). La **zone** peut ainsi cacher un facteur socio-économique ; l'**âge** est parfois limité par la loi. Deux principes à connaître. D'abord, **retirer la variable ne retire pas la discrimination** si d'autres variables corrélées la reconstituent. Ensuite, la différence de prix doit être **fondée sur une différence de risque démontrable et proportionnée**. Le volume III (section 5.4) donne les outils de mesure ; la décision, elle, relève de la mutuelle, de son régulateur et de la loi. Les règles varient d'un pays à l'autre : ce chapitre ne dit pas ce qui est permis, il dit ce qu'il faut vérifier.

**Les limites de ce que nous avons fait.** Trois années de données simulées ; un portefeuille unique ; pas de **résiliations** (un tarif modifie le portefeuille qui le paie) ; pas de **réassurance** (chapitre 6) ; pas de **marge de sécurité** pour l'incertitude de paramètres ; une segmentation par GLM, que la section 2.4 compare à un boosting. Un vrai tarif est un exercice de plusieurs mois ; celui-ci en est la charpente.

> ✅ **À retenir.**
> - La **prime pure** est $E[N\mid x]\times E[X\mid x]$ ; le prix commercial est $(\pi+F)/(1-\tau-m)$.
> - On modélise **fréquence** (Poisson, exposition en décalage) et **sévérité** (Gamma sur les montants écrêtés, charge pour gros sinistres) séparément, ou le coût directement (**Tweedie**) ; on préfère la décomposition, plus lisible.
> - Un tarif se **valide hors période** par la courbe de Lorenz ordonnée, le Gini de tarification et la lecture par dixièmes ; **un Gini seul n'a pas de sens sans son intervalle**.
> - Un tarif trop grossier subit l'**antisélection** : le concurrent mieux segmenté lui laisse les mauvais risques.
> - Plafonnements, arrondis et rééquilibrages ont un **coût mesurable** ; les variables sensibles et leurs substituts demandent une réflexion d'équité.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.4 et 2.5 et exercices 2.4 à 2.6 (GLM de fréquence et de sévérité, prime pure, chargements, validation par Gini et antisélection).


## 2.3 Provisionnement des sinistres

La tarification fixe le prix d'un risque *avant* qu'il ne se réalise. Le provisionnement s'occupe de ce qui s'est **déjà** réalisé mais n'est pas encore entièrement payé : un accident de décembre, déclaré en janvier, réglé en trois ans après expertises et recours. À la clôture de chaque exercice, la mutuelle doit inscrire à son passif une estimation de ces paiements futurs, la **provision pour sinistres à payer**. C'est souvent le plus gros poste de son bilan, et celui dont l'incertitude est la plus grande.

### 2.3.1 Pourquoi provisionner, et que provisionne-t-on ?

Un sinistre passe par plusieurs états : il survient, il est **déclaré** (parfois des mois plus tard), il est évalué par un gestionnaire (une **provision dossier par dossier**), puis payé en une ou plusieurs fois, parfois après réouverture. À une date donnée, les sinistres survenus se répartissent en trois groupes :

- les sinistres **déclarés et en cours** (on connaît leur existence, pas leur coût final) ;
- les sinistres **survenus mais non encore déclarés** (en anglais *incurred but not reported*, **IBNR**) ;
- les sinistres **déclarés dont le coût définitif dépassera ou sera inférieur à l'estimation du dossier** (le « IBNER »).

La provision couvre les trois. Elle n'est pas un fait comptable que l'on constaterait : c'est une **estimation**. Sous-provisionner donne des résultats flatteurs aujourd'hui qui se paient demain (et fait parfois disparaître des assureurs) ; sur-provisionner immobilise du capital et fausse les prix. D'où l'importance de la mesurer **avec son incertitude** (section 2.5) et de la juger **a posteriori** : le jour où les sinistres sont réglés, on sait si la provision était suffisante (le « boni » ou le « mali »).

### 2.3.2 Le triangle de développement

On regroupe les sinistres par **année de survenance** (l'année de l'accident) et l'on suit leurs paiements cumulés année après année : le **délai de développement** $j$ vaut 0 l'année de survenance, 1 l'année suivante, etc. Les données forment un **triangle** : à la fin de 2024, les sinistres de 2015 ont dix années de recul (délais 0 à 9), ceux de 2024 une seule (délai 0). La partie du carré située sous la diagonale est **le futur** : c'est elle qu'il faut estimer.

On note $C_{i,j}$ le **paiement cumulé** de l'année de survenance $i$ au délai $j$. Voici notre triangle de responsabilité civile (garantie à développement lent), en millions d'euros :


```text
        0     1     2     3     4     5     6     7     8     9
2015  5.6  14.2  22.6  29.6  35.7  40.3  43.7  45.3  46.9  47.7
2016  6.5  15.7  25.7  34.0  41.4  46.6  50.4  52.7  54.7      
2017  6.9  17.5  28.3  36.2  43.3  48.4  53.2  55.7            
2018  5.6  15.6  26.0  33.7  40.6  46.2  50.1                  
2019  7.0  18.2  29.1  37.7  45.1  51.2                        
2020  9.2  22.3  35.2  45.8  55.6                              
2021  8.1  19.9  32.7  43.2                                    
2022  8.1  20.3  32.2                                          
2023  9.7  24.2                                                
2024  9.1                                                      
```

Chaque ligne se lit de gauche à droite : l'année 2015 a été payée à hauteur de 5,6 M€ la première année, puis 14,2 M€ en cumul au bout de deux ans, et ainsi de suite jusqu'à 47,7 M€. Le **triangle supérieur** est connu ; le **triangle inférieur** est vide, et c'est lui qui constitue la provision à constituer.


> ⚠️ **Lire les diagonales.** Une diagonale du triangle est une **année calendaire** : la diagonale la plus basse contient les paiements de 2024, toutes années de survenance confondues. Un événement qui touche tous les paiements d'une année (une revalorisation des indemnités, une accélération du règlement) se voit sur **une diagonale**, pas sur une ligne ni sur une colonne. Ce point sera crucial en section 2.5.

### 2.3.3 La méthode chain ladder

La méthode la plus répandue est la **chaîne d'échelle** (*chain ladder*). Son idée tient en une phrase : **les années passées montrent comment les paiements s'accumulent d'un délai au suivant, et les années récentes suivront le même schéma.**

On mesure, pour chaque délai $j$, le **facteur de développement** : le rapport entre la somme des cumuls au délai $j+1$ et la somme des cumuls au délai $j$, calculé sur les années où les deux sont connus :
$$\hat f_j=\frac{\sum_{i}C_{i,j+1}}{\sum_{i}C_{i,j}}.$$
Puis l'on **prolonge** chaque ligne en multipliant son dernier cumul connu par les facteurs restants : $\hat C_{i,J}=C_{i,\,I-i}\prod_{j=I-i}^{J-1}\hat f_j$. La provision de l'année $i$ est l'**ultime estimé** moins le cumul déjà payé.

> 📐 **Pourquoi cette moyenne ?** Mack (1993) formule le chain ladder par trois hypothèses : (1) les années de survenance sont indépendantes ; (2) $E[C_{i,j+1}\mid C_{i,0},\dots,C_{i,j}]=f_j\,C_{i,j}$ ; (3) $\mathrm{Var}(C_{i,j+1}\mid\cdot)=\sigma_j^2\,C_{i,j}$. Sous ces hypothèses, l'estimateur $\hat f_j$ ci-dessus est la solution des **moindres carrés pondérés** : il minimise $\sum_i C_{i,j}\bigl(C_{i,j+1}/C_{i,j}-f\bigr)^2$. En dérivant, $\sum_i C_{i,j}\bigl(C_{i,j+1}/C_{i,j}-f\bigr)=\sum_i C_{i,j+1}-f\sum_iC_{i,j}=0$, d'où $f=\sum_iC_{i,j+1}/\sum_iC_{i,j}$. La moyenne est **pondérée par le volume** : les grandes années comptent plus que les petites.

**Un exemple à la main.** Un triangle de quatre années, en milliers d'euros.

| Année | Délai 0 | Délai 1 | Délai 2 | Délai 3 |
|---|---|---|---|---|
| 1 | 100 | 150 | 165 | 170 |
| 2 | 110 | 168 | 185 | |
| 3 | 120 | 185 | | |
| 4 | 130 | | | |

Facteurs : $\hat f_0=(150+168+185)/(100+110+120)=503/330=1{,}524$ ; $\hat f_1=(165+185)/(150+168)=350/318=1{,}101$ ; $\hat f_2=170/165=1{,}030$. L'année 4, payée à 130 au délai 0, est prolongée en $130\times1{,}524\times1{,}101\times1{,}030=224{,}7$ ; sa provision est donc de $224{,}7-130=94{,}7$. L'année 3 est prolongée de 185 à $209{,}8$ (provision 24,8), l'année 2 de 185 à $190{,}6$ (provision 5,6). La provision totale est de 125,1 milliers d'euros, dont les trois quarts viennent de la dernière année : **les années récentes, peu développées, portent presque toute l'incertitude**.


Appliquons-le au triangle de responsabilité civile. Un appel suffit :

```python
f = facteurs_chain_ladder(C_rc)             # facteurs de développement f_0, ..., f_8
Cp, ult = projeter(C_rc, f)                 # triangle complété, ultime de chaque année
```


Les facteurs vont de $\hat f_0=2{,}52$ (entre le premier et le second délai, les paiements sont multipliés par 2,52) à $\hat f_8=1{,}017$ (entre le neuvième et le dixième, ils croissent de moins de 2 %). Leur produit, 8,6, dit qu'une année de survenance n'est payée qu'à environ 12 % de son ultime à la fin de sa première année. L'ultime estimé de la dernière année est donc 8,6 fois son paiement initial. La provision totale estimée est de **230,2 M€**, dont 56 % pour les deux dernières années de survenance : sur un total payé à ce jour de 423,7 M€, la provision en représente 54 %.


### 2.3.4 La queue de développement

Notre triangle s'arrête au délai 9, mais les sinistres de responsabilité civile se règlent bien après dix ans : un petit pourcentage reste à payer pour **chaque** année, même la plus ancienne. Le chain ladder « tel quel » donne une provision **nulle** pour l'année 2015, ce qui est faux : le triangle ne contient simplement pas l'information sur ce qui se passe après le délai 9. On ajoute un **facteur de queue** $f_{\text{queue}}$ qui multiplie tous les ultimes. Il ne peut pas se lire dans les données ; il faut le **choisir**.

Trois façons de le faire. (1) **Ne rien ajouter** ($f_{\text{queue}}=1$), valable seulement pour une garantie à développement court. (2) **Extrapoler** la décroissance des facteurs : on observe que $\hat f_j-1$ décroît à peu près géométriquement avec $j$, on ajuste $\ln(\hat f_j-1)=a+bj$ sur les derniers délais et l'on prolonge. (3) **Importer** une valeur d'une source externe (un triangle plus long, un benchmark de marché, une étude sectorielle).


L'extrapolation (2) donne ici un facteur de queue de 1,029, c'est-à-dire un taux de décroissance des $\hat f_j-1$ de 0,61 d'un délai à l'autre. Avec ce facteur, la provision passe de 230,2 M€ (sans queue) à 249,3 M€. **La différence, 19,2 M€, est plusieurs fois supérieure à l'erreur d'estimation statistique du triangle** (environ 5,4 M€, section 2.5). Une variation de un point de pourcentage sur le facteur de queue déplace la provision de 6,5 M€ : c'est typiquement l'endroit où se loge le jugement de l'actuaire, et où un « prudent » et un « optimiste » diffèrent le plus.


### 2.3.5 Juger les provisions a posteriori

Comme le triangle est simulé, nous disposons de ce que la réalité refuse : **les paiements futurs réels** (le carré complet). On peut donc faire ce que fait chaque assureur, avec dix ans de retard : comparer la provision constituée à ce qui a été payé.


```text
        payé  provision CL  provision CL + queue  réel à payer
2015    47.7           0.0                   1.4           0.7
2016    54.7           0.9                   2.5           2.1
2017    55.7           3.1                   4.8           4.3
2018    50.1           5.0                   6.6           6.1
2019    51.2          10.0                  11.8          11.8
2020    55.6          19.5                  21.7          22.3
2021    43.2          27.2                  29.3          26.2
2022    32.2          36.2                  38.2          36.2
2023    24.2          58.6                  61.0          60.3
2024     9.1          69.6                  71.9          72.1
total  423.7         230.1                 249.2         242.1
```

![À gauche : part de l'ultime déjà payée selon le délai, estimée par chain ladder et programmée. À droite : provision par année de survenance, avec ou sans facteur de queue, comparée aux paiements réellement effectués ensuite.](figures/ch02-provision.png)

Trois constats. **Le chain ladder sans queue sous-estime la provision de 5 %** (230,2 M€ pour 242,1 M€ réellement payés). **Avec la queue extrapolée, il la surestime** de 3 % (249,3 M€), parce que la décroissance estimée sur quelques délais bruités est plus lente que la décroissance réelle. **Avec le bon facteur de queue** (celui que l'on ne peut connaître qu'ici : 1,017), on obtiendrait 241,3 M€, à 0,3 % de la réalité. La leçon est nette : **sur ce triangle, le chain ladder estime très bien la dynamique des délais observés ; ce qui fait la différence est ce qu'il ne voit pas.**


**Une garantie à développement court.** Le triangle de dommages aux biens (sinistres réglés presque entièrement en trois ans) se comporte tout autrement. Le chain ladder sans queue donne 31,9 M€ pour 32,3 M€ réellement payés : un écart de −1,2 %. Quand la queue est négligeable, **la méthode fonctionne remarquablement bien**, et le problème de la queue disparaît. C'est pourquoi les actuaires séparent leurs triangles par **garantie** et ne mélangent jamais des développements lents et rapides.

> ⚠️ **Ce que le chain ladder suppose.** Un schéma de développement **stable** dans le temps, indépendant du niveau de l'année de survenance ; pas de changement de gestion des dossiers, pas de revalorisation soudaine des indemnités, pas de changement de mix de garanties. Chacune de ces hypothèses se casse dans la vraie vie, et chaque cassure donne un biais qui s'applique à *toute* la provision. La section 2.5 donne les outils pour diagnostiquer ces ruptures, estimer l'incertitude, et compléter la méthode par une information a priori.

> ✅ **À retenir.**
> - Une provision est une **estimation de paiements futurs** pour des sinistres déjà survenus ; elle se mesure avec son incertitude et se juge a posteriori.
> - Le **triangle** range les paiements par année de survenance et délai ; les **diagonales** sont des années calendaires.
> - Le **chain ladder** multiplie le dernier cumul de chaque année par les **facteurs de développement** moyens (pondérés par le volume) ; les années récentes portent l'essentiel de l'incertitude.
> - La **queue** n'est pas dans le triangle : elle se choisit, et c'est souvent la plus grosse source d'écart.
> - Pour une garantie à développement court, le chain ladder fonctionne très bien ; pour une garantie longue, tout est dans la queue.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.6 et exercices 2.7 à 2.8 (chain ladder à la main, queue de développement, comparaison à la réalité).


## 2.4 ➕ Pour aller plus loin : GLM tarifaires et théorie de la crédibilité

> 🧭 **Section optionnelle.** Elle ouvre le capot du GLM de la section 2.2 (déviance, tests, formes des variables continues, régularisation), présente la **théorie de la crédibilité**, l'outil historique de l'actuaire pour doser *données propres* et *information a priori*, puis compare le GLM à un boosting. Elle suppose acquis le volume II, chapitre 2 (GLM) et le volume III, chapitre 2 (boosting).

### 2.4.1 Sous le capot du GLM : déviance et tests

Un GLM de comptage décrit $E[N_i]=\mu_i=e_i\exp(x_i^\top\beta)$. On l'ajuste en maximisant la vraisemblance, et l'on compare des modèles par la **déviance**, qui mesure l'écart à un modèle parfait (un paramètre par observation) :
$$D=2\sum_i\Bigl[N_i\ln\frac{N_i}{\hat\mu_i}-(N_i-\hat\mu_i)\Bigr]\qquad(\text{avec } 0\ln0=0).$$
C'est deux fois la différence des log-vraisemblances, et c'est **l'équivalent, pour un modèle de Poisson, de la somme des carrés des résidus**. Pour trois contrats avec $N=(0{,}1{,}0)$ et $\hat\mu=(0{,}10\,;0{,}20\,;0{,}05)$ : $D=2\bigl[0{,}10+(\ln5-0{,}8)+0{,}05\bigr]=1{,}919$.

> 📐 **Test du rapport de vraisemblance.** Si le modèle $M_0$ (à $p_0$ paramètres) est contenu dans le modèle $M_1$ (à $p_1>p_0$), alors, sous $M_0$, $D_0-D_1\sim\chi^2_{p_1-p_0}$ approximativement : ajouter des variables diminue toujours la déviance, et le test dit si la baisse dépasse ce que le hasard donnerait. On l'utilise pour décider si une variable (ou un bloc de modalités) mérite sa place.

Construisons le modèle pas à pas sur 2022-2023 :


```text
                                             paramètres déviance      AIC baisse de déviance p-valeur
modèle                                                                                               
taux global                                           1  20633.5  27555.0                            
+ zone                                                6  20554.8  27486.2               78.7  1.5e-15
+ âge (7 classes)                                    12  20347.2  27290.6              207.6  4.5e-42
+ bonus-malus                                        13  20319.4  27264.8               27.8  1.4e-07
+ puissance, usage, carburant, âge véhicule          18  20256.2  27211.6               63.2  2.6e-12
```

Chaque étape fait baisser la déviance (de 20 634 à 20 256), et l'on mesure la contribution : la zone retire 79 (pour 5 paramètres), l'âge 208 (6 paramètres), le bonus-malus 28 (1 paramètre), le reste 63. Toutes ces baisses sont très supérieures à ce que donnerait le hasard (un $\chi^2$ à 5 degrés de liberté dépasse rarement 11). **La déviance est une somme sur 70 000 contrats et ne se lit qu'en comparaison** : sa valeur absolue ne dit rien.

> ⚠️ **Les résidus d'un modèle de comptage sont illisibles contrat par contrat.** Avec une moyenne de 0,06 sinistre par contrat, un résidu de déviance ne prend que deux ou trois valeurs distinctes. On vérifie donc l'adéquation en **regroupant** les contrats (par dixièmes du tarif, par classe d'âge, par zone) et en comparant sinistres observés et prédits dans chaque groupe, comme pour la courbe de calibration du volume III (section 5.2).

### 2.4.2 Variables continues : classes, splines, interactions

L'âge du conducteur est continu, mais son effet ne l'est pas : le risque est élevé avant 25 ans, puis presque plat. Trois façons de le coder : une **variable linéaire** (un seul coefficient : $\ln\mu$ varie à pente constante), des **classes** (une relativité par tranche, comme dans notre tarif) ou une **spline** (une courbe lisse à quelques degrés de liberté). Elles se départagent sur l'année suivante, avec la déviance **hors période** (2024) :


```text
                                   paramètres  AIC (2022-2023)  déviance 2024
âge linéaire                               13          27312.4        12110.9
âge en 7 classes                           18          27211.6        12054.3
âge par spline (5 d.l.)                    17          27232.0        12067.7
classes + interaction âge × usage          24          27218.5        12053.9
```

La variable **linéaire** est nettement moins bonne (12 111 de déviance en 2024 contre 12 054 pour les sept classes) : le modèle impose une pente continue là où l'effet est un **saut** chez les jeunes conducteurs. La **spline** fait mieux que le linéaire mais pas aussi bien que les classes (12 068) : ici la vérité programmée est un palier (moins de 25 ans, plus de 70 ans), que des classes épousent mieux qu'une courbe lisse. Sur des données réelles, avec un effet plus progressif, la conclusion pourrait s'inverser ; on teste. Enfin l'**interaction** âge × usage n'apporte rien (baisse de déviance de 5,1 pour 6 paramètres, $p=0{,}53$) : **le test dit de ne pas la garder**, et la vérité programmée n'en contient pas. Un modèle sans interaction est un tarif plus lisible, plus stable et plus facile à justifier.

### 2.4.3 Régularisation : quand les cellules sont trop nombreuses

Imaginons maintenant un tarif plus fin : une relativité par **combinaison** zone × puissance × classe d'âge, soit plus de 300 cellules. Plusieurs sont presque vides, et l'estimateur du maximum de vraisemblance y dit n'importe quoi (une cellule à 8 années d'exposition et un sinistre « a » une fréquence de 12 %). La **régularisation** (volume II, section 1.5) pénalise les coefficients grands. Pour un modèle de Poisson, avec une pénalité de type ridge de force $\alpha$, on minimise $D(\beta)/(2n)+\tfrac{\alpha}{2}\lVert\beta\rVert_2^2$.


```python
from sklearn.linear_model import PoissonRegressor
reg = PoissonRegressor(alpha=1e-4, max_iter=500)              # alpha = force de la pénalité (ridge)
reg.fit(X_cell_tr, y_tr, sample_weight=e_tr)                  # fréquence par unité d'exposition, pondérée par l'exposition
```

```text
          déviance 2024
alpha                  
0.000001        12265.1
0.000010        12234.6
0.000100        12130.9
0.001000        12057.7
0.010000        12076.8
```

Sur les 378 cellules, la déviance de 2024 est mauvaise quand la pénalité est trop faible (12 265 pour $\alpha=10^{-6}$ : le modèle apprend le bruit des cellules vides), s'améliore jusqu'à un optimum (12 058 pour $\alpha=1{,}0\times10^{-3}$), puis se dégrade quand la pénalité écrase les relativités (12 077 pour $\alpha=10^{-2}$, le tarif plat valant 12 226). Le réglage de $\alpha$ se fait, comme tout hyperparamètre, **hors période** ou par validation croisée par blocs d'années (volume III, section 1.5). Même à son optimum, le modèle à cellules ne fait pas mieux que le GLM sans cellules (12 054) : la finesse du tarif ne paie que si elle est domptée, et ne paie pas toujours.

### 2.4.4 La théorie de la crédibilité

La crédibilité répond à une question que l'on se pose chaque fois qu'un segment est petit : **dans quelle mesure faut-il croire l'expérience propre d'un groupe, par rapport à la moyenne du portefeuille ?** Si la zone F n'a que 40 années d'exposition et 6 sinistres (15 %), la moyenne de 6,6 % du portefeuille est plus fiable que le 15 % observé. À l'inverse, un segment de 10 000 années d'exposition doit être cru.

L'estimateur de crédibilité est une moyenne pondérée :
$$\hat\lambda_g=Z_g\,\bar x_g+(1-Z_g)\,\mu,\qquad Z_g=\frac{w_g}{w_g+k},$$
où $\bar x_g$ est la fréquence observée du groupe $g$, $\mu$ la moyenne générale, $w_g$ l'exposition du groupe et $k$ une constante, **le point de crédibilité à 50 %** : un groupe d'exposition $k$ a $Z=1/2$. Le coefficient $Z_g$ croît de 0 à 1 avec le volume.

**Un exemple à la main.** Avec $\mu=6{,}6$ %, $k=500$ années d'exposition : un groupe de 1 000 années à 5,0 % reçoit $Z=1\,000/1\,500=0{,}667$, d'où $0{,}667\times5{,}0+0{,}333\times6{,}6=5{,}5$ % ; un groupe de 50 années à 12 % reçoit $Z=50/550=0{,}091$, d'où $0{,}091\times12+0{,}909\times6{,}6=7{,}1$ %. Le premier est quasiment cru (on lui retire un tiers de son écart à la moyenne), le second est ramené presque entièrement vers la moyenne.

> 📐 **Pourquoi cette forme, et d'où vient $k$ ?** Le modèle de **Bühlmann–Straub** suppose que chaque groupe a un taux « vrai » $\Lambda_g$ tiré d'une loi de moyenne $\mu$ et de variance $a$ (l'**hétérogénéité entre groupes**), et que, sachant $\Lambda_g$, la fréquence observée sur une exposition $w$ a pour variance $s^2/w$ (la **variance de processus**). Parmi tous les estimateurs linéaires de $\Lambda_g$, le meilleur au sens des moindres carrés est la moyenne pondérée ci-dessus, avec $k=s^2/a$. On estime $s^2$ par la variance intra-groupes (entre années, pour un même groupe) et $a$ par la variance entre groupes corrigée du bruit de processus. **Le point de crédibilité est le rapport bruit sur signal.**
>
> Dans le cas de la fréquence, avec la loi Poisson–Gamma de la section 2.1.3 (taux $\lambda\Theta$, $\Theta$ de moyenne 1 et de variance $\alpha$), la crédibilité est **exacte** : la moyenne a posteriori de $\lambda\Theta$ sachant $N$ sinistres sur une exposition $e$ est $\lambda\,(r+N)/(r+\lambda e)$ avec $r=1/\alpha$, soit $Z\,(N/e)+(1-Z)\lambda$ avec $Z=e/(e+k)$ et $k=1/(\alpha\lambda)$. Pour un contrat individuel, $k=1/(0{,}4\times0{,}066)\approx38$ années d'exposition.

Appliquons-le à un vrai problème : des **cellules tarifaires** zone × puissance × usage ($6\times9\times2=108$ cellules, de très inégale taille). On estime la fréquence de chaque cellule sur 2022 et 2023, on applique la crédibilité de Bühlmann–Straub (années comme périodes d'un même groupe), puis on juge ces estimations sur **2024**, contre l'expérience brute et contre la moyenne générale.


![Fréquence annuelle de chacune des cellules tarifaires, brute (gris) et après crédibilité (bleu), selon leur exposition ; la ligne orange est la moyenne du portefeuille. Les petites cellules, très dispersées, sont ramenées vers la moyenne.](figures/ch02-credibilite.png)

L'estimation donne une moyenne de 6,6 %, un point de crédibilité de $k\approx503$ années d'exposition (beaucoup plus que les 38 d'un contrat individuel, parce que les cellules rassemblent des centaines de contrats dont l'hétérogénéité *résiduelle* est faible) et une crédibilité médiane de 33 % pour une cellule médiane de 242 années d'exposition. Sur 2024, la déviance des fréquences de cellules est de 277 pour l'expérience brute, 195 pour la moyenne générale et **141 pour l'estimateur de crédibilité** : il bat les deux, parce qu'il est brut là où les données sont abondantes et conservateur ailleurs.

> 🧪 **Crédibilité et GLM.** Les deux répondent au même besoin avec des outils différents. Le **GLM** partage l'information entre cellules *par la structure* (une relativité de zone et une relativité de puissance valent pour toutes les cellules : un modèle additif sur l'échelle logarithmique) ; la **crédibilité** la partage *par la moyenne* (une cellule est tirée vers le groupe). Dans la pratique, on les combine : le GLM donne la moyenne a priori de chaque cellule, et la crédibilité dose l'écart de l'expérience de la cellule à ce a priori. La théorie des modèles à effets aléatoires (volume II, section 1.7) en est la forme moderne.

### 2.4.5 GLM ou boosting ?

Le volume III a montré la supériorité fréquente du **gradient boosting** sur les tableaux de données. Pour la tarification, la question est : à quoi bon un GLM, plus rigide ? Comparons sur la fréquence, avec une objective de Poisson, 200 arbres peu profonds (huit feuilles), validés hors période :


```text
                                    déviance 2024
tarif plat                                12226.3
GLM (âge en classes)                      12054.3
boosting, 200 arbres                      12072.3
boosting, contraintes de monotonie        12072.7
boosting, 600 arbres                      12109.9
```

Le GLM obtient 12 054 ; le boosting 12 072 avec 200 arbres, 12 073 avec des contraintes de monotonie sur la puissance et le bonus-malus, et 12 110 avec 600 arbres (il dérive : plus d'arbres, c'est plus de surapprentissage). **Le boosting ne fait pas mieux que le GLM ici**, et ce n'est pas un hasard : la vérité programmée est **multiplicative et sans interaction**, exactement la forme d'un GLM. Le boosting n'a rien à découvrir que le GLM ne sache déjà, et il paie sa flexibilité en variance.

Sur des données réelles, où des interactions et des non-linéarités existent, le boosting l'emporte parfois ; les assureurs l'utilisent alors de trois manières. (1) **Comme référence** : si le boosting bat nettement le GLM, il y a une structure que le GLM manque, à chercher. (2) **Comme source de variables** : on repère les interactions importantes (par SHAP, volume III, section 5.3) et on les ajoute au GLM. (3) **En production**, avec contraintes de monotonie et explicabilité, quand le régulateur et le marché l'acceptent. Ce qui compte, ce n'est pas l'algorithme : c'est la **lisibilité** du tarif, la **stabilité** de ses relativités d'une année à l'autre, et la capacité à **justifier** chaque écart de prix.

> ✅ **À retenir.**
> - On compare des GLM par leur **déviance** et par un test du rapport de vraisemblance ; la valeur absolue de la déviance ne signifie rien.
> - La forme d'une variable continue (linéaire, classes, spline) se choisit **hors période** ; une interaction se garde seulement si elle améliore nettement la déviance.
> - La **régularisation** domestique les cellules trop fines ; son intensité se règle hors période.
> - La **crédibilité** $Z=w/(w+k)$ pèse expérience propre et moyenne ; $k$ est le rapport entre variance de processus et hétérogénéité entre groupes. Elle bat l'expérience brute et la moyenne générale sur des cellules inégales.
> - Un boosting ne bat pas un GLM quand la structure vraie est multiplicative et additive ; c'est avant tout un étalon, pas un remplaçant.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.7 et exercices 2.9 à 2.10 (déviance et test, crédibilité de Bühlmann–Straub, GLM contre boosting).


## 2.5 ➕ Pour aller plus loin : chain ladder, Bornhuetter–Ferguson, Mack et bootstrap

> 🧭 **Section optionnelle.** Elle prolonge la section 2.3 : on cherche maintenant non plus *une* provision, mais **une provision avec son incertitude**, on la complète par une information a priori, et l'on examine ce qui met le chain ladder en défaut. Elle suppose connue la section 2.3.

### 2.5.1 Les hypothèses à vérifier

Le chain ladder de Mack repose sur trois hypothèses (section 2.3.3), dont la deuxième, celle d'un **schéma de développement stable**, est la plus exposée : les facteurs $f_j$ doivent valoir la même chose pour toutes les années de survenance et toutes les années calendaires. Dans la réalité, trois événements la font casser :

- un **changement de gestion** (la mutuelle règle plus vite ses dossiers : tous les paiements d'une diagonale sont avancés) ;
- une **revalorisation soudaine** (une décision de justice ou une réforme augmente les indemnités de toutes les années non encore réglées) ;
- un **changement de portefeuille** (un nouveau canal de distribution, une nouvelle garantie : les années récentes ne ressemblent plus aux anciennes).

Les deux premiers touchent **une diagonale** (une année calendaire) ; le troisième touche **les dernières lignes**. Le diagnostic consiste donc à chercher, dans les résidus, une structure en diagonale ou en ligne. Nous le ferons en 2.5.5.

### 2.5.2 Cape Cod et Bornhuetter–Ferguson : ajouter une information a priori

Le chain ladder a un défaut : il **extrapole** le dernier cumul observé de chaque année. Pour la dernière année de survenance (payée à 9 M€ après un seul délai), la provision est $(\prod_j\hat f_j-1)\times9$ M€ : tout repose sur un unique chiffre, bruité, multiplié par 8,6. Si le premier paiement de l'année est exceptionnellement bas ou haut, la provision l'est aussi dans la même proportion.

La méthode de **Bornhuetter–Ferguson** (BF) remplace cette extrapolation par une **information a priori** : un ratio sinistres sur primes attendu $\rho_i$ (issu de la tarification, de l'expérience, du jugement), appliqué à la prime acquise $P_i$. L'ultime attendu est $P_i\rho_i$, et l'on n'en retient que la **part non encore payée** :
$$\widehat R_i^{\text{BF}}=P_i\,\rho_i\,\bigl(1-\hat p_i\bigr),\qquad \hat p_i=\frac{1}{\prod_{j\ge I-i}\hat f_j},$$
où $\hat p_i$ est la **part déjà payée attendue** au délai atteint par l'année $i$. L'estimation BF ne dépend du paiement observé que *via* le fait qu'il est déjà payé (il vient s'ajouter à la réserve). Le chain ladder, lui, estime l'ultime par $C_{i,I-i}/\hat p_i$.

> 📐 **BF comme moyenne pondérée (crédibilité).** L'ultime BF s'écrit $\hat U^{\text{BF}}_i=C_i+P_i\rho_i(1-\hat p_i)$, et l'ultime CL $\hat U^{\text{CL}}_i=C_i/\hat p_i$. On en déduit
> $$\hat U_i^{\text{BF}}=\hat p_i\,\hat U^{\text{CL}}_i+(1-\hat p_i)\,P_i\rho_i.$$
> **Plus l'année est développée ($\hat p_i$ proche de 1), plus BF croit les données ; plus elle est jeune ($\hat p_i$ proche de 0), plus il croit l'a priori.** C'est de la crédibilité (section 2.4.4) avec comme poids la part payée. Le choix du ratio a priori compte donc surtout pour les années récentes, celles qui portent la provision.

La variante **Cape Cod** estime l'a priori **à partir des données** plutôt que de le fixer : $\hat\rho=\sum_iC_i\big/\sum_iP_i\hat p_i$ (le ratio sinistres sur primes moyen, ramené à un ultime), puis applique BF.


Prenons un a priori **de plan** de 80 % pour les deux garanties, une valeur raisonnable *a priori* mais qui n'a jamais été confrontée aux réalisations. Les ratios réellement programmés sont, en moyenne, de 92 % pour la responsabilité civile (l'inflation des indemnités le tire au-dessus de l'hypothèse de tarification) et de 61 % pour les dommages. Le Cape Cod les retrouve : 92 % et 61 %.

Résultat, comparé aux paiements réels :

- **Responsabilité civile** (provision réelle : 242,1 M€) : BF avec l'a priori de 80 % donne 207,4 M€ (−14 %), Cape Cod 238,3 M€ (−2 %). L'a priori trop bas **entraîne BF vers le bas**, surtout sur les années récentes : pour 2024, BF donne 60,6 M€ contre 71,9 M€ pour le chain ladder (et 72,1 M€ réellement payés).
- **Dommages** (provision réelle : 32,3 M€) : BF avec 80 % donne 41,6 M€ (+29 %), car l'a priori est ici **trop haut** ; Cape Cod, qui apprend le ratio dans les données, donne 32,0 M€ (−1,0 %).

**BF n'est donc pas « meilleur » que le chain ladder : il est meilleur quand l'a priori est bon et les données bruitées, pire quand l'a priori est faux.** Son intérêt est d'être **stable** : une dérive du premier paiement n'emporte pas la provision. Le Cape Cod garde cette stabilité en se débarrassant du risque d'un a priori mal posé, au prix d'une hypothèse (le même ratio pour toutes les années, ce qui est faux ici à cause de l'inflation).

### 2.5.3 L'erreur de prédiction de Mack

Une provision est une **moyenne** d'une distribution ; l'écart-type de cette distribution est ce que mesure l'**erreur quadratique de prédiction** (MSEP). Mack (1993) a obtenu, sous ses hypothèses, une formule explicite pour celle de l'ultime d'une année de survenance $i$ qui a atteint le délai $d_i$ :
$$\widehat{\mathrm{MSEP}}(\hat U_i)=\hat U_i^{\,2}\sum_{k=d_i}^{J-1}\frac{\hat\sigma_k^2}{\hat f_k^{\,2}}\Bigl(\frac{1}{\hat C_{i,k}}+\frac{1}{\sum_{j}C_{j,k}}\Bigr),\qquad \hat\sigma_k^2=\frac{1}{n_k-1}\sum_jC_{j,k}\Bigl(\frac{C_{j,k+1}}{C_{j,k}}-\hat f_k\Bigr)^2,$$
où $n_k$ est le nombre d'années disponibles au délai $k$ et la dernière somme porte sur les années utilisées pour estimer $\hat f_k$. Deux termes, deux sources d'incertitude : $1/\hat C_{i,k}$ est la **variance de processus** (le hasard pur des paiements futurs, plus fort quand le montant est petit) et $1/\sum_jC_{j,k}$ la **variance d'estimation** (les facteurs sont estimés avec une précision limitée). Pour le **total** de toutes les années, il faut ajouter les covariances entre années, qui existent parce que **les mêmes facteurs estimés** servent à toutes les lignes.


```text
       réserve  erreur-type  coefficient de variation
2017     3.063        0.203                     0.066
2018     5.022        0.372                     0.074
2019    10.042        0.587                     0.058
2020    19.522        0.824                     0.042
2021    27.200        0.972                     0.036
2022    36.233        1.256                     0.035
2023    58.579        2.103                     0.036
2024    69.589        3.554                     0.051
total  230.159        5.359                     0.023
```

(Les années 2015 et 2016, dont la provision est quasi nulle, sont omises du tableau.) Pour la responsabilité civile, l'erreur-type de la provision totale est de **5,4 M€**, soit 2,3 % de la provision : un chiffre rassurant. Par année, le coefficient de variation va de 3 % à 7 % (années 2017 à 2024) ; la dernière année, à elle seule, contribue pour 3,6 M€ à l'erreur-type. Pour la garantie à développement court, l'erreur-type vaut 1,3 M€ pour une provision de 31,9 M€ (4 %).

Maintenant, la comparaison avec la réalité, qui donne à ce chiffre sa juste signification : la provision réelle dépasse celle du chain ladder sans queue de **2,2 erreurs-types de Mack**. Autrement dit, **l'erreur réellement commise est sans commune mesure avec l'erreur-type annoncée**, parce que la formule de Mack ne couvre que le hasard des paiements et l'estimation des facteurs **sous l'hypothèse que le schéma observé se prolonge** : elle ne couvre ni la queue ni les ruptures. Avec la queue extrapolée, l'écart tombe à 1,3 erreur-type.

> ⚠️ **L'erreur de Mack est un plancher.** Elle mesure l'incertitude *statistique conditionnelle au modèle*. L'incertitude **de modèle** (queue, rupture de schéma, choix de la méthode) lui est généralement bien supérieure. Les directions des risques en tiennent compte en élargissant ces intervalles ou en comparant plusieurs méthodes (section 2.5.6).

### 2.5.4 Le bootstrap de l'« overdispersed Poisson »

Mack donne un écart-type, pas une distribution. Pour obtenir **tous les quantiles** (le 75ᵉ centile d'une provision prudente, le 99,5ᵉ de la réglementation, chapitre 4), on simule. Le **bootstrap de England et Verrall** repose sur le fait que le chain ladder est exactement l'estimation d'un modèle de Poisson sur-dispersé (*overdispersed Poisson*, ODP) pour les paiements **incrémentaux** : $E[Y_{ij}]=\exp(a_i+b_j)=\mu_{ij}$, $\mathrm{Var}(Y_{ij})=\phi\,\mu_{ij}$. Le GLM de Poisson à effet ligne et effet colonne redonne la même provision que le chain ladder.

L'algorithme tient en cinq étapes : (1) ajuster le GLM sur le triangle observé, obtenir les $\hat\mu_{ij}$ ; (2) calculer les **résidus de Pearson** $r_{ij}=(y_{ij}-\hat\mu_{ij})/\sqrt{\hat\mu_{ij}}$, corrigés du nombre de paramètres ; (3) **rééchantillonner** ces résidus avec remise et en déduire un triangle pseudo-observé $y^*_{ij}=\hat\mu_{ij}+r^*_{ij}\sqrt{\hat\mu_{ij}}$ ; (4) **réajuster** le modèle sur $y^*$ (incertitude d'estimation) ; (5) **simuler** les paiements futurs par une loi de Poisson sur-dispersée de moyenne $\hat\mu^*_{ij}$ (incertitude de processus), et cumuler. On répète 1 000 fois.


![Distribution de la provision totale de responsabilité civile obtenue par bootstrap de l'overdispersed Poisson (1 000 simulations) ; trait noir : provision du chain ladder ; trait rouge : quantile à 99,5 % ; trait orange pointillé : provision réellement payée ensuite.](figures/ch02-bootstrap.png)

La provision centrale du modèle ODP vaut 230,2 M€, **identique à celle du chain ladder** (écart de 0,000 %), ce qui vérifie l'équivalence annoncée. L'écart-type de la distribution simulée est de 5,6 M€ (contre 5,4 M€ pour Mack : les deux méthodes mesurent la même chose et s'accordent). La dispersion estimée est $\hat\phi\approx17 906$ € (la programmation avait fixé 20 000 €). Les quantiles sont : médiane 230,4 M€, 75ᵉ centile 234,1 M€, 95ᵉ 239,4 M€, 99,5ᵉ 245,3 M€. La **provision réellement payée** (242,1 M€) se place au 98ᵉ centile de cette distribution : elle est dans l'étendue, mais loin du centre, ce qui est cohérent avec ce que nous savons (la queue n'est pas dans le triangle).


> 🧪 **À quoi servent les quantiles d'une provision ?** À trois choses : (1) fixer une provision **prudente** (au 75ᵉ centile, par exemple) ; (2) mesurer le **risque de provisionnement** que Solvabilité II demande de couvrir par du capital (la différence entre le 99,5ᵉ centile et la moyenne, chapitre 4, section 4.2) ; (3) comparer des garanties ou des méthodes. Un bootstrap bien fait sur un triangle de dix ans reste un outil **grossier** : un seul schéma de résidus, des années supposées indépendantes, une queue fixée.

### 2.5.5 Quand l'hypothèse de calendrier échoue : le triangle « choc »

Le troisième triangle a été fabriqué avec un **choc de +12 %** sur tous les paiements de l'année calendaire 2022 (une diagonale entière), en plus de l'inflation habituelle. C'est exactement le type d'événement qui viole l'hypothèse de Mack. Comment le détecter ?

**Les résidus par année calendaire.** On ajuste le modèle ODP, on calcule les résidus de Pearson de chaque cellule, et on les range **par diagonale**. Si le schéma est stable, les résidus d'une diagonale n'ont aucune raison d'être de même signe.


![Résidus de Pearson du modèle ODP, cellule par cellule, pour le triangle stable (à gauche) et pour le triangle avec choc calendaire (à droite) ; rouge : paiement supérieur au modèle, bleu : inférieur. La diagonale du choc (année calendaire 2022, repérée par des points noirs) apparaît comme une bande rougeâtre.](figures/ch02-residus.png)

Sur le triangle stable, le résidu moyen d'une diagonale ne dépasse pas 0,73 en valeur absolue ; sur le triangle « choc », la diagonale 2022 a un résidu moyen de **1,41**, et aucune autre ne dépasse 0,60. **Le choc se voit en une image, bien avant de se voir dans la provision.** Deuxième symptôme : l'erreur de Mack du total passe de 5,4 M€ (triangle stable) à 8,2 M€ (triangle choc) : le modèle perçoit un désordre dans les facteurs sans le localiser.

**Et la provision ?** Sans queue, le chain ladder donne 242,2 M€ pour 243,5 M€ réellement payés : presque juste. C'est un effet de **compensation** : le choc de 2022 a gonflé les facteurs et les paiements cumulés, ce qui pousse la provision vers le haut, tandis que l'absence de queue la tire vers le bas ; les deux effets s'annulent presque. La preuve que ce n'est pas la méthode qui est bonne : dès que l'on ajoute la queue extrapolée, qui amplifie les facteurs gonflés, la provision monte à 262,6 M€, soit 8 % de trop (contre 3 % sur le triangle stable). Et, par année, les écarts atteignent 26 %. Une compensation de ce genre est une **chance**, pas une propriété de la méthode.

Pour voir le dommage lorsque la chance disparaît, déplaçons le choc sur **la dernière diagonale** du triangle stable (le paiement de l'année en cours est majoré de 12 %, rien ne se produit ensuite) :


La provision du chain ladder passe à 280,0 M€, soit 16 % **de plus** que la provision réellement payée : le modèle a pris un accident calendaire pour une tendance et l'a propagé à toute la provision. Corrigée du choc (si on le connaît et que l'on dégonfle la diagonale), elle revient à 249,3 M€ (3 % d'écart). **L'enjeu n'est pas la méthode mais la connaissance du portefeuille** : savoir qu'une diagonale est anormale vaut plus que n'importe quelle sophistication. Les remèdes sont de la même famille : exclure ou dégonfler la diagonale douteuse des facteurs, ajouter un **effet calendaire** au GLM (en acceptant de le prolonger), ou changer de méthode (BF, qui est moins sensible puisqu'il s'appuie moins sur le dernier cumul).

### 2.5.6 Comparer les méthodes aux paiements réels

Résumons ce que chaque méthode donne, pour les trois triangles, avec l'écart par rapport à la provision réellement payée (en %) :


```text
                                          RC      dommages           choc
méthode (M€)                                                             
CL sans queue                   230.2 (-5 %)   31.9 (-1 %)   242.2 (-1 %)
CL avec queue                   249.3 (+3 %)   31.9 (-1 %)   262.6 (+8 %)
Bornhuetter-Ferguson           207.4 (-14 %)  41.6 (+29 %)  212.2 (-13 %)
Cape Cod                        238.3 (-2 %)   32.0 (-1 %)   249.3 (+2 %)
médiane du bootstrap ODP (RC)   230.4 (-5 %)                             
provision réellement payée             242.1          32.3          243.5
```

Trois enseignements. **Cape Cod est ici le plus régulier** (écarts de −2 %, −1 % et +2 %) : son hypothèse (un même ratio sinistres sur primes pour toutes les années) est presque vraie dans ces données, et il intègre la queue sans la deviner ; dans un portefeuille dont le ratio change d'une année à l'autre, il perdrait cet avantage. **Le chain ladder** est excellent quand la queue est courte (dommages : −1 %) et dépend entièrement de la queue quand elle ne l'est pas : de −5 % sans queue à +3 % avec la queue extrapolée en responsabilité civile, et +8 % sur le triangle choc. **BF avec un a priori faux est la pire des méthodes** (−14 %, +29 % et −13 %) : elle est stable, mais elle est stable autour du mauvais chiffre.

La conclusion pratique n'est pas « utilisez Cape Cod » : c'est que **les écarts les plus grands viennent des hypothèses (queue, a priori, stabilité du calendrier), pas des estimateurs**. D'où la discipline : appliquer **plusieurs méthodes**, expliquer leurs écarts, regarder les résidus, puis fixer sa provision avec un jugement documenté. C'est ce que les actuaires appellent un « meilleur estimé » (*best estimate*), et c'est aussi ce que demande Solvabilité II (chapitre 4, section 4.2).

> ✅ **À retenir.**
> - **BF** remplace l'extrapolation du dernier cumul par un a priori ; c'est une moyenne pondérée par la part payée entre chain ladder et a priori. Un a priori faux donne une provision fausse ; **Cape Cod** apprend l'a priori dans les données.
> - La formule de **Mack** donne l'erreur de prédiction du chain ladder (processus + estimation) ; c'est un **plancher** : elle ignore la queue et les ruptures de schéma.
> - Le **bootstrap ODP** redonne la provision du chain ladder et sa **distribution** complète ; ses quantiles servent à la prudence et au capital.
> - Un **choc calendaire** (diagonale) se voit dans les résidus par diagonale ; il peut s'annuler sur le total et se payer ailleurs. La connaissance du portefeuille prime sur la méthode.
> - Comparer plusieurs méthodes et expliquer leurs écarts est la pratique, pas le choix d'une méthode unique.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.8 et exercices 2.11 à 2.13 (Bornhuetter–Ferguson, erreur de Mack, bootstrap, diagnostic d'un choc calendaire).


## 2.6 ➕ Pour aller plus loin : l'assurance santé

> 🧭 **Section optionnelle.** L'assurance santé réutilise la boîte à outils de la tarification (GLM, Gamma/Tweedie, validation hors période), mais elle pose des problèmes d'une autre nature : le coût est **continu et positif presque toujours** (on consomme tous des soins), il est **concentré** sur une minorité de personnes malades, et **le choix du niveau de garantie dépend de la santé de l'assuré**. Les données sont celles de `sante_assures.csv` (simulées).

### 2.6.1 Que coûte la santé ?

Le fichier compte 39 112 lignes *assuré-année* (2022 à 2024) pour 15 884 personnes différentes, soit 35 792 années d'exposition. Le coût annuel moyen est de 1 412 € par année d'exposition. Quatre postes le composent.


```text
consultations      22 %
hospitalisation    59 %
pharmacie          11 %
dentaire            8 %
```

L'**hospitalisation** pèse 59 % du coût, les consultations 22 %, la pharmacie 11 %, le dentaire 8 %. Surtout, le coût est **très concentré** : les 5 % d'assurés-années les plus coûteux représentent 46 % du coût total, les 10 % les plus coûteux 62 %, et le 1 % le plus coûteux à lui seul 17 %. C'est une concentration moins extrême que celle des sinistres automobiles (section 2.1.5), mais elle domine la gestion du risque : **le coût d'un portefeuille santé se joue sur quelques malades**.

![À gauche : courbe de concentration du coût (plus elle s'éloigne de la diagonale, plus le coût est concentré sur peu d'assurés). À droite : coût annuel par année d'exposition selon la tranche d'âge, avec ou sans affection de longue durée (ALD) ; les points avec ALD aux âges extrêmes reposent sur peu d'assurés.](figures/ch02-sante.png)

Deux facteurs dominent. L'**âge** : de 904 € pour les 18-29 ans à 2 280 € pour les plus de 75 ans. Et l'**affection de longue durée** (ALD, maladie chronique) : elle concerne 17 % des lignes et multiplie le coût par 3,5 environ. Contrairement à l'automobile, **la part des assurés sans aucun coût est quasi nulle** (0,003 % des lignes) : tout le monde consomme au moins de la pharmacie. Les modèles « à excès de zéros » ou « à deux parties » (probabilité d'avoir un coût, puis montant) sont donc inutiles ici.

### 2.6.2 Modéliser le coût annuel

Le coût par année d'exposition étant positif et asymétrique, on le modélise par un **GLM Gamma à lien logarithmique**, pondéré par l'exposition (une ligne couvrant trois mois pèse un quart d'une ligne d'un an). On compare quatre tarifs, du plus simple au plus fin, sur 2022-2023 pour estimer et sur 2024 pour juger :

```python
tr_s = sante[sante["annee"] <= 2023]
modele = smf.glm("cpe ~ age + I(age ** 2) + ald + C(niveau) + C(sexe)", tr_s,
                 family=sm.families.Gamma(sm.families.links.Log()), freq_weights=tr_s["exposition"]).fit()
```


```text
                           Gini 2024  prévu / observé
tarif                                                
plat                          -0.002            0.974
âge                            0.143            0.997
âge + ALD                      0.304            0.998
âge + ALD + niveau + sexe      0.321            0.999
```

L'indice de Gini passe de −0,00 pour le tarif plat à 0,14 avec l'âge seul, 0,30 en ajoutant l'ALD et 0,32 avec le niveau de garantie et le sexe (bruit d'un tarif aléatoire : 0,011). L'**ALD** est le gain le plus important : c'est une information que l'assureur connaît (par la déclaration, les remboursements précédents) et qui sépare nettement les coûts. Le niveau apporte encore, mais pour une raison qui n'est pas du tout celle que l'on croit : c'est l'objet de la section suivante. Le tarif complet est calibré à 100 % du coût observé en 2024 (prévu sur observé).

### 2.6.3 Sélection adverse et aléa moral

Regardons le coût selon le niveau de garantie (basique, confort, premium) :


```text
         coût par année d'exposition  part d'ALD  âge moyen
niveau                                                     
basique                       1052.0         9.5       44.4
confort                       1423.0        17.3       45.0
premium                       2246.0        35.9       46.2
```

Le niveau « premium » coûte 2,1 fois le niveau « basique » (1,35 pour « confort »). On y verrait, à tort, la conséquence d'une meilleure garantie. Deux mécanismes très différents s'y mélangent :

- la **sélection adverse** : les personnes malades choisissent plus souvent la meilleure garantie (la part d'ALD passe de 10 % en basique à 36 % en premium) ; l'âge moyen, lui, est le même (44,4 et 46,2 ans) ;
- l'**aléa moral** : une garantie plus généreuse **change le comportement** (on consulte plus, on prend le dentaire).

Pour les séparer, on ajuste un modèle sur l'âge, l'ALD et le sexe : l'effet « niveau » ajusté vaut alors **1,48** pour premium (intervalle à 95 % de 1,38 à 1,59) et 1,18 pour confort. La décomposition est multiplicative : le rapport de 2,20 (proche du rapport brut, mais calculé avec les valeurs ajustées du modèle) vaut 1,48 de **sélection** (leur coût si on leur donnait le comportement « basique », par rapport au coût des assurés basique) fois 1,48 d'**aléa moral**. Les deux effets pèsent autant l'un que l'autre.

> ⚠️ **Pourquoi c'est un problème de tarif.** Si l'on tarife la différence entre niveaux sur le rapport brut (2,1), on facture à l'assuré une différence de comportement qui est en réalité, pour moitié, une différence de santé : le prix du premium devient prohibitif pour ceux qui n'ont pas d'ALD, qui quittent alors le niveau, ce qui élève encore le coût moyen des restants. C'est la **spirale d'antisélection** classique. L'assureur doit tarifer le niveau sur la **composition réelle** de ses assurés (et la surveiller), et se protéger par des délais de carence, une sélection médicale ou une **mutualisation** assumée.

### 2.6.4 Table de morbidité et mutualisation

Une **table de morbidité** donne, par âge, la fréquence et le coût moyen des événements de santé. On la lit ici par tranche d'âge : le nombre d'hospitalisations pour 1 000 années d'exposition, le coût moyen d'un séjour, le nombre annuel de consultations et le coût annuel.


```text
         hospitalisations / 1000 ans  coût moyen d'un séjour (€)  consultations / an  coût annuel (€)  exposition (ans)
tranche                                                                                                                
0-17                            84.0                      5775.4                 4.1            852.9            1036.3
18-29                           98.7                      4692.9                 5.2            904.5            6098.4
30-44                          142.3                      4944.1                 6.5           1227.7           12162.4
45-59                          195.3                      5080.9                 8.2           1617.9            9356.8
60-74                          218.7                      5010.1                 9.8           1805.7            4659.3
75+                            278.4                      5100.5                11.8           2280.5            2478.7
```

Trois régularités. Les hospitalisations croissent avec l'âge : de 84 pour 1 000 années d'exposition chez les 0-17 ans à 278 chez les plus de 75 ans. Les consultations aussi (de 4,1 à 11,8 par an). En revanche, **le coût moyen d'un séjour varie peu et sans tendance nette** (4 693 € à 5 775 € selon la tranche d'âge) : c'est la *fréquence*, pas la gravité, qui augmente avec l'âge. On retrouve la décomposition fréquence × sévérité de la section 2.2.

**Mutualiser, ou tarifer par âge ?** Une mutuelle peut appliquer une **prime unique** (la mutualisation) ou une prime par âge. Avec une prime unique égale au coût moyen (1 412 €), les assurés de moins de 30 ans (qui représentent 20 % de l'exposition) paient 57 % **de plus** que leur coût (897 € par an), et subventionnent les autres. C'est un choix de solidarité, qui a un prix : si 30 % des moins de 30 ans partent (parce qu'un concurrent leur propose moins cher), la prime d'équilibre des restants passe à 1 445 €, soit **2,3 % de plus**, ce qui incite d'autres bons risques à partir à leur tour. La solidarité n'est tenable que si elle est **encadrée** (obligation d'assurance, règles de tarification communes pour tout le marché) ou compensée (ajustement de risque entre assureurs).

### 2.6.5 Inflation médicale, grands risques et ajustement de risque

**Tendance.** Les coûts de santé progressent avec les prix, mais aussi avec la fréquence de consommation. Un modèle qui contrôle l'âge, l'ALD, le niveau et le sexe, et ajoute l'année, estime la tendance annuelle du coût à l'unité d'exposition.


L'estimation donne 2,0 % par an (intervalle à 95 % de −1,0 % à 5,2 %). La vérité programmée est une inflation de 3 % sur le coût unitaire des consultations et des hospitalisations, nulle sur les autres postes : le résultat global se situe donc naturellement un peu en dessous de 3 %. **Une tendance se projette pour l'année tarifée** : sans ajustement, un tarif construit sur les années passées est d'avance en retard.

**Grands risques.** Les 899 lignes de plus de 10 000 € de coût annuel ne représentent que 2,3 % des lignes, mais 30 % du coût. Comme en automobile (section 2.1.5), on les traite à part : on **écrête** le coût individuel dans le tarif et l'on met en commun la charge au-delà (une **mutualisation des grands risques** entre assureurs, ou une réassurance : chapitre 6).

**Ajustement de risque.** Quand plusieurs assureurs se partagent un même marché obligatoire à prime commune, celui qui attire les malades est pénalisé. On corrige par un **ajustement de risque** : chaque assureur reverse ou reçoit une compensation fonction du profil de ses assurés (âge, sexe, ALD), calculée à partir d'un modèle de coût comme celui de la section 2.6.2. C'est l'application la plus directe de ce que nous avons fait, avec un enjeu politique : ce qu'on compense (l'âge, l'ALD) et ce qu'on ne compense pas (le comportement) se décide par la loi.

> ✅ **À retenir.**
> - Le coût de santé est **positif presque toujours** (un GLM Gamma convient, pas de modèle à excès de zéros) et **très concentré** sur quelques assurés.
> - Les facteurs dominants sont l'**âge** et l'**affection de longue durée** ; le coût d'un séjour varie peu avec l'âge, c'est la **fréquence** qui croît.
> - L'effet brut du niveau de garantie mélange **sélection adverse** et **aléa moral** ; un modèle ajusté permet de les séparer (ici, à parts égales).
> - Une prime **unique** subventionne les jeunes ; si ceux-ci partent, la prime d'équilibre des restants monte (spirale d'antisélection) : la solidarité demande un cadre.
> - Les grands risques s'écrêtent et se mutualisent ; l'**ajustement de risque** compense les différences de profil entre assureurs.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.9 et exercice 2.14 (coût santé, sélection adverse et aléa moral, table de morbidité).


## Bilan du chapitre 2

Vous savez maintenant :

- **décomposer** le coût d'un contrat en une fréquence et une sévérité, estimer une fréquence **sur l'exposition** (et non sur le nombre de contrats), reconnaître la **sur-dispersion** et la modéliser par une binomiale négative (Poisson–Gamma) ;
- **décrire** des montants asymétriques (Gamma pour le cœur, Pareto généralisée pour la queue), mesurer le poids des gros sinistres, **écrêter** et mutualiser leur charge, et reconstruire la **charge annuelle** d'un portefeuille par le modèle collectif ;
- **construire un tarif** : prime pure $=E[N\mid x]\,E[X\mid x]$ par deux GLM (ou un Tweedie), chargements $(\pi+F)/(1-\tau-m)$, relativités lisibles, puis le **valider hors période** (courbe de Lorenz ordonnée, Gini et son intervalle, lecture par dixièmes) et mesurer le prix d'un tarif trop grossier (**antisélection**) ;
- **provisionner** par triangle et *chain ladder*, choisir une **queue**, et **juger a posteriori** une provision contre les paiements réels ;
- (en option) lire la **déviance** et les tests d'un GLM, choisir la forme des variables, **régulariser**, doser expérience et a priori par la **crédibilité** de Bühlmann–Straub, comparer un GLM à un boosting ;
- (en option) estimer une provision **avec son incertitude** (Bornhuetter–Ferguson, Cape Cod, Mack, bootstrap ODP), diagnostiquer un **choc calendaire** par les résidus de diagonale ;
- (en option) analyser un portefeuille de **santé** : concentration des coûts, sélection adverse et aléa moral, table de morbidité, mutualisation.

Le tableau suivant résume **ce que nous avons mesuré**, avec la vérité programmée quand on la connaît :

| Question | Résultat mesuré | Vérité ou référence |
|---|---|---|
| Fréquence annuelle (automobile) | 6,61 % | environ 6,5 % |
| Hétérogénéité $\alpha$ (binomiale négative) | 0,47 ± 0,09 | 0,4 |
| Part du coût due aux sinistres > 100 000 € | 53 % pour 1,6 % des sinistres | queue de Pareto programmée |
| Quantile à 99,5 % de la charge annuelle | 23,9 M€ (moyenne 17,1 M€) | plancher plausible |
| Gini du tarif complet, 2024 | 0,18 (plat : 0,02) | bruit d'un tarif aléatoire : ± 0,04 |
| Ratio sinistres/primes d'un tarif plat après antisélection | 114 % | 97 % avant |
| Provision RC par chain ladder, sans queue | 230,2 M€ | réel : 242,1 M€ |
| Provision RC par chain ladder, avec queue extrapolée | 249,3 M€ | réel : 242,1 M€ |
| Erreur de Mack sur la provision totale (RC) | 5,4 M€ | l'erreur réelle est bien plus grande |
| Provision dommages (développement court) | 31,9 M€ | réel : 32,3 M€ |
| Niveau « premium » contre « basique » (santé) | brut ×2,1, ajusté ×1,48 | sélection et aléa moral à parts égales |

Trois idées dépassent ce chapitre. **D'abord, ce qui fait la qualité d'un modèle d'assurance se joue dans les queues et les hypothèses**, pas dans la vraisemblance : la charge annuelle dépend de quelques sinistres, la provision de la queue du triangle. **Ensuite, un chiffre de risque est toujours accompagné de son incertitude et d'une validation hors période** : un Gini sans intervalle, une provision sans erreur de prédiction, un quantile à 99,5 % sans mention de sa fragilité ne sont pas des résultats. **Enfin, un tarif et une provision sont des décisions** : ils engagent de l'argent, créent des subventions entre assurés, exposent à l'antisélection, et leur « juste » valeur ne se connaît que des années plus tard.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 à 2.9 (comptage et exposition, binomiale négative, queue de Pareto, modèle collectif, GLM de fréquence et de sévérité, validation et antisélection, chain ladder, Bornhuetter–Ferguson/Mack/bootstrap, santé) et exercices 2.1 à 2.14.

Le chapitre 3 reprend la **charge annuelle** et ses queues sous un autre angle : celui des **mesures de risque** (valeur à risque, perte attendue au-delà du seuil) et des **stress tests**, qui servent aussi bien à une banque qu'à une mutuelle.


---

# Chapitre 3 : Mesures de risque et stress tests

> « Un chiffre de risque est une réponse à une question. Avant de le lire, il faut retrouver la question. »

Les deux premiers chapitres ont chiffré des risques *individuels* : la probabilité qu'un emprunteur ne rembourse pas, la charge de sinistres d'un contrat d'assurance. Mais ni la banque ni la mutuelle ne vivent contrat par contrat. Elles vivent **en portefeuille**, c'est-à-dire avec des milliers de risques qui se compensent un jour et s'additionnent le lendemain, et c'est la **perte du portefeuille entier** qui décide de la solvabilité. Ce chapitre apprend à résumer cette perte par quelques nombres, à les calculer de plusieurs façons, à les **mettre à l'épreuve** par des scénarios extrêmes, puis à vérifier qu'ils tiennent face à la réalité.

Le fil conducteur est une phrase : **un nombre de risque n'a de sens qu'avec sa définition, son horizon, son niveau de confiance… et son incertitude**. La *valeur à risque* (VaR) à 99 % sur un jour et la VaR à 99 % sur dix jours ne répondent pas à la même question ; la VaR et la perte moyenne au-delà de la VaR (l'*expected shortfall*) ne disent pas la même chose de la queue de la distribution ; un modèle calibré en période calme se trompe précisément quand la période cesse de l'être. Nous le verrons sur des données simulées dont nous connaissons la vérité : nous pourrons donc, ce que la vie réelle ne permet presque jamais, **juger chaque méthode par rapport à ce qui s'est vraiment passé**.

## Le chemin de ce chapitre

- **3.1 VaR et expected shortfall.** Définir une perte, un quantile, un horizon. Calculer la VaR par la loi normale (formule démontrée), par l'histoire, par simulation, par un modèle de volatilité qui change (EWMA, GARCH). Comprendre l'expected shortfall, démontrer pourquoi la VaR n'est pas une mesure *cohérente*, et mesurer l'incertitude d'un chiffre de queue.
- **3.2 Stress tests et scénarios.** Répondre à la question « et si ? » : sensibilités, scénarios historiques et hypothétiques, scénario *macroéconomique* relié aux défauts de crédit par un modèle statistique, choc de taux d'intérêt, stress *inversé*, et pourquoi les corrélations montent quand tout va mal.
- **➕ 3.3 Risques opérationnel, de marché et de liquidité.** L'approche par distribution des pertes (fréquence × sévérité) appliquée à des incidents opérationnels, les contributions au risque d'un portefeuille de marché, et un aperçu de la liquidité.
- **➕ 3.4 Backtesting et validation des modèles.** Les tests de Kupiec et de Christoffersen, le « feu tricolore », le contrôle de l'expected shortfall, et la démarche de validation indépendante d'un modèle, avec son risque propre : le **risque de modèle**.
- **Bilan du chapitre**, puis, dans le **cahier**, huit applications et douze exercices corrigés.

Ce chapitre s'appuie sur le volume II (régression logistique, section 2.2 ; modèles GARCH, section 4.4 ; valeurs extrêmes, section 6.5) et sur le volume III (validation, chapitre 1 ; métriques et calibration, chapitre 5). Il prépare le chapitre 4 : les cadres réglementaires de Bâle et de Solvabilité *imposent* des mesures de risque, et nous saurons ce qu'elles valent.

## Les données du chapitre

> 📦 **Données (simulées, graines fixes).** Quatre jeux, tous fabriqués par `build/donnees5.py`, qui connaît donc la vérité.
> - `rendements_marche.csv` : 4 000 jours ouvrés de rendements journaliers de cinq actifs (deux paniers d'actions, des obligations, de l'immobilier coté, des matières premières). La volatilité change au fil du temps (modèle GARCH) et le marché alterne entre un régime **calme** et un régime de **stress** (volatilité doublée, corrélations en hausse) ; `marche_verite.csv` donne le régime vrai de chaque jour.
> - `taux_defaut_macro.csv` : 80 trimestres de variables macroéconomiques (croissance, chômage, variation de l'immobilier) et le taux de défaut annualisé d'un portefeuille de crédit, avec une récession aux trimestres 48 à 54.
> - `courbe_taux.csv` : 120 mois d'une courbe de taux sur neuf maturités, avec un cycle de hausse des taux entre les mois 60 et 90.
> - `pertes_operationnelles.csv` : dix ans d'incidents opérationnels (fraudes, erreurs de traitement, pannes, pratiques commerciales) avec perte brute, récupération et perte nette.
>
> Le portefeuille d'exemple est celui d'un investisseur institutionnel fictif : **100 M€** répartis ainsi : 35 % d'actions A, 15 % d'actions B, 30 % d'obligations, 10 % d'immobilier et 10 % de matières premières. Toutes les pertes sont exprimées en **millions d'euros**, comptées **positivement** (une perte de 2 signifie que le portefeuille a perdu 2 M€).

<!--sortie-->

Un premier regard suffit à comprendre l'enjeu : l'écart-type de la perte journalière du portefeuille est de 0,57 M€ en régime calme et de 1,56 M€ en régime de stress, soit 2,7 fois plus, alors que les jours de stress ne représentent que 7,0 % des 4 000 jours observés. Presque toute la difficulté du chapitre tient dans cette asymétrie : **la queue de la distribution est fabriquée par une minorité de jours qui ne ressemblent pas aux autres**.


## 3.1 VaR et expected shortfall

Cette section répond à une question qui paraît simple : *combien peut-on perdre ?* Elle montrera qu'il n'existe pas **un** chiffre mais une famille de chiffres, chacun avec une définition précise, des hypothèses et une incertitude. Nous partons de la perte d'un portefeuille, la résumons par la **valeur à risque** (VaR) et l'**expected shortfall** (ES), calculons ces deux mesures de quatre façons différentes, puis démontrons que la VaR a un défaut de fond que l'ES n'a pas.

### 3.1.1 De la position à la perte

Un risque de marché ou de portefeuille se mesure sur une **perte** : la variation de valeur, changée de signe pour qu'une perte soit positive. Si la valeur du portefeuille est $V$ et que son rendement sur la période est $R$, la perte est $L=-V\,R$. Un portefeuille de $n$ actifs de poids $w_1,\dots,w_n$ (positifs, de somme 1) a pour rendement $R=\sum_i w_iR_i$ : **la perte du portefeuille est une combinaison linéaire des pertes des actifs**, ce qui donnera plus loin une formule simple pour sa variance.

Notre portefeuille d'exemple vaut 100 M€ et se répartit comme suit.

| Actif | Poids | Montant |
|---|---|---|
| Actions A | 35 % | 35 M€ |
| Actions B | 15 % | 15 M€ |
| Obligations | 30 % | 30 M€ |
| Immobilier coté | 10 % | 10 M€ |
| Matières premières | 10 % | 10 M€ |

Sur les 4 000 jours observés, la perte journalière moyenne est de -0,016 M€ (le portefeuille a plutôt gagné), son écart-type de 0,69 M€, la pire journée a coûté 5,98 M€ et la meilleure a rapporté 10,45 M€. Le coefficient d'aplatissement en excès (*kurtosis*) vaut 20,3, alors qu'il serait nul pour une loi normale : les journées extrêmes sont **beaucoup plus fréquentes** que ne le prévoirait une cloche de Gauss de même écart-type. (Le plus gros mouvement observé est d'ailleurs un *gain* ; il tire le kurtosis vers le haut, mais la VaR ne regarde que le côté des pertes, où la queue est elle aussi épaisse, comme nous allons le voir.)

<!--sortie-->

Comptons les jours où la perte dépasse la moyenne de plus de trois écarts-types : il y en a 40 dans nos données, contre 5,4 attendus si la loi était normale. Voilà le point de départ : nous allons chercher des nombres qui résument bien **ces** jours-là.

### 3.1.2 La valeur à risque : un quantile de la perte

> 📐 **Définition.** Soit $L$ la perte sur un horizon donné et $\alpha\in(0,1)$ un niveau de confiance (95 %, 99 %…). La **valeur à risque** de niveau $\alpha$ est
> $$\mathrm{VaR}_\alpha(L)=\inf\{x:\ P(L\le x)\ge\alpha\},$$
> c'est-à-dire le **quantile** d'ordre $\alpha$ de la perte : la perte n'est dépassée qu'avec la probabilité $1-\alpha$.

Une VaR n'a donc de sens qu'accompagnée de **trois précisions** : le niveau $\alpha$, l'**horizon** (un jour, dix jours, un an) et la **convention de signe** (ici : perte positive). « VaR à 99 % sur un jour de 2 M€ » signifie : *sur 99 jours sur 100, la perte du jour ne dépasse pas 2 M€*. Elle ne dit **ni** « la perte maximale » **ni** « ce que l'on perd les mauvais jours » : les jours où la VaR est dépassée peuvent coûter à peine plus ou bien trois fois plus, la VaR ne le saura jamais.

Un exemple à la main, sur dix pertes journalières fictives (en M€), classées de la plus petite à la plus grande : $-0{,}7$ ; $-0{,}4$ ; $-0{,}1$ ; $0{,}2$ ; $0{,}3$ ; $0{,}5$ ; $0{,}9$ ; $1{,}4$ ; $2{,}6$ ; $4{,}1$. Pour $\alpha=90\ \%$ et dix observations, le plus petit $x$ tel qu'au moins 90 % des pertes soient inférieures ou égales à $x$ est la **neuvième** valeur : la VaR à 90 % vaut 2,6 M€. Pour $\alpha=80\ \%$, c'est la huitième : 1,4 M€. Retenons la règle : avec $n$ observations, la VaR empirique est la valeur de rang $\lceil\alpha n\rceil$.

<!--sortie-->

Sur nos 4 000 jours, la VaR historique s'obtient en une ligne. L'option `method="inverted_cdf"` donne exactement la définition ci-dessus.

```python
niveaux = [0.95, 0.99, 0.999]
print(dict(zip(niveaux, np.quantile(L, niveaux, method="inverted_cdf").round(2).tolist())))
```
<!--sortie-->
```text
{0.95: 0.92, 0.99: 2.04, 0.999: 3.87}
```
<!--sortie-->

<!--sortie-->

Le portefeuille de 100 M€ a donc perdu plus de 0,92 M€ un jour sur vingt, plus de 2,04 M€ un jour sur cent et plus de 3,87 M€ un jour sur mille. Ces trois nombres sont des **mesures** : ils dépendent de la période d'observation, du portefeuille et du niveau choisi.

> 🧭 **En pratique.** Le niveau de confiance est une convention d'usage et non une loi de la nature : les cadres prudentiels retiennent des niveaux élevés (99 %, 99,9 %) parce qu'ils visent la survie, alors que la gestion interne utilise souvent 95 % pour suivre le risque courant. Plus le niveau est élevé, **moins il y a d'observations pour l'estimer** : à 99,9 % sur 4 000 jours, il n'y en a que quatre (section 3.1.9).

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : exercice 3.1.

### 3.1.3 La VaR normale en forme close

Si l'on suppose que la perte suit une loi normale $\mathcal N(\mu,\sigma^2)$, la VaR s'écrit sans simulation.

> 📐 **Démonstration.** $P(L\le x)=\Phi\!\left(\dfrac{x-\mu}{\sigma}\right)$, où $\Phi$ est la fonction de répartition de la loi normale centrée réduite. Elle est supérieure ou égale à $\alpha$ si et seulement si $\dfrac{x-\mu}{\sigma}\ge z_\alpha:=\Phi^{-1}(\alpha)$. La plus petite valeur de $x$ est donc
> $$\boxed{\mathrm{VaR}_\alpha=\mu+\sigma\,z_\alpha}.$$
> Les quantiles utiles sont $z_{95\%}\approx1{,}645$, $z_{99\%}\approx2{,}326$ et $z_{99{,}9\%}\approx3{,}090$.

Pour un portefeuille, $\mu=\sum_iw_i\mu_i\,V$ et la variance est celle d'une combinaison linéaire : $\sigma^2=V^2\,w^\top\Sigma w$, où $\Sigma$ est la matrice de covariance des rendements. C'est la **méthode variance-covariance**, historiquement la première utilisée en salle de marché parce qu'elle ne demande qu'une matrice $n\times n$. Elle met aussi en évidence l'effet de diversification : $\sigma\le V\sum_iw_i\sigma_i$, avec égalité si et seulement si tous les actifs sont parfaitement corrélés.

Appliquons-la à notre portefeuille avec la moyenne et l'écart-type observés (-0,016 et 0,69 M€). À 95 %, on trouve 1,12 M€ (historique : 0,92), à 99 %, 1,59 M€ (historique : 2,04), à 99,9 %, 2,12 M€ (historique : 3,87).

<!--sortie-->

Le constat est net et central pour tout le chapitre : **à 95 %, la loi normale est un peu prudente, à 99 % elle sous-estime nettement la VaR historique, et à 99,9 % elle la divise presque par deux.** Une cloche de Gauss ajustée sur l'écart-type ne voit pas que notre portefeuille a des queues épaisses : l'écart-type est surtout fabriqué par les jours ordinaires, alors que la VaR à 99,9 % ne regarde que les jours exceptionnels.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : exercice 3.2, application 3.1.

### 3.1.4 La VaR historique et la VaR par simulation

La **VaR historique** n'invente aucune loi : elle prend les $N$ dernières pertes observées, les applique au portefeuille d'aujourd'hui et lit le quantile empirique, comme nous l'avons fait ci-dessus. Ses forces : aucune hypothèse de forme, les corrélations et les queues réelles sont préservées. Ses faiblesses : elle ne connaît que le passé (un type de crise jamais vu n'y figure pas) et elle dépend du **choix de la fenêtre**. Sur nos données, la VaR à 99 % calculée sur les 250 derniers jours vaut 2,04 M€, sur les 500 derniers jours 2,23 M€, sur les 1 000 derniers 1,84 M€ et sur les 4 000 jours 2,04 M€. Une fenêtre courte réagit vite mais oublie les crises ; une fenêtre longue se souvient mais réagit tard.

Elle a aussi un défaut discret, l'**effet fantôme** : lorsqu'une journée extrême quitte la fenêtre, la VaR chute d'un coup sans que le risque ait changé. Sur une fenêtre glissante de 500 jours, la VaR à 99 % a déjà varié de 0,57 M€ d'un jour à l'autre alors que le portefeuille était inchangé.

<!--sortie-->

La **VaR par simulation de Monte-Carlo** choisit un modèle, tire de nombreux scénarios de rendements conformes à ce modèle, revalorise le portefeuille dans chacun et lit le quantile. Elle a l'avantage de s'adapter à des portefeuilles non linéaires (options, produits complexes) que la matrice de covariance ne sait pas traiter. Mais son résultat n'est **jamais meilleur que le modèle** : avec une loi normale multivariée de mêmes moyennes et covariances, nos 200 000 scénarios redonnent la VaR à 99 % de la formule fermée, soit 1,59 M€ ; avec une loi de Student multivariée à 4 degrés de liberté, de même matrice de covariance, on obtient 1,81 M€. L'écart entre les deux ne vient pas de la simulation, il vient du **choix de la loi**.

<!--sortie-->

> 💡 **Intuition.** Les trois méthodes ne sont pas concurrentes mais complémentaires : la formule fermée est rapide et lisible, la méthode historique est honnête sur ce qui s'est passé, la simulation est souple. Un risk manager les compare : un écart important entre elles est une **information** (la queue n'est pas normale, ou la fenêtre est trop courte), pas une erreur à corriger.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.3.

### 3.1.5 Quand la volatilité change : EWMA et GARCH

Jusqu'ici nous avons supposé que l'écart-type était constant. Or l'observation du début de chapitre montrait le contraire : les mauvais jours viennent **par grappes**. Le graphique suivant montre la volatilité glissante sur 60 jours ; les zones grisées sont les périodes de stress du marché (que le simulateur connaît, mais que l'analyste ne voit pas).

![Volatilité glissante de la perte du portefeuille sur 60 jours (M€). Les bandes grisées sont les périodes de régime de stress ; la volatilité s'y envole puis retombe.](figures/ch03-volatilite-regimes.png)

<!--sortie-->

Le marché a traversé 8 épisodes de stress, d'une durée moyenne de 35 jours ; on remarque que la volatilité continue de monter ou de retomber lentement après un épisode, et qu'elle connaît aussi des pics en dehors de tout régime de stress : c'est la signature d'un modèle de volatilité de type GARCH, dans lequel un choc en appelle d'autres. Une VaR calibrée sur toute l'histoire est trop basse pendant ces épisodes et trop haute le reste du temps : elle mesure un risque moyen qui n'existe jamais. Deux familles de modèles suivent la volatilité du moment.

**L'EWMA** (*exponentially weighted moving average*) met à jour la variance chaque jour en pondérant davantage le passé récent :
$$\sigma_t^2=\lambda\,\sigma_{t-1}^2+(1-\lambda)\,L_{t-1}^2 ,$$
avec $\lambda=0{,}94$ pour des données journalières, valeur popularisée par la méthodologie RiskMetrics. Elle a un seul paramètre fixé par convention et une mémoire d'environ $1/(1-\lambda)\approx17$ jours.

**Le GARCH(1,1)** (volume II, section 4.4) estime ses paramètres par maximum de vraisemblance :
$$\sigma_t^2=\omega+\alpha\,L_{t-1}^2+\beta\,\sigma_{t-1}^2 .$$
Il est stationnaire si $\alpha+\beta<1$, et sa variance de long terme est $\omega/(1-\alpha-\beta)$. La somme $\alpha+\beta$, appelée **persistance**, dit combien de temps un choc de volatilité se prolonge. Ajusté sur les 2 000 premiers jours avec des innovations de Student (pour les queues épaisses), il donne le résultat suivant.

```python
from arch import arch_model
apprentissage, test = L[:2000], L[2000:]
modele = arch_model(apprentissage, mean="Zero", vol="GARCH", p=1, q=1, dist="t").fit(disp="off")
print(modele.params.round(3))
```
<!--sortie-->
```text
omega       0.012
alpha[1]    0.099
beta[1]     0.870
nu          5.054
Name: params, dtype: float64
```
<!--sortie-->

<!--sortie-->

On lit $\hat\alpha$ = 0,099 et $\hat\beta$ = 0,870, donc une persistance de 0,969 (très proche de 1 : les chocs de volatilité s'éteignent lentement) et $\hat\nu$ = 5,1 degrés de liberté (des queues bien plus épaisses que la normale ; le simulateur en utilisait 5). Pour que la comparaison soit honnête, **les paramètres sont figés sur les 2 000 premiers jours** et nous *filtrons* ensuite la volatilité sur les 2 000 jours suivants : chaque matin, le modèle ne connaît que ce qui s'est passé la veille. Trois VaR à 99 % sur un jour sont comparées : la VaR historique et la VaR normale calibrées une fois pour toutes sur les 2 000 premiers jours, et la VaR GARCH-Student qui s'ajuste chaque jour. Le tableau donne la **fréquence des dépassements** (jours où la perte excède la VaR) ; elle devrait valoir 1 %.

| Méthode | Tous les jours | Régime calme | Régime de stress |
|---|---|---|---|
| Historique (fixe) | 1,7 % | 0,6 % | 10,4 % |
| Normale (fixe) | 2,2 % | 1,0 % | 12,8 % |
| GARCH-Student (filtrée) | 1,1 % | 0,9 % | 3,3 % |

<!--sortie-->

Les deux méthodes figées dépassent trop souvent, et **presque tous les dépassements surviennent en régime de stress**, où la fréquence monte à plus de 10 % : le jour où l'on a le plus besoin de la VaR, elle est fausse d'un facteur dix. La VaR GARCH, qui s'adapte, reste bien plus proche de 1 %, sans l'atteindre en stress (3,3 % sur 211 jours de stress) : le modèle réagit après coup, il ne **prévoit** pas les basculements de régime. Un modèle de volatilité améliore beaucoup la couverture, il ne la rend pas parfaite.

> ⚠️ **Piège.** Une VaR « historique » sur une fenêtre calme est la VaR d'une époque calme. Calculer sur une période sans crise puis annoncer que « le risque est faible » est l'erreur la plus fréquente, et la plus coûteuse.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.2.

### 3.1.6 Du jour à dix jours : la règle de la racine

Les cadres prudentiels demandent souvent un horizon de plusieurs jours (la période pendant laquelle on ne peut pas dénouer ses positions). Plutôt que de réestimer, on **met à l'échelle** par la règle de la racine carrée du temps.

> 📐 **Démonstration.** Si les pertes journalières $L_1,\dots,L_h$ sont indépendantes, de même loi, de moyenne nulle et d'écart-type $\sigma$, alors $\mathrm{Var}(L_1+\dots+L_h)=h\sigma^2$, donc l'écart-type à $h$ jours est $\sigma\sqrt h$. Si de plus la loi est normale, la somme l'est aussi et $\mathrm{VaR}_\alpha^{(h)}=\sqrt h\ \mathrm{VaR}_\alpha^{(1)}$. Avec une moyenne $\mu$ non nulle, le terme de moyenne croît en $h$ et non en $\sqrt h$.

Pour dix jours, la VaR à 99 % historique journalière de 2,04 M€ donne 6,46 M€. Mesurons maintenant la VaR sur les **sommes de dix pertes consécutives sans chevauchement** (400 observations) : 6,56 M€, soit 2 % d'écart seulement. Sur nos données, **la règle fonctionne remarquablement bien**, et pour une bonne raison : les pertes d'un jour à l'autre sont sans mémoire (leur corrélation est de -0,005), ce qui est la condition centrale de la démonstration. Elle fonctionne aussi à l'intérieur de chaque régime : le rapport entre la VaR à dix jours observée et $\sqrt{10}$ fois la VaR à un jour vaut 0,93 pour les fenêtres qui débutent en régime calme et 1,09 pour celles qui débutent en stress.

Ce bon résultat ne doit pas rassurer à l'excès : il tient à notre simulation, où les rendements sont sans autocorrélation. La règle se brise dès que les pertes ont de la **mémoire** : des portefeuilles de produits peu liquides dont les valorisations sont lissées (les pertes se propagent sur plusieurs jours, la corrélation est positive et le risque à dix jours dépasse nettement $\sqrt{10}$ fois celui d'un jour), ou des marchés qui changent de régime *pendant* la fenêtre (la corrélation entre les carrés des pertes de deux jours consécutifs vaut ici 0,11 : c'est la signature des grappes de volatilité).

<!--sortie-->

> ⚠️ **Piège.** La règle de la racine est une approximation commode, pas un théorème sur vos données : elle suppose des pertes **indépendantes** (et, pour passer à la VaR, normales). Vérifiez l'autocorrélation avant de l'appliquer, et rappelez-vous que l'horizon est une **hypothèse économique** (le temps qu'il faut pour sortir d'une position) avant d'être un paramètre statistique : les cadres prudentiels retiennent d'ailleurs des horizons différents selon la liquidité des positions (valeurs à vérifier dans les textes en vigueur).

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : exercice 3.5.

### 3.1.7 L'expected shortfall

La VaR dit *à partir de quelle perte* on entre dans la queue, mais pas *combien* on y perd. L'**expected shortfall** (ES, ou *perte moyenne conditionnelle*, ou CVaR) répond à la seconde question.

> 📐 **Définition.** Pour une perte $L$ de moyenne finie,
> $$\mathrm{ES}_\alpha(L)=\frac{1}{1-\alpha}\int_\alpha^1\mathrm{VaR}_u(L)\,du ,$$
> et lorsque la loi est continue, $\mathrm{ES}_\alpha=\mathbb E\,[L\mid L\ge\mathrm{VaR}_\alpha]$ : la **perte moyenne les jours où la VaR est dépassée**.

Sur nos dix pertes fictives, à 90 %, la VaR est de 2,6 M€ et l'ES est la moyenne des pertes supérieures ou égales à elle, $(2{,}6+4{,}1)/2$, soit 3,35 M€. Sur le portefeuille réel, l'ES historique à 99 % est de 2,94 M€, contre une VaR de 2,04 M€ : le rapport ES/VaR vaut 1,44. Pour une loi normale, l'ES à 99 % n'est que 1,15 fois la VaR ; un rapport nettement supérieur révèle une **queue épaisse** : lorsque la VaR est franchie, elle l'est de loin.

> 📐 **ES d'une loi normale.** Si $L\sim\mathcal N(\mu,\sigma^2)$, alors $L=\mu+\sigma Z$ avec $Z$ normale centrée réduite et $\mathrm{VaR}_\alpha=\mu+\sigma z_\alpha$. Comme $\int_z^\infty u\,\varphi(u)\,du=\varphi(z)$ (car $\varphi'(u)=-u\varphi(u)$),
> $$\mathrm{ES}_\alpha=\mu+\sigma\,\mathbb E[Z\mid Z\ge z_\alpha]=\mu+\sigma\,\frac{\varphi(z_\alpha)}{1-\alpha}.$$
> Pour $\alpha=99\ \%$ : $\varphi(2{,}326)/0{,}01\approx2{,}665$, donc $\mathrm{ES}_{99\%}\approx\mu+2{,}665\,\sigma$, à comparer à $\mu+2{,}326\,\sigma$ pour la VaR.

Avec les paramètres observés, l'ES normale à 99 % vaut 1,82 M€, très en deçà de l'ES historique (2,94 M€) : comme la VaR, elle est trompée par la queue. Notons qu'une propriété utile relie les deux mesures : pour une loi normale, l'ES à **97,5 %** vaut $\mu+2{,}338\,\sigma$, presque la VaR à 99 % ($\mu+2{,}326\,\sigma$). C'est l'une des raisons pour lesquelles certains cadres prudentiels de marché ont remplacé la VaR à 99 % par l'ES à 97,5 % (niveau à vérifier dans les textes en vigueur) : sur des données normales cela ne change presque rien, sur des queues épaisses l'ES prend en compte ce que la VaR ignore.

<!--sortie-->

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : exercice 3.3.

### 3.1.8 Cohérence : pourquoi la VaR ne diversifie pas toujours

Artzner, Delbaen, Eber et Heath ont proposé en 1999 quatre propriétés qu'une mesure de risque $\rho$ « raisonnable » devrait avoir, et appelé **cohérentes** les mesures qui les vérifient toutes : la **monotonie** (une position qui perd toujours plus a un risque plus grand), l'**invariance par translation** (ajouter de la trésorerie réduit le risque d'autant), l'**homogénéité positive** (doubler la position double le risque) et la **sous-additivité**, $\rho(L_1+L_2)\le\rho(L_1)+\rho(L_2)$ : *fusionner deux portefeuilles ne crée pas de risque*, c'est la traduction mathématique de la diversification. L'ES vérifie les quatre. La VaR vérifie les trois premières mais **pas la sous-additivité** en général.

Un contre-exemple à la main suffit. Deux prêts indépendants de 1 M€ chacun ont une probabilité de défaut de 4 % et une perte de 1 M€ en cas de défaut (perte nulle sinon). On travaille au niveau de 95 %.

- **Chaque prêt seul.** La perte vaut 1 avec la probabilité 0,04 et 0 avec la probabilité 0,96. Comme $P(L\le0)=0{,}96\ge0{,}95$, on a $\mathrm{VaR}_{95\%}=0$. La somme des deux VaR est donc **0**.
- **Les deux prêts ensemble.** La probabilité qu'aucun ne fasse défaut est $0{,}96^2=0{,}9216<0{,}95$. La perte totale vaut donc 1 ou plus avec une probabilité de $1-0{,}9216=7{,}84\ \%>5\ \%$ : $\mathrm{VaR}_{95\%}=1$ M€.

La VaR du portefeuille (1) **dépasse** la somme des VaR (0) : selon la VaR, regrouper deux prêts *augmente* le risque, ce qui contredit toute intuition de diversification. Avec l'ES à 95 % : pour un prêt seul, $\mathrm{VaR}_u=0$ pour $u\le0{,}96$ et 1 au-delà, donc $\mathrm{ES}=(0{,}04\times1)/0{,}05$, soit 0,80 M€ pour chaque prêt, soit 1,60 M€ pour les deux. Pour les deux ensemble, $P(L=0)=0{,}9216$, $P(L=1)=0{,}0768$, $P(L=2)=0{,}0016$ : l'ES vaut $[(0{,}9984-0{,}95)\times1+(1-0{,}9984)\times2]/0{,}05$, soit 1,032 M€, **inférieure** à 1,60 : l'ES respecte la diversification.

<!--sortie-->

> ⚠️ **Piège.** La VaR est parfaitement acceptable pour des pertes de loi normale (elle est alors sous-additive), et c'est précisément ce qui la rend dangereuse : le contre-exemple ne se produit que quand les pertes sont **discontinues et concentrées**, comme dans le crédit, où l'on perd tout ou rien. Dans un portefeuille de prêts, la VaR peut décourager la diversification ; l'ES, non.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : exercice 3.4.

### 3.1.9 Combien vaut un chiffre de queue ?

Une VaR à 99 % sur 4 000 jours repose sur les **40 plus mauvais jours** ; à 99,9 %, sur **quatre**. Avant de discuter la méthode, demandons-nous à quel point le chiffre est *stable*. Le **bootstrap** réestime la VaR sur de nombreux échantillons tirés avec remise parmi les 4 000 pertes, et le quantile de ces estimations donne un intervalle de confiance. (Il suppose des pertes indépendantes, ce qui est faux ici à cause des grappes de volatilité : l'intervalle est donc *optimiste*.)

| Mesure | Estimation | Intervalle à 95 % | Largeur relative |
|---|---|---|---|
| VaR 99 % | 2,04 M€ | [1,74 ; 2,38] | 31 % |
| ES 99 % | 2,94 M€ | [2,57 ; 3,33] | 26 % |
| VaR 99,9 % | 3,87 M€ | [3,36 ; 4,84] | 38 % |

<!--sortie-->

Même avec cet intervalle optimiste, la VaR à 99 % n'est connue qu'à ±15 % près, et la VaR à 99,9 % à ±19 % : en valeur absolue, l'intervalle est 2,3 fois plus large au niveau de 99,9 %. L'ES à 99 % est ici un peu plus stable que la VaR au même niveau, parce qu'elle moyenne les 40 plus mauvais jours au lieu de lire un seul rang, mais elle reste sensible aux quelques plus grosses pertes de l'échantillon. **Un chiffre de queue donné sans intervalle est un chiffre dont on ignore la précision.** Les techniques de la théorie des valeurs extrêmes (volume II, section 6.5) ajustent une loi à la queue pour extrapoler au-delà des données, au prix d'hypothèses supplémentaires ; nous les retrouverons en 3.3 pour les pertes opérationnelles.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.4.

<!--sortie-->

> ✅ **À retenir.**
> - La **VaR** de niveau $\alpha$ est le quantile $\alpha$ de la perte ; elle se lit avec son niveau, son horizon et sa convention de signe, et ne dit rien de ce qui se passe au-delà.
> - La **VaR normale** $\mu+\sigma z_\alpha$ est rapide mais sous-estime les queues épaisses ; la VaR **historique** est honnête mais dépend de la fenêtre ; la simulation n'est jamais meilleure que son modèle.
> - Une volatilité qui change (EWMA, GARCH) améliore beaucoup la couverture, surtout en stress, sans prévoir les basculements.
> - La règle de la racine carrée suppose des pertes indépendantes et normales ; elle sous-estime ici le risque à dix jours.
> - L'**ES** est la perte moyenne au-delà de la VaR ; elle est **cohérente** (sous-additive), alors que la VaR ne l'est pas en général.
> - Un chiffre de queue sans intervalle est un chiffre dont on ignore la précision.


## 3.2 Stress tests et scénarios

La section précédente mesurait le risque **à partir de la distribution observée** des pertes. Un stress test pose une autre question : *que se passe-t-il si… ?* Si le chômage monte de deux points, si les taux gagnent deux points, si les marchés se comportent comme pendant le pire épisode connu. Un stress test ne donne **aucune probabilité** : il décrit une situation plausible mais sévère et en chiffre les conséquences. La VaR répond « quelle est la perte d'un mauvais jour ordinaire ? », le stress test répond « quelle serait la perte d'un jour qui ne l'est pas ? ».

### 3.2.1 Pourquoi stresser, quand on a une VaR ?

Trois raisons, toutes déjà entrevues. Premièrement, la VaR historique **ne connaît que ce qui s'est produit** : un événement absent de la fenêtre n'existe pas pour elle. Deuxièmement, la VaR est un chiffre de quantile : elle ne mesure rien au-delà, alors que la survie d'un établissement se joue justement au-delà. Troisièmement, les relations estimées en période calme (volatilités, corrélations) **changent** en période de crise, comme le montre le graphique de volatilité de la section précédente. Les superviseurs et les directions des risques demandent donc les deux : une mesure statistique pour le suivi courant, des scénarios pour la résistance aux chocs.

Un bon scénario obéit à quatre critères : il est **plausible** (on peut raconter comment il arriverait), **sévère** (il fait mal), **cohérent** (ses variables bougent ensemble de façon réaliste : un krach actions sans effet sur le crédit est suspect), et **pertinent** pour le portefeuille testé (un choc sur une matière première que l'on ne détient pas ne dit rien).

### 3.2.2 Les sensibilités : un choc, un facteur

La forme la plus simple de stress est l'**analyse de sensibilité** : on fait varier **un seul** facteur de risque et l'on mesure la perte. Pour notre portefeuille de 100 M€, la perte pour une baisse de 10 % de chaque actif pris isolément est proportionnelle à son poids : 3,5 M€ pour les actions A, 1,5 M€ pour les actions B, 3 M€ pour les obligations, 1 M€ pour l'immobilier et 1 M€ pour les matières premières. Le résultat se lit en une seconde, ce qui fait son intérêt, mais il est **incohérent** : dans la réalité, les actifs ne bougent pas un par un.

Un scénario *hypothétique* construit à la main fait bouger tous les facteurs ensemble. Prenons un « krach actions » : actions A −30 %, actions B −35 %, immobilier coté −20 %, matières premières −25 %, et des obligations qui **montent** de 3 % (fuite vers la qualité). La perte est la somme pondérée des chocs :

| Actif | Montant | Choc | Perte (M€) |
|---|---|---|---|
| Actions A | 35 M€ | −30 % | 10,50 |
| Actions B | 15 M€ | −35 % | 5,25 |
| Obligations | 30 M€ | +3 % | −0,90 |
| Immobilier coté | 10 M€ | −20 % | 2,00 |
| Matières premières | 10 M€ | −25 % | 2,50 |
| **Total** | **100 M€** | | **19,35** |

La perte totale est de 19,35 M€, soit 19,4 % du portefeuille : environ 9 fois la VaR historique à 99 % d'un jour (2,04 M€). Ce rapport n'a rien d'alarmant ou de rassurant en soi : il rappelle que la VaR et le scénario ne mesurent pas la même chose, l'une un jour ordinaire sévère, l'autre une crise.

<!--sortie-->

### 3.2.3 Les scénarios historiques

Un **scénario historique** rejoue un épisode réel sur le portefeuille actuel. Il a l'immense avantage de la cohérence (les chocs se sont réellement produits ensemble) et de la crédibilité (« cela est arrivé »). Dans nos données, l'épisode le pire est la fenêtre de **dix jours consécutifs** dont la perte cumulée est la plus forte : 17,8 M€, atteinte en fenêtre terminée le 30/06/2020. À titre de comparaison, la VaR à 99 % sur dix jours obtenue par la règle de la racine (section 3.1.6) est de 6,46 M€ : le pire épisode observé coûte **2,8 fois** plus. Rien d'anormal : cet épisode se situe en régime de stress, que la VaR calibrée sur toute l'histoire dilue.

<!--sortie-->

Un scénario historique a deux limites. Il suppose que le **portefeuille d'aujourd'hui** réagit comme celui d'hier (alors que sa composition a changé), et il est **prisonnier du passé** : la prochaine crise ne ressemblera pas à la précédente. D'où la complémentarité avec les scénarios hypothétiques, qui explorent des situations jamais observées.

### 3.2.4 Des variables macroéconomiques aux défauts de crédit

Pour la banque, le stress test le plus important relie l'**économie** aux **défauts** de son portefeuille de crédits. La démarche standard comporte trois étapes : estimer un modèle statistique entre les variables macroéconomiques et le taux de défaut, construire des trajectoires macroéconomiques (de base, adverse, sévère), puis en déduire des pertes.

Nos données donnent 80 trimestres de croissance du PIB, de chômage, de variation des prix de l'immobilier et de taux de défaut annualisé du portefeuille, avec une récession entre les trimestres 48 et 54. Un taux de défaut est une proportion, comprise entre 0 et 1 : on modélise donc sa **transformation logit**, $\ln\dfrac{p}{1-p}$, par une régression linéaire des trois variables (comme pour la régression logistique, volume II, section 2.2). Un appel suffit.

```python
import statsmodels.api as sm
t = pd.read_csv("donnees/taux_defaut_macro.csv")
y = np.log(t["taux_defaut"] / (1 - t["taux_defaut"]))
X = sm.add_constant(t[["croissance_pib", "chomage", "variation_immo"]])
macro = sm.OLS(y, X).fit()
print(macro.params.round(3).to_dict(), round(macro.rsquared, 3))
```
<!--sortie-->
```text
{'const': -5.03, 'croissance_pib': -0.401, 'chomage': 0.245, 'variation_immo': -0.063} 0.989
```
<!--sortie-->

<!--sortie-->

Chaque point de croissance en plus **multiplie** les chances de défaut par 0,67 (donc les réduit), chaque point de chômage en plus les multiplie par 1,28, et le modèle explique 0,989 de la variance du logit. L'ajustement est spectaculaire, trop pour être honnête : il tient à ce que les données sont simulées avec une relation de ce type. Il faut donc lui faire passer l'épreuve que la réalité imposerait : **a-t-il prévu la crise avant de la voir ?** Réestimons le modèle sur les seuls 44 premiers trimestres (calmes) et comparons sa prédiction au taux réellement observé pendant la récession.

![Taux de défaut observé (courbe pleine) et prédit par le modèle estimé sur les 44 premiers trimestres seulement (tirets). La zone grisée est la récession.](figures/ch03-modele-macro.png)

<!--sortie-->

Le modèle appris **avant** la crise en annonce un sommet de 12,0 % contre 12,8 % observé, avec une erreur quadratique moyenne de 0,23 point sur les 36 trimestres suivants. C'est un très bon résultat, et il faut l'interpréter avec méfiance : dans nos données la relation macro-défaut est **stable** par construction. Dans la réalité, trois obstacles se dressent : l'échantillon est court (quelques dizaines de trimestres, une ou deux récessions), les variables macroéconomiques sont corrélées entre elles (les coefficients individuels sont instables), et surtout la relation **change** quand le comportement des emprunteurs ou la politique d'octroi change. Un modèle qui a bien « prédit » une crise passée n'a pas démontré qu'il prédira la suivante.

> ⚠️ **Piège.** Un excellent $R^2$ sur 80 points et trois variables explicatives d'allure économique n'est pas une preuve de causalité ni de stabilité. Les modèles de stress test sont fréquemment estimés sur très peu de crises : on teste leur **robustesse** (changer la période, retirer une variable) plus qu'on ne célèbre leur ajustement.

### 3.2.5 Du scénario aux pertes de crédit

Reste à définir les scénarios et à traduire les taux de défaut en pertes. Nous prenons un portefeuille de crédits de **500 M€** d'encours (EAD) et une perte en cas de défaut (LGD) égale à la moyenne des pertes observées sur nos défauts passés, soit 45,9 % (fichier `recouvrements.csv`, chapitre 1). La perte annuelle attendue est le taux de défaut moyen de l'année multiplié par l'encours et par la LGD. Trois trajectoires de quatre trimestres sont comparées : le **scénario de base** prolonge la moyenne des quatre derniers trimestres (croissance de 1,3 %, chômage de 8,2 %) ; le **scénario adverse** reproduit une récession comparable à la pire observée (croissance de −1,5 %, chômage montant à 9,5 %, immobilier −3 % par trimestre) ; le **scénario sévère** va au-delà de tout ce que nos 80 trimestres ont connu (croissance de −3 %, chômage à 11 %, immobilier −6 %).

| Scénario | Croissance | Chômage (fin) | Immobilier | Taux de défaut moyen | Perte annuelle | En % de l'encours |
|---|---|---|---|---|---|---|
| Base | 1,3 % | 8,2 % | -0,2 % | 2,8 % | 6,5 M€ | 1,3 % |
| Adverse | −1,5 % | 9,5 % | −3,0 % | 11,7 % | 26,8 M€ | 5,4 % |
| Sévère | −3,0 % | 11,0 % | −6,0 % | 27,0 % | 61,8 M€ | 12,4 % |

<!--sortie-->

La perte annuelle passe de 6,5 M€ en base à 26,8 M€ en scénario adverse (un facteur 4,1) puis à 61,8 M€ en sévère. Deux remarques s'imposent. D'abord, la **non-linéarité** : une récession de l'ampleur de la pire observée multiplie la perte par 4,1, parce que le logit transforme une somme de petits effets en une explosion du taux. Ensuite, le scénario sévère aboutit à un taux de défaut de 27,0 %, plus du double du maximum jamais observé dans l'échantillon (12,8 %) : le modèle **extrapole** loin de ses données, et son résultat n'a plus la même fiabilité que celui du scénario adverse. Un chiffre de stress est d'autant moins sûr qu'il est extrême, ce que les superviseurs savent et c'est pourquoi les résultats sont toujours présentés avec leurs hypothèses.

Enfin, la perte de crédit n'est qu'une partie du tableau. Un vrai stress test fait aussi varier les **marges d'intérêt**, les **valeurs de garantie** (donc la LGD, qui augmente quand l'immobilier baisse), les **provisions** et le **coût du risque**, puis consolide le tout dans une évolution du **ratio de fonds propres** (chapitre 4). Retenons le principe : on enchaîne *scénario macro → variables de risque → pertes → capital*.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.5, exercice 3.6.

### 3.2.6 Le choc de taux d'intérêt

Une banque et surtout une mutuelle d'assurance détiennent beaucoup d'obligations : leur valeur dépend de la courbe des taux. Une obligation de coupon $c$, de nominal 100 et de maturité $T$ a pour prix $P=\sum_{t=1}^{T}\dfrac{\text{flux}_t}{(1+y_t)^t}$, où $y_t$ est le taux d'actualisation de l'échéance $t$ lu sur la courbe. Quand les taux montent, le prix baisse, d'autant plus que la maturité est longue.

> 📐 **Duration et convexité.** Par un développement de Taylor du prix en fonction d'un déplacement parallèle $\Delta y$ de la courbe, $\dfrac{\Delta P}{P}\approx-D\,\Delta y+\dfrac12\,C\,(\Delta y)^2$, où $D=-\dfrac{1}{P}\dfrac{dP}{dy}$ est la **duration modifiée** et $C=\dfrac1P\dfrac{d^2P}{dy^2}$ la **convexité**. La duration est la sensibilité de premier ordre ; la convexité corrige la courbure (le prix baisse moins que ne le prévoit la droite quand les taux montent, et monte plus quand ils baissent).

Prenons trois obligations (2 ans à 2 %, 5 ans à 3 %, 10 ans à 3,5 %) actualisées sur la courbe du dernier mois de nos données, et chiffrons l'effet d'un choc parallèle de +100, +200 et +300 points de base (pb) sur l'obligation à 10 ans, dont la duration est de 8,5 et la convexité de 86.

| Choc | Prix exact | Duration seule | Duration + convexité |
|---|---|---|---|
| +100 pb | -8,1 % | -8,5 % | -8,0 % |
| +200 pb | -15,3 % | -16,9 % | -15,2 % |
| +300 pb | -21,9 % | -25,4 % | -21,5 % |

La duration seule surestime la baisse (elle ne voit pas que la courbe du prix se redresse) et l'erreur grossit avec le choc ; l'ajout de la convexité ramène l'écart à 0,4 point sur +300 pb. Pour un choc de faible amplitude, l'approximation est excellente ; pour un stress, on **réévalue intégralement** le portefeuille (c'est ce que fait la colonne « prix exact »).

![Variation du prix de l'obligation à 10 ans selon le choc parallèle de taux : réévaluation exacte (trait plein), approximation par la duration (tirets) et par duration et convexité (pointillés).](figures/ch03-taux-duration.png)

<!--sortie-->

Un choc parallèle est trop simple : les courbes réelles **se déforment** (pentification, aplatissement). Un scénario *historique de taux* applique à la courbe actuelle la déformation observée entre deux dates. Entre les mois 60 et 90 de nos données (le cycle de hausse), les taux ont monté de 120 pb à 3 mois, de 127 pb à 1 an et jusqu'à 177 pb à 30 ans. Appliquée à trois obligations de 10 M€ chacune, cette déformation coûte 2,19 M€ (soit 7,3 % du portefeuille obligataire), contre 1,44 M€ pour un choc parallèle de +100 pb : la forme du choc compte autant que son ampleur.

<!--sortie-->

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.6, exercice 3.7.

### 3.2.7 Le stress test inversé

Un stress test classique part d'un scénario et calcule la perte. Le **stress test inversé** (*reverse stress test*) fait le chemin contraire : il part d'un **résultat inacceptable** (le capital est épuisé, le ratio passe sous le seuil) et cherche *quel scénario y conduit*, puis demande s'il est plausible. L'exercice est salutaire parce qu'il oblige à regarder les vulnérabilités que les scénarios « raisonnables » n'effleurent pas.

Supposons que les fonds propres disponibles pour absorber les pertes de crédit s'élèvent à **25 M€** (5 % de l'encours). Paramétrons une famille de scénarios qui va continûment du scénario de base ($s=0$) au scénario sévère ($s=1$), et cherchons l'intensité $s$ pour laquelle la perte annuelle atteint 25 M€. On trouve $s=$ 56 % de la distance entre base et sévère, ce qui correspond à une croissance de -1,1 % et à un chômage de 9,8 % en fin d'année. Ce scénario est **moins sévère que la récession déjà observée** dans l'échantillon (croissance minimale de -1,6 %, chômage maximal de 10,2 %) : le coussin de 25 M€ ne résisterait pas à une récession plus douce que celle que le portefeuille a déjà connue. C'est une conclusion que ni la VaR ni un scénario « raisonnable » n'auraient fait apparaître.

<!--sortie-->

Le raisonnement inversé est précieux justement parce qu'il évite le piège du scénario « confortable » : il ne dit pas si la banque est solide, il dit **ce qu'il faudrait pour qu'elle ne le soit plus**, et laisse la direction juger si c'est crédible.

### 3.2.8 Quand les corrélations montent

Dernier point, essentiel : la diversification **disparaît quand on en a le plus besoin**. Le graphique compare les corrélations estimées sur les jours calmes et sur les jours de stress de nos données.

![Corrélations des rendements journaliers entre actifs, estimées sur les jours calmes (à gauche) et sur les jours de stress (à droite). Les actions, l'immobilier et les matières premières se resserrent ; les obligations restent presque indépendantes.](figures/ch03-correlations-regimes.png)

<!--sortie-->

La corrélation entre les actions A et les actions B passe de 0,57 à 0,89, celle entre les actions A et l'immobilier de 0,43 à 0,87, alors que celle avec les obligations reste proche de zéro (-0,08 puis 0,01). Mesurons l'effet de diversification par le rapport entre l'écart-type du portefeuille et la somme des écarts-types pondérés des actifs (1 = aucune diversification, 0 = diversification totale) : il vaut 0,70 en jours calmes, mais 0,83 en jours de stress. **La diversification a perdu une part importante de son effet au moment où elle devait servir.** La VaR normale à 99 % vaut 1,33 M€ avec les caractéristiques des jours calmes, 3,63 M€ avec celles des jours de stress : le seul changement de régime multiplie le risque par 2,7.

<!--sortie-->

C'est la raison pour laquelle les scénarios de stress **n'utilisent pas les corrélations moyennes** : ils appliquent des corrélations de crise (souvent proches de 1 pour les actifs risqués), ou, comme dans notre scénario « krach » de 3.2.2, des chocs simultanés.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : exercice 3.8 (pour le stress inversé).

### 3.2.9 Gouvernance et limites des stress tests

Un stress test n'est utile que si l'on en tire une décision. Trois précautions résument la pratique. **Gouvernance** : les scénarios sont proposés par la fonction de gestion des risques, **discutés** par la direction, **révisés** régulièrement, et les résultats sont reliés à des **actions** (réduire une exposition, relever le capital, préparer un plan de financement). **Limites** : un scénario est une histoire parmi d'autres ; il y a un risque de se concentrer sur la crise passée (le « dernier conflit »), d'ignorer les effets de second tour (une vente forcée fait baisser les prix, qui déclenche d'autres ventes), et de croire à la précision des chiffres (voir le modèle macro, qui extrapole). **Complémentarité** : le stress test ne remplace pas la VaR, il la complète. La VaR dit comment le risque courant se répartit, le stress dit où l'on casse.

> ✅ **À retenir.**
> - Un stress test répond à « et si ? » ; il ne donne **aucune probabilité**, mais une perte conditionnelle à un scénario plausible et sévère.
> - On distingue sensibilités (un facteur), scénarios historiques (cohérents, mais prisonniers du passé) et scénarios hypothétiques (construits, plus libres).
> - Un scénario macroéconomique relie l'économie aux défauts par un modèle statistique : *macro → taux de défaut → perte → capital*. Les relations extrapolées au-delà des données sont moins fiables.
> - Un choc de taux se chiffre par duration et convexité pour les petits chocs, par réévaluation complète pour les grands ; la **forme** du choc compte.
> - Le stress test **inversé** part d'un résultat inacceptable et cherche le scénario qui y mène.
> - Les corrélations montent en crise : la diversification mesurée en période calme est un mirage au moment où l'on en a besoin.


## 3.3 ➕ Pour aller plus loin : risques opérationnel, de marché et de liquidité

> 🧭 **Section optionnelle.** Les sections 3.1 et 3.2 suffisent pour la suite du volume. Celle-ci applique les mêmes idées à trois autres familles de risques : les **incidents opérationnels** (où les queues épaisses dominent tout), les **contributions au risque** d'un portefeuille de marché, et la **liquidité** (où l'on ne manque pas de valeur, mais de temps).

### 3.3.1 Le risque opérationnel et la distribution des pertes

Le **risque opérationnel** est le risque de perte résultant de processus, de personnes ou de systèmes inadéquats ou défaillants, ou d'événements extérieurs : une fraude, une erreur de traitement, une panne informatique, une pratique commerciale défaillante. Les cadres prudentiels le répartissent classiquement en sept catégories d'événements ; notre jeu de données en retient cinq. Il se distingue des risques de marché et de crédit par un trait : on ne le **prend** pas pour gagner un rendement. On le subit.

La méthode de référence pour le chiffrer est l'**approche par distribution des pertes** (*loss distribution approach*, LDA). La perte annuelle est la somme d'un nombre aléatoire d'incidents, chacun de montant aléatoire :
$$S=\sum_{i=1}^{N}X_i ,\qquad N\sim\text{Poisson}(\lambda),\quad X_i\ \text{indépendantes, de même loi}.$$
On modélise donc séparément la **fréquence** $N$ et la **sévérité** $X$, comme en assurance (chapitre 2), puis on combine les deux par simulation. On en tire la **perte attendue** $\mathbb E[S]$ et la **perte inattendue** $\mathrm{VaR}_\alpha(S)-\mathbb E[S]$, celle que le capital est censé couvrir.

### 3.3.2 Ajuster la fréquence et la sévérité

Notre fichier contient 1802 incidents sur dix ans. Leur nombre annuel va de 158 à 214, avec une moyenne de 180,2. Pour une loi de Poisson, la variance égale la moyenne ; ici le rapport variance/moyenne vaut 2,4. L'écart vient surtout d'une **tendance** : le nombre d'incidents croît de 3,1 % par an en moyenne. On garde dans la suite une fréquence constante de 180,2 incidents par an pour ne pas surcharger l'exemple, en sachant qu'une estimation sérieuse la ferait croître.

La **sévérité** est le vrai sujet. La perte nette médiane est de 2 358 €, la moyenne de 14 238 € : la moyenne vaut plusieurs fois la médiane, signe d'une queue lourde. Le plus gros incident a coûté 1,8 M€. Un seul modèle ne s'ajuste pas bien à l'ensemble : on coupe en deux. Le **corps** (pertes inférieures à 100 000 €) est ajusté par une loi log-normale. La **queue** (les 53 incidents au-delà de 100 000 €, soit 2,9 % des cas) est ajustée par une **loi de Pareto généralisée** (GPD), que la théorie des valeurs extrêmes (volume II, section 6.5) désigne comme la loi limite des excès au-dessus d'un seuil élevé. Son paramètre $\xi$ décide de tout : il mesure l'épaisseur de la queue. Si $\xi<1$ la perte moyenne est finie ; si $\xi\ge1$, la moyenne **n'existe pas** (infinie), et plus on collecte de données, plus la moyenne observée grossit.

```python
from scipy import stats
net = pd.read_csv("donnees/pertes_operationnelles.csv")["perte_nette"].values
exces = net[net > 100000] - 100000
xi, _, echelle = stats.genpareto.fit(exces, floc=0)
print(len(exces), round(xi, 2), round(echelle))
```
<!--sortie-->
```text
53 0.99 57811
```
<!--sortie-->

<!--sortie-->

On lit $\hat\xi$ = 0,99 pour une échelle de 58 k€, avec seulement 53 observations. Un $\hat\xi$ proche de 1 signifie une queue extrêmement lourde ; mais **53 points ne permettent pas de trancher** : nous mesurerons plus bas l'incertitude de cette estimation. Notons aussi une subtilité de méthode : les pertes **nettes** (après récupérations, assurances) sont 5,7 % plus faibles que les pertes **brutes** (annuel : 2,57 M€ nets contre 2,72 M€ bruts). Selon les approches, on modélise les pertes brutes ou nettes ; la différence reflète ce que l'assurance et les recours couvrent, qui n'est jamais garanti à l'avance.

### 3.3.3 La perte agrégée et l'instabilité du 99,9 %

On simule 20 000 années : pour chacune, on tire le nombre d'incidents (loi de Poisson de moyenne 180,2) puis la perte de chaque incident dans le modèle ajusté (corps log-normal tronqué, queue GPD), et l'on somme. Voici ce que donne la même simulation avec trois graines différentes.

| Graine | Perte annuelle moyenne | VaR 99 % | VaR 99,9 % |
|---|---|---|---|
| 1 | 10,6 M€ | 32 M€ | 264 M€ |
| 2 | 4,8 M€ | 29 M€ | 206 M€ |
| 3 | 6,6 M€ | 33 M€ | 365 M€ |
| *Observé sur dix ans* | *2,57 M€* | *max annuel 6,7 M€* | |

Trois enseignements, du plus anodin au plus grave. **La VaR à 99 %** est assez stable d'une graine à l'autre (29 à 33 M€) mais reste très supérieure au pire exercice observé en dix ans (6,7 M€) : un modèle ajusté sur dix ans ne peut pas être contredit par dix ans de données au niveau 99 %. **La perte moyenne simulée** est de l'ordre de 5 à 11 M€ selon la graine, contre 2,57 M€ observés : avec $\hat\xi$ proche de 1, la moyenne est instable parce qu'une seule perte colossale fait basculer l'année. **La VaR à 99,9 %** varie de 206 à 365 M€ selon la graine : un facteur 1,8 entre la plus petite et la plus grande, sans que rien n'ait changé que le générateur aléatoire. Ce n'est pas un défaut de la simulation (on a déjà 20 000 années) : c'est la signature d'une queue à variance infinie.

Reste l'incertitude sur le **paramètre** lui-même. Rééchantillonnons les 1802 incidents avec remise, ré-ajustons la GPD et recalculons la VaR à 99,9 % (100 rééchantillons, 5 000 années simulées chacun). Le paramètre $\hat\xi$ varie de 0,49 à 1,55 (intervalle à 95 %) et dépasse 1 dans 31 % des cas ; la VaR à 99,9 % médiane vaut 179 M€, et sa borne basse 10 M€. **La borne haute n'a aucun sens économique** (plusieurs milliards d'euros) : quand $\hat\xi$ dépasse 1, le modèle prédit des pertes qu'aucune institution ne subirait sans disparaître.

![À gauche : probabilité qu'un incident dépasse un montant (échelles logarithmiques), observée (points) et ajustée par la GPD au-delà de 100 000 € (trait). À droite : VaR à 99,9 % (échelle logarithmique) pour 100 rééchantillonnages des données ; le trait vertical marque le pire exercice annuel observé en dix ans.](figures/ch03-operationnel.png)

<!--sortie-->

> ⚠️ **Piège.** Une VaR à 99,9 % calculée sur dix ans de données opérationnelles est une extrapolation à *mille* ans. Elle exige une queue modélisée, un seuil choisi, un paramètre estimé sur quelques dizaines de points : chacun de ces choix peut multiplier le résultat par dix. Les praticiens bornent donc les pertes (une perte maximale plausible par événement), combinent les données internes avec des données externes et des **scénarios d'experts**, et présentent le chiffre avec sa plage d'incertitude. Avec un plafond de 50 M€ par incident, la VaR à 99,9 % du même modèle tombe à 55 M€ : le plafond *est* l'hypothèse qui décide.

<!--sortie-->

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.7, exercice 3.10.

### 3.3.4 Risque de marché : sensibilités et contributions

Le risque de marché est celui que nous avons traité en 3.1 et 3.2 : la perte vient de la variation des prix des actifs, des taux, des changes. Deux outils complètent la VaR pour la gestion.

La **sensibilité** à un facteur est la perte pour une variation donnée de ce facteur (1 point de base de taux, 1 % d'un indice). Pour une position linéaire, c'est le produit du montant par la variation ; pour une option, il faut les « grecques » (*delta*, *gamma*, *vega*), qui sortent du cadre de ce volume.

La **période de détention** est le temps nécessaire pour dénouer ou couvrir une position ; elle fixe l'horizon de la mesure (section 3.1.6). Les actifs peu liquides (immobilier non coté, obligations d'émetteurs peu actifs) ont une période plus longue, donc un risque plus élevé *à mesure équivalente*.

La **contribution au risque** répond à la question « qui, dans mon portefeuille, fabrique le risque ? ». La réponse n'est pas le poids : l'écart-type du portefeuille $\sigma_p=\sqrt{w^\top\Sigma w}$ est une fonction homogène de degré 1 des poids, donc, par le théorème d'Euler,
$$\sigma_p=\sum_i w_i\,\frac{\partial\sigma_p}{\partial w_i},\qquad \frac{\partial\sigma_p}{\partial w_i}=\frac{(\Sigma w)_i}{\sigma_p},$$
et la **contribution** de l'actif $i$ est $w_i(\Sigma w)_i/\sigma_p$, dont la somme sur les actifs redonne $\sigma_p$. La part de chaque actif dans le risque total est alors son poids multiplié par sa covariance avec le portefeuille, divisé par la variance du portefeuille.

| Actif | Poids | Part du risque (jours calmes) | Part du risque (jours de stress) |
|---|---|---|---|
| Actions A | 35 % | 57,2 % | 51,8 % |
| Actions B | 15 % | 25,7 % | 25,6 % |
| Obligations | 30 % | 0,5 % | 1,0 % |
| Immobilier coté | 10 % | 7,5 % | 8,6 % |
| Matières premières | 10 % | 9,0 % | 12,9 % |

Les obligations pèsent 30 % du portefeuille et ne contribuent presque pas au risque (0,5 % en jours calmes) : elles sont peu volatiles et peu corrélées au reste. À l'inverse, les actions A (35 % du capital) fournissent plus de la moitié du risque. En régime de stress, la part des matières premières passe de 9,0 % à 12,9 %, parce que leur corrélation avec les actions augmente : **la structure du risque, pas seulement son niveau, dépend du régime**. Un gestionnaire qui réduit une position pour « réduire le risque » doit regarder sa contribution, pas son poids.

<!--sortie-->

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : exercice 3.9.

### 3.3.5 Risque de liquidité : le coussin et le temps

Le **risque de liquidité** est le risque de ne pas pouvoir honorer ses engagements à temps, même en étant solvable. Une banque finance des crédits à long terme avec des dépôts à vue : la **transformation d'échéances** est son métier et sa fragilité. On distingue le risque de **liquidité de financement** (les prêteurs ne renouvellent plus) et de **liquidité de marché** (on ne peut vendre un actif qu'avec une forte décote).

Un exemple chiffré. Une banque fictive a le bilan suivant (en M€) : à l'actif, 60 de réserves auprès de la banque centrale, 90 de titres publics, 700 de crédits, 50 d'autres actifs ; au passif, 540 de dépôts de particuliers, 220 de financements de marché à court terme, 80 de dettes longues, 60 de fonds propres. Un **ratio de liquidité simplifié** compare le coussin d'actifs liquides aux sorties de trésorerie sur trente jours dans un scénario de stress : $\text{ratio}=\dfrac{\text{actifs liquides de haute qualité}}{\text{sorties nettes à 30 jours}}$. (Les ratios réglementaires existent sous cette forme avec des taux de retrait et des décotes fixés par les textes ; les valeurs ci-dessous sont **illustratives**.)

- **Coussin** : 60 de réserves plus 90 de titres publics avec une décote de 10 % en cas de vente, soit 141 M€.
- **Scénario modéré** : 8 % des dépôts de particuliers et 40 % des financements de marché partent. Les sorties valent $540\times8\,\%+220\times40\,\%=131,2$ M€, le ratio 107 % : le coussin couvre tout juste.
- **Scénario sévère** : 15 % et 70 %. Les sorties atteignent 235 M€ et le ratio tombe à 60 % : il faudrait vendre des crédits (invendables en trente jours) ou s'adresser à la banque centrale.

Le raisonnement inversé s'applique encore : si une même fraction $f$ de tous les financements instables ($540+220=760$ M€) s'enfuyait, le coussin serait épuisé pour $f=141/760=18,6$ %. Ce chiffre dit **à quelle vitesse la confiance peut disparaître** avant que la banque ne puisse plus payer : une banque parfaitement solvable peut ainsi faire faillite par manque de liquidité, ce que la VaR de marché ne voit pas.

<!--sortie-->

> ✅ **À retenir.**
> - Le risque **opérationnel** se chiffre par fréquence × sévérité (LDA) ; sa queue est lourde, et un paramètre $\xi$ proche ou supérieur à 1 rend la moyenne et les quantiles extrêmes **instables**.
> - Un quantile à 99,9 % sur dix ans de données est une extrapolation : on le borne, on le complète par des scénarios d'experts, et on le publie avec sa plage d'incertitude.
> - La **contribution** d'un actif au risque (Euler) n'est pas son poids ; elle change avec le régime.
> - Une banque solvable peut manquer de **liquidité** : on compare un coussin à des sorties de stress, et l'on cherche le taux de retrait qui l'épuise.


## 3.4 ➕ Pour aller plus loin : backtesting et validation des modèles

> 🧭 **Section optionnelle.** Un modèle de risque est une promesse (« la perte dépassera ce montant un jour sur cent ») que l'on peut **vérifier** : chaque jour la réalité répond. Cette section apprend à lire la réponse avec les tests de Kupiec et de Christoffersen, à en voir les limites, puis à situer le backtest dans la démarche plus large de **validation** d'un modèle.

### 3.4.1 Le principe du backtest

Un **backtest** compare, jour après jour, la VaR prévue à la perte réalisée. À la date $t$, on connaît la prévision $\mathrm{VaR}_t$ (calculée avec l'information de la veille) et l'on observe la perte $L_t$. Le **dépassement** (*exception* ou *violation*) est l'indicateur $I_t=\mathbf 1\{L_t>\mathrm{VaR}_t\}$. Si le modèle est bon au niveau $\alpha$, la suite des $I_t$ doit avoir deux propriétés :

1. **La couverture inconditionnelle** : la probabilité d'un dépassement est $p=1-\alpha$ (1 % pour une VaR à 99 %). Sur $n$ jours, le nombre de dépassements suit une loi binomiale de paramètres $n$ et $p$.
2. **L'indépendance** : un dépassement aujourd'hui ne rend pas un dépassement demain plus probable. Des dépassements **groupés** signalent un modèle qui réagit trop lentement aux changements de régime : même si leur nombre total est correct, ils tombent justement les jours où il aurait fallu être prudent.

Les deux tests qui suivent vérifient chacune de ces propriétés. L'ensemble est la **couverture conditionnelle**.

> 💡 **Intuition.** Ce n'est pas un test sur l'ampleur des pertes mais sur la **fréquence et la répartition des surprises**. Une VaR peut passer parfaitement le backtest et être inutile : celle qui annonce toujours une perte immense dépasse rarement, mais coûte du capital pour rien. Le backtest mesure l'honnêteté, pas l'utilité.

### 3.4.2 Le test de Kupiec

Si $x$ est le nombre de dépassements sur $n$ jours, l'estimation naturelle de la probabilité de dépassement est $\hat\pi=x/n$. Le **test du rapport de vraisemblance de Kupiec** (test de la proportion de dépassements, POF) compare la vraisemblance binomiale sous l'hypothèse $\pi=p$ à celle obtenue avec $\hat\pi$.

> 📐 **Statistique de Kupiec.** La vraisemblance d'une série de $n$ épreuves de Bernoulli contenant $x$ succès est $\pi^x(1-\pi)^{n-x}$. La statistique
> $$\mathrm{LR}_{\mathrm{POF}}=-2\ln\frac{(1-p)^{\,n-x}\,p^{\,x}}{(1-x/n)^{\,n-x}\,(x/n)^{\,x}}$$
> suit asymptotiquement, sous l'hypothèse nulle, une loi du $\chi^2$ à **un** degré de liberté ; on rejette au seuil de 5 % si elle dépasse 3,84.

Exemple à la main : pour $n=250$ jours, un niveau de 99 % ($p=0{,}01$) et $x=6$ dépassements (alors que 2,5 sont attendus), la statistique vaut 3,56, soit une probabilité critique de 0,059 : à 5 %, on ne rejette pas, de peu. Avec 7 dépassements, la statistique monterait à 5,50 et l'on rejetterait. La frontière est étroite : un jour de plus ou de moins change le verdict.

<!--sortie-->

### 3.4.3 Le test de Christoffersen

Le test d'**indépendance** de Christoffersen regarde les enchaînements : après un jour sans dépassement, quelle est la probabilité $\pi_{01}$ d'en avoir un le lendemain ? Après un jour avec dépassement, quelle est la probabilité $\pi_{11}$ d'en avoir un autre ? Sous l'indépendance, $\pi_{01}=\pi_{11}$. On compte les quatre types de transitions $n_{00},n_{01},n_{10},n_{11}$, on estime $\hat\pi_{01}=\dfrac{n_{01}}{n_{00}+n_{01}}$ et $\hat\pi_{11}=\dfrac{n_{11}}{n_{10}+n_{11}}$, et la statistique du rapport de vraisemblance suit un $\chi^2$ à un degré de liberté. Additionner les deux statistiques donne un test **conjoint** de couverture conditionnelle, de loi $\chi^2$ à deux degrés de liberté : $\mathrm{LR}_{\mathrm{CC}}=\mathrm{LR}_{\mathrm{POF}}+\mathrm{LR}_{\mathrm{IND}}$.

### 3.4.4 Le backtest de quatre méthodes

Passons à des données. À chaque jour à partir du 1 001ᵉ, quatre méthodes prévoient la VaR à 99 % du lendemain : la **historique** (fenêtre de 500 jours), la **normale** (moyenne et écart-type de la même fenêtre), l'**EWMA** ($\lambda=0{,}94$) et le **GARCH-Student** (paramètres réestimés tous les 250 jours sur les 1 000 derniers jours). Les 3 000 jours de test donnent, pour chaque méthode, le nombre de dépassements (1 % attendu, soit 30), les probabilités critiques des deux tests, la fréquence de dépassement par régime (invisible à l'analyste mais connue du simulateur) et la **perte d'étalonnage** moyenne (voir plus bas).

| Méthode | Dépassements | Fréquence | Kupiec (p) | Christoffersen (p) | Fréquence en calme | Fréquence en stress | Perte d'étalonnage |
|---|---|---|---|---|---|---|---|
| Historique (500 j) | 44 | 1,47 % | 0,016 | 0,029 | 0,7 % | 9,8 % | 3,25 |
| Normale (500 j) | 62 | 2,07 % | < 0,001 | 0,184 | 1,1 % | 12,1 % | 3,20 |
| EWMA | 56 | 1,87 % | < 0,001 | 0,144 | 1,6 % | 4,5 % | 2,59 |
| GARCH-Student | 36 | 1,20 % | 0,286 | 0,350 | 1,0 % | 3,8 % | 2,50 |

![Perte quotidienne du portefeuille (points gris), VaR à 99 % de la méthode historique (orange) et du GARCH-Student (bleu), avec les dépassements de chaque méthode marqués (croix) sur les 3 000 jours de test. Les bandes grisées sont les périodes de stress.](figures/ch03-backtest.png)

La lecture est instructive. La méthode **normale** et l'**EWMA** dépassent nettement trop souvent (62 et 56 dépassements pour 30 attendus) : le test de Kupiec les rejette sans hésitation. La méthode **historique** est plus proche mais encore rejetée (44 dépassements, probabilité critique de Kupiec 0,016) et elle dépasse presque 15 fois plus souvent en stress qu'en calme. Le **GARCH-Student** est la seule des quatre dont la fréquence globale (1,20 %) est compatible avec 1 % au sens du test (probabilité critique de 0,286), et c'est aussi celle dont la perte d'étalonnage est la plus faible. Mais regardons la colonne du stress : même le meilleur modèle dépasse **3,8 %** du temps en régime de stress (au lieu de 1 %). Les dépassements du GARCH se concentrent dans les basculements : le modèle suit la volatilité, il ne **prévoit** pas qu'elle va changer.

Quant à l'indépendance, aucune méthode n'est rejetée au seuil de 1 % ; la méthode historique l'est à 5 % (probabilité critique de 0,029) : ses dépassements arrivent en grappes, comme on pouvait s'y attendre d'une fenêtre qui oublie lentement la volatilité récente.

<!--sortie-->

> ⚠️ **Piège.** « Le modèle a passé le backtest » ne veut pas dire « le modèle est juste ». Cela veut dire « sur cette période, avec ce niveau, on n'a pas pu prouver qu'il avait tort ». La section suivante montre à quel point un test à 250 jours est myope.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.8, exercice 3.11.

### 3.4.5 Un test qui voit mal : la puissance

Un test statistique a un **niveau** (la probabilité de rejeter à tort un bon modèle) et une **puissance** (la probabilité de rejeter un mauvais modèle). Calculons-la exactement pour le test de Kupiec, en sommant la loi binomiale sur les nombres de dépassements qui conduisent au rejet. Supposons un modèle dont la vraie fréquence de dépassement serait de 2 % au lieu de 1 %, c'est-à-dire une VaR qui **sous-estime d'un facteur deux** la probabilité de la queue.

| Taille de l'échantillon | Puissance pour une vraie fréquence de 1,5 % | Puissance pour 2 % |
|---|---|---|
| 250 jours (un an) | 11 % | 24 % |
| 1 000 jours | 34 % | 78 % |
| 3 000 jours | 69 % | 99 % |

Sur un an, un modèle dont la fréquence réelle de dépassement est le **double** de celle annoncée n'est détecté que 24 fois sur 100. Même après trois ans de données, une fréquence de 1,5 % n'est repérée qu'environ 69 fois sur 100. **Un backtest de 250 jours ne distingue presque rien** : c'est la raison pour laquelle les cadres prudentiels se contentent de seuils larges (le « feu tricolore » ci-dessous) et pourquoi un modèle ne se valide pas sur le seul backtest.

<!--sortie-->

### 3.4.6 Le feu tricolore

Plutôt que de tester, on peut **classer**. La zone dans laquelle tombe le nombre de dépassements sur 250 jours pour une VaR à 99 % se détermine par la loi binomiale $B(250;\,0{,}01)$ : on est en zone **verte** tant que la probabilité cumulée du nombre observé reste inférieure à 95 %, en zone **orange** (ou jaune) jusqu'à 99,99 %, en zone **rouge** au-delà. En calculant ces probabilités on retrouve les seuils usuels, 4 dépassements au plus pour le vert, 5 à 9 pour l'orange, 10 et plus pour le rouge.

| Dépassements sur 250 jours | 0 | 2 | 4 | 5 | 7 | 9 | 10 |
|---|---|---|---|---|---|---|---|
| Probabilité cumulée | 8,11 | 54,32 | 89,22 | 95,88 | 99,60 | 99,97 | 99,99 |
| Zone | verte | verte | verte | orange | orange | orange | rouge |

Dans le cadre réglementaire de marché de la fin des années 1990, la zone orange ou rouge entraîne une majoration du facteur multiplicatif appliqué à la VaR pour déterminer le capital (de quelques dixièmes à un point entier, valeurs **à vérifier dans les textes en vigueur**). Sur les 250 derniers jours de notre échantillon, la VaR historique a connu 2 dépassements et la VaR GARCH 4 : toutes deux en zone verte, alors que la VaR historique a été rejetée par le test de Kupiec sur les 3 000 jours. **Sur la fenêtre d'un an, rien ne distingue le bon modèle du mauvais.**

<!--sortie-->

### 3.4.7 Backtester l'expected shortfall

Un backtest de VaR ne regarde que la **fréquence** des dépassements ; il ignore leur **ampleur**. Or l'ES a pour rôle de dire de combien on dépasse. Contrôler une ES est plus difficile que contrôler une VaR : il y a peu de dépassements (30 attendus sur 3 000 jours), et la grandeur à comparer est une moyenne conditionnelle. Plusieurs tests existent (le principe est dû, entre autres, à Acerbi et Székely) ; nous nous contentons ici d'un **contrôle de bon sens** : sur les jours où la VaR est dépassée, comparer la perte **moyenne réalisée** à l'ES **moyenne prévue** ces jours-là.

| Méthode | ES prévue les jours de dépassement (M€) | Perte moyenne réalisée (M€) | Écart |
|---|---|---|---|
| Historique | 2,22 | 2,49 | 11 % |
| Normale | 1,69 | 2,24 | 25 % |
| EWMA | 1,48 | 1,88 | 21 % |
| GARCH-Student | 2,11 | 2,27 | 7 % |

Toutes les méthodes **sous-estiment** la perte moyenne des jours difficiles, mais pas de la même façon : la normale et l'EWMA sont loin de la réalité (par construction, une queue normale ne voit pas les pertes extrêmes), le GARCH-Student s'en approche de 7 %. Ce contrôle est approximatif (le nombre de dépassements diffère d'une méthode à l'autre, et un petit nombre de très grosses pertes domine la moyenne), mais il illustre l'idée essentielle : **on peut valider la fréquence tout en ignorant l'ampleur**.

<!--sortie-->

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : exercice 3.12.

### 3.4.8 La validation d'un modèle

Le backtest n'est qu'une pièce de la **validation**, c'est-à-dire de l'évaluation indépendante d'un modèle avant et pendant son usage. Les institutions la confient à une équipe **distincte** de celle qui l'a construit, pour la même raison qu'on ne corrige pas sa propre copie. Les cinq questions classiques structurent l'examen.

| Question | Ce que l'on vérifie | Exemple dans ce chapitre |
|---|---|---|
| **Le concept est-il solide ?** | Les hypothèses sont-elles défendables, la théorie adaptée à l'usage ? | La normalité est-elle raisonnable pour un portefeuille dont le kurtosis vaut 20,3 ? |
| **Les données sont-elles fiables ?** | Qualité, représentativité, période d'estimation | Une fenêtre calme sous-estime la VaR ; un seul épisode de stress dans l'échantillon |
| **L'implémentation est-elle correcte ?** | Le code fait-il ce que la documentation annonce ? On réexécute indépendamment. | Convention de signe, définition du quantile (rang $\lceil\alpha n\rceil$), unité (M€) |
| **Les résultats tiennent-ils ?** | Backtest, comparaison à un modèle concurrent (*challenger*), analyse de sensibilité | Le tableau de 3.4.4, la puissance de 3.4.5 |
| **L'usage est-il encadré ?** | Domaine de validité, limites, plan de surveillance, revue périodique | Les chiffres au-delà de 99 % sont des extrapolations (3.1.9, 3.3.3) |

Une validation conclut par un **niveau de confiance** et des **limitations** ou des **conditions d'usage** (un coefficient de prudence, une revue plus fréquente, l'interdiction de l'utiliser pour tel produit), jamais par un simple « validé » ou « rejeté ».

### 3.4.9 Le risque de modèle

Tout modèle simplifie, donc se trompe. Le **risque de modèle** est le risque de pertes ou de mauvaises décisions dues à l'utilisation d'un modèle erroné ou mal utilisé. Ce chapitre en a offert quatre visages. **La spécification** : avec les mêmes données, les quatre méthodes donnent des VaR à 99 % moyennes qui diffèrent de 30 % entre la plus basse et la plus haute. **L'estimation** : un chiffre de queue vient avec un intervalle de confiance large (3.1.9), et un paramètre comme $\xi$ peut faire basculer la conclusion (3.3.3). **L'implémentation** : un signe inversé, une unité confondue, une fenêtre mal alignée donnent un chiffre faux mais plausible. **L'usage** : un modèle de défaut estimé sur des périodes calmes utilisé pour un scénario sévère (3.2.4).

On ne supprime pas le risque de modèle, on le **gère** : par un **inventaire** de tous les modèles avec leur propriétaire, leur finalité et leur niveau d'importance ; par une validation plus approfondie pour les modèles à fort enjeu ; par des modèles **concurrents** (si deux modèles raisonnables divergent, l'écart est une mesure du risque de modèle) ; par des **marges de prudence** explicites ; et par une documentation qui permet à un tiers de refaire le calcul. La première défense contre le risque de modèle reste la lucidité : **un chiffre de risque est toujours conditionnel à un modèle**.

> ✅ **À retenir.**
> - Le backtest de VaR vérifie deux propriétés des dépassements : leur **fréquence** (Kupiec) et leur **indépendance** (Christoffersen).
> - Sur nos données, seul le GARCH-Student passe les deux tests ; même lui échoue en stress (dépasse trop souvent dans les basculements).
> - La **puissance** des tests est faible : un an de données ne distingue pas 1 % de 2 % ; le feu tricolore classe, il ne prouve pas.
> - Le backtest de l'ES est plus délicat que celui de la VaR ; un contrôle élémentaire montre que toutes les méthodes sous-estiment les pertes extrêmes.
> - La **validation** est une démarche indépendante en cinq questions (concept, données, implémentation, résultats, usage) ; le **risque de modèle** se gère par inventaire, modèles concurrents, marges de prudence et documentation.


## Bilan du chapitre 3

Vous savez maintenant :

- **définir** une perte de portefeuille, une **VaR** (quantile de niveau $\alpha$, avec son horizon et sa convention de signe) et une **expected shortfall** (perte moyenne au-delà de la VaR), les **calculer** par la loi normale ($\mu+\sigma z_\alpha$, démontrée), par l'histoire, par simulation et avec une volatilité qui change (EWMA, GARCH) ;
- **démontrer** que la VaR n'est pas sous-additive (deux prêts à 4 % de probabilité de défaut) alors que l'ES l'est, et **mesurer l'incertitude** d'un chiffre de queue par bootstrap ;
- **mettre à l'échelle** un horizon par la règle de la racine carrée en connaissant ses conditions (pertes indépendantes) ;
- **concevoir** un stress test : sensibilités, scénarios historiques et hypothétiques, scénario macroéconomique relié aux défauts par un modèle logit, choc de taux (duration, convexité, réévaluation complète), stress **inversé**, et **expliquer** pourquoi les corrélations montent en crise ;
- (en option) **chiffrer** un risque opérationnel par fréquence × sévérité, reconnaître l'instabilité d'un quantile à 99,9 %, **allouer** le risque d'un portefeuille (contributions d'Euler), et lire un **coussin de liquidité** ;
- (en option) **backtester** une VaR (Kupiec, Christoffersen, feu tricolore), connaître la faible puissance de ces tests, contrôler grossièrement une ES, et situer le backtest dans la **validation** et le **risque de modèle**.

Le tableau suivant résume **ce que nous avons mesuré** sur les données simulées de ce chapitre, portefeuille de 100 M€ :

| Question | Résultat | Ce qu'il faut en retenir |
|---|---|---|
| VaR à 99 % sur un jour | historique 2,04 M€ ; normale 1,59 M€ ; ES historique 2,94 M€ | la loi normale sous-estime la queue ; l'ES est 1,44 fois la VaR |
| Fréquence de dépassement en stress (méthodes figées) | historique 10,4 %, normale 12,8 % | le jour où l'on a besoin de la VaR, elle est fausse d'un facteur dix |
| Diversification | corrélation actions A–B 0,57 (calme) puis 0,89 (stress) | elle s'érode quand on en a le plus besoin |
| Scénario macro adverse | perte de crédit de 26,8 M€ contre 6,5 M€ en base | un facteur 4,1 pour une récession déjà observée |
| Stress inversé | coussin de 25 M€ épuisé par une croissance de -1,1 % | moins sévère que la pire récession de l'échantillon |
| Opérationnel (➕) | VaR à 99,9 % de 206 à 365 M€ selon la graine | une queue à $\xi$ proche de 1 rend l'extrême instable |
| Backtest (➕) | seul le GARCH-Student passe Kupiec (36 dépassements pour 30 attendus) | encore 3,8 % de dépassements en stress |

Le fil conducteur du chapitre tient en une phrase : **un nombre de risque est une réponse conditionnelle**, à un niveau, à un horizon, à une méthode, à une période d'estimation, et il vient avec une incertitude qu'il faut lui rattacher. La VaR décrit les jours ordinaires, le stress test les jours qui ne le sont pas, le backtest vérifie que le modèle tient, la validation demande si l'on peut s'y fier ; **aucune de ces quatre démarches ne suffit seule**.

> 🧭 **En pratique : liste de questions devant tout chiffre de risque.**
> 1. À quel niveau, sur quel horizon, avec quelle convention de signe ?
> 2. Calculé comment (loi, fenêtre, volatilité) et sur quelle période : calme ou crise incluse ?
> 3. Avec quelle incertitude (intervalle, plage entre deux méthodes) ?
> 4. Qu'en dit un scénario de stress, y compris inversé ?
> 5. Le backtest a-t-il assez de puissance pour dire que c'est bon ?
> 6. Qui a validé le modèle, avec quelles limites d'usage ?

> ⚠️ **Rappel d'honnêteté.** Les données de ce chapitre sont **simulées** : le simulateur connaît le régime de marché, la relation macro-défaut et les lois des pertes, ce qui nous a permis de juger les méthodes ; en réalité on ne dispose jamais de cette vérité. Le modèle macro de 3.2 est stable par construction, les seuils réglementaires cités (zones du feu tricolore, niveau de l'ES) sont à vérifier dans les textes en vigueur, et rien ici n'est un conseil financier ou réglementaire.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.1 à 3.8 (VaR et ES sur le portefeuille, EWMA et GARCH filtré, simulation et loi de Student, incertitude par bootstrap, stress macro, choc de taux, perte opérationnelle agrégée, backtest complet) et exercices 3.1 à 3.12.

Le chapitre 4 change de point de vue : ces mesures de risque ne sont plus seulement des outils de gestion, elles sont **imposées** par des cadres réglementaires (Bâle pour les banques, Solvabilité pour les assureurs). Nous verrons comment ces textes transforment une PD, une LGD ou une VaR en **exigence de capital**, et ce que valent ces conventions.


---

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


---

# Chapitre 5 : ➕ Assurance vie

> « Assurer une vie, c'est mettre un prix sur une date que personne ne connaît, en comptant sur ce que l'on sait de toutes les autres. »

> 🧭 **Chapitre complémentaire.** Ce chapitre est facultatif : le reste du volume ne le suppose pas. Il montre comment les outils des chapitres précédents (modèle de comptage de Poisson, vraisemblance, validation hors période, quantiles d'une distribution simulée) servent un autre métier de l'actuariat : celui où l'on promet de payer **dans vingt, quarante ou soixante ans**. Il se lit mieux après le chapitre 2 (fréquence, sévérité, tarification) et le chapitre 3 (mesures de risque).

En assurance dommages (chapitre 2), un contrat dure un an et l'on peut se corriger chaque année : si la sinistralité monte, on augmente le tarif à l'échéance. En assurance **vie**, la promesse est de long terme : une rente versée jusqu'au décès, un capital garanti à un âge lointain, une prime fixée **aujourd'hui** pour des décennies. Le prix d'un tel contrat repose donc sur trois ingrédients : **une table de mortalité** (quelle est la probabilité de décéder à chaque âge ?), **un taux d'actualisation** (que vaut aujourd'hui un euro payé dans trente ans ?) et **une projection** (la mortalité de demain ressemblera-t-elle à celle d'aujourd'hui ?). Ce chapitre suit exactement cet ordre.

## Le chemin de ce chapitre

- **5.1 Tables de mortalité.** On passe des décès et des expositions observés aux taux, puis aux probabilités de décès, puis à la table ($\ell_x$, $d_x$, $e_x$). On compare table de période et table de génération, on lisse par la loi de Gompertz–Makeham, et l'on mesure par un **rapport réel/attendu** si les assurés meurent moins que la population.
- **5.2 Mathématiques actuarielles de la vie.** On actualise : capital décès $A_x$, rente viagère $\ddot a_x$, la relation $A_x = 1 - d\,\ddot a_x$, les primes nivelées par le principe d'équivalence, les provisions mathématiques, et la sensibilité au taux technique et à la table.
- **5.3 Le modèle de Lee–Carter.** On modélise la **tendance** : $\ln m_{x,t} = a_x + b_x k_t$. On l'ajuste par décomposition en valeurs singulières, on projette l'indice $k_t$, on **compare à la vérité programmée**, et l'on quantifie le **risque de longévité** d'un portefeuille de rentes.

Le fil conducteur est celui du volume : **chiffrer un risque, puis prouver que le chiffre tient**. Ici, la réponse a une particularité heureuse : les données sont simulées à partir d'un modèle connu, de sorte que l'on peut comparer chaque estimation à la vérité, ce que la réalité ne permet jamais.

## Les données du chapitre

> 📦 **Données.** Deux jeux, tous deux **simulés** (graines fixes ; générateur `build/donnees5.py`).
> - `mortalite_population.csv` : les décès et les expositions au risque d'une **population fictive**, par sexe (F, M), âge (0 à 99 ans) et année (1980 à 2019), soit 8 000 lignes. La mortalité y suit **exactement** un modèle de Lee–Carter (section 5.3), avec une vérité connue : `mortalite_verite.csv` ($a_x$, $b_x$) et `mortalite_kt_vrai.csv` ($k_t$).
> - `portefeuille_vie.csv` : 20 000 contrats d'une mutuelle fictive (temporaire 10 ou 20 ans, vie entière), observés de 2015 à 2019, avec pour chacun l'âge à l'émission, le capital, l'exposition observée et l'indicateur de décès. La mortalité des assurés a été programmée à **75 % de celle de la population**.
>
> Aucune donnée n'est réelle : les ordres de grandeur sont plausibles, mais l'espérance de vie à la naissance (environ 74 ans pour les femmes de cette population fictive) n'est pas celle d'un pays donné.


Un coup d'œil aux premières lignes du jeu de population suffit à fixer le vocabulaire : une ligne par année, âge et sexe, avec l'**exposition** (le nombre d'années-personnes vécues dans la cellule) et les **décès** observés.

```python
print(pop[(pop["annee"] == 2019) & (pop["sexe"] == "F")].iloc[[0, 30, 60, 90]].to_string(index=False))
```
<!--sortie-->
```text
 annee  age sexe  exposition  deces        m
  2019    0    F     98750.0    332 0.003362
  2019   30    F     51759.3     37 0.000715
  2019   60    F     25642.5    340 0.013259
  2019   90    F     14196.2   4154 0.292614
```

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.8 (tables de période, lissage et graduation, rapport réel/attendu, valeurs actuarielles, provisions, Lee–Carter, risque de longévité, validation hors période) et exercices 5.1 à 5.12.


## 5.1 Tables de mortalité

Cette section construit l'objet central de l'assurance vie : la **table de mortalité**. On part de ce que l'on observe (des décès et des années-personnes vécues), on en tire des taux, des probabilités, puis une table ; on se demande si la table d'une année décrit bien l'avenir de ceux qui la vivent ; on la lisse par une loi paramétrique ; enfin on vérifie si les assurés d'un portefeuille meurent moins que la population générale.


### 5.1.1 Du décès observé au taux de mortalité

Prenons la cellule « femmes de 60 ans en 2019 » du jeu de population. Elle contient une **exposition** de 25 642 années-personnes (chaque personne de 60 ans présente toute l'année compte pour 1 ; une personne qui entre ou sort en cours d'année compte pour la fraction vécue) et 340 décès. Le **taux central de mortalité** est le rapport

$$
m_{x} = \frac{D_x}{E_x} = \frac{ 340 }{ 25642 } \approx 0{,}01326 .
$$

C'est un **taux par année-personne**, pas une probabilité : il se lit « environ 1,33 décès par an pour 100 personnes de 60 ans ».

> 📐 **Pourquoi ce rapport est le bon estimateur.** Si les décès d'une cellule suivent une loi de Poisson, $D_x \sim \text{Poisson}(E_x\, m_x)$ (hypothèse : chaque année-personne est exposée à une force de mortalité constante $m_x$ et les décès sont indépendants), la log-vraisemblance est $\ell(m) = D\ln m - E\,m + \text{cte}$. Sa dérivée $D/m - E$ s'annule en $\hat m = D/E$, et la dérivée seconde $-D/m^2$ donne la variance $\widehat{\text{Var}}(\hat m)= \hat m/E$. L'erreur relative est donc $1/\sqrt{D}$ : avec 340 décès, environ 5,4 %. **C'est le nombre de décès, pas le nombre d'habitants, qui fixe la précision.**

Le taux central n'est pas encore la **probabilité de décéder dans l'année**, $q_x$, que l'on attend d'une table. Si la force de mortalité est constante sur l'année, la survie sur l'année est $e^{-m_x}$ et

$$
q_x = 1 - e^{-m_x}.
$$

Une autre convention répandue suppose les décès répartis uniformément dans l'année, ce qui donne $q_x = m_x/(1+m_x/2)$. Pour les âges courants, les deux formules sont indiscernables (à 60 ans, $q_{60}\approx0{,}01317$) ; elles ne divergent que là où $m$ est grand : pour $m=0{,}3$, la première donne 0{,}2592 et la seconde 0{,}2609. Le jeu de ce chapitre a été simulé avec la première, que nous adoptons.

> 🧪 **Ce que la vérité programmée dit ici.** Le taux vrai de cette cellule est 0,01253, contre 0,01326 observé : l'écart est de l'ordre de l'erreur attendue (5,4 %). Il reste, de cellule en cellule, un bruit de Poisson que les tables lissent et que les petits portefeuilles subissent de plein fouet (section 5.1.5).

La figure suivante montre les taux de mortalité par âge, en 1980 et en 2019, pour les deux sexes. Sur une échelle logarithmique, la partie adulte est presque **une droite** : c'est la loi de Gompertz (section 5.1.4). La bosse du jeune âge et le niveau plus élevé des hommes sont des traits du jeu simulé, inspirés des tables réelles sans les copier.


![Taux de mortalité par âge (échelle logarithmique), femmes en bleu et hommes en orange, en 1980 (tirets) et en 2019 (trait plein). Données simulées.](figures/ch05-taux-mortalite.png)

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.1, exercices 5.1 et 5.2.

### 5.1.2 La table de mortalité

Une **table de mortalité** suit une cohorte fictive de $\ell_0 = 100\,000$ naissances (la *racine*, ou *radix*) en lui appliquant les probabilités de décès $q_x$ âge après âge :

$$
\ell_{x+1} = \ell_x\,(1-q_x), \qquad d_x = \ell_x\,q_x = \ell_x-\ell_{x+1}.
$$

$\ell_x$ est le nombre de survivants à l'âge exact $x$, $d_x$ le nombre de décès entre $x$ et $x+1$. On en tire les **années vécues** dans l'intervalle, $L_x \approx (\ell_x+\ell_{x+1})/2$, et l'**espérance de vie** à l'âge $x$ :

$$
e_x = \frac{\sum_{k\ge x} L_k}{\ell_x}.
$$

Un exemple à la main avec des probabilités arrondies, $q_{60}=0{,}013$, $q_{61}=0{,}014$, $q_{62}=0{,}015$, $q_{63}=0{,}016$ :

| Âge $x$ | $q_x$ | $\ell_x$ | $d_x = \ell_x q_x$ |
|---|---|---|---|
| 60 | 0,013 | 100 000,0 | 1 300,0 |
| 61 | 0,014 | 98 700,0 | 1 381,8 |
| 62 | 0,015 | 97 318,2 | 1 459,8 |
| 63 | 0,016 | 95 858,4 | 1 533,7 |
| 64 | | 94 324,7 | |

On lit par exemple qu'une cohorte de 100 000 personnes de 60 ans en compte encore 94 325 à 64 ans, soit une probabilité de survie de 4 ans $_4p_{60} = 0{,}013$ → $0{,}987 \times 0{,}986 \times 0{,}985 \times 0{,}984 = 0{,}94325$. La probabilité de survie sur plusieurs années est **le produit** des probabilités annuelles de survie.

Avec les 8 000 cellules du jeu, on construit la table des femmes de 2019 en trois étapes : taux, probabilités, table. Au-delà de 99 ans la table est **prolongée jusqu'à 120 ans** par une loi paramétrique (section 5.1.4), et le dernier $q$ vaut 1 : sans cette fermeture, la table s'arrêterait en laissant des survivants sans destin.

```python
q = prolonge(q_depuis_m(M["F"][2019].to_numpy()), P_GM)   # probabilités de décès, fermées à 120 ans
table = table_vie(q)                                       # l_x, d_x, L_x, e_x
print(table.loc[[0, 30, 60, 65, 90], ["age", "q", "l", "e"]].round({"q": 4, "l": 0, "e": 2}).to_string(index=False))
```
<!--sortie-->
```text
 age      q        l     e
   0 0.0034 100000.0 74.39
  30 0.0007  98438.0 45.37
  60 0.0132  88055.0 18.22
  65 0.0209  81580.0 14.45
  90 0.2537   6897.0  2.81
```

L'espérance de vie à la naissance de cette population fictive est de 74,39 ans pour les femmes de 2019 (71,54 pour les hommes) et l'espérance de vie à 65 ans de 14,45 ans (12,68 pour les hommes). Parmi 100 000 naissances féminines, 81 580 atteignent 65 ans.

> 🧪 **Comparaison à la vérité.** La table construite à partir des taux **vrais** donne 74,37 ans à la naissance et 14,50 ans à 65 ans, soit des écarts de l'ordre de 0,02 an et 0,05 an : à cette échelle (des centaines de milliers de personnes par âge), le bruit de Poisson est négligeable. C'est ce qui changera pour un portefeuille d'assurés (section 5.1.5).

> ⚠️ **L'espérance de vie à la naissance est une moyenne de toutes les mortalités.** Elle dépend beaucoup de la mortalité infantile et n'indique rien sur la durée d'un contrat conclu à 40 ans. Pour l'assurance vie, les quantités utiles sont les $q_x$ et les $e_x$ aux âges de souscription, pas $e_0$.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.1, exercices 5.1 et 5.2.

### 5.1.3 Table de période ou table de génération ?

La table précédente est une **table de période** : elle combine les taux observés **la même année** à tous les âges. C'est une photographie de 2019. Elle ne décrit pas la vie d'une personne réelle, qui vieillit pendant que les taux changent : une personne de 60 ans en 2019 aura 70 ans en 2029 et affrontera alors la mortalité de 2029 à 70 ans, qui sera probablement plus basse que celle que la table de 2019 lui prête.

Une **table de génération** suit au contraire une cohorte de naissance $g$ le long de la diagonale : $q_x^{(g)}$ est la probabilité de décès à l'âge $x$ pendant l'année $g+x$. Quand la mortalité baisse, la table de génération est plus favorable que la table de période de l'année de naissance.

Le jeu de données permet une expérience propre : la cohorte née en 1920 a 60 ans en 1980 et 99 ans en 2019, donc **toute sa vie de 60 à 100 ans est observée** dans la fenêtre 1980–2019. Comparons le nombre moyen d'années vécues entre 60 et 100 ans (une espérance **partielle**, tronquée à 100 ans) selon trois tables : la table de période de 1980, celle de 2019 et la cohorte de 1920.


Les résultats : 15,90 années vécues entre 60 et 100 ans avec la table de période de 1980, 16,71 avec la cohorte réelle de 1920 et 18,71 avec la table de période de 2019. La cohorte a vécu **0,81 an de plus** que la photographie de 1980 ne le promettait, parce que sa mortalité a baissé pendant qu'elle vieillissait ; et elle a vécu **2,00 ans de moins** que la photographie de 2019 ne le laisserait croire, parce qu'elle a traversé des années moins favorables. À 80 ans, 30,9 % des personnes de 60 ans survivent selon la table de 1980, 34,9 % pour la cohorte, 44,0 % selon la table de 2019.

![Courbes de survie à partir de 60 ans : table de période 1980 (orange), cohorte née en 1920 (violet, observée de 1980 à 2019) et table de période 2019 (bleu). Données simulées.](figures/ch05-survie-tables.png)

> ⚠️ **Piège de l'actuaire de rentes.** Valoriser une rente viagère avec la table de période du jour **sous-estime** sa durée dès que la mortalité baisse : la rente sera servie plus longtemps que prévu et le provisionnement sera insuffisant. C'est le **risque de longévité** (section 5.3.4). La réponse standard consiste à projeter la mortalité (une table de génération prospective) : c'est l'objet du modèle de Lee–Carter.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.1, exercices 5.1 et 5.2.

### 5.1.4 Lisser : la loi de Gompertz–Makeham

Deux raisons de lisser. La première est la **fermeture** : aux grands âges, les effectifs fondent, les taux observés sont erratiques, et il faut pourtant une table complète jusqu'à l'âge limite. La seconde est le **petit nombre** : pour un portefeuille d'assurés, les décès par âge se comptent en dizaines, et le bruit de Poisson masque la structure.

La loi de **Gompertz–Makeham** décrit la force de mortalité adulte par

$$
\mu(x) = A + B\,e^{c\,x}, \qquad A,\,B,\,c>0 .
$$

Le terme constant $A$ (Makeham) représente une mortalité indépendante de l'âge (accidents) ; le terme exponentiel (Gompertz) décrit l'**usure** : la mortalité est multipliée par la même constante $e^{c}$ à chaque année d'âge supplémentaire, et **double tous les $\ln 2/c$ ans**. Les paramètres s'ajustent par maximum de vraisemblance poissonien, en maximisant $\sum_x \left(D_x\ln m_x - E_x m_x\right)$ avec $m_x \approx \mu(x+\tfrac12)$.

```python
a = np.arange(30, 100)                                        # ajustement sur les âges adultes
p = gm_ajuste(a, D["F"][2019].loc[a].to_numpy(), E["F"][2019].loc[a].to_numpy())
A_, B_, c_ = np.exp(p)                                         # paramètres (on optimise leurs logarithmes)
print(f"A = {A_:.1e}   B = {B_:.2e}   c = {c_:.4f}   doublement tous les {np.log(2) / c_:.2f} ans")
```
<!--sortie-->
```text
A = 2.0e-15   B = 2.91e-05   c = 0.1013   doublement tous les 6.84 ans
```

Pour les femmes de 2019, la mortalité double environ tous les 6,84 ans (la valeur programmée dans le jeu est $c=0{,}1$, soit 6,93 ans). La constante de Makeham estimée est nulle à la précision de l'optimiseur : les âges de 30 à 99 ans ne laissent pas de place à un terme constant. La loi ajustée reste proche de la vérité entre 40 et 90 ans (à moins de 10 %) et s'en écarte aux extrémités : une loi à trois paramètres ne remplace pas une table entière, mais **elle prolonge raisonnablement**. C'est elle qui ferme notre table à 120 ans.

> ⚠️ **L'extrapolation est une hypothèse, pas une mesure.** Au-delà de 100 ans, aucun décès n'est observé dans la table : elle est prolongée par la loi de Gompertz–Makeham. Ici l'enjeu est faible : fermer la table à 100 ans plutôt qu'à 120 changerait l'espérance de vie à 65 ans de 0,002 an seulement, car il ne reste que 79 survivants à 100 ans sur 100 000 naissances. L'extrapolation pèserait bien davantage pour une population plus âgée, pour une mortalité aux grands âges plus basse, ou pour une rente de réversion servie au dernier survivant d'un couple.

Le lissage sert surtout pour les **portefeuilles d'assurés**. La figure suivante compare, pour les contrats observés de 2015 à 2019, les taux bruts par âge (avec leur intervalle à 95 %), la table de population multipliée par 0,75 (le niveau programmé) et une loi de Gompertz–Makeham ajustée directement sur le portefeuille. Les taux bruts sont si dispersés qu'aucun âge ne se lit seul, alors que la forme lissée raconte une histoire cohérente.


![Mortalité des assurés par âge : taux bruts avec intervalle de Poisson à 95 % (gris), table de population × 0,75 (bleu) et loi de Gompertz–Makeham ajustée au portefeuille (orange). Données simulées.](figures/ch05-portefeuille-taux.png)

Sur les 55 âges du portefeuille, la médiane est de 9 décès par âge : chaque taux brut est connu à $1/\sqrt{D}$ près, soit environ 33 % à l'âge médian. La loi ajustée sur ces seules données double tous les 6,48 ans, c'est-à-dire presque exactement comme la population ; le portefeuille se distingue par un **niveau** plus bas, non par une pente différente.

> 🧭 **Pour aller plus loin : les méthodes de graduation.** Plutôt qu'une loi paramétrique, on peut lisser par la méthode de **Whittaker–Henderson** : on cherche les taux $\hat g$ qui minimisent $\sum_x w_x(m_x-\hat g_x)^2+\lambda\sum_x(\Delta^3\hat g_x)^2$, compromis entre fidélité aux données (poids $w_x$ égaux aux expositions) et régularité (les différences troisièmes sont petites). On la pratique dans l'application 5.2 du cahier.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.2, exercice 5.3.

### 5.1.5 Les assurés meurent-ils moins que la population ? Le rapport réel/attendu

Un assureur ne tarifie pas avec la mortalité de la population générale : les assurés sont **sélectionnés** (un questionnaire médical écarte des risques aggravés), plus aisés, plus attentifs à leur santé. Le **rapport réel/attendu** (en anglais *actual over expected*, A/E) mesure cet écart :

$$
\text{A/E} = \frac{\text{décès observés}}{\text{décès attendus}} = \frac{\sum_i \delta_i}{\sum_i E_i\, m^{\text{réf}}(x_i,t_i)} ,
$$

où $\delta_i$ vaut 1 si le contrat $i$ est sorti par décès, $E_i$ est son exposition de l'année et $m^{\text{réf}}$ le taux de la **table de référence** pour son sexe, son âge et son année. Au dénominateur, on somme sur toutes les années-contrats **en vigueur** : un contrat émis en 2017 n'apporte d'exposition qu'à partir de 2017, et celui d'un assuré décédé en 2016 n'est plus compté ensuite.

Sur les 20 000 contrats du portefeuille, la reconstruction des lignes contrat-année donne 85 325 lignes, 84 909 années d'exposition et 832 décès. La table de référence est la population de la même année et du même sexe.

```python
L = lignes_police_annee(pv)                                              # une ligne par contrat-année en vigueur
L["attendu"] = L["expo"] * np.array([M[s].loc[a, t] for s, a, t in zip(L["sexe"], L["age"], L["annee"])])
ae, bas, haut = ae_ic(L["deces"].sum(), L["attendu"].sum())              # intervalle exact de Poisson à 95 %
print(f"réels {L['deces'].sum()}  attendus {L['attendu'].sum():.1f}  A/E = {ae:.3f}  [{bas:.3f} ; {haut:.3f}]")
```
<!--sortie-->
```text
réels 832  attendus 1088.2  A/E = 0.765  [0.713 ; 0.818]
```


Le rapport réel/attendu est de **0,765**, avec un intervalle à 95 % de [0,713 ; 0,818] : les assurés meurent environ **24 % de moins** que la population, et la valeur programmée (0,75) est bien dans l'intervalle. L'intervalle repose sur l'hypothèse que le nombre de décès suit une loi de Poisson dont l'espérance est $\text{A/E}_{\text{vrai}}\times$ attendu, avec l'attendu supposé connu (la table de référence n'est pas, elle aussi, estimée avec incertitude).

> 📐 **Combien de décès faut-il ?** Pour un rapport estimé à ±10 % près (demi-largeur de l'intervalle à 95 %), il faut $1{,}96/\sqrt{D}\le0{,}10$, c'est-à-dire $D \ge 384$ décès. À ±5 %, il en faut 1 537. Un portefeuille de 20 000 contrats suffit ici (832 décès), mais **pas pour comparer des sous-groupes** : l'analyse par âge ou par contrat se fait avec beaucoup moins de décès par cellule et des intervalles larges.

La même mesure, détaillée par tranche d'âge, montre que le rapport n'est pas constant :

```text
tranche d'âge  décès  attendus   A/E  borne basse  borne haute
        25–40     18      31.0 0.580        0.344        0.917
        41–50     55      77.4 0.710        0.535        0.925
        51–60    162     209.8 0.772        0.658        0.901
        61–70    375     496.2 0.756        0.681        0.836
          71+    222     273.7 0.811        0.708        0.925
```

Le tableau semble montrer un rapport qui **croît avec l'âge** (de 0,58 à 0,81) : on y retrouverait le schéma classique d'une sélection médicale qui s'estompe avec l'âge. Mais **la sélection programmée est la même à tous les âges** (un facteur 0,75 sur le taux), et les intervalles le disent : chacun contient la valeur 0,75. Les différences entre tranches sont du **bruit d'échantillonnage**, d'autant plus fort que les tranches comptent peu de décès (la première n'en compte que 18). Lire une tendance dans ce tableau serait une erreur : c'est exactement ce qui se produit quand on découpe un portefeuille trop finement.


![Rapport réel/attendu par tranche d'âge avec son intervalle de Poisson à 95 %. La ligne pointillée orange est la valeur programmée (0,75) et la ligne grise la mortalité de la population (1). Données simulées.](figures/ch05-ae-tranches.png)

Que faire d'un tel rapport ? Deux usages classiques : **tarifer avec une table de référence multipliée par un coefficient** ($q^{\text{assurés}}\approx 0{,}75\,q^{\text{pop.}}$, en pratique appliqué au taux $m$ plutôt qu'à $q$), tant que les données du portefeuille ne justifient pas une table d'expérience propre ; et **surveiller** le rapport dans le temps (une dérive vers 1 signale une sélection qui se dégrade ou une population qui change). Le prix correspondant, et sa sensibilité à la table, sont l'objet de la section 5.2.

> ⚠️ **Pièges du rapport réel/attendu.** (1) La table de référence doit correspondre au sexe, à la période et à la **définition de l'âge** (à la dernière date anniversaire, ou à l'âge le plus proche) : une définition décalée d'un demi-an change le rapport de plusieurs pour cent. (2) Un rapport global peut cacher des sous-populations très différentes (par contrat, par capital) : les capitaux élevés pèsent davantage dans le coût que dans le nombre de décès, et l'on calcule alors un A/E **pondéré par le capital**. (3) Il ne dit rien de la **cause** : sélection médicale, effet du contrat, mode de souscription.

> ✅ **À retenir (5.1).**
> - Le taux central est $m_x=D_x/E_x$ (estimateur du maximum de vraisemblance d'un modèle de Poisson) ; la probabilité de décès est $q_x=1-e^{-m_x}$ si la force est constante dans l'année ; la précision relative est $1/\sqrt{D}$.
> - Une table donne $\ell_x$, $d_x$, $L_x$, $e_x$ ; la survie sur plusieurs années est un **produit** de survies annuelles.
> - Une **table de période** est une photographie ; une **table de génération** suit une cohorte. Avec une mortalité en baisse, la première sous-estime la durée de vie des vivants : c'est le risque de longévité.
> - Gompertz–Makeham lisse et prolonge, mais l'extrapolation reste une hypothèse.
> - Le **rapport réel/attendu** mesure l'écart à une table de référence, avec un intervalle de Poisson : il faut près de 400 décès pour ±10 %.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.3, exercices 5.1 à 5.4.


## 5.2 Mathématiques actuarielles de la vie

Une table de mortalité donne des probabilités ; un contrat d'assurance vie donne des **flux d'argent** subordonnés à la vie ou au décès de l'assuré. Cette section relie les deux : on calcule ce que valent aujourd'hui un capital payé au décès et une rente versée tant que l'assuré vit, on en déduit la **prime** par le principe d'équivalence, puis la **provision** que l'assureur doit garder en cours de contrat, et l'on mesure la sensibilité de ces chiffres à deux hypothèses qui changent d'une année à l'autre : le taux d'actualisation et la table.


### 5.2.1 Actualiser : ce que vaut un euro futur

Un euro payé dans un an vaut aujourd'hui moins qu'un euro payé tout de suite, parce que l'on pourrait placer la somme. Avec un taux d'intérêt annuel $i$, la **valeur actuelle** d'un euro payé dans $n$ ans est $v^n$, où $v = 1/(1+i)$ est le **facteur d'actualisation**. On définit aussi le taux d'escompte $d = 1 - v = i\,v$ et l'intensité d'intérêt $\delta = \ln(1+i)$. Avec $i=2\,\%$, on a $v=0,980392$ et $d=0,019608$ : ce sont des **taux d'illustration**, choisis pour que les calculs soient lisibles, pas des taux de marché (le taux technique d'un vrai contrat est fixé par des règles prudentielles et par l'environnement financier).

En assurance vie, un flux est aussi **aléatoire** : on le paie seulement si l'assuré est vivant (rente) ou seulement s'il décède (capital). La **valeur actuelle actuarielle** est l'espérance de la valeur actuelle de ces flux : pour chaque flux possible, on multiplie son montant actualisé par sa probabilité.

Voici le calcul à la main le plus simple : une assurance **temporaire de 3 ans** souscrite à 60 ans, qui verse un capital de 100 000 € à la fin de l'année du décès si celui-ci a lieu dans les 3 ans, avec les probabilités arrondies $q_{60}=0{,}013$, $q_{61}=0{,}014$, $q_{62}=0{,}015$ et $i=2\,\%$. Il y a trois façons de payer : décéder à 60, à 61 ou à 62 ans. Les probabilités de ces trois événements sont $q_{60}$, $p_{60}q_{61}$ et $p_{60}p_{61}q_{62}$ (il faut survivre jusqu'à l'année de décès), et les capitaux sont versés respectivement dans 1, 2 et 3 ans :

$$
A^{1}_{60:\overline{3}|} = v\,q_{60} + v^2\,p_{60}q_{61} + v^3\,p_{60}p_{61}q_{62}
= 0{,}012745 + 0{,}013281 + 0{,}013756 = 0{,}039782 .
$$

Le capital de 100 000 € a donc une valeur actuarielle de **3 978,2 €** : c'est la **prime unique pure** de ce contrat, la somme qui, versée aujourd'hui, suffirait à payer en moyenne les sinistres. Si le client préfère payer chaque année, d'avance et tant qu'il est en vie, on calcule d'abord la valeur actuelle d'une **rente temporaire** de 1 € par an payée en début d'année tant que l'assuré vit :

$$
\ddot a_{60:\overline{3}|} = 1 + v\,p_{60} + v^2\,p_{60}p_{61} = 1 + 0{,}96765 + 0{,}93539 = 2{,}90304 .
$$

La prime annuelle $P$ doit vérifier l'**équivalence** « valeur actuelle des primes = valeur actuelle des prestations », soit $P\times 2{,}90304 = 3\,978{,}2$ et $P = 3\,978{,}2/2{,}90304 = $ **1 370,4 € par an**. Le calcul est vérifié en code caché. C'est tout le principe : le reste de la section l'applique à des horizons plus longs en remplaçant les trois probabilités à la main par la table.

> 💡 **Intuition.** Une prime est un **prix moyen**, calculé comme si l'on connaissait les probabilités. Chaque client individuel paiera plus ou moins que son coût réel ; c'est la mutualisation (loi des grands nombres) qui rend l'opération soutenable pour l'assureur. Ce que la loi des grands nombres ne résout pas, c'est l'erreur sur les probabilités elles-mêmes (section 5.3.4).

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.4, exercice 5.5.

### 5.2.2 Capital décès et rente viagère

Étendons le calcul de la section précédente à toute la vie de l'assuré. Notons ${}_kp_x$ la probabilité de survivre $k$ ans depuis l'âge $x$ ; le capital de 1 € payé à la fin de l'année du décès (**assurance vie entière**) et la rente de 1 € par an payée d'avance tant que l'assuré vit (**rente viagère**) ont pour valeurs actuarielles

$$
A_x = \sum_{k\ge 0} v^{k+1}\; {}_kp_x\, q_{x+k},
\qquad
\ddot a_x = \sum_{k\ge 0} v^{k}\; {}_kp_x .
$$

Ces sommes se calculent à rebours sur la table, puisque chaque valeur s'exprime à partir de celle de l'âge suivant :

$$
A_x = v\,q_x + v\,p_x\,A_{x+1},
\qquad
\ddot a_x = 1 + v\,p_x\,\ddot a_{x+1},
$$

avec, à l'âge de fermeture $\omega$ où $q_\omega = 1$, $A_\omega = v$ et $\ddot a_\omega = 1$ (le dernier paiement a lieu une fois, puis plus rien). La première récurrence se lit : « soit je décède cette année, et je touche (actualisé) ; soit je survis, et je repars de $A_{x+1}$ ».

> 📐 **Relation entre capital décès et rente : $A_x = 1 - d\,\ddot a_x$.** Écrivons $p_k = {}_kp_x$ pour alléger, avec $p_0=1$ et $q_{x+k}\,p_k = p_k - p_{k+1}$. Alors
> $$A_x=\sum_{k\ge0}v^{k+1}(p_k-p_{k+1}) = v\sum_{k\ge0}v^kp_k - \sum_{k\ge0}v^{k+1}p_{k+1}.$$
> Le premier terme vaut $v\,\ddot a_x$. Le second, en posant $j=k+1$, vaut $\sum_{j\ge1}v^jp_j=\ddot a_x - 1$. Donc $A_x = v\,\ddot a_x - \ddot a_x + 1 = 1-(1-v)\ddot a_x = 1 - d\,\ddot a_x$. $\square$
> L'interprétation : un capital payé au décès et une rente viagère sont les deux faces d'une même chose. Connaître l'un donne l'autre, et le calcul des primes d'un portefeuille d'assurance décès et de rentes se fait sur une seule quantité.

Appliquons à la table des femmes de 2019, fermée à 120 ans, avec $i=2\,\%$ :

```python
A, a = valeurs(qF19, I)                         # A_x et ä_x pour tous les âges, par récurrence à rebours
for x in (30, 40, 50, 60, 65):
    print(f"âge {x}:  A_x = {A[x]:.4f}   ä_x = {a[x]:.3f}   1 - d·ä_x = {1 - D_ * a[x]:.4f}")
```
<!--sortie-->
```text
âge 30:  A_x = 0.4150   ä_x = 29.833   1 - d·ä_x = 0.4150
âge 40:  A_x = 0.5001   ä_x = 25.494   1 - d·ä_x = 0.5001
âge 50:  A_x = 0.5964   ä_x = 20.586   1 - d·ä_x = 0.5964
âge 60:  A_x = 0.7001   ä_x = 15.297   1 - d·ä_x = 0.7001
âge 65:  A_x = 0.7519   ä_x = 12.653   1 - d·ä_x = 0.7519
```

Pour 65 ans, un capital de 1 € payé au décès vaut aujourd'hui 0,7519 € et une rente de 1 € par an payée d'avance vaut 12,653 € : autrement dit, la rente vaut environ douze ans et demi de versements, une fois actualisée et pondérée par la survie. La dernière colonne, calculée à partir de la rente, **retrouve** $A_x$ à l'arrondi près (l'écart est inférieur à $10^{-10}$ sur tous les âges : c'est l'identité démontrée ci-dessus).

Les deux quantités évoluent en sens inverse avec l'âge : plus on est âgé, plus le capital décès est proche de 1 (le décès est proche) et moins la rente vaut cher (il reste peu d'années à payer). La figure montre ces deux courbes pour les deux sexes ; l'écart entre hommes et femmes est celui de leurs tables : la rente d'un homme de 65 ans coûte moins cher que celle d'une femme, son capital décès davantage.


![Valeur actuarielle d'un capital décès de 1 € (à gauche) et d'une rente viagère d'1 € par an payée d'avance (à droite), selon l'âge, à 2 % et avec la table de 2019 : femmes en bleu, hommes en orange. Données simulées.](figures/ch05-valeurs-actuarielles.png)

À 65 ans, la rente d'une femme vaut 12,653 et celle d'un homme 11,353 (pour 1 € par an) ; le capital décès vaut 0,7519 pour une femme et 0,7774 pour un homme.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.4, exercice 5.6.

### 5.2.3 Les primes : le principe d'équivalence

**Principe d'équivalence.** À la souscription, la valeur actuarielle des primes que paiera le client doit égaler celle des prestations que paiera l'assureur :

$$
\mathbb E[\text{VA des primes}] = \mathbb E[\text{VA des prestations}] .
$$

Si la prime est payée en une fois (**prime unique**), elle vaut simplement la valeur actuarielle des prestations : $\Pi = C\,A_x$ pour un capital $C$ en vie entière. Si elle est payée chaque année, d'avance et tant que l'assuré vit et que le contrat dure (**prime nivelée**), elle est la valeur actuarielle des prestations divisée par celle de la rente de primes :

$$
P = \frac{C\,A^{1}_{x:\overline{n}|}}{\ddot a_{x:\overline{n}|}} \quad\text{(temporaire de } n \text{ ans)}, \qquad
P = \frac{C\,A_x}{\ddot a_x} \quad\text{(vie entière)} .
$$

La prime ainsi obtenue est la **prime pure** : elle couvre le coût moyen de la mortalité, rien d'autre. La **prime commerciale** y ajoute les chargements (frais d'acquisition, de gestion, marge de sécurité et de profit), souvent exprimés en pourcentage de la prime ou du capital.

Le tableau suivant donne, pour 1 000 € de capital, la prime pure annuelle d'une temporaire de 20 ans et d'une vie entière, aux âges 30, 40, 50 et 60 ans, pour les deux sexes (table de population de 2019, $i=2\,\%$).

```text
 âge  temp. 20 ans F  temp. 20 ans H  vie entière F  vie entière H
  30            1.74            2.26          13.91          15.19
  40            4.59            5.90          19.62          21.58
  50           12.31           16.04          28.97          32.43
  60           32.46           40.82          45.76          52.26
NUM p30 1.738
NUM p60 32.462
NUM pv40 19.617
NUM pv60 45.763
NUM rat_p60_p30 18.7
NUM ratio_hf60 1.26
```

La lecture est instructive. La temporaire de 20 ans coûte 1,74 € par an pour 1 000 € à 30 ans et 32,46 € à 60 ans : **19 fois plus**, parce que la mortalité croît exponentiellement. La vie entière, qui paie certainement un jour, est bien plus chère à 30 ans que la temporaire (puisque la prime finance un capital qui sera effectivement versé) mais l'écart se réduit avec l'âge. Les hommes paient plus que les femmes : à 60 ans, la prime de la temporaire est 1,26 fois celle d'une femme.

> ⚠️ **Tarifer selon le sexe : un point réglementaire.** Les chiffres ci-dessus tarifent hommes et femmes différemment parce que **leurs tables diffèrent**. Dans certaines juridictions, l'usage du sexe comme critère de tarification est interdit ou encadré : on tarife alors avec une table unique, ce qui déplace un coût entre les deux populations. C'est une question de règle locale, que ce volume ne tranche pas  : vérifiez toujours le droit en vigueur.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.4, exercice 5.5.

### 5.2.4 Les provisions mathématiques

Avec une prime nivelée, le client paie **trop** au début (puisque la mortalité est encore faible) et **pas assez** à la fin (puisqu'elle est devenue élevée) : l'excédent des premières années est mis de côté pour couvrir le déficit des dernières. Cette réserve, que l'assureur doit constituer et garder à son bilan à tout moment du contrat, est la **provision mathématique**. Par la **méthode prospective**, c'est la différence entre ce qu'il reste à payer à l'assuré et ce qu'il reste à recevoir de lui :

$$
{}_tV = C\,A^{1}_{x+t:\overline{n-t}|} - P\,\ddot a_{x+t:\overline{n-t}|} \qquad (\text{à l'âge } x+t, \text{ après paiement de la prime } t).
$$

Par la **méthode rétrospective**, c'est l'accumulation du passé : les primes encaissées, capitalisées au taux $i$ et à la survie (« tous les assurés qui ont payé sont toujours là »), moins les sinistres payés, capitalisés de même :

$$
{}_tV = \frac{1}{{}_tp_x}\left[P\sum_{k=0}^{t-1}(1+i)^{t-k}\,{}_kp_x \;-\; C\sum_{k=0}^{t-1}(1+i)^{t-k-1}\,{}_kp_x\,q_{x+k}\right].
$$

> 📐 **Les deux méthodes coïncident (esquisse).** Par construction (équivalence), la valeur actuarielle des prestations moins celle des primes, sur toute la durée du contrat, est nulle. Coupons cette durée en deux au temps $t$. La partie future, vue de $t$ pour un assuré encore en vie, vaut ${}_tV$ (c'est la définition prospective). La partie passée, vue de $t$ (capitalisée au taux $i$ et à la survie, c'est-à-dire divisée par ${}_tp_x$), vaut « primes encaissées moins sinistres payés », qui est la définition rétrospective ; comme la somme des deux parties est nulle, les deux expressions sont égales. Elles ne le restent que **si la base technique (table, taux) est la même du début à la fin** : si l'on change de table en cours de contrat, les deux méthodes divergent.

Pour une temporaire de 20 ans souscrite à 40 ans pour un capital de 100 000 €, la prime annuelle pure est de 100 × la prime pour mille, soit environ 459,5 €, et la provision suit une courbe en cloche : positive, croissante au début, puis ramenée à zéro à l'échéance (le contrat ne laisse plus rien à payer).


![Provision mathématique d'une temporaire de 20 ans souscrite à 40 ans, capital de 100 000 € et prime nivelée pure, en fonction du nombre d'années écoulées (table de 2019, i = 2 %).](figures/ch05-provision.png)

La provision atteint 2 214 € à l'année 11, soit environ 2,2 % du capital, puis redescend vers zéro. Ce n'est pas un détail comptable : c'est de l'argent qui, **à chaque instant**, appartient en pratique aux assurés et que l'assureur doit pouvoir représenter par des actifs (chapitre 7 sur l'adossement des actifs). Le code caché vérifie que les deux méthodes donnent les mêmes valeurs (écart maximal de l'ordre de 8,1e-12), que la provision est nulle au début et à la fin, et que la **récurrence de Thiele** en temps discret, $(\,{}_tV+P)(1+i) = q_{x+t}\,C + p_{x+t}\,{}_{t+1}V$, est satisfaite à chaque pas : « ce que je détiens en début d'année, plus la prime, capitalisé, paie le sinistre éventuel et finance la provision de l'année suivante pour les survivants ».

> 🧭 **Pour aller plus loin : Thiele en temps continu.** En temps continu, la même relation devient l'équation différentielle de Thiele, $\dfrac{d\,{}_tV}{dt} = \delta\,{}_tV + P - \mu_{x+t}\,\big(C - {}_tV\big)$ : la provision croît par les intérêts et les primes et décroît du **capital sous risque** $C - {}_tV$ multiplié par l'intensité de décès. Sa lecture, « la provision est financée par l'écart entre prime et coût du risque », est utile pour comprendre les contrats d'épargne, que nous ne traitons pas.

> ⚠️ **Ce que cette provision ne contient pas.** Nous avons supposé que tous les assurés restent jusqu'à la fin du contrat. En pratique, les **rachats** et les **résiliations** (choix du client) jouent un rôle central dans l'épargne en assurance vie, et les frais futurs n'ont pas été comptés. Une provision réelle intègre la meilleure estimation des flux, incluant ces éléments, et une marge de risque (chapitre 4, section 4.2).

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.5, exercice 5.8.

### 5.2.5 Sensibilité : taux technique, table et longévité

Une prime ou une provision dépend de deux hypothèses **qui vieillissent**. Mesurons leur influence sur deux contrats opposés : une temporaire de 20 ans à 40 ans (le risque est que l'assuré décède) et une rente viagère à 65 ans (le risque est qu'il vive longtemps).

```text
                       temporaire 20 ans à 40 ans (€)  rente à 65 ans (€)
table 1980                                        8.2             10947.6
table 2019                                        4.6             12652.9
assurés (0,75 × 2019)                             3.5             14079.7
NUM var_temp_abs 44
NUM var_rente 15.6
NUM var_temp_ass_abs 25
NUM var_rente_ass 11.3
NUM rente_i1 13720
NUM temp_i1 4.78
NUM rente_i2 12653
NUM temp_i2 4.59
NUM rente_i3 11723
NUM temp_i3 4.42
NUM sens_rente 15
NUM sens_temp 8
NUM V_pic_pct 2.2
```

Le tableau se lit en deux temps. **D'une table à l'autre**, les deux contrats bougent dans **des sens opposés**. Entre 1980 et 2019 la mortalité a baissé : la temporaire est devenue moins chère de 44 %, tandis que la rente coûte 15,6 % de plus, parce qu'elle sera servie plus longtemps. Utiliser la table de 1980 pour tarifer une rente en 2019 aurait donc **sous-estimé** son coût de 15,6 % : c'est le risque de longévité en une phrase.

**De la population aux assurés**, le passage à la mortalité des assurés en cas de décès (0,75 × la table de 2019, section 5.1.5) fait baisser la prime de la temporaire de 25 % et fait **monter** le coût de la rente de 11,3 % : le même contrôle de sélection qui rend l'assurance décès moins chère rend les rentes plus chères. C'est pourquoi les assureurs utilisent des tables **distinctes** pour les deux types de contrats, et pourquoi la sélection médicale n'a pas de sens pour les rentes (on y observe plutôt l'inverse : les clients qui se savent en bonne santé achètent des rentes).

**Le taux technique** agit autrement, parce que les flux sont éloignés. Quand il passe de 1 % à 2 % puis à 3 %, le coût d'une rente de 1 000 € par an à 65 ans passe de 13 720 € à 12 653 € puis à 11 723 €, et la prime annuelle pour mille de la temporaire de 4,78 € à 4,59 € puis à 4,42 €. Entre 1 % et 3 %, la rente baisse de 15 % et la temporaire de 8 % : **plus le flux est lointain, plus l'actualisation compte**.

> 🧪 **Un couvert naturel.** Une mutuelle qui détient à la fois des contrats de décès et des rentes bénéficie d'une couverture partielle : si la mortalité baisse plus vite que prévu, elle perd sur les rentes et gagne sur les décès. La couverture reste imparfaite, parce que les âges et les montants ne correspondent pas. Les chapitres 6 (réassurance) et 7 (actif-passif) abordent la gestion d'un tel équilibre.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.4 et 5.5, exercice 5.7.

> ✅ **À retenir (5.2).**
> - La valeur actuarielle d'un flux est son montant actualisé, pondéré par sa probabilité. $A_x = \sum v^{k+1}{}_kp_x q_{x+k}$ et $\ddot a_x=\sum v^k {}_kp_x$ se calculent par récurrence à rebours, et $A_x = 1-d\,\ddot a_x$.
> - Le **principe d'équivalence** fixe la prime pure : $P = C\,A/\ddot a$. La prime commerciale ajoute les chargements.
> - La **provision mathématique** est ${}_tV = $ prestations futures − primes futures (méthode prospective) ; elle égale la méthode rétrospective tant que la base technique ne change pas.
> - La table et le taux technique sont des **hypothèses** : une table trop ancienne sous-tarife les rentes, la sélection rend les décès moins chers mais les rentes plus chères, et l'actualisation pèse davantage sur les flux lointains.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.4 et 5.5, exercices 5.5 à 5.8.


## 5.3 Le modèle de Lee–Carter

La section 5.1 a montré que la table d'une année n'est pas celle de la vie des assurés : la mortalité **baisse** et il faut la projeter. Le modèle de **Lee–Carter** (1992) est la référence historique pour le faire : il tient en une équation, s'ajuste en une décomposition en valeurs singulières, et résume l'évolution de la mortalité de tous les âges par **un seul indice du temps** que l'on prolonge comme une série chronologique. Cette section l'ajuste sur nos données, le compare à la **vérité programmée**, le projette, le met à l'épreuve hors période, puis chiffre le **risque de longévité** d'un portefeuille de rentes.


### 5.3.1 Le modèle

Le modèle de Lee–Carter décrit le logarithme du taux de mortalité à l'âge $x$ l'année $t$ par

$$
\ln m_{x,t} = a_x + b_x\,k_t + \varepsilon_{x,t}.
$$

Chaque terme a un rôle précis :

- $a_x$ est le **profil moyen** : le logarithme du taux à l'âge $x$ en moyenne sur la période (la courbe en J des taux de la section 5.1.1).
- $k_t$ est l'**indice du temps** : un nombre par année, qui résume le niveau général de la mortalité. Quand $k_t$ baisse, la mortalité baisse à tous les âges.
- $b_x$ est la **sensibilité de l'âge $x$** à cet indice. Si $k$ diminue de $\Delta k$, le taux à l'âge $x$ est multiplié par $e^{b_x\Delta k}$.

Un chiffre aide à lire $b_x$ : dans cette population, $b_{20}=0,0129$, $b_{35}=0,0145$, $b_{60}=0,0106$ et $b_{90}=0,0042$ (valeurs vraies). Avec une dérive de $-1{,}2$ par an pour $k_t$, la mortalité baisse chaque année d'environ 1,3 % à 60 ans et de 1,5 % à 20 ans. L'amélioration est donc **inégale** selon l'âge, et c'est précisément ce que le terme $b_x$ permet de représenter (avec un seul $k_t$ et des taux d'amélioration constants, on retrouverait au contraire une baisse identique à tous les âges).

> 📐 **Identification : pourquoi deux contraintes.** Le modèle n'est pas identifiable tel quel : si $(a_x, b_x, k_t)$ convient, alors $(a_x + c\,b_x,\; b_x,\; k_t - c)$ donne exactement les mêmes taux (on déplace une constante de $k$ vers $a$), et $(a_x,\; \lambda b_x,\; k_t/\lambda)$ aussi (on échange une échelle entre $b$ et $k$). On fixe donc ces deux libertés par
> $$\sum_t k_t = 0, \qquad \sum_x b_x = 1 .$$
> La première rend $a_x$ égal à la moyenne temporelle de $\ln m_{x,t}$ (c'est ce qu'on calcule en premier) ; la seconde donne à $k_t$ l'unité d'une variation de « taux moyen » et rend les $b_x$ comparables à des parts. **Cette convention est arbitraire** : changer la normalisation change la valeur de $k_t$ sans changer les taux ajustés. Quand on compare des estimations à la vérité, il faut donc comparer les mêmes conventions : c'est le cas ici, la vérité programmée vérifiant $\sum_t k_t = 0$ et $\sum_x b_x = 1$.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : exercice 5.9.

### 5.3.2 Ajustement par décomposition en valeurs singulières

Une fois $a_x$ estimé par la moyenne en ligne de la matrice des $\ln m_{x,t}$ (âges en lignes, années en colonnes), la matrice centrée $Z_{x,t} = \ln m_{x,t} - \hat a_x$ doit se factoriser sous la forme $b_x k_t$ : c'est une approximation de **rang 1**. Le théorème d'Eckart–Young dit que la meilleure approximation de rang 1 au sens des moindres carrés est donnée par le premier terme de la **décomposition en valeurs singulières** (SVD) : $Z \approx s_1\,u_1 v_1^{\top}$. On pose alors $b_x \propto u_{1,x}$ et $k_t \propto s_1\,v_{1,t}$, normalisés par les deux contraintes.

```python
ax_hat, bx_hat, kt_hat, sv = lc_ajuste(M["F"])        # SVD de ln m − a_x, normalisée (Σb = 1, Σk = 0)
part = sv ** 2 / (sv ** 2).sum()                       # part de variation de chaque composante
print(f"première composante : {100 * part[0]:.1f} % ;  Σ b = {bx_hat.sum():.3f} ;  Σ k = {kt_hat.sum():.0e}")
```
<!--sortie-->
```text
première composante : 64.1 % ;  Σ b = 1.000 ;  Σ k = 2e-13
```

La première composante explique 64,1 % de la variation de $Z$. Ce n'est pas davantage parce que le reste est du **bruit** et non de la structure : chaque cellule a des décès de Poisson, dont le bruit relatif est grand aux âges où les décès sont rares. Ce taux de 64,1 % ne mesure donc pas la qualité du modèle (qui est ici exactement vrai), mais la part de bruit dans les données. Dans la littérature, sur des populations nationales bien plus nombreuses, la première composante explique d'ordinaire une part nettement plus élevée de la variation (de l'ordre de 90 % ou plus, valeur à vérifier selon les données).

**Seconde étape : recaler $k_t$.** La SVD minimise des erreurs sur les *logarithmes* des taux, et traite aussi fortement les âges rares (peu de décès) que les âges fréquents. Lee et Carter ajoutent donc une étape : pour chaque année, on **ré-estime $k_t$** pour que le nombre de décès prédit soit égal au nombre de décès observé, c'est-à-dire que l'on résout en $k$ l'équation $\sum_x E_{x,t}\,e^{\hat a_x+\hat b_x k}=\sum_x D_{x,t}$. Le recalage réduit l'erreur : l'écart quadratique moyen entre $k_t$ estimé et vrai passe de 1,36 (SVD seule) à 0,89 (recalé).

La figure compare les trois composantes à la vérité programmée. Les $a_x$ sont retrouvés (écart maximal 0,09 sur le logarithme du taux), les $b_x$ ont la bonne forme (corrélation 0,931 avec les vrais $b_x$) et le $k_t$ recalé suit la vérité, y compris le **pic de 2018** que nous discutons en 5.3.3.


![Modèle de Lee–Carter ajusté sur les femmes : $a_x$, $b_x$ et $k_t$ estimés (bleu) contre la vérité programmée (gris épais) ; en orange, $k_t$ obtenu par la SVD seule avant recalage. Données simulées.](figures/ch05-lee-carter.png)

> 🧪 **Un avantage de l'honnêteté des données simulées.** Avec des données réelles, on ne peut pas vérifier si $\hat b_x$ est « le vrai $b_x$ » : il n'existe pas. Ici, on constate que l'estimation est **bonne mais pas exacte** : l'erreur relative sur $b_x$ est en médiane de 6 % entre 20 et 90 ans (au maximum 44 %), et elle se répercute sur $k_t$ : l'erreur de $k_t$ a une corrélation de 0,61 avec $k_t$ lui-même, signe d'une erreur d'échelle. Cette erreur d'estimation va jouer un rôle dans la projection.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.6, exercices 5.9 et 5.10.

### 5.3.3 Projeter l'indice $k_t$

Le mérite du modèle est de transformer un problème de dimension 100 (une série par âge) en un problème de **dimension 1** : la série $k_t$. Lee et Carter la modélisent par une **marche aléatoire avec dérive** :

$$
k_{t+1} = k_t + \delta + \sigma\,\eta_{t+1}, \qquad \eta_t \sim \mathcal N(0,1) \text{ indépendants}.
$$

L'estimateur naturel de la dérive est la pente moyenne, $\hat\delta = (k_T - k_1)/(T-1)$ (les accroissements intermédiaires s'annulent), et celui de $\sigma$ est l'écart-type des accroissements $\Delta k_t = k_{t}-k_{t-1}$. La prévision à $h$ années est $k_T + h\,\hat\delta$, avec un écart-type $\sigma\sqrt{h}$ qui **croît** avec l'horizon.

```python
delta, sigma = derive_sigma(KTe)                           # dérive et écart-type des accroissements de k_t
print(f"dérive estimée δ = {delta:.3f}   écart-type σ = {sigma:.3f}")
```
<!--sortie-->
```text
dérive estimée δ = -1.286   écart-type σ = 1.895
```

La dérive estimée est de -1,286 par an, **très proche de la vérité programmée** ($-1{,}2$) : l'estimateur de la pente, qui ne dépend que des deux extrémités, résiste bien au bruit. L'écart-type estimé est de 1,90, **nettement supérieur** à la vérité programmée ($\sigma=1$). Deux causes se combinent, et chacune est instructive.

**Première cause : le choc de 2018.** Le jeu contient un pic transitoire de mortalité en 2018 (un épisode de surmortalité qui ne dure qu'une année, de $+4$ sur $k$). Il crée un accroissement positif d'environ $+4$ l'année du choc puis un accroissement négatif d'environ $-4$ l'année suivante. La dérive, qui ne dépend que des extrémités, l'ignore, mais l'écart-type en est fortement gonflé. En remplaçant la valeur de 2018 par l'interpolation de ses voisines, on passe à 1,57. Le bon traitement dépend de la nature du choc : s'il est **transitoire** (épidémie, canicule), on l'écarte de l'estimation de $\sigma$ ; s'il est **permanent** (une rupture structurelle de tendance), on le garde et l'on s'interroge sur la dérive.

**Seconde cause : l'erreur d'estimation de $k_t$.** Les $\hat k_t$ ne sont pas les vrais $k_t$ : chacun est estimé avec une erreur d'écart-type $\tau\approx0,64$ d'après l'information de Fisher du modèle de Poisson ($\tau_t^2 = 1/\sum_x D_{x,t}\,\hat b_x^2$). Les accroissements estimés ont donc une variance $\sigma^2 + 2\tau^2$ (deux erreurs, chacune comptée une fois, et indépendantes d'une année à l'autre), ce qui donne $\sigma$ corrigé $=\sqrt{\hat\sigma^2 - 2\tau^2}\approx1,28$, plus proche de la vérité (la variabilité effectivement réalisée par les vrais $k_t$ est de 1,00 hors choc). **Ignorer cette correction rend les intervalles de projection trop larges** : une prudence parfois voulue, mais qu'il vaut mieux faire par choix que par accident.

Projetons maintenant $k_t$ sur 30 ans (jusqu'en 2049) par simulation de 2 000 trajectoires, avec la dérive estimée et l'écart-type interpolé. L'espérance de vie à 65 ans se déduit de $k$ par la table construite avec $a_x+b_x k$ : on la calcule pour chaque niveau de $k$. La figure montre l'éventail des trajectoires de $k_t$ et l'espérance de vie à 65 ans correspondante.


![Projection de Lee–Carter pour les femmes : indice $k_t$ (à gauche) et espérance de vie à 65 ans correspondante (à droite). La ligne pleine est l'historique estimé, les tirets la médiane projetée, les zones foncée et claire les intervalles à 50 % et à 90 % (2 000 trajectoires). Données simulées.](figures/ch05-projection.png)

L'espérance de vie à 65 ans passe de 14,47 ans en 2019 (valeur lissée par le modèle) à une médiane de 16,17 ans en 2049 (intervalle à 90 % : de 15,52 à 16,78 ans), soit un gain médian de 1,7 an sur trente ans. Le modèle fait **gagner du temps au même rythme qu'avant** : si le rythme passé s'est interrompu, la projection l'ignore.

**Incertitude de paramètre.** L'intervalle ci-dessus ne contient que l'incertitude de **trajectoire** (le bruit $\sigma\eta$). Il ignore que la dérive elle-même est estimée : son écart-type est environ $\sigma/\sqrt{T-1}$, soit 0,25 pour une dérive de -1,286, une imprécision relative d'environ 19 %. On peut la prendre en compte en tirant la dérive de chaque trajectoire dans sa loi d'estimation (5.3.4).

> ⚠️ **Un intervalle de projection n'est qu'un modèle de plus.** L'éventail de la figure repose sur l'hypothèse d'une marche aléatoire à dérive **constante**, des mêmes $b_x$ pour toujours, et d'erreurs gaussiennes indépendantes. Rien ne garantit que la médiocre prévisibilité du passé se prolonge : l'incertitude **de modèle** est hors de l'intervalle.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.6, exercice 5.11.

### 5.3.4 Mettre le modèle à l'épreuve hors période, puis chiffrer le risque de longévité

**Une prévision se juge sur des données qu'elle n'a pas vues.** Refaisons l'exercice en ne montrant au modèle que les années 1980 à 2009, projetons dix ans, et comparons à ce qui s'est réellement passé jusqu'en 2019.


Le modèle ajusté sur 1980–2009 prévoit pour 2019 un indice médian de -30,3 (intervalle à 90 % : de -39,3 à -21,7) ; la valeur effectivement estimée sur toutes les données est de -26,5, **dans l'intervalle**. En espérance de vie à 65 ans en 2019, la prévision est de 14,34 ans contre 14,45 réellement, soit une erreur de 0,11 an ; la méthode **naïve** (garder la table de 2009 telle quelle) aurait donné 13,79 ans, soit une erreur de 0,66 an : **6 fois plus**. La projection fait mieux que l'immobilisme, et c'est ce que l'on attendait.

> ⚠️ **Une validation flatteuse.** Les données ont été simulées avec exactement le modèle de Lee–Carter : l'ajustement ne peut qu'être bon. Sur des données réelles, on attend un modèle moins bien spécifié (effets de cohorte, ruptures) et des erreurs de prévision plus fortes. Le **protocole** (ajuster sur le passé, projeter, comparer) est ce qu'il faut retenir, pas le score.

**Le risque de longévité d'un portefeuille de rentes.** Un assureur sert des rentes viagères à des personnes qui ont 65 ans en 2019. Le coût d'une rente d'un euro par an payée d'avance, actualisée à 2 %, se calcule de trois manières :

1. **table de période 2019** : on suppose que la mortalité de 2019 ne change plus ;
2. **table de génération projetée** : on suit la cohorte, la mortalité de chaque année future étant celle que le modèle projette (valeur moyenne des simulations) ;
3. **distribution complète** : pour chaque trajectoire simulée de $k_t$, on recalcule le coût de la rente, ce qui donne une **loi** du coût.

Les trajectoires simulées incluent, pour chacune, une dérive tirée dans la loi d'estimation (incertitude de paramètre). Le **99,5 %-quantile** de cette loi, comparé à la moyenne, est le **capital de risque de tendance** : la somme à ajouter aux provisions pour couvrir un scénario de longévité aussi défavorable qu'un cas sur 200 (le seuil de 99,5 % est celui de Solvabilité II, section 4.2 ; il s'agit ici d'un ordre de grandeur pédagogique, non d'un calcul réglementaire).


Les résultats : la rente coûte 12,65 € par euro de rente avec la table de période 2019, **13,03 €** avec la table de génération projetée (soit 3,0 % de plus : c'est le prix de l'ignorance de l'amélioration future), et le 99,5 %-quantile de la distribution est de 13,40 €, soit 2,8 % au-dessus de la moyenne. Le coefficient de variation du coût dû à la tendance est de 1,0 %.

Ce chiffre de 2,8 % est **petit**, et il faut s'en méfier pour deux raisons. D'abord, il dépend de l'hypothèse de marche aléatoire à dérive constante, qui ne laisse aucune place à une rupture de tendance. Ensuite, il est très inférieur à la secousse que l'on obtiendrait si l'on supposait simplement que les taux de décès sont **20 % plus bas** que prévu pour toujours : cela augmenterait le coût de la rente de 9,1 %. Les cadres prudentiels retiennent des chocs forfaitaires de cet ordre (paramètre à vérifier dans les textes en vigueur) justement parce que la **vraie** incertitude de modèle est supérieure à celle d'un modèle ajusté sur un passé récent : c'est le sens de la prudence réglementaire, qui ne mesure pas le même risque que l'intervalle statistique de la figure.

![Risque de longévité d'un portefeuille de rentes à 65 ans (femmes, 2019, i = 2 %). À gauche : coût d'une rente de 1 € par an selon 2 000 trajectoires de la tendance, avec la table de période (violet), la moyenne (gris) et le quantile à 99,5 % (rouge). À droite : écart-type relatif du coût moyen par rentier selon le nombre de rentiers, risque individuel (bleu) et risque de tendance (rouge). Données simulées.](figures/ch05-longevite.png)

La figure de droite montre la différence de nature entre les deux risques. Le **risque individuel** (un rentier vit plus ou moins longtemps) a un coefficient de variation de 45 % pour un seul rentier ; il **se dilue** avec le nombre : 4,5 % pour 100 rentiers, 1,4 % pour 1 000, 0,45 % pour 10 000. Le **risque de tendance** (toute la cohorte vit plus longtemps que prévu) touche tout le portefeuille en même temps : il **ne se mutualise pas**, et plafonne le risque restant à environ 1,0 % quel que soit le nombre de rentiers. Au-delà d'environ 1 900 rentiers, c'est lui qui domine.

> 💡 **Intuition.** La loi des grands nombres fait disparaître les **hasards** (qui meurt cette année), pas les **erreurs de modèle ou de tendance** (comment la mortalité évolue pour tous). C'est le même principe qu'au chapitre 3 pour le risque de marché : la diversification protège contre le bruit idiosyncratique, pas contre un facteur commun. La réassurance et le transfert de risque de longévité (chapitre 6) visent précisément ce facteur commun.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.7 et 5.8, exercice 5.12.

### 5.3.5 Limites du modèle

Le modèle de Lee–Carter est une **référence**, pas une vérité. Ses limites, à garder en tête quand on lit une projection :

- **Un seul facteur.** Un seul $k_t$ impose que tous les âges évoluent de façon parfaitement corrélée, au rythme $b_x$. Les modèles à plusieurs facteurs, ou les modèles qui séparent effets d'âge, de période et de **cohorte** (par exemple Cairns–Blake–Dowd, Renshaw–Haberman, âge-période-cohorte), corrigent ce défaut en ajoutant des paramètres.
- **Un bruit mal pris en compte.** L'ajustement par SVD suppose des erreurs de même variance sur les logarithmes, ce qui est faux (le bruit de Poisson est beaucoup plus fort aux âges rares). La formulation de **Brouhns, Denuit et Vermunt** ajuste directement la vraisemblance de Poisson et corrige ce défaut ; le recalage de la seconde étape en est une approximation.
- **Une dérive constante.** Rien dans les données ne prouve que le rythme d'amélioration restera celui du passé. Plusieurs pays ont connu des ralentissements, et des accélérations par vagues (selon la cause de décès), que ni la dérive constante ni l'éventail de la figure ne contiennent.
- **Des chocs de natures différentes.** Un pic transitoire (2018 ici) n'est pas une rupture, mais nous avons dû l'identifier **à la main**. Les épidémies et les canicules se traitent par des termes d'évènement distincts.
- **La vérité n'est pas connue.** Sur des données réelles, on ne peut pas comparer les estimations à la vérité : la validation hors période (5.3.4) est la meilleure assurance, et elle n'est jamais définitive.

> ✅ **À retenir (5.3).**
> - $\ln m_{x,t}=a_x+b_xk_t$ : profil moyen, sensibilité par âge, indice du temps ; contraintes $\sum k_t=0$ et $\sum b_x=1$. Ajustement par SVD (meilleure approximation de rang 1), puis recalage de $k_t$ sur les décès.
> - On projette $k_t$ par une marche aléatoire avec dérive : la dérive est bien estimée par les extrémités, mais $\sigma$ est **gonflé** par l'erreur d'estimation de $k_t$ et par les chocs transitoires.
> - **Valider hors période** : sur ces données, la projection fait nettement mieux que de figer la table.
> - Le **risque de longévité** a deux composantes : un risque individuel qui se mutualise, et un risque de tendance qui ne se mutualise pas. Le second plafonne la précision d'un portefeuille de rentes.
> - Les chiffres de capital sont **conditionnels** au modèle : les chocs réglementaires forfaitaires sont plus larges que l'intervalle statistique parce qu'ils couvrent aussi l'incertitude de modèle.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.6 à 5.8, exercices 5.9 à 5.12.


## Bilan du chapitre 5

Vous savez maintenant :

- **passer des décès aux taux et aux probabilités** : $m_x=D_x/E_x$ (estimateur de Poisson, précision relative $1/\sqrt{D}$), $q_x=1-e^{-m_x}$, et construire une **table** ($\ell_x$, $d_x$, $L_x$, $e_x$) ; distinguer **table de période** et **table de génération**, et savoir pourquoi la première sous-estime la durée de vie quand la mortalité baisse ;
- **lisser et prolonger** une table par la loi de **Gompertz–Makeham** (doublement de la mortalité tous les $\ln 2/c$ ans), en sachant que l'extrapolation est une hypothèse ;
- **mesurer la sélection** par un **rapport réel/attendu** avec son intervalle exact de Poisson (0,765 avec [0,713 ; 0,818] sur ce portefeuille, pour une valeur programmée de 0,75), et savoir qu'un découpage trop fin ne produit que du bruit ;
- **actualiser** des flux incertains : capital décès $A_x$, rente viagère $\ddot a_x$, relation $A_x=1-d\,\ddot a_x$, **prime pure** par le principe d'équivalence, **provision mathématique** prospective et rétrospective, récurrence de Thiele ;
- **mesurer la sensibilité** d'un contrat à la table et au taux technique, et comprendre que **la baisse de la mortalité aide les contrats de décès et pénalise les rentes** ;
- **ajuster un modèle de Lee–Carter** ($\ln m_{x,t}=a_x+b_xk_t$) par SVD, recaler $k_t$, **projeter** $k_t$ par une marche aléatoire avec dérive, le **valider hors période**, et reconnaître ce qui gonfle l'écart-type estimé (chocs transitoires, erreur d'estimation) ;
- **chiffrer un risque de longévité** : coût d'une rente selon la table de période ou de génération, quantile à 99,5 %, et différence entre **risque individuel** (qui se mutualise) et **risque de tendance** (qui ne se mutualise pas).

Le tableau suivant résume **ce que nous avons mesuré** sur les femmes de la population simulée (données simulées, taux technique de 2 % pris pour l'illustration) :

| Question | Résultat |
|---|---|
| Espérance de vie à la naissance / à 65 ans, table de 2019 | 74,39 ans / 14,45 ans |
| Années vécues de 60 à 100 ans : période 1980, cohorte 1920, période 2019 | 15,90 / 16,71 / 18,71 |
| Mortalité des assurés par rapport à la population (A/E) | 0,765 |
| Prime annuelle pour 1 000 € : temporaire de 20 ans à 40 ans | 4,59 € |
| Coût d'une rente de 1 € par an à 65 ans : période, génération projetée | 12,65 €, 13,03 € |
| Rente à 65 ans : effet d'une mortalité de 20 % plus basse | + 9,1 % |
| Dérive de $k_t$ estimée / vraie | -1,286 / −1,2 |
| Espérance de vie à 65 ans en 2049 (médiane projetée) | 16,17 ans |

Le fil conducteur du chapitre tient en une phrase : **une table de mortalité est une hypothèse sur l'avenir déguisée en tableau de chiffres**. On peut estimer le niveau d'une mortalité avec une précision remarquable (une population de centaines de milliers de personnes), mais le prix d'un contrat à long terme dépend de **la tendance**, qu'aucune observation ne garantit, et le risque qui en résulte ne se diversifie pas. Le chapitre 6 présente le transfert d'un tel risque (la réassurance) et le chapitre 7 la manière dont un assureur ajuste ses placements à ses engagements.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.8 (table de période, lissage et graduation, rapport réel/attendu, valeurs actuarielles, provisions, Lee–Carter, risque de longévité, validation hors période) et exercices 5.1 à 5.12.


---

# Chapitre 6 : ➕ Bases de la réassurance et de sa tarification

> « Réassurer, c'est acheter de la tranquillité. Son prix se calcule, et surtout il se discute. »

> 🧭 **Chapitre complémentaire.** Il peut être lu sans le reste du volume, mais il suppose les notions de sévérité à queue lourde (volume II, section 6.5), de VaR et d'*expected shortfall* (section 3.1) et de capital réglementaire (section 4.2). Le chapitre 7 en est indépendant.

Une mutuelle d'assurance a un métier simple à énoncer : mettre en commun des risques pour que chacun supporte une part prévisible d'un aléa que, seul, il ne pourrait pas porter. Mais la mutuelle est elle-même exposée à un aléa qu'elle ne peut pas diluer indéfiniment : **quelques sinistres très gros** (un incendie qui détruit un entrepôt, une tempête qui touche tout un territoire le même jour) peuvent à eux seuls faire basculer un exercice, voire menacer sa solvabilité. La **réassurance** est l'assurance de l'assureur : la mutuelle (la **cédante**) transfère à un **réassureur** une partie de ses risques, contre une prime.

Ce chapitre répond à trois questions, dans l'ordre où une cédante se les pose.

## Le chemin de ce chapitre

| Section | Question | Ce que vous saurez faire |
|---|---|---|
| **6.1 Principes et formes** | Comment un traité partage-t-il les sinistres entre cédante et réassureur ? | Distinguer **proportionnel** et **non proportionnel**, calculer à la main ce que cède chaque forme, lire une clause (priorité, portée, réintégration). |
| **6.2 Tarifer un traité** | Combien vaut une tranche de sinistres gros ? | Estimer une prime pure par le *burning cost*, par une loi de queue (GPD) et par l'exposition ; **chiffrer l'incertitude** ; passer de la prime pure à la prime technique. |
| **6.3 Choisir une couverture** | Que gagne-t-on à réassurer, et à quel prix ? | Simuler la charge annuelle, comparer des programmes par le **coût d'un euro de capital économisé**, regarder le risque de contrepartie et l'épuisement des garanties. |

Le fil conducteur est celui du volume : **chiffrer un risque, puis prouver que le chiffre tient**. Ici, la preuve est difficile, parce que le risque réassuré est précisément celui dont on a **le moins d'observations** : on parle de sinistres qui arrivent une fois en cinq ans, une fois en vingt ans. Vous verrez qu'une estimation correcte peut se tromper de 10 %, de 30 %, ou de beaucoup plus sur une tranche haute, **sans qu'aucun calcul n'ait été faux**.

## Les données du chapitre

> 📦 **Données.** Deux fichiers **simulés**, sans lien avec une entreprise réelle.
> - `sinistres_gros.csv` : 2 898 sinistres « incendie » de la mutuelle sur 15 ans (2010 à 2024), avec l'année de survenance et le montant en €. Le nombre de sinistres croît d'environ 3 % par an, parce que le portefeuille grandit.
> - `cat_annuel.csv` : la perte annuelle due à des **événements catastrophiques** sur 40 ans (1985 à 2024), en €, avec beaucoup d'années à zéro.
>
> Comme toujours, les données sont fabriquées par un programme : nous **connaissons la vérité** (la loi des sinistres, la loi des catastrophes, le taux de croissance), et nous la révélerons au fil des études pour juger les estimations. En pratique, elle n'est jamais connue.


Les sinistres se résument en quelques lignes :

```python
sg, cat = O.charger()
print(sg["montant"].describe().round(0))
```
<!--sortie-->
```text
count       2898.0
mean      115984.0
std       290925.0
min          189.0
25%        10088.0
50%        30118.0
75%        86846.0
max      4310320.0
Name: montant, dtype: float64
```

Le sinistre médian vaut 30 118 €, le sinistre moyen 115 984 € : **la moyenne vaut près de quatre fois la médiane**, signe d'une distribution très asymétrique. Les 177 sinistres de plus de 500 000 € (6,1 % des sinistres) pèsent 53 % du montant total ; le plus gros atteint 4 310 320 €. Les catastrophes sont encore plus rares : 17 années sur 40 ont connu un événement, et la pire a coûté 35 614 167 €. Ce sont ces queues que la réassurance vient couvrir, et ce sont elles qui rendent leur prix incertain.

> ⚠️ **Deux conventions de lecture.** Les tranches s'écrivent « **portée xs priorité** » : « 1 M€ xs 1 M€ » désigne la tranche qui paie la part d'un sinistre comprise **entre 1 M€ et 2 M€**. Et tous les montants « au niveau 2025 » désignent l'**exposition attendue de l'année 2025** (environ 249 sinistres par an, contre 160 en 2010).


## 6.1 Principes et formes de réassurance

Avant de tarifer un traité, il faut comprendre ce qu'il fait : qui paie quoi, quand, et dans quelle proportion. Cette section pose le vocabulaire, montre **pourquoi** une cédante réassure (c'est une affaire de variance et de capital, pas de moyenne), puis décrit les deux grandes familles de traités en calculant, **à la main**, ce que chacune cède sur huit sinistres.

### 6.1.1 Pourquoi réassurer ?

Une cédante ne réassure pas pour réduire son coût moyen : en moyenne, la réassurance **coûte** (le réassureur facture ses frais et une marge). Elle réassure pour trois raisons qui concernent la **dispersion** du résultat.

**Stabiliser le résultat.** Un exercice où un seul sinistre pèse un quart de la charge annuelle est un exercice imprévisible. Les dirigeants, les adhérents, le régulateur et les agences de notation préfèrent un résultat qui ne dépend pas d'un coup du sort.

**Gagner de la capacité.** Un assureur ne peut accepter un risque de 50 M€ que si une perte totale ne l'anéantit pas. En cédant la part qui dépasse ce qu'il peut porter, il accepte des risques plus gros, donc gagne des clients.

**Économiser du capital.** Le capital réglementaire (section 4.2) et le capital économique dépendent de la queue de la distribution des pertes. Transférer la queue au réassureur réduit le capital immobilisé. Nous mesurerons cela en 6.3.

Le vocabulaire se résume en quelques mots. La **cédante** est l'assureur direct qui cède ; le **réassureur** accepte la cession ; le **rétrocessionnaire** réassure le réassureur. Un **traité** couvre automatiquement tout un portefeuille selon des règles convenues ; une **facultative** couvre un risque isolé, négocié au cas par cas. Les montants **bruts** sont ceux de la cédante avant réassurance, les montants **nets** après. La **prime cédée** est ce que la cédante paie, les **récupérations** ce que le réassureur rembourse.

#### Un coup d'œil sur la variance

Pourquoi la réassurance agit-elle surtout sur les gros sinistres ? Parce que la variance de la charge annuelle vient d'eux. Notons $S=X_1+\dots+X_N$ la charge annuelle, où le nombre de sinistres $N$ suit une loi de Poisson de moyenne $\lambda$ et où les montants $X_i$ sont indépendants, de même loi, de moyenne $\mu$.

> 📐 **Variance de la charge annuelle.** Par la formule de l'espérance totale, $E[S]=\lambda\mu$. Par la formule de la variance totale,
> $$\operatorname{Var}(S)=E[\operatorname{Var}(S\mid N)]+\operatorname{Var}(E[S\mid N])=E[N]\operatorname{Var}(X)+\operatorname{Var}(N)\,\mu^2=\lambda\bigl(\operatorname{Var}(X)+\mu^2\bigr)=\lambda\,E[X^2],$$
> puisque $E[N]=\operatorname{Var}(N)=\lambda$ pour une loi de Poisson. Le **coefficient de variation** de la charge annuelle vaut donc
> $$\mathrm{CV}(S)=\frac{\sqrt{\lambda E[X^2]}}{\lambda\mu}=\sqrt{\frac{1+\mathrm{CV}(X)^2}{\lambda}}.$$

Deux enseignements. D'abord, avec $\lambda$ sinistres par an, le CV décroît comme $1/\sqrt\lambda$ : **quadrupler** le portefeuille ne fait que **diviser par deux** l'incertitude relative. Ensuite, le CV dépend du **CV d'un sinistre** : une queue lourde (un $E[X^2]$ gigantesque) annule les bénéfices de la mutualisation.

Appliquons-le à nos sinistres. Le CV d'un sinistre vaut 2,51 ; avec 249 sinistres attendus, le CV de la charge annuelle brute est de 17,1 %. Si la cédante **plafonne** chaque sinistre à 500 000 € (c'est ce que fait un excédent de sinistre « 500 xs 500 »), le CV d'un sinistre net tombe à 1,55, et celui de la charge annuelle à 11,7 %. Pour obtenir la même régularité **sans** réassurance, il faudrait un portefeuille **2,1 fois plus gros**.


> 💡 **Réassurer, c'est couper la queue.** La loi des grands nombres protège des petits sinistres (ils se compensent), pas des gros (ils dominent la variance). La réassurance est l'outil qui s'attaque exactement à ce que la mutualisation ne sait pas faire.

### 6.1.2 Les traités proportionnels

Dans un traité **proportionnel**, cédante et réassureur partagent **à la fois les primes et les sinistres, dans la même proportion**. Deux variantes existent.

**La quote-part.** La cédante cède un pourcentage fixe $\alpha$ de **chaque** risque : prime $\alpha P$, sinistre $\alpha X$. Le réassureur verse en outre à la cédante une **commission de cession** (un pourcentage de la prime cédée), qui couvre les frais d'acquisition et de gestion qu'elle a engagés. Le partage est simple et sans négociation sur les sinistres : le réassureur « suit la fortune » de la cédante.

**L'excédent de plénitude** (on dit aussi *surplus*). La cédante fixe une **plénitude** $R$, le montant maximal qu'elle garde sur un risque. Pour un risque de capital assuré (valeur exposée) $V_i$, elle cède la fraction
$$\tau_i=\max\Bigl(0,\;1-\frac{R}{V_i}\Bigr)$$
de ce risque, avec la même fraction de la prime et de chaque sinistre sur ce risque. Les petits risques ($V_i\le R$) restent entièrement chez la cédante ; les gros sont partagés. Le traité **homogénéise** ainsi le portefeuille net : aucun risque ne dépasse $R$ en valeur exposée.

#### Un exemple à la main

Huit sinistres de l'année (en k€), chacun survenu sur un risque dont le capital assuré est connu :

| Sinistre | Capital assuré | Quote-part 30 % : cédé | Taux de cession (plénitude 1 000) | Plénitude : cédé | 500 xs 500 : cédé |
|---|---:|---:|---:|---:|---:|
| 30 | 200 | 9 | 0 % | 0 | 0 |
| 45 | 300 | 13,5 | 0 % | 0 | 0 |
| 80 | 500 | 24 | 0 % | 0 | 0 |
| 120 | 800 | 36 | 0 % | 0 | 0 |
| 250 | 1 000 | 75 | 0 % | 0 | 0 |
| 600 | 2 500 | 180 | 60 % | 360 | 100 |
| 900 | 3 000 | 270 | 66,7 % | 600 | 400 |
| 2 000 | 5 000 | 600 | 80 % | 1 600 | 500 |
| **Total : 4 025** | | **1 207,5** | | **2 560** | **1 000** |

Avec la quote-part de 30 %, la cédante garde 2 817,5 : chaque sinistre est réduit de 30 %, **la forme de la distribution ne change pas**, seule son échelle. Avec l'excédent de plénitude de 1 000, elle cède plus (2 560) et garde 1 465 : le traité prélève surtout sur les gros risques, donc sur les gros sinistres. Pour le sinistre de 600, par exemple, le risque valait 2 500, la cédante en garde $1\,000/2\,500=40\,\%$ et cède donc $60\,\%\times600=360$.

![Trois façons de partager les mêmes huit sinistres. En bleu, la part gardée par la cédante ; en orange, la part cédée.](figures/ch06-formes.png)


> ⚠️ **La quote-part ne réduit pas le risque relatif.** Elle réduit de 30 % la perte maximale en euros, mais le sinistre de 2 000 reste, à l'échelle de l'année, le sinistre qui domine. Elle sert surtout à **alléger le capital** et à **financer la croissance** (la commission). Pour couper la queue, il faut un traité qui se déclenche **sur les gros montants**.

### 6.1.3 Les traités non proportionnels

Dans un traité **non proportionnel**, le réassureur ne paie que **la part des sinistres qui dépasse un seuil**, et la prime n'est plus un pourcentage de la prime d'origine : elle se tarife (section 6.2).

**L'excédent de sinistre par risque** (*per risk excess of loss*). La tranche « $L$ xs $a$ » a une **priorité** $a$ (le montant que la cédante garde toujours) et une **portée** $L$ (le maximum que le réassureur paie par sinistre). Pour un sinistre $X$, le réassureur paie
$$R(X)=\min\bigl(\max(X-a,\,0),\;L\bigr),$$
et la cédante garde $X-R(X)$. Sur nos huit sinistres, la tranche « 500 xs 500 » paie $100$ pour le sinistre de 600, $400$ pour celui de 900, et $500$ (la portée entière) pour celui de 2 000 : **1 000 en tout**, soit un quart du total, alors qu'elle n'intervient que sur trois sinistres.

**L'excédent de sinistre par événement** (*catastrophe*, ou cat XL). Même mécanisme, mais le sinistre est **la somme des pertes d'un même événement** (une tempête, une inondation) sur toutes les polices touchées, dans une fenêtre de temps que la clause précise. Il couvre l'accumulation, pas le sinistre unitaire.

**Le stop-loss** couvre la **charge annuelle totale**, ou le rapport sinistres à primes, au-delà d'un seuil. Avec une prime de 4 500 et une garantie « 1 000 xs 3 500 », une année à 4 025 de sinistres coûte au réassureur $4\,025-3\,500=525$.

**Les clauses de limite annuelle et de réintégration.** Une tranche à portée $L$ ne peut pas être consommée sans fin. Un **plafond annuel** (*annual aggregate limit*) borne le total payé sur l'année, souvent à $(1+k)L$ où $k$ est le nombre de **réintégrations** : après un sinistre qui consomme une partie de la portée, la garantie est **reconstituée**, contre une **prime de réintégration**, généralement proportionnelle à la portée utilisée (*pro rata amount*).

Voyons-le sur la tranche « 500 xs 500 », de prime annuelle 300 (un montant d'exemple), avec **une** réintégration à 100 % pro rata du montant. Les trois sinistres touchent la tranche pour $100$, $400$ puis $500$. Les deux premiers consomment $500$ de portée au total, qui sont reconstitués : prime de réintégration $300\times100/500=60$, puis $300\times400/500=240$, soit **300**. Pour le troisième, la seule réintégration disponible est épuisée : il est payé (le plafond annuel est de $2\times500=1\,000$, atteint), mais ne donne pas lieu à reconstitution. Bilan de l'année : récupérations $1\,000$, coût de la protection $300+300=600$, **gain net 400**.


On exprime souvent le prix d'une tranche de deux façons. Le **taux de prime** divise la prime de la tranche par la **prime d'origine** de la cédante (la prime sur laquelle elle porte). Le **rate on line** (**ROL**) divise la prime par la **portée** $L$ ; son inverse, la **période de retour** (*payback*), est le nombre d'années de prime nécessaires pour payer une perte totale de la tranche. Un ROL de 5 % correspond à un *payback* de 20 ans : c'est le langage des tranches de catastrophe, rarement touchées.

| | Proportionnel | Non proportionnel |
|---|---|---|
| Partage | primes et sinistres, même proportion | les sinistres au-delà d'un seuil |
| Effet sur la variance | réduit l'échelle, pas la forme | **coupe la queue** |
| Prix | proportion de la prime d'origine (± commission) | tarifé selon l'exposition et l'expérience (6.2) |
| Intérêts | alignés : le réassureur suit la cédante | la cédante garde la fréquence ; le réassureur porte la sévérité |
| Usage typique | financer la croissance, alléger le capital | protéger contre les sinistres gros et les accumulations |

### 6.1.4 Lire un programme de réassurance

Une cédante achète rarement un seul traité. Elle empile des **couches** : une quote-part ou un petit excédent « de travail » en bas (on y est touché plusieurs fois par an), des excédents par risque au milieu, une couverture catastrophe en haut, parfois un stop-loss au sommet. La **rétention** est ce qui reste chez la cédante sous la première couche ; chaque couche est vendue à un ou plusieurs réassureurs qui se partagent la **ligne**.

Trois précautions à garder en mémoire quand on lit un programme.

**La définition de ce qui est couvert.** Un « événement » (une catastrophe) est défini par une période et une zone ; deux tempêtes à dix jours d'intervalle peuvent compter pour une ou pour deux. Les **exclusions** (guerre, risques nucléaires, cyber…) limitent la couverture réelle. Le **risque de base** (*basis risk*) est l'écart entre ce que la cédante subit et ce que le contrat paie.

**Le calendrier.** Un sinistre survenu en 2025 sera peut-être payé en 2029. Les récupérations de réassurance entrent donc dans le **provisionnement** (chapitre 2, section 2.3) : on provisionne les sinistres bruts **et** la part qui reviendra du réassureur.

**La solidité du réassureur.** La réassurance transforme un risque d'assurance en un **risque de contrepartie** : la créance sur le réassureur n'a de valeur que si celui-ci paie. Nous le chiffrerons en 6.3.4.

> ✅ **À retenir.** Un traité proportionnel partage tout au prorata et allège le capital ; un traité non proportionnel ne paie que les sinistres qui dépassent une priorité et coupe la queue de la distribution. La variance de la charge annuelle vient des gros sinistres : c'est là que la réassurance est la plus efficace. Une tranche se décrit par sa **priorité**, sa **portée**, ses **réintégrations** et son **plafond annuel**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.1 et 6.2, exercices 6.1 à 6.5.


## 6.2 Tarifer un traité

Combien doit coûter la tranche « 1 M€ xs 1 M€ » ? Le réassureur répond par une **prime pure** (la charge annuelle attendue de la tranche), puis par un **chargement** pour le risque et les frais. Cette section estime la prime pure de trois façons (l'expérience, la loi de queue, l'exposition), les compare à la **vérité programmée**, mesure l'incertitude de chacune, traite à part le cas des catastrophes, et passe enfin de la prime pure à la prime technique.

### 6.2.1 L'expérience : le *burning cost* et le piège de l'exposition

La méthode la plus naturelle demande : « **combien la tranche aurait-elle coûté, chaque année passée ?** ». On rejoue l'historique des sinistres à travers la tranche, année par année, et l'on fait la moyenne. C'est le **burning cost** (coût de la « combustion » passée de la tranche).

Pour que cette moyenne ait un sens, il faut ramener chaque année passée **à la situation de l'année couverte**. Trois corrections s'imposent :

1. **Développer** les sinistres récents, dont le montant final n'est pas connu (chapitre 2, sections 2.3 et 2.5). Dans nos données, les montants sont finaux ; en pratique, c'est une étape à part entière.
2. **Indexer** les montants passés au niveau de coût actuel (inflation des sinistres), **avant** d'appliquer la tranche, puisque la tranche s'applique à chaque sinistre au prix d'aujourd'hui.
3. **Ajuster l'exposition** : une année où le portefeuille était plus petit aurait produit plus de sinistres avec le portefeuille d'aujourd'hui.

Avec $C_t$ la charge de la tranche sur l'année $t$ et $E_t$ l'exposition de cette année (nombre de risques, primes, capitaux assurés…), le *burning cost* de l'année couverte $T$ est
$$\mathrm{BC}=\frac1n\sum_{t=1}^{n}C_t\cdot\frac{E_T}{E_t}.$$

Ici, le portefeuille croît de 3 % par an : l'exposition de 2025 vaut $1{,}03^{15}\approx1,56$ fois celle de 2010. Comparons le *burning cost* **brut** (sans correction) et **ajusté** de l'exposition, aux trois tranches « par risque » suivantes.

```python
for a, L in O.COUCHES:
    brut, _ = O.burning_cost(sg, a, L, ajuste=False)
    ajuste, _ = O.burning_cost(sg, a, L)
    print(f"{L/1e6:g} xs {a/1e6:g} : brut {brut/1e6:.2f} M€  ajusté {ajuste/1e6:.2f} M€  vérité {O.prix_vrai(a, L)/1e6:.2f} M€")
```
<!--sortie-->
```text
0.5 xs 0.5 : brut 3.19 M€  ajusté 4.07 M€  vérité 4.47 M€
1 xs 1 : brut 1.95 M€  ajusté 2.50 M€  vérité 2.63 M€
2 xs 2 : brut 0.78 M€  ajusté 1.01 M€  vérité 1.42 M€
```

Le *burning cost* brut sous-estime de 29, 26 et 45 % les trois tranches : il traite 2010 et 2024 comme si le portefeuille avait toujours eu la même taille. L'ajustement d'exposition supprime ce **biais** (il reste des écarts de -9 %, -5 % et -29 %, signes compris, qui relèvent du **bruit d'échantillonnage** que nous mesurerons en 6.2.4).

![Charge annuelle de chaque tranche, brute (gris) et ramenée à l'exposition 2025 (bleu). La ligne orange est la charge annuelle attendue réelle.](figures/ch06-burning.png)

La figure montre ce que cache la moyenne : la tranche haute (« 2 M€ xs 2 M€ ») a coûté **moins de 0,09 M€ par an de 2015 à 2021**, puis jusqu'à 2,1 M€ en 2024. Une tarification fondée sur la seule période calme aurait donné un prix dérisoire.

> ⚠️ **L'indexation est une hypothèse, pas une formalité.** L'inflation des sinistres s'**applique avant la tranche**, et la tranche **l'amplifie** : si tous les sinistres augmentent de 4 % par an, un sinistre de 900 000 € passe en dix ans à environ 1,33 M€, c'est-à-dire qu'il **entre** dans la tranche « 1 M€ xs 1 M€ » qu'il ne touchait pas. C'est l'**effet de levier de l'inflation sur les tranches**. Dans nos données, il n'y a **aucune** inflation de la sévérité : sur les sinistres de plus de 500 000 €, la pente du logarithme du montant selon l'année est de -0,41 % par an (statistiquement nulle). Si l'on avait indexé à 4 % par habitude, les trois tranches auraient été surestimées de 46, 73 et 86 % : une erreur de **+86 %** sur la tranche la plus haute. Le taux d'indexation doit être **estimé et justifié**, pas hérité.


> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : application 6.3 et exercices 6.6 et 6.7.

### 6.2.2 La tarification par l'exposition

Le *burning cost* exige un historique. Pour un **nouveau traité**, ou une tranche qui n'a jamais été touchée, on ne peut pas s'y fier. La **tarification par l'exposition** part d'une autre idée : au lieu d'observer ce que la tranche a coûté, on **décrit la répartition des sinistres** à l'aide d'une **courbe d'exposition**, et l'on en déduit la part de la charge totale qui tombe dans la tranche.

Soit $X$ un sinistre. La **courbe d'exposition** (ou *limited expected value* normalisée) est
$$G(d)=\frac{E[\min(X,d)]}{E[X]},$$
la **part de la charge attendue qui se situe sous le plafond $d$**. La charge attendue d'une tranche « $L$ xs $a$ » est alors
$$E\bigl[\min(\max(X-a,0),L)\bigr]=E[X]\,\bigl(G(a+L)-G(a)\bigr),$$
puisque $\min(\max(X-a,0),L)=\min(X,a+L)-\min(X,a)$. Multipliée par le nombre attendu de sinistres $\lambda$, elle donne la prime pure de la tranche. En pratique, on applique la courbe à **chaque risque de capital assuré $V_i$** (le plafond relatif est $d/V_i$), à l'aide de courbes publiées pour chaque type de risque : c'est ce qu'on fait pour les risques industriels, quand l'historique est mince.

Notre jeu de données n'a pas de capitaux assurés ; nous pouvons toutefois **estimer la courbe d'exposition à partir des sinistres eux-mêmes**, en euros.

| Plafond $d$ | 100 000 | 250 000 | 500 000 | 1 000 000 | 2 000 000 | 3 000 000 |
|---|---:|---:|---:|---:|---:|---:|
| $G(d)$ | 37,8 % | 56,9 % | 73,5 % | 87,7 % | 96,4 % | 99,3 % |

Lecture : 73,5 % de la charge attendue se situe sous 500 000 € par sinistre ; les **26,5 % restants** viennent des parties de sinistres au-delà de 500 000 €, et 12,3 % au-delà de 1 M€. La tranche « 1 M€ xs 1 M€ » reçoit donc $G(2\,\mathrm{M€})-G(1\,\mathrm{M€})=8,7$ % de la charge : en multipliant par la charge annuelle attendue (249 sinistres de moyenne 115 984 €), on trouve 2,52 M€, contre 2,63 M€ en vérité. Pour les trois tranches, cette approche « **fréquence × sévérité empirique** » donne 4,11, 2,52 et 1,00 M€.

#### Un exemple à la main avec une loi de Pareto

Supposons que les sinistres au-delà de 500 000 € soient au nombre de 15 par an et suivent une loi de Pareto de paramètre 2 : $P(X>x\mid X>u)=(u/x)^2$ avec $u=500\,000$. La charge annuelle attendue de la tranche « 1 M€ xs 1 M€ » est
$$15\int_{1\,000\,000}^{2\,000\,000}\Bigl(\frac{500\,000}{x}\Bigr)^2dx=15\times(500\,000)^2\Bigl(\frac1{1\,000\,000}-\frac1{2\,000\,000}\Bigr)=15\times125\,000=1\,875\,000\ \text{€}.$$
On voit le mécanisme : **tout repose sur la forme supposée de la queue**. Avec un exposant de 1,5 (queue plus lourde) la même tranche coûterait 3,11 M€ ; avec 3 (queue plus légère), 0,70 M€.


> 💡 **Deux méthodes, deux informations.** Le *burning cost* dit ce que la tranche **a coûté** ; l'exposition dit ce que la tranche **devrait coûter** si les sinistres se répartissent comme le suppose la courbe. Quand l'historique est riche, la première est plus honnête ; quand il est mince, la seconde est la seule disponible, et sa validité dépend de la courbe choisie.

### 6.2.3 Ajuster une loi de queue : la GPD

Le *burning cost* de la tranche haute repose sur très peu de sinistres. Pour mieux utiliser l'information, on **ajuste une loi** à la queue et l'on calcule la prime par une formule. La théorie des valeurs extrêmes (volume II, section 6.5) assure que les dépassements d'un seuil élevé $u$ suivent, sous des conditions générales, une **loi de Pareto généralisée** (GPD) :
$$P(X-u>y\mid X>u)=\Bigl(1+\xi\,\frac{y}{\beta}\Bigr)^{-1/\xi},\qquad y\ge0,$$
où $\xi$ est l'**indice de queue** (plus il est grand, plus la queue est lourde ; $\xi\ge1$ rend la moyenne infinie) et $\beta$ un paramètre d'échelle.

Pour un seuil $u$ et un nombre annuel $\lambda_u$ de dépassements, la prime pure d'une tranche « $L$ xs $a$ » avec $a\ge u$ est
$$\lambda_u\int_a^{a+L}\Bigl(1+\xi\,\frac{x-u}{\beta}\Bigr)^{-1/\xi}dx=\lambda_u\,\frac{\beta}{1-\xi}\Bigl[\Bigl(1+\xi\frac{a-u}{\beta}\Bigr)^{1-1/\xi}-\Bigl(1+\xi\frac{a+L-u}{\beta}\Bigr)^{1-1/\xi}\Bigr].$$

> 📐 **Pourquoi cette formule.** Pour un sinistre $X$, $\min(\max(X-a,0),L)=\int_a^{a+L}\mathbf 1\{X>x\}\,dx$. En prenant l'espérance (échange de l'intégrale et de l'espérance, théorème de Fubini) et en multipliant par le nombre annuel $\lambda$ de sinistres, la charge annuelle attendue vaut $\int_a^{a+L}\lambda P(X>x)\,dx$. Or, pour $x\ge u$, $\lambda P(X>x)=\lambda_u\,P(X>x\mid X>u)$, la survie de la GPD. Une primitive de $\bigl(1+\xi\frac{x-u}{\beta}\bigr)^{-1/\xi}$ est $-\frac{\beta}{1-\xi}\bigl(1+\xi\frac{x-u}{\beta}\bigr)^{1-1/\xi}$, d'où la formule.

Ajustons-la au seuil de 500 000 €, avec le nombre annuel de dépassements ramené à l'exposition de 2025.

```python
u = 5e5
exces = sg["montant"].values[sg["montant"].values > u] - u
xi, _, beta = stats.genpareto.fit(exces, floc=0)
lam_u = O.taux_depassement(sg, u)
print(f"n = {len(exces)}  xi = {xi:.3f}  beta = {beta:,.0f}  lambda_u = {lam_u:.1f} par an")
```
<!--sortie-->
```text
n = 177  xi = 0.416  beta = 312,975  lambda_u = 15.0 par an
```

On obtient $\hat\xi=0,416$ et $\hat\beta=312 975$ € sur 177 dépassements, soit 15,0 par an au niveau 2025. Les prix de la formule sont de 4,11, 2,21 et 1,02 M€ pour les trois tranches.

> ⚠️ **Le choix du seuil est un choix de modèle.** Si $u$ est trop bas, la loi ne suit plus la GPD (on y mêle le corps de la distribution) ; trop haut, il reste trop peu de points. On regarde la **stabilité** de $\hat\xi$ quand $u$ varie. La figure ci-dessous le montre : $\hat\xi$ vaut 0,22 au seuil de 300 000 €, 0,42 à 500 000 €, et -0,15 à 1 M€, où il devient **négatif** (une queue qui « s'arrête ») alors que nous savons que la vraie queue est très lourde ($\xi=0{,}55$). À ce seuil, il ne reste que 49 dépassements : la bande d'incertitude de $\hat\xi$ est large, et le résultat n'est pas fiable.

![À gauche, l'excès moyen au-delà d'un seuil ; à droite, l'estimation de l'indice de queue selon le seuil, avec sa bande d'incertitude.](figures/ch06-gpd.png)

Le prix de la tranche la plus haute dépend de ce choix. Avec les seuils de 300 000 €, de 500 000 € et de 1 M€, le prix de « 2 M€ xs 2 M€ » vaut respectivement 0,83, 1,02 et 0,93 M€, alors que la vérité est de 1,42 M€. **Aucun** de ces chiffres n'est faux au sens du calcul : ils reflètent l'incertitude du modèle, qu'il faut annoncer plutôt que cacher.


Mettons toutes les estimations côte à côte, en M€ par an au niveau de 2025.

| Tranche | *Burning cost* brut | *Burning cost* ajusté | Fréquence × sévérité | GPD (seuil 500 000) | **Vérité** |
|---|---:|---:|---:|---:|---:|
| 0,5 M€ xs 0,5 M€ | 3,19 | 4,07 | 4,11 | 4,11 | **4,47** |
| 1 M€ xs 1 M€ | 1,95 | 2,50 | 2,52 | 2,21 | **2,63** |
| 2 M€ xs 2 M€ | 0,78 | 1,01 | 1,00 | 1,02 | **1,42** |

Trois remarques. La correction d'exposition est **indispensable** : le brut est loin de tout le reste. Les trois estimations corrigées sont **voisines** entre elles : elles utilisent les mêmes données, donc partagent les mêmes aléas. Et elles sont **toutes en dessous** de la vérité sur la tranche haute. Est-ce un biais de méthode ou la malchance de ces quinze années ? C'est la question de la section suivante.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.4 et 6.5 et exercices 6.8 à 6.10.

### 6.2.4 Mesurer l'incertitude : le même tarif aurait pu être très différent

Nos quinze années d'observation sont **un tirage parmi beaucoup d'autres possibles**. Pour mesurer l'incertitude d'une estimation, on veut savoir ce qu'elle serait sur d'autres tirages. On en a deux moyens.

**Le bootstrap par années.** On rééchantillonne les **années** (avec remise) : chaque année est une observation de la charge annuelle de la tranche. On refait le calcul du *burning cost* sur chaque rééchantillon, et l'on lit un intervalle de 2,5 % à 97,5 %. On rééchantillonne des années entières et non des sinistres, parce que les sinistres d'une même année partagent la même exposition. Voici l'intervalle pour les trois tranches :

| Tranche | Estimation ajustée | Intervalle à 95 % (bootstrap) | Largeur relative |
|---|---:|---|---:|
| 0,5 M€ xs 0,5 M€ | 4,07 M€ | de 3,45 à 4,65 | ± 15 % |
| 1 M€ xs 1 M€ | 2,50 M€ | de 1,77 à 3,20 | ± 29 % |
| 2 M€ xs 2 M€ | 1,01 M€ | de 0,56 à 1,54 | ± 49 % |

L'incertitude **grandit à mesure que l'on monte**, parce que la tranche haute est touchée par peu de sinistres : dans l'historique, seuls 15 sinistres dépassent 2 M€. La vérité, qui reste dans les trois intervalles ici, n'y serait pas **forcément** : « 95 % » n'est pas « toujours ».

**Rejouer l'expérience sous la vérité.** Puisque nous connaissons la loi qui a produit les données, nous pouvons refaire **300 fois** l'aventure « quinze années d'observation », calculer chaque fois le *burning cost* ajusté, et regarder la dispersion. C'est un luxe de simulation : en vrai, on n'a qu'une histoire.

| Tranche | Moyenne des 300 estimations | Coefficient de variation | Part des estimations sous la vérité |
|---|---:|---:|---:|
| 0,5 M€ xs 0,5 M€ | 4,46 M€ | 8 % | 51 % |
| 1 M€ xs 1 M€ | 2,63 M€ | 16 % | 50 % |
| 2 M€ xs 2 M€ | 1,42 M€ | 31 % | 51 % |

La moyenne des estimations est **voisine de la vérité** : la méthode corrigée de l'exposition n'est pas biaisée. Mais son **erreur typique** est de 8 %, 16 % et 31 % : une erreur de -29 % sur la tranche haute (celle de notre échantillon) est donc banale, de l'ordre d'un écart-type. Le réassureur et la cédante qui s'accordent sur le prix de la tranche haute se mettent d'accord sur un chiffre dont l'incertitude est **du même ordre que le chargement qu'ils négocient**.

![Estimations de la charge annuelle de chaque tranche : *burning cost* brut (gris), ajusté avec son intervalle bootstrap (bleu), GPD (violet). La ligne orange est la vérité.](figures/ch06-tranches.png)


> 💡 **Une prime est une estimation.** Le « prix » d'une tranche haute est, avec 15 ans de données, une fourchette large. Les réassureurs le savent : c'est pourquoi les tranches hautes se tarifient avec des **modèles**, des **hypothèses prudentes** et des **chargements**, et pas avec la seule moyenne observée.

### 6.2.5 Les catastrophes : peu de données, beaucoup d'incertitude

Pour les catastrophes, l'historique est encore plus mince : **17 événements en 40 ans**. Le tarif d'une tranche de catastrophe repose sur le **modèle de queue** presque seul.

Nous ajustons une loi de Pareto $P(X>x)=(x_m/x)^{\alpha}$ aux pertes des années à événement, avec un minimum $x_m=2$ M€ (la plus petite perte observée vaut 2,11 M€). L'estimateur du maximum de vraisemblance de $\alpha$ est $\hat\alpha=n/\sum\ln(x_i/x_m)$, soit ici 1,33, et la fréquence des années à événement vaut 42,5 %. Le tableau compare l'estimation empirique, la loi ajustée et la vérité, pour trois tranches.

| Tranche | Empirique | Pareto ajusté | Vérité | Intervalle bootstrap |
|---|---:|---:|---:|---|
| 5 M€ xs 5 M€ | 0,46 | 0,39 | **0,54** | 0,11 à 0,89 |
| 10 M€ xs 10 M€ | 0,26 | 0,31 | **0,50** | 0,00 à 0,79 |
| 20 M€ xs 20 M€ | 0,39 | 0,24 | **0,46** | 0,00 à 1,17 |

L'intervalle de la tranche « 10 M€ xs 10 M€ » commence à **zéro** : certains rééchantillonnages de 40 ans n'ont aucune perte dans la tranche. Sur 40 ans, la loi ajustée sous-estime la queue ($\hat\alpha=1,33$ contre une vérité de 1,11) : l'exposant est surestimé, la queue paraît plus légère, les tranches hautes sont sous-tarifées, et la méthode empirique se trompe dans le même sens. Avec 17 points, un écart de cette taille est banal : **les observations de pertes extrêmes sont rares par nature**, et un échantillon court ne contient en général pas la pire perte possible.

![À gauche, la queue des pertes d'événement (échelle logarithmique) : observations, loi ajustée et vérité. À droite, la charge annuelle de trois tranches de catastrophe selon la méthode.](figures/ch06-cat.png)

Pour une tranche de catastrophe, on parle plutôt en **ROL** qu'en pourcentage de prime. Si la tranche « 10 M€ xs 10 M€ » est vendue à son prix pur de 0,50 M€, son ROL est de 5,0 %, soit une période de retour de 20 ans : pendant ce temps, la cédante paie chaque année, et ne récupère l'équivalent d'une portée entière, en moyenne, qu'une fois en 20 ans. Le réassureur n'a guère plus d'information que nous : il s'appuie sur des **modèles de catastrophe** (physiques ou statistiques), hors du champ de cet ouvrage.


> ⚠️ **Quand les données manquent, le chargement n'est pas un luxe.** Une tranche de catastrophe dont l'espérance est connue à un facteur deux près se vend nécessairement avec un chargement important : il rémunère l'incertitude du réassureur autant que son risque.

### 6.2.6 De la prime pure à la prime technique

La prime pure est l'espérance de la charge. Le prix facturé par le réassureur, la **prime technique**, ajoute un **chargement** qui couvre les frais, le coût du capital et la marge. Deux principes classiques, tous deux **illustratifs** ici (les paramètres sont ceux d'un exemple, pas ceux d'un marché) :

- **Le principe de l'écart-type** : $\pi=E[S]+k\,\sigma(S)$, où $S$ est la charge annuelle de la tranche et $k$ un coefficient d'aversion (nous prenons $k=0{,}15$).
- **Le principe du coût du capital** : le réassureur immobilise un capital $K$ pour porter le risque (la perte inattendue à 99,5 %, $K=\mathrm{VaR}_{99{,}5\,\%}(S)-E[S]$, voir section 3.1) et exige un rendement de $i$ sur ce capital : $\pi=E[S]+i\,K$ (nous prenons $i=8\,\%$).

Pour les calculer, il faut la **distribution** de la charge annuelle de la tranche, pas seulement sa moyenne. Nous la simulons (20 000 années, nombre de sinistres de Poisson, montants tirés sous la loi des sinistres) :

| Tranche | Espérance | Écart-type | VaR à 99,5 % | Capital $K$ | Prime (écart-type) | Prime (coût du capital) |
|---|---:|---:|---:|---:|---:|---:|
| 1 M€ xs 1 M€ | 2,61 M€ | 1,43 M€ | 7,04 M€ | 4,43 M€ | 2,82 M€ (+8 %) | 2,96 M€ (+14 %) |
| 2 M€ xs 2 M€ | 1,42 M€ | 1,49 M€ | 6,45 M€ | 5,03 M€ | 1,64 M€ (+16 %) | 1,82 M€ (+28 %) |

Plus la tranche est haute, plus le **risque relatif** est grand (l'écart-type est supérieur à l'espérance pour la tranche « 2 M€ xs 2 M€ »), donc plus le chargement relatif l'est aussi. Un chargement unique, exprimé en pourcentage de la prime pure, ne peut pas convenir aux deux tranches : il faut ajouter 8 % à la première et 16 % à la seconde avec le principe de l'écart-type, ou 14 % et 28 % avec le coût du capital. Le chargement suit le **risque**, pas la prime.

Reste le coût des **réintégrations** et d'éventuelles **commissions** de courtage, qui s'ajoutent à la prime technique. Le prix final n'est donc pas une simple « moyenne plus dix pour cent » : c'est un compromis entre le modèle du réassureur, son appétit, son capital disponible et la concurrence du moment.


> ✅ **À retenir.** La prime pure d'une tranche s'estime par l'expérience (*burning cost*, **à ajuster de l'exposition et de l'inflation**, qui s'amplifie dans les tranches), par une loi de queue (GPD), ou par l'exposition (courbe d'exposition) ; ces méthodes se comparent mais partagent les mêmes données. Pour les tranches hautes et les catastrophes, l'incertitude est **du même ordre que le chargement** : il faut la mesurer (bootstrap) et l'annoncer. La prime technique ajoute un chargement proportionnel au **risque** (écart-type, coût du capital), pas à la prime pure.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.3 à 6.8, exercices 6.6 à 6.12.


## 6.3 Choisir une couverture

Savoir tarifer une tranche ne dit pas s'il faut l'acheter. Cette section se place du côté de la **cédante** : elle simule la charge annuelle, mesure ce que chaque programme de réassurance retire de la volatilité et du capital, et le compare à son coût. Elle termine par ce qui peut mal tourner : un réassureur qui ne paie pas, une garantie épuisée, un prix qui semble trop beau.

### 6.3.1 Le modèle de la cédante

Pour comparer des programmes, il faut un **modèle du résultat annuel** de la cédante. Le nôtre est volontairement simple :

- le nombre de sinistres de l'année suit une loi de Poisson de moyenne 249 (niveau d'exposition de 2025) ;
- chaque montant est tiré avec remise parmi les sinistres observés (nous reprenons la loi **empirique**, pas la vérité) ;
- la prime d'origine $P$ est fixée pour que la sinistralité attendue soit de **70 %** de $P$, les frais de **25 %** et la marge attendue de **5 %** ;
- le résultat annuel brut est $R=0{,}75\,P-S$, où $S$ est la charge annuelle brute.

Nous mesurons un programme par quatre grandeurs : la **moyenne** et l'**écart-type** du résultat, la **probabilité de ruine** (un résultat inférieur à $-C_0$ avec un capital de départ $C_0=8$ M€), et la **perte inattendue** $K=E[R]-q_{0{,}5\,\%}(R)$, le capital qu'il faut détenir pour absorber une année à 1 chance sur 200. $K$ est une version simplifiée du capital réglementaire (VaR à 99,5 % sur un an, section 4.2) ; la VaR et l'*expected shortfall* sont détaillées en section 3.1.

```python
simu = O.simuler(N=20000, seed=2026)          # 20 000 années au niveau d'exposition 2025
prime = simu["brute"].mean() / 0.70           # sinistres 70 %, frais 25 %, marge 5 %
resultat_brut = 0.75 * prime - simu["brute"]  # prime nette de frais, moins les sinistres
K0 = resultat_brut.mean() - np.percentile(resultat_brut, 0.5)
print(f"prime {prime/1e6:.1f} M€  résultat moyen {resultat_brut.mean()/1e6:.2f}  écart-type {resultat_brut.std()/1e6:.2f}  K {K0/1e6:.1f}")
```
<!--sortie-->
```text
prime 41.3 M€  résultat moyen 2.06  écart-type 4.95  K 14.3
```

La prime d'origine est de 41,3 M€ ; le résultat moyen est de 2,06 M€ (5 % de la prime), avec un écart-type de 4,95 M€, soit **plus de deux fois le résultat attendu** : une année sur trois environ est déficitaire. Une année sur 200, le résultat tombe à -12,2 M€ : $K=14,3$ M€. Avec un capital de 8 M€, la probabilité de ruine à un an vaut 3,0 %.

> ⚠️ **Limites du modèle.** Les sinistres sont tirés **parmi ceux déjà observés** : une année simulée ne peut pas contenir un sinistre plus gros que le plus gros observé (4 310 320 €). La queue est donc **tronquée**, et les capitaux ci-dessous sont des **minima**. Nous ne simulons pas non plus d'événement catastrophique dans cette étape (il fait l'objet de 6.3.3).

### 6.3.2 Comparer des programmes

Cinq programmes sont comparés au cas sans réassurance. Les prix sont des **hypothèses d'exemple**, pas des cotations : pour les excédents de sinistre, la prime est l'espérance simulée des récupérations multipliée par $1+$ un chargement ; pour la quote-part, la prime cédée est 20 % de $P$ et la commission de cession est de 25 % de la prime cédée (elle couvre les frais, cf. 6.1.2).

| Programme | Chargement | Coût annuel | Écart-type | $K$ | Capital économisé | Coût par € économisé | Ruine à 8 M€ |
|---|---:|---:|---:|---:|---:|---:|---:|
| Aucun | | | 4,95 M€ | 14,25 M€ | | | 3,0 % |
| XL 0,5 M€ xs 0,5 M€ | 30 % | 1,23 M€ | 3,89 M€ | 11,35 M€ | 2,90 M€ | 0,42 | 2,0 % |
| XL 1 M€ xs 1 M€ | 35 % | 0,88 M€ | 3,92 M€ | 11,25 M€ | 3,00 M€ | 0,29 | 1,5 % |
| XL 2 M€ xs 2 M€ | 50 % | 0,50 M€ | 4,38 M€ | 12,44 M€ | 1,82 M€ | 0,27 | 2,0 % |
| Quote-part 20 % | commission 25 % | 0,41 M€ | 3,96 M€ | 11,40 M€ | 2,85 M€ | 0,14 | 1,3 % |
| Stop-loss 10 M€ xs 38 M€ | 40 % | 0,04 M€ | 4,70 M€ | 9,22 M€ | 5,03 M€ | 0,008 | 0,0 % |

Le **coût annuel** est la prime payée moins les récupérations attendues : c'est la **marge du réassureur**, ce que la cédante abandonne en moyenne pour réduire son risque. Le **coût par euro économisé** divise ce coût par le capital libéré ($K$ sans réassurance moins $K$ avec).

![À gauche, la distribution du résultat annuel sans réassurance et avec trois programmes. À droite, le coût de chaque programme et le capital qu'il économise ; la droite en pointillé marque le point d'équilibre pour un coût du capital de 8 %.](figures/ch06-programmes.png)

La lecture est instructive.

**Les tranches « de travail » coûtent cher pour ce qu'elles font.** « 0,5 M€ xs 0,5 M€ » est touchée une quinzaine de fois par an : la cédante paie une prime de 5,3 M€ pour récupérer 4,1 M€ en moyenne, c'est-à-dire un échange presque certain d'argent contre de l'argent, **moins** un chargement de 1,23 M€. Elle libère 2,9 M€ de capital, soit 0,42 € de coût par euro économisé.

**La quote-part est la moins chère des protections « générales »**, parce que la commission de cession de 25 % rembourse exactement les frais de la cédante : le coût ne vient que de l'écart entre la marge de la cédante et celle du réassureur. Elle réduit le risque dans la même proportion que la cession (20 %), mais ne cible pas la queue.

**Le stop-loss est de loin le plus efficace par euro**, parce qu'il ne protège que l'extrême (il se déclenche dans 4,1 % des années), exactement là où se situe $K$. Mais il est aussi le plus **fragile** : son prix repose sur la queue de la distribution, que nous connaissons le moins bien (6.2.4), et un réassureur le vend rarement à un chargement aussi bas que les 40 % supposés.

Les écarts entre programmes voisins doivent être lus avec prudence. Avec 20 000 années simulées, le quantile à 0,5 % repose sur 100 années ; son erreur-type, estimée par bootstrap, est de 0,30 M€. Une différence de $K$ de quelques dixièmes de M€ n'est pas significative.


#### Combien faudrait-il que la protection coûte ?

Si la cédante raisonne **uniquement** en coût du capital (un euro de capital immobilisé lui coûte 8 % par an), une protection vaut son prix quand $\text{coût}\le 8\,\%\times\text{capital libéré}$. Pour les trois excédents de sinistre, cela correspond à des chargements d'**équilibre** de 6 %, 10 % et 15 % de la prime pure, très inférieurs aux chargements supposés (30 %, 35 %, 50 %). **Au seul coût du capital, ces tranches ne se paient pas.** Alors pourquoi en acheter ?

Parce que le coût du capital n'est pas la seule raison. La cédante achète aussi :

- de la **stabilité** (l'écart-type du résultat) : la cédante cotée, la mutuelle qui fait face à ses adhérents, l'entreprise qui doit verser des dividendes réguliers valorisent un résultat moins volatil ;
- le respect d'une **contrainte** : un ratio de solvabilité à tenir (section 4.2), une notation à préserver, une probabilité de ruine à ne pas dépasser (la colonne « ruine » du tableau) ; dans ce cas, c'est la **contrainte** qui fixe le besoin de réassurance, et le coût est le prix de la conformité ;
- de la **capacité** pour souscrire des risques plus gros, dont la marge compense le coût.

> 💡 **Un programme se juge sur un tableau, pas sur un chiffre.** Le coût, la volatilité, le capital, la ruine : on regarde les quatre, et l'on décide selon ce qui contraint réellement la cédante. Un programme qui économise beaucoup de capital pour un coût élevé n'est « bon » que si le capital est effectivement rare.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : application 6.9 et exercices 6.9 à 6.12.

### 6.3.3 Et la catastrophe ?

Ajoutons maintenant la perte annuelle liée aux événements catastrophiques. Nous la tirons de **trois façons**, que nous avons déjà rencontrées en 6.2.5 : par tirage avec remise parmi les 40 années **observées**, par la loi de **Pareto ajustée** ($\hat\alpha=1,33$), et sous la **vérité** ($\alpha=1{,}11$).

Le réassureur propose une **tour** de trois tranches : 5 M€ xs 5 M€, 10 M€ xs 10 M€ et 20 M€ xs 20 M€, qui couvre les pertes d'événement jusqu'à 40 M€. Nous supposons que son prix vaut **1,5 fois l'espérance sous la vérité** (le réassureur dispose de modèles de catastrophe) : 2,26 M€ par an. La cédante, elle, juge l'intérêt de la tour avec **son** modèle de la catastrophe.

| Vue de la cédante sur la catastrophe | Perte cat. moyenne | Perte cat. à 99,5 % | $K$ sans tour | $K$ avec tour | Capital économisé | Coût par € économisé |
|---|---:|---:|---:|---:|---:|---:|
| Années observées (rééchantillonnage) | 2,7 M€ | 35,6 M€ | 37,1 M€ | 15,1 M€ | 22,0 M€ | 0,05 |
| Pareto ajusté | 2,8 M€ | 47,2 M€ | 44,7 M€ | 18,2 M€ | 26,6 M€ | 0,05 |
| **Vérité programmée** | 5,7 M€ | 114,2 M€ | 108,0 M€ | 74,5 M€ | 33,5 M€ | 0,02 |

Trois constats. D'abord, la **catastrophe domine tout** : avec elle, $K$ passe de 14,3 M€ à 37,1 M€ dès la vue la plus optimiste, soit presque le niveau de la prime (41,3 M€) : la cédante de l'exemple **ne peut pas porter** ce risque sans réassurance. Ensuite, **la vue de la cédante change la valeur de la tour** : avec les seules années observées, la tour semble coûter 0,05 € par euro de capital libéré ; avec la vérité, 0,02 €. Les données courtes rendent la protection **moins attrayante qu'elle ne l'est**, parce qu'elles sous-estiment la queue (6.2.5). Enfin, même avec une tour jusqu'à 40 M€, le capital restant est de 74,5 M€ sous la vérité : **au-delà de 40 M€, la cédante porte tout**, et un seul événement de 100 M€ suffit à ruiner le portefeuille. Une tour se dimensionne sur ce que l'on est prêt à perdre, pas sur ce que les données montrent.


### 6.3.4 Contrepartie, épuisement et prix trop bas

La réassurance déplace le risque ; elle ne le supprime pas. Trois fragilités méritent un chiffre.

#### Le risque de contrepartie

Une créance sur un réassureur n'a de valeur que si celui-ci paie. Simulons le **stop-loss** du tableau précédent dans trois mondes : un réassureur **toujours solvable** ; un réassureur qui fait défaut avec une probabilité de 0,5 % par an, **indépendamment** des sinistres, et ne paie alors que la moitié des récupérations ; et un réassureur qui fait défaut avec une probabilité de 10 % **précisément les années où la charge brute dépasse son 99ᵉ centile** (un défaut lié à un événement majeur, qui frappe souvent plusieurs cédantes à la fois).

| Monde | Probabilité de ruine à 8 M€ |
|---|---:|
| Aucune réassurance | 2,98 % |
| Réassureur toujours solvable | 0,04 % |
| Défaut indépendant (0,5 % par an) | 0,05 % |
| Défaut lié aux gros sinistres (10 % dans le 1 % pire) | 0,14 % |

Un défaut **indépendant** change peu le résultat (la ruine reste proche de 0,05 %). Un défaut **corrélé aux sinistres** (0,14 %) multiplie la probabilité de ruine par 3,2 par rapport au cas parfait : le réassureur manque **quand on a le plus besoin de lui**. C'est le **risque de corrélation défavorable** (*wrong-way risk*). Les parades sont la **diversification** des réassureurs, une exigence de **notation** minimale, le **nantissement** de garanties et des clauses de résiliation en cas de dégradation.

#### L'épuisement de la garantie

Revenons à la tranche « 2 M€ xs 2 M€ ». Si on la vend avec une **réintégration** (plafond annuel de 4 M€, soit deux portées), la charge annuelle de la tranche atteint ce plafond dans 7,7 % des années. Sans réintégration (plafond de 2 M€), la garantie s'épuise dans 36,6 % des années, et **la part des pertes attendues qui n'est pas couverte** vaut 26 % de l'espérance : le plafond annuel retire du prix de la tranche ce qu'il retire de la couverture.

#### Le prix trop bas

Une offre de réassurance moins chère que les autres peut être une bonne affaire ou un risque caché. Les points de contrôle sont toujours les mêmes :

> ⚠️ **Quand le prix est trop beau, cherchez où le risque est passé.**
> 1. **Un plafond annuel trop bas** : sans réintégration, la tranche « 2 M€ xs 2 M€ » ne couvre que 74 % de l'espérance de pertes ; comparez son prix à celui d'une tranche réintégrable.
> 2. **Une définition étroite de l'événement** (durée trop courte, zone restreinte) : la tranche ne se déclenche pas quand la cédante en a besoin.
> 3. **Des exclusions** non chiffrées, qui retirent du champ les scénarios coûteux.
> 4. **Une notation faible** du réassureur, ou un portefeuille de réassureurs trop concentré : le risque de contrepartie.
> 5. **Un prix de cycle** : en marché mou, le prix baisse sous le niveau durable, puis remonte brutalement ; ce qui est bon marché cette année est cher à renouveler.
> 6. **Un risque de base** : l'indice déclencheur ne suit pas les pertes réelles de la cédante.


### 6.3.5 Une méthode pour décider

> 🧭 **En pratique : choisir une couverture.**
> 1. **Formuler ce qui contraint** : ratio de solvabilité, probabilité de ruine acceptable, volatilité du résultat, capacité de souscription. Sans contrainte claire, le coût du capital seul conclut presque toujours « ne pas réassurer ».
> 2. **Modéliser la charge annuelle brute** (fréquence × sévérité, catastrophes à part) et dire ce que le modèle ne sait pas faire (queue tronquée, peu d'observations).
> 3. **Chiffrer chaque programme** : coût attendu, écart-type, capital économisé, ruine, **coût par euro de capital économisé**.
> 4. **Éprouver la sensibilité** : à la queue (vue observée contre ajustée), au chargement, au seuil, à l'exposition future.
> 5. **Regarder la contrepartie** : notation, concentration, corrélation avec les sinistres.
> 6. **Lire les clauses** : priorité par rapport au capital (si la priorité dépasse ce que le capital peut absorber, la cédante est ruinée avant que la garantie ne joue), plafonds, réintégrations, définitions.
> 7. **Réévaluer chaque année** : l'exposition croît, les prix de marché varient, les modèles vieillissent (section 3.4 pour la validation de ces modèles).

> ✅ **À retenir.** Un programme de réassurance se juge sur **quatre axes** : coût, volatilité, capital, contrainte. Au seul coût du capital, les tranches basses se paient rarement ; la réassurance vaut par la **contrainte** qu'elle permet de tenir. Les données courtes **sous-estiment la queue** : la valeur de la protection catastrophe est plus grande que ne le disent les observations. Un réassureur est une **contrepartie** (surtout si son défaut est corrélé aux sinistres), et un plafond annuel bas retire à la couverture ce qu'il retire au prix.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.9 et 6.10, exercices 6.9 à 6.12.


## Bilan du chapitre 6

Vous savez maintenant :

- **expliquer** pourquoi une cédante réassure : non pour réduire son coût moyen, mais pour **stabiliser** son résultat, gagner de la **capacité** et **économiser du capital** ; et pourquoi la variance de la charge annuelle vient des gros sinistres, que la mutualisation ne diminue pas (17,1 % de coefficient de variation brut, 11,7 % une fois les sinistres plafonnés à 500 000 €) ;
- **distinguer** les traités **proportionnels** (quote-part, excédent de plénitude : mêmes proportions de primes et de sinistres) des traités **non proportionnels** (excédent de sinistre « portée xs priorité », par événement, stop-loss), calculer à la main ce que chacun cède sur huit sinistres (1 207,5, 2 560 et 1 000 sur 4 025), et lire les **réintégrations**, le **plafond annuel**, le **taux de prime** et le **ROL** ;
- **estimer** la prime pure d'une tranche par le *burning cost* (à **ajuster de l'exposition et de l'inflation**), par une loi de queue **GPD** (avec sa formule fermée) et par l'**exposition** (courbe $G(d)$) ;
- **mesurer l'incertitude** par le bootstrap par années, et savoir que l'erreur typique d'un tarif à quinze ans d'historique est de 8 %, 16 % et 31 % pour trois tranches de plus en plus hautes ;
- **traiter** les catastrophes avec peu de données (une loi de Pareto ajustée sur 17 événements, des tranches dont l'espérance est incertaine à un facteur deux), et passer de la prime pure à la **prime technique** (écart-type, coût du capital) ;
- **comparer** des programmes sur quatre axes (coût, volatilité, capital, ruine) par le **coût d'un euro de capital économisé**, évaluer l'effet d'une tour de catastrophe selon la vue que l'on a de la queue, et chiffrer le **risque de contrepartie** et l'**épuisement** d'une garantie.

Le chapitre a mis des chiffres sur des idées souvent qualitatives.

| Ce que l'on a vu | Résultat mesuré |
|---|---|
| *Burning cost* brut contre ajusté de l'exposition | sous-estimation de 29 à 45 % sans ajustement |
| Indexation de 4 % par habitude, alors que la sévérité est stable | tranches surestimées de 46 à 86 % |
| GPD sur le seuil de 1 M€ | $\hat\xi=-0,15$ (vérité 0,55) : seuil trop haut, trop peu de points |
| Bootstrap sur la tranche 2 M€ xs 2 M€ | intervalle à 95 % de 0,56 à 1,54 M€ (vérité 1,42) |
| Catastrophes : $\hat\alpha$ sur 17 événements | 1,33 contre 1,11 en vérité |
| Coût par euro de capital économisé | stop-loss 0,008 ; quote-part 0,14 ; excédents de sinistre de 0,27 à 0,42 |
| Défaut du réassureur lié aux gros sinistres | probabilité de ruine multipliée par 3,2 |

Le fil conducteur du chapitre tient en une phrase : **le prix d'une protection est une estimation incertaine d'un risque rare, et sa valeur dépend de ce qui contraint la cédante**. L'incertitude du tarif est de l'ordre de grandeur du chargement que l'on négocie ; les données courtes sous-estiment la queue ; la couverture n'est jamais plus solide que le contrat et que le réassureur.

> ⚠️ **Rappel d'honnêteté.** Les sinistres et les catastrophes sont **simulés** : nous avons pu comparer les estimations à la vérité, ce que personne ne peut faire en pratique. Les chargements, le coût du capital (8 %), la structure de frais (25 %) et les prix des programmes sont des **hypothèses d'exemple**, pas des conditions de marché. Les modèles de catastrophe, la modélisation de la dépendance entre branches, et le traitement comptable et prudentiel de la réassurance dépassent ce chapitre.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.1 à 6.10 (répartir huit sinistres entre trois traités, coefficient de variation selon la rétention, *burning cost*, courbe d'exposition, GPD, bootstrap, tranche de catastrophe, prime de risque, comparaison de programmes, contrepartie et épuisement) et exercices 6.1 à 6.12.

Le chapitre 7 change de sujet : il relie ce que l'on **doit** (le passif d'un assureur) à ce que l'on **détient** (ses placements), avec la gestion actif-passif et la théorie du portefeuille.


---

# Chapitre 7 : ➕ Gestion actif-passif et théorie du portefeuille

> « Une assurance vendue aujourd'hui est une promesse payable dans vingt ans. Le risque n'est pas dans la promesse, ni dans les placements : il est dans l'écart entre les deux. »

> 🧭 **Chapitre complémentaire.** Ce chapitre est facultatif : les chapitres 1 à 4 se lisent sans lui. Il s'adresse à celles et ceux qui devront **décider comment placer les primes encaissées** (en assurance) ou **comment financer des prêts avec des dépôts** (en banque). Il suppose les notions de rendement, de variance et de covariance (volume I) et reprend les mesures de risque du chapitre 3 (VaR et expected shortfall, section 3.1).

Les chapitres précédents ont chiffré des risques **un par un** : la probabilité de défaut d'un emprunteur (chapitre 1), le coût des sinistres d'un portefeuille (chapitre 2), la perte maximale d'un jeu de positions (chapitre 3), le capital que le régulateur exige (chapitre 4), la mortalité d'une génération (chapitre 5), le coût d'une protection (chapitre 6). Reste la question que se pose la direction financière une fois tous ces chiffres posés : **avec quoi la mutuelle (ou la banque) paiera-t-elle ce qu'elle a promis, et que se passe-t-il si les marchés bougent ?**

Cette question a deux visages. Le premier est celui de l'**actif-passif** (*asset-liability management*, ALM) : les promesses faites aux assurés ou aux déposants forment un **passif**, c'est-à-dire un échéancier de paiements futurs ; les placements forment l'**actif**. Quand les taux d'intérêt changent, les deux ne se déplacent pas de la même quantité, et c'est leur **différence**, le surplus, qui absorbe le choc. Le second visage est celui de la **théorie du portefeuille** : étant donné des actifs aux rendements incertains et corrélés, comment répartir un capital entre eux pour obtenir le meilleur compromis entre rendement attendu et risque ? Le chapitre commence par le premier, puis passe au second, puis les réunit.

## Le chemin de ce chapitre

- **7.1 Gestion actif-passif** : le bilan comme deux échéanciers, la valeur actuelle, la **duration** et la **convexité** (avec leur démonstration), la construction du **passif d'un portefeuille d'assurance vie** à partir de tables de mortalité, l'**écart de duration**, l'**immunisation** et ses conditions, les chocs de courbe qui ne sont pas parallèles, l'échéancier de refixation d'une banque, et ce que l'histoire (simulée) des taux aurait fait au surplus.
- **7.2 Théorie du portefeuille** : rendement et risque d'un portefeuille (formules matricielles), la **frontière efficiente** à deux puis à cinq actifs, le portefeuille de variance minimale, le ratio de Sharpe, les **contributions au risque**, l'idée du CAPM, la fragilité des estimations (rendements, covariances, rétrécissement) et ce que devient la diversification **en période de stress**.
- **7.3 De la frontière efficiente à l'actif-passif** : le **surplus** comme objet à optimiser, l'allocation sous contrainte de duration, la **VaR et l'expected shortfall du surplus**, une simulation sur dix ans du taux de couverture, et les limites de tout ce qui précède.
- **Bilan du chapitre.**

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : huit applications (prix et duration d'une obligation, passif d'un portefeuille vie, appariement, chocs de courbe, frontière efficiente, contributions au risque, estimation et rétrécissement, surplus et simulation) et douze exercices corrigés.

## Les données du chapitre

> 📦 **Données (toutes simulées).** `courbe_taux.csv` : 120 mois de courbes des taux zéro-coupon à neuf maturités (de 3 mois à 30 ans). `rendements_marche.csv` : 4 000 jours de rendements de cinq classes d'actifs (deux actions, obligations, immobilier, matières premières) et `marche_verite.csv`, le régime vrai (calme ou stress) de chaque jour, que l'on **ne connaît pas** dans la réalité. `portefeuille_vie.csv` : 20 000 contrats d'assurance vie observés de 2015 à 2019, et `mortalite_population.csv`, la mortalité de la population par sexe et par âge, qui sert à bâtir la table de mortalité.

Trois précautions, à garder à l'esprit tout au long du chapitre.

> ⚠️ **Honnêteté.** (1) Les données sont **simulées**, et les deux jeux de marché (`courbe_taux.csv` et `rendements_marche.csv`) ont été simulés **indépendamment** : les taux et les actions n'y sont donc pas corrélés, alors qu'ils le sont dans la réalité (et que cette corrélation compte beaucoup pour un assureur). (2) Le « bilan » construit dans ce chapitre est un **jouet** : passif à prestations fixes, sans rachats, sans amélioration future de la mortalité, sans frais, sans écart de crédit. Il sert à comprendre des mécanismes, pas à calibrer un portefeuille. (3) Ce chapitre n'est **pas un conseil en placement** : les allocations obtenues dépendent d'un historique simulé et d'hypothèses qui sont écrites à chaque fois.

Le bloc caché ci-dessous charge les outils du chapitre (un module écrit à la main, `build/outils_ch07.py`) et construit le **bilan jouet** de la mutuelle : le passif est l'échéancier attendu des prestations de décès des contrats en vigueur au 1er janvier 2020, l'actif vaut 10 % de plus que la valeur actuelle de ce passif.


## 7.1 Gestion actif-passif

Une mutuelle d'assurance vie encaisse des primes aujourd'hui et verse des capitaux dans dix, vingt ou quarante ans ; une banque de détail reçoit des dépôts qui peuvent repartir demain et prête sur des années. Dans les deux cas, **le temps** est le produit, et le **taux d'intérêt** est le prix du temps. Cette section apprend à mesurer, avec un seul nombre (la duration), de combien la valeur d'une promesse et la valeur d'un placement changent quand les taux bougent, puis à construire le passif d'un portefeuille réel à partir de tables de mortalité.

### 7.1.1 Le bilan comme deux échéanciers

Un bilan simplifié oppose trois lignes : l'**actif** A (ce que l'on possède : obligations, immobilier, actions, prêts), le **passif** L (ce que l'on doit : provisions pour prestations futures, dépôts) et les **fonds propres**, ou **surplus** S = A − L. Le surplus est le coussin qui absorbe les mauvaises surprises ; c'est lui que le régulateur surveille (chapitre 4).

Ce qui rend la gestion délicate, c'est que A et L ne sont pas des montants mais des **échéanciers** : des paiements aux dates t = 1, 2, 3… Leur valeur du jour est leur **valeur actuelle**, calculée avec la courbe des taux. Quand la courbe se déplace, A et L changent de valeur, **de quantités différentes** si leurs échéanciers diffèrent. Deux lectures complémentaires coexistent :

- la **valeur économique** : S = A − L, valeur actuelle des actifs moins valeur actuelle des passifs, qui répond à « que vaut l'entreprise si on la liquide aux conditions d'aujourd'hui ? » ;
- le **résultat courant** : la marge d'intérêt d'une banque, ou le rendement financier d'un assureur, qui répond à « combien gagne-t-on cette année ? ».

Les deux peuvent raconter des histoires opposées : une hausse des taux réduit la valeur de marché d'un portefeuille obligataire (valeur économique en baisse) et augmente ensuite ses revenus de réinvestissement (résultat en hausse).

| | Assurance vie | Banque de détail |
|---|---|---|
| **Passif** | prestations de décès et de rente, **long** | dépôts à vue et à terme, **court** |
| **Actif** | obligations, immobilier, actions | prêts, **plus longs** que le passif |
| **Risque de taux dominant** | une **baisse** des taux : le passif (plus long) gagne plus en valeur que l'actif | une **hausse** des taux : le coût des dépôts remonte plus vite que le rendement des prêts |

> 💡 **Intuition.** Pensez à deux seaux d'eau suspendus à des cordes de longueurs différentes. Si le vent (le taux) les balance, le plus long se balance plus. L'actif-passif consiste à régler les cordes pour que **les deux seaux oscillent ensemble**.

### 7.1.2 Valeur actuelle, duration et convexité

Un titre qui verse les flux F₁, F₂, …, F_n aux dates 1, 2, …, n (en années) a pour valeur, à un taux unique y (composition annuelle) :

$$P(y)=\sum_{t=1}^{n}\frac{F_t}{(1+y)^t}.$$

**Un exemple calculé à la main.** Une obligation de 100 € à trois ans, qui verse 4 € de coupon par an, quand le taux vaut 3 % :

| Date t | Flux F_t | Facteur (1,03)^−t | Valeur actuelle | t × valeur actuelle |
|---|---|---|---|---|
| 1 | 4 | 0,9709 | 3,883 | 3,883 |
| 2 | 4 | 0,9426 | 3,770 | 7,540 |
| 3 | 104 | 0,9151 | 95,173 | 285,519 |
| **Total** | | | **102,829** | **296,942** |

Le prix est 102,829 €. La **duration de Macaulay** est la date moyenne des flux, pondérée par leur valeur actuelle : D = 296,942 / 102,829 ≈ 2,888 années. Les trois ans de l'échéance sont tirés vers le bas par les coupons intermédiaires.

> 📐 **Démonstration : ce que mesure la duration.** On dérive le prix par rapport au taux :
> $$\frac{dP}{dy}=-\sum_{t}\frac{t\,F_t}{(1+y)^{t+1}}=-\frac{1}{1+y}\sum_t t\,\mathrm{VA}_t=-\frac{D_{\text{Mac}}}{1+y}\,P .$$
> On appelle **duration modifiée** D_mod = D_Mac/(1+y). Donc **dP/P = −D_mod · dy** : la duration modifiée est la **variation relative du prix pour une hausse de 1 point de taux, au signe près** (en pourcentage par point). Une dérivée seconde donne
> $$\frac{d^2P}{dy^2}=\sum_t\frac{t(t+1)F_t}{(1+y)^{t+2}},\qquad C=\frac{1}{P}\frac{d^2P}{dy^2}=\frac{1}{P(1+y)^2}\sum_t t(t+1)\,\mathrm{VA}_t ,$$
> la **convexité** C. Le développement de Taylor à l'ordre deux s'écrit
> $$\frac{\Delta P}{P}\;\approx\;-D_{\text{mod}}\,\Delta y+\tfrac12\,C\,\Delta y^2 .$$

Pour notre obligation : D_mod = 2,888 / 1,03 ≈ 2,804 et C ≈ 10,75. Si le taux monte de 1 point (de 3 % à 4 %), la duration seule prévoit une variation de −2,804 %, la convexité ajoute +½ × 10,75 × 0,01² ≈ +0,054 %, soit −2,750 % au total. Le prix **exact** à 4 % est 100,000 € (le coupon égale le taux : l'obligation vaut son nominal), donc −2,829 € ou −2,751 %. L'approximation à deux termes est bonne ; celle à un terme **surestime** la baisse d'environ 0,05 point (la convexité, positive, amortit la chute).


![Prix d'une obligation à trois ans (coupon de 4 %) en fonction du taux. La courbe est **convexe** : la tangente en 3 % (la duration) sous-estime le prix, que l'on baisse ou que l'on augmente le taux, et la parabole (duration plus convexité) colle bien à la courbe.](figures/ch07-prix-taux.png)

Trois remarques à retenir. **La duration d'un zéro-coupon de maturité m vaut m/(1+y)** : un seul flux, donc une date moyenne égale à m. **Plus l'échéancier est long, plus la duration est grande.** **La convexité est toujours positive** pour des flux positifs : à duration égale, un échéancier plus étalé est plus convexe, donc plus avantageux quand les taux bougent beaucoup dans un sens ou dans l'autre.

> ⚠️ **Piège : la duration est une pente, pas une garantie.** Elle décrit un déplacement **petit** et **parallèle** de la courbe. Pour un choc de 3 points, ou une courbe qui se déforme, il faut **revaloriser** les flux sur la nouvelle courbe (revalorisation complète), ce que fait tout le reste du chapitre.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : application 7.1 (prix, duration et convexité d'une obligation), exercices 7.1 à 7.3.

### 7.1.3 Le passif d'un portefeuille d'assurance vie

Un contrat d'assurance **décès** promet de verser un capital si l'assuré meurt pendant la durée du contrat (**temporaire**) ou à tout moment (**vie entière**). Le passif de la mutuelle est donc un échéancier **aléatoire** dont on calcule l'**espérance** : à la date t, le flux attendu d'un contrat est le capital multiplié par la probabilité de décéder entre t − 1 et t.

Pour un assuré d'âge x aujourd'hui, notons q_x la probabilité de mourir dans l'année à l'âge x, et _tp_x = ∏ (1 − q_{x+j}) la probabilité de survivre t années. Le flux attendu à la fin de l'année t est
$$F_t=\text{capital}\times {}_{t-1}p_x\times q_{x+t-1},$$
tant que le contrat est en vigueur. (Les tables, les probabilités de survie et les calculs sur la durée de vie font l'objet du chapitre 5.)

La table des q_x se calcule à partir des décès et des expositions de la population, par sexe et par âge, cumulés sur 2015–2019 (la mortalité dépend de l'âge et de l'année, et une seule année serait trop bruitée aux grands âges). Les assurés ne meurent pas comme la population : on **mesure** l'écart par le rapport décès observés / décès attendus (*actual / expected*, A/E) sur l'historique du portefeuille. Ici, il vaut 0,783 : les assurés meurent environ 78 % aussi souvent que la population (les personnes assurées sont sélectionnées, donc en meilleure santé). Ce rapport est appliqué à la table pour projeter les prestations (la vérité programmée est 0,75 ; la mesure du chapitre est approximative, voir la section 5.1 pour une version plus fine).

On retient les contrats en vigueur au 1er janvier 2020 : ceux dont l'assuré n'est pas décédé en 2015–2019 et dont la durée n'est pas échue, soit 16 908 contrats sur 20 000.


```python
flux, n = O.flux_passif(portefeuille, table, b.ae)   # prestations attendues par année, t = 1 … 45
taux = O.taux_annuels(derniere_courbe)               # taux zéro-coupon aux maturités 1 … 45
L0 = O.vp(flux, taux)                                # valeur actuelle du passif
print(n, "contrats ;", round(L0 / 1e6, 1), "M€")
```
<!--sortie-->
```text
16908 contrats ; 460.2 M€
```

La première ligne construit l'échéancier à partir des contrats et de la table, la deuxième interpole la courbe des taux du dernier mois (plate au-delà de 30 ans), la troisième actualise. Les prestations nominales cumulées s'élèvent à 716 M€ ; leur valeur actuelle est **460,2 M€**. Le passif est donc, en valeur, **bien moins** que la somme des paiements : de l'argent versé dans vingt ans vaut moins que de l'argent versé demain.


![Prestations de décès attendues du portefeuille par année (barres claires) et leur valeur actuelle sur la courbe de taux du dernier mois (barres foncées). L'échéancier s'étale sur 45 ans, avec une queue de contrats « vie entière ».](figures/ch07-passif-flux.png)

Sur cet échéancier, la duration de Macaulay vaut **16,6 ans**, la duration modifiée 16,2 et la convexité 408. Pour cette mutuelle, une baisse de 1 point de tous les taux gonfle donc le passif d'environ 16 % (plus un peu de convexité), soit de l'ordre de 85 M€ : voilà **le** risque de ce portefeuille.


> ⚠️ **Ce que ce passif ignore.** Pas d'amélioration future de la mortalité (la table de 2015–2019 est figée, ce qui retarde ou réduit les décès réels si la longévité progresse), pas de **rachats** (un assuré qui résilie fait disparaître son flux), pas de frais de gestion, pas de participation aux bénéfices, pas d'options cachées dans les contrats (garanties de taux). Chacune de ces simplifications **change la duration**. Les calculs complets relèvent de l'actuariat vie (chapitre 5) et, sur le plan réglementaire, du *best estimate* (section 4.2).

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : application 7.2 (construire le passif d'un portefeuille vie), exercice 7.3.

### 7.1.4 L'écart de duration et l'immunisation

Supposons que la mutuelle place ses actifs en obligations. Combien doit durer le portefeuille obligataire pour que le surplus ne bouge pas quand les taux bougent ?

Pour un déplacement parallèle Δy de la courbe, on a ΔA ≈ −D_A · A · Δy et ΔL ≈ −D_L · L · Δy, donc
$$\Delta S=\Delta A-\Delta L\approx-\big(D_A\,A-D_L\,L\big)\,\Delta y .$$
La quantité **D_A · A − D_L · L** est l'**écart de duration en euros** (la sensibilité du surplus à 1 point de taux). Pour l'annuler, il faut
$$D_A=D_L\times\frac{L}{A}.$$

> ⚠️ **Le piège de l'appariement naïf.** Beaucoup de débutants égalisent **les durations** (D_A = D_L) et croient le risque supprimé. Il ne l'est que si A = L. Quand l'actif vaut 10 % de plus que le passif, un même D donne à l'actif une sensibilité **en euros** 10 % plus grande. Il faut D_A = D_L × L/A, ici 14,71 ans au lieu de 16,18.

Pour le constater, comparons quatre portefeuilles d'obligations zéro-coupon, tous de valeur A₀ : (a) un portefeuille de maturité 5 ans, (b) un portefeuille de maturités 10 et 20 ans de duration égale à celle du passif (appariement **naïf**), (c) le même, de duration D_L × L/A (appariement **en euros**), et (d) un **haltère** de maturités 5 et 30 ans, de même duration que (c). Le tableau donne la variation du surplus, en M€, après un déplacement parallèle des taux de Δy, **revalorisation complète** (on réactualise tous les flux).

```text
      (a) 5 ans  (b) naïf  (c) en euros  (d) haltère
-3 %     -261.9     -12.8         -48.3         -1.2
-1 %      -59.5       5.1          -3.6          0.0
+1 %       41.9      -8.9          -2.5          0.1
+3 %       91.4     -29.9         -15.6          0.8
NUM DA_cible 14.705283846271243
NUM w20_app 0.5065750782328956
NUM w30_halt 0.40258952096062023
NUM dS_a_m1 -59.45274921597612
NUM dS_a_p1 41.94797934972614
NUM dS_b_m1 5.09714882227844
NUM dS_b_p1 -8.861178755150915
NUM dS_c_m1 -3.5732211960722804
NUM dS_c_p1 -2.4546971838560103
NUM dS_d_m1 0.039298157275259496
NUM dS_d_p1 0.08627521427822113
NUM dS_a_p3 91.43940057928997
NUM dS_a_m3 -261.87698781017764
NUM dS_d_m3 -1.2112423181503416
NUM dS_d_p3 0.7530510789011121
NUM dS_c_m3 -48.31053162424678
NUM dS_c_p3 -15.62115986602658
NUM conv_c 254.41886644709993
NUM conv_d 373.8392190312863
NUM conv_c_adj 279.86075309180995
NUM conv_d_adj 411.2231409344149
```

Lecture du tableau. Le portefeuille (a), trop court, **perd** 262 M€ de surplus si les taux baissent de 3 points : il n'a pas assez de sensibilité pour suivre le passif, qui gonfle. L'appariement **naïf** (b) fait mieux, mais il laisse une exposition du premier ordre : le même D avec un actif plus grand que le passif crée une sensibilité **à la hausse des taux** (−8,9 M€ pour +1 point, +5,1 M€ pour −1 point). L'appariement **en euros** (c) réduit ce résidu, mais il reste **négatif dans les deux sens** (−48,3 M€ à −3 points, −15,6 M€ à +3 points) : c'est un défaut de **convexité**. Seul l'**haltère** (d) est presque insensible dans les deux sens (de -1,2 à 0,8 M€ pour ∓ 3 points).


![Variation du surplus (M€) après un déplacement parallèle de la courbe de taux, pour quatre façons de placer l'actif. Le portefeuille de maturité 5 ans suit mal ; l'appariement naïf ne suffit pas ; l'appariement en euros laisse un défaut de convexité (surplus négatif dans les deux sens) ; l'haltère, plus convexe que le passif, reste proche de zéro.](figures/ch07-surplus-chocs.png)

> 📐 **Les conditions de Redington (1952).** Un actif est **immunisé** contre de petits déplacements parallèles de taux si : (i) la valeur actuelle de l'actif égale celle du passif (ou la dépasse), (ii) les **sensibilités en euros** sont égales (D_A · A = D_L · L), et (iii) la **convexité en euros de l'actif dépasse celle du passif** (C_A · A ≥ C_L · L). En effet, à l'ordre deux,
> $$\Delta S\approx-\big(D_AA-D_LL\big)\Delta y+\tfrac12\big(C_AA-C_LL\big)\Delta y^2 ,$$
> et sous (ii) le premier terme disparaît ; sous (iii), le second est positif : le surplus **ne peut qu'augmenter**, quel que soit le sens du choc. Ici, la convexité du passif est 408, par rapport à L. Rapportée à la même base, celle de l'actif vaut C_A · A/L : 280 pour le portefeuille (c), concentré sur les maturités 10 et 20 ans, qui viole (iii) ; 411 pour l'haltère (d), aux maturités 5 et 30 ans, qui la respecte. **La convexité de l'actif doit entourer l'échéancier du passif.**

Cette condition est **locale** et **parallèle** : l'immunisation de Redington est la ceinture, pas le parachute.

> ✅ **À retenir.** (1) La sensibilité du surplus s'écrit D_A·A − D_L·L : égaliser les durations ne suffit pas si A ≠ L. (2) Pour éviter un risque de pertes dans les deux sens, l'actif doit être **plus convexe** que le passif (haltère). (3) Cela ne protège que contre des déplacements **parallèles** de la courbe, ce que les deux sous-sections suivantes mettent à l'épreuve.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : application 7.3 (apparier l'actif au passif), exercices 7.4 et 7.5.

### 7.1.5 Quand la courbe ne se déplace pas parallèlement

Une courbe réelle se **déplace** (niveau), se **pente** (écart entre taux courts et longs) et se **courbe**. Pour mesurer l'exposition à chaque partie de la courbe, on calcule des **durations par maturité** (*key rate durations*) : on déplace un seul nœud de la courbe de 1 point de base (0,01 %), on interpole, et on lit la variation de valeur. Pour notre passif, une hausse de 1 point de base des taux à chaque nœud donne :

```text
Variation du passif pour +1 point de base du seul nœud (k€) :
1      -2
2      -4
3      -9
5     -19
7     -32
10   -111
20   -196
30   -373
NUM kr_10 110.6460590569973
NUM kr_20 195.70756137984992
NUM kr_30 372.71548620176316
NUM kr_total 743.657776958406
NUM dv01_L 743.5147876511812
```

Le passif est surtout exposé au nœud **30 ans** (373 k€ pour un point de base) : la courbe étant prolongée à plat au-delà de 30 ans, ce nœud porte à lui seul tous les flux au-delà de 20 ans. Viennent ensuite le nœud 20 ans (196 k€) et le nœud 10 ans (111 k€). La somme des nœuds (744 k€) retrouve la sensibilité à un déplacement parallèle de toute la courbe (744 k€ pour un point de base), puisque l'interpolation est linéaire. Un actif apparié « en euros » sur la duration globale peut donc être **mal apparié nœud par nœud**.

Testons-le sur le portefeuille (c). Trois chocs d'amplitude comparable : parallèle (+1 point), **pentification** (taux courts −0,5 point, taux longs +1 point à partir de dix ans) et **aplatissement** (taux courts +1 point, taux longs −0,5 point). On revalorise.

```text
                           passif (M€)  actif (M€)  surplus (M€)
parallèle +1 pt                  -65.9       -68.4          -2.5
pentification (-0,5 / +1)        -61.2       -68.4          -7.2
aplatissement (+1 / -0,5)         34.7        38.9           4.2
NUM pent_dS -7.202248812294125
NUM aplat_dS 4.15834712656635
NUM para_dS -2.4546971838560103
NUM pent_dL -61.200204991811454
```

Le parallèle donne -2,5 M€ (le défaut de convexité vu plus haut) ; la pentification, qui touche les maturités longues où le passif est concentré, coûte -7,2 M€, soit environ trois fois plus ; l'aplatissement rapporte 4,2 M€. **La duration globale ne dit rien du sens dans lequel la courbe se déforme** : c'est pourquoi les régulateurs et les gestionnaires testent plusieurs scénarios de courbe (section 3.2).

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : application 7.4 (chocs de courbe et durations par maturité), exercice 7.12.

### 7.1.6 La banque : l'échéancier de refixation

Une banque de détail se préoccupe d'abord de sa **marge nette d'intérêt** (MNI) de l'année qui vient. On y répond par un **tableau de refixation** (*repricing gap*) : on range actifs et passifs sensibles aux taux selon la date à laquelle leur taux sera révisé, puis on calcule, par tranche, l'écart (actif − passif).

**Un exemple à la main** (montants en M€) :

| Tranche de refixation | Actifs | Passifs | Écart | Part de l'année qui reste après refixation |
|---|---|---|---|---|
| moins de 3 mois | 200 | 430 | −230 | 0,875 |
| 3 à 12 mois | 150 | 250 | −100 | 0,375 |
| 1 à 5 ans | 400 | 170 | +230 | 0 |
| plus de 5 ans | 250 | 100 | +150 | 0 |
| **Total sensible** | 1 000 | 950 | +50 | |

(Les 50 M€ restants sont les fonds propres, qui ne portent pas de taux.) Une hausse **parallèle** de 1 point des taux modifie la marge de l'année de
$$\Delta\text{MNI}\approx\sum_i \text{écart}_i\times\text{part}_i\times\Delta y=\big(-230\times0{,}875-100\times0{,}375\big)\times0{,}01=-2{,}39\ \text{M€},$$
puisque seules les tranches qui se refixent **avant la fin de l'année** profitent (ou souffrent) du nouveau taux, et pendant la fraction de l'année qui reste. Cette banque, qui finance des prêts à taux fixe longs avec des dépôts qui se refixent vite, **perd** quand les taux montent, et gagne quand ils baissent : exactement l'inverse de la mutuelle de la section précédente.


> ⚠️ **Ce que le tableau de refixation ne voit pas.** Les dépôts à vue n'ont pas d'échéance contractuelle : leur comportement (stabilité, taux servi) est un **modèle** ; les clients remboursent leurs prêts par anticipation quand les taux baissent ; une hausse des taux n'est pas toujours répercutée en totalité sur les taux débiteurs. Les banques complètent le tableau par une simulation de marge et par la valeur économique des fonds propres, calculée comme en 7.1.4 avec les durations de l'actif et du passif.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : application 7.4, exercice 7.12 (échéancier de refixation d'une banque).

### 7.1.7 Rejouer l'histoire des taux

Une manière concrète de sentir le risque est de **rejouer** les 120 mois de courbes de `courbe_taux.csv` sur le bilan jouet : à chaque mois, on revalorise le même échéancier de passif et les mêmes portefeuilles zéro-coupon sur la courbe de ce mois (on ignore le temps qui passe et les achats ou ventes : c'est un test de **sensibilité statique** aux courbes passées).


![À gauche : taux à 5 ans et à 20 ans sur les 120 mois simulés ; la zone orangée est le cycle de hausse des taux (mois 60 à 90). À droite : surplus, en pourcentage du passif initial, de quatre portefeuilles d'actifs revalorisés à chaque courbe. Le portefeuille court gagne pendant la hausse (le passif perd plus que l'actif) ; les portefeuilles appariés restent proches de 10 %.](figures/ch07-replay-taux.png)

La valeur du passif varie de **325 M€** (mois 85, sommet du cycle de hausse) à **484 M€** (mois 27) : une variation de plus de 30 % pour un portefeuille dont les prestations ne changent pas d'un euro. Le surplus du portefeuille de maturité 5 ans oscille avec un écart-type de 6,1 points de passif, de 7 % à 28 % ; l'appariement naïf ramène l'écart-type à 1,5 point, l'appariement en euros à 0,6 point.

Une leçon, qui sera mise en chiffres en 7.3 : **le risque de ce portefeuille est la baisse des taux, pas leur hausse**. Il suffit de lire le graphique : le portefeuille court s'enrichit quand les taux montent, mais voit son surplus passer de 27 % du passif au mois 90 à 10 % au mois 120, quand les taux retombent. Un assureur dont le passif est plus long que l'actif n'est jamais protégé : il est en **pari** sur la direction des taux.

> ✅ **À retenir.** (1) Un échéancier se résume par sa valeur actuelle, sa duration (pente) et sa convexité (courbure). (2) Le surplus bouge de D_A·A − D_L·L par point de taux : l'écart de duration se mesure **en euros**. (3) La convexité de l'actif doit entourer celle du passif. (4) Une courbe qui se déforme (pente, courbure) demande des durations par maturité et des **revalorisations complètes**. (5) Le risque d'un passif long est la **baisse** des taux.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.1 à 7.4 et exercices 7.1 à 7.5 et 7.12.


## 7.2 Théorie du portefeuille

La section précédente a traité le **passif** comme une donnée. Celle-ci s'occupe de l'**actif** seul : on dispose d'un capital et de quelques classes d'actifs aux rendements incertains ; comment le répartir ? Harry Markowitz a proposé en 1952 une réponse qui tient en une idée : **le risque d'un portefeuille n'est pas la moyenne des risques de ses composants**, parce que les composants ne bougent pas tous ensemble.


### 7.2.1 Rendement et risque d'un portefeuille

Soit n actifs, de rendements aléatoires r₁, …, r_n, de rendements espérés μ = (μ₁, …, μ_n) et de matrice de covariance Σ (de terme général σ_ij = ρ_ij σ_i σ_j). Un portefeuille est un vecteur de poids w = (w₁, …, w_n), de somme 1. Son rendement a pour moyenne et variance
$$\mu_p=w^\top\mu,\qquad \sigma_p^2=w^\top\Sigma\,w=\sum_{i,j}w_iw_j\sigma_{ij}.$$
La moyenne est la moyenne des moyennes : rien de surprenant. La variance, elle, contient les **covariances** : c'est la clé de la diversification.

**Deux actifs, à la main.** Un actif risqué (« actions » : μ₁ = 6 %, σ₁ = 20 %) et un actif sûr (« obligations » : μ₂ = 3 %, σ₂ = 5 %), de corrélation ρ. Pour un portefeuille moitié-moitié, le rendement espéré vaut 4,5 % quel que soit ρ, et la variance
$$\sigma_p^2=0{,}25\times0{,}04+0{,}25\times0{,}0025+2\times0{,}25\times\rho\times0{,}20\times0{,}05=0{,}010625+0{,}005\,\rho .$$

| Corrélation ρ | Variance | Écart-type du portefeuille 50/50 |
|---|---|---|
| −0,5 | 0,008125 | 9,01 % |
| 0,2 | 0,011625 | 10,78 % |
| 1 | 0,015625 | 12,50 % |

À ρ = 1, l'écart-type est la moyenne des écarts-types (12,5 % = 0,5 × 20 % + 0,5 × 5 %) : aucune diversification. À ρ < 1, il est **strictement inférieur** : on obtient le même rendement espéré avec moins de risque. C'est le seul « repas gratuit » de la finance.


### 7.2.2 La frontière efficiente à deux actifs

Faisons varier le poids w de l'actif risqué entre 0 et 1. Les couples (σ_p, μ_p) dessinent une courbe : la **frontière**, qui va du portefeuille 100 % sûr (w = 0) au portefeuille 100 % risqué (w = 1). Sa forme dépend de ρ : droite si ρ = 1, courbe de plus en plus creusée quand ρ diminue.

> 📐 **Le portefeuille de variance minimale à deux actifs.** Avec les poids w et 1 − w, σ_p² = w²σ₁² + (1 − w)²σ₂² + 2w(1 − w)ρσ₁σ₂. On dérive par rapport à w et on annule :
> $$w^\star=\frac{\sigma_2^2-\rho\,\sigma_1\sigma_2}{\sigma_1^2+\sigma_2^2-2\rho\,\sigma_1\sigma_2}.$$
> Le dénominateur est positif (c'est la variance de r₁ − r₂). Le numérateur est **négatif** si ρ > σ₂/σ₁, auquel cas w* < 0 : sans vente à découvert, la variance minimale s'obtient avec 0 % d'actif risqué.

Avec nos chiffres, σ₂/σ₁ = 0,25. Pour ρ = 0,2, w* = 0,0005/0,0385 ≈ 0,013 : on détient presque uniquement l'actif sûr, avec un peu d'actions qui **réduisent** le risque (la variance minimale, 4,99 %, est inférieure à 5 %). Pour ρ = 0,5, le numérateur est négatif, et le portefeuille de variance minimale est 100 % obligations (5,0 %).


![Frontière de deux actifs (actions : rendement espéré 6 %, écart-type 20 % ; obligations : 3 % et 5 %) pour trois corrélations. Plus la corrélation est faible, plus la courbe se creuse vers la gauche : à rendement égal, on prend moins de risque.](figures/ch07-frontiere-2actifs.png)

### 7.2.3 Cinq actifs : la frontière sur nos données

Passons aux cinq classes d'actifs de `rendements_marche.csv`. Les paramètres μ et Σ sont **estimés** sur les 4 000 jours d'historique (rendements journaliers moyens × 252, covariances × 252) : c'est une première convention, et la section 7.2.6 montrera ce qu'elle cache. Le calcul de la frontière se fait par optimisation numérique : pour chaque rendement cible, on cherche les poids de variance minimale, de somme 1, **sans vente à découvert** (poids positifs).

```python
mu, S = O.stats_annuelles(rend)            # rendements moyens et covariance, annualisés
w_min = O.min_variance(S)                  # portefeuille de variance minimale
w_tan = O.tangent(mu, S, rf=0.015)         # portefeuille de ratio de Sharpe maximal (taux sans risque 1,5 %)
```

Le **ratio de Sharpe** d'un portefeuille est (μ_p − r_f)/σ_p : le rendement en excès du taux sans risque, par unité de risque. Le portefeuille « tangent » est celui qui le maximise ; on le trouve en traçant, depuis le point (0, r_f), la droite la plus pentue qui touche la frontière.

```text
             rendement (%)  volatilité (%)  poids variance min. (%)  poids tangent (%)
actions_A              5.6            18.7                      1.9                3.8
actions_B              4.3            22.8                      1.2                0.0
obligations            4.0             4.4                     88.8               84.0
immobilier             5.7            13.2                      6.2               12.2
matieres              -2.9            22.0                      1.9                0.0

portefeuille variance minimale : 4.09 % de volatilité, 4.03 % de rendement
portefeuille tangent           : 4.19 % de volatilité, 4.29 % de rendement
NUM vol_min 4.089868238090334
NUM mu_min 4.026407480941068
NUM vol_tan 4.188319863573829
NUM mu_tan 4.287995591581401
NUM w_obl_min 88.84166102309152
NUM w_obl_tan 83.98434443296364
NUM w_imm_tan 12.172675863313193
NUM sharpe_tan 0.6656596636347749
NUM vol_eq 11.65583286155107
NUM mu_eq 3.3624536400000022
NUM sharpe_eq 0.1597872637779194
NUM sharpe_obl 0.5772969912342076
NUM sharpe_actA 0.22116114746699628
```

Trois constats. **(1)** Le portefeuille de variance minimale est presque entièrement en obligations (89 %) : c'est de loin l'actif le moins volatil. **(2)** Le portefeuille tangent l'est aussi (84 % d'obligations, 12 % d'immobilier) : sur cet historique, le ratio de Sharpe des obligations (0,58) écrase celui des actions (0,22 pour l'indice A). **(3)** Le portefeuille « égal pondéré » (20 % de chaque classe) a une volatilité de 11,7 % pour un rendement de 3,4 %, soit un Sharpe de 0,16 : l'optimisation fait gagner beaucoup, **sur l'historique**. La section 7.2.6 demande si ce gain survit à l'avenir.


![Cinq classes d'actifs de `rendements_marche.csv` : les actifs pris isolément (points), 3 000 portefeuilles aléatoires (nuage gris), la frontière efficiente sans vente à découvert (courbe bleue), le portefeuille de variance minimale et le portefeuille tangent, avec la droite qui part du taux sans risque (1,5 %). Les matières premières, au rendement moyen négatif sur l'historique, sont dominées.](figures/ch07-frontiere-5actifs.png)

### 7.2.4 Contributions au risque

Savoir qu'un portefeuille a une volatilité de 10 % ne dit pas **qui** la produit. Comme σ_p(w) est **homogène de degré 1** (multiplier tous les poids par λ multiplie σ_p par λ), le théorème d'Euler donne
$$\sigma_p=\sum_i w_i\frac{\partial\sigma_p}{\partial w_i},\qquad \frac{\partial\sigma_p}{\partial w_i}=\frac{(\Sigma w)_i}{\sigma_p}.$$
La **contribution au risque** de l'actif i est donc RC_i = w_i(Σw)_i/σ_p, et les contributions **s'additionnent** exactement à la volatilité du portefeuille. Un actif peut peser 20 % du capital et 70 % du risque.

La **parité des risques** (*risk parity*) cherche les poids qui égalisent les contributions : RC_i = σ_p/n pour tout i. Pas de formule fermée en général ; on résout numériquement.

```text
part de chaque actif dans le risque (%), puis volatilité du portefeuille (%)
             égal pondéré  variance min.  parité des risques
actions_A              26              2                  20
actions_B              33              1                  20
obligations             0             89                  20
immobilier             16              6                  20
matieres               25              2                  20
volatilité           11.7            4.1                 5.8
NUM rc_eq_actions 58.894695480984524
NUM rc_eq_obl 0.13104321161395846
NUM vol_rp 5.780075085270962
NUM w_rp_obl 62.29466897961221
NUM mu_rp 3.783987101618801
```

Dans le portefeuille égal pondéré, les deux indices d'actions, qui pèsent 40 % du capital, produisent 59 % du risque ; les obligations, 20 % du capital, en produisent 0,1 %. La parité des risques doit pour cela mettre 62 % du capital en obligations, ce qui donne une volatilité de 5,8 % et un rendement de 3,8 % sur l'historique.

> 💡 **Intuition.** Répartir le **capital** également n'est pas répartir le **risque** également. La contribution au risque est la bonne comptabilité pour dire « d'où viendra la prochaine mauvaise nouvelle ».

### 7.2.5 L'idée du CAPM

Si **tous** les investisseurs raisonnaient comme Markowitz avec les mêmes anticipations, ils détiendraient tous le même portefeuille risqué (le tangent), et ce portefeuille serait le **marché** lui-même. Le **modèle d'équilibre des actifs financiers** (CAPM, Sharpe 1964) en tire une conséquence : le rendement espéré d'un actif ne dépend que de son **bêta**, sa sensibilité au marché,
$$\mu_i-r_f=\beta_i\,(\mu_m-r_f),\qquad \beta_i=\frac{\operatorname{cov}(r_i,r_m)}{\operatorname{var}(r_m)}.$$
Le risque **propre** d'un actif (celui qui n'est pas lié au marché) se diversifie et n'est pas rémunéré.

Pour voir le bêta à l'œuvre, prenons comme « marché » la moyenne des deux indices d'actions :

```text
             bêta  rendement observé (%)  rendement CAPM (%)
actions_A    0.88                   5.63                4.57
actions_B    1.12                   4.34                5.40
obligations -0.02                   4.02                1.44
immobilier   0.40                   5.71                2.91
matieres     0.41                  -2.89                2.92
NUM beta_obl -0.017996729993034907
NUM beta_imm 0.40409575779034085
NUM beta_mat 0.4083400104677518
NUM capm_imm 2.9081799252739544
NUM obs_imm 5.7071637000000015
```

Le bêta des obligations est -0,02 (quasi indépendantes des actions), celui de l'immobilier 0,40, celui des matières premières 0,41. Le CAPM prévoit pour l'immobilier un rendement de 2,9 % ; l'historique donne 5,7 %. **L'écart n'est pas une erreur du modèle : c'est une propriété des données**, dont les rendements espérés ont été programmés sans aucune référence au CAPM. Dans la réalité, on observe des écarts (les « alphas ») et on ne sait jamais s'ils sont du bruit d'estimation ou de l'information : voir la section suivante.

> ⚠️ **Limites.** Le CAPM suppose des investisseurs identiques, un marché observable (le « vrai » portefeuille de marché contient tous les actifs, y compris les actifs non cotés), un seul horizon et des rendements décrits par leur moyenne et leur variance. Il reste utile comme **langage** (bêta, risque systématique, risque propre) bien plus que comme prévision.

### 7.2.6 L'estimation, maillon faible

L'optimisation de Markowitz est un **amplificateur d'erreurs** : elle surpondère les actifs dont les paramètres estimés flattent le rendement, et sous-pondère ceux dont ils sont défavorables. Or on estime μ et Σ avec peu de données.

**Les rendements espérés sont très mal connus.** L'écart-type de la moyenne d'un rendement annuel observé pendant T années est σ/√T. Avec T = 15,9 ans, pour l'indice d'actions A (volatilité 19 %), cela fait ± 4,7 points : la moyenne observée (5,6 %) est compatible, à deux erreurs types, avec des rendements espérés allant de -4 % à 15 %. Le tableau compare les moyennes observées à la **vérité programmée** (rendement espéré journalier de 4, 4, 1, 2 et 1 pour dix mille, soit environ 10,1 %, 10,1 %, 2,5 %, 5,0 % et 2,5 % par an) :

```text
             observé (%)  vrai (%)  erreur type (pts)  écart en erreurs types
actions_A            5.6      10.1                4.7                    -0.9
actions_B            4.3      10.1                5.7                    -1.0
obligations          4.0       2.5                1.1                     1.4
immobilier           5.7       5.0                3.3                     0.2
matieres            -2.9       2.5                5.5                    -1.0
NUM sd_A 18.687930711775554
NUM se_A 4.6906333815543295
NUM mu_A 5.633044200000001
NUM ic_lo -3.748222563108657
NUM ic_hi 15.01431096310866
NUM mu_mat -2.885185799999999
NUM vrai_mat 2.52
NUM ecart_max 1.36932999812444
```

Aucun écart n'est « anormal » (le plus grand est de 1,4 erreur type), et pourtant l'estimation place les matières premières à -2,9 % alors que leur rendement espéré vrai est de 2,5 %, et classe l'immobilier (5,7 %) devant l'indice d'actions B alors que le rendement espéré vrai de l'immobilier (5,0 %) est deux fois plus faible que celui des actions (10,1 %). **L'optimiseur s'appuie donc sur du bruit.**

**Les poids optimaux sautent d'une fenêtre à l'autre.** On découpe l'historique en fenêtres d'un an (250 jours), on calcule à chaque fois le portefeuille de variance minimale et le portefeuille tangent, puis on regarde la stabilité des poids :


![Poids des cinq actifs dans les portefeuilles de variance minimale (à gauche) et tangent (à droite), recalculés sur chacune des fenêtres successives d'un an (un point par fenêtre). La variance minimale, qui n'utilise que les covariances, est stable ; le portefeuille tangent, qui utilise aussi les rendements moyens, change de visage d'une année à l'autre.](figures/ch07-instabilite.png)

Sur 14 fenêtres, le poids des obligations dans le portefeuille de variance minimale reste entre 70 % et 94 % ; celui du portefeuille tangent varie de 0 % à 100 %, avec jusqu'à 59 % d'actions certaines années. La rotation (somme des variations absolues de poids d'une fenêtre à la suivante, 2 au maximum) vaut 0,19 en moyenne pour la variance minimale et 1,07 pour le tangent. **La variance minimale dépend seulement de Σ, bien estimée ; le tangent dépend de μ, mal estimé.**

**Le rétrécissement de la covariance.** Quand le nombre d'actifs n s'approche du nombre d'observations T, la covariance empirique devient instable (elle compte n(n + 1)/2 paramètres). Le remède classique de **Ledoit et Wolf** consiste à la **rétrécir** vers une cible simple (une matrice scalaire) : Σ* = (1 − δ) S + δ · m · I, où m est la variance moyenne et δ ∈ [0, 1] est choisi par une formule de risque quadratique. Testons-le deux fois, en jugeant les portefeuilles de variance minimale sur des données qu'ils n'ont pas vues :

```text
NUM oos_emp 4.030384294524111
NUM oos_rét 4.334113286267227
NUM oos_poi 11.072743921763355
5 actifs réels, estimation sur 250 jours, test sur les 250 suivants (volatilité annuelle, %)
empirique                  4.03
rétrécie (Ledoit–Wolf)     4.33
poids égaux               11.07

60 actifs simulés, estimation sur 120 jours, volatilité VRAIE (%)
empirique                  1.03
rétrécie (Ledoit–Wolf)     0.90
poids égaux               10.28
optimum vrai               0.73
NUM lw60_emp 1.0305149087762866
NUM lw60_lw 0.8989668954229215
NUM lw60_eq 10.275877674205237
NUM lw60_opt 0.73359987781327
```

Avec **5 actifs réels et 250 jours**, le rétrécissement **n'aide pas** : la covariance empirique est déjà bien estimée, et le rétrécissement vers la matrice scalaire relève la variance estimée des actifs peu volatils : le poids moyen des obligations passe de 86 % à 77 %, ce qui rend le portefeuille plus risqué. Avec **60 actifs simulés et 120 jours**, il aide nettement : la volatilité vraie du portefeuille construit sur la covariance rétrécie est 0,90 %, contre 1,03 % avec la covariance empirique ; le minimum possible, avec la vraie covariance, est 0,73 %. Quant aux poids égaux (10,3 %), ils sont dix fois plus risqués : ne rien optimiser n'est pas une solution non plus.

> ✅ **À retenir.** (1) Un portefeuille de variance minimale ne dépend que de Σ ; un portefeuille tangent dépend de μ, très mal connu. (2) Les poids « optimaux » d'un historique sont un **résultat avec incertitude**, pas une vérité. (3) Le rétrécissement de la covariance est utile quand n s'approche de T, inutile (voire nuisible) quand n est petit. (4) On **contraint** les poids (bornes, pas de vente à découvert) et on **diversifie les méthodes** pour que le portefeuille ne dépende pas d'une estimation fragile.

### 7.2.7 La diversification en période de stress

La diversification dépend des **corrélations**, et celles-ci ne sont pas constantes. Dans `marche_verite.csv`, chaque jour est étiqueté « calme » ou « stress » ; **on ne connaît pas cette étiquette en réalité**, mais elle permet de mesurer ce que l'on aurait vu si on l'avait connue.

```text
                              calme  stress
jours                          3718     282
volatilité actions A (%)         16      38
corrélation A–B                0.57    0.89
corrélation A–immobilier       0.43    0.87
volatilité égal pondéré (%)     9.5    27.1
volatilité variance min. (%)    3.6     7.9
NUM part_stress 7.049999999999999
NUM n_stress 282
NUM volA_calme 16.288569897557117
NUM volA_stress 38.181025579624006
NUM vol_min_calme 3.642538879463517
NUM vol_min_stress 7.905887846449958
NUM vol_eq_calme 9.511104049729584
NUM vol_eq_stress 27.10878517551788
NUM corrAB_stress 0.885792994364173
NUM corrAB_calme 0.5731072398636516
```

Les jours de stress (7 % des jours) doublent la volatilité (indice A : 16 % en calme, 38 % en stress), et les corrélations entre actions et immobilier **s'envolent** (A–B de 0,57 à 0,89). Les actifs qui se diversifiaient hier chutent ensemble aujourd'hui. Le portefeuille de variance minimale, dont la volatilité « moyenne » est 4,1 %, a une volatilité de 3,6 % en calme et de 7,9 % en stress ; le portefeuille égal pondéré passe de 9,5 % à 27,1 %.


![Matrices de corrélation des cinq actifs dans les jours « calmes » (à gauche) et dans les jours de « stress » (à droite). En stress, les corrélations entre les deux indices d'actions et l'immobilier approchent 0,9 ; les obligations restent indépendantes.](figures/ch07-correlations-regimes.png)

Une autre façon de voir la même chose : les **queues** des rendements. Le rendement journalier d'un portefeuille n'est pas gaussien. La kurtosis en excès (0 pour une loi normale) de l'indice A vaut 19, celle du portefeuille de variance minimale 7 : les extrêmes sont beaucoup plus fréquents que ne le dit la loi normale. Pour le portefeuille de variance minimale, la perte journalière dépassée un jour sur cent est de 0,71 % sur l'historique, mais de 0,58 % si l'on suppose les rendements gaussiens de même moyenne et de même variance : la loi normale **sous-estime** la perte d'environ 21 %. Les mesures de risque (VaR et expected shortfall, section 3.1) dépendent de ce choix.


> ⚠️ **Piège : la corrélation moyenne ment.** Une matrice de corrélation estimée sur tout l'historique mélange les jours calmes et les jours de stress : elle prédit un risque (4,1 %) qui n'est celui d'aucun des deux régimes, et qui **sous-estime** le risque quand on en a le plus besoin. Les remèdes (modèles à régimes, corrélations de stress, **scénarios**) font l'objet du chapitre 3 (3.2 : stress tests).

> ✅ **À retenir.** (1) Le risque d'un portefeuille dépend des covariances, pas seulement des volatilités. (2) La frontière efficiente est un **outil de réflexion**, dont les entrées (μ, Σ) sont estimées avec erreur. (3) Les corrélations montent en stress : la diversification est la plus fragile quand elle est la plus utile. (4) Un portefeuille se juge aussi sur ses queues.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.5 à 7.7 et exercices 7.6 à 7.10.


## 7.3 De la frontière efficiente à l'actif-passif

Les deux sections précédentes se sont ignorées : la première a traité l'actif comme un moyen d'**apparier** un passif, la seconde a choisi des actifs **sans passif**. Un gestionnaire d'assurance doit faire les deux en même temps : le critère n'est pas le risque de l'actif, c'est le risque du **surplus**. Cette section reprend la théorie du portefeuille avec le bon objet, puis mesure le risque du surplus par une VaR et une expected shortfall, et enfin le simule sur dix ans.


### 7.3.1 Le surplus comme objet à optimiser

Sur un an, la variation du surplus d'une allocation w vaut
$$\Delta S=\underbrace{A_0\,w^\top r}_{\text{gain de l'actif}}-\underbrace{\Delta L}_{\text{variation du passif (et prestations)}},$$
où r est le vecteur des rendements des instruments. Sa variance se décompose :
$$\operatorname{Var}(\Delta S)=A_0^2\,w^\top\Sigma_r\,w\;-\;2A_0\,w^\top\operatorname{Cov}(r,\Delta L)\;+\;\operatorname{Var}(\Delta L).$$
Le premier terme est le risque de l'actif seul (celui de Markowitz). Le deuxième est le **terme de couverture** : il récompense les actifs qui varient **comme le passif**. Le troisième ne dépend pas de w. Minimiser le risque du surplus, c'est donc **régresser le passif sur les actifs** : le meilleur portefeuille est celui qui **réplique** le passif, et non celui qui minimise la variance de l'actif.

> 💡 **Intuition.** Pour une famille qui doit payer un loyer fixe dans cinq ans, le placement le moins risqué n'est pas le plus stable d'année en année : c'est celui qui vaudra exactement le loyer dans cinq ans. Le risque se mesure **par rapport à la dette**, pas dans l'absolu.

Pour le vérifier, on tire 5 000 scénarios annuels (courbe des taux et marchés tirés dans l'historique, voir plus bas), on calcule pour chaque scénario le gain en euros de six instruments (zéros-coupons de maturités 5, 10, 20 et 30 ans, actions, immobilier) et la variation du passif, **avec revalorisation complète**. Comparons deux critères :

- **Markowitz sans passif** : le portefeuille de variance minimale des **actifs** ;
- **réplication** : le portefeuille de variance minimale du **surplus**.

```text
poids (%) puis écart-type de la variation annuelle du surplus (M€)
                       variance min. de l'actif  réplication du passif
ZC 5 ans                                     99                     48
ZC 10 ans                                     0                     14
ZC 20 ans                                     0                      0
ZC 30 ans                                     0                     38
actions                                       1                      0
immobilier                                    1                      0
écart-type du surplus                      22.2                    0.4
NUM sd_mk 22.24321548367511
NUM sd_rep 0.4200616799472272
NUM sd_liab 30.94542997774432
NUM w_mk_z5 98.6125162111943
NUM w_rep_z5 47.827796486785346
NUM w_rep_z10 14.330419319574442
NUM w_rep_z30 37.818072975317506
NUM w_rep_risque 0.02371121832234738
```

Le portefeuille de variance minimale **de l'actif** est presque entièrement en zéro-coupon à 5 ans (99 %), l'actif le moins volatil ; il laisse un surplus dont l'écart-type annuel est de **22,2 M€**, soit 72 % du risque du passif lui-même (30,9 M€) : il ne le couvre presque pas. Le portefeuille de **réplication** utilise des maturités 5, 10 et 30 ans (48 %, 14 % et 38 %) et aucun actif risqué (0 %) ; l'écart-type du surplus tombe à **0,4 M€**, soit environ 53 fois moins. Le meilleur actif pour ce passif n'est pas l'actif le moins risqué : c'est celui qui **lui ressemble**.


### 7.3.2 Optimiser sous contrainte de risque

Aucun gestionnaire ne se contente de répliquer : un portefeuille de réplication rapporte peu, et l'on a de bonnes raisons de prendre un peu de risque pour augmenter le gain espéré. Le problème devient celui de la section 7.2, avec le surplus à la place du portefeuille :
$$\max_{w}\;\mathbb{E}[\Delta S]\quad\text{sous}\quad \sum_j w_j=1,\; w_j\ge0,\;\;\sigma(\Delta S)\le\sigma_{\text{budget}}.$$
On balaie le **budget de risque** σ_budget (l'écart-type annuel du surplus que la direction accepte) et on lit l'allocation qui rapporte le plus.

```text
allocation (%) et gain espéré du surplus (M€) selon le budget de risque (écart-type annuel du surplus)
                  2 M€  5 M€  10 M€  20 M€  40 M€  80 M€
ZC 5 ans            56    49     39     19      0      0
ZC 10 ans            0     0      0      0      0      0
ZC 20 ans            0     0      0      0      0      0
ZC 30 ans           42    45     50     59     54     12
actions              1     2      4      9     16     24
immobilier           1     3      6     13     31     65
gain espéré (M€)   1.7   2.5    3.7    6.2   10.6     16
NUM gain_2 1.7157182791349535
NUM gain_10 3.7236071707487657
NUM gain_40 10.560725460418782
NUM gain_80 16.02227501989792
NUM risque_10_pct 10.64231843368498
NUM risque_80_pct 88.18717031210659
```

Le tableau se lit de gauche à droite comme un **dial de risque**. À 2 M€ d'écart-type, on retrouve la réplication (gain espéré de 1,7 M€). À 10 M€, la part d'actifs risqués est de 11 % ; à 80 M€, de 88 %, pour un gain espéré de 16 M€. **Le gain espéré croît bien plus lentement que le risque** : multiplier le risque par 40 (de 2 à 80 M€) ne multiplie le gain que par 9. Et ce gain est un **gain historique** : les espérances viennent des mêmes tirages que le risque, avec toutes les réserves de la section 7.2.6.


![Frontière du surplus : gain espéré du surplus (M€) en fonction de son écart-type annuel, pour l'allocation de gain maximal à budget de risque donné (courbe), et pour quatre allocations de référence (points). Les quatre allocations de référence sont **sous** la frontière : pour le même risque, une allocation optimisée rapporte plus. « Markowitz sans passif » est le plus éloigné : il prend du risque de surplus pour un gain espéré négatif.](figures/ch07-frontiere-surplus.png)

> ⚠️ **Piège : une frontière qui dépend du modèle de passif.** Tout ce qui précède suppose le passif connu : prestations fixes, mortalité figée. Si les prestations dépendent des taux (garantie de taux minimum, rachats), le passif est **optionnel** et le meilleur actif change. Le résultat d'une optimisation actif-passif n'est jamais meilleur que le modèle de passif sur lequel il repose.

### 7.3.3 VaR et expected shortfall du surplus

La direction ne regarde pas l'écart-type, elle regarde les **pertes extrêmes** : quelle baisse du surplus un an « sur 200 » ? Ce sont la VaR à 99,5 % sur un an (le quantile de la perte, c'est l'idée du capital requis du régime Solvabilité, section 4.2) et l'expected shortfall (la perte moyenne dans la queue, section 3.1). On les calcule sur les scénarios annuels :

```text
NUM var_mar 134.1491567818308
NUM es_mar 138.57008182863942
NUM cov_mar 0.3430703282995982
NUM p_neg_mar 17.36
NUM var_app 5.149561246166238
NUM es_app 5.858566366294979
NUM cov_app 8.937187666720154
NUM p_neg_app 0.0
NUM var_mix 40.809950530820274
NUM es_mix 42.072182975024475
NUM cov_mix 1.1277297487410585
NUM p_neg_mix 0.13999999999999999
NUM var_opt 18.499473855705833
NUM es_opt 19.137203432171088
NUM cov_opt 2.4877786047986503
NUM p_neg_opt 0.0
NUM var_mk 62.57615094648593
NUM es_mk 66.58164103694848
NUM cov_mk 0.7354654219243162
NUM p_neg_mk 3.0
                       gain espéré (M€)  écart-type (M€)  VaR 99,5 % (M€)  ES 99 % (M€)  surplus initial / VaR
Marché                              9.5             58.2            134.1         138.6                   0.34
Apparié                             0.4                2              5.1           5.9                   8.94
Mixte                               3.7             18.2             40.8          42.1                   1.13
Optimisé (10 M€)                    3.7               10             18.5          19.1                   2.49
Markowitz sans passif              -0.8             22.2             62.6          66.6                   0.74
```

Le même bilan, avec le même surplus initial de 46 M€, donne des diagnostics opposés :

- avec l'allocation « Marché » (45 % d'actions, 15 % d'immobilier, 40 % d'obligations à 5 ans), la perte à 99,5 % est de **134 M€**, soit 2,9 fois le surplus : un tel assureur est **insolvable** au sens de Solvabilité sur ce modèle jouet (surplus / VaR = 0,34) ;
- avec l'allocation « Apparié », elle est de **5,1 M€** (surplus / VaR = 8,9) ;
- avec l'allocation « Mixte » (80 % apparié, 20 % d'actifs risqués), de 41 M€ (1,1 fois couvert) ;
- le portefeuille « Markowitz sans passif », qui minimise le risque de l'actif, perd jusqu'à 63 M€ pour un gain espéré **négatif** (-0,8 M€) : il est 12 fois plus risqué que l'allocation « Apparié », alors qu'il est le moins risqué **des actifs**.


Une VaR estimée sur 5 000 tirages repose sur une **queue de 25 observations** à 99,5 % : elle est incertaine. Deux sources d'incertitude se distinguent : l'**erreur de tirage** (on aurait pu tirer d'autres scénarios dans le même historique), qui diminue quand on tire davantage ; et l'**erreur d'historique** (on n'a observé que 119 variations mensuelles de taux), qui ne diminue pas. On les mesure par **rééchantillonnage** (*bootstrap*).

```text
VaR 99,5 % de l'allocation Mixte : 40.8 M€
intervalle à 95 %, erreur de tirage seule         : [39.0 ; 42.3]
intervalle à 95 %, historique des taux rééchantillonné : [34.8 ; 46.8]
NUM var_mix_lo 39.014770999564675
NUM var_mix_hi 42.32436470195427
NUM var_mix_lo2 34.78396059254116
NUM var_mix_hi2 46.79178291894242
```

L'erreur de tirage seule donne un intervalle étroit (de 39 à 42 M€ pour une estimation de 41 M€). Mais si l'on rééchantillonne aussi l'**historique des taux**, l'intervalle s'élargit à [35 ; 47] M€ : la seconde source d'incertitude domine. Et aucun de ces intervalles ne mesure l'**erreur de modèle** (taux et actions indépendants, passif fixe). À 99,5 %, **ne jamais présenter la VaR sans son incertitude**.


![Distribution de la variation annuelle du surplus (5 000 scénarios) pour trois allocations. Trait pointillé : −VaR à 99,5 % ; trait rouge : le surplus initial, qu'une perte supérieure efface. À gauche (« Marché »), la queue dépasse le surplus ; à droite (« Apparié »), la distribution est étroite autour de zéro.](figures/ch07-var-surplus.png)

> 📐 **Pourquoi la VaR du surplus n'est pas la VaR de l'actif.** La VaR de l'actif dit combien l'on peut perdre sur les placements. Celle du surplus dit combien l'on peut perdre **de marge de manœuvre** : une baisse des taux qui fait perdre 5 % à l'actif obligataire n'est pas un risque si elle fait gagner 5 % au passif. Les cadres réglementaires (chapitre 4) raisonnent sur le surplus, pas sur l'actif.

### 7.3.4 Une simulation sur dix ans

Le risque sur un an ne dit pas ce qui se passe sur le long terme : le passif se paie, les taux dérivent, les marchés ont des cycles. On simule donc dix années de plus : à chaque année, la courbe des taux évolue (tirage de douze variations mensuelles de l'historique, courbe positive), les actifs gagnent un rendement annuel tiré dans l'historique, la prestation de l'année est payée par les actifs, le passif restant est **revalorisé** sur la nouvelle courbe. On suit le **taux de couverture** A_k/L_k : il passe sous 1 quand l'actif ne suffit plus à couvrir le passif.

```text
NUM med_mar 1.3818214774806274
NUM q05_mar 0.6501620710381487
NUM pfin_mar 21.8
NUM pjam_mar 48.449999999999996
NUM med_app 1.1428602620319577
NUM q05_app 1.0706587331224326
NUM pfin_app 0.25
NUM pjam_app 0.25
NUM med_mix 1.243340036494016
NUM q05_mix 0.9766938092546391
NUM pfin_mix 6.65
NUM pjam_mix 14.000000000000002
         médiane A/L à 10 ans  5e percentile  P(A/L < 1 à 10 ans) %  P(A/L < 1 un jour) %
Marché                   1.38           0.65                   21.8                  48.4
Apparié                  1.14           1.07                    0.2                   0.2
Mixte                    1.24           0.98                    6.6                    14
```

Résultats pour un taux de couverture initial de 1,10 :

- l'allocation « Marché » a la **meilleure médiane** (1,38) et la pire queue : dans 48 % des trajectoires, le taux de couverture passe sous 1 au moins une fois, et dans 22 % il est encore sous 1 à dix ans ;
- l'allocation « Apparié » a une médiane plus faible (1,14) mais **presque aucun risque** (P(A/L < 1 un jour) = 0,2 %) ;
- l'allocation « Mixte » est intermédiaire : médiane 1,24, probabilité de passer sous 1 un jour de 14 %.


![Taux de couverture (actif / passif) sur dix ans, 2 000 trajectoires simulées, pour trois allocations : médiane (trait), intervalle interquartile (bande foncée) et intervalle 5–95 % (bande claire). La ligne rouge est le seuil de couverture 1.](figures/ch07-alm-dix-ans.png)

Enfin, **le surplus initial est une assurance**. On refait la simulation de l'allocation « Mixte » avec un surplus initial de 5 %, 10 % et 20 % du passif :

```text
NUM pjam_s5 33.95
NUM pjam_s10 14.000000000000002
NUM pjam_s20 1.8499999999999999
      P(A/L < 1 un jour) %  médiane A/L à 10 ans
5 %                     34                  1.16
10 %                    14                  1.24
20 %                   1.8                  1.41
```

La probabilité de passer sous 1 un jour tombe de 34 % (surplus initial de 5 %) à 1,8 % (20 %) : **le capital est le dernier rempart quand la gestion actif-passif n'a pas tout couvert**, ce qui est l'esprit des exigences de fonds propres du chapitre 4.

### 7.3.5 Ce que le modèle ne sait pas faire

Il faut être aussi précis sur les limites que sur les résultats. Les chiffres de cette section dépendent d'hypothèses qui sont **toutes contestables** :

- **Les taux et les actions sont indépendants** dans les données (simulées séparément). Dans la réalité, ils sont corrélés, et cette corrélation peut changer de signe selon l'époque : elle modifie la VaR du surplus, dans un sens ou dans l'autre.
- **Les scénarios sont tirés dans un historique de 10 ans pour les taux et de 16 ans pour les marchés.** Un rééchantillonnage ne crée aucun événement qui ne soit déjà dans l'historique. Le cycle de hausse des taux du mois 60 au mois 90 est le pire mouvement du jeu ; un pire existe sans doute (section 3.2).
- **Le passif est fixe.** Pas de rachats (qui dépendent des taux), pas de garanties de taux, pas d'amélioration de la longévité, pas de frais. Ces ingrédients rendent le passif **optionnel**, et les durations, calculées sur des flux fixes, fausses.
- **Pas de risque de crédit ni d'écart de crédit** : les obligations sont des zéro-coupons sans défaut.
- **Pas de coûts de transaction ni de rééquilibrage dynamique** : les portefeuilles sont rééquilibrés sans frais chaque année.
- **Les rendements espérés sont historiques** et donc bruités (section 7.2.6).
- **La VaR est une convention** : un seuil à 99,5 % sur un an, avec des intervalles d'incertitude larges (section 7.3.3).

Un modèle ALM réel est calibré sur des scénarios économiques générés (modèles de taux, d'actions et d'inflation corrélés), validé de façon indépendante (section 3.4) et revu chaque année. Le but de ce chapitre n'était pas d'en fournir un, mais de faire comprendre **pourquoi** ils sont construits comme ils le sont.

> ✅ **À retenir.** (1) Le critère est le risque du **surplus**, pas celui de l'actif : le portefeuille de variance minimale de l'actif peut être le pire pour le surplus. (2) Le meilleur actif pour un passif est celui qui le **réplique** ; le risque s'ajoute ensuite comme un « dial » dont le gain espéré croît bien plus lentement que le risque. (3) La VaR et l'ES du surplus mesurent la perte de marge de manœuvre ; leur estimation à 99,5 % est incertaine. (4) Sur dix ans, le surplus initial et l'appariement protègent ; l'allocation « de marché » a la meilleure médiane et la pire queue. (5) Toutes ces conclusions dépendent d'hypothèses de modèle (indépendance, passif fixe, historique court) qu'il faut écrire et contester.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : application 7.8 et exercice 7.11.


## Bilan du chapitre 7

Vous savez maintenant :

- **lire un bilan comme deux échéanciers** et distinguer la **valeur économique** (A − L) du résultat courant, et expliquer pourquoi le risque dominant d'un assureur vie est la **baisse** des taux et celui d'une banque de détail la **hausse** ;
- **calculer à la main** la valeur actuelle, la **duration** (Macaulay et modifiée) et la **convexité** d'un échéancier, démontrer ΔP/P ≈ −D_mod Δy + ½ C Δy², et savoir quand l'approximation cesse de valoir (chocs larges, courbe déformée) ;
- **construire le passif d'un portefeuille d'assurance vie** à partir d'une table de mortalité et d'un rapport décès observés / attendus, l'actualiser sur une courbe de taux et en lire la duration (16,2 ans) ;
- **apparier un actif à un passif** en euros (D_A · A = D_L · L), voir pourquoi l'égalité des durations seule est un piège quand A ≠ L, énoncer et vérifier les **conditions de Redington** et comprendre le rôle d'un **haltère** ;
- **mesurer l'exposition à la forme de la courbe** (durations par maturité, pentification, aplatissement) et **rejouer** un historique de taux sur un bilan ; **lire un échéancier de refixation** de banque ;
- **calculer le rendement et le risque d'un portefeuille** (formules matricielles), tracer la **frontière efficiente** à deux puis à cinq actifs, trouver les portefeuilles de **variance minimale** et **tangent**, et décomposer le risque en **contributions d'Euler** ;
- **expliquer le CAPM** comme un langage (bêta, risque systématique) et **douter des estimations** : erreur type des rendements, instabilité des poids, rétrécissement de la covariance (utile à n grand, inutile à n petit) ;
- **montrer que la diversification faiblit en stress** (corrélations qui montent, queues épaisses) ;
- **optimiser pour le surplus plutôt que pour l'actif** (réplication, frontière du surplus), estimer sa **VaR et son expected shortfall** avec leur incertitude, et **simuler** le taux de couverture sur dix ans.

Quelques chiffres à garder de ce chapitre (bilan jouet de la mutuelle, données simulées) :

| Question | Résultat mesuré |
|---|---|
| Duration modifiée du passif | 16,2 ans (convexité 408) |
| Surplus après +1 point de taux, portefeuille de maturité 5 ans | 42 M€ (gain) ; -59 M€ pour −1 point |
| Surplus après ±3 points, haltère apparié en euros | de -1,2 à 0,8 M€ |
| Volatilité du portefeuille de variance minimale (5 actifs) | 4,1 % en moyenne, 3,6 % en calme, 7,9 % en stress |
| Poids des obligations dans le portefeuille tangent selon l'année | de 0 % à 100 % |
| VaR à 99,5 % du surplus : allocation « Marché » contre « Apparié » | 134 M€ contre 5,1 M€ |
| Probabilité de passer sous 1 un jour (10 ans) : « Marché » contre « Apparié » | 48 % contre 0,2 % |

Le fil conducteur du chapitre tient en une phrase : **le risque d'une institution financière est celui de l'écart entre ses promesses et ses placements, et on ne le gère qu'en regardant les deux à la fois**. Un portefeuille « optimal » pour l'actif peut être le pire pour le surplus ; un portefeuille apparié aujourd'hui ne l'est plus quand la courbe se déforme ; une frontière estimée sur dix ans se lit avec ses barres d'erreur. Les mesures de risque du chapitre 3, les exigences de capital du chapitre 4, la mortalité du chapitre 5 et la réassurance du chapitre 6 sont les briques d'un même édifice : ce chapitre en a montré le **plan**.

> ⚠️ **Rappel d'honnêteté.** Toutes les données de ce chapitre sont simulées, les taux et les actions sont indépendants par construction, le passif est un échéancier fixe sans option et les scénarios sont tirés dans un historique court. Les résultats illustrent des **mécanismes** ; ils ne calibrent aucun portefeuille réel et ne constituent pas un conseil en placement.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.1 à 7.8 (prix et duration d'une obligation, passif d'un portefeuille vie, appariement, chocs de courbe, frontière efficiente, contributions au risque, estimation et rétrécissement, surplus et simulation) et exercices 7.1 à 7.12.


---

# Points clés

> « Un risque chiffré n'est utile que si l'on sait de combien le chiffre peut se tromper. »

Ce court chapitre fixe l'essentiel du volume, chapitre par chapitre, puis les idées qui les relient. Le **projet du volume** (le tarif d'une assurance automobile, validé hors période, avec ses notes réglementaires) et une **auto-évaluation** de quarante questions se trouvent dans le cahier d'exercices.

> 📒 **Pour s'entraîner.** Cahier, projet du volume et auto-évaluation : neuf étapes, du cahier des charges au rapport, une variante de score de crédit, puis quarante questions avec corrigés.

## Les points clés, chapitre par chapitre

| Chapitre | Ce que vous devez emporter |
|---|---|
| **1. Risque de crédit et scoring** | Un score est une **cote écrite en points** : classes, poids de l'évidence, régression logistique, échelle (score de base, PDO). On le juge par le **classement** (AUC, **Gini = 2·AUC − 1**, KS), la **calibration** (la probabilité annoncée est-elle la bonne ?) et la **stabilité** (PSI), **hors période**. Les dossiers refusés biaisent la grille (4,4 % annoncés contre 6,0 % réels). ➕ WOE/IV ; **perte attendue = PD × LGD × EAD**, trois étapes IFRS 9, scénarios ; matrices de migration déformées par la conjoncture. |
| **2. Modélisation actuarielle** | Le coût d'un contrat est une **fréquence** (Poisson sur l'**exposition**, sur-dispersion) et une **sévérité** (Gamma, queue de Pareto généralisée) ; **prime pure = fréquence × sévérité**, puis chargements. Un tarif se **valide hors période** (Lorenz, Gini, calibration) et se lit avec le **bruit** : la queue est volatile. Provisionnement : triangle, **chain ladder**, queue, jugement a posteriori. ➕ GLM, crédibilité ; BF, Mack, bootstrap ; santé (sélection adverse, aléa moral). |
| **3. Mesures de risque et stress tests** | La **VaR** est un quantile, l'**expected shortfall** une moyenne de queue : la VaR n'est pas sous-additive, l'ES l'est. La loi normale **sous-estime** la queue, la règle de la racine suppose des pertes indépendantes. Un **stress test** relie un scénario à des pertes ; le stress **inversé** part de la perte inacceptable ; en crise, les **corrélations montent**. ➕ Un quantile à 99,9 % sur dix ans est **instable** ; backtests (Kupiec, Christoffersen, feu tricolore) de **faible puissance** ; la validation et le **risque de modèle**. |
| **4. Cadre réglementaire** | Le capital couvre la **perte inattendue**, la perte attendue se provisionne. **Bâle** : trois piliers, ratios, formule **IRB** (démontrée à partir d'un facteur systématique). **Solvabilité** : meilleure estimation, marge de risque, **SCR agrégé par corrélations** (exact pour des pertes normales seulement). **Takaful** : deux fonds, prêt sans intérêt, supervision charia. ➕ IFRS 17 et plancher de Bâle III ; excédent (wakala, moudaraba, hybride) ; **LAB** : règles à fenêtre de temps, graphes, anomalies, apprentissage supervisé. Les textes se **datent** et se vérifient. |
| **➕ 5. Assurance vie** | Taux de mortalité $m_x=D_x/E_x$, table ($\ell_x$, $d_x$, $e_x$), période ou génération, **Gompertz–Makeham**, rapport **réel/attendu** avec son intervalle. Valeurs actuelles actuarielles : $A_x=1-d\,\ddot a_x$, primes d'équivalence, provisions. **Lee–Carter** : $\ln m_{x,t}=a_x+b_xk_t$, projection de $k_t$ ; la baisse de mortalité **aide** les décès et **pénalise** les rentes ; risque individuel (mutualisable) et de tendance (non). |
| **➕ 6. Réassurance** | On réassure pour **stabiliser**, gagner de la **capacité** et économiser du **capital**, pas pour réduire le coût moyen. **Proportionnel** (quote-part) ou **non proportionnel** (excédent de sinistre). Tarifer une tranche : *burning cost* (ajusté de l'exposition et de l'inflation), **loi de queue**, tarification par l'exposition, avec une incertitude **élevée** sur les tranches hautes. |
| **➕ 7. Actif-passif et portefeuille** | Un bilan est deux échéanciers : **duration**, **convexité**, immunisation $D_A\,A=D_L\,L$ (en euros, pas en durations). **Markowitz** : frontière efficiente, contributions au risque, estimation fragile (rétrécissement), diversification qui **s'érode en stress**. Optimiser le **surplus** plutôt que l'actif ; VaR du surplus, simulation sur dix ans. |
| **Projet (cahier)** | Auditer et découper hors période → fréquence (GLM) → sévérité (écrêtée, mutualisée si le bruit l'emporte) → prime pure validée → tarif → scénarios, capital et réassurance → notes réglementaires → **rapport go / no-go** (critères fixés avant les résultats). |

## Six idées qui traversent tout le volume

> 💡 **Les six idées.**
> 1. **Un chiffre de risque est une convention.** VaR à 99 %, SCR à 99,5 %, formule IRB à 99,9 % : chacun se lit avec son niveau, son horizon et ses hypothèses.
> 2. **L'espérance se facture, la queue se capitalise.** La perte attendue entre dans le prix ou la provision ; la perte inattendue exige du capital, de la réassurance ou des limites.
> 3. **On valide hors période, et on dit l'incertitude.** Un écart entre prévu et réel est d'abord du bruit : on le simule avant de conclure (déciles, quantiles, intervalles).
> 4. **Les queues se trompent le plus, là où ça coûte le plus.** Normalité, quantiles extrêmes, corrélations calmes, tranches hautes : le modèle est moins fiable justement où l'enjeu est le plus grand.
> 5. **Les facteurs communs ne se diversifient pas.** Le hasard individuel s'éteint dans un grand portefeuille ; la conjoncture, l'inflation, la longévité, les corrélations de crise subsistent.
> 6. **Le modèle est une décision, donc un dossier.** Données, hypothèses, validation indépendante, limites, critères de décision écrits à l'avance, textes datés : sans cela, le meilleur modèle n'est pas défendable.

## Et maintenant ?

Vous savez maintenant **chiffrer un risque de crédit, de sinistre, de marché ou de longévité, et défendre ce chiffre** : mesure, validation, scénarios, capital, réassurance. Le **volume VI** (travaux appliqués et portfolio) demande de présenter des travaux réels ; en attendant, le meilleur entraînement est de reprendre **un portefeuille que vous connaissez** et de dérouler la démarche du projet : audit, modèle, validation hors période, scénarios, rapport.

> ✅ **À retenir, tout simplement.** Un modèle de risque ne vaut pas par son ajustement, mais par la **qualité de la décision qu'il éclaire** : un prix, une provision, un capital. Chiffrez, validez, doutez des queues, et écrivez ce que le chiffre ne sait pas.
