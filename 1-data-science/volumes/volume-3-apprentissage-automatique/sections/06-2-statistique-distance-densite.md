## 6.2 Méthodes statistiques, distances et densités

Les méthodes les plus anciennes de détection d'anomalies reposent sur une idée simple : **une observation est suspecte si elle est loin des autres**. Tout l'art consiste à définir « loin ». Cette section présente quatre définitions de plus en plus fines : la distance **à la médiane**, la distance qui **tient compte des corrélations** (Mahalanobis), la distance **aux voisins les plus proches**, et la distance **relative à la densité locale** (LOF). Ces méthodes ne font jamais appel à l'étiquette : elles apprennent ce qu'est une commande « normale » à partir des seules variables.

```python hide
from scipy.stats import norm, chi2
from sklearn.neighbors import NearestNeighbors, LocalOutlierFactor
from sklearn.covariance import MinCovDet

def tableau(noms):
    """Tableau de résultats (sorties à budget fixé) pour une liste de méthodes."""
    d = pd.DataFrame({n: R[n] for n in noms}).T
    d = d.rename(columns={"rappel1": "rappel type 1", "rappel2": "rappel type 2", "Pk": "précision à k"})
    return d[["AUC", "AP", "précision à k", "rappel type 1", "rappel type 2"]].round(3)
```

### 6.2.1 Le z-score, et pourquoi il faut parfois le rendre robuste

Le **z-score** d'une valeur $x$ mesure son écart à la moyenne en nombre d'écarts-types : $z=(x-\bar x)/s$. On juge anormale une valeur dont $|z|$ dépasse 3. Mais la moyenne et l'écart-type sont eux-mêmes **sensibles aux anomalies**.

Prenons sept montants de commandes d'un même compte : 12, 15, 14, 13, 16, 15 et **480** €. La moyenne vaut 80,7 € et l'écart-type 176,1 € : l'anomalie a gonflé les deux mesures qui devaient la repérer. Son z-score n'est que de $(480-80{,}7)/176{,}1=\mathbf{2{,}27}$, **sous le seuil habituel de 3** : le z-score classique ne voit pas la commande de 480 €. C'est le phénomène de **masquage** : l'anomalie se cache derrière sa propre influence.

Le remède est de remplacer la moyenne par la **médiane** et l'écart-type par l'**écart absolu médian** (MAD, *median absolute deviation*) :

$$\mathrm{MAD}=\operatorname{médiane}\bigl(|x_i-\operatorname{médiane}(x)|\bigr),\qquad z^{\text{rob}}=\frac{x-\operatorname{médiane}(x)}{1{,}4826\ \mathrm{MAD}}.$$

Sur nos sept montants : la médiane vaut 15, les écarts absolus à 15 sont 3, 0, 1, 2, 1, 0 et 465, rangés 0, 0, 1, 1, 2, 3, 465, de médiane **1**. Le MAD vaut 1 et le z-score robuste de 480 est $465/(1{,}4826\times1)\approx\mathbf{314}$ : l'anomalie saute aux yeux. La médiane et le MAD, eux, ne bougent presque pas quand on ajoute une valeur extrême : on dit qu'ils sont **robustes**.

> 📐 **D'où vient la constante 1,4826 ?** Elle rend le MAD comparable à un écart-type. Pour une loi normale $\mathcal N(\mu,\sigma^2)$, la moitié des valeurs est à moins de $a\sigma$ de la médiane, où $a$ vérifie $P(|Z|\le a)=\tfrac12$, c'est-à-dire $a=\Phi^{-1}(0{,}75)\approx 0{,}6745$. Donc $\mathrm{MAD}\approx0{,}6745\,\sigma$ et $\sigma\approx\mathrm{MAD}/0{,}6745=1{,}4826\ \mathrm{MAD}$.

```python hide
x = np.array([12, 15, 14, 13, 16, 15, 480.])
print("moyenne", round(x.mean(), 1), "| écart-type", round(x.std(ddof=1), 1), "| z de 480 :", round((480 - x.mean()) / x.std(ddof=1), 2))
med = np.median(x); mad_x = np.median(np.abs(x - med))
print("médiane", med, "| MAD", mad_x, "| z robuste de 480 :", round((480 - med) / (1.4826 * mad_x), 1))
print("MAD d'une loi normale réduite (simulation, 1 million de tirages) :", round(float(np.median(np.abs(np.random.default_rng(0).normal(size=1_000_000)))), 4), "; Phi^-1(0,75) =", round(float(norm.ppf(0.75)), 4), "; 1/0,6745 =", round(1 / float(norm.ppf(0.75)), 4))
```
<!--sortie-->
```text
moyenne 80.7 | écart-type 176.1 | z de 480 : 2.27
médiane 15.0 | MAD 1.0 | z robuste de 480 : 313.6
MAD d'une loi normale réduite (simulation, 1 million de tirages) : 0.6757 ; Phi^-1(0,75) = 0.6745 ; 1/0,6745 = 1.4826
```

