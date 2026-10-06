## ➕ 4.7 Surveillance des modèles et détection de dérive

*Section complémentaire : elle prolonge 4.3 (supervision) en quantifiant la dérive et en décidant quoi en faire.*

Un modèle est appris sur le **passé** et appliqué à l'**avenir** ; il ne reste juste que tant que l'avenir ressemble au passé. La **dérive** (*drift*) désigne tout changement qui rompt cette ressemblance. La section 4.3 a montré qu'on la détecte tard par les étiquettes, et plus tôt, mais imparfaitement, par les entrées et les scores. Nous allons ici distinguer ses formes, construire deux outils de mesure (le PSI et le test de Kolmogorov-Smirnov), simuler un mois de production, et regarder ce qu'il faut en conclure.

### Trois formes de dérive

Un modèle de résiliation apprend, en gros, une relation entre des variables $x$ (récence, satisfaction, nombre de commandes…) et une étiquette $y$ (résilier ou non). Tout le jeu de données se résume à la loi conjointe, qui se factorise de deux façons :
$$
P(x, y) \;=\; P(y \mid x)\, P(x) \;=\; P(x \mid y)\, P(y).
$$
La première factorisation désigne deux endroits où le monde peut changer, et la seconde un troisième.

| Forme | Ce qui change | Exemple dans la boutique | Visible sans étiquettes ? | Effet sur le modèle |
|---|---|---|---|---|
| **Dérive des variables** (*covariate shift*) | $P(x)$ : les clients ne sont plus les mêmes | arrivée de clients attirés par les promotions | **oui** (les entrées changent) | souvent modéré, si $P(y \mid x)$ reste vraie ; fort si l'on sort du domaine d'apprentissage |
| **Dérive de l'étiquette** (*label shift*) | $P(y)$ : le taux de résiliation change | un concurrent s'installe, la résiliation passe de 14 % à 20 % | partiellement (les scores montent) | calibrage faussé, classement parfois préservé |
| **Dérive du concept** (*concept drift*) | $P(y \mid x)$ : **la relation** change | une campagne de rétention retient les clients que le modèle signale ; un changement de politique de retours | **non** | le modèle devient faux, sans que les entrées bougent |

Cette dernière est la plus dangereuse et la plus subtile : elle survient notamment **quand le modèle sert à agir**. Si la boutique relance les clients dont le score est élevé, et que la relance réussit, ces clients ne résilient finalement pas : **le modèle a modifié le monde qu'il prédit**, et la relation que ses données d'apprentissage décrivaient n'existe plus. Nous le simulons plus bas.

### Mesurer un changement de distribution : le PSI

