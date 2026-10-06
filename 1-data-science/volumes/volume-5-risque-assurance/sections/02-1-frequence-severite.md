## 2.1 Modèles de fréquence et de sévérité

Un contrat d'assurance automobile produit, sur une année, soit rien (le plus souvent), soit un sinistre, soit rarement plusieurs. Quand il y a sinistre, son montant va de quelques centaines d'euros à plusieurs millions. Cette section **sépare ces deux sources d'aléa**, parce qu'elles n'obéissent ni aux mêmes lois ni aux mêmes facteurs de risque, puis les **recompose** pour décrire ce que le portefeuille coûtera sur une année.

### 2.1.1 Le coût d'un contrat : un nombre, puis un montant

Notons $N$ le nombre de sinistres d'un contrat sur la période et $X_1,\dots,X_N$ leurs montants. Le **coût total** est
$$S=\sum_{k=1}^{N}X_k,\qquad S=0\ \text{si } N=0.$$
C'est la structure du **modèle collectif** : $N$ est la *fréquence* (une variable de comptage), les $X_k$ forment la *sévérité* (des montants positifs). On suppose d'ordinaire que les $X_k$ sont **indépendants entre eux et indépendants de $N$**, et de même loi. Ces hypothèses sont fausses de mille façons (un orage provoque beaucoup de sinistres à la fois), mais elles donnent un point de départ calculable, et nous verrons à la fin de la section ce qu'elles coûtent.

**Un exemple à la main.** Cinq contrats, une année chacun :

| Contrat | Sinistres $N$ | Montants (€) | Coût $S$ (€) |
|---|---|---|---|
| 1 | 0 | — | 0 |
| 2 | 1 | 1 800 | 1 800 |
| 3 | 0 | — | 0 |
| 4 | 2 | 900 ; 2 400 | 3 300 |
| 5 | 0 | — | 0 |

La fréquence moyenne est $3/5=0{,}6$ sinistre par contrat et par an. La sévérité moyenne est $(1\,800+900+2\,400)/3=1\,700$ €. Le coût moyen par contrat est $5\,100/5=1\,020$ €, et l'on retrouve bien $0{,}6\times1\,700=1\,020$ : **le coût moyen est le produit de la fréquence moyenne par la sévérité moyenne**. Cette égalité, démontrée plus bas, est le fondement de toute la tarification.

Voyons nos données. Chaque ligne de `pol` est un contrat sur une année, avec son **exposition** (la fraction de l'année pendant laquelle le contrat a été en vigueur : 0,5 pour un contrat résilié en juin).

```python
resume = pol.groupby("annee").agg(contrats=("id_police", "size"), exposition=("exposition", "sum"),
                                  sinistres=("nb_sinistres", "sum"))
resume["frequence"] = resume["sinistres"] / resume["exposition"]     # sinistres par année d'exposition
print(resume.round(3))
```
<!--sortie-->
```text
       contrats  exposition  sinistres  frequence
annee                                            
2022      30244   26199.870       1679      0.064
2023      32741   28320.718       1907      0.067
2024      37015   32080.943       2136      0.067
```

Les années-contrats d'exposition augmentent d'une année à l'autre (le portefeuille grandit), et la fréquence reste proche de 6,6 % : c'est ce qu'on attend d'un portefeuille stable.

### 2.1.2 Compter les sinistres : Poisson et exposition

Le modèle de référence pour un nombre de sinistres est la **loi de Poisson** :
$$P(N=k)=e^{-\mu}\frac{\mu^k}{k!},\qquad E[N]=\mathrm{Var}(N)=\mu.$$
Elle a une justification : si des sinistres surviennent indépendamment les uns des autres, à un rythme constant, le nombre de sinistres sur une durée donnée suit une loi de Poisson. Pour un contrat d'exposition $e_i$ et de **taux annuel** $\lambda$, on pose donc $N_i\sim\mathrm{Poisson}(e_i\lambda)$ : un contrat couvert six mois a deux fois moins de chances d'avoir un sinistre qu'un contrat d'un an. L'exposition entre dans le modèle comme un **décalage** (en anglais *offset*) : $\ln\mu_i=\ln e_i+\ln\lambda$, c'est-à-dire une variable explicative dont le coefficient est imposé égal à 1.

> 📐 **Estimateur du taux.** La log-vraisemblance de $n$ contrats est $\ell(\lambda)=\sum_i\bigl[N_i\ln(e_i\lambda)-e_i\lambda-\ln N_i!\bigr]$. En dérivant, $\ell'(\lambda)=\sum_i N_i/\lambda-\sum_i e_i=0$, d'où
> $$\hat\lambda=\frac{\sum_i N_i}{\sum_i e_i}.$$
> Le taux estimé est le **nombre total de sinistres divisé par l'exposition totale**, pas par le nombre de contrats. L'information de Fisher vaut $\sum_i e_i/\lambda$, donc $\mathrm{Var}(\hat\lambda)\approx\lambda/\sum_i e_i$ : l'incertitude ne dépend que de l'exposition totale.

Sur nos données, $\hat\lambda=6{,}61$ % par année d'exposition, avec une erreur-type de 0,09 point (pour une exposition totale de 86 602 années). Si l'on avait divisé par le nombre de contrats plutôt que par l'exposition, on aurait obtenu 5,72 %, un taux **sous-estimé** de 13 % parce que les contrats incomplets comptent pour une année entière : une erreur classique, silencieuse, et qui fausse le prix.

> ⚠️ **Exposition ou nombre de contrats ?** Le dénominateur d'une fréquence est la durée de couverture, pas le nombre de lignes. Un tarif construit avec des fréquences « par contrat » sous-estime systématiquement le risque quand le portefeuille contient beaucoup de contrats incomplets (nouvelles affaires en cours d'année, résiliations).

