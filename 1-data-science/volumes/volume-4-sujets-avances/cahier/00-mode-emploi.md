# Mode d'emploi

> « On comprend en lisant, on retient en construisant. »

Ce cahier est le **compagnon du livre** du volume IV (*Sujets avancés et modernes*). Le livre explique les idées ; le cahier les fait travailler. Il contient, chapitre par chapitre, des **applications guidées**, des **exercices** et leurs **corrigés**, puis le **projet du volume** (déployer un modèle avec un pipeline et une supervision) et l'auto-évaluation.

## Comment utiliser ce cahier

1. **Lisez d'abord la section du livre.** Chaque section qui a un prolongement ici se termine par une ligne de ce genre :
   > 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.1, exercices 1.1 à 1.4.
2. **Essayez avant de regarder le corrigé.** Les énoncés sont regroupés dans la partie *Exercices*, les corrigés dans la partie *Corrigés* du même chapitre : on peut chercher sans voir la réponse.
3. **Tapez le code vous-même** plutôt que de le copier : modifiez-le, cassez-le, lisez les messages d'erreur. Dans ce volume, on apprend surtout en changeant un réglage (le pas d'apprentissage, le nombre de partitions, une unité en amont) et en observant ce que devient le résultat.
4. **Faites les applications dans l'ordre** : chacune raconte une petite étude, avec une question, des étapes, du code et une lecture des résultats.
5. **Mesurez avant de conclure.** Un réseau « qui apprend », un service « qui répond » ou un traitement « plus rapide » sont des affirmations qui se vérifient : chaque application demande un chiffre, pas une impression.

## Numérotation et niveaux

Chaque chapitre du cahier correspond au chapitre du livre de même numéro.

| Élément | Numérotation | Exemple |
|---|---|---|
| Application | `Application N.k` | Application 2.1 : première application du chapitre 2 |
| Exercice | `Exercice N.k` | Exercice 2.3 : troisième exercice du chapitre 2 |
| Corrigé | `Corrigé N.k` | Corrigé 2.3 : correction de l'exercice 2.3 |

La difficulté des exercices est indiquée par des étoiles :

| Niveau | Signification |
|---|---|
| ⭐ | application directe d'une formule ou d'une idée vue dans la section |
| ⭐⭐ | demande de combiner deux idées, ou un petit raisonnement |
| ⭐⭐⭐ | demande de la réflexion, une démonstration ou une petite expérience |

Un exercice cite la section du livre qu'il exerce, par exemple « (section 1.2) ».

## Données, modèles et environnement

Les données sont celles du livre, dans le dossier `donnees/` ; les modèles pré-entraînés, dans `modeles/`. Les jeux de la boutique sont **simulés** avec des graines fixes (script `build/donnees4.py`) : vos résultats seront identiques à ceux du livre.

| Fichier | Contenu |
|---|---|
| `mnist_sous_ensemble.npz` | **jeu réel** : 12 000 images de chiffres manuscrits (10 000 pour apprendre, 2 000 pour tester) |
| `ventes_quotidiennes.csv` | ventes journalières de la boutique : `date`, `ventes`, `promo`, `jour_semaine`, `mois` |
| `avis_clients.csv` | avis en français : `id_avis`, `categorie`, `canal`, `note`, `sujet`, `texte` |
| `clients_ml.csv` | les 12 000 clients du volume III, avec la cible `churn_90j` |
| `sources/*.csv` | exports « bruts » volontairement sales : commandes, CRM, catalogues, et les fichiers `verite_*` qui donnent la bonne réponse |
| `gros_volume` (fonction de `donnees4.py`) | des millions de transactions écrites **à la demande** au format Parquet, dans un dossier ignoré par Git |

Les colonnes de `clients_ml.csv` ont le même statut qu'au volume III (identifiant, 19 entrées, cible, et trois colonnes à **ne pas utiliser en entrée** : `depense_6m`, `segment_vrai`, `commandes_apres_cible`). Le dictionnaire des autres jeux figure dans la section « Les données, les modèles et l'environnement du volume » du livre. Chaque chapitre du cahier est **autonome** : il commence par recharger ses données et refaire ses imports.

## Lancer le code

Placez-vous dans le dossier du volume (celui qui contient `donnees/` et `modeles/`), car les chemins sont relatifs (`donnees/clients_ml.csv`). Vous pouvez travailler dans un notebook Jupyter, dans un éditeur avec la commande `python`, ou dans un terminal interactif.

> ⚠️ **Les chemins.** Si Python répond `FileNotFoundError`, c'est presque toujours que vous n'êtes pas dans le bon dossier : vérifiez avec `import os; print(os.getcwd())`.

