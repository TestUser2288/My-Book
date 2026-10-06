## 1.5 ➕ Pour aller plus loin : apprentissage par transfert, vision par ordinateur et OCR

> 🧭 Section optionnelle. Elle montre comment réutiliser un réseau déjà entraîné, panorama les tâches de vision, puis traite un cas concret : lire des factures.

### 1.5.1 Réutiliser un réseau entraîné : le transfert

Entraîner un réseau convolutif profond demande des millions d'images et des jours de calcul. Heureusement, ce qu'il apprend est en grande partie **réutilisable** : les premières couches détectent des contours et des textures utiles pour presque toute image. L'**apprentissage par transfert** (*transfer learning*) consiste à prendre un réseau **pré-entraîné** sur un grand jeu (ici **ResNet-18**, entraîné sur ImageNet, un million d'images de 1 000 catégories), à retirer sa dernière couche (celle qui produit les 1 000 catégories d'ImageNet) et à utiliser ce qui reste comme **extracteur de caractéristiques** : chaque image devient un vecteur de 512 nombres, sur lequel on entraîne un modèle simple.

Deux variantes existent. L'**extraction de caractéristiques** (celle que nous faisons) gèle tout le réseau. Le **réglage fin** (*fine-tuning*) continue l'entraînement de tout ou partie des couches avec un très petit pas d'apprentissage.

```python
import torchvision
resnet = torchvision.models.resnet18(weights=torchvision.models.ResNet18_Weights.IMAGENET1K_V1).eval()
resnet.fc = nn.Identity()                                   # on retire la classification : il reste 512 caractéristiques
moy, ect = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1), torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)

def caracteristiques(x, lot=250):
    sortie = []
    with torch.no_grad():
        for i in range(0, len(x), lot):
            b = nn.functional.interpolate(x[i:i + lot], size=64, mode="bilinear").repeat(1, 3, 1, 1)   # 28×28 gris -> 64×64 couleur
            sortie.append(resnet((b - moy) / ect))                                                    # mêmes statistiques qu'ImageNet
    return torch.cat(sortie).numpy()
```

Les images de MNIST sont en niveaux de gris de $28\times28$ ; ResNet attend des images en couleurs de grande taille, normalisées comme ImageNet. Nous agrandissons donc les chiffres à $64\times64$ et répétons le canal gris trois fois.

> ⚠️ **Un test honnête.** ImageNet ne contient **aucun chiffre manuscrit** : ses caractéristiques ont été apprises sur des chats, des voitures, des outils. Le transfert marche d'autant mieux que la nouvelle tâche **ressemble** à la tâche d'origine. MNIST est donc un cas défavorable, ce qui en fait un test instructif : nous comparons, selon le nombre d'images d'entraînement, trois approches : une régression logistique sur les pixels, un petit réseau convolutif entraîné **de zéro** (celui de la section 1.2) et une régression logistique sur les **caractéristiques de ResNet**.

```python hide
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
t0 = time.time()
F_te = caracteristiques(xte[:1000]); F_tr = caracteristiques(xi[:2000])
tailles = [50, 200, 1000, 2000]; courbe = {"pixels": [], "zéro": [], "ResNet": []}
for n in tailles:
    pix = LogisticRegression(max_iter=500).fit(xi[:n].reshape(n, -1).numpy(), yi[:n].numpy()).score(xte[:1000].reshape(1000, -1).numpy(), yte[:1000].numpy())
    sc = StandardScaler().fit(F_tr[:n])
    tl = LogisticRegression(max_iter=1000, C=0.1).fit(sc.transform(F_tr[:n]), yi[:n].numpy()).score(sc.transform(F_te), yte[:1000].numpy())
    graine(0); cn = nn.Sequential(nn.Conv2d(1, 8, 3), nn.ReLU(), nn.MaxPool2d(2), nn.Conv2d(8, 16, 3), nn.ReLU(), nn.MaxPool2d(2), nn.Flatten(), nn.Linear(400, 10))
    entrainer(cn, xi[:n], yi[:n], xte[1000:1500], yte[1000:1500], epoques=40, lr=3e-3); scr = exactitude(cn, xte[:1000], yte[:1000])
    for cle, v in zip(["pixels", "zéro", "ResNet"], [pix, scr, tl]): courbe[cle].append(v)
    NUM(f"tl_pix_{n}", pix); NUM(f"tl_zero_{n}", scr); NUM(f"tl_res_{n}", tl)
fig, ax = plt.subplots(figsize=(6.4, 3.6))
for (nom, v), coul, lab in zip(courbe.items(), [MUET, BLEU, ORANGE], ["régression logistique sur les pixels", "petit CNN entraîné de zéro", "ResNet-18 gelé + régression logistique"]):
    ax.plot(tailles, v, marker="o", color=coul, lw=2, label=lab)
ax.set_xscale("log"); ax.set_xticks(tailles); ax.set_xticklabels([str(n) for n in tailles]); ax.set_xlabel("images d'entraînement"); ax.set_ylabel("exactitude (1 000 images de test)"); ax.legend(frameon=False, fontsize=8)
style.save(fig, "ch01-transfert.png")
```
<!--sortie-->
```text
NUM tl_pix_50 0.652
NUM tl_zero_50 0.693
NUM tl_res_50 0.636
NUM tl_pix_200 0.8
NUM tl_zero_200 0.84
NUM tl_res_200 0.823
NUM tl_pix_1000 0.868
NUM tl_zero_1000 0.919
NUM tl_res_1000 0.913
NUM tl_pix_2000 0.872
NUM tl_zero_2000 0.943
NUM tl_res_2000 0.925
figure : ch01-transfert.png
```

![Exactitude sur 1 000 images de test selon le nombre d'images d'entraînement, pour trois approches.](figures/ch01-transfert.png)

| Images d'entraînement | Régression logistique (pixels) | Petit CNN de zéro | ResNet-18 gelé + régression |
|---|---|---|---|
| 50 | 65,2 % | 69,3 % | 63,6 % |
| 200 | 80,0 % | 84,0 % | 82,3 % |
| 1 000 | 86,8 % | 91,9 % | 91,3 % |
| 2 000 | 87,2 % | 94,3 % | 92,5 % |

Trois constats, qu'il faut lire avec la prudence d'un seul jeu de 1 000 images de test (une exactitude vaut à environ ±1 point près) :

1. **Avec très peu d'images (50), aucune approche n'est bonne**, et les caractéristiques d'ImageNet ne sont pas meilleures que les pixels bruts (63,6 % contre 65,2 %).
2. **Avec plus d'images, ResNet gelé devance la régression sur les pixels** : de 82,3 % contre 80,0 % à 200 images (un écart encore à peine plus grand que l'incertitude), à 91,3 % contre 86,8 % à 1 000 images. Ses 512 caractéristiques (contours, courbes) sont plus informatives que les pixels isolés, **même sans avoir jamais vu un chiffre**.
3. **Sur ce problème, le petit CNN entraîné de zéro fait aussi bien, voire mieux** (94,3 % contre 92,5 % à 2 000 images). Le transfert n'est pas un gain automatique : sur une tâche simple et éloignée d'ImageNet, un petit réseau bien adapté suffit.

