## 7.3 Factorisation matricielle

Les méthodes de voisinage ne relient deux produits que s'ils ont des clients **en commun**. La factorisation matricielle fait mieux : elle résume chaque client et chaque produit par un petit nombre de **facteurs latents**, des grandeurs cachées que l'on n'observe pas mais que l'on apprend à partir des achats. Deux produits qui n'ont aucun acheteur commun peuvent alors avoir des facteurs proches, et c'est cela qui permet de généraliser. Ce principe est celui qui a dominé les systèmes de recommandation pendant une décennie ; il s'appuie sur les idées de la décomposition en valeurs singulières (volume I, section 1.1.4) et de la régularisation (section 2.1).

### 7.3.1 L'idée : des facteurs latents

Associons à chaque client $u$ un vecteur $p_u\in\mathbb R^k$ et à chaque produit $i$ un vecteur $q_i\in\mathbb R^k$, avec $k$ petit (quelques unités à quelques dizaines). L'**affinité** prédite entre le client et le produit est leur produit scalaire :
$$\hat r_{ui}=p_u^\top q_i=\sum_{f=1}^kp_{uf}\,q_{if}.$$
On peut imaginer que chaque coordonnée $f$ est un « goût » : le produit $i$ possède plus ou moins ce trait (valeur $q_{if}$), le client y est plus ou moins sensible (valeur $p_{uf}$), et l'affinité additionne les rencontres entre les deux. Rien n'impose de nommer ces goûts : on les laisse émerger.

En notation matricielle, la matrice $R$ ($n$ clients $\times$ $m$ produits) est approchée par un produit de deux matrices plus petites, $R\approx P\,Q^\top$, où $P$ est $n\times k$ et $Q$ est $m\times k$.

```python hide
fig, ax = plt.subplots(figsize=(9.2, 3.1)); ax.axis("off"); ax.set_xlim(0, 10.4); ax.set_ylim(0, 3.1)
def boite(x, y, w, h, texte, col):
    ax.add_patch(plt.Rectangle((x, y), w, h, fc=col, ec="white", alpha=0.85, lw=1.5))
    ax.text(x + w / 2, y + h / 2, texte, ha="center", va="center", color="white", fontsize=11, fontweight="bold")
boite(0.2, 0.3, 2.4, 2.4, "R\nclients × produits\n(presque vide)", BLEU)
ax.text(3.0, 1.5, "≈", fontsize=26, ha="center", va="center", color=style.ENCRE2)
boite(3.4, 0.3, 0.9, 2.4, "P\nclients\n× k", ORANGE)
ax.text(4.65, 1.5, "×", fontsize=22, ha="center", va="center", color=style.ENCRE2)
boite(5.0, 1.8, 2.4, 0.9, "Qᵀ : k × produits", AQUA)
ax.text(8.5, 1.5, "n×m cases\ncontre k(n+m)\nnombres appris", fontsize=10.5, ha="center", va="center", color=style.ENCRE2)
plt.savefig("figures/ch07-schema-factorisation.png", dpi=200, bbox_inches="tight"); plt.close()
n, m = 3000, 150
print("cases de R :", n * m, "| paramètres pour k = 6 :", 6 * (n + m), "| pour k = 20 :", 20 * (n + m))
```
<!--sortie-->
```text
cases de R : 450000 | paramètres pour k = 6 : 18900 | pour k = 20 : 63000
```

