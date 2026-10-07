## 3.5 ➕ Pour aller plus loin : SQL avancé

> 🧭 **Section complémentaire.** Elle prolonge le parcours essentiel par les notions que l'on rencontre dès que l'on travaille sur une vraie base d'entreprise : les sous-requêtes, les index et l'optimisation, les vues, les transactions, les déclencheurs et la sécurité. Rien ici n'est nécessaire pour la suite du volume.

### 3.5.1 Sous-requêtes : une requête dans une requête

Une **sous-requête** est un `SELECT` placé entre parenthèses à l'intérieur d'un autre. On en a déjà croisé (le dénominateur d'un pourcentage en 3.1.7). Il en existe trois usages principaux, selon ce que renvoie la sous-requête.

**Une valeur unique** (sous-requête *scalaire*), utilisée comme une constante dans une comparaison ou un calcul. Quels produits sont plus chers que le prix moyen du catalogue ?

```sql
SELECT COUNT(*) AS nb_produits_au_dessus_de_la_moyenne,
       (SELECT ROUND(AVG(prix_vente), 2) FROM produits) AS prix_moyen
FROM produits
WHERE prix_vente > (SELECT AVG(prix_vente) FROM produits)
```
<!--sortie-->
```text
 nb_produits_au_dessus_de_la_moyenne  prix_moyen
                                  47       35.88
```

La sous-requête `(SELECT AVG(prix_vente) FROM produits)` est évaluée une fois et remplacée par son résultat : **47 produits sur 120** dépassent le prix moyen de 35,88 €. On ne pourrait pas écrire `WHERE prix_vente > AVG(prix_vente)` : un agrégat n'est pas autorisé dans le `WHERE` (l'ordre d'exécution de la section 3.1.7).

**Une liste de valeurs** (sous-requête de liste), avec `IN`. Combien de produits ont donné lieu à au moins un retour de plus de 100 € ?

```sql
SELECT COUNT(*) AS produits_concernes
FROM produits
WHERE id_produit IN (SELECT l.id_produit
                     FROM lignes_commande l JOIN retours r USING (id_ligne)
                     WHERE r.montant_rembourse > 100)
```
<!--sortie-->
```text
 produits_concernes
                 55
```

La sous-requête renvoie la liste des identifiants de produits concernés, et la requête extérieure ne garde que ces produits : **55 produits** (près de la moitié du catalogue) ont déjà fait l'objet d'un remboursement de plus de 100 €, ce qui invite à regarder de près les articles chers.

**Une sous-requête corrélée** est une sous-requête qui **dépend de la ligne courante** de la requête extérieure : elle est « réévaluée » pour chaque ligne. Elle sert aux comparaisons avec le groupe de la ligne. Quel est, dans chaque catégorie, le produit le plus cher ?

```sql
SELECT p.categorie, p.nom_produit, p.prix_vente
FROM produits p
WHERE p.prix_vente = (SELECT MAX(q.prix_vente) FROM produits q WHERE q.categorie = p.categorie)
ORDER BY p.categorie
```
<!--sortie-->
```text
 categorie        nom_produit  prix_vente
 Bien-être    Tisane nordique        68.9
   Cuisine Casserole nordique        57.9
Décoration   Horloge nordique        96.9
    Jardin   Transat nordique       152.9
    Maison       Lampe design       126.9
 Papeterie        Trousse mat        21.9
```

Pour chaque produit `p`, la sous-requête cherche le prix maximal des produits `q` **de la même catégorie** (`q.categorie = p.categorie`), et la condition ne garde que les produits qui atteignent ce maximum. Le résultat compte six lignes, une par catégorie, du transat à 152,90 € pour le jardin à la trousse à 21,90 € pour la papeterie. Cette écriture est correcte, mais un **classement avec fonction fenêtre** (section 3.3.3) fait la même chose plus lisiblement et, sur de gros volumes, bien plus vite : les sous-requêtes corrélées sont des **candidates à la réécriture**.

Enfin, `EXISTS (sous-requête)` ne demande pas **quoi**, seulement **s'il existe** au moins une ligne. C'est la forme préférée pour les tests de présence : elle s'arrête à la première correspondance trouvée. Combien de clients ont déjà fait au moins un retour ?

```sql
SELECT COUNT(*) AS clients_avec_retour
FROM clients cl
WHERE EXISTS (SELECT 1
              FROM commandes c
              JOIN lignes_commande l USING (id_commande)
              JOIN retours r USING (id_ligne)
              WHERE c.id_client = cl.id_client)
```
<!--sortie-->
```text
 clients_avec_retour
                2443
```

**2 443 clients** (sur 6 000) ont déjà renvoyé un article : un client sur quatre environ, une proportion qui pèsera sur la politique de reprise. Le `SELECT 1` de la sous-requête n'a pas d'importance : seule compte l'existence d'une ligne. `NOT EXISTS` en est le contraire, et c'est une anti-jointure (section 3.2.3).

> ⚠️ **Piège : `NOT IN` et les valeurs absentes.** `x NOT IN (liste)` renvoie un résultat **inconnu** dès que la liste contient une valeur absente (`NULL`), et donc **aucune ligne**. La même requête écrite avec `NOT EXISTS` ne souffre pas de ce défaut. Dans le doute, préférez `NOT EXISTS`.

### 3.5.2 Index et plans d'exécution

Quand on demande à la base les commandes d'un client, elle peut lire la table **ligne par ligne** jusqu'à la fin (un **balayage complet**, *full scan*), ou consulter un **index**, comme le fait un lecteur qui cherche un mot dans l'index d'un livre au lieu de relire tout l'ouvrage. Un index est une structure triée, maintenue par la base, qui permet de **retrouver des lignes sans tout lire**. En contrepartie, il occupe de la place et ralentit un peu les écritures, puisqu'il faut le mettre à jour.

La base propose d'**expliquer** le plan qu'elle a choisi : `EXPLAIN QUERY PLAN` en SQLite, `EXPLAIN` ailleurs. Le mot `SCAN` signale une lecture complète, `SEARCH` une recherche par index. Écrivons une petite fonction qui renvoie le plan d'une requête, et interrogeons trois requêtes :

```python
def plan(requete):
    return [ligne[3] for ligne in con.execute("EXPLAIN QUERY PLAN " + requete)]

print(plan("SELECT COUNT(*) FROM commandes WHERE canal = 'Site'"))
print(plan("SELECT COUNT(*) FROM commandes WHERE id_client = 2"))
print(plan("SELECT COUNT(*) FROM commandes WHERE strftime('%Y', date_commande) = '2025'"))
print(plan("SELECT COUNT(*) FROM commandes WHERE date_commande >= '2025-01-01' AND date_commande < '2026-01-01'"))
```
<!--sortie-->
```text
['SCAN commandes']
['SEARCH commandes USING COVERING INDEX idx_cmd_client (id_client=?)']
['SCAN commandes USING COVERING INDEX idx_cmd_date']
['SEARCH commandes USING COVERING INDEX idx_cmd_date (date_commande>? AND date_commande<?)']
```

Les quatre plans sont instructifs. Aucun index n'existe sur `canal` : la première requête fait un **balayage complet** de `commandes`. La deuxième utilise l'index de `id_client` (`SEARCH … USING INDEX`). La troisième et la quatrième portent sur la date, qui est indexée, **mais pas de la même façon** : quand on applique une **fonction** à la colonne (`strftime('%Y', date_commande)`), la base ne peut plus se servir de l'ordre de l'index et doit le **parcourir en entier** (`SCAN`) ; quand on exprime la même condition par un **intervalle** (`>= … AND < …`), elle fait une **recherche** directe (`SEARCH`). Les deux écritures donnent le même résultat, mais **pas le même effort**. Créons maintenant un index sur `canal` pour voir le plan changer :

```python
con.execute("CREATE INDEX idx_cmd_canal ON commandes(canal)")
print(plan("SELECT COUNT(*) FROM commandes WHERE canal = 'Site'"))
```
<!--sortie-->
```text
['SEARCH commandes USING COVERING INDEX idx_cmd_canal (canal=?)']
```

Le plan passe de `SCAN` à `SEARCH … USING COVERING INDEX idx_cmd_canal (canal=?)`. Un index n'est pourtant **pas toujours utile** : ici, la colonne ne contient que trois valeurs, et un index ne rend de grands services que si la condition **isole peu de lignes** (on dit qu'elle est *sélective*). Chercher les commandes d'un seul client sur 6 000 (sélectif) en profite largement ; chercher « toutes celles du site » (42 % de la table) beaucoup moins.

