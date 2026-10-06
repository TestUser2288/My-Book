# Chapitre 4 : MLOps

> « Un modèle qui n'existe que dans un notebook n'a encore aidé personne. »

Les trois volumes précédents ont appris à **construire** de bons modèles : les estimer, les valider, les expliquer. Ce chapitre répond à la question suivante, que l'on découvre d'ordinaire à ses dépens : **que se passe-t-il le lendemain du jour où le modèle est bon ?** Il faut le rendre utilisable par d'autres (une application, un service de relance, une équipe commerciale), le garder reproductible, le remplacer sans casser ce qui l'utilise, et s'apercevoir quand il cesse de dire vrai. L'ensemble de ces pratiques porte un nom, **MLOps** (*machine learning operations*), par analogie avec le DevOps du logiciel.


## Le chemin de ce chapitre

- **4.1 Pipelines et automatisation** : du notebook au projet reproductible, le pipeline qui s'ajuste une fois, les tests de données et de modèles, le piège du décalage entre entraînement et service.
- **4.2 Déploiement et mise à disposition** : les quatre façons de servir un modèle, la sérialisation (et ses dangers), une API de scoring, et comment remplacer un modèle sans casser le service.
- **4.3 Supervision** : quoi surveiller, journaliser, composer avec des étiquettes qui arrivent en retard, régler des alertes qui ne fatiguent pas.
- ➕ **4.4 Orchestration** : les graphes de tâches, les reprises, l'idempotence, avec un mini-orchestrateur exécutable.
- ➕ **4.5 Suivi d'expériences** : MLflow, le registre de modèles, versionner les données.
- ➕ **4.6 CI/CD, Docker, Kubernetes, API REST** : automatiser la livraison, empaqueter, exposer proprement.
- ➕ **4.7 Surveillance des modèles et détection de dérive** : PSI, test de Kolmogorov-Smirnov, et un mois de production simulé.

## Le fil rouge : le modèle de résiliation, du notebook au service

Nous reprenons le **modèle de résiliation** du volume III (section 2.4) : prédire, pour chacun des 12 000 clients de la boutique, s'il aura cessé de commander dans les 90 jours (`churn_90j`, 14,0 % de résiliations). Les colonnes qui sont des cibles ou des fuites (`depense_6m`, `segment_vrai`, et surtout `commandes_apres_cible`, la fuite d'information du volume III, section 1.1) sont exclues d'emblée : il reste 19 variables d'entrée. Les données sont **simulées** (graines fixes) ; les modèles sont ceux que vous connaissez :

- la **version 1**, une régression logistique avec imputation, mise à l'échelle et codage disjonctif, d'AUC 0,867 sur le jeu de test ;
- la **version 2**, un gradient boosting par histogrammes qui gère nativement les manquants et les catégories, d'AUC 0,893.

Pour les besoins du chapitre, les 12 000 clients sont répartis en trois jeux, sans recouvrement : **7 200 pour l'entraînement**, **2 400 pour le test** (qui sert à juger une fois), et **2 400 de « réservoir de production »**, que nous utiliserons comme source de clients « nouveaux » dans les sections de déploiement et de supervision.

