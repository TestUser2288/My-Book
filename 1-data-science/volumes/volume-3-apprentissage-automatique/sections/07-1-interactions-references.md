## 7.1 Données d'interaction et références simples

Avant de chercher à faire du « sur mesure », il faut comprendre ce que contiennent les données d'une boutique, et se donner des **références** : des méthodes si simples que tout modèle sophistiqué devra les battre pour justifier son existence. Cette section pose le vocabulaire, la matrice sur laquelle tout le chapitre repose, et deux premières méthodes : la popularité et le filtrage par contenu.

### 7.1.1 Ce que l'on recommande, et à qui

On appelle **utilisateurs** les clients à qui l'on recommande, et **articles** (*items*) ce que l'on recommande : ici, des produits. Un système de recommandation peut poursuivre deux tâches différentes, que l'on confond souvent.

- **Prédire une note** : « quelle note ce client donnerait-il à ce produit ? ». C'est un problème de régression sur une grandeur observée de temps en temps.
- **Classer** : « quels sont les dix produits à afficher en premier pour ce client ? ». Ce qui compte n'est pas la valeur précise d'un score, mais l'**ordre** : un produit placé en dixième position et un autre en première ne rapportent pas la même chose.

La seconde tâche est celle de la gérante. Une note de 3,9 plutôt que 4,1 n'a aucune importance si les deux produits sont bien classés l'un par rapport à l'autre, alors qu'une liste qui oublie le produit que le client aurait acheté est un échec. Le chapitre est donc organisé autour du **classement** ; la prédiction de notes n'apparaît qu'au cahier.

Le but commercial n'est jamais un score : c'est une conversion plus élevée, un panier plus grand, ou la **découverte** de produits que le client n'aurait pas trouvés seul. Nous verrons en 7.4 que ces objectifs ne se mesurent pas tous avec la même métrique.

### 7.1.2 Retours explicites et implicites

Les signaux dont on dispose sont de deux natures.

