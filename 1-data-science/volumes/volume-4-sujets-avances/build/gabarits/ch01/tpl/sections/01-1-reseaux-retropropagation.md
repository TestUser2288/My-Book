## 1.1 Réseaux de neurones et rétropropagation

> 💡 **Intuition.** Un réseau de neurones est une **chaîne de petites machines à calculer**. Chacune prend des nombres, les combine par une somme pondérée, puis les « tord » par une fonction simple. En enchaînant quelques dizaines de ces machines, on obtient une fonction capable de dessiner presque n'importe quelle frontière. La seule difficulté est de **régler les poids** : c'est le rôle de la **rétropropagation**, qui n'est rien d'autre que la règle de dérivation des fonctions composées, appliquée avec méthode.

### 1.1.1 Un neurone, c'est une régression logistique

Un **neurone** reçoit un vecteur $\mathbf x=(x_1,\dots,x_p)$, calcule une somme pondérée et lui applique une fonction d'**activation** $\varphi$ :

$$a=\varphi(z),\qquad z=\mathbf w^\top\mathbf x+b=w_1x_1+\dots+w_px_p+b.$$

Si $\varphi$ est la sigmoïde $\sigma(z)=\frac1{1+e^{-z}}$, ce neurone **est** une régression logistique (volume II, section 2.2 ; volume III, section 2.1) : $a$ est une probabilité. Un neurone seul trace donc une frontière **droite** dans l'espace des variables. Sa puissance vient de l'assemblage.

### 1.1.2 Les fonctions d'activation : pourquoi tordre ?

Pourquoi ne pas se contenter de sommes pondérées ? Parce qu'enchaîner des opérations linéaires donne… une opération linéaire : $W_2(W_1\mathbf x)=(W_2W_1)\mathbf x$. Dix couches sans activation valent **une seule couche**. C'est la non-linéarité de $\varphi$ qui donne de la profondeur au réseau.

Trois activations dominent :

