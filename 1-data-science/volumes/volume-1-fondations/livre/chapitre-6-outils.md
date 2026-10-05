<!-- NOTE POUR LA MAINTENANCE : les fichiers 06-*.md se remplissent en UN SEUL appel de fill.py (sessions bash partagées, ordre 06-0 → 06-6), avec :
     DONNEES=<chemin absolu du dossier donnees/>  PATH=<venv avec pandas, nbformat, nbclient, nbconvert, ipykernel en tête>  NO_COLOR=1
     Outils système requis : git, pandoc, xelatex (+polyglossia), make, R (+rmarkdown, knitr), sha256sum. Réseau requis pour 6.3.6, 6.4.4, exercice 7 (pip install tabulate). -->

# Chapitre 6 : Outils de travail

> « Un bon artisan ne se reconnaît pas seulement à ses gestes, mais à **l'ordre de son atelier**. »

Vous savez maintenant calculer (chapitres 1 à 3), programmer (chapitre 4) et interroger une base de données (chapitre 5). Reste une question que personne n'ose poser en cours, mais qui décide de la vie quotidienne d'un data scientist : **comment ne pas se perdre dans son propre travail ?**

Voici la scène, que tout le monde a vécue au moins une fois. Yasmine ouvre le dossier de son analyse des ventes de Dar Jasmin :

```text
analyse.py
analyse_v2.py
analyse_v2_corrige.py
analyse_FINAL.py
analyse_FINAL_vrai.py
analyse_FINAL_vrai_ne_pas_toucher.py
rapport_mars.docx
rapport_mars (copie).docx
```

Quelle version a produit le graphique envoyé à la banque la semaine dernière ? Impossible de le savoir. Que s'est-il passé quand elle a « juste changé un petit truc » mardi soir, et que tous les chiffres se sont mis à bouger ? Mystère. Et si son frère Amine veut l'aider, comment fusionnent-ils leurs deux versions sans écraser le travail de l'autre ?

Ce chapitre vous donne **quatre outils** qui répondent à ces questions, et qui sont utilisés dans toutes les équipes de données du monde.

## Le chemin de ce chapitre

- **6.1 Git et gestion de versions** : une machine à remonter le temps pour vos fichiers. On y apprend à photographier son travail (*commit*), à comparer, à défaire, à travailler à plusieurs (*branches*, *fusions*, *conflits*) et à partager (*dépôts distants*).
- **6.2 Notebooks Jupyter** : le carnet de laboratoire interactif où code, résultats et explications cohabitent. On y apprend aussi à **s'en méfier** : un notebook mal utilisé produit des résultats que personne ne peut reproduire.
- **6.3 Ligne de commande et environnements** : parler directement à l'ordinateur avec du texte, enchaîner de petits outils, et isoler les bibliothèques de chaque projet dans un **environnement virtuel**.
- ➕ **Pour aller plus loin** : scripts shell et bases de Docker (6.4) ; recherche reproductible, de Pandoc à Quarto en passant par LaTeX et Make (6.5).
- **6.6 Exercices corrigés** et bilan du chapitre.

> 🧭 **Le fil conducteur : la reproductibilité.** Un résultat n'a de valeur que si **quelqu'un d'autre (ou vous-même dans six mois) peut le refaire**. Chaque outil de ce chapitre attaque une cause différente de non-reproductibilité : Git (« quelle version du code ? »), les notebooks bien tenus (« dans quel ordre a-t-on exécuté les cellules ? »), les environnements (« avec quelles versions des bibliothèques ? »), les graines aléatoires et les `Makefile` (« avec quelles données et quelles étapes ? »). Le terme technique est la *reproductibilité computationnelle*.

> 🛠️ **Comment travailler avec ce chapitre.** Contrairement aux précédents, les exemples de ce chapitre se tapent dans un **terminal** (aussi appelé *console* ou *shell*), pas dans Python. Sous Linux et macOS, ouvrez l'application « Terminal ». Sous Windows, installez **Git for Windows** (il fournit *Git Bash*, un terminal compatible avec tous nos exemples) ou, mieux, **WSL** (le sous-système Linux de Windows). Les lignes que vous devez taper sont celles des blocs de code ; les blocs gris qui suivent montrent ce que l'ordinateur répond.

## L'atelier de Yasmine

Pour que les exemples soient concrets, nous préparons un petit **atelier** : un dossier de travail dans lequel nous copions le fichier de données du livre.

> 📦 **À propos de `$DONNEES`.** Le fichier `commandes.csv` est fourni avec le livre dans le dossier `donnees/`. Dans les exemples qui suivent, la variable `$DONNEES` désigne le **chemin de ce dossier** sur la machine qui exécute le code. Chez vous, remplacez `"$DONNEES"` par l'endroit où vous avez rangé le fichier (par exemple `~/livre/donnees`). Le caractère `~` est une abréviation pour votre dossier personnel ; nous l'expliquons au 6.3.

```bash
mkdir -p ~/atelier/dar-jasmin
cd ~/atelier/dar-jasmin
cp "$DONNEES/commandes.csv" .
ls
wc -l commandes.csv
```
<!--sortie-->
```text
commandes.csv
401 commandes.csv
```

Chaque ligne tapée est une **commande** : un nom (`mkdir`, `cd`, `cp`, `ls`) suivi d'**arguments**. Ici : créer un dossier (`mkdir`, pour *make directory* ; l'option `-p` crée aussi les dossiers intermédiaires et ne se plaint pas s'il existe déjà), s'y placer (`cd`, *change directory*), y copier le fichier (`cp`, *copy*; le point `.` désigne « le dossier où je suis »), puis lister le contenu (`ls`, *list*) et compter les lignes du fichier (`wc -l`, *word count*, option *lines*). Le résultat est celui qu'on attend : 400 commandes, une ligne chacune, plus la ligne d'en-tête, soit 401 lignes.

> ⚠️ **Honnêteté sur l'exécution.** Tous les exemples de ce chapitre qui peuvent s'exécuter sans réseau ni logiciel spécial ont été **réellement exécutés** dans un atelier jetable, et la sortie affichée est la vraie. Les rares exceptions (Docker, Quarto, services en ligne comme GitHub) sont clairement signalées « **non exécuté** » : nous n'y affichons que la commande, jamais une sortie inventée.


## 6.1 Git et gestion de versions

> 💡 **Intuition.** Imaginez que vous puissiez, à tout moment, prendre une **photographie complète** de votre dossier de travail, lui donner un titre (« ajout du calcul par canal de vente »), et la ranger dans un album. Plus tard, vous pouvez feuilleter l'album, comparer deux photos, revenir à celle d'il y a un mois, ou même ouvrir **deux albums parallèles** pour tester une idée folle sans toucher à la version qui marche. **Git** est exactement cet album, avec trois cadeaux en plus : il est gratuit, il fonctionne hors ligne, et il permet à plusieurs personnes de travailler sur le même dossier sans se marcher dessus.

### 6.1.1 Pourquoi pas simplement « analyse_FINAL_vrai.py » ?

Copier ses fichiers avec un suffixe (`_v2`, `_FINAL`) semble naturel, mais les défauts apparaissent vite :

| Problème | Avec des copies de fichiers | Avec Git |
|---|---|---|
| « Qu'est-ce qui a changé entre hier et aujourd'hui ? » | Ouvrir deux fichiers et comparer à l'œil | `git diff` liste chaque ligne modifiée |
| « Pourquoi ai-je changé ça ? » | Personne ne s'en souvient | Chaque version porte un **message** daté et signé |
| « Je veux revenir à la version de mars » | Si elle existe encore et si son nom est clair | Une commande |
| « Je veux tester une idée sans risque » | Dupliquer tout le dossier | Une **branche**, en une seconde |
| « Amine et moi avons modifié le même fichier » | L'un des deux écrase l'autre, ou on recopie à la main | Git **fusionne** et signale seulement les vrais conflits |
| « Quel code a produit ce graphique ? » | Aucune idée | On retrouve la version exacte |

Git a été créé en 2005 par Linus Torvalds pour développer le noyau Linux ; il est aujourd'hui le standard de fait, bien au-delà de la programmation : vous l'utiliserez pour du code, des notebooks, des rapports en texte, des fichiers de configuration. (Ce livre lui-même est écrit dans des fichiers texte suivis avec Git.)

> 🧭 **Git et GitHub, ce n'est pas pareil.** *Git* est le logiciel qui tourne **sur votre machine** et garde l'historique. *GitHub*, *GitLab* ou *Bitbucket* sont des **sites web** qui hébergent des copies de dépôts Git pour les partager. On peut utiliser Git des années sans jamais toucher à GitHub.

### 6.1.2 Premiers réglages

Git vérifie que vous êtes bien installé, puis il faut lui dire **qui vous êtes** : chaque version enregistrée est signée.

```bash
git --version
git config --global user.name "Yasmine de Dar Jasmin"
git config --global user.email "yasmine@dar-jasmin.example"
git config --global init.defaultBranch main
git config --global --list
```
<!--sortie-->
```text
git version 2.48.1
user.name=Yasmine de Dar Jasmin
user.email=yasmine@dar-jasmin.example
init.defaultbranch=main
```

Les trois réglages sont enregistrés une fois pour toutes dans le fichier `.gitconfig` de votre dossier personnel. La branche par défaut s'appellera `main` (l'ancien nom était `master` ; beaucoup de dépôts anciens l'utilisent encore).

> 💡 **Une astuce de reproductibilité (à ne pas reproduire chez vous).** Chaque version Git est identifiée par une empreinte qui dépend, entre autres, **de la date**. Pour que le livre affiche toujours les mêmes empreintes à chaque exécution, les exemples de cette section fixent artificiellement la date de toutes les versions (variables `GIT_AUTHOR_DATE` et `GIT_COMMITTER_DATE`). Chez vous, ne fixez rien : Git utilise l'heure de l'horloge, et vos empreintes seront donc différentes des nôtres. Pas de souci : aucun raisonnement ne dépend de leur valeur.

```bash
export GIT_AUTHOR_DATE="2026-03-02T10:00:00+01:00"
export GIT_COMMITTER_DATE="2026-03-02T10:00:00+01:00"
echo "dates fixées pour la démonstration"
```
<!--sortie-->
```text
dates fixées pour la démonstration
```

### 6.1.3 Le premier dépôt : init, add, commit

Un **dépôt** (*repository*, ou *repo*) est un dossier que Git surveille. On l'initialise avec `git init`. Écrivons d'abord le tout premier script d'analyse de Yasmine : il calcule le montant moyen des commandes.

```bash
cd ~/atelier/dar-jasmin
git init -q
cat > analyse.py <<'FIN'
import pandas as pd

df = pd.read_csv("commandes.csv")
print("Nombre de commandes :", len(df))
print("Montant moyen :", round(df["montant"].mean(), 2), "DT")
FIN
python analyse.py
```
<!--sortie-->
```text
Nombre de commandes : 400
Montant moyen : 60.25 DT
```

(`cat > analyse.py <<'FIN' … FIN` est une façon de créer un fichier directement depuis le terminal : tout ce qui se trouve entre les deux `FIN` est écrit dans `analyse.py`. En pratique, vous utiliserez plutôt votre éditeur de code.) Le script fonctionne, avec le fil rouge habituel : 60,25 DT de montant moyen. Que pense Git de l'état du dossier ?

```bash
git status
```
<!--sortie-->
```text
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	analyse.py
	commandes.csv

nothing added to commit but untracked files present (use "git add" to track)
```

Git voit deux fichiers **non suivis** (*untracked*) : il les a remarqués mais ne les surveille pas encore. Pour comprendre la suite, il faut connaître les **trois zones** de Git :

```text
 dossier de travail        zone d'index              dépôt (historique)
  (vos fichiers)     ──►   (« staging area »)  ──►   (les photos rangées)
                  git add                     git commit
```

- Le **dossier de travail** contient vos fichiers, tels que vous les éditez.
- La **zone d'index** (*staging area*) est la table où l'on **prépare la prochaine photo** : on y dépose seulement ce qu'on veut y voir.
- Le **dépôt** contient les photos prises, à jamais (les *commits*).

Pourquoi cette zone intermédiaire ? Parce qu'on a souvent modifié trois fichiers pour trois raisons différentes ; on peut ainsi faire **trois commits distincts et propres** plutôt qu'un fourre-tout. Ajoutons le script, puis prenons la photo.

```bash
git add analyse.py
git status --short
git commit -q -m "Premier script : montant moyen des commandes"
git log --oneline
```
<!--sortie-->
```text
A  analyse.py
?? commandes.csv
aa98f06 Premier script : montant moyen des commandes
```

`git status --short` affiche une lettre par fichier : `A` (ajouté à l'index) pour `analyse.py`, `??` (non suivi) pour `commandes.csv`. Après le `commit`, `git log --oneline` montre une ligne : l'empreinte courte de la version, suivie de son message.

> ⚠️ **Écrire de bons messages.** Un message de commit répond à la question « **que fait** ce changement, et pourquoi ? », dans un langage que vous comprendrez dans six mois. « maj » ou « modifs » sont inutiles ; « Ajout du montant moyen par canal de vente » est excellent. Convention courante : une première ligne courte (≈ 50 caractères), à l'impératif ou au passé de façon cohérente.

On a laissé `commandes.csv` de côté volontairement. Faut-il suivre les données dans Git ? Pour un petit fichier fixe comme celui-ci, oui, cela garantit que l'analyse reste rejouable avec **exactement** les mêmes données. Pour de gros fichiers, non (voir 6.1.11). Ici, on l'ajoute :

```bash
git add commandes.csv
git commit -q -m "Ajout du fichier de données (400 commandes)"
git log --oneline
```
<!--sortie-->
```text
09e8168 Ajout du fichier de données (400 commandes)
aa98f06 Premier script : montant moyen des commandes
```

### 6.1.4 Ce qu'il y a vraiment dans un commit

> 📐 **Rigueur : le modèle d'objets de Git.** Un *commit* n'est pas une liste de différences : c'est une **photographie complète** du dossier, accompagnée de métadonnées et d'un **pointeur vers le commit précédent** (son *parent*). Chaque objet est stocké sous un nom qui est l'**empreinte de son contenu** (une fonction de hachage SHA-1, qui transforme n'importe quel contenu en un nombre de 40 chiffres hexadécimaux). Il y a trois sortes d'objets :
>
> - un **blob** : le contenu d'un fichier, sans son nom ;
> - un **arbre** (*tree*) : la liste des fichiers d'un dossier, avec pour chacun le nom et l'empreinte de son blob ;
> - un **commit** : l'empreinte d'un arbre, l'empreinte du ou des parents, l'auteur, la date, le message.
>
> Conséquence cruciale : si on change **un seul caractère** dans un fichier, l'empreinte du blob change, donc celle de l'arbre, donc celle du commit, et de tous ses descendants. Un historique Git ne peut donc pas être modifié en douce : c'est ce qui le rend digne de confiance. Autre conséquence : deux fichiers de contenu identique partagent le même blob, et Git ne les stocke qu'une fois.

C'est vérifiable à la main ! L'empreinte d'un blob est simplement le SHA-1 de la chaîne `blob`, suivie de la taille du contenu, d'un caractère nul, puis du contenu. Calculons-la de deux façons : avec Git, et avec l'outil `sha1sum`, sans Git :

```bash
echo "Dar Jasmin" > bonjour.txt
git hash-object bonjour.txt
printf 'blob 11\0Dar Jasmin\n' | sha1sum
```
<!--sortie-->
```text
6f7ea4d27e6759345d14bb395b92f846451619de
6f7ea4d27e6759345d14bb395b92f846451619de  -
```

Les deux empreintes sont **identiques** : Git ne fait rien de magique, il hache le contenu (11 octets : les 10 caractères de « Dar Jasmin » plus le saut de ligne). Voyons maintenant le dernier commit « de l'intérieur » :

```bash
git cat-file -p HEAD
echo "---"
git cat-file -p 'HEAD^{tree}'
rm bonjour.txt
```
<!--sortie-->
```text
tree 9def47f7022f460faed35f54531145c9e6c3373d
parent aa98f06b76c0b3fd78b10dbb79a071afd2c878b4
author Yasmine de Dar Jasmin <yasmine@dar-jasmin.example> 1772442000 +0100
committer Yasmine de Dar Jasmin <yasmine@dar-jasmin.example> 1772442000 +0100

Ajout du fichier de données (400 commandes)
---
100644 blob 7141581ddbf60852e4f5e00be8e4b8aa412c6a73	analyse.py
100644 blob 39d5bed793efe2ff7b963d7ff459bf3a8023daa1	commandes.csv
```

