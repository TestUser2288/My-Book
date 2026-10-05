## 5.4 Modèles de durée paramétriques

> 💡 **Intuition.** Le modèle de Cox est élégant parce qu'il ne dit rien sur la forme du risque de base. Mais ce silence a un prix : on ne peut rien dire **au-delà** de ce qu'on a observé. La gérante voudrait savoir combien un client rapporte *au total*, y compris pendant les années à venir que personne n'a encore vécues. Pour extrapoler, il faut **parier sur une forme** de loi. Les modèles paramétriques font ce pari : ils décrivent la durée par une loi connue (exponentielle, Weibull, log-normale…) dont les paramètres dépendent des caractéristiques du client. En échange du pari, on obtient des courbes lisses, des durées moyennes, des extrapolations, et des estimations plus précises *si la forme est bonne*.

### 5.4.1 Le modèle à temps de vie accéléré

Les modèles paramétriques s'écrivent le plus naturellement sur le **logarithme de la durée** (le logarithme transforme une quantité positive et asymétrique en une quantité symétrique, comme pour la régression linéaire du début du volume) :
$$\boxed{\ \ln T=\mu(x)+\sigma\,W,\qquad \mu(x)=x^\top\gamma\ }$$
où $W$ est une variable aléatoire de loi **fixée** (le « bruit ») et $\sigma>0$ un paramètre d'**échelle**. C'est le **modèle à temps de vie accéléré** (en anglais *accelerated failure time*, AFT). Le choix de la loi de $W$ détermine la famille :

| Loi de $W$ | Loi de $T$ | $S(t\mid x)$, avec $z=(\ln t-\mu)/\sigma$ | Forme du risque $h(t)$ |
|---|---|---|---|
| $\sigma=1$, valeur extrême | **exponentielle** | $\exp(-e^{z})$ | constant |
| valeur extrême (Gumbel du minimum) | **Weibull** | $\exp(-e^{z})$ | monotone : croissant si $\sigma<1$, décroissant si $\sigma>1$ |
| normale | **log-normale** | $1-\Phi(z)$ | croît puis décroît |
| logistique | **log-logistique** | $1/(1+e^{z})$ | croît puis décroît (ou décroît seulement si $\sigma\ge1$) |

