## 1.2 Distributions et courbe normale

Dire qu'un panier moyen est de 100 € ne dit pas **quelle proportion** de clients dépense plus de 200 €. Pour répondre à ce genre de question, il faut connaître la **forme** de la répartition des valeurs, c'est-à-dire une **distribution**. Cette section présente les quelques distributions qui suffisent à décrire la plupart des phénomènes que l'on rencontre en entreprise : des **comptages** (retours, commandes), des **mesures** (âges) et des **montants**. Elle apprend aussi à reconnaître quand aucune de ces lois ne convient, ce qui arrive plus souvent qu'on ne le croit.

### 1.2.1 Qu'est-ce qu'une distribution ?

Une **distribution** décrit **à quelle fréquence** chaque valeur (ou chaque intervalle de valeurs) apparaît. On en distingue deux grandes familles :

- une variable **discrète** ne prend que des valeurs isolées (le nombre de lignes d'une commande : 1, 2, 3…) ; sa distribution est la liste des probabilités $P(X=k)$ ;
- une variable **continue** prend toutes les valeurs d'un intervalle (le panier en euros, une température) ; on ne parle plus de la probabilité d'une valeur exacte (nulle) mais de la probabilité de tomber **dans un intervalle**, qui est l'**aire** sous une courbe appelée **densité**.

L'histogramme est l'image **observée** d'une distribution ; une loi théorique (binomiale, de Poisson, normale…) en est un **modèle**, c'est-à-dire une formule à un ou deux paramètres qui reproduit la forme. Le modèle est pratique : il permet de calculer des probabilités qu'on ne peut pas lire directement sur les données (la probabilité d'un événement rare, par exemple), à condition que **ses hypothèses tiennent**.

La plus simple des lois est la loi **uniforme** : toutes les valeurs ont la même probabilité. La minute à laquelle une commande est passée (de 0 à 59) en est un bon exemple : rien ne distingue 17 heures 03 de 17 heures 48. Les commandes tombent dans les quinze premières minutes de l'heure avec une fréquence de 25,0 %, très près des 25 % que prédit l'uniforme ($15/60$).

```python hide
minutes = cmd["heure"].str[3:].astype(int)
NUM("part_min15", (minutes < 15).mean() * 100)
NUM("min_freq", minutes.value_counts(normalize=True).min() * 100)
NUM("max_freq", minutes.value_counts(normalize=True).max() * 100)
```
<!--sortie-->
```text
NUM part_min15 24.97046297568347
NUM min_freq 1.5496634153043
NUM max_freq 1.8216788020332462
```

### 1.2.2 Compter : les lois binomiale et de Poisson

#### La loi binomiale : combien de retours sur $n$ lignes ?

La gérante veut savoir si un lot de **50 lignes vendues sur le Site** peut contenir 10 retours ou plus, ce qui serait un signal d'alerte. Le taux de retour du Site est de 8,98 %. Chaque ligne est retournée ou non (deux issues), indépendamment des autres, avec la même probabilité $p$ : c'est le schéma de la loi **binomiale** de paramètres $n=50$ et $p=0{,}0898$.

La probabilité d'obtenir exactement $k$ retours est

$$P(K=k)=\binom{n}{k}\,p^k\,(1-p)^{n-k},\qquad E(K)=np,\qquad \text{Var}(K)=np(1-p).$$

Le coefficient $\binom nk=\frac{n!}{k!\,(n-k)!}$ compte les façons de choisir quelles lignes sont retournées. Calculons à la main les deux cas les plus simples : **aucun retour** ($k=0$), $P(K=0)=(1-p)^{50}=0{,}9102^{50}$, soit environ 0,0091 ou 0,9 % ; et le nombre de retours **attendu**, $np=50\times0{,}0898=4{,}49$, avec un écart-type $\sqrt{np(1-p)}$ de 2,02. Obtenir 10 retours ou plus, c'est donc s'éloigner de la moyenne de plus de deux écarts-types : un événement possible mais rare.

```python
from scipy.stats import binom
print("P(0 retour) :", round(binom.pmf(0, 50, 0.0898), 4))
print("P(10 retours ou plus) :", round(binom.sf(9, 50, 0.0898), 4))      # sf(9) = P(K > 9)
```
<!--sortie-->
```text
P(0 retour) : 0.0091
P(10 retours ou plus) : 0.0123
```

Pour **vérifier** que le modèle décrit bien les données, on tire 20 000 fois 50 lignes du Site au hasard dans les données réelles et l'on compte les retours. La figure de gauche ci-dessous compare les fréquences observées aux probabilités de la loi : elles se superposent presque parfaitement. La fréquence observée de « 10 retours ou plus » est de 1,24 % pour 1,23 % attendus.