On lit d'abord le commit : l'empreinte de l'arbre (`tree`), celle du parent (`parent`), l'auteur, et le message. Puis l'arbre : deux lignes, une par fichier, chacune avec le mode, le type `blob`, l'empreinte et le nom. Le mot `HEAD` désigne « le commit où je suis en ce moment » ; `HEAD^` est son parent.

### 6.1.5 Modifier, comparer, enregistrer : le cycle de travail

Le quotidien avec Git est une boucle de quatre gestes : **modifier** des fichiers, **regarder** ce qui a changé (`git status`, `git diff`), **choisir** ce qui part dans la prochaine photo (`git add`), **enregistrer** (`git commit`). Yasmine veut maintenant le montant moyen **par canal de vente**.

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
index 7141581..feccec9 100644
--- a/analyse.py
+++ b/analyse.py
@@ -3,3 +3,6 @@ import pandas as pd
 df = pd.read_csv("commandes.csv")
 print("Nombre de commandes :", len(df))
 print("Montant moyen :", round(df["montant"].mean(), 2), "DT")
+print()
+print("Montant moyen par canal :")
+print(df.groupby("canal")["montant"].mean().round(2))
```

`git diff` montre les différences entre le dossier de travail et la dernière photo : les lignes précédées de `+` sont ajoutées, celles précédées de `-` seraient supprimées. Le bloc `@@ … @@` situe la modification dans le fichier. Lançons le script, puis enregistrons :

```bash
python analyse.py
git add analyse.py
git commit -q -m "Ajout du montant moyen par canal"
git log --format='%h  %s'
```
<!--sortie-->
```text
Nombre de commandes : 400
Montant moyen : 60.25 DT

Montant moyen par canal :
canal
Boutique     74.81
Instagram    49.01
Site         59.50
Name: montant, dtype: float64
11985b5  Ajout du montant moyen par canal
09e8168  Ajout du fichier de données (400 commandes)
aa98f06  Premier script : montant moyen des commandes
```

> 🛠️ **Trois variantes utiles de `git diff`.** `git diff` compare le dossier de travail à l'index (« ce que je n'ai pas encore préparé ») ; `git diff --staged` compare l'index au dernier commit (« ce qui partira au prochain commit ») ; `git diff HEAD~1 HEAD` compare deux commits (ici, le précédent et le dernier).

Pour relire l'historique avec le détail des changements :

```bash
git log --stat
git show --stat HEAD~1
```
<!--sortie-->
```text
commit 11985b58f7a7c55501f7f918b708d0baa4f29019
Author: Yasmine de Dar Jasmin <yasmine@dar-jasmin.example>
Date:   Mon Mar 2 10:00:00 2026 +0100

    Ajout du montant moyen par canal

 analyse.py | 3 +++
 1 file changed, 3 insertions(+)

commit 09e8168a199194eccfc0277b890b4b17948587ff
Author: Yasmine de Dar Jasmin <yasmine@dar-jasmin.example>
Date:   Mon Mar 2 10:00:00 2026 +0100

    Ajout du fichier de données (400 commandes)

 commandes.csv | 401 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 401 insertions(+)

commit aa98f06b76c0b3fd78b10dbb79a071afd2c878b4
Author: Yasmine de Dar Jasmin <yasmine@dar-jasmin.example>
Date:   Mon Mar 2 10:00:00 2026 +0100

    Premier script : montant moyen des commandes

 analyse.py | 5 +++++
 1 file changed, 5 insertions(+)
commit 09e8168a199194eccfc0277b890b4b17948587ff
Author: Yasmine de Dar Jasmin <yasmine@dar-jasmin.example>
Date:   Mon Mar 2 10:00:00 2026 +0100

    Ajout du fichier de données (400 commandes)

 commandes.csv | 401 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 401 insertions(+)
```

`--stat` résume chaque commit par fichiers touchés et nombre de lignes ajoutées (`+`) ou supprimées (`-`). `HEAD~1` désigne « un commit avant HEAD », `HEAD~2` deux avant, etc.

### 6.1.6 Défaire une erreur

C'est la plus grande qualité de Git : **presque tout se rattrape**, à condition de choisir la bonne commande. Trois situations classiques, de la plus bénigne à la plus lourde.

**Situation 1 : « J'ai cassé un fichier, je veux retrouver la version du dernier commit. »** Yasmine, fatiguée, efface par erreur tout le contenu de son script :

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
255 analyse.py
0 analyse.py
255 analyse.py
Nombre de commandes : 400
Montant moyen : 60.25 DT
```

`wc -c` compte les octets du fichier. La ligne `> analyse.py` (une redirection vers un fichier, sans commande devant : voir 6.3) **vide** le fichier : 0 octet, et le script n'affiche plus rien du tout. Puis `git restore analyse.py` ramène le fichier à l'état du dernier commit : la taille d'origine revient, et le script affiche de nouveau ses résultats.

> ⚠️ **`git restore` est irréversible pour les modifications non enregistrées.** Ce que Git n'a jamais photographié, il ne peut pas le retrouver. D'où la règle d'or : **faites des commits petits et fréquents**.

**Situation 2 : « J'ai enregistré une erreur dans un commit, mais je l'ai déjà partagé ou je veux garder une trace. »** On **annule par un nouveau commit** qui fait l'inverse : c'est `git revert`. L'historique reste intact, il s'enrichit d'une ligne « annulation ». Yasmine ajoute une ligne erronée, la commite, puis la retire proprement :

```bash
echo 'print("TODO supprimer cette ligne")' >> analyse.py
git commit -q -am "Ligne de debug oubliée"
git revert --no-edit HEAD
git log --format='%h  %s'
python analyse.py | tail -n 1
```
<!--sortie-->
```text
[main 23f717b] Revert "Ligne de debug oubliée"
 Date: Mon Mar 2 10:00:00 2026 +0100
 1 file changed, 1 deletion(-)
23f717b  Revert "Ligne de debug oubliée"
57b0242  Ligne de debug oubliée
11985b5  Ajout du montant moyen par canal
09e8168  Ajout du fichier de données (400 commandes)
aa98f06  Premier script : montant moyen des commandes
Name: montant, dtype: float64
```

(L'option `-a` de `commit` ajoute automatiquement tous les fichiers **déjà suivis** et modifiés ; pratique, mais elle ne règle pas la question « qu'ai-je vraiment modifié ? » : on vérifie avec `git status` avant.)

L'historique contient maintenant les deux lignes (l'erreur *et* son annulation), et le script est redevenu propre : sa dernière ligne de sortie est de nouveau la fin du tableau par canal, sans notre message de debug.