### 2.1.3 Quand la variance dépasse la moyenne : la binomiale négative

La loi de Poisson impose $\mathrm{Var}(N)=E[N]$. Or, dans un portefeuille réel, deux contrats de mêmes caractéristiques observables n'ont pas le même risque : l'un conduit prudemment, l'autre non. Ce risque **non observé** ajoute de la variabilité. Modélisons-le par un facteur aléatoire $\Theta$ de moyenne 1 : sachant $\Theta$, le nombre de sinistres est Poisson de moyenne $\mu\Theta$. Si $\Theta$ suit une loi Gamma de moyenne 1 et de variance $\alpha$, la loi de $N$ devient une **binomiale négative**, et l'on a :
$$E[N]=\mu,\qquad \mathrm{Var}(N)=E[\mathrm{Var}(N\mid\Theta)]+\mathrm{Var}(E[N\mid\Theta])=\mu+\alpha\mu^2.$$

> 📐 **Poisson–Gamma = binomiale négative.** Posons $r=1/\alpha$ ; $\Theta\sim\mathrm{Gamma}(r,\text{taux } r)$. Alors
> $$P(N=k)=\int_0^\infty e^{-\mu\theta}\frac{(\mu\theta)^k}{k!}\,\frac{r^r\theta^{r-1}e^{-r\theta}}{\Gamma(r)}\,d\theta=\frac{\Gamma(k+r)}{k!\,\Gamma(r)}\Bigl(\frac{r}{r+\mu}\Bigr)^{r}\Bigl(\frac{\mu}{r+\mu}\Bigr)^{k},$$
> la loi binomiale négative de paramètres $r$ et $p=r/(r+\mu)$. Quand $\alpha\to0$ (pas d'hétérogénéité), on retrouve la loi de Poisson.

Une vérification numérique rassure : en simulant un million de contrats avec $\mu=1$ et $\alpha=0{,}5$, la variance empirique vaut 1,50 pour une valeur théorique de $\mu+\alpha\mu^2=1{,}5$.

Quelle est l'ampleur du phénomène sur notre portefeuille ? Le taux de sinistres étant faible, la sur-dispersion y est discrète : le rapport variance sur moyenne d'un contrat vaut $1+\alpha\mu\approx1+0{,}4\times0{,}066$, soit environ $1{,}03$. Un modèle de Poisson avec les variables explicatives donne une **dispersion de Pearson** de 1,027 ; un modèle binomial négatif estime $\hat\alpha=0{,}47$ avec une erreur-type de 0,09. L'estimation est imprécise (la variance est un moment d'ordre deux) mais elle écarte nettement zéro. La **vérité programmée** est $\alpha=0{,}4$ : l'estimation en est à moins de deux erreurs-types.

Pourquoi s'en préoccuper si l'effet est si discret ? Parce qu'il se paie dans les **queues** : les contrats à plusieurs sinistres sont bien plus fréquents que ne le prévoit Poisson.

