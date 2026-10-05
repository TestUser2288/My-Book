## 5.6 Exercices du chapitre 5

> 🧭 Cherchez d'abord seul(e) (sur papier, ou en écrivant la requête dans votre éditeur), vérifiez ensuite en exécutant, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse. Tous les exercices s'appuient sur la base de Dar Jasmin du 5.1 (`donnees/dar_jasmin.db`). **La date « du jour » est le 31 décembre 2025.**

### Énoncés

**Exercice 1 ⭐ (clés et contraintes).** Yasmine veut enregistrer les **avis** des clients sur les produits. Un avis a un numéro, est écrit par **un** client sur **un** produit, à une date, avec une note de 1 à 5 et un commentaire facultatif. Un client ne peut laisser **qu'un seul avis par produit**. (a) Quelle est la clé primaire, quelles sont les clés étrangères ? (b) Écrivez le `CREATE TABLE` avec toutes les contraintes. (c) Vérifiez qu'un avis valide est accepté, et que trois avis invalides (note 6, doublon client/produit, produit inexistant) sont refusés.

**Exercice 2 ⭐ (filtrer).** Combien de commandes de **plus de 100 DT** ont été passées **en boutique** en **décembre 2025** ? Affichez les trois plus grosses.

**Exercice 3 ⭐ (agréger et joindre).** Pour chaque **ville de client**, donnez le nombre de clients ayant commandé, le nombre de commandes, le chiffre d'affaires et le panier moyen, classées par chiffre d'affaires décroissant. Quelle ville a le meilleur panier moyen ? Est-ce aussi celle qui a le plus gros chiffre d'affaires ?

**Exercice 4 ⭐⭐ (`HAVING`, jointure externe).** Quels produits se sont vendus à **moins de 40 unités** sur l'année ? Pour chacun, donnez les unités vendues et le chiffre d'affaires. Faut-il arrêter de vendre tous ces produits ?

**Exercice 5 ⭐⭐ (anti-jointure).** Les clients qui habitent près de la boutique (**Tunis, La Marsa, Ariana**) mais n'y ont **jamais acheté** sont une cible de choix pour une invitation. Listez-les, de deux façons différentes (`NOT EXISTS` et `LEFT JOIN ... IS NULL`), et vérifiez que les deux donnent le même nombre.

**Exercice 6 ⭐⭐ (`NULL`).** (a) Pour chaque ville, quel est le **pourcentage de clients dont le téléphone est renseigné** ? (b) Un stagiaire écrit `WHERE id_parrain != 3` pour compter les clients **qui n'ont pas été parrainés par le client n° 3**. Combien de lignes obtient-il ? Combien devrait-il en obtenir ? Corrigez.

**Exercice 7 ⭐⭐ (dates, et regard statistique).** Quel est le **jour de la semaine** le plus chargé (en nombre de commandes et en chiffre d'affaires) ? Cette différence entre jours est-elle significative, ou du bruit ? (Utilisez un test du khi-deux d'adéquation, chapitre 3.)

**Exercice 8 ⭐⭐⭐ (fenêtre).** Pour **chaque catégorie**, quel est le produit au **plus gros chiffre d'affaires** ?

**Exercice 9 ⭐⭐⭐ (CTE et fenêtres).** (a) Quelle proportion des clients actifs a commandé **au moins deux fois** (taux de réachat) ? (b) Pour ces clients, comparez le montant de leur **première** commande à celui de leur **dernière** : combien dépensent plus à la fin qu'au début ?

**Exercice 10 ⭐⭐⭐ (récursivité).** Pour les trois clients ayant le plus de filleuls (directs ou non), calculez le **nombre de membres** de leur réseau (sans eux-mêmes) et le **chiffre d'affaires cumulé de ces membres**. Qui est l'ambassadeur le plus rentable ?