**Situation 3 : « Je veux revoir l'état du dossier à une date passée. »** On se déplace temporairement dans l'historique avec `git switch --detach` (le dossier prend l'apparence du commit demandé, sans rien détruire), puis on revient :

```bash
git switch --detach HEAD~3 2>&1 | head -n 1
cat analyse.py
git switch main
```
<!--sortie-->
```text
HEAD is now at 09e8168 Ajout du fichier de données (400 commandes)
import pandas as pd

df = pd.read_csv("commandes.csv")
print("Nombre de commandes :", len(df))
print("Montant moyen :", round(df["montant"].mean(), 2), "DT")
Previous HEAD position was 09e8168 Ajout du fichier de données (400 commandes)
Switched to branch 'main'
```

On y voit le script tel qu'il était à ce moment-là, **sans** le calcul par canal. `git switch main` nous ramène au présent. Pendant qu'on est dans le passé, on peut regarder, lancer le code, mais on ne doit pas y travailler : Git met d'ailleurs en garde (état *detached HEAD*).

> ⚠️ **Les commandes dangereuses.** `git reset --hard` et `git clean -fd` détruisent les modifications non enregistrées sans demander confirmation. Et réécrire un historique déjà partagé (`git push --force`) peut effacer le travail des autres. En cas de doute, créez une branche de secours (`git branch sauvegarde`) avant d'expérimenter : cela ne coûte rien.

### 6.1.7 Ce qu'il ne faut pas suivre : `.gitignore`

Certains fichiers n'ont rien à faire dans l'historique : les fichiers temporaires de Python (`__pycache__/`), l'environnement virtuel (`.venv/`, section 6.3), les points de contrôle des notebooks, les mots de passe, les données volumineuses ou confidentielles. On les déclare dans un fichier texte nommé `.gitignore`.

```bash
mkdir -p .venv __pycache__
touch .venv/pyvenv.cfg __pycache__/analyse.cpython-313.pyc secrets.env
git status --short
```
<!--sortie-->
```text
?? .venv/
?? __pycache__/
?? secrets.env
```

Git voit trois choses nouvelles qui polluent la vue : `.venv/`, `__pycache__/` et `secrets.env`. (Git ne s'intéresse qu'aux fichiers, jamais aux dossiers vides : c'est pourquoi nous avons mis un fichier dans `.venv/`.) Ajoutons un fichier `.gitignore` :

```bash
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
git add .gitignore
git commit -q -m "Ajout du .gitignore"
git check-ignore -v secrets.env
```
<!--sortie-->
```text
?? .gitignore
.gitignore:7:*.env	secrets.env
```

Il ne reste que `.gitignore` lui-même (qu'on **veut** suivre, pour que toute l'équipe ignore les mêmes choses). La dernière commande, `git check-ignore -v`, explique pourquoi un fichier est ignoré : elle cite la règle et la ligne responsable.

> ⚠️ **Un secret commité est un secret perdu.** Si vous enregistrez par erreur un mot de passe ou une clé d'accès, le retirer dans un commit suivant ne suffit pas : il reste lisible dans l'historique. Considérez-le comme compromis et **changez-le**. Prévenez l'erreur en mettant `.gitignore` en place **avant** de créer le fichier secret.

### 6.1.8 Les branches : tester une idée sans risque

Une **branche** est une ligne de travail parallèle. Techniquement, c'est trivial : un simple **pointeur** (une étiquette) vers un commit, qui avance à chaque nouveau commit. La branche par défaut s'appelle `main`. Créer une branche ne copie rien : cela prend une milliseconde, quelle que soit la taille du dépôt.

Yasmine se demande à partir de quel montant offrir la livraison. Elle ouvre une branche dédiée à cette expérience, plutôt que de modifier le script principal :

```bash
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

L'étoile `*` marque la branche sur laquelle on se trouve. Travaillons sur la branche : on ajoute un seuil de livraison gratuite et on calcule la part de commandes concernées.

```bash
cat >> analyse.py <<'FIN'

SEUIL = 80  # seuil de livraison gratuite (DT)
part = (df["montant"] >= SEUIL).mean()
print(f"Part des commandes dès {SEUIL} DT : {part:.1%}")
FIN
python analyse.py | tail -n 2
git commit -q -am "Seuil de livraison gratuite à 80 DT"
git switch main
tail -n 3 analyse.py
```
<!--sortie-->
```text
Name: montant, dtype: float64
Part des commandes dès 80 DT : 21.8%
Switched to branch 'main'
print()
print("Montant moyen par canal :")
print(df.groupby("canal")["montant"].mean().round(2))
```

Retour sur `main` : les lignes du seuil **ont disparu** du fichier, car elles n'existent que sur la branche `seuil-livraison`. Rien n'est perdu : Git remplace simplement le contenu du dossier par celui du commit pointé par `main`. En repassant sur la branche, tout revient.

#### Fusionner : le cas facile (avance rapide)

Yasmine est contente de l'expérience. Elle veut la reporter dans `main` : c'est une **fusion** (*merge*). Comme `main` n'a pas bougé depuis la création de la branche, Git n'a rien à réconcilier : il se contente d'**avancer le pointeur** de `main` (*fast-forward*).

```bash
git merge seuil-livraison
git log --oneline --graph
git branch -d seuil-livraison
```
<!--sortie-->
```text
Updating ef0e5ce..164d45e
Fast-forward
 analyse.py | 4 ++++
 1 file changed, 4 insertions(+)
* 164d45e Seuil de livraison gratuite à 80 DT
* ef0e5ce Ajout du .gitignore
* 23f717b Revert "Ligne de debug oubliée"
* 57b0242 Ligne de debug oubliée
* 11985b5 Ajout du montant moyen par canal
* 09e8168 Ajout du fichier de données (400 commandes)
* aa98f06 Premier script : montant moyen des commandes
Deleted branch seuil-livraison (was 164d45e).
```

#### Fusionner : le cas où les deux ont bougé

Le cas intéressant arrive quand **deux personnes** ont modifié le dépôt en parallèle. Amine, de son côté, veut tester un seuil plus bas (60 DT) ; Yasmine, en parallèle, décide d'ajouter une moyenne des notes de satisfaction. On simule les deux lignes de travail :

```bash
# Amine : une branche pour un autre seuil
git switch -c seuil-amine
sed -i 's/^SEUIL = 80.*/SEUIL = 60  # seuil proposé par Amine (DT)/' analyse.py
git commit -q -am "Seuil à 60 DT (proposition d'Amine)"

# Yasmine revient sur main et ajoute la satisfaction
git switch main
cat >> analyse.py <<'FIN'

print("Satisfaction moyenne :", round(df["satisfaction"].mean(), 2))
FIN
git commit -q -am "Ajout de la satisfaction moyenne"

git log --oneline --graph --all
```
<!--sortie-->
```text
Switched to a new branch 'seuil-amine'
Switched to branch 'main'
* 0f93f5f Ajout de la satisfaction moyenne
| * 5e60494 Seuil à 60 DT (proposition d'Amine)
|/  
* 164d45e Seuil de livraison gratuite à 80 DT
* ef0e5ce Ajout du .gitignore
* 23f717b Revert "Ligne de debug oubliée"
* 57b0242 Ligne de debug oubliée
* 11985b5 Ajout du montant moyen par canal
* 09e8168 Ajout du fichier de données (400 commandes)
* aa98f06 Premier script : montant moyen des commandes
```

Le graphe a maintenant la forme d'un « Y » : les deux branches sont parties du même commit et ont chacune avancé de leur côté. Fusionnons celle d'Amine dans `main` :

```bash
git merge --no-edit seuil-amine
git log --oneline --graph
```
<!--sortie-->
```text
Auto-merging analyse.py
Merge made by the 'ort' strategy.
 analyse.py | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
*   7fbd1eb Merge branch 'seuil-amine'
|\  
| * 5e60494 Seuil à 60 DT (proposition d'Amine)
* | 0f93f5f Ajout de la satisfaction moyenne
|/  
* 164d45e Seuil de livraison gratuite à 80 DT
* ef0e5ce Ajout du .gitignore
* 23f717b Revert "Ligne de debug oubliée"
* 57b0242 Ligne de debug oubliée
* 11985b5 Ajout du montant moyen par canal
* 09e8168 Ajout du fichier de données (400 commandes)
* aa98f06 Premier script : montant moyen des commandes
```

Git a réussi **automatiquement** : les deux changements portaient sur des zones différentes du fichier (une ligne du seuil d'un côté, des lignes ajoutées à la fin de l'autre). Il a créé un **commit de fusion** à deux parents, ce qui apparaît sur le graphe. Python confirme que le script fonctionne et applique bien les deux modifications :

```bash
python analyse.py | tail -n 3
```
<!--sortie-->
```text
Name: montant, dtype: float64
Part des commandes dès 60 DT : 41.0%
Satisfaction moyenne : 3.96
```

#### Quand Git ne peut pas décider : un conflit

Un **conflit** survient quand deux branches modifient **la même ligne** de façons différentes : Git ne sait pas laquelle choisir, et vous demande de trancher. Ce n'est pas une catastrophe, c'est le fonctionnement normal du travail à plusieurs. Provoquons-en un : Yasmine veut un seuil de 70 DT, Amine veut 65 DT.

```bash
git switch -c seuil-yasmine
sed -i 's/^SEUIL = .*/SEUIL = 70  # seuil retenu par Yasmine (DT)/' analyse.py
git commit -q -am "Seuil à 70 DT"

git switch main
sed -i 's/^SEUIL = .*/SEUIL = 65  # compromis d'"'"'Amine (DT)/' analyse.py
git commit -q -am "Seuil à 65 DT"

git merge --no-edit seuil-yasmine
```
<!--sortie-->
```text
Switched to a new branch 'seuil-yasmine'
Switched to branch 'main'
Auto-merging analyse.py
CONFLICT (content): Merge conflict in analyse.py
Automatic merge failed; fix conflicts and then commit the result.
```

Git s'arrête et prévient : `CONFLICT (content)`. Le dépôt est en cours de fusion ; consultons l'état, puis le fichier :

```bash
git status --short
grep -n -A6 '<<<<<<<' analyse.py
```
<!--sortie-->
```text
UU analyse.py
10:<<<<<<< HEAD
11-SEUIL = 65  # compromis d'Amine (DT)
12-=======
13-SEUIL = 70  # seuil retenu par Yasmine (DT)
14->>>>>>> seuil-yasmine
15-part = (df["montant"] >= SEUIL).mean()
16-print(f"Part des commandes dès {SEUIL} DT : {part:.1%}")
```

Git a écrit dans le fichier, autour de la ligne litigieuse, trois **marqueurs** :

```text
<<<<<<< HEAD
 …version de la branche où l'on se trouve (main : 65 DT)…
=======
 …version de la branche qu'on fusionne (seuil-yasmine : 70 DT)…
>>>>>>> seuil-yasmine
```

Résoudre le conflit, c'est **éditer le fichier à la main** pour ne garder que ce qu'on veut (ici, après discussion, 70 DT), supprimer les marqueurs, puis déclarer le conflit réglé avec `git add` et conclure par un commit.

```bash
sed -i '/^<<<<<<< /d; /^=======$/d; /^>>>>>>> /d; /^SEUIL = 65/d' analyse.py
grep -n '^SEUIL' analyse.py
python analyse.py | tail -n 3
git add analyse.py
git commit -q --no-edit
git log --oneline --graph | head -n 8
```
<!--sortie-->
```text
10:SEUIL = 70  # seuil retenu par Yasmine (DT)
Name: montant, dtype: float64
Part des commandes dès 70 DT : 29.2%
Satisfaction moyenne : 3.96
*   5b8831d Merge branch 'seuil-yasmine'
|\  
| * dd1b0a7 Seuil à 70 DT
* | 8bcaa34 Seuil à 65 DT
|/  
*   7fbd1eb Merge branch 'seuil-amine'
|\  
| * 5e60494 Seuil à 60 DT (proposition d'Amine)
```

(Le long `sed` enlève les trois lignes de marqueurs et la ligne de la version d'Amine. Avec un éditeur comme VS Code, vous cliquez simplement sur « Accepter la modification actuelle / entrante » ; le principe est identique.) Avant de valider, **toujours relancer le code** : une fusion peut réussir sans conflit et pourtant produire un programme qui ne marche plus.

> 💡 **Réduire les conflits.** Les conflits sont d'autant plus rares que (1) les branches vivent peu de temps, (2) on rapatrie souvent `main` dans sa branche, (3) on évite de reformater un fichier entier « pour faire joli » pendant que d'autres y travaillent, (4) on se répartit les fichiers. Un conflit est surtout un signal de **communication** à rattraper.

Nettoyons les branches devenues inutiles :

```bash
git branch -d seuil-amine seuil-yasmine
git branch
```
<!--sortie-->
```text
Deleted branch seuil-amine (was 5e60494).
Deleted branch seuil-yasmine (was dd1b0a7).
* main
```

### 6.1.9 Étiqueter une version : les tags

Quand une version a une signification particulière (« le rapport remis à la banque »), on lui pose une **étiquette** (*tag*) qui ne bouge plus, contrairement à une branche. On pourra toujours retrouver exactement le code de ce jour-là.

```bash
git tag -a v1.0-rapport-banque -m "Version remise à la banque (mars 2026)"
git tag
git show --stat v1.0-rapport-banque | head -n 6
```
<!--sortie-->
```text
v1.0-rapport-banque
tag v1.0-rapport-banque
Tagger: Yasmine de Dar Jasmin <yasmine@dar-jasmin.example>
Date:   Mon Mar 2 10:00:00 2026 +0100

Version remise à la banque (mars 2026)
```

C'est la réponse à la question qui ouvrait ce chapitre : « quel code a produit le graphique envoyé à la banque ? » Il suffit de noter le *tag* dans le rapport.

### 6.1.10 Dépôts distants : partager et sauvegarder

Jusqu'ici tout se passe sur une seule machine. Pour collaborer, ou simplement se **sauvegarder**, on utilise un **dépôt distant** (*remote*) : un autre dépôt Git, hébergé sur un serveur ou un site comme GitHub. Quatre commandes suffisent à comprendre l'essentiel :

| Commande | Effet |
|---|---|
| `git clone <adresse>` | copie complète d'un dépôt distant (historique compris) sur votre machine |
| `git push` | envoie vos nouveaux commits vers le dépôt distant |
| `git fetch` | récupère les nouveaux commits du distant **sans** toucher à vos fichiers |
| `git pull` | `fetch` puis fusion dans votre branche courante |

Un dépôt distant n'a rien de mystérieux : c'est un dépôt Git comme les autres, souvent « nu » (*bare*, sans dossier de travail, car personne n'y édite directement). Nous pouvons donc le **simuler sans Internet** avec un second dossier de notre machine ! Voici le scénario complet : Yasmine envoie son travail ; Amine le clone, ajoute une ligne et l'envoie à son tour ; Yasmine récupère.

```bash
cd ~/atelier
git init -q --bare depot-partage.git
cd dar-jasmin
git remote add origin ~/atelier/depot-partage.git
git remote -v | sed "s|$HOME|~|"
git push -q -u origin main --tags 2>&1 | tail -n 3
cd ..
git clone -q depot-partage.git copie-amine
cd copie-amine
git config user.name "Amine"
git config user.email "amine@dar-jasmin.example"
git log --oneline | wc -l
```
<!--sortie-->
```text
origin	~/atelier/depot-partage.git (fetch)
origin	~/atelier/depot-partage.git (push)
13
```

(Le `sed` ne sert qu'à abréger le chemin de l'atelier en `~` pour l'affichage.) Après le `push`, le dépôt partagé contient tout l'historique de Yasmine ; le `clone` d'Amine en reçoit une copie intégrale (la dernière commande compte les commits reçus : les 13 de l'historique, fusions comprises ; les deux lignes `git config` donnent à ce clone sa propre identité, Amine travaillant sur une autre machine). Amine travaille :

```bash
echo 'print("Commandes Instagram :", (df["canal"] == "Instagram").sum())' >> analyse.py
git commit -q -am "Ajout du nombre de commandes Instagram"
git push -q origin main 2>&1 | tail -n 3
cd ../dar-jasmin
git pull -q origin main 2>&1 | tail -n 3
git log --format='%an : %s' | head -n 3
python analyse.py | tail -n 1
```
<!--sortie-->
```text
Amine : Ajout du nombre de commandes Instagram
Yasmine de Dar Jasmin : Merge branch 'seuil-yasmine'
Yasmine de Dar Jasmin : Seuil à 65 DT
Commandes Instagram : 138
```

Yasmine a récupéré la modification d'Amine : chaque commit porte le nom de son auteur, et le script affiche bien la nouvelle ligne.

> 🧭 **Et avec GitHub, concrètement ?** *Non exécuté ici (cela demande un compte et une connexion).* Le principe est le même qu'au-dessus, avec une adresse de la forme `https://github.com/nom/depot` ou `git@github.com:nom/depot.git`. Le flux de travail standard en équipe est : (1) créer une **branche** pour chaque tâche ; (2) la pousser sur le site ; (3) ouvrir une **pull request** (*demande de fusion*) : une page où les collègues relisent les changements, commentent, puis acceptent la fusion dans `main` ; (4) supprimer la branche. Le *fork* est une copie personnelle d'un dépôt qui ne vous appartient pas, pour y proposer des modifications.

### 6.1.11 Bonnes pratiques pour la data science

1. **Un commit = une idée.** Corriger un bug et ajouter une analyse, ce sont deux commits.
2. **Ne versionnez pas les gros fichiers de données ni les secrets.** Pour des jeux de données volumineux, on les place ailleurs et on versionne un petit fichier décrivant leur origine, ou l'on utilise un outil dédié (*Git LFS*, *DVC*).
3. **Versionnez le code qui produit les résultats, pas les résultats.** Un graphique se régénère ; un script ne se reconstitue pas.
4. **Commitez souvent, poussez régulièrement.** Un disque dur peut mourir ; un dépôt distant est une sauvegarde.
5. **Ajoutez un fichier `README`** : à quoi sert le projet, comment l'exécuter (6.3 et 6.5).
6. **Posez des tags** sur les versions livrées.

Le mini-aide-mémoire des commandes de la section :

| Je veux… | Commande |
|---|---|
| démarrer un dépôt | `git init` |
| voir l'état du dossier | `git status` |
| préparer / enregistrer | `git add fichier` puis `git commit -m "message"` |
| voir ce qui a changé | `git diff`, `git diff --staged` |
| lire l'historique | `git log --oneline --graph` |
| jeter mes modifications d'un fichier | `git restore fichier` |
| annuler un commit proprement | `git revert <commit>` |
| créer / changer de branche | `git switch -c nom`, `git switch nom` |
| fusionner | `git merge nom` |
| poser une étiquette | `git tag -a nom -m "message"` |
| copier / envoyer / récupérer | `git clone`, `git push`, `git pull` |

> ✅ **À retenir**
> - Git garde un **album de photographies complètes** de votre dossier ; chaque photo (*commit*) porte un message, un auteur, une date et un pointeur vers sa parente.
> - Trois zones : dossier de travail → `git add` → index → `git commit` → dépôt.
> - Presque tout se rattrape (`restore`, `revert`, `switch --detach`) **si l'on a enregistré**. Faites des commits petits et fréquents.
> - Une **branche** est un pointeur : en créer coûte rien ; on y teste une idée avant de **fusionner**.
> - Un **conflit** n'apparaît que lorsque deux changements touchent la même ligne ; on édite, on `add`, on `commit`, et on **relance le code**.
> - `.gitignore` pour les fichiers temporaires et secrets ; les secrets commités sont perdus.
> - Un **dépôt distant** (GitHub…) est un dépôt Git ordinaire qui sert à partager et à sauvegarder.


## 6.2 Notebooks Jupyter

> 💡 **Intuition.** Un **notebook** (« carnet ») est un document où l'on mélange, dans l'ordre où l'on réfléchit : du **texte** (« voici la question »), du **code** (« voici le calcul ») et le **résultat** de ce code (tableau, graphique), juste en dessous. C'est le cahier de laboratoire du data scientist : on explore, on essaie, on commente, et le tout se lit comme un récit. Le projet s'appelle **Jupyter** (de *Julia, Python, R*, les trois langages d'origine) ; ses fichiers portent l'extension `.ipynb`.

Dans un notebook, vous tapez un calcul, appuyez sur `Maj + Entrée`, et le résultat s'affiche à l'instant. Pas de cycle « écrire le fichier, l'enregistrer, lancer le programme, regarder l'écran » : c'est idéal pour **explorer** des données, **enseigner**, ou **raconter** une analyse. Mais cet outil a un défaut sournois, et toute la seconde moitié de cette section lui est consacrée : **un notebook mal tenu produit des résultats qu'on ne peut pas reproduire**.

### 6.2.1 Les ingrédients : cellules et noyau

Un notebook est une suite de **cellules** de deux sortes principales :

| Type de cellule | Contenu | Résultat de l'exécution |
|---|---|---|
| **Code** | du Python (ou un autre langage) | la sortie du code : texte, tableau, graphique, erreur |
| **Markdown** | du texte mis en forme, titres, listes, formules `$…$` | du texte formaté (rien n'est « calculé ») |

Derrière l'interface se cache un second ingrédient, essentiel pour tout comprendre : le **noyau** (*kernel*). C'est un **programme Python qui tourne en arrière-plan**, avec sa **mémoire**. Quand vous exécutez une cellule, son code est envoyé au noyau, qui l'exécute et renvoie le résultat. Les variables créées par une cellule **restent en mémoire dans le noyau** et sont donc visibles par toutes les cellules exécutées ensuite.

```text
  ┌───────────────────────────┐          ┌──────────────────────────┐
  │  Interface (navigateur)   │ ─ code ─►│  Noyau Python            │
  │  cellules, texte, images  │ ◄─ sortie│  (variables en mémoire)  │
  └───────────────────────────┘          └──────────────────────────┘
        le fichier .ipynb                  disparaît si on ferme
        (texte + résultats)                ou redémarre le noyau
```

Retenez bien cette image : **le fichier** `.ipynb` et **la mémoire** du noyau sont deux choses distinctes. Le fichier garde le texte, le code et les derniers résultats affichés ; la mémoire, elle, contient l'état *actuel* des variables, qui peut très bien ne plus correspondre à ce que le code écrit dans le fichier produirait.

Pour installer et lancer l'interface (*non exécuté ici : l'interface s'ouvre dans un navigateur et ne peut pas être reproduite dans un livre*) :

```bash noexec
pip install jupyterlab        # installe JupyterLab (l'interface moderne)
jupyter lab                   # lance le serveur et ouvre le navigateur
```

On peut aussi ouvrir des notebooks directement dans **VS Code** (extension Jupyter), ou en ligne, sans rien installer, dans **Google Colab** (service gratuit de Google ; non testé ici). Le format des fichiers est le même partout.

### 6.2.2 Un notebook est un fichier texte (JSON)

Il n'y a rien de magique dans un fichier `.ipynb` : c'est du **JSON**, un format texte qui décrit des données imbriquées (dictionnaires et listes), lisible par n'importe quel langage. Pour s'en convaincre, nous allons **fabriquer un notebook en Python** avec la bibliothèque `nbformat`, puis l'ouvrir comme un simple texte. Yasmine veut un petit carnet « Ventes de Dar Jasmin » en trois cellules : un titre, le chargement des données, un calcul par canal.

```python
import json
import nbformat
from nbformat import v4 as nbf

nb = nbf.new_notebook()
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
nb.cells = [
    nbf.new_markdown_cell("# Ventes de Dar Jasmin\nMontant moyen des commandes, par canal.", id="titre"),
    nbf.new_code_cell("import pandas as pd\ndf = pd.read_csv('donnees/commandes.csv')\ndf.shape", id="chargement"),
    nbf.new_code_cell("df.groupby('canal')['montant'].mean().round(2)", id="par-canal"),
]
texte = nbformat.writes(nb)
print(texte[:1100])
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
    "# Ventes de Dar Jasmin\n",
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
   "language": "python",
   "name": "python3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
```

Voilà le notebook, vu comme du texte. On y reconnaît : une liste de `cells` ; pour chaque cellule, son `cell_type` (`markdown` ou `code`), sa `source` (le texte tapé), et, pour les cellules de code, deux champs : `execution_count` (le numéro d'exécution, vide tant que la cellule n'a pas tourné) et `outputs` (la liste des résultats affichés, vide pour l'instant). Les `metadata` décrivent le noyau à utiliser. Pas encore de résultats : le carnet n'a jamais été exécuté. Exécutons-le avec `nbclient`, la bibliothèque qui pilote un noyau depuis un programme (c'est ce que fait le bouton « Exécuter tout ») :

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
        Boutique     74.81
        Instagram    49.01
        Site         59.50
        Name: montant, dtype: float64
```

Chaque cellule de code porte désormais son **numéro d'exécution** (`[1]`, `[2]`) et ses **sorties**, enregistrées dans le fichier lui-même. Le texte de la sortie est stocké sous le type `text/plain` ; un graphique serait stocké sous `image/png`, encodé en texte (base64) : un notebook avec beaucoup de graphiques devient donc volumineux.

> 🛠️ **Ce que cela implique, concrètement.** Comme les résultats sont *écrits dans le fichier*, vous pouvez ouvrir un notebook et voir des résultats **sans rien exécuter**. C'est pratique pour partager… et dangereux, car **rien ne garantit que ces résultats correspondent au code affiché** (voir 6.2.3).

### 6.2.3 Le piège : l'état caché

Dans un script Python ordinaire, l'ordre d'exécution est celui du fichier, de haut en bas, toujours. Dans un notebook, **vous choisissez l'ordre** : vous pouvez relancer la cellule 5 trois fois, sauter la cellule 3, retourner modifier la cellule 1 sans relancer les suivantes, ou même supprimer une cellule dont la variable continue d'exister en mémoire. Le noyau, lui, se souvient de tout.

Pour voir ce phénomène sans notebook, **simulons** un noyau avec Python pur : un dictionnaire `memoire` joue la mémoire du noyau, et `executer` joue le rôle de `Maj + Entrée`. Trois cellules calculent le prix total d'une commande de Yasmine : trois paniers à 50 DT, avec TVA à 19 %.

```python
memoire = {}

def executer(code):
    exec(code, memoire)

cellules = {
    "A": "prix_unitaire = 50",
    "B": "total = prix_unitaire * 3 * 1.19",
    "C": "print('Total TTC :', round(total, 2), 'DT')",
}

# Exécution normale : A, puis B, puis C
for nom in "ABC":
    executer(cellules[nom])
```
<!--sortie-->
```text
Total TTC : 178.5 DT
```

Le total attendu est $50\times 3\times 1{,}19 = 178{,}5$ DT. Maintenant, Yasmine se rend compte que le prix unitaire est en fait de 80 DT. Elle retourne à la cellule A, corrige, la relance… puis relance la cellule C pour voir le résultat, **en oubliant de relancer B** :

```python
cellules["A"] = "prix_unitaire = 80"   # on corrige la cellule A
executer(cellules["A"])                # on la relance
executer(cellules["C"])                # on relance C (mais pas B !)
```
<!--sortie-->
```text
Total TTC : 178.5 DT
```

Le total affiché est **toujours 178,5 DT** alors que le prix a changé : la variable `total` en mémoire date de l'ancienne exécution de B. Sur l'écran, la cellule A affiche `80`, la cellule C affiche un total faux, et rien ne signale l'incohérence. Pire : si Yasmine enregistre et envoie ce notebook, son collègue qui l'exécutera de haut en bas obtiendra un résultat **différent** du sien. Voici ce que donnerait une exécution propre, sur un noyau neuf :

```python
memoire = {}                           # noyau tout neuf
for nom in "ABC":
    executer(cellules[nom])
print("Vérification à la main :", 80 * 3 * 1.19)
```
<!--sortie-->
```text
Total TTC : 285.6 DT
Vérification à la main : 285.59999999999997
```

Le vrai total est **285,6 DT**, et non 178,5 DT : l'écart est considérable. (La ligne de vérification affiche `285.59999999999997` au lieu de `285.6` : c'est l'artefact de calcul en virgule flottante rencontré en 1.5, sans importance ici.)

Un second exemple du même piège, encore plus traître : la **cellule supprimée**. Yasmine définit une remise dans une cellule, l'utilise plus bas, puis supprime la cellule de la remise « pour faire propre ». Tout continue de marcher (la variable vit toujours en mémoire)… jusqu'à ce que quelqu'un d'autre ouvre le notebook :

```python
memoire = {}
executer("remise = 0.10")                           # cellule D, qui sera supprimée plus tard
executer("prix_remise = 80 * (1 - remise)")         # cellule E : utilise la variable de D
print("prix remisé (noyau de Yasmine) :", memoire["prix_remise"])

memoire = {}                                        # noyau neuf chez un collègue, sans la cellule D
try:
    executer("prix_remise = 80 * (1 - remise)")
except NameError as erreur:
    print("collègue : NameError :", erreur)
```
<!--sortie-->
```text
prix remisé (noyau de Yasmine) : 72.0
collègue : NameError : name 'remise' is not defined
```

Ces deux scénarios ont un point commun : **le résultat dépendait d'un état invisible**, la mémoire du noyau, qui n'est écrit nulle part dans le fichier. C'est la première cause de notebooks non reproductibles. L'antidote est simple :

> ⚠️ **La règle du « Restart & Run All ».** Avant de partager un notebook, de le commiter ou d'en tirer un chiffre pour un rapport, faites **Noyau → Redémarrer et tout exécuter** (*Restart Kernel and Run All Cells*). Cela efface la mémoire et rejoue toutes les cellules **dans l'ordre du fichier**. Si tout passe et que les résultats ne changent pas, votre notebook est sain. S'il casse, vous venez de découvrir un état caché, et mieux vaut le découvrir maintenant que devant votre client.

> 📐 **Pourquoi cela revient à un problème d'ordre.** Un programme est reproductible si son résultat est une **fonction** de ses entrées (code + données + graine aléatoire). Dans un notebook, le résultat dépend en plus de la **suite des cellules exécutées** : une *séquence*, pas seulement un ensemble. Il existe $n!$ façons d'ordonner $n$ cellules, et le fichier n'en garde qu'une trace partielle (les numéros `[1]`, `[2]`…). Imposer l'ordre du fichier (« Run All ») ramène la dépendance à **une seule** séquence canonique : celle qu'on lit.

### 6.2.4 Un détecteur d'ordre suspect

Les numéros d'exécution enregistrés dans le fichier permettent de repérer les notebooks douteux **sans les exécuter**. Un notebook exécuté d'un seul trait, sur un noyau neuf, affiche `[1]`, `[2]`, `[3]`… sans trou ni saut. Si les numéros sont désordonnés (3, 1, 2), ou si une cellule n'a jamais tourné, ou s'il y a une erreur enregistrée, l'alarme sonne. Écrivons-en un petit détecteur : c'est un bon exemple de **petite application** de ce que nous avons appris au chapitre 4 (fonctions, listes) à un fichier de notebook.

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

print("notebook de Yasmine :", audit(nb))

# Un notebook « bidouillé » : les cellules ont été exécutées dans le désordre
douteux = copy.deepcopy(nb)
douteux.cells[1].execution_count = 3
douteux.cells[2].execution_count = 1
print("notebook bidouillé  :", audit(douteux))
```
<!--sortie-->
```text
notebook de Yasmine : ["OK : notebook exécuté dans l'ordre, sans erreur"]
notebook bidouillé  : ["numéros d'exécution [3, 1] : pas 1, 2, 3… (ordre ou noyau douteux)"]
```

Le premier notebook passe l'audit. Le second, dont nous avons truqué les numéros pour imiter une session désordonnée, est signalé. Le détecteur ne *prouve* pas qu'un notebook est reproductible (la seule preuve est de le réexécuter), mais il repère les cas flagrants en une milliseconde, par exemple dans un script de vérification avant chaque commit.

### 6.2.5 Bonnes pratiques

1. **Restart & Run All avant tout partage.** Règle numéro un.
2. **Les imports et les réglages en première cellule** : bibliothèques, graine aléatoire (`rng = np.random.default_rng(42)`), chemins des fichiers. On voit d'emblée ce dont le notebook dépend.
3. **Un notebook, une question.** Un notebook de 200 cellules est ingérable ; découpez : `01-nettoyage.ipynb`, `02-exploration.ipynb`, `03-modele.ipynb`.
4. **Sortez le code réutilisable dans des fichiers `.py`** (fonctions de nettoyage, de calcul) et importez-les : `from outils import nettoyer`. Ce code se teste (4.6), se versionne proprement avec Git, et sert à d'autres notebooks.
5. **Écrivez du texte entre les cellules** : titres, hypothèses, interprétation. Le notebook est un récit, pas un brouillon.
6. **Chemins relatifs** (`donnees/commandes.csv`), jamais `C:\Users\Yasmine\Bureau\…` : le notebook doit marcher sur une autre machine.
7. **N'utilisez pas le notebook pour la production.** Une fois l'analyse stabilisée, un script `.py` lancé depuis la ligne de commande (6.3) est plus fiable qu'un carnet qu'on clique à la main.

### 6.2.6 Notebooks et Git : le problème des sorties

Un notebook est un fichier texte : Git peut donc le suivre. Mais, comme les **sorties** et les **numéros d'exécution** sont stockés dans le fichier, la moindre ré-exécution modifie des dizaines de lignes (graphiques encodés en base64, numéros qui changent) : les comparaisons `git diff` deviennent illisibles et les conflits de fusion cauchemardesques. La pratique courante est de **ne garder dans Git que les sources**, en effaçant les sorties avant de commiter. Voici l'opération, que nous écrivons nous-mêmes avec `nbformat` :

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

Dans la pratique, on n'écrit pas ce nettoyage à la main : l'outil `nbstripout` (non utilisé ici) s'installe en « crochet » Git et efface les sorties automatiquement à chaque commit. Le revers de la médaille : le fichier commité n'affiche plus de résultats ; on publie alors, à côté, une version **exportée** (voir ci-dessous).

### 6.2.7 Exporter : du notebook au rapport, au script

La bibliothèque `nbconvert` transforme un notebook en d'autres formats : **HTML** (à envoyer par e-mail), **PDF**, **Markdown**, ou **script Python** (le code seul). Avec Python :

```python
from nbconvert import PythonExporter, MarkdownExporter

script, _ = PythonExporter().from_notebook_node(nb)
print(script)
```
<!--sortie-->
```text
#!/usr/bin/env python
# coding: utf-8

# # Ventes de Dar Jasmin
# Montant moyen des commandes, par canal.

# In[1]:


import pandas as pd
df = pd.read_csv('donnees/commandes.csv')
df.shape


# In[2]:


df.groupby('canal')['montant'].mean().round(2)
```

Le script contient le code de chaque cellule, précédé d'un commentaire `# In[1]:` marquant les cellules ; le texte Markdown est transformé en commentaires. Version rapport :

```python
rapport, _ = MarkdownExporter().from_notebook_node(nb)
print(rapport.replace("```", "~~~"))   # ~~~ à la place des accents graves, pour l'affichage dans le livre
```
<!--sortie-->
```text
# Ventes de Dar Jasmin
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
    Boutique     74.81
    Instagram    49.01
    Site         59.50
    Name: montant, dtype: float64
```

Le résultat est un document Markdown contenant le titre, le code de chaque cellule (dans un bloc de code) et ses sorties. (Les blocs de code Markdown s'écrivent normalement avec trois accents graves ; nous les avons remplacés par `~~~` uniquement pour pouvoir afficher le résultat à l'intérieur de ce livre.) C'est ainsi que l'on peut générer un rapport propre à partir d'un notebook.

Même chose en ligne de commande, avec l'option `--execute` qui rejoue d'abord tout le notebook dans un noyau neuf (c'est exactement la règle « Restart & Run All », automatisée). Dans l'atelier, nous créons un petit notebook depuis le terminal, puis le convertissons :

```bash
mkdir -p ~/atelier/notebook
cd ~/atelier/notebook
cp ~/atelier/dar-jasmin/commandes.csv .
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
[NbConvertApp] Writing 268 bytes to satisfaction.md
# Satisfaction par canal


~~~python
import pandas as pd
df = pd.read_csv('commandes.csv')
df.groupby('canal')['satisfaction'].mean().round(2)
~~~




    canal
    Boutique     4.49
    Instagram    3.72
    Site         3.79
    Name: satisfaction, dtype: float64
```

La commande de conversion affiche ce qu'elle fait (lecture du notebook, écriture du fichier `satisfaction.md`) ; `sed` affiche ensuite le document obtenu (avec la même substitution `~~~` que ci-dessus). Pour obtenir un fichier HTML, il suffit de remplacer `markdown` par `html` ; pour un PDF, `--to pdf` demande en plus une installation de LaTeX (6.5).

### 6.2.8 Pour finir : choisir son outil

| Je veux… | J'utilise… |
|---|---|
| explorer des données, essayer des idées | un **notebook** |
| un traitement répétable, automatisé (tous les soirs) | un **script** `.py` |
| une fonction que je vais réutiliser | un **module** `.py`, importé dans le notebook |
| un rapport reproductible de bout en bout | un document qui mélange texte et code, exécuté d'un trait (6.5) |

> ✅ **À retenir**
> - Un notebook = des **cellules** (code / Markdown) + un **noyau** (la mémoire). Le fichier `.ipynb` est du JSON qui stocke le code **et** les derniers résultats.
> - Piège principal : l'**état caché**. La mémoire du noyau peut contenir des variables qui ne correspondent plus au code écrit (cellule modifiée mais pas relancée, cellule supprimée…).
> - Avant de partager : **Restart & Run All**. Des numéros d'exécution `[1], [2], [3]…` sans trou sont bon signe.
> - Rangez le code réutilisable dans des `.py`, ne versionnez pas les sorties, exportez avec `nbconvert`.
> - Un notebook sert à **explorer et raconter**, un script à **produire**.


## 6.3 Ligne de commande et environnements

> 💡 **Intuition.** Une interface graphique, c'est un **menu de restaurant** : on montre du doigt ce qu'on veut parmi ce qui est proposé. La **ligne de commande** (*command line*, *terminal*), c'est parler directement au cuisinier : on peut demander des choses que le menu n'a jamais prévues, et surtout **écrire sa commande sur un papier** pour la rejouer à l'identique demain, ou la donner à un collègue. Pour un data scientist, ce second point est capital : une suite de commandes est une **recette reproductible**, alors qu'une série de clics ne laisse aucune trace.

Le terminal fait peur au début : un écran noir, un curseur clignotant, aucune indication. Il suffit pourtant d'une douzaine de commandes pour devenir efficace, et elles servent pour toute une carrière : sur votre ordinateur, sur un serveur distant, dans un conteneur, dans un outil d'automatisation. Dans ce livre, nous utilisons **Bash**, le terminal de Linux, de macOS et de Git Bash/WSL sous Windows.

### 6.3.1 S'orienter dans les dossiers

Les fichiers sont rangés dans une **arborescence** : un dossier contient des fichiers et d'autres dossiers. Le terminal est toujours « placé » dans un dossier, le **dossier courant**. Cinq commandes pour s'y repérer :

| Commande | Signification | Mnémonique |
|---|---|---|
| `pwd` | afficher le dossier courant | *print working directory* |
| `ls` | lister le contenu du dossier | *list* |
| `cd dossier` | se déplacer dans un dossier | *change directory* |
| `mkdir dossier` | créer un dossier | *make directory* |
| `touch fichier` | créer un fichier vide (ou mettre à jour sa date) | |

Quelques **chemins spéciaux** à connaître : `.` est le dossier courant, `..` le dossier **parent** (celui qui contient le dossier courant), `~` votre dossier personnel, `/` la racine de toute l'arborescence. Un chemin est **absolu** s'il part de la racine (`/home/yasmine/atelier`) et **relatif** s'il part du dossier courant (`donnees/commandes.csv`).

Yasmine organise enfin son travail. Voici l'arborescence d'un projet d'analyse bien rangé, créée d'un coup :

```bash
cd ~/atelier
mkdir -p etude-ventes/{donnees,notebooks,src,rapports}
cd etude-ventes
cp ../dar-jasmin/commandes.csv donnees/
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

La syntaxe `{a,b,c}` est une **expansion d'accolades** : `mkdir -p etude-ventes/{donnees,notebooks,src,rapports}` équivaut à quatre créations. `pwd` donne le dossier courant (nous avons remplacé le début du chemin par `~`, comme le fait votre terminal dans son invite de commande), `ls` en liste le contenu, et `find` en affiche l'arborescence complète, triée. Chaque dossier a un rôle : les données brutes ne se modifient jamais, les notebooks explorent, `src` contient le code réutilisable, `rapports` reçoit les résultats.

Pour **déplacer, renommer, supprimer** :

```bash
mv README.md LISEZMOI.md          # renommer
mv LISEZMOI.md README.md          # et on revient en arrière
cp -r rapports rapports-copie     # copier un dossier entier (-r : récursif)
rm -r rapports-copie              # supprimer un dossier et son contenu
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

> ⚠️ **`rm` n'a pas de corbeille.** Ce qui est supprimé dans le terminal est **définitivement perdu**. Ne tapez jamais `rm -r` sans relire la ligne entière, et n'écrivez jamais de commande de suppression avec un chemin que vous n'avez pas vérifié avec `ls` juste avant. Avec Git (6.1), au moins, vous pouvez toujours récupérer une version enregistrée.

> 🛠️ **Quatre astuces qui changent la vie.** (1) La touche **Tab** complète les noms de fichiers : tapez `cd etu` puis Tab. (2) La flèche **↑** rappelle les commandes précédentes ; `Ctrl + R` cherche dans l'historique. (3) **Ctrl + C** interrompt une commande qui tourne. (4) `commande --help` (ou `man commande`) affiche la documentation de n'importe quelle commande.

### 6.3.2 Regarder le contenu d'un fichier

Un fichier CSV est un fichier **texte** : on peut le lire dans le terminal sans l'ouvrir dans un tableur. C'est très pratique pour vérifier rapidement un fichier de plusieurs millions de lignes que Excel ne saurait pas ouvrir.

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
Instagram,88.2,5,4
Instagram,30.1,4,4
...
Site,62.6,4,3
Instagram,37.5,3,4
Site,31.4,4,4
401 commandes.csv
```

`head -n 5` affiche les 5 premières lignes, `tail -n 3` les 3 dernières, `wc -l` compte les lignes. Le CSV a une ligne d'en-tête (les noms de colonnes) puis une commande par ligne : on retrouve bien 401 lignes. Pour parcourir un long fichier page par page, il existe `less` (on avance avec la barre d'espace, on quitte avec `q`) ; il est interactif, donc nous ne pouvons pas l'illustrer ici. `cat fichier` affiche tout le fichier d'un coup.

### 6.3.3 Interroger des données avec des outils de texte

Il existe quelques outils très anciens, très rapides, et parfaitement adaptés aux fichiers de données en colonnes. Les voici, appliqués au fichier de Dar Jasmin. Chaque outil fait **une chose** :

| Outil | Rôle |
|---|---|
| `grep motif` | garder les lignes qui contiennent le motif |
| `cut -d, -f2` | extraire la colonne n°2 (séparateur `,`) |
| `sort` | trier (`-n` : numérique, `-r` : décroissant, `-t,` : séparateur, `-k2` : colonne) |
| `uniq -c` | compter les lignes identiques **consécutives** (d'où le `sort` avant) |
| `awk` | mini-langage pour calculer sur les colonnes |

Première question : combien de commandes viennent d'Instagram ?

```bash
grep -c Instagram commandes.csv
```
<!--sortie-->
```text
138
```

`grep -c` compte les lignes contenant le mot. (Pandas nous donnerait la même chose avec `(df["canal"] == "Instagram").sum()`.) Combien de commandes par canal ? Il faut extraire la colonne des canaux (sans l'en-tête), la trier pour regrouper les valeurs identiques, puis compter :

```bash
tail -n +2 commandes.csv | cut -d, -f1 | sort | uniq -c | sort -rn
```
<!--sortie-->
```text
    148 Site
    138 Instagram
    114 Boutique
```

Cette ligne est un **pipeline** (« tuyau ») : `tail -n +2` supprime l'en-tête (« commence à la ligne 2 »), `cut -d, -f1` garde la première colonne, `sort` regroupe les canaux, `uniq -c` compte chaque groupe, et `sort -rn` classe du plus fréquent au plus rare. Le site est donc le premier canal en nombre de commandes (148), devant Instagram (138) et la boutique (114) : 400 commandes au total, comme prévu. Le symbole `|` (« pipe ») envoie la sortie d'une commande à l'entrée de la suivante. Quelles sont les trois plus grosses commandes ?

```bash
tail -n +2 commandes.csv | sort -t, -k2 -n -r | head -n 3
```
<!--sortie-->
```text
Site,255.7,4,3
Site,243.8,5,3
Site,217.1,7,4
```

On trie sur la 2ᵉ colonne (`-k2`), numériquement (`-n`), de la plus grande à la plus petite (`-r`), et on garde les trois premières lignes. La plus grosse commande atteint 255,7 DT : c'est le maximum déjà vu avec `describe()` au chapitre 3. Et pour le montant moyen ? Il faut calculer, ce que fait `awk` : il lit le fichier ligne par ligne, `$2` désigne la 2ᵉ colonne, `NR` le numéro de ligne.

```bash
awk -F, 'NR > 1 { somme += $2; n++ } END { printf "montant moyen : %.2f DT sur %d commandes\n", somme/n, n }' commandes.csv
```
<!--sortie-->
```text
montant moyen : 60.25 DT sur 400 commandes
```

L'option `-F,` fixe le séparateur. Pour chaque ligne sauf l'en-tête (`NR > 1`), on ajoute le montant à une somme et on compte ; à la fin (`END`) on affiche la moyenne. Retrouve-t-on bien le 60,25 DT du chapitre 3 ? On peut même faire une moyenne **par canal**, avec un tableau associatif (l'équivalent d'un dictionnaire Python) :

```bash
awk -F, 'NR > 1 { somme[$1] += $2; n[$1]++ }
         END { for (canal in n) printf "%-10s %.2f\n", canal, somme[canal]/n[canal] }' commandes.csv | sort
```
<!--sortie-->
```text
Boutique   74.81
Instagram  49.01
Site       59.50
```

Ces trois moyennes sont celles que `df.groupby("canal")["montant"].mean()` nous avait données en 6.1 : les deux outils sont d'accord, ce qui est rassurant.

> 🧭 **Quand utiliser quoi ?** Ces commandes brillent pour un **coup d'œil rapide**, pour traiter des fichiers trop gros pour la mémoire, ou pour assembler une chaîne de traitement dans un script. Dès que l'analyse devient subtile (jointures, valeurs manquantes, statistiques), on passe à pandas (4.4). Les deux approches sont complémentaires.

### 6.3.4 Pipes et redirections : assembler de petits outils

Toutes ces commandes obéissent à la même philosophie, dite « **philosophie Unix** » : *chaque programme fait une seule chose, la fait bien, et lit/écrit du texte*. Ainsi tous les programmes se branchent les uns sur les autres, comme des briques de LEGO. Il y a trois flux : l'**entrée standard** (clavier ou tuyau), la **sortie standard** (écran) et la **sortie d'erreur** (écran aussi, mais distincte). Les quatre opérateurs de redirection vers ou depuis des fichiers :

| Opérateur | Effet | Exemple |
|---|---|---|
| `>` | écrire la sortie dans un fichier (**écrase** l'existant) | `ls > liste.txt` |
| `>>` | **ajouter** la sortie à la fin du fichier | `echo "fin" >> liste.txt` |
| `<` | lire l'entrée depuis un fichier | `sort < liste.txt` |
| `2>` | rediriger les **messages d'erreur** | `ls absent 2> erreurs.txt` |

À ces quatre opérateurs s'ajoute le **tuyau** (la barre verticale `|`, *pipe* en anglais), déjà utilisé plus haut : il branche la sortie d'une commande directement sur l'entrée de la suivante, sans passer par un fichier. Sauvegardons un résumé des ventes dans un fichier, puis voyons comment les erreurs se redirigent :

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
    138 Instagram
    148 Site
# généré par la ligne de commande
code de sortie : 2
ls: cannot access 'donnees/inexistant.csv': No such file or directory
```

Le premier bloc écrit le décompte dans un fichier (`>`), puis y ajoute une ligne de commentaire (`>>`). Le second tente de lister un fichier qui n'existe pas : le message d'erreur va dans `erreurs.txt` au lieu de s'afficher. (Ici, la commande `ls` a échoué et le code vaut 2.) La variable spéciale `$?` contient le **code de sortie** de la dernière commande : **0 signifie « tout s'est bien passé »**, toute autre valeur signale une erreur. Les scripts s'appuient sur ces codes pour enchaîner des étapes : `commande1 && commande2` lance la seconde **seulement si** la première a réussi ; `commande1 || commande2` la lance seulement si la première a échoué.

### 6.3.5 Lancer des programmes Python depuis le terminal

Jusqu'ici nous avons utilisé des commandes « toutes faites ». Le plus utile est de pouvoir **lancer ses propres scripts Python**, avec des paramètres. Écrivons un petit outil : `src/resume.py` prend en argument le nom d'un fichier CSV et affiche un résumé de ses colonnes numériques. Les arguments tapés après le nom du script sont disponibles en Python dans la liste `sys.argv` (le premier élément, `sys.argv[0]`, est le nom du script lui-même).

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

Notre script respecte la convention : code **0** quand tout va bien, **1** pour un fichier absent, **2** pour un mauvais usage (appel sans argument). Ces codes permettent à d'autres programmes d'enchaîner les étapes automatiquement, et de s'arrêter proprement en cas de problème. Deux variantes utiles de `python` : `python -c "print(2+3)"` exécute une ligne, `python -m module` exécute un module de la bibliothèque (par exemple `python -m venv`, juste après).

### 6.3.6 Le problème des bibliothèques : les environnements virtuels

Voici un scénario qui arrive à tout le monde. En janvier, Yasmine installe `pandas` pour son analyse. En juin, elle commence un autre projet qui nécessite une **ancienne** version de la même bibliothèque. Si tout est installé au même endroit, mettre à jour casse l'ancien projet, et rétrograder casse le nouveau. Pire : quand elle envoie son code à Amine, comment sait-il quelles versions utiliser ? D'où l'**environnement virtuel** :

> 💡 **Définition.** Un environnement virtuel est un **dossier isolé** contenant une copie de l'interpréteur Python et ses propres bibliothèques. Chaque projet a le sien : les bibliothèques de l'un n'affectent jamais celles de l'autre. L'environnement se **crée**, s'**active**, puis on y installe ce dont le projet a besoin avec **pip**, le gestionnaire de paquets de Python.

Voici le cycle complet, avec exactement les commandes de l'avant-propos. Pour ne pas télécharger des centaines de mégaoctets dans cet exemple, nous installerons une toute petite bibliothèque, `tabulate` (qui formate joliment des tableaux en texte), à la place de `pandas`.

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

`python -m venv .venv` crée l'environnement dans un dossier caché nommé `.venv` (le point initial le cache de `ls`). `source .venv/bin/activate` l'**active** : dès cet instant, `python` et `pip` désignent ceux du dossier `.venv`, et l'invite du terminal affiche généralement `(.venv)`. Sous Windows, la commande d'activation est `.venv\Scripts\activate`. L'environnement est **vierge** : la liste des bibliothèques ci-dessus ne contient que `pip` lui-même (ou à peine plus). Installons-en une, et vérifions qu'elle fonctionne :

```bash
pip install --quiet tabulate 2>&1 | grep -v -i -E "notice|warning"
python -c "from tabulate import tabulate; print(tabulate([['Boutique', 74.81], ['Instagram', 49.01], ['Site', 59.5]], headers=['canal', 'montant moyen'], floatfmt='.2f'))"
pip freeze
```
<!--sortie-->
```text
canal        montant moyen
---------  ---------------
Boutique             74.81
Instagram            49.01
Site                 59.50
tabulate==0.10.0
```

`pip install` télécharge et installe la bibliothèque (et ses dépendances) **dans `.venv` uniquement**. `pip freeze` liste tout ce qui est installé, avec les **numéros de version exacts**. Ce dernier point est la clé de la reproductibilité : on enregistre cette liste dans un fichier, traditionnellement nommé `requirements.txt`, que l'on versionne avec Git (6.1) :

```bash
pip freeze > requirements.txt
cat requirements.txt
deactivate
```
<!--sortie-->
```text
tabulate==0.10.0
```

`deactivate` quitte l'environnement et rend le terminal à son état ordinaire. Quelqu'un qui reçoit le projet (Amine, ou Yasmine dans un an) reconstruit **le même environnement** en deux commandes :

```bash
python -m venv .venv-amine
source .venv-amine/bin/activate
pip install --quiet -r requirements.txt 2>&1 | grep -v -i -E "notice|warning"
pip freeze
deactivate
```
<!--sortie-->
```text
tabulate==0.10.0
```

La liste obtenue est **identique** à celle de Yasmine : mêmes bibliothèques, mêmes versions. Le dossier `.venv` lui-même ne se partage pas (il est propre à la machine et volumineux) : il figure dans le `.gitignore` de 6.1, et seul `requirements.txt` voyage avec le projet.

> ⚠️ **`requirements.txt` fige les bibliothèques, pas Python lui-même.** Mentionnez aussi la version de Python dans le `README` (« testé avec Python 3.13 »). Pour des besoins plus avancés, il existe des outils qui gèrent aussi la version de Python : `conda` (très répandu en data science, notamment sous Windows), `uv` (récent et très rapide), ou Poetry. Ils répondent au même besoin : isoler, figer, reproduire.

Pour le livre complet, l'installation recommandée dans l'avant-propos serait donc (*non exécutée ici : elle télécharge environ 200 Mo de bibliothèques*) :

```bash noexec
python -m venv .venv
source .venv/bin/activate        # sous Windows : .venv\Scripts\activate
pip install numpy pandas scipy matplotlib seaborn
pip freeze > requirements.txt
```

### 6.3.7 Variables d'environnement et `PATH`

Le terminal garde en mémoire des **variables** (texte nommé), que l'on affiche avec `$` : c'est ainsi que nous avons utilisé `$?` et `$HOME`. On en crée avec `NOM=valeur` (sans espaces autour du `=`) ; `export` les rend visibles aux programmes lancés ensuite.

```bash
BOUTIQUE="Dar Jasmin"
echo "Bienvenue chez $BOUTIQUE"
export TAUX_TVA=0.19
python -c "import os; print('TVA lue depuis Python :', float(os.environ['TAUX_TVA']))"
```
<!--sortie-->
```text
Bienvenue chez Dar Jasmin
TVA lue depuis Python : 0.19
```

Ce mécanisme sert à **transmettre des réglages** à un programme sans les écrire dans son code : un chemin de fichier, un taux, ou un **mot de passe de base de données** (qu'on ne met jamais dans le code ni dans Git !). Une variable est particulièrement importante : **`PATH`**, la liste des dossiers où le terminal cherche les programmes. Quand vous tapez `python`, le terminal parcourt les dossiers de `PATH` dans l'ordre et lance le premier `python` trouvé. **Activer un environnement virtuel, c'est simplement placer son dossier `bin` en tête du `PATH`** : voilà pourquoi `python` désigne alors celui de `.venv`.

### 6.3.8 Et sous Windows ?

Trois options : **WSL** (un vrai Linux intégré à Windows, recommandé), **Git Bash** (fourni avec Git for Windows), ou **PowerShell** qui a ses propres noms de commandes :

| Bash | PowerShell | Rôle |
|---|---|---|
| `pwd` | `pwd` ou `Get-Location` | dossier courant |
| `ls` | `ls` ou `dir` | lister |
| `cp`, `mv`, `rm` | `cp`, `mv`, `rm` | copier, déplacer, supprimer |
| `cat` | `cat` ou `type` | afficher un fichier |
| `source .venv/bin/activate` | `.venv\Scripts\Activate.ps1` | activer l'environnement |

> ✅ **À retenir**
> - Une suite de commandes est une **recette reproductible** ; un clic n'en est pas une.
> - Se repérer : `pwd`, `ls`, `cd`, `mkdir`, `cp`, `mv`, `rm` (sans corbeille !). `.` = ici, `..` = parent, `~` = maison.
> - Lire et interroger du texte : `head`, `tail`, `wc`, `grep`, `cut`, `sort`, `uniq`, `awk`. On les assemble avec `|`, on redirige avec `>`, `>>`, `2>`.
> - Un programme renvoie un **code de sortie** (0 = succès) ; `&&` et `||` s'appuient dessus.
> - **Un environnement virtuel par projet** : `python -m venv .venv`, `source .venv/bin/activate`, `pip install`, `pip freeze > requirements.txt`. On partage `requirements.txt`, pas `.venv`.


## 6.4 ➕ Pour aller plus loin : scripts shell, environnements avancés et Docker

> 🧭 **Section optionnelle.** Elle prolonge la section 6.3 pour celles et ceux qui veulent **automatiser** leurs analyses (scripts shell), **isoler** plus finement leurs projets, et découvrir **Docker**, l'outil qui emballe un projet avec tout son système. Vous pouvez passer directement à 6.5 sans rien perdre du fil.

### 6.4.1 Écrire un script shell

Quand on retape trois fois la même suite de commandes, on la range dans un **script shell** : un fichier texte contenant des commandes, exécuté d'un coup. Notre premier script, `scripts/rapport.sh`, affiche pour un fichier de commandes le nombre de commandes par canal et leur part. Il introduit les ingrédients de base : **arguments** (`$1` est le premier argument, `$#` leur nombre), **variables**, **test** (`if`), **boucle** (`for`) et **substitution de commande** (`$( … )` insère le résultat d'une commande dans une autre).

```bash
cd ~/atelier/etude-ventes
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

total=$(( $(wc -l < "$fichier") - 1 ))
echo "== Rapport sur $fichier ($total commandes) =="
for canal in Boutique Instagram Site; do
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
  Instagram : 138 commandes (34.5 %)
  Site : 148 commandes (37.0 %)
```

Passons en revue ce fichier, ligne par ligne :

- La première ligne, `#!/usr/bin/env bash`, s'appelle le **shebang** : elle indique avec quel programme exécuter le fichier. Les lignes qui commencent par `#` sont des **commentaires**.
- `set -euo pipefail` est une **ceinture de sécurité** que l'on met en tête de tout script sérieux : `-e` arrête le script à la première commande qui échoue, `-u` refuse d'utiliser une variable jamais définie (souvent une faute de frappe), `-o pipefail` fait échouer un pipeline si l'une de ses commandes échoue (et pas seulement la dernière). Nous verrons plus bas ce qu'elle apporte.
- Le premier `if` vérifie qu'on a reçu un argument (`$#` vaut 1) ; sinon il affiche un mode d'emploi **sur la sortie d'erreur** (`>&2`) et quitte avec le code 2. Le second vérifie que le fichier existe (`-f`).
- `total=$(( $(wc -l < "$fichier") - 1 ))` calcule le nombre de lignes moins l'en-tête (la double parenthèse `$(( … ))` fait de l'arithmétique entière).
- La boucle `for` passe en revue chaque canal ; `grep -c "^$canal,"` compte les lignes **commençant** par le nom du canal suivi d'une virgule (`^` marque le début de ligne) ; `awk` calcule le pourcentage, car le shell ne sait pas faire de décimales.

Les trois parts s'ajoutent bien à 100 %. Le script est utilisable depuis n'importe où ; on peut aussi le rendre directement exécutable :

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

`chmod +x` ajoute le droit d'**exécution** au fichier. Les deux appels fautifs affichent leur message et renvoient des codes différents (1 puis 2), comme au 6.3.5. Un autre usage typique : appliquer un traitement à **chaque fichier** d'un groupe, avec une boucle. Séparons le fichier de données en un fichier par canal (en recopiant l'en-tête dans chacun) :

```bash
mkdir -p donnees/par-canal
for canal in Boutique Instagram Site; do
    (head -n 1 donnees/commandes.csv; grep "^$canal," donnees/commandes.csv) > "donnees/par-canal/$canal.csv"
done
wc -l donnees/par-canal/*.csv
```
<!--sortie-->
```text
 115 donnees/par-canal/Boutique.csv
 139 donnees/par-canal/Instagram.csv
 149 donnees/par-canal/Site.csv
 403 total
```

Le `*` est un **joker** : `donnees/par-canal/*.csv` désigne tous les fichiers `.csv` du dossier. Chaque fichier compte une ligne de plus que son nombre de commandes (l'en-tête) ; le total est donc de 400 commandes + 3 en-têtes.

### 6.4.2 Enchaîner des étapes : un petit pipeline

Un vrai projet d'analyse est une **chaîne d'étapes** : vérifier les données, calculer, produire le rapport. Écrivons-la sous forme d'un script qui appelle notre script shell et notre programme Python de 6.3.5 :

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
  Instagram : 138 commandes (34.5 %)
  Site : 148 commandes (37.0 %)
400 lignes, 4 colonnes
      montant  livraison  satisfaction
mean    60.25       3.29          3.96
min      8.60       0.00          1.00
max    255.70      13.00          5.00
```

Tout se passe bien. Voyons maintenant ce qui se passe quand les données sont introuvables, **avec** puis **sans** la ceinture de sécurité `set -e` (nous fabriquons une copie du script d'où cette ligne est retirée) :

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

Dans le premier cas, le script s'**arrête net** à la première étape défaillante et renvoie un code d'erreur : on sait immédiatement que quelque chose ne va pas. Dans le second, il continue comme si de rien n'était, annonce « terminé » et renvoie le code 0 (succès !) alors que **rien n'a été calculé** : le pire des scénarios, car personne ne se doute que le rapport est vide ou partiel. D'où la règle : **un script qui échoue doit échouer bruyamment**.

> ⚠️ **Les limites du shell.** Le shell est parfait pour **enchaîner des programmes**, manipuler des fichiers et des dossiers. Mais dès qu'il faut des calculs, des structures de données ou de la logique non triviale, passez à Python : ses 300 lignes seront plus lisibles et plus testables que 300 lignes de shell. Règle pratique : si le script dépasse une cinquantaine de lignes ou nécessite des tableaux, c'est un script Python.

### 6.4.3 Faire tourner un script tout seul : `cron`

Sous Linux et macOS, le programme **cron** exécute des commandes à heure fixe. On le configure en ajoutant des lignes à la **table cron** (`crontab -e`). Une ligne comporte cinq champs de temps (minute, heure, jour du mois, mois, jour de la semaine) suivis de la commande. Par exemple, pour lancer notre pipeline tous les jours à 7 h du matin :

```bash noexec
# minute heure jour mois jour-semaine   commande
0 7 * * *  cd ~/etude-ventes && bash scripts/pipeline.sh donnees/commandes.csv
```

(*Non exécuté : la table cron appartient à l'utilisateur de la machine, et le résultat ne se verrait qu'à 7 h.*) Le `*` signifie « toutes les valeurs ». Sous Windows, l'équivalent est le *Planificateur de tâches*. Dans le cloud, on utilise des services d'orchestration plus riches (comme Airflow), que vous rencontrerez dans les volumes suivants de la série.

### 6.4.4 Isoler plus finement : plusieurs versions d'une même bibliothèque

Au 6.3.6, nous avons dit que des projets distincts peuvent avoir besoin de **versions différentes** d'une même bibliothèque. Démontrons-le : en plus de l'environnement `.venv` (qui contient la dernière version de `tabulate`), créons `.venv-ancien` avec une version plus ancienne, **exigée avec `==`** dans la commande d'installation. Les deux coexistent sans se gêner.

```bash
cd ~/atelier/etude-ventes
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

(Ici nous avons appelé directement le `pip` de chaque environnement par son chemin, sans l'activer : c'est strictement équivalent, et très pratique dans un script.) Les deux projets travaillent chacun avec **leur** version : on a deux « mondes » indépendants sur la même machine. Dans un fichier `requirements.txt`, les **numéros de version** peuvent s'écrire avec plus ou moins de rigueur :

| Écriture | Signification |
|---|---|
| `pandas==3.0.0` | exactement cette version (reproductibilité maximale) |
| `pandas>=3.0,<4` | n'importe quelle version 3.x, à partir de la 3.0 |
| `pandas` | n'importe quelle version (déconseillé : le résultat change avec le temps) |

La bonne pratique à retenir : **`==` pour reproduire un résultat** (rapport remis à un client, article), **fourchette** pour une bibliothèque en développement qui doit rester compatible avec d'autres.

Deux outils alternatifs que vous croiserez (*non exécutés ici : non installés*) :

```bash noexec
# conda : un gestionnaire qui installe aussi Python lui-même et des bibliothèques non Python
conda create --name etude-ventes python=3.13 pandas matplotlib
conda activate etude-ventes
conda env export > environment.yml        # l'équivalent de requirements.txt

# uv : un installateur très rapide, compatible avec pip
uv venv
uv pip install -r requirements.txt
```

### 6.4.5 Docker : emballer le projet avec son système

Un environnement virtuel isole les **bibliothèques Python**. Mais votre analyse peut dépendre d'autre chose : une version précise de Python, une bibliothèque système (par exemple pour lire certains fichiers), un outil comme R, une configuration. « Chez moi, ça marche ! » reste possible. **Docker** résout ce problème en emballant le projet avec **tout son système d'exploitation de base**, dans une sorte de mini-ordinateur virtuel appelé **conteneur**.

> 💡 **Une analogie.** Un environnement virtuel, c'est une **étagère personnelle** dans une cuisine partagée : vos ingrédients sont à vous, mais la cuisine (le système) est celle de tout le monde. Docker, c'est un **repas livré dans une boîte hermétique** : la boîte contient les aliments, les couverts et même la table. Où qu'on ouvre la boîte, le repas est identique.

Trois mots à retenir :

- Une **image** est le **modèle** figé : le système de base, Python, vos bibliothèques, votre code. On la construit une fois à partir d'une **recette** (le `Dockerfile`).
- Un **conteneur** est une **instance en marche** d'une image. On peut en lancer dix à partir de la même image.
- Un **registre** (comme *Docker Hub*) est un entrepôt d'images, un peu comme GitHub pour le code : on y trouve des images prêtes à l'emploi (`python`, `postgres`, `jupyter`…).

Voici le `Dockerfile` d'un projet d'analyse comme le nôtre (dans un vrai projet, `requirements.txt` listerait aussi `pandas`) :

```dockerfile
# 1. on part d'une image Python toute prête
FROM python:3.13-slim
# 2. le dossier de travail dans le conteneur
WORKDIR /app
# 3. on copie la liste des bibliothèques...
COPY requirements.txt .
# 4. ...et on les installe
RUN pip install --no-cache-dir -r requirements.txt
# 5. on copie ensuite le reste du projet
COPY . .
# 6. commande lancée au démarrage du conteneur
CMD ["python", "src/resume.py", "donnees/commandes.csv"]
```

Chaque ligne non commentée est une **instruction** (les lignes en `#` sont des commentaires, qui doivent être sur leur propre ligne dans un `Dockerfile`) : `FROM` choisit la base, `WORKDIR` fixe le dossier, `COPY` copie des fichiers de votre machine vers l'image, `RUN` exécute une commande **pendant la construction**, `CMD` définit ce que fera le conteneur **au démarrage**. L'ordre des lignes n'est pas anodin : Docker garde en cache chaque étape, et la copie de `requirements.txt` **avant** celle du code permet de ne pas réinstaller les bibliothèques à chaque modification d'un script.

On construit puis on lance :

```bash noexec
docker build -t etude-ventes .          # construit l'image à partir du Dockerfile
docker run --rm etude-ventes            # lance un conteneur, le supprime à la fin (--rm)
docker run --rm -v "$PWD/rapports:/app/rapports" etude-ventes   # partage le dossier rapports/
```

La troisième commande montre un point essentiel : un conteneur est **éphémère**, ce qu'il écrit disparaît avec lui. Pour récupérer des résultats, on **monte** un dossier de votre machine dans le conteneur (option `-v`).

> ⚠️ **Non exécuté, honnêtement.** Docker n'est pas disponible dans l'environnement où ce livre a été rédigé. Vérifions-le, plutôt que de le supposer :

```bash
command -v docker || echo "docker : absent de cet environnement"
```
<!--sortie-->
```text
docker : absent de cet environnement
```

Le `Dockerfile` et les commandes ci-dessus sont donc donnés **sans sortie**, et n'ont pas été testés ici. Ils suivent le modèle standard de la documentation de Docker ; si vous les essayez, une erreur de syntaxe ou de version est possible, et le message d'erreur vous guidera.

> 🧭 **Docker en data science, à quoi ça sert ?** (1) **Reproduire** une analyse des années plus tard, à l'identique. (2) **Déployer** un modèle sur un serveur (volume III). (3) **Travailler en équipe** sans que chacun installe la même pile logicielle. (4) Lancer facilement des logiciels complexes (une base de données, Jupyter) sans les installer : `docker run postgres`. Le coût : une courbe d'apprentissage et des images volumineuses (quelques centaines de Mo à plusieurs Go).

> ✅ **À retenir**
> - Un **script shell** range des commandes dans un fichier : shebang, arguments (`$1`, `$#`), `if`, `for`, `$(…)`. Commencez-le par `set -euo pipefail` pour qu'il échoue **bruyamment**.
> - Pour tout ce qui est calcul ou logique complexe, passez à Python ; gardez le shell pour **enchaîner**.
> - `cron` lance des commandes à heure fixe (5 champs de temps + commande).
> - Plusieurs environnements virtuels peuvent contenir **des versions différentes** de la même bibliothèque ; `==` fige une version, `>=,<` la borne.
> - **Docker** emballe un projet avec son système (image → conteneur). Ici : concepts et recette donnés, mais **non exécutés**.


## 6.5 ➕ Pour aller plus loin : recherche reproductible

> 🧭 **Section optionnelle.** Elle rassemble les outils du chapitre pour répondre à une exigence centrale de la science des données : **n'importe qui doit pouvoir refaire votre analyse, et obtenir les mêmes résultats.** Vous y verrez comment produire un rapport **qui se régénère tout seul** à partir des données, des graines aléatoires, un fichier `Makefile`, R Markdown, Quarto et LaTeX.

### 6.5.1 Reproductible, répliquable : de quoi parle-t-on ?

Deux mots proches, deux idées différentes :

| Terme | Question posée | Ce qu'on garde fixe | Ce qu'on change |
|---|---|---|---|
| **Reproductibilité** | « Si je relance **exactement** la même analyse, ai-je les mêmes chiffres ? » | données, code, environnement | rien (c'est une exigence **technique**) |
| **Réplicabilité** | « Si quelqu'un refait l'étude avec **de nouvelles données**, arrive-t-il à la même conclusion ? » | la méthode | les données (c'est une exigence **scientifique**) |

On ne peut pas espérer la seconde sans la première : si je ne sais même pas refaire mes propres calculs, personne ne pourra juger si ma conclusion est solide. Une partie des « crises de réplication » observées dans plusieurs disciplines vient de simples **défauts de reproductibilité** : données modifiées à la main dans un tableur, numéros de version oubliés, code introuvable, étapes faites « à la souris ». Les outils des sections précédentes en sont le remède. Voici la **liste de contrôle** que nous allons dérouler :

| Élément | Question à se poser | Outil (section) |
|---|---|---|
| **Données** | Ai-je gardé les données brutes intactes ? Sont-elles identifiables ? | dossier `donnees/` en lecture seule, empreinte `sha256` (6.5.6) |
| **Code** | Est-il versionné ? Retrouve-t-on la version qui a produit le résultat ? | Git (6.1) |
| **Aléa** | Mes simulations donnent-elles les mêmes nombres à chaque fois ? | graines aléatoires (6.5.2) |
| **Environnement** | Quelles versions de Python et des bibliothèques ? | `requirements.txt` (6.3), relevé de versions (6.5.3) |
| **Exécution** | Les étapes s'enchaînent-elles sans intervention manuelle ? | scripts, `Makefile` (6.4, 6.5.5) |
| **Rapport** | Les chiffres du texte viennent-ils *directement* du code ? | documents dynamiques (6.5.4) |

### 6.5.2 L'aléa maîtrisé : les graines

Beaucoup d'analyses font appel au hasard : échantillonnage, simulation, validation croisée, bootstrap (3.7), initialisation de modèles. Or un ordinateur ne tire pas vraiment au hasard : il calcule une suite de nombres qui **a l'air** aléatoire à partir d'un point de départ, la **graine** (*seed*). Même graine, même suite. Sans graine explicite, Python en choisit une différente à chaque exécution (à partir de l'horloge, par exemple), et les résultats changent.

Voici ce que cela donne pour la moyenne d'un petit échantillon tiré au hasard dans les montants des commandes :

```python
import numpy as np
import pandas as pd

montants = pd.read_csv("donnees/commandes.csv")["montant"].to_numpy()

def moyenne_echantillon(rng, taille=10):
    return montants[rng.choice(len(montants), size=taille, replace=False)].mean()

# Sans graine : chaque exécution tire des nombres différents
a = moyenne_echantillon(np.random.default_rng())
b = moyenne_echantillon(np.random.default_rng())
print("sans graine, deux exécutions identiques ?", a == b)

# Avec graine : la même suite à chaque exécution
c = moyenne_echantillon(np.random.default_rng(42))
d = moyenne_echantillon(np.random.default_rng(42))
print("graine 42 deux fois :", round(c, 2), "et", round(d, 2), "-> identiques ?", c == d)
```
<!--sortie-->
```text
sans graine, deux exécutions identiques ? False
graine 42 deux fois : 46.55 et 46.55 -> identiques ? True
```

Sans graine, les deux tirages diffèrent (à une coïncidence près, de probabilité quasi nulle) ; avec la même graine 42, on obtient **exactement** le même nombre à chaque fois, sur n'importe quel ordinateur (pour la même version de NumPy). C'est ce qui rend les nombres du livre reproductibles.

Reste à savoir **quelle graine choisir**. La réponse est contre-intuitive : *n'importe laquelle*, mais **sans la choisir en regardant le résultat**. Changer de graine jusqu'à obtenir le résultat qui nous arrange est une forme de triche appelée *p-hacking* (voir 3.5). La graine sert à **figer** une exécution, pas à l'améliorer. Pour vérifier qu'un résultat n'est pas un accident de graine, on l'observe pour **plusieurs graines** :

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

Les moyennes d'échantillons de 10 commandes varient fortement d'une graine à l'autre (voir l'erreur-type, 3.2) : la graine 42 n'a donc rien de spécial, et une conclusion qui ne tiendrait que pour elle serait suspecte. Deux règles pratiques : **(1)** créer **un seul** générateur `rng = np.random.default_rng(graine)` en début de programme, et le passer aux fonctions qui en ont besoin (comme ci-dessus), plutôt que de multiplier les graines cachées ; **(2)** se souvenir que chaque bibliothèque a sa propre source d'aléa (`random` de Python, NumPy, et plus tard PyTorch ou scikit-learn avec leur paramètre `random_state`) : il faut fixer **chacune** de celles qu'on utilise.

> ⚠️ **Une graine ne garantit pas l'identité entre versions.** Les mêmes graine et code peuvent donner des tirages différents si la **version** de NumPy change (les algorithmes évoluent). D'où la nécessité de noter aussi les versions, juste après.

### 6.5.3 Relever l'environnement

Le fichier `requirements.txt` (6.3) fige les bibliothèques à *installer*. On peut aussi, en fin de rapport, **imprimer ce qui a réellement servi**. Cela prend quelques lignes et sauve bien des enquêtes :

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

La sortie est le **relevé des versions** de cette exécution. Vous pouvez l'ajouter au bas de chaque rapport (nous le ferons juste après) ; en R, la fonction `sessionInfo()` joue ce rôle.

### 6.5.4 Un rapport qui se fabrique tout seul

Le défaut le plus courant d'un rapport : on calcule un chiffre dans un notebook, on le **recopie à la main** dans un document Word, et trois semaines plus tard on met à jour les données sans mettre à jour le texte. Le remède s'appelle le **document dynamique** (*literate programming*, « programmation lettrée ») : le texte et les chiffres sont produits **par le même programme**, donc ils ne peuvent pas diverger.

Nous allons construire cette chaîne, étape par étape, avec ce que nous avons déjà :

```text
 donnees/commandes.csv ──► src/faire_rapport.py ──► rapport.md ──► pandoc ──► HTML, PDF
        (données)             (code : calcule et          (texte et chiffres      (mise en forme)
                               écrit le texte)             cohérents)
```

Première étape : un programme Python qui **écrit** un document Markdown en y insérant les chiffres calculés. Le format de sortie est du Markdown, le même que celui qui sert à écrire ce livre.

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

print("---")
print('title: "Les ventes de Dar Jasmin"')
print("lang: fr")
print("---")
print()
print("## Résumé")
print()
print(f"Le fichier contient **{n} commandes**. Le montant moyen est de **{fr(m.mean())} DT** "
      f"(intervalle de confiance à 95 % : de {fr(m.mean() - marge)} à {fr(m.mean() + marge)} DT), "
      f"et la médiane de **{fr(m.median())} DT**.")
print()
print("L'intervalle est calculé par $\\bar{x} \\pm 1{,}96\\,\\frac{s}{\\sqrt{n}}$.")
print()
print("## Par canal de vente")
print()
print("| Canal | Commandes | Montant moyen (DT) |")
print("|:------|----------:|-------------------:|")
for canal, ligne in par_canal.iterrows():
    print(f"| {canal} | {int(ligne['count'])} | {fr(ligne['mean'])} |")
print()
meilleur = par_canal["mean"].idxmax()
print(f"Le canal au panier moyen le plus élevé est **{meilleur}**.")
FIN
python src/faire_rapport.py donnees/commandes.csv > rapports/rapport-ventes.md
cat rapports/rapport-ventes.md
```
<!--sortie-->
```text
---
title: "Les ventes de Dar Jasmin"
lang: fr
---

## Résumé

Le fichier contient **400 commandes**. Le montant moyen est de **60,25 DT** (intervalle de confiance à 95 % : de 56,52 à 63,97 DT), et la médiane de **51,00 DT**.

L'intervalle est calculé par $\bar{x} \pm 1{,}96\,\frac{s}{\sqrt{n}}$.

## Par canal de vente

| Canal | Commandes | Montant moyen (DT) |
|:------|----------:|-------------------:|
| Boutique | 114 | 74,81 |
| Instagram | 138 | 49,01 |
| Site | 148 | 59,50 |

Le canal au panier moyen le plus élevé est **Boutique**.
```

Le programme n'écrit **aucun chiffre en dur** : le nombre de commandes, la moyenne, l'intervalle, le tableau et même la phrase sur le « meilleur canal » sont calculés. Si les données changent demain, il suffit de relancer. (Les doubles barres `\\` dans le texte du programme sont des échappements Python pour obtenir une seule barre `\` dans le LaTeX de la formule.) Le résultat est un fichier Markdown propre. **Pandoc**, le « couteau suisse » de la conversion de documents (installé avec ce livre), le transforme en d'autres formats. Convertissons-le en page web HTML, vérifions son contenu en texte brut, et fabriquons un PDF :

```bash
pandoc --standalone --mathml rapports/rapport-ventes.md -o rapports/rapport-ventes.html
pandoc rapports/rapport-ventes.md -t plain | head -n 14
pandoc rapports/rapport-ventes.md -o rapports/rapport-ventes.pdf --pdf-engine=xelatex
head -c 5 rapports/rapport-ventes.pdf; echo
```
<!--sortie-->
```text
[WARNING] Could not convert TeX math \bar{x} \pm 1{,}96\,\frac{s}{\sqrt{n}}, rendering as TeX
Résumé

Le fichier contient 400 commandes. Le montant moyen est de 60,25 DT
(intervalle de confiance à 95 % : de 56,52 à 63,97 DT), et la médiane de
51,00 DT.

L’intervalle est calculé par $\bar{x} \pm 1{,}96\,\frac{s}{\sqrt{n}}$.

Par canal de vente

  Canal         Commandes   Montant moyen (DT)
  ----------- ----------- --------------------
  Boutique            114                74,81
  Instagram           138                49,01
%PDF-
```

L'option `--mathml` demande à Pandoc de convertir la formule en MathML, une écriture que les navigateurs savent afficher. La commande `-t plain` montre le texte tel qu'un lecteur le verrait en texte brut : le tableau est mis en forme, et Pandoc **avertit** (`[WARNING]`) qu'il ne sait pas écrire une fraction avec de simples caractères et laisse donc la formule en LaTeX. C'est normal : un format purement textuel n'a pas de fraction. Les cinq premiers octets du fichier PDF sont `%PDF-` : c'est la signature de ce format, preuve que le PDF a bien été produit (ouvrez-le avec votre lecteur habituel pour voir la mise en page). Le moteur `xelatex` fabrique le PDF en passant par **LaTeX**, que nous verrons plus bas.

Pour ajouter le relevé des versions en bas du rapport, il suffirait d'une petite fonction (celle du 6.5.3) dans `faire_rapport.py`. Retenez le principe : **pas de date du jour ni de valeur aléatoire non figée dans un rapport reproductible**, sinon deux exécutions ne produisent plus le même fichier.

### 6.5.5 `make` : ne refaire que ce qui a changé

Tant que la chaîne tient en deux commandes, on les retape. Mais un vrai projet compte des dizaines d'étapes : nettoyage, tableaux, graphiques, rapport. Relancer **tout** à chaque modification est lent ; relancer **à la main** les bonnes étapes est source d'oublis. L'outil **`make`** (né en 1976, toujours en pleine forme) résout les deux problèmes. On lui décrit dans un fichier nommé `Makefile` des **règles** de la forme :

```text
cible: dépendances
<TAB>commande qui fabrique la cible à partir des dépendances
```

`make` compare les **dates de modification** : si une dépendance est plus récente que la cible, il **refait** la cible ; sinon il ne fait rien. Voici le `Makefile` de notre projet. (Attention : l'indentation des commandes **doit être une vraie tabulation**, pas des espaces.)

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

(Dans le fichier, nous avons écrit `<TAB>` puis la commande `sed` le remplace par une vraie tabulation, pour que l'exemple soit sans ambiguïté.) Lisons les règles. La première cible, `tout`, est celle qu'on construit par défaut ; elle dépend du rapport HTML. Le rapport HTML dépend du fichier Markdown ; le fichier Markdown dépend des **données** et du **programme** qui le fabrique. Dans les commandes, `$@` désigne la cible, `$<` la première dépendance. Cette fois, **`make` affiche chaque commande qu'il lance** : on voit qu'après `make propre` (qui supprime les fichiers produits), le premier `make` refait les **deux** étapes, le deuxième `make` répond qu'il n'y a **rien à faire**, et que, quand on « touche » le fichier de données (ce qui met à jour sa date), les **deux** étapes sont de nouveau déclenchées.

> 💡 **Le grand intérêt.** Il suffit de modifier le texte du rapport, et seule la conversion se refait. Dans un grand projet, c'est un gain de temps considérable, et, surtout, **la documentation de la chaîne de traitement** est le `Makefile` lui-même : un lecteur voit d'un coup d'œil de quoi dépend quoi. Le `README` du projet peut alors se résumer à : « Pour tout reproduire : `make` ».

### 6.5.6 Les outils « tout-en-un » : R Markdown et Quarto

Notre chaîne maison (Python qui écrit du Markdown, puis Pandoc) fonctionne, mais le monde de la data science a standardisé la même idée dans des outils dédiés : un **seul fichier** mélange texte Markdown et **blocs de code** ; à la compilation, le code est exécuté et **ses résultats sont insérés** dans le document final (HTML, PDF, Word, diaporama).

**R Markdown** (pour R, mais aussi Python) fonctionne ainsi : le fichier `.Rmd` contient un en-tête, du texte, des blocs de code `{r}` et du code R **en ligne** dans le texte (`` `r ...` ``). Comme le format utilise les trois accents graves que ce livre emploie lui-même pour afficher du code, nous écrivons ici les blocs avec des tildes `~~~`, puis une commande `sed` les remplace par les vrais accents graves avant la compilation :

```bash
mkdir -p ~/atelier/etude-rmd
cd ~/atelier/etude-rmd
cp ~/atelier/etude-ventes/donnees/commandes.csv .
cat > rapport.Rmd <<'FIN'
---
title: "Satisfaction des clients de Dar Jasmin"
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
Satisfaction des clients de Dar Jasmin

Voici le lien entre le délai de livraison et la note de satisfaction.

    d <- read.csv("commandes.csv")
    d <- d[d$canal != "Boutique", ]      # on ne garde que les commandes livrées
    tapply(d$satisfaction, d$livraison <= 3, mean)

    ##    FALSE     TRUE 
    ## 3.631313 4.034091

La satisfaction moyenne des commandes livrées est de 3.76 sur 286
commandes.
```

On y retrouve le même principe : le chiffre du texte (le code `r round(…)` écrit entre accents graves, au milieu de la phrase) est **calculé** à la compilation, et le bloc de code est exécuté, avec son résultat inséré. Le bloc de code a été exécuté lors de la compilation, et sa sortie est insérée sous lui (les lignes qui commencent par `##`). `tapply` calcule la satisfaction moyenne séparément pour `FALSE` (livraison de plus de 3 jours : environ 3,63) et `TRUE` (3 jours ou moins : environ 4,03) : les clients livrés rapidement sont plus satisfaits, ce qui est conforme à l'intuition. Les chiffres du paragraphe suivant (la moyenne générale et le nombre de commandes) sont eux aussi calculés par le code R en ligne. Notez le détail : R affiche un point décimal (`3.76`), alors que notre rapport Python écrivait une virgule grâce à sa petite fonction `fr()`.

**Quarto** est le successeur de R Markdown : même idée, mais indépendant du langage (Python, R, Julia), avec davantage de formats (sites, livres, présentations). Un fichier `.qmd` ressemble à ceci :

~~~markdown
---
title: "Les ventes de Dar Jasmin"
format: html
---

Le montant moyen est de `{python} round(moyenne, 2)` DT.

```{python}
import pandas as pd
df = pd.read_csv("donnees/commandes.csv")
moyenne = df["montant"].mean()
df.groupby("canal")["montant"].mean().round(2)
```
~~~

```bash noexec
quarto render rapport.qmd              # produit rapport.html
quarto render rapport.qmd --to pdf     # produit un PDF (via LaTeX)
```

> ⚠️ **Non exécuté.** Quarto n'est pas installé dans l'environnement de rédaction : l'exemple `.qmd` et les deux commandes ci-dessus sont donnés **à titre d'illustration, sans avoir été testés ici**. (R Markdown, lui, a bien été exécuté ci-dessus.) La syntaxe exacte, notamment celle du code en ligne `{python}`, peut dépendre de la version de Quarto : consultez sa documentation si vous l'installez.

### 6.5.7 LaTeX : composer proprement les formules et les PDF

**LaTeX** (on prononce « latèk ») est le langage de composition de documents scientifiques : c'est lui qui met en forme les formules des chapitres 1 à 3 de ce livre. Vous l'avez déjà écrit sans le savoir : `$\bar{x}$`, `\sum`, `\frac{a}{b}` sont des commandes LaTeX. Un document complet se compose d'un **préambule** (les réglages) et d'un **corps**. Compilons un minuscule document, qui contient l'intervalle de confiance du chapitre 3 :

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

Le code de sortie 0 indique que la compilation a réussi, et le fichier `mini.pdf` commence bien par la signature `%PDF-`. Si une erreur survient (une accolade oubliée), `xelatex` s'arrête et la raison se trouve dans `compilation.log`. En pratique, vous n'écrirez presque jamais du LaTeX *complet* : vous le laisserez Pandoc ou Quarto générer à partir du Markdown, et vous n'écrirez à la main que les formules. Pour écrire à plusieurs un document LaTeX sans rien installer, le service en ligne **Overleaf** est très utilisé (non testé ici).

### 6.5.8 Garder une empreinte des données

Dernier maillon de la chaîne : s'assurer que les **données** n'ont pas changé en cachette. Une **empreinte cryptographique** (*hash*) est un court texte, calculé à partir du contenu d'un fichier : le moindre changement du fichier (même un seul chiffre) change complètement l'empreinte. C'est le principe que nous avons vu au 6.1.4 pour les objets de Git. On calcule celle de `commandes.csv`, on la **note dans le `README`**, et n'importe qui peut vérifier :

```bash
cd ~/atelier/etude-ventes
sha256sum donnees/commandes.csv > donnees/EMPREINTES.sha256
cat donnees/EMPREINTES.sha256
sha256sum -c donnees/EMPREINTES.sha256
echo "--- une faute de frappe glisse dans le fichier ---"
sed -i '2s/44.8/448.0/' donnees/commandes.csv
sha256sum -c donnees/EMPREINTES.sha256 || echo "ALERTE : les données ont été modifiées"
```
<!--sortie-->
```text
824d99115defe345920b4c8d4425fb4a1ab6b7a01e20984831cf564827e8d1b3  donnees/commandes.csv
donnees/commandes.csv: OK
--- une faute de frappe glisse dans le fichier ---
donnees/commandes.csv: FAILED
sha256sum: WARNING: 1 computed checksum did NOT match
ALERTE : les données ont été modifiées
```

La première vérification répond `OK`. Après avoir **modifié un seul nombre** (le premier montant, 44,8, devenu 448,0 par une faute de frappe), la vérification échoue : l'alerte sonne avant même qu'on lance l'analyse. Remettons le fichier en état :

```bash
sed -i '2s/448.0/44.8/' donnees/commandes.csv
sha256sum -c donnees/EMPREINTES.sha256
```
<!--sortie-->
```text
donnees/commandes.csv: OK
```

> 🛠️ **Le « kit de reproductibilité » d'un projet, en une page.** Un dossier de projet bien tenu contient : un `README` (but, comment reproduire, version de Python), un fichier `requirements.txt`, les données brutes **non modifiées** avec leur empreinte, le code versionné avec Git, un `Makefile` (ou un script) qui enchaîne les étapes, et le rapport généré. Pour archiver une version définitive de manière pérenne, on dépose le tout sur un service qui attribue un identifiant stable (*DOI*), comme **Zenodo** (non testé ici).

> ✅ **À retenir**
> - **Reproductible** = mêmes données + même code + même environnement ⟹ mêmes résultats. **Répliquable** = mêmes conclusions sur de nouvelles données.
> - **Graine aléatoire** : fixer *une* graine par exécution, la choisir *avant* de voir les résultats, et vérifier sur plusieurs graines que la conclusion tient. Noter aussi les versions des bibliothèques.
> - **Document dynamique** : le texte et les chiffres sortent du **même** programme (Python + Pandoc, R Markdown, Quarto) ; on ne recopie jamais un chiffre à la main.
> - **`make`** ne refait que ce qui est périmé ; le `Makefile` documente la chaîne de traitement.
> - **LaTeX** compose les formules et les PDF ; on le fait généralement générer par Pandoc ou Quarto.
> - Une **empreinte** (`sha256sum`) détecte toute modification des données.


## 6.6 Exercices du chapitre 6

> 🧭 Cherchez d'abord par vous-même (en tapant les commandes dans un vrai terminal !), vérifiez ensuite, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse. Les corrigés ont été **réellement exécutés** dans l'atelier ; leurs sorties sont celles du livre. Les exercices utilisent un dossier de travail neuf, `~/atelier/exercices`, et le fichier `commandes.csv`.

### Énoncés

**Exercice 1 ⭐ (se repérer).** Créez le dossier `projet-yasmine` contenant deux sous-dossiers, `donnees` et `src`, copiez-y `commandes.csv` (dans `donnees`), puis (a) affichez l'arborescence créée, (b) affichez les **trois dernières** lignes du fichier, (c) comptez ses lignes.

**Exercice 2 ⭐ (tuyaux).** Combien de commandes ont reçu chacune des notes de satisfaction (1 à 5) ? Répondez avec **une seule ligne** de commandes enchaînées par des tuyaux, puis vérifiez avec pandas.

**Exercice 3 ⭐ (premiers pas avec Git).** Dans un nouveau dépôt `journal`, créez un fichier `notes.txt` contenant la ligne « Hypothèse : les commandes Instagram sont plus petites. » et enregistrez-le (commit 1). Ajoutez une seconde ligne « Test à faire : comparer les moyennes par canal. » et enregistrez (commit 2). Par maladresse, vous supprimez ensuite `notes.txt` avec `rm`. Retrouvez-le **sans refaire à la main**, puis affichez l'historique en une ligne par commit.

**Exercice 4 ⭐⭐ (awk).** Calculez, pour chaque canal, le **pourcentage de commandes notées 4 ou 5** (colonne `satisfaction`), avec `awk`. Vérifiez avec pandas.

**Exercice 5 ⭐⭐ (conflit).** Un fichier `params.txt` contient la ligne `seuil=50`. Sur une branche `prudent`, vous passez la valeur à `seuil=40` ; sur `main`, votre collègue la passe à `seuil=60`. Fusionnez `prudent` dans `main`. Que se passe-t-il ? Résolvez le conflit en gardant la valeur la **plus élevée**, et terminez la fusion.

**Exercice 6 ⭐⭐ (état caché).** Un notebook contient, de haut en bas, les cinq cellules suivantes :
(A) `n = 100` ; (B) `taux = 0.19` ; (C) `tva = n * taux` ; (D) `n = 200` ; (E) `print(tva)`.
Yasmine les exécute dans l'ordre **A, B, D, C, E** (elle a lancé D avant C). (a) Qu'affiche E ? (b) Qu'afficherait E après « Restart & Run All » ? (c) Quelle conclusion en tirez-vous ?

**Exercice 7 ⭐⭐ (environnement).** Créez un environnement virtuel `env-a`, installez-y `tabulate==0.8.9` et enregistrez les versions dans `requirements.txt`. Reconstruisez ensuite, dans un second environnement `env-b`, **exactement les mêmes** bibliothèques à partir de ce seul fichier, et prouvez qu'elles sont identiques.

**Exercice 8 ⭐⭐ (script shell).** Écrivez un script `compte.sh` qui prend **deux arguments**, un fichier CSV et un numéro de colonne, et affiche le nombre d'occurrences de chaque valeur de cette colonne (sans l'en-tête). Il doit s'arrêter avec un message et un code d'erreur non nul si on lui donne un mauvais nombre d'arguments ou un fichier inexistant. Testez-le sur la colonne 1 puis sur la colonne 4.

**Exercice 9 ⭐⭐⭐ (Makefile).** Écrivez un `Makefile` dont la cible `resume.txt` dépend de `commandes.csv` et du script `resume.py`, et qui la fabrique par `python resume.py commandes.csv > resume.txt`. Montrez que : (a) un premier `make` construit la cible, (b) un deuxième ne fait rien, (c) modifier le script (date de modification) relance la construction, (d) modifier un fichier **sans rapport** (`LISEZMOI.txt`) ne la relance pas.

**Exercice 10 ⭐⭐⭐ (synthèse : un projet reproductible).** Montez un mini-projet « rapport sur les ventes » qui réunit tout le chapitre : dépôt Git avec `.gitignore`, données, script de rapport, `Makefile`, empreinte `sha256` des données, un commit étiqueté `v1.0`. Démontrez sa reproductibilité : **clonez** le dépôt dans un autre dossier, vérifiez l'empreinte des données, lancez `make`, et prouvez que le rapport obtenu est **identique octet pour octet** à l'original.

### Corrigés

**Corrigé 1.** `mkdir -p` crée d'un coup les dossiers imbriqués (et l'accolade en crée deux) ; `find` affiche l'arborescence ; `tail -n 3` et `wc -l` répondent à (b) et (c).

```bash
mkdir -p ~/atelier/exercices
cd ~/atelier/exercices
mkdir -p projet-yasmine/{donnees,src}
cp ~/atelier/dar-jasmin/commandes.csv projet-yasmine/donnees/
find projet-yasmine | sort
tail -n 3 projet-yasmine/donnees/commandes.csv
wc -l projet-yasmine/donnees/commandes.csv
```
<!--sortie-->
```text
projet-yasmine
projet-yasmine/donnees
projet-yasmine/donnees/commandes.csv
projet-yasmine/src
Site,62.6,4,3
Instagram,37.5,3,4
Site,31.4,4,4
401 projet-yasmine/donnees/commandes.csv
```

Le fichier compte 401 lignes : 400 commandes plus l'en-tête.

**Corrigé 2.** La note est dans la 4ᵉ colonne. On enlève l'en-tête (`tail -n +2`), on extrait la colonne (`cut`), on **trie** (indispensable avant `uniq`), puis on compte les groupes (`uniq -c`) :

```bash
cd ~/atelier/exercices/projet-yasmine/donnees
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

Les deux méthodes donnent les mêmes effectifs : la note 4 est la plus fréquente (195 commandes sur 400), et les notes très basses sont rares (une seule note 1), ce qui est cohérent avec une satisfaction moyenne proche de 4 (3.1). Le total fait bien 400.

**Corrigé 3.** `git restore` ramène un fichier supprimé ou modifié à son état du dernier commit. Comme notre `rm` a supprimé le fichier **sans** l'enregistrer, c'est la bonne commande :

```bash
cd ~/atelier/exercices
mkdir journal
cd journal
git init -q
echo "Hypothèse : les commandes Instagram sont plus petites." > notes.txt
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
Hypothèse : les commandes Instagram sont plus petites.
Test à faire : comparer les moyennes par canal.
07f3ebd Ajout du test à faire
7c4ddf0 Première hypothèse
```

Après le `rm`, `ls` n'affiche rien (le fichier a disparu) ; après `git restore`, le fichier est revenu avec **ses deux lignes**, car elles figuraient dans le dernier commit. Le tout a été possible parce qu'on avait enregistré : un fichier jamais commité aurait été perdu.

**Corrigé 4.** On compte, pour chaque canal, le nombre total de commandes (`n`) et le nombre de commandes notées 4 ou 5 (`bons`) ; à la fin, on affiche le pourcentage. (Dans `awk`, une variable ou une case de tableau jamais utilisée vaut 0, donc `bons[c]` fonctionne même si un canal n'a aucune bonne note.)

```bash
cd ~/atelier/exercices/projet-yasmine/donnees
awk -F, 'NR > 1 { n[$1]++; if ($4 >= 4) bons[$1]++ }
         END { for (c in n) printf "%-10s %.1f %%\n", c, 100 * bons[c] / n[c] }' commandes.csv | sort
```
<!--sortie-->
```text
Boutique   95.6 %
Instagram  63.0 %
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
Boutique     95.6
Instagram    63.0
Site         69.6
Name: satisfaction, dtype: float64
```

Les deux approches coïncident. Les clients de la **boutique** sont les plus satisfaits : pas de délai de livraison, donc pas de pénalité (voir la construction du jeu de données au 3.1.2, où la note diminue avec le délai).

**Corrigé 5.** Les deux branches ont modifié **la même ligne** : Git ne peut pas choisir, il signale un conflit. On édite le fichier pour garder `seuil=60`, on déclare le conflit résolu avec `git add`, puis on termine par un commit.

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
*   a1b9309 Merge branch 'prudent'
|\  
| * fd20715 Seuil prudent
* | 6669eef Seuil ambitieux
|/  
* ded7106 Paramètre initial
seuil=60
```

Le graphe montre bien la **fusion** de deux lignes de travail en un commit à deux parents. N'oubliez pas, dans un vrai projet, de **relancer le code** avant de valider.

**Corrigé 6.** On simule le noyau avec un dictionnaire, comme au 6.2.3. Le point clé est l'**ordre d'exécution**, pas l'ordre d'écriture :

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

(a) Dans l'ordre réellement joué, `n` vaut déjà 200 quand C calcule la TVA : E affiche $200\times0{,}19=38$. (b) Dans l'ordre du fichier, C est exécutée alors que `n` vaut encore 100 : E affiche $100\times0{,}19=19$. (c) Le **même notebook** donne deux résultats différents selon l'ordre d'exécution : le chiffre que Yasmine voyait à l'écran (38) n'est pas celui qu'obtiendra quiconque ouvrira le fichier et exécutera tout (19). C'est exactement l'état caché du 6.2.3 : **toujours** redémarrer et tout exécuter avant de se fier à un résultat. (Une analyse correcte de la logique du carnet dirait aussi que la cellule D, placée *après* C mais qui change `n`, est probablement mal placée.)

**Corrigé 7.** On crée le premier environnement, on y installe la version exacte demandée, puis on fige ; le second environnement est reconstruit uniquement depuis `requirements.txt`.

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

La commande `cmp` compare deux fichiers octet par octet et ne dit rien s'ils sont identiques ; notre `&& echo` confirme alors le succès. (On appelle ici directement `env-a/bin/pip` au lieu d'activer l'environnement : c'est strictement équivalent, cf. 6.4.4.)

**Corrigé 8.** Le script vérifie ses arguments (`$#`), l'existence du fichier (`-f`), puis enchaîne les outils du 6.3 : `tail` (supprimer l'en-tête), `cut` (extraire la colonne), `sort`, `uniq -c`.

```bash
cd ~/atelier/exercices/projet-yasmine
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
    138 Instagram
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

Les effectifs de la colonne 4 sont ceux de l'exercice 2, et ceux de la colonne 1 retrouvent les 148, 138 et 114 commandes du 6.3. Les deux appels fautifs affichent leur message et renvoient des codes **2** (mauvais usage) et **1** (fichier absent), comme convenu.

**Corrigé 9.** Le `Makefile` décrit la dépendance de `resume.txt` à ses deux sources. Pour l'écrire sans ambiguïté sur les tabulations, nous employons encore la substitution `<TAB>` du 6.5.5.

```bash
cd ~/atelier/exercices
mkdir make-demo
cd make-demo
cp ~/atelier/etude-ventes/src/resume.py .
cp ~/atelier/dar-jasmin/commandes.csv .
echo "Notes de lecture" > LISEZMOI.txt
cat > Makefile <<'FIN'
resume.txt: commandes.csv resume.py
<TAB>python resume.py commandes.csv > resume.txt
FIN
sed -i 's/^<TAB>/\t/' Makefile
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

(a) Le premier `make` exécute la commande ; (b) le deuxième répond que la cible est déjà à jour ; (c) en modifiant la date du script (ce qui simule une modification), `make` détecte que la dépendance est plus récente que la cible et **refabrique** ; (d) `LISEZMOI.txt` n'est pas une dépendance : `make` n'y réagit pas. Seul ce qui est **déclaré** comme dépendance déclenche une reconstruction, d'où l'importance de **lister toutes** les sources dans la règle.

**Corrigé 10.** C'est le projet de synthèse du chapitre. On le construit pas à pas, puis on le **clone** pour le rejouer ailleurs. D'abord le projet, avec son script de rapport (très simple, il n'écrit ni date ni valeur aléatoire), son `Makefile` et l'empreinte des données :

```bash
cd ~/atelier/exercices
mkdir ventes-reproductibles
cd ventes-reproductibles
git init -q
mkdir donnees src rapports
cp ~/atelier/dar-jasmin/commandes.csv donnees/
sha256sum donnees/commandes.csv > donnees/EMPREINTES.sha256
cat > src/rapport.py <<'FIN'
import sys
import pandas as pd

df = pd.read_csv(sys.argv[1])
print("# Rapport sur les ventes")
print()
print(f"- Commandes : {len(df)}")
print(f"- Montant moyen : {df['montant'].mean():.2f} DT")
print(f"- Satisfaction moyenne : {df['satisfaction'].mean():.2f} / 5")
FIN
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
- Montant moyen : 60.25 DT
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
295a1b8 Projet de rapport reproductible
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

Les données sont intègres (`OK`), le rapport a été refabriqué par `make`, et la comparaison `cmp` confirme qu'il est **identique** à l'original. C'est la définition opérationnelle de la reproductibilité : *un tiers, sur un dossier neuf, obtient exactement le même résultat avec une commande*. Chaque élément du chapitre y a joué son rôle : Git (le code et ses versions), le `.gitignore`, le `Makefile`, l'empreinte des données, et, pour l'environnement, le `requirements.txt` que l'on ajouterait dans un vrai projet (ici l'environnement est celui du livre).

---

## Bilan du chapitre 6

Vous savez maintenant :

- **versionner** votre travail avec Git : photographier (`add`, `commit`), comparer (`diff`), défaire (`restore`, `revert`), travailler en parallèle (branches, fusions, conflits) et partager (dépôts distants) ;
- **utiliser un notebook** pour explorer et raconter, **sans tomber dans le piège de l'état caché** (Restart & Run All, détecteur d'ordre, ne pas versionner les sorties) ;
- **vous servir du terminal** : vous repérer, lire, filtrer et résumer des fichiers avec `grep`, `cut`, `sort`, `uniq` et `awk`, assembler des commandes avec les tuyaux et les redirections, comprendre les codes de sortie ;
- **isoler chaque projet** dans un environnement virtuel et **figer** ses dépendances dans `requirements.txt` ;
- (en option) **automatiser** avec des scripts shell et `make`, comprendre Docker, fabriquer un **rapport dynamique** (Python + Pandoc, R Markdown, Quarto, LaTeX), maîtriser les graines aléatoires et surveiller l'intégrité des données avec une empreinte.

Le fil rouge de tout le chapitre tient en une phrase : **un résultat n'existe que s'il peut être refait**. Vous disposez désormais de l'ensemble des fondations du volume : les mathématiques (chapitre 1), les probabilités (2), la statistique (3), la programmation (4), les bases de données (5) et les outils de travail (6). Il est temps de tout assembler dans le **projet du volume** : une étude complète des ventes de Dar Jasmin, des données brutes jusqu'au rapport.
