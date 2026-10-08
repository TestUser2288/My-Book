# Chapitre 1 : Entrepôts de données et modélisation — exercices et applications

> 🧭 Ce cahier prolonge le chapitre 1 : on y **définit** un chiffre avant de le calculer, on **construit** les dimensions que le livre a laissées de côté, on **contrôle** un chargement, on **teste** un grain, on **historise** une dimension et l'on **écrit** un petit data mart et un fichier en colonnes. Le cahier est autonome : il reconstruit l'entrepôt de la boutique (schéma `dwh`, avec le script de référence `build/outils_ch01.py`) à partir de la base d'exploitation (schéma `src`). Les données sont **simulées** ; les frais de port sont calculés par une règle simple (voir le chapitre).

```python
import os, re, sys, glob, shutil, tempfile
import numpy as np
import pandas as pd
sys.path.insert(0, "build")
import outils_ch01 as O

D = os.environ["DONNEES"]
con = O.ouvrir(D)                                 # schéma src : la base d'exploitation de la boutique
O.construire_etoile(con)                          # schéma dwh : l'étoile de référence du livre
con.executescript("CREATE MACRO cle_date(d) AS CAST(strftime(CAST(d AS DATE), '%Y%m%d') AS INTEGER)")
con.executescript(f"CREATE TABLE src.hist_clients AS SELECT * FROM read_csv_auto('{D}/ch01-historique-clients.csv')")
con.executescript("CREATE SCHEMA tp")             # votre espace de travail : on n'écrit jamais dans dwh à la main
print(con.df("SELECT COUNT(*) AS lignes FROM dwh.fait_ventes")["lignes"][0], "lignes de ventes dans l'étoile")
```
<!--sortie-->
```text
83905 lignes de ventes dans l'étoile
```

## Applications

### Application 1.1 — Une définition, quatre chiffres (introduction et section 1.1)

**Objectif.** Refaire, pour **2024**, le travail de l'ouverture du chapitre : trouver pourquoi quatre personnes donnent quatre chiffres d'affaires, et écrire **la** définition qui les réconcilie.

**Étape 1 — le chiffre brut.** Le chiffre d'affaires 2024 des lignes de commande, toutes taxes comprises puis hors taxe (TVA fictive de 20 %) :

```sql
SELECT ROUND(SUM(l.montant)) AS ttc, ROUND(SUM(l.montant) / 1.2) AS ht
FROM src.lignes_commande l JOIN src.commandes c USING (id_commande)
WHERE year(c.date_commande) = 2024;
```
<!--sortie-->
```text
      ttc       ht
1189461.0 991218.0
```

**Étape 2 — ce qui s'y ajoute ou s'en retranche.** Les remboursements (comptés à la date du retour) et les frais de port, comptés une fois par commande, puis — **à tort** — une fois par ligne :

```sql
SELECT (SELECT ROUND(SUM(montant_rembourse) / 1.2) FROM src.retours WHERE year(date_retour) = 2024) AS retours_ht,
       (SELECT ROUND(SUM(frais_port)) FROM src.commandes WHERE year(date_commande) = 2024) AS port_vrai,
       (SELECT ROUND(SUM(c.frais_port)) FROM src.commandes c JOIN src.lignes_commande l USING (id_commande)
        WHERE year(c.date_commande) = 2024) AS port_repete;
```
<!--sortie-->
```text
 retours_ht  port_vrai  port_repete
    59153.0    15427.0      25218.0
```

**Étape 3 — la fiche de définition.** Une définition d'indicateur tient dans une petite table. On l'écrit **avant** de modéliser : c'est elle qui dit quelle colonne de l'entrepôt porte le chiffre.

```python
fiche = pd.DataFrame([
    ("chiffre d'affaires", "somme des montants des lignes de commande / 1,2", "dwh.fait_ventes.montant_ht",
     "remises accordées sur la ligne", "frais de port, retours, TVA", "direction financière"),
    ("retours", "somme des montants remboursés / 1,2, à la date du retour", "dwh.fait_retours", "—", "—", "service client"),
], columns=["indicateur", "formule", "colonne", "inclus", "exclus", "propriétaire"])
print(fiche.set_index("indicateur").T.to_string())
```
<!--sortie-->
```text
indicateur                                 chiffre d'affaires                                                   retours
formule       somme des montants des lignes de commande / 1,2  somme des montants remboursés / 1,2, à la date du retour
colonne                            dwh.fait_ventes.montant_ht                                          dwh.fait_retours
inclus                         remises accordées sur la ligne                                                         —
exclus                            frais de port, retours, TVA                                                         —
propriétaire                             direction financière                                            service client
```

**À vous.** Ajoutez deux lignes à la fiche : le **chiffre d'affaires net des retours** (que faut-il décider sur la période de rattachement des retours ?) et le **panier moyen** (par commande ou par ligne ?). Donnez pour chacun la colonne de l'entrepôt qui le porte et son propriétaire.

> 📒 Ce travail prépare l'**exercice 1.1** (OLTP ou OLAP) et le **projet du volume**.

### Application 1.2 — Les dimensions que le livre a laissées (section 1.2.2)

**Objectif.** Écrire vous-même la dimension du **canal** (qui regroupe canal de vente et mode de livraison), celle des **promotions**, puis les comparer à celles du livre.

**Étape 1 — la dimension des canaux.** Une ligne par combinaison **existante** de canal et de mode de livraison, avec une clé de substitution.

```sql
CREATE TABLE tp.dim_canal AS
SELECT row_number() OVER (ORDER BY canal, mode_livraison) AS canal_key, canal, mode_livraison
FROM (SELECT DISTINCT canal, mode_livraison FROM src.commandes);
```

**Étape 2 — la dimension des promotions.** Un code vide (`NULL`) dans la commande veut dire « pas de promotion » : on lui donne une **vraie ligne**, plutôt que de laisser des valeurs vides se perdre dans les jointures.

```sql
CREATE TABLE tp.dim_promotion AS
SELECT row_number() OVER (ORDER BY code_promo) AS promo_key, code_promo
FROM (SELECT DISTINCT COALESCE(code_promo, 'Aucune') AS code_promo FROM src.commandes);
```

**Étape 3 — la comparaison.** Même nombre de lignes que les tables du livre ? Mêmes combinaisons ?

