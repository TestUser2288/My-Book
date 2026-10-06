## 2.5 ➕ Pour aller plus loin : chain ladder, Bornhuetter–Ferguson, Mack et bootstrap

> 🧭 **Section optionnelle.** Elle prolonge la section 2.3 : on cherche maintenant non plus *une* provision, mais **une provision avec son incertitude**, on la complète par une information a priori, et l'on examine ce qui met le chain ladder en défaut. Elle suppose connue la section 2.3.

### 2.5.1 Les hypothèses à vérifier

Le chain ladder de Mack repose sur trois hypothèses (section 2.3.3), dont la deuxième, celle d'un **schéma de développement stable**, est la plus exposée : les facteurs $f_j$ doivent valoir la même chose pour toutes les années de survenance et toutes les années calendaires. Dans la réalité, trois événements la font casser :

- un **changement de gestion** (la mutuelle règle plus vite ses dossiers : tous les paiements d'une diagonale sont avancés) ;
- une **revalorisation soudaine** (une décision de justice ou une réforme augmente les indemnités de toutes les années non encore réglées) ;
- un **changement de portefeuille** (un nouveau canal de distribution, une nouvelle garantie : les années récentes ne ressemblent plus aux anciennes).

Les deux premiers touchent **une diagonale** (une année calendaire) ; le troisième touche **les dernières lignes**. Le diagnostic consiste donc à chercher, dans les résidus, une structure en diagonale ou en ligne. Nous le ferons en 2.5.5.

### 2.5.2 Cape Cod et Bornhuetter–Ferguson : ajouter une information a priori

Le chain ladder a un défaut : il **extrapole** le dernier cumul observé de chaque année. Pour la dernière année de survenance (payée à 9 M€ après un seul délai), la provision est $(\prod_j\hat f_j-1)\times9$ M€ : tout repose sur un unique chiffre, bruité, multiplié par {{cdf0|1}}. Si le premier paiement de l'année est exceptionnellement bas ou haut, la provision l'est aussi dans la même proportion.

La méthode de **Bornhuetter–Ferguson** (BF) remplace cette extrapolation par une **information a priori** : un ratio sinistres sur primes attendu $\rho_i$ (issu de la tarification, de l'expérience, du jugement), appliqué à la prime acquise $P_i$. L'ultime attendu est $P_i\rho_i$, et l'on n'en retient que la **part non encore payée** :
$$\widehat R_i^{\text{BF}}=P_i\,\rho_i\,\bigl(1-\hat p_i\bigr),\qquad \hat p_i=\frac{1}{\prod_{j\ge I-i}\hat f_j},$$
où $\hat p_i$ est la **part déjà payée attendue** au délai atteint par l'année $i$. L'estimation BF ne dépend du paiement observé que *via* le fait qu'il est déjà payé (il vient s'ajouter à la réserve). Le chain ladder, lui, estime l'ultime par $C_{i,I-i}/\hat p_i$.

> 📐 **BF comme moyenne pondérée (crédibilité).** L'ultime BF s'écrit $\hat U^{\text{BF}}_i=C_i+P_i\rho_i(1-\hat p_i)$, et l'ultime CL $\hat U^{\text{CL}}_i=C_i/\hat p_i$. On en déduit
> $$\hat U_i^{\text{BF}}=\hat p_i\,\hat U^{\text{CL}}_i+(1-\hat p_i)\,P_i\rho_i.$$
> **Plus l'année est développée ($\hat p_i$ proche de 1), plus BF croit les données ; plus elle est jeune ($\hat p_i$ proche de 0), plus il croit l'a priori.** C'est de la crédibilité (section 2.4.4) avec comme poids la part payée. Le choix du ratio a priori compte donc surtout pour les années récentes, celles qui portent la provision.

La variante **Cape Cod** estime l'a priori **à partir des données** plutôt que de le fixer : $\hat\rho=\sum_iC_i\big/\sum_iP_i\hat p_i$ (le ratio sinistres sur primes moyen, ramené à un ultime), puis applique BF.

```python hide
tri_ch = pd.read_csv("donnees/triangle_choc.csv"); ver_ch = pd.read_csv("donnees/triangle_choc_verite.csv")
C_ch = triangle_cumule(tri_ch).values; I_ch = triangle_cumule(tri_ch, "paiement_incremental").values
V_ch = ver_ch.pivot(index="annee_survenance", columns="delai", values="paiement_cumule").values
prime_rc = tri_rc.groupby("annee_survenance")["prime_acquise"].first().values
prime_dom = tri_dom.groupby("annee_survenance")["prime_acquise"].first().values
prime_ch = tri_ch.groupby("annee_survenance")["prime_acquise"].first().values

def methodes(C, V, prime, prior, avec_queue):
    """Provisions totales (M€) de plusieurs méthodes, et provision réelle ; renvoie aussi le détail par année de CL, BF, CC."""
    f_ = facteurs_chain_ladder(C); pay = dernier_cumul(C)
    ft_ = facteur_queue(f_)[0] if avec_queue else 1.0
    _, u_cl0 = projeter(C, f_); _, u_cl1 = projeter(C, f_, ft_)
    ders = [int(np.max(np.where(~np.isnan(C[i]))[0])) for i in range(C.shape[0])]
    pct = np.array([1 / (np.prod(f_[d:]) * ft_) for d in ders])
    rho_cc = pay.sum() / (prime * pct).sum()
    u_bf = bornhuetter_ferguson(C, f_, prime, prior, ft_)
    u_cc = bornhuetter_ferguson(C, f_, prime, rho_cc, ft_)
    vrai = V[:, -1] - pay
    out = {"CL sans queue": (u_cl0 - pay), "CL avec queue": (u_cl1 - pay), "Bornhuetter-Ferguson": (u_bf - pay), "Cape Cod": (u_cc - pay), "réel": vrai}
    return out, ft_, rho_cc, pay, pct

res_rc, ft_rc, rho_cc_rc, pay_rc, pct_rc = methodes(C_rc, V_rc, prime_rc, 0.80, True)
res_dom, ft_dom, rho_cc_dom, pay_dom, pct_dom = methodes(C_dom, V_dom, prime_dom, 0.80, False)
res_ch, ft_ch, rho_cc_ch, pay_ch, pct_ch = methodes(C_ch, V_ch, prime_ch, 0.80, True)
rho_vrai_rc = V_rc[:, -1].sum() / prime_rc.sum(); rho_vrai_dom = V_dom[:, -1].sum() / prime_dom.sum()
tot = lambda d: {k: v.sum() / 1e6 for k, v in d.items()}
t_rc, t_dom, t_ch = tot(res_rc), tot(res_dom), tot(res_ch)
NUM("bf_rc", t_rc["Bornhuetter-Ferguson"]); NUM("cc_rc", t_rc["Cape Cod"]); NUM("rho_cc_rc", rho_cc_rc); NUM("rho_vrai_rc", rho_vrai_rc)
NUM("bf_dom", t_dom["Bornhuetter-Ferguson"]); NUM("cc_dom", t_dom["Cape Cod"]); NUM("rho_cc_dom", rho_cc_dom); NUM("rho_vrai_dom", rho_vrai_dom)
NUM("vrai_rc2", t_rc["réel"]); NUM("vrai_dom2", t_dom["réel"])
NUM("ecart_bf_rc", t_rc["Bornhuetter-Ferguson"] / t_rc["réel"] - 1); NUM("ecart_cc_rc", t_rc["Cape Cod"] / t_rc["réel"] - 1)
NUM("ecart_bf_dom", t_dom["Bornhuetter-Ferguson"] / t_dom["réel"] - 1); NUM("ecart_cc_dom", t_dom["Cape Cod"] / t_dom["réel"] - 1)
NUM("pct_9", pct_rc[9]); NUM("bf_9", res_rc["Bornhuetter-Ferguson"][9] / 1e6); NUM("cl_9", res_rc["CL avec queue"][9] / 1e6); NUM("vrai_9", res_rc["réel"][9] / 1e6)
```

Prenons un a priori **de plan** de 80 % pour les deux garanties, une valeur raisonnable *a priori* mais qui n'a jamais été confrontée aux réalisations. Les ratios réellement programmés sont, en moyenne, de {{rho_vrai_rc|pc0}} % pour la responsabilité civile (l'inflation des indemnités le tire au-dessus de l'hypothèse de tarification) et de {{rho_vrai_dom|pc0}} % pour les dommages. Le Cape Cod les retrouve : {{rho_cc_rc|pc0}} % et {{rho_cc_dom|pc0}} %.

Résultat, comparé aux paiements réels :

- **Responsabilité civile** (provision réelle : {{vrai_rc2|1}} M€) : BF avec l'a priori de 80 % donne {{bf_rc|1}} M€ ({{ecart_bf_rc|pcs0}} %), Cape Cod {{cc_rc|1}} M€ ({{ecart_cc_rc|pcs0}} %). L'a priori trop bas **entraîne BF vers le bas**, surtout sur les années récentes : pour 2024, BF donne {{bf_9|1}} M€ contre {{cl_9|1}} M€ pour le chain ladder (et {{vrai_9|1}} M€ réellement payés).
- **Dommages** (provision réelle : {{vrai_dom2|1}} M€) : BF avec 80 % donne {{bf_dom|1}} M€ ({{ecart_bf_dom|pcs0}} %), car l'a priori est ici **trop haut** ; Cape Cod, qui apprend le ratio dans les données, donne {{cc_dom|1}} M€ ({{ecart_cc_dom|pcs1}} %).

**BF n'est donc pas « meilleur » que le chain ladder : il est meilleur quand l'a priori est bon et les données bruitées, pire quand l'a priori est faux.** Son intérêt est d'être **stable** : une dérive du premier paiement n'emporte pas la provision. Le Cape Cod garde cette stabilité en se débarrassant du risque d'un a priori mal posé, au prix d'une hypothèse (le même ratio pour toutes les années, ce qui est faux ici à cause de l'inflation).