**Plusieurs variables.** Nos commandes ont dix variables. Pour une variable continue ou de comptage, on calcule le z-score de chaque variable, puis on additionne les valeurs absolues : une fraude qui est *modérément* étrange sur plusieurs variables obtient un score élevé, même si aucune variable ne dépasse seule le seuil. Les variables binaires (appareil inconnu, IP étrangère) n'ont pas de z-score qui ait un sens ; nous n'utilisons ici que les six variables continues ou de comptage : montant, distance entre les adresses, nombre de commandes des dernières 24 heures, ancienneté du compte, délai depuis la dernière commande et nombre d'articles (en logarithme pour les quatre premières, car elles sont très asymétriques : chapitre 4, section 4.1).

> ⚠️ **Le piège du MAD nul.** Si plus de la moitié des valeurs sont égales (donc à la médiane), alors le MAD vaut **zéro** et le z-score robuste est indéfini. C'est exactement le cas du nombre de commandes des dernières 24 heures : **74 %** des commandes sont les premières de la journée pour leur compte, la médiane vaut 0, le MAD vaut 0. Si l'on ignore cette variable (ou si on la laisse à zéro), le détecteur « robuste » devient aveugle à la **rafale de commandes**, qui est justement le signe des prises de contrôle de compte. Une solution classique est d'utiliser, quand le MAD est nul, l'**écart absolu moyen** à la médiane multiplié par 1,2533 (la constante qui le rend comparable à un écart-type pour une loi normale : $E|X-\mu|=\sigma\sqrt{2/\pi}$, donc $\sigma\approx1{,}2533\,E|X-\mu|$).

```python hide
cont = ["log_montant", "log_distance", "nb_cmd_24h", "log_age_compte", "log_delai", "nb_articles"]
mu, sd = X_app[cont].mean(), X_app[cont].std()
med = X_app[cont].median(); ecarts = (X_app[cont] - med).abs(); mad = ecarts.median()
echelle_repli = pd.Series(np.where(mad > 0, 1.4826 * mad, 1.2533 * ecarts.mean()), index=cont)
z_classique = ((X_test[cont] - mu) / sd).abs()
z_mad = ((X_test[cont] - med) / (1.4826 * mad).replace(0, np.nan)).abs().fillna(0)      # variable à MAD nul : contribution nulle
z_repli = ((X_test[cont] - med) / echelle_repli).abs()
evaluer("z-score classique", z_classique.sum(axis=1).values)
evaluer("z-score robuste (MAD seul)", z_mad.sum(axis=1).values)
evaluer("z-score robuste (avec repli)", z_repli.sum(axis=1).values)
print("part des commandes sans autre commande dans les 24 h :", round(float((X_app["nb_cmd_24h"] == 0).mean()), 3), "| variables à MAD nul :", [c for c in cont if mad[c] == 0])
print(tableau(["z-score classique", "z-score robuste (MAD seul)", "z-score robuste (avec repli)"]).to_string())
```
<!--sortie-->
```text
part des commandes sans autre commande dans les 24 h : 0.743 | variables à MAD nul : ['nb_cmd_24h']
                                AUC     AP  précision à k  rappel type 1  rappel type 2
z-score classique             0.939  0.433          0.452          0.457          0.477
z-score robuste (MAD seul)    0.890  0.296          0.349          0.568          0.169
z-score robuste (avec repli)  0.930  0.331          0.342          0.222          0.600
```

Les trois variantes donnent des résultats **très différents** (précision moyenne AP, et part des fraudes de chaque type retrouvées parmi les 180 alertes) :

| z-score (somme des écarts) | AP | rappel type 1 | rappel type 2 |
|---|---:|---:|---:|
| classique | 0,433 | 0,46 | 0,48 |
| robuste, MAD seul | 0,296 | 0,57 | 0,17 |
| robuste, avec repli | 0,331 | 0,22 | 0,60 |

Il ne faut pas en conclure que « robuste » est un défaut, mais que **le choix de l'échelle revient à choisir le poids de chaque variable**. Le MAD seul ignore la rafale de commandes (variable à MAD nul) : il retrouve bien les fraudes de type 1 (compte neuf) mais presque aucune de type 2 (prise de contrôle). Le repli donne à la rafale une échelle étroite (0,38 contre 1 à 1,5 pour les autres variables) : le moindre excès de commandes pèse lourd, la prise de contrôle ressort, et les fraudes de type 1 passent au second plan. Le z-score classique, avec ses échelles larges, équilibre les deux. Ici la contamination (0,8 %) est trop faible pour fausser sensiblement moyenne et écart-type, ce qui explique que la version classique s'en sorte bien. La robustesse est une **assurance** : elle coûte un peu quand il n'y a pas de sinistre, et elle sauve quand il y en a un.

Reste un défaut fondamental : le z-score regarde **chaque variable séparément**. Une commande peut avoir un montant banal, une heure banale et une distance banale, et être pourtant inhabituelle par la **combinaison** (par exemple un petit montant, de nuit, depuis un compte vieux de deux jours). La section suivante prend en compte ces liaisons.

### 6.2.2 La distance de Mahalanobis