**Exercice 11 ⭐⭐⭐ (dépendances fonctionnelles).** Dar Jasmin enregistre ses livraisons dans une seule table : `livraisons(id_livraison, id_commande, transporteur, tel_transporteur, ville_livraison, frais)`. Règles de gestion : une livraison concerne une commande, est assurée par un transporteur et part vers une ville ; un transporteur n'a qu'un seul numéro de téléphone ; les **frais ne dépendent que de la ville** de livraison (barème par ville). (a) Écrivez les dépendances fonctionnelles. (b) Déterminez la clé. (c) La table est-elle en 2FN ? en 3FN ? (d) Proposez une décomposition en 3FN, et vérifiez-la avec la fonction `fermeture` du 5.4.2.

### Corrigés

**Corrigé 1.** (a) La clé primaire est `id_avis`. Les clés étrangères sont `id_client` (vers `clients`) et `id_produit` (vers `produits`). La règle « un avis par client et par produit » se traduit par une contrainte `UNIQUE (id_client, id_produit)` : le couple est une **clé candidate** en plus de `id_avis`. (b) et (c) :

```sql
CREATE TABLE ex_avis (
    id_avis      INTEGER PRIMARY KEY,
    id_client    INTEGER NOT NULL REFERENCES clients(id_client),
    id_produit   INTEGER NOT NULL REFERENCES produits(id_produit),
    date_avis    TEXT    NOT NULL,
    note         INTEGER NOT NULL CHECK (note BETWEEN 1 AND 5),
    commentaire  TEXT,
    UNIQUE (id_client, id_produit)
);
INSERT INTO ex_avis VALUES (1, 2, 8, '2025-12-02', 5, 'Magnifique broderie');
```

```python
essais = {
    "note de 6":              "INSERT INTO ex_avis VALUES (2, 3, 8, '2025-12-03', 6, NULL)",
    "doublon client/produit": "INSERT INTO ex_avis VALUES (3, 2, 8, '2025-12-04', 4, NULL)",
    "produit inexistant":     "INSERT INTO ex_avis VALUES (4, 2, 99, '2025-12-05', 4, NULL)",
}
for nom, requete in essais.items():
    try:
        con.execute(requete)
        print(f"{nom:24s} -> accepté (!)")
    except sqlite3.IntegrityError as erreur:
        print(f"{nom:24s} -> refusé : {erreur}")
print("avis enregistrés :", con.execute("SELECT COUNT(*) FROM ex_avis").fetchone()[0])
con.execute("DROP TABLE ex_avis")
```
<!--sortie-->
```text
note de 6                -> refusé : CHECK constraint failed: note BETWEEN 1 AND 5
doublon client/produit   -> refusé : UNIQUE constraint failed: ex_avis.id_client, ex_avis.id_produit
produit inexistant       -> refusé : FOREIGN KEY constraint failed
avis enregistrés : 1
```

L'avis valide est enregistré, les trois autres sont refusés chacun par une contrainte différente (`CHECK`, `UNIQUE`, clé étrangère). Le commentaire est facultatif : c'est la seule colonne sans `NOT NULL`.

**Corrigé 2.** On filtre sur trois conditions (`AND`) ; les dates ISO se comparent comme du texte (5.1.4) : « à partir du 1er décembre » suffit, puisque la base s'arrête au 31.

```sql
SELECT COUNT(*) AS nb_commandes
FROM commandes
WHERE canal = 'Boutique' AND date_commande >= '2025-12-01' AND montant > 100;
```
<!--sortie-->
```text
 nb_commandes
            6
```

```sql
SELECT id_commande, date_commande, montant
FROM commandes
WHERE canal = 'Boutique' AND date_commande >= '2025-12-01' AND montant > 100
ORDER BY montant DESC
LIMIT 3;
```
<!--sortie-->
```text
 id_commande date_commande  montant
         362    2025-12-16    208.8
         376    2025-12-22    147.6
         391    2025-12-29    128.5
```

**Corrigé 3.** Il faut joindre `clients` (la ville) et `commandes` (les montants). Pour compter les *clients distincts*, `COUNT(DISTINCT ...)`.

