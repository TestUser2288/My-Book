# Chapitre 2 : ETL et automatisation des flux de travail

> « Un chiffre fabriqué à la main n'est juste que les lundis où personne n'est en congé. »


## Le lundi où vous n'étiez pas là

Chaque lundi matin, la gérante reçoit le point de la semaine : le chiffre d'affaires du mois en cours, par canal, avec les commandes et le panier moyen. Depuis le début de l'année, c'est vous qui le fabriquez. Le système de commandes dépose un fichier par mois ; vous l'ouvrez, vous corrigez ce qui doit l'être (une date mal écrite, une colonne renommée, quelques lignes en double), vous collez le résultat dans le classeur de suivi, vous actualisez les tableaux croisés, puis vous envoyez le message. Quarante-cinq minutes, quand tout va bien.

Un lundi de novembre, vous êtes en congé. Un collègue prend le relais, de bonne foi. Il ouvre le fichier du mois d'octobre, livré le 3 novembre, il le colle, il envoie. Personne ne voit rien. Voici ce que le fichier contenait vraiment.

```python
chemin = os.path.join(DEPOT, "commandes_2025-10.csv")
recu = pd.read_csv(chemin)
print("lignes dans le fichier livré :", len(recu))
print("chiffre d'affaires du fichier :", fr(recu["montant"].sum(), 0), "€")
print("chiffre d'affaires réel d'octobre :", fr(VERITE["par_mois"]["2025-10"]["total_original"], 0), "€")
print("écart :", fr((recu["montant"].sum() / VERITE["par_mois"]["2025-10"]["total_original"] - 1) * 100, 1, True), "%")
```
<!--sortie-->
```text
lignes dans le fichier livré : 2249
chiffre d'affaires du fichier : 102 601 €
chiffre d'affaires réel d'octobre : 120 064 €
écart : −14,5 %
```

Le fichier s'est **interrompu en route** : il manque environ une ligne sur sept, donc près de quinze pour cent du chiffre d'affaires. L'exportateur annonçait pourtant 2 645 lignes, mais personne ne l'a comparé à ce qu'il a reçu. La gérante a décidé, pendant trois semaines, avec un chiffre d'octobre trop faible de près de 17 500 €. Aucune faute de calcul : un **processus** qui ne contrôle rien et qui dépend d'une personne.

> 💡 **Intuition.** Ce n'est pas la personne en congé qui a failli, c'est la chaîne. Une chaîne manuelle repose sur le regard de quelqu'un qui « sent » que quelque chose cloche ; un programme n'a que les contrôles qu'on lui a écrits. L'automatisation n'est donc pas « faire plus vite » : c'est **écrire ce que le regard faisait sans le dire**.

Ce chapitre construit, pas à pas, la chaîne qui aurait évité cela. Elle lit les fichiers qui arrivent, les contrôle, met de côté ce qui est douteux, charge le reste dans un entrepôt sans jamais le charger deux fois, s'exécute à heure fixe, raconte ce qu'elle fait dans un journal, prévient quand elle échoue, et envoie le rapport. Chaque pièce est simple. Le travail est de les faire tenir ensemble.

## Le chemin de ce chapitre

| Section | La question de départ | Ce que vous saurez faire |
|---|---|---|
| **2.1 Principes de l'ETL** | « Comment passe-t-on d'un fichier livré à une table fiable ? » | extraire, transformer, charger ; chargement complet ou incrémental ; **idempotence** (relancer sans doubler) |
| **2.2 Scripts planifiés et pipelines** | « Et si cela se lançait tout seul, le 3 de chaque mois ? » | découper en étapes, paramétrer, lancer en ligne de commande, planifier (cron, APScheduler), rattraper des mois manqués, éviter deux exécutions simultanées |
| **2.3 Erreurs et journalisation** | « Comment sait-on que ça a marché, et pourquoi ça n'a pas marché ? » | journal, table des exécutions, quarantaine, contrôles avant et après, reprises, **alertes utiles** |
| **➕ 2.4 Outils d'orchestration** | « Existe-t-il quelque chose de plus solide que mon script ? » | ce que font dbt, Airflow et les outils bas-code (décrits, non exécutés) ; deux jouets exécutés pour comprendre le principe |
| **➕ 2.5 Automatisation robotisée** | « Et quand il n'y a ni fichier ni API ? » | quand un robot qui manipule un écran se justifie, et pourquoi il reste le dernier recours |
| **➕ 2.6 API et diffusion** | « Comment lire un service en ligne, et envoyer le rapport ? » | lire une API paginée avec reprises, gérer ses secrets, envoyer un e-mail avec pièce jointe, penser à la diffusion |

Les sections 2.1 à 2.3 forment le parcours essentiel et se lisent dans l'ordre. Les trois suivantes sont facultatives et indépendantes l'une de l'autre.

## Les données du chapitre

> 📦 **Données du chapitre.** Un **dépôt** de fichiers livrés par le système de commandes de la boutique, dans `donnees/ch02-depot/`, et deux référentiels du volume III (`clients.csv`, `produits.csv`). Tout est **simulé**, avec une graine fixe (script `build/outils_ch02.py`).

Le dépôt contient un fichier par mois de 2025 (`commandes_2025-01.csv` à `commandes_2025-12.csv`), une ligne par **ligne de commande** (identifiant de ligne et de commande, date, client, canal, produit, quantité, montant TTC), et un **manifeste** qui indique, pour chaque fichier, sa date de livraison et le nombre de lignes que l'exportateur dit avoir écrites. Le total des lignes d'origine est celui du volume III : 29 827 lignes, 12 946 commandes, 1 324 764 € de chiffre d'affaires TTC en 2025.

Trois mois ont été livrés **deux fois** : un premier fichier défectueux, puis un renvoi avec le suffixe `_v2`.

```python
man = P.manifeste(DEPOT)
print("fichiers :", len(man), "| mois :", man["mois"].nunique(), "| lignes annoncées au total :", int(man["lignes_annoncees"].sum()))
print(man.groupby("mois").size().loc[lambda s: s > 1].rename("fichiers").to_string())
```
<!--sortie-->
```text
fichiers : 15 | mois : 12 | lignes annoncées au total : 37074
mois
2025-03    2
2025-09    2
2025-10    2
```

Les fichiers ne sont pas tous propres, et c'est voulu : un format qui change en cours d'année, un encodage différent, un fichier vide, des lignes en double, des clients inconnus. Vous les découvrirez en chemin, comme dans la vraie vie, et leur liste complète (la « vérité programmée ») sera donnée dans le bilan du chapitre pour que vous puissiez juger ce que votre pipeline a trouvé.

> ⚠️ **Piège : un exemple à taille réelle, pas un jouet.** Les fichiers sont petits (moins de 200 Ko), mais les défauts sont de ceux que l'on rencontre vraiment. Un pipeline qui ne traite que le cas propre n'a pas été testé.

## Ce que ce chapitre suppose

