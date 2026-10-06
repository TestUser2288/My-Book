## 1.2 Réseaux convolutifs

> 💡 **Intuition.** Pour reconnaître un « 7 », il ne faut pas regarder les 784 pixels un par un : il faut repérer **un trait horizontal en haut, puis un trait oblique**, où qu'ils se trouvent dans l'image. Un réseau convolutif encode exactement cette idée : il fait glisser sur l'image un **petit détecteur** (un filtre de $3\times3$ pixels) et note **où** il se déclenche. Le même détecteur sert partout, ce qui réduit le nombre de paramètres de façon spectaculaire.

### 1.2.1 Pourquoi un réseau dense convient mal aux images

Le réseau de la section 1.1 traite l'image comme une liste de 784 nombres. Deux défauts en découlent.

- **Trop de paramètres.** Une seule couche dense de 128 neurones sur une image de $28\times28$ en a $100\,480$. Sur une photographie de $1\,000\times1\,000$ pixels, ce serait **plus de 128 millions** de poids pour la seule première couche.
- **Aucune notion de voisinage.** Pour un réseau dense, mélanger au hasard les 784 pixels (avec la même permutation pour toutes les images) ne change rien à ce qu'il peut apprendre : il ne sait pas que deux pixels voisins se ressemblent. De plus, un chiffre **décalé** de deux pixels devient, pour lui, une image entièrement différente.

Une image a pourtant deux propriétés évidentes : ce qui compte est **local** (un contour est fait de pixels voisins) et **répété** (un contour peut apparaître n'importe où).

### 1.2.2 La convolution, entièrement à la main

Une **convolution** (en réalité une *corrélation croisée*, mais tout le monde dit convolution) fait glisser un **filtre** $K$ de taille $k\times k$ sur l'image. À chaque position, on multiplie terme à terme le filtre et la zone qu'il recouvre, puis on somme.

Prenons une image de $5\times5$ pixels avec un **bord vertical** (sombre à gauche, clair à droite), et un filtre qui répond aux transitions « sombre → clair » :

$$\text{image}=\begin{pmatrix}0&0&1&1&1\\0&0&1&1&1\\0&0&1&1&1\\0&0&1&1&1\\0&0&1&1&1\end{pmatrix},\qquad K=\begin{pmatrix}-1&0&1\\-1&0&1\\-1&0&1\end{pmatrix}.$$

En haut à gauche, le filtre recouvre les colonnes 1 à 3 de l'image, c'est-à-dire les valeurs $(0,0,1)$ sur chaque ligne :
$$(-1\times0+0\times0+1\times1)\times3\ \text{lignes}=3.$$
Une position plus à droite (colonnes 2 à 4, valeurs $(0,1,1)$) donne $(0+0+1)\times3=3$ ; encore une plus à droite (colonnes 3 à 5, valeurs $(1,1,1)$), $(-1+0+1)\times3=0$. En répétant sur les trois lignes de positions, on obtient une **carte de caractéristiques** (*feature map*) de $3\times3$ :

$$\text{sortie}=\begin{pmatrix}3&3&0\\3&3&0\\3&3&0\end{pmatrix}.$$

Le filtre « s'allume » (valeur 3) là où la fenêtre contient le bord, et reste éteint (0) là où l'image est uniforme. Il a **détecté un contour vertical**.

```python hide
import torch.nn.functional as Fn
img = torch.tensor([[0, 0, 1, 1, 1]] * 5, dtype=torch.float32).reshape(1, 1, 5, 5)
K = torch.tensor([[-1, 0, 1]] * 3, dtype=torch.float32).reshape(1, 1, 3, 3)
sortie_conv = Fn.conv2d(img, K)
NUM("conv_ok", bool(torch.equal(sortie_conv[0, 0], torch.tensor([[3.0, 3, 0]] * 3))))
# pooling à la main : carte 4x4, fenêtres 2x2
carte = torch.tensor([[1, 3, 2, 0], [4, 2, 1, 1], [0, 1, 5, 2], [2, 0, 3, 6]], dtype=torch.float32).reshape(1, 1, 4, 4)
pool = Fn.max_pool2d(carte, 2)
NUM("pool_ok", bool(torch.equal(pool[0, 0], torch.tensor([[4.0, 2], [2, 6]]))))
# taille de sortie et rembourrage
NUM("taille_pad", Fn.conv2d(img, K, padding=1).shape[-1]); NUM("taille_stride2", Fn.conv2d(img, K, stride=2).shape[-1])
```

La taille de la sortie se calcule avec une formule à connaître : pour une entrée de largeur $n$, un filtre de largeur $k$, un **rembourrage** (*padding*) de $p$ pixels de zéros de chaque côté et un **pas** (*stride*) $s$,

$$\text{largeur de sortie}=\left\lfloor\frac{n+2p-k}{s}\right\rfloor+1.$$

Sur notre exemple : $n=5,\ k=3$. Sans rembourrage ($p=0,s=1$) : $\frac{5-3}{1}+1=3$. Avec $p=1$ : $\frac{5+2-3}{1}+1=5$, la sortie garde la taille de l'entrée (c'est le rôle du rembourrage). Avec un pas de 2 : $\frac{5-3}{2}+1=2$ (calculs vérifiés par PyTorch : {{taille_pad}} et {{taille_stride2}} de largeur).

