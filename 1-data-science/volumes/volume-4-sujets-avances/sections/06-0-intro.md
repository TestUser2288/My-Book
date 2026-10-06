# Chapitre 6 : ➕ Plateformes cloud

> « Le cloud, ce n'est pas l'ordinateur de quelqu'un d'autre. C'est un contrat : vous achetez de la souplesse, et vous payez en dépendance, en vigilance et en factures. »

> 🧭 **Chapitre complémentaire.** Ce chapitre est entièrement facultatif. Les chapitres 1 à 5 se lisent et se comprennent sans lui. Il s'adresse à celles et ceux qui devront **choisir, dimensionner ou payer** une infrastructure : il répond à la question « où fait-on tourner tout cela ? ».

Le volume s'est jusqu'ici occupé de **ce que l'on construit** : des réseaux de neurones, des modèles de langage, des traitements distribués, des services de prédiction, des pipelines de données. Reste à savoir **sur quelle machine, chez qui, pour quel prix et avec quels risques** tout cela s'exécute. Pour la plupart des équipes aujourd'hui, la réponse est : dans le **cloud**, c'est-à-dire sur des ressources informatiques louées à un fournisseur, à la demande, par internet.

## Ce que ce chapitre fait, et ne fait pas

> ⚠️ **Honnêteté d'abord.** L'auteur n'a pu utiliser **aucun compte** chez aucun fournisseur de cloud pour écrire ce chapitre. Il n'y a donc **aucune capture d'écran, aucune manipulation de console, aucun tarif réel** dans ces pages. Les prix, les latences et les niveaux de disponibilité utilisés sont **inventés, à titre d'illustration** : ils servent à comprendre des **mécanismes** (pourquoi une réservation peut coûter moins cher, pourquoi sortir des données coûte cher, pourquoi la redondance ne suffit pas) et pas à budgéter un projet. Les tarifs et les noms de services changent souvent : tout ce qui est donné ici comme exemple est **à vérifier** auprès du fournisseur avant toute décision.

Ce que le chapitre apporte, en revanche, c'est la **méthode** : savoir poser le calcul, voir quelles hypothèses pèsent le plus, repérer les pièges classiques. Tous les chiffres de ce chapitre sortent de **petits modèles écrits en Python** (le code est caché dans le livre, mais il est exécuté à chaque contrôle ; une partie est reprise, étape par étape, dans le cahier). Vous pourrez les refaire avec **vos** prix.

## Le chemin de ce chapitre

- **6.1 Ce que change le cloud** : du capital à la consommation, l'élasticité, les niveaux de service (IaaS, PaaS, FaaS, SaaS), les régions et les zones de disponibilité (avec l'arithmétique de la disponibilité), le partage des responsabilités, le verrouillage et la « gravité » des données.
- **6.2 Les grandes familles de services** : calcul (machines, conteneurs, serverless), stockage, bases de données, analytique, plateformes d'apprentissage automatique, identité et réseau ; une table d'équivalences entre trois grands fournisseurs, et la correspondance avec les outils de ce volume.
- **6.3 Coûts, sécurité et choix** : modes d'achat et seuils de rentabilité, bonnes pratiques de maîtrise des coûts (FinOps), le piège des frais de sortie, sécurité (moindre privilège, chiffrement, secrets), conformité, choisir entre cloud, sur site, hybride et multicloud, et préparer sa sortie.
- **Bilan du chapitre.**

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : huit applications (calculateurs de coût, disponibilité, autoscaling, stockage, modes d'achat, audit d'une politique d'accès, grille de décision) et douze exercices corrigés.

## Comment lire ce chapitre

Les pages qui suivent contiennent peu de code visible : un modèle chiffré est présenté par ses **hypothèses** et par son **résultat**, sous forme de tableau ou de figure. La question à se poser, à chaque tableau, est toujours la même : *quelle hypothèse, si je la change, renverse la conclusion ?* C'est la compétence la plus utile face à un devis de cloud.

Les montants sont en euros, pour la boutique fictive du fil rouge, et sont **tous inventés**. Les paramètres du modèle sont rassemblés ci-dessous (ils sont définis une fois, dans un bloc caché, et réutilisés dans tout le chapitre).

```python hide
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "build")
import style
from style import BLEU, ORANGE, AQUA, VIOLET, ROUGE, MUET, ENCRE2

style.setup()
pd.set_option("display.width", 200)

# --- Prix et paramètres INVENTÉS, à titre d'illustration (jamais de vrais tarifs) ---------------------
P = dict(
    serveur_achat=6000.0, annees=4, expl_an=1200.0,      # achat d'un serveur, durée d'amortissement, exploitation annuelle (énergie, maintenance)
    vm_od=0.40, vm_res=0.25, vm_spot=0.12,               # € par heure : à la demande, réservée 1 an (facturée tout le mois), spot
    unite_site=0.030, unite_od=0.050,                    # € par « unité de calcul » et par heure : sur site, cloud à la demande
    heures_mois=730,
)
print("paramètres définis")
```
<!--sortie-->
```text
paramètres définis
```