Le transfert est surtout précieux quand la tâche **ressemble** aux données d'origine (photos de produits, de plantes, de documents), que les images sont **peu nombreuses** et que l'on ne peut pas entraîner un grand réseau. Dans ce cas, c'est souvent la meilleure première approche, avant d'envisager le réglage fin. Le temps d'extraction des caractéristiques de ces 3 000 images est de quelques secondes sur un processeur ordinaire.

### 1.5.2 Les tâches de la vision par ordinateur

La classification d'images n'est qu'une tâche parmi d'autres. Chacune a ses architectures et sa mesure d'erreur.

| Tâche | Question | Exemples de modèles | Mesure usuelle |
|---|---|---|---|
| **Classification** | « Que contient l'image ? » | ResNet, EfficientNet, Vision Transformer | exactitude, AUC |
| **Détection** | « Quels objets, et où ? » (boîtes) | YOLO, Faster R-CNN | $\mathrm{IoU}$, précision moyenne (mAP) |
| **Segmentation** | « Quels pixels appartiennent à quoi ? » | U-Net, Mask R-CNN | $\mathrm{IoU}$ moyen par classe |
| **Reconnaissance de texte (OCR)** | « Quels caractères sont écrits ? » | Tesseract, modèles de lecture de documents | taux d'erreur par caractère |
| **Génération** | « Produire une image » | modèles de diffusion | évaluation humaine, métriques de distribution |