Un filtre est un **petit détecteur de motif** ; un réseau convolutif en apprend **plusieurs** par couche (8, 16, 64…), dont les poids sont appris par rétropropagation exactement comme ceux d'un réseau dense. Ils découvrent seuls des détecteurs de contours, de coins, de textures.

### 1.2.3 Le pooling : résumer, tolérer les petits décalages

Après la convolution et la ReLU, on réduit souvent la carte par **pooling** : on découpe la carte en fenêtres de $2\times2$ et l'on ne garde que **le maximum** (*max pooling*) de chaque fenêtre. Sur une carte de $4\times4$ :

$$\begin{pmatrix}1&3&2&0\\4&2&1&1\\0&1&5&2\\2&0&3&6\end{pmatrix}\ \longrightarrow\ \begin{pmatrix}\max(1,3,4,2)&\max(2,0,1,1)\\\max(0,1,2,0)&\max(5,2,3,6)\end{pmatrix}=\begin{pmatrix}4&2\\2&6\end{pmatrix}.$$

La carte est quatre fois plus petite, et la valeur gardée est « le détecteur s'est-il déclenché *quelque part* dans cette zone ? » : un motif décalé d'un pixel donne souvent le même résultat. C'est la première source de **tolérance aux décalages**.

### 1.2.4 Partage des paramètres et champ réceptif

Deux idées font l'efficacité des réseaux convolutifs.

1. **Le partage des paramètres.** Un filtre de $3\times3$ n'a que $9+1=10$ paramètres (9 poids et un biais), quelle que soit la taille de l'image : le **même** filtre est appliqué à toutes les positions.
2. **Le champ réceptif.** Un neurone de la première couche voit une zone de $3\times3$ pixels. Un neurone de la deuxième couche voit $3\times3$ neurones de la première, c'est-à-dire une zone de $5\times5$ pixels. Chaque couche supplémentaire de filtres $3\times3$ élargit le champ de 2 pixels ; un pooling $2\times2$ **double l'écart entre neurones voisins** : les couches suivantes élargissent alors le champ deux fois plus vite. En **empilant** des couches, les neurones profonds voient de grandes zones : les premières couches détectent des contours, les suivantes des formes, les dernières des objets.

### 1.2.5 Un petit réseau convolutif, pas à pas

Construisons un réseau minuscule pour MNIST : une convolution à 8 filtres $3\times3$, une ReLU, un pooling ; une convolution à 16 filtres, une ReLU, un pooling ; puis une couche dense qui produit les 10 scores.

```python
cnn = nn.Sequential(
    nn.Conv2d(1, 8, kernel_size=3), nn.ReLU(), nn.MaxPool2d(2),
    nn.Conv2d(8, 16, kernel_size=3), nn.ReLU(), nn.MaxPool2d(2),
    nn.Flatten(), nn.Linear(16 * 5 * 5, 10))
histo_cnn = entrainer(cnn, xt, yt, xv, yv, epoques=6, lr=3e-3)
x = xte[:1]
for couche in cnn:
    x = couche(x); print(f"{type(couche).__name__:10s} -> {tuple(x.shape)}")
```

Le suivi des **formes** (*shape bookkeeping*) est le premier outil de débogage d'un réseau : à chaque couche, on vérifie que ce qui sort est ce que l'on attendait. Ici, $28\to26$ (filtre $3\times3$ sans rembourrage : $28-3+1$), puis $26\to13$ (pooling), $13\to11$, $11\to5$ (pooling, avec arrondi vers le bas), et enfin $16\times5\times5=400$ valeurs aplaties.

