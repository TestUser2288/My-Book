# Chapitre 4 : Segmentation et analyse de cohortes

> « Une moyenne décrit un client qui n'existe pas. Un segment décrit un groupe à qui l'on peut parler. »


Un jeudi, la gérante de la boutique pose deux questions qui ressemblent à une seule : « **Quels clients dois-je chouchouter ? Et nos nouveaux clients, est-ce qu'ils reviennent ?** » Elle a une enveloppe de quelques milliers d'euros pour les fêtes de fin d'année : une carte de remerciement, un code promotionnel, un appel. Elle ne peut pas l'envoyer à tout le monde, et elle sent bien que « les clients » ne forment pas un bloc : certains passent chaque mois, d'autres une fois par an, d'autres n'achètent que pendant les soldes.

Vous avez, au chapitre 3, appris à expliquer un chiffre par d'autres chiffres. Ici, la méthode change : au lieu de relier **une** variable à d'autres, vous allez **regrouper les clients qui se ressemblent** (la **segmentation**) et **suivre des groupes dans le temps** (l'**analyse de cohortes**). Ces deux gestes répondent à deux questions différentes, qu'il faut savoir distinguer.

> 💡 **Intuition.** Un **segment** répond à la question « **qui sont-ils ?** » : on photographie la clientèle à une date et l'on range les clients selon ce qu'ils *font* (leur fréquence, leur panier, leur canal). Une **cohorte** répond à la question « **que deviennent-ils ?** » : on prend les clients **entrés ensemble** (le même trimestre) et l'on observe ce qu'ils font, trimestre après trimestre. Le premier est une coupe transversale, la seconde un film.

## Un vocabulaire pour ce chapitre

| Mot | Sens | Exemple de la boutique |
|---|---|---|
| **Segment** | groupe de clients qui se ressemblent sur des variables choisies, et auquel on peut réserver une action | « les réguliers actifs », « les chasseurs de promotions » |
| **Segmentation par règles** | segments définis à la main par des seuils métier | « au moins trois commandes sur douze mois » |
| **Segmentation statistique** | segments découverts par un algorithme (les k-moyennes) | quatre groupes calculés à partir de cinq variables |
| **Cohorte** | clients entrés (inscrits, ou ayant acheté une première fois) pendant la même période | les 167 clients inscrits au premier trimestre de 2023 |
| **Rétention** | part des clients d'une cohorte encore actifs à un âge donné | 36 % des clients d'une cohorte commandent au trimestre suivant |
| **RFM** | segmentation fondée sur la **R**écence, la **F**réquence et le **M**ontant | « champions » : récents et fréquents |
| **Valeur vie client** | revenu ou marge qu'un client rapporte pendant sa vie de client | ce que rapporte un nouveau client en un an |
| **Entonnoir** | suite d'étapes que l'on franchit pour acheter, avec la perte à chaque étape | session, panier, paiement, commande |

## Le chemin de ce chapitre

Le parcours essentiel répond aux deux questions de la gérante ; les deux sections facultatives donnent des outils d'usage courant.

- **4.1 Segmentation de la clientèle et du portefeuille** : des segments par règles métier, puis par k-moyennes (calcul d'une itération à la main, choix du nombre de segments, lecture et nom des segments), et comment **vérifier** qu'une segmentation vaut quelque chose (stabilité, pouvoir de prédiction) plutôt que de la croire sur parole.
- **4.2 Analyse de cohortes** : définir une cohorte, construire la **matrice de rétention**, la lire, **séparer l'effet de l'âge, de la période et de la cohorte**, éviter les deux pièges classiques (petits effectifs, observation tronquée), mesurer la rétention en revenu, et répondre enfin à « mes nouveaux clients reviennent-ils ? ».
- **➕ 4.3 Analyse RFM, valeur vie client, analyse du churn** : scorer les clients par quintiles, estimer une valeur vie client par une formule et par les cohortes, et comprendre pourquoi un client silencieux n'est pas un client perdu.
- **➕ 4.4 Tableaux d'entonnoir, de rétention et de cohortes** : lire l'entonnoir du site (les 127 022 sessions de 2025), et présenter un tableau de cohortes à quelqu'un qui n'a pas le temps de le déchiffrer.

Comme dans les chapitres précédents, **chaque résultat est confronté à la vérité programmée** des données quand elle est connue, et le chapitre insiste sur ce que ces méthodes **ne prouvent pas** : un segment n'est pas une cause, et une cohorte plus faible n'est pas forcément un client plus faible.

> 🧪 **Un avertissement dès maintenant.** Ces méthodes fabriquent toujours un résultat : les k-moyennes rendent des groupes même sur un nuage sans structure, et une matrice de cohortes se remplit même quand les effectifs sont minuscules. Nous apprendrons donc à *tester* chaque résultat avant de s'en servir.

## Les données du chapitre

> 📦 **Les données.** Les tables de la boutique des volumes précédents : `clients.csv` (6 000 clients), `commandes.csv` (36 395 commandes de 2023 à 2025), `lignes_commande.csv` (les lignes et leur montant), `produits.csv`, `retours.csv`, et pour la section 4.4 `sessions_web.csv` (127 022 sessions du site en 2025). Elles sont **simulées**. Deux particularités structurent tout le chapitre.
>
> - **4 806 clients seulement ont commandé** entre 2023 et 2025 ; 1 194 sont inscrits sans commande. Parmi les 6 000 clients, **4 000 étaient déjà inscrits en janvier 2023** (leur « première commande » observée n'est donc pas leur vraie première commande) et **2 000 se sont inscrits entre 2023 et 2025** : ce sont les seuls dont on connaît toute l'histoire, et ce sont eux qui forment nos cohortes.
> - La date d'observation est le **31 décembre 2025**. Tout ce qui est « récent » ou « ancien » se mesure par rapport à elle.

Le premier de ces deux faits n'est pas un détail technique : il décide **quelles** analyses de cohortes sont légitimes, et nous y reviendrons dès la section 4.2.


## 4.1 Segmentation de la clientèle et du portefeuille

Segmenter, c'est renoncer à la moyenne pour parler à des groupes. Cette section montre deux façons de former des groupes, par **règles** puis par **k-moyennes**, décortique l'algorithme sur six clients, apprend à choisir le nombre de segments et à les nommer, et surtout à **vérifier** qu'ils servent à quelque chose. Elle s'appuie sur les 4 806 clients qui ont commandé au moins une fois.


### 4.1.1 Pourquoi segmenter : une action différente par groupe

Une segmentation ne vaut pas par la beauté de ses groupes, mais par **les décisions qu'elle permet**. La gérante a une enveloppe pour les fêtes : avec un seul groupe, elle envoie le même message à tous et dépense autant pour une cliente qui commande douze fois par an que pour un client qui n'a pas acheté depuis deux ans. Avec des segments, elle peut remercier les premiers, relancer les seconds, et ne pas dépenser un euro pour ceux qui reviendraient de toute façon.

On distingue deux familles de segmentations, qui se complètent.

- **Par règles métier** : on fixe des seuils à la main (« au moins trois commandes sur douze mois »). Elles sont **lisibles**, **stables** et faciles à expliquer ; leur défaut est que les seuils sont arbitraires et que l'on ne voit que les structures que l'on a prévues.
- **Statistiques** (algorithmes de regroupement, ici les **k-moyennes**) : on laisse les données proposer des groupes à partir de plusieurs variables à la fois. Elles découvrent des combinaisons auxquelles on n'avait pas pensé ; leur défaut est qu'elles rendent toujours un résultat, même sans structure, et que leurs groupes demandent à être **lus, nommés et vérifiés**.

Le bon réflexe est de commencer par les règles : elles donnent une référence, et elles disent déjà beaucoup.

### 4.1.2 Des segments par règles métier

Prenons cinq segments, fondés sur la dernière année et sur l'ancienneté d'inscription : les **nouveaux** (inscrits depuis moins de douze mois), les **réguliers** (au moins trois commandes sur douze mois), les **occasionnels** (une ou deux), les **endormis** (déjà clients, mais aucune commande sur douze mois) et ceux qui **n'ont jamais commandé**. L'appel suivant fabrique ces segments en une instruction.

```python
deb = O.FIN - pd.Timedelta(days=365)
c12 = cmd[cmd["date_commande"] > deb].groupby("id_client").agg(n12=("id_commande", "size"), ca12=("ca", "sum"))
b = cli.set_index("id_client").join(c12).join(g[["n"]].rename(columns={"n": "n_tot"}))
b[["n12", "ca12", "n_tot"]] = b[["n12", "ca12", "n_tot"]].fillna(0)
b["segment"] = np.select([b["date_inscription"] > deb, b["n12"] >= 3, b["n12"] >= 1, b["n_tot"] > 0],
                         ["Nouveaux", "Réguliers", "Occasionnels", "Endormis"], "Jamais commandé")
t = b.groupby("segment").agg(clients=("n12", "size"), ca12=("ca12", "sum"))
t["part_clients"] = (t["clients"] / t["clients"].sum() * 100).round(1)
t["part_ca"] = (t["ca12"] / t["ca12"].sum() * 100).round(1)
print(t[["clients", "part_clients", "part_ca"]].sort_values("part_ca", ascending=False))
```
<!--sortie-->
```text
                 clients  part_clients  part_ca
segment                                        
Réguliers           1726          28.8     73.9
Occasionnels        1813          30.2     19.2
Nouveaux             634          10.6      6.9
Endormis             931          15.5      0.0
Jamais commandé      896          14.9      0.0
```

Ce simple tableau est déjà un résultat : **29 % des clients réalisent 74 % du chiffre d'affaires des douze derniers mois**, tandis que 30 % des clients n'ont **rien acheté depuis douze mois** (931 endormis, et 896 qui n'ont jamais commandé). La gérante sait où est l'enjeu. Remarquez au passage une précaution : les règles s'appliquent **dans un ordre** (un nouveau client n'est pas aussi « régulier »), et cet ordre est une décision à écrire.


### 4.1.3 Les k-moyennes, à la main sur six clients

Pour qu'une règle statistique soit autre chose qu'une boîte noire, calculons-la à la main. Les **k-moyennes** (k-means) cherchent **k** groupes tels que chaque client soit proche du **centre** de son groupe. L'algorithme tient en quatre phrases :

1. on choisit k centres de départ ;
2. on affecte chaque client au **centre le plus proche** ;
3. on recalcule chaque centre comme la **moyenne** de ses clients ;
4. on recommence les étapes 2 et 3 jusqu'à ce que les affectations ne changent plus.

Six clients, deux variables : le nombre de commandes et le panier moyen (en €).

| Client | A | B | C | D | E | F |
|---|---|---|---|---|---|---|
| Commandes | 1 | 2 | 2 | 9 | 10 | 12 |
| Panier moyen | 60 | 80 | 70 | 95 | 110 | 100 |

Les deux variables n'ont pas la même échelle (des unités contre des dizaines d'euros) : on les **standardise** d'abord, c'est-à-dire que l'on retire la moyenne et que l'on divise par l'écart-type. Les moyennes sont 6 commandes et 85,83 €, les écarts-types 4,43 et 17,42. On obtient les valeurs standardisées suivantes, puis les distances euclidiennes aux deux centres de départ (on prend les clients A et F, au hasard).

| Client | Commandes (z) | Panier (z) | Distance à A | Distance à F | Segment |
|---|---|---|---|---|---|
| A | −1,13 | −1,48 | 0,00 | 3,38 | 1 |
| B | −0,90 | −0,33 | 1,17 | 2,52 | 1 |
| C | −0,90 | −0,91 | 0,61 | 2,83 | 1 |
| D | 0,68 | 0,53 | 2,70 | 0,73 | 2 |
| E | 0,90 | 1,39 | 3,52 | 0,73 | 2 |
| F | 1,35 | 0,81 | 3,38 | 0,00 | 2 |

La distance de B à A vaut $\sqrt{(-0{,}90+1{,}13)^2+(-0{,}33+1{,}48)^2}\approx1{,}17$ : c'est un théorème de Pythagore sur les valeurs standardisées. Chaque client rejoint le centre le plus proche : A, B, C forment le segment 1, D, E, F le segment 2. On recalcule alors les centres : celui du segment 1 est $(-0{,}98 ; -0{,}91)$, celui du segment 2 est $(0{,}98 ; 0{,}91)$. Recalculées, les distances donnent **les mêmes affectations** : l'algorithme a convergé en une itération. La somme des carrés des distances de chaque client à son centre, que l'on appelle l'**inertie**, vaut environ 1,3 ; c'est la quantité que l'algorithme cherche à rendre petite.


### 4.1.4 Préparer les variables avant de regrouper

Les k-moyennes mesurent des **distances** : tout ce qui change l'échelle d'une variable change le résultat. Trois précautions s'imposent pour nos 4 806 clients.

- **Choisir des variables qui décrivent un comportement et qui n'ont pas de lien mécanique entre elles.** Nous retenons cinq variables : le nombre de commandes, le panier moyen, la récence (jours depuis la dernière commande), la part de commandes passées sur le Site, et la part de commandes avec un code promotionnel. Nous n'utilisons pas le chiffre d'affaires total, qui est le produit du nombre de commandes par le panier.
- **Rendre symétriques les variables très asymétriques.** Le nombre de commandes va de 1 à 88 et la récence de 0 à 1 094 jours : on prend leur **logarithme**, sinon quelques gros clients tirent les centres.
- **Standardiser**, pour que chaque variable pèse autant.

```python
X = O.variables_kmeans(g)              # logarithme du nombre de commandes, du panier et de la récence ; parts du Site et des promotions
Z = StandardScaler().fit_transform(X)
km = KMeans(n_clusters=4, n_init=10, random_state=0).fit(Z)
g["segment"] = O.nommer_segments(g, km.labels_)
print(g["segment"].value_counts())
```
<!--sortie-->
```text
segment
Réguliers actifs           2295
Dormants de la Boutique    1066
Dormants du Site           1053
Chasseurs de promotions     392
Name: count, dtype: int64
```

Que se passe-t-il si l'on oublie ces précautions ? Les mêmes cinq variables, en unités naturelles (commandes, euros, jours, parts), donnent des groupes **très différents** : le nombre de jours depuis la dernière commande, qui varie sur des centaines d'unités, écrase les parts qui varient entre 0 et 1. Le résultat concorde faiblement avec le précédent (indice de Rand ajusté de 0,35 : 1 pour des groupes identiques, 0 pour des groupes sans rapport).

```text
tailles des segments sans transformation ni standardisation : [378, 641, 968, 2819] | accord avec la version standardisée : 0.35
```

### 4.1.5 Combien de segments ? Le coude et la silhouette

L'algorithme demande k à l'avance. Deux outils aident à le choisir, aucun ne tranche seul.

- Le **coude** : on trace l'inertie (la dispersion à l'intérieur des groupes) selon k. Elle baisse toujours quand k augmente (avec autant de groupes que de clients, elle est nulle) ; on cherche un k après lequel la baisse devient lente. Sur nos données, la courbe descend régulièrement, **sans cassure nette**.
- La **silhouette** de chaque client compare la distance moyenne aux autres membres de son groupe (a) à la distance moyenne aux membres du groupe voisin le plus proche (b) : $s=(b-a)/\max(a,b)$. Elle vaut 1 si le client est bien à sa place, 0 s'il est entre deux groupes, un nombre négatif s'il est mal classé. On moyenne sur tous les clients.

```python
sil = {k: silhouette_score(Z, KMeans(k, n_init=10, random_state=0).fit_predict(Z), sample_size=3000, random_state=0) for k in range(2, 9)}
print({k: round(v, 3) for k, v in sil.items()})
```
<!--sortie-->
```text
{2: 0.23, 3: 0.264, 4: 0.276, 5: 0.213, 6: 0.224, 7: 0.224, 8: 0.206}
```


![Inertie et silhouette moyenne selon le nombre de segments : la silhouette est maximale pour quatre segments, mais ne dépasse pas 0,28.](figures/ch04-coude-silhouette.png)

Le maximum est à **k = 4**, avec une silhouette de 0,276. Retenez l'ordre de grandeur plus que le maximum : on lit en général une silhouette supérieure à 0,5 comme une structure nette, entre 0,25 et 0,5 comme **faible**, et en dessous comme absente. Notre clientèle ne forme donc pas des îlots séparés : c'est un **nuage continu** que l'algorithme découpe en quatre morceaux utiles. Cela n'invalide pas la segmentation, mais change ce qu'on peut en dire : les frontières sont des conventions commodes, pas des faits.

> 💡 **Intuition.** Segmenter un nuage continu ressemble à découper un pays en régions : les frontières sont tracées pour la commodité de la gestion, pas parce que les habitants changent brusquement d'un côté à l'autre. Cela suffit pour gérer, pourvu qu'on s'en souvienne.

### 4.1.6 Lire et nommer les segments

Un segment n'existe pour la gérante que lorsqu'il a un **nom** et un **profil**. On le lit de deux façons : un tableau en unités naturelles, et une carte de chaleur des écarts à la moyenne générale (en écarts-types), qui montre d'un coup d'œil ce qui distingue chaque groupe.

```text
                         clients  commandes  panier  recence_mediane  part_site  part_promo  part_ca_%
segment                                                                                               
Réguliers actifs            2295      12.84  101.85             29.0       0.42        0.16      81.62
Chasseurs de promotions      392       2.28   85.18            225.5       0.45        0.76       2.08
Dormants du Site            1053       2.96   96.51            220.0       0.76        0.06       8.19
Dormants de la Boutique     1066       2.75  105.59            290.0       0.10        0.06       8.11
```


![Écart de chaque segment à la moyenne générale pour les cinq variables de la segmentation, en écarts-types : rouge au-dessus, bleu en dessous.](figures/ch04-profils-segments.png)

On y lit quatre profils.

- **Les réguliers actifs** (2 295 clients, 48 % de la clientèle active) : près de 13 commandes en trois ans, une dernière commande vieille de 29 jours en médiane. Ils réalisent **82 % du chiffre d'affaires**.
- **Les chasseurs de promotions** (392 clients) : seulement 2,3 commandes en moyenne, un panier plus petit (85 €), et **76 % de leurs commandes passent par un code promotionnel**. C'est le profil le plus facile à reconnaître, la carte de chaleur le désigne par la valeur +2,6 sur la part de promotions.
- **Les dormants du Site** (1 053 clients) et **les dormants de la Boutique** (1 066 clients) : trois commandes environ, dont la dernière date de 220 jours et 290 jours en médiane ; ce qui les sépare est le **canal** (76 % de commandes sur le Site contre 10 %).

Un nom doit **suggérer l'action**. « Réguliers actifs » : on les remercie. « Chasseurs de promotions » : une étiquette à **tester** avant d'agir (voir la section suivante : elle tient mal dans le temps). « Dormants » : on les relance, par le canal qu'ils utilisent. Un nom comme « segment 3 » ne dit rien à la gérante, qui oubliera de s'en servir.

### 4.1.7 Vérifier : stabilité et pouvoir de prédiction

Une segmentation qui n'a pas été éprouvée est une jolie image. Deux épreuves, simples, la rendent crédible.

**La stabilité.** Si l'on retire ou remplace quelques clients, retrouve-t-on les mêmes groupes ? On rééchantillonne cinq fois la clientèle (avec remise), on refait la segmentation, et l'on compare ses affectations à celles de la segmentation de référence par l'indice de Rand ajusté.

```text
accord avec la segmentation de référence sur cinq rééchantillonnages : [0.91, 0.99, 0.96, 0.94, 0.93]
```

Les accords vont de 0,91 à 0,99 : les groupes ne dépendent pas de l'échantillon, c'est rassurant.

**Le pouvoir de prédiction.** Un segment utile prédit **quelque chose que l'on n'a pas utilisé pour le fabriquer**. On se place au 30 juin 2025 : on construit les segments avec les seules données connues à cette date, puis on regarde ce que font les clients au **second semestre**. Les segments distinguent-ils des comportements futurs ?


```text
                          eff  achat    ca2
segment                                    
Réguliers actifs         2018   83.3  253.0
Chasseurs de promotions   431   49.2   91.4
Dormants du Site          896   45.0   73.8
Dormants de la Boutique  1064   43.5   76.6
ensemble : 4409 clients, 62.6 % ont commandé, 158.2 € par client
```


![Part de clients ayant commandé au second semestre 2025, selon le segment construit au 30 juin.](figures/ch04-validation-segments.png)

Les segments **prédisent** : 83 % des réguliers actifs commandent au second semestre et dépensent 253 € en moyenne, contre 43 à 49 % et 74 à 91 € pour les trois autres groupes ; la moyenne générale (63 % et 158 €) cache cet écart. Notez ce que le test **ne dit pas** : les trois derniers segments ne se distinguent presque pas entre eux sur ce critère (43 % à 49 %). Si la gérante voulait un traitement différent pour eux, il faudrait que la différence entre eux soit visible sur *une autre* mesure, par exemple la sensibilité aux promotions. L'exercice 4.4 du cahier fait précisément ce test pour les « chasseurs de promotions » : au second semestre, **15,9 %** de leurs commandes utilisent un code promotionnel, contre 12,5 à 14,1 % pour les trois autres segments. Leur étiquette, fondée sur 76 % de commandes avec code sur deux ou trois commandes en tout, était en grande partie un **effet de petits nombres** : le nom promettait plus que les données ne tiennent.

> ⚠️ **Piège : les segments bougent.** Une segmentation décrit les clients à **une date**. Entre le 30 juin et le 31 décembre, **22,5 %** des clients présents aux deux dates changent de segment (77,5 % restent dans le leur). Refaire la segmentation périodiquement, avec les mêmes variables et les mêmes règles de nommage, est une tâche courante ; la comparer à la précédente en fait un outil de suivi (qui entre chez les réguliers ? qui en sort ?).


### 4.1.8 Les pièges de la segmentation

Quatre erreurs reviennent presque toujours.

1. **Segmenter sur ce que l'on veut ensuite comparer.** Si l'on fabrique les segments avec le chiffre d'affaires, il est évident que les segments diffèrent par leur chiffre d'affaires : c'est un cercle. Les variables de la segmentation décrivent le comportement ; le critère de validation doit être **extérieur** (ici, la commande du semestre suivant).
2. **Trop de segments.** Avec huit segments, la silhouette tombe à 0,206 : on découpe du bruit. Un segment qu'on ne sait pas nommer, ni traiter différemment, n'a pas de raison d'exister. Le nombre utile est souvent celui des **actions distinctes** dont on dispose.
3. **Oublier la standardisation** (section 4.1.4) : l'algorithme ne regroupe alors que la variable qui a les plus grandes unités.
4. **Prendre les segments pour des causes.** Les chasseurs de promotions achètent avec des codes ; cela ne prouve pas que la promotion les fait acheter plus qu'ils ne le feraient sans elle. Un segment décrit, il n'explique pas (voir la section 1.4 du volume I et la section 2.3 pour la différence entre corrélation et causalité, et le chapitre 3 pour les outils qui isolent un effet).

> ✅ **À retenir.** Une segmentation est un **outil de décision**, pas une découverte. Commencez par des règles lisibles ; si vous utilisez les k-moyennes, transformez et standardisez les variables, choisissez k avec le coude **et** la silhouette **et** votre capacité d'agir, donnez un nom qui suggère l'action, puis **éprouvez** les segments (stabilité, prédiction d'un critère extérieur) et refaites-les régulièrement.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 à 4.3, exercices 4.1 à 4.4.


## 4.2 Analyse de cohortes

La segmentation photographie les clients ; l'analyse de cohortes les **suit**. On prend des clients qui sont entrés en même temps, et l'on regarde ce qu'ils font, période après période. C'est l'outil de la question « mes nouveaux clients reviennent-ils ? », et c'est aussi un outil à risques : on y confond facilement l'effet de l'**âge** d'un client, de la **période** où l'on observe et de la **cohorte** à laquelle il appartient. Cette section apprend à construire la matrice, à la lire, et à ne pas lui faire dire ce qu'elle ne dit pas.


### 4.2.1 Une cohorte : qui, et à partir de quand ?

Une **cohorte** est un groupe de clients qui partagent un **événement d'entrée** survenu pendant la même période. Le choix de cet événement est une décision d'analyste, qui change la question :

- l'**inscription** (ou la création du compte) répond à « que deviennent les clients que nous *recrutons* ? » ;
- la **première commande** répond à « que deviennent les clients qui *achètent* ? » : plus pertinent pour le revenu, mais on ignore les inscrits qui n'achètent jamais ;
- une **première commande d'un certain type** (au moyen d'un code de bienvenue, d'un canal) isole l'effet d'une campagne.

La période est choisie selon le volume : le **mois** donne une courbe fine mais des groupes minuscules, le **trimestre** un compromis, l'**année** un trait grossier. Pour la boutique, nous retenons l'**inscription** et le **trimestre**.

Reste à savoir **qui** a le droit d'entrer dans une cohorte. Sur les 6 000 clients, 4 000 étaient déjà inscrits en janvier 2023, premier jour de nos données. Pour eux, on ne connaît pas l'histoire d'avant : leur « première commande observée » n'est pas leur première commande, et l'inscrire dans une cohorte de 2023 serait une erreur de **troncature à gauche**. Seuls les **2 000 clients inscrits depuis 2023** forment des cohortes honnêtes, et c'est sur eux que porte toute la section.

### 4.2.2 Un exemple à la main

Cinq clients s'inscrivent au premier trimestre de 2024. Le tableau indique, pour chacun, les trimestres (0 = celui de l'inscription) pendant lesquels il a passé au moins une commande.

| Client | Trimestres avec une commande |
|---|---|
| 1 | 0, 1, 3 |
| 2 | 1 |
| 3 | aucun |
| 4 | 0, 2 |
| 5 | 1, 2, 3 |

La **rétention** à l'âge *k* est la part des clients de la cohorte qui sont **actifs** à l'âge *k* : ici 2/5 = 40 % à l'âge 0 (clients 1 et 4), 3/5 = 60 % à l'âge 1 (clients 1, 2 et 5), 2/5 = 40 % à l'âge 2 (clients 4 et 5) et 2/5 = 40 % à l'âge 3 (clients 1 et 5). On range ces pourcentages dans **une ligne** de la matrice ; chaque cohorte occupe une ligne, chaque âge une colonne. Deux remarques de vocabulaire : « actif » veut dire « a commandé pendant la période », pas « est encore client » (le client 2 est actif à l'âge 1, absent à l'âge 2, mais pourrait revenir) ; et la matrice mesure une **part de la taille initiale** de la cohorte, jamais une part des survivants.

### 4.2.3 La matrice de rétention de la boutique

L'appel suivant construit la matrice pour les 12 cohortes trimestrielles de 2023 à 2025 : les effectifs, le taux d'activité par âge, et le chiffre d'affaires par client (nous y reviendrons). Les cinq premières lignes, sur les six premiers âges, donnent le ton.

```python
eff, taux, ca_client = O.matrice_cohortes(cli, cmd, pas="Q")
t5 = (taux.iloc[:5, :6] * 100).round(0).astype(int)
t5.insert(0, "clients", eff.iloc[:5].values)
print(t5)
```
<!--sortie-->
```text
age     clients   0   1   2   3   4   5
coh                                    
2023Q1      167  22  40  40  50  31  31
2023Q2      180  26  36  42  38  41  36
2023Q3      168  24  36  32  29  34  38
2023Q4      185  39  30  33  32  41  31
2024Q1      177  24  37  33  44  35  36
```

La carte de chaleur ci-dessous montre toute la matrice. Les cases vides en bas à droite ne sont pas des zéros : ce sont des âges que les cohortes récentes **n'ont pas encore vécus**.


![Matrice de rétention trimestrielle : part des clients de chaque cohorte (ligne) qui ont commandé au trimestre d'âge donné (colonne). Les cases vides sont des âges pas encore observés.](figures/ch04-cohortes-retention.png)

### 4.2.4 Lire la matrice : colonnes, lignes, diagonales

Une matrice de cohortes se lit dans trois directions, qui répondent à trois questions.

- **Une ligne** suit **une cohorte** dans le temps : comment ses clients évoluent-ils ?
- **Une colonne** compare **des cohortes au même âge** : les clients recrutés en 2024 se comportent-ils comme ceux de 2023 ?
- **Une diagonale** compare des cases du **même trimestre civil** : un événement collectif (les fêtes, une panne, une campagne) a-t-il touché tout le monde au même moment ?

Que voit-on ici ? Premièrement, **la première colonne est basse** (27,5 % en moyenne) : le trimestre d'inscription est un trimestre **partiel** (le client s'inscrit en cours de trimestre), donc il a moins de temps pour commander. Ce n'est pas un faible engagement, c'est de la géométrie. Deuxièmement, **dès le trimestre suivant, le taux d'activité s'installe autour de 36 % et ne bouge plus** : 36 % à l'âge 1, 36 % à l'âge 2, 38 % à l'âge 3, 37 % à l'âge 4, 35 % à l'âge 5… Il n'y a **aucune érosion visible** : un client recruté il y a deux ans commande autant qu'un client recruté le trimestre dernier. C'est un résultat inhabituel (dans beaucoup d'activités, la courbe descend), et il mérite d'être vérifié avant d'être annoncé. Troisièmement, **les cases fluctuent** : de 26 à 50 selon les cases (hors première colonne), sans motif apparent. Il faut savoir si ce sont des variations réelles ou du bruit d'échantillonnage, ce que la suite montre.

### 4.2.5 Âge, période, cohorte : trois effets, une seule matrice

Dans une matrice de cohortes, chaque case est la rencontre de **trois** notions : l'**âge** du client (la colonne), le **trimestre civil** d'observation (la diagonale) et sa **cohorte** (la ligne). On voudrait attribuer une variation à l'une d'elles, mais les trois sont liées (âge = trimestre civil − cohorte) : on ne peut pas les séparer sans hypothèse supplémentaire. On procède donc par **comparaisons ciblées**.

- Pour isoler l'effet d'**âge**, on regarde les colonnes **en moyenne** : le taux moyen d'activité à chaque âge.
- Pour isoler la **période**, on regarde le taux d'activité par **trimestre civil** (les diagonales), à âge comparable.
- Pour isoler la **cohorte**, on compare les lignes aux **mêmes âges**.


![À gauche, taux d'activité moyen selon l'âge ; à droite, taux d'activité selon le trimestre civil, pour les clients déjà inscrits depuis au moins un trimestre.](figures/ch04-age-periode.png)

Le graphique de gauche confirme que l'**âge** n'a pas d'effet après le premier trimestre. Le graphique de droite montre un fort effet de **période** : chaque **quatrième trimestre** (les fêtes) porte le taux d'activité à 41–43 %, contre 32–34 % aux autres trimestres de 2024 et de 2025. C'est la saison, pas un comportement de cohorte.

Le piège est là : **le dernier point de la courbe de gauche (44 % à l'âge 11) est une illusion**. Il n'y a qu'**une seule cohorte** observée à cet âge (celle du premier trimestre de 2023, observée au quatrième trimestre de 2025) : c'est une case de **quatrième trimestre**, qui profite de l'effet de saison, et non un effet d'âge. Quiconque lirait « la rétention remonte à 44 % après onze trimestres » se tromperait. Règle pratique : ne jamais interpréter les colonnes de droite d'une matrice, où il reste une ou deux cohortes.

Reste l'effet de **cohorte**. Au même âge 1, les onze cohortes observées donnent des taux de 30 % à 41 % ; avec des cohortes de 150 à 190 clients, cet écart est du même ordre que le bruit (section suivante). Rien n'oblige à y voir une différence de qualité entre cohortes.

> 🧪 **La vérité programmée.** Dans les données de la boutique, chaque client garde une propension constante à commander (il n'y a pas de désengagement programmé) : l'absence d'effet d'âge est donc **exacte**, et la matrice la retrouve. La demande totale d'un mois (saison, tendance, promotions) est répartie entre les clients **inscrits à cette date** : l'effet du quatrième trimestre est donc retrouvé, mais **chaque nouvel inscrit dilue les autres**, ce qui abaisse un peu les taux des périodes tardives (le taux d'activité des trimestres de 2023 est plus élevé que celui des trimestres équivalents de 2025). Nous l'observerons à la section 4.2.8.

### 4.2.6 Deux pièges : les petits effectifs et l'observation tronquée

**Les petits effectifs.** Une case de matrice est une **proportion** calculée sur la taille de la cohorte. Avec 150 à 190 clients par cohorte trimestrielle, l'incertitude est déjà sensible ; avec des **cohortes mensuelles**, elle devient écrasante. Les 36 cohortes mensuelles comptent de 42 à 66 clients, 57 en médiane. Pour un taux d'activité de 16 % (la valeur typique d'un mois) sur 55 clients, l'intervalle de confiance à 95 % de la proportion va de **9 % à 28 %** : une cohorte « à 12 % » et une autre « à 20 % » ne sont **pas distinguables**. Lire des tendances dans une matrice mensuelle de 36 lignes, c'est lire dans le marc de café.


La parade est de **regrouper** : des cohortes trimestrielles, ou annuelles ; de **moyenner** des cohortes comparables ; de joindre aux chiffres leur intervalle de confiance (volume I, section 1.3) ; et de ne retenir que les **écarts qui dépassent le bruit**.

**L'observation tronquée.** Une cohorte récente n'a pas eu le temps de vivre toutes les périodes : la cohorte du dernier trimestre de 2025 n'a qu'une case, celle du premier trimestre de 2023 en a douze. Deux conséquences : les colonnes de droite reposent sur **peu de cohortes** (on vient de le voir), et toute statistique « globale » qui mélange des cohortes d'âges différents est trompeuse. Par exemple, la part de clients qui n'ont **jamais** passé de seconde commande est mécaniquement plus grande pour les cohortes récentes (elles n'ont pas eu le temps) : comparer ce taux entre cohortes sans fixer **la même durée d'observation** pour toutes est une erreur classique. Nous le ferons correctement à la section 4.2.8.

### 4.2.7 La rétention en revenu et cumulée

Le taux d'activité compte les clients ; le **revenu par client** compte ce qu'ils rapportent. Même matrice, autre valeur : à chaque âge, le chiffre d'affaires de la cohorte divisé par sa **taille initiale**. Cela mélange la fréquence des clients et la taille de leurs paniers, ce qui est souvent ce que l'on veut.

```text
CA moyen par client, selon l'âge (€) : {0: 37.9, 1: 62.2, 2: 60.6, 3: 64.7, 4: 57.2, 5: 60.0}
CA cumulé par client sur les 4 premiers trimestres, cohortes 2023T1 à 2024T4 (€) : [263, 231, 209, 196, 206, 226, 185, 236] | moyenne : 218.9
```

Un client inscrit rapporte **38 €** le trimestre de son inscription (trimestre partiel), puis **environ 60 €** par trimestre : 62 € au trimestre suivant, 61 €, 65 €, 57 €, 60 €. Sur les quatre premiers trimestres, **un client inscrit rapporte en moyenne 219 € de chiffre d'affaires**, avec des cohortes qui vont de 185 à 263 €. Cette **courbe cumulée** (la somme des colonnes) est la matière première de la valeur vie client, section 4.3. Attention à la même précaution que plus haut : on ne cumule que sur des **cohortes observées** à tous les âges concernés, ici les huit cohortes de 2023 et 2024.

Deux mots sur la lecture. Le revenu cumulé par client **ne peut que monter** (on ajoute des revenus positifs), la courbe d'un client qui ne revient pas est plate : c'est son pente qui informe, pas son niveau. Et un revenu par client élevé dans une cohorte peut venir de **quelques gros clients** : la boutique a des clients à 88 commandes. Regardez toujours la médiane à côté de la moyenne.

### 4.2.8 « Mes nouveaux clients reviennent-ils ? »

C'est la question de la gérante, qui se pose souvent mieux **sans** matrice : parmi les nouveaux clients, quelle part passe une **seconde commande** dans un délai donné ? La précaution à ne pas oublier est celle de la troncature : pour comparer des clients, on ne garde que ceux dont la première commande date d'**au moins 180 jours** avant la date d'observation, de sorte que chacun ait eu le **même temps** pour revenir.

```python
n = cmd[cmd["id_client"].isin(cli.loc[cli["date_inscription"] >= "2023-01-01", "id_client"])].sort_values("date_commande")
deux = n.groupby("id_client")["date_commande"].apply(lambda s: list(s.iloc[:2]))
prem = deux.map(lambda l: l[0]); sec = deux.map(lambda l: l[1] if len(l) > 1 else pd.NaT)
obs = pd.DataFrame({"prem": prem, "delai": (pd.to_datetime(sec) - prem).dt.days}).query("prem <= '2025-07-04'")
print("nouveaux clients ayant commandé :", len(deux), "sur 2000 | observables 180 jours :", len(obs))
print("seconde commande sous 90 jours :", round((obs["delai"] <= 90).mean() * 100, 1), "% | sous 180 jours :", round((obs["delai"] <= 180).mean() * 100, 1), "% | jamais :", round(obs["delai"].isna().mean() * 100, 1), "%")
print((obs.assign(an=obs["prem"].dt.year, r=obs["delai"] <= 180).groupby("an")["r"].agg(["size", "mean"]).assign(mean=lambda d: (d["mean"] * 100).round(1))))
```
<!--sortie-->
```text
nouveaux clients ayant commandé : 1418 sur 2000 | observables 180 jours : 1126
seconde commande sous 90 jours : 46.0 % | sous 180 jours : 63.4 % | jamais : 14.3 %
      size  mean
an              
2023   375  70.4
2024   499  61.7
2025   252  56.3
```

Voici la réponse, avec ses nuances. Sur les 2 000 clients inscrits depuis 2023, **1 418 ont commandé** (71 %). Parmi les 1 126 dont la première commande est assez ancienne, **46 % passent une seconde commande en moins de 90 jours et 63 % en moins de 180 jours** ; 14 % n'ont jamais passé de seconde commande.

Le dernier tableau est le plus instructif : **la part de clients qui reviennent en 180 jours baisse selon l'année de première commande**, de 70 % (2023) à 62 % (2024) puis 56 % (2025). Les trois groupes ont tous eu 180 jours pour revenir : la troncature n'explique pas l'écart. Avec 252 à 499 clients par ligne, la différence entre 70 % et 56 % est bien supérieure au bruit (l'intervalle de 56 % sur 252 clients va d'environ 50 % à 62 %). Les nouveaux clients de 2025 reviennent donc moins vite que ceux de 2023 : un effet de **cohorte** ou de **période**, que la matrice ne permettait pas d'attribuer.

La vérité programmée le dit : la demande totale étant fixée, **chaque inscrit supplémentaire dilue** l'activité des autres ; la clientèle passe de 4 000 à 6 000 inscrits en trois ans, et le taux de retour des nouveaux baisse avec elle. Dans une vraie boutique, ce serait un signal à instruire (qualité du recrutement, saturation du marché, changement de mix de canaux), pas à expliquer par une règle simple. Retenez la méthode : une comparaison **à durée d'observation égale** a révélé une baisse que la matrice, qui mélange âge et période, ne laissait pas voir.


> ✅ **À retenir.** Une cohorte regroupe des clients entrés **au même moment** ; on ne cohorte honnêtement que ceux dont **on connaît l'entrée**. Lisez la matrice dans les trois sens (ligne, colonne, diagonale) et **séparez âge, période et cohorte** par des comparaisons ciblées. Méfiez-vous des cohortes **petites** (mensuelles) et des colonnes de droite (peu de cohortes, observation tronquée) ; comparez toujours à **durée d'observation égale**. La rétention se mesure en part de la **taille initiale**, en nombre de clients ou en revenu.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.4 et 4.5, exercices 4.5 à 4.8.


## 4.3 ➕ Pour aller plus loin : analyse RFM, valeur vie client, analyse du churn

> 🧭 **Section complémentaire.** Trois outils d'usage courant en relation client, qui prolongent les segments et les cohortes : un score simple pour classer les clients (**RFM**), une estimation de ce qu'un client rapporte pendant sa vie (**valeur vie client**), et une manière sérieuse de parler de clients « perdus » (**churn**). Ils ne sont pas nécessaires à la suite du volume.


### 4.3.1 Le score RFM : récence, fréquence, montant

Le **RFM** résume un client par trois nombres : sa **récence** (depuis combien de jours a-t-il commandé pour la dernière fois ?), sa **fréquence** (combien de commandes ?) et son **montant** (combien a-t-il dépensé ?). L'idée est ancienne et robuste : les meilleurs clients sont récents, fréquents et dépensiers, et les trois mesures se calculent en une requête.

Le procédé tient en trois gestes.

1. **Découper chaque mesure en cinq groupes de même taille** (les quintiles) et donner un score de 1 (faible) à 5 (fort). Pour la récence, c'est le plus **récent** qui reçoit 5.
2. **Combiner** les scores en segments nommés : par exemple les clients à R ≥ 4 et F ≥ 4 sont des « champions », ceux à R ≤ 2 et F ≥ 4 sont des « gros clients à risque » (ils étaient bons, ils se sont tus).
3. **Vérifier** que les segments se comportent comme leur nom le dit.

Une précaution technique, que l'on oublie souvent : la fréquence compte beaucoup d'**ex æquo** (17 % de nos clients n'ont passé qu'une commande). Un découpage en quintiles sur les valeurs brutes donnerait des groupes de tailles inégales, voire impossibles. On classe donc les clients par **rang** avant de découper, et les ex æquo sont départagés arbitrairement : il faut le savoir pour ne pas sur-interpréter la différence entre deux clients de même fréquence.

```python
s = O.rfm(g)                                    # scores R, F, M de 1 à 5 par quintiles de rang
s["segment"] = [O.nom_segment_rfm(r, f) for r, f in zip(s["R"], s["F"])]
t = g.join(s).groupby("segment").agg(clients=("n", "size"), recence_med=("rec", "median"), commandes=("n", "mean"), ca=("ca", "sum"))
t["part_clients"] = t["clients"] / t["clients"].sum() * 100
t["part_ca"] = t["ca"] / t["ca"].sum() * 100
print(t.drop(columns="ca").sort_values("part_ca", ascending=False).round(1))
```
<!--sortie-->
```text
                         clients  recence_med  commandes  part_clients  part_ca
segment                                                                        
Champions                   1221         18.0       16.3          25.4     54.6
Fidèles                      995         64.0        8.4          20.7     23.0
À risque (gros clients)      257        209.0       10.1           5.3      7.3
À surveiller                 713        176.0        3.6          14.8      7.0
Perdus                      1256        422.0        1.8          26.1      6.1
Nouveaux ou récents          364         21.0        2.1           7.6      2.0
```


![Nombre de clients par couple de scores (récence R, fréquence F) : la diagonale est dense, les coins opposés sont presque vides.](figures/ch04-rfm.png)

Le tableau est parlant : **25 % des clients (les champions) font 55 % du chiffre d'affaires**, 26 % (les perdus) en font 6 %. La grille de la figure montre aussi une structure réelle : les clients **récents et fréquents** (en haut à droite) et **anciens et rares** (en bas à gauche) sont nombreux, les deux autres coins presque vides : ceux qui commandent souvent et ne sont plus revenus depuis longtemps sont rares, mais c'est précisément le groupe « gros clients à risque » (257 clients, 7 % du chiffre d'affaires) qu'un coup de téléphone peut sauver.

**La vérification** est la même qu'à la section 4.1 : se placer au 30 juin 2025, scorer les clients avec les données connues à cette date, et regarder qui commande au second semestre.

```text
                         clients  achat    ca2
segment                                       
Champions                   1102   89.9  305.4
À risque (gros clients)      268   78.0  178.5
Fidèles                      963   71.9  173.2
À surveiller                 567   51.5   90.5
Nouveaux ou récents          325   47.7  104.0
Perdus                      1184   35.5   51.7
```

Les segments sont **ordonnés comme annoncé** : 90 % des champions recommandent dans les six mois (305 € de chiffre d'affaires par client), contre 36 % des perdus (52 €). Remarquez la ligne « Perdus » : **un client sur trois classé « perdu » recommande dans les six mois**. Nous y revenons à la section 4.3.3.

> ⚠️ **Piège.** Le RFM est **simple, donc fragile** : les trois scores pèsent autant sans raison, les quintiles de rang sont relatifs à la clientèle du moment (un « 5 » de récence n'a pas le même sens après un mois creux), et les noms des segments dépendent de seuils arbitraires. Utilisez-le pour **prioriser des actions**, pas pour établir une vérité. Et ne le confondez pas avec une segmentation statistique : le RFM classe sur **trois** variables fixées d'avance.

### 4.3.2 La valeur vie client

La **valeur vie client** (en anglais *customer lifetime value*, CLV) est ce qu'un client rapporte en tout, pendant qu'il est client. On l'utilise pour décider de ce qu'on peut dépenser pour l'acquérir (un client qui rapporte 70 € de marge justifie moins de publicité qu'un client qui en rapporte 400 €) et pour comparer des segments.

**La formule simple.** Elle suppose que le client rapporte chaque année la même **marge** et qu'il reste client avec une probabilité constante $\rho$ d'une année à l'autre :

$$\text{CLV}=m\sum_{t\ge0}\left(\frac{\rho}{1+i}\right)^t=\frac{m}{1-\rho/(1+i)},$$

où $m$ est la marge annuelle d'un client actif, $\rho$ la **rétention annuelle** et $i$ un taux d'actualisation (un euro dans un an vaut moins qu'un euro aujourd'hui). Sans actualisation ($i=0$), c'est simplement $m$ multiplié par la **durée de vie moyenne** $1/(1-\rho)$.

Avec les chiffres de 2025 : on compte 3 875 clients actifs ; la marge brute hors taxe de l'année est de 419 017 €, soit **108 € par client actif** ; sur 3 479 clients actifs en 2024, 2 828 le sont encore en 2025, soit une rétention de 81,3 % (une perte de 18,7 %), qui donne une durée de vie de 5,3 ans. Sans actualisation, $\text{CLV}=108\times5{,}35\approx578$ € ; avec un taux fictif de 8 %, 437 €.

```text
clients actifs 2025 : 3875 | marge brute HT 2025 : 419017 € | marge par client actif : 108.1 €
rétention 2024 -> 2025 : 2828 sur 3479 = 81.3 % | durée de vie : 5.34 ans
CLV sans actualisation : 578 € | avec 8 % : 437 €
```

**La version empirique par cohortes.** Mais ces 578 € surestiment ce que rapporte un **nouveau** client : la formule suit les clients **actifs**, un groupe déjà trié (un client qui n'a jamais commandé n'y figure pas). Observons plutôt ce que rapportent les clients **inscrits**, grâce aux cohortes de la section 4.2 : sur les quatre premiers trimestres, un client inscrit rapporte en moyenne **219 €** de chiffre d'affaires, soit environ **69 €** de marge brute hors taxe (le taux de marge de 2025 est de 31,6 % du chiffre d'affaires toutes taxes comprises) ; sur les huit premiers trimestres, 446 € de chiffre d'affaires, soit environ 141 € de marge.

Les deux estimations ne se contredisent pas : 69 € est à peu près **108 € × 3 875 / 6 000**, c'est-à-dire la marge par client actif, répartie sur **tous** les clients inscrits (en 2025, 3 875 des 6 000 inscrits ont commandé, soit 65 %). La différence est une question de **dénominateur**, et c'est le piège numéro un de la valeur vie client : *par client de quoi ?*

> ⚠️ **Les pièges de la valeur vie client.**
> 1. **Revenu ou marge ?** Une valeur vie en chiffre d'affaires n'est pas une valeur vie en marge ; seule la seconde se compare à un coût d'acquisition.
> 2. **L'horizon.** Dire « 578 € » suppose que les clients durent 5,3 ans en moyenne, alors que nos données n'ont que trois ans d'histoire : le reste est une **extrapolation**. Préférez une valeur à horizon donné (« 141 € de marge sur deux ans »).
> 3. **L'hypothèse de rétention constante.** Elle est fausse si les clients diffèrent (c'est le cas : section 4.3.3).
> 4. **La moyenne.** Le revenu moyen d'un client sur la période est de 760 €, sa médiane de 474 € : les 10 % de meilleurs clients font 36 % du chiffre d'affaires, les 20 % meilleurs 55 %. Une moyenne de valeur vie masque cette concentration ; donnez la médiane et la part des meilleurs.
> 5. **L'actualisation** : un taux de 8 % est un exemple, pas une vérité ; la valeur change de 578 € à 437 € selon qu'on actualise ou non.


### 4.3.3 Le churn : un client silencieux est-il un client perdu ?

Le **churn** (ou attrition) est la perte de clients. Le mot paraît simple, mais il cache une question de **définition** : dans une boutique, **où est la frontière entre un client « endormi » et un client « parti » ?** Un abonnement donne la réponse (le client résilie) ; un achat libre ne la donne pas : il n'y a pas de résiliation, seulement du silence.

**Première approche : un taux annuel.** On compte les clients actifs une année et l'on regarde combien ne le sont plus la suivante : **18,7 %** des clients actifs en 2024 n'ont rien commandé en 2025 (3 479 actifs, 2 828 encore actifs), et 18,8 % entre 2023 et 2024. C'est stable, donc utilisable. Mais c'est un taux **de silence sur douze mois**, pas un taux de départ : un client silencieux en 2025 peut commander en 2026.

**Seconde approche : la probabilité de revenir.** Plutôt que de décréter « perdu », demandons aux données quelle est la probabilité qu'un client commande à nouveau **selon le temps écoulé depuis sa dernière commande**. On se place au 30 juin 2025 : pour chaque client déjà connu, on note le nombre de jours depuis sa dernière commande, puis on regarde s'il recommande dans les six mois suivants.

```python
r = O.reachat(cmd, "2025-06-30")                     # récence au 30 juin 2025 et achat dans les 184 jours suivants
r["groupe"] = pd.cut(r["rec"], [-1, 30, 90, 180, 365, 2000], labels=["0-30 j", "31-90 j", "91-180 j", "181-365 j", "plus de 365 j"])
tb = r.groupby("groupe").agg(n=("reachete", "size"), p=("reachete", "mean"))
tb["p"] = (tb["p"] * 100).round(1)
print(tb)
```
<!--sortie-->
```text
                  n     p
groupe                   
0-30 j          847  77.6
31-90 j        1070  74.3
91-180 j        771  67.1
181-365 j       961  53.6
plus de 365 j   760  36.2
```


![Part des clients qui commandent dans les six mois suivants, selon le nombre de jours écoulés depuis leur dernière commande au 30 juin 2025.](figures/ch04-reachat.png)

La probabilité de revenir **baisse régulièrement avec le silence**, mais **ne tombe jamais à zéro** : **36 % des clients silencieux depuis plus d'un an recommandent dans les six mois**. Décréter « perdu après douze mois » aurait classé 760 clients comme perdus, dont 275 seraient revenus. Le churn est une **probabilité**, pas un état.

Deux éléments de cadrage aident à choisir un seuil raisonnable. Le délai **habituel** entre deux commandes d'un même client est de 47 jours en médiane, mais 213 jours pour le 90ᵉ centile et 306 jours pour le 95ᵉ : un silence de 200 jours est banal pour une partie de la clientèle. Et la fréquence passée change tout : au 30 juin, parmi les clients qui n'avaient commandé **qu'une fois**, 33 % recommandent dans les six mois ; parmi ceux qui avaient commandé **dix fois et plus**, 94 %. Un seuil de silence doit donc **dépendre du rythme du client** (un gros client qui s'arrête trois mois est plus inquiétant qu'un acheteur annuel qui s'arrête huit mois).


### 4.3.4 Du churn à l'action

Une probabilité de revenir sert à **décider qui relancer**. La logique est celle d'un arbitrage : relancer coûte (un code promotionnel, un message), et rapporte si le client revient *à cause* de la relance. Trois conséquences pratiques.

- **Ne pas relancer ceux qui reviendront seuls.** Les clients à 0–30 jours reviennent à 78 % sans rien faire : leur offrir un rabais est de l'argent perdu. À l'inverse, les 181–365 jours (54 %) et plus de 365 jours (36 %) sont ceux où une action peut changer quelque chose, à condition que la valeur d'un client retrouvé dépasse le coût de la relance.
- **Prédire avec plusieurs variables.** Pour aller plus loin que la seule récence, on estime la probabilité de recommander par une **régression logistique** (récence, fréquence, panier, canal, part de promotions…) : c'est exactement l'outil de la section 3.3. Le gain par rapport à la grille de récence se mesure sur des données **qui n'ont pas servi** à l'estimation (comme ci-dessus : on construit à une date, on évalue après).
- **Mesurer l'effet réel de la relance** par un test A/B (chapitre 2, section 2.2), car la corrélation « les relancés reviennent plus » ne prouve pas que la relance en est la cause : les clients relancés sont souvent choisis parce qu'ils sont déjà plus actifs.

> ✅ **À retenir.** Le **RFM** classe les clients sur trois mesures simples (quintiles de rang, segments nommés) et se vérifie en regardant ce que font les segments ensuite. La **valeur vie client** dépend du dénominateur (clients actifs ou inscrits), de l'horizon, de la marge et de l'actualisation : annoncez-la avec ces quatre précisions et à horizon fini. Le **churn** est une probabilité qui dépend du temps de silence et du rythme du client : un client silencieux n'est pas un client perdu.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.6 et 4.7, exercices 4.9 et 4.10.


## 4.4 ➕ Pour aller plus loin : tableaux d'entonnoir, de rétention et de cohortes

> 🧭 **Section complémentaire.** Deux tableaux que l'on rencontre dans presque tous les rapports de clientèle : l'**entonnoir**, qui dit *où l'on perd* les visiteurs d'un site avant l'achat, et la **matrice de cohortes**, qui dit *combien reviennent*. La section apprend à les lire sur les données de la boutique, puis à les **présenter** à quelqu'un qui n'a pas le temps de les déchiffrer.


### 4.4.1 L'entonnoir de conversion du site

Un **entonnoir** (*funnel*) décrit une suite d'étapes que l'on franchit pour acheter, avec, à chaque étape, la part de ceux qui passent à la suivante. Pour le site de la boutique, les données de 2025 (`sessions_web`) retiennent quatre étapes : la **session** (une visite), l'**ajout au panier**, le **début du paiement** et la **commande**. Chaque ligne du fichier est une session ; les trois colonnes d'étapes valent 1 si la session a atteint l'étape.

```python
e = O.entonnoir(sess)
print(e[["sessions", "ajout_panier", "debut_paiement", "commande"]].to_string(index=False))
print((e[["taux_panier", "taux_paiement", "taux_commande", "conversion"]] * 100).round(1).to_string(index=False))
```
<!--sortie-->
```text
 sessions  ajout_panier  debut_paiement  commande
   127022         18116           10358      6078
 taux_panier  taux_paiement  taux_commande  conversion
        14.3           57.2           58.7         4.8
```

On lit l'entonnoir en deux temps. D'abord les **effectifs** : sur 127 022 sessions, 18 116 ajoutent un article au panier, 10 358 commencent à payer, 6 078 commandent. Ensuite les **taux de passage entre deux étapes consécutives** : 14,3 % des sessions ajoutent au panier, 57,2 % des paniers vont jusqu'au paiement, 58,7 % des paiements commencés aboutissent. La **conversion globale** est le produit des trois : 4,8 % des sessions finissent en commande ($0{,}143\times0{,}572\times0{,}587\approx0{,}048$).

Où est le « goulot » ? Deux lectures donnent deux réponses, et il faut savoir les distinguer.

- En **proportion**, la plus grosse perte est à la première étape : 85,7 % des sessions n'ajoutent rien au panier. Mais beaucoup de ces visiteurs ne voulaient pas acheter (ils regardaient, comparaient, cherchaient un horaire) : perdre un visiteur qui ne voulait pas acheter n'est pas une perte.
- En **valeur**, on regarde les étapes où l'**intention d'achat est démontrée** : 7 758 paniers n'arrivent pas au paiement, et 4 280 paiements commencés n'aboutissent pas. Ce sont des clients qui voulaient acheter et qui ont renoncé : les **abandons de panier et de paiement**. Les récupérer vaut davantage que de convaincre un visiteur de passer au panier.

> ⚠️ **Un entonnoir compte des sessions, pas des personnes.** Une personne qui remplit son panier sur son téléphone puis paie le lendemain sur son ordinateur apparaît comme une session abandonnée et une session convertie sans panier. Les taux d'étapes sont donc **approximatifs** et ne se lisent qu'en **comparaison** (entre sources, entre appareils, entre semaines), jamais comme des vérités absolues. De même, l'entonnoir suppose un ordre que les clients ne respectent pas toujours (on peut payer sans voir le panier si l'on utilise un lien direct).

### 4.4.2 L'entonnoir selon la source

Le vrai pouvoir d'un entonnoir apparaît quand on le **découpe**. Selon la source de la visite (direct, moteur de recherche, publicité, e-mail, réseaux, site référent), les taux diffèrent-ils ?

```text
           sessions  commande  panier %  paiement %  commande %  conversion %
source                                                                       
email          8892       772      17.8        68.6        71.0           8.7
direct        35566      2467      16.5        62.5        67.0           6.9
organique     43187      1736      13.4        55.0        54.4           4.0
referent       6351       239      12.6        56.1        53.2           3.8
payant        17783       535      12.6        49.8        48.0           3.0
reseaux       15243       329      11.9        46.3        39.3           2.2
```


![Taux de passage à chaque étape de l'entonnoir, selon la source de la session ; la conversion globale est indiquée à côté du nom de la source.](figures/ch04-entonnoir.png)

Le contraste est net : une session venue d'un **e-mail** se transforme en commande dans **8,7 %** des cas, une session venue des **réseaux sociaux** dans **2,2 %**, soit quatre fois moins. Ces conversions ont une incertitude : pour les réseaux, 329 commandes sur 15 243 sessions donnent un intervalle de confiance de 1,9 % à 2,4 % ; pour l'e-mail, de 8,1 % à 9,3 % : les deux intervalles sont très loin l'un de l'autre, la différence n'est pas du bruit.

Plus intéressant que l'écart global, le **profil** : les visiteurs des réseaux ne se distinguent pas tant par le premier pas (11,9 % ajoutent au panier, contre 17,8 % pour l'e-mail) que par les deux derniers : **39 % seulement** de ceux qui commencent à payer aboutissent (contre 71 % pour l'e-mail). Ce n'est pas le même problème : l'e-mail touche des gens qui connaissent la boutique, les réseaux amènent des curieux qui s'arrêtent au moment de sortir la carte bancaire. Une conclusion de ce genre déclenche une **hypothèse** (frais de livraison découverts tard ? paiement mal adapté au mobile ?) à tester, pas une certitude.

> 🧪 **Un résultat qui ne s'y trouve pas.** On pourrait croire que le **mobile** convertit plus mal que l'ordinateur : c'est une hypothèse courante. Ici, les trois appareils convertissent presque pareil : 4,8 % sur mobile, 4,7 % sur ordinateur, 4,8 % sur tablette (et des taux d'étapes quasi identiques). Ne pas trouver d'écart est un résultat : sur ces données, **l'appareil n'explique pas la conversion**, la source si.


> 🧪 **La vérité programmée.** Les données ont été fabriquées avec des conversions de 9 % pour l'e-mail, 7 % pour le direct, 4 % pour la recherche organique, 3,5 % pour les sites référents, 3 % pour la publicité et 2 % pour les réseaux : l'entonnoir les retrouve à quelques dixièmes de point près (site référent : 3,8 % observé pour 3,5 % programmé, un écart que l'effectif de 6 351 sessions rend banal). Une limite à garder en tête : les clients qui arrivent par e-mail sont presque tous **déjà clients** (15 % de nouveaux visiteurs, contre 55 % pour les autres sources) : leur bonne conversion reflète en partie **qui ils sont**, pas seulement le canal.

### 4.4.3 Présenter un tableau de cohortes

La matrice de la section 4.2 est un outil de travail ; pour **présenter** le résultat, il faut la retravailler. Quelques règles simples la rendent lisible en dix secondes.

1. **Un rectangle plutôt qu'un triangle.** On ne montre que les cohortes et les âges **observés pour tous** : ici, huit cohortes (de 2023 à 2024) sur huit trimestres. Cela supprime les cases vides, et les colonnes de droite qui reposent sur une ou deux cohortes.
2. **Une échelle de couleur unique, qui commence à une valeur raisonnable**, et des **chiffres dans les cases** : la couleur donne l'impression d'ensemble, le chiffre permet de vérifier.
3. **Les effectifs en regard de chaque cohorte** : le lecteur doit pouvoir juger si une case repose sur 40 ou sur 400 clients.
4. **Une ligne de moyenne**, qui résume ce que la matrice veut dire.
5. **La colonne d'inscription à part** : le trimestre d'entrée est partiel, on l'annonce.
6. **Un titre qui dit ce qui est mesuré** (« clients ayant commandé, en % de la cohorte »), pas « matrice de rétention ».


![Version présentable de la matrice de rétention : huit cohortes inscrites de 2023 à 2024, huit trimestres chacune, avec les effectifs et la moyenne par trimestre.](figures/ch04-cohortes-presentable.png)

### 4.4.4 Ce que l'on écrit sous le tableau

Un tableau seul est une énigme ; **les trois phrases qui l'accompagnent** sont l'analyse. Elles disent ce qu'on voit, ce que cela signifie, et ce que cela ne permet pas de dire. Pour la matrice ci-dessus :

> *Sur huit cohortes de 2023 et 2024 (de 149 à 188 clients chacune), la part de clients qui commandent chaque trimestre se stabilise à 36 % dès le trimestre qui suit l'inscription et ne baisse pas pendant les sept trimestres suivants. Le trimestre d'inscription (27 %) est partiel. Les écarts entre cases, de l'ordre de dix points, restent dans le bruit statistique attendu pour des cohortes de 150 à 190 clients, et le pic des quatrièmes trimestres vient de la saison des fêtes, pas d'un effet d'âge. Ce tableau ne dit pas pourquoi les clients restent aussi actifs : il ne permet pas de distinguer la qualité de l'offre de la nature des clients recrutés.*

Ces phrases suivent une grammaire reproductible : **le fait** (avec ses chiffres et ses effectifs), **la lecture** (ce que cela veut dire, en écartant les artefacts qu'on connaît : trimestre partiel, saison), **la limite** (ce qu'on ne peut pas conclure). Remarquez que la phrase de limite est la plus importante : c'est celle qui empêche qu'on prenne une corrélation observée pour une explication.

Trois erreurs de présentation reviennent souvent : montrer le **triangle complet** sans prévenir que les cases de droite reposent sur peu de cohortes ; présenter une **moyenne de cohortes d'âges différents** comme un taux de rétention global ; et conclure à une **tendance** sur des cohortes de 40 personnes.

> ✅ **À retenir.** L'**entonnoir** se lit par effectifs, par taux d'étapes et en **comparaison** (source, appareil, période) : les pertes qui comptent sont celles des clients qui voulaient acheter. La **matrice de cohortes** se présente en rectangle observé, avec effectifs, moyenne et trois phrases (le fait, la lecture, la limite). Dans les deux cas, on affiche l'**incertitude** et l'on dit ce que le tableau ne démontre pas.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.8, exercices 4.11 et 4.12.


## Bilan du chapitre 4

Vous savez maintenant :

- **distinguer** une segmentation (« qui sont-ils ? », une photo à une date) d'une analyse de cohortes (« que deviennent-ils ? », un film), et choisir l'outil selon la question de la gérante ;
- **construire** des segments **par règles métier** (lisibles, stables) puis **par k-moyennes** : variables choisies, transformées et **standardisées**, une itération calculée à la main, k choisi par le coude, la silhouette et la capacité d'agir, segments **nommés** pour suggérer l'action ;
- **éprouver** une segmentation : **stabilité** (rééchantillonnage), **pouvoir de prédiction** d'un critère extérieur (le semestre suivant), et savoir qu'elle **vieillit** (22,5 % des clients changent de segment en six mois) ;
- **bâtir** une matrice de cohortes honnête (seuls les clients dont on connaît l'entrée), la **lire** dans trois directions (lignes, colonnes, diagonales), **séparer âge, période et cohorte**, et éviter les pièges des **petits effectifs** et de l'**observation tronquée** ;
- **mesurer** la rétention en nombre de clients, en revenu et en cumul, et comparer des nouveaux clients **à durée d'observation égale** ;
- (en option) **scorer** les clients par **RFM** et vérifier les segments ; estimer une **valeur vie client** par la formule et par les cohortes, en précisant dénominateur, horizon, marge et actualisation ; parler du **churn** comme d'une probabilité qui dépend du silence et du rythme du client ;
- (en option) **lire un entonnoir** (par effectifs, taux d'étapes et comparaisons) et **présenter** un tableau de cohortes (rectangle observé, effectifs, moyenne, trois phrases : le fait, la lecture, la limite).

Le tableau suivant résume **ce que nous avons mesuré** sur les données de la boutique, avec la vérité programmée quand on la connaît.

| Question | Résultat mesuré | Ce qu'il faut en retenir |
|---|---|---|
| Clients réguliers (règle : ≥ 3 commandes sur 12 mois) | 29 % des clients, 74 % du chiffre d'affaires de l'année | l'enjeu est concentré |
| Segmentation par k-moyennes | 4 segments, silhouette 0,276 ; stabilité 0,91 à 0,99 | des groupes utiles mais pas des îlots séparés |
| Prédiction au semestre suivant | 83 % des réguliers actifs recommandent, 43 à 49 % pour les autres | la segmentation prédit un critère extérieur |
| Étiquette « chasseurs de promotions » | 15,9 % de leurs commandes au S2 avec un code, contre 12,5 à 14,1 % ailleurs | un nom doit se tester : c'était un effet de petits nombres |
| Segmenter sans standardiser | accord de 0,35 seulement avec la version correcte | l'échelle des variables décide du résultat |
| Rétention des cohortes | 36 % de clients actifs par trimestre, sans érosion avec l'âge | vérité programmée : aucun désengagement |
| Effet de la période | 41–43 % chaque quatrième trimestre, 32–34 % sinon | la saison, pas un effet de cohorte |
| Colonne de droite de la matrice (âge 11) | 44 %, mais une seule cohorte, observée en T4 | ne jamais lire les colonnes à une cohorte |
| Cohortes mensuelles | 42 à 66 clients ; intervalle de 9 % à 28 % pour un taux de 16 % | regrouper plutôt que lire du bruit |
| Nouveaux clients qui reviennent en 180 jours | 70 % (2023), 62 % (2024), 56 % (2025) | la comparaison à durée égale révèle une baisse |
| RFM | champions : 25 % des clients, 55 % du chiffre d'affaires, 90 % recommandent | le score est ordonné comme annoncé |
| Valeur vie client | 578 € (sans actualisation) ou 437 € (8 %) par client actif ; environ 69 € de marge la première année par client inscrit | le dénominateur change tout |
| Churn | 18,7 % de silence en un an ; 36 % de retour en six mois après plus d'un an de silence | un silence n'est pas un départ |
| Entonnoir du site | conversion 4,8 % ; e-mail 8,7 %, réseaux 2,2 % ; aucun écart selon l'appareil | la source compte, l'appareil non |

Le fil conducteur du chapitre tient en une phrase : **un groupe n'est utile que s'il change une décision, et un tableau de groupes n'est honnête que si l'on dit sur quoi il repose**. Une segmentation sans vérification est une jolie image ; une matrice de cohortes sans effectifs est une rumeur ; un chiffre de rétention sans durée d'observation égale est un artefact.

> ⚠️ **Rappel d'honnêteté.** Les clients, leurs commandes et leurs sessions sont **simulés**. En particulier, le comportement des clients n'évolue pas avec l'âge dans ces données (aucun désengagement n'a été programmé) : ne cherchez pas le « vrai » taux de rétention d'une boutique dans ces chiffres. Ce sont les **méthodes**, et leurs pièges, qui s'appliquent à de vraies données.

Le chapitre 5 passe d'une vision par client à une vision par **période** : les **séries temporelles**, c'est-à-dire l'évolution des ventes dans le temps, sa tendance et sa saisonnalité, que nous avons déjà croisées (l'effet du quatrième trimestre) sans les mesurer.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 à 4.8 (règles et k-moyennes, stabilité, cohortes, RFM, valeur vie client, réachat, entonnoir) et exercices 4.1 à 4.12.
