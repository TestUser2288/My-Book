## 5.1 Ce qu'est (et ce que n'est pas) un LLM pour un analyste

Avant de confier du travail à un modèle de langage, il faut en avoir une image juste, ni magique ni méprisante. Cette section en donne cinq morceaux utiles à un analyste : comment il produit un texte, ce qu'il coûte à lire des données, pourquoi il peut répondre autrement la fois suivante, ce qu'on ne lui envoie jamais, et comment on lui écrit une consigne.

### 5.1.1 Un LLM prédit le mot suivant

Un **modèle de langage** (en anglais *large language model*, LLM) lit un texte découpé en morceaux appelés **jetons** (*tokens* : des mots, des fragments de mots, des signes de ponctuation). Pour chaque suite de jetons, il calcule un **score** pour chacun des jetons possibles à la suite, en choisit un, l'ajoute au texte, et recommence. Une réponse de dix lignes est donc le résultat de quelques centaines de choix successifs « quel est le prochain jeton plausible ? ».

Regardons ce que fait vraiment un tout petit modèle (135 millions de paramètres, exécuté ici hors ligne, dont nous avons enregistré les scores) quand on lui donne le début d'une phrase de rapport.

```python
lg = sorties["logits"]
sc = np.array(lg["scores"])
top = pd.DataFrame({"jeton suivant": [repr(j) for j in lg["jetons"][:6]], "probabilité (%)": (100 * np.exp(sc - sc.max()) / np.exp(sc - sc.max()).sum())[:6].round(1)})
print(lg["amorce"] + " ...")
print(top.to_string(index=False))
```
<!--sortie-->
```text
Le chiffre d'affaires de décembre a ...
jeton suivant  probabilité (%)
        'vec'             50.2
        'ins'             23.7
          ' '              7.7
        'uss'              4.7
         'up'              4.1
          'j'              2.5
```
<!--sortie-->

Le jeton le plus probable, `vec`, n'est pas un mot mais un **fragment** : il complète « a » en « avec ». Rien dans ce calcul ne consulte vos données : le modèle ne sait pas que le chiffre d'affaires de décembre a progressé ou reculé, il sait seulement quels mots **suivent d'ordinaire** ce début de phrase. Deux conséquences capitales pour un analyste.

