## 5.1 Tables de mortalité

Cette section construit l'objet central de l'assurance vie : la **table de mortalité**. On part de ce que l'on observe (des décès et des années-personnes vécues), on en tire des taux, des probabilités, puis une table ; on se demande si la table d'une année décrit bien l'avenir de ceux qui la vivent ; on la lisse par une loi paramétrique ; enfin on vérifie si les assurés d'un portefeuille meurent moins que la population générale.

```python hide
ages = np.arange(100)
tab = {}
for s in "FM":
    for an in (1980, 2019):
        tab[(s, an)] = M[s][an].to_numpy()
a_fit = np.arange(30, 100)
P_GM = gm_ajuste(a_fit, D["F"][2019].loc[a_fit].to_numpy(), E["F"][2019].loc[a_fit].to_numpy())
qF19 = prolonge(q_depuis_m(tab[("F", 2019)]), P_GM)
TF19 = table_vie(qF19)
qM19 = prolonge(q_depuis_m(tab[("M", 2019)]), P_GM)
TM19 = table_vie(qM19)
qV19 = prolonge(q_depuis_m(m_vrai("F", 2019)), P_GM)
TV19 = table_vie(qV19)
# cellule d'exemple : femmes de 60 ans en 2019
d60, e60 = int(D["F"].loc[60, 2019]), float(E["F"].loc[60, 2019])
m60 = d60 / e60
NUM("d60", d60); NUM("e60", round(e60)); NUM("m60", round(m60, 5)); NUM("q60", round(1 - np.exp(-m60), 5))
NUM("sd_rel60", round(100 / np.sqrt(d60), 1))
NUM("m60_vrai", round(m_vrai("F", 2019)[60], 5))
NUM("q_exp_03", round(1 - np.exp(-0.3), 4)); NUM("q_act_03", round(0.3 / 1.15, 4))
NUM("e0F", round(TF19.e[0], 2)); NUM("e65F", round(TF19.e[65], 2)); NUM("e0M", round(TM19.e[0], 2)); NUM("e65M", round(TM19.e[65], 2))
NUM("e0V", round(TV19.e[0], 2)); NUM("e65V", round(TV19.e[65], 2))
NUM("l65F", round(TF19.l[65])); NUM("l100F", round(TF19.l[100], 1))
NUM("e60_i", round(e60)); NUM("m60_m", str(round(m60, 5)).replace(".", "{.}")); NUM("q60_m", str(round(1 - np.exp(-m60), 5)).replace(".", "{.}"))
NUM("q_exp_03_m", str(round(1 - np.exp(-0.3), 4)).replace(".", "{.}")); NUM("q_act_03_m", str(round(0.3 / 1.15, 4)).replace(".", "{.}"))
NUM("m60_pct", round(100 * m60, 2))
# vérifications des affirmations de la prose
assert abs(TF19.e[0] - TV19.e[0]) < 0.05 and abs(TF19.e[65] - TV19.e[65]) < 0.08
lt = np.array([100000.0]); qq = np.array([0.013, 0.014, 0.015, 0.016])
ll = 100000 * np.concatenate([[1], np.cumprod(1 - qq)])
assert np.allclose(ll, [100000, 98700, 97318.2, 95858.427, 94324.69], atol=0.1) and abs(np.prod(1 - qq) - 0.94325) < 1e-5
NUM("surv4", round(np.prod(1 - qq), 5))
```

### 5.1.1 Du décès observé au taux de mortalité

Prenons la cellule « femmes de 60 ans en 2019 » du jeu de population. Elle contient une **exposition** de {{e60:,.0f}} années-personnes (chaque personne de 60 ans présente toute l'année compte pour 1 ; une personne qui entre ou sort en cours d'année compte pour la fraction vécue) et {{d60}} décès. Le **taux central de mortalité** est le rapport

$$
m_{x} = \frac{D_x}{E_x} = \frac{ {{d60}} }{ {{e60_i}} } \approx {{m60_m}} .
$$

C'est un **taux par année-personne**, pas une probabilité : il se lit « environ {{m60_pct}} décès par an pour 100 personnes de 60 ans ».

