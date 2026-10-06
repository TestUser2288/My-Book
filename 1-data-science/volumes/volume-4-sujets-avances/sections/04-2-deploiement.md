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

```python hide
sous = Xte.iloc[:300]
t0 = time.perf_counter(); v1.predict_proba(sous); t_lot = time.perf_counter() - t0
t0 = time.perf_counter()
for i in range(len(sous)):
    v1.predict_proba(sous.iloc[[i]])
t_ligne = time.perf_counter() - t0
assert t_ligne > 10 * t_lot, "le traitement par lots devrait être plus de dix fois plus rapide par client"
```

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

```python hide
modele_onnx = helper.make_model(graphe, opset_imports=[helper.make_opsetid("", 13)]); modele_onnx.ir_version = 8
onnx.checker.check_model(modele_onnx)
chemin_onnx = os.path.join(WORK, "churn_v1.onnx")
with open(chemin_onnx, "wb") as f:
    f.write(modele_onnx.SerializeToString())
session = ort.InferenceSession(chemin_onnx, providers=["CPUExecutionProvider"])
p_onnx = session.run(None, {"Z": Z.astype(np.float32)})[0][:, 0]
ecart_onnx = float(np.abs(p_onnx - v1.predict_proba(Xte)[:, 1]).max())
m_o, e_o = f"{ecart_onnx:.1e}".split("e"); NUM("ecart_onnx_m", m_o); NUM("ecart_onnx_e", int(e_o)); NUM("n_entrees_onnx", Z.shape[1]); NUM("taille_onnx_ko", round(os.path.getsize(chemin_onnx) / 1024, 1))
assert ecart_onnx < 1e-5
```
<!--sortie-->
```text
NUM ecart_onnx_m 1.9
NUM ecart_onnx_e -7
NUM n_entrees_onnx 49
NUM taille_onnx_ko 0.3
```