```python hide-code
Fcomptage = ("nb_sinistres ~ C(classe_age, Treatment('40-49')) + puissance + C(zone, Treatment('Zone C'))"
             " + bonus_malus + C(usage) + C(carburant) + age_vehicule")
mod_p = smf.glm(Fcomptage, pol, family=sm.families.Poisson(), offset=np.log(pol["exposition"])).fit()
mod_nb = smf.negativebinomial(Fcomptage, pol, offset=np.log(pol["exposition"])).fit(disp=0)
mu = mod_p.fittedvalues.values
alpha = float(mod_nb.params["alpha"]); r = 1 / alpha
obs = pol["nb_sinistres"].clip(upper=3).value_counts().sort_index()
th_p = [stats.poisson.pmf(k, mu).sum() for k in range(3)]; th_p.append(len(mu) - sum(th_p))
th_n = [stats.nbinom.pmf(k, r, r / (r + mu)).sum() for k in range(3)]; th_n.append(len(mu) - sum(th_n))
tab = pd.DataFrame({"observé": obs.values, "Poisson": np.round(th_p, 1), "binomiale négative": np.round(th_n, 1)},
                   index=["0", "1", "2", "3 et plus"])
print(tab)
```
<!--sortie-->
```text
           observé  Poisson  binomiale négative
0            94559  94471.3             94556.0
1             5168   5340.7              5180.0
2              265    183.1               250.9
3 et plus        8      5.0                13.1
```

```python hide
phi = float(mod_p.pearson_chi2 / mod_p.df_resid)
NUM("phi_pearson", phi); NUM("alpha_nb", alpha); NUM("alpha_se", float(mod_nb.bse["alpha"]))
NUM("deux_obs", int(obs.get(2, 0))); NUM("deux_poisson", th_p[2]); NUM("deux_nb", th_n[2])
NUM("trois_obs", int(obs.get(3, 0))); NUM("trois_poisson", th_p[3]); NUM("trois_nb", th_n[3])
rng = np.random.default_rng(0)
theta = rng.gamma(2.0, 0.5, 1_000_000)          # moyenne 1, variance 0,5
NUM("var_sim", float(rng.poisson(theta).var()))
lam_hat = pol["nb_sinistres"].sum() / pol["exposition"].sum()
NUM("freq", lam_hat); NUM("se_freq", np.sqrt(lam_hat / pol["exposition"].sum()))
NUM("expo", pol["exposition"].sum()); NUM("freq_contrat", pol["nb_sinistres"].sum() / len(pol))
NUM("biais_exp", 1 - (pol["nb_sinistres"].sum() / len(pol)) / lam_hat)
NUM("sinistres_total", int(pol["nb_sinistres"].sum()))
```
<!--sortie-->
```text
NUM phi_pearson 1.0266522409733678
NUM alpha_nb 0.474023236608274
NUM alpha_se 0.08984073028959412
NUM deux_obs 265
NUM deux_poisson 183.05005415719904
NUM deux_nb 250.92562742686846
NUM trois_obs 8
NUM trois_poisson 5.0420869472727645
NUM trois_nb 13.139254667432397
NUM var_sim 1.5030294464639997
NUM freq 0.06607273490349727
NUM se_freq 0.0008734707310926153
NUM expo 86601.53099999999
NUM freq_contrat 0.05722
NUM biais_exp 0.13398469000000013
NUM sinistres_total 5722
```

Le tableau compare, parmi 100 000 contrats, le nombre de contrats ayant 0, 1, 2 ou 3 sinistres et plus avec ce que prévoit chaque modèle (en utilisant les moyennes ajustées contrat par contrat) : Poisson prévoit 183,1 contrats à deux sinistres, la binomiale négative 250,9, et l'on en observe 265. À trois sinistres ou plus : 5,0, 13,1 et 8 observés. Les écarts sont modestes en valeur absolue mais systématiques : **Poisson sous-estime les contrats à sinistres multiples**, et la binomiale négative les rattrape.

> 🧪 **Zéros en excès ?** On pense parfois à des modèles « à excès de zéros » quand il y a beaucoup de contrats sans sinistre. Ici le tableau montre que les zéros sont correctement prévus par les deux lois (la masse en zéro est portée par le faible taux de sinistres, pas par une population de contrats « immunisés »). Un modèle à inflation de zéros n'aurait rien apporté. À réserver aux cas où le diagnostic le justifie (volume II, section 2.6).

### 2.1.4 La sévérité : des montants très asymétriques

Passons aux montants. Les sinistres sont ici de deux natures : **matériels** (une carrosserie) et **corporels** (une personne blessée). Le tableau, en euros de 2024, donne l'effectif, la moyenne, la médiane et le maximum de chaque type.

```python hide-code
tab = sin.groupby("type")["rev"].agg(effectif="count", moyenne="mean", mediane="median", maximum="max").round(0).astype(int)
print(tab)
```
<!--sortie-->
```text
          effectif  moyenne  mediane  maximum
type                                         
corporel       576    55383    10315  2576725
materiel      5146     2733     2338    16694
```