Considérons deux variables corrélées, par exemple le montant et le nombre d'articles : les grosses commandes contiennent en général plus d'articles. Un point (grosse commande, peu d'articles) est inhabituel *parce qu'il va à contre-courant de la corrélation*, sans être extrême sur aucune variable. La distance euclidienne ne le voit pas ; la **distance de Mahalanobis** le voit, car elle mesure l'écart en tenant compte de la forme du nuage :

$$d_M^2(x)=(x-\mu)^\top\Sigma^{-1}(x-\mu),$$

où $\mu$ est le vecteur des moyennes et $\Sigma$ la matrice de covariance.

**Un exemple à la main.** Deux variables standardisées (moyenne 0, variance 1) de corrélation $\rho=0{,}9$ : $\Sigma=\begin{pmatrix}1&0{,}9\\0{,}9&1\end{pmatrix}$, d'inverse $\Sigma^{-1}=\dfrac{1}{0{,}19}\begin{pmatrix}1&-0{,}9\\-0{,}9&1\end{pmatrix}$ (le déterminant vaut $1-0{,}81=0{,}19$). Comparons deux points à la même distance euclidienne de l'origine :

- $x=(2,\,2)$, qui suit la corrélation : $d_M^2=\dfrac{1}{0{,}19}\bigl(4-2\times0{,}9\times4+4\bigr)=\dfrac{0{,}8}{0{,}19}\approx\mathbf{4{,}21}$ ;
- $x=(2,\,-2)$, qui va à contre-courant : $d_M^2=\dfrac{1}{0{,}19}\bigl(4+2\times0{,}9\times4+4\bigr)=\dfrac{15{,}2}{0{,}19}=\mathbf{80}$.

Les deux points sont à la distance euclidienne $\sqrt 8$ de l'origine, mais l'un est parfaitement banal et l'autre rarissime. Mahalanobis dit que le premier est dans le nuage et le second hors de portée.

> 📐 **Pourquoi cette formule, et quelle valeur seuil ?** Écrivons la décomposition de Cholesky $\Sigma=LL^\top$ et posons $y=L^{-1}(x-\mu)$. Si $x\sim\mathcal N(\mu,\Sigma)$, alors $y\sim\mathcal N(0,I_p)$ : on a « blanchi » les variables, qui deviennent indépendantes et de variance 1. Or $y^\top y=(x-\mu)^\top L^{-\top}L^{-1}(x-\mu)=(x-\mu)^\top\Sigma^{-1}(x-\mu)=d_M^2$. C'est donc une somme de $p$ carrés de lois normales réduites indépendantes, qui suit une **loi du $\chi^2$ à $p$ degrés de liberté**. Un point est « à rejeter » au niveau 99,9 % si $d_M^2$ dépasse le quantile 0,999 de cette loi : 13,8 pour $p=2$, 29,6 pour $p=10$ (nos dix variables).

Cette théorie suppose des données gaussiennes, ce qui n'est pas le cas de nos commandes (certaines variables sont binaires, d'autres très asymétriques). Sur le jeu de test, **2,3 %** des commandes normales dépassent le seuil de 29,6, alors que la théorie en prévoirait 0,1 %. Le seuil théorique n'est donc **pas calibré** ; nous ne l'utilisons pas pour décider, mais pour **classer** (on garde les 180 commandes de plus grande distance).

```python hide
S2 = np.array([[1, 0.9], [0.9, 1]]); S2i = np.linalg.inv(S2)
for p in [np.array([2., 2.]), np.array([2., -2.])]:
    print("point", p, "| distance euclidienne^2 :", p @ p, "| Mahalanobis^2 :", round(float(p @ S2i @ p), 2))
print("quantiles 0,999 du khi-deux : p=2 ->", round(float(chi2.ppf(0.999, 2)), 1), "; p=10 ->", round(float(chi2.ppf(0.999, 10)), 1))
precision_app = np.linalg.inv(np.cov(Z_app.T))
d2_test = np.einsum("ij,jk,ik->i", Z_test, precision_app, Z_test)
seuil = chi2.ppf(0.999, 10)
evaluer("Mahalanobis", d2_test)
print("commandes normales au-dessus du seuil théorique :", round(100 * float((d2_test[y_test == 0] > seuil).mean()), 1), "% (théorie : 0,1 %) ; fraudes au-dessus :", round(100 * float((d2_test[y_test == 1] > seuil).mean()), 1), "%")
```
<!--sortie-->
```text
point [2. 2.] | distance euclidienne^2 : 8.0 | Mahalanobis^2 : 4.21
point [ 2. -2.] | distance euclidienne^2 : 8.0 | Mahalanobis^2 : 80.0
quantiles 0,999 du khi-deux : p=2 -> 13.8 ; p=10 -> 29.6
commandes normales au-dessus du seuil théorique : 2.3 % (théorie : 0,1 %) ; fraudes au-dessus : 54.1 %
```

**Le masquage, encore.** La moyenne $\mu$ et la covariance $\Sigma$ sont **estimées sur les données**, donc faussées par les anomalies elles-mêmes. Quand elles sont nombreuses ou groupées, elles gonflent $\Sigma$ et leurs distances s'écrasent. L'estimateur à **déterminant de covariance minimal** (MCD, *minimum covariance determinant*) calcule $\mu$ et $\Sigma$ sur le sous-ensemble de $h\approx90\ \%$ des points dont la covariance a le plus petit déterminant : on laisse de côté les points qui étirent le nuage. La figure montre l'effet sur un exemple simulé où 20 % des points forment un groupe lointain.