> ⚠️ **Plausible n'est pas vrai.** Un modèle produit ce qui **ressemble** à une bonne réponse. Quand il « connaît » la réponse (une syntaxe SQL très courante), c'est excellent. Quand il ne la connaît pas (le chiffre d'affaires de **votre** décembre, le nom exact de **vos** colonnes), il produit quand même une réponse du même style, avec le même aplomb. Sa confiance apparente ne dit rien de sa justesse.

> ⚠️ **Un modèle ne calcule pas, il imite des calculs.** Additionner de longues colonnes, appliquer une moyenne pondérée, compter des lignes : pour tout cela, **on lui fait écrire du code** (une requête, un script) que l'on exécute ailleurs, on ne lui demande pas le résultat. C'est la raison d'être du *text-to-SQL* de la section 5.2.

### 5.1.2 Jetons, fenêtre de contexte et coût

Le texte est découpé en jetons : selon le découpeur du modèle, un jeton couvre en français de deux à quatre caractères, mais des nombres, des identifiants ou des séquences inhabituelles se découpent beaucoup plus finement. Trois quantités en dépendent.

- La **fenêtre de contexte** : le nombre maximal de jetons (consigne **et** réponse) que le modèle peut considérer à la fois. Selon les modèles, de quelques milliers à plusieurs centaines de milliers de jetons ; à vérifier dans la documentation du modèle que vous utilisez.
- Le **coût** : les services hébergés facturent généralement au nombre de jetons lus et écrits (les tarifs changent : consultez ceux du fournisseur).
- Le **temps de réponse**, qui croît lui aussi avec la longueur.

Mesurons le découpage sur quelques textes de ce chapitre, avec le découpeur du petit modèle (comptages enregistrés).

```python
t = pd.DataFrame(sorties["tokens"])[["nom", "caracteres", "jetons"]]
t["caractères par jeton"] = (t["caracteres"] / t["jetons"]).round(1)
print(t.to_string(index=False))
```
<!--sortie-->
```text
                nom  caracteres  jetons  caractères par jeton
         schema_ddl        1160     416                   2.8
schema_descriptions        2325     837                   2.8
          ligne_csv          64      64                   1.0
             phrase          82      36                   2.3
            requete          63      20                   3.2
```
<!--sortie-->

Le rapport varie : un peu plus de deux caractères par jeton pour une phrase française avec le découpeur de ce petit modèle, et un seul pour des lignes de nombres, où chaque chiffre ou presque pèse un jeton. Cela fixe un ordre de grandeur utile : que coûterait-il de **coller les données** dans la consigne ?

```python hide
car = {f: len(open(os.path.join(os.environ["DONNEES"], f + ".csv"), encoding="utf-8").read()) for f in O.TABLES}      # caractères de chaque CSV
rapport_csv = t.set_index("nom").loc["ligne_csv", "caractères par jeton"]
rapport_txt = t.set_index("nom").loc["phrase", "caractères par jeton"]
faits_mois = O.faits_mensuels(con)
j_schema = int(t.set_index("nom").loc["schema_descriptions", "jetons"])
j_faits = int(len(json.dumps(faits_mois, ensure_ascii=False)) / rapport_txt)
j_lignes = int(car["lignes_commande"] / rapport_csv)
j_base = int(sum(car.values()) / rapport_csv)
F.fig_jetons([("schéma commenté (6 tables)", j_schema), ("chiffres d'un rapport mensuel", j_faits), ("table lignes_commande entière", j_lignes), ("toute la base de la boutique", j_base)])
print(j_schema, j_faits, j_lignes, j_base)
```
<!--sortie-->
```text
figure : ch05-jetons.png
837 128 2460593 6231862
```
<!--sortie-->

![Jetons nécessaires pour décrire la base, pour lui donner les chiffres d'un rapport, et pour lui coller les données (estimations à partir du rapport mesuré sur trois lignes).](figures/ch05-jetons.png)

Le schéma commenté pèse environ 840 jetons et les chiffres d'un rapport mensuel environ 130, alors que la seule table des lignes de commande en exigerait environ 2,5 millions, et toute la base plus de 6 millions. La conclusion est nette : **le schéma et les chiffres calculés tiennent dans quelques centaines de jetons ; les données elles-mêmes, jamais.** Cela tombe bien, car c'est aussi ce qu'il faut faire pour la justesse (le modèle écrit le code, la base calcule) et pour la confidentialité (ce que vous n'envoyez pas ne peut pas fuir).

> 🧭 **En pratique.** On ne « colle » pas un fichier dans un modèle pour qu'il l'analyse. On lui donne : le **schéma**, les **règles métier**, quelques **exemples**, et, pour un commentaire, des **chiffres déjà calculés**. Le calcul reste dans la base ou dans pandas.

### 5.1.3 Le hasard et la température

Le modèle n'est pas forcé de choisir le jeton le plus probable. Un réglage appelé **température** contrôle le tirage : à température basse, il choisit presque toujours le meilleur candidat ; à température élevée, il explore des candidats moins probables. La figure applique ce réglage aux **vrais scores** du petit modèle pour la phrase précédente.

```python hide
F.fig_temperature(sorties["logits"])
```
<!--sortie-->
```text
figure : ch05-temperature.png
```
<!--sortie-->

![Probabilité du jeton suivant pour trois températures, calculée à partir des scores réels du petit modèle (0,3 resserre la distribution, 2 l'aplatit).](figures/ch05-temperature.png)

Pour un analyste, la conséquence se résume ainsi : **à température élevée, deux demandes identiques donnent deux réponses différentes**, ce qui est précieux pour rédiger et désastreux pour une requête que l'on veut reproductible. Simulons dix tirages pour deux réglages.

```python
rng = np.random.default_rng(3)
cand = np.array(lg["jetons"][:8])
def tirer(T, n=10):
    p = np.exp((sc[:8] - sc[:8].max()) / T)
    return [s.strip() for s in rng.choice(cand, n, p=p / p.sum())]
print("T = 0,3 :", tirer(0.3))
print("T = 1,5 :", tirer(1.5))
```
<!--sortie-->
```text
T = 0,3 : ['vec', 'vec', 'vec', 'vec', 'vec', 'vec', 'vec', 'vec', 'vec', 'vec']
T = 1,5 : ['ins', 'ins', 'ins', 'ins', 'uss', '-', 'vec', '', '', 'vec']
```
<!--sortie-->

À 0,3, les dix tirages sont identiques ; à 1,5, ils varient (les jetons vides sont des espaces).

> ⚠️ **Température nulle ne veut pas dire reproductible.** Même au réglage le plus bas, un service hébergé peut changer de version de modèle sans prévenir, ou arrondir différemment selon la charge. Reproductible veut dire : **on enregistre la requête qu'on a acceptée**, pas « on redemandera ». C'est exactement ce que fait ce chapitre : les sorties du petit modèle sont enregistrées dans un fichier versionné, et c'est ce fichier que le livre relit.

### 5.1.4 Quelles données envoyer, et où

La question qui précède toutes les autres : **que le modèle voit-il ?** Un modèle **hébergé** reçoit votre texte sur les machines d'un fournisseur ; un modèle **local** tourne sur votre machine ou votre réseau, au prix d'une qualité souvent moindre et d'un travail d'installation. Le tableau fixe une règle simple, à adapter à la politique de votre organisation.

| Ce que contient la consigne | Hébergé | Local |
|---|---|---|
| Le **schéma** (noms de tables et colonnes), les règles métier, des questions | en général acceptable | oui |
| Des **agrégats** déjà calculés (chiffre d'affaires du mois, taux de retard) | acceptable si l'organisation l'autorise | oui |
| Des **lignes individuelles** de clients, de salariés, de patients, de contrats | **non**, sauf accord explicite et cadre contractuel | possible, avec accès contrôlé |
| Des **identifiants directs ou indirects** (nom, e-mail, téléphone, adresse) | **non** | à éviter même en local |
| Des **secrets** (mots de passe, clés d'accès, chaînes de connexion) | **jamais**, dans aucun cas | jamais |

« Sans nom » ne veut pas dire « anonyme ». Mesurons-le sur les clients de la boutique : combien sont les seuls à partager leur année de naissance et leur ville ?

```python
k = con.execute("""SELECT n_groupe, COUNT(*) AS clients FROM
                   (SELECT COUNT(*) OVER (PARTITION BY annee_naissance, ville) AS n_groupe FROM clients)
                   GROUP BY n_groupe ORDER BY n_groupe LIMIT 3""").fetchdf()
print(k.to_string(index=False))
```
<!--sortie-->
```text
 n_groupe  clients
        1      203
        2      326
        3      384
```
<!--sortie-->

Sur 6 000 clients, 203 sont **seuls** de leur ville et de leur année de naissance, et 326 autres ne partagent cette combinaison qu'avec une personne. Deux colonnes anodines suffisent donc à isoler quelqu'un dès qu'on y ajoute un peu de contexte (une date d'inscription, un montant). La **sécurité** vient d'abord de ce que l'on n'envoie pas, ensuite de contrats, et seulement après de bonnes intentions.

### 5.1.5 Le prompt : un document de travail

Une **consigne** (*prompt*) n'est pas une formule magique, c'est un **brief** : ce qu'on écrirait à un collègue compétent mais qui ne connaît pas l'entreprise. Six parties reviennent presque toujours.

```python hide
F.fig_prompt()
```
<!--sortie-->
```text
figure : ch05-anatomie-prompt.png
```
<!--sortie-->

![Les six parties d'une consigne efficace.](figures/ch05-anatomie-prompt.png)

1. **Rôle et tâche** : ce qu'on attend, en une phrase (« écrivez une requête SELECT en dialecte DuckDB »).
2. **Contexte** : qui lit le résultat et pour quoi faire.
3. **Schéma** : tables, colonnes, types, descriptions, parfois des exemples de valeurs.
4. **Règles métier** : les définitions et les pièges qu'un nouveau collègue ignorerait.
5. **Exemples** : deux ou trois paires question → réponse, dans le format exact attendu.
6. **Format de sortie** : « une requête, rien d'autre », ou un JSON de forme donnée, pour que le résultat se vérifie par du code.

Voici la fin de la consigne que nous utiliserons en 5.2 (règles et exemples ; le schéma commenté précède).

```python
lignes = O.prompt_texte("Combien de clients ont commandé en 2025 ?", "v3").splitlines()
print("\n".join(l[:110] for l in lignes[-11:]))
```
<!--sortie-->
```text
-- Le chiffre d'affaires est la somme de lignes_commande.montant (montants TTC, TVA fictive de 20 %).
-- Les noms de produits ne sont pas uniques (60 noms pour 120 produits) : regrouper par id_produit.
-- frais_port est une valeur par commande : ne la sommez pas après une jointure avec lignes_commande.
-- Les données vont du 2023-01-01 au 2025-12-31 : « le dernier trimestre » veut dire le 4e trimestre 2025.
-- Écrivez UNE requête SELECT en dialecte DuckDB, sans commentaire.
-- Question : combien de commandes en 2023 ?
SELECT COUNT(*) FROM commandes WHERE date_commande >= DATE '2023-01-01' AND date_commande < DATE '2024-01-01';
-- Question : nombre de lignes par catégorie de produit
SELECT p.categorie, COUNT(*) AS n FROM lignes_commande l JOIN produits p USING (id_produit) GROUP BY p.categor
-- Question : Combien de clients ont commandé en 2025 ?
SELECT
```
<!--sortie-->

> 🧭 **En pratique : un prompt est du code.** On le met dans un fichier, on lui donne un **numéro de version**, on note ce qui a changé et pourquoi, et on le teste sur un jeu de questions fixe avant de le remplacer. La section 5.5 montre comment.

> ✅ **À retenir.** Un LLM **imite** des textes plausibles ; il ne consulte pas vos données, ne calcule pas, et peut répondre autrement demain. On lui fait donc **écrire du code** et **rédiger du texte à partir de chiffres calculés**, jamais lire vos données brutes ni garantir un résultat : la vérification est notre travail.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.1 (écrire un prompt de schéma), exercices 5.1 et 5.2.
