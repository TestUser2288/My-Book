<!-- NOTE POUR LA MAINTENANCE : les fichiers sections/06-*.md se remplissent en UN SEUL appel de fill.py (sessions bash partagées, ordre 06-0 → 06-6), avec :
     DONNEES=<chemin absolu du dossier donnees/>  PATH=<venv avec pandas, nbformat, nbclient, nbconvert, ipykernel en tête>  NO_COLOR=1
     Le cahier (cahier/06-exercices.md) se remplit à part, avec les mêmes variables ; il est autonome.
     Outils système requis : git, pandoc, xelatex (+polyglossia), make, R (+rmarkdown, knitr), sha256sum. Réseau requis pour 6.3.6 et pour le cahier (pip install tabulate).
     Les blocs `hide` préparent l'état de la session bash (dossiers, fichiers) sans apparaître dans le livre. -->

# Chapitre 6 : Outils de travail

> « Un bon artisan ne se reconnaît pas seulement à ses gestes, mais à **l'ordre de son atelier**. »

Vous savez maintenant calculer (chapitres 1 à 3), programmer (chapitre 4) et interroger une base de données (chapitre 5). Reste une question que personne n'ose poser en cours, mais qui décide de la vie quotidienne d'un data scientist : **comment ne pas se perdre dans son propre travail ?**

Voici la scène, que tout le monde a vécue au moins une fois. La gérante ouvre le dossier de son analyse des ventes :

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

Quelle version a produit le graphique envoyé à la banque la semaine dernière ? Impossible de le savoir. Que s'est-il passé quand elle a « juste changé un petit truc » mardi soir, et que tous les chiffres se sont mis à bouger ? Mystère. Et si un collègue veut l'aider, comment fusionnent-ils leurs deux versions sans écraser le travail de l'autre ?

Ce chapitre vous donne **quatre outils** qui répondent à ces questions, et qui sont utilisés dans toutes les équipes de données du monde.

## Le chemin de ce chapitre

- **6.1 Git et gestion de versions** : une machine à remonter le temps pour vos fichiers. On y apprend à photographier son travail (*commit*), à comparer, à défaire, à travailler à plusieurs (*branches*, *fusions*, *conflits*) et à partager (*dépôts distants*).
- **6.2 Notebooks Jupyter** : le carnet de laboratoire interactif où code, résultats et explications cohabitent. On y apprend aussi à **s'en méfier** : un notebook mal utilisé produit des résultats que personne ne peut reproduire.
- **6.3 Ligne de commande et environnements** : parler directement à l'ordinateur avec du texte, enchaîner de petits outils, et isoler les bibliothèques de chaque projet dans un **environnement virtuel**.
- ➕ **Pour aller plus loin** : scripts shell et bases de Docker (6.4) ; recherche reproductible, de Pandoc à Quarto en passant par LaTeX et Make (6.5).
- **Bilan du chapitre.** Les applications guidées et les exercices corrigés de ce chapitre se trouvent dans le **cahier** (chapitre 6) ; chaque section y renvoie.

> 🧭 **Le fil conducteur : la reproductibilité.** Un résultat n'a de valeur que si **quelqu'un d'autre (ou vous-même dans six mois) peut le refaire**. Chaque outil de ce chapitre attaque une cause différente de non-reproductibilité : Git (« quelle version du code ? »), les notebooks bien tenus (« dans quel ordre a-t-on exécuté les cellules ? »), les environnements (« avec quelles versions des bibliothèques ? »), les graines aléatoires et les `Makefile` (« avec quelles données et quelles étapes ? »). Le terme technique est la *reproductibilité computationnelle*.

> 🧭 **Comment lire ce chapitre.** Contrairement aux précédents, les exemples se tapent dans un **terminal** (aussi appelé *console* ou *shell*), pas dans Python. Sous Linux et macOS, ouvrez l'application « Terminal ». Sous Windows, installez **Git for Windows** (il fournit *Git Bash*, un terminal compatible avec tous nos exemples) ou, mieux, **WSL** (le sous-système Linux de Windows). Les lignes à taper sont celles des blocs de code ; les blocs gris qui suivent montrent ce que l'ordinateur répond. Le livre n'en garde que l'essentiel : les séances complètes, pas à pas, sont dans le cahier.

## L'atelier de la gérante

Pour que les exemples soient concrets, nous préparons un petit **atelier** : un dossier de travail dans lequel nous copions le fichier de données du livre.

> 📦 **À propos de `$DONNEES`.** Le fichier `commandes.csv` est fourni avec le livre dans le dossier `donnees/`. Dans les exemples qui suivent, la variable `$DONNEES` désigne le **chemin de ce dossier** sur la machine qui exécute le code. Chez vous, remplacez `"$DONNEES"` par l'endroit où vous avez rangé le fichier (par exemple `~/livre/donnees`). Le caractère `~` est une abréviation pour votre dossier personnel ; nous l'expliquons au 6.3.

```bash
mkdir -p ~/atelier/boutique
cd ~/atelier/boutique
cp "$DONNEES/commandes.csv" .
ls
```
<!--sortie-->
```text
commandes.csv
```

Chaque ligne tapée est une **commande** : un nom (`mkdir`, `cd`, `cp`, `ls`) suivi d'**arguments**. Ici : créer un dossier (`mkdir`, pour *make directory* ; l'option `-p` crée aussi les dossiers intermédiaires), s'y placer (`cd`, *change directory*), y copier le fichier (`cp`, *copy* ; le point `.` désigne « le dossier où je suis »), puis lister le contenu (`ls`, *list*).

> ⚠️ **Honnêteté sur l'exécution.** Tous les exemples de ce chapitre qui peuvent s'exécuter sans réseau ni logiciel spécial ont été **réellement exécutés** dans un atelier jetable, et la sortie affichée est la vraie. Les rares exceptions (Docker, Quarto, services en ligne comme GitHub) sont clairement signalées « **non exécuté** » : nous n'y affichons que la commande, jamais une sortie inventée.


## 6.1 Git et gestion de versions

> 💡 **Intuition.** Imaginez que vous puissiez, à tout moment, prendre une **photographie complète** de votre dossier de travail, lui donner un titre (« ajout du calcul par canal de vente »), et la ranger dans un album. Plus tard, vous pouvez feuilleter l'album, comparer deux photos, revenir à celle d'il y a un mois, ou même ouvrir **deux albums parallèles** pour tester une idée folle sans toucher à la version qui marche. **Git** est exactement cet album, avec trois cadeaux en plus : il est gratuit, il fonctionne hors ligne, et il permet à plusieurs personnes de travailler sur le même dossier sans se marcher dessus.

Cette section présente les idées et les commandes essentielles, avec de courts exemples. Les séances complètes, pas à pas, sont proposées dans le cahier (applications 6.1 à 6.3).

### 6.1.1 Pourquoi pas simplement « analyse_FINAL_vrai.py » ?

Copier ses fichiers avec un suffixe (`_v2`, `_FINAL`) semble naturel, mais les défauts apparaissent vite :

| Problème | Avec des copies de fichiers | Avec Git |
|---|---|---|
| « Qu'est-ce qui a changé entre hier et aujourd'hui ? » | Ouvrir deux fichiers et comparer à l'œil | `git diff` liste chaque ligne modifiée |
| « Pourquoi ai-je changé ça ? » | Personne ne s'en souvient | Chaque version porte un **message** daté et signé |
| « Je veux revenir à la version de mars » | Si elle existe encore et si son nom est clair | Une commande |
| « Je veux tester une idée sans risque » | Dupliquer tout le dossier | Une **branche**, en une seconde |
| « Un collègue et moi avons modifié le même fichier » | L'un des deux écrase l'autre, ou on recopie à la main | Git **fusionne** et signale seulement les vrais conflits |
| « Quel code a produit ce graphique ? » | Aucune idée | On retrouve la version exacte |

Git a été créé en 2005 par Linus Torvalds pour développer le noyau Linux ; il est aujourd'hui le standard de fait, bien au-delà de la programmation : vous l'utiliserez pour du code, des notebooks, des rapports en texte, des fichiers de configuration.

> 🧭 **Git et GitHub, ce n'est pas pareil.** *Git* est le logiciel qui tourne **sur votre machine** et garde l'historique. *GitHub*, *GitLab* ou *Bitbucket* sont des **sites web** qui hébergent des copies de dépôts Git pour les partager. On peut utiliser Git des années sans jamais toucher à GitHub.

### 6.1.2 Premiers réglages

Chaque version enregistrée est **signée** : il faut dire à Git qui vous êtes, une fois pour toutes.

```bash
git config --global user.name "La gérante"
git config --global user.email "gerante@boutique.example"
git config --global init.defaultBranch main
git config --global --list
```
<!--sortie-->
```text
user.name=La gérante
user.email=gerante@boutique.example
init.defaultbranch=main
```

Les réglages sont rangés dans le fichier `.gitconfig` de votre dossier personnel. La branche par défaut s'appellera `main` (l'ancien nom était `master`).


> 💡 **Une astuce de reproductibilité (à ne pas reproduire chez vous).** Chaque version Git est identifiée par une empreinte qui dépend, entre autres, **de la date**. Pour que le livre affiche toujours les mêmes empreintes, nous avons fixé artificiellement la date de toutes les versions de cette section. Chez vous, Git utilisera l'horloge et vos empreintes seront différentes des nôtres : aucun raisonnement ne dépend de leur valeur.