L'**indice de stabilité de population** (PSI, *population stability index*) compare la distribution d'une variable dans la population de référence (celle de l'entraînement) à celle d'une période récente. On découpe d'abord la plage de la variable en $k$ **intervalles** (en général les 10 déciles de la référence), de sorte que chacun contient 10 % de la référence. Si $p_i$ est la part de la référence dans l'intervalle $i$ et $q_i$ celle de la période récente, le PSI vaut
$$
\text{PSI} \;=\; \sum_{i=1}^{k} (q_i - p_i)\,\ln\frac{q_i}{p_i}.
$$
Cette formule n'est pas arbitraire : c'est la somme des deux **divergences de Kullback-Leibler** dans les deux sens, car
$$
\underbrace{\sum_i q_i \ln\frac{q_i}{p_i}}_{\mathrm{KL}(q \,\|\, p)} + \underbrace{\sum_i p_i \ln\frac{p_i}{q_i}}_{\mathrm{KL}(p \,\|\, q)} \;=\; \sum_i (q_i - p_i)\ln\frac{q_i}{p_i}.
$$
Le PSI est donc **symétrique**, nul si les deux distributions sont identiques, positif sinon, et chaque terme $(q_i - p_i)\ln(q_i/p_i)$ est lui-même positif (les deux facteurs ont le même signe), ce qui permet de voir **quel intervalle** contribue le plus. Un exemple à la main, avec trois intervalles : la référence a pour parts $(0{,}5\;;\;0{,}3\;;\;0{,}2)$ et la période récente $(0{,}3\;;\;0{,}3\;;\;0{,}4)$.

```python hide
p_ref, q_new = np.array([0.5, 0.3, 0.2]), np.array([0.3, 0.3, 0.4])
termes = (q_new - p_ref) * np.log(q_new / p_ref)
NUM("t1", round(termes[0], 4)); NUM("t2", round(termes[1], 4)); NUM("t3", round(termes[2], 4)); NUM("psi_main", round(termes.sum(), 4))
kl_qp, kl_pq = (q_new * np.log(q_new / p_ref)).sum(), (p_ref * np.log(p_ref / q_new)).sum()
assert abs(kl_qp + kl_pq - termes.sum()) < 1e-12
```
<!--sortie-->
```text
NUM t1 0.1022
NUM t2 0.0
NUM t3 0.1386
NUM psi_main 0.2408
```

Les trois termes valent $(0{,}3-0{,}5)\ln(0{,}3/0{,}5) = 0{,}1022$, $0$ (l'intervalle central n'a pas bougé) et $(0{,}4-0{,}2)\ln(0{,}4/0{,}2) = 0{,}1386$, soit un PSI de **0,2408**. Les conventions usuelles (héritées de la notation de crédit, et à prendre comme des **repères** plutôt que des lois) lisent : PSI inférieur à 0,1 : stable ; entre 0,1 et 0,25 : changement modéré, à regarder ; au-delà de 0,25 : changement majeur. Deux précautions : le PSI dépend du **découpage** (10 intervalles ou 20) et il est bruité sur de petits échantillons ; et une variable qui change beaucoup mais qui **pèse peu** dans le modèle compte moins qu'une variable importante qui change un peu.

### Tester un changement de distribution : Kolmogorov-Smirnov

Le **test de Kolmogorov-Smirnov** à deux échantillons (volume I) compare deux **fonctions de répartition empiriques** $F_{\text{ref}}$ et $F_{\text{new}}$. Sa statistique est le plus grand écart vertical entre elles :
$$
D = \sup_x \bigl| F_{\text{ref}}(x) - F_{\text{new}}(x) \bigr|.
$$
Pour la calculer, il suffit de regarder les écarts aux points de l'échantillon réunis.

```python
def ks_stat(a, b):
    tout = np.sort(np.concatenate([a, b]))
    Fa = np.searchsorted(np.sort(a), tout, side="right") / len(a)
    Fb = np.searchsorted(np.sort(b), tout, side="right") / len(b)
    return np.abs(Fa - Fb).max()
```

```python hide
from scipy import stats
rng = np.random.default_rng(3)
a_ks, b_ks = rng.normal(0, 1, 800), rng.normal(0.3, 1, 800)
D_main, D_scipy = ks_stat(a_ks, b_ks), stats.ks_2samp(a_ks, b_ks).statistic
NUM("D_main", round(D_main, 4)); NUM("p_main", f"{stats.ks_2samp(a_ks, b_ks).pvalue:.1e}")
assert abs(D_main - D_scipy) < 1e-12
```
<!--sortie-->
```text
NUM D_main 0.1612
NUM p_main 1.7e-09
```

Sur deux échantillons de 800 valeurs, d'espérances 0 et 0,3 (écart-type 1), notre fonction donne $D = 0{,}1612$, la valeur exacte rendue par `scipy.stats.ks_2samp`, dont la loi sous l'hypothèse « mêmes distributions » donne la valeur-p. La valeur-p dit si l'écart est **statistiquement distinguable du hasard**, pas s'il est **important**. Le contraste est net quand l'échantillon grossit : un décalage minuscule (0,05 écart-type) finit toujours par être « significatif », alors que le PSI, lui, reste négligeable :

```python hide
rng = np.random.default_rng(3)
fmt_p = lambda p: f"{p:.2f}" if p >= 0.001 else f"{p:.0e}"
lignes = []
for n in (500, 5000, 50000):
    a_, b_ = rng.normal(0, 1, n), rng.normal(0.05, 1, n)
    lignes.append((n, stats.ks_2samp(a_, b_).pvalue, psi(a_, b_)))
    NUM(f"ks_p_{n}", fmt_p(lignes[-1][1])); NUM(f"ks_psi_{n}", round(lignes[-1][2], 4))
tab_ks = pd.DataFrame({"taille de chaque échantillon": [l[0] for l in lignes], "valeur-p KS": [fmt_p(l[1]) for l in lignes], "PSI": [round(l[2], 4) for l in lignes]})
assert lignes[2][1] < 0.05 and lignes[2][2] < 0.01
```
<!--sortie-->
```text
NUM ks_p_500 0.96
NUM ks_psi_500 0.0277
NUM ks_p_5000 0.12
NUM ks_psi_5000 0.0032
NUM ks_p_50000 7e-06
NUM ks_psi_50000 0.0015
```

```python hide-code
print(tab_ks.to_string(index=False))
```
<!--sortie-->
```text
 taille de chaque échantillon valeur-p KS    PSI
                          500        0.96 0.0277
                         5000        0.12 0.0032
                        50000       7e-06 0.0015
```

Avec 500 valeurs par échantillon, le test ne voit rien (p = 0,96) ; avec 50 000, il rejette l'égalité ($p \approx 7\times10^{-6}$) pour un écart de 0,0015 de PSI, bien en dessous de tout seuil d'inquiétude. **En production on regarde donc l'ampleur du changement (PSI, écart de moyennes) et on réserve le test aux petits échantillons**, où il évite de réagir au bruit.

### Un mois de production simulé

Reprenons le modèle de version 2 et simulons quatre semaines de 800 clients tirés du réservoir de production, dans deux scénarios, avec une dérive de plus en plus forte d'une semaine à la suivante :

- **dérive des variables** : la population change (plus de clients sensibles aux promotions, moins de clients satisfaits), la relation entre variables et résiliation reste la même ;
- **dérive du concept** : la population est identique, mais une campagne de rétention retient une part croissante des clients que **le modèle signale** (score au moins égal à 0,30) : ils ne résilient finalement pas.

Pour chaque semaine, on mesure le PSI de deux variables par rapport à l'entraînement, la valeur-p du test KS sur la part d'achats en promotion, la précision attendue sans étiquettes (4.3), et — une fois les étiquettes arrivées — la précision réelle et l'AUC.

```python hide
def suivi_semaines(scenario):
    lignes = []
    for k in range(1, 5):
        Xw, yw = semaine(d, v2, k, scenario)
        p = v2.predict_proba(Xw)[:, 1]; sig = p >= 0.30
        lignes.append({"semaine": k, "PSI promo": psi(Xtr["part_achats_promo"], Xw["part_achats_promo"]),
                       "PSI satisf.": psi(Xtr["satisfaction_moy"], Xw["satisfaction_moy"]),
                       "KS p (promo)": f"{stats.ks_2samp(Xtr['part_achats_promo'].dropna(), Xw['part_achats_promo'].dropna()).pvalue:.0e}",
                       "préc. attendue": p[sig].mean(), "préc. réelle": yw[sig].mean(), "AUC": roc_auc_score(yw, p)})
    return pd.DataFrame(lignes)
mois = {s: suivi_semaines(s) for s in ("covariable", "concept")}
cov, con = mois["covariable"], mois["concept"]
for k in range(4):
    NUM(f"cov_psi{k + 1}", round(cov.loc[k, "PSI promo"], 2)); NUM(f"cov_auc{k + 1}", round(cov.loc[k, "AUC"], 3))
    NUM(f"con_psi{k + 1}", round(con.loc[k, "PSI promo"], 2)); NUM(f"con_auc{k + 1}", round(con.loc[k, "AUC"], 3))
NUM("con_att4", round(100 * con.loc[3, "préc. attendue"])); NUM("con_reel4", round(100 * con.loc[3, "préc. réelle"]))
assert cov.loc[3, "PSI promo"] > 0.1 > con.loc[3, "PSI promo"] and cov["AUC"].min() > 0.85 and con.loc[3, "AUC"] < cov.loc[3, "AUC"] - 0.05
```
<!--sortie-->
```text
NUM cov_psi1 0.02
NUM cov_auc1 0.876
NUM con_psi1 0.02
NUM con_auc1 0.876
NUM cov_psi2 0.11
NUM cov_auc2 0.859
NUM con_psi2 0.02
NUM con_auc2 0.847
NUM cov_psi3 0.35
NUM cov_auc3 0.869
NUM con_psi3 0.01
NUM con_auc3 0.808
NUM cov_psi4 0.79
NUM cov_auc4 0.857
NUM con_psi4 0.0
NUM con_auc4 0.776
NUM con_att4 63
NUM con_reel4 10
```

Dérive des **variables** (la population change) :

```python hide-code
print(cov.round(3).to_string(index=False))
```
<!--sortie-->
```text
 semaine  PSI promo  PSI satisf. KS p (promo)  préc. attendue  préc. réelle   AUC
       1      0.015        0.014        9e-02           0.618         0.655 0.876
       2      0.106        0.074        1e-12           0.609         0.553 0.859
       3      0.345        0.384        4e-45           0.635         0.571 0.869
       4      0.795        0.713       7e-103           0.637         0.552 0.857
```

Dérive du **concept** (la population est la même, la relation change) :

```python hide-code
print(con.round(3).to_string(index=False))
```
<!--sortie-->
```text
 semaine  PSI promo  PSI satisf. KS p (promo)  préc. attendue  préc. réelle   AUC
       1      0.015        0.014        9e-02           0.618         0.655 0.876
       2      0.023        0.008        8e-01           0.655         0.467 0.847
       3      0.008        0.007        5e-01           0.647         0.269 0.808
       4      0.002        0.006        9e-01           0.633         0.100 0.776
```

Les deux scénarios racontent **des histoires opposées**.

- Quand la **population change**, le PSI de la part d'achats en promotion monte de 0,02 à 0,79 en quatre semaines : l'alarme est franche. Mais **l'AUC ne bouge presque pas** (0,876 puis 0,857) : le modèle a appris une relation qui reste vraie, il l'applique à des clients différents. La dérive est réelle mais **sans conséquence grave** ; ré-entraîner ne s'impose pas, il faut surtout surveiller.
- Quand le **concept change**, le PSI reste à 0,02, 0,0 : **aucune alarme sur les entrées**. L'estimation sans étiquettes annonce toujours une précision d'environ 63 %, alors que la précision réelle de la semaine 4 est de 10 % et que l'AUC passe de 0,876 à 0,776. C'est l'angle mort de la surveillance par les entrées : **la dérive la plus coûteuse est justement celle qu'elle ne voit pas**.

```python hide
fig, axes = plt.subplots(1, 3, figsize=(12.4, 3.9))
sem = np.arange(1, 5)
a, b, c = axes
a.plot(sem, cov["PSI promo"], "o-", color=ORANGE, lw=2, label="dérive des variables")
a.plot(sem, con["PSI promo"], "s-", color=BLEU, lw=2, label="dérive du concept")
a.axhline(0.1, color=MUET, ls="--", lw=1); a.axhline(0.25, color=ROUGE, ls="--", lw=1)
a.text(1.05, 0.105, "0,1", fontsize=8, color=MUET); a.text(1.05, 0.255, "0,25", fontsize=8, color=ROUGE)
a.set_xticks(sem); a.set_xlabel("semaine"); a.set_ylabel("PSI (part d'achats en promotion)"); a.legend(fontsize=8); a.set_title("Ce que voient les entrées", fontsize=10)
b.plot(sem, cov["AUC"], "o-", color=ORANGE, lw=2); b.plot(sem, con["AUC"], "s-", color=BLEU, lw=2)
b.set_xticks(sem); b.set_xlabel("semaine"); b.set_ylabel("AUC (étiquettes arrivées)"); b.set_ylim(0.7, 0.95); b.set_title("Ce que subit le modèle", fontsize=10)
Xw4, _ = semaine(d, v2, 4, "covariable")
bins = np.linspace(0, 1, 21)
c.hist(Xtr["part_achats_promo"].dropna(), bins, density=True, alpha=0.55, color=MUET, label="entraînement")
c.hist(Xw4["part_achats_promo"].dropna(), bins, density=True, alpha=0.55, color=ORANGE, label="semaine 4")
c.set_xlabel("part d'achats en promotion"); c.set_ylabel("densité"); c.legend(fontsize=8); c.set_title("Dérive des variables : la distribution", fontsize=10)
fig.tight_layout(); style.save(fig, "ch04-derive.png")
```
<!--sortie-->
```text
figure : ch04-derive.png
```

![À gauche : PSI de la part d'achats en promotion pendant quatre semaines pour les deux scénarios, avec les seuils conventionnels de 0,1 et 0,25. Au centre : AUC mesurée une fois les étiquettes arrivées. À droite : distribution de cette variable à l'entraînement et à la semaine 4 du scénario de dérive des variables.](figures/ch04-derive.png)

> 💡 **Intuition.** Les entrées répondent à la question « **les clients ont-ils changé ?** », les étiquettes à la question « **le modèle se trompe-t-il ?** ». Les deux questions sont indépendantes : on peut avoir une réponse oui/non, non/oui, oui/oui ou non/non. D'où la règle : on surveille **les deux**, et l'on ne déclenche une action coûteuse que sur la seconde, ou sur la première **accompagnée** d'un indice d'impact (estimation sans étiquettes, variable importante).

### Que faire d'une dérive avérée ?

Constater la dérive n'est que la moitié du travail. Avant de ré-entraîner, on **diagnostique** : est-ce un **bug** en amont (une unité changée, comme en 4.1) ? Dans ce cas on corrige la source, on ne ré-entraîne pas sur des données fausses. Est-ce un **changement réel** ? Alors seulement, on choisit une politique de ré-entraînement :

| Politique | Principe | Atouts | Limites |
|---|---|---|---|
| **Calendaire** | ré-entraîner chaque mois / trimestre | simple, prévisible | gaspillage si rien n'a changé ; trop lent en cas de rupture |
| **Déclenchée** | quand la performance mesurée ou estimée tombe sous un seuil, ou qu'un PSI majeur touche une variable importante | réagit à ce qui compte | exige une bonne supervision (4.3) et des seuils réglés |
| **Continue** | mise à jour progressive du modèle à chaque nouveau lot | s'adapte vite | risque d'instabilité, plus difficile à tester |

Un ré-entraînement reste un **nouveau modèle** : il repasse par la porte de qualité de 4.6 et par un déploiement progressif (4.2). Testons sur le scénario de dérive du concept : le modèle gelé (appris sur les données d'origine) est comparé à deux versions ré-entraînées avec les étiquettes **arrivées entre-temps** (semaines 2 et 3), toutes évaluées sur la semaine 4.

```python hide
Xs, ys = [], []
for k in (2, 3):
    Xw, yw = semaine(d, v2, k, "concept"); Xs.append(Xw); ys.append(yw)
X4, y4 = semaine(d, v2, 4, "concept")
d_plus = dict(d, Xtr=pd.concat([d["Xtr"]] + Xs), ytr=pd.Series(np.concatenate([d["ytr"].to_numpy()] + ys)))
d_seul = dict(d, Xtr=pd.concat(Xs).reset_index(drop=True), ytr=pd.Series(np.concatenate(ys)))
v2_plus, v2_seul = modele_v2(d_plus), modele_v2(d_seul)
auc_gele, auc_plus, auc_seul = (roc_auc_score(y4, m.predict_proba(X4)[:, 1]) for m in (v2, v2_plus, v2_seul))
sig_ancien = v2.predict_proba(X4)[:, 1] >= 0.30
score_ancien, score_plus = v2.predict_proba(X4)[sig_ancien, 1].mean(), v2_plus.predict_proba(X4)[sig_ancien, 1].mean()
NUM("auc_gele", round(auc_gele, 3)); NUM("auc_plus", round(auc_plus, 3)); NUM("auc_seul", round(auc_seul, 3))
NUM("score_ancien", round(100 * score_ancien)); NUM("score_plus", round(100 * score_plus))
assert auc_plus > auc_gele and auc_seul > auc_gele and score_plus < score_ancien
tab_retrain = pd.DataFrame({"modèle": ["gelé (données d'origine)", "ré-entraîné : origine + semaines 2-3", "ré-entraîné : semaines 2-3 seules"], "AUC semaine 4": [auc_gele, auc_plus, auc_seul]})
```
<!--sortie-->
```text
NUM auc_gele 0.776
NUM auc_plus 0.891
NUM auc_seul 0.909
NUM score_ancien 63
NUM score_plus 48
```

```python hide-code
print(tab_retrain.round(3).to_string(index=False))
```
<!--sortie-->
```text
                              modèle  AUC semaine 4
            gelé (données d'origine)          0.776
ré-entraîné : origine + semaines 2-3          0.891
   ré-entraîné : semaines 2-3 seules          0.909
```

Le ré-entraînement fait remonter l'AUC de 0,776 à 0,891 (ou 0,909 avec les seules semaines récentes). **Il faut pourtant se méfier de ce succès.** Les étiquettes de ces semaines sont celles que **la campagne de rétention a modifiées** : les clients que l'ancien modèle signalait ont été retenus, donc étiquetés « n'a pas résilié ». Le nouveau modèle apprend à reconnaître ce motif : le score moyen des clients que l'ancien modèle signalait passe de 63 % à 48 % sous le nouveau. Il prédit donc **ce qui s'est passé après la campagne**, pas **qui risque de partir en l'absence de campagne**. Utilisé pour cibler la rétention, il cesserait de désigner justement les clients que l'on veut retenir : c'est une **boucle de rétroaction**.

> ⚠️ **Piège.** Quand le modèle déclenche une action qui modifie le résultat, les étiquettes collectées ensuite ne mesurent plus le risque d'origine. Le remède classique est de **réserver au hasard un petit groupe témoin** (par exemple 5 %) qui ne reçoit jamais l'action, et de n'utiliser que lui pour mesurer la performance réelle et ré-entraîner. C'est le raisonnement causal du volume II, chapitre 7 : on cherche l'effet de la relance, et pas seulement la prédiction de l'issue observée.

> 🧭 **En pratique.** Une surveillance complète tient en quatre éléments : un **suivi des entrées** (PSI sur les variables importantes, seuils réglés), un **suivi des scores** (distribution, estimation sans étiquettes), un **suivi des étiquettes** quand elles arrivent (avec un groupe témoin si le modèle agit), et un **processus de décision écrit** (qui est alerté, qui diagnostique, qui décide de ré-entraîner, avec quelles portes de contrôle).

> 📒 **Pour pratiquer.** Le cahier propose de simuler un mois de production en mesurant PSI, KS et AUC (application 4.8), de calculer un PSI à la main et de montrer qu'il se décompose en deux divergences de Kullback-Leibler (exercice 4.10), et d'écrire une politique de ré-entraînement avec groupe témoin (exercices 4.11 et 4.12).
