## 2.1 Principes de l'ETL

Un pipeline de données est une chaîne qui prend des fichiers ou des tables qu'on ne contrôle pas et en fait des tables sur lesquelles on peut s'appuyer. Cette section donne le vocabulaire et les trois idées qui font la différence entre un script qui marche une fois et une chaîne qui tient : on **sépare** lecture, transformation et chargement ; on **n'écrit jamais** dans la copie brute ; et surtout on rend le chargement **idempotent**, c'est-à-dire qu'on peut le relancer sans en changer le résultat.

### 2.1.1 Trois verbes et une chaîne

**ETL** est le sigle de trois verbes : **E**xtract (extraire les données de leur source), **T**ransform (les mettre en forme et les contrôler), **L**oad (les charger dans l'entrepôt). Ces trois gestes se retrouvent dans tous les systèmes, sous des habits très différents : un notebook, un script planifié, un outil graphique ou un service infonuagique.

```python hide
P.fig_chaine("ch02-chaine-etl.png")
```
<!--sortie-->
```text
figure : ch02-chaine-etl.png
```

![La chaîne de chargement de ce chapitre : les fichiers livrés sont copiés tels quels dans un dépôt, transformés et contrôlés, puis chargés dans l'entrepôt ; ce qui est rejeté va en quarantaine avec son motif, et chaque exécution laisse une trace dans le journal et la table des exécutions. Schéma dessiné.](figures/ch02-chaine-etl.png)

Trois mots du schéma méritent d'être posés dès maintenant.

- Le **dépôt** (on dit aussi *zone de transit* ou *staging*) est une copie **brute** de ce qui est arrivé. On n'y corrige rien. Si une règle de transformation se révèle fausse dans trois mois, on pourra refaire le calcul depuis le brut ; si on a corrigé le brut, on ne le pourra plus.
- L'**entrepôt** est la base de données propre, organisée en faits et en dimensions (chapitre 1 de ce volume, sections 1.2 et 1.3). Ici, une table de faits des lignes de commande et deux dimensions, le client et le produit.
- Les **marts** (ou *magasins de données*) sont des tables ou des vues plus petites, bâties sur l'entrepôt pour un usage précis : le tableau de bord de la gérante, par exemple.

Un dernier mot sur le vocabulaire. On dit **ELT** quand l'ordre des deux dernières lettres change : on charge d'abord les données presque brutes dans l'entrepôt, puis on les transforme *dans* l'entrepôt, en SQL. Cette variante est devenue courante avec les entrepôts infonuagiques, qui calculent vite sur de gros volumes. Nous y reviendrons à la fin de la section.

### 2.1.2 Extraire : lire ce qui arrive, sans le modifier

L'extraction est le geste le plus ingrat et celui qui provoque le plus de pannes. La règle est simple : **lire tout en texte**, ne rien interpréter à ce stade. C'est pandas lui-même qui interprète trop vite : il lit « 03/04/2025 » comme il peut, il transforme un identifiant avec un zéro initial en nombre, il devine une colonne de montants et se trompe sur une virgule. Si on lit en texte, tout est possible ensuite, et rien n'est perdu.

Voici la fonction qui lit un fichier du dépôt. Elle essaie l'UTF-8, retombe sur l'ancien encodage `cp1252` quand le fichier n'est pas de l'UTF-8, et refuse un fichier vide.

```python
COLONNES = ["id_ligne", "id_commande", "date_commande", "id_client", "canal", "id_produit", "quantite", "montant"]

def lire_brut(chemin):
    octets = open(chemin, "rb").read()
    try:
        texte = octets.decode("utf-8")
    except UnicodeDecodeError:
        texte = octets.decode("cp1252")
    if not texte.strip():
        raise ValueError("fichier vide")
    return pd.read_csv(io.StringIO(texte), dtype=str, keep_default_na=False)
```

Que donne-t-elle sur les quinze fichiers du dépôt ? Ne regardons que ceux qui posent problème, en comparant le nombre de lignes lues au nombre annoncé par le manifeste et les colonnes trouvées aux colonnes attendues.

```python hide-code
diag = []
for _, f in man.iterrows():
    try:
        d = lire_brut(os.path.join(DEPOT, f["fichier"]))
        diag.append((f["fichier"], len(d), f["lignes_annoncees"], sorted(set(COLONNES) ^ set(d.columns))))
    except ValueError as e:
        diag.append((f["fichier"], 0, f["lignes_annoncees"], [str(e)]))
diag = pd.DataFrame(diag, columns=["fichier", "lues", "annoncées", "écart de colonnes"])
print(diag[(diag["lues"] != diag["annoncées"]) | (diag["écart de colonnes"].str.len() > 0)].to_string(index=False))
```
<!--sortie-->
```text
              fichier  lues  annoncées      écart de colonnes
commandes_2025-05.csv  2388       2388 [montant, total_ligne]
commandes_2025-09.csv     0       2522         [fichier vide]
commandes_2025-10.csv  2249       2645                     []
```

Trois fichiers sortent du lot : celui de mai, dont la colonne des montants s'appelle autrement ; celui de septembre, **vide** ; celui d'octobre, **tronqué** (le même que dans l'introduction). Quant au fichier d'août, il est lu sans erreur, et il faut pourtant s'en méfier : il est en `cp1252`, et un mauvais décodage ne lève aucune erreur, il produit des caractères étranges.

```python
print(list(lire_brut(os.path.join(DEPOT, "commandes_2025-08.csv"))["canal"].unique()))
```
<!--sortie-->
```text
['Boutique', 'Site', 'Réseaux']
```

Le canal « Réseaux » est correctement lu : le repli sur `cp1252` a fonctionné. Mais ce repli est un **pari**. Si le fichier avait été dans un troisième encodage, nous aurions obtenu un texte faux sans le savoir. Dans une chaîne sérieuse, on le détecte : on vérifie que les valeurs des colonnes de catégories sont dans la liste connue (c'est ce que fera la transformation).

> ⚠️ **Piège : le fichier « qui s'ouvre » n'est pas un fichier correct.** Un fichier vide, tronqué, mal encodé ou renommé s'ouvre souvent sans erreur. Le **manifeste** (le nombre de lignes que l'exportateur annonce) est le plus simple des contrôles à la source : il aurait détecté à lui seul l'octobre tronqué et le septembre vide. Demandez-le à l'équipe qui exporte, comme un reçu de livraison.

### 2.1.3 Transformer : un contrat, des règles, une quarantaine

La transformation fait deux choses distinctes. D'abord, elle vérifie que la livraison respecte le **contrat de données**, c'est-à-dire l'accord écrit entre qui produit le fichier et qui le consomme. Ensuite, elle applique des **règles** ligne par ligne : types, valeurs permises, cohérence avec les référentiels.

Voici notre contrat, qui tient en un tableau.

| Colonne | Type attendu | Règle |
|---|---|---|
| `id_ligne` | entier | clé naturelle, unique dans l'ensemble des livraisons |
| `id_commande` | entier | non vide |
| `date_commande` | date | écrite `AAAA-MM-JJ` (ou `JJ/MM/AAAA`, tolérée) |
| `id_client` | entier | doit exister dans le référentiel des clients |
| `canal` | texte | `Boutique`, `Site` ou `Réseaux` |
| `id_produit` | entier | non vide |
| `quantite` | entier | non vide |
| `montant` | nombre | montant TTC de la ligne, **positif** (les avoirs passent par un autre circuit) |

Une livraison qui n'a pas les bonnes colonnes **s'arrête** : il est inutile de deviner. Une livraison qui a les bonnes colonnes mais contient quelques lignes incorrectes **continue**, et les lignes incorrectes sont mises de côté avec leur motif. Voici d'abord la partie « colonnes », qui sait aussi reconnaître l'ancien nom d'une colonne renommée.

```python
ALIAS = {"total_ligne": "montant"}

def appliquer_contrat(df):
    df = df.rename(columns=ALIAS)
    manque = [c for c in COLONNES if c not in df.columns]
    if manque:
        raise ValueError("colonnes absentes : " + ", ".join(manque))
    return df[COLONNES]

def extraire(chemin):
    return appliquer_contrat(lire_brut(chemin))
```

Puis la partie « lignes ». Elle convertit les types (une valeur illisible devient une valeur manquante, jamais une erreur qui arrête tout), cherche les lignes qui violent une règle, et renvoie **deux** tables : les lignes valides et les lignes rejetées, chacune avec son motif.

```python
CANAUX = {"Boutique", "Site", "Réseaux"}
NOMBRES = ["id_ligne", "id_commande", "id_client", "id_produit", "quantite", "montant"]

def transformer(df, clients):
    d = pd.to_datetime(df["date_commande"], format="%Y-%m-%d", errors="coerce")
    d = d.fillna(pd.to_datetime(df["date_commande"], format="%d/%m/%Y", errors="coerce"))
    t = df.assign(date_commande=d, **{c: pd.to_numeric(df[c], errors="coerce") for c in NOMBRES})
    motif = np.select([df.duplicated(), t.isna().any(axis=1), ~df["canal"].isin(CANAUX), t["montant"] < 0, ~t["id_client"].isin(clients)],
                      ["doublon exact", "valeur illisible ou manquante", "canal inconnu", "montant négatif", "client inconnu"], default="")
    ok = motif == ""
    valides = t[ok].astype({c: "int64" for c in NOMBRES[:5]}).reset_index(drop=True)
    return valides, df[~ok].assign(motif=motif[~ok], ligne=np.flatnonzero(~ok) + 2).reset_index(drop=True)
```

Deux détails comptent. L'ordre des règles est celui de la liste : une ligne dupliquée et fautive est signalée comme « doublon exact » plutôt que comme faute, ce qui évite de compter deux fois. Et la date accepte deux formats, ce qui est écrit **dans le contrat** (« tolérée ») plutôt que laissé au hasard : le fichier de juillet est rédigé en `JJ/MM/AAAA`. Essayons sur le fichier d'avril.

```python
clients = set(pd.read_csv(os.path.join(os.environ["DONNEES"], "clients.csv"))["id_client"])
valides, rejets = transformer(extraire(os.path.join(DEPOT, "commandes_2025-04.csv")), clients)
print(len(valides), "lignes valides,", len(rejets), "rejetées")
print(rejets[["ligne", "id_ligne", "id_client", "montant", "motif"]].to_string(index=False))
```
<!--sortie-->
```text
2225 lignes valides, 3 rejetées
 ligne id_ligne id_client montant           motif
   713   900019      4598  -72.83 montant négatif
   906   900001     90001   18.44  client inconnu
  1666   900013     90013    32.2  client inconnu
```

Les trois lignes rejetées sont deux « lignes orphelines » (le client n'existe pas dans le référentiel) et un montant négatif : en vrai, un avoir saisi par erreur dans le circuit des commandes.

> 💡 **Intuition : on ne jette pas, on met de côté.** Supprimer en silence une ligne douteuse revient à dire « cette vente n'a pas existé ». La mettre en **quarantaine** avec son motif permet de la corriger à la source, de la réintégrer, ou de décider en connaissance de cause de l'écarter. Les chiffres du rapport doivent alors se lire « hors lignes en quarantaine », et le nombre de lignes concernées doit être connu.

### 2.1.4 Charger : complet ou incrémental

Une fois les lignes valides en main, il faut les écrire dans l'entrepôt. Il y a deux grandes manières de le faire.

| | Chargement **complet** | Chargement **incrémental** |
|---|---|---|
| Principe | on vide la cible, on recharge tout | on n'ajoute que ce qui est nouveau ou modifié |
| Avantage | simple, impossible de dériver | rapide, adapté aux gros volumes et aux historiques |
| Risque | lent quand les volumes croissent ; fenêtre pendant laquelle la cible est vide | perdre des corrections, doubler des lignes |
| Convient à | petites tables, **dimensions** (clients, produits) | **faits** volumineux (lignes de commande) |

Les dimensions de notre entrepôt sont petites (6 000 clients, 120 produits) : on les recharge en entier à chaque exécution. Les faits (près de 30 000 lignes cette année, bien davantage en pratique) se chargent par incréments.

Pour un incrément, il faut un moyen de savoir « ce qui est nouveau ». La méthode la plus répandue est le **filigrane** (*watermark*) : on retient la plus grande date déjà chargée et on ne prend que les lignes plus récentes. C'est simple, c'est tentant, et c'est exactement ce qui aurait gardé le **mauvais montant de mars**. Calculons ce que le filigrane aurait laissé passer quand le fichier corrigé arrive.

```python hide-code
entrepot = P.nouvel_entrepot()
for f in ["commandes_2025-01.csv", "commandes_2025-02.csv", "commandes_2025-03.csv"]:
    v, _ = transformer(extraire(os.path.join(DEPOT, f)), clients)
    P.charger(entrepot, v, f)
filigrane = entrepot.execute("SELECT max(date_commande) FROM fait_ligne").fetchone()[0]
v2, _ = transformer(extraire(os.path.join(DEPOT, "commandes_2025-03_v2.csv")), clients)
print("filigrane :", filigrane, "| lignes du renvoi retenues par le filigrane :", int((v2["date_commande"] > pd.Timestamp(filigrane)).sum()), "sur", len(v2))
```
<!--sortie-->
```text
filigrane : 2025-03-31 | lignes du renvoi retenues par le filigrane : 0 sur 2023
```

Le fichier corrigé de mars concerne des **dates passées** : aucune de ses lignes n'est plus récente que le filigrane, donc aucune n'est chargée, et le montant erroné reste dans l'entrepôt. Le filigrane de date convient à des données qui **ne changent jamais après coup** (des événements). Dès qu'une source corrige ses livraisons, il faut une autre stratégie : charger par **lot** (le fichier livré) et **fusionner sur la clé naturelle**.

### 2.1.5 L'idempotence : relancer sans danger

Une opération est **idempotente** quand l'exécuter deux fois donne le même résultat que l'exécuter une fois. Pour un pipeline, c'est la propriété la plus précieuse : on peut relancer après une panne, rejouer un mois, corriger une règle et recharger sans se demander « est-ce que j'ai déjà chargé celui-là ? ».

Le chargement le plus simple, l'**ajout**, n'est pas idempotent. Le chargement par **fusion** sur la clé naturelle (en anglais *upsert*, pour *update* ou *insert*) l'est : si la ligne existe, on la remplace ; sinon, on l'ajoute. Voici les deux, côte à côte.

```python
entrepot.execute("CREATE TABLE fait_ajout AS SELECT * FROM fait_ligne WHERE false")
entrepot.execute("DELETE FROM fait_ligne")

def charger_ajout(con, v, fichier):
    con.register("lot", v.assign(fichier=fichier)[COLONNES + ["fichier"]])
    con.execute("INSERT INTO fait_ajout SELECT * FROM lot")
```

La fusion, elle, est celle du module `P.charger` : une seule instruction SQL, `INSERT OR REPLACE`, qui s'appuie sur la clé primaire déclarée sur `id_ligne`. Rejouons l'histoire du premier trimestre : trois livraisons, la relance accidentelle de mars (le planificateur a redémarré), puis le fichier corrigé.

```python hide-code
histoire = [("janvier", "commandes_2025-01.csv"), ("février", "commandes_2025-02.csv"), ("mars", "commandes_2025-03.csv"),
            ("mars relancé", "commandes_2025-03.csv"), ("mars corrigé", "commandes_2025-03_v2.csv")]
resultats = []
for nom, f in histoire:
    v, _ = transformer(extraire(os.path.join(DEPOT, f)), clients)
    charger_ajout(entrepot, v, f)
    P.charger(entrepot, v, f)
    resultats.append((nom, *[entrepot.execute(f"SELECT round(sum(montant), 2) FROM {t}").fetchone()[0] for t in ("fait_ajout", "fait_ligne")]))
tableau = pd.DataFrame(resultats, columns=["étape", "ajout simple (€)", "fusion (€)"])
tableau.index = tableau.index + 1
print(tableau.to_string())
```
<!--sortie-->
```text
          étape  ajout simple (€)  fusion (€)
1       janvier          89178.95    89178.95
2       février         161821.39   161821.39
3          mars         256012.48   256012.48
4  mars relancé         350203.57   256012.48
5  mars corrigé         439990.87   251608.69
```

```python hide
vrai_t1 = sum(VERITE["par_mois"][m]["total_original"] for m in ("2025-01", "2025-02", "2025-03"))
P.fig_idempotence([r[0] for r in resultats], [r[1] for r in resultats], [r[2] for r in resultats], vrai_t1, "ch02-idempotence.png")
```
<!--sortie-->
```text
figure : ch02-idempotence.png
```

![Le chiffre d'affaires TTC chargé après chacune des cinq livraisons du premier trimestre, par un ajout simple (orange) et par une fusion sur la clé (bleu). Le trait pointillé est le vrai total du trimestre. La fusion corrige le mauvais montant de mars quand le fichier corrigé arrive ; l'ajout compte les ventes de mars en double, puis en triple exemplaire.](figures/ch02-idempotence.png)

Le résultat est sans appel. Après la relance de mars, l'ajout simple a **doublé** les ventes du mois ; après le fichier corrigé, il en garde **trois exemplaires**, avec un total qui n'a plus rien à voir avec la réalité. La fusion, elle, reste stable à la relance et **se corrige** quand le renvoi arrive : elle retombe sur le vrai total du trimestre, soit 251 609 €.

On peut transformer cette propriété en test, que l'on garde dans la chaîne : une **empreinte** de l'état de la table, calculée avant et après une exécution répétée.

```python
def empreinte(con):
    return con.execute("""SELECT count(*), round(sum(montant), 2),
           md5(string_agg(id_ligne || ':' || montant, ',' ORDER BY id_ligne)) FROM fait_ligne""").fetchone()
avant = empreinte(entrepot)
P.charger(entrepot, v2, "commandes_2025-03_v2.csv")
print("état identique après un rechargement :", avant == empreinte(entrepot))
```
<!--sortie-->
```text
état identique après un rechargement : True
```

Il existe d'autres manières d'obtenir l'idempotence, chacune avec ses usages.

| Stratégie | Comment | Quand l'utiliser |
|---|---|---|
| **Fusion sur la clé** | `INSERT OR REPLACE` / `MERGE` sur la clé naturelle | des lignes qui peuvent être corrigées après coup (notre cas) |
| **Remplacement de partition** | on supprime tout le mois, on recharge le mois | pas de clé fiable, mais un découpage net (par mois) |
| **Vidage et rechargement** | on vide la table, on recharge tout | petites tables, dimensions |
| **Dédoublonnage en lecture** | on charge tout, la vue garde la ligne la plus récente | cible où les mises à jour sont coûteuses |

> ⚠️ **Piège : l'idempotence n'est pas la sécurité de la clé.** La fusion suppose que `id_ligne` identifie **vraiment** une ligne dans toutes les livraisons. Si la source recyclait ses identifiants d'un mois à l'autre, la fusion écraserait des ventes différentes par des ventes plus récentes, sans erreur. La clé naturelle est un **contrat**, au même titre que les colonnes : on la vérifie (unicité, stabilité) avant de bâtir dessus.

### 2.1.6 ELT : laisser l'entrepôt calculer

Dans notre chaîne, la transformation se fait en pandas, **avant** le chargement : c'est de l'ETL. Dès que les données sont chargées proprement, les agrégations (le chiffre d'affaires par mois et par canal, par exemple) se font de préférence en SQL, **dans** l'entrepôt : c'est de l'ELT. Les deux ne s'opposent pas. On transforme avant le chargement ce qui est lié au **fichier** (encodage, dates, contrat) ; on transforme après ce qui est lié à l'**analyse** (agrégats, indicateurs).

Voici le mart du chiffre d'affaires mensuel, défini par une vue SQL : l'entrepôt ne stocke que la définition, et le calcul se fait à la lecture.

```python
entrepot.execute("""CREATE OR REPLACE VIEW mart_ca_mensuel AS
    SELECT strftime(date_commande, '%Y-%m') AS mois, canal, count(DISTINCT id_commande) AS commandes,
           round(sum(montant), 2) AS ca_ttc, round(sum(montant) / 1.2, 2) AS ca_ht
    FROM fait_ligne GROUP BY ALL""")
print(entrepot.execute("SELECT * FROM mart_ca_mensuel WHERE mois = '2025-03' ORDER BY canal").df().to_string(index=False))
```
<!--sortie-->
```text
   mois    canal  commandes   ca_ttc    ca_ht
2025-03 Boutique        402 39038.90 32532.42
2025-03  Réseaux         90  8440.16  7033.47
2025-03     Site        398 42308.24 35256.87
```

On ne fait pas confiance à un calcul tant qu'un autre outil ne l'a pas confirmé. Recalculons le même mart avec pandas, à partir des lignes de l'entrepôt, et comparons.

```python hide-code
lignes = entrepot.execute("SELECT * FROM fait_ligne").df()
pd_mart = lignes.assign(mois=lignes["date_commande"].dt.strftime("%Y-%m")).groupby(["mois", "canal"]).agg(ca_ttc=("montant", "sum")).round(2)
sql_mart = entrepot.execute("SELECT mois, canal, ca_ttc FROM mart_ca_mensuel").df().set_index(["mois", "canal"])
print("écart maximal entre SQL et pandas :", fr((pd_mart["ca_ttc"] - sql_mart["ca_ttc"]).abs().max(), 2), "€ sur", len(sql_mart), "cellules")
```
<!--sortie-->
```text
écart maximal entre SQL et pandas : 0,00 € sur 9 cellules
```

> 🧭 **En pratique : ETL ou ELT ?** Pour des fichiers de quelques mégaoctets, la distinction est académique. Elle compte quand les volumes dépassent la mémoire d'un poste (on veut alors calculer là où sont les données) et quand plusieurs équipes réutilisent les mêmes tables (la logique SQL vit alors dans l'entrepôt, versionnée, testée, partagée : voir les modèles de la section 2.4).

> ✅ **À retenir.**
> - Un pipeline sépare trois gestes : **extraire** (lire en texte, sans rien interpréter), **transformer** (contrat, types, règles, quarantaine), **charger** (écrire dans l'entrepôt).
> - Le **dépôt brut** n'est jamais modifié : c'est ce qui permet de refaire un calcul.
> - Les lignes douteuses vont en **quarantaine avec leur motif**, elles ne disparaissent pas.
> - Un filigrane de date rate les **corrections** ; la **fusion sur la clé naturelle** les absorbe.
> - Un chargement est **idempotent** quand le relancer donne le même état ; on le vérifie par une empreinte.
> - Le manifeste de la livraison (nombre de lignes annoncé) est le contrôle à la source le moins cher.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 à 2.3, exercices 2.1 à 2.4.