> 📐 **Pourquoi ce rapport est le bon estimateur.** Si les décès d'une cellule suivent une loi de Poisson, $D_x \sim \text{Poisson}(E_x\, m_x)$ (hypothèse : chaque année-personne est exposée à une force de mortalité constante $m_x$ et les décès sont indépendants), la log-vraisemblance est $\ell(m) = D\ln m - E\,m + \text{cte}$. Sa dérivée $D/m - E$ s'annule en $\hat m = D/E$, et la dérivée seconde $-D/m^2$ donne la variance $\widehat{\text{Var}}(\hat m)= \hat m/E$. L'erreur relative est donc $1/\sqrt{D}$ : avec {{d60}} décès, environ {{sd_rel60}} %. **C'est le nombre de décès, pas le nombre d'habitants, qui fixe la précision.**

Le taux central n'est pas encore la **probabilité de décéder dans l'année**, $q_x$, que l'on attend d'une table. Si la force de mortalité est constante sur l'année, la survie sur l'année est $e^{-m_x}$ et

$$
q_x = 1 - e^{-m_x}.
$$

Une autre convention répandue suppose les décès répartis uniformément dans l'année, ce qui donne $q_x = m_x/(1+m_x/2)$. Pour les âges courants, les deux formules sont indiscernables (à 60 ans, $q_{60}\approx{{q60_m}}$) ; elles ne divergent que là où $m$ est grand : pour $m=0{,}3$, la première donne {{q_exp_03_m}} et la seconde {{q_act_03_m}}. Le jeu de ce chapitre a été simulé avec la première, que nous adoptons.

> 🧪 **Ce que la vérité programmée dit ici.** Le taux vrai de cette cellule est {{m60_vrai}}, contre {{m60}} observé : l'écart est de l'ordre de l'erreur attendue ({{sd_rel60}} %). Il reste, de cellule en cellule, un bruit de Poisson que les tables lissent et que les petits portefeuilles subissent de plein fouet (section 5.1.5).

La figure suivante montre les taux de mortalité par âge, en 1980 et en 2019, pour les deux sexes. Sur une échelle logarithmique, la partie adulte est presque **une droite** : c'est la loi de Gompertz (section 5.1.4). La bosse du jeune âge et le niveau plus élevé des hommes sont des traits du jeu simulé, inspirés des tables réelles sans les copier.

