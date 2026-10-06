## 2.2 Transformers

> 💡 **Intuition.** Dans une phrase, chaque mot a besoin de **regarder les autres** pour savoir ce qu'il veut dire : « pas » modifie « vraiment », « cher » change de sens selon qu'il s'agit d'un prix ou d'un client. Le transformer généralise cette idée : à chaque couche, **chaque jeton compose son nouveau vecteur comme une moyenne pondérée des vecteurs de tous les autres**, les poids étant calculés à partir du contenu. Cette opération, l'**attention**, est le seul mécanisme nouveau ; tout le reste de l'architecture est du déjà-vu (couches linéaires, résidus, normalisation, rétropropagation du chapitre 1).

Cette section démonte le mécanisme sur un exemple si petit qu'on le calcule à la main, justifie chaque détail de la formule, puis assemble un **mini-transformer** entraîné sur nos avis, et le compare honnêtement à un modèle pré-entraîné.

### 2.2.1 Le problème que l'attention résout

Les réseaux récurrents du chapitre 1 (section 1.3) lisent un texte **mot à mot**, en résumant tout ce qu'ils ont lu dans un vecteur de taille fixe. Ce goulot d'étranglement pose deux problèmes : l'information d'un mot lointain s'efface (le gradient se dilue à chaque pas), et le calcul est **séquentiel** : on ne peut pas traiter le dixième mot avant le neuvième, ce qui interdit de profiter pleinement du calcul parallèle des processeurs modernes.

L'attention supprime les deux : tous les mots sont traités **en même temps**, et deux mots, aussi éloignés soient-ils, sont reliés **directement**, en un seul pas.

### 2.2.2 L'attention, calculée à la main

Chaque jeton de la phrase est représenté par un vecteur $x_i$. L'attention fabrique à partir de $x_i$ trois vecteurs par trois **projections linéaires** apprises :

- une **requête** $q_i=x_iW_Q$ : « que cherche ce mot ? » ;
- une **clé** $k_i=x_iW_K$ : « de quoi ce mot peut-il parler ? » ;
- une **valeur** $v_i=x_iW_V$ : « ce que ce mot apporte s'il est regardé ».

Le jeton $i$ compare sa requête à la clé de **chaque** jeton $j$ par un produit scalaire, normalise les scores par un softmax, et moyenne les valeurs avec ces poids :