> ⚠️ **Le temps de calcul.** Les applications sont dimensionnées pour tourner en quelques dizaines de secondes sur un ordinateur ordinaire, **sans carte graphique**. Un réseau y est donc petit, un corpus restreint, un « grand volume » de quelques millions de lignes. Si l'une d'elles est trop lente chez vous, réduisez le nombre d'époques ou l'échantillon, sans changer le raisonnement. Le lancement de Spark prend une quinzaine de secondes : ce n'est pas un blocage.

> ⚠️ **Hors ligne.** Après l'installation unique décrite dans le livre, plus aucun téléchargement n'est nécessaire. Si un programme tente d'aller sur le réseau, c'est qu'une variable d'environnement manque (voir la dernière vérification ci-dessous).

## Vérifier son installation

Avant de commencer, ces trois courts blocs vérifient que les bibliothèques sont installées, que les modèles pré-entraînés se chargent sans réseau, que Java et Tesseract sont trouvés, et qu'un petit réseau à graine fixe donne le résultat attendu. Les numéros de version peuvent différer des nôtres (voir le livre, section « L'environnement »), à condition que tout s'exécute.

**1. Les bibliothèques.**

```python
import sys
from importlib import import_module
from importlib.metadata import version
print("python", sys.version.split()[0])
for p in ["torch", "transformers", "pyspark", "duckdb", "fastapi", "mlflow", "streamlit"]:
    import_module(p)                              # échoue si la bibliothèque est absente
    print(f"{p:13s}", version(p))
```
<!--sortie-->
```text
python 3.13.3
torch         2.14.1+cpu
transformers  5.18.0
pyspark       4.2.0
duckdb        1.5.6
fastapi       0.142.2
mlflow        3.16.1
streamlit     1.65.0
```

**2. Les modèles, Java et Tesseract.**

```python
import os, subprocess
os.environ.setdefault("HF_HOME", "modeles/hf")      # cache local des modèles
os.environ.setdefault("HF_HUB_OFFLINE", "1")        # interdit tout téléchargement
from sentence_transformers import SentenceTransformer
st = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device="cpu")
v = st.encode(["La livraison a été rapide.", "Colis reçu très vite."], normalize_embeddings=True)
print("plongement :", v.shape, "; similarité", round(float(v[0] @ v[1]), 3))
print("java :", subprocess.run(["java", "-version"], capture_output=True, text=True).stderr.splitlines()[0])
import pytesseract
print("tesseract :", pytesseract.get_tesseract_version(), "; français :", "fra" in pytesseract.get_languages())
```
<!--sortie-->
```text
plongement : (2, 384) ; similarité 0.728
java : openjdk version "21.0.9" 2025-10-21
tesseract : 5.5.0 ; français : True
```

**3. Un petit réseau, reproductible.**

```python
import torch
torch.manual_seed(0)
x = torch.linspace(-1, 1, 64).unsqueeze(1)
y = 3 * x + 0.5                                     # la droite à retrouver
net = torch.nn.Linear(1, 1)
opt = torch.optim.SGD(net.parameters(), lr=0.5)
for _ in range(200):
    opt.zero_grad()
    perte = torch.nn.functional.mse_loss(net(x), y)
    perte.backward()
    opt.step()
print("pente", round(net.weight.item(), 3), "ordonnée", round(net.bias.item(), 3), "perte", f"{perte.item():.1e}")
```
<!--sortie-->
```text
pente 3.0 ordonnée 0.5 perte 2.4e-14
```

Vous devez lire une version pour chaque bibliothèque, une similarité positive entre les deux phrases, une version de Java et de Tesseract avec `français : True`, puis une pente proche de 3 et une ordonnée proche de 0,5. Si le deuxième bloc échoue en cherchant un modèle sur internet, c'est que `modeles/` est absent : lancez `bash setup-env.sh` (voir le livre).

## Plan du cahier

| Chapitre | Contenu |
|---|---|
| 1. Deep learning | rétropropagation à la main, réseau à entraîner, convolutions sur les chiffres manuscrits, prévision par réseau récurrent ; ➕ frameworks, apprentissage par transfert, deep learning tabulaire |
| 2. NLP et modèles de langage | du texte aux nombres, plongements, attention, modèle de langage en pratique et son évaluation ; ➕ text mining, sentiments, recherche par plongements |
| 3. Big data et calcul distribué | partitions, mini-MapReduce, requêtes Spark sur un grand volume ; ➕ flux d'événements |
| 4. MLOps | pipelines reproductibles, service d'un modèle, supervision et dérive ; ➕ orchestration, suivi d'expériences, intégration continue, API |
| 5. Ingénierie des données | ETL, contrôles de qualité, réconciliation d'exports sales ; ➕ gouvernance, collecte par API |
| 6 et 7 (facultatifs) | plateformes cloud (coûts, risques) ; applications de démonstration |
| Projet et auto-évaluation | déployer un modèle avec un pipeline et une supervision, puis des questions pour vérifier ses acquis |
