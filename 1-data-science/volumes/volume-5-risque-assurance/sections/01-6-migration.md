## 1.6 ➕ Migration de notations et matrices de transition

> 🧭 **Section optionnelle.** Elle étudie la **dynamique** du risque : une note n'est pas figée, elle monte et descend, et la probabilité qu'un emprunteur fasse défaut dans cinq ans dépend de ce chemin.

Les banques et les agences de notation rangent les emprunteurs dans une **échelle de notes** (ici de 1, la meilleure, à 7, la plus risquée) et suivent leur évolution chaque année. Le tableau des probabilités de passer d'une note à une autre est la **matrice de transition**. Elle sert à trois choses : estimer la probabilité de défaut **à plusieurs années** (1.6.4), anticiper la **dégradation** d'un portefeuille (c'est un moteur des étapes IFRS 9 de la section 1.5), et simuler des scénarios de crise. Cette section l'estime sur dix ans de notes, la compare à la **vérité programmée**, et montre pourquoi une matrice « moyenne » trompe en période de crise.

```python hide
import donnees5
from scipy.stats import chi2_contingency
from scipy.linalg import logm
P_vrai = donnees5.matrice_vraie()
panel = pd.read_csv("donnees/notations_panel.csv")
N = O.compter_transitions(panel)
M_hat = O.matrice_cohortes(N)
```

### 1.6.1 Qu'est-ce qu'une matrice de transition ?

Notons $X_t$ la note d'un emprunteur à la fin de l'année $t$, dans $\{1,\dots,7\}$, plus l'état **défaut** (noté 8). La matrice de transition annuelle $P$ a pour coefficient $P_{ij}=P(X_{t+1}=j\mid X_t=i)$ : chaque **ligne** est une distribution de probabilité (la somme vaut 1). Deux propriétés la structurent :

- le **défaut est absorbant** : un emprunteur en défaut y reste ($P_{88}=1$) ; la matrice complète est donc de taille $8\times8$, dont nous estimons les 7 premières lignes ;
- les notes bougent **peu** : la **diagonale** domine (on garde la même note le plus souvent), et les passages d'une note à la voisine sont bien plus fréquents que les sauts de plusieurs crans.

La dernière colonne est la **probabilité de défaut à un an** de chaque note : c'est le lien avec tout ce qui précède. Voici la matrice **vraie** utilisée pour simuler les données (une année « neutre », sans choc de conjoncture) :

```python hide-code
etiq = ["1", "2", "3", "4", "5", "6", "7", "défaut"]
print((100 * pd.DataFrame(P_vrai, index=[f"note {i}" for i in range(1, 8)], columns=etiq)).round(1).to_string())
```
<!--sortie-->
```text
           1     2     3     4     5     6     7  défaut
note 1  91.5   7.0   1.0   0.3   0.1   0.0   0.0     0.1
note 2   4.0  88.0   6.0   1.2   0.4   0.2   0.1     0.1
note 3   0.5   6.0  86.0   5.5   1.2   0.4   0.2     0.2
note 4   0.2   1.0   7.0  83.0   6.2   1.5   0.6     0.5
note 5   0.1   0.3   1.2   7.5  80.0   7.0   2.2     1.7
note 6   0.0   0.2   0.4   1.5   8.0  76.0   8.0     5.9
note 7   0.0   0.0   0.2   0.5   2.0   9.0  60.0    28.3
```

Lecture : un emprunteur noté 4 a 83,0 % de chances de rester en 4, 7,0 % de passer en 3 (amélioration), 6,2 % en 5, et **0,5 % de faire défaut dans l'année**. La note 7, la plus risquée, fait défaut dans plus d'un cas sur quatre (28,3 %).

### 1.6.2 Estimer par cohortes

L'estimation la plus simple s'appelle la **méthode des cohortes** : pour chaque note de départ $i$, on compte parmi les emprunteurs notés $i$ en début d'année combien se retrouvent dans l'état $j$ en fin d'année, et l'on divise :

$$\widehat P_{ij}=\frac{N_{ij}}{N_{i\cdot}}.$$

C'est l'estimateur du maximum de vraisemblance d'un modèle multinomial, indépendamment pour chaque ligne. Il reste une question pratique : que fait-on des emprunteurs **dont la note est retirée** (sortie du portefeuille, remboursement anticipé, perte de contact) ? On les compte à part et on les **retire du dénominateur** de l'année : l'hypothèse est que leur sortie n'informe pas sur leur risque, ce qui est une hypothèse (elle est vraie dans nos données, où 4 % sortent chaque année au hasard ; elle est souvent fausse dans la réalité, où l'on sort plus volontiers quand tout va bien, ou quand tout va très mal).

Voici les effectifs de transitions du panel (5 000 emprunteurs suivis jusqu'à dix ans, 39 102 observations « emprunteur-année »), avant la division :

```python hide-code
cnt = pd.DataFrame(N, index=[f"note {i}" for i in range(1, 8)], columns=["sortie"] + etiq)
print(cnt.to_string())
```
<!--sortie-->
```text
        sortie     1     2     3     4     5     6    7  défaut
note 1      96  2150   205    29     1     2     0    0       1
note 2     280   254  5669   447    91    31    16    6       6
note 3     404    55   605  8401   625   174    46   26      23
note 4     390    26    91   653  7770   650   163   75      55
note 5     215     2     8    56   416  4179   439  141     109
note 6     115     0     5     3    44   174  1977  279     186
note 7      37     0     0     0     5    20    87  702     387
```

Les effectifs sont très inégaux : 10 359 emprunteurs-années pour la note 3, 1 238 pour la note 7. Les transitions rares (un saut de la note 1 à la note 5) reposent sur quelques cas ou aucun, d'où l'importance de l'**incertitude**. Pour la mesurer, on rééchantillonne les **emprunteurs** (et non les lignes : les années d'un même emprunteur ne sont pas indépendantes) : c'est un bootstrap par grappes.

```python hide
ids = panel["id_emprunteur"].values - 1
C = np.zeros((5000, 7, 9), dtype=np.int32)
np.add.at(C, (ids, panel["note_debut"].values - 1, panel["note_fin"].values), 1)
rng_b = np.random.default_rng(0)
dfl = []
for _ in range(300):
    idx = rng_b.integers(0, 5000, 5000)
    Nb = C[idx].sum(axis=0); Mb = Nb[:, 1:] / Nb[:, 1:].sum(axis=1, keepdims=True); dfl.append(Mb[:, 7])
dfl = np.array(dfl); lo, hi = np.percentile(dfl, [2.5, 97.5], axis=0)
tab_d = pd.DataFrame({"vraie": P_vrai[:, 7], "estimée": M_hat[:, 7], "bas": lo, "haut": hi}, index=[f"note {i}" for i in range(1, 8)])
```

```python hide-code
print((100 * tab_d).round(2).rename(columns={"vraie": "PD vraie (%)", "estimée": "PD estimée (%)", "bas": "IC bas", "haut": "IC haut"}).to_string())
```
<!--sortie-->
```text
        PD vraie (%)  PD estimée (%)  IC bas  IC haut
note 1           0.1            0.04    0.00     0.13
note 2           0.1            0.09    0.03     0.19
note 3           0.2            0.23    0.15     0.33
note 4           0.5            0.58    0.44     0.73
note 5           1.7            2.04    1.65     2.45
note 6           5.9            6.97    6.14     8.00
note 7          28.3           32.22   29.59    34.71
```

```python hide
print("NUM pd_est", [round(float(x), 4) for x in M_hat[:, 7]]); print("NUM pd_vrai", [round(float(x), 4) for x in P_vrai[:, 7]])
print("NUM ic", [(round(float(a), 4), round(float(b), 4)) for a, b in zip(lo, hi)])
print("NUM nb_obs", int(N[:, 1:].sum() + N[:, 0].sum())); print("NUM n_sorties", int(N[:, 0].sum()))
print("NUM dans_ic", int(((P_vrai[:, 7] >= lo) & (P_vrai[:, 7] <= hi)).sum()))
```
<!--sortie-->
```text
NUM pd_est [0.0004, 0.0009, 0.0023, 0.0058, 0.0204, 0.0697, 0.3222]
NUM pd_vrai [0.001, 0.001, 0.002, 0.005, 0.017, 0.059, 0.283]
NUM ic [(0.0, 0.0013), (0.0003, 0.0019), (0.0015, 0.0033), (0.0044, 0.0073), (0.0165, 0.0245), (0.0614, 0.08), (0.2959, 0.3471)]
NUM nb_obs 39102
NUM n_sorties 1537
NUM dans_ic 5
```

La probabilité de défaut estimée est **systématiquement supérieure** à la vraie pour les notes risquées (7,0 % contre 5,9 % pour la note 6, 32,2 % contre 28,3 % pour la note 7), et la vraie valeur sort de l'intervalle de confiance pour deux notes sur sept (6 et 7) : ce n'est pas un défaut de l'estimateur, mais une **révélation**. La matrice vraie décrit une année neutre ; or le panel contient dix années dont **deux de récession**, qui augmentent les dégradations. La matrice estimée est donc une **moyenne sur le cycle**, plus sombre qu'une année neutre. Voyons-le.

```python hide
est_m = np.abs(M_hat - P_vrai[:, :]).max()
fig, axs = plt.subplots(1, 2, figsize=(10.0, 3.9))
lab = ["1", "2", "3", "4", "5", "6", "7", "D"]
for ax, mat, titre, cmap, vm in [(axs[0], 100 * M_hat, "Matrice estimée (%)", style.SEQ, None), (axs[1], 100 * (M_hat - P_vrai), "Écart estimée − vraie (points)", style.DIV, 4.0)]:
    if vm is None:
        im = ax.imshow(np.sqrt(mat), cmap=cmap, aspect="auto")
    else:
        im = ax.imshow(mat, cmap=cmap, vmin=-vm, vmax=vm, aspect="auto")
    ax.set_xticks(range(8)); ax.set_xticklabels(lab); ax.set_yticks(range(7)); ax.set_yticklabels(range(1, 8))
    ax.set_xlabel("note en fin d'année"); ax.set_ylabel("note en début d'année"); ax.set_title(titre)
    for i in range(7):
        for j in range(8):
            v = mat[i, j]
            if (vm is None and v >= 0.5) or (vm is not None and abs(v) >= 0.5):
                ax.text(j, i, f"{v:.1f}" if abs(v) < 10 else f"{v:.0f}", ha="center", va="center", fontsize=7.5,
                        color="white" if (vm is None and np.sqrt(v) > 5) else ENCRE)
fig.tight_layout(); fig.savefig("figures/ch01-migration.png", dpi=200, bbox_inches="tight"); plt.close(fig)
print("NUM max_ecart", round(float(100 * est_m), 1))
```
<!--sortie-->
```text
NUM max_ecart 3.9
```

![À gauche, matrice de transition estimée par cohortes ; à droite, son écart avec la matrice vraie d'une année neutre : la diagonale est plus faible et les dégradations plus fortes.](figures/ch01-migration.png)

### 1.6.3 La conjoncture déforme la matrice

Séparons les années. Le taux de défaut de l'ensemble du panel et la part d'emprunteurs **dégradés** (note de fin plus mauvaise que celle de début) varient fortement :

```python hide-code
pan2 = panel.assign(defaut=(panel["note_fin"] == 8), baisse=(panel["note_fin"] > panel["note_debut"]) & (panel["note_fin"] > 0), actifs=panel["note_fin"] >= 0)
ty = pan2.groupby("annee").agg(emprunteurs=("defaut", "size"), defauts_pct=("defaut", lambda s: 100 * s.mean()), degrades_pct=("baisse", lambda s: 100 * s.mean())).round(2)
print(ty.T.to_string())
```
<!--sortie-->
```text
annee               0        1        2        3        4        5        6        7        8        9
emprunteurs   5000.00  4755.00  4517.00  4268.00  4041.00  3814.00  3527.00  3260.00  3046.00  2874.00
defauts_pct      1.10     1.07     1.44     1.34     1.76     3.64     4.17     2.39     1.77     1.74
degrades_pct     7.42     7.00     8.10     9.98    12.00    19.87    19.14    11.60     7.78     6.40
```

```python hide
print("NUM an_def", [round(float(x), 2) for x in ty["defauts_pct"]]); print("NUM an_baisse", [round(float(x), 2) for x in ty["degrades_pct"]])
```
<!--sortie-->
```text
NUM an_def [1.1, 1.07, 1.44, 1.34, 1.76, 3.64, 4.17, 2.39, 1.77, 1.74]
NUM an_baisse [7.42, 7.0, 8.1, 9.98, 12.0, 19.87, 19.14, 11.6, 7.78, 6.4]
```

Les années 5 et 6 se détachent : le taux de défaut passe de 1,1–1,8 % les années ordinaires à 3,6–4,2 %, et la part de dégradations passe de 6–12 % à près de 20 %. Comparons les matrices estimées sur **deux sous-périodes** : les années calmes (0 à 3, 8 et 9) et la récession (5 et 6).

```python hide-code
calme = O.matrice_cohortes(O.compter_transitions(panel, [0, 1, 2, 3, 8, 9]))
rec = O.matrice_cohortes(O.compter_transitions(panel, [5, 6]))
nd_c = O.compter_transitions(panel, [0, 1, 2, 3, 8, 9]); nd_r = O.compter_transitions(panel, [5, 6])
tcy = pd.DataFrame({"PD calme (%)": 100 * calme[:, 7], "PD récession (%)": 100 * rec[:, 7],
                    "défauts calme": nd_c[:, 8], "défauts récession": nd_r[:, 8]}, index=[f"note {i}" for i in range(1, 8)])
tcy["rapport"] = tcy["PD récession (%)"] / tcy["PD calme (%)"].replace(0, np.nan)
print(tcy.round(2).to_string())
```
<!--sortie-->
```text
        PD calme (%)  PD récession (%)  défauts calme  défauts récession  rapport
note 1          0.07              0.00              1                  0     0.00
note 2          0.08              0.08              3                  1     1.04
note 3          0.13              0.49              8                  9     3.85
note 4          0.45              1.11             28                 18     2.46
note 5          1.39              4.71             46                 49     3.38
note 6          4.95             14.07             79                 76     2.84
note 7         24.49             51.55            167                133     2.11
```

```python hide
z_c = np.mean([-0.3, -0.5, -0.3, 0.0, -0.4, -0.5]); z_r = np.mean([1.4, 1.3])
print("NUM rap_cycle", [None if np.isnan(x) else round(float(x), 2) for x in tcy["rapport"]]); print("NUM facteur_prog", round(float(np.exp(0.6 * (z_r - z_c))), 2))
print("NUM pd_calme", [round(float(x), 2) for x in tcy["PD calme (%)"]]); print("NUM pd_rec", [round(float(x), 2) for x in tcy["PD récession (%)"]])
print("NUM n_calme", int(nd_c[:, 1:].sum())); print("NUM n_rec", int(nd_r[:, 1:].sum()))
```
<!--sortie-->
```text
NUM rap_cycle [0.0, 1.04, 3.85, 2.46, 3.38, 2.84, 2.11]
NUM facteur_prog 2.75
NUM pd_calme [0.07, 0.08, 0.13, 0.45, 1.39, 4.95, 24.49]
NUM pd_rec [0.0, 0.08, 0.49, 1.11, 4.71, 14.07, 51.55]
NUM n_calme 23483
NUM n_rec 7073
```

Pour les notes de milieu d'échelle (de 3 à 6), la **probabilité de défaut est multipliée par 2,5 à 3,9** en récession : pour la note 5, de 1,4 % à 4,7 %. Pour les deux premières notes, les défauts sont si rares (de zéro à trois par sous-période) que le rapport n'a pas de sens : c'est la limite de toute estimation de transitions rares. Pour la note 7, le rapport est de 2,1 seulement : une PD déjà élevée (24,5 % en période calme) ne peut pas être multipliée par plus de 4. Le facteur programmé dans le simulateur, qui multiplie les probabilités brutes de dégradation par $e^{0{,}6\,\Delta z}\approx2{,}75$ avant renormalisation, retrouve cet ordre de grandeur.

> 💡 **« Sur le cycle » ou « à la date » ?** La matrice moyenne (1.6.2) convient à un horizon long et au capital, qui doit survivre à une crise. La matrice d'une année donnée (ou d'un état de la conjoncture) convient aux provisions (section 1.5), qui doivent refléter la situation et les perspectives. Utiliser la moyenne pour provisionner **sous-estime** la perte d'une récession et **surestime** celle d'une expansion. Les établissements estiment pour cela des matrices **conditionnelles** à un indicateur de conjoncture, ce que l'on fait ici de la façon la plus simple : une matrice par régime.

### 1.6.4 La probabilité de défaut à plusieurs années

La force d'une matrice est de donner la PD à **horizon $n$ années**. Si les transitions sont indépendantes d'une année à l'autre (propriété de Markov) et si la matrice est la même chaque année (homogénéité), la matrice à $n$ ans est la puissance $n$ de la matrice annuelle : $P^{(n)}=P^n$. Avec le défaut absorbant, la dernière colonne de $P^n$ est la **probabilité de défaut cumulée** à $n$ ans pour chaque note de départ.

```python
M_abs = np.vstack([M_hat, np.r_[np.zeros(7), 1.0]])       # ajoute la ligne « défaut → défaut » : l'état est absorbant
PD_5 = np.linalg.matrix_power(M_abs, 5)[:7, 7]             # défaut cumulé à 5 ans, note par note
print((100 * PD_5).round(1))
```
<!--sortie-->
```text
[ 0.4  1.2  2.7  6.5 17.  39.3 76.5]
```

À 5 ans, la note 1 a 0,4 % de risque cumulé et la note 7 en a 76,5 % : trois emprunteurs sur quatre sont en défaut avant cinq ans. Comparons cette prédiction à ce que l'on observe réellement, en suivant la **cohorte initiale** (les 5 000 emprunteurs de l'année 0, suivis sur cinq ans, les retraits étant traités comme des sorties sans défaut), et à la valeur vraie $P^5$ de la matrice neutre :

```python hide-code
Mv_abs = np.vstack([P_vrai, np.r_[np.zeros(7), 1.0]])
pd5_vrai = np.linalg.matrix_power(Mv_abs, 5)[:7, 7]
init = panel[panel["annee"] == 0].set_index("id_emprunteur")["note_debut"]
obs5 = []
for k in range(1, 8):
    sub = panel[panel["id_emprunteur"].isin(init[init == k].index)]
    S = 1.0
    for a in range(5):
        s_a = sub[sub["annee"] == a]
        S *= 1 - (s_a["note_fin"] == 8).sum() / len(s_a)
    obs5.append(1 - S)
t5 = pd.DataFrame({"matrice estimée (%)": 100 * PD_5, "matrice vraie (%)": 100 * pd5_vrai, "cohorte 0 observée (%)": 100 * np.array(obs5)}, index=[f"note {i}" for i in range(1, 8)]).round(1)
print(t5.to_string())
```
<!--sortie-->
```text
        matrice estimée (%)  matrice vraie (%)  cohorte 0 observée (%)
note 1                  0.4                0.6                     0.5
note 2                  1.2                1.0                     0.8
note 3                  2.7                2.0                     1.1
note 4                  6.5                5.0                     5.2
note 5                 17.0               13.3                    10.8
note 6                 39.3               31.7                    28.1
note 7                 76.5               69.5                    63.0
```

```python hide
print("NUM pd5", {"est": [round(float(x), 3) for x in PD_5], "vrai": [round(float(x), 3) for x in pd5_vrai], "obs": [round(float(x), 3) for x in obs5]})
fig, ax = plt.subplots(figsize=(8.0, 3.8))
for k, col in [(3, AQUA), (5, BLEU), (6, ORANGE), (7, ROUGE)]:
    cum = [np.linalg.matrix_power(M_abs, n)[k - 1, 7] * 100 for n in range(0, 11)]
    cumv = [np.linalg.matrix_power(Mv_abs, n)[k - 1, 7] * 100 for n in range(0, 11)]
    ax.plot(range(0, 11), cum, color=col, lw=2, label=f"note {k}")
    ax.plot(range(0, 11), cumv, color=col, lw=1.2, ls="--")
ax.set_xlabel("horizon (années)"); ax.set_ylabel("probabilité de défaut cumulée (%)"); ax.legend(frameon=False, fontsize=9, loc="upper left")
ax.set_title("trait plein : matrice estimée ; tirets : matrice vraie (année neutre)", fontsize=9)
fig.tight_layout(); fig.savefig("figures/ch01-pd-cumulee.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```
<!--sortie-->
```text
NUM pd5 {'est': [0.004, 0.012, 0.027, 0.065, 0.17, 0.393, 0.765], 'vrai': [0.006, 0.01, 0.02, 0.05, 0.133, 0.317, 0.695], 'obs': [0.005, 0.008, 0.011, 0.052, 0.108, 0.281, 0.63]}
```

![Probabilité de défaut cumulée selon l'horizon, pour quatre notes de départ : la matrice estimée sur dix ans (trait plein) est plus sombre que la matrice neutre (tirets), et l'écart se creuse avec l'horizon.](figures/ch01-pd-cumulee.png)

Trois lectures. **Premièrement**, la PD cumulée croît **plus vite que proportionnellement** au nombre d'années pour les notes **bonnes** (note 3 : 2,7 % à 5 ans pour 0,23 % à un an, soit douze fois plus pour cinq fois plus de temps), parce que ces emprunteurs migrent d'abord vers des notes plus risquées avant de faire défaut ; elle s'**aplatit** pour les notes très mauvaises (saturation). **Deuxièmement**, la matrice estimée donne des PD à 5 ans plus fortes que la matrice neutre (note 5 : 17,0 % contre 13,3 %), puisqu'elle intègre la récession : les erreurs **se cumulent** avec l'horizon. **Troisièmement**, la cohorte de l'année 0, qui traverse les années 0 à 4, donc **avant** la récession, observe moins de défauts que les deux matrices (note 5 : 10,8 %) : la matrice annuelle moyenne n'est ni la cohorte passée ni la cohorte à venir. L'écart n'est pas une erreur de calcul : c'est la différence entre **la moyenne du cycle** et **un morceau particulier du cycle**.

### 1.6.5 Les hypothèses : Markov, homogénéité

Le calcul $P^n$ suppose deux choses, qu'on **teste** avant de s'y fier.

**La propriété de Markov** : la note de demain ne dépend que de celle d'aujourd'hui, pas du chemin parcouru. Dans la réalité, il existe souvent un **effet d'élan** (*momentum*) : un emprunteur récemment dégradé a plus de chances de l'être encore que celui qui est resté stable. Testons-le sur les emprunteurs notés 4 : sont-ils plus risqués s'ils viennent de **plus haut** (ils ont été dégradés), de **plus bas** (ils se sont améliorés) ou s'ils étaient déjà 4 l'année précédente ?

```python hide-code
pan = panel.sort_values(["id_emprunteur", "annee"]).copy()
pan["prec"] = pan.groupby("id_emprunteur")["note_debut"].shift(1)
sub4 = pan[(pan["note_debut"] == 4) & pan["prec"].notna()].copy()
sub4["origine"] = np.where(sub4["prec"] < 4, "vient d'une note meilleure", np.where(sub4["prec"] > 4, "vient d'une note moins bonne", "était déjà 4"))
issue = np.where(sub4["note_fin"] == 8, "défaut", np.where(sub4["note_fin"] > 4, "dégradé", np.where((sub4["note_fin"] < 4) & (sub4["note_fin"] > 0), "amélioré", np.where(sub4["note_fin"] == 4, "inchangé", "sorti"))))
tm = pd.crosstab(sub4["origine"], issue)
tm_pct = (100 * tm.div(tm.sum(axis=1), axis=0)).round(1)
print(tm_pct.to_string()); print(f"test du khi-deux d'indépendance : p = {chi2_contingency(tm)[1]:.2f}")
```
<!--sortie-->
```text
col_0                         amélioré  défaut  dégradé  inchangé  sorti
origine                                                                 
vient d'une note meilleure         7.1     0.4      9.2      80.7    2.6
vient d'une note moins bonne       8.7     0.9      9.6      77.5    3.3
était déjà 4                       7.7     0.6      9.5      78.1    4.2
test du khi-deux d'indépendance : p = 0.49
```

```python hide
print("NUM markov_p", round(float(chi2_contingency(tm)[1]), 2)); print("NUM markov_n", [int(x) for x in tm.sum(axis=1)])
```
<!--sortie-->
```text
NUM markov_p 0.49
NUM markov_n [693, 426, 7247]
```

Les distributions d'issue sont **semblables** quelle que soit l'origine (la probabilité de dégradation reste autour de 9 à 10 %, celle de défaut, sous 1 %) et le test d'indépendance donne $p=0{,}49$ : nous **ne détectons aucun effet d'élan**, ce qui est cohérent avec la vérité, puisque nos données ont été simulées avec des transitions de Markov. Sur des données réelles, ce test conclut souvent le contraire, et l'on enrichit alors le modèle (l'état devient la note **et** la note précédente, ou la durée dans la note).

**L'homogénéité dans le temps** est, elle, manifestement **fausse** ici : on vient de voir que deux années sur dix multiplient les défauts par trois. Un test d'homogénéité formel compare les matrices de deux périodes (khi-deux de comparaison ligne par ligne) ; il rejette massivement pour les notes de milieu d'échelle. Conséquence pratique : la puissance $P^n$ d'une matrice moyenne est une **approximation**, valable en moyenne sur un cycle et trompeuse un jour de crise.

### 1.6.6 Un mot sur le temps continu

Une année est un pas arbitraire : on voudrait la probabilité de transition sur six mois, ou sur dix-huit. Le modèle à **temps continu** décrit les transitions par un **générateur** $Q$ (taux instantanés de passage d'une note à l'autre) tel que $P(t)=e^{tQ}$. On l'obtient formellement par le **logarithme matriciel** $Q=\ln P$, que l'on peut calculer sur la matrice estimée :

```python hide-code
Q = logm(M_abs).real
hors_diag = Q - np.diag(np.diag(Q))
print(f"coefficients hors diagonale négatifs : {int((hors_diag < -1e-6).sum())}  (le plus bas : {hors_diag.min():.3f})")
print((np.round(Q[:3, :4], 3)))
```
<!--sortie-->
```text
coefficients hors diagonale négatifs : 7  (le plus bas : -0.001)
[[-0.107  0.097  0.01  -0.001]
 [ 0.044 -0.145  0.079  0.013]
 [ 0.005  0.071 -0.176  0.074]]
```

```python hide
print("NUM q_neg", int((hors_diag < -1e-6).sum())); print("NUM q_min", round(float(hors_diag.min()), 3))
```
<!--sortie-->
```text
NUM q_neg 7
NUM q_min -0.001
```

Le logarithme de la matrice estimée contient 7 **taux négatifs** (très petits : −0,001 au plus bas, dans les transitions les plus rares), ce qui n'a pas de sens pour un taux de passage. Une matrice annuelle est dite **plongeable** (*embeddable*) quand un générateur valide existe ; l'estimée ne l'est pas. On la **régularise** alors (on remplace les taux négatifs par zéro et l'on renormalise la diagonale) ou l'on estime directement le générateur à partir des durées passées dans chaque note, ce qui est une autre méthode (l'estimateur de durée, à temps continu). Retenez la précaution : **la racine carrée ou le logarithme d'une matrice de transition n'est pas toujours une matrice de transition**.

> ✅ **À retenir.**
> - Une **matrice de transition** est une matrice stochastique dont la dernière colonne est la PD à un an ; le défaut est **absorbant**. L'estimateur par **cohortes** est un simple rapport d'effectifs ; son incertitude se mesure par un bootstrap **par emprunteur**.
> - Les **transitions rares** sont mal estimées ; les notes extrêmes ont peu d'observations.
> - La conjoncture **déforme** la matrice : en récession, la PD des notes intermédiaires est multipliée par 2,5 à 3,9 dans nos données. Une matrice moyenne sert le capital, une matrice conditionnelle sert les provisions.
> - La PD à $n$ ans est la dernière colonne de $P^n$, sous les hypothèses de **Markov** et d'**homogénéité**, qu'on teste : ici, pas d'effet d'élan, mais une forte hétérogénéité temporelle.
> - Le logarithme d'une matrice estimée n'est pas toujours un générateur valide.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.8, exercices 1.13 et 1.14.
