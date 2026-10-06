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

```python hide
copie = os.path.join(WORK, "clients_modifie.csv")
shutil.copy("donnees/clients_ml.csv", copie)
with open(copie, "a") as f:
    f.write("\n")                                                  # un seul octet de plus
NUM("hash_orig", hash_fichier("donnees/clients_ml.csv", 8))
NUM("hash_modif", hash_fichier(copie, 8))
assert hash_fichier("donnees/clients_ml.csv") != hash_fichier(copie)

from sklearn.ensemble import RandomForestClassifier
Xn_tr = Xtr[d["num"]].fillna(Xtr[d["num"]].median()); Xn_te = Xte[d["num"]].fillna(Xtr[d["num"]].median())
def foret(graine):
    return RandomForestClassifier(n_estimators=60, max_depth=6, random_state=graine, n_jobs=1).fit(Xn_tr, ytr).predict_proba(Xn_te)[:, 1]
a, b = foret(1), foret(2)                                          # sans graine fixée, la graine est tirée au hasard : c'est comme deux graines différentes
NUM("ecart_sans", round(float(np.abs(a - b).max()), 3))
a, b = foret(0), foret(0)
NUM("ecart_avec", float(np.abs(a - b).max()))
assert float(np.abs(a - b).max()) == 0.0
```
<!--sortie-->
```text
NUM hash_orig fa48edff
NUM hash_modif 86c8ec59
NUM ecart_sans 0.132
NUM ecart_avec 0.0
```

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

```python hide
chemin_v1 = os.path.join(WORK, "churn_v1.joblib")
joblib.dump(v1, chemin_v1)
recharge = joblib.load(chemin_v1)
ecart_rech = float(np.abs(recharge.predict_proba(Xte)[:, 1] - v1.predict_proba(Xte)[:, 1]).max())
NUM("ecart_rechargement", ecart_rech); NUM("taille_v1_ko", round(os.path.getsize(chemin_v1) / 1024))
assert ecart_rech == 0.0
```
<!--sortie-->
```text
NUM ecart_rechargement 0.0
NUM taille_v1_ko 6
```

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

```python hide
def lancer(tests, **ctx):
    for t in tests:
        noms = t.__code__.co_varnames[:t.__code__.co_argcount]
        try:
            t(**{k: v for k, v in ctx.items() if k in noms})
            print(f"  réussi  {t.__name__}")
        except AssertionError as e:
            print(f"  ÉCHEC   {t.__name__} : {e}")

def test_determinisme(modele, lot):
    p = modele.predict_proba(lot)[:, 1]
    assert np.array_equal(p, modele.predict_proba(lot.sample(frac=1, random_state=0).loc[lot.index])[:, 1]), "dépend de l'ordre des lignes"

def test_pas_de_fuite(lot):
    interdits = {"churn_90j", "commandes_apres_cible", "segment_vrai", "depense_6m", "id_client"}
    assert not interdits & set(lot.columns), f"colonne interdite : {interdits & set(lot.columns)}"
```

Le premier passage, sur un lot de test conforme :

```python hide-code
print("lot conforme :")
lancer([test_schema, test_plages, test_determinisme, test_pas_de_fuite, test_non_regression], lot=Xte, modele=v1)
```
<!--sortie-->
```text
lot conforme :
  réussi  test_schema
  réussi  test_plages
  réussi  test_determinisme
  réussi  test_pas_de_fuite
  réussi  test_non_regression
```

Puis le même lot, après un **incident de production** typique : un client en amont a modifié l'export et envoie la part d'achats en promotion en pourcentage (de 0 à 100) au lieu d'une fraction (de 0 à 1), et une colonne interdite s'est glissée dans le fichier.

```python hide-code
lot_casse = Xte.copy()
lot_casse["part_achats_promo"] = lot_casse["part_achats_promo"] * 100
lot_casse["commandes_apres_cible"] = 0
print("lot cassé :")
lancer([test_schema, test_plages, test_determinisme, test_pas_de_fuite], lot=lot_casse, modele=v1)
```
<!--sortie-->
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