Le moteur `onnxruntime` charge ce fichier de 0,3 ko **sans scikit-learn** et rend les mêmes probabilités à $1{,}9\times10^{-7}$ près sur les 2 400 clients de test (les calculs sont faits en simple précision, d'où un écart de l'ordre de $10^{-7}$ et non de zéro) : le test de **parité** vu en 4.1 s'applique aussi après conversion. Deux remarques d'honnêteté : ici seule la partie linéaire est exportée, et la préparation (imputation, mise à l'échelle, codage) reste à faire en amont sur les 49 colonnes de $Z$ (ce qui rouvre la porte au décalage de 4.1) ; un convertisseur dédié (`skl2onnx`) exporte le pipeline entier, au prix de limites sur les transformations acceptées, **à vérifier dans sa documentation** pour chaque version.

### Un service de prédiction avec FastAPI

Pour le mode en ligne, le modèle est enveloppé dans un petit **service web**. **FastAPI** est une bibliothèque Python qui expose des fonctions comme des *points d'accès* HTTP et valide automatiquement les entrées à l'aide de **pydantic**, qui décrit chaque champ attendu (type, bornes). L'essentiel du service tient en une dizaine de lignes :

```python noexec
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

```python hide
p_hors_ligne = round(float(v2.predict_proba(Xte.iloc[[0]])[0, 1]), 4)
assert reponse.json()["probabilite"] == p_hors_ligne
lot = [ligne_json(Xte.iloc[i]) for i in range(50)]
rep_lot = api.post("/predict_batch", json=lot).json()["probabilites"]
ecart_api = float(np.abs(np.array(rep_lot) - v2.predict_proba(Xte.iloc[:50])[:, 1]).max())
NUM("ecart_api", round(ecart_api, 4)); NUM("n_lot_api", len(rep_lot))
assert ecart_api < 1e-4
```
<!--sortie-->
```text
NUM ecart_api 0.0
NUM n_lot_api 50
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

```python hide
alias = {"champion": "1.0.0", "canari": "2.0.0"}
ids = np.arange(len(Xpool))
for part in (5, 10, 25):
    servies = np.array([version_servie(i, part, alias) for i in ids])
    NUM(f"part_canari_{part}", round(100 * (servies == "2.0.0").mean(), 1))
stable = all(version_servie(i, 10, alias) == version_servie(i, 10, alias) for i in ids)
assert stable
servies10 = np.array([version_servie(i, 10, alias) for i in ids])
servies25 = np.array([version_servie(i, 25, alias) for i in ids])
NUM("emboites", bool(np.all(servies25[servies10 == "2.0.0"] == "2.0.0")))
alias["canari"] = "1.0.0"                                                         # retour arrière : on change l'alias, pas le code
assert all(version_servie(i, 10, alias) == "1.0.0" for i in ids)
```
<!--sortie-->
```text
NUM part_canari_5 5.2
NUM part_canari_10 10.4
NUM part_canari_25 25.5
NUM emboites True
```

Sur les 2 400 clients du réservoir de production, un palier annoncé à 5, 10 et 25 % envoie réellement 5,2, 10,4 et 25,5 % des clients vers la version 2 : le hachage répartit uniformément, sans état à stocker. Les groupes sont **emboîtés** (tous les clients du palier à 10 % sont encore dans le palier à 25 %), ce qui évite de faire changer d'avis les clients quand on monte en charge.

**Le retour arrière** (*rollback*) est la contrepartie indispensable. Il n'est possible que si deux conditions ont été respectées en amont : les anciennes versions du modèle sont **conservées, immuables et identifiées** (numéro de version, hash du fichier), et le service sélectionne la version par un **alias** (« champion », « canari ») plutôt que par un nom de fichier écrit dans le code. Revenir en arrière revient alors à changer une ligne de configuration (ici `alias["canari"] = "1.0.0"` : le canari pointe de nouveau sur la version 1, et plus aucun client ne reçoit la version 2), sans rien reconstruire. La section 4.5 montre un registre de modèles qui fournit exactement cela.

**Combien de clients faut-il pour trancher ?** Imaginons que la relance soit envoyée aux 10 % de clients les mieux notés, et que l'on compare la **précision** de ce ciblage (la part de clients ciblés qui résilient réellement) pour les deux versions. Sur le réservoir, où nous connaissons toutes les étiquettes, les scores donnent :

```python hide
s1, s2 = v1.predict_proba(Xpool)[:, 1], v2.predict_proba(Xpool)[:, 1]
ypool = d["ypool"]
cible1, cible2 = s1 >= np.quantile(s1, 0.9), s2 >= np.quantile(s2, 0.9)
p1, p2 = ypool[cible1].mean(), ypool[cible2].mean()
recouvre = (cible1 & cible2).sum() / cible1.sum()
NUM("ecart_prec", round(100 * (p2 - p1), 1)); NUM("prec1", round(100 * p1, 1)); NUM("prec2", round(100 * p2, 1)); NUM("recouvrement", round(100 * recouvre))
z_a, z_b = 1.96, 0.84
m_cibles = (z_a + z_b) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2)) / (p2 - p1) ** 2
n_formule = m_cibles / 0.10
NUM("m_cibles", round(m_cibles)); NUM("n_formule", round(n_formule, -2))

rng = np.random.default_rng(7)
def detecte(n, rep=600):
    ok = 0
    for _ in range(rep):
        ia, ib = rng.integers(0, len(ypool), n), rng.integers(0, len(ypool), n)
        ya, yb = ypool[ia][cible1[ia]], ypool[ib][cible2[ib]]
        pa, pb = ya.mean(), yb.mean()
        pp = (ya.sum() + yb.sum()) / (len(ya) + len(yb))
        se = np.sqrt(pp * (1 - pp) * (1 / len(ya) + 1 / len(yb)))
        ok += (pb - pa) / se > 1.96
    return ok / rep
tailles = [500, 1000, 2000, 4000, 8000, 12000]
puissance = [detecte(n) for n in tailles]
for n, pw in zip(tailles, puissance):
    NUM(f"puissance_{n}", round(100 * pw))
```
<!--sortie-->
```text
NUM ecart_prec 7.9
NUM prec1 59.6
NUM prec2 67.5
NUM recouvrement 65
NUM m_cibles 576
NUM n_formule 5800.0
NUM puissance_500 18
NUM puissance_1000 23
NUM puissance_2000 36
NUM puissance_4000 61
NUM puissance_8000 94
NUM puissance_12000 98
```

La version 1 cible avec une précision de 59,6 % et la version 2 de 67,5 % : un avantage réel mais **modeste** (7,9 points), d'autant que les deux versions désignent à 65 % les mêmes clients. Pour l'établir avec 80 % de chances, il faudra un nombre élevé de clients. La formule de dimensionnement d'un test de comparaison de deux proportions (volume I, chapitre 3) est
$$
m \approx \frac{(z_{1-\alpha/2} + z_{1-\beta})^{2}\,\bigl[p_1(1-p_1) + p_2(1-p_2)\bigr]}{(p_2 - p_1)^{2}}
$$
avec $z_{1-\alpha/2} = 1{,}96$ (seuil à 5 %) et $z_{1-\beta} = 0{,}84$ (puissance de 80 %), soit $m \approx 576$ clients **ciblés** par groupe, c'est-à-dire, comme seuls 10 % des clients sont ciblés, environ **5 800 clients par groupe**. La simulation confirme : en tirant des groupes de $n$ clients dans le réservoir et en testant la différence, la version 2 est reconnue meilleure dans 18 % des essais avec 500 clients par groupe, 36 % avec 2 000, 94 % avec 8 000.

```python hide
fig, (a, b) = plt.subplots(1, 2, figsize=(10.8, 4.0), gridspec_kw={"width_ratios": [1.15, 1]})
a.set_xlim(0, 10); a.set_ylim(0, 6); a.axis("off")
boite(a, 1.0, 3.0, 1.5, 1.0, "Requêtes\nclients", MUET)
boite(a, 3.6, 3.0, 1.6, 1.0, "Routeur\n(hash de\nl'identifiant)", BLEU)
boite(a, 7.0, 4.8, 2.9, 1.0, "v1 « champion »\n(90 % du trafic)", BLEU)
boite(a, 7.0, 3.0, 2.9, 1.0, "v2 « canari »\n(10 % du trafic)", ORANGE)
boite(a, 7.0, 1.2, 2.9, 1.0, "v2 en fantôme\n(copie, réponse jetée)", MUET)
fleche(a, (1.8, 3.0), (2.75, 3.0)); fleche(a, (4.4, 3.2), (5.5, 4.7)); fleche(a, (4.4, 3.0), (5.5, 3.0)); fleche(a, (4.4, 2.8), (5.5, 1.3), MUET, ls="--")
a.text(5.0, 5.75, "Trois façons d'introduire une nouvelle version", ha="center", fontsize=10.5, color=ENCRE)
b.plot(tailles, [100 * x for x in puissance], "o-", color=ORANGE, lw=2)
b.axhline(80, color=MUET, ls="--", lw=1); b.axvline(n_formule, color=BLEU, ls=":", lw=1.5)
b.text(n_formule * 1.04, 12, "formule", color=BLEU, fontsize=9, rotation=90)
b.set_xlabel("clients par groupe (n)"); b.set_ylabel("probabilité de conclure (%)"); b.set_ylim(0, 105)
b.set_title("Puissance du test A/B (simulation)", fontsize=10.5)
fig.tight_layout(); style.save(fig, "ch04-deploiement.png")
```
<!--sortie-->
```text
figure : ch04-deploiement.png
```

![À gauche : un routeur envoie une petite part du trafic à la nouvelle version (canari) et une copie à la version fantôme. À droite : probabilité de conclure qu'une version est meilleure selon le nombre de clients par groupe ; la ligne en pointillé indique 80 % et la ligne bleue la taille donnée par la formule.](figures/ch04-deploiement.png)

> 💡 **Intuition.** Le déploiement progressif **achète de l'information** : un canari à 10 % pendant une semaine mesure le même effet qu'un déploiement complet, au prix d'un risque dix fois plus petit. Mais l'information a un prix en **temps** : tant que les étiquettes (ici les résiliations à 90 jours) ne sont pas arrivées, on ne juge que sur des indicateurs indirects (latence, taux d'erreurs, distribution des scores, accord avec la version 1). Le **mode fantôme** donne ces indicateurs sans risque ; le canari ajoute le risque, mais mesure aussi l'effet de la décision.

> ⚠️ **Piège.** Dans un test A/B d'un modèle qui déclenche une action (relance, remise), l'indicateur n'est pas la précision de la prédiction mais **l'effet de l'action sur les clients** (la rétention obtenue). Un modèle qui désigne très bien les clients qui vont partir n'est pas nécessairement celui qui désigne ceux qu'une relance peut retenir : c'est la distinction entre prédiction et effet causal, au cœur du volume II, chapitre 7.

> 📒 **Pour pratiquer.** Le cahier propose de construire et tester l'API de scoring (application 4.2), de convertir un modèle en ONNX et vérifier la parité (exercice 4.3), et de simuler un déploiement canari avec retour arrière (application 4.3).