### 3.5.3 Quelques règles d'optimisation

Sur les volumes de la boutique, toutes les requêtes de ce chapitre répondent instantanément. Sur des millions de lignes, quelques règles font la différence :

- **Filtrer tôt** : placer les conditions `WHERE` le plus près possible des tables, pour réduire le nombre de lignes avant les jointures et les agrégats.
- **Ne sélectionner que les colonnes utiles** : éviter `SELECT *`, qui transporte des colonnes inutiles et empêche certains accès rapides par index.
- **Ne pas appliquer de fonction à une colonne indexée** dans un `WHERE` (le plan de 3.5.2) : exprimer la condition sur la colonne brute.
- **Agréger avant de joindre** quand on le peut : c'est plus rapide **et** cela évite la multiplication des lignes (section 3.2.6).
- **Éviter `LIKE '%mot'`** (joker en tête) : aucun index ne sait chercher « se termine par ». `LIKE 'mot%'` est, lui, efficace.
- **Lire le plan** avant d'accuser la base : un `SCAN` sur une grosse table dans une requête lente indique souvent l'index manquant.

> 🧭 **En pratique.** Un analyste ne crée pas, en général, les index d'une base de production : c'est le rôle de l'équipe qui la gère. Savoir **lire un plan** vous permet en revanche de lui faire une demande précise (« la requête X lit toute la table `commandes` ; un index sur `canal, date_commande` l'accélérerait »), ce que les administrateurs de bases apprécient.

