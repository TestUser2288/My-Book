# Points clés

> « Un modèle qui répond toujours n'est pas un modèle qui a toujours raison. »

Ce court chapitre fixe l'essentiel du volume, chapitre par chapitre, puis les idées qui les relient. Le **projet du volume** (déployer un modèle avec un pipeline et une supervision) et une **auto-évaluation** de quarante questions se trouvent dans le cahier d'exercices.

> 📒 **Pour s'entraîner.** Cahier, projet du volume et auto-évaluation : huit étapes, de la structure du projet au rapport de mise en production, puis quarante questions avec corrigés.

## Les points clés, chapitre par chapitre

| Chapitre | Ce que vous devez emporter |
|---|---|
| **1. Deep learning** | Un réseau est un empilement de **fonctions simples dérivables** que la **rétropropagation** ajuste par gradient ; on sait la calculer à la main et la vérifier. Les gradients peuvent disparaître (ReLU, initialisation), le **pas d'apprentissage** reste décisif, la **régularisation** se juge sur plusieurs graines. Le **convolutif** exploite des pixels voisins, le **récurrent** une suite ordonnée. Sur un tableau, le **boosting** reste difficile à battre. |
| **2. NLP et modèles de langage** | Tout le progrès du texte est une meilleure manière de **transformer des mots en vecteurs** : comptage, TF-IDF, plongements, **attention**. Une référence simple (TF-IDF + logistique) et un **test qui sort du moule** valent mieux qu'un grand modèle jugé sur des phrases semblables à l'entraînement. Un modèle de langage **prédit un jeton suivant** ; le **pré-entraînement** fait la généralisation ; l'hallucination, la confidentialité et le coût restent des limites. Un **RAG** s'évalue maillon par maillon, et la sécurité d'un **agent** est dans son harnais. |
| **3. Big data et calcul distribué** | **Distribuer est un moyen, pas un but** : son coût se mesure en données qui voyagent (le **mélange**). Une machine qui suffit vaut mieux que dix qui se coordonnent ; DuckDB ou pandas suffisent souvent. **MapReduce** marche parce que la combinaison est **associative** ; la **loi d'Amdahl** borne le gain. Avec Spark, on lit le **plan** ; on traite l'**asymétrie des clés** et les **petits fichiers**. Sous « au moins une fois », on écrit des traitements **idempotents**. |
| **4. MLOps** | **Un modèle de ML échoue en silence.** Un seul **pipeline** pour l'entraînement et le service, des **tests** qui bloquent, des entrées **validées**, un déploiement **par paliers** avec **retour arrière**, une **supervision** à quatre couches. La **dérive des variables** et la **dérive du concept** ne se voient pas aux mêmes indicateurs : le PSI repère l'une, seule la performance (ou la calibration) repère l'autre. |
| **5. Ingénierie des données** | Une donnée n'est fiable que si **chaque transformation est explicite, mesurée et rejouable**. **Rien ne se perd en silence** (équation de conservation), un chargement est **rejouable** (clé, fusion), la qualité se **mesure** par dimensions, les rapprochements se jugent par **précision et rappel** avec une file de revue. Un hachage nu ne protège pas : il faut une **clé secrète**. |
| **➕ 6. Plateformes cloud** | Le cloud **échange de l'investissement contre de la dépendance et de la vigilance**. On raisonne par **seuils** (réserver le socle, louer la pointe), on surveille les **frais de sortie**, on applique le **moindre privilège**, et les prix du chapitre sont **inventés** : ce sont les hypothèses qui comptent. |
| **➕ 7. Applications de démonstration** | Une démonstration réussie se montre **sans mentir** et se refait **sans l'auteur**. Entrées bornées, **incertitude** affichée, explication dont la somme reproduit le score, test **sans navigateur**, secrets hors du code. Quand un autre programme a besoin du modèle, on passe à une **API**. |
| **Projet (cahier)** | Structurer et configurer → pipeline testé → suivre les essais et enregistrer → servir par une API qui valide → journaliser et superviser → mesurer la dérive et décider d'un réentraînement → automatiser → **rapport de mise en production** (go / no-go). |

## Six idées qui traversent tout le volume

> 💡 **Les six idées.**
> 1. **La structure des données dicte l'architecture.** Pixels, suites, texte : le réseau convient quand il sait exploiter une structure ; sur un tableau, une référence simple reste redoutable.
> 2. **On mesure avant de croire.** Une référence simple, un test qui sort du moule, un écart accompagné de son incertitude : les chiffres de ce volume contredisent parfois l'enthousiasme.
> 3. **Le coût d'une donnée ou d'un calcul est celui de son déplacement.** Mélange entre machines, frais de sortie, décalage entre entraînement et service : ce qui voyage coûte et se déforme.
> 4. **Ce qui apprend ou calcule passe par un seul chemin.** Un pipeline, un contrat de données, un registre : deux chemins finissent toujours par diverger.
> 5. **Les pannes les plus graves sont silencieuses.** Un défaut d'unité, une dérive du concept, un résultat vide : aucune exception, mais une décision dégradée. On teste les entrées, on supervise les sorties.
> 6. **Tout se rejoue, tout se retire.** Idempotence, alias de version, retour arrière, graines et versions figées : on ne met en production que ce que l'on peut refaire et défaire.

## Et maintenant ?

Vous savez maintenant **entraîner un réseau, traiter du texte, passer à l'échelle, déployer et surveiller un modèle**, et fiabiliser les données qui l'alimentent. Les volumes suivants poursuivent selon le plan de la série ; en attendant, le meilleur entraînement est de reprendre **un de vos propres jeux de données** et de dérouler la démarche du projet : référence simple, pipeline testé, mise à disposition, supervision.

> ✅ **À retenir, tout simplement.** Un modèle en production, ce n'est pas un fichier : c'est **un pipeline testé, des données maîtrisées, un service qui valide, une supervision qui regarde et un moyen de revenir en arrière**. Le modèle n'en est qu'une brique.
