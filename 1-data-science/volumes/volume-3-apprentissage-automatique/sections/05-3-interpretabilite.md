## 5.3 Interprétabilité

Un modèle de boosting de 150 arbres n'a pas de « formule » que l'on puisse lire. Pourtant, il faut pouvoir répondre à des questions simples : *quelles variables comptent ? Pourquoi ce client est-il signalé ? Le modèle a-t-il appris quelque chose de raisonnable, ou une erreur ?* Cette section présente les outils standard, du plus simple au plus fondé, et surtout leurs **limites**.

### 5.3.1 Expliquer quoi, et à qui ?

Une « explication » peut répondre à plusieurs questions, qu'il faut distinguer.

- **Globale ou locale.** Une explication *globale* décrit le comportement général du modèle (« la récence est la variable la plus déterminante »). Une explication *locale* décrit **une** prédiction (« ce client est signalé à 92 % surtout parce que sa dernière commande date de plus d'un an »).
- **Intrinsèque ou post hoc.** Certains modèles sont *interprétables par construction* : une régression logistique (chaque coefficient est un effet sur la cote, volume II, section 2.2), un arbre peu profond (section 2.2). Pour les autres, on applique après coup des méthodes qui interrogent le modèle comme une boîte noire.
- **Pour qui ?** La gérante veut une phrase ; le data scientist veut un diagnostic ; l'auditeur veut une traçabilité. L'explication utile dépend de l'usage.

Dans toute la section, le modèle expliqué est un **gradient boosting LightGBM** de 150 arbres (AUC de 0,902 et Brier de 0,0744 sur le jeu de test), entraîné sur les 7 200 clients d'entraînement.

> ⚠️ **Une explication explique le modèle, pas le monde.** Si le modèle dit « les clients de moins de 28 ans partent plus », l'explication le montrera fidèlement. Elle ne dit pas que *l'âge cause le départ* : elle dit que *le modèle utilise l'âge*. La confusion entre les deux est l'erreur la plus fréquente (voir 5.3.7).

```python hide
import lightgbm as lgb
import shap, itertools
from sklearn.inspection import permutation_importance
mg = lgb.LGBMClassifier(n_estimators=150, learning_rate=0.05, num_leaves=15, min_child_samples=40, subsample=0.8, subsample_freq=1, colsample_bytree=0.8,
                        random_state=0, verbose=-1, n_jobs=1).fit(Xtr, ytr)
pm = mg.predict_proba(Xte)[:, 1]
print("LightGBM : AUC", round(M.roc_auc_score(yte, pm), 4), "| Brier", round(M.brier_score_loss(yte, pm), 4))
pi_ = permutation_importance(mg, Xte, yte, scoring="roc_auc", n_repeats=5, random_state=0, n_jobs=1)
imp = pd.DataFrame({"variable": Xte.columns, "baisse d'AUC": pi_.importances_mean, "écart-type": pi_.importances_std}).sort_values("baisse d'AUC", ascending=False)
print(imp.head(10).round(4).to_string(index=False))
# --- deux variables corrélées se partagent l'importance : on ajoute une copie bruitée de recence_jours (écart-type 15 jours)
rng_d = np.random.default_rng(0)
Xtr_d, Xte_d = Xtr.copy(), Xte.copy()
Xtr_d["recence_copie"] = Xtr_d["recence_jours"] + rng_d.normal(0, 15, len(Xtr_d)); Xte_d["recence_copie"] = Xte_d["recence_jours"] + rng_d.normal(0, 15, len(Xte_d))
print("corrélation entre recence_jours et sa copie bruitée :", round(float(np.corrcoef(Xte_d["recence_jours"], Xte_d["recence_copie"])[0, 1]), 3))
mg_d = lgb.LGBMClassifier(n_estimators=150, learning_rate=0.05, num_leaves=15, min_child_samples=40, subsample=0.8, subsample_freq=1, colsample_bytree=0.8, random_state=0, verbose=-1, n_jobs=1).fit(Xtr_d, ytr)
pd_ = permutation_importance(mg_d, Xte_d, yte, scoring="roc_auc", n_repeats=5, random_state=0, n_jobs=1)
imp_d = pd.Series(pd_.importances_mean, index=Xte_d.columns)
print("importance de recence_jours : seule", round(float(imp.set_index("variable").loc["recence_jours", "baisse d'AUC"]), 4), "| avec une copie bruitée :", round(float(imp_d["recence_jours"]), 4), "(originale) et", round(float(imp_d["recence_copie"]), 4), "(copie), somme", round(float(imp_d["recence_jours"] + imp_d["recence_copie"]), 4))
print("AUC avec la copie bruitée :", round(M.roc_auc_score(yte, mg_d.predict_proba(Xte_d)[:, 1]), 4))
```
<!--sortie-->
```text
LightGBM : AUC 0.9017 | Brier 0.0744
                  variable  baisse d'AUC  écart-type
                       age        0.0655      0.0049
             recence_jours        0.0612      0.0073
          satisfaction_moy        0.0409      0.0029
               montant_12m        0.0403      0.0047
         part_achats_promo        0.0200      0.0022
        programme_fidelite        0.0088      0.0034
          nb_commandes_12m        0.0072      0.0013
             ville_Ville T        0.0025      0.0005
canal_acquisition_Boutique        0.0024      0.0006
             ville_Ville B        0.0019      0.0006
corrélation entre recence_jours et sa copie bruitée : 0.993
importance de recence_jours : seule 0.0612 | avec une copie bruitée : 0.0189 (originale) et 0.0126 (copie), somme 0.0315
AUC avec la copie bruitée : 0.899
```

### 5.3.2 L'importance par permutation

L'idée est d'une simplicité désarmante : **si une variable est utile, détruire son information doit dégrader le modèle**. On mesure la performance sur le jeu de test (ici l'AUC), puis on **mélange au hasard** les valeurs d'une seule variable (on casse son lien avec la cible et avec les autres variables) et l'on mesure à nouveau. La **baisse de performance** est l'importance de cette variable. On répète le mélange plusieurs fois (ici 5) pour obtenir un écart-type.

| Variable | Baisse d'AUC | Écart-type |
|---|---:|---:|
| `age` | 0,0655 | 0,0049 |
| `recence_jours` | 0,0612 | 0,0073 |
| `satisfaction_moy` | 0,0409 | 0,0029 |
| `montant_12m` | 0,0403 | 0,0047 |
| `part_achats_promo` | 0,0200 | 0,0022 |
| `programme_fidelite` | 0,0088 | 0,0034 |
| `nb_commandes_12m` | 0,0072 | 0,0013 |

Sept variables dominent ; les 40 autres (dont les 20 villes) pèsent chacune moins de 0,003. C'est cohérent avec ce qui a été programmé : l'âge (par un effet en U), la récence, la satisfaction, le montant et la part d'achats en promotion jouent un rôle central dans le départ.

La méthode a deux avantages : elle marche avec **n'importe quel modèle**, et elle mesure l'effet sur la **performance** (ce qui compte), pas sur la structure interne. Elle a aussi deux limites sérieuses.

> ⚠️ **Les variables corrélées se partagent l'importance.** Si deux variables portent la même information, mélanger l'une laisse l'autre compenser : aucune n'apparaît importante, alors que leur information l'est. Expérience : on ajoute au jeu une copie *bruitée* de `recence_jours` (corrélation de l'ordre de 0,99, écart-type du bruit de 15 jours). La récence valait seule 0,0612 d'AUC ; avec la copie, l'importance se répartit entre les deux variables (0,0189 pour l'originale et 0,0126 pour la copie, soit 0,0315 au total, la moitié de l'importance initiale), alors que l'AUC du modèle est pratiquement inchangée. Aucune des deux ne semble cruciale, et pourtant leur information l'est. **Ne concluez jamais « cette variable est inutile » d'une importance faible quand des variables voisines existent.**

> ⚠️ **L'importance n'est pas un effet.** L'importance dit « le modèle perd 0,06 d'AUC sans la récence », pas « la récence augmente (ou diminue) le risque ». Pour la *direction* de l'effet, il faut les outils suivants.

### 5.3.3 Effets moyens et individuels : PDP et ICE

Le **graphique de dépendance partielle** (PDP, *partial dependence plot*) répond à la question « *que fait le modèle quand je fais varier cette variable ?* ». On fixe la variable $x_j$ à une valeur $v$ pour **tous** les clients, on fait prédire le modèle, et l'on prend la moyenne des probabilités ; on répète pour une grille de valeurs $v$ :
$$\mathrm{PDP}_j(v)=\frac1n\sum_{i=1}^n\hat f\bigl(x_{ij}\!:=v,\ x_{i,-j}\bigr).$$
Si l'on ne moyenne pas, on obtient une courbe par client : ce sont les courbes **ICE** (*individual conditional expectation*). Le PDP est leur moyenne.

```python hide
# --- PDP et ICE à la main
def courbes(model, Z, var, grille):
    out = np.empty((len(Z), len(grille)))
    for j, g in enumerate(grille):
        Zg = Z.copy(); Zg[var] = g; out[:, j] = model.predict_proba(Zg)[:, 1]
    return out
rng = np.random.default_rng(5)
sous = Xte.iloc[rng.choice(len(Xte), 600, replace=False)]
gr = np.linspace(0, 365, 74)
ice = courbes(mg, sous, "recence_jours", gr)
bas = ((sous["satisfaction_moy"] < 3.2) & (sous["satisfaction_manquante"] == 0)).to_numpy()
print("PDP (recence_jours) à 10, 100, 150, 200, 300 jours :", [round(float(ice.mean(axis=0)[np.argmin(abs(gr - t))]), 3) for t in (10, 100, 150, 200, 300)])
print("part de clients à satisfaction < 3,2 dans l'échantillon :", round(bas.mean(), 3))
for nom, m_ in [("satisfaction < 3,2", bas), ("satisfaction >= 3,2 ou manquante", ~bas)]:
    pdp = ice[m_].mean(axis=0); print(nom, "| PDP à 100 j :", round(float(pdp[np.argmin(abs(gr - 100))]), 3), "à 200 j :", round(float(pdp[np.argmin(abs(gr - 200))]), 3))
fig, ax = plt.subplots(1, 2, figsize=(10.5, 4.2))
for i in range(40): ax[0].plot(gr, ice[i], color="#2a78d6", alpha=0.18, lw=0.9)
ax[0].plot(gr, ice.mean(axis=0), color="#eb6834", lw=2.4); ax[0].text(215, 0.27, "moyenne : PDP", color="#eb6834", fontsize=9, bbox=dict(facecolor="white", edgecolor="none", pad=1.5))
ax[0].set_xlabel("jours depuis la dernière commande"); ax[0].set_ylabel("probabilité de départ prédite"); ax[0].set_title("ICE (40 clients) et PDP")
ax[1].plot(gr, ice[bas].mean(axis=0), color="#e34948", lw=2); ax[1].plot(gr, ice[~bas].mean(axis=0), color="#2a78d6", lw=2)
ax[1].text(20, ice[bas].mean(axis=0).max() * 0.9, "satisfaction < 3,2", color="#e34948", fontsize=9); ax[1].text(20, ice[~bas].mean(axis=0).max() * 1.7, "satisfaction ≥ 3,2 ou manquante", color="#2a78d6", fontsize=9)
ax[1].set_xlabel("jours depuis la dernière commande"); ax[1].set_title("Le même effet selon la satisfaction : une interaction")
plt.tight_layout(); plt.savefig("figures/ch05-pdp-ice.png", dpi=200, bbox_inches="tight"); plt.close()
```
<!--sortie-->
```text
PDP (recence_jours) à 10, 100, 150, 200, 300 jours : [0.079, 0.087, 0.137, 0.189, 0.203]
part de clients à satisfaction < 3,2 dans l'échantillon : 0.168
satisfaction < 3,2 | PDP à 100 j : 0.135 à 200 j : 0.549
satisfaction >= 3,2 ou manquante | PDP à 100 j : 0.078 à 200 j : 0.116
```

![À gauche : courbes ICE (40 clients, en bleu) et leur moyenne, le PDP (en orange), pour la récence. À droite : le même PDP calculé séparément pour les clients peu satisfaits et les autres.](figures/ch05-pdp-ice.png)

Le PDP de la récence est presque plat jusqu'à 100 jours (probabilité moyenne de 0,079 à 10 jours et de 0,087 à 100 jours), puis monte brutalement : 0,137 à 150 jours, 0,189 à 200 jours, 0,203 à 300 jours. Une lecture sans nuance conclurait que « le risque augmente avec la récence, surtout entre 100 et 200 jours ».

Les courbes ICE disent qu'**il y a quelque chose de plus**. Elles ne sont pas parallèles : le PDP moyenne des comportements très différents. Coupons les clients en deux groupes selon leur satisfaction. Pour les clients à satisfaction inférieure à 3,2 (17 % de l'échantillon), la probabilité moyenne passe de **0,135 à 100 jours à 0,549 à 200 jours** ; pour les autres, de **0,078 à 0,116**. C'est exactement ce qui avait été programmé : la récence ne devient dangereuse que combinée à une faible satisfaction. Un effet qui dépend d'une autre variable est une **interaction** ; le PDP seul l'aurait masquée, les ICE l'ont révélée.

