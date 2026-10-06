# Chapitre 3 : Big data et calcul distribué

> « Quand une machine ne suffit plus, on ne cherche pas une machine plus grosse : on apprend à faire travailler plusieurs machines ensemble. Et c'est là que les vrais problèmes commencent. »

> 🧭 **Où se situe ce chapitre.** Les chapitres 1 et 2 ont changé de **modèle** (réseaux de neurones, transformers). Celui-ci change d'**échelle** : que devient une analyse quand les données ne tiennent plus en mémoire, ou quand le calcul prend des heures ? Il suppose le SQL du volume I (chapitre 5, surtout les fonctions fenêtres de la section 5.3) et pandas (volume I, section 4.4).

La boutique a bien grandi. À ses débuts, quatre cents commandes tenaient dans un petit tableau ; aujourd'hui, le site, les réseaux sociaux et le magasin produisent **des millions de transactions** par an. La gérante veut des réponses de toujours (« combien a-t-on vendu par canal et par mois ? », « quels produits se vendent ensemble ? », « quels clients achètent le plus ? »), mais l'ordinateur portable commence à ramer, puis à planter.

Que faire ? Deux réflexes opposés sont à éviter.

- **Le réflexe « big data »** : « cent millions de lignes, il faut un *cluster* ! » C'est souvent faux. Les machines actuelles traitent très bien des dizaines de gigaoctets, et un cluster coûte cher en argent, en complexité et en pannes.
- **Le réflexe « ça ira bien »** : continuer avec les outils habituels en espérant que ça passe. Tant que les données tiennent en mémoire, c'est raisonnable ; au-delà, le programme s'arrête sur une erreur de mémoire sans prévenir.

Ce chapitre apprend à **choisir en connaissance de cause**. Il explique pourquoi et comment on répartit un calcul sur plusieurs machines, ce qu'on y gagne, ce qu'on y perd, puis il présente l'outil le plus répandu, **Apache Spark**.

## Le chemin de ce chapitre

- **3.1 Concepts du calcul distribué** : les quatre limites d'une machine, la **partition** des données, le modèle **MapReduce** (calculé à la main, puis programmé), la **loi d'Amdahl** qui plafonne les gains, les **pannes** et le théorème CAP, les formats **en colonnes** comme Parquet, et surtout **quand ne pas distribuer**.
- **3.2 Spark et PySpark** : l'architecture (pilote, exécuteurs, tâches), l'**évaluation paresseuse** et le **plan d'exécution**, les transformations qui déplacent des données (*shuffle*), les jointures, les fonctions fenêtres, les pièges (asymétrie des clés, petits fichiers) et une comparaison honnête avec DuckDB et pandas.
- ➕ **3.3 Hadoop, Kafka et traitement en flux** : l'écosystème qui a précédé Spark, les journaux de messages (Kafka) et le calcul sur des données qui n'arrêtent jamais d'arriver (fenêtres de temps, retards, garanties de livraison).

## Les données du chapitre

> 📦 **Un historique de transactions simulé.** Nous utilisons **deux millions de transactions** de la boutique, simulées avec une graine fixe par la fonction `gros_volume` du dossier `build/`. Chaque ligne a sept colonnes :
>
> | Colonne | Contenu |
> |---|---|
> | `id_transaction` | numéro unique (entier) |
> | `date` | jour de la transaction, en 2025 |
> | `id_client` | un des 200 000 clients |
> | `id_produit` | un des 500 produits |
> | `magasin` | une des dix villes (« Ville A » à « Ville J ») |
> | `canal` | `Boutique`, `Site` ou `Réseaux` |
> | `montant` | montant en euros |
>
> Ces fichiers **ne sont pas versionnés** : ils pèsent plusieurs dizaines de mégaoctets et se régénèrent en quelques secondes. Chaque exemple de ce chapitre les crée dans un dossier temporaire, qu'il efface ensuite.

> 💡 **Pourquoi deux millions et pas deux milliards ?** Parce que le livre doit s'exécuter sur un ordinateur ordinaire. Les mécanismes (partitions, mélange, plan d'exécution) sont **les mêmes** à toute échelle, et nous en mesurons les conséquences sur des tailles où elles se voient déjà. Une conséquence honnête : à deux millions de lignes, **un seul ordinateur suffit largement**, et le chapitre le montrera.

```python hide
import os, re, sys, shutil, tempfile, time, warnings, collections
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, "build")
import style
from style import BLEU, ORANGE, AQUA, VIOLET, ROUGE, ENCRE2, MUET
style.setup()
import donnees4, fig_ch03

# dossier temporaire (hors du dépôt) : supprimé à la fin du chapitre (fichier 03-4)
TMP = tempfile.mkdtemp(prefix="v4c3_")                      # respecte TMPDIR (posé par le Makefile)
DOSSIER = donnees4.gros_volume(2_000_000, 4, dossier=os.path.join(TMP, "gros_volume"))
print("fichiers :", sorted(os.listdir(DOSSIER)))
```
<!--sortie-->
```text
fichiers : ['part-00.parquet', 'part-01.parquet', 'part-02.parquet', 'part-03.parquet']
```