### 2.5.3 L'erreur de prédiction de Mack

Une provision est une **moyenne** d'une distribution ; l'écart-type de cette distribution est ce que mesure l'**erreur quadratique de prédiction** (MSEP). Mack (1993) a obtenu, sous ses hypothèses, une formule explicite pour celle de l'ultime d'une année de survenance $i$ qui a atteint le délai $d_i$ :
$$\widehat{\mathrm{MSEP}}(\hat U_i)=\hat U_i^{\,2}\sum_{k=d_i}^{J-1}\frac{\hat\sigma_k^2}{\hat f_k^{\,2}}\Bigl(\frac{1}{\hat C_{i,k}}+\frac{1}{\sum_{j}C_{j,k}}\Bigr),\qquad \hat\sigma_k^2=\frac{1}{n_k-1}\sum_jC_{j,k}\Bigl(\frac{C_{j,k+1}}{C_{j,k}}-\hat f_k\Bigr)^2,$$
où $n_k$ est le nombre d'années disponibles au délai $k$ et la dernière somme porte sur les années utilisées pour estimer $\hat f_k$. Deux termes, deux sources d'incertitude : $1/\hat C_{i,k}$ est la **variance de processus** (le hasard pur des paiements futurs, plus fort quand le montant est petit) et $1/\sum_jC_{j,k}$ la **variance d'estimation** (les facteurs sont estimés avec une précision limitée). Pour le **total** de toutes les années, il faut ajouter les covariances entre années, qui existent parce que **les mêmes facteurs estimés** servent à toutes les lignes.

