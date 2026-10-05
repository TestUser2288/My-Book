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
