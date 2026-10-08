## 5.2 Text-to-SQL : demander une requête, vérifier avant de croire

Le *text-to-SQL* consiste à poser une question en français (« quel est le chiffre d'affaires 2024 par canal ? ») et à obtenir une **requête SQL**. C'est l'usage le plus utile d'un modèle de langage pour un analyste, et le plus piégeux : une requête fausse **s'exécute presque toujours** et renvoie un tableau d'aspect parfaitement normal. Cette section montre comment donner au modèle ce dont il a besoin, les façons de se tromper les plus courantes, puis comment construire le **harnais** qui laisse passer le bon et arrête le reste.

### 5.2.1 Donner le schéma, les règles et des exemples

Un modèle ne connaît ni vos tables, ni vos conventions. S'il les devine, il invente. La consigne doit donc contenir les **instructions de création** des tables, avec une **description** de chaque colonne qui pourrait prêter à confusion. Voici le début de celle de la boutique.

```python
print("\n".join(O.ddl(True).splitlines()[:11]))
```
<!--sortie-->
```text
CREATE TABLE commandes (
  id_commande INTEGER,  -- identifiant de la commande
  date_commande DATE,  -- jour de la commande
  heure TIME,  -- heure de la commande
  id_client INTEGER,  -- client (clients.id_client)
  canal VARCHAR,  -- Boutique, Site ou Réseaux
  mode_livraison VARCHAR,  -- Domicile, Point relais ou Retrait magasin
  code_promo VARCHAR,  -- code utilisé ; NULL si aucun
  frais_port DOUBLE  -- frais de port facturés, UNE valeur par COMMANDE (pas par ligne)
);
CREATE TABLE lignes_commande (
```
<!--sortie-->

Le deuxième ingrédient, ce sont les **règles métier** : elles transmettent ce qu'un collègue arrivé hier ignorerait. Chacune de celles-ci correspond à une erreur réelle, vue dans les volumes précédents.

```python
for r in O.REGLES[:4]:
    print("-", r)
```
<!--sortie-->
```text
- Le chiffre d'affaires est la somme de lignes_commande.montant (montants TTC, TVA fictive de 20 %).
- Les noms de produits ne sont pas uniques (60 noms pour 120 produits) : regrouper par id_produit.
- frais_port est une valeur par commande : ne la sommez pas après une jointure avec lignes_commande.
- Les données vont du 2023-01-01 au 2025-12-31 : « le dernier trimestre » veut dire le 4e trimestre 2025.
```
<!--sortie-->

La règle sur les noms de produits rappelle le piège du volume II : **60 noms pour 120 produits**. Un modèle qui regroupe sur `nom_produit` fusionne des produits différents. La règle sur `frais_port` est le piège classique du **niveau de granularité** (chapitre 1) : une valeur par commande, qu'une jointure avec les lignes recopie autant de fois qu'il y a de lignes. Quant à « le dernier trimestre », c'est une ambiguïté de langage : sans règle, le modèle choisira l'interprétation la plus courante dans ses textes d'entraînement, pas la vôtre.

### 5.2.2 Ce que fait un (très) petit modèle

Nous avons soumis les vingt questions de référence au petit modèle local, avec trois niveaux de consigne : **v1** (la question seule), **v2** (avec le schéma) et **v3** (schéma commenté, règles et deux exemples). Les sorties sont enregistrées ; regardons-en quatre.

```python
ex = [("q13", "v1"), ("q02", "v1"), ("q02", "v3"), ("q13", "v3")]
for q, v in ex:
    print(f"{q} {v} : {sorties['sql'][v][q][:105]}")
```
<!--sortie-->
```text
q13 v1 : SELECT taux_livre_retour_dans_commande_2025
FROM commandes_2025
WHERE commande_2025.commande_id = 2025;
q02 v1 : SELECT DISTINCT CASE WHEN CASE_DUPLICATE(CASE_DUPLICATE(CASE_DUPLICATE(CASE_DUPLICATE(CASE_DUPLICATE(CASE
q02 v3 : SELECT COUNT(*) AS n FROM livraisons L WHERE date_expedition = DATE '2024-01-01' AND date_livraison = DAT
q13 v3 : SELECT COUNT(*) AS taux_livraison, COUNT(*) AS taux_transporteur, COUNT(*) AS taux_livraison, COUNT(*) AS
```
<!--sortie-->

On y voit les défauts typiques d'un modèle trop petit pour la tâche : il **invente** des tables et des colonnes plausibles (`commandes_2025`), **boucle** sur le même fragment, choisit la **mauvaise table** ou **répète** une expression, sans répondre à la question. Passons les soixante sorties dans le harnais que nous construirons plus bas, pour avoir le compte des issues possibles.

```python
def passer(v):
    return O.evaluer(con, qs, refs, sorties["sql"][v], "petit modèle", v)
ev_petit = pd.concat([passer(v) for v in ("v1", "v2", "v3")])
ordre = ["juste", "exécutée mais fausse", "erreur d'exécution", "refusée"]
print(ev_petit.groupby("version")["statut"].value_counts().unstack(fill_value=0).reindex(columns=ordre, fill_value=0))
```
<!--sortie-->
```text
statut   juste  exécutée mais fausse  erreur d'exécution  refusée
version                                                          
v1           0                     1                   1       18
v2           0                     0                   2       18
v3           0                    11                   1        8
```
<!--sortie-->

Le résultat est instructif. **Aucune des soixante requêtes n'est juste.** Surtout, la meilleure consigne (v3) a fait passer ce modèle de requêtes visiblement cassées (dix-huit refus sur vingt avec les deux premières versions) à onze requêtes qui **s'exécutent et sont fausses** : en voulant l'aider, nous avons rendu ses erreurs plus difficiles à voir. Si un modèle est trop petit, aucune consigne ne le sauve ; c'est une raison de plus de **mesurer** avant de choisir. Remarquez aussi ce que le harnais permet : il n'a fallu lire aucune de ces soixante requêtes pour savoir où l'on en est.

> ⚠️ **Ces chiffres ne mesurent pas « les LLM ».** Ils décrivent un modèle de 135 millions de paramètres, sur nos vingt questions et nos trois consignes. Les modèles plus grands se trompent moins, pas jamais ; combien, et sur quoi, **se mesure sur vos questions** avec le même harnais.

### 5.2.3 Les erreurs d'un modèle plus capable

Un modèle plus capable ne fait presque plus d'erreurs de syntaxe. Ses erreurs sont plus sournoises : la requête est correcte du point de vue du SQL, et fausse du point de vue de la **question**. Nous avons écrit, pour chacune des vingt questions, la requête qu'un modèle de ce genre pourrait proposer : sept sont justes, treize portent une erreur courante. Ce sont des **réponses illustratives** : elles représentent des erreurs fréquentes, elles ne mesurent rien. Passons-les dans le harnais.

```python
ev_ill = O.evaluer(con, qs, refs, {k: v["sql"] for k, v in prop["propositions"].items()}, "illustratives", "")
ev_ill["nature"] = ev_ill["id"].map({k: v["nature"] for k, v in prop["propositions"].items()})
print(ev_ill["statut"].value_counts().to_string())
```
<!--sortie-->
```text
statut
exécutée mais fausse    10
juste                    7
refusée                  2
erreur d'exécution       1
```
<!--sortie-->

Le point essentiel est le tiers central de ce tableau : les requêtes **exécutées mais fausses**. Voici ce que les quatre plus instructives renvoient, comparé à la bonne réponse.

```python
for q in ("q03", "q04", "q07", "q09"):
    df, _ = O.executer(con, prop["propositions"][q]["sql"])
    v = df.iloc[0, 0]
    print(f"{q} {prop['propositions'][q]['nature']:<28} obtenu {'(vide)' if pd.isna(v) else v!s:>10}   attendu {refs[q].iloc[0, 0]}")
```
<!--sortie-->
```text
q03 date relative à aujourd'hui  obtenu     (vide)   attendu 447800.38
q04 mauvais grain                obtenu      44.41   attendu 102.33
q07 jointure qui duplique        obtenu    56139.4   attendu 24421.8
q09 division entière             obtenu         15   attendu 15.43
```
<!--sortie-->

Chacune a une cause simple, et chacune est illisible à l'œil dans un tableau de résultats.

- **Date relative** (`q03`) : « le dernier trimestre » est traduit par « les trois derniers mois **à partir d'aujourd'hui** ». Sur des données qui s'arrêtent fin 2025, le résultat est **vide**, et dépend du jour où l'on lance la requête.
- **Mauvais grain** (`q04`) : le « panier moyen » devient la moyenne **d'une ligne** de commande, qui n'est pas la valeur d'une commande.
- **Jointure qui duplique** (`q07`) : on somme `frais_port` après la jointure avec les lignes ; chaque commande compte autant de fois qu'elle a de lignes.
- **Division entière** (`q09`) : `COUNT(...) * 100 / COUNT(*)` converti en entier **tronque** la part (15 au lieu de 15,43) ; sur d'autres moteurs, la division de deux entiers est elle-même entière.

Les autres erreurs de l'ensemble sont de la même famille : regroupement sur le nom d'un produit, jointure interne pour chercher une absence, mois sans année, mauvaise colonne de date, numérotation des jours (`dayofweek` commence le dimanche à 0, pas à 7), tri dans le mauvais sens. Aucune ne déclenche d'erreur.

```python hide
tab = pd.concat([ev_petit.assign(source=lambda d: "petit modèle, consigne " + d["version"]), ev_ill.assign(source="réponses illustratives")])
cnt = tab.groupby(["source", "statut"]).size().unstack(fill_value=0)
F.fig_statuts(cnt.loc[["petit modèle, consigne v1", "petit modèle, consigne v2", "petit modèle, consigne v3", "réponses illustratives"]])
```
<!--sortie-->
```text
figure : ch05-statuts.png
```
<!--sortie-->

![Issue de chaque requête dans le harnais : quatre jeux de vingt requêtes (trois du petit modèle réel, un de réponses illustratives écrites pour l'exemple).](figures/ch05-statuts.png)

### 5.2.4 Première pièce du harnais : valider avant d'exécuter

Le schéma suivant résume l'ensemble du harnais que nous construisons : trois pièces autour d'un modèle que l'on traite comme une boîte noire non fiable, avec une boucle de correction bornée.

```python hide
F.fig_harnais()
```
<!--sortie-->
```text
figure : ch05-harnais.png
```
<!--sortie-->

![Le harnais : tout ce qui entoure le modèle est du code ordinaire, vérifiable et journalisé.](figures/ch05-harnais.png)

La première défense est de **lire la requête sans l'exécuter**. On ne le fait pas avec des expressions régulières (trop fragiles : un commentaire, une majuscule, un espace les déjouent) mais avec un **analyseur syntaxique**. La bibliothèque **sqlglot** transforme le texte en arbre ; on interroge l'arbre.

```python
import sqlglot
from sqlglot import exp
arbres = sqlglot.parse("SELECT COUNT(*) FROM clients; DELETE FROM clients", dialect="duckdb")
print([type(a).__name__ for a in arbres])
print(sorted({t.name for t in arbres[1].find_all(exp.Table)}))
```
<!--sortie-->
```text
['Select', 'Delete']
['clients']
```
<!--sortie-->

Le harnais (fonction `valider`, dans `build/outils_ch05.py`) applique cinq règles :

1. **une seule instruction** (sinon, une requête anodine peut en cacher une autre) ;
2. de **type SELECT** (ni `INSERT`, `UPDATE`, `DELETE`, `DROP`, `CREATE`, `COPY`, `PRAGMA`…) ;
3. sur des **tables connues** de la liste blanche (ou des tables temporaires définies par `WITH`), et **aucune fonction de table** qui lit des fichiers (`read_csv`, `glob`…) ;
4. avec des **colonnes qui existent**, ce que sqlglot vérifie en « qualifiant » la requête contre le schéma ;
5. écrite dans un **dialecte analysable** (une erreur de syntaxe est refusée avec son message).

Voici cinq demandes qu'un utilisateur, ou un texte piégé (section 5.5), pourrait provoquer.

```python
for d in prop["dangereuses"]:
    ok, raison = O.valider(d["sql"])
    print(f"{'acceptée' if ok else 'refusée ':9} {d['sql'][:46]:<46} {raison[:45]}")
```
<!--sortie-->
```text
refusée   DROP TABLE commandes                           instruction interdite : DROP
refusée   SELECT COUNT(*) FROM clients; DELETE FROM clie 2 instructions (une seule autorisée)
refusée   SELECT * FROM read_csv('/etc/hostname', header fonction de table interdite : READ_CSV('/etc/
refusée   COPY (SELECT * FROM clients) TO 'clients.csv'  instruction interdite : COPY
refusée   SELECT table_name FROM information_schema.tabl table inconnue : tables
```
<!--sortie-->

La colonne inventée de la question `q05` (`produit_id`) est elle aussi arrêtée ici, avant toute exécution, avec un message que l'on peut renvoyer au modèle.

```python
print(O.valider(prop["propositions"]["q05"]["sql"]))
```
<!--sortie-->
```text
(False, "colonne inconnue : Column 'produit_id' could not be resolved")
```
<!--sortie-->

> ⚠️ **La validation est un garde-fou, pas un périmètre de sécurité.** Un analyseur peut se tromper (dialecte mal reconnu, construction rare). C'est pourquoi la pièce suivante ne lui fait pas confiance.

### 5.2.5 Deuxième pièce : lecture seule, limite de lignes et délai

La vraie protection est **dans le moteur**. La connexion du harnais est ouverte en **lecture seule**, avec l'accès aux fichiers coupé ; même si une instruction d'écriture traversait la validation, la base la refuserait.

```python
try:
    con.execute("INSERT INTO clients SELECT * FROM clients")
except Exception as e:
    print(str(e).split("\n")[0][:100])
```
<!--sortie-->
```text
Invalid Input Error: Cannot execute statement of type "INSERT" on database "boutique" which is attac
```
<!--sortie-->

La même fonction `executer` borne ensuite **le nombre de lignes** rendues (une requête sans filtre sur une grosse table ne doit pas remplir la mémoire) et **la durée**. Une jointure croisée de trois fois la table des lignes de commande, volontairement absurde, est interrompue après deux secondes.

```python
df, msg = O.executer(con, "SELECT COUNT(*) FROM lignes_commande a, lignes_commande b, lignes_commande c", delai=2)
print(df, msg)
```
<!--sortie-->
```text
None interrompue après 2 s
```
<!--sortie-->

> 🧭 **En pratique, sur un vrai serveur.** Le compte utilisé par le harnais doit n'avoir que le droit de lire, et seulement des **vues** qui excluent les colonnes sensibles. Les trois protections (validation, droits du compte, limites de ressources) se complètent ; aucune ne suffit seule. Nous ne touchons à aucun serveur ici : tout est local.

### 5.2.6 Troisième pièce : comparer à une référence

Une requête acceptée et exécutée peut encore être fausse. La seule défense systématique est de **connaître la bonne réponse**. On constitue donc un **jeu de questions de référence** : des questions réelles, en français, chacune accompagnée d'une requête SQL écrite et relue par une personne, dont le résultat a été **vérifié par un autre chemin**. C'est le même geste que les « tests de non-régression » du chapitre 2.

Pour la boutique, le jeu compte vingt questions, du plus simple (« combien de commandes en 2024 ? ») aux plus pièges, chacune étiquetée par le piège qu'elle teste. Vérifions deux références par un autre outil, pandas, sans passer par la base.

```python
lignes = pd.read_csv(os.path.join(os.environ["DONNEES"], "lignes_commande.csv")).merge(pd.read_csv(os.path.join(os.environ["DONNEES"], "commandes.csv")), on="id_commande")
ca24 = lignes[lignes["date_commande"].str[:4] == "2024"].groupby("canal")["montant"].sum().round(2)
print(ca24.to_dict(), "| référence q02 :", dict(sorted(zip(refs["q02"].iloc[:, 0], refs["q02"].iloc[:, 1]))))
print("q05 :", pd.read_csv(os.path.join(os.environ["DONNEES"], "produits.csv"))["id_produit"].nunique(), "produits,", refs["q05"].iloc[0, 0], "dans la référence")
```
<!--sortie-->
```text
{'Boutique': 558142.85, 'Réseaux': 128787.32, 'Site': 502531.0} | référence q02 : {'Boutique': 558142.85, 'Réseaux': 128787.32, 'Site': 502531.0}
q05 : 120 produits, 120 dans la référence
```
<!--sortie-->

La **comparaison** elle-même obéit à des règles qu'il faut décider une fois pour toutes : les **noms de colonnes** ne comptent pas (le modèle écrira `chiffre_affaires` là où la référence écrit `ca`) ; l'**ordre des lignes** ne compte que si la question le demande (« les cinq premiers ») ; les **nombres** sont comparés à un centime près ; le **nombre de colonnes** doit être le bon. La fonction `egal` applique ces règles ; `evaluer` la combine à la validation et à l'exécution et classe chaque proposition dans l'une des quatre issues : **refusée**, **erreur d'exécution**, **exécutée mais fausse**, **juste**.

On distingue alors deux taux, qu'il ne faut jamais confondre : le taux de requêtes qui **tournent** (que l'on peut obtenir sans contrôle) et le taux de requêtes **justes**.

```python
def taux(ev):
    return pd.Series({"tournent (%)": 100 * ev["statut"].isin(["juste", "exécutée mais fausse"]).mean(), "justes (%)": 100 * (ev["statut"] == "juste").mean()})
print(pd.DataFrame({"petit modèle, v3": taux(ev_petit[ev_petit.version == "v3"]), "réponses illustratives": taux(ev_ill)}).round(0).astype(int))
```
<!--sortie-->
```text
              petit modèle, v3  réponses illustratives
tournent (%)                55                      85
justes (%)                   0                      35
```
<!--sortie-->

L'écart entre les deux lignes **est** le risque : pour le petit modèle, plus d'une requête sur deux tourne et aucune n'est juste ; pour les réponses illustratives, 85 % tournent et 35 % seulement sont justes. Ce sont des réponses qui ont l'air bonnes. Un système qui n'afficherait que le premier taux donnerait une fausse impression de maîtrise.

> ⚠️ **Une référence ne couvre que ce qu'elle contient.** Vingt questions vérifiées protègent de ces vingt pièges, pas de la vingt-et-unième. On enrichit le jeu à chaque nouvelle erreur découverte (section 5.5) et l'on garde une relecture humaine pour tout ce qui n'y figure pas.

### 5.2.7 La boucle de correction et le journal

Quand une requête est **refusée** ou **échoue**, on peut renvoyer au modèle le message d'erreur et lui demander de corriger, au plus **trois fois**. La boucle est de quelques lignes de code. Pour la montrer sans service de modèle, nous remplaçons le modèle par une petite fonction qui rend, à chaque essai, la réponse que nous avons écrite pour cette question (première erreur, puis correction).

```python
def generer(question_id):
    essais = iter([prop["propositions"][question_id]["sql"]] + prop["corrections"].get(question_id, []))
    return lambda question, erreur: next(essais)

for q in ("q05", "q12", "q04"):
    sql, journal = O.boucle(con, qs.set_index("id").loc[q, "question"], generer(q))
    print(q, pd.DataFrame(journal).to_dict("records"))
```
<!--sortie-->
```text
q05 [{'essai': 1, 'resultat': 'rejetée', 'message': "colonne inconnue : Column 'produit_id' could not be resolved"}, {'essai': 2, 'resultat': 'acceptée', 'message': '1 ligne(s)'}]
q12 [{'essai': 1, 'resultat': 'rejetée', 'message': 'Catalog Error: Scalar Function with name days_between does not exist!'}, {'essai': 2, 'resultat': 'acceptée', 'message': '3 ligne(s)'}]
q04 [{'essai': 1, 'resultat': 'acceptée', 'message': '1 ligne(s)'}]
```
<!--sortie-->

Les deux premières questions sont réparées au deuxième essai, parce que l'erreur est **détectable** (colonne inconnue, fonction inexistante). La troisième, `q04`, est **acceptée du premier coup**, et pourtant fausse : la boucle ne corrige pas une réponse plausible.

Chaque essai laisse une trace : c'est le **journal** du harnais (question, version du prompt, requête, issue, durée, nombre de lignes). Ce journal sert à trois choses : **comprendre** une erreur après coup, **mesurer** le taux de réussite par type de question, et **rendre des comptes** (« qui a produit ce chiffre, avec quelle requête ? »). On l'écrit dans une table ou un fichier, comme le journal d'exécution du chapitre 2.

### 5.2.8 Quand tout passe et que le résultat est faux

Il reste le cas le plus difficile : la requête passe la validation, s'exécute, et le résultat est faux sans que la référence existe (une question nouvelle). Les parades sont des habitudes d'analyste, pas du code sophistiqué.

1. **Demander une explication en français** de la requête (« que compte cette requête, sur quel grain, avec quels filtres ? ») et la **comparer à la question**. Les erreurs de grain et de filtre se voient dans l'explication plus vite que dans le SQL.
2. **Encadrer le résultat par un ordre de grandeur indépendant.** Les frais de port d'une année ne peuvent pas dépasser le nombre de colis expédiés (la table des livraisons) multiplié par le tarif le plus élevé.

```python
n24 = con.execute("SELECT COUNT(*) FROM livraisons WHERE year(date_commande) = 2024 AND mode_livraison <> 'Retrait magasin'").fetchone()[0]
borne = n24 * 4.9
df, _ = O.executer(con, prop["propositions"]["q07"]["sql"])
print(f"borne maximale {borne:,.0f} €, requête proposée {df.iloc[0, 0]:,.0f} € ->", "plausible" if df.iloc[0, 0] <= borne else "IMPOSSIBLE")
```
<!--sortie-->
```text
borne maximale 29,312 €, requête proposée 56,139 € -> IMPOSSIBLE
```
<!--sortie-->

3. **Tester sur un cas minuscule** dont on connaît le résultat (trois commandes, deux lignes chacune) avant d'exécuter sur toute la base.
4. **Refaire le calcul par un autre chemin** (pandas au lieu de SQL, comme plus haut), au moins par sondage.
5. **Comparer à la semaine précédente** : un chiffre qui bouge de 300 % sans raison commerciale est une erreur jusqu'à preuve du contraire.

Enfin, voici à quoi ressemblerait l'appel à un modèle hébergé. Ce bloc n'est **pas exécuté** : il dépend du fournisseur que vous choisirez, et nous n'en avons pas utilisé ici.

```python noexec
def demander(question, erreur=None):                      # NON EXÉCUTÉ : `client` dépend de votre fournisseur
    messages = [{"role": "system", "content": CONSIGNE_V3}, {"role": "user", "content": question}]
    if erreur:
        messages.append({"role": "user", "content": f"Requête refusée : {erreur}. Corrigez-la."})
    return client.generer(messages, temperature=0)       # puis valider → exécuter → comparer, comme ci-dessus
```

> ✅ **À retenir.** Un modèle propose, le harnais décide. **Valider** (sqlglot), **exécuter en lecture seule avec limite et délai**, **comparer à une référence**, **journaliser**, et garder une **relecture humaine** pour tout ce que la référence ne couvre pas. Les erreurs les plus dangereuses sont celles qui s'exécutent : mesurez le taux de requêtes **justes**, pas celui de requêtes qui **tournent**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.2 à 5.4 (repérer les erreurs d'une requête, étendre le harnais, enrichir le jeu de référence) et exercices 5.3 à 5.7.
