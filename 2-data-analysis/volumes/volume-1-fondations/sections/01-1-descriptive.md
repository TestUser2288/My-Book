## 1.1 Statistique descriptive : centre, dispersion, forme

Décrire un jeu de données, c'est répondre à trois questions : **autour de quelle valeur** se répartissent les observations (le centre), **à quel point** elles s'écartent les unes des autres (la dispersion), et **quelle allure** a cette répartition (la forme : symétrique ou étirée, avec ou sans valeurs extrêmes). Ces trois familles de nombres sont les **statistiques descriptives**. Elles ne démontrent rien : elles **résument**. Mais un bon résumé évite la moitié des erreurs d'analyse, et un mauvais résumé (une moyenne seule, par exemple) en fabrique beaucoup.

### 1.1.1 Résumer un panier : le centre

Pour garder les calculs lisibles, partons de **neuf commandes seulement** : les neuf premières enregistrées en boutique le 15 avril 2025. Leurs paniers, en euros, dans l'ordre où elles sont arrivées :

$$9{,}69\;;\;207{,}56\;;\;132{,}37\;;\;258{,}83\;;\;66{,}75\;;\;22{,}56\;;\;50{,}27\;;\;48{,}74\;;\;128{,}25.$$

**La moyenne** est le total divisé par le nombre d'observations :

$$\bar x=\frac{1}{n}\sum_{i=1}^{n}x_i=\frac{925{,}02}{9}=102{,}78\ €.$$

C'est le montant que chaque commande aurait si l'on **répartissait le total à parts égales**. C'est aussi le point d'équilibre : si l'on posait les neuf montants sur une règle, la règle tiendrait en équilibre sur 102,78 €.

**La médiane** est la valeur du milieu quand on range les observations par ordre croissant : la moitié des commandes est en dessous, la moitié au-dessus. Rangeons :

$$9{,}69\;;\;22{,}56\;;\;48{,}74\;;\;50{,}27\;;\;\mathbf{66{,}75}\;;\;128{,}25\;;\;132{,}37\;;\;207{,}56\;;\;258{,}83.$$

Avec neuf valeurs, c'est la cinquième : **66,75 €**. (Avec un nombre pair de valeurs, on fait la moyenne des deux valeurs centrales.)

Les deux résumés diffèrent de **36 €**, et cet écart est une information : quelques grosses commandes (207,56 € et 258,83 €) **tirent la moyenne vers le haut** sans toucher la médiane. Si l'on retirait la commande de 258,83 €, la moyenne tomberait à 83,3 € et la médiane à 58,5 € ; si on la remplaçait par 2 588,30 € (une erreur de virgule), la moyenne exploserait à 361,6 €, alors que la médiane ne bougerait pas. La médiane est **robuste** aux valeurs extrêmes ; la moyenne ne l'est pas.

> 💡 **Moyenne et médiane, en une image.** La moyenne est le **centre de gravité** de la distribution : elle tient compte de la distance de chaque valeur. La médiane est le **centre de position** : elle ne tient compte que de l'ordre. Quand la distribution est étirée d'un côté, la moyenne se laisse entraîner de ce côté ; la médiane reste au milieu des observations.

Deux autres résumés du centre servent régulièrement. **Le mode** est la valeur la plus fréquente : il a un sens pour une variable qui prend peu de valeurs (le nombre d'articles par commande), pas pour un montant en euros où presque toutes les valeurs sont distinctes (on le remplace alors par la **classe modale** d'un histogramme). **La moyenne tronquée** retire un pourcentage de valeurs de chaque extrémité avant de moyenner : c'est un compromis entre la moyenne (sensible aux extrêmes) et la médiane (qui les ignore toutes).

Voyons ces quatre résumés sur les 36 395 commandes de la boutique.

```python
from scipy.stats import trim_mean
print(panier.agg(["mean", "median"]).round(2).to_dict())
print("moyenne tronquée à 5 % :", round(trim_mean(panier, 0.05), 2))
print("mode du nombre de lignes par commande :", lignes.groupby("id_commande").size().mode()[0])
```
<!--sortie-->
```text
{'mean': 100.38, 'median': 79.8}
moyenne tronquée à 5 % : 92.44
mode du nombre de lignes par commande : 2
```