```python hide
p_site = ls.loc["Site", "r"] / ls.loc["Site", "n"]
site = lig[lig["canal"] == "Site"]["retournee"].values
rng = np.random.default_rng(101)
tirages = np.array([rng.choice(site, 50, replace=False).sum() for _ in range(20000)])
ks = np.arange(0, 17)
emp = np.array([(tirages == k).mean() for k in ks])
theo = stats.binom.pmf(ks, 50, p_site)
NUM("t_site", p_site * 100)
NUM("p0", stats.binom.pmf(0, 50, 0.0898)); NUM("p0_pct", stats.binom.pmf(0, 50, 0.0898) * 100)
NUM("sd_bin", np.sqrt(50 * 0.0898 * (1 - 0.0898)))
NUM("emp_10", (tirages >= 10).mean() * 100); NUM("theo_10", stats.binom.sf(9, 50, 0.0898) * 100)
assert abs(p_site - 0.0898) < 5e-5 and abs(50 * p_site - 4.49) < 0.01
assert abs((tirages >= 10).mean() - stats.binom.sf(9, 50, p_site)) < 0.004
```
<!--sortie-->
```text
NUM t_site 8.981732070365359
NUM p0 0.009054022272764141
NUM p0_pct 0.9054022272764142
NUM sd_bin 2.0215830430630346
NUM emp_10 1.24
NUM theo_10 1.2337798822020984
```

#### La loi de Poisson : combien d'articles de plus dans un panier ?

Quand on **compte des événements dans un intervalle** (une journée, une commande, une heure) et que ces événements surviennent **indépendamment** et à un rythme moyen constant $\lambda$, on obtient la loi de **Poisson** :

$$P(N=k)=e^{-\lambda}\,\frac{\lambda^k}{k!},\qquad E(N)=\text{Var}(N)=\lambda.$$

Sa signature est que **la variance est égale à la moyenne**. Vérifions sur un cas simple : le nombre d'articles **en plus du premier** dans une commande (nombre de lignes moins un). Sa moyenne vaut 1,31 et sa variance 1,31 : deux nombres voisins, ce qui est bon signe. À la main, avec $\lambda=1{,}3$ : $P(N=0)=e^{-1{,}3}\approx0{,}273$, $P(N=1)=1{,}3\,e^{-1{,}3}\approx0{,}354$, $P(N=2)=\frac{1{,}3^2}{2}e^{-1{,}3}\approx0{,}230$. La figure de droite compare fréquences observées et loi de Poisson : l'accord est excellent.

```python hide
nl = lig.groupby("id_commande").size()
sup = (nl - 1).values
NUM("lam_lignes", sup.mean()); NUM("var_lignes", sup.var(ddof=1))
lam = sup.mean()
kk = np.arange(0, 8)
emp_p = np.array([(sup == k).mean() for k in kk])
theo_p = stats.poisson.pmf(kk, lam)
assert abs(np.exp(-1.3) - 0.2725) < 1e-3 and abs(1.3 * np.exp(-1.3) - 0.3543) < 1e-3 and abs(1.3 ** 2 / 2 * np.exp(-1.3) - 0.2303) < 1e-3
fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.5))
ax = axs[0]
ax.bar(ks, emp * 100, color=BLEU, alpha=0.75, width=0.8, label="observé (20 000 tirages)")
ax.plot(ks, theo * 100, "o", color=ORANGE, ms=5, label="loi binomiale (n = 50, p = 8,98 %)")
ax.set_ylim(0, 25); ax.set_xticks(range(0, 17, 2))
ax.set_xlabel("nombre de retours sur 50 lignes du Site"); ax.set_ylabel("fréquence (%)"); ax.set_title("Binomiale : les retours")
ax.legend(fontsize=8, loc="upper right")
ax = axs[1]
ax.bar(kk, emp_p * 100, color=BLEU, alpha=0.75, width=0.8, label="observé (toutes les commandes)")
ax.plot(kk, theo_p * 100, "o", color=ORANGE, ms=5, label=f"loi de Poisson (λ = {lam:.2f})".replace(".", ","))
ax.set_ylim(0, 44)
ax.set_xlabel("articles en plus du premier dans une commande"); ax.set_ylabel("fréquence (%)"); ax.set_title("Poisson : les articles supplémentaires")
ax.legend(fontsize=8, loc="upper right")
style.save(fig, "ch01-comptage.png")
```
<!--sortie-->
```text
NUM lam_lignes 1.3053990932820443
NUM var_lignes 1.313416746666211
figure : ch01-comptage.png
```