```sql
SELECT cl.ville,
       COUNT(DISTINCT cl.id_client)  AS clients_actifs,
       COUNT(*)                      AS commandes,
       ROUND(SUM(c.montant))         AS chiffre_affaires,
       ROUND(AVG(c.montant), 2)      AS panier_moyen
FROM clients AS cl
JOIN commandes AS c ON c.id_client = cl.id_client
GROUP BY cl.ville
ORDER BY chiffre_affaires DESC;
```
<!--sortie-->
```text
   ville  clients_actifs  commandes  chiffre_affaires  panier_moyen
  Ariana              13        100            6456.0         64.56
La Marsa               9         80            4619.0         57.73
   Tunis               9         49            3407.0         69.53
  Sousse               7         38            2200.0         57.89
Monastir               6         41            2101.0         51.25
    Sfax               6         34            2043.0         60.09
 Bizerte               8         31            1735.0         55.95
  Nabeul               8         27            1538.0         56.96
```

Ariana est en tête pour le chiffre d'affaires (6 456 DT) mais pas pour le panier : c'est **Tunis** qui a le meilleur panier moyen (69,53 DT), avec un nombre de commandes beaucoup plus faible (49 contre 100). Le chiffre d'affaires est le produit *nombre de commandes × panier moyen* : un fort volume de petits paniers peut battre un faible volume de gros paniers.

**Corrigé 4.** `LEFT JOIN` pour ne pas perdre un éventuel produit **jamais vendu** (il aurait 0 unité, ou `NULL` : voir `COALESCE`). Le filtre sur une valeur agrégée s'écrit avec `HAVING`.

```sql
SELECT p.nom                                          AS produit,
       COALESCE(SUM(l.quantite), 0)                   AS unites,
       ROUND(COALESCE(SUM(l.quantite * l.prix_unitaire), 0)) AS chiffre_affaires
FROM produits AS p
LEFT JOIN lignes_commande AS l ON l.id_produit = p.id_produit
GROUP BY p.id_produit
HAVING COALESCE(SUM(l.quantite), 0) < 40
ORDER BY unites;
```
<!--sortie-->
```text
              produit  unites  chiffre_affaires
Margoum (petit tapis)      13            1593.0
 Vase peint à la main      37            2411.0
      Écharpe en soie      37            2031.0
```

Trois produits. Mais **faible volume ne veut pas dire faible intérêt** : le margoum (petit tapis), à 120 DT l'unité, ne s'est vendu qu'à 13 exemplaires et rapporte pourtant 1 593 DT, plus que bien des produits très vendus. Le vase peint et l'écharpe en soie (37 unités chacun) sont même parmi les produits au plus gros chiffre d'affaires du magasin. Arrêter de les vendre serait une erreur : le bon indicateur dépend de la question (rotation, chiffre d'affaires, marge). Aucun de nos produits n'est resté invendu.

**Corrigé 5.** Version `NOT EXISTS` : on garde les clients de ces villes pour lesquels il n'existe **aucune** commande en boutique. Version `LEFT JOIN` : on joint **seulement** les commandes de boutique (la condition sur le canal va dans le `ON`, pas dans le `WHERE` !), puis on garde ceux qui n'ont aucun partenaire.

```sql
SELECT cl.id_client, cl.prenom, cl.nom, cl.ville
FROM clients AS cl
WHERE cl.ville IN ('Tunis', 'La Marsa', 'Ariana')
  AND NOT EXISTS (SELECT 1 FROM commandes AS c
                  WHERE c.id_client = cl.id_client AND c.canal = 'Boutique')
ORDER BY cl.id_client;
```
<!--sortie-->
```text
 id_client  prenom       nom    ville
        10    Nour     Hamdi    Tunis
        20   Aymen  Bouazizi    Tunis
        28    Emna Ben Salah   Ariana
        32 Oussama   Khelifi La Marsa
        55 Oussama     Mejri La Marsa
        65   Dorra     Mejri    Tunis
        75    Lina     Mejri La Marsa
        78    Ines     Ayari    Tunis
```

```sql
SELECT COUNT(*) AS avec_left_join
FROM clients AS cl
LEFT JOIN commandes AS c ON c.id_client = cl.id_client AND c.canal = 'Boutique'
WHERE cl.ville IN ('Tunis', 'La Marsa', 'Ariana')
  AND c.id_commande IS NULL;
```
<!--sortie-->
```text
 avec_left_join
              8
```