```python hide
rng_m = np.random.default_rng(5)
normaux = rng_m.multivariate_normal([0, 0], [[1, 0.8], [0.8, 1]], 800)
contamines = rng_m.multivariate_normal([4.5, -2.5], [[0.25, 0], [0, 0.25]], 200)
donnees_m = np.vstack([normaux, contamines])
classique_m = np.cov(donnees_m.T); centre_c = donnees_m.mean(axis=0)
mcd_m = MinCovDet(random_state=0, support_fraction=0.8).fit(donnees_m)
def ellipse(centre, cov, niveau):
    angles = np.linspace(0, 2 * np.pi, 200); L = np.linalg.cholesky(cov)
    return centre[:, None] + np.sqrt(chi2.ppf(niveau, 2)) * L @ np.vstack([np.cos(angles), np.sin(angles)])
d2_c = np.einsum("ij,jk,ik->i", donnees_m - centre_c, np.linalg.inv(classique_m), donnees_m - centre_c)
d2_r = mcd_m.mahalanobis(donnees_m)
seuil2 = chi2.ppf(0.975, 2)
fig, ax = plt.subplots(figsize=(6.3, 4.4))
ax.scatter(*normaux.T, s=7, color=MUET, alpha=0.5, label="800 points normaux")
ax.scatter(*contamines.T, s=7, color=ROUGE, alpha=0.7, label="200 points contaminants")
e1 = ellipse(centre_c, classique_m, 0.975); e2 = ellipse(mcd_m.location_, mcd_m.covariance_, 0.975)
ax.plot(*e1, color=ORANGE, lw=2, label="ellipse classique (97,5 %)"); ax.plot(*e2, color=BLEU, lw=2, label="ellipse robuste, MCD (97,5 %)")
ax.set_xlabel("variable 1"); ax.set_ylabel("variable 2"); ax.legend(frameon=False, fontsize=8, loc="lower left")
plt.tight_layout(); plt.savefig("figures/ch06-masquage.png", dpi=200, bbox_inches="tight"); plt.close()
print("contaminants détectés (au-dessus du seuil du khi-deux à 97,5 %) : classique", round(100 * float((d2_c[800:] > seuil2).mean())), "% ; robuste", round(100 * float((d2_r[800:] > seuil2).mean())), "%")
print("points normaux déclarés anormaux : classique", round(100 * float((d2_c[:800] > seuil2).mean()), 1), "% ; robuste", round(100 * float((d2_r[:800] > seuil2).mean()), 1), "%")
```
<!--sortie-->
```text
contaminants détectés (au-dessus du seuil du khi-deux à 97,5 %) : classique 0 % ; robuste 100 %
points normaux déclarés anormaux : classique 1.8 % ; robuste 1.5 %
```