```sql
SELECT (SELECT COUNT(*) FROM tp.dim_canal) AS canaux_tp, (SELECT COUNT(*) FROM dwh.dim_canal) AS canaux_livre,
       (SELECT COUNT(*) FROM tp.dim_promotion) AS promos_tp, (SELECT COUNT(*) FROM dwh.dim_promotion) AS promos_livre,
       (SELECT COUNT(*) FROM (SELECT canal, mode_livraison FROM tp.dim_canal EXCEPT
                              SELECT canal, mode_livraison FROM dwh.dim_canal)) AS canaux_differents;
```
<!--sortie-->
```text
 canaux_tp  canaux_livre  promos_tp  promos_livre  canaux_differents
         7             7          4             4                  0
```

**À vous.** Les clés de `tp.dim_promotion` ne sont pas les mêmes que celles du livre (ordre alphabétique contre ordre choisi). Est-ce un problème ? Que se passerait-il si l'on mélangeait les deux tables dans une même jointure ? (Piste : une clé de substitution n'a de sens **que dans l'entrepôt qui l'a créée**.)

> 📒 Ce travail prépare les **exercices 1.2 à 1.4**.

### Application 1.3 — Contrôles de chargement (sections 1.2.3 et 1.3.5)

**Objectif.** Transformer les vérifications du livre en une **fonction de contrôle** réutilisable, puis la mettre à l'épreuve sur un chargement **volontairement cassé**.

**Étape 1 — la fonction.** Quatre contrôles : mêmes effectifs que la source, même total, aucune clé orpheline (une ligne de fait dont le produit n'existe pas dans la dimension), grain respecté.

```python
def controles(dim_produit="dwh.dim_produit", fait="dwh.fait_ventes"):
    q = lambda s: con.df(s).iloc[0, 0]
    res = {
        "effectifs identiques": q(f"SELECT (SELECT COUNT(*) FROM src.lignes_commande) = (SELECT COUNT(*) FROM {fait})"),
        "total TTC identique": q(f"SELECT ABS((SELECT SUM(montant) FROM src.lignes_commande) - (SELECT SUM(montant_ttc) FROM {fait})) < 0.01"),
        "aucune clé orpheline": q(f"SELECT COUNT(*) = 0 FROM {fait} f LEFT JOIN {dim_produit} p USING (produit_key) WHERE p.produit_key IS NULL"),
        "grain tenu": q(f"SELECT COUNT(*) = COUNT(DISTINCT id_ligne) FROM {fait}"),
    }
    return pd.Series(res)

print(controles().to_string())
```
<!--sortie-->
```text
effectifs identiques    True
total TTC identique     True
aucune clé orpheline    True
grain tenu              True
```

**Étape 2 — un chargement cassé.** On simule un incident : la dimension des produits est reconstruite **sans** les produits dont l'identifiant est multiple de 20. Les contrôles le voient-ils ?

```python
con.executescript("CREATE TABLE tp.dim_produit_cassee AS SELECT * FROM dwh.dim_produit WHERE id_produit % 20 <> 0")
print(controles(dim_produit="tp.dim_produit_cassee").to_string())
perdu = con.df("""SELECT COUNT(*) AS lignes, ROUND(SUM(f.montant_ttc)) AS ttc FROM dwh.fait_ventes f
                  LEFT JOIN tp.dim_produit_cassee p USING (produit_key) WHERE p.produit_key IS NULL""").iloc[0]
print(f"{int(perdu['lignes'])} lignes ({perdu['ttc']:,.0f} € TTC) n'ont plus de produit".replace(",", " "))
```
<!--sortie-->
```text
effectifs identiques     True
total TTC identique      True
aucune clé orpheline    False
grain tenu               True
1774 lignes (69 550 € TTC) n'ont plus de produit
```

**À vous.** Ajoutez un cinquième contrôle : **le total hors taxe de l'étoile retrouve le chiffre d'affaires du compte de résultat à un euro près** (table `src.compte_resultat`, colonne `ca_ht`). Sur quel chiffre porte-t-il : celui de chaque mois, ou celui de l'année ?

> 📒 Ce travail prépare les **exercices 1.4, 1.8** et le chapitre 2 (les contrôles deviennent une étape du chargement).

### Application 1.4 — Le grain et les mesures (sections 1.3.1 à 1.3.3)

**Objectif.** Calculer **correctement** un panier moyen et une marge nette des frais de port, en respectant les grains.

**Étape 1 — le panier moyen.** Si l'on moyenne les montants de `fait_ventes`, on obtient le montant moyen d'une **ligne**, pas le panier d'une **commande**. Le bon calcul s'appuie sur la table au grain de la commande.

```sql
SELECT (SELECT ROUND(AVG(montant_ttc), 2) FROM dwh.fait_ventes) AS moyenne_par_ligne,
       (SELECT ROUND(AVG(montant_ttc), 2) FROM dwh.fait_commandes) AS panier_moyen,
       (SELECT ROUND(SUM(montant_ttc) / COUNT(DISTINCT id_commande), 2) FROM dwh.fait_ventes) AS panier_recompte;
```
<!--sortie-->
```text
 moyenne_par_ligne  panier_moyen  panier_recompte
             43.54        100.38           100.38
```

Les deux derniers chiffres sont égaux : le panier moyen est une **somme divisée par un nombre de commandes distinctes**, ce qui s'obtient aussi bien dans l'une ou l'autre table, à condition de **compter les commandes** et non les lignes.

**Étape 2 — la marge nette des frais de port.** On répartit les frais de port de chaque commande **au prorata du montant** des lignes, puis on calcule la marge hors taxe par catégorie. Le contrôle est que la somme des frais répartis retrouve le total.

```python
marge = con.df("""
    SELECT p.categorie, ROUND(SUM(v.montant_ht - v.cout_achat)) AS marge_brute,
           ROUND(SUM(c.frais_port * v.montant_ttc / c.montant_ttc) / 1.2) AS port_reparti_ht
    FROM dwh.fait_ventes v JOIN dwh.fait_commandes c USING (id_commande)
    JOIN dwh.dim_produit p ON p.produit_key = v.produit_key GROUP BY 1 ORDER BY 1""")
marge["marge_nette"] = marge["marge_brute"] - marge["port_reparti_ht"]
print(marge.to_string(index=False))
total_port = con.df("SELECT SUM(frais_port) / 1.2 AS t FROM dwh.fait_commandes")["t"][0]
print("contrôle :", round(marge["port_reparti_ht"].sum()), "contre", round(total_port))
```
<!--sortie-->
```text
 categorie  marge_brute  port_reparti_ht  marge_nette
 Bien-être      91816.0           5420.0      86396.0
   Cuisine     199010.0           7347.0     191663.0
Décoration     230078.0           8404.0     221674.0
    Jardin     299548.0           5159.0     294389.0
    Maison     254326.0           6076.0     248250.0
 Papeterie      47061.0           5998.0      41063.0
contrôle : 38404 contre 38404
```

**À vous.** Les frais de port sont facturés **au client** : sont-ils un produit ou une charge de la boutique ? La réponse change le signe du calcul ci-dessus. Écrivez, comme à l'application 1.1, la ligne de la fiche de définition qui tranche, et dites qui doit la valider.

> 📒 Ce travail prépare les **exercices 1.5 à 1.7**.

### Application 1.5 — Cumulative et instantané (section 1.3.4)

**Objectif.** Tirer les deux types de faits qui ne sont pas des transactions : la table **cumulative** des livraisons et l'**instantané** du stock.

**Étape 1 — les délais par mois et par transporteur.** Pour 2025, le délai moyen de livraison (en jours) pour chaque transporteur, mois par mois, calculé en divisant des **sommes** (jamais en moyennant des moyennes).

```python
liv = con.df("""
    SELECT d.mois, t.transporteur, SUM(f.delai_total_j) / COUNT(*) AS delai
    FROM dwh.fait_livraisons f JOIN dwh.dim_date d ON d.date_key = f.date_commande_key
    JOIN dwh.dim_transporteur t USING (transporteur_key) WHERE d.annee = 2025 GROUP BY 1, 2""")
print(liv.pivot(index="mois", columns="transporteur", values="delai").round(1).to_string())
```
<!--sortie-->
```text
transporteur  Transporteur A  Transporteur B  Transporteur C
mois                                                        
1                        5.0             5.6             6.6
2                        4.9             5.5             6.5
3                        5.0             5.5             6.4
4                        5.0             5.8             6.7
5                        5.0             5.6             6.7
6                        5.0             5.7             6.6
7                        5.1             5.5             6.5
8                        5.0             5.5             6.6
9                        4.9             5.6             6.4
10                       5.1             5.8             6.3
11                       5.0             5.7             6.5
12                       6.3             6.9             7.7
```

**Étape 2 — le stock : moyenne et dernière valeur.** Pour chaque catégorie qui figure dans le suivi de stock, le stock **moyen** de l'année (somme entre produits d'un jour, puis moyenne des jours) et le stock au **31 décembre** :

