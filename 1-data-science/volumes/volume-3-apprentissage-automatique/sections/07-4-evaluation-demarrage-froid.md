## 7.4 Évaluation et démarrage à froid

Les trois sections précédentes ont comparé des méthodes sur le jeu de validation, avec des métriques annoncées mais pas encore définies. Cette dernière section fait le travail de rigueur qui, depuis le chapitre 1, est le fil rouge du volume : définir précisément ce que l'on mesure, comparer **honnêtement** les méthodes sur le jeu de test, s'interroger sur ce que ces chiffres ne disent pas, et regarder ce qui arrive quand le client ou le produit est **nouveau**.

### 7.4.1 Évaluer un classement

Pour un client donné, un système produit une liste ordonnée de $k$ produits (ici $k=10$). On dispose de l'ensemble des produits **pertinents** pour ce client : ceux qu'il a effectivement achetés et que l'on avait mis de côté (jeu de test). Cinq métriques complémentaires comparent la liste à cet ensemble.

- **Précision@k** : part des $k$ produits recommandés qui sont pertinents. Elle répond à : « combien de ma vitrine sert-elle ? ».
- **Rappel@k** : part des produits pertinents qui figurent dans la liste. Elle répond à : « quelle part de ce que le client voulait ai-je trouvée ? ».
- **Taux de succès@k** (*hit rate*) : part des clients pour lesquels **au moins un** produit pertinent figure dans la liste.
- **MAP@k** (*mean average precision*) : pour chaque client, on moyenne la précision aux rangs où apparaît un produit pertinent, puis on moyenne sur les clients. Elle récompense de **placer les bons produits haut**.
- **NDCG@k** (*normalised discounted cumulative gain*) : on attribue à chaque produit pertinent un gain $1/\log_2(\text{rang}+1)$, qui décroît avec le rang ; on somme (DCG), puis on divise par la valeur maximale possible (IDCG) pour obtenir un nombre entre 0 et 1.