| Activation | Formule | Dérivée | Remarque |
|---|---|---|---|
| **Sigmoïde** | $\sigma(z)=\dfrac1{1+e^{-z}}$ | $\sigma(z)\,(1-\sigma(z))$ | sortie dans $]0,1[$ ; dérivée au plus égale à $0{,}25$ |
| **Tangente hyperbolique** | $\tanh(z)$ | $1-\tanh^2(z)$ | sortie dans $]-1,1[$, centrée ; dérivée au plus égale à $1$ |
| **ReLU** | $\max(0,z)$ | $1$ si $z>0$, $0$ sinon | très simple, ne « sature » pas pour $z>0$ |

```python hide
z = np.linspace(-6, 6, 400)
sig = 1 / (1 + np.exp(-z))
fig, axs = plt.subplots(1, 2, figsize=(10.4, 3.4), sharex=True)
for f, d, nom, col in [(sig, sig * (1 - sig), "sigmoïde", BLEU), (np.tanh(z), 1 - np.tanh(z) ** 2, "tanh", ORANGE), (np.maximum(0, z), (z > 0).astype(float), "ReLU", AQUA)]:
    axs[0].plot(z, f, color=col, lw=2, label=nom); axs[1].plot(z, d, color=col, lw=2, label=nom)
axs[0].set_title("fonction d'activation"); axs[1].set_title("dérivée"); axs[0].set_ylim(-1.3, 2.2); axs[1].set_ylim(-0.05, 1.15)
axs[0].legend(frameon=False, loc="upper left"); axs[0].set_xlabel("z"); axs[1].set_xlabel("z")
style.save(fig, "ch01-activations.png")
NUM("sigmoide_prime_0", 0.25); NUM("sigmoide_prime_5", float(1 / (1 + np.exp(-5)) * (1 - 1 / (1 + np.exp(-5)))))
```

![Les trois activations les plus courantes (à gauche) et leurs dérivées (à droite). La dérivée de la sigmoïde ne dépasse jamais 0,25 et s'écrase vers 0 loin de l'origine ; celle de la ReLU vaut 1 partout où le neurone est actif.](figures/ch01-activations.png)

La dérivée compte autant que la fonction : c'est elle qui transporte le signal d'apprentissage vers l'arrière du réseau. Nous verrons en 1.1.6 pourquoi la faible dérivée de la sigmoïde est un problème.

### 1.1.3 Un réseau, c'est des produits de matrices

Regroupons $m$ neurones en une **couche** : leurs poids forment une matrice $W$ de $m$ lignes (une par neurone) et $p$ colonnes, leurs biais un vecteur $\mathbf b$. La couche calcule d'un coup

$$\mathbf a=\varphi(W\mathbf x+\mathbf b).$$

Un réseau à deux couches cachées et une sortie s'écrit $\hat y=f_3\big(f_2(f_1(\mathbf x))\big)$ avec $f_k(\mathbf u)=\varphi_k(W_k\mathbf u+\mathbf b_k)$. Le **nombre de paramètres** se compte simplement : une couche de $p$ entrées et $m$ sorties en a $m\,(p+1)$. Pour un réseau qui lit une image aplatie de $784$ pixels, avec deux couches cachées de $128$ et $64$ neurones et $10$ sorties (un score par chiffre) :

$$128\times(784+1)+64\times(128+1)+10\times(64+1)=100\,480+8\,256+650=109\,386\ \text{paramètres}.$$

### 1.1.4 La perte : mesurer l'erreur

Entraîner, c'est **minimiser une perte** $L$ qui mesure l'écart entre la prédiction et la réalité.

- **Régression** : l'erreur quadratique $L=\frac12(\hat y-y)^2$.
- **Classification binaire** : l'entropie croisée $L=-\big[y\ln\hat y+(1-y)\ln(1-\hat y)\big]$ (c'est l'opposé de la log-vraisemblance de la régression logistique).
- **Classification à $K$ classes** : on transforme les $K$ scores $z_k$ en probabilités par la fonction **softmax**, $p_k=\dfrac{e^{z_k}}{\sum_j e^{z_j}}$, puis on prend $L=-\ln p_{y}$, l'opposé du logarithme de la probabilité attribuée à la bonne classe.

> 📐 **Un résultat utile : le gradient de softmax + entropie croisée.** Pour la perte $L=-\ln p_y$, on a $\dfrac{\partial L}{\partial z_k}=p_k-\mathbb 1_{k=y}$. Autrement dit : *probabilité prédite moins probabilité réelle (0 ou 1)*. *Preuve.* $L=-z_y+\ln\sum_je^{z_j}$ ; donc $\partial L/\partial z_k=-\mathbb 1_{k=y}+\dfrac{e^{z_k}}{\sum_je^{z_j}}$. $\blacksquare$ Pour la sigmoïde et l'entropie croisée binaire, le résultat est le même : $\partial L/\partial z=\hat y-y$. Cette simplicité explique que l'on associe presque toujours ces deux éléments.

### 1.1.5 La rétropropagation, entièrement à la main

L'entraînement par descente de gradient exige $\partial L/\partial w$ pour **chaque** poids du réseau. Le principe de la **rétropropagation** (*backpropagation*) est la règle de la chaîne : si $L$ dépend de $z_2$, qui dépend de $a_1$, qui dépend de $z_1$, qui dépend de $w$, alors

$$\frac{\partial L}{\partial w}=\frac{\partial L}{\partial z_2}\cdot\frac{\partial z_2}{\partial a_1}\cdot\frac{\partial a_1}{\partial z_1}\cdot\frac{\partial z_1}{\partial w}.$$

On calcule d'abord toutes les valeurs **en avançant** (passe avant), puis on remonte les dérivées **en reculant** (passe arrière), en réutilisant à chaque couche le résultat de la couche suivante. C'est ce qui rend le calcul efficace : un seul aller-retour donne **tous** les gradients.

Prenons le plus petit réseau intéressant : **deux entrées, deux neurones cachés (sigmoïde), un neurone de sortie (sigmoïde)**, avec l'entropie croisée binaire. Les valeurs sont choisies pour que les calculs restent lisibles.

- Entrée : $\mathbf x=(1,\ 2)$, étiquette $y=1$.
- Couche cachée : $W_1=\begin{pmatrix}0{,}1&0{,}3\\0{,}2&-0{,}1\end{pmatrix}$, $\mathbf b_1=(0,\ 0{,}1)$.
- Sortie : $W_2=(0{,}4,\ -0{,}2)$, $b_2=0{,}05$.

```python hide
sig_ = lambda u: 1 / (1 + np.exp(-u))
x_ = np.array([1.0, 2.0]); W1 = np.array([[0.1, 0.3], [0.2, -0.1]]); b1 = np.array([0.0, 0.1]); W2 = np.array([0.4, -0.2]); b2 = 0.05; y_ = 1.0; eta = 0.5
# passe avant
z1 = W1 @ x_ + b1; a1 = sig_(z1); z2 = W2 @ a1 + b2; a2 = sig_(z2); L0 = -(y_ * np.log(a2) + (1 - y_) * np.log(1 - a2))
# passe arrière
d2 = a2 - y_; gW2 = d2 * a1; gb2 = d2
d1 = (W2 * d2) * a1 * (1 - a1); gW1 = np.outer(d1, x_); gb1 = d1
# pas de gradient
W2n, b2n, W1n, b1n = W2 - eta * gW2, b2 - eta * gb2, W1 - eta * gW1, b1 - eta * gb1
a2n = sig_(W2n @ sig_(W1n @ x_ + b1n) + b2n); L1 = -np.log(a2n)
for k, v in dict(z1a=z1[0], z1b=z1[1], a1a=a1[0], a1b=a1[1], z2=z2, a2=a2, L0=L0, d2=d2, gW2a=gW2[0], gW2b=gW2[1], d1a=d1[0], d1b=d1[1],
                 gW1aa=gW1[0, 0], gW1ab=gW1[0, 1], gW1ba=gW1[1, 0], gW1bb=gW1[1, 1], W2a_n=W2n[0], W2b_n=W2n[1], b2_n=b2n,
                 W1aa_n=W1n[0, 0], W1ab_n=W1n[0, 1], W1ba_n=W1n[1, 0], W1bb_n=W1n[1, 1], b1a_n=b1n[0], b1b_n=b1n[1], a2n=a2n, L1=L1,
                 sp1a=a1[0] * (1 - a1[0]), sp1b=a1[1] * (1 - a1[1])).items():
    NUM(k, float(v))
# vérification par différentiation automatique (PyTorch)
t = lambda v: torch.tensor(v, dtype=torch.float64, requires_grad=True)
tW1, tb1, tW2, tb2 = t(W1), t(b1), t(W2), t(b2)
tx = torch.tensor(x_, dtype=torch.float64)
sortie = torch.sigmoid(tW2 @ torch.sigmoid(tW1 @ tx + tb1) + tb2)
(-(torch.log(sortie))).backward()
ok = all(np.allclose(g.grad.numpy(), v) for g, v in [(tW1, gW1), (tb1, gb1), (tW2, gW2), (tb2, gb2)])
NUM("autograd_ok", ok)
# vérification par différences finies sur un poids
def perte_w1(w):
    W = W1.copy(); W[0, 0] = w
    return -np.log(sig_(W2 @ sig_(W @ x_ + b1) + b2))
NUM("diff_finies_ok", bool(abs((perte_w1(0.1 + 1e-6) - perte_w1(0.1 - 1e-6)) / 2e-6 - gW1[0, 0]) < 1e-8))
```

**Passe avant.** On avance, couche par couche :

| Étape | Calcul | Valeur |
|---|---|---|
| $z_1^{(1)}$ | $0{,}1\times1+0{,}3\times2+0$ | ${{z1a|4m}}$ |
| $z_1^{(2)}$ | $0{,}2\times1-0{,}1\times2+0{,}1$ | ${{z1b|4m}}$ |
| $a_1^{(1)}=\sigma(z_1^{(1)})$ | | ${{a1a|4m}}$ |
| $a_1^{(2)}=\sigma(z_1^{(2)})$ | | ${{a1b|4m}}$ |
| $z_2$ | $0{,}4\times{{a1a|4m}}-0{,}2\times{{a1b|4m}}+0{,}05$ | ${{z2|4m}}$ |
| $\hat y=a_2=\sigma(z_2)$ | | ${{a2|4m}}$ |
| Perte $L=-\ln\hat y$ | | ${{L0|4m}}$ |

Le réseau donne une probabilité de {{a2|pc1}} % à la classe 1, alors que la vérité est 1 : la perte vaut {{L0|3}}.

**Passe arrière.** On remonte. À la sortie, d'après le résultat du 1.1.4 (sigmoïde et entropie croisée), $\delta_2=\dfrac{\partial L}{\partial z_2}=\hat y-y={{d2|4m}}$. Les gradients de la couche de sortie s'en déduisent immédiatement, car $z_2=\mathbf w_2^\top\mathbf a_1+b_2$ :

$$\frac{\partial L}{\partial W_2}=\delta_2\,\mathbf a_1=({{gW2a|4m}},\ {{gW2b|4m}}),\qquad\frac{\partial L}{\partial b_2}=\delta_2={{d2|4m}}.$$

Pour la couche cachée, le signal $\delta_2$ **revient** vers chaque neurone caché, multiplié par le poids qui les relie, puis par la dérivée de la sigmoïde $a(1-a)$ (valant ${{sp1a|4m}}$ et ${{sp1b|4m}}$) :

$$\delta_1^{(j)}=\big(w_2^{(j)}\,\delta_2\big)\cdot a_1^{(j)}\big(1-a_1^{(j)}\big)\quad\Longrightarrow\quad\boldsymbol\delta_1=({{d1a|4m}},\ {{d1b|4m}}).$$

Les gradients de $W_1$ sont le produit extérieur $\boldsymbol\delta_1\mathbf x^\top$ :

$$\frac{\partial L}{\partial W_1}=\begin{pmatrix}{{gW1aa|4m}}&{{gW1ab|4m}}\\{{gW1ba|4m}}&{{gW1bb|4m}}\end{pmatrix},\qquad\frac{\partial L}{\partial\mathbf b_1}=\boldsymbol\delta_1.$$

**Un pas de descente de gradient** (pas $\eta=0{,}5$) : chaque paramètre est diminué de $\eta$ fois son gradient. On obtient $W_2=({{W2a_n|4m}},\ {{W2b_n|4m}})$, $b_2={{b2_n|4m}}$ et $W_1=\begin{pmatrix}{{W1aa_n|4m}}&{{W1ab_n|4m}}\\{{W1ba_n|4m}}&{{W1bb_n|4m}}\end{pmatrix}$. Refaisons la passe avant avec ces nouveaux poids : la sortie passe de ${{a2|4m}}$ à ${{a2n|4m}}$ et la **perte de ${{L0|3m}}$ à ${{L1|3m}}$**. Le réseau s'est rapproché de la bonne réponse.

> ✅ **Vérifié deux fois.** Ces gradients ont été recalculés par la **différentiation automatique** de PyTorch : les quatre tenseurs de gradients coïncident avec ceux de la main (`autograd_ok = {{autograd_ok}}`), et une **différence finie** sur un poids (on calcule $\frac{L(w+\varepsilon)-L(w-\varepsilon)}{2\varepsilon}$) donne la même valeur (`{{diff_finies_ok}}`). Cette dernière vérification, la **vérification de gradient**, est le réflexe à avoir quand on écrit une rétropropagation soi-même.

Les bibliothèques (PyTorch, TensorFlow) font exactement ce calcul, sur des millions de paramètres, en construisant automatiquement le graphe des opérations pendant la passe avant. Vous n'écrirez jamais la rétropropagation vous-même en pratique ; mais l'avoir faite une fois explique **tout ce qui suit** : pourquoi les gradients peuvent disparaître, pourquoi l'initialisation compte, pourquoi la ReLU a changé la donne.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.1 (la même rétropropagation en `numpy`, avec vérification de gradient), exercices 1.1 à 1.4.

### 1.1.6 Quand les gradients disparaissent (ou explosent)

Dans la passe arrière, le signal d'erreur est **multiplié** à chaque couche par une dérivée d'activation et par un poids. Avec $L$ couches, il subit environ $L$ multiplications. Pour la sigmoïde, dont la dérivée vaut au plus $0{,}25$, le signal est au plus divisé par 4 à chaque couche : au bout de 10 couches, par plus d'un million. Les premières couches **n'apprennent presque plus** : c'est le problème des **gradients qui disparaissent** (*vanishing gradients*). À l'inverse, des poids trop grands les font **exploser**.

```python hide
def profil(activation, L=10, largeur=128, init=None, graine_=0):
    torch.manual_seed(graine_); couches = []
    for i in range(L):
        lin = nn.Linear(largeur if i else 20, largeur)
        if init == "he": nn.init.kaiming_normal_(lin.weight, nonlinearity="relu"); nn.init.zeros_(lin.bias)
        couches += [lin, activation()]
    m = nn.Sequential(*couches, nn.Linear(largeur, 1)); xx = torch.randn(64, 20); m(xx).pow(2).mean().backward()
    return np.array([m[2 * i].weight.grad.norm().item() for i in range(L)])
profils = {"sigmoïde": profil(nn.Sigmoid), "tanh": profil(nn.Tanh), "ReLU (init. par défaut)": profil(nn.ReLU), "ReLU (init. de He)": profil(nn.ReLU, init="he")}
fig, ax = plt.subplots(figsize=(7.2, 3.6))
for (nom, g), col in zip(profils.items(), [BLEU, ORANGE, AQUA, VIOLET]):
    ax.semilogy(np.arange(1, 11), g, marker="o", ms=4, lw=1.8, color=col, label=nom)
ax.set_xlabel("couche (1 = la plus proche de l'entrée)"); ax.set_ylabel("norme du gradient (échelle log)"); ax.legend(frameon=False, fontsize=8.5)
style.save(fig, "ch01-gradients-profondeur.png")
for nom, cle in [("sigmoïde", "sig"), ("tanh", "tanh"), ("ReLU (init. par défaut)", "relu"), ("ReLU (init. de He)", "relu_he")]:
    NUM("rapport_" + cle, float(profils[nom][0] / profils[nom][-1]))
```

![Norme du gradient dans chacune des 10 couches d'un réseau profond (échelle logarithmique). Avec la sigmoïde, la première couche reçoit un signal environ un milliard de fois plus faible que la dernière.](figures/ch01-gradients-profondeur.png)

Mesurons-le : dans un réseau de 10 couches, le rapport entre le gradient de la première et celui de la dernière couche est de ${{rapport_sig|sci}}$ avec la sigmoïde, ${{rapport_tanh|sci}}$ avec la tanh, ${{rapport_relu|sci}}$ avec la ReLU et l'initialisation par défaut, et seulement ${{rapport_relu_he|2m}}$ avec la ReLU et l'**initialisation de He**. Trois remèdes se sont imposés :

1. **La ReLU** : sa dérivée vaut 1 pour les neurones actifs, le signal n'est plus écrasé.
2. **Une bonne initialisation.** Si les poids sont tirés avec une variance trop faible, le signal s'éteint ; trop grande, il explose. L'initialisation de **Glorot** (variance $\frac{2}{n_{\text{ent}}+n_{\text{sor}}}$, adaptée à la tanh) et celle de **He** (variance $\frac2{n_{\text{ent}}}$, adaptée à la ReLU) maintiennent la variance du signal d'une couche à l'autre.
3. **Les connexions résiduelles** (*skip connections*) des réseaux profonds : on ajoute l'entrée de la couche à sa sortie, $\mathbf a=\mathbf x+f(\mathbf x)$, ce qui laisse au gradient un chemin direct vers l'arrière (voir ResNet, section 1.5).

### 1.1.7 Les optimiseurs : comment descendre

La descente de gradient du volume I (section 1.3.3) fait un pas dans la direction opposée au gradient. En pratique on ne calcule pas le gradient sur toutes les données, mais sur un petit **lot** (*mini-batch*) tiré au hasard : c'est la **descente de gradient stochastique** (SGD), plus rapide et mieux adaptée aux gros jeux de données. Trois variantes se rencontrent partout :

- **SGD** : $w\leftarrow w-\eta\,g$.
- **Avec moment** (*momentum*) : on garde une moyenne glissante des gradients, $v\leftarrow\beta v+g$ puis $w\leftarrow w-\eta v$ ; la « vitesse » lisse les oscillations et accélère dans les vallées étroites.
- **Adam** : il adapte le pas **paramètre par paramètre** en suivant la moyenne des gradients $m$ et celle de leurs carrés $v$ :
$$m\leftarrow\beta_1m+(1-\beta_1)g,\quad v\leftarrow\beta_2v+(1-\beta_2)g^2,\quad w\leftarrow w-\eta\,\frac{\hat m}{\sqrt{\hat v}+\varepsilon},$$
où $\hat m$ et $\hat v$ sont les moyennes corrigées de leur biais initial. Les valeurs usuelles sont $\beta_1=0{,}9$, $\beta_2=0{,}999$.

```python hide
xt_p, xv_p, xte_p = xt.reshape(len(xt), -1), xv.reshape(len(xv), -1), xte.reshape(len(xte), -1)
mlp = lambda: nn.Sequential(nn.Linear(784, 128), nn.ReLU(), nn.Linear(128, 64), nn.ReLU(), nn.Linear(64, 10))
courbes = {}
for nom, f in [("SGD", lambda p: torch.optim.SGD(p, lr=0.05)), ("SGD avec moment", lambda p: torch.optim.SGD(p, lr=0.05, momentum=0.9)), ("Adam", lambda p: torch.optim.Adam(p, lr=1e-3))]:
    graine(0); m_ = mlp(); courbes[nom] = entrainer(m_, xt_p, yt, xv_p, yv, epoques=10, optimiseur=f)
fig, axs = plt.subplots(1, 2, figsize=(10.4, 3.4))
for (nom, h), col in zip(courbes.items(), [BLEU, ORANGE, AQUA]):
    axs[0].plot(range(1, 11), h["perte"], marker="o", ms=3.5, lw=1.8, color=col, label=nom); axs[1].plot(range(1, 11), h["acc_val"], marker="o", ms=3.5, lw=1.8, color=col, label=nom)
axs[0].set_title("perte d'entraînement"); axs[1].set_title("exactitude en validation"); axs[0].set_xlabel("époque"); axs[1].set_xlabel("époque"); axs[0].legend(frameon=False)
style.save(fig, "ch01-optimiseurs.png")
for nom, cle in [("SGD", "sgd"), ("SGD avec moment", "mom"), ("Adam", "adam")]:
    NUM("val_" + cle, courbes[nom]["acc_val"][-1]); NUM("perte1_" + cle, courbes[nom]["perte"][0]); NUM("perte10_" + cle, courbes[nom]["perte"][-1])
```

![Trois optimiseurs sur le même réseau (MNIST, 10 époques, mêmes données et même initialisation). À gauche, la perte d'entraînement ; à droite, l'exactitude en validation.](figures/ch01-optimiseurs.png)

Sur le même réseau, après 10 époques, le SGD simple atteint {{val_sgd|pc1}} % d'exactitude en validation, le SGD avec moment {{val_mom|pc1}} % et Adam {{val_adam|pc1}} %. La leçon n'est pas qu'« Adam est le meilleur » : le SGD avec moment gagne ici, parce que **le pas d'apprentissage a été réglé pour lui** ($0{,}05$) et non pour Adam ($0{,}001$, sa valeur usuelle). Le **pas d'apprentissage** est le réglage le plus influent d'un entraînement : trop petit, on n'avance pas ; trop grand, la perte oscille ou diverge. Adam est populaire parce qu'il est **peu sensible** à ce réglage, pas parce qu'il serait toujours meilleur.

### 1.1.8 La régularisation : empêcher le réseau d'apprendre par cœur

Un réseau a tant de paramètres qu'il peut **mémoriser** un jeu d'entraînement : l'erreur d'entraînement tombe à zéro, l'erreur sur des données nouvelles reste élevée (c'est le surapprentissage du volume III, section 1.3). Quatre moyens de le limiter :

- **La décroissance des poids** (*weight decay*) : on pénalise la taille des poids, comme la régression Ridge (volume II, section 1.5), pour des fonctions plus lisses.
- **Le dropout** : à chaque pas, on **éteint au hasard** une fraction $p$ des neurones. Le réseau ne peut plus compter sur un neurone précis : il doit répartir l'information. À la prédiction, on les rallume tous (avec une mise à l'échelle qui conserve l'espérance, voir l'exercice 1.5 du cahier).
- **L'arrêt précoce** : on suit l'erreur de validation et l'on conserve les poids de la meilleure époque (le même principe que l'arrêt précoce du boosting, volume III, section 2.4.5).
- **La normalisation par lots** (*batch normalization*) : on recentre et on réduit les activations de chaque lot ; cela stabilise l'entraînement et régularise légèrement.