```python hide
mk, se_tot, sig2 = mack(C_rc)
NUM("mack_se", se_tot / 1e6); NUM("mack_cv", se_tot / res_cl.sum())
NUM("mack_2024", mk["erreur_type"].iloc[9] / 1e6)
cvs = (mk["erreur_type"] / mk["reserve"]).iloc[2:]
NUM("cv_min", cvs.min()); NUM("cv_max", cvs.max())
ecart_vrai = (res_vrai.sum() - res_cl.sum()) / se_tot
ecart_vrai_ft = (res_vrai.sum() - (ult_ft - paye).sum()) / se_tot
NUM("z_vrai_sq", ecart_vrai); NUM("z_vrai_ft", abs(ecart_vrai_ft))
mk_dom, se_dom, _ = mack(C_dom)
NUM("mack_se_dom", se_dom / 1e6); NUM("mack_cv_dom", se_dom / (np.nansum(res_dom["CL sans queue"])))
tab_mk = pd.DataFrame({"réserve": mk["reserve"].values / 1e6, "erreur-type": mk["erreur_type"].values / 1e6,
                       "coefficient de variation": mk["erreur_type"].values / np.where(mk["reserve"].values == 0, np.nan, mk["reserve"].values)}, index=annees)
tab_mk.loc["total"] = [mk["reserve"].sum() / 1e6, se_tot / 1e6, se_tot / mk["reserve"].sum()]
```