Huit clients, quelle que soit la méthode. Si l'on avait placé `c.canal = 'Boutique'` dans le `WHERE`, la requête aurait éliminé justement les lignes « sans partenaire » (dont `c.canal` est `NULL`), et le résultat aurait été vide : un cas d'école du 5.2.7. Parmi ces huit clients, certains n'ont **jamais** acheté du tout (comme Nour Hamdi, la grande ambassadrice du 5.3.6) : l'invitation à la boutique serait pour eux un premier achat.

**Corrigé 6.** (a) `telephone IS NOT NULL` vaut 1 ou 0 : sa moyenne est la proportion de numéros renseignés.

```sql
SELECT ville,
       COUNT(*)                                      AS clients,
       SUM(telephone IS NOT NULL)                    AS avec_telephone,
       ROUND(100.0 * AVG(telephone IS NOT NULL), 1)  AS pourcentage
FROM clients
GROUP BY ville
ORDER BY pourcentage DESC;
```
<!--sortie-->
```text
   ville  clients  avec_telephone  pourcentage
Monastir        7               7        100.0
 Bizerte       11              11        100.0
  Sousse       11              10         90.9
    Sfax        7               6         85.7
  Nabeul       10               8         80.0
   Tunis       11               8         72.7
  Ariana       13               9         69.2
La Marsa       10               6         60.0
```

Les numéros sont toujours renseignés à Monastir et à Bizerte, mais seulement à 60 % à La Marsa. (b) Le comparatif `!=` renvoie *inconnu* quand `id_parrain` est `NULL` : les 49 clients **sans parrain** sont éliminés, alors qu'ils ne sont évidemment pas parrainés par le client n° 3.

```sql
SELECT (SELECT COUNT(*) FROM clients WHERE id_parrain != 3)                      AS naif,
       (SELECT COUNT(*) FROM clients WHERE id_parrain != 3 OR id_parrain IS NULL) AS corrige,
       (SELECT COUNT(*) FROM clients WHERE id_parrain = 3)                       AS parraines_par_3,
       (SELECT COUNT(*) FROM clients WHERE id_parrain IS NULL)                   AS sans_parrain;
```
<!--sortie-->
```text
 naif  corrige  parraines_par_3  sans_parrain
   30       79                1            49
```

Le stagiaire obtient 30 lignes, alors qu'il en faut 79 (80 clients moins l'unique filleul du client n° 3). Les 49 sans parrain manquent à l'appel ; 30 + 49 = 79. On peut aussi écrire `WHERE id_parrain IS NOT 3` (opérateur de SQLite qui traite proprement `NULL`) ou `COALESCE(id_parrain, 0) != 3`.

**Corrigé 7.** `strftime('%w', ...)` donne 0 pour dimanche... 6 pour samedi ; un `CASE` donne des noms lisibles.

```sql
SELECT CASE strftime('%w', date_commande)
            WHEN '0' THEN 'dimanche' WHEN '1' THEN 'lundi'    WHEN '2' THEN 'mardi'
            WHEN '3' THEN 'mercredi' WHEN '4' THEN 'jeudi'    WHEN '5' THEN 'vendredi'
            ELSE 'samedi' END                  AS jour,
       COUNT(*)                                AS commandes,
       ROUND(SUM(montant))                     AS chiffre_affaires
FROM commandes
GROUP BY strftime('%w', date_commande)
ORDER BY commandes DESC, chiffre_affaires DESC;
```
<!--sortie-->
```text
    jour  commandes  chiffre_affaires
mercredi         66            3722.0
   lundi         63            4071.0
vendredi         61            3794.0
dimanche         56            3350.0
   mardi         54            3203.0
   jeudi         50            3319.0
  samedi         50            2641.0
```

Le mercredi est en tête pour le nombre de commandes (66), le lundi pour le chiffre d'affaires. Mais l'écart est-il autre chose que du bruit ? Test du khi-deux d'adéquation (3.4) de l'hypothèse « les commandes se répartissent **uniformément** sur les sept jours » :