**À la main.** Une liste de $k=5$ produits, dont les deuxième et quatrième sont pertinents ; le client avait en tout **3** produits pertinents dans le jeu de test (le troisième n'a pas été recommandé).

| Rang | 1 | 2 | 3 | 4 | 5 |
|---|:-:|:-:|:-:|:-:|:-:|
| Pertinent ? | non | **oui** | non | **oui** | non |

- Précision@5 $=2/5=0{,}4$ ; rappel@5 $=2/3\approx0{,}667$ ; succès@5 $=1$.
- Précision aux rangs des succès : $1/2$ au rang 2, $2/4$ au rang 4. La précision moyenne (AP) est la somme de ces précisions divisée par le nombre de produits pertinents (borné par $k$), soit $(0{,}5+0{,}5)/3\approx0{,}333$.
- DCG $=\dfrac1{\log_23}+\dfrac1{\log_25}=0{,}631+0{,}431=1{,}062$. Le meilleur classement possible placerait les 3 produits pertinents aux rangs 1, 2 et 3 : IDCG $=1+0{,}631+0{,}5=2{,}131$. Donc NDCG@5 $=1{,}062/2{,}131\approx0{,}498$.

```python hide
rel = np.array([0, 1, 0, 1, 0]); n_rel = 3; k = 5
rangs = np.arange(1, k + 1); gain = 1 / np.log2(rangs + 1)
dcg = (rel * gain).sum(); idcg = gain[:min(n_rel, k)].sum()
ap = (rel * np.cumsum(rel) / rangs).sum() / min(n_rel, k)
print("précision", rel.sum() / k, "| rappel", round(rel.sum() / n_rel, 4), "| AP", round(ap, 4), "| DCG", round(dcg, 4), "| IDCG", round(idcg, 4), "| NDCG", round(dcg / idcg, 4))
print("gains aux rangs 1 à 5 :", gain.round(4))
```
<!--sortie-->
```text
précision 0.4 | rappel 0.6667 | AP 0.3333 | DCG 1.0616 | IDCG 2.1309 | NDCG 0.4982
gains aux rangs 1 à 5 : [1.     0.6309 0.5    0.4307 0.3869]
```

> 💡 **Quelle métrique choisir ?** Cela dépend de l'usage. Si l'on affiche une longue liste que le client parcourt, le **rappel** compte. Si la vitrine ne montre que trois produits, la **précision** et la position (**NDCG**, **MAP**) comptent. Aucune ne remplace la mesure commerciale finale (panier, conversion) : elles ne sont que des indicateurs hors ligne. Dans la suite, nous retenons le **NDCG@10** comme métrique principale et le **rappel@10** comme métrique de lecture facile.

> ⚠️ **Le « faux négatif » de l'évaluation.** Un produit recommandé que le client n'a pas acheté compte comme une erreur, alors qu'il est peut-être un excellent choix qu'il n'avait pas vu. L'évaluation sur achats cachés **sous-estime** donc la qualité réelle de tout système, et pénalise davantage ceux qui recommandent des produits peu connus (7.4.4).

### 7.4.2 Un protocole honnête et des comparaisons avec incertitude

Voici la comparaison finale. Elle suit la discipline du chapitre 1 :

1. les hyperparamètres ont été choisis sur la **validation** (sections 7.2 et 7.3) ;
2. chaque méthode est maintenant **réentraînée sur l'entraînement et la validation réunis** (tout sauf le jeu de test) ;
3. elle est évaluée **une seule fois** sur le jeu de test, qui n'a servi à aucun choix ;
4. chaque métrique est accompagnée d'un **intervalle de confiance** obtenu par bootstrap sur les clients (volume I, section 3.3.5).

```python hide
Rtv, Tt, users = d["R_trainval"], d["test"], d["users"]
k_a, sh_a = choix["art"]; k_c = choix["cli"]; k_f, lam_f = choix["als"]; k_s = choix["svd"]
modeles = {
    "Au hasard": scores_aleatoire(Rtv),
    "Popularité": scores_popularite(Rtv),
    "Contenu": scores_contenu(Rtv, prod),
    "Voisins de produits": scores_voisins_articles(Rtv, k_a, sh_a),
    "Voisins de clients": scores_voisins_clients(Rtv, k_c),
    "SVD tronquée": scores_svd(Rtv, k=k_s),
    "ALS implicite": scores_als(Rtv, k=k_f, lam=lam_f, alpha=8.0, n_iter=10, seed=0),
}
par_client = {nom: evaluer(S, Rtv, Tt, users) for nom, S in modeles.items()}
lignes = []
for nom, df in par_client.items():
    m = resume(df)
    ic_n = ic_bootstrap(df["ndcg"].values); ic_r = ic_bootstrap(df["rappel"].values)
    lignes.append({"méthode": nom, "précision@10": m.precision, "rappel@10": m.rappel, "IC rappel": f"[{ic_r[0]:.3f} ; {ic_r[1]:.3f}]",
                   "NDCG@10": m.ndcg, "IC NDCG": f"[{ic_n[0]:.3f} ; {ic_n[1]:.3f}]", "MAP@10": m.ap})
tab_test = pd.DataFrame(lignes)
print(tab_test.round(3).to_string(index=False))
print("clients évalués :", len(users), "| achats de test :", int(Tt.nnz))
```
<!--sortie-->
```text
            méthode  précision@10  rappel@10       IC rappel  NDCG@10         IC NDCG  MAP@10
          Au hasard         0.020      0.070 [0.063 ; 0.077]    0.044 [0.039 ; 0.048]   0.022
         Popularité         0.066      0.244 [0.232 ; 0.256]    0.174 [0.165 ; 0.182]   0.103
            Contenu         0.036      0.122 [0.113 ; 0.130]    0.075 [0.069 ; 0.080]   0.038
Voisins de produits         0.079      0.270 [0.258 ; 0.282]    0.199 [0.189 ; 0.208]   0.122
 Voisins de clients         0.083      0.288 [0.275 ; 0.300]    0.209 [0.200 ; 0.218]   0.128
       SVD tronquée         0.074      0.255 [0.243 ; 0.267]    0.179 [0.171 ; 0.188]   0.106
      ALS implicite         0.084      0.295 [0.282 ; 0.307]    0.216 [0.206 ; 0.225]   0.133
clients évalués : 2365 | achats de test : 6523
```

```python hide-code
print(tab_test[["méthode", "rappel@10", "IC rappel", "NDCG@10", "IC NDCG"]].round(3).to_string(index=False))
```
<!--sortie-->
```text
            méthode  rappel@10       IC rappel  NDCG@10         IC NDCG
          Au hasard      0.070 [0.063 ; 0.077]    0.044 [0.039 ; 0.048]
         Popularité      0.244 [0.232 ; 0.256]    0.174 [0.165 ; 0.182]
            Contenu      0.122 [0.113 ; 0.130]    0.075 [0.069 ; 0.080]
Voisins de produits      0.270 [0.258 ; 0.282]    0.199 [0.189 ; 0.208]
 Voisins de clients      0.288 [0.275 ; 0.300]    0.209 [0.200 ; 0.218]
       SVD tronquée      0.255 [0.243 ; 0.267]    0.179 [0.171 ; 0.188]
      ALS implicite      0.295 [0.282 ; 0.307]    0.216 [0.206 ; 0.225]
```

```python hide-code
def diff_ic(a, b, col="ndcg", B=2000, seed=0):
    dd = par_client[a][col].values - par_client[b][col].values
    lo, hi = ic_bootstrap(dd, B=B, seed=seed)
    return dd.mean(), lo, hi
paires = [("ALS implicite", "Popularité"), ("Voisins de clients", "Popularité"), ("Voisins de produits", "Popularité"),
          ("ALS implicite", "Voisins de clients"), ("ALS implicite", "Voisins de produits"), ("SVD tronquée", "Popularité")]
tab_diff = pd.DataFrame([{"comparaison": f"{a} − {b}", "écart NDCG@10": diff_ic(a, b)[0], "IC 95 %": f"[{diff_ic(a, b)[1]:.3f} ; {diff_ic(a, b)[2]:.3f}]"} for a, b in paires])
print(tab_diff.round(4).to_string(index=False))
a_, p_ = par_client["ALS implicite"]["ndcg"].values, par_client["Popularité"]["ndcg"].values
print("clients : ALS meilleur", round((a_ > p_).mean(), 3), "| égalité", round((a_ == p_).mean(), 3), "dont les deux à zéro", round(((a_ == p_) & (a_ == 0)).mean(), 3), "| ALS moins bon", round((a_ < p_).mean(), 3))
```
<!--sortie-->
```text
                        comparaison  écart NDCG@10          IC 95 %
         ALS implicite − Popularité         0.0420  [0.036 ; 0.048]
    Voisins de clients − Popularité         0.0352  [0.030 ; 0.041]
   Voisins de produits − Popularité         0.0250  [0.018 ; 0.031]
 ALS implicite − Voisins de clients         0.0068  [0.002 ; 0.011]
ALS implicite − Voisins de produits         0.0169  [0.011 ; 0.022]
          SVD tronquée − Popularité         0.0053 [-0.005 ; 0.015]
clients : ALS meilleur 0.391 | égalité 0.446 dont les deux à zéro 0.362 | ALS moins bon 0.163
```

```python hide
fig, ax = plt.subplots(1, 2, figsize=(10.5, 3.9), sharey=True)
ordre = list(par_client)
for a, (col, titre) in zip(ax, (("ndcg", "NDCG@10"), ("rappel", "rappel@10"))):
    moy = np.array([par_client[n][col].mean() for n in ordre])
    ic = np.array([ic_bootstrap(par_client[n][col].values) for n in ordre])
    couleurs = [MUET, ORANGE, AQUA, BLEU, BLEU, VIOLET, ROUGE]
    a.barh(range(len(ordre)), moy, xerr=[moy - ic[:, 0], ic[:, 1] - moy], color=couleurs, capsize=3, ecolor=style.ENCRE2)
    a.set_yticks(range(len(ordre))); a.set_yticklabels(ordre); a.invert_yaxis(); a.set_xlabel(titre + " sur le jeu de test (avec IC à 95 %)")
    for i, v in enumerate(moy):
        a.text(ic[i, 1] + 0.004, i, f"{v:.3f}", va="center", fontsize=9, color=style.ENCRE2)
    a.set_xlim(0, moy.max() * 1.35)
plt.tight_layout(); plt.savefig("figures/ch07-comparaison-modeles.png", dpi=200, bbox_inches="tight"); plt.close()
```

![Performance des sept méthodes sur le jeu de test (2 365 clients) : NDCG@10 à gauche, rappel@10 à droite, avec l'intervalle de confiance à 95 % obtenu par bootstrap sur les clients.](figures/ch07-comparaison-modeles.png)

On y lit quatre choses.

- **Toutes les méthodes personnalisées battent le hasard et la popularité, sauf la SVD tronquée** (NDCG 0,179 contre 0,174 pour la popularité : écart non significatif, voir plus bas).
- **L'ALS implicite est la meilleure** : NDCG@10 de **0,216** (intervalle de confiance [0,206 ; 0,225]) et rappel@10 de **29,5 %**. En moyenne, 0,84 des dix produits recommandés correspond à un achat caché (précision@10 de 0,084), et près de trois achats cachés sur dix sont retrouvés. Les voisins de clients (0,209) et les voisins de produits (0,199) suivent ; la popularité atteint 0,174 (rappel de 24,4 %). Le gain de la meilleure méthode sur la référence est donc de **4 points de NDCG** et de **5 points de rappel** : réel, mais ce n'est pas une révolution.
- **Le contenu seul est loin derrière** (0,075), bien au-dessus du hasard (0,044) mais en dessous de la popularité.
- **Les niveaux du test ne se comparent pas à ceux de la validation** (0,216 contre 0,168 pour l'ALS) : le test cache davantage d'achats par client (6 523 au total contre 3 987), ce qui facilite la tâche, et les modèles sont réentraînés avec 23 % d'achats de plus. Seules les comparaisons entre méthodes **sur un même jeu** ont un sens.

Les intervalles de confiance de deux méthodes peuvent se chevaucher alors que leur **différence** est significative : les deux méthodes sont évaluées sur les **mêmes clients**, et la comparaison est **appariée** (chapitre 1, section 1.4). On calcule donc, client par client, la différence de leur NDCG, puis un intervalle de confiance de la moyenne de cette différence.

Les écarts se lisent ainsi :

- **L'ALS bat nettement la popularité** : $+0{,}042$ de NDCG, avec un intervalle de [0,036 ; 0,048] qui est loin de zéro.
- **L'ALS bat aussi les voisins de clients**, de peu : $+0{,}0068$, intervalle [0,002 ; 0,011]. L'intervalle exclut zéro, donc sur ces données la factorisation est très probablement un peu meilleure ; il faut toutefois nuancer, car ce résultat porte sur **un seul jeu de données** et **une seule initialisation** de l'ALS. En validation, nous n'avions pas pu départager les deux méthodes ; le jeu de test, plus gros, le permet de justesse.
- **La SVD tronquée ne se distingue pas de la popularité** : $+0{,}005$, intervalle [−0,005 ; 0,015] qui contient zéro.
- **L'avantage moyen cache des situations très inégales.** L'ALS fait mieux que la popularité pour **39,1 %** des clients, moins bien pour **16,3 %**, et fait **jeu égal** pour 44,6 %, dont 36,2 points où ni l'une ni l'autre ne retrouve aucun achat. Le gain moyen est le fruit d'un avantage net sur une minorité de clients.

### 7.4.3 Pourquoi un découpage aléatoire peut tromper

Nous avons évalué en retirant des achats **au hasard**, client par client. Dans un vrai projet, les achats ont des dates, et ce découpage pose un problème : le jeu d'entraînement contient des achats **postérieurs** à certains achats du jeu de test. Le modèle « voit l'avenir » : il connaît, par exemple, la popularité qu'aura un produit au moment où on lui demande de la prédire. Le chapitre 1 (section 1.1) l'a dit pour les modèles supervisés ; c'est encore plus net en recommandation, où les goûts et les catalogues changent.

Nos données n'ont pas de dates : nous ne pouvons pas mesurer l'écart. Simulons donc un monde où le temps existe. 2 000 clients et 100 produits, deux périodes ; entre les deux, la popularité de **30 produits** change nettement (certains montent, d'autres chutent). Le but est de prédire les achats de la **seconde** période de produits que le client n'avait pas achetés dans la première. Deux protocoles :

- **découpage aléatoire** : on mélange les deux périodes, on retire 25 % des achats de chaque client au hasard, on entraîne sur le reste ;
- **découpage temporel** : on entraîne sur la première période et on teste sur la seconde.

```python hide
R1, R2 = monde_en_derive()
Rall = ((R1 + R2) > 0).astype(float).tocsr()
d_s = decouper(Rall, seed=3, part_test=0.25, part_val=0.0001)
T2 = (R2 - R2.multiply(R1)).tocsr(); T2.eliminate_zeros()
us2 = np.where(np.asarray(T2.sum(axis=1)).ravel() >= 1)[0]
mods = {"Popularité": scores_popularite, "Voisins de produits": lambda R: scores_voisins_articles(R, 20, 10), "ALS implicite": lambda R: scores_als(R, k=4, lam=30, alpha=8.0, n_iter=8)}
res_derive = {}
for nom, f in mods.items():
    a = resume(evaluer(f(d_s["R_trainval"]), d_s["R_trainval"], d_s["test"], d_s["users"]))
    b = resume(evaluer(f(R1.tocsr()), R1.tocsr(), T2, us2))
    res_derive[nom] = (a.rappel, b.rappel)
tab_derive = pd.DataFrame(res_derive, index=["découpage aléatoire", "découpage temporel"]).T.rename_axis("méthode")
print(tab_derive.round(3).to_string())
print("achats période 1 :", int(R1.nnz), "| période 2 :", int(R2.nnz), "| clients évalués (aléatoire) :", len(d_s["users"]), "| (temporel) :", len(us2))
fig, ax = plt.subplots(figsize=(6.4, 3.8))
x = np.arange(3); w = 0.36
ax.bar(x - w / 2, tab_derive["découpage aléatoire"], w, color=ORANGE, label="découpage aléatoire")
ax.bar(x + w / 2, tab_derive["découpage temporel"], w, color=BLEU, label="découpage temporel")
for xi, (a_, b_) in zip(x, tab_derive.values):
    ax.text(xi - w / 2, a_ + 0.006, f"{a_:.2f}", ha="center", fontsize=9); ax.text(xi + w / 2, b_ + 0.006, f"{b_:.2f}", ha="center", fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(tab_derive.index); ax.set_ylabel("rappel@10"); ax.set_ylim(0, 0.5); ax.legend(frameon=False, loc="upper left")
ax.set_title("Un monde qui change : ce que le découpage aléatoire cache")
plt.tight_layout(); plt.savefig("figures/ch07-hasard-vs-temps.png", dpi=200, bbox_inches="tight"); plt.close()
```
<!--sortie-->
```text
                     découpage aléatoire  découpage temporel
méthode                                                     
Popularité                         0.328               0.221
Voisins de produits                0.397               0.259
ALS implicite                      0.398               0.260
achats période 1 : 11406 | période 2 : 14992 | clients évalués (aléatoire) : 1986 | (temporel) : 2000
```

```python hide-code
print(tab_derive.round(3).to_string())
```
<!--sortie-->
```text
                     découpage aléatoire  découpage temporel
méthode                                                     
Popularité                         0.328               0.221
Voisins de produits                0.397               0.259
ALS implicite                      0.398               0.260
```

![Rappel@10 de trois méthodes sur un monde simulé où la popularité de 30 produits change entre deux périodes, selon que l'on évalue avec un découpage aléatoire ou un découpage temporel.](figures/ch07-hasard-vs-temps.png)

Le découpage aléatoire **gonfle toutes les performances** : le rappel@10 de la popularité passe de 0,22 (temporel) à 0,33 (aléatoire), soit **48 % de plus** ; celui des voisins de produits de 0,26 à 0,40 (+53 %) et celui de l'ALS de 0,26 à 0,40 (+53 %). Le modèle entraîné sur un mélange des deux périodes connaît déjà les produits devenus populaires pendant la seconde, que le modèle « du passé » ne pouvait pas deviner. Et le découpage aléatoire **exagère aussi l'intérêt de la personnalisation** : l'ALS dépasse la popularité de 0,07 de rappel en évaluation aléatoire, de 0,04 seulement en évaluation temporelle. Le classement des méthodes reste le même (hyperparamètres fixés sans réglage dans cette simulation, une seule simulation).

> ⚠️ **Conséquence pratique.** Avec des données datées, on découpe **toujours dans le temps** : on entraîne sur le passé, on valide sur la période suivante, on teste sur la plus récente. C'est le même principe que la validation des séries temporelles (volume II, section 4.3). Notre évaluation par retrait aléatoire est donc, sur ce jeu sans dates, la meilleure option disponible, mais ses chiffres sont **optimistes en valeur absolue** ; les comparaisons entre méthodes y sont plus fiables que les niveaux.

### 7.4.4 Au-delà de la précision : couverture, nouveauté, biais de popularité

Une méthode qui recommande toujours les mêmes dix produits peut avoir un bon rappel et pourtant décevoir la gérante : le catalogue entier ne bénéficie pas de la vitrine, et les clients ne découvrent rien. Trois indicateurs complètent la précision.

- La **couverture** : part des 150 produits qui apparaissent au moins une fois dans une liste de dix.
- La **nouveauté** : le « degré de surprise » moyen des produits recommandés, mesuré par $-\log_2$ de leur part de popularité ; plus elle est élevée, plus on recommande des produits peu connus.
- La **diversité** d'une liste : part des paires de produits d'une même liste qui appartiennent à des catégories différentes.

```python hide
cat = prod["categorie"].to_numpy()
pop_part = np.asarray(Rtv.sum(axis=0)).ravel(); pop_part = pop_part / pop_part.sum()
top10_pop = set(np.argsort(-pop_part)[:10])
lig = []
for nom, df in par_client.items():
    L = np.vstack(df["recommandes"].values)
    couv = len(np.unique(L)) / 150
    nouv = (-np.log2(pop_part[L])).mean()
    part_top = np.mean([[i in top10_pop for i in row] for row in L])
    div = np.mean([np.mean([cat[a] != cat[b] for ia, a in enumerate(row) for b in row[ia + 1:]]) for row in L])
    lig.append({"méthode": nom, "NDCG@10": df["ndcg"].mean(), "couverture": couv, "nouveauté (bits)": nouv, "part des 10 plus populaires": part_top, "diversité": div})
tab_beyond = pd.DataFrame(lig)
print(tab_beyond.round(3).to_string(index=False))
```
<!--sortie-->
```text
            méthode  NDCG@10  couverture  nouveauté (bits)  part des 10 plus populaires  diversité
          Au hasard    0.044       1.000             7.695                        0.058      0.748
         Popularité    0.174       0.160             5.711                        0.827      0.801
            Contenu    0.075       1.000             7.741                        0.048      0.115
Voisins de produits    0.199       0.480             6.016                        0.433      0.614
 Voisins de clients    0.209       0.433             5.909                        0.536      0.704
       SVD tronquée    0.179       0.380             6.176                        0.356      0.577
      ALS implicite    0.216       0.340             5.903                        0.517      0.686
```

```python hide-code
print(tab_beyond.round(3).to_string(index=False))
```
<!--sortie-->
```text
            méthode  NDCG@10  couverture  nouveauté (bits)  part des 10 plus populaires  diversité
          Au hasard    0.044       1.000             7.695                        0.058      0.748
         Popularité    0.174       0.160             5.711                        0.827      0.801
            Contenu    0.075       1.000             7.741                        0.048      0.115
Voisins de produits    0.199       0.480             6.016                        0.433      0.614
 Voisins de clients    0.209       0.433             5.909                        0.536      0.704
       SVD tronquée    0.179       0.380             6.176                        0.356      0.577
      ALS implicite    0.216       0.340             5.903                        0.517      0.686
```

Les chiffres appellent quelques remarques.

- **La popularité est la moins variée** : seuls **24 produits sur 150** (16 %) apparaissent dans les listes, **83 %** des emplacements sont occupés par les dix produits les plus vendus, et la nouveauté est la plus basse (5,7 bits).
- **Parmi les méthodes personnalisées, la couverture est de 48 %** pour les voisins de produits, 43 % pour les voisins de clients, 38 % pour la SVD et **34 % pour l'ALS**. Celle qui a la meilleure précision est donc la moins variée de ce groupe : 52 % de ses emplacements sont occupés par les dix produits les plus populaires, contre 43 % pour les voisins de produits.
- **Le contenu couvre tout le catalogue** (100 %) avec la nouveauté la plus élevée (7,7 bits, comparable au hasard), mais sa **diversité** est de 0,12 : ses listes sont presque entièrement de **la même catégorie**, le client est enfermé dans ce qu'il a déjà acheté. C'est la « bulle de filtre ».
- **Le hasard a une couverture parfaite et ne sert à rien** (NDCG de 0,044) : un indicateur de variété ne dit rien de la qualité s'il est lu seul.

> 💡 **Le compromis précision-découverte.** Ces indicateurs vont rarement dans le même sens que la précision. Un système qui améliore la couverture et la nouveauté aide les produits de la longue traîne, mais il prend plus de risques sur chaque recommandation individuelle. Le bon réglage dépend d'un choix commercial (vendre plus aujourd'hui ou élargir les achats de demain) que la donnée seule ne tranche pas.

### 7.4.5 Le démarrage à froid

Toutes les méthodes précédentes ont besoin d'**historique**. Que faire face à un client qui n'a encore rien acheté, ou à un produit qui n'a pas encore été acheté par personne ? C'est le problème du **démarrage à froid** (*cold start*).

**Un nouveau client.** Plaçons-nous du point de vue d'un client dont on ne connaît que $m$ achats. On prend les clients ayant au moins 11 achats, on en met un quart à l'écart comme « nouveaux », on entraîne les modèles sur les autres, et on révèle aux nouveaux clients seulement $m$ de leurs achats (0, 1, 2, 3, 5 ou 8) : le but est de retrouver tous les autres. Pour l'ALS, le facteur d'un nouveau client se calcule en **une seule étape** de la section 7.3 (le *fold-in*), sans réentraîner le modèle. À $m=0$, aucune méthode personnalisée n'a rien à utiliser : elles retombent toutes sur la popularité.

```python hide
rng7 = np.random.default_rng(21)
Rc = R.tocsr(); nb_ach = np.asarray(Rc.sum(axis=1)).ravel()
eligibles = np.where(nb_ach >= 11)[0]
froids = np.sort(rng7.choice(eligibles, len(eligibles) // 4, replace=False))
R_tr = Rc.tolil(); R_tr[froids, :] = 0; R_tr = R_tr.tocsr(); R_tr.eliminate_zeros()
S_it = cosinus_colonnes(R_tr)
U_f, V_f = als_implicite(R_tr, k=k_f, lam=lam_f, alpha=8.0, n_iter=10, seed=0)
pop_tr = scores_popularite(R_tr)[0]
revele = {m: [] for m in (0, 1, 2, 3, 5, 8)}
res_froid = {nom: [] for nom in ("Popularité", "Voisins de produits", "ALS implicite")}
for m in revele:
    L_r, C_r, L_c, C_c = [], [], [], []
    S_p = np.zeros((3000, 150)); S_i = np.zeros((3000, 150)); S_a = np.zeros((3000, 150))
    for u in froids:
        items = rng7.permutation(Rc.indices[Rc.indptr[u]:Rc.indptr[u + 1]])
        vus, cibles = items[:m], items[m:]
        L_r += [u] * len(vus); C_r += list(vus); L_c += [u] * len(cibles); C_c += list(cibles)
        S_p[u] = pop_tr
        if m == 0:
            S_i[u] = pop_tr; S_a[u] = pop_tr
        else:
            S_i[u] = S_it[vus].sum(axis=0); S_a[u] = vecteur_client(V_f, vus, lam=lam_f, alpha=8.0) @ V_f.T
    Rv_ = sp.csr_matrix((np.ones(len(C_r)), (L_r, C_r)), shape=(3000, 150)); Cb = sp.csr_matrix((np.ones(len(C_c)), (L_c, C_c)), shape=(3000, 150))
    for nom, S_ in (("Popularité", S_p), ("Voisins de produits", S_i), ("ALS implicite", S_a)):
        res_froid[nom].append(evaluer(S_, Rv_, Cb, froids)["rappel"].mean())
tab_froid = pd.DataFrame(res_froid, index=list(revele)).rename_axis("achats connus")
print(tab_froid.round(3).to_string())
print("clients éligibles :", len(eligibles), "| nouveaux clients simulés :", len(froids))
```
<!--sortie-->
```text
               Popularité  Voisins de produits  ALS implicite
achats connus                                                
0                   0.198                0.198          0.198
1                   0.201                0.197          0.210
2                   0.208                0.237          0.240
3                   0.209                0.259          0.248
5                   0.216                0.269          0.274
8                   0.224                0.293          0.294
clients éligibles : 1000 | nouveaux clients simulés : 250
```

```python hide-code
print(tab_froid.round(3).to_string())
```
<!--sortie-->
```text
               Popularité  Voisins de produits  ALS implicite
achats connus                                                
0                   0.198                0.198          0.198
1                   0.201                0.197          0.210
2                   0.208                0.237          0.240
3                   0.209                0.259          0.248
5                   0.216                0.269          0.274
8                   0.224                0.293          0.294
```

**Un nouveau produit.** Le problème est plus dur encore : un produit sans acheteur n'a **aucune colonne** utilisable par le filtrage collaboratif, ni par la popularité. Seul le **contenu** (catégorie, prix) peut parler. Pour le mesurer, on retire de l'entraînement les **26 produits récents** (`nouveaute = 1`) ; pour chaque client qui en a acheté, on classe les 26 produits récents à partir de ses **autres achats** et on regarde si ceux qu'il a réellement achetés arrivent en tête. Une liste au hasard retrouverait en moyenne 5/26 $\approx19{,}2$ % des achats parmi ses cinq premiers choix.

```python hide
nouv = np.where(prod["nouveaute"].to_numpy() == 1)[0]; anciens = np.where(prod["nouveaute"].to_numpy() == 0)[0]
F_cat = pd.get_dummies(prod["categorie"], dtype=float).to_numpy()
lp = np.log(prod["prix"].to_numpy()); F_full = np.hstack([F_cat, ((lp - lp.mean()) / lp.std())[:, None]])
Ra = Rc[:, anciens]; Rn = Rc[:, nouv].toarray() > 0
cibles_u = np.where(Rn.sum(axis=1) >= 1)[0]
def profil(F, R_):
    n = np.asarray(R_.sum(axis=1)).ravel(); n[n == 0] = 1
    P = (R_ @ F[anciens]) / n[:, None]
    return P
def cos_scores(P, F):
    nP = np.linalg.norm(P, axis=1, keepdims=True); nP[nP == 0] = 1
    nF = np.linalg.norm(F, axis=1, keepdims=True); nF[nF == 0] = 1
    return (P / nP) @ (F / nF).T
S_content = cos_scores(profil(F_full, Ra), F_full[nouv])[cibles_u]
S_cat = cos_scores(profil(F_cat, Ra), F_cat[nouv])[cibles_u]
rng8 = np.random.default_rng(8)
S_alea = rng8.random(S_content.shape)
Y = Rn[cibles_u]
def metriques_nouveaux(S, Y, k=5):
    rec, aucs = [], []
    for s, y in zip(S, Y):
        ordre = np.argsort(-s, kind="stable")[:k]
        rec.append(y[ordre].sum() / y.sum())
        pos, neg = s[y], s[~y]
        aucs.append(((pos[:, None] > neg[None, :]).mean() + 0.5 * (pos[:, None] == neg[None, :]).mean()) if len(neg) else np.nan)
    return np.mean(rec), np.nanmean(aucs)
res_nouveaux = {nom: metriques_nouveaux(S_, Y) for nom, S_ in (("Au hasard", S_alea), ("Catégorie seule", S_cat), ("Catégorie et prix", S_content))}
tab_nouveaux = pd.DataFrame(res_nouveaux, index=["rappel@5 parmi les 26 nouveaux", "AUC par client"]).T
print(tab_nouveaux.round(3).to_string())
print("clients ayant acheté au moins un produit récent :", len(cibles_u), "| achats de produits récents :", int(Y.sum()), "| moyenne par client", round(Y.sum() / len(cibles_u), 2))
```
<!--sortie-->
```text
                   rappel@5 parmi les 26 nouveaux  AUC par client
Au hasard                                   0.195           0.498
Catégorie seule                             0.296           0.617
Catégorie et prix                           0.290           0.592
clients ayant acheté au moins un produit récent : 2348 | achats de produits récents : 5503 | moyenne par client 2.34
```

```python hide-code
print(tab_nouveaux.round(3).to_string())
```
<!--sortie-->
```text
                   rappel@5 parmi les 26 nouveaux  AUC par client
Au hasard                                   0.195           0.498
Catégorie seule                             0.296           0.617
Catégorie et prix                           0.290           0.592
```

```python hide
fig, ax = plt.subplots(1, 2, figsize=(10.5, 3.9))
for nom, col in (("Popularité", MUET), ("Voisins de produits", BLEU), ("ALS implicite", ROUGE)):
    ax[0].plot(tab_froid.index, tab_froid[nom], "o-", color=col, label=nom)
ax[0].set_xlabel("nombre d'achats connus du nouveau client"); ax[0].set_ylabel("rappel@10"); ax[0].legend(frameon=False, loc="upper left", fontsize=9)
ax[0].set_title("Nouveau client")
noms_n = list(tab_nouveaux.index); vals = tab_nouveaux.iloc[:, 0].values
ax[1].bar(range(3), vals, color=[MUET, AQUA, VIOLET]); ax[1].set_xticks(range(3)); ax[1].set_xticklabels(noms_n)
ax[1].axhline(5 / 26, color=ROUGE, ls="--", lw=1.2, label="espérance du hasard : 5/26")
for i, v in enumerate(vals):
    ax[1].text(i, v + 0.006, f"{v:.3f}", ha="center", fontsize=9)
ax[1].set_ylabel("rappel@5 parmi les 26 produits récents"); ax[1].set_ylim(0, max(vals) * 1.3); ax[1].legend(frameon=False, loc="upper left", fontsize=9); ax[1].set_title("Nouveau produit")
plt.tight_layout(); plt.savefig("figures/ch07-demarrage-froid.png", dpi=200, bbox_inches="tight"); plt.close()
```

![À gauche : rappel@10 en fonction du nombre d'achats connus d'un nouveau client, pour trois méthodes. À droite : rappel@5 parmi les 26 produits récents, avec la ligne du hasard.](figures/ch07-demarrage-froid.png)

**Pour un nouveau client**, la courbe de gauche se lit en trois temps.

- Sans aucun achat connu, **toutes les méthodes sont à égalité** (rappel@10 de 19,8 %) : ce sont, par construction, des recommandations de popularité.
- Avec **un seul achat**, l'ALS (21,0 %) dépasse à peine la popularité (20,1 %), et les voisins de produits (19,7 %) font un peu moins bien qu'elle ; sur 250 nouveaux clients, ces écarts ne sont pas mesurables.
- À partir de **deux achats**, l'écart devient net (24,0 % pour l'ALS et 23,7 % pour les voisins de produits, contre 20,8 %) et il atteint 7 points à huit achats (29,4 % et 29,3 % contre 22,4 %). La popularité progresse elle aussi un peu, car les produits déjà connus sont retirés de la liste, ce qui libère des places.

Pratiquement, deux ou trois achats suffisent pour que la personnalisation décolle : d'où l'intérêt d'un parcours d'accueil qui recueille rapidement quelques préférences.

**Pour un nouveau produit**, le contenu fait mieux que le hasard : en classant les 26 produits récents par ressemblance de catégorie avec les achats du client, on retrouve **29,6 %** de ses achats dans les cinq premiers choix (AUC de 0,62), contre 19,5 % pour une liste tirée au hasard (l'espérance est de 5/26, soit 19,2 %). Ajouter le prix **n'apporte rien** (29,0 % ; AUC de 0,59) : sur ces données simulées, le prix n'est en effet lié à aucun goût. Le gain est réel mais modeste : un produit sans historique reste difficile à recommander, et c'est une raison d'**organiser son lancement** (mise en avant volontaire, exploration) plutôt que d'attendre que les ventes le fassent remonter.

### 7.4.6 Les recommandations changent les données

Il reste la limite la plus profonde. Les achats que nous utilisons pour apprendre ne sont pas tombés du ciel : ils ont été **influencés par ce que le site affichait**. Un produit en vitrine est acheté plus souvent *parce qu'il est en vitrine*. Un modèle entraîné sur ces achats apprend, en partie, ce que le modèle précédent montrait. C'est une **boucle de rétroaction**.

Simulons-la. 1 500 clients, 60 produits dont l'attrait réel est connu (nous le programmons). À chaque tour, la vitrine montre 5 produits à chaque client ; il en achète un avec une probabilité qui dépend de son **goût réel** ; la vitrine du tour suivant est recalculée à partir des achats observés. Quatre politiques de vitrine :

1. **les produits les plus vendus** (le classement par popularité de 7.1.5) ;
2. les produits les plus vendus, avec **20 % d'exploration** (un emplacement sur cinq est tiré au hasard) ;
3. le classement par **taux d'achat** (achats divisés par expositions, lissé), avec 20 % d'exploration ;
4. le classement par taux d'achat, sans exploration.

```python hide
politiques = {"ventes seules": (0.0, False), "ventes + 20 % de hasard": (0.2, False), "taux d'achat + 20 % de hasard": (0.2, True), "taux d'achat seul": (0.0, True)}
graines = range(8)
suivi = {nom: pd.concat([boucle_retroaction(e, t, seed=s) for s in graines]).groupby("tour").mean() for nom, (e, t) in politiques.items()}
final = pd.DataFrame({nom: df.iloc[-1] for nom, df in suivi.items()}).T[["part_top5", "produits_achetes", "correlation_vrai", "bons_en_vitrine"]]
final.columns = ["part des achats sur 5 produits", "produits achetés (sur 60)", "corrélation avec l'attrait réel", "bons produits en vitrine (sur 5)"]
print(final.round(2).to_string())
fig, ax = plt.subplots(1, 2, figsize=(10.5, 3.9))
for (nom, df), col, ls, lw in zip(suivi.items(), (ROUGE, ORANGE, AQUA, BLEU), ("-", "--", "-", "-"), (3.2, 1.8, 2.0, 2.0)):
    ax[0].plot(df.index, df["correlation_vrai"], color=col, ls=ls, lw=lw, label=nom)
    ax[1].plot(df.index, df["bons_en_vitrine"], color=col, ls=ls, lw=lw, label=nom)
ax[0].set_ylabel("corrélation entre achats observés et attrait réel"); ax[1].set_ylabel("nombre des 5 meilleurs produits en vitrine")
for a in ax: a.set_xlabel("tour")
ax[1].legend(frameon=False, fontsize=9, loc="center right")
ax[0].set_title("Ce que le système apprend"); ax[1].set_title("Ce qu'il met en vitrine")
plt.tight_layout(); plt.savefig("figures/ch07-boucle-retroaction.png", dpi=200, bbox_inches="tight"); plt.close()
```
<!--sortie-->
```text
                               part des achats sur 5 produits  produits achetés (sur 60)  corrélation avec l'attrait réel  bons produits en vitrine (sur 5)
ventes seules                                            0.96                      47.25                             0.78                              0.50
ventes + 20 % de hasard                                  0.78                      59.62                             0.82                              0.50
taux d'achat + 20 % de hasard                            0.83                      59.62                             0.94                              4.62
taux d'achat seul                                        0.80                      45.88                             0.99                              4.88
```

```python hide-code
print(final.round(2).to_string())
```
<!--sortie-->
```text
                               part des achats sur 5 produits  produits achetés (sur 60)  corrélation avec l'attrait réel  bons produits en vitrine (sur 5)
ventes seules                                            0.96                      47.25                             0.78                              0.50
ventes + 20 % de hasard                                  0.78                      59.62                             0.82                              0.50
taux d'achat + 20 % de hasard                            0.83                      59.62                             0.94                              4.62
taux d'achat seul                                        0.80                      45.88                             0.99                              4.88
```

![Boucle de rétroaction simulée sur 40 tours (moyenne de 8 simulations) pour quatre politiques de vitrine : corrélation entre les achats observés et l'attrait réel des produits (à gauche) et nombre des cinq meilleurs produits présents en vitrine (à droite).](figures/ch07-boucle-retroaction.png)

Le tableau et les courbes montrent un résultat net.

- **Avec le classement par ventes seules, la boucle se referme** : 96 % des achats se concentrent sur cinq produits, seuls 47 produits sur 60 sont achetés au moins une fois, et **la vitrine ne contient en moyenne que 0,5 des cinq meilleurs produits réels**. Les ventes mesurent ce qu'on a montré, pas ce que les clients aiment.
- **Ajouter 20 % d'exploration ne suffit pas** : on achète alors presque tous les produits (59,6 sur 60), la corrélation avec l'attrait réel passe de 0,78 à 0,82, mais la vitrine ne contient toujours que 0,5 des cinq meilleurs. Le problème n'est pas seulement de montrer plus de produits, c'est de **lire correctement** les ventes.
- **Le classement par taux d'achat** (achats par exposition) corrige cette lecture : la corrélation monte à 0,94 avec exploration et 0,99 sans, et la vitrine contient **4,6 à 4,9 des cinq meilleurs produits**.
- **Sans exploration explicite, la méthode découvre quand même**, mais lentement : le lissage donne à un produit jamais montré un taux optimiste, de sorte que les produits peu convaincants quittent la vitrine. La courbe bleue montre une dizaine de tours pendant lesquels la vitrine ne contient presque aucun bon produit, avant qu'elle ne bascule ; pendant ce temps, seuls 46 produits sur 60 sont achetés.

> ⚠️ **Ce que cela implique en pratique.**
> - Un modèle de recommandation évalué **hors ligne** (comme ici) mesure sa capacité à prédire des achats *influencés par le système précédent*. Seul un **test en conditions réelles** (A/B test, volume II, chapitre 7) mesure l'effet *causal* des recommandations sur les achats.
> - Il faut **réserver de l'exploration** : montrer de temps en temps des produits que le modèle n'aurait pas choisis, pour apprendre ce qu'on ignore.
> - Un produit recommandé n'est pas toujours un produit **en plus** : il peut simplement avoir été acheté à la place d'un autre (cannibalisation). Un bon indicateur est le chiffre d'affaires total, pas la part des ventes qui passent par les recommandations.

> ✅ **À retenir (7.4).**
> - On évalue un **classement** : précision@k, rappel@k, succès@k, MAP@k, NDCG@k ; aucune ne remplace la mesure commerciale.
> - Protocole : hyperparamètres choisis sur la validation, réentraînement sur tout sauf le test, **une seule** évaluation sur le test, **intervalles de confiance** et comparaisons **appariées**.
> - Avec des données datées, **on découpe dans le temps** : un découpage aléatoire fait voir l'avenir au modèle et gonfle les performances.
> - Couverture, nouveauté et diversité complètent la précision ; la popularité est un biais à surveiller.
> - **Démarrage à froid** : sans historique, tout retombe sur la popularité ; le contenu est le seul recours pour un produit nouveau.
> - Les recommandations modifient les achats futurs : prévoir de l'exploration et valider par des tests réels.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.5 (métriques et intervalles de confiance), 7.6 (démarrage à froid), 7.7 (découpage aléatoire contre temporel), 7.8 (boucle de rétroaction) et 7.9 (mélange de méthodes et diversité), exercices 7.10 à 7.12.
