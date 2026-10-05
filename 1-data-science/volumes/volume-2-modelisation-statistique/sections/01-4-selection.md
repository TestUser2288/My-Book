## 1.4 Sélection de variables et comparaison de modèles

> 💡 **Intuition.** Face à dix variables possibles, laquelle garder ? Tout garder semble prudent, mais chaque variable inutile ajoute du **bruit** à l'estimation (les erreurs standard grossissent) et peut conduire à des prédictions pires que celles d'un modèle plus simple. À l'inverse, oublier une variable utile introduit un **biais**. Choisir un modèle, c'est trouver le bon compromis entre **trop simple** (qui rate des effets réels) et **trop complexe** (qui s'ajuste au hasard de l'échantillon, c'est le *surajustement*). Il existe pour cela des outils objectifs : des critères d'information (AIC, BIC), la validation croisée, des tests emboîtés.

Pour avoir plus de variables à départager, nous ajoutons aux données précédentes les **notes de l'enquête de satisfaction** (`donnees/enquete_satisfaction.csv`) : 60 % des clients y ont répondu (au hasard), avec huit questions notées de 1 à 5. Les questions q1 à q4 portent sur les **produits**, q5 à q8 sur le **service et la livraison** ; nous en tirons deux scores moyens.

```python hide
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from sklearn.model_selection import KFold
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, ENCRE, GRIS, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#898781", "#e34948"
STYLE = {"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#e1e0d9",
         "grid.linewidth": 0.6, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
         "savefig.facecolor": "#fcfcfb", "font.size": 10, "axes.edgecolor": "#c3c2b7"}
plt.rcParams.update(STYLE)

clients = pd.read_csv("donnees/clients.csv")
df = clients[clients["nb_commandes_an"] > 0].copy()
df["canal"] = pd.Categorical(df["canal_acquisition"], categories=["Boutique", "Site", "Réseaux"])
df["a"] = df["age"] - 36
df["log_panier"] = np.log(df["panier_moyen"])

enq = pd.read_csv("donnees/enquete_satisfaction.csv")
enq["score_produit"] = enq[["q1", "q2", "q3", "q4"]].mean(axis=1)
enq["score_service"] = enq[["q5", "q6", "q7", "q8"]].mean(axis=1)
bq = df.merge(enq[["id_client", "score_produit", "score_service"]], on="id_client")   # clients actifs ayant répondu
print(len(enq), "répondants à l'enquête |", len(df), "clients actifs |", len(bq), "clients actifs répondants")
print(bq[["score_produit", "score_service", "a"]].describe().round(2).loc[["mean", "std", "min", "max"]].to_string())
```
<!--sortie-->
```text
1212 répondants à l'enquête | 1740 clients actifs | 1076 clients actifs répondants
      score_produit  score_service      a
mean           3.64           3.55   0.17
std            0.69           0.74  10.51
min            1.25           1.25 -18.00
max            5.00           5.00  37.00
```

Nous travaillerons sur ces clients (tableau **`bq`**) : les clients actifs qui ont répondu à l'enquête (1 212 répondants à l'enquête, dont 1 076 clients actifs). La question est : quelles variables (âge, canal, ville, offre de bienvenue, scores produit et service, courbure de l'âge…) méritent de figurer dans le modèle du log-panier ?

### 1.4.1 Le surajustement : mieux s'ajuster n'est pas mieux prédire

Rappelons l'enjeu (volume I, chapitre 3 : biais et variance d'un estimateur). Un modèle très flexible épouse les données d'entraînement, y compris leur bruit. Pour le **voir**, faisons une expérience : on tire au hasard **40 clients** pour entraîner un modèle polynomial en l'âge de degré 0, 1, 2…, 8, et on mesure l'erreur sur les clients **non utilisés** pour l'entraînement. On répète 300 fois, et on moyenne.

```python hide
z = ((df["age"] - 36) / 10).to_numpy()                 # âge centré et réduit (évite les problèmes numériques des puissances)
yy = df["log_panier"].to_numpy()
rng = np.random.default_rng(21)
degres = np.arange(0, 9)
err_app, err_test = np.zeros((300, len(degres))), np.zeros((300, len(degres)))
for r in range(300):
    idx = rng.permutation(len(z))
    tr, te = idx[:40], idx[40:]
    for j, d in enumerate(degres):
        coef = np.polyfit(z[tr], yy[tr], d)
        err_app[r, j] = np.mean((yy[tr] - np.polyval(coef, z[tr])) ** 2)
        err_test[r, j] = np.mean((yy[te] - np.polyval(coef, z[te])) ** 2)
res = pd.DataFrame({"degré": degres, "erreur d'apprentissage": err_app.mean(axis=0), "erreur sur nouveaux clients": err_test.mean(axis=0)})
print(res.round(4).to_string(index=False))

fig, ax = plt.subplots(figsize=(6.8, 4.2))
ax.plot(degres, err_app.mean(axis=0), "o-", color=BLEU, lw=2)
ax.plot(degres, err_test.mean(axis=0), "o-", color=ORANGE, lw=2)
ax.text(3.0, 0.108, "erreur sur les clients d'entraînement", color=BLEU, ha="left", va="center")
ax.text(0.1, 0.228, "erreur sur de\nnouveaux clients", color=ORANGE, ha="left", va="center")
ax.text(4.5, 0.33, "au-delà du degré 4, l'erreur\nexplose (axe coupé) :\n1,44 au degré 5,\nplus de 12 000 au degré 8", color=ORANGE, ha="left", va="center")
ax.set_xlabel("degré du polynôme en l'âge (complexité du modèle)")
ax.set_ylabel("erreur quadratique moyenne")
ax.set_xlim(-0.3, 8.5)
ax.set_ylim(0.10, 0.42)
plt.savefig("figures/ch01-surajustement.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
 degré  erreur d'apprentissage  erreur sur nouveaux clients
     0                  0.1610                       0.1684
     1                  0.1490                       0.1629
     2                  0.1454                       0.1696
     3                  0.1423                       0.1853
     4                  0.1389                       0.2958
     5                  0.1353                       1.4399
     6                  0.1311                      50.3002
     7                  0.1261                     612.0571
     8                  0.1220                   12583.0488
figure enregistrée
```