(On reconnaît la forme de Weibull du 5.1.3 avec la **forme** $k=1/\sigma$ et l'**échelle** $e^{\mu}$.)

**Interprétation : l'« accélération ».** Écrivons $T=e^{x^\top\gamma}\,T_0$, où $T_0=e^{\sigma W}$ est la durée d'un client « de référence » ($x=0$). Un client de caractéristiques $x$ vit **$e^{x^\top\gamma}$ fois plus longtemps** : les covariables **accélèrent ou ralentissent l'horloge** :
$$S(t\mid x)=S_0\big(t\,e^{-x^\top\gamma}\big).$$
Le facteur $e^{\gamma_j}$ est le **facteur d'accélération** : s'il vaut 1,37 pour l'offre de bienvenue, tout se passe comme si le temps s'écoulait 1,37 fois plus lentement pour un client qui l'a reçue ; sa durée **médiane** (et sa durée moyenne) est 37 % plus longue. C'est un langage plus parlant que le rapport de risques : *« l'offre rallonge la relation de 37 % »*.

> ⚠️ **Attention au sens des coefficients.** Dans un modèle AFT, un coefficient **positif** signifie une durée **plus longue** (protecteur). Dans le modèle de Cox, un coefficient **positif** signifie un risque **plus élevé** (néfaste). Les signes sont opposés ! Si l'on compare ce que fait Cox et ce que fait un AFT, il faut convertir (ce que nous ferons au 5.4.2).

### 5.4.2 La Weibull : à la fois « risques proportionnels » et « temps accéléré »

Parmi toutes les lois, la Weibull a une propriété unique : elle appartient aux **deux** familles. Montrons-le. Avec $k=1/\sigma$ et $\lambda(x)=e^{x^\top\gamma}$,
$$S(t\mid x)=\exp\!\Big[-\Big(\frac{t}{\lambda(x)}\Big)^{k}\Big],\qquad H(t\mid x)=\Big(\frac{t}{\lambda(x)}\Big)^{k}=t^{k}\,e^{-k\,x^\top\gamma}.$$
Dérivons pour obtenir le risque :
$$h(t\mid x)=k\,t^{k-1}\,e^{-k\,x^\top\gamma}=\underbrace{k\,t^{k-1}}_{h_0(t)}\ \cdot\ e^{x^\top\beta}\qquad\text{avec}\quad\boxed{\ \beta=-k\,\gamma=-\gamma/\sigma\ }.$$
C'est exactement la forme du modèle de Cox, avec un risque de base **imposé** $h_0(t)=kt^{k-1}$. Les coefficients des deux modèles se déduisent l'un de l'autre. C'est un excellent test de cohérence : *si les données sont vraiment Weibull, un modèle de Cox et un AFT Weibull doivent donner les mêmes effets*.

### 5.4.3 Le maximum de vraisemblance, écrit à la main

La vraisemblance avec censure (5.1.5) s'écrit pour un AFT, avec $z_i=(\ln y_i-x_i^\top\gamma)/\sigma$, $f_W$ la densité et $S_W$ la survie de $W$ :
$$\ell(\gamma,\sigma)=\sum_i\Big[\delta_i\big(\ln f_W(z_i)-\ln\sigma-\ln y_i\big)+(1-\delta_i)\ln S_W(z_i)\Big].$$
(La densité de $T=e^{\mu+\sigma W}$ est $f_W(z)/(\sigma t)$ : c'est le changement de variable habituel.) Pour la Weibull, $\ln f_W(z)=z-e^z$ et $\ln S_W(z)=-e^z$ ; pour la log-normale, $f_W=\varphi$ et $S_W=1-\Phi$ ; pour la log-logistique, $\ln f_W(z)=z-2\ln(1+e^z)$ et $\ln S_W(z)=-\ln(1+e^z)$. Le code suivant écrit ces trois vraisemblances, les maximise numériquement et calcule les erreurs standard par la **hessienne** numérique de $-\ell$ (l'inverse de l'information, comme au volume I, section 3.2).

```python
import numpy as np
import pandas as pd
from math import gamma as Gamma
from scipy import stats
from scipy.optimize import minimize
from statsmodels.tools.numdiff import approx_hess3

c = pd.read_csv("donnees/clients.csv")
y, d = c["duree_mois"].to_numpy(), c["churn"].to_numpy()
X = pd.get_dummies(c[["offre_bienvenue", "age", "canal_acquisition"]], drop_first=True, dtype=float)
Xc = np.column_stack([np.ones(len(c)), X.to_numpy()])            # première colonne : constante
noms = ["(constante)"] + list(X.columns)

def log_vrais_aft(theta, y, d, X, loi):
    """theta = (gamma_0..gamma_p, ln sigma). Retourne la log-vraisemblance (avec censure à droite)."""
    gam, sigma = theta[:-1], np.exp(theta[-1])
    z = (np.log(y) - X @ gam) / sigma
    if loi == "weibull":
        lf, ls = z - np.exp(z), -np.exp(z)
    elif loi == "lognormale":
        lf, ls = stats.norm.logpdf(z), stats.norm.logsf(z)
    elif loi == "loglogistique":
        lf, ls = z - 2 * np.log1p(np.exp(z)), -np.log1p(np.exp(z))
    return np.sum(d * (lf - np.log(sigma) - np.log(y)) + (1 - d) * ls)

def ajuster(loi, y, d, X, sigma_fixe=None):
    """Maximum de vraisemblance. sigma_fixe=1 donne l'exponentielle (Weibull avec sigma = 1)."""
    p = X.shape[1]
    if sigma_fixe is None:
        f = lambda t: -log_vrais_aft(t, y, d, X, loi)
        t0 = np.concatenate([[np.log(y.mean())], np.zeros(p - 1), [0.0]])
    else:
        f = lambda t: -log_vrais_aft(np.concatenate([t, [np.log(sigma_fixe)]]), y, d, X, loi)
        t0 = np.concatenate([[np.log(y.mean())], np.zeros(p - 1)])
    r = minimize(f, t0, method="Nelder-Mead", options={"xatol": 1e-9, "fatol": 1e-11, "maxiter": 20000, "maxfev": 20000})
    r = minimize(f, r.x, method="BFGS")                                   # affinage
    H = approx_hess3(r.x, f)
    return {"theta": r.x, "cov": np.linalg.inv(H), "ll": -r.fun, "k": len(r.x)}

ajustements = {loi: ajuster(loi, y, d, Xc) for loi in ("weibull", "lognormale", "loglogistique")}
ajustements["exponentielle"] = ajuster("weibull", y, d, Xc, sigma_fixe=1.0)

wb = ajustements["weibull"]
se = np.sqrt(np.diag(wb["cov"]))
tab = pd.DataFrame({"gamma": wb["theta"][:-1], "ET": se[:-1], "facteur d'accélération e^gamma": np.exp(wb["theta"][:-1])}, index=noms)
print(tab.round(4).to_string())
sigma = np.exp(wb["theta"][-1])
print(f"\nsigma = {sigma:.4f}  ->  forme k = 1/sigma = {1 / sigma:.4f}   (ET de ln sigma : {se[-1]:.4f})")
print(f"log-vraisemblance = {wb['ll']:.3f}")
```
<!--sortie-->
```text
                              gamma      ET  facteur d'accélération e^gamma
(constante)                  3.5257  0.0970                         33.9765
offre_bienvenue              0.3132  0.0489                          1.3678
age                          0.0102  0.0023                          1.0102
canal_acquisition_Instagram -0.4799  0.0636                          0.6188
canal_acquisition_Site      -0.2452  0.0671                          0.7825

sigma = 0.7563  ->  forme k = 1/sigma = 1.3223   (ET de ln sigma : 0.0253)
log-vraisemblance = -4657.378
```

Comparons avec **R** (`survreg`, la référence) et avec `lifelines` :

```r
w_r <- survreg(Surv(duree_mois, churn) ~ offre_bienvenue + age + canal_acquisition, data = clients, dist = "weibull")
print(summary(w_r))
```
<!--sortie-->
```text

Call:
survreg(formula = Surv(duree_mois, churn) ~ offre_bienvenue + 
    age + canal_acquisition, data = clients, dist = "weibull")
                             Value Std. Error      z       p
(Intercept)                 3.5257     0.0970  36.34 < 2e-16
offre_bienvenue             0.3132     0.0489   6.40 1.5e-10
age                         0.0102     0.0023   4.43 9.3e-06
canal_acquisitionInstagram -0.4799     0.0636  -7.55 4.4e-14
canal_acquisitionSite      -0.2452     0.0671  -3.66 0.00026
Log(scale)                 -0.2794     0.0253 -11.04 < 2e-16

Scale= 0.756 

Weibull distribution
Loglik(model)= -4657.4   Loglik(intercept only)= -4714.4
	Chisq= 114.02 on 4 degrees of freedom, p= 1e-23 
Number of Newton-Raphson Iterations: 6 
n= 2000 
```

```python
from lifelines import WeibullAFTFitter

df_ll = pd.concat([c[["duree_mois", "churn"]], X], axis=1)
ll_w = WeibullAFTFitter().fit(df_ll, "duree_mois", "churn")
print("lifelines : coefficients de lambda_ :", ll_w.params_["lambda_"].round(4).to_dict())
print(f"lifelines : rho = ln k = {ll_w.params_[('rho_', 'Intercept')]:.4f} (à la main : -ln sigma = {-wb['theta'][-1]:.4f}) ; log-vraisemblance {ll_w.log_likelihood_:.3f}")
```
<!--sortie-->
```text
lifelines : coefficients de lambda_ : {'age': 0.0102, 'canal_acquisition_Instagram': -0.4799, 'canal_acquisition_Site': -0.2452, 'offre_bienvenue': 0.3132, 'Intercept': 3.5257}
lifelines : rho = ln k = 0.2794 (à la main : -ln sigma = 0.2794) ; log-vraisemblance -4657.378
```

Les trois sources donnent les mêmes coefficients, la même échelle et la même log-vraisemblance. Lecture :

- **Offre de bienvenue** : facteur d'accélération $e^{0{,}313}\approx1{,}37$ : la durée de vie d'un client qui l'a reçue est **37 % plus longue** (à âge et canal égaux).
- **Canal** : par rapport à la boutique, un client arrivé par Réseaux a une durée de vie **38 % plus courte** ($e^{-0{,}48}\approx0{,}62$) et un client arrivé par le site, **22 % plus courte** ($e^{-0{,}245}\approx0{,}78$).
- **Âge** : chaque année en plus allonge la durée d'environ 1 %.
- **Forme** : $k\approx1{,}32>1$ : le risque **augmente** avec l'ancienneté, ce qui confirme ce que montrait la comparaison de Kaplan-Meier et de l'exponentielle (5.2.2).

**La vérification croisée avec Cox.** Convertissons ces coefficients AFT en coefficients de risques par $\beta=-\gamma/\sigma$ et comparons au modèle de Cox de la section 5.3 :

```python
beta_ph = -wb["theta"][1:-1] / sigma
cox_coef = np.array([-0.40612, -0.01363, 0.63508, 0.32580])          # section 5.3.3 (Breslow)
print(pd.DataFrame({"Weibull converti (-gamma/sigma)": beta_ph, "Cox (5.3.3)": cox_coef}, index=noms[1:]).round(4).to_string())
```
<!--sortie-->
```text
                             Weibull converti (-gamma/sigma)  Cox (5.3.3)
offre_bienvenue                                      -0.4141      -0.4061
age                                                  -0.0135      -0.0136
canal_acquisition_Instagram                           0.6346       0.6351
canal_acquisition_Site                                0.3242       0.3258
```

Les deux séries sont presque identiques : les données sont bien compatibles avec une Weibull. Les erreurs standard sont, elles aussi, voisines (environ 0,065 pour l'offre dans les deux cas, en convertissant celle de l'AFT par $0{,}0489/0{,}756$). Quand la forme paramétrique est bonne, on pourrait espérer un gain de précision par rapport à Cox ; ici il est négligeable : avec 977 départs, le risque de base est déjà estimé très précisément, et Cox ne perd presque rien.

### 5.4.4 Choisir entre plusieurs lois

Tous ces modèles ont le même nombre de paramètres sauf l'exponentielle (un de moins) ; on peut donc les comparer par la **vraisemblance** et le **critère d'Akaike** (AIC $=2k-2\ell$, voir la section 1.4 de ce volume ; plus petit = meilleur).

```python
lignes = []
for loi, r in ajustements.items():
    lignes.append({"loi": loi, "paramètres": r["k"], "log-vraisemblance": round(r["ll"], 2), "AIC": round(2 * r["k"] - 2 * r["ll"], 2)})
print(pd.DataFrame(lignes).sort_values("AIC").to_string(index=False))

# Test du rapport de vraisemblance : exponentielle (sigma = 1) contre Weibull
lr = 2 * (ajustements["weibull"]["ll"] - ajustements["exponentielle"]["ll"])
print(f"\nexponentielle contre Weibull : chi2 = {lr:.1f} (1 ddl), p = {stats.chi2.sf(lr, 1):.1e}")
```
<!--sortie-->
```text
          loi  paramètres  log-vraisemblance     AIC
      weibull           6           -4657.38 9326.76
loglogistique           6           -4663.73 9339.45
   lognormale           6           -4697.20 9406.40
exponentielle           5           -4710.58 9431.17

exponentielle contre Weibull : chi2 = 106.4 (1 ddl), p = 6.0e-25
```

```r
for (loi in c("weibull", "lognormal", "loglogistic", "exponential")) {
  f <- survreg(Surv(duree_mois, churn) ~ offre_bienvenue + age + canal_acquisition, data = clients, dist = loi)
  cat(sprintf("%-12s log-vraisemblance = %.3f   AIC = %.2f\n", loi, f$loglik[2], AIC(f)))
}
```
<!--sortie-->
```text
weibull      log-vraisemblance = -4657.378   AIC = 9326.76
lognormal    log-vraisemblance = -4697.200   AIC = 9406.40
loglogistic  log-vraisemblance = -4663.725   AIC = 9339.45
exponential  log-vraisemblance = -4710.583   AIC = 9431.17
```

La **Weibull** est nettement la meilleure ; la log-logistique arrive deuxième (13 points d'AIC derrière), la log-normale troisième, l'exponentielle dernière. Le test du rapport de vraisemblance rejette l'exponentielle de façon écrasante : le risque n'est pas constant. Les valeurs coïncident avec celles de R.

Un AIC compare des modèles **entre eux** ; il ne dit pas si le meilleur est *bon*. Pour juger l'adéquation, on utilise les **résidus de Cox-Snell**.

> 📐 **Résidus de Cox-Snell.** Si $T$ a pour fonction de survie $S$, alors $S(T)$ suit une loi uniforme (transformée intégrale de probabilité) et donc $H(T)=-\ln S(T)$ suit une loi **exponentielle de paramètre 1**. Pour un modèle correct, les résidus $r_i=\hat H(y_i\mid x_i)$ se comportent comme un échantillon **censuré** de loi exponentielle(1). On estime donc le risque cumulé de ces résidus par Kaplan-Meier (on garde la censure, $\delta_i$) : le graphique de ce risque cumulé contre $r$ doit suivre la **diagonale**.

Superposons la comparaison globale (survie marginale prédite par chaque modèle, contre Kaplan-Meier) et les résidus de Cox-Snell, pour la Weibull et pour l'exponentielle :

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"

def survie_aft(t, mu, sigma, loi):
    z = (np.log(t) - mu) / sigma
    return {"weibull": lambda: np.exp(-np.exp(z)), "lognormale": lambda: stats.norm.sf(z), "loglogistique": lambda: 1 / (1 + np.exp(z))}[loi]()

def survie_marginale(t_grille, theta, loi, Xmat):
    mu, sg = Xmat @ theta[:-1], np.exp(theta[-1])
    return np.array([survie_aft(t, mu, sg, loi).mean() for t in t_grille])

def km_simple(t, dd):
    tj = np.unique(t[dd == 1])
    ys, ev = np.sort(t), np.sort(t[dd == 1])
    n_ = len(t) - np.searchsorted(ys, tj, side="left")
    dj_ = np.searchsorted(ev, tj, side="right") - np.searchsorted(ev, tj, side="left")
    return tj, np.cumprod(1 - dj_ / n_)

grille = np.linspace(0.5, 84, 150)
tj_km, S_km = km_simple(y, d)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
ax1.step(np.concatenate([[0], tj_km]), np.concatenate([[1], S_km]), where="post", color="#52514e", lw=2.2, label="Kaplan-Meier")
for loi, couleur, nom in [("weibull", ORANGE, "Weibull"), ("loglogistique", AQUA, "log-logistique"),
                          ("lognormale", VIOLET, "log-normale")]:
    ax1.plot(grille, survie_marginale(grille, ajustements[loi]["theta"], loi, Xc), color=couleur, lw=1.6, label=nom)
th_e = np.concatenate([ajustements["exponentielle"]["theta"], [0.0]])
ax1.plot(grille, survie_marginale(grille, th_e, "weibull", Xc), color=BLEU, lw=1.6, ls="--", label="exponentielle")
ax1.set_xlabel("mois depuis l'inscription")
ax1.set_ylabel("proportion de clients encore là")
ax1.set_title("Survie prédite (moyenne sur les 2 000 clients)")
ax1.legend(frameon=False, fontsize=9)
ax1.set_ylim(0, 1.02)

# Résidus de Cox-Snell
for loi, th, couleur, nom in [("weibull", ajustements["weibull"]["theta"], ORANGE, "Weibull"), ("weibull", th_e, BLEU, "exponentielle")]:
    mu, sg = Xc @ th[:-1], np.exp(th[-1])
    r = -np.log(survie_aft(y, mu, sg, loi))                  # résidus de Cox-Snell : H(y_i | x_i)
    tj_r, S_r = km_simple(r, d)
    ax2.step(tj_r, -np.log(S_r), where="post", color=couleur, lw=1.8, label=nom)
ax2.plot([0, 3], [0, 3], color="#898781", lw=1, ls=":")
ax2.set_xlim(0, 2.6)
ax2.set_ylim(0, 2.6)
ax2.set_xlabel("résidu de Cox-Snell r")
ax2.set_ylabel("risque cumulé estimé des résidus")
ax2.set_title("Adéquation : suivre la diagonale")
ax2.legend(frameon=False, fontsize=9, loc="upper left")
plt.tight_layout()
plt.savefig("figures/ch05-param-ajustement.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![À gauche : survie de Kaplan-Meier des 2 000 clients et survie moyenne prédite par quatre modèles paramétriques. À droite : résidus de Cox-Snell du modèle de Weibull et du modèle exponentiel avec covariables ; le bon modèle suit la diagonale.](figures/ch05-param-ajustement.png)

À gauche, les quatre modèles sont presque indiscernables de Kaplan-Meier jusqu'à 35 mois environ, sauf l'exponentielle, qui prévoit trop de départs au tout début (le schéma de la section 5.2.2). Au-delà de 40 mois, les courbes se séparent : la Weibull suit Kaplan-Meier jusqu'à 55 mois environ, puis passe **un peu en dessous** ; les trois autres lois restent **au-dessus**. À droite, les résidus de Cox-Snell du modèle de Weibull suivent la diagonale jusqu'à $r\approx1{,}5$ (au-delà, quelques résidus seulement : le tracé est instable), tandis que ceux du modèle exponentiel s'en écartent dès que $r$ dépasse environ 0,7.

### 5.4.5 Extrapoler et chiffrer : la valeur vie client

La gérante veut savoir **ce que rapporte un client en moyenne sur toute sa vie**. Pour cela, il lui faut la survie *au-delà* de la fenêtre observée (84 mois au plus). Seul un modèle paramétrique peut fournir cette extrapolation.

La **durée de vie moyenne** d'un client de profil $x$ dans un modèle de Weibull est $E[T\mid x]=\lambda(x)\,\Gamma(1+1/k)$ (section 5.1.3). La **valeur vie client** actualisée (en anglais *customer lifetime value*, CLV) combine cette survie avec un revenu :
$$\mathrm{CLV}(x)=m\sum_{t=0}^{T_{\max}}\frac{S(t\mid x)}{(1+r)^{t}}$$
où $m$ est la **marge mensuelle** par client encore actif, $r$ le taux d'actualisation mensuel (un euro dans un an vaut moins qu'un euro aujourd'hui), et $S(t\mid x)$ la probabilité d'être encore client au mois $t$.

> 🧭 **Des hypothèses, pas des données.** Nous n'avons dans nos fichiers **ni marge ni coût**. Les trois chiffres ci-dessous sont des hypothèses que la gérante devrait remplacer par les siens : une marge de **6 € par mois** et par client actif, un taux d'actualisation de **1 % par mois** (environ 13 % par an) et un horizon de 20 ans (240 mois). Le but est de montrer la **mécanique** du calcul, pas de chiffrer vraiment la boutique.

```python
m_mensuelle, taux, horizon = 6.0, 0.01, 240
mois = np.arange(0, horizon)
k_hat, th = 1 / sigma, wb["theta"]
lam = np.exp(Xc @ th[:-1])                                         # échelle e^{x gamma} de chaque client

def S_groupe(masque):
    """Survie moyenne du groupe, d'après le modèle de Weibull ajusté, mois par mois."""
    return np.array([np.mean(np.exp(-(t / lam[masque]) ** k_hat)) for t in mois])

groupes = {"tous les clients": np.ones(len(c), bool),
           "sans offre": (c["offre_bienvenue"] == 0).to_numpy(), "avec offre": (c["offre_bienvenue"] == 1).to_numpy(),
           "Boutique": (c["canal_acquisition"] == "Boutique").to_numpy(), "Site": (c["canal_acquisition"] == "Site").to_numpy(),
           "Réseaux": (c["canal_acquisition"] == "Réseaux").to_numpy()}
lignes = []
for nom, masque in groupes.items():
    S = S_groupe(masque)
    clv = m_mensuelle * np.sum(S / (1 + taux) ** mois)
    apres_84 = m_mensuelle * np.sum(S[84:] / (1 + taux) ** mois[84:])
    lignes.append({"groupe": nom, "clients": int(masque.sum()), "durée moyenne (mois)": np.mean(lam[masque]) * Gamma(1 + 1 / k_hat),
                   "survie à 36 mois": S[36], "CLV (€)": clv, "part de la CLV après 84 mois (%)": 100 * apres_84 / clv})
print(pd.DataFrame(lignes).round(3).to_string(index=False))
```
<!--sortie-->
```text
          groupe  clients  durée moyenne (mois)  survie à 36 mois  CLV (€)  part de la CLV après 84 mois (%)
tous les clients     2000                41.339             0.453   186.096                             3.741
      sans offre      985                35.167             0.384   165.806                             2.156
      avec offre     1015                47.329             0.521   205.785                             4.981
        Boutique      504                53.159             0.574   223.468                             6.364
            Site      680                42.068             0.471   189.751                             3.545
       Réseaux      816                33.431             0.364   159.967                             1.672
```

Quelques vérifications de bon sens. La survie moyenne à 36 mois du modèle (0,453) retrouve **exactement** la valeur de Kaplan-Meier de la section 5.2 (0,453), ce qui confirme que le modèle colle aux données observées. La durée moyenne d'un client est de **41 mois**, tandis que la durée moyenne *restreinte* à 60 mois de Kaplan-Meier valait 34 mois : l'écart (7 mois) est la part de la vie *au-delà de 60 mois*, que Kaplan-Meier ne peut pas chiffrer et que le modèle extrapole. Et la durée moyenne **exponentielle** de la section 5.1.5 (48 mois) était trop optimiste.

**L'offre de bienvenue en valait-elle la peine ?** Elle augmente la CLV de 166 à 206 € par client, soit un gain de **40 €** d'actualisé. Si l'offre coûte, par hypothèse, 10 € par client, le gain net est de 30 € par client. Comme l'offre est randomisée, cette différence est une estimation de **l'effet causal** de l'offre sur la valeur. Voyons si le résultat dépend des hypothèses :

```python
S0, S1 = S_groupe(groupes["sans offre"]), S_groupe(groupes["avec offre"])
cout_offre = 10.0
print(f"CLV sans offre : {m_mensuelle * np.sum(S0 / (1 + taux) ** mois):.1f} € | avec offre : {m_mensuelle * np.sum(S1 / (1 + taux) ** mois):.1f} €\n")
print("gain net par client (CLV avec offre - CLV sans offre - coût de 10 €), selon les hypothèses :")
resultats = pd.DataFrame(index=[f"taux {100 * r:.1f} %/mois" for r in (0.005, 0.01, 0.02)],
                         columns=[f"marge {m} €/mois" for m in (3, 6, 9)], dtype=float)
for r in (0.005, 0.01, 0.02):
    for m in (3, 6, 9):
        v = (1 + r) ** (-mois)
        resultats.loc[f"taux {100 * r:.1f} %/mois", f"marge {m} €/mois"] = m * np.sum((S1 - S0) * v) - cout_offre
print(resultats.round(1).to_string())
```
<!--sortie-->
```text
CLV sans offre : 165.8 € | avec offre : 205.8 €

gain net par client (CLV avec offre - CLV sans offre - coût de 10 €), selon les hypothèses :
                 marge 3 €/mois  marge 6 €/mois  marge 9 €/mois
taux 0.5 %/mois             16.5             42.9             69.4
taux 1.0 %/mois             10.0             30.0             50.0
taux 2.0 %/mois              2.4             14.7             27.1
```

Le gain net reste **positif dans les neuf cas testés**, mais son ordre de grandeur varie d'un facteur 30 : de 69 € par client (marge de 9 €, actualisation faible) à seulement 2,4 € (marge de 3 €, actualisation de 2 % par mois), c'est-à-dire presque rien. La conclusion « l'offre est rentable » est donc **robuste** ; la conclusion « elle rapporte 30 € par client » ne l'est pas. Voilà exactement le genre d'information utile : on peut dire à la gérante que l'offre ne perd pas d'argent dans ce domaine d'hypothèses, et lui demander sa vraie marge pour chiffrer le gain.

> ⚠️ **Les limites de l'extrapolation.** La CLV dépend de la survie *au-delà* des données, donc de la forme de loi supposée. La dernière colonne du premier tableau chiffre cette dépendance : la part de la valeur située **après 84 mois** n'est que d'environ 4 % pour l'ensemble des clients (6 % pour la boutique), parce que l'**actualisation** écrase les mois lointains et que beaucoup de clients sont déjà partis. La CLV est donc peu sensible à l'extrapolation. Ce n'est pas le cas de la **durée moyenne**, qui n'est pas actualisée : c'est elle qui réclame de l'extrapolation (7 mois de plus que la RMST à 60 mois). Deux lois qui s'ajustent presque aussi bien sur 84 mois peuvent extrapoler très différemment : la figure du 5.4.4 le montre, avec une Weibull qui passe sous Kaplan-Meier à partir de 55 mois et des lois log-logistique et log-normale qui restent au-dessus. Le bon réflexe : refaire le calcul avec une autre loi (log-logistique) et comparer ; et ne jamais interpréter une CLV comme une certitude.

### 5.4.6 Une variable manquante : le service

Nos modèles ne connaissent ni la qualité du service reçu, ni la satisfaction du client. Or l'enquête de satisfaction (`donnees/enquete_satisfaction.csv`) en mesure une partie : les notes `q5` à `q8` portent sur le service et la livraison. Environ 60 % des clients ont répondu. Que se passe-t-il si l'on ajoute leur **note moyenne de service** au modèle de survie, sur les répondants ?

```python
q = pd.read_csv("donnees/enquete_satisfaction.csv")
q["service"] = q[["q5", "q6", "q7", "q8"]].mean(axis=1)
rep = c.merge(q[["id_client", "service"]], on="id_client")
rep["service_std"] = (rep["service"] - rep["service"].mean()) / rep["service"].std()
Xr_base = np.column_stack([np.ones(len(rep)), pd.get_dummies(rep[["offre_bienvenue", "age", "canal_acquisition"]], drop_first=True, dtype=float).to_numpy()])
Xr_serv = np.column_stack([Xr_base, rep["service_std"]])
yr, dr = rep["duree_mois"].to_numpy(), rep["churn"].to_numpy()
sans = ajuster("weibull", yr, dr, Xr_base)
avec = ajuster("weibull", yr, dr, Xr_serv)
se_a = np.sqrt(np.diag(avec["cov"]))
print(f"répondants : {len(rep)}")
print(f"sans le service : log-vraisemblance {sans['ll']:.1f} ; forme k = {1 / np.exp(sans['theta'][-1]):.3f}")
print(f"avec le service : log-vraisemblance {avec['ll']:.1f} ; forme k = {1 / np.exp(avec['theta'][-1]):.3f}")
print(f"coefficient du service (par écart-type de la note) : {avec['theta'][-2]:.3f} (ET {se_a[-2]:.3f}) -> durée x {np.exp(avec['theta'][-2]):.2f}")
lr_s = 2 * (avec["ll"] - sans["ll"])
print(f"rapport de vraisemblance : chi2 = {lr_s:.1f} (1 ddl), p = {stats.chi2.sf(lr_s, 1):.1e}")
```
<!--sortie-->
```text
répondants : 1212
sans le service : log-vraisemblance -2785.8 ; forme k = 1.312
avec le service : log-vraisemblance -2750.2 ; forme k = 1.368
coefficient du service (par écart-type de la note) : 0.262 (ET 0.031) -> durée x 1.30
rapport de vraisemblance : chi2 = 71.2 (1 ddl), p = 3.2e-17
```

Un client dont la note de service est **un écart-type au-dessus de la moyenne** reste en moyenne environ **30 % plus longtemps** (facteur 1,30) : le service compte, et le test du rapport de vraisemblance le confirme. C'est un exemple concret de ce qu'apportent les **variables explicatives pertinentes** (et du travail de construction d'indicateurs de la section 3.2 de ce volume, l'analyse factorielle, pour condenser huit notes en un score de service).

### 5.4.7 Révéler la vérité

Comme les données sont simulées, nous pouvons maintenant comparer nos estimations à la loi qui les a engendrées (documentée en tête de `build/donnees2.py`). Les durées sont de loi de **Weibull de forme 1,35**, avec
$$\ln T=3{,}6+0{,}30\,F_2+0{,}35\,\mathrm{offre}+\big\{\text{Boutique }{+}0{,}30,\ \text{Site }0,\ \text{Réseaux }{-}0{,}15\big\}+0{,}008\,(\mathrm{âge}-36)+\sigma W,$$
où $F_2$ est un **facteur de sensibilité au service** (loi normale centrée réduite) **que le fichier ne contient pas**, et où $\sigma=1/1{,}35\approx0{,}74$. On peut même reconstruire ce facteur manquant avec le générateur de données, et ajuster le modèle « oracle » qui le connaît :

```python
import sys
sys.path.insert(0, "build")
import donnees2
_, F1, F2 = donnees2.clients()
oracle = ajuster("weibull", y, d, np.column_stack([Xc, F2]))
se_o = np.sqrt(np.diag(oracle["cov"]))

# Valeurs vraies, exprimées dans la même paramétrisation que notre modèle (âge centré en 36 dans le générateur,
# référence = Boutique, donc Réseaux = -0.15 - 0.30 et Site = 0 - 0.30)
vrai = {"(constante)": 3.6 + 0.30 - 0.008 * 36, "offre_bienvenue": 0.35, "age": 0.008,
        "canal_acquisition_Instagram": -0.15 - 0.30, "canal_acquisition_Site": 0.0 - 0.30}
lignes = []
for j, nom in enumerate(noms):
    lignes.append({"paramètre": nom, "vérité": vrai[nom], "estimé (sans F2)": wb["theta"][j], "ET": se[j],
                   "écart / ET": (wb["theta"][j] - vrai[nom]) / se[j], "oracle (avec F2)": oracle["theta"][j]})
lignes.append({"paramètre": "forme k = 1/sigma", "vérité": 1.35, "estimé (sans F2)": 1 / sigma, "ET": np.nan,
               "écart / ET": np.nan, "oracle (avec F2)": 1 / np.exp(oracle["theta"][-1])})
lignes.append({"paramètre": "F2 (facteur manquant)", "vérité": 0.30, "estimé (sans F2)": np.nan, "ET": np.nan,
               "écart / ET": np.nan, "oracle (avec F2)": oracle["theta"][len(noms)]})
print(pd.DataFrame(lignes).round(3).to_string(index=False))
```
<!--sortie-->
```text
                  paramètre  vérité  estimé (sans F2)    ET  écart / ET  oracle (avec F2)
                (constante)   3.612             3.526 0.097      -0.890             3.562
            offre_bienvenue   0.350             0.313 0.049      -0.753             0.299
                        age   0.008             0.010 0.002       0.955             0.009
canal_acquisition_Instagram  -0.450            -0.480 0.064      -0.471            -0.486
     canal_acquisition_Site  -0.300            -0.245 0.067       0.817            -0.242
          forme k = 1/sigma   1.350             1.322   NaN         NaN             1.400
      F2 (facteur manquant)   0.300               NaN   NaN         NaN             0.310
```

Que montre cette comparaison ?

1. **Tous les coefficients du modèle réaliste sont à moins d'une erreur standard de la vérité** (colonne « écart / ET ») : la méthode retrouve ce qu'on a programmé (effet de l'offre : $+0{,}31$ estimé contre $+0{,}35$ ; les canaux et l'âge aussi).
2. Le modèle **oracle**, qui connaît le facteur manquant, retrouve **son coefficient** ($\approx0{,}31$ pour une vérité de 0,30). Il estime aussi une forme de $1{,}40$, contre $1{,}32$ pour le modèle sans $F_2$ : la vraie valeur (1,35) se situe entre les deux, et l'écart entre les deux estimations est précisément ce que prédit le point suivant. (De même, sur les répondants à l'enquête, la forme passe de 1,31 à 1,37 quand on ajoute la note de service.)
3. Le **déplacement de la forme** est un phénomène classique : quand une variable qui joue sur le risque est **omise**, le risque observé pour l'ensemble de la population est un **mélange** de risques individuels ; les clients les plus fragiles partent les premiers, de sorte que les survivants sont de plus en plus robustes. La population semble avoir un risque qui augmente **moins vite** que celui de chaque individu. En termes de modèle, on parle d'**hétérogénéité non observée** (ou de **fragilité**, *frailty*). Elle est inévitable : il y a toujours des variables que l'on ne mesure pas.

> ✅ **À retenir**
> - Un modèle **paramétrique** parie sur la loi de la durée. Il permet d'**extrapoler**, de calculer des durées moyennes et d'être plus précis que Cox *si la forme est bonne*.
> - Le modèle **AFT** s'écrit $\ln T=x^\top\gamma+\sigma W$ : les covariables **accélèrent ou ralentissent le temps** ; $e^{\gamma}$ est le facteur d'accélération (**signe opposé** à celui de Cox).
> - La **Weibull** est à la fois AFT et à risques proportionnels, avec $\beta=-\gamma/\sigma$ : un excellent test de cohérence avec Cox.
> - La vraisemblance avec censure s'écrit à la main pour chaque loi ; le résultat doit coïncider avec `survreg` de R. On choisit entre lois par l'**AIC** et on vérifie l'**adéquation** par les **résidus de Cox-Snell**.
> - La **valeur vie client** $\sum_t S(t\mid x)\,m/(1+r)^t$ repose sur des hypothèses explicites (marge, actualisation, horizon) et sur une extrapolation : on la présente avec une analyse de sensibilité, jamais comme une certitude.
> - Une variable pertinente **omise** (hétérogénéité non observée) déplace la forme apparente du risque ; on ne peut jamais exclure qu'il en existe.
