# Chapitre 4 : MLOps

> « Un modèle qui n'existe que dans un notebook n'a encore aidé personne. »

Les trois volumes précédents ont appris à **construire** de bons modèles : les estimer, les valider, les expliquer. Ce chapitre répond à la question suivante, que l'on découvre d'ordinaire à ses dépens : **que se passe-t-il le lendemain du jour où le modèle est bon ?** Il faut le rendre utilisable par d'autres (une application, un service de relance, une équipe commerciale), le garder reproductible, le remplacer sans casser ce qui l'utilise, et s'apercevoir quand il cesse de dire vrai. L'ensemble de ces pratiques porte un nom, **MLOps** (*machine learning operations*), par analogie avec le DevOps du logiciel.

```python hide
import atexit, json, logging, math, os, shutil, sys, tempfile, time, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd, joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import style
from style import BLEU, ORANGE, AQUA, VIOLET, ROUGE, ENCRE, ENCRE2, MUET
from sklearn.metrics import roc_auc_score
from outils_ch04 import *
style.setup()

WORK = tempfile.mkdtemp(prefix="ch04_", dir=os.environ.get("TMPDIR"))        # tout temporaire vit ici et disparaît à la fin
atexit.register(shutil.rmtree, WORK, ignore_errors=True)


def NUM(cle, valeur):
    """Imprime un nombre cité dans la prose : le texte le relit dans cette sortie."""
    print("NUM", cle, valeur)


def boite(ax, x, y, w, h, texte, couleur=BLEU, taille=9.5, plein=False):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=couleur if plein else "#fcfcfb", ec=couleur, lw=1.5, zorder=2))
    ax.text(x, y, texte, ha="center", va="center", fontsize=taille, color="white" if plein else ENCRE, zorder=3, linespacing=1.25)


def fleche(ax, p, q, couleur=ENCRE2, rad=0.0, ls="-", lw=1.4):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=13, color=couleur, lw=lw, ls=ls,
                                 connectionstyle=f"arc3,rad={rad}", zorder=1, shrinkA=0, shrinkB=0))


d = donnees()
v1, v2 = modele_v1(d), modele_v2(d)
Xtr, Xte, Xpool, ytr, yte = d["Xtr"], d["Xte"], d["Xpool"], d["ytr"], d["yte"].to_numpy()
COLONNES = list(d["X"].columns)
auc1, auc2 = roc_auc_score(yte, v1.predict_proba(Xte)[:, 1]), roc_auc_score(yte, v2.predict_proba(Xte)[:, 1])
NUM("n_clients", len(d["X"])); NUM("n_train", len(Xtr)); NUM("n_test", len(Xte)); NUM("n_pool", len(Xpool))
NUM("taux_churn", round(100 * d["y"].mean(), 1)); NUM("n_var", len(COLONNES)); NUM("auc_v1", round(auc1, 3)); NUM("auc_v2", round(auc2, 3))

fig, ax = plt.subplots(figsize=(10.4, 4.5)); ax.set_xlim(0, 10.4); ax.set_ylim(0, 4.5); ax.axis("off")
etapes = [(1.2, "Données\n(clients,\ncommandes)", MUET), (3.3, "Pipeline\nd'entraînement", BLEU), (5.4, "Modèle\n(artefact\nversionné)", BLEU), (7.5, "Service\n(API ou lot)", AQUA), (9.4, "Décisions\n(relances)", ORANGE)]
for x, t, c in etapes:
    boite(ax, x, 3.35, 1.55, 1.15, t, c)
for (x1, _, _), (x2, _, _) in zip(etapes[:-1], etapes[1:]):
    fleche(ax, (x1 + 0.8, 3.35), (x2 - 0.8, 3.35))
boite(ax, 5.2, 1.35, 8.8, 0.8, "Supervision : système · données · scores · performance · coûts", VIOLET, taille=9.5, plein=True)
for x in (1.2, 7.5, 9.4):
    fleche(ax, (x, 2.75), (x, 1.76), VIOLET, ls="--")
fleche(ax, (2.9, 1.76), (3.3, 2.75), ROUGE, ls=":")
ax.text(3.6, 2.2, "étiquettes (90 jours plus tard)\n→ ré-entraînement", ha="left", va="center", fontsize=8.5, color=ROUGE)
ax.text(5.2, 4.25, "Le modèle n'est qu'une boîte parmi cinq", ha="center", fontsize=10.5, color=ENCRE)
style.save(fig, "ch04-chaine-mlops.png")
```
<!--sortie-->
```text
NUM n_clients 12000
NUM n_train 7200
NUM n_test 2400
NUM n_pool 2400
NUM taux_churn 14.0
NUM n_var 19
NUM auc_v1 0.867
NUM auc_v2 0.893
figure : ch04-chaine-mlops.png
```

