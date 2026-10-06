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

```python hide
import logging, mlflow, mlflow.sklearn
from mlflow.tracking import MlflowClient
from sklearn.base import clone
from sklearn.model_selection import cross_val_score
logging.getLogger("mlflow").setLevel(logging.ERROR)
# types que skops accepte de recharger, déclarés après revue (il refuse tout objet non déclaré)
APPROUVES = ["numpy.dtype", "functools.partial", "sklearn.utils.validation.check_array",
             "sklearn.ensemble._hist_gradient_boosting.predictor.TreePredictor"]
```

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

```python hide
meilleur = essais.iloc[0]
NUM("meilleur_nom", meilleur["tags.mlflow.runName"]); NUM("auc_cv_meilleur", round(meilleur["metrics.auc_cv"], 3)); NUM("n_essais", len(essais))
assert meilleur["tags.mlflow.runName"].startswith("boosting")
```
<!--sortie-->
```text
NUM meilleur_nom boosting pas=0,05
NUM auc_cv_meilleur 0.891
NUM n_essais 4
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

```python hide
ecart_registre = float(np.abs(en_prod.predict_proba(Xte)[:, 1] - AJUSTES["boosting pas=0,05"].predict_proba(Xte)[:, 1]).max())
NUM("ecart_registre", ecart_registre)
assert ecart_registre < 1e-12
v_champion = reg.get_model_version_by_alias("resiliation", "champion")
run_champion = reg.get_run(v_champion.run_id)
assert run_champion.data.params["hash_donnees"] == hash_fichier("donnees/clients_ml.csv")
NUM("hash_champion", run_champion.data.params["hash_donnees"][:8])
```
<!--sortie-->
```text
NUM ecart_registre 0.0
NUM hash_champion fa48edff
```

Le modèle rechargé par l'alias rend **les mêmes probabilités** que celui de l'essai (écart maximal 0,0). Et à partir de n'importe quelle version du registre, on remonte à l'essai d'origine puis aux données (le hash `fa48edff…` du champion actuel) : c'est la **traçabilité** que 4.1 réclamait. En cas de litige (« pourquoi ce client a-t-il été relancé en mars ? »), on sait quelle version était « champion » ce jour-là, avec quels paramètres, entraînée sur quelles données.

> ⚠️ **Piège.** MLflow a connu plusieurs systèmes de gestion du cycle de vie d'un modèle : les anciens « stades » (*Staging*, *Production*) sont dépréciés au profit des **alias**, utilisés ici. Comme les interfaces de ces outils changent vite, **à vérifier dans la documentation** de la version installée.

### Versionner les données

Git versionne bien le code, mal les gros fichiers (chaque version est stockée en entier, les dépôts gonflent). Pour les données, on utilise le **stockage adressé par le contenu** : un fichier est rangé sous le nom de son hash. Deux fichiers identiques ont le même nom, donc ne sont stockés qu'une fois ; deux versions différentes ont des noms différents. Dans Git, on ne versionne qu'un petit **pointeur** (nom du fichier, hash, taille) ; un pointeur à jour suffit à retrouver exactement la bonne version des données. C'est le principe de **DVC** (*data version control*), dont les commandes sont les suivantes (**non exécutées** : l'outil n'est pas installé ici).

```bash noexec
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

```python hide
magasin = os.path.join(WORK, "magasin")
corrige = os.path.join(WORK, "clients_corrige.csv")
tab = pd.read_csv("donnees/clients_ml.csv"); tab.loc[:4, "age"] = tab.loc[:4, "age"] + 1; tab.to_csv(corrige, index=False)
p1 = stocker("donnees/clients_ml.csv", magasin)
p2 = stocker(corrige, magasin)
p1_bis = stocker("donnees/clients_ml.csv", magasin)
n_objets = sum(len(fs) for _, _, fs in os.walk(magasin))
restaure = os.path.join(WORK, "restaure.csv"); restaurer(p1, magasin, restaure)
assert hash_fichier(restaure, 64) == p1["hash"] == p1_bis["hash"] != p2["hash"] and n_objets == 2
assert p1["hash"].startswith(run_champion.data.params["hash_donnees"])
NUM("n_objets", n_objets); NUM("hash_p1", p1["hash"][:12]); NUM("hash_p2", p2["hash"][:12])
```
<!--sortie-->
```text
NUM n_objets 2
NUM hash_p1 fa48edff3715
NUM hash_p2 041b3c3d9ffb
```