```python
from scipy import stats
effectifs = [r[0] for r in con.execute(
    "SELECT COUNT(*) FROM commandes GROUP BY strftime('%w', date_commande) ORDER BY strftime('%w', date_commande)")]
khi2, p = stats.chisquare(effectifs)
print("effectifs (dimanche ... samedi) :", effectifs)
print(f"khi-deux = {khi2:.2f}, p-valeur = {p:.3f}")
```
<!--sortie-->
```text
effectifs (dimanche ... samedi) : [56, 63, 54, 66, 50, 61, 50]
khi-deux = 4.21, p-valeur = 0.648
```

Avec une p-valeur largement supérieure à 5 %, on **ne peut pas rejeter** l'uniformité : les différences entre jours sont compatibles avec le simple hasard. (C'est d'ailleurs normal : ces dates ont été simulées sans aucun effet de jour de semaine.) Leçon : un classement (« le mercredi est le meilleur jour ») n'est pas une découverte tant qu'on ne l'a pas confronté au hasard.

**Corrigé 8.** On calcule d'abord le chiffre d'affaires par produit (CTE `par_produit`), puis un `RANK` par catégorie, et l'on ne garde que le rang 1 (5.3.2).

```sql
WITH par_produit AS (
    SELECT cat.nom AS categorie, p.nom AS produit,
           ROUND(SUM(l.quantite * l.prix_unitaire)) AS chiffre_affaires
    FROM lignes_commande AS l
    JOIN produits   AS p   ON p.id_produit = l.id_produit
    JOIN categories AS cat ON cat.id_categorie = p.id_categorie
    GROUP BY p.id_produit
)
SELECT categorie, produit, chiffre_affaires
FROM (
    SELECT *, RANK() OVER (PARTITION BY categorie ORDER BY chiffre_affaires DESC) AS rang
    FROM par_produit
)
WHERE rang = 1
ORDER BY categorie;
```
<!--sortie-->
```text
  categorie              produit  chiffre_affaires
     Bijoux      Bague en argent            2638.0
Cosmétiques     Huile de nigelle            1128.0
    Poterie Vase peint à la main            2411.0
    Textile      Écharpe en soie            2031.0
```

La bague en argent domine les bijoux, le vase peint la poterie, l'écharpe en soie le textile et l'huile de nigelle les cosmétiques. (`RANK` laisserait apparaître deux lignes en cas d'égalité parfaite ; ici il n'y en a pas.)

**Corrigé 9.** (a) Un client « actif » est un client qui a au moins une commande. (b) On numérote les commandes de chaque client dans les deux sens (`ROW_NUMBER` croissant et décroissant) : la première a le rang 1 dans l'ordre croissant, la dernière a le rang 1 dans l'ordre décroissant.

```sql
SELECT COUNT(*)                                         AS clients_actifs,
       SUM(n >= 2)                                      AS reachetent,
       ROUND(100.0 * SUM(n >= 2) / COUNT(*), 1)         AS taux_de_reachat_pct
FROM (SELECT id_client, COUNT(*) AS n FROM commandes GROUP BY id_client);
```
<!--sortie-->
```text
 clients_actifs  reachetent  taux_de_reachat_pct
             66          58                 87.9
```

```sql
WITH numerotees AS (
    SELECT id_client, montant,
           ROW_NUMBER() OVER (PARTITION BY id_client ORDER BY date_commande, id_commande)           AS depuis_le_debut,
           ROW_NUMBER() OVER (PARTITION BY id_client ORDER BY date_commande DESC, id_commande DESC) AS depuis_la_fin,
           COUNT(*)     OVER (PARTITION BY id_client)                                               AS nb_commandes
    FROM commandes
),
premiere_et_derniere AS (
    SELECT id_client,
           MAX(CASE WHEN depuis_le_debut = 1 THEN montant END) AS premiere,
           MAX(CASE WHEN depuis_la_fin   = 1 THEN montant END) AS derniere
    FROM numerotees
    WHERE nb_commandes >= 2
    GROUP BY id_client
)
SELECT COUNT(*)                         AS clients,
       SUM(derniere > premiere)         AS depensent_plus_a_la_fin,
       ROUND(AVG(premiere), 2)          AS premiere_moyenne,
       ROUND(AVG(derniere), 2)          AS derniere_moyenne
FROM premiere_et_derniere;
```
<!--sortie-->
```text
 clients  depensent_plus_a_la_fin  premiere_moyenne  derniere_moyenne
      58                       29             61.91              57.4
```

