# Mode d'emploi

> « On ne sait pas si un pipeline marche tant qu'on ne l'a pas cassé exprès. »

Ce cahier est le **compagnon du livre** du volume V (*Analytique avancée et automatisation*). Le livre explique les principes ; le cahier les fait travailler. Il contient, chapitre par chapitre, des **applications guidées**, des **exercices** et leurs **corrigés**, puis le **projet du volume** (un pipeline de reporting automatisé qui alimente un tableau de bord) et l'**auto-évaluation**. Dans ce volume, la plupart des exercices demandent d'**écrire, d'exécuter ou de réparer** un morceau de système : une requête, une étape de chargement, un contrôle, un modèle, un état de reporting.

## Comment utiliser ce cahier

1. **Lisez d'abord la section du livre.** Chaque section qui a un prolongement ici se termine par une ligne de ce genre :
   > 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.1, exercices 1.1 à 1.4.
2. **Exécutez, puis cassez.** Pour un pipeline, un contrôle ou une requête : faites-le tourner, puis provoquez une panne (fichier vide, doublon, colonne renommée) et regardez ce qui se passe. C'est l'habitude centrale du volume.
3. **Écrivez le contrôle avant le calcul.** Pour chaque chiffre produit, demandez-vous : *par quel autre chemin pourrais-je retrouver ce chiffre ?*
4. **Essayez avant de regarder le corrigé.** Les énoncés sont regroupés dans la partie *Exercices*, les corrigés dans la partie *Corrigés* du même chapitre.
5. **Gardez une trace.** Notez ce que vous avez essayé et ce qui a échoué : un journal des essais fait partie de la démarche.

## Numérotation et niveaux

Chaque chapitre du cahier correspond au chapitre du livre de même numéro.

| Élément | Numérotation | Exemple |
|---|---|---|
| Application | `Application N.k` | Application 1.1 : première application du chapitre 1 |
| Exercice | `Exercice N.k` | Exercice 1.3 : troisième exercice du chapitre 1 |
| Corrigé | `Corrigé N.k` | Corrigé 1.3 : correction de l'exercice 1.3 |

| Niveau | Signification |
|---|---|
| ⭐ | application directe d'une idée ou d'un geste vu dans la section |
| ⭐⭐ | demande de combiner deux idées, ou un petit raisonnement |
| ⭐⭐⭐ | demande de la réflexion, un choix de conception ou une petite expérience |

Un exercice cite la section du livre qu'il exerce, par exemple « (section 1.2) ».

## Données et environnement

Les données sont celles du livre, dans le dossier `donnees/` : les jeux de la boutique (volume III), l'assureur et la banque fictifs (chapitre 4) et les petits jeux propres à chaque chapitre. Elles sont toutes **simulées**, avec des graines fixes (script `build/donnees_a5.py`) : vos résultats seront identiques à ceux du livre. Le catalogue complet figure dans la section « Carte du volume, données et environnement ». Chaque chapitre du cahier est **autonome** : il recharge ses données et ne dépend d'aucun autre.

> ⚠️ **Prudence.** Les exercices de pipeline écrivent dans un dossier temporaire et jamais dans `donnees/`. Si vous adaptez un exercice à vos propres données, travaillez sur une **copie**.

## Auto-évaluation et projet

Le dernier chapitre du cahier regroupe le **projet du volume**, en étapes, et **quarante questions d'auto-évaluation** avec corrigés. Le projet reprend les gestes de tout le volume : modéliser, charger, contrôler, calculer, présenter, planifier.
