# Chapitre 6 : Outils de travail — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 6 du livre (Git, notebooks, ligne de commande, scripts, reproductibilité). Les **applications** reprennent, pas à pas et en entier, les séances que le livre ne fait qu'esquisser ; les **exercices** (avec corrigés) servent à s'entraîner seul. Tout se tape dans un **terminal** (Linux, macOS, Git Bash ou WSL) ; le fichier de données est `commandes.csv`, dans le dossier que la variable `$DONNEES` désigne (chez vous : l'endroit où vous avez rangé le dossier `donnees/` du livre). Les exemples Python s'exécutent depuis la racine du volume. Les sorties affichées sont les vraies.

```bash
mkdir -p ~/atelier
git config --global user.name "La gérante"
git config --global user.email "gerante@boutique.example"
git config --global init.defaultBranch main
```

```bash hide
export GIT_AUTHOR_DATE="2026-03-02T10:00:00+01:00"
export GIT_COMMITTER_DATE="2026-03-02T10:00:00+01:00"
```

> 💡 **Une astuce de reproductibilité (à ne pas reproduire chez vous).** Pour que les empreintes Git affichées ci-dessous soient toujours les mêmes, la date de toutes les versions est fixée artificiellement (variables `GIT_AUTHOR_DATE` et `GIT_COMMITTER_DATE`). Chez vous, Git utilise l'horloge : vos empreintes seront différentes, ce qui n'a aucune importance.

## Applications

### Application 6.1 — Une séance Git de A à Z

**Objectif.** Rejouer toute la vie d'un petit dépôt : le créer, photographier le travail, comparer, regarder à l'intérieur d'un commit, défaire des erreurs, ignorer des fichiers, étiqueter une version. *Section du livre : 6.1.*

**Étape 1 : un dossier, un script, un dépôt.**

```bash
mkdir -p ~/atelier/boutique
cd ~/atelier/boutique
cp "$DONNEES/commandes.csv" .
git init -q
cat > analyse.py <<'FIN'
import pandas as pd

df = pd.read_csv("commandes.csv")
print("Nombre de commandes :", len(df))
print("Montant moyen :", round(df["montant"].mean(), 2), "€")
FIN
python analyse.py
git status
```
<!--sortie-->
```text
Nombre de commandes : 400
Montant moyen : 60.25 €
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	analyse.py
	commandes.csv

nothing added to commit but untracked files present (use "git add" to track)
```

Git voit deux fichiers **non suivis** (*untracked*) : il les a remarqués mais ne les surveille pas encore. Rappel des trois zones : dossier de travail → (`git add`) → index → (`git commit`) → dépôt.

**Étape 2 : deux commits propres.** On enregistre d'abord le script, puis les données, en deux photos distinctes.

```bash
git add analyse.py
git status --short
git commit -q -m "Premier script : montant moyen des commandes"
git add commandes.csv
git commit -q -m "Ajout du fichier de données (400 commandes)"
git log --oneline
```
<!--sortie-->
```text
A  analyse.py
?? commandes.csv
1a81aa5 Ajout du fichier de données (400 commandes)
07eefcb Premier script : montant moyen des commandes
```

`git status --short` affiche une lettre par fichier : `A` (ajouté à l'index) pour `analyse.py`, `??` (non suivi) pour `commandes.csv`. Après les deux commits, `git log --oneline` montre une ligne par version.

**Étape 3 : regarder à l'intérieur d'un commit.** L'empreinte d'un blob est le SHA-1 de la chaîne `blob`, de la taille du contenu, d'un caractère nul et du contenu : on la calcule avec Git, puis à la main avec `sha1sum`.

```bash
echo "bonjour" > bonjour.txt
git hash-object bonjour.txt
printf 'blob 8\0bonjour\n' | sha1sum
rm bonjour.txt
```
<!--sortie-->
```text
1cd909e05d33f0f6bc4ea1caf19b5749b434ceb3
1cd909e05d33f0f6bc4ea1caf19b5749b434ceb3  -
```

Les deux empreintes sont identiques : Git hache simplement le contenu. Voyons le dernier commit et son arbre :

```bash
git cat-file -p HEAD
echo "---"
git cat-file -p 'HEAD^{tree}'
```
<!--sortie-->
```text
tree 25e41e984c9bfc34cd88069b6821dcf2a9176257
parent 07eefcb2bdc2698f8f0e9eb534afa347c96a5088
author La gérante <gerante@boutique.example> 1772442000 +0100
committer La gérante <gerante@boutique.example> 1772442000 +0100

Ajout du fichier de données (400 commandes)
---
100644 blob e6c6d1eb7801facd05a2164e7d875a2e82b1f3e0	analyse.py
100644 blob 3872f3a74145a4a12a3c77704adfe45a309b6f7b	commandes.csv
```

On lit d'abord le commit (empreinte de l'arbre, du parent, auteur, message), puis l'arbre : une ligne par fichier, avec le mode, le type `blob`, l'empreinte et le nom.

**Étape 4 : le cycle modifier, comparer, enregistrer.** La gérante veut le montant moyen par canal.

```bash
cat >> analyse.py <<'FIN'
print()
print("Montant moyen par canal :")
print(df.groupby("canal")["montant"].mean().round(2))
FIN
git status --short
git diff
```
<!--sortie-->
```text
 M analyse.py
diff --git a/analyse.py b/analyse.py
index e6c6d1e..7d5d285 100644
--- a/analyse.py
+++ b/analyse.py
@@ -3,3 +3,6 @@ import pandas as pd
 df = pd.read_csv("commandes.csv")
 print("Nombre de commandes :", len(df))
 print("Montant moyen :", round(df["montant"].mean(), 2), "€")
+print()
+print("Montant moyen par canal :")
+print(df.groupby("canal")["montant"].mean().round(2))
```

`git diff` montre les différences entre le dossier de travail et la dernière photo (`+` : ligne ajoutée ; `-` : ligne supprimée). Lançons le script, enregistrons, puis relisons l'historique avec le détail des fichiers touchés :

```bash
python analyse.py
git add analyse.py
git commit -q -m "Ajout du montant moyen par canal"
git log --stat | head -n 12
git show --stat HEAD~1 | head -n 8
```
<!--sortie-->
```text
Nombre de commandes : 400
Montant moyen : 60.25 €

Montant moyen par canal :
canal
Boutique    74.81
Réseaux     49.01
Site        59.50
Name: montant, dtype: float64
commit 511c5a6e737e6dde7fee3937a80290aa5e92e0d7
Author: La gérante <gerante@boutique.example>
Date:   Mon Mar 2 10:00:00 2026 +0100

    Ajout du montant moyen par canal

 analyse.py | 3 +++
 1 file changed, 3 insertions(+)

commit 1a81aa5eef7d5801ef4e929907514907fe0db2c8
Author: La gérante <gerante@boutique.example>
Date:   Mon Mar 2 10:00:00 2026 +0100
commit 1a81aa5eef7d5801ef4e929907514907fe0db2c8
Author: La gérante <gerante@boutique.example>
Date:   Mon Mar 2 10:00:00 2026 +0100

    Ajout du fichier de données (400 commandes)

 commandes.csv | 401 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 401 insertions(+)
```

**Étape 5 : défaire une erreur, trois situations.** *Situation 1 : « J'ai cassé un fichier, je veux la version du dernier commit. »* La gérante, fatiguée, efface tout le contenu de son script.

```bash
wc -c analyse.py
> analyse.py
wc -c analyse.py
python analyse.py
git restore analyse.py
wc -c analyse.py
python analyse.py | head -n 2
```
<!--sortie-->
```text
256 analyse.py
0 analyse.py
256 analyse.py
Nombre de commandes : 400
Montant moyen : 60.25 €
```

`wc -c` compte les octets. La ligne `> analyse.py` **vide** le fichier : 0 octet, et le script n'affiche plus rien. `git restore` ramène le fichier à l'état du dernier commit. Ce que Git n'a jamais photographié, il ne peut pas le retrouver : **commits petits et fréquents**.

*Situation 2 : « J'ai enregistré une erreur ; je l'ai déjà partagée ou je veux garder une trace. »* On annule par un **nouveau commit** qui fait l'inverse (`git revert`) : l'historique reste intact.

```bash
echo 'print("TODO supprimer cette ligne")' >> analyse.py
git commit -q -am "Ligne de debug oubliée"
git revert --no-edit HEAD
git log --format='%h  %s'
python analyse.py | tail -n 1
```
<!--sortie-->
```text
[main fe75e16] Revert "Ligne de debug oubliée"
 Date: Mon Mar 2 10:00:00 2026 +0100
 1 file changed, 1 deletion(-)
fe75e16  Revert "Ligne de debug oubliée"
c057bea  Ligne de debug oubliée
511c5a6  Ajout du montant moyen par canal
1a81aa5  Ajout du fichier de données (400 commandes)
07eefcb  Premier script : montant moyen des commandes
Name: montant, dtype: float64
```

(L'option `-a` de `commit` ajoute automatiquement tous les fichiers **déjà suivis** et modifiés ; on vérifie quand même avec `git status` avant.) L'historique contient l'erreur *et* son annulation, et le script est redevenu propre.

*Situation 3 : « Je veux revoir l'état du dossier à une date passée. »* On se déplace temporairement dans l'historique avec `git switch --detach`, puis on revient.

```bash
git switch --detach HEAD~3 2>&1 | head -n 1
cat analyse.py
git switch main
```
<!--sortie-->
```text
HEAD is now at 1a81aa5 Ajout du fichier de données (400 commandes)
import pandas as pd

df = pd.read_csv("commandes.csv")
print("Nombre de commandes :", len(df))
print("Montant moyen :", round(df["montant"].mean(), 2), "€")
Previous HEAD position was 1a81aa5 Ajout du fichier de données (400 commandes)
Switched to branch 'main'
```

On y voit le script tel qu'il était, **sans** le calcul par canal. On peut regarder et lancer le code, mais on ne doit pas y travailler (Git parle d'état *detached HEAD*).

**Étape 6 : ignorer des fichiers.** Les fichiers temporaires, l'environnement virtuel et surtout les **secrets** n'ont pas leur place dans l'historique.

```bash
mkdir -p .venv __pycache__
touch .venv/pyvenv.cfg __pycache__/analyse.cpython-313.pyc secrets.env
git status --short
cat > .gitignore <<'FIN'
# environnement et fichiers temporaires
.venv/
__pycache__/
*.pyc
.ipynb_checkpoints/
# secrets : JAMAIS dans Git
*.env
FIN
git status --short
```
<!--sortie-->
```text
?? .venv/
?? __pycache__/
?? secrets.env
?? .gitignore
```

