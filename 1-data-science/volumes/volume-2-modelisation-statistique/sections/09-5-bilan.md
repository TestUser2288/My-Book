## Bilan du chapitre 9

Vous savez maintenant :

- distinguer les **trois familles** de données spatiales (géostatistique, surfacique, semis de points) en se demandant *qu'est-ce qui est aléatoire ?* ;
- repérer un point et **mesurer une distance** correctement (haversine, projection locale) et dessiner une carte honnête sans fond de carte ;
- **définir un voisinage** par une matrice de poids et mesurer l'**autocorrélation** avec les indices de **Moran** et de **Geary**, les tester par **permutations**, et localiser les îlots avec les indices locaux (LISA) en **corrigeant** les tests multiples ;
- expliquer pourquoi ignorer l'autocorrélation fait **rejeter à tort** (46 % de faux positifs au lieu de 5 % dans notre simulation) et la tester sur les **résidus** d'un modèle ;
- estimer et ajuster un **variogramme** (pépite, palier, portée), connaître ses incertitudes, et **prédire par krigeage** avec une variance d'erreur, en validant par **validation croisée** ;
- étudier un **semis de points** par quadrats, plus proche voisin et **fonction $K$ de Ripley**, avec une **enveloppe de Monte-Carlo** et une **correction de bord**.

Ce chapitre a aussi rassemblé les **limites** qui reviennent à chaque étape :

| Limite | Où elle apparaît | Précaution |
|---|---|---|
| **Effet de bord** | plus proche voisin (biais de $R$), fonction $K$, indices locaux | correction (Donnelly, méthode du bord), enveloppe de Monte-Carlo dans la même fenêtre, examiner les bords à part |
| **Problème de l'unité spatiale modifiable** | corrélations et indices calculés sur des zones | indiquer le découpage, tester plusieurs échelles, ne pas transposer à l'individu |
| **Non-stationnarité** | variogramme, krigeage | retirer ou modéliser la tendance (krigeage universel) |
| **Anisotropie** | variogramme | variogrammes directionnels, **calibrés** par simulation |
| **Densité variable** | fonction $K$ | $K$ inhomogène ; ne pas confondre premier et second ordre |
| **Variogramme estimé, pas connu** | barres d'erreur du krigeage | validation croisée avec réajustement, prudence sur les intervalles |

> ✅ **Si vous ne deviez retenir qu'une idée.** *L'espace n'est pas une colonne de plus dans le tableau : il change la nature de l'information.* Des observations voisines ne sont pas indépendantes, donc : définissez le voisinage, mesurez la dépendance, vérifiez-la dans les résidus, et attribuez-lui une incertitude honnête.

> 🧭 **Pour aller plus loin** (hors de ce chapitre) : les modèles de régression spatiale (*spatial lag* et *spatial error*, par maximum de vraisemblance), le krigeage universel et le co-krigeage, les modèles géostatistiques bayésiens, la fonction $K$ inhomogène et les modèles de Cox log-gaussiens pour les semis de points, la statistique spatio-temporelle. Ces extensions reposent exactement sur les trois idées que vous venez de pratiquer : un **voisinage**, une **fonction de dépendance** et une **comparaison à un hasard bien défini**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : applications 9.1 à 9.7 et exercices 9.1 à 9.12.