```sql
WITH j AS (SELECT p.categorie, s.date_key, SUM(s.stock_fin_jour) AS stock
           FROM dwh.fait_stock s JOIN dwh.dim_produit p USING (produit_key) GROUP BY 1, 2)
SELECT categorie, ROUND(AVG(stock), 1) AS stock_moyen,
       MAX(stock) FILTER (WHERE date_key = 20251231) AS fin_decembre
FROM j GROUP BY 1 ORDER BY 1;
```
<!--sortie-->
```text
 categorie  stock_moyen  fin_decembre
   Cuisine         95.8           118
Décoration        153.5           139
    Jardin         79.6            79
    Maison         79.0             6
 Papeterie         87.4            50
```

**À vous.** Quelle erreur produirait `SUM(stock_fin_jour)` sur l'année ? À partir de quelle mesure de `fait_stock` pourrait-on calculer un **taux de rupture** (part des jours-produits où le produit manquait) ? Écrivez la requête.

> 📒 Ce travail prépare les **exercices 1.5, 1.6 et 1.9**.

### Application 1.6 — Historique et dimension de type 2 (section 1.4)

**Objectif.** Construire la dimension historisée des clients et la comparer à la dimension courante.

**Étape 1 — la dimension et le fait historisés.**

```sql
CREATE TABLE tp.dim_client_hist AS
SELECT row_number() OVER (ORDER BY id_client, date_debut) AS client_hist_key, id_client, ville,
       CAST(date_debut AS DATE) AS valide_du, CAST(date_fin AS DATE) AS valide_au, courant = 1 AS est_courant
FROM src.hist_clients;
CREATE TABLE tp.fait_ventes_hist AS
SELECT v.id_ligne, v.montant_ttc, d.annee, h.client_hist_key
FROM dwh.fait_ventes v JOIN dwh.dim_client c USING (client_key) JOIN dwh.dim_date d USING (date_key)
JOIN tp.dim_client_hist h ON h.id_client = c.id_client AND d.date BETWEEN h.valide_du AND h.valide_au;
```

**Étape 2 — les contrôles et la part des achats concernés.** On vérifie qu'aucune ligne n'a été perdue ni dupliquée, puis on compte la part des lignes dont la **ville d'achat** diffère de la **ville actuelle**.

```sql
SELECT (SELECT COUNT(*) FROM tp.fait_ventes_hist) AS lignes, (SELECT COUNT(*) FROM dwh.fait_ventes) AS lignes_etoile,
       ROUND(100.0 * SUM(CASE WHEN h.ville <> c.ville THEN 1 ELSE 0 END) / COUNT(*), 2) AS part_lignes_ville_differente_pct
FROM tp.fait_ventes_hist f JOIN tp.dim_client_hist h USING (client_hist_key)
JOIN (SELECT id_client, ville FROM src.hist_clients WHERE courant = 1) c USING (id_client);
```
<!--sortie-->
```text
 lignes  lignes_etoile  part_lignes_ville_differente_pct
  83905          83905                               4.4
```