![Factorisation matricielle : la grande matrice d'achats est approchée par le produit d'une matrice de facteurs de clients (une ligne par client) et d'une matrice de facteurs de produits (une colonne par produit).](figures/ch07-schema-factorisation.png)

Le gain d'économie est immédiat : au lieu des 450 000 cases de la matrice, on apprend $k(n+m)$ nombres, soit **18 900** pour $k=6$. Surtout, ces nombres sont **partagés** : un produit, quel que soit le client, a le même vecteur $q_i$, appris à partir de tous ses acheteurs.

### 7.3.2 L'objectif : des moindres carrés régularisés

Pour apprendre $P$ et $Q$ à partir de retours **explicites** (des notes), on minimise l'erreur de reconstruction sur les cases **observées** uniquement, notées $\Omega$, avec une pénalité qui retient les vecteurs de devenir démesurés :
$$\min_{P,Q}\ \sum_{(u,i)\in\Omega}\bigl(r_{ui}-p_u^\top q_i\bigr)^2+\lambda\Bigl(\sum_u\|p_u\|^2+\sum_i\|q_i\|^2\Bigr).$$
Les deux termes jouent les rôles que l'on connaît. Le premier mesure l'erreur sur ce que l'on a vu. Le second, la **régularisation de Ridge** du volume II (section 1.5), empêche le surapprentissage : sans lui, avec assez de facteurs, on reproduirait exactement les notes connues et on prédirait n'importe quoi ailleurs (nous en verrons un exemple en 7.3.4).

> 💡 **Pourquoi on n'utilise que les cases observées.** Dans une matrice de notes, une case vide n'est pas un zéro : c'est une note inconnue. Pénaliser l'écart à zéro sur ces cases forcerait le modèle à prédire des notes nulles. L'objectif ne somme donc que sur $\Omega$. Pour des achats (retours implicites), les cases vides ont un statut différent, que traite la section 7.3.5.

### 7.3.3 Deux algorithmes

Le problème n'est pas convexe en $(P,Q)$ simultanément (c'est un produit de deux inconnues), mais il l'est **en chacun des deux séparément**. Deux stratégies en découlent.

**La descente de gradient stochastique (SGD).** On parcourt les notes connues une à une. Pour la note $r_{ui}$ d'erreur $e_{ui}=r_{ui}-p_u^\top q_i$, on déplace les deux vecteurs un peu dans le sens qui réduit l'erreur, avec un pas $\gamma$ :
$$p_u\leftarrow p_u+\gamma\,(e_{ui}\,q_i-\lambda\,p_u),\qquad q_i\leftarrow q_i+\gamma\,(e_{ui}\,p_u-\lambda\,q_i).$$
C'est la descente de gradient du volume I (section 1.3.3), appliquée à un exemple à la fois.

