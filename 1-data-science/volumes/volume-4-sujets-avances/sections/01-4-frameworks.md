## 1.4 ➕ Pour aller plus loin : les frameworks de deep learning

> 🧭 Section optionnelle. Elle est utile dès que vous écrivez vos propres réseaux ; vous pouvez la sauter si vous voulez seulement comprendre les principes.

Jusqu'ici, nous avons utilisé la fonction `entrainer` (fournie avec le livre) pour ne pas encombrer les explications. Cette section ouvre la boîte : ce qu'un **framework** fournit, à quoi ressemble une boucle d'entraînement, et comment PyTorch se compare à TensorFlow/Keras.

### 1.4.1 Ce que fournit un framework

Un framework de deep learning apporte quatre choses que nous avons faites à la main dans la section 1.1, et qu'il fait **pour vous** :

1. des **tenseurs** (tableaux à plusieurs dimensions), utilisables sur processeur comme sur carte graphique ;
2. la **différentiation automatique** : il enregistre les opérations effectuées et calcule tous les gradients (c'est le `backward()` que nous avons comparé à notre rétropropagation manuelle) ;
3. des **couches et optimiseurs** prêts à l'emploi (`Linear`, `Conv2d`, `LSTM`, `Adam`…) ;
4. de quoi **sauvegarder, charger et déployer** les modèles.

### 1.4.2 PyTorch et TensorFlow/Keras

Les deux frameworks dominants sont **PyTorch** (Meta) et **TensorFlow** avec son interface **Keras** (Google). Ce livre utilise PyTorch, qui s'est imposé dans la recherche et dans la plupart des projets récents.

| | PyTorch | TensorFlow / Keras |
|---|---|---|
| Style | on écrit la boucle d'entraînement ; le graphe est construit **à l'exécution** | `model.fit(...)` fait tout ; le graphe peut être compilé |
| Débogage | comme du Python ordinaire (`print`, point d'arrêt) | plus indirect en mode compilé |
| Souplesse | très grande (architectures inhabituelles, recherche) | grande, mais l'API de haut niveau cadre davantage |
| Déploiement | export ONNX, TorchScript, serveurs dédiés | écosystème de déploiement très complet (mobile, navigateur) |
| Usage typique | recherche, modèles de langage, la plupart des nouveaux projets | systèmes existants en production, déploiement embarqué |

Le même petit réseau s'écrit ainsi en Keras (code **non exécuté** ici : TensorFlow n'est pas installé dans l'environnement du livre) :

```python noexec
import keras
modele = keras.Sequential([keras.layers.Input((784,)), keras.layers.Dense(64, activation="relu"), keras.layers.Dense(10)])
modele.compile(optimizer="adam", loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True), metrics=["accuracy"])
modele.fit(x_train, y_train, epochs=5, batch_size=128, validation_data=(x_val, y_val))
```

> 💡 **Lequel choisir ?** Le choix compte moins que l'on croit : les concepts (tenseurs, gradients, couches, optimiseurs) sont les mêmes, et un réseau écrit dans l'un se traduit dans l'autre en une heure. Choisissez celui que votre équipe maîtrise, ou celui de l'écosystème dont vous avez besoin (modèles pré-entraînés, déploiement).

### 1.4.3 Une boucle d'entraînement lisible

Voici la boucle que `entrainer` exécute, réduite à l'essentiel : à chaque **époque** (un passage sur toutes les données), on mélange les exemples, on les découpe en **lots**, et pour chaque lot on enchaîne quatre gestes : remettre les gradients à zéro, calculer la perte, rétropropager, mettre à jour.

```python
modele = nn.Sequential(nn.Linear(784, 64), nn.ReLU(), nn.Linear(64, 10))
optimiseur = torch.optim.Adam(modele.parameters(), lr=3e-3)
graine(0)
for epoque in range(3):
    ordre = torch.randperm(len(xt_p))                        # on mélange les exemples
    for debut in range(0, len(ordre), 128):
        lot = ordre[debut:debut + 128]
        optimiseur.zero_grad()                               # 1. gradients à zéro
        perte = nn.functional.cross_entropy(modele(xt_p[lot]), yt[lot])   # 2. perte
        perte.backward()                                     # 3. rétropropagation
        optimiseur.step()                                    # 4. mise à jour des poids
    print(f"époque {epoque + 1} : perte du dernier lot = {perte.item():.3f}")
```
<!--sortie-->
```text
époque 1 : perte du dernier lot = 0.557
époque 2 : perte du dernier lot = 0.212
époque 3 : perte du dernier lot = 0.195
```

Les quatre gestes se retrouvent dans **tous** les programmes d'entraînement PyTorch. Deux oublis classiques : omettre `zero_grad()` (les gradients s'**accumulent** d'un lot à l'autre, et l'entraînement diverge) et évaluer le modèle sans `modele.eval()` ni `torch.no_grad()` (le dropout reste actif, et l'on gaspille de la mémoire à mémoriser un graphe inutile).

### 1.4.4 Processeur, carte graphique et reproductibilité

PyTorch place les tenseurs sur un **périphérique** : `cpu` ou `cuda` (une carte graphique NVIDIA). Le code de la section précédente s'exécute sur l'un ou l'autre en déplaçant le modèle et les données avec `.to(périphérique)`. Les cartes graphiques accélèrent massivement les grands réseaux (multiplications de matrices), mais pas les petits : pour les exemples de ce chapitre, un processeur suffit.

```python
print("carte graphique disponible sur cette machine :", torch.cuda.is_available())
peripherique = "cuda" if torch.cuda.is_available() else "cpu"
modele = modele.to(peripherique)           # les données se déplacent de la même façon : x.to(peripherique)
```
<!--sortie-->
```text
carte graphique disponible sur cette machine : False
```

La **reproductibilité** demande de fixer les graines des générateurs aléatoires (`torch.manual_seed`, `np.random.seed`) **avant** de créer le modèle et de mélanger les lots. Vérifions que deux entraînements avec la même graine donnent exactement la même perte, et qu'une autre graine donne un résultat légèrement différent :

```python hide
def perte_finale(g):
    graine(g); m = nn.Sequential(nn.Linear(784, 64), nn.ReLU(), nn.Linear(64, 10)); o = torch.optim.Adam(m.parameters(), lr=3e-3)
    for _ in range(3):
        ordre = torch.randperm(len(xt_p))
        for deb in range(0, len(ordre), 128):
            lot = ordre[deb:deb + 128]; o.zero_grad(); p = nn.functional.cross_entropy(m(xt_p[lot]), yt[lot]); p.backward(); o.step()
    with torch.no_grad(): return nn.functional.cross_entropy(m(xv_p), yv).item()
pa, pb, pc = perte_finale(0), perte_finale(0), perte_finale(1)
NUM("repro_a", f"{pa:.6f}"); NUM("repro_b", f"{pb:.6f}"); NUM("repro_c", f"{pc:.6f}"); NUM("repro_ok", pa == pb)
```
<!--sortie-->
```text
NUM repro_a 0.319800
NUM repro_b 0.319800
NUM repro_c 0.315035
NUM repro_ok True
```

| Entraînement | Perte de validation |
|---|---|
| graine 0, première exécution | 0.319800 |
| graine 0, deuxième exécution | 0.319800 |
| graine 1 | 0.315035 |

Les deux premières lignes sont identiques (égalité exacte : `True`). Sur carte graphique, certaines opérations restent non déterministes (l'ordre des additions varie), et l'égalité n'est alors qu'approchée ; `torch.use_deterministic_algorithms(True)` force le déterminisme, au prix de la vitesse. Dans tous les cas, **le résultat d'un réseau dépend de la graine** : pour comparer deux modèles, il faut plusieurs graines (nous l'avons fait en 1.1.8).

### 1.4.5 Sauvegarder et recharger

Un modèle entraîné se sauvegarde sous la forme de son **dictionnaire d'état** (`state_dict`) : les valeurs de tous ses paramètres. Pour le recharger, on recrée **la même architecture**, puis on y charge les valeurs.

```python
chemin = "modele_ch01.pt"
torch.save(modele.state_dict(), chemin)
copie = nn.Sequential(nn.Linear(784, 64), nn.ReLU(), nn.Linear(64, 10))   # même architecture
copie.load_state_dict(torch.load(chemin)); copie.eval()
print("mêmes sorties après rechargement :", torch.allclose(modele.cpu()(xte_p[:50]), copie(xte_p[:50])))
```
<!--sortie-->
```text
mêmes sorties après rechargement : True
```

```python hide
import os
os.remove(chemin)
```

Pour **déployer** un modèle hors de Python (serveur de production, navigateur, mobile), on l'exporte dans un format neutre comme **ONNX**, lisible par des moteurs d'inférence rapides. Le chapitre 4 de ce volume y revient avec la mise en production.

> ✅ **À retenir.**
> - Un framework fournit **tenseurs, différentiation automatique, couches, optimiseurs** et outils de sauvegarde.
> - La boucle d'entraînement PyTorch tient en quatre gestes : `zero_grad`, perte, `backward`, `step`.
> - Fixer les **graines** rend un entraînement reproductible sur processeur ; comparer des modèles exige plusieurs graines.
> - On sauvegarde le `state_dict`, et on recharge dans la même architecture.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : exercice 1.10.
