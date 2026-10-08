# Chapitre 3 : Introduction à l'analytique prédictive

> « Prédire, ce n'est pas deviner : c'est dire ce que l'on s'attend à voir, et de combien on peut se tromper. »

```python hide
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch03 as O
import fig_ch03 as F

D = os.environ["DONNEES"]
d = O.charger(D)
print("commandes :", len(d["cmd"]), "| clients :", len(d["cli"]), "| mois :", len(d["M"]), "| janvier 2025 :", int(d["M"].loc["2025-01"]))
assert len(d["cmd"]) == 36395 and len(d["M"]) == 36 and int(d["M"].loc["2025-01"]) == 963
```
<!--sortie-->
```text
commandes : 36395 | clients : 6000 | mois : 36 | janvier 2025 : 963
```

Un lundi de décembre, la gérante passe la tête dans votre bureau. Elle a deux questions, et elle les pose comme on pose des questions simples :

> « *Combien de commandes aurons-nous en janvier ? J'ai des équipes à placer. Et puis… quels clients ne reviendront probablement plus ? Je voudrais leur écrire avant qu'il soit trop tard.* »

Ces deux questions se ressemblent par la grammaire (« aurons-nous », « reviendront ») et par rien d'autre. La première demande **un nombre** : combien de commandes, avec quelle marge d'erreur. La seconde demande **une probabilité par personne** : pour chaque client, quelle chance de revenir. Dans les deux cas, on ne décrit pas le passé et on n'explique pas non plus pourquoi il s'est passé : on **annonce** ce qui n'est pas encore arrivé. C'est le sujet de ce chapitre.

Les volumes précédents vous ont appris à décrire (volume II), à expliquer et à estimer un effet (volume III). Vous savez déjà tout ce qu'il faut pour **construire** un modèle prédictif : une régression, une série temporelle, une régression logistique. Ce qui change, c'est la **façon de le juger** et **l'usage qu'on en fait**. Un modèle qui explique bien le passé peut prédire mal l'avenir ; un modèle qui prédit bien peut ne servir à aucune décision ; et il est très facile de se tromper soi-même sans le savoir, en laissant le modèle voir un peu de l'avenir qu'il prétend prédire.

> 💡 **Intuition.** Une prévision n'est pas un oracle, c'est une **promesse chiffrée** que l'on peut vérifier. On la fait **avant**, on la compare à la réalité **après**, et l'on garde le modèle seulement s'il fait mieux qu'une règle de bon sens (la « référence naïve »). Tout ce chapitre en découle.

Vous écrivez ici en **analyste**, pas en spécialiste de l'apprentissage automatique. Cela veut dire : peu de modèles, bien choisis, **bien évalués**, expliqués à la gérante, et reliés à une **décision**. Les algorithmes sophistiqués (forêts, boosting, réseaux de neurones) sont l'affaire de la science des données ; la série 1 de cette collection (indépendante de celle-ci : vous n'avez pas besoin de l'avoir lue) leur est consacrée. La section 3.3 vous apprend justement à **reconnaître le moment** où il faut leur passer la main, et à bien préparer la passation.

## Le chemin de ce chapitre

Le chapitre suit les deux questions de la gérante, puis la question « que faire d'un modèle ? ».

- **3.1 Ce qu'apporte l'analytique prédictive.** Quatre sortes de questions (décrire, diagnostiquer, prédire, prescrire), la différence entre **prédire, expliquer et décider**, la **valeur d'une prévision** (c'est la décision qu'elle change, calculée en euros), l'horizon, la granularité, la fraîcheur, et la **référence naïve** que tout modèle doit battre.
- **3.2 Modèles prédictifs simples.** Deux cas complets sur la boutique. **Cas A**, combien de commandes en janvier : références saisonnières, régression de comptage, jugement par **origine glissante**, prévision avec fourchette. **Cas B**, quels clients rachètent dans les 90 jours : construire la cible, ne regarder que le passé, séparer **dans le temps**, régression logistique et arbre, AUC, calibration, courbe de gain, **fuite d'information**, et choix de qui contacter **selon les coûts**.
- **3.3 Quand passer la main à la data science.** Les signes qu'un modèle simple ne suffit plus, un **test honnête** (modèle simple contre boosting), le **dossier de passation**, la vie d'un modèle après sa mise en service (**dérive**, recalibrage), le risque de modèle et l'éthique.
- **3.4 ➕ AutoML et outils sans code.** Ce que ces outils automatisent, un **mini-AutoML** écrit en quelques lignes, et le **piège du classement** : le gagnant d'une compétition interne est souvent flatté.

## Les données du chapitre

> 📦 **Les données.** Les fichiers de la boutique des volumes précédents, **simulés**, propres : `commandes.csv`, `lignes_commande.csv`, `produits.csv`, `retours.csv`, `clients.csv` et `jours_exploitation.csv` (1 096 jours de 2023 à 2025). Aucun fichier nouveau : les tables de ce chapitre (la série mensuelle des commandes, et un « instantané » de chaque client à une date donnée) sont **calculées** par `build/outils_ch03.py`, et les figures par `build/fig_ch03.py`. Comme partout dans ce livre, on connaît la **vérité programmée** : la fabrique des données, écrite dans `build/donnees_a1.py`, fait dépendre les commandes de la saison, du jour de la semaine, d'une tendance de +6 % par an et des promotions, et donne à chaque client une « propension » à acheter qui lui est propre. On peut donc dire, à la fin d'une étude, ce qu'un modèle aurait pu atteindre au mieux.

Un mot sur ce que le chapitre ne fait pas : il n'exécute **aucun produit commercial** d'apprentissage automatique ou d'AutoML. Ceux de la section 3.4 sont décrits, jamais reproduits à l'écran ; ce qu'ils font est refait en quelques lignes avec scikit-learn, pour comprendre le principe.
