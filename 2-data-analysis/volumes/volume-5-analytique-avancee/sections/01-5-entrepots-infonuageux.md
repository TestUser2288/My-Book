## 1.5 ➕ Pour aller plus loin : BigQuery, Snowflake, Redshift, Azure Synapse

> 🧭 Section optionnelle. Aucun des quatre services nommés ici n'est exécuté dans ce livre. Ce que nous montrons **en local**, avec des fichiers Parquet et DuckDB, ce sont les **mécanismes** sur lesquels ils reposent : le stockage en colonnes et le partitionnement.

```python hide
import os, re, sys, glob, shutil, tempfile
import numpy as np
import pandas as pd
sys.path.insert(0, "build")
import outils_ch01 as O
```

### 1.5.1 Ce que change un entrepôt infonuagique, et ce qui ne change pas

Un entrepôt infonuagique est un entrepôt **loué** : on n'installe rien, on ne gère pas les serveurs, on envoie des données et des requêtes SQL à un service, et l'on paie ce que l'on utilise. Quatre services sont très connus : **BigQuery**, **Snowflake**, **Redshift** et **Azure Synapse**. Ils diffèrent par bien des détails, mais ils partagent des idées.

- **Stockage et calcul séparés.** Les données vivent dans un stockage partagé, bon marché et durable ; la puissance de calcul se **démarre, s'arrête et se dimensionne** indépendamment. Plusieurs équipes peuvent interroger les mêmes données avec des calculs différents, sans se gêner.
- **Stockage en colonnes.** Les données sont rangées **colonne par colonne** et compressées. Une requête qui ne lit que trois colonnes sur trente ne lit que ces trois-là.
- **Élasticité.** On peut disposer de beaucoup de puissance pour une heure, puis plus du tout. Ce qui coûtait un serveur acheté coûte une durée d'utilisation.
- **Facturation à l'usage**, sous des formes qui varient : au volume de données **lues**, au **temps** de calcul, ou à une **capacité** réservée.