```python hide
def evalue(lot):
    p = v1.predict_proba(lot)[:, 1]
    return roc_auc_score(yte, p), p.mean()

lignes = []
for nom, modif in [("aucun défaut", lambda x: x),
                   ("récence en semaines (÷ 7)", lambda x: x.assign(recence_jours=x["recence_jours"] / 7)),
                   ("part promo en % (× 100)", lambda x: x.assign(part_achats_promo=x["part_achats_promo"] * 100))]:
    auc, moy = evalue(modif(Xte))
    lignes.append((nom, auc, moy))
skew = pd.DataFrame(lignes, columns=["entrée envoyée au service", "AUC", "probabilité moyenne"])
for k, (nom, auc, moy) in enumerate(lignes):
    NUM(f"skew_auc{k}", round(auc, 3)); NUM(f"skew_moy{k}", round(100 * moy, 1))
NUM("taux_test", round(100 * yte.mean(), 1))
```
<!--sortie-->
```text
NUM skew_auc0 0.867
NUM skew_moy0 13.1
NUM skew_auc1 0.837
NUM skew_moy1 6.7
NUM skew_auc2 0.538
NUM skew_moy2 89.7
NUM taux_test 14.0
```

```python hide-code
print(skew.round(3).to_string(index=False))
```
<!--sortie-->
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

```python hide
fig, ax = plt.subplots(figsize=(10.4, 3.9)); ax.set_xlim(0, 10.4); ax.set_ylim(0, 3.9); ax.axis("off")
noeuds = {"don": (1.0, 2.9, "Données\nbrutes", MUET), "val": (3.0, 2.9, "Validation\n(tests de\ndonnées)", ROUGE), "var": (5.0, 2.9, "Variables\n(pipeline)", BLEU),
          "ent": (7.0, 2.9, "Entraînement", BLEU), "eva": (9.0, 2.9, "Évaluation\n(non-\nrégression)", ROUGE),
          "cfg": (7.0, 0.9, "Configuration\n+ graine", MUET), "reg": (9.0, 0.9, "Registre :\nmodèle\nversionné", AQUA)}
for k, (x, y, t, c) in noeuds.items():
    boite(ax, x, y, 1.55, 1.1, t, c)
for a, b in [("don", "val"), ("val", "var"), ("var", "ent"), ("ent", "eva")]:
    fleche(ax, (noeuds[a][0] + 0.8, noeuds[a][1]), (noeuds[b][0] - 0.8, noeuds[b][1]))
fleche(ax, (7.0, 1.5), (7.0, 2.33), MUET, ls="--")
fleche(ax, (9.0, 2.33), (9.0, 1.47), AQUA)
ax.text(8.9, 1.9, "réussi seulement", fontsize=8.5, color=AQUA, ha="right")
fleche(ax, (3.0, 2.33), (3.0, 1.5), ROUGE, ls=":")
ax.text(3.0, 1.2, "test de données en échec :\narrêt de la chaîne et alerte", fontsize=8.5, color=ROUGE, ha="center", va="center")
ax.text(5.2, 3.75, "Un pipeline d'entraînement est un graphe : chaque flèche est une dépendance", fontsize=10.5, ha="center", color=ENCRE)
style.save(fig, "ch04-pipeline-dag.png")
```
<!--sortie-->
```text
figure : ch04-pipeline-dag.png
```

![Le pipeline d'entraînement comme graphe : deux étapes de contrôle (rouge) peuvent arrêter la chaîne, la configuration alimente l'entraînement, et seul un modèle qui passe l'évaluation arrive au registre.](figures/ch04-pipeline-dag.png)

> 📒 **Pour pratiquer.** Le cahier propose d'écrire une batterie de tests de données et de modèle (application 4.1) et de reproduire un décalage entraînement-service pas à pas (exercices 4.1 et 4.2).