```python hide-code
print(tab_mk.iloc[2:].to_string(float_format=lambda v: f"{v:.3f}"))
```

(Les années 2015 et 2016, dont la provision est quasi nulle, sont omises du tableau.) Pour la responsabilité civile, l'erreur-type de la provision totale est de **{{mack_se|1}} M€**, soit {{mack_cv|pc1}} % de la provision : un chiffre rassurant. Par année, le coefficient de variation va de {{cv_min|pc0}} % à {{cv_max|pc0}} % (années 2017 à 2024) ; la dernière année, à elle seule, contribue pour {{mack_2024|1}} M€ à l'erreur-type. Pour la garantie à développement court, l'erreur-type vaut {{mack_se_dom|1}} M€ pour une provision de {{res_d|1}} M€ ({{mack_cv_dom|pc0}} %).

Maintenant, la comparaison avec la réalité, qui donne à ce chiffre sa juste signification : la provision réelle dépasse celle du chain ladder sans queue de **{{z_vrai_sq|1}} erreurs-types de Mack**. Autrement dit, **l'erreur réellement commise est sans commune mesure avec l'erreur-type annoncée**, parce que la formule de Mack ne couvre que le hasard des paiements et l'estimation des facteurs **sous l'hypothèse que le schéma observé se prolonge** : elle ne couvre ni la queue ni les ruptures. Avec la queue extrapolée, l'écart tombe à {{z_vrai_ft|1}} erreur-type.

> ⚠️ **L'erreur de Mack est un plancher.** Elle mesure l'incertitude *statistique conditionnelle au modèle*. L'incertitude **de modèle** (queue, rupture de schéma, choix de la méthode) lui est généralement bien supérieure. Les directions des risques en tiennent compte en élargissant ces intervalles ou en comparant plusieurs méthodes (section 2.5.6).

### 2.5.4 Le bootstrap de l'« overdispersed Poisson »

Mack donne un écart-type, pas une distribution. Pour obtenir **tous les quantiles** (le 75ᵉ centile d'une provision prudente, le 99,5ᵉ de la réglementation, chapitre 4), on simule. Le **bootstrap de England et Verrall** repose sur le fait que le chain ladder est exactement l'estimation d'un modèle de Poisson sur-dispersé (*overdispersed Poisson*, ODP) pour les paiements **incrémentaux** : $E[Y_{ij}]=\exp(a_i+b_j)=\mu_{ij}$, $\mathrm{Var}(Y_{ij})=\phi\,\mu_{ij}$. Le GLM de Poisson à effet ligne et effet colonne redonne la même provision que le chain ladder.

L'algorithme tient en cinq étapes : (1) ajuster le GLM sur le triangle observé, obtenir les $\hat\mu_{ij}$ ; (2) calculer les **résidus de Pearson** $r_{ij}=(y_{ij}-\hat\mu_{ij})/\sqrt{\hat\mu_{ij}}$, corrigés du nombre de paramètres ; (3) **rééchantillonner** ces résidus avec remise et en déduire un triangle pseudo-observé $y^*_{ij}=\hat\mu_{ij}+r^*_{ij}\sqrt{\hat\mu_{ij}}$ ; (4) **réajuster** le modèle sur $y^*$ (incertitude d'estimation) ; (5) **simuler** les paiements futurs par une loi de Poisson sur-dispersée de moyenne $\hat\mu^*_{ij}$ (incertitude de processus), et cumuler. On répète 1 000 fois.

