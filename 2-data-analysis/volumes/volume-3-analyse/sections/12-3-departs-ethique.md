## 12.3 Prédire les départs, et ce que l'on a le droit d'en faire

Cette section pose la question qui revient dans toutes les directions : *peut-on prédire qui va partir ?* Elle construit un modèle logistique sur nos données, mesure honnêtement sa performance, explique pourquoi un modèle fait sur vingt départs ne peut presque rien dire, **simule** ce qui aurait été détecté avec davantage de données, puis aborde ce qu'il faut se demander avant d'utiliser un tel modèle sur des personnes.

### 12.3.1 Poser le problème

L'unité d'analyse est la **ligne collaborateur-année** (245 lignes) et la cible est l'indicateur « part dans l'année » (20 départs). Les variables explicatives sont celles dont on peut raisonnablement penser qu'elles jouent : les **heures supplémentaires** par mois, le **compa-ratio** (le salaire relatif à la médiane du poste, section 12.2.5), une **promotion** au cours des trois dernières années, l'**évaluation** de l'année et l'**ancienneté**.

Avant d'ajuster quoi que ce soit, un calcul de bon sens : on a **20 événements** pour **5 variables**, soit **4 événements par variable**. Une règle de pouce de la statistique médicale réclame au moins dix événements par variable pour qu'une régression logistique soit stable. Nous sommes très en dessous : les coefficients seront imprécis, et un modèle trop complexe apprendra du bruit.

```python hide
NUM("epv", int(ea["depart_dans_l_annee"].sum()) / 5, 0)
NUM("taux_dep", ea["depart_dans_l_annee"].mean() * 100, 1)
```
<!--sortie-->
```text
NUM epv 4
NUM taux_dep 8.2
```

### 12.3.2 Un modèle logistique

La régression logistique (section 3.3) modélise le **logarithme du rapport de chances** de départ comme une combinaison linéaire des variables. On lit les coefficients sous forme d'**odds ratios** : un odds ratio de 1,10 signifie que la variable multiplie les chances de départ par 1,10 quand elle augmente d'une unité.

```python
ea["compa_10"] = (ea["compa_ratio"] - 1) * 10          # une unité = 10 points de compa-ratio
X = ea[["heures_sup_mensuelles", "compa_10", "promo_3ans", "evaluation", "anciennete"]]
y = ea["depart_dans_l_annee"]
res = sm.Logit(y, sm.add_constant(X)).fit(disp=0)
tab = pd.DataFrame({"odds ratio": np.exp(res.params), "bas": np.exp(res.conf_int()[0]), "haut": np.exp(res.conf_int()[1]), "p": res.pvalues}).drop("const")
print(tab.round(3))
```
<!--sortie-->
```text
                       odds ratio    bas   haut      p
heures_sup_mensuelles       0.963  0.822  1.129  0.644
compa_10                    0.338  0.096  1.187  0.090
promo_3ans                  1.257  0.260  6.069  0.776
evaluation                  0.765  0.397  1.474  0.423
anciennete                  0.964  0.782  1.188  0.731
```

```python hide
tab = tab.copy()
NUM("or_hs", tab.loc["heures_sup_mensuelles", "odds ratio"], 2); NUM("or_hs_bas", tab.loc["heures_sup_mensuelles", "bas"], 2); NUM("or_hs_haut", tab.loc["heures_sup_mensuelles", "haut"], 2)
NUM("p_min", tab["p"].min(), 2)
NUM("n_signif", int((tab["p"] < 0.05).sum()))
NUM("or_cr", tab.loc["compa_10", "odds ratio"], 2); NUM("or_cr_bas", tab.loc["compa_10", "bas"], 2); NUM("or_cr_haut", tab.loc["compa_10", "haut"], 2)
NUM("or_promo", tab.loc["promo_3ans", "odds ratio"], 2); NUM("or_promo_bas", tab.loc["promo_3ans", "bas"], 2); NUM("or_promo_haut", tab.loc["promo_3ans", "haut"], 2)
```
<!--sortie-->
```text
NUM or_hs 0.96
NUM or_hs_bas 0.82
NUM or_hs_haut 1.13
NUM p_min 0.09
NUM n_signif 0
NUM or_cr 0.34
NUM or_cr_bas 0.10
NUM or_cr_haut 1.19
NUM or_promo 1.26
NUM or_promo_bas 0.26
NUM or_promo_haut 6.07
```