Deux phrases résument le tableau. **Pour les sinistres matériels**, moyenne et médiane sont voisines (2 733 et 2 338 €) : la loi est modérément asymétrique. **Pour les sinistres corporels**, la moyenne (55 383 €) est **plus de cinq fois la médiane** (10 315 €) : quelques sinistres énormes tirent la moyenne vers le haut, jusqu'à 2 576 725 € pour le plus grand. Dans un tel cas, **la moyenne est instable** : retirer le sinistre le plus coûteux d'une année la fait varier de plusieurs points.

```python hide
mat = sin[sin["type"] == "materiel"]; cor = sin[sin["type"] == "corporel"]
NUM("moy_mat", mat["rev"].mean()); NUM("med_mat", mat["rev"].median())
NUM("moy_cor", cor["rev"].mean()); NUM("med_cor", cor["rev"].median()); NUM("max_cor", cor["rev"].max())
NUM("part_cor", len(cor) / len(sin))
# Gamma de moyenne dépendant des variables : la forme est l'inverse de la dispersion
mg = smf.glm("montant ~ puissance + C(zone, Treatment('Zone C')) + I(annee - 2022)", sin[sin["type"] == "materiel"],
             family=sm.families.Gamma(sm.families.links.Log())).fit(scale="X2")
NUM("forme_mat", 1 / mg.scale); NUM("coef_puiss", mg.params["puissance"]); NUM("infl_est", np.exp(mg.params["I(annee - 2022)"]) - 1)
NUM("cv_mat", float(np.sqrt(mg.scale)))
```
<!--sortie-->
```text
NUM moy_mat 2732.7612772638945
NUM med_mat 2338.48
NUM moy_cor 55383.07720555556
NUM med_cor 10314.5696
NUM max_cor 2576724.8000000003
NUM part_cor 0.10066410346032856
NUM forme_mat 2.3379018128411446
NUM coef_puiss 0.049992733864592166
NUM infl_est 0.04425063115118011
NUM cv_mat 0.6540137305799532
```

La loi **Gamma** convient bien aux sinistres matériels : elle est positive, asymétrique, et à moyenne $\mu$ et forme $k$ elle a pour variance $\mu^2/k$, donc un **coefficient de variation** constant $1/\sqrt k$. Un Gamma de moyenne dépendant des variables est justement le modèle linéaire généralisé de sévérité (section 2.2). Sur les sinistres matériels, la forme estimée est $\hat k=2{,}34$ (coefficient de variation 0,65) ; la forme programmée est 2,5. Le coefficient de la puissance est 0,050 (valeur programmée : 0,05) et l'inflation estimée atteint 4,4 % par an (valeur programmée : 4 %).

Pour les sinistres corporels, aucune loi usuelle ne tient d'un bout à l'autre : le corps de la distribution ressemble à une lognormale, mais les grands montants s'étirent beaucoup plus que ne le permet une lognormale. Deux outils décrivent ce comportement.

**Le graphique des montants en échelle logarithmique** montre les deux populations : les sinistres matériels se concentrent entre 1 000 et 10 000 €, les corporels s'étalent de quelques dizaines d'euros à plusieurs millions.

**La fonction d'excès moyen** $e(u)=E[X-u\mid X>u]$ mesure, pour un seuil $u$, ce que l'on perd *en moyenne au-delà du seuil*. Pour une loi **à queue légère** (exponentielle, Gamma), $e(u)$ devient constante ou décroît ; pour une loi **à queue lourde** de type Pareto, $e(u)$ **croît avec $u$**. L'empirique, calculée sur tous les sinistres, croît nettement : à $u=10\,000$ €, un sinistre qui dépasse ce seuil le dépasse en moyenne de 88 264 € ; à $u=100\,000$ €, de 170 057 €.

```python hide
def excedent_moyen(x, u):
    return float(x[x > u].mean() - u) if (x > u).sum() >= 15 else np.nan
for u, cle in ((10_000, "e10"), (100_000, "e100")):
    NUM(cle, excedent_moyen(sin["rev"].values, u))
style.setup()
fig, ax = plt.subplots(1, 2, figsize=(10.5, 4.0))
b = np.linspace(1.5, 6.6, 46)
ax[0].hist(np.log10(mat["rev"]), bins=b, density=True, color=BLEU, alpha=0.75, label="matériel")
ax[0].hist(np.log10(cor["rev"]), bins=b, density=True, color=ORANGE, alpha=0.65, label="corporel")
ax[0].set_xticks([2, 3, 4, 5, 6]); ax[0].set_xticklabels(["100", "1 000", "10 000", "100 000", "1 M"])
ax[0].set_xlabel("montant du sinistre (€ de 2024, échelle logarithmique)"); ax[0].set_ylabel("densité")
ax[0].set_title("Deux populations de sinistres"); ax[0].legend(frameon=False)
us = np.unique(np.quantile(sin["rev"], np.linspace(0.05, 0.985, 60)))
ee = [excedent_moyen(sin["rev"].values, u) for u in us]
ax[1].plot(us / 1000, np.array(ee) / 1000, color=VIOLET, lw=1.6)
ax[1].set_xlabel("seuil $u$ (milliers d'€)"); ax[1].set_ylabel("excès moyen $e(u)$ (milliers d'€)")
ax[1].set_title("L'excès moyen croît avec le seuil : queue lourde")
fig.tight_layout(); fig.savefig("figures/ch02-severite.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```
<!--sortie-->
```text
NUM e10 88263.5169164557
NUM e100 170057.2267956044
```

