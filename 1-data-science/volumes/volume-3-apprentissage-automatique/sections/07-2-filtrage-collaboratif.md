## 7.2 Filtrage collaboratif : les méthodes de voisinage

Le filtrage par contenu regarde les **produits**. Le **filtrage collaboratif** regarde le **comportement collectif** : il recommande à un client ce qu'ont acheté des clients qui lui ressemblent, ou des produits qui ressemblent à ce qu'il a déjà acheté, sans jamais avoir besoin de savoir ce qu'est un produit. Cette section présente les méthodes les plus directes, dites de **voisinage**, qui n'ont pas de paramètres à ajuster au sens du chapitre 2 : tout le travail se joue dans la définition de la ressemblance et dans le nombre de voisins retenus.

### 7.2.1 L'intelligence collective

L'idée tient en une phrase : *les gens qui ont aimé les mêmes choses dans le passé aimeront probablement les mêmes choses dans l'avenir*. Elle se décline de deux façons symétriques.

- Les **voisins de clients** (*user-user*) : pour recommander au client $u$, on cherche les $k$ clients dont l'historique ressemble le plus au sien, et on lui propose ce qu'ils ont acheté et qu'il n'a pas encore acheté.
- Les **voisins de produits** (*item-item*) : pour chaque produit candidat, on mesure sa ressemblance avec les produits que $u$ a déjà achetés. Deux produits se ressemblent s'ils sont **achetés par les mêmes clients**.

Dans les deux cas, la ressemblance est la similarité cosinus de la section 7.1.4, appliquée soit aux lignes de la matrice $R$ (les clients), soit à ses colonnes (les produits).

### 7.2.2 Les voisins de clients

**Retours implicites.** Pour des achats binaires, on retient pour chaque client $u$ l'ensemble $N_k(u)$ de ses $k$ voisins les plus proches (au sens du cosinus), puis on attribue à chaque produit $i$ le score
$$\hat s_{ui}=\sum_{v\in N_k(u)}\operatorname{sim}(u,v)\,R_{vi}.$$
Un produit est bien classé s'il a été acheté par beaucoup de voisins, d'autant plus proches de $u$ que leur similarité est élevée. On ne classe que les produits que $u$ n'a pas déjà achetés.

**Retours explicites.** Avec des notes, une difficulté apparaît : certains clients notent toujours haut, d'autres toujours bas. On corrige ce biais en **centrant** les notes sur la moyenne de chaque client, $\bar r_u$, et on prédit
$$\hat r_{ui}=\bar r_u+\frac{\sum_{v\in N(u)}\operatorname{sim}(u,v)\,(r_{vi}-\bar r_v)}{\sum_{v\in N(u)}|\operatorname{sim}(u,v)|}.$$
La note prédite est la moyenne du client plus la moyenne **pondérée** des écarts que ses voisins ont à leur propre moyenne.

**À la main.** Quatre clients ont noté quatre produits (A à D) ; nous voulons prédire la note de $u_1$ pour le produit D.

| Client | A | B | C | D | Moyenne $\bar r$ |
|---|:-:|:-:|:-:|:-:|:-:|
| $u_1$ (cible) | 5 | 3 | 4 | ? | 4,00 |
| $u_2$ | 4 | 2 | 5 | 4 | 3,75 |
| $u_3$ | 2 | 5 | 1 | 2 | 2,50 |
| $u_4$ | 5 | 4 | 4 | 5 | 4,50 |

On mesure la ressemblance sur les produits notés par les deux clients (A, B, C), après centrage. Le vecteur centré de $u_1$ est $(1,-1,0)$, de norme $\sqrt2\approx1{,}414$. Pour $u_2$ : $(0{,}25,-1{,}75,1{,}25)$, de norme $\approx2{,}165$, et le produit scalaire avec $u_1$ vaut $0{,}25+1{,}75=2$, d'où $\operatorname{sim}(u_1,u_2)=\dfrac{2}{1{,}414\times2{,}165}\approx0{,}653$. De même $\operatorname{sim}(u_1,u_3)\approx-0{,}717$ (goûts opposés) et $\operatorname{sim}(u_1,u_4)\approx0{,}816$.