- Un retour **explicite** est une opinion exprimée : une note de 1 à 5, un « j'aime ». Il est précieux, mais rare : dans les données de la boutique, seulement un achat sur quatre est accompagné d'une note.
- Un retour **implicite** est un comportement : un achat, un clic, une page consultée. Il est abondant, mais ambigu : acheter un produit ne prouve pas qu'on l'a aimé (c'était peut-être un cadeau), et ne pas l'acheter ne prouve pas qu'on ne l'aimerait pas.

> ⚠️ **L'absence n'est pas un « non ».** Dans la matrice d'achats, une case vide signifie « le client n'a pas acheté ce produit », ce qui mélange trois situations : il ne l'a jamais vu, il l'a vu et n'en veut pas, ou il l'achètera demain. Traiter les cases vides comme des refus est l'erreur la plus fréquente. Elle a deux conséquences que nous retrouverons : en 7.3, on donne aux cases vides un **poids faible** plutôt qu'un poids égal à celui des achats ; en 7.4, on se rappelle qu'un produit recommandé que le client n'a pas acheté **n'est pas forcément une erreur** : l'évaluation sur achats cachés sous-estime la valeur réelle d'un bon classement.

Dans les données de la boutique, la colonne `nb_achats` compte les exemplaires achetés : **un achat sur trois environ** (33 %) concerne plus d'un exemplaire. Nous l'ignorerons dans la suite (un client « a acheté » ou « n'a pas acheté » le produit), ce qui revient à utiliser un signal binaire ; la fin de l'application 7.3 du cahier propose d'exploiter la quantité comme mesure de confiance.

### 7.1.3 La matrice d'interactions

Notons $R$ la matrice dont la ligne $u$ correspond au client $u$, la colonne $i$ au produit $i$, et dont l'entrée vaut $R_{ui}=1$ si le client a acheté le produit, $0$ sinon. Voici un exemple minuscule, que nous garderons pour tous les calculs à la main de la section : 5 clients et 6 produits.

| Client | P1 | P2 | P3 | P4 | P5 | P6 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| U1 | 1 | 1 | 0 | 1 | 0 | 0 |
| U2 | 1 | 0 | 1 | 1 | 0 | 0 |
| U3 | 0 | 1 | 1 | 1 | 1 | 0 |
| U4 | 1 | 1 | 0 | 0 | 0 | 1 |
| U5 | 1 | 0 | 1 | 1 | 1 | 0 |

Lisez la matrice par lignes (ce que chaque client a acheté) ou par colonnes (qui a acheté chaque produit). Le client U1 a acheté P1, P2 et P4. Le produit P4 a été acheté par U1, U2, U3 et U5. Ici plus de la moitié des cases sont remplies (17 sur 30) ; dans la réalité, ce n'est presque jamais le cas.

```python hide
M = np.array([[1, 1, 0, 1, 0, 0], [1, 0, 1, 1, 0, 0], [0, 1, 1, 1, 1, 0], [1, 1, 0, 0, 0, 1], [1, 0, 1, 1, 1, 0]], float)
print("achats par produit :", M.sum(axis=0).astype(int).tolist(), "| achats par client :", M.sum(axis=1).astype(int).tolist(), "| densité :", M.mean())
```
<!--sortie-->
```text
achats par produit : [4, 3, 3, 4, 2, 1] | achats par client : [3, 3, 4, 3, 4] | densité : 0.5666666666666667
```

Sur les données de la boutique, la même matrice a 3 000 lignes et 150 colonnes. On ne la stocke jamais comme un grand tableau plein de zéros, mais en **format creux** : on ne garde que les positions des cases remplies. Le fichier d'achats est justement un tableau « une ligne par achat », que l'on convertit ainsi :

```python
from scipy.sparse import csr_matrix

R = csr_matrix((np.ones(len(inter)), (inter.id_client - 1, inter.id_produit - 1)), shape=(3000, 150))
print(R.shape, R.nnz)   # nombre de cases remplies
```
<!--sortie-->
```text
(3000, 150) 27687
```

Deux régularités frappent immédiatement quand on regarde les marges de la matrice.

```python hide
fig, ax = plt.subplots(1, 2, figsize=(10.5, 3.8))
tri = np.sort(nb_par_produit)[::-1]
ax[0].bar(range(1, 151), tri, color=BLEU, width=1.0)
ax[0].set_xlabel("produits, du plus au moins acheté"); ax[0].set_ylabel("nombre de clients acheteurs")
ax[0].set_title("Quelques produits écrasent les autres")
ax[1].hist(nb_par_client[nb_par_client > 0], bins=np.arange(0.5, 44.5, 1), color=ORANGE)
ax[1].set_xlabel("nombre de produits achetés par client"); ax[1].set_ylabel("nombre de clients")
ax[1].set_title("La plupart des clients ont peu acheté")
plt.tight_layout(); plt.savefig("figures/ch07-longue-traine.png", dpi=200, bbox_inches="tight"); plt.close()
part10 = np.sort(nb_par_produit)[::-1][:10].sum() / R.nnz
print("part des 10 produits les plus achetés :", round(part10, 3), "| plus acheté :", int(nb_par_produit.max()), "| moins acheté :", int(nb_par_produit.min()))
print("achats par client (clients actifs) : médiane", np.median(nb_par_client[nb_par_client > 0]), ", moyenne", round(nb_par_client[nb_par_client > 0].mean(), 2), ", max", int(nb_par_client.max()))
print("produits avec moins de 50 acheteurs :", int((nb_par_produit < 50).sum()))
```
<!--sortie-->
```text
part des 10 produits les plus achetés : 0.211 | plus acheté : 1020 | moins acheté : 20
achats par client (clients actifs) : médiane 8.0 , moyenne 9.29 , max 43
produits avec moins de 50 acheteurs : 12
```

![À gauche : nombre de clients ayant acheté chaque produit, du plus au moins acheté (le plus acheté l'a été par plus de mille clients, le moins acheté par une vingtaine). À droite : nombre de produits distincts achetés par client.](figures/ch07-longue-traine.png)

Le produit le plus acheté l'a été par **1 020** clients, le moins acheté par **20** : un rapport de plus de cinquante entre les deux. Les dix premiers produits concentrent à eux seuls **21 %** des achats. Du côté des clients, la médiane est de **8** produits achetés, avec une queue longue (au plus **43**). Cette asymétrie est typique : on parle de **longue traîne**. Elle a deux conséquences : un client a peu d'historique pour apprendre ses goûts, et un produit peu acheté a peu de données pour qu'on le recommande à bon escient.

### 7.1.4 La similarité cosinus

Presque toutes les méthodes de cette section et de la suivante reposent sur une même question : **à quel point deux vecteurs se ressemblent-ils ?** Deux clients sont proches s'ils ont acheté les mêmes produits ; deux produits sont proches s'ils ont été achetés par les mêmes clients. Il faut une mesure.

La **similarité cosinus** entre deux vecteurs $a$ et $b$ est le cosinus de l'angle qu'ils forment :
$$\cos(a,b)=\frac{a\cdot b}{\|a\|\,\|b\|}=\frac{\sum_k a_kb_k}{\sqrt{\sum_k a_k^2}\ \sqrt{\sum_k b_k^2}}.$$
Elle vaut 1 si les deux vecteurs pointent dans la même direction, 0 s'ils sont orthogonaux. Pour des vecteurs d'achats (des 0 et des 1), le calcul se simplifie : si $n_i$ et $n_j$ sont les nombres de clients ayant acheté les produits $i$ et $j$, et $n_{ij}$ le nombre de ceux qui ont acheté **les deux**,
$$\cos(i,j)=\frac{n_{ij}}{\sqrt{n_i\,n_j}}.$$

> 📐 **Pourquoi cette formule.** Le produit scalaire de deux vecteurs binaires compte les positions où les deux valent 1, soit $n_{ij}$. La norme au carré d'un vecteur binaire est son nombre de 1, soit $n_i$. Le numérateur mesure les achats communs ; le dénominateur, $\sqrt{n_in_j}$, est la moyenne géométrique des tailles : il **normalise** pour qu'un produit très vendu ne soit pas automatiquement « proche de tout ».

**À la main.** Reprenons le petit tableau. Les produits P3 et P5 ont été achetés respectivement par $n_3=3$ clients (U2, U3, U5) et $n_5=2$ clients (U3, U5), dont $n_{35}=2$ en commun. Donc
$$\cos(\text{P3},\text{P5})=\frac{2}{\sqrt{3\times2}}=\frac{2}{\sqrt6}\approx0{,}816.$$
À l'inverse, P5 et P6 n'ont aucun acheteur commun : $n_{56}=0$ et la similarité vaut 0.

```python hide
def cos_bin(M, i, j):
    return M[:, i] @ M[:, j] / np.sqrt(M[:, i].sum() * M[:, j].sum())
print("cos(P3,P5) =", round(cos_bin(M, 2, 4), 4), "| cos(P5,P6) =", round(cos_bin(M, 4, 5), 4), "| cos(P1,P4) =", round(cos_bin(M, 0, 3), 4), "| cos(P1,P2) =", round(cos_bin(M, 0, 1), 4))
```
<!--sortie-->
```text
cos(P3,P5) = 0.8165 | cos(P5,P6) = 0.0 | cos(P1,P4) = 0.75 | cos(P1,P2) = 0.5774
```

> 💡 **Cosinus, Jaccard, corrélation.** On rencontre aussi l'indice de **Jaccard** $n_{ij}/(n_i+n_j-n_{ij})$, qui compte la part d'acheteurs communs parmi tous les acheteurs, et la **corrélation** de Pearson, qui centre les vecteurs. Pour des données binaires et creuses, le cosinus est le choix courant : il ignore les zéros communs (deux produits qu'aucun des deux clients n'a achetés ne se « ressemblent » pas), ce que la corrélation ne fait pas.

### 7.1.5 La référence : la popularité

La méthode la plus simple consiste à recommander à tout le monde **les produits les plus achetés**, en retirant à chaque client ceux qu'il a déjà. Elle n'est pas personnalisée (deux clients ayant acheté la même chose reçoivent la même liste) et ne demande aucun apprentissage : un simple comptage.

**À la main.** Dans le petit tableau, les nombres d'acheteurs sont $(4,3,3,4,2,1)$ pour P1 à P6. Le client U1 a acheté P1, P2 et P4 ; il reste P3 (3 acheteurs), P5 (2) et P6 (1). La popularité recommande donc P3, puis P5, puis P6, dans cet ordre.

Pourquoi parler de référence ? Parce que, dans presque tous les catalogues, les produits les plus vendus le sont **pour une raison** : ils plaisent à beaucoup de monde. Un modèle qui n'arrive pas à faire mieux que de montrer ces produits n'a rien appris de personnel sur le client.

Mesurons-la sur les données de la boutique, avec la méthode d'évaluation décrite plus haut : on recommande **10 produits** à chaque client évalué, et on regarde quelle part de ses achats cachés (jeu de validation) figure parmi ces 10. Cette part s'appelle le **rappel@10**. Comme point de repère, une liste **tirée au hasard** donne les résultats suivants.

```python hide-code
Rt, Rv = d["R_train"], d["val"]
refs = {}
for nom, S in (("au hasard", scores_aleatoire(Rt)), ("popularité", scores_popularite(Rt)), ("contenu", scores_contenu(Rt, prod))):
    refs[nom] = resume(evaluer(S, Rt, Rv, d["users"]))
tab_refs = pd.DataFrame(refs).T.rename(columns={"precision": "précision@10", "rappel": "rappel@10", "ap": "MAP@10", "ndcg": "NDCG@10", "succes": "au moins un achat retrouvé"})
print(tab_refs.round(3).to_string())
```
<!--sortie-->
```text
            précision@10  rappel@10  MAP@10  NDCG@10  au moins un achat retrouvé
au hasard          0.012      0.071   0.024    0.040                       0.119
popularité         0.039      0.241   0.094    0.143                       0.352
contenu            0.020      0.112   0.033    0.059                       0.184
```

Une liste tirée au hasard retrouve **7,1 %** des achats cachés dans ses dix produits ; la popularité en retrouve **24,1 %**, soit **plus de trois fois plus**. Autrement dit, sur ce catalogue, une grande partie de l'information utile tient dans un simple comptage. Ce que la personnalisation pourra apporter s'ajoute à ce socle.

### 7.1.6 Le filtrage par contenu

Le **filtrage par contenu** recommande à un client des produits qui **ressemblent à ceux qu'il a déjà achetés**, en s'appuyant sur les caractéristiques des produits (catégorie, prix, description…) et non sur le comportement des autres clients.

La construction se fait en trois temps. On décrit chaque produit par un vecteur de caractéristiques ; on résume chaque client par un **profil**, la moyenne des vecteurs de ses produits ; on classe les produits par ressemblance (cosinus) avec ce profil.

**À la main, avec une mise en garde.** Décrivons trois produits par un vecteur $(\text{catégorie A},\ \text{catégorie B},\ \text{prix})$, le prix étant exprimé en dizaines d'euros : P1 $=(1,0,2)$, P2 $=(1,0,3)$ et deux candidats, P3 $=(0,1,2{,}5)$ et P4 $=(1,0,2{,}5)$. Un client a acheté P1 et P2 ; son profil est la moyenne, $(1,0,2{,}5)$. Le candidat P4 (même catégorie, même prix moyen) a un cosinus de 1, ce qui est rassurant. Mais le candidat P3, d'une **autre catégorie**, obtient
$$\cos=\frac{0\times1+1\times0+2{,}5\times2{,}5}{\sqrt{1+6{,}25}\ \sqrt{1+6{,}25}}=\frac{6{,}25}{7{,}25}\approx0{,}862.$$
Le résultat est presque aussi élevé que pour le bon candidat : le prix, qui n'est pas à la même échelle que les indicatrices de catégorie, **domine le calcul**.

> ⚠️ **Les échelles comptent.** Le cosinus (comme toute distance) est sensible à l'échelle des variables. Avant de comparer des produits, il faut **mettre les caractéristiques à la même échelle** : ici, centrer et réduire le logarithme du prix. C'est la même idée que la standardisation du chapitre 4 (section 4.1) et de l'ACP (volume II, section 3.1).

```python hide
a = np.array([[1, 0, 2.0], [1, 0, 3.0]]); profil = a.mean(axis=0)
c = lambda x, y: x @ y / (np.linalg.norm(x) * np.linalg.norm(y))
print("profil", profil, "| cos P4 =", round(c(profil, np.array([1, 0, 2.5])), 3), "| cos P3 =", round(c(profil, np.array([0, 1, 2.5])), 3), "| cos P5(0,1,0.5) =", round(c(profil, np.array([0, 1, 0.5])), 3))
```
<!--sortie-->
```text
profil [1.  0.  2.5] | cos P4 = 1.0 | cos P3 = 0.862 | cos P5(0,1,0.5) = 0.415
```

Sur les données de la boutique, les caractéristiques disponibles sont pauvres : une catégorie parmi quatre, et un prix. Le résultat, **11,2 %** de rappel@10, se situe entre le hasard (7,1 %) et la popularité (24,1 %) : le contenu apporte un signal, mais bien moins que le comportement collectif. Le filtrage par contenu n'est pourtant pas inutile. Il fonctionne **sans historique d'autres clients**, ce qui en fait la méthode de choix pour un **produit tout neuf** (section 7.4.5), et ses recommandations sont faciles à expliquer (« parce que vous avez acheté un produit de la même catégorie »).

> ✅ **À retenir (7.1).**
> - Recommander, c'est **classer** des produits pour chaque client ; le résultat se juge sur l'ordre, pas sur un score.
> - Les achats sont un retour **implicite** : une case vide n'est pas un refus. La matrice clients × produits est **creuse** et sa « longue traîne » limite l'information disponible.
> - La **similarité cosinus** mesure la ressemblance de deux vecteurs ; pour des achats binaires, $\cos(i,j)=n_{ij}/\sqrt{n_in_j}$. Les caractéristiques doivent être à la même échelle.
> - Deux références à battre : la **popularité** (très solide) et le **contenu** (utile surtout au démarrage à froid).

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : application 7.1 (matrice d'interactions, popularité et contenu à la main), exercices 7.1 à 7.3.
