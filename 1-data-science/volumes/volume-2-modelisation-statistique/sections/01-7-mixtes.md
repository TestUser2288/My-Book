## 1.7 ➕ Pour aller plus loin : les modèles à effets mixtes et hiérarchiques

> 🧭 **Section optionnelle.** Elle s'adresse à qui travaille sur des données **groupées** (clients dans des villes, élèves dans des classes, mesures répétées sur les mêmes personnes). Elle prépare les modèles hiérarchiques bayésiens du chapitre 6.

> 💡 **Intuition.** La régression ordinaire suppose que les observations sont **indépendantes** (hypothèse H4 du 1.1.2). Mais les 20 commandes retirées dans le **même point relais** se ressemblent : elles partagent la même équipe, le même emplacement, la même ambiance. Les traiter comme 20 observations indépendantes revient à compter vingt fois une information qui n'existe qu'une fois : on se croit plus sûr de soi qu'on ne l'est. Le **modèle mixte** reconnaît explicitement que chaque groupe a sa propre « personnalité » (un niveau de base propre) et la modélise comme un **effet aléatoire**, tiré d'une loi commune. Chaque groupe est ainsi à la fois **différent** des autres et **lié** à eux.

### 1.7.1 Un jeu de données groupé : les points relais

Dar Jasmin livre en partie via **30 points relais** (commerces partenaires où les clients viennent retirer leur colis). Pour chaque commande retirée, on dispose du **délai de livraison** (de 1 à 10 jours) et de la **note de satisfaction** (sur 20). Les relais sont de tailles très inégales (certains ont reçu 4 commandes, d'autres près de 60), et certains sont en zone **urbaine**. Les données sont simulées (graine fixe) selon un modèle que nous connaîtrons, comme d'habitude :

$$\text{note}_{ij}=12+1{,}2\,\text{urbain}_j+u_{0j}+(-0{,}7+u_{1j})(\text{délai}_{ij}-5)+\varepsilon_{ij},$$

où $i$ numérote les commandes du relais $j$, $u_{0j}\sim\mathcal N(0,1{,}6^2)$ est le **niveau de base propre au relais** (« certains relais notent plus généreusement »), $u_{1j}\sim\mathcal N(0,0{,}3^2)$ la **sensibilité propre au retard** de ce relais, et $\varepsilon_{ij}\sim\mathcal N(0,1{,}8^2)$ le bruit.

```python
import warnings
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, VIOLET, ENCRE, GRIS, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#0b0b0b", "#898781", "#e34948"
STYLE = {"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#e1e0d9",
         "grid.linewidth": 0.6, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
         "savefig.facecolor": "#fcfcfb", "font.size": 10, "axes.edgecolor": "#c3c2b7"}
plt.rcParams.update(STYLE)

# Simulation des 30 points relais (graine fixe)
rng = np.random.default_rng(41)
J = 30
tailles = np.clip(np.round(rng.lognormal(np.log(12), 0.8, J)), 3, 60).astype(int)    # commandes par relais (très inégal)
urbain = (rng.random(J) < 0.5).astype(int)
u0 = rng.normal(0, 1.6, J)                                                           # vrai niveau de base de chaque relais
u1 = rng.normal(0, 0.3, J)                                                           # vraie sensibilité au retard de chaque relais
lignes = []
for j in range(J):
    delai = rng.integers(1, 11, tailles[j])
    note = 12 + 1.2 * urbain[j] + u0[j] + (-0.7 + u1[j]) * (delai - 5) + rng.normal(0, 1.8, tailles[j])
    for d, y in zip(delai, note):
        lignes.append((f"R{j + 1:02d}", urbain[j], int(d), round(float(y), 2)))
rel = pd.DataFrame(lignes, columns=["relais", "urbain", "delai", "note"])
rel.to_csv("donnees/ch01-relais.csv", index=False)         # fichier fourni avec le livre (lu aussi par R plus bas)
rel["dc"] = rel["delai"] - 5                                # délai centré : 0 = délai de 5 jours
print(rel.shape, "| relais :", rel["relais"].nunique(), "| relais urbains :", int(urbain.sum()))
print("commandes par relais : min =", tailles.min(), "| médiane =", int(np.median(tailles)), "| max =", tailles.max())
print("écart-type RÉALISÉ des 30 vrais niveaux de base u0 :", round(u0.std(ddof=1), 2), "(la loi dont ils sont tirés a un écart-type de 1,6)")
print(rel.head(5).to_string(index=False))
```
<!--sortie-->
```text
(484, 5) | relais : 30 | relais urbains : 14
commandes par relais : min = 4 | médiane = 11 | max = 58
écart-type RÉALISÉ des 30 vrais niveaux de base u0 : 1.31 (la loi dont ils sont tirés a un écart-type de 1,6)
relais  urbain  delai  note  dc
   R01       0      6 12.57   1
   R01       0      4 11.23  -1
   R01       0      8  4.98   3
   R01       0     10  7.56   5
   R02       1      6  9.91   1
```

Notons déjà un fait important. Les 30 niveaux de base $u_{0j}$ ont été **tirés** d'une loi d'écart-type 1,6, mais avec seulement 30 relais, leur écart-type **réalisé** n'est que de 1,31. Avec peu de groupes, les composantes de variance sont **mal connues** : nous y reviendrons.

### 1.7.2 Trois façons de traiter les groupes

Pour estimer le niveau de base de chaque relais, trois stratégies s'offrent à nous :

1. **Mise en commun totale** (*complete pooling*) : on ignore les groupes (régression ordinaire sur les 484 commandes). On suppose que tous les relais sont identiques.
2. **Pas de mise en commun** (*no pooling*) : on estime chaque relais **séparément** (une indicatrice par relais). On suppose qu'ils n'ont rien en commun.
3. **Mise en commun partielle** (*partial pooling*) : le **modèle mixte**. Chaque relais a son propre niveau, mais ces niveaux sont supposés tirés d'une même loi : l'information d'un relais **aide** à estimer les autres.

Commençons par les deux premières, et regardons les conséquences sur les erreurs standard :

```python
m_commun = smf.ols("note ~ dc + urbain", data=rel).fit()                           # ignore les groupes
m_separe = smf.ols("note ~ dc + C(relais)", data=rel).fit()                         # une indicatrice par relais (urbain y est absorbé)
print("Mise en commun totale (MCO, groupes ignorés) :")
print(pd.DataFrame({"coef": m_commun.params, "erreur standard": m_commun.bse, "IC bas": m_commun.conf_int()[0], "IC haut": m_commun.conf_int()[1]}).round(3).to_string())
print(f"\nrésidu : s = {np.sqrt(m_commun.scale):.2f}")
print("\nPas de mise en commun : l'effet « urbain » n'est plus estimable (il est confondu avec les indicatrices de relais).")
print(f"coefficient du délai avec indicatrices de relais : {m_separe.params['dc']:.3f} (erreur standard {m_separe.bse['dc']:.3f})")
```
<!--sortie-->
```text
Mise en commun totale (MCO, groupes ignorés) :
             coef  erreur standard  IC bas  IC haut
Intercept  12.644            0.152  12.345   12.943
dc         -0.721            0.039  -0.796   -0.645
urbain      0.482            0.224   0.043    0.922

résidu : s = 2.44

Pas de mise en commun : l'effet « urbain » n'est plus estimable (il est confondu avec les indicatrices de relais).
coefficient du délai avec indicatrices de relais : -0.703 (erreur standard 0.034)
```

> ⚠️ **Le problème de la mise en commun totale.** Les p-valeurs et intervalles de ce premier modèle supposent 484 observations **indépendantes**. Or elles sont groupées en 30 relais. Pour une variable qui ne varie **qu'entre** relais (comme `urbain`), l'information ne vient que de 30 unités, pas de 484 : la mise en commun totale **sous-estime fortement** son incertitude. Nous le démontrons par simulation plus bas (1.7.6).

Le **pas de mise en commun** a l'inconvénient inverse : il ne peut pas estimer l'effet d'une variable de niveau groupe (`urbain`), et il estime très mal le niveau d'un petit relais (4 commandes) : l'estimation est trop bruitée.

### 1.7.3 Le modèle à intercept aléatoire

Le **modèle mixte à intercept aléatoire** s'écrit

$$y_{ij}=\mathbf x_{ij}^\top\boldsymbol\beta+u_{j}+\varepsilon_{ij},\qquad u_j\sim\mathcal N(0,\tau^2),\quad\varepsilon_{ij}\sim\mathcal N(0,\sigma^2),$$

les $u_j$ et les $\varepsilon_{ij}$ étant indépendants. Les $\boldsymbol\beta$ sont les **effets fixes** (communs à tous), les $u_j$ des **effets aléatoires**. Deux paramètres de variance : $\tau^2$ (variance **entre** relais) et $\sigma^2$ (variance **à l'intérieur** d'un relais).

> 📐 **Ce que cela implique pour les observations.** Pour deux commandes $i\ne i'$ du **même** relais, $\operatorname{Cov}(y_{ij},y_{i'j})=\operatorname{Var}(u_j)=\tau^2$ : elles sont **corrélées**, avec une corrélation
> $$\rho=\frac{\tau^2}{\tau^2+\sigma^2}\qquad\text{(coefficient de corrélation intraclasse, ICC).}$$
> Pour deux commandes de relais différents, la covariance est nulle. Le vecteur des commandes d'un relais de $n_j$ commandes a donc pour matrice de variance $\mathbf V_j=\sigma^2\mathbf I+\tau^2\mathbf 1\mathbf 1^\top$ (« symétrie composée »). Par conséquent, la **variance de la moyenne** de $n_j$ commandes est $\tau^2+\sigma^2/n_j$, et non $\sigma^2/n_j$ : *il y a un plancher*, $\tau^2$, que l'on ne peut jamais dépasser en ajoutant des commandes dans un même relais. L'**effectif effectif** d'un échantillon de $m$ commandes par groupe est $m/(1+(m-1)\rho)$ (« effet de plan »).

