# Chapitre 5 : Présenter à des interlocuteurs non techniques

> « Ce que l'on a trouvé importe moins que ce que l'autre a compris et décidé. »

```python hide
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch05 as O
D = os.environ["DONNEES"]
F = O.faits(D)
SIM = O.simulation_incrementale(F)
print("jours de promotion :", F["jours_promo"], "| sessions :", F["n_sessions"], "| commandes du site :", F["n_cmd_site"])
```
<!--sortie-->
```text
jours de promotion : 153 | sessions : 127022 | commandes du site : 6078
```

Un mardi matin, la gérante passe la tête dans votre bureau. « La réunion de direction est **jeudi de la semaine prochaine**. J'ai inscrit le point des soldes à l'ordre du jour. **Tu as dix minutes.** Il y aura le responsable logistique, la comptable, et le représentant de la banque qui suit notre dossier. Dis-leur ce que tu as trouvé, et dis-leur ce qu'on doit faire. »

Vous avez fait le plus dur : l'analyse est terminée, vérifiée par plusieurs méthodes, et vous en êtes fier. Elle tient en quarante pages de résultats, dont une régression, un contrefactuel de marge, une simulation et un seuil de bascule. Et c'est ici que beaucoup d'analystes **perdent** ce qu'ils ont gagné : ils présentent **ce qu'ils ont fait** au lieu de ce que **l'autre doit en retenir**, ils parlent de la méthode alors qu'on leur demande une décision, ou ils disent « il y a une incertitude » d'un air gêné alors qu'on attend « voici ce qu'il faut faire, et voici la marge d'erreur ».

Ce chapitre ne contient presque pas de calcul : il traite de la **parole**, de l'**écoute** et de la **préparation**. Les deux premières sections suivent votre semaine de préparation ; les deux dernières, facultatives, regardent en amont (comprendre ce qu'on vous demande) et plus largement (négocier, collaborer, rester honnête).

## Le chemin de ce chapitre

- **5.1 Comprendre son public.** Qui est dans la salle, ce que chacun sait, veut et craint ; comment dire **le même résultat** à trois personnes différentes ; comment traduire le jargon en phrases claires ; comment rendre un support lisible (daltonisme, projection) ; ce qui change à distance.
- **5.2 Présenter résultats et recommandations.** Une présentation de dix minutes : la **réponse d'abord**, trois preuves, une recommandation que l'on peut exécuter, la décision demandée ; comment parler de l'**incertitude** sans perdre la salle ; comment traiter les questions, les objections, le chiffre qui déplaît et l'erreur découverte en séance ; le compte rendu en cinq lignes.
- **5.3 ➕ Recueil des besoins, entretiens avec les parties prenantes, formulation de la question métier.** De « je veux un tableau de bord » à une question que l'on peut tester ; l'entretien structuré ; la fiche de cadrage.
- **5.4 ➕ Compétences transversales.** Raconter, négocier (dire non sans fermer la porte), collaborer avec les équipes métier, gérer un désaccord sur un chiffre, éthique professionnelle, retours d'expérience, développement de carrière.

> 💡 **Intuition.** Présenter, c'est **traduire** : de votre langue (la méthode, l'incertitude, les hypothèses) vers celle de l'autre (la décision, le risque, l'argent, le temps). Une bonne traduction ne perd rien d'important, mais elle ne garde que ce qui est nécessaire pour décider.

## Les données du chapitre

Ce chapitre ne produit pas de nouvelle analyse : il **présente** celles des volumes précédents. Les nombres qui servent d'exemples viennent de la boutique simulée (volume III) : l'effet des promotions sur les commandes et sur la marge (volume III, projet du volume), les retards de livraison par transporteur et par mois (volume III, chapitre 11), la conversion du site par source (volume III, chapitre 10) et le budget 2025 (volume III, chapitre 7). Tout est **simulé** ; la vérité programmée est celle des générateurs du volume III. Chaque nombre cité est recalculé par un bloc exécuté, souvent caché.

Pour les dialogues et les scénarios, les personnes sont désignées **par leur fonction** (la gérante, le responsable logistique, la comptable, le financeur) : aucun nom, aucune entreprise réelle n'apparaît.
