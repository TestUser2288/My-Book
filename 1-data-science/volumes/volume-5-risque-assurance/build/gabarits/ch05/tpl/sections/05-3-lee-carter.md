## 5.3 Le modèle de Lee–Carter

La section 5.1 a montré que la table d'une année n'est pas celle de la vie des assurés : la mortalité **baisse** et il faut la projeter. Le modèle de **Lee–Carter** (1992) est la référence historique pour le faire : il tient en une équation, s'ajuste en une décomposition en valeurs singulières, et résume l'évolution de la mortalité de tous les âges par **un seul indice du temps** que l'on prolonge comme une série chronologique. Cette section l'ajuste sur nos données, le compare à la **vérité programmée**, le projette, le met à l'épreuve hors période, puis chiffre le **risque de longévité** d'un portefeuille de rentes.

```python hide
AXe, BXe, KTs, SV = lc_ajuste(M["F"])                                   # étape 1 : SVD
KTe = lc_recale(AXe, BXe, KTs, D["F"].to_numpy(), E["F"].to_numpy())    # étape 2 : k_t recalé sur les décès
KTv = KT["kt_F"].to_numpy()
AXv, BXv = AX["F"], BX
part = SV ** 2 / (SV ** 2).sum()
NUM("part1", round(100 * part[0], 1)); NUM("sumb", round(BXe.sum(), 3)); NUM("sumk", f"{KTs.sum():.0e}")
NUM("max_ax", round(np.abs(AXe - AXv).max(), 2)); NUM("corr_bx", round(np.corrcoef(BXe, BXv)[0, 1], 3))
NUM("rmse_svd", round(np.sqrt(np.mean((KTs - KTv) ** 2)), 2)); NUM("rmse_rec", round(np.sqrt(np.mean((KTe - KTv) ** 2)), 2))
NUM("bx20", round(BXv[20], 4)); NUM("bx35", round(BXv[35], 4)); NUM("bx60", round(BXv[60], 4)); NUM("bx90", round(BXv[90], 4))
NUM("bx60_pct_abs", round(100 * (1 - np.exp(-1.2 * BXv[60])), 1)); NUM("bx20_pct_abs", round(100 * (1 - np.exp(-1.2 * BXv[20])), 1))
rel_b = np.abs(BXe / BXv - 1)[20:91]
NUM("relb_med", round(100 * np.median(rel_b))); NUM("relb_max", round(100 * rel_b.max()))
NUM("corr_err_k", round(np.corrcoef(KTe - KTv, KTv)[0, 1], 2))
NUM("kt1980", round(KTv[0], 1)); NUM("kt2019", round(KTv[-1], 1))
```

### 5.3.1 Le modèle

Le modèle de Lee–Carter décrit le logarithme du taux de mortalité à l'âge $x$ l'année $t$ par

$$
\ln m_{x,t} = a_x + b_x\,k_t + \varepsilon_{x,t}.
$$

Chaque terme a un rôle précis :

- $a_x$ est le **profil moyen** : le logarithme du taux à l'âge $x$ en moyenne sur la période (la courbe en J des taux de la section 5.1.1).
- $k_t$ est l'**indice du temps** : un nombre par année, qui résume le niveau général de la mortalité. Quand $k_t$ baisse, la mortalité baisse à tous les âges.
- $b_x$ est la **sensibilité de l'âge $x$** à cet indice. Si $k$ diminue de $\Delta k$, le taux à l'âge $x$ est multiplié par $e^{b_x\Delta k}$.