Pour **voir** le surapprentissage, il faut peu de données. Entraînons un réseau large (512-512) sur seulement 1 000 images, et comparons les quatre variantes, **sur trois graines** pour ne pas confondre effet réel et hasard.

```python hide
x1, y1 = xi[:1000].reshape(1000, -1), yi[:1000]; xv2, yv2 = xi[2000:8000].reshape(6000, -1), yi[2000:8000]
large = lambda p=0.0: nn.Sequential(nn.Linear(784, 512), nn.ReLU(), nn.Dropout(p), nn.Linear(512, 512), nn.ReLU(), nn.Dropout(p), nn.Linear(512, 10))
variantes = [("sans régularisation", dict(), 0.0), ("décroissance des poids (0,01)", dict(wd=1e-2), 0.0), ("dropout (0,5)", dict(), 0.5), ("arrêt précoce", dict(patience=5), 0.0)]
resultats = {}
for nom, kw, p in variantes:
    accs = []
    for s in range(3):
        graine(s); m_ = large(p); h = entrainer(m_, x1, y1, xv2, yv2, epoques=60, lr=1e-3, **kw); accs.append((h["acc_train"][-1], h["acc_val"][-1] if "meilleure_epoque" not in h else exactitude(m_, xv2, yv2)))
        if nom == "sans régularisation" and s == 0: h_sans = h
    resultats[nom] = np.array(accs)
for k, (nom, a) in enumerate(resultats.items()):
    NUM(f"reg{k}_train", a[:, 0].mean()); NUM(f"reg{k}_val", a[:, 1].mean()); NUM(f"reg{k}_sd", a[:, 1].std(ddof=1))
list_ = list(resultats.values()); NUM("reg_gain_dropout", 100 * (list_[2][:, 1].mean() - list_[0][:, 1].mean())); NUM("reg_perte_wd", 100 * (list_[0][:, 1].mean() - list_[1][:, 1].mean()))
fig, ax = plt.subplots(figsize=(7.2, 3.5))
ax.plot(range(1, 61), h_sans["acc_train"], color=BLEU, lw=2, label="entraînement"); ax.plot(range(1, 61), h_sans["acc_val"], color=ORANGE, lw=2, label="validation")
ax.set_ylim(0.6, 1.02); ax.set_xlabel("époque"); ax.set_ylabel("exactitude"); ax.legend(frameon=False, loc="lower right"); ax.set_title("1 000 images, aucune régularisation")
style.save(fig, "ch01-surapprentissage.png")
```

