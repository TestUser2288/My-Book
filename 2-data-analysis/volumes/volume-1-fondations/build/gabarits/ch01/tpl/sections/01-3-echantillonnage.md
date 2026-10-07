## 1.3 Échantillonnage et erreur d'échantillonnage

Presque toute analyse repose sur un **échantillon** : une partie des clients, des commandes, des réponses à une enquête, dont on veut tirer une conclusion sur **l'ensemble**. La gérante demande : « Vous avez regardé 100 commandes et trouvé un panier moyen de 98 € : est-ce que le vrai chiffre peut être de 110 € ? » Pour répondre, il faut savoir de combien un chiffre calculé sur une partie peut s'écarter du chiffre « vrai ». C'est le sujet de cette section : **quantifier l'erreur due au hasard du tirage**, puis reconnaître les erreurs que le hasard n'explique pas.

### 1.3.1 Population, échantillon, paramètre, statistique

Quatre mots suffisent pour tout ce qui suit.

- La **population** est l'ensemble sur lequel on veut conclure (toutes les commandes de 2025, tous les clients de la boutique).
- L'**échantillon** est la partie effectivement observée, de taille $n$.
- Un **paramètre** est une caractéristique de la population (la moyenne $\mu$ des paniers de 2025), fixe mais généralement inconnue.
- Une **statistique** est une caractéristique de l'échantillon (la moyenne $\bar x$ des 100 paniers observés), connue, mais **qui change d'un échantillon à l'autre**.

On utilise la statistique $\bar x$ pour **estimer** le paramètre $\mu$. L'**erreur d'échantillonnage** est l'écart $\bar x-\mu$ dû uniquement au fait que l'on n'a pas vu toute la population : un autre tirage de 100 commandes aurait donné un autre $\bar x$.

Cette boutique a un luxe que vous aurez rarement : les {{n25:,.0f}} commandes de 2025 sont toutes dans le fichier, et leur panier moyen vaut **{{mu25:.2f}} €**. Ici, pour une question sur 2025, il n'y a donc pas d'échantillonnage à faire. Nous allons pourtant **faire comme si** nous ne pouvions voir que 100 commandes, parce que c'est le meilleur moyen de voir la méthode fonctionner : on connaît la réponse exacte, on peut juger l'estimation. Deux remarques de fond avant de commencer :

- **Un recensement n'est pas la fin de l'incertitude.** Les commandes de 2025 sont une population complète pour décrire 2025 ; elles sont **un échantillon** de ce que sera 2026. Dès que l'on généralise à l'avenir (« le panier moyen sera de… »), on est de nouveau en situation d'échantillonnage.
- **« Population » est un choix de l'analyste**, pas une donnée : si la question porte sur les clients actifs, les clients inscrits depuis dix ans ne font pas partie de la population.

### 1.3.2 L'erreur d'échantillonnage en action

Simulons le travail de l'analyste qui ne voit que 100 commandes. On tire au hasard 100 commandes de 2025, on calcule leur moyenne, et l'on **recommence 1 000 fois**.

```python
import numpy as np
rng = np.random.default_rng(1)
ids25 = commandes.loc[commandes["date_commande"] >= "2025-01-01", "id_commande"]
pop = panier.loc[ids25].values                      # la population : tous les paniers de 2025
moyennes = [rng.choice(pop, 100, replace=False).mean() for _ in range(1000)]
print("moyenne des moyennes :", round(np.mean(moyennes), 2), "| vraie moyenne :", round(pop.mean(), 2))
print("écart-type des moyennes :", round(np.std(moyennes), 2), "| σ/√n :", round(pop.std() / 10, 2))
```

```python hide
mu25 = pop.mean(); sig25 = pop.std()
NUM("mu25", mu25); NUM("n25", len(pop)); NUM("sig25", sig25)
NUM("m_moy", np.mean(moyennes)); NUM("sd_moy", np.std(moyennes)); NUM("se100", sig25 / 10)
NUM("min_moy", np.min(moyennes)); NUM("max_moy", np.max(moyennes))
NUM("n_hors", np.mean(np.abs(np.array(moyennes) - mu25) > 10) * 100)
```