> ⚠️ **Limite du PDP.** Fixer la récence à 365 jours *pour tous* les clients crée des clients irréalistes (un client qui a passé dix commandes le mois dernier et dont la dernière commande date d'un an). Le PDP suppose les variables indépendantes ; quand elles ne le sont pas, il évalue le modèle là où il n'a pas de données.

### 5.3.4 LIME : un modèle simple autour d'un client

**LIME** (*Local Interpretable Model-agnostic Explanations*) explique une prédiction individuelle en la **remplaçant localement par un modèle simple**. Pour un client $x_0$ :

1. on fabrique des milliers de clients fictifs *autour* de $x_0$ (en perturbant ses variables) ;
2. on fait prédire le modèle complexe sur ces clients fictifs ;
3. on ajuste une **régression linéaire pondérée** (les clients proches de $x_0$ comptent plus) pour approcher ces prédictions ;
4. les coefficients de cette régression sont l'explication.

Autrement dit, LIME minimise $\sum_k w_k\,\bigl(\hat f(z_k)-g(z_k)\bigr)^2$ sur des points $z_k$ voisins de $x_0$, avec $g$ linéaire (et parcimonieuse).

```python hide
# --- LIME : un client, plusieurs graines
from lime.lime_tabular import LimeTabularExplainer
idx = int(np.argsort(np.abs(pm - 0.55))[0]); x0 = Xte.iloc[idx].to_numpy()
print("client expliqué : indice", idx, "| probabilité prédite", round(float(pm[idx]), 3), "| départ observé", int(yte.iloc[idx]))
tops = []
for graine in range(5):
    ex = LimeTabularExplainer(Xtr.to_numpy(), feature_names=list(Xtr.columns), mode="classification", random_state=graine, discretize_continuous=True)
    e = ex.explain_instance(x0, mg.predict_proba, num_features=5, num_samples=1500)
    tops.append([t for t, _ in e.as_list()])
    if graine < 2: print("graine", graine, ":", [(t, round(w, 3)) for t, w in e.as_list()])
def vars_(lst): return {next(v for v in Xtr.columns if v in t) for t in lst}
sets = [vars_(t) for t in tops]
jac = [len(sets[i] & sets[j]) / len(sets[i] | sets[j]) for i in range(5) for j in range(i + 1, 5)]
print("recouvrement (Jaccard) des 5 variables principales entre graines : moyenne", round(float(np.mean(jac)), 2), "min", round(min(jac), 2), "max", round(max(jac), 2))
```
<!--sortie-->
```text
client expliqué : indice 961 | probabilité prédite 0.548 | départ observé 0
graine 0 : [('recence_jours > 148.00', 0.147), ('age <= 28.00', 0.133), ('part_achats_promo > 0.34', 0.051), ('montant_12m <= 40.13', 0.048), ('programme_fidelite <= 0.00', 0.035)]
graine 1 : [('recence_jours > 148.00', 0.145), ('age <= 28.00', 0.115), ('montant_12m <= 40.13', 0.054), ('part_achats_promo > 0.34', 0.045), ('programme_fidelite <= 0.00', 0.042)]
recouvrement (Jaccard) des 5 variables principales entre graines : moyenne 0.8 min 0.67 max 1.0
```

Prenons un client du jeu de test dont la probabilité de départ est de 0,548 (il est finalement resté). Avec la graine 0, LIME répond que ce risque s'explique par : récence supérieure à 148 jours (+0,147), âge inférieur à 28 ans (+0,133), part d'achats en promotion supérieure à 0,34 (+0,051), montant annuel inférieur à 40 € (+0,048), absence de programme de fidélité (+0,035). C'est une explication lisible, en phrases.

Mais relançons LIME avec d'autres graines, sur **le même client et le même modèle**. Les poids changent (avec la graine 1, l'âge passe de +0,133 à +0,115) et les variables retenues parmi les cinq premières ne sont pas toujours les mêmes : le recouvrement moyen (indice de Jaccard) entre les ensembles de cinq variables de deux graines est de 0,80, et il descend à 0,67 pour certaines paires. **Une explication qui varie avec la graine aléatoire n'est pas une explication stable.** LIME est utile pour *se faire une idée* d'un cas, pas pour le *justifier* devant un tiers sans vérification.