**L'ICC répond à la question « les groupes comptent-ils ? ».** Comparons deux situations. D'abord un cas où la réponse est **non** : les clients de Dar Jasmin sont répartis en six **villes**. Le panier dépend-il de la ville, au-delà de l'âge et du canal ?

```python
clients = pd.read_csv("donnees/clients.csv")
cl = clients[clients["nb_commandes_an"] > 0].copy().reset_index(drop=True)
cl["canal"] = pd.Categorical(cl["canal_acquisition"], categories=["Boutique", "Site", "Instagram"])
cl["a"] = cl["age"] - 36
cl["log_panier"] = np.log(cl["panier_moyen"])
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    m_ville = smf.mixedlm("log_panier ~ a + C(canal)", cl, groups=cl["ville"]).fit(reml=True)
tau2_v, sigma2_v = m_ville.cov_re.iloc[0, 0], m_ville.scale
print(f"clients groupés par ville : variance entre villes tau² = {tau2_v:.5f} | variance résiduelle sigma² = {sigma2_v:.4f}")
print(f"ICC = tau²/(tau² + sigma²) = {tau2_v / (tau2_v + sigma2_v):.4f}")
```
<!--sortie-->
```text
clients groupés par ville : variance entre villes tau² = 0.00000 | variance résiduelle sigma² = 0.1373
ICC = tau²/(tau² + sigma²) = 0.0000
```

