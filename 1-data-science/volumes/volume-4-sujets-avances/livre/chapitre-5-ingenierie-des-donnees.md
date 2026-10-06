# Chapitre 5 : Ingénierie des données

> « Un modèle sophistiqué sur des données douteuses est une erreur très bien calculée. »

Les chapitres précédents ont supposé que **la table d'entrée existait**, propre, typée, sans doublons, avec les bonnes colonnes. Dans une entreprise, ce n'est presque jamais le cas. Les données naissent dans des systèmes différents (la caisse du magasin, le site web, un tableur du service client, le fichier d'un fournisseur), chacun avec **ses formats, ses clés, ses habitudes et ses erreurs**. Quelqu'un doit les faire arriver, les contrôler, les réconcilier et les livrer, **tous les jours**, sans les abîmer. Ce travail s'appelle l'**ingénierie des données** (*data engineering*), et c'est lui qui décide en grande partie si les modèles du reste de ce volume serviront ou non.

La gérante de la boutique vous confie quatre fichiers « exportés tels quels » de ses outils : une liste de commandes, le carnet de clients de son logiciel de relation client (le CRM), le catalogue de ses produits, et la liste d'un fournisseur. Ce chapitre raconte, pas à pas, comment les transformer en **tables fiables**.

## Le chemin de ce chapitre

- **5.1 Conception d'ETL** : extraire, transformer, charger ; les couches (brut, nettoyé, mart) ; rejeter proprement ; **idempotence** et chargements incrémentaux ; ETL en pandas et ELT en SQL avec DuckDB.
- **5.2 Qualité des données** : les dimensions de la qualité, des règles écrites comme de petites fonctions, un score, des seuils, et le **coût concret** d'une donnée sale sur un chiffre d'affaires.
- **5.3 Réconciliation** : retrouver que « Bol  coton (lot) » et « Bol en coton » sont le même produit, et que deux lignes du CRM sont la même personne ; comparer des chaînes, **bloquer** pour passer à l'échelle, mesurer précision et rappel.
- ➕ **5.4 Gouvernance, lignage et protection des données** : qui est responsable de quoi, d'où vient chaque chiffre, et comment protéger les données personnelles (pseudonymisation).
- ➕ **5.5 Collecte par scraping et par API** : pages web et API paginées, limitation de débit, politesse et légalité, sur un **site de démonstration local**.

> 🧭 **Données de ce chapitre.** Quatre exports volontairement **sales**, dans `donnees/sources/` : `commandes_export.csv`, `clients_crm.csv`, `produits_catalogue.csv` et `produits_fournisseur.csv`. Ils sont **simulés**, avec une vérité connue (`verite_produits.csv`, `verite_clients.csv`) qui permet de **mesurer** la qualité d'une réconciliation, ce qui est impossible sur des données réelles où l'on ne connaît jamais la vérité. Aucun code de ce chapitre n'ouvre de connexion extérieure : les exemples de collecte interrogent un petit site fabriqué **sur votre machine**.


Les quatre fichiers comptent respectivement **19 700**, **5 000**, **48** et **40** lignes. Les écarts sont déjà un indice : le catalogue décrit 48 produits, le fournisseur en livre 40 ; le CRM contient 5 000 lignes, mais combien de personnes ? C'est ce que le chapitre va établir.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.9 et exercices 5.1 à 5.12, section par section.


## 5.1 Conception d'ETL

Un **ETL** (*Extract, Transform, Load*) est le processus qui **extrait** des données de leurs sources, les **transforme** (les typer, les nettoyer, les rapprocher) et les **charge** dans un endroit où l'on pourra travailler. Cette section montre comment on le **conçoit** pour qu'il soit lisible, testable et, surtout, **rejouable sans danger**. Le fil : transformer les 19 700 lignes de commandes brutes en une table propre, en gardant la trace de tout ce qu'on a écarté.

### 5.1.1 Le vocabulaire : couches, ETL et ELT

Un pipeline sérieux ne transforme pas d'un seul coup : il range les données dans des **couches** successives, chacune avec un contrat clair.

| Couche | Contenu | Règle d'or |
|---|---|---|
| **Sources** | les systèmes d'origine (caisse, CRM, fichier fournisseur) | on n'y touche pas : on les lit |
| **Staging** (zone d'atterrissage) | copie **brute** de ce qui a été extrait, telle quelle, avec des métadonnées de chargement | immuable : on ne corrige jamais le brut, on garde de quoi tout rejouer |
| **Nettoyé** (*cleaned*) | données typées, dédoublonnées, validées | une ligne = une commande valable |
| **Rebut** (*rejects*, ou *dead letter*) | lignes refusées, avec le **motif** du refus | rien ne disparaît en silence |
| **Marts** | tables prêtes à l'emploi (chiffre d'affaires par mois, par catégorie) | construites uniquement à partir du nettoyé |

<!--sortie-->

Deux philosophies s'opposent sur **où** faire les transformations.

- **ETL** : on transforme **avant** de charger, dans un moteur extérieur (un script Python, par exemple), et l'on ne charge que du propre.
- **ELT** : on charge d'abord le **brut** dans l'entrepôt de données, puis on transforme **à l'intérieur**, en SQL. C'est devenu la norme avec les entrepôts puissants : on garde le brut, et chaque transformation est une requête que l'on peut relire, versionner et rejouer. Nous ferons les deux sur les mêmes données en 5.1.6.

<!--sortie-->

![Les couches d'un pipeline de données : les sources alimentent un staging brut, qui est typé, dédoublonné et validé pour donner la couche nettoyée ; les lignes refusées vont dans une table de rebut avec leur motif ; les marts sont construits à partir du seul nettoyé.](figures/ch05-couches-etl.png)

### 5.1.2 Extraire : lire sans rien déformer

La première étape paraît anodine et rate souvent. Un `read_csv` « intelligent » **devine** les types : il transformerait `"03/12/2025"` en texte, `"12,38"` en texte aussi, une quantité vide en nombre à virgule, et un identifiant `"007"` en `7`. Chaque devinette est une **décision silencieuse**. La règle est de tout lire **comme du texte** et de laisser l'étape suivante décider, explicitement.

```python
lu = pd.read_csv("donnees/sources/commandes_export.csv", dtype=str, na_values=[""], keep_default_na=False)
lu["_charge_le"] = "2025-12-31"            # métadonnée de chargement : quand, d'où, quelle version
lu["_fichier"] = "commandes_export.csv"
```

Les deux colonnes ajoutées, qui commencent par `_`, sont des **métadonnées techniques**. Elles ne décrivent pas la commande mais **l'histoire de la ligne** : sans elles, impossible de savoir plus tard de quel lot provient une valeur douteuse.

### 5.1.3 Transformer : typer, normaliser, dédoublonner, valider

Les commandes brutes cachent trois sortes de défauts, qui se traitent **dans cet ordre**.

**1. Des formats mélangés.** Les dates arrivent sous trois formes : `2025-04-26` (60 % des lignes), `03/12/2025` (30 %, jour avant mois) et `12-24-2025` (10 %, mois avant jour, à l'américaine). Le piège : `03/12/2025` et `12-03-2025` peuvent désigner **le même 3 décembre ou deux jours différents** selon la convention. Ici, le **séparateur** lève l'ambiguïté (barre oblique pour le jour d'abord, tiret avec l'année en dernier pour le mois d'abord), à condition de l'avoir **vérifié sur les données** et de le consigner. Les prix, eux, utilisent tantôt le point, tantôt la virgule décimale (30 % des lignes).

```python
def parser_date(s):
    s = str(s).strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        return pd.to_datetime(s, format="%Y-%m-%d")
    if re.fullmatch(r"\d{2}/\d{2}/\d{4}", s):
        return pd.to_datetime(s, format="%d/%m/%Y")
    if re.fullmatch(r"\d{2}-\d{2}-\d{4}", s):
        return pd.to_datetime(s, format="%m-%d-%Y")
    return pd.NaT                      # un format inconnu devient visible, il n'est pas deviné
```

**2. Des doublons.** La table contient 1 700 lignes en trop : une commande revient jusqu'à deux fois avec le même numéro. Un `drop_duplicates()` appliqué **avant** de normaliser n'en retire que **1 524**, car 176 copies diffèrent par le **format du prix** (`12.38` d'un côté, `12,38` de l'autre). Après typage, les copies deviennent identiques et les 1 700 sont éliminées. La leçon est générale : **on normalise avant de comparer**, sinon on laisse passer les quasi-doublons.

**3. Des valeurs invalides.** Une fois typées et dédoublonnées, il reste 18 000 commandes. Parmi elles, 782 (4,3 %) violent une règle de gestion : 334 portent sur un client absent du CRM, 245 n'ont pas de quantité, 203 ont une quantité négative ou nulle. On ne les **corrige pas** (comment deviner une quantité ?) et on ne les **supprime pas** non plus : on les range dans le rebut, avec leur motif.

> 💡 **L'équation de conservation.** Un bon pipeline s'auto-contrôle par une égalité comptable : $19\,700 - 1\,700 \text{ (doublons)} - 782 \text{ (rejets)} = 17\,218 \text{ (propres)}$. Si cette égalité ne tient pas à la ligne près, des lignes se sont perdues ou dupliquées en route. Écrire ce contrôle en test automatique est l'une des meilleures habitudes que l'on puisse prendre.

### 5.1.4 Rejeter proprement : la table de rebut

Écarter une ligne est une décision qui doit rester **traçable**. La table de rebut (*dead letter table*) garde la ligne d'origine, le **motif** et la date, ce qui permet trois choses : **corriger à la source** (le magasin saisit mal les quantités ?), **rejouer** les lignes corrigées au prochain passage, et **mesurer** la dérive (le taux de rejet monte-t-il ?).

```text
                            lignes
motif                             
client inconnu                 334
quantité manquante             245
quantité négative ou nulle     203
```
<!--sortie-->

Un seuil d'alerte sur le **taux de rejet** protège le pipeline : s'il dépasse, par exemple, 10 %, on **arrête le chargement** et l'on prévient un humain, plutôt que de publier un chiffre d'affaires bâti sur un échantillon amputé. Ici, 4,3 % est dans la norme.

### 5.1.5 Tester les transformations

Une transformation de données est du code, et le code se teste. Les tests les plus utiles sont des **cas à la main**, que l'on sait justes sans exécuter quoi que ce soit.

```python
def test_parser_date():
    assert parser_date("2025-12-03") == pd.Timestamp("2025-12-03")
    assert parser_date("03/12/2025") == pd.Timestamp("2025-12-03")     # jour d'abord
    assert parser_date("12-03-2025") == pd.Timestamp("2025-12-03")     # mois d'abord
    assert pd.isna(parser_date("3 décembre"))                          # inconnu : visible, pas deviné

test_parser_date()
```

Deux autres tests valent presque tous les autres : **l'équation de conservation** ci-dessus, et l'**idempotence** (rejouer la transformation sur sa propre sortie ne doit rien changer). Nous y revenons en 5.1.7.

### 5.1.6 ELT : la même chose en SQL avec DuckDB

Faisons maintenant la même transformation **dans la base**, en SQL. DuckDB est un moteur de requêtes analytiques qui tient dans une bibliothèque Python : il lit un tableau pandas ou un fichier et exécute du SQL dessus.


```python
con.execute("""
CREATE TABLE propres_sql AS
WITH typees AS (
  SELECT CAST(id_commande AS INT) AS id_commande, CAST(id_client AS INT) AS id_client, id_produit,
         CASE WHEN date LIKE '%/%' THEN strptime(date, '%d/%m/%Y')
              WHEN regexp_matches(date, '^[0-9]{2}-[0-9]{2}-[0-9]{4}$') THEN strptime(date, '%m-%d-%Y')
              ELSE strptime(date, '%Y-%m-%d') END AS date,
         try_cast(quantite AS DOUBLE) AS quantite,
         try_cast(replace(prix_unitaire, ',', '.') AS DOUBLE) AS prix_unitaire
  FROM staging_commandes),
uniques AS (SELECT DISTINCT ON (id_commande) * FROM typees)
SELECT *, round(quantite * prix_unitaire, 2) AS montant FROM uniques
WHERE quantite >= 1 AND prix_unitaire > 0 AND id_client IN (SELECT id_crm FROM crm) AND id_produit IN (SELECT id_produit FROM catalogue)""")
```

<!--sortie-->

Le résultat est **identique** à celui du script pandas : 17 218 commandes propres et 893 243,24 € de chiffre d'affaires, ligne à ligne. Ce n'est pas un hasard, c'est un **test** : lorsqu'on porte une transformation d'un outil à un autre, on vérifie l'égalité des résultats. Le gain de l'ELT est ailleurs : la requête SQL **est** la documentation de la règle, un analyste peut la lire sans connaître Python, et elle s'exécute là où se trouvent les données, sans les déplacer.

À partir du nettoyé, un **mart** n'est qu'une agrégation :

```text
           commandes         ca
categorie                      
A               4278  222190.42
B               4265  218570.96
C               4402  231831.04
D               4273  220650.82
NUM ca_total_mart 893243.24
```
<!--sortie-->

### 5.1.7 Idempotence et chargements incrémentaux

Un pipeline s'exécute **toutes les nuits**, et il échouera un jour à mi-chemin. Que se passe-t-il quand on le **relance** ? Une propriété décide de tout : l'**idempotence**. Une opération est idempotente si l'exécuter deux fois (ou dix) donne **le même résultat qu'une seule**.

Prenons un chargement par **lots** : janvier à avril, mai à août, septembre à décembre. Le chargement naïf *ajoute* chaque lot (`INSERT`). Si le lot 2 est rejoué après un incident, ses lignes sont ajoutées **deux fois**. La solution est de déclarer la **clé** de la table et d'écrire les lignes avec une **fusion** (*upsert* : *update or insert*) : si la clé existe, on met à jour, sinon on insère.

```python
con.execute("CREATE TABLE cible (id_commande INT PRIMARY KEY, date TIMESTAMP, id_client INT, id_produit VARCHAR, quantite DOUBLE, prix_unitaire DOUBLE, montant DOUBLE)")
con.execute("""INSERT INTO cible SELECT * FROM lot
               ON CONFLICT (id_commande) DO UPDATE SET quantite = excluded.quantite,
               prix_unitaire = excluded.prix_unitaire, montant = excluded.montant""")
```

<!--sortie-->

Les chiffres parlent. Après chaque lot, la table passe de 5 611 à 11 504, puis à **17 218** lignes. Rejouer le lot 2, puis le lot 3, **ne change rien** : 17 218. Avec le chargement naïf, le même scénario aboutit à **23 111** lignes, soit 5 893 de trop (le lot rejoué). Enfin, quand le lot 2 revient avec 50 prix corrigés, la fusion **met à jour** ces 50 lignes sans en ajouter : le chiffre d'affaires varie de +197,82 €, exactement ce que l'on attendait.

> ⚠️ **Le piège du « filigrane » sur la date métier.** Pour ne pas relire toute la source à chaque nuit, on retient souvent un *filigrane* (*watermark*) : « charger seulement ce qui est postérieur à la dernière date chargée ». Mais une commande **peut arriver en retard** : saisie le 3 janvier, elle n'atteint l'entrepôt qu'en décembre. Son `date` (janvier) est antérieure au filigrane, donc **jamais relue**.

<!--sortie-->

Dans notre simulation, 40 commandes d'avril arrivent dans un quatrième lot : **aucune** n'a une date supérieure au filigrane du 31 décembre, les 40 seraient donc perdues. Deux remèdes : filtrer sur un **identifiant de lot** ou une **date technique de chargement** (qui, elle, croît toujours), plutôt que sur la date métier ; ou relire une **fenêtre glissante** assez large et compter sur l'upsert pour éviter les doublons.

### 5.1.8 Schémas qui évoluent, journalisation, batch ou flux

**Les schémas changent.** Un jour, la caisse ajoute une colonne `canal` à ses exports. Un pipeline rigide casse ; un pipeline **tolérant** lit les colonnes par **nom** et traite l'absence ou l'apparition d'une colonne comme un cas prévu. DuckDB sait fusionner par nom plusieurs fichiers dont les colonnes diffèrent :

<!--sortie-->

Les lignes de l'ancien lot reçoivent la valeur **manquante** pour la nouvelle colonne, au lieu de faire échouer le chargement. Il reste à **décider** quoi faire de ces manquants, et à prévenir le producteur de la donnée : c'est l'objet des **contrats de données** (5.2.7).

**Journaliser.** Chaque étape consigne ce qu'elle a lu, ce qu'elle a produit et combien de lignes, dans un **journal de lignage**. Il sert à diagnostiquer, à vérifier l'équation de conservation, et à répondre plus tard à « d'où vient ce chiffre ? » (5.4.2).

**Batch ou flux.** Notre pipeline travaille par **lots** (*batch*) : toutes les nuits, un paquet de lignes. D'autres cas exigent de traiter chaque événement dès son arrivée (détection de fraude, alertes) : c'est le **traitement en flux** (*streaming*), présenté en ➕ 3.3. Les principes de ce chapitre (idempotence, rejet traçable, schéma tolérant) s'y appliquent tout autant, avec en plus la difficulté de l'ordre et du retard des événements.

> ✅ **À retenir (conception d'ETL).**
> - Une architecture en **couches** (brut immuable → nettoyé → marts) et une **table de rebut** : rien ne disparaît en silence.
> - **Lire sans deviner** (`dtype=str`), **normaliser avant de comparer**, **typer explicitement**.
> - L'**équation de conservation** (entrées − doublons − rejets = sorties) est un test que tout pipeline doit passer.
> - Un pipeline **idempotent** (clé + fusion) se relance sans danger ; l'ajout naïf duplique.
> - Le **filigrane sur la date métier** perd les données tardives : préférer un identifiant de lot ou une fenêtre glissante.
> - Un même traitement s'écrit en pandas (ETL) ou en SQL (ELT) : on vérifie **l'égalité des résultats**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.3 (ETL pas à pas, ELT en SQL, chargement incrémental) et exercices 5.1 à 5.3.


## 5.2 Qualité des données

Au 5.1, le pipeline a **écarté** 782 lignes et 1 700 doublons. C'était la bonne décision, mais elle pose une question que l'on évite trop souvent : **à quel point** les données d'origine étaient-elles mauvaises, **où**, et **cela empire-t-il** ? Un pipeline qui nettoie sans mesurer est un pansement ; un pipeline qui **mesure** la qualité est un instrument de pilotage.

### 5.2.1 Le coût concret d'une donnée sale

Commençons par ce qui parle à la gérante : de l'argent. Calculons le chiffre d'affaires de 2025 **sans aucun contrôle** (on multiplie quantité et prix de chaque ligne, puis on additionne), puis retirons les défauts un par un.

```text
                            étape    CA (€)  écart (€)
       Calcul naïf, sans contrôle 987829.85       0.00
       Après retrait des doublons 903094.46  -84735.39
Après retrait des lignes rejetées 893243.24   -9851.22
NUM surestimation du CA par le calcul naïf (€, %) (94586.61, 10.6)
```

Le calcul naïf **surestime** le chiffre d'affaires de 94 586,61 €, soit 10,6 %. Les doublons pèsent le plus lourd (84 735,39 €) : une commande exportée deux fois est comptée deux fois. Les lignes rejetées (9 851,22 €) agissent dans des sens variés : un client inconnu fait *monter* le total (la vente existe, mais on ne sait pas à qui), une quantité négative le fait *descendre* (c'est probablement un retour, mal saisi). **Aucune erreur ne se compense de façon fiable.** C'est pourquoi la qualité se traite par des règles explicites et non par un « ça doit à peu près s'équilibrer ».

### 5.2.2 Les dimensions de la qualité

« Qualité » est un mot vague. Les praticiens le décomposent en **dimensions**, chacune répondant à une question précise et mesurable par un taux.

| Dimension | Question posée | Exemple dans nos commandes | Mesure |
|---|---|---|---|
| **Complétude** | Les valeurs attendues sont-elles là ? | Quantité vide | part de valeurs manquantes |
| **Validité** | La valeur respecte-t-elle le format et le domaine ? | Quantité ≥ 1, prix entre 0 et 1 000 | part de valeurs hors domaine |
| **Unicité** | Une réalité est-elle représentée une seule fois ? | Même `id_commande` deux fois | part de clés répétées |
| **Cohérence** | Les sources se contredisent-elles ? | Client absent du CRM | part de références orphelines |
| **Exactitude** | La valeur est-elle conforme à la réalité ? | Prix d'achat supérieur au prix de vente | écart à une référence de confiance |
| **Fraîcheur** | La donnée est-elle assez récente ? | Dernière commande vieille de 9 jours | âge de la dernière mise à jour |

> 💡 **Exactitude, la dimension difficile.** Les cinq autres se mesurent avec les données elles-mêmes. L'exactitude demande une **référence extérieure** : on ne sait pas qu'un prix est faux sans connaître le bon. Elle se contrôle donc par des **recoupements** (le prix d'achat doit être inférieur au prix de vente), des **plausibilités statistiques** (5.2.6) ou des **échantillons vérifiés à la main**.

### 5.2.3 Des règles écrites comme de petites fonctions

Une règle de qualité est une fonction qui renvoie, pour chaque ligne, **vrai si la ligne la viole**. Quelques fonctions génériques suffisent à écrire toutes nos règles.

```python
def vide(d, col):                 return d[col].isna()
def hors_domaine(d, col, lo, hi): return d[col].notna() & ~d[col].between(lo, hi)
def repete(d, col):               return d.duplicated(col)
def orpheline(d, col, ref):       return ~d[col].isin(ref)

regles = [("complétude", "quantité renseignée", "bloquant", vide(typ, "quantite")),
          ("validité", "quantité ≥ 1", "bloquant", hors_domaine(typ, "quantite", 1, 1e6)),
          ("unicité", "id_commande unique", "bloquant", repete(typ, "id_commande")),
          ("cohérence", "client connu du CRM", "bloquant", orpheline(typ, "id_client", clients_connus))]
```

Le niveau de **gravité** décide de la suite : une règle *bloquante* écarte la ligne (elle va au rebut), une règle d'*avertissement* la laisse passer mais la signale. Le tableau complet des neuf règles du pipeline, avec leur taux de violation, donne la photographie initiale :

```text
 dimension                      règle  gravité  violations  taux (%)
 cohérence        client connu du CRM bloquant         359      1.82
 cohérence produit connu du catalogue bloquant           0      0.00
complétude            date renseignée bloquant           0      0.00
complétude             prix renseigné bloquant           0      0.00
complétude        quantité renseignée bloquant         286      1.45
   unicité         id_commande unique bloquant        1700      8.63
  validité             date dans 2025 bloquant           0      0.00
  validité      prix dans ]0 ; 1 000] bloquant           0      0.00
  validité               quantité ≥ 1 bloquant         226      1.15
NUM lignes avec au moins une violation (nombre, %) (2482, 12.6)
```

Trois constats. D'abord, **quatre règles seulement sont violées** : les cinq autres, à zéro, sont des garanties utiles (le système source ne produit ni prix négatif, ni date hors année, ni produit fantôme). Ensuite, l'**unicité** domine : 8,6 % de lignes sont des répétitions. Enfin, le total des lignes touchées est inférieur à la somme des taux, car **une ligne peut violer plusieurs règles** à la fois (un doublon avec une quantité vide, par exemple).

### 5.2.4 Un score, des seuils, une décision

Pour décider quoi faire, il faut **résumer**. Le **score de qualité** le plus courant est la part de lignes qui ne violent **aucune** règle bloquante ; on le calcule aussi **par dimension** pour savoir où agir.

```text
SCORE GLOBAL    87.4
cohérence       98.2
complétude      98.5
unicité         91.4
validité        98.9
```

Le score global est un **tableau de bord** à lui seul, mais il ne vaut que **comparé** à des seuils décidés avec l'équipe métier. Une grille simple suffit :

| Score | Décision |
|---|---|
| ≥ 95 % | on publie |
| 85 % à 95 % | on publie **et** on alerte le propriétaire de la source |
| < 85 % | on **arrête** le chargement ; un humain tranche |

Avec 87,4 %, nous sommes dans la zone « publier et alerter », et c'est l'**unicité** (91,4 %) qui tire le score vers le bas : les données sont exploitables, mais la source doit être corrigée. Écarter des lignes ne **répare** rien : c'est la correction à la source (la caisse qui exporte deux fois, le formulaire qui accepte une quantité vide) qui fait remonter le score durablement.

### 5.2.5 Surveiller dans le temps

Une photographie ne suffit pas : ce qui compte, c'est la **tendance**. Un taux de défauts qui passe de 12 % à 30 % en une semaine signale un incident (un export modifié, un formulaire cassé) bien avant que quelqu'un s'en plaigne. Le tableau de bord ci-dessous réunit les deux vues : le taux de violation de chaque règle, et l'évolution mensuelle du taux global avec son seuil d'alerte.

```text
figure : ch05-qualite-tableau.png
```
![Tableau de bord de qualité : à gauche, le taux de violation de chaque règle (quatre règles violées, cinq à zéro) ; à droite, le taux global par mois, stable entre 12 et 14 % et sous le seuil d'alerte de 15 %.](figures/ch05-qualite-tableau.png)

Le taux global est **stable**, entre 12 et 14 % chaque mois : le problème est **structurel** (la source produit toujours les mêmes défauts), et non un incident. Un pic isolé aurait raconté une autre histoire et déclenché l'alerte.

### 5.2.6 Profiler : laisser les données se dénoncer

Avant d'écrire des règles, on **profile** : on regarde les valeurs les plus fréquentes, les extrêmes, les valeurs « trop belles ». Le profilage révèle ce qu'aucune règle n'avait prévu. Regardons, par exemple, **quels** clients sont inconnus du CRM.

```text
           lignes
id_client        
999999        359
NUM identifiants distincts parmi les clients inconnus 1
```

Les 359 lignes « orphelines » ne sont **pas** des clients mal saisis : elles portent **toutes le même identifiant**, 999999. C'est la **valeur par défaut de la caisse** quand la vente est faite sans compte client. La règle « client connu » était donc trop sévère sur le fond : ces ventes sont **réelles**, et les rejeter (comme au 5.1) retire du chiffre d'affaires légitime. La décision correcte dépend de la question posée : pour un **chiffre d'affaires**, on les garde avec un client « anonyme » ; pour une **analyse de fidélité**, on les exclut. Une règle de qualité n'est jamais purement technique, elle encode une **décision métier**.

Une seconde famille de contrôles est **statistique** : une valeur plausible dans l'absolu peut être **anormale pour son produit**. On signale, en avertissement, un prix supérieur à cinq fois la médiane de son produit.

```text
 id_commande id_produit  prix_unitaire  mediane_produit
       11747       P015         157.27            24.56
       10197       P040         150.33            26.92
        2706       P047         161.12            28.23
       17725       P033         254.81            28.78
        9283       P047         150.95            28.23
NUM prix suspects (nombre, %) (57, 0.29)
```

Ces 57 lignes (0,3 %) ne sont pas rejetées : elles sont **soumises à relecture**. C'est la différence entre une règle bloquante (la valeur est impossible) et un avertissement (la valeur est improbable).

### 5.2.7 Contrats de données

Le meilleur moment pour traiter un défaut est **avant** qu'il n'entre dans le pipeline. Un **contrat de données** est un accord écrit entre le producteur d'une donnée (la caisse) et ses consommateurs (le pipeline) : quelles colonnes, de quel type, avec quelles garanties. On le rend **exécutable**, pour que la violation soit détectée à l'arrivée du fichier plutôt que dans le rapport du directeur.

```python
contrat = {"colonnes": ["id_commande", "date", "id_client", "id_produit", "quantite", "prix_unitaire"],
           "non_nulles": ["id_commande", "date", "id_client", "id_produit"],
           "taux_vide_max": {"quantite": 0.02}}

def verifier(lot, contrat):
    manques = [c for c in contrat["colonnes"] if c not in lot.columns]
    en_plus = [c for c in lot.columns if c not in contrat["colonnes"]]
    vides = [c for c in contrat["non_nulles"] if c in lot.columns and lot[c].isna().any()]
    seuils = [c for c, m in contrat["taux_vide_max"].items() if c in lot.columns and lot[c].isna().mean() > m]
    return {"colonnes manquantes": manques, "colonnes en plus": en_plus, "vides interdits": vides, "seuils dépassés": seuils}
```

Appliquons-le au lot d'aujourd'hui, puis à un lot où la caisse a **renommé** une colonne et en a **ajouté** une, comme au 5.1.8.

```text
lot du jour -> {'colonnes manquantes': [], 'colonnes en plus': [], 'vides interdits': [], 'seuils dépassés': []}
lot modifié -> {'colonnes manquantes': ['quantite'], 'colonnes en plus': ['qte', 'canal'], 'vides interdits': [], 'seuils dépassés': []}
```

Le premier lot passe tous les contrôles : son taux de quantités vides (1,45 %) reste sous le seuil de 2 %, la marge de tolérance du contrat. Le second est **refusé avant tout traitement**, avec un message qui dit exactement quoi corriger : la colonne `quantite` manque, `qte` et `canal` sont inattendues. Un contrat transforme une panne silencieuse en un message clair, adressé à la bonne personne.

> ✅ **À retenir (qualité des données).**
> - La qualité se **mesure** par dimensions (complétude, validité, unicité, cohérence, exactitude, fraîcheur), chacune avec un taux.
> - Une règle est une **fonction** qui désigne les lignes fautives ; on distingue règles **bloquantes** et **avertissements**.
> - Un **score** global et par dimension, comparé à des **seuils** décidés avec le métier, déclenche : publier, alerter, arrêter.
> - On surveille la **tendance** : un taux stable est un défaut structurel, un pic est un incident.
> - Le **profilage** révèle ce que les règles n'avaient pas prévu (ici, un identifiant client par défaut) ; une règle encode une **décision métier**.
> - Un **contrat de données** exécutable détecte les changements de structure **à l'arrivée**, avant tout calcul.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.4 à 5.5 (règles et score, contrat de données) et exercices 5.4 à 5.6.


## 5.3 Réconciliation : retrouver que deux lignes parlent de la même chose

Le catalogue de la boutique parle de « Bol en coton » ; la liste du fournisseur de « BOL coton ». Dans le CRM, la même cliente apparaît parfois deux fois, à deux orthographes. Pour un humain, c'est évident. Pour une jointure SQL, ce sont des **valeurs différentes**, donc des entités différentes : le chiffre d'affaires d'un produit est coupé en deux, le nombre de clientes est gonflé. Retrouver que deux enregistrements désignent la même entité s'appelle la **réconciliation** (*entity resolution*, ou *record linkage*).

### 5.3.1 Le problème, sur nos données

```text
id_produit           libelle
      P001     Plat en coton
      P002     Plat en verre
      P003 Plat en céramique
      P004  Bol en céramique
ref_fournisseur           designation
        F-15128     Plat  coton (lot)
        F-47481            Verre plat
        F-80941 Plat  céramique (lot)
        F-60568         Céramique bol
```

Aucune clé commune : le catalogue utilise `P001`, le fournisseur `F-15128`. Il faut comparer les **libellés**, et ceux-ci diffèrent par la casse, les espaces doubles, l'ordre des mots (« Céramique bol »), des mots parasites (« (lot) ») et des abréviations (« Plaid cér. »). La démarche est toujours la même, en trois temps : **normaliser** les textes, **mesurer** leur ressemblance, **décider** d'après un seuil.

### 5.3.2 Normaliser avant de comparer

Neuf fois sur dix, la normalisation fait l'essentiel du travail. Elle met tout en minuscules, retire les accents et les mots vides, développe les abréviations et **trie les mots** pour que l'ordre ne compte plus.

```text
     libellé brut       normalisé
Plat  coton (lot)      coton plat
        BOL coton       bol coton
    Céramique bol   bol ceramique
       Plaid cér. ceramique plaid
```

Après normalisation, « Céramique bol » et « Bol en céramique » deviennent le **même** texte : `bol ceramique`. La comparaison redevient triviale.

### 5.3.3 Mesurer la ressemblance entre deux textes

Quand deux textes ne sont **pas** identiques après normalisation (une faute de frappe, une lettre manquante), on mesure leur distance. Trois mesures courantes :

- **Distance de Levenshtein** : le nombre minimal de modifications (insertion, suppression, remplacement d'un caractère) pour passer d'un mot à l'autre. « dubois » → « dubios » demande 2 remplacements. On la convertit en similarité entre 0 et 1 par $1 - d / \max(|a|, |b|)$.
- **Similarité de Jaro-Winkler** : conçue pour les **noms de personnes**. Elle compte les caractères communs proches l'un de l'autre, pénalise les transpositions et **récompense un début de mot identique**, ce qui convient aux fautes de frappe qui touchent plutôt la fin.
- **Comparaison par jetons** (*token sort*, *token set*) : on découpe en mots avant de comparer, pour ignorer l'ordre ou les mots en trop.

```python
from rapidfuzz.distance import Levenshtein, JaroWinkler
print(Levenshtein.distance("dubois", "dubios"), round(JaroWinkler.similarity("dubois", "dubios"), 3))
```
<!--sortie-->
```text
2 0.961
```

```text
     a        b  Levenshtein  similarité (Lev.)  Jaro-Winkler
dubois   dubios            2               0.67          0.96
michel michelle            2               0.75          0.95
moreau    morin            3               0.50          0.79
martin   durand            5               0.17          0.56
```

La transposition « dubois / dubios » reste très proche (Jaro-Winkler 0,96), comme « michel / michelle » (0,95). Plus subtil : « moreau / morin » sont **deux noms différents** mais déjà à 0,79, loin des 0,56 de deux noms sans rapport. Aucune mesure ne sait si deux noms proches sont la même personne : c'est la raison pour laquelle on **combine** la similarité avec d'autres indices (5.3.5).

### 5.3.4 Rapprocher les produits

Comparons chaque désignation du fournisseur aux 48 libellés du catalogue et retenons le meilleur. Un test sur les 40 références **dont on connaît la bonne réponse** mesure la qualité de chaque niveau de préparation du texte.

```python
from rapidfuzz import fuzz

def meilleur_produit(designation, preparer):
    scores = [fuzz.ratio(preparer(designation), preparer(l)) for l in catalogue["libelle"]]
    k = int(np.argmax(scores))
    return catalogue["id_produit"][k], scores[k]
```

```text
                  préparation du texte  bonnes réponses (sur 40)  exactitude (%)
                          Textes bruts                        29            72.5
                          + minuscules                        36            90.0
        + espaces, accents, mots vides                        37            92.5
+ mots triés, abréviations développées                        40           100.0
```

La progression est le résultat à retenir : **chaque étape de normalisation vaut plus que le choix de la mesure**. Sur textes bruts, plus d'un appariement sur quatre échoue ; avec la normalisation complète, on atteint **100 %**. Dans ce cas précis, le meilleur score est même **exactement 100** pour les 40 références : après normalisation, les libellés sont **identiques**, et la « similarité floue » n'est plus nécessaire. Une simple jointure sur le texte normalisé aurait suffi.

> 💡 **Ne pas sortir l'artillerie floue trop tôt.** La comparaison approximative est coûteuse (chaque ligne contre toutes les autres) et risquée (elle accepte des presque-égalités qui n'en sont pas). On normalise d'abord, on essaie la jointure exacte, et l'on ne passe au flou que pour ce qui reste.

Le fournisseur fournit un indice supplémentaire, déjà utile : son **prix d'achat**. Un produit acheté 15 € ne peut pas être revendu 12 €. Ce recoupement (le prix d'achat vaut entre 45 % et 65 % du prix catalogue sur nos données connues) sert à **écarter** des candidats absurdes quand deux libellés sont ambigus.

### 5.3.5 Rapprocher les clients : blocage, score, décision

Le cas des clients est plus dur : il n'existe pas de libellé à normaliser, mais des fiches (prénom, nom, ville, date d'inscription) où l'on peut avoir deux personnes **homonymes** et une même personne **saisie deux fois avec une faute**. Une vérité est connue ici : sur 5 000 fiches, **800 sont des doublons** d'une autre fiche.

> 🧭 **Une clé facile, mais pas toujours disponible.** L'adresse électronique, passée en minuscules, retrouve **les 800 doublons** sans une erreur. Quand elle est fiable, c'est le meilleur identifiant et il faut s'arrêter là. Pour rendre l'exercice instructif, nous supposons qu'elle est **indisponible** (champ vide, ou adresse personnelle remplacée par une adresse de travail), ce qui arrive en pratique plus souvent qu'on ne le croit. Nous ajoutons aussi des **fautes de frappe** dans le nom de 35 % des doublons récents, comme le ferait une saisie à la main.


**Première tentative : égalité exacte** sur (prénom, nom, ville, date). Sur les textes bruts, puis normalisés :

```text
                               paires trouvées  rappel (%)
égalité sur textes bruts                     2         0.2
égalité sur textes normalisés              514        64.2
```

La normalisation fait passer le rappel de **0,2 % à 64,2 %** (514 paires sur 800) ; il reste les doublons dont le **nom a une faute**. Pour eux, il faut comparer de façon approximative. Mais comparer chacune des 5 000 fiches aux 4 999 autres représente près de **12,5 millions** de paires. Sur un million de fiches, ce serait $5 \times 10^{11}$. Il faut **réduire** le nombre de paires à examiner.

**Le blocage** (*blocking*) consiste à ne comparer que des fiches qui **partagent déjà une même valeur** sur une clé grossière (même ville, même prénom, même date d'inscription). Le choix de la clé est un arbitrage : trop large, il laisse trop de paires ; trop étroit, il **sépare des doublons** qui ne seront jamais comparés.

```text
                          clé de blocage  paires à comparer  part des paires (%)
       Aucun blocage (toutes les paires)           12497500              100.000
                              Même ville            1041310                8.332
               Même prénom et même ville              53153                0.425
Même prénom, ville et date d'inscription                828                0.007
```

Avec la clé la plus fine, on passe de plus de 12 millions de paires à moins d'un millier, un facteur **15 000**. Reste à **comparer** chaque paire candidate et à décider. Nous mesurons la similarité des **noms** par Jaro-Winkler.

```python
cles = ["prenom_n", "ville_n", "date_inscription"]
paires = paires_candidates(cl, cles)                       # blocage
scores = [JaroWinkler.similarity(cl["nom_n"][i], cl["nom_n"][j]) for i, j in paires]
meme_personne = [cl["id_vrai"][i] == cl["id_vrai"][j] for i, j in paires]     # vérité, pour évaluer
```

### 5.3.6 Précision, rappel et file de revue

Pour chaque seuil de similarité, deux erreurs sont possibles : **fusionner à tort** deux personnes différentes (faux positif), ou **laisser séparées** deux fiches de la même personne (faux négatif). On les résume par deux taux, que l'on a déjà rencontrés au volume III pour les classements :

$$\text{précision} = \frac{\text{paires fusionnées à raison}}{\text{paires fusionnées}}, \qquad \text{rappel} = \frac{\text{paires fusionnées à raison}}{\text{vraies paires de doublons}}$$

Une précision basse **détruit** des clientes (deux personnes fondues en une) ; un rappel bas **laisse** des doublons. Le coût relatif décide du seuil. La figure compare deux stratégies : un blocage **large** (même prénom et même ville) avec le seul nom comme indice, puis le blocage **fin** qui ajoute la date d'inscription.

```text
figure : ch05-reconciliation-pr.png
```
![À gauche, courbes précision-rappel pour la comparaison des noms : sans la date d'inscription, la précision reste très basse ; avec elle, elle dépasse 99 % pour un rappel de 100 %. À droite, nombre de paires à comparer selon la clé de blocage, de 12,5 millions à 828.](figures/ch05-reconciliation-pr.png)

```text
 seuil  paires  précision  rappel
  0.60     803       99.6   100.0
  0.80     803       99.6   100.0
  0.90     803       99.6   100.0
  0.95     720       99.7    89.8
  1.00     514       99.6    64.0
 seuil  paires  précision  rappel
  0.60    8393        9.5   100.0
  0.80    4326       18.5   100.0
  0.90    3938       20.3   100.0
  0.95    3746       19.2    89.8
  1.00    3299       15.5    64.0
```

Deux enseignements. **Le nom seul ne suffit pas** : beaucoup de personnes partagent prénom, nom et ville (des homonymes), si bien que même une similarité parfaite ne donne qu'une précision d'environ 15 à 20 %. **Le recoupement avec la date d'inscription change tout** : la précision monte à plus de 99 % **sans perdre de rappel** tant que le seuil reste raisonnable. La leçon est générale : un seuil sur **un** indice est fragile, la décision solide combine **plusieurs indices indépendants**.

Reste le choix du seuil. Une organisation sérieuse utilise **trois zones** plutôt qu'un seuil unique : au-dessus de 0,95, la fusion est automatique ; en dessous de 0,80, les fiches restent séparées ; entre les deux, la paire part en **file de revue** pour qu'un humain tranche.

```text
                       zone  paires  dont vraies doublons
fusion automatique (≥ 0,95)     720                   718
file de revue (0,80 à 0,95)      83                    82
          séparées (< 0,80)      25                     0
```

La file de revue ne contient que **83 paires** à relire (dont 82 sont de vrais doublons), contre 720 fusionnées automatiquement : l'automatisation traite l'évident, l'humain l'ambigu. Il reste **trois fusions à tort** sur 803 (deux en zone automatique, une en revue) : des **homonymes inscrits le même jour**, indiscernables par les données. Seul un humain ou une autre source (l'e-mail, un téléphone) peut les départager.

### 5.3.7 La fiche d'or

Une fois les doublons identifiés, on construit pour chaque personne une **fiche d'or** (*golden record*) qui remplace ses fiches multiples. Il faut décider, champ par champ, quelle valeur **survit** : c'est une **règle de survie**. Quelques règles usuelles : garder la valeur la plus récente, la plus complète, ou celle de la source la plus fiable. Ici, nous gardons la **plus ancienne fiche** et complétons ses champs vides avec ceux de l'autre.

```text
NUM fiches avant, fiches d'or après, vérité (5000, 4198, 4200)
```

Cinq mille fiches deviennent **4 198 personnes**, pour 4 200 en réalité : le nombre de clientes passe d'une valeur gonflée de 19 % à une valeur exacte à deux fiches près, qui correspondent aux homonymes fusionnés à tort. C'est le résultat concret de la réconciliation, que n'aurait jamais révélé un simple comptage des lignes du CRM.

> ✅ **À retenir (réconciliation).**
> - La démarche est toujours : **normaliser**, **bloquer**, **comparer**, **décider**, puis construire une fiche d'or.
> - La **normalisation** (casse, accents, mots vides, abréviations, mots triés) fait l'essentiel : sur nos produits, de 72 % à 100 % de bonnes réponses, sans mesure floue.
> - Levenshtein et Jaro-Winkler mesurent les **fautes de frappe** ; aucune mesure ne distingue deux **homonymes**.
> - Le **blocage** réduit le coût de plusieurs ordres de grandeur ; une clé trop fine sépare des doublons.
> - On évalue par **précision** et **rappel** contre une vérité connue, et l'on combine **plusieurs indices** plutôt qu'un seuil unique.
> - Trois zones (fusion, revue, séparation) : l'automate traite l'évident, l'humain l'incertain.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.6 à 5.7 (rapprocher les produits, rapprocher les clients) et exercices 5.7 à 5.9.


## 5.4 ➕ Pour aller plus loin : gouvernance, lignage et protection des données

> 🧭 **Section optionnelle.** Elle répond à trois questions que se pose toute organisation dès que ses pipelines se multiplient : *qui est responsable de quoi ?*, *d'où vient ce chiffre ?* et *comment protéger les personnes derrière les données ?* On peut la sauter à la première lecture ; le lignage et la pseudonymisation se retrouvent dans le projet de fin de volume.

Tant que l'on a un fichier et un script, tout est dans la tête de son auteur. Avec dix sources, vingt tables et trois équipes, personne ne sait plus qui corrige quoi, quelle table dépend de laquelle, ni si l'on a le droit de conserver l'adresse d'une cliente partie depuis trois ans. La **gouvernance des données** est l'ensemble des règles, des rôles et des outils qui répondent à ces questions **avant** qu'un incident ne les pose.

### 5.4.1 Qui est responsable de quoi ?

La gouvernance commence par des **rôles**, écrits et nommés. Sans eux, une anomalie signalée par un analyste tombe dans le vide.

| Rôle | Responsabilité | Exemple dans la boutique |
|---|---|---|
| **Propriétaire** (*data owner*) | décide de l'usage, de l'accès et de la durée de conservation | la gérante, pour les données clients |
| **Intendant** (*data steward*) | maintient la qualité et le sens de la donnée, tranche les cas ambigus | la personne qui traite la file de revue du 5.3 |
| **Producteur** | génère la donnée dans le système source | la caisse, le site web |
| **Consommateur** | utilise la donnée pour un besoin précis | l'analyste, le modèle de prévision |

À ces rôles s'ajoutent un **glossaire** (que veut dire exactement « client actif » ?), des **niveaux de sensibilité** (public, interne, personnel, confidentiel) et des **règles d'accès** (qui peut lire quoi). Un chiffre d'affaires dont deux services donnent des valeurs différentes parce qu'ils ne définissent pas pareil une « commande valide » est le symptôme classique d'un glossaire manquant.

### 5.4.2 Le lignage : d'où vient ce chiffre ?

Le **lignage** (*lineage*) est la **généalogie** d'une donnée : de quelles tables elle est issue, par quelles transformations. Il sert à trois usages concrets : **expliquer** un chiffre contesté, **mesurer l'impact** d'un changement (« si la caisse modifie son export, quelles tables sont touchées ? ») et **retrouver la cause** d'une erreur en remontant le fil.

La méthode la plus simple consiste à faire **enregistrer chaque étape** par le pipeline lui-même : ses entrées, ses sorties, le nombre de lignes avant et après. Nous rejouons le pipeline de ce chapitre avec un journal.

```text
                    etape                                           entrees                             sorties  lignes_in  lignes_out
               chargement                                  commandes_export                       stg_commandes      19700       19700
  typage et dédoublonnage                                     stg_commandes                    commandes_typees      19700       18000
               validation commandes_typees, clients_crm, produits_catalogue commandes_propres, commandes_rejets      18000       17218
rapprochement des clients                                       clients_crm                    clients_fiche_or       5000        4198
       mart par catégorie             commandes_propres, produits_catalogue                   mart_ca_categorie      17218           4
           mart par ville               commandes_propres, clients_fiche_or                       mart_ca_ville      17218          12
```

Ce journal **est** le graphe de lignage : chaque ligne relie des tables d'entrée à des tables de sortie. Pour répondre à « d'où vient `mart_ca_categorie` ? », il suffit de **remonter** les liens, récursivement. Pour l'analyse d'impact, on les **descend**.

```python
def en_amont(table, etapes):
    trouves = set()
    for e in etapes:
        if table in e["sorties"]:
            for source in e["entrees"]:
                trouves |= {source} | en_amont(source, etapes)
    return trouves
```

```text
D'où vient mart_ca_categorie ?    ['clients_crm', 'commandes_export', 'commandes_propres', 'commandes_typees', 'produits_catalogue', 'stg_commandes']
Qui dépend de clients_crm ?       ['clients_fiche_or', 'commandes_propres', 'commandes_rejets', 'mart_ca_categorie', 'mart_ca_ville']
Qui dépend de produits_catalogue ? ['commandes_propres', 'commandes_rejets', 'mart_ca_categorie', 'mart_ca_ville']
```

La deuxième question est celle de l'**analyse d'impact** : si le CRM change de format, **cinq** tables sont touchées, dont les deux marts de fin de chaîne (la table des rejets l'est aussi, car la validation vérifie que le client existe). La figure montre le même graphe, tel que le restituerait un outil de catalogue.

```text
figure : ch05-lignage.png
```
```text
figure : ch05-lignage.png
```
![Graphe de lignage : trois sources (commandes, CRM, catalogue) alimentent le staging puis les commandes propres, avec une branche vers le rebut (le lien du CRM et du catalogue vers le rebut, porté par la même étape de validation, n'est pas dessiné) ; les commandes propres et la fiche d'or des clients alimentent deux marts, par catégorie et par ville.](figures/ch05-lignage.png)

> 💡 **Le journal, une assurance bon marché.** Les outils du marché (dbt, Airflow, catalogues commerciaux) reconstruisent automatiquement ce graphe à partir du code des transformations. Le principe est celui que nous venons d'écrire : tout traitement déclare **ce qu'il lit et ce qu'il produit**.

### 5.4.3 Un catalogue de données

Le **catalogue** est l'annuaire des tables : pour chacune, une description, un responsable, une sensibilité, une fraîcheur. Même sous sa forme la plus modeste (un tableau tenu à jour), il évite à chaque nouvel arrivant de redécouvrir ce que les autres savent déjà.

| Table | Description | Propriétaire | Sensibilité | Mise à jour |
|---|---|---|---|---|
| `commandes_propres` | commandes validées, dédoublonnées | ventes | interne | chaque nuit |
| `clients_fiche_or` | une ligne par cliente, après réconciliation | gérante | **personnel** | chaque nuit |
| `commandes_rejets` | lignes refusées avec leur motif | intendant | interne | chaque nuit |
| `mart_ca_categorie` | chiffre d'affaires par catégorie | direction | public (en interne) | chaque nuit |

La colonne **sensibilité** décide de tout le reste : qui peut lire, combien de temps on conserve, et si la table doit être **pseudonymisée** avant d'être partagée.

### 5.4.4 Protéger les personnes : les principes

Dès qu'une table contient une personne, la loi (en Europe, le RGPD) impose trois réflexes, qui sont aussi de bonnes pratiques d'ingénierie : la **minimisation** (ne collecter et ne garder que ce dont on a besoin), la **finalité** (n'utiliser la donnée que pour l'usage annoncé) et la **limitation de durée** (ne pas conserver indéfiniment). Techniquement, on distingue deux opérations qu'on confond souvent :

- la **pseudonymisation** remplace l'identifiant (le nom, l'e-mail) par un code. La personne reste **ré-identifiable** par celui qui détient la clé ou d'autres informations : la donnée reste personnelle aux yeux de la loi ;
- l'**anonymisation** rend la ré-identification impossible, par tout moyen raisonnable. Elle est bien plus difficile à garantir qu'on ne le croit.

### 5.4.5 Pseudonymiser : le hachage ne suffit pas

Le premier réflexe est de remplacer l'e-mail par son **empreinte** (*hash*) : une fonction à sens unique, impossible à inverser directement. C'est insuffisant, car l'attaquant n'a pas besoin d'inverser : il **calcule l'empreinte de chaque e-mail plausible** et regarde lesquelles correspondent.

```python
import hmac

def empreinte(valeur):                        # naïf : même entrée, même empreinte, pour tout le monde
    return hashlib.sha256(valeur.lower().encode()).hexdigest()

def pseudonyme(valeur, cle_secrete):          # avec clé secrète : sans la clé, rien à rejouer
    return hmac.new(cle_secrete, valeur.lower().encode(), hashlib.sha256).hexdigest()
```

Simulons l'attaquant. Il connaît le **format** des adresses de la boutique (prénom, point, nom, numéro) et dispose des listes de prénoms et de noms courants. Il génère 1,6 million de candidats, calcule leurs empreintes, et compare avec la colonne « pseudonymisée ».


Résultat : **toutes** les adresses « anonymisées » par une empreinte nue sont retrouvées, aucune de celles protégées par une clé secrète. Le secret change la nature du problème : l'attaquant ne peut plus précalculer, il lui faudrait la clé. D'où les règles de pratique : une **clé secrète** conservée **hors** du jeu de données, jamais publiée avec lui, et renouvelée si elle fuit.

> ⚠️ **Pseudonymiser ne rend pas anonyme.** Même sans e-mail, une personne se reconnaît par **la combinaison** de ses attributs : ville, prénom, date d'inscription. On les appelle des **quasi-identifiants**.

Mesurons-le. Pour chaque combinaison d'attributs, calculons le **k** de chaque personne : le nombre de personnes qui partagent exactement ses valeurs (le *k-anonymat*). Un k de 1 signifie qu'elle est **unique**, donc identifiable par quiconque connaît ces attributs.

```text
                 attributs conservés  personnes uniques (%)  k minimal
                               ville                    0.0        324
                      ville + prénom                    0.0          8
ville + prénom + année d'inscription                    1.5          1
 ville + prénom + date d'inscription                   99.1          1
```

Avec la ville, ou la ville et le prénom, personne n'est identifiable (le plus petit groupe compte 8 personnes). Avec la date d'inscription **précise** en plus, **99 %** des personnes deviennent uniques : un simple prénom, une ville et un jour suffisent à les retrouver. Le remède est la **généralisation** : remplacer la date par l'année ramène la part de personnes uniques à 1,5 %. On perd en précision analytique, on gagne en protection. Le bon niveau dépend de l'usage, et c'est précisément une décision de **gouvernance**, pas de technique.

> ✅ **À retenir (gouvernance et protection).**
> - La gouvernance, ce sont des **rôles nommés** (propriétaire, intendant), un **glossaire**, des **niveaux de sensibilité** et des règles d'accès.
> - Le **lignage** relie chaque table à ses sources ; il se construit en faisant **déclarer** à chaque étape ses entrées et ses sorties, et sert à expliquer, à mesurer l'impact, à retrouver une cause.
> - Un **catalogue** décrit chaque table : sens, responsable, sensibilité, fraîcheur.
> - Une empreinte nue se **rejoue** par dictionnaire ; il faut une **clé secrète** conservée à part.
> - La pseudonymisation n'est pas l'anonymisation : les **quasi-identifiants** réidentifient ; on **généralise** et l'on mesure le *k*-anonymat.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.8 (lignage et pseudonymisation) et exercices 5.10 et 5.11.


## 5.5 ➕ Pour aller plus loin : collecter par scraping et par API

> 🧭 **Section optionnelle.** Jusqu'ici, les données arrivaient dans des fichiers. Il arrive qu'il faille **aller les chercher** : sur une page web, ou auprès d'un service qui les expose. Cette section montre comment le faire proprement, avec ses limites techniques et juridiques, sur un petit site **fabriqué sur votre machine** : aucun exemple n'ouvre de connexion vers l'extérieur.

### 5.5.1 Trois façons d'obtenir une donnée

Avant d'écrire la moindre ligne de collecte, on se demande si elle est nécessaire. Dans l'ordre de préférence :

1. **Un fichier ou un accès direct** fourni par le propriétaire de la donnée (export, base partagée). C'est le plus fiable, et il est presque toujours possible de le demander.
2. **Une API** (*Application Programming Interface*) : le service expose ses données dans un format prévu pour les machines (JSON), avec une documentation, des règles d'usage et des quotas.
3. **Le scraping** (*web scraping*) : on **lit la page web** comme le ferait un navigateur et l'on en extrait l'information. Il n'y a aucun contrat : la page peut changer sans prévenir, et l'usage peut être interdit.

Le scraping est le dernier recours : il est **fragile** (5.5.6) et **juridiquement incertain** (5.5.2). Quand une API existe, on l'utilise.

### 5.5.2 Les règles du jeu : droit, éthique, politesse

Collecter des données publiques n'est pas automatiquement permis. Une liste de vérifications à faire **avant** :

| Question | Pourquoi |
|---|---|
| Les **conditions d'utilisation** du site autorisent-elles l'extraction automatique ? | Un site peut l'interdire, et la violation de ces conditions peut engager votre responsabilité. |
| Le fichier **`robots.txt`** déclare-t-il la page interdite aux robots ? | C'est le mécanisme standard par lequel un site dit où il accepte les robots. Le respecter est une règle de base. |
| Les données sont-elles **personnelles** ? | Une donnée « publique » reste soumise à la protection des données (5.4.4) : avoir accès n'est pas avoir le droit d'en faire n'importe quoi. |
| Le contenu est-il **protégé** (droit d'auteur, droit des bases de données) ? | Extraire n'est pas réutiliser : la republication peut être interdite. |
| Votre collecte **charge-t-elle** le serveur ? | Un robot trop rapide ressemble à une attaque. On limite le débit et l'on s'identifie. |

> ⚠️ **Ce livre ne vous donne pas un avis juridique.** Les règles varient selon les pays et les sites. Dans le doute, on demande l'accès officiel : c'est presque toujours plus rapide qu'une collecte bricolée, et sans risque.

### 5.5.3 Un site de démonstration local

Pour s'exercer sans cible réelle, nous démarrons un petit serveur **dans un fil d'exécution de notre propre machine**. Il propose : un fichier `robots.txt` qui interdit le dossier `/prive/`, une page `/catalogue` qui liste les 48 produits en HTML, et une API `/api/avis` qui rend 400 avis clients, **paginés** et **limités en débit** (le serveur refuse une requête sur sept, comme le ferait un vrai service surchargé).


### 5.5.4 Scraper une page HTML

Un site respectueux commence par lire le `robots.txt`. La bibliothèque standard sait l'interpréter.

```python
import requests
from urllib import robotparser

robots = robotparser.RobotFileParser(base + "/robots.txt")
robots.read()
print(robots.can_fetch("*", base + "/catalogue"), robots.can_fetch("*", base + "/prive/clients"), robots.crawl_delay("*"))
```
<!--sortie-->
```text
True False 1
```

La page `/catalogue` est autorisée, le dossier `/prive/` ne l'est pas, et le site demande **une seconde entre deux requêtes** (`Crawl-delay`). Si l'on insiste sur une page interdite, le serveur répond par un code **403** (accès refusé) ; un bon robot n'essaie même pas.

Le contenu d'une page HTML est un **arbre de balises**. La bibliothèque `BeautifulSoup` permet de désigner des éléments par des **sélecteurs CSS** : `div.produit` désigne les balises `div` de classe `produit`, `.prix` les éléments de classe `prix`.

```python
from bs4 import BeautifulSoup

page = requests.get(base + "/catalogue", timeout=5).text
soupe = BeautifulSoup(page, "html.parser")
produits = [{"id_produit": d["data-id"], "libelle": d.select_one(".nom").text,
             "prix": float(d.select_one(".prix").text.replace("€", ""))} for d in soupe.select("div.produit")]
```

```text
id_produit           libelle  prix
      P001     Plat en coton 33.09
      P002     Plat en verre 31.61
      P003 Plat en céramique 12.75
NUM produits extraits, identiques au catalogue source (48, True)
```

Trois points demandent de l'attention : le **texte brut** contient des symboles (« € ») à retirer avant de convertir en nombre ; on utilise des **attributs stables** (`data-id`) plutôt que l'ordre d'apparition ; et l'on **vérifie** le résultat contre ce que l'on sait (ici, les 48 produits et leurs prix concordent avec le catalogue).

### 5.5.5 Interroger une API paginée, limitée en débit

Une API renvoie des données **structurées** : plus besoin de décoder du HTML. Mais elle ne livre pas tout d'un coup : elle découpe le résultat en **pages**, et chaque réponse indique s'il y en a une suivante. Elle **limite** aussi le nombre de requêtes par minute : au-delà, elle répond **429 Too Many Requests**, souvent avec un en-tête `Retry-After` qui dit quand réessayer.

Un collecteur naïf ignore ce code et perd des pages **sans le savoir**. Voyons-le d'abord.

```text
NUM collecteur naïf : pages reçues sur 16, avis reçus sur 400 (14, 350)
NUM pages perdues sans erreur visible [7, 14]
```

Seules 14 pages sur 16 sont arrivées (350 avis sur 400) ; les pages 7 et 14 manquent, et rien ne l'a signalé : le jeu d'avis est **tronqué en silence**. Le collecteur correct traite explicitement le 429, avec une **attente croissante** (*backoff exponentiel*) pour ne pas aggraver la surcharge, et un **nombre d'essais limité**.

```python
import time

def lire_page(session, url, essais=5):
    for k in range(essais):
        r = session.get(url, timeout=5)
        if r.status_code == 429:                                    # trop de requêtes : on attend, puis on réessaie
            time.sleep(float(r.headers.get("Retry-After", 0)) + 0.01 * 2 ** k)
            continue
        r.raise_for_status()                                        # toute autre erreur est une vraie erreur
        return r.json()
    raise RuntimeError(f"abandon après {essais} essais : {url}")
```

```python
session, avis_collectes, page = requests.Session(), [], 1
while page:                                                         # la réponse dit s'il y a une page suivante
    reponse = lire_page(session, f"{base}/api/avis?page={page}&taille=25")
    avis_collectes += reponse["resultats"]
    page = reponse["suivante"]
```

```text
NUM collecteur robuste : avis collectés, identifiants uniques, identiques à la source (400, 400, True)
```

Les 400 avis sont là, **sans doublon**, identiques à la source. Pour l'ingénierie des données, le principe est celui du 5.1 : on **conserve la réponse brute** (dans la couche de staging, avec la date de collecte), puis on la transforme ; et une relance doit être **idempotente**, d'où l'intérêt d'un identifiant d'avis pour fusionner plutôt qu'ajouter.

### 5.5.6 Fragilité et surveillance

Un scraper repose sur la **structure de la page**, que personne ne s'engage à conserver. Le site de démonstration a une seconde mise en page, `/catalogue-v2`, qui contient les mêmes produits avec **d'autres balises** : le sélecteur `div.produit` ne trouve plus rien.

```text
NUM produits trouvés par le sélecteur d'origine (ancienne page, nouvelle page) (48, 0)
NUM produits trouvés par un sélecteur plus robuste, article[id] 48
```

Le pire scénario n'est pas une erreur, c'est un **résultat vide qui passe inaperçu** : le pipeline continue et la table du jour est vide. La défense est celle du 5.2 : un **contrôle à l'arrivée** (« on attend 48 produits, au moins 40 »), qui arrête le chargement et alerte plutôt que de publier du vide.


> ✅ **À retenir (collecte).**
> - Par ordre de préférence : **accès direct**, puis **API**, puis **scraping** en dernier recours.
> - Avant de collecter : conditions d'utilisation, **`robots.txt`**, données personnelles, droits sur le contenu. Le collecteur **s'identifie** et **limite son débit**.
> - Une API **paginée** se parcourt jusqu'à la dernière page ; une réponse **429** se traite par attente croissante et nombre d'essais borné. Ignorer un 429 **tronque les données en silence**.
> - Un scraper dépend de la structure de la page : **sélecteurs stables**, **contrôle de volume** à l'arrivée, alerte en cas de résultat vide.
> - On garde la **réponse brute** avec sa date de collecte, et l'on charge de façon **idempotente**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.9 (collecter sur le site local) et exercice 5.12.


## Bilan du chapitre 5

Vous savez maintenant :

- **concevoir un pipeline en couches** (sources, staging brut, nettoyé, rebut, marts), **lire sans deviner** (tout en texte, typage explicite) et **ne rien perdre en silence** : l'équation de conservation (19 700 lignes lues, 1 700 doublons, 782 rejets, 17 218 commandes propres) est un test que tout pipeline doit passer ;
- **écrire la même transformation en pandas (ETL) et en SQL avec DuckDB (ELT)**, et vérifier l'égalité des résultats (17 218 commandes, 893 243,24 € dans les deux cas) ;
- **rendre un chargement rejouable** par une clé et une fusion (*upsert*) : l'ajout naïf d'un lot rejoué gonfle la table de 17 218 à 23 111 lignes, la fusion la laisse à 17 218 ; et se méfier du **filigrane** sur la date métier, qui perd les données tardives ;
- **mesurer la qualité** par dimensions (complétude, validité, unicité, cohérence, exactitude, fraîcheur), avec des règles écrites comme de petites fonctions, un score (87,4 %), des seuils de décision et un tableau de bord dans le temps ; **profiler** pour découvrir ce que les règles n'avaient pas prévu (359 « clients inconnus » qui sont un seul identifiant par défaut) ; et **faire respecter un contrat de données** à l'arrivée du fichier ;
- **chiffrer le coût d'une donnée sale** : un calcul naïf surestime le chiffre d'affaires de 94 586,61 €, soit 10,6 % ;
- **réconcilier des enregistrements** : normaliser (de 72,5 % à 100 % de bons rapprochements de produits sans aucune mesure floue), mesurer la ressemblance (Levenshtein, Jaro-Winkler), **bloquer** pour passer de 12,5 millions à 828 paires, juger par précision et rappel, router les cas douteux vers une file de revue et construire une **fiche d'or** (5 000 fiches, 4 198 personnes pour 4 200 en réalité) ;
- (en option) **tracer le lignage** d'une table et mesurer l'impact d'un changement, **gouverner** (rôles, glossaire, sensibilité), **pseudonymiser avec une clé secrète** en sachant qu'une empreinte nue se retrouve par dictionnaire (4 200 adresses sur 4 200) et que les quasi-identifiants réidentifient (99 % d'uniques avec ville, prénom et date précise) ;
- (en option) **collecter par scraping et par API** dans le respect de `robots.txt` et du débit, gérer la pagination et le code 429, et se défendre contre le résultat vide qui passe inaperçu.

Le fil rouge du chapitre tient en une phrase : **une donnée ne devient fiable que si chaque transformation est explicite, mesurée et rejouable**. Rejeter, dédoublonner, rapprocher, pseudonymiser : toutes ces décisions encodent des choix **métier**, qu'il faut écrire, tracer et faire valider, plutôt que de les enterrer dans un script.

Le chapitre 6 présente les **plateformes cloud**, où ces pipelines tournent en pratique : stockage, calcul à la demande, et la question qui décide de beaucoup de projets, **ce que cela coûte**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.9 et exercices 5.1 à 5.12.

