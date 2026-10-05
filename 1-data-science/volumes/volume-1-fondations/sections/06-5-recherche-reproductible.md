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

```python hide
moyennes = [moyenne(np.random.default_rng(g)) for g in range(1, 9)]
print([round(float(m), 1) for m in moyennes], round(min(moyennes), 1), round(max(moyennes), 1), round(montants.mean(), 2))
```
<!--sortie-->
```text
[54.1, 60.5, 45.2, 63.4, 71.8, 73.3, 59.5, 43.3] 43.3 73.3 60.25
```

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

```bash hide
printf 'rapports/rapport-ventes.html: rapports/rapport-ventes.md\n\tpandoc --standalone rapports/rapport-ventes.md -o $@\n\nrapports/rapport-ventes.md: donnees/commandes.csv src/faire_rapport.py\n\tpython src/faire_rapport.py donnees/commandes.csv > $@\n' > Makefile
rm -f rapports/rapport-ventes.md rapports/rapport-ventes.html
```

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

```bash hide
sed -i '2s/448.0/44.8/' donnees/commandes.csv
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