**À vous.** Pour 2025 seulement, calculez le chiffre d'affaires par ville en type 1 puis en type 2 (`tp.fait_ventes_hist`, colonne `annee`) et listez les trois villes où l'écart relatif est le plus grand. Ces villes sont-elles les plus grandes ? (Piste : l'écart relatif frappe les petites villes.)

> 📒 Ce travail prépare les **exercices 1.10 et 1.11**.

### Application 1.7 — Un data mart et un fichier en colonnes (sections 1.4.5 et 1.5)

**Objectif.** Écrire un petit mart qui stocke des **sommes**, le **réagréger** en trimestres sans se tromper, puis comparer deux compressions de Parquet.

**Étape 1 — le mart de logistique.** Une ligne par mois et par transporteur, avec des comptes et des sommes ; le taux de retard trimestriel se **recalcule** à partir d'eux.

```sql
CREATE TABLE tp.service AS
SELECT d.annee_mois, d.trimestre, d.annee, t.transporteur, COUNT(*) AS commandes, SUM(f.retard) AS retards
FROM dwh.fait_livraisons f JOIN dwh.dim_date d ON d.date_key = f.date_commande_key
JOIN dwh.dim_transporteur t USING (transporteur_key) GROUP BY ALL;
SELECT annee, trimestre, transporteur, commandes, ROUND(100.0 * retards / commandes, 1) AS retard_pct
FROM (SELECT annee, trimestre, transporteur, SUM(commandes) AS commandes, SUM(retards) AS retards
      FROM tp.service WHERE annee = 2025 GROUP BY ALL) WHERE transporteur = 'Transporteur C' ORDER BY 1, 2;
```
<!--sortie-->
```text
 annee  trimestre   transporteur  commandes  retard_pct
  2025          1 Transporteur C        301        43.9
  2025          2 Transporteur C        314        49.7
  2025          3 Transporteur C        334        45.5
  2025          4 Transporteur C        529        62.6
```

**Étape 2 — deux compressions.** On écrit la table de faits en Parquet avec deux méthodes de compression et l'on compare les tailles (dans un dossier temporaire, supprimé à la fin).

```python
TMP = tempfile.mkdtemp(dir=os.environ.get("TMPDIR"), prefix="cahier01_")
for codec in ["snappy", "zstd"]:
    con.executescript(f"COPY dwh.fait_ventes TO '{TMP}/{codec}.parquet' (FORMAT parquet, COMPRESSION {codec})")
tailles = {c: os.path.getsize(f"{TMP}/{c}.parquet") / 1024 for c in ["snappy", "zstd"]}
print({c: f"{t:.0f} ko" for c, t in tailles.items()}, "| rapport :", round(tailles["snappy"] / tailles["zstd"], 2))
assert TMP.startswith(os.environ.get("TMPDIR", "/tmp"))
shutil.rmtree(TMP)
```
<!--sortie-->
```text
{'snappy': '1268 ko', 'zstd': '818 ko'} | rapport : 1.55
```

**À vous.** Dans le mart, pourquoi stocker `retards` et `commandes` plutôt que `retard_pct` ? Écrivez la requête qui donnerait, **à partir de ce mart seul**, le taux de retard annuel de tous les transporteurs. (Piste : comparez la **moyenne des taux trimestriels** au taux calculé sur les sommes.)

> 📒 Ce travail prépare les **exercices 1.12 et le projet du volume**.

## Exercices

### Exercice 1.1 ⭐ — OLTP ou OLAP ? (section 1.1.1)

Pour chacune des six demandes suivantes, dites si elle relève de l'**exploitation** (OLTP) ou de l'**analyse** (OLAP), et dans quel schéma (`src` ou `dwh`) vous l'exécuteriez : (a) afficher les articles de la commande 3 000 ; (b) enregistrer un retour ; (c) le chiffre d'affaires par canal et par trimestre depuis trois ans ; (d) corriger l'adresse d'un client ; (e) le taux de retour par catégorie ; (f) vérifier qu'un colis est parti.

### Exercice 1.2 ⭐ — Où sont les faits ? (section 1.2.1)

Voici trois lignes d'un classeur à plat de la logistique :

| livraison | date d'expédition | transporteur | ville de livraison | poids (kg) | coût du transport (€) |
|---|---|---|---|---|---|
| 1 | 3 janv. | Transporteur A | Ville B | 1,2 | 4,10 |
| 2 | 3 janv. | Transporteur C | Ville A | 0,8 | 3,60 |
| 3 | 4 janv. | Transporteur A | Ville B | 2,5 | 5,40 |

Dites quelle est la **table de faits** (son grain, ses mesures) et quelles sont les **dimensions**. Y a-t-il une mesure non additive ?

### Exercice 1.3 ⭐ — Une requête sur l'étoile (section 1.2.3)

Écrivez une requête SQL qui donne le **chiffre d'affaires hors taxe par trimestre et par canal** pour 2025 en n'utilisant que l'étoile (`dwh`), puis **vérifiez** le total par pandas, à partir de `commandes.csv` et `lignes_commande.csv`.

### Exercice 1.4 ⭐⭐ — Critique d'une table mal modélisée (sections 1.2 et 1.3)

Un collègue a construit la table suivante pour « faciliter les rapports » :

```python
mauvaise = con.df("""
    SELECT c.id_commande, l.id_ligne, p.nom_produit, p.categorie, l.montant AS montant_ligne,
           c.frais_port AS frais_port_commande, l.remise_pct AS taux_remise, k.ville AS ville_actuelle
    FROM src.commandes c JOIN src.lignes_commande l USING (id_commande)
    JOIN src.produits p USING (id_produit) JOIN src.clients k ON k.id_client = c.id_client""")
print(mauvaise.head(3).to_string(index=False))
```
<!--sortie-->
```text
 id_commande  id_ligne           nom_produit  categorie  montant_ligne  frais_port_commande  taux_remise ville_actuelle
           1         1       Étagère compact     Maison           33.9                  0.0            0        Ville G
           1         2 Set de table rustique    Cuisine           49.9                  0.0            0        Ville G
           2         3       Bougie nordique Décoration           28.9                  0.0            0        Ville F
```

Trouvez **au moins cinq défauts** de modélisation (grain, mesures, clés, historique, valeurs inconnues…) et, pour chacun, dites **quel chiffre faux** il fabriquera.

### Exercice 1.5 ⭐ — Déclarer et tester un grain (section 1.3.1)

Pour chacune des tables `fait_retours`, `fait_livraisons` et `fait_stock` : écrivez la phrase « **une ligne = …** » et une requête qui **teste** ce grain (une clé unique, ou une paire de clés unique).

### Exercice 1.6 ⭐⭐ — Additif ou non ? (section 1.3.2)

(a) Classez en additive, semi-additive ou non additive : la quantité vendue, le prix moyen d'un produit, le nombre de clients actifs, le stock en fin de jour, le taux de retour, la marge en euros, le délai moyen de livraison. (b) Calculez, par canal de vente, le **taux de retour 2025** (retours remboursés rapportés au chiffre d'affaires, en pourcentage) de deux façons : en divisant des sommes, puis en moyennant les taux mensuels. Laquelle est juste ?