```python hide
sims, centrale, phi_odp = bootstrap_odp(I_rc, n_boot=1000, graine=1)
q = np.percentile(sims, [5, 50, 75, 95, 99.5]) / 1e6
NUM("odp_centrale", centrale / 1e6); NUM("odp_ecart_cl", abs(centrale - res_cl.sum()) / res_cl.sum()); NUM("odp_phi", phi_odp)
NUM("odp_sd", sims.std() / 1e6); NUM("odp_q5", q[0]); NUM("odp_q50", q[1]); NUM("odp_q75", q[2]); NUM("odp_q95", q[3]); NUM("odp_q995", q[4])
NUM("odp_pvrai", (sims < res_vrai.sum()).mean())
fig, ax = plt.subplots(figsize=(6.6, 3.9))
ax.hist(sims / 1e6, bins=40, color=BLEU, alpha=0.75)
ymax = ax.get_ylim()[1]
for val, c, txt, ha in ((res_cl.sum() / 1e6, ENCRE, "chain ladder", "right"), (q[4], ROUGE, "99,5 %", "left"), (res_vrai.sum() / 1e6, ORANGE, "réel", "left")):
    ax.axvline(val, color=c, lw=1.5, ls="--" if txt == "réel" else "-"); ax.text(val, ymax * (0.95 if txt != "99,5 %" else 0.8), (" " if ha == "left" else "") + txt + (" " if ha == "right" else ""), color=c, fontsize=9, ha=ha, va="top")
ax.set_xlabel("provision totale simulée (M€)"); ax.set_ylabel("nombre de simulations"); ax.set_title("Bootstrap ODP : distribution de la provision (RC)")
fig.tight_layout(); fig.savefig("figures/ch02-bootstrap.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

![Distribution de la provision totale de responsabilité civile obtenue par bootstrap de l'overdispersed Poisson (1 000 simulations) ; trait noir : provision du chain ladder ; trait rouge : quantile à 99,5 % ; trait orange pointillé : provision réellement payée ensuite.](figures/ch02-bootstrap.png)

La provision centrale du modèle ODP vaut {{odp_centrale|1}} M€, **identique à celle du chain ladder** (écart de {{odp_ecart_cl|pc3}} %), ce qui vérifie l'équivalence annoncée. L'écart-type de la distribution simulée est de {{odp_sd|1}} M€ (contre {{mack_se|1}} M€ pour Mack : les deux méthodes mesurent la même chose et s'accordent). La dispersion estimée est $\hat\phi\approx{{odp_phi|int}}$ € (la programmation avait fixé 20 000 €). Les quantiles sont : médiane {{odp_q50|1}} M€, 75ᵉ centile {{odp_q75|1}} M€, 95ᵉ {{odp_q95|1}} M€, 99,5ᵉ {{odp_q995|1}} M€. La **provision réellement payée** ({{res_vrai_m|1}} M€) se place au {{odp_pvrai|pc0}}ᵉ centile de cette distribution : elle est dans l'étendue, mais loin du centre, ce qui est cohérent avec ce que nous savons (la queue n'est pas dans le triangle).

```python hide
NUM("res_vrai_m", res_vrai.sum() / 1e6)
```

> 🧪 **À quoi servent les quantiles d'une provision ?** À trois choses : (1) fixer une provision **prudente** (au 75ᵉ centile, par exemple) ; (2) mesurer le **risque de provisionnement** que Solvabilité II demande de couvrir par du capital (la différence entre le 99,5ᵉ centile et la moyenne, chapitre 4, section 4.2) ; (3) comparer des garanties ou des méthodes. Un bootstrap bien fait sur un triangle de dix ans reste un outil **grossier** : un seul schéma de résidus, des années supposées indépendantes, une queue fixée.

### 2.5.5 Quand l'hypothèse de calendrier échoue : le triangle « choc »

Le troisième triangle a été fabriqué avec un **choc de +12 %** sur tous les paiements de l'année calendaire 2022 (une diagonale entière), en plus de l'inflation habituelle. C'est exactement le type d'événement qui viole l'hypothèse de Mack. Comment le détecter ?

**Les résidus par année calendaire.** On ajuste le modèle ODP, on calcule les résidus de Pearson de chaque cellule, et on les range **par diagonale**. Si le schéma est stable, les résidus d'une diagonale n'ont aucune raison d'être de même signe.

```python hide
def residus(I):
    n, m = I.shape
    ii, jj = np.indices((n, m)); obs = ~np.isnan(I)
    X = np.zeros((obs.sum(), n + m - 1))
    X[np.arange(obs.sum()), ii[obs]] = 1
    mc = jj[obs] > 0
    X[np.arange(obs.sum())[mc], n + jj[obs][mc] - 1] = 1
    y = I[obs]; mod = sm.GLM(y, X, family=sm.families.Poisson()).fit()
    mu_ = mod.fittedvalues; phi_ = float(np.sum((y - mu_) ** 2 / mu_) / (len(y) - len(mod.params)))
    R = np.full((n, m), np.nan); R[obs] = (y - mu_) / np.sqrt(phi_ * mu_)
    return R