### 3.5.4 Vues : donner un nom à une requête

Une **vue** est une requête enregistrée sous un nom : elle se comporte comme une table, mais ne contient aucune donnée propre, elle est recalculée à chaque utilisation. Les vues servent à **partager** une logique (« le chiffre d'affaires, c'est ceci ») pour que tous les rapports calculent la même chose, et à **simplifier** les requêtes. Créons une vue qui recolle les lignes, leurs commandes et leurs produits, c'est-à-dire la jointure que nous avons écrite en 3.2.2 :

```sql
CREATE VIEW v_ventes AS
SELECT l.id_ligne, c.id_commande, c.date_commande, c.canal, c.id_client,
       p.categorie, p.nom_produit, l.quantite, l.montant
FROM lignes_commande l
JOIN commandes c ON c.id_commande = l.id_commande
JOIN produits p ON p.id_produit = l.id_produit
```

Elle s'interroge ensuite comme n'importe quelle table, sans réécrire les jointures :

```sql
SELECT canal, ROUND(SUM(montant), 0) AS ca_2025, COUNT(DISTINCT id_client) AS clients
FROM v_ventes
WHERE date_commande >= '2025-01-01'
GROUP BY canal
ORDER BY ca_2025 DESC
```
<!--sortie-->
```text
   canal  ca_2025  clients
    Site 617715.0     2844
Boutique 560974.0     2731
 Réseaux 146074.0     1139
```