```python hide
fig, ax = plt.subplots(figsize=(8.2, 4.2))
for (s, an), col, ls, nom in [(("F", 1980), BLEU, "--", "femmes 1980"), (("F", 2019), BLEU, "-", "femmes 2019"), (("M", 1980), ORANGE, "--", "hommes 1980"), (("M", 2019), ORANGE, "-", "hommes 2019")]:
    ax.plot(ages, tab[(s, an)], color=col, ls=ls, lw=1.6, label=nom)
ax.set_yscale("log"); ax.set_xlabel("âge"); ax.set_ylabel("taux central de mortalité $m_x$ (échelle log)")
ax.legend(frameon=False, fontsize=9, loc="upper left", ncol=2)
fig.savefig("figures/ch05-taux-mortalite.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

![Taux de mortalité par âge (échelle logarithmique), femmes en bleu et hommes en orange, en 1980 (tirets) et en 2019 (trait plein). Données simulées.](figures/ch05-taux-mortalite.png)

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.1, exercices 5.1 et 5.2.

### 5.1.2 La table de mortalité

Une **table de mortalité** suit une cohorte fictive de $\ell_0 = 100\,000$ naissances (la *racine*, ou *radix*) en lui appliquant les probabilités de décès $q_x$ âge après âge :

$$
\ell_{x+1} = \ell_x\,(1-q_x), \qquad d_x = \ell_x\,q_x = \ell_x-\ell_{x+1}.
$$

$\ell_x$ est le nombre de survivants à l'âge exact $x$, $d_x$ le nombre de décès entre $x$ et $x+1$. On en tire les **années vécues** dans l'intervalle, $L_x \approx (\ell_x+\ell_{x+1})/2$, et l'**espérance de vie** à l'âge $x$ :

$$
e_x = \frac{\sum_{k\ge x} L_k}{\ell_x}.
$$

Un exemple à la main avec des probabilités arrondies, $q_{60}=0{,}013$, $q_{61}=0{,}014$, $q_{62}=0{,}015$, $q_{63}=0{,}016$ :

| Âge $x$ | $q_x$ | $\ell_x$ | $d_x = \ell_x q_x$ |
|---|---|---|---|
| 60 | 0,013 | 100 000,0 | 1 300,0 |
| 61 | 0,014 | 98 700,0 | 1 381,8 |
| 62 | 0,015 | 97 318,2 | 1 459,8 |
| 63 | 0,016 | 95 858,4 | 1 533,7 |
| 64 | | 94 324,7 | |

On lit par exemple qu'une cohorte de 100 000 personnes de 60 ans en compte encore 94 325 à 64 ans, soit une probabilité de survie de 4 ans $_4p_{60} = 0{,}013$ → $0{,}987 \times 0{,}986 \times 0{,}985 \times 0{,}984 = 0{,}94325$. La probabilité de survie sur plusieurs années est **le produit** des probabilités annuelles de survie.

Avec les 8 000 cellules du jeu, on construit la table des femmes de 2019 en trois étapes : taux, probabilités, table. Au-delà de 99 ans la table est **prolongée jusqu'à 120 ans** par une loi paramétrique (section 5.1.4), et le dernier $q$ vaut 1 : sans cette fermeture, la table s'arrêterait en laissant des survivants sans destin.

```python
q = prolonge(q_depuis_m(M["F"][2019].to_numpy()), P_GM)   # probabilités de décès, fermées à 120 ans
table = table_vie(q)                                       # l_x, d_x, L_x, e_x
print(table.loc[[0, 30, 60, 65, 90], ["age", "q", "l", "e"]].round({"q": 4, "l": 0, "e": 2}).to_string(index=False))
```

L'espérance de vie à la naissance de cette population fictive est de {{e0F}} ans pour les femmes de 2019 ({{e0M}} pour les hommes) et l'espérance de vie à 65 ans de {{e65F}} ans ({{e65M}} pour les hommes). Parmi 100 000 naissances féminines, {{l65F:,.0f}} atteignent 65 ans.

> 🧪 **Comparaison à la vérité.** La table construite à partir des taux **vrais** donne {{e0V}} ans à la naissance et {{e65V:.2f}} ans à 65 ans, soit des écarts de l'ordre de 0,02 an et 0,05 an : à cette échelle (des centaines de milliers de personnes par âge), le bruit de Poisson est négligeable. C'est ce qui changera pour un portefeuille d'assurés (section 5.1.5).

> ⚠️ **L'espérance de vie à la naissance est une moyenne de toutes les mortalités.** Elle dépend beaucoup de la mortalité infantile et n'indique rien sur la durée d'un contrat conclu à 40 ans. Pour l'assurance vie, les quantités utiles sont les $q_x$ et les $e_x$ aux âges de souscription, pas $e_0$.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.1, exercices 5.1 et 5.2.

### 5.1.3 Table de période ou table de génération ?

La table précédente est une **table de période** : elle combine les taux observés **la même année** à tous les âges. C'est une photographie de 2019. Elle ne décrit pas la vie d'une personne réelle, qui vieillit pendant que les taux changent : une personne de 60 ans en 2019 aura 70 ans en 2029 et affrontera alors la mortalité de 2029 à 70 ans, qui sera probablement plus basse que celle que la table de 2019 lui prête.

Une **table de génération** suit au contraire une cohorte de naissance $g$ le long de la diagonale : $q_x^{(g)}$ est la probabilité de décès à l'âge $x$ pendant l'année $g+x$. Quand la mortalité baisse, la table de génération est plus favorable que la table de période de l'année de naissance.

Le jeu de données permet une expérience propre : la cohorte née en 1920 a 60 ans en 1980 et 99 ans en 2019, donc **toute sa vie de 60 à 100 ans est observée** dans la fenêtre 1980–2019. Comparons le nombre moyen d'années vécues entre 60 et 100 ans (une espérance **partielle**, tronquée à 100 ans) selon trois tables : la table de période de 1980, celle de 2019 et la cohorte de 1920.

```python hide
def partielle_60(m_seq):
    """espérance de vie partielle à 60 ans, tronquée à 100 ans : somme des probabilités de survie de 1 à 40 ans (convention : survie en début d'année)"""
    surv = np.concatenate([[1.0], np.cumprod(np.exp(-np.asarray(m_seq)))])[:-1]
    return surv.sum(), np.concatenate([[1.0], np.cumprod(np.exp(-np.asarray(m_seq)))])