- **SQL et Python** : volume I, chapitres 3 et 4 (nous utilisons **DuckDB**, une base de données qui tient dans un fichier et s'interroge en SQL, comme entrepôt local ; volume I, section 3.6.4).
- **Nettoyage et contrôles de qualité** : volume II, chapitre 1 (formats, dates, doublons), section 3.2 (contrôles de validation) et section 3.5 (pandera). Ici, on ne refait pas ces contrôles : on les **branche dans une chaîne qui se déclenche seule**.
- **Rapport automatisé simple** : volume IV, section 4.4 (un programme qui produit le rapport de la semaine). Ce chapitre en est le prolongement industriel : ce qu'il faut autour pour qu'on puisse **lui faire confiance un lundi de congé**.
- **Entrepôt de données** : chapitre 1 de ce volume. Nous y renvoyons pour le schéma en étoile (section 1.2) et la granularité (section 1.3). La cible de ce chapitre en est une version minimale, expliquée au fil du texte.

## Ce qui est exécuté, et ce qui ne l'est pas

Tout le code de ce chapitre tourne sur une machine ordinaire, hors ligne : l'entrepôt est un fichier DuckDB créé dans un dossier temporaire, la « planification » utilise la bibliothèque APScheduler sur des échéances de quelques secondes, l'API est un petit service lancé localement sur le port 20120 puis arrêté, le serveur d'e-mail est un serveur de **test** local sur le port 20130 : aucun message ne quitte la machine. Les produits qui ne sont pas installés ici (dbt, Airflow, Power Automate, UiPath, les entrepôts infonuagiques) sont **décrits, jamais exécutés**, et chaque extrait de code qui les concerne porte la mention « non exécuté ». Les menus et les noms de paramètres de ces produits changent d'une version à l'autre : vérifiez-les dans la documentation de votre version.


## 2.1 Principes de l'ETL

Un pipeline de données est une chaîne qui prend des fichiers ou des tables qu'on ne contrôle pas et en fait des tables sur lesquelles on peut s'appuyer. Cette section donne le vocabulaire et les trois idées qui font la différence entre un script qui marche une fois et une chaîne qui tient : on **sépare** lecture, transformation et chargement ; on **n'écrit jamais** dans la copie brute ; et surtout on rend le chargement **idempotent**, c'est-à-dire qu'on peut le relancer sans en changer le résultat.

### 2.1.1 Trois verbes et une chaîne

**ETL** est le sigle de trois verbes : **E**xtract (extraire les données de leur source), **T**ransform (les mettre en forme et les contrôler), **L**oad (les charger dans l'entrepôt). Ces trois gestes se retrouvent dans tous les systèmes, sous des habits très différents : un notebook, un script planifié, un outil graphique ou un service infonuagique.


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

```text
          étape  ajout simple (€)  fusion (€)
1       janvier          89178.95    89178.95
2       février         161821.39   161821.39
3          mars         256012.48   256012.48
4  mars relancé         350203.57   256012.48
5  mars corrigé         439990.87   251608.69
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


## 2.2 Scripts planifiés et pipelines

La section précédente a donné les pièces : lire, contrôler, charger. Pour que cela tourne **sans vous**, il reste trois choses : découper le travail en étapes qui s'enchaînent, le rendre pilotable de l'extérieur (une ligne de commande, des paramètres), et le déclencher à heure fixe, en sachant le relancer et le rattraper quand il a manqué un rendez-vous.

### 2.2.1 Un pipeline est une suite d'étapes qui dépendent les unes des autres

Un pipeline n'est pas un long script, c'est une suite d'**étapes**, chacune faisant une chose et une seule. Chaque étape reçoit ce que la précédente a produit et rend quelque chose à la suivante. Cette découpe a trois avantages : on teste une étape isolément, on la relance seule quand elle a échoué, et on sait toujours **où** le travail s'est arrêté.

Nos étapes sont celles du schéma de la section 2.1 : repérer le fichier du mois, l'extraire, le transformer, charger les lignes valides, mettre les autres en quarantaine, contrôler le résultat, publier. On les écrit comme un **graphe de dépendances** : pour chaque étape, la liste de celles qui doivent être terminées avant elle.

```python
from graphlib import TopologicalSorter
GRAPHE = {"repérer": set(), "extraire": {"repérer"}, "transformer": {"extraire"}, "quarantaine": {"transformer"},
          "charger": {"transformer"}, "contrôler": {"charger"}, "publier": {"contrôler"}}
print(list(TopologicalSorter(GRAPHE).static_order()))
```
<!--sortie-->
```text
['repérer', 'extraire', 'transformer', 'quarantaine', 'charger', 'contrôler', 'publier']
```


![Le graphe des étapes du pipeline mensuel : chaque flèche dit « l'étape de droite ne peut commencer que quand celle de gauche est terminée ». La quarantaine et le chargement sont indépendants l'un de l'autre. Schéma dessiné.](figures/ch02-dag-pipeline.png)

Le module standard `graphlib` fournit l'ordre d'exécution : une étape n'apparaît jamais avant celles dont elle dépend. On l'appelle un **graphe orienté acyclique** (*DAG*, en anglais) : orienté parce que les flèches ont un sens, acyclique parce qu'on ne peut pas revenir en arrière, sans quoi une étape attendrait sa propre fin. Ce vocabulaire reviendra en section 2.4, car il est celui de tous les orchestrateurs.

Les étapes ne se contentent pas de s'enchaîner, elles se **paramètrent**. Notre pipeline travaille pour un mois donné, sur un dossier de dépôt donné, avec un seuil de rejets donné : ce sont des paramètres, pas des constantes enfouies dans le code. Voici la version la plus simple de la chaîne, qui prend le mois et la cible en arguments.

```python
CONFIG = {"depot": DEPOT, "seuil_rejets": 0.02}

def derniere_version(depot, mois):
    m = P.manifeste(depot)
    return m[m["mois"] == mois].sort_values("date_livraison").iloc[-1]

def pipeline(mois, cible, config=CONFIG):
    f = derniere_version(config["depot"], mois)
    valides, rejets = transformer(extraire(os.path.join(config["depot"], f["fichier"])), clients)
    inserees, majs = P.charger(cible, valides, f["fichier"])
    return {"fichier": f["fichier"], "insérées": inserees, "mises à jour": majs, "rejetées": len(rejets)}
```

La règle « on prend la **dernière version livrée** du mois » est une décision de métier, écrite à un seul endroit : quand le renvoi de mars arrive, la chaîne le préfère automatiquement au premier fichier. Essayons deux fois de suite sur mars, sur un entrepôt neuf.

```python
ent2 = P.nouvel_entrepot()
cl2 = P.charger_dimensions(ent2)
print(pipeline("2025-03", ent2))
print(pipeline("2025-03", ent2))
```
<!--sortie-->
```text
{'fichier': 'commandes_2025-03_v2.csv', 'insérées': 2023, 'mises à jour': 0, 'rejetées': 5}
{'fichier': 'commandes_2025-03_v2.csv', 'insérées': 0, 'mises à jour': 2023, 'rejetées': 5}
```

Le deuxième appel ne charge plus rien de nouveau et remplace les 2 023 lignes déjà présentes : c'est l'idempotence de la section 2.1, que l'on retrouve ici sans y penser. Un pipeline **paramétré par le mois** et **idempotent** peut être rejoué pour n'importe quel mois, dans n'importe quel ordre, autant de fois qu'on veut : c'est la propriété qui rend possible tout le reste de la section.

> 💡 **Intuition.** Les paramètres sont les boutons du pipeline, l'idempotence est son filet de sécurité. Sans paramètres, on ne peut pas rejouer un mois ancien ; sans idempotence, on n'ose pas le faire.

### 2.2.2 Piloter de l'extérieur : la ligne de commande

Un planificateur ne sait pas appeler une fonction Python : il sait **lancer une commande** et lire son **code de sortie** (0 si tout va bien, autre chose sinon). Il faut donc donner à notre pipeline une porte d'entrée en ligne de commande. Le module standard `argparse` s'en charge, avec une aide en prime.

```python
import argparse
parseur = argparse.ArgumentParser(prog="pipeline", description="Charge les commandes livrées par mois dans l'entrepôt.")
parseur.add_argument("--depot", default="donnees/ch02-depot", help="dossier des fichiers livrés")
parseur.add_argument("--mois", help="un seul mois (AAAA-MM) ; sinon tous les mois")
parseur.add_argument("--simuler", action="store_true", help="n'écrit rien : liste ce qui serait fait")
parseur.add_argument("--seuil-rejets", type=float, default=0.02, help="part maximale de lignes rejetées")
print(parseur.parse_args(["--mois", "2025-03", "--simuler"]))
```
<!--sortie-->
```text
Namespace(depot='donnees/ch02-depot', mois='2025-03', simuler=True, seuil_rejets=0.02)
```

Le script complet est `build/outils_ch02.py` (sous-commande `pipeline`) ; il enveloppe la chaîne que nous construisons. Lançons-le comme le ferait un planificateur : dans un processus à part, en lisant sa sortie et son code de sortie. D'abord en **simulation**, qui n'écrit rien.

```python
import subprocess
def lancer(*arguments):
    r = subprocess.run([sys.executable, "build/outils_ch02.py", "pipeline", *arguments], capture_output=True, text=True)
    print(r.stdout.rstrip())
    print("code de sortie :", r.returncode)
lancer("--mois", "2025-03", "--simuler")
```
<!--sortie-->
```text
[simulation] chargerait commandes_2025-03_v2.csv (2028 lignes annoncées)
code de sortie : 0
```

L'option `--simuler` (on dit aussi *dry run*) est l'une des plus utiles que l'on puisse offrir : avant de lancer une opération sur douze mois, on voit ce qu'elle ferait. Elle n'a de valeur que si elle ne fait **réellement rien d'autre** ; ici, elle sort avant toute écriture. Maintenant pour de vrai, puis avec un seuil de rejets très strict, qui doit faire échouer novembre (25 lignes en double sur plus de 3 400).

```python
lancer("--mois", "2025-03")
lancer("--mois", "2025-11", "--seuil-rejets", "0.005")
```
<!--sortie-->
```text
2025-04-14 06:00:06 INFO    début commandes_2025-03_v2.csv
2025-04-14 06:00:09 INFO    fin commandes_2025-03_v2.csv : 2023 insérées, 0 mises à jour, 5 rejetées
code de sortie : 0
2025-12-03 06:00:06 INFO    début commandes_2025-11.csv
2025-12-03 06:00:09 ERROR   commandes_2025-11.csv : ControleEchoue : 25 lignes rejetées sur 3484 (seuil 0,50 %)
code de sortie : 1
```

Le code de sortie **1** du second appel est l'information essentielle pour le planificateur : c'est lui qui déclenche une alerte, une nouvelle tentative ou un arrêt. Un script qui échoue mais rend 0 est le pire des scripts, car personne n'est prévenu.

> ⚠️ **Piège : le script qui avale ses erreurs.** Une exception attrapée par un `try/except` qui se contente d'afficher un message laisse le script se terminer « normalement ». Dans un pipeline, une erreur doit soit être **traitée** (on sait quoi faire), soit **remonter** jusqu'au code de sortie.

### 2.2.3 Planifier : le cron

Sous Linux et macOS, le planificateur historique s'appelle **cron**. On lui donne, pour chaque tâche, une **expression** de cinq champs qui dit *quand* la lancer, suivie de la commande. Windows a le Planificateur de tâches, qui fait la même chose avec des fenêtres.


![Les cinq champs d'une expression cron, ici « 0 6 3 * * » : minute 0, heure 6, jour du mois 3, tous les mois, tous les jours de la semaine. Schéma dessiné.](figures/ch02-cron.png)

Chaque champ accepte les mêmes écritures.

| Écriture | Sens | Exemple | Lecture |
|---|---|---|---|
| `*` | toutes les valeurs | `0 6 * * *` | tous les jours à 6 h |
| `a,b` | liste | `0 6,18 * * *` | à 6 h et à 18 h |
| `a-b` | plage | `0 6 * * 1-5` | à 6 h, du lundi au vendredi |
| `*/n` | pas | `*/15 8-18 * * *` | toutes les 15 minutes, de 8 h à 18 h |

Pour comprendre, rien ne vaut l'écriture d'un petit évaluateur : une fonction qui, pour une expression et une date, donne la **prochaine échéance**. Elle tient en une vingtaine de lignes (le code est dans `build/outils_ch02.py`). Pour chaque champ, elle calcule l'ensemble des valeurs permises (`*`, listes, plages, pas) ; puis elle parcourt les jours à partir de la date donnée et renvoie la première minute qui satisfait les cinq champs. Une règle mérite d'être connue : quand le jour du mois **et** le jour de la semaine sont tous deux précisés, le cron classique déclenche si **l'un ou l'autre** convient.


Le test : à partir du mercredi 5 novembre 2025 à 10 h 17, quand se déclenchent nos quatre exemples ?

```python
depuis = datetime(2025, 11, 5, 10, 17)
for expr in ["0 6 3 * *", "0 6 * * 1", "*/15 8-18 * * 1-5", "30 7 1 * *"]:
    print(f"{expr:20s}", prochaine_echeance(expr, depuis), "|", prochaine_echeance(expr, prochaine_echeance(expr, depuis)))
```
<!--sortie-->
```text
0 6 3 * *            2025-12-03 06:00:00 | 2026-01-03 06:00:00
0 6 * * 1            2025-11-10 06:00:00 | 2025-11-17 06:00:00
*/15 8-18 * * 1-5    2025-11-05 10:30:00 | 2025-11-05 10:45:00
30 7 1 * *           2025-12-01 07:30:00 | 2026-01-01 07:30:00
```

Notre évaluateur raisonne comme le cron classique. La bibliothèque APScheduler, que nous utilisons juste après, propose aussi `CronTrigger.from_crontab`. On pourrait croire qu'elle donne les mêmes réponses. Comparons.

```python
from apscheduler.triggers.cron import CronTrigger
depuis_utc = depuis.replace(tzinfo=timezone.utc)
for expr in ["0 6 3 * *", "0 6 * * 1", "0 0 13 * 5"]:
    aps = CronTrigger.from_crontab(expr, timezone="UTC").get_next_fire_time(None, depuis_utc)
    print(f"{expr:12s} cron classique : {prochaine_echeance(expr, depuis)} | APScheduler : {aps.replace(tzinfo=None)}")
```
<!--sortie-->
```text
0 6 3 * *    cron classique : 2025-12-03 06:00:00 | APScheduler : 2025-12-03 06:00:00
0 6 * * 1    cron classique : 2025-11-10 06:00:00 | APScheduler : 2025-11-11 06:00:00
0 0 13 * 5   cron classique : 2025-11-07 00:00:00 | APScheduler : 2025-12-13 00:00:00
```

Les deux derniers résultats **diffèrent**, et ce n'est pas un bogue de notre évaluateur. Dans la version d'APScheduler utilisée ici (3.11), les numéros de jours de la semaine de `from_crontab` **commencent au lundi** (0 = lundi, donc `1` désigne le mardi), alors que le cron classique commence au dimanche ; et quand le jour du mois **et** le jour de la semaine sont tous deux précisés, APScheduler exige **les deux** (un 13 qui tombe le jour numéro 5 de sa propre numérotation, soit un samedi, d'où le 13 décembre), alors que le cron classique accepte **l'un ou l'autre** (le 13 **ou** un vendredi, d'où le vendredi 7 novembre).

> ⚠️ **Piège : deux « cron » qui ne se ressemblent pas.** Une expression recopiée d'un outil à un autre peut se déclencher un autre jour sans erreur. Deux précautions : écrire les jours **en toutes lettres** (`mon`, `tue`…) quand l'outil le permet, et **calculer les prochaines échéances** pour les lire avant de mettre en production. Vérifiez la convention dans la documentation de votre version.

Quelques conseils d'usage, qui épargnent des soirées de dépannage.

- **L'heure.** Choisissez un fuseau explicite (le plus sûr : UTC) et évitez les créneaux de la nuit du changement d'heure : à 2 h 30, certains jours n'existent pas et d'autres existent deux fois.
- **La marge.** Le fichier est « livré le 3 » : planifier le chargement le 3 à 6 h, c'est parier que la livraison est faite avant. On préfère un chargement plus tardif, ou, mieux, un pipeline qui **vérifie la présence du fichier** et réessaie plus tard (section 2.3).
- **Le propriétaire.** Chaque tâche planifiée a un nom, une personne responsable et une adresse où se plaindre. Une tâche sans propriétaire est une tâche qu'on découvrira le jour où elle casse.

### 2.2.4 Planifier depuis Python : APScheduler

Quand le planificateur du système n'est pas disponible, ou quand on veut que le calendrier fasse partie du programme, on peut planifier **depuis Python**. La bibliothèque **APScheduler** lance des tâches dans un fil d'exécution à part, selon un déclencheur (intervalle, cron, date unique). Pour l'illustrer sans attendre un mois, utilisons une échéance d'**une seconde** et laissons trois exécutions se produire avant d'arrêter proprement.

```python
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
tops, fini = [], threading.Event()

def tache():
    tops.append(time.monotonic())
    if len(tops) == 3:
        fini.set()

planif = BackgroundScheduler()
planif.add_job(tache, IntervalTrigger(seconds=1))
planif.start(); fini.wait(timeout=10); planif.shutdown(wait=True)
print(len(tops), "exécutions, écarts arrondis (s) :", [round(b - a) for a, b in zip(tops, tops[1:])])
```
<!--sortie-->
```text
3 exécutions, écarts arrondis (s) : [1, 1]
```

Trois détails de ce code comptent plus que la planification elle-même. D'abord, on **attend un signal** (`fini.wait`) plutôt qu'un délai fixe, pour que l'exemple soit fiable. Ensuite, on arrête avec `shutdown(wait=True)`, qui laisse finir la tâche en cours : un arrêt brutal pourrait couper un chargement en plein milieu. Enfin, le planificateur vit **dans le processus** : s'il s'arrête, plus rien ne se déclenche. C'est son principal défaut par rapport à cron, géré par le système.

Trois réglages d'APScheduler méritent d'être connus, car ils décident de ce qui arrive quand le calendrier **se heurte à la réalité**.

| Réglage | Question à laquelle il répond | Valeur prudente pour un chargement |
|---|---|---|
| `max_instances` | Que faire si la tâche précédente n'est pas finie quand l'échéance revient ? | `1` : on ne lance pas deux chargements en parallèle |
| `coalesce` | Plusieurs échéances manquées (machine éteinte) : en rejouer une seule, ou toutes ? | `True` : une seule suffit, car le chargement est idempotent |
| `misfire_grace_time` | De combien de temps une échéance en retard est-elle encore valable ? | quelques heures : un chargement tardif vaut mieux que pas de chargement |

Vérifions le premier. Une tâche lente (une seconde) est planifiée toutes les 0,4 seconde, avec `max_instances=1`. Elle ne doit jamais tourner en double, et les échéances qui tombent pendant qu'elle travaille doivent être **refusées** (et signalées, jamais perdues en silence).

```text
jamais deux en même temps : True | échéances refusées signalées : True
```

### 2.2.5 Relancer et rattraper

Le calendrier a des trous : la machine était éteinte, le fichier n'est arrivé que le 9, le planificateur a planté. Un bon pipeline sait **combler les trous** sans qu'on lui dise lesquels. C'est le **rattrapage** (*backfill*).

Le principe est de **comparer ce qui devrait être chargé à ce qui l'a été**. Ce qui devrait l'être : la dernière version livrée de chaque mois du manifeste. Ce qui l'a été : les exécutions réussies, que notre chaîne enregistre dans une table `executions` (section 2.3). La différence est la liste de ce qu'il reste à faire.

Imaginons que le planificateur n'ait fonctionné que de janvier à mai, avant une panne de machine.

```python
h2 = P.Horloge("2025-06-04 06:00:00")
dernier = man.sort_values("date_livraison").groupby("mois").tail(1)
for _, f in dernier.head(5).iterrows():
    P.executer(ent2, os.path.join(DEPOT, f["fichier"]), int(f["lignes_annoncees"]), cl2, h2)
print(P.a_rattraper(ent2, DEPOT)[["mois", "fichier"]].to_string(index=False))
```
<!--sortie-->
```text
   mois                  fichier
2025-06    commandes_2025-06.csv
2025-07    commandes_2025-07.csv
2025-08    commandes_2025-08.csv
2025-09 commandes_2025-09_v2.csv
2025-10 commandes_2025-10_v2.csv
2025-11    commandes_2025-11.csv
2025-12    commandes_2025-12.csv
```

La liste est celle des sept mois de juin à décembre. Il suffit de les rejouer : comme le chargement est idempotent, on n'a pas à se demander si l'un d'eux avait été **partiellement** chargé.

```text
à rattraper : 0 | lignes chargées : 29827 | chiffre d'affaires TTC : 1 324 763,72 €
```

Après rattrapage, plus rien n'est à faire, et l'entrepôt contient **exactement** les 29 827 lignes d'origine et le chiffre d'affaires du volume III (1 324 763,72 €) : les lignes orphelines, les avoirs et les doublons ont été mis en quarantaine, et le total de ce qui reste est juste, au centime. La section 2.3 revient sur ce calcul de rapprochement.

> 💡 **Intuition : planifier, c'est facile ; rattraper, c'est ce qui fait la robustesse.** Un pipeline qui ne sait que « faire le travail du jour » dépend de sa propre ponctualité. Un pipeline qui sait « faire tout ce qui manque » se moque d'avoir raté trois rendez-vous.

### 2.2.6 Éviter les exécutions simultanées

Dernier danger : deux exécutions en même temps. Cela arrive plus souvent qu'on ne croit : un chargement qui dure plus longtemps que prévu et la tâche suivante qui démarre, un collègue qui relance à la main pendant que le planificateur tourne. Deux processus qui écrivent dans la même table donnent, au mieux, une erreur, au pire un état incohérent.

La parade est un **verrou**. Sous Linux, un verrou de fichier (`flock`) a l'avantage d'être **libéré automatiquement** si le processus meurt : pas de verrou orphelin qui bloquerait tout jusqu'à intervention humaine.

```python
import fcntl, contextlib

@contextlib.contextmanager
def verrou(chemin):
    with open(chemin, "w") as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("une exécution est déjà en cours")
        yield
```

Faisons-le jouer : une première exécution prend le verrou et travaille, une seconde essaie de démarrer pendant ce temps.

```text
{'B': 'refusée : une exécution est déjà en cours', 'A': 'terminée'}
```

La seconde exécution est **refusée avec un message clair** plutôt que de s'exécuter en parallèle. Dans un vrai déploiement, le verrou est un fichier à un emplacement fixe (par exemple dans le dossier temporaire du système, au nom du pipeline) ; ici, il se trouve dans le dossier temporaire de l'entrepôt de démonstration, supprimé à la fin.

> 🧭 **En pratique : le tableau de ce qu'il faut régler avant la mise en production.**
> - **Qui** lance (un compte de service, pas un compte personnel) et **où** (une machine toujours allumée, sauvegardée).
> - **Quand**, dans quel fuseau, avec quelle marge après la livraison des fichiers.
> - **Comment on relance** : à la main, avec un mois en paramètre, sans rien casser.
> - **Que se passe-t-il si deux exécutions se chevauchent**, ou si l'une est interrompue.
> - **Qui est prévenu** quand ça échoue (section 2.3).

> ✅ **À retenir.**
> - Un pipeline est une suite d'**étapes** qui dépendent les unes des autres : un **graphe** orienté sans cycle.
> - Il se **paramètre** (mois, dossier, seuils) et se lance en **ligne de commande**, avec un code de sortie fiable et une option de **simulation**.
> - **cron** (ou le planificateur du système) lance ; APScheduler planifie depuis Python. Les conventions d'écriture diffèrent d'un outil à l'autre : **calculez les prochaines échéances** avant de faire confiance à une expression.
> - Le **rattrapage** compare « ce qui devrait être chargé » à « ce qui l'a été » ; il n'est sûr que si le chargement est **idempotent**.
> - Un **verrou** empêche deux exécutions simultanées ; préférez un verrou que le système libère si le processus meurt.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.4, exercices 2.5 à 2.7.


## 2.3 Gestion des erreurs et journalisation

Un pipeline qui marche le jour de sa mise en service ne prouve rien. Ce qui compte, c'est ce qu'il fait **le jour où quelque chose ne va pas**, et la rapidité avec laquelle vous en êtes informé et pouvez comprendre. Cette section équipe notre chaîne de ce qui lui manque : un **journal** qui raconte, une **table des exécutions** qui compte, une **quarantaine** qui garde ce qui est douteux, des **contrôles** avant et après le chargement, des **reprises** pour les pannes passagères, et des **alertes** qui ne crient que quand il le faut.

### 2.3.1 Ce qui peut mal tourner

Avant d'ajouter des garde-fous, il faut savoir contre quoi. Les ennuis d'un pipeline se rangent en cinq familles, qui appellent des réponses différentes.

| Famille | Exemples dans notre dépôt | Réponse |
|---|---|---|
| **La source** | fichier absent, vide (septembre), tronqué (octobre), renvoyé (mars) | contrôle à la source (manifeste), alerte, attente d'un renvoi |
| **Le format** | colonne renommée (mai), dates en `JJ/MM/AAAA` (juillet), encodage (août) | contrat de données, tolérance **écrite**, échec clair sinon |
| **Les lignes** | doublons (novembre), clients inconnus, montants négatifs | quarantaine avec motif, seuil de tolérance |
| **Le traitement** | bogue, mémoire insuffisante, base verrouillée | exceptions, reprises si la panne est passagère, journal |
| **L'orchestration** | exécution en double, exécution oubliée, planificateur arrêté | verrou (section 2.2), rattrapage, alerte « rien ne s'est passé » |

Mettons la chaîne complète à l'épreuve : on **rejoue l'histoire** de l'année, livraison après livraison, dans l'ordre où les fichiers sont arrivés. L'exécution complète (`P.executer`) contient tout ce qu'on va détailler : lecture, contrat, contrôles, transformation, chargement en transaction, quarantaine, trace.

```python
ent3 = P.nouvel_entrepot()
cl3 = P.charger_dimensions(ent3)
h3 = P.Horloge()
journal_fichier = os.path.join(P.dossier_de(ent3), "pipeline.log")
log, tampon = P.journal(h3, fichier=journal_fichier)
P.rejouer(ent3, DEPOT, cl3, h3, log)
print(ent3.execute("SELECT statut, count(*) AS exécutions FROM executions GROUP BY ALL ORDER BY 1").df().to_string(index=False))
```
<!--sortie-->
```text
statut  exécutions
 ECHEC           2
SUCCES          13
```

Sur les quinze livraisons, **deux ont échoué** : le fichier vide de septembre et le fichier tronqué d'octobre. Dans les deux cas, **rien n'a été écrit** dans l'entrepôt, et les renvois du 9 octobre et du 6 novembre ont ensuite été chargés normalement. C'est ce que le collègue en congé de l'introduction aurait voulu : un échec **visible et sans conséquence** plutôt qu'un chiffre faux.

### 2.3.2 Le journal : raconter ce qu'on fait

Le **journal** (*log*) est le récit, ligne à ligne, de ce que le pipeline a fait. Le module standard `logging` de Python en offre l'essentiel : des **niveaux** de gravité, des **gestionnaires** qui décident où écrire (écran, fichier, serveur), et des **formateurs** qui décident de l'apparence.

| Niveau | Ce qu'on y met | Exemple |
|---|---|---|
| `DEBUG` | le détail technique, utile seulement pour comprendre un bogue | « requête SQL envoyée » |
| `INFO` | la marche normale : début, fin, nombres de lignes | « fin avril : 2 225 lignes chargées » |
| `WARNING` | quelque chose d'inhabituel mais sans gravité | « 25 lignes en quarantaine » |
| `ERROR` | une étape a échoué, le pipeline s'arrête ou saute | « fichier vide » |
| `CRITICAL` | le pipeline entier est hors service | « entrepôt injoignable » |

On règle le niveau du journal : à `INFO`, les messages `DEBUG` sont ignorés. Voici le principe, avec un journal qui écrit dans un tampon mémoire pour qu'on en voie le contenu.

```python
flux = io.StringIO()
demo = logging.getLogger("demo")
demo.setLevel(logging.INFO)
gestionnaire = logging.StreamHandler(flux)
gestionnaire.setFormatter(logging.Formatter("%(levelname)-7s %(message)s"))
demo.addHandler(gestionnaire)
demo.debug("requête envoyée")
demo.info("fin avril : %d lignes chargées", 2225)
demo.warning("%d lignes en quarantaine", 25)
demo.error("fichier vide")
print(flux.getvalue())
```
<!--sortie-->
```text
INFO    fin avril : 2225 lignes chargées
WARNING 25 lignes en quarantaine
ERROR   fichier vide
```

Le message `DEBUG` n'apparaît pas : il est sous le niveau réglé. En production on ajoute au format la date et l'heure (`%(asctime)s`), le nom du programme et, pour les journaux que lira une machine, une structure fixe.

Un journal en **texte libre** se lit bien à l'œil et mal à la machine. Un journal **structuré**, une ligne JSON par événement, permet de le **filtrer** (« tous les échecs d'octobre ») et de le **compter** sans expression régulière. Un formateur de quelques lignes suffit.

```python
class FormatJson(logging.Formatter):
    def format(self, record):
        return json.dumps({"niveau": record.levelname, "mois": getattr(record, "mois", ""), "message": record.getMessage()}, ensure_ascii=False)

gestionnaire.setFormatter(FormatJson())
demo.info("fin %s : %d lignes chargées", "commandes_2025-04.csv", 2225, extra={"mois": "2025-04"})
demo.error("%s est vide", "commandes_2025-09.csv", extra={"mois": "2025-09"})
print("\n".join(flux.getvalue().splitlines()[-2:]))
```
<!--sortie-->
```text
{"niveau": "INFO", "mois": "2025-04", "message": "fin commandes_2025-04.csv : 2225 lignes chargées"}
{"niveau": "ERROR", "mois": "2025-09", "message": "commandes_2025-09.csv est vide"}
```

Pour que les sorties de ce livre soient **identiques à chaque exécution**, les journaux de notre pipeline utilisent une **horloge factice** qui avance de trois secondes à chaque lecture (et saute à la date de livraison de chaque fichier). Dans la réalité, ce serait l'heure du système. Voici ce que le journal de l'année a écrit autour de l'échec d'octobre.

```python
extrait = [l for l in tampon.getvalue().splitlines() if "2025-10-03" <= l[:10] <= "2025-11-06"]
print("\n".join(extrait))
```
<!--sortie-->
```text
2025-10-03 06:00:06 INFO    début commandes_2025-09.csv
2025-10-03 06:00:12 ERROR   commandes_2025-09.csv : SourceVide : commandes_2025-09.csv est vide
2025-10-09 06:00:06 INFO    début commandes_2025-09_v2.csv
2025-10-09 06:00:12 INFO    fin commandes_2025-09_v2.csv : 2521 insérées, 0 mises à jour, 1 rejetées
2025-11-03 06:00:06 INFO    début commandes_2025-10.csv
2025-11-03 06:00:12 ERROR   commandes_2025-10.csv : ControleEchoue : 2249 lignes lues pour 2645 annoncées
2025-11-06 06:00:06 INFO    début commandes_2025-10_v2.csv
2025-11-06 06:00:12 INFO    fin commandes_2025-10_v2.csv : 2644 insérées, 0 mises à jour, 1 rejetées
```


![Le journal du pipeline autour de l'échec du fichier d'octobre : le premier fichier est refusé car il contient 2 249 lignes pour 2 645 annoncées, puis le renvoi du 6 novembre est chargé normalement. Capture réelle d'un journal généré localement, rendu en HTML (le niveau est écrit en toutes lettres et en couleur).](figures/ch02-journal.png)

Un bon message de journal répond à quatre questions : **quoi** (quelle étape, quel fichier), **combien** (nombres de lignes lues, chargées, rejetées), **avec quel résultat** et, en cas d'erreur, **pourquoi**. Il ne contient **jamais** de secret (mot de passe, clé d'accès) ni de donnée personnelle (adresse e-mail, nom d'un client) : un journal circule bien plus que la base.

> ⚠️ **Piège : le journal qui dit tout ou rien.** Un journal bavard cache l'essentiel dans le bruit ; un journal silencieux ne dit rien le jour où l'on en a besoin. Règle pratique : **une ligne au début, une ligne à la fin, une ligne par décision ou anomalie**, avec les nombres.

### 2.3.3 La table des exécutions : le journal pour les machines

Le journal est fait pour un humain qui cherche. Pour répondre à des questions comme « quel mois n'a pas été chargé ? » ou « combien de lignes ont été rejetées cette année ? », on tient en plus une **table** : une ligne par exécution, avec son mois, son fichier, ses heures de début et de fin, son statut, ses compteurs et son message. C'est la table que lisent le rattrapage (section 2.2.5), les alertes (2.3.7) et, plus tard, le tableau de bord de santé du pipeline.

```python
print(ent3.execute("""SELECT mois, fichier, statut, lignes_lues AS lues, lignes_chargees AS chargées, lignes_rejetees AS rejetées
                      FROM executions WHERE mois IN ('2025-09', '2025-10') ORDER BY id_execution""").df().to_string(index=False))
```
<!--sortie-->
```text
   mois                  fichier statut  lues  chargées  rejetées
2025-09    commandes_2025-09.csv  ECHEC     0         0         0
2025-09 commandes_2025-09_v2.csv SUCCES  2522      2521         1
2025-10    commandes_2025-10.csv  ECHEC  2249         0         0
2025-10 commandes_2025-10_v2.csv SUCCES  2645      2644         1
```

Les quatre lignes racontent les deux histoires d'un coup d'œil : pour septembre et octobre, un **échec** (0 ligne chargée) suivi d'un **succès** quand le renvoi est arrivé. Le même contenu, mis en calendrier, donne la vue d'ensemble de l'année.


![Le calendrier des quinze exécutions de l'année : un cercle pour un succès, une croix pour un échec, placés à la date d'exécution sur la ligne du mois traité. Mars, septembre et octobre ont demandé une seconde livraison ; les croix de septembre et d'octobre sont les deux échecs.](figures/ch02-calendrier-executions.png)

> 💡 **Intuition.** Le journal répond à « que s'est-il passé ? », la table des exécutions répond à « où en est-on ? ». On a besoin des deux, et la table est celle que l'on branche sur des alertes et des tableaux de bord.

### 2.3.4 La quarantaine : mettre de côté, pas jeter

Les lignes que la transformation rejette ne disparaissent pas : elles sont écrites dans la table `rejets`, avec le fichier, le numéro de ligne dans le fichier, le motif et le contenu. Regardons ce que la quarantaine contient à la fin de l'année, pour la **dernière version** livrée de chaque mois (les premières versions de mars, de septembre et d'octobre sont remplacées).

```python
derniers = man.sort_values("date_livraison").groupby("mois").tail(1)["fichier"].tolist()
q = ent3.execute("SELECT motif, count(*) AS lignes FROM rejets WHERE fichier IN (SELECT unnest(?)) GROUP BY ALL ORDER BY 2 DESC", [derniers]).df()
print(q.to_string(index=False))
```
<!--sortie-->
```text
          motif  lignes
  doublon exact      25
 client inconnu      18
montant négatif       9
```

La quarantaine contient exactement les défauts qui ont été **injectés** dans les fichiers : 25 doublons (tous en novembre), 18 lignes dont le client n'est pas dans le référentiel et 9 montants négatifs. Une chaîne qui ne retrouverait pas ces nombres aurait un défaut, soit de contrôle, soit de comptage.


![Les lignes en quarantaine à la fin de l'année, par mois et par motif : novembre concentre les 25 doublons, les autres mois n'ont que quelques lignes orphelines ou quelques avoirs.](figures/ch02-rejets.png)

La quarantaine est un **outil de travail**, pas une poubelle. Il faut décider **qui** la lit, **à quelle fréquence** et **ce qu'on en fait** : renvoyer à l'équipe source pour correction, ou rectifier le référentiel. Voici le cas d'un client qui manque au référentiel : le client 90001 est un nouveau client que le système de commandes connaissait déjà mais pas encore le référentiel. Une fois qu'il y est ajouté, on **relance le mois** : la ligne en quarantaine entre dans l'entrepôt, et rien d'autre ne change.

```text
 exécution  chargées  rejetées                       message
         1      2225         3 2225 insérées, 0 mises à jour
         2      2226         2 1 insérées, 2225 mises à jour
```

La seconde exécution met à jour les lignes déjà présentes et ajoute celle qui était en quarantaine ; le nombre de lignes rejetées baisse d'une unité. On a corrigé à la **source** (le référentiel) puis **relancé**, au lieu de modifier à la main une ligne dans l'entrepôt : c'est la seule façon de rester reproductible.

### 2.3.5 Les contrôles de qualité : avant et après

Une chaîne sûre contrôle à **deux moments**. Avant le chargement, on vérifie que ce qu'on a reçu est exploitable ; après, on vérifie que ce qu'on a écrit correspond à ce qu'on voulait écrire. Les contrôles d'entrée protègent l'entrepôt ; les contrôles de sortie protègent le lecteur du rapport. Les techniques de contrôle (complétude, validité, cohérence) ont été vues au volume II (section 3.2) : ici, on les **branche** dans la chaîne.

| Moment | Contrôle | Notre dépôt |
|---|---|---|
| **Avant** | le fichier n'est pas vide | septembre |
| **Avant** | les colonnes du contrat sont là | mai (nom différent, toléré) |
| **Avant** | **lignes lues = lignes annoncées** par le manifeste | octobre |
| **Avant** | la part de lignes rejetées reste sous le seuil | seuil de 2 % |
| **Après** | **lignes lues = lignes chargées + lignes rejetées** (rien ne s'est perdu) | tous les mois |
| **Après** | **somme des montants de la source = somme chargée + somme rejetée** (au centime) | tous les mois |
| **Après** | toutes les dates sont dans le mois du fichier | tous les mois |
| **Après** | le total de l'entrepôt retombe sur celui d'**une autre source** | voir plus bas |

Les deux contrôles de conservation s'écrivent en quelques lignes. Mettons-les à l'épreuve sur le fichier de mars, d'abord tel quel, puis après avoir **perdu dix lignes** en route (comme le ferait une jointure qui élimine des lignes sans qu'on s'en aperçoive).

```python
def rapprocher(brut, valides, rejets):
    source = pd.to_numeric(brut["montant"], errors="coerce").sum()
    cible = valides["montant"].sum() + pd.to_numeric(rejets["montant"], errors="coerce").sum()
    return {"lignes conservées": len(brut) == len(valides) + len(rejets), "montants conservés": bool(abs(source - cible) < 0.005)}

brut = extraire(os.path.join(DEPOT, "commandes_2025-03_v2.csv"))
valides, rejets = transformer(brut, clients)
print("intact :", rapprocher(brut, valides, rejets))
print("dix lignes perdues :", rapprocher(brut, valides.iloc[10:], rejets))
```
<!--sortie-->
```text
intact : {'lignes conservées': True, 'montants conservés': True}
dix lignes perdues : {'lignes conservées': False, 'montants conservés': False}
```

Le second contrôle est le plus précieux : il **ne dépend d'aucune règle de gestion**. Il dit seulement « tout ce qui est entré est ressorti, quelque part », et il attrape une catégorie entière d'erreurs (jointures qui perdent ou multiplient des lignes, filtres trop gourmands) que les règles ligne à ligne ne voient pas.

Reste le dernier contrôle du tableau, qui ne regarde plus le fichier mais **une autre source** : le total de l'entrepôt doit retrouver celui de la base des commandes du volume III, qui est un système indépendant du dépôt (volume II, section 3.3 sur la réconciliation).

```python
c25 = pd.read_csv(os.path.join(os.environ["DONNEES"], "commandes.csv")).query("date_commande >= '2025-01-01'")
base_ca = pd.read_csv(os.path.join(os.environ["DONNEES"], "lignes_commande.csv")).merge(c25[["id_commande"]])["montant"].sum()
entrepot_ca = ent3.execute("SELECT sum(montant) FROM fait_ligne").fetchone()[0]
print("base :", fr(base_ca, 2), "€ | entrepôt :", fr(entrepot_ca, 2), "€ | écart :", fr(entrepot_ca - base_ca, 2), "€ | état identique à celui du rattrapage :", P.empreinte(ent3) == P.empreinte(ent2))
```
<!--sortie-->
```text
base : 1 324 763,72 € | entrepôt : 1 324 763,72 € | écart : 0,00 € | état identique à celui du rattrapage : True
```

L'écart est nul : l'entrepôt retrouve le chiffre d'affaires de la base, **au centime**, malgré un fichier tronqué, un fichier vide, des doublons et des erreurs de saisie. Et l'état obtenu en rejouant l'histoire dans l'ordre d'arrivée est **identique**, empreinte comprise, à celui du rattrapage de la section 2.2.5, qui n'avait chargé que la dernière version de chaque mois : c'est l'idempotence qui l'assure.

Pour les contrôles de **forme** (types, valeurs permises, unicité), on peut aussi s'appuyer sur une bibliothèque de validation comme **pandera** (volume II, section 3.5), qui exprime le contrat comme un schéma et rapporte **tous** les défauts d'un coup plutôt que le premier. Voici le schéma des colonnes qui comptent pour le rapport, appliqué aux lignes valides, puis à une version où un montant a été rendu négatif.

```python
import pandera.pandas as pa
schema = pa.DataFrameSchema({"id_ligne": pa.Column(int, unique=True), "montant": pa.Column(float, pa.Check.ge(0)), "canal": pa.Column(str, pa.Check.isin(CANAUX))})
schema.validate(valides)
abime = valides.assign(montant=valides["montant"].where(valides.index != 3, -5.0))
try:
    schema.validate(abime, lazy=True)
except pa.errors.SchemaErrors as e:
    print(e.failure_cases[["column", "check", "failure_case"]].to_string(index=False))
```
<!--sortie-->
```text
 column                       check  failure_case
montant greater_than_or_equal_to(0)          -5.0
```

> 🧭 **En pratique : où mettre quel contrôle ?** Les contrôles **bloquants** (fichier vide, colonnes absentes, conservation violée) arrêtent le chargement. Les contrôles **d'avertissement** (part de lignes rejetées au-dessus d'un seuil bas) laissent charger mais signalent. Le seuil est un choix métier : à 2 % de rejets le fichier de novembre passe (25 lignes sur 3 484, soit 0,7 %), à 0,5 % il aurait été refusé. L'important est qu'il soit **écrit**, **réglable** et **connu** de la gérante.

### 2.3.6 Les reprises : réessayer ce qui peut l'être

Toutes les pannes ne se valent pas. Un réseau qui coupe une seconde, un service qui répond « trop de demandes », une base momentanément verrouillée : réessayer un peu plus tard a toutes les chances de réussir. Un fichier vide, une colonne manquante, un contrôle de conservation violé : réessayer cent fois ne changera rien.

| Panne | Passagère ? | Que faire |
|---|---|---|
| connexion coupée, délai dépassé, service surchargé (429, 503) | **oui** | réessayer avec attente |
| fichier absent **pour l'instant** (livraison en retard) | **oui** | réessayer plus tard, avec une limite de durée |
| fichier vide, colonne absente, contrat violé | non | s'arrêter, prévenir |
| bogue (division par zéro, type inattendu) | non | s'arrêter, prévenir, corriger |

Pour les pannes passagères, la méthode classique est l'**attente exponentielle** : on réessaie après 1 seconde, puis 2, puis 4, en ajoutant un peu d'aléa (*jitter*) pour que mille processus qui ont échoué en même temps ne reviennent pas tous au même instant. Dans le code, on **passe en argument** la fonction qui dort, pour pouvoir tester sans attendre.

```python
def avec_reprises(fonction, essais=4, base=1.0, dormir=time.sleep, transitoires=(ConnectionError, TimeoutError)):
    rng = np.random.default_rng(0)
    for k in range(essais):
        try:
            return fonction()
        except transitoires:
            if k == essais - 1:
                raise
            dormir(base * 2 ** k * (1 + 0.25 * rng.random()))
```

Une fonction qui échoue deux fois puis réussit, et une autre qui échoue pour une raison **définitive** :

```text
données reçues | essais : 3 | attentes (s) : [1.2, 2.1]
erreur définitive, aucune nouvelle tentative : fichier vide
```

La première panne est surmontée en trois essais (les attentes réelles auraient été d'environ une seconde, puis deux). La seconde, un fichier vide, **remonte tout de suite** : on ne réessaie pas ce qui ne peut pas s'arranger seul. Toute reprise a une **limite** (ici quatre essais) : à l'infini, un pipeline réessaie en silence ce qu'il aurait fallu signaler.

> ⚠️ **Piège : les reprises sans idempotence.** Réessayer un chargement qui a réussi à moitié double des lignes s'il n'est pas idempotent. C'est une raison de plus pour écrire les chargements en transaction (tout ou rien) et par fusion, comme à la section 2.1.

### 2.3.7 Les alertes : crier au bon moment

Le journal et la table des exécutions ne servent à rien si personne ne les lit. L'**alerte** est ce qui vient chercher quelqu'un. Le piège est symétrique : trop peu d'alertes et l'on découvre la panne par la gérante ; trop d'alertes et l'on **n'ouvre plus** les messages, y compris le jour où l'un d'eux compte vraiment. C'est la **fatigue d'alerte**.

La règle qui y répond : **n'alerter que sur ce qui appelle une action**, par une personne identifiée, qui sait quoi faire. Voici le jeu de règles de notre pipeline, rangé par gravité.

| Gravité | Règle | Action attendue |
|---|---|---|
| **Critique** | un mois a échoué et n'a pas été résolu depuis | contacter la source, relancer à la main |
| **Critique** | **aucun chargement réussi depuis plus de 35 jours** | le planificateur est peut-être arrêté |
| **Attention** | plus de 0,5 % de lignes en quarantaine sur un mois | lire la quarantaine, prévenir l'équipe source |
| *Pas d'alerte* | une ligne rejetée, un avertissement isolé, une reprise qui a réussi | à lire dans le journal, si on le souhaite |

Appliquons ces règles **au fil de l'année**, aux dates où l'on aurait pu les lire. On compte aussi, pour comparaison, les alertes qu'aurait émises une règle naïve « prévenir dès qu'une ligne est rejetée ou qu'une exécution échoue ».

```text
alertes utiles sur l'année : 3 | alertes d'une règle naïve : 15
2025-09 : échec non résolu (SourceVide : commandes_2025-09.csv est vide)
2025-10 : échec non résolu (ControleEchoue : 2249 lignes lues pour 2645 annoncées)
2025-11 : 25 lignes en quarantaine sur 3484
```

Sur quinze exécutions, la règle naïve aurait sonné **à chaque fois** (une ligne rejetée suffit : quinze alertes sur quinze), contre **trois** alertes utiles : deux échecs et le mois de novembre. Quand toutes les exécutions déclenchent une alerte, plus aucune n'en est une.

Reste la panne la plus sournoise, celle que **rien ne signale** : si le planificateur est arrêté, il n'échoue pas, il **ne fait rien**, et aucune règle fondée sur les échecs ne s'enclenche. On l'attrape par un **battement de cœur** (*heartbeat* ou *dead man's switch*) : une règle qui alerte quand il ne s'est **pas** passé quelque chose pendant plus longtemps que prévu. Vérifions-la : si nous regardons le 20 février 2026 sans que rien n'ait été chargé depuis le 3 janvier, la règle des 35 jours se déclenche.

```python
print([m for _, m in P.evaluer_alertes(ent3, "2026-02-20") if m.startswith("aucun")])
```
<!--sortie-->
```text
['aucun chargement réussi depuis plus de 35 jours']
```

> 🧭 **En pratique : quelques règles pour des alertes qui servent.**
> - **Un propriétaire** par alerte (une personne ou un groupe), et un message qui dit **ce qui s'est passé, depuis quand, et quoi faire** en premier.
> - **Pas de répétition** : une alerte déjà envoyée n'est pas renvoyée chaque jour ; on la renvoie si elle change de gravité.
> - **Un canal différent selon la gravité** : un message pour « attention », un appel ou une notification pour « critique ».
> - **Testez le chemin d'alerte** lui-même : une fois par trimestre, provoquez une fausse panne et vérifiez que quelqu'un la reçoit. Une alerte qui n'arrive nulle part est pire qu'une absence d'alerte, car elle donne le sentiment d'être protégé.

### 2.3.8 Échouer bruyamment

Tout ce qui précède tient en un principe : **un pipeline doit échouer bruyamment**. Entre un programme qui plante avec un message clair et un programme qui livre un chiffre faux sans rien dire, le premier coûte une matinée de dépannage, le second coûte une décision prise sur une erreur. Concrètement :

- un contrôle qui échoue **arrête** la chaîne et empêche la **publication** (on n'envoie pas le rapport d'un mois qui n'est pas contrôlé) ;
- le programme rend un **code de sortie** différent de zéro, que le planificateur sait lire ;
- le **message** nomme le fichier, le contrôle et les nombres en cause (« 2 249 lignes lues pour 2 645 annoncées ») ;
- l'état de l'entrepôt reste **celui d'avant** (transaction), donc aucun lecteur ne tombe sur un état à moitié chargé ;
- et un **humain** est prévenu, par un canal qu'il lit.

> ✅ **À retenir.**
> - Cinq familles d'ennuis : la **source**, le **format**, les **lignes**, le **traitement**, l'**orchestration**. Chacune a sa réponse.
> - Le **journal** raconte (quoi, combien, résultat, pourquoi ; jamais de secret ni de donnée personnelle) ; la **table des exécutions** compte et alimente alertes et tableaux de bord.
> - La **quarantaine** garde ce qui est douteux, avec son motif ; on corrige à la source, puis on relance.
> - On contrôle **avant** (fichier non vide, colonnes, nombre de lignes annoncé) et **après** (rien ne s'est perdu en lignes ni en montants ; retombée sur une autre source).
> - On **réessaie** les pannes passagères avec attente exponentielle et limite, jamais les pannes définitives.
> - Les alertes sont **rares, actionnables, avec un propriétaire** ; un **battement de cœur** attrape la panne qui ne fait pas de bruit.
> - **Échouer bruyamment** vaut mieux que se tromper en silence.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.5 et 2.6, exercices 2.8 à 2.10.


## 2.4 ➕ Pour aller plus loin : dbt, Airflow, Power Automate et la planification avec Python

> 🧭 Section optionnelle. Elle décrit des outils que ce livre **n'exécute pas** (dbt, Airflow, Power Automate) : ce qui en est dit vient de leur documentation publique, sans essai ici, et les noms de paramètres comme la syntaxe changent d'une version à l'autre. Pour comprendre leur principe malgré tout, vous écrirez **deux jouets** qui, eux, s'exécutent.

Notre pipeline tient dans un script, un cron et une table des exécutions. C'est suffisant pour une boutique. Quand les chaînes se multiplient (vingt sources, trois équipes, des tableaux de bord qui dépendent les uns des autres), les mêmes besoins reviennent et on les confie à des outils dédiés.

### 2.4.1 Ce que cron ne sait pas faire

| Besoin | cron + script | Outil d'orchestration |
|---|---|---|
| **Dépendances** entre tâches (la tâche C attend A **et** B) | à écrire à la main | déclarées dans un graphe, respectées par le planificateur |
| **Reprise** au point d'échec | à écrire à la main | « relancer à partir de la tâche en échec » |
| **Historique** et interface | un journal, une table | interface qui montre chaque exécution, ses durées, ses journaux |
| **Rattrapage** de dates passées | à écrire à la main (section 2.2.5) | intégré (on demande « rejoue le 1er janvier au 31 mars ») |
| **Alertes**, relances automatiques | à écrire à la main | réglages par tâche |
| **Parallélisme**, plusieurs machines | difficile | prévu |
| **Secrets**, connexions | variables d'environnement | coffre intégré ou lié à un coffre |

La contrepartie est réelle : un orchestrateur est un **système de plus à installer, surveiller, mettre à jour et sécuriser**. Pour dix tâches simples, il coûte plus qu'il ne rapporte.

### 2.4.2 Airflow : planifier et superviser des graphes de tâches

**Apache Airflow** est un orchestrateur libre. On y décrit un **DAG** (le graphe orienté acyclique de la section 2.2.1) en Python : chaque nœud est une **tâche**, créée à partir d'un **opérateur** (exécuter une fonction Python, une commande, une requête SQL…), et les dépendances s'écrivent avec un opérateur `>>`. Le planificateur lance les exécutions selon un calendrier, un serveur web montre l'état de chaque tâche pour chaque date, et chaque exécution est associée à une **date logique** : on peut donc demander au système de rejouer les dates passées (*catchup*, *backfill*).

Voici l'allure d'un DAG pour notre chaîne. **Ce code n'est pas exécuté ici** et la syntaxe (en particulier le paramètre de calendrier) varie selon la version : il sert à montrer la forme, pas à être recopié.

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

with DAG("commandes_mensuelles", start_date=datetime(2025, 1, 1), schedule="0 6 3 * *", catchup=True, max_active_runs=1) as dag:
    extraire = PythonOperator(task_id="extraire", python_callable=extraire_fichier)
    transformer = PythonOperator(task_id="transformer", python_callable=transformer_lignes)
    charger = PythonOperator(task_id="charger", python_callable=charger_entrepot, retries=3)
    controler = PythonOperator(task_id="controler", python_callable=controler_chargement)
    extraire >> transformer >> charger >> controler
```

Retrouvez, dans ces lignes, des notions de la section 2.2 : l'expression cron (`schedule`), l'exécution unique à la fois (`max_active_runs`), le rattrapage (`catchup`), les reprises (`retries`) et le graphe de dépendances (`>>`). Ce que l'outil apporte, ce n'est pas une idée nouvelle : c'est la **tuyauterie** (interface, historique, reprise ciblée, alertes) qu'on aurait dû écrire. Ce qu'il ne fait **pas** : il n'écrit pas les tâches, et un DAG dont les tâches ne sont pas idempotentes se rejoue mal avec Airflow comme sans lui.

### 2.4.3 dbt : la transformation en SQL, testée et documentée

**dbt** (*data build tool*) s'occupe d'une seule partie de la chaîne, la transformation **dans l'entrepôt** (la lettre T de l'ELT de la section 2.1.6). On écrit des **modèles** : chacun est un fichier SQL qui contient un seul `SELECT`. Un modèle désigne ceux dont il dépend par `{{ ref('nom') }}` ; dbt en déduit l'**ordre de construction** et le **graphe de lignage** (quelle table dépend de laquelle), puis crée les tables ou les vues. On peut y attacher des **tests** (unicité, absence de valeurs vides, valeurs permises, référence vers une autre table) et de la **documentation**.

**Non exécuté ici**, voici l'allure d'un modèle et du fichier de tests qui l'accompagne.

```sql
-- models/ca_mois.sql
{{ config(materialized='table') }}
select strftime(date_commande, '%Y-%m') as mois, canal, sum(montant) as ca_ttc
from {{ ref('stg_lignes') }}
group by 1, 2
```

```yaml
# models/ca_mois.yml
models:
  - name: ca_mois
    columns:
      - name: ca_ttc
        tests: [not_null]
```

Les modèles peuvent être matérialisés en **vue** (calculée à la lecture), en **table** (recalculée à chaque exécution), ou en table **incrémentale** (on n'ajoute que les nouvelles lignes). Ce dernier mode retrouve **exactement** le piège de la section 2.1.4 : s'il se fonde sur « les lignes plus récentes que la dernière date chargée », il rate les **corrections** de lignes anciennes, et les équipes ajoutent en pratique une fenêtre de recouvrement ou une clé de fusion. Un outil ne vous dispense pas de comprendre le problème qu'il résout.

### 2.4.4 Power Automate et les outils « bas code »

**Power Automate** (et ses équivalents) est un outil de **flux** à construire avec des blocs, sans écrire de code : un **déclencheur** (« un e-mail arrive avec une pièce jointe », « un fichier est déposé », « tous les lundis à 7 h »), puis une suite d'**actions** (enregistrer la pièce jointe dans un dossier, ajouter une ligne dans un tableau, envoyer un message) reliées par des **connecteurs** à d'autres services. Pour un besoin simple (« quand le fichier arrive, le copier dans le dossier partagé et prévenir l'équipe »), il va plus vite qu'un script, et il est maniable par des personnes qui ne programment pas.

Ses limites sont celles de tous les outils graphiques : les transformations lourdes y sont pénibles, les licences et quotas comptent, le suivi de versions et les tests y sont moins naturels qu'avec du code, et un flux construit par une personne qui part devient vite **opaque**. Une bonne règle : s'en servir pour **déclencher et acheminer** (déposer, notifier, relayer), et garder le **calcul** dans du code versionné et testé. *Cet outil n'est pas exécuté ici, et son interface n'est pas reproduite : vérifiez ses possibilités dans la documentation de votre version.*

### 2.4.5 Premier jouet : un exécuteur de graphe

Pour comprendre ce que fait un orchestrateur, écrivons-en un de quelques lignes. Il parcourt le graphe dans l'ordre (le module `graphlib` vu en 2.2.1), exécute chaque tâche, **saute** celles dont une précédente a échoué, et sait **reprendre** en ne relançant que ce qui n'est pas terminé.

```python
def lancer_graphe(graphe, actions, etat=None):
    etat = dict(etat or {})
    for tache in TopologicalSorter(graphe).static_order():
        if etat.get(tache) == "ok":
            continue
        if any(etat.get(p) != "ok" for p in graphe.get(tache, ())):
            etat[tache] = "ignorée"
            continue
        try:
            actions[tache]()
            etat[tache] = "ok"
        except Exception:
            etat[tache] = "échec"
    return etat
```

Utilisons-le sur les sept étapes de la section 2.2 : chaque action note son nom dans une liste, et l'entrepôt est **verrouillé** au moment de charger.

```text
exécutées : ['repérer', 'extraire', 'transformer', 'quarantaine', 'charger'] 
état : {'repérer': 'ok', 'extraire': 'ok', 'transformer': 'ok', 'quarantaine': 'ok', 'charger': 'échec', 'contrôler': 'ignorée', 'publier': 'ignorée'}
```

Le chargement a échoué ; le contrôle et la publication, qui en dépendent, sont **ignorés** : on ne publie pas sur un chargement qui n'a pas eu lieu. La quarantaine, indépendante du chargement, est faite. Une fois la panne réparée, on relance **avec l'état précédent**.

```python
appels.clear()
actions["charger"] = action("charger")
etat2 = lancer_graphe(GRAPHE, actions, etat1)
print("relancées :", appels, "\nétat :", etat2)
```
<!--sortie-->
```text
relancées : ['charger', 'contrôler', 'publier'] 
état : {'repérer': 'ok', 'extraire': 'ok', 'transformer': 'ok', 'quarantaine': 'ok', 'charger': 'ok', 'contrôler': 'ok', 'publier': 'ok'}
```


![L'état du graphe après la panne du chargement : les trois premières étapes et la quarantaine sont terminées (✓), le chargement est en échec (✗), le contrôle et la publication sont ignorés (–). La couleur et le symbole disent la même chose. Schéma dessiné à partir de l'état réel du petit exécuteur.](figures/ch02-graphe-panne.png)

Seules les tâches **non terminées** sont relancées : c'est le « relancer à partir de l'échec » que proposent les orchestrateurs. Notre jouet n'a pourtant **ni parallélisme** (il exécute une tâche à la fois), **ni mémoire** (l'état disparaît avec le programme), **ni interface**, **ni reprise automatique**. Il montre le principe, il ne remplace rien.

### 2.4.6 Second jouet : des modèles SQL avec `ref()`

L'idée de dbt tient, elle aussi, en quelques lignes : des modèles écrits en SQL, un repérage des `ref('...')` qui donne l'ordre de construction, des tests simples. Écrivons-la sur notre entrepôt. Quatre modèles : une vue de base, le chiffre d'affaires par jour, par mois, et par catégorie de produit et par mois.

```python
MODELES = {
    "stg_lignes": "SELECT id_ligne, date_commande, canal, id_produit, montant FROM fait_ligne",
    "ca_jour": "SELECT date_commande, canal, sum(montant) AS ca_ttc FROM {{ ref('stg_lignes') }} GROUP BY ALL",
    "ca_mois": "SELECT strftime(date_commande, '%Y-%m') AS mois, canal, sum(ca_ttc) AS ca_ttc FROM {{ ref('ca_jour') }} GROUP BY ALL",
    "ca_categorie_mois": """SELECT strftime(l.date_commande, '%Y-%m') AS mois, p.categorie, sum(l.montant) AS ca_ttc
                            FROM {{ ref('stg_lignes') }} l JOIN dim_produit p USING (id_produit) GROUP BY ALL""",
}
ordre, compile_sql = P.construire_modeles(ent3, MODELES)
print("ordre de construction :", ordre)
print(compile_sql["ca_jour"])
```
<!--sortie-->
```text
ordre de construction : ['stg_lignes', 'ca_jour', 'ca_categorie_mois', 'ca_mois']
SELECT date_commande, canal, sum(montant) AS ca_ttc FROM stg_lignes GROUP BY ALL
```

Les `{{ ref('...') }}` ont servi deux fois : à **ordonner** les modèles (aucun n'est construit avant ceux dont il dépend) et à être remplacés par le nom de la vue. Le **lignage** se lit directement dans ces références.


![Le lignage des quatre modèles : les modèles bleus se calculent à partir des tables de l'entrepôt (vertes). Le graphe est déduit des références `ref()` écrites dans le SQL. Schéma dessiné.](figures/ch02-lignage-modeles.png)

Restent les **tests**. Deux suffisent à comprendre : « aucune clé en double » et « aucune valeur vide ». Appliquons-les aux modèles, puis à un modèle **fautif** qui, par une erreur d'union, reprend deux fois les lignes du canal `Site`.

```text
ca_mois {'unique:mois,canal': 0, 'non_nul:ca_ttc': 0}
ca_categorie_mois {'unique:mois,categorie': 0}
stg_faux {'unique:id_ligne': 13928}
```

Les modèles corrects passent (zéro ligne en défaut), le modèle fautif échoue : il a **dupliqué** des lignes, et le test d'unicité l'a vu avant qu'un tableau de bord n'affiche un chiffre d'affaires gonflé. C'est l'essentiel de ce que dbt apporte : des transformations **versionnées**, **ordonnées automatiquement** et **testées à chaque exécution**.

> ⚠️ **Piège : l'outil ne remplace pas le jugement.** Un test « unique » passe sur un modèle qui contient une somme **fausse**. Les tests attrapent des catégories d'erreurs, pas toutes ; les rapprochements de la section 2.3.5 (lignes et montants conservés, retombée sur une autre source) restent indispensables.

### 2.4.7 Choisir

| Votre situation | Raisonnable |
|---|---|
| Un ou deux pipelines, un petit entrepôt, vous seul | un script, cron ou APScheduler, une table des exécutions (ce chapitre) |
| Beaucoup de transformations SQL dans un entrepôt, plusieurs analystes | un outil de transformation comme **dbt** : ordre, tests, documentation partagés |
| Des dizaines de tâches dépendantes, des équipes, de l'historique à rejouer | un **orchestrateur** comme Airflow (ou un service géré équivalent) |
| Un besoin simple de déclenchement entre applications, sans programmeur | un outil **bas code** comme Power Automate, pour acheminer plus que pour calculer |

Dans tous les cas, la qualité d'une chaîne tient moins à l'outil qu'à ses **propriétés** : tâches idempotentes, contrôles avant et après, journal et alertes, propriétaire désigné.

> ✅ **À retenir.**
> - Un orchestrateur apporte la **tuyauterie** (dépendances, reprise ciblée, historique, rattrapage, alertes) ; il n'apporte **ni** l'idempotence **ni** les contrôles.
> - **Airflow** décrit des graphes de tâches en Python ; **dbt** gère les transformations SQL (ordre déduit des `ref()`, tests, lignage) ; les outils **bas code** acheminent plus qu'ils ne calculent. *Aucun n'est exécuté dans ce livre.*
> - Deux jouets écrits en quelques lignes (un exécuteur de graphe, des modèles SQL avec `ref()`) suffisent à comprendre le principe, sans en avoir ni la solidité ni les fonctions.
> - Plus d'outils, c'est plus de systèmes à maintenir : on n'en ajoute que si le besoin est réel.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.7, exercice 2.11.


## 2.5 ➕ Pour aller plus loin : l'automatisation robotisée des processus (UiPath et les autres)

> 🧭 Section optionnelle. Aucun outil de RPA n'est installé ici : tout ce qui concerne un produit (UiPath, par exemple) est décrit d'après sa documentation publique, **non exécuté**, et aucune de ses interfaces n'est reproduite. Les illustrations exécutées sont de petits programmes écrits pour l'occasion.

Jusqu'ici, nous avons automatisé des échanges de **fichiers** et d'**API**, c'est-à-dire des interfaces faites pour les programmes. Il existe des situations où il n'y en a pas : une application ancienne qui n'exporte rien, un portail de fournisseur qui n'offre qu'un écran de saisie, une tâche de recopie entre deux logiciels qui ne se parlent pas. L'**automatisation robotisée des processus** (*robotic process automation*, RPA) répond à ce besoin d'une manière particulière : un « robot » logiciel **reproduit ce que ferait une personne devant l'écran**, en cliquant, en saisissant du texte, en copiant des valeurs d'une fenêtre à l'autre.

### 2.5.1 Ce que fait un robot, et ce qu'il ne fait pas

Les plateformes de RPA (UiPath est l'une des plus connues, il en existe d'autres) proposent généralement un éditeur graphique où l'on enchaîne des **activités** (ouvrir une application, cliquer sur un bouton, lire une zone de texte, saisir une valeur, boucler sur les lignes d'un tableau), un **environnement d'exécution** (le robot) et un **chef d'orchestre** qui planifie les robots, gère leurs identifiants et conserve leurs journaux. On distingue souvent les robots **assistés** (ils travaillent sur le poste d'une personne, qui les déclenche) des robots **autonomes** (ils tournent seuls, sur un serveur, à heure fixe).

Un robot ne **comprend** rien : il suit une recette écrite à l'avance, dans un monde supposé immobile. Il ne sait ni qu'une colonne a changé de place, ni qu'un message d'erreur est apparu, ni qu'un chiffre est absurde, sauf si on l'a prévu. C'est la raison pour laquelle il se classe **en dernier recours** dans la hiérarchie de l'automatisation :

| Niveau | Interface utilisée | Robustesse | Exemple |
|---|---|---|---|
| 1 | **API** documentée | élevée : l'interface est un contrat versionné | lire les colis d'un transporteur (section 2.6) |
| 2 | **Fichier ou base** livrés pour cet usage | élevée si le format est stable | les exports mensuels de ce chapitre |
| 3 | **Navigation web programmée** (récupérer des pages) | moyenne : la page peut changer | récupérer un tableau publié sur un portail |
| 4 | **Robot d'interface** (clics et saisies à l'écran) | faible : tout changement d'écran le casse | recopier entre deux logiciels sans lien |

### 2.5.2 Quand la RPA se justifie

Elle se justifie quand **toutes** ces conditions sont réunies : la tâche est **répétitive** et suit des **règles précises**, les données sont **structurées**, il n'existe **ni API ni export** utilisable, l'application change **rarement**, et le volume est assez grand pour amortir la construction. Deux contextes typiques : une **solution d'attente** (le temps qu'une vraie intégration soit construite, ou qu'un vieux logiciel soit remplacé) et un **grand volume** de saisies identiques dans une application qu'on ne peut pas modifier.

Elle ne se justifie **pas** quand une alternative de niveau supérieur existe ou peut être demandée, quand la tâche exige du **jugement** (sauf à le confier à une personne, au bon endroit du processus), ou quand l'application change souvent.

### 2.5.3 La fragilité, en miniature

Pour sentir pourquoi le niveau 4 est le dernier recours, regardons le niveau 3, qui lui ressemble : récupérer une valeur dans une page web. Notre petit « robot » lit le chiffre d'affaires du jour sur la page de l'application de caisse, en repérant la zone par son identifiant. Il est écrit pour **échouer bruyamment** si la zone n'existe pas.

```python
from bs4 import BeautifulSoup

def lire_ca(html):
    zone = BeautifulSoup(html, "html.parser").select_one("#ca-jour .valeur")
    if zone is None:
        raise LookupError("zone « chiffre d'affaires du jour » introuvable : la page a-t-elle changé ?")
    return float(zone.text.replace(" ", "").replace("€", "").replace(",", "."))
```


Voici ce qui se passe quand l'éditeur de l'application **refond la page** : le chiffre est le même, mais les noms des éléments ont changé.

```python
for nom, page in (("page d'origine", page_v1), ("page refondue", page_v2)):
    try:
        print(nom, ":", fr(lire_ca(page), 2), "€")
    except LookupError as e:
        print(nom, ": ÉCHEC,", e)
```
<!--sortie-->
```text
page d'origine : 4 523,80 €
page refondue : ÉCHEC, zone « chiffre d'affaires du jour » introuvable : la page a-t-elle changé ?
```

Le robot bien écrit **s'arrête et le dit**. Un robot écrit sans cette précaution aurait renvoyé « rien », puis écrit un zéro dans le rapport, sans erreur. Et pourtant, la page n'a pas changé de **sens** : seul son habillage a bougé. Un robot d'interface, qui cherche un bouton à un endroit de l'écran, une image ou un champ de saisie, est exposé à la même fragilité, à chaque mise à jour de l'application, de la résolution d'écran, ou de la langue de l'interface.

> ⚠️ **Piège : le robot qui réussit à côté.** Le pire échec d'un robot n'est pas le plantage, c'est de cliquer au mauvais endroit et de **continuer**. Faites-lui vérifier, à chaque étape, qu'il est bien là où il le croit (un titre de fenêtre, un libellé) et rapprochez ses résultats d'un total de contrôle, comme à la section 2.3.5.

### 2.5.4 Faire le calcul avant de construire

Un robot coûte à **construire** et à **entretenir**, et l'entretien est le poste qu'on oublie. Pour une tâche que l'on fait aujourd'hui à la main vingt minutes par semaine, comparons trois voies **avec des hypothèses d'ordre de grandeur** (elles sont inventées pour l'exemple : remplacez-les par les vôtres).

| | Hypothèse |
|---|---|
| Tâche manuelle | 20 minutes par semaine, soit 17,3 heures par an |
| Robot d'interface | 24 heures à construire ; 6 incidents par an (changements d'écran) de 3 heures chacun |
| Chargement par fichier ou API | 16 heures à construire ; 2 incidents par an de 1,5 heure chacun |

```text
             voie  construction (h) entretien (h/an) remboursée en
        à la main                 0             17,3             —
robot d'interface                24             18,0        jamais
   fichier ou API                16              3,0        1,1 an
```


![Heures cumulées, sur quatre ans, de la tâche manuelle (gris), d'un robot d'interface (orange) et d'un chargement par fichier ou API (bleu), avec les hypothèses de ce paragraphe. Le robot coûte toujours plus que de continuer à la main : son entretien dépasse le temps qu'il fait gagner ; le chargement par fichier rembourse sa construction en un peu plus d'un an.](figures/ch02-cout-automatisation.png)

Avec ces hypothèses, le robot **ne rembourse jamais** : son entretien (dix-huit heures par an) dépasse le temps qu'il fait gagner (dix-sept heures). Le chargement par fichier ou API rembourse sa construction en un peu plus d'un an. Les hypothèses sont **fragiles**, et c'est justement la leçon : si le robot casse deux fois par an au lieu de six, le calcul s'inverse. Avant de construire, demandez-vous donc *combien de fois l'application change par an* et *combien coûte un arrêt*, pas seulement combien de minutes la tâche prend.

### 2.5.5 Gouverner ses robots

Un robot est un **utilisateur** de l'entreprise, souvent plus actif que les autres, qui ne se plaint jamais. Il demande une gouvernance précise.

- **Une identité à lui**, avec les **droits minimaux** nécessaires, jamais le compte d'une personne : quand la personne part, le robot continuerait de tourner sous un compte désactivé, ou pire, avec des droits qu'elle n'aurait plus dû avoir.
- **Des secrets dans un coffre**, pas dans le flux, pas dans le journal (section 2.6.3).
- **Un propriétaire nommé** et un **responsable métier** : qui répond quand il casse, qui accepte qu'il change.
- **Un journal complet** et, en cas d'échec, une **capture de l'écran** : sans elle, on devine ce que le robot « voyait ».
- **Un interrupteur d'urgence** : savoir l'arrêter en une minute, et savoir ce qu'il aura laissé à moitié fait.
- **Un cadre légal et contractuel** : respecter les conditions d'utilisation des applications et des portails qu'il manipule, ne pas contourner un contrôle d'accès, ne pas copier de données personnelles hors de ce que la finalité autorise (volume II, chapitre 5).
- **Un plan de sortie** : le robot est une solution **d'attente** ; la tâche de remplacement par une intégration en bonne et due forme doit être inscrite quelque part.

> ✅ **À retenir.**
> - La RPA reproduit les gestes d'une personne devant un écran ; elle sert **quand il n'existe ni API ni fichier**, en dernier recours.
> - Plus l'interface est proche de l'**écran**, plus l'automatisation est **fragile** : API, fichier, page web, robot d'interface, dans cet ordre de robustesse décroissante.
> - Un robot doit **échouer bruyamment** et vérifier **où il est** à chaque étape ; un robot qui réussit à côté est le pire des cas.
> - Le calcul de rentabilité doit inclure l'**entretien**, qui domine souvent la construction.
> - Un robot est un utilisateur : **identité propre**, droits minimaux, secrets au coffre, propriétaire, journal, interrupteur, plan de sortie.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : exercice 2.12.


## 2.6 ➕ Pour aller plus loin : intégration d'API et diffusion de rapports par e-mail

> 🧭 Section optionnelle. Les deux bouts de la chaîne : **lire** des données qu'un service met à disposition, et **envoyer** le résultat. L'API de cette section est un petit service **local**, lancé puis arrêté dans le chapitre (port 20120), et le serveur d'e-mail est un serveur de **test** local (port 20130) : rien ne sort de la machine.

### 2.6.1 Une API en trois idées

Une **API** (*application programming interface*) est une porte d'entrée faite pour les programmes : au lieu de télécharger un fichier à la main, on envoie une **requête** à une adresse, on reçoit une **réponse**, le plus souvent en JSON. Trois idées suffisent pour commencer.

1. **Une requête a une adresse, des paramètres et une identité.** Ici : `GET /colis?curseur=c0&taille=500`, avec une **clé** envoyée dans un en-tête (`Authorization: Bearer …`) qui dit qui demande.
2. **Une réponse a un code qui dit comment ça s'est passé**, avant même son contenu.
3. **Une API limite ce qu'on peut lui demander** : volume par page, nombre de requêtes par minute, droit d'accès.

| Code | Sens | Que faire |
|---|---|---|
| **200** | réussi | lire la réponse |
| **401** / **403** | pas identifié / pas autorisé | s'arrêter : la clé est absente, expirée ou insuffisante |
| **404** | introuvable | s'arrêter : l'adresse ou l'identifiant est faux |
| **429** | trop de demandes | attendre (l'en-tête `Retry-After` indique combien), puis réessayer |
| **500**, **502**, **503** | panne côté service | réessayer avec attente, quelques fois seulement |

Notre service fictif est celui d'un **transporteur** : il renvoie les colis de 2025 (date d'expédition, date de livraison, délai promis, retard). Pour que les exemples soient reproductibles, il est **programmé** pour tomber en panne : sa septième requête reçoit une erreur 500 et la dixième une erreur 429. Voici d'abord ce que répond le service à une requête **sans clé**, puis avec la clé de démonstration.


```text
sans clé : 401
avec clé : 200 | suivant : c2 | total : 7504
 id_commande   transporteur date_expedition date_livraison  delai_promis_j  retard
       23450 Transporteur A      2025-01-03     2025-01-07               6       0
       23452 Transporteur A      2025-01-10     2025-01-13               6       0
```

La réponse contient les données, un **curseur** (`suivant`) qui désigne la page suivante, et le **total** annoncé : un équivalent du manifeste de la section 2.1, à ne pas négliger.

### 2.6.2 Lire toutes les pages, avec patience

Une API ne renvoie pas tout d'un coup : elle découpe en **pages**. Pour tout lire, il faut suivre les curseurs jusqu'à ce qu'il n'y en ait plus. Il faut aussi **supporter les pannes passagères** de la section 2.3.6 : réessayer sur 429 et 500, en respectant l'en-tête `Retry-After` quand le service en donne un, et s'arrêter pour de bon sur les autres erreurs (401, 404).

```python
trace = []

def obtenir(session, adresse, params, dormir=time.sleep):
    for essai in range(5):
        r = session.get(adresse, params=params, timeout=10)
        trace.append((params["curseur"], r.status_code))
        if r.status_code not in (429, 500, 502, 503):
            r.raise_for_status()
            return r.json()
        dormir(float(r.headers.get("Retry-After", 2 ** essai)))
    raise RuntimeError("trop d'échecs sur la page " + params["curseur"])
```

La fonction qui parcourt les pages est alors courte.

```python
def lire_tout(url, cle):
    session = requests.Session()
    session.headers["Authorization"] = "Bearer " + cle
    lignes, curseur = [], "c0"
    while curseur:
        page = obtenir(session, url + "/colis", {"curseur": curseur, "taille": 500})
        lignes += page["donnees"]
        curseur = page["suivant"]
    return pd.DataFrame(lignes), page["total"]
```

Lançons-la sur un service neuf, puis **rapprochons** le résultat de deux références : le total annoncé par l'API et le fichier des livraisons du volume III.

```python
with P.serveur_api(20120, os.environ["API_COLIS_CLE"]) as url:
    colis, total_annonce = lire_tout(url, os.environ["API_COLIS_CLE"])
livraisons = pd.read_csv(os.path.join(os.environ["DONNEES"], "livraisons.csv"))
print("pages :", len({c for c, _ in trace}), "| requêtes :", len(trace), "| codes reçus :", dict(Counter(k for _, k in trace)))
print("lignes lues :", len(colis), "| total annoncé :", total_annonce, "| livraisons 2025 du volume III :", int((livraisons["date_commande"] >= "2025-01-01").sum()))
```
<!--sortie-->
```text
pages : 16 | requêtes : 18 | codes reçus : {200: 16, 500: 1, 429: 1}
lignes lues : 7504 | total annoncé : 7504 | livraisons 2025 du volume III : 7504
```


![Les dix-huit requêtes nécessaires pour lire les seize pages : la septième (erreur 500) et la dixième (429, trop de demandes) sont réessayées, et la lecture se termine sans que personne n'ait eu à intervenir. Schéma tracé à partir des requêtes réelles faites au service local.](figures/ch02-api-trace.png)

Les trois nombres concordent : tout a été lu. Les deux pannes passagères ont été **absorbées** par les reprises, sans intervention. Remarquez aussi ce que la fonction **ne fait pas** : elle ne réessaie pas un 401 (la clé est fausse, cent essais n'y changeraient rien) et elle s'arrête après cinq essais.

Pour intégrer ces données à l'entrepôt, on les écrit d'abord **telles quelles** dans le dépôt brut (un fichier par extraction, daté), puis on les charge **par fusion** sur leur clé, comme les fichiers de la section 2.1 : une API qui répond deux fois la même page ne doit pas doubler les colis. Pour les extractions volumineuses, on demande aussi, quand l'API le permet, « seulement ce qui a changé depuis telle date » (ce que les services appellent souvent un paramètre *modifié depuis*), avec la même **réserve** que pour le filigrane de la section 2.1.4 : un service qui corrige des données anciennes doit alors offrir une date de **modification**, pas seulement de création.

> ⚠️ **Piège : lire une API comme si elle était gratuite et sans limite.** Quotas, tarifs, conditions d'utilisation et protection des données s'appliquent aux API comme aux fichiers. Lisez la documentation, **demandez le minimum** de champs et de lignes, mettez en cache ce qui ne change pas, et ne stockez pas de données personnelles dont vous n'avez pas besoin.

### 2.6.3 Les secrets : jamais dans le code

La clé d'API est un **secret** : qui la possède peut agir au nom de l'entreprise. Règles élémentaires.

- **Pas dans le code.** Un secret écrit dans un script finit dans un dépôt Git, puis dans un historique que tout le monde peut lire, **même après suppression** de la ligne.
- **Dans l'environnement ou un coffre.** Le programme lit une **variable d'environnement** (ou interroge un coffre de secrets) ; la valeur est posée par la personne qui déploie. En développement, un fichier `.env` **non versionné** (inscrit dans `.gitignore`) tient lieu de coffre.
- **Jamais dans le journal ni dans un message d'erreur.** Un journal circule plus que la base.
- **Un secret par usage, remplaçable.** Si l'un d'eux fuit, on le **révoque** et on en génère un nouveau ; c'est pourquoi un secret n'est jamais partagé entre dix usages.

```python
def secret(nom):
    valeur = os.environ.get(nom)
    if not valeur:
        raise RuntimeError(f"variable d'environnement {nom} absente : voir le coffre (ou le fichier .env non versionné)")
    return valeur

class MasqueSecrets(logging.Filter):
    def filter(self, record):
        record.msg, record.args = re.sub(r"Bearer \S+", "Bearer ***", record.getMessage()), ()
        return True
```

La fonction `secret` échoue **tout de suite et clairement** si la variable manque (mieux qu'une erreur 401 obscure vingt minutes plus tard). Le filtre, branché sur le journal, masque ce qui ressemble à une clé avant que la ligne ne soit écrite : une seconde ceinture, car les erreurs de programmation arrivent.

```text
erreur claire : variable d'environnement MOT_DE_PASSE_INEXISTANT absente : voir le coffre (ou le fichier .env non versionné)
dans le journal : requête avec l'en-tête Authorization: Bearer ***
```

### 2.6.4 Diffuser le résultat par e-mail

Le rapport existe, il faut le faire parvenir. Un message électronique se construit en trois couches : des **en-têtes** (expéditeur, destinataires, objet), un **corps** (idéalement en deux versions, texte et HTML, pour les messageries qui n'affichent que l'un des deux) et des **pièces jointes**. La bibliothèque standard `email` les assemble, et `smtplib` les envoie à un serveur SMTP.

Préparons le contenu : le chiffre d'affaires de novembre par canal, comparé à octobre, calculé sur l'entrepôt de la section 2.3.

```text
   Canal Novembre (€ TTC) Octobre (€ TTC) Variation
Boutique           60 587          51 321   +18,1 %
 Réseaux           18 454          12 208   +51,2 %
    Site           64 851          56 535   +14,7 % 
total novembre : 143 892 € | octobre : 120 064 €
```

On en fait un message : texte, version HTML, et le détail en pièce jointe.

```python
import smtplib
from email.message import EmailMessage
note = "Chiffres calculés sur les lignes contrôlées ; 25 lignes en double écartées en novembre (quarantaine)."
msg = EmailMessage()
msg["From"], msg["To"], msg["Reply-To"] = "rapports@boutique.example", "gerante@boutique.example", "analyste@boutique.example"
msg["Subject"] = f"Chiffre d'affaires de novembre 2025 : {fr(total_nov / 1000, 0)} k€ TTC"
msg.set_content(f"Novembre : {fr(total_nov, 0)} € TTC, contre {fr(total_oct, 0)} € en octobre.\n{note}\nLe détail est en pièce jointe.")
msg.add_alternative(P.rapport_html(rapport, "Chiffre d'affaires de novembre 2025", note), subtype="html")
msg.add_attachment(ca.to_csv(index=False), subtype="csv", filename="ca_novembre_2025.csv")
```

Les adresses utilisent le domaine réservé `.example`, qui ne désigne aucune vraie boîte. L'envoi tient dans une fonction, avec une **option de simulation** comme pour le pipeline (section 2.2.2) : en simulation, on affiche ce qui partirait sans rien envoyer.

```python
def envoyer(message, hote="127.0.0.1", port=20130, simuler=False):
    if simuler:
        return "[simulation] « " + message["Subject"] + " » à " + message["To"]
    with smtplib.SMTP(hote, port, timeout=10) as serveur:
        serveur.send_message(message)
    return "envoyé"
```

Essayons dans l'ordre : la simulation, l'envoi au serveur de test, puis l'envoi quand **personne n'écoute** (la panne passagère de la section 2.3.6, avec trois essais).

```text
[simulation] « Chiffre d'affaires de novembre 2025 : 144 k€ TTC » à gerante@boutique.example
envoyé
serveur injoignable après 3 essais : ConnectionRefusedError
```

Le serveur de test a gardé le message. Relisons-le **comme le ferait son destinataire** pour vérifier ce qui est réellement parti : l'objet, les destinataires, les pièces jointes et leur contenu.

```python
import email, email.policy
recu = email.message_from_bytes(recus[0]["octets"], policy=email.policy.default)
pj = next(recu.iter_attachments())
print("objet :", recu["Subject"], "| à :", recu["To"], "| parties :", [p.get_content_type() for p in recu.walk() if not p.is_multipart()])
print("pièce jointe :", pj.get_filename(), "| contenu identique à l'original :", pj.get_content().splitlines() == ca.to_csv(index=False).splitlines())
```
<!--sortie-->
```text
objet : Chiffre d'affaires de novembre 2025 : 144 k€ TTC | à : gerante@boutique.example | parties : ['text/plain', 'text/html', 'text/csv']
pièce jointe : ca_novembre_2025.csv | contenu identique à l'original : True
```


![Le message tel qu'il a été reçu par le serveur de test : objet, expéditeur, destinataire, pièce jointe, et le tableau du corps HTML. Capture réelle d'une page HTML construite à partir du message relu ; la présentation est générique et ne reproduit aucune messagerie existante.](figures/ch02-courriel.png)

Pour envoyer **pour de vrai**, il faut en plus se connecter à un serveur SMTP de l'entreprise, chiffrer la connexion et s'identifier, avec des identifiants qui sont, eux aussi, des **secrets** lus dans l'environnement. **Non exécuté ici**, l'allure du code :

```python
with smtplib.SMTP("smtp.entreprise.example", 587) as serveur:
    serveur.starttls()
    serveur.login(secret("SMTP_UTILISATEUR"), secret("SMTP_MOT_DE_PASSE"))
    serveur.send_message(msg)
```

### 2.6.5 Penser à la diffusion

Envoyer est facile ; envoyer **bien** demande quelques décisions que l'on prend une fois, par écrit.

| Question | Bonne pratique |
|---|---|
| **À qui ?** | une **liste de diffusion** gérée à part, pas une adresse tapée dans le code ; une personne responsable de la liste |
| **Quand ?** | **après** les contrôles et jamais avant : un rapport qui part malgré un contrôle échoué est pire qu'un rapport en retard |
| **Quoi ?** | un résumé lisible dans le corps, le détail en pièce jointe **ou, mieux, un lien** vers le tableau de bord, qui reste à jour |
| **Quelles données ?** | le **minimum** : pas d'adresses de clients ni de données personnelles dans une pièce jointe qui voyagera de boîte en boîte |
| **Quelle version ?** | la **date de calcul** et la période dans l'objet, et la note sur les lignes écartées dans le corps |
| **Qui répond ?** | une adresse de réponse **humaine** (`Reply-To`) : un rapport dont on ne peut pas poser les questions est lu avec méfiance |
| **Et si ça échoue ?** | les reprises (section 2.3.6), puis une alerte à l'analyste, jamais un silence |
| **Qui le lit vraiment ?** | **demandez-le** : un rapport automatique qu'on ne lit plus est un coût, pas un service |

> 🧭 **En pratique : le premier envoi se fait à vous-même.** Avant de brancher la liste de la direction, envoyez les trois premiers cycles à l'analyste seul, comparez-les à ce que vous auriez produit à la main (c'est la **vérification croisée** du volume), puis ouvrez la diffusion. Prévoyez aussi un **mode test** permanent (la simulation de ce chapitre) pour les évolutions futures.

> ✅ **À retenir.**
> - Une API se lit avec une **adresse**, une **identité** et des **codes de réponse** ; on **suit les curseurs** de pagination et on **rapproche** le nombre de lignes lues du total annoncé.
> - On **réessaie** les 429 et les 500 (attente, limite d'essais, respect de `Retry-After`), jamais les 401 ni les 404.
> - Un **secret** vit dans l'environnement ou un coffre : jamais dans le code, jamais dans le journal ; il échoue **tôt et clairement** quand il manque.
> - Un e-mail se construit en **en-têtes, corps (texte et HTML) et pièces jointes** ; on le **relit** pour vérifier ce qui est parti, et on offre une **simulation**.
> - La diffusion est une décision : **qui, quand (après les contrôles), quoi (le minimum), quelle version, qui répond, qui lit**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.8 et 2.9, exercices 2.13 et 2.14.


## Bilan du chapitre 2

On est parti d'un lundi de congé et d'un chiffre d'octobre faux de près de quinze pour cent, que personne n'avait vu. On a construit la chaîne qui l'aurait évité : elle lit, contrôle, met de côté, charge sans doubler, se déclenche seule, raconte, prévient, et envoie. Le tableau suivant résume ce que chaque section a ajouté.

| Section | Ce que vous savez faire désormais |
|---|---|
| **2.1 Principes de l'ETL** | séparer extraire, transformer, charger ; lire en texte et sans modifier le brut ; écrire un **contrat de données** et une **quarantaine** ; choisir entre chargement complet et incrémental ; rendre un chargement **idempotent** (fusion sur la clé) et le prouver par une empreinte |
| **2.2 Scripts planifiés** | découper en étapes dépendantes, **paramétrer**, lancer en **ligne de commande** avec un code de sortie fiable et une **simulation** ; lire une expression **cron** et se méfier des différences d'un outil à l'autre ; planifier avec APScheduler ; **rattraper** des mois manqués ; verrouiller |
| **2.3 Erreurs et journalisation** | **journaliser** (texte et JSON), tenir une **table des exécutions**, **contrôler avant et après** (nombre de lignes annoncé, conservation des lignes et des montants, retombée sur une autre source), **réessayer** les pannes passagères, écrire des **alertes** rares et utiles, **échouer bruyamment** |
| **➕ 2.4 Outils** | situer dbt, Airflow et les outils bas code (non exécutés) ; comprendre leur principe avec un exécuteur de graphe et des modèles SQL avec `ref()` écrits en quelques lignes |
| **➕ 2.5 RPA** | savoir **quand** un robot d'interface se justifie, pourquoi il reste le dernier recours, faire le **calcul avec l'entretien**, et le gouverner |
| **➕ 2.6 API et diffusion** | lire une API paginée avec reprises, **rapprocher** le nombre de lignes lues du total annoncé, garder ses **secrets** hors du code, envoyer un e-mail avec pièce jointe et le **relire**, penser la diffusion |

### La vérité programmée, et ce que la chaîne a trouvé

Les fichiers du dépôt avaient été piégés dès la génération (script `build/outils_ch02.py`, docstring). Voici la liste, et ce que la chaîne en a fait. Les nombres du tableau sont vérifiés par le code de ce chapitre.


| Défaut programmé | Détecté ou traité par | Résultat |
|---|---|---|
| **Mars** : 12 montants multipliés par 10 dans le premier fichier (4 404 € en trop) | le renvoi du 14 avril, chargé **par fusion** | les 12 montants sont corrigés ; aucun doublon |
| **Mai** : la colonne des montants s'appelle `total_ligne` | le contrat (alias écrit) | chargé normalement |
| **Juillet** : dates en `JJ/MM/AAAA` | le contrat (format toléré, écrit) | chargé normalement |
| **Août** : fichier en `cp1252` | la lecture avec repli, puis la liste des canaux connus | chargé normalement |
| **Septembre** : fichier vide | le contrôle à la source | échec **sans écriture**, puis chargement du renvoi |
| **Octobre** : fichier tronqué (2 249 lignes lues pour 2 645 annoncées) | le **manifeste** (nombre de lignes annoncé) | échec **sans écriture**, puis chargement du renvoi |
| **Novembre** : 25 lignes en double exact | la quarantaine (« doublon exact ») | 25 lignes écartées, **alerte « attention »** (0,7 % de rejets) |
| **18 lignes orphelines** (client absent du référentiel) | la quarantaine (« client inconnu ») | 18 lignes écartées ; chacune peut être réintégrée après correction du référentiel |
| **9 montants négatifs** (avoirs) | la quarantaine (« montant négatif ») | 9 lignes écartées |
| **Total** | rapprochement avec la base du volume III | **1 324 763,72 €**, au centime, et un état **identique** que l'on rejoue l'histoire ou qu'on rattrape les derniers fichiers |

La chaîne a retrouvé tout ce qui avait été injecté, sans en inventer. Retenez la méthode plus que les nombres : on **programme** les défauts, on **écrit** ce que l'on s'attend à trouver, et on compare. C'est ainsi qu'on teste un pipeline : sur des cas où l'on connaît la réponse.

### Les pièges du chapitre

- **Croire que « le fichier s'ouvre » veut dire « le fichier est bon »** : vide, tronqué, mal encodé, renommé s'ouvrent sans erreur. Demandez le nombre de lignes à la source.
- **Un filigrane de date** qui rate les corrections de lignes anciennes ; la fusion sur la clé naturelle les absorbe, à condition que la clé soit **vraiment** stable.
- **Un chargement qui n'est pas idempotent** : la première relance double les lignes, et on la lance toujours le jour où quelque chose a déjà mal tourné.
- **Un script qui avale ses erreurs** et rend le code de sortie 0.
- **Deux « cron » différents** : les numéros de jours et la combinaison jour du mois / jour de la semaine ne sont pas les mêmes d'un outil à l'autre.
- **Des alertes pour tout** : on finit par n'en lire aucune. Et **aucune alerte** sur ce qui ne se produit pas (le battement de cœur).
- **Un robot d'interface qui réussit à côté**, ou dont on a oublié l'entretien dans le calcul de rentabilité.
- **Un secret dans le code, dans le journal ou dans un message d'erreur.**
- **Un rapport qui part malgré un contrôle échoué.**

### Une liste de contrôle pour mettre un pipeline en service

1. **La source** : un contrat écrit (colonnes, types, clé), un manifeste ou un total de contrôle, un propriétaire côté source.
2. **Le brut** est conservé, jamais modifié.
3. **La transformation** est écrite en règles lisibles ; ce qui est rejeté va en **quarantaine** avec son motif, et quelqu'un la lit.
4. **Le chargement** est idempotent et en **transaction** ; on l'a rejoué deux fois pour le prouver.
5. **Les contrôles** : avant (fichier, colonnes, nombre de lignes), après (lignes et montants conservés, retombée sur une autre source) ; un contrôle bloquant arrête **et** empêche la publication.
6. **Le journal** (une ligne par décision, avec les nombres, sans secret) et la **table des exécutions**.
7. **La planification** : fuseau explicite, marge après la livraison, **verrou**, **rattrapage** testé, option de **simulation**.
8. **Les alertes** : rares, actionnables, avec propriétaire ; un **battement de cœur** ; le chemin d'alerte **testé**.
9. **Les secrets** dans l'environnement ou un coffre.
10. **La diffusion** : liste gérée, minimum de données, version et date, adresse de réponse humaine, premier envoi à vous seul.
11. **Un plan de reprise** écrit : qui relance quoi, dans quel ordre, avec quelle commande.

> ✅ **À retenir, tout simplement.** Un pipeline fiable n'est pas celui qui ne tombe jamais en panne : c'est celui qui, **le jour où il tombe**, ne ment pas, ne casse rien, se laisse relancer sans danger et vous prévient.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 à 2.9, exercices 2.1 à 2.14. Le **projet du volume** (un pipeline de reporting automatisé alimentant un tableau de bord) s'appuie sur ce chapitre : voir le cahier, chapitre « Projet et auto-évaluation ».