Chacun a noté le produit D ; l'écart de leur note à leur moyenne vaut $+0{,}25$ pour $u_2$, $-0{,}5$ pour $u_3$ et $+0{,}5$ pour $u_4$. La prédiction est donc
$$\hat r_{1D}=4+\frac{0{,}653\times0{,}25+(-0{,}717)\times(-0{,}5)+0{,}816\times0{,}5}{0{,}653+0{,}717+0{,}816}=4+\frac{0{,}930}{2{,}187}\approx4{,}43.$$

```python hide
notes = np.array([[5, 3, 4, np.nan], [4, 2, 5, 4], [2, 5, 1, 2], [5, 4, 4, 5]])
moy = np.nanmean(notes, axis=1)
cent = notes - moy[:, None]
sims = []
for v in (1, 2, 3):
    a, b = cent[0, :3], cent[v, :3]
    sims.append(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))
sims = np.array(sims)
ecarts = cent[1:, 3]
pred = moy[0] + (sims * ecarts).sum() / np.abs(sims).sum()
print("moyennes", moy.round(3), "| similarités", sims.round(3), "| écarts", ecarts, "| numérateur", round((sims * ecarts).sum(), 3), "| dénominateur", round(np.abs(sims).sum(), 3), "| prédiction", round(pred, 3))
```
<!--sortie-->
```text
moyennes [4.   3.75 2.5  4.5 ] | similarités [ 0.653 -0.717  0.816] | écarts [ 0.25 -0.5   0.5 ] | numérateur 0.93 | dénominateur 2.187 | prédiction 4.425
```