![Un exemple simulé : 800 points normaux (gris) corrélés et 200 points contaminants (rouge). L'ellipse classique (orange), estimée sur tous les points, est étirée vers les contaminants et les englobe ; l'ellipse robuste MCD (bleue) épouse les points normaux et laisse les contaminants à l'extérieur.](figures/ch06-masquage.png)

L'ellipse classique, étirée par les contaminants, **les englobe** : **aucun** d'entre eux (0 %) ne dépasse le seuil, contre 100 % avec l'estimateur robuste. Sur nos transactions, en revanche, les fraudes ne représentent que 0,8 % des données : il n'y a pas de masquage à craindre, et l'estimateur robuste n'apporte pas grand-chose (précision moyenne de 0,410 contre 0,382 pour la version classique, avec un temps de calcul bien plus long). **La robustesse a un coût, qu'il faut payer seulement si la contamination le justifie** : plus les anomalies sont nombreuses ou groupées dans les données d'apprentissage, plus elle devient nécessaire.

```python hide
t0 = time.time()
mcd = MinCovDet(random_state=0, support_fraction=0.9).fit(Z_app[:15000])
evaluer("Mahalanobis robuste (MCD)", mcd.mahalanobis(Z_test))
print(tableau(["Mahalanobis", "Mahalanobis robuste (MCD)"]).to_string())
```
<!--sortie-->
```text
                             AUC     AP  précision à k  rappel type 1  rappel type 2
Mahalanobis                0.946  0.382          0.356          0.198          0.615
Mahalanobis robuste (MCD)  0.949  0.410          0.404          0.235          0.677
```

### 6.2.3 Les plus proches voisins

La distance de Mahalanobis suppose un seul nuage de forme elliptique. Les vraies données ont souvent plusieurs groupes, des formes courbes, des zones vides. L'idée des **plus proches voisins** s'affranchit de toute forme : *une commande est suspecte si ses voisins sont loin*. Pour chaque commande, on calcule la **distance moyenne à ses $k$ plus proches voisins** dans un échantillon de référence de commandes (supposées en majorité normales) ; plus elle est grande, plus la commande est isolée.

Le nombre de voisins $k$ est un **réglage**. Avec $k=1$, un seul voisin proche suffit à « innocenter » une commande, et le score est bruité ; avec $k$ très grand, on compare la commande à la masse entière des commandes, et l'on perd la finesse. Nous le choisissons **sur le jeu de validation** (jamais sur le test), parmi 1, 3, 5, 10, 30 et 100 :

```python hide-code
grille_knn = [1, 3, 5, 10, 30, 100]
voisins_100 = NearestNeighbors(n_neighbors=100).fit(Z_app[reference])
d_val, _ = voisins_100.kneighbors(Z_val); d_test, _ = voisins_100.kneighbors(Z_test)
ap_knn = {k: (average_precision_score(y_val, d_val[:, :k].mean(axis=1)), average_precision_score(y_test, d_test[:, :k].mean(axis=1))) for k in grille_knn}
k_knn = max(ap_knn, key=lambda k: ap_knn[k][0])
nom_knn = f"Plus proches voisins (k = {k_knn})"
print("   k   AP validation   AP test")
for k, (v_, te_) in ap_knn.items():
    print(f"{k:4d}   {v_:13.3f}   {te_:7.3f}")
print("k choisi sur la validation :", k_knn)
```
<!--sortie-->
```text
   k   AP validation   AP test
   1           0.261     0.303
   3           0.321     0.378
   5           0.350     0.411
  10           0.382     0.444
  30           0.400     0.460
 100           0.399     0.448
k choisi sur la validation : 30
```

```python hide
db_, _ = NearestNeighbors(n_neighbors=k_knn).fit(X_app.values[reference]).kneighbors(X_test.values)
print("AP test avec les variables brutes (non standardisées), k =", k_knn, ":", round(average_precision_score(y_test, db_.mean(axis=1)), 3))
binaires = [list(X.columns).index(c) for c in ["ip_different", "appareil_inconnu"]]
Z_mixte_app, Z_mixte_test = Z_app.copy(), Z_test.copy()
Z_mixte_app[:, binaires] = X_app.values[:, binaires]; Z_mixte_test[:, binaires] = X_test.values[:, binaires]      # variables continues standardisées, binaires laissées en 0/1
dm_, _ = NearestNeighbors(n_neighbors=k_knn).fit(Z_mixte_app[reference]).kneighbors(Z_mixte_test)
print("AP test, variables continues standardisées et binaires en 0/1 :", round(average_precision_score(y_test, dm_.mean(axis=1)), 3))
print("écarts-types des deux variables binaires :", X_app[["ip_different", "appareil_inconnu"]].std().round(2).to_dict(), "| des autres variables : de", round(float(X_app.drop(columns=["ip_different", "appareil_inconnu"]).std().min()), 2), "à", round(float(X_app.drop(columns=["ip_different", "appareil_inconnu"]).std().max()), 2))
```
<!--sortie-->
```text
AP test avec les variables brutes (non standardisées), k = 30 : 0.511
AP test, variables continues standardisées et binaires en 0/1 : 0.513
écarts-types des deux variables binaires : {'ip_different': 0.2, 'appareil_inconnu': 0.3} | des autres variables : de 0.56 à 1.22
```

La précision moyenne sur le jeu de validation passe de 0,261 pour $k=1$ à **0,400 pour $k=30$**, puis plafonne (0,399 pour $k=100$) : nous retenons $k=30$. Le jeu de test donne le même classement des réglages (0,303 pour $k=1$, 0,460 pour $k=30$), ce qui rassure sur le choix.

```python
from sklearn.neighbors import NearestNeighbors

voisins = NearestNeighbors(n_neighbors=k_knn).fit(Z_app[reference])    # 10 000 commandes de référence, variables standardisées
distances, _ = voisins.kneighbors(Z_test)
score_knn = distances.mean(axis=1)                                      # distance moyenne aux k plus proches voisins
```

```python hide
evaluer(nom_knn, score_knn)
print(tableau([nom_knn]).to_string())
```
<!--sortie-->
```text
                                 AUC    AP  précision à k  rappel type 1  rappel type 2
Plus proches voisins (k = 30)  0.959  0.46          0.432          0.259          0.692
```

Quelques points de méthode :

- **Il faut des variables à des échelles comparables** (chapitre 4, section 4.1) : sans cela, la variable d'échelle la plus grande décide seule des distances. La standardisation est le choix par défaut, et nous l'appliquons à tous les détecteurs de ce chapitre pour les comparer sur le même pied. Elle n'est pourtant pas toujours le meilleur : ici nos variables ont déjà été passées au logarithme et ont des échelles voisines, alors que les deux variables binaires (IP étrangère, appareil inconnu) ont un écart-type faible (0,20 et 0,30, contre 0,56 à 1,22 pour les autres) : standardiser les **multiplie par 5 et 3,3** et leur donne un poids très supérieur dans la distance. Avec les variables brutes, la précision moyenne des mêmes voisins monte à **0,511** (contre 0,460) ; en ne standardisant que les variables continues et en laissant les deux variables binaires en 0/1, on obtient **0,513**, ce qui confirme l'explication. L'application 6.3 du cahier reproduit ces calculs.
- **Le coût de calcul.** Comparer chaque commande à toutes les autres est quadratique ; nous utilisons un **échantillon de référence** de 10 000 commandes, ce qui suffit à décrire le comportement normal (l'application 6.3 montre que la précision moyenne passe de 0,37 avec 500 commandes de référence à 0,46 avec 2 000, puis ne progresse plus que lentement, jusqu'à 0,48 avec 20 000). Des structures d'index (arbres, graphes de voisinage approchés) accélèrent le calcul quand la dimension est modeste.

Cette méthode toute simple obtient une précision moyenne de **0,460** sur le jeu de test, et retrouve **69 %** des fraudes de type 2 dans les 180 alertes (contre 26 % de celles de type 1). Elle repose sur très peu d'hypothèses, et c'est l'une des raisons pour lesquelles elle reste un excellent premier essai.

### 6.2.4 Le facteur local d'anomalie (LOF)

Une limite des distances aux voisins : elles supposent que la **densité est la même partout**. Imaginons deux groupes de clients, l'un très concentré (des habitudes d'achat très régulières) et l'autre très étalé. Un point à 1,3 unité du groupe concentré est une **vraie anomalie pour ce groupe**, mais sa distance aux voisins (1,3) est *inférieure* aux distances ordinaires dans le groupe étalé. Une distance globale le noie.

