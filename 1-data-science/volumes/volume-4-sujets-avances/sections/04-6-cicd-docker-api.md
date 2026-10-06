## ➕ 4.6 CI/CD, conteneurs, Kubernetes et API REST

*Section complémentaire : elle prolonge 4.2 (déployer un service) et 4.1 (les tests qui bloquent).*

Savoir entraîner, tester et servir un modèle ne suffit pas : il faut que **chaque modification** (une variable ajoutée, une bibliothèque mise à jour) suive le même chemin automatique jusqu'à la production, sans que quelqu'un exécute à la main une liste de commandes dont il oubliera une étape. Cette section regroupe les quatre outils qui rendent ce chemin fiable : l'**automatisation de la livraison** (CI/CD), les **conteneurs** (Docker), leur **exploitation à l'échelle** (Kubernetes) et la **façon d'exposer** le service (API REST), avec ses bases de sécurité. Les exemples de CI/CD, de Docker, de Kubernetes et de Flask sont donnés **non exécutés** ; ce qui peut s'exécuter ici (porte de qualité, configuration, test de contrat de l'API, authentification) l'est.

### L'intégration et la livraison continues (CI/CD)

- l'**intégration continue** (CI, *continuous integration*) exécute **automatiquement**, à chaque modification du code, les tests de 4.1 : si l'un échoue, la modification est refusée ;
- la **livraison continue** (CD, *continuous delivery*) prépare, à chaque modification validée, un **paquet livrable** (une image de conteneur, une version de modèle) et le déploie, éventuellement après une validation humaine ; le **déploiement continu** retire cette validation.

Le principe est celui d'une chaîne avec des **portes** : on n'avance que si la porte précédente est franchie. Voici un fichier de **GitHub Actions** (un service d'automatisation attaché à un dépôt Git) qui exécute les tests et construit l'image à chaque envoi de code ; il est **non exécuté** ici, et la syntaxe de ces fichiers évolue : **à vérifier dans la documentation** du service.

```yaml noexec
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

```python hide
petit = dict(d, Xtr=d["Xtr"].iloc[:300], ytr=d["ytr"].iloc[:300])
candidat_faible = modele_v1(petit)                                  # entraîné sur 300 clients seulement
lignes = []
for nom, cand in [("boosting (version 2)", v2), ("logistique sur 300 clients", candidat_faible)]:
    ok, auc, verdicts = porte_qualite(cand, v1, Xte, yte)
    lignes.append((nom, round(auc, 3), "publié" if ok else "REFUSÉ", ", ".join(k for k, v in verdicts.items() if not v) or "-"))
    NUM(f"porte_auc{len(lignes) - 1}", round(auc, 3))
assert lignes[0][2] == "publié" and lignes[1][2] == "REFUSÉ"
tab_porte = pd.DataFrame(lignes, columns=["candidat", "AUC test", "décision", "règle(s) non respectée(s)"])
```
<!--sortie-->
```text
NUM porte_auc0 0.893
NUM porte_auc1 0.818
```

Appliquons-la à deux candidats, face au modèle logistique de la version 1 considéré comme « champion » :

```python hide-code
print(tab_porte.to_string(index=False))
```
<!--sortie-->
```text
                  candidat  AUC test décision                      règle(s) non respectée(s)
      boosting (version 2)     0.893   publié                                              -
logistique sur 300 clients     0.818   REFUSÉ AUC ≥ 0.85, pas de régression de plus de 0.005
```

Le boosting (AUC 0,893) franchit la porte ; le modèle appris sur 300 clients seulement (AUC 0,818) est **refusé**, et la chaîne s'arrête sans intervention humaine, avec un message qui dit quelle règle a échoué. Dans une vraie chaîne, ce refus se traduit par un code de sortie non nul du programme, que l'outil de CI reconnaît comme un échec.

> ⚠️ **Piège.** La porte compare au jeu de test. Si l'on enchaîne de nombreux candidats en ne gardant que ceux qui passent, le jeu de test se contamine à la longue (volume III) : on le renouvelle de temps en temps, et l'on garde de côté un jeu **jamais utilisé pour décider**.

### Les conteneurs avec Docker

« Chez moi, ça marche. » Un **conteneur** est la réponse systématique à cette phrase : c'est une boîte qui embarque le programme **et son environnement** (version de Python, bibliothèques, fichiers) et qui s'exécute de la même façon sur n'importe quelle machine disposant du moteur de conteneurs. On le décrit dans un fichier, le **Dockerfile**, qui produit une **image** (le modèle de la boîte) ; chaque lancement de l'image est un **conteneur**. Le Dockerfile du service de 4.2 (**non exécuté** : Docker n'est pas installé ici) :

```dockerfile noexec
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

```python hide
try:
    charger_config({"MODELE_ALIAS": "challenger"})
    msg_manquante = "aucune erreur"
except KeyError as e:
    msg_manquante = f"configuration incomplète : variable {e} absente"
cfg = charger_config({"URL_REGISTRE": "sqlite:///exemple", "SEUIL_ALERTE": "0.25"})
NUM("msg_manquante", msg_manquante); NUM("cfg_alias", cfg["alias"]); NUM("cfg_seuil", cfg["seuil"])
assert msg_manquante.startswith("configuration incomplète") and cfg["alias"] == "champion"
```
<!--sortie-->
```text
NUM msg_manquante configuration incomplète : variable 'URL_REGISTRE' absente
NUM cfg_alias champion
NUM cfg_seuil 0.25
```

Sans l'adresse du registre, la fonction **échoue immédiatement et bruyamment** (« configuration incomplète : variable 'URL_REGISTRE' absente ») plutôt que de démarrer avec une valeur inventée ; avec une configuration complète, les valeurs absentes prennent leur valeur par défaut (alias « champion ») et celles fournies sont lues telles quelles (seuil 0,25).

### Kubernetes : faire tourner beaucoup de conteneurs

Un conteneur ne suffit plus quand le service doit tenir la charge (plusieurs copies, loi de Little de 4.2), survivre à des pannes (relancer un conteneur qui tombe) et se mettre à jour sans interruption. **Kubernetes** est le système qui gère un parc de conteneurs : vous lui **déclarez l'état voulu** (« trois copies de cette image, prêtes avant de recevoir du trafic »), et il agit en permanence pour que l'état réel s'en rapproche. Trois objets suffisent pour comprendre :

- un **pod** : un ou plusieurs conteneurs qui tournent ensemble (en général, un seul) ;
- un **déploiement** (*Deployment*) : le nombre de copies voulues d'un pod, et la façon de les remplacer lors d'une mise à jour (**mise à jour progressive** : un pod à la fois, sans coupure) ;
- un **service** : une adresse stable devant ces copies, qui répartit les requêtes entre celles qui sont prêtes.

Le manifeste ci-dessous (**non exécuté**) déclare le service de scoring : trois copies, des ressources bornées, et deux **sondes** qui interrogent la route `/health` de 4.2. La sonde de **vivacité** redémarre un pod bloqué ; celle de **disponibilité** n'envoie du trafic qu'aux pods dont le modèle est chargé.

```yaml noexec
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

```python hide
L = 200 * 0.05
pods_min = math.ceil(L / 4); pods_marge = math.ceil(1.3 * L / 4)
NUM("L_simultanees", int(L)); NUM("pods_min", pods_min); NUM("pods_marge", pods_marge)
assert (pods_min, pods_marge) == (3, 4)
```
<!--sortie-->
```text
NUM L_simultanees 10
NUM pods_min 3
NUM pods_marge 4
```

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

```python hide
assert all(l[-1] == "oui" for l in rapport)
chemins = sorted(api.get("/openapi.json").json()["paths"])
NUM("chemins_api", ", ".join(chemins))
```
<!--sortie-->
```text
NUM chemins_api /health, /predict, /predict_batch
```

Les six comportements sont conformes, et la description OpenAPI générée contient exactement les routes attendues : /health, /predict, /predict_batch. Écrire ce genre de test **avant** de déployer une nouvelle version garantit qu'un changement interne n'a pas modifié le contrat que d'autres programmes utilisent.

**Flask, l'autre bibliothèque courante.** Beaucoup de services de ML existants sont écrits avec Flask, plus ancienne et plus minimaliste : elle ne valide pas les entrées (il faut le faire à la main) et ne produit pas de description OpenAPI, mais elle est très répandue. Le même service s'y écrit ainsi (**non exécuté**, Flask n'étant pas une dépendance de ce livre) :

```python noexec
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

```python hide
cp = TestClient(protege)
codes = [cp.get("/score").status_code, cp.get("/score", headers={"x-api-key": "mauvaise"}).status_code]
codes += [cp.get("/score", headers={"x-api-key": "cle-de-test"}).status_code for _ in range(4)]
NUM("codes_secu", " ".join(map(str, codes)))
assert codes == [401, 401, 200, 200, 200, 429]
tab_secu = pd.DataFrame({"appel": ["sans clé", "mauvaise clé", "bonne clé (1)", "bonne clé (2)", "bonne clé (3)", "bonne clé (4)"], "code": codes})
```
<!--sortie-->
```text
NUM codes_secu 401 401 200 200 200 429
```

```python hide-code
print(tab_secu.to_string(index=False))
```
<!--sortie-->
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

```python hide
fig, ax = plt.subplots(figsize=(11, 5.0)); ax.set_xlim(0, 11); ax.set_ylim(-0.5, 4.6); ax.axis("off")
etapes = [("Commit\n(code, config)", MUET), ("CI :\ntests de code\net de données", ROUGE), ("Build :\nimage Docker", BLEU), ("Porte :\nmodèle assez\nbon ?", ROUGE), ("Déploiement\ncanari 10 %", ORANGE), ("Production\n100 %", AQUA)]
xs = np.linspace(1.0, 10.0, len(etapes))
for (t, c), x in zip(etapes, xs):
    boite(ax, x, 3.5, 1.45, 1.05, t, c, taille=8.5)
for x1, x2 in zip(xs[:-1], xs[1:]):
    fleche(ax, (x1 + 0.74, 3.5), (x2 - 0.74, 3.5))
fleche(ax, (xs[-2], 2.93), (xs[2], 2.93), ROUGE, rad=-0.35, ls=":")
ax.text(5.5, 1.75, "indicateurs dégradés : retour arrière (alias)", ha="center", fontsize=8.5, color=ROUGE)
ax.text(5.5, 4.4, "Chaque porte peut arrêter la chaîne", ha="center", fontsize=10.5, color=ENCRE)
boite(ax, 2.4, 0.65, 2.6, 0.7, "Service  (adresse stable)", AQUA, taille=8.5, plein=True)
for k, y in enumerate((1.4, 0.65, -0.1)):
    boite(ax, 6.2, y, 1.6, 0.52, f"pod {k + 1}  (prêt)", BLEU, taille=8.5)
    fleche(ax, (3.7, 0.65), (5.4, y), AQUA)
ax.text(8.2, 0.65, "les requêtes sont réparties\nentre les pods prêts", fontsize=8.5, color=ENCRE2, va="center")
style.save(fig, "ch04-cicd.png")
```
<!--sortie-->
```text
figure : ch04-cicd.png
```

![En haut : la chaîne de livraison, avec ses portes (tests, qualité du modèle) qui peuvent chacune arrêter la chaîne, et le retour arrière quand les indicateurs se dégradent après déploiement. En bas : un service Kubernetes qui répartit les requêtes entre plusieurs copies prêtes du conteneur.](figures/ch04-cicd.png)

> 🧭 **En pratique.** On automatise **dans cet ordre** : d'abord les tests (4.1), puis la construction reproductible de l'image, puis le déploiement, et en dernier seulement l'orchestration lourde. Une chaîne simple mais complète vaut mieux qu'une plateforme sophistiquée que personne ne sait réparer.

> 📒 **Pour pratiquer.** Le cahier propose d'écrire une porte de qualité et de la tester sur des candidats (application 4.7), de rédiger le test de contrat d'une API (exercice 4.8) et d'ajouter l'authentification et la limitation de débit à un service (exercice 4.9).