### 6.1.3 Le premier dépôt : init, add, commit

Un **dépôt** (*repository*, ou *repo*) est un dossier que Git surveille. On l'initialise avec `git init`. Écrivons le tout premier script d'analyse de la gérante, qui calcule le montant moyen des commandes, puis demandons à Git ce qu'il en pense.

```bash
cd ~/atelier/boutique
git init -q
cat > analyse.py <<'FIN'
import pandas as pd
df = pd.read_csv("commandes.csv")
print("Montant moyen :", round(df["montant"].mean(), 2), "€")
FIN
git status --short
```
<!--sortie-->
```text
?? analyse.py
?? commandes.csv
```

Le double point d'interrogation `??` signifie **non suivi** (*untracked*) : Git a remarqué les deux fichiers mais ne les surveille pas encore. Pour comprendre la suite, il faut connaître les **trois zones** de Git :

```text
 dossier de travail        zone d'index              dépôt (historique)
  (vos fichiers)     ──►   (« staging area »)  ──►   (les photos rangées)
                  git add                     git commit
```

- Le **dossier de travail** contient vos fichiers, tels que vous les éditez.
- La **zone d'index** (*staging area*) est la table où l'on **prépare la prochaine photo** : on y dépose seulement ce qu'on veut y voir.
- Le **dépôt** contient les photos prises, à jamais (les *commits*).

Pourquoi cette zone intermédiaire ? Parce qu'on a souvent modifié trois fichiers pour trois raisons différentes : on peut ainsi faire **trois commits distincts et propres** plutôt qu'un fourre-tout.

```bash
git add analyse.py commandes.csv
git commit -q -m "Premier script et données (400 commandes)"
git log --oneline
```
<!--sortie-->
```text
04c558e Premier script et données (400 commandes)
```

`git log --oneline` montre une ligne par version : l'empreinte courte, puis le message.

> ⚠️ **Écrire de bons messages.** Un message de commit répond à la question « **que fait** ce changement, et pourquoi ? », dans un langage que vous comprendrez dans six mois. « maj » ou « modifs » sont inutiles ; « Ajout du montant moyen par canal de vente » est excellent. Convention courante : une première ligne courte (une cinquantaine de caractères).

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : application 6.1, exercice 6.3.

### 6.1.4 Ce qu'il y a vraiment dans un commit

> 📐 **Rigueur : le modèle d'objets de Git.** Un *commit* n'est pas une liste de différences : c'est une **photographie complète** du dossier, accompagnée de métadonnées et d'un **pointeur vers le commit précédent** (son *parent*). Chaque objet est stocké sous un nom qui est l'**empreinte de son contenu** (une fonction de hachage SHA-1, qui transforme n'importe quel contenu en un nombre de 40 chiffres hexadécimaux). Il y a trois sortes d'objets :
>
> - un **blob** : le contenu d'un fichier, sans son nom ;
> - un **arbre** (*tree*) : la liste des fichiers d'un dossier, avec pour chacun le nom et l'empreinte de son blob ;
> - un **commit** : l'empreinte d'un arbre, l'empreinte du ou des parents, l'auteur, la date, le message.
>
> Conséquence cruciale : si on change **un seul caractère** dans un fichier, l'empreinte du blob change, donc celle de l'arbre, donc celle du commit, et de tous ses descendants. Un historique Git ne peut donc pas être modifié en douce : c'est ce qui le rend digne de confiance. Autre conséquence : deux fichiers de contenu identique partagent le même blob, et Git ne les stocke qu'une fois.

C'est vérifiable à la main. L'empreinte d'un blob est simplement le SHA-1 de la chaîne `blob`, suivie de la taille du contenu, d'un caractère nul, puis du contenu. Calculons-la avec Git, puis sans Git, avec l'outil `sha1sum` :

```bash
echo "bonjour" > bonjour.txt
git hash-object bonjour.txt
printf 'blob 8\0bonjour\n' | sha1sum
```
<!--sortie-->
```text
1cd909e05d33f0f6bc4ea1caf19b5749b434ceb3
1cd909e05d33f0f6bc4ea1caf19b5749b434ceb3  -
```

Les deux empreintes sont **identiques** : Git ne fait rien de magique, il hache le contenu (8 octets : les 7 lettres de « bonjour » plus le saut de ligne). Voyons le dernier commit « de l'intérieur » :

```bash
git cat-file -p HEAD
```
<!--sortie-->
```text
tree 14f9f852d095c04f65343c0f4fb89e500c3460ad
author La gérante <gerante@boutique.example> 1772442000 +0100
committer La gérante <gerante@boutique.example> 1772442000 +0100

Premier script et données (400 commandes)
```

On lit l'empreinte de l'arbre (`tree`), l'auteur, la date (en secondes) et le message. Ce premier commit n'a pas de ligne `parent` ; les suivants en auront une. Le mot `HEAD` désigne « le commit où je suis en ce moment » ; `HEAD~1` est son parent.


### 6.1.5 Modifier, comparer, enregistrer : le cycle de travail

Le quotidien avec Git est une boucle de quatre gestes : **modifier** des fichiers, **regarder** ce qui a changé (`git status`, `git diff`), **choisir** ce qui part dans la prochaine photo (`git add`), **enregistrer** (`git commit`). La gérante veut maintenant le montant moyen **par canal de vente**.

```bash
echo 'print(df.groupby("canal")["montant"].mean().round(2))' >> analyse.py
git diff
git commit -q -am "Ajout du montant moyen par canal"
git log --oneline
```
<!--sortie-->
```text
diff --git a/analyse.py b/analyse.py
index 4f821d9..51a90f6 100644
--- a/analyse.py
+++ b/analyse.py
@@ -1,3 +1,4 @@
 import pandas as pd
 df = pd.read_csv("commandes.csv")
 print("Montant moyen :", round(df["montant"].mean(), 2), "€")
+print(df.groupby("canal")["montant"].mean().round(2))
5dca424 Ajout du montant moyen par canal
04c558e Premier script et données (400 commandes)
```

`git diff` montre les différences entre le dossier de travail et la dernière photo : les lignes précédées de `+` sont ajoutées, celles précédées de `-` seraient supprimées, et le bloc `@@ … @@` situe la modification dans le fichier. L'option `-a` de `git commit` ajoute d'office les fichiers **déjà suivis** qui ont changé.

> 💡 **Trois variantes utiles de `git diff`.** `git diff` compare le dossier de travail à l'index (« ce que je n'ai pas encore préparé ») ; `git diff --staged` compare l'index au dernier commit (« ce qui partira au prochain commit ») ; `git diff HEAD~1 HEAD` compare deux commits. Pour relire l'historique avec le détail des fichiers touchés : `git log --stat`.

### 6.1.6 Défaire une erreur

C'est la plus grande qualité de Git : **presque tout se rattrape**, à condition de choisir la bonne commande.

| Situation | Commande | Effet |
|---|---|---|
| « J'ai cassé un fichier, je veux la version du dernier commit. » | `git restore fichier` | le fichier revient à l'état du dernier commit |
| « J'ai enregistré une erreur dans un commit. » | `git revert <commit>` | un **nouveau** commit fait l'inverse ; l'historique reste intact |
| « Je veux revoir l'état du dossier à une date passée. » | `git switch --detach <commit>` | on regarde le passé sans rien détruire ; `git switch main` pour revenir |

Voici les deux premières en action : la gérante vide son script par erreur et le retrouve, puis commite une ligne de debug qu'elle annule proprement.

```bash
> analyse.py                  # oups : le fichier est vidé
git restore analyse.py        # on retrouve le dernier commit
wc -l analyse.py
echo 'print("TODO")' >> analyse.py
git commit -q -am "Ligne de debug oubliée"
git revert --no-edit HEAD
```
<!--sortie-->
```text
4 analyse.py
[main 02d76fa] Revert "Ligne de debug oubliée"
 Date: Mon Mar 2 10:00:00 2026 +0100
 1 file changed, 1 deletion(-)
```

Le fichier a retrouvé ses 4 lignes ; l'historique contient maintenant l'erreur *et* son annulation, et le script est redevenu propre.

> ⚠️ **`git restore` est irréversible pour les modifications non enregistrées.** Ce que Git n'a jamais photographié, il ne peut pas le retrouver. D'où la règle d'or : **faites des commits petits et fréquents**. Et méfiez-vous de `git reset --hard`, `git clean -fd` et `git push --force`, qui détruisent du travail sans confirmation ; en cas de doute, créez d'abord une branche de secours (`git branch sauvegarde`).

### 6.1.7 Ce qu'il ne faut pas suivre : `.gitignore`

Certains fichiers n'ont rien à faire dans l'historique : les fichiers temporaires de Python (`__pycache__/`), l'environnement virtuel (`.venv/`, section 6.3), les mots de passe, les données volumineuses ou confidentielles. On les déclare dans un fichier texte nommé `.gitignore`.


```bash
cat > .gitignore <<'FIN'
.venv/
__pycache__/
*.env
FIN
git status --short
git check-ignore -v secrets.env
```
<!--sortie-->
```text
?? .gitignore
.gitignore:3:*.env	secrets.env
```