![Sans régularisation, l'exactitude d'entraînement atteint 100 % en quelques époques alors que l'exactitude en validation plafonne : l'écart entre les deux courbes mesure le surapprentissage.](figures/ch01-surapprentissage.png)

| Variante (1 000 images, 3 graines) | Exactitude d'entraînement | Exactitude de validation (moyenne ± écart-type) |
|---|---|---|
| sans régularisation | {{reg0_train|pc1}} % | {{reg0_val|pc1}} % ± {{reg0_sd|pc1}} |
| décroissance des poids (0,01) | {{reg1_train|pc1}} % | {{reg1_val|pc1}} % ± {{reg1_sd|pc1}} |
| dropout (0,5) | {{reg2_train|pc1}} % | {{reg2_val|pc1}} % ± {{reg2_sd|pc1}} |
| arrêt précoce | {{reg3_train|pc1}} % | {{reg3_val|pc1}} % ± {{reg3_sd|pc1}} |

Le réseau sans régularisation apprend les 1 000 images par cœur ({{reg0_train|pc1}} % en entraînement) mais n'en généralise que {{reg0_val|pc1}} %. Le **dropout** est ici la variante la plus utile : il gagne {{reg_gain_dropout|1}} point(s) de validation, soit nettement plus que l'écart-type entre graines (de l'ordre de {{reg0_sd|pc1}} à {{reg2_sd|pc1}} point). La décroissance des poids avec ce coefficient (0,01) **fait perdre** {{reg_perte_wd|1}} point : un coefficient trop fort bride le réseau, et il faudrait le régler. L'arrêt précoce ne change rien de mesurable ici. Retenez deux choses : l'effet d'une régularisation dépend de son **réglage** et du problème, et il faut le **mesurer sur plusieurs graines** avant de proclamer qu'une astuce « marche ».

### 1.1.9 Ce que savent faire les réseaux, et ce qu'ils coûtent

Un résultat théorique explique la polyvalence des réseaux : le **théorème d'approximation universelle** (Cybenko, 1989 ; Hornik, 1991) affirme qu'un réseau à **une seule couche cachée** suffisamment large peut approcher n'importe quelle fonction continue sur un domaine borné, avec la précision voulue. Attention à ce qu'il **ne dit pas** : il ne dit pas combien de neurones il faut (possiblement un nombre énorme), ni que la descente de gradient **trouvera** les bons poids, ni que le réseau **généralisera**. C'est un théorème d'existence, pas une recette.

Voyons ce que cela donne sur MNIST, face aux références du volume III. Le réseau 784-128-64-10 de la section 1.1.3 se définit et s'entraîne ainsi :

```python
modele = nn.Sequential(nn.Linear(784, 128), nn.ReLU(), nn.Linear(128, 64), nn.ReLU(), nn.Linear(64, 10))
histo = entrainer(modele, xt_p, yt, xv_p, yv, epoques=25, lr=3e-3)
print(nb_parametres(modele), "paramètres | exactitude sur le test :", round(exactitude(modele, xte_p, yte), 4))
```

La fonction `entrainer` contient la boucle d'entraînement ; nous la détaillerons en 1.4.

```python hide
import lightgbm as lgb
from sklearn.linear_model import LogisticRegression
NUM("mlp_params", nb_parametres(modele)); NUM("mlp_test", exactitude(modele, xte_p, yte)); NUM("mlp_train", histo["acc_train"][-1])
lr_ = LogisticRegression(max_iter=300).fit(xt_p.numpy(), yt.numpy()); NUM("logit_test", lr_.score(xte_p.numpy(), yte.numpy()))
gb_ = lgb.LGBMClassifier(n_estimators=100, num_leaves=31, n_jobs=2, verbose=-1, random_state=0).fit(xt_p.numpy(), yt.numpy()); NUM("lgbm_test", gb_.score(xte_p.numpy(), yte.numpy()))
```

| Modèle (entraîné sur 8 000 images) | Exactitude sur le test |
|---|---|
| Régression logistique (sur les pixels) | {{logit_test|pc1}} % |
| Boosting (LightGBM, 100 arbres) | {{lgbm_test|pc1}} % |
| Réseau dense 784-128-64-10 ({{mlp_params|int}} paramètres) | {{mlp_test|pc1}} % |

> ⚠️ **Le réseau ne « bat » pas le boosting ici.** Un perceptron multicouche entraîné sur 8 000 images obtient à peu près le score d'un boosting bien réglé. L'avantage du deep learning sur les images ne vient pas des couches *denses*, mais des couches **convolutives** de la section suivante, qui exploitent la structure de l'image. Un réseau dense traite les 784 pixels comme 784 colonnes indépendantes, comme le ferait un boosting.

> ✅ **À retenir.**
> - Un **neurone** = somme pondérée + activation ; une **couche** = un produit de matrices ; un réseau = des couches enchaînées ; son nombre de paramètres se compte à la main.
> - La **non-linéarité** des activations est indispensable ; la **ReLU** et une bonne **initialisation** combattent les gradients qui disparaissent.
> - La **rétropropagation** est la règle de la chaîne appliquée de l'arrière vers l'avant ; avec sigmoïde (ou softmax) et entropie croisée, le gradient de sortie vaut simplement « prédiction moins vérité ».
> - **Adam** est peu sensible au pas d'apprentissage ; le **pas** reste le réglage décisif.
> - La régularisation (poids, dropout, arrêt précoce) limite le surapprentissage ; on la juge sur **plusieurs graines**.
> - Le théorème d'approximation universelle est un théorème d'existence : il ne garantit ni l'apprentissage ni la généralisation.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.2 et 1.3, exercice 1.5.
