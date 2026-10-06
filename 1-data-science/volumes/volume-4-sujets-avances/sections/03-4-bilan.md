## Bilan du chapitre 3

Vous savez maintenant :

- **décider s'il faut distribuer** : les quatre limites d'une machine (mémoire, disque, temps, panne), ce qu'une machine moderne sait faire seule, et pourquoi **DuckDB** ou pandas suffisent bien plus souvent qu'on ne le croit ;
- **découper un calcul** : partitions par hachage ou par intervalles, le modèle **MapReduce** (*map*, mélange, *reduce*), et la raison pour laquelle il marche (une combinaison **associative**) ;
- **borner un gain** : la **loi d'Amdahl** $S(n)=1/[(1-p)+p/n]$ et son plafond $1/(1-p)$, avec le coût du mélange qui aggrave le tableau ;
- **raisonner sur les pannes** (réplication, lignage) et sur le **théorème CAP** (cohérence ou disponibilité pendant une coupure) ;
- **choisir un format** : Parquet (en colonnes, compressé, typé) contre CSV (en lignes) ;
- **écrire du Spark** : l'architecture pilote–exécuteurs, l'**évaluation paresseuse**, la lecture d'un **plan** et de ses `Exchange`, `repartition`, `coalesce`, `cache`, la **jointure par diffusion**, les fonctions fenêtres, le coût des UDF ;
- **repérer et corriger** l'**asymétrie des clés** (par le salage) et le **problème des petits fichiers** ;
- (en option) **situer Hadoop et Kafka**, distinguer **lot et flux**, choisir une **fenêtre** et un **filigrane**, et écrire des traitements **idempotents** sous la garantie « au moins une fois ».

Le fil conducteur du chapitre tient en une phrase : **distribuer est un moyen, pas un but, et son coût se mesure en données qui voyagent**. Une machine qui suffit est préférable à dix qui coordonnent ; quand elle ne suffit plus, la performance se joue dans le **mélange** : on le lit dans le plan, on le réduit par le filtrage et l'agrégation précoces, on évite qu'une clé l'écrase.

Le chapitre 4 change de sujet : ce qui compte maintenant n'est plus de calculer un résultat, mais de **le rendre fiable dans la durée**. Un modèle est mis en production, il vieillit, ses données changent : c'est l'objet du **MLOps** (suivi des expériences, déploiement, surveillance).

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.1 à 3.6 (MapReduce sur les avis, loi d'Amdahl sur votre machine, plan d'exécution et jointure, asymétrie et salage, journal de messages idempotent, fenêtres et filigrane) et exercices 3.1 à 3.18.

```python hide
spark.stop()
shutil.rmtree(TMP, ignore_errors=True)
print("dossier temporaire supprimé :", not os.path.exists(TMP))
```
<!--sortie-->
```text
dossier temporaire supprimé : True
```
