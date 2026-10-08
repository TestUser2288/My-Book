# Introduction : des analyses ponctuelles aux systèmes reproductibles

> « Un chiffre que l'on ne sait pas refaire est un chiffre que l'on ne sait pas défendre. »

## Le lundi où vous n'êtes pas là

Depuis des mois, vous préparez chaque début de mois le même rapport pour la gérante : chiffre d'affaires, marge, retards de livraison, ruptures de stock. Vous exportez des fichiers, vous les nettoyez, vous recopiez des formules, vous collez des graphiques dans un document. Cela prend une demi-journée, et cela marche, **tant que c'est vous**.

Un lundi, vous êtes en congé. La responsable logistique lance le rapport à votre place, avec le fichier du mois **précédent** (elle s'est trompée de dossier). Le chiffre d'affaires est faux de 8 %. Personne ne le remarque : le document est bien mis en page, les graphiques sont jolis, et les chiffres ont l'air plausibles. Jeudi, la gérante décide un réapprovisionnement sur la foi de ce rapport.

Cette histoire n'est pas celle d'une erreur de calcul. C'est celle d'une **absence de système** : aucune étape n'a vérifié que le fichier était le bon, que le mois était complet, que le total ressemblait à celui du mois précédent, ni prévenu quelqu'un que quelque chose clochait. Les volumes précédents vous ont appris à **trouver** un résultat juste et à le **montrer**. Celui-ci vous apprend à le **produire de façon fiable, chaque fois, sans vous**.

> 🧭 **Le critère.** Une analyse est professionnelle quand une autre personne, ou vous-même dans six mois, peut la **refaire**, la **vérifier** et la **relancer sans risque**.

## Sept étapes à la main, sept occasions de se tromper

Reprenons le rapport mensuel tel qu'on le fait à la main.

```python hide
import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
sys.path.insert(0, "build")
from style import setup, BLEU, ORANGE, MUET, ENCRE, ENCRE2, ROUGE
setup()
```

| # | Étape manuelle | Comment elle casse (sans que personne ne le voie) |
|---|---|---|
| 1 | Télécharger les exports | mauvais fichier, mois incomplet, export lancé avant la fin de la journée |
| 2 | Les ouvrir dans le tableur | séparateur, encodage, dates lues à l'envers |
| 3 | Nettoyer à la main | une correction oubliée, une ligne supprimée par erreur |
| 4 | Recopier les formules du mois précédent | une plage décalée d'une ligne |
| 5 | Calculer les indicateurs | une définition qui change (hors taxe ou toutes taxes ?) |
| 6 | Construire les graphiques | un axe qui ne s'est pas mis à jour |
| 7 | Envoyer le rapport | la mauvaise version, la mauvaise liste de destinataires |

Il suffit d'une hypothèse simple pour mesurer le risque : supposons que chaque étape manuelle ait **2 %** de chances de contenir une erreur.

```python
p_etape, n_etapes = 0.02, 7
p_rapport = 1 - (1 - p_etape) ** n_etapes
p_annee = 1 - (1 - p_rapport) ** 12
print(f"un rapport : {p_rapport:.1%} | au moins une erreur dans l'année : {p_annee:.1%}")
```
<!--sortie-->
```text
un rapport : 13.2% | au moins une erreur dans l'année : 81.7%
```

Un rapport sur huit environ contiendrait une erreur, et **plus de quatre années sur cinq** en compteraient au moins une. Le chiffre de 2 % est une hypothèse, pas une mesure ; ce qu'il montre est un ordre de grandeur : **les erreurs d'un processus manuel s'accumulent**, et plus le processus est long, moins il est fiable. L'automatisation ne rend pas les étapes plus intelligentes ; elle les rend **identiques à chaque fois**, ce qui permet enfin de les **contrôler**.

```python hide
fig, ax = plt.subplots(figsize=(10.4, 3.0))
ax.set_xlim(0, 100); ax.set_ylim(0, 30); ax.axis("off")
noms = ["Exports", "Tableur", "Nettoyage", "Formules", "Indicateurs", "Graphiques", "Envoi"]
for i, nom in enumerate(noms):
    x0 = 0.5 + i * 14.2
    ax.add_patch(FancyBboxPatch((x0, 12), 11.5, 10, boxstyle="round,pad=0.3,rounding_size=1.0", fc="white", ec=BLEU, lw=1.6))
    ax.text(x0 + 5.75, 17, nom, ha="center", va="center", fontsize=9.5, color=ENCRE)
    ax.text(x0 + 5.75, 9.3, "?", ha="center", va="center", fontsize=15, color=ORANGE, weight="bold")
    if i < len(noms) - 1:
        ax.add_patch(FancyArrowPatch((x0 + 12.0, 17), (x0 + 14.0, 17), arrowstyle="-|>", mutation_scale=10, color=ENCRE2))
ax.text(0.5, 3.3, "chaque « ? » est un endroit où personne ne contrôle rien : 2 % d'erreur par étape donnent 13,2 % pour le rapport (hypothèse)", fontsize=9, color=MUET)
fig.savefig("figures/ch00-chaine-manuelle.png", dpi=200, bbox_inches="tight"); plt.close(fig)
print("figure écrite")
```
<!--sortie-->
```text
figure écrite
```

![Le rapport mensuel fait à la main : sept étapes, et à chacune un point d'interrogation, c'est-à-dire un endroit où une erreur peut passer sans être vue.](figures/ch00-chaine-manuelle.png)

## Ce qui change quand l'analyse devient un système

Passer d'une analyse ponctuelle à un système, ce n'est pas écrire plus de code : c'est **ajouter des propriétés** que l'analyse ponctuelle n'a pas besoin d'avoir.

| Propriété | Analyse ponctuelle | Système reproductible |
|---|---|---|
| **Reproductible** | « ça marchait sur mon ordinateur » | mêmes entrées, mêmes sorties, sur n'importe quelle machine |
| **Idempotent** | relancer duplique ou corrompt | relancer **n'ajoute rien** : le résultat est le même |
| **Contrôlé** | on regarde si le chiffre « a l'air bon » | des vérifications écrites (comptage, rapprochement, plausibilité) échouent bruyamment |
| **Journalisé** | « je crois que ça a tourné » | chaque exécution laisse une trace : quand, quoi, combien, pourquoi |
| **Planifié** | on s'en souvient (ou pas) | une échéance, un rattrapage si elle est manquée |
| **Documenté** | dans la tête de l'auteur | définitions, schémas, responsable, procédure en cas de panne |
| **Défini une fois** | chaque rapport recalcule à sa façon | un indicateur est calculé **à un seul endroit** et réutilisé |

La dernière ligne est la plus importante, et c'est elle qui justifie le **premier chapitre** de ce volume : tant que chaque tableau de bord, chaque tableur et chaque rapport recalcule le chiffre d'affaires à sa manière, on aura trois chiffres d'affaires. La solution est de **modéliser les données une fois** (l'entrepôt), de les **charger de façon fiable** (l'ETL), puis d'en tirer les rapports.

> 💡 **Intuition.** Un système de reporting est une chaîne de production. On n'inspecte pas chaque pièce à la main : on installe des **contrôles** aux points où les défauts apparaissent, et l'on s'arrête quand un contrôle échoue.

## Trois idées qui tiennent le volume

1. **Une seule vérité, plusieurs usages.** Les données sont modélisées et nettoyées une fois ; les rapports, les tableaux de bord et les modèles lisent la même source.
2. **Échouer bruyamment.** Un pipeline qui se tait quand il se trompe est pire qu'un pipeline qui s'arrête : il distribue des erreurs avec l'autorité d'une machine.
3. **Prédire n'est pas décider, et générer n'est pas vérifier.** Les modèles prédictifs et les assistants fondés sur des modèles de langage sont des outils puissants **à encadrer** : par une référence simple à battre, par une validation hors échantillon, par des vérifications automatiques de ce qu'ils produisent.

## Carte des cinq chapitres

Les trois premiers chapitres forment le tronc ; le chapitre 4 applique la méthode à un domaine précis, celui du **risque** ; le chapitre 5, complémentaire, ouvre sur l'usage des modèles de langage.

| Chapitre | Question de fond | Ce que vous saurez faire |
|---|---|---|
| **1. Entrepôts de données et modélisation** | « Comment obtenir le même chiffre partout ? » | concevoir un schéma en étoile, déclarer un grain, séparer faits et dimensions ; ➕ dimensions à évolution lente, data marts, entrepôts infonuagiques |
| **2. ETL et automatisation** | « Comment faire tourner tout cela sans moi ? » | charger de façon incrémentale et idempotente, planifier, journaliser, gérer les erreurs ; ➕ outils d'orchestration, API, e-mail |
| **3. Analytique prédictive** | « Que va-t-il se passer, et que changer ? » | construire et évaluer un modèle simple, savoir quand passer la main ; ➕ AutoML |
| **4. Risque et assurance** | « Le portefeuille se dégrade-t-il, et à quelle vitesse ? » | sinistres, portefeuille, alertes, reporting de gestion et réglementaire |
| **➕ 5. LLM pour l'analyse** | « Peut-on déléguer les requêtes et les commentaires ? » | encadrer et vérifier un assistant : text-to-SQL, données synthétiques, rapports |
| **Projet du volume (cahier)** | « Le rapport du lundi, sans moi » | un pipeline de reporting automatisé qui alimente un tableau de bord |

> ✅ **À retenir.** Le travail d'un analyste ne s'arrête pas au résultat : il s'arrête quand le résultat peut être **reproduit, contrôlé et relancé** par quelqu'un d'autre. Automatiser, ce n'est pas aller plus vite : c'est devenir **fiable**.
