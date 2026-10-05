## 6.6 Exercices du chapitre 6

> 🧭 Cherchez d'abord par vous-même (en tapant les commandes dans un vrai terminal !), vérifiez ensuite, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse. Les corrigés ont été **réellement exécutés** dans l'atelier ; leurs sorties sont celles du livre. Les exercices utilisent un dossier de travail neuf, `~/atelier/exercices`, et le fichier `commandes.csv`.

### Énoncés

**Exercice 1 ⭐ (se repérer).** Créez le dossier `projet-yasmine` contenant deux sous-dossiers, `donnees` et `src`, copiez-y `commandes.csv` (dans `donnees`), puis (a) affichez l'arborescence créée, (b) affichez les **trois dernières** lignes du fichier, (c) comptez ses lignes.

**Exercice 2 ⭐ (tuyaux).** Combien de commandes ont reçu chacune des notes de satisfaction (1 à 5) ? Répondez avec **une seule ligne** de commandes enchaînées par des tuyaux, puis vérifiez avec pandas.

**Exercice 3 ⭐ (premiers pas avec Git).** Dans un nouveau dépôt `journal`, créez un fichier `notes.txt` contenant la ligne « Hypothèse : les commandes Réseaux sont plus petites. » et enregistrez-le (commit 1). Ajoutez une seconde ligne « Test à faire : comparer les moyennes par canal. » et enregistrez (commit 2). Par maladresse, vous supprimez ensuite `notes.txt` avec `rm`. Retrouvez-le **sans refaire à la main**, puis affichez l'historique en une ligne par commit.

**Exercice 4 ⭐⭐ (awk).** Calculez, pour chaque canal, le **pourcentage de commandes notées 4 ou 5** (colonne `satisfaction`), avec `awk`. Vérifiez avec pandas.

**Exercice 5 ⭐⭐ (conflit).** Un fichier `params.txt` contient la ligne `seuil=50`. Sur une branche `prudent`, vous passez la valeur à `seuil=40` ; sur `main`, votre collègue la passe à `seuil=60`. Fusionnez `prudent` dans `main`. Que se passe-t-il ? Résolvez le conflit en gardant la valeur la **plus élevée**, et terminez la fusion.

**Exercice 6 ⭐⭐ (état caché).** Un notebook contient, de haut en bas, les cinq cellules suivantes :
(A) `n = 100` ; (B) `taux = 0.19` ; (C) `tva = n * taux` ; (D) `n = 200` ; (E) `print(tva)`.
La gérante les exécute dans l'ordre **A, B, D, C, E** (elle a lancé D avant C). (a) Qu'affiche E ? (b) Qu'afficherait E après « Restart & Run All » ? (c) Quelle conclusion en tirez-vous ?

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
Réseaux,37.5,3,4
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
Réseaux  63.0 %
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
Réseaux    63.0
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

(a) Dans l'ordre réellement joué, `n` vaut déjà 200 quand C calcule la TVA : E affiche $200\times0{,}19=38$. (b) Dans l'ordre du fichier, C est exécutée alors que `n` vaut encore 100 : E affiche $100\times0{,}19=19$. (c) Le **même notebook** donne deux résultats différents selon l'ordre d'exécution : le chiffre que la gérante voyait à l'écran (38) n'est pas celui qu'obtiendra quiconque ouvrira le fichier et exécutera tout (19). C'est exactement l'état caché du 6.2.3 : **toujours** redémarrer et tout exécuter avant de se fier à un résultat. (Une analyse correcte de la logique du carnet dirait aussi que la cellule D, placée *après* C mais qui change `n`, est probablement mal placée.)

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
print(f"- Montant moyen : {df['montant'].mean():.2f} €")
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

Le fil rouge de tout le chapitre tient en une phrase : **un résultat n'existe que s'il peut être refait**. Vous disposez désormais de l'ensemble des fondations du volume : les mathématiques (chapitre 1), les probabilités (2), la statistique (3), la programmation (4), les bases de données (5) et les outils de travail (6). Il est temps de tout assembler dans le **projet du volume** : une étude complète des ventes de la boutique, des données brutes jusqu'au rapport.