Après l'ajout du `.gitignore`, il ne reste que ce fichier lui-même, que l'on **veut** suivre (pour que toute l'équipe ignore les mêmes choses). `git check-ignore -v` explique pourquoi un fichier est ignoré, et la dernière commande pose une étiquette sur la version :

```bash
git add .gitignore
git commit -q -m "Ajout du .gitignore"
git check-ignore -v secrets.env
git tag -a v1.0-rapport-banque -m "Version remise à la banque (mars 2026)"
git tag
git show --stat v1.0-rapport-banque | head -n 6
```
<!--sortie-->
```text
.gitignore:7:*.env	secrets.env
v1.0-rapport-banque
tag v1.0-rapport-banque
Tagger: La gérante <gerante@boutique.example>
Date:   Mon Mar 2 10:00:00 2026 +0100

Version remise à la banque (mars 2026)
```

> ⚠️ **Un secret commité est un secret perdu.** Le retirer dans un commit suivant ne suffit pas : il reste lisible dans l'historique. Mettez `.gitignore` en place **avant** de créer le fichier secret.

**Pour aller plus loin.** Écrivez un message de commit que vous comprendriez dans six mois pour chacun des commits de l'étape 4 ; puis essayez `git diff HEAD~1 HEAD` et `git diff --staged` après avoir modifié le script sans le commiter.

### Application 6.2 — Branches, fusions et conflits

**Objectif.** Tester une idée sur une branche, fusionner (cas facile, cas automatique, cas conflictuel) et résoudre un conflit à la main. *À la suite de l'application 6.1 (même dépôt `~/atelier/boutique`). Section du livre : 6.1.8.*

**Une expérience sur une branche.** La gérante se demande à partir de quel montant offrir la livraison. Elle ouvre une branche dédiée.

```bash
cd ~/atelier/boutique
git branch
git switch -c seuil-livraison
git branch
```
<!--sortie-->
```text
* main
Switched to a new branch 'seuil-livraison'
  main
* seuil-livraison
```

L'étoile `*` marque la branche courante. Travaillons dessus : on ajoute un seuil de livraison gratuite et on calcule la part de commandes concernées.

```bash
cat >> analyse.py <<'FIN'

SEUIL = 80  # seuil de livraison gratuite (€)
part = (df["montant"] >= SEUIL).mean()
print(f"Part des commandes dès {SEUIL} € : {part:.1%}")
FIN
python analyse.py | tail -n 2
git commit -q -am "Seuil de livraison gratuite à 80 €"
git switch main
tail -n 3 analyse.py
```
<!--sortie-->
```text
Name: montant, dtype: float64
Part des commandes dès 80 € : 21.8%
Switched to branch 'main'
print()
print("Montant moyen par canal :")
print(df.groupby("canal")["montant"].mean().round(2))
```

Retour sur `main` : les lignes du seuil ont **disparu** du fichier, car elles n'existent que sur la branche. En repassant sur la branche, tout revient.

**Fusion facile : l'avance rapide.** `main` n'a pas bougé depuis la création de la branche : Git se contente d'avancer le pointeur de `main` (*fast-forward*).

```bash
git merge seuil-livraison
git log --oneline --graph | head -n 4
git branch -d seuil-livraison
```
<!--sortie-->
```text
Updating 9687a07..247efd8
Fast-forward
 analyse.py | 4 ++++
 1 file changed, 4 insertions(+)
* 247efd8 Seuil de livraison gratuite à 80 €
* 9687a07 Ajout du .gitignore
* fe75e16 Revert "Ligne de debug oubliée"
* c057bea Ligne de debug oubliée
Deleted branch seuil-livraison (was 247efd8).
```

**Les deux ont bougé : fusion automatique.** Sam teste un seuil plus bas (60 €) sur sa branche ; la gérante, en parallèle sur `main`, ajoute une moyenne de satisfaction.

```bash
git switch -c seuil-sam
sed -i 's/^SEUIL = 80.*/SEUIL = 60  # seuil proposé par Sam (€)/' analyse.py
git commit -q -am "Seuil à 60 € (proposition de Sam)"
git switch main
cat >> analyse.py <<'FIN'

print("Satisfaction moyenne :", round(df["satisfaction"].mean(), 2))
FIN
git commit -q -am "Ajout de la satisfaction moyenne"
git log --oneline --graph --all | head -n 4
```
<!--sortie-->
```text
Switched to a new branch 'seuil-sam'
Switched to branch 'main'
* 112a992 Ajout de la satisfaction moyenne
| * b82cc85 Seuil à 60 € (proposition de Sam)
|/  
* 247efd8 Seuil de livraison gratuite à 80 €
```

Le graphe a la forme d'un « Y » : les deux branches sont parties du même commit et ont chacune avancé. Fusionnons celle de Sam :

```bash
git merge --no-edit seuil-sam
git log --oneline --graph | head -n 5
python analyse.py | tail -n 3
```
<!--sortie-->
```text
Auto-merging analyse.py
Merge made by the 'ort' strategy.
 analyse.py | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
*   752a0ca Merge branch 'seuil-sam'
|\  
| * b82cc85 Seuil à 60 € (proposition de Sam)
* | 112a992 Ajout de la satisfaction moyenne
|/  
Name: montant, dtype: float64
Part des commandes dès 60 € : 41.0%
Satisfaction moyenne : 3.96
```

Git a réussi **automatiquement** : les deux changements portaient sur des zones différentes du fichier. Il a créé un **commit de fusion** à deux parents. Python confirme que le script fonctionne et applique bien les deux modifications.

**Un conflit.** Un conflit survient quand deux branches modifient **la même ligne** de façons différentes. La gérante veut un seuil de 70 €, Sam de 65 €.

```bash
git switch -c seuil-gerante
sed -i 's/^SEUIL = .*/SEUIL = 70  # seuil retenu par la gérante (€)/' analyse.py
git commit -q -am "Seuil à 70 €"
git switch main
sed -i 's/^SEUIL = .*/SEUIL = 65  # compromis de Sam (€)/' analyse.py
git commit -q -am "Seuil à 65 €"
git merge --no-edit seuil-gerante
```
<!--sortie-->
```text
Switched to a new branch 'seuil-gerante'
Switched to branch 'main'
Auto-merging analyse.py
CONFLICT (content): Merge conflict in analyse.py
Automatic merge failed; fix conflicts and then commit the result.
```

Git s'arrête : `CONFLICT (content)`. Le dépôt est en cours de fusion ; consultons l'état puis le fichier.

```bash
git status --short
grep -n -A6 '<<<<<<<' analyse.py
```
<!--sortie-->
```text
UU analyse.py
10:<<<<<<< HEAD
11-SEUIL = 65  # compromis de Sam (€)
12-=======
13-SEUIL = 70  # seuil retenu par la gérante (€)
14->>>>>>> seuil-gerante
15-part = (df["montant"] >= SEUIL).mean()
16-print(f"Part des commandes dès {SEUIL} € : {part:.1%}")
```

Git a écrit, autour de la ligne litigieuse, trois **marqueurs** : `<<<<<<< HEAD` (version de la branche où l'on se trouve : 65 €), `=======` (séparation) et `>>>>>>> seuil-gerante` (version qu'on fusionne : 70 €). Résoudre le conflit, c'est **éditer le fichier** pour ne garder que ce qu'on veut (ici, après discussion, 70 €), supprimer les marqueurs, déclarer le conflit réglé avec `git add`, et conclure par un commit.

```bash
sed -i '/^<<<<<<< /d; /^=======$/d; /^>>>>>>> /d; /^SEUIL = 65/d' analyse.py
grep -n '^SEUIL' analyse.py
python analyse.py | tail -n 3
git add analyse.py
git commit -q --no-edit
git log --oneline --graph | head -n 8
git branch -d seuil-sam seuil-gerante
```
<!--sortie-->
```text
10:SEUIL = 70  # seuil retenu par la gérante (€)
Name: montant, dtype: float64
Part des commandes dès 70 € : 29.2%
Satisfaction moyenne : 3.96
*   0f9316c Merge branch 'seuil-gerante'
|\  
| * ec2c633 Seuil à 70 €
* | 56af79a Seuil à 65 €
|/  
*   752a0ca Merge branch 'seuil-sam'
|\  
| * b82cc85 Seuil à 60 € (proposition de Sam)
Deleted branch seuil-sam (was b82cc85).
Deleted branch seuil-gerante (was ec2c633).
```

(Le long `sed` enlève les trois lignes de marqueurs et la ligne de la version de Sam. Avec un éditeur comme VS Code, vous cliquez sur « Accepter la modification actuelle / entrante » ; le principe est identique.) Avant de valider, **toujours relancer le code**.

**Pour aller plus loin.** Provoquez un second conflit, mais cette fois résolvez-le en gardant **les deux** modifications (par exemple deux seuils affichés côte à côte).

### Application 6.3 — Un dépôt partagé, simulé sans Internet

**Objectif.** Comprendre `push`, `clone` et `pull` avec un dépôt « distant » qui n'est qu'un autre dossier. *À la suite de l'application 6.2. Section du livre : 6.1.10.*

Un dépôt distant est souvent « nu » (*bare* : sans dossier de travail, car personne n'y édite directement). La gérante crée un dépôt partagé et y envoie son travail ; Sam le clone.

```bash
cd ~/atelier
git init -q --bare depot-partage.git
cd boutique
git remote add origin ~/atelier/depot-partage.git
git remote -v | sed "s|$HOME|~|"
git push -q -u origin main --tags 2>&1 | tail -n 3
cd ..
git clone -q depot-partage.git copie-sam
cd copie-sam
git config user.name "Sam"
git config user.email "sam@boutique.example"
git log --oneline | wc -l
```
<!--sortie-->
```text
origin	~/atelier/depot-partage.git (fetch)
origin	~/atelier/depot-partage.git (push)
13
```

(Le `sed` ne sert qu'à abréger le chemin en `~` pour l'affichage ; les deux `git config` donnent à ce clone sa propre identité, Sam travaillant sur une autre machine.) La dernière commande compte les commits reçus : tout l'historique de la gérante, fusions comprises. Sam travaille et envoie sa modification ; la gérante la récupère.

```bash
echo 'print("Commandes Réseaux :", (df["canal"] == "Réseaux").sum())' >> analyse.py
git commit -q -am "Ajout du nombre de commandes Réseaux"
git push -q origin main 2>&1 | tail -n 3
cd ../boutique
git pull -q origin main 2>&1 | tail -n 3
git log --format='%an : %s' | head -n 3
python analyse.py | tail -n 1
```
<!--sortie-->
```text
Sam : Ajout du nombre de commandes Réseaux
La gérante : Merge branch 'seuil-gerante'
La gérante : Seuil à 65 €
Commandes Réseaux : 138
```

Chaque commit porte le nom de son auteur, et le script affiche bien la nouvelle ligne. *Avec GitHub, le principe est le même* (adresse de la forme `git@github.com:nom/depot.git`), avec en plus la **pull request** pour relire avant de fusionner (non exécuté ici : cela demande un compte et une connexion).

**Pour aller plus loin.** Faites modifier la **même ligne** par la gérante et par Sam avant le `pull` : que se passe-t-il ? Résolvez le conflit comme dans l'application 6.2.

### Application 6.4 — Un notebook : le fabriquer, l'exécuter, l'exporter

**Objectif.** Constater qu'un notebook n'est qu'un fichier JSON, l'exécuter depuis un programme, puis l'exporter en script, en Markdown et en HTML. *Section du livre : 6.2.2 et 6.2.7.*

**Fabriquer le carnet.** Trois cellules : un titre, le chargement des données, un calcul par canal.

```python
import json
import nbformat
from nbformat import v4 as nbf

nb = nbf.new_notebook()
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nb.cells = [
    nbf.new_markdown_cell("# Ventes de la boutique\nMontant moyen des commandes, par canal.", id="titre"),
    nbf.new_code_cell("import pandas as pd\ndf = pd.read_csv('donnees/commandes.csv')\ndf.shape", id="chargement"),
    nbf.new_code_cell("df.groupby('canal')['montant'].mean().round(2)", id="par-canal"),
]
texte = nbformat.writes(nb)
print(texte[:700])
```
<!--sortie-->
```text
{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "titre",
   "metadata": {},
   "source": [
    "# Ventes de la boutique\n",
    "Montant moyen des commandes, par canal."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "chargement",
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "df = pd.read_csv('donnees/commandes.csv')\n",
    "df.shape"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "par-canal",
   "metadata": {},
   "outputs": [],
   "source": [
    "df.groupby('canal')['montant'].mean().round(2)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "p
```

On y reconnaît : une liste de `cells` ; pour chaque cellule, son `cell_type` (`markdown` ou `code`), sa `source`, et, pour les cellules de code, `execution_count` (vide tant que la cellule n'a pas tourné) et `outputs` (vide pour l'instant). Exécutons-le avec `nbclient`, la bibliothèque qui pilote un noyau depuis un programme (c'est ce que fait le bouton « Exécuter tout ») :

```python
from nbclient import NotebookClient

NotebookClient(nb, timeout=120, kernel_name="python3", record_timing=False,
               resources={"metadata": {"path": "."}}).execute()

for cellule in nb.cells:
    if cellule.cell_type == "code":
        print(f"[{cellule.execution_count}] {cellule.source.splitlines()[-1]}")
        for sortie in cellule.outputs:
            print("     ->", sortie.output_type, ":", sortie.data["text/plain"].replace("\n", "\n        "))
```
<!--sortie-->
```text
[1] df.shape
     -> execute_result : (400, 4)
[2] df.groupby('canal')['montant'].mean().round(2)
     -> execute_result : canal
        Boutique    74.81
        Réseaux     49.01
        Site        59.50
        Name: montant, dtype: float64
```

Chaque cellule de code porte désormais son **numéro d'exécution** et ses **sorties**, enregistrées dans le fichier. Un graphique serait stocké sous `image/png`, encodé en texte : un notebook avec beaucoup de graphiques devient volumineux.

**Exporter.** `nbconvert` transforme un notebook en d'autres formats. D'abord en script Python (le code seul), puis en rapport Markdown :

```python
from nbconvert import PythonExporter, MarkdownExporter

script, _ = PythonExporter().from_notebook_node(nb)
print(script)
rapport, _ = MarkdownExporter().from_notebook_node(nb)
print(rapport.replace("```", "~~~"))   # ~~~ à la place des accents graves, pour l'affichage dans le cahier
```
<!--sortie-->
```text
#!/usr/bin/env python
# coding: utf-8

# # Ventes de la boutique
# Montant moyen des commandes, par canal.

# In[1]:


import pandas as pd
df = pd.read_csv('donnees/commandes.csv')
df.shape


# In[2]:


df.groupby('canal')['montant'].mean().round(2)


# Ventes de la boutique
Montant moyen des commandes, par canal.


~~~python
import pandas as pd
df = pd.read_csv('donnees/commandes.csv')
df.shape
~~~




    (400, 4)




~~~python
df.groupby('canal')['montant'].mean().round(2)
~~~




    canal
    Boutique    74.81
    Réseaux     49.01
    Site        59.50
    Name: montant, dtype: float64
```

Le script contient le code de chaque cellule, précédé d'un commentaire `# In[1]:` ; le texte Markdown est transformé en commentaires. Le rapport contient le titre, le code de chaque cellule et ses sorties. **En ligne de commande**, avec l'option `--execute` qui rejoue d'abord tout le notebook dans un noyau neuf (la règle « Restart & Run All », automatisée) :

```bash
mkdir -p ~/atelier/notebook
cd ~/atelier/notebook
cp "$DONNEES/commandes.csv" .
python - <<'FIN'
import nbformat
from nbformat import v4 as nbf
nb = nbf.new_notebook(cells=[
    nbf.new_markdown_cell("# Satisfaction par canal", id="a"),
    nbf.new_code_cell("import pandas as pd\ndf = pd.read_csv('commandes.csv')\ndf.groupby('canal')['satisfaction'].mean().round(2)", id="b"),
])
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nbformat.write(nb, "satisfaction.ipynb")
FIN
jupyter nbconvert --to markdown --execute satisfaction.ipynb 2>&1 | grep -v -i warning
sed 's/```/~~~/' satisfaction.md
```
<!--sortie-->
```text
[NbConvertApp] Converting notebook satisfaction.ipynb to markdown
[NbConvertApp] Writing 265 bytes to satisfaction.md
# Satisfaction par canal


~~~python
import pandas as pd
df = pd.read_csv('commandes.csv')
df.groupby('canal')['satisfaction'].mean().round(2)
~~~




    canal
    Boutique    4.49
    Réseaux     3.72
    Site        3.79
    Name: satisfaction, dtype: float64
```

Pour obtenir un fichier HTML, remplacez `markdown` par `html` ; pour un PDF, `--to pdf` demande en plus une installation de LaTeX.

**Pour aller plus loin.** Ajoutez une cellule qui trace un histogramme des montants : que devient la taille du fichier `.ipynb` après exécution ?

### Application 6.5 — L'état caché, le détecteur d'ordre et le nettoyeur de sorties

**Objectif.** Reproduire le piège principal des notebooks (l'état caché), puis écrire deux petits outils : un détecteur de notebooks douteux et un nettoyeur de sorties avant commit. *À la suite de l'application 6.4 (le notebook `nb` est réutilisé). Sections du livre : 6.2.3, 6.2.4, 6.2.6.*

**Simuler un noyau.** Un dictionnaire `memoire` joue la mémoire du noyau, `executer` joue le rôle de `Maj + Entrée`. Trois cellules calculent le prix d'une commande : trois articles à 50 €, TVA à 19 %.

```python
memoire = {}

def executer(code):
    exec(code, memoire)

cellules = {
    "A": "prix_unitaire = 50",
    "B": "total = prix_unitaire * 3 * 1.19",
    "C": "print('Total TTC :', round(total, 2), '€')",
}
for nom in "ABC":                       # exécution normale : A, puis B, puis C
    executer(cellules[nom])
```
<!--sortie-->
```text
Total TTC : 178.5 €
```

Le total attendu est $50\times3\times1{,}19=178{,}5$ €. Maintenant la gérante corrige le prix à 80 €, relance A, puis C… en **oubliant B** :

```python
cellules["A"] = "prix_unitaire = 80"
executer(cellules["A"])
executer(cellules["C"])                 # on relance C, mais pas B !
```
<!--sortie-->
```text
Total TTC : 178.5 €
```

Le total est **toujours 178,5 €** : la variable `total` en mémoire date de l'ancienne exécution de B. Voici ce que donne une exécution propre, sur un noyau neuf :

```python
memoire = {}
for nom in "ABC":
    executer(cellules[nom])
print("Vérification à la main :", 80 * 3 * 1.19)
```
<!--sortie-->
```text
Total TTC : 285.6 €
Vérification à la main : 285.59999999999997
```

Le vrai total est **285,6 €**. (La ligne de vérification affiche `285.59999999999997` : l'artefact de virgule flottante vu en 1.5.) **Second exemple : la cellule supprimée.** La gérante définit une remise dans une cellule, l'utilise plus bas, puis supprime la cellule de la remise « pour faire propre » : tout marche encore, jusqu'à ce qu'un collègue ouvre le notebook.

```python
memoire = {}
executer("remise = 0.10")                           # cellule D, supprimée plus tard
executer("prix_remise = 80 * (1 - remise)")         # cellule E : utilise la variable de D
print("prix remisé (noyau de la gérante) :", memoire["prix_remise"])

memoire = {}                                        # noyau neuf chez un collègue, sans la cellule D
try:
    executer("prix_remise = 80 * (1 - remise)")
except NameError as erreur:
    print("collègue : NameError :", erreur)
```
<!--sortie-->
```text
prix remisé (noyau de la gérante) : 72.0
collègue : NameError : name 'remise' is not defined
```

**Le détecteur d'ordre suspect.** Un notebook exécuté d'un trait, sur un noyau neuf, affiche `[1]`, `[2]`, `[3]`… sans trou ni saut. Écrivons une fonction qui repère les numéros désordonnés, les cellules jamais exécutées et les erreurs enregistrées.

```python
import copy

def audit(carnet):
    """Retourne la liste des problèmes détectés dans un notebook déjà exécuté."""
    problemes = []
    code = [c for c in carnet.cells if c.cell_type == "code"]
    comptes = [c.execution_count for c in code]
    if any(n is None for n in comptes):
        problemes.append("au moins une cellule n'a jamais été exécutée")
    vus = [n for n in comptes if n is not None]
    if vus != list(range(1, len(vus) + 1)):
        problemes.append(f"numéros d'exécution {comptes} : pas 1, 2, 3… (ordre ou noyau douteux)")
    if any(s.output_type == "error" for c in code for s in c.outputs):
        problemes.append("une erreur est enregistrée dans les sorties")
    return problemes or ["OK : notebook exécuté dans l'ordre, sans erreur"]
```

```python
print("notebook de la gérante :", audit(nb))
douteux = copy.deepcopy(nb)                   # un notebook « bidouillé » : ordre d'exécution désordonné
douteux.cells[1].execution_count = 3
douteux.cells[2].execution_count = 1
print("notebook bidouillé  :", audit(douteux))
```
<!--sortie-->
```text
notebook de la gérante : ["OK : notebook exécuté dans l'ordre, sans erreur"]
notebook bidouillé  : ["numéros d'exécution [3, 1] : pas 1, 2, 3… (ordre ou noyau douteux)"]
```

Le détecteur ne *prouve* pas qu'un notebook est reproductible (la seule preuve est de le réexécuter), mais il repère les cas flagrants en une milliseconde. **Le nettoyeur de sorties.** Comme les sorties et les numéros sont stockés dans le fichier, la moindre ré-exécution modifie des dizaines de lignes : on ne garde dans Git que les sources.

```python
def nettoyer(carnet):
    """Copie du notebook sans sorties ni numéros d'exécution."""
    propre = copy.deepcopy(carnet)
    for c in propre.cells:
        if c.cell_type == "code":
            c.outputs = []
            c.execution_count = None
    return propre

complet, propre = nbformat.writes(nb), nbformat.writes(nettoyer(nb))
print("lignes du JSON avec sorties :", complet.count("\n"))
print("lignes du JSON sans sorties :", propre.count("\n"))
cellule = json.loads(propre)["cells"][2]
print("cellule 3 nettoyée :", cellule["execution_count"], cellule["outputs"])
```
<!--sortie-->
```text
lignes du JSON avec sorties : 81
lignes du JSON sans sorties : 55
cellule 3 nettoyée : None []
```

Dans la pratique, l'outil `nbstripout` fait ce nettoyage automatiquement à chaque commit. **Pour aller plus loin.** Étendez `audit` pour signaler un notebook dont la dernière cellule de code n'a pas de sortie, ou dont une cellule contient un chemin absolu (par exemple une chaîne qui commence par `/home/`).

### Application 6.6 — Explorer un fichier avec les outils du terminal

**Objectif.** Se repérer dans une arborescence, lire un CSV sans l'ouvrir, interroger les données avec `grep`, `cut`, `sort`, `uniq` et `awk`, et sauvegarder des résultats par redirection. *Sections du livre : 6.3.1 à 6.3.4.*

**Un projet bien rangé.** Les données brutes ne se modifient jamais, les notebooks explorent, `src` contient le code réutilisable, `rapports` reçoit les résultats.

```bash
cd ~/atelier
mkdir -p etude-ventes/{donnees,notebooks,src,rapports}
cd etude-ventes
cp "$DONNEES/commandes.csv" donnees/
touch README.md src/outils.py
pwd | sed "s|^$HOME|~|"
ls
find . -not -name '.' | sort
```
<!--sortie-->
```text
~/atelier/etude-ventes
README.md
donnees
notebooks
rapports
src
./README.md
./donnees
./donnees/commandes.csv
./notebooks
./rapports
./src
./src/outils.py
```

La syntaxe `{a,b,c}` est une **expansion d'accolades**. Pour **déplacer, renommer, supprimer** :

```bash
mv README.md LISEZMOI.md          # renommer
mv LISEZMOI.md README.md          # et on revient en arrière
cp -r rapports rapports-copie     # copier un dossier entier (-r : récursif)
rm -r rapports-copie              # supprimer un dossier et son contenu (sans corbeille !)
ls
```
<!--sortie-->
```text
README.md
donnees
notebooks
rapports
src
```

**Lire un fichier.**

```bash
cd donnees
head -n 5 commandes.csv
echo "..."
tail -n 3 commandes.csv
wc -l commandes.csv
```
<!--sortie-->
```text
canal,montant,livraison,satisfaction
Boutique,44.8,0,4
Site,34.5,2,4
Réseaux,88.2,5,4
Réseaux,30.1,4,4
...
Site,62.6,4,3
Réseaux,37.5,3,4
Site,31.4,4,4
401 commandes.csv
```

**Interroger les données.** Combien de commandes viennent des réseaux sociaux ? Combien par canal ? Quelles sont les trois plus grosses ?

```bash
grep -c Réseaux commandes.csv
tail -n +2 commandes.csv | cut -d, -f1 | sort | uniq -c | sort -rn
tail -n +2 commandes.csv | sort -t, -k2 -n -r | head -n 3
```
<!--sortie-->
```text
138
    148 Site
    138 Réseaux
    114 Boutique
Site,255.7,4,3
Site,243.8,5,3
Site,217.1,7,4
```

Le pipeline de la deuxième ligne : `tail -n +2` supprime l'en-tête, `cut -d, -f1` garde la colonne des canaux, `sort` regroupe, `uniq -c` compte, `sort -rn` classe. La troisième trie sur la 2ᵉ colonne (`-k2`), numériquement (`-n`), de la plus grande à la plus petite (`-r`) : la plus grosse commande atteint le maximum vu avec `describe()` au chapitre 3. Pour le montant moyen, il faut calculer, ce que fait `awk` : `$2` désigne la 2ᵉ colonne, `NR` le numéro de ligne.

```bash
awk -F, 'NR > 1 { somme += $2; n++ } END { printf "montant moyen : %.2f € sur %d commandes\n", somme/n, n }' commandes.csv
awk -F, 'NR > 1 { somme[$1] += $2; n[$1]++ }
         END { for (canal in n) printf "%-10s %.2f\n", canal, somme[canal]/n[canal] }' commandes.csv | sort
```
<!--sortie-->
```text
montant moyen : 60.25 € sur 400 commandes
Boutique   74.81
Réseaux    49.01
Site       59.50
```

La seconde commande calcule une moyenne **par canal** grâce à un tableau associatif (l'équivalent d'un dictionnaire Python) : ce sont les trois moyennes que `df.groupby("canal")["montant"].mean()` donne dans pandas.

**Rediriger vers des fichiers.** `>` écrase, `>>` ajoute, `2>` capte les messages d'erreur ; `$?` donne le code de sortie de la dernière commande (0 : succès).

```bash
cd ..
tail -n +2 donnees/commandes.csv | cut -d, -f1 | sort | uniq -c > rapports/commandes-par-canal.txt
echo "# généré par la ligne de commande" >> rapports/commandes-par-canal.txt
cat rapports/commandes-par-canal.txt

ls donnees/inexistant.csv 2> rapports/erreurs.txt
echo "code de sortie : $?"
cat rapports/erreurs.txt
```
<!--sortie-->
```text
    114 Boutique
    138 Réseaux
    148 Site
# généré par la ligne de commande
code de sortie : 2
ls: cannot access 'donnees/inexistant.csv': No such file or directory
```

**Pour aller plus loin.** Écrivez, avec seulement des outils du terminal, la liste des commandes de plus de 150 € livrées en plus de 5 jours (colonnes 2 et 3), puis comptez-les.

### Application 6.7 — Un outil en ligne de commande, avec ses codes de sortie

**Objectif.** Écrire un script Python qui prend un fichier en argument et respecte la convention des codes de sortie (0 : succès ; non nul : erreur). *À la suite de l'application 6.6. Section du livre : 6.3.5.*

Les arguments tapés après le nom du script sont dans la liste `sys.argv` (`sys.argv[0]` est le nom du script).

```bash
cat > src/resume.py <<'FIN'
"""Résumé rapide d'un fichier CSV : python src/resume.py fichier.csv"""
import sys
import pandas as pd

if len(sys.argv) != 2:
    print("usage : python src/resume.py fichier.csv")
    sys.exit(2)

try:
    df = pd.read_csv(sys.argv[1])
except FileNotFoundError:
    print(f"fichier introuvable : {sys.argv[1]}")
    sys.exit(1)

print(f"{len(df)} lignes, {df.shape[1]} colonnes")
print(df.describe().loc[["mean", "min", "max"]].round(2))
FIN
python src/resume.py donnees/commandes.csv
echo "code de sortie : $?"
python src/resume.py donnees/absent.csv
echo "code de sortie : $?"
python src/resume.py
echo "code de sortie : $?"
```
<!--sortie-->
```text
400 lignes, 4 colonnes
      montant  livraison  satisfaction
mean    60.25       3.29          3.96
min      8.60       0.00          1.00
max    255.70      13.00          5.00
code de sortie : 0
fichier introuvable : donnees/absent.csv
code de sortie : 1
usage : python src/resume.py fichier.csv
code de sortie : 2
```

Le script renvoie **0** quand tout va bien, **1** pour un fichier absent, **2** pour un mauvais usage. Ces codes permettent à d'autres programmes d'enchaîner les étapes automatiquement et de s'arrêter proprement en cas de problème. **Pour aller plus loin.** Ajoutez une option facultative donnant le nom de la colonne à résumer, et un code de sortie 3 si cette colonne n'existe pas.

### Application 6.8 — Des scripts shell et un petit pipeline

**Objectif.** Écrire un script shell avec arguments, test, boucle et substitution de commande, l'enchaîner avec le script Python, et mesurer ce que `set -e` apporte. *À la suite de l'application 6.7. Section du livre : 6.4.1 et 6.4.2.*

**Un premier script.** Il affiche, pour un fichier de commandes, le nombre de commandes par canal et leur part. On l'écrit en deux morceaux (`>` crée le fichier, `>>` ajoute la suite).

```bash
mkdir -p scripts
cat > scripts/rapport.sh <<'FIN'
#!/usr/bin/env bash
# rapport.sh : nombre de commandes par canal, avec leur part
# usage : bash scripts/rapport.sh donnees/commandes.csv
set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "usage : $0 fichier.csv" >&2
    exit 2
fi
fichier="$1"
if [ ! -f "$fichier" ]; then
    echo "fichier introuvable : $fichier" >&2
    exit 1
fi
FIN
```

Seconde moitié du script : le calcul et la boucle sur les canaux.

```bash
cat >> scripts/rapport.sh <<'FIN'

total=$(( $(wc -l < "$fichier") - 1 ))
echo "== Rapport sur $fichier ($total commandes) =="
for canal in Boutique Réseaux Site; do
    n=$(grep -c "^$canal," "$fichier")
    part=$(awk -v n="$n" -v t="$total" 'BEGIN { printf "%.1f", 100 * n / t }')
    echo "  $canal : $n commandes ($part %)"
done
FIN
bash scripts/rapport.sh donnees/commandes.csv
```
<!--sortie-->
```text
== Rapport sur donnees/commandes.csv (400 commandes) ==
  Boutique : 114 commandes (28.5 %)
  Réseaux : 138 commandes (34.5 %)
  Site : 148 commandes (37.0 %)
```

Relisez le script : le **shebang** (`#!/usr/bin/env bash`) dit avec quel programme l'exécuter ; `set -euo pipefail` est la ceinture de sécurité (`-e` : s'arrêter à la première erreur ; `-u` : refuser une variable jamais définie ; `-o pipefail` : faire échouer un pipeline si l'une de ses commandes échoue) ; `$#` est le nombre d'arguments, `>&2` écrit sur la sortie d'erreur ; `$(( … ))` fait de l'arithmétique entière ; `awk` calcule le pourcentage (le shell ne sait pas faire de décimales). On peut rendre le script exécutable et tester ses garde-fous :

```bash
chmod +x scripts/rapport.sh
./scripts/rapport.sh donnees/commandes.csv | head -n 2
bash scripts/rapport.sh donnees/absent.csv
echo "code de sortie : $?"
bash scripts/rapport.sh
echo "code de sortie : $?"
```
<!--sortie-->
```text
== Rapport sur donnees/commandes.csv (400 commandes) ==
  Boutique : 114 commandes (28.5 %)
fichier introuvable : donnees/absent.csv
code de sortie : 1
usage : scripts/rapport.sh fichier.csv
code de sortie : 2
```

**Une boucle sur des fichiers.** Séparons le fichier de données en un fichier par canal, en recopiant l'en-tête dans chacun. Le `*` est un **joker** qui désigne tous les fichiers d'un motif.

```bash
mkdir -p donnees/par-canal
for canal in Boutique Réseaux Site; do
    (head -n 1 donnees/commandes.csv; grep "^$canal," donnees/commandes.csv) > "donnees/par-canal/$canal.csv"
done
wc -l donnees/par-canal/*.csv
```
<!--sortie-->
```text
 115 donnees/par-canal/Boutique.csv
 139 donnees/par-canal/Réseaux.csv
 149 donnees/par-canal/Site.csv
 403 total
```

Chaque fichier compte une ligne de plus que son nombre de commandes (l'en-tête) ; le total est donc de 400 commandes + 3 en-têtes.

**Un petit pipeline.** Un vrai projet est une chaîne d'étapes. Ce script appelle le script shell puis le programme Python de l'application 6.7.

```bash
cat > scripts/pipeline.sh <<'FIN'
#!/usr/bin/env bash
set -euo pipefail
echo "[1/3] comptage par canal"
bash scripts/rapport.sh "$1" > rapports/rapport.txt
echo "[2/3] résumé des colonnes numériques"
python src/resume.py "$1" >> rapports/rapport.txt
echo "[3/3] terminé : rapport dans rapports/rapport.txt"
FIN
bash scripts/pipeline.sh donnees/commandes.csv
cat rapports/rapport.txt
```
<!--sortie-->
```text
[1/3] comptage par canal
[2/3] résumé des colonnes numériques
[3/3] terminé : rapport dans rapports/rapport.txt
== Rapport sur donnees/commandes.csv (400 commandes) ==
  Boutique : 114 commandes (28.5 %)
  Réseaux : 138 commandes (34.5 %)
  Site : 148 commandes (37.0 %)
400 lignes, 4 colonnes
      montant  livraison  satisfaction
mean    60.25       3.29          3.96
min      8.60       0.00          1.00
max    255.70      13.00          5.00
```

**Échouer bruyamment.** Que se passe-t-il quand les données sont introuvables, **avec** puis **sans** la ceinture de sécurité (une copie du script d'où la ligne `set` est retirée) ?

```bash
echo "--- avec set -euo pipefail ---"
bash scripts/pipeline.sh donnees/absent.csv
echo "code de sortie : $?"
echo
echo "--- sans set -e (script imprudent) ---"
sed '/^set -euo/d' scripts/pipeline.sh > scripts/pipeline-imprudent.sh
bash scripts/pipeline-imprudent.sh donnees/absent.csv
echo "code de sortie : $?"
```
<!--sortie-->
```text
--- avec set -euo pipefail ---
[1/3] comptage par canal
fichier introuvable : donnees/absent.csv
code de sortie : 1

--- sans set -e (script imprudent) ---
[1/3] comptage par canal
fichier introuvable : donnees/absent.csv
[2/3] résumé des colonnes numériques
[3/3] terminé : rapport dans rapports/rapport.txt
code de sortie : 0
```

Avec `set -e`, le script s'arrête net à la première étape défaillante et renvoie un code d'erreur. Sans elle, il continue, annonce « terminé » et renvoie le code 0 (succès !) alors que **rien n'a été calculé** : le pire des scénarios. **Un script qui échoue doit échouer bruyamment.** **Pour aller plus loin.** Ajoutez une quatrième étape au pipeline qui vérifie que `rapports/rapport.txt` n'est pas vide, et testez-la en simulant une panne de l'étape 2.

### Application 6.9 — Environnements virtuels : deux mondes sur une machine

**Objectif.** Créer un environnement virtuel, y installer une bibliothèque, figer les versions, reconstruire l'environnement ailleurs, et faire cohabiter deux versions d'une même bibliothèque. *Cette application télécharge un petit paquet (`tabulate`) : elle demande une connexion. À la suite de l'application 6.8. Sections du livre : 6.3.6 et 6.4.4.*

```bash
cd ~/atelier/etude-ventes
python -m venv .venv
source .venv/bin/activate
python -c "import sys; print('environnement virtuel actif :', sys.prefix != sys.base_prefix)"
pip list 2>/dev/null
```
<!--sortie-->
```text
environnement virtuel actif : True
Package Version
------- -------
pip     25.0
```

L'environnement est **vierge** : il ne contient que `pip` lui-même. Installons une petite bibliothèque, `tabulate` (qui formate des tableaux en texte), et vérifions qu'elle fonctionne :

```bash
pip install --quiet tabulate 2>&1 | grep -v -i -E "notice|warning"
python -c "from tabulate import tabulate; print(tabulate([['Boutique', 74.81], ['Réseaux', 49.01], ['Site', 59.5]], headers=['canal', 'montant moyen'], floatfmt='.2f'))"
pip freeze
pip freeze > requirements.txt
cat requirements.txt
deactivate
```
<!--sortie-->
```text
canal       montant moyen
--------  ---------------
Boutique            74.81
Réseaux             49.01
Site                59.50
tabulate==0.10.0
tabulate==0.10.0
```

`pip freeze` liste ce qui est installé avec les **versions exactes** : c'est la clé de la reproductibilité. Quelqu'un qui reçoit le projet reconstruit **le même environnement** en trois commandes :

```bash
python -m venv .venv-collegue
source .venv-collegue/bin/activate
pip install --quiet -r requirements.txt 2>&1 | grep -v -i -E "notice|warning"
pip freeze
deactivate
```
<!--sortie-->
```text
tabulate==0.10.0
```

La liste obtenue est **identique**. **Deux versions d'une même bibliothèque.** Créons un second environnement, `.venv-ancien`, avec une version plus ancienne exigée par `==` ; les deux coexistent sans se gêner (on appelle ici directement le `pip` de chaque environnement, sans l'activer : c'est équivalent et très pratique dans un script).

```bash
python -m venv .venv-ancien
.venv-ancien/bin/pip install --quiet "tabulate==0.8.10" 2>&1 | grep -v -i -E "notice|warning"
echo "projet ancien :"
.venv-ancien/bin/pip freeze
echo "projet récent :"
.venv/bin/pip freeze
```
<!--sortie-->
```text
projet ancien :
tabulate==0.8.10
projet récent :
tabulate==0.10.0
```

**Pour aller plus loin.** Écrivez un `requirements.txt` à la main qui accepte n'importe quelle version 0.9.x de `tabulate` (écriture `>=0.9,<0.10`) et vérifiez ce que `pip install -r` installe.

### Application 6.10 — Un rapport reproductible, de Markdown à PDF, avec `make`

**Objectif.** Assembler les outils : graines aléatoires, relevé d'environnement, rapport dont les chiffres sont calculés, conversion avec Pandoc, `Makefile`, empreinte des données. *À la suite de l'application 6.9. Sections du livre : 6.5.2 à 6.5.5 et 6.5.8.*

**Les graines.** Sans graine, deux exécutions donnent des tirages différents ; avec la même graine, des tirages identiques.

```python
import numpy as np
import pandas as pd

montants = pd.read_csv("donnees/commandes.csv")["montant"].to_numpy()

def moyenne_echantillon(rng, taille=10):
    return montants[rng.choice(len(montants), size=taille, replace=False)].mean()

a = moyenne_echantillon(np.random.default_rng())
b = moyenne_echantillon(np.random.default_rng())
print("sans graine, deux exécutions identiques ?", a == b)
c = moyenne_echantillon(np.random.default_rng(42))
d = moyenne_echantillon(np.random.default_rng(42))
print("graine 42 deux fois :", round(c, 2), "et", round(d, 2), "-> identiques ?", c == d)
```
<!--sortie-->
```text
sans graine, deux exécutions identiques ? False
graine 42 deux fois : 46.55 et 46.55 -> identiques ? True
```

La graine sert à **figer** une exécution, pas à l'améliorer. Pour vérifier qu'un résultat n'est pas un accident de graine, on l'observe pour **plusieurs graines** :

```python
moyennes = [moyenne_echantillon(np.random.default_rng(graine)) for graine in range(1, 9)]
print("moyennes pour les graines 1 à 8 :", [round(float(m), 1) for m in moyennes])
print("vraie moyenne de la population  :", round(montants.mean(), 2))
```
<!--sortie-->
```text
moyennes pour les graines 1 à 8 : [54.1, 60.5, 45.2, 63.4, 71.8, 73.3, 59.5, 43.3]
vraie moyenne de la population  : 60.25
```

**Relever l'environnement.** On peut imprimer, en fin de rapport, ce qui a réellement servi :

```python
import sys
import importlib.metadata as meta

def empreinte_environnement(paquets=("numpy", "pandas", "scipy", "matplotlib")):
    lignes = [f"Python {sys.version.split()[0]}"]
    lignes += [f"{p} {meta.version(p)}" for p in paquets]
    return lignes

print("\n".join(empreinte_environnement()))
```
<!--sortie-->
```text
Python 3.13.3
numpy 2.5.3
pandas 3.0.6
scipy 1.18.1
matplotlib 3.11.2
```

**Un rapport qui se fabrique tout seul.** Un programme Python **écrit** un document Markdown en y insérant les chiffres calculés (aucun chiffre en dur). On l'écrit en deux morceaux.

```bash
cd ~/atelier/etude-ventes
cat > src/faire_rapport.py <<'FIN'
"""Écrit sur la sortie standard un rapport Markdown : python src/faire_rapport.py commandes.csv"""
import sys
import numpy as np
import pandas as pd

def fr(x, decimales=2):
    """Nombre au format français : virgule décimale."""
    return f"{x:.{decimales}f}".replace(".", ",")

df = pd.read_csv(sys.argv[1])
n = len(df)
m = df["montant"]
marge = 1.96 * m.std() / np.sqrt(n)           # demi-largeur de l'intervalle de confiance à 95 %
par_canal = df.groupby("canal")["montant"].agg(["count", "mean"]).sort_index()
FIN
```

Seconde moitié du programme : l'écriture du document, en Markdown.

```bash
cat >> src/faire_rapport.py <<'FIN'

print("---")
print('title: "Les ventes de la boutique"')
print("lang: fr")
print("---")
print()
print(f"Le fichier contient **{n} commandes**. Le montant moyen est de **{fr(m.mean())} €** "
      f"(intervalle de confiance à 95 % : de {fr(m.mean() - marge)} à {fr(m.mean() + marge)} €), "
      f"et la médiane de **{fr(m.median())} €**.")
print()
print("L'intervalle est calculé par $\\bar{x} \\pm 1{,}96\\,\\frac{s}{\\sqrt{n}}$.")
print()
print("| Canal | Commandes | Montant moyen (€) |")
print("|:------|----------:|-------------------:|")
for canal, ligne in par_canal.iterrows():
    print(f"| {canal} | {int(ligne['count'])} | {fr(ligne['mean'])} |")
print()
print(f"Le canal au panier moyen le plus élevé est **{par_canal['mean'].idxmax()}**.")
FIN
python src/faire_rapport.py donnees/commandes.csv > rapports/rapport-ventes.md
cat rapports/rapport-ventes.md
```
<!--sortie-->
```text
---
title: "Les ventes de la boutique"
lang: fr
---

Le fichier contient **400 commandes**. Le montant moyen est de **60,25 €** (intervalle de confiance à 95 % : de 56,52 à 63,97 €), et la médiane de **51,00 €**.

L'intervalle est calculé par $\bar{x} \pm 1{,}96\,\frac{s}{\sqrt{n}}$.

| Canal | Commandes | Montant moyen (€) |
|:------|----------:|-------------------:|
| Boutique | 114 | 74,81 |
| Réseaux | 138 | 49,01 |
| Site | 148 | 59,50 |

Le canal au panier moyen le plus élevé est **Boutique**.
```

(Les doubles barres `\\` dans le programme sont des échappements Python pour obtenir une seule barre `\` dans la formule LaTeX.) **Pandoc** convertit le Markdown en HTML, en texte brut, en PDF :

```bash
pandoc --standalone --mathml rapports/rapport-ventes.md -o rapports/rapport-ventes.html
pandoc rapports/rapport-ventes.md -t plain | head -n 14
pandoc rapports/rapport-ventes.md -o rapports/rapport-ventes.pdf --pdf-engine=xelatex
head -c 5 rapports/rapport-ventes.pdf; echo
```
<!--sortie-->
```text
[WARNING] Could not convert TeX math \bar{x} \pm 1{,}96\,\frac{s}{\sqrt{n}}, rendering as TeX
Le fichier contient 400 commandes. Le montant moyen est de 60,25 €
(intervalle de confiance à 95 % : de 56,52 à 63,97 €), et la médiane de
51,00 €.

L’intervalle est calculé par $\bar{x} \pm 1{,}96\,\frac{s}{\sqrt{n}}$.

  Canal        Commandes   Montant moyen (€)
  ---------- ----------- -------------------
  Boutique           114               74,81
  Réseaux            138               49,01
  Site               148               59,50

Le canal au panier moyen le plus élevé est Boutique.
%PDF-
```

Pandoc **avertit** (`[WARNING]`) qu'il ne sait pas écrire une fraction en texte brut et laisse la formule en LaTeX : normal. Les cinq premiers octets du PDF sont `%PDF-`, la signature du format. **`make` : ne refaire que ce qui a changé.** On décrit dans un `Makefile` des règles *cible : dépendances* suivies de la commande ; `make` compare les dates de modification. (Les commandes doivent être indentées par une **vraie tabulation** ; nous écrivons `<TAB>` puis un `sed` le remplace.)

```bash
cat > Makefile <<'FIN'
.PHONY: tout propre

tout: rapports/rapport-ventes.html

rapports/rapport-ventes.md: donnees/commandes.csv src/faire_rapport.py
<TAB>python src/faire_rapport.py donnees/commandes.csv > $@

rapports/rapport-ventes.html: rapports/rapport-ventes.md
<TAB>pandoc --standalone --mathml $< -o $@

propre:
<TAB>rm -f rapports/rapport-ventes.md rapports/rapport-ventes.html
FIN
sed -i 's/^<TAB>/\t/' Makefile
make propre
make
echo "--- deuxième appel, rien n'a changé ---"
make
echo "--- on touche le fichier de données ---"
touch donnees/commandes.csv
make
```
<!--sortie-->
```text
rm -f rapports/rapport-ventes.md rapports/rapport-ventes.html
python src/faire_rapport.py donnees/commandes.csv > rapports/rapport-ventes.md
pandoc --standalone --mathml rapports/rapport-ventes.md -o rapports/rapport-ventes.html
--- deuxième appel, rien n'a changé ---
make: Nothing to be done for 'tout'.
--- on touche le fichier de données ---
python src/faire_rapport.py donnees/commandes.csv > rapports/rapport-ventes.md
pandoc --standalone --mathml rapports/rapport-ventes.md -o rapports/rapport-ventes.html
```

Dans les commandes, `$@` désigne la cible, `$<` la première dépendance. Le premier `make` refait **les deux** étapes, le deuxième répond qu'il n'y a **rien à faire**, et quand on « touche » les données, les deux étapes repartent. **Une empreinte des données.** On calcule celle de `commandes.csv`, on la note, et n'importe qui peut vérifier ; une faute de frappe fait sonner l'alerte avant même l'analyse.

```bash
sha256sum donnees/commandes.csv > donnees/EMPREINTES.sha256
cat donnees/EMPREINTES.sha256
sha256sum -c donnees/EMPREINTES.sha256
echo "--- une faute de frappe glisse dans le fichier ---"
sed -i '2s/44.8/448.0/' donnees/commandes.csv
sha256sum -c donnees/EMPREINTES.sha256 || echo "ALERTE : les données ont été modifiées"
sed -i '2s/448.0/44.8/' donnees/commandes.csv
sha256sum -c donnees/EMPREINTES.sha256
```
<!--sortie-->
```text
27f43bf0bf7fed83c6b0e313e8a6e212547175fb6d596de3141dfde256d88acc  donnees/commandes.csv
donnees/commandes.csv: OK
--- une faute de frappe glisse dans le fichier ---
donnees/commandes.csv: FAILED
sha256sum: WARNING: 1 computed checksum did NOT match
ALERTE : les données ont été modifiées
donnees/commandes.csv: OK
```

**Pour aller plus loin.** Ajoutez au `Makefile` une cible `verifier` qui contrôle l'empreinte des données, et faites dépendre le rapport de cette cible : `make` doit alors refuser de construire un rapport sur des données altérées.

### Application 6.11 — R Markdown et LaTeX

**Objectif.** Compiler un vrai document dynamique R Markdown (le texte et les chiffres naissent du même code), puis un minuscule document LaTeX. *Sections du livre : 6.5.6 et 6.5.7.*

R Markdown mélange texte Markdown et blocs de code. Comme le format utilise les trois accents graves que ce cahier emploie lui-même, nous écrivons les blocs avec des tildes `~~~` et un `sed` les remplace avant la compilation. Le document calcule la satisfaction moyenne des commandes livrées, en distinguant les livraisons rapides (3 jours ou moins) des autres.

```bash
mkdir -p ~/atelier/etude-rmd
cd ~/atelier/etude-rmd
cp "$DONNEES/commandes.csv" .
cat > rapport.Rmd <<'FIN'
---
title: "Satisfaction des clients de la boutique"
output: html_document
---

Voici le lien entre le délai de livraison et la note de satisfaction.

~~~{r}
d <- read.csv("commandes.csv")
d <- d[d$canal != "Boutique", ]      # on ne garde que les commandes livrées
tapply(d$satisfaction, d$livraison <= 3, mean)
~~~

La satisfaction moyenne des commandes livrées est de **`r round(mean(d$satisfaction), 2)`**
sur `r nrow(d)` commandes.
FIN
sed -i 's/^~~~{r}$/```{r}/; s/^~~~$/```/' rapport.Rmd
Rscript -e 'rmarkdown::render("rapport.Rmd", quiet = TRUE)'
ls
pandoc rapport.html -t plain
```
<!--sortie-->
```text
commandes.csv
rapport.Rmd
rapport.html
Satisfaction des clients de la boutique

Voici le lien entre le délai de livraison et la note de satisfaction.

    d <- read.csv("commandes.csv")
    d <- d[d$canal != "Boutique", ]      # on ne garde que les commandes livrées
    tapply(d$satisfaction, d$livraison <= 3, mean)

    ##    FALSE     TRUE 
    ## 3.631313 4.034091

La satisfaction moyenne des commandes livrées est de 3.76 sur 286
commandes.
```

Le chiffre du texte (l'expression `r round(…)` écrite entre accents graves, au milieu de la phrase) est **calculé** à la compilation, et le bloc de code est exécuté avec sa sortie insérée sous lui (lignes `##`). `FALSE` correspond aux livraisons de plus de 3 jours, `TRUE` aux livraisons de 3 jours ou moins : les clients livrés vite sont plus satisfaits. Notez le détail : R affiche un point décimal, alors que notre rapport Python de l'application 6.10 écrivait une virgule grâce à sa fonction `fr()`. **LaTeX** est le langage qui met en forme les formules du livre. Compilons un minuscule document :

```bash
mkdir -p ~/atelier/mini-latex
cd ~/atelier/mini-latex
cat > mini.tex <<'FIN'
\documentclass{article}
\usepackage{fontspec}
\usepackage{amsmath}
\usepackage[french]{babel}
\begin{document}
\section*{Intervalle de confiance}
Pour un échantillon de taille $n$, de moyenne $\bar{x}$ et d'écart-type $s$,
l'intervalle de confiance à 95\,\% de la moyenne est
\[
  \bar{x} \;\pm\; 1{,}96\,\frac{s}{\sqrt{n}} .
\]
\end{document}
FIN
xelatex -interaction=nonstopmode -halt-on-error mini.tex > compilation.log 2>&1
echo "code de sortie : $?"
head -c 5 mini.pdf; echo
```
<!--sortie-->
```text
code de sortie : 0
%PDF-
```

Le code de sortie 0 indique que la compilation a réussi, et `mini.pdf` commence bien par `%PDF-`. Si une erreur survient (une accolade oubliée), `xelatex` s'arrête et la raison se trouve dans `compilation.log`. **Pour aller plus loin.** Ajoutez au document LaTeX la formule de l'écart-type d'échantillon, puis provoquez volontairement une erreur (une accolade en moins) et retrouvez-la dans le journal.

## Exercices

> 🧭 Cherchez d'abord par vous-même (en tapant les commandes dans un vrai terminal !), vérifiez ensuite, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse. Les exercices utilisent un dossier de travail neuf, `~/atelier/exercices`, et le fichier `commandes.csv`.

### Exercice 6.1 ⭐ — Se repérer (section 6.3)

Créez le dossier `projet-boutique` contenant deux sous-dossiers, `donnees` et `src`, copiez-y `commandes.csv` (dans `donnees`), puis (a) affichez l'arborescence créée, (b) affichez les **trois dernières** lignes du fichier, (c) comptez ses lignes.

### Exercice 6.2 ⭐ — Tuyaux (section 6.3)

Combien de commandes ont reçu chacune des notes de satisfaction (1 à 5) ? Répondez avec **une seule ligne** de commandes enchaînées par des tuyaux, puis vérifiez avec pandas.

### Exercice 6.3 ⭐ — Premiers pas avec Git (section 6.1)

Dans un nouveau dépôt `journal`, créez un fichier `notes.txt` contenant la ligne « Hypothèse : les commandes Réseaux sont plus petites. » et enregistrez-le (commit 1). Ajoutez une seconde ligne « Test à faire : comparer les moyennes par canal. » et enregistrez (commit 2). Par maladresse, vous supprimez ensuite `notes.txt` avec `rm`. Retrouvez-le **sans refaire à la main**, puis affichez l'historique en une ligne par commit.

### Exercice 6.4 ⭐⭐ — awk (section 6.3)

Calculez, pour chaque canal, le **pourcentage de commandes notées 4 ou 5** (colonne `satisfaction`), avec `awk`. Vérifiez avec pandas.

### Exercice 6.5 ⭐⭐ — Conflit (section 6.1)

Un fichier `params.txt` contient la ligne `seuil=50`. Sur une branche `prudent`, vous passez la valeur à `seuil=40` ; sur `main`, votre collègue la passe à `seuil=60`. Fusionnez `prudent` dans `main`. Que se passe-t-il ? Résolvez le conflit en gardant la valeur la **plus élevée**, et terminez la fusion.

### Exercice 6.6 ⭐⭐ — État caché (section 6.2)

Un notebook contient, de haut en bas, les cinq cellules suivantes : (A) `n = 100` ; (B) `taux = 0.19` ; (C) `tva = n * taux` ; (D) `n = 200` ; (E) `print(tva)`. La gérante les exécute dans l'ordre **A, B, D, C, E** (elle a lancé D avant C). (a) Qu'affiche E ? (b) Qu'afficherait E après « Restart & Run All » ? (c) Quelle conclusion en tirez-vous ?

### Exercice 6.7 ⭐⭐ — Environnement (section 6.3)

Créez un environnement virtuel `env-a`, installez-y `tabulate==0.8.9` et enregistrez les versions dans `requirements.txt`. Reconstruisez ensuite, dans un second environnement `env-b`, **exactement les mêmes** bibliothèques à partir de ce seul fichier, et prouvez qu'elles sont identiques.

### Exercice 6.8 ⭐⭐ — Script shell (section 6.4)

Écrivez un script `compte.sh` qui prend **deux arguments**, un fichier CSV et un numéro de colonne, et affiche le nombre d'occurrences de chaque valeur de cette colonne (sans l'en-tête). Il doit s'arrêter avec un message et un code d'erreur non nul si on lui donne un mauvais nombre d'arguments ou un fichier inexistant. Testez-le sur la colonne 1 puis sur la colonne 4.

### Exercice 6.9 ⭐⭐⭐ — Makefile (section 6.5)

Écrivez un `Makefile` dont la cible `resume.txt` dépend de `commandes.csv` et du script `resume.py`, et qui la fabrique par `python resume.py commandes.csv > resume.txt`. Montrez que : (a) un premier `make` construit la cible, (b) un deuxième ne fait rien, (c) modifier le script (date de modification) relance la construction, (d) modifier un fichier **sans rapport** (`LISEZMOI.txt`) ne la relance pas.

### Exercice 6.10 ⭐⭐⭐ — Synthèse : un projet reproductible (section 6.5)

Montez un mini-projet « rapport sur les ventes » qui réunit tout le chapitre : dépôt Git avec `.gitignore`, données, script de rapport, `Makefile`, empreinte `sha256` des données, un commit étiqueté `v1.0`. Démontrez sa reproductibilité : **clonez** le dépôt dans un autre dossier, vérifiez l'empreinte des données, lancez `make`, et prouvez que le rapport obtenu est **identique octet pour octet** à l'original.

## Corrigés

### Corrigé 6.1

`mkdir -p` crée d'un coup les dossiers imbriqués (et l'accolade en crée deux) ; `find` affiche l'arborescence ; `tail -n 3` et `wc -l` répondent à (b) et (c).

```bash
mkdir -p ~/atelier/exercices
cd ~/atelier/exercices
mkdir -p projet-boutique/{donnees,src}
cp "$DONNEES/commandes.csv" projet-boutique/donnees/
find projet-boutique | sort
tail -n 3 projet-boutique/donnees/commandes.csv
wc -l projet-boutique/donnees/commandes.csv
```
<!--sortie-->
```text
projet-boutique
projet-boutique/donnees
projet-boutique/donnees/commandes.csv
projet-boutique/src
Site,62.6,4,3
Réseaux,37.5,3,4
Site,31.4,4,4
401 projet-boutique/donnees/commandes.csv
```

Le fichier compte 401 lignes : 400 commandes plus l'en-tête.

### Corrigé 6.2

La note est dans la 4ᵉ colonne. On enlève l'en-tête (`tail -n +2`), on extrait la colonne (`cut`), on **trie** (indispensable avant `uniq`), puis on compte les groupes (`uniq -c`) :

```bash
cd ~/atelier/exercices/projet-boutique/donnees
tail -n +2 commandes.csv | cut -d, -f4 | sort -n | uniq -c
```
<!--sortie-->
```text
      1 1
     15 2
     85 3
    195 4
    104 5
```

Vérification avec pandas (même résultat attendu) :

```python
import pandas as pd
df = pd.read_csv("donnees/commandes.csv")
print(df["satisfaction"].value_counts().sort_index())
```
<!--sortie-->
```text
satisfaction
1      1
2     15
3     85
4    195
5    104
Name: count, dtype: int64
```

Les deux méthodes donnent les mêmes effectifs : la note 4 est la plus fréquente, et les notes très basses sont rares (une seule note 1), ce qui est cohérent avec une satisfaction moyenne proche de 4 (3,96). Le total fait bien 400.

### Corrigé 6.3

`git restore` ramène un fichier supprimé ou modifié à son état du dernier commit. Comme notre `rm` a supprimé le fichier **sans** l'enregistrer, c'est la bonne commande :

```bash
cd ~/atelier/exercices
mkdir journal
cd journal
git init -q
echo "Hypothèse : les commandes Réseaux sont plus petites." > notes.txt
git add notes.txt
git commit -q -m "Première hypothèse"
echo "Test à faire : comparer les moyennes par canal." >> notes.txt
git commit -q -am "Ajout du test à faire"
rm notes.txt
ls
git restore notes.txt
cat notes.txt
git log --oneline
```
<!--sortie-->
```text
Hypothèse : les commandes Réseaux sont plus petites.
Test à faire : comparer les moyennes par canal.
3af636d Ajout du test à faire
fe687dd Première hypothèse
```

Après le `rm`, `ls` n'affiche rien (le fichier a disparu) ; après `git restore`, le fichier est revenu avec **ses deux lignes**, car elles figuraient dans le dernier commit. Le tout a été possible parce qu'on avait enregistré : un fichier jamais commité aurait été perdu.

### Corrigé 6.4

On compte, pour chaque canal, le nombre total de commandes (`n`) et le nombre de commandes notées 4 ou 5 (`bons`) ; à la fin, on affiche le pourcentage. (Dans `awk`, une case de tableau jamais utilisée vaut 0, donc `bons[c]` fonctionne même si un canal n'a aucune bonne note.)

```bash
cd ~/atelier/exercices/projet-boutique/donnees
awk -F, 'NR > 1 { n[$1]++; if ($4 >= 4) bons[$1]++ }
         END { for (c in n) printf "%-10s %.1f %%\n", c, 100 * bons[c] / n[c] }' commandes.csv | sort
```
<!--sortie-->
```text
Boutique   95.6 %
Réseaux    63.0 %
Site       69.6 %
```

Et la vérification avec pandas :

```python
satisfaits = (df["satisfaction"] >= 4).groupby(df["canal"]).mean() * 100
print(satisfaits.round(1))
```
<!--sortie-->
```text
canal
Boutique    95.6
Réseaux     63.0
Site        69.6
Name: satisfaction, dtype: float64
```

Les deux approches coïncident. Les clients de la **boutique** sont les plus satisfaits : pas de délai de livraison, donc pas de pénalité (voir la construction du jeu de données au 3.1.2, où la note diminue avec le délai).

### Corrigé 6.5

Les deux branches ont modifié **la même ligne** : Git ne peut pas choisir, il signale un conflit. On édite le fichier pour garder `seuil=60`, on déclare le conflit résolu avec `git add`, puis on termine par un commit.

```bash
cd ~/atelier/exercices
mkdir conflit
cd conflit
git init -q
echo "seuil=50" > params.txt
git add params.txt
git commit -q -m "Paramètre initial"
git switch -q -c prudent
echo "seuil=40" > params.txt
git commit -q -am "Seuil prudent"
git switch -q main
echo "seuil=60" > params.txt
git commit -q -am "Seuil ambitieux"
git merge --no-edit prudent
echo "----- fichier en conflit -----"
cat params.txt
```
<!--sortie-->
```text
Auto-merging params.txt
CONFLICT (content): Merge conflict in params.txt
Automatic merge failed; fix conflicts and then commit the result.
----- fichier en conflit -----
<<<<<<< HEAD
seuil=60
=======
seuil=40
>>>>>>> prudent
```

Le fichier contient maintenant les marqueurs `<<<<<<<`, `=======` et `>>>>>>>` autour des deux versions. On résout en écrivant la valeur voulue (ici nous la réécrivons directement, ce qui revient à supprimer les marqueurs et la ligne `seuil=40`) :

```bash
echo "seuil=60" > params.txt
git add params.txt
git commit -q --no-edit
git log --oneline --graph
cat params.txt
```
<!--sortie-->
```text
*   772e5c8 Merge branch 'prudent'
|\  
| * 3723e50 Seuil prudent
* | 8d91b2b Seuil ambitieux
|/  
* f3f63d7 Paramètre initial
seuil=60
```

Le graphe montre bien la **fusion** de deux lignes de travail en un commit à deux parents. N'oubliez pas, dans un vrai projet, de **relancer le code** avant de valider.

### Corrigé 6.6

On simule le noyau avec un dictionnaire, comme dans l'application 6.5. Le point clé est l'**ordre d'exécution**, pas l'ordre d'écriture :

```python
def jouer(ordre):
    memoire = {}
    cellules = {"A": "n = 100", "B": "taux = 0.19", "C": "tva = n * taux",
                "D": "n = 200", "E": "print(round(tva, 2))"}
    for nom in ordre:
        exec(cellules[nom], memoire)

print("(a) ordre A, B, D, C, E :", end=" ")
jouer("ABDCE")
print("(b) Restart & Run All (A, B, C, D, E) :", end=" ")
jouer("ABCDE")
```
<!--sortie-->
```text
(a) ordre A, B, D, C, E : 38.0
(b) Restart & Run All (A, B, C, D, E) : 19.0
```

(a) Dans l'ordre réellement joué, `n` vaut déjà 200 quand C calcule la TVA : E affiche $200\times0{,}19=38$. (b) Dans l'ordre du fichier, C est exécutée alors que `n` vaut encore 100 : E affiche $100\times0{,}19=19$. (c) Le **même notebook** donne deux résultats différents selon l'ordre d'exécution : le chiffre que la gérante voyait à l'écran (38) n'est pas celui qu'obtiendra quiconque ouvrira le fichier et exécutera tout (19). C'est exactement l'état caché : **toujours** redémarrer et tout exécuter avant de se fier à un résultat. (Une analyse correcte de la logique du carnet dirait aussi que la cellule D, placée *après* C mais qui change `n`, est probablement mal placée.)

### Corrigé 6.7

On crée le premier environnement, on y installe la version exacte demandée, puis on fige ; le second environnement est reconstruit uniquement depuis `requirements.txt`.

```bash
cd ~/atelier/exercices
mkdir env-demo
cd env-demo
python -m venv env-a
env-a/bin/pip install --quiet "tabulate==0.8.9" 2>&1 | grep -v -i -E "notice|warning"
env-a/bin/pip freeze > requirements.txt
cat requirements.txt
python -m venv env-b
env-b/bin/pip install --quiet -r requirements.txt 2>&1 | grep -v -i -E "notice|warning"
env-b/bin/pip freeze > freeze-b.txt
cmp requirements.txt freeze-b.txt && echo "les deux environnements sont identiques"
```
<!--sortie-->
```text
tabulate==0.8.9
les deux environnements sont identiques
```

La commande `cmp` compare deux fichiers octet par octet et ne dit rien s'ils sont identiques ; notre `&& echo` confirme alors le succès. (On appelle directement `env-a/bin/pip` au lieu d'activer l'environnement : c'est strictement équivalent.)

### Corrigé 6.8

Le script vérifie ses arguments (`$#`), l'existence du fichier (`-f`), puis enchaîne les outils de l'application 6.6 : `tail` (supprimer l'en-tête), `cut` (extraire la colonne), `sort`, `uniq -c`.

```bash
cd ~/atelier/exercices/projet-boutique
cat > src/compte.sh <<'FIN'
#!/usr/bin/env bash
# compte.sh : effectifs de chaque valeur d'une colonne d'un CSV
# usage : bash src/compte.sh fichier.csv numero_de_colonne
set -euo pipefail
if [ "$#" -ne 2 ]; then
    echo "usage : $0 fichier.csv numero_de_colonne" >&2
    exit 2
fi
if [ ! -f "$1" ]; then
    echo "fichier introuvable : $1" >&2
    exit 1
fi
tail -n +2 "$1" | cut -d, -f"$2" | sort | uniq -c
FIN
echo "--- colonne 1 (canal) ---"
bash src/compte.sh donnees/commandes.csv 1
echo "--- colonne 4 (satisfaction) ---"
bash src/compte.sh donnees/commandes.csv 4
echo "--- erreurs ---"
bash src/compte.sh donnees/commandes.csv; echo "code : $?"
bash src/compte.sh absent.csv 1; echo "code : $?"
```
<!--sortie-->
```text
--- colonne 1 (canal) ---
    114 Boutique
    138 Réseaux
    148 Site
--- colonne 4 (satisfaction) ---
      1 1
     15 2
     85 3
    195 4
    104 5
--- erreurs ---
usage : src/compte.sh fichier.csv numero_de_colonne
code : 2
fichier introuvable : absent.csv
code : 1
```

Les effectifs de la colonne 4 sont ceux de l'exercice 6.2, et ceux de la colonne 1 retrouvent les effectifs par canal. Les deux appels fautifs affichent leur message et renvoient des codes **2** (mauvais usage) et **1** (fichier absent), comme convenu.

### Corrigé 6.9

Le `Makefile` décrit la dépendance de `resume.txt` à ses deux sources. Le script `resume.py` est écrit ici en quelques lignes pour que l'exercice soit autonome ; pour la tabulation, on emploie encore la substitution `<TAB>`.

```bash
cd ~/atelier/exercices
mkdir make-demo
cd make-demo
cp "$DONNEES/commandes.csv" .
cat > resume.py <<'FIN'
import sys
import pandas as pd

df = pd.read_csv(sys.argv[1])
print(f"{len(df)} lignes, {df.shape[1]} colonnes")
print(df.describe().loc[["mean", "min", "max"]].round(2))
FIN
echo "Notes de lecture" > LISEZMOI.txt
cat > Makefile <<'FIN'
resume.txt: commandes.csv resume.py
<TAB>python resume.py commandes.csv > resume.txt
FIN
sed -i 's/^<TAB>/\t/' Makefile
```

```bash
echo "--- (a) premier make ---"
make
echo "--- (b) deuxième make ---"
make
echo "--- (c) on touche resume.py ---"
touch resume.py
make
echo "--- (d) on touche LISEZMOI.txt ---"
touch LISEZMOI.txt
make
cat resume.txt
```
<!--sortie-->
```text
--- (a) premier make ---
python resume.py commandes.csv > resume.txt
--- (b) deuxième make ---
make: 'resume.txt' is up to date.
--- (c) on touche resume.py ---
python resume.py commandes.csv > resume.txt
--- (d) on touche LISEZMOI.txt ---
make: 'resume.txt' is up to date.
400 lignes, 4 colonnes
      montant  livraison  satisfaction
mean    60.25       3.29          3.96
min      8.60       0.00          1.00
max    255.70      13.00          5.00
```

(a) Le premier `make` exécute la commande ; (b) le deuxième répond que la cible est déjà à jour ; (c) en modifiant la date du script, `make` détecte que la dépendance est plus récente que la cible et **refabrique** ; (d) `LISEZMOI.txt` n'est pas une dépendance : `make` n'y réagit pas. Seul ce qui est **déclaré** comme dépendance déclenche une reconstruction, d'où l'importance de **lister toutes** les sources dans la règle.

### Corrigé 6.10

C'est le projet de synthèse du chapitre. On le construit pas à pas, puis on le **clone** pour le rejouer ailleurs. D'abord le projet, avec son script de rapport (très simple, il n'écrit ni date ni valeur aléatoire), son `Makefile` et l'empreinte des données :

```bash
cd ~/atelier/exercices
mkdir ventes-reproductibles
cd ventes-reproductibles
git init -q
mkdir donnees src rapports
cp "$DONNEES/commandes.csv" donnees/
sha256sum donnees/commandes.csv > donnees/EMPREINTES.sha256
cat > src/rapport.py <<'FIN'
import sys
import pandas as pd

df = pd.read_csv(sys.argv[1])
print("# Rapport sur les ventes")
print()
print(f"- Commandes : {len(df)}")
print(f"- Montant moyen : {df['montant'].mean():.2f} €")
print(f"- Satisfaction moyenne : {df['satisfaction'].mean():.2f} / 5")
FIN
```

On ajoute le `Makefile`, un `.gitignore` et un `README`, puis on construit le rapport.

```bash
cat > Makefile <<'FIN'
rapports/rapport.md: donnees/commandes.csv src/rapport.py
<TAB>python src/rapport.py donnees/commandes.csv > $@
FIN
sed -i 's/^<TAB>/\t/' Makefile
printf '.venv/\n__pycache__/\n*.env\n' > .gitignore
printf 'Pour tout reproduire : sha256sum -c donnees/EMPREINTES.sha256 && make\n' > README.md
make
cat rapports/rapport.md
```
<!--sortie-->
```text
python src/rapport.py donnees/commandes.csv > rapports/rapport.md
# Rapport sur les ventes

- Commandes : 400
- Montant moyen : 60.25 €
- Satisfaction moyenne : 3.96 / 5
```

Puis on enregistre dans Git : le **rapport produit** est lui aussi versionné ici pour pouvoir le comparer, mais en pratique on ne versionne que les sources (6.1.11). On pose l'étiquette `v1.0` :

```bash
git add .
git commit -q -m "Projet de rapport reproductible"
git tag -a v1.0 -m "Version livrée"
git log --oneline
git status --short
```
<!--sortie-->
```text
ee53fd3 Projet de rapport reproductible
```

Il ne reste rien d'« en attente » (`git status` est vide). Passons à la **preuve** : un collègue clone le dépôt dans un dossier tout neuf, vérifie l'intégrité des données, reconstruit le rapport (après avoir supprimé le rapport cloné, pour être sûr que `make` le refabrique), et compare :

```bash
cd ~/atelier/exercices
git clone -q ventes-reproductibles collegue
cd collegue
git checkout -q v1.0
sha256sum -c donnees/EMPREINTES.sha256
rm rapports/rapport.md
make
cmp rapports/rapport.md ../ventes-reproductibles/rapports/rapport.md && echo "rapports identiques, octet pour octet"
```
<!--sortie-->
```text
donnees/commandes.csv: OK
python src/rapport.py donnees/commandes.csv > rapports/rapport.md
rapports identiques, octet pour octet
```

Les données sont intègres (`OK`), le rapport a été refabriqué par `make`, et la comparaison `cmp` confirme qu'il est **identique** à l'original. C'est la définition opérationnelle de la reproductibilité : *un tiers, sur un dossier neuf, obtient exactement le même résultat avec une commande*. Chaque élément du chapitre y a joué son rôle : Git (le code et ses versions), le `.gitignore`, le `Makefile`, l'empreinte des données, et, pour l'environnement, le `requirements.txt` que l'on ajouterait dans un vrai projet.