**Les moindres carrés alternés (ALS).** On **fixe** $Q$ : l'objectif devient, pour chaque client $u$, une régression de Ridge de ses notes sur les vecteurs des produits qu'il a notés. Notons $Q_u$ la matrice dont les lignes sont les $q_i$ des produits notés par $u$, et $r_u$ le vecteur de ses notes ; l'annulation du gradient donne la solution **explicite**
$$p_u=\bigl(Q_u^\top Q_u+\lambda I\bigr)^{-1}Q_u^\top r_u.$$
Puis on fixe $P$ et on résout de même pour chaque produit. On **alterne** jusqu'à stabilisation. Chaque étape ne peut que faire baisser l'objectif, donc la suite converge, vers un minimum local (qui dépend de l'initialisation).

> 📐 **Pourquoi la formule.** Pour un client donné, l'objectif en $p_u$ est $\|r_u-Q_up_u\|^2+\lambda\|p_u\|^2$ : exactement une régression de Ridge, dont les équations normales sont $(Q_u^\top Q_u+\lambda I)p_u=Q_u^\top r_u$ (volume II, section 1.5.1). Les $n$ problèmes (un par client) sont **indépendants** : on peut les résoudre en parallèle, ce qui fait la force de l'ALS pour les grands catalogues.

### 7.3.4 Une itération à la main

Prenons quatre clients, quatre produits, onze notes connues et cinq cases vides (symbole « ? »).

| | P1 | P2 | P3 | P4 |
|---|:-:|:-:|:-:|:-:|
| Client 1 | 5 | 3 | ? | 1 |
| Client 2 | 4 | ? | ? | 1 |
| Client 3 | 1 | 1 | ? | 5 |
| Client 4 | ? | 1 | 5 | 4 |

Avec un seul facteur ($k=1$), chaque client et chaque produit est un simple nombre, et la formule d'ALS devient une division. Prenons $\lambda=1$ et initialisons tous les facteurs des produits à $q=(1,1,1,1)$.

**Étape 1 : les clients.** Pour le client 1, qui a noté P1, P2 et P4 (notes $5,3,1$) :
$$p_1=\frac{5\times1+3\times1+1\times1}{(1^2+1^2+1^2)+1}=\frac{9}{4}=2{,}25.$$
De même $p_2=\dfrac{4+1}{2+1}=1{,}667$, $p_3=\dfrac{1+1+5}{3+1}=1{,}75$ et $p_4=\dfrac{1+5+4}{3+1}=2{,}5$. Le terme $+1$ au dénominateur est la régularisation : il tire chaque facteur vers zéro.

**Étape 2 : les produits.** On fixe maintenant $p=(2{,}25;\ 1{,}667;\ 1{,}75;\ 2{,}5)$. Pour le produit P1, noté par les clients 1, 2 et 3 (notes $5,4,1$) :
$$q_1=\frac{5\times2{,}25+4\times1{,}667+1\times1{,}75}{2{,}25^2+1{,}667^2+1{,}75^2+1}=\frac{19{,}67}{11{,}90}\approx1{,}652.$$
On trouve de même $q_2\approx0{,}715$, $q_3\approx1{,}724$ (une seule note, celle du client 4) et $q_4\approx1{,}249$.

**L'objectif baisse.** Après l'étape 1, la somme des erreurs au carré sur les notes connues, plus la pénalité, vaut **59,17** ; après l'étape 2, **47,93**. Une seconde passe sur les clients donne $p\approx(2{,}01;\ 1{,}49;\ 1{,}48;\ 2{,}37)$ et un objectif de **46,91**. Après une centaine d'alternances, il se stabilise à **45,66**.

```python hide
R4 = np.array([[5, 3, np.nan, 1], [4, np.nan, np.nan, 1], [1, 1, np.nan, 5], [np.nan, 1, 5, 4]])
obs4 = ~np.isnan(R4); lam4 = 1.0
etape_p = lambda q: np.array([R4[i, obs4[i]] @ q[obs4[i]] / (q[obs4[i]] @ q[obs4[i]] + lam4) for i in range(4)])
etape_q = lambda p: np.array([R4[obs4[:, j], j] @ p[obs4[:, j]] / (p[obs4[:, j]] @ p[obs4[:, j]] + lam4) for j in range(4)])
def objectif(p, q):
    e = np.where(obs4, R4 - np.outer(p, q), 0)
    return (e ** 2).sum() + lam4 * ((p ** 2).sum() + (q ** 2).sum())
q4 = np.ones(4)
p4 = etape_p(q4); o1 = objectif(p4, q4)
q4 = etape_q(p4); o2 = objectif(p4, q4)
p4 = etape_p(q4); o3 = objectif(p4, q4)
print("p après l'étape 1 :", etape_p(np.ones(4)).round(3), "| objectif", round(o1, 2))
print("q après l'étape 2 :", etape_q(etape_p(np.ones(4))).round(3), "| objectif", round(o2, 2))
print("p après la 2e passe :", p4.round(3), "| objectif", round(o3, 2))
for _ in range(100):
    q4 = etape_q(p4); p4 = etape_p(q4)
print("objectif après 100 alternances :", round(objectif(p4, q4), 2), "| facteurs", p4.round(2), q4.round(2))
print("prédictions des cases vides (client 1 P3, client 2 P2, client 2 P3, client 3 P3, client 4 P1) :", np.outer(p4, q4)[~obs4].round(2))

def als_k(k, lam, it=200, seed=0):
    rng = np.random.default_rng(seed); P = rng.standard_normal((4, k)) * 0.5; Q = rng.standard_normal((4, k)) * 0.5
    for _ in range(it):
        for i in range(4):
            Qi = Q[obs4[i]]; P[i] = np.linalg.solve(Qi.T @ Qi + lam * np.eye(k), Qi.T @ R4[i, obs4[i]])
        for j in range(4):
            Pj = P[obs4[:, j]]; Q[j] = np.linalg.solve(Pj.T @ Pj + lam * np.eye(k), Pj.T @ R4[obs4[:, j], j])
    e = np.where(obs4, R4 - P @ Q.T, 0)
    return np.sqrt((e ** 2).sum() / obs4.sum()), (P @ Q.T)[~obs4]
for k in (1, 2):
    rm, pr = als_k(k, 0.1)
    print(f"k = {k}, lambda = 0,1 : erreur quadratique moyenne sur les notes connues", round(rm, 3), "| prédictions des cases vides", pr.round(2))
```
<!--sortie-->
```text
p après l'étape 1 : [2.25  1.667 1.75  2.5  ] | objectif 59.17
q après l'étape 2 : [1.652 0.715 1.724 1.249] | objectif 47.93
p après la 2e passe : [2.009 1.486 1.484 2.371] | objectif 46.91
objectif après 100 alternances : 45.66 | facteurs [1.74 1.3  1.26 2.15] [2.08 0.84 1.91 1.5 ]
prédictions des cases vides (client 1 P3, client 2 P2, client 2 P3, client 3 P3, client 4 P1) : [3.32 1.09 2.47 2.41 4.47]
k = 1, lambda = 0,1 : erreur quadratique moyenne sur les notes connues 1.415 | prédictions des cases vides [4.1  1.25 3.09 2.87 4.99]
k = 2, lambda = 0,1 : erreur quadratique moyenne sur les notes connues 0.063 | prédictions des cases vides [1.45 2.35 1.39 5.87 1.15]
```

Un seul facteur ne suffit pas à représenter ce tableau (deux groupes de clients aux goûts opposés : les clients 1 et 2 notent P1 haut et P4 bas, les clients 3 et 4 l'inverse) ; que se passe-t-il avec deux facteurs et presque pas de régularisation ($\lambda=0{,}1$) ? L'erreur sur les notes connues tombe à **0,06**, contre 1,42 avec un seul facteur : le modèle a **recopié** les onze notes. Mais l'une de ses prédictions pour les cases vides est absurde : il prédit **5,87** pour le client 3 et le produit P3, une note supérieure au maximum possible de 5. C'est le surapprentissage en miniature : onze observations pour seize paramètres. Régulariser (et valider !) n'est pas facultatif.

### 7.3.5 Retours implicites : donner aux cases vides un poids faible

Pour des achats, la situation est différente : la matrice ne contient que des 1 (achats) et des cases vides. Si l'on ne somme que sur les achats observés, le modèle apprend à tout prédire à 1 et n'apprend rien. Si l'on traite toutes les cases vides comme des 0 avec le même poids que les achats, on enseigne au modèle que les produits non achetés sont rejetés, ce qui est faux (7.1.2). La solution de **Hu, Koren et Volinsky** (2008) est un compromis : on garde **toutes** les cases, mais on pondère par la **confiance** que l'on a dans chaque observation.

Pour chaque paire $(u,i)$, notons $x_{ui}=1$ si le client a acheté le produit et $0$ sinon, et donnons-lui la confiance
$$c_{ui}=1+\alpha\,R_{ui}.$$
Une case vide a la confiance minimale 1 ; un achat a la confiance $1+\alpha$, avec $\alpha$ de l'ordre de quelques unités. L'objectif devient
$$\min_{P,Q}\ \sum_{u,i}c_{ui}\bigl(x_{ui}-p_u^\top q_i\bigr)^2+\lambda\Bigl(\sum_u\|p_u\|^2+\sum_i\|q_i\|^2\Bigr),$$
avec, pour un client, la solution ALS $p_u=\bigl(Q^\top C_uQ+\lambda I\bigr)^{-1}Q^\top C_ux_u$, où $C_u$ est la matrice diagonale des confiances de $u$. Le calcul paraît lourd (il porte sur tous les produits), mais une astuce le rend rapide : $Q^\top C_uQ=Q^\top Q+\alpha\,Q_u^\top Q_u$, où $Q^\top Q$ est calculé une fois pour tous les clients et $Q_u$ ne contient que les produits **achetés** par $u$.

**À la main.** Un seul facteur ($k=1$), trois produits dont les facteurs sont $q=(1;\ 0{,}5;\ 2)$, un client qui a acheté P1 et P3, $\alpha=4$ (confiance 5 sur les achats) et $\lambda=1$. Le numérateur $\sum c\,x\,q=5\times1+5\times2=15$ ; le dénominateur $\sum c\,q^2+\lambda=5\times1+1\times0{,}25+5\times4+1=26{,}25$. Donc $p_u=15/26{,}25\approx0{,}571$ : les cases vides pèsent dans le dénominateur, mais faiblement.

```python hide
qq = np.array([1.0, 0.5, 2.0]); c = np.array([5.0, 1.0, 5.0]); x = np.array([1.0, 0.0, 1.0])
print("numérateur", (c * x * qq).sum(), "| dénominateur", (c * qq ** 2).sum() + 1, "| p_u =", round((c * x * qq).sum() / ((c * qq ** 2).sum() + 1), 4))
```
<!--sortie-->
```text
numérateur 15.0 | dénominateur 26.25 | p_u = 0.5714
```

### 7.3.6 La SVD tronquée comme référence

Il existe une version plus simple, et qui sert de **référence** : la décomposition en valeurs singulières tronquée (volume I, section 1.1.4) de la matrice d'achats. Le théorème d'**Eckart-Young** affirme que la meilleure approximation de rang $k$ de $R$ au sens des moindres carrés est obtenue en gardant les $k$ plus grandes valeurs singulières. Elle s'obtient en une ligne :

```python
from sklearn.decomposition import TruncatedSVD

svd = TruncatedSVD(n_components=4, random_state=0)
Z = svd.fit_transform(R_train)         # facteurs des clients
scores = Z @ svd.components_           # reconstruction : score de chaque produit pour chaque client
```

La différence avec l'ALS pondéré est instructive : la SVD traite **toutes les cases vides comme des zéros de même poids que les achats**, et ne régularise pas. Elle approche donc surtout la popularité et se met à surapprendre dès que $k$ grandit.

### 7.3.7 Choisir $k$ et $\lambda$, et ce que valent les facteurs

Il reste à régler le nombre de facteurs $k$, la régularisation $\lambda$ et la confiance $\alpha$ (fixée ici à 8). Comme pour les voisins, le choix se fait sur le jeu de **validation**.

```python hide
Rt, Rv = d["R_train"], d["val"]
k_als, lam_als = [2, 4, 6, 8, 12], [20, 50, 100, 150]
k_svd = [2, 4, 6, 10, 20]
lignes = []
for lam in lam_als:
    for k in k_als:
        S_als = scores_als(Rt, k=k, lam=lam, alpha=8.0, n_iter=10, seed=0)
        m = resume(evaluer(S_als, Rt, Rv, d["users"]))
        lignes.append({"méthode": "ALS", "k": k, "lambda": lam, "rappel@10": m.rappel, "NDCG@10": m.ndcg})
for k in k_svd:
    m = resume(evaluer(scores_svd(Rt, k=k), Rt, Rv, d["users"]))
    lignes.append({"méthode": "SVD", "k": k, "lambda": 0, "rappel@10": m.rappel, "NDCG@10": m.ndcg})
grille_fact = pd.DataFrame(lignes)
b_als = grille_fact[grille_fact["méthode"] == "ALS"].sort_values("NDCG@10", ascending=False).iloc[0]
b_svd = grille_fact[grille_fact["méthode"] == "SVD"].sort_values("NDCG@10", ascending=False).iloc[0]
choix["als"] = (int(b_als["k"]), int(b_als["lambda"])); choix["svd"] = int(b_svd["k"])
print(grille_fact.round(4).to_string(index=False))
print("meilleurs :", choix, "| ALS NDCG", round(b_als["NDCG@10"], 4), "rappel", round(b_als["rappel@10"], 4), "| SVD NDCG", round(b_svd["NDCG@10"], 4), "rappel", round(b_svd["rappel@10"], 4))
```
<!--sortie-->
```text
méthode  k  lambda  rappel@10  NDCG@10
    ALS  2      20     0.2638   0.1532
    ALS  4      20     0.2555   0.1545
    ALS  6      20     0.2468   0.1497
    ALS  8      20     0.2365   0.1395
    ALS 12      20     0.2106   0.1253
    ALS  2      50     0.2643   0.1564
    ALS  4      50     0.2641   0.1597
    ALS  6      50     0.2577   0.1565
    ALS  8      50     0.2497   0.1495
    ALS 12      50     0.2403   0.1412
    ALS  2     100     0.2643   0.1570
    ALS  4     100     0.2713   0.1640
    ALS  6     100     0.2761   0.1681
    ALS  8     100     0.2755   0.1678
    ALS 12     100     0.2744   0.1681
    ALS  2     150     0.2407   0.1429
    ALS  4     150     0.2388   0.1423
    ALS  6     150     0.2410   0.1431
    ALS  8     150     0.2408   0.1430
    ALS 12     150     0.2412   0.1431
    SVD  2       0     0.2289   0.1355
    SVD  4       0     0.2367   0.1427
    SVD  6       0     0.2251   0.1330
    SVD 10       0     0.2026   0.1160
    SVD 20       0     0.1654   0.0898
meilleurs : {'art': (149, 0), 'cli': 300, 'als': (6, 100), 'svd': 4} | ALS NDCG 0.1681 rappel 0.2761 | SVD NDCG 0.1427 rappel 0.2367
```

```python hide
fig, ax = plt.subplots(figsize=(6.6, 4.0))
for lam, col in zip(lam_als, (BLEU, ORANGE, AQUA, ROUGE)):
    g = grille_fact[(grille_fact["méthode"] == "ALS") & (grille_fact["lambda"] == lam)]
    ax.plot(g["k"], g["NDCG@10"], "o-", color=col, label=f"ALS, λ = {lam}")
g = grille_fact[grille_fact["méthode"] == "SVD"]
ax.plot(g["k"], g["NDCG@10"], "s-", color=VIOLET, label="SVD tronquée")
ax.axhline(ref_pop.ndcg, color=MUET, ls="--", lw=1.2); ax.text(13.5, ref_pop.ndcg - 0.0055, "popularité (référence)", color=MUET, fontsize=9)
ax.set_xlabel("nombre de facteurs k"); ax.set_ylabel("NDCG@10 sur la validation"); ax.legend(frameon=False, fontsize=9, loc="upper right")
ax.set_title("Réglage des méthodes de factorisation")
plt.tight_layout(); plt.savefig("figures/ch07-reglage-factorisation.png", dpi=200, bbox_inches="tight"); plt.close()
```

![NDCG@10 sur le jeu de validation selon le nombre de facteurs, pour l'ALS implicite avec trois niveaux de régularisation et pour la SVD tronquée. La ligne en tirets est la popularité.](figures/ch07-reglage-factorisation.png)

Le tableau et la figure se lisent en quatre points.

- **Le meilleur réglage est $k=6$ facteurs et $\lambda=100$** : NDCG@10 de **0,168** (rappel@10 de 27,6 %), contre 0,165 pour les meilleurs voisins de clients, 0,158 pour les voisins de produits et 0,143 pour la popularité. Le gain sur la popularité est réel, mais modeste : 2,5 points de NDCG.
- **Plus de facteurs demandent plus de régularisation.** Avec $\lambda=20$, le NDCG atteint 0,155 pour $k=4$, puis baisse jusqu'à 0,125 pour $k=12$ : c'est le surapprentissage. Avec $\lambda=100$, il reste stable à 0,168 de $k=6$ à $k=12$ : la pénalité maintient en pratique la complexité effective du modèle, quel que soit $k$.
- **Une régularisation trop forte écrase tout.** Avec $\lambda=150$, le NDCG vaut 0,143 pour **toutes** les valeurs de $k$ : exactement celui de la popularité. Les facteurs de personnalisation sont réduits à zéro et il ne reste que la direction « produit populaire ». Le meilleur réglage se situe donc **près d'un précipice**, ce qui rappelle qu'on doit explorer une grille assez large pour voir l'autre côté de l'optimum (l'échelle de $\lambda$ dépend aussi de $\alpha$ et de la taille des données).
- **La SVD tronquée ne fait pas mieux que la popularité.** Son meilleur NDCG (0,143, avec $k=4$) est celui de la popularité, puis il baisse jusqu'à 0,090 pour $k=20$ : sans pondération ni régularisation, elle apprend surtout le bruit.

Que valent les facteurs eux-mêmes ? Projetons les vecteurs des produits appris par le meilleur modèle sur leurs deux directions principales (l'ACP du volume II, section 3.1).

```python hide
from sklearn.decomposition import PCA
k_b, lam_b = choix["als"]
U_b, V_b = als_implicite(Rt, k=k_b, lam=lam_b, alpha=8.0, n_iter=10, seed=0)
Z2 = PCA(n_components=2, random_state=0).fit_transform(V_b)
fig, ax = plt.subplots(figsize=(6.0, 4.6))
for cat, col in zip("ABCD", (BLEU, ORANGE, AQUA, VIOLET)):
    mask = (prod["categorie"] == cat).to_numpy()
    ax.scatter(Z2[mask, 0], Z2[mask, 1], s=34, color=col, alpha=0.85, label=f"catégorie {cat}")
ax.set_xlabel("première direction principale"); ax.set_ylabel("deuxième direction principale")
ax.set_title("Les 150 produits dans l'espace des facteurs"); ax.legend(frameon=False, fontsize=9)
plt.tight_layout(); plt.savefig("figures/ch07-espace-latent.png", dpi=200, bbox_inches="tight"); plt.close()
cent = np.array([Z2[(prod["categorie"] == c).to_numpy()].mean(axis=0) for c in "ABCD"])
disp_intra = np.mean([np.linalg.norm(Z2[(prod["categorie"] == c).to_numpy()] - cent[i], axis=1).mean() for i, c in enumerate("ABCD")])
disp_inter = np.mean([np.linalg.norm(cent[i] - cent[j]) for i in range(4) for j in range(i + 1, 4)])
print("dispersion moyenne à l'intérieur d'une catégorie :", round(disp_intra, 3), "| distance moyenne entre centres :", round(disp_inter, 3))
Vn = V_b / np.linalg.norm(V_b, axis=1, keepdims=True); simv = Vn @ Vn.T; np.fill_diagonal(simv, -1)
cat_arr = prod["categorie"].to_numpy()
meme_cat = np.mean([(cat_arr[np.argsort(-simv[i])[:5]] == cat_arr[i]).mean() for i in range(150)])
hasard_cat = float(((prod["categorie"].value_counts() / 150) ** 2).sum())
print("part des 5 plus proches voisins (dimension complète) de la même catégorie :", round(meme_cat, 3), "| au hasard :", round(hasard_cat, 3))
```
<!--sortie-->
```text
dispersion moyenne à l'intérieur d'une catégorie : 0.403 | distance moyenne entre centres : 0.452
part des 5 plus proches voisins (dimension complète) de la même catégorie : 0.86 | au hasard : 0.258
```

![Les 150 produits projetés sur les deux premières directions de l'espace des facteurs appris par l'ALS, colorés par catégorie. Le modèle ne connaissait pas les catégories : elles se regroupent en partie.](figures/ch07-espace-latent.png)

La projection montre une structure : les produits de la catégorie C se regroupent en haut, ceux de la catégorie A en bas à gauche, ceux de la catégorie B à droite, la catégorie D étant plus diffuse. Les groupes se **recouvrent** pourtant : la dispersion moyenne à l'intérieur d'une catégorie (0,40) est proche de la distance moyenne entre les centres de deux catégories (0,45). Mais la projection en deux dimensions **écrase** l'information : dans l'espace complet des six facteurs, **86 %** des cinq plus proches voisins d'un produit (au sens du cosinus de leurs facteurs) appartiennent à sa catégorie, contre environ 26 % si les voisins étaient tirés au hasard. Les facteurs ne sont donc pas des catégories : ils capturent des goûts qui recoupent largement, mais pas exactement, le rangement du catalogue. (Les données ont été fabriquées avec six facteurs latents, dont les produits d'une même catégorie partagent une part ; le modèle retrouve cette trace sans connaître ni les catégories ni cette vérité.)

> ⚠️ **N'interprétez pas trop les axes.** Les facteurs latents ne sont définis qu'**à une rotation près** : si l'on remplace $P$ par $PA$ et $Q$ par $QA^{-\top}$ pour une matrice inversible $A$, le produit $PQ^\top$ est inchangé (et la pénalité l'est aussi pour une rotation orthogonale). Une direction de l'espace des facteurs n'a donc pas de sens propre ; seules comptent les **distances** et les **produits scalaires**. Nommer un axe « goût pour le traditionnel » est une histoire que l'on se raconte, pas un résultat.

> ✅ **À retenir (7.3).**
> - La factorisation approche $R\approx PQ^\top$ : chaque client et chaque produit reçoit un vecteur de $k$ **facteurs latents**, l'affinité étant leur produit scalaire. Elle **généralise** à des produits sans acheteurs communs.
> - On minimise une erreur de reconstruction **régularisée** (Ridge) par **SGD** ou par **moindres carrés alternés** (chaque étape est une régression de Ridge).
> - Pour des achats, on pondère par la **confiance** : cases vides à poids faible, achats à poids $1+\alpha$.
> - La SVD tronquée est une référence simple, qui traite les cases vides comme des zéros.
> - $k$ et $\lambda$ se règlent sur la validation ; trop de facteurs sans régularisation = surapprentissage.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.3 (ALS implicite écrit à la main) et 7.4 (factorisation sur les notes explicites par SGD), exercices 7.7 à 7.9.