L'ICC est estimé à **0** (la variance entre villes est estimée au bord de l'espace des paramètres : exactement 0) : une fois l'âge et le canal pris en compte, la ville n'explique rien du panier. Le modèle mixte aurait ici été superflu, et nos analyses des sections précédentes (sans effet de ville) étaient légitimes. Retenons que **regrouper n'implique pas toujours une dépendance** : le modèle mixte est un outil à utiliser quand l'ICC est notable.

Pour les points relais, la situation est tout autre :

```python
m_ri = smf.mixedlm("note ~ dc + urbain", rel, groups=rel["relais"]).fit(reml=True)
tau2, sigma2 = m_ri.cov_re.iloc[0, 0], m_ri.scale
print(m_ri.summary().tables[1])
print(f"\nvariance entre relais tau² = {tau2:.3f} (écart-type {np.sqrt(tau2):.2f}) | variance résiduelle sigma² = {sigma2:.3f} (écart-type {np.sqrt(sigma2):.2f})")
print(f"ICC = {tau2 / (tau2 + sigma2):.3f} : environ {100 * tau2 / (tau2 + sigma2):.0f} % de la variance des notes (après effet du délai et du type de relais) est due au relais")
```
<!--sortie-->
```text
            Coef. Std.Err.        z  P>|z|  [0.025  0.975]
Intercept  12.489    0.364   34.284  0.000  11.775  13.202
dc         -0.710    0.034  -21.047  0.000  -0.776  -0.644
urbain      0.377    0.534    0.705  0.481  -0.671   1.424
Group Var   1.711    0.280                                

variance entre relais tau² = 1.711 (écart-type 1.31) | variance résiduelle sigma² = 4.350 (écart-type 2.09)
ICC = 0.282 : environ 28 % de la variance des notes (après effet du délai et du type de relais) est due au relais
```

Plus du quart (28 %) de la variance résiduelle des notes est **entre relais** : deux commandes du même relais sont corrélées (corrélation ≈ 0,28). Avec 16 commandes par relais en moyenne, l'**effet de plan** est considérable : $1+(m-1)\rho\approx1+15\times0{,}28\approx5{,}2$ : pour une variable qui ne varie qu'entre relais, les 484 commandes **valent environ 484/5 ≈ 93 observations indépendantes**. Remarquez le résultat sur `urbain` : sa erreur standard est de 0,534 avec le modèle mixte, contre 0,224 pour la régression ordinaire du 1.7.2, soit **2,4 fois plus**. L'intervalle de confiance ordinaire (de 0,04 à 0,92) **exclut** zéro et laisse croire à un effet « significatif » ; l'intervalle mixte (de −0,67 à 1,42) **ne l'exclut pas**. C'est l'effet de plan en action : les 484 commandes n'apportent, sur le type de relais, que l'information de 30 relais.

**Comment estime-t-on ce modèle ? La méthode REML.** La variance de $\hat{\boldsymbol\beta}$ dépend de $\mathbf V=\operatorname{diag}(\mathbf V_j)$, qui dépend de $\tau^2$ et $\sigma^2$, inconnus. Étant donné $\mathbf V$, l'estimateur des effets fixes est celui des **moindres carrés généralisés** (qui pondère selon la fiabilité de chaque observation)

$$\hat{\boldsymbol\beta}=\big(\mathbf X^\top\mathbf V^{-1}\mathbf X\big)^{-1}\mathbf X^\top\mathbf V^{-1}\mathbf y .$$

