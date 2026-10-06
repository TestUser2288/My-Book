## Bilan du chapitre 4

Vous savez maintenant :

- **rendre un modèle reproductible** : graines, versions, empreinte des données, configuration, et un **pipeline** unique qui enchaîne préparation et modèle ;
- **tester un système de ML** : tests de données (schéma, plages), de comportement (déterminisme, absence de fuite) et de non-régression, qui doivent **bloquer** quelque chose quand ils échouent ;
- **reconnaître le décalage entraînement-service** et en mesurer l'effet : une erreur d'unité ne plante rien, elle dégrade la décision sans bruit ;
- **choisir un mode de service** (lots, ligne, flux, embarqué), raisonner sur la **latence** (centiles) et le **débit** (loi de Little $L=\lambda W$), **sérialiser** (le danger de `pickle`, la parité ONNX) et **exposer** un modèle par une API validée ;
- **introduire une version par paliers** (fantôme, canari, test A/B) avec un routage déterministe, **dimensionner** un test A/B et **revenir en arrière** par un alias ;
- **superviser** quatre couches (système, données, scores, métier), **journaliser** les prédictions, composer avec des **étiquettes tardives**, estimer la performance **sans étiquettes** (et savoir quand cette estimation est aveugle) et **régler des alertes** en connaissant le prix des fausses alarmes ;
- (en option) **orchestrer** un graphe de tâches avec reprises, **idempotence** et rattrapage, **suivre les essais** et gérer un **registre de modèles**, **versionner les données** par leur empreinte, **automatiser la livraison** (CI/CD, conteneurs, Kubernetes), concevoir une **API REST** sûre, et **mesurer la dérive** (PSI, Kolmogorov-Smirnov) en distinguant dérive des variables et dérive du concept.

Le chapitre a mis quelques chiffres sur des idées qui restent souvent abstraites :

| Ce que l'on a vu | Mesure sur la résiliation |
|---|---|
| Un défaut d'unité dans l'entrée du service | l'AUC passe de 0,867 à 0,538 sans aucune erreur visible |
| Combien de clients pour départager deux versions | environ 5 800 clients par groupe pour un écart de 7,9 points de précision |
| Estimation sans étiquettes, dérive du concept | 63 % annoncés, 10 % réels |
| Dérive des variables, quatre semaines | PSI de 0,02 à 0,79, mais AUC de 0,876 à 0,857 |
| Dérive du concept, quatre semaines | PSI toujours sous 0,02, mais AUC de 0,876 à 0,776 |

Quatre leçons dépassent ce chapitre. **Un modèle de ML échoue en silence** : il répond toujours, et les erreurs graves n'ont ni exception ni alarme ; c'est pourquoi on teste les entrées et on supervise les sorties. **Tout ce qui est appris ou calculé doit passer par un seul chemin** : un pipeline unique pour l'entraînement et le service, un registre qui relie une version à ses données et à son code. **Introduire, c'est mesurer, et mesurer demande du temps et des volumes** : un canari achète de l'information au prix du risque, et la performance réelle n'arrive qu'après le délai de l'étiquette. Enfin, **la dérive la plus coûteuse est souvent celle que l'on ne voit pas dans les entrées**, notamment quand le modèle sert à agir et modifie lui-même ce qu'il prédit : le seul remède est de **conserver une mesure indépendante** (un groupe témoin).

> 🧭 **En pratique : liste de contrôle avant la mise en production.**
> 1. L'entraînement se refait à l'identique (graines, versions, hash des données, 4.1).
> 2. Préparation et modèle sont **un seul objet**, testés par un test de parité (4.1).
> 3. Les entrées du service sont **validées** (type et bornes, 4.2) et le contrat de l'API est testé (4.6).
> 4. Le modèle n'est chargé que depuis une source maîtrisée (4.2), l'accès est authentifié et limité en débit (4.6).
> 5. Le déploiement est **progressif** (fantôme, canari) avec un **retour arrière** par alias (4.2, 4.5).
> 6. Chaque prédiction est **journalisée** avec la version du modèle (4.3).
> 7. Des alertes **réglées** sur les entrées, les scores et les erreurs existent, avec un responsable et un runbook (4.3).
> 8. La performance réelle est mesurée **quand les étiquettes arrivent**, avec un **groupe témoin** si le modèle agit (4.3, 4.7).
> 9. Une **politique de ré-entraînement** écrite dit quand, avec quelles données, et par quelle porte de qualité (4.6, 4.7).

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 à 4.9 (batterie de tests, API de scoring, canari avec retour arrière, journal et étiquettes tardives, orchestration avec reprises, suivi MLflow, porte de qualité, mois de production simulé, et une **chaîne complète** de bout en bout) et exercices 4.1 à 4.12.

Le chapitre 5 remonte en amont de tout cela : avant le modèle, il y a **la donnée**, et la qualité de ce qu'elle apporte dépend de **l'ingénierie des données** (extraction, transformation, chargement, tests de qualité). Le chapitre 6 replace ces briques dans les services d'un **fournisseur de cloud** (mise à l'échelle, coûts, sécurité), et le chapitre 7 montre comment présenter un modèle servi, comme celui de ce chapitre, dans une **application** que des non-spécialistes peuvent utiliser.

```python hide
mlflow.end_run() if mlflow.active_run() else None
shutil.rmtree(WORK, ignore_errors=True)
print("dossier temporaire supprimé :", not os.path.exists(WORK))
```
<!--sortie-->
```text
dossier temporaire supprimé : True
```