```python hide-code
print(pd.DataFrame([{"version": "actuelle", **{k: (v[:12] if k == "hash" else v) for k, v in p1.items()}},
                    {"version": "corrigée", **{k: (v[:12] if k == "hash" else v) for k, v in p2.items()}}]).to_string(index=False))
```
<!--sortie-->
```text
 version             fichier         hash  taille
actuelle      clients_ml.csv fa48edff3715 1153851
corrigée clients_corrige.csv 041b3c3d9ffb 1153851
```

Trois appels, mais **2 objets** seulement dans le magasin : la seconde sauvegarde de la version actuelle n'a rien ajouté (même hash, même objet). La version actuelle commence par `fa48edff3715` et la version corrigée par `041b3c3d9ffb` ; la restauration d'un pointeur redonne un fichier de même hash, et refuse un objet altéré. Le hash des données enregistré dans les essais MLflow ci-dessus est précisément le début de ce hash : **le registre de modèles et le magasin de données se recoupent**.

```python hide
fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.0), gridspec_kw={"width_ratios": [1.2, 1]})
a.set_xlim(0, 10); a.set_ylim(0, 5); a.axis("off")
boite(a, 1.3, 3.8, 2.2, 0.9, "Données\nhash a1b2…", MUET, taille=9)
boite(a, 1.3, 1.7, 2.2, 0.9, "Code\ncommit 7f3c…", MUET, taille=9)
boite(a, 4.8, 2.75, 2.2, 1.3, "Essai (run)\nparamètres,\nmétriques", BLEU, taille=9)
boite(a, 7.7, 3.8, 2.0, 0.9, "Version\ndu modèle", AQUA, taille=9)
boite(a, 7.7, 1.7, 2.0, 0.9, "alias\n« champion »", ORANGE, taille=9)
fleche(a, (2.45, 3.8), (3.7, 3.05)); fleche(a, (2.45, 1.7), (3.7, 2.45)); fleche(a, (5.95, 3.0), (6.7, 3.7))
fleche(a, (7.7, 2.17), (7.7, 3.33), ORANGE, ls="--")
a.text(5.0, 4.7, "Traçabilité : de l'alias aux données", ha="center", fontsize=10.5, color=ENCRE)
couleurs = [BLEU if n.startswith("logistique") else ORANGE for n in essais["tags.mlflow.runName"]]
b.scatter(essais["metrics.auc_cv"], essais["metrics.auc_test"], c=couleurs, s=60, zorder=3)
for _, r in essais.iterrows():
    b.annotate(r["tags.mlflow.runName"].replace("0,", "0.").replace(",", "."), (r["metrics.auc_cv"], r["metrics.auc_test"]), textcoords="offset points", xytext=(-75, 7) if r["tags.mlflow.runName"] == "logistique C=0,1" else (5, -10), fontsize=7.5, color=ENCRE2)
lim = [essais[["metrics.auc_cv", "metrics.auc_test"]].min().min() - 0.01, essais[["metrics.auc_cv", "metrics.auc_test"]].max().max() + 0.01]
b.plot(lim, lim, color=MUET, ls="--", lw=1); b.set_xlim(lim); b.set_ylim(lim)
b.set_xlabel("AUC en validation croisée (choix)"); b.set_ylabel("AUC de test (contrôle)"); b.set_title("Les quatre essais enregistrés", fontsize=10.5)
fig.tight_layout(); style.save(fig, "ch04-suivi.png")
```
<!--sortie-->
```text
figure : ch04-suivi.png
```

![À gauche : la chaîne de traçabilité, de l'alias « champion » à la version du modèle, à l'essai qui l'a produit, aux données et au code. À droite : AUC en validation croisée (qui sert à choisir) et AUC de test (qui contrôle) des quatre essais ; les deux mesures classent les essais dans le même ordre ; le test est un peu plus élevé, sans doute parce que la validation croisée n'entraîne chaque modèle que sur les deux tiers du jeu d'entraînement.](figures/ch04-suivi.png)

> 📒 **Pour pratiquer.** Le cahier propose de suivre une petite recherche d'hyperparamètres avec MLflow et de promouvoir un modèle par alias (application 4.6), et de montrer qu'un modèle ne peut pas être reproduit sans le hash des données (exercice 4.7).
