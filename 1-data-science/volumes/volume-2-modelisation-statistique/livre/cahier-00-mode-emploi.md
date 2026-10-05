# Mode d'emploi

> « On comprend en lisant, on retient en pratiquant. »

Ce cahier est le **compagnon du livre** du volume II (*Modélisation statistique*). Le livre explique les idées ; le cahier les fait travailler. Il contient, chapitre par chapitre, des **applications guidées** sur données, des **exercices** et leurs **corrigés**, puis le **projet du volume** et l'auto-évaluation.

## Comment utiliser ce cahier

1. **Lisez d'abord la section du livre.** Chaque section qui a un prolongement ici se termine par une ligne de ce genre :
   > 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.1, exercices 2.1 à 2.4.
2. **Essayez avant de regarder le corrigé.** Les énoncés sont regroupés dans la partie *Exercices*, les corrigés dans la partie *Corrigés* du même chapitre : on peut ainsi chercher sans voir la réponse.
3. **Tapez le code vous-même** plutôt que de le copier : modifiez-le, cassez-le, lisez les messages d'erreur. C'est la seule façon d'apprendre à programmer.
4. **Faites les applications dans l'ordre** : chacune raconte une petite étude, avec une question, des étapes, du code et une lecture des résultats.

## Numérotation et niveaux

Chaque chapitre du cahier correspond au chapitre du livre de même numéro.

| Élément | Numérotation | Exemple |
|---|---|---|
| Application | `Application N.k` | Application 2.1 : première application du chapitre 2 |
| Exercice | `Exercice N.k` | Exercice 2.3 : troisième exercice du chapitre 2 |
| Corrigé | `Corrigé N.k` | Corrigé 2.3 : correction de l'exercice 2.3 |

La difficulté des exercices est indiquée par des étoiles :

| Niveau | Signification |
|---|---|
| ⭐ | application directe d'une formule ou d'une idée vue dans la section |
| ⭐⭐ | demande de combiner deux idées, ou un petit raisonnement |
| ⭐⭐⭐ | demande de la réflexion, une démonstration ou une petite simulation |

Un exercice cite la section du livre qu'il exerce, par exemple « (section 1.2) ».

## Données et environnement

Les données sont celles du livre, dans le dossier `donnees/` :

| Fichier | Contenu |
|---|---|
| `clients.csv` | 2 000 clients : âge, ville, canal d'acquisition, offre de bienvenue (tirée au sort), commandes, dépense, rachat, durée de la relation |
| `enquete_satisfaction.csv` | huit questions de satisfaction pour 1 212 répondants |
| `ventes_mensuelles.csv` | chiffre d'affaires mensuel, 2016 à 2025 |

Certains chapitres ajoutent leurs propres jeux (par exemple `ch07-*.csv`) : ils sont fournis, et le script qui les produit se trouve dans `build/`. Toutes les données sont **simulées**, avec des graines fixes : vos résultats seront identiques à ceux du livre.

Chaque chapitre du cahier est **autonome** : il commence par recharger ses données et refaire ses imports, de sorte qu'on peut le faire sans avoir exécuté rien d'autre. Les installations nécessaires sont décrites à la fin du livre, section « L'environnement de travail ».

## Lancer le code

Placez-vous dans le dossier du volume (celui qui contient `donnees/`), car les chemins sont relatifs (`donnees/clients.csv`). Vous pouvez travailler dans un notebook Jupyter, dans un éditeur avec la commande `python`, ou dans un terminal interactif. Les blocs de R se lancent depuis le même dossier.

> ⚠️ **Les chemins.** Si Python répond `FileNotFoundError`, c'est presque toujours que vous n'êtes pas dans le bon dossier : vérifiez avec `import os; print(os.getcwd())`.

## Vérifier son installation

Avant de commencer, ce court bloc vérifie que les données sont trouvées et que les bibliothèques principales sont installées.

```python
import pandas as pd, numpy as np, scipy, statsmodels, sklearn
clients = pd.read_csv("donnees/clients.csv")
print(clients.shape)
print("statsmodels", statsmodels.__version__)
```
<!--sortie-->
```text
(2000, 12)
statsmodels 0.15.0
```

Vous devez lire `(2000, 12)`, puis une version de `statsmodels`. Si le chargement échoue, relisez l'encadré précédent ; si une bibliothèque manque, installez-la avec `pip install statsmodels scikit-learn` (voir le livre).

## Plan du cahier

| Chapitre | Contenu |
|---|---|
| 1. Régression linéaire | applications et exercices sur les moindres carrés, l'inférence, les diagnostics, la sélection de variables, la régularisation |
| 2. Modèles linéaires généralisés | logistique, comptages, montants positifs, déviance |
| 3. Analyse multivariée | ACP, analyse factorielle, classification |
| 4. Séries temporelles | stationnarité, ARIMA, prévision |
| 5. Analyse de survie | Kaplan-Meier, Cox, modèles paramétriques |
| 6. Statistique bayésienne et simulation | lois a priori, Monte-Carlo, MCMC |
| 7 à 9 (facultatifs) | inférence causale, plans d'expériences, statistique spatiale |
| Projet et auto-évaluation | le plan de l'année suivante de la boutique, puis 42 questions pour vérifier ses acquis |