### 5.3.5 Les valeurs de Shapley

On aimerait une méthode qui répartisse la prédiction entre les variables de façon **équitable et sans ambiguïté**. La théorie des jeux coopératifs en a une, inventée par Lloyd Shapley en 1953.

**Le problème du partage.** Trois joueurs coopèrent et gagnent ensemble une somme. Comment partager le gain équitablement, sachant que chaque joueur contribue différemment, et que certains ne servent qu'en présence d'autres ? Ici, les « joueurs » sont des *variables* (la récence R, la satisfaction S et le nombre de tickets de support T), et le « gain » est la *probabilité de départ* prédite pour un client. On note $v(S)$ le gain qu'obtient la coalition $S$ de variables connues. Imaginons, pour un client donné, les valeurs suivantes :

| Coalition | $\varnothing$ | R | S | T | R, S | R, T | S, T | R, S, T |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| $v$ | 0,14 | 0,30 | 0,20 | 0,15 | 0,62 | 0,34 | 0,22 | 0,66 |

($v(\varnothing)=0{,}14$ est la prévalence : le risque sans aucune information ; $v(R,S,T)=0{,}66$ est la prédiction du modèle quand on connaît tout.) La récence et la satisfaction ont un effet conjoint fort : $v(R,S)=0{,}62$, bien plus que $0{,}30+0{,}20-0{,}14=0{,}36$. Comment attribuer les $0{,}66-0{,}14=0{,}52$ de risque ?

