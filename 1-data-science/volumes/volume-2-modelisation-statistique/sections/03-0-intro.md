# Chapitre 3 : Analyse multivariée

> « Une variable, on la regarde. Deux variables, on les relie.
> Vingt variables, il faut apprendre à les **résumer**. »

Les chapitres 1 et 2 avaient un point commun : une variable **à expliquer** (la dépense, le rachat, le nombre de commandes) et des variables **explicatives**. Ici, le décor change. Nous n'avons plus de variable réponse : nous avons **un tableau de variables**, et la question est « que contient ce tableau ? ». Quelles variables disent la même chose ? Peut-on les remplacer par deux ou trois indicateurs qui conservent l'essentiel ? Les clients se rangent-ils naturellement en familles ? C'est ce qu'on appelle l'**analyse multivariée**, ou, dans le vocabulaire de l'apprentissage automatique, l'apprentissage **non supervisé** : on cherche de la structure sans qu'aucune « bonne réponse » ne guide la recherche.

La gérante a posé ces questions sans le savoir. Elle a envoyé à ses clientes un petit questionnaire de huit questions et se retrouve avec huit colonnes de notes qui se ressemblent beaucoup : « Les clientes qui aiment la qualité des vases aiment aussi celle des écharpes, non ? » Elle voudrait **un ou deux chiffres par cliente** plutôt que huit. Et elle voudrait aussi savoir si ses 2 000 clientes forment des « types » (les occasionnelles, les fidèles, les grosses acheteuses) à qui s'adresser différemment.

## Le chemin de ce chapitre

- **3.1 Analyse en composantes principales (ACP)** : la technique reine pour **résumer** des variables numériques corrélées. Nous la construirons à la main sur cinq clientes, la démontrerons proprement (c'est un problème d'optimisation, avec les valeurs propres du volume I), puis l'appliquerons au questionnaire.
- **3.2 Analyse factorielle** : un modèle voisin mais différent. L'ACP **résume** ; l'analyse factorielle **explique** les corrélations par des causes cachées (des « facteurs »), comme la qualité du service. Nous apprendrons à les estimer, à les faire tourner (rotation), et à vérifier si l'on retrouve ce que la simulation avait programmé.
- **3.3 Classification non supervisée** : les **k-means** et la **classification hiérarchique**, avec leurs pièges, et une segmentation honnête des clientes de la boutique.
- ➕ **3.4 Analyse des correspondances (AC et ACM)** : l'équivalent de l'ACP pour des **variables qualitatives** (canal, ville, tranche d'âge).
- ➕ **3.5 Analyse discriminante** : quand les groupes sont connus d'avance et que l'on cherche la meilleure frontière entre eux ; le lien avec la régression logistique de la section 2.2.
- **Bilan du chapitre**, puis, dans le **cahier**, les exercices corrigés et les applications guidées.

> 📒 **Comment travailler avec ce chapitre.** Le livre explique chaque méthode avec un exemple calculé à la main, puis en montre le résultat sur les données (chiffres et figures). Les algorithmes de ce chapitre sont courts : le cahier (chapitre 3) vous les fait écrire **vous-même** en NumPy avant d'utiliser `scikit-learn`, puis compare les deux. Si votre version et celle de la bibliothèque donnent les mêmes nombres, vous avez compris l'algorithme. Un conseil : à chaque figure, **prédisez ce que vous allez voir** avant de lire la légende.

> 🧭 **Ce que vous devez avoir en tête du volume I.** Le chapitre s'appuie sur les valeurs propres et la décomposition en valeurs singulières (volume I, sections 1.1.3 et 1.1.4), sur la covariance et la corrélation (volume I, sections 2.3 et 3.1.7) et sur les multiplicateurs de Lagrange (volume I, section 1.3.5). Si ces notions sont floues, relisez-les d'abord : l'ACP n'en est, au fond, que l'application directe.

> 📦 **Les données.** Deux fichiers du dossier `donnees/`, **entièrement simulés** :
> - `enquete_satisfaction.csv` : 1 212 répondantes (60 % des clientes, tirées au hasard) et leurs huit notes de 1 à 5, `q1` à `q8`. Les quatre premières portent sur les **produits** (qualité, finitions…), les quatre dernières sur le **service** (livraison, emballage…).
> - `clients.csv` : les 2 000 clientes, avec âge, canal d'acquisition, nombre de commandes, panier moyen, dépense annuelle et durée de la relation.
>
> Comme les données sont simulées, nous connaîtrons **la vérité** et nous la révélerons à la fin de chaque étude pour juger de la qualité de nos méthodes. Dans la vraie vie, cette vérité n'est jamais disponible : c'est précisément ce qui rend les méthodes de ce chapitre difficiles à valider, et ce qui impose la prudence que nous cultiverons à chaque page.

```python hide
# régénère les figures du chapitre (script build/fig_ch03.py) : elles sont ainsi vérifiées par `make check`
import subprocess, sys
subprocess.run([sys.executable, "build/fig_ch03.py"], check=True)
```