![Erreur d'apprentissage (bleu) et erreur sur de nouveaux clients (orange) selon le degré du polynôme, avec 40 clients d'entraînement. L'erreur d'apprentissage ne fait que baisser ; l'erreur de prédiction est minimale au degré 1 puis explose (axe coupé).](figures/ch01-surajustement.png)

C'est le dessin classique du **surajustement** : l'erreur sur les données d'entraînement (bleu) **ne peut que baisser** quand on ajoute des paramètres, alors que l'erreur sur de nouvelles données (orange) atteint son minimum pour un modèle **simple** (le **degré 1**, avec une erreur de 0,163 : l'âge n'explique qu'une faible partie de la variation, et la vraie relation est linéaire) puis **remonte**, d'abord doucement, puis **vertigineusement** : 1,44 au degré 5 et plus de 12 000 au degré 8. Cette explosion vient de ce que les polynômes de haut degré, ajustés sur 40 clients, oscillent violemment dès qu'on sort de la zone dense des données (certains clients de test ont des âges bien plus extrêmes que ceux de l'entraînement) : c'est le surajustement dans sa forme la plus spectaculaire. L'écart entre les deux courbes mesure l'**optimisme** de l'erreur d'apprentissage. Retenez : *on ne peut jamais juger un modèle sur les données qui ont servi à l'ajuster* ; il faut une mesure corrigée de l'optimisme (critères d'information) ou une mesure sur des données mises de côté (validation).

### 1.4.2 Les critères d'information : AIC et BIC

On cherche une note qui récompense l'ajustement mais **pénalise la complexité**. Le $R^2$ ajusté (1.1.6) en est une, mais la statistique propose mieux : des critères fondés sur la **vraisemblance**.

> 📐 **La vraisemblance du modèle linéaire gaussien.** Sous H5, les $y_i$ sont indépendants de loi $\mathcal N(\mathbf x_i^\top\boldsymbol\beta,\sigma^2)$. La log-vraisemblance est
> $$\ell(\boldsymbol\beta,\sigma^2)=-\frac n2\log(2\pi\sigma^2)-\frac{1}{2\sigma^2}\|\mathbf y-\mathbf X\boldsymbol\beta\|^2 .$$
> La maximiser en $\boldsymbol\beta$ revient à **minimiser les moindres carrés** : l'estimateur du maximum de vraisemblance est $\hat{\boldsymbol\beta}$ (volume I, section 3.2.5). En $\sigma^2$, on obtient $\hat\sigma^2_{\text{MV}}=\text{SCR}/n$ (le facteur $1/n$ et non $1/(n-p)$ : l'estimateur du maximum de vraisemblance est biaisé, comme nous l'avons vu en 1.1.5). En reportant, la valeur maximale de la log-vraisemblance est
> $$\hat\ell=-\frac n2\Big(\log(2\pi)+\log\frac{\text{SCR}}n+1\Big).$$