La mesure $\mathrm{IoU}$ (*intersection over union*) compare une boîte prédite $P$ à la boîte vraie $V$ : $\mathrm{IoU}=\dfrac{\text{aire}(P\cap V)}{\text{aire}(P\cup V)}$ ; elle vaut 1 pour une boîte parfaite et 0 pour deux boîtes disjointes ; on compte souvent une détection comme correcte à partir de 0,5. Deux boîtes de $10\times10$ décalées de 5 pixels se recouvrent sur $5\times10=50$, leur union est de $100+100-50=150$ : $\mathrm{IoU}=1/3$, une détection **ratée** malgré une position qui paraît proche.

Les **Vision Transformers** (2020), qui découpent l'image en petits carrés traités comme les mots d'une phrase, rivalisent aujourd'hui avec les réseaux convolutifs sur les grands jeux de données ; le mécanisme d'attention qu'ils utilisent est présenté au chapitre 2.

### 1.5.3 Cas concret : lire des factures (OCR)

La boutique reçoit des factures de ses fournisseurs sous forme d'images, et voudrait en extraire le texte. L'**OCR** (*optical character recognition*, reconnaissance optique de caractères) transforme une image de texte en texte. Nous utilisons **Tesseract**, un moteur libre, par l'intermédiaire de la bibliothèque `pytesseract`, sur des factures **fabriquées** avec la bibliothèque de dessin Pillow (texte noir sur fond blanc, cinq lignes : numéro, date, client, article, total). Fabriquer les images nous donne la **vérité** (le texte exact) pour mesurer l'erreur.

```python hide
from PIL import Image, ImageDraw, ImageFont, ImageFilter
police = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
rng_ocr = np.random.default_rng(0)
def facture(i):
    lignes = [f"FACTURE N° 2025-{i:04d}", f"Date : {int(rng_ocr.integers(1, 28)):02d}/{int(rng_ocr.integers(1, 13)):02d}/2025", f"Client : Ville {chr(65 + int(rng_ocr.integers(0, 8)))}",
              f"Article {rng_ocr.choice(['A', 'B', 'C', 'D'])}{int(rng_ocr.integers(1, 9))} x{int(rng_ocr.integers(1, 4))}   {rng_ocr.uniform(5, 120):.2f} €", f"TOTAL TTC : {rng_ocr.uniform(20, 400):.2f} €"]
    im = Image.new("L", (620, 200), 255); dr = ImageDraw.Draw(im)
    for k, l in enumerate(lignes): dr.text((15, 10 + 36 * k), l, font=police, fill=0)
    return im, "\n".join(lignes)
def degrade(im, mode):
    if mode == "propre": return im
    if mode == "bruit": return Image.fromarray(np.clip(np.array(im).astype(float) + rng_ocr.normal(0, 45, (200, 620)), 0, 255).astype(np.uint8))
    if mode == "rotation": return im.rotate(4, fillcolor=255)
    if mode == "basse résolution": return im.resize((155, 50)).resize((620, 200))
    if mode == "flou": return im.filter(ImageFilter.GaussianBlur(2.2))
import pytesseract
image = facture(1)[0]
def lire_facture(im):                                    # on retire les lignes vides que le moteur insère entre les blocs
    return "\n".join(l.strip() for l in pytesseract.image_to_string(im, lang="fra").splitlines() if l.strip())
```

```python
import pytesseract
texte = pytesseract.image_to_string(image, lang="fra")      # image : un objet PIL ; le résultat est une chaîne de caractères
```

**Mesurer la qualité de lecture.** On compare le texte lu au texte vrai par la **distance d'édition de Levenshtein** : le plus petit nombre d'insertions, de suppressions et de substitutions de caractères pour passer d'un texte à l'autre. Divisée par la longueur du texte vrai, elle donne le **taux d'erreur par caractère** (*character error rate*, CER) : 0 pour une lecture parfaite, 0,10 si environ un caractère sur dix est faux.