**L'idée de Shapley.** Faisons arriver les variables **dans un ordre**, et comptons ce que chacune apporte en arrivant. Pour que l'ordre n'avantage personne, on prend la moyenne sur **tous les ordres possibles** (ici $3!=6$). Voici les apports marginaux de chaque variable :

| Ordre d'arrivée | Apport de R | Apport de S | Apport de T |
|---|---:|---:|---:|
| R, S, T | $0{,}30-0{,}14=0{,}16$ | $0{,}62-0{,}30=0{,}32$ | $0{,}66-0{,}62=0{,}04$ |
| R, T, S | $0{,}16$ | $0{,}66-0{,}34=0{,}32$ | $0{,}34-0{,}30=0{,}04$ |
| S, R, T | $0{,}62-0{,}20=0{,}42$ | $0{,}20-0{,}14=0{,}06$ | $0{,}04$ |
| S, T, R | $0{,}66-0{,}22=0{,}44$ | $0{,}06$ | $0{,}22-0{,}20=0{,}02$ |
| T, R, S | $0{,}34-0{,}15=0{,}19$ | $0{,}66-0{,}34=0{,}32$ | $0{,}15-0{,}14=0{,}01$ |
| T, S, R | $0{,}66-0{,}22=0{,}44$ | $0{,}22-0{,}15=0{,}07$ | $0{,}01$ |
| **Moyenne** | $\mathbf{1{,}81/6\approx0{,}302}$ | $\mathbf{1{,}15/6\approx0{,}192}$ | $\mathbf{0{,}16/6\approx0{,}027}$ |

