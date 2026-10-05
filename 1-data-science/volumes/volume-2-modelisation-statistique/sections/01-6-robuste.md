## 1.6 ➕ Pour aller plus loin : la régression robuste

> 🧭 **Section optionnelle.** Elle prolonge la discussion des observations aberrantes et influentes de 1.3.4 et s'appuie sur l'idée, vue au volume I (section 3.1.3), que la médiane est plus robuste que la moyenne.

> 💡 **Intuition.** Les moindres carrés élèvent chaque écart **au carré** : un client dont le panier est dix fois trop grand (une virgule mal placée dans un export) pèse **cent fois** plus qu'un client ordinaire. Quelques erreurs de saisie peuvent suffire à fausser tout le modèle. La régression **robuste** limite l'influence des points extrêmes : elle cherche la droite qui colle à **la majorité** des données, sans se laisser tirer par quelques cas isolés. Elle fait pour la régression ce que la médiane fait pour la moyenne.

Voici la préparation habituelle :

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, VIOLET, ENCRE, GRIS, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#0b0b0b", "#898781", "#e34948"
STYLE = {"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#e1e0d9",
         "grid.linewidth": 0.6, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
         "savefig.facecolor": "#fcfcfb", "font.size": 10, "axes.edgecolor": "#c3c2b7"}
plt.rcParams.update(STYLE)

clients = pd.read_csv("donnees/clients.csv")
df = clients[clients["nb_commandes_an"] > 0].copy().reset_index(drop=True)
df["canal"] = pd.Categorical(df["canal_acquisition"], categories=["Boutique", "Site", "Réseaux"])
df["a"] = df["age"] - 36
df["log_panier"] = np.log(df["panier_moyen"])
m_propre = smf.ols("log_panier ~ a + C(canal)", data=df).fit()
print(len(df), "clients | coefficients du modèle sur les données propres :")
print(m_propre.params.round(4).to_string())
```
<!--sortie-->
```text
1740 clients | coefficients du modèle sur les données propres :
Intercept                4.2206
C(canal)[T.Site]        -0.1571
C(canal)[T.Réseaux]   -0.3368
a                        0.0092
```

### 1.6.1 La fragilité des moindres carrés

Reprenons l'exemple du volume I (3.1.3) : cinq commandes de 20, 25, 30, 35 et 400 €. La **moyenne** (102 €) est entraînée par la dernière valeur ; la **médiane** (30 €) ne bouge pas. On dit que la médiane a un **point de rupture** de 50 % (il faut corrompre la moitié des données pour la faire dériver à l'infini) alors que celui de la moyenne est de **0 %** (une seule valeur suffit). Les moindres carrés, qui généralisent la moyenne, héritent de cette fragilité.

> 📐 **Pourquoi ? La fonction d'influence.** Un estimateur $\hat\theta$ minimise $\sum_i\rho(e_i)$. Son équation d'estimation est $\sum_i\psi(e_i)\,\mathbf x_i=\mathbf 0$ où $\psi=\rho'$ (comme les équations normales du 1.1.3, qui correspondent à $\rho(e)=e^2/2$ et $\psi(e)=e$). La fonction $\psi$ mesure **l'influence** d'un résidu sur l'estimation. Pour les moindres carrés, $\psi(e)=e$ n'est **pas bornée** : plus un point est extrême, plus il tire. Un estimateur robuste choisit un $\rho$ dont la dérivée $\psi$ est **bornée** : au-delà d'un seuil, un résidu de plus en plus grand n'a pas plus d'influence.

### 1.6.2 Les M-estimateurs et la fonction de Huber

La fonction de **Huber** est quadratique pour les petits résidus (comme les moindres carrés : efficace quand tout va bien) et **linéaire** pour les grands (comme la valeur absolue : l'influence est plafonnée). Avec un seuil $c$ (en unités d'écart-type du résidu) :

$$\rho_c(u)=\begin{cases}\tfrac12u^2&\text{si }|u|\le c\\ c|u|-\tfrac12c^2&\text{si }|u|>c\end{cases}\qquad\psi_c(u)=\begin{cases}u&\text{si }|u|\le c\\ c\,\operatorname{signe}(u)&\text{si }|u|>c\end{cases}\qquad u=\frac{e}{s}$$

où $s$ est une estimation **robuste** de l'échelle des résidus : on prend le **MAD** (écart absolu médian) : $s=\operatorname{médiane}(|e_i-\operatorname{médiane}(e)|)/0{,}6745$ (le facteur 0,6745 rend $s$ cohérent avec l'écart-type pour des erreurs normales). Le seuil usuel $c=1{,}345$ garantit que, **si les erreurs sont réellement normales**, l'estimateur de Huber conserve **95 % de l'efficacité** des moindres carrés : on perd très peu quand tout va bien, et on gagne beaucoup quand il y a des aberrations.

**L'algorithme : les moindres carrés repondérés (IRLS).** Les équations d'estimation $\sum_i\psi(u_i)\mathbf x_i=\mathbf 0$ s'écrivent $\sum_iw_iu_i\mathbf x_i=\mathbf 0$ avec les **poids** $w_i=\psi(u_i)/u_i$ : une régression **pondérée**. Pour Huber, $w_i=1$ si $|u_i|\le c$ et $w_i=c/|u_i|$ sinon : chaque point reçoit un poids d'autant plus petit qu'il est loin de la droite. Comme les poids dépendent des résidus qui dépendent de $\boldsymbol\beta$, on **itère** : (1) calculer les résidus, (2) en déduire les poids, (3) refaire une régression pondérée, jusqu'à stabilisation.

Dessinons les fonctions de perte et de poids de trois méthodes : les moindres carrés, Huber, et la fonction « bisquare » de Tukey (plus radicale : les points très éloignés reçoivent un poids **nul**).

```python
u = np.linspace(-6, 6, 400)
c_h, c_t = 1.345, 4.685
rho_mco = u**2 / 2
rho_huber = np.where(np.abs(u) <= c_h, u**2 / 2, c_h * np.abs(u) - c_h**2 / 2)
rho_tukey = np.where(np.abs(u) <= c_t, c_t**2 / 6 * (1 - (1 - (u / c_t)**2)**3), c_t**2 / 6)
w_mco = np.ones_like(u)
w_huber = np.where(np.abs(u) <= c_h, 1.0, c_h / np.abs(u))
w_tukey = np.where(np.abs(u) <= c_t, (1 - (u / c_t)**2)**2, 0.0)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.0))
for rho, nom, col in [(rho_mco, "moindres carrés", GRIS), (rho_huber, "Huber (c = 1,345)", BLEU), (rho_tukey, "Tukey bisquare (c = 4,685)", ORANGE)]:
    ax1.plot(u, rho, color=col, lw=2.2, label=nom)