Git ne voit plus que `.gitignore` lui-même (qu'on **veut** suivre, pour que toute l'équipe ignore les mêmes choses). `git check-ignore -v` explique pourquoi un fichier est ignoré : il cite la règle et la ligne responsable.

> ⚠️ **Un secret commité est un secret perdu.** Si vous enregistrez par erreur un mot de passe ou une clé d'accès, le retirer dans un commit suivant ne suffit pas : il reste lisible dans l'historique. Considérez-le comme compromis et **changez-le**. Prévenez l'erreur en mettant `.gitignore` en place **avant** de créer le fichier secret.


### 6.1.8 Les branches : tester une idée sans risque

Une **branche** est une ligne de travail parallèle. Techniquement, c'est trivial : un simple **pointeur** (une étiquette) vers un commit, qui avance à chaque nouveau commit. Créer une branche ne copie rien : cela prend une milliseconde, quelle que soit la taille du dépôt.

#### Une expérience sur une branche, puis la fusion

La gérante se demande à partir de quel montant offrir la livraison. Elle ouvre une branche dédiée à cette expérience, plutôt que de modifier le script principal ; quand elle est satisfaite, elle la **fusionne** (*merge*) dans `main`. Comme `main` n'a pas bougé entretemps, Git n'a rien à réconcilier : il se contente d'**avancer le pointeur** (*fast-forward*).

```bash
git switch -c seuil-livraison
printf 'SEUIL = 80\nprint("part >= SEUIL :", (df["montant"] >= SEUIL).mean())\n' >> analyse.py
git commit -q -am "Seuil de livraison gratuite à 80 €"
git switch main
git merge seuil-livraison
```
<!--sortie-->
```text
Switched to a new branch 'seuil-livraison'
Switched to branch 'main'
Updating 5798a46..a21fa8b
Fast-forward
 analyse.py | 2 ++
 1 file changed, 2 insertions(+)
```

Tant qu'on est sur `main`, avant la fusion, les lignes du seuil **n'existent pas** dans le fichier : elles ne vivent que sur la branche, et rien n'est perdu. Après la fusion, `main` les contient.

#### Quand les deux ont bougé : fusion automatique, puis conflit

Le cas intéressant arrive quand **deux personnes** modifient le dépôt en parallèle. Un collègue, Sam, teste sur sa branche un seuil de 60 € ; la gérante, sur `main`, ajoute une moyenne de satisfaction. Les deux historiques divergent, en « Y », puis se rejoignent dans un **commit de fusion** à deux parents :

```text
        branche de Sam : seuil à 60 €
       ●───────────────────────╮
      ╱                         ╲
 ●───●   (point de départ)       ●   commit de fusion
      ╲                         ╱
       ●───────────────────────╯
        main : moyenne de satisfaction
```


```bash
git merge --no-edit seuil-sam
```
<!--sortie-->
```text
Auto-merging analyse.py
Merge made by the 'ort' strategy.
 analyse.py | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

Git a réussi **automatiquement** : les deux changements portaient sur des zones différentes du fichier. Un **conflit** survient quand les deux branches modifient **la même ligne** de façons différentes : Git ne sait pas laquelle choisir et vous demande de trancher. Ce n'est pas une catastrophe, c'est le fonctionnement normal du travail à plusieurs. Provoquons-en un : la gérante veut un seuil de 70 €, Sam de 65 €.


```bash
git merge --no-edit seuil-gerante
grep -n -A4 '<<<<<<<' analyse.py
```
<!--sortie-->
```text
Auto-merging analyse.py
CONFLICT (content): Merge conflict in analyse.py
Automatic merge failed; fix conflicts and then commit the result.
5:<<<<<<< HEAD
6-SEUIL = 65
7-=======
8-SEUIL = 70
9->>>>>>> seuil-gerante
```

Git s'arrête (`CONFLICT (content)`) et écrit dans le fichier, autour de la ligne litigieuse, trois **marqueurs** : `<<<<<<< HEAD` (début de la version de la branche où l'on se trouve), `=======` (séparation) et `>>>>>>> seuil-gerante` (fin de la version qu'on fusionne). Résoudre le conflit, c'est **éditer le fichier à la main** pour ne garder que ce qu'on veut (ici, après discussion, 70 €), supprimer les marqueurs, puis déclarer le conflit réglé avec `git add` et conclure par un commit. Avant de valider, **relancez toujours le code** : une fusion peut réussir sans conflit et pourtant produire un programme qui ne marche plus.


```bash
# (après avoir édité analyse.py : on garde SEUIL = 70 et on supprime les marqueurs)
git add analyse.py
git commit -q --no-edit
git log --oneline --graph | head -n 5
```
<!--sortie-->
```text
*   9161812 Merge branch 'seuil-gerante'
|\  
| * 885efd7 Seuil à 70 €
* | 3dcee2e Seuil à 65 €
|/  
```

> 💡 **Réduire les conflits.** Ils sont d'autant plus rares que les branches vivent peu de temps, qu'on rapatrie souvent `main` dans sa branche, qu'on évite de reformater un fichier entier pendant que d'autres y travaillent, et qu'on se répartit les fichiers. Un conflit est surtout un signal de **communication** à rattraper.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : application 6.2, exercice 6.5.

### 6.1.9 Étiqueter une version : les tags

Quand une version a une signification particulière (« le rapport remis à la banque »), on lui pose une **étiquette** (*tag*) qui ne bouge plus, contrairement à une branche.

```bash
git tag -a v1.0-rapport-banque -m "Version remise à la banque"
git tag
```
<!--sortie-->
```text
v1.0-rapport-banque
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

Un dépôt distant n'a rien de mystérieux : c'est un dépôt Git comme les autres, souvent « nu » (*bare*, sans dossier de travail). On peut donc le **simuler sans Internet** avec un second dossier de la machine : c'est l'objet de l'application 6.3 du cahier. Avec un vrai service, les commandes ressemblent à ceci (*non exécuté ici : il faut un compte et une connexion*) :

```bash noexec
git remote add origin git@github.com:nom/depot.git   # déclarer l'adresse du dépôt distant
git push -u origin main                              # envoyer son travail
git pull                                             # récupérer celui des autres
```

Le flux de travail standard en équipe est : (1) créer une **branche** pour chaque tâche ; (2) la pousser sur le site ; (3) ouvrir une **pull request** (*demande de fusion*) : une page où les collègues relisent les changements, commentent, puis acceptent la fusion dans `main` ; (4) supprimer la branche. Le *fork* est une copie personnelle d'un dépôt qui ne vous appartient pas, pour y proposer des modifications.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : application 6.3.

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
> - Une **branche** est un pointeur : en créer ne coûte rien ; on y teste une idée avant de **fusionner**.
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

Il n'y a rien de magique dans un fichier `.ipynb` : c'est du **JSON**, un format texte qui décrit des données imbriquées (dictionnaires et listes), lisible par n'importe quel langage. Pour s'en convaincre, fabriquons un notebook de deux cellules avec la bibliothèque `nbformat`, et regardons la cellule de code **comme du simple texte** :

```python
import json
import nbformat
from nbformat import v4 as nbf

nb = nbf.new_notebook(cells=[
    nbf.new_markdown_cell("# Ventes de la boutique", id="titre"),
    nbf.new_code_cell("import pandas as pd\ndf = pd.read_csv('donnees/commandes.csv')\ndf.shape", id="chargement"),
])
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
print(json.dumps(nb.cells[1], indent=1))
```
<!--sortie-->
```text
{
 "id": "chargement",
 "cell_type": "code",
 "metadata": {},
 "execution_count": null,
 "source": "import pandas as pd\ndf = pd.read_csv('donnees/commandes.csv')\ndf.shape",
 "outputs": []
}
```

On y reconnaît le `cell_type` (`code`), la `source` (le texte tapé), et deux champs propres aux cellules de code : `execution_count` (le numéro d'exécution, vide tant que la cellule n'a pas tourné) et `outputs` (la liste des résultats affichés, vide pour l'instant). Exécutons maintenant le carnet avec `nbclient`, la bibliothèque qui pilote un noyau depuis un programme (c'est ce que fait le bouton « Exécuter tout ») :

```python
from nbclient import NotebookClient

NotebookClient(nb, kernel_name="python3", resources={"metadata": {"path": "."}}).execute()
cellule = nb.cells[1]
print(cellule.execution_count, cellule.outputs[0].data["text/plain"])
```
<!--sortie-->
```text
1 (400, 4)
```

La cellule porte désormais son **numéro d'exécution** (1) et sa **sortie** (le tableau compte 400 lignes et 4 colonnes), enregistrées dans le fichier lui-même. Un graphique serait stocké sous forme d'image encodée en texte : un notebook avec beaucoup de graphiques devient donc volumineux.

> 🧭 **Ce que cela implique.** Comme les résultats sont *écrits dans le fichier*, vous pouvez ouvrir un notebook et voir des résultats **sans rien exécuter**. C'est pratique pour partager… et dangereux, car **rien ne garantit que ces résultats correspondent au code affiché** (voir 6.2.3).

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : application 6.4.

### 6.2.3 Le piège : l'état caché