### Exercice 1.7 ⭐⭐ — Répartir autrement (section 1.3.3)

Répartissez les frais de port **au prorata de la quantité** (et non du montant) et comparez, par catégorie, la part de frais obtenue avec la répartition au prorata du montant (application 1.4). Contrôlez que la somme est la même dans les deux cas. Laquelle choisiriez-vous pour une marge par produit, et pourquoi ?

### Exercice 1.8 ⭐⭐ — Valeur inconnue (section 1.3.5)

Retirez de la dimension des produits (copie dans `tp`) un produit sur vingt. (a) Mesurez ce que **perd** une jointure interne ; (b) écrivez le chargement qui **rattache** les ventes de ces produits à la ligne « inconnu » (clé 0) sans rien perdre ; (c) comparez les totaux.

### Exercice 1.9 ⭐⭐⭐ — Trois faits, une table (section 1.3.6)

Pour le premier trimestre 2025 et chaque catégorie présente dans `fait_stock`, construisez **en une table** : le chiffre d'affaires hors taxe (`fait_ventes`), les retours (`fait_retours`) et le **nombre de jours-produits en rupture** (`fait_stock`). Aucune jointure directe entre faits : on agrège chacun, puis on joint.

### Exercice 1.10 ⭐⭐ — Quel type pour quel attribut ? (section 1.4.2)

Pour chacun de ces six attributs, choisissez un traitement (type 1, 2 ou 3, ou « pas dans la dimension ») et justifiez : (a) la faute de frappe dans le nom d'un produit ; (b) la ville d'un client ; (c) la catégorie d'un produit reclassée une fois ; (d) le nombre d'achats cumulé d'un client ; (e) le transporteur habituel d'une ville ; (f) le fournisseur d'un produit (changé deux fois en trois ans).

### Exercice 1.11 ⭐⭐⭐ — Un chargement de type 2 idempotent (section 1.4.4)

Sur une copie de la dimension historisée des produits (créée à partir de `ch01-historique-produits.csv`), écrivez la **fonction de chargement** qui reçoit un instantané (id, catégorie), ferme les versions changées et insère les nouvelles. Appliquez-la à un instantané où **deux** produits changent de catégorie au 1er janvier 2026, puis **une seconde fois** : le nombre de lignes doit rester le même.

### Exercice 1.12 ⭐⭐ — Quelle clé de partition ? (section 1.5.3)

On veut alimenter un tableau de bord qui filtre presque toujours sur **l'année** puis sur le **canal**. Écrivez la table de faits en Parquet **partitionnée par année**, puis **partitionnée par canal** (`canal_key`), et comptez les fichiers ouverts pour la requête « chiffre d'affaires 2025, canal Site ». Laquelle des deux clés de partition recommandez-vous, et pourquoi ?

## Corrigés

### Corrigé 1.1

(a) **OLTP** (une consultation de quelques lignes), schéma `src`. (b) **OLTP** (une écriture), `src`. (c) **OLAP** (toute la table des ventes), `dwh`. (d) **OLTP** (une mise à jour de la source ; l'entrepôt la verra au prochain chargement, avec l'historique si la dimension est de type 2). (e) **OLAP**, `dwh` : il rapproche deux processus. (f) **OLTP** : une consultation unitaire à l'instant présent.

La règle de décision : **combien de lignes lit-on, et pour quoi faire ?** Peu, pour enregistrer ou consulter un cas : exploitation. Beaucoup, pour comparer ou additionner : analyse.

### Corrigé 1.2

La **table de faits** est « une **livraison** » (une ligne par colis expédié) ; ses **mesures** sont le poids et le coût du transport, toutes deux additives ; les **dimensions** sont la date d'expédition, le transporteur et la ville de livraison (et le numéro de livraison est une dimension **dégénérée**). Une mesure non additive apparaîtrait si l'on ajoutait un **coût au kilo** (rapport de deux mesures) : on stocke le poids et le coût, et le coût au kilo se recalcule par `SUM(cout) / SUM(poids)`.

### Corrigé 1.3

```sql
SELECT d.trimestre, ca.canal, ROUND(SUM(v.montant_ht)) AS ca_ht
FROM dwh.fait_ventes v JOIN dwh.dim_date d USING (date_key) JOIN dwh.dim_canal ca USING (canal_key)
WHERE d.annee = 2025 GROUP BY 1, 2 ORDER BY 1, 2;
```
<!--sortie-->
```text
 trimestre    canal    ca_ht
         1 Boutique  92501.0
         1  Réseaux  19048.0
         1     Site  98125.0
         2 Boutique 111547.0
         2  Réseaux  29064.0
         2     Site 118374.0
         3 Boutique 109020.0
         3  Réseaux  31055.0
         3     Site 122069.0
         4 Boutique 154411.0
         4  Réseaux  42561.0
         4     Site 176195.0
```

La vérification par pandas, à partir des fichiers d'origine, et la comparaison avec le résultat SQL :

```python
cmd = pd.read_csv(f"{D}/commandes.csv", usecols=["id_commande", "date_commande", "canal"])
lig = pd.read_csv(f"{D}/lignes_commande.csv", usecols=["id_commande", "montant"])
x = lig.merge(cmd, on="id_commande")
x = x[x["date_commande"].str[:4] == "2025"].assign(trimestre=lambda t: (t["date_commande"].str[5:7].astype(int) - 1) // 3 + 1)
pdv = x.groupby(["trimestre", "canal"])["montant"].sum() / 1.2
sqlv = con.df("""SELECT d.trimestre, ca.canal, SUM(v.montant_ht) AS ca_ht FROM dwh.fait_ventes v JOIN dwh.dim_date d USING (date_key)
                 JOIN dwh.dim_canal ca USING (canal_key) WHERE d.annee = 2025 GROUP BY 1, 2""").set_index(["trimestre", "canal"])["ca_ht"]
print(len(pdv), "chiffres comparés ; écart maximal SQL / pandas :", round((pdv - sqlv).abs().max(), 6), "€")
```
<!--sortie-->
```text
12 chiffres comparés ; écart maximal SQL / pandas : 0.0 €
```

