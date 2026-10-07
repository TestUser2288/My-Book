# Chapitre 2 : Tests d'hypothèses, tests A/B et corrélation

> « Un écart observé est une question, pas une réponse. »

Le lundi matin, la gérante arrive avec une impression de victoire.

— L'e-mail de la semaine dernière, celui avec le nouvel objet : **3,4 % d'achats contre 2,9 %** pour l'ancien. On le garde pour toutes nos campagnes, non ?

Vous regardez les chiffres. 3,4 est plus grand que 2,9. Mais 12 000 personnes ont reçu l'e-mail, et chaque groupe compte 6 000 contacts : sur 6 000 contacts, 2,9 % font 175 acheteurs, 3,4 % en font 203. Il y a **28 acheteurs de différence**. Est-ce que le nouvel objet les a fait acheter, ou est-ce que le hasard du tirage au sort, d'un groupe à l'autre, a placé 28 acheteurs de plus par chance ?

C'est la question de ce chapitre, et c'est la plus fréquente de toute la vie d'un analyste : **un écart observé est-il réel, ou est-il du bruit ?** Nous répondons avec trois familles d'outils.

- Les **tests d'hypothèses** (section 2.1) donnent une façon disciplinée de dire « cet écart est peu compatible avec le hasard » ou « cet écart pourrait très bien être du hasard », et de **ne pas confondre** les deux.
- Les **tests A/B** (section 2.2) sont des tests d'hypothèses appliqués à une **expérience** : on compare deux versions (un objet d'e-mail, une page de paiement) en les montrant à des groupes tirés au sort. C'est le seul cadre où l'on peut parler de **cause**.
- La **corrélation** (section 2.3) mesure la liaison entre deux variables observées. Elle sert à explorer ; elle ne dit rien de la cause, et nous verrons comment un chiffre élevé peut être trompeur.

Deux sections facultatives complètent : un **catalogue des tests** classiques (2.4) et la **puissance** d'un test, c'est-à-dire la taille d'échantillon dont on a besoin pour avoir une chance de voir ce que l'on cherche (2.5).

## Le chemin de ce chapitre

- **2.1 Tests essentiels et quand les utiliser** : hypothèse nulle, p-valeur (et les cinq façons de la mal comprendre), erreurs de type I et II, intervalle de confiance, et un arbre de décision pour choisir son test.
- **2.2 Tests A/B : conception et lecture des résultats** : préparer un test avant de le lancer, lire le test d'e-mail (non significatif… et pourquoi), vérifier la répartition des groupes sur le test de la page de paiement, éviter les pièges (regarder en continu, comparer dix sous-groupes), décider et rapporter.
- **2.3 Analyse de corrélation** : Pearson, Spearman, Kendall, nuages de points, corrélation fallacieuse, séries temporelles, et le passage (prudent) de la corrélation à la cause.
- **➕ 2.4 Catalogue des tests statistiques** : un tableau de choix et un exemple exécuté pour chaque test classique.
- **➕ 2.5 Analyse de puissance et taille d'échantillon** : combien de personnes interroger ou observer, combien de temps attendre.

> 💡 **Fil conducteur du chapitre.** Un test ne dit pas « cet effet est vrai » ou « faux ». Il répond à une question plus étroite : *si rien ne se passait, verrait-on souvent un écart aussi grand ?* La réponse n'a de sens que si l'expérience était bien conçue, assez grande, et lue une seule fois.

## Les données du chapitre

> 📦 **Les données.** Tout est **simulé** (docstring de `build/donnees_a3.py`), déjà propre, et la **vérité programmée** est connue ; nous la révélerons après chaque analyse, pour que vous puissiez juger ce que la méthode retrouve et ce qu'elle rate.

- `ab_email.csv` : 12 000 contacts d'une liste de diffusion (moitié clients, moitié contacts qui n'ont jamais acheté), tirés au sort entre l'objet **A** (ancien) et **B** (nouveau) ; pour chacun, l'ouverture, le clic, l'achat dans les 7 jours et son montant.
- `ab_site.csv` : environ 38 600 sessions du site pendant trois semaines de juin, avec l'ancienne page de paiement (**A**) ou la nouvelle (**B**), l'appareil utilisé, et si la session a débouché sur une commande.
- `jours_exploitation.csv` : les 1 096 jours de la boutique, avec les commandes, le chiffre d'affaires, la température, la pluie, la promotion du jour et la dépense publicitaire.
- Les tables de la boutique (`commandes.csv`, `lignes_commande.csv`, `retours.csv`, `produits.csv`) pour les exemples du catalogue de tests.

```python hide
import sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
import outils_ch02 as O
from style import setup, BLEU, ORANGE, AQUA, VIOLET, ROUGE, MUET
setup()
d = O.charger()
email, site, jours, cmd, lig, ret, prod = d.email, d.site, d.jours, d.commandes, d.lignes, d.retours, d.produits
print(len(email), "contacts ;", len(site), "sessions ;", len(jours), "jours ;", len(cmd), "commandes")
```
<!--sortie-->
```text
12000 contacts ; 38622 sessions ; 1096 jours ; 36395 commandes
```

Rappel des bases dont ce chapitre a besoin : l'erreur type, l'intervalle de confiance d'une moyenne et d'une proportion, la différence entre corrélation et causalité (volume I, sections 1.3.3, 1.3.4 et 1.4).
