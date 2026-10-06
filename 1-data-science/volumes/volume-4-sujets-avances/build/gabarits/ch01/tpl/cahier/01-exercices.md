# Chapitre 1 : Deep learning — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 1 du livre (réseaux de neurones, convolutifs, récurrents, frameworks, transfert et OCR, tabulaire). Les **applications** reprennent, avec leur code, des expériences dont le livre ne montre que les résultats ; les **exercices** se font à la main ou avec quelques lignes ; les **corrigés** des exercices sont à la fin.

## Préparation

Toutes les applications utilisent le sous-ensemble de MNIST et les fichiers du dossier `donnees/`, ainsi que quelques fonctions utilitaires fournies avec le livre (`build/outils_ch01.py`) : `graine`, `charger_mnist`, `nb_parametres`, `exactitude` et `entrainer` (la boucle d'entraînement de la section 1.4.3 du livre, avec arrêt précoce optionnel).

```python
import sys, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, torch, torch.nn as nn
sys.path.insert(0, "build")
from outils_ch01 import graine, charger_mnist, nb_parametres, exactitude, entrainer

graine(0)
xi, yi, xte, yte = charger_mnist()                 # images (N, 1, 28, 28), valeurs dans [0, 1]
xt, yt, xv, yv = xi[:4000], yi[:4000], xi[8000:9000], yi[8000:9000]
xt_p, xv_p, xte_p = xt.flatten(1), xv.flatten(1), xte.flatten(1)   # versions aplaties (N, 784) pour les réseaux denses
print(xt.shape, xv.shape, xte.shape)
```

```python hide
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import style
from style import AQUA, BLEU, ENCRE2, MUET, ORANGE, ROUGE, VIOLET
style.setup()
def NUM(cle, valeur):
    print("NUM", cle, valeur)
```

## Applications

### Application 1.1 — La rétropropagation sur un nouveau réseau (section 1.1.5)

**Énoncé.** Écrivez en `numpy` une fonction qui calcule, pour un réseau « deux entrées, $n$ neurones cachés (tanh), une sortie (sigmoïde) » avec l'entropie croisée binaire, la perte **et tous les gradients**. Vérifiez-la par **différences finies** sur chaque paramètre, puis faites un pas de descente de gradient et constatez que la perte diminue. Entrée $\mathbf x=(0{,}5,\,-1)$, étiquette $y=0$, trois neurones cachés, poids tirés au hasard avec la graine 0.

```python
def avant_arriere(theta, x, y):
    W1, b1, W2, b2 = theta[:6].reshape(3, 2), theta[6:9], theta[9:12], theta[12]
    a1 = np.tanh(W1 @ x + b1)                          # couche cachée
    p = 1 / (1 + np.exp(-(W2 @ a1 + b2)))              # sortie : probabilité de la classe 1
    perte = -(y * np.log(p) + (1 - y) * np.log(1 - p))
    d2 = p - y                                         # gradient en sortie : prédiction moins vérité
    d1 = (W2 * d2) * (1 - a1 ** 2)                     # retour vers la couche cachée (dérivée de tanh)
    return perte, np.concatenate([np.outer(d1, x).ravel(), d1, d2 * a1, [d2]])   # gradient de tous les paramètres

theta = np.random.default_rng(0).normal(0, 0.5, 13)    # 6 poids cachés, 3 biais, 3 poids de sortie, 1 biais
x, y = np.array([0.5, -1.0]), 0.0
perte, grad = avant_arriere(theta, x, y)

ecart = 0.0                                            # différences finies, un paramètre à la fois
for k in range(13):
    h = np.zeros(13); h[k] = 1e-6
    numerique = (avant_arriere(theta + h, x, y)[0] - avant_arriere(theta - h, x, y)[0]) / 2e-6
    ecart = max(ecart, abs(numerique - grad[k]))
print("perte :", round(perte, 4), "| écart maximal avec les différences finies :", f"{ecart:.1e}")
```

```python hide
NUM("c_a11_perte", perte); NUM("c_a11_ecart", ecart)
NUM("c_a11_perte2", avant_arriere(theta - 0.5 * grad, x, y)[0])
```

**Corrigé.** Les gradients de la fonction concordent avec les différences finies à {{c_a11_ecart|sci}} près : la rétropropagation est correcte. Le point à retenir est la **structure** : le signal d'erreur `d2 = p - y` remonte à la couche cachée en étant multiplié par les poids de sortie et par la dérivée de l'activation ($1-a^2$ pour la tanh). Un pas de descente de gradient (pas de 0,5) fait passer la perte de {{c_a11_perte|4}} à {{c_a11_perte2|4}}.

### Application 1.2 — Optimiseurs et pas d'apprentissage (section 1.1.7)

**Énoncé.** Entraînez le même réseau 784-64-10 pendant 6 époques avec le SGD simple, le SGD avec moment et Adam, pour quatre valeurs du pas d'apprentissage ($10^{-3}$, $10^{-2}$, $10^{-1}$ et $3\cdot10^{-1}$ pour le SGD ; $10^{-4}$, $10^{-3}$, $10^{-2}$ et $10^{-1}$ pour Adam). Quel optimiseur est le plus sensible au pas ?

```python
def essai(fabrique_opt):
    graine(0)
    m = nn.Sequential(nn.Linear(784, 64), nn.ReLU(), nn.Linear(64, 10))
    return entrainer(m, xt_p, yt, xv_p, yv, epoques=6, optimiseur=fabrique_opt)["acc_val"][-1]

pas_sgd, pas_adam = [1e-3, 1e-2, 1e-1, 3e-1], [1e-4, 1e-3, 1e-2, 1e-1]
tab = pd.DataFrame({
    "pas SGD": [f"{l:g}" for l in pas_sgd], "SGD": [essai(lambda p, l=l: torch.optim.SGD(p, lr=l)) for l in pas_sgd],
    "SGD + moment": [essai(lambda p, l=l: torch.optim.SGD(p, lr=l, momentum=0.9)) for l in pas_sgd],
    "pas Adam": [f"{l:g}" for l in pas_adam], "Adam": [essai(lambda p, l=l: torch.optim.Adam(p, lr=l)) for l in pas_adam]})
print(tab.round(3).to_string(index=False))
```

```python hide
for cle, col in [("sgd", "SGD"), ("mom", "SGD + moment"), ("adam", "Adam")]:
    NUM(f"c_a12_{cle}_min", tab[col].min()); NUM(f"c_a12_{cle}_max", tab[col].max())
```

**Corrigé.** L'exactitude de validation varie selon le pas de {{c_a12_sgd_min|pc1}} % à {{c_a12_sgd_max|pc1}} % pour le SGD simple, de {{c_a12_mom_min|pc1}} % à {{c_a12_mom_max|pc1}} % pour le SGD avec moment, et de {{c_a12_adam_min|pc1}} % à {{c_a12_adam_max|pc1}} % pour Adam. Le **SGD simple** est le plus sensible : avec un pas trop petit ($10^{-3}$), il n'a presque rien appris en 6 époques, et il n'atteint son meilleur niveau qu'avec le plus grand pas essayé. Le **moment** accélère nettement l'apprentissage aux petits pas. **Adam** donne de bons résultats sur une plage plus large (de $10^{-3}$ à $10^{-2}$ ici), mais il n'est **pas insensible** : un pas de $10^{-4}$ est trop lent pour 6 époques, et un pas de $10^{-1}$ dégrade la validation. Retenez : Adam rend le réglage du pas **moins délicat**, pas inutile.

### Application 1.3 — Arrêt précoce et pénalité sur les poids (section 1.1.8)

**Énoncé.** Sur seulement 1 000 images d'entraînement, entraînez un réseau 784-256-128-10 pendant 40 époques, avec (a) rien, (b) une pénalité de poids (`weight_decay`), (c) un arrêt précoce (patience 5). Comparez l'exactitude d'entraînement, de validation et de test.

```python
def modele_grand():
    graine(0); return nn.Sequential(nn.Linear(784, 256), nn.ReLU(), nn.Linear(256, 128), nn.ReLU(), nn.Linear(128, 10))

resultats = {}
for nom, args in {"rien": {}, "pénalité de poids": {"wd": 1e-3}, "arrêt précoce": {"patience": 5}}.items():
    m = modele_grand(); h = entrainer(m, xt_p[:1000], yt[:1000], xv_p, yv, epoques=40, lr=1e-3, **args)
    resultats[nom] = (len(h["perte"]), h["acc_train"][-1], exactitude(m, xv_p, yv), exactitude(m, xte_p, yte))
print(pd.DataFrame(resultats, index=["époques", "train", "val", "test"]).T.round(3).to_string())
```

```python hide
for cle, nom in [("rien", "rien"), ("wd", "pénalité de poids"), ("es", "arrêt précoce")]:
    for j, c in enumerate(["ep", "tr", "va", "te"]): NUM(f"c_a13_{cle}_{c}", resultats[nom][j])
```

**Corrigé.** Sans rien, le réseau mémorise les 1 000 images ({{c_a13_rien_tr|pc1}} % en entraînement) et obtient {{c_a13_rien_te|pc1}} % au test. La pénalité de poids donne {{c_a13_wd_te|pc1}} % ; l'arrêt précoce, qui s'arrête après {{c_a13_es_ep|0}} époques, {{c_a13_es_te|pc1}} %. Les écarts entre ces trois lignes sont de l'ordre du **bruit d'une graine** (voir la section 1.1.8 : plusieurs graines sont nécessaires pour conclure) ; l'enseignement robuste est que l'écart entre entraînement et test **montre** le surapprentissage, et que l'arrêt précoce économise du calcul.

### Application 1.4 — Une convolution écrite à la main (section 1.2.2)

**Énoncé.** Écrivez avec deux boucles une convolution $3\times3$ sans rembourrage ; vérifiez-la contre `torch.nn.functional.conv2d`, puis appliquez à un vrai chiffre de MNIST le filtre de détection des contours verticaux de la section 1.2.2 et celui des contours horizontaux (le transposé).

```python
import torch.nn.functional as Fn
def convolution(image, K):
    k = K.shape[0]; n = image.shape[0] - k + 1
    sortie = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            sortie[i, j] = (image[i:i + k, j:j + k] * K).sum()
    return sortie

V = np.array([[-1, 0, 1]] * 3, dtype=float); H = V.T                  # contours verticaux, horizontaux
chiffre = xte[0, 0].numpy()
ref = Fn.conv2d(xte[:1], torch.tensor(V, dtype=torch.float32).reshape(1, 1, 3, 3))[0, 0].numpy()
print("identique à PyTorch :", np.allclose(convolution(chiffre, V), ref, atol=1e-5), "| taille de la sortie :", convolution(chiffre, V).shape)
```

```python hide
NUM("c_a14_ok", bool(np.allclose(convolution(chiffre, V), ref, atol=1e-5)))
fig, axs = plt.subplots(1, 3, figsize=(7.8, 2.7))
for ax, im, t in zip(axs, [chiffre, convolution(chiffre, V), convolution(chiffre, H)], ["chiffre", "contours verticaux", "contours horizontaux"]):
    ax.imshow(im, cmap="gray_r" if t == "chiffre" else "RdBu_r"); ax.set_title(t, fontsize=9, color=ENCRE2); ax.axis("off")
style.save(fig, "ch01-c-convolution.png")
```

![Un chiffre de test, puis les cartes obtenues avec le filtre vertical et le filtre horizontal : le premier met en valeur les traits verticaux, le second les traits horizontaux.](figures/ch01-c-convolution.png)

**Corrigé.** La convolution écrite à la main est identique à celle de PyTorch (vérification : `{{c_a14_ok}}`). La sortie fait $26\times26$ : $28-3+1$. Les couleurs de la figure montrent que chaque filtre répond aux transitions d'une orientation donnée (positives en rouge, négatives en bleu) : c'est ce type de détecteur que les 8 filtres du livre apprennent seuls.

### Application 1.5 — Mesurer l'effet de l'augmentation de données (section 1.2.6)

**Énoncé.** Entraînez un petit réseau convolutif sur 2 000 images, avec et sans augmentation (chaque image est dupliquée avec un décalage aléatoire de $-3$ à $+3$ pixels dans chaque direction). Évaluez sur le test, puis sur le test décalé de 3 pixels horizontalement.

```python
def petit_cnn():
    graine(0); return nn.Sequential(nn.Conv2d(1, 8, 3), nn.ReLU(), nn.MaxPool2d(2), nn.Conv2d(8, 16, 3), nn.ReLU(), nn.MaxPool2d(2), nn.Flatten(), nn.Linear(400, 10))

def decale(x, g):
    gen = torch.Generator().manual_seed(g)
    return torch.stack([torch.roll(im, shifts=tuple(torch.randint(-3, 4, (2,), generator=gen).tolist()), dims=(1, 2)) for im in x])

x2, y2 = xt[:2000], yt[:2000]
x2a, y2a = torch.cat([x2, decale(x2, 1)]), torch.cat([y2, y2])
lignes = {}
for nom, (x_, y_) in {"sans augmentation": (x2, y2), "avec augmentation": (x2a, y2a)}.items():
    m = petit_cnn(); entrainer(m, x_, y_, xv, yv, epoques=8, lr=3e-3)
    lignes[nom] = (exactitude(m, xte, yte), exactitude(m, torch.roll(xte, 3, dims=3), yte))
print(pd.DataFrame(lignes, index=["test", "test décalé de 3 px"]).T.round(3).to_string())
```

```python hide
for cle, nom in [("sans", "sans augmentation"), ("avec", "avec augmentation")]:
    NUM(f"c_a15_{cle}_te", lignes[nom][0]); NUM(f"c_a15_{cle}_dec", lignes[nom][1])
```

**Corrigé.** Sans augmentation : {{c_a15_sans_te|pc1}} % au test et {{c_a15_sans_dec|pc1}} % sur le test décalé. Avec augmentation : {{c_a15_avec_te|pc1}} % et {{c_a15_avec_dec|pc1}} %. Le gain est **spectaculaire sur les images décalées** (de {{c_a15_sans_dec|pc1}} % à {{c_a15_avec_dec|pc1}} %) : le réseau a vu pendant son entraînement les situations qu'il rencontre au test. Il se voit aussi, plus modestement, sur le test non décalé, parce que l'augmentation double aussi la quantité d'exemples d'un jeu de seulement 2 000 images (une graine seulement ici : ne retenez que l'ordre de grandeur).

### Application 1.6 — LSTM ou GRU ? Fenêtre courte ou longue ? (section 1.3.4)

**Énoncé.** Reprenez la prévision des ventes quotidiennes du livre (entraînement 2023-2024, test 2025). Comparez un LSTM et un GRU de 16 unités, avec une fenêtre de 7 puis de 28 jours, sur deux graines. Rapportez le nombre de paramètres et l'erreur absolue moyenne (MAE) en euros.

```python
vd = pd.read_csv("donnees/ventes_quotidiennes.csv", parse_dates=["date"]); vd["ly"] = np.log(vd.ventes)
tr_i, te_i = vd[vd.date < "2025-01-01"].index, vd[vd.date >= "2025-01-01"].index
mu, sg = vd.ly[tr_i].mean(), vd.ly[tr_i].std(); z = ((vd.ly - mu) / sg).values
promo = vd.promo.values.astype(float); doy = vd.date.dt.dayofyear.values; dow = np.eye(7)[vd.jour_semaine.values]

def jeux(W, idx):
    X = np.stack([np.column_stack([z[i - W:i], promo[i - W:i]]) for i in idx])
    C = np.column_stack([promo[idx], dow[idx], np.sin(2 * np.pi * doy[idx] / 365), np.cos(2 * np.pi * doy[idx] / 365)])
    return [torch.tensor(a, dtype=torch.float32) for a in (X, C, z[idx])]

class Prevision(nn.Module):
    def __init__(self, cellule):
        super().__init__(); self.rnn = cellule(2, 16, batch_first=True); self.tete = nn.Sequential(nn.Linear(26, 16), nn.ReLU(), nn.Linear(16, 1))
    def forward(self, f, c): return self.tete(torch.cat([self.rnn(f)[0][:, -1], c], 1)).squeeze(1)
```

```python
def evaluer(cellule, W, g):
    Xa, Ca, ya = jeux(W, [i for i in tr_i if i >= 28]); Xb, Cb, _ = jeux(W, list(te_i))
    graine(g); m = Prevision(cellule); opt = torch.optim.Adam(m.parameters(), 2e-3)
    for e in range(25):
        perm = torch.randperm(len(Xa))
        for i in range(0, len(Xa), 64):
            idx = perm[i:i + 64]; opt.zero_grad(); nn.functional.mse_loss(m(Xa[idx], Ca[idx]), ya[idx]).backward(); opt.step()
    with torch.no_grad(): p = np.exp(m.eval()(Xb, Cb).numpy() * sg + mu)
    return nb_parametres(m), float(np.mean(np.abs(vd.ventes.values[te_i] - p)))

res = {(n, W): [evaluer(c, W, g) for g in (0, 1)] for n, c in [("LSTM", nn.LSTM), ("GRU", nn.GRU)] for W in (7, 28)}
print(pd.DataFrame({f"{n}, fenêtre {W}": [v[0][0], round(np.mean([a[1] for a in v]), 2)] for (n, W), v in res.items()}, index=["paramètres", "MAE (€)"]).T.to_string())
```

```python hide
for (n, W), v in res.items(): NUM(f"c_a16_{n.lower()}_{W}_mae", np.mean([a[1] for a in v])); NUM(f"c_a16_{n.lower()}_{W}_p", v[0][0])
```

**Corrigé.** Le GRU a **{{c_a16_gru_28_p|int}}** paramètres contre **{{c_a16_lstm_28_p|int}}** pour le LSTM (trois blocs de portes au lieu de quatre). Les MAE moyennes (2 graines) sont de {{c_a16_lstm_7_mae|2}} € (LSTM, fenêtre de 7 jours), {{c_a16_lstm_28_mae|2}} € (LSTM, 28 jours), {{c_a16_gru_7_mae|2}} € (GRU, 7 jours) et {{c_a16_gru_28_mae|2}} € (GRU, 28 jours). Avec deux graines seulement, de petits écarts ne sont pas interprétables ; ce qui compte est l'**ordre de grandeur** (ces MAE, obtenues avec 25 époques, sont un peu plus élevées que celles du livre, obtenues avec 40) et la règle : à performance voisine, on prend le modèle le plus simple.

### Application 1.7 — Lire des factures dégradées : OCR et inclinaison (section 1.5)

**Énoncé.** Générez huit factures synthétiques avec Pillow, inclinez chaque image d'un angle de 0°, 5°, 10° ou 15° et mesurez le taux d'erreur par caractère (CER) de Tesseract. Redresser l'image de l'angle connu (en pratique, on l'estime) améliore-t-il la lecture ?

```python
from PIL import Image, ImageDraw, ImageFont
import pytesseract
from rapidfuzz.distance import Levenshtein
police = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
rng = np.random.default_rng(1)

def facture(i):
    lignes = [f"FACTURE N° 2025-{i:04d}", f"Client : Ville {chr(65 + i % 8)}", f"Article A{i % 9 + 1} x{i % 3 + 1}   {rng.uniform(5, 120):.2f} €", f"TOTAL TTC : {rng.uniform(20, 400):.2f} €"]
    im = Image.new("L", (620, 170), 255); dr = ImageDraw.Draw(im)
    for k, l in enumerate(lignes): dr.text((15, 10 + 36 * k), l, font=police, fill=0)
    return im, "\n".join(lignes)

def cer(lu, vrai): return Levenshtein.distance(lu, vrai) / len(vrai)
data = [facture(i) for i in range(1, 9)]
tab = {}
for ang in (0, 5, 10, 15):
    brut = [cer(pytesseract.image_to_string(im.rotate(ang, fillcolor=255), lang="fra").strip(), t) for im, t in data]
    redr = [cer(pytesseract.image_to_string(im.rotate(ang, fillcolor=255).rotate(-ang, fillcolor=255), lang="fra").strip(), t) for im, t in data]
    tab[ang] = (np.mean(brut), np.mean(redr))
print(pd.DataFrame(tab, index=["CER incliné", "CER redressé"]).T.round(3).to_string())
```

```python hide
for ang, (a, b) in tab.items(): NUM(f"c_a17_{ang}_brut", a); NUM(f"c_a17_{ang}_redr", b)
```

**Corrigé.** À 0° le CER est de {{c_a17_0_brut|3}}. Il augmente avec l'inclinaison : {{c_a17_5_brut|3}} à 5°, puis **{{c_a17_10_brut|3}} à 10°** (la lecture est devenue presque entièrement fausse) et {{c_a17_15_brut|3}} à 15° (Tesseract ne reconnaît plus rien : un CER de 1 signifie que le texte lu est entièrement faux ou absent). Redresser avant la lecture ramène le CER à {{c_a17_5_redr|3}} (5°), {{c_a17_10_redr|3}} (10°) et {{c_a17_15_redr|3}} (15°). Le redressement n'est pas parfait : l'image inclinée a perdu ses coins (la rotation n'agrandissait pas le cadre) et l'interpolation adoucit les caractères, d'où un CER encore supérieur à celui de l'image d'origine. En pratique, l'angle est **estimé** (par la direction des lignes de texte) ; cette étape de prétraitement est souvent plus rentable que de changer de moteur OCR.

### Application 1.8 — Réseau ou boosting : l'effet de la taille des données (section 1.6)

**Énoncé.** Sur les clients du volume III, comparez l'AUC d'un réseau à plongements et d'un `HistGradientBoosting` pour des tailles d'entraînement de 500, 1 500, 4 500 et 9 000 clients (test fixe de 3 000 clients, trois graines pour le réseau). Le réseau rattrape-t-il le boosting quand les données augmentent ?

```python
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
cl = pd.read_csv("donnees/clients_ml.csv"); yc = cl.churn_90j.values
cats = ["ville", "canal_acquisition", "appareil", "categorie_preferee"]
nums = [k for k in cl.columns if k not in cats + ["id_client", "churn_90j", "depense_6m", "segment_vrai", "commandes_apres_cible"]]
codes = np.column_stack([pd.Categorical(cl[k].fillna("manquant")).codes for k in cats]).astype(np.int64)
nbmod = [int(codes[:, i].max()) + 1 for i in range(len(cats))]
N = cl[nums]; manq = N.isna().astype(float).loc[:, N.isna().any()].values
X_hgb = pd.concat([N, pd.DataFrame(codes, columns=cats)], axis=1)
test = np.arange(9000, 12000); score = {}
```

```python
class Reseau(nn.Module):
    def __init__(self, d):
        super().__init__(); self.e = nn.ModuleList([nn.Embedding(n, min(8, n)) for n in nbmod])
        self.f = nn.Sequential(nn.Linear(sum(min(8, n) for n in nbmod) + d, 64), nn.ReLU(), nn.Linear(64, 1))
    def forward(self, xn, xc): return self.f(torch.cat([e(xc[:, i]) for i, e in enumerate(self.e)] + [xn], 1)).squeeze(1)

def auc_reseau(n, g):
    tr = np.arange(n); A = N.fillna(N.iloc[tr].median()); sc = StandardScaler().fit(A.iloc[tr])
    Z = torch.tensor(np.column_stack([sc.transform(A), manq]), dtype=torch.float32); C = torch.tensor(codes)
    graine(g); m = Reseau(Z.shape[1]); opt = torch.optim.Adam(m.parameters(), 2e-3); yt_ = torch.tensor(yc, dtype=torch.float32)
    for e in range(25):
        perm = torch.randperm(n)
        for i in range(0, n, 128):
            idx = perm[i:i + 128]; opt.zero_grad(); nn.functional.binary_cross_entropy_with_logits(m(Z[idx], C[idx]), yt_[idx]).backward(); opt.step()
    with torch.no_grad(): return roc_auc_score(yc[test], m.eval()(Z[test], C[test]).numpy())

for n in (500, 1500, 4500, 9000):
    hg = HistGradientBoostingClassifier(random_state=0, categorical_features=[X_hgb.columns.get_loc(c) for c in cats]).fit(X_hgb.iloc[:n], yc[:n])
    score[n] = (roc_auc_score(yc[test], hg.predict_proba(X_hgb.iloc[test])[:, 1]), np.mean([auc_reseau(n, g) for g in range(3)]))
print(pd.DataFrame(score, index=["boosting", "réseau"]).T.round(4).to_string())
```

```python hide
for n, (a, b) in score.items(): NUM(f"c_a18_{n}_hgb", a); NUM(f"c_a18_{n}_mlp", b); NUM(f"c_a18_{n}_gap", a - b)
```

**Corrigé.**

| Clients d'entraînement | AUC du boosting | AUC du réseau | Écart |
|---|---|---|---|
| 500 | {{c_a18_500_hgb|3}} | {{c_a18_500_mlp|3}} | {{c_a18_500_gap|3}} |
| 1 500 | {{c_a18_1500_hgb|3}} | {{c_a18_1500_mlp|3}} | {{c_a18_1500_gap|3}} |
| 4 500 | {{c_a18_4500_hgb|3}} | {{c_a18_4500_mlp|3}} | {{c_a18_4500_gap|3}} |
| 9 000 | {{c_a18_9000_hgb|3}} | {{c_a18_9000_mlp|3}} | {{c_a18_9000_gap|3}} |

Les deux méthodes progressent avec les données, mais **l'écart ne se réduit pas** : le réseau ne rattrape pas le boosting dans cette plage de tailles. Une courbe qui se resserrerait avec le volume serait la signature habituelle du deep learning, qui profite davantage de l'abondance de données que les arbres ; ici, à 9 000 clients, nous n'y sommes pas. Un test fixe de 3 000 clients et trois graines donnent une incertitude de quelques millièmes d'AUC : un écart constant d'environ 0,02 est donc au-delà du bruit, mais les petites variations de cet écart d'une taille à l'autre ne se lisent pas.

## Exercices

### Exercice 1.1 ⭐ — Le gradient du softmax (section 1.1.4)

Un réseau produit les scores (« logits ») $\mathbf z=(2,\,1,\,0)$ pour trois classes ; la vraie classe est la première. (a) Calculez les probabilités softmax $\mathbf p$. (b) Calculez la perte d'entropie croisée $L=-\ln p_1$. (c) Montrez que $\partial L/\partial z_k=p_k-y_k$ (où $y_k$ vaut 1 pour la vraie classe, 0 sinon), et donnez numériquement le gradient.

### Exercice 1.2 ⭐ — Compter les paramètres (sections 1.1.3 et 1.2.5)

(a) Un réseau dense 784-256-128-10 : combien de paramètres ? (b) Un réseau convolutif : convolution à 16 filtres $5\times5$ sur une image à 1 canal, puis convolution à 32 filtres $3\times3$, puis une couche dense de 10 sorties appliquée à 32 cartes de $4\times4$ aplaties : combien de paramètres ?

### Exercice 1.3 ⭐⭐ — Rétropropagation avec une ReLU (section 1.1.5)

Un réseau à une entrée, deux neurones cachés (ReLU) et une sortie linéaire, avec la perte quadratique $L=\tfrac12(\hat y-y)^2$. Entrée $x=2$, cible $y=1$. Couche cachée : poids $w=(0{,}5,\,-1)$, biais $b=(0{,}1,\,0{,}2)$. Sortie : poids $v=(1{,}5,\,0{,}5)$, biais $c=0$. Calculez la passe avant, puis tous les gradients, puis le gradient par rapport à $w_2$. Que vaut-il, et pourquoi ?

### Exercice 1.4 ⭐ — Choisir une activation (section 1.1.2)

Pour chaque situation, choisissez la sortie et la perte adaptées, et justifiez en une phrase : (a) prédire si un client résilie (oui/non) ; (b) prédire le chiffre sur une image (10 classes exclusives) ; (c) prédire les ventes du lendemain en euros ; (d) étiqueter un article avec plusieurs thèmes possibles à la fois.

### Exercice 1.5 ⭐⭐ — Le dropout « inversé » (section 1.1.8)

On applique un dropout de probabilité $p=0{,}5$ à $\mathbf a=(1,\,2,\,3,\,4)$ : chaque valeur est mise à zéro avec la probabilité $p$, et les valeurs conservées sont **multipliées par $1/(1-p)$**. (a) Pourquoi cette mise à l'échelle ? (b) Vérifiez par simulation (10 000 tirages) que l'espérance de la sortie est $\mathbf a$. (c) Que fait le dropout à la prédiction ?

### Exercice 1.6 ⭐ — Taille de sortie d'une convolution (section 1.2.2)

Une image de $64\times64$ passe par : convolution $5\times5$ (pas 1, sans rembourrage), pooling $2\times2$, convolution $3\times3$ avec rembourrage 1, pooling $2\times2$, convolution $3\times3$ de pas 2 sans rembourrage. Donnez la taille après chaque étape.

### Exercice 1.7 ⭐⭐ — Le champ réceptif (section 1.2.4)

Même réseau qu'à l'exercice 1.6. Quel est le **champ réceptif** (en pixels de l'image) d'un neurone situé après la troisième convolution ? On rappelle la récurrence : à chaque couche de filtre $k$ et de pas $s$, le champ vaut $r\leftarrow r+(k-1)\,j$, puis le « saut » devient $j\leftarrow j\,s$ (au départ, $r=1$ et $j=1$).

### Exercice 1.8 ⭐⭐ — Un pas de LSTM à la main (section 1.3.3)

Un LSTM à une unité, entrée $x=-1$, $h_{t-1}=0$, $c_{t-1}=1$. Poids (entrée, état, biais) : entrée $(1;\,0;\,0)$, oubli $(0;\,0;\,2)$, candidat $(1;\,0;\,0)$, sortie $(0;\,0;\,0)$. Calculez les portes, $c_t$ et $h_t$. Que fait ce LSTM de sa mémoire ?

### Exercice 1.9 ⭐ — Le naïf saisonnier à la main (section 1.3.4)

Les ventes de deux semaines sont : semaine 1 = (10, 12, 11, 13, 15, 20, 14) et semaine 2 = (11, 13, 10, 14, 16, 22, 13). Prévoyez la semaine 2 par le naïf saisonnier (même jour, semaine précédente). Calculez l'erreur absolue moyenne, et comparez-la à celle du naïf « hier ».

### Exercice 1.10 ⭐ — Le bug de la boucle (section 1.4.3)

Un étudiant écrit une boucle d'entraînement où il a oublié `optimiseur.zero_grad()`. (a) Que se passe-t-il pour les gradients d'un lot à l'autre ? (b) Montrez-le sur un exemple minimal : un seul paramètre $w=1$, la perte $L=3w$ calculée et rétropropagée trois fois de suite.

### Exercice 1.11 ⭐ — Le taux d'erreur par caractère (section 1.5)

La vraie ligne est `FACTURE N° 2025`. Tesseract a lu `FACTURF N° 2O25` (la lettre O à la place du chiffre 0). Calculez la distance d'édition de Levenshtein et le CER. Que vaudrait le CER si la lecture avait **supprimé** l'espace entre `N°` et `2025` ?

### Exercice 1.12 ⭐ — Choisir la méthode (sections 1.2 à 1.6)

Pour chaque cas, dites si vous commenceriez par un réseau de neurones, et lequel : (a) 5 000 photos de produits à classer en 12 rayons ; (b) un tableau de 20 000 clients, 40 colonnes, prédire la résiliation ; (c) la prévision hebdomadaire des ventes de 3 000 produits ; (d) 200 factures scannées par mois à saisir automatiquement.

## Corrigés

### Corrigé 1.1

```python hide
zz = np.array([2.0, 1.0, 0.0]); pp = np.exp(zz) / np.exp(zz).sum()
for k in range(3): NUM(f"c_e11_p{k}", pp[k])
NUM("c_e11_L", -np.log(pp[0])); NUM("c_e11_g0", pp[0] - 1); NUM("c_e11_g1", pp[1]); NUM("c_e11_g2", pp[2])
tz = torch.tensor(zz, requires_grad=True); nn.functional.cross_entropy(tz[None], torch.tensor([0])).backward()
NUM("c_e11_ok", bool(np.allclose(tz.grad.numpy(), [pp[0] - 1, pp[1], pp[2]])))
```

(a) $p_k=e^{z_k}/\sum_j e^{z_j}$ : $\mathbf p=({{c_e11_p0|4}},\ {{c_e11_p1|4}},\ {{c_e11_p2|4}})$. (b) $L=-\ln p_1={{c_e11_L|4}}$. (c) Avec $L=-z_1+\ln\sum_j e^{z_j}$, la dérivée par rapport à $z_k$ est $-y_k+e^{z_k}/\sum_j e^{z_j}=p_k-y_k$. Numériquement : $(p_1-1,\ p_2,\ p_3)=({{c_e11_g0|4}},\ {{c_e11_g1|4}},\ {{c_e11_g2|4}})$ ; les trois composantes somment à zéro, et PyTorch retrouve les mêmes valeurs (vérification : `{{c_e11_ok}}`).

### Corrigé 1.2

```python hide
mlp_c = nn.Sequential(nn.Linear(784, 256), nn.ReLU(), nn.Linear(256, 128), nn.ReLU(), nn.Linear(128, 10))
cnn_c = nn.Sequential(nn.Conv2d(1, 16, 5), nn.ReLU(), nn.Conv2d(16, 32, 3), nn.ReLU(), nn.Flatten(), nn.Linear(32 * 16, 10))
NUM("c_e12_mlp", nb_parametres(mlp_c)); NUM("c_e12_cnn", nb_parametres(cnn_c))
```

(a) $784\times256+256=200\,960$, puis $256\times128+128=32\,896$, puis $128\times10+10=1\,290$ : au total **{{c_e12_mlp|int}}**. (b) Première convolution : $16\times(1\times5\times5+1)=416$ ; seconde : $32\times(16\times3\times3+1)=4\,640$ ; couche dense : $(32\times4\times4)\times10+10=5\,130$ ; au total **{{c_e12_cnn|int}}**. Les deux comptes sont confirmés par `nb_parametres`. Remarque : la convolution a très peu de paramètres comparée à sa taille ; c'est la couche dense finale qui pèse le plus.

### Corrigé 1.3

```python hide
xx, yy = 2.0, 1.0; ww = np.array([0.5, -1.0]); bb = np.array([0.1, 0.2]); vv = np.array([1.5, 0.5]); cc = 0.0
zc = ww * xx + bb; ac = np.maximum(zc, 0); yh = vv @ ac + cc; L = 0.5 * (yh - yy) ** 2
dy = yh - yy; dac = vv * dy; dzc = dac * (zc > 0); gw = dzc * xx
for k, v in dict(z1=zc[0], z2=zc[1], a1=ac[0], a2=ac[1], yh=yh, L=L, dy=dy, gw1=gw[0], gw2=gw[1], gb1=dzc[0], gb2=dzc[1], gv1=dy * ac[0], gv2=dy * ac[1]).items(): NUM(f"c_e13_{k}", float(v))
```

Passe avant : $z=({{c_e13_z1|2}},\ {{c_e13_z2|2}})$, activations ReLU $a=({{c_e13_a1|2}},\ {{c_e13_a2|2}})$, sortie $\hat y=1{,}5\times{{c_e13_a1|2}}+0{,}5\times0={{c_e13_yh|2}}$, perte $L={{c_e13_L|3}}$. Passe arrière : $\partial L/\partial\hat y=\hat y-y={{c_e13_dy|2}}$ ; gradients de sortie $\partial L/\partial v=(\ {{c_e13_gv1|3}},\ {{c_e13_gv2|3}})$ ; pour les neurones cachés, le signal est multiplié par la dérivée de la ReLU (1 si $z>0$, sinon 0) : $\partial L/\partial b=({{c_e13_gb1|3}},\ {{c_e13_gb2|3}})$ et $\partial L/\partial w=({{c_e13_gw1|3}},\ {{c_e13_gw2|3}})$. Le gradient par rapport à $w_2$ est **nul** : le neurone 2 est « éteint » ($z_2<0$), donc aucun signal ne le traverse ; il ne bougera pas pour cet exemple. C'est le risque de la ReLU (neurones « morts ») dont l'initialisation de He et un pas raisonnable protègent.

### Corrigé 1.4

(a) **Une sortie, sigmoïde, entropie croisée binaire** : une probabilité pour la classe « résilie ». (b) **Dix sorties, softmax, entropie croisée** : des probabilités qui somment à 1 pour des classes exclusives. (c) **Une sortie linéaire** (aucune activation), perte quadratique ou absolue : une valeur réelle, pas bornée. (d) **Une sigmoïde par thème**, entropie croisée binaire pour chaque sortie : les thèmes ne s'excluent pas, donc pas de softmax.

### Corrigé 1.5

```python hide
aa = np.array([1.0, 2.0, 3.0, 4.0]); rr = np.random.default_rng(0)
masques = rr.random((10000, 4)) >= 0.5
sorties = masques * aa / 0.5
for k in range(4): NUM(f"c_e15_m{k}", sorties[:, k].mean())
```

(a) Si l'on se contentait de couper la moitié des valeurs, la somme reçue par la couche suivante serait **divisée par deux** à l'entraînement, mais pas à la prédiction. La mise à l'échelle par $1/(1-p)$ compense : l'**espérance** de chaque sortie est $a\cdot(1-p)\cdot\frac1{1-p}=a$. (b) La moyenne simulée de la sortie vaut $({{c_e15_m0|2}},\ {{c_e15_m1|2}},\ {{c_e15_m2|2}},\ {{c_e15_m3|2}})$ : c'est $\mathbf a$, à l'erreur de simulation près. (c) À la prédiction, le dropout est **désactivé** (`modele.eval()`) : toutes les unités sont actives, sans mise à l'échelle supplémentaire, grâce à la compensation faite à l'entraînement.

### Corrigé 1.6

```python hide
def taille(n, k, s=1, p=0): return (n + 2 * p - k) // s + 1
n_ = 64; etapes = []
for k, s, p in [(5, 1, 0), (2, 2, 0), (3, 1, 1), (2, 2, 0), (3, 2, 0)]:
    n_ = taille(n_, k, s, p); etapes.append(n_)
for i, v in enumerate(etapes): NUM(f"c_e16_{i}", v)
```

Avec $\lfloor(n+2p-k)/s\rfloor+1$ : $64\to{{c_e16_0}}$ (conv. $5\times5$) $\to{{c_e16_1}}$ (pooling) $\to{{c_e16_2}}$ (conv. $3\times3$ avec rembourrage, la taille est conservée) $\to{{c_e16_3}}$ (pooling) $\to{{c_e16_4}}$ (conv. $3\times3$ de pas 2).

### Corrigé 1.7

```python hide
r_, j_ = 1, 1; hist_r = []
for k, s in [(5, 1), (2, 2), (3, 1), (2, 2), (3, 2)]:
    r_ = r_ + (k - 1) * j_; j_ = j_ * s; hist_r.append(r_)
NUM("c_e17_final", r_); NUM("c_e17_saut", j_)
for i, v in enumerate(hist_r): NUM(f"c_e17_{i}", v)
```

On applique la récurrence couche par couche : champ de {{c_e17_0}} pixels après la première convolution, {{c_e17_1}} après le premier pooling, {{c_e17_2}} après la deuxième convolution, {{c_e17_3}} après le second pooling, puis **{{c_e17_final}}** après la troisième convolution : un carré de {{c_e17_final}} pixels de côté, sur une image de $64\times64$. Un neurone de la dernière couche voit donc une large portion de l'image, alors que chaque filtre n'est que de $3\times3$ ou $5\times5$ : c'est l'effet de l'empilement.

### Corrigé 1.8

```python hide
sg_ = lambda u: 1 / (1 + np.exp(-u))
xe, he, ce = -1.0, 0.0, 1.0
ie, fe, ge, oe = sg_(1 * xe + 0), sg_(0 * xe + 2), np.tanh(1 * xe + 0), sg_(0.0)
c2 = fe * ce + ie * ge; h2 = oe * np.tanh(c2)
for k, v in dict(i=ie, f=fe, g=ge, o=oe, c=c2, h=h2).items(): NUM(f"c_e18_{k}", v)
```

Portes : entrée $i=\sigma(-1)={{c_e18_i|3}}$, oubli $f=\sigma(2)={{c_e18_f|3}}$, candidat $g=\tanh(-1)={{c_e18_g|3}}$, sortie $o=\sigma(0)={{c_e18_o|3}}$. Mémoire : $c_t=f\cdot1+i\cdot g={{c_e18_c|3}}$ ; état : $h_t=o\cdot\tanh(c_t)={{c_e18_h|3}}$. La porte d'oubli est proche de 1 : la mémoire (1) est presque conservée ; l'information nouvelle (négative) en retranche un peu. C'est le comportement « mémoire stable » qui permet de relier des instants éloignés.

### Corrigé 1.9

```python hide
s1 = np.array([10, 12, 11, 13, 15, 20, 14.0]); s2 = np.array([11, 13, 10, 14, 16, 22, 13.0])
NUM("c_e19_sn", np.mean(np.abs(s2 - s1)))
serie = np.concatenate([s1, s2]); hier = serie[6:13]
NUM("c_e19_hier", np.mean(np.abs(s2 - hier)))
```

Le naïf saisonnier prédit la semaine 1 pour la semaine 2 : les erreurs absolues sont $(1,1,1,1,1,2,1)$, d'où une MAE de **{{c_e19_sn|2}}**. Le naïf « hier » prédit chaque jour par la veille ; sa MAE vaut **{{c_e19_hier|2}}**, bien plus grande, parce qu'il ignore le rythme hebdomadaire (le samedi est fort, le dimanche plus faible). C'est pourquoi le naïf **saisonnier** est la bonne référence ici.

### Corrigé 1.10

```python hide
w = torch.tensor(1.0, requires_grad=True); suites = []
for _ in range(3):
    (3 * w).backward(); suites.append(w.grad.item())
for i, v in enumerate(suites): NUM(f"c_e110_{i}", v)
```

(a) Par défaut, PyTorch **additionne** les nouveaux gradients à ceux déjà présents : sans `zero_grad()`, chaque pas utilise la somme des gradients de tous les lots précédents, et l'entraînement diverge ou se comporte de façon incohérente. (b) Avec $L=3w$, le gradient vaut 3 à chaque calcul ; mais le champ `w.grad` prend successivement les valeurs {{c_e110_0|0}}, {{c_e110_1|0}} puis {{c_e110_2|0}} : il **s'accumule**. (Cette accumulation est parfois utile, pour simuler de gros lots, mais elle doit être voulue.)

### Corrigé 1.11

```python hide
from rapidfuzz.distance import Levenshtein as Lv
vraie = "FACTURE N° 2025"; lue = "FACTURF N° 2O25"; sans_espace = "FACTURE N°2025"
NUM("c_e111_n", len(vraie)); NUM("c_e111_d", Lv.distance(lue, vraie)); NUM("c_e111_cer", Lv.distance(lue, vraie) / len(vraie))
NUM("c_e111_d2", Lv.distance(sans_espace, vraie)); NUM("c_e111_cer2", Lv.distance(sans_espace, vraie) / len(vraie))
```

La vraie ligne compte {{c_e111_n}} caractères. La lecture comporte deux substitutions (E→F, 0→O) : la distance de Levenshtein est {{c_e111_d}} et le CER vaut {{c_e111_d}}/{{c_e111_n}} = **{{c_e111_cer|3}}**. Si l'espace avait été supprimé, ce serait une seule suppression : distance {{c_e111_d2}}, CER {{c_e111_cer2|3}}. Le CER compte les erreurs de n'importe quel type, mais ne dit pas leur gravité : $0$ lu $O$ dans un montant est bien plus grave qu'un espace manquant ; en pratique on ajoute des contrôles métier (le total est-il la somme des lignes ?).

### Corrigé 1.12

(a) **Oui, un réseau convolutif**, mais surtout **par transfert** : avec 5 000 photos, on réutilise un réseau pré-entraîné et l'on n'entraîne que la fin (section 1.5). (b) **Non** : régression logistique puis boosting ; un réseau à plongements ne sera qu'un essai de plus, rarement meilleur (section 1.6). (c) **Peut-être** : avec des milliers de séries, un modèle global (un seul réseau pour toutes les séries) devient intéressant, mais **après** les références classiques (naïf saisonnier, boosting à retards). (d) **Un OCR existant** (Tesseract ou service équivalent), avec un prétraitement et des contrôles métier ; entraîner un réseau de reconnaissance sur 200 documents par mois n'a pas de sens.