On pénalise ensuite par le **nombre de paramètres estimés** $k$. Par convention (celle de `statsmodels`), on compte les $p$ coefficients : $k=p$. (Certains logiciels comptent aussi $\sigma^2$, donc $k=p+1$ : cela ajoute la **même constante** à tous les modèles — 2 à l'AIC, $\log n$ au BIC — sans changer le moindre classement ; mais deux logiciels peuvent afficher des valeurs différentes pour le même modèle.)

$$\boxed{\text{AIC}=-2\hat\ell+2k},\qquad\boxed{\text{BIC}=-2\hat\ell+k\log n}.$$

**Plus petit = meilleur.** Les deux critères ont la même forme (ajustement + pénalité), avec une pénalité par paramètre de **2** pour l'AIC et de $\log n$ pour le BIC. Dès que $n\ge8$, $\log n>2$ : le BIC est **plus sévère**, et choisit donc des modèles plus petits.

> 💡 **D'où viennent-ils ?** (1) L'**AIC** (Akaike) estime, à une constante près, la **qualité prédictive** attendue du modèle sur de nouvelles données : $-2\hat\ell$ est trop optimiste (c'est l'erreur d'apprentissage), et on montre (asymptotiquement) que l'optimisme moyen vaut environ $2k$, d'où la correction. Il vise la **prédiction**. (2) Le **BIC** (Schwarz) approche la probabilité *a posteriori* d'un modèle dans une approche bayésienne (chapitre 6) ; il est **consistant** : si le vrai modèle fait partie des candidats, il le retrouve avec une probabilité qui tend vers 1 quand $n$ grandit, ce que l'AIC ne garantit pas (il a tendance à garder quelques variables en trop). Les deux peuvent être en désaccord : c'est normal, ils ne visent pas la même chose.

Sur le modèle âge + canal ajusté sur `bq`, le calcul à la main donne une log-vraisemblance de −431,47, un AIC de 870,94 et un BIC de 890,87 : exactement les valeurs de `statsmodels`.

```python hide
m_ex = smf.ols("log_panier ~ a + C(canal)", data=bq).fit()
n, p = m_ex.model.exog.shape
scr = m_ex.ssr
ll = -n / 2 * (np.log(2 * np.pi) + np.log(scr / n) + 1)
k = p                                                   # convention de statsmodels : on ne compte pas sigma²
print(f"log-vraisemblance : à la main = {ll:.3f} | statsmodels = {m_ex.llf:.3f}")
print(f"AIC : à la main = {-2*ll + 2*k:.3f} | statsmodels = {m_ex.aic:.3f}")
print(f"BIC : à la main = {-2*ll + k*np.log(n):.3f} | statsmodels = {m_ex.bic:.3f}")
```
<!--sortie-->
```text
log-vraisemblance : à la main = -431.472 | statsmodels = -431.472
AIC : à la main = 870.944 | statsmodels = 870.944
BIC : à la main = 890.868 | statsmodels = 890.868
```

> ⚠️ **Deux précautions.** (1) On ne peut comparer les AIC/BIC de deux modèles que s'ils sont ajustés **sur exactement les mêmes données et la même variable réponse** (comparer l'AIC d'un modèle sur $y$ à celui d'un modèle sur $\log y$ n'a aucun sens, sans correction). (2) La valeur absolue d'un AIC ne signifie rien ; seules les **différences** comptent. Une différence de moins de 2 est négligeable ; de plus de 10, très forte.

### 1.4.3 La validation croisée

Les critères d'information reposent sur des hypothèses (modèle bien spécifié, grand échantillon). La **validation croisée** est plus directe : on **simule** la prédiction sur des données nouvelles en réservant une partie des données.

**$K$-fold.** On découpe l'échantillon en $K$ paquets (*folds*) de taille égale (typiquement $K=10$). Pour chaque paquet, on ajuste le modèle sur les $K-1$ autres et on mesure l'erreur de prédiction sur le paquet laissé de côté. La moyenne des erreurs estime l'erreur de généralisation.

**Leave-one-out et la formule de PRESS.** Si $K=n$ (un client par paquet), on parle de *leave-one-out*. Pour la régression linéaire, il n'est pas nécessaire de refaire $n$ ajustements :

> 📐 **Théorème (PRESS).** L'erreur de prédiction de l'observation $i$ par le modèle ajusté **sans elle** est $y_i-\mathbf x_i^\top\hat{\boldsymbol\beta}_{(i)}=\dfrac{\hat\varepsilon_i}{1-h_{ii}}$. La somme des carrés $\text{PRESS}=\sum_i\big(\hat\varepsilon_i/(1-h_{ii})\big)^2$ s'obtient donc **avec un seul ajustement**.
> *Démonstration.* On a vu (1.3.4) que $\hat{\boldsymbol\beta}-\hat{\boldsymbol\beta}_{(i)}=(\mathbf X^\top\mathbf X)^{-1}\mathbf x_i\,\hat\varepsilon_i/(1-h_{ii})$. Multiplions à gauche par $\mathbf x_i^\top$ : $\mathbf x_i^\top\hat{\boldsymbol\beta}-\mathbf x_i^\top\hat{\boldsymbol\beta}_{(i)}=h_{ii}\hat\varepsilon_i/(1-h_{ii})$. Donc $y_i-\mathbf x_i^\top\hat{\boldsymbol\beta}_{(i)}=\hat\varepsilon_i+h_{ii}\hat\varepsilon_i/(1-h_{ii})=\hat\varepsilon_i/(1-h_{ii})$. $\square$

Un client à fort levier est mal prédit quand on le retire, d'où le diviseur $1-h_{ii}$ : l'erreur « honnête » est supérieure au résidu brut. Une boucle explicite de $n=1\,076$ ajustements (un par client écarté) donne le même résultat que la formule : PRESS = 141,52, à comparer à la somme des carrés résiduelle, plus optimiste, de 140,49.

```python hide
Xb, yb = m_ex.model.exog, m_ex.model.endog
h = m_ex.get_influence().hat_matrix_diag
press_formule = np.sum((m_ex.resid / (1 - h)) ** 2)
loo = np.empty(len(yb))
for i in range(len(yb)):                                           # n ajustements, un par client écarté
    mask = np.arange(len(yb)) != i
    b_i = np.linalg.lstsq(Xb[mask], yb[mask], rcond=None)[0]
    loo[i] = yb[i] - Xb[i] @ b_i
print(f"PRESS (formule, 1 ajustement)       = {press_formule:.4f}")
print(f"PRESS (boucle, {len(yb)} ajustements) = {np.sum(loo**2):.4f}")
print(f"erreur quadratique d'apprentissage (SCR) = {scr:.4f}  <- plus optimiste")
```
<!--sortie-->
```text
PRESS (formule, 1 ajustement)       = 141.5167
PRESS (boucle, 1076 ajustements) = 141.5167
erreur quadratique d'apprentissage (SCR) = 140.4879  <- plus optimiste
```

Pour la validation croisée $K$-fold, on écrit une petite fonction (10 paquets). **Règle importante : utiliser les mêmes paquets pour tous les modèles comparés** (comparaison appariée). Pour le modèle âge + canal, le RMSE de validation croisée vaut 0,3629, contre 0,3613 sur les données d'apprentissage.

```python hide
def cv_rmse(formule, data, K=10, graine=0):
    """RMSE de validation croisée K-fold (sur l'échelle du log-panier), mêmes paquets pour tous les modèles."""
    kf = KFold(n_splits=K, shuffle=True, random_state=graine)
    erreurs = []
    for tr, te in kf.split(data):
        m = smf.ols(formule, data=data.iloc[tr]).fit()
        pred = np.asarray(m.predict(data.iloc[te]))
        if pred.size == 1:                                       # modèle à constante seule : predict renvoie un seul nombre
            pred = np.repeat(pred, len(te))
        erreurs.append(data.iloc[te]["log_panier"].to_numpy() - pred)
    e = np.concatenate(erreurs)
    return np.sqrt(np.mean(e ** 2))

print("RMSE par validation croisée 10-fold, modèle log_panier ~ a + C(canal) :", round(cv_rmse("log_panier ~ a + C(canal)", bq), 4))
print("RMSE d'apprentissage                                                   :", round(np.sqrt(scr / n), 4))
```
<!--sortie-->
```text
RMSE par validation croisée 10-fold, modèle log_panier ~ a + C(canal) : 0.3629
RMSE d'apprentissage                                                   : 0.3613
```

### 1.4.4 Comparer plusieurs modèles sur les données de l'enquête

Mettons les outils à l'épreuve. Voici huit modèles candidats, du plus simple au plus chargé :

| | Variables |
|---|---|
| **M0** | constante seule |
| **M1** | âge |
| **M2** | âge + canal |
| **M3** | âge + canal + score produit |
| **M4** | M3 + score service |
| **M5** | M3 + ville + offre de bienvenue |
| **M6** | M3 + âge² + interaction âge × canal |
| **M7** | tout : âge, âge², canal, ville, offre, scores, interactions |

```python hide
bq = bq.copy()
bq["a2"] = bq["a"] ** 2
candidats = {
    "M0": "log_panier ~ 1",
    "M1": "log_panier ~ a",
    "M2": "log_panier ~ a + C(canal)",
    "M3": "log_panier ~ a + C(canal) + score_produit",
    "M4": "log_panier ~ a + C(canal) + score_produit + score_service",
    "M5": "log_panier ~ a + C(canal) + score_produit + C(ville) + offre_bienvenue",
    "M6": "log_panier ~ a * C(canal) + a2 + score_produit",
    "M7": "log_panier ~ a * C(canal) + a2 + C(ville) + offre_bienvenue + score_produit + score_service",
}
lignes, fits = [], {}
for nom, f in candidats.items():
    m = smf.ols(f, data=bq).fit()
    fits[nom] = m
    h = m.get_influence().hat_matrix_diag
    lignes.append({"modèle": nom, "paramètres p": int(m.df_model) + 1, "R²": m.rsquared, "R² ajusté": m.rsquared_adj,
                   "AIC": m.aic, "BIC": m.bic, "RMSE appr.": np.sqrt(m.mse_resid * m.df_resid / m.nobs),
                   "RMSE LOO (PRESS)": np.sqrt(np.mean((m.resid / (1 - h)) ** 2)), "RMSE CV10": cv_rmse(f, bq)})
tab = pd.DataFrame(lignes).set_index("modèle")
with pd.option_context("display.width", 200):
    print(tab.round(4).to_string())
print()
for crit in ["R² ajusté", "AIC", "BIC", "RMSE LOO (PRESS)", "RMSE CV10"]:
    meilleur = tab[crit].idxmax() if crit == "R² ajusté" else tab[crit].idxmin()
    print(f"meilleur modèle selon {crit:18s} : {meilleur}")
```
<!--sortie-->
```text
        paramètres p      R²  R² ajusté        AIC        BIC  RMSE appr.  RMSE LOO (PRESS)  RMSE CV10
modèle                                                                                                
M0                 1  0.0000     0.0000  1082.3441  1087.3251      0.3997            0.4001     0.4005
M1                 2  0.0663     0.0654  1010.5132  1020.4752      0.3863            0.3870     0.3872
M2                 4  0.1829     0.1807   870.9438   890.8679      0.3613            0.3627     0.3629
M3                 5  0.2542     0.2514   774.7862   799.6912      0.3452            0.3469     0.3478
M4                 6  0.2567     0.2532   773.1610   803.0470      0.3446            0.3466     0.3474
M5                11  0.2548     0.2478   785.8815   840.6726      0.3451            0.3487     0.3503
M6                 8  0.2549     0.2500   779.7843   819.6323      0.3451            0.3476     0.3485
M7                15  0.2582     0.2484   788.9871   863.7021      0.3443            0.3491     0.3506

meilleur modèle selon R² ajusté          : M4
meilleur modèle selon AIC                : M4
meilleur modèle selon BIC                : M3
meilleur modèle selon RMSE LOO (PRESS)   : M4
meilleur modèle selon RMSE CV10          : M4
```

```python
print(tab[["paramètres p", "R² ajusté", "AIC", "BIC", "RMSE CV10"]].round(3))
```
<!--sortie-->
```text
        paramètres p  R² ajusté       AIC       BIC  RMSE CV10
modèle                                                        
M0                 1      0.000  1082.344  1087.325      0.400
M1                 2      0.065  1010.513  1020.475      0.387
M2                 4      0.181   870.944   890.868      0.363
M3                 5      0.251   774.786   799.691      0.348
M4                 6      0.253   773.161   803.047      0.347
M5                11      0.248   785.882   840.673      0.350
M6                 8      0.250   779.784   819.632      0.349
M7                15      0.248   788.987   863.702      0.351
```

Lisons ce tableau avec méthode.

- Le **$R^2$ et le RMSE d'apprentissage** s'améliorent (ou restent égaux) à chaque ajout de variables : ils recommandent toujours le modèle le plus gros (M7). Pas un critère de sélection.
- Les **critères corrigés** (AIC, BIC, $R^2$ ajusté, validation croisée) arrêtent leur progression bien avant. Retenez l'ordre de grandeur : l'ajout du **score produit** (M2 → M3) est un gain énorme, l'ajout du **score service** (M3 → M4) est marginal, et tout ce qui vient après (ville, offre, âge², interactions) n'apporte **rien** (voire détériore).
- Le **BIC**, plus sévère, désigne le modèle **M3**. Les autres critères (AIC, $R^2$ ajusté, PRESS, validation croisée) désignent **M4**, qui ajoute le score service, mais **de justesse** : l'AIC de M4 est inférieur de 1,6 point à celui de M3 (différence inférieure à 2 : négligeable, selon la règle du 1.4.2), et le RMSE de validation croisée passe de 0,3478 à 0,3474. M3 et M4 prédisent donc pratiquement aussi bien ; à prédiction égale, on **préfère le plus simple** (principe de parcimonie), ce que fait le BIC. Les trois mesures hors échantillon (PRESS, CV10) sont très proches l'une de l'autre, ce qui rassure sur la fiabilité du classement.

**Les tests emboîtés** (1.2.3) répondent à des questions précises sur des modèles qui se contiennent :

```python hide
print("M2 -> M3 (ajout du score produit) :")
print(sm.stats.anova_lm(fits["M2"], fits["M3"]).round(4).iloc[:, [0, 2, 4, 5]].to_string())
print("\nM3 -> M4 (ajout du score service) :")
print(sm.stats.anova_lm(fits["M3"], fits["M4"]).round(4).iloc[:, [0, 2, 4, 5]].to_string())
print("\nM3 -> M5 (ajout de la ville et de l'offre de bienvenue, 6 paramètres) :")
print(sm.stats.anova_lm(fits["M3"], fits["M5"]).round(4).iloc[:, [0, 2, 4, 5]].to_string())
print("\nM3 -> M6 (âge² et interactions, 3 paramètres) :")
print(sm.stats.anova_lm(fits["M3"], fits["M6"]).round(4).iloc[:, [0, 2, 4, 5]].to_string())
```
<!--sortie-->
```text
M2 -> M3 (ajout du score produit) :
   df_resid  df_diff         F  Pr(>F)
0    1072.0      0.0       NaN     NaN
1    1071.0      1.0  102.2966     0.0

M3 -> M4 (ajout du score service) :
   df_resid  df_diff       F  Pr(>F)
0    1071.0      0.0     NaN     NaN
1    1070.0      1.0  3.6111  0.0577

M3 -> M5 (ajout de la ville et de l'offre de bienvenue, 6 paramètres) :
   df_resid  df_diff       F  Pr(>F)
0    1071.0      0.0     NaN     NaN
1    1065.0      6.0  0.1493  0.9892

M3 -> M6 (âge² et interactions, 3 paramètres) :
   df_resid  df_diff       F  Pr(>F)
0    1071.0      0.0     NaN     NaN
1    1068.0      3.0  0.3316  0.8025
```

Le score produit est hautement significatif ($F\approx102$) ; le score service est **à la limite** ($F\approx3{,}6$, p-valeur de 0,058) ; la ville et l'offre de bienvenue (p-valeur de 0,99), la courbure de l'âge et les interactions (0,80) n'ont **aucun** effet décelable. C'est cohérent avec les critères d'information : *deux méthodes différentes, la même conclusion*. Le cas du score service illustre bien la tension entre AIC et BIC : sa $t$-statistique, voisine de 1,9, dépasse le seuil $\sqrt2\approx1{,}41$ que l'AIC applique implicitement (un paramètre en plus est conservé si $t^2>2$) mais pas le seuil $\sqrt{\log n}\approx2{,}6$ du BIC pour $n\approx1000$.

### 1.4.5 La sélection automatique, et pourquoi il faut s'en méfier

Avec beaucoup de variables, comparer à la main devient impossible, d'où la tentation des procédures automatiques : sélection **ascendante** (*forward* : on part de rien et on ajoute à chaque étape la variable qui améliore le plus), **descendante** (*backward*), **pas à pas** (*stepwise*), ou **tous les sous-ensembles**. Elles sont commodes, mais elles posent un problème **statistique profond** : *le modèle final est choisi sur les données, puis ses p-valeurs sont lues comme si on l'avait choisi à l'avance.* Les p-valeurs et les intervalles du modèle final sont donc **trop optimistes**.

Une simulation le montre. On génère $n=100$ observations d'une variable réponse $y$ qui **n'a aucun lien** avec 20 variables explicatives (toutes du pur bruit). On applique la sélection ascendante par p-valeur (on ajoute la variable la plus significative tant que sa p-valeur est inférieure à 0,05). Combien de « découvertes » la méthode va-t-elle faire ? On répète 500 fois.

```python hide
def selection_ascendante(X, y, alpha=0.05):
    """Sélection ascendante par p-valeur. X : matrice n x q sans constante. Retourne la liste des colonnes retenues."""
    n, q = X.shape
    retenues = []
    while len(retenues) < q:
        meilleur, p_min = None, 1.0
        for j in range(q):
            if j in retenues:
                continue
            Z = np.column_stack([np.ones(n), X[:, retenues + [j]]])
            b, _, _, _ = np.linalg.lstsq(Z, y, rcond=None)
            e = y - Z @ b
            s2 = e @ e / (n - Z.shape[1])
            se = np.sqrt(s2 * np.linalg.inv(Z.T @ Z)[-1, -1])
            pj = 2 * stats.t.sf(abs(b[-1] / se), n - Z.shape[1])
            if pj < p_min:
                meilleur, p_min = j, pj
        if meilleur is None or p_min >= alpha:
            break
        retenues.append(meilleur)
    return retenues

def ols_pvaleurs(X, y):
    Z = np.column_stack([np.ones(len(y)), X])
    b = np.linalg.lstsq(Z, y, rcond=None)[0]
    e = y - Z @ b
    s2 = e @ e / (len(y) - Z.shape[1])
    se = np.sqrt(s2 * np.diag(np.linalg.inv(Z.T @ Z)))
    return 2 * stats.t.sf(np.abs(b / se), len(y) - Z.shape[1])[1:], 1 - (e @ e) / np.sum((y - y.mean()) ** 2)

rng = np.random.default_rng(99)
R, n_obs, q = 500, 100, 20
nb_retenues, r2_final, sig_final, sig_honnete, nb_honnete = [], [], [], [], []
for _ in range(R):
    X = rng.normal(size=(n_obs, q)); y = rng.normal(size=n_obs)            # y est indépendant de tout X
    ret = selection_ascendante(X, y)
    nb_retenues.append(len(ret))
    if ret:
        pv, r2 = ols_pvaleurs(X[:, ret], y)
        r2_final.append(r2); sig_final.append(np.mean(pv < 0.05))
    # procédure honnête : on choisit sur les 50 premiers, on teste sur les 50 autres
    ret_h = selection_ascendante(X[:50], y[:50])
    if ret_h:
        pv_h, _ = ols_pvaleurs(X[50:][:, ret_h], y[50:])
        sig_honnete.append(np.sum(pv_h < 0.05)); nb_honnete.append(len(ret_h))
nb_retenues = np.array(nb_retenues)
print(f"y est du pur bruit, indépendant des {q} variables explicatives (n = {n_obs}).")
print(f"part des jeux de données où au moins une variable est « découverte » : {np.mean(nb_retenues > 0):.1%}  (théorie pour une seule étape : 1 - 0,95^20 = {1 - 0.95**20:.1%})")
print(f"nombre moyen de variables retenues : {nb_retenues.mean():.2f}")
print(f"R² moyen du modèle final (quand il est non vide) : {np.mean(r2_final):.3f}  alors que le vrai R² est 0")
print(f"part de coefficients « significatifs à 5 % » dans le modèle final : {np.mean(sig_final):.1%}  (c'est trompeur : ils ont été choisis POUR l'être)")
print(f"procédure honnête (choix sur la moitié A, test sur la moitié B) : {np.sum(sig_honnete) / np.sum(nb_honnete):.1%} de significatifs parmi les variables retenues (≈ 5 % attendu)")
```
<!--sortie-->
```text
y est du pur bruit, indépendant des 20 variables explicatives (n = 100).
part des jeux de données où au moins une variable est « découverte » : 63.4%  (théorie pour une seule étape : 1 - 0,95^20 = 64.2%)
nombre moyen de variables retenues : 1.09
R² moyen du modèle final (quand il est non vide) : 0.093  alors que le vrai R² est 0
part de coefficients « significatifs à 5 % » dans le modèle final : 100.0%  (c'est trompeur : ils ont été choisis POUR l'être)
procédure honnête (choix sur la moitié A, test sur la moitié B) : 5.6% de significatifs parmi les variables retenues (≈ 5 % attendu)
```

Dans près des deux tiers des jeux de données, la procédure « découvre » au moins une variable explicative, alors qu'il n'y en a **aucune** ; le $R^2$ du modèle final est nettement positif (environ 0,09 en moyenne, alors que la vraie valeur est 0) ; et, dans le modèle final, les coefficients retenus apparaissent **tous** significatifs, ce qui est trompeur : ils n'ont été retenus que parce qu'ils l'étaient. La procédure « honnête », qui **sépare** les données utilisées pour choisir des données utilisées pour tester, retrouve le taux d'erreur attendu de 5 %.

> ⚠️ **Les défauts de la sélection automatique.** (1) Les **p-valeurs et intervalles** du modèle final sont **trop optimistes** (biais de sélection). (2) Les coefficients retenus sont **gonflés** en valeur absolue (on garde ceux qui, par chance, sont grands). (3) Le résultat est **instable** : un autre échantillon donne un autre modèle. (4) Les procédures ne connaissent pas **le sens** des variables : on risque de retirer une variable de confusion essentielle. (5) Plus on essaie de modèles, plus on a de chances d'en trouver un « bon » par hasard (c'est le problème des tests multiples du volume I, section 3.5.5).

> 💡 **Bonnes pratiques.** (1) **Commencez par la connaissance du domaine** : quelles variables ont un sens ? (2) Fixez les modèles candidats **à l'avance**, en petit nombre, et comparez-les par AIC/BIC et validation croisée. (3) Si vous devez explorer beaucoup de variables, **mettez de côté un échantillon de test** *avant* de commencer, et ne l'utilisez qu'**une fois**, à la fin. (4) Pour la prédiction avec beaucoup de variables, préférez la **régularisation** (section 1.5), qui fait une sélection plus stable. (5) Décrivez honnêtement tout ce qui a été essayé.

### 1.4.6 Verdict : retrouver la vérité

Nous avons un luxe : les données sont simulées, nous connaissons donc le vrai modèle (détails dans la documentation de `build/donnees2.py`). Les clients actifs ont été produits par

$$\log(\text{panier})=4{,}00+0{,}008\,(\text{âge}-36)+\delta_{\text{canal}}+0{,}12\,F_1+\varepsilon,\qquad\varepsilon\sim\mathcal N(0,\,0{,}35^2),$$

avec $\delta=+0{,}22$ pour la Boutique, $+0{,}05$ pour le Site, $-0{,}12$ pour Réseaux. Ici $F_1$ est un **« goût pour les produits »** non observé (de moyenne 0 et d'écart-type 1) ; ni la ville, ni l'offre de bienvenue, ni le score de service **n'interviennent** dans le panier. Comparons au modèle M3 retenu par le BIC :

```python hide-code
m3 = fits["M3"]
ic = m3.conf_int()
vrai_site, vrai_reseaux = 0.05 - 0.22, -0.12 - 0.22          # effets du Site et de Réseaux RELATIVEMENT à la Boutique
vrai = {"Intercept": np.nan, "C(canal)[T.Site]": vrai_site, "C(canal)[T.Réseaux]": vrai_reseaux, "a": 0.008}
comp = pd.DataFrame({"estimation (M3)": m3.params, "IC95 bas": ic[0], "IC95 haut": ic[1]})
comp["vérité"] = pd.Series(vrai)
comp["IC contient la vérité ?"] = [("oui" if (lo <= v <= hi) else "non") if not np.isnan(v) else "—" for lo, hi, v in zip(comp["IC95 bas"], comp["IC95 haut"], comp["vérité"])]
print(comp.round(4).to_string())
```
<!--sortie-->
```text
                     estimation (M3)  IC95 bas  IC95 haut  vérité IC contient la vérité ?
Intercept                     3.6543    3.5385     3.7701     NaN                       —
C(canal)[T.Site]             -0.1573   -0.2114    -0.1032  -0.170                     oui
C(canal)[T.Réseaux]          -0.3519   -0.4045    -0.2993  -0.340                     oui
a                             0.0097    0.0078     0.0117   0.008                     oui
score_produit                 0.1557    0.1255     0.1859     NaN                       —
```

```python hide
print("Dans M7 (le modèle « tout »), p-valeurs des variables sans effet réel :")
print(fits["M7"].pvalues[["C(ville)[T.Ville A]", "C(ville)[T.Ville B]", "C(ville)[T.Ville C]", "C(ville)[T.Ville D]", "C(ville)[T.Ville E]", "offre_bienvenue", "a2", "score_service"]].round(3).to_string())
```
<!--sortie-->
```text
Dans M7 (le modèle « tout »), p-valeurs des variables sans effet réel :
C(ville)[T.Ville A]    0.901
C(ville)[T.Ville B]    0.934
C(ville)[T.Ville C]    0.526
C(ville)[T.Ville D]    0.808
C(ville)[T.Ville E]    0.883
offre_bienvenue        0.788
a2                     0.300
score_service          0.051
```

Les effets du **canal** et de l'**âge** sont retrouvés : les intervalles à 95 % contiennent les vraies valeurs (−0,17 pour le Site, −0,34 pour Réseaux, +0,008 par année d'âge). La méthode a bien écarté les variables **sans effet réel** (ville, offre, courbure, interactions : dans le modèle « tout » M7, leurs p-valeurs vont de 0,30 à 0,93). L'intercept ne se compare pas directement, car dans M3 il correspond à un score produit de 0 (une valeur impossible sur une échelle de 1 à 5) : un bon exemple de la nécessité de **centrer** les variables pour interpréter la constante.

Reste le cas du **score service** : il n'a aucun effet direct dans le vrai modèle du panier, et pourtant l'AIC et la validation croisée le **gardent**, de justesse, avec une $t$-statistique voisine de 1,9. C'est la **conséquence mécanique** de la corrélation entre les facteurs « produit » et « service » dans la population (corrélation de 0,3 entre $F_1$ et $F_2$) : le score de service est un peu informatif sur $F_1$, donc sur le panier. Et c'est un rappel qu'**une association n'est pas un effet**.

**Un dernier point, sur le score produit.** Le vrai effet est de **0,12 par écart-type de $F_1$**. Or le coefficient estimé (0,15 environ) est un effet **par point de note**, ce qui est autre chose : la note moyenne est un reflet **imparfait** de $F_1$ (chaque question est bruitée). Un calcul direct à partir de la façon dont les notes ont été simulées (générateur `build/donnees2.py` : $q_j\approx3{,}6+0{,}95\,(\lambda_jF_1+\sqrt{1-\lambda_j^2}\,\eta_j)$, avec des poids $\lambda_j=0{,}8;\,0{,}7;\,0{,}75;\,0{,}6$) permet de prédire le coefficient attendu **par point de note** :

```python hide
lam = np.array([0.80, 0.70, 0.75, 0.60])
var_bruit = np.mean(1 - lam**2) / 4                       # variance du bruit de la moyenne de 4 questions (en unités de F1)
charge = lam.mean()                                        # poids moyen de F1 dans la moyenne des questions
fiabilite = charge**2 / (charge**2 + var_bruit)            # part de la variance de la note qui provient de F1
cov_F_score = 0.95 * charge
var_score = 0.95**2 * (charge**2 + var_bruit)
pente_F_sur_score = cov_F_score / var_score                # E[F1 | score] = pente * (score - moyenne)
print(f"fiabilité du score produit : {fiabilite:.2f}")
print(f"effet attendu par point de note : 0,12 x {pente_F_sur_score:.3f} = {0.12 * pente_F_sur_score:.3f}   | estimé dans M3 : {m3.params['score_produit']:.3f}  (IC95 % : [{ic.loc['score_produit', 0]:.3f} ; {ic.loc['score_produit', 1]:.3f}])")
```
<!--sortie-->
```text
fiabilité du score produit : 0.81
effet attendu par point de note : 0,12 x 1.192 = 0.143   | estimé dans M3 : 0.156  (IC95 % : [0.125 ; 0.186])
```

La valeur attendue tombe **à l'intérieur** de l'intervalle de confiance. La **fiabilité** (la part de la variance de la note qui provient du vrai facteur, environ 0,8) est une notion générale : quand une variable explicative est mesurée avec du bruit, son coefficient est **atténué** par rapport à l'effet de la grandeur « vraie » (*erreur de mesure*) ; ici, la conversion d'échelle (par point de note plutôt que par écart-type de $F_1$) cache cet effet, mais il est bien là.

> 🧪 **Une dernière subtilité (hors programme, mais honnête).** Nous n'observons le panier que pour les clients **actifs** (ayant commandé), et l'activité dépend elle-même de $F_1$ dans la simulation (le goût pour les produits augmente le nombre de commandes). En ne gardant que les clients actifs, nous opérons une **sélection** qui peut biaiser légèrement la relation entre les notes et le panier. Le biais est ici faible et invisible dans les intervalles ; mais en pratique, restreindre un échantillon sur une variable liée à la réponse est une source classique de biais, que la section 2.6 (modèles à zéros excédentaires) permettra de traiter proprement.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.6 et 1.7, exercice 1.7.

> ✅ **À retenir (1.4).**
> - Un modèle plus complexe s'ajuste toujours mieux aux données d'**entraînement** ($R^2$ croissant) mais pas forcément aux **nouvelles** données : c'est le **surajustement**.
> - **AIC** $=-2\hat\ell+2k$ vise la prédiction ; **BIC** $=-2\hat\ell+k\log n$ est plus sévère et consistant. Comparez les modèles sur les mêmes données et la même réponse ; seules les **différences** comptent.
> - La **validation croisée** estime l'erreur sur de nouvelles données ; pour la régression linéaire, le leave-one-out s'obtient d'un seul ajustement : $\text{PRESS}=\sum_i(\hat\varepsilon_i/(1-h_{ii}))^2$.
> - Les **tests $F$ emboîtés** comparent deux modèles qui se contiennent.
> - La **sélection automatique** fabrique des « découvertes » dans le bruit, gonfle les coefficients et rend les p-valeurs trompeuses : fixez des modèles candidats à l'avance, séparez choix et test, expliquez ce qui a été essayé.
> - Sur nos données, les critères retrouvent la vérité : âge, canal et score produit comptent ; ville, offre de bienvenue et courbure n'ont aucun effet.
