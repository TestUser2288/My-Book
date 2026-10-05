## 5.4 Normalisation et conception de schémas

> 💡 **Intuition.** Pourquoi avoir découpé les données de la boutique en cinq tables, au lieu d'un seul grand tableau, comme dans Excel ? Parce qu'un tableau unique **répète** les mêmes informations (la ville d'une cliente apparaît sur chacune de ses commandes), et que **tout ce qui est répété finit par se contredire**. La **normalisation** est la méthode qui consiste à ranger chaque fait **une seule fois**, à sa place. Cette section explique *pourquoi* le schéma du 5.1 est bon, et vous donne la méthode pour en concevoir un vous-même. Nous terminerons par deux sujets de **performance et de fiabilité** : les index et les transactions.

### 5.4.1 Le problème : la grande feuille unique

Imaginons que la gérante ait gardé son habitude du tableur : **une seule feuille** avec une ligne par article vendu, contenant tout ce qu'on sait sur la commande, la cliente et le produit. Fabriquons cette feuille pour les **huit premières commandes** : nous créons dans la base des tables de travail préfixées `ex_` (nous les supprimerons à la fin de la section).

```sql
CREATE TABLE ex_feuille (
    id_commande INTEGER NOT NULL, id_produit INTEGER NOT NULL,
    date_commande TEXT, id_client INTEGER, prenom TEXT, nom TEXT, ville TEXT,
    nom_produit TEXT, id_categorie INTEGER, nom_categorie TEXT, prix_catalogue REAL,
    quantite INTEGER, prix_unitaire REAL,
    PRIMARY KEY (id_commande, id_produit)
);
INSERT INTO ex_feuille
SELECT c.id_commande, p.id_produit, c.date_commande, cl.id_client, cl.prenom, cl.nom, cl.ville,
       p.nom, ca.id_categorie, ca.nom, p.prix_catalogue, l.quantite, l.prix_unitaire
FROM commandes AS c
JOIN clients AS cl ON cl.id_client = c.id_client
JOIN lignes_commande AS l ON l.id_commande = c.id_commande
JOIN produits AS p ON p.id_produit = l.id_produit
JOIN categories AS ca ON ca.id_categorie = p.id_categorie
WHERE c.id_commande <= 8;
```

Voici un extrait de la feuille (quelques colonnes seulement pour tenir en largeur) :

```sql
SELECT id_commande, id_produit, id_client, prenom, ville, nom_produit, nom_categorie, quantite
FROM ex_feuille
ORDER BY id_commande, id_produit;
```
<!--sortie-->
```text
 id_commande  id_produit  id_client  prenom    ville                nom_produit nom_categorie  quantite
           1           1          2    Sami   Ville A           Tajine décoratif       Poterie         1
           2          10          6   Hatem Ville C           Pendentif khamsa        Bijoux         1
           3           2          3   Aymen     Ville F Bol en céramique de Ville E       Poterie         1
           3           3          3   Aymen     Ville F       Vase peint à la main       Poterie         1
           3          13          3   Aymen     Ville F    Savon à l'huile d'olive   Cosmétiques         1
           4          11          1 Yassine Ville C         Bracelet de perles        Bijoux         1
           4          14          1 Yassine Ville C              Eau de jasmin   Cosmétiques         1
           5           8          5    Emna   Ville A            Pochette brodée       Textile         2
           5           9          5    Emna   Ville A            Bague en argent        Bijoux         1
           5          15          5    Emna   Ville A           Huile de nigelle   Cosmétiques         1
           6           2          9   Salma    Ville H Bol en céramique de Ville E       Poterie         1
           6           8          9   Salma    Ville H            Pochette brodée       Textile         1
           7           5          4    Emna   Ville A            Foutah en coton       Textile         1
           7           9          4    Emna   Ville A            Bague en argent        Bijoux         1
           8           4          5    Emna   Ville A            Plat à couscous       Poterie         2
           8           5          5    Emna   Ville A            Foutah en coton       Textile         1
```

Regardez la cliente n° 5, Emna Hamdi : elle apparaît sur **cinq lignes**, et sa ville « Ville A » est écrite cinq fois. Même chose pour le produit n° 9 (Bague en argent) et sa catégorie « Bijoux ». Cette redondance cause trois catégories de problèmes, appelées **anomalies**.

**1. Anomalie de mise à jour.** Emna déménage à Ville G. L'employé de la gérante ne corrige qu'**une** ligne sur cinq (il a oublié les autres) :

```sql
UPDATE ex_feuille SET ville = 'Ville G'
WHERE id_client = 5 AND id_commande = 8 AND id_produit = 5;
```

```sql
SELECT id_client, prenom, nom, ville, COUNT(*) AS lignes
FROM ex_feuille
WHERE id_client = 5
GROUP BY id_client, prenom, nom, ville;
```
<!--sortie-->
```text
 id_client prenom   nom  ville  lignes
         5   Emna Hamdi Ville A       4
         5   Emna Hamdi Ville G       1
```

Deux villes pour la même personne : on ne sait plus laquelle est vraie. C'est exactement l'histoire de « Amel Ben Salah » du 5.1.1. Dans notre vraie base, cette erreur est **impossible** : la ville d'une cliente n'est écrite qu'à un seul endroit.

> ⚠️ **Une incohérence ne se résorbe pas toute seule.** Même un `SELECT DISTINCT id_client, ville` ne sait pas « choisir » la bonne ville : il renvoie les deux. Les doublons contradictoires sont de la **vraie** information fausse, que seul un humain peut trancher. Remettons la ville d'origine pour la suite :

```sql
UPDATE ex_feuille SET ville = 'Ville A'
WHERE id_client = 5 AND id_commande = 8 AND id_produit = 5;
```

**2. Anomalie d'insertion.** la gérante veut ajouter au catalogue un nouveau produit, pas encore vendu. Impossible : la feuille n'a de place que pour des *lignes de commande*, et la clé primaire exige un numéro de commande.

```python
try:
    con.execute("INSERT INTO ex_feuille (id_produit, nom_produit, prix_catalogue) VALUES (17, 'Narguilé', 90)")
except sqlite3.IntegrityError as erreur:
    print("refusé :", erreur)
```
<!--sortie-->
```text
refusé : NOT NULL constraint failed: ex_feuille.id_commande
```

(Et en supprimant la contrainte, on aurait une ligne avec des trous partout.)

**3. Anomalie de suppression.** Quels produits n'apparaissent que sur **une seule** ligne de la feuille ? Pour ceux-là, supprimer cette ligne (par exemple parce que la commande est annulée) effacerait **toute trace du produit** : son nom, sa catégorie, son prix catalogue.

```sql
SELECT id_produit, nom_produit, prix_catalogue, MIN(id_commande) AS seule_commande
FROM ex_feuille
GROUP BY id_produit
HAVING COUNT(*) = 1
ORDER BY id_produit;
```
<!--sortie-->
```text
 id_produit             nom_produit  prix_catalogue  seule_commande
          1        Tajine décoratif            45.0               1
          3    Vase peint à la main            65.0               3
          4         Plat à couscous            38.0               8
         10        Pendentif khamsa            35.0               2
         11      Bracelet de perles            15.0               4
         13 Savon à l'huile d'olive             6.0               3
         14           Eau de jasmin            14.0               4
         15        Huile de nigelle            24.0               5
```

Annuler la commande n° 5 ferait disparaître l'huile de nigelle du catalogue : on a voulu supprimer *une vente* et on a perdu *un produit*.

Résumé : dans une table, **tout fait doit être associé à un seul sujet**. Un client, un produit, une commande et une vente sont quatre sujets différents ; les mélanger dans une même table provoque ces trois anomalies.

### 5.4.2 Dépendances fonctionnelles : la théorie derrière la normalisation

> 📐 **Définition.** Dans une table $R$ d'attributs $A$, on dit que $X$ **détermine fonctionnellement** $Y$, noté $X\to Y$ (avec $X,Y\subseteq A$), si deux lignes qui ont la **même valeur de $X$** ont **forcément la même valeur de $Y$** :
> $$\forall\,t_1,t_2\in R,\quad t_1[X]=t_2[X]\ \Longrightarrow\ t_1[Y]=t_2[Y].$$
> Exemples dans notre feuille : `id_client` $\to$ `ville` (un client n'a qu'une ville) ; `id_produit` $\to$ `prix_catalogue` ; mais **pas** `ville` $\to$ `id_client` (plusieurs clientes habitent Ville A).

Une clé primaire est un cas particulier : $K$ est une **clé** de $R$ si $K\to A$ (elle détermine *toutes* les colonnes) et si aucun sous-ensemble strict de $K$ n'en fait autant (minimalité).

Les dépendances fonctionnelles obéissent à trois règles, les **axiomes d'Armstrong** (1974), qui permettent d'en déduire d'autres :

1. **Réflexivité** : si $Y\subseteq X$, alors $X\to Y$ (trivial).
2. **Augmentation** : si $X\to Y$, alors $XZ\to YZ$ pour tout $Z$.
3. **Transitivité** : si $X\to Y$ et $Y\to Z$, alors $X\to Z$.

La **fermeture** $X^+$ d'un ensemble d'attributs est l'ensemble de tout ce qu'il détermine, directement ou par transitivité. On la calcule en partant de $X$ et en ajoutant les attributs déterminés tant que c'est possible. Appliquons-le à notre feuille. Les dépendances que nous croyons vraies (règles de gestion de la boutique) sont :

```python
dependances = [
    (["id_commande"],                ["date_commande", "id_client"]),
    (["id_client"],                  ["prenom", "nom", "ville"]),
    (["id_produit"],                 ["nom_produit", "id_categorie", "prix_catalogue"]),
    (["id_categorie"],               ["nom_categorie"]),
    (["id_commande", "id_produit"],  ["quantite", "prix_unitaire"]),
]

def fermeture(X, deps):
    """Ensemble des attributs déterminés par X (algorithme de point fixe)."""
    res, change = set(X), True
    while change:
        change = False
        for gauche, droite in deps:
            if set(gauche) <= res and not set(droite) <= res:
                res |= set(droite)
                change = True
    return res
```

Avant de s'en servir, vérifions que ces dépendances sont **respectées par les données** de la feuille. On charge celle-ci dans pandas, et l'on teste, pour chaque dépendance $X\to Y$, qu'aucun groupe de lignes de même $X$ ne contient deux valeurs différentes de $Y$ :

```python
feuille = pd.read_sql_query("SELECT * FROM ex_feuille", con)

def verifie(df, X, Y):
    """Vrai si X -> Y n'est contredit par aucune paire de lignes."""
    return bool((df.groupby(X)[Y].nunique() <= 1).all().all())

for gauche, droite in dependances:
    print(f"{' + '.join(gauche):25s} -> {', '.join(droite):45s} {verifie(feuille, gauche, droite)}")

print()
print("ville -> id_client ?               ", verifie(feuille, ["ville"], ["id_client"]))
print("id_commande -> prix_unitaire ?     ", verifie(feuille, ["id_commande"], ["prix_unitaire"]))
```
<!--sortie-->
```text
id_commande               -> date_commande, id_client                      True
id_client                 -> prenom, nom, ville                            True
id_produit                -> nom_produit, id_categorie, prix_catalogue     True
id_categorie              -> nom_categorie                                 True
id_commande + id_produit  -> quantite, prix_unitaire                       True

ville -> id_client ?                False
id_commande -> prix_unitaire ?      False
```

Les cinq dépendances sont respectées ; les deux « fausses » dépendances (`ville` $\to$ `id_client`, `id_commande` $\to$ `prix_unitaire`) sont **contredites** par les données, comme prévu. Attention à la nuance logique : un jeu de données peut seulement **réfuter** une dépendance (une paire de lignes suffit), jamais la **démontrer** ; seule la connaissance du métier (« un client n'a qu'une ville de livraison par défaut ») l'affirme.

Calculons maintenant des fermetures et cherchons la clé de la feuille :

```python
from itertools import combinations

attributs = set(feuille.columns)
print("fermeture de {id_commande}            :", sorted(fermeture(["id_commande"], dependances)))
print("fermeture de {id_client}              :", sorted(fermeture(["id_client"], dependances)))
print()

# clés candidates : sous-ensembles minimaux dont la fermeture est tous les attributs
cles = []
for k in range(1, 4):
    for X in combinations(sorted(attributs), k):
        if fermeture(X, dependances) == attributs and not any(set(c) <= set(X) for c in cles):
            cles.append(X)
print("clé(s) candidate(s) :", cles)
```
<!--sortie-->
```text
fermeture de {id_commande}            : ['date_commande', 'id_client', 'id_commande', 'nom', 'prenom', 'ville']
fermeture de {id_client}              : ['id_client', 'nom', 'prenom', 'ville']

clé(s) candidate(s) : [('id_commande', 'id_produit')]
```

La seule clé est le couple (`id_commande`, `id_produit`) : c'est la clé primaire que nous avions déclarée. Le calcul explique aussi l'origine des anomalies : beaucoup d'attributs dépendent seulement d'**une partie** de la clé (`prenom`, `ville`... dépendent de `id_commande` seul ; `nom_produit`, `prix_catalogue`... de `id_produit` seul), ou d'un attribut qui n'est pas la clé (`ville` dépend de `id_client`, qui dépend de `id_commande`). On a trouvé la source du mal. Il reste à la soigner.

### 5.4.3 Les trois premières formes normales

Les **formes normales** sont des niveaux de « propreté » d'un schéma, chaque niveau supprimant un type de redondance. Retenez la formule qui résume les trois premières, dans l'esprit du serment d'un témoin au tribunal : *chaque attribut dépend de **la clé, de toute la clé, et rien que de la clé*** (« so help me Codd »).

| Forme | Exigence | Anomalie évitée |
|---|---|---|
| **1FN** | chaque case contient **une seule valeur** (atomique) ; pas de listes ni de colonnes répétées | cases du type « Tajine ; Foutah » |
| **2FN** | 1FN **et** aucun attribut ne dépend d'une **partie** de la clé (utile quand la clé est composite) | informations sur le produit répétées sur chaque vente |
| **3FN** | 2FN **et** aucun attribut non-clé ne dépend d'un **autre attribut non-clé** (pas de dépendance transitive) | ville du client recopiée parce que `id_client` détermine `ville` |

**1FN.** Si la gérante avait noté le panier dans une seule case (`articles = "Foutah en coton ; Pochette brodée"`), elle n'aurait pu ni compter les ventes par produit, ni les joindre au catalogue : on ne sait pas jointer un morceau de texte. La solution est **une ligne par article** : c'est ce que fait notre feuille, qui est donc déjà en 1FN (et nous aurions eu le même problème avec des colonnes `produit1`, `produit2`, `produit3`).

**2FN.** La clé de la feuille est composite (`id_commande`, `id_produit`). Or les infos du produit ne dépendent que de `id_produit`, et celles de la commande que de `id_commande` : ce sont des **dépendances partielles**. On découpe : chaque groupe d'attributs va dans une table dont la clé est l'attribut qui le détermine.

```sql
CREATE TABLE ex_lignes AS
SELECT id_commande, id_produit, quantite, prix_unitaire FROM ex_feuille;

CREATE TABLE ex_commandes AS
SELECT DISTINCT id_commande, date_commande, id_client, prenom, nom, ville FROM ex_feuille;

CREATE TABLE ex_produits AS
SELECT DISTINCT id_produit, nom_produit, id_categorie, nom_categorie, prix_catalogue FROM ex_feuille;
```

(`DISTINCT` supprime les doublons : chaque commande et chaque produit n'est plus écrit qu'une fois.) La redondance a déjà fortement baissé, mais elle n'a pas disparu : dans `ex_commandes`, la ville d'Emna est encore écrite pour **chacune** de ses commandes (n° 5 et n° 8). Cause : `id_commande` $\to$ `id_client` $\to$ `ville` : c'est une **dépendance transitive**.

**3FN.** On extrait ce qui dépend d'un attribut non-clé dans sa propre table : les clients (clé `id_client`) d'un côté, les catégories (clé `id_categorie`) de l'autre.

```sql
CREATE TABLE ex_clients AS
SELECT DISTINCT id_client, prenom, nom, ville FROM ex_commandes;

CREATE TABLE ex_categories AS
SELECT DISTINCT id_categorie, nom_categorie FROM ex_produits;

CREATE TABLE ex_commandes3 AS
SELECT DISTINCT id_commande, date_commande, id_client FROM ex_commandes;

CREATE TABLE ex_produits3 AS
SELECT DISTINCT id_produit, nom_produit, id_categorie, prix_catalogue FROM ex_produits;
```

Comptons les lignes de chaque table pour voir la différence :

```sql
SELECT 'feuille unique' AS table_, COUNT(*) AS lignes FROM ex_feuille
UNION ALL SELECT 'lignes',     COUNT(*) FROM ex_lignes
UNION ALL SELECT 'commandes',  COUNT(*) FROM ex_commandes3
UNION ALL SELECT 'clients',    COUNT(*) FROM ex_clients
UNION ALL SELECT 'produits',   COUNT(*) FROM ex_produits3
UNION ALL SELECT 'categories', COUNT(*) FROM ex_categories;
```
<!--sortie-->
```text
        table_  lignes
feuille unique      16
        lignes      16
     commandes       8
       clients       7
      produits      12
    categories       4
```

La grande feuille (16 lignes) est devenue cinq petites tables : exactement la structure du 5.1 ! La normalisation est ce qui a conduit à notre schéma, et un dessin préalable des entités (5.1.2) aurait donné le même résultat plus vite. Les anomalies ont disparu : changer la ville d'Emna se fait par **un seul** `UPDATE` sur **une seule** ligne ; ajouter un produit au catalogue est un simple `INSERT` dans `produits` ; supprimer une vente laisse produit et client intacts.

> 💡 **Le test de sécurité : « décomposer sans rien perdre ».** Découper une table en plusieurs ne doit pas **perdre d'information**. Vérifions que, si l'on recolle les morceaux par des jointures, on retrouve **exactement** la feuille d'origine, ni plus ni moins. On compare dans les deux sens avec `EXCEPT` (5.2.5) : les lignes reconstituées absentes de la feuille, puis l'inverse.

```sql
CREATE TEMP VIEW ex_recollee AS
SELECT l.id_commande, l.id_produit, c.date_commande, c.id_client, cl.prenom, cl.nom, cl.ville,
       p.nom_produit, p.id_categorie, ca.nom_categorie, p.prix_catalogue, l.quantite, l.prix_unitaire
FROM ex_lignes AS l
JOIN ex_commandes3  AS c  ON c.id_commande  = l.id_commande
JOIN ex_clients     AS cl ON cl.id_client   = c.id_client
JOIN ex_produits3   AS p  ON p.id_produit   = l.id_produit
JOIN ex_categories  AS ca ON ca.id_categorie = p.id_categorie;
```

```sql
SELECT (SELECT COUNT(*) FROM (SELECT * FROM ex_recollee EXCEPT SELECT * FROM ex_feuille)) AS en_trop,
       (SELECT COUNT(*) FROM (SELECT * FROM ex_feuille  EXCEPT SELECT * FROM ex_recollee)) AS manquantes;
```
<!--sortie-->
```text
 en_trop  manquantes
       0           0
```

Zéro et zéro : la décomposition est **sans perte**. (Et grâce à la remarque du 5.4.1 sur la ville d'Emna, nous avons pris soin de remettre la feuille en état avant de la découper : normaliser des données **déjà contradictoires** aurait recopié fidèlement la contradiction dans la table `ex_clients`, avec deux lignes pour la même cliente. Un schéma normalisé rend les *nouvelles* incohérences impossibles, par exemple en déclarant `id_client` clé primaire de `clients`, mais ne répare pas les anciennes.)

> 📐 **Pourquoi la décomposition sans perte fonctionne (théorème de Heath).** Soit $R(X,Y,Z)$ une table avec la dépendance $X\to Y$. Alors $R=\pi_{X,Y}(R)\bowtie\pi_{X,Z}(R)$. *Preuve.* L'inclusion $R\subseteq\pi_{XY}(R)\bowtie\pi_{XZ}(R)$ est évidente (toute ligne se retrouve en recollant ses propres morceaux). Réciproquement, soit $(x,y,z)$ dans la jointure : $(x,y)$ vient d'une ligne $(x,y,z')\in R$ et $(x,z)$ d'une ligne $(x,y',z)\in R$. Ces deux lignes ont la **même valeur $x$**, donc, comme $X\to Y$, la **même valeur $y=y'$**. La ligne $(x,y',z)=(x,y,z)$ est donc dans $R$. $\square$ Sans la dépendance, la jointure pourrait fabriquer de **fausses lignes** : c'est le piège de la décomposition faite « au feeling ».

Pour finir proprement, supprimons nos tables de travail (il faut le faire pour que la base redevienne celle du 5.1) :

```python
con.execute("DROP VIEW IF EXISTS ex_recollee")
for t in ["ex_lignes", "ex_commandes3", "ex_clients", "ex_produits3", "ex_categories",
          "ex_commandes", "ex_produits", "ex_feuille"]:
    con.execute(f"DROP TABLE IF EXISTS {t}")
con.commit()
print([r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")])
```
<!--sortie-->
```text
['categories', 'clients', 'commandes', 'lignes_commande', 'produits']
```

### 5.4.4 Aller plus loin, ou s'arrêter plus tôt ?

**La forme normale de Boyce-Codd (BCNF)** renforce la 3FN : pour *toute* dépendance $X\to Y$ non triviale, $X$ doit être une clé. Dans la pratique, la 3FN suffit presque toujours, et un schéma en 3FN est souvent déjà en BCNF. Il existe des formes supérieures (4FN, 5FN) pour des cas plus rares.

**Mais attention : « plus normalisé » n'est pas toujours « mieux ».** Un schéma normalisé est idéal pour **enregistrer** des données (les systèmes *transactionnels*, dits **OLTP** : caisse, site de vente, réservations) : peu de redondance, mises à jour sûres. Pour **analyser** (les systèmes **OLAP** : entrepôts de données, tableaux de bord), l'analyste doit en revanche joindre cinq tables pour la moindre question, ce qui est lent et fastidieux. On **dénormalise** donc volontairement dans les entrepôts, par exemple avec un **schéma en étoile** : au centre, une grosse table de **faits** (les ventes : une ligne par article vendu, avec des montants et des clés), autour d'elle de petites tables de **dimensions** (client, produit, date) qui décrivent le contexte. Notre `lignes_commande` entourée de `commandes`, `produits`, `clients` ressemble déjà à une étoile.

Règle pratique : **normalisez pour écrire, dénormalisez pour lire**. En attendant de construire un entrepôt, une **vue** donne à l'analyste une « grande table » toute prête, sans dupliquer les données : une vue est une **requête enregistrée sous un nom**, qu'on interroge comme une table.

```sql
CREATE VIEW v_ventes AS
SELECT l.id_commande, c.date_commande, c.canal, c.satisfaction,
       cl.id_client, cl.ville,
       ca.nom AS categorie, p.nom AS produit,
       l.quantite, l.prix_unitaire, l.quantite * l.prix_unitaire AS montant_ligne
FROM lignes_commande AS l
JOIN commandes  AS c  ON c.id_commande  = l.id_commande
JOIN clients    AS cl ON cl.id_client   = c.id_client
JOIN produits   AS p  ON p.id_produit   = l.id_produit
JOIN categories AS ca ON ca.id_categorie = p.id_categorie;
```

```sql
SELECT categorie, canal, ROUND(SUM(montant_ligne)) AS chiffre_affaires
FROM v_ventes
GROUP BY categorie, canal
ORDER BY categorie, canal;
```
<!--sortie-->
```text
  categorie     canal  chiffre_affaires
     Bijoux  Boutique            2256.0
     Bijoux Réseaux            1914.0
     Bijoux      Site            2836.0
Cosmétiques  Boutique             878.0
Cosmétiques Réseaux            1099.0
Cosmétiques      Site            1170.0
    Poterie  Boutique            2397.0
    Poterie Réseaux            2143.0
    Poterie      Site            2410.0
    Textile  Boutique            2997.0
    Textile Réseaux            1607.0
    Textile      Site            2390.0
```

Une requête qui exigeait quatre jointures tient maintenant en trois lignes, et la vue peut évoluer (changer de définition) sans que les analystes changent leurs requêtes.

### 5.4.5 Les index : retrouver une ligne sans tout lire

Quand on écrit `WHERE id_client = 2`, comment la base trouve-t-elle les commandes du client ? Sans aide, elle doit **lire toutes les lignes** de la table, une par une (un *balayage complet*, ou *full scan*). Avec 400 lignes, c'est instantané ; avec 100 millions, c'est insupportable. Un **index** est une structure annexe, triée, comparable à l'**index alphabétique à la fin d'un livre** : au lieu de feuilleter tout l'ouvrage pour trouver « Khi-deux », on consulte l'index qui renvoie à la bonne page. Techniquement c'est le plus souvent un **arbre B** (*B-tree*) : on trouve une valeur parmi $N$ en environ $\log_2 N$ comparaisons au lieu de $N$.

Pour $N=500\,000$, c'est $\log_2 N\approx19$ comparaisons contre 500 000 : un facteur **plus de 25 000**. On peut demander à la base **comment elle compte exécuter** une requête, avec `EXPLAIN QUERY PLAN` (c'est le premier outil de l'analyste qui s'occupe de performance) :

```python
def plan(requete):
    for ligne in con.execute("EXPLAIN QUERY PLAN " + requete):
        print("  ", ligne[3])

print("Avant l'index :")
plan("SELECT * FROM commandes WHERE id_client = 2")
con.execute("CREATE INDEX idx_commandes_client ON commandes(id_client)")
print("Après CREATE INDEX :")
plan("SELECT * FROM commandes WHERE id_client = 2")
print("Recherche par la clé primaire (index automatique) :")
plan("SELECT * FROM commandes WHERE id_commande = 2")
print("Filtre sur une colonne non indexée :")
plan("SELECT * FROM commandes WHERE montant > 100")
```
<!--sortie-->
```text
Avant l'index :
   SCAN commandes
Après CREATE INDEX :
   SEARCH commandes USING INDEX idx_commandes_client (id_client=?)
Recherche par la clé primaire (index automatique) :
   SEARCH commandes USING INTEGER PRIMARY KEY (rowid=?)
Filtre sur une colonne non indexée :
   SCAN commandes
```

`SCAN` signifie « lire toute la table » ; `SEARCH ... USING INDEX` signifie « chercher via l'arbre ». La clé primaire est **toujours** indexée automatiquement ; c'est aussi pourquoi les clés étrangères mal indexées sont une cause classique de lenteur. Le filtre sur `montant` reste un `SCAN` : aucun index ne l'aide.

Pour mesurer le gain « pour de vrai », construisons une table de **500 000 lignes** (par une CTE récursive, 5.3.6) et chronométrons la même recherche avant et après un index. Les durées exactes dépendent de votre machine ; nous n'affichons donc que le **facteur de gain**, arrondi à la puissance de dix inférieure, pour que le résultat reste le même d'une exécution à l'autre.

```python
import time, math

con.executescript("""
CREATE TABLE ex_gros (id INTEGER PRIMARY KEY, id_client INTEGER, montant REAL);
WITH RECURSIVE s(i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM s WHERE i < 500000)
INSERT INTO ex_gros SELECT i, (i * 7919) % 50000, ROUND(10 + (i * 31) % 190, 2) FROM s;
""")

def duree(repetitions=20):
    debut = time.perf_counter()
    for k in range(repetitions):
        con.execute("SELECT COUNT(*), SUM(montant) FROM ex_gros WHERE id_client = ?", (123 + k,)).fetchone()
    return (time.perf_counter() - debut) / repetitions

sans_index = duree()
con.execute("CREATE INDEX idx_gros_client ON ex_gros(id_client)")
avec_index = duree()

gain = sans_index / avec_index
print("lignes dans la table :", con.execute("SELECT COUNT(*) FROM ex_gros").fetchone()[0])
print("gain au moins égal à :", 10 ** int(math.log10(gain)), "fois")
con.execute("DROP TABLE ex_gros")
```
<!--sortie-->
```text
lignes dans la table : 500000
gain au moins égal à : 100 fois
```

Chez nous, le gain réel est de l'ordre de plusieurs centaines de fois (le programme n'affiche que la puissance de dix inférieure, pour rester reproductible) : voilà pourquoi les index sont **la** première optimisation. Mais ils ne sont pas gratuits : un index occupe de la place, et il doit être **mis à jour à chaque insertion ou modification**, ce qui ralentit l'écriture. Règle d'usage : indexer les colonnes **souvent utilisées dans un `WHERE` ou un `JOIN`** (surtout les clés étrangères) et ne pas indexer à tout va. Notez enfin que les index peuvent changer le **temps** d'une requête, **jamais son résultat**.

### 5.4.6 Les transactions : tout ou rien

Enregistrer une commande, c'est plusieurs écritures : une ligne dans `commandes`, puis une ligne par article dans `lignes_commande` (et, dans un vrai système, la mise à jour du stock). Que se passe-t-il si le courant saute **entre** deux de ces écritures ? On aurait une commande **sans** articles : une base incohérente. Une **transaction** regroupe plusieurs opérations en un bloc **indivisible** : soit toutes réussissent (`COMMIT`), soit aucune n'a d'effet (`ROLLBACK`). On résume les garanties d'une transaction par l'acronyme **ACID** :

| Lettre | Garantie | Signification |
|---|---|---|
| **A**tomicité | tout ou rien | si une étape échoue, tout est annulé |
| **C**ohérence | les règles tiennent toujours | les contraintes (clés, `CHECK`) sont respectées avant et après |
| **I**solation | pas d'interférence | deux transactions simultanées ne voient pas les états intermédiaires l'une de l'autre |
| **D**urabilité | c'est définitif | une fois validée, la modification survit à une panne |

Voyons l'atomicité en action. On tente d'enregistrer une commande dont la **deuxième** étape échoue (un produit n° 999 qui n'existe pas) :

```python
def nb_commandes():
    return con.execute("SELECT COUNT(*) FROM commandes").fetchone()[0]

print("avant :", nb_commandes(), "commandes")
try:
    with con:                                   # ouvre une transaction ; ROLLBACK automatique si exception
        con.execute("INSERT INTO commandes VALUES (9001, 1, '2025-12-31', 'Site', 80, 3, 5)")
        print("pendant la transaction :", nb_commandes(), "commandes (la nouvelle est visible pour nous)")
        con.execute("INSERT INTO lignes_commande VALUES (9001, 999, 1, 80)")   # produit inexistant : échec
except sqlite3.IntegrityError as erreur:
    print("échec :", erreur)
print("après  :", nb_commandes(), "commandes")
```
<!--sortie-->
```text
avant : 400 commandes
pendant la transaction : 401 commandes (la nouvelle est visible pour nous)
échec : FOREIGN KEY constraint failed
après  : 400 commandes
```

La commande n° 9001, pourtant bien insérée à l'étape 1, a **disparu** : l'échec de l'étape 2 a annulé toute la transaction. Sans transaction, on aurait gardé une commande fantôme sans article. Dans le bloc `with con:`, Python déclenche un `COMMIT` si tout se passe bien, un `ROLLBACK` à la première exception.

> 🧪 **Pourquoi l'isolation compte.** Deux caissiers enregistrent en même temps la vente du dernier exemplaire d'un tajine. Sans isolation, chacun lit « stock = 1 », chacun vend, et le stock tombe à −1. Avec une transaction isolée, la seconde attend (ou échoue) et lit « stock = 0 ». Les SGBD offrent plusieurs **niveaux d'isolation**, du plus laxiste au plus strict, avec un compromis entre sécurité et vitesse ; le détail dépasse ce chapitre, mais retenez que les bases relationnelles gèrent pour vous un problème que les fichiers CSV ignorent complètement.

> ✅ **À retenir**
>
> - Une table qui mélange plusieurs sujets provoque des **anomalies** de mise à jour, d'insertion et de suppression.
> - Une **dépendance fonctionnelle** $X\to Y$ dit que $X$ détermine $Y$. La fermeture $X^+$ permet de trouver les **clés**. Les données peuvent **réfuter** une dépendance, pas la prouver.
> - **1FN** : cases atomiques. **2FN** : rien ne dépend d'une partie de la clé. **3FN** : rien ne dépend d'un non-clé. Formule : « la clé, toute la clé, et rien que la clé ».
> - Une décomposition doit être **sans perte** (théorème de Heath). Normaliser ne répare pas des données déjà contradictoires.
> - **Normalisez pour écrire, dénormalisez pour lire** (OLTP contre OLAP, schéma en étoile, vues).
> - Un **index** accélère les recherches (de $N$ à $\log N$ comparaisons) au prix de l'espace et de l'écriture ; `EXPLAIN QUERY PLAN` montre si la base lit tout (`SCAN`) ou utilise l'index (`SEARCH`).
> - Une **transaction** est un bloc « tout ou rien » (ACID).