Les douze chiffres coïncident.

### Corrigé 1.4

Cinq défauts au moins, et le chiffre faux qu'ils fabriquent :

1. **Deux grains dans une table** (la ligne et l'en-tête de commande) : `frais_port_commande` est répété sur chaque ligne ; sa somme **surestime** les frais de port (+ 64 % sur trois ans).
2. **Un taux stocké comme mesure** (`taux_remise`) : sa moyenne n'est pas la remise globale ; un tableau de bord qui « moyenne la colonne » donne un chiffre faux.
3. **Des clés textuelles** : `nom_produit` n'est pas unique (120 identifiants pour 60 noms) ; regrouper par nom **fusionne** des produits.
4. **Pas d'historique** : `ville_actuelle` rattache les achats anciens à la ville actuelle du client (jusqu'à 9,4 % d'écart pour une ville).
5. **Pas de ligne « inconnu »** ni de dimension de date : tout filtre sur le trimestre ou le jour de la semaine est réécrit dans chaque requête, avec ses variantes ; un client absent de la source fait **disparaître** la ligne à la jointure.
6. **Aucune définition écrite** : la table contient `montant_ligne` sans dire s'il est TTC ou hors taxe, avant ou après remise.

Illustration du défaut 1, en trois lignes :

```python
print("frais de port, somme de la colonne :", round(mauvaise["frais_port_commande"].sum()), "€ ; vrai total :",
      round(con.df("SELECT SUM(frais_port) AS t FROM src.commandes")["t"][0]), "€")
```
<!--sortie-->
```text
frais de port, somme de la colonne : 75458 € ; vrai total : 46085 €
```

### Corrigé 1.5

- `fait_retours` : « une ligne = **un retour** (une ligne de commande retournée) ». Test : `SELECT COUNT(*) = COUNT(DISTINCT id_retour) FROM dwh.fait_retours`.
- `fait_livraisons` : « une ligne = **une commande livrée** ». Test : `COUNT(*) = COUNT(DISTINCT id_commande)`.
- `fait_stock` : « une ligne = **un produit un jour donné** ». Test sur la **paire** de clés : `COUNT(*) = COUNT(DISTINCT (produit_key, date_key))`.

```sql
SELECT (SELECT COUNT(*) = COUNT(DISTINCT id_retour) FROM dwh.fait_retours) AS retours_ok,
       (SELECT COUNT(*) = COUNT(DISTINCT id_commande) FROM dwh.fait_livraisons) AS livraisons_ok,
       (SELECT COUNT(*) = COUNT(DISTINCT (produit_key, date_key)) FROM dwh.fait_stock) AS stock_ok;
```
<!--sortie-->
```text
 retours_ok  livraisons_ok  stock_ok
       True           True      True
```

### Corrigé 1.6

(a) Quantité vendue : **additive**. Prix moyen d'un produit : **non additive** (recalculée par somme / somme). Nombre de clients actifs : **non additive** (un client actif sur deux mois n'est compté qu'une fois). Stock en fin de jour : **semi-additive** (additive entre produits, pas dans le temps). Taux de retour : **non additive** (rapport de sommes). Marge en euros : **additive**. Délai moyen de livraison : **non additive** (somme des délais / nombre de livraisons).

(b) Les deux calculs par canal :

```python
r = con.df("""
    WITH v AS (SELECT ca.canal, d.annee_mois AS mois, SUM(f.montant_ht) AS ca FROM dwh.fait_ventes f
               JOIN dwh.dim_date d USING (date_key) JOIN dwh.dim_canal ca USING (canal_key) WHERE d.annee = 2025 GROUP BY 1, 2),
         r AS (SELECT ca.canal, d.annee_mois AS mois, SUM(f.montant_rembourse) / 1.2 AS ret FROM dwh.fait_retours f
               JOIN dwh.dim_date d USING (date_key) JOIN dwh.dim_canal ca USING (canal_key) WHERE d.annee = 2025 GROUP BY 1, 2)
    SELECT v.canal, v.mois, v.ca, COALESCE(r.ret, 0) AS ret FROM v LEFT JOIN r USING (canal, mois)""")
g = r.groupby("canal")[["ca", "ret"]].sum()
moyenne_taux = r.assign(t=r["ret"] / r["ca"]).groupby("canal")["t"].mean()
print(pd.DataFrame({"somme/somme (%)": (100 * g["ret"] / g["ca"]).round(2), "moyenne des taux (%)": (100 * moyenne_taux).round(2)}).to_string())
```
<!--sortie-->
```text
          somme/somme (%)  moyenne des taux (%)
canal                                          
Boutique             3.24                  3.28
Réseaux              6.66                  6.81
Site                 9.03                  9.11
```

Le calcul **juste** est celui qui divise des **sommes** : il donne à chaque mois le poids de son chiffre d'affaires. La moyenne des taux mensuels donne autant de poids à janvier (creux) qu'à décembre (pic). L'écart est ici faible (de 0,04 à 0,15 point) parce que les taux varient peu d'un mois à l'autre ; il est **systématique**, et il deviendrait grand avec un taux qui varie beaucoup ou des volumes très inégaux.

### Corrigé 1.7

```python
rep = con.df("""
    SELECT p.categorie, SUM(c.frais_port * v.quantite / q.n) AS par_quantite, SUM(c.frais_port * v.montant_ttc / c.montant_ttc) AS par_montant
    FROM dwh.fait_ventes v JOIN dwh.fait_commandes c USING (id_commande)
    JOIN (SELECT id_commande, SUM(quantite) AS n FROM dwh.fait_ventes GROUP BY 1) q USING (id_commande)
    JOIN dwh.dim_produit p ON p.produit_key = v.produit_key GROUP BY 1 ORDER BY 1""").set_index("categorie")
print(rep.round(0).to_string())
print("totaux :", round(rep["par_quantite"].sum(), 1), "et", round(rep["par_montant"].sum(), 1))
```
<!--sortie-->
```text
            par_quantite  par_montant
categorie                            
Bien-être         6431.0       6504.0
Cuisine           7820.0       8816.0
Décoration        9299.0      10085.0
Jardin            6293.0       6191.0
Maison            6767.0       7291.0
Papeterie         9474.0       7198.0
totaux : 46084.6 et 46084.6
```

Les deux répartitions retrouvent le **même total**, mais déplacent des frais entre catégories : les articles bon marché en reçoivent plus quand on répartit **par quantité** (la papeterie : 9 474 € contre 7 198 € au prorata du montant), les articles plus chers en reçoivent moins (la cuisine : 7 820 € contre 8 816 €). Pour une **marge par produit**, on préfère le **montant** si les frais suivent la valeur (une assurance), la **quantité** s'ils suivent le volume manipulé. Le choix est une **règle de gestion** à faire valider, et à écrire dans la définition.

### Corrigé 1.8

```python
con.executescript("CREATE TABLE tp.dim_produit_inc AS SELECT * FROM dwh.dim_produit WHERE produit_key = 0 OR id_produit % 20 <> 0")
r = con.df("""
    SELECT 'jointure interne' AS methode, COUNT(*) AS lignes, ROUND(SUM(v.montant_ttc)) AS ttc
    FROM dwh.fait_ventes v JOIN tp.dim_produit_inc p USING (produit_key)
    UNION ALL
    SELECT 'rattachement à inconnu', COUNT(*), ROUND(SUM(v.montant_ttc))
    FROM dwh.fait_ventes v LEFT JOIN tp.dim_produit_inc p USING (produit_key)""")
print(r.to_string(index=False))
con.executescript("""CREATE TABLE tp.ventes_rattachees AS
    SELECT v.id_ligne, COALESCE(p.produit_key, 0) AS produit_key, v.montant_ttc
    FROM dwh.fait_ventes v LEFT JOIN tp.dim_produit_inc p USING (produit_key)""")
print(con.df("SELECT COUNT(*) AS lignes, ROUND(SUM(montant_ttc)) AS ttc, SUM(CASE WHEN produit_key = 0 THEN montant_ttc END) AS dont_inconnu FROM tp.ventes_rattachees").round(0).to_string(index=False))
```
<!--sortie-->
```text
               methode  lignes       ttc
      jointure interne   82131 3583608.0
rattachement à inconnu   83905 3653157.0
 lignes       ttc  dont_inconnu
  83905 3653157.0       69550.0
```

La jointure interne perd les lignes des produits retirés ; le rattachement à la clé 0 les conserve toutes, et le total retrouve celui de la source. La part « inconnu » est **visible** : c'est elle qu'on surveille, et qui doit retomber à zéro dès que la dimension est complétée.

### Corrigé 1.9

```python
t = con.df("""
    WITH v AS (SELECT p.categorie, SUM(f.montant_ht) AS ca_ht FROM dwh.fait_ventes f JOIN dwh.dim_date d USING (date_key)
               JOIN dwh.dim_produit p USING (produit_key) WHERE d.date BETWEEN '2025-01-01' AND '2025-03-31' GROUP BY 1),
         r AS (SELECT p.categorie, SUM(f.montant_rembourse) / 1.2 AS retours_ht FROM dwh.fait_retours f JOIN dwh.dim_date d USING (date_key)
               JOIN dwh.dim_produit p USING (produit_key) WHERE d.date BETWEEN '2025-01-01' AND '2025-03-31' GROUP BY 1),
         s AS (SELECT p.categorie, SUM(f.rupture) AS jours_rupture, COUNT(*) AS jours_produits FROM dwh.fait_stock f JOIN dwh.dim_date d USING (date_key)
               JOIN dwh.dim_produit p USING (produit_key) WHERE d.date BETWEEN '2025-01-01' AND '2025-03-31' GROUP BY 1)
    SELECT categorie, ROUND(ca_ht) AS ca_ht, ROUND(COALESCE(retours_ht, 0)) AS retours_ht, jours_rupture, jours_produits
    FROM s JOIN v USING (categorie) LEFT JOIN r USING (categorie) ORDER BY 1""")
print(t.to_string(index=False))
```
<!--sortie-->
```text
 categorie   ca_ht  retours_ht  jours_rupture  jours_produits
   Cuisine 44741.0      2685.0            9.0             360
Décoration 45956.0      3591.0           30.0             540
    Jardin 24911.0      1922.0            2.0             270
    Maison 60992.0      4173.0           18.0             270
 Papeterie 10206.0       577.0           33.0             360
```

Chaque fait est **agrégé à la catégorie d'abord**, puis les trois résultats sont joints : aucune ligne n'est multipliée. Le contrôle : le chiffre d'affaires de chaque catégorie est celui que donne la requête sur `fait_ventes` seul. (Seules les catégories qui figurent dans le suivi de stock apparaissent : la jointure interne entre `s` et `v` les restreint, et c'est un choix à documenter.)