$$\text{Attention}(Q,K,V)=\text{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V.$$

Les lignes de $Q$, $K$ et $V$ sont les vecteurs de tous les jetons ; $QK^\top$ est donc une matrice $n\times n$ de scores, $n$ étant le nombre de jetons ; le softmax est appliqué **ligne par ligne**, si bien que chaque ligne de poids somme à 1.

**Un exemple minimal.** Trois jetons en dimension 2 : $x_1=(1,0)$, $x_2=(0,1)$, $x_3=(1,1)$. Pour simplifier, posons $W_Q=W_K=W_V=I$ (les trois projections ne changent rien), donc $Q=K=V=X$.

1. Les scores bruts $XX^\top$ sont les produits scalaires deux à deux : $x_1\cdot x_1=1$, $x_1\cdot x_2=0$, $x_1\cdot x_3=1$, et ainsi de suite.
2. On divise par $\sqrt{d_k}=\sqrt2\approx1{,}41$.
3. On applique le softmax à chaque ligne : pour le jeton 1, le softmax de $(1,0,1)/\sqrt2$ donne les poids $(@@a11:f3@@,\;@@a12:f3@@,\;@@a13:f3@@)$.
4. La nouvelle représentation du jeton 1 est la moyenne pondérée $a_{11}x_1+a_{12}x_2+a_{13}x_3=(@@s1x:f3@@,\;@@s1y:f3@@)$.

```python
X = np.array([[1., 0.], [0., 1.], [1., 1.]])
scores = X @ X.T / np.sqrt(2)
A = np.exp(scores) / np.exp(scores).sum(axis=1, keepdims=True)    # softmax par ligne
sortie = A @ X
print(A.round(3)); print(sortie.round(3))
```

Le jeton 1 accorde le plus de poids à lui-même et au jeton 3 (qui lui ressemble : produit scalaire de 1) et le moins au jeton 2 (orthogonal). Le résultat est un vecteur « mélangé », plus proche de ce que contient son voisinage. Vérification croisée : la fonction `scaled_dot_product_attention` de PyTorch, utilisée dans les vrais modèles, donne la même matrice (écart maximal inférieur à @@ecart_sdpa:e@@).

```python hide
import torch.nn.functional as F
Xt = torch.tensor(X, dtype=torch.float64)
ref = F.scaled_dot_product_attention(Xt[None], Xt[None], Xt[None])[0].numpy()
NUM("a11", A[0, 0]); NUM("a12", A[0, 1]); NUM("a13", A[0, 2]); NUM("s1x", sortie[0, 0]); NUM("s1y", sortie[0, 1])
NUM("somme_lignes", A.sum(axis=1).max()); NUM("ecart_sdpa", np.abs(ref - sortie).max())
```

Trois remarques sur ce calcul, qui valent pour tous les transformers :

- **Les poids viennent du contenu**, pas de la position : ce sont des produits scalaires entre vecteurs appris. Un mot « cherche » ceux dont la clé lui ressemble.
- **La somme pondérée est une opération différentiable** : les projections $W_Q,W_K,W_V$ s'apprennent par rétropropagation (chapitre 1, section 1.1) comme n'importe quel poids.
- **La phrase entière est traitée par deux produits matriciels** ($QK^\top$ puis $AV$) : c'est ce qui rend l'architecture si efficace sur du matériel parallèle.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.3 (l'attention de zéro), exercices 2.5 et 2.6.

### 2.2.3 Pourquoi diviser par $\sqrt{d_k}$ ?

Ce détail de la formule n'est pas décoratif. Supposons que les composantes de $q$ et de $k$ soient indépendantes, de moyenne 0 et de variance 1. Alors $q\cdot k=\sum_{m=1}^{d_k}q_mk_m$ est une somme de $d_k$ termes indépendants, chacun de moyenne 0 et de variance $E[q_m^2]E[k_m^2]=1$ ; sa variance vaut donc **$d_k$** et son écart-type $\sqrt{d_k}$. Plus la dimension est grande, plus les scores sont dispersés.

Or le softmax de scores très dispersés est quasi **« tout ou rien »** : il met presque tout le poids sur le meilleur score, et son gradient devient minuscule partout ailleurs (le softmax est saturé). Diviser par $\sqrt{d_k}$ ramène la variance des scores à 1, quelle que soit la dimension. Nous le vérifions par simulation (10 000 couples de vecteurs gaussiens) :

```python hide-code
rng = np.random.default_rng(0)
lignes = []
for dk in (4, 64, 512):
    q = rng.standard_normal((10000, dk)); k = rng.standard_normal((10000, 10, dk))
    s = np.einsum("nd,nmd->nm", q, k)
    p_brut, p_ech = [np.mean([O.softmax(l).max() for l in s[:2000] / f]) for f in (1, np.sqrt(dk))]
    lignes.append((dk, s.var(), (s / np.sqrt(dk)).var(), p_brut, p_ech))
print(pd.DataFrame(lignes, columns=["d_k", "variance des scores", "après division", "poids max (brut)", "poids max (divisé)"]).round(2).to_string(index=False))
```

```python hide
for dk, v, v2, pb, pe_ in lignes:
    NUM(f"var_{dk}", v); NUM(f"pmax_brut_{dk}", pb); NUM(f"pmax_ech_{dk}", pe_)
```

La variance des scores bruts suit $d_k$ (≈ 4, 64, 512) et celle des scores divisés reste à 1. Conséquence : avec 10 clés possibles, le poids maximal d'une attention **sans** division atteint @@pmax_brut_512:f2@@ en dimension 512 (le softmax a choisi un gagnant), alors qu'avec la division il reste à @@pmax_ech_512:f2@@, valeur proche de celle obtenue en dimension 4 (@@pmax_ech_4:f2@@). Le modèle garde ainsi un gradient exploitable à toutes les dimensions.

### 2.2.4 Les positions : sans elles, un transformer est un sac de mots

Regardons la formule : si l'on permute les jetons d'entrée, les lignes de $Q$, $K$ et $V$ sont permutées de la même façon, et le résultat est **la même sortie, permutée** (on dit que l'attention est *équivariante* par permutation). Autrement dit, sans information supplémentaire, « le chien mord l'homme » et « l'homme mord le chien » produisent les mêmes vecteurs, simplement rangés dans un autre ordre : c'est un sac de mots. Nous le vérifions numériquement avec la couche d'attention de notre mini-transformer :

```python hide
torch.manual_seed(0)
att = O.Attention(16, 4).eval()
x = torch.randn(1, 6, 16); perm = torch.tensor([3, 0, 5, 1, 4, 2])
with torch.no_grad():
    sans = (att(x[:, perm]) - att(x)[:, perm]).abs().max().item()
    pe = torch.tensor(O.encodage_sinusoidal(6, 16), dtype=torch.float)
    avec = (att((x + pe)[:, perm]) - att(x + pe)[:, perm]).abs().max().item()
    # variante : on permute les mots mais pas les positions
    ordre = (att(x[:, perm] + pe) - att(x + pe)[:, perm]).abs().max().item()
NUM("ecart_perm_sans", sans); NUM("ecart_perm_avec", avec); NUM("ecart_ordre", ordre)
```

Avec des positions ignorées, l'écart entre « sortie des mots permutés » et « permutation de la sortie » reste inférieur à @@ecart_perm_sans:e@@ (arrondi numérique). Si en revanche on **ajoute à chaque vecteur un code de position avant l'attention** et que l'on permute les **mots** en laissant les positions en place, l'écart devient @@ecart_ordre:f2@@ : l'attention distingue désormais les deux phrases.

La solution historique est l'**encodage positionnel sinusoïdal** : le vecteur de la position $p$ a pour composantes

$$PE_{p,2i}=\sin\!\left(\frac{p}{10000^{2i/d}}\right),\qquad PE_{p,2i+1}=\cos\!\left(\frac{p}{10000^{2i/d}}\right).$$

Chaque paire de dimensions est une **horloge** de période différente : les premières tournent vite (elles distinguent des positions voisines), les dernières lentement (elles repèrent la zone de la phrase). Deux positions différentes ont toujours des codes différents, et le code d'une position décalée de $\delta$ s'obtient par une **rotation** de celui de la position d'origine (formules d'addition du sinus et du cosinus), ce qui facilite l'apprentissage de « trois mots plus loin ». Les modèles récents emploient d'autres variantes (positions apprises, encodages rotatifs), mais le principe reste : **l'ordre est injecté de l'extérieur**.

```python hide
pe = O.encodage_sinusoidal(40, 48)
fig, ax = plt.subplots(figsize=(7.2, 3.6))
im = ax.imshow(pe.T, aspect="auto", cmap="RdBu_r", vmin=-1, vmax=1); ax.grid(False)
ax.set_xlabel("position dans la phrase"); ax.set_ylabel("dimension du vecteur"); ax.set_title("Encodage positionnel sinusoïdal (40 positions, 48 dimensions)", fontsize=10)
fig.colorbar(im, ax=ax, label="valeur", shrink=0.85)
style.save(fig, "ch02-encodage-positionnel.png")
dist = np.linalg.norm(pe[:, None] - pe[None], axis=-1)
NUM("dist_min_pos", dist[np.triu_indices(40, 1)].min())
```

![Encodage positionnel sinusoïdal : chaque colonne est le code d'une position. Les dimensions du haut (indices faibles) oscillent vite, celles du bas lentement.](figures/ch02-encodage-positionnel.png)

### 2.2.5 Plusieurs têtes, résidus, normalisation : le bloc transformer

Une seule attention ne peut regarder qu'« une chose à la fois ». On en lance donc plusieurs en parallèle, les **têtes** : on découpe les vecteurs en $h$ sous-espaces de dimension $d/h$, chaque tête a ses propres $W_Q,W_K,W_V$ et calcule sa propre attention, puis on **concatène** les résultats et on les remélange par une dernière projection $W_O$. Une tête peut ainsi suivre la négation, une autre la proximité, une autre le sujet de la phrase. Le coût de calcul est le même qu'une attention unique de dimension $d$.

Un **bloc transformer** empile alors deux sous-couches :

1. l'attention multi-têtes ;
2. un petit réseau **par jeton** (deux couches linéaires avec une non-linéarité GELU entre elles, d'une largeur intermédiaire $4d$ en général), appliqué indépendamment à chaque position.

Autour de chaque sous-couche, deux outils stabilisent l'apprentissage : la **connexion résiduelle** (on ajoute l'entrée à la sortie : $x\leftarrow x+\text{sous-couche}(x)$, ce qui laisse passer le gradient directement, comme dans les réseaux résiduels du chapitre 1) et la **normalisation par couche** (chaque vecteur est recentré et remis à l'échelle). Le modèle complet est un plongement de mots, plus l'encodage positionnel, suivi de $L$ blocs identiques empilés.

**Combien de paramètres ?** Pour une dimension $d$, une couche contient les projections $Q,K,V$ ($3d^2$ poids), la projection de sortie ($d^2$) et le réseau par jeton ($d\cdot4d+4d\cdot d=8d^2$) : soit environ **$12d^2$ paramètres** par bloc (plus des termes en $d$ pour les biais et les normalisations). L'essentiel du modèle est donc dans des multiplications matricielles ; il y a $12d^2L$ paramètres hors plongements. Nous vérifions la formule sur notre bloc de dimension 48 :

```python hide-code
d_ = 48
bloc = O.Bloc(d_, 4)
n_bloc = sum(p.numel() for p in bloc.parameters())
exact = 12 * d_**2 + 13 * d_
print(f"paramètres du bloc (d = {d_}) : {n_bloc}   |   12 d² + 13 d = {exact}   |   12 d² = {12 * d_**2}")
```

```python hide
NUM("n_bloc", n_bloc); NUM("n_12d2", 12 * d_**2); NUM("d_bloc", d_)
```

L'écart entre le décompte exact et $12d^2$ vient des biais et des normalisations, négligeables dès que $d$ est grand. Ce décompte sert aussi plus tard : un modèle de 135 millions de paramètres comme celui de la section 2.3 est un empilement de 30 blocs de dimension 576, avec un gros bloc de plongements.

### 2.2.6 Masque causal, et le prix du carré

Pour **générer** du texte mot à mot (section 2.3), le modèle ne doit pas « tricher » en regardant les mots à venir. On ajoute un **masque causal** : avant le softmax, les scores de la partie triangulaire supérieure de $QK^\top$ (les positions futures) sont remplacés par $-\infty$, ce qui leur donne un poids nul. Chaque jeton ne voit alors que lui-même et ses prédécesseurs. Nous le vérifions en modifiant le dernier mot d'une phrase : la sortie des positions précédentes ne bouge pas.

```python hide
torch.manual_seed(1)
lm_test = O.MiniTransformer(50, d=16, tetes=2, couches=2, longueur=10, tache="langage").eval()
cl_test = O.MiniTransformer(50, d=16, tetes=2, couches=2, longueur=10, tache="classe").eval()
ids = torch.randint(4, 50, (1, 8)); ids2 = ids.clone(); ids2[0, -1] = 7 if ids[0, -1] != 7 else 8
with torch.no_grad():
    diff_causal = (lm_test(ids)[0, :-1] - lm_test(ids2)[0, :-1]).abs().max().item()
    diff_causal_dernier = (lm_test(ids)[0, -1] - lm_test(ids2)[0, -1]).abs().max().item()
    diff_bidir = (cl_test(ids) - cl_test(ids2)).abs().max().item()
NUM("diff_causal", diff_causal); NUM("diff_causal_dernier", diff_causal_dernier); NUM("diff_bidir", diff_bidir)
```

La sortie des 7 premières positions reste identique (écart inférieur à @@diff_causal:e@@) ; seule la dernière change (@@diff_causal_dernier:f2@@). Sans masque (modèle **bidirectionnel**, utilisé pour comprendre un texte plutôt que le continuer), tout dépend de tout.

Le revers de l'attention est son **coût quadratique** : la matrice des scores a $n^2$ entrées pour $n$ jetons, par tête et par couche. Doubler la longueur du texte multiplie ce coût par quatre.

```python hide-code
lignes = []
for n in (512, 4096, 32768, 131072):
    lignes.append((n, n * n, n * n * 4 / 1e9))
print(pd.DataFrame(lignes, columns=["jetons n", "entrées n²", "Go (flottants 32 bits)"]).round(3).to_string(index=False))
```

```python hide
for n, _, go in lignes:
    NUM(f"go_{n}", go)
```

Pour 512 jetons, la matrice tient dans 1 Mo ; pour 131 072 jetons (la longueur annoncée par certains modèles actuels), la matérialiser prendrait @@go_131072:i@@ Go **par tête et par couche**. Les implémentations modernes calculent donc l'attention par blocs sans jamais écrire toute la matrice (c'est l'idée de « FlashAttention »), et des variantes à attention locale ou creuse réduisent le nombre de paires comparées. Le coût de calcul, lui, reste en $n^2d$. D'où la **limite de contexte** des modèles de langage, et l'intérêt de ne leur donner que les passages utiles (c'est le principe du RAG, section 2.5).

### 2.2.7 Un mini-transformer sur nos avis

Passons à la pratique. Nous avons écrit à la main, en une cinquantaine de lignes de PyTorch (fichier `outils_ch02.py`, que le lecteur peut lire), un transformer **minuscule** : dimension 48, 4 têtes, 2 blocs, un vocabulaire de mots du corpus, et une tête de classification qui prend la **moyenne** des vecteurs de sortie. Entraînement sur les avis positifs et négatifs du jeu d'entraînement (8 passages, optimiseur AdamW, volume I section 1.3.3 pour la descente de gradient).

```python
voc = O.Vocabulaire(tr["texte"].tolist(), min_freq=2)
mini = O.entrainer_classifieur(tr["texte"].tolist(), tr["y"].to_numpy(), voc, epoques=8)
p_te = O.predire_classe(mini, voc, te["texte"].tolist())
print("paramètres :", sum(p.numel() for p in mini.parameters()), "| exactitude :", round(((p_te > 0.5) == te["y"].to_numpy()).mean(), 3))
```

À titre de comparaison, nous ajoutons un modèle **pré-entraîné** : MiniLM multilingue, un transformer de 12 couches déjà entraîné par d'autres sur un très grand corpus de paires de phrases. Nous ne le modifions pas : nous calculons le vecteur de chaque avis (la phrase est lue en entier, le vecteur final est la moyenne des sorties) et entraînons dessus une simple régression logistique.

```python
from sentence_transformers import SentenceTransformer

st = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device="cpu")
Emb = st.encode(avis["texte"].tolist(), batch_size=128, normalize_embeddings=True)      # un vecteur de 384 nombres par avis
clf = LogisticRegression(max_iter=3000, C=10).fit(Emb[tr.index], tr["y"])
```

```python hide
Eso = st.encode(O.SONDES, normalize_embeddings=True)
p_so_mini = O.predire_classe(mini, voc, O.SONDES)
ok_mini_te = ((p_te > 0.5) == te["y"].to_numpy()).mean(); ok_mini_so = ((p_so_mini > 0.5) == O.Y_SONDES).mean()
ok_pre_te = clf.score(Emb[te.index], te["y"]); ok_pre_so = ((clf.predict_proba(Eso)[:, 1] > 0.5) == O.Y_SONDES).mean()
n_mini = sum(p.numel() for p in mini.parameters()); n_pre = sum(p.numel() for p in st[0].auto_model.parameters())
err_pre = [O.SONDES[i] for i in range(len(O.SONDES)) if (clf.predict_proba(Eso)[i, 1] > 0.5) != O.Y_SONDES[i]]
NUM("acc_mini_te", ok_mini_te); NUM("acc_mini_so", ok_mini_so); NUM("acc_pre_te", ok_pre_te); NUM("acc_pre_so", ok_pre_so)
NUM("n_mini", n_mini); NUM("n_pre", n_pre / 1e6); NUM("n_err_pre", len(err_pre)); NUM("n_voc_mini", len(voc))
NUM("se_so", np.sqrt(0.75 * 0.25 / len(O.SONDES)))
```

Le tableau résume les trois modèles : la référence TF-IDF de la section 2.1, le mini-transformer appris sur le corpus, et le modèle pré-entraîné suivi d'une régression logistique.

```python hide-code
tab = pd.DataFrame({
    "modèle": ["TF-IDF + régression logistique", "mini-transformer (appris ici)", "MiniLM pré-entraîné + régression logistique"],
    "paramètres": [f"{len(vec.vocabulary_):,}".replace(",", " "), f"{n_mini:,}".replace(",", " "), f"{n_pre / 1e6:.0f} M"],
    "test du corpus": [ok.mean(), ok_mini_te, ok_pre_te],
    "48 phrases hors gabarit": [ok_sond_tfidf.mean(), ok_mini_so, ok_pre_so]}).round(3)
print(tab.to_string(index=False))
```

Les conclusions se lisent sur les deux colonnes de droite.

- **Sur le test du corpus**, les trois modèles sont à égalité (autour de 94 %, c'est-à-dire au plafond fixé par le bruit des étiquettes, section 2.1). **Ce test ne distingue pas les modèles.**
- **Sur les phrases hors gabarit**, le mini-transformer (@@acc_mini_so:p1@@) ne fait pas mieux que TF-IDF (@@acc_sondes_tfidf:p1@@), alors qu'il possède des couches d'attention, des positions et un vocabulaire à lui. La raison est la même : il n'a appris qu'à partir de **8 000 phrases très régulières** de @@n_voc_mini:i@@ mots ; il n'a rien à dire d'une phrase qui emploie des mots inconnus. L'attention est un mécanisme puissant, **pas une garantie de compréhension**. Avec 48 phrases, l'incertitude statistique d'une exactitude vaut environ @@se_so:p0@@ (un écart-type) : la différence entre ces deux modèles est donc du bruit.
- **Le modèle pré-entraîné atteint @@acc_pre_so:p1@@** (soit @@n_err_pre:i@@ erreurs seulement), une différence nettement au-delà du bruit. Il n'a pas été entraîné sur nos avis, mais sur d'énormes corpus : il sait déjà que « interminable » ressemble à « lent » et que « irréprochable » est un compliment. Nous retrouvons le message de la section 2.1 : **le sens est dans le vecteur**, et les vecteurs appris sur un grand corpus se **transfèrent**. C'est le même principe que le transfert par ResNet-18 du chapitre 1 (section 1.5).

> ⚠️ **Deux précautions.** La différence est réelle, mais le jeu de 48 phrases est petit et écrit par l'auteur : il illustre un phénomène, il ne chiffre pas un gain. Et sur un corpus réel, où le vocabulaire est ouvert et les tournures variées, c'est ce genre de test (des phrases que le modèle n'a pas pu mémoriser) qui doit servir de juge.

### 2.2.8 Que regardent les têtes d'attention ?

On aime regarder les poids d'attention : ils sont une fenêtre sur ce que le modèle « consulte ». La figure montre ceux de notre mini-transformer, pour la dernière couche, sur un avis nié.

```python hide
phrase = "rapide, la livraison ? pas vraiment. emballage insuffisant."
jetons = O.tokeniser(phrase)
with torch.no_grad():
    p_phr = mini(torch.tensor([voc.encoder(phrase, 40)])).softmax(-1)[0, 1].item()
poids = mini.blocs[-1].att.poids[0, :, : len(jetons), : len(jetons)].numpy()
fig, axes = plt.subplots(1, 4, figsize=(11, 3.1))
for h, ax in enumerate(axes):
    ax.imshow(poids[h], cmap="Blues", vmin=0, vmax=poids.max()); ax.grid(False)
    ax.set_xticks(range(len(jetons))); ax.set_xticklabels(jetons, rotation=90, fontsize=7)
    ax.set_yticks(range(len(jetons))); ax.set_yticklabels(jetons if h == 0 else [], fontsize=7)
    ax.set_title(f"tête {h + 1}", fontsize=9)
fig.suptitle("Poids d'attention de la dernière couche (ligne : jeton qui regarde, colonne : jeton regardé)", fontsize=9)
fig.tight_layout()
style.save(fig, "ch02-attention-tetes.png")
NUM("p_phrase_niee", p_phr); NUM("n_jetons_phrase", len(jetons))
NUM("entropie_moy", float(-(poids * np.log(poids + 1e-12)).sum(-1).mean()))
NUM("entropie_unif", float(np.log(len(jetons))))
```

![Poids d'attention des quatre têtes de la dernière couche du mini-transformer sur l'avis « rapide, la livraison ? pas vraiment. emballage insuffisant. » : chaque ligne montre où le jeton correspondant puise l'information.](figures/ch02-attention-tetes.png)

Le mini-transformer classe cet avis comme négatif (probabilité de positif : @@p_phrase_niee:p0@@), à raison. Que lit-on dans la figure ?

- **Les têtes se spécialisent, sans qu'on le leur ait demandé.** Dans les têtes 1 et 3, la plupart des jetons puisent surtout dans le signe « ? » ; dans la tête 4, ils puisent dans le mot « insuffisant » (le mot porteur du sentiment négatif) ; la tête 2 se partage entre « livraison », « emballage » et « ? » (des mots qui disent *de quoi* l'on parle).
- **Une partie de ce qui est consulté est du bruit utile** : le point d'interrogation ne dit rien du sentiment, mais il sert de « puits » où le modèle range une information de la phrase ; ce comportement est courant dans les transformers.
- **Le mot « pas » est très peu consulté**, alors qu'il est la clé de la négation : le modèle n'a pas appris à traiter la négation comme un humain (sa classification s'appuie plutôt sur « insuffisant »). Cela cadre avec son échec sur les phrases hors gabarit.

Les poids sont concentrés : leur entropie moyenne vaut @@entropie_moy:f1@@ nat, contre @@entropie_unif:f1@@ pour une attention uniforme sur les @@n_jetons_phrase:i@@ jetons.

> ⚠️ **L'attention n'est pas une explication.** Les poids montrent d'où l'information est *tirée* à une couche donnée, pas ce qui a *causé* la décision (les couches suivantes recombinent tout). La littérature est partagée sur la valeur explicative de ces poids (on peut en obtenir de très différents pour une même prédiction). Pour expliquer une décision, on préfère les méthodes du volume III (section 5.3, SHAP et les attributions) appliquées au modèle complet.

### 2.2.9 Trois familles de transformers

Le même bloc sert de brique à trois grandes familles, qui ne diffèrent que par le masque et la tâche d'entraînement :

| Famille | Masque | Tâche d'entraînement | Exemples d'usage |
|---|---|---|---|
| **Encodeur** (bidirectionnel) | aucun : chaque jeton voit tout | deviner des mots masqués dans la phrase | classer, comparer, rechercher (MiniLM) |
| **Décodeur** (causal) | triangulaire : on ne voit que le passé | prédire le mot suivant | générer du texte : les grands modèles de langage (section 2.3) |
| **Encodeur-décodeur** | encodeur sans masque, décodeur causal qui consulte l'encodeur | produire une sortie à partir d'une entrée | traduire, résumer |

> ✅ **À retenir.**
> - L'**attention** calcule, pour chaque jeton, une moyenne pondérée des valeurs de tous les jetons, avec des poids donnés par softmax$(QK^\top/\sqrt{d_k})$ ; elle traite toute la phrase en parallèle et relie directement deux mots éloignés.
> - La division par $\sqrt{d_k}$ garde la variance des scores à 1 : sans elle, le softmax sature en grande dimension (poids maximal de @@pmax_brut_512:f2@@ en dimension 512 contre @@pmax_ech_512:f2@@).
> - L'attention ignore l'ordre : on **ajoute un encodage positionnel**. Un **masque causal** interdit de voir l'avenir (génération). Le coût est **quadratique** en la longueur du texte.
> - Un bloc = attention multi-têtes + réseau par jeton, entourés de résidus et de normalisation ; environ $12d^2$ paramètres par bloc.
> - Entraîné sur 8 000 phrases régulières, notre mini-transformer égale TF-IDF au test et échoue comme lui hors gabarit ; **le modèle pré-entraîné généralise** (@@acc_pre_so:p1@@ contre @@acc_sondes_tfidf:p1@@ sur les phrases écrites à la main) : la qualité vient du **pré-entraînement**, pas de la seule architecture.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.3 et 2.4, exercices 2.5 à 2.8.