Trois constats. D'abord, **les 1 000 moyennes sont toutes différentes** : de {{min_moy:.1f}} € à {{max_moy:.1f}} €, alors que la vraie moyenne est {{mu25:.1f}} €. Ensuite, elles sont **centrées sur la vraie valeur** (leur moyenne vaut {{m_moy:.2f}} €) : tirer au hasard ne crée pas de biais. Enfin, leur dispersion, l'**erreur type** (*standard error*), vaut {{sd_moy:.2f}} € : elle est très proche de $\sigma/\sqrt n$ ({{se100:.2f}} €). C'est la formule centrale de cette section :

$$\text{erreur type de }\bar x=\frac{\sigma}{\sqrt n}.$$

L'erreur type dit **de combien la moyenne d'un échantillon s'écarte typiquement de la vraie moyenne**. Elle décroît avec la **racine** de $n$ : pour diviser l'erreur par 2, il faut **quadrupler** l'échantillon ; pour la diviser par 10, il faut le multiplier par 100. Les rendements décroissent vite. Voici l'erreur observée et l'erreur prévue pour quatre tailles d'échantillon :

| Taille $n$ | Erreur type observée (1 000 tirages) | $\sigma/\sqrt n$ |
|---:|---:|---:|
| 10 | {{se_obs_10:.1f}} € | {{se_th_10:.1f}} € |
| 30 | {{se_obs_30:.1f}} € | {{se_th_30:.1f}} € |
| 100 | {{se_obs_100:.1f}} € | {{se_th_100:.1f}} € |
| 400 | {{se_obs_400:.1f}} € | {{se_th_400:.1f}} € |

```python hide
rng_t = np.random.default_rng(2)
for n in (10, 30, 100, 400):
    mm = [rng_t.choice(pop, n, replace=False).mean() for _ in range(1000)]
    NUM(f"se_obs_{n}", np.std(mm)); NUM(f"se_th_{n}", sig25 / np.sqrt(n))
```

> 💡 **La loi des grands nombres.** Quand $n$ augmente, $\bar x$ se rapproche de $\mu$. C'est ce que dit l'erreur type : elle tend vers zéro. En pratique : la moyenne de 10 commandes tirées au hasard vaut {{lgn_10:.1f}} €, celle de 100 commandes {{lgn_100:.1f}} €, celle de 1 000 commandes {{lgn_1000:.1f}} € et celle des {{n25:,.0f}} commandes {{mu25:.1f}} €. Mais la loi ne dit pas **à quelle vitesse** : c'est le rôle de l'erreur type. Et elle suppose un **tirage au hasard** : les 1 000 *premières* commandes de l'année (en janvier, pendant les soldes) ont un panier moyen de {{lgn_chrono:.1f}} €, loin de la vérité. Ce n'est pas un échantillon, c'est un morceau de calendrier.

```python hide
rng_l = np.random.default_rng(4)
ordre_alea = rng_l.permutation(pop)
for n in (10, 100, 1000):
    NUM(f"lgn_{n}", ordre_alea[:n].mean())
ordre25 = cmd[cmd["annee"] == 2025].sort_values(["date_commande", "id_commande"])["panier"].values
NUM("lgn_chrono", ordre25[:1000].mean())
```

#### La forme de la distribution des moyennes : le théorème central limite

Les paniers eux-mêmes ont une distribution très asymétrique. Mais regardons la distribution des **moyennes** de plusieurs paniers.