![À gauche : densité des montants (échelle logarithmique) des sinistres matériels et corporels, en euros de 2024. À droite : fonction d'excès moyen empirique ; sa croissance indique une queue lourde.](figures/ch02-severite.png)

### 2.1.5 La queue : seuil, loi de Pareto généralisée et gros sinistres

Quand les grands sinistres dominent, on les modélise à part. Le théorème de **Pickands, Balkema et de Haan** (volume II, section 6.5) dit que, pour presque toute loi, les excès au-delà d'un seuil $u$ assez élevé suivent approximativement une **loi de Pareto généralisée** (GPD) :
$$P(X-u>y\mid X>u)=\Bigl(1+\xi\,\frac{y}{\sigma}\Bigr)^{-1/\xi},\qquad y>0,$$
d'**indice de queue** $\xi>0$ pour une queue lourde. L'indice $\xi$ commande tout : les moments d'ordre $m$ n'existent que si $\xi<1/m$. Avec $\xi>0{,}5$, **la variance est infinie** ; avec $\xi>1$, la moyenne l'est aussi. La sévérité programmée contient une queue de Pareto d'indice $\alpha=1{,}8$, soit $\xi=1/\alpha\approx0{,}56$ : la variance de ces sinistres est donc, en théorie, infinie. On le sait ici parce que c'est nous qui l'avons programmé.

Reste à choisir **le seuil**, compromis classique : trop bas, le modèle GPD est mal ajusté (biais) ; trop haut, il reste trop peu d'excès (variance). On ajuste donc la GPD pour plusieurs seuils et l'on regarde si $\hat\xi$ se **stabilise**.

```python hide
x_all = sin["rev"].values
def gpd_xi(x, u):
    ex = x[x > u] - u
    c, _, sc = stats.genpareto.fit(ex, floc=0)
    return c, sc, len(ex)
seuils = [30_000, 50_000, 75_000, 100_000, 150_000, 200_000]
rng = np.random.default_rng(1)
lignes = []
for u in seuils:
    c, sc, k = gpd_xi(x_all, u)
    xis = []
    for _ in range(200):
        xb = rng.choice(x_all, len(x_all))
        xis.append(gpd_xi(xb, u)[0])
    lignes.append((u, k, c, sc, np.percentile(xis, 2.5), np.percentile(xis, 97.5)))
tab_gpd = pd.DataFrame(lignes, columns=["seuil", "excès", "xi", "echelle", "xi_bas", "xi_haut"])
i100 = tab_gpd.index[tab_gpd["seuil"] == 100_000][0]
NUM("xi100", tab_gpd.loc[i100, "xi"]); NUM("xi100_bas", tab_gpd.loc[i100, "xi_bas"]); NUM("xi100_haut", tab_gpd.loc[i100, "xi_haut"])
NUM("k100", int(tab_gpd.loc[i100, "excès"])); NUM("sc100", tab_gpd.loc[i100, "echelle"])
NUM("xi30", tab_gpd.loc[0, "xi"]); NUM("k30", int(tab_gpd.loc[0, "excès"]))
NUM("xi200", tab_gpd.loc[5, "xi"]); NUM("k200", int(tab_gpd.loc[5, "excès"]))
NUM("xi_min", tab_gpd["xi"].min()); NUM("xi_max", tab_gpd["xi"].max())
grands = sin[sin["rev"] > 100_000]
NUM("part_grands_n", len(grands) / len(sin)); NUM("part_grands_cout", grands["rev"].sum() / sin["rev"].sum()); NUM("n_grands", len(grands))
top = sin["rev"].sort_values(ascending=False)
NUM("top10_part", top.head(10).sum() / top.sum()); NUM("top50_part", top.head(50).sum() / top.sum())
fig, ax = plt.subplots(figsize=(6.2, 3.8))
ax.errorbar(np.arange(len(seuils)), tab_gpd["xi"], yerr=[tab_gpd["xi"] - tab_gpd["xi_bas"], tab_gpd["xi_haut"] - tab_gpd["xi"]],
            fmt="o", color=BLEU, capsize=3, lw=1.4)
ax.axhline(1 / 1.8, color=ORANGE, ls="--", lw=1.2); ax.text(5.15, 1 / 1.8, "queue programmée\n$\\xi = 0{,}56$", color=ORANGE, va="center", fontsize=9)
ax.set_xticks(np.arange(len(seuils))); ax.set_xticklabels([f"{u // 1000} k€\n({int(k)} excès)" for u, k in zip(tab_gpd["seuil"], tab_gpd["excès"])], fontsize=8)
ax.set_xlim(-0.4, 6.5); ax.set_ylabel("indice de queue estimé $\\hat\\xi$")
ax.set_title("L'indice de queue selon le seuil (intervalle à 95 % par bootstrap)")
fig.tight_layout(); fig.savefig("figures/ch02-gpd.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```
<!--sortie-->
```text
NUM xi100 0.6640936536357235
NUM xi100_bas 0.354013798609708
NUM xi100_haut 0.9341718905762805
NUM k100 91
NUM sc100 72867.30417584465
NUM xi30 0.4683057843808869
NUM k30 167
NUM xi200 0.2708153908279517
NUM k200 34
NUM xi_min 0.2708153908279517
NUM xi_max 0.6640936536357235
NUM part_grands_n 0.015903530234183852
NUM part_grands_cout 0.534668566307307
NUM n_grands 91
NUM top10_part 0.20081180425428974
NUM top50_part 0.42668091933225144
```

```python hide-code
print(tab_gpd[["seuil", "excès", "xi", "echelle"]].round(2).to_string(index=False))
```
<!--sortie-->
```text
 seuil  excès   xi   echelle
 30000    167 0.47  77945.91
 50000    128 0.39  98897.00
 75000    101 0.40 107026.44
100000     91 0.66  72867.30
150000     48 0.40 156753.45
200000     34 0.27 217089.33
```

![Indice de queue estimé de la loi de Pareto généralisée selon le seuil, avec son intervalle de confiance à 95 % obtenu par rééchantillonnage ; la ligne en pointillé donne la valeur de la queue de Pareto programmée.](figures/ch02-gpd.png)

On lit trois choses. D'abord, $\hat\xi$ varie de 0,27 à 0,66 selon le seuil : **il ne se stabilise pas nettement**. Ensuite, l'intervalle de confiance à 100 000 € (avec seulement 91 excès) va de 0,35 à 0,93 : il contient la valeur programmée de 0,56, mais aussi des valeurs pour lesquelles la moyenne même serait presque infinie. Enfin, la raison de cette instabilité est instructive : la sévérité corporelle programmée est un **mélange** d'une lognormale (à queue modérée) et d'une queue de Pareto, de sorte que les seuils bas mélangent deux comportements. Aucune loi simple ne s'ajuste, et les chiffres de queue sont **incertains** de façon irréductible.

> ⚠️ **Se méfier d'un indice de queue précis.** Un $\hat\xi$ à trois décimales est une illusion avec une centaine d'observations dans la queue. Une conclusion tarifaire ne doit pas dépendre de la deuxième décimale : on teste la sensibilité (seuils, intervalles), et l'on reste prudent sur les quantiles extrêmes.

**Pourquoi la queue compte autant.** Les 91 sinistres de plus de 100 000 € ne représentent que 1,6 % des sinistres, mais **53 % du coût total**. Les dix plus grands pèsent à eux seuls 20 % du coût, les cinquante plus grands 43 %. Le coût d'un portefeuille automobile dépend donc d'une poignée de sinistres, dont la sévérité n'est connue qu'avec peine.

**L'écrêtement.** La pratique courante est de **ne pas laisser ces sinistres bruiter le tarif** : on plafonne chaque sinistre à un seuil $c$ (ici 100 000 €), on estime les modèles sur les montants écrêtés $\min(X,c)$, et l'on ajoute une **charge pour gros sinistres** commune à tous les contrats :
$$E[X]=E[\min(X,c)]+E[(X-c)_+],\qquad\text{charge}=\frac{\text{somme des excès au-delà de } c}{\text{exposition totale}}.$$
On répartit uniformément la partie imprévisible (qui est surtout du hasard) et l'on réserve la segmentation à la partie ordinaire. Nous l'utiliserons en section 2.2. La réassurance (chapitre 6) est l'autre réponse : transférer cette queue à un tiers.

### 2.1.6 Le modèle collectif : la charge annuelle du portefeuille

Reconstituons maintenant le coût total $S=\sum_{k=1}^N X_k$ d'un portefeuille. Le raisonnement par conditionnement donne, sous les hypothèses d'indépendance de la section 2.1.1 :
$$E[S]=E[N]\,E[X],\qquad \mathrm{Var}(S)=E[N]\,\mathrm{Var}(X)+\mathrm{Var}(N)\,E[X]^2.$$

> 📐 **Démonstration.** Sachant $N=n$, $E[S\mid N=n]=nE[X]$ et $\mathrm{Var}(S\mid N=n)=n\mathrm{Var}(X)$. Donc $E[S]=E\bigl[E[S\mid N]\bigr]=E[N]E[X]$ et, par la formule de la variance totale, $\mathrm{Var}(S)=E[N]\mathrm{Var}(X)+\mathrm{Var}(N)E[X]^2$. Pour un nombre de Poisson, $\mathrm{Var}(N)=E[N]$ et $\mathrm{Var}(S)=E[N]\,E[X^2]$.

La première relation est **l'égalité de la prime pure** annoncée plus haut : le coût moyen est le produit de la fréquence moyenne par la sévérité moyenne (démontrée ici, utilisée en section 2.2). La seconde dit que **la variance de la charge vient de deux sources** : la variabilité des montants et celle du nombre de sinistres.

**Application à l'année 2024.** L'exposition de 2024 est de 32 081 années. Avec le taux estimé, le nombre de sinistres attendu est de 2 120. Pour la sévérité, on rééchantillonne les montants observés (revalorisés en euros de 2024). On simule 2 000 années : le nombre de sinistres tiré selon Poisson, les montants tirés avec remise.

```python hide
rng = np.random.default_rng(2024)
lam24 = lam_hat * pol.loc[pol["annee"] == 2024, "exposition"].sum()
x = sin["rev"].values
NUM("expo24", pol.loc[pol["annee"] == 2024, "exposition"].sum()); NUM("n24", lam24)
N = rng.poisson(lam24, 2000)
S = np.array([rng.choice(x, n).sum() for n in N])
m_f = lam24 * x.mean(); sd_f = np.sqrt(lam24 * np.mean(x ** 2))
NUM("S_moy_sim", S.mean() / 1e6); NUM("S_sd_sim", S.std() / 1e6); NUM("S_moy_f", m_f / 1e6); NUM("S_sd_f", sd_f / 1e6)
q995 = np.quantile(S, 0.995); NUM("S_q995", q995 / 1e6); NUM("S_q995_exc", (q995 - S.mean()) / 1e6)
NUM("S_q995_sd", (q995 - S.mean()) / S.std())
obs24 = sin.loc[sin["annee"] == 2024, "montant"].sum()
NUM("S_obs24", obs24 / 1e6); NUM("S_z24", abs(obs24 - S.mean()) / S.std())
par_an = []
for a in (2022, 2023, 2024):
    e_a = pol.loc[pol["annee"] == a, "exposition"].sum()
    attendu = lam_hat * e_a * x.mean()
    observe = sin.loc[sin["annee"] == a, "rev"].sum()
    par_an.append((a, attendu / 1e6, observe / 1e6))
tab_an = pd.DataFrame(par_an, columns=["année", "attendu (M€ 2024)", "observé (M€ 2024)"])
NUM("an_att3", tab_an.iloc[:, 1].sum()); NUM("an_obs3", tab_an.iloc[:, 2].sum())
fig, ax = plt.subplots(figsize=(6.4, 3.8))
ax.hist(S / 1e6, bins=40, color=BLEU, alpha=0.75)
ax.axvline(S.mean() / 1e6, color=ENCRE, lw=1.2); ax.text(S.mean() / 1e6, ax.get_ylim()[1] * 0.97, " moyenne", fontsize=9, va="top")
ax.axvline(q995 / 1e6, color=ROUGE, lw=1.5); ax.text(q995 / 1e6, ax.get_ylim()[1] * 0.97, " quantile 99,5 %", color=ROUGE, fontsize=9, va="top")
ax.axvline(obs24 / 1e6, color=ORANGE, lw=1.5, ls="--"); ax.text(obs24 / 1e6, ax.get_ylim()[1] * 0.8, "observé 2024 ", color=ORANGE, fontsize=9, ha="right")
ax.set_xlabel("charge annuelle du portefeuille (M€)"); ax.set_ylabel("nombre d'années simulées")
ax.set_title("2 000 années simulées pour 2024")
fig.tight_layout(); fig.savefig("figures/ch02-charge.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```
<!--sortie-->
```text
NUM expo24 32080.943
NUM n24 2119.6756422932062
NUM S_moy_sim 17.103123628898405
NUM S_sd_sim 2.4302163147125864
NUM S_moy_f 17.026841742422143
NUM S_sd_f 2.426673112827197
NUM S_q995 23.877339181743995
NUM S_q995_exc 6.77421555284559
NUM S_q995_sd 2.7874948875268144
NUM S_obs24 13.713928
NUM S_z24 1.3946065658353684
NUM an_att3 45.96344200320001
NUM an_obs3 45.9634420032
```

![Distribution de la charge annuelle du portefeuille obtenue en simulant 2 000 années (nombre de sinistres de Poisson, montants tirés dans l'historique) ; la ligne rouge est le quantile à 99,5 %, la ligne orange pointillée la charge réellement observée en 2024.](figures/ch02-charge.png)

La simulation donne une charge moyenne de 17,1 M€ et un écart-type de 2,43 M€ ; les formules en forme close donnent 17,0 M€ et 2,43 M€, un accord qui valide les deux. Le **quantile à 99,5 %** de la charge annuelle vaut 23,9 M€, soit 6,8 M€ au-dessus de la moyenne (2,8 écarts-types). C'est exactement le genre de chiffre que la réglementation Solvabilité demande de calculer (chapitre 4, section 4.2).

La charge réellement observée en 2024 est de 13,7 M€ (en euros courants) : à 1,4 écarts-types **sous** la moyenne simulée. Ce n'est pas nécessairement une erreur du modèle : c'est une année où la queue ne s'est presque pas manifestée. Le tableau compare, année par année, la charge attendue avec le taux moyen et la sévérité moyenne (tout en euros de 2024) et la charge observée.

```python hide-code
print(tab_an.round(1).to_string(index=False))
```
<!--sortie-->
```text
 année  attendu (M€ 2024)  observé (M€ 2024)
  2022               13.9               15.3
  2023               15.0               17.0
  2024               17.0               13.7
```

Les deux premières années dépassent l'attendu, la dernière est nettement en dessous, et sur les trois années les écarts se compensent presque : 46,0 M€ observés pour 46,0 M€ attendus. C'est le signe d'un modèle **bien centré** et d'une charge annuelle **très variable**, ce que dit déjà l'écart-type de 2,4 M€.

> ⚠️ **Ce que cette simulation suppose.** Trois choses, toutes discutables : (1) les montants sont tirés dans les 5 722 sinistres observés, donc **la queue au-delà du maximum observé n'existe pas** dans la simulation (or c'est là que se trouvent les quantiles extrêmes) ; (2) le nombre de sinistres est de Poisson pur, sans la sur-dispersion de la section 2.1.3 ni la corrélation entre contrats (un orage, une épidémie) ; (3) les montants sont indépendants du nombre. Le quantile à 99,5 % estimé ici est donc un **plancher plausible**, pas un chiffre fiable à l'euro près.

### 2.1.7 Les paramètres programmés, enfin révélés

| Quantité | Vérité programmée | Estimation |
|---|---|---|
| Fréquence annuelle moyenne | environ 6,5 % | 6,61 % |
| Variance de l'hétérogénéité $\alpha$ | 0,4 | 0,47 (erreur-type 0,09) |
| Forme du Gamma (matériel) | 2,5 | 2,34 |
| Effet de la puissance sur la sévérité | 0,05 | 0,050 |
| Inflation annuelle des coûts | 4 % | 4,4 % |
| Indice de queue corporel | 0,56 | 0,66 à 100 k€ (de 0,35 à 0,93) |

Tout est retrouvé à l'erreur d'estimation près, **sauf ce qui reste fragile par nature** : l'hétérogénéité et l'indice de queue. C'est une leçon de méthode : les paramètres d'un cœur de distribution se retrouvent bien avec peu de données, ceux d'une queue ou d'une variance non observée demandent beaucoup plus.

> ✅ **À retenir.**
> - Le coût d'un contrat est $S=\sum_{k\le N}X_k$ ; sa moyenne est le produit de la **fréquence moyenne** par la **sévérité moyenne**.
> - La fréquence s'estime par **sinistres sur exposition** ; le dénominateur n'est jamais le nombre de contrats.
> - La loi de Poisson impose $\mathrm{Var}=\text{moyenne}$ ; l'hétérogénéité non observée donne une **binomiale négative** ($\mathrm{Var}=\mu+\alpha\mu^2$), visible surtout dans les queues.
> - La sévérité est asymétrique : les sinistres matériels se décrivent par un **Gamma**, les grands sinistres par une **loi de Pareto généralisée** dont l'indice de queue est **incertain** ; on **écrête** et l'on met une charge pour gros sinistres.
> - Le **modèle collectif** reconstruit la charge annuelle ; son quantile à 99,5 % est le chiffre qu'attend la réglementation, et il est fragile.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 à 2.3 et exercices 2.1 à 2.3 (comptage et exposition, binomiale négative, queue et écrêtement, modèle collectif).