ax1.set_ylim(0, 9); ax1.set_xlabel("résidu standardisé u"); ax1.set_ylabel("perte ρ(u)"); ax1.set_title("Perte attribuée à un résidu", fontsize=10.5)
ax1.legend(frameon=False, loc="upper center", fontsize=9)
for w, col, nom in [(w_mco, GRIS, "moindres carrés : poids constant égal à 1"), (w_huber, BLEU, "Huber : poids c/|u| au-delà de 1,345"), (w_tukey, ORANGE, "Tukey : poids nul au-delà de 4,685")]:
    ax2.plot(u, w, color=col, lw=2.2, label=nom)
ax2.set_ylim(-0.05, 1.15); ax2.set_xlabel("résidu standardisé u"); ax2.set_ylabel("poids w(u)"); ax2.set_title("Poids donné à l'observation", fontsize=10.5)
ax2.legend(frameon=False, loc="lower center", fontsize=8.5, bbox_to_anchor=(0.5, 0.08))
plt.tight_layout()
plt.savefig("figures/ch01-fonctions-robustes.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Fonctions de perte (à gauche) et poids (à droite). Les moindres carrés (gris) pénalisent quadratiquement et donnent le même poids à tous. Huber (bleu) devient linéaire au-delà de 1,345 écart-type. Tukey (orange) plafonne la perte et annule le poids des points très éloignés.](figures/ch01-fonctions-robustes.png)

Écrivons l'algorithme IRLS à la main et comparons à `statsmodels` (`RLM`, *robust linear model*) sur les données propres :

```python
def huber_irls(X, y, c=1.345, n_iter=100, tol=1e-10):
    beta = np.linalg.lstsq(X, y, rcond=None)[0]                  # départ : les moindres carrés
    for _ in range(n_iter):
        e = y - X @ beta
        s = np.median(np.abs(e - np.median(e))) / 0.6745        # échelle robuste (MAD)
        u = e / s
        w = np.where(np.abs(u) <= c, 1.0, c / np.abs(u))        # poids de Huber
        W = X.T * w                                              # X' diag(w)
        beta_new = np.linalg.solve(W @ X, W @ y)                 # régression pondérée
        if np.max(np.abs(beta_new - beta)) < tol:
            beta = beta_new
            break
        beta = beta_new
    return beta, w, s

Xp, yp = m_propre.model.exog, m_propre.model.endog
b_main, w_main, s_main = huber_irls(Xp, yp)
rlm = sm.RLM(yp, Xp, M=sm.robust.norms.HuberT(t=1.345)).fit()
print(pd.DataFrame({"MCO": m_propre.params, "Huber (à la main)": b_main, "RLM statsmodels": rlm.params}).round(4).to_string())
print(f"échelle robuste s : {s_main:.4f} | écart-type résiduel des MCO : {np.sqrt(m_propre.scale):.4f}")
print(f"part des clients dont le poids est inférieur à 1 : {np.mean(w_main < 1):.1%}")
```
<!--sortie-->
```text
                          MCO  Huber (à la main)  RLM statsmodels
Intercept              4.2206             4.2171           4.2172
C(canal)[T.Site]      -0.1571            -0.1602          -0.1602
C(canal)[T.Réseaux] -0.3368            -0.3331          -0.3332
a                      0.0092             0.0090           0.0090
échelle robuste s : 0.3667 | écart-type résiduel des MCO : 0.3705
part des clients dont le poids est inférieur à 1 : 18.1%
```

Sur des données **propres**, Huber et les moindres carrés donnent presque les mêmes coefficients : c'est l'efficacité de 95 % en action : on ne paie quasiment rien pour la robustesse. (L'écart minime, de l'ordre de $10^{-4}$, entre notre version et `RLM` tient à des choix de détail sur l'estimation de l'échelle.) Remarquez aussi que **18 % des clients reçoivent un poids inférieur à 1 même sur ces données propres** : ce n'est pas un signe d'anomalie, c'est exactement la proportion attendue pour des erreurs normales, puisque $\mathbb P(|Z|>1{,}345)\approx17{,}9\,\%$. Huber n'écarte pas 18 % des données : il en réduit un peu le poids.

### 1.6.3 Une contamination : les erreurs de saisie

Corrompons maintenant les données, comme le ferait un export mal formaté. Dans **6 %** des clients tirés au hasard, la virgule du panier est mal placée : le panier est **multiplié par 10** (54 € devient 540 €). Nous gardons la version propre (`df`) et fabriquons une copie contaminée (`dfc`).

```python
rng = np.random.default_rng(77)
dfc = df.copy()
cible = rng.choice(len(df), size=int(0.06 * len(df)), replace=False)       # 6 % de clients touchés
dfc.loc[cible, "panier_moyen"] = dfc.loc[cible, "panier_moyen"] * 10
dfc["log_panier"] = np.log(dfc["panier_moyen"])
contamine = np.zeros(len(df), dtype=bool); contamine[cible] = True
print(len(cible), "paniers corrompus sur", len(df), f"({contamine.mean():.1%})")

m_mco_c = smf.ols("log_panier ~ a + C(canal)", data=dfc).fit()
rlm_c = smf.rlm("log_panier ~ a + C(canal)", data=dfc, M=sm.robust.norms.HuberT(t=1.345)).fit()
tab = pd.DataFrame({"MCO données propres": m_propre.params, "MCO contaminé": m_mco_c.params, "Huber contaminé": rlm_c.params})
tab_se = pd.DataFrame({"MCO données propres": m_propre.bse, "MCO contaminé": m_mco_c.bse, "Huber contaminé": rlm_c.bse})
print("Coefficients :"); print(tab.round(4).to_string())
print("\nErreurs standard :"); print(tab_se.round(4).to_string())
print(f"\nécart-type résiduel : MCO propre = {np.sqrt(m_propre.scale):.3f} | MCO contaminé = {np.sqrt(m_mco_c.scale):.3f} | échelle robuste de Huber = {rlm_c.scale:.3f}")
print(f"panier médian prédit pour un client Boutique de 36 ans : propre = {np.exp(m_propre.params['Intercept']):.1f} € | MCO contaminé = {np.exp(m_mco_c.params['Intercept']):.1f} € | Huber contaminé = {np.exp(rlm_c.params['Intercept']):.1f} €")
poids = rlm_c.weights
print(f"poids de Huber moyen : clients corrompus = {poids[contamine].mean():.2f} | clients intacts = {poids[~contamine].mean():.2f}")
```
<!--sortie-->
```text
104 paniers corrompus sur 1740 (6.0%)
Coefficients :
                       MCO données propres  MCO contaminé  Huber contaminé
Intercept                           4.2206         4.3898           4.2628
C(canal)[T.Site]                   -0.1571        -0.1853          -0.1573
C(canal)[T.Réseaux]              -0.3368        -0.3919          -0.3527
a                                   0.0092         0.0088           0.0091

Erreurs standard :
                       MCO données propres  MCO contaminé  Huber contaminé
Intercept                           0.0175         0.0314           0.0201
C(canal)[T.Site]                    0.0231         0.0414           0.0265
C(canal)[T.Réseaux]               0.0225         0.0403           0.0258
a                                   0.0008         0.0015           0.0010

écart-type résiduel : MCO propre = 0.370 | MCO contaminé = 0.665 | échelle robuste de Huber = 0.402
panier médian prédit pour un client Boutique de 36 ans : propre = 68.1 € | MCO contaminé = 80.6 € | Huber contaminé = 71.0 €
poids de Huber moyen : clients corrompus = 0.24 | clients intacts = 0.97
```

Les conséquences pour les moindres carrés sont de deux types. (1) Un **biais** : la constante est tirée vers le haut (de 4,22 à 4,39, soit +18 % sur le panier médian prédit : 80,6 € au lieu de 68,1 € ; en moyenne on attendrait $0{,}06\times\ln10\approx0{,}14$, le reste vient de la répartition aléatoire des erreurs entre les canaux), les effets du Site et d'Réseaux sont gonflés, et les erreurs standard grossissent ; (2) surtout, l'**écart-type résiduel** passe de 0,37 à 0,665 : les moindres carrés *attribuent à tort un bruit énorme* à tout le modèle, donc des intervalles de confiance beaucoup trop larges, des prévisions moins précises, et des effets réels (le canal, l'âge) qui deviennent plus difficiles à détecter. Huber, lui, **donne un poids faible aux clients corrompus** (0,24 en moyenne, contre 0,97 aux clients intacts) : sa constante (4,26) et son effet d'Réseaux (−0,353) restent proches de ceux des données propres (4,22 et −0,337), alors que ceux des moindres carrés dérivent (4,39 et −0,392) ; son échelle (0,40) est proche de l'écart-type propre (0,37) alors que celui des moindres carrés double (0,665). Ses erreurs standard (0,020 pour la constante) sont proches de celles des données propres (0,017) et loin de celles des moindres carrés contaminés (0,031).

Visualisons-le sur un modèle simple (le log-panier selon l'âge seul, pour pouvoir tracer les droites) :

```python
fig, ax = plt.subplots(figsize=(7.4, 4.6))
ax.scatter(dfc.loc[~contamine, "age"], dfc.loc[~contamine, "log_panier"], s=7, color=GRIS, alpha=0.5, label="paniers corrects")
ax.scatter(dfc.loc[contamine, "age"], dfc.loc[contamine, "log_panier"], s=14, color=ROUGE, alpha=0.8, label="paniers corrompus (× 10)")
s1 = smf.ols("log_panier ~ a", data=df).fit()
s2 = smf.ols("log_panier ~ a", data=dfc).fit()
s3 = smf.rlm("log_panier ~ a", data=dfc, M=sm.robust.norms.HuberT(t=1.345)).fit()
xa = np.linspace(18, 75, 50)
for m, col, nom, ls in [(s1, ENCRE, "MCO, données propres", "-"), (s2, ORANGE, "MCO, données contaminées", "-"), (s3, BLEU, "Huber, données contaminées", "--")]:
    ax.plot(xa, m.params["Intercept"] + m.params["a"] * (xa - 36), color=col, lw=2.2, ls=ls, label=nom)
ax.set_xlabel("âge (ans)"); ax.set_ylabel("log du panier moyen")
ax.legend(frameon=False, fontsize=8.5, loc="lower right", ncol=2)
ax.set_ylim(1.5, 7.6)
plt.savefig("figures/ch01-robuste-contamination.png", dpi=200, bbox_inches="tight")
print("pente (MCO propre) =", round(s1.params["a"], 4), "| (MCO contaminé) =", round(s2.params["a"], 4), "| (Huber contaminé) =", round(s3.params["a"], 4))
print("constante (MCO propre) =", round(s1.params["Intercept"], 3), "| (MCO contaminé) =", round(s2.params["Intercept"], 3), "| (Huber contaminé) =", round(s3.params["Intercept"], 3))
```
<!--sortie-->
```text
pente (MCO propre) = 0.009 | (MCO contaminé) = 0.0086 | (Huber contaminé) = 0.0092
constante (MCO propre) = 4.033 | (MCO contaminé) = 4.171 | (Huber contaminé) = 4.07
```

![Nuage du log-panier selon l'âge, avec 6 % de paniers corrompus (rouge, environ 2,3 plus haut). La droite des moindres carrés sur les données contaminées (orange) est décalée vers le haut par rapport à la droite sur données propres (noire) ; la droite de Huber sur les mêmes données contaminées (bleu pointillé) reste beaucoup plus proche de la droite propre.](figures/ch01-robuste-contamination.png)

Les points rouges forment une bande décalée d'environ $\ln10\approx2{,}3$ au-dessus du nuage principal. La droite des moindres carrés (orange) est visiblement tirée vers le haut ; celle de Huber (bleu pointillé) reste beaucoup plus proche de la droite que l'on obtiendrait sans contamination (noire) : la constante passe de 4,03 (données propres) à 4,17 pour les moindres carrés mais seulement à 4,07 pour Huber, et la pente est presque intacte (0,0092 pour Huber, 0,0086 pour les moindres carrés, 0,0090 sans contamination). Huber n'est pas totalement insensible (les points corrompus gardent un petit poids, 0,24 en moyenne), mais l'essentiel du dégât est évité.

### 1.6.4 La limite : les points à fort levier

Les M-estimateurs de Huber protègent contre les **valeurs aberrantes de la réponse** $y$ (les « aberrations verticales »), mais **pas contre les points à fort levier** (valeurs aberrantes des *variables explicatives*, 1.3.4). Leur fonction $\psi$ borne l'influence du résidu, mais pas celle de la position $\mathbf x_i$ : un point très éloigné en $x$ attire la droite, et se retrouve avec un résidu qui n'a pas l'air grand. Faisons une seconde contamination : cette fois, ce sont des **âges** mal saisis. Pour 1 % des clients, l'âge est écrit avec un chiffre de trop (35 devient 350).

```python
rng = np.random.default_rng(78)
dfl = df.copy()
cible_l = rng.choice(len(df), size=int(0.01 * len(df)), replace=False)
dfl.loc[cible_l, "age"] = dfl.loc[cible_l, "age"] * 10
dfl["a"] = dfl["age"] - 36
print(len(cible_l), "âges corrompus ; âge maximal après contamination :", int(dfl["age"].max()), "ans")
m_mco_l = smf.ols("log_panier ~ a + C(canal)", data=dfl).fit()
rlm_l = smf.rlm("log_panier ~ a + C(canal)", data=dfl, M=sm.robust.norms.HuberT(t=1.345)).fit()
print(pd.DataFrame({"MCO propre": m_propre.params, "MCO âges corrompus": m_mco_l.params, "Huber âges corrompus": rlm_l.params}).round(4).to_string())
print(f"coefficient de l'âge : propre = {m_propre.params['a']:.4f} | MCO corrompu = {m_mco_l.params['a']:.4f} | Huber corrompu = {rlm_l.params['a']:.4f}")
print(f"levier maximal : {m_mco_l.get_influence().hat_matrix_diag.max():.3f} (levier moyen = {4/len(dfl):.4f})")
```
<!--sortie-->
```text
17 âges corrompus ; âge maximal après contamination : 640 ans
                       MCO propre  MCO âges corrompus  Huber âges corrompus
Intercept                  4.2206              4.2156                4.2126
C(canal)[T.Site]          -0.1571             -0.1575               -0.1603
C(canal)[T.Réseaux]     -0.3368             -0.3349               -0.3338
a                          0.0092              0.0008                0.0009
coefficient de l'âge : propre = 0.0092 | MCO corrompu = 0.0008 | Huber corrompu = 0.0009
levier maximal : 0.126 (levier moyen = 0.0023)
```

Les deux méthodes sont mises en échec : le coefficient de l'âge est **écrasé vers 0** (par les moindres carrés comme par Huber), parce que ces 17 clients, supposés avoir jusqu'à 640 ans, ont un panier ordinaire : sur ces points, la droite « âge ↗, panier ↗ » est contredite, et leur très fort levier leur donne le pouvoir de l'aplatir. Les estimateurs robustes **à fort levier** (MM-estimateurs, moindres carrés tronqués) existent, mais dans ce cas la bonne réponse est plus simple : **vérifier les données**. Un âge de 350 ans est **impossible** : une règle de validation élémentaire (`age <= 100`) l'élimine.

> ⚠️ **Robuste ne veut pas dire infaillible.** (1) Une méthode robuste ne remplace pas la **vérification des données** : un âge de 350 ans doit être détecté et corrigé, pas « absorbé » par un estimateur. (2) Les méthodes robustes protègent contre un certain **type** d'anomalie (ici, les erreurs sur $y$) et pas contre tous. (3) Elles sont moins efficaces que les moindres carrés si les données sont parfaitement propres (un peu : 5 % pour Huber). (4) Leurs erreurs standard demandent des formules spécifiques ; `RLM` les fournit, mais leurs propriétés sont asymptotiques. (5) Si les « aberrations » sont **réelles** (quelques très gros clients), il ne faut pas les cacher : il faut **les étudier**, car elles peuvent être ce qu'il y a de plus important commercialement.

### 1.6.5 Une autre voie : la régression quantile

Une approche voisine consiste à modéliser non plus la **moyenne** conditionnelle mais la **médiane** conditionnelle, en minimisant la **somme des valeurs absolues** des résidus (perte $\rho(e)=|e|$, dont l'influence $\psi=\operatorname{signe}(e)$ est bornée) : c'est la **régression médiane** (LAD, *least absolute deviations*), robuste aux aberrations verticales. Elle se généralise à un **quantile** quelconque $\tau\in(0,1)$ avec la perte asymétrique $\rho_\tau(e)=e\,(\tau-\mathbb 1_{e<0})$ : on modélise alors le $\tau$-ième quantile de la réponse, ce qui décrit **toute la distribution** et non son seul centre.

Voyons-le sur les paniers. Dans le modèle en **euros**, que dit le canal Réseaux sur les paniers faibles, moyens et élevés ? Et dans le modèle en **log** ?

```python
taus = [0.1, 0.25, 0.5, 0.75, 0.9]
res_niveau, res_log = [], []
for tau in taus:
    qn = smf.quantreg("panier_moyen ~ a + C(canal)", data=df).fit(q=tau)
    ql = smf.quantreg("log_panier ~ a + C(canal)", data=df).fit(q=tau)
    res_niveau.append((tau, qn.params["C(canal)[T.Réseaux]"], *qn.conf_int().loc["C(canal)[T.Réseaux]"]))
    res_log.append((tau, ql.params["C(canal)[T.Réseaux]"], *ql.conf_int().loc["C(canal)[T.Réseaux]"]))
rn = pd.DataFrame(res_niveau, columns=["tau", "coef", "bas", "haut"]).set_index("tau")
rl = pd.DataFrame(res_log, columns=["tau", "coef", "bas", "haut"]).set_index("tau")
mco_n = smf.ols("panier_moyen ~ a + C(canal)", data=df).fit()
print("Effet d'Réseaux (par rapport à la Boutique) sur le panier en €, par quantile :")
print(rn.round(2).to_string())
print(f"(MCO, effet sur la moyenne : {mco_n.params['C(canal)[T.Réseaux]']:.2f} €)")
print("\nEffet d'Réseaux sur le log du panier, par quantile :")
print(rl.round(3).to_string())
print(f"(MCO, effet sur la moyenne du log : {m_propre.params['C(canal)[T.Réseaux]']:.3f})")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.0))
for ax, r, ref, titre, yl in [(ax1, rn, mco_n.params["C(canal)[T.Réseaux]"], "Panier en €", "effet d'Réseaux (€)"),
                              (ax2, rl, m_propre.params["C(canal)[T.Réseaux]"], "Log du panier", "effet d'Réseaux (log)")]:
    ax.fill_between(r.index, r["bas"], r["haut"], color=BLEU, alpha=0.2)
    ax.plot(r.index, r["coef"], "o-", color=BLEU, lw=2, label="régression quantile")
    ax.axhline(ref, color=ORANGE, lw=1.8, ls="--", label="moindres carrés (moyenne)")
    ax.set_xlabel("quantile τ du panier (0,1 = petits paniers ; 0,9 = grands paniers)"); ax.set_ylabel(yl); ax.set_title(titre, fontsize=10.5)
ax1.legend(frameon=False, fontsize=8.5, loc="lower left")
plt.tight_layout()
plt.savefig("figures/ch01-regression-quantile.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
Effet d'Réseaux (par rapport à la Boutique) sur le panier en €, par quantile :
       coef    bas   haut
tau                      
0.10 -13.50 -16.18 -10.82
0.25 -14.40 -16.92 -11.89
0.50 -18.27 -21.44 -15.09
0.75 -24.22 -28.42 -20.02
0.90 -33.87 -40.70 -27.04
(MCO, effet sur la moyenne : -20.81 €)

Effet d'Réseaux sur le log du panier, par quantile :
       coef    bas   haut
tau                      
0.10 -0.373 -0.448 -0.298
0.25 -0.331 -0.387 -0.275
0.50 -0.310 -0.369 -0.252
0.75 -0.339 -0.400 -0.278
0.90 -0.372 -0.446 -0.299
(MCO, effet sur la moyenne du log : -0.337)
figure enregistrée
```

![Effet du canal Réseaux selon le quantile du panier. À gauche (en euros) : l'effet est faible pour les petits paniers et de plus en plus négatif pour les grands. À droite (en log) : l'effet est à peu près constant, autour de −0,34, avec une bande de confiance qui contient la valeur des moindres carrés. Les bandes bleues sont les intervalles de confiance à 95 %.](figures/ch01-regression-quantile.png)

Lisons la figure. En **euros** (à gauche), l'effet d'Réseaux n'est pas le même sur les petits et les grands paniers : le déficit est de 13,5 € pour les petits paniers (quantile 10 %) et de 33,9 € pour les gros (quantile 90 %), à comparer aux 20,8 € de l'effet moyen des moindres carrés. La moyenne (moindres carrés) ne voit qu'un effet moyen. En **log** (à droite), l'effet varie peu le long de la distribution (de −0,31 à −0,37, des intervalles de confiance qui se chevauchent largement et contiennent la valeur des moindres carrés, −0,337) : on peut le considérer comme **constant**. Les deux lectures sont **cohérentes** : un effet **multiplicatif** constant ($-29$ % du panier, quel que soit son niveau) se traduit en euros par un effet **proportionnel** au niveau (un gros panier perd plus de euros qu'un petit). C'est exactement ce que le modèle simulé a programmé, et c'est une raison de plus de préférer le log : l'effet s'y résume par un **seul nombre**.

> ✅ **À retenir (1.6).**
> - Les moindres carrés ont un **point de rupture de 0 %** : une seule aberration peut les fausser, car leur fonction d'influence $\psi(e)=e$ n'est pas bornée.
> - Les **M-estimateurs** (Huber, Tukey) minimisent $\sum\rho(e_i/s)$ avec un $\rho$ à influence bornée ; on les calcule par **moindres carrés repondérés** (IRLS), avec une échelle robuste (MAD). Huber avec $c=1{,}345$ garde 95 % d'efficacité si les erreurs sont normales.
> - Sur nos données contaminées, Huber **ignore presque** les paniers corrompus ; les moindres carrés sont biaisés et croient à un bruit énorme.
> - Les M-estimateurs ne protègent **pas** contre les points à **fort levier** : il faut vérifier les données d'abord.
> - La **régression quantile** (médiane ou autres quantiles) est robuste elle aussi, et décrit l'effet d'une variable sur **toute la distribution**.