```python hide
rng_c = np.random.default_rng(3)
fig, axs = plt.subplots(1, 4, figsize=(11.5, 2.9), sharey=False)
ax = axs[0]
ax.hist(pop, bins=np.arange(0, 701, 20), color=BLEU, alpha=0.75, edgecolor="white", lw=0.3, density=True)
ax.set_xlim(0, 700); ax.set_title("Un panier (population)", fontsize=10); ax.set_xlabel("€"); ax.set_yticks([])
for ax, n in zip(axs[1:], (5, 30, 200)):
    mm = np.array([rng_c.choice(pop, n, replace=False).mean() for _ in range(2000)])
    ax.hist(mm, bins=30, color=BLEU, alpha=0.75, edgecolor="white", lw=0.3, density=True)
    xs = np.linspace(mm.min(), mm.max(), 200)
    ax.plot(xs, stats.norm.pdf(xs, mu25, sig25 / np.sqrt(n)), color=ORANGE, lw=1.8)
    ax.set_title(f"Moyenne de {n} paniers", fontsize=10); ax.set_xlabel("€"); ax.set_yticks([])
    NUM(f"skew_moy_{n}", stats.skew(mm))
style.save(fig, "ch01-tcl.png")
```

![Le théorème central limite sur les paniers de 2025. À gauche, la distribution d'un panier (très asymétrique). Ensuite, la distribution de la moyenne de 5, de 30 puis de 200 paniers, sur 2 000 tirages chacune : elle devient de plus en plus symétrique et se rapproche de la courbe normale (orange) de moyenne μ et d'écart-type σ/√n.](figures/ch01-tcl.png)

Avec 5 paniers, la distribution de la moyenne reste étirée à droite (asymétrie {{skew_moy_5:.2f}}) ; avec 30, elle est déjà presque symétrique ({{skew_moy_30:.2f}}) ; avec 200, elle épouse la courbe normale ({{skew_moy_200:.2f}}). C'est le **théorème central limite** : **la moyenne d'un grand nombre d'observations indépendantes suit approximativement une loi normale, quelle que soit la forme des données d'origine**, de moyenne $\mu$ et d'écart-type $\sigma/\sqrt n$. C'est lui qui justifie tous les intervalles de confiance et tous les tests des chapitres suivants. Il demande, en contrepartie, que $n$ soit assez grand : plus la distribution d'origine est asymétrique, plus il faut d'observations (quelques dizaines suffisent ici ; pour des montants très concentrés sur quelques gros clients, il en faudrait bien davantage).

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.5, exercice 1.8.

### 1.3.3 L'intervalle de confiance d'une moyenne

Une moyenne seule est une estimation **ponctuelle** : on ne sait pas si elle est précise. Un **intervalle de confiance** (IC) lui ajoute une fourchette. Puisque $\bar x$ est à peu près normale, centrée sur $\mu$ avec l'écart-type $\sigma/\sqrt n$, 95 % des échantillons donnent une moyenne à moins de **deux erreurs types** de la vraie valeur. On en déduit l'intervalle :

$$\bar x\;\pm\;t\,\frac{s}{\sqrt n},$$