Le nombre de paramètres se compte à la main : la première convolution a $8\times(1\times3\times3+1)=80$ paramètres, la seconde $16\times(8\times3\times3+1)=1\,168$, la couche dense $400\times10+10=4\,010$ : en tout **{{cnn_params|int}}**. À comparer aux **{{mlp_params|int}}** du réseau dense de la section 1.1.

```python hide
NUM("cnn_params", nb_parametres(cnn)); NUM("ratio_params", nb_parametres(modele) / nb_parametres(cnn)); NUM("cnn_test", exactitude(cnn, xte, yte)); NUM("cnn_val_derniere", histo_cnn["acc_val"][-1])
mlp_img = nn.Sequential(nn.Flatten(), *modele)                 # le réseau dense de 1.1, appliqué à des images (N, 1, 28, 28)
NUM("mlp_test_img", exactitude(mlp_img, xte, yte))
# --- figure : filtres appris et cartes de caractéristiques
filtres = cnn[0].weight.detach()[:, 0]
cartes = torch.relu(cnn[0](xte[3:4])).detach()[0]
fig, axs = plt.subplots(3, 8, figsize=(10.4, 4.3))
for k in range(8):
    axs[0, k].imshow(filtres[k], cmap="RdBu_r", vmin=-filtres.abs().max(), vmax=filtres.abs().max()); axs[0, k].axis("off")
    axs[1, k].imshow(cartes[k], cmap="gray_r"); axs[1, k].axis("off")
    axs[2, k].axis("off")
axs[0, 0].set_title("8 filtres 3×3 appris", loc="left", fontsize=9, color=ENCRE2); axs[1, 0].set_title("leurs cartes pour le chiffre ci-dessous (après ReLU)", loc="left", fontsize=9, color=ENCRE2)
axs[2, 3].imshow(xte[3, 0], cmap="gray_r"); axs[2, 3].set_title(f"entrée : un {int(yte[3])}", fontsize=9, color=ENCRE2)
style.save(fig, "ch01-filtres-cartes.png")
```