```python hide
x9 = np.array([9.69, 207.56, 132.37, 258.83, 66.75, 22.56, 50.27, 48.74, 128.25])
ref9 = cmd[(cmd["date_commande"] == "2025-04-15") & (cmd["canal"] == "Boutique")]["panier"].head(9).round(2).values
assert np.allclose(x9, ref9), (x9, ref9)
assert round(x9.sum(), 2) == 925.02 and round(x9.mean(), 2) == 102.78 and np.median(x9) == 66.75
x_sans = np.delete(x9, 3)
assert round(x_sans.mean(), 1) == 83.3 and round(np.median(x_sans), 1) == 58.5
x_erreur = x9.copy(); x_erreur[3] = 2588.30
assert round(x_erreur.mean(), 1) == 361.6 and np.median(x_erreur) == 66.75
x = cmd["panier"]
NUM("panier_median", x.median())
NUM("panier_tronque", stats.trim_mean(x, 0.05))
NUM("ecart_moy_med", x.mean() - x.median())
NUM("mode_lignes", lig.groupby("id_commande").size().mode()[0])
nl = lig.groupby("id_commande").size()
NUM("part_mode_lignes", (nl == nl.mode()[0]).mean() * 100)
p95 = x.quantile(0.95)
NUM("p95", p95)
tri = np.sort(x.values)[::-1]
NUM("part_top10", tri[: int(0.1 * len(tri))].sum() / tri.sum() * 100)
NUM("part_sous_moy", (x < x.mean()).mean() * 100)
```
<!--sortie-->
```text
NUM panier_median 79.8
NUM panier_tronque 92.43703941142351
NUM ecart_moy_med 20.575251545541974
NUM mode_lignes 2
NUM part_mode_lignes 35.348262123918126
NUM p95 254.4509999999997
NUM part_top10 27.933476217591153
NUM part_sous_moy 60.84352246187663
```