Dans un script Python ordinaire, l'ordre d'exécution est celui du fichier, de haut en bas, toujours. Dans un notebook, **vous choisissez l'ordre** : vous pouvez relancer la cellule 5 trois fois, sauter la cellule 3, retourner modifier la cellule 1 sans relancer les suivantes, ou même supprimer une cellule dont la variable continue d'exister en mémoire. Le noyau, lui, se souvient de tout.

Pour voir ce phénomène sans notebook, **simulons** un noyau avec Python pur : un dictionnaire `memoire` joue la mémoire du noyau, et `executer` joue le rôle de `Maj + Entrée`. Trois cellules calculent le prix d'une commande de trois articles à 50 €, TVA à 19 % comprise. Puis la gérante corrige le prix à 80 €, relance la cellule A et la cellule C… **en oubliant de relancer B**.

```python
memoire = {}
def executer(code): exec(code, memoire)          # joue « Maj + Entrée »

A, B, C = "prix = 50", "total = prix * 3 * 1.19", "print('Total TTC :', round(total, 2), '€')"
for cellule in (A, B, C): executer(cellule)      # exécution normale : 50 × 3 × 1,19 = 178,5
A = "prix = 80"
executer(A); executer(C)                         # on corrige A, on relance C, mais pas B
```
<!--sortie-->
```text
Total TTC : 178.5 €
Total TTC : 178.5 €
```