m_coh = np.array([D["F"].loc[60 + i, 1980 + i] / E["F"].loc[60 + i, 1980 + i] for i in range(40)])
e_coh, S_coh = partielle_60(m_coh)
e_p80, S_p80 = partielle_60(tab[("F", 1980)][60:100])
e_p19, S_p19 = partielle_60(tab[("F", 2019)][60:100])
NUM("e_coh", round(e_coh, 2)); NUM("e_p80", round(e_p80, 2)); NUM("e_p19", round(e_p19, 2))
NUM("ecart_coh_p80", round(round(e_coh, 2) - round(e_p80, 2), 2)); NUM("ecart_p19_coh", round(round(e_p19, 2) - round(e_coh, 2), 2))
NUM("s80_coh", round(100 * S_coh[20], 1)); NUM("s80_p80", round(100 * S_p80[20], 1)); NUM("s80_p19", round(100 * S_p19[20], 1))
fig, ax = plt.subplots(figsize=(8.2, 4.0))
x = np.arange(60, 101)
ax.plot(x, 100 * S_p80, color=ORANGE, lw=1.8, label="table de période 1980"); ax.plot(x, 100 * S_coh, color=VIOLET, lw=2.0, label="cohorte née en 1920"); ax.plot(x, 100 * S_p19, color=BLEU, lw=1.8, label="table de période 2019")
ax.set_xlabel("âge"); ax.set_ylabel("survivants à l'âge $x$ (% des 60 ans)"); ax.legend(frameon=False, fontsize=9, loc="upper right")
fig.savefig("figures/ch05-survie-tables.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

Les résultats : {{e_p80:.2f}} années vécues entre 60 et 100 ans avec la table de période de 1980, {{e_coh}} avec la cohorte réelle de 1920 et {{e_p19}} avec la table de période de 2019. La cohorte a vécu **{{ecart_coh_p80:.2f}} an de plus** que la photographie de 1980 ne le promettait, parce que sa mortalité a baissé pendant qu'elle vieillissait ; et elle a vécu **{{ecart_p19_coh:.2f}} ans de moins** que la photographie de 2019 ne le laisserait croire, parce qu'elle a traversé des années moins favorables. À 80 ans, {{s80_p80}} % des personnes de 60 ans survivent selon la table de 1980, {{s80_coh}} % pour la cohorte, {{s80_p19}} % selon la table de 2019.

![Courbes de survie à partir de 60 ans : table de période 1980 (orange), cohorte née en 1920 (violet, observée de 1980 à 2019) et table de période 2019 (bleu). Données simulées.](figures/ch05-survie-tables.png)

> ⚠️ **Piège de l'actuaire de rentes.** Valoriser une rente viagère avec la table de période du jour **sous-estime** sa durée dès que la mortalité baisse : la rente sera servie plus longtemps que prévu et le provisionnement sera insuffisant. C'est le **risque de longévité** (section 5.3.4). La réponse standard consiste à projeter la mortalité (une table de génération prospective) : c'est l'objet du modèle de Lee–Carter.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.1, exercices 5.1 et 5.2.

### 5.1.4 Lisser : la loi de Gompertz–Makeham

Deux raisons de lisser. La première est la **fermeture** : aux grands âges, les effectifs fondent, les taux observés sont erratiques, et il faut pourtant une table complète jusqu'à l'âge limite. La seconde est le **petit nombre** : pour un portefeuille d'assurés, les décès par âge se comptent en dizaines, et le bruit de Poisson masque la structure.

La loi de **Gompertz–Makeham** décrit la force de mortalité adulte par

$$
\mu(x) = A + B\,e^{c\,x}, \qquad A,\,B,\,c>0 .
$$

Le terme constant $A$ (Makeham) représente une mortalité indépendante de l'âge (accidents) ; le terme exponentiel (Gompertz) décrit l'**usure** : la mortalité est multipliée par la même constante $e^{c}$ à chaque année d'âge supplémentaire, et **double tous les $\ln 2/c$ ans**. Les paramètres s'ajustent par maximum de vraisemblance poissonien, en maximisant $\sum_x \left(D_x\ln m_x - E_x m_x\right)$ avec $m_x \approx \mu(x+\tfrac12)$.

```python
a = np.arange(30, 100)                                        # ajustement sur les âges adultes
p = gm_ajuste(a, D["F"][2019].loc[a].to_numpy(), E["F"][2019].loc[a].to_numpy())
A_, B_, c_ = np.exp(p)                                         # paramètres (on optimise leurs logarithmes)
print(f"A = {A_:.1e}   B = {B_:.2e}   c = {c_:.4f}   doublement tous les {np.log(2) / c_:.2f} ans")
```

Pour les femmes de 2019, la mortalité double environ tous les {{dbl}} ans (la valeur programmée dans le jeu est $c=0{,}1$, soit {{dbl_vrai}} ans). La constante de Makeham estimée est nulle à la précision de l'optimiseur : les âges de 30 à 99 ans ne laissent pas de place à un terme constant. La loi ajustée reste proche de la vérité entre 40 et 90 ans (à moins de 10 %) et s'en écarte aux extrémités : une loi à trois paramètres ne remplace pas une table entière, mais **elle prolonge raisonnablement**. C'est elle qui ferme notre table à 120 ans.

> ⚠️ **L'extrapolation est une hypothèse, pas une mesure.** Au-delà de 100 ans, aucun décès n'est observé dans la table : elle est prolongée par la loi de Gompertz–Makeham. Ici l'enjeu est faible : fermer la table à 100 ans plutôt qu'à 120 changerait l'espérance de vie à 65 ans de {{de65_cut}} an seulement, car il ne reste que {{l100F:.0f}} survivants à 100 ans sur 100 000 naissances. L'extrapolation pèserait bien davantage pour une population plus âgée, pour une mortalité aux grands âges plus basse, ou pour une rente de réversion servie au dernier survivant d'un couple.

Le lissage sert surtout pour les **portefeuilles d'assurés**. La figure suivante compare, pour les contrats observés de 2015 à 2019, les taux bruts par âge (avec leur intervalle à 95 %), la table de population multipliée par 0,75 (le niveau programmé) et une loi de Gompertz–Makeham ajustée directement sur le portefeuille. Les taux bruts sont si dispersés qu'aucun âge ne se lit seul, alors que la forme lissée raconte une histoire cohérente.

```python hide
L = lignes_police_annee(pv)
L["m_ref"] = [M[s].loc[ag, an] for s, ag, an in zip(L["sexe"], L["age"], L["annee"])]
par_age = L.groupby("age").apply(lambda g: pd.Series({"D": g["deces"].sum(), "E": g["expo"].sum(), "Eref": (g["expo"] * g["m_ref"]).sum()}))
par_age = par_age[par_age["E"] > 0]
a_pf = par_age.index.to_numpy()
p_pf = gm_ajuste(a_pf, par_age["D"].to_numpy(), par_age["E"].to_numpy(), p0=(-8.0, -10.0, -2.3))
taux_bruts = par_age["D"] / par_age["E"]
# intervalle exact de Poisson de chaque taux brut
from scipy.stats import chi2
bas = np.array([chi2.ppf(0.025, 2 * d) / 2 if d > 0 else 0 for d in par_age["D"]]) / par_age["E"].to_numpy()
haut = np.array([chi2.ppf(0.975, 2 * (d + 1)) / 2 for d in par_age["D"]]) / par_age["E"].to_numpy()
ref075 = 0.75 * np.array([M["F"][2019].loc[x] * 0.5 + M["M"][2019].loc[x] * 0.5 for x in a_pf])
fig, ax = plt.subplots(figsize=(8.2, 4.2))
ax.errorbar(a_pf, taux_bruts, yerr=[taux_bruts - bas, haut - taux_bruts], fmt="o", ms=3.2, color=MUET, ecolor="#c3c2b7", lw=0.9, label="taux bruts du portefeuille")
ax.plot(a_pf, ref075, color=BLEU, lw=1.6, label="0,75 × population (hommes et femmes à parts égales)")
ax.plot(a_pf, gm_mu(a_pf + 0.5, p_pf), color=ORANGE, lw=1.8, label="Gompertz–Makeham ajustée au portefeuille")
ax.set_yscale("log"); ax.set_ylim(1e-4, 0.5); ax.set_xlabel("âge"); ax.set_ylabel("taux de mortalité (échelle log)")
ax.legend(frameon=False, fontsize=8.5, loc="upper left")
fig.savefig("figures/ch05-portefeuille-taux.png", dpi=200, bbox_inches="tight"); plt.close(fig)
NUM("dbl", round(np.log(2) / c_, 2)); NUM("dbl_vrai", round(np.log(2) / 0.1, 2))
qcut = qF19[:100].copy(); qcut[99] = 1.0
NUM("de65_cut", round(TF19.e[65] - table_vie(qcut).e[65], 3))
NUM("n_ages_pf", len(a_pf)); NUM("dec_med_age", int(par_age["D"].median()))
NUM("c_pf", round(float(np.exp(p_pf[2])), 4)); NUM("dbl_pf", round(np.log(2) / float(np.exp(p_pf[2])), 2))
NUM("sd_med", round(100 / np.sqrt(par_age["D"].median()), 0))
r_gm = gm_mu(np.arange(40, 91) + 0.5, P_GM) / m_vrai("F", 2019)[40:91]
assert r_gm.min() > 0.9 and r_gm.max() < 1.1, (r_gm.min(), r_gm.max())
assert abs(np.exp(p_pf[2]) - c_) < 0.01
```

![Mortalité des assurés par âge : taux bruts avec intervalle de Poisson à 95 % (gris), table de population × 0,75 (bleu) et loi de Gompertz–Makeham ajustée au portefeuille (orange). Données simulées.](figures/ch05-portefeuille-taux.png)

Sur les {{n_ages_pf}} âges du portefeuille, la médiane est de {{dec_med_age}} décès par âge : chaque taux brut est connu à $1/\sqrt{D}$ près, soit environ {{sd_med:.0f}} % à l'âge médian. La loi ajustée sur ces seules données double tous les {{dbl_pf}} ans, c'est-à-dire presque exactement comme la population ; le portefeuille se distingue par un **niveau** plus bas, non par une pente différente.

> 🧭 **Pour aller plus loin : les méthodes de graduation.** Plutôt qu'une loi paramétrique, on peut lisser par la méthode de **Whittaker–Henderson** : on cherche les taux $\hat g$ qui minimisent $\sum_x w_x(m_x-\hat g_x)^2+\lambda\sum_x(\Delta^3\hat g_x)^2$, compromis entre fidélité aux données (poids $w_x$ égaux aux expositions) et régularité (les différences troisièmes sont petites). On la pratique dans l'application 5.2 du cahier.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.2, exercice 5.3.

### 5.1.5 Les assurés meurent-ils moins que la population ? Le rapport réel/attendu

Un assureur ne tarifie pas avec la mortalité de la population générale : les assurés sont **sélectionnés** (un questionnaire médical écarte des risques aggravés), plus aisés, plus attentifs à leur santé. Le **rapport réel/attendu** (en anglais *actual over expected*, A/E) mesure cet écart :

$$
\text{A/E} = \frac{\text{décès observés}}{\text{décès attendus}} = \frac{\sum_i \delta_i}{\sum_i E_i\, m^{\text{réf}}(x_i,t_i)} ,
$$

où $\delta_i$ vaut 1 si le contrat $i$ est sorti par décès, $E_i$ est son exposition de l'année et $m^{\text{réf}}$ le taux de la **table de référence** pour son sexe, son âge et son année. Au dénominateur, on somme sur toutes les années-contrats **en vigueur** : un contrat émis en 2017 n'apporte d'exposition qu'à partir de 2017, et celui d'un assuré décédé en 2016 n'est plus compté ensuite.

Sur les {{n_contrats:,.0f}} contrats du portefeuille, la reconstruction des lignes contrat-année donne {{n_lignes:,.0f}} lignes, {{expo_L:,.0f}} années d'exposition et {{deces_pv}} décès. La table de référence est la population de la même année et du même sexe.

```python
L = lignes_police_annee(pv)                                              # une ligne par contrat-année en vigueur
L["attendu"] = L["expo"] * np.array([M[s].loc[a, t] for s, a, t in zip(L["sexe"], L["age"], L["annee"])])
ae, bas, haut = ae_ic(L["deces"].sum(), L["attendu"].sum())              # intervalle exact de Poisson à 95 %
print(f"réels {L['deces'].sum()}  attendus {L['attendu'].sum():.1f}  A/E = {ae:.3f}  [{bas:.3f} ; {haut:.3f}]")
```

```python hide
NUM("n_lignes", len(L)); NUM("expo_L", round(L["expo"].sum())); NUM("ae", round(ae, 3)); NUM("ae_bas", round(bas, 3)); NUM("ae_haut", round(haut, 3))
NUM("gain_pct", round(100 * (1 - ae))); NUM("attendu", round(L["attendu"].sum(), 1))
assert bas < 0.75 < haut
```

Le rapport réel/attendu est de **{{ae}}**, avec un intervalle à 95 % de [{{ae_bas}} ; {{ae_haut}}] : les assurés meurent environ **{{gain_pct}} % de moins** que la population, et la valeur programmée (0,75) est bien dans l'intervalle. L'intervalle repose sur l'hypothèse que le nombre de décès suit une loi de Poisson dont l'espérance est $\text{A/E}_{\text{vrai}}\times$ attendu, avec l'attendu supposé connu (la table de référence n'est pas, elle aussi, estimée avec incertitude).