![Stockage et calcul séparés : plusieurs calculs, démarrés et arrêtés indépendamment, lisent le même stockage partagé (schéma générique, sans identité d'un produit).](figures/ch01-stockage-calcul.png)

```python hide
O.fig_stockage_calcul()
```
<!--sortie-->
```text
figure : ch01-stockage-calcul.png
```

Ce qui **ne change pas** est tout ce que ce chapitre a enseigné : l'**étoile**, le **grain**, les mesures additives, les dimensions conformes, les dimensions à évolution lente, les contrôles de rapprochement. Un entrepôt infonuagique mal modélisé donne, à plus grande échelle et plus cher, les mêmes quatre chiffres d'affaires. **La modélisation est indépendante de l'outil.**

> ⚠️ **Piège : croire que le service règle la méthode.** Un service puissant exécute vite une requête fausse. La puissance accélère la **réponse**, pas la **justesse**.

### 1.5.2 Le stockage en colonnes, démontré en local

Un fichier CSV range les données **ligne par ligne** : pour lire une colonne, il faut parcourir toutes les lignes en entier. **Parquet**, format de fichier ouvert très répandu (et lisible par DuckDB comme par les entrepôts infonuagiques), les range **colonne par colonne**, les compresse, et note dans un pied de fichier ce que contient chaque colonne.

Écrivons la table de faits de la boutique dans les deux formats, dans un dossier temporaire :

```python
TMP = tempfile.mkdtemp(dir=os.environ.get("TMPDIR"), prefix="ch01_")
con.executescript("CREATE TABLE dwh.vf AS SELECT v.*, d.annee FROM dwh.fait_ventes v "
                  "JOIN dwh.dim_date d USING (date_key) ORDER BY id_ligne")
con.executescript(f"COPY dwh.vf TO '{TMP}/ventes.csv' (HEADER)")
con.executescript(f"COPY dwh.vf TO '{TMP}/ventes.parquet' (FORMAT parquet, COMPRESSION zstd)")
ko = lambda f: os.path.getsize(f"{TMP}/{f}") / 1024
print(f"CSV : {ko('ventes.csv'):.0f} ko ; Parquet : {ko('ventes.parquet'):.0f} ko ; "
      f"rapport : {ko('ventes.csv') / ko('ventes.parquet'):.1f}")
```
<!--sortie-->
```text
CSV : 5959 ko ; Parquet : 818 ko ; rapport : 7.3
```

Le même contenu pèse **7,3 fois moins** en Parquet, parce que chaque colonne se compresse bien (les valeurs d'une colonne se ressemblent : un canal parmi sept, une quantité de un à cinq). Le pied du fichier dit de plus **combien d'octets occupe chaque colonne** :

```python
m = con.df(f"""SELECT path_in_schema AS colonne, SUM(total_compressed_size) AS octets
               FROM parquet_metadata('{TMP}/ventes.parquet') GROUP BY 1 ORDER BY 2 DESC""")
m["part_pct"] = (100 * m["octets"] / m["octets"].sum()).round(1)
print(m.head(5).to_string(index=False))
```
<!--sortie-->
```text
    colonne   octets  part_pct
 client_key 127203.0      15.5
   id_ligne 121672.0      14.8
 montant_ht 113165.0      13.8
montant_ttc 113067.0      13.8
 cout_achat  92996.0      11.3
```

Une requête qui additionne **seulement** `montant_ttc` ne lit donc que **13,8 %** du fichier, et ignore le reste. (Les colonnes d'identifiants, dont presque toutes les valeurs sont différentes, sont celles qui se compressent le moins.)

![À gauche, l'espace que chaque colonne occupe dans le fichier Parquet de la table de faits : lire montant_ttc seul, c'est lire la barre orange. À droite, un fichier par année : filtrer sur l'année évite d'ouvrir les autres.](figures/ch01-parquet.png)

```python hide
O.fig_parquet(m.set_index("colonne")["octets"])
```
<!--sortie-->
```text
figure : ch01-parquet.png
```

> 💡 **Intuition.** Un CSV est un **registre relié** : pour connaître la somme d'une colonne, il faut tourner toutes les pages. Un fichier en colonnes est un **classeur à onglets** : on ouvre l'onglet voulu. Plus la table est large (quarante colonnes dans une vraie table de faits), plus l'avantage grandit.

### 1.5.3 Partitionner, et ce que cela change au coût

Seconde idée : **découper** la table en plusieurs fichiers selon une colonne (la date, le plus souvent), de sorte qu'une requête qui filtre sur cette colonne **n'ouvre que les fichiers concernés**. C'est le **partitionnement**. DuckDB sait l'écrire en une instruction, et le relire en n'ouvrant que ce qu'il faut :

```python
con.executescript(f"COPY dwh.vf TO '{TMP}/ventes_part' (FORMAT parquet, COMPRESSION zstd, PARTITION_BY (annee))")
print(sorted(os.path.relpath(f, f"{TMP}/ventes_part") for f in glob.glob(f"{TMP}/ventes_part/*/*")))
lire = f"read_parquet('{TMP}/ventes_part/*/*.parquet', hive_partitioning = true)"
plan = con.df(f"EXPLAIN SELECT SUM(montant_ttc) FROM {lire} WHERE annee = 2025").iloc[0, 1]
print("fichiers ouverts :", re.search(r"Scanning Files: (\d+/\d+)", plan).group(1))
```
<!--sortie-->
```text
['annee=2023/data_0.parquet', 'annee=2024/data_0.parquet', 'annee=2025/data_0.parquet']
fichiers ouverts : 1/3
```

Sur les trois années, **un seul fichier** est ouvert pour la requête de 2025 : c'est l'**élagage des partitions** (*partition pruning*). Le résultat est le même qu'en lisant tout, avec deux tiers de données en moins à lire.

Dans les entrepôts infonuagiques, cette idée a une conséquence **financière**. Selon le service et l'offre, on est facturé en partie ou en totalité au **volume de données lues**. Les bonnes pratiques qui en découlent sont les mêmes partout :

- **ne sélectionner que les colonnes utiles** (`SELECT *` lit toutes les colonnes ; certains services le facturent comme tel) ;
- **filtrer sur la colonne de partition**, pour que les autres partitions ne soient pas lues ;
- **agréger dans des marts** les requêtes répétées par les tableaux de bord, plutôt que de relire chaque fois la table de faits ;
- **vérifier ce qu'une limite de lignes change vraiment** : dans certains services, ajouter `LIMIT 10` n'allège pas la lecture ; c'est à vérifier dans la documentation de votre version.

Les services offrent aussi un **regroupement** (*clustering*) à l'intérieur des partitions (par produit, par exemple), ou des **clés de tri et de distribution**, qui jouent le même rôle : faire en sorte que les lignes qu'une requête cherche soient **voisines**. Voici à quoi ressemble une telle déclaration, à titre **indicatif** (syntaxe d'un dialecte, qui varie d'un service à l'autre ; non exécutée, non vérifiée ici) :

```sql noexec
-- Syntaxe indicative, de type « entrepôt infonuagique » : table partitionnée par date, regroupée par produit
CREATE TABLE ventes (
  id_ligne INT64, date_commande DATE, produit_key INT64, montant_ttc NUMERIC
)
PARTITION BY date_commande
CLUSTER BY produit_key;
```

### 1.5.4 Les quatre services nommés : une comparaison prudente

Le tableau suivant situe les quatre services **par les idées qu'ils partagent et la façon dont ils les organisent**. Il repose sur l'état des connaissances de l'auteur à l'**automne 2026**, **sans exécution** ; les offres, les noms et les tarifs évoluent vite. **À vérifier dans la documentation de votre version avant toute décision.**

| | BigQuery | Snowflake | Redshift | Azure Synapse |
|---|---|---|---|---|
| **Calcul** | sans serveur : la puissance est allouée par le service | entrepôts de calcul **virtuels**, démarrés et arrêtés à la demande | **cluster** de nœuds (une variante sans serveur existe) | pools dédiés (capacité réservée) et pool sans serveur |
| **Facturation (grandes lignes)** | au volume lu, ou à une capacité réservée | au temps d'activité des calculs, selon leur taille | à la taille et à la durée du cluster, ou à l'usage en version sans serveur | à la capacité réservée, ou au volume lu pour le pool sans serveur |
| **Organisation physique** | partitions et regroupement (*clustering*) | découpage automatique, clés de regroupement facultatives | clés de **distribution** et de **tri** | **distribution** (par hachage, tourniquet ou répliquée) |
| **Langage** | SQL, avec des extensions propres | SQL, avec des extensions propres | SQL, très proche de PostgreSQL | SQL (famille T-SQL) |
| **Ce qu'il faut surveiller** | le volume lu par requête | la durée pendant laquelle les calculs restent allumés | le dimensionnement du cluster, le choix des clés | la capacité réservée, le choix de la distribution |

### 1.5.5 Choisir, et choisir à la bonne échelle

Choisir un service ne se fait pas sur une comparaison de fonctions. Les critères réels sont d'autres :

- **l'écosystème existant** : où sont déjà les données, les outils de tableau de bord, les compétences ?
- **le volume et la concurrence** : combien de données, combien de personnes interrogent en même temps ?
- **la gouvernance** : droits d'accès, localisation des données, chiffrement, traçabilité ;
- **la maîtrise du coût** : quelle facturation, quelles alertes, qui surveille ?
- **la réversibilité** : dans quel format sont les données, comment en sortir ?

Et surtout **la bonne échelle**. Notre table de faits de **83 905 lignes** tient dans un fichier de moins d'un mégaoctet (en Parquet) ; un fichier DuckDB, ou une base relationnelle ordinaire, suffit largement à la boutique. Un entrepôt infonuagique se justifie quand le **volume**, le **nombre d'utilisateurs** ou le besoin de **partage** dépassent ce qu'une machine unique sait faire, pas avant. Une organisation peut très bien avoir un entrepôt **bien modélisé** sur un petit outil, et **mal modélisé** sur le plus gros service du marché.

```python hide
assert TMP.startswith(os.environ.get("TMPDIR", "/tmp")) and os.path.isdir(TMP)
shutil.rmtree(TMP)
assert not os.path.exists(TMP)
```

> ✅ **À retenir.**
> - Un entrepôt infonuagique **sépare le stockage du calcul**, range les données **en colonnes** et se facture **à l'usage** (volume lu, temps ou capacité). La **modélisation**, elle, ne change pas.
> - Le **stockage en colonnes** (Parquet) compresse et ne lit que les colonnes demandées ; le **partitionnement** n'ouvre que les fichiers concernés. Cela se démontre en local.
> - On maîtrise le coût en **choisissant les colonnes**, en **filtrant sur la partition**, en **agrégeant dans des marts**.
> - On choisit un service sur l'écosystème, la gouvernance, le coût et la réversibilité ; **la bonne échelle** pour la boutique est un simple fichier.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.7 et exercice 1.12.