R_rc, R_ch = residus(I_rc), residus(I_ch)
def par_diag(R):
    n, m = R.shape
    return np.array([np.nanmean([R[i, d - i] for i in range(n) if 0 <= d - i < m and not np.isnan(R[i, d - i])]) for d in range(n)])
d_rc, d_ch = par_diag(R_rc), par_diag(R_ch)
NUM("res_diag_choc", d_ch[7]); NUM("res_diag_rc_max", np.max(np.abs(d_rc[1:])))
NUM("res_diag_choc_autres", np.max(np.abs(np.delete(d_ch, 7)[1:])))
fig, ax = plt.subplots(1, 2, figsize=(10.5, 3.9), sharey=True)
for a_, R_, tit in ((ax[0], R_rc, "Triangle RC (stable)"), (ax[1], R_ch, "Triangle « choc »")):
    im = a_.imshow(R_, cmap=style.DIV, vmin=-3, vmax=3, aspect="auto")
    a_.set_xticks(range(R_.shape[1])); a_.set_yticks(range(R_.shape[0])); a_.set_yticklabels([str(a) for a in annees])
    a_.set_xlabel("délai de développement"); a_.set_title(tit)
ax[0].set_ylabel("année de survenance")
for i in range(10):
    if 0 <= 7 - i <= 9:
        ax[1].plot(7 - i, i, ".", color=ENCRE, ms=4)          # cellules de la diagonale du choc
fig.colorbar(im, ax=ax, shrink=0.8, label="résidu de Pearson")
fig.savefig("figures/ch02-residus.png", dpi=200, bbox_inches="tight"); plt.close(fig)
mk_ch, se_ch, _ = mack(C_ch)
NUM("mack_se_ch", se_ch / 1e6); NUM("res_ch_cl", t_ch["CL sans queue"]); NUM("res_ch_ft", t_ch["CL avec queue"]); NUM("res_ch_vrai", t_ch["réel"])
err_ay = (res_ch["CL avec queue"] - res_ch["réel"]) / np.maximum(res_ch["réel"], 1) 
NUM("ch_err_max", np.max(np.abs(err_ay[3:]))); NUM("ch_ft_exces", t_ch["CL avec queue"] / t_ch["réel"] - 1)
```

![Résidus de Pearson du modèle ODP, cellule par cellule, pour le triangle stable (à gauche) et pour le triangle avec choc calendaire (à droite) ; rouge : paiement supérieur au modèle, bleu : inférieur. La diagonale du choc (année calendaire 2022, repérée par des points noirs) apparaît comme une bande rougeâtre.](figures/ch02-residus.png)

Sur le triangle stable, le résidu moyen d'une diagonale ne dépasse pas {{res_diag_rc_max|2}} en valeur absolue ; sur le triangle « choc », la diagonale 2022 a un résidu moyen de **{{res_diag_choc|2}}**, et aucune autre ne dépasse {{res_diag_choc_autres|2}}. **Le choc se voit en une image, bien avant de se voir dans la provision.** Deuxième symptôme : l'erreur de Mack du total passe de {{mack_se|1}} M€ (triangle stable) à {{mack_se_ch|1}} M€ (triangle choc) : le modèle perçoit un désordre dans les facteurs sans le localiser.

**Et la provision ?** Sans queue, le chain ladder donne {{res_ch_cl|1}} M€ pour {{res_ch_vrai|1}} M€ réellement payés : presque juste. C'est un effet de **compensation** : le choc de 2022 a gonflé les facteurs et les paiements cumulés, ce qui pousse la provision vers le haut, tandis que l'absence de queue la tire vers le bas ; les deux effets s'annulent presque. La preuve que ce n'est pas la méthode qui est bonne : dès que l'on ajoute la queue extrapolée, qui amplifie les facteurs gonflés, la provision monte à {{res_ch_ft|1}} M€, soit {{ch_ft_exces|pc0}} % de trop (contre {{ecart_ft_abs|pc0}} % sur le triangle stable). Et, par année, les écarts atteignent {{ch_err_max|pc0}} %. Une compensation de ce genre est une **chance**, pas une propriété de la méthode.

Pour voir le dommage lorsque la chance disparaît, déplaçons le choc sur **la dernière diagonale** du triangle stable (le paiement de l'année en cours est majoré de 12 %, rien ne se produit ensuite) :

```python hide
I_alt = I_rc.copy()
n_, m_ = I_alt.shape
for i in range(n_):
    j = n_ - 1 - i
    I_alt[i, j] *= 1.12