![Les 8 filtres de la première couche (rouge : poids positifs, bleu : négatifs), et les cartes de caractéristiques qu'ils produisent pour un chiffre de test. Chaque filtre réagit à une orientation ou à une zone différente.](figures/ch01-filtres-cartes.png)

Après 6 époques, ce réseau de {{cnn_params|int}} paramètres atteint **{{cnn_test|pc1}} %** d'exactitude sur le test, contre **{{mlp_test_img|pc1}} %** pour le réseau dense de {{mlp_params|int}} paramètres : **environ {{ratio_params|0}} fois moins de paramètres pour un résultat équivalent ou meilleur**. Les filtres de la figure sont lisibles : certains répondent à des contours obliques, d'autres à des zones sombres ou claires.

### 1.2.6 Robustesse aux décalages et augmentation de données

L'avantage réel du convolutif apparaît quand les images **changent un peu**. Décalons horizontalement les images de test de 0 à 4 pixels, sans réentraîner, et mesurons l'exactitude des deux réseaux.

```python hide
def decaler(x, dx): return torch.roll(x, shifts=dx, dims=3)
dec = {dx: (exactitude(cnn, decaler(xte, dx), yte), exactitude(mlp_img, decaler(xte, dx), yte)) for dx in range(5)}
for dx, (a, b) in dec.items(): NUM(f"dec{dx}_cnn", a); NUM(f"dec{dx}_mlp", b)
fig, ax = plt.subplots(figsize=(6.4, 3.5))
ax.plot(list(dec), [v[0] for v in dec.values()], marker="o", color=BLEU, lw=2, label="réseau convolutif"); ax.plot(list(dec), [v[1] for v in dec.values()], marker="o", color=ORANGE, lw=2, label="réseau dense")
ax.set_xlabel("décalage horizontal des images de test (pixels)"); ax.set_ylabel("exactitude"); ax.legend(frameon=False); ax.set_xticks(range(5))
style.save(fig, "ch01-decalages.png")
# augmentation : chaque image d'entraînement est dupliquée avec deux décalages aléatoires dans [-3, 3] pixels (verticaux et horizontaux)
def augmenter(x, graine_):
    g = torch.Generator().manual_seed(graine_); sortie = x.clone()
    for i in range(len(x)):
        d = torch.randint(-3, 4, (2,), generator=g); sortie[i] = torch.roll(x[i], shifts=(int(d[0]), int(d[1])), dims=(1, 2))
    return sortie
xa = torch.cat([xt, augmenter(xt, 1), augmenter(xt, 2)]); ya = torch.cat([yt, yt, yt])
graine(0); cnn_a = nn.Sequential(nn.Conv2d(1, 8, 3), nn.ReLU(), nn.MaxPool2d(2), nn.Conv2d(8, 16, 3), nn.ReLU(), nn.MaxPool2d(2), nn.Flatten(), nn.Linear(400, 10)); entrainer(cnn_a, xa, ya, xv, yv, epoques=6, lr=3e-3)
graine(0); mlp_a = nn.Sequential(nn.Flatten(), nn.Linear(784, 128), nn.ReLU(), nn.Linear(128, 64), nn.ReLU(), nn.Linear(64, 10)); entrainer(mlp_a, xa, ya, xv, yv, epoques=15, lr=3e-3)
NUM("aug_cnn", exactitude(cnn_a, xte, yte)); NUM("aug_mlp", exactitude(mlp_a, xte, yte)); NUM("aug_cnn_dec3", exactitude(cnn_a, decaler(xte, 3), yte)); NUM("aug_mlp_dec3", exactitude(mlp_a, decaler(xte, 3), yte))
```

![Exactitude des deux réseaux quand on décale les images de test (sans réentraînement). L'exactitude des deux s'effondre, mais celle du réseau dense s'effondre plus vite.](figures/ch01-decalages.png)

Sans décalage, les deux réseaux sont proches ({{dec0_cnn|pc1}} % et {{dec0_mlp|pc1}} %). Avec un décalage de 3 pixels, le réseau convolutif conserve {{dec3_cnn|pc1}} % d'exactitude, le réseau dense seulement {{dec3_mlp|pc1}} %. Ni l'un ni l'autre n'est **invariant** aux décalages (la convolution est *équivariante* : décaler l'entrée décale la carte, mais le pooling et la couche dense finale ne rétablissent qu'une invariance partielle) ; le convolutif y est simplement plus tolérant.

Le remède le plus répandu est l'**augmentation de données** : on fabrique des exemples d'entraînement supplémentaires en appliquant à chaque image des transformations qui **ne changent pas l'étiquette** (décalages, petites rotations, retournements si le sujet s'y prête, changements de luminosité). Ici, nous ajoutons à chaque image deux copies décalées au hasard de $-3$ à $+3$ pixels. Le réseau convolutif passe à **{{aug_cnn|pc1}} %** sur le test (et {{aug_cnn_dec3|pc1}} % sur les images décalées de 3 pixels) ; le réseau dense à {{aug_mlp|pc1}} % ({{aug_mlp_dec3|pc1}} % décalé).

> ⚠️ **L'augmentation doit respecter l'étiquette.** Retourner un « 6 » à l'envers en fait un « 9 » ; décaler un chiffre de quelques pixels n'en change pas le sens. Les transformations d'augmentation se choisissent avec la connaissance du métier, et ne s'appliquent qu'au jeu d'**entraînement**.

### 1.2.7 Les grandes architectures

Les réseaux convolutifs ont connu une succession d'architectures de plus en plus profondes. **LeNet** (1998), pour la reconnaissance de chiffres, ressemble beaucoup au réseau de cette section. **AlexNet** (2012) a remporté une compétition de reconnaissance d'images avec une marge si large qu'elle a lancé la vague actuelle : plus de couches, des ReLU, du dropout et des cartes graphiques. **VGG** (2014) a montré qu'empiler des filtres $3\times3$ suffit. **ResNet** (2015) a introduit les **connexions résiduelles** qui permettent d'entraîner des réseaux de plus de cent couches (nous le réutiliserons en 1.5). Les noms changent ; le principe reste celui de cette section : **des filtres locaux et partagés, empilés**.

> ✅ **À retenir.**
> - Un réseau dense ignore le voisinage des pixels et compte des centaines de milliers de poids ; un **réseau convolutif** exploite le caractère **local** et **répété** des motifs.
> - Une convolution fait glisser un filtre ; la taille de sortie vaut $\lfloor(n+2p-k)/s\rfloor+1$ ; le **pooling** résume et apporte une tolérance aux petits décalages.
> - Le **partage des paramètres** réduit drastiquement leur nombre ; empiler les couches élargit le **champ réceptif**.
> - Le suivi des **formes** à chaque couche est le premier outil de débogage.
> - L'**augmentation de données** (transformations qui préservent l'étiquette) améliore la généralisation, sur l'entraînement seulement.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.4 et 1.5, exercices 1.6 et 1.7.