## Le chemin de ce chapitre

- **4.1 Pipelines et automatisation** : du notebook au projet reproductible, le pipeline qui s'ajuste une fois, les tests de données et de modèles, le piège du décalage entre entraînement et service.
- **4.2 Déploiement et mise à disposition** : les quatre façons de servir un modèle, la sérialisation (et ses dangers), une API de scoring, et comment remplacer un modèle sans casser le service.
- **4.3 Supervision** : quoi surveiller, journaliser, composer avec des étiquettes qui arrivent en retard, régler des alertes qui ne fatiguent pas.
- ➕ **4.4 Orchestration** : les graphes de tâches, les reprises, l'idempotence, avec un mini-orchestrateur exécutable.
- ➕ **4.5 Suivi d'expériences** : MLflow, le registre de modèles, versionner les données.
- ➕ **4.6 CI/CD, Docker, Kubernetes, API REST** : automatiser la livraison, empaqueter, exposer proprement.
- ➕ **4.7 Surveillance des modèles et détection de dérive** : PSI, test de Kolmogorov-Smirnov, et un mois de production simulé.

## Le fil rouge : le modèle de résiliation, du notebook au service

Nous reprenons le **modèle de résiliation** du volume III (section 2.4) : prédire, pour chacun des 12 000 clients de la boutique, s'il aura cessé de commander dans les 90 jours (`churn_90j`, 14,0 % de résiliations). Les colonnes qui sont des cibles ou des fuites (`depense_6m`, `segment_vrai`, et surtout `commandes_apres_cible`, la fuite d'information du volume III, section 1.1) sont exclues d'emblée : il reste 19 variables d'entrée. Les données sont **simulées** (graines fixes) ; les modèles sont ceux que vous connaissez :

- la **version 1**, une régression logistique avec imputation, mise à l'échelle et codage disjonctif, d'AUC 0,867 sur le jeu de test ;
- la **version 2**, un gradient boosting par histogrammes qui gère nativement les manquants et les catégories, d'AUC 0,893.

Pour les besoins du chapitre, les 12 000 clients sont répartis en trois jeux, sans recouvrement : **7 200 pour l'entraînement**, **2 400 pour le test** (qui sert à juger une fois), et **2 400 de « réservoir de production »**, que nous utiliserons comme source de clients « nouveaux » dans les sections de déploiement et de supervision.

> 💡 **Intuition.** Un modèle est une **fonction** ; un système de ML est une **chaîne de production**. La fonction se juge sur un jeu de test. La chaîne se juge sur sa **fiabilité** (elle tourne chaque jour), sa **reproductibilité** (on peut refaire le même modèle), sa **traçabilité** (on sait quelle version a produit quelle décision) et sa **vigilance** (elle s'aperçoit quand le monde change). La figure suivante montre les cinq maillons ; le chapitre les parcourt dans l'ordre, puis ajoute les outils qui les automatisent.

![Les maillons d'un système de ML : données, pipeline d'entraînement, modèle versionné, service, décisions. La supervision observe l'ensemble ; les étiquettes qui arrivent plus tard (ici 90 jours après) permettent de mesurer la performance réelle et de ré-entraîner.](figures/ch04-chaine-mlops.png)

## Ce qui est exécuté, et ce qui ne l'est pas

Ce livre n'affiche que les exemples qui enseignent quelque chose. Tout ce qui tourne ici tourne **hors ligne et dans le processus Python** : l'API est interrogée par un client de test (aucun port réseau n'est ouvert), le suivi d'expériences utilise une base SQLite temporaire, l'orchestrateur est un petit programme Python. En revanche, **Airflow, Prefect, dbt, Docker, Kubernetes, les workflows de CI/CD, DVC et Flask** ne font pas partie des outils que ce livre exécute (ils ne sont pas installés sur la machine qui l'a produit, ou ne figurent pas dans ses dépendances) : leurs exemples sont donnés **non exécutés**, signalés comme tels, avec chaque fois un équivalent exécutable minimal quand il en existe un. Les noms d'outils commerciaux sont des exemples, pas des recommandations ; leurs interfaces changent vite (**à vérifier dans leur documentation** avant de s'y fier).