![Deux lois de comptage face aux données de la boutique. À gauche : le nombre de retours dans un lot de 50 lignes du Site (barres bleues : 20 000 tirages dans les données ; points orange : loi binomiale). À droite : le nombre d'articles supplémentaires dans une commande (barres : fréquences observées ; points : loi de Poisson de même moyenne).](figures/ch01-comptage.png)

#### Quand la loi de Poisson ne convient plus

Appliquons maintenant la même loi à une quantité voisine, le **nombre de commandes par jour**. La moyenne est de 33,2 commandes, mais la variance vaut 169 : **5,1 fois** la moyenne. Ce n'est plus du Poisson. La raison est que les journées ne sont pas comparables : un samedi de décembre en période de soldes n'a rien à voir avec un mardi d'août. La loi de Poisson suppose un **rythme constant** ; ici, le rythme change tous les jours, et mélanger des rythmes différents **gonfle la variance**.

Si l'on se restreint à des journées **comparables** (les mardis hors promotion de septembre et octobre, sur trois ans), le rapport variance/moyenne tombe à 1,3, beaucoup plus près de 1 (il reste un peu au-dessus, car l'activité croît d'une année sur l'autre ; avec 27 journées seulement, l'estimation est elle-même bruitée). La leçon est générale : **un modèle n'est valable que dans les conditions où ses hypothèses tiennent**, et la comparaison variance/moyenne est un test rapide pour la loi de Poisson.

```python hide
j = jours
NUM("moy_jour", j["nb_commandes"].mean()); NUM("var_jour", j["nb_commandes"].var(ddof=1)); NUM("ratio_jour", j["nb_commandes"].var(ddof=1) / j["nb_commandes"].mean())
h = j[(j["jour_sem"] == 1) & (j["mois"].isin([9, 10])) & (j["promo_active"] == 0)]
NUM("ratio_mardi", h["nb_commandes"].var(ddof=1) / h["nb_commandes"].mean()); NUM("n_mardi", len(h))
```
<!--sortie-->
```text
NUM moy_jour 33.207116788321166
NUM var_jour 169.27852464753525
NUM ratio_jour 5.097658002849255
NUM ratio_mardi 1.3492955064737238
NUM n_mardi 27
```

### 1.2.3 La courbe normale

La loi **normale** (ou de Laplace-Gauss, la « courbe en cloche ») est la plus célèbre. Elle est caractérisée par deux paramètres : la **moyenne** $\mu$ (le centre de la cloche) et l'**écart-type** $\sigma$ (sa largeur). Sa densité est

$$f(x)=\frac{1}{\sigma\sqrt{2\pi}}\exp\!\left(-\frac{(x-\mu)^2}{2\sigma^2}\right).$$

Il n'est pas nécessaire de retenir la formule. Il faut retenir **trois propriétés** : la courbe est **symétrique** autour de $\mu$ ; elle est **entièrement déterminée** par $\mu$ et $\sigma$ ; et elle obéit à la règle **68-95-99,7** :

- environ **68 %** des valeurs se trouvent à moins de **1 écart-type** de la moyenne ;
- environ **95 %** à moins de **2 écarts-types** ;
- environ **99,7 %** à moins de **3 écarts-types**.

L'âge des clients de la boutique en offre un exemple. Sur les 6 000 clients, l'âge moyen est de 43,3 ans et l'écart-type de 13,7 ans. La règle prédit 68 % des clients entre 30 et 57 ans ; on observe **66,3 %**. À deux écarts-types (de 16 à 71 ans) on observe **97,4 %** (prédit : 95 %), et à trois écarts-types **99,8 %** (prédit : 99,7 %). L'accord est bon : l'âge est une grandeur à peu près normale. (Le pic isolé à 18 ans, visible sur la figure, est un artefact de la simulation : les clients « plus jeunes » ont été ramenés à 18 ans. Dans des données réelles, un tel pic signale une **coupure** ou une valeur par défaut, et mérite une vérification.)

```python hide
age = 2025 - cli["annee_naissance"]
m_a, s_a = age.mean(), age.std()
NUM("age_moy", m_a); NUM("age_sd", s_a)
for k in (1, 2, 3):
    NUM(f"p{k}", ((age - m_a).abs() <= k * s_a).mean() * 100)
    NUM(f"b{k}_bas", m_a - k * s_a); NUM(f"b{k}_haut", m_a + k * s_a)
z70 = (70 - m_a) / s_a
NUM("z70", z70); NUM("cent70", stats.norm.cdf(z70) * 100); NUM("emp70", (age >= 70).mean() * 100); NUM("th70", stats.norm.sf(z70) * 100)
NUM("age_skew", age.skew())
fig, ax = plt.subplots(figsize=(8.6, 3.5))
xs = np.linspace(m_a - 4 * s_a, m_a + 4 * s_a, 400)
dens = stats.norm.pdf(xs, m_a, s_a)
for k, col, al in ((3, "#cde2fb", 0.55), (2, "#86b6ef", 0.55), (1, BLEU, 0.45)):
    msk = np.abs(xs - m_a) <= k * s_a
    ax.fill_between(xs[msk], dens[msk], color=col, alpha=al, lw=0)
ax.hist(age, bins=np.arange(16, 90, 2), density=True, color="none", edgecolor=ENCRE2, lw=0.7)
ax.plot(xs, dens, color=ORANGE, lw=2)
for k in (-3, -2, -1, 1, 2, 3):
    ax.axvline(m_a + k * s_a, color=MUET, lw=0.7, ls=":")
    ax.text(m_a + k * s_a, 0.0335, f"{'+' if k > 0 else '−'}{abs(k)} σ", ha="center", fontsize=8.5, color=ENCRE2)
ax.set_ylim(0, 0.036)
ax.set_xlim(0, 95); ax.set_xlabel("âge des clients (ans)"); ax.set_ylabel("densité"); ax.set_title("L'âge des clients et la courbe normale")
style.save(fig, "ch01-normale.png")
```
<!--sortie-->
```text
NUM age_moy 43.2925
NUM age_sd 13.668482541446618
NUM p1 66.26666666666667
NUM b1_bas 29.62401745855338
NUM b1_haut 56.96098254144661
NUM p2 97.39999999999999
NUM b2_bas 15.95553491710676
NUM b2_haut 70.62946508289323
NUM p3 99.83333333333333
NUM b3_bas 2.2870523756601457
NUM b3_haut 84.29794762433986
NUM z70 1.9539476982185462
NUM cent70 97.46462985804442
NUM emp70 3.1
NUM th70 2.53537014195558
NUM age_skew 0.1600573776941422
figure : ch01-normale.png
```

![L'âge des clients (histogramme, contour gris) et la courbe normale de même moyenne et de même écart-type (orange). Les trois zones bleues correspondent à ±1, ±2 et ±3 écarts-types : elles contiennent environ 68 %, 95 % et 99,7 % des valeurs.](figures/ch01-normale.png)

#### Le score $z$ : mesurer en écarts-types

Comment dire qu'une cliente de 70 ans est « très âgée » pour la clientèle ? En la situant **par rapport à la moyenne, en nombre d'écarts-types**. C'est le **score $z$** :

$$z=\frac{x-\mu}{\sigma}.$$

Pour 70 ans : z = (70 − 43,3) / 13,7 ≈ 1,95.

Un score de 1,95 signifie que la cliente se situe à presque deux écarts-types **au-dessus** de la moyenne. Les tables de la loi normale (ou la fonction `LOI.NORMALE.STANDARD.N` d'Excel, avec l'option cumulative à `VRAI` : à vérifier dans votre version) donnent la probabilité d'être en dessous d'un score $z$ : pour $z=1{,}95$, **97,4 %** (c'est le **centile** de la cliente). Environ **2,5 %** des clients devraient donc avoir 70 ans ou plus si l'âge était exactement normal ; on en observe **3,1 %**. Le score $z$ a un avantage précieux : il permet de **comparer des grandeurs d'unités différentes** (un panier de 250 € et un âge de 70 ans) en les ramenant à la même échelle.

> 💡 **Pourquoi la normale est-elle partout ?** Quand on **additionne** (ou moyenne) beaucoup de petites influences indépendantes, le résultat est approximativement normal, même si chaque influence ne l'est pas. C'est ce qu'établit le **théorème central limite**, que la section 1.3 illustre. Voilà pourquoi la taille ou l'âge d'une population suivent souvent une cloche, et pourquoi les **moyennes** d'échantillons sont presque toujours normales, quelle que soit la forme des données d'origine.

### 1.2.4 Quand la normale ne convient pas

Les montants des paniers, eux, ne sont **pas** normaux : nous l'avons vu, leur histogramme est étiré à droite (asymétrie 1,85). Un modèle normal ajusté à ces paniers prévoirait des paniers **négatifs**. Comment le **vérifier** autrement qu'« à l'œil » ? Avec un **diagramme quantile-quantile** (*Q-Q plot*). On compare chaque quantile des données au quantile correspondant de la loi normale : si les données sont normales, les points s'alignent sur une droite ; une courbure révèle l'écart.

```python hide
xv = cmd["panier"].values
fig, axs = plt.subplots(1, 2, figsize=(9.2, 3.6))
for ax, vals, titre, xl in ((axs[0], xv, "Paniers (€)", "panier observé (€)"), (axs[1], np.log(xv), "Logarithme des paniers", "log du panier observé")):
    (osm, osr), (pente, ordo, r) = stats.probplot(vals, dist="norm")
    ax.plot(osm, osr, ".", color=BLEU, ms=2.5, alpha=0.6)
    ax.plot(osm, pente * osm + ordo, color=ORANGE, lw=1.6)
    ax.set_xlabel("quantile de la loi normale"); ax.set_ylabel(xl); ax.set_title(titre)
    ax.text(0.04, 0.9, f"corrélation = {r:.3f}".replace(".", ","), transform=ax.transAxes, fontsize=9)
style.save(fig, "ch01-qq.png")
r_pan = stats.probplot(xv, dist="norm")[1][2]; r_log = stats.probplot(np.log(xv), dist="norm")[1][2]
NUM("qq_pan", r_pan); NUM("qq_log", r_log)
NUM("skew_log", pd.Series(np.log(xv)).skew())
NUM("part_neg", stats.norm.cdf(0, xv.mean(), xv.std()) * 100)
```
<!--sortie-->
```text
figure : ch01-qq.png
NUM qq_pan 0.925057673614618
NUM qq_log 0.9858774621193379
NUM skew_log -0.711080543104352
NUM part_neg 10.68714641319864
```

![Diagrammes quantile-quantile. À gauche, les paniers : les points s'écartent nettement de la droite (la traîne droite est bien plus longue que celle d'une normale). À droite, leur logarithme : l'alignement est bien meilleur, mais pas parfait (les petits paniers sont plus rares que ne le prévoit une normale).](figures/ch01-qq.png)

Les paniers forment une courbe très nette (corrélation avec la droite de 0,925) ; leur **logarithme** s'aligne bien mieux (0,986). Quand le logarithme d'une variable est à peu près normal, la variable est dite **log-normale** : c'est le cas typique des montants, des revenus, des tailles d'entreprises, qui résultent de **multiplications** d'effets (un prix multiplié par une quantité, multiplié par une remise…) plutôt que d'additions. Le modèle normal prévoirait 11 % de paniers négatifs, ce qui est absurde ; le modèle log-normal ne le peut pas. Le diagramme montre pourtant que la log-normale n'est elle non plus **qu'une approximation** (asymétrie résiduelle de -0,71) : les paniers très petits sont moins nombreux que le modèle ne le prévoit.

Que faire d'une variable qui n'est pas normale ? Trois attitudes sont courantes. On peut **transformer** (le logarithme) pour se ramener à une cloche. On peut **changer de résumé** : médiane et centiles au lieu de moyenne et écart-type, ce qui ne suppose aucune forme. Ou l'on peut **ne rien supposer** et laisser les données parler (simulation, méthodes dites « non paramétriques »). L'important est de **ne pas appliquer par réflexe** une règle 68-95-99,7 à une variable qui n'est pas en cloche.

#### Quelle loi pour quel phénomène ?

| Phénomène de la boutique | Loi plausible | Paramètres | À vérifier |
|---|---|---|---|
| Minute d'une commande | uniforme | aucun | fréquences égales |
| Retours parmi $n$ lignes | binomiale | $n$, $p$ (9,0 % pour le Site) | indépendance, $p$ constant |
| Articles supplémentaires par commande | Poisson | $\lambda$ (1,3) | variance ≈ moyenne |
| Commandes par jour | Poisson **par tranche homogène** | $\lambda$ qui varie | variance ≈ moyenne dans la tranche |
| Âge des clients | normale | $\mu$ (43 ans), $\sigma$ (14 ans) | Q-Q plot, symétrie |
| Panier d'une commande | asymétrique ; log-normale en première approximation | moyenne et écart-type du logarithme | Q-Q plot du logarithme |

> ✅ **À retenir.** (1) Une distribution est un modèle de la forme des données ; elle permet de calculer des probabilités, **si ses hypothèses tiennent**. (2) Binomiale pour compter des succès sur $n$ essais, Poisson pour compter des événements dans un intervalle (variance = moyenne). (3) La normale est décrite par $\mu$ et $\sigma$ ; le score $z$ mesure en écarts-types ; la règle 68-95-99,7 n'a de sens que pour une variable en cloche. (4) Les montants sont asymétriques : prenez le logarithme, ou résumez par la médiane et les centiles ; vérifiez par un Q-Q plot.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.4, exercices 1.6 et 1.7.