C_alt = np.cumsum(np.where(np.isnan(I_alt), 0, I_alt), axis=1); C_alt[np.isnan(I_alt)] = np.nan
f_alt = facteurs_chain_ladder(C_alt); ft_alt = facteur_queue(f_alt)[0]
_, u_alt = projeter(C_alt, f_alt, ft_alt); pay_alt = dernier_cumul(C_alt)
res_alt = (u_alt - pay_alt).sum()
NUM("alt_res", res_alt / 1e6); NUM("alt_exces", res_alt / res_vrai.sum() - 1)
# correction : on dégonfle la diagonale connue du choc
I_fix = I_alt.copy()
for i in range(n_):
    I_fix[i, n_ - 1 - i] /= 1.12
C_fix = np.cumsum(np.where(np.isnan(I_fix), 0, I_fix), axis=1); C_fix[np.isnan(I_fix)] = np.nan
f_fix = facteurs_chain_ladder(C_fix); ft_fix = facteur_queue(f_fix)[0]
_, u_fix = projeter(C_fix, f_fix, ft_fix); res_fix = (u_fix - dernier_cumul(C_fix)).sum()
NUM("fix_res", res_fix / 1e6); NUM("fix_exces", res_fix / res_vrai.sum() - 1)
```

La provision du chain ladder passe à {{alt_res|1}} M€, soit {{alt_exces|pc0}} % **de plus** que la provision réellement payée : le modèle a pris un accident calendaire pour une tendance et l'a propagé à toute la provision. Corrigée du choc (si on le connaît et que l'on dégonfle la diagonale), elle revient à {{fix_res|1}} M€ ({{fix_exces|pc0}} % d'écart). **L'enjeu n'est pas la méthode mais la connaissance du portefeuille** : savoir qu'une diagonale est anormale vaut plus que n'importe quelle sophistication. Les remèdes sont de la même famille : exclure ou dégonfler la diagonale douteuse des facteurs, ajouter un **effet calendaire** au GLM (en acceptant de le prolonger), ou changer de méthode (BF, qui est moins sensible puisqu'il s'appuie moins sur le dernier cumul).

### 2.5.6 Comparer les méthodes aux paiements réels

Résumons ce que chaque méthode donne, pour les trois triangles, avec l'écart par rapport à la provision réellement payée (en %) :

```python hide
noms = ["CL sans queue", "CL avec queue", "Bornhuetter-Ferguson", "Cape Cod"]
lignes = []
for nom in noms:
    lignes.append((nom, f"{t_rc[nom]:.1f} ({100 * (t_rc[nom] / t_rc['réel'] - 1):+.0f} %)", f"{t_dom[nom]:.1f} ({100 * (t_dom[nom] / t_dom['réel'] - 1):+.0f} %)", f"{t_ch[nom]:.1f} ({100 * (t_ch[nom] / t_ch['réel'] - 1):+.0f} %)"))