```python
def levenshtein(a, b):
    ligne = list(range(len(b) + 1))                              # distances de "" à chaque préfixe de b
    for i, ca in enumerate(a, 1):
        precedent, ligne[0] = ligne[0], i
        for j, cb in enumerate(b, 1):
            precedent, ligne[j] = ligne[j], min(ligne[j] + 1, ligne[j - 1] + 1, precedent + (ca != cb))
    return ligne[-1]

cer = lambda lu, vrai: levenshtein(lu, vrai) / len(vrai)
print(levenshtein("FACTURE", "FACTURF"), "erreur sur 7 caractères ->", round(cer("FACTURF", "FACTURE"), 3))
```
<!--sortie-->
```text
1 erreur sur 7 caractères -> 0.143
```

Un exemple de lecture, sur une facture propre (on ignore les lignes vides que le moteur insère entre les blocs de texte, et l'on n'affiche que les lignes qui diffèrent du texte vrai) :

```python hide
from rapidfuzz.distance import Levenshtein
chaines = [("kitten", "sitting"), ("TOTAL TTC", "TOTAL  TTC"), ("", "abc"), ("2025", "2O25")]
NUM("lev_ok", all(levenshtein(a, b) == Levenshtein.distance(a, b) for a, b in chaines))
fact_demo, vrai_demo = facture(1)
lu_demo = lire_facture(fact_demo)
NUM("cer_demo", cer(lu_demo, vrai_demo)); NUM("lev_demo", levenshtein(lu_demo, vrai_demo)); NUM("long_demo", len(vrai_demo))
```
<!--sortie-->
```text
NUM lev_ok True
NUM cer_demo 0.04
NUM lev_demo 4
NUM long_demo 100
```

```python hide-code
for lu_l, vrai_l in zip(lu_demo.split("\n"), vrai_demo.split("\n")):
    if lu_l != vrai_l: print(f"lu   : {lu_l}\nvrai : {vrai_l}")
```
<!--sortie-->
```text
lu   : Article C8 x3 67.52€
vrai : Article C8 x3   67.52 €
lu   : TOTAL TIC : 375.33 €
vrai : TOTAL TTC : 375.33 €
```

Sur cette facture, la distance d'édition est de 4 pour 100 caractères vrais : un CER de **0,040**. Le calcul à la main est identique à celui de la bibliothèque `rapidfuzz` sur les quatre paires de contrôle (vérification : `True`).

**Le prétraitement : aide ou piège ?** Une règle de bon sens veut que l'on **nettoie** l'image avant la lecture. Voici le prétraitement classique : un filtre médian (qui efface le bruit isolé), une **binarisation** (chaque pixel devient noir ou blanc selon un seuil) et un agrandissement ×2.

```python
def pretraiter(image):
    adouci = image.filter(ImageFilter.MedianFilter(3))                       # efface le bruit isolé
    gris = np.array(adouci)
    noir_blanc = ((gris > gris.mean() * 0.8) * 255).astype(np.uint8)         # binarisation par seuil
    return Image.fromarray(noir_blanc).resize((image.width * 2, image.height * 2))
```

Nous le testons sur 8 factures, dans cinq conditions : image propre, avec bruit, inclinée de 4°, en basse résolution (réduite puis agrandie) et floue.