### Corrigé 1.10

(a) **Type 1** : c'est une correction, l'ancienne valeur n'a aucune valeur historique. (b) **Type 2** : l'analyse géographique des ventes passées dépend de la ville **d'alors** (section 1.4.3). (c) **Type 2** si l'on compare les catégories dans le temps (comme dans l'exemple du livre, où la cuisine paraît 32 % trop grande), ou **type 3** si l'on veut seulement comparer « avant » et « après » ce reclassement unique. (d) **Pas dans la dimension** : un attribut qui change à chaque achat se range dans un fait (instantané périodique) ou une **mini-dimension** de tranches. (e) **Type 1 ou 2** selon que l'on veut rejouer l'historique des décisions logistiques ; à défaut d'usage précis, type 1. (f) **Type 2** : deux changements en trois ans, et les achats auprès de chaque fournisseur se rattachent à celui d'alors ; un type 3 ne garderait qu'un seul prédécesseur.

### Corrigé 1.11

```python
con.executescript("CREATE TABLE tp.dim_prod AS SELECT id_produit, categorie, CAST(date_debut AS DATE) AS valide_du, CAST(date_fin AS DATE) AS valide_au FROM read_csv_auto('" + f"{D}/ch01-historique-produits.csv')")

def charger_type2(con, arrivee, date_effet):
    con.d.register("arrivee", arrivee)
    con.executescript(f"""UPDATE tp.dim_prod d SET valide_au = DATE '{date_effet}' - 1 FROM arrivee a
        WHERE a.id_produit = d.id_produit AND d.valide_au = DATE '9999-12-31' AND a.categorie <> d.categorie""")
    con.executescript(f"""INSERT INTO tp.dim_prod SELECT a.id_produit, a.categorie, DATE '{date_effet}', DATE '9999-12-31' FROM arrivee a
        LEFT JOIN tp.dim_prod d ON d.id_produit = a.id_produit AND d.valide_au = DATE '9999-12-31' WHERE d.id_produit IS NULL""")

courant = con.df("SELECT id_produit, categorie FROM tp.dim_prod WHERE valide_au = DATE '9999-12-31'")
arrivee = courant.copy()
arrivee.loc[arrivee["id_produit"].isin([7, 8]), "categorie"] = "Jardin"       # deux produits changent de catégorie
n0 = con.df("SELECT COUNT(*) AS n FROM tp.dim_prod")["n"][0]
charger_type2(con, arrivee, "2026-01-01"); n1 = con.df("SELECT COUNT(*) AS n FROM tp.dim_prod")["n"][0]
charger_type2(con, arrivee, "2026-01-01"); n2 = con.df("SELECT COUNT(*) AS n FROM tp.dim_prod")["n"][0]
print("lignes avant :", n0, "| après un chargement :", n1, "| après un second :", n2)
```
<!--sortie-->
```text
lignes avant : 128 | après un chargement : 130 | après un second : 130
```

La première passe ferme les versions de deux produits et en insère deux nouvelles (**+ 2 lignes**, de 128 à 130) ; la seconde passe ne trouve **rien à faire** : le chargement est **idempotent**. C'est cette propriété qui permet de relancer sans crainte un chargement interrompu (chapitre 2).

### Corrigé 1.12

```python
TMP = tempfile.mkdtemp(dir=os.environ.get("TMPDIR"), prefix="cahier01_")
con.executescript("CREATE TABLE tp.vf AS SELECT v.*, d.annee FROM dwh.fait_ventes v JOIN dwh.dim_date d USING (date_key)")
ck = con.df("SELECT canal_key FROM dwh.dim_canal WHERE canal = 'Site' AND mode_livraison = 'Domicile'")["canal_key"][0]
for cle in ["annee", "canal_key"]:
    con.executescript(f"COPY tp.vf TO '{TMP}/part_{cle}' (FORMAT parquet, PARTITION_BY ({cle}))")
    plan = con.df(f"""EXPLAIN SELECT SUM(montant_ttc) FROM read_parquet('{TMP}/part_{cle}/*/*.parquet', hive_partitioning = true)
                      WHERE annee = 2025 AND canal_key = {ck}""").iloc[0, 1]
    print(f"partition par {cle} : fichiers ouverts", re.search(r"Scanning Files: (\d+/\d+)", plan).group(1))
assert TMP.startswith(os.environ.get("TMPDIR", "/tmp"))
shutil.rmtree(TMP)
```
<!--sortie-->
```text
partition par annee : fichiers ouverts 1/3
partition par canal_key : fichiers ouverts 1/7
```

Le canal est ici un couple (canal de vente, mode de livraison) à sept valeurs : le partitionnement par canal ouvre **un fichier sur sept** ; celui par année **un sur trois**. On recommande de partitionner par **la colonne qui filtre le plus et dont les valeurs sont nombreuses et croissantes dans le temps** : l'**année** (ou, mieux, le mois quand la table est grande), parce qu'on ajoute des partitions sans réécrire les anciennes. Partitionner par canal multiplie les petits fichiers et n'aide qu'un filtre précis ; on laisse le **regroupement** (*clustering*) s'en charger à l'intérieur des partitions. (On n'a filtré que sur **un** des sept couples canal-mode ; un filtre sur le seul canal `Site` ouvrirait trois fichiers sur sept.)

## Pistes des applications

Quelques pistes pour les « À vous » des applications.

**Application 1.1 (définition).** Le **net des retours** doit trancher la **période de rattachement** : on retranche les retours **de la période** (date du retour : simple, mais mélange des ventes de périodes différentes) ou ceux **des ventes de la période** (date de la vente : plus juste, mais le chiffre change après coup quand de nouveaux retours arrivent, et il faut un recul). Le **panier moyen** se calcule **par commande** : `SUM(montant_ttc) / COUNT(DISTINCT id_commande)`, porté par `dwh.fait_commandes`.

**Application 1.2 (dimensions).** Oui, c'est un problème si l'on mélange : les clés de substitution n'ont de sens que dans la table qui les a créées. Deux entrepôts qui numérotent différemment ne se joignent **que par la clé naturelle** (le code), jamais par la clé de substitution.

**Application 1.3 (contrôles).** Le cinquième contrôle porte sur **chaque mois** : un écart annuel peut cacher des écarts mensuels qui se compensent. Dans le livre, l'écart maximal sur 36 mois est de 0,49 €.

**Application 1.4 (frais de port).** Facturés au client, ils sont un **produit** (un revenu), rarement un chiffre d'affaires de vente ; on les range à part. Le signe de la marge nette dépend donc de la **charge réelle** payée au transporteur, qui n'est pas dans nos données. La fiche doit nommer **la direction financière** comme propriétaire.

**Application 1.5 (stock).** `SUM(stock_fin_jour)` sur l'année additionne le même stock 365 fois. Le taux de rupture se calcule à partir de l'indicateur `rupture` (0/1) : `SUM(rupture) / COUNT(*)` sur la période.

**Application 1.6 (type 2).** Les villes où l'écart relatif est le plus grand sont les **petites villes** : quelques déménagements pèsent beaucoup sur un petit chiffre d'affaires.

**Application 1.7 (mart).** On stocke des sommes parce que `retard_pct` ne se réagrège pas : le taux annuel est `SUM(retards) / SUM(commandes)`, et non la moyenne des taux trimestriels.