lignes.append(("médiane du bootstrap ODP (RC)", f"{q[1]:.1f} ({100 * (q[1] / t_rc['réel'] - 1):+.0f} %)", "", ""))
lignes.append(("provision réellement payée", f"{t_rc['réel']:.1f}", f"{t_dom['réel']:.1f}", f"{t_ch['réel']:.1f}"))
tab_cmp = pd.DataFrame(lignes, columns=["méthode (M€)", "RC", "dommages", "choc"]).set_index("méthode (M€)")
ec = lambda t, nom: t[nom] / t["réel"] - 1
for cle, t_, nom in (("ec_cc_rc", t_rc, "Cape Cod"), ("ec_cc_dom", t_dom, "Cape Cod"), ("ec_cc_ch", t_ch, "Cape Cod"), ("ec_cl0_dom", t_dom, "CL sans queue"),
                     ("ec_cl0_rc", t_rc, "CL sans queue"), ("ec_clq_rc", t_rc, "CL avec queue"), ("ec_clq_ch", t_ch, "CL avec queue"),
                     ("ec_bf_rc", t_rc, "Bornhuetter-Ferguson"), ("ec_bf_dom", t_dom, "Bornhuetter-Ferguson"), ("ec_bf_ch", t_ch, "Bornhuetter-Ferguson")):
    NUM(cle, ec(t_, nom))
```

```python hide-code
print(tab_cmp.to_string())
```

Trois enseignements. **Cape Cod est ici le plus régulier** (écarts de {{ec_cc_rc|pcs0}} %, {{ec_cc_dom|pcs0}} % et {{ec_cc_ch|pcs0}} %) : son hypothèse (un même ratio sinistres sur primes pour toutes les années) est presque vraie dans ces données, et il intègre la queue sans la deviner ; dans un portefeuille dont le ratio change d'une année à l'autre, il perdrait cet avantage. **Le chain ladder** est excellent quand la queue est courte (dommages : {{ec_cl0_dom|pcs0}} %) et dépend entièrement de la queue quand elle ne l'est pas : de {{ec_cl0_rc|pcs0}} % sans queue à {{ec_clq_rc|pcs0}} % avec la queue extrapolée en responsabilité civile, et {{ec_clq_ch|pcs0}} % sur le triangle choc. **BF avec un a priori faux est la pire des méthodes** ({{ec_bf_rc|pcs0}} %, {{ec_bf_dom|pcs0}} % et {{ec_bf_ch|pcs0}} %) : elle est stable, mais elle est stable autour du mauvais chiffre.

La conclusion pratique n'est pas « utilisez Cape Cod » : c'est que **les écarts les plus grands viennent des hypothèses (queue, a priori, stabilité du calendrier), pas des estimateurs**. D'où la discipline : appliquer **plusieurs méthodes**, expliquer leurs écarts, regarder les résidus, puis fixer sa provision avec un jugement documenté. C'est ce que les actuaires appellent un « meilleur estimé » (*best estimate*), et c'est aussi ce que demande Solvabilité II (chapitre 4, section 4.2).

> ✅ **À retenir.**
> - **BF** remplace l'extrapolation du dernier cumul par un a priori ; c'est une moyenne pondérée par la part payée entre chain ladder et a priori. Un a priori faux donne une provision fausse ; **Cape Cod** apprend l'a priori dans les données.
> - La formule de **Mack** donne l'erreur de prédiction du chain ladder (processus + estimation) ; c'est un **plancher** : elle ignore la queue et les ruptures de schéma.
> - Le **bootstrap ODP** redonne la provision du chain ladder et sa **distribution** complète ; ses quantiles servent à la prudence et au capital.
> - Un **choc calendaire** (diagonale) se voit dans les résidus par diagonale ; il peut s'annuler sur le total et se payer ailleurs. La connaissance du portefeuille prime sur la méthode.
> - Comparer plusieurs méthodes et expliquer leurs écarts est la pratique, pas le choix d'une méthode unique.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.8 et exercices 2.11 à 2.13 (Bornhuetter–Ferguson, erreur de Mack, bootstrap, diagnostic d'un choc calendaire).