> 💡 **Intuition.** Un modèle est une **fonction** ; un système de ML est une **chaîne de production**. La fonction se juge sur un jeu de test. La chaîne se juge sur sa **fiabilité** (elle tourne chaque jour), sa **reproductibilité** (on peut refaire le même modèle), sa **traçabilité** (on sait quelle version a produit quelle décision) et sa **vigilance** (elle s'aperçoit quand le monde change). La figure suivante montre les cinq maillons ; le chapitre les parcourt dans l'ordre, puis ajoute les outils qui les automatisent.

![Les maillons d'un système de ML : données, pipeline d'entraînement, modèle versionné, service, décisions. La supervision observe l'ensemble ; les étiquettes qui arrivent plus tard (ici 90 jours après) permettent de mesurer la performance réelle et de ré-entraîner.](figures/ch04-chaine-mlops.png)

## Ce qui est exécuté, et ce qui ne l'est pas

Ce livre n'affiche que les exemples qui enseignent quelque chose. Tout ce qui tourne ici tourne **hors ligne et dans le processus Python** : l'API est interrogée par un client de test (aucun port réseau n'est ouvert), le suivi d'expériences utilise une base SQLite temporaire, l'orchestrateur est un petit programme Python. En revanche, **Airflow, Prefect, dbt, Docker, Kubernetes, les workflows de CI/CD, DVC et Flask** ne font pas partie des outils que ce livre exécute (ils ne sont pas installés sur la machine qui l'a produit, ou ne figurent pas dans ses dépendances) : leurs exemples sont donnés **non exécutés**, signalés comme tels, avec chaque fois un équivalent exécutable minimal quand il en existe un. Les noms d'outils commerciaux sont des exemples, pas des recommandations ; leurs interfaces changent vite (**à vérifier dans leur documentation** avant de s'y fier).


## 4.1 Pipelines et automatisation

### Du notebook au projet reproductible

Un notebook est un excellent outil d'exploration et un mauvais outil de production : l'ordre d'exécution des cellules compte sans être écrit, l'état caché (une variable modifiée trois cellules plus haut) change le résultat, et personne ne sait dire avec quelles données ni quelles versions de bibliothèques le modèle a été produit. La **reproductibilité** est la propriété qui permet à quelqu'un d'autre (ou à vous-même dans six mois) de **refaire exactement le même modèle**. Elle repose sur cinq éléments, que l'on peut cocher un à un :

| Élément | Risque s'il manque | Comment le fixer |
|---|---|---|
| **Graines aléatoires** | deux entraînements donnent deux modèles différents | une graine par composant aléatoire (découpage, modèle, sous-échantillonnage) |
| **Versions des bibliothèques** | une mise à jour change silencieusement un calcul | fichier d'exigences avec versions exactes, environnement isolé |
| **Empreinte des données** | on ne sait plus quelles données ont servi | somme de contrôle (hash) du fichier ou de la table, enregistrée avec le modèle |
| **Configuration** | des paramètres dispersés dans le code | un fichier de configuration unique, versionné |
| **Code** | « ça marchait sur mon poste » | dépôt Git, un commit identifie le code exact |

Le plus sûr est d'écrire ces informations dans un petit fichier d'**empreinte**, enregistré à côté du modèle. Ici, quatre lignes suffisent à capturer ce qui permettrait de refaire l'entraînement :

```python
import platform, sklearn
config = {"graine": 0, "part_test": 0.4, "modele": "logistique", "C": 1.0}
empreinte = {"donnees": hash_fichier("donnees/clients_ml.csv"), "config": config,
             "python": platform.python_version(), "numpy": np.__version__,
             "pandas": pd.__version__, "sklearn": sklearn.__version__}
print(json.dumps(empreinte, indent=1))
```
<!--sortie-->
```text
{
 "donnees": "fa48edff3715",
 "config": {
  "graine": 0,
  "part_test": 0.4,
  "modele": "logistique",
  "C": 1.0
 },
 "python": "3.13.3",
 "numpy": "2.5.3",
 "pandas": "3.0.6",
 "sklearn": "1.9.1"
}
```

Le hash est une « signature » du fichier : modifier **un seul octet** change complètement la signature (c'est le principe des fonctions de hachage cryptographiques, que nous retrouverons en 4.5 pour versionner les données). On peut donc, avant tout entraînement, **vérifier que le fichier est bien celui qu'on croit**.


Sans graine fixée, la graine est tirée au hasard à chaque exécution : deux entraînements successifs de la même forêt aléatoire sur les mêmes données reviennent à deux graines différentes (ici 1 et 2), et donnent des probabilités qui diffèrent **jusqu'à 0,132** pour un même client ; avec la même graine, l'écart est exactement 0,0. Et un octet ajouté à la fin du fichier de données (ici un simple retour à la ligne) fait passer le début du hash de `fa48edff` à `86c8ec59`.

> ⚠️ **Piège.** « Fixer la graine » ne suffit pas toujours : sur GPU ou en parallèle, l'ordre des additions flottantes peut varier d'une exécution à l'autre ; certaines bibliothèques ont plusieurs graines (une pour NumPy, une pour la bibliothèque, une pour le découpage). On vise la reproductibilité **à des différences numériques négligeables près**, on la vérifie par un test (plus bas), et l'on note les rares exceptions connues.

### Le pipeline : un seul objet à entraîner, à enregistrer, à servir

Entre les données brutes et la probabilité de résiliation, il y a des étapes de préparation (imputation des manquants, mise à l'échelle, codage des catégories) et un modèle. Si ces étapes sont écrites à la main dans le notebook et **ré-écrites** dans l'application, elles finiront par diverger (voir plus bas). La solution est de les rassembler dans **un seul objet**. En scikit-learn, c'est un `Pipeline` (étapes en série) contenant un `ColumnTransformer` (étapes différentes selon les colonnes), vus au volume III :

```python
print([(nom, type(etape).__name__) for nom, etape in v1.steps])
print([(nom, type(t).__name__) for nom, t, _ in v1.named_steps["pre"].transformers])
```
<!--sortie-->
```text
[('pre', 'ColumnTransformer'), ('clf', 'LogisticRegression')]
[('num', 'Pipeline'), ('cat', 'OneHotEncoder')]
```

Deux propriétés rendent ce choix précieux. D'abord, **tout ce qui est appris sur les données** (médianes pour imputer, moyennes et écarts-types pour centrer-réduire, liste des catégories) est appris **sur le jeu d'entraînement seulement** puis figé : à tout instant, l'objet applique à un nouveau client la transformation
$$
z = \frac{x - \mu_{\text{train}}}{\sigma_{\text{train}}},
$$
jamais ses propres statistiques. C'est ce qui évite la fuite d'information du volume III. Ensuite, l'objet entier est **sérialisé en un fichier** avec `joblib` ; le recharger donne une fonction qui accepte des clients bruts et rend une probabilité.


Après enregistrement dans un fichier de 6 ko puis rechargement, le modèle rend **exactement** les mêmes probabilités que l'objet d'origine (écart maximal : 0,0). Ce test de **parité** est le premier d'une série que nous allons systématiser.

> 💡 **Intuition.** Le pipeline est la **recette complète**, pas seulement le modèle : en production on ne dit pas « voici les coefficients », on dit « voici une fonction qui prend un client brut et rend une probabilité ». Tant qu'une étape de préparation vit en dehors de cette fonction, elle est une dette technique.

### La structure d'un projet

Un projet reproductible sépare ce qui change vite (expériences) de ce qui doit rester stable (code de production). Une organisation courante, que l'on retrouve avec des variantes dans la plupart des équipes :

```text
projet-resiliation/
├── config/entrainement.yaml     paramètres : graine, hyperparamètres, seuils
├── donnees/                     données brutes (jamais modifiées à la main) ; hash enregistré
├── src/
│   ├── donnees.py               chargement + validation
│   ├── variables.py             préparation (ColumnTransformer)
│   ├── entrainement.py          ajustement + évaluation + enregistrement
│   └── service.py               API de scoring (section 4.2)
├── tests/                       tests de données, de code, de modèle
├── notebooks/                   exploration seulement, rien n'en dépend
├── requirements.txt             versions exactes
└── Makefile                     « make test », « make entrainer », « make servir »
```

La règle qui compte est la dernière : **rien ne doit dépendre d'un notebook**. Un notebook peut appeler le code de `src/`, jamais l'inverse.

### Tester un système de ML

Le logiciel ordinaire se teste par des assertions (« cette fonction rend 4 pour 2+2 ») ; un modèle de ML n'a pas de réponse exacte, mais il a des **invariants** que l'on peut vérifier. On distingue quatre familles, dont trois sont particulières au ML :

1. **tests de code** : les fonctions de préparation rendent le bon type et la bonne forme (comme dans tout logiciel) ;
2. **tests de données** : le *schéma* (colonnes, types), les *plages* de valeurs, les valeurs manquantes sont conformes ;
3. **tests de comportement** : le modèle est déterministe, ne dépend pas de l'ordre des lignes, réagit dans le bon sens (plus de retours produit, plus de risque de résiliation, toutes choses égales par ailleurs) ;
4. **tests de non-régression** : le nouveau modèle ne fait pas moins bien qu'un seuil ou que le modèle en production.

Ces tests s'écrivent comme des fonctions courtes qui lèvent une erreur si l'invariant est violé ; l'outil `pytest` les découvre et les exécute (son usage a été vu au volume I). Pour rester dans le processus du livre, nous écrivons un petit lanceur, et trois tests représentatifs :

```python
def test_schema(lot):
    assert list(lot.columns) == COLONNES, "colonnes différentes de celles de l'entraînement"

def test_plages(lot):
    assert lot["age"].between(18, 100).all(), "âge hors de [18, 100]"
    assert lot["part_achats_promo"].dropna().between(0, 1).all(), "part de promotions hors de [0, 1]"

def test_non_regression(lot, modele, seuil=0.85):
    auc = roc_auc_score(yte, modele.predict_proba(lot)[:, 1])
    assert auc >= seuil, f"AUC {auc:.3f} sous le seuil {seuil}"
```


Le premier passage, sur un lot de test conforme :

```text
lot conforme :
  réussi  test_schema
  réussi  test_plages
  réussi  test_determinisme
  réussi  test_pas_de_fuite
  réussi  test_non_regression
```

Puis le même lot, après un **incident de production** typique : un client en amont a modifié l'export et envoie la part d'achats en promotion en pourcentage (de 0 à 100) au lieu d'une fraction (de 0 à 1), et une colonne interdite s'est glissée dans le fichier.

```text
lot cassé :
  ÉCHEC   test_schema : colonnes différentes de celles de l'entraînement
  ÉCHEC   test_plages : part de promotions hors de [0, 1]
  réussi  test_determinisme
  ÉCHEC   test_pas_de_fuite : colonne interdite : {'commandes_apres_cible'}
```

Le test de plages et le test de schéma attrapent l'anomalie **avant** que le modèle ne produise une seule prédiction ; c'est tout leur intérêt : un modèle qui reçoit des entrées aberrantes ne plante presque jamais, il répond quelque chose, et ce « quelque chose » est faux sans bruit. Un test de non-régression se place en fin de chaîne : si le nouveau modèle passe sous le seuil, on **refuse de le publier**.

> 🧭 **En pratique.** Un test qui échoue doit **bloquer** quelque chose : l'entraînement, la publication du modèle, la mise en production. Un test qui ne bloque rien est un commentaire.

### Le décalage entre entraînement et service

Le défaut le plus fréquent des systèmes de ML en production porte un nom : le **décalage entraînement-service** (*training-serving skew*). Le modèle a été appris sur des variables calculées d'une certaine façon ; en service, elles sont calculées **autrement**. Les causes habituelles sont banales :

- le code de préparation est **écrit deux fois** (en Python pour l'entraînement, dans un autre langage ou une autre équipe pour le service) ;
- une **unité** change (jours/semaines, fraction/pourcentage, euros/centimes) ;
- une valeur **par défaut** diffère pour les manquants ;
- une variable est calculée avec des données **qui n'existent pas encore** au moment de la prédiction (une fuite temporelle que le jeu de test, lui, ne montre pas).

Mesurons l'effet de deux erreurs d'unité, sans toucher au modèle : la récence reçue en **semaines** au lieu de jours, la part d'achats en promotion reçue en **pourcentage** au lieu d'une fraction.


```text
entrée envoyée au service   AUC  probabilité moyenne
             aucun défaut 0.867                0.131
récence en semaines (÷ 7) 0.837                0.067
  part promo en % (× 100) 0.538                0.897
```

Sans défaut, la probabilité moyenne prédite (13,1 %) est proche du taux observé (14,0 %). Avec la récence en semaines, l'AUC passe de 0,867 à 0,837 et la probabilité moyenne à 6,7 % : **le système ne plante pas, il se trompe**. L'erreur sur la part de promotions est encore plus nette (AUC 0,538, probabilité moyenne 89,7 %). Aucune alerte système ne se déclenche : le service répond en quelques millisecondes, avec le bon format.

Les remèdes sont connus, et tous reviennent à **n'avoir qu'un seul chemin de calcul** :

1. **un seul objet** pour la préparation et le modèle (le pipeline ci-dessus), servi tel quel ;
2. des **tests de parité** : un lot de clients est passé à la fois dans l'entraînement et dans le service, les sorties doivent coïncider ;
3. des **tests de plages** sur les entrées du service (section 4.2) ;
4. pour les variables calculées sur l'historique (nombre de commandes sur douze mois), une **table de variables** partagée (*feature store*), calculée **une fois** et lue par l'entraînement comme par le service ;
5. la **journalisation** des entrées réellement reçues en production (section 4.3), pour pouvoir comparer leur distribution à celle de l'entraînement.

### Penser en graphe : le pipeline comme suite d'étapes

Un pipeline d'entraînement complet n'est pas une fonction unique mais une **suite d'étapes** dont chacune consomme les sorties des précédentes : charger, valider, préparer, entraîner, évaluer, publier. Le dessiner comme un **graphe dirigé sans cycle** (DAG, *directed acyclic graph*) apporte trois choses : on voit ce qui dépend de quoi (donc ce qui peut tourner en parallèle), on peut **relancer à partir d'une étape** plutôt que tout recommencer, et chaque étape devient **testable** isolément. La section 4.4 formalise cette idée et en construit une version exécutable.


![Le pipeline d'entraînement comme graphe : deux étapes de contrôle (rouge) peuvent arrêter la chaîne, la configuration alimente l'entraînement, et seul un modèle qui passe l'évaluation arrive au registre.](figures/ch04-pipeline-dag.png)

> 📒 **Pour pratiquer.** Le cahier propose d'écrire une batterie de tests de données et de modèle (application 4.1) et de reproduire un décalage entraînement-service pas à pas (exercices 4.1 et 4.2).


## 4.2 Déploiement et mise à disposition

Un modèle entraîné et testé reste inutile tant qu'il n'est pas **servi** : tant que ses prédictions n'arrivent pas, à temps et sous la bonne forme, à ceux qui s'en servent. Le **déploiement** est l'ensemble des choix qui rendent cela possible : *quand* la prédiction est calculée, *où* tourne le modèle, *sous quel format* il est enregistré, et *comment* on le remplace par un meilleur sans interrompre le service.

### Quatre façons de servir un modèle

Le choix dépend d'abord d'une question : **combien de temps peut-on attendre la prédiction ?**

| Mode | Principe | Quand l'utiliser | Exemple (boutique) |
|---|---|---|---|
| **Par lots** (*batch*) | un programme calcule la prédiction de **tous** les clients à heure fixe et l'écrit dans une table | la décision n'est pas immédiate ; on veut le débit maximal au coût minimal | chaque lundi, on liste les clients à relancer |
| **En ligne** (*online*) | un service répond à **une requête à la fois**, en quelques dizaines de millisecondes | la décision se prend pendant l'interaction | afficher une offre pendant la navigation |
| **En flux** (*streaming*) | la prédiction est calculée au fil d'un **flux d'événements** (chapitre 3) | il faut réagir en secondes à une suite d'événements | détecter un panier abandonné |
| **Embarqué** | le modèle tourne **chez l'utilisateur** (téléphone, caisse, navigateur) | pas de réseau, ou données qui ne doivent pas sortir | suggestion locale sur l'application mobile |

> 🧭 **En pratique.** Le plus simple qui convient est presque toujours le bon. Le mode par lots est le moins cher, le plus facile à tester et à relancer, et le moins sujet aux pannes ; il suffit à beaucoup de cas qu'on croit « temps réel ». On ne passe en ligne que lorsque **la valeur de la décision se perd avec le délai**.

**Budgets de latence et de débit.** Deux nombres décident de l'architecture : la **latence** (le temps d'une requête, notée $W$) et le **débit** (le nombre de requêtes par seconde, noté $\lambda$). Leur lien avec le nombre de requêtes **simultanément en cours de traitement**, $L$, est la **loi de Little** :
$$
L = \lambda \, W .
$$
Si le site envoie 200 requêtes par seconde au service et que chacune demande 50 ms (0,05 s), il y a en moyenne $L = 200 \times 0{,}05 = 10$ requêtes en cours à tout instant : un service qui n'en traite que 4 à la fois **accumule une file d'attente** et la latence explose. Pour tenir, il faut soit réduire $W$ (modèle plus léger, moins de variables à calculer), soit multiplier les processus de service (*workers*).

Le gain du traitement **par lots** vient de cet effet : appliquer le modèle à un tableau de clients en une seule fois partage les coûts fixes (appel de fonction, conversion des types) sur toutes les lignes.


Sur ce modèle, scorer 300 clients un par un prend **plus de dix fois** plus de temps que de les scorer en un seul appel (nous le vérifions à chaque exécution du livre par une assertion, car l'ordre de grandeur est stable alors que les durées exactes dépendent de la machine : nous ne les citons donc pas).

### Sérialiser le modèle : trois formats et leurs conditions

Enregistrer le modèle dans un fichier, c'est le **sérialiser**. Trois familles de formats sont courantes :

| Format | Atouts | Limites |
|---|---|---|
| **`pickle` / `joblib`** | immédiat, conserve tout le pipeline scikit-learn | Python seulement ; **lié aux versions** de scikit-learn et NumPy ; **charger un fichier non fiable exécute du code** |
| **`skops`** | variante de `joblib` qui **refuse par défaut** les objets non déclarés sûrs | même dépendance aux versions |
| **ONNX** | format ouvert, **indépendant du langage** ; un moteur d'exécution léger suffit (pas de scikit-learn en production) | seuls les opérations connues du format sont exportables ; la préparation des données doit être exportée aussi |

Le danger du premier format mérite une démonstration, inoffensive ici. Lire un fichier `pickle`, c'est **exécuter** les instructions qu'il contient ; un attaquant qui peut vous faire charger un « modèle » peut donc faire exécuter ce qu'il veut. Voici un « modèle » qui se contente d'afficher un message au chargement :

```python
import pickle

class Piege:
    def __reduce__(self):                       # instruction exécutée par pickle au chargement
        return (print, ("  ← du code vient de s'exécuter pendant le chargement",))

pickle.loads(pickle.dumps(Piege()))
```
<!--sortie-->
```text
  ← du code vient de s'exécuter pendant le chargement
```

**Règle** : on ne charge un fichier `pickle` ou `joblib` que s'il vient d'une source **que l'on contrôle** (votre propre registre, voir 4.5), jamais d'un téléchargement ou d'un dépôt de fichiers ouvert. Et on enregistre avec le modèle les **versions** de scikit-learn et NumPy qui l'ont produit (c'est le rôle de l'empreinte de 4.1) : un fichier chargé avec une autre version peut donner un résultat différent, sans erreur.

**Le format ONNX** (*Open Neural Network Exchange*) représente un modèle comme un **graphe de calcul** : des nœuds (opérations) reliés par des tenseurs. Un modèle logistique est un graphe de deux nœuds : un produit matriciel avec biais (`Gemm`, qui calcule $ZW + b$), puis la fonction sigmoïde. En voici la construction à la main, à partir des coefficients appris par notre pipeline :

```python
import onnx, onnxruntime as ort
from onnx import helper, TensorProto, numpy_helper
Z = v1.named_steps["pre"].transform(Xte); Z = Z.toarray() if hasattr(Z, "toarray") else Z
clf = v1.named_steps["clf"]; W, b = clf.coef_.T.astype(np.float32), clf.intercept_.astype(np.float32)
graphe = helper.make_graph(
    [helper.make_node("Gemm", ["Z", "W", "b"], ["lin"]), helper.make_node("Sigmoid", ["lin"], ["p"])], "resiliation",
    [helper.make_tensor_value_info("Z", TensorProto.FLOAT, [None, W.shape[0]])],
    [helper.make_tensor_value_info("p", TensorProto.FLOAT, [None, 1])],
    [numpy_helper.from_array(W, "W"), numpy_helper.from_array(b, "b")])
```


Le moteur `onnxruntime` charge ce fichier de 0,3 ko **sans scikit-learn** et rend les mêmes probabilités à $1{,}9\times10^{-7}$ près sur les 2 400 clients de test (les calculs sont faits en simple précision, d'où un écart de l'ordre de $10^{-7}$ et non de zéro) : le test de **parité** vu en 4.1 s'applique aussi après conversion. Deux remarques d'honnêteté : ici seule la partie linéaire est exportée, et la préparation (imputation, mise à l'échelle, codage) reste à faire en amont sur les 49 colonnes de $Z$ (ce qui rouvre la porte au décalage de 4.1) ; un convertisseur dédié (`skl2onnx`) exporte le pipeline entier, au prix de limites sur les transformations acceptées, **à vérifier dans sa documentation** pour chaque version.

### Un service de prédiction avec FastAPI

Pour le mode en ligne, le modèle est enveloppé dans un petit **service web**. **FastAPI** est une bibliothèque Python qui expose des fonctions comme des *points d'accès* HTTP et valide automatiquement les entrées à l'aide de **pydantic**, qui décrit chaque champ attendu (type, bornes). L'essentiel du service tient en une dizaine de lignes :

```python
class Client(BaseModel):                       # le contrat d'entrée : une ligne par variable
    age: int = Field(ge=18, le=100)
    part_achats_promo: float = Field(ge=0, le=1)
    ...                                        # 19 champs au total, avec leurs bornes

modele = joblib.load(CHEMIN_MODELE)            # chargé UNE fois, au démarrage
app = FastAPI(title="Risque de résiliation")

@app.post("/predict")
def predict(c: Client):
    df = pd.DataFrame([c.model_dump()])[COLONNES]
    return {"probabilite": float(modele.predict_proba(df)[0, 1]), "version": VERSION}
```

Le service complet (les 19 champs validés, `/health`, `/predict`, `/predict_batch`) est dans `build/outils_ch04.py` ; il est **exécuté** ci-dessous. Au lieu d'ouvrir un port réseau, on l'interroge avec un **client de test** (`TestClient`), qui envoie de vraies requêtes HTTP au programme dans le même processus : c'est la manière standard de tester une API.

```python
from fastapi.testclient import TestClient
chemin_v2 = os.path.join(WORK, "churn_v2.joblib"); joblib.dump(v2, chemin_v2)
api = TestClient(creer_app(chemin_v2, COLONNES, version="2.0.0"))
print(api.get("/health").json())
client = ligne_json(Xte.iloc[0])
reponse = api.post("/predict", json=client)
print(reponse.status_code, reponse.json())
```
<!--sortie-->
```text
{'status': 'ok', 'version': '2.0.0'}
200 {'probabilite': 0.0049, 'version': '2.0.0'}
```


La réponse du service coïncide avec la prédiction hors ligne (**parité** : 0,0000 d'écart maximal sur un lot de 50 clients envoyés à `/predict_batch`, aux arrondis près). Le **contrat d'entrée** est ce qui protège le modèle des entrées aberrantes de 4.1 : une requête invalide est refusée **avant** d'atteindre le modèle, avec un code d'erreur 422 (« entité non traitable ») et un message (rédigé en anglais par pydantic) qui dit quel champ est en cause.

```python
for nom, requete in [("âge de 17 ans", {**client, "age": 17}), ("champ manquant", {k: v for k, v in client.items() if k != "ville"})]:
    r = api.post("/predict", json=requete)
    erreur = r.json()["detail"][0]
    print(f"{nom:15s} → {r.status_code} · champ {erreur['loc'][-1]} · {erreur['msg']}")
```
<!--sortie-->
```text
âge de 17 ans   → 422 · champ age · Input should be greater than or equal to 18
champ manquant  → 422 · champ ville · Field required
```

> ⚠️ **Piège.** La validation pydantic arrête les valeurs **impossibles** (un âge négatif, une fraction à 90) ; elle n'arrête pas les valeurs **plausibles mais fausses** (une récence en semaines à la place de jours reste un entier valide). Le contrôle de dérive de 4.3 et de 4.7 est là pour cela.

**Mise en service réelle.** Dans la vraie vie, ce programme est lancé par un serveur (par exemple `uvicorn service:app --workers 4`) qui ouvre un port, et plusieurs **processus** tournent en parallèle pour absorber le débit (loi de Little ci-dessus). Chaque processus charge **sa propre copie** du modèle en mémoire : on le charge donc au démarrage et non à chaque requête (les chargements répétés coûtent bien plus que la prédiction), et on compte la mémoire d'un modèle multiplié par le nombre de processus. Une route `/health` sert aux systèmes d'orchestration à savoir si le service est prêt : elle ne doit répondre « ok » qu'**une fois le modèle chargé**.

### Remplacer un modèle sans casser le service

Le modèle de version 2 est meilleur que la version 1 sur le jeu de test. Faut-il le substituer d'un coup ? Non, pour deux raisons : le jeu de test n'est pas la production (les données ont pu changer, les entrées passent par un autre chemin de calcul), et un défaut ne se verrait qu'après coup, sur tous les clients à la fois. On introduit donc le nouveau modèle par **paliers**, selon trois stratégies que l'on peut combiner :

- **le mode fantôme** (*shadow*) : la version 2 reçoit **les mêmes requêtes** et calcule ses scores, mais ses réponses sont **jetées** (seulement journalisées) ; c'est le test le moins risqué, il détecte les plantages, les latences et les écarts forts avec la version 1 ;
- **le déploiement canari** (*canary*) : une **petite part** du trafic (5 %, 10 %) est réellement servie par la version 2 ; on surveille les indicateurs, puis on augmente la part ou on revient en arrière ;
- **le test A/B** : deux versions sont comparées sur **des groupes tirés au hasard**, jusqu'à ce que la différence d'un indicateur métier soit établie statistiquement (volume I, section 3.4.5 ; plans d'expériences au volume II, chapitre 8).

Dans tous les cas, la décision de **qui reçoit quelle version** doit être **déterministe** : un même client doit toujours voir la même version, sinon son expérience oscille et les groupes se contaminent. On y parvient avec une fonction de hachage de l'identifiant (le même principe que le hash de 4.1) :

```python
import hashlib

def version_servie(id_client, part_canari, alias):
    alea = int(hashlib.sha256(str(id_client).encode()).hexdigest(), 16) % 100     # entier stable entre 0 et 99
    return alias["canari"] if alea < part_canari else alias["champion"]
```


Sur les 2 400 clients du réservoir de production, un palier annoncé à 5, 10 et 25 % envoie réellement 5,2, 10,4 et 25,5 % des clients vers la version 2 : le hachage répartit uniformément, sans état à stocker. Les groupes sont **emboîtés** (tous les clients du palier à 10 % sont encore dans le palier à 25 %), ce qui évite de faire changer d'avis les clients quand on monte en charge.

**Le retour arrière** (*rollback*) est la contrepartie indispensable. Il n'est possible que si deux conditions ont été respectées en amont : les anciennes versions du modèle sont **conservées, immuables et identifiées** (numéro de version, hash du fichier), et le service sélectionne la version par un **alias** (« champion », « canari ») plutôt que par un nom de fichier écrit dans le code. Revenir en arrière revient alors à changer une ligne de configuration (ici `alias["canari"] = "1.0.0"` : le canari pointe de nouveau sur la version 1, et plus aucun client ne reçoit la version 2), sans rien reconstruire. La section 4.5 montre un registre de modèles qui fournit exactement cela.

**Combien de clients faut-il pour trancher ?** Imaginons que la relance soit envoyée aux 10 % de clients les mieux notés, et que l'on compare la **précision** de ce ciblage (la part de clients ciblés qui résilient réellement) pour les deux versions. Sur le réservoir, où nous connaissons toutes les étiquettes, les scores donnent :


La version 1 cible avec une précision de 59,6 % et la version 2 de 67,5 % : un avantage réel mais **modeste** (7,9 points), d'autant que les deux versions désignent à 65 % les mêmes clients. Pour l'établir avec 80 % de chances, il faudra un nombre élevé de clients. La formule de dimensionnement d'un test de comparaison de deux proportions (volume I, chapitre 3) est
$$
m \approx \frac{(z_{1-\alpha/2} + z_{1-\beta})^{2}\,\bigl[p_1(1-p_1) + p_2(1-p_2)\bigr]}{(p_2 - p_1)^{2}}
$$
avec $z_{1-\alpha/2} = 1{,}96$ (seuil à 5 %) et $z_{1-\beta} = 0{,}84$ (puissance de 80 %), soit $m \approx 576$ clients **ciblés** par groupe, c'est-à-dire, comme seuls 10 % des clients sont ciblés, environ **5 800 clients par groupe**. La simulation confirme : en tirant des groupes de $n$ clients dans le réservoir et en testant la différence, la version 2 est reconnue meilleure dans 18 % des essais avec 500 clients par groupe, 36 % avec 2 000, 94 % avec 8 000.


![À gauche : un routeur envoie une petite part du trafic à la nouvelle version (canari) et une copie à la version fantôme. À droite : probabilité de conclure qu'une version est meilleure selon le nombre de clients par groupe ; la ligne en pointillé indique 80 % et la ligne bleue la taille donnée par la formule.](figures/ch04-deploiement.png)

> 💡 **Intuition.** Le déploiement progressif **achète de l'information** : un canari à 10 % pendant une semaine mesure le même effet qu'un déploiement complet, au prix d'un risque dix fois plus petit. Mais l'information a un prix en **temps** : tant que les étiquettes (ici les résiliations à 90 jours) ne sont pas arrivées, on ne juge que sur des indicateurs indirects (latence, taux d'erreurs, distribution des scores, accord avec la version 1). Le **mode fantôme** donne ces indicateurs sans risque ; le canari ajoute le risque, mais mesure aussi l'effet de la décision.

> ⚠️ **Piège.** Dans un test A/B d'un modèle qui déclenche une action (relance, remise), l'indicateur n'est pas la précision de la prédiction mais **l'effet de l'action sur les clients** (la rétention obtenue). Un modèle qui désigne très bien les clients qui vont partir n'est pas nécessairement celui qui désigne ceux qu'une relance peut retenir : c'est la distinction entre prédiction et effet causal, au cœur du volume II, chapitre 7.

> 📒 **Pour pratiquer.** Le cahier propose de construire et tester l'API de scoring (application 4.2), de convertir un modèle en ONNX et vérifier la parité (exercice 4.3), et de simuler un déploiement canari avec retour arrière (application 4.3).


## 4.3 Supervision

Un logiciel ordinaire échoue **bruyamment** : une exception, un écran d'erreur, un service qui ne répond plus. Un modèle de ML échoue **en silence** : il continue à répondre, au bon format, dans le bon délai, avec des probabilités qui ne veulent plus rien dire. Nous l'avons vu en 4.1 avec les erreurs d'unité ; le monde, lui, change aussi tout seul (saisonnalité, nouveaux clients, concurrent, campagne de l'entreprise elle-même). La **supervision** (*monitoring*) est l'ensemble des mesures qui permettent de s'en apercevoir **à temps**.

### Quatre couches de supervision

On ne surveille pas « le modèle » : on surveille quatre couches qui se distinguent par ce qu'elles mesurent et par **le délai avant que l'on sache**.

| Couche | Exemples d'indicateurs | Disponible | Ce qu'elle détecte |
|---|---|---|---|
| **Système** | latence (médiane, p95), taux d'erreurs, mémoire, disponibilité | immédiatement | pannes, saturation |
| **Données** | schéma, valeurs manquantes, plages, distribution de chaque variable | immédiatement | changement d'un export, bug amont, décalage de 4.1 |
| **Modèle** | distribution des scores, part de décisions positives, score moyen | immédiatement | dérive des entrées, modèle devenu extrême |
| **Métier** | taux de résiliation réel, précision, gain de la relance | **après le délai de l'étiquette** (ici 90 jours) | le modèle ne dit plus vrai |

Les trois premières couches se voient tout de suite mais ne prouvent rien sur la justesse du modèle ; la quatrième est la seule qui la mesure, mais elle arrive tard. Toute la difficulté de la supervision d'un modèle est dans ce décalage, et la suite du chapitre y revient.

> 💡 **Intuition.** Les trois premières couches sont le **tableau de bord de la voiture** (vitesse, température), la dernière est **l'arrivée de la course** : on ne la connaît qu'à la fin, il faut donc se fier aux premières pour savoir **plus tôt** si quelque chose va mal.

**Latence : regarder la queue, pas la moyenne.** Pour la couche système, la moyenne trompe : quelques requêtes très lentes passent inaperçues dans la moyenne et gâchent l'expérience de ceux qui les subissent. On suit les **centiles** : le *p95* est le temps en deçà duquel passent 95 % des requêtes. Sur une série de 20 000 latences simulées (loi log-normale, graine fixée) :


```text
   indicateur  latence (ms)
      moyenne            48
médiane (p50)            40
          p95           107
          p99           160
```

La latence moyenne est de 48 ms, la médiane de 40 ms, mais **1 requête sur 20 dépasse 107 ms** et 1 sur 100 dépasse 160 ms. Un engagement de service s'exprime donc sur un centile (« 95 % des réponses en moins de 100 ms »), jamais sur la moyenne.

### Journaliser les prédictions

Aucune supervision n'est possible sans **trace** de ce que le modèle a reçu et répondu. Chaque prédiction en production est enregistrée : un identifiant, la date, la **version du modèle**, les entrées (ou celles qui servent à la surveillance), la sortie. Ce journal a trois usages : surveiller les distributions, **rejouer** un incident (« que s'est-il passé pour ce client ? »), et plus tard **rapprocher** chaque prédiction de ce qui s'est réellement passé. Un format simple convient : une ligne JSON par prédiction.

```python
def journaliser(fichier, id_pred, jour, client, proba, version):
    ligne = {"id": id_pred, "jour": jour, "version": version, "proba": round(proba, 4),
             "entrees": {k: client[k] for k in ("recence_jours", "satisfaction_moy", "part_achats_promo")}}
    with open(fichier, "a") as f:
        f.write(json.dumps(ligne) + "\n")
```

> ⚠️ **Piège.** Le journal contient des données de clients : il tombe sous les règles de protection des données (durée de conservation, accès restreint, pseudonymisation de l'identifiant, minimisation des champs). On n'y écrit que ce qui sert à la supervision.

Simulons 60 jours de production : chaque jour, 40 clients du réservoir de production demandent un score (en tout les 2 400 clients du réservoir, une fois chacun), et le service les journalise.


### Les étiquettes arrivent en retard

Le journal contient 2 400 prédictions sur 60 jours. Pour savoir si elles étaient **justes**, il faut l'étiquette : ici, la résiliation dans les 90 jours qui suivent la prédiction. Une prédiction faite le jour $t$ ne peut donc être jugée qu'à partir du jour $t + 90$. La performance d'un modèle en production est ainsi **toujours en retard d'un trimestre**, et pendant ce retard le modèle peut se dégrader sans que l'on le sache.

Voyons ce que l'on sait à trois dates d'observation : au jour 100 (les prédictions des 10 premiers jours ont mûri), au jour 120 (celles du premier mois), au jour 150 (toutes). On rapproche le journal des étiquettes disponibles et l'on calcule l'AUC avec un intervalle de confiance obtenu par rééchantillonnage (*bootstrap*, volume I) :


```text
 jour d'observation  prédictions étiquetées   AUC  borne basse  borne haute
                100                     440 0.884        0.834        0.925
                120                    1240 0.874        0.851        0.903
                150                    2400 0.888        0.869        0.905
```

Au jour 100, seules 440 prédictions sont étiquetées et l'AUC estimée (0,884) est entourée d'un intervalle de largeur 0,092 ; au jour 150, avec 2 400 prédictions, l'intervalle est 0,036 de large. Même quand l'étiquette est enfin là, **le début de la période est jugé sur peu de cas** : on ne conclut à une dégradation que si la baisse dépasse nettement l'incertitude statistique.

### Estimer la performance sans étiquettes

Peut-on se passer de l'étiquette ? Pas entièrement, mais **une partie de l'information est dans les scores eux-mêmes**. Si le modèle est **bien calibré** (une probabilité de 0,3 signifie qu'environ 30 % de ces clients résilient, volume III, section 5.2), alors parmi les clients que le modèle signale, le nombre attendu de résiliations est la **somme des probabilités** ; la **précision attendue** de la liste est leur moyenne. C'est le principe de l'estimation de performance par la confiance (*confidence-based performance estimation*, CBPE) :

$$
\text{précision attendue} \;=\; \frac{1}{|S|}\sum_{i \in S} \hat p_i ,
\qquad S = \{ i : \hat p_i \ge s \}.
$$

```python
def precision_attendue(p, seuil=0.30):
    signales = p >= seuil
    return p[signales].mean()
```

Comparons cette estimation, calculée **sans aucune étiquette**, à la précision réellement observée dans trois situations : le jeu de test (aucun changement), une dérive des **entrées** (la population change, la relation entre variables et résiliation reste la même), et une dérive du **concept** (la population ne change pas, mais la relation change : ici, une campagne de rétention retient une part des clients que le modèle signale ; la section 4.7 décrit ces scénarios en détail).


```text
                     situation  précision attendue (scores)  précision réelle (étiquettes)
  jeu de test (rien ne change)                        0.600                          0.609
dérive des entrées (semaine 4)                        0.637                          0.552
 dérive du concept (semaine 4)                        0.633                          0.100
```

Sans changement, l'estimation sans étiquettes colle à la réalité (60 % attendus contre 61 % observés sur le jeu de test). Avec une dérive des entrées, elle reste du bon ordre de grandeur (64 % contre 55 % à la semaine 4) ; l'écart dépasse l'erreur-type de la précision observée (3 points sur 210 clients signalés), ce qui rappelle que le calibrage n'est jamais parfait, surtout dans les zones que le modèle a peu vues. Avec une dérive du concept, elle est **aveugle** : elle annonce toujours 63 % alors que la précision réelle tombe à 10 %. C'est logique : l'estimateur suppose que la relation entre variables et résiliation n'a pas bougé ; quand c'est justement elle qui change, les scores n'en savent rien.

> 🧭 **En pratique.** L'estimation sans étiquettes est un **signal précoce** précieux contre la dérive des entrées et les bugs de données, et **inutile** contre la dérive du concept. On l'utilise donc en complément de la mesure réelle (étiquettes tardives, échantillon étiqueté à la main, groupe témoin), jamais à sa place.

### Régler des alertes qui ne fatiguent pas

Un indicateur n'est utile que s'il déclenche **une action**. Une alerte mal réglée produit soit trop de fausses alarmes (on finit par les ignorer : c'est la **fatigue d'alerte**), soit trop peu (on rate la vraie panne). Prenons le score moyen du jour comme indicateur. On calcule sa moyenne $\mu$ et son écart-type $\sigma$ sur une **période de référence** de 30 jours sans incident, puis chaque jour on regarde l'écart réduit
$$
z_t = \frac{m_t - \mu}{\sigma},
$$
et l'on déclenche l'alerte si $|z_t|$ dépasse un seuil (2 ou 3 écarts-types). Pour une variable normale, un seuil à 2 écarts-types est dépassé par hasard **un jour sur vingt** (5 %). Sur 60 jours, la probabilité d'au moins une fausse alarme est donc
$$
1 - 0{,}95^{60} \;\approx\; 0{,}95,
$$
quasi certaine, et avec 20 indicateurs surveillés chacun avec ce seuil, on attend en moyenne $20 \times 60 \times 0{,}05 = 60$ fausses alertes par période. C'est le problème des **comparaisons multiples** (volume I), qui apparaît ici sous une forme opérationnelle.

Simulons 90 jours de production avec 200 clients par jour, tirés du réservoir. Les 60 premiers jours sont sans changement (les 30 premiers servent de référence) ; **à partir du jour 61, la population dérive** (plus de clients sensibles aux promotions, moins de clients satisfaits). On compare trois règles sur 300 historiques simulés :

```python
def alerte(z, regle):
    if regle == "2σ":        return np.abs(z) > 2
    if regle == "3σ":        return np.abs(z) > 3
    if regle == "2σ deux jours de suite":
        a = np.abs(z) > 2;   return a & np.r_[False, a[:-1]]
```


```text
                 règle  fausses alertes (30 jours calmes)  dérive détectée (%)  délai médian (jours)
                    2σ                                1.8                 98.3                   4.0
                    3σ                                0.2                 63.7                   9.0
2σ deux jours de suite                                0.1                 59.0                  12.0
```

Sur les 30 jours calmes qui suivent la référence, la règle à 2 écarts-types donne en moyenne 1,8 fausses alertes, celle à 3 écarts-types 0,2, la règle « deux jours de suite » 0,1. Après le début de la dérive (modérée : le score moyen se déplace d'environ un écart-type journalier), ces trois règles la détectent, dans les 30 jours, dans 98 %, 64 % et 59 % des historiques, avec un délai médian de 4, 9 et 12 jours. **Aucune règle ne gagne partout** : durcir le seuil réduit les fausses alertes mais retarde ou manque la détection. Le réglage se fait en connaissance du **coût de chaque erreur** (une fausse alerte coûte une demi-heure d'analyse ; une dérive non vue coûte des relances mal ciblées pendant un trimestre).


![À gauche : score moyen quotidien d'une histoire simulée de 90 jours ; la zone grise est la période de référence, les marques signalent les alertes de deux règles, la ligne rouge le début de la dérive. À droite : précision attendue à partir des scores seuls, comparée à la précision réelle dans trois situations.](figures/ch04-supervision.png)

### Objectifs de niveau de service et budget d'erreur

Pour que les alertes aient un sens, on fixe en amont ce qu'est un service **acceptable**. Un **objectif de niveau de service** (SLO, *service level objective*) est une promesse chiffrée sur un indicateur, mesurée sur une période : par exemple « 99,5 % des requêtes réussissent, mesuré sur 30 jours » ou « le p95 de latence reste sous 100 ms ». L'écart entre la promesse et 100 % est le **budget d'erreur** : ce que l'on s'autorise à rater. Pour 99,5 % de disponibilité sur 30 jours, le budget est
$$
(1 - 0{,}995) \times 30 \times 24 \times 60 \;=\; 216 \text{ minutes d'indisponibilité}.
$$
Tant que le budget n'est pas consommé, on peut déployer de nouvelles versions sans état d'âme ; une fois consommé, on gèle les changements et l'on répare. C'est un moyen d'objectiver la tension entre « avancer vite » et « ne rien casser », qui est de toute façon présente dans chaque équipe.


Une alerte **utile** respecte quelques règles simples : elle est **actionnable** (un texte dit quoi regarder en premier : un *runbook*), **urgente** (si elle peut attendre lundi, c'est un rapport, pas une alerte), **rare** (une alerte qui sonne tous les jours est un bruit de fond), et **adressée** à quelqu'un de précis. Pour un modèle, on distingue en général des alertes **immédiates** (service en panne, entrées hors plages, taux d'erreurs), des alertes **quotidiennes** (distribution des scores, valeurs manquantes) et un **rapport périodique** (performance mesurée sur les étiquettes arrivées).

> 📒 **Pour pratiquer.** Le cahier propose de mettre en place le journal des prédictions et le suivi à étiquettes retardées (application 4.4) et de régler des règles d'alerte en mesurant fausses alertes et délai de détection (exercices 4.4 et 4.5). La section 4.7 prolonge cette section pour la **dérive** : comment la quantifier (PSI, test de Kolmogorov-Smirnov), et quoi faire quand elle est avérée.


## ➕ 4.4 Orchestration

*Section complémentaire : elle prolonge 4.1 (le pipeline comme graphe) et ne conditionne pas la suite du chapitre.*

Jusqu'ici, chaque étape a été lancée à la main. En production, **les mêmes étapes tournent tous les jours** (extraire les clients du jour, valider, calculer les variables, scorer, publier) et il faut que quelqu'un s'occupe de ce qui peut mal tourner : une source indisponible, une étape qui échoue, un jour manqué à rattraper. Cette fonction s'appelle l'**orchestration** : un outil, l'**orchestrateur**, connaît le graphe des tâches, les déclenche à l'heure prévue dans le bon ordre, les relance en cas d'échec, garde une trace de ce qui s'est passé et alerte si besoin. Le plus connu est **Apache Airflow** ; il en existe d'autres (Prefect, Dagster, des services gérés par les fournisseurs de cloud, voir chapitre 6) et le principe est le même.

> 💡 **Intuition.** Un orchestrateur ne **calcule** rien : c'est un chef de chantier qui sait dans quel ordre les corps de métier doivent intervenir, qui rappelle l'électricien s'il n'est pas venu, et qui note ce qui est fait. Le travail lui-même (la validation, l'entraînement, le scoring) reste dans vos fonctions Python, SQL ou Spark.

### Les concepts : tâche, graphe, jour logique

- une **tâche** est une unité de travail qui réussit ou échoue (« valider les données du jour ») ;
- un **graphe de tâches** (DAG) dit quelle tâche dépend de quelle autre ; sans dépendance entre elles, deux tâches peuvent tourner **en parallèle** ;
- une **exécution** (*run*) est une instance du graphe pour **un jour logique** donné : « le traitement du 12 mars », lancé peut-être le 13 mars. La distinction est essentielle : le graphe reçoit **la date qu'il doit traiter**, pas la date du moment où il tourne ;
- chaque tâche d'une exécution a un **état** : planifiée, en cours, réussie, échouée, relancée, ou **ignorée** (parce qu'une tâche dont elle dépend a échoué).

L'ordre d'exécution se déduit du graphe : c'est un **tri topologique**, un ordre où chaque tâche vient après toutes celles dont elle dépend. La bibliothèque standard de Python en fournit un (`graphlib`). Reprenons le scoring quotidien de la boutique, avec une tâche d'alerte qualité qui dépend, comme le calcul des variables, de la validation :

```python
from graphlib import TopologicalSorter
deps = {"valider": {"extraire"}, "variables": {"valider"}, "alerte_qualite": {"valider"},
        "scorer": {"variables"}, "publier": {"scorer"}}
ts = TopologicalSorter(deps); ts.prepare()
while ts.is_active():
    prets = ts.get_ready(); print(sorted(prets)); ts.done(*prets)
```
<!--sortie-->
```text
['extraire']
['valider']
['alerte_qualite', 'variables']
['scorer']
['publier']
```

Chaque ligne est un **niveau** : les tâches d'un même niveau ne dépendent pas les unes des autres et peuvent tourner en même temps (ici, le calcul des variables et l'alerte qualité). C'est ce parallélisme que l'orchestrateur exploite, et c'est aussi ce qui rend la **dépendance explicite** précieuse : sans elle, on ne sait pas ce qui peut être relancé sans danger.

### Reprises, idempotence et rattrapage

Trois propriétés distinguent un pipeline « qui marche » d'un pipeline **qui tient en production**.

**Les reprises (*retries*).** Beaucoup d'échecs sont **transitoires** (une connexion qui saute, une base momentanément saturée) : relancer la tâche quelques secondes plus tard suffit. Si chaque tentative échoue indépendamment avec une probabilité $q$, la probabilité qu'au moins une des $r+1$ tentatives réussisse est
$$
1 - q^{\,r+1}.
$$
Pour $q = 0{,}1$ et deux reprises ($r = 2$), cela donne $1 - 0{,}1^{3} = 0{,}999$ : une panne transitoire fréquente devient presque invisible. On espace les tentatives de façon croissante (**attente exponentielle** : 30 s, 1 min, 2 min…) pour laisser le système se rétablir. Mais attention : une reprise ne guérit **que les pannes aléatoires**. Une erreur déterministe (une donnée invalide, un bug) échoue à chaque tentative et les reprises ne font que retarder l'alerte.

**L'idempotence.** Une tâche est **idempotente** si l'exécuter deux fois (ou dix) a le même effet que l'exécuter une fois. C'est la condition pour que reprises et rattrapages soient sans danger : si une tâche échoue à moitié puis est relancée, elle ne doit pas avoir laissé deux fois les mêmes lignes. On l'obtient presque toujours par un des trois moyens suivants : **écraser** la sortie du jour plutôt que lui ajouter des lignes (une partition par jour), faire un **upsert** (insérer ou mettre à jour selon une clé), ou écrire dans un fichier temporaire puis le **renommer** d'un coup (opération atomique).

**Le rattrapage (*backfill*).** Quand on met en service un nouveau pipeline, ou qu'on corrige une erreur, il faut **rejouer des jours passés**. Un orchestrateur sait lancer le graphe pour chaque jour logique d'une plage ; c'est ici que l'idempotence et le « jour logique » du paragraphe précédent paient.

### Un mini-orchestrateur exécutable

Airflow ne se lance pas dans ce livre (voir plus bas), mais **ses principes tiennent en une trentaine de lignes de Python**, et c'est la meilleure façon de les voir. Le petit orchestrateur de `build/outils_ch04.py` (classe `MiniOrchestrateur`) fait exactement ce qui précède : il parcourt les tâches dans l'ordre topologique, relance celles qui échouent (au plus 2 fois), marque « ignorée » toute tâche dont une dépendance a échoué, et tient un **journal** de chaque tentative. Nous déclarons les quatre tâches du scoring de chaque jour : chacune reçoit le **jour logique** en argument.


```python
orch = MiniOrchestrateur(reprises=2)

@orch.tache("extraire")
def extraire(jour):
    appel_source_instable(jour)                    # échoue deux fois le jour 1 (panne transitoire simulée)
    ecrire_brut(jour)
@orch.tache("valider", depend_de=["extraire"])
def valider(jour):
    assert lire_brut(jour)["part_achats_promo"].between(0, 1).all(), "part de promotions hors de [0, 1]"
@orch.tache("scorer", depend_de=["valider"])
def scorer(jour):
    ecrire_scores(jour)
@orch.tache("publier", depend_de=["scorer"])
def publier(jour):
    publier_partition(jour)
```

Lançons le graphe pour les six premiers jours. Le jour 1 subit deux pannes transitoires ; le jour 3, la source envoie un export cassé (la part de promotions en pourcentage, comme en 4.1).

```python
etats = {jour: orch.lancer(jour) for jour in range(6)}
journal = pd.DataFrame(orch.journal, columns=["jour", "tâche", "essai", "état"])
print(journal[((journal["jour"] == 1) & (journal["tâche"] == "extraire")) | ((journal["jour"] == 3) & (journal["tâche"] != "extraire"))].to_string(index=False))
```
<!--sortie-->
```text
 jour    tâche  essai                    état
    1 extraire      1 échec (ConnectionError)
    1 extraire      2 échec (ConnectionError)
    1 extraire      3                      ok
    3  valider      1  échec (AssertionError)
    3  valider      2  échec (AssertionError)
    3  valider      3  échec (AssertionError)
    3   scorer      0                 ignorée
    3  publier      0                 ignorée
```

Le jour 1, l'extraction a échoué deux fois puis réussi à la troisième tentative : **la reprise a absorbé la panne**. Le jour 3, la validation a échoué trois fois de suite (les reprises ne servent à rien contre une erreur déterministe) ; l'orchestrateur a alors **ignoré** les deux tâches suivantes plutôt que de scorer des données fausses. C'est le comportement voulu : un test de données qui échoue **bloque** la suite (4.1). Vue d'ensemble de l'état final de chaque tâche, jour par jour :


```text
       extraire valider   scorer  publier
jour 0       ok      ok       ok       ok
jour 1       ok      ok       ok       ok
jour 2       ok      ok       ok       ok
jour 3       ok   échec  ignorée  ignorée
jour 4       ok      ok       ok       ok
jour 5       ok      ok       ok       ok
```

Sur 24 tâches, 21 ont réussi, 1 a échoué et 2 ont été ignorées : l'incident est **circonscrit** à un jour et laisse les autres intacts, les jours étant indépendants.

### Corriger et rattraper : l'idempotence à l'épreuve

La source est réparée ; il reste à **rejouer le jour 3**, et pour plus de sûreté on rejoue même toute la période. Le mini-orchestrateur est inchangé : c'est la propriété des tâches (écrasement de la partition du jour) qui empêche les doublons. Pour s'en convaincre, comparons à une publication **par ajout**, non idempotente :


Après la correction, la table publiée contient 240 lignes (6 jours × 40 clients = 240, comme attendu) ; **rejouer les six jours** n'y change rien (240 lignes). À l'inverse, publier deux fois le seul jour 0 par ajout donne 80 lignes pour 40 clients : chaque reprise aurait **dupliqué** les données. C'est pourquoi on conçoit les tâches pour qu'elles soient idempotentes **avant** de les confier à un orchestrateur.


![À gauche : le graphe du jour 3, où la validation a échoué et les deux tâches suivantes sont ignorées. À droite : l'état final de chaque tâche pour les six premiers jours (le nombre d'essais est indiqué quand il dépasse un) avant la correction.](figures/ch04-orchestration.png)

### Les outils réels

Dans un projet réel, on n'écrit pas son orchestrateur ; on déclare le même graphe dans un outil. Voici le même scoring dans **Airflow** et **Prefect**, **non exécutés** (ces bibliothèques ne sont pas installées sur la machine qui a produit ce livre) : leurs interfaces évoluent d'une version majeure à l'autre, **à vérifier dans la documentation** de la version utilisée.

```python
# Airflow — non exécuté (ne pas copier tel quel : l'API varie selon la version)
from airflow.decorators import dag, task
from datetime import datetime

@dag(schedule="@daily", start_date=datetime(2026, 1, 1), catchup=True,
     default_args={"retries": 2})
def scoring_quotidien():
    @task
    def extraire(ds=None): ...         # ds : le jour logique, fourni par Airflow
    @task
    def valider(ds=None): ...
    extraire() >> valider()            # ">>" : « valider dépend de extraire »

scoring_quotidien()
```

```python
# Prefect — non exécuté
from prefect import flow, task

@task(retries=2, retry_delay_seconds=30)
def extraire(jour): ...

@flow
def scoring_quotidien(jour):
    extraire(jour)
```

Le paramètre `catchup=True` d'Airflow est le rattrapage : si le graphe est activé avec une date de début passée, il lance une exécution pour **chaque jour manqué**. Un autre outil, **dbt**, orchestre des transformations SQL : chaque modèle est une requête, et les dépendances sont déclarées par la fonction `ref` ; dbt en déduit le graphe, l'ordre et les tests de données (colonne non nulle, valeurs uniques).

```sql
-- modèle dbt « scores_jour » — non exécuté
select c.id_client, s.proba, s.jour
from {{ ref('clients_valides') }} c
join {{ ref('scores_bruts') }} s using (id_client)
```

> 🧭 **En pratique.** On ne choisit pas un orchestrateur pour ses fonctions mais pour **ce qu'on sait exploiter**. Pour un seul pipeline quotidien, une simple tâche planifiée (`cron`) avec des journaux et une alerte sur code de retour suffit et sera plus fiable qu'un système lourd mal administré. L'orchestrateur devient utile quand les **dépendances** se multiplient, quand on doit **rattraper** des jours, ou quand plusieurs équipes partagent des données. Et l'orchestrateur lui-même doit être **supervisé** : un planificateur arrêté sans que personne ne le sache produit le pire des incidents, celui où rien ne tourne et rien n'alerte.

> 📒 **Pour pratiquer.** Le cahier propose de construire un pipeline de scoring avec reprises et rattrapage (application 4.5) et de rendre idempotente une tâche qui duplique ses sorties (exercice 4.6).


## ➕ 4.5 Suivi d'expériences et registre de modèles

*Section complémentaire : elle prolonge 4.1 (reproductibilité) et 4.2 (alias, retour arrière).*

Un projet de ML produit, en quelques semaines, des dizaines de modèles : on essaie un paramètre, une variable, un autre algorithme. Sans méthode, on se retrouve avec des fichiers `modele_final.joblib`, `modele_final_v2.joblib`, `modele_final_ok.joblib` et plus personne ne sait lequel est en production, avec quels paramètres il a été entraîné, ni sur quelles données. Le **suivi d'expériences** résout cela en enregistrant, pour chaque essai, tout ce qui permet de le comprendre et de le refaire ; le **registre de modèles** gère, parmi ces essais, ceux qui ont le droit d'aller en production.

### Ce que l'on enregistre pour chaque essai

Un essai (*run*) regroupe :

- les **paramètres** : hyperparamètres, graine, choix de variables, **empreinte des données** (4.1) ;
- les **métriques** : AUC en validation croisée, AUC de test, durée ;
- les **artefacts** : le modèle lui-même, la liste des colonnes, les graphiques ;
- des **étiquettes** (*tags*) : qui l'a lancé, version du code (le numéro de commit Git).

Les essais d'un même objectif sont rassemblés dans une **expérience**. **MLflow** est l'outil le plus répandu pour cela : une bibliothèque Python qui écrit ces informations dans un **magasin de suivi** (base de données SQLite en local, PostgreSQL ou un service géré pour une équipe) et les expose par une interface web ou par du code. Tout ce qui suit tourne ici sur une **base SQLite temporaire** : aucun serveur n'est lancé, rien n'est conservé après l'exécution.


Nous comparons quatre candidats pour la prédiction de résiliation : deux régressions logistiques de régularisation différente, deux boostings de pas d'apprentissage différent. Chaque essai enregistre les paramètres, l'AUC en **validation croisée** (sur le jeu d'entraînement : c'est elle qui sert à choisir), l'AUC de test (qui sert à juger une fois, volume III), et le modèle.

```python
mlflow.set_tracking_uri(f"sqlite:///{WORK}/mlflow.db")
mlflow.create_experiment("resiliation", artifact_location=f"file://{WORK}/artefacts"); mlflow.set_experiment("resiliation")
AJUSTES = {}

def enregistrer_run(nom, modele, params):
    with mlflow.start_run(run_name=nom):
        mlflow.log_params({**params, "graine": 0, "hash_donnees": hash_fichier("donnees/clients_ml.csv")})
        mlflow.log_metric("auc_cv", cross_val_score(modele, Xtr, ytr, cv=3, scoring="roc_auc").mean())
        mlflow.log_metric("auc_test", roc_auc_score(yte, modele.fit(Xtr, ytr).predict_proba(Xte)[:, 1]))
        mlflow.sklearn.log_model(modele, name="modele", skops_trusted_types=APPROUVES)
    AJUSTES[nom] = modele

for nom, base, params in [("logistique C=0,1", v1, {"clf__C": 0.1}), ("logistique C=1", v1, {"clf__C": 1.0}),
                          ("boosting pas=0,05", v2, {"clf__learning_rate": 0.05}), ("boosting pas=0,1", v2, {"clf__learning_rate": 0.1})]:
    enregistrer_run(nom, clone(base).set_params(**params), params)
```

Le fichier créé par `log_model` est enregistré au format **skops**, la variante prudente de `joblib` de 4.2 : il refuse de recharger tout objet qui n'a pas été **déclaré sûr** (ici la liste `APPROUVES`, établie après revue). C'est la contrepartie logique du danger du `pickle`. Interrogeons maintenant le magasin : les essais sont rangés du meilleur au moins bon selon l'AUC de validation croisée.

```python
essais = mlflow.search_runs(experiment_names=["resiliation"], order_by=["metrics.auc_cv DESC"])
print(essais[["tags.mlflow.runName", "metrics.auc_cv", "metrics.auc_test"]].round(4).rename(columns=lambda c: c.split(".")[-1]).to_string(index=False))
```
<!--sortie-->
```text
          runName  auc_cv  auc_test
boosting pas=0,05  0.8907    0.8977
 boosting pas=0,1  0.8835    0.8926
   logistique C=1  0.8604    0.8674
 logistique C=0,1  0.8601    0.8672
```


Le meilleur essai selon la validation croisée est « boosting pas=0,05 » (AUC 0,891), et l'on choisit **sur la validation croisée, pas sur le test** : choisir le modèle sur le jeu de test le contaminerait (volume III). L'AUC de test, enregistrée à côté, sert de contrôle final. Les 4 essais restent consultables, comparables et reproductibles : le paramètre `hash_donnees` dit quelles données ont servi, les paramètres du modèle ce qui a été réglé.

> 🧭 **En pratique.** Enregistrer automatiquement **tout** coûte peu et sauve beaucoup. Une règle utile : un essai dont on ne peut pas retrouver les données, le code et l'environnement n'est pas reproductible, donc n'existe pas. On y met donc le hash des données, le commit Git, et le fichier d'exigences (4.1). On n'y met **jamais** de secret (mot de passe, clé d'accès).

### Le registre de modèles : alias et promotion

Parmi tous les essais, quelques modèles méritent d'aller en production. Le **registre de modèles** les nomme et les **versionne** : le modèle « resiliation » aura une version 1, une version 2, chacune renvoyant à l'essai qui l'a produit. On y ajoute des **alias**, des étiquettes mobiles comme « champion » (la version en production) ou « challenger » (celle qu'on teste). Le service de 4.2 charge `models:/resiliation@champion` : promouvoir un modèle ou revenir en arrière revient à **déplacer l'alias**, sans toucher au code du service.

Enregistrons deux versions (la meilleure logistique et le meilleur boosting) et supposons que la logistique est actuellement en production.

```python
reg = MlflowClient()
runs = {r["tags.mlflow.runName"]: r["run_id"] for _, r in essais.iterrows()}
v_log = mlflow.register_model(f"runs:/{runs['logistique C=1']}/modele", "resiliation").version
v_boost = mlflow.register_model(f"runs:/{runs['boosting pas=0,05']}/modele", "resiliation").version
reg.set_registered_model_alias("resiliation", "champion", v_log)
reg.set_registered_model_alias("resiliation", "challenger", v_boost)
print({a: reg.get_model_version_by_alias("resiliation", a).version for a in ("champion", "challenger")})
```
<!--sortie-->
```text
{'champion': 1, 'challenger': 2}
```

La promotion et le retour arrière sont de simples déplacements d'alias, et l'on charge toujours par l'alias :

```python
reg.set_registered_model_alias("resiliation", "champion", v_boost)          # promotion
en_prod = mlflow.sklearn.load_model("models:/resiliation@champion")
print("champion = version", reg.get_model_version_by_alias("resiliation", "champion").version)
reg.set_registered_model_alias("resiliation", "champion", v_log)            # retour arrière
print("champion = version", reg.get_model_version_by_alias("resiliation", "champion").version)
```
<!--sortie-->
```text
champion = version 2
champion = version 1
```


Le modèle rechargé par l'alias rend **les mêmes probabilités** que celui de l'essai (écart maximal 0,0). Et à partir de n'importe quelle version du registre, on remonte à l'essai d'origine puis aux données (le hash `fa48edff…` du champion actuel) : c'est la **traçabilité** que 4.1 réclamait. En cas de litige (« pourquoi ce client a-t-il été relancé en mars ? »), on sait quelle version était « champion » ce jour-là, avec quels paramètres, entraînée sur quelles données.

> ⚠️ **Piège.** MLflow a connu plusieurs systèmes de gestion du cycle de vie d'un modèle : les anciens « stades » (*Staging*, *Production*) sont dépréciés au profit des **alias**, utilisés ici. Comme les interfaces de ces outils changent vite, **à vérifier dans la documentation** de la version installée.

### Versionner les données

Git versionne bien le code, mal les gros fichiers (chaque version est stockée en entier, les dépôts gonflent). Pour les données, on utilise le **stockage adressé par le contenu** : un fichier est rangé sous le nom de son hash. Deux fichiers identiques ont le même nom, donc ne sont stockés qu'une fois ; deux versions différentes ont des noms différents. Dans Git, on ne versionne qu'un petit **pointeur** (nom du fichier, hash, taille) ; un pointeur à jour suffit à retrouver exactement la bonne version des données. C'est le principe de **DVC** (*data version control*), dont les commandes sont les suivantes (**non exécutées** : l'outil n'est pas installé ici).

```bash
dvc init                                          # une fois par dépôt
dvc add donnees/clients_ml.csv                    # crée clients_ml.csv.dvc (le pointeur), retire le fichier de Git
git add donnees/clients_ml.csv.dvc .gitignore     # on versionne le pointeur
git commit -m "Données du 5 octobre"
dvc push                                          # envoie le fichier vers le stockage distant configuré
dvc checkout                                      # retrouve la version qui correspond au commit courant
```

Le mécanisme se réécrit en quelques lignes, à la main, et c'est la meilleure façon de le comprendre :

```python
def stocker(chemin, magasin):
    h = hash_fichier(chemin, 64)                                    # empreinte complète (SHA-256)
    cible = os.path.join(magasin, h[:2], h)
    os.makedirs(os.path.dirname(cible), exist_ok=True)
    if not os.path.exists(cible):
        shutil.copy(chemin, cible)                                  # un objet identique n'est stocké qu'une fois
    return {"fichier": os.path.basename(chemin), "hash": h, "taille": os.path.getsize(chemin)}   # le pointeur

def restaurer(pointeur, magasin, destination):
    source = os.path.join(magasin, pointeur["hash"][:2], pointeur["hash"])
    assert hash_fichier(source, 64) == pointeur["hash"], "objet du magasin corrompu"
    shutil.copy(source, destination)
```

Stockons la version actuelle des données, puis une version corrigée (quelques valeurs rectifiées), puis la version actuelle une seconde fois :


```text
 version             fichier         hash  taille
actuelle      clients_ml.csv fa48edff3715 1153851
corrigée clients_corrige.csv 041b3c3d9ffb 1153851
```

Trois appels, mais **2 objets** seulement dans le magasin : la seconde sauvegarde de la version actuelle n'a rien ajouté (même hash, même objet). La version actuelle commence par `fa48edff3715` et la version corrigée par `041b3c3d9ffb` ; la restauration d'un pointeur redonne un fichier de même hash, et refuse un objet altéré. Le hash des données enregistré dans les essais MLflow ci-dessus est précisément le début de ce hash : **le registre de modèles et le magasin de données se recoupent**.


![À gauche : la chaîne de traçabilité, de l'alias « champion » à la version du modèle, à l'essai qui l'a produit, aux données et au code. À droite : AUC en validation croisée (qui sert à choisir) et AUC de test (qui contrôle) des quatre essais ; les deux mesures classent les essais dans le même ordre ; le test est un peu plus élevé, sans doute parce que la validation croisée n'entraîne chaque modèle que sur les deux tiers du jeu d'entraînement.](figures/ch04-suivi.png)

> 📒 **Pour pratiquer.** Le cahier propose de suivre une petite recherche d'hyperparamètres avec MLflow et de promouvoir un modèle par alias (application 4.6), et de montrer qu'un modèle ne peut pas être reproduit sans le hash des données (exercice 4.7).


## ➕ 4.6 CI/CD, conteneurs, Kubernetes et API REST

*Section complémentaire : elle prolonge 4.2 (déployer un service) et 4.1 (les tests qui bloquent).*

Savoir entraîner, tester et servir un modèle ne suffit pas : il faut que **chaque modification** (une variable ajoutée, une bibliothèque mise à jour) suive le même chemin automatique jusqu'à la production, sans que quelqu'un exécute à la main une liste de commandes dont il oubliera une étape. Cette section regroupe les quatre outils qui rendent ce chemin fiable : l'**automatisation de la livraison** (CI/CD), les **conteneurs** (Docker), leur **exploitation à l'échelle** (Kubernetes) et la **façon d'exposer** le service (API REST), avec ses bases de sécurité. Les exemples de CI/CD, de Docker, de Kubernetes et de Flask sont donnés **non exécutés** ; ce qui peut s'exécuter ici (porte de qualité, configuration, test de contrat de l'API, authentification) l'est.

### L'intégration et la livraison continues (CI/CD)

- l'**intégration continue** (CI, *continuous integration*) exécute **automatiquement**, à chaque modification du code, les tests de 4.1 : si l'un échoue, la modification est refusée ;
- la **livraison continue** (CD, *continuous delivery*) prépare, à chaque modification validée, un **paquet livrable** (une image de conteneur, une version de modèle) et le déploie, éventuellement après une validation humaine ; le **déploiement continu** retire cette validation.

Le principe est celui d'une chaîne avec des **portes** : on n'avance que si la porte précédente est franchie. Voici un fichier de **GitHub Actions** (un service d'automatisation attaché à un dépôt Git) qui exécute les tests et construit l'image à chaque envoi de code ; il est **non exécuté** ici, et la syntaxe de ces fichiers évolue : **à vérifier dans la documentation** du service.

```yaml
name: integration
on: [push, pull_request]
jobs:
  verifier:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.13"}
      - run: pip install -r requirements.txt
      - run: pytest tests/ -q                       # un test qui échoue bloque la fusion
      - run: docker build -t resiliation:${{ github.sha }} .
```

Pour un projet de ML, la porte la plus importante n'est pas un test de code mais un test de **modèle** : un candidat n'est publié que s'il est assez bon **et** pas moins bon que celui en production (la non-régression de 4.1). Cette porte s'écrit comme n'importe quelle fonction ; la CI n'a plus qu'à l'appeler et à échouer si elle refuse :

```python
def porte_qualite(candidat, champion, lot, y, plancher=0.85, tolerance=0.005):
    auc_c, auc_p = (roc_auc_score(y, m.predict_proba(lot)[:, 1]) for m in (candidat, champion))
    verdicts = {f"AUC ≥ {plancher}": auc_c >= plancher, f"pas de régression de plus de {tolerance}": auc_c >= auc_p - tolerance}
    return all(verdicts.values()), auc_c, verdicts
```


Appliquons-la à deux candidats, face au modèle logistique de la version 1 considéré comme « champion » :

```text
                  candidat  AUC test décision                      règle(s) non respectée(s)
      boosting (version 2)     0.893   publié                                              -
logistique sur 300 clients     0.818   REFUSÉ AUC ≥ 0.85, pas de régression de plus de 0.005
```

Le boosting (AUC 0,893) franchit la porte ; le modèle appris sur 300 clients seulement (AUC 0,818) est **refusé**, et la chaîne s'arrête sans intervention humaine, avec un message qui dit quelle règle a échoué. Dans une vraie chaîne, ce refus se traduit par un code de sortie non nul du programme, que l'outil de CI reconnaît comme un échec.

> ⚠️ **Piège.** La porte compare au jeu de test. Si l'on enchaîne de nombreux candidats en ne gardant que ceux qui passent, le jeu de test se contamine à la longue (volume III) : on le renouvelle de temps en temps, et l'on garde de côté un jeu **jamais utilisé pour décider**.

### Les conteneurs avec Docker

« Chez moi, ça marche. » Un **conteneur** est la réponse systématique à cette phrase : c'est une boîte qui embarque le programme **et son environnement** (version de Python, bibliothèques, fichiers) et qui s'exécute de la même façon sur n'importe quelle machine disposant du moteur de conteneurs. On le décrit dans un fichier, le **Dockerfile**, qui produit une **image** (le modèle de la boîte) ; chaque lancement de l'image est un **conteneur**. Le Dockerfile du service de 4.2 (**non exécuté** : Docker n'est pas installé ici) :

```dockerfile
FROM python:3.13-slim                      # image de base, version fixée (jamais « latest »)
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt     # étape lente : placée avant le code pour être mise en cache
COPY src/ src/
COPY modele/ modele/
RUN useradd --create-home service          # ne pas tourner en administrateur
USER service
EXPOSE 8000
HEALTHCHECK CMD python -c "import urllib.request as u; u.urlopen('http://localhost:8000/health')"
CMD ["uvicorn", "src.service:app", "--host", "0.0.0.0", "--port", "8000"]
```

Quelques règles découlent directement de ce fichier :

- **versions fixées partout** : l'image de base et les bibliothèques (`requirements.txt` aux versions exactes, 4.1), sinon la même construction faite deux mois plus tard donne une image différente ;
- **l'ordre des instructions compte** : Docker met en cache chaque étape ; en copiant d'abord les exigences, puis le code, une modification du code ne refait pas l'installation des bibliothèques ;
- **le modèle** est soit copié dans l'image (simple, mais il faut reconstruire l'image à chaque nouveau modèle), soit **téléchargé au démarrage** depuis le registre par son alias (4.5) : le second choix permet de changer de modèle sans reconstruire ;
- **pas de secret dans l'image** : quiconque peut lire l'image peut lire ce qu'elle contient.

### La configuration par l'environnement

Une image doit être **la même** en test et en production ; ce qui change (adresse du registre, seuil d'alerte, clé d'accès) est fourni **de l'extérieur**, par des **variables d'environnement**. C'est un des principes de la méthode dite des **douze facteurs** (*twelve-factor app*) : le code ne contient aucune configuration, et un secret n'est jamais écrit dans le dépôt. Le chargement de la configuration est lui aussi une fonction testable :

```python
def charger_config(env):
    return {"alias": env.get("MODELE_ALIAS", "champion"),                   # valeur par défaut sûre
            "seuil": float(env.get("SEUIL_ALERTE", "0.30")),
            "registre": env["URL_REGISTRE"]}                               # pas de défaut : KeyError si absente
```


Sans l'adresse du registre, la fonction **échoue immédiatement et bruyamment** (« configuration incomplète : variable 'URL_REGISTRE' absente ») plutôt que de démarrer avec une valeur inventée ; avec une configuration complète, les valeurs absentes prennent leur valeur par défaut (alias « champion ») et celles fournies sont lues telles quelles (seuil 0,25).

### Kubernetes : faire tourner beaucoup de conteneurs

Un conteneur ne suffit plus quand le service doit tenir la charge (plusieurs copies, loi de Little de 4.2), survivre à des pannes (relancer un conteneur qui tombe) et se mettre à jour sans interruption. **Kubernetes** est le système qui gère un parc de conteneurs : vous lui **déclarez l'état voulu** (« trois copies de cette image, prêtes avant de recevoir du trafic »), et il agit en permanence pour que l'état réel s'en rapproche. Trois objets suffisent pour comprendre :

- un **pod** : un ou plusieurs conteneurs qui tournent ensemble (en général, un seul) ;
- un **déploiement** (*Deployment*) : le nombre de copies voulues d'un pod, et la façon de les remplacer lors d'une mise à jour (**mise à jour progressive** : un pod à la fois, sans coupure) ;
- un **service** : une adresse stable devant ces copies, qui répartit les requêtes entre celles qui sont prêtes.

Le manifeste ci-dessous (**non exécuté**) déclare le service de scoring : trois copies, des ressources bornées, et deux **sondes** qui interrogent la route `/health` de 4.2. La sonde de **vivacité** redémarre un pod bloqué ; celle de **disponibilité** n'envoie du trafic qu'aux pods dont le modèle est chargé.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: {name: resiliation}
spec:
  replicas: 3
  selector: {matchLabels: {app: resiliation}}
  template:
    metadata: {labels: {app: resiliation}}
    spec:
      containers:
        - name: service
          image: registre.exemple/resiliation:2.0.0
          resources: {requests: {cpu: "500m", memory: "512Mi"}, limits: {memory: "1Gi"}}
          readinessProbe: {httpGet: {path: /health, port: 8000}}
          env: [{name: MODELE_ALIAS, value: champion}]
```

Le nombre de copies se déduit de la loi de Little : à 200 requêtes par seconde de 50 ms, il y a en moyenne 10 requêtes simultanées ; si un pod en traite 4 à la fois, il en faut au moins $\lceil 10/4 \rceil = 3$, et avec une marge de 30 % pour les pointes, $\lceil 13/4 \rceil = 4$.


Kubernetes sait aussi **ajuster le nombre de copies à la charge** (mise à l'échelle automatique, voir le chapitre 6) et appliquer les stratégies de 4.2 (canari, retour arrière) ; mais il ajoute une **complexité considérable** à exploiter. Pour un service de scoring de quelques requêtes par seconde, un simple conteneur sur un service géré par un fournisseur de cloud est souvent le meilleur choix. On ne prend Kubernetes que pour ce qu'il résout (plusieurs services, charge variable, équipe qui sait l'exploiter).

### Concevoir l'API : les principes REST

L'interface entre le modèle et ceux qui l'utilisent est une **API** (*application programming interface*). Le style le plus courant pour une API web est **REST** : on manipule des **ressources**, désignées par des adresses (URL), avec un petit nombre d'**actions** standard, les méthodes HTTP, et on lit le résultat dans un **code de statut**.

| Méthode | Sens | Exemple | Répétable sans effet ? |
|---|---|---|---|
| `GET` | lire | `GET /health` | oui |
| `POST` | créer / demander un calcul | `POST /predict` | non en général |
| `PUT` | remplacer | `PUT /modeles/resiliation/alias/champion` | oui |
| `DELETE` | supprimer | `DELETE /predictions/42` | oui |

| Code | Sens | Quand |
|---|---|---|
| 200 | succès | la prédiction est rendue |
| 400 / 422 | requête mal formée / invalide | JSON illisible, âge de 17 ans |
| 401 / 403 | non authentifié / non autorisé | clé absente / droits insuffisants |
| 404 / 405 | inconnu / méthode interdite | URL inexistante, `GET` sur `/predict` |
| 429 | trop de requêtes | quota dépassé |
| 500 / 503 | erreur du serveur / indisponible | bug, modèle pas encore chargé |

Quelques règles de conception évitent des années de gêne : des **noms** (au pluriel) plutôt que des verbes dans les URL, un **numéro de version** dans l'adresse (`/v1/predict`) pour pouvoir faire évoluer l'API sans casser ceux qui l'utilisent, des **réponses structurées** et stables (le même schéma JSON, toujours), et des **codes de statut exacts** (une erreur de validation n'est pas un code 200 avec un message dedans). L'API décrit elle-même son **contrat** : FastAPI génère automatiquement une description au format **OpenAPI**, d'où l'on tire une documentation interactive et des tests. Le contrat se vérifie par un test, que nous exécutons sur le service de 4.2 :

```python
requetes = [("GET", "/health", None, 200), ("POST", "/predict", client, 200), ("POST", "/predict", {**client, "age": 17}, 422),
            ("POST", "/predict", "pas du json", 422), ("GET", "/predict", None, 405), ("GET", "/inexistant", None, 404)]
rapport = []
for methode, url, corps, attendu in requetes:
    r = api.request(methode, url, json=corps) if not isinstance(corps, str) else api.request(methode, url, content=corps)
    rapport.append((methode, url, attendu, r.status_code, "oui" if r.status_code == attendu else "NON"))
print(pd.DataFrame(rapport, columns=["méthode", "URL", "attendu", "obtenu", "conforme"]).to_string(index=False))
```
<!--sortie-->
```text
méthode         URL  attendu  obtenu conforme
    GET     /health      200     200      oui
   POST    /predict      200     200      oui
   POST    /predict      422     422      oui
   POST    /predict      422     422      oui
    GET    /predict      405     405      oui
    GET /inexistant      404     404      oui
```


Les six comportements sont conformes, et la description OpenAPI générée contient exactement les routes attendues : /health, /predict, /predict_batch. Écrire ce genre de test **avant** de déployer une nouvelle version garantit qu'un changement interne n'a pas modifié le contrat que d'autres programmes utilisent.

**Flask, l'autre bibliothèque courante.** Beaucoup de services de ML existants sont écrits avec Flask, plus ancienne et plus minimaliste : elle ne valide pas les entrées (il faut le faire à la main) et ne produit pas de description OpenAPI, mais elle est très répandue. Le même service s'y écrit ainsi (**non exécuté**, Flask n'étant pas une dépendance de ce livre) :

```python
from flask import Flask, request, jsonify

app = Flask(__name__)
modele = joblib.load(CHEMIN_MODELE)

@app.post("/predict")
def predict():
    donnees = request.get_json(silent=True)
    if donnees is None or not valide(donnees):          # la validation est à écrire soi-même
        return jsonify(erreur="entrée invalide"), 422
    p = modele.predict_proba(pd.DataFrame([donnees])[COLONNES])[0, 1]
    return jsonify(probabilite=float(p), version=VERSION)
```

### Bases de sécurité

Un service de prédiction est un programme exposé : il faut le protéger comme n'importe quel service, et le modèle ajoute quelques risques propres. Les mesures de base, par ordre d'importance :

| Risque | Mesure |
|---|---|
| accès par n'importe qui | **authentification** (clé d'API, jeton), chiffrement du trafic (HTTPS) |
| accès à des données qui ne sont pas les siennes | **autorisation** (qui peut appeler quoi), moindre privilège |
| abus, surcharge | **limitation du débit** (code 429), délais maximaux |
| entrées malveillantes ou aberrantes | **validation stricte** (pydantic, 4.2), taille maximale des requêtes |
| secrets dans le code ou l'image | variables d'environnement, **gestionnaire de secrets**, analyse automatique du dépôt |
| bibliothèques vulnérables | mises à jour régulières, **analyse des images** |
| fuites dans les journaux | ne pas journaliser de données personnelles inutiles (4.3) |
| modèle téléchargé piégé | `pickle`/`joblib` seulement depuis une source maîtrisée (4.2) |
| modèle copié ou interrogé pour en déduire les données | limiter le nombre de requêtes, ne rendre que ce qui est nécessaire (pas les scores internes) |

Voici la mise en œuvre minimale des deux premières lignes : un petit service où chaque appel doit présenter une clé, et qui limite chaque clé à trois appels. La clé est ici écrite en clair **pour l'exemple** ; en production, elle serait lue dans l'environnement ou un gestionnaire de secrets, comme plus haut.

```python
from fastapi import FastAPI, Header, HTTPException
protege, appels = FastAPI(), {}
CLES = {"cle-de-test"}                                       # exemple seulement : jamais de secret dans le code

@protege.get("/score")
def score(x_api_key: str = Header(default="")):
    if x_api_key not in CLES:
        raise HTTPException(401, "clé absente ou invalide")
    appels[x_api_key] = appels.get(x_api_key, 0) + 1
    if appels[x_api_key] > 3:
        raise HTTPException(429, "trop de requêtes")
    return {"ok": True}
```


```text
        appel  code
     sans clé   401
 mauvaise clé   401
bonne clé (1)   200
bonne clé (2)   200
bonne clé (3)   200
bonne clé (4)   429
```

Sans clé ou avec une mauvaise clé, le service répond 401 sans rien calculer ; avec la bonne clé, les trois premiers appels passent, **le quatrième reçoit 429**. Remarquons que le **refus arrive avant tout calcul** : un service qui vérifie après avoir calculé a déjà perdu la ressource qu'on voulait protéger.


![En haut : la chaîne de livraison, avec ses portes (tests, qualité du modèle) qui peuvent chacune arrêter la chaîne, et le retour arrière quand les indicateurs se dégradent après déploiement. En bas : un service Kubernetes qui répartit les requêtes entre plusieurs copies prêtes du conteneur.](figures/ch04-cicd.png)

> 🧭 **En pratique.** On automatise **dans cet ordre** : d'abord les tests (4.1), puis la construction reproductible de l'image, puis le déploiement, et en dernier seulement l'orchestration lourde. Une chaîne simple mais complète vaut mieux qu'une plateforme sophistiquée que personne ne sait réparer.

> 📒 **Pour pratiquer.** Le cahier propose d'écrire une porte de qualité et de la tester sur des candidats (application 4.7), de rédiger le test de contrat d'une API (exercice 4.8) et d'ajouter l'authentification et la limitation de débit à un service (exercice 4.9).


## ➕ 4.7 Surveillance des modèles et détection de dérive

*Section complémentaire : elle prolonge 4.3 (supervision) en quantifiant la dérive et en décidant quoi en faire.*

Un modèle est appris sur le **passé** et appliqué à l'**avenir** ; il ne reste juste que tant que l'avenir ressemble au passé. La **dérive** (*drift*) désigne tout changement qui rompt cette ressemblance. La section 4.3 a montré qu'on la détecte tard par les étiquettes, et plus tôt, mais imparfaitement, par les entrées et les scores. Nous allons ici distinguer ses formes, construire deux outils de mesure (le PSI et le test de Kolmogorov-Smirnov), simuler un mois de production, et regarder ce qu'il faut en conclure.

### Trois formes de dérive

Un modèle de résiliation apprend, en gros, une relation entre des variables $x$ (récence, satisfaction, nombre de commandes…) et une étiquette $y$ (résilier ou non). Tout le jeu de données se résume à la loi conjointe, qui se factorise de deux façons :
$$
P(x, y) \;=\; P(y \mid x)\, P(x) \;=\; P(x \mid y)\, P(y).
$$
La première factorisation désigne deux endroits où le monde peut changer, et la seconde un troisième.

| Forme | Ce qui change | Exemple dans la boutique | Visible sans étiquettes ? | Effet sur le modèle |
|---|---|---|---|---|
| **Dérive des variables** (*covariate shift*) | $P(x)$ : les clients ne sont plus les mêmes | arrivée de clients attirés par les promotions | **oui** (les entrées changent) | souvent modéré, si $P(y \mid x)$ reste vraie ; fort si l'on sort du domaine d'apprentissage |
| **Dérive de l'étiquette** (*label shift*) | $P(y)$ : le taux de résiliation change | un concurrent s'installe, la résiliation passe de 14 % à 20 % | partiellement (les scores montent) | calibrage faussé, classement parfois préservé |
| **Dérive du concept** (*concept drift*) | $P(y \mid x)$ : **la relation** change | une campagne de rétention retient les clients que le modèle signale ; un changement de politique de retours | **non** | le modèle devient faux, sans que les entrées bougent |

Cette dernière est la plus dangereuse et la plus subtile : elle survient notamment **quand le modèle sert à agir**. Si la boutique relance les clients dont le score est élevé, et que la relance réussit, ces clients ne résilient finalement pas : **le modèle a modifié le monde qu'il prédit**, et la relation que ses données d'apprentissage décrivaient n'existe plus. Nous le simulons plus bas.

### Mesurer un changement de distribution : le PSI

L'**indice de stabilité de population** (PSI, *population stability index*) compare la distribution d'une variable dans la population de référence (celle de l'entraînement) à celle d'une période récente. On découpe d'abord la plage de la variable en $k$ **intervalles** (en général les 10 déciles de la référence), de sorte que chacun contient 10 % de la référence. Si $p_i$ est la part de la référence dans l'intervalle $i$ et $q_i$ celle de la période récente, le PSI vaut
$$
\text{PSI} \;=\; \sum_{i=1}^{k} (q_i - p_i)\,\ln\frac{q_i}{p_i}.
$$
Cette formule n'est pas arbitraire : c'est la somme des deux **divergences de Kullback-Leibler** dans les deux sens, car
$$
\underbrace{\sum_i q_i \ln\frac{q_i}{p_i}}_{\mathrm{KL}(q \,\|\, p)} + \underbrace{\sum_i p_i \ln\frac{p_i}{q_i}}_{\mathrm{KL}(p \,\|\, q)} \;=\; \sum_i (q_i - p_i)\ln\frac{q_i}{p_i}.
$$
Le PSI est donc **symétrique**, nul si les deux distributions sont identiques, positif sinon, et chaque terme $(q_i - p_i)\ln(q_i/p_i)$ est lui-même positif (les deux facteurs ont le même signe), ce qui permet de voir **quel intervalle** contribue le plus. Un exemple à la main, avec trois intervalles : la référence a pour parts $(0{,}5\;;\;0{,}3\;;\;0{,}2)$ et la période récente $(0{,}3\;;\;0{,}3\;;\;0{,}4)$.


Les trois termes valent $(0{,}3-0{,}5)\ln(0{,}3/0{,}5) = 0{,}1022$, $0$ (l'intervalle central n'a pas bougé) et $(0{,}4-0{,}2)\ln(0{,}4/0{,}2) = 0{,}1386$, soit un PSI de **0,2408**. Les conventions usuelles (héritées de la notation de crédit, et à prendre comme des **repères** plutôt que des lois) lisent : PSI inférieur à 0,1 : stable ; entre 0,1 et 0,25 : changement modéré, à regarder ; au-delà de 0,25 : changement majeur. Deux précautions : le PSI dépend du **découpage** (10 intervalles ou 20) et il est bruité sur de petits échantillons ; et une variable qui change beaucoup mais qui **pèse peu** dans le modèle compte moins qu'une variable importante qui change un peu.

### Tester un changement de distribution : Kolmogorov-Smirnov

Le **test de Kolmogorov-Smirnov** à deux échantillons (volume I) compare deux **fonctions de répartition empiriques** $F_{\text{ref}}$ et $F_{\text{new}}$. Sa statistique est le plus grand écart vertical entre elles :
$$
D = \sup_x \bigl| F_{\text{ref}}(x) - F_{\text{new}}(x) \bigr|.
$$
Pour la calculer, il suffit de regarder les écarts aux points de l'échantillon réunis.

```python
def ks_stat(a, b):
    tout = np.sort(np.concatenate([a, b]))
    Fa = np.searchsorted(np.sort(a), tout, side="right") / len(a)
    Fb = np.searchsorted(np.sort(b), tout, side="right") / len(b)
    return np.abs(Fa - Fb).max()
```


Sur deux échantillons de 800 valeurs, d'espérances 0 et 0,3 (écart-type 1), notre fonction donne $D = 0{,}1612$, la valeur exacte rendue par `scipy.stats.ks_2samp`, dont la loi sous l'hypothèse « mêmes distributions » donne la valeur-p. La valeur-p dit si l'écart est **statistiquement distinguable du hasard**, pas s'il est **important**. Le contraste est net quand l'échantillon grossit : un décalage minuscule (0,05 écart-type) finit toujours par être « significatif », alors que le PSI, lui, reste négligeable :


```text
 taille de chaque échantillon valeur-p KS    PSI
                          500        0.96 0.0277
                         5000        0.12 0.0032
                        50000       7e-06 0.0015
```

Avec 500 valeurs par échantillon, le test ne voit rien (p = 0,96) ; avec 50 000, il rejette l'égalité ($p \approx 7\times10^{-6}$) pour un écart de 0,0015 de PSI, bien en dessous de tout seuil d'inquiétude. **En production on regarde donc l'ampleur du changement (PSI, écart de moyennes) et on réserve le test aux petits échantillons**, où il évite de réagir au bruit.

### Un mois de production simulé

Reprenons le modèle de version 2 et simulons quatre semaines de 800 clients tirés du réservoir de production, dans deux scénarios, avec une dérive de plus en plus forte d'une semaine à la suivante :

- **dérive des variables** : la population change (plus de clients sensibles aux promotions, moins de clients satisfaits), la relation entre variables et résiliation reste la même ;
- **dérive du concept** : la population est identique, mais une campagne de rétention retient une part croissante des clients que **le modèle signale** (score au moins égal à 0,30) : ils ne résilient finalement pas.

Pour chaque semaine, on mesure le PSI de deux variables par rapport à l'entraînement, la valeur-p du test KS sur la part d'achats en promotion, la précision attendue sans étiquettes (4.3), et — une fois les étiquettes arrivées — la précision réelle et l'AUC.


Dérive des **variables** (la population change) :

```text
 semaine  PSI promo  PSI satisf. KS p (promo)  préc. attendue  préc. réelle   AUC
       1      0.015        0.014        9e-02           0.618         0.655 0.876
       2      0.106        0.074        1e-12           0.609         0.553 0.859
       3      0.345        0.384        4e-45           0.635         0.571 0.869
       4      0.795        0.713       7e-103           0.637         0.552 0.857
```

Dérive du **concept** (la population est la même, la relation change) :

```text
 semaine  PSI promo  PSI satisf. KS p (promo)  préc. attendue  préc. réelle   AUC
       1      0.015        0.014        9e-02           0.618         0.655 0.876
       2      0.023        0.008        8e-01           0.655         0.467 0.847
       3      0.008        0.007        5e-01           0.647         0.269 0.808
       4      0.002        0.006        9e-01           0.633         0.100 0.776
```

Les deux scénarios racontent **des histoires opposées**.

- Quand la **population change**, le PSI de la part d'achats en promotion monte de 0,02 à 0,79 en quatre semaines : l'alarme est franche. Mais **l'AUC ne bouge presque pas** (0,876 puis 0,857) : le modèle a appris une relation qui reste vraie, il l'applique à des clients différents. La dérive est réelle mais **sans conséquence grave** ; ré-entraîner ne s'impose pas, il faut surtout surveiller.
- Quand le **concept change**, le PSI reste à 0,02, 0,0 : **aucune alarme sur les entrées**. L'estimation sans étiquettes annonce toujours une précision d'environ 63 %, alors que la précision réelle de la semaine 4 est de 10 % et que l'AUC passe de 0,876 à 0,776. C'est l'angle mort de la surveillance par les entrées : **la dérive la plus coûteuse est justement celle qu'elle ne voit pas**.


![À gauche : PSI de la part d'achats en promotion pendant quatre semaines pour les deux scénarios, avec les seuils conventionnels de 0,1 et 0,25. Au centre : AUC mesurée une fois les étiquettes arrivées. À droite : distribution de cette variable à l'entraînement et à la semaine 4 du scénario de dérive des variables.](figures/ch04-derive.png)

> 💡 **Intuition.** Les entrées répondent à la question « **les clients ont-ils changé ?** », les étiquettes à la question « **le modèle se trompe-t-il ?** ». Les deux questions sont indépendantes : on peut avoir une réponse oui/non, non/oui, oui/oui ou non/non. D'où la règle : on surveille **les deux**, et l'on ne déclenche une action coûteuse que sur la seconde, ou sur la première **accompagnée** d'un indice d'impact (estimation sans étiquettes, variable importante).

### Que faire d'une dérive avérée ?

Constater la dérive n'est que la moitié du travail. Avant de ré-entraîner, on **diagnostique** : est-ce un **bug** en amont (une unité changée, comme en 4.1) ? Dans ce cas on corrige la source, on ne ré-entraîne pas sur des données fausses. Est-ce un **changement réel** ? Alors seulement, on choisit une politique de ré-entraînement :

| Politique | Principe | Atouts | Limites |
|---|---|---|---|
| **Calendaire** | ré-entraîner chaque mois / trimestre | simple, prévisible | gaspillage si rien n'a changé ; trop lent en cas de rupture |
| **Déclenchée** | quand la performance mesurée ou estimée tombe sous un seuil, ou qu'un PSI majeur touche une variable importante | réagit à ce qui compte | exige une bonne supervision (4.3) et des seuils réglés |
| **Continue** | mise à jour progressive du modèle à chaque nouveau lot | s'adapte vite | risque d'instabilité, plus difficile à tester |

Un ré-entraînement reste un **nouveau modèle** : il repasse par la porte de qualité de 4.6 et par un déploiement progressif (4.2). Testons sur le scénario de dérive du concept : le modèle gelé (appris sur les données d'origine) est comparé à deux versions ré-entraînées avec les étiquettes **arrivées entre-temps** (semaines 2 et 3), toutes évaluées sur la semaine 4.


```text
                              modèle  AUC semaine 4
            gelé (données d'origine)          0.776
ré-entraîné : origine + semaines 2-3          0.891
   ré-entraîné : semaines 2-3 seules          0.909
```

Le ré-entraînement fait remonter l'AUC de 0,776 à 0,891 (ou 0,909 avec les seules semaines récentes). **Il faut pourtant se méfier de ce succès.** Les étiquettes de ces semaines sont celles que **la campagne de rétention a modifiées** : les clients que l'ancien modèle signalait ont été retenus, donc étiquetés « n'a pas résilié ». Le nouveau modèle apprend à reconnaître ce motif : le score moyen des clients que l'ancien modèle signalait passe de 63 % à 48 % sous le nouveau. Il prédit donc **ce qui s'est passé après la campagne**, pas **qui risque de partir en l'absence de campagne**. Utilisé pour cibler la rétention, il cesserait de désigner justement les clients que l'on veut retenir : c'est une **boucle de rétroaction**.

> ⚠️ **Piège.** Quand le modèle déclenche une action qui modifie le résultat, les étiquettes collectées ensuite ne mesurent plus le risque d'origine. Le remède classique est de **réserver au hasard un petit groupe témoin** (par exemple 5 %) qui ne reçoit jamais l'action, et de n'utiliser que lui pour mesurer la performance réelle et ré-entraîner. C'est le raisonnement causal du volume II, chapitre 7 : on cherche l'effet de la relance, et pas seulement la prédiction de l'issue observée.

> 🧭 **En pratique.** Une surveillance complète tient en quatre éléments : un **suivi des entrées** (PSI sur les variables importantes, seuils réglés), un **suivi des scores** (distribution, estimation sans étiquettes), un **suivi des étiquettes** quand elles arrivent (avec un groupe témoin si le modèle agit), et un **processus de décision écrit** (qui est alerté, qui diagnostique, qui décide de ré-entraîner, avec quelles portes de contrôle).

> 📒 **Pour pratiquer.** Le cahier propose de simuler un mois de production en mesurant PSI, KS et AUC (application 4.8), de calculer un PSI à la main et de montrer qu'il se décompose en deux divergences de Kullback-Leibler (exercice 4.10), et d'écrire une politique de ré-entraînement avec groupe témoin (exercices 4.11 et 4.12).


## Bilan du chapitre 4

Vous savez maintenant :

- **rendre un modèle reproductible** : graines, versions, empreinte des données, configuration, et un **pipeline** unique qui enchaîne préparation et modèle ;
- **tester un système de ML** : tests de données (schéma, plages), de comportement (déterminisme, absence de fuite) et de non-régression, qui doivent **bloquer** quelque chose quand ils échouent ;
- **reconnaître le décalage entraînement-service** et en mesurer l'effet : une erreur d'unité ne plante rien, elle dégrade la décision sans bruit ;
- **choisir un mode de service** (lots, ligne, flux, embarqué), raisonner sur la **latence** (centiles) et le **débit** (loi de Little $L=\lambda W$), **sérialiser** (le danger de `pickle`, la parité ONNX) et **exposer** un modèle par une API validée ;
- **introduire une version par paliers** (fantôme, canari, test A/B) avec un routage déterministe, **dimensionner** un test A/B et **revenir en arrière** par un alias ;
- **superviser** quatre couches (système, données, scores, métier), **journaliser** les prédictions, composer avec des **étiquettes tardives**, estimer la performance **sans étiquettes** (et savoir quand cette estimation est aveugle) et **régler des alertes** en connaissant le prix des fausses alarmes ;
- (en option) **orchestrer** un graphe de tâches avec reprises, **idempotence** et rattrapage, **suivre les essais** et gérer un **registre de modèles**, **versionner les données** par leur empreinte, **automatiser la livraison** (CI/CD, conteneurs, Kubernetes), concevoir une **API REST** sûre, et **mesurer la dérive** (PSI, Kolmogorov-Smirnov) en distinguant dérive des variables et dérive du concept.

Le chapitre a mis quelques chiffres sur des idées qui restent souvent abstraites :

| Ce que l'on a vu | Mesure sur la résiliation |
|---|---|
| Un défaut d'unité dans l'entrée du service | l'AUC passe de 0,867 à 0,538 sans aucune erreur visible |
| Combien de clients pour départager deux versions | environ 5 800 clients par groupe pour un écart de 7,9 points de précision |
| Estimation sans étiquettes, dérive du concept | 63 % annoncés, 10 % réels |
| Dérive des variables, quatre semaines | PSI de 0,02 à 0,79, mais AUC de 0,876 à 0,857 |
| Dérive du concept, quatre semaines | PSI toujours sous 0,02, mais AUC de 0,876 à 0,776 |

Quatre leçons dépassent ce chapitre. **Un modèle de ML échoue en silence** : il répond toujours, et les erreurs graves n'ont ni exception ni alarme ; c'est pourquoi on teste les entrées et on supervise les sorties. **Tout ce qui est appris ou calculé doit passer par un seul chemin** : un pipeline unique pour l'entraînement et le service, un registre qui relie une version à ses données et à son code. **Introduire, c'est mesurer, et mesurer demande du temps et des volumes** : un canari achète de l'information au prix du risque, et la performance réelle n'arrive qu'après le délai de l'étiquette. Enfin, **la dérive la plus coûteuse est souvent celle que l'on ne voit pas dans les entrées**, notamment quand le modèle sert à agir et modifie lui-même ce qu'il prédit : le seul remède est de **conserver une mesure indépendante** (un groupe témoin).

> 🧭 **En pratique : liste de contrôle avant la mise en production.**
> 1. L'entraînement se refait à l'identique (graines, versions, hash des données, 4.1).
> 2. Préparation et modèle sont **un seul objet**, testés par un test de parité (4.1).
> 3. Les entrées du service sont **validées** (type et bornes, 4.2) et le contrat de l'API est testé (4.6).
> 4. Le modèle n'est chargé que depuis une source maîtrisée (4.2), l'accès est authentifié et limité en débit (4.6).
> 5. Le déploiement est **progressif** (fantôme, canari) avec un **retour arrière** par alias (4.2, 4.5).
> 6. Chaque prédiction est **journalisée** avec la version du modèle (4.3).
> 7. Des alertes **réglées** sur les entrées, les scores et les erreurs existent, avec un responsable et un runbook (4.3).
> 8. La performance réelle est mesurée **quand les étiquettes arrivent**, avec un **groupe témoin** si le modèle agit (4.3, 4.7).
> 9. Une **politique de ré-entraînement** écrite dit quand, avec quelles données, et par quelle porte de qualité (4.6, 4.7).

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 à 4.9 (batterie de tests, API de scoring, canari avec retour arrière, journal et étiquettes tardives, orchestration avec reprises, suivi MLflow, porte de qualité, mois de production simulé, et une **chaîne complète** de bout en bout) et exercices 4.1 à 4.12.

Le chapitre 5 remonte en amont de tout cela : avant le modèle, il y a **la donnée**, et la qualité de ce qu'elle apporte dépend de **l'ingénierie des données** (extraction, transformation, chargement, tests de qualité). Le chapitre 6 replace ces briques dans les services d'un **fournisseur de cloud** (mise à l'échelle, coûts, sécurité), et le chapitre 7 montre comment présenter un modèle servi, comme celui de ce chapitre, dans une **application** que des non-spécialistes peuvent utiliser.