Le **LOF** (*Local Outlier Factor*) compare la densité autour d'un point à celle de ses voisins. Voici les définitions, pour un entier $k$ :

1. la **$k$-distance** $d_k(p)$ : la distance de $p$ à son $k$-ième plus proche voisin ; $N_k(p)$ est l'ensemble de ses $k$ plus proches voisins ;
2. la **distance d'atteignabilité** de $p$ depuis $o$ : $\operatorname{rd}_k(p,o)=\max\{d_k(o),\,d(p,o)\}$ (on ne descend pas en dessous de la $k$-distance du voisin, ce qui lisse les fluctuations) ;
3. la **densité d'atteignabilité locale** : $\operatorname{lrd}_k(p)=\Bigl(\dfrac{1}{|N_k(p)|}\sum_{o\in N_k(p)}\operatorname{rd}_k(p,o)\Bigr)^{-1}$, l'inverse de la distance d'atteignabilité moyenne ;
4. le **facteur d'anomalie** $\mathrm{LOF}_k(p)=\dfrac{1}{|N_k(p)|}\sum_{o\in N_k(p)}\dfrac{\operatorname{lrd}_k(o)}{\operatorname{lrd}_k(p)}$ : le rapport entre la densité des voisins et celle de $p$.

Un $\mathrm{LOF}$ voisin de **1** signifie que $p$ est aussi dense que ses voisins ; un $\mathrm{LOF}$ **nettement supérieur à 1** signifie que $p$ est plus isolé que ses voisins.

**Un exemple à la main : six points sur une droite**, aux abscisses $0;\ 1;\ 3;\ 4{,}4;\ 6{,}1;\ 10$, avec $k=2$. Le tableau donne, pour chaque point, ses deux voisins, sa 2-distance, sa densité et son LOF (calculés ligne à ligne avec les formules ci-dessus, puis vérifiés avec `scikit-learn`) :

```python hide-code
pts = np.array([0, 1, 3, 4.4, 6.1, 10.0]); k = 2
D = np.abs(pts[:, None] - pts[None, :])
ordre = np.argsort(D, axis=1)
kdist = np.array([D[i, ordre[i, k]] for i in range(6)])
voisins_toy = [[int(j) for j in ordre[i, 1:k + 1]] for i in range(6)]
lrd_toy = np.array([1 / np.mean([max(kdist[j], D[i, j]) for j in voisins_toy[i]]) for i in range(6)])
lof_toy = np.array([np.mean([lrd_toy[j] for j in voisins_toy[i]]) / lrd_toy[i] for i in range(6)])
lof_sk = -LocalOutlierFactor(n_neighbors=2).fit(pts.reshape(-1, 1)).negative_outlier_factor_
assert np.allclose(lof_toy, lof_sk)
print("abscisse   voisins (abscisses)   2-distance   densité lrd   LOF")
for i in range(6):
    print(f"{pts[i]:7.1f}   {str([float(pts[j]) for j in voisins_toy[i]]):20s}  {kdist[i]:8.1f}   {lrd_toy[i]:11.4f}   {lof_toy[i]:.3f}")
print("(vérification : mêmes LOF que scikit-learn)")
```
<!--sortie-->
```text
abscisse   voisins (abscisses)   2-distance   densité lrd   LOF
    0.0   [1.0, 3.0]                 3.0        0.4000   1.176
    1.0   [0.0, 3.0]                 2.0        0.4000   1.176
    3.0   [4.4, 1.0]                 2.0        0.5405   0.733
    4.4   [3.0, 6.1]                 1.7        0.3922   1.220
    6.1   [4.4, 3.0]                 3.1        0.4167   1.119
   10.0   [6.1, 4.4]                 5.6        0.2105   1.921
(vérification : mêmes LOF que scikit-learn)
```