Remarquez le rôle de $u_3$ : ses goûts sont opposés à ceux de $u_1$ (similarité négative) et il a mal noté D ; le signe négatif de la similarité transforme cette mauvaise note en un argument **en faveur** de D. En pratique on écarte souvent les voisins de similarité négative, car cette inférence (« il n'aime pas ce que j'aime, donc ce qu'il déteste me plaira ») est fragile.

### 7.2.3 Les voisins de produits

L'approche symétrique raisonne sur les **colonnes**. Notons $I_u$ l'ensemble des produits achetés par $u$. Le score d'un produit candidat $j$ est la somme de ses ressemblances avec les produits de $I_u$ :
$$\hat s_{uj}=\sum_{i\in I_u}\operatorname{sim}(i,j).$$
On peut ne retenir, pour chaque produit $j$, que ses $k$ produits les plus proches (ses **voisins**) ; les autres similarités sont mises à zéro. Matriciellement, en notant $S$ la matrice des similarités entre produits (diagonale nulle), tout le calcul est un produit de matrices : $\hat S=R\,S$.

**À la main.** Reprenons le petit tableau de 7.1.3 (5 clients, 6 produits) et calculons les similarités nécessaires avec $\cos(i,j)=n_{ij}/\sqrt{n_in_j}$. Les nombres d'acheteurs sont $(4,3,3,4,2,1)$. Le client U1, qui a acheté P1, P2 et P4, a trois produits candidats :

- **P3** : $\cos(\text{P3},\text{P1})=\dfrac{2}{\sqrt{12}}=0{,}577$, $\cos(\text{P3},\text{P2})=\dfrac{1}{\sqrt9}=0{,}333$, $\cos(\text{P3},\text{P4})=\dfrac{3}{\sqrt{12}}=0{,}866$. Score : $1{,}777$.
- **P5** : $\dfrac{1}{\sqrt8}=0{,}354$, $\dfrac{1}{\sqrt6}=0{,}408$, $\dfrac{2}{\sqrt8}=0{,}707$. Score : $1{,}469$.
- **P6** : $\dfrac{1}{\sqrt4}=0{,}5$, $\dfrac{1}{\sqrt3}=0{,}577$, $0$. Score : $1{,}077$.

Le classement est P3, P5, P6. Ici, il coïncide avec celui de la popularité ; la personnalisation ne devient visible que sur des historiques plus variés, comme ceux de la boutique.

```python hide
def sim_items(M):
    n = M.sum(axis=0); co = M.T @ M
    S = co / np.sqrt(np.outer(n, n)); np.fill_diagonal(S, 0); return S
S5 = sim_items(M)
u1 = M[0]
sc = u1 @ S5
print("scores U1 (P3, P5, P6) :", sc[[2, 4, 5]].round(3), "| détail P3 :", S5[2, [0, 1, 3]].round(3), "| P5 :", S5[4, [0, 1, 3]].round(3), "| P6 :", S5[5, [0, 1, 3]].round(3))
```
<!--sortie-->
```text
scores U1 (P3, P5, P6) : [1.777 1.469 1.077] | détail P3 : [0.577 0.333 0.866] | P5 : [0.354 0.408 0.707] | P6 : [0.5   0.577 0.   ]
```

> 💡 **Pourquoi on préfère souvent les voisins de produits.** Dans une boutique, le catalogue (150 produits) est bien plus petit et plus **stable** que la clientèle (3 000 clients, qui changent d'une semaine à l'autre) : la matrice de similarités entre produits est petite et évolue lentement, on peut donc la calculer à l'avance. Un client n'a de plus que quelques achats, ce qui rend la mesure de sa ressemblance avec les autres clients bruitée, alors que la ressemblance de deux produits s'appuie sur tous les clients qui les ont achetés. Enfin, les recommandations sont faciles à expliquer : « parce que vous avez acheté P1 ».

Voici ce calcul sur les données de la boutique. Une seule fonction de bibliothèque suffit pour la similarité, un produit de matrices pour les scores :

```python hide
R_train = d["R_train"]
```

```python
from sklearn.metrics.pairwise import cosine_similarity

S = cosine_similarity(R_train.T)       # similarité entre produits (colonnes de R)
np.fill_diagonal(S, 0)
scores = R_train @ S                   # score du produit j pour le client u : somme des similarités
```

```python hide
from sklearn.metrics.pairwise import cosine_similarity
S = cosine_similarity(R_train.T)
np.fill_diagonal(S, 0)
scores = np.asarray(R_train @ S)
print("même résultat que la fonction du chapitre :", np.allclose(scores, scores_voisins_articles(R_train, k=149, shrink=0)))
```
<!--sortie-->
```text
même résultat que la fonction du chapitre : True
```

### 7.2.4 Rétrécissement et choix du voisinage

Une similarité calculée sur peu de données est peu fiable. Imaginez deux paires de produits : la paire $a$ a un cosinus de 0,8 obtenu sur seulement $n_{ij}=2$ clients communs ; la paire $b$ a un cosinus de 0,6 obtenu sur 40 clients communs. Laquelle croire ? Plutôt la seconde, malgré sa valeur plus faible, parce que 0,8 sur deux clients peut être une coïncidence.

Le **rétrécissement** (*shrinkage*) traduit cette intuition : on multiplie la similarité par un facteur qui tend vers 0 quand le nombre de co-achats est faible,
$$\operatorname{sim}'(i,j)=\operatorname{sim}(i,j)\times\frac{n_{ij}}{n_{ij}+\lambda},$$
où $\lambda>0$ est un paramètre de prudence. Avec $\lambda=10$, la paire $a$ devient $0{,}8\times\frac{2}{12}\approx0{,}133$ et la paire $b$ devient $0{,}6\times\frac{40}{50}=0{,}48$ : leur ordre s'**inverse**. C'est le même principe que la régularisation du chapitre 2 (section 2.1) : on tire vers zéro les estimations les moins fiables.

Il reste deux réglages : le **nombre de voisins** $k$ (trop petit, on gaspille de l'information ; trop grand, on dilue le signal avec des voisins peu ressemblants) et le coefficient $\lambda$. Ce sont des hyperparamètres : on les choisit sur le **jeu de validation**, jamais sur le jeu de test (chapitre 1, section 1.1 et section 1.5).

```python hide
k_art = [5, 10, 20, 50, 149]
shr = [0, 10, 50]
k_cli = [10, 30, 100, 300, 500, 1000]
Rt, Rv = d["R_train"], d["val"]
lignes = []
for sh in shr:
    for k in k_art:
        m = resume(evaluer(scores_voisins_articles(Rt, k, sh), Rt, Rv, d["users"]))
        lignes.append({"méthode": "produits", "k": k, "rétrécissement": sh, "rappel@10": m.rappel, "NDCG@10": m.ndcg})
for k in k_cli:
    m = resume(evaluer(scores_voisins_clients(Rt, k), Rt, Rv, d["users"]))
    lignes.append({"méthode": "clients", "k": k, "rétrécissement": 0, "rappel@10": m.rappel, "NDCG@10": m.ndcg})
grille_voisins = pd.DataFrame(lignes)
ref_pop = resume(evaluer(scores_popularite(Rt), Rt, Rv, d["users"]))
meilleur_art = grille_voisins[grille_voisins["méthode"] == "produits"].sort_values("NDCG@10", ascending=False).iloc[0]
meilleur_cli = grille_voisins[grille_voisins["méthode"] == "clients"].sort_values("NDCG@10", ascending=False).iloc[0]
choix = {"art": (int(meilleur_art["k"]), int(meilleur_art["rétrécissement"])), "cli": int(meilleur_cli["k"])}
co = (Rt.T @ Rt).toarray(); iu = np.triu_indices(150, 1)
print("co-achats par paire de produits : médiane", int(np.median(co[iu])), ", minimum", int(co[iu].min()), ", part des paires avec moins de 10 co-achats", round((co[iu] < 10).mean(), 3))
print("popularité : rappel", round(ref_pop.rappel, 4), "NDCG", round(ref_pop.ndcg, 4))
print(grille_voisins.round(4).to_string(index=False))
print("meilleurs :", choix, "| NDCG art", round(meilleur_art["NDCG@10"], 4), "cli", round(meilleur_cli["NDCG@10"], 4))
```
<!--sortie-->
```text
co-achats par paire de produits : médiane 3 , minimum 0 , part des paires avec moins de 10 co-achats 0.845
popularité : rappel 0.2409 NDCG 0.1431
 méthode    k  rétrécissement  rappel@10  NDCG@10
produits    5               0     0.2204   0.1406
produits   10               0     0.2401   0.1526
produits   20               0     0.2498   0.1557
produits   50               0     0.2554   0.1564
produits  149               0     0.2583   0.1584
produits    5              10     0.2357   0.1483
produits   10              10     0.2456   0.1531
produits   20              10     0.2514   0.1559
produits   50              10     0.2515   0.1560
produits  149              10     0.2563   0.1578
produits    5              50     0.2343   0.1466
produits   10              50     0.2426   0.1516
produits   20              50     0.2525   0.1559
produits   50              50     0.2521   0.1557
produits  149              50     0.2538   0.1563
 clients   10               0     0.1651   0.0990
 clients   30               0     0.2147   0.1337
 clients  100               0     0.2589   0.1587
 clients  300               0     0.2715   0.1646
 clients  500               0     0.2654   0.1614
 clients 1000               0     0.2604   0.1567
meilleurs : {'art': (149, 0), 'cli': 300} | NDCG art 0.1584 cli 0.1646
```

```python hide
fig, ax = plt.subplots(1, 2, figsize=(10.5, 3.8), sharey=True)
for sh, col in zip(shr, (BLEU, ORANGE, AQUA)):
    g = grille_voisins[(grille_voisins["méthode"] == "produits") & (grille_voisins["rétrécissement"] == sh)]
    ax[0].plot(g["k"], g["NDCG@10"], "o-", color=col, label=f"rétrécissement {sh}")
g = grille_voisins[grille_voisins["méthode"] == "clients"]
ax[1].plot(g["k"], g["NDCG@10"], "o-", color=VIOLET, label="voisins de clients")
for a in ax:
    a.axhline(ref_pop.ndcg, color=MUET, ls="--", lw=1.2)
    a.set_xscale("log"); a.set_xlabel("nombre de voisins k (échelle logarithmique)")
    a.legend(frameon=False, loc="lower right", fontsize=9)
ax[0].text(40, ref_pop.ndcg - 0.0045, "popularité (référence)", color=MUET, fontsize=9)
ax[0].set_ylabel("NDCG@10 sur la validation"); ax[0].set_title("Voisins de produits"); ax[1].set_title("Voisins de clients")
plt.tight_layout(); plt.savefig("figures/ch07-reglage-voisins.png", dpi=200, bbox_inches="tight"); plt.close()
```

![NDCG@10 sur le jeu de validation selon le nombre de voisins retenus. À gauche, voisins de produits pour trois valeurs du rétrécissement ; à droite, voisins de clients. La ligne en tirets est la popularité.](figures/ch07-reglage-voisins.png)

### 7.2.5 Premiers résultats et limites

La figure et la grille donnent plusieurs enseignements.

- **La popularité est battue, mais de peu.** Elle obtient un NDCG@10 de 0,143 (rappel@10 de 24,1 %). Les voisins de produits, bien réglés, atteignent 0,158 (rappel de 25,8 %) et les voisins de clients 0,165 (rappel de 27,2 %).
- **Un voisinage trop étroit fait perdre.** Avec 5 produits voisins seulement, les voisins de produits tombent à 0,141 : **en dessous de la popularité**. Avec 10 voisins de clients, on tombe à 0,099. Le meilleur réglage garde tous les produits (149 voisins) ou 300 clients voisins : avec un catalogue de 150 produits, restreindre le voisinage jette presque toute l'information.
- **Le rétrécissement aide quand le voisinage est étroit, pas quand il est large.** Avec $k=5$ voisins de produits, passer de $\lambda=0$ à $\lambda=10$ fait passer le NDCG de 0,141 à 0,148 ; avec tous les voisins, il n'apporte plus rien (0,158 dans les deux cas). Les paires de produits ont en effet **peu de co-achats** sur l'entraînement (médiane de 3, et 84,5 % des paires en ont moins de 10) : chaque similarité est bruitée, mais le bruit se moyenne quand on additionne les similarités avec tous les produits du client.
- **Au-delà de 300 voisins de clients, on dilue** : le NDCG redescend à 0,157 pour 1 000 voisins.
- **L'écart entre les deux méthodes est petit** (0,006 de NDCG) : le jeu de validation compte 2 365 clients, ce qui ne permet pas de conclure laquelle est meilleure. Nous attendrons l'intervalle de confiance de 7.4.2.

> ⚠️ **Choisir un hyperparamètre sur la validation, puis le juger sur le test.** Les chiffres ci-dessus sont ceux de la **validation**, utilisée pour choisir $k$ et $\lambda$ : ils sont légèrement optimistes (on a gardé le meilleur de plusieurs essais). La comparaison honnête de toutes les méthodes se fera en 7.4.2, sur le jeu de test, avec des modèles réentraînés sur l'entraînement **et** la validation.

**Le coût de calcul.** Les voisins de produits demandent la matrice des similarités entre produits : pour $m$ produits, $m(m-1)/2$ paires, soit 11 175 ici, un calcul instantané. Les voisins de clients demandent les similarités entre clients : pour $n$ clients, $n(n-1)/2$ paires, soit environ 4,5 millions ici (3 000 clients). Pour un site de plusieurs millions de clients, cette matrice ne tient plus en mémoire : on passe à des méthodes de **voisins approchés** ou, plus souvent, à la factorisation de la section 7.3. Le nombre d'opérations pour une matrice creuse dépend de la somme des carrés des tailles d'historique, $\sum_u d_u^2$ pour les voisins de produits, où $d_u$ est le nombre d'achats du client $u$ : un client très actif pèse plus lourd que tous les autres.

**Les limites.** Les méthodes de voisinage sont simples, interprétables et difficiles à battre, mais elles ne **généralisent** pas : deux produits ne sont liés que s'ils ont des clients communs, de sorte qu'un produit peu acheté, ou un client sans historique, restent sans recommandation. Elles suivent aussi la popularité (les produits très achetés ont des voisins nombreux) : nous mesurerons ce biais en 7.4.4. La factorisation matricielle répond à une partie de ces limites en résumant chaque client et chaque produit par quelques facteurs latents.

> ✅ **À retenir (7.2).**
> - Le filtrage collaboratif recommande à partir du **comportement collectif** : voisins de clients (lignes de $R$) ou voisins de produits (colonnes de $R$), avec la similarité cosinus.
> - Pour les achats binaires, $\hat s_{uj}=\sum_{i\in I_u}\operatorname{sim}(i,j)$ ; avec des notes, on **centre** par la moyenne du client.
> - Le **rétrécissement** $n_{ij}/(n_{ij}+\lambda)$ protège des similarités calculées sur peu de co-achats ; $k$ et $\lambda$ se choisissent sur la **validation**.
> - Les voisins de produits sont plus stables et plus faciles à expliquer ; les deux approches ne recommandent rien sans co-achats.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : application 7.2 (voisins écrits à la main, rétrécissement), exercices 7.4 à 7.6.
