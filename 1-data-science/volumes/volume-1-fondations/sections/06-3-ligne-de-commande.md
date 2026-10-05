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

La gérante organise enfin son travail. Voici l'arborescence d'un projet d'analyse bien rangé, créée d'un coup :

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
Réseaux,88.2,5,4
Réseaux,30.1,4,4
...
Site,62.6,4,3
Réseaux,37.5,3,4
Site,31.4,4,4
401 commandes.csv
```

`head -n 5` affiche les 5 premières lignes, `tail -n 3` les 3 dernières, `wc -l` compte les lignes. Le CSV a une ligne d'en-tête (les noms de colonnes) puis une commande par ligne : on retrouve bien 401 lignes. Pour parcourir un long fichier page par page, il existe `less` (on avance avec la barre d'espace, on quitte avec `q`) ; il est interactif, donc nous ne pouvons pas l'illustrer ici. `cat fichier` affiche tout le fichier d'un coup.

### 6.3.3 Interroger des données avec des outils de texte

Il existe quelques outils très anciens, très rapides, et parfaitement adaptés aux fichiers de données en colonnes. Les voici, appliqués au fichier de la boutique. Chaque outil fait **une chose** :

| Outil | Rôle |
|---|---|
| `grep motif` | garder les lignes qui contiennent le motif |
| `cut -d, -f2` | extraire la colonne n°2 (séparateur `,`) |
| `sort` | trier (`-n` : numérique, `-r` : décroissant, `-t,` : séparateur, `-k2` : colonne) |
| `uniq -c` | compter les lignes identiques **consécutives** (d'où le `sort` avant) |
| `awk` | mini-langage pour calculer sur les colonnes |

Première question : combien de commandes viennent d'Réseaux ?

```bash
grep -c Réseaux commandes.csv
```
<!--sortie-->
```text
138
```

`grep -c` compte les lignes contenant le mot. (Pandas nous donnerait la même chose avec `(df["canal"] == "Réseaux").sum()`.) Combien de commandes par canal ? Il faut extraire la colonne des canaux (sans l'en-tête), la trier pour regrouper les valeurs identiques, puis compter :

```bash
tail -n +2 commandes.csv | cut -d, -f1 | sort | uniq -c | sort -rn
```
<!--sortie-->
```text
    148 Site
    138 Réseaux
    114 Boutique
```

Cette ligne est un **pipeline** (« tuyau ») : `tail -n +2` supprime l'en-tête (« commence à la ligne 2 »), `cut -d, -f1` garde la première colonne, `sort` regroupe les canaux, `uniq -c` compte chaque groupe, et `sort -rn` classe du plus fréquent au plus rare. Le site est donc le premier canal en nombre de commandes (148), devant Réseaux (138) et la boutique (114) : 400 commandes au total, comme prévu. Le symbole `|` (« pipe ») envoie la sortie d'une commande à l'entrée de la suivante. Quelles sont les trois plus grosses commandes ?

```bash
tail -n +2 commandes.csv | sort -t, -k2 -n -r | head -n 3
```
<!--sortie-->
```text
Site,255.7,4,3
Site,243.8,5,3
Site,217.1,7,4
```

On trie sur la 2ᵉ colonne (`-k2`), numériquement (`-n`), de la plus grande à la plus petite (`-r`), et on garde les trois premières lignes. La plus grosse commande atteint 255,7 € : c'est le maximum déjà vu avec `describe()` au chapitre 3. Et pour le montant moyen ? Il faut calculer, ce que fait `awk` : il lit le fichier ligne par ligne, `$2` désigne la 2ᵉ colonne, `NR` le numéro de ligne.

```bash
awk -F, 'NR > 1 { somme += $2; n++ } END { printf "montant moyen : %.2f € sur %d commandes\n", somme/n, n }' commandes.csv
```
<!--sortie-->
```text
montant moyen : 60.25 € sur 400 commandes
```

L'option `-F,` fixe le séparateur. Pour chaque ligne sauf l'en-tête (`NR > 1`), on ajoute le montant à une somme et on compte ; à la fin (`END`) on affiche la moyenne. Retrouve-t-on bien le 60,25 € du chapitre 3 ? On peut même faire une moyenne **par canal**, avec un tableau associatif (l'équivalent d'un dictionnaire Python) :

```bash
awk -F, 'NR > 1 { somme[$1] += $2; n[$1]++ }
         END { for (canal in n) printf "%-10s %.2f\n", canal, somme[canal]/n[canal] }' commandes.csv | sort
```
<!--sortie-->
```text
Boutique   74.81
Réseaux  49.01
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
    138 Réseaux
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

Voici un scénario qui arrive à tout le monde. En janvier, la gérante installe `pandas` pour son analyse. En juin, elle commence un autre projet qui nécessite une **ancienne** version de la même bibliothèque. Si tout est installé au même endroit, mettre à jour casse l'ancien projet, et rétrograder casse le nouveau. Pire : quand elle envoie son code à Amine, comment sait-il quelles versions utiliser ? D'où l'**environnement virtuel** :

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
python -c "from tabulate import tabulate; print(tabulate([['Boutique', 74.81], ['Réseaux', 49.01], ['Site', 59.5]], headers=['canal', 'montant moyen'], floatfmt='.2f'))"
pip freeze
```
<!--sortie-->
```text
canal        montant moyen
---------  ---------------
Boutique             74.81
Réseaux            49.01
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

`deactivate` quitte l'environnement et rend le terminal à son état ordinaire. Quelqu'un qui reçoit le projet (Amine, ou la gérante dans un an) reconstruit **le même environnement** en deux commandes :

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

La liste obtenue est **identique** à celle de la gérante : mêmes bibliothèques, mêmes versions. Le dossier `.venv` lui-même ne se partage pas (il est propre à la machine et volumineux) : il figure dans le `.gitignore` de 6.1, et seul `requirements.txt` voyage avec le projet.

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
BOUTIQUE="la boutique"
echo "Bienvenue chez $BOUTIQUE"
export TAUX_TVA=0.19
python -c "import os; print('TVA lue depuis Python :', float(os.environ['TAUX_TVA']))"
```
<!--sortie-->
```text
Bienvenue chez la boutique
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