Les paramètres de variance sont estimés par maximum de vraisemblance, mais la version « classique » **sous-estime** les variances (comme la division par $n$ au lieu de $n-p$, 1.1.5) : on lui préfère la **vraisemblance restreinte (REML)**, qui maximise la vraisemblance des **résidus** (les combinaisons des données indépendantes des effets fixes) et corrige ce biais. `statsmodels` (`reml=True`, par défaut) et R (`lme4`) utilisent la REML.

### 1.7.4 La mise en commun partielle : le rétrécissement

Le grand intérêt du modèle mixte est ce qu'il fait des **niveaux des groupes**. Une fois les effets fixes estimés, on prédit l'effet aléatoire $u_j$ de chaque relais par le **meilleur prédicteur linéaire sans biais (BLUP)**.

> 📐 **Le BLUP est une moyenne rétrécie.** Soit $\bar r_j$ la moyenne, pour le relais $j$, des résidus « fixes » $r_{ij}=y_{ij}-\mathbf x_{ij}^\top\hat{\boldsymbol\beta}$ (c'est l'estimation « sans mise en commun » du niveau de base du relais). Le BLUP est
> $$\hat u_j=\underbrace{\frac{\tau^2}{\tau^2+\sigma^2/n_j}}_{B_j\in(0,1)}\ \bar r_j .$$
> *Démonstration.* Pour un groupe de $n_j$ observations, $\mathbf V_j=\sigma^2\mathbf I+\tau^2\mathbf 1\mathbf 1^\top$ vérifie $\mathbf V_j\mathbf 1=(\sigma^2+n_j\tau^2)\mathbf 1$, donc $\mathbf V_j^{-1}\mathbf 1=\mathbf 1/(\sigma^2+n_j\tau^2)$. Le BLUP est $\hat u_j=\tau^2\,\mathbf 1^\top\mathbf V_j^{-1}\mathbf r_j=\tau^2\,\dfrac{n_j\bar r_j}{\sigma^2+n_j\tau^2}=\dfrac{\tau^2}{\tau^2+\sigma^2/n_j}\,\bar r_j$. $\square$
>
> Le facteur $B_j$ est la **fiabilité** de la moyenne du groupe. Pour un **grand** groupe ($n_j\to\infty$), $B_j\to1$ : on fait confiance à sa moyenne. Pour un **petit** groupe, $B_j$ est petit : sa moyenne est bruitée, on la **rapproche de la moyenne générale** (0). C'est un compromis entre « ce relais est unique » ($B_j=1$, pas de mise en commun) et « tous les relais sont pareils » ($B_j=0$, mise en commun totale).

Vérifions la formule, puis comparons les deux estimations à la **vérité**, que nous connaissons ici (les vrais $u_{0j}$) :

```python
beta_ri = m_ri.fe_params
rel["r"] = rel["note"] - (beta_ri["Intercept"] + beta_ri["dc"] * rel["dc"] + beta_ri["urbain"] * rel["urbain"])      # résidus « fixes »
groupes = rel.groupby("relais")["r"].agg(["mean", "size"]).rename(columns={"mean": "r_bar", "size": "n_j"})
groupes["B"] = tau2 / (tau2 + sigma2 / groupes["n_j"])
groupes["u_formule"] = groupes["B"] * groupes["r_bar"]
groupes["u_statsmodels"] = [m_ri.random_effects[g]["Group"] for g in groupes.index]
groupes["u_vrai"] = u0
print("formule du BLUP = statsmodels :", np.allclose(groupes["u_formule"], groupes["u_statsmodels"]))
print(groupes.sort_values("n_j").iloc[[0, 1, 2, 14, 27, 28, 29]].round(3).to_string())
erreur_sans = np.sqrt(np.mean((groupes["r_bar"] - groupes["u_vrai"])**2))
erreur_part = np.sqrt(np.mean((groupes["u_statsmodels"] - groupes["u_vrai"])**2))
print(f"\nerreur quadratique moyenne par rapport aux vrais niveaux u0 :  sans mise en commun = {erreur_sans:.3f} | mise en commun partielle = {erreur_part:.3f}")
petits = groupes["n_j"] <= 8
print(f"  pour les {petits.sum()} petits relais (8 commandes ou moins) :   sans = {np.sqrt(np.mean((groupes.loc[petits, 'r_bar'] - groupes.loc[petits, 'u_vrai'])**2)):.3f} | partielle = {np.sqrt(np.mean((groupes.loc[petits, 'u_statsmodels'] - groupes.loc[petits, 'u_vrai'])**2)):.3f}")
```
<!--sortie-->
```text
formule du BLUP = statsmodels : True
        r_bar  n_j      B  u_formule  u_statsmodels  u_vrai
relais                                                     
R01    -1.983    4  0.611     -1.213         -1.213  -0.937
R05     0.997    4  0.611      0.610          0.610  -0.683
R10    -2.442    4  0.611     -1.493         -1.493   0.413
R19    -0.426   11  0.812     -0.346         -0.346   0.624
R12    -0.644   31  0.924     -0.595         -0.595  -0.548
R16     1.386   56  0.957      1.326          1.326   1.867
R29     1.257   58  0.958      1.204          1.204   0.725

erreur quadratique moyenne par rapport aux vrais niveaux u0 :  sans mise en commun = 0.900 | mise en commun partielle = 0.765
  pour les 10 petits relais (8 commandes ou moins) :   sans = 1.273 | partielle = 1.031
```