La récence est responsable de 0,302 du risque, la satisfaction de 0,192 et les tickets de 0,027. Leur somme est $0{,}302+0{,}192+0{,}027=0{,}52=v(R,S,T)-v(\varnothing)$ : **le gain est exactement réparti, sans reste.**

> 📐 **Définition générale.** Pour un jeu à $p$ joueurs, la valeur de Shapley du joueur $j$ est
> $$\varphi_j=\sum_{S\subseteq N\setminus\{j\}}\frac{|S|!\,(p-|S|-1)!}{p!}\Bigl[v(S\cup\{j\})-v(S)\Bigr],$$
> la moyenne de son apport marginal sur tous les ordres d'arrivée. C'est **la seule** attribution qui vérifie quatre propriétés raisonnables : (1) **efficacité** : $\sum_j\varphi_j=v(N)-v(\varnothing)$ ; (2) **symétrie** : deux joueurs qui apportent la même chose à toutes les coalitions reçoivent la même valeur ; (3) **joueur nul** : un joueur qui n'apporte jamais rien reçoit zéro ; (4) **additivité** : si l'on additionne deux jeux, les valeurs s'additionnent.

Le calcul exact demande d'évaluer $2^p$ coalitions : impraticable pour 47 variables (plus de $10^{14}$ coalitions). C'est le rôle de SHAP.

### 5.3.6 SHAP : Shapley appliqué à un modèle

**SHAP** (*SHapley Additive exPlanations*) applique cette idée à un modèle : les « joueurs » sont les variables, et $v(S)$ est la **prédiction moyenne du modèle quand seules les variables de $S$ sont connues** (les autres étant intégrées sur leur distribution). On obtient, pour **chaque client et chaque variable**, une valeur $\varphi_{ij}$, avec la propriété d'efficacité :
$$\hat f(x_i)=\varphi_0+\sum_{j=1}^p\varphi_{ij},$$
où $\varphi_0$ est la **valeur de base** (la prédiction moyenne du modèle). Pour un classifieur à arbres, la prédiction est exprimée en *log-cote* ; une valeur positive augmente le risque, une valeur négative le diminue.

L'ingénieux **TreeSHAP** calcule ces valeurs **exactement** pour des arbres, en un temps polynomial, au lieu des $2^p$ coalitions. En pratique, deux lignes suffisent :

```python
import shap

explicateur = shap.TreeExplainer(mg)                 # mg : le modèle LightGBM entraîné plus haut
valeurs = explicateur.shap_values(Xte.iloc[:500])    # une valeur de Shapley par client et par variable
print(np.shape(valeurs), "| valeur de base (log-cote) :", round(float(np.ravel(explicateur.expected_value)[-1]), 3))
```
<!--sortie-->
```text
(500, 47) | valeur de base (log-cote) : -2.993
```