Le **site** réalise 617 715 € de chiffre d'affaires en 2025, devant la **boutique** (560 974 €) et les **réseaux** (146 074 €) ; les trois montants totalisent 1 324 763 €, soit les 1 324 764 € de la section 3.3 à l'arrondi près. Les nombres de clients (2 844, 2 731 et 1 139) **ne s'additionnent pas** : un même client peut acheter par plusieurs canaux, et `COUNT(DISTINCT id_client)` ne compte chacun qu'une fois **par canal**. L'intérêt de la vue est **organisationnel** : si l'on décide demain d'exclure les commandes de test, on corrige **la vue**, et tous les rapports sont corrigés d'un coup. Dans certaines bases (PostgreSQL, Oracle), une **vue matérialisée** stocke le résultat et le rafraîchit à la demande : on gagne en vitesse, on perd en fraîcheur.

> ⚠️ **Piège : une vue fige un grain.** `v_ventes` a le grain « une ligne de commande » : calculer un nombre de commandes dessus exige `COUNT(DISTINCT id_commande)`, comme dans l'exemple (`COUNT(DISTINCT id_client)` pour les clients). Documentez le grain de chaque vue en commentaire.

### 3.5.5 Transactions : tout ou rien

Une **transaction** regroupe plusieurs opérations en un bloc indivisible : soit **toutes** réussissent (`COMMIT`), soit **aucune** n'est appliquée (`ROLLBACK`). C'est la garantie qui évite, par exemple, de débiter un stock sans enregistrer la commande correspondante si la machine s'arrête entre les deux. On résume les propriétés d'une transaction par le sigle **ACID** : atomicité (tout ou rien), cohérence (les règles de la base sont respectées), isolation (deux transactions simultanées ne se voient pas à moitié faites), durabilité (ce qui est validé survit à une panne). Une démonstration sur une petite table de stock :

```python
con.execute("CREATE TABLE demo_stock (id_produit INTEGER PRIMARY KEY, quantite INTEGER)")
con.execute("INSERT INTO demo_stock VALUES (1, 10), (2, 5)")
con.commit()
con.execute("UPDATE demo_stock SET quantite = quantite - 3 WHERE id_produit = 1")
print("pendant la transaction :", con.execute("SELECT quantite FROM demo_stock WHERE id_produit = 1").fetchone()[0])
con.rollback()
print("après annulation       :", con.execute("SELECT quantite FROM demo_stock WHERE id_produit = 1").fetchone()[0])
```
<!--sortie-->
```text
pendant la transaction : 7
après annulation       : 10
```

Pendant la transaction, la quantité est de 7 ; après le `ROLLBACK`, elle est revenue à 10 : l'opération n'a jamais eu lieu. Un analyste, qui **lit** surtout, rencontre rarement les transactions, mais il doit savoir qu'elles existent : un chiffre lu **au milieu** d'un chargement de données peut être incohérent si la base n'isole pas bien les lectures, d'où l'intérêt de lire les données **après** la fin des traitements de nuit.

### 3.5.6 Déclencheurs et procédures stockées

Un **déclencheur** (*trigger*) est un morceau de SQL que la base exécute **automatiquement** quand un événement survient (insertion, modification, suppression). Il sert à tenir un **journal d'audit** : qui a changé quel prix, quand. Exemple minimal : à chaque modification d'un prix, une ligne est ajoutée à un journal.

```python
con.executescript("""
CREATE TABLE demo_prix (id_produit INTEGER PRIMARY KEY, prix REAL);
CREATE TABLE demo_journal (id_produit INTEGER, ancien REAL, nouveau REAL);
CREATE TRIGGER trg_prix AFTER UPDATE OF prix ON demo_prix
BEGIN INSERT INTO demo_journal VALUES (OLD.id_produit, OLD.prix, NEW.prix); END;
INSERT INTO demo_prix VALUES (1, 20.0);
UPDATE demo_prix SET prix = 22.0 WHERE id_produit = 1;""")
print(con.execute("SELECT * FROM demo_journal").fetchall())
```
<!--sortie-->
```text
[(1, 20.0, 22.0)]
```