La formule reproduit exactement les prédictions de `statsmodels`. Surtout, l'erreur par rapport aux **vrais** niveaux est plus faible avec la mise en commun partielle, et le gain est **le plus net pour les petits relais**, dont l'estimation individuelle était la plus bruitée. Voyons le mécanisme sur un graphique : pour chaque relais (classés par taille), on relie son estimation « sans mise en commun » à son estimation rétrécie.

```python
ordre = groupes.sort_values("n_j").reset_index()
fig, ax = plt.subplots(figsize=(8.8, 4.8))
x = np.arange(len(ordre))
for i, ligne in ordre.iterrows():
    ax.plot([i, i], [ligne["r_bar"], ligne["u_statsmodels"]], color=GRIS, lw=1.2, zorder=1)
ax.scatter(x, ordre["r_bar"], facecolors="none", edgecolors=ORANGE, s=45, lw=1.6, zorder=3, label="sans mise en commun (moyenne du relais)")
ax.scatter(x, ordre["u_statsmodels"], color=BLEU, s=32, zorder=4, label="mise en commun partielle (BLUP)")
ax.scatter(x, ordre["u_vrai"], marker="_", color=ENCRE, s=130, lw=2, zorder=5, label="vérité (connue car simulée)")
ax.axhline(0, color=GRIS, lw=1)
ax.set_xticks(x); ax.set_xticklabels(ordre["n_j"], fontsize=7.5)
ax.set_xlabel("nombre de commandes du relais (relais classés du plus petit au plus grand)")
ax.set_ylabel("niveau de base du relais (écart à la moyenne, en points)")
ax.set_ylim(-3.3, 3.8)                                    # marge en haut pour la légende
ax.legend(frameon=False, loc="upper left", fontsize=8.5)
plt.savefig("figures/ch01-retrecissement.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Niveau de base de chacun des 30 relais, classés par nombre de commandes. Les cercles orange sont les moyennes de chaque relais, les points bleus leurs versions rétrécies par le modèle mixte, les traits noirs la vérité. Les segments gris relient les deux estimations. Le rétrécissement est fort pour les petits relais (à gauche) et faible pour les grands (à droite).](figures/ch01-retrecissement.png)

Le dessin raconte l'idée centrale. À gauche, les **petits** relais (4 à 8 commandes) : leur moyenne brute (cercle orange) est très variable, parfois extrême ; le modèle la **ramène nettement vers 0** (point bleu), ce qui la rapproche souvent de la vérité (trait noir). À droite, les **grands** relais : l'estimation brute est déjà fiable et le rétrécissement est faible. Ce principe, **« emprunter de la force aux autres groupes »**, est l'un des plus puissants de la statistique moderne : on le retrouvera dans le cadre bayésien (chapitre 6, avec la loi *a priori* $u_j\sim\mathcal N(0,\tau^2)$).

### 1.7.5 Pente aléatoire : chaque relais a sa propre sensibilité au retard

Jusqu'ici, tous les relais partagent la même pente (−0,7 point par jour de retard, en moyenne). Mais les vraies données ont été produites avec une **pente propre à chaque relais** ($u_{1j}$). On l'inclut par une **pente aléatoire** : $y_{ij}=\beta_0+\beta_1x_{ij}+\dots+u_{0j}+u_{1j}x_{ij}+\varepsilon_{ij}$, où le couple $(u_{0j},u_{1j})$ est tiré d'une loi normale bidimensionnelle de matrice de covariance $\mathbf G$.

```python
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    m_rs = smf.mixedlm("note ~ dc + urbain", rel, groups=rel["relais"], re_formula="~dc").fit(reml=True, method="lbfgs")
print("Converge :", m_rs.converged)
print(m_rs.summary().tables[1])
G = m_rs.cov_re
print(f"\nécart-type des niveaux de base : {np.sqrt(G.iloc[0, 0]):.3f} (vrai : 1,6) | écart-type des pentes : {np.sqrt(G.iloc[1, 1]):.3f} (vrai : 0,3)")
print(f"corrélation niveau de base / pente : {G.iloc[0, 1] / np.sqrt(G.iloc[0, 0] * G.iloc[1, 1]):.2f} (vraie : 0) | écart-type résiduel : {np.sqrt(m_rs.scale):.3f} (vrai : 1,8)")
```
<!--sortie-->
```text
Converge : True
                 Coef. Std.Err.        z  P>|z|  [0.025  0.975]