```python hide
# --- valeurs de Shapley : exemple à la main (3 variables) vérifié par énumération
v = {(): 0.14, ("R",): 0.30, ("S",): 0.20, ("T",): 0.15, ("R", "S"): 0.62, ("R", "T"): 0.34, ("S", "T"): 0.22, ("R", "S", "T"): 0.66}
def val(S): return v[tuple(sorted(S, key="RST".index))]
joueurs = ["R", "S", "T"]; phi = {j: 0.0 for j in joueurs}
for ordre in itertools.permutations(joueurs):
    pris = []
    for j in ordre:
        phi[j] += (val(pris + [j]) - val(pris)) / 6; pris.append(j)
print("Shapley :", {k: round(x, 4) for k, x in phi.items()}, "| somme", round(sum(phi.values()), 4), "| v(RST) - v(vide) =", round(v[("R", "S", "T")] - v[()], 4))
# --- SHAP exact pour LightGBM (TreeSHAP) sur 500 clients
expl = shap.TreeExplainer(mg)
Zs = Xte.iloc[:500]
sv = expl.shap_values(Zs); sv = sv[1] if isinstance(sv, list) else sv
base = float(np.ravel(expl.expected_value)[-1])
marge = mg.predict(Zs, raw_score=True)
print("efficacité : max |base + somme SHAP - sortie brute| =", float(np.abs(base + sv.sum(axis=1) - marge).max()))
msv = pd.Series(np.abs(sv).mean(axis=0), index=Zs.columns).sort_values(ascending=False)
print(msv.head(10).round(4).to_string())
rang_perm = {v_: i + 1 for i, v_ in enumerate(imp["variable"])}
print("rangs SHAP vs permutation (10 premières variables SHAP) :", [(v_, i + 1, rang_perm[v_]) for i, v_ in enumerate(msv.index[:10])])
```
<!--sortie-->
```text
Shapley : {'R': 0.3017, 'S': 0.1917, 'T': 0.0267} | somme 0.52 | v(RST) - v(vide) = 0.52
efficacité : max |base + somme SHAP - sortie brute| = 9.769962616701378e-15
age                           0.6834
montant_12m                   0.6476
recence_jours                 0.5583
part_achats_promo             0.2780
satisfaction_moy              0.2666
nb_commandes_12m              0.2179
programme_fidelite            0.2036
taux_ouverture_email          0.1394
canal_acquisition_Boutique    0.0810
panier_moyen                  0.0711
rangs SHAP vs permutation (10 premières variables SHAP) : [('age', 1, 1), ('montant_12m', 2, 4), ('recence_jours', 3, 2), ('part_achats_promo', 4, 5), ('satisfaction_moy', 5, 3), ('nb_commandes_12m', 6, 7), ('programme_fidelite', 7, 6), ('taux_ouverture_email', 8, 47), ('canal_acquisition_Boutique', 9, 9), ('panier_moyen', 10, 45)]
```

On obtient une matrice de 500 clients par 47 variables, et la valeur de base vaut $-2{,}993$ en log-cote, soit une probabilité de $0{,}048$. (Elle est très inférieure à la prévalence de 14 % : la valeur de base est la *moyenne des log-cotes*, et non la log-cote de la moyenne. Quelques clients très risqués tirent la moyenne des probabilités vers le haut sans déplacer beaucoup celle des log-cotes.) Vérifions l'efficacité : pour chaque client, la valeur de base plus la somme de ses 47 valeurs SHAP doit redonner exactement la sortie brute du modèle. L'écart maximal sur les 500 clients est de $10^{-14}$ : c'est de l'arrondi informatique. Rien n'est « approximatif » : l'explication est une **décomposition exacte** de la prédiction.

**Lecture globale.** La moyenne des valeurs absolues de SHAP par variable donne une importance globale, cette fois dans l'unité du modèle (la log-cote). En tête : l'âge (0,683), le montant annuel (0,648), la récence (0,558), la part d'achats en promotion (0,278), la satisfaction (0,267), le nombre de commandes (0,218) et le programme de fidélité (0,204). Le classement est proche de celui de la permutation, mais pas identique :

| Variable | Rang SHAP | Rang permutation |
|---|---:|---:|
| `age` | 1 | 1 |
| `montant_12m` | 2 | 4 |
| `recence_jours` | 3 | 2 |
| `part_achats_promo` | 4 | 5 |
| `satisfaction_moy` | 5 | 3 |
| `nb_commandes_12m` | 6 | 7 |
| `programme_fidelite` | 7 | 6 |
| `taux_ouverture_email` | 8 | 47 |
| `panier_moyen` | 10 | 45 |

L'écart le plus net concerne `taux_ouverture_email` (8ᵉ en SHAP, 47ᵉ en permutation) : cette variable a un effet **réel mais faible** sur chaque client, que SHAP restitue, mais qui ne se traduit que par une dégradation négligeable de l'AUC quand on la mélange. Ce sont deux questions différentes : SHAP répond à « *combien cette variable déplace-t-elle les prédictions ?* », la permutation à « *combien le modèle perd-il à l'ignorer ?* ».

![Résumé SHAP : un point par client (500 clients) et par variable ; position horizontale = effet sur la log-cote ; couleur = valeur de la variable (rouge : élevée).](figures/ch05-shap-resume.png)

![Dépendance de la valeur SHAP de la récence à la récence elle-même, colorée par la satisfaction.](figures/ch05-shap-dependance.png)