L'écart entre moyenne et médiane se retrouve à grande échelle : **100,38 €** contre **79,80 €**, soit 21 € d'écart. La moyenne tronquée (92,44 €) tombe entre les deux. Et le fait le plus parlant est que **61 % des commandes sont en dessous de la moyenne** : la gérante voit passer une majorité de paniers inférieurs au « panier moyen » de la boutique. Par ailleurs, le nombre de lignes par commande est le plus souvent de **2** (c'est le mode, atteint par 35 % des commandes).

#### Quel résumé annoncer ?

Il n'y a pas de bon résumé en soi : il y a un résumé adapté à la **question posée**.

| Question | Résumé adapté | Pourquoi |
|---|---|---|
| Combien une commande rapporte-t-elle **en moyenne**, pour prévoir le chiffre d'affaires d'un mois ? | la **moyenne** | total = moyenne × nombre de commandes ; la moyenne conserve le total |
| Que dépense un client **typique** ? | la **médiane** | elle n'est pas tirée par les grosses commandes |
| À partir de quel montant une commande est-elle « grosse » ? | un **centile** (par exemple le 95ᵉ : 254 €) | on cherche un seuil, pas un centre |
| Quel est le nombre d'articles le plus courant ? | le **mode** | variable à peu de valeurs |

Pour la gérante, la réponse honnête est donc : « le panier moyen est de 100 € ; **mais** une commande sur deux est inférieure à 80 €, et les 10 % de commandes les plus importantes représentent à elles seules **28 %** du chiffre d'affaires ». La moyenne sert à prévoir, la médiane à décrire. Les deux ensemble disent quelque chose que ni l'une ni l'autre ne dit seule.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.1, exercice 1.1.

### 1.1.2 Mesurer la dispersion

Deux boutiques peuvent avoir le même panier moyen de 100 € : l'une avec des paniers tous compris entre 90 € et 110 €, l'autre avec des paniers de 5 € à 900 €. Le centre ne les distingue pas. La **dispersion** mesure l'écart entre les observations.

**L'étendue** est la différence entre la plus grande et la plus petite valeur : $258{,}83-9{,}69=249{,}14$ € pour nos neuf commandes. Simple, mais fragile : elle ne dépend que de deux observations.

**Les quartiles** coupent les observations rangées en quatre parts égales. Le premier quartile $Q_1$ laisse 25 % des valeurs en dessous, le troisième $Q_3$ en laisse 75 %. Avec $n$ valeurs rangées, la méthode la plus courante (celle d'Excel avec `QUARTILE.INCLURE`, de R et de pandas par défaut) cherche la valeur à la position $1+p\,(n-1)$, en interpolant entre deux observations voisines si la position n'est pas entière. Pour $n=9$ : $Q_1$ est à la position $1+0{,}25\times8=3$, soit **48,74 €**, et $Q_3$ à la position $1+0{,}75\times8=7$, soit **132,37 €**. **L'écart interquartile** (EIQ) est $Q_3-Q_1=83{,}63$ € : c'est l'étendue des 50 % de valeurs centrales, insensible aux extrêmes.

**La variance et l'écart-type** mesurent la distance **typique** des observations à la moyenne. On part des écarts $x_i-\bar x$, on les élève au carré (pour que les écarts positifs et négatifs ne s'annulent pas), on les additionne, et l'on divise par $n-1$ :

$$s^2=\frac{1}{n-1}\sum_{i=1}^{n}(x_i-\bar x)^2,\qquad s=\sqrt{s^2}.$$

Le calcul sur nos neuf commandes, moyenne 102,78 € :

| Commande $x_i$ | Écart $x_i-\bar x$ | Écart au carré |
|---:|---:|---:|
| 9,69 | −93,09 | 8 665,7 |
| 22,56 | −80,22 | 6 435,2 |
| 48,74 | −54,04 | 2 920,3 |
| 50,27 | −52,51 | 2 757,3 |
| 66,75 | −36,03 | 1 298,2 |
| 128,25 | 25,47 | 648,7 |
| 132,37 | 29,59 | 875,6 |
| 207,56 | 104,78 | 10 978,8 |
| 258,83 | 156,05 | 24 351,6 |
| **Somme** | 0 | **58 931,5** |

La somme des écarts vaut 0 par construction (c'est ce qui définit la moyenne). La variance vaut $58\,931{,}5/8\approx7\,366{,}4$ €² et l'écart-type $s=\sqrt{7\,366{,}4}\approx\mathbf{85{,}83}$ €. L'écart-type s'exprime dans **la même unité** que les données, ce qui le rend interprétable : un panier s'écarte typiquement de 86 € de la moyenne.

> 💡 **Pourquoi diviser par $n-1$ et pas par $n$ ?** Les écarts sont mesurés par rapport à la moyenne **de l'échantillon**, qui est précisément la valeur la plus proche des observations : ils sont mécaniquement un peu plus petits que les écarts à la vraie moyenne (inconnue). Diviser par $n-1$ corrige ce biais. On dit aussi que, la moyenne étant connue, **seuls $n-1$ écarts sont libres** : le dernier se déduit des autres, puisque leur somme vaut zéro. Pour des milliers d'observations, la différence entre $n$ et $n-1$ disparaît ; pour neuf observations, elle compte.

Enfin, **le coefficient de variation** $\text{CV}=s/\bar x$ exprime la dispersion **relativement** au centre. Il permet de comparer des grandeurs d'unités différentes (des paniers en euros et des délais en jours) : ici $85{,}83/102{,}78\approx0{,}84$.

Sur l'ensemble des commandes :

```python
q1, q3 = panier.quantile([0.25, 0.75])
print("quartiles :", round(q1, 2), round(q3, 2), "| écart interquartile :", round(q3 - q1, 2))
print("écart-type :", round(panier.std(), 2), "| coefficient de variation :", round(panier.std() / panier.mean(), 2))
print("min et max :", panier.min(), panier.max())
```
<!--sortie-->
```text
quartiles : 42.9 135.4 | écart interquartile : 92.5
écart-type : 80.73 | coefficient de variation : 0.8
min et max : 2.32 987.9
```

```python hide
dev = x9 - x9.mean()
assert round((dev ** 2).sum(), 1) == 58931.5
assert round(np.quantile(x9, 0.25), 2) == 48.74 and round(np.quantile(x9, 0.75), 2) == 132.37
assert round(x9.std(ddof=1), 2) == 85.83 and round(x9.std(ddof=1) / x9.mean(), 2) == 0.84
q1, q3 = x.quantile([0.25, 0.75])
NUM("q1", q1); NUM("q3", q3); NUM("eiq", q3 - q1)
NUM("panier_sd", x.std()); NUM("cv", x.std() / x.mean())
NUM("panier_min", x.min()); NUM("panier_max", x.max())
```
<!--sortie-->
```text
NUM q1 42.9
NUM q3 135.4
NUM eiq 92.5
NUM panier_sd 80.73150469249322
NUM cv 0.804296910338142
NUM panier_min 2.32
NUM panier_max 987.9
```

Les paniers de la boutique ont un écart-type de **81 €** pour une moyenne de 100 € : un coefficient de variation de **0,80**, très élevé. Les 50 % de commandes centrales vont de 43 € à 135 € (EIQ de 92 €), alors que la plus petite vaut 2,32 € et la plus grande 988 €. Il y a de tout, et c'est pourquoi **la moyenne seule est un mauvais portrait** de la clientèle.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.1, exercice 1.2.

### 1.1.3 La forme : asymétrie, queues et valeurs aberrantes

Le troisième aspect d'une distribution est sa **forme**. Dessinons les paniers.

```python hide
fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.6), gridspec_kw={"width_ratios": [2.3, 1]})
ax = axs[0]
ax.hist(x, bins=np.arange(0, 1001, 20), color=BLEU, alpha=0.75, edgecolor="white", linewidth=0.4)
ax.axvline(x.mean(), color=ORANGE, lw=2); ax.axvline(x.median(), color=VIOLET, lw=2, ls="--")
ax.set_ylim(0, 6700)
ax.text(x.mean() + 8, 6500, f"moyenne {x.mean():.0f} €", color=ORANGE, fontsize=9, va="top")
ax.text(x.median() - 8, 6500, f"médiane {x.median():.0f} €", color=VIOLET, fontsize=9, va="top", ha="right")
ax.set_xlim(0, 700); ax.set_xlabel("panier d'une commande (€)"); ax.set_ylabel("nombre de commandes"); ax.set_title("Histogramme des paniers")
ax = axs[1]
ax.boxplot(x, vert=True, widths=0.5, patch_artist=True, showfliers=True, flierprops=dict(marker="o", markersize=2, markerfacecolor=MUET, markeredgecolor="none", alpha=0.5),
           boxprops=dict(facecolor="#cde2fb", edgecolor=BLEU), medianprops=dict(color=VIOLET, lw=2), whiskerprops=dict(color=BLEU), capprops=dict(color=BLEU))
ax.set_xticks([]); ax.set_ylabel("panier (€)"); ax.set_title("Boîte à moustaches")
style.save(fig, "ch01-paniers.png")
```
<!--sortie-->
```text
figure : ch01-paniers.png
```

![Les paniers des commandes de la boutique. À gauche, l'histogramme (classes de 20 €) : la distribution est étirée vers la droite, la moyenne (orange) est plus grande que la médiane (violet). À droite, la boîte à moustaches : la boîte va du premier au troisième quartile, le trait central est la médiane, les points au-dessus de la moustache sont les valeurs jugées « aberrantes » par la règle de 1,5 écart interquartile.](figures/ch01-paniers.png)

L'histogramme a une allure typique des montants : un **pic à gauche** (beaucoup de petits paniers) et une **longue traîne à droite** (quelques paniers très gros). On dit que la distribution est **asymétrique à droite** (ou « étalée à droite »). La **boîte à moustaches** résume la même information : la boîte contient la moitié centrale des commandes ($Q_1$ à $Q_3$), le trait épais est la médiane, les moustaches s'étendent jusqu'aux valeurs les plus éloignées qui ne sont pas jugées extrêmes, et les points isolés sont les extrêmes.

On mesure l'asymétrie par le **coefficient d'asymétrie** (*skewness*), la moyenne des écarts réduits élevés au cube :

$$g_1=\frac{1}{n}\sum_{i=1}^{n}\left(\frac{x_i-\bar x}{s}\right)^3.$$

Il vaut 0 pour une distribution symétrique, est positif quand la traîne est à droite et négatif quand elle est à gauche. Le **coefficient d'aplatissement** (*kurtosis*, ici en « excès » : 0 pour une courbe normale) mesure le poids des **queues** : il est grand quand il y a plus de valeurs extrêmes que ne le prévoirait une courbe normale. Excel (`COEFFICIENT.ASYMETRIE`, `KURTOSIS`) et pandas utilisent la même version corrigée pour les petits échantillons.

```python
print("asymétrie :", round(panier.skew(), 2), "| aplatissement (excès) :", round(panier.kurt(), 2))
```
<!--sortie-->
```text
asymétrie : 1.85 | aplatissement (excès) : 5.8
```

#### Les valeurs aberrantes : une règle, pas un verdict

Quand une valeur est-elle « aberrante » ? La règle de **Tukey** (celle qui dessine les moustaches) déclare extrême toute valeur située à plus de **1,5 écart interquartile** au-delà des quartiles :

$$x<Q_1-1{,}5\times\text{EIQ}\qquad\text{ou}\qquad x>Q_3+1{,}5\times\text{EIQ}.$$

Pour nos neuf commandes, la borne supérieure est $132{,}37+1{,}5\times83{,}63\approx257{,}8$ € : la commande de 258,83 € la dépasse **d'un euro**. Pour l'ensemble des commandes, la borne inférieure est négative (aucun panier ne peut être « trop petit ») et la borne supérieure vaut :

```python hide
NUM("borne_sup", q3 + 1.5 * (q3 - q1))
NUM("borne_inf", q1 - 1.5 * (q3 - q1))
NUM("n_aberrants", (x > q3 + 1.5 * (q3 - q1)).sum())
NUM("part_aberrants", (x > q3 + 1.5 * (q3 - q1)).mean() * 100)
NUM("skew", x.skew()); NUM("kurt", x.kurt())
assert abs(132.37 + 1.5 * 83.63 - 257.815) < 1e-9 and 258.83 > 257.815
```
<!--sortie-->
```text
NUM borne_sup 274.15
NUM borne_inf -95.85
NUM n_aberrants 1400
NUM part_aberrants 3.846682236570958
NUM skew 1.8499143085919443
NUM kurt 5.797077772387226
```

135,40 + 1,5 × 92,50 = **274,15 €**. Au-delà, la règle signale **1 400 commandes**, soit 3,8 % du total ; l'asymétrie vaut **1,85** et l'aplatissement **5,8**, confirmant une traîne droite lourde.

> ⚠️ **« Aberrant » ne veut pas dire « faux ».** La règle de Tukey signale des valeurs **inhabituelles**, pas des erreurs. Une commande de 700 € passée par un client qui meuble son salon est parfaitement valide ; une commande de 2 588,30 € parce que la virgule a glissé est une erreur de saisie. Devant une valeur extrême, on se pose **trois questions dans cet ordre** : est-ce une *erreur* (à corriger ou à retirer) ? est-ce un cas *légitime mais rare* (à garder, en le sachant) ? ou est-ce un cas d'un **autre type** (une commande de professionnel, une revente) qui mérite une analyse à part ? On **ne supprime jamais** une valeur au seul motif qu'elle est grande, et l'on dit toujours ce que l'on a fait.

Le **résumé des cinq nombres** (minimum, $Q_1$, médiane, $Q_3$, maximum) est le portrait le plus économique d'une distribution : 2,32 ; 42,90 ; 79,80 ; 135,40 ; 987,90. Il montre l'asymétrie d'un coup d'œil : la médiane est plus proche de $Q_1$ que de $Q_3$, et le maximum est très loin de $Q_3$.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.1, exercice 1.3.

### 1.1.4 Quand les moyennes mentent

Une moyenne est un calcul simple, ce qui la rend dangereuse : on la calcule sans réfléchir à **ce qu'elle moyenne**. Deux pièges reviennent sans cesse.

#### La moyenne des moyennes

La gérante demande : « Quel est le taux de retour de la boutique ? » Vous avez le taux de chacun des trois canaux, calculé sur les lignes vendues en 2023-2025 :

| Canal | Lignes vendues | Lignes retournées | Taux de retour |
|---|---:|---:|---:|
| Boutique | 39 362 | 1 211 | 3,08 % |
| Réseaux | 9 071 | 605 | 6,67 % |
| Site | 35 472 | 3 186 | 8,98 % |

Faire la moyenne des trois taux donne 6,24 %. Mais le taux de **toute la boutique** est le nombre total de retours divisé par le nombre total de lignes : 5 002 / 83 905 = **5,96 %**. L'écart (0,28 point) vient de ce que la moyenne simple traite les trois canaux **à égalité**, alors que les canaux n'ont pas le même poids : la Boutique vend près de la moitié des lignes, et son taux est le plus bas. **Une moyenne de pourcentages doit être pondérée** par la taille de chaque groupe (c'est la moyenne pondérée, que la section 1.5.3 détaille). La règle pratique : **repartez toujours des totaux** (retours et lignes), jamais des ratios.

```python hide
ls = lig.groupby("canal").agg(n=("id_ligne", "size"), r=("retournee", "sum"))
for k, row in ls.iterrows():
    kk = k.replace("é", "e")
    NUM(f"n_{kk}", row.n); NUM(f"r_{kk}", row.r); NUM(f"t_{kk}", row.r / row.n * 100)
NUM("taux_simple", (ls.r / ls.n).mean() * 100)
NUM("n_total", ls.n.sum()); NUM("r_total", ls.r.sum()); NUM("taux_global", ls.r.sum() / ls.n.sum() * 100)
NUM("ecart_taux", ((ls.r / ls.n).mean() - ls.r.sum() / ls.n.sum()) * 100)
assert ls.n.sum() == len(lig)
```
<!--sortie-->
```text
NUM n_Boutique 39362
NUM r_Boutique 1211
NUM t_Boutique 3.076571312433311
NUM n_Reseaux 9071
NUM r_Reseaux 605
NUM t_Reseaux 6.6696064380994375
NUM n_Site 35472
NUM r_Site 3186
NUM t_Site 8.981732070365359
NUM taux_simple 6.242636606966037
NUM n_total 83905
NUM r_total 5002
NUM taux_global 5.961504081997497
NUM ecart_taux 0.28113252496853935
```

#### Le paradoxe de Simpson

Le second piège est plus troublant : **une tendance observée sur l'ensemble peut s'inverser dans chaque sous-groupe**. Voici un exemple volontairement inventé (les chiffres ne viennent pas des données de la boutique). La boutique a testé deux campagnes d'e-mail, A et B, auprès de 1 500 clients chacune. On compte les clients qui ont acheté dans la semaine, en séparant les clients fidèles (titulaires d'une carte) des nouveaux :

| | Campagne A | | Campagne B | |
|---|---:|---:|---:|---:|
| | envois | achats | envois | achats |
| Clients fidèles | 1 200 | 240 (20 %) | 300 | 66 (22 %) |
| Nouveaux clients | 300 | 15 (5 %) | 1 200 | 78 (6,5 %) |
| **Ensemble** | 1 500 | 255 (**17,0 %**) | 1 500 | 144 (**9,6 %**) |

Dans **chaque** groupe, la campagne B convertit mieux (22 % contre 20 % chez les fidèles, 6,5 % contre 5 % chez les nouveaux). Et pourtant, **sur l'ensemble**, A l'emporte nettement (17,0 % contre 9,6 %). Il n'y a pas d'erreur de calcul : la campagne B a été envoyée surtout à des nouveaux clients, qui achètent beaucoup moins par nature. Le **type de client** est un **facteur de confusion** : il influence à la fois la campagne reçue et le résultat.

```python hide
a_f, a_n, b_f, b_n = (1200, 240), (300, 15), (300, 66), (1200, 78)
assert a_f[1] / a_f[0] == 0.20 and a_n[1] / a_n[0] == 0.05 and b_f[1] / b_f[0] == 0.22 and b_n[1] / b_n[0] == 0.065
assert round((a_f[1] + a_n[1]) / 1500, 3) == 0.17 and round((b_f[1] + b_n[1]) / 1500, 3) == 0.096
```

La leçon n'est pas « il faut toujours découper » (on peut découper à l'infini et trouver n'importe quoi), mais : **avant de comparer des groupes, demandez-vous s'ils sont comparables**. Les sections 1.3 et 1.4 reviendront sur cette question, qui est au cœur de l'analyse de données.

> ✅ **À retenir.** (1) Moyenne et médiane répondent à des questions différentes : la moyenne conserve le total, la médiane décrit le cas typique. (2) Un centre sans dispersion n'est pas un résumé. (3) Une valeur extrême est une question, pas une erreur. (4) Une moyenne de ratios se calcule à partir des totaux ; une comparaison de groupes suppose des groupes comparables.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.2, exercices 1.4 et 1.5.

### 1.1.5 Les mêmes chiffres dans Excel et dans R

Un chiffre qui sort d'un seul outil est un chiffre à vérifier. Voyons comment obtenir les mêmes résumés dans **Excel** et dans **R**, et pourquoi ils concordent.

Dans Excel, on écrit les neuf paniers dans une colonne, puis chaque résumé est une formule. Voici la feuille avec les formules saisies en français ; les formules ont été **vérifiées en les faisant calculer par LibreOffice Calc**, et le dessin est une maquette (ce n'est pas une capture d'Excel).

```python hide
import tempfile, os, shutil
tmp = tempfile.mkdtemp(prefix="ch01_", dir=os.environ.get("TMPDIR"))
formules_en = ["=AVERAGE(A2:A10)", "=MEDIAN(A2:A10)", "=QUARTILE.INC(A2:A10,1)", "=QUARTILE.INC(A2:A10,3)", "=STDEV.S(A2:A10)", "=SKEW(A2:A10)", "=TRIMMEAN(A2:A10,0.25)"]
lignes_xl = [["Panier", None, "Statistique", "Formule"]]
labels = ["Moyenne", "Médiane", "Premier quartile", "Troisième quartile", "Écart-type", "Asymétrie", "Moy. tronquée (7 valeurs)"]
for i in range(9):
    ligne = [float(x9[i]), None, labels[i] if i < 7 else None, None]
    lignes_xl.append(ligne)
for i, f in enumerate(formules_en):
    lignes_xl[i + 1].append(f)
chemin = X.classeur(os.path.join(tmp, "neuf.xlsx"), {"Feuil1": lignes_xl}, largeurs=[10, 3, 24, 8, 14])
val = X.valeurs(X.recalculer(chemin, tmp))
res_xl = [val[i + 1][4] for i in range(7)]
ref = [x9.mean(), np.median(x9), np.quantile(x9, 0.25), np.quantile(x9, 0.75), x9.std(ddof=1), stats.skew(x9, bias=False), np.mean(np.sort(x9)[1:-1])]
assert all(abs(a - b) < 1e-6 for a, b in zip(res_xl, ref)), (res_xl, ref)
NUM("tm_excel", res_xl[6])
affiche = [["Panier", None, "Statistique", "Résultat", "Formule (Excel en français)"]]
for i in range(7):
    aff = [float(x9[i]) if i < 9 else None, None, labels[i], float(res_xl[i]), X.en_fr(formules_en[i])]
    affiche.append(aff)
for i in range(7, 9):
    affiche.append([float(x9[i]), None, None, None, None])
X.maquette(os.path.join("figures", "ch01-excel-resume.png"), affiche, largeurs=[9, 2, 24, 10, 34], active="D2", formule=X.en_fr(formules_en[0]), surligne=["A2:A10"])
shutil.rmtree(tmp, ignore_errors=True)
```
<!--sortie-->
```text
NUM tm_excel 93.7857142857143
```

![Maquette d'une feuille Excel : les neuf paniers en colonne A, et les résumés calculés par des formules (colonnes C à E). La maquette est dessinée à partir des valeurs calculées par LibreOffice Calc : ce n'est pas une capture d'écran d'Excel.](figures/ch01-excel-resume.png)

Les résultats concordent avec le calcul à la main : 102,78 € ; 66,75 € ; 48,74 € ; 132,37 € ; 85,83 €. Trois remarques de lecture :

- `QUARTILE.INCLURE` utilise l'interpolation « inclusive » vue plus haut (position $1+p(n-1)$) ; il existe aussi `QUARTILE.EXCLURE`, qui donne **d'autres quartiles** sur de petits jeux de données. Précisez toujours la version que vous utilisez.
- `ECARTYPE.STANDARD` divise par $n-1$ (écart-type d'échantillon) ; `ECARTYPE.PEARSON` divise par $n$. Sur un échantillon, c'est le premier qu'il faut.
- `MOYENNE.REDUITE(plage ; proportion)` retire la proportion indiquée **au total** (moitié de chaque côté) et arrondit le nombre de valeurs retirées vers le bas, à un nombre pair : avec 9 valeurs et 0,25, on retire 2,25 → 2 valeurs (la plus petite et la plus grande) ; la moyenne tronquée de la feuille porte donc sur 7 valeurs.

Dans R, les mêmes résumés tiennent en quelques lignes. Calculons-les sur les paniers de **l'année 2025** (le même fichier, un autre outil) :

```r
cmd <- read.csv("donnees/commandes.csv"); lig <- read.csv("donnees/lignes_commande.csv")
panier <- tapply(lig$montant, lig$id_commande, sum)
p25 <- panier[as.character(cmd$id_commande[substr(cmd$date_commande, 1, 4) == "2025"])]
c(moyenne = mean(p25), mediane = median(p25), ecart_type = sd(p25))
quantile(p25, c(0.25, 0.75))      # type 7 : même méthode que pandas et QUARTILE.INCLURE
```
<!--sortie-->
```text
   moyenne    mediane ecart_type 
 102.32996   81.61500   82.32644 
   25%    75% 
 44.09 137.72 
```

```python hide
p25 = cmd[cmd["annee"] == 2025]["panier"]
NUM("moy25", p25.mean()); NUM("med25", p25.median()); NUM("sd25", p25.std())
NUM("q1_25", p25.quantile(0.25)); NUM("q3_25", p25.quantile(0.75)); NUM("n25", len(p25))
```
<!--sortie-->
```text
NUM moy25 102.3299644677893
NUM med25 81.61500000000001
NUM sd25 82.32644482342288
NUM q1_25 44.09
NUM q3_25 137.72
NUM n25 12946
```

En pandas sur les mêmes 12 946 commandes de 2025 : moyenne **102,33**, médiane **81,62**, écart-type **82,33**, quartiles 44,09 et 137,72 : ce sont les nombres que R vient d'afficher (à l'arrondi d'affichage près). Que les trois outils s'accordent n'est pas une formalité : c'est la première **vérification croisée**, que ce livre pratique autant que possible. Quand deux outils donnent deux résultats, la différence est presque toujours une **convention** (quartiles inclusifs ou exclusifs, $n$ ou $n-1$) ou une **donnée différente** (lignes filtrées, valeurs vides), et il faut la trouver avant de publier.

> 🧭 **En pratique.** Excel pour explorer et partager, SQL pour interroger de gros volumes, Python ou R pour automatiser et reproduire : le chapitre 2 détaille Excel, le chapitre 3 SQL et le chapitre 4 Python et R. Ce volume apprend à **passer de l'un à l'autre** en retrouvant les mêmes chiffres.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.3.