Sur 66 clients actifs, 58 ont recommandé au moins une fois : un **taux de réachat de 87,9 %**, excellent. Parmi eux, la moitié exactement (29 sur 58) dépense davantage lors de la dernière commande que lors de la première, et les montants moyens sont proches (61,91 DT contre 57,40 DT) : **pas de tendance** à dépenser plus avec le temps dans ces données (là encore, un test de comparaison de moyennes au sens du chapitre 3 serait à faire avant de conclure à autre chose que du hasard).

**Corrigé 10.** Une CTE récursive parcourt les réseaux, en gardant la **racine** de chacun comme au 5.3.6. On retire la racine elle-même (profondeur 0) du décompte et du chiffre d'affaires.

```sql
WITH RECURSIVE reseau(id_client, racine, profondeur) AS (
    SELECT id_client, id_client, 0 FROM clients WHERE id_parrain IS NULL
    UNION ALL
    SELECT c.id_client, r.racine, r.profondeur + 1
    FROM clients AS c JOIN reseau AS r ON c.id_parrain = r.id_client
),
ca_client AS (
    SELECT id_client, SUM(montant) AS ca FROM commandes GROUP BY id_client
)
SELECT r.racine,
       cl.prenom || ' ' || cl.nom        AS ambassadeur,
       COUNT(*)                          AS membres,
       ROUND(COALESCE(SUM(ca.ca), 0), 2) AS ca_des_membres
FROM reseau AS r
JOIN clients AS cl ON cl.id_client = r.racine
LEFT JOIN ca_client AS ca ON ca.id_client = r.id_client
WHERE r.profondeur > 0
GROUP BY r.racine
ORDER BY membres DESC, ca_des_membres DESC
LIMIT 3;
```
<!--sortie-->
```text
 racine    ambassadeur  membres  ca_des_membres
     10     Nour Hamdi        5           808.2
      7 Zied Ben Salah        4          2048.7
      1 Yassine Lahmar        4          1117.0
```