Le journal contient une ligne : le produit 1, l'ancien prix 20, le nouveau 22. `OLD` et `NEW` désignent les valeurs avant et après la modification. Les déclencheurs ont un coût : ils rendent le comportement de la base **moins visible** (une modification déclenche des effets que l'on ne voit pas dans la requête), et il vaut mieux les réserver à l'audit et aux règles d'intégrité.

Une **procédure stockée** est un programme enregistré **dans** la base, appelé par son nom avec des paramètres. SQLite n'en possède pas ; PostgreSQL, SQL Server, MySQL et Oracle, si, chacun avec son propre langage. Voici, à titre d'illustration, la forme d'une fonction PostgreSQL qui renvoie le chiffre d'affaires d'une année :

```sql noexec
-- PostgreSQL — non exécuté (SQLite n'a pas de procédures stockées)
CREATE FUNCTION ca_annee(annee integer) RETURNS numeric AS $$
  SELECT SUM(l.montant)
  FROM lignes_commande l JOIN commandes c USING (id_commande)
  WHERE EXTRACT(YEAR FROM c.date_commande) = annee;
$$ LANGUAGE sql;
-- appel : SELECT ca_annee(2025);
```

Pour un analyste, l'intérêt est de **réutiliser** une logique validée sans la recopier ; l'inconvénient est qu'elle vit dans la base et non dans votre dépôt de code : veillez à ce qu'elle soit **documentée et versionnée**.

### 3.5.7 Sécurité : l'injection SQL

Quand une application ou un script construit une requête **en collant du texte saisi par un utilisateur**, un malin peut y glisser du SQL. C'est l'**injection SQL**, l'une des failles les plus répandues et les plus coûteuses. Supposons qu'un formulaire demande « quel canal ? » et que le script colle la réponse dans la requête :

```python
saisie = "Site' OR '1'='1"
dangereux = f"SELECT COUNT(*) FROM commandes WHERE canal = '{saisie}'"
prudent = "SELECT COUNT(*) FROM commandes WHERE canal = ?"
print("collé dans le texte :", con.execute(dangereux).fetchone()[0])
print("paramètre           :", con.execute(prudent, (saisie,)).fetchone()[0])
```
<!--sortie-->
```text
collé dans le texte : 36395
paramètre           : 0
```

La saisie piégée transforme la condition en `canal = 'Site' OR '1'='1'`, **toujours vraie** : la requête renvoie **toutes** les commandes (36 395), alors que le canal demandé n'existe pas. Avec un **paramètre** (`?`), la base traite la saisie comme une **valeur** et non comme du SQL, et renvoie 0 ligne, ce qui est la bonne réponse. La règle est absolue : **ne jamais assembler une requête par concaténation avec une donnée extérieure** ; utiliser des requêtes paramétrées. Dans le même esprit, on donne à un analyste un compte en **lecture seule** et limité aux tables dont il a besoin (principe du moindre privilège) : une erreur de frappe ne doit pas pouvoir effacer une table.

```sql hide
DROP VIEW v_ventes;
DROP TABLE demo_stock;
DROP TABLE demo_journal;
DROP TABLE demo_prix;
DROP INDEX idx_cmd_canal
```

> ✅ **À retenir.**
> - Une **sous-requête** renvoie une valeur, une liste, ou sert à tester l'existence (`EXISTS`) ; les sous-requêtes corrélées se réécrivent souvent avec une fonction fenêtre. Préférez `NOT EXISTS` à `NOT IN`.
> - Un **index** accélère les recherches **sélectives** ; une fonction appliquée à une colonne indexée l'empêche de servir. `EXPLAIN` montre le plan : `SCAN` (tout lire) ou `SEARCH` (par index).
> - Une **vue** nomme une requête pour que tous calculent la même chose ; une **transaction** est un bloc tout-ou-rien ; un **déclencheur** réagit automatiquement à un événement.
> - **Ne jamais coller** une saisie dans une requête : utilisez des **paramètres**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.9 (index et plan d'exécution), exercice 3.14.