**Aucune des cinq variables n'est significative** (0 sur 5 ; la plus petite p-valeur est de 0,09). L'odds ratio des heures supplémentaires par heure mensuelle est de 0,96 avec un intervalle de 0,82 à 1,13 : il contient 1 (pas d'effet), mais aussi des valeurs qui seraient importantes. Pour le salaire relatif (par tranche de 10 points de compa-ratio), l'odds ratio de 0,34 va de 0,10 à 1,19 : le sens est plausible (un salaire plus bas va avec plus de départs), mais l'intervalle contient 1. Pour la promotion récente, l'odds ratio de 1,26 s'accompagne d'un intervalle de 0,26 à 6,07, **extrêmement large** parce que seules quelques personnes ont été promues et sont parties. Un intervalle aussi large dit : « **nous ne savons pas** ».

### 12.3.3 Une performance mesurée honnêtement

Un modèle de prédiction se juge par sa performance **sur des personnes qu'il n'a pas vues**. Comme les données sont rares, on utilise la **validation croisée répétée** (on découpe cinq fois les données en cinq morceaux, vingt fois de suite, en gardant la proportion de départs ; pour aller plus loin, voir la série 1, volume III, section 1.2). L'indicateur est l'**AUC** (série 1, volume III, section 5.1) : la probabilité que le modèle attribue un risque plus élevé à une personne qui part qu'à une personne qui reste (0,5 = hasard, 1 = parfait).

```python
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
modele = make_pipeline(StandardScaler(), LogisticRegression(C=0.5, max_iter=1000))
auc = cross_val_score(modele, X, y, cv=RepeatedStratifiedKFold(n_splits=5, n_repeats=20, random_state=0), scoring="roc_auc")
print(round(auc.mean(), 2), round(auc.std(), 2), np.percentile(auc, [2.5, 97.5]).round(2))
```
<!--sortie-->
```text
0.53 0.11 [0.3  0.73]
```

```python hide
NUM("auc_moy", auc.mean(), 2); NUM("auc_sd", auc.std(), 2)
NUM("auc_bas", np.percentile(auc, 2.5), 2); NUM("auc_haut", np.percentile(auc, 97.5), 2)
rng = np.random.default_rng(5)
perm = [cross_val_score(modele, X, rng.permutation(y.values), cv=RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=i), scoring="roc_auc").mean() for i in range(60)]
NUM("p_perm", (np.array(perm) >= auc.mean()).mean() * 100, 0); NUM("perm_moy", np.mean(perm), 2)
```
<!--sortie-->
```text
NUM auc_moy 0.53
NUM auc_sd 0.11
NUM auc_bas 0.30
NUM auc_haut 0.73
NUM p_perm 33
NUM perm_moy 0.49
```

L'AUC moyenne en validation croisée est de **0,53**, très proche du hasard (0,5), avec une dispersion de 0,11 d'un découpage à l'autre : l'intervalle va de 0,30 à 0,73. Pour savoir si ce score est distinguable du hasard, on le compare à celui qu'on obtiendrait avec des départs **mélangés au hasard** (test de permutation) : la moyenne sous le hasard est de 0,49 et la part des tirages au hasard qui font aussi bien que notre modèle est de 33 % : **ce modèle ne prédit pas mieux que le hasard**.

> 🧭 **En pratique.** Ce résultat n'est pas un échec de l'analyste : c'est une **information utile pour la direction**. Elle apprend que, avec ces données, un « score de risque de départ » individuel serait un **tirage au sort habillé de statistiques**. Ne pas le construire est une décision d'analyste.

### 12.3.4 Ce que la vérité programmée dit : la puissance qui manque

Les départs ont été fabriqués selon une règle connue : le **risque augmente** avec les heures supplémentaires (coefficient de 0,07 par heure mensuelle, soit un odds ratio de 1,07), **baisse** après une promotion récente (coefficient de −0,8), baisse avec une meilleure évaluation et avec l'ancienneté, et dépend légèrement du salaire relatif. Ces effets **existent**, et notre analyse ne les voit pas. Pourquoi ? Parce qu'avec 20 événements, la **puissance** statistique est trop faible. On peut le mesurer : on simule cent autres entreprises de même taille, avec la même règle, et l'on regarde combien de fois l'analyse détecterait l'effet des heures supplémentaires.

```python
import donnees_a3 as G
detecte, coefs = 0, []
for graine in range(100):
    _, panel, _ = G.rh(seed=9000 + graine)
    panel = panel.sort_values(["id_employe", "annee"])
    panel["compa_ratio"] = panel["salaire_brut_mensuel"] / panel.groupby(["poste", "annee"])["salaire_brut_mensuel"].transform("median")
    panel["promo_3ans"] = panel.groupby("id_employe")["promotion"].transform(lambda s: s.rolling(3, min_periods=1).max())
    panel["compa_10"] = (panel["compa_ratio"] - 1) * 10
    r = sm.Logit(panel["depart_dans_l_annee"], sm.add_constant(panel[X.columns])).fit(disp=0)
    coefs.append(r.params["heures_sup_mensuelles"]); detecte += int(r.pvalues["heures_sup_mensuelles"] < 0.05 and r.params["heures_sup_mensuelles"] > 0)
print(detecte, "détections sur 100 | coefficient moyen :", round(np.mean(coefs), 3))
```
<!--sortie-->
```text
18 détections sur 100 | coefficient moyen : 0.068
```

```python hide
NUM("detecte", detecte); NUM("coef_moy", np.mean(coefs), 3); NUM("coef_sd", np.std(coefs), 3)
fig, ax = plt.subplots(figsize=(6.6, 3.3))
ax.hist(coefs, bins=18, color=BLEU, alpha=0.85)
ax.axvline(0.07, color=ORANGE, lw=2); ax.text(0.074, ax.get_ylim()[1] * 0.9, "vérité : 0,07", color=ORANGE, fontsize=9)
ax.axvline(0, color=MUET, lw=1, ls=":")
ax.set_xlabel("Coefficient estimé des heures supplémentaires (une entreprise simulée = un tirage)"); ax.set_ylabel("Nombre de tirages")
ax.set_title("L'effet existe, mais chaque échantillon l'estime très mal", loc="left")
fig.savefig("figures/ch12-puissance.png", dpi=200, bbox_inches="tight"); plt.close(fig)
panels = []
for i in range(40):
    _, p_, _ = G.rh(seed=9000 + i)
    p_ = p_.sort_values(["id_employe", "annee"]).assign(id_employe=lambda d, i=i: d["id_employe"] + 1000 * i)
    p_["compa_ratio"] = p_["salaire_brut_mensuel"] / p_.groupby(["poste", "annee"])["salaire_brut_mensuel"].transform("median")
    p_["promo_3ans"] = p_.groupby("id_employe")["promotion"].transform(lambda s: s.rolling(3, min_periods=1).max())
    p_["compa_10"] = (p_["compa_ratio"] - 1) * 10
    panels.append(p_)
gros = pd.concat(panels)
rg = sm.Logit(gros["depart_dans_l_annee"], sm.add_constant(gros[X.columns])).fit(disp=0)
NUM("n_gros", len(gros)); NUM("ev_gros", int(gros["depart_dans_l_annee"].sum()))
assert rg.pvalues["heures_sup_mensuelles"] < 0.001
NUM("g_hs", rg.params["heures_sup_mensuelles"], 3)
NUM("g_promo", rg.params["promo_3ans"], 2); NUM("g_eval", rg.params["evaluation"], 2); NUM("g_anc", rg.params["anciennete"], 3)
```
<!--sortie-->
```text
NUM detecte 18
NUM coef_moy 0.068
NUM coef_sd 0.094
NUM n_gros 9 839
NUM ev_gros 707
NUM g_hs 0.066
NUM g_promo −0.69
NUM g_eval −0.37
NUM g_anc −0.055
```

![Distribution du coefficient estimé des heures supplémentaires dans cent entreprises simulées de même taille : la moyenne est proche de la vérité (0,07), mais l'étalement est tel que la plupart des tirages ne détectent pas l'effet.](figures/ch12-puissance.png)

L'analyse détecte l'effet des heures supplémentaires dans seulement **18 tirages sur 100**. Le coefficient estimé vaut en moyenne **0,068**, très près de la vérité (0,07) : l'estimateur n'est pas **biaisé**, mais il est **tellement dispersé** (écart-type de 0,094 d'un tirage à l'autre, soit davantage que l'effet lui-même) qu'un échantillon seul le noie. La **puissance** est faible : c'est le même phénomène que celui du test A/B de la section 2.5, appliqué à la régression.

Il suffit de regarder ce qui se passe avec beaucoup plus de données. En empilant 40 entreprises simulées (9 839 collaborateur-années, 707 départs), l'effet des heures supplémentaires est estimé à **0,066** (p-valeur inférieure à 0,001), la promotion récente à −0,69, l'évaluation à −0,37 et l'ancienneté à −0,055 : les effets programmés réapparaissent, avec les bons signes. La **vérité** est donc dans la règle ; ce qui manquait n'était pas la bonne méthode, mais **des données**.

> ⚠️ **Piège.** Une régression qui ne trouve « rien » n'a pas démontré que **rien** n'existe. Quand les effectifs sont faibles, « non significatif » veut dire « indécidable », pas « nul ». La seule manière honnête de le dire à la gérante est : *avec cinquante personnes, nous ne pouvons pas identifier ce qui fait partir ; nous pouvons seulement l'exclure pour les très gros effets.*

> 📒 **Pour s'entraîner.** Cahier, chapitre 12 : application 12.5, exercices 12.7 et 12.8.

### 12.3.5 Les limites éthiques d'un score de départ

Admettons que l'on ait **beaucoup** plus de données et un modèle qui marche. Faut-il pour autant s'en servir sur des personnes ? Cinq questions doivent précéder toute utilisation.

**À quoi servira-t-il, exactement ?** Un score de risque de départ peut orienter des actions positives (proposer un entretien, revoir une charge de travail, une rémunération) ou négatives (écarter une personne d'une promotion « parce qu'elle va partir », la surveiller davantage). La même statistique sert deux politiques opposées ; **c'est l'usage qui est bon ou mauvais, pas le calcul**.

**Que sait la personne ?** Les cadres de protection des données prévoient en général que les personnes soient **informées** des traitements qui les concernent, de leur finalité et de leurs droits (volume II, section 5.1). Un score calculé en secret est difficile à justifier.

**Le modèle est-il équitable ?** Même sans utiliser le genre ou l'âge, un modèle peut les **reconstituer** par des variables proches (poste, heures supplémentaires, temps partiel) et produire des scores systématiquement plus élevés pour un groupe. Il faut **auditer** le score par groupe, comme nous le faisons ci-dessous. Ce contrôle est nécessaire, pas suffisant.

**Que fait-on d'une erreur ?** À performance modeste, la plupart des personnes à « risque élevé » ne partiront pas, et certaines personnes à « risque faible » partiront. Traiter les premières comme des « futurs partants » est une injustice individuelle, que seule la transparence et une action **non pénalisante** peuvent éviter.

**Existe-t-il une alternative moins intrusive ?** Presque toujours : une **enquête d'engagement** anonyme, des **entretiens de départ** et de mi-carrière, des **statistiques d'équipe** (jamais d'individus) : elles répondent à la question de la gérante (« pourquoi partent-ils ? ») sans scorer personne.

```python hide
modele.fit(X, y)
ea["risque"] = modele.predict_proba(X)[:, 1]
rg_ = ea.groupby("genre")["risque"].mean() * 100
NUM("risque_f", rg_["F"], 1); NUM("risque_h", rg_["H"], 1); NUM("risque_moy", ea["risque"].mean() * 100, 1)
rp = ea.groupby("poste")["risque"].mean() * 100
NUM("risque_poste_min", rp.min(), 1); NUM("risque_poste_max", rp.max(), 1)
top = ea.nlargest(int(len(ea) * 0.1), "risque")
NUM("top_taux", top["depart_dans_l_annee"].mean() * 100, 1); NUM("top_n", len(top)); NUM("top_ev", int(top["depart_dans_l_annee"].sum()))
sans = make_pipeline(StandardScaler(), LogisticRegression(C=0.5, max_iter=1000)).fit(X.drop(columns="compa_10"), y)
ea["risque_sans"] = sans.predict_proba(X.drop(columns="compa_10"))[:, 1]
rs = ea.groupby("genre")["risque_sans"].mean() * 100
NUM("risque_f_sans", rs["F"], 1); NUM("risque_h_sans", rs["H"], 1)
```
<!--sortie-->
```text
NUM risque_f 9.2
NUM risque_h 6.9
NUM risque_moy 8.2
NUM risque_poste_min 7.5
NUM risque_poste_max 8.4
NUM top_taux 16.7
NUM top_n 24
NUM top_ev 4
NUM risque_f_sans 8.1
NUM risque_h_sans 8.2
```

Pour fixer les idées, voici un **audit** rapide du modèle ajusté. Le risque moyen prédit est de 8,2 % ; il est de 9,2 % pour les femmes et de 6,9 % pour les hommes, et va de 7,5 % à 8,4 % selon le poste. Parmi les 10 % de personnes au score le plus élevé (24 collaborateur-années), le taux de départ réel est de **16,7 %**, pour 8,2 % dans l'ensemble : soit **deux fois** le taux d'ensemble, mais sur 4 départs seulement : un résultat trop fragile pour guider une décision. Un point mérite l'attention : le modèle n'utilise pas le genre, et pourtant le risque prédit est plus élevé pour les femmes. La raison probable est leur **compa-ratio plus bas** (section 12.2.5) : sans cette variable, le risque prédit tombe à 8,1 % pour les femmes et 8,2 % pour les hommes. Un score fondé sur le salaire relatif **reproduit** donc l'écart de salaire. Retenons surtout le principe : **auditer par groupe, regarder l'écart réel entre score et résultat, et ne pas s'arrêter à l'AUC**.

> ✅ **À retenir.**
> - Avec **20 événements**, un modèle logistique ne peut identifier que des effets énormes ; on regarde l'**intervalle** des coefficients et l'**AUC en validation croisée**.
> - « Non significatif » veut dire « indécidable » quand la **puissance** est faible ; une simulation chiffre cette puissance.
> - Un **score individuel de départ** pose des questions d'**usage**, d'**information** des personnes, d'**équité** et d'**erreur** avant toute question technique.
> - Les **alternatives** (enquête d'engagement, entretiens, statistiques d'équipe) répondent mieux à la vraie question, sans scorer personne.
> - La **vérité programmée** (effets réels mais faibles) montre ce qu'un échantillon trop petit rate.