Le total affiché est **toujours 178,5 €** alors que le prix est maintenant de 80 € : la variable `total` en mémoire date de l'ancienne exécution de B. Sur l'écran, la cellule A affiche 80, la cellule C un total faux, et rien ne signale l'incohérence. Pire : un collègue qui exécute le notebook de haut en bas obtient $80\times3\times1{,}19=285{,}6$ €, un résultat **différent** de celui de la gérante. Autre variante du même piège, la **cellule supprimée** : une variable définie dans une cellule effacée « pour faire propre » continue de vivre dans le noyau, jusqu'à ce que quelqu'un d'autre ouvre le notebook et obtienne une erreur `NameError` (voir l'application 6.5 du cahier).

Ces scénarios ont un point commun : **le résultat dépendait d'un état invisible**, la mémoire du noyau, qui n'est écrit nulle part dans le fichier. C'est la première cause de notebooks non reproductibles. L'antidote est simple :

> ⚠️ **La règle du « Restart & Run All ».** Avant de partager un notebook, de le commiter ou d'en tirer un chiffre pour un rapport, faites **Noyau → Redémarrer et tout exécuter** (*Restart Kernel and Run All Cells*). Cela efface la mémoire et rejoue toutes les cellules **dans l'ordre du fichier**. Si tout passe et que les résultats ne changent pas, votre notebook est sain. S'il casse, vous venez de découvrir un état caché, et mieux vaut le découvrir maintenant que devant votre client.

> 📐 **Pourquoi cela revient à un problème d'ordre.** Un programme est reproductible si son résultat est une **fonction** de ses entrées (code + données + graine aléatoire). Dans un notebook, le résultat dépend en plus de la **suite des cellules exécutées** : une *séquence*, pas seulement un ensemble. Il existe $n!$ façons d'ordonner $n$ cellules, et le fichier n'en garde qu'une trace partielle (les numéros `[1]`, `[2]`…). Imposer l'ordre du fichier (« Run All ») ramène la dépendance à **une seule** séquence canonique : celle qu'on lit.

### 6.2.4 Repérer un notebook douteux

Les numéros d'exécution enregistrés dans le fichier permettent de repérer les notebooks douteux **sans les exécuter**. Un notebook exécuté d'un seul trait, sur un noyau neuf, affiche `[1]`, `[2]`, `[3]`… sans trou ni saut. Si les numéros sont désordonnés (3, 1, 2), si une cellule n'a jamais tourné, ou si une erreur est enregistrée, l'alarme sonne. Un tel détecteur tient en une quinzaine de lignes de Python (c'est un bon exemple de petite application des fonctions et des listes du chapitre 4 à un fichier de notebook) ; il ne *prouve* pas qu'un notebook est reproductible (la seule preuve est de le réexécuter), mais il repère les cas flagrants en une milliseconde, par exemple dans un script de vérification avant chaque commit. Vous l'écrirez dans l'application 6.5 du cahier.

### 6.2.5 Bonnes pratiques

1. **Restart & Run All avant tout partage.** Règle numéro un.
2. **Les imports et les réglages en première cellule** : bibliothèques, graine aléatoire (`rng = np.random.default_rng(42)`), chemins des fichiers. On voit d'emblée ce dont le notebook dépend.
3. **Un notebook, une question.** Un notebook de 200 cellules est ingérable ; découpez : `01-nettoyage.ipynb`, `02-exploration.ipynb`, `03-modele.ipynb`.
4. **Sortez le code réutilisable dans des fichiers `.py`** (fonctions de nettoyage, de calcul) et importez-les : `from outils import nettoyer`. Ce code se teste (4.6), se versionne proprement avec Git, et sert à d'autres notebooks.
5. **Écrivez du texte entre les cellules** : titres, hypothèses, interprétation. Le notebook est un récit, pas un brouillon.
6. **Chemins relatifs** (`donnees/commandes.csv`), jamais un chemin absolu propre à votre ordinateur : le notebook doit marcher sur une autre machine.
7. **N'utilisez pas le notebook pour la production.** Une fois l'analyse stabilisée, un script `.py` lancé depuis la ligne de commande (6.3) est plus fiable qu'un carnet qu'on clique à la main.

### 6.2.6 Notebooks et Git : le problème des sorties

Un notebook est un fichier texte : Git peut donc le suivre. Mais, comme les **sorties** et les **numéros d'exécution** sont stockés dans le fichier, la moindre ré-exécution modifie des dizaines de lignes (graphiques encodés, numéros qui changent) : les comparaisons `git diff` deviennent illisibles et les conflits de fusion cauchemardesques. La pratique courante est de **ne garder dans Git que les sources**, en effaçant les sorties avant de commiter. Effacer les sorties revient à vider la liste `outputs` et à remettre `execution_count` à vide dans chaque cellule de code : l'application 6.5 le fait en quelques lignes avec `nbformat`. Dans la pratique, on n'écrit pas ce nettoyage à la main : l'outil `nbstripout` s'installe en « crochet » Git et efface les sorties automatiquement à chaque commit. Le revers de la médaille : le fichier commité n'affiche plus de résultats ; on publie alors, à côté, une version **exportée** (voir ci-dessous).

### 6.2.7 Exporter : du notebook au rapport, au script

La bibliothèque `nbconvert` transforme un notebook en d'autres formats : **HTML** (à envoyer par e-mail), **PDF**, **Markdown**, ou **script Python** (le code seul). En ligne de commande, l'option `--execute` rejoue d'abord tout le notebook dans un noyau neuf, c'est-à-dire exactement la règle « Restart & Run All », automatisée :

```bash noexec
jupyter nbconvert --to html --execute analyse.ipynb       # page web, après avoir tout rejoué
jupyter nbconvert --to script analyse.ipynb               # le code seul, en fichier .py
jupyter nbconvert --to markdown analyse.ipynb             # document Markdown
```

(*Ces commandes supposent un fichier `analyse.ipynb` ; elles sont exécutées pour de vrai dans l'application 6.4 du cahier.*) Pour un PDF, `--to pdf` demande en plus une installation de LaTeX (6.5).

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

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.4 et 6.5, exercice 6.6.


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

Pour **copier, déplacer, renommer, supprimer**, on a de même `cp`, `mv` (qui sert aux deux usages : déplacer et renommer) et `rm`. Quelques **chemins spéciaux** sont à connaître : `.` est le dossier courant, `..` le dossier **parent**, `~` votre dossier personnel, `/` la racine de toute l'arborescence. Un chemin est **absolu** s'il part de la racine et **relatif** s'il part du dossier courant (`donnees/commandes.csv`).

> ⚠️ **`rm` n'a pas de corbeille.** Ce qui est supprimé dans le terminal est **définitivement perdu**. Ne tapez jamais `rm -r` sans relire la ligne entière, et n'écrivez jamais de commande de suppression avec un chemin que vous n'avez pas vérifié avec `ls` juste avant. Avec Git (6.1), au moins, vous pouvez toujours récupérer une version enregistrée.

> 💡 **Quatre astuces qui changent la vie.** (1) La touche **Tab** complète les noms de fichiers : tapez `cd etu` puis Tab. (2) La flèche **↑** rappelle les commandes précédentes ; `Ctrl + R` cherche dans l'historique. (3) **Ctrl + C** interrompt une commande qui tourne. (4) `commande --help` (ou `man commande`) affiche la documentation de n'importe quelle commande.

Voici l'arborescence d'un projet d'analyse bien rangé, créée d'un coup. La syntaxe `{a,b,c}` est une **expansion d'accolades** : une seule ligne `mkdir` crée les quatre dossiers.

```bash
cd ~/atelier
mkdir -p etude-ventes/{donnees,notebooks,src,rapports}
cp boutique/commandes.csv etude-ventes/donnees/
cd etude-ventes
find . -not -name '.' | sort
```
<!--sortie-->
```text
./donnees
./donnees/commandes.csv
./notebooks
./rapports
./src
```

Chaque dossier a un rôle : les données brutes ne se modifient jamais, les notebooks explorent, `src` contient le code réutilisable, `rapports` reçoit les résultats.

### 6.3.2 Regarder le contenu d'un fichier

Un fichier CSV est un fichier **texte** : on peut le lire dans le terminal sans l'ouvrir dans un tableur. C'est très pratique pour vérifier rapidement un fichier de plusieurs millions de lignes que Excel ne saurait pas ouvrir.

```bash
cd donnees
head -n 3 commandes.csv
tail -n 2 commandes.csv
wc -l commandes.csv
```
<!--sortie-->
```text
canal,montant,livraison,satisfaction
Boutique,44.8,0,4
Site,34.5,2,4
Réseaux,37.5,3,4
Site,31.4,4,4
401 commandes.csv
```

`head -n 3` affiche les 3 premières lignes, `tail -n 2` les 2 dernières, `wc -l` compte les lignes : le CSV a une ligne d'en-tête (les noms de colonnes) puis une commande par ligne, soit 401 lignes pour 400 commandes. Pour parcourir un long fichier page par page, il existe `less` (on avance avec la barre d'espace, on quitte avec `q`) ; `cat fichier` affiche tout le fichier d'un coup.

### 6.3.3 Interroger des données avec des outils de texte

Il existe quelques outils très anciens, très rapides, et parfaitement adaptés aux fichiers de données en colonnes. Chaque outil fait **une chose** :

| Outil | Rôle |
|---|---|
| `grep motif` | garder les lignes qui contiennent le motif |
| `cut -d, -f2` | extraire la colonne n°2 (séparateur `,`) |
| `sort` | trier (`-n` : numérique, `-r` : décroissant, `-t,` : séparateur, `-k2` : colonne) |
| `uniq -c` | compter les lignes identiques **consécutives** (d'où le `sort` avant) |
| `awk` | mini-langage pour calculer sur les colonnes |

Combien de commandes viennent du canal « Réseaux » ? Et combien par canal ? Pour la seconde question, il faut extraire la colonne des canaux (sans l'en-tête), la trier pour regrouper les valeurs identiques, puis compter :

```bash
grep -c Réseaux commandes.csv
tail -n +2 commandes.csv | cut -d, -f1 | sort | uniq -c | sort -rn
```
<!--sortie-->
```text
138
    148 Site
    138 Réseaux
    114 Boutique
```

La seconde ligne est un **pipeline** (« tuyau ») : `tail -n +2` supprime l'en-tête (« commence à la ligne 2 »), `cut -d, -f1` garde la première colonne, `sort` regroupe les canaux, `uniq -c` compte chaque groupe, et `sort -rn` classe du plus fréquent au plus rare. Le symbole `|` (« pipe ») envoie la sortie d'une commande à l'entrée de la suivante. Le site est le premier canal en nombre de commandes, devant les réseaux et la boutique. Pour calculer, par exemple un montant moyen, on utilise `awk` : il lit le fichier ligne par ligne, `$2` désigne la 2ᵉ colonne, `NR` le numéro de ligne.

```bash
awk -F, 'NR > 1 { somme += $2; n++ } END { printf "montant moyen : %.2f € sur %d commandes\n", somme/n, n }' commandes.csv
```
<!--sortie-->
```text
montant moyen : 60.25 € sur 400 commandes
```

L'option `-F,` fixe le séparateur. Pour chaque ligne sauf l'en-tête (`NR > 1`), on ajoute le montant à une somme et on compte ; à la fin (`END`) on affiche la moyenne : on retrouve bien les 60,25 € du chapitre 3.

> 🧭 **Quand utiliser quoi ?** Ces commandes brillent pour un **coup d'œil rapide**, pour traiter des fichiers trop gros pour la mémoire, ou pour assembler une chaîne de traitement dans un script. Dès que l'analyse devient subtile (jointures, valeurs manquantes, statistiques), on passe à pandas (4.4). Les deux approches sont complémentaires.

### 6.3.4 Pipes et redirections : assembler de petits outils

Toutes ces commandes obéissent à la même philosophie, dite « **philosophie Unix** » : *chaque programme fait une seule chose, la fait bien, et lit/écrit du texte*. Ainsi tous les programmes se branchent les uns sur les autres, comme des briques de LEGO. Il y a trois flux : l'**entrée standard** (clavier ou tuyau), la **sortie standard** (écran) et la **sortie d'erreur** (écran aussi, mais distincte). Les opérateurs de redirection vers ou depuis des fichiers :

| Opérateur | Effet | Exemple |
|---|---|---|
| `>` | écrire la sortie dans un fichier (**écrase** l'existant) | `ls > liste.txt` |
| `>>` | **ajouter** la sortie à la fin du fichier | `echo "fin" >> liste.txt` |
| `<` | lire l'entrée depuis un fichier | `sort < liste.txt` |
| `2>` | rediriger les **messages d'erreur** | `ls absent 2> erreurs.txt` |

Sauvegardons un résumé des ventes dans un fichier, puis provoquons une erreur pour voir le **code de sortie** :

```bash
cd ..
tail -n +2 donnees/commandes.csv | cut -d, -f1 | sort | uniq -c > rapports/commandes-par-canal.txt
cat rapports/commandes-par-canal.txt
ls donnees/inexistant.csv 2> rapports/erreurs.txt
echo "code de sortie : $?"
```
<!--sortie-->
```text
    114 Boutique
    138 Réseaux
    148 Site
code de sortie : 2
```

La variable spéciale `$?` contient le **code de sortie** de la dernière commande : **0 signifie « tout s'est bien passé »**, toute autre valeur signale une erreur (ici, `ls` a échoué : le message est allé dans `erreurs.txt` au lieu de s'afficher). Les scripts s'appuient sur ces codes pour enchaîner des étapes : `commande1 && commande2` lance la seconde **seulement si** la première a réussi ; `commande1 || commande2` la lance seulement si la première a échoué.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : application 6.6, exercices 6.1, 6.2 et 6.4.

### 6.3.5 Lancer des programmes Python depuis le terminal

Le plus utile est de pouvoir **lancer ses propres scripts Python**, avec des paramètres. Les arguments tapés après le nom du script sont disponibles en Python dans la liste `sys.argv` (le premier élément, `sys.argv[0]`, est le nom du script lui-même). Voici un petit outil qui résume un fichier CSV donné en argument :

```bash
cat > src/resume.py <<'FIN'
import sys
import pandas as pd

df = pd.read_csv(sys.argv[1])
print(f"{len(df)} lignes, {df.shape[1]} colonnes")
print(df.describe().loc[["mean", "max"]].round(2))
FIN
python src/resume.py donnees/commandes.csv
```
<!--sortie-->
```text
400 lignes, 4 colonnes
      montant  livraison  satisfaction
mean    60.25       3.29          3.96
max    255.70      13.00          5.00
```

Un bon outil respecte la convention des codes de sortie : **0** quand tout va bien, un code non nul (avec un message clair) pour un fichier absent ou un mauvais usage. En Python, on le fait avec `sys.exit(code)`. L'application 6.7 du cahier ajoute cette gestion d'erreurs à notre outil. Deux variantes utiles de `python` : `python -c "print(2+3)"` exécute une ligne, `python -m module` exécute un module de la bibliothèque (par exemple `python -m venv`, juste après).

### 6.3.6 Le problème des bibliothèques : les environnements virtuels

Voici un scénario qui arrive à tout le monde. En janvier, la gérante installe `pandas` pour son analyse. En juin, elle commence un autre projet qui nécessite une **ancienne** version de la même bibliothèque. Si tout est installé au même endroit, mettre à jour casse l'ancien projet, et rétrograder casse le nouveau. Pire : quand elle envoie son code à un collègue, comment sait-il quelles versions utiliser ? D'où l'**environnement virtuel** :

> 💡 **Définition.** Un environnement virtuel est un **dossier isolé** contenant une copie de l'interpréteur Python et ses propres bibliothèques. Chaque projet a le sien : les bibliothèques de l'un n'affectent jamais celles de l'autre. L'environnement se **crée**, s'**active**, puis on y installe ce dont le projet a besoin avec **pip**, le gestionnaire de paquets de Python.

Voici le cycle complet. Pour ne pas télécharger des centaines de mégaoctets dans cet exemple, nous installons une toute petite bibliothèque, `tabulate` (qui formate joliment des tableaux en texte), à la place de `pandas`.

```bash
python -m venv .venv
source .venv/bin/activate
pip install --quiet tabulate 2>&1 | grep -v -i -E "notice|warning"
pip freeze > requirements.txt
cat requirements.txt
deactivate
```
<!--sortie-->
```text
tabulate==0.10.0
```

`python -m venv .venv` crée l'environnement dans un dossier caché nommé `.venv`. `source .venv/bin/activate` l'**active** : dès cet instant, `python` et `pip` désignent ceux du dossier `.venv` (sous Windows, la commande d'activation est `.venv\Scripts\activate`). `pip install` installe la bibliothèque **dans `.venv` uniquement**, et `pip freeze` liste tout ce qui est installé avec les **numéros de version exacts**. Ce dernier point est la clé de la reproductibilité : on enregistre cette liste dans un fichier, traditionnellement nommé `requirements.txt`, que l'on versionne avec Git (6.1). Quelqu'un qui reçoit le projet reconstruit **le même environnement** en trois commandes : créer un environnement neuf, l'activer, puis `pip install -r requirements.txt`. Le dossier `.venv` lui-même ne se partage pas (il est propre à la machine et volumineux) : il figure dans le `.gitignore` de 6.1, et seul `requirements.txt` voyage avec le projet.

> ⚠️ **`requirements.txt` fige les bibliothèques, pas Python lui-même.** Mentionnez aussi la version de Python dans le `README` (« testé avec Python 3.13 »). Pour des besoins plus avancés, il existe des outils qui gèrent aussi la version de Python : `conda` (très répandu en data science, notamment sous Windows), `uv` (récent et très rapide), ou Poetry. Ils répondent au même besoin : isoler, figer, reproduire.

Pour le livre complet, l'installation recommandée dans l'avant-propos serait donc (*non exécutée ici : elle télécharge environ 200 Mo de bibliothèques*) :

```bash noexec
python -m venv .venv
source .venv/bin/activate        # sous Windows : .venv\Scripts\activate
pip install numpy pandas scipy matplotlib seaborn
pip freeze > requirements.txt
```

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : application 6.9, exercice 6.7.

### 6.3.7 Variables d'environnement et `PATH`

Le terminal garde en mémoire des **variables** (texte nommé), que l'on affiche avec `$` : c'est ainsi que nous avons utilisé `$?` et `$HOME`. On en crée avec `NOM=valeur` (sans espaces autour du `=`) ; `export` les rend visibles aux programmes lancés ensuite.

```bash
export TAUX_TVA=0.19
python -c "import os; print('TVA lue depuis Python :', float(os.environ['TAUX_TVA']))"
```
<!--sortie-->
```text
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

Quand on retape trois fois la même suite de commandes, on la range dans un **script shell** : un fichier texte contenant des commandes, exécuté d'un coup. Notre premier script affiche, pour un fichier de commandes, le nombre de commandes par canal. Il introduit les ingrédients de base : **arguments** (`$1` est le premier argument, `$#` leur nombre), **variables**, **test** (`if`), **boucle** (`for`) et **substitution de commande** (`$( … )` insère le résultat d'une commande dans une autre).

```bash
mkdir -p scripts
cat > scripts/rapport.sh <<'FIN'
#!/usr/bin/env bash
set -euo pipefail
[ "$#" -eq 1 ] || { echo "usage : $0 fichier.csv" >&2; exit 2; }
total=$(( $(wc -l < "$1") - 1 ))
echo "== $total commandes dans $1 =="
for canal in Boutique Réseaux Site; do
    echo "  $canal : $(grep -c "^$canal," "$1")"
done
FIN
bash scripts/rapport.sh donnees/commandes.csv
```
<!--sortie-->
```text
== 400 commandes dans donnees/commandes.csv ==
  Boutique : 114
  Réseaux : 138
  Site : 148
```

Passons ce fichier en revue :

- La première ligne, `#!/usr/bin/env bash`, s'appelle le **shebang** : elle indique avec quel programme exécuter le fichier. Les lignes qui commencent par `#` sont des **commentaires**.
- `set -euo pipefail` est une **ceinture de sécurité** que l'on met en tête de tout script sérieux : `-e` arrête le script à la première commande qui échoue, `-u` refuse d'utiliser une variable jamais définie (souvent une faute de frappe), `-o pipefail` fait échouer un pipeline si l'une de ses commandes échoue (et pas seulement la dernière).
- La ligne `[ "$#" -eq 1 ] || { … }` vérifie qu'on a reçu exactement un argument ; sinon elle affiche un mode d'emploi **sur la sortie d'erreur** (`>&2`) et quitte avec le code 2.
- `total=$(( $(wc -l < "$1") - 1 ))` calcule le nombre de lignes moins l'en-tête (la double parenthèse `$(( … ))` fait de l'arithmétique entière).
- La boucle `for` passe en revue chaque canal ; `grep -c "^$canal,"` compte les lignes **commençant** par le nom du canal suivi d'une virgule.

Un script peut aussi être rendu directement exécutable (`chmod +x scripts/rapport.sh`, puis `./scripts/rapport.sh`), appliquer un traitement à **chaque fichier** d'un groupe avec une boucle (le joker `*` désigne tous les fichiers d'un motif, comme `donnees/*.csv`), et s'enchaîner avec d'autres scripts dans un petit **pipeline**.

### 6.4.2 Enchaîner des étapes : échouer bruyamment

Un vrai projet d'analyse est une **chaîne d'étapes** : vérifier les données, calculer, produire le rapport. Le point crucial est ce qui se passe quand une étape échoue. Avec `set -e`, le script **s'arrête net** à la première étape défaillante et renvoie un code d'erreur : on sait immédiatement que quelque chose ne va pas. Sans cette ceinture, il continue comme si de rien n'était, annonce « terminé » et renvoie le code 0 (succès !) alors que **rien n'a été calculé** : le pire des scénarios, car personne ne se doute que le rapport est vide ou partiel. D'où la règle : **un script qui échoue doit échouer bruyamment**. L'application 6.8 du cahier met les deux comportements côte à côte.

> ⚠️ **Les limites du shell.** Le shell est parfait pour **enchaîner des programmes**, manipuler des fichiers et des dossiers. Mais dès qu'il faut des calculs, des structures de données ou de la logique non triviale, passez à Python : ses 300 lignes seront plus lisibles et plus testables que 300 lignes de shell. Règle pratique : si le script dépasse une cinquantaine de lignes ou nécessite des tableaux, c'est un script Python.

### 6.4.3 Faire tourner un script tout seul : `cron`

Sous Linux et macOS, le programme **cron** exécute des commandes à heure fixe. On le configure en ajoutant des lignes à la **table cron** (`crontab -e`). Une ligne comporte cinq champs de temps (minute, heure, jour du mois, mois, jour de la semaine) suivis de la commande. Par exemple, pour lancer notre script tous les jours à 7 h du matin :

```bash noexec
# minute heure jour mois jour-semaine   commande
0 7 * * *  cd ~/etude-ventes && bash scripts/rapport.sh donnees/commandes.csv
```

(*Non exécuté : la table cron appartient à l'utilisateur de la machine, et le résultat ne se verrait qu'à 7 h.*) Le `*` signifie « toutes les valeurs ». Sous Windows, l'équivalent est le *Planificateur de tâches*. Dans le cloud, on utilise des services d'orchestration plus riches (comme Airflow), que vous rencontrerez dans les volumes suivants de la série.

### 6.4.4 Isoler plus finement : plusieurs versions d'une même bibliothèque

Au 6.3.6, nous avons dit que des projets distincts peuvent avoir besoin de **versions différentes** d'une même bibliothèque : deux environnements virtuels coexistent sans se gêner, chacun avec **sa** version, exigée avec `==` dans la commande d'installation (l'application 6.9 du cahier le démontre). Dans un fichier `requirements.txt`, les **numéros de version** peuvent s'écrire avec plus ou moins de rigueur :

| Écriture | Signification |
|---|---|
| `pandas==3.0.0` | exactement cette version (reproductibilité maximale) |
| `pandas>=3.0,<4` | n'importe quelle version 3.x, à partir de la 3.0 |
| `pandas` | n'importe quelle version (déconseillé : le résultat change avec le temps) |

La bonne pratique à retenir : **`==` pour reproduire un résultat** (rapport remis à un client, article), **fourchette** pour une bibliothèque en développement qui doit rester compatible avec d'autres. Deux outils alternatifs que vous croiserez (*non exécutés ici : non installés*) :

```bash noexec
conda create --name etude-ventes python=3.13 pandas   # conda installe aussi Python lui-même
uv venv && uv pip install -r requirements.txt         # uv : un installateur très rapide, compatible avec pip
```

### 6.4.5 Docker : emballer le projet avec son système

Un environnement virtuel isole les **bibliothèques Python**. Mais votre analyse peut dépendre d'autre chose : une version précise de Python, une bibliothèque système, un outil comme R, une configuration. « Chez moi, ça marche ! » reste possible. **Docker** résout ce problème en emballant le projet avec **tout son système d'exploitation de base**, dans une sorte de mini-ordinateur virtuel appelé **conteneur**.

> 💡 **Une analogie.** Un environnement virtuel, c'est une **étagère personnelle** dans une cuisine partagée : vos ingrédients sont à vous, mais la cuisine (le système) est celle de tout le monde. Docker, c'est un **repas livré dans une boîte hermétique** : la boîte contient les aliments, les couverts et même la table. Où qu'on ouvre la boîte, le repas est identique.

Trois mots à retenir :

- Une **image** est le **modèle** figé : le système de base, Python, vos bibliothèques, votre code. On la construit une fois à partir d'une **recette** (le `Dockerfile`).
- Un **conteneur** est une **instance en marche** d'une image. On peut en lancer dix à partir de la même image.
- Un **registre** (comme *Docker Hub*) est un entrepôt d'images, un peu comme GitHub pour le code : on y trouve des images prêtes à l'emploi (`python`, `postgres`, `jupyter`…).

Voici le `Dockerfile` d'un projet d'analyse comme le nôtre :

```dockerfile
# une image Python toute prête
FROM python:3.13-slim
# le dossier de travail dans le conteneur
WORKDIR /app
# la liste des bibliothèques, installées pendant la construction
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# puis le reste du projet
COPY . .
# la commande lancée au démarrage du conteneur
CMD ["python", "src/resume.py", "donnees/commandes.csv"]
```

`FROM` choisit la base, `WORKDIR` fixe le dossier, `COPY` copie des fichiers de votre machine vers l'image, `RUN` exécute une commande **pendant la construction**, `CMD` définit ce que fera le conteneur **au démarrage**. L'ordre des lignes n'est pas anodin : Docker garde en cache chaque étape, et la copie de `requirements.txt` **avant** celle du code permet de ne pas réinstaller les bibliothèques à chaque modification d'un script. On construit puis on lance :

```bash noexec
docker build -t etude-ventes .          # construit l'image à partir du Dockerfile
docker run --rm etude-ventes            # lance un conteneur, le supprime à la fin
docker run --rm -v "$PWD/rapports:/app/rapports" etude-ventes   # partage le dossier rapports/
```

La troisième commande montre un point essentiel : un conteneur est **éphémère**, ce qu'il écrit disparaît avec lui. Pour récupérer des résultats, on **monte** un dossier de votre machine dans le conteneur (option `-v`).

> ⚠️ **Non exécuté, honnêtement.** Docker n'est pas disponible dans l'environnement où ce livre a été rédigé. Vérifions-le plutôt que de le supposer :

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

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.8 et 6.9, exercices 6.7 et 6.8.


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
| **Données** | Ai-je gardé les données brutes intactes ? Sont-elles identifiables ? | dossier `donnees/` en lecture seule, empreinte `sha256` (6.5.8) |
| **Code** | Est-il versionné ? Retrouve-t-on la version qui a produit le résultat ? | Git (6.1) |
| **Aléa** | Mes simulations donnent-elles les mêmes nombres à chaque fois ? | graines aléatoires (6.5.2) |
| **Environnement** | Quelles versions de Python et des bibliothèques ? | `requirements.txt` (6.3), relevé de versions (6.5.3) |
| **Exécution** | Les étapes s'enchaînent-elles sans intervention manuelle ? | scripts, `Makefile` (6.4, 6.5.5) |
| **Rapport** | Les chiffres du texte viennent-ils *directement* du code ? | documents dynamiques (6.5.4) |

### 6.5.2 L'aléa maîtrisé : les graines

Beaucoup d'analyses font appel au hasard : échantillonnage, simulation, validation croisée, bootstrap (3.7), initialisation de modèles. Or un ordinateur ne tire pas vraiment au hasard : il calcule une suite de nombres qui **a l'air** aléatoire à partir d'un point de départ, la **graine** (*seed*). Même graine, même suite. Sans graine explicite, Python en choisit une différente à chaque exécution (à partir de l'horloge, par exemple), et les résultats changent. Voici la moyenne d'un échantillon de 10 commandes tiré au hasard, avec et sans graine :

```python
import numpy as np
import pandas as pd

montants = pd.read_csv("donnees/commandes.csv")["montant"].to_numpy()
def moyenne(rng, taille=10):
    return montants[rng.choice(len(montants), size=taille, replace=False)].mean()

print("graine 42, deux fois :", round(moyenne(np.random.default_rng(42)), 2), round(moyenne(np.random.default_rng(42)), 2))
print("sans graine, deux fois identiques ?", moyenne(np.random.default_rng()) == moyenne(np.random.default_rng()))
```
<!--sortie-->
```text
graine 42, deux fois : 46.55 46.55
sans graine, deux fois identiques ? False
```

Avec la même graine 42, on obtient **exactement** le même nombre à chaque fois, sur n'importe quel ordinateur (pour la même version de NumPy) ; sans graine, les deux tirages diffèrent. C'est ce qui rend les nombres du livre reproductibles.

Reste à savoir **quelle graine choisir**. La réponse est contre-intuitive : *n'importe laquelle*, mais **sans la choisir en regardant le résultat**. Changer de graine jusqu'à obtenir le résultat qui nous arrange est une forme de triche appelée *p-hacking* (voir 3.5). La graine sert à **figer** une exécution, pas à l'améliorer. Pour vérifier qu'un résultat n'est pas un accident de graine, on l'observe pour **plusieurs graines** :


Pour les graines 1 à 8, les moyennes d'échantillons de 10 commandes vont de 43,3 € à 73,3 €, alors que la vraie moyenne de la population est de 60,25 € : elles varient fortement d'une graine à l'autre (voir l'erreur-type, 3.2). La graine 42 n'a donc rien de spécial, et une conclusion qui ne tiendrait que pour elle serait suspecte. Deux règles pratiques : **(1)** créer **un seul** générateur `rng = np.random.default_rng(graine)` en début de programme, et le passer aux fonctions qui en ont besoin, plutôt que de multiplier les graines cachées ; **(2)** se souvenir que chaque bibliothèque a sa propre source d'aléa (`random` de Python, NumPy, et plus tard PyTorch ou scikit-learn avec leur paramètre `random_state`) : il faut fixer **chacune** de celles qu'on utilise.

> ⚠️ **Une graine ne garantit pas l'identité entre versions.** Les mêmes graine et code peuvent donner des tirages différents si la **version** de NumPy change (les algorithmes évoluent). D'où la nécessité de noter aussi les versions, juste après.

### 6.5.3 Relever l'environnement

Le fichier `requirements.txt` (6.3) fige les bibliothèques à *installer*. On peut aussi, en fin de rapport, **imprimer ce qui a réellement servi**. Cela prend deux lignes et sauve bien des enquêtes (en R, la fonction `sessionInfo()` joue ce rôle) :

```python
import sys, importlib.metadata as meta
print("Python", sys.version.split()[0], "| numpy", meta.version("numpy"), "| pandas", meta.version("pandas"))
```
<!--sortie-->
```text
Python 3.13.3 | numpy 2.5.3 | pandas 3.0.6
```

La sortie est le **relevé des versions** de cette exécution : on l'ajoute au bas de chaque rapport.

### 6.5.4 Un rapport qui se fabrique tout seul

Le défaut le plus courant d'un rapport : on calcule un chiffre dans un notebook, on le **recopie à la main** dans un document, et trois semaines plus tard on met à jour les données sans mettre à jour le texte. Le remède s'appelle le **document dynamique** (*literate programming*, « programmation lettrée ») : le texte et les chiffres sont produits **par le même programme**, donc ils ne peuvent pas diverger. Nous construisons cette chaîne avec ce que nous avons déjà :

```text
 donnees/commandes.csv ──► src/faire_rapport.py ──► rapport.md ──► pandoc ──► HTML, PDF
        (données)             (code : calcule et          (texte et chiffres      (mise en forme)
                               écrit le texte)             cohérents)
```

Première étape : un programme Python qui **écrit** un document Markdown en y insérant les chiffres calculés. Le Markdown est le format qui sert à écrire ce livre.

```bash
cat > src/faire_rapport.py <<'FIN'
import sys
import pandas as pd

df = pd.read_csv(sys.argv[1])
m = df["montant"]
print('---\ntitle: "Les ventes de la boutique"\nlang: fr\n---\n')
print(f"Le fichier contient **{len(df)} commandes** ; le montant moyen est de "
      f"**{m.mean():.2f} €**, la médiane de **{m.median():.2f} €**.")
for canal, g in df.groupby("canal"):
    print(f"- {canal} : {len(g)} commandes, panier moyen {g['montant'].mean():.2f} €")
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

Le fichier contient **400 commandes** ; le montant moyen est de **60.25 €**, la médiane de **51.00 €**.
- Boutique : 114 commandes, panier moyen 74.81 €
- Réseaux : 138 commandes, panier moyen 49.01 €
- Site : 148 commandes, panier moyen 59.50 €
```

Le programme n'écrit **aucun chiffre en dur** : le nombre de commandes, les moyennes et le détail par canal sont calculés. Si les données changent demain, il suffit de relancer. Le résultat est un fichier Markdown propre ; **Pandoc**, le « couteau suisse » de la conversion de documents, le transforme en page web, en PDF ou en document Word :

```bash
pandoc --standalone rapports/rapport-ventes.md -o rapports/rapport-ventes.html
ls rapports
```
<!--sortie-->
```text
commandes-par-canal.txt
erreurs.txt
rapport-ventes.html
rapport-ventes.md
```

L'application 6.10 du cahier ajoute à ce rapport un intervalle de confiance, une formule, un tableau et un PDF. Retenez le principe : **pas de date du jour ni de valeur aléatoire non figée dans un rapport reproductible**, sinon deux exécutions ne produisent plus le même fichier.

### 6.5.5 `make` : ne refaire que ce qui a changé

Tant que la chaîne tient en deux commandes, on les retape. Mais un vrai projet compte des dizaines d'étapes : nettoyage, tableaux, graphiques, rapport. Relancer **tout** à chaque modification est lent ; relancer **à la main** les bonnes étapes est source d'oublis. L'outil **`make`** (né en 1976, toujours en pleine forme) résout les deux problèmes. On lui décrit dans un fichier nommé `Makefile` des **règles** : une cible, ses dépendances, et la commande qui fabrique la cible à partir d'elles. `make` compare les **dates de modification** : si une dépendance est plus récente que la cible, il **refait** la cible ; sinon il ne fait rien. Voici le `Makefile` de notre projet (attention : l'indentation des commandes **doit être une vraie tabulation**, pas des espaces) :

```makefile
rapports/rapport-ventes.html: rapports/rapport-ventes.md
	pandoc --standalone rapports/rapport-ventes.md -o $@

rapports/rapport-ventes.md: donnees/commandes.csv src/faire_rapport.py
	python src/faire_rapport.py donnees/commandes.csv > $@
```

Lisons-le de haut en bas. Le rapport HTML dépend du fichier Markdown ; le fichier Markdown dépend des **données** et du **programme** qui le fabrique. Dans les commandes, `$@` désigne la cible. Supprimons les fichiers produits, puis lançons `make` deux fois, et enfin « touchons » le fichier de données (ce qui met à jour sa date) :


```bash
make
make
touch donnees/commandes.csv
make
```
<!--sortie-->
```text
python src/faire_rapport.py donnees/commandes.csv > rapports/rapport-ventes.md
pandoc --standalone rapports/rapport-ventes.md -o rapports/rapport-ventes.html
make: 'rapports/rapport-ventes.html' is up to date.
python src/faire_rapport.py donnees/commandes.csv > rapports/rapport-ventes.md
pandoc --standalone rapports/rapport-ventes.md -o rapports/rapport-ventes.html
```

**`make` affiche chaque commande qu'il lance** : le premier appel refait les **deux** étapes, le deuxième répond qu'il n'y a **rien à faire**, et, quand on « touche » le fichier de données, les **deux** étapes sont de nouveau déclenchées.

> 💡 **Le grand intérêt.** Il suffit de modifier le texte du rapport, et seule la conversion se refait. Dans un grand projet, c'est un gain de temps considérable, et, surtout, **la documentation de la chaîne de traitement** est le `Makefile` lui-même : un lecteur voit d'un coup d'œil de quoi dépend quoi. Le `README` du projet peut alors se résumer à : « Pour tout reproduire : `make` ».

### 6.5.6 Les outils « tout-en-un » : R Markdown et Quarto

Notre chaîne maison (Python qui écrit du Markdown, puis Pandoc) fonctionne, mais le monde de la data science a standardisé la même idée dans des outils dédiés : un **seul fichier** mélange texte Markdown et **blocs de code** ; à la compilation, le code est exécuté et **ses résultats sont insérés** dans le document final (HTML, PDF, Word, diaporama).

**R Markdown** (pour R, mais aussi Python) fonctionne ainsi : le fichier `.Rmd` contient un en-tête, du texte, des blocs de code `{r}` et du code R **en ligne** dans le texte (une expression entre accents graves, précédée de `r`). La moyenne écrite dans une phrase est alors **calculée** à la compilation, jamais recopiée. L'application 6.11 du cahier compile un vrai document R Markdown.

**Quarto** est le successeur de R Markdown : même idée, mais indépendant du langage (Python, R, Julia), avec davantage de formats (sites, livres, présentations). Un fichier `.qmd` ressemble à ceci :

~~~markdown
---
title: "Les ventes de la boutique"
format: html
---

Le montant moyen est de `{python} round(moyenne, 2)` €.

```{python}
import pandas as pd
df = pd.read_csv("donnees/commandes.csv")
moyenne = df["montant"].mean()
```
~~~

```bash noexec
quarto render rapport.qmd              # produit rapport.html
quarto render rapport.qmd --to pdf     # produit un PDF (via LaTeX)
```

> ⚠️ **Non exécuté.** Quarto n'est pas installé dans l'environnement de rédaction : l'exemple `.qmd` et les deux commandes ci-dessus sont donnés **à titre d'illustration, sans avoir été testés ici**. (R Markdown, lui, est exécuté dans le cahier.) La syntaxe exacte, notamment celle du code en ligne `{python}`, peut dépendre de la version de Quarto : consultez sa documentation si vous l'installez.

### 6.5.7 LaTeX : composer proprement les formules et les PDF

**LaTeX** (on prononce « latèk ») est le langage de composition de documents scientifiques : c'est lui qui met en forme les formules des chapitres 1 à 3 de ce livre. Vous l'avez déjà écrit sans le savoir : `$\bar{x}$`, `\sum`, `\frac{a}{b}` sont des commandes LaTeX. Un document complet se compose d'un **préambule** (les réglages) et d'un **corps** :

```latex
\documentclass{article}
\usepackage{amsmath}
\begin{document}
Intervalle de confiance à 95\,\% de la moyenne :
\[ \bar{x} \;\pm\; 1{,}96\,\frac{s}{\sqrt{n}} . \]
\end{document}
```

Un compilateur (`xelatex`, installé avec ce livre) transforme ce fichier en PDF ; l'application 6.11 du cahier le fait pour de vrai. En pratique, vous n'écrirez presque jamais du LaTeX *complet* : vous le laisserez Pandoc ou Quarto générer à partir du Markdown, et vous n'écrirez à la main que les formules. Pour écrire à plusieurs un document LaTeX sans rien installer, le service en ligne **Overleaf** est très utilisé (non testé ici).

### 6.5.8 Garder une empreinte des données

Dernier maillon de la chaîne : s'assurer que les **données** n'ont pas changé en cachette. Une **empreinte cryptographique** (*hash*) est un court texte, calculé à partir du contenu d'un fichier : le moindre changement du fichier (même un seul chiffre) change complètement l'empreinte. C'est le principe que nous avons vu au 6.1.4 pour les objets de Git. On calcule celle de `commandes.csv`, on la **note dans le `README`**, et n'importe qui peut vérifier. Ici, une faute de frappe glisse dans le fichier (le premier montant, 44,8, devient 448,0) :

```bash
sha256sum donnees/commandes.csv > donnees/EMPREINTES.sha256
sha256sum -c donnees/EMPREINTES.sha256
sed -i '2s/44.8/448.0/' donnees/commandes.csv
sha256sum -c donnees/EMPREINTES.sha256 || echo "ALERTE : les données ont été modifiées"
```
<!--sortie-->
```text
donnees/commandes.csv: OK
donnees/commandes.csv: FAILED
sha256sum: WARNING: 1 computed checksum did NOT match
ALERTE : les données ont été modifiées
```


La première vérification répond `OK` ; après la modification d'un seul nombre, elle échoue : l'alerte sonne avant même qu'on lance l'analyse.

> 🧭 **Le « kit de reproductibilité » d'un projet, en une page.** Un dossier de projet bien tenu contient : un `README` (but, comment reproduire, version de Python), un fichier `requirements.txt`, les données brutes **non modifiées** avec leur empreinte, le code versionné avec Git, un `Makefile` (ou un script) qui enchaîne les étapes, et le rapport généré. Pour archiver une version définitive de manière pérenne, on dépose le tout sur un service qui attribue un identifiant stable (*DOI*), comme **Zenodo** (non testé ici).

> ✅ **À retenir**
> - **Reproductible** = mêmes données + même code + même environnement ⟹ mêmes résultats. **Répliquable** = mêmes conclusions sur de nouvelles données.
> - **Graine aléatoire** : fixer *une* graine par exécution, la choisir *avant* de voir les résultats, et vérifier sur plusieurs graines que la conclusion tient. Noter aussi les versions des bibliothèques.
> - **Document dynamique** : le texte et les chiffres sortent du **même** programme (Python + Pandoc, R Markdown, Quarto) ; on ne recopie jamais un chiffre à la main.
> - **`make`** ne refait que ce qui est périmé ; le `Makefile` documente la chaîne de traitement.
> - **LaTeX** compose les formules et les PDF ; on le fait généralement générer par Pandoc ou Quarto.
> - Une **empreinte** (`sha256sum`) détecte toute modification des données.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.10 et 6.11, exercices 6.9 et 6.10.


## Bilan du chapitre 6

Vous savez maintenant :

- **versionner** votre travail avec Git : photographier (`add`, `commit`), comparer (`diff`), défaire (`restore`, `revert`), travailler en parallèle (branches, fusions, conflits) et partager (dépôts distants) ;
- **utiliser un notebook** pour explorer et raconter, **sans tomber dans le piège de l'état caché** (Restart & Run All, détecteur d'ordre, ne pas versionner les sorties) ;
- **vous servir du terminal** : vous repérer, lire, filtrer et résumer des fichiers avec `grep`, `cut`, `sort`, `uniq` et `awk`, assembler des commandes avec les tuyaux et les redirections, comprendre les codes de sortie ;
- **isoler chaque projet** dans un environnement virtuel et **figer** ses dépendances dans `requirements.txt` ;
- (en option) **automatiser** avec des scripts shell et `make`, comprendre Docker, fabriquer un **rapport dynamique** (Python + Pandoc, R Markdown, Quarto, LaTeX), maîtriser les graines aléatoires et surveiller l'intégrité des données avec une empreinte.

Le fil rouge de tout le chapitre tient en une phrase : **un résultat n'existe que s'il peut être refait**. Vous disposez désormais de l'ensemble des fondations du volume : les mathématiques (chapitre 1), les probabilités (2), la statistique (3), la programmation (4), les bases de données (5) et les outils de travail (6). Il est temps de tout assembler dans le **projet du volume** (au cahier) : une étude complète des ventes de la boutique, des données brutes jusqu'au rapport.

> 📒 **Pour s'entraîner.** Le cahier (chapitre 6) rassemble les onze applications guidées et les dix exercices corrigés de ce chapitre.