Intercept       12.596    0.339   37.166  0.000  11.932  13.260
dc              -0.760    0.064  -11.806  0.000  -0.886  -0.634
urbain           0.277    0.501    0.553  0.581  -0.705   1.259
Group Var        1.427    0.252                                
Group x dc Cov   0.072    0.044                                
dc Var           0.079    0.017                                

écart-type des niveaux de base : 1.195 (vrai : 1,6) | écart-type des pentes : 0.281 (vrai : 0,3)
corrélation niveau de base / pente : 0.21 (vraie : 0) | écart-type résiduel : 1.930 (vrai : 1,8)
```

Les composantes de variance sont raisonnablement proches des vraies valeurs, compte tenu du petit nombre de relais : l'écart-type des niveaux de base est estimé à 1,19 (vrai : 1,6, mais **réalisé** : 1,31 : l'estimation colle à ce qui a effectivement été tiré), celui des pentes à 0,28 (vrai : 0,3), l'écart-type résiduel à 1,93 (vrai : 1,8). La corrélation estimée niveau/pente (0,21), alors que la vraie est nulle, est du bruit d'échantillonnage (son erreur est large avec 30 relais). Les **effets fixes** sont bien retrouvés pour le délai : −0,76 point par jour (vrai : −0,7, intervalle [−0,89 ; −0,63]) ; en revanche l'effet « urbain » est estimé à 0,28 avec une erreur standard de 0,50 : **positif mais très imprécis** (la vraie valeur, 1,2, est à moins de deux erreurs standard). Avec 30 relais, on ne peut tout simplement pas mesurer un effet de niveau groupe de cette taille avec précision.

**Comparer les deux modèles par un test du rapport de vraisemblance.** Les modèles à intercept aléatoire seul et à intercept + pente aléatoire sont emboîtés. On compare leurs vraisemblances. Comme les deux modèles ont les **mêmes effets fixes**, la REML conviendrait aussi ; l'usage prudent, que nous suivons, est de comparer les modèles ajustés par **maximum de vraisemblance** (ML), car la vraisemblance REML ne se compare pas entre modèles d'effets fixes différents.

```python
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    ml_ri = smf.mixedlm("note ~ dc + urbain", rel, groups=rel["relais"]).fit(reml=False)      # optimiseur par défaut (voir la remarque ci-dessous)
    ml_rs = smf.mixedlm("note ~ dc + urbain", rel, groups=rel["relais"], re_formula="~dc").fit(reml=False, method="lbfgs")
LR = 2 * (ml_rs.llf - ml_ri.llf)
# Sous H0, la variance de la pente est sur le bord de l'espace des paramètres (>= 0) : loi limite = mélange 50/50 de chi²(1) et chi²(2)
p_val = 0.5 * stats.chi2.sf(LR, 1) + 0.5 * stats.chi2.sf(LR, 2)
print(f"log-vraisemblance (ML) : intercept aléatoire = {ml_ri.llf:.2f} | intercept + pente aléatoires = {ml_rs.llf:.2f}")
print(f"LR = {LR:.2f} | p-valeur (mélange de chi²) = {p_val:.2e}")
print(f"AIC : {-2 * ml_ri.llf + 2 * 5:.1f} (intercept aléatoire, 5 paramètres) contre {-2 * ml_rs.llf + 2 * 7:.1f} (intercept + pente, 7 paramètres)")
```
<!--sortie-->
```text
log-vraisemblance (ML) : intercept aléatoire = -1067.99 | intercept + pente aléatoires = -1047.41
LR = 41.15 | p-valeur (mélange de chi²) = 6.50e-10
AIC : 2146.0 (intercept aléatoire, 5 paramètres) contre 2108.8 (intercept + pente, 7 paramètres)
```

> ⚠️ **Un piège de l'optimisation.** En préparant ce bloc, la même ligne ajustée avec `method="lbfgs"` (l'optimiseur que nous avions utilisé pour la pente aléatoire) a renvoyé une log-vraisemblance **infinie** pour le modèle à intercept aléatoire, sans la moindre erreur : l'optimiseur avait convergé vers une solution dégénérée (variance entre groupes égale à 0). Avec l'optimiseur par défaut, ou avec `bfgs`, on obtient −1067,99, la valeur que donne aussi `lme4`. **Un optimiseur peut échouer en silence.** Vérifiez toujours qu'un ajustement est plausible (log-vraisemblance finie, variances raisonnables) et, dans le doute, comparez deux optimiseurs ou le résultat de `lme4`.

> ⚠️ **Un piège du test.** Tester qu'une **variance** est nulle ($H_0:\tau_1^2=0$) place l'hypothèse nulle **au bord** de l'espace des paramètres (une variance est $\ge0$) : la loi du rapport de vraisemblance n'est pas un simple $\chi^2$ mais un **mélange** de $\chi^2$ (ici 50/50 entre $\chi^2_1$ et $\chi^2_2$). Utiliser un $\chi^2_2$ naïf est **conservateur** (p-valeur trop grande).

Visualisons maintenant le résultat : les droites de **chaque relais** (prédites avec leurs effets aléatoires), autour de la droite moyenne :

```python
fig, ax = plt.subplots(figsize=(8.0, 4.8))
dd = np.arange(-4, 5.01, 1.0)
for j, g in enumerate(sorted(rel["relais"].unique())):
    re = m_rs.random_effects[g]
    u_urb = urbain[j]
    y_g = m_rs.fe_params["Intercept"] + m_rs.fe_params["urbain"] * u_urb + re["Group"] + (m_rs.fe_params["dc"] + re["dc"]) * dd
    ax.plot(dd + 5, y_g, color=ORANGE if u_urb else AQUA, lw=0.9, alpha=0.55)