**Comment lire le résumé.** Chaque ligne est une variable, chaque point un client ; la position horizontale est l'effet du client sur la log-cote du départ (à droite : le risque augmente) et la couleur est la valeur de la variable pour ce client (rouge : élevée). On y retrouve ce qui a été programmé. La **récence** : les points rouges (longue absence) sont à droite, jusqu'à $+1{,}9$ ; les points bleus (achat récent) à gauche. La **satisfaction** : les clients peu satisfaits (points bleus) poussent le risque de $+0{,}3$ à $+1{,}5$, les clients satisfaits le diminuent légèrement. Le **montant annuel** : un montant élevé protège (jusqu'à $-1{,}1$), un montant nul ou faible expose. Le **programme de fidélité** : les membres (rouge) sont du côté protecteur. Enfin l'**âge** montre l'effet **en U** : les clients les plus jeunes (points bleus) ont des contributions fortement positives, qui atteignent $+2{,}2$, la zone centrale est négative, et quelques clients plus âgés (points rouges, à droite) retrouvent des contributions positives. Une courbe moyenne, ou une seule importance, n'aurait pas montré cette forme.

**Comment lire la dépendance.** Pour la récence, la contribution passe d'environ $-1$ (achat très récent) à $0$ vers 100 jours, puis grimpe nettement après 150 jours. Au-delà de 150 jours, les points se séparent verticalement selon leur couleur : les clients **peu satisfaits** (bleus) atteignent $+1{,}3$ à $+1{,}9$, les clients **satisfaits** (rouges ou violets) restent entre $+0{,}8$ et $+1{,}2$. C'est l'interaction repérée en 5.3.3, cette fois mesurée sur chaque client. L'empilement vertical à 365 jours correspond aux clients qui n'ont passé aucune commande dans l'année.

**Lecture locale.** Prenons, parmi les 500, le client le plus à risque. Sa sortie brute est de $2{,}398$ en log-cote (probabilité $0{,}917$), contre $-2{,}993$ pour la valeur de base (probabilité $0{,}048$). La différence, $5{,}39$, est répartie entre les variables : **récence** (365 jours, c'est-à-dire aucune commande depuis un an) $+1{,}78$, **satisfaction** (2,4) $+1{,}21$, **âge** (24 ans) $+0{,}77$, **montant annuel** (0 €) $+0{,}76$, **nombre de commandes** (0) $+0{,}28$, **ancienneté** (38 mois) $+0{,}22$, et d'autres plus petites. Chaque contribution est lisible par un non-spécialiste : « ce client est signalé parce qu'il n'a rien acheté depuis un an, qu'il est peu satisfait et qu'il est jeune ».

![Décomposition de la prédiction du client le plus à risque parmi les 500 : de la valeur de base aux 8 plus grandes contributions.](figures/ch05-shap-cas.png)

### 5.3.7 Les pièges de l'interprétation

**SHAP n'est pas de la causalité.** Les valeurs SHAP décrivent comment le *modèle* utilise les variables. Elles ne disent pas ce qui arriverait si l'on *intervenait* sur la variable. Que la satisfaction ait une forte contribution ne dit pas qu'augmenter la satisfaction fera baisser le départ ; cela relève de l'inférence causale (volume II, chapitre 7, facultatif).

**Les variables corrélées brouillent la lecture.** Comme en 5.3.2, quand deux variables portent la même information, SHAP la partage entre elles de façon dépendante du modèle. Lire « la variable A pèse deux fois plus que B » n'a de sens que si A et B sont à peu près indépendantes.

**Une explication peut être fausse sans que le modèle le soit.** Les explications dépendent d'hypothèses (la distribution de fond utilisée pour « supprimer » les variables, le nombre de perturbations de LIME…). Deux outils peuvent donner deux récits différents pour la même prédiction ; il faut le savoir.

**Mais l'interprétabilité sert aussi à débusquer les erreurs.** Rappelez-vous le piège du chapitre 1 : la colonne `commandes_apres_cible`, qui contient les commandes des trois mois *suivants*, donc l'avenir. Entraînons le même modèle en la laissant parmi les variables. L'AUC sur le jeu de test monte de 0,902 à **0,933**, ce qui est tentant. Mais SHAP trahit immédiatement le modèle : la première variable est `commandes_apres_cible` (importance moyenne 1,394), bien devant l'âge (0,531) et le montant annuel (0,452). Un modèle de prévision dont la variable la plus importante est une information du futur est un modèle qui triche. **Regardez toujours les variables que votre modèle juge les plus importantes : si l'une est suspecte, vous avez probablement une fuite d'information.**

> ✅ **À retenir.**
> - Distinguez l'explication **globale** et **locale**, et ce que l'on explique : le **modèle**, pas le monde.
> - L'**importance par permutation** mesure la perte de performance sans une variable ; elle est trompée par les variables corrélées.
> - **PDP** et **ICE** montrent *comment* une variable agit ; les ICE révèlent les interactions que le PDP moyenne.
> - **LIME** ajuste un modèle linéaire local : lisible, mais **instable** (varie avec la graine).
> - Les **valeurs de Shapley** répartissent la prédiction de façon unique (efficacité, symétrie, joueur nul, additivité) ; **TreeSHAP** les calcule exactement pour les arbres. Leur somme redonne la prédiction.
> - Utilisez l'interprétabilité comme **outil de diagnostic** : elle débusque les fuites d'information.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.6 et 5.7, exercices 5.9 et 5.10.

```python hide
plt.figure(figsize=(8, 5)); shap.summary_plot(sv, Zs, max_display=10, show=False, plot_size=None)
plt.gca().set_xlabel("valeur SHAP (effet sur la log-cote du départ)"); cb = plt.gcf().axes[-1]; cb.set_ylabel("valeur de la variable"); cb.set_yticklabels(["faible", "élevée"])
plt.tight_layout(); plt.savefig("figures/ch05-shap-resume.png", dpi=200, bbox_inches="tight"); plt.close()
plt.figure(figsize=(7, 4.6)); shap.dependence_plot("recence_jours", sv, Zs, interaction_index="satisfaction_moy", show=False)
plt.gca().set_ylabel("valeur SHAP de recence_jours"); plt.gca().set_xlabel("jours depuis la dernière commande")
plt.tight_layout(); plt.savefig("figures/ch05-shap-dependance.png", dpi=200, bbox_inches="tight"); plt.close()
i0 = int(np.argmax(sv.sum(axis=1)))
top7 = np.argsort(-np.abs(sv[i0]))[:7]
etiq = [f"{Zs.iloc[i0, j]:g} = {Zs.columns[j]}" for j in top7] + [f"{len(Zs.columns) - 7} autres variables"]
vals = [float(sv[i0, j]) for j in top7]; vals.append(float(sv[i0].sum() - sum(vals)))
fig, ax = plt.subplots(figsize=(8.2, 4.6)); debut = base
for k, v in enumerate(vals):
    ax.barh(k, v, left=debut, color="#e34948" if v > 0 else "#2a78d6", height=0.65)
    ax.text(max(debut, debut + v) + 0.06, k, f"{v:+.2f}", va="center", fontsize=9, color="#52514e"); debut += v
ax.set_yticks(range(len(vals))); ax.set_yticklabels(etiq); ax.invert_yaxis(); ax.set_xlim(base - 0.4, debut + 0.9)
ax.axvline(base, color="#898781", ls=":", lw=1); ax.axvline(debut, color="#898781", ls="--", lw=1)
ax.text(base, len(vals) - 0.35, f"valeur de base {base:.2f}", ha="center", fontsize=9, color="#898781"); ax.text(debut, -0.75, f"sortie du modèle {debut:.2f}", ha="center", fontsize=9, color="#898781")
ax.set_xlabel("log-cote du départ : de la valeur de base à la sortie du modèle"); ax.grid(axis="y", visible=False)
plt.tight_layout(); plt.savefig("figures/ch05-shap-cas.png", dpi=200, bbox_inches="tight"); plt.close()
print("client le plus à risque (indice", i0, ") : sortie brute", round(float(marge[i0]), 3), "= probabilité", round(float(1 / (1 + np.exp(-marge[i0]))), 3), "| base", round(base, 3), "-> probabilité de base", round(float(1 / (1 + np.exp(-base))), 3))
print([ (Zs.columns[j], round(float(sv[i0, j]), 3), float(Zs.iloc[i0, j])) for j in np.argsort(-np.abs(sv[i0]))[:6]])
# --- la fuite d'information saute aux yeux dans SHAP
Xf = X.copy(); Xf["commandes_apres_cible"] = c["commandes_apres_cible"]
Xf = Xf.loc[Xtr.index.union(Xte.index)].fillna(med)
mf = lgb.LGBMClassifier(n_estimators=150, learning_rate=0.05, num_leaves=15, min_child_samples=40, random_state=0, verbose=-1, n_jobs=1).fit(Xf.loc[Xtr.index], ytr)
svf = shap.TreeExplainer(mf).shap_values(Xf.loc[Xte.index].iloc[:500]); svf = svf[1] if isinstance(svf, list) else svf
mf_ = pd.Series(np.abs(svf).mean(axis=0), index=Xf.columns).sort_values(ascending=False)
print("avec la colonne de fuite : AUC", round(M.roc_auc_score(yte, mf.predict_proba(Xf.loc[Xte.index])[:, 1]), 4), "| 3 premières variables SHAP :", [(k, round(float(x), 3)) for k, x in mf_.head(3).items()])
```
<!--sortie-->
```text
client le plus à risque (indice 1 ) : sortie brute 2.398 = probabilité 0.917 | base -2.993 -> probabilité de base 0.048
[('recence_jours', 1.779, 365.0), ('satisfaction_moy', 1.207, 2.4), ('age', 0.771, 24.0), ('montant_12m', 0.756, 0.0), ('nb_commandes_12m', 0.283, 0.0), ('anciennete_mois', 0.216, 38.0)]
avec la colonne de fuite : AUC 0.9325 | 3 premières variables SHAP : [('commandes_apres_cible', 1.394), ('age', 0.531), ('montant_12m', 0.452)]
```