Lecture : le point d'abscisse **10**, isolé au bout de la droite, a un LOF de **1,92** ; les points au centre du groupe (3 ; 4,4 ; 6,1) ont des LOF proches de 1 (0,73 ; 1,22 ; 1,12) ; le point 3, entouré, est même plus dense que ses voisins (0,73).

```python hide
fig, ax = plt.subplots(figsize=(8, 2.3))
ax.axhline(0, color=MUET, lw=0.8)
ax.scatter(pts, np.zeros(6), s=300 * lof_toy ** 2, color=BLEU, alpha=0.45, edgecolor=BLEU)
for i_, (x_, l_) in enumerate(zip(pts, lof_toy)): ax.annotate(f"{l_:.2f}".replace(".", ","), (x_, 0), xytext=(x_, 0.17 + 0.1 * (i_ % 2)), ha="center", fontsize=9.5, color="#0b0b0b")
ax.set_ylim(-0.3, 0.5); ax.set_xlim(-1, 11.5); ax.set_yticks([]); ax.set_xlabel("position (le nombre au-dessus de chaque point est son LOF)")
plt.tight_layout(); plt.savefig("figures/ch06-lof-jouet.png", dpi=200, bbox_inches="tight"); plt.close()
```

![Six points sur une droite. La surface de chaque disque est proportionnelle au carré du facteur d'anomalie (LOF) : le point isolé à 10 a le LOF le plus élevé (1,92).](figures/ch06-lof-jouet.png)

Voici maintenant l'avantage du LOF sur la distance aux voisins, sur un exemple simulé : un groupe concentré de 200 points (écart-type 0,25), un groupe étalé de 100 points (écart-type 1,5), et un point **ajouté à 1,3 unité** du groupe concentré (cercle orange).

```python hide
rng_l = np.random.default_rng(3)
dense = rng_l.normal([0, 0], 0.25, (200, 2)); etale = rng_l.normal([6, 0], 1.5, (100, 2))
pts2 = np.vstack([dense, etale, [[1.3, 0.0]]]); idx_out = len(pts2) - 1
d_l, _ = NearestNeighbors(n_neighbors=11).fit(pts2).kneighbors(pts2); knn_l = d_l[:, 1:].mean(axis=1)
lof_l = -LocalOutlierFactor(n_neighbors=10).fit(pts2).negative_outlier_factor_
rang = lambda v: int(len(v) - (v < v[idx_out]).sum())
fig, ax = plt.subplots(1, 2, figsize=(10.5, 3.7), sharex=True, sharey=True)
for a, sc_, titre in [(ax[0], knn_l, f"Distance aux voisins : rang {rang(knn_l)} sur {len(pts2)}"), (ax[1], lof_l, f"LOF : rang {rang(lof_l)} sur {len(pts2)}")]:
    m_ = a.scatter(pts2[:, 0], pts2[:, 1], c=sc_, cmap=style.SEQ, s=14); a.set_title(titre, fontsize=10)
    a.scatter(*pts2[idx_out], s=170, facecolors="none", edgecolors=ORANGE, lw=2)
    a.set_xlabel("variable 1")
ax[0].set_ylabel("variable 2")
plt.tight_layout(); plt.savefig("figures/ch06-lof-densites.png", dpi=200, bbox_inches="tight"); plt.close()
print("point ajouté : distance aux voisins", round(float(knn_l[idx_out]), 2), "(rang", rang(knn_l), ") ; LOF", round(float(lof_l[idx_out]), 2), "(rang", rang(lof_l), ") ; plus grande distance aux voisins du groupe étalé :", round(float(knn_l[200:300].max()), 2))
```
<!--sortie-->
```text
point ajouté : distance aux voisins 0.81 (rang 26 ) ; LOF 5.09 (rang 1 ) ; plus grande distance aux voisins du groupe étalé : 4.08
```

![Deux groupes de densités différentes. Les points sont colorés par la distance moyenne aux voisins (à gauche) ou par le LOF (à droite) ; plus la couleur est foncée, plus le score est élevé. Le point ajouté près du groupe concentré (cercle orange) est noyé parmi les points du groupe étalé à gauche, et il est le plus anormal à droite.](figures/ch06-lof-densites.png)

Selon la distance aux voisins, le point ajouté n'arrive qu'au **26e rang** sur 301 : les points du groupe étalé, naturellement plus éloignés les uns des autres, le dominent (la plus grande distance du groupe étalé dépasse 4). Selon le LOF, il est **premier**, avec un LOF d'environ 5 : relativement à ses voisins, il est cinq fois moins dense.

Le LOF dépend lui aussi d'un réglage $k$, et beaucoup plus que les voisins simples. Nous le choisissons sur le jeu de validation, parmi 10, 30, 100 et 300 :

```python hide-code
grille_lof = [10, 30, 100, 300]
ap_lof = {}
for k in grille_lof:
    modele_lof = LocalOutlierFactor(n_neighbors=k, novelty=True).fit(Z_app[reference])
    ap_lof[k] = (average_precision_score(y_val, -modele_lof.score_samples(Z_val)), average_precision_score(y_test, -modele_lof.score_samples(Z_test)))
k_lof = max(ap_lof, key=lambda k: ap_lof[k][0])
nom_lof = f"LOF (k = {k_lof})"
print("   k   AP validation   AP test")
for k, (v_, te_) in ap_lof.items():
    print(f"{k:4d}   {v_:13.3f}   {te_:7.3f}")
print("k choisi sur la validation :", k_lof)
```
<!--sortie-->
```text
   k   AP validation   AP test
  10           0.114     0.113
  30           0.243     0.306
 100           0.408     0.471
 300           0.433     0.492
k choisi sur la validation : 300
```

La précision moyenne sur la validation passe de **0,114** pour $k=10$ à **0,433** pour $k=300$ : un LOF réglé à la légère est un très mauvais détecteur, un LOF bien réglé est l'un des meilleurs. La raison est que la densité « locale » estimée avec peu de voisins est très bruitée ; avec 300 voisins, elle devient stable. Le meilleur $k$ est en bout de grille : une grille plus large aurait peut-être fait mieux, ce que nous n'avons pas exploré.

```python
from sklearn.neighbors import LocalOutlierFactor

lof = LocalOutlierFactor(n_neighbors=k_lof, novelty=True).fit(Z_app[reference])
score_lof = -lof.score_samples(Z_test)               # novelty=True : on score de nouveaux points
```

```python hide
evaluer(nom_lof, score_lof)
print(tableau([nom_lof]).to_string())
```
<!--sortie-->
```text
                 AUC     AP  précision à k  rappel type 1  rappel type 2
LOF (k = 300)  0.944  0.492          0.493          0.519          0.492
```

Sur nos transactions, le LOF réglé à $k=300$ obtient une précision moyenne de **0,492** sur le jeu de test, mieux que les voisins simples (0,460) ; il retrouve **52 %** des fraudes de type 1 et **49 %** de celles de type 2. Le LOF repère les commandes isolées *par rapport à leur voisinage*, ce qui convient à des fraudes qui s'éloignent localement des habitudes sans être extrêmes dans l'absolu.

### 6.2.5 Ce que voient ces méthodes, et ce qu'elles ratent

Toutes les méthodes de cette section sont ajustées sans étiquette, et toutes ont reçu le même jeu d'apprentissage. Le tableau résume leurs performances sur le jeu de test.

```python hide-code
print(tableau(["z-score classique", "z-score robuste (avec repli)", "Mahalanobis", "Mahalanobis robuste (MCD)", nom_knn, nom_lof]).to_string())
```
<!--sortie-->
```text
                                 AUC     AP  précision à k  rappel type 1  rappel type 2
z-score classique              0.939  0.433          0.452          0.457          0.477
z-score robuste (avec repli)   0.930  0.331          0.342          0.222          0.600
Mahalanobis                    0.946  0.382          0.356          0.198          0.615
Mahalanobis robuste (MCD)      0.949  0.410          0.404          0.235          0.677
Plus proches voisins (k = 30)  0.959  0.460          0.432          0.259          0.692
LOF (k = 300)                  0.944  0.492          0.493          0.519          0.492
```

Deux enseignements, que la section 6.4.5 reprendra avec les méthodes suivantes :

1. **Chaque méthode définit autrement ce qui est « normal »**, donc trouve d'autres fraudes. Mahalanobis, les voisins (avec 69 %) retrouvent surtout le type 2 et peu le type 1 (de 20 à 26 %) ; le z-score classique les équilibre (0,46 et 0,48) ; et le LOF réglé à $k=300$ retrouve les deux types à parts à peu près égales (52 % et 49 %). Il n'existe pas de « meilleure méthode » dans l'absolu.
2. **Le réglage compte autant que la méthode.** Le LOF passe d'une précision moyenne de 0,11 (avec 10 voisins) à 0,49 (avec 300) ; les voisins simples varient de 0,30 à 0,46 selon $k$. Aucun réglage n'est universel, et sans étiquette on ne peut pas savoir lequel convient : c'est pourquoi on garde un **jeu de validation étiqueté**, même petit, pour régler, et un jeu de test pour juger.

> ✅ **À retenir.**
> - Le **z-score** juge chaque variable seule ; moyenne et écart-type sont faussés par les anomalies (**masquage**) : médiane et **MAD** (constante 1,4826) sont robustes. Attention au **MAD nul** (plus de la moitié de valeurs identiques).
> - La **distance de Mahalanobis** $d_M^2=(x-\mu)^\top\Sigma^{-1}(x-\mu)$ tient compte des corrélations ; sous hypothèse gaussienne elle suit un $\chi^2_p$. La version robuste (MCD) n'est utile que si la contamination est importante.
> - La **distance aux $k$ plus proches voisins** ne suppose aucune forme ; il faut des variables à des échelles comparables et un $k$ **choisi sur un jeu de validation**.
> - Le **LOF** compare la densité d'un point à celle de ses voisins : il détecte les anomalies **locales** quand les densités varient ; il est **très sensible à $k$** (précision moyenne de 0,11 à 0,49 selon le réglage).
> - Aucune de ces méthodes n'est la meilleure partout ; chacune a ses fraudes de prédilection.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.2 et 6.3, exercices 6.5 à 6.7.