ax.plot(dd + 5, m_rs.fe_params["Intercept"] + m_rs.fe_params["dc"] * dd, color=ENCRE, lw=3, label="effet moyen (effets fixes), relais non urbain")
ax.scatter(rel["delai"], rel["note"], s=6, color=GRIS, alpha=0.35)
ax.plot([], [], color=ORANGE, lw=1.4, label="relais urbains"); ax.plot([], [], color=AQUA, lw=1.4, label="relais non urbains")
ax.set_xlabel("délai de livraison (jours)"); ax.set_ylabel("note de satisfaction (sur 20)")
ax.legend(frameon=False, fontsize=8.5, loc="lower left")
ax.set_xlim(0.7, 10.3)
plt.savefig("figures/ch01-droites-par-relais.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Droites de régression propres à chaque relais (orange : urbains, vert : non urbains) autour de l'effet moyen (noir). Les relais diffèrent par leur niveau de base (décalage vertical) et par leur sensibilité au retard (pente).](figures/ch01-droites-par-relais.png)

**Les mêmes résultats en R avec `lme4`.** Le paquet `lme4` est la référence pour ces modèles. Les nombres doivent coïncider avec ceux de `statsmodels` (le fichier `donnees/ch01-relais.csv` vient d'être écrit par notre bloc Python) :

```r
suppressMessages(library(lme4))
d <- read.csv("donnees/ch01-relais.csv")
d$dc <- d$delai - 5
m <- lmer(note ~ dc + urbain + (1 + dc | relais), data = d)
print(round(fixef(m), 4))
print(VarCorr(m), digits = 4)
cat("log-vraisemblance REML :", round(as.numeric(logLik(m)), 3), "\n")
```
<!--sortie-->
```text
(Intercept)          dc      urbain 
    12.5960     -0.7598      0.2769 
 Groups   Name        Std.Dev. Corr
 relais   (Intercept) 1.1948       
          dc          0.2812   0.21
 Residual             1.9299       
log-vraisemblance REML : -1049.555 
```

### 1.7.6 Pourquoi ignorer les groupes est dangereux : une simulation

Terminons par la démonstration promise : l'effet d'ignorer la structure de groupes sur la fiabilité des tests. Prenons les **mêmes** tailles de relais et la même variance entre relais, mais supposons que le type de relais (urbain ou non) n'a **aucun effet** réel. Un bon test doit alors rejeter l'hypothèse « aucun effet » dans **5 %** des cas. Combien rejettent-ils réellement ? On répète 300 fois.

```python
rng2 = np.random.default_rng(2024)
R = 300
rej_mco, rej_mixte, z_mixte, tau2_est = 0, 0, [], []
degenere_lbfgs, degenere_defaut = 0, 0
groupe = np.repeat(np.arange(J), tailles)
urb_obs = urbain[groupe]
dc_obs = rel["dc"].to_numpy()
for r in range(R):
    u = rng2.normal(0, 1.6, J)
    y = 12 + u[groupe] - 0.7 * dc_obs + rng2.normal(0, 1.8, len(groupe))                   # AUCUN effet du type de relais
    d_sim = pd.DataFrame({"note": y, "dc": dc_obs, "urbain": urb_obs, "g": groupe})
    p_mco = sm.OLS(y, sm.add_constant(d_sim[["dc", "urbain"]])).fit().pvalues["urbain"]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        f = smf.mixedlm("note ~ dc + urbain", d_sim, groups=d_sim["g"]).fit(reml=True)                # optimiseur par défaut
        if r < 60:                                                                                   # même ajustement avec lbfgs, sur 60 répétitions
            f2 = smf.mixedlm("note ~ dc + urbain", d_sim, groups=d_sim["g"]).fit(reml=True, method="lbfgs")
            degenere_lbfgs += f2.cov_re.iloc[0, 0] < 1e-6
            degenere_defaut += f.cov_re.iloc[0, 0] < 1e-6
    rej_mco += p_mco < 0.05
    rej_mixte += f.pvalues["urbain"] < 0.05
    z_mixte.append(f.params["urbain"] / f.bse["urbain"])
    tau2_est.append(f.cov_re.iloc[0, 0])
print(f"quand AUCUN effet n'existe, part de tests « significatifs à 5 % » sur la variable urbain, sur {R} simulations :")
print(f"  régression ordinaire (groupes ignorés) : {rej_mco / R:.1%}")
print(f"  modèle mixte (intercept aléatoire)     : {rej_mixte / R:.1%}   | écart-type de la statistique z : {np.std(z_mixte):.2f} (théorie : 1)")
print(f"variance entre relais estimée en moyenne : {np.mean(tau2_est):.2f} (vraie valeur : {1.6**2:.2f})")
print(f"sur 60 répétitions, ajustements qui dégénèrent (variance estimée = 0) : optimiseur par défaut = {degenere_defaut}/60 | lbfgs = {degenere_lbfgs}/60")
```
<!--sortie-->
```text
quand AUCUN effet n'existe, part de tests « significatifs à 5 % » sur la variable urbain, sur 300 simulations :
  régression ordinaire (groupes ignorés) : 55.3%
  modèle mixte (intercept aléatoire)     : 6.7%   | écart-type de la statistique z : 1.04 (théorie : 1)
variance entre relais estimée en moyenne : 2.54 (vraie valeur : 2.56)
sur 60 répétitions, ajustements qui dégénèrent (variance estimée = 0) : optimiseur par défaut = 0/60 | lbfgs = 43/60
```

La régression ordinaire, qui ignore le groupage, déclare un effet « significatif » dans **plus de la moitié** des simulations alors qu'il n'y a **aucun effet** : plus de dix fois le taux nominal de 5 %. C'est la conséquence directe de l'effet de plan : des **faux positifs en rafale**. Le modèle mixte, lui, se tient près du niveau nominal (un peu au-dessus de 5 %, ce qui est attendu : l'approximation de Wald est légèrement optimiste avec seulement 30 groupes) ; sa statistique $z$ a un écart-type voisin de 1, et sa variance entre relais est estimée sans biais notable. Voilà pourquoi, dès que les données sont groupées, **les erreurs standard ordinaires ne sont pas fiables pour les variables de niveau groupe**.

La dernière ligne de la sortie confirme l'avertissement du 1.7.5 : avec l'optimiseur `lbfgs`, la plupart des ajustements de ce modèle pourtant simple dégénèrent (43 sur 60 : la variance entre relais est estimée à 0, ce qui fausse tout), alors que l'optimiseur par défaut ne dégénère jamais (0 sur 60). Un résultat qui paraît plausible peut être faux : c'est pourquoi nous avons systématiquement comparé aux valeurs de `lme4`.

> ⚠️ **Précautions.**
> - **Peu de groupes** (moins de 5 à 10) : les variances entre groupes sont très mal estimées, et les approximations de Wald des effets fixes sont trop optimistes. Dans ce cas, envisagez de traiter le groupe comme un effet **fixe** (une indicatrice par groupe) ou une approche bayésienne.
> - **Effets fixes ou aléatoires ?** Traiter les groupes comme **aléatoires** est pertinent si l'on veut généraliser à d'autres groupes de la même population (les 30 relais sont un échantillon des relais possibles) et si les groupes sont nombreux. Si les groupes sont **tous** ceux qui existent (les 6 villes) et peu nombreux, des effets fixes suffisent.
> - **Convergence** : l'optimisation de ces modèles est parfois délicate (variances proches de 0, corrélations proches de ±1). Essayez un autre optimiseur (`method="bfgs"`, `"powell"`…), simplifiez la structure aléatoire, ou comparez à `lme4`.
> - **Interprétation** : les effets fixes sont des effets **moyens** dans la population de groupes ; les effets aléatoires sont des **écarts** propres à chaque groupe.

> ✅ **À retenir (1.7).**
> - Des observations **groupées** (clients d'une même ville, commandes d'un même relais) ne sont pas indépendantes ; l'ignorer rend les **erreurs standard trop petites**, surtout pour les variables de niveau groupe.
> - Le **modèle mixte** ajoute des **effets aléatoires** : $y_{ij}=\mathbf x_{ij}^\top\boldsymbol\beta+u_j+\varepsilon_{ij}$, $u_j\sim\mathcal N(0,\tau^2)$. L'**ICC** $=\tau^2/(\tau^2+\sigma^2)$ mesure la part de variance due aux groupes (elle était nulle pour les villes, notable pour les relais).
> - Les effets aléatoires sont prédits par **rétrécissement** : $\hat u_j=\frac{\tau^2}{\tau^2+\sigma^2/n_j}\bar r_j$. Les petits groupes sont davantage ramenés vers la moyenne : c'est la **mise en commun partielle**, qui bat à la fois « tous pareils » et « tous différents ».
> - On peut ajouter des **pentes aléatoires**. Les paramètres se comparent par un test du rapport de vraisemblance (**attention** à la loi limite au bord de l'espace des paramètres) ; l'estimation se fait par **REML**.
> - `statsmodels.MixedLM` et `lme4` en R donnent les mêmes résultats.