```python hide
data_f = [facture(i) for i in range(1, 9)]
modes = ["propre", "bruit", "rotation", "basse résolution", "flou"]; cles = ["propre", "bruit", "rotation", "basse", "flou"]
t0 = time.time(); ocr = {}
for mode, cle in zip(modes, cles):
    brut, pre = [], []
    for im, vrai in data_f:
        d_ = degrade(im, mode)
        brut.append(cer(lire_facture(d_), vrai)); pre.append(cer(lire_facture(pretraiter(d_)), vrai))
    ocr[mode] = (np.mean(brut), np.mean(pre), int(np.sum(np.array(pre) < np.array(brut))))
    NUM(f"ocr_{cle}_brut", ocr[mode][0]); NUM(f"ocr_{cle}_pre", ocr[mode][1]); NUM(f"ocr_{cle}_mieux", ocr[mode][2])
fig = plt.figure(figsize=(9.2, 4.6)); gs = fig.add_gridspec(2, 3, height_ratios=[0.75, 1.25], hspace=0.12)
for k, (mode, t) in enumerate([("propre", "propre"), ("rotation", "inclinée de 4°"), ("flou", "floue")]):
    ax = fig.add_subplot(gs[0, k]); ax.imshow(degrade(data_f[0][0], mode), cmap="gray", vmin=0, vmax=255); ax.set_title(t, fontsize=9, color=ENCRE2); ax.axis("off")
ax = fig.add_subplot(gs[1, :]); x_ = np.arange(5)
ax.bar(x_ - 0.19, [ocr[m][0] for m in modes], 0.38, color=BLEU, label="image brute"); ax.bar(x_ + 0.19, [ocr[m][1] for m in modes], 0.38, color=ORANGE, label="après prétraitement")
ax.set_xticks(x_); ax.set_xticklabels(modes); ax.set_ylabel("CER moyen"); ax.legend(frameon=False)
style.save(fig, "ch01-ocr.png")
```
<!--sortie-->
```text
NUM ocr_propre_brut 0.03248812381238124
NUM ocr_propre_pre 0.023763126312631264
NUM ocr_propre_mieux 6
NUM ocr_bruit_brut 0.051301505150515056
NUM ocr_bruit_pre 0.046313881388138814
NUM ocr_bruit_mieux 3
NUM ocr_rotation_brut 0.06622624762476248
NUM ocr_rotation_pre 0.057513626362636266
NUM ocr_rotation_mieux 4
NUM ocr_basse_brut 0.15245349534953498
NUM ocr_basse_pre 0.2461926192619262
NUM ocr_basse_mieux 0
NUM ocr_flou_brut 0.22863861386138618
NUM ocr_flou_pre 0.36003375337533755
NUM ocr_flou_mieux 1
figure : ch01-ocr.png
```

![En haut : la même facture propre, inclinée et floue. En bas : taux d'erreur par caractère moyen de Tesseract sur 8 factures, avec et sans prétraitement.](figures/ch01-ocr.png)

| Condition | CER, image brute | CER, après prétraitement | Factures améliorées (sur 8) |
|---|---|---|---|
| Propre | 0,032 | 0,024 | 6 |
| Bruit | 0,051 | 0,046 | 3 |
| Inclinée de 4° | 0,066 | 0,058 | 4 |
| Basse résolution | 0,152 | 0,246 | 0 |
| Floue | 0,229 | 0,360 | 1 |

La leçon est contrintuitive : **le prétraitement n'est pas une recette universelle**. Il aide un peu sur l'image propre et inclinée, mais **dégrade** la lecture quand l'image est floue ou de basse résolution (0,229 → 0,360 et 0,152 → 0,246) : la binarisation par seuil détruit les niveaux de gris dont le moteur avait besoin pour deviner les caractères flous. Avec seulement 8 factures, les écarts fins sont fragiles ; ce qui est solide est le **sens** des grandes différences (le flou et la basse résolution coûtent bien plus cher que le bruit modéré ou l'inclinaison).

> 💡 **Le bon réflexe en OCR.** (1) Mesurez le CER sur des **documents représentatifs** avant et après chaque étape ; (2) corrigez d'abord la **qualité de capture** (résolution, éclairage, cadrage) plutôt que de réparer ensuite ; (3) ajoutez des **contrôles métier** (un total doit être la somme des lignes ; une date doit exister) ; (4) gardez un humain pour les cas douteux. Les erreurs de lecture les plus coûteuses (un `0` lu `O` dans un montant) ne sont pas celles que le CER pénalise le plus.

> ✅ **À retenir.**
> - Le **transfert** réutilise un réseau pré-entraîné comme extracteur de caractéristiques (gelé) ou le **règle finement** ; il est précieux quand les données sont peu nombreuses **et** proches de la tâche d'origine.
> - Il n'est pas gratuit : sur une tâche éloignée et simple (ici, des chiffres), un petit réseau entraîné de zéro peut faire aussi bien.
> - Les tâches de vision (classification, détection, segmentation, OCR) ont chacune leurs modèles et leurs mesures (exactitude, $\mathrm{IoU}$, CER).
> - L'OCR se mesure par le **CER** (distance de Levenshtein) ; le prétraitement doit être **testé**, car il peut dégrader la lecture.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.7, exercice 1.11.