Le `LEFT JOIN` est indispensable : un membre qui n'a jamais commandé n'a pas de ligne dans `ca_client` ; avec un `JOIN` ordinaire, il disparaîtrait du décompte des membres. Les trois plus gros réseaux sont ceux de Nour Hamdi (n° 10, 5 membres), de Zied Ben Salah (n° 7, 4 membres) et de Yassine Lahmar (n° 1, 4 membres ; il est classé après Zied car on départage les ex æquo par le chiffre d'affaires). L'ambassadeur le plus **rentable** est **Zied Ben Salah** : ses quatre filleuls ont dépensé 2 048,70 DT, contre 1 117,00 DT pour ceux de Yassine Lahmar et 808,20 DT seulement pour les cinq membres du plus grand réseau, celui de Nour Hamdi. Le réseau le plus **grand** n'est donc pas le plus **rentable** : il faut mesurer ce qu'on veut optimiser.

**Corrigé 11.** (a) Dépendances :
- `id_livraison` $\to$ `id_commande`, `transporteur`, `ville_livraison` (une livraison fixe sa commande, son transporteur et sa destination) ;
- `transporteur` $\to$ `tel_transporteur` ;
- `ville_livraison` $\to$ `frais`.

(b) La fermeture de `id_livraison` contient tous les attributs (elle atteint `tel_transporteur` par `transporteur` et `frais` par `ville_livraison`), et c'est un attribut seul : c'est donc **la clé**. (c) **2FN** : oui, trivialement, car la clé est formée d'**un seul** attribut (il ne peut pas y avoir de dépendance partielle). **3FN** : **non**, car deux dépendances sont **transitives** : `id_livraison` $\to$ `transporteur` $\to$ `tel_transporteur`, et `id_livraison` $\to$ `ville_livraison` $\to$ `frais`. Conséquence concrète : le téléphone d'un transporteur est répété sur toutes ses livraisons, et le barème d'une ville sur chaque livraison vers elle (anomalies du 5.4.1). (d) Décomposition : `livraisons(id_livraison, id_commande, transporteur, ville_livraison)`, `transporteurs(transporteur, tel_transporteur)`, `tarifs(ville_livraison, frais)`. Vérification par le calcul :

```python
deps = [
    (["id_livraison"],     ["id_commande", "transporteur", "ville_livraison"]),
    (["transporteur"],     ["tel_transporteur"]),
    (["ville_livraison"],  ["frais"]),
]
tous = {"id_livraison", "id_commande", "transporteur", "tel_transporteur", "ville_livraison", "frais"}
print("fermeture de {id_livraison} :", sorted(fermeture(["id_livraison"], deps)))
print("c'est une clé :", fermeture(["id_livraison"], deps) == tous)

# Dans chaque table de la décomposition, la clé détermine bien toutes les colonnes de la table.
decomposition = {
    "livraisons":    ({"id_livraison", "id_commande", "transporteur", "ville_livraison"}, {"id_livraison"}),
    "transporteurs": ({"transporteur", "tel_transporteur"}, {"transporteur"}),
    "tarifs":        ({"ville_livraison", "frais"}, {"ville_livraison"}),
}
for nom, (attributs, cle) in decomposition.items():
    print(f"{nom:14s} clé {sorted(cle)} détermine toute la table : {fermeture(cle, deps) >= attributs}")
```
<!--sortie-->
```text
fermeture de {id_livraison} : ['frais', 'id_commande', 'id_livraison', 'tel_transporteur', 'transporteur', 'ville_livraison']
c'est une clé : True
livraisons     clé ['id_livraison'] détermine toute la table : True
transporteurs  clé ['transporteur'] détermine toute la table : True
tarifs         clé ['ville_livraison'] détermine toute la table : True
```

Dans chaque table, la clé détermine toutes les autres colonnes, et les deux dépendances transitives ont été isolées chacune dans sa propre table (aucune dépendance entre colonnes non-clés ne subsiste) : le schéma est en 3FN, et même en BCNF puisque le seul déterminant de chaque table est sa clé. La décomposition est **sans perte** (théorème de Heath, 5.4.3) : chaque découpage sépare un attribut déterminant (`transporteur`, `ville_livraison`) de ce qu'il détermine, et le garde dans la table de gauche comme clé étrangère.

---

## Bilan du chapitre 5

Vous savez maintenant :

- **expliquer pourquoi** une base relationnelle vaut mieux qu'un fichier (redondance, incohérence, contraintes, volume, accès simultanés), et lire un schéma : tables, **clés primaires et étrangères**, relations 1–N et N–N ;
- **écrire des requêtes SQL** complètes : `SELECT`, `WHERE`, `ORDER BY`, `GROUP BY`/`HAVING`, **jointures** (`INNER`, `LEFT`, auto-jointure), sous-requêtes, opérations ensemblistes ;
- **éviter les pièges classiques** : priorité de `AND`/`OR`, `NULL` (trois valeurs de vérité, `NOT IN`), dates et `date('now')`, `WHERE` contre `HAVING` ;
- **calculer sans écraser les lignes** grâce aux **fonctions fenêtres** (classements, cumuls, moyennes mobiles, `LAG`/`LEAD`), structurer une requête en **CTE**, et parcourir des hiérarchies par **récursion** ;
- **concevoir un schéma** : dépendances fonctionnelles, 1FN/2FN/3FN, décomposition sans perte, et savoir quand dénormaliser (OLTP contre OLAP, vues, schéma en étoile) ;
- comprendre ce que font les **index** (`EXPLAIN QUERY PLAN`) et les **transactions** (ACID) ;
- (en option) situer les bases **NoSQL** (documents, clé–valeur) et le théorème **CAP**.

Le chapitre 6 clôt la partie « boîte à outils » avec les habitudes de travail du professionnel : **Git** pour garder l'historique de vos analyses (y compris vos requêtes SQL, qui sont du code comme les autres), les **notebooks Jupyter** pour mélanger code, résultats et explications, et la **ligne de commande** pour tout automatiser. Ensuite, le projet de clôture du volume réunira tout ce que vous avez appris, des mathématiques au SQL, dans une seule étude de bout en bout.