où $s$ est l'écart-type de l'échantillon (on ne connaît pas $\sigma$) et $t$ un coefficient (1,96 pour un grand $n$ ; un peu plus pour un petit $n$, d'après la **loi de Student** : 2,306 pour $n=9$).

**À la main, sur nos neuf commandes** (moyenne 102,78 €, écart-type 85,83 €) : l'erreur type vaut $85{,}83/\sqrt9=28{,}61$ €, la marge $2{,}306\times28{,}61\approx65{,}98$ €, d'où l'intervalle **[36,8 € ; 168,8 €]**. Il est **immense**, et c'est normal : avec neuf commandes très dispersées, on ne sait presque rien du vrai panier moyen.

Avec un échantillon de **100 commandes** de 2025, tiré au hasard :

```python
from outils_ch01 import ic_moyenne
echantillon = np.random.default_rng(12).choice(pop, 100, replace=False)
bas, haut = ic_moyenne(echantillon)
print("moyenne :", round(echantillon.mean(), 2), "| IC à 95 % : [", round(bas, 1), ";", round(haut, 1), "]")
```

```python hide
t9 = stats.t.ppf(0.975, 8)
assert abs(t9 - 2.306) < 5e-4 and abs(85.83 / 3 - 28.61) < 5e-3 and abs(t9 * 28.61 - 65.98) < 0.05
assert abs(102.78 - 65.98 - 36.8) < 0.05 and abs(102.78 + 65.98 - 168.76) < 0.05
b_, h_ = ic_moyenne(echantillon)
NUM("x100", echantillon.mean()); NUM("s100", echantillon.std(ddof=1)); NUM("ic_bas", b_); NUM("ic_haut", h_)
NUM("marge100", (h_ - b_) / 2); NUM("marge_rel", (h_ - b_) / 2 / echantillon.mean() * 100)
NUM("contient_txt", "se trouve bien" if b_ <= mu25 <= h_ else "ne se trouve pas")
```

On a trouvé {{x100:.1f}} € avec un écart-type de {{s100:.1f}} € ; l'intervalle à 95 % est [{{ic_bas:.1f}} € ; {{ic_haut:.1f}} €], de **demi-largeur {{marge100:.1f}} €**. La vraie moyenne ({{mu25:.1f}} €) {{contient_txt:raw}} dans l'intervalle. La gérante peut donc être informée : avec 100 commandes, le panier moyen est connu à environ **plus ou moins {{marge100:.0f}} €**, soit {{marge_rel:.0f}} %. Avec un panier observé de 98 € et la même précision, « 110 € » ne serait donc pas exclu : il se trouverait à l'intérieur de l'intervalle.

#### Que signifie « 95 % » ?

Le « 95 % » **ne** décrit **pas** la probabilité que $\mu$ soit dans *cet* intervalle (une fois l'intervalle calculé, $\mu$ y est ou n'y est pas). Il décrit la **méthode** : si l'on répétait l'échantillonnage un grand nombre de fois, **95 % des intervalles construits ainsi contiendraient** la vraie valeur. Vérifions-le : on construit 1 000 intervalles à partir de 1 000 échantillons de 100 commandes.

```python hide
rng_i = np.random.default_rng(5)
ics = np.array([ic_moyenne(rng_i.choice(pop, 100, replace=False)) for _ in range(1000)])
couvre = (ics[:, 0] <= mu25) & (mu25 <= ics[:, 1])
NUM("couverture", couvre.mean() * 100); NUM("n_rates", (~couvre).sum())
fig, ax = plt.subplots(figsize=(8.6, 4.2))
for i in range(40):
    col = BLEU if couvre[i] else ROUGE
    ax.plot(ics[i], [i, i], color=col, lw=2 if not couvre[i] else 1.4)
    ax.plot(ics[i].mean(), i, "o", color=col, ms=3)
ax.axvline(mu25, color=ENCRE, lw=1.4)
ax.text(mu25 + 0.5, 43, f"vraie moyenne {mu25:.1f} €".replace(".", ","), fontsize=9)
ax.set_ylim(-1, 45); ax.set_yticks([]); ax.set_xlabel("panier moyen (€)"); ax.set_title("40 intervalles de confiance à 95 %, construits sur 40 échantillons de 100 commandes")
ax.grid(axis="y", visible=False)
style.save(fig, "ch01-ic.png")
```

![Quarante intervalles de confiance à 95 %, chacun construit sur un échantillon différent de 100 commandes. La ligne verticale est la vraie moyenne ; les intervalles bleus la contiennent, les intervalles rouges la manquent.](figures/ch01-ic.png)

Sur les 1 000 intervalles, **{{couverture:.1f}} %** contiennent la vraie moyenne : {{n_rates:.0f}} la manquent, soit un peu plus que les 5 % annoncés (le théorème central limite n'est qu'une approximation pour des paniers aussi asymétriques). Sur les 40 premiers de la figure, quelques-uns, en rouge, la manquent : c'est le **prix** d'un niveau de confiance de 95 % et non de 100 %. Pour viser 99 %, on élargit l'intervalle (coefficient 2,58 au lieu de 1,96) ; pour un intervalle plus étroit, on paie par un niveau de confiance plus faible.

> ⚠️ **Trois lectures fausses à éviter.** (1) « Il y a 95 % de chances que $\mu$ soit dans l'intervalle » : le hasard est dans l'échantillon, pas dans $\mu$. (2) « 95 % des commandes sont dans l'intervalle » : l'intervalle concerne la **moyenne**, pas les commandes individuelles ; les paniers vont de 2 à 988 €. (3) « Deux intervalles qui se chevauchent prouvent qu'il n'y a pas de différence » : c'est plus subtil, et c'est l'objet des tests du volume III.

### 1.3.4 L'intervalle de confiance d'une proportion

Beaucoup de questions d'entreprise portent sur une **proportion** : le taux de retour, la part de clients satisfaits, le taux d'ouverture d'un e-mail. La gérante demande : « Sur 400 lignes du Site, 36 ont été retournées : est-ce 9 % ? » Le chiffre observé est $\hat p=36/400=9{,}0\ \%$. Son erreur type est

$$\text{erreur type}(\hat p)=\sqrt{\frac{\hat p\,(1-\hat p)}{n}}=\sqrt{\frac{0{,}09\times0{,}91}{400}}\approx0{,}0143,$$

et l'intervalle à 95 % est $\hat p\pm1{,}96\times0{,}0143$, soit $9{,}0\ \%\pm2{,}8$ points : **[6,2 % ; 11,8 %]**. Même avec 400 lignes, le taux de retour est connu à près de trois points près, ce qui est large devant un taux de 9 %. Voyons ce que donne un tirage de 400 lignes dans les données.

```python
from outils_ch01 import ic_proportion
site = lignes.merge(commandes[["id_commande", "canal"]], on="id_commande").query("canal == 'Site'")
retourne = site["id_ligne"].isin(pd.read_csv("donnees/retours.csv")["id_ligne"]).values
tirage = np.random.default_rng(8).choice(retourne, 400, replace=False)
print("taux observé :", round(tirage.mean(), 4), "| IC de Wald :", np.round(ic_proportion(tirage.sum(), 400), 4))
```

```python hide
assert abs(36 / 400 - 0.09) < 1e-12 and abs(np.sqrt(0.09 * 0.91 / 400) - 0.0143) < 5e-5 and abs(1.96 * 0.0143 - 0.028) < 5e-4
pv = retourne.mean()
NUM("p_vrai", pv * 100); NUM("p_hat", tirage.mean() * 100)
w = ic_proportion(tirage.sum(), 400); wi = ic_proportion(tirage.sum(), 400, methode="wilson")
NUM("w_bas", w[0] * 100); NUM("w_haut", w[1] * 100); NUM("wi_bas", wi[0] * 100); NUM("wi_haut", wi[1] * 100)
NUM("p_vrai_ok", int(w[0] <= pv <= w[1]))
```

Sur ces 400 lignes, {{k400:.0f}} sont retournées : {{p_hat:.2f}} %, avec un intervalle de [{{w_bas:.1f}} % ; {{w_haut:.1f}} %]. Le taux de retour de l'ensemble du Site, lui, est de {{p_vrai:.2f}} %. Quand la proportion est **proche de 0 ou de 1**, ou l'échantillon petit, l'intervalle « de Wald » ci-dessus (symétrique autour de $\hat p$) devient peu fiable (il peut même descendre sous 0 %) ; l'intervalle de **Wilson**, légèrement asymétrique, donne [{{wi_bas:.1f}} % ; {{wi_haut:.1f}} %] ici, et c'est celui qu'on préfère. Retenez surtout l'**ordre de grandeur** : pour une proportion voisine de 50 %, la marge vaut environ $1/\sqrt n$ (3 points pour $n=1\,000$, 5 points pour $n=400$).

```python hide
NUM("k400", tirage.sum())
```

### 1.3.5 Combien d'observations faut-il ?

Avant une enquête, une question domine : **quelle taille d'échantillon** pour atteindre une précision donnée ? On inverse les formules. Pour une **moyenne** et une marge d'erreur souhaitée $e$ :

$$n=\left(\frac{1{,}96\,\sigma}{e}\right)^2.$$

Pour connaître le panier moyen à plus ou moins 5 € près, avec un écart-type de {{sig25:.1f}} €, il faut $n=(1{,}96\times{{sig25:.1f}}/5)^2\approx$ **{{n_moy5:,.0f}} commandes**. À ±10 €, il en faut le quart : {{n_moy10:,.0f}}. Pour une **proportion** $p$ et une marge $e$ :

$$n=\frac{1{,}96^2\;p\,(1-p)}{e^2}.$$

Pour un taux de retour d'environ 9 %, connu à ±2 points, il faut $n=1{,}96^2\times0{,}09\times0{,}91/0{,}02^2\approx$ **{{n_prop2:,.0f}} lignes** ; à ±1 point, **{{n_prop1:,.0f}}**. Si l'on ne sait rien de $p$, on prend le cas le plus défavorable $p=0{,}5$ (le produit $p(1-p)$ est maximal) : $\pm3$ points demandent alors {{n_prop_pire:,.0f}} répondants, le chiffre classique des sondages.

```python hide
NUM("n_moy5", (1.96 * sig25 / 5) ** 2); NUM("n_moy10", (1.96 * sig25 / 10) ** 2)
NUM("n_prop2", 1.96 ** 2 * 0.09 * 0.91 / 0.02 ** 2); NUM("n_prop1", 1.96 ** 2 * 0.09 * 0.91 / 0.01 ** 2)
NUM("n_prop_pire", 1.96 ** 2 * 0.25 / 0.03 ** 2)
assert round(1.96 ** 2 * 0.09 * 0.91 / 0.02 ** 2) in (786, 787)
```

Deux points de méthode. D'abord, **les formules supposent un échantillon tiré au hasard dans une population très grande** devant lui. Quand l'échantillon représente une fraction notable de la population (disons plus de 5 %), l'erreur est plus petite : on la multiplie par le **facteur de correction de population finie** $\sqrt{(N-n)/(N-1)}$. Pour 400 commandes tirées sur {{n25:,.0f}}, il vaut {{fpc400:.3f}} (négligeable) ; pour 5 000 commandes, {{fpc5000:.2f}}. Ensuite, la **précision a un coût qui croît très vite** : passer de ±10 € à ±5 € demande quatre fois plus de commandes, de ±5 € à ±2,5 € encore quatre fois plus. Il est souvent plus rentable de **mieux tirer** un petit échantillon que d'en agrandir un mauvais, ce qui nous amène à la dernière question.

```python hide
NUM("fpc400", np.sqrt((len(pop) - 400) / (len(pop) - 1))); NUM("fpc5000", np.sqrt((len(pop) - 5000) / (len(pop) - 1)))
```

### 1.3.6 Les biais, que la taille ne corrige pas

Toute la section précédente mesure l'erreur due **au hasard**. Elle disparaît quand $n$ augmente. Il existe une autre sorte d'erreur, le **biais**, qui ne disparaît **jamais** avec la taille : il vient de la **façon** dont l'échantillon a été constitué, et un grand échantillon biaisé donne simplement une mauvaise réponse **avec une grande assurance**.

Un exemple tiré de la boutique. La gérante veut savoir : « **En moyenne, combien de commandes passe un client en trois ans ?** » Deux manières d'interroger les données :

- **Méthode A** : tirer au hasard 300 clients dans la liste des {{n_clients:,.0f}} clients inscrits et compter leurs commandes.
- **Méthode B** : tirer au hasard 300 *commandes* (« les clients que l'on croise à la caisse ») et compter, pour chacune, les commandes de son client.

La méthode B paraît naturelle (« on prend des gens qui achètent ») ; mais un client qui commande 40 fois a **40 fois plus de chances** d'être croisé qu'un client qui commande une seule fois. On sur-représente les fidèles.

```python hide
cpt = cmd.groupby("id_client").size().reindex(cli["id_client"], fill_value=0)
vrai_moy = cpt.mean()
rng_b = np.random.default_rng(6)
est_a = np.array([cpt.sample(300, random_state=int(rng_b.integers(1e9))).mean() for _ in range(1000)])
cmd_clients = cmd["id_client"].values
est_b = np.array([cpt.loc[rng_b.choice(cmd_clients, 300)].values.mean() for _ in range(1000)])
NUM("vrai_moy", vrai_moy); NUM("est_a", est_a.mean()); NUM("est_b", est_b.mean())
NUM("sd_a", est_a.std()); NUM("sd_b", est_b.std())
gros = cpt[cpt > 0]
NUM("n_sans", (cpt == 0).sum()); NUM("max_cmd", cpt.max())
big = rng_b.choice(cmd_clients, 3000)
vals_b = cpt.loc[big].values
b_, h_ = O.ic_moyenne(vals_b)
NUM("bb_bas", b_); NUM("bb_haut", h_)
fig, ax = plt.subplots(figsize=(8.4, 3.4))
ax.hist(est_a, bins=30, color=BLEU, alpha=0.75, label="méthode A : clients tirés dans la liste")
ax.hist(est_b, bins=30, color=ORANGE, alpha=0.75, label="méthode B : clients croisés à la caisse")
ax.axvline(vrai_moy, color=ENCRE, lw=1.6)
ax.set_ylim(0, 125)
ax.text(vrai_moy + 0.2, 118, "vérité", fontsize=9)
ax.set_xlabel("nombre moyen de commandes par client estimé (échantillons de 300)"); ax.set_ylabel("nombre d'échantillons"); ax.legend(fontsize=8.5, loc="upper right")
style.save(fig, "ch01-biais.png")
```

![Deux façons d'estimer le nombre moyen de commandes par client, avec 1 000 échantillons de 300 chacune. La méthode A (bleu), qui tire des clients dans la liste, est centrée sur la vérité (trait noir). La méthode B (orange), qui tire des commandes, est centrée très au-dessus : le biais ne dépend pas de la taille de l'échantillon.](figures/ch01-biais.png)

La vérité est de **{{vrai_moy:.2f}} commandes par client** (en comptant les {{n_sans:,.0f}} clients inscrits qui n'ont jamais commandé). La méthode A donne en moyenne {{est_a:.2f}}, avec une erreur type de {{sd_a:.2f}} : sans biais. La méthode B donne en moyenne **{{est_b:.2f}}**, plus de deux fois trop. Et ce n'est pas une question de taille : avec 3 000 commandes tirées par la méthode B, l'intervalle de confiance à 95 % devient [{{bb_bas:.1f}} ; {{bb_haut:.1f}}], **très étroit et très faux**. C'est l'image de ce que l'on appelle être « précisément à côté de la plaque ».

On retrouve ce mécanisme partout : l'enquête auprès des clients qui ont **accepté** de répondre (les mécontents et les enthousiastes répondent plus que les indifférents), l'analyse des clients **encore actifs** (on a oublié ceux qui sont partis), l'étude des seules **réussites**. La section 5.3 y revient dans le cadre des enquêtes.

> ⚠️ **Erreur d'échantillonnage, biais, erreur de mesure : trois choses différentes.** L'**erreur d'échantillonnage** vient du hasard du tirage ; elle diminue en $1/\sqrt n$ et se quantifie par l'intervalle de confiance. Le **biais de sélection** vient de la façon de constituer l'échantillon ; il ne diminue pas avec $n$ et ne se voit **pas** dans l'intervalle de confiance. L'**erreur de mesure** vient de la façon d'observer (une saisie fausse, une question mal posée, un capteur déréglé) ; elle aussi persiste quand $n$ augmente. Un intervalle étroit ne garantit que l'absence de hasard, **jamais** l'absence d'erreur.

> ✅ **À retenir.** (1) Une statistique d'échantillon varie d'un tirage à l'autre ; son écart-type est l'erreur type $\sigma/\sqrt n$ (division par deux : quadrupler $n$). (2) Le théorème central limite rend la moyenne approximativement normale, d'où l'intervalle $\bar x\pm t\,s/\sqrt n$ ; « 95 % » décrit la méthode, pas une probabilité sur $\mu$. (3) Une proportion a une erreur type $\sqrt{\hat p(1-\hat p)/n}$ ; $n$ se calcule en inversant la formule. (4) Aucune taille d'échantillon ne corrige un biais de sélection : posez toujours la question « **comment ces observations sont-elles arrivées dans mon fichier ?** ».

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.5 et 1.6, exercices 1.9 et 1.10.