Un chiffre aide à lire $b_x$ : dans cette population, $b_{20}={{bx20}}$, $b_{35}={{bx35}}$, $b_{60}={{bx60}}$ et $b_{90}={{bx90}}$ (valeurs vraies). Avec une dérive de $-1{,}2$ par an pour $k_t$, la mortalité baisse chaque année d'environ {{bx60_pct_abs}} % à 60 ans et de {{bx20_pct_abs}} % à 20 ans. L'amélioration est donc **inégale** selon l'âge, et c'est précisément ce que le terme $b_x$ permet de représenter (avec un seul $k_t$ et des taux d'amélioration constants, on retrouverait au contraire une baisse identique à tous les âges).

> 📐 **Identification : pourquoi deux contraintes.** Le modèle n'est pas identifiable tel quel : si $(a_x, b_x, k_t)$ convient, alors $(a_x + c\,b_x,\; b_x,\; k_t - c)$ donne exactement les mêmes taux (on déplace une constante de $k$ vers $a$), et $(a_x,\; \lambda b_x,\; k_t/\lambda)$ aussi (on échange une échelle entre $b$ et $k$). On fixe donc ces deux libertés par
> $$\sum_t k_t = 0, \qquad \sum_x b_x = 1 .$$
> La première rend $a_x$ égal à la moyenne temporelle de $\ln m_{x,t}$ (c'est ce qu'on calcule en premier) ; la seconde donne à $k_t$ l'unité d'une variation de « taux moyen » et rend les $b_x$ comparables à des parts. **Cette convention est arbitraire** : changer la normalisation change la valeur de $k_t$ sans changer les taux ajustés. Quand on compare des estimations à la vérité, il faut donc comparer les mêmes conventions : c'est le cas ici, la vérité programmée vérifiant $\sum_t k_t = 0$ et $\sum_x b_x = 1$.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : exercice 5.9.

### 5.3.2 Ajustement par décomposition en valeurs singulières

Une fois $a_x$ estimé par la moyenne en ligne de la matrice des $\ln m_{x,t}$ (âges en lignes, années en colonnes), la matrice centrée $Z_{x,t} = \ln m_{x,t} - \hat a_x$ doit se factoriser sous la forme $b_x k_t$ : c'est une approximation de **rang 1**. Le théorème d'Eckart–Young dit que la meilleure approximation de rang 1 au sens des moindres carrés est donnée par le premier terme de la **décomposition en valeurs singulières** (SVD) : $Z \approx s_1\,u_1 v_1^{\top}$. On pose alors $b_x \propto u_{1,x}$ et $k_t \propto s_1\,v_{1,t}$, normalisés par les deux contraintes.

```python
ax_hat, bx_hat, kt_hat, sv = lc_ajuste(M["F"])        # SVD de ln m − a_x, normalisée (Σb = 1, Σk = 0)
part = sv ** 2 / (sv ** 2).sum()                       # part de variation de chaque composante
print(f"première composante : {100 * part[0]:.1f} % ;  Σ b = {bx_hat.sum():.3f} ;  Σ k = {kt_hat.sum():.0e}")
```

La première composante explique {{part1}} % de la variation de $Z$. Ce n'est pas davantage parce que le reste est du **bruit** et non de la structure : chaque cellule a des décès de Poisson, dont le bruit relatif est grand aux âges où les décès sont rares. Ce taux de {{part1}} % ne mesure donc pas la qualité du modèle (qui est ici exactement vrai), mais la part de bruit dans les données. Dans la littérature, sur des populations nationales bien plus nombreuses, la première composante explique d'ordinaire une part nettement plus élevée de la variation (de l'ordre de 90 % ou plus, valeur à vérifier selon les données).

**Seconde étape : recaler $k_t$.** La SVD minimise des erreurs sur les *logarithmes* des taux, et traite aussi fortement les âges rares (peu de décès) que les âges fréquents. Lee et Carter ajoutent donc une étape : pour chaque année, on **ré-estime $k_t$** pour que le nombre de décès prédit soit égal au nombre de décès observé, c'est-à-dire que l'on résout en $k$ l'équation $\sum_x E_{x,t}\,e^{\hat a_x+\hat b_x k}=\sum_x D_{x,t}$. Le recalage réduit l'erreur : l'écart quadratique moyen entre $k_t$ estimé et vrai passe de {{rmse_svd}} (SVD seule) à {{rmse_rec}} (recalé).

La figure compare les trois composantes à la vérité programmée. Les $a_x$ sont retrouvés (écart maximal {{max_ax}} sur le logarithme du taux), les $b_x$ ont la bonne forme (corrélation {{corr_bx}} avec les vrais $b_x$) et le $k_t$ recalé suit la vérité, y compris le **pic de 2018** que nous discutons en 5.3.3.

```python hide
fig, ax = plt.subplots(1, 3, figsize=(11.6, 3.5))
xs = np.arange(100)
ax[0].plot(xs, AXv, color=MUET, lw=2.6); ax[0].plot(xs, AXe, color=BLEU, lw=1.2)
ax[0].set_xlabel("âge"); ax[0].set_ylabel("$a_x$ (log du taux moyen)"); ax[0].text(3, -1.5, "vrai : gris\nestimé : bleu", fontsize=8.5, color=ENCRE2)
ax[1].plot(xs, BXv, color=MUET, lw=2.6); ax[1].plot(xs, BXe, color=BLEU, lw=1.2)
ax[1].set_xlabel("âge"); ax[1].set_ylabel("$b_x$")
ax[2].plot(ANNEES, KTv, color=MUET, lw=2.6); ax[2].plot(ANNEES, KTe, color=BLEU, lw=1.2); ax[2].plot(ANNEES, KTs, color=ORANGE, lw=1.0, ls="--")
ax[2].set_xlabel("année"); ax[2].set_ylabel("$k_t$"); ax[2].annotate("pic 2018", (2018, KTv[list(ANNEES).index(2018)]), (1999, KTv[list(ANNEES).index(2018)] + 2), fontsize=8.5, color=ENCRE2, arrowprops=dict(arrowstyle="-", color=MUET))
ax[2].text(1981, -18, "SVD seule (orange)\nrecalé (bleu)", fontsize=8.5, color=ENCRE2)
fig.tight_layout(); fig.savefig("figures/ch05-lee-carter.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

![Modèle de Lee–Carter ajusté sur les femmes : $a_x$, $b_x$ et $k_t$ estimés (bleu) contre la vérité programmée (gris épais) ; en orange, $k_t$ obtenu par la SVD seule avant recalage. Données simulées.](figures/ch05-lee-carter.png)

> 🧪 **Un avantage de l'honnêteté des données simulées.** Avec des données réelles, on ne peut pas vérifier si $\hat b_x$ est « le vrai $b_x$ » : il n'existe pas. Ici, on constate que l'estimation est **bonne mais pas exacte** : l'erreur relative sur $b_x$ est en médiane de {{relb_med}} % entre 20 et 90 ans (au maximum {{relb_max}} %), et elle se répercute sur $k_t$ : l'erreur de $k_t$ a une corrélation de {{corr_err_k}} avec $k_t$ lui-même, signe d'une erreur d'échelle. Cette erreur d'estimation va jouer un rôle dans la projection.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.6, exercices 5.9 et 5.10.

### 5.3.3 Projeter l'indice $k_t$

Le mérite du modèle est de transformer un problème de dimension 100 (une série par âge) en un problème de **dimension 1** : la série $k_t$. Lee et Carter la modélisent par une **marche aléatoire avec dérive** :

$$
k_{t+1} = k_t + \delta + \sigma\,\eta_{t+1}, \qquad \eta_t \sim \mathcal N(0,1) \text{ indépendants}.
$$

L'estimateur naturel de la dérive est la pente moyenne, $\hat\delta = (k_T - k_1)/(T-1)$ (les accroissements intermédiaires s'annulent), et celui de $\sigma$ est l'écart-type des accroissements $\Delta k_t = k_{t}-k_{t-1}$. La prévision à $h$ années est $k_T + h\,\hat\delta$, avec un écart-type $\sigma\sqrt{h}$ qui **croît** avec l'horizon.

```python
delta, sigma = derive_sigma(KTe)                           # dérive et écart-type des accroissements de k_t
print(f"dérive estimée δ = {delta:.3f}   écart-type σ = {sigma:.3f}")
```

La dérive estimée est de {{delta_hat}} par an, **très proche de la vérité programmée** ($-1{,}2$) : l'estimateur de la pente, qui ne dépend que des deux extrémités, résiste bien au bruit. L'écart-type estimé est de {{sigma_hat:.2f}}, **nettement supérieur** à la vérité programmée ($\sigma=1$). Deux causes se combinent, et chacune est instructive.

**Première cause : le choc de 2018.** Le jeu contient un pic transitoire de mortalité en 2018 (un épisode de surmortalité qui ne dure qu'une année, de $+4$ sur $k$). Il crée un accroissement positif d'environ $+4$ l'année du choc puis un accroissement négatif d'environ $-4$ l'année suivante. La dérive, qui ne dépend que des extrémités, l'ignore, mais l'écart-type en est fortement gonflé. En remplaçant la valeur de 2018 par l'interpolation de ses voisines, on passe à {{sigma_i:.2f}}. Le bon traitement dépend de la nature du choc : s'il est **transitoire** (épidémie, canicule), on l'écarte de l'estimation de $\sigma$ ; s'il est **permanent** (une rupture structurelle de tendance), on le garde et l'on s'interroge sur la dérive.

**Seconde cause : l'erreur d'estimation de $k_t$.** Les $\hat k_t$ ne sont pas les vrais $k_t$ : chacun est estimé avec une erreur d'écart-type $\tau\approx{{tau}}$ d'après l'information de Fisher du modèle de Poisson ($\tau_t^2 = 1/\sum_x D_{x,t}\,\hat b_x^2$). Les accroissements estimés ont donc une variance $\sigma^2 + 2\tau^2$ (deux erreurs, chacune comptée une fois, et indépendantes d'une année à l'autre), ce qui donne $\sigma$ corrigé $=\sqrt{\hat\sigma^2 - 2\tau^2}\approx{{sigma_c:.2f}}$, plus proche de la vérité (la variabilité effectivement réalisée par les vrais $k_t$ est de {{sigma_vrai:.2f}} hors choc). **Ignorer cette correction rend les intervalles de projection trop larges** : une prudence parfois voulue, mais qu'il vaut mieux faire par choix que par accident.

Projetons maintenant $k_t$ sur 30 ans (jusqu'en 2049) par simulation de 2 000 trajectoires, avec la dérive estimée et l'écart-type interpolé. L'espérance de vie à 65 ans se déduit de $k$ par la table construite avec $a_x+b_x k$ : on la calcule pour chaque niveau de $k$. La figure montre l'éventail des trajectoires de $k_t$ et l'espérance de vie à 65 ans correspondante.

```python hide
i18 = list(ANNEES).index(2018)
KTi = KTe.copy(); KTi[i18] = (KTi[i18 - 1] + KTi[i18 + 1]) / 2
delta_i, sigma_i = derive_sigma(KTi)
tau = np.array([1 / np.sqrt((D["F"][t].to_numpy() * BXe ** 2).sum()) for t in ANNEES])
sigma_c = np.sqrt(max(sigma_i ** 2 - 2 * np.mean(tau ** 2), 0))
dv, sv_ = derive_sigma(KTv); dkv = np.delete(np.diff(KTv), [i18 - 1, i18]); sig_vrai = dkv.std(ddof=1)
d_hat, s_hat = derive_sigma(KTe)
NUM("delta_hat", round(d_hat, 3)); NUM("sigma_hat", round(s_hat, 2)); NUM("sigma_i", round(sigma_i, 2)); NUM("tau", round(float(np.mean(tau)), 2))
NUM("sigma_c", round(float(sigma_c), 2)); NUM("sigma_vrai", round(float(sig_vrai), 2)); NUM("sd_delta", round(sigma_i / np.sqrt(len(KTe) - 1), 2)); NUM("sd_delta_pct", round(100 * sigma_i / np.sqrt(len(KTe) - 1) / abs(d_hat)))
assert abs(d_hat + 1.2) < 0.2 and s_hat > 1.3 and sigma_c < sigma_i
H30 = 30
rng = np.random.default_rng(2024)
sim30 = lc_projette(AXe, BXe, KTe, H30, 2000, delta_i, sigma_i, rng)
def qfull(k):
    return prolonge(q_depuis_m(np.exp(AXe + BXe * k)), P_GM)
grille_k = np.linspace(min(sim30.min(), KTe.min()) - 1, KTe.max() + 1, 40)
e65_g = np.array([table_vie(qfull(k)).e[65] for k in grille_k])
e65_de = lambda k: np.interp(k, grille_k, e65_g)
e65_hist = np.array([e65_de(k) for k in KTe])
qs = np.percentile(sim30, [5, 25, 50, 75, 95], axis=0)
e65_qs = e65_de(qs)
NUM("e65_2019", round(float(e65_hist[-1]), 2)); NUM("e65_2049", round(float(e65_qs[2, -1]), 2))
NUM("e65_2049_lo", round(float(e65_qs[4, -1]), 2)); NUM("e65_2049_hi", round(float(e65_qs[0, -1]), 2))
NUM("e65_1980", round(float(e65_hist[0]), 2)); NUM("gain_e65", round(float(e65_qs[2, -1] - e65_hist[-1]), 1))
fig, ax = plt.subplots(1, 2, figsize=(10.4, 3.9))
fut = np.arange(2020, 2020 + H30)
ax[0].plot(ANNEES, KTe, color=BLEU, lw=1.6)
ax[0].fill_between(fut, qs[0], qs[4], color=BLEU, alpha=0.15, lw=0); ax[0].fill_between(fut, qs[1], qs[3], color=BLEU, alpha=0.25, lw=0)
ax[0].plot(fut, qs[2], color=BLEU, lw=1.6, ls="--")
ax[0].set_xlabel("année"); ax[0].set_ylabel("indice $k_t$"); ax[0].text(1982, -62, "zones : 50 % et 90 % des trajectoires", fontsize=8.5, color=ENCRE2)
ax[1].plot(ANNEES, e65_hist, color=BLEU, lw=1.6)
ax[1].fill_between(fut, e65_qs[4], e65_qs[0], color=BLEU, alpha=0.15, lw=0); ax[1].fill_between(fut, e65_qs[3], e65_qs[1], color=BLEU, alpha=0.25, lw=0)
ax[1].plot(fut, e65_qs[2], color=BLEU, lw=1.6, ls="--")
ax[1].set_xlabel("année"); ax[1].set_ylabel("espérance de vie à 65 ans (années)")
fig.tight_layout(); fig.savefig("figures/ch05-projection.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

![Projection de Lee–Carter pour les femmes : indice $k_t$ (à gauche) et espérance de vie à 65 ans correspondante (à droite). La ligne pleine est l'historique estimé, les tirets la médiane projetée, les zones foncée et claire les intervalles à 50 % et à 90 % (2 000 trajectoires). Données simulées.](figures/ch05-projection.png)

L'espérance de vie à 65 ans passe de {{e65_2019:.2f}} ans en 2019 (valeur lissée par le modèle) à une médiane de {{e65_2049:.2f}} ans en 2049 (intervalle à 90 % : de {{e65_2049_lo:.2f}} à {{e65_2049_hi:.2f}} ans), soit un gain médian de {{gain_e65}} an sur trente ans. Le modèle fait **gagner du temps au même rythme qu'avant** : si le rythme passé s'est interrompu, la projection l'ignore.

**Incertitude de paramètre.** L'intervalle ci-dessus ne contient que l'incertitude de **trajectoire** (le bruit $\sigma\eta$). Il ignore que la dérive elle-même est estimée : son écart-type est environ $\sigma/\sqrt{T-1}$, soit {{sd_delta}} pour une dérive de {{delta_hat}}, une imprécision relative d'environ {{sd_delta_pct}} %. On peut la prendre en compte en tirant la dérive de chaque trajectoire dans sa loi d'estimation (5.3.4).

> ⚠️ **Un intervalle de projection n'est qu'un modèle de plus.** L'éventail de la figure repose sur l'hypothèse d'une marche aléatoire à dérive **constante**, des mêmes $b_x$ pour toujours, et d'erreurs gaussiennes indépendantes. Rien ne garantit que la médiocre prévisibilité du passé se prolonge : l'incertitude **de modèle** est hors de l'intervalle.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.6, exercice 5.11.

### 5.3.4 Mettre le modèle à l'épreuve hors période, puis chiffrer le risque de longévité

**Une prévision se juge sur des données qu'elle n'a pas vues.** Refaisons l'exercice en ne montrant au modèle que les années 1980 à 2009, projetons dix ans, et comparons à ce qui s'est réellement passé jusqu'en 2019.

```python hide
Mb = M["F"].loc[:, 1980:2009]
axb, bxb, ktb, _ = lc_ajuste(Mb)
ktb = lc_recale(axb, bxb, ktb, D["F"].loc[:, 1980:2009].to_numpy(), E["F"].loc[:, 1980:2009].to_numpy())
ib = list(range(1980, 2010)).index(2009)
db, sb = derive_sigma(ktb)
rng = np.random.default_rng(7)
simb = lc_projette(axb, bxb, ktb, 10, 4000, db, sb, rng)
k19 = simb[:, -1]
lo, med, hi = np.percentile(k19, [5, 50, 95])
qb = lambda a_, b_, k: prolonge(q_depuis_m(np.exp(a_ + b_ * k)), P_GM)
e65_prev = table_vie(qb(axb, bxb, med)).e[65]
e65_fige = table_vie(qb(axb, bxb, ktb[-1])).e[65]
e65_reel = TF19.e[65]                                   # espérance de vie observée en 2019 (table de la section 5.1.2)
NUM("kbt_med", round(med, 1)); NUM("kbt_lo", round(lo, 1)); NUM("kbt_hi", round(hi, 1)); NUM("k19_reel", round(KTe[-1], 1))
NUM("e65_prev", round(e65_prev, 2)); NUM("e65_fige", round(e65_fige, 2)); NUM("e65_reel", round(e65_reel, 2))
NUM("err_prev", round(abs(e65_prev - e65_reel), 2)); NUM("err_fige", round(abs(e65_fige - e65_reel), 2)); NUM("ratio_err", round(abs(e65_fige - e65_reel) / abs(e65_prev - e65_reel)))
assert lo < KTe[-1] < hi and abs(e65_prev - e65_reel) < abs(e65_fige - e65_reel)
```

Le modèle ajusté sur 1980–2009 prévoit pour 2019 un indice médian de {{kbt_med}} (intervalle à 90 % : de {{kbt_lo}} à {{kbt_hi}}) ; la valeur effectivement estimée sur toutes les données est de {{k19_reel}}, **dans l'intervalle**. En espérance de vie à 65 ans en 2019, la prévision est de {{e65_prev:.2f}} ans contre {{e65_reel:.2f}} réellement, soit une erreur de {{err_prev:.2f}} an ; la méthode **naïve** (garder la table de 2009 telle quelle) aurait donné {{e65_fige:.2f}} ans, soit une erreur de {{err_fige:.2f}} an : **{{ratio_err}} fois plus**. La projection fait mieux que l'immobilisme, et c'est ce que l'on attendait.

> ⚠️ **Une validation flatteuse.** Les données ont été simulées avec exactement le modèle de Lee–Carter : l'ajustement ne peut qu'être bon. Sur des données réelles, on attend un modèle moins bien spécifié (effets de cohorte, ruptures) et des erreurs de prévision plus fortes. Le **protocole** (ajuster sur le passé, projeter, comparer) est ce qu'il faut retenir, pas le score.

**Le risque de longévité d'un portefeuille de rentes.** Un assureur sert des rentes viagères à des personnes qui ont 65 ans en 2019. Le coût d'une rente d'un euro par an payée d'avance, actualisée à 2 %, se calcule de trois manières :

1. **table de période 2019** : on suppose que la mortalité de 2019 ne change plus ;
2. **table de génération projetée** : on suit la cohorte, la mortalité de chaque année future étant celle que le modèle projette (valeur moyenne des simulations) ;
3. **distribution complète** : pour chaque trajectoire simulée de $k_t$, on recalcule le coût de la rente, ce qui donne une **loi** du coût.

Les trajectoires simulées incluent, pour chacune, une dérive tirée dans la loi d'estimation (incertitude de paramètre). Le **99,5 %-quantile** de cette loi, comparé à la moyenne, est le **capital de risque de tendance** : la somme à ajouter aux provisions pour couvrir un scénario de longévité aussi défavorable qu'un cas sur 200 (le seuil de 99,5 % est celui de Solvabilité II, section 4.2 ; il s'agit ici d'un ordre de grandeur pédagogique, non d'un calcul réglementaire).

```python hide
Hh = 55
rng = np.random.default_rng(11)
N_S = 2000
dsim = rng.normal(delta_i, sigma_i / np.sqrt(len(KTe) - 1), N_S)
paths = KTe[-1] + np.cumsum(dsim[:, None] + rng.normal(0, sigma_i, (N_S, Hh)), axis=1)
kk = np.column_stack([np.full(N_S, KTe[-1]), paths[:, :Hh - 1]])
v_ = 1 / 1.02
pv = np.zeros(N_S); surv = np.ones(N_S)
for j in range(Hh):
    age = 65 + j
    pv += v_ ** j * surv
    m = np.exp(AXe[age] + BXe[age] * kk[:, j]) if age < 100 else gm_mu(age + 0.5, P_GM)
    surv = surv * np.exp(-m)
a_per = valeurs(qF19, 0.02)[1][65]
q995 = np.quantile(pv, 0.995)
NUM("a_per", round(a_per, 2)); NUM("a_gen", round(pv.mean(), 2)); NUM("a_q995", round(q995, 2))
NUM("prime_gen", round(100 * (pv.mean() / a_per - 1), 1)); NUM("cap_tend", round(100 * (q995 / pv.mean() - 1), 1))
NUM("cv_tend", round(100 * pv.std() / pv.mean(), 1))
a_choc = valeurs(np.minimum(0.8 * qF19, 1.0), 0.02)[1][65]
NUM("choc20", round(100 * (a_choc / a_per - 1), 1))
# risque individuel : durées de vie simulées sous le scénario moyen
kmoy = np.concatenate([[KTe[-1]], KTe[-1] + delta_i * np.arange(1, Hh)])
qsc = np.array([1 - np.exp(-(np.exp(AXe[65 + j] + BXe[65 + j] * kmoy[j]) if 65 + j < 100 else gm_mu(65 + j + 0.5, P_GM))) for j in range(Hh)]); qsc[-1] = 1.0
rng = np.random.default_rng(5); n_i = 50000; vivant = np.ones(n_i, bool); pvi = np.zeros(n_i)
for j in range(Hh):
    pvi += v_ ** j * vivant; vivant &= rng.random(n_i) >= qsc[j]
cv1 = pvi.std() / pvi.mean()
NUM("cv_indiv", round(100 * cv1)); NUM("cv_100", round(100 * cv1 / np.sqrt(100), 1)); NUM("cv_1000", round(100 * cv1 / np.sqrt(1000), 1)); NUM("cv_10000", round(100 * cv1 / np.sqrt(10000), 2))
n_cross = (cv1 / (pv.std() / pv.mean())) ** 2
NUM("n_cross", round(n_cross, -2))
fig, ax = plt.subplots(1, 2, figsize=(10.4, 3.9))
ax[0].hist(pv, bins=40, color=BLEU, alpha=0.8)
for val, col in [(a_per, VIOLET), (pv.mean(), ENCRE2), (q995, ROUGE)]:
    ax[0].axvline(val, color=col, lw=1.4)
ymax = ax[0].get_ylim()[1]; ax[0].set_ylim(0, ymax * 1.22)
ax[0].text(a_per + 0.01, ymax * 1.12, "période 2019", color=VIOLET, fontsize=8.5, ha="left")
ax[0].text(pv.mean() + 0.01, ymax * 1.12, "moyenne", color=ENCRE2, fontsize=8.5, ha="left")
ax[0].text(q995 - 0.01, ymax * 1.12, "quantile 99,5 %", color=ROUGE, fontsize=8.5, ha="right")
ax[0].set_xlabel("coût d'une rente de 1 € par an à 65 ans"); ax[0].set_ylabel("nombre de trajectoires")
Ns = np.logspace(1, 5, 40)
ax[1].plot(Ns, 100 * cv1 / np.sqrt(Ns), color=BLEU, lw=1.8)
ax[1].axhline(100 * pv.std() / pv.mean(), color=ROUGE, lw=1.6, ls="--")
ax[1].set_xscale("log"); ax[1].set_yscale("log")
ax[1].set_xlabel("nombre de rentiers $N$"); ax[1].set_ylabel("écart-type relatif du coût moyen par rentier (%)")
ax[1].text(12, 100 * pv.std() / pv.mean() * 1.2, "risque de tendance (non diversifiable)", color=ROUGE, fontsize=8.5)
ax[1].text(1.3e3, 100 * cv1 / np.sqrt(1.3e3) * 1.6, "risque individuel", color=BLEU, fontsize=8.5)
fig.tight_layout(); fig.savefig("figures/ch05-longevite.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

Les résultats : la rente coûte {{a_per:.2f}} € par euro de rente avec la table de période 2019, **{{a_gen:.2f}} €** avec la table de génération projetée (soit {{prime_gen}} % de plus : c'est le prix de l'ignorance de l'amélioration future), et le 99,5 %-quantile de la distribution est de {{a_q995:.2f}} €, soit {{cap_tend}} % au-dessus de la moyenne. Le coefficient de variation du coût dû à la tendance est de {{cv_tend}} %.

Ce chiffre de {{cap_tend}} % est **petit**, et il faut s'en méfier pour deux raisons. D'abord, il dépend de l'hypothèse de marche aléatoire à dérive constante, qui ne laisse aucune place à une rupture de tendance. Ensuite, il est très inférieur à la secousse que l'on obtiendrait si l'on supposait simplement que les taux de décès sont **20 % plus bas** que prévu pour toujours : cela augmenterait le coût de la rente de {{choc20}} %. Les cadres prudentiels retiennent des chocs forfaitaires de cet ordre (paramètre à vérifier dans les textes en vigueur) justement parce que la **vraie** incertitude de modèle est supérieure à celle d'un modèle ajusté sur un passé récent : c'est le sens de la prudence réglementaire, qui ne mesure pas le même risque que l'intervalle statistique de la figure.

![Risque de longévité d'un portefeuille de rentes à 65 ans (femmes, 2019, i = 2 %). À gauche : coût d'une rente de 1 € par an selon 2 000 trajectoires de la tendance, avec la table de période (violet), la moyenne (gris) et le quantile à 99,5 % (rouge). À droite : écart-type relatif du coût moyen par rentier selon le nombre de rentiers, risque individuel (bleu) et risque de tendance (rouge). Données simulées.](figures/ch05-longevite.png)

La figure de droite montre la différence de nature entre les deux risques. Le **risque individuel** (un rentier vit plus ou moins longtemps) a un coefficient de variation de {{cv_indiv}} % pour un seul rentier ; il **se dilue** avec le nombre : {{cv_100}} % pour 100 rentiers, {{cv_1000}} % pour 1 000, {{cv_10000}} % pour 10 000. Le **risque de tendance** (toute la cohorte vit plus longtemps que prévu) touche tout le portefeuille en même temps : il **ne se mutualise pas**, et plafonne le risque restant à environ {{cv_tend}} % quel que soit le nombre de rentiers. Au-delà d'environ {{n_cross:,.0f}} rentiers, c'est lui qui domine.

> 💡 **Intuition.** La loi des grands nombres fait disparaître les **hasards** (qui meurt cette année), pas les **erreurs de modèle ou de tendance** (comment la mortalité évolue pour tous). C'est le même principe qu'au chapitre 3 pour le risque de marché : la diversification protège contre le bruit idiosyncratique, pas contre un facteur commun. La réassurance et le transfert de risque de longévité (chapitre 6) visent précisément ce facteur commun.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.7 et 5.8, exercice 5.12.

### 5.3.5 Limites du modèle

Le modèle de Lee–Carter est une **référence**, pas une vérité. Ses limites, à garder en tête quand on lit une projection :

- **Un seul facteur.** Un seul $k_t$ impose que tous les âges évoluent de façon parfaitement corrélée, au rythme $b_x$. Les modèles à plusieurs facteurs, ou les modèles qui séparent effets d'âge, de période et de **cohorte** (par exemple Cairns–Blake–Dowd, Renshaw–Haberman, âge-période-cohorte), corrigent ce défaut en ajoutant des paramètres.
- **Un bruit mal pris en compte.** L'ajustement par SVD suppose des erreurs de même variance sur les logarithmes, ce qui est faux (le bruit de Poisson est beaucoup plus fort aux âges rares). La formulation de **Brouhns, Denuit et Vermunt** ajuste directement la vraisemblance de Poisson et corrige ce défaut ; le recalage de la seconde étape en est une approximation.
- **Une dérive constante.** Rien dans les données ne prouve que le rythme d'amélioration restera celui du passé. Plusieurs pays ont connu des ralentissements, et des accélérations par vagues (selon la cause de décès), que ni la dérive constante ni l'éventail de la figure ne contiennent.
- **Des chocs de natures différentes.** Un pic transitoire (2018 ici) n'est pas une rupture, mais nous avons dû l'identifier **à la main**. Les épidémies et les canicules se traitent par des termes d'évènement distincts.
- **La vérité n'est pas connue.** Sur des données réelles, on ne peut pas comparer les estimations à la vérité : la validation hors période (5.3.4) est la meilleure assurance, et elle n'est jamais définitive.

> ✅ **À retenir (5.3).**
> - $\ln m_{x,t}=a_x+b_xk_t$ : profil moyen, sensibilité par âge, indice du temps ; contraintes $\sum k_t=0$ et $\sum b_x=1$. Ajustement par SVD (meilleure approximation de rang 1), puis recalage de $k_t$ sur les décès.
> - On projette $k_t$ par une marche aléatoire avec dérive : la dérive est bien estimée par les extrémités, mais $\sigma$ est **gonflé** par l'erreur d'estimation de $k_t$ et par les chocs transitoires.
> - **Valider hors période** : sur ces données, la projection fait nettement mieux que de figer la table.
> - Le **risque de longévité** a deux composantes : un risque individuel qui se mutualise, et un risque de tendance qui ne se mutualise pas. Le second plafonne la précision d'un portefeuille de rentes.
> - Les chiffres de capital sont **conditionnels** au modèle : les chocs réglementaires forfaitaires sont plus larges que l'intervalle statistique parce qu'ils couvrent aussi l'incertitude de modèle.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.6 à 5.8, exercices 5.9 à 5.12.
