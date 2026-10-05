# Chapitre 9 : ➕ Bases de l'apprentissage par renforcement

> « Personne n'apprend à faire du vélo en lisant un manuel : on tombe, on ajuste, on recommence. »

> 🧭 **Chapitre complémentaire.** Ce chapitre est entièrement facultatif : on peut lire le volume sans lui. Il suppose le chapitre 1 (démarche d'évaluation) et s'appuie sur trois résultats des volumes précédents : les chaînes de Markov (volume I, section 2.6.2), le test A/B (volume I, section 3.4.5) et la mise à jour bayésienne d'une probabilité (volume II, section 6.1). Il est indépendant des chapitres 2 à 8.

Jusqu'ici, dans ce volume, un modèle recevait un **tableau de données déjà constitué** et apprenait à prédire une colonne. Personne ne se demandait *comment* ces données avaient été produites. Dans la vie d'une boutique, pourtant, beaucoup de questions sont d'une autre nature :

- **Quelle bannière afficher** sur la page d'accueil, sachant que l'on ne connaît pas à l'avance celle qui convertit le mieux, et que chaque affichage « gaspillé » sur une mauvaise bannière coûte des ventes ?
- **Quand et combien commander** pour ne pas tomber en rupture, sans immobiliser de la marchandise qui ne se vendra pas ?
- **Quelle offre envoyer** à quel client, et à quel moment du cycle de vie, pour qu'il devienne fidèle ?

Dans chaque cas, on **agit**, le monde **répond** (une vente, une rupture, un abandon), et la réponse dépend de ce que l'on a fait. Les données que l'on recueillera demain dépendent des décisions d'aujourd'hui. C'est le terrain de l'**apprentissage par renforcement** (*reinforcement learning*, RL) : apprendre, par essais et erreurs, **une façon d'agir** qui maximise une récompense cumulée.

## Le chemin de ce chapitre

- **9.1 Processus de décision markoviens** : le vocabulaire (agent, état, action, récompense), la notion de **retour actualisé**, les **équations de Bellman** démontrées, et un premier algorithme, l'**itération de la valeur**, calculé à la main sur un exemple à trois états.
- **9.2 Bandits manchots** : le cas le plus simple, sans état, où le seul enjeu est le dilemme **explorer ou exploiter**. On compare le test A/B, ε-glouton, UCB et l'échantillonnage de Thompson sur quatre bannières.
- **9.3 Q-learning** : apprendre sans connaître les règles du jeu. On démontre la règle de mise à jour, on oppose **Q-learning et SARSA**, et on apprend à gérer un petit stock.
- **9.4 Du Q-learning à l'apprentissage profond** : pourquoi la table ne suffit plus, ce que changent les réseaux de neurones, et les précautions (récompenses mal posées, sécurité, éthique). Section de lecture, sans exécution.

## Ce qui change par rapport à l'apprentissage supervisé

| | Apprentissage supervisé (chapitres 1 à 5) | Apprentissage par renforcement |
|---|---|---|
| **Ce qu'on reçoit** | des exemples étiquetés : l'entrée **et** la bonne réponse | une **récompense** après l'action, souvent différée et partielle |
| **D'où viennent les données** | elles préexistent (le tableau est donné) | elles dépendent des **décisions prises** : l'agent influence ce qu'il observe |
| **Ce qu'on apprend** | une fonction qui prédit | une **politique** : quelle action prendre dans quel état |
| **Difficulté propre** | le surapprentissage | l'**attribution du crédit** (quelle action passée explique ce gain ?) et l'**exploration** |
| **Évaluation** | un jeu de test mis de côté | la récompense cumulée obtenue **en agissant** |

Le point de départ est donc le même (des données, un objectif), mais deux difficultés nouvelles apparaissent : **le feedback est retardé** (la commande passée aujourd'hui ne montre son effet que dans trois jours) et **les données sont biaisées par nos propres choix** (on n'observe pas ce qui serait arrivé avec l'autre bannière).

## Trois petits mondes pour tout le chapitre

Les chapitres précédents travaillaient sur des tableaux de clients. Ici, l'apprentissage par renforcement a besoin d'un **environnement** avec lequel interagir. Aucune bibliothèque dédiée n'est nécessaire : nous écrivons à la main trois environnements simples. Ils sont **simulés** (graines fixes, déclarées à chaque fois), et nous connaissons donc les vrais paramètres, ce qui permet de vérifier ce que l'algorithme apprend.

| Environnement | Section | Question | Graine(s) |
|---|---|---|---|
| **Quatre bannières** | 9.2 | laquelle afficher, sachant que les taux de conversion (4,0 ; 5,2 ; 5,8 et 7,0 %) sont inconnus ? | 900 (200 répétitions), 4, 1 et 77 |
| **Le cycle de vie d'un client** (3 états) et **le stock** (5 états) | 9.1, 9.3 | quelle action dans quel état ? | 1 (évaluation), 5 et 100 à 109 (apprentissage) |
| **Un couloir d'entrepôt** (grille 4 × 10) | 9.1, 9.3 | comment traverser sans entrer dans la zone dangereuse ? | 0 à 9 et 3 |

> 📦 **Pas de données à charger.** Ce chapitre n'utilise aucun fichier : tout est simulé dans le texte et dans les blocs de calcul. Les mêmes environnements, avec leur code complet, sont reconstruits pas à pas dans le cahier.

> ⚠️ **Un chapitre d'introduction, pas un manuel d'ingénierie.** L'apprentissage par renforcement « pour de vrai » (robotique, jeux, recommandation en ligne à grande échelle) demande des simulateurs, beaucoup de calcul et une grande prudence. Nous voulons ici comprendre **les idées** et leurs limites, sur des problèmes assez petits pour être résolus **exactement** et ainsi comparés à ce que l'apprentissage trouve.

```python hide
import sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
sys.path.insert(0, "build")
import style
from style import BLEU, ORANGE, AQUA, VIOLET, ROUGE, ENCRE2, MUET
style.setup()
RNG_INFO = "les graines sont déclarées dans chaque bloc de calcul"
```
