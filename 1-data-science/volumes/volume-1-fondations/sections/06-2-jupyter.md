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