> 📐 **Combien de décès faut-il ?** Pour un rapport estimé à ±10 % près (demi-largeur de l'intervalle à 95 %), il faut $1{,}96/\sqrt{D}\le0{,}10$, c'est-à-dire $D \ge 384$ décès. À ±5 %, il en faut 1 537. Un portefeuille de 20 000 contrats suffit ici (832 décès), mais **pas pour comparer des sous-groupes** : l'analyse par âge ou par contrat se fait avec beaucoup moins de décès par cellule et des intervalles larges.

La même mesure, détaillée par tranche d'âge, montre que le rapport n'est pas constant :

```python hide-code
L["tranche"] = pd.cut(L["age"], [24, 40, 50, 60, 70, 100], labels=["25–40", "41–50", "51–60", "61–70", "71+"])
tab_ae = []
for t, g in L.groupby("tranche", observed=True):
    r, b, h = ae_ic(int(g["deces"].sum()), g["attendu"].sum())
    tab_ae.append((t, int(g["deces"].sum()), round(g["attendu"].sum(), 1), round(r, 3), round(b, 3), round(h, 3)))
print(pd.DataFrame(tab_ae, columns=["tranche d'âge", "décès", "attendus", "A/E", "borne basse", "borne haute"]).to_string(index=False))
```

Le tableau semble montrer un rapport qui **croît avec l'âge** (de {{ae_min}} à {{ae_max}}) : on y retrouverait le schéma classique d'une sélection médicale qui s'estompe avec l'âge. Mais **la sélection programmée est la même à tous les âges** (un facteur 0,75 sur le taux), et les intervalles le disent : chacun contient la valeur 0,75. Les différences entre tranches sont du **bruit d'échantillonnage**, d'autant plus fort que les tranches comptent peu de décès (la première n'en compte que {{d_tr1}}). Lire une tendance dans ce tableau serait une erreur : c'est exactement ce qui se produit quand on découpe un portefeuille trop finement.

```python hide
NUM("ae_min", round(min(r[3] for r in tab_ae), 2)); NUM("ae_max", round(max(r[3] for r in tab_ae), 2)); NUM("d_tr1", tab_ae[0][1])
assert all(r[4] < 0.75 < r[5] for r in tab_ae)
```

```python hide
ae_i = pd.DataFrame(tab_ae, columns=["t", "D", "E", "r", "b", "h"])
fig, ax = plt.subplots(figsize=(7.6, 3.6))
y = np.arange(len(ae_i))[::-1]
ax.errorbar(ae_i["r"], y, xerr=[ae_i["r"] - ae_i["b"], ae_i["h"] - ae_i["r"]], fmt="o", color=BLEU, ecolor=BLEU, capsize=3, lw=1.4)
ax.axvline(0.75, color=ORANGE, lw=1.4, ls="--"); ax.axvline(1.0, color=MUET, lw=1.0, ls=":")
ax.text(0.755, y[0] + 0.45, "vérité programmée : 0,75", color=ORANGE, fontsize=8.5, ha="left", va="bottom")
ax.text(1.005, y[-1] - 0.45, "population", color=MUET, fontsize=8.5, ha="left", va="top")
ax.set_yticks(y); ax.set_yticklabels(ae_i["t"]); ax.set_xlabel("rapport réel/attendu (intervalle à 95 %)"); ax.set_ylabel("tranche d'âge")
ax.set_xlim(0.3, 1.25); ax.set_ylim(y[-1] - 0.9, y[0] + 0.9)
fig.savefig("figures/ch05-ae-tranches.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

![Rapport réel/attendu par tranche d'âge avec son intervalle de Poisson à 95 %. La ligne pointillée orange est la valeur programmée (0,75) et la ligne grise la mortalité de la population (1). Données simulées.](figures/ch05-ae-tranches.png)

Que faire d'un tel rapport ? Deux usages classiques : **tarifer avec une table de référence multipliée par un coefficient** ($q^{\text{assurés}}\approx 0{,}75\,q^{\text{pop.}}$, en pratique appliqué au taux $m$ plutôt qu'à $q$), tant que les données du portefeuille ne justifient pas une table d'expérience propre ; et **surveiller** le rapport dans le temps (une dérive vers 1 signale une sélection qui se dégrade ou une population qui change). Le prix correspondant, et sa sensibilité à la table, sont l'objet de la section 5.2.

> ⚠️ **Pièges du rapport réel/attendu.** (1) La table de référence doit correspondre au sexe, à la période et à la **définition de l'âge** (à la dernière date anniversaire, ou à l'âge le plus proche) : une définition décalée d'un demi-an change le rapport de plusieurs pour cent. (2) Un rapport global peut cacher des sous-populations très différentes (par contrat, par capital) : les capitaux élevés pèsent davantage dans le coût que dans le nombre de décès, et l'on calcule alors un A/E **pondéré par le capital**. (3) Il ne dit rien de la **cause** : sélection médicale, effet du contrat, mode de souscription.

> ✅ **À retenir (5.1).**
> - Le taux central est $m_x=D_x/E_x$ (estimateur du maximum de vraisemblance d'un modèle de Poisson) ; la probabilité de décès est $q_x=1-e^{-m_x}$ si la force est constante dans l'année ; la précision relative est $1/\sqrt{D}$.
> - Une table donne $\ell_x$, $d_x$, $L_x$, $e_x$ ; la survie sur plusieurs années est un **produit** de survies annuelles.
> - Une **table de période** est une photographie ; une **table de génération** suit une cohorte. Avec une mortalité en baisse, la première sous-estime la durée de vie des vivants : c'est le risque de longévité.
> - Gompertz–Makeham lisse et prolonge, mais l'extrapolation reste une hypothèse.
> - Le **rapport réel/attendu** mesure l'écart à une table de référence, avec un intervalle de Poisson : il faut près de 400 décès pour ±10 %.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.3, exercices 5.1 à 5.4.
