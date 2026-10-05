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
